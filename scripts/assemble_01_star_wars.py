import os
import sys

sys.path.insert(0, "/Users/jack/.gemini/antigravity/scratch/nomad-cinema-parodies/scripts")
import studio_pipeline

BASE = "/Users/jack/.gemini/antigravity/scratch/nomad-cinema-parodies"

specs = [
    {
        "clip": f"{BASE}/clips/01_star_wars/sw_01_vader.mp4",
        "vo": f"{BASE}/audio/01_star_wars/vader_01.mp3",
        "sfx": f"{BASE}/audio/01_star_wars/sfx_vader_breath.mp3",
        "sfx_vol": 0.42,
        "max_tail": 0.28,
        "v_filter": "highpass=f=180,lowpass=f=3000,acompressor=threshold=-16dB:ratio=4",
    },
    {
        "clip": f"{BASE}/clips/01_star_wars/sw_02_damon.mp4",
        "vo": f"{BASE}/audio/01_star_wars/damon_02.mp3",
        "sfx": f"{BASE}/audio/01_star_wars/sfx_blaster_doors.mp3",
        "sfx_vol": 0.30,
        "sfx_delay": 4.2,
        "max_tail": 0.25,
    },
    {
        "clip": f"{BASE}/clips/01_star_wars/sw_03_gigi.mp4",
        "vo": f"{BASE}/audio/01_star_wars/gigi_03.mp3",
        "max_tail": 0.30,
        "max_dur": 9.10,
    },
    {
        "clip": f"{BASE}/clips/01_star_wars/sw_04_deron.mp4",
        "vo": f"{BASE}/audio/01_star_wars/deron_04.mp3",
        "max_tail": 0.35,
        "max_dur": 7.10,
    },
    {
        "clip": f"{BASE}/clips/01_star_wars/sw_05_zach.mp4",
        "vo": f"{BASE}/audio/01_star_wars/zach_05.mp3",
        "max_tail": 0.35,
    },
    {
        "clip": f"{BASE}/clips/01_star_wars/sw_06_hooman.mp4",
        "vo": f"{BASE}/audio/01_star_wars/hooman_07.mp3",
        "max_tail": 0.35,
    },
    {
        "clip": f"{BASE}/clips/01_star_wars/sw_07_ajay.mp4",
        "vo": f"{BASE}/audio/01_star_wars/ajay_09.mp3",
        "max_tail": 0.35,
    },
    {
        "clip": f"{BASE}/clips/01_star_wars/sw_08_sheren.mp4",
        "vo": f"{BASE}/audio/01_star_wars/sheren_12.mp3",
        "sfx": f"{BASE}/audio/01_star_wars/sfx_falcon_hyperdrive.mp3",
        "sfx_vol": 0.48,
        "sfx_delay": 2.0,
        "max_tail": 0.45,
    },
]

if __name__ == "__main__":
    studio_pipeline.assemble_film(
        film_slug="01_star_wars",
        look_key="star_wars",
        shot_specs=specs,
        score_path=f"{BASE}/audio/01_star_wars/score_sw_imperial.mp3",
        out_mp4=f"{BASE}/films/01_star_wars_1080p.mp4",
        score_vol=0.22,
    )
