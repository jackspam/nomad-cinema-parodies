import json
import re

BASE = "/Users/jack/.gemini/antigravity/scratch/nomad-cinema-parodies"
SCRIPT_PATH = f"{BASE}/scripts/09_no_country_v2_script.json"
OUT_PATH = f"{BASE}/scripts/09_no_country_v2_jobs.json"

BANNED_PROMPT_RE = re.compile(
    r"\b(rain|storm|streak|streaks|line|lines|particle|particles|droplet|droplets|"
    r"smile|smiling|grin|grinning|cheerful|happy|goofy|never|zero|motionless|rigid|still)\b",
    re.I,
)

CAM_DESC = {
    "STATIC_LOCKED": "Use a steady locked-off cinema camera mounted on a heavy studio tripod with grounded Roger Deakins composition.",
    "HANDHELD_35MM": "Use subtle organic 35mm handheld camera breathing with gentle operator micro-movements while maintaining framing distance.",
    "SLOW_DOLLY_IN": "Use a smooth measured linear cinema push-in on dolly rails deepening psychological dread.",
}

ACTING_BY_SHOT = {
    "NC2_02": "leaning politely over the oak counter with friendly West Texas curiosity, natural brow lift, and relaxed easy cadence",
    "NC2_03": "holding ice-cold deadpan authority with slight deliberate head tilt toward the counter, unhurried blinks, and steady gaze",
    "NC2_04": "raising eyebrows awkwardly with defensive shoulder shrug, quick earnest explanation, and expressive jaw movement",
    "NC2_05": "shifting his shoulders subtly with quiet menacing poise, tilting his head calmly on stressed accusations, natural eye blinks, and expressive measured jaw movement",
    "NC2_06": "holding earnest worried brow furrows, tense flat unamused mouth, and anxious steady eye contact across the oak counter",
    "NC2_07": "tilting his chin down slightly toward the silver quarter on the wood grain, speaking in low deliberate hypnotic cadence",
    "NC2_08": "leaning back uneasily behind the register with widening worried eyes, nervous swallows, and pleading gesture toward the jerky rack",
    "NC2_09": "holding unblinking flint-cold predator focus under harsh fluorescent light, delivering measured low-toned menace with calm jaw control",
    "NC2_10": "tensing up with panicked incredulous eyebrow raise, leaning forward slightly in genuine disbelief with brisk articulate phrasing",
    "NC2_11": "holding grave philosophical coldness past Zach's shoulder, shifting weight subtly with slow measured head emphasis",
    "NC2_12": "glancing down at the counter in exasperated disbelief with tight stressed brow, urging frantically yet honestly",
    "NC2_13": "maintaining flint-cold solemn authority with flat downward-set unamused lips, heavy serious brow, minimal decisive chin dip, and piercing unamused stare",
    "NC2_14": "exhaling nervously, squinting in sudden desperate surrender with brisk animated brow and urgent final warning",
    "NC2_15": "holding cold icy direct stare straight ahead under the slow dolly push with flat stoic poise and slight deliberate chin lift at the punchline",
    "NC2_16": "widening eyes in horrified awe, leaning forward cautiously over the wood counter with breathless urgent articulation",
    "NC2_17": "holding eerie calm fatalistic resolve right before impact, faint blinking beat and quiet deadpan closure",
    "NC2_19": "resting both hands quietly flat on the oak counter beside the upright bright pink Pepto-Bismol bottle with pale stunned exhaustion, slow bewildered blinks, and hollow voice",
    "NC2_20": "keeping both hands completely down out of view with cold stony stoic composure, steady piercing gaze behind black-rimmed glasses, subtle calm head tilt, and crisp flat deadpan lip closure",
}

SPEAKER_DESC = {
    "damon": "ONLY the bald Black man on the right side wearing black-rimmed rectangular glasses, a dark navy snap-front work jacket over a black crew tee, and short dark trimmed beard actively speaks",
    "zach": "ONLY the brown-haired brown-bearded man on the left side wearing a faded yellow-ochre plaid short-sleeve button-up shirt over a white tee with tan suspenders actively speaks",
}

NEG_IT = (
    "smiling, smile, grin, grinning, smirk, smirking, happy, cheerful, laughing, teeth showing, bared teeth, "
    "wide smile, upturned mouth corners, cheeks lifting, amused, amusement, dimples, frozen lips, closed mouth while speaking, "
    "raised hand, hand near face, adjusting glasses, bottle lifting, listener talking, extra shoppers, background crowd, waxy plastic skin, blurry, "
    "stiff robot pose, frozen eyes, subtitles, watermark"
)

NEG_LTX = (
    "smiling, smile, grin, laughing, frozen cone, stiff solid beam, wavy limbs, melting wood counter, extra people, "
    "customers, clerk walking away, crowd, blurry, subtitles, watermark, waxy plastic skin"
)

SEED_OVERRIDES = {
    "NC2_05": 9955,
    "NC2_06": 9956,
    "NC2_13": 9963,
    "NC2_19": 9969,
    "NC2_20": 9970,
}
CFG_OVERRIDES = {
    "NC2_05": 1.5,
    "NC2_06": 1.6,
    "NC2_13": 1.6,
    "NC2_19": 1.6,
    "NC2_20": 1.6,
}
ASCALE_OVERRIDES = {"NC2_05": 1.08}


def main():
    script = json.load(open(SCRIPT_PATH))
    setups = script["setups"]
    jobs = []

    for idx, s in enumerate(script["shots"]):
        sid = s["shot_id"]
        cm = s["camera_motion"]
        sp = s["speaker"]
        st_img = s["start_image"]
        setup_desc = setups[s["setup"]].replace("zero other customers inside", "quiet empty rural general store interior with only the two men")

        if sid == "NC2_01":
            prompt = (
                f"Photorealistic 1980 35mm gritty West Texas gas-station thriller matching the starting frame. "
                f"Bleached dusty afternoon desert sunlight streaming past the glass window contrasted with warm store fluorescent ceiling light. "
                f"Set context: {setup_desc} Zach shifts his weight gently behind the oak counter, blinks naturally, and glances politely toward Damon, while Damon subtly tilts his chin and blinks calmly across the silver quarter and foil cashew bag as sunlit desert dust motes drift slowly across the air. "
                f"{CAM_DESC[cm]} Crisp 35mm film grain and authentic human skin texture."
            )
            jobs.append({
                "shot_id": sid,
                "out_prefix": f"nc2_{sid}",
                "engine": "ltx25",
                "start_image": st_img,
                "end_image": None,
                "audio": f"{sid}.mp3",
                "silent_on_camera": True,
                "ltx_length": 89,
                "s1_img_strength": 0.55,
                "camera_motion": cm,
                "speaker": "fx",
                "speaker_side": "center",
                "seed": 9951,
                "ltx_prompt": prompt,
                "negative_prompt": NEG_LTX,
                "force": True,
            })
        elif sid == "NC2_18":
            prompt = (
                "Photorealistic 1980 35mm gritty West Texas thriller practical-FX shot matching the starting frame and ending frame. "
                "Frame 1 opens cleanly across the spotless, dry scarred oak Texaco checkout counter with Zach on left behind the register and Damon on right in his dark navy work jacket and black-rimmed glasses standing over clean sunlit dry floorboards. "
                "Damon keeps a stone-cold stoic poker face above the counter as a catastrophic high-pressure wave of thick, chunky, glossy, disgusting dark-brown liquid diarrhea blasts explosively backward from behind his black trousers across the clean sunlit floorboards, splashing dynamically onto the lower white store door and puddling naturally while Zach freezes in stunned shock. "
                f"{CAM_DESC[cm]} Dynamic practical fluid splash physics, wet glossy sheen, crisp 35mm film grain."
            )
            jobs.append({
                "shot_id": sid,
                "out_prefix": f"nc2_{sid}",
                "engine": "ltx25",
                "start_image": "nc2_climax_start.jpg",
                "end_image": "nc2_climax_fx.jpg",
                "audio": f"{sid}.mp3",
                "silent_on_camera": True,
                "ltx_length": 97,
                "end_guide_strength": 0.55,
                "s1_img_strength": 0.65,
                "camera_motion": cm,
                "speaker": "fx",
                "speaker_side": "center",
                "seed": 9968,
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
                f"Photorealistic 1980 35mm gritty West Texas gas-station thriller matching the starting frame. "
                f"Bleached sunlit desert window and vintage store fluorescent mix lighting. "
                f"Set context: {setup_desc} {CAM_DESC[cm]} "
                f"Exact face, glasses, hair, wardrobe, jars, register, quarter, and Pepto bottle preserved from the starting frame. "
                f"{SPEAKER_DESC[sp]} with natural expressive jaw and lip articulation synced cleanly to the dialogue: \"{dlg}\", "
                f"{acting}, finishing with lips closing calmly in deadpan gravity.{extra_ots} "
                f"Real human skin pores, subtle shoulder breathing, authentic eye blinks, 1980s 35mm film grain."
            )
            jobs.append({
                "shot_id": sid,
                "out_prefix": f"nc2_{sid}",
                "engine": "infinitetalk",
                "start_image": st_img,
                "end_image": None,
                "audio": f"{sid}.mp3",
                "silent_on_camera": False,
                "ltx_length": None,
                "camera_motion": cm,
                "speaker": sp,
                "speaker_side": s["speaker_side"],
                "seed": SEED_OVERRIDES.get(sid, 9900 + idx + 1),
                "wan_cfg": CFG_OVERRIDES.get(sid, 1.5),
                "wan_steps": 6,
                "wan_audio_scale": ASCALE_OVERRIDES.get(sid, 1.05),
                "ltx_prompt": prompt,
                "negative_prompt": NEG_IT,
                "force": sid in SEED_OVERRIDES,
            })

    for j in jobs:
        vis = re.sub(r'"[^"]*"', '""', j["ltx_prompt"])
        hits = BANNED_PROMPT_RE.findall(vis)
        assert not hits, f"{j['shot_id']} has banned bleed/negative word(s) in visual prompt: {hits}"

    json.dump(jobs, open(OUT_PATH, "w"), indent=2)
    print(f"WROTE {len(jobs)} clean v2.8 jobs to {OUT_PATH}")


if __name__ == "__main__":
    main()
