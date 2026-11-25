# Nomad Cinema Parodies — Hardened Production Pipeline Rules

Learnings distilled from producing Films 02–07 (~119 rendered clips):

1. **LTX-2.5 IA2V Is the Default Engine (`1 + 8*k` Frames at 24fps)**
   - Run LTX-2.5 (`colab_ltx25_jobs.py`) across Colab GPUs, prioritizing **G4 (`RTX PRO 6000`, ~20–30s/clip)**, then **A100 (`~45–125s/clip`)**, with **L4 `--lowvram` (`~120–215s/clip`)** as extra parallel capacity.
   - Use `SetLatentNoiseMask(0.0)` over encoded `<Audio 1>` so ElevenLabs dialogue locks 100% verbatim.
   - Always stop provisioned GPUs immediately after clip QA finishes; never touch unrelated `[?]` sessions.

2. **Casting & Voice Rule for Batch 2 (~5-Minute Scenes)**
   - **Target ~5-minute scenes (~40–45 shots)** extracted shot-for-shot from real YouTube clips (`>= 40–60` YT reference frames).
   - **Cast Nomads in all heavy talking roles**; keep recognizable movie sets, wardrobe, camera blocking, and silent/secondary characters true to the original film so famous actor voice mismatches never distract.
   - When expressive non-Nomad voices are needed, design/use `eleven_v4_turbo` voices tuned for full theatrical energy (zero accidental whispers).

3. **Audio Preflight & Ear Audit (Before Any GPU Time)**
   - Trim trailing silence (`silencedetect`), **listen** to outlier MP3s (`duration > words * 0.55 + 2.5s` or `> 10s`), and slice any ElevenLabs `eleven_multilingual_v2` duplicate sentences or gibberish tails cleanly before rendering video.
   - Listen to **every generated background score & Foley SFX** individually before assembly: ensure continuous musical body (zero trailing dead air, zero rain-sounding-like-applause).

4. **Mandatory Actor-to-Keyframe Matching & Open-Weight Fallback**
   - Visually inspect (`read_file`) every bespoke keyframe in `refs/<slug>/` against the speaking character and camera angle of every shot using it.
   - Never reuse a different character's keyframe under a prompt hoping I2V will swap them.
   - If cloud image generation hits capacity (`HTTP 503`), fall back automatically to **`Qwen/Qwen-Image-Edit-2509`** on Colab `G4` (`96 GB`) conditioned on the `-face-hd.png` portrait refs, then inspect every output image before I2V.

5. **Single-Speaker & Silent-Listener Prompt Discipline**
   - In multi-person or wide shots (`2–6` people), explicitly name the **one** speaker by costume and left/center/right position AND specify that all other characters keep their mouths completely **CLOSED** listening quietly.
   - For off-screen VO / monitor audio shots (`silent_on_camera: true`), bind `LTXVEmptyLatentAudio` and instruct all on-screen characters to keep mouths closed in silence (plus avoid unrequested giant overlays).
   - Keep camera prompts tight to `<Picture 1>` (ban whip-pans, orbit-behind, and characters walking past lens).

6. **100% Clip & Final Master QA Before Publishing**
   - Visually inspect every generated clip (`read_file`); reject and re-render anything scoring `< 8/10` (face morphing, wrong speaker mouthing, cloned characters).
   - Assemble `< 90 MB` 1080p MP4 masters (CRF 19, `4200k` maxrate, `+faststart`, `-14 LUFS`), inspect each full 1080p MP4 end-to-end via `read_file`, then push clean commits to `origin main`.
