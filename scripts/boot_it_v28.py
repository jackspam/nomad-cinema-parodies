import os, subprocess, time, urllib.request

os.makedirs("/content", exist_ok=True)
if not os.path.exists("/content/ComfyUI"):
    subprocess.run(["git", "clone", "--depth", "1", "https://github.com/comfyanonymous/ComfyUI.git", "/content/ComfyUI"], check=True)
    subprocess.run(["pip", "install", "-q", "-r", "/content/ComfyUI/requirements.txt"], check=True)

for repo_url, name in [
    ("https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git", "ComfyUI-VideoHelperSuite"),
    ("https://github.com/kijai/ComfyUI-WanVideoWrapper.git", "ComfyUI-WanVideoWrapper"),
]:
    ndir = f"/content/ComfyUI/custom_nodes/{name}"
    if not os.path.exists(ndir):
        subprocess.run(["git", "clone", "--depth", "1", repo_url, ndir], check=True)
        req = f"{ndir}/requirements.txt"
        if os.path.exists(req):
            subprocess.run(["pip", "install", "-q", "-r", req], check=True)

subprocess.run(["pip", "install", "-q", "-U", "huggingface_hub", "hf_transfer", "accelerate", "librosa", "soundfile", "einops"], check=True)
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"

# Patch ComfyUI-WanVideoWrapper MultiTalk for transformers v5 compatibility
p_w2v = "/content/ComfyUI/custom_nodes/ComfyUI-WanVideoWrapper/multitalk/wav2vec2.py"
if os.path.exists(p_w2v):
    src = open(p_w2v).read()
    if "capture_outputs" not in src:
        src = src.replace(
            "from transformers.modeling_outputs import BaseModelOutput\n",
            "from transformers.modeling_outputs import BaseModelOutput\nfrom transformers.utils.generic import merge_with_config_defaults\nfrom transformers.utils.output_capturing import capture_outputs\n",
        )
        src = src.replace(
            "    def forward(\n",
            "    @merge_with_config_defaults\n    @capture_outputs(tie_last_hidden_states=False)\n    def forward(\n",
            1,
        )
        open(p_w2v, "w").write(src)

p_nodes = "/content/ComfyUI/custom_nodes/ComfyUI-WanVideoWrapper/multitalk/nodes.py"
if os.path.exists(p_nodes):
    nsrc = open(p_nodes).read()
    old_line = "audio_emb = torch.stack(embeddings.hidden_states[1:], dim=1).squeeze(0)"
    new_line = "audio_emb = torch.stack(embeddings.hidden_states[1:] if len(embeddings.hidden_states) > 12 else embeddings.hidden_states, dim=1).squeeze(0)"
    if old_line in nsrc:
        open(p_nodes, "w").write(nsrc.replace(old_line, new_line))

import sys, torch
from transformers import Wav2Vec2Config
sys.path.insert(0, "/content/ComfyUI/custom_nodes/ComfyUI-WanVideoWrapper")
from multitalk.wav2vec2 import Wav2Vec2Model as MTWav2Vec2
m = MTWav2Vec2(Wav2Vec2Config())
out = m(torch.randn(1, 16000), seq_len=24, output_hidden_states=True)
hs = out.hidden_states[1:] if len(out.hidden_states) > 12 else out.hidden_states
st = torch.stack(hs, dim=1).squeeze(0)
assert st.shape == (12, 24, 768), f"Unexpected MultiTalk emb shape {st.shape}"
print("VERIFIED_MULTITALK_WAV2VEC2:", st.shape, flush=True)

from huggingface_hub import hf_hub_download

M = "/content/ComfyUI/models"
os.makedirs("/content/ComfyUI/input", exist_ok=True)
os.makedirs("/content/ComfyUI/output/video", exist_ok=True)
for sub in ("clip_vision", "vae", "loras", "diffusion_models", "unet", "wav2vec2", "transformers", "text_encoders"):
    os.makedirs(f"{M}/{sub}", exist_ok=True)

DOWNLOADS = [
    ("Comfy-Org/Wan_2.1_ComfyUI_repackaged", "split_files/clip_vision/clip_vision_h.safetensors", f"{M}/clip_vision/clip_vision_h.safetensors", []),
    ("Kijai/WanVideo_comfy", "Wan2_1_VAE_bf16.safetensors", f"{M}/vae/Wan2_1_VAE_bf16.safetensors", []),
    ("Kijai/WanVideo_comfy", "umt5-xxl-enc-fp8_e4m3fn.safetensors", f"{M}/text_encoders/umt5-xxl-enc-fp8_e4m3fn.safetensors", []),
    ("Kijai/WanVideo_comfy", "Lightx2v/lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors", f"{M}/loras/lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors", []),
    ("Kijai/WanVideo_comfy", "InfiniteTalk/Wan2_1-InfiniTetalk-Single_fp16.safetensors", f"{M}/diffusion_models/Wan2_1-InfiniTetalk-Single_fp16.safetensors", [f"{M}/unet/Wan2_1-InfiniTetalk-Single_fp16.safetensors"]),
    ("Kijai/WanVideo_comfy_fp8_scaled", "I2V/Wan2_1-I2V-14B-480p_fp8_e4m3fn_scaled_KJ.safetensors", f"{M}/diffusion_models/Wan2_1-I2V-14B-480p_fp8_e4m3fn_scaled_KJ.safetensors", [f"{M}/unet/Wan2_1-I2V-14B-480p_fp8_e4m3fn_scaled_KJ.safetensors"]),
    ("Kijai/wav2vec2_safetensors", "wav2vec2-chinese-base_fp16.safetensors", f"{M}/wav2vec2/wav2vec2-chinese-base_fp16.safetensors", [f"{M}/transformers/wav2vec2-chinese-base_fp16.safetensors"]),
]

for repo, remote_fn, dst, extra_links in DOWNLOADS:
    if not os.path.exists(dst):
        print(f"Downloading {remote_fn} -> {dst}", flush=True)
        local_dl = hf_hub_download(repo_id=repo, filename=remote_fn)
        os.symlink(local_dl, dst)
    for el in extra_links:
        if not os.path.exists(el):
            os.symlink(dst, el)

print("ALL_INFINITETALK_MODELS_READY", flush=True)

try:
    with urllib.request.urlopen("http://127.0.0.1:8188/system_stats", timeout=2) as r:
        if r.status == 200:
            raise SystemExit(0)
except Exception:
    pass

subprocess.Popen(["python3", "/content/ComfyUI/main.py", "--listen", "127.0.0.1", "--port", "8188"],
                 cwd="/content/ComfyUI", stdout=open("/content/comfy.log", "w"), stderr=subprocess.STDOUT)
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
