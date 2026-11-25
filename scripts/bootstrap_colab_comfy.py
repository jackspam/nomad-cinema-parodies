import os
import subprocess
import time
import urllib.request
from huggingface_hub import hf_hub_download

MODELS_DIR = "/content/ComfyUI/models"
os.makedirs("/content/ComfyUI/input", exist_ok=True)
os.makedirs("/content/ComfyUI/output/video", exist_ok=True)

files = [
    "diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors",
    "loras/minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors",
    "text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors",
    "vae/minimax_h3_video_vae_int8_convrot.safetensors",
    "vae/minimax_h3_audio_vae_fp32.safetensors",
]

for fn in files:
    dst = os.path.join(MODELS_DIR, fn)
    if os.path.exists(dst):
        print("Already have", dst, flush=True)
        continue
    print("Downloading", fn, flush=True)
    hf_hub_download(repo_id="Comfy-Org/MiniMax-H3", filename=fn, local_dir=MODELS_DIR)

print("ALL_H3_MODELS_READY", flush=True)

try:
    with urllib.request.urlopen("http://127.0.0.1:8188/system_stats", timeout=2) as r:
        if r.status == 200:
            print("COMFY_ALREADY_RUNNING", flush=True)
            raise SystemExit(0)
except Exception:
    pass

subprocess.Popen(
    ["python3", "/content/ComfyUI/main.py", "--listen", "127.0.0.1", "--port", "8188"],
    cwd="/content/ComfyUI",
    stdout=open("/content/comfy.log", "w"),
    stderr=subprocess.STDOUT,
)
for _ in range(45):
    try:
        with urllib.request.urlopen("http://127.0.0.1:8188/system_stats", timeout=2) as r:
            if r.status == 200:
                print("COMFY_STARTED_OK", flush=True)
                break
    except Exception:
        pass
    time.sleep(2)
else:
    raise RuntimeError("ComfyUI failed to start")
