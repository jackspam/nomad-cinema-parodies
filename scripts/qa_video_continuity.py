"""Post-render visual continuity audit across all 40 rendered MP4s in Dark Knight v2."""
import os
import subprocess
from PIL import Image, ImageDraw

BASE = "/Users/jack/.gemini/antigravity/scratch/nomad-cinema-parodies"
CLIPS_DIR = f"{BASE}/clips/02_dark_knight_v2"
OUT_DIR = f"{CLIPS_DIR}/continuity"
TMP_FRAMES = "/tmp/dk2_cont_frames"


def ffprobe_dur(path: str) -> float:
    return float(
        subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path],
            text=True,
        ).strip()
    )


def extract_frame(mp4_path: str, ts: float, out_jpg: str):
    subprocess.run(
        ["ffmpeg", "-y", "-ss", f"{ts:.3f}", "-i", mp4_path, "-vframes", "1", "-q:v", "3", out_jpg],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def build_cast_grid(name: str, shot_nums: list[int], cols: int = 3):
    tile_w, tile_h = 640, 277
    rows = (len(shot_nums) + cols - 1) // cols
    canvas = Image.new("RGB", (cols * tile_w, rows * tile_h), (10, 12, 16))
    draw = ImageDraw.Draw(canvas)
    for idx, n in enumerate(shot_nums):
        img_path = f"{TMP_FRAMES}/mid_{n:02d}.jpg"
        im = Image.open(img_path).resize((tile_w, tile_h), Image.Resampling.LANCZOS)
        x = (idx % cols) * tile_w
        y = (idx // cols) * tile_h
        canvas.paste(im, (x, y))
        draw.rectangle([x + 6, y + 6, x + 98, y + 30], fill=(0, 0, 0))
        draw.text((x + 12, y + 11), f"DK2_{n:02d}", fill=(120, 235, 190))
    out_p = f"{OUT_DIR}/{name}.jpg"
    canvas.save(out_p, quality=90)
    print(f"SAVED {out_p} ({len(shot_nums)} shots)")


def build_cut_grid(name: str, pairs: list[tuple[int, int]]):
    tile_w, tile_h = 480, 208
    cols = 2  # each row = [pair A: end | start] | [pair B: end | start]
    rows = (len(pairs) + cols - 1) // cols
    pair_w = tile_w * 2 + 6
    canvas = Image.new("RGB", (cols * pair_w, rows * tile_h), (14, 16, 22))
    draw = ImageDraw.Draw(canvas)
    for idx, (a, b) in enumerate(pairs):
        col = idx % cols
        row = idx // cols
        x0 = col * pair_w
        y0 = row * tile_h
        im_a = Image.open(f"{TMP_FRAMES}/end_{a:02d}.jpg").resize((tile_w, tile_h), Image.Resampling.LANCZOS)
        im_b = Image.open(f"{TMP_FRAMES}/start_{b:02d}.jpg").resize((tile_w, tile_h), Image.Resampling.LANCZOS)
        canvas.paste(im_a, (x0, y0))
        canvas.paste(im_b, (x0 + tile_w + 6, y0))
        draw.rectangle([x0 + 4, y0 + 4, x0 + 130, y0 + 26], fill=(0, 0, 0))
        draw.text((x0 + 10, y0 + 8), f"END {a:02d} -> START {b:02d}", fill=(255, 220, 120))
    out_p = f"{OUT_DIR}/{name}.jpg"
    canvas.save(out_p, quality=90)
    print(f"SAVED {out_p} ({len(pairs)} cuts)")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(TMP_FRAMES, exist_ok=True)

    for n in range(1, 41):
        mp4 = f"{CLIPS_DIR}/dk2_DK2_{n:02d}_00001_.mp4"
        if not os.path.exists(mp4):
            raise FileNotFoundError(mp4)
        dur = ffprobe_dur(mp4)
        extract_frame(mp4, 0.08, f"{TMP_FRAMES}/start_{n:02d}.jpg")
        extract_frame(mp4, dur * 0.40, f"{TMP_FRAMES}/mid_{n:02d}.jpg")
        extract_frame(mp4, max(0.2, dur - 0.12), f"{TMP_FRAMES}/end_{n:02d}.jpg")

    build_cast_grid("grid_gigi", [1, 2, 4, 6, 8, 9, 14, 32, 35], cols=3)
    build_cast_grid("grid_hooman_dark", [3, 5, 7], cols=3)
    build_cast_grid("grid_hooman_bright", [10, 12, 15, 16, 18, 20, 22, 25, 26, 29, 31, 34, 36, 38, 40], cols=3)
    build_cast_grid("grid_damon", [11, 13, 17, 19, 21, 23, 24, 27, 30, 33, 37, 39], cols=3)
    build_cast_grid("grid_deron_zach", [14, 28, 32, 35], cols=2)

    cuts_first = [(i, i + 1) for i in range(1, 21)]
    cuts_second = [(i, i + 1) for i in range(21, 40)]
    build_cut_grid("cuts_01_20", cuts_first)
    build_cut_grid("cuts_21_40", cuts_second)


if __name__ == "__main__":
    main()
