"""Build per-character cross-shot consistency contact grids across all 71 Dark Knight v2 keyframes."""
import json
import os
import math
from PIL import Image, ImageDraw

BASE = "/Users/jack/.gemini/antigravity/scratch/nomad-cinema-parodies"
JOBS = {j["shot_id"]: j for j in json.load(open(f"{BASE}/scripts/02_dark_knight_v2_jobs.json"))}
SCRIPT = json.load(open(f"{BASE}/scripts/02_dark_knight_v2_script.json"))["shots"]
OUT_DIR = f"{BASE}/refs/02_dark_knight_v2/coherence"
os.makedirs(OUT_DIR, exist_ok=True)


def make_grid(title: str, hero_name: str, items: list[tuple[str, str]], out_name: str, cols: int = 4):
    # Prepend Hero Anchor at index 0
    tiles = [("HERO ANCHOR", hero_name)] + items
    TW, TH = 480, 208
    LBL = 28
    HDR = 44
    rows = math.ceil(len(tiles) / cols)
    canvas = Image.new("RGB", (cols * TW, HDR + rows * (TH + LBL)), (14, 15, 20))
    draw = ImageDraw.Draw(canvas)
    draw.text((14, 14), title, fill=(140, 220, 255))

    for idx, (tag, fn) in enumerate(tiles):
        r, c = divmod(idx, cols)
        x0, y0 = c * TW, HDR + r * (TH + LBL)
        p = f"{BASE}/refs/02_dark_knight_v2/{fn}"
        if os.path.exists(p):
            im = Image.open(p).convert("RGB").resize((TW, TH), Image.Resampling.LANCZOS)
            canvas.paste(im, (x0, y0))
        color = (110, 255, 160) if idx == 0 else (235, 235, 240)
        draw.text((x0 + 8, y0 + TH + 6), f"{tag}: {fn}", fill=color)
        if idx == 0:
            draw.rectangle([x0, y0, x0 + TW - 1, y0 + TH - 1], outline=(110, 255, 160), width=3)

    out_p = f"{OUT_DIR}/{out_name}"
    canvas.save(out_p, quality=92)
    print(f"WROTE {out_p} ({len(items)} frames)")


def collect(pred):
    out = []
    for sh in SCRIPT:
        if not pred(sh):
            continue
        sid = sh["shot_id"]
        j = JOBS[sid]
        out.append((f"{sid} START", j["start_image"]))
        if j.get("end_image"):
            out.append((f"{sid} END", j["end_image"]))
    return out


make_grid(
    "GIGI (Commissioner Gordon) — All Appearances vs Hero Anchor dk2_shot02_start.jpg",
    "dk2_shot02_start.jpg",
    collect(lambda s: "gigi" in s.get("speaker", "").lower() or s["shot_id"] in ("DK2_32", "DK2_35", "DK2_28")),
    "gigi_all.jpg",
)
make_grid(
    "HOOMAN ACT 1 (Dark Purple Coat) — All Appearances vs Hero Anchor dk2_shot03_start.jpg",
    "dk2_shot03_start.jpg",
    collect(lambda s: s["act"] == 1 and "hooman" in s.get("speaker", "").lower()),
    "hooman_act1_dark.jpg",
)
make_grid(
    "HOOMAN ACT 2-3 (Bright / Coatless Hex Shirt + Vest) — All Appearances vs Hero Anchor dk2_shot12_start.jpg",
    "dk2_shot12_start.jpg",
    collect(lambda s: s["act"] >= 2 and ("hooman" in s.get("speaker", "").lower() or s["shot_id"] in ("DK2_11", "DK2_17", "DK2_21", "DK2_23", "DK2_24", "DK2_27", "DK2_30"))),
    "hooman_act23_bright.jpg",
)
make_grid(
    "DAMON (Cowl-less Batman) — All Appearances vs Hero Anchor dk2_shot11_start.jpg",
    "dk2_shot11_start.jpg",
    collect(lambda s: "damon" in s.get("speaker", "").lower() or s["shot_id"] in ("DK2_10", "DK2_18", "DK2_29", "DK2_31", "DK2_38", "DK2_40")),
    "damon_all.jpg",
)
make_grid(
    "DERON & ZACH — All Observation/Corridor Appearances",
    "dk2_shot14_start.jpg",
    collect(lambda s: any(k in s.get("speaker", "").lower() for k in ("deron", "zach")) or s["shot_id"] == "DK2_28"),
    "deron_zach_all.jpg",
)
