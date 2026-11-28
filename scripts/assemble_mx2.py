"""Assemble The Matrix v2 (07_matrix_1080p.mp4) with gothic storm rain, thunder, pill-case foley & Don Davis OST."""
import subprocess
from v27_assemble_common import measure_lufs, place_sfx_cues, run_standard_assembly


def build_ambience(shot_timing, total_dur, out_wav, tmp_dir, audio_dir):
    src = f"{audio_dir}/sfx_mx2_rain_clean.wav"
    in_i = measure_lufs(src)
    g = max(-24.0, min(38.0, -32.0 - in_i))
    fade_st = max(0.5, total_dur - 1.0)
    subprocess.run([
        "ffmpeg", "-y", "-stream_loop", "-1", "-t", f"{total_dur + 0.5:.4f}", "-i", src,
        "-af", f"aresample=48000,highpass=f=45,lowpass=f=2800,volume={g:.2f}dB,alimiter=limit=-14dB:level=disabled,atrim=0:{total_dur:.6f},afade=t=in:st=0:d=0.4,afade=t=out:st={fade_st:.3f}:d=1.0",
        "-t", f"{total_dur:.6f}", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", out_wav,
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def build_score(shot_timing, total_dur, out_wav, tmp_dir, audio_dir):
    # Wachowski/Don Davis spotting: gothic rain dry banter Acts 1-2 -> "Unable to Speak" OST blooms right on Dual Pill reveal (MX2_12..24)
    t_start = shot_timing[12][0]
    dur = max(2.0, total_dur - t_start)
    src = f"{audio_dir}/score_mx2_don_davis_tension.mp3"
    in_i = measure_lufs(src)
    g = max(-20.0, min(12.0, -18.5 - in_i))
    t20_s, t20_d = shot_timing[20][0] - t_start, shot_timing[20][1]
    vol_expr = f"if(between(t,{t20_s:.2f},{t20_s + t20_d:.2f}),0.40,1.0)"
    cue_wav = f"{tmp_dir}/sc_pills.wav"
    af_tail = (
        f"[a][b]acrossfade=d=3.0:c1=tri:c2=tri,atrim=0:{dur:.4f},asetpts=PTS-STARTPTS,"
        f"volume={g:.2f}dB,volume='{vol_expr}':eval=frame,"
        f"afade=t=in:st=0:d=1.2,afade=t=out:st={max(0.2, dur - 1.5):.3f}:d=1.5,aresample=48000[sc]"
    )
    subprocess.run([
        "ffmpeg", "-y", "-i", src,
        "-filter_complex", (
            f"[0:a]atrim=start=4.0:end=67.5,asetpts=PTS-STARTPTS[a];"
            f"[0:a]atrim=start=26.0:end=67.5,asetpts=PTS-STARTPTS[b];"
            f"{af_tail}"
        ),
        "-map", "[sc]", "-t", f"{dur:.4f}", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", cue_wav,
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
        (1,  lambda s, d: s + 0.10, f"{audio_dir}/sfx_mx2_thunder_crack.mp3",    -8.5, 3.3),
        (3,  lambda s, d: s + 2.00, f"{audio_dir}/sfx_mx2_phone_tap.mp3",       -16.5, 1.6),
        (12, lambda s, d: s + 0.35, f"{audio_dir}/sfx_mx2_thunder_crack.mp3",   -13.5, 2.8),
        (19, lambda s, d: s + 1.10, f"{audio_dir}/sfx_mx2_thunder_crack.mp3",   -12.5, 2.2),
        (20, lambda s, d: s + 4.25, f"{audio_dir}/sfx_mx2_diarrhea_torrent.mp3", -4.0, 3.00),
        (20, lambda s, d: s + 4.20, f"{audio_dir}/sfx_mx2_thunder_crack.mp3",    -9.0, 3.05),
    ]
    return place_sfx_cues(cues, shot_timing, total_dur, out_wav, "MX2")


if __name__ == "__main__":
    run_standard_assembly({
        "slug": "07_matrix_v2",
        "tag": "mx2",
        "clip_prefix": "mx2",
        "out_name": "07_matrix_1080p.mp4",
        "sfx_shots": [1, 19, 20],
        "beat_holds": [12, 17, 18, 22, 24],
        "impact_shots": [],
        "start_trims": {},
        "fx_durations": {1: 3.40, 19: 3.30, 20: 7.25},
        "grade_filter": "eq=contrast=1.03:saturation=1.01",
        "sidechain_ratio": 1.8,
        "build_ambience": build_ambience,
        "build_score": build_score,
        "build_foley": build_foley,
    })
