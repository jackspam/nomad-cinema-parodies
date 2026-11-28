"""Stage 2 Audio Generator for Film 2: 09_no_country_v2 (No Country for Old Men — Call It, Damon & Zach ONLY)."""
import json
import os
import subprocess
import sys

sys.path.insert(0, "/Users/jack/.gemini/antigravity/scratch/nomad-cinema-parodies")
from studio_audio import CAST, gen_sfx, gen_tts, load_key

BASE = "/Users/jack/.gemini/antigravity/scratch/nomad-cinema-parodies"
AUDIO_DIR = f"{BASE}/audio/09_no_country_v2"
SCRIPT_PATH = f"{BASE}/scripts/09_no_country_v2_script.json"
os.makedirs(AUDIO_DIR, exist_ok=True)


def ffprobe_dur(p: str) -> float:
    return float(
        subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", p],
            text=True,
        ).strip()
    )


def build_script() -> dict:
    return {
        "filename_base": "09_no_country_v2",
        "film_number": "09",
        "title": "No Country for Old Men \u2014 Call It",
        "subtitle": "1980 West Texas Texaco Counter \u00b7 Two-Hander v2.8: Damon & Zach",
        "setups": {
            "NC2_WIDE": "Gritty 1980 Roger Deakins 35mm West Texas Texaco general store interior at sun-bleached midday; Zach (brown-bearded gas-station clerk in faded yellow-ochre plaid short-sleeve button-up shirt over white crew tee and tan suspenders) stands on left behind scarred oak checkout counter with sunlit cracked-earth desert plains in the wide glass window behind him and vintage jerky jars beside an old brass cash register; Damon (bald Black man with rectangular black-rimmed glasses and short trimmed beard, dressed in dark navy snap-front work jacket over black cotton tee) stands on right across the counter beside a crinkled foil cashew bag and a single silver quarter on the wood grain; zero other customers inside.",
            "NC2_ZACH_OTS": "Shallow f/2.2 35mm OTS past Damon's dark navy work-jacket shoulder in foreground right onto nervous Zach on left behind the oak counter framed against sunlit West Texas desert glass.",
            "NC2_DAMON_OTS": "Shallow f/2.2 35mm OTS past Zach's yellow-ochre plaid shoulder & suspender strap in foreground left onto ice-cold deadpan Damon on right framed against sunlit white store doorway and dusty snack shelves.",
            "NC2_ZACH_MCU": "Gritty Deakins MCU of bearded Zach framed left-of-center behind the scratched wooden counter beside jerky jars and brass cash register edge under harsh overhead fluorescent and window key light.",
            "NC2_DAMON_MCU": "Gritty Deakins MCU of Damon framed right-of-center in dark work jacket against sunlit white paneled door and dusty Texaco pegboard snacks, eyes unwavering across the counter.",
            "NC2_ZACH_CU": "Tight intense 35mm CU of Zach framed left, forehead beaded with nervous West Texas heat sweat, staring helplessly down toward the counter coin.",
            "NC2_DAMON_CU": "Tight intense 35mm CU of Damon framed right in stark half-shadow beneath overhead store light, razor-cold focus fixed forward.",
            "NC2_CLIMAX_FX": "Wide Texaco checkout-counter practical-FX frame derived from NC2_WIDE: Damon holds completely deadpan above the wooden counter on the right as a catastrophic pressurized horizontal torrent of thick dark-brown liquid diarrhea blasts violently from behind his black trousers across the faded dusty floorboards behind the counter base while Zach freezes in shock on the left.",
            "NC2_ZACH_POST": "Derived from NC2_ZACH_MCU: pale shell-shocked Zach slowly sliding a bright pink bottle of Pepto-Bismol across the scratched oak counter toward the tarnished silver quarter.",
            "NC2_DAMON_POST": "Derived from NC2_DAMON_CU: composed, stone-faced Damon adjusting his black glasses calmly with one hand beside the sunlit store door.",
        },
        "shots": [
            {
                "shot_id": "NC2_01",
                "setup": "NC2_WIDE",
                "start_image": "nc2_master_wide.jpg",
                "act": 1,
                "speaker": "fx",
                "speaker_side": "center",
                "camera_motion": "STATIC_LOCKED",
                "cam": "Static wide Texaco counter establishing Zach left behind the register and Damon right beside a silver quarter and cashew bag.",
                "dialogue": "",
                "tts": "",
            },
            {
                "shot_id": "NC2_02",
                "setup": "NC2_ZACH_OTS",
                "start_image": "nc2_zach_ots.jpg",
                "act": 1,
                "speaker": "zach",
                "speaker_side": "left",
                "camera_motion": "STATIC_LOCKED",
                "cam": "Locked OTS past Damon's dark shoulder onto polite, awkward Zach behind the register.",
                "dialogue": "Cash or pump two, mister? Fair warning though, that roller-grill brisket taco been spinning since Tuesday morning... y'all fixin' to get rain out west?",
                "tts": "Cash or pump two, mister? Fair warning though, that roller-grill brisket taco been spinning since Tuesday morning... y'all fixin' to get rain out west?",
            },
            {
                "shot_id": "NC2_03",
                "setup": "NC2_DAMON_OTS",
                "start_image": "nc2_damon_ots.jpg",
                "act": 1,
                "speaker": "damon",
                "speaker_side": "right",
                "camera_motion": "STATIC_LOCKED",
                "cam": "Locked OTS past Zach's plaid shoulder onto unblinking Damon.",
                "dialogue": "Two forty-nine for the cashews. Why did you ask about the brisket taco? It's none of your business what I ate before my morning Aquabike ride.",
                "tts": "Two forty-nine for the cashews. Why did you ask about the brisket taco? It's none of your business what I ate before my morning Aquabike ride.",
            },
            {
                "shot_id": "NC2_04",
                "setup": "NC2_ZACH_MCU",
                "start_image": "nc2_zach_mcu.jpg",
                "act": 1,
                "speaker": "zach",
                "speaker_side": "left",
                "camera_motion": "HANDHELD_35MM",
                "cam": "MCU on flustered Zach trying to defuse the sudden hostility.",
                "dialogue": "Whoa, hey, I didn't mean nothing by it, man. You just grabbed three Imodium packs and two wet naps, so I figured maybe the brisket got you.",
                "tts": "Whoa, hey, I didn't mean nothing by it, man. You just grabbed three Imodium packs and two wet naps, so I figured maybe the brisket got you.",
            },
            {
                "shot_id": "NC2_05",
                "setup": "NC2_DAMON_MCU",
                "start_image": "nc2_damon_mcu.jpg",
                "act": 1,
                "speaker": "damon",
                "speaker_side": "right",
                "camera_motion": "STATIC_LOCKED",
                "cam": "Deadpan locked MCU of Damon across the dusty counter.",
                "dialogue": "What time do you close this station? Wait... did you just assume an expired gas-station taco can rattle my core?",
                "tts": "What time do you close this station? Wait... did you just assume an expired gas-station taco can rattle my core?",
            },
            {
                "shot_id": "NC2_06",
                "setup": "NC2_ZACH_OTS",
                "start_image": "nc2_zach_ots.jpg",
                "act": 1,
                "speaker": "zach",
                "speaker_side": "left",
                "camera_motion": "STATIC_LOCKED",
                "cam": "Locked OTS onto bewildered Zach eyeing the dusty clock behind him.",
                "dialogue": "We close at six, round suppertime. Listen, dude, you're sweating straight through a heavy denim shirt at sixty-eight degrees. Take the Pepto.",
                "tts": "We close at six, round suppertime. Listen, dude, you're sweating straight through a heavy denim shirt at sixty-eight degrees. Take the Pepto.",
            },
            {
                "shot_id": "NC2_07",
                "setup": "NC2_DAMON_OTS",
                "start_image": "nc2_damon_ots.jpg",
                "act": 1,
                "speaker": "damon",
                "speaker_side": "right",
                "camera_motion": "STATIC_LOCKED",
                "cam": "Locked OTS on Damon tilting his chin down calmly toward the counter.",
                "dialogue": "You see this 1958 quarter? It's been traveling twenty-two years to get across this counter... right beside three warm brisket tortillas.",
                "tts": "You see this 1958 quarter? It's been traveling twenty-two years to get across this counter... right beside three warm brisket tortillas.",
            },
            {
                "shot_id": "NC2_08",
                "setup": "NC2_ZACH_MCU",
                "start_image": "nc2_zach_mcu.jpg",
                "act": 2,
                "speaker": "zach",
                "speaker_side": "left",
                "camera_motion": "STATIC_LOCKED",
                "cam": "Locked MCU on Zach nervously eyeballing the quarter.",
                "dialogue": "Look, man, your stomach just made a sound like a wet carburetor. You don't gotta flip coins—the bathroom key is hanging right next to the jerky.",
                "tts": "Look, man, your stomach just made a sound like a wet carburetor. You don't gotta flip coins—the bathroom key is hanging right next to the jerky.",
            },
            {
                "shot_id": "NC2_09",
                "setup": "NC2_DAMON_CU",
                "start_image": "nc2_damon_cu.jpg",
                "act": 2,
                "speaker": "damon",
                "speaker_side": "right",
                "camera_motion": "STATIC_LOCKED",
                "cam": "Tight CU of Damon's icy unblinking intensity.",
                "dialogue": "What's the most you ever lost in an Aquabike age-group transition? If you call heads, I walk calmly out that door to my bike rack.",
                "tts": "What's the most you ever lost in an Aquabike age-group transition? If you call heads, I walk calmly out that door to my bike rack.",
            },
            {
                "shot_id": "NC2_10",
                "setup": "NC2_ZACH_CU",
                "start_image": "nc2_zach_cu.jpg",
                "act": 2,
                "speaker": "zach",
                "speaker_side": "left",
                "camera_motion": "HANDHELD_35MM",
                "cam": "Tight CU on Zach panicking over what he's being asked to wager.",
                "dialogue": "Wait a second... what happens if I call tails?! I ain't mopping aisle four on a Friday afternoon, friendo!",
                "tts": "Wait a second... what happens if I call tails?! I ain't mopping aisle four on a Friday afternoon, friendo!",
            },
            {
                "shot_id": "NC2_11",
                "setup": "NC2_DAMON_OTS",
                "start_image": "nc2_damon_ots.jpg",
                "act": 2,
                "speaker": "damon",
                "speaker_side": "right",
                "camera_motion": "STATIC_LOCKED",
                "cam": "Locked OTS onto cold unhurried Damon holding his ground.",
                "dialogue": "I can't call it for you. Wouldn't be fair. That second brisket taco was already riding shotgun in my lower tract when I pulled up to pump two.",
                "tts": "I can't call it for you. Wouldn't be fair. That second brisket taco was already riding shotgun in my lower tract when I pulled up to pump two.",
            },
            {
                "shot_id": "NC2_12",
                "setup": "NC2_ZACH_CU",
                "start_image": "nc2_zach_cu.jpg",
                "act": 2,
                "speaker": "zach",
                "speaker_side": "left",
                "camera_motion": "STATIC_LOCKED",
                "cam": "Sweating tight CU of Zach trapped by pure logic.",
                "dialogue": "Why am I betting on YOUR digestive system?! You didn't even open the cashews yet—just grab the pink bottle on my counter!",
                "tts": "Why am I betting on YOUR digestive system?! You didn't even open the cashews yet—just grab the pink bottle on my counter!",
            },
            {
                "shot_id": "NC2_13",
                "setup": "NC2_DAMON_CU",
                "start_image": "nc2_damon_cu.jpg",
                "act": 2,
                "speaker": "damon",
                "speaker_side": "right",
                "camera_motion": "STATIC_LOCKED",
                "cam": "Stone-faced tight CU of Damon pressing harder.",
                "dialogue": "No medicine. Everything in my race nutrition is weighed to the gram. Call it, friend.",
                "tts": "No medicine. Everything in my race nutrition is weighed to the gram. Call it, friend.",
            },
            {
                "shot_id": "NC2_14",
                "setup": "NC2_ZACH_CU",
                "start_image": "nc2_zach_cu.jpg",
                "act": 2,
                "speaker": "zach",
                "speaker_side": "left",
                "camera_motion": "HANDHELD_35MM",
                "cam": "Desperate wide-eyed CU of Zach giving in.",
                "dialogue": "Alright... fine! Heads then! Call it heads, lock it in, and take three giant steps backward away from that magazine rack!",
                "tts": "Alright... fine! Heads then! Call it heads, lock it in, and take three giant steps backward away from that magazine rack!",
            },
            {
                "shot_id": "NC2_15",
                "setup": "NC2_DAMON_CU",
                "start_image": "nc2_damon_cu.jpg",
                "act": 2,
                "speaker": "damon",
                "speaker_side": "right",
                "camera_motion": "SLOW_DOLLY_IN",
                "cam": "Slow measured push-in onto Damon staring down at his own palm on the counter.",
                "dialogue": "Well done. You called heads cleanly... Unfortunately, the quarter landed tails. Keep the change on the receipt.",
                "tts": "Well done. You called heads cleanly... Unfortunately, the quarter landed tails. Keep the change on the receipt.",
            },
            {
                "shot_id": "NC2_16",
                "setup": "NC2_ZACH_CU",
                "start_image": "nc2_zach_cu.jpg",
                "act": 2,
                "speaker": "zach",
                "speaker_side": "left",
                "camera_motion": "STATIC_LOCKED",
                "cam": "Horrified whispered reaction CU of Zach looking down at Damon's knees.",
                "dialogue": "Hold on... you got three seconds on that gasket, man! What is happening under your counter right now?!",
                "tts": "Hold on... you got three seconds on that gasket, man! What is happening under your counter right now?!",
            },
            {
                "shot_id": "NC2_17",
                "setup": "NC2_DAMON_CU",
                "start_image": "nc2_damon_cu.jpg",
                "act": 2,
                "speaker": "damon",
                "speaker_side": "right",
                "camera_motion": "STATIC_LOCKED",
                "cam": "Cold fatalistic pre-eruption beat CU of Damon.",
                "dialogue": "If the rule I followed brought me to this... of what use was the taco?",
                "tts": "If the rule I followed brought me to this... of what use was the taco?",
            },
            {
                "shot_id": "NC2_18",
                "setup": "NC2_CLIMAX_FX",
                "start_image": "nc2_master_wide.jpg",
                "act": 3,
                "speaker": "fx",
                "speaker_side": "center",
                "camera_motion": "STATIC_LOCKED",
                "cam": "Static wide Texaco counter shot: Damon stands utterly deadpan while a catastrophic horizontal torrent of brown diarrhea blasts behind his legs across the dusty store floorboards.",
                "dialogue": "",
                "tts": "",
            },
            {
                "shot_id": "NC2_19",
                "setup": "NC2_ZACH_POST",
                "start_image": "nc2_zach_post.jpg",
                "act": 3,
                "speaker": "zach",
                "speaker_side": "left",
                "camera_motion": "HANDHELD_35MM",
                "cam": "Post-blast MCU on numb Zach slowly sliding pink Pepto across the counter.",
                "dialogue": "You... didn't even blink once. Keep the cashews, keep the twenty bucks, and please don't use my mop bucket on pump two.",
                "tts": "You... didn't even blink once. Keep the cashews, keep the twenty bucks, and please don't use my mop bucket on pump two.",
            },
            {
                "shot_id": "NC2_20",
                "setup": "NC2_DAMON_POST",
                "start_image": "nc2_damon_post.jpg",
                "act": 3,
                "speaker": "damon",
                "speaker_side": "right",
                "camera_motion": "STATIC_LOCKED",
                "cam": "Ice-cold parting CU of Damon adjusting his glasses calmly.",
                "dialogue": "Don't put that quarter in your pocket. Otherwise it gets washed in the sink like everything else. Call it.",
                "tts": "Don't put that quarter in your pocket. Otherwise it gets washed in the sink like everything else. Call it.",
            },
        ],
    }


def main():
    key = load_key()
    script = build_script()
    json.dump(script, open(SCRIPT_PATH, "w"), indent=2)
    print(f"Wrote {SCRIPT_PATH} ({len(script['shots'])} shots)")

    # 1. ElevenLabs dialogue stems
    for s in script["shots"]:
        sid = s["shot_id"]
        out = f"{AUDIO_DIR}/{sid}.mp3"
        if not s["tts"]:
            continue
        sp = s["speaker"]
        gen_tts(sp, s["tts"], out, key)
        print(f"  TTS {sid} ({sp}): {ffprobe_dur(out):.2f}s", flush=True)

    # 2. SFX stems via ElevenLabs Sound Generation
    sfx_defs = [
        ("sfx_nc2_desert_hum.mp3", "Quiet empty West Texas country general store ambience, faint vintage refrigerator buzz, soft dry desert wind outside window, minimal room tone, no music", 8.0),
        ("sfx_nc2_coin_toss.mp3", "Sharp crisp metallic silver quarter coin flip flick and solid wooden checkout counter slap impact, clean studio foley", 2.0),
        ("sfx_nc2_bag_crinkle.mp3", "Dry foil snack wrapper slow crinkle on a quiet wooden store counter, subtle intimate close foley", 2.5),
        ("sfx_nc2_gut_rumble.mp3", "Deep ominous wet stomach gurgle and pressurized bowel groan building sharply inside quiet store, ominous bass foley", 3.5),
        ("sfx_nc2_diarrhea_blast.mp3", "Explosive high-pressure watery mud and liquid torrent blasting violently across wooden floorboards with messy splatter, comedic loud practical sound effect", 4.5),
    ]
    for fn, prompt, dur in sfx_defs:
        p = f"{AUDIO_DIR}/{fn}"
        gen_sfx(prompt, dur, p, key)
        print(f"  SFX {fn}: {ffprobe_dur(p):.2f}s", flush=True)

    # Trim / create placeholder stems for silent LTX shots (NC2_01, NC2_18)
    subprocess.run([
        "ffmpeg", "-y", "-i", f"{AUDIO_DIR}/sfx_nc2_desert_hum.mp3", "-t", "3.50",
        "-af", "afade=t=out:st=3.20:d=0.30", "-c:a", "libmp3lame", "-b:a", "192k", f"{AUDIO_DIR}/NC2_01.mp3"
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run([
        "ffmpeg", "-y", "-i", f"{AUDIO_DIR}/sfx_nc2_diarrhea_blast.mp3", "-t", "3.80",
        "-af", "afade=t=out:st=3.50:d=0.30", "-c:a", "libmp3lame", "-b:a", "192k", f"{AUDIO_DIR}/NC2_18.mp3"
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 3. Radio-Play stitched MP3 for mandatory ear-check BEFORE rendering
    lines = []
    for s in script["shots"]:
        if s["tts"]:
            lines.append(f"file '{AUDIO_DIR}/{s['shot_id']}.mp3'")
    lst = "/tmp/nc2_radio_list.txt"
    open(lst, "w").write("\n".join(lines))
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst,
        "-c:a", "libmp3lame", "-b:a", "192k", "/tmp/nc2_radio_play.mp3"
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"RADIO_PLAY_READY: /tmp/nc2_radio_play.mp3 ({ffprobe_dur('/tmp/nc2_radio_play.mp3'):.2f}s)")

    # 4. Lyria 3.5 two-act continuous Western thriller scores (clean prompts: zero names/director/"crime")
    scores = [
        (
            "score_nc2_act1_desert.mp3",
            "Minimalist desolate West Texas neo-western tension score: sparse dry acoustic baritone guitar notes ringing softly over subtle bowed cello drone and dry desert wind texture, slow unhurried ominous patience, balanced midrange focus, no percussion, no vocals",
        ),
        (
            "score_nc2_act2_coin.mp3",
            "Sparse brooding desert suspense thriller score: dark low steel-string twang, tight bowed cello ostinato pulsing deliberately over faint metallic pocket-watch tick and tense midrange strings building dread, clear mid frequencies, clean stereo depth, no vocals",
        ),
    ]
    for fn, prompt in scores:
        raw = f"/tmp/raw_{fn}"
        out = f"{AUDIO_DIR}/{fn}"
        subprocess.run([
            os.path.expanduser("~/.local/bin/gemini-api"),
            "music", prompt, "-m", "lyria-3.5", "--out", raw
        ], check=True)
        # EQ + peak limiter mastering for clean broadcast compliance
        subprocess.run([
            "ffmpeg", "-y", "-i", raw,
            "-af", "highpass=f=135,equalizer=f=90:t=q:w=1.2:g=-4,equalizer=f=950:t=q:w=1.1:g=2.5,volume=-1.5dB,alimiter=limit=-1.8dB:level=disabled",
            "-c:a", "libmp3lame", "-b:a", "192k", out,
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"  SCORE {fn}: {ffprobe_dur(out):.2f}s", flush=True)


if __name__ == "__main__":
    main()
