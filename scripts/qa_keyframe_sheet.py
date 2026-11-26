"""
Hardened Keyframe QA Sheet Generator (Detection Gate #1: Anti-Wax & Movie-Match)

Usage:
  python3 scripts/qa_keyframe_sheet.py <yt_frame> <gen_frame> <out_qa_png> [label]
"""
import math
import os
import sys
import numpy as np
from PIL import Image, ImageDraw

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False


def detect_primary_face_box(img_rgb: np.ndarray, side: str = "auto"):
    """Locate the sharp, high-contrast foreground face using Sobel sharpness density (works on both normal skin & Joker paint)."""
    h, w, _ = img_rgb.shape
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY) if HAS_CV2 else img_rgb.mean(axis=2).astype(np.uint8)
    gx = np.abs(np.diff(gray.astype(np.float32), axis=1, prepend=gray[:, :1]))
    gy = np.abs(np.diff(gray.astype(np.float32), axis=0, prepend=gray[:1, :]))
    grad = gx + gy
    # Search window in upper 78% of frame where subject heads live
    win_h = int(h * 0.48)
    win_w = int(h * 0.48)
    x_min = 0 if side in ("auto", "left") else int(w * 0.25) if side == "center" else int(w * 0.45)
    x_max = int(w * 0.55) if side == "left" else int(w * 0.78) if side == "center" else w
    best_score, best_box = -1.0, (max(0, w // 2 - win_w // 2), max(0, int(h * 0.38) - win_h // 2), min(w, w // 2 + win_w // 2), min(h, int(h * 0.38) + win_h // 2))
    step = 48
    for cy in range(int(h * 0.22), int(h * 0.62), step):
        for cx in range(max(win_w // 2, x_min), min(w - win_w // 2, x_max), step):
            x1, y1 = max(0, cx - win_w // 2), max(0, cy - win_h // 2)
            x2, y2 = min(w, x1 + win_w), min(h, y1 + win_h)
            patch = grad[y1:y2, x1:x2]
            # Slight center-horizontal & upper-head prior to prefer in-focus face over blurry foreground shoulders
            center_prior = 1.0 - 0.25 * abs(cx - w * 0.5) / (w * 0.5)
            score = float(np.mean(patch)) * center_prior
            if score > best_score:
                best_score = score
                best_box = (x1, y1, x2, y2)
    return best_box


def compute_metrics(yt_rgb: np.ndarray, gen_rgb: np.ndarray, face_box):
    x1, y1, x2, y2 = face_box
    crop = gen_rgb[y1:y2, x1:x2]
    yt_crop = yt_rgb[y1:y2, x1:x2]
    if HAS_CV2:
        yt_lab = cv2.cvtColor(cv2.resize(yt_rgb, (320, 140)), cv2.COLOR_RGB2LAB).astype(np.float32)
        gen_lab = cv2.cvtColor(cv2.resize(gen_rgb, (320, 140)), cv2.COLOR_RGB2LAB).astype(np.float32)
        # Compare mean & std per LAB channel (wall color / contrast parity)
        mean_diff = float(np.linalg.norm(yt_lab.mean(axis=(0, 1)) - gen_lab.mean(axis=(0, 1))))
        gray_face = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY)
        lap_var = float(cv2.Laplacian(gray_face, cv2.CV_64F).var())
        yt_gray_face = cv2.cvtColor(yt_crop, cv2.COLOR_RGB2GRAY)
        yt_lap_var = float(cv2.Laplacian(yt_gray_face, cv2.CV_64F).var())
    else:
        mean_diff = float(np.linalg.norm(yt_rgb.mean(axis=(0, 1)) - gen_rgb.mean(axis=(0, 1))))
        lap_var = float(np.std(np.diff(crop.astype(np.float32), axis=1)) ** 2)
        yt_lap_var = float(np.std(np.diff(yt_crop.astype(np.float32), axis=1)) ** 2)
    return {
        "lab_mean_diff": round(mean_diff, 2),
        "face_texture_laplacian": round(lap_var, 1),
        "yt_ref_laplacian": round(yt_lap_var, 1),
    }


def make_qa_sheet(yt_path: str, gen_path: str, out_path: str, label: str = ""):
    yt_im = Image.open(yt_path).convert("RGB")
    gen_im = Image.open(gen_path).convert("RGB")
    if yt_im.size != gen_im.size:
        yt_im = yt_im.resize(gen_im.size, Image.Resampling.LANCZOS)

    yt_arr = np.array(yt_im)
    gen_arr = np.array(gen_im)
    box = detect_primary_face_box(gen_arr)
    metrics = compute_metrics(yt_arr, gen_arr, box)

    # Panel height 512: (Left) YT frame 960x416, (Center) Gen frame 960x416, (Right) 1:1 512x512 face crop
    pw, ph = 960, 416
    crop_w = 512
    canvas = Image.new("RGB", (pw * 2 + crop_w, 560), (14, 14, 16))
    draw = ImageDraw.Draw(canvas)

    canvas.paste(yt_im.resize((pw, ph), Image.Resampling.LANCZOS), (0, 48))
    canvas.paste(gen_im.resize((pw, ph), Image.Resampling.LANCZOS), (pw, 48))

    face_crop = gen_im.crop(box).resize((crop_w, crop_w), Image.Resampling.LANCZOS)
    canvas.paste(face_crop, (pw * 2, 48))

    # Draw bounding box on center image for clarity
    sx = pw / gen_im.width
    sy = ph / gen_im.height
    draw.rectangle(
        [pw + box[0] * sx, 48 + box[1] * sy, pw + box[2] * sx, 48 + box[3] * sy],
        outline=(255, 220, 80), width=2,
    )

    wax_flag = "OK_TEXTURE" if metrics["face_texture_laplacian"] >= max(25.0, metrics["yt_ref_laplacian"] * 0.45) else "WARN_LOW_TEXTURE_OR_WAXY"
    col_flag = "OK_COLOR" if metrics["lab_mean_diff"] <= 28.0 else "WARN_COLOR_DRIFT"
    header = (
        f"{label}  |  YOUTUBE SOURCE (LEFT)  vs  GENERATED KEYFRAME (CENTER)  vs  1:1 FACE DETAIL (RIGHT)  "
        f"|  LAB_diff={metrics['lab_mean_diff']} ({col_flag})  |  FaceLap={metrics['face_texture_laplacian']} vs YT={metrics['yt_ref_laplacian']} ({wax_flag})"
    )
    draw.text((14, 14), header, fill=(245, 235, 160))

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    canvas.save(out_path)
    print(f"QA_KEYFRAME {label}: LAB_diff={metrics['lab_mean_diff']} ({col_flag}), FaceLap={metrics['face_texture_laplacian']} vs YT={metrics['yt_ref_laplacian']} ({wax_flag}) -> {out_path}")
    return metrics


if __name__ == "__main__":
    yt_p, gen_p, out_p = sys.argv[1], sys.argv[2], sys.argv[3]
    lbl = sys.argv[4] if len(sys.argv) > 4 else os.path.basename(gen_p)
    make_qa_sheet(yt_p, gen_p, out_p, lbl)
