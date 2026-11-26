"""
Generate & trim all 40 ElevenLabs dialogue tracks for Dark Knight v2.
Only uses genuine Nomad cast voices (hooman, damon, gigi, deron, zach).
"""
import json
import os
import re
import subprocess
import sys

BASE = "/Users/jack/.gemini/antigravity/scratch/nomad-cinema-parodies"
sys.path.insert(0, BASE)
from studio_audio import CAST, gen_tts, load_key

SCRIPT_PATH = f"{BASE}/scripts/02_dark_knight_v2_script.json"
OUT_DIR = f"{BASE}/audio/02_dark_knight_v2"
os.makedirs(OUT_DIR, exist_ok=True)


def trim_trailing_silence(mp3_path: str) -> float:
    p = subprocess.run(
        ["ffmpeg", "-i", mp3_path, "-af", "silencedetect=n=-38dB:d=0.20", "-f", "null", "-"],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    dur_m = re.search(r"Duration:\s+(\d+):(\d+):([\d.]+)", p.stderr)
    total = int(dur_m.group(1)) * 3600 + int(dur_m.group(2)) * 60 + float(dur_m.group(3)) if dur_m else 0.0
    starts = [float(x) for x in re.findall(r"silence_start:\s*([0-9.]+)", p.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end:\s*([0-9.]+)", p.stderr)]
    if starts and len(starts) > len(ends):
        cut_at = min(total, starts[-1] + 0.12)
        if total - cut_at > 0.25 and cut_at > 1.2:
            tmp = mp3_path + ".trim.mp3"
            subprocess.run(
                ["ffmpeg", "-y", "-i", mp3_path, "-t", f"{cut_at:.3f}", "-c:a", "libmp3lame", "-q:a", "2", tmp],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            os.replace(tmp, mp3_path)
            return cut_at
    return total


def main():
    key = load_key()
    data = json.load(open(SCRIPT_PATH))
    allowed = {"hooman", "damon", "gigi", "deron", "zach"}
    summary = []
    for sh in data["shots"]:
        spk = sh["speaker"]
        if spk not in allowed:
            raise ValueError(f"{sh['shot_id']}: non-Nomad speaker {spk} forbidden in v2!")
        sid = sh["shot_id"]
        out_mp3 = f"{OUT_DIR}/{sid}.mp3"
        if not os.path.exists(out_mp3) or os.path.getsize(out_mp3) < 1000:
            gen_tts(spk, sh["tts"], out_mp3, key)
        dur = trim_trailing_silence(out_mp3)
        words = len(sh["dialogue"].split())
        flag = "WARN_OUTLIER" if (dur > max(9.5, words * 0.55 + 2.2)) else "OK"
        print(f"  {sid} [{spk:6s}] {words:2d}w -> {dur:5.2f}s ({flag})")
        summary.append({"shot_id": sid, "speaker": spk, "words": words, "dur": round(dur, 2), "flag": flag})
    json.dump(summary, open(f"{OUT_DIR}/audio_manifest.json", "w"), indent=2)
    print("DONE_ALL_40_AUDIO_TRACKS")


if __name__ == "__main__":
    main()
