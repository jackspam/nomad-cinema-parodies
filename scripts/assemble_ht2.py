"""Assemble Heat — Thirty Seconds Flat (08_heat_1080p.mp4) with continuous two-act Lyria score, diner ambience & foley."""
import subprocess
from v27_assemble_common import measure_lufs, place_sfx_cues, run_standard_assembly


def build_ambience(shot_timing, total_dur, out_wav, tmp_dir, audio_dir):
    src = f"{audio_dir}/sfx_ht2_diner_ambience.mp3"
    in_i = measure_lufs(src)
    g = max(-24.0, min(32.0, -35.0 - in_i))
    fade_st = max(0.5, total_dur - 1.2)
    subprocess.run([
        "ffmpeg", "-y", "-stream_loop", "-1", "-t", f"{total_dur + 0.5:.4f}", "-i", src,
        "-af", f"aresample=48000,highpass=f=45,lowpass=f=2400,volume={g:.2f}dB,alimiter=limit=-14dB:level=disabled,atrim=0:{total_dur:.6f},afade=t=in:st=0:d=0.5,afade=t=out:st={fade_st:.3f}:d=1.2",
        "-t", f"{total_dur:.6f}", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", out_wav,
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def build_score(shot_timing, total_dur, out_wav, tmp_dir, audio_dir):
    # Continuous 0.0s -> end score: Act 1 noir synthesizer pulse crossfades cleanly at HT2_08 into Act 2 escalating thriller pulse.
    t_act2 = shot_timing[8][0]
    d_fade = 3.0
    a1_end = 2.0 + t_act2 + d_fade * 0.5
    act2_need = max(6.0, total_dur - t_act2 + d_fade * 0.5 + 1.0)
    src1 = f"{audio_dir}/score_ht2_act1_noir.mp3"
    src2 = f"{audio_dir}/score_ht2_act2_tension.mp3"

    g1 = max(-20.0, min(12.0, -20.0 - measure_lufs(src1)))
    g2 = max(-20.0, min(12.0, -20.0 - measure_lufs(src2)))
    t18_s, t18_d = shot_timing[18][0], shot_timing[18][1]
    vol_expr = f"if(between(t,{t18_s:.2f},{t18_s + t18_d:.2f}),0.42,1.0)"
    fade_out_st = max(0.5, total_dur - 1.8)

    subprocess.run([
        "ffmpeg", "-y", "-i", src1, "-i", src2,
        "-filter_complex", (
            f"[0:a]atrim=start=2.0:end={a1_end:.4f},asetpts=PTS-STARTPTS,volume={g1:.2f}dB,aresample=48000[s1];"
            f"[1:a]atrim=start=2.0:end={2.0 + act2_need:.4f},asetpts=PTS-STARTPTS,volume={g2:.2f}dB,aresample=48000[s2];"
            f"[s1][s2]acrossfade=d={d_fade:.2f}:c1=tri:c2=tri,atrim=0:{total_dur:.6f},asetpts=PTS-STARTPTS,"
            f"volume='{vol_expr}':eval=frame,afade=t=in:st=0:d=0.6,afade=t=out:st={fade_out_st:.3f}:d=1.8[aout]"
        ),
        "-map", "[aout]", "-t", f"{total_dur:.6f}", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", out_wav,
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return (0.0, total_dur)


def build_foley(shot_timing, total_dur, out_wav, audio_dir):
    cues = [
        (17, lambda s, d: s + 0.25, f"{audio_dir}/sfx_ht2_gut_rumble.mp3",      -10.5, 2.60),
        (18, lambda s, d: s + 0.35, f"{audio_dir}/sfx_ht2_diarrhea_blast.mp3",  -4.8,  3.25),
    ]
    return place_sfx_cues(cues, shot_timing, total_dur, out_wav, "HT2")


if __name__ == "__main__":
    run_standard_assembly({
        "slug": "08_heat_v2",
        "tag": "ht2",
        "clip_prefix": "ht2",
        "out_name": "08_heat_1080p.mp4",
        "sfx_shots": [1, 18],
        "beat_holds": [7, 13, 17, 20],
        "impact_shots": [18],
        "start_trims": {},
        "fx_durations": {1: 3.40, 18: 3.60},
        "grade_filter": "eq=contrast=1.04:saturation=0.96:brightness=-0.01",
        "sidechain_ratio": 1.8,
        "build_ambience": build_ambience,
        "build_score": build_score,
        "build_foley": build_foley,
    })
