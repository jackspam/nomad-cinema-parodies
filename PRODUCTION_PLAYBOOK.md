# Nomad Cinema Parodies — Self-Improving Production Playbook

Every real defect caught during video review becomes a mandatory preflight gate in `scripts/preflight_validate.py` and `scripts/studio_pipeline.py` so subsequent films one-shot cleanly.

## Empirical Lessons Encoded Into the Pipeline

1. **Single Iconic Scene Only (Zero Mashups):** Extract 40 single-scene frames from YouTube (`refs/yt/<slug>/yt_01..40.jpg`) covering one continuous movie location before generating keyframes. Multi-location mashups (*Star Wars* v1, *Breaking Bad* early RV drafts) are blocked before upload.
2. **Exact Lighting & Color Matching:** Generate every keyframe directly from the sampled YouTube frames' light direction, color temperature, and contrast (and apply matching 1080p LUT/color-balance + 35mm film grain in `studio_pipeline.py`).
3. **Prevent Face Morphing & CGI Mascot Hallucinations (`<Picture 1>` Lock):** When a bespoke keyframe already contains the Nomad/character likeness, pass ONLY `[shot_image]` (not a second reference portrait) with explicit `<Picture 1>` and `<Audio 1>` tags, and forbid mentioning off-screen characters, props, or camera pan-aways in prompts (`DK_01` dragon mascot lesson).
4. **Prevent Repeating / Slurred End Syllables (Silence-Trim Before H3):** ElevenLabs MP3s often include 1–2s of trailing digital silence, causing MiniMax H3 to hallucinate extra repeated words (`SW_03`, `SW_04`, `DK_02`). `preflight_validate.py` strips trailing silence before H3 generation and computes `valid_h3_frames(trimmed_dur + 0.45)`.
5. **Frame-Accurate Lip-Sync Lock in Post:** Anchor ElevenLabs VO at exact `t = 0.0` of every clip (matching MiniMax H3's `ref_audio_0` anchor), mute native video speech track (`volume=0`) to avoid double-voices (`GOT_04` lesson), and cut cleanly right after natural decay (`SW_02` lesson).
6. **Zero Physics & Walk-Through Artifacts:** Never prompt foreground crowds walking across speakers (`SW_04` clipping lesson) or 180-degree behind-the-head camera orbits (`DK_03` morph lesson). Keep camera motion to a slow controlled 2–5% cinema dolly/push-in.
7. **Studio Gate (`< 8/10` Auto-Reject):** Every clip is visually inspected via `read_file` and scored on Visual Quality, Physics/Coherence, Movie Match, and Lip Sync. Anything scoring `< 8/10` on Physics or Lip Sync is rejected and re-rendered with a corrected prompt before publishing.
