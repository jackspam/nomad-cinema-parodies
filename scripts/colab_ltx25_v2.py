"""
Hardened LTX-2.5 Dev BF16 IA2V Runner for Dark Knight v2 on Colab G4 (96 GB).
Fixes all v1 root causes:
  1. Pre-pads clean input audio to exact WAV matching ltx_length / 24.0 seconds before LTXVAudioVAEEncode.
  2. Applies SetLatentNoiseMask(0.0) (frozen_audio) and feeds the SAME frozen_audio into BOTH Stage 1 & Stage 2.
  3. Zero LTXVModalityGuidance; uses deterministic `euler` sampler in BOTH stages.
  4. Uses LTXVPreprocess(img_compression=0) + Dev BF16 (24 steps, cfg=3.0 at 960x416) -> Distilled LoRA 450 x2 Upscale (1920x832 native Scope, 3 steps, cfg=1.0).
  5. Uses LTXVAddGuide for Start+End multi-keyframe camera motion anchoring when `end_image` is set.
"""
import array
import glob
import json
import math
import os
import subprocess
import sys
import time
import urllib.request

COMFY = "http://127.0.0.1:8188"
INPUT_DIR = "/content/ComfyUI/input"


def ffprobe_duration(path: str) -> float:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path]
    ).decode().strip()
    return float(out)


def ltx_num_frames(audio_path: str, fps: int = 24) -> int:
    dur = ffprobe_duration(audio_path)
    # 1 + 8*k frames; add +0.25s tail margin, minimum 73 frames (~3.04s)
    n = 1 + math.ceil(((dur + 0.20) * fps) / 8.0) * 8
    return max(73, n)


def prep_exact_wav(src_audio: str, num_frames: int, out_wav_rel: str) -> str:
    """Apply zero-latency linear gain to loud speech (rms > 0.11 -> 0.075) and convert to 48kHz stereo WAV padded to num_frames / 24s."""
    target_sec = num_frames / 24.0
    dst = os.path.join(INPUT_DIR, out_wav_rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    pcm = subprocess.check_output(
        ["ffmpeg", "-y", "-i", src_audio, "-ac", "1", "-ar", "16000", "-f", "s16le", "pipe:1"],
        stderr=subprocess.DEVNULL,
    )
    samples = array.array("h", pcm)
    rms = math.sqrt(sum(s * s for s in samples) / len(samples)) / 32768.0 if samples else 0.0
    af_parts = []
    if rms > 0.11:
        af_parts.append(f"volume={0.075 / rms:.4f}")
    af_parts.extend(["aresample=48000", f"apad=whole_dur={target_sec:.4f}"])
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", src_audio,
            "-af", ",".join(af_parts),
            "-t", f"{target_sec:.4f}",
            "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", dst,
        ],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    return out_wav_rel


def ensure_comfy():
    try:
        with urllib.request.urlopen(f"{COMFY}/system_stats", timeout=2) as r:
            if r.status == 200:
                return
    except Exception:
        pass
    print("Starting local ComfyUI server...", flush=True)
    subprocess.Popen(
        ["python3", "/content/ComfyUI/main.py", "--listen", "127.0.0.1", "--port", "8188"],
        cwd="/content/ComfyUI",
        stdout=open("/content/comfy.log", "w"),
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    for _ in range(60):
        try:
            with urllib.request.urlopen(f"{COMFY}/system_stats", timeout=2) as r:
                if r.status == 200:
                    print("COMFY_STARTED_OK", flush=True)
                    return
        except Exception:
            pass
        time.sleep(2)
    raise RuntimeError("ComfyUI failed to start — check /content/comfy.log")


def get_object_info(cls_name: str) -> dict:
    with urllib.request.urlopen(f"{COMFY}/object_info/{cls_name}") as r:
        return json.loads(r.read()).get(cls_name, {})


def build_workflow(job: dict, add_guide_info: dict, use_dev_int8: bool = False) -> dict:
    w_s1, h_s1 = 960, 416  # Upscales x2 cleanly to 1920x832 Scope!
    length = job["ltx_length"]
    seed = job["seed"]
    unet_name = "ltx-2.5-22b-dev-transformer-comfy-int8-convrot.safetensors" if use_dev_int8 else "ltx-2.5-22b-dev-transformer-bf16.safetensors"

    g = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": unet_name, "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "gemma4-12b-with-proj-ltx-2.5-comfy-int8-convrot.safetensors", "type": "ltxv", "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "ltx-2.5-video-vae-bf16.safetensors"}},
        "4": {"class_type": "VAELoader", "inputs": {"vae_name": "ltx-2.5-audio-vae-bf16.safetensors"}},
        "5": {"class_type": "LatentUpscaleModelLoader", "inputs": {"model_name": "ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0.safetensors"}},
        "6": {"class_type": "LoadImage", "inputs": {"image": job["start_image"]}},
        "7": {"class_type": "LTXVPreprocess", "inputs": {"image": ["6", 0], "img_compression": 0}},
        "8": {"class_type": "CLIPTextEncode", "inputs": {"text": job["ltx_prompt"], "clip": ["2", 0]}},
        "9": {"class_type": "CLIPTextEncode", "inputs": {"text": job["negative_prompt"], "clip": ["2", 0]}},
        "10": {"class_type": "LTXVConditioning", "inputs": {"positive": ["8", 0], "negative": ["9", 0], "frame_rate": 24.0}},
        "11": {"class_type": "EmptyLTXVLatentVideo", "inputs": {"width": w_s1, "height": h_s1, "length": length, "batch_size": 1}},
        "12": {"class_type": "LTXVImgToVideoInplace", "inputs": {"vae": ["3", 0], "image": ["7", 0], "latent": ["11", 0], "strength": job.get("s1_img_strength", 0.60), "bypass": False}},
    }

    cond_pos = ["10", 0]
    cond_neg = ["10", 1]
    lat_s1 = ["12", 0]

    # Optional Start+End multi-keyframe camera motion anchoring via LTXVAddGuide
    if job.get("end_image") and add_guide_info:
        g["60"] = {"class_type": "LoadImage", "inputs": {"image": job["end_image"]}}
        g["61"] = {"class_type": "LTXVPreprocess", "inputs": {"image": ["60", 0], "img_compression": 0}}
        req_inputs = add_guide_info.get("input", {}).get("required", {})
        guide_in = {
            "positive": cond_pos,
            "negative": cond_neg,
            "vae": ["3", 0],
            "latent": lat_s1,
            "image": ["61", 0],
            "frame_idx": length - 1,
            "strength": job.get("end_guide_strength", 0.55),
        }
        # Keep only keys accepted by installed ComfyUI LTXVAddGuide
        opt_inputs = add_guide_info.get("input", {}).get("optional", {})
        allowed_keys = set(req_inputs.keys()) | set(opt_inputs.keys())
        guide_in = {k: v for k, v in guide_in.items() if k in allowed_keys}
        g["62"] = {"class_type": "LTXVAddGuide", "inputs": guide_in}
        cond_pos = ["62", 0]
        cond_neg = ["62", 1]
        lat_s1 = ["62", 2]

    # Audio track locked via official LTXVFreezeLatent across BOTH Stage 1 & Stage 2!
    if job.get("silent_on_camera") or not job.get("wav_rel"):
        g["16"] = {"class_type": "LTXVEmptyLatentAudio", "inputs": {"frames_number": length, "frame_rate": 24, "batch_size": 1, "audio_vae": ["4", 0]}}
    else:
        g["13"] = {"class_type": "LoadAudio", "inputs": {"audio": job["wav_rel"]}}
        g["14"] = {"class_type": "LTXVAudioVAEEncode", "inputs": {"audio": ["13", 0], "audio_vae": ["4", 0]}}
        g["16"] = {"class_type": "LTXVFreezeLatent", "inputs": {"latent": ["14", 0]}}

    # Stage 1: Dev BF16 24-step Euler wired directly to CFGGuider (no LTXVModalityGuidance)
    g["17"] = {"class_type": "LTXVConcatAVLatent", "inputs": {"video_latent": lat_s1, "audio_latent": ["16", 0]}}
    g["18"] = {"class_type": "RandomNoise", "inputs": {"noise_seed": seed}}
    g["19"] = {"class_type": "CFGGuider", "inputs": {"model": ["1", 0], "positive": cond_pos, "negative": cond_neg, "cfg": job.get("cfg", 3.0)}}
    g["20"] = {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}}
    g["21"] = {"class_type": "LTXVScheduler", "inputs": {"steps": job.get("steps", 24), "max_shift": 2.05, "base_shift": 0.95, "stretch": True, "terminal": 0.1, "latent": ["17", 0]}}
    g["22"] = {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": ["18", 0], "guider": ["19", 0], "sampler": ["20", 0], "sigmas": ["21", 0], "latent_image": ["17", 0]}}
    g["23"] = {"class_type": "LTXVSeparateAVLatent", "inputs": {"av_latent": ["22", 0]}}

    # Stage 2: Crop guide tokens out before Spatial Upscale -> 1920x832 + Distilled LoRA 450 + SAME frozen audio ["16", 0]!
    s2_lat_in = ["23", 0]
    s2_pos, s2_neg = cond_pos, cond_neg
    if job.get("end_image") and add_guide_info:
        g["63"] = {"class_type": "LTXVCropGuides", "inputs": {"positive": cond_pos, "negative": cond_neg, "latent": ["23", 0]}}
        s2_pos = ["63", 0]
        s2_neg = ["63", 1]
        s2_lat_in = ["63", 2]

    g["24"] = {"class_type": "LTXVLatentUpsampler", "inputs": {"samples": s2_lat_in, "upscale_model": ["5", 0], "vae": ["3", 0]}}
    g["25"] = {"class_type": "LTXVImgToVideoInplace", "inputs": {"vae": ["3", 0], "image": ["7", 0], "latent": ["24", 0], "strength": 1.0, "bypass": False}}
    g["26"] = {"class_type": "LTXVConcatAVLatent", "inputs": {"video_latent": ["25", 0], "audio_latent": ["16", 0]}}
    g["26b"] = {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["1", 0], "lora_name": "ltx-2.5-22b-distilled-lora-450-bf16.safetensors", "strength_model": 1.0}}
    g["27"] = {"class_type": "RandomNoise", "inputs": {"noise_seed": seed + 1}}
    g["28"] = {"class_type": "CFGGuider", "inputs": {"model": ["26b", 0], "positive": s2_pos, "negative": s2_neg, "cfg": 1.0}}
    g["29"] = {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}}
    g["30"] = {"class_type": "ManualSigmas", "inputs": {"sigmas": "0.85, 0.7250, 0.4219, 0.0"}}
    g["31"] = {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": ["27", 0], "guider": ["28", 0], "sampler": ["29", 0], "sigmas": ["30", 0], "latent_image": ["26", 0]}}
    g["32"] = {"class_type": "LTXVSeparateAVLatent", "inputs": {"av_latent": ["31", 0]}}

    g["33"] = {"class_type": "VAEDecodeTiled", "inputs": {"samples": ["32", 0], "vae": ["3", 0], "tile_size": 512, "overlap": 64, "temporal_size": 64, "temporal_overlap": 8}}
    g["34"] = {"class_type": "LTXVAudioVAEDecode", "inputs": {"samples": ["32", 1], "audio_vae": ["4", 0]}}
    g["35"] = {"class_type": "CreateVideo", "inputs": {"images": ["33", 0], "audio": ["34", 0], "fps": 24}}
    g["36"] = {"class_type": "SaveVideo", "inputs": {"video": ["35", 0], "filename_prefix": f"video/{job['out_prefix']}", "format": "auto", "codec": "auto"}}
    return g


def submit(wf):
    req = urllib.request.Request(f"{COMFY}/prompt", data=json.dumps({"prompt": wf}).encode(), headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())["prompt_id"]
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"ComfyUI HTTP {e.code}: {e.read().decode()}")


def wait_done(pid):
    while True:
        with urllib.request.urlopen(f"{COMFY}/history/{pid}") as r:
            h = json.loads(r.read())
        if pid in h:
            st = h[pid]["status"]["status_str"]
            if st != "success":
                raise RuntimeError(f"ComfyUI failed: {h[pid]['status']}")
            return h[pid]["outputs"]
        time.sleep(3)


def main():
    jobs_path = sys.argv[1]
    only_ids = set(sys.argv[2].split(",")) if len(sys.argv) > 2 and sys.argv[2] else None

    ensure_comfy()
    jobs = json.load(open(jobs_path))
    add_guide_info = get_object_info("LTXVAddGuide")
    print("LTXVAddGuide schema:", json.dumps(add_guide_info.get("input", {})), flush=True)

    timings_path = "/content/ltx25_v2_timings.json"
    timings = json.load(open(timings_path)) if os.path.exists(timings_path) else {}

    for job in jobs:
        sid = job["shot_id"]
        if only_ids and sid not in only_ids:
            continue
        out_prefix = job["out_prefix"]
        existing = sorted(glob.glob(f"/content/ComfyUI/output/video/{out_prefix}_*.mp4"))
        if existing and not job.get("force"):
            print(f"=== Skipping {out_prefix} (already rendered: {existing[-1]}) ===", flush=True)
            continue

        src_au = os.path.join(INPUT_DIR, job["audio"])
        num_frames = ltx_num_frames(src_au)
        wav_rel = prep_exact_wav(src_au, num_frames, f"wav/{sid}.wav")

        j = dict(job)
        j["ltx_length"] = num_frames
        j["wav_rel"] = wav_rel

        t0 = time.time()
        print(f"=== LTX-2.5 Dev BF16 Starting {out_prefix} (frames={num_frames}, end_guide={bool(j.get('end_image'))}) ===", flush=True)
        wf = build_workflow(j, add_guide_info)
        pid = submit(wf)
        out = wait_done(pid)
        elapsed = round(time.time() - t0, 1)
        timings[out_prefix] = {"elapsed_sec": elapsed, "frames": num_frames, "outputs": out.get("36", {}).get("images", [])}
        json.dump(timings, open(timings_path, "w"), indent=2)
        print(f"=== LTX-2.5 Dev BF16 Finished {out_prefix} in {elapsed}s ===", flush=True)


if __name__ == "__main__":
    main()
