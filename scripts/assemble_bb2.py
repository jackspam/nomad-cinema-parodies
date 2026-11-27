"""Assemble Breaking Bad v2 (03_breaking_bad_1080p.mp4) with authentic desert foley & Act 3 minimalist tension score."""
import subprocess
from v27_assemble_common import measure_lufs, place_sfx_cues, run_standard_assembly


def build_ambience(shot_timing, total_dur, out_wav, tmp_dir, audio_dir):
    src = f"{audio_dir}/sfx_bb2_desert_clean.wav"
    in_i = measure_lufs(src)
    g = max(-24.0, min(12.0, -34.0 - in_i))
    fade_st = max(0.5, total_dur - 1.0)
    subprocess.run([
        "ffmpeg", "-y", "-stream_loop", "-1", "-t", f"{total_dur + 0.5:.4f}", "-i", src,
        "-af", f"aresample=48000,highpass=f=45,lowpass=f=240,volume={g:.2f}dB,atrim=0:{total_dur:.6f},afade=t=in:st=0:d=0.4,afade=t=out:st={fade_st:.3f}:d=1.0",
        "-t", f"{total_dur:.6f}", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", out_wav,
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def build_score(shot_timing, total_dur, out_wav, tmp_dir, audio_dir):
    # Gilligan spotting: ZERO music Acts 1-2 (BB2_01..20); sparse desert dobro tension creeps in Act 3 (BB2_21..25)
    t_start = shot_timing[21][0]
    dur = max(2.0, total_dur - t_start)
    src = f"{audio_dir}/score_bb2_minimal_tension.mp3"
    in_i = measure_lufs(src)
    g = max(-20.0, min(12.0, -18.5 - in_i))
    cue_wav = f"{tmp_dir}/sc_act3.wav"
    subprocess.run([
        "ffmpeg", "-y", "-ss", "2.0", "-i", src,
        "-af", f"atrim=0:{dur:.4f},asetpts=PTS-STARTPTS,volume={g:.2f}dB,afade=t=in:st=0:d=1.8,afade=t=out:st={max(0.2, dur - 1.4):.3f}:d=1.4,aresample=48000",
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
        (1,  lambda s, d: s + 0.15,               f"{audio_dir}/sfx_bb2_gravel_steps.mp3", -15.0, 2.5),
        (4,  lambda s, d: s + 0.25,               f"{audio_dir}/sfx_bb2_bag_rustle.mp3",   -16.0, 1.8),
        (6,  lambda s, d: s + max(0.0, d - 1.50), f"{audio_dir}/sfx_stomach_groan.mp3",    -12.5, 1.6),
        (7,  lambda s, d: s + 0.20,               f"{audio_dir}/sfx_bb2_cone_tap.mp3",     -15.0, 1.4),
        (12, lambda s, d: s + 0.10,               f"{audio_dir}/sfx_stomach_groan.mp3",    -11.5, 1.8),
        (15, lambda s, d: s + max(0.0, d - 1.40), f"{audio_dir}/sfx_stomach_groan.mp3",    -10.5, 1.8),
        (17, lambda s, d: s + 0.00,               f"{audio_dir}/sfx_diarrhea_torrent.mp3",  -4.0, 3.6),
    ]
    return place_sfx_cues(cues, shot_timing, total_dur, out_wav, "BB2")


if __name__ == "__main__":
    run_standard_assembly({
        "slug": "03_breaking_bad_v2",
        "tag": "bb2",
        "clip_prefix": "bb2",
        "out_name": "03_breaking_bad_1080p.mp4",
        "sfx_shots": [1, 17],
        "beat_holds": [16, 23, 25],
        "impact_shots": [17],
        "fx_durations": {1: 3.30, 17: 3.70},
        "grade_filter": "eq=contrast=1.02:saturation=1.02",
        "sidechain_ratio": 1.9,
        "build_ambience": build_ambience,
        "build_score": build_score,
        "build_foley": build_foley,
    })
