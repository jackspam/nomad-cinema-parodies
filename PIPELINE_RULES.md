# Nomad Cinema Parodies — Pipeline Rules & Hardened Quality Gates (v2.2)

_Living engineering standard. Every gate, threshold, and lesson below is automatically published to the live studio Process Handbook and updated whenever a failure mode is discovered and fixed._

---

## Version & Hardening Changelog

- **v2.2 (2026-11-25) — Cinematography Grammar, YouTube Optical-Flow Analysis & Camera Control Architecture:**
  - Responded to director critique on Act 1 Gigi hair jumps across cuts and repetitive standalone camera push-ins (`01 -> 02 -> 04 -> 06 -> 08`) making consecutive shots feel disconnected rather than one continuous Nolan scene.
  - Added **Stage 1.5 (Automated YouTube Cinematography & Optical-Flow Decomposition)** measuring `zoom_rate (ds/dt)`, `pan/tilt (dx/dt, dy/dt)`, `handheld_jitter`, shot scale (`ECU..WIDE`), and 180° eye-line blocking per cut from reference frames.
  - Added **Gate 8 (Sequence-Level Camera Grammar & Hair/Silhouette Lock)** banning default `"slow dolly push-in"` prompts, prohibiting consecutive unmotivated push-ins across `A -> B -> A -> B` coverage, and requiring hair part/silhouette continuity checks.
  - Documented **LTX-2.5 Static/Dolly Camera Control LoRAs**, **IC-LoRA Cameraman** reference motion transfer, **Two-Stage Motion + V2V InfiniteTalk** (`Camera Motion -> Wav2Vec2 Lip-Sync`), and calibrated **Editorial 35 mm Handheld Micro-Weave**.
- **v2.1 (2026-11-25) — Brutal Cinema QA, Living Process Page & Media Deploy Verification:**
  - Anchored `/clips/` and `/audio/` in `.gitignore` after unanchored `clips/` silently dropped `preview/clips/` on GitHub Pages (`HTTP 404`); moved web preview assets to `preview_media/` with generated `.jpg` poster stills and mandated **HTTP 200 verification on both HTML pages AND actual `.mp4` media URLs** before reporting live.
  - Enforced zero-tolerance acting/artifact review on every passing SyncNet clip (caught and queued `DK2_18` for an unmotivated `0:00` blurry hand-drop swipe despite `LSE-C 6.91`).
  - Added post-render **Video Continuity & Adjacent Cut-Pair Grids** (actual rendered mid-frames and `Shot N end -> Shot N+1 start` comparisons across all 40 cuts).
  - Upgraded editorial assembly to **Nolan-tight tail trimming** (`speech_end + 0.20s`), **matched `-16 LUFS` zero-latency dialogue leveling**, room tone, sidechain-ducked tension score, hard SFX cues, unified 35 mm Panavision grade/grain, and **high-density 45s segmented Director's Cut screening**.
- **v2.0 (2026-11-25) — SyncNet Hard Gate, Hero-Anchor Continuity & Hybrid LTX-2.5 + InfiniteTalk:**
  - Rejected v1 Dark Knight + Parodies 03–07 for off-cast faces, morphs, unprompted tail grins, and lip desync; mandated **Nomads ONLY in every speaking role**.
  - Added single Hero-Anchor portrait locking (`21:9` native Nano Banana Pro) + 5 pre-render **Cast Continuity Grids**.
  - Replaced self-written optical-flow lip heuristic with **ByteDance/SyncNet** (`LSE-C >= 4.5`, `|offset| <= 2f`, `LSE-D <= 10.0`) + **Final-1.2s Expression Strip**.
  - Rejected **LatentSync-1.5** (`4/4` SyncNet failures + smeared Joker greasepaint/scars) and **LTXVModalityGuidance(3.0)** + **FFmpeg 1-pass `loudnorm`** (introduced `-30 ms` audio lag and dropped SyncNet).
  - Deployed **Hybrid Engine Routing**: **LTX-2.5 Dev BF16** (with `LTXVFreezeLatent` + zero-latency linear gain + `euler`) for Start+End camera/action choreography, and **InfiniteTalk (Wan2.1-14B + Wav2Vec2 + LightX2V)** for phoneme-locked dialogue and heavy theatrical makeup.

---

## 8-Stage End-to-End Filmmaking Pipeline

### Stage 1 — Reference Scene Breakdown & Beat Extraction
- Inspect source scene cut-by-cut and extract 250–350+ clean reference frames from the original film (`refs/yt/<slug>/`) to match camera blocking, focal lengths, cyan-dark vs clinical fluorescent lighting transitions, and shot pacing.
- Build a structured 40-shot shot list (`scripts/<slug>_script.json`) preserving exact emotional beats, two-shot spatial continuity (left/right eye-line), and scene transitions.

### Stage 1.5 — Automated YouTube Cinematography & Optical-Flow Analysis
- Do not prompt camera movement blindly. Analyze the extracted source YouTube shots cut-by-cut (`scripts/analyze_yt_camera.py`) before writing any video generation prompt:
  - **Optical-Flow Motion Vector Profile:** Fit frame-to-frame affine homographies within each cut to measure `zoom_rate (ds/dt)`, `pan/tilt velocity (dx/dt, dy/dt)`, and `high-frequency handheld jitter`.
  - **Cinematography Classification Tag:** Label every shot explicitly as `STATIC_LOCKED`, `HANDHELD_35MM`, `SLOW_DOLLY_IN`, `SLOW_DOLLY_OUT`, `PAN_ORBIT`, or `IMPACT_SHAKE` (only shots with genuine source camera motion get movement directives).
  - **Shot Scale & 180° Eye-Line Matrix:** Measure face-height / frame-height ratio (`ECU`, `CU`, `MCU`, `MS`, `OTS`, `WIDE`) and lock camera-side eye-lines so returning cuts on the same speaker hold identical focal length and screen direction.

### Stage 2 — Nomads-Only Casting & Voice Generation
- **100% Nomad Cast Rule:** Every speaking role is played by a verified Nomad cast member anchored to high-res studio likeness refs — zero generic stock strangers in dialogue shots.
- Generate clean dialogue stems with **ElevenLabs** (`scripts/gen_*_audio.py`) with authentic vocal delivery (crisp pronunciation, zero trailing gibberish, matched emotional intensity).
- Inspect waveforms for zero clipping, minimal leading silence, and clean trailing decay; store exact pre-trim MP3 stems in `/audio/<slug>/`.

### Stage 3 — Hero-Anchor Keyframe Generation & Pre-Render Continuity Grids
- Generate `21:9` Scope starting (and optional ending) keyframes using **Nano Banana Pro** (`image-generator` Ultra subscription first, Paid Tier 3 `gemini-3-pro-image` at native `21:9` `2K` as fallback), locking costume, lighting, set dressing, and facial likeness to **one single Hero Anchor per character/lighting state**.
- Crop and pack every keyframe to exact **`1920x832`** Panavision Scope (`scripts/prep_keyframe.py`).
- Build and visually inspect **5 Pre-Render Cast Continuity Grids** across all 71 stills before touching GPU video compute — zero wardrobe swaps, glasses changes, makeup drift, or face morphs allowed to proceed.

### Stage 4 — Hybrid Video Rendering (`LTX-2.5` + `InfiniteTalk` on Colab G4 RTX PRO 6000)
- **Single-Anchor Rule on Tight Close-Ups:** Omit `end_image` (`end_image = null`) on tight talking close-ups so end-frame blending never causes double-exposure dissolves or abrupt tail expression shifts.
- **Technical Camera-Control Architecture (No Default Push-Ins):**
  - **LTX-2.5 Static & Directional Camera LoRAs:** Never let text prompts default to `"slow dolly push-in"`. Use Lightricks' `LTX-2/2.5` Static Camera LoRA (plus explicit negative `"dolly in, zoom in, push in"`) for locked dialogue coverage, and use Directional Dolly/Jib LoRAs *only* on beats matching Stage 1.5 motion vectors.
  - **IC-LoRA Cameraman (Reference Video Motion Transfer):** For handheld tension, table orbits, or whip pans matching real cinema photography, drive `LTX-2.5` with `IC-LoRA Cameraman` at `>= 960x512` Stage 1 using a clean reference motion clip extracted from the source YouTube cut.
  - **Two-Stage Motion + Lip-Sync (`Camera Motion -> V2V InfiniteTalk`):** When a shot requires both dramatic camera choreography (handheld tracking, orbital push, physical struggle) and tight lip sync on painted makeup, generate the clean camera/body performance first in `LTX-2.5`, then run **V2V InfiniteTalk** (`Wan2.1-14B`) so Wav2Vec2 drives the lips while inheriting the exact camera trajectory.
- **LTX-2.5 Dev BF16 (`scripts/colab_ltx25_v2.py`):** Used for Start+End camera choreography and physical action (`960x416` 24-step `euler` -> Stage 2 Distilled LoRA `450` x2 latent upscale -> `1920x832`). Always freeze custom audio with `LTXVFreezeLatent`, use zero-latency linear `volume` scaling (never `loudnorm`), and **never enable `LTXVModalityGuidance`**.
- **InfiniteTalk Wan2.1-14B (`scripts/colab_infinitetalk_v2.py`):** Used for phoneme-locked close-up dialogue, tilted/expressive heads, and heavy prosthetic makeup (`960x416` `dpm++_sde` `6`-step `LightX2V` + `Wav2Vec2` audio embeddings -> Lanczos/unsharp x2 to `1920x832` muxed with exact clean WAV).
- Keep GPU alive continuously through full QA, continuity checks, and master screening; never leave stale `_00001_.mp4` prefixes when re-rendering.

### Stage 5 — 7-Gate Automated & Brutal Visual Clip QA
Every single rendered MP4 must pass ALL clip gates below (zero exceptions — failed shots are re-seeded or switched between engines immediately):

| Gate | Automated / Visual Check | Pass Threshold (Fail = Immediate Retry) |
| :--- | :--- | :--- |
| **1. Lip-Sync Confidence** | SyncNet (`sfd_face` + `syncnet_v2`, speaker horizontally isolated on multi-person shots) | **`LSE-C >= 4.5`** (target `>= 5.0`; `3.5` allowed *only* on extreme physical action `DK2_27` / distant hall `DK2_35`) |
| **2. Audio-Video Timing Offset** | SyncNet temporal lag check | **`|offset| <= 2` frames (`±83 ms`)** — no `±3f+` lag tolerated (`DK2_04` tightened) |
| **3. Feature Distance** | SyncNet audio-visual embedding distance | **`LSE-D <= 10.2`** (target `<= 9.5`) |
| **4. Final-1.2s Expression Strip** | 6-frame visual inspection across final 1.2s (`strips/<SID>_tail.jpg`) | Clean mouth closure at end of dialogue; **zero unprompted tail smiles, grins, or frozen teeth** |
| **5. Silent-Listener Discipline** | Full-MP4 inspection on all 2-shots and group shots | Listening characters keep **mouths 100% sealed**, zero echoing, zero phantom lip twitches |
| **6. Makeup, Texture & Physics** | Full-MP4 inspection (`read_file` native video audit) | Natural skin pores, intact paint/scars/glasses, zero blurry hand swipes (`DK2_18` caught), zero wall wobble |
| **7. Zero Post-Hoc Mouth Patching** | Pipeline ban on SD1.5 face-inpainting refiners | Never run `LatentSync` on heavy greasepaint or detailed facial stubble |
| **8. Camera Grammar & Silhouette Lock** | Stage 1.5 motion match + pre-render returning-coverage check | Zero consecutive unmotivated push-ins (`A -> B -> A -> B`); hair parting, ear visibility, and glasses stay locked across cuts |

### Stage 6 — Post-Render Video Continuity & Adjacent Cut-Pair Audit
- Run `scripts/qa_video_continuity.py` on **all 40 final rendered MP4s** (not source stills):
  - **5 Rendered-Video Character Continuity Grids:** Verify facial structure, makeup, lighting contrast, and sharpness across every cut (ensuring `LTX-2.5` and `InfiniteTalk` shots match as one cohesive camera package).
  - **Adjacent Cut-Pair Grids (`Shot N end` next to `Shot N+1 start`):** Verify all 39 edit transitions (`01->02` through `39->40`) for eye-line continuity, exposure jump, and color temperature lock.

### Stage 7 — Hollywood Editorial Assembly, Broadcast Mix & 35mm Grade
- **Tight Nolan Cut Pacing:** Detect true last vocal energy (`> -38 dB`) per clip and trim cleanly to **`speech_end + 0.20s`** (`0.35s` dramatic hold on Act breaks) — zero dead-air frozen tails, zero clipped final consonants.
- **Broadcast Dialogue Leveling (`-16 LUFS`):** Measure per-stem integrated loudness and apply zero-latency linear gain so every cast member speaks at uniform cinema presence, plus `15 ms` audio micro-fades at cuts.
- **Cinematic Sound Design:** Subtle room tone bed + sidechain-ducked score (`score_dk_tension.mp3`) + crisp hard SFX hits synced cleanly to visual actions (overhead lights slam ON, heavy table slam, precinct door rattle).
- **Unified 35 mm Panavision Finishing & Organic Handheld Weave:** Color/contrast/sharpness normalization + fine 35 mm film grain + calibrated organic handheld micro-drift (`0.35%–0.55%` dual-sine weave inside `1.016x` overscan on handheld scenes so locked shots breathe instead of freezing) + matte Scope letterbox inside **`1920x1080`** (`< 90 MB`, `-movflags +faststart` web streaming).

### Stage 8 — Segmented Director's Cut Screening & Live Deploy Verification
- Split the assembled 1080p master into **45-second high-density segments** and screen **every segment end-to-end** while the GPU is still warm; fix any edit, audio, or shot flaw immediately.
- Stop Colab GPU only after the final master passes 100%, run `python3 scripts/preflight_validate.py` & `python3 scripts/build_site.py`, commit cleanly (respecting `/clips/`, `/audio/`, `.env*` ignores), push to GitHub, and verify **HTTP 200 on every deployed HTML page AND every referenced `.mp4` stream**.

---

## Hard-Won Failure Modes Blocked by This Standard

- **Unanchored `.gitignore` Dropping Web Previews:** Never put bare `clips/` in `.gitignore` when hosting web previews under `preview/clips/`; anchor `/clips/` and ALWAYS curl the actual `.mp4` URL for HTTP 200.
- **One-Pass `loudnorm` Desync:** FFmpeg's single-pass `loudnorm` buffers and shifts speech by `-30 ms` (`-2f`) + trims starts; always use pre-measured linear `volume` gain (`0 ms` shift).
- **LTX-2.5 `LTXVModalityGuidance` Regression & Joker Grin Prior:** Adding `LTXVModalityGuidance(3.0)` degraded lip sync; LTX-2.5 also defaults to silent Joker smirks mid-shot. Routing complex dialogue/makeup shots to **InfiniteTalk** solves both cleanly (`LSE-C 5.52–7.70`).
- **Two-Anchor Morph Dissolves:** Feeding `end_image` into LTX-2.5 on tight CUs causes half-clip double exposures; tight talking CUs must stay single-anchor (`end_image = null`).
