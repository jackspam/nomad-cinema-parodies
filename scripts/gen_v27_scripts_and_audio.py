"""Generate canonical v2.7 shot-by-shot scripts, trimmed ElevenLabs dialogue stems, and Radio-Play verification mixes
for all three tight-cast (max 3 characters) films:
  - 03_breaking_bad_v2 (25 shots: Damon, Hooman, Zach)
  - 04_goodfellas_v2   (24 shots: Deron, Ajay, Sheren)
  - 07_matrix_v2       (24 shots: Gigi, Zach, Damon)
"""
import json
import os
import re
import subprocess
import sys

BASE = "/Users/jack/.gemini/antigravity/scratch/nomad-cinema-parodies"
sys.path.insert(0, BASE)
from studio_audio import CAST, gen_tts, load_key


def trim_trailing_silence(mp3_path: str) -> float:
    p = subprocess.run(
        ["ffmpeg", "-i", mp3_path, "-af", "silencedetect=n=-38dB:d=0.20", "-f", "null", "-"],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    dur_m = re.search(r"Duration:\s+(\d+):(\d+):([\d.]+)", p.stderr)
    total = int(dur_m.group(1)) * 3600 + int(dur_m.group(2)) * 60 + float(dur_m.group(3)) if dur_m else 0.0
    starts = [float(x) for x in re.findall(r"silence_start:\s*([0-9.]+)", p.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end:\s*([0-9.]+)", p.stderr)]
    if starts and len(starts) > len(ends):
        cut_at = min(total, starts[-1] + 0.14)
        if total - cut_at > 0.25 and cut_at > 0.8:
            tmp = mp3_path + ".trim.mp3"
            subprocess.run(
                ["ffmpeg", "-y", "-i", mp3_path, "-t", f"{cut_at:.3f}", "-c:a", "libmp3lame", "-q:a", "2", tmp],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            os.replace(tmp, mp3_path)
            return cut_at
    return total


SCRIPTS = {
    "03_breaking_bad_v2": {
        "filename_base": "03_breaking_bad_v2",
        "film_number": "03",
        "title": "Breaking Bad — Say My Name (Brown Meth Deal)",
        "subtitle": "35mm High-Noon New Mexico Desert · Max-3 Cast: Damon, Hooman & Zach",
        "setups": {
            "BB2_WIDE": "High-noon New Mexico desert standoff; older matte-black Chrysler sedan on left beside Damon (Heisenberg black porkpie hat, dark rectangular glasses, black zip jacket) and Zach (olive desert utility jacket beside open trunk stacked with translucent brown meth bags); sleek matte-black SUV on right beside Hooman (black leather jacket, open-collar white dress shirt, carrying gleaming metallic Magic Cone).",
            "BB2_DAMON": "Tight MCU on Damon (Heisenberg: black porkpie hat, dark rectangular glasses, black zip jacket) framed left-center against blazing turquoise New Mexico sky and ochre desert horizon.",
            "BB2_HOOMAN": "Medium close-up on Hooman (black leather jacket over open-collar white dress shirt, carrying gleaming metallic Magic Cone) framed center-right against pale blue desert clouds with black SUV behind.",
            "BB2_ZACH": "Medium close-up on Zach (olive desert utility jacket) framed slightly right beside open black sedan trunk stacked with glistening brown meth ziplocks under harsh desert sun.",
            "BB2_CLIMAX_FX": "Static wide desert practical-FX angle matching BB2_WIDE: Damon standing rigid while a pressurized torrent of thick brown diarrhea blasts violently across the sand, drenching Hooman's Italian loafers and splattering the chrome grille of the black SUV.",
            "BB2_HOOMAN_POST": "Edited from BB2_HOOMAN: shaken Hooman holding the speckled Magic Cone with dark brown splatters across his leather lapel under blinding desert sun."
        },
        "shots": [
            {"shot_id": "BB2_01", "setup": "BB2_WIDE", "start_image": "bb2_master_wide.jpg", "act": 1, "speaker": "fx", "speaker_side": "center", "camera_motion": "STATIC_LOCKED",
             "cam": "Static wide desert establishing standoff beside parked black sedan loaded with brown meth and matte-black SUV; heat shimmer rises off the sand.",
             "dialogue": "", "tts": ""},
            {"shot_id": "BB2_02", "setup": "BB2_HOOMAN", "start_image": "bb2_master_hooman.jpg", "act": 1, "speaker": "hooman", "speaker_side": "center", "camera_motion": "HANDHELD_35MM",
             "cam": "MCU on Hooman squinting smugly under noon desert sun holding gleaming metallic Magic Cone.",
             "dialogue": "Hoobeeee? Chetoreeee, Damon! Why you stand in middle of desert sweating like old yogurt, dood?",
             "tts": "Hoobee? Chetoreee, Damon! Why you stand in middle of desert sweating like old yogurt, dood?"},
            {"shot_id": "BB2_03", "setup": "BB2_DAMON", "start_image": "bb2_master_damon.jpg", "act": 1, "speaker": "damon", "speaker_side": "center", "camera_motion": "STATIC_LOCKED",
             "cam": "Dead-still MCU on Damon in Heisenberg porkpie hat and dark rectangular glasses against turquoise sky.",
             "dialogue": "Cut the small talk, Hooman. You wanted a sit-down on the brown meth. Put your offer on the table.",
             "tts": "[cold, gravelly, ramrod-straight Heisenberg deadpan] Cut the small talk, Hooman. You wanted a sit-down on the brown meth. Put your offer on the table."},
            {"shot_id": "BB2_04", "setup": "BB2_HOOMAN", "start_image": "bb2_master_hooman.jpg", "act": 1, "speaker": "hooman", "speaker_side": "center", "camera_motion": "STATIC_LOCKED",
             "cam": "MCU on Hooman raising the gleaming metallic Magic Cone in sunlight.",
             "dialogue": "Look at this stuff, dood. Ninety-nine percent pure brown meth. Best batch in whole Southwest, and everybody who touch it explode from stomach in twenty minute.",
             "tts": "Look at this stuff, dood. Ninety-nine percent pure brown meth. Best batch in whole Southwest, and everybody who touch it explode from stomach in twenty minute."},
            {"shot_id": "BB2_05", "setup": "BB2_ZACH", "start_image": "bb2_master_zach.jpg", "act": 1, "speaker": "zach", "speaker_side": "center", "camera_motion": "HANDHELD_35MM",
             "cam": "MCU on Zach beside the open black sedan trunk stacked with brown meth crystals, glancing worriedly toward Damon.",
             "dialogue": "Dude, I don't think you realize how pale you look right now. You tested a pinch before your morning Aquabike ride—just hear him out.",
             "tts": "[earnest, worried, urgent boyish tone] Dude, I don't think you realize how pale you look right now. You tested a pinch before your morning Aquabike ride—just hear him out."},
            {"shot_id": "BB2_06", "setup": "BB2_DAMON", "start_image": "bb2_master_damon.jpg", "act": 1, "speaker": "damon", "speaker_side": "center", "camera_motion": "STATIC_LOCKED",
             "cam": "Still MCU on Damon barely blinking beneath his porkpie hat.",
             "dialogue": "Word. I test my own product, Zach. Keeps my Aquabike watts clean from swim exit to bike finish. Hooman, make your pitch.",
             "tts": "[dry, clipped, completely unbothered despite stomach pressure] Word. I test my own product, Zach. Keeps my Aquabike watts clean from swim exit to bike finish. Hooman, make your pitch."},
            {"shot_id": "BB2_07", "setup": "BB2_HOOMAN", "start_image": "bb2_master_hooman.jpg", "act": 1, "speaker": "hooman", "speaker_side": "center", "camera_motion": "HANDHELD_35MM",
             "cam": "MCU on Hooman holding the Magic Cone out like an unpatented miracle device.",
             "dialogue": "Simple, dood. You stop cooking brown meth, sell me whole territory fifty-fifty, and right now I give you Magic Cone. One flush clean whole pipe in sixty second, finish!",
             "tts": "Simple, dood. You stop cooking brown meth, sell me whole territory fifty-fifty, and right now I give you Magic Cone. One flush clean whole pipe in sixty second, finish!"},
            {"shot_id": "BB2_08", "setup": "BB2_DAMON", "start_image": "bb2_master_damon.jpg", "act": 2, "speaker": "damon", "speaker_side": "center", "camera_motion": "STATIC_LOCKED",
             "cam": "Locked Heisenberg CU under blazing desert glare.",
             "dialogue": "Fifty percent of my brown meth operation for a stainless-steel funnel.",
             "tts": "[ice-cold disbelief, flat rhythmic cadence] Fifty percent of my brown meth operation for a stainless-steel funnel."},
            {"shot_id": "BB2_09", "setup": "BB2_HOOMAN", "start_image": "bb2_master_hooman.jpg", "act": 2, "speaker": "hooman", "speaker_side": "center", "camera_motion": "HANDHELD_35MM",
             "cam": "MCU on Hooman gesturing passionately with the Magic Cone.",
             "dialogue": "Dood, fuck that shit dood! Not regular funnel, this Magic Cone! Without Magic Cone, your stomach blow up right before Sunday Aquabike race, whole Malibu beach shut down!",
             "tts": "Dood, fuck that shit dood! Not regular funnel, this Magic Cone! Without Magic Cone, your stomach blow up right before Sunday Aquabike race, whole Malibu beach shut down!"},
            {"shot_id": "BB2_10", "setup": "BB2_ZACH", "start_image": "bb2_master_zach.jpg", "act": 2, "speaker": "zach", "speaker_side": "center", "camera_motion": "STATIC_LOCKED",
             "cam": "MCU on Zach beside open brown-meth trunk, lowering his voice anxiously.",
             "dialogue": "Holy fudge, Damon, your core is literally shaking. Give him thirty percent, take the Magic Cone, and let's get out of this desert.",
             "tts": "[tense, whispered panic] Holy fudge, Damon, your core is literally shaking. Give him thirty percent, take the Magic Cone, and let's get out of this desert."},
            {"shot_id": "BB2_11", "setup": "BB2_DAMON", "start_image": "bb2_master_damon.jpg", "act": 2, "speaker": "damon", "speaker_side": "center", "camera_motion": "STATIC_LOCKED",
             "cam": "Motionless Heisenberg MCU.",
             "dialogue": "Nope. Stay out of it, Zach. Hooman, I trained six months for Aquabike—pure swim and bike, no run, zero margin. You're not taking half my empire.",
             "tts": "[hard, immovable authority] Nope. Stay out of it, Zach. Hooman, I trained six months for Aquabike—pure swim and bike, no run, zero margin. You're not taking half my empire."},
            {"shot_id": "BB2_12", "setup": "BB2_HOOMAN", "start_image": "bb2_master_hooman.jpg", "act": 2, "speaker": "hooman", "speaker_side": "center", "camera_motion": "HANDHELD_35MM",
             "cam": "MCU on Hooman smiling smugly, tilting the Magic Cone forward.",
             "dialogue": "Listen to stomach, brother, sound like busted Porsche transmission! I got buyer in Westwood ready right now. Take Magic Cone, retire from brown meth, go ride little bicycle!",
             "tts": "Listen to stomach, brother, sound like busted Porsche transmission! I got buyer in Westwood ready right now. Take Magic Cone, retire from brown meth, go ride little bicycle!"},
            {"shot_id": "BB2_13", "setup": "BB2_DAMON", "start_image": "bb2_master_damon.jpg", "act": 2, "speaker": "damon", "speaker_side": "center", "camera_motion": "STATIC_LOCKED",
             "cam": "Cold deadpan MCU on Damon under porkpie hat.",
             "dialogue": "Walk back to your SUV and try cooking brown meth yourself tomorrow, Hooman. Without my formula, you've got dirt in a ziplock.",
             "tts": "[calm, ruthless menace] Walk back to your SUV and try cooking brown meth yourself tomorrow, Hooman. Without my formula, you've got dirt in a ziplock."},
            {"shot_id": "BB2_14", "setup": "BB2_HOOMAN", "start_image": "bb2_master_hooman.jpg", "act": 2, "speaker": "hooman", "speaker_side": "center", "camera_motion": "HANDHELD_35MM",
             "cam": "MCU on Hooman leaning slightly forward, wide-eyed.",
             "dialogue": "Dood, fuck that shit dood! Nobody hold back brown meth diarrhea on willpower alone! You got maybe thirty second before pants completely finished!",
             "tts": "Dood, fuck that shit dood! Nobody hold back brown meth diarrhea on willpower alone! You got maybe thirty second before pants completely finished!"},
            {"shot_id": "BB2_15", "setup": "BB2_DAMON", "start_image": "bb2_master_damon.jpg", "act": 2, "speaker": "damon", "speaker_side": "center", "camera_motion": "STATIC_LOCKED",
             "cam": "Ice-still CU on Damon not flinching a millimeter.",
             "dialogue": "Then I guess we're both about to see how strong my core is.",
             "tts": "[low, ominous stillness, utterly unfazed] Then I guess we're both about to see how strong my core is."},
            {"shot_id": "BB2_16", "setup": "BB2_ZACH", "start_image": "bb2_master_zach.jpg", "act": 2, "speaker": "zach", "speaker_side": "center", "camera_motion": "HANDHELD_35MM",
             "cam": "MCU on Zach backing half a pace away from the trunk in dread.",
             "dialogue": "O. m. g., Damon, seriously, step away from the trunk!",
             "tts": "[shrill anxious warning, clearly pronouncing oh em gee] O. m. g., Damon, seriously, step away from the trunk!"},
            {"shot_id": "BB2_17", "setup": "BB2_CLIMAX_FX", "start_image": "bb2_climax_fx.jpg", "act": 3, "speaker": "fx", "speaker_side": "center", "camera_motion": "STATIC_LOCKED",
             "cam": "Static wide desert standoff shot: Damon stands ramrod-straight under his Heisenberg porkpie hat as a catastrophic, pressurized torrent of disgusting brown diarrhea erupts violently across the desert sand onto Hooman's loafers and SUV bumper.",
             "dialogue": "", "tts": ""},
            {"shot_id": "BB2_18", "setup": "BB2_HOOMAN_POST", "start_image": "bb2_hooman_post.jpg", "act": 3, "speaker": "hooman", "speaker_side": "center", "camera_motion": "HANDHELD_35MM",
             "cam": "MCU on splattered, horrified Hooman clutching the useless speckled Magic Cone.",
             "dialogue": "Dood... fuck that shit, dood! My loafers! You... you didn't even bend knee!",
             "tts": "Dood... fuck that shit, dood! My loafers! You... you didn't even bend knee!"},
            {"shot_id": "BB2_19", "setup": "BB2_DAMON", "start_image": "bb2_master_damon.jpg", "act": 3, "speaker": "damon", "speaker_side": "center", "camera_motion": "STATIC_LOCKED",
             "cam": "Serene, utterly unbothered Heisenberg MCU against crisp desert sky.",
             "dialogue": "Facts. System cleared. Race weight locked. My Aquabike bike split just dropped four minutes.",
             "tts": "[relaxed, victorious deadpan] Facts. System cleared. Race weight locked. My Aquabike bike split just dropped four minutes."},
            {"shot_id": "BB2_20", "setup": "BB2_ZACH", "start_image": "bb2_master_zach.jpg", "act": 3, "speaker": "zach", "speaker_side": "center", "camera_motion": "STATIC_LOCKED",
             "cam": "MCU on Zach staring off-screen at the sand wreckage in quiet awe.",
             "dialogue": "Well... guess we don't need the Magic Cone after all.",
             "tts": "[quiet, bewildered awe] Well... guess we don't need the Magic Cone after all."},
            {"shot_id": "BB2_21", "setup": "BB2_DAMON", "start_image": "bb2_master_damon.jpg", "act": 3, "speaker": "damon", "speaker_side": "center", "camera_motion": "STATIC_LOCKED",
             "cam": "Locked Heisenberg MCU; wind brushes faintly beneath motionless glasses.",
             "dialogue": "Your leverage just evaporated, Hooman. Put that cone back in your trunk. You distribute my brown meth—you get twenty percent.",
             "tts": "[commanding, unyielding finale authority] Your leverage just evaporated, Hooman. Put that cone back in your trunk. You distribute my brown meth—you get twenty percent."},
            {"shot_id": "BB2_22", "setup": "BB2_HOOMAN_POST", "start_image": "bb2_hooman_post.jpg", "act": 3, "speaker": "hooman", "speaker_side": "center", "camera_motion": "HANDHELD_35MM",
             "cam": "MCU on intimidated, splattered Hooman under desert haze.",
             "dialogue": "Twenty percent... after that? Dood... who the hell you think you are?",
             "tts": "Twenty percent... after that? Dood... who the hell you think you are?"},
            {"shot_id": "BB2_23", "setup": "BB2_DAMON", "start_image": "bb2_master_damon.jpg", "act": 3, "speaker": "damon", "speaker_side": "center", "camera_motion": "SLOW_DOLLY_IN",
             "cam": "Signature slow closing Heisenberg push-in beneath dark porkpie hat.",
             "dialogue": "You know exactly who I am. I cooked the brown meth, and I'm still making T-one on Sunday. Now... say my name.",
             "tts": "[slow, iconic, terrifying Heisenberg cadence] You know exactly who I am. I cooked the brown meth, and I'm still making T-one on Sunday. Now... say my name."},
            {"shot_id": "BB2_24", "setup": "BB2_HOOMAN_POST", "start_image": "bb2_hooman_post.jpg", "act": 3, "speaker": "hooman", "speaker_side": "center", "camera_motion": "STATIC_LOCKED",
             "cam": "Locked CU on deflated Hooman conceding softly.",
             "dialogue": "...Damon.",
             "tts": "Damon."},
            {"shot_id": "BB2_25", "setup": "BB2_DAMON", "start_image": "bb2_master_damon.jpg", "act": 3, "speaker": "damon", "speaker_side": "center", "camera_motion": "STATIC_LOCKED",
             "cam": "Final razor-still Heisenberg close-up.",
             "dialogue": "You're goddamn right.",
             "tts": "[quiet, lethal certainty] You're goddamn right."},
        ],
    },
    "04_goodfellas_v2": {
        "filename_base": "04_goodfellas_v2",
        "film_number": "04",
        "title": "Goodfellas — Funny How? (Copacabana Booth)",
        "subtitle": "Scorsese 1970s 35mm Nightclub · Max-3 Cast: Deron, Ajay & Sheren",
        "setups": {
            "GF2_WIDE": "1970s Copacabana crimson-velvet VIP booth bathed in glowing red fringed table lamps; Deron centered-left in woven bamboo conical rice paddy hat and ornate red dragon Chinese silk robe holding crystal scotch glass; Ajay right in crisp 1970s ivory dinner jacket & dark tie; Sheren between/beside them in chic 1970s black velvet evening dress.",
            "GF2_DERON": "Crimson-lit Tommy DeVito MCU on Deron wearing woven bamboo conical rice paddy hat (generous headroom above cone tip) and ornate red dragon Chinese silk robe, holding crystal scotch glass under warm red club lamp.",
            "GF2_AJAY": "Henry Hill MCU on Ajay wearing 1970s ivory/cream mob dinner jacket, white dress shirt, dark tie, slicked hair under smoky crimson Copa club lighting.",
            "GF2_SHEREN": "MCU on Sheren wearing chic 1970s black velvet nightclub evening dress and gold earrings beside red fringed Copa lamp.",
            "GF2_CLIMAX_FX": "Static medium-wide Copacabana VIP booth practical-FX shot: Deron sitting ramrod-still under bamboo hat and red dragon robe as a violent torrent of disgusting brown diarrhea blasts from beneath the crimson linen tablecloth across the burgundy carpet and Ajay's cream trousers.",
            "GF2_AJAY_POST": "Edited from GF2_AJAY: stunned, wide-eyed Ajay with brown splatters on his ivory dinner jacket lapel in silent frozen Copa club lighting."
        },
        "shots": [
            {"shot_id": "GF2_01", "setup": "GF2_WIDE", "start_image": "gf2_master_wide.jpg", "act": 1, "speaker": "deron", "speaker_side": "left", "camera_motion": "HANDHELD_35MM",
             "cam": "Warm crimson Copacabana 3-person booth two/three-shot; Deron left in conical bamboo hat & red dragon robe holding court over crystal glass.",
             "dialogue": "Wah, that rival bookie try pay short envelope last night lah! Me walk in back room, take cash, take whole crate off-truck oyster too—show whole neighborhood who boss, right or not?!",
             "tts": "Wah, that rival bookie try pay short envelope last night lah! Me walk in back room, take cash, take whole crate off-truck oyster too—show whole neighborhood who boss, right or not?!"},
            {"shot_id": "GF2_02", "setup": "GF2_WIDE", "start_image": "gf2_master_wide.jpg", "act": 1, "speaker": "fx", "speaker_side": "center", "camera_motion": "STATIC_LOCKED",
             "cam": "Static Copa booth three-shot hold as a loud wet stomach groan rumbles beneath the red tablecloth; Deron keeps stony composure while Ajay glances down.",
             "dialogue": "", "tts": ""},
            {"shot_id": "GF2_03", "setup": "GF2_AJAY", "start_image": "gf2_master_ajay.jpg", "act": 1, "speaker": "ajay", "speaker_side": "center", "camera_motion": "HANDHELD_35MM",
             "cam": "MCU on laughing Ajay in ivory 1970s dinner jacket raising scotch glass fondly.",
             "dialogue": "Arre baap re, Deron! What timing, yaar! Big tough gangster stomach making sound like my nineteen-eighty-four Porsche gearbox! You are total funny guy, yaar!",
             "tts": "Arre baap re, Deron! What timing, yaar! Big tough gangster stomach making sound like my nineteen-eighty-four Porsche gearbox! You are total funny guy, yaar!"},
            {"shot_id": "GF2_04", "setup": "GF2_SHEREN", "start_image": "gf2_master_sheren.jpg", "act": 1, "speaker": "sheren", "speaker_side": "center", "camera_motion": "STATIC_LOCKED",
             "cam": "MCU on Sheren in black velvet evening dress setting her glass down very slowly.",
             "dialogue": "Ajay. Stop talking. Right now.",
             "tts": "[icy, quiet, urgent warning] Ajay. Stop talking. Right now."},
            {"shot_id": "GF2_05", "setup": "GF2_DERON", "start_image": "gf2_master_deron.jpg", "act": 2, "speaker": "deron", "speaker_side": "center", "camera_motion": "STATIC_LOCKED",
             "cam": "Frozen crimson MCU on Deron beneath bamboo hat; background chatter drops DEAD SILENT.",
             "dialogue": "Funny how lah?",
             "tts": "Funny how lah?"},
            {"shot_id": "GF2_06", "setup": "GF2_AJAY", "start_image": "gf2_master_ajay.jpg", "act": 2, "speaker": "ajay", "speaker_side": "center", "camera_motion": "HANDHELD_35MM",
             "cam": "MCU on Ajay chuckling nervously in crimson tungsten light.",
             "dialogue": "Simply—you know what I am saying, yaar! Big shakedown story, then stomach goes boom—it is total amazing comedy, Deron!",
             "tts": "Simply—you know what I am saying, yaar! Big shakedown story, then stomach goes boom—it is total amazing comedy, Deron!"},
            {"shot_id": "GF2_07", "setup": "GF2_DERON", "start_image": "gf2_master_deron.jpg", "act": 2, "speaker": "deron", "speaker_side": "center", "camera_motion": "STATIC_LOCKED",
             "cam": "Dead-still MCU on Deron glaring sharply from beneath bamboo hat.",
             "dialogue": "No, no, me no know. You say funny two time. How me funny ah? Me look like circus clown sit here entertain you while you drink scotch, right or not?",
             "tts": "No, no, me no know. You say funny two time. How me funny ah? Me look like circus clown sit here entertain you while you drink scotch, right or not?"},
            {"shot_id": "GF2_08", "setup": "GF2_SHEREN", "start_image": "gf2_master_sheren.jpg", "act": 2, "speaker": "sheren", "speaker_side": "center", "camera_motion": "STATIC_LOCKED",
             "cam": "MCU on deadpan Sheren lifting her evening clutch off the floor.",
             "dialogue": "Yikes. You just walked straight into a code red, Ajay.",
             "tts": "[flat, sharp, unapologetic realism] Yikes. You just walked straight into a code red, Ajay."},
            {"shot_id": "GF2_09", "setup": "GF2_AJAY", "start_image": "gf2_master_ajay.jpg", "act": 2, "speaker": "ajay", "speaker_side": "center", "camera_motion": "HANDHELD_35MM",
             "cam": "MCU on anxious Ajay pleading with wide eyes.",
             "dialogue": "Negative, Deron! No clown, yaar! Please—I am saying you are eating bad hijacked oyster and sitting so straight like mafia don—it is simply amusing!",
             "tts": "Negative, Deron! No clown, yaar! Please—I am saying you are eating bad hijacked oyster and sitting so straight like mafia don—it is simply amusing!"},
            {"shot_id": "GF2_10", "setup": "GF2_DERON", "start_image": "gf2_master_deron.jpg", "act": 2, "speaker": "deron", "speaker_side": "center", "camera_motion": "SLOW_DOLLY_IN",
             "cam": "Slow ominous Scorsese push-in on Deron in conical bamboo hat & red dragon silk robe.",
             "dialogue": "Amusing ah?! Whole room owe me money, half Brooklyn scared look at red dragon robe, and you think boss stomach is big joke lah?!",
             "tts": "Amusing ah?! Whole room owe me money, half Brooklyn scared look at red dragon robe, and you think boss stomach is big joke lah?!"},
            {"shot_id": "GF2_11", "setup": "GF2_AJAY", "start_image": "gf2_master_ajay.jpg", "act": 2, "speaker": "ajay", "speaker_side": "center", "camera_motion": "STATIC_LOCKED",
             "cam": "MCU on sweating Ajay in clinical doctor panic.",
             "dialogue": "Arre baap re, Deron, look at your face—it is completely grey! Your bowel sounds are total hyperactive—please do the needful and go restroom fast fast!",
             "tts": "Arre baap re, Deron, look at your face—it is completely grey! Your bowel sounds are total hyperactive—please do the needful and go restroom fast fast!"},
            {"shot_id": "GF2_12", "setup": "GF2_DERON", "start_image": "gf2_master_deron.jpg", "act": 2, "speaker": "deron", "speaker_side": "center", "camera_motion": "STATIC_LOCKED",
             "cam": "Locked stony glare under bamboo brim.",
             "dialogue": "Boss no run to toilet in front of whole Copacabana, lah! Nobody leave table until me say finish! Now tell me again—how me funny?!",
             "tts": "Boss no run to toilet in front of whole Copacabana, lah! Nobody leave table until me say finish! Now tell me again—how me funny?!"},
            {"shot_id": "GF2_13", "setup": "GF2_SHEREN", "start_image": "gf2_master_sheren.jpg", "act": 2, "speaker": "sheren", "speaker_side": "center", "camera_motion": "STATIC_LOCKED",
             "cam": "Calm MCU on Sheren leaning cleanly away from center booth.",
             "dialogue": "Relax, Ajay. Don't look at his eyes, and definitely don't sit directly in front of him.",
             "tts": "[cool, dry, calm warning] Relax, Ajay. Don't look at his eyes, and definitely don't sit directly in front of him."},
            {"shot_id": "GF2_14", "setup": "GF2_DERON", "start_image": "gf2_master_deron.jpg", "act": 2, "speaker": "deron", "speaker_side": "center", "camera_motion": "STATIC_LOCKED",
             "cam": "Razor-locked CU on Deron under crimson lamp glow.",
             "dialogue": "You smart doctor, yaar? Big brain surgeon? Explain to whole table right now what so funny about me!",
             "tts": "You smart doctor, yaar? Big brain surgeon? Explain to whole table right now what so funny about me!"},
            {"shot_id": "GF2_15", "setup": "GF2_AJAY", "start_image": "gf2_master_ajay.jpg", "act": 2, "speaker": "ajay", "speaker_side": "center", "camera_motion": "STATIC_LOCKED",
             "cam": "Frozen stiff MCU on terrified Ajay.",
             "dialogue": "Nothing is funny, Deron! Zero percent funny! It is completely serious gangster gastroenteritis and I am making massive mistake!",
             "tts": "Nothing is funny, Deron! Zero percent funny! It is completely serious gangster gastroenteritis and I am making massive mistake!"},
            {"shot_id": "GF2_16", "setup": "GF2_DERON", "start_image": "gf2_master_deron.jpg", "act": 2, "speaker": "deron", "speaker_side": "center", "camera_motion": "STATIC_LOCKED",
             "cam": "Silent three-second freeze broken only by icy whisper.",
             "dialogue": "...Massive mistake.",
             "tts": "Massive mistake."},
            {"shot_id": "GF2_17", "setup": "GF2_AJAY", "start_image": "gf2_master_ajay.jpg", "act": 2, "speaker": "ajay", "speaker_side": "center", "camera_motion": "STATIC_LOCKED",
             "cam": "MCU on frozen Ajay whispering carefully.",
             "dialogue": "Yes, boss. Very massive mistake. Please, Deron—just stand up slow slow.",
             "tts": "Yes, boss. Very massive mistake. Please, Deron—just stand up slow slow."},
            {"shot_id": "GF2_18", "setup": "GF2_DERON", "start_image": "gf2_master_deron.jpg", "act": 2, "speaker": "deron", "speaker_side": "center", "camera_motion": "STATIC_LOCKED",
             "cam": "Ice-still CU on Deron unblinking.",
             "dialogue": "Me no stand up.",
             "tts": "Me no stand up."},
            {"shot_id": "GF2_19", "setup": "GF2_CLIMAX_FX", "start_image": "gf2_climax_fx.jpg", "act": 3, "speaker": "fx", "speaker_side": "center", "camera_motion": "STATIC_LOCKED",
             "cam": "Static medium-wide Copacabana VIP booth shot: Deron keeps stony eye contact beneath his bamboo hat as a pressurized torrent of disgusting brown diarrhea explodes out from beneath the crimson tablecloth across the carpet, table lamp base, and Ajay's ivory slacks.",
             "dialogue": "", "tts": ""},
            {"shot_id": "GF2_20", "setup": "GF2_AJAY_POST", "start_image": "gf2_ajay_post.jpg", "act": 3, "speaker": "ajay", "speaker_side": "center", "camera_motion": "HANDHELD_35MM",
             "cam": "MCU on stunned, brown-splattered Ajay gaping in disbelief.",
             "dialogue": "Arre baap re... my white tuxedo trouser, yaar! You really did not leave the table!",
             "tts": "Arre baap re... my white tuxedo trouser, yaar! You really did not leave the table!"},
            {"shot_id": "GF2_21", "setup": "GF2_SHEREN", "start_image": "gf2_master_sheren.jpg", "act": 3, "speaker": "sheren", "speaker_side": "center", "camera_motion": "STATIC_LOCKED",
             "cam": "Deadpan MCU on completely unfazed Sheren in black velvet dress.",
             "dialogue": "Obviously. He never bluffs.",
             "tts": "[dry, calm, completely unbothered] Obviously. He never bluffs."},
            {"shot_id": "GF2_22", "setup": "GF2_DERON", "start_image": "gf2_master_deron.jpg", "act": 3, "speaker": "deron", "speaker_side": "center", "camera_motion": "STATIC_LOCKED",
             "cam": "Calm MCU on Deron sipping scotch serenely under bamboo hat & red dragon robe.",
             "dialogue": "See? Very serious business lah. Nobody laugh now, right or not?",
             "tts": "See? Very serious business lah. Nobody laugh now, right or not?"},
            {"shot_id": "GF2_23", "setup": "GF2_DERON", "start_image": "gf2_master_deron.jpg", "act": 3, "speaker": "deron", "speaker_side": "center", "camera_motion": "STATIC_LOCKED",
             "cam": "Commanding MCU on Deron setting his scotch glass softly on the table.",
             "dialogue": "Now you pay dinner bill, pay carpet guy, and nobody say one word outside Copacabana, understand ah?",
             "tts": "Now you pay dinner bill, pay carpet guy, and nobody say one word outside Copacabana, understand ah?"},
            {"shot_id": "GF2_24", "setup": "GF2_SHEREN", "start_image": "gf2_master_sheren.jpg", "act": 3, "speaker": "sheren", "speaker_side": "center", "camera_motion": "STATIC_LOCKED",
             "cam": "Closing deadpan smirk on Sheren raising her glass toward waiter.",
             "dialogue": "Bring two more scotches and a mop. And put the dry cleaning on his tab.",
             "tts": "[cool, wicked, deadpan closing verdict] Bring two more scotches and a mop. And put the dry cleaning on his tab."},
        ],
    },
    "07_matrix_v2": {
        "filename_base": "07_matrix_v2",
        "film_number": "07",
        "title": "The Matrix — Prompt Zero (The Red Pill Purge)",
        "subtitle": "1999 Wachowski Emerald-Green 2.39:1 Noir · Max-3 Cast: Gigi (Morpheus), Zach & Damon",
        "setups": {
            "MX2_WIDE": "Symmetrical 1999 Bill Pope emerald-green tinted Lafayette Hotel room; rain sheets down gothic windows; Gigi left seated in cracked burgundy wingback armchair styled directly as Morpheus (black alligator-textured leather trenchcoat, deep purple silk shirt & dark tie, armless round dark pince-nez sunglasses); Zach right hunched sweating in black 1999 wool coat gripping glowing phone; Damon standing motionless by arched rain window in black leather Matrix trenchcoat & rectangular dark glasses.",
            "MX2_GIGI": "Iconic 1999 Morpheus CU matching yt_10: Gigi left-of-center seated in cracked burgundy tufted leather armchair, wearing black alligator-textured leather trenchcoat, deep purple silk shirt & dark tie, armless round dark pince-nez sunglasses, emerald chiaroscuro storm lighting.",
            "MX2_GIGI_PILLS": "Edited directly from MX2_GIGI matching yt_30: Gigi raising both black-gloved hands forward holding glowing red pill (left palm) and cobalt blue pill (right palm) reflected in her round pince-nez lenses.",
            "MX2_ZACH": "Neo MCU matching yt_08: Zach framed right-of-center in rain-damp 1999 black wool coat sweating against shadowed emerald-green hotel wall while gripping glowing smartphone.",
            "MX2_ZACH_REDPILL": "Edited from MX2_ZACH: phone lying face-down on dark side table as Zach lifts the single red pill capsule in storm lightning.",
            "MX2_DAMON": "Trinity-style veteran MCU: Damon in sleek black leather Matrix trenchcoat & dark rectangular glasses standing silently beside rain-streaked gothic window in emerald storm light.",
            "MX2_CLIMAX_FX": "Static emerald-tinted wide Lafayette Hotel practical-FX shot: thunder flashes as a massive, pressurized torrent of disgusting brown diarrhea blasts straight out of Zach's burgundy armchair across the damp hotel carpet and peeling emerald baseboards while Zach grips both armrests rigidly.",
            "MX2_ZACH_POST": "Edited from MX2_ZACH: stunned clear-eyed Zach exhaling softly in emerald storm afterglow with faint dark splatters on background baseboard."
        },
        "shots": [
            {"shot_id": "MX2_01", "setup": "MX2_WIDE", "start_image": "mx2_master_wide.jpg", "act": 1, "speaker": "fx", "speaker_side": "center", "camera_motion": "STATIC_LOCKED",
             "cam": "Symmetrical emerald Lafayette Hotel establishing shot; rain pounds gothic windows as lightning flickers across Gigi (Morpheus), hunched Zach gripping phone, and Damon by window.",
             "dialogue": "", "tts": ""},
            {"shot_id": "MX2_02", "setup": "MX2_GIGI", "start_image": "mx2_master_gigi.jpg", "act": 1, "speaker": "gigi", "speaker_side": "left", "camera_motion": "STATIC_LOCKED",
             "cam": "Cathedral-solemn Morpheus MCU on Gigi in black alligator leather trenchcoat, purple silk tie, and armless pince-nez sunglasses.",
             "dialogue": "Put the phone down, Zach. Look at yourself. You're sweating through your coat, your stomach is tearing itself apart, and you are still asking ChatGPT what to do.",
             "tts": "[deep, serene, cathedral-solemn Morpheus command] Put the phone down, Zach. Look at yourself. You're sweating through your coat, your stomach is tearing itself apart, and you are still asking ChatGPT what to do."},
            {"shot_id": "MX2_03", "setup": "MX2_ZACH", "start_image": "mx2_master_zach.jpg", "act": 1, "speaker": "zach", "speaker_side": "right", "camera_motion": "HANDHELD_35MM",
             "cam": "MCU on sweating Zach staring at glowing phone under green lightning.",
             "dialogue": "Hold on—dude, this is a major deal! I'm typing my exact stomach symptoms into ChatGPT so it can rank my top five probabilities!",
             "tts": "[strained, frantic, boyish ChatGPT dependence] Hold on—dude, this is a major deal! I'm typing my exact stomach symptoms into ChatGPT so it can rank my top five probabilities!"},
            {"shot_id": "MX2_04", "setup": "MX2_GIGI", "start_image": "mx2_master_gigi.jpg", "act": 1, "speaker": "gigi", "speaker_side": "left", "camera_motion": "STATIC_LOCKED",
             "cam": "Unblinking Morpheus MCU on Gigi in pince-nez glasses.",
             "dialogue": "ChatGPT is the reason your intestines are failing, Zach. ChatGPT told you to eat midnight discount sushi. ChatGPT told you to chase it with three scoops of magnesium citrate.",
             "tts": "[measured, lethal, hypnotic Morpheus cadence] ChatGPT is the reason your intestines are failing, Zach. ChatGPT told you to eat midnight discount sushi. ChatGPT told you to chase it with three scoops of magnesium citrate."},
            {"shot_id": "MX2_05", "setup": "MX2_ZACH", "start_image": "mx2_master_zach.jpg", "act": 1, "speaker": "zach", "speaker_side": "right", "camera_motion": "HANDHELD_35MM",
             "cam": "Defensive MCU on Zach holding phone up urgently.",
             "dialogue": "It gave me a structured optimization protocol, Gigi! With bullet points! I can't just make a medical move without sending it to ChatGPT first!",
             "tts": "[defensive, earnest frustration] It gave me a structured optimization protocol, Gigi! With bullet points! I can't just make a medical move without sending it to ChatGPT first!"},
            {"shot_id": "MX2_06", "setup": "MX2_DAMON", "start_image": "mx2_master_damon.jpg", "act": 1, "speaker": "damon", "speaker_side": "center", "camera_motion": "STATIC_LOCKED",
             "cam": "Cold 1999 noir MCU on Damon by rain-lashed window in black leather Matrix coat.",
             "dialogue": "Word. Fifty-six miles into an Aquabike—open-water swim straight into the aero tuck, no run. When your gut turns in fifty-four-degree water, there's no ChatGPT in your wetsuit, Zach. You make a call or you sink.",
             "tts": "[ice-cold veteran deadpan] Word. Fifty-six miles into an Aquabike—open-water swim straight into the aero tuck, no run. When your gut turns in fifty-four-degree water, there's no ChatGPT in your wetsuit, Zach. You make a call or you sink."},
            {"shot_id": "MX2_07", "setup": "MX2_ZACH", "start_image": "mx2_master_zach.jpg", "act": 1, "speaker": "zach", "speaker_side": "right", "camera_motion": "HANDHELD_35MM",
             "cam": "MCU on hunched Zach shivering as storm rain drums on glass.",
             "dialogue": "Holy fudge, Damon, easy for you to say—you're an Aquabike cyborg! Let me just prompt ChatGPT to see if this cramp is urgent or just detox, lol!",
             "tts": "[pained, sweating, desperately saying lol casually] Holy fudge, Damon, easy for you to say—you're an Aquabike cyborg! Let me just prompt ChatGPT to see if this cramp is urgent or just detox, lol!"},
            {"shot_id": "MX2_08", "setup": "MX2_GIGI", "start_image": "mx2_master_gigi.jpg", "act": 2, "speaker": "gigi", "speaker_side": "left", "camera_motion": "STATIC_LOCKED",
             "cam": "Still Morpheus MCU; storm lightning flashes faintly over Gigi's sunglasses.",
             "dialogue": "You are living inside a polite prison, Zach. A prison for your mind, and your colon. Every meal, every reply, every trip to the bathroom, outsourced to a prompt box.",
             "tts": "[deep, devastating Morpheus prophecy] You are living inside a polite prison, Zach. A prison for your mind, and your colon. Every meal, every reply, every trip to the bathroom, outsourced to a prompt box."},
            {"shot_id": "MX2_09", "setup": "MX2_ZACH", "start_image": "mx2_master_zach.jpg", "act": 2, "speaker": "zach", "speaker_side": "right", "camera_motion": "STATIC_LOCKED",
             "cam": "Breathless MCU on Zach staring helplessly at phone screen.",
             "dialogue": "Wait, ChatGPT is still generating... o. m. g., it says I should monitor discomfort and hydrate mindfully!",
             "tts": "[breathless panic, pronouncing oh em gee] Wait, ChatGPT is still generating... o. m. g., it says I should monitor discomfort and hydrate mindfully!"},
            {"shot_id": "MX2_10", "setup": "MX2_DAMON", "start_image": "mx2_master_damon.jpg", "act": 2, "speaker": "damon", "speaker_side": "center", "camera_motion": "STATIC_LOCKED",
             "cam": "MCU on razor-calm Damon framed in green hotel lamp shadow.",
             "dialogue": "Your body is screaming at you in plain English, and you're waiting on a chatbot to write you a summary.",
             "tts": "[flat, surgical deadpan] Your body is screaming at you in plain English, and you're waiting on a chatbot to write you a summary."},
            {"shot_id": "MX2_11", "setup": "MX2_ZACH", "start_image": "mx2_master_zach.jpg", "act": 2, "speaker": "zach", "speaker_side": "right", "camera_motion": "HANDHELD_35MM",
             "cam": "MCU on cornered Zach trembling slightly.",
             "dialogue": "I literally don't know what to do if I don't ask ChatGPT! What if I make the wrong decision?!",
             "tts": "[raw helpless panic] I literally don't know what to do if I don't ask ChatGPT! What if I make the wrong decision?!"},
            {"shot_id": "MX2_12", "setup": "MX2_GIGI_PILLS", "start_image": "mx2_gigi_pills.jpg", "act": 2, "speaker": "gigi", "speaker_side": "left", "camera_motion": "STATIC_LOCKED",
             "cam": "Iconic dual-pill Morpheus shot matching yt_30: Gigi raises both black leather gloves holding glowing blue & red pills reflected in her round pince-nez.",
             "dialogue": "This is your last chance, Zach. After this, there is no turning back.",
             "tts": "[slow, velvety, monumental Morpheus ultimatum] This is your last chance, Zach. After this, there is no turning back."},
            {"shot_id": "MX2_13", "setup": "MX2_GIGI_PILLS", "start_image": "mx2_gigi_pills.jpg", "act": 2, "speaker": "gigi", "speaker_side": "left", "camera_motion": "STATIC_LOCKED",
             "cam": "Held Morpheus pill frame tilting softly toward the blue capsule.",
             "dialogue": "You take the blue pill, the story ends. It numbs your stomach, you go home, and tomorrow morning you ask ChatGPT what to eat for breakfast all over again.",
             "tts": "[calm hypnotic clarity] You take the blue pill, the story ends. It numbs your stomach, you go home, and tomorrow morning you ask ChatGPT what to eat for breakfast all over again."},
            {"shot_id": "MX2_14", "setup": "MX2_GIGI_PILLS", "start_image": "mx2_gigi_pills.jpg", "act": 2, "speaker": "gigi", "speaker_side": "left", "camera_motion": "SLOW_DOLLY_IN",
             "cam": "Slow measured Morpheus push-in highlighting the glowing crimson red capsule.",
             "dialogue": "You take the red pill, you stay in Wonderland. We log you out of ChatGPT forever, and your body purges every single lie that algorithm ever fed you.",
             "tts": "[deep ominous promise] You take the red pill, you stay in Wonderland. We log you out of ChatGPT forever, and your body purges every single lie that algorithm ever fed you."},
            {"shot_id": "MX2_15", "setup": "MX2_DAMON", "start_image": "mx2_master_damon.jpg", "act": 2, "speaker": "damon", "speaker_side": "center", "camera_motion": "STATIC_LOCKED",
             "cam": "Still MCU on Damon in black Matrix trenchcoat.",
             "dialogue": "Think carefully, Zach. Just like mile forty on an Aquabike course—once you commit, there's no undo button.",
             "tts": "[grave, crisp warning] Think carefully, Zach. Just like mile forty on an Aquabike course—once you commit, there's no undo button."},
            {"shot_id": "MX2_16", "setup": "MX2_ZACH", "start_image": "mx2_master_zach.jpg", "act": 2, "speaker": "zach", "speaker_side": "right", "camera_motion": "HANDHELD_35MM",
             "cam": "MCU on panicking Zach trying to lift his phone one last time.",
             "dialogue": "Okay, fudge, give me five seconds! Let me just ask ChatGPT whether red or blue has better side-effect reviews!",
             "tts": "[frantic, trembling plea] Okay, fudge, give me five seconds! Let me just ask ChatGPT whether red or blue has better side-effect reviews!"},
            {"shot_id": "MX2_17", "setup": "MX2_GIGI", "start_image": "mx2_master_gigi.jpg", "act": 2, "speaker": "gigi", "speaker_side": "left", "camera_motion": "STATIC_LOCKED",
             "cam": "Ice-still Morpheus MCU.",
             "dialogue": "No ChatGPT. No prompts. No summaries. Decide for yourself.",
             "tts": "[soft, absolute, unbreakable command] No ChatGPT. No prompts. No summaries. Decide for yourself."},
            {"shot_id": "MX2_18", "setup": "MX2_ZACH_REDPILL", "start_image": "mx2_zach_redpill.jpg", "act": 3, "speaker": "zach", "speaker_side": "right", "camera_motion": "STATIC_LOCKED",
             "cam": "MCU on Zach with phone lying face-down on table beside him as he grips the red pill.",
             "dialogue": "...Fine. No ChatGPT. Give me the red pill.",
             "tts": "[quiet, shaking resolve] Fine. No ChatGPT. Give me the red pill."},
            {"shot_id": "MX2_19", "setup": "MX2_ZACH_REDPILL", "start_image": "mx2_zach_redpill.jpg", "act": 3, "speaker": "fx", "speaker_side": "right", "camera_motion": "STATIC_LOCKED",
             "cam": "Close action beat: Zach tosses the red capsule into his mouth and swallows hard as green storm lightning illuminates his face.",
             "dialogue": "", "tts": ""},
            {"shot_id": "MX2_20", "setup": "MX2_CLIMAX_FX", "start_image": "mx2_climax_fx.jpg", "act": 3, "speaker": "fx", "speaker_side": "center", "camera_motion": "STATIC_LOCKED",
             "cam": "Static wide emerald Lafayette Hotel shot: thunder slams the arched windows as a catastrophic, pressurized torrent of disgusting brown diarrhea explodes straight out of Zach's burgundy armchair across the damp carpet and peeling green wallpaper while Zach grips both armrests in stoic silence.",
             "dialogue": "", "tts": ""},
            {"shot_id": "MX2_21", "setup": "MX2_DAMON", "start_image": "mx2_master_damon.jpg", "act": 3, "speaker": "damon", "speaker_side": "center", "camera_motion": "STATIC_LOCKED",
             "cam": "Motionless MCU on Damon by rain-lashed window giving a tiny approving nod.",
             "dialogue": "Facts. Cleaner transition than my last Aquabike T-one.",
             "tts": "[calm, impressed deadpan] Facts. Cleaner transition than my last Aquabike T-one."},
            {"shot_id": "MX2_22", "setup": "MX2_ZACH_POST", "start_image": "mx2_zach_post.jpg", "act": 3, "speaker": "zach", "speaker_side": "right", "camera_motion": "STATIC_LOCKED",
             "cam": "MCU on wide-eyed, liberated Zach exhaling quietly in the storm afterglow.",
             "dialogue": "Holy fudge... I didn't ask ChatGPT. Not even once.",
             "tts": "[stunned, exhausted, quiet wonder] Holy fudge... I didn't ask ChatGPT. Not even once."},
            {"shot_id": "MX2_23", "setup": "MX2_GIGI", "start_image": "mx2_master_gigi.jpg", "act": 3, "speaker": "gigi", "speaker_side": "left", "camera_motion": "STATIC_LOCKED",
             "cam": "Serene Morpheus MCU as lightning glints softly across pince-nez lenses.",
             "dialogue": "Because for the first time in years... you trusted your own gut, Zach.",
             "tts": "[serene, warm, triumphant Morpheus clarity] Because for the first time in years... you trusted your own gut, Zach."},
            {"shot_id": "MX2_24", "setup": "MX2_GIGI", "start_image": "mx2_master_gigi.jpg", "act": 3, "speaker": "gigi", "speaker_side": "left", "camera_motion": "STATIC_LOCKED",
             "cam": "Closing Morpheus CU under rolling emerald storm clouds.",
             "dialogue": "Welcome to the real world. Now stand up—we're burning that chair.",
             "tts": "[measured, dryly triumphant finale] Welcome to the real world. Now stand up—we're burning that chair."},
        ],
    },
}


def main():
    key = load_key()
    for slug, data in SCRIPTS.items():
        s_path = f"{BASE}/scripts/{slug}_script.json"
        json.dump(data, open(s_path, "w"), indent=2)
        au_dir = f"{BASE}/audio/{slug}"
        os.makedirs(au_dir, exist_ok=True)
        print(f"=== WROTE {s_path} ({len(data['shots'])} shots) ===", flush=True)

        dialogue_mp3s = []
        tot = 0.0
        for sh in data["shots"]:
            sid = sh["shot_id"]
            spk = sh["speaker"]
            out_mp3 = f"{au_dir}/{sid}.mp3"
            if spk == "fx":
                continue
            if not os.path.exists(out_mp3) or os.path.getsize(out_mp3) < 1000:
                gen_tts(spk, sh["tts"], out_mp3, key)
            dur = trim_trailing_silence(out_mp3)
            tot += dur
            dialogue_mp3s.append(out_mp3)
            print(f"  [{sid}] {spk:6s} dur={dur:.2f}s | {sh['dialogue'][:65]}", flush=True)

        # Build continuous Radio-Play MP3 with 0.30s gaps for human listening QA
        radio_out = f"/tmp/radio_{slug}.mp3"
        sil_wav = f"/tmp/_sil_{slug}.wav"
        subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "0.30", sil_wav],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        inputs = []
        fc_parts = []
        idx = 0
        for i, mp3 in enumerate(dialogue_mp3s):
            inputs += ["-i", mp3]
            fc_parts.append(f"[{idx}:a]aresample=44100,aformat=channel_layouts=mono,loudnorm=I=-16:TP=-1.5:LRA=11[a{i}];")
            idx += 1
            if i < len(dialogue_mp3s) - 1:
                inputs += ["-i", sil_wav]
                fc_parts.append(f"[{idx}:a]aformat=channel_layouts=mono[s{i}];")
                idx += 1
        concat_list = "".join(f"[a{i}]" + (f"[s{i}]" if i < len(dialogue_mp3s) - 1 else "") for i in range(len(dialogue_mp3s)))
        fc = "".join(fc_parts) + f"{concat_list}concat=n={len(dialogue_mp3s)*2 - 1}:v=0:a=1[out]"
        subprocess.run(["ffmpeg", "-y", *inputs, "-filter_complex", fc, "-map", "[out]", "-c:a", "libmp3lame", "-q:a", "3", radio_out],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.remove(sil_wav)
        print(f"RADIO_PLAY_READY {radio_out} (dialogue sum={tot:.1f}s across {len(dialogue_mp3s)} tracks)", flush=True)


if __name__ == "__main__":
    main()
