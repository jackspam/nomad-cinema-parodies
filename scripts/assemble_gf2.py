"""Assemble Goodfellas v2 (04_goodfellas_1080p.mp4) with Copa walla -> hard dead-silence cut on 'Funny how lah?' -> finale swell."""
import subprocess
from v27_assemble_common import measure_lufs, place_sfx_cues, run_standard_assembly


def build_ambience(shot_timing, total_dur, out_wav, tmp_dir, audio_dir):
    # Room tone continuous all film (-38 LUFS) + supper-club walla strictly on GF2_01..04 cutting HARD SILENT at GF2_05!
    src_room = f"{audio_dir}/sfx_gf2_room_clean.wav"
    in_r = measure_lufs(src_room)
    g_r = max(-24.0, min(38.0, -34.0 - in_r))
    fade_st = max(0.5, total_dur - 1.0)
    r_wav = f"{tmp_dir}/amb_room.wav"
    subprocess.run([
        "ffmpeg", "-y", "-stream_loop", "-1", "-t", f"{total_dur + 0.5:.4f}", "-i", src_room,
        "-af", f"aresample=48000,highpass=f=50,lowpass=f=240,volume={g_r:.2f}dB,alimiter=limit=-14dB:level=disabled,atrim=0:{total_dur:.6f},afade=t=in:st=0:d=0.4,afade=t=out:st={fade_st:.3f}:d=1.0",
        "-t", f"{total_dur:.6f}", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", r_wav,
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    t_cut = shot_timing[5][0]  # exact frame boundary of GF2_05 ("Funny how lah?")
    src_w = f"{audio_dir}/sfx_gf2_supperclub_walla.mp3"
    in_w = measure_lufs(src_w)
    g_w = max(-24.0, min(12.0, -24.5 - in_w))
    w_wav = f"{tmp_dir}/amb_walla.wav"
    subprocess.run([
        "ffmpeg", "-y", "-stream_loop", "-1", "-t", f"{t_cut + 0.2:.4f}", "-i", src_w,
        "-af", f"aresample=48000,highpass=f=180,lowpass=f=4500,volume={g_w:.2f}dB,atrim=0:{t_cut:.6f},afade=t=in:st=0:d=0.3,afade=t=out:st={max(0.05, t_cut - 0.015):.4f}:d=0.015,apad=whole_dur={total_dur:.6f},atrim=0:{total_dur:.6f}",
        "-t", f"{total_dur:.6f}", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", w_wav,
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    subprocess.run([
        "ffmpeg", "-y", "-i", r_wav, "-i", w_wav,
        "-filter_complex", f"[0:a][1:a]amix=inputs=2:duration=first:normalize=0,atrim=0:{total_dur:.6f}[aout]",
        "-map", "[aout]", "-t", f"{total_dur:.6f}", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", out_wav,
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def build_score(shot_timing, total_dur, out_wav, tmp_dir, audio_dir):
    # Scorsese spotting: zero music during comedy -> confrontation tension; warm 1970s Copa closing swell on GF2_22..24
    t_start = shot_timing[22][0]
    dur = max(2.0, total_dur - t_start)
    src = f"{audio_dir}/score_gf2_finale_swell.mp3"
    in_i = measure_lufs(src)
    g = max(-20.0, min(12.0, -18.0 - in_i))
    cue_wav = f"{tmp_dir}/sc_finale.wav"
    subprocess.run([
        "ffmpeg", "-y", "-ss", "4.0", "-i", src,
        "-af", f"atrim=0:{dur:.4f},asetpts=PTS-STARTPTS,volume={g:.2f}dB,afade=t=in:st=0:d=1.2,afade=t=out:st={max(0.2, dur - 1.2):.3f}:d=1.2,aresample=48000",
        "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", cue_wav,
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    d_ms = int(round(t_start * 1000))
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", "-t", f"{total_dur:.6f}", "-i", "anullsrc=r=48000:cl=stereo", "-i", cue_wav,
        "-filter_complex", f"[0:a]aresample=48000[b];[1:a]adelay={d_ms}|{d_ms},apad=whole_dur={total_dur:.6f},atrim=0:{total_dur:.6f}[m];[b][m]amix=inputs=2:normalize=0:duration=first[aout]",
        "-map", "[aout]", "-t", f"{total_dur:.6f}", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", out_wav,
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return (t_start, total_dur)


def build_foley(shot_timing, total_dur, out_wav, audio_dir):
    cues = [
        (2,  lambda s, d: s + 0.05,               f"{audio_dir}/sfx_gf2_stomach_groan.mp3",    -10.0, 2.5),
        (2,  lambda s, d: s + 2.10,               f"{audio_dir}/sfx_gf2_glass_clink.mp3",      -16.5, 1.2),
        (5,  lambda s, d: s + max(0.0, d - 0.85), f"{audio_dir}/sfx_gf2_glass_clink.mp3",      -14.5, 1.2),
        (7,  lambda s, d: s + max(0.0, d - 1.50), f"{audio_dir}/sfx_gf2_stomach_groan.mp3",    -12.5, 1.6),
        (16, lambda s, d: s + 0.00,               f"{audio_dir}/sfx_gf2_stomach_groan.mp3",    -11.5, 1.8),
        (19, lambda s, d: s + 0.00,               f"{audio_dir}/sfx_gf2_diarrhea_torrent.mp3",  -4.0, 3.6),
        (23, lambda s, d: s + max(0.0, d - 0.90), f"{audio_dir}/sfx_gf2_glass_clink.mp3",      -14.5, 1.4),
    ]
    return place_sfx_cues(cues, shot_timing, total_dur, out_wav, "GF2")


if __name__ == "__main__":
    run_standard_assembly({
        "slug": "04_goodfellas_v2",
        "tag": "gf2",
        "clip_prefix": "gf2",
        "out_name": "04_goodfellas_1080p.mp4",
        "sfx_shots": [2, 19],
        "beat_holds": [4, 5, 16, 18, 24],
        "impact_shots": [19],
        "start_trims": {"GF2_20": 0.16},
        "audio_offsets": {"GF2_04": 0.042, "GF2_13": 0.042},
        "fx_durations": {2: 3.30, 19: 3.70},
        "grade_filter": "eq=contrast=1.02:saturation=1.02",
        "sidechain_ratio": 1.9,
        "build_ambience": build_ambience,
        "build_score": build_score,
        "build_foley": build_foley,
    })
