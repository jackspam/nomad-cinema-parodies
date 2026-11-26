"""Assemble the 40-shot Hollywood 1080p Scope master for Dark Knight v2 with Lyria 3.5 Two-Act score & peak-safe cinema SFX."""
import json
import math
import os
import re
import subprocess
import numpy as np

BASE = "/Users/jack/.gemini/antigravity/scratch/nomad-cinema-parodies"
SCRIPT_PATH = f"{BASE}/scripts/02_dark_knight_v2_script.json"
CLIPS_DIR = f"{BASE}/clips/02_dark_knight_v2"
AUDIO_DIR = f"{BASE}/audio/02_dark_knight_v2"
OUT_MP4 = f"{BASE}/films/02_dark_knight_1080p.mp4"
TMP_DIR = f"{CLIPS_DIR}/_assembled_parts"
QA_BUS_DIR = "/tmp/qa_buses"

# DK2_01 & DK2_08 now rendered on InfiniteTalk with matched hair-down keyframes
LTX_SHOTS = {2, 3, 4, 6, 9, 11, 17, 19, 27}
BEAT_HOLD_SHOTS = {9, 10, 27, 40}
AUDIO_START_OFFSET = {"DK2_04": 0.083, "DK2_08": 0.083}
PER_SHOT_GRADE = {}


def ffprobe_dur(path: str) -> float:
    return float(
        subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path],
            text=True,
        ).strip()
    )


def detect_speech_end(mp3_path: str, audio_offset: float = 0.0) -> tuple[float, float]:
    """Return (raw_shifted_dur, speech_end_sec) using 20ms RMS envelope (> -38 dB)."""
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
    blocks = arr[: n_win * win].reshape(n_win, win)
    rms = np.sqrt(np.mean(blocks * blocks, axis=1))
    active = np.where(rms > 0.012)[0]
    if len(active) == 0:
        return dur, dur
    speech_end = min(dur, (active[-1] + 1) * (win / 16000.0))
    return dur, speech_end


def measure_lufs(audio_path: str, audio_offset: float = 0.0) -> float:
    cmd = ["ffmpeg"]
    if audio_offset > 0:
        cmd += ["-ss", f"{audio_offset:.4f}"]
    cmd += ["-i", audio_path, "-af", "loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json", "-f", "null", "-"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    m = re.search(r"\{[\s\S]*?\}", res.stderr)
    return float(json.loads(m.group(0))["input_i"]) if m else -20.0


def measure_peak_db(audio_path: str) -> float:
    res = subprocess.run(
        ["ffmpeg", "-i", audio_path, "-af", "volumedetect", "-f", "null", "-"],
        capture_output=True, text=True, check=True,
    )
    m = re.search(r"max_volume:\s*([-\d.]+)\s*dB", res.stderr)
    return float(m.group(1)) if m else 0.0


def build_seamless_score_bed(act1_dur: float, total_dur: float, out_wav: str):
    """Build continuous Lyria 3.5 Two-Act score leveled to -19.5 LUFS (Act 1) / -18.0 LUFS (Act 2/3)."""
    s1_mp3 = f"{AUDIO_DIR}/score_dk_act1_dark.mp3"
    s2_mp3 = f"{AUDIO_DIR}/score_dk_act2_intense.mp3"

    # Extract rich solo-cello/ticking interrogation core starting at t=12.0s (covers ~52s Act 1 without looping)
    s1_in_lufs = measure_lufs(s1_mp3, 12.0)
    s1_gain = max(-18.0, min(12.0, -19.5 - s1_in_lufs))
    act1_wav = f"{TMP_DIR}/score_act1.wav"
    subprocess.run(
        [
            "ffmpeg", "-y", "-ss", "12.0", "-i", s1_mp3,
            "-af", f"atrim=0:{act1_dur + 1.5:.4f},asetpts=PTS-STARTPTS,volume={s1_gain:.2f}dB,aresample=48000",
            "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", act1_wav,
        ],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    print(f"  SCORE ACT 1 {os.path.basename(s1_mp3)} (ss=12s): raw={s1_in_lufs:.1f} -> -19.5 LUFS ({s1_gain:+.1f} dB)")

    # Extract driving orchestral intense core starting at t=8.0s; crossfade once cleanly to cover Act 2/3
    s2_dur = ffprobe_dur(s2_mp3)
    s2_seg_len = min(145.0, max(30.0, s2_dur - 16.0))
    s2_in_lufs = measure_lufs(s2_mp3, 8.0)
    s2_gain = max(-18.0, min(12.0, -18.0 - s2_in_lufs))
    s2_seg = f"{TMP_DIR}/score_act2_seg.wav"
    subprocess.run(
        [
            "ffmpeg", "-y", "-ss", "8.0", "-i", s2_mp3,
            "-af", f"atrim=0:{s2_seg_len:.4f},asetpts=PTS-STARTPTS,volume={s2_gain:.2f}dB,aresample=48000",
            "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", s2_seg,
        ],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    act2_needed = max(5.0, total_dur - act1_dur + 2.0)
    act2_wav = f"{TMP_DIR}/score_act2.wav"
    if act2_needed <= s2_seg_len:
        subprocess.run(
            ["ffmpeg", "-y", "-i", s2_seg, "-t", f"{act2_needed:.4f}", "-c:a", "copy", act2_wav],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    else:
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", s2_seg, "-i", s2_seg,
                "-filter_complex", "[0:a][1:a]acrossfade=d=3.0:c1=tri:c2=tri[aout]",
                "-map", "[aout]", "-t", f"{act2_needed:.4f}",
                "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", act2_wav,
            ],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    print(f"  SCORE ACT 2/3 {os.path.basename(s2_mp3)} (ss=8s): raw={s2_in_lufs:.1f} -> -18.0 LUFS ({s2_gain:+.1f} dB)")

    fade_out_bgm = max(1.0, total_dur - 1.6)
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", act1_wav, "-i", act2_wav,
            "-filter_complex", (
                f"[0:a]atrim=0:{act1_dur + 0.6:.4f},asetpts=PTS-STARTPTS[s1];"
                f"[s1][1:a]acrossfade=d=1.0:c1=tri:c2=tri,atrim=0:{total_dur:.6f},"
                f"afade=t=in:st=0:d=0.6,afade=t=out:st={fade_out_bgm:.3f}:d=1.6[bout]"
            ),
            "-map", "[bout]", "-t", f"{total_dur:.6f}", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", out_wav,
        ],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def build_continuous_room_tone(total_dur: float, out_wav: str):
    """Build ONE continuous <240Hz clean room ambience bed across full runtime (no per-shot cuts)."""
    src = f"{AUDIO_DIR}/sfx_room_tone_clean.wav"
    in_lufs = measure_lufs(src)
    gain = max(-24.0, min(12.0, -42.0 - in_lufs))
    fade_st = max(0.5, total_dur - 1.0)
    subprocess.run(
        [
            "ffmpeg", "-y", "-stream_loop", "-1", "-t", f"{total_dur:.6f}", "-i", src,
            "-af", f"aresample=48000,highpass=f=45,lowpass=f=240,volume={gain:.2f}dB,afade=t=in:st=0:d=0.5,afade=t=out:st={fade_st:.3f}:d=1.0",
            "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", out_wav,
        ],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    print(f"  ROOM TONE continuous {os.path.basename(src)}: raw={in_lufs:.1f} -> -42.0 LUFS ({gain:+.1f} dB)")


def build_timeline_sfx_bus(shot_timing: dict, total_dur: float, out_wav: str):
    """Place strictly visually-verified, peak-normalized SFX cues at exact timeline timestamps."""
    cues = [
        # (shot_num, offset_fn, path, target_peak_db, trim_dur_or_None)
        (9, lambda s, d: s + max(0.0, d - 0.85), f"{AUDIO_DIR}/sfx_dk_door_latch.mp3", -14.0, None),
        (10, lambda s, d: s + 0.0, f"{AUDIO_DIR}/sfx_dk_light_thunk.mp3", -11.0, 0.55),
        (27, lambda s, d: s + 0.15, f"{AUDIO_DIR}/sfx_dk_wall_thud.mp3", -8.0, None),
        (35, lambda s, d: s + 0.08, f"{AUDIO_DIR}/sfx_dk_knob_rattle.mp3", -14.0, None),
    ]
    inputs = ["-f", "lavfi", "-t", f"{total_dur:.6f}", "-i", "anullsrc=r=48000:cl=stereo"]
    filter_parts = ["[0:a]aresample=48000[base]"]
    mix_labels = ["[base]"]

    for idx, (snum, off_fn, spath, target_pk, trim_d) in enumerate(cues, start=1):
        st, sd = shot_timing[snum]
        at_sec = max(0.0, off_fn(st, sd))
        delay_ms = int(round(at_sec * 1000.0))
        pk = measure_peak_db(spath)
        gain_db = max(-24.0, min(12.0, target_pk - pk))
        inputs += ["-i", spath]
        chain = f"[{idx}:a]aresample=48000"
        if trim_d is not None:
            fade_t = max(0.08, trim_d - 0.30)
            chain += f",atrim=0:{trim_d:.3f},asetpts=PTS-STARTPTS,afade=t=out:st={fade_t:.3f}:d=0.30"
        chain += f",volume={gain_db:.2f}dB,adelay={delay_ms}|{delay_ms},apad=whole_dur={total_dur:.6f},atrim=0:{total_dur:.6f}[c{idx}]"
        filter_parts.append(chain)
        mix_labels.append(f"[c{idx}]")
        print(f"  SFX CUE [DK2_{snum:02d}] @{at_sec:6.2f}s {os.path.basename(spath)} (pk={pk:+.1f}->{target_pk:+.1f}dBFS, gain={gain_db:+.1f}dB)")

    filter_parts.append(f"{''.join(mix_labels)}amix=inputs={len(mix_labels)}:normalize=0:duration=first,atrim=0:{total_dur:.6f}[sout]")
    subprocess.run(
        ["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(filter_parts), "-map", "[sout]", "-t", f"{total_dur:.6f}", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", out_wav],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    return [(snum, off_fn(*shot_timing[snum])) for snum, off_fn, _, _, _ in cues]


def main():
    os.makedirs(TMP_DIR, exist_ok=True)
    os.makedirs(QA_BUS_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(OUT_MP4), exist_ok=True)
    shots = json.load(open(SCRIPT_PATH))["shots"]

    v_parts, d_parts = [], []
    total_frames = 0
    act1_frames = 0
    shot_timing = {}

    for idx, sh in enumerate(shots):
        sid = sh["shot_id"]
        n = int(sid.split("_")[1])
        clip_p = f"{CLIPS_DIR}/dk2_{sid}_00001_.mp4"
        vo_p = f"{AUDIO_DIR}/{sid}.mp3"

        clip_dur = ffprobe_dur(clip_p)
        au_off = AUDIO_START_OFFSET.get(sid, 0.0)
        vo_dur, speech_end = detect_speech_end(vo_p, au_off)
        lufs = measure_lufs(vo_p, au_off)
        gain_db = max(-10.0, min(14.0, -16.0 - lufs))

        tail = 0.35 if n in BEAT_HOLD_SHOTS else 0.20
        base_end = max(vo_dur, speech_end)
        if n == 27:
            target_dur = min(clip_dur, max(base_end + tail, clip_dur - 0.05))
        else:
            target_dur = min(clip_dur, max(base_end + tail, 1.5))

        n_frames = max(24, int(round(target_dur * 24.0)))
        if n_frames / 24.0 > clip_dur:
            n_frames = max(24, int(math.floor(clip_dur * 24.0)))
        exact_dur = n_frames / 24.0
        shot_timing[n] = (total_frames / 24.0, exact_dur)
        total_frames += n_frames
        if sh["act"] == 1:
            act1_frames += n_frames

        # 1) Video chain
        vf_steps = ["fps=24"]
        if n not in LTX_SHOTS:
            p1 = (n * 1.37) % (2 * math.pi)
            p2 = (n * 2.51 + 0.8) % (2 * math.pi)
            vf_steps.append(
                f"scale=3904:1692:flags=lanczos,"
                f"crop=3840:1664:x='32+10*sin(0.85*t+{p1:.3f})+5*sin(1.9*t+{p2:.3f})':"
                f"y='14+5*cos(0.70*t+{p1:.3f})+3*sin(1.6*t+{p2:.3f})':exact=1,"
                f"scale=1920:832:flags=lanczos"
            )
        else:
            vf_steps.append("scale=1920:832:flags=lanczos")

        if sid in PER_SHOT_GRADE:
            vf_steps.append(PER_SHOT_GRADE[sid])
        vf_steps += ["pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black", "noise=alls=2:allf=t+u", "format=yuv420p"]

        v_part = f"{TMP_DIR}/v_{idx:02d}.mp4"
        d_part = f"{TMP_DIR}/d_{idx:02d}.wav"
        v_parts.append(v_part)
        d_parts.append(d_part)

        subprocess.run(
            [
                "ffmpeg", "-y", "-i", clip_p, "-vf", ",".join(vf_steps), "-an",
                "-frames:v", str(n_frames), "-c:v", "libx264", "-preset", "fast", "-crf", "14", "-pix_fmt", "yuv420p", v_part,
            ],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )

        # 2) Zero-latency -16 LUFS dialogue WAV
        fade_out_st = max(0.02, exact_dur - 0.015)
        d_cmd = ["ffmpeg", "-y"]
        if au_off > 0:
            d_cmd += ["-ss", f"{au_off:.4f}"]
        d_cmd += [
            "-i", vo_p,
            "-af", (
                f"highpass=f=75,volume={gain_db:.2f}dB,aresample=48000,"
                f"apad=whole_dur={exact_dur:.6f},atrim=0:{exact_dur:.6f},"
                f"afade=t=in:st=0:d=0.015,afade=t=out:st={fade_out_st:.6f}:d=0.015"
            ),
            "-t", f"{exact_dur:.6f}", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", d_part,
        ]
        subprocess.run(d_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"  [{sid}] @{shot_timing[n][0]:6.2f}s cut={exact_dur:.2f}s ({n_frames}f) dlg={lufs:.1f}->{gain_db:+.1f}dB", flush=True)

    def concat_list(paths: list[str], txt_p: str, out_p: str):
        with open(txt_p, "w") as f:
            for p in paths:
                f.write(f"file '{p}'\n")
        subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", txt_p, "-c", "copy", out_p], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    v_cat, d_cat = f"{TMP_DIR}/v_cat.mp4", f"{TMP_DIR}/d_cat.wav"
    concat_list(v_parts, f"{TMP_DIR}/v_list.txt", v_cat)
    concat_list(d_parts, f"{TMP_DIR}/d_list.txt", d_cat)

    total_dur = total_frames / 24.0
    act1_dur = act1_frames / 24.0
    score_bed = f"{TMP_DIR}/score_bed.wav"
    room_cat = f"{TMP_DIR}/room_cat.wav"
    sfx_cat = f"{TMP_DIR}/sfx_cat.wav"

    build_seamless_score_bed(act1_dur, total_dur, score_bed)
    build_continuous_room_tone(total_dur, room_cat)
    cue_times = build_timeline_sfx_bus(shot_timing, total_dur, sfx_cat)

    fade_out_vid = max(0.5, total_dur - 1.0)
    pre_mix = f"{TMP_DIR}/pre_mix.wav"
    # Light ratio=1.8 ducking under speech keeps Lyria score clearly audible while never pumping dynamics
    mix_filter = (
        f"[0:a]asplit=2[dlg_main][dlg_sc];"
        f"[3:a][dlg_sc]sidechaincompress=threshold=0.06:ratio=1.8:attack=40:release=450[bgm_ducked];"
        f"[dlg_main][1:a][2:a][bgm_ducked]amix=inputs=4:duration=first:normalize=0[aout]"
    )
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", d_cat, "-i", room_cat, "-i", sfx_cat, "-i", score_bed,
            "-filter_complex", mix_filter, "-map", "[aout]",
            "-t", f"{total_dur:.6f}", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", pre_mix,
        ],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )

    # Pure linear master gain (-15.0 LUFS) + transparent safety limiter (-2.0 dBFS): leaves AAC headroom & preserves dynamics!
    raw_i = measure_lufs(pre_mix)
    master_gain = max(-8.0, min(8.0, -15.0 - raw_i))
    print(f"  MASTER LINEAR GAIN: pre_mix={raw_i:.2f} LUFS -> -15.0 LUFS (gain={master_gain:+.2f} dB)")

    subprocess.run(
        [
            "ffmpeg", "-y", "-i", v_cat, "-i", pre_mix,
            "-filter_complex", f"[0:v]fade=t=in:st=0:d=0.4,fade=t=out:st={fade_out_vid:.3f}:d=1.0[vout];[1:a]volume={master_gain:.2f}dB,alimiter=limit=-2.0dB:attack=5:release=50:level=disabled[aout]",
            "-map", "[vout]", "-map", "[aout]",
            "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-maxrate", "2550k", "-bufsize", "8000k",
            "-movflags", "+faststart", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            "-t", f"{total_dur:.6f}", OUT_MP4,
        ],
        check=True,
    )

    # Export isolated v2.5 QA buses + phone simulation before cleanup
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "0", "-t", "90", "-i", score_bed, "-c:a", "libmp3lame", "-b:a", "192k", f"{QA_BUS_DIR}/score_only.mp3"], check=True)
    # Concatenate 4s isolated SFX+room windows around every cue
    sfx_slices = []
    for i, (_, ct) in enumerate(cue_times):
        ss = max(0.0, ct - 1.0)
        sl = f"{TMP_DIR}/sfx_win_{i}.wav"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ss:.2f}", "-t", "4.0", "-i", sfx_cat, "-i", room_cat, "-filter_complex", "[0:a][1:a]amix=inputs=2:normalize=0[w]", "-map", "[w]", "-c:a", "pcm_s16le", sl], check=True)
        sfx_slices.append(sl)
    concat_list(sfx_slices, f"{TMP_DIR}/sfx_win_list.txt", f"{TMP_DIR}/sfx_win_all.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", f"{TMP_DIR}/sfx_win_all.wav", "-c:a", "libmp3lame", "-b:a", "192k", f"{QA_BUS_DIR}/sfx_only.mp3"], check=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "0", "-t", "75", "-i", OUT_MP4, "-vn", "-af", "highpass=f=220,lowpass=f=7000", "-c:a", "libmp3lame", "-b:a", "192k", f"{QA_BUS_DIR}/final_phone_220hz.mp3"], check=True)
    for tag, ss, dur_s in [("final_00_25", 0, 25), ("final_48_75", 48, 27), ("final_155_185", 155, 30)]:
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(ss), "-t", str(dur_s), "-i", OUT_MP4, "-vn", "-c:a", "libmp3lame", "-b:a", "192k", f"{QA_BUS_DIR}/{tag}.mp3"], check=True)

    size_mb = os.path.getsize(OUT_MP4) / (1024 * 1024)
    print(f"MASTER_READY {OUT_MP4} -> {total_dur:.2f}s ({total_frames}f), {size_mb:.2f} MB (QA buses saved in {QA_BUS_DIR})")


if __name__ == "__main__":
    main()
