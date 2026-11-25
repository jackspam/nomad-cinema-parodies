import glob
import json
import math
import os
import re
import shutil
import subprocess
import sys

BASE = "/Users/jack/.gemini/antigravity/scratch/nomad-cinema-parodies"

BANNED_PROMPT_PATTERNS = [
    r"\bwhip[- ]?pan\b",
    r"\borbit behind\b",
    r"\bwalk past camera\b",
    r"\bcross in front of\b",
    r"\bmarch(?:ing)? past\b",
]


def ffprobe_dur(path: str) -> float:
    return float(
        subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path],
            text=True,
        ).strip()
    )


def valid_h3_frames(min_seconds: float) -> int:
    needed = math.ceil(min_seconds * 24.0)
    k = max(8, math.ceil((needed - 5) / 17.0))
    return 5 + 17 * k


def valid_ltx_frames(min_seconds: float) -> int:
    # LTX-2.5 requires 1 + 8*k frames at 24fps
    needed = math.ceil(min_seconds * 24.0)
    k = max(5, math.ceil((needed - 1) / 8.0))
    return 1 + 8 * k


def trim_trailing_silence(mp3_path: str) -> tuple[float, float]:
    """Strip trailing digital silence (>0.25s below -38dB) while keeping a 0.15s natural breath tail."""
    before = ffprobe_dur(mp3_path)
    out = subprocess.check_output(
        ["ffmpeg", "-i", mp3_path, "-af", "silencedetect=n=-38dB:d=0.25", "-f", "null", "-"],
        stderr=subprocess.STDOUT,
        text=True,
    )
    starts = [float(m.group(1)) for m in re.finditer(r"silence_start:\s*([0-9.]+)", out)]
    # Only trim a trailing silence that starts past the first 1.2s and extends near the end
    target_end = before
    for s in starts:
        if s >= 1.2 and (before - s) >= 0.40:
            # Verify there is no later speech after this silence_start
            ends = [float(m.group(1)) for m in re.finditer(r"silence_end:\s*([0-9.]+)", out)]
            if not any(e > s for e in ends):
                target_end = min(before, s + 0.18)
                break
    if target_end < before - 0.15 and target_end >= 1.5:
        tmp = mp3_path + ".trim.mp3"
        subprocess.run(
            ["ffmpeg", "-y", "-i", mp3_path, "-t", f"{target_end:.3f}", "-af", "afade=t=out:st={:.3f}:d=0.08".format(max(0.1, target_end - 0.08)), "-c:a", "libmp3lame", "-b:a", "192k", tmp],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        shutil.move(tmp, mp3_path)
        return before, ffprobe_dur(mp3_path)
    return before, before


def validate_and_prepare(slug: str) -> list[str]:
    issues = []
    yt_frames = glob.glob(f"{BASE}/refs/yt/{slug}/*.jpg")
    if len(yt_frames) < 40:
        issues.append(f"{slug}: only {len(yt_frames)} YT frames (need >= 40)")

    jobs_path = f"{BASE}/scripts/{slug}_jobs.json"
    script_path = f"{BASE}/scripts/{slug}_script.json"
    jobs = json.load(open(jobs_path))
    script_shots = {}
    if os.path.exists(script_path):
        script_shots = {s["shot_id"].lower(): s for s in json.load(open(script_path)).get("shots", [])}
    trimmed_count = 0

    for j in jobs:
        prefix = j["prefix"]
        imgs = j.get("images", [])
        if len(imgs) != 1:
            issues.append(f"{prefix}: expected 1 bespoke keyframe, found {len(imgs)}")
        for im in imgs:
            im_path = f"{BASE}/refs/{slug}/{im}"
            if not os.path.exists(im_path) or os.path.getsize(im_path) < 1000:
                issues.append(f"{prefix}: missing or empty keyframe refs/{slug}/{im}")

        prompt = j.get("prompt", "")
        if "<Picture 1>" not in prompt:
            issues.append(f"{prefix}: missing <Picture 1> tag")
        if not j.get("silent_on_camera") and "<Audio 1>" not in prompt:
            issues.append(f"{prefix}: missing <Audio 1> tag")
        for pat in BANNED_PROMPT_PATTERNS:
            if re.search(pat, prompt, re.I):
                issues.append(f"{prefix}: risky motion/physics phrase matched '{pat}'")

        au = f"{BASE}/audio/{slug}/{j['audio']}"
        if not os.path.exists(au) or os.path.getsize(au) < 1000:
            issues.append(f"{prefix}: missing audio {au}")
        else:
            b, a = trim_trailing_silence(au)
            if a < b:
                trimmed_count += 1
            shot_id = prefix.split("_", 1)[1].lower() if "_" in prefix else prefix.lower()
            words = len(script_shots.get(shot_id, {}).get("exact_dialogue", "").split())
            if words > 0 and a > max(10.0, words * 0.55 + 2.5):
                print(f"  WARN (long audio check): {prefix} audio {a:.2f}s looks unusually long for {words} words (inspect for ElevenLabs repeat or gibberish tail)")
            nf = valid_h3_frames(a + 0.45)
            j["length"] = nf

    json.dump(jobs, open(jobs_path, "w"), indent=2)
    print(f"[PREFLIGHT] {slug}: {len(jobs)} jobs, {len(yt_frames)} YT frames, {trimmed_count} MP3s silence-trimmed, total video {sum(x['length'] for x in jobs)/24:.1f}s")
    if issues:
        for iss in issues:
            print("  WARN/FAIL:", iss)
    return issues


if __name__ == "__main__":
    targets = sys.argv[1:] or ["03_breaking_bad", "04_goodfellas"]
    all_issues = []
    for t in targets:
        all_issues.extend(validate_and_prepare(t))
    if all_issues:
        sys.exit(1)
    print("ALL_PREFLIGHT_CHECKS_PASSED")
