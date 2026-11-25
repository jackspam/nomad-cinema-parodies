import os
import sys

sys.path.insert(0, os.path.expanduser("~/.gemini/antigravity/scratch/nomad-cinema-parodies"))
from studio_audio import gen_sfx, gen_tts, load_key

OUT_DIR = os.path.expanduser("~/.gemini/antigravity/scratch/nomad-cinema-parodies/audio/01_star_wars")


def main():
    key = load_key()

    lines = [
        ("vader_01", "villain", "I find your lack of bowel control... disturbing. Seal the blast doors."),
        ("damon_02", "damon", "[dry, deadpan dread, straining] Vader... that Mos Eisley cantina burrito was a trap. Clear the detention block."),
        ("gigi_03", "gigi", "[harsh kindergarten teacher authority] Inside voices! Both of you! Lord Vader, line leader goes last, and nobody uses the Death Star refresher until we finish attendance."),
        ("deron_04", "deron", "Aiya! Gigi la, this Death Star corridor colder than San Gabriel freezer! Even Din Tai Fung soup dumpling has better ventilation, good or not?"),
        ("zach_05", "zach", "[calm, earnest, slightly worried] Dude, I asked ChatGPT and it said we should hydrate, plus I'm checking X—wait, Elon's hyperdrive design is literally cleaner than this Imperial garbage, also did anyone water my olive trees on Tatooine?"),
        ("gigi_06", "gigi", "[furious, snapping] Do NOT say Elon Musk on my bridge, Zachary! Sit down!"),
        ("hooman_07", "hooman", "Chee-chee-chettore! Damon, baba, you have diarrhea again? Big like Death Star, dood! Listen to Hooman—stand-up Magic Cone! Fifty-fifty on the Cone, huuuuh?"),
        ("gigi_08", "gigi", "[disgusted, sharp] Turn off that hologram! I am NOT using your cone, Hooman!"),
        ("ajay_09", "ajay", "Calm down, Damon. This intestinal crisis is purely neurological. Hold still, I will perform deep brain stimulation right here in the corridor."),
        ("deron_10", "deron", "Wah, Ajay! No brain surgery before dim sum la! Look at Damon—moving faster than Jeremy Lin in the fourth quarter! BLACKPINK in your area!"),
        ("damon_11", "damon", "[straining, urgent whisper] Too late... the Force is... leaving my body."),
        ("sheren_12", "sheren", "[manic, fast, impatient] Get in the Falcon, losers! No brakes! I am punching it to lightspeed right now!"),
    ]

    for lid, speaker, text in lines:
        gen_tts(speaker, text, os.path.join(OUT_DIR, f"{lid}.mp3"), key)

    sfx_list = [
        ("score_sw_imperial.mp3", 25.0, "Sweeping 1977 sci-fi orchestral brass and strings fanfare, ominous imperial march tension in a vast hangar, classic cinema score, no vocals"),
        ("sfx_vader_breath.mp3", 8.0, "Slow heavy mechanical respirator breathing inside a dark metallic helmet, subtle starship engine hum"),
        ("sfx_blaster_doors.mp3", 8.0, "Sci-fi pneumatic blast doors hissing shut, laser blaster bolts ricocheting off steel walls, echoing corridor alarms"),
        ("sfx_falcon_hyperdrive.mp3", 8.0, "Spaceship hyperdrive engines roaring to life with futuristic turbine whine and dramatic sci-fi whoosh"),
    ]

    for fname, dur, prompt in sfx_list:
        gen_sfx(prompt, dur, os.path.join(OUT_DIR, fname), key)


if __name__ == "__main__":
    main()
