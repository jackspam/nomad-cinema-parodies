# Nomad Cinema Parodies — Pipeline Rules & Hardened Quality Gates (v2.4)

_Living engineering standard. Every gate, threshold, and lesson below is automatically published to the live studio Process Handbook and updated whenever a failure mode is discovered and fixed._

---

## Version & Hardening Changelog

- **v2.4 (2026-11-26) — Measured-LUFS Mix Leveling, Mandatory Silent-Listener Spatial Locking & Anti-Extreme-Zoom Rule:**
  - **Measured-LUFS Music & SFX Leveling:** Never apply raw scalar gain (`* 0.22`) or blind heavy sidechain compression onto music/SFX stems. Measure every dialogue, music, and SFX stem's integrated LUFS with `ffmpeg loudnorm ... print_format=json` first, apply linear gain to exact cinema targets (music bed `-21.5` to `-22.5 LUFS` gently ducked `~-3.5 dB` under `-16 LUFS` dialogue; hard SFX at `-13` to `-18 LUFS`), and trim reverb tails cleanly with triangular `acrossfade` for seamless score loops (`score_dk_act1_dark` -> `score_dk_act2_intense`).
  - **Mandatory Silent-Listener Spatial Lock Audit (Gate 5):** Inspect EVERY multi-face InfiniteTalk clip end-to-end (`read_file` MP4) and composite horizontal cosine-feathered spatial reference locks (`scripts/lock_listeners_dk2.py`) onto any secondary face showing sympathetic lip bleed (`DK2_14, 23, 28, 31, 32, 35`), then re-run SyncNet to confirm zero seam and preserved speaker lip score.
  - **Anti-Extreme-Zoom Opening Rule (Gate 8):** Ban `> 20%/s` wide-to-ECU LTX-2.5 camera zooms starting from `< 100px` background faces (which trigger facial aging/morph hallucinations as in original `DK2_01`). Anchor opening/establishing dialogue lines at a matched medium close-up keyframe routed cleanly through InfiniteTalk (`DK2_01` fixed to match Shots `02–09` 1:1).

- **v2.3 (2026-11-25) — Optical-Flow YouTube Camera Decomposition, Camera Control LoRAs & Return-Cut Hair/Makeup Locking:**
  - Built automated RANSAC optical-flow cinematography analyzer (`scripts/analyze_yt_camera.py`) to inspect extracted source scenes cut-by-cut and convert real movie camera trajectories (`zoom_rate`, `pan/tilt`, `handheld_jitter`, shot scale, screen side) into structured JSON specs and explicit preflight grammar validation (`scripts/preflight_validate.py`).
  - Documented exact **Lightricks `LTX-2-19b-LoRA-Camera-Control-*`** adapters (`Static`, `Dolly-In`, `Dolly-Out`, `Dolly-Left`, `Dolly-Right`, `Jib-Up`, `Jib-Down`), **`IC-LoRA Cameraman`** reference trajectory transfer, LTX-2.5 **positive-only physical camera prompting** (eliminating confusing negative tokens like `"no zoom"` or `"don't move"` that trigger creeping push-ins), and **Wan `Uni3C` / `ReCamMaster` / `ATI`** + **Two-Stage `Camera Motion -> InfiniteTalk V2V`** routing.
  - Added the **Return-Cut Master Anchor & Hair/Makeup Lock Protocol** in Stage 3: generate ONE master setup keyframe per camera angle and pass BOTH the character Hero Anchor AND the prior approved return-cut frame to lock exact hair parting, shoulder placement, glasses tilt, and prosthetic greasepaint/scar continuity across alternating `A -> B -> A` edits.

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
- Do not prompt camera movement blindly. Run `scripts/analyze_yt_camera.py` on the extracted source YouTube clip before writing any video generation prompt or keyframe brief:
  - **Shot Boundary & RANSAC Optical-Flow Decomposition:** Detect exact cuts via `PySceneDetect` (`ContentDetector`) and run Lucas-Kanade optical flow (`goodFeaturesToTrack` + `calcOpticalFlowPyrLK` + `estimateAffinePartial2D` RANSAC) at `8 fps` inside each cut so actor lip/head motion is ignored as outliers and true global camera motion is isolated cleanly.
  - **Measured Camera Motion Telemetry:** Compute `zoom_rate_pct_s` (`(scale - 1) * 100 / dur`), `pan_pct_s`, `tilt_pct_s`, high-frequency `handheld_jitter_pct` (RMS residual after subtracting linear pan/tilt), and `peak_shake_pct`.
  - **Automatic Motion Tags & Model Routing:**
    - `IMPACT_SHAKE` (`peak_shake >= 1.8%`) -> Route to `LTX-2.5` + `IC-LoRA Cameraman`.
    - `SLOW_DOLLY_IN` / `SLOW_DOLLY_OUT` (`|zoom_rate| >= 1.2%/s`) -> Route to `Lightricks/LTX-2-19b-LoRA-Camera-Control-Dolly-In` / `Dolly-Out` (or `LTX-2.5 -> InfiniteTalk V2V` for close-up dialogue).
    - `PAN_ORBIT` (`|pan| >= 2.0%/s` or `|tilt| >= 1.8%/s`) -> Route to `Dolly-Left/Right` or `IC-LoRA Cameraman`.
    - `HANDHELD_35MM` (`handheld_jitter >= 0.14%`) -> Route to `InfiniteTalk I2V + 1.016x 35mm organic weave` or `Two-Stage LTX Handheld -> InfiniteTalk V2V`.
    - `STATIC_LOCKED` (default) -> Route to `InfiniteTalk I2V` (dialogue) or `LTX-2.5` + `Lightricks/LTX-2-19b-LoRA-Camera-Control-Static`.
  - **Shot Scale, Screen Side & Sequence Grammar Audit:** Measure `face_height / frame_height` (`ECU`, `CU`, `MCU`, `MS`, `WIDE`), lock screen side (`left`/`center`/`right`), and automatically flag consecutive `SLOW_DOLLY_IN` streaks (`>= 2` in a row or `A -> B -> A` return-cut push-ins) before preflight passes.

### Stage 2 — Nomads-Only Casting & Voice Generation
- **100% Nomad Cast Rule:** Every speaking role is played by a verified Nomad cast member anchored to high-res studio likeness refs — zero generic stock strangers in dialogue shots.
- Generate clean dialogue stems with **ElevenLabs** (`scripts/gen_*_audio.py`) with authentic vocal delivery (crisp pronunciation, zero trailing gibberish, matched emotional intensity).
- Inspect waveforms for zero clipping, minimal leading silence, and clean trailing decay; store exact pre-trim MP3 stems in `/audio/<slug>/`.

### Stage 3 — Hero-Anchor Keyframes & Return-Cut Hair/Makeup Locking
- Generate `21:9` Scope starting (and optional ending) keyframes using **Nano Banana Pro** (`image-generator` Ultra subscription first, Paid Tier 3 `gemini-3-pro-image` at native `21:9` `2K` as fallback), locking costume, lighting, set dressing, and facial likeness to **one single Hero Anchor per character/lighting state**.
- **Return-Cut Master Anchor Protocol (Zero Hair Jumps or Mid-Scene Makeup Drift):**
  - Establish **one Gold-Master Keyframe per recurring camera setup** (`Setup A`, `Setup B`, etc.) at the start of a lighting act.
  - On EVERY return cut (`Shot N+2` returning to the same setup/character as `Shot N`), pass **BOTH** the actor's **Hero Anchor portrait** AND the **previously approved keyframe from that setup** (`Setup A Master` or `Shot N`), explicitly instructing the generator to keep identical hair parting, shoulder/collar hair placement, glasses angle, and prosthetic greasepaint/scar intensity across the sequence.
  - **Multi-Face Angle Consistency:** When the same character appears in a solo CU and a side-angle group shot, verify ear exposure, hair tuck, and facial makeup density side-by-side before rendering video.
- Crop and pack every keyframe to exact **`1920x832`** Panavision Scope (`scripts/prep_keyframe.py`).
- Build and visually inspect **5 Pre-Render Cast Continuity Grids** across all stills before touching GPU video compute — zero wardrobe swaps, hair flips, glasses changes, or makeup drift allowed to proceed.

### Stage 4 — Hybrid Video Rendering (`LTX-2.5` + `InfiniteTalk` on Colab G4 RTX PRO 6000)
- **Single-Anchor Rule on Tight Close-Ups:** Omit `end_image` (`end_image = null`) on tight talking close-ups so end-frame blending never causes double-exposure dissolves or abrupt tail expression shifts.
- **Technical Camera-Control Architecture (No Default Push-Ins):**
  - **Positive-Only Physical Camera Directives (LTX-2.5 Rule):** LTX-2.5 defaults to a creeping push-in on long clips if camera behavior is unspecified or prompted negatively (`"no zoom"`, `"don't move"`, `"no camera movement"` confuse the transformer and are blocked by `preflight_validate.py`). Always declare positive physical state in a single present-tense paragraph: `"static lock-off camera mounted on a heavy tripod, completely stationary framing"` for locked coverage, `"subtle organic 35mm handheld camera breathing with tiny operator micro-movements, maintaining fixed framing distance"` for handheld, or `"measured slow linear dolly push-in along fixed axis on weighted rails"` strictly when Stage 1.5 detects `SLOW_DOLLY_IN`.
  - **Verified Lightricks Camera Control LoRAs & IC-LoRA Cameraman:** Load official `Lightricks/LTX-2-19b-LoRA-Camera-Control-Static` (plus `Dolly-In`, `Dolly-Out`, `Dolly-Left`, `Dolly-Right`, `Jib-Up`, `Jib-Down`) for directional control, or `IC-LoRA Cameraman` with the extracted source YouTube clip passed as the reference control video at `>= 960x512` Stage 1 to transfer genuine cinema handheld shake and panning curves directly.
  - **Two-Stage Motion + Lip-Sync (`Camera Motion -> InfiniteTalk V2V`) & Wan Ecosystem:** For shots combining aggressive camera choreography with tight phoneme-locked dialogue and heavy theatrical makeup, generate the clean camera trajectory/body performance first in `LTX-2.5` (or Wan2.1/2.2 `Uni3C` / `ReCamMaster` / ByteDance `ATI` trajectory conditioning), then pass that clip through **InfiniteTalk V2V** (`ComfyUI-WanVideoWrapper` `wanvideo_InfiniteTalk_V2V`) so Wav2Vec2 syncs lips cleanly while preserving the exact camera move.
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
| **5. Silent-Listener Discipline** | Full-MP4 audit + horizontal cosine-feathered spatial lock across EVERY multi-face InfiniteTalk clip | Listening characters keep **mouths 100% sealed**, zero sympathetic lip echo (`lock_listeners` verified + SyncNet re-passed) |
| **6. Makeup, Texture & Physics** | Full-MP4 inspection (`read_file` native video audit) | Natural skin pores, intact paint/scars/glasses, zero blurry hand swipes (`DK2_18` caught), zero wall wobble |
| **7. Zero Post-Hoc Mouth Patching** | Pipeline ban on SD1.5 face-inpainting refiners | Never run `LatentSync` on heavy greasepaint or detailed facial stubble |
| **8. Camera Grammar & Return-Cut Lock** | Stage 1.5 motion match + preflight camera-grammar gate + return-cut side-by-side diff | Zero consecutive unmotivated push-ins (`A -> B -> A -> B`), **no `> 20%/s` LTX zooms from `< 100px` faces**, zero negative camera phrasing (`no zoom`), and identical hair/glasses/makeup density across cuts |

### Stage 6 — Post-Render Video Continuity & Adjacent Cut-Pair Audit
- Run `scripts/qa_video_continuity.py` on **all 40 final rendered MP4s** (not source stills):
  - **5 Rendered-Video Character Continuity Grids:** Verify facial structure, makeup, lighting contrast, and sharpness across every cut (ensuring `LTX-2.5` and `InfiniteTalk` shots match as one cohesive camera package).
  - **Adjacent Cut-Pair Grids (`Shot N end` next to `Shot N+1 start`):** Verify all 39 edit transitions (`01->02` through `39->40`) for eye-line continuity, exposure jump, and color temperature lock.

### Stage 7 — Hollywood Editorial Assembly, Broadcast Mix & 35mm Grade
- **Tight Nolan Cut Pacing:** Detect true last vocal energy (`> -38 dB`) per clip and trim cleanly to **`speech_end + 0.20s`** (`0.35s` dramatic hold on Act breaks) — zero dead-air frozen tails, zero clipped final consonants.
- **Broadcast Dialogue Leveling (`-16 LUFS`):** Measure per-stem integrated loudness and apply zero-latency linear gain so every cast member speaks at uniform cinema presence, plus `15 ms` audio micro-fades at cuts.
- **Cinematic Sound Design (Measured LUFS Only):** Subtle room tone bed (`-32` to `-36 LUFS`) + pre-measured LUFS score (`-21.5` to `-22.5 LUFS`, light `ratio=2.2` ducking `-3.5 dB` under `-16 LUFS` speech) + measured-LUFS hard SFX (`-13` to `-18 LUFS`) synced cleanly to visual actions (overhead lights slam ON, heavy table slam, precinct door rattle) — never use blind raw scalar multipliers.
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
