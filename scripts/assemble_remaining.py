import os
import sys

BASE = "/Users/jack/.gemini/antigravity/scratch/nomad-cinema-parodies"
sys.path.insert(0, os.path.join(BASE, "scripts"))
from studio_pipeline import assemble_film

crt_eq = "highpass=f=320,lowpass=f=2400"

# 1. 04. Goodfellas (20 shots)
gf_specs = []
for i in range(1, 21):
    clip = f"{BASE}/clips/04_goodfellas/ltx25_gf_gf_{i:02d}.mp4"
    vo = f"{BASE}/audio/04_goodfellas/GF_{i:02d}{'_clean' if i in (19, 20) else ''}.mp3"
    sp = {
        "clip": clip,
        "vo": vo,
        "sfx": f"{BASE}/audio/04_goodfellas/sfx_copa_ambience.mp3",
        "sfx_vol": 0.14,
        "max_tail": 0.25,
    }
    if i == 19:
        sp["max_dur"] = 8.65
    elif i == 20:
        sp["max_dur"] = 7.95
    gf_specs.append(sp)

assemble_film(
    "04_goodfellas",
    "goodfellas",
    gf_specs,
    f"{BASE}/audio/04_goodfellas/score_gf_club.mp3",
    f"{BASE}/films/04_goodfellas_1080p.mp4",
    score_vol=0.20,
)

# 2. 05. Pulp Fiction (21 shots)
pf_specs = []
for i in range(1, 22):
    clip = f"{BASE}/clips/05_pulp_fiction/ltx25_pf_pf_{i:02d}.mp4"
    clean = "_clean" if i in (2, 20) else ""
    vo = f"{BASE}/audio/05_pulp_fiction/PF_{i:02d}{clean}.mp3"
    sp = {"clip": clip, "vo": vo, "max_tail": 0.25}
    if i == 2:
        sp["max_dur"] = 7.50
    elif i == 20:
        sp["max_dur"] = 6.30
        sp["v_filter"] = crt_eq
    pf_specs.append(sp)

assemble_film(
    "05_pulp_fiction",
    "pulp_fiction",
    pf_specs,
    f"{BASE}/audio/05_pulp_fiction/score_pf_surf_full.mp3",
    f"{BASE}/films/05_pulp_fiction_1080p.mp4",
    score_vol=0.18,
)

# 3. 07. The Matrix (20 shots, upgraded with storm rain Foley)
mx_specs = []
for i in range(1, 21):
    clip = f"{BASE}/clips/07_matrix/ltx25_mx_mx_{i:02d}.mp4"
    vo = f"{BASE}/audio/07_matrix/MX_{i:02d}.mp3"
    sp = {
        "clip": clip,
        "vo": vo,
        "sfx": f"{BASE}/audio/07_matrix/sfx_mx_storm.mp3",
        "sfx_vol": 0.16,
        "max_tail": 0.25,
    }
    if i in (11, 13, 19):
        sp["v_filter"] = crt_eq
    mx_specs.append(sp)

assemble_film(
    "07_matrix",
    "matrix",
    mx_specs,
    f"{BASE}/audio/07_matrix/score_mx_drone.mp3",
    f"{BASE}/films/07_matrix_1080p.mp4",
    score_vol=0.22,
)

# 4. 06. Jurassic Park (18 shots)
jp_nums = [1, 2, 3, 4, 5, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
jp_specs = []
for i in jp_nums:
    clip = f"{BASE}/clips/06_jurassic_park/ltx25_jp_jp_{i:02d}.mp4"
    vo = f"{BASE}/audio/06_jurassic_park/JP_{i:02d}.mp3"
    sp = {"clip": clip, "vo": vo, "max_tail": 0.25}
    if i == 1:
        sp["sfx"] = f"{BASE}/audio/06_jurassic_park/sfx_trex_thump.mp3"
        sp["sfx_vol"] = 0.45
    elif i in (7, 12, 16, 20):
        sp["sfx"] = f"{BASE}/audio/06_jurassic_park/sfx_trex_roar.mp3"
        sp["sfx_vol"] = 0.48
        sp["sfx_delay"] = 0.35 if i == 7 else 1.2
    elif i in (15, 19):
        sp["sfx"] = f"{BASE}/audio/06_jurassic_park/sfx_car_horn_rain.mp3"
        sp["sfx_vol"] = 0.38
    jp_specs.append(sp)

assemble_film(
    "06_jurassic_park",
    "jurassic_park",
    jp_specs,
    f"{BASE}/audio/06_jurassic_park/score_jp_rain_full.mp3",
    f"{BASE}/films/06_jurassic_park_1080p.mp4",
    score_vol=0.24,
)
print("ALL_FOUR_REMAINING_FILMS_ASSEMBLED")
