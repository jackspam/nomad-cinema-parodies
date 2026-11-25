import json
import subprocess
import sys
import time
import urllib.request

COMFY_URL = "http://127.0.0.1:8188"


def ensure_comfyui(timeout=120):
    try:
        with urllib.request.urlopen(f"{COMFY_URL}/system_stats", timeout=2) as r:
            if r.status == 200:
                return
    except Exception:
        pass
    print("Starting ComfyUI...", flush=True)
    logf = open("/content/comfyui.log", "w")
    subprocess.Popen(
        ["python3", "main.py", "--listen", "127.0.0.1", "--port", "8188"],
        cwd="/content/ComfyUI",
        stdout=logf,
        stderr=subprocess.STDOUT,
    )
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{COMFY_URL}/system_stats", timeout=2) as r:
                if r.status == 200:
                    return
        except Exception:
            pass
        time.sleep(2)
    raise RuntimeError("ComfyUI did not start in time")


def post_prompt(prompt_graph):
    data = json.dumps({"prompt": prompt_graph}).encode()
    req = urllib.request.Request(
        f"{COMFY_URL}/prompt",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def wait_for_history(prompt_id, timeout=1800):
    deadline = time.time() + timeout
    while time.time() < deadline:
        with urllib.request.urlopen(f"{COMFY_URL}/history/{prompt_id}", timeout=15) as r:
            hist = json.loads(r.read())
        if prompt_id in hist:
            entry = hist[prompt_id]
            status = entry.get("status", {})
            if status.get("status_str") == "error":
                print("EXEC ERROR:", json.dumps(status, indent=2), file=sys.stderr)
                raise RuntimeError("ComfyUI execution failed")
            if entry.get("outputs"):
                return entry
        time.sleep(4)
    raise TimeoutError(f"Prompt {prompt_id} timed out")


def build_graph(
    *,
    face_image: str | None,
    shot_image: str,
    ref_audio: str | None,
    prompt_text: str,
    prefix: str,
    seed: int,
    length: int = 192,
    steps: int = 4,
    width: int = 1344,
    height: int = 768,
):
    g = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "minimax_h3_ref2va_pruned_int8_convrot.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["1", 0], "lora_name": "minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors", "strength_model": 1.0}},
        "3": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors", "type": "minimax", "device": "default"}},
        "4": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_video_vae_int8_convrot.safetensors"}},
        "5": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_audio_vae_fp32.safetensors"}},
        "18": {"class_type": "LoadImage", "inputs": {"image": shot_image}},
        "8": {
            "class_type": "MiniMaxH3ReferenceToVideo",
            "inputs": {
                "clip": ["3", 0],
                "vae": ["4", 0],
                "audio_vae": ["5", 0],
                "prompt": prompt_text,
                "width": width,
                "height": height,
                "length": length,
                "ref_image_size": "match",
            },
        },
        "9": {"class_type": "BasicGuider", "inputs": {"model": ["2", 0], "conditioning": ["8", 0]}},
        "10": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "res_multistep"}},
        "11": {"class_type": "BasicScheduler", "inputs": {"model": ["2", 0], "scheduler": "simple", "steps": steps, "denoise": 1.0}},
        "12": {"class_type": "RandomNoise", "inputs": {"noise_seed": seed}},
        "13": {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": ["12", 0], "guider": ["9", 0], "sampler": ["10", 0], "sigmas": ["11", 0], "latent_image": ["8", 1]}},
        "14": {"class_type": "VAEDecode", "inputs": {"samples": ["13", 0], "vae": ["4", 0]}},
        "15": {"class_type": "VAEDecodeAudio", "inputs": {"samples": ["13", 0], "vae": ["5", 0]}},
        "16": {"class_type": "CreateVideo", "inputs": {"images": ["14", 0], "audio": ["15", 0], "fps": 24}},
        "17": {"class_type": "SaveVideo", "inputs": {"video": ["16", 0], "filename_prefix": prefix, "format": "auto", "codec": "auto"}},
    }
    if face_image:
        g["6"] = {"class_type": "LoadImage", "inputs": {"image": face_image}}
        g["8"]["inputs"]["ref_images.ref_image_0"] = ["6", 0]
        g["8"]["inputs"]["ref_images.ref_image_1"] = ["18", 0]
    else:
        g["8"]["inputs"]["ref_images.ref_image_0"] = ["18", 0]

    if ref_audio:
        g["7"] = {"class_type": "LoadAudio", "inputs": {"audio": ref_audio}}
        g["8"]["inputs"]["ref_audios.ref_audio_0"] = ["7", 0]
    return g


SHOTS = [
    {
        "name": "sw_01_vader",
        "face": None,
        "shot": "sw_shot01_vader_door.jpg",
        "audio": "vader_01.mp3",
        "seed": 2001,
        "length": 158,  # ~6.5s
        "prompt": (
            "<Subject 1> is the dark-armored caped overlord and two troopers in the smoky steel Imperial corridor from <Picture 1>. <Picture 1> is the exact starting frame.\n"
            "<Audio 1> is the exact spoken dialogue audio track for <Subject 1> (S1) and is reused verbatim.\n"
            "Live-action 1977/Rogue One 35mm anamorphic Star Wars cinematography, steam drifting through cold overhead light strips, subtle film grain, NO lens flare.\n"
            "Slow menacing low-angle push-in as <Subject 1> strides forward through the smoke, speaking <Audio 1> with heavy mechanical respirator breathing."
        ),
    },
    {
        "name": "sw_02_damon",
        "face": "damon.jpg",
        "shot": "sw_shot02_damon_cell.jpg",
        "audio": "damon_02.mp3",
        "seed": 2002,
        "length": 175,  # ~7.3s
        "prompt": (
            "<Subject 1> is Damon, whose face and glasses come from <Picture 1> and whose weathered Rebel gear and Death Star Detention Block corridor come from <Picture 2>. <Picture 2> is the exact starting frame.\n"
            "<Audio 1> is the exact spoken dialogue audio track for <Subject 1> (S1) and is reused verbatim, tightly lip-synced.\n"
            "Live-action 35mm anamorphic Star Wars cinematography, cold steel shadows, amber wall indicator light, subtle film grain.\n"
            "<Subject 1> (S1) clutches his stomach in grim dread against the blast door and delivers <Audio 1> urgently."
        ),
    },
    {
        "name": "sw_03_gigi",
        "face": "gigi.jpg",
        "shot": "sw_shot03_gigi_bridge.jpg",
        "audio": "gigi_03.mp3",
        "seed": 2003,
        "length": 243,  # ~10.1s
        "prompt": (
            "<Subject 1> is Gigi, whose face comes from <Picture 1> and whose slate-grey Imperial officer uniform, cap, and Death Star bridge with two Stormtroopers come from <Picture 2>. <Picture 2> is the exact starting frame.\n"
            "<Audio 1> is the exact spoken dialogue audio track for <Subject 1> (S1) and is reused verbatim, tightly lip-synced.\n"
            "Live-action 1977 Star Wars 35mm anamorphic cinematography, glowing retro amber/green radar monitors, subtle film grain.\n"
            "<Subject 1> (S1) points sharply and scolds the two sheepish Stormtroopers like misbehaving kindergarteners while speaking <Audio 1>."
        ),
    },
    {
        "name": "sw_04_deron",
        "face": "deron.jpg",
        "shot": "sw_shot04_deron_corridor.jpg",
        "audio": "deron_04.mp3",
        "seed": 2004,
        "length": 226,  # ~9.4s
        "prompt": (
            "<Subject 1> is Deron, whose face comes from <Picture 1> and whose conical woven rice paddy hat, red satin gold-dragon robe, boba tea cup, and Death Star corridor with Stormtroopers come from <Picture 2>. <Picture 2> is the exact starting frame.\n"
            "<Audio 1> is the exact spoken dialogue audio track for <Subject 1> (S1) and is reused verbatim, tightly lip-synced.\n"
            "Live-action 35mm anamorphic Star Wars cinematography, Stormtroopers passing in foreground bokeh, subtle film grain.\n"
            "<Subject 1> (S1) gestures casually with his boba cup and speaks <Audio 1> in animated Cantonese-accented enthusiasm."
        ),
    },
    {
        "name": "sw_05_zach",
        "face": "zach.jpg",
        "shot": "sw_shot05_zach_datapad.jpg",
        "audio": "zach_05.mp3",
        "seed": 2005,
        "length": 311,  # ~13s
        "prompt": (
            "<Subject 1> is Zach, whose face comes from <Picture 1> and whose brown Rebel flight suit, glowing datapad, and Death Star control room with rushing Stormtroopers come from <Picture 2>. <Picture 2> is the exact starting frame.\n"
            "<Audio 1> is the exact spoken dialogue audio track for <Subject 1> (S1) and is reused verbatim, tightly lip-synced.\n"
            "Live-action 35mm anamorphic Star Wars cinematography, subtle film grain.\n"
            "<Subject 1> (S1) looks up calmly from scrolling his datapad while Stormtroopers rush past behind him and delivers <Audio 1>."
        ),
    },
    {
        "name": "sw_06_hooman",
        "face": "hooman.jpg",
        "shot": "sw_shot06_hooman_holo.jpg",
        "audio": "hooman_07.mp3",
        "seed": 2006,
        "length": 277,  # ~11.5s
        "prompt": (
            "<Subject 1> is Hooman, whose face comes from <Picture 1> and whose flickering blue-cyan Imperial hologram projection holding up a metallic Magic Cone funnel above the steel holo-table comes from <Picture 2>. <Picture 2> is the exact starting frame.\n"
            "<Audio 1> is the exact spoken dialogue audio track for <Subject 1> (S1) and is reused verbatim, tightly lip-synced.\n"
            "Live-action 35mm anamorphic Star Wars cinematography, smoky briefing room, Imperial officer silhouettes watching.\n"
            "The hologram <Subject 1> (S1) flickers slightly and pitches the metallic funnel enthusiastically while speaking <Audio 1>."
        ),
    },
    {
        "name": "sw_07_ajay",
        "face": "ajay.jpg",
        "shot": "sw_shot07_ajay_medbay.jpg",
        "audio": "ajay_09.mp3",
        "seed": 2007,
        "length": 209,  # ~8.7s
        "prompt": (
            "<Subject 1> is Ajay, whose face comes from <Picture 1> and whose dark medical robes, gleaming sci-fi neural DBS halo headset, and cold blue Death Star medbay come from <Picture 2>. <Picture 2> is the exact starting frame.\n"
            "<Audio 1> is the exact spoken dialogue audio track for <Subject 1> (S1) and is reused verbatim, tightly lip-synced.\n"
            "Live-action 35mm anamorphic Star Wars cinematography, cold surgical light, subtle film grain.\n"
            "<Subject 1> (S1) tilts the neural headset calmly toward the camera with clinical poise and speaks <Audio 1>."
        ),
    },
    {
        "name": "sw_08_sheren",
        "face": "sheren.jpg",
        "shot": "sw_shot08_sheren_cockpit.jpg",
        "audio": "sheren_12.mp3",
        "seed": 2008,
        "length": 158,  # ~6.5s
        "prompt": (
            "<Subject 1> is Sheren, whose face comes from <Picture 1> and whose Rebel pilot vest, Millennium Falcon cockpit, and streaking hyperspace stars come from <Picture 2>. <Picture 2> is the exact starting frame.\n"
            "<Audio 1> is the exact spoken dialogue audio track for <Subject 1> (S1) and is reused verbatim, tightly lip-synced.\n"
            "Live-action 35mm anamorphic Star Wars cinematography, camera shake, glowing console switches, hyperspace star streaks.\n"
            "<Subject 1> (S1) slams the hyperdrive throttle forward with a fearless grin and shouts <Audio 1>."
        ),
    },
]


def main():
    ensure_comfyui()
    for s in SHOTS:
        t0 = time.time()
        print(f"=== Starting {s['name']} (len={s['length']}) ===", flush=True)
        g = build_graph(
            face_image=s["face"],
            shot_image=s["shot"],
            ref_audio=s["audio"],
            prompt_text=s["prompt"],
            prefix=f"video/{s['name']}",
            seed=s["seed"],
            length=s["length"],
        )
        pid = post_prompt(g)["prompt_id"]
        entry = wait_for_history(pid, timeout=1800)
        print(f"=== Finished {s['name']} in {time.time() - t0:.1f}s ===", flush=True)
        print(json.dumps(entry.get("outputs", {}), indent=2), flush=True)


if __name__ == "__main__":
    main()
