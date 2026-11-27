"""
Hardened SyncNet + Final-1.2s Expression Strip Verifier
Run with: /Users/jack/.venvs/qa/bin/python scripts/verify_syncnet.py <clip_mp4> <vo_mp3> <out_tail_strip_png> [--speaker-side auto|left|center|right] [--label SID] [--min-conf 4.5]
"""
import argparse
import os
import subprocess
import sys
import tempfile
import cv2
from PIL import Image, ImageDraw
from syncnet_python import SyncNetPipeline

S3FD_W = "/Users/jack/.venvs/qa/weights/sfd_face.pth"
SYNCNET_W = "/Users/jack/.venvs/qa/weights/syncnet_v2.model"


def crop_speaker_video(src_mp4: str, speaker_side: str, dst_mp4: str) -> str:
    """Horizontally crop multi-person clips so SyncNet tracks ONLY the speaking Nomad."""
    if speaker_side == "left":
        vf = "crop=iw*0.60:ih:0:0"
    elif speaker_side == "right":
        vf = "crop=iw*0.60:ih:iw*0.40:0"
    elif speaker_side == "far_right":
        vf = "crop=iw*0.32:ih:iw*0.68:0"
    elif speaker_side == "center":
        vf = "crop=iw*0.72:ih:iw*0.14:0"
    else:
        return src_mp4
    subprocess.run(
        ["ffmpeg", "-y", "-i", src_mp4, "-vf", vf, "-c:a", "copy", "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", dst_mp4],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    return dst_mp4


def make_tail_strip(clip_mp4: str, speaker_side: str, out_png: str, label: str, line_summary: str):
    """Save a 6-frame strip across the FINAL 1.2 seconds so unprompted smiles/morphs are caught immediately."""
    cap = cv2.VideoCapture(clip_mp4)
    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    frames = []
    while True:
        ok, bgr = cap.read()
        if not ok:
            break
        frames.append(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
    cap.release()
    if not frames:
        return
    H, W, _ = frames[0].shape
    n = len(frames)
    # 6 frames evenly spaced across last 1.2s (or whole clip if shorter)
    tail_frames = min(n, max(6, int(round(1.2 * fps))))
    start_f = max(0, n - tail_frames)
    idxs = [min(n - 1, start_f + int(round(i * (tail_frames - 1) / 5.0))) for i in range(6)]

    # Crop around speaker horizontal band
    if speaker_side == "left":
        x1, x2 = 0, int(W * 0.58)
    elif speaker_side == "right":
        x1, x2 = int(W * 0.42), W
    elif speaker_side == "far_right":
        x1, x2 = int(W * 0.68), W
    else:
        x1, x2 = int(W * 0.16), int(W * 0.84)

    TW, TH = 320, 240
    HDR = 38
    canvas = Image.new("RGB", (6 * TW, HDR + TH + 24), (14, 15, 20))
    draw = ImageDraw.Draw(canvas)
    draw.text((10, 10), f"{label} FINAL-1.2s EXPRESSION CHECK | {line_summary}", fill=(255, 220, 130))

    for i, fi in enumerate(idxs):
        crop = frames[fi][:, x1:x2]
        # Center-square / aspect fit into TW x TH focusing upper-middle face region
        ch, cw, _ = crop.shape
        im = Image.fromarray(crop).resize((TW, int(round(TW * ch / cw))), Image.Resampling.LANCZOS)
        if im.height > TH:
            im = im.crop((0, 0, TW, TH))
        canvas.paste(im, (i * TW, HDR))
        draw.text((i * TW + 8, HDR + TH + 4), f"t={fi/fps:.2f}s (f={fi})", fill=(210, 210, 220))

    os.makedirs(os.path.dirname(out_png) or ".", exist_ok=True)
    canvas.save(out_png, quality=92)


def verify_one(pipeline: SyncNetPipeline, clip_mp4: str, vo_mp3: str, out_tail_png: str, speaker_side: str = "auto", label: str = "", min_conf: float = 4.5, max_offset: int = 2, max_dist: float = 10.2):
    with tempfile.TemporaryDirectory() as td:
        vid_for_sync = crop_speaker_video(clip_mp4, speaker_side, os.path.join(td, "spk.mp4")) if speaker_side in ("left", "right", "far_right", "center") else clip_mp4
        try:
            offsets, confs, dists, max_conf, min_dist, s3fd_json, has_face = pipeline.inference(video_path=vid_for_sync, audio_path=vo_mp3)
        except Exception as e:
            make_tail_strip(clip_mp4, speaker_side, out_tail_png, label, f"SYNCNET_ERR={e}")
            print(f"SYNCNET [{label}] -> FAIL | err={e} | tail={out_tail_png}", flush=True)
            return False, {"passed": False, "reason": str(e)}

    off = int(offsets[0]) if offsets else 999
    passed = bool(has_face) and (max_conf >= min_conf) and (abs(off) <= max_offset) and (min_dist <= max_dist)
    reasons = []
    if not has_face:
        reasons.append("NO_FACE_TRACK")
    if max_conf < min_conf:
        reasons.append(f"LOW_LSE_C({max_conf:.2f}<{min_conf})")
    if abs(off) > max_offset:
        reasons.append(f"BAD_OFFSET({off})")
    if min_dist > max_dist:
        reasons.append(f"HIGH_LSE_D({min_dist:.2f}>{max_dist})")
    status = "PASS" if passed else ";".join(reasons)
    summary = f"{status} | LSE-C={max_conf:.2f} LSE-D={min_dist:.2f} off={off:+d}f"
    make_tail_strip(clip_mp4, speaker_side, out_tail_png, label, summary)
    print(f"SYNCNET [{label}] -> {summary} | tail={out_tail_png}", flush=True)
    return passed, {"passed": passed, "status": status, "lse_c": round(float(max_conf), 3), "lse_d": round(float(min_dist), 3), "offset": off}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("clip_mp4")
    ap.add_argument("vo_mp3")
    ap.add_argument("out_tail_strip")
    ap.add_argument("--speaker-side", default="auto", choices=["auto", "left", "center", "right", "far_right"])
    ap.add_argument("--label", default="")
    ap.add_argument("--min-conf", type=float, default=4.5)
    ap.add_argument("--max-offset", type=int, default=2)
    ap.add_argument("--max-dist", type=float, default=10.2)
    args = ap.parse_args()

    pipe = SyncNetPipeline({
        "s3fd_weights": S3FD_W,
        "syncnet_weights": SYNCNET_W,
        "min_face_size": 55,
        "min_track": 18,
    }, device="cpu")
    ok, _ = verify_one(pipe, args.clip_mp4, args.vo_mp3, args.out_tail_strip, args.speaker_side, args.label or os.path.basename(args.clip_mp4), args.min_conf, args.max_offset, args.max_dist)
    sys.exit(0 if ok else 2)
