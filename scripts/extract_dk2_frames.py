import glob
import json
import os
import re
import subprocess
from PIL import Image, ImageDraw, ImageFont

BASE = "/Users/jack/.gemini/antigravity/scratch/nomad-cinema-parodies"
SRC_MP4 = f"{BASE}/refs/yt_src/02_dark_knight_hd_hq.mp4"
OUT_DIR = f"{BASE}/refs/yt/02_dark_knight_v2"
FRAMES_DIR = f"{OUT_DIR}/frames"
SHEETS_DIR = f"{OUT_DIR}/sheets"
os.makedirs(FRAMES_DIR, exist_ok=True)
os.makedirs(SHEETS_DIR, exist_ok=True)

# Clean old frames if re-running
for p in glob.glob(f"{FRAMES_DIR}/*.jpg") + glob.glob(f"{SHEETS_DIR}/*.jpg"):
    os.remove(p)

CROP_SCALE = "crop=1848:800:36:140,scale=1920:832:flags=lanczos"

# 1. Extract every 1s frame cleanly
fps_dir = f"{OUT_DIR}/_tmp_fps"
os.makedirs(fps_dir, exist_ok=True)
for p in glob.glob(f"{fps_dir}/*.jpg"):
    os.remove(p)

subprocess.run(
    [
        "ffmpeg", "-y", "-i", SRC_MP4,
        "-vf", f"{CROP_SCALE},fps=1",
        "-q:v", "2", f"{fps_dir}/sec_%04d.jpg",
    ],
    check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
)

# 2. Extract every scene boundary frame + capture timestamps
sc_dir = f"{OUT_DIR}/_tmp_sc"
os.makedirs(sc_dir, exist_ok=True)
for p in glob.glob(f"{sc_dir}/*.jpg"):
    os.remove(p)

sc_res = subprocess.run(
    [
        "ffmpeg", "-y", "-i", SRC_MP4,
        "-vf", f"select='gt(scene,0.14)',showinfo,{CROP_SCALE}",
        "-fps_mode", "vfr", "-q:v", "2", f"{sc_dir}/sc_%04d.jpg",
    ],
    text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
)
if sc_res.returncode != 0:
    raise RuntimeError(sc_res.stderr[-1000:])
sc_times = [float(m.group(1)) for m in re.finditer(r"pts_time:([0-9.]+)", sc_res.stderr)]

records = []
for idx, p in enumerate(sorted(glob.glob(f"{fps_dir}/sec_*.jpg")), start=1):
    t = float(idx - 1)
    records.append({"t": t, "src": p, "kind": "1fps"})

sc_files = sorted(glob.glob(f"{sc_dir}/sc_*.jpg"))
for p, t in zip(sc_files, sc_times):
    # Keep scene cuts even if near a 1fps frame if > 0.25s away, otherwise replace to catch exact cut
    if any(abs(r["t"] - t) < 0.25 for r in records):
        continue
    records.append({"t": round(t, 2), "src": p, "kind": "cut"})

records.sort(key=lambda r: r["t"])
manifest = []
for i, r in enumerate(records, start=1):
    fname = f"dk2_yt_{i:04d}.jpg"
    dst = f"{FRAMES_DIR}/{fname}"
    os.replace(r["src"], dst)
    manifest.append({"frame": fname, "t": r["t"], "kind": r["kind"]})

for tmp in (fps_dir, sc_dir):
    for p in glob.glob(f"{tmp}/*.jpg"):
        os.remove(p)
    os.rmdir(tmp)

json.dump(manifest, open(f"{OUT_DIR}/frames_manifest.json", "w"), indent=2)
print(f"EXTRACTED {len(manifest)} FRAMES (1920x832 SDR) into {FRAMES_DIR}")

# 3. Build 5x6 (30 per sheet) contact sheets labeled with frame index & timestamp
COLS, ROWS = 5, 6
TW, TH = 384, 166
PER_SHEET = COLS * ROWS
for s_idx in range(0, len(manifest), PER_SHEET):
    chunk = manifest[s_idx:s_idx + PER_SHEET]
    canvas = Image.new("RGB", (COLS * TW, ROWS * TH), (15, 15, 15))
    draw = ImageDraw.Draw(canvas)
    for k, item in enumerate(chunk):
        r, c = divmod(k, COLS)
        x, y = c * TW, r * TH
        im = Image.open(f"{FRAMES_DIR}/{item['frame']}").resize((TW, TH), Image.Resampling.LANCZOS)
        canvas.paste(im, (x, y))
        label = f"{item['frame'].replace('dk2_yt_','').replace('.jpg','')} | {item['t']:.1f}s {'*' if item['kind']=='cut' else ''}"
        draw.rectangle([x, y, x + 150, y + 20], fill=(0, 0, 0))
        draw.text((x + 4, y + 4), label, fill=(255, 230, 120))
    sheet_num = (s_idx // PER_SHEET) + 1
    out_sheet = f"{SHEETS_DIR}/sheet_{sheet_num:02d}.jpg"
    canvas.save(out_sheet, quality=92)
    print(f"SAVED {out_sheet} ({len(chunk)} frames)")
