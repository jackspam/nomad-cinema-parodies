"""Bootstrap ComfyUI + LTX-2.5 Dev BF16 + Refiner + Qwen-Image-Edit deps on dk2-g4."""
import os
import subprocess
import time
import urllib.request

os.makedirs("/content", exist_ok=True)
if not os.path.exists("/content/ComfyUI"):
    subprocess.run(["git", "clone", "--depth", "1", "https://github.com/comfyanonymous/ComfyUI.git", "/content/ComfyUI"], check=True)
    subprocess.run(["pip", "install", "-q", "-r", "/content/ComfyUI/requirements.txt"], check=True)

vhs_dir = "/content/ComfyUI/custom_nodes/ComfyUI-VideoHelperSuite"
if not os.path.exists(vhs_dir):
    subprocess.run(["git", "clone", "--depth", "1", "https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git", vhs_dir], check=True)
    subprocess.run(["pip", "install", "-q", "-r", f"{vhs_dir}/requirements.txt"], check=True)

subprocess.run(["pip", "install", "-q", "-U", "huggingface_hub", "hf_transfer", "diffusers", "transformers", "accelerate", "qwen-vl-utils"], check=True)
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"

from huggingface_hub import hf_hub_download

MODELS = "/content/ComfyUI/models"
os.makedirs("/content/ComfyUI/input", exist_ok=True)
os.makedirs("/content/ComfyUI/output/video", exist_ok=True)

ltx_files = [
    ("Lightricks/LTX-2.5", "diffusion_models/ltx-2.5-22b-dev-transformer-bf16.safetensors"),
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
    hf_hub_download(repo_id=repo, filename=fn, local_dir=MODELS)

print("ALL_LTX25_DEV_MODELS_READY", flush=True)

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
