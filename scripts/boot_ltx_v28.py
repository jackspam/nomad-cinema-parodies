"""Swap/boot ComfyUI + LTX-2.5 Dev models (BF16 on >=60GB G4/A100/H100, int8 on L4) in v2.8."""
import os
import subprocess
import time
import urllib.request

from huggingface_hub import hf_hub_download

os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
if os.path.exists("/content/.env.local"):
    for line in open("/content/.env.local"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            k = k.replace("export ", "").strip()
            v = v.strip().strip('"').strip("'")
            if k == "HF_TOKEN":
                os.environ["HF_TOKEN"] = v

subprocess.run(["pkill", "-9", "-f", "ComfyUI/main.py"], check=False)
time.sleep(2)

MODELS = "/content/ComfyUI/models"
for d in ("diffusion_models", "loras", "text_encoders", "vae", "latent_upscale_models"):
    os.makedirs(f"{MODELS}/{d}", exist_ok=True)

vram_mb = float(
    subprocess.check_output(
        ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
        text=True,
    ).strip().splitlines()[0]
)
unet_fn = (
    "diffusion_models/ltx-2.5-22b-dev-transformer-comfy-int8-convrot.safetensors"
    if vram_mb < 60000.0
    else "diffusion_models/ltx-2.5-22b-dev-transformer-bf16.safetensors"
)
print(f"Detected VRAM={vram_mb:.0f} MB -> {unet_fn}", flush=True)

ltx_files = [
    ("Lightricks/LTX-2.5", unet_fn),
    ("Lightricks/LTX-2.5", "loras/ltx-2.5-22b-distilled-lora-450-bf16.safetensors"),
    ("Lightricks/LTX-2.5", "text_encoders/gemma4-12b-with-proj-ltx-2.5-comfy-int8-convrot.safetensors"),
    ("Lightricks/LTX-2.5", "vae/ltx-2.5-video-vae-bf16.safetensors"),
    ("Lightricks/LTX-2.5", "vae/ltx-2.5-audio-vae-bf16.safetensors"),
    ("Lightricks/LTX-2.5", "latent_upscale_models/ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0.safetensors"),
]

for repo, fn in ltx_files:
    dst = os.path.join(MODELS, fn)
    if os.path.exists(dst):
        print("Already have", dst, flush=True)
        continue
    print("Downloading", fn, flush=True)
    hf_hub_download(repo_id=repo, filename=fn, local_dir=MODELS, token=os.environ.get("HF_TOKEN"))

if os.path.exists("/content/.env.local"):
    os.remove("/content/.env.local")

print("ALL_LTX25_DEV_MODELS_READY", flush=True)

subprocess.Popen(
    ["python3", "/content/ComfyUI/main.py", "--listen", "127.0.0.1", "--port", "8188"],
    cwd="/content/ComfyUI",
    stdout=open("/content/comfy.log", "w"),
    stderr=subprocess.STDOUT,
)
for _ in range(60):
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
