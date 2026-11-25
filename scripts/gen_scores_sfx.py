import os
import sys

BASE = "/Users/jack/.gemini/antigravity/scratch/nomad-cinema-parodies"
sys.path.insert(0, BASE)
from studio_audio import gen_sfx, load_key

key = load_key()
specs = [
    (
        f"{BASE}/audio/05_pulp_fiction/score_pf_surf_full.mp3",
        "Continuous tense 1994 Quentin Tarantino vintage Los Angeles surf-noir electric guitar and muted upright bass groove, steady brooding cinematic underscore throughout",
        22.0,
        0.35,
    ),
    (
        f"{BASE}/audio/06_jurassic_park/score_jp_rain_full.mp3",
        "Continuous heavy tropical midnight monsoon rain pouring on car roof and jungle leaves layered with low ominous orchestral suspense strings and deep brass swells",
        22.0,
        0.35,
    ),
    (
        f"{BASE}/audio/06_jurassic_park/sfx_trex_roar.mp3",
        "Earth-shaking 1993 giant tyrannosaurus rex dinosaur roar reverberating through torrential storm rain and snapping electric fence cables",
        5.0,
        0.4,
    ),
    (
        f"{BASE}/audio/06_jurassic_park/sfx_trex_thump.mp3",
        "Deep seismic dinosaur footstep thuds shaking plastic water cups inside a parked car during heavy rain",
        5.0,
        0.4,
    ),
    (
        f"{BASE}/audio/06_jurassic_park/sfx_car_horn_rain.mp3",
        "Impatient double car horn honk and tires spinning on wet muddy gravel in pouring rain",
        4.0,
        0.4,
    ),
    (
        f"{BASE}/audio/04_goodfellas/sfx_copa_ambience.mp3",
        "Lively 1970s New York Copacabana supper-club ambience, clinking cocktail glasses, soft warm dinner crowd murmur",
        15.0,
        0.3,
    ),
    (
        f"{BASE}/audio/07_matrix/sfx_mx_storm.mp3",
        "Steady heavy rain pelting old hotel window glass with distant rolling thunder and subtle low electrical hum",
        15.0,
        0.3,
    ),
    (
        f"{BASE}/audio/05_pulp_fiction/sfx_pf_apartment.mp3",
        "Quiet 1990s Los Angeles morning apartment room tone with faint distant traffic, buzzing fridge, and subtle wooden floor creak",
        15.0,
        0.3,
    ),
]

for path, prompt, dur, inf in specs:
    print(f"Generating {os.path.basename(path)} ({dur}s)...")
    gen_sfx(prompt, dur, path, key, inf)
print("ALL_SCORES_AND_SFX_DONE")
