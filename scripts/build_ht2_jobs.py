import json
import os
import re

BASE = "/Users/jack/.gemini/antigravity/scratch/nomad-cinema-parodies"
SCRIPT_PATH = f"{BASE}/scripts/08_heat_v2_script.json"
OUT_PATH = f"{BASE}/scripts/08_heat_v2_jobs.json"

BANNED_PROMPT_RE = re.compile(
    r"\b(rain|storm|streak|streaks|line|lines|particle|particles|droplet|droplets|"
    r"smile|smiling|grin|grinning|cheerful|happy|goofy|never|zero|motionless|rigid|still)\b",
    re.I,
)

CAM_DESC = {
    "STATIC_LOCKED": "Use a steady locked-off cinema camera mounted on a heavy studio tripod with grounded framing.",
    "HANDHELD_35MM": "Use subtle organic 35mm handheld camera breathing with gentle operator micro-movements while maintaining framing distance.",
    "SLOW_DOLLY_IN": "Use a smooth measured linear cinema push-in on dolly rails heightening psychological intensity.",
}

ACTING_BY_SHOT = {
    "HT2_02": "leaning slightly forward across the booth with focused detective intensity, measured micro-head tilts on stressed accusations, and sharp rhythmic eyebrow emphasis",
    "HT2_03": "holding cool, unhurried heist-leader poise, resting elbows calmly, delivering crisp deliberate head emphasis with steady blinks",
    "HT2_04": "tapping an incredulous beat with expressive brow tension, slight incredulous chin lift, and natural breathing shoulders",
    "HT2_05": "maintaining cold gravelly stoicism with subtle jaw tension, steady blinks, and calm measured delivery",
    "HT2_06": "shaking his head gently in exasperated fatherly disbelief, lifting his chin slightly under the conical bamboo hat rim with crisp lip articulation",
    "HT2_07": "locking cold steady eye contact across the booth with controlled minimal head emphasis and calm stern poise",
    "HT2_08": "narrowing his eyes analytically as he leans toward the warm brass lamp, tilting his head with urgent detective curiosity",
    "HT2_09": "holding tight shadowed composure with slight jaw clench, cold focused gaze, and steady measured articulation",
    "HT2_10": "dropping into urgent, frustrated detective conviction, leaning forward subtly with sharp brow emphasis and clear enunciated cadence",
    "HT2_11": "holding ruthless calm authority across the coffee cup, lifting his chin subtly with cold poise and deliberate lip sync",
    "HT2_12": "leaning closer with earnest tactical warning, slight head nod toward the small brown glass vial held calmly in view, and focused grave delivery",
    "HT2_13": "maintaining flint-hard refusal with cold downward-set lips at completion, subtle jaw shift, and unwavering gaze",
    "HT2_14": "widening his eyes slightly under the bamboo hat brim with urgent warning cadence and brisk expressive jaw articulation",
    "HT2_15": "holding icy solemn unamused conviction under the slow dolly push, tense flat lips, grave furrowed brow, and deliberate stressed beats",
    "HT2_16": "giving a razor-dry deadpan warning glare under the bamboo hat rim, tense unamused flat mouth, and calm grave brow posture",
    "HT2_17": "blinking a tight cold beat of sudden realization with subtle parted-lip hesitation before snapping cleanly shut",
    "HT2_19": "shaking his head calmly with weary dry humor, tilting the small brown glass vial slightly while speaking in unhurried deadpan cadence",
    "HT2_20": "sweating subtly under the brass diner light, dabbing his shirt collar calmly with grave stoic dignity and clean final lip closure",
}

SPEAKER_DESC = {
    "damon": "ONLY the bald Black man on the right side wearing black-rimmed rectangular glasses, a charcoal tailored wool suit jacket, open crisp white dress shirt collar, and short dark trimmed beard actively speaks",
    "deron": "ONLY the middle-aged East Asian man on the left side wearing a woven bamboo conical rice paddy hat and crimson gold-dragon embroidered Chinese silk robe actively speaks",
}

NEG_IT = (
    "smiling, smile, grin, grinning, smirk, smirking, happy, cheerful, laughing, teeth showing, bared teeth, "
    "wide smile, upturned mouth corners, cheeks lifting, amused, amusement, dimples, frozen lips, closed mouth while speaking, "
    "listener talking, extra bystanders, background crowd, waxy plastic skin, blurry, "
    "stiff robot pose, frozen eyes, subtitles, watermark"
)

NEG_LTX = (
    "smiling, smile, grin, laughing, dry straw, hay, chaff, dust cloud, broom bristles, wavy limbs, melting furniture, extra people, "
    "background diners, waiter, crowd, blurry, subtitles, watermark, waxy plastic skin"
)

SEED_OVERRIDES = {"HT2_06": 9906, "HT2_12": 9912, "HT2_15": 9915, "HT2_16": 9916}
CFG_OVERRIDES = {"HT2_15": 1.6, "HT2_16": 1.6}


def main():
    script = json.load(open(SCRIPT_PATH))
    setups = script["setups"]
    jobs = []

    for idx, s in enumerate(script["shots"]):
        sid = s["shot_id"]
        cm = s["camera_motion"]
        sp = s["speaker"]
        st_img = s["start_image"]
        setup_desc = setups[s["setup"]].replace("zero other diners", "empty quiet midnight diner booths behind them")

        if sid == "HT2_01":
            prompt = (
                f"Photorealistic 1995 35mm gritty Los Angeles midnight diner drama matching the starting frame. "
                f"Warm brass booth lamp glow contrasting with deep teal-blue midnight diner window reflections and distant out-of-focus city taillights. "
                f"Set context: {setup_desc} Soft wisps of hot steam curl gently upward from the white porcelain teapot and ceramic coffee mug "
                f"while Damon and Deron sit across the formica booth locked in quiet tense standoff with subtle shoulder breathing and natural eye blinks. "
                f"{CAM_DESC[cm]} Crisp 35mm film grain and authentic skin texture."
            )
            jobs.append({
                "shot_id": sid,
                "out_prefix": f"ht2_{sid}",
                "engine": "ltx25",
                "start_image": st_img,
                "end_image": None,
                "audio": f"{sid}.mp3",
                "silent_on_camera": True,
                "ltx_length": 89,
                "camera_motion": cm,
                "speaker": "fx",
                "speaker_side": "center",
                "seed": 8801,
                "ltx_prompt": prompt,
                "negative_prompt": NEG_LTX,
                "force": True,
            })
        elif sid == "HT2_18":
            prompt = (
                "Photorealistic 1995 35mm gritty Los Angeles midnight diner comedy-drama practical-FX shot matching the starting frame and ending frame. "
                "Frame 1 opens cleanly across the spotless, dry midnight formica diner booth with Damon in charcoal wool suit seated on the right and Deron in red gold-dragon silk robe and woven bamboo conical hat seated on the left above a completely clean black-and-white checkered floor. "
                "Damon keeps a stone-cold stoic poker face above the formica tabletop as a catastrophic pressurized wave of thick, chunky, glossy, disgusting dark-brown liquid diarrhea surges violently forward underneath the table across the checkered floor toward Deron's booth bench, splashing chunky glossy dark-brown puddles beneath the pedestal leg while both cups, teapot, and small glass vial stay untouched on top. "
                f"{CAM_DESC[cm]} Authentic practical 35mm film physics, fluid hydrodynamic liquid splash, crisp 35mm film grain."
            )
            jobs.append({
                "shot_id": sid,
                "out_prefix": f"ht2_{sid}",
                "engine": "ltx25",
                "start_image": "ht2_climax_start.jpg",
                "end_image": "ht2_climax_fx.jpg",
                "audio": f"{sid}.mp3",
                "silent_on_camera": True,
                "ltx_length": 97,
                "end_guide_strength": 0.60,
                "s1_img_strength": 0.65,
                "camera_motion": cm,
                "speaker": "fx",
                "speaker_side": "center",
                "seed": 9918,
                "ltx_prompt": prompt,
                "negative_prompt": NEG_LTX,
                "force": True,
            })
        else:
            dlg = s["dialogue"].replace('"', "'")
            acting = ACTING_BY_SHOT[sid]
            extra_ots = (
                " The blurred foreground listener remains silent with lips comfortably sealed."
                if "OTS" in s["setup"] else ""
            )
            prompt = (
                f"Photorealistic 1995 35mm gritty Los Angeles midnight diner drama matching the starting frame. "
                f"Warm amber tungsten booth lamp and deep teal-black midnight glass reflections. "
                f"Set context: {setup_desc} {CAM_DESC[cm]} "
                f"Exact hair, bamboo hat, glasses, wardrobe, teapot, vial, and lighting preserved from the starting frame. "
                f"{SPEAKER_DESC[sp]} with natural expressive jaw and lip articulation synced cleanly to the dialogue: \"{dlg}\", "
                f"{acting}, finishing with lips closing calmly in deadpan gravity.{extra_ots} "
                f"Real human skin pores, subtle breathing motion, authentic eye blinks, 1990s 35mm film grain."
            )
            jobs.append({
                "shot_id": sid,
                "out_prefix": f"ht2_{sid}",
                "engine": "infinitetalk",
                "start_image": st_img,
                "end_image": None,
                "audio": f"{sid}.mp3",
                "silent_on_camera": False,
                "ltx_length": None,
                "camera_motion": cm,
                "speaker": sp,
                "speaker_side": s["speaker_side"],
                "seed": SEED_OVERRIDES.get(sid, 8800 + idx + 1),
                "wan_cfg": CFG_OVERRIDES.get(sid, 1.5),
                "wan_steps": 6,
                "wan_audio_scale": 1.05,
                "ltx_prompt": prompt,
                "negative_prompt": NEG_IT,
                "force": sid in SEED_OVERRIDES,
            })

    # Strict affirmative-prompt audit (strip spoken dialogue quotes before testing visual cues)
    for j in jobs:
        vis = re.sub(r'"[^"]*"', '""', j["ltx_prompt"])
        hits = BANNED_PROMPT_RE.findall(vis)
        assert not hits, f"{j['shot_id']} has banned bleed/negative word(s) in visual prompt: {hits}"

    json.dump(jobs, open(OUT_PATH, "w"), indent=2)
    print(f"WROTE {len(jobs)} clean v2.8 jobs to {OUT_PATH}")


if __name__ == "__main__":
    main()
