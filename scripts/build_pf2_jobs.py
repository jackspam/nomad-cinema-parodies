"""Build scripts/05_pulp_fiction_v2_jobs.json strictly compliant with PIPELINE_RULES.md v2.4."""
import json

BASE = "/Users/jack/.gemini/antigravity/scratch/nomad-cinema-parodies"
SCRIPT = json.load(open(f"{BASE}/scripts/05_pulp_fiction_v2_script.json"))
MANIFEST = json.load(open(f"{BASE}/audio/05_pulp_fiction_v2/audio_manifest.json"))
DUR_BY_ID = {x["shot_id"]: x["dur"] for x in MANIFEST["shots"]}

CAMERA_DIRECTIVES = {
    "STATIC_LOCKED": "static lock-off camera mounted on a heavy tripod, completely stationary framing",
    "HANDHELD_35MM": "subtle organic 35mm handheld camera breathing with tiny operator micro-movements, maintaining fixed framing distance",
    "SLOW_DOLLY_IN": "measured slow linear dolly push-in along fixed axis on weighted rails",
    "SLOW_DOLLY_OUT": "measured slow linear dolly pull-out revealing surrounding space",
    "PAN_ORBIT": "smooth continuous lateral tracking move matching blocked screen direction",
    "IMPACT_SHAKE": "handheld camera jolting organically on physical motion or explosive shockwave, crisp 35mm Panavision lens, stable subject focus",
}

SPEAKER_DESCS = {
    "hooman": "the olive-skinned man with short curly dark hair, mustache and goatee stubble, wearing a crisp 1994 black wool suit, white shirt, and skinny black tie",
    "damon": "the bald man wearing rectangular black-framed glasses, tailored 1994 black wool suit, white shirt, and skinny black tie",
    "deron": "the East Asian man with short spiky black hair wearing an open-collar burgundy silk shirt and gold wristwatch",
    "zach": "the bearded man wearing a brown Alo crewneck pullover",
    "ajay": "the Indian-American man in blue Kaiser surgical scrubs with stethoscope and silver forehead surgical headlamp",
    "gigi": "the 67-year-old woman with long strawberry-blonde hair and crimson-framed eyeglasses wearing a tailored charcoal blazer",
    "sheren": "the dark-haired woman in a sleek black leather jacket",
}

SETTING_BY_SETUP = {
    "A_CAR_WIDE": "Inside the sunlit 1994 cream white-leather sedan driving through morning Los Angeles streets",
    "B_CAR_CU_DAMON": "Inside the sunlit 1994 cream white-leather sedan passenger seat with sunny LA palm trees outside",
    "C_CAR_CU_HOOMAN": "Inside the sunlit 1994 cream white-leather sedan driver seat with morning LA street outside",
    "D_HALLWAY": "Inside the dim bare-bulb amber tungsten 1970s apartment corridor outside Apartment 49",
    "E_APT_WIDE": "Inside the sunlit olive-green 1994 Los Angeles apartment bathed in warm morning amber venetian-blind light",
    "F_HOOMAN_BLINDS": "Inside the olive-green 1994 apartment beside bright glowing amber horizontal venetian blinds and cream door trim",
    "G_DAMON_DOOR": "Inside the sunlit olive-green 1994 apartment beside the ajar beige-white interior doorway",
    "H_DERON_TABLE": "At the white Formica breakfast table in the olive-green apartment beside bamboo har gow steamer, teacup, and Po Chai Pills box",
    "I_ZACH_KITCHEN": "Inside the sunlit 1970s olive-green apartment kitchen pass-through with vintage cream refrigerator behind",
    "J_AJAY_SOFA": "On the orange-brown 1970s plaid apartment sofa bathed in warm golden window light",
    "K_GIGI_DOOR": "At the open sunlit apartment front doorway with retro olive kitchen cabinets behind",
    "L_BATHROOM_FX": "Looking through the open 1970s white-tiled apartment bathroom doorway as thick chunky brown practical-FX sludge erupts with billowing steam",
    "M_BRIEFCASE_GOLD": "Looking upward from inside the glowing golden-amber open leather briefcase inside the olive-green kitchen",
}

jobs = []
md_rows = []
for idx, sh in enumerate(SCRIPT["shots"], start=1):
    sid = sh["shot_id"]
    spk = sh["speaker"]
    cm = sh["camera_motion"]
    cam_dir = CAMERA_DIRECTIVES[cm]
    setting = SETTING_BY_SETUP[sh["setup"]]
    dur = DUR_BY_ID.get(sid, 5.0)
    is_fx = (spk == "sfx")

    # Hybrid engine routing: InfiniteTalk for tight/dialogue acting; LTX-2.5 for physical FX beats & wide entrance/exit moves
    if is_fx or sid in {"PF2_06", "PF2_21", "PF2_38", "PF2_42"}:
        engine = "ltx25"
    else:
        engine = "infinitetalk"

    if is_fx:
        prompt = (
            f"Photorealistic 1994 35mm Kodachrome movie scene matching the starting frame. {setting}. "
            f"Use {cam_dir}. Practical movie-prop slapstick physics: thick chunky brown liquid sludge blasts dynamically "
            f"across tile and linoleum with billowing steam and realistic splashes while clothed character braces/reacts naturally. "
            f"1994 Kodak 5248 35mm film grain, authentic contrast."
        )
        neg = (
            "waxy skin, smooth plastic surface, nudity, static freeze, flickering background, extra limbs, subtitles, watermark, blurry"
        )
    else:
        spk_desc = SPEAKER_DESCS[spk]
        side_phrase = f"on the {sh['speaker_side']} of frame" if sh["speaker_side"] != "center" else "in frame"
        prompt = (
            f"Photorealistic 1994 35mm Kodachrome movie scene matching the starting frame. {setting}. "
            f"Use {cam_dir}. Exact character hair, glasses, costume, and set lighting from the starting frame. "
            f"ONLY {spk_desc} {side_phrase} actively speaks with natural jaw and lip articulation synced cleanly to the dialogue: "
            f"\"{sh['dialogue']}\" maintaining serious deadpan 1994 thriller gravity and closing mouth cleanly when dialogue finishes. "
            f"All other characters visible in frame keep their mouths completely CLOSED and listen silently without speaking. "
            f"Real human skin pores, subtle 1994 35mm film grain."
        )
        neg = (
            "frozen lips, mouth not moving, closed mouth while speaking, everyone mouthing, listener talking, "
            "unprompted grin at end, waxy skin, hat or crown, dragon robe, extra limbs, subtitles, watermark, blurry"
        )

    jobs.append({
        "shot_id": sid,
        "out_prefix": f"pf2_{sid}",
        "engine": engine,
        "start_image": f"pf2_shot{idx:02d}_start.jpg",
        "end_image": None,
        "audio": f"{sid}.mp3",
        "ltx_length": max(49, int(round(dur * 24))),
        "camera_motion": cm,
        "speaker": spk,
        "speaker_side": sh["speaker_side"],
        "seed": 7200 + idx,
        "ltx_prompt": prompt,
        "negative_prompt": neg,
        "force": False,
    })

    md_rows.append(f"| `{sid}` | Act {sh['act']} | `{spk.upper()}` | `{dur:.2f}s` | `{engine}` | `{cm}` | {sh['dialogue']} |")

json.dump(jobs, open(f"{BASE}/scripts/05_pulp_fiction_v2_jobs.json", "w"), indent=2)
print(f"WROTE {len(jobs)} jobs -> scripts/05_pulp_fiction_v2_jobs.json (est runtime = {MANIFEST['estimated_runtime_sec']}s)")

# Append full shot table cleanly to markdown screenplay if not already appended
md_path = f"{BASE}/scripts/05_pulp_fiction_v2_script.md"
md_base = open(md_path).read().split("## Complete 42-Shot Roster")[0].rstrip()
table_md = (
    "\n\n## Complete 42-Shot Roster & Camera Schedule\n\n"
    f"- **Total Audio-Driven Pacing:** **{MANIFEST['estimated_runtime_sec']:.1f}s ({MANIFEST['estimated_runtime_sec']/60:.2f} min)**\n\n"
    "| Shot | Act | Speaker | Audio | Engine | Camera Motion | Dialogue / Beat |\n"
    "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
    + "\n".join(md_rows)
    + "\n"
)
open(md_path, "w").write(md_base + table_md)
print(f"UPDATED {md_path}")
