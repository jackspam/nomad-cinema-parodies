"""Generate Two-Act Hans Zimmer style Dark Knight scores and full beat SFX stems."""
import os
import sys

BASE = "/Users/jack/.gemini/antigravity/scratch/nomad-cinema-parodies"
sys.path.insert(0, BASE)
from studio_audio import gen_sfx, load_key

key = load_key()
OUT = f"{BASE}/audio/02_dark_knight_v2"

SPECS = [
    (
        f"{OUT}/score_dk_act1_dark.mp3",
        "Continuous brooding Hans Zimmer Dark Knight interrogation-room tension underscore — deep bowed cello pulse, dark cinematic low brass swell, tense suspenseful rhythmic heartbeat, steady moody underscore throughout",
        22.0,
        0.45,
    ),
    (
        f"{OUT}/score_dk_act2_intense.mp3",
        "Continuous escalating Hans Zimmer Dark Knight thriller underscore — driving intense low string ostinato, dark brooding bass pulses, ominous rising suspense strings, relentless cinematic tension throughout",
        22.0,
        0.45,
    ),
    (
        f"{OUT}/sfx_door_heavy_enter.mp3",
        "Heavy riveted steel prison interrogation door clanking open, deliberate hard footsteps on concrete floor, heavy steel door shutting with sharp metallic latch",
        4.0,
        0.45,
    ),
    (
        f"{OUT}/sfx_handcuffs_unlock.mp3",
        "Metal police handcuffs unlocking with sharp key click and heavy steel chain clattering onto a hollow metal table",
        3.0,
        0.45,
    ),
    (
        f"{OUT}/sfx_door_exit_switch.mp3",
        "Heavy steel interrogation door latch clanking shut followed by a loud industrial electrical circuit breaker switch snapping on",
        4.0,
        0.45,
    ),
    (
        f"{OUT}/sfx_light_slam_v2.mp3",
        "Loud industrial fluorescent overhead prison lights snapping on with sharp electrical relay crack and stark electric buzz surge",
        4.0,
        0.50,
    ),
    (
        f"{OUT}/sfx_table_slam.mp3",
        "Heavy violent body and palm slam onto a hollow steel interrogation table with loud metallic thud and reverberation",
        3.0,
        0.50,
    ),
    (
        f"{OUT}/sfx_collar_scuffle.mp3",
        "Tense leather combat gloves grabbing wool jacket collar and pinning fabric firmly against a concrete cinderblock wall",
        3.0,
        0.45,
    ),
    (
        f"{OUT}/sfx_table_crash.mp3",
        "Heavy body thrown sideways across a metal interrogation table with loud hollow steel scrape, impact thud, and clatter",
        3.5,
        0.50,
    ),
    (
        f"{OUT}/sfx_batman_exit.mp3",
        "Heavy tactical combat boots striding decisively across concrete floor with leather cape rustle into hallway",
        4.0,
        0.45,
    ),
]

for path, prompt, dur, inf in SPECS:
    print(f"Generating {os.path.basename(path)} ({dur}s)...", flush=True)
    gen_sfx(prompt, dur, path, key, inf)

print("ALL_DK2_SFX_AND_SCORES_GENERATED")
