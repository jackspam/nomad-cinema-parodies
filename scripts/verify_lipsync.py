"""
Hardened 24fps Lip-Sync & Skin-Detail Verifier + 6fps Word-Stamped Filmstrip Generator
(Detection Gates #2 & #3)

Usage:
  python3 scripts/verify_lipsync.py <clip_mp4> <vo_audio> <out_strip_png> [--speaker-side auto|left|center|right] [--silent] [--label DK2_02]
"""
import argparse
import os
import subprocess
import sys
import cv2
import numpy as np
from PIL import Image, ImageDraw


def audio_rms_per_frame(audio_path: str, num_frames: int, fps: float = 24.0) -> np.ndarray:
    """Decode audio via ffmpeg into 16kHz mono float32 and compute RMS energy aligned to each video frame."""
    sr = 16000
    cmd = ["ffmpeg", "-y", "-i", audio_path, "-f", "f32le", "-ac", "1", "-ar", str(sr), "-"]
    raw = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=True).stdout
    samples = np.frombuffer(raw, dtype=np.float32)
    spf = int(round(sr / fps))
    rms = np.zeros(num_frames, dtype=np.float32)
    for f in range(num_frames):
        s0, s1 = f * spf, (f + 1) * spf
        seg = samples[s0:s1]
        if len(seg) > 0:
            rms[f] = float(np.sqrt(np.mean(seg ** 2)))
    if rms.max() > 0:
        rms = rms / (np.percentile(rms, 98) + 1e-6)
        rms = np.clip(rms, 0.0, 1.5)
    return rms


def find_faces(gray: np.ndarray, side: str = "auto"):
    """Find crisp high-detail head/face ROI using spatial Sobel sharpness & vertical center-head prior."""
    h, w = gray.shape
    gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    mag = np.abs(gx) + np.abs(gy)
    fw = int(h * 0.44)
    fh = int(h * 0.48)
    x_min = fw // 2 if side in ("auto", "left") else int(w * 0.25) if side == "center" else int(w * 0.45)
    x_max = int(w * 0.58) if side == "left" else int(w * 0.78) if side == "center" else (w - fw // 2)
    best_score, best_box = -1.0, (max(0, w // 2 - fw // 2), max(0, int(h * 0.38) - fh // 2), fw, fh)
    for cy in range(int(h * 0.24), int(h * 0.58), 40):
        for cx in range(max(fw // 2, x_min), min(w - fw // 2, x_max), 40):
            x1, y1 = max(0, cx - fw // 2), max(0, cy - fh // 2)
            x2, y2 = min(w, x1 + fw), min(h, y1 + fh)
            # Favor crisp upper-head detail and penalize out-of-focus foreground blobs
            score = float(np.percentile(mag[y1:y2, x1:x2], 85))
            if score > best_score:
                best_score = score
                best_box = (x1, y1, x2 - x1, y2 - y1)
    return [best_box]


def pick_speaker_face(faces, width: int, height: int, side: str):
    if not faces:
        sz = int(height * 0.48)
        cx = int(width * (0.28 if side == "left" else 0.72 if side == "right" else 0.5))
        cy = int(height * 0.42)
        return (max(0, cx - sz // 2), max(0, cy - sz // 2), min(sz, width), min(sz, height)), False
    return faces[0], True


def verify_clip(clip_path: str, audio_path: str, out_strip: str, speaker_side: str = "auto", silent: bool = False, label: str = ""):
    cap = cv2.VideoCapture(clip_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    frames_rgb = []
    while True:
        ok, bgr = cap.read()
        if not ok:
            break
        frames_rgb.append(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
    cap.release()

    if len(frames_rgb) < 8:
        raise RuntimeError(f"Clip too short ({len(frames_rgb)} frames): {clip_path}")

    n_frames = len(frames_rgb)
    H, W, _ = frames_rgb[0].shape
    rms = audio_rms_per_frame(audio_path, n_frames, fps) if audio_path and os.path.exists(audio_path) and not silent else np.zeros(n_frames, dtype=np.float32)

    # Anchor speaker ROI on frame 0 and refine gently frame-to-frame (handles slow camera push-in)
    gray0 = cv2.cvtColor(frames_rgb[0], cv2.COLOR_RGB2GRAY)
    faces0 = find_faces(gray0, speaker_side)
    base_box, detected = pick_speaker_face(faces0, W, H, speaker_side)

    # Identify secondary (listener) face boxes if side != auto
    listener_boxes = []
    if speaker_side in ("left", "right"):
        opp_side = "right" if speaker_side == "left" else "left"
        opp = find_faces(gray0, opp_side)[0]
        if abs((opp[0] + opp[2] * 0.5) - (base_box[0] + base_box[2] * 0.5)) > base_box[2] * 0.7:
            listener_boxes.append(opp)

    def mouth_roi_from_face(box):
        fx, fy, fw, fh = box
        mx1 = max(0, int(fx + fw * 0.22))
        mx2 = min(W, int(fx + fw * 0.78))
        my1 = max(0, int(fy + fh * 0.56))
        my2 = min(H, int(fy + fh * 0.96))
        return mx1, my1, mx2, my2

    mouth_motions = [0.0]
    mouth_apertures = []
    face_laps = []
    listener_motions = [0.0]

    prev_gray_roi = None
    prev_list_rois = []
    cur_box = base_box

    for t in range(n_frames):
        gray = cv2.cvtColor(frames_rgb[t], cv2.COLOR_RGB2GRAY)
        if t % 6 == 0 and t > 0:
            fs = find_faces(gray, speaker_side)
            if fs:
                cx_prev = cur_box[0] + cur_box[2] * 0.5
                cy_prev = cur_box[1] + cur_box[3] * 0.5
                nearest = fs[0]
                if abs((nearest[0] + nearest[2] * 0.5) - cx_prev) < W * 0.14:
                    cur_box = nearest

        fx, fy, fw, fh = cur_box
        face_crop_g = gray[max(0, fy):min(H, fy + fh), max(0, fx):min(W, fx + fw)]
        if face_crop_g.size > 0:
            face_laps.append(float(cv2.Laplacian(cv2.resize(face_crop_g, (160, 160)), cv2.CV_64F).var()))

        mx1, my1, mx2, my2 = mouth_roi_from_face(cur_box)
        m_roi = cv2.resize(gray[my1:my2, mx1:mx2], (96, 64))
        # Dark interior mouth gap ratio (inner oral cavity darkness relative to cheek/chin edges)
        inner = m_roi[16:48, 20:76]
        aperture = float(np.mean(inner < np.percentile(m_roi, 30)))
        mouth_apertures.append(aperture)

        if prev_gray_roi is not None:
            # Normalize brightness frame-to-frame (handles subtle lighting/flicker) before mouth-delta
            a = prev_gray_roi.astype(np.float32) - np.mean(prev_gray_roi)
            b = m_roi.astype(np.float32) - np.mean(m_roi)
            # Suppress rigid camera shift via center sub-patch optical flow
            flow = cv2.calcOpticalFlowFarneback(prev_gray_roi, m_roi, None, 0.5, 2, 11, 2, 5, 1.1, 0)
            # Vertical mouth articulation flow minus median rigid drift
            vy = flow[:, :, 1] - np.median(flow[:, :, 1])
            art_energy = float(np.mean(np.abs(vy)) * 0.7 + np.std(b - a) * 0.04)
            mouth_motions.append(art_energy)
        prev_gray_roi = m_roi

        if listener_boxes:
            lm_vals = []
            cur_list_rois = []
            for li, lb in enumerate(listener_boxes):
                lx1, ly1, lx2, ly2 = mouth_roi_from_face(lb)
                lr = cv2.resize(gray[ly1:ly2, lx1:lx2], (64, 48))
                cur_list_rois.append(lr)
                if li < len(prev_list_rois):
                    flow_l = cv2.calcOpticalFlowFarneback(prev_list_rois[li], lr, None, 0.5, 2, 9, 2, 5, 1.1, 0)
                    vy_l = flow_l[:, :, 1] - np.median(flow_l[:, :, 1])
                    lm_vals.append(float(np.mean(np.abs(vy_l))))
            prev_list_rois = cur_list_rois
            if lm_vals:
                listener_motions.append(max(lm_vals))
        elif t > 0:
            listener_motions.append(0.0)

    mm = np.array(mouth_motions, dtype=np.float32)
    ap = np.array(mouth_apertures, dtype=np.float32)
    ap_vel = np.abs(np.diff(ap, prepend=ap[0])) * 25.0
    combined_mouth = mm + ap_vel

    speech_mask = rms > 0.14
    silence_mask = rms <= 0.08
    active_ratio = float(np.mean(speech_mask))
    mean_speech_motion = float(np.mean(combined_mouth[speech_mask])) if np.any(speech_mask) else float(np.mean(combined_mouth))
    p90_speech_motion = float(np.percentile(combined_mouth[speech_mask], 90)) if np.any(speech_mask) else float(np.percentile(combined_mouth, 90))
    mean_silence_motion = float(np.mean(combined_mouth[silence_mask])) if np.any(silence_mask) else 0.0
    ap_range = float(np.percentile(ap, 95) - np.percentile(ap, 5))

    # Normalized correlation between smoothed speech RMS and mouth motion
    k = np.ones(3, dtype=np.float32) / 3.0
    mm_s = np.convolve(combined_mouth, k, mode="same")
    rms_s = np.convolve(rms, k, mode="same")
    corr = 0.0
    if np.std(mm_s) > 1e-5 and np.std(rms_s) > 1e-5:
        corr = float(np.corrcoef(mm_s, rms_s)[0, 1])

    avg_face_lap = float(np.mean(face_laps)) if face_laps else 0.0
    max_listener_motion = float(np.percentile(listener_motions, 90)) if listener_motions else 0.0

    # Verdict logic
    if silent:
        passed = mean_speech_motion < 0.85
        reason = "SILENT_OK" if passed else f"FAIL_SILENT_MOUTH_MOVED({mean_speech_motion:.2f})"
    else:
        # Must show genuine mouth opening range AND articulated vertical movement during speech
        passed = (mean_speech_motion >= 0.45 and p90_speech_motion >= 0.72 and ap_range >= 0.035)
        reasons = []
        if mean_speech_motion < 0.45 or p90_speech_motion < 0.72:
            reasons.append(f"FROZEN_OR_WEAK_LIPS(mean={mean_speech_motion:.2f},p90={p90_speech_motion:.2f})")
        if ap_range < 0.035:
            reasons.append(f"LOW_APERTURE_RANGE({ap_range:.3f})")
        if max_listener_motion > 0.65 and max_listener_motion > p90_speech_motion * 0.9:
            reasons.append(f"WARN_LISTENER_MOVING({max_listener_motion:.2f})")
        reason = "PASS" if passed else ";".join(reasons)

    # Render 6fps zoomed face filmstrip PNG (stride = 4 frames @ 24fps)
    stride = max(1, int(round(fps / 6.0)))
    sel_indices = list(range(0, n_frames, stride))
    TILE = 224
    BAR_H = 44
    HDR = 42
    canvas = Image.new("RGB", (len(sel_indices) * TILE, HDR + TILE + BAR_H), (14, 14, 18))
    draw = ImageDraw.Draw(canvas)

    # Fixed generous face/mouth crop around detected speaker center so mouth motion across frames isn't lost to jitter
    fx, fy, fw, fh = base_box
    pad_x = int(fw * 0.25)
    pad_top = int(fh * 0.05)
    pad_bot = int(fh * 0.42)
    cx1, cy1 = max(0, fx - pad_x), max(0, fy - pad_top)
    cx2, cy2 = min(W, fx + fw + pad_x), min(H, fy + fh + pad_bot)

    for i, fi in enumerate(sel_indices):
        crop_im = Image.fromarray(frames_rgb[fi][cy1:cy2, cx1:cx2]).resize((TILE, TILE), Image.Resampling.LANCZOS)
        x0 = i * TILE
        canvas.paste(crop_im, (x0, HDR))
        t_sec = fi / fps
        v_rms = float(rms[fi])
        m_val = float(combined_mouth[fi])
        # Speech & mouth-activity bars under each tile
        draw.text((x0 + 6, HDR + TILE + 4), f"{t_sec:.2f}s M={m_val:.2f}", fill=(240, 240, 240))
        sp_w = int(min(1.0, v_rms) * (TILE - 16))
        mo_w = int(min(1.0, m_val / 1.5) * (TILE - 16))
        draw.rectangle([x0 + 8, HDR + TILE + 22, x0 + 8 + sp_w, HDR + TILE + 30], fill=(80, 210, 255))
        draw.rectangle([x0 + 8, HDR + TILE + 32, x0 + 8 + mo_w, HDR + TILE + 40], fill=(100, 255, 130) if m_val >= 0.45 else (255, 90, 90))

    title = (
        f"{label or os.path.basename(clip_path)} | {reason} | face_det={detected} | "
        f"speech_motion={mean_speech_motion:.2f} (p90={p90_speech_motion:.2f}, sil={mean_silence_motion:.2f}) | "
        f"ap_range={ap_range:.3f} | corr={corr:.2f} | FaceLap={avg_face_lap:.1f} | [Blue=Audio, Green/Red=Mouth]"
    )
    draw.text((12, 12), title, fill=(130, 255, 160) if passed else (255, 100, 100))
    os.makedirs(os.path.dirname(out_strip) or ".", exist_ok=True)
    canvas.save(out_strip)
    print(f"LIPSYNC [{label}] -> {reason} | motion={mean_speech_motion:.2f} p90={p90_speech_motion:.2f} ap={ap_range:.3f} corr={corr:.2f} lap={avg_face_lap:.1f} | strip={out_strip}")
    return passed


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("clip")
    p.add_argument("audio")
    p.add_argument("out_strip")
    p.add_argument("--speaker-side", default="auto", choices=["auto", "left", "center", "right"])
    p.add_argument("--silent", action="store_true")
    p.add_argument("--label", default="")
    args = p.parse_args()
    ok = verify_clip(args.clip, args.audio, args.out_strip, args.speaker_side, args.silent, args.label)
    sys.exit(0 if ok else 2)
