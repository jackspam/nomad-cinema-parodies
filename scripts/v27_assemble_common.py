"""Shared assembly utilities for v2.7 3-Film Batch (BB2, GF2, MX2).
Implements hardened v2.6/v2.7 specs:
  - Pre-measured linear -16 LUFS dialogue normalization (zero loudnorm lag)
  - 15ms shot-boundary audio micro-fades
  - Calibrated camera motion (STATIC_LOCKED, HANDHELD_35MM weave, IMPACT_SHAKE burst, SLOW_DOLLY_IN)
  - Continuous zero-reset ambience bed + sample-accurate peak-safe foley & score spotting
  - Pure linear master gain (-15.0 LUFS) + -2.0 dBFS safety limiter
  - Isolated QA bus export (/tmp/qa_buses_<tag>/) + 45s screening chunks (/tmp/v27_screen/<tag>/)
"""
import glob
import json
import math
import os
import re
import subprocess
import numpy as np
from PIL import Image, ImageDraw

BASE = "/Users/jack/.gemini/antigravity/scratch/nomad-cinema-parodies"


def ffprobe_dur(path: str) -> float:
    return float(
        subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path],
            text=True,
        ).strip()
    )


def detect_speech_end(mp3_path: str, audio_offset: float = 0.0) -> tuple[float, float]:
    cmd = ["ffmpeg", "-v", "error"]
    if audio_offset > 0:
        cmd += ["-ss", f"{audio_offset:.4f}"]
    cmd += ["-i", mp3_path, "-f", "s16le", "-ac", "1", "-ar", "16000", "-"]
    raw = subprocess.check_output(cmd)
    arr = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    dur = len(arr) / 16000.0
    win = 320
    n_win = len(arr) // win
    if n_win == 0:
        return dur, dur
    rms = np.sqrt(np.mean(arr[: n_win * win].reshape(n_win, win) ** 2, axis=1))
    active = np.where(rms > 0.012)[0]
    if len(active) == 0:
        return dur, dur
    return dur, min(dur, (active[-1] + 1) * (win / 16000.0))


def measure_lufs(audio_path: str, audio_offset: float = 0.0) -> float:
    cmd = ["ffmpeg"]
    if audio_offset > 0:
        cmd += ["-ss", f"{audio_offset:.4f}"]
    cmd += ["-i", audio_path, "-af", "loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json", "-f", "null", "-"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    m = re.search(r"\{[\s\S]*?\}", res.stderr)
    return float(json.loads(m.group(0))["input_i"]) if m else -20.0


def measure_peak_db(audio_path: str) -> float:
    res = subprocess.run(["ffmpeg", "-i", audio_path, "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True, check=True)
    m = re.search(r"max_volume:\s*([-\d.]+)\s*dB", res.stderr)
    return float(m.group(1)) if m else 0.0


def concat_list(paths: list[str], txt_p: str, out_p: str):
    with open(txt_p, "w") as f:
        for p in paths:
            f.write(f"file '{p}'\n")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", txt_p, "-c", "copy", out_p],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def place_sfx_cues(cues: list[tuple], shot_timing: dict, total_dur: float, out_wav: str, tag: str):
    """Place [(shot_num, offset_fn(st, sd), path, target_peak_dbfs, trim_dur_or_none), ...] on timeline."""
    inputs = ["-f", "lavfi", "-t", f"{total_dur:.6f}", "-i", "anullsrc=r=48000:cl=stereo"]
    filter_parts = ["[0:a]aresample=48000[base]"]
    mix_labels = ["[base]"]
    cue_times = []

    for idx, (snum, off_fn, spath, target_pk, trim_d) in enumerate(cues, start=1):
        st, sd = shot_timing[snum]
        at_sec = max(0.0, off_fn(st, sd))
        cue_times.append((snum, at_sec))
        delay_ms = int(round(at_sec * 1000.0))
        pk = measure_peak_db(spath)
        gain_db = max(-26.0, min(14.0, target_pk - pk))
        inputs += ["-i", spath]
        chain = f"[{idx}:a]aresample=48000"
        if trim_d is not None:
            fade_t = max(0.08, trim_d - 0.25)
            chain += f",atrim=0:{trim_d:.3f},asetpts=PTS-STARTPTS,afade=t=out:st={fade_t:.3f}:d=0.25"
        chain += f",volume={gain_db:.2f}dB,adelay={delay_ms}|{delay_ms},apad=whole_dur={total_dur:.6f},atrim=0:{total_dur:.6f}[c{idx}]"
        filter_parts.append(chain)
        mix_labels.append(f"[c{idx}]")
        print(f"  FOLEY [{tag}_{snum:02d}] @{at_sec:6.2f}s {os.path.basename(spath)} (pk={pk:+.1f}->{target_pk:+.1f}dBFS)")

    filter_parts.append(f"{''.join(mix_labels)}amix=inputs={len(mix_labels)}:normalize=0:duration=first,atrim=0:{total_dur:.6f}[sout]")
    subprocess.run([
        "ffmpeg", "-y", *inputs, "-filter_complex", ";".join(filter_parts), "-map", "[sout]",
        "-t", f"{total_dur:.6f}", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", out_wav,
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return cue_times


def export_qa_artifacts(out_mp4: str, score_bed: str, foley_bed: str, amb_bed: str, scored_window: tuple[float, float], total_dur: float, tmp_dir: str, qa_bus_dir: str, screen_dir: str, shots: list[dict], shot_timing: dict, tag: str):
    os.makedirs(qa_bus_dir, exist_ok=True)
    os.makedirs(screen_dir, exist_ok=True)
    for p in glob.glob(f"{screen_dir}/part_*.mp4"):
        os.remove(p)

    # 1) Isolated Audio Buses
    w_s, w_e = scored_window
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-ss", f"{w_s:.2f}", "-t", f"{max(4.0, w_e - w_s):.2f}",
        "-i", score_bed, "-c:a", "libmp3lame", "-b:a", "192k", f"{qa_bus_dir}/score_only.mp3",
    ], check=True)
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", foley_bed, "-i", amb_bed,
        "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=first:normalize=0[s]",
        "-map", "[s]", "-c:a", "libmp3lame", "-b:a", "192k", f"{qa_bus_dir}/sfx_only.mp3",
    ], check=True)
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-ss", f"{w_s:.2f}", "-t", f"{max(5.0, w_e - w_s):.2f}",
        "-i", out_mp4, "-vn", "-af", "highpass=f=220,lowpass=f=7000",
        "-c:a", "libmp3lame", "-b:a", "192k", f"{qa_bus_dir}/final_phone_220hz.mp3",
    ], check=True)

    # 2) 45s Screening Chunks
    idx = 1
    t = 0.0
    while t < total_dur - 0.5:
        d = min(45.0, total_dur - t)
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-ss", f"{t:.3f}", "-t", f"{d:.3f}", "-i", out_mp4,
            "-c:v", "libx264", "-crf", "20", "-preset", "fast", "-c:a", "aac", "-b:a", "160k",
            f"{screen_dir}/part_{idx:02d}.mp4",
        ], check=True)
        t += d
        idx += 1

    # 3) Rendered Cast Continuity Grid (mid-frame of every assembled shot directly from OUT_MP4)
    tile_w, tile_h, cols = 480, 270, 5
    rows = (len(shots) + cols - 1) // cols
    grid = Image.new("RGB", (cols * tile_w, rows * tile_h), (12, 14, 18))
    draw = ImageDraw.Draw(grid)
    tail_rows = []
    for i, sh in enumerate(shots):
        n = int(sh["shot_id"].split("_")[1])
        st, sd = shot_timing[n]
        mid_t = st + sd * 0.45
        jpg = f"{tmp_dir}/rend_mid_{n:02d}.jpg"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{mid_t:.3f}", "-i", out_mp4, "-vframes", "1", "-q:v", "3", jpg], check=True)
        im = Image.open(jpg).resize((tile_w, tile_h), Image.Resampling.LANCZOS)
        x, y = (i % cols) * tile_w, (i // cols) * tile_h
        grid.paste(im, (x, y))
        draw.rectangle([x + 4, y + 4, x + 150, y + 26], fill=(0, 0, 0))
        draw.text((x + 8, y + 8), f"{sh['shot_id']} ({sh['speaker']})", fill=(130, 240, 195))

        # 3-frame tail strip per shot (-0.70s, -0.35s, -0.08s from shot end)
        strip = Image.new("RGB", (3 * 320, 180 + 22), (16, 18, 24))
        sdraw = ImageDraw.Draw(strip)
        for ti, off in enumerate((0.70, 0.35, 0.08)):
            ft = min(st + sd - 0.04, max(st + 0.04, st + sd - off))
            tjpg = f"{tmp_dir}/rend_tail_{n:02d}_{ti}.jpg"
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ft:.3f}", "-i", out_mp4, "-vframes", "1", "-q:v", "3", tjpg], check=True)
            tim = Image.open(tjpg).resize((320, 180), Image.Resampling.LANCZOS)
            strip.paste(tim, (ti * 320, 0))
        sdraw.text((6, 184), f"{sh['shot_id']} ({sh['speaker']}) end={st+sd:.2f}s", fill=(255, 220, 130))
        tail_rows.append(strip)

    grid.save(f"{screen_dir}/{tag}_continuity_grid.jpg", quality=90)
    if tail_rows:
        tw, th = tail_rows[0].size
        full_tail = Image.new("RGB", (tw, th * len(tail_rows)), (12, 14, 18))
        for ri, row_im in enumerate(tail_rows):
            full_tail.paste(row_im, (0, ri * th))
        full_tail.save(f"{screen_dir}/{tag}_tail_strip.jpg", quality=88)
    print(f"  EXPORTED QA SCREENING & GRIDS -> {screen_dir}/ & {qa_bus_dir}/")


def run_standard_assembly(cfg: dict):
    slug = cfg["slug"]
    tag = cfg["tag"]
    prefix = cfg["clip_prefix"]
    clips_dir = f"{BASE}/clips/{slug}"
    audio_dir = f"{BASE}/audio/{slug}"
    tmp_dir = f"{clips_dir}/_assembled_parts"
    qa_bus_dir = f"/tmp/qa_buses_{tag}"
    screen_dir = f"/tmp/v27_screen/{tag}"
    out_mp4 = f"{BASE}/films/{cfg['out_name']}"

    os.makedirs(tmp_dir, exist_ok=True)
    os.makedirs(os.path.dirname(out_mp4), exist_ok=True)

    shots = json.load(open(f"{BASE}/scripts/{slug}_script.json"))["shots"]
    jobs = {j["shot_id"]: j for j in json.load(open(f"{BASE}/scripts/{slug}_jobs.json"))}
    sfx_shots = set(cfg["sfx_shots"])
    beat_holds = set(cfg.get("beat_holds", ()))
    impact_shots = set(cfg.get("impact_shots", ()))
    au_offsets = cfg.get("audio_offsets", {})
    start_trims = cfg.get("start_trims", {})
    grade_filter = cfg.get("grade_filter", "")

    v_parts, d_parts = [], []
    total_frames = 0
    shot_timing = {}

    for idx, sh in enumerate(shots):
        sid = sh["shot_id"]
        n = int(sid.split("_")[1])
        job = jobs[sid]
        clip_p = f"{clips_dir}/{prefix}_{sid}_00001_.mp4"
        vo_p = f"{audio_dir}/{sid}.mp3"

        st_trim = float(start_trims.get(sid, 0.0))
        clip_dur = max(0.5, ffprobe_dur(clip_p) - st_trim)
        au_off = float(au_offsets.get(sid, 0.0)) + st_trim
        if n in sfx_shots:
            target_dur = min(clip_dur, cfg.get("fx_durations", {}).get(n, 3.60))
            lufs, gain_db = -99.0, 0.0
        else:
            vo_dur, speech_end = detect_speech_end(vo_p, au_off)
            lufs = measure_lufs(vo_p, au_off)
            gain_db = max(-10.0, min(14.0, -16.0 - lufs))
            tail = 0.38 if n in beat_holds else 0.22
            target_dur = min(clip_dur, max(max(vo_dur, speech_end) + tail, 1.5))

        n_frames = max(24, int(round(target_dur * 24.0)))
        if n_frames / 24.0 > clip_dur:
            n_frames = max(24, int(math.floor(clip_dur * 24.0)))
        exact_dur = n_frames / 24.0
        shot_timing[n] = (total_frames / 24.0, exact_dur)
        total_frames += n_frames

        vf_steps = ["fps=24"]
        if n in impact_shots:
            vf_steps.append(
                "scale=3960:1716:flags=lanczos,"
                "crop=3840:1664:"
                "x='60+28*sin(42*t)*between(t,0.25,2.10)':"
                "y='26+20*cos(51*t)*between(t,0.25,2.10)':exact=1,"
                "scale=1920:832:flags=lanczos"
            )
        elif job.get("camera_motion") == "HANDHELD_35MM" and job.get("engine") == "infinitetalk":
            p1 = (n * 1.41) % (2 * math.pi)
            p2 = (n * 2.63 + 0.7) % (2 * math.pi)
            vf_steps.append(
                "scale=3904:1692:flags=lanczos,"
                f"crop=3840:1664:x='32+10*sin(0.85*t+{p1:.3f})+5*sin(1.9*t+{p2:.3f})':"
                f"y='14+5*cos(0.70*t+{p1:.3f})+3*sin(1.6*t+{p2:.3f})':exact=1,"
                "scale=1920:832:flags=lanczos"
            )
        elif job.get("camera_motion") == "SLOW_DOLLY_IN":
            vf_steps.append(
                f"scale=3840:1664:flags=lanczos,"
                f"zoompan=z='1+0.07*min(1,on/{max(1, n_frames - 1)})':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x832:fps=24"
            )
        else:
            vf_steps.append("scale=1920:832:flags=lanczos")

        if grade_filter:
            vf_steps.append(grade_filter)
        vf_steps += ["vignette=PI/7", "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black", "noise=alls=2:allf=t+u", "format=yuv420p"]

        v_part = f"{tmp_dir}/v_{idx:02d}.mp4"
        d_part = f"{tmp_dir}/d_{idx:02d}.wav"
        v_parts.append(v_part)
        d_parts.append(d_part)

        v_cmd = ["ffmpeg", "-y"]
        if st_trim > 0:
            v_cmd += ["-ss", f"{st_trim:.4f}"]
        v_cmd += [
            "-i", clip_p, "-vf", ",".join(vf_steps), "-an",
            "-frames:v", str(n_frames), "-c:v", "libx264", "-preset", "fast", "-crf", "14", "-pix_fmt", "yuv420p", v_part,
        ]
        subprocess.run(v_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        fade_out_st = max(0.02, exact_dur - 0.015)
        if n in sfx_shots:
            subprocess.run([
                "ffmpeg", "-y", "-f", "lavfi", "-t", f"{exact_dur:.6f}", "-i", "anullsrc=r=48000:cl=stereo",
                "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", d_part,
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            d_cmd = ["ffmpeg", "-y"]
            if au_off > 0:
                d_cmd += ["-ss", f"{au_off:.4f}"]
            d_cmd += [
                "-i", vo_p,
                "-af", f"highpass=f=75,volume={gain_db:.2f}dB,aresample=48000,apad=whole_dur={exact_dur:.6f},atrim=0:{exact_dur:.6f},afade=t=in:st=0:d=0.015,afade=t=out:st={fade_out_st:.6f}:d=0.015",
                "-t", f"{exact_dur:.6f}", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", d_part,
            ]
            subprocess.run(d_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"  [{sid}] @{shot_timing[n][0]:6.2f}s cut={exact_dur:.2f}s ({n_frames}f) cam={job.get('camera_motion'):13s} dlg={lufs:.1f}->{gain_db:+.1f}dB", flush=True)

    v_cat, d_cat = f"{tmp_dir}/v_cat.mp4", f"{tmp_dir}/d_cat.wav"
    concat_list(v_parts, f"{tmp_dir}/v_list.txt", v_cat)
    concat_list(d_parts, f"{tmp_dir}/d_list.txt", d_cat)

    total_dur = total_frames / 24.0
    score_bed = f"{tmp_dir}/score_bed.wav"
    amb_bed = f"{tmp_dir}/amb_bed.wav"
    foley_bed = f"{tmp_dir}/foley_bed.wav"

    scored_window = cfg["build_score"](shot_timing, total_dur, score_bed, tmp_dir, audio_dir)
    cfg["build_ambience"](shot_timing, total_dur, amb_bed, tmp_dir, audio_dir)
    cfg["build_foley"](shot_timing, total_dur, foley_bed, audio_dir)

    pre_mix = f"{tmp_dir}/pre_mix.wav"
    ratio = cfg.get("sidechain_ratio", 2.0)
    mix_filter = (
        "[0:a]asplit=2[dlg_main][dlg_sc];"
        f"[3:a][dlg_sc]sidechaincompress=threshold=0.05:ratio={ratio}:attack=30:release=400[bgm_ducked];"
        "[dlg_main][1:a][2:a][bgm_ducked]amix=inputs=4:duration=first:normalize=0[aout]"
    )
    subprocess.run([
        "ffmpeg", "-y", "-i", d_cat, "-i", amb_bed, "-i", foley_bed, "-i", score_bed,
        "-filter_complex", mix_filter, "-map", "[aout]",
        "-t", f"{total_dur:.6f}", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", pre_mix,
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    raw_i = measure_lufs(pre_mix)
    master_gain = max(-8.0, min(8.0, -15.0 - raw_i))
    print(f"  MASTER LINEAR GAIN [{tag.upper()}]: pre_mix={raw_i:.2f} LUFS -> -15.0 LUFS (gain={master_gain:+.2f} dB)")

    fade_out_vid = max(0.5, total_dur - 1.0)
    subprocess.run([
        "ffmpeg", "-y", "-i", v_cat, "-i", pre_mix,
        "-filter_complex", f"[0:v]fade=t=in:st=0:d=0.4,fade=t=out:st={fade_out_vid:.3f}:d=1.0[vout];[1:a]volume={master_gain:.2f}dB,alimiter=limit=-2.0dB:attack=5:release=50:level=disabled[aout]",
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-maxrate", "2800k", "-bufsize", "8000k",
        "-movflags", "+faststart", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        "-t", f"{total_dur:.6f}", out_mp4,
    ], check=True)

    size_mb = os.path.getsize(out_mp4) / (1024 * 1024)
    if size_mb > 88.0:
        print(f"  RE-ENCODING at CRF 20 ({size_mb:.1f} MB > 88 MB limit)...")
        subprocess.run([
            "ffmpeg", "-y", "-i", v_cat, "-i", pre_mix,
            "-filter_complex", f"[0:v]fade=t=in:st=0:d=0.4,fade=t=out:st={fade_out_vid:.3f}:d=1.0[vout];[1:a]volume={master_gain:.2f}dB,alimiter=limit=-2.0dB:attack=5:release=50:level=disabled[aout]",
            "-map", "[vout]", "-map", "[aout]",
            "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-maxrate", "2200k", "-bufsize", "7000k",
            "-movflags", "+faststart", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            "-t", f"{total_dur:.6f}", out_mp4,
        ], check=True)
        size_mb = os.path.getsize(out_mp4) / (1024 * 1024)

    export_qa_artifacts(out_mp4, score_bed, foley_bed, amb_bed, scored_window, total_dur, tmp_dir, qa_bus_dir, screen_dir, shots, shot_timing, tag)
    print(f"MASTER_READY {out_mp4} -> {total_dur:.2f}s ({total_frames}f), {size_mb:.2f} MB | scored_window={scored_window[0]:.2f}:{scored_window[1]:.2f}")
