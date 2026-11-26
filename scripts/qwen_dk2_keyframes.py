"""
Generate missing / Hooman-refined Dark Knight v2 keyframes on Colab G4 using Qwen/Qwen-Image-Edit-2509.
Outputs exact 1920x832 Scope JPEGs matching each source YouTube frame's lighting, color, and 35mm texture.
"""
import json
import os
import torch
from PIL import Image
from diffusers import QwenImageEditPlusPipeline

WORK = "/content/dk2_qwen"
JOBS = json.load(open(f"{WORK}/qwen_jobs.json"))
OUT_DIR = f"{WORK}/out"
os.makedirs(OUT_DIR, exist_ok=True)

pipe = QwenImageEditPlusPipeline.from_pretrained(
    "Qwen/Qwen-Image-Edit-2509",
    torch_dtype=torch.bfloat16,
)
pipe.to("cuda")
pipe.set_progress_bar_config(disable=True)

for idx, job in enumerate(JOBS, 1):
    out_p = f"{OUT_DIR}/{job['out_name']}"
    if os.path.exists(out_p):
        print(f"[{idx}/{len(JOBS)}] Skipping existing {job['out_name']}", flush=True)
        continue
    imgs = [Image.open(f"{WORK}/in/{fn}").convert("RGB") for fn in job["images"]]
    w, h = imgs[0].size
    # Ensure exact 1920x832 divisible by 16 for Qwen
    gen = torch.Generator(device="cuda").manual_seed(job.get("seed", 4242 + idx))
    res = pipe(
        image=imgs,
        prompt=job["prompt"],
        negative_prompt="waxy skin, plastic face, smooth airbrushed skin, cartoon, 3d render, Heath Ledger likeness, receding blond hair, neon teal-orange relighting, open screaming mouth, watermark, blurry",
        num_inference_steps=36,
        true_cfg_scale=4.0,
        height=h,
        width=w,
        generator=gen,
    ).images[0]
    res = res.convert("RGB").resize((1920, 832), Image.Resampling.LANCZOS)
    res.save(out_p, quality=95)
    print(f"[{idx}/{len(JOBS)}] SAVED {out_p} ({res.size})", flush=True)

print("ALL_QWEN_DK2_KEYFRAMES_DONE", flush=True)
