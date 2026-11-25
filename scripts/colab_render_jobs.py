import glob
import json
import os
import sys
import time
import urllib.request

COMFY = "http://127.0.0.1:8188"


def build_workflow(job):
    shot_image = job["images"][0]
    face_image = job["images"][1] if len(job["images"]) > 1 else None
    g = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "minimax_h3_ref2va_pruned_int8_convrot.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["1", 0], "lora_name": "minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors", "strength_model": 1.0}},
        "3": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors", "type": "minimax", "device": "default"}},
        "4": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_video_vae_int8_convrot.safetensors"}},
        "5": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_audio_vae_fp32.safetensors"}},
        "18": {"class_type": "LoadImage", "inputs": {"image": shot_image}},
        "8": {
            "class_type": "MiniMaxH3ReferenceToVideo",
            "inputs": {
                "clip": ["3", 0],
                "vae": ["4", 0],
                "audio_vae": ["5", 0],
                "prompt": job["prompt"],
                "width": 1344,
                "height": 768,
                "length": job["length"],
                "ref_image_size": "match",
            },
        },
        "9": {"class_type": "BasicGuider", "inputs": {"model": ["2", 0], "conditioning": ["8", 0]}},
        "10": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "res_multistep"}},
        "11": {"class_type": "BasicScheduler", "inputs": {"model": ["2", 0], "scheduler": "simple", "steps": 4, "denoise": 1.0}},
        "12": {"class_type": "RandomNoise", "inputs": {"noise_seed": job["seed"]}},
        "13": {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": ["12", 0], "guider": ["9", 0], "sampler": ["10", 0], "sigmas": ["11", 0], "latent_image": ["8", 1]}},
        "14": {"class_type": "VAEDecode", "inputs": {"samples": ["13", 0], "vae": ["4", 0]}},
        "15": {"class_type": "VAEDecodeAudio", "inputs": {"samples": ["13", 0], "vae": ["5", 0]}},
        "16": {"class_type": "CreateVideo", "inputs": {"images": ["14", 0], "audio": ["15", 0], "fps": 24}},
        "17": {"class_type": "SaveVideo", "inputs": {"video": ["16", 0], "filename_prefix": f"video/{job['prefix']}", "format": "auto", "codec": "auto"}},
    }
    if face_image:
        g["6"] = {"class_type": "LoadImage", "inputs": {"image": face_image}}
        g["8"]["inputs"]["ref_images.ref_image_0"] = ["6", 0]
        g["8"]["inputs"]["ref_images.ref_image_1"] = ["18", 0]
    else:
        g["8"]["inputs"]["ref_images.ref_image_0"] = ["18", 0]

    if job.get("audio"):
        g["7"] = {"class_type": "LoadAudio", "inputs": {"audio": job["audio"]}}
        g["8"]["inputs"]["ref_audios.ref_audio_0"] = ["7", 0]
    return g


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
        time.sleep(8)


def wait_queue_empty():
    while True:
        with urllib.request.urlopen(f"{COMFY}/queue") as r:
            q = json.loads(r.read())
        if not q.get("queue_running") and not q.get("queue_pending"):
            return
        time.sleep(8)


def main():
    jobs_path = sys.argv[1]
    jobs = json.load(open(jobs_path))
    timings_path = "/content/render_timing_log.json"
    timings = json.load(open(timings_path)) if os.path.exists(timings_path) else {}

    wait_queue_empty()

    for job in jobs:
        prefix = job["prefix"]
        existing = sorted(glob.glob(f"/content/ComfyUI/output/video/{prefix}_*.mp4"))
        if existing:
            print(f"=== Skipping {prefix} (already rendered: {existing[-1]}) ===", flush=True)
            continue
        t0 = time.time()
        print(f"=== Starting {prefix} (len={job['length']}) ===", flush=True)
        pid = submit(build_workflow(job))
        out = wait_done(pid)
        elapsed = round(time.time() - t0, 1)
        timings[prefix] = {"elapsed_sec": elapsed, "frames": job["length"], "outputs": out.get("17", {}).get("images", [])}
        json.dump(timings, open(timings_path, "w"), indent=2)
        print(f"=== Finished {prefix} in {elapsed}s ===", flush=True)
        print(json.dumps(out.get("17", {}), indent=2), flush=True)


if __name__ == "__main__":
    main()
