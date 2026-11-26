"""
Generate & trim all 42 ElevenLabs audio tracks for Pulp Fiction v2 ("The 7:22 AM Porcelain Reckoning"),
plus Tarantino surf-noir/tension score stems and practical diarrhea & apartment foley SFX.
Uses ONLY verified Nomad cast voices (hooman, damon, deron, zach, ajay, gigi, sheren).
"""
import json
import os
import re
import subprocess
import sys

BASE = "/Users/jack/.gemini/antigravity/scratch/nomad-cinema-parodies"
sys.path.insert(0, BASE)
from studio_audio import CAST, gen_sfx, gen_tts, load_key

SCRIPT_PATH = f"{BASE}/scripts/05_pulp_fiction_v2_script.json"
OUT_DIR = f"{BASE}/audio/05_pulp_fiction_v2"
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
        cut_at = min(total, starts[-1] + 0.14)
        if total - cut_at > 0.25 and cut_at > 1.2:
            tmp = mp3_path + ".trim.mp3"
            subprocess.run(
                ["ffmpeg", "-y", "-i", mp3_path, "-t", f"{cut_at:.3f}", "-c:a", "libmp3lame", "-q:a", "2", tmp],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            os.replace(tmp, mp3_path)
            return cut_at
    return total


def measure_lufs(path: str) -> float:
    p = subprocess.run(
        ["ffmpeg", "-i", path, "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    m = re.search(r"\{[^{}]*input_i[^{}]*\}", p.stderr, re.S)
    if m:
        try:
            return float(json.loads(m.group(0))["input_i"])
        except Exception:
            pass
    return -99.0


def main():
    key = load_key()
    data = json.load(open(SCRIPT_PATH))
    allowed_nomads = {"hooman", "damon", "deron", "zach", "ajay", "gigi", "sheren"}
    summary = []
    tot_dur = 0.0

    for sh in data["shots"]:
        sid = sh["shot_id"]
        spk = sh["speaker"]
        out_mp3 = f"{OUT_DIR}/{sid}.mp3"

        if spk == "sfx":
            if not os.path.exists(out_mp3) or os.path.getsize(out_mp3) < 1000:
                if sid == "PF2_24":
                    gen_sfx(
                        "Violent comedic explosive wet liquid diarrhea eruption inside echoed porcelain toilet bowl, loud pressurized bubbly mud splash splattering ceramic tiles and water gush",
                        4.8, out_mp3, key, influence=0.55,
                    )
                else:
                    gen_sfx(
                        "Loud explosive pressurized wet liquid diarrhea blast bursting open a wooden apartment bathroom door, splattering thick sloppy liquid across linoleum floor and splashing echo",
                        4.8, out_mp3, key, influence=0.55,
                    )
        else:
            if spk not in allowed_nomads:
                raise ValueError(f"{sid}: speaker {spk} is not a Nomad cast member!")
            if not os.path.exists(out_mp3) or os.path.getsize(out_mp3) < 1000:
                gen_tts(spk, sh["tts"], out_mp3, key)
            trim_trailing_silence(out_mp3)

        dur = float(
            subprocess.check_output(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", out_mp3],
                text=True,
            ).strip()
        )
        words = len(sh["dialogue"].split())
        flag = "WARN_OUTLIER" if (spk != "sfx" and dur > max(10.0, words * 0.52 + 2.2)) else "OK"
        lufs = measure_lufs(out_mp3)
        tot_dur += dur + 0.20
        print(f"  {sid} [{spk:6s}] {words:2d}w -> {dur:5.2f}s  ({lufs:+.1f} LUFS)  [{flag}]", flush=True)
        summary.append({"shot_id": sid, "speaker": spk, "words": words, "dur": round(dur, 2), "lufs": round(lufs, 2), "flag": flag})

    # Scores & practical SFX library for Stage 7 assembly
    sfx_defs = [
        ("score_pf2_cool_noir.mp3", 22.0, "1994 LA retro surf noir bassline groove, muted fender twang guitar pulse and crisp snare tension underscore, brooding cinema dialogue score, steady level"),
        ("score_pf2_chaos_tension.mp3", 22.0, "Intense 1994 gritty thriller bass pulse, urgent percussive rimshots and rising suspense strings, high stakes standoff film underscore"),
        ("sfx_sedan_drive.mp3", 6.0, "1994 classic V8 sedan interior steady cruising road rumble with asphalt bump thump"),
        ("sfx_stomach_gurgle_deep.mp3", 4.0, "Loud ominous deep abdominal stomach groan and wet intestinal bubbling gurgle indoors"),
        ("sfx_apartment_door_knock.mp3", 3.0, "Heavy knuckles knocking crisply on solid painted wooden apartment door with hallway echo"),
        ("sfx_door_burst_sheren_gigi.mp3", 3.0, "Sharp wooden apartment door swinging open hurriedly with brass latch click and footsteps"),
        ("sfx_wet_splat_squelch.mp3", 3.5, "Humiliating wet muddy liquid splatter on hardwood floor followed by squelching shoe step"),
        ("sfx_briefcase_open_glow.mp3", 4.0, "Crisp twin brass briefcase latches snapping open followed by mystical warm shimmering golden choir swell"),
        ("sfx_tire_screech_hydrant.mp3", 4.0, "Abrupt sports car tires screeching outside window with distant horn beep"),
    ]
    for fn, dur_s, prompt in sfx_defs:
        p = f"{OUT_DIR}/{fn}"
        if not os.path.exists(p) or os.path.getsize(p) < 1000:
            gen_sfx(prompt, dur_s, p, key, influence=0.45)
        lufs = measure_lufs(p)
        print(f"  STEM {fn:32s} -> {dur_s:4.1f}s ({lufs:+.1f} LUFS)", flush=True)

    json.dump({"estimated_runtime_sec": round(tot_dur, 1), "shots": summary}, open(f"{OUT_DIR}/audio_manifest.json", "w"), indent=2)
    print(f"DONE_PF2_AUDIO: {len(summary)} clips, estimated cut runtime = {tot_dur:.1f}s ({tot_dur/60:.2f} min)")


if __name__ == "__main__":
    main()
