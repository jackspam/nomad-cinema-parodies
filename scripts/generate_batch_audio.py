import json
import os
import sys

sys.path.insert(0, "/Users/jack/.gemini/antigravity/scratch/nomad-cinema-parodies")
import studio_audio

SPEAKER_MAP = {
    "Damon": "damon",
    "Zach": "zach",
    "Sheren": "sheren",
    "Gigi": "gigi",
    "Deron": "deron",
    "Hooman": "hooman",
    "Ajay": "ajay",
    "The Joker": "joker",
    "Walter White": "walter",
    "Gus Fring": "gus",
    "Tommy DeVito": "tommy",
    "Henry Hill": "trooper",
    "Jules Winnfield": "jules",
    "Vincent Vega": "trooper",
    "Morpheus": "morpheus",
}

FILMS = [
    ("05_pulp_fiction_script.json", "05_pulp_fiction", "score_pf_surf.mp3",
     "1990s Tarantino surf rock twangy reverb electric guitar and dry vinyl apartment tension pulse, instrumental only, no vocals", 12.0),
    ("06_jurassic_park_script.json", "06_jurassic_park", "score_jp_rain.mp3",
     "1993 blockbuster orchestral suspense low French horns and trembling cello over heavy tropical rainstorm thunder, instrumental only", 12.0),
    ("07_matrix_script.json", "07_matrix", "score_mx_drone.mp3",
     "1999 cyberpunk sci-fi thriller low ominous analog synth drone with distant rain and tense industrial pulse, instrumental only", 12.0),
]

UPGRADE_FILMS = [
    ("02_dark_knight_script.json", "02_dark_knight", {"The Joker"}),
    ("03_breaking_bad_script.json", "03_breaking_bad", {"Walter White", "Gus Fring"}),
    ("04_goodfellas_script.json", "04_goodfellas", {"Tommy DeVito", "Henry Hill"}),
]

def main():
    key = studio_audio.load_key()
    base = "/Users/jack/.gemini/antigravity/scratch/nomad-cinema-parodies"

    # 1. Upgrade iconic character voices on 02, 03, 04
    for script_name, folder, target_speakers in UPGRADE_FILMS:
        data = json.load(open(os.path.join(base, "scripts", script_name)))
        out_dir = os.path.join(base, "audio", folder)
        os.makedirs(out_dir, exist_ok=True)
        for shot in data.get("shots", []):
            spk = shot.get("speaker")
            if spk in target_speakers:
                out_p = os.path.join(out_dir, f"{shot['shot_id']}.mp3")
                txt = shot.get("tts_text") or shot.get("exact_dialogue") or ""
                if txt.strip():
                    print(f"[UPGRADE] {folder}/{shot['shot_id']}.mp3 -> {spk} ({SPEAKER_MAP[spk]})")
                    studio_audio.gen_tts(SPEAKER_MAP[spk], txt, out_p, key)

    # 2. Generate all VO + score for 05, 06, 07
    for script_name, folder, score_name, score_prompt, score_dur in FILMS:
        data = json.load(open(os.path.join(base, "scripts", script_name)))
        out_dir = os.path.join(base, "audio", folder)
        os.makedirs(out_dir, exist_ok=True)
        for shot in data.get("shots", []):
            spk = shot.get("speaker")
            out_p = os.path.join(out_dir, f"{shot['shot_id']}.mp3")
            txt = shot.get("tts_text") or shot.get("exact_dialogue") or ""
            if spk and txt.strip() and not os.path.exists(out_p):
                vkey = SPEAKER_MAP.get(spk, "villain")
                print(f"[TTS] {folder}/{shot['shot_id']}.mp3 -> {spk} ({vkey})")
                studio_audio.gen_tts(vkey, txt, out_p, key)
        score_p = os.path.join(out_dir, score_name)
        if not os.path.exists(score_p):
            print(f"[SCORE] {folder}/{score_name}")
            studio_audio.gen_sfx(score_prompt, score_dur, score_p, key, influence=0.55)

    print("ALL_BATCH_AUDIO_DONE")

if __name__ == "__main__":
    main()
