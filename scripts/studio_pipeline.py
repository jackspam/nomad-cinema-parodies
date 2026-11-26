import json
import math
import os
import subprocess
import sys

BASE_DIR = "/Users/jack/.gemini/antigravity/scratch/nomad-cinema-parodies"

LOOK_GRADES = {
    "star_wars": "scale=1920:1080:flags=lanczos,eq=contrast=1.08:brightness=-0.02:saturation=0.95,colorbalance=rs=0.02:gs=0.0:bs=-0.02:rh=0.03:gh=0.01:bh=-0.02,noise=alls=4:allf=t+u,unsharp=5:5:0.45:5:5:0.0",
    "dark_knight": "scale=1920:1080:flags=lanczos,eq=contrast=1.10:brightness=-0.03:saturation=0.82,colorbalance=rs=-0.04:gs=0.01:bs=0.04:rm=-0.02:gm=0.01:bm=0.02,noise=alls=4:allf=t+u,unsharp=5:5:0.5:5:5:0.0",
    "dark_knight_v2": "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,noise=alls=2:allf=t+u",
    "breaking_bad": "scale=1920:1080:flags=lanczos,eq=contrast=1.08:brightness=0.0:saturation=1.06,colorbalance=rs=0.04:gs=0.01:bs=-0.05:rh=0.04:gh=0.02:bh=-0.03,noise=alls=4:allf=t+u,unsharp=5:5:0.5:5:5:0.0",
    "goodfellas": "scale=1920:1080:flags=lanczos,eq=contrast=1.09:brightness=-0.02:saturation=1.04,colorbalance=rs=0.05:gs=-0.01:bs=-0.04:rm=0.03:gm=-0.01:bm=-0.02,noise=alls=5:allf=t+u,unsharp=5:5:0.45:5:5:0.0",
    "pulp_fiction": "scale=1920:1080:flags=lanczos,eq=contrast=1.08:brightness=-0.01:saturation=1.05,colorbalance=rs=0.04:gs=0.01:bs=-0.03,noise=alls=4:allf=t+u,unsharp=5:5:0.45:5:5:0.0",
    "jurassic_park": "scale=1920:1080:flags=lanczos,eq=contrast=1.10:brightness=-0.03:saturation=0.92,colorbalance=rs=-0.03:gs=0.01:bs=0.05,noise=alls=4:allf=t+u,unsharp=5:5:0.5:5:5:0.0",
    "matrix": "scale=1920:1080:flags=lanczos,eq=contrast=1.10:brightness=-0.03:saturation=0.86,colorbalance=rs=-0.05:gs=0.05:bs=-0.03:rm=-0.03:gm=0.04:bm=-0.02,noise=alls=4:allf=t+u,unsharp=5:5:0.5:5:5:0.0",
}


def ffprobe_dur(path: str) -> float:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path],
        text=True,
    ).strip()
    return float(out)


def valid_h3_frames(min_seconds: float) -> int:
    # MiniMax H3 requires 5 + 17*k frames at 24fps
    needed = math.ceil(min_seconds * 24.0)
    k = max(8, math.ceil((needed - 5) / 17.0))
    return 5 + 17 * k


def assemble_film(film_slug: str, look_key: str, shot_specs: list, score_path: str, out_mp4: str, score_vol: float = 0.22, maxrate: str = "4200k"):
    """
    shot_specs: list of dicts:
      {
        "clip": "/abs/path/to/clip.mp4",
        "vo": "/abs/path/to/line.mp3",
        "sfx": "/abs/path/to/sfx.mp3" (optional),
        "sfx_vol": 0.45 (optional),
        "sfx_delay": 0.0 (optional),
        "trim_start": 0.0 (optional),
        "max_tail": 0.65 (optional, seconds after VO ends before cut),
        "v_filter": "" (optional extra audio filter for VO, e.g. CRT/helmet EQ),
      }
    """
    tmp_dir = os.path.join(BASE_DIR, "clips", film_slug, "_assembled_parts")
    os.makedirs(tmp_dir, exist_ok=True)
    os.makedirs(os.path.dirname(out_mp4), exist_ok=True)

    vf_base = LOOK_GRADES.get(look_key, LOOK_GRADES["dark_knight"])
    part_files = []

    for idx, sp in enumerate(shot_specs):
        clip = sp["clip"]
        vo = sp["vo"]
        clip_dur = ffprobe_dur(clip)
        vo_dur = ffprobe_dur(vo)
        t_start = float(sp.get("trim_start", 0.0))
        tail = float(sp.get("max_tail", 0.60))
        # Ensure we never cut off VO, and trim any trailing AI mouth artifact
        seg_dur = min(clip_dur - t_start, max(vo_dur + tail, 3.0))
        if seg_dur < vo_dur + 0.15:
            seg_dur = min(clip_dur - t_start, vo_dur + 0.15)
        if sp.get("max_dur"):
            seg_dur = min(seg_dur, float(sp["max_dur"]))

        part_out = os.path.join(tmp_dir, f"part_{idx:02d}.mp4")
        part_files.append(part_out)

        # Build ffmpeg command: mute raw clip voice, anchor ElevenLabs VO at t=0 (1:1 lip sync)
        inputs = ["-ss", f"{t_start:.3f}", "-t", f"{seg_dur:.3f}", "-i", clip, "-i", vo]
        vo_filt = sp.get("v_filter", "")
        vo_chain = f"[1:a]aresample=48000,apad=whole_dur={seg_dur:.3f}"
        if vo_filt:
            vo_chain += f",{vo_filt}"
        vo_chain += "[voa]"

        if sp.get("sfx") and os.path.exists(sp["sfx"]):
            inputs += ["-i", sp["sfx"]]
            sfx_vol = float(sp.get("sfx_vol", 0.45))
            sfx_delay_ms = int(float(sp.get("sfx_delay", 0.0)) * 1000)
            acomp = (
                f"{vo_chain};"
                f"[2:a]aresample=48000,adelay={sfx_delay_ms}|{sfx_delay_ms},volume={sfx_vol:.2f},apad=whole_dur={seg_dur:.3f}[sfxa];"
                f"[voa][sfxa]amix=inputs=2:duration=first:normalize=0[aout]"
            )
        else:
            acomp = f"{vo_chain};[voa]anull[aout]"

        cmd = [
            "ffmpeg", "-y", *inputs,
            "-filter_complex", f"[0:v]{vf_base},fps=24,format=yuv420p[vout];{acomp}",
            "-map", "[vout]", "-map", "[aout]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "16",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            "-t", f"{seg_dur:.3f}", part_out,
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    concat_txt = os.path.join(tmp_dir, "concat.txt")
    with open(concat_txt, "w") as f:
        for p in part_files:
            f.write(f"file '{p}'\n")

    raw_concat = os.path.join(tmp_dir, "raw_concat.mp4")
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_txt, "-c", "copy", raw_concat],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )

    total_dur = ffprobe_dur(raw_concat)
    fade_out_start = max(0.5, total_dur - 1.2)

    # Mix looping background score underneath + broadcast -14 LUFS loudnorm, capped <90MB for GitHub
    if score_path and os.path.exists(score_path):
        af = (
            f"[1:a]aresample=48000,volume={score_vol:.2f},afade=t=in:st=0:d=1.0,afade=t=out:st={fade_out_start:.2f}:d=1.2[bgm];"
            f"[0:a][bgm]amix=inputs=2:duration=first:normalize=0,"
            f"loudnorm=I=-14:TP=-1.5:LRA=9[aout]"
        )
        score_in = ["-stream_loop", "-1", "-i", score_path]
    else:
        af = "[0:a]loudnorm=I=-14:TP=-1.5:LRA=9[aout]"
        score_in = []

    subprocess.run(
        [
            "ffmpeg", "-y", "-i", raw_concat, *score_in,
            "-filter_complex", f"[0:v]fade=t=in:st=0:d=0.4,fade=t=out:st={fade_out_start:.2f}:d=1.0[vout];{af}",
            "-map", "[vout]", "-map", "[aout]",
            "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-maxrate", maxrate, "-bufsize", "8400k",
            "-movflags", "+faststart",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            "-t", f"{total_dur:.3f}", out_mp4,
        ],
        check=True,
    )
    size_mb = os.path.getsize(out_mp4) / (1024 * 1024)
    print(f"ASSEMBLED {out_mp4} ({total_dur:.2f}s, {size_mb:.1f} MB)")
