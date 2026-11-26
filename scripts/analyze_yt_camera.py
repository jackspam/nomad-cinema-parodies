"""Automated YouTube cinematography, optical-flow camera motion & shot-scale analyzer.

Usage:
  /Users/jack/.venvs/qa/bin/python scripts/analyze_yt_camera.py <video_mp4> --out <camera_spec.json>
"""
import argparse
import json
import math
import os
import sys
import cv2
import numpy as np


def detect_cuts_scenedetect(video_path: str, threshold: float = 24.0, min_scene_len: int = 12) -> list[tuple[float, float]]:
    """Detect shot boundaries using PySceneDetect ContentDetector with histogram fallback."""
    try:
        from scenedetect import open_video, SceneManager
        from scenedetect.detectors import ContentDetector

        video = open_video(video_path)
        fps = float(video.frame_rate or 24.0)
        total_dur = float(video.duration.get_seconds())
        mgr = SceneManager()
        mgr.add_detector(ContentDetector(threshold=threshold, min_scene_len=min_scene_len))
        mgr.detect_scenes(video, show_progress=False)
        scenes = mgr.get_scene_list()
        if scenes:
            return [(round(s[0].get_seconds(), 3), round(s[1].get_seconds(), 3)) for s in scenes if (s[1].get_seconds() - s[0].get_seconds()) >= 0.4]
        if total_dur > 0:
            return [(0.0, round(total_dur, 3))]
    except Exception:
        pass

    # Fallback: OpenCV HSV histogram Bhattacharyya distance
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    prev_hist = None
    cuts = [0.0]
    idx = 0
    while True:
        ok, bgr = cap.read()
        if not ok:
            break
        hsv = cv2.cvtColor(cv2.resize(bgr, (160, 90)), cv2.COLOR_BGR2HSV)
        hist = cv2.calcHist([hsv], [0, 1], None, [16, 16], [0, 180, 0, 256])
        cv2.normalize(hist, hist)
        if prev_hist is not None:
            dist = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_BHATTACHARYYA)
            t = idx / fps
            if dist > 0.42 and (t - cuts[-1]) >= 0.5:
                cuts.append(round(t, 3))
        prev_hist = hist
        idx += 1
    cap.release()
    total_dur = round(n_frames / fps, 3)
    cuts.append(total_dur)
    return [(cuts[i], cuts[i + 1]) for i in range(len(cuts) - 1) if cuts[i + 1] - cuts[i] >= 0.4]


def crop_active_content(bgr: np.ndarray) -> tuple[np.ndarray, tuple[int, int]]:
    """Return active non-letterbox vertical crop bounds (y0, y1) and cropped frame."""
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    row_means = gray.mean(axis=1)
    active = np.where(row_means > 12)[0]
    if len(active) > int(bgr.shape[0] * 0.4):
        y0, y1 = int(active[0]), int(active[-1] + 1)
        return bgr[y0:y1], (y0, y1)
    return bgr, (0, bgr.shape[0])


def estimate_cut_motion(cap: cv2.VideoCapture, fps: float, start_s: float, end_s: float, sample_fps: float = 8.0) -> dict:
    """Measure global 4-DOF camera motion via RANSAC LK optical flow over sampled frames in [start_s, end_s)."""
    dur = max(0.25, end_s - start_s)
    # Trim 2 frames inward from cut edges to avoid transition blur / fade artifacts
    t0 = start_s + min(0.10, dur * 0.1)
    t1 = end_s - min(0.10, dur * 0.1)
    if t1 <= t0:
        t0, t1 = start_s, end_s

    step_s = 1.0 / max(2.0, sample_fps)
    times = np.arange(t0, t1, step_s)
    if len(times) < 2:
        times = np.array([t0, t1])

    raw_frames = []
    for ts in times:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(round(ts * fps)))
        ok, bgr = cap.read()
        if ok:
            raw_frames.append(bgr)

    if len(raw_frames) < 2:
        return {
            "zoom_rate_pct_s": 0.0,
            "pan_pct_s": 0.0,
            "tilt_pct_s": 0.0,
            "handheld_jitter_pct": 0.0,
            "peak_shake_pct": 0.0,
        }

    # Determine single fixed crop band & output size across the whole cut so g0.shape == g1.shape
    mid_bgr = raw_frames[len(raw_frames) // 2]
    _, (y0, y1) = crop_active_content(mid_bgr)
    crop_h = max(64, y1 - y0)
    full_w = mid_bgr.shape[1]
    target_w = 640
    target_h = max(64, int(round(crop_h * (target_w / full_w))))

    frames = []
    for bgr in raw_frames:
        sub = bgr[y0:y1]
        resized = cv2.resize(sub, (target_w, target_h), interpolation=cv2.INTER_AREA)
        frames.append(cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY))

    h, w = frames[0].shape
    dxs, dys, scales, step_mags = [], [], [], []
    eff_dur = max(0.2, float(times[-1] - times[0]))

    for i in range(len(frames) - 1):
        g0, g1 = frames[i], frames[i + 1]
        pts0 = cv2.goodFeaturesToTrack(g0, maxCorners=220, qualityLevel=0.01, minDistance=18, blockSize=7)
        if pts0 is None or len(pts0) < 12:
            continue
        pts1, st, _ = cv2.calcOpticalFlowPyrLK(g0, g1, pts0, None, winSize=(21, 21), maxLevel=3)
        if pts1 is None or st is None:
            continue
        good0 = pts0[st.ravel() == 1]
        good1 = pts1[st.ravel() == 1]
        if len(good0) < 10:
            continue
        mat, _ = cv2.estimateAffinePartial2D(good0, good1, method=cv2.RANSAC, ransacReprojThreshold=2.5)
        if mat is None:
            continue
        a, b, tx = float(mat[0, 0]), float(mat[0, 1]), float(mat[0, 2])
        sc = math.hypot(a, b)
        ty = float(mat[1, 2])
        # Clamp wild RANSAC outliers (>12% jump per step)
        if not (0.90 <= sc <= 1.12) or abs(tx) > w * 0.12 or abs(ty) > h * 0.12:
            continue
        dxs.append(tx / w * 100.0)
        dys.append(ty / h * 100.0)
        scales.append(sc)
        step_mags.append(math.hypot(tx / w * 100.0, ty / h * 100.0))

    if not scales:
        return {
            "zoom_rate_pct_s": 0.0,
            "pan_pct_s": 0.0,
            "tilt_pct_s": 0.0,
            "handheld_jitter_pct": 0.0,
            "peak_shake_pct": 0.0,
        }

    net_scale = float(np.prod(scales))
    zoom_rate_pct_s = (net_scale - 1.0) * 100.0 / eff_dur
    pan_pct_s = float(np.sum(dxs)) / eff_dur
    tilt_pct_s = float(np.sum(dys)) / eff_dur

    # High-frequency jitter: frame-to-frame delta after removing per-step linear drift
    dx_arr = np.array(dxs, dtype=np.float32)
    dy_arr = np.array(dys, dtype=np.float32)
    resid_dx = dx_arr - float(np.mean(dx_arr))
    resid_dy = dy_arr - float(np.mean(dy_arr))
    handheld_jitter_pct = float(np.sqrt(np.mean(resid_dx ** 2 + resid_dy ** 2)))
    peak_shake_pct = float(np.percentile(step_mags, 95))

    return {
        "zoom_rate_pct_s": round(zoom_rate_pct_s, 3),
        "pan_pct_s": round(pan_pct_s, 3),
        "tilt_pct_s": round(tilt_pct_s, 3),
        "handheld_jitter_pct": round(handheld_jitter_pct, 3),
        "peak_shake_pct": round(peak_shake_pct, 3),
    }


def estimate_shot_scale_and_side(cap: cv2.VideoCapture, fps: float, mid_s: float, cascade: cv2.CascadeClassifier) -> dict:
    """Detect primary face size ratio (ECU/CU/MCU/MS/WIDE) and horizontal screen position."""
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(round(mid_s * fps)))
    ok, bgr = cap.read()
    if not ok:
        return {"shot_scale": "MS", "speaker_side": "center", "face_height_ratio": 0.0}

    cropped, _ = crop_active_content(bgr)
    h, w = cropped.shape[:2]
    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
    faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(48, 48))
    if len(faces) == 0:
        return {"shot_scale": "WIDE", "speaker_side": "center", "face_height_ratio": 0.0}

    # Pick dominant face by area
    x, y, fw, fh = max(faces, key=lambda r: r[2] * r[3])
    ratio = float(fh) / max(1, h)
    cx = (float(x) + float(fw) * 0.5) / max(1, w)

    if ratio >= 0.52:
        scale = "ECU"
    elif ratio >= 0.34:
        scale = "CU"
    elif ratio >= 0.22:
        scale = "MCU"
    elif ratio >= 0.13:
        scale = "MS"
    else:
        scale = "WIDE"

    side = "left" if cx < 0.40 else ("right" if cx > 0.60 else "center")
    return {"shot_scale": scale, "speaker_side": side, "face_height_ratio": round(ratio, 3)}


def route_camera_and_model(motion: dict, shot_scale: str) -> dict:
    """Map measured camera motion vectors to canonical tag, LTX LoRA/prompt, and InfiniteTalk route."""
    zr = motion["zoom_rate_pct_s"]
    pan = motion["pan_pct_s"]
    tilt = motion["tilt_pct_s"]
    jitter = motion["handheld_jitter_pct"]
    peak = motion["peak_shake_pct"]

    if peak >= 1.8:
        tag = "IMPACT_SHAKE"
        lora = "IC-LoRA Cameraman (reference trajectory)"
        engine = "LTX-2.5 (+ optional InfiniteTalk V2V if dialogue)"
        prompt = "handheld camera jolting subtly on physical impact, crisp 35mm Panavision lens, stable subject focus"
    elif zr >= 1.2:
        tag = "SLOW_DOLLY_IN"
        lora = "Lightricks/LTX-2-19b-LoRA-Camera-Control-Dolly-In"
        engine = "LTX-2.5 -> InfiniteTalk V2V" if shot_scale in ("ECU", "CU", "MCU") else "LTX-2.5"
        prompt = "measured slow linear dolly push-in along fixed axis on weighted rails"
    elif zr <= -1.2:
        tag = "SLOW_DOLLY_OUT"
        lora = "Lightricks/LTX-2-19b-LoRA-Camera-Control-Dolly-Out"
        engine = "LTX-2.5 -> InfiniteTalk V2V" if shot_scale in ("ECU", "CU") else "LTX-2.5"
        prompt = "measured slow linear dolly pull-out revealing surrounding space"
    elif abs(pan) >= 2.0 or abs(tilt) >= 1.8:
        direction = "Dolly-Right" if pan > 0 else "Dolly-Left"
        tag = "PAN_ORBIT"
        lora = f"Lightricks/LTX-2-19b-LoRA-Camera-Control-{direction} or IC-LoRA Cameraman"
        engine = "LTX-2.5 -> InfiniteTalk V2V"
        prompt = "smooth continuous tracking move matching blocked screen direction"
    elif jitter >= 0.14:
        tag = "HANDHELD_35MM"
        lora = "IC-LoRA Cameraman (or editorial 1.016x 35mm weave)"
        engine = "InfiniteTalk I2V + 35mm weave (or LTX-2.5 -> InfiniteTalk V2V)"
        prompt = "subtle organic 35mm handheld camera breathing with tiny operator micro-movements, maintaining fixed framing distance"
    else:
        tag = "STATIC_LOCKED"
        lora = "Lightricks/LTX-2-19b-LoRA-Camera-Control-Static"
        engine = "InfiniteTalk I2V" if shot_scale in ("ECU", "CU", "MCU") else "LTX-2.5 + Static Camera LoRA"
        prompt = "static lock-off camera mounted on a heavy tripod, completely stationary framing"

    return {
        "camera_motion": tag,
        "recommended_lora": lora,
        "recommended_engine": engine,
        "positive_camera_directive": prompt,
    }


def audit_sequence_grammar(shots: list[dict]) -> list[str]:
    """Flag repetitive unmotivated push-in streaks and incoherent A->B->A coverage changes."""
    warnings = []
    streak = 0
    for i, sh in enumerate(shots):
        if sh["camera_motion"] == "SLOW_DOLLY_IN":
            streak += 1
            if streak >= 2:
                prev_id = shots[i - 1]["cut_id"]
                warnings.append(f"CONSECUTIVE_PUSH_IN: {prev_id} -> {sh['cut_id']} both classify as SLOW_DOLLY_IN (break monotony with STATIC_LOCKED or HANDHELD_35MM).")
        else:
            streak = 0

        if i >= 2:
            a, b, c = shots[i - 2], shots[i - 1], sh
            if a["speaker_side"] == c["speaker_side"] and a["speaker_side"] != b["speaker_side"]:
                if a["camera_motion"] == "SLOW_DOLLY_IN" and c["camera_motion"] == "SLOW_DOLLY_IN":
                    warnings.append(f"REPEAT_RETURN_PUSH_IN: {a['cut_id']} -> {b['cut_id']} -> {c['cut_id']} resets a push-in on returning coverage.")
    return warnings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video_mp4")
    ap.add_argument("--out", required=True)
    ap.add_argument("--threshold", type=float, default=24.0)
    ap.add_argument("--sample-fps", type=float, default=8.0)
    args = ap.parse_args()

    cuts = detect_cuts_scenedetect(args.video_mp4, threshold=args.threshold)
    cap = cv2.VideoCapture(args.video_mp4)
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 24.0)
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    shots = []
    for idx, (s, e) in enumerate(cuts, start=1):
        cid = f"CUT_{idx:02d}"
        motion = estimate_cut_motion(cap, fps, s, e, sample_fps=args.sample_fps)
        framing = estimate_shot_scale_and_side(cap, fps, (s + e) * 0.5, cascade)
        routing = route_camera_and_model(motion, framing["shot_scale"])
        rec = {
            "cut_id": cid,
            "start_s": s,
            "end_s": e,
            "dur_s": round(e - s, 3),
            **framing,
            **motion,
            **routing,
        }
        shots.append(rec)

    cap.release()
    warnings = audit_sequence_grammar(shots)
    counts = {}
    for sh in shots:
        counts[sh["camera_motion"]] = counts.get(sh["camera_motion"], 0) + 1

    out_obj = {
        "source_video": os.path.abspath(args.video_mp4),
        "total_cuts": len(shots),
        "motion_counts": counts,
        "grammar_warnings": warnings,
        "shots": shots,
    }
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    json.dump(out_obj, open(args.out, "w"), indent=2)

    print(f"ANALYZED {len(shots)} cuts -> {counts}")
    if warnings:
        print(f"GRAMMAR_WARNINGS ({len(warnings)}):")
        for w in warnings[:10]:
            print(f"  - {w}")
    for sh in shots[:12]:
        print(f"  {sh['cut_id']} ({sh['start_s']:.1f}-{sh['end_s']:.1f}s) | {sh['shot_scale']:4s} {sh['speaker_side']:6s} | {sh['camera_motion']:14s} zoom={sh['zoom_rate_pct_s']:+.2f}%/s jitt={sh['handheld_jitter_pct']:.2f}% | {sh['recommended_engine']}")


if __name__ == "__main__":
    main()
