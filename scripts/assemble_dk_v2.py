"""Assemble the 40-shot 1080p Scope master for Dark Knight v2."""
import json
import os
import sys

BASE = "/Users/jack/.gemini/antigravity/scratch/nomad-cinema-parodies"
sys.path.insert(0, f"{BASE}/scripts")
from studio_pipeline import assemble_film

SCRIPT = json.load(open(f"{BASE}/scripts/02_dark_knight_v2_script.json"))["shots"]
CLIPS_DIR = f"{BASE}/clips/02_dark_knight_v2"
AUDIO_DIR = f"{BASE}/audio/02_dark_knight_v2"

specs = []
for sh in SCRIPT:
    sid = sh["shot_id"]
    n = int(sid.split("_")[1])
    clip_p = f"{CLIPS_DIR}/dk2_{sid}_00001_.mp4"
    vo_p = f"{AUDIO_DIR}/{sid}.mp3"
    sp = {
        "clip": clip_p,
        "vo": vo_p,
        "max_tail": 0.20,
    }
    if n == 10:
        sp["sfx"] = f"{AUDIO_DIR}/sfx_light_slam.mp3"
        sp["sfx_vol"] = 0.55
    elif n == 27:
        sp["sfx"] = f"{AUDIO_DIR}/sfx_wall_slam.mp3"
        sp["sfx_vol"] = 0.55
    elif n == 35:
        sp["sfx"] = f"{AUDIO_DIR}/sfx_door_clank.mp3"
        sp["sfx_vol"] = 0.55
    elif sh["act"] == 1:
        sp["sfx"] = f"{AUDIO_DIR}/sfx_fluorescent_buzz.mp3"
        sp["sfx_vol"] = 0.14
    elif n in (12, 15, 20, 25, 30, 36):
        sp["sfx"] = f"{AUDIO_DIR}/sfx_fluorescent_buzz.mp3"
        sp["sfx_vol"] = 0.10
    specs.append(sp)

assemble_film(
    "02_dark_knight_v2",
    "dark_knight_v2",
    specs,
    f"{BASE}/audio/02_dark_knight/score_dk_tension.mp3",
    f"{BASE}/films/02_dark_knight_1080p.mp4",
    score_vol=0.19,
    maxrate="2650k",
)
