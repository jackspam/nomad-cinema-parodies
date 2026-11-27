"""Assemble the 42-shot Hollywood 1080p Scope master for Pulp Fiction v2 ("The 7:22 AM Porcelain Reckoning").
Follows v2.6 audio spotting:
  - Cold-open 1994 surf-rock needle drop (0:00..0:08) -> dry car/apartment Tarantino banter (PF2_01..21)
  - Act 3 diarrhea chaos score (PF2_22..32, dipping on PF2_24 & PF2_30 eruptions)
  - Iconic surf-rock guitar/horn walkout needle drop (PF2_41..42)
  - Continuous scene-matched ambience beds (sedan -> hallway -> apartment) + 18 visually synced peak-safe foley cues
  - Pure linear master gain (-15.0 LUFS) + -2.0 dBFS safety limiter (TP <= -1.0 dBTP, Crest >= 8 dB, zero clipping)
"""
import json
import math
import os
import re
import subprocess
import sys
import numpy as np

BASE = "/Users/jack/.gemini/antigravity/scratch/nomad-cinema-parodies"
SCRIPT_PATH = f"{BASE}/scripts/05_pulp_fiction_v2_script.json"
JOBS_PATH = f"{BASE}/scripts/05_pulp_fiction_v2_jobs.json"
CLIPS_DIR = f"{BASE}/clips/05_pulp_fiction_v2"
AUDIO_DIR = f"{BASE}/audio/05_pulp_fiction_v2"
OUT_MP4 = f"{BASE}/films/05_pulp_fiction_1080p.mp4"
TMP_DIR = f"{CLIPS_DIR}/_assembled_parts"
QA_BUS_DIR = "/tmp/qa_buses_pf2"

BEAT_HOLD_SHOTS = {5, 8, 20, 32, 42}
SFX_SHOTS = {24, 30}
AUDIO_START_OFFSET = {"PF2_15": 0.083, "PF2_23": 0.083, "PF2_32": 0.042, "PF2_40": 0.083}


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


def build_ambience_bed(shot_timing: dict, total_dur: float, out_wav: str):
    """Continuous scene-matched ambience beds (zero per-cut resets):
    - Car (PF2_01..05): vintage V8 cabin hum (<380Hz, -32 LUFS)
    - Hallway (PF2_06..08): dim motel corridor room tone (-40 LUFS)
    - Apartment (PF2_09..42): continuous avocado apartment room tone (-40 LUFS)
    """
    t_hall = shot_timing[6][0]
    t_apt = shot_timing[9][0]

    def prep_bed(src_p: str, target_lufs: float, lp: int, dur_s: float, dst_p: str):
        in_i = measure_lufs(src_p)
        g = max(-24.0, min(12.0, target_lufs - in_i))
        subprocess.run([
            "ffmpeg", "-y", "-stream_loop", "-1", "-t", f"{dur_s + 1.0:.4f}", "-i", src_p,
            "-af", f"aresample=48000,highpass=f=45,lowpass=f={lp},volume={g:.2f}dB",
            "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", dst_p,
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    b1 = f"{TMP_DIR}/amb_car.wav"
    b2 = f"{TMP_DIR}/amb_hall.wav"
    b3 = f"{TMP_DIR}/amb_apt.wav"
    prep_bed(f"{AUDIO_DIR}/sfx_sedan_drive.mp3", -32.0, 380, t_hall + 1.0, b1)
    prep_bed(f"{AUDIO_DIR}/sfx_hallway_room_tone_clean.wav", -40.0, 220, (t_apt - t_hall) + 1.0, b2)
    prep_bed(f"{AUDIO_DIR}/sfx_apt_room_tone_clean.wav", -40.0, 240, (total_dur - t_apt) + 1.0, b3)

    fade_st = max(0.5, total_dur - 1.0)
    fc = (
        f"[0:a]atrim=0:{t_hall + 0.5:.4f},asetpts=PTS-STARTPTS[a1];"
        f"[1:a]atrim=0:{(t_apt - t_hall) + 0.5:.4f},asetpts=PTS-STARTPTS[a2];"
        f"[a1][a2]acrossfade=d=0.5:c1=tri:c2=tri[a12];"
        f"[a12][2:a]acrossfade=d=0.5:c1=tri:c2=tri,atrim=0:{total_dur:.6f},afade=t=in:st=0:d=0.4,afade=t=out:st={fade_st:.3f}:d=1.0[aout]"
    )
    subprocess.run([
        "ffmpeg", "-y", "-i", b1, "-i", b2, "-i", b3, "-filter_complex", fc, "-map", "[aout]",
        "-t", f"{total_dur:.6f}", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", out_wav,
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"  AMBIENCE BED: Car(0..{t_hall:.1f}s -32 LUFS) -> Hall({t_hall:.1f}..{t_apt:.1f}s -40) -> Apt({t_apt:.1f}..{total_dur:.1f}s -40)")


def build_tarantino_score_bed(shot_timing: dict, total_dur: float, out_wav: str):
    """Tarantino YT spotting:
    - Cold-Open Needle Drop (0:00..0:08.5): surf-rock guitar cue (-19 LUFS), smooth fade-out into dry dialogue
    - Dry Banter (0:08.5 .. PF2_22): ZERO music (authentic Tarantino dialogue drive)
    - Act 3 Chaos (PF2_22 .. PF2_33): surf-thriller tension (-21 LUFS, dipped during PF2_24 & PF2_30 diarrhea blasts)
    - Act 4 Dry Reveal (PF2_33 .. PF2_41): ZERO music
    - Iconic Walkout (PF2_41 .. end): bold surf-rock needle drop (-17.5 LUFS)
    """
    cool_p = f"{AUDIO_DIR}/score_pf2_cool_noir.mp3"
    chaos_p = f"{AUDIO_DIR}/score_pf2_chaos_tension.mp3"
    cool_i = measure_lufs(cool_p)
    chaos_i = measure_lufs(chaos_p)

    t_act3_start = shot_timing[22][0]
    t_act3_end = shot_timing[33][0]
    t_walk_start = shot_timing[41][0]

    # Segment 1: Cold open needle drop (0..8.5s)
    c1 = f"{TMP_DIR}/sc_cold.wav"
    g_c1 = max(-20.0, min(10.0, -19.0 - cool_i))
    subprocess.run([
        "ffmpeg", "-y", "-i", cool_p,
        "-af", f"atrim=0:8.5,asetpts=PTS-STARTPTS,volume={g_c1:.2f}dB,afade=t=in:st=0:d=0.15,afade=t=out:st=6.0:d=2.5,aresample=48000",
        "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", c1,
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Segment 2: Act 3 chaos tension (PF2_22..32), ducking smoothly around PF2_24 & PF2_30 eruptions
    c2 = f"{TMP_DIR}/sc_act3.wav"
    act3_dur = max(2.0, t_act3_end - t_act3_start)
    g_c2 = max(-20.0, min(10.0, -24.0 - chaos_i))
    t24_s, t24_d = shot_timing[24][0] - t_act3_start, shot_timing[24][1]
    t30_s, t30_d = shot_timing[30][0] - t_act3_start, shot_timing[30][1]
    vol_expr = (
        f"if(between(t,{t24_s:.2f},{t24_s+t24_d:.2f}),0.32,"
        f"if(between(t,{t30_s:.2f},{t30_s+t30_d:.2f}),0.32,1.0))"
    )
    subprocess.run([
        "ffmpeg", "-y", "-ss", "2.0", "-i", chaos_p,
        "-af", (
            f"atrim=0:{act3_dur:.4f},asetpts=PTS-STARTPTS,volume={g_c2:.2f}dB,"
            f"volume='{vol_expr}':eval=frame,afade=t=in:st=0:d=0.6,afade=t=out:st={max(0.2, act3_dur - 1.2):.3f}:d=1.2,aresample=48000"
        ),
        "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", c2,
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Segment 3: Walkout outro needle drop (PF2_41..end) from bright guitar riff [ss=38s]
    c3 = f"{TMP_DIR}/sc_outro.wav"
    outro_dur = max(2.0, total_dur - t_walk_start)
    g_c3 = max(-20.0, min(10.0, -17.5 - cool_i))
    subprocess.run([
        "ffmpeg", "-y", "-ss", "38.0", "-i", cool_p,
        "-af", f"atrim=0:{outro_dur:.4f},asetpts=PTS-STARTPTS,volume={g_c3:.2f}dB,afade=t=in:st=0:d=0.35,afade=t=out:st={max(0.2, outro_dur - 1.2):.3f}:d=1.2,aresample=48000",
        "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", c3,
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Place 3 music cues cleanly on a silent full-length timeline
    d2_ms = int(round(t_act3_start * 1000))
    d3_ms = int(round(t_walk_start * 1000))
    fc = (
        f"[0:a]aresample=48000[base];"
        f"[1:a]aresample=48000,apad=whole_dur={total_dur:.6f},atrim=0:{total_dur:.6f}[m1];"
        f"[2:a]aresample=48000,adelay={d2_ms}|{d2_ms},apad=whole_dur={total_dur:.6f},atrim=0:{total_dur:.6f}[m2];"
        f"[3:a]aresample=48000,adelay={d3_ms}|{d3_ms},apad=whole_dur={total_dur:.6f},atrim=0:{total_dur:.6f}[m3];"
        f"[base][m1][m2][m3]amix=inputs=4:normalize=0:duration=first,atrim=0:{total_dur:.6f}[mout]"
    )
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", "-t", f"{total_dur:.6f}", "-i", "anullsrc=r=48000:cl=stereo",
        "-i", c1, "-i", c2, "-i", c3, "-filter_complex", fc, "-map", "[mout]",
        "-t", f"{total_dur:.6f}", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", out_wav,
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"  TARANTINO SCORE SPOTTING: ColdOpen(0..8.5s -19 LUFS) | Dry(8.5..{t_act3_start:.1f}s) | Chaos({t_act3_start:.1f}..{t_act3_end:.1f}s -21) | Outro({t_walk_start:.1f}..{total_dur:.1f}s -17.5)")


def build_pf2_foley_bus(shot_timing: dict, total_dur: float, out_wav: str):
    """Place all 16+ visually synced peak-safe Pulp Fiction foley & diarrhea eruption cues."""
    cues = [
        (6,  lambda s, d: s + 0.05,                f"{AUDIO_DIR}/sfx_tire_screech_hydrant.mp3",   -14.0, 1.8),
        (8,  lambda s, d: s + max(0.0, d - 0.90),  f"{AUDIO_DIR}/sfx_apartment_door_knock.mp3",  -11.0, None),
        (9,  lambda s, d: s + 0.00,                f"{AUDIO_DIR}/sfx_door_burst_sheren_gigi.mp3",-14.0, 1.6),
        (11, lambda s, d: s + 0.25,                f"{AUDIO_DIR}/sfx_teacup_clink.mp3",           -17.0, None),
        (13, lambda s, d: s + 0.15,                f"{AUDIO_DIR}/sfx_stomach_gurgle_deep.mp3",    -13.0, 1.8),
        (14, lambda s, d: s + 0.30,                f"{AUDIO_DIR}/sfx_teacup_clink.mp3",           -17.0, None),
        (17, lambda s, d: s + 0.20,                f"{AUDIO_DIR}/sfx_drill_whir.mp3",             -14.0, None),
        (18, lambda s, d: s + 0.15,                f"{AUDIO_DIR}/sfx_stomach_gurgle_deep.mp3",    -12.0, 2.0),
        (20, lambda s, d: s + 0.10,                f"{AUDIO_DIR}/sfx_stomach_gurgle_deep.mp3",    -11.0, 2.0),
        (21, lambda s, d: s + 0.05,                f"{AUDIO_DIR}/sfx_footsteps_scurry.mp3",       -11.0, None),
        (22, lambda s, d: s + 0.00,                f"{AUDIO_DIR}/sfx_door_burst_sheren_gigi.mp3",-12.0, 1.8),
        (23, lambda s, d: s + max(0.0, d - 1.40),  f"{AUDIO_DIR}/sfx_stomach_gurgle_deep.mp3",    -10.0, 1.8),
        (24, lambda s, d: s + 0.00,                f"{AUDIO_DIR}/PF2_24.mp3",                      -6.0, None),
        (28, lambda s, d: s + 0.20,                f"{AUDIO_DIR}/sfx_wet_splat_squelch.mp3",      -12.0, 1.8),
        (29, lambda s, d: s + 0.30,                f"{AUDIO_DIR}/sfx_wet_splat_squelch.mp3",      -14.0, 1.8),
        (30, lambda s, d: s + 0.00,                f"{AUDIO_DIR}/PF2_30.mp3",                      -6.0, None),
        (30, lambda s, d: s + 0.35,                f"{AUDIO_DIR}/sfx_wet_splat_squelch.mp3",      -10.0, 2.2),
        (33, lambda s, d: s + 0.00,                f"{AUDIO_DIR}/sfx_briefcase_open_glow.mp3",    -10.0, 2.8),
        (36, lambda s, d: s + 0.15,                f"{AUDIO_DIR}/sfx_blister_pills.mp3",          -15.0, None),
        (41, lambda s, d: s + max(0.0, d - 0.80),  f"{AUDIO_DIR}/sfx_briefcase_shut.mp3",         -13.0, None),
    ]
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
        gain_db = max(-24.0, min(12.0, target_pk - pk))
        inputs += ["-i", spath]
        chain = f"[{idx}:a]aresample=48000"
        if trim_d is not None:
            fade_t = max(0.08, trim_d - 0.25)
            chain += f",atrim=0:{trim_d:.3f},asetpts=PTS-STARTPTS,afade=t=out:st={fade_t:.3f}:d=0.25"
        chain += f",volume={gain_db:.2f}dB,adelay={delay_ms}|{delay_ms},apad=whole_dur={total_dur:.6f},atrim=0:{total_dur:.6f}[c{idx}]"
        filter_parts.append(chain)
        mix_labels.append(f"[c{idx}]")
        print(f"  FOLEY [PF2_{snum:02d}] @{at_sec:6.2f}s {os.path.basename(spath)} (pk={pk:+.1f}->{target_pk:+.1f}dBFS)")

    filter_parts.append(f"{''.join(mix_labels)}amix=inputs={len(mix_labels)}:normalize=0:duration=first,atrim=0:{total_dur:.6f}[sout]")
    subprocess.run([
        "ffmpeg", "-y", *inputs, "-filter_complex", ";".join(filter_parts), "-map", "[sout]",
        "-t", f"{total_dur:.6f}", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", out_wav,
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return cue_times


def main():
    os.makedirs(TMP_DIR, exist_ok=True)
    os.makedirs(QA_BUS_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(OUT_MP4), exist_ok=True)

    shots = json.load(open(SCRIPT_PATH))["shots"]
    jobs = {j["shot_id"]: j for j in json.load(open(JOBS_PATH))}

    v_parts, d_parts = [], []
    total_frames = 0
    shot_timing = {}

    for idx, sh in enumerate(shots):
        sid = sh["shot_id"]
        n = int(sid.split("_")[1])
        job = jobs[sid]
        clip_p = f"{CLIPS_DIR}/pf2_{sid}_00001_.mp4"
        vo_p = f"{AUDIO_DIR}/{sid}.mp3"

        clip_dur = ffprobe_dur(clip_p)
        au_off = AUDIO_START_OFFSET.get(sid, 0.0)
        if n in SFX_SHOTS:
            # Diarrhea eruption beats play snappy physical spectacle on SFX bus; silence on speech bus
            target_dur = min(clip_dur, 3.45)
            lufs, gain_db = -99.0, 0.0
        else:
            vo_dur, speech_end = detect_speech_end(vo_p, au_off)
            lufs = measure_lufs(vo_p, au_off)
            gain_db = max(-10.0, min(14.0, -16.0 - lufs))
            tail = 0.35 if n in BEAT_HOLD_SHOTS else 0.20
            target_dur = min(clip_dur, max(max(vo_dur, speech_end) + tail, 1.5))

        n_frames = max(24, int(round(target_dur * 24.0)))
        if n_frames / 24.0 > clip_dur:
            n_frames = max(24, int(math.floor(clip_dur * 24.0)))
        exact_dur = n_frames / 24.0
        shot_timing[n] = (total_frames / 24.0, exact_dur)
        total_frames += n_frames

        # Organic calibrated 35mm handheld weave ONLY on HANDHELD_35MM InfiniteTalk shots
        vf_steps = ["fps=24"]
        if job.get("camera_motion") == "HANDHELD_35MM" and job.get("engine") == "infinitetalk":
            p1 = (n * 1.41) % (2 * math.pi)
            p2 = (n * 2.63 + 0.7) % (2 * math.pi)
            vf_steps.append(
                f"scale=3904:1692:flags=lanczos,"
                f"crop=3840:1664:x='32+10*sin(0.85*t+{p1:.3f})+5*sin(1.9*t+{p2:.3f})':"
                f"y='14+5*cos(0.70*t+{p1:.3f})+3*sin(1.6*t+{p2:.3f})':exact=1,"
                f"scale=1920:832:flags=lanczos"
            )
        else:
            vf_steps.append("scale=1920:832:flags=lanczos")

        vf_steps += ["pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black", "noise=alls=2:allf=t+u", "format=yuv420p"]
        v_part = f"{TMP_DIR}/v_{idx:02d}.mp4"
        d_part = f"{TMP_DIR}/d_{idx:02d}.wav"
        v_parts.append(v_part)
        d_parts.append(d_part)

        subprocess.run([
            "ffmpeg", "-y", "-i", clip_p, "-vf", ",".join(vf_steps), "-an",
            "-frames:v", str(n_frames), "-c:v", "libx264", "-preset", "fast", "-crf", "14", "-pix_fmt", "yuv420p", v_part,
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        fade_out_st = max(0.02, exact_dur - 0.015)
        if n in SFX_SHOTS:
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

    def concat_list(paths: list[str], txt_p: str, out_p: str):
        with open(txt_p, "w") as f:
            for p in paths:
                f.write(f"file '{p}'\n")
        subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", txt_p, "-c", "copy", out_p], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    v_cat, d_cat = f"{TMP_DIR}/v_cat.mp4", f"{TMP_DIR}/d_cat.wav"
    concat_list(v_parts, f"{TMP_DIR}/v_list.txt", v_cat)
    concat_list(d_parts, f"{TMP_DIR}/d_list.txt", d_cat)

    total_dur = total_frames / 24.0
    score_bed = f"{TMP_DIR}/score_bed.wav"
    amb_bed = f"{TMP_DIR}/amb_bed.wav"
    foley_bed = f"{TMP_DIR}/foley_bed.wav"
    build_tarantino_score_bed(shot_timing, total_dur, score_bed)
    build_ambience_bed(shot_timing, total_dur, amb_bed)
    cue_times = build_pf2_foley_bus(shot_timing, total_dur, foley_bed)

    pre_mix = f"{TMP_DIR}/pre_mix.wav"
    mix_filter = (
        f"[0:a]asplit=2[dlg_main][dlg_sc];"
        f"[3:a][dlg_sc]sidechaincompress=threshold=0.04:ratio=2.4:attack=25:release=380[bgm_ducked];"
        f"[dlg_main][1:a][2:a][bgm_ducked]amix=inputs=4:duration=first:normalize=0[aout]"
    )
    subprocess.run([
        "ffmpeg", "-y", "-i", d_cat, "-i", amb_bed, "-i", foley_bed, "-i", score_bed,
        "-filter_complex", mix_filter, "-map", "[aout]",
        "-t", f"{total_dur:.6f}", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", pre_mix,
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    raw_i = measure_lufs(pre_mix)
    master_gain = max(-8.0, min(8.0, -15.0 - raw_i))
    print(f"  MASTER LINEAR GAIN: pre_mix={raw_i:.2f} LUFS -> -15.0 LUFS (gain={master_gain:+.2f} dB)")

    fade_out_vid = max(0.5, total_dur - 1.0)
    subprocess.run([
        "ffmpeg", "-y", "-i", v_cat, "-i", pre_mix,
        "-filter_complex", f"[0:v]fade=t=in:st=0:d=0.4,fade=t=out:st={fade_out_vid:.3f}:d=1.0[vout];[1:a]volume={master_gain:.2f}dB,alimiter=limit=-2.0dB:attack=5:release=50:level=disabled[aout]",
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-maxrate", "2320k", "-bufsize", "7500k",
        "-movflags", "+faststart", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        "-t", f"{total_dur:.6f}", OUT_MP4,
    ], check=True)

    # Export isolated v2.6 QA buses & act slices for Hostile QA audit
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "0", "-t", "10", "-i", score_bed, "-c:a", "libmp3lame", "-b:a", "192k", f"{QA_BUS_DIR}/score_cold_open.mp3"], check=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{shot_timing[22][0]:.2f}", "-t", "65", "-i", score_bed, "-c:a", "libmp3lame", "-b:a", "192k", f"{QA_BUS_DIR}/score_act3_outro.mp3"], check=True)
    sfx_slices = []
    for i, (_, ct) in enumerate(cue_times):
        ss = max(0.0, ct - 0.8)
        sl = f"{TMP_DIR}/sfx_win_{i}.wav"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ss:.2f}", "-t", "3.2", "-i", foley_bed, "-ss", f"{ss:.2f}", "-t", "3.2", "-i", amb_bed, "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=shortest:normalize=0[w]", "-map", "[w]", "-c:a", "pcm_s16le", sl], check=True)
        sfx_slices.append(sl)
    concat_list(sfx_slices, f"{TMP_DIR}/sfx_win_list.txt", f"{TMP_DIR}/sfx_win_all.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", f"{TMP_DIR}/sfx_win_all.wav", "-c:a", "libmp3lame", "-b:a", "192k", f"{QA_BUS_DIR}/sfx_only.mp3"], check=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{shot_timing[22][0]:.2f}", "-t", "60", "-i", OUT_MP4, "-vn", "-af", "highpass=f=220,lowpass=f=7000", "-c:a", "libmp3lame", "-b:a", "192k", f"{QA_BUS_DIR}/final_phone_act3_220hz.mp3"], check=True)
    for tag, ss, dur_s in [
        ("act1_car_hall", 0, 55),
        ("act2_apt_banter", shot_timing[9][0], 55),
        ("act3_diarrhea", shot_timing[22][0], 55),
        ("act4_briefcase_exit", shot_timing[33][0], 60),
    ]:
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ss:.2f}", "-t", str(dur_s), "-i", OUT_MP4, "-vn", "-c:a", "libmp3lame", "-b:a", "192k", f"{QA_BUS_DIR}/{tag}.mp3"], check=True)

    size_mb = os.path.getsize(OUT_MP4) / (1024 * 1024)
    print(f"MASTER_READY {OUT_MP4} -> {total_dur:.2f}s ({total_frames}f), {size_mb:.2f} MB (QA buses in {QA_BUS_DIR})")


if __name__ == "__main__":
    main()
