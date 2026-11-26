"""Assemble the 40-shot Hollywood 1080p Scope master for Dark Knight v2 with leveled Two-Act Zimmer score & cinema SFX."""
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

# DK2_01 now rendered on InfiniteTalk with dk2_shot01_fixed.jpg so Gigi matches DK2_02..09 seamlessly
LTX_SHOTS = {2, 3, 4, 6, 8, 9, 11, 17, 19, 27}
BEAT_HOLD_SHOTS = {9, 10, 27, 40}
AUDIO_START_OFFSET = {"DK2_04": 0.083}
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


def build_seamless_score_bed(act1_dur: float, total_dur: float, out_wav: str):
    """Build continuous seam-free Two-Act Hans Zimmer underscore leveled to -22.5 LUFS (Act 1) / -21.5 LUFS (Act 2/3)."""
    s1_mp3 = f"{AUDIO_DIR}/score_dk_act1_dark.mp3"
    s2_mp3 = f"{AUDIO_DIR}/score_dk_act2_intense.mp3"

    def make_loop_wav(src_mp3: str, target_lufs: float, needed_dur: float, dst_wav: str):
        in_lufs = measure_lufs(src_mp3)
        gain_db = max(-18.0, min(18.0, target_lufs - in_lufs))
        # Trim the natural 22s generation before its end fade-out (keep active 18.0s core) and crossfade loops cleanly
        seg_len = 17.5
        tile_wav = dst_wav + ".tile.wav"
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", src_mp3,
                "-af", f"atrim=0:{seg_len},asetpts=PTS-STARTPTS,volume={gain_db:.2f}dB,aresample=48000",
                "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", tile_wav,
            ],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        # Concatenate with 1.2s acrossfade to eliminate loop seams until > needed_dur
        cur = tile_wav
        reps = int(math.ceil((needed_dur + 3.0) / (seg_len - 1.2)))
        inputs = []
        fparts = []
        for idx in range(max(2, reps)):
            inputs += ["-i", tile_wav]
        chain = "[0:a][1:a]acrossfade=d=1.2:c1=tri:c2=tri[a1]"
        for idx in range(2, max(2, reps)):
            prev = f"a{idx-1}"
            nxt = f"a{idx}" if idx < max(2, reps) - 1 else "aout"
            chain += f";[{prev}][{idx}:a]acrossfade=d=1.2:c1=tri:c2=tri[{nxt}]"
        if max(2, reps) == 2:
            chain = "[0:a][1:a]acrossfade=d=1.2:c1=tri:c2=tri[aout]"
        subprocess.run(
            [
                "ffmpeg", "-y", *inputs, "-filter_complex", chain, "-map", "[aout]",
                "-t", f"{needed_dur + 0.8:.4f}", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", dst_wav,
            ],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        os.remove(tile_wav)
        print(f"  SCORE BED {os.path.basename(src_mp3)}: raw={in_lufs:.1f} LUFS -> leveled={target_lufs:.1f} LUFS ({gain_db:+.1f} dB)")

    act1_wav = f"{TMP_DIR}/score_act1.wav"
    act2_wav = f"{TMP_DIR}/score_act2.wav"
    act2_needed = max(5.0, total_dur - act1_dur + 1.5)
    make_loop_wav(s1_mp3, -22.5, act1_dur + 0.8, act1_wav)
    make_loop_wav(s2_mp3, -21.5, act2_needed, act2_wav)

    fade_out_bgm = max(1.0, total_dur - 1.4)
    # Crossfade cleanly right when fluorescent lights slam ON (t = act1_dur)
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", act1_wav, "-i", act2_wav,
            "-filter_complex", (
                f"[0:a]atrim=0:{act1_dur + 0.5:.4f},asetpts=PTS-STARTPTS[s1];"
                f"[s1][1:a]acrossfade=d=0.6:c1=tri:c2=tri,atrim=0:{total_dur:.6f},"
                f"afade=t=in:st=0:d=0.8,afade=t=out:st={fade_out_bgm:.3f}:d=1.4[bout]"
            ),
            "-map", "[bout]", "-t", f"{total_dur:.6f}", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", out_wav,
        ],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def main():
    os.makedirs(TMP_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(OUT_MP4), exist_ok=True)
    shots = json.load(open(SCRIPT_PATH))["shots"]

    # Cache measured LUFS of all SFX stems
    sfx_lufs_cache = {}
    def get_sfx_gain(path: str, target_lufs: float) -> float:
        if path not in sfx_lufs_cache:
            sfx_lufs_cache[path] = measure_lufs(path)
        return max(-24.0, min(18.0, target_lufs - sfx_lufs_cache[path]))

    room_buzz = f"{AUDIO_DIR}/sfx_fluorescent_buzz.mp3"

    v_parts, d_parts, s_parts = [], [], []
    total_frames = 0
    act1_frames = 0

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
        s_part = f"{TMP_DIR}/s_{idx:02d}.wav"
        v_parts.append(v_part)
        d_parts.append(d_part)
        s_parts.append(s_part)

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

        # 3) Leveled room tone + beat-synced cinema SFX WAV
        buzz_target = -36.0 if sh["act"] == 1 else -32.0
        buzz_gain = get_sfx_gain(room_buzz, buzz_target)

        sfx_map = {
            1: (f"{AUDIO_DIR}/sfx_door_heavy_enter.mp3", -17.0, 0),
            8: (f"{AUDIO_DIR}/sfx_handcuffs_unlock.mp3", -17.0, 300),
            9: (f"{AUDIO_DIR}/sfx_door_exit_switch.mp3", -16.0, int(max(0.0, exact_dur - 2.6) * 1000)),
            10: (f"{AUDIO_DIR}/sfx_light_slam_v2.mp3", -13.0, 0),
            12: (f"{AUDIO_DIR}/sfx_table_slam.mp3", -14.0, 0),
            27: (f"{AUDIO_DIR}/sfx_wall_slam.mp3", -13.0, 80),
            29: (f"{AUDIO_DIR}/sfx_collar_scuffle.mp3", -18.0, 0),
            31: (f"{AUDIO_DIR}/sfx_collar_scuffle.mp3", -18.0, 150),
            34: (f"{AUDIO_DIR}/sfx_table_crash.mp3", -14.0, 0),
            35: (f"{AUDIO_DIR}/sfx_door_clank.mp3", -14.0, 120),
            39: (f"{AUDIO_DIR}/sfx_batman_exit.mp3", -17.0, int(max(0.0, exact_dur - 2.4) * 1000)),
        }

        if n in sfx_map and os.path.exists(sfx_map[n][0]):
            sp, tgt_lufs, delay_ms = sfx_map[n]
            hit_gain = get_sfx_gain(sp, tgt_lufs)
            s_af = (
                f"[0:a]aresample=48000,volume={buzz_gain:.2f}dB[rz];"
                f"[1:a]aresample=48000,volume={hit_gain:.2f}dB,adelay={delay_ms}|{delay_ms},apad=whole_dur={exact_dur:.6f}[hit];"
                f"[rz][hit]amix=inputs=2:duration=first:normalize=0,atrim=0:{exact_dur:.6f},"
                f"afade=t=in:st=0:d=0.015,afade=t=out:st={fade_out_st:.6f}:d=0.015[sout]"
            )
            s_cmd = [
                "ffmpeg", "-y", "-stream_loop", "-1", "-t", f"{exact_dur:.6f}", "-i", room_buzz,
                "-i", sp, "-filter_complex", s_af, "-map", "[sout]",
                "-t", f"{exact_dur:.6f}", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", s_part,
            ]
        else:
            s_cmd = [
                "ffmpeg", "-y", "-stream_loop", "-1", "-t", f"{exact_dur:.6f}", "-i", room_buzz,
                "-af", (
                    f"aresample=48000,volume={buzz_gain:.2f}dB,atrim=0:{exact_dur:.6f},"
                    f"afade=t=in:st=0:d=0.015,afade=t=out:st={fade_out_st:.6f}:d=0.015"
                ),
                "-t", f"{exact_dur:.6f}", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", s_part,
            ]
        subprocess.run(s_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"  [{sid}] cut={exact_dur:.2f}s ({n_frames}f) dlg={lufs:.1f}->{gain_db:+.1f}dB" + (f" +SFX({os.path.basename(sfx_map[n][0])})" if n in sfx_map else ""), flush=True)

    def concat_list(paths: list[str], txt_p: str, out_p: str):
        with open(txt_p, "w") as f:
            for p in paths:
                f.write(f"file '{p}'\n")
        subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", txt_p, "-c", "copy", out_p], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    v_cat, d_cat, s_cat = f"{TMP_DIR}/v_cat.mp4", f"{TMP_DIR}/d_cat.wav", f"{TMP_DIR}/s_cat.wav"
    concat_list(v_parts, f"{TMP_DIR}/v_list.txt", v_cat)
    concat_list(d_parts, f"{TMP_DIR}/d_list.txt", d_cat)
    concat_list(s_parts, f"{TMP_DIR}/s_list.txt", s_cat)

    total_dur = total_frames / 24.0
    act1_dur = act1_frames / 24.0
    score_bed = f"{TMP_DIR}/score_bed.wav"
    build_seamless_score_bed(act1_dur, total_dur, score_bed)

    fade_out_vid = max(0.5, total_dur - 1.0)
    pre_mix = f"{TMP_DIR}/pre_mix.wav"
    # Gentle -3.5dB sidechain ducking under active dialogue so score breathes clearly between lines & stays audible under speech
    mix_filter = (
        f"[0:a]asplit=2[dlg_main][dlg_sc];"
        f"[2:a][dlg_sc]sidechaincompress=threshold=0.05:ratio=2.2:attack=35:release=400[bgm_ducked];"
        f"[dlg_main][1:a][bgm_ducked]amix=inputs=3:duration=first:normalize=0[aout]"
    )
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", d_cat, "-i", s_cat, "-i", score_bed,
            "-filter_complex", mix_filter, "-map", "[aout]",
            "-t", f"{total_dur:.6f}", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", pre_mix,
        ],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )

    m_res = subprocess.run(
        ["ffmpeg", "-i", pre_mix, "-af", "loudnorm=I=-14:TP=-1.5:LRA=9:print_format=json", "-f", "null", "-"],
        capture_output=True, text=True, check=True,
    )
    stats = json.loads(re.search(r"\{[\s\S]*?\}", m_res.stderr).group(0))
    ln_filter = (
        f"loudnorm=I=-14:TP=-1.5:LRA=9:linear=true:"
        f"measured_I={stats['input_i']}:measured_TP={stats['input_tp']}:"
        f"measured_LRA={stats['input_lra']}:measured_thresh={stats['input_thresh']}:"
        f"offset={stats['target_offset']}"
    )

    subprocess.run(
        [
            "ffmpeg", "-y", "-i", v_cat, "-i", pre_mix,
            "-filter_complex", f"[0:v]fade=t=in:st=0:d=0.4,fade=t=out:st={fade_out_vid:.3f}:d=1.0[vout];[1:a]{ln_filter}[aout]",
            "-map", "[vout]", "-map", "[aout]",
            "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-maxrate", "2550k", "-bufsize", "8000k",
            "-movflags", "+faststart", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            "-t", f"{total_dur:.6f}", OUT_MP4,
        ],
        check=True,
    )
    size_mb = os.path.getsize(OUT_MP4) / (1024 * 1024)
    print(f"MASTER_READY {OUT_MP4} -> {total_dur:.2f}s ({total_frames}f), {size_mb:.2f} MB")


if __name__ == "__main__":
    main()
