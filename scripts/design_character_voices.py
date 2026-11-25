import json
import os
import sys
import urllib.request
import urllib.error

sys.path.insert(0, "/Users/jack/.gemini/antigravity/scratch/nomad-cinema-parodies")
import studio_audio

CHARACTERS = [
    (
        "joker",
        "Theatrical Raspy Baritone",
        "Male voice in his early 30s, crisp American accent, gravelly raspy baritone-tenor with slight nasal pinch, occasional playful upward pitch inflections, light vocal fry on low notes, and unhurried dramatic pacing.",
        "Good evening, Commissioner. You brought a rather serious detective in a heavy cape tonight, and an associate wearing a red silk robe. Tell me, do I really look like someone with a spreadsheet?",
    ),
    (
        "walter",
        "Dry Authoritative Baritone",
        "Male voice in his early 50s, dry American baritone, tight focused chest resonance, crisp deliberate consonant enunciation, low gravelly texture, and calm steady cadence dropping softly at sentence ends.",
        "You know very well who is standing in front of you. We have a straightforward business arrangement in this desert, and I expect everyone at this meeting to listen very carefully.",
    ),
    (
        "gus",
        "Calm Measured Chilean-American",
        "Male voice in his late 40s, subtle refined Chilean-American accent, razor-precise clipped articulation, cool level emotional tone, polite warm baritone, and slow measured pauses between phrases.",
        "A conscientious proprietor pays attention to every detail in broad daylight. Customer service requires courtesy, patience, and complete composure at all times, even under unusual circumstances.",
    ),
    (
        "tommy",
        "Brooklyn 70s Fast Tenor",
        "Male voice in his late 30s, energetic 1970s Brooklyn New York Italian-American tenor-baritone, sharp nasal edge, brisk staccato rhythm, expressive animated emphasis, and gritty raspy punch on stressed words.",
        "What do you mean funny? Funny how, like I am here to tell jokes for the whole table? Tell me specifically what part of my story sounded funny to you right this second.",
    ),
    (
        "jules",
        "Booming Rhythmic Preacher Baritone",
        "Male voice in his mid-40s, deep powerful African-American baritone, rich chest resonance, charismatic oratorical rhythm, strong dynamic contrast, and crisp dramatic pauses before key words.",
        "Look at the clock on the wall. It is seven twenty-two in the morning, and we came to have a very serious conversation about breakfast, punctuality, and the contents of that silver briefcase.",
    ),
    (
        "morpheus",
        "Deep Velvety Bass Baritone",
        "Male voice in his early 40s, deep smooth velvety African-American bass-baritone, slow rhythmic theatrical legato, warm chest resonance, and calm steady philosophical authority.",
        "This is your final moment to choose. On one hand sits the comfortable story you already know. On the other hand lies an uncomfortable truth that will change how you see everything.",
    ),
]


def post_json(url, payload, key):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"xi-api-key": key, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code} on {url}: {e.read().decode()[:400]}")
        raise


def main():
    key = studio_audio.load_key()
    out_ids = {}
    for slug, name, desc, sample_text in CHARACTERS:
        print(f"Designing voice: {name}...", flush=True)
        res = post_json(
            "https://api.elevenlabs.io/v1/text-to-voice/create-previews",
            {"voice_description": desc, "text": sample_text},
            key,
        )
        previews = res.get("previews", [])
        if not previews:
            print(f"  No previews for {slug}")
            continue
        gen_id = previews[0]["generated_voice_id"]
        created = post_json(
            "https://api.elevenlabs.io/v1/text-to-voice/create-voice-from-preview",
            {
                "voice_name": name,
                "voice_description": desc,
                "generated_voice_id": gen_id,
            },
            key,
        )
        vid = created["voice_id"]
        out_ids[slug] = vid
        print(f"  CREATED {slug} -> {vid}", flush=True)

    out_path = "/Users/jack/.gemini/antigravity/scratch/nomad-cinema-parodies/scripts/designed_voices.json"
    json.dump(out_ids, open(out_path, "w"), indent=2)
    print("ALL_VOICES_DESIGNED:", json.dumps(out_ids))


if __name__ == "__main__":
    main()
