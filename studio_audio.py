import json
import os
import re
import urllib.request

CAST = {
    "damon": {
        "voice_id": "aaNMql2UhMtHkuPocdpu",
        "model_id": "eleven_v4_turbo",
        "settings": {"stability": 0.36, "similarity_boost": 0.85, "style": 0.60, "use_speaker_boost": True},
    },
    "zach": {
        "voice_id": "wIcsWQVRxZU3MzAyBlyG",
        "model_id": "eleven_v4_turbo",
        "settings": {"stability": 0.40, "similarity_boost": 0.85, "style": 0.55, "use_speaker_boost": True},
    },
    "sheren": {
        "voice_id": "54Cze5LrTSyLgbO6Fhlc",
        "model_id": "eleven_v4_turbo",
        "settings": {"stability": 0.30, "similarity_boost": 0.82, "style": 0.65, "use_speaker_boost": True},
    },
    "gigi": {
        "voice_id": "8fwYhwfiWkLjR4FKLHSQ",
        "model_id": "eleven_v4_turbo",
        "settings": {"stability": 0.35, "similarity_boost": 0.85, "style": 0.65, "use_speaker_boost": True},
    },
    "deron": {
        "voice_id": "8ICpLIG0QgIrxptKb54Y",
        "model_id": "eleven_multilingual_v2",
        "plain": True,
        "settings": {"stability": 0.12, "similarity_boost": 0.70, "style": 0.90, "speed": 1.12, "use_speaker_boost": True},
    },
    "hooman": {
        "voice_id": "81njo0eNJYbZUuCsv0DL",
        "model_id": "eleven_multilingual_v2",
        "plain": True,
        "settings": {"stability": 0.34, "similarity_boost": 0.92, "style": 0.76, "speed": 0.94, "use_speaker_boost": True},
    },
    "ajay": {
        "voice_id": "D83oVuoTV1UdYxASEwXo",
        "model_id": "eleven_multilingual_v2",
        "plain": True,
        "settings": {"stability": 0.28, "similarity_boost": 0.85, "style": 0.70, "speed": 1.04, "use_speaker_boost": True},
    },
    "villain": {
        "voice_id": "ybjoxm7ASLDUFh2pC2eM",
        "model_id": "eleven_v4_turbo",
        "settings": {"stability": 0.45, "similarity_boost": 0.85, "style": 0.50, "use_speaker_boost": True},
    },
    "trooper": {
        "voice_id": "cjVigY5qzO86Huf0OWal",
        "model_id": "eleven_v4_turbo",
        "settings": {"stability": 0.50, "similarity_boost": 0.80, "style": 0.40, "use_speaker_boost": True},
    },
    "joker": {
        "voice_id": "Uk6eYbU4r5zMY9PINcHP",
        "model_id": "eleven_v4_turbo",
        "settings": {"stability": 0.16, "similarity_boost": 0.85, "style": 0.92, "use_speaker_boost": True},
    },
    "walter": {
        "voice_id": "X4vZcFRLktMRyjtw02rv",
        "model_id": "eleven_v4_turbo",
        "settings": {"stability": 0.30, "similarity_boost": 0.85, "style": 0.78, "use_speaker_boost": True},
    },
    "gus": {
        "voice_id": "Solf0V1aX6Q3S0ishkdH",
        "model_id": "eleven_v4_turbo",
        "settings": {"stability": 0.55, "similarity_boost": 0.85, "style": 0.45, "use_speaker_boost": True},
    },
    "tommy": {
        "voice_id": "S3Tx0ZjaAEPNL7jm1vbu",
        "model_id": "eleven_v4_turbo",
        "settings": {"stability": 0.18, "similarity_boost": 0.85, "style": 0.92, "use_speaker_boost": True},
    },
    "jules": {
        "voice_id": "dvOBTt324r2rsqu6y4HI",
        "model_id": "eleven_v4_turbo",
        "settings": {"stability": 0.20, "similarity_boost": 0.85, "style": 0.92, "use_speaker_boost": True},
    },
    "morpheus": {
        "voice_id": "4nZS5FZSTamJ3UQIG5gx",
        "model_id": "eleven_v4_turbo",
        "settings": {"stability": 0.42, "similarity_boost": 0.85, "style": 0.65, "use_speaker_boost": True},
    },
    "hammond": {
        "voice_id": "pqHfZKP75CvOlQylNhV4",
        "model_id": "eleven_v4_turbo",
        "settings": {"stability": 0.45, "similarity_boost": 0.85, "style": 0.55, "use_speaker_boost": True},
    },
    "gordon": {
        "voice_id": "pNInz6obpgDQGcFmaJgB",
        "model_id": "eleven_v4_turbo",
        "settings": {"stability": 0.50, "similarity_boost": 0.85, "style": 0.45, "use_speaker_boost": True},
    },
}


def load_key():
    env_text = open(os.path.expanduser("~/.gemini/antigravity/scratch/abyss/.env.local")).read()
    m = re.search(r'^\s*(?:export\s+)?ELEVENLABS_API_KEY\s*=\s*["\']?([^"\'\s#]+)', env_text, re.M)
    if not m:
        raise RuntimeError("ELEVENLABS_API_KEY not found")
    return m.group(1)


def gen_tts(speaker: str, text: str, out_path: str, key: str):
    cfg = CAST[speaker]
    clean_text = text
    if cfg.get("plain"):
        clean_text = re.sub(r"\s*\[[^\]]+\]\s*", " ", clean_text).strip()
    payload = {
        "text": clean_text,
        "model_id": cfg["model_id"],
        "voice_settings": cfg["settings"],
    }
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{cfg['voice_id']}",
        data=json.dumps(payload).encode(),
        headers={"xi-api-key": key, "Content-Type": "application/json", "Accept": "audio/mpeg"},
    )
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with urllib.request.urlopen(req, timeout=45) as r:
        open(out_path, "wb").write(r.read())
    print(f"TTS [{speaker}] -> {out_path} ({os.path.getsize(out_path)} bytes)")


def gen_sfx(prompt: str, duration: float, out_path: str, key: str, influence: float = 0.45):
    payload = {"text": prompt, "duration_seconds": duration, "prompt_influence": influence}
    req = urllib.request.Request(
        "https://api.elevenlabs.io/v1/sound-generation",
        data=json.dumps(payload).encode(),
        headers={"xi-api-key": key, "Content-Type": "application/json", "Accept": "audio/mpeg"},
    )
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with urllib.request.urlopen(req, timeout=60) as r:
        open(out_path, "wb").write(r.read())
    print(f"SFX ({duration}s) -> {out_path} ({os.path.getsize(out_path)} bytes)")
