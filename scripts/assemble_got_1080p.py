import os
import subprocess

GOT_DIR = os.path.expanduser("~/.gemini/antigravity/scratch/game-of-thrones-damon")
OUT_DIR = os.path.expanduser("~/.gemini/antigravity/scratch/nomad-cinema-parodies/films")
os.makedirs(OUT_DIR, exist_ok=True)
WORK = "/tmp/got_edit"
os.makedirs(WORK, exist_ok=True)

# Trim each shot to tight HBO pacing:
# Shot 1: 0.0 -> 6.8s (corridor walk)
# Shot 2: 0.0 -> 7.4s (confession, trims 0.6s tail glitch)
# Shot 3: 0.3 -> 6.8s (Iron Toilet reveal push-in)
# Shot 4: 0.8 -> 7.6s (cataclysm + final whisper)
trims = [
    (f"{GOT_DIR}/clips/got_shot1_corridor.mp4", 0.0, 6.8, f"{WORK}/s1.mp4"),
    (f"{GOT_DIR}/clips/got_shot2_confession.mp4", 0.0, 7.4, f"{WORK}/s2.mp4"),
    (f"{GOT_DIR}/clips/got_shot3_throne_reveal.mp4", 0.3, 6.5, f"{WORK}/s3.mp4"),
    (f"{GOT_DIR}/clips/got_shot4_cataclysm.mp4", 2.6, 5.2, f"{WORK}/s4.mp4"),
]

# Westeros 1080p film grade: lanczos 1920x1080, slight desaturation (0.82), lifted blacks/contrast, cool shadows, subtle 35mm grain
vf_grade = (
    "scale=1920:1080:flags=lanczos,"
    "eq=saturation=0.82:contrast=1.06:brightness=-0.02,"
    "colorbalance=bs=0.05:gs=0.01:rs=-0.03:rh=0.02,"
    "noise=alls=4:allf=t+u,"
    "format=yuv420p"
)

for src, ss, dur, dst in trims:
    subprocess.run(
        [
            "ffmpeg", "-y", "-ss", str(ss), "-t", str(dur), "-i", src,
            "-vf", vf_grade, "-r", "24",
            "-c:v", "libx264", "-preset", "medium", "-crf", "17",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            dst,
        ],
        check=True,
    )

concat_txt = f"{WORK}/concat.txt"
with open(concat_txt, "w") as f:
    for _, _, _, dst in trims:
        f.write(f"file '{dst}'\n")

raw_video = f"{WORK}/got_video_raw.mp4"
subprocess.run(
    ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_txt, "-c", "copy", raw_video],
    check=True,
)

# Audio mix:
# - Original clip audio (boots, shot2 ElevenLabs dialogue, shot3 strings) with Shot 4 dialogue muted after 3.2s
# - Continuous ElevenLabs orchestral tension score (score_got_tension.mp3, looped/trimmed to 27.5s) at -16dB
# - Shot 3 door/rumble SFX at 13.8s
# - Shot 4 eruption SFX at 20.5s
# - Shot 4 crisp ElevenLabs Damon final whisper at 23.6s ("Winter is coming... and so is round two.")
final_mp4 = f"{OUT_DIR}/00_game_of_thrones_1080p.mp4"
filter_complex = (
    "[0:a]volume='if(gt(t,20.7),0.0,1.0)':eval=frame[clip_a];"
    "[1:a]aloop=loop=1:size=1056000,atrim=0:25.9,afade=t=in:st=0:d=1.0,afade=t=out:st=23.9:d=2.0,volume=0.35[score];"
    "[2:a]atrim=0:5.5,adelay=13800|13800,volume=0.45[sfx_door];"
    "[3:a]atrim=0:5.0,adelay=20200|20200,volume=0.70[sfx_erupt];"
    "[4:a]adelay=21700|21700,volume=1.20[vo4];"
    "[clip_a][score][sfx_door][sfx_erupt][vo4]amix=inputs=5:duration=first:normalize=0,"
    "loudnorm=I=-14:TP=-1.5:LRA=11[aout]"
)

subprocess.run(
    [
        "ffmpeg", "-y",
        "-i", raw_video,
        "-i", f"{GOT_DIR}/audio/score_got_tension.mp3",
        "-i", f"{GOT_DIR}/audio/sfx_doors_rumble.mp3",
        "-i", f"{GOT_DIR}/audio/sfx_eruption.mp3",
        "-i", f"{GOT_DIR}/audio/damon_shot4.mp3",
        "-filter_complex", filter_complex,
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-movflags", "+faststart",
        final_mp4,
    ],
    check=True,
)
print("BUILT:", final_mp4, os.path.getsize(final_mp4))
