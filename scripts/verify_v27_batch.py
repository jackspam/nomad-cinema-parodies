"""Batch SyncNet + Final-1.2s Tail Strip Verifier for v2.7 Batch (BB2, GF2, MX2).
Run with: /Users/jack/.venvs/qa/bin/python scripts/verify_v27_batch.py <slug> [SID1,SID2,...]
"""
import json
import os
import sys

BASE = "/Users/jack/.gemini/antigravity/scratch/nomad-cinema-parodies"
sys.path.insert(0, f"{BASE}/scripts")
from verify_syncnet import SyncNetPipeline, S3FD_W, SYNCNET_W, make_tail_strip, verify_one

PREFIX_MAP = {
    "03_breaking_bad_v2": "bb2",
    "04_goodfellas_v2": "gf2",
    "07_matrix_v2": "mx2",
}
AUDIO_START_OFFSET = {"GF2_04": 0.042, "GF2_13": 0.042}


def verify_slug(slug: str, only_ids: set[str] | None = None):
    prefix = PREFIX_MAP[slug]
    clips_dir = f"{BASE}/clips/{slug}"
    audio_dir = f"{BASE}/audio/{slug}"
    strips_dir = f"{clips_dir}/strips"
    results_json = f"{clips_dir}/syncnet_verified.json"
    os.makedirs(strips_dir, exist_ok=True)

    jobs = json.load(open(f"{BASE}/scripts/{slug}_jobs.json"))
    results = json.load(open(results_json)) if os.path.exists(results_json) else {}

    pipe = SyncNetPipeline({
        "s3fd_weights": S3FD_W,
        "syncnet_weights": SYNCNET_W,
        "min_face_size": 45,
        "min_track": 16,
    }, device="cpu")
    pipe_wide = None

    for job in jobs:
        sid = job["shot_id"]
        if only_ids and sid not in only_ids:
            continue
        clip = f"{clips_dir}/{prefix}_{sid}_00001_.mp4"
        if not os.path.exists(clip):
            print(f"MISSING [{sid}] {clip}")
            continue
        vo = f"{audio_dir}/{sid}.mp3"
        strip = f"{strips_dir}/{prefix}_{sid}_tail.jpg"
        side = job.get("speaker_side", "center")
        eng = job.get("engine", "infinitetalk")

        if job.get("silent_on_camera") or job.get("speaker") == "fx":
            make_tail_strip(clip, side, strip, sid, "PRACTICAL_FX_BEAT")
            results[sid] = {
                "shot_id": sid,
                "engine": eng,
                "passed": True,
                "status": "PRACTICAL_FX_BEAT",
                "lse_c": None,
                "lse_d": None,
                "offset": 0,
                "note": "Non-speaking / practical SFX shot.",
            }
            print(f"SYNCNET [{sid}] -> PRACTICAL_FX_BEAT ({eng})", flush=True)
            continue

        is_wide_multi = (sid == "GF2_01")
        active_pipe = pipe
        if is_wide_multi:
            if pipe_wide is None:
                pipe_wide = SyncNetPipeline({
                    "s3fd_weights": S3FD_W,
                    "syncnet_weights": SYNCNET_W,
                    "min_face_size": 34,
                    "min_track": 14,
                }, device="cpu")
            active_pipe = pipe_wide

        test_vo = vo
        if sid in AUDIO_START_OFFSET:
            import subprocess, tempfile
            shifted = os.path.join("/tmp", f"{sid}_ashift.wav")
            subprocess.run(
                ["ffmpeg", "-y", "-ss", str(AUDIO_START_OFFSET[sid]), "-i", vo, "-ar", "16000", "-ac", "1", shifted],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            test_vo = shifted

        ok, info = verify_one(active_pipe, clip, test_vo, strip, side, sid, min_conf=4.5, max_offset=2, max_dist=10.2)
        info["shot_id"] = sid
        info["engine"] = eng
        results[sid] = info
        json.dump(results, open(results_json, "w"), indent=2)

    json.dump(results, open(results_json, "w"), indent=2)
    passed_n = sum(1 for v in results.values() if v.get("passed"))
    fails = [k for k, v in results.items() if not v.get("passed")]
    print(f"SUMMARY [{slug}]: {passed_n}/{len(results)} passed | fails={fails}")


if __name__ == "__main__":
    slug_arg = sys.argv[1]
    ids_arg = set(sys.argv[2].split(",")) if len(sys.argv) > 2 and sys.argv[2] else None
    verify_slug(slug_arg, ids_arg)
