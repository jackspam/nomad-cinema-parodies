import glob
import json
import math
import os
import re
import subprocess
import sys
import time
import urllib.request

COMFY = "http://127.0.0.1:8188"


def ffprobe_duration(path: str) -> float:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path]
    ).decode().strip()
    return float(out)


def clean_ltx_prompt(raw_prompt: str, dialogue: str = "") -> str:
    txt = raw_prompt
    txt = txt.replace("<Picture 1> is the exact starting frame of this photorealistic 35mm live-action movie scene.\n", "")
    txt = txt.replace("<Audio 1> is the exact spoken dialogue audio track for the speaking character in <Picture 1> and is reused verbatim.\n", "")
    txt = re.sub(r"</?(Picture|Audio)\s*\d+>", "the reference frame", txt)
    txt = re.sub(r"Subtle controlled cinema camera movement,.*$", "", txt, flags=re.S).strip()
    if dialogue:
        txt = f"{txt} The speaking character performs dynamically in crisp lip-sync to the audio dialogue: \"{dialogue}\""
    return txt


def ltx_num_frames(audio_path: str, fps: int = 24) -> int:
    dur = ffprobe_duration(audio_path)
    n = 1 + math.ceil((dur * fps) / 8.0) * 8
    return max(97, n)


def build_ltx_workflow(job):
    return {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "ltx-2.5-22b-distilled-transformer-comfy-int8-convrot.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "gemma4-12b-with-proj-ltx-2.5-comfy-int8-convrot.safetensors", "type": "ltxv", "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "ltx-2.5-video-vae-bf16.safetensors"}},
        "4": {"class_type": "VAELoader", "inputs": {"vae_name": "ltx-2.5-audio-vae-bf16.safetensors"}},
        "5": {"class_type": "LatentUpscaleModelLoader", "inputs": {"model_name": "ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0.safetensors"}},
        "6": {"class_type": "LoadImage", "inputs": {"image": job["images"][0]}},
        "7": {"class_type": "LTXVPreprocess", "inputs": {"image": ["6", 0], "img_compression": 18}},
        "8": {"class_type": "CLIPTextEncode", "inputs": {"text": job["ltx_prompt"], "clip": ["2", 0]}},
        "9": {"class_type": "CLIPTextEncode", "inputs": {"text": "worst quality, blurry, jittery, morphing, distorted face, extra limbs, static freeze, watermark, subtitles", "clip": ["2", 0]}},
        "10": {"class_type": "LTXVConditioning", "inputs": {"positive": ["8", 0], "negative": ["9", 0], "frame_rate": 24.0}},
        "11": {"class_type": "EmptyLTXVLatentVideo", "inputs": {"width": 672, "height": 384, "length": job["ltx_length"], "batch_size": 1}},
        "12": {"class_type": "LTXVImgToVideoInplace", "inputs": {"vae": ["3", 0], "image": ["7", 0], "latent": ["11", 0], "strength": 0.85, "bypass": False}},
        "13": {"class_type": "LoadAudio", "inputs": {"audio": job["audio"]}},
        "14": {"class_type": "LTXVAudioVAEEncode", "inputs": {"audio": ["13", 0], "audio_vae": ["4", 0]}},
        "15": {"class_type": "SolidMask", "inputs": {"value": 0.0, "width": 512, "height": 512}},
        "16": {"class_type": "SetLatentNoiseMask", "inputs": {"samples": ["14", 0], "mask": ["15", 0]}},
        "17": {"class_type": "LTXVConcatAVLatent", "inputs": {"video_latent": ["12", 0], "audio_latent": ["16", 0]}},
        "18": {"class_type": "RandomNoise", "inputs": {"noise_seed": job["seed"]}},
        "19": {"class_type": "CFGGuider", "inputs": {"model": ["1", 0], "positive": ["10", 0], "negative": ["10", 1], "cfg": 1.0}},
        "20": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler_ancestral"}},
        "21": {"class_type": "ManualSigmas", "inputs": {"sigmas": "1.0, 0.99375, 0.9875, 0.98125, 0.975, 0.909375, 0.725, 0.421875, 0.0"}},
        "22": {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": ["18", 0], "guider": ["19", 0], "sampler": ["20", 0], "sigmas": ["21", 0], "latent_image": ["17", 0]}},
        "23": {"class_type": "LTXVSeparateAVLatent", "inputs": {"av_latent": ["22", 0]}},
        "24": {"class_type": "LTXVLatentUpsampler", "inputs": {"samples": ["23", 0], "upscale_model": ["5", 0], "vae": ["3", 0]}},
        "25": {"class_type": "LTXVImgToVideoInplace", "inputs": {"vae": ["3", 0], "image": ["7", 0], "latent": ["24", 0], "strength": 1.0, "bypass": False}},
        "26": {"class_type": "LTXVConcatAVLatent", "inputs": {"video_latent": ["25", 0], "audio_latent": ["23", 1]}},
        "27": {"class_type": "RandomNoise", "inputs": {"noise_seed": job["seed"]}},
        "28": {"class_type": "CFGGuider", "inputs": {"model": ["1", 0], "positive": ["10", 0], "negative": ["10", 1], "cfg": 1.0}},
        "29": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler_ancestral"}},
        "30": {"class_type": "ManualSigmas", "inputs": {"sigmas": "0.85, 0.7250, 0.4219, 0.0"}},
        "31": {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": ["27", 0], "guider": ["28", 0], "sampler": ["29", 0], "sigmas": ["30", 0], "latent_image": ["26", 0]}},
        "32": {"class_type": "LTXVSeparateAVLatent", "inputs": {"av_latent": ["31", 0]}},
        "33": {"class_type": "VAEDecodeTiled", "inputs": {"samples": ["32", 0], "vae": ["3", 0], "tile_size": 512, "overlap": 64, "temporal_size": 64, "temporal_overlap": 8}},
        "34": {"class_type": "LTXVAudioVAEDecode", "inputs": {"samples": ["32", 1], "audio_vae": ["4", 0]}},
        "35": {"class_type": "CreateVideo", "inputs": {"images": ["33", 0], "audio": ["34", 0], "fps": 24}},
        "36": {"class_type": "SaveVideo", "inputs": {"video": ["35", 0], "filename_prefix": f"video/{job['out_prefix']}", "format": "auto", "codec": "auto"}},
    }


def submit(wf):
    req = urllib.request.Request(f"{COMFY}/prompt", data=json.dumps({"prompt": wf}).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())["prompt_id"]


def wait_done(pid):
    while True:
        with urllib.request.urlopen(f"{COMFY}/history/{pid}") as r:
            h = json.loads(r.read())
        if pid in h:
            st = h[pid]["status"]["status_str"]
            if st != "success":
                raise RuntimeError(f"ComfyUI failed: {h[pid]['status']}")
            return h[pid]["outputs"]
        time.sleep(5)


def wait_queue_empty():
    while True:
        with urllib.request.urlopen(f"{COMFY}/queue") as r:
            q = json.loads(r.read())
        if not q.get("queue_running") and not q.get("queue_pending"):
            return
        time.sleep(5)


def free_comfy():
    req = urllib.request.Request(
        f"{COMFY}/free",
        data=json.dumps({"unload_models": True, "free_memory": True}).encode(),
        headers={"Content-Type": "application/json"},
    )
    urllib.request.urlopen(req, timeout=10).read()
    print("FREED_COMFY_VRAM_OK", flush=True)


def main():
    jobs_path = sys.argv[1]
    script_path = sys.argv[2] if len(sys.argv) > 2 else None
    only_prefixes = set(sys.argv[3].split(",")) if len(sys.argv) > 3 and sys.argv[3] else None

    jobs = json.load(open(jobs_path))
    dialogue_by_id = {}
    if script_path and os.path.exists(script_path):
        for sh in json.load(open(script_path)).get("shots", []):
            dialogue_by_id[sh["shot_id"].lower()] = sh.get("exact_dialogue", "")

    timings_path = "/content/ltx25_render_timing_log.json"
    timings = json.load(open(timings_path)) if os.path.exists(timings_path) else {}

    wait_queue_empty()
    free_comfy()

    for job in jobs:
        prefix = job["prefix"]
        if only_prefixes and prefix not in only_prefixes:
            continue
        out_prefix = f"ltx25_{prefix}"
        existing = sorted(glob.glob(f"/content/ComfyUI/output/video/{out_prefix}_*.mp4"))
        if existing:
            print(f"=== LTX Skipping {out_prefix} (already rendered: {existing[-1]}) ===", flush=True)
            continue

        sid = prefix.split("_", 1)[1] if "_" in prefix else prefix
        dialogue = job.get("dialogue") or dialogue_by_id.get(sid, "")
        audio_path = os.path.join("/content/ComfyUI/input", job["audio"]) if job.get("audio") else None
        job_copy = dict(job)
        job_copy["out_prefix"] = out_prefix
        job_copy["ltx_length"] = job.get("ltx_length") or (ltx_num_frames(audio_path) if audio_path and os.path.exists(audio_path) else max(97, 1 + ((job["length"] - 1 + 7) // 8) * 8))
        job_copy["ltx_prompt"] = job.get("ltx_prompt") or clean_ltx_prompt(job["prompt"], dialogue)

        t0 = time.time()
        print(f"=== LTX Starting {out_prefix} (len={job_copy['ltx_length']}) ===", flush=True)
        pid = submit(build_ltx_workflow(job_copy))
        out = wait_done(pid)
        elapsed = round(time.time() - t0, 1)
        timings[out_prefix] = {"elapsed_sec": elapsed, "frames": job_copy["ltx_length"], "outputs": out.get("36", {}).get("images", [])}
        json.dump(timings, open(timings_path, "w"), indent=2)
        print(f"=== LTX Finished {out_prefix} in {elapsed}s ===", flush=True)


if __name__ == "__main__":
    main()
