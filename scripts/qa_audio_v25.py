"""Automated v2.5 audio spectrum, peak, dynamic-range, and phone-speaker QA gate."""
import argparse
import glob
import json
import os
import re
import subprocess
import sys
import numpy as np


def probe_loudnorm(path: str) -> dict:
    res = subprocess.run(
        ["ffmpeg", "-i", path, "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
        capture_output=True,
        text=True,
        check=True,
    )
    m = re.search(r"\{[^{}]*input_i[^{}]*\}", res.stderr, re.S)
    if not m:
        return {}
    return json.loads(m.group(0))


def decode_mono_48k(path: str, vf_audio: str | None = None) -> np.ndarray:
    cmd = ["ffmpeg", "-v", "error", "-i", path]
    if vf_audio:
        cmd += ["-af", vf_audio]
    cmd += ["-f", "f32le", "-ac", "1", "-ar", "48000", "-"]
    raw = subprocess.check_output(cmd)
    return np.frombuffer(raw, dtype=np.float32)


def spectrum_bands(path: str) -> dict:
    x = decode_mono_48k(path)
    if len(x) == 0:
        return {"sub_pct": 100.0, "mid_pct": 0.0, "high_pct": 0.0}
    spec = np.abs(np.fft.rfft(x))
    freqs = np.fft.rfftfreq(len(x), 1.0 / 48000.0)
    tot = float(np.sum(spec * spec)) + 1e-12
    sub = float(np.sum(spec[freqs < 120.0] ** 2)) / tot * 100.0
    mid = float(np.sum(spec[(freqs >= 250.0) & (freqs <= 4000.0)] ** 2)) / tot * 100.0
    high = float(np.sum(spec[freqs > 2500.0] ** 2)) / tot * 100.0
    return {"sub_pct": sub, "mid_pct": mid, "high_pct": high}


def check_stems(audio_dir: str) -> list[str]:
    failures = []
    if not os.path.isdir(audio_dir):
        return [f"Missing audio directory: {audio_dir}"]

    score_files = sorted(
        glob.glob(f"{audio_dir}/score_*.mp3") + glob.glob(f"{audio_dir}/score_*.wav")
    )
    sfx_files = sorted(
        glob.glob(f"{audio_dir}/sfx_*.mp3") + glob.glob(f"{audio_dir}/sfx_*.wav")
    )

    print(f"=== QA AUDIO v2.5 STEMS: {audio_dir} ===")
    for p in score_files:
        name = os.path.basename(p)
        bands = spectrum_bands(p)
        ln = probe_loudnorm(p)
        tp = float(ln.get("input_tp", -99.0))
        lufs = float(ln.get("input_i", -99.0))
        errs = []
        if bands["mid_pct"] < 35.0:
            errs.append(f"mid(250-4kHz)={bands['mid_pct']:.1f}% < 35.0%")
        if bands["sub_pct"] > 55.0:
            errs.append(f"sub(<120Hz)={bands['sub_pct']:.1f}% > 55.0%")
        if tp > -0.5:
            errs.append(f"TP={tp:.2f} dBTP > -0.5 dBTP")
        status = "FAIL" if errs else "PASS"
        print(
            f"  [SCORE] {name:30s} | I={lufs:6.1f} LUFS | TP={tp:5.2f} dBTP | <120Hz={bands['sub_pct']:5.1f}% | 250-4k={bands['mid_pct']:5.1f}% -> {status}"
            + (f" ({'; '.join(errs)})" if errs else "")
        )
        if errs:
            failures.append(f"{name}: {'; '.join(errs)}")

    for p in sfx_files:
        name = os.path.basename(p)
        ln = probe_loudnorm(p)
        tp = float(ln.get("input_tp", -99.0))
        lufs = float(ln.get("input_i", -99.0))
        bands = spectrum_bands(p)
        errs = []
        if "buzz" in name.lower() or "room" in name.lower():
            if bands["high_pct"] > 5.0:
                errs.append(f">2500Hz={bands['high_pct']:.1f}% > 5.0% (screech)")
        if tp > -0.5:
            errs.append(f"TP={tp:.2f} dBTP > -0.5 dBTP")
        status = "FAIL" if errs else "PASS"
        print(
            f"  [SFX]   {name:30s} | I={lufs:6.1f} LUFS | TP={tp:5.2f} dBTP | >2.5k={bands['high_pct']:5.1f}% -> {status}"
            + (f" ({'; '.join(errs)})" if errs else "")
        )
        if errs:
            failures.append(f"{name}: {'; '.join(errs)}")

    return failures


def check_master(mp4_path: str) -> list[str]:
    failures = []
    if not os.path.exists(mp4_path):
        return [f"Missing master MP4: {mp4_path}"]

    print(f"=== QA AUDIO v2.5 MASTER: {mp4_path} ===")
    ln = probe_loudnorm(mp4_path)
    lufs = float(ln.get("input_i", -99.0))
    tp = float(ln.get("input_tp", 0.0))
    lra = float(ln.get("input_lra", 0.0))

    raw = subprocess.check_output(
        ["ffmpeg", "-v", "error", "-i", mp4_path, "-f", "f32le", "-ac", "2", "-ar", "48000", "-"]
    )
    arr = np.frombuffer(raw, dtype=np.float32)
    clipped = int(np.sum(np.abs(arr) >= 0.99))

    # Phone-speaker simulation: high-pass at 220 Hz, measure 50 ms RMS windows, take 20th percentile floor
    hp = decode_mono_48k(mp4_path, "highpass=f=220")
    win = 2400  # 50ms at 48kHz
    n_win = len(hp) // win
    if n_win > 0:
        w = hp[: n_win * win].reshape(n_win, win)
        rms = np.sqrt(np.mean(w * w, axis=1))
        p20_db = float(20.0 * np.log10(np.percentile(rms, 20) + 1e-9))
    else:
        p20_db = -99.0

    crest_db = tp - lufs

    if not (-16.0 <= lufs <= -13.0):
        failures.append(f"Master I={lufs:.2f} LUFS outside [-16.0, -13.0]")
    if tp > -1.0:
        failures.append(f"Master TP={tp:.2f} dBTP > -1.0 dBTP")
    if lra < 2.5:
        failures.append(f"Master LRA={lra:.2f} LU < 2.5 LU (brickwall crushed dynamics)")
    if crest_db < 8.0:
        failures.append(f"Master Crest(TP-I)={crest_db:.2f} dB < 8.0 dB (squashed transients)")
    if clipped > 0:
        failures.append(f"Master clipped_samples={clipped} (>0)")
    if p20_db < -34.0:
        failures.append(f"Phone-speaker 220Hz p20 floor={p20_db:.1f} dBFS < -34.0 dBFS (music/bed too quiet)")

    print(
        f"  Integrated I   : {lufs:.2f} LUFS (target -16.0..-13.0)\n"
        f"  True Peak      : {tp:.2f} dBTP (limit <= -1.0)\n"
        f"  Loudness Range : {lra:.2f} LU (min >= 2.5)\n"
        f"  Crest Factor   : {crest_db:.2f} dB (min >= 8.0)\n"
        f"  Clipped Samples: {clipped} (must be 0)\n"
        f"  Phone 220Hz p20: {p20_db:.2f} dBFS (min >= -34.0)\n"
        f"  Result         : {'FAIL' if failures else 'PASS'}"
    )
    for f in failures:
        print(f"    -> FAIL: {f}")
    return failures


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stems", help="Audio directory containing score_*.mp3 and sfx_*.mp3")
    ap.add_argument("--master", help="Final assembled MP4 to audit")
    args = ap.parse_args()
    if not args.stems and not args.master:
        ap.error("Provide --stems <dir> and/or --master <mp4>")
    all_fails = []
    if args.stems:
        all_fails.extend(check_stems(args.stems))
    if args.master:
        all_fails.extend(check_master(args.master))
    if all_fails:
        sys.exit(1)
    print("AUDIO_QA_V25_PASSED")


if __name__ == "__main__":
    main()
