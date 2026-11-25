import os
import shutil
import sys

BASE = "/Users/jack/.gemini/antigravity/scratch/nomad-cinema-parodies"
sys.path.insert(0, os.path.join(BASE, "scripts"))
from studio_pipeline import assemble_film

# Refresh maniacal Joker LTX-2.5 A/B benchmark clips
shutil.copy2(f"{BASE}/clips/02_dark_knight/ltx25_dk_dk_02.mp4", f"{BASE}/films/ltx25_bench/ltx25_dk_02.mp4")
shutil.copy2(f"{BASE}/clips/02_dark_knight/ltx25_dk_dk_04.mp4", f"{BASE}/films/ltx25_bench/ltx25_dk_04.mp4")

dk_specs = [
    {"clip": f"{BASE}/clips/02_dark_knight/dk_dk_01.mp4", "vo": f"{BASE}/audio/02_dark_knight/DK_01.mp3", "max_tail": 0.35},
    {"clip": f"{BASE}/clips/02_dark_knight/ltx25_dk_dk_02.mp4", "vo": f"{BASE}/audio/02_dark_knight/DK_02.mp3", "max_tail": 0.18},
    {"clip": f"{BASE}/clips/02_dark_knight/dk_dk_03.mp4", "vo": f"{BASE}/audio/02_dark_knight/DK_03.mp3", "max_tail": 0.30},
    {"clip": f"{BASE}/clips/02_dark_knight/ltx25_dk_dk_04.mp4", "vo": f"{BASE}/audio/02_dark_knight/DK_04.mp3", "max_dur": 8.15},
    {"clip": f"{BASE}/clips/02_dark_knight/dk_dk_05.mp4", "vo": f"{BASE}/audio/02_dark_knight/DK_05.mp3", "max_tail": 0.30},
    {"clip": f"{BASE}/clips/02_dark_knight/dk_dk_06.mp4", "vo": f"{BASE}/audio/02_dark_knight/DK_06.mp3", "max_tail": 0.30},
    {"clip": f"{BASE}/clips/02_dark_knight/dk_dk_07.mp4", "vo": f"{BASE}/audio/02_dark_knight/DK_07.mp3", "max_tail": 0.25},
    {"clip": f"{BASE}/clips/02_dark_knight/ltx25_dk_dk_08.mp4", "vo": f"{BASE}/audio/02_dark_knight/DK_08.mp3", "max_tail": 0.25},
    {"clip": f"{BASE}/clips/02_dark_knight/dk_dk_09.mp4", "vo": f"{BASE}/audio/02_dark_knight/DK_09.mp3", "max_tail": 0.25},
    {"clip": f"{BASE}/clips/02_dark_knight/dk_dk_10.mp4", "vo": f"{BASE}/audio/02_dark_knight/DK_10.mp3", "max_tail": 0.25},
    {"clip": f"{BASE}/clips/02_dark_knight/ltx25_dk_dk_11.mp4", "vo": f"{BASE}/audio/02_dark_knight/DK_11.mp3", "max_tail": 0.11},
    {"clip": f"{BASE}/clips/02_dark_knight/dk_dk_12.mp4", "vo": f"{BASE}/audio/02_dark_knight/DK_12.mp3", "max_tail": 0.25},
    {"clip": f"{BASE}/clips/02_dark_knight/dk_dk_13.mp4", "vo": f"{BASE}/audio/02_dark_knight/DK_13.mp3", "max_tail": 0.25, "v_filter": "highpass=f=320,lowpass=f=2400"},
    {"clip": f"{BASE}/clips/02_dark_knight/dk_dk_14.mp4", "vo": f"{BASE}/audio/02_dark_knight/DK_14.mp3", "max_tail": 0.25},
    {"clip": f"{BASE}/clips/02_dark_knight/dk_dk_15.mp4", "vo": f"{BASE}/audio/02_dark_knight/DK_15.mp3", "max_tail": 0.25, "v_filter": "highpass=f=320,lowpass=f=2400"},
    {"clip": f"{BASE}/clips/02_dark_knight/dk_dk_16.mp4", "vo": f"{BASE}/audio/02_dark_knight/DK_16.mp3", "max_tail": 0.25},
    {"clip": f"{BASE}/clips/02_dark_knight/ltx25_dk_dk_17.mp4", "vo": f"{BASE}/audio/02_dark_knight/DK_17.mp3", "max_tail": 0.24},
    {"clip": f"{BASE}/clips/02_dark_knight/dk_dk_18.mp4", "vo": f"{BASE}/audio/02_dark_knight/DK_18.mp3", "max_tail": 0.25},
    {"clip": f"{BASE}/clips/02_dark_knight/ltx25_dk_dk_19.mp4", "vo": f"{BASE}/audio/02_dark_knight/DK_19.mp3", "max_tail": 0.25},
    {"clip": f"{BASE}/clips/02_dark_knight/ltx25_dk_dk_20.mp4", "vo": f"{BASE}/audio/02_dark_knight/DK_20_clean.mp3", "max_dur": 6.75, "v_filter": "highpass=f=320,lowpass=f=2400"},
]

assemble_film(
    "02_dark_knight",
    "dark_knight",
    dk_specs,
    f"{BASE}/audio/02_dark_knight/score_dk_tension.mp3",
    f"{BASE}/films/02_dark_knight_1080p.mp4",
    score_vol=0.20,
)

bb_specs = [
    {"clip": f"{BASE}/clips/03_breaking_bad/ltx25_bb_bb_02.mp4", "vo": f"{BASE}/audio/03_breaking_bad/BB_02.mp3", "max_tail": 0.30},
    {"clip": f"{BASE}/clips/03_breaking_bad/bb_bb_03.mp4", "vo": f"{BASE}/audio/03_breaking_bad/BB_03.mp3", "max_tail": 0.25},
    {"clip": f"{BASE}/clips/03_breaking_bad/bb_bb_04.mp4", "vo": f"{BASE}/audio/03_breaking_bad/BB_04.mp3", "max_tail": 0.25},
    {"clip": f"{BASE}/clips/03_breaking_bad/bb_bb_05.mp4", "vo": f"{BASE}/audio/03_breaking_bad/BB_05.mp3", "max_tail": 0.25},
    {"clip": f"{BASE}/clips/03_breaking_bad/bb_bb_06.mp4", "vo": f"{BASE}/audio/03_breaking_bad/BB_06.mp3", "max_tail": 0.25},
    {"clip": f"{BASE}/clips/03_breaking_bad/bb_bb_07.mp4", "vo": f"{BASE}/audio/03_breaking_bad/BB_07.mp3", "max_tail": 0.25},
    {"clip": f"{BASE}/clips/03_breaking_bad/ltx25_bb_bb_08.mp4", "vo": f"{BASE}/audio/03_breaking_bad/BB_08.mp3", "max_tail": 0.22},
    {"clip": f"{BASE}/clips/03_breaking_bad/bb_bb_09.mp4", "vo": f"{BASE}/audio/03_breaking_bad/BB_09.mp3", "max_tail": 0.25},
    {"clip": f"{BASE}/clips/03_breaking_bad/bb_bb_10.mp4", "vo": f"{BASE}/audio/03_breaking_bad/BB_10.mp3", "max_tail": 0.25},
    {"clip": f"{BASE}/clips/03_breaking_bad/ltx25_bb_bb_11.mp4", "vo": f"{BASE}/audio/03_breaking_bad/BB_11.mp3", "max_tail": 0.17},
    {"clip": f"{BASE}/clips/03_breaking_bad/bb_bb_12.mp4", "vo": f"{BASE}/audio/03_breaking_bad/BB_12.mp3", "max_tail": 0.25},
    {"clip": f"{BASE}/clips/03_breaking_bad/bb_bb_13.mp4", "vo": f"{BASE}/audio/03_breaking_bad/BB_13.mp3", "max_tail": 0.25},
    {"clip": f"{BASE}/clips/03_breaking_bad/bb_bb_14.mp4", "vo": f"{BASE}/audio/03_breaking_bad/BB_14.mp3", "max_tail": 0.25},
    {"clip": f"{BASE}/clips/03_breaking_bad/bb_bb_15.mp4", "vo": f"{BASE}/audio/03_breaking_bad/BB_15.mp3", "max_tail": 0.25},
    {"clip": f"{BASE}/clips/03_breaking_bad/bb_bb_16.mp4", "vo": f"{BASE}/audio/03_breaking_bad/BB_16.mp3", "max_tail": 0.25},
    {"clip": f"{BASE}/clips/03_breaking_bad/bb_bb_17.mp4", "vo": f"{BASE}/audio/03_breaking_bad/BB_17.mp3", "max_tail": 0.25},
    {"clip": f"{BASE}/clips/03_breaking_bad/ltx25_bb_bb_18.mp4", "vo": f"{BASE}/audio/03_breaking_bad/BB_18.mp3", "max_tail": 0.16},
    {"clip": f"{BASE}/clips/03_breaking_bad/ltx25_bb_bb_19.mp4", "vo": f"{BASE}/audio/03_breaking_bad/BB_19.mp3", "max_tail": 0.22},
    {"clip": f"{BASE}/clips/03_breaking_bad/ltx25_bb_bb_20.mp4", "vo": f"{BASE}/audio/03_breaking_bad/BB_20_clean.mp3", "max_dur": 8.45},
    {"clip": f"{BASE}/clips/03_breaking_bad/bb_bb_21.mp4", "vo": f"{BASE}/audio/03_breaking_bad/BB_21.mp3", "max_tail": 0.25},
]

assemble_film(
    "03_breaking_bad",
    "breaking_bad",
    bb_specs,
    f"{BASE}/audio/03_breaking_bad/score_bb_desert.mp3",
    f"{BASE}/films/03_breaking_bad_1080p.mp4",
    score_vol=0.20,
)
