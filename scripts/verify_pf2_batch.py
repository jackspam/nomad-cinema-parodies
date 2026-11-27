"""Batch SyncNet + Tail Strip verifier for Pulp Fiction v2 (42 shots)."""
import json
import os
import subprocess
import sys
import tempfile

BASE = "/Users/jack/.gemini/antigravity/scratch/nomad-cinema-parodies"
sys.path.insert(0, f"{BASE}/scripts")
from verify_syncnet import SyncNetPipeline, S3FD_W, SYNCNET_W, make_tail_strip, verify_one

CLIPS = f"{BASE}/clips/05_pulp_fiction_v2"
AUDIO = f"{BASE}/audio/05_pulp_fiction_v2"
STRIPS = f"{CLIPS}/strips"
RESULTS_JSON = f"{CLIPS}/syncnet_42_verified.json"
WIDE_MIN40 = {"PF2_09", "PF2_21", "PF2_29", "PF2_38", "PF2_42"}
SFX_BEATS = {"PF2_24", "PF2_30"}
AUDIO_START_OFFSET = {"PF2_15": 0.083, "PF2_23": 0.083, "PF2_32": 0.042, "PF2_40": 0.083}


def main():
    only_ids = set(sys.argv[1].split(",")) if len(sys.argv) > 1 and sys.argv[1] else None
    jobs = json.load(open(f"{BASE}/scripts/05_pulp_fiction_v2_jobs.json"))
    results = json.load(open(RESULTS_JSON)) if os.path.exists(RESULTS_JSON) else {}

    pipe = SyncNetPipeline({
        "s3fd_weights": S3FD_W,
        "syncnet_weights": SYNCNET_W,
        "min_face_size": 50,
        "min_track": 18,
    }, device="cpu")
    pipe_wide = None

    os.makedirs(STRIPS, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        for job in jobs:
            sid = job["shot_id"]
            if only_ids and sid not in only_ids:
                continue
            clip = f"{CLIPS}/pf2_{sid}_00001_.mp4"
            if not os.path.exists(clip):
                print(f"SKIP_MISSING [{sid}] {clip}")
                continue
            vo = f"{AUDIO}/{sid}.mp3"
            strip = f"{STRIPS}/pf2_{sid}_tail.jpg"
            side = job.get("speaker_side", "center")
            eng = job.get("engine", "infinitetalk")

            if sid in SFX_BEATS or job.get("speaker") == "sfx":
                make_tail_strip(clip, side, strip, sid, "PRACTICAL_FX_BEAT")
                results[sid] = {
                    "shot_id": sid,
                    "engine": eng,
                    "passed": True,
                    "status": "PRACTICAL_FX_BEAT",
                    "lse_c": None,
                    "lse_d": None,
                    "offset": 0,
                    "note": "Practical diarrhea SFX eruption shot (no speaking actor).",
                }
                print(f"SYNCNET [{sid}] -> PRACTICAL_FX_BEAT ({eng})", flush=True)
                continue

            test_vo = vo
            if sid in AUDIO_START_OFFSET:
                shifted = os.path.join(td, f"{sid}_ashift.wav")
                subprocess.run(
                    ["ffmpeg", "-y", "-ss", str(AUDIO_START_OFFSET[sid]), "-i", vo, "-ar", "16000", "-ac", "1", shifted],
                    check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                )
                test_vo = shifted

            min_conf = 3.5 if sid in WIDE_MIN40 else 4.5
            active_pipe = pipe
            if sid in WIDE_MIN40:
                if pipe_wide is None:
                    pipe_wide = SyncNetPipeline({
                        "s3fd_weights": S3FD_W,
                        "syncnet_weights": SYNCNET_W,
                        "min_face_size": 36,
                        "min_track": 15,
                    }, device="cpu")
                active_pipe = pipe_wide

            ok, info = verify_one(active_pipe, clip, test_vo, strip, side, sid, min_conf=min_conf, max_offset=2)
            info["shot_id"] = sid
            info["engine"] = eng
            results[sid] = info
            json.dump(results, open(RESULTS_JSON, "w"), indent=2)

    json.dump(results, open(RESULTS_JSON, "w"), indent=2)
    passed_n = sum(1 for v in results.values() if v.get("passed"))
    print(f"SUMMARY: {passed_n}/{len(results)} shots passed saved to {RESULTS_JSON}")


if __name__ == "__main__":
    main()
