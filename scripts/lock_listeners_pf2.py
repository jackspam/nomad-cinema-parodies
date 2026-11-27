"""Soft-feathered horizontal spatial listener-lock composite for multi-face Pulp Fiction v2 InfiniteTalk shots."""
import os
import subprocess
import sys
import cv2
import numpy as np

BASE = "/Users/jack/.gemini/antigravity/scratch/nomad-cinema-parodies"

# Exact verified x-coordinates on 1920x832 Scope frames:
LOCK_SPECS = {
    "PF2_01": ("refs/05_pulp_fiction_v2/pf2_shot01_start.jpg", [("left_of", 980, 22)]),
    "PF2_05": ("refs/05_pulp_fiction_v2/pf2_shot05_start.jpg", [("left_of", 980, 22)]),
    "PF2_07": ("refs/05_pulp_fiction_v2/pf2_shot07_start.jpg", [("left_of", 850, 25)]),
    "PF2_09": ("refs/05_pulp_fiction_v2/pf2_shot09_start.jpg", [("left_of", 1290, 22)]),
    "PF2_42": ("refs/05_pulp_fiction_v2/pf2_shot42_start.jpg", [("left_of", 1080, 22)]),
}


def build_lock_alpha(w: int, h: int, zones: list) -> np.ndarray:
    xs = np.arange(w, dtype=np.float32)
    mask_x = np.zeros(w, dtype=np.float32)
    for kind, bx, hw in zones:
        if kind == "right_of":
            t = np.clip((xs - (bx - hw)) / max(1.0, 2.0 * hw), 0.0, 1.0)
        elif kind == "left_of":
            t = np.clip(((bx + hw) - xs) / max(1.0, 2.0 * hw), 0.0, 1.0)
        else:
            raise ValueError(kind)
        smooth = 0.5 - 0.5 * np.cos(np.pi * t)
        mask_x = np.maximum(mask_x, smooth)
    return np.broadcast_to(mask_x[None, :, None], (h, w, 1)).copy()


def lock_shot(shot_id: str):
    if shot_id not in LOCK_SPECS:
        raise ValueError(f"No lock spec for {shot_id}")
    ref_rel, zones = LOCK_SPECS[shot_id]
    mp4_path = f"{BASE}/clips/05_pulp_fiction_v2/pf2_{shot_id}_00001_.mp4"
    ref_img = cv2.imread(f"{BASE}/{ref_rel}")
    if ref_img is None:
        raise FileNotFoundError(ref_rel)

    cap = cv2.VideoCapture(mp4_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    ref_resized = cv2.resize(ref_img, (w, h), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)

    alpha = build_lock_alpha(w, h, zones)
    inv_alpha = 1.0 - alpha

    tmp_vid = mp4_path + ".lock_tmp.mp4"
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(tmp_vid, fourcc, fps, (w, h))

    n_frames = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        blended = (frame.astype(np.float32) * inv_alpha + ref_resized * alpha).clip(0, 255).astype(np.uint8)
        out.write(blended)
        n_frames += 1

    cap.release()
    out.release()

    final_tmp = mp4_path + ".mux_tmp.mp4"
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", tmp_vid, "-i", mp4_path,
            "-map", "0:v:0", "-map", "1:a:0",
            "-c:v", "libx264", "-crf", "15", "-preset", "fast", "-pix_fmt", "yuv420p",
            "-c:a", "copy", "-shortest", final_tmp,
        ],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    os.remove(tmp_vid)
    os.replace(final_tmp, mp4_path)
    print(f"LOCKED_LISTENERS [{shot_id}] -> {n_frames} frames composited cleanly into {mp4_path}")


if __name__ == "__main__":
    targets = sys.argv[1:] or ["PF2_01", "PF2_05", "PF2_07", "PF2_09"]
    for sid in targets:
        lock_shot(sid)
