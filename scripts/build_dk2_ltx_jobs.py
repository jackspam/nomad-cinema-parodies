"""Build complete 40-shot LTX-2.5 Dev BF16 job manifest for Dark Knight v2."""
import json
import os

BASE = "/Users/jack/.gemini/antigravity/scratch/nomad-cinema-parodies"
SCRIPT = json.load(open(f"{BASE}/scripts/02_dark_knight_v2_script.json"))["shots"]
REFS_DIR = f"{BASE}/refs/02_dark_knight_v2"

CAST_DESC = {
    "hooman_act1": "the man in flaky cracked white Joker greasepaint, blackened eye paint, smeared crimson mouth scars, shorter dark-green streaked curly hair, subtle dark mustache/goatee stubble under paint, and dark purple tailored coat over green vest",
    "hooman_act2": "the coatless man in flaky cracked white Joker greasepaint, blackened eye paint, smeared crimson mouth scars, shorter dark-green streaked curly hair, subtle mustache/goatee stubble under paint, patterned grey-lavender dress shirt, and dark green waistcoat",
    "damon": "the bald man with heavy black-framed glasses, tanned weathered skin pores, and salt-and-pepper stubble wearing matte-black armored Dark Knight Batsuit plates and black cape with NO mask cowl",
    "gigi": "the 67-year-old woman with weathered skin, red-framed glasses, and strawberry-blonde hair wearing a dark charcoal GCPD trench coat",
    "deron": "the East Asian detective wearing a woven bamboo conical hat and ornate red dragon silk robe over a GCPD vest",
    "zach": "the curly-haired bearded tech officer in dark-framed glasses and a brown jacket",
}

jobs = []
for idx, sh in enumerate(SCRIPT, 1):
    sid = sh["shot_id"]
    n = int(sid.split("_")[1])
    start_img = f"dk2_shot{n:02d}_start.jpg"
    end_img = f"dk2_shot{n:02d}_end.jpg" if sh.get("yt_end_frame") else None

    spk = sh["speaker"]
    if spk == "hooman":
        spk_desc = CAST_DESC["hooman_act1"] if sh["act"] == 1 else CAST_DESC["hooman_act2"]
    else:
        spk_desc = CAST_DESC[spk]

    side_phrase = {
        "left": "on the left",
        "center": "in the center of frame",
        "right": "on the right",
    }[sh.get("speaker_side", "center")]

    act_light = (
        "Inside the pitch-dark cyan-slate shadowed interrogation room under dim frosted ceiling glow and black desk lamp."
        if sh["act"] == 1 and n != 9
        else "Inside the blinding clinical fluorescent-lit interrogation room against pale greenish-beige painted cinderblocks and white painted brick."
    )
    if n in (14, 28, 32):
        act_light = "Inside the dark green-shadowed police observation room behind the two-way mirrored glass."
    elif n == 35:
        act_light = "In the dim dark precinct hallway outside the frosted glass interrogation door."
    elif n == 9:
        act_light = "Standing beside the heavy riveted steel interrogation door in moody overhead corridor spill."

    silent_others = "All other characters in the frame keep their mouths completely CLOSED and listen silently without speaking."
    motion_line = (
        "Smoothly transition camera perspective and subtle body movement from the starting frame toward the ending keyframe's exact composition."
        if end_img
        else "Keep camera framing closely locked to the starting frame with only subtle realistic cinema breathing and micro-movement."
    )

    ltx_prompt = (
        f"Photorealistic 2008 35mm movie scene matching the starting frame. {act_light} "
        f"{motion_line} "
        f"ONLY {spk_desc} {side_phrase} actively speaks, moving his or her lips, mouth shapes, teeth, and jaw clearly and precisely in real-time lip synchronization "
        f"with every syllable of the dialogue: \"{sh['dialogue']}\" "
        f"{silent_others} Real human skin pores, authentic natural facial expressions, subtle 2008 35mm film grain."
    )

    neg = (
        "frozen lips, mouth not moving, closed mouth while speaking, bad lip sync, off-timing lip sync, static freeze, "
        "everyone mouthing, listener talking, waxy skin, plastic face, airbrushed smooth skin, face morphing, "
        "Batman wearing cowl mask, Heath Ledger blond hair, extra limbs, subtitles, watermark, blurry"
    )

    job = {
        "shot_id": sid,
        "out_prefix": f"dk2_{sid}",
        "start_image": start_img,
        "end_image": end_img,
        "audio": f"{sid}.mp3",
        "seed": 5000 + n,
        "speaker_side": sh.get("speaker_side", "center"),
        "s1_img_strength": 0.65 if n == 27 else 0.60,
        "end_guide_strength": 0.80 if n == 27 else 0.55,
        "cfg": 3.5,
        "steps": 24,
        "ltx_prompt": ltx_prompt,
        "negative_prompt": neg,
    }
    jobs.append(job)

out_path = f"{BASE}/scripts/02_dark_knight_v2_jobs.json"
json.dump(jobs, open(out_path, "w"), indent=2)
print(f"WROTE {len(jobs)} LTX-2.5 Dev BF16 jobs -> {out_path}")
