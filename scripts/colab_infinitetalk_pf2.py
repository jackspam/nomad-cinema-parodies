"""
InfiniteTalk (Wan2.1-I2V-14B-480p + InfiniteTalk-Single + LightX2V) Runner for Pulp Fiction v2 on Colab.
Renders at 960x416 (exact 1920x832 / 2 Scope resolution, 24 fps) with wav2vec2 phoneme-locked audio embeddings,
then crisply scales x2 to 1920x832 Scope and muxes the exact source dialogue WAV (zero audio shift).
"""
import glob
import json
import math
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

COMFY = "http://127.0.0.1:8188"
INPUT_DIR = "/content/ComfyUI/input"
OUTPUT_DIR = "/content/ComfyUI/output/video"


def ffprobe_duration(path: str) -> float:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path]
    ).decode().strip()
    return float(out)


def prep_clean_wav(src_audio: str, num_frames: int, out_wav_rel: str) -> str:
    """Convert audio cleanly to 48kHz stereo WAV padded with silence to exact num_frames / 24.0s (no loudnorm lag)."""
    target_sec = num_frames / 24.0
    dst = os.path.join(INPUT_DIR, out_wav_rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", src_audio,
            "-af", f"aresample=48000,apad=whole_dur={target_sec:.4f}",
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


def build_prompt_for_wan(job: dict) -> tuple[str, str]:
    p = job.get("ltx_prompt", "").lower()
    if "sedan" in p or "windshield" in p or "leather" in p:
        setting = "sunlit 1974 vintage cream-leather sedan driving down a Los Angeles palm boulevard"
    elif "hallway" in p or "49" in p or "dim" in p:
        setting = "dimly lit worn vintage Los Angeles motel apartment hallway outside painted door 49"
    elif "bathroom" in p or "briefcase" in p:
        setting = "sunny 1970s avocado-green Los Angeles apartment interior with golden slatted venetian blinds"
    else:
        setting = "warm Kodachrome sunlit 1970s avocado-green Los Angeles apartment interior"

    cam = job.get("camera_motion", "STATIC_LOCKED")
    if cam in ("HANDHELD_35MM", "IMPACT_SHAKE"):
        cam_desc = "Subtle authentic 35mm handheld camera feel keeping stable composition."
    else:
        cam_desc = "Steady tripod-locked 35mm camera framing."

    pos = (
        f"Photorealistic 1994 35mm Kodachrome cinema shot inside a {setting}. "
        f"Exact character likeness, wardrobe, glasses, hairstyle, and warm golden sunlight from the reference frame. "
        f"{cam_desc} Only the speaking character articulates every syllable naturally with expressive eyes, "
        f"subtle realistic jaw motion synced to speech, fine skin texture, and 35mm film grain. "
        f"Natural serious expression at end of sentence with closed mouth."
    )
    neg = (
        "blurred details, subtitles, extra limbs, distorted face, double mouthing by silent listeners, "
        "waxy smooth skin, frozen mouth, unprompted grin at end, dark superhero armor, clown makeup, "
        "worst quality, low quality, jpeg artifacts"
    )
    return pos, neg


def detect_low_vram() -> bool:
    if os.environ.get("INFINITETALK_LOW_VRAM") == "1":
        return True
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
            text=True,
        ).strip().splitlines()[0]
        return float(out) < 32000.0
    except Exception:
        return False


def build_workflow(job: dict, num_frames: int, wav_rel: str) -> dict:
    w_gen, h_gen = 960, 416
    seed = int(job["seed"])
    pos, neg = build_prompt_for_wan(job)
    out_prefix_raw = f"{job['out_prefix']}_raw"
    low_vram = detect_low_vram()

    g = {
        "1": {"class_type": "LoadImage", "inputs": {"image": job["start_image"]}},
        "2": {"class_type": "ImageScale", "inputs": {
            "image": ["1", 0],
            "upscale_method": "lanczos",
            "width": w_gen,
            "height": h_gen,
            "crop": "disabled",
        }},
        "3": {"class_type": "CLIPVisionLoader", "inputs": {"clip_name": "clip_vision_h.safetensors"}},
        "4": {"class_type": "WanVideoClipVisionEncode", "inputs": {
            "clip_vision": ["3", 0],
            "image_1": ["2", 0],
            "strength_1": 1.0,
            "strength_2": 1.0,
            "crop": "center",
            "combine_embeds": "average",
            "force_offload": True,
        }},
        "5": {"class_type": "WanVideoVAELoader", "inputs": {
            "model_name": "Wan2_1_VAE_bf16.safetensors",
            "precision": "bf16",
            "use_cpu_cache": low_vram,
            "verbose": False,
        }},
        "6": {"class_type": "WanVideoLoraSelect", "inputs": {
            "lora": "lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors",
            "strength": float(job.get("wan_lora_strength", 1.0)),
            "low_mem_load": low_vram,
            "merge_loras": False,
        }},
        "7": {"class_type": "MultiTalkModelLoader", "inputs": {
            "model": "Wan2_1-InfiniTetalk-Single_fp16.safetensors",
        }},
        "8": {"class_type": "WanVideoModelLoader", "inputs": {
            "model": "Wan2_1-I2V-14B-480p_fp8_e4m3fn_scaled_KJ.safetensors",
            "base_precision": "bf16",
            "quantization": "fp8_e4m3fn_scaled",
            "load_device": "offload_device" if low_vram else "main_device",
            "attention_mode": "sdpa",
            "lora": ["6", 0],
            "multitalk_model": ["7", 0],
        }},
        "9": {"class_type": "Wav2VecModelLoader", "inputs": {
            "model": "wav2vec2-chinese-base_fp16.safetensors",
            "base_precision": "fp16",
            "load_device": "offload_device" if low_vram else "main_device",
        }},
        "10": {"class_type": "LoadAudio", "inputs": {"audio": wav_rel}},
        "11": {"class_type": "MultiTalkWav2VecEmbeds", "inputs": {
            "wav2vec_model": ["9", 0],
            "audio_1": ["10", 0],
            "normalize_loudness": True,
            "num_frames": num_frames,
            "fps": 24.0,
            "audio_scale": float(job.get("wan_audio_scale", 1.0)),
            "audio_cfg_scale": 1.0,
            "multi_audio_type": "para",
            "add_noise_floor": False,
            "smooth_transients": False,
        }},
        "12": {"class_type": "WanVideoTextEncodeCached", "inputs": {
            "model_name": "umt5-xxl-enc-fp8_e4m3fn.safetensors",
            "precision": "bf16",
            "positive_prompt": pos,
            "negative_prompt": neg,
            "quantization": "disabled",
            "use_disk_cache": True,
            "device": "cpu" if low_vram else "gpu",
        }},
        "13": {"class_type": "WanVideoImageToVideoMultiTalk", "inputs": {
            "vae": ["5", 0],
            "width": w_gen,
            "height": h_gen,
            "frame_window_size": 81,
            "motion_frame": 9,
            "force_offload": low_vram,
            "colormatch": "disabled",
            "start_image": ["2", 0],
            "tiled_vae": low_vram,
            "clip_embeds": ["4", 0],
            "mode": "infinitetalk",
            "output_path": "",
        }},
        "14": {"class_type": "WanVideoSampler", "inputs": {
            "model": ["8", 0],
            "image_embeds": ["13", 0],
            "steps": int(job.get("wan_steps", 6)),
            "cfg": float(job.get("wan_cfg", 1.0)),
            "shift": float(job.get("wan_shift", 11.0)),
            "seed": seed,
            "force_offload": low_vram,
            "scheduler": "dpm++_sde",
            "riflex_freq_index": 0,
            "text_embeds": ["12", 0],
            "denoise_strength": 1.0,
            "batched_cfg": False,
            "rope_function": "comfy",
            "multitalk_embeds": ["11", 0],
            "start_step": 0,
            "end_step": -1,
            "add_noise_to_samples": False,
        }},
        "15": {"class_type": "WanVideoDecode", "inputs": {
            "vae": ["5", 0],
            "samples": ["14", 0],
            "enable_vae_tiling": low_vram,
            "tile_x": 272,
            "tile_y": 272,
            "tile_stride_x": 144,
            "tile_stride_y": 128,
            "normalization": "default",
        }},
        "16": {"class_type": "CreateVideo", "inputs": {
            "images": ["15", 0],
            "audio": ["11", 1],
            "fps": 24,
        }},
        "17": {"class_type": "SaveVideo", "inputs": {
            "video": ["16", 0],
            "filename_prefix": f"video/{out_prefix_raw}",
            "format": "auto",
            "codec": "auto",
        }},
    }
    if low_vram:
        g["18"] = {
            "class_type": "WanVideoBlockSwap",
            "inputs": {
                "blocks_to_swap": 20,
                "offload_img_emb": False,
                "offload_txt_emb": False,
            },
        }
        g["8"]["inputs"]["block_swap_args"] = ["18", 0]
    return g


def submit(wf):
    req = urllib.request.Request(
        f"{COMFY}/prompt",
        data=json.dumps({"prompt": wf}).encode(),
        headers={"Content-Type": "application/json"},
    )
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
        time.sleep(2)


def upscale_and_mux(raw_mp4: str, clean_wav: str, out_mp4: str):
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", raw_mp4,
            "-i", clean_wav,
            "-map", "0:v:0", "-map", "1:a:0",
            "-vf", "scale=1920:832:flags=lanczos,unsharp=5:5:0.45:3:3:0.0",
            "-r", "24",
            "-c:v", "libx264", "-crf", "15", "-preset", "fast", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            "-shortest",
            out_mp4,
        ],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def main():
    jobs_path = sys.argv[1]
    only_ids = set(sys.argv[2].split(",")) if len(sys.argv) > 2 and sys.argv[2] else None

    ensure_comfy()
    jobs = json.load(open(jobs_path))
    timings_path = "/content/infinitetalk_pf2_timings.json"
    timings = json.load(open(timings_path)) if os.path.exists(timings_path) else {}

    for job in jobs:
        sid = job["shot_id"]
        if only_ids and sid not in only_ids:
            continue
        if not only_ids and job.get("engine") != "infinitetalk":
            continue
        out_prefix = job["out_prefix"]
        final_mp4 = os.path.join(OUTPUT_DIR, f"{out_prefix}_00001_.mp4")
        if os.path.exists(final_mp4) and not job.get("force"):
            print(f"=== Skipping {out_prefix} (already rendered) ===", flush=True)
            continue

        for old in glob.glob(os.path.join(OUTPUT_DIR, f"{out_prefix}*")):
            os.remove(old)

        src_au = os.path.join(INPUT_DIR, job["audio"])
        dur = ffprobe_duration(src_au)
        raw_frames = math.ceil((dur + 0.16) * 24.0)
        num_frames = max(49, ((raw_frames - 1 + 3) // 4) * 4 + 1)
        wav_rel = prep_clean_wav(src_au, num_frames, f"wav_pf2/{sid}.wav")
        clean_wav_abs = os.path.join(INPUT_DIR, wav_rel)

        t0 = time.time()
        print(f"=== InfiniteTalk Starting {out_prefix} (dur={dur:.2f}s, frames={num_frames}) ===", flush=True)
        wf = build_workflow(job, num_frames, wav_rel)
        pid = submit(wf)
        wait_done(pid)
        raw_files = sorted(glob.glob(os.path.join(OUTPUT_DIR, f"{out_prefix}_raw*.mp4")))
        if not raw_files:
            raise RuntimeError(f"Missing raw InfiniteTalk output for {out_prefix}")
        upscale_and_mux(raw_files[-1], clean_wav_abs, final_mp4)
        for rf in raw_files:
            os.remove(rf)
        elapsed = round(time.time() - t0, 1)
        timings[out_prefix] = {"elapsed_sec": elapsed, "frames": num_frames, "out": final_mp4}
        json.dump(timings, open(timings_path, "w"), indent=2)
        print(f"=== InfiniteTalk Finished {out_prefix} in {elapsed}s ===", flush=True)


if __name__ == "__main__":
    main()
