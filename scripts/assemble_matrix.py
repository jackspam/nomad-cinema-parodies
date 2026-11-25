import os
import subprocess
import sys

BASE = "/Users/jack/.gemini/antigravity/scratch/nomad-cinema-parodies"
sys.path.insert(0, os.path.join(BASE, "scripts"))
from studio_pipeline import assemble_film

crt_eq = "highpass=f=320,lowpass=f=2400"
specs = []
for i in range(1, 21):
    clip = f"{BASE}/clips/07_matrix/ltx25_mx_mx_{i:02d}.mp4"
    vo = f"{BASE}/audio/07_matrix/MX_{i:02d}.mp3"
    sp = {"clip": clip, "vo": vo, "max_tail": 0.25}
    if i in (11, 13, 19):
        sp["v_filter"] = crt_eq
    specs.append(sp)

assemble_film(
    "07_matrix",
    "matrix",
    specs,
    f"{BASE}/audio/07_matrix/score_mx_drone.mp3",
    f"{BASE}/films/07_matrix_1080p.mp4",
    score_vol=0.22,
)
