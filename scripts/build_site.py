import glob
import json
import os
import html as html_mod

BASE = "/Users/jack/.gemini/antigravity/scratch/nomad-cinema-parodies"

FILMS = [
    {
        "slug": "00_game_of_thrones",
        "num": "00",
        "title": "Game of Thrones — The Porcelain Keep (Pilot)",
        "subtitle": "HBO Winterfell 35mm Look · Starring Damon",
        "status": "1080p Ready",
        "status_cls": "done",
        "mp4": "films/00_game_of_thrones_1080p.mp4",
        "prep_time": "Pilot phase",
        "render_time": "~26 min (L4, 4 clips)",
        "audit": [
            {"shot": "GOT_01", "quality": 8, "physics": 8, "similarity": 8, "lipsync": 8, "notes": "Winterfell courtyard lighting & snow match HBO; initial keyframe revised from illustration to photoreal.", "revisions": "v1 illustration rejected -> v2 photoreal HBO grade."},
            {"shot": "GOT_02", "quality": 8, "physics": 8, "similarity": 8, "lipsync": 7, "notes": "Good interior candlelight.", "revisions": "None."},
            {"shot": "GOT_03", "quality": 7, "physics": 7, "similarity": 7, "lipsync": 7, "notes": "Slight AI smoothness late in shot.", "revisions": "Unified 35mm grain applied."},
            {"shot": "GOT_04", "quality": 7, "physics": 7, "similarity": 7, "lipsync": 6, "notes": "Minor lip-sync drift & double-voice at end.", "revisions": "Muted native voice track & trimmed splash tail."},
        ],
    },
    {
        "slug": "02_dark_knight",
        "num": "02",
        "title": "The Dark Knight — The Interrogation Room",
        "subtitle": "IMAX 65mm & 35mm Panavision · Damon, Deron, Hooman, Gigi & The Joker",
        "status": "Ingredients Ready · Rendering on G4",
        "status_cls": "",
        "mp4": "films/02_dark_knight_1080p.mp4",
        "prep_time": "25m 37s",
        "render_time": "In progress on L4: Shots 1-9 approved (v2 DK_01 761.6s, v2 DK_07 761.3s); rendering Shot 10/20",
        "audit": [
            {"shot": "DK_01 (800.4s -> v2: 761.6s)", "quality": 9, "physics": 9, "similarity": 9, "lipsync": 8, "notes": "v1 rejected for 4-9s pan-right & dragon mascot; v2 locked camera cleanly on Gigi for all 10s with crisp SWAT movement behind glass.", "revisions": "v2 APPROVED. Overlay clean DK_01.mp3 at t=0 and trim cleanly after dialogue tail."},
            {"shot": "DK_02 (457.2s)", "quality": 9, "physics": 9, "similarity": 9, "lipsync": 9, "notes": "Custom designed Joker voice + Nolan interrogation push-in dead-on; slight mouth slur on final 1.2s silence.", "revisions": "Trim point set to 5.4s; silence-trim added to preflight for future films."},
            {"shot": "DK_03 (521.2s)", "quality": 9, "physics": 9, "similarity": 9, "lipsync": 8, "notes": "Damon Batsuit straight-on framing clean with zero face morph; slight slur on 'unlocked' at 5.5s.", "revisions": "Approved (native voice muted, clean DK_03.mp3 anchored at t=0)."},
            {"shot": "DK_04 (456.1s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 9, "notes": "Dead-on two-shot profile Joker leaning toward Batman's gauntlets; slight trailing word echo at 6.1s.", "revisions": "Approved with clean trim at 6.0s."},
            {"shot": "DK_05 (521.3s)", "quality": 9, "physics": 9, "similarity": 10, "lipsync": 8, "notes": "Overhead fluorescents slam on from dark to bright glare just like Nolan's cut.", "revisions": "Approved (overlay crisp DK_05.mp3 at t=0, mute native audio)."},
            {"shot": "DK_06 (330.8s)", "quality": 9, "physics": 9, "similarity": 9, "lipsync": 9, "notes": "Deron (conical hat & red dragon robe) holding siu mai in observation booth beside Gigi; slight 'dim sum' echo on final 0.4s.", "revisions": "Approved with clean 5.25s trim."},
            {"shot": "DK_07 (768.2s -> v2: 761.3s)", "quality": 9, "physics": 9, "similarity": 9, "lipsync": 8, "notes": "v1 rejected for red-line/scissors hallucination; v2 clean push-in on Gigi pointing chopsticks with crisp green glass reflection.", "revisions": "v2 APPROVED. Overlay clean DK_07.mp3 at t=0 and trim cleanly at 8.9s."},
            {"shot": "DK_08 (680.4s)", "quality": 10, "physics": 9, "similarity": 10, "lipsync": 9, "notes": "Smooth Nolan table circle around Joker & Batman with accurate mirror reflections; repeats 'and a little' at 7.8s tail.", "revisions": "Approved with clean 7.6s trim."},
            {"shot": "DK_09 (done)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 9, "notes": "Batman slams Joker's head against metal table cleanly on 'Word.' while gripping stomach in Zone-5 pain; dead-on interrogation framing.", "revisions": "Approved (overlay clean DK_09.mp3 at t=0 and trim cleanly at ~6.3s)."},
        ],
    },
    {
        "slug": "03_breaking_bad",
        "num": "03",
        "title": "Breaking Bad — Say My Name (New Mexico Desert)",
        "subtitle": "35mm High-Noon To'hajiilee Desert Standoff · Damon, Zach, Ajay, Hooman, Walter White & Gus Fring",
        "status": "Ingredients Ready · Queued",
        "status_cls": "",
        "mp4": "films/03_breaking_bad_1080p.mp4",
        "prep_time": "25m 37s",
        "render_time": "Queued for G4",
        "audit": [],
    },
    {
        "slug": "04_goodfellas",
        "num": "04",
        "title": "Goodfellas — \"Funny How?\" (Copacabana)",
        "subtitle": "Scorsese 1970s 35mm · Damon, Hooman, Deron, Zach, Tommy DeVito & Henry Hill",
        "status": "Ingredients Ready · Queued",
        "status_cls": "",
        "mp4": "films/04_goodfellas_1080p.mp4",
        "prep_time": "25m 37s",
        "render_time": "Queued for G4",
        "audit": [],
    },
    {
        "slug": "05_pulp_fiction",
        "num": "05",
        "title": "Pulp Fiction — Ezekiel 25:17 (Brett's Apartment)",
        "subtitle": "Tarantino 35mm Panavision · Damon, Deron, Zach, Jules Winnfield & Vincent Vega",
        "status": "Ingredients Ready · Queued",
        "status_cls": "",
        "mp4": "films/05_pulp_fiction_1080p.mp4",
        "prep_time": "25m 37s",
        "render_time": "Queued for G4",
        "audit": [],
    },
    {
        "slug": "06_jurassic_park",
        "num": "06",
        "title": "Jurassic Park — T-Rex Paddock Attack",
        "subtitle": "1993 Spielberg Tropical Night Storm · Damon, Gigi, Ajay & Sheren",
        "status": "Ingredients Ready · Queued",
        "status_cls": "",
        "mp4": "films/06_jurassic_park_1080p.mp4",
        "prep_time": "25m 37s",
        "render_time": "Queued for G4",
        "audit": [],
    },
    {
        "slug": "07_matrix",
        "num": "07",
        "title": "The Matrix — Red Pill / Magic Cone",
        "subtitle": "1999 Emerald-Green Noir · Damon, Deron, Hooman, Zach & Morpheus",
        "status": "Ingredients Ready · Queued",
        "status_cls": "",
        "mp4": "films/07_matrix_1080p.mp4",
        "prep_time": "25m 37s",
        "render_time": "Queued for G4",
        "audit": [],
    },
]

CSS = """
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #0b0d12; color: #e5e7eb; margin: 0; padding: 32px; max-width: 1280px; margin-inline: auto; }
a { color: #93c5fd; text-decoration: none; }
a:hover { text-decoration: underline; }
h1 { margin: 0 0 8px; font-size: 28px; letter-spacing: -0.02em; }
h2 { margin: 28px 0 12px; font-size: 20px; color: #f9fafb; }
p.sub { color: #9ca3af; margin: 0 0 24px; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(380px, 1fr)); gap: 24px; }
.ref-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }
.card { background: #141720; border: 1px solid #262b38; border-radius: 14px; padding: 18px; display: flex; flex-direction: column; gap: 10px; }
.card h2, .card h3 { margin: 0; font-size: 17px; color: #f9fafb; }
.badge { display: inline-block; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; padding: 3px 8px; border-radius: 999px; background: #1f2937; color: #93c5fd; width: fit-content; }
.badge.done { background: #064e3b; color: #6ee7b7; }
.meta { font-size: 13px; color: #9ca3af; line-height: 1.5; }
video, img { width: 100%; border-radius: 8px; background: #000; display: block; }
.actions { display: flex; gap: 10px; flex-wrap: wrap; margin-top: auto; }
a.btn { display: inline-block; text-align: center; padding: 9px 14px; border-radius: 8px; background: #2563eb; color: #fff; text-decoration: none; font-weight: 600; font-size: 13px; }
a.btn.sec { background: #1f2937; color: #e5e7eb; border: 1px solid #374151; }
a.btn:hover { opacity: 0.9; text-decoration: none; }
table { width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 13px; background: #141720; border-radius: 10px; overflow: hidden; }
th, td { padding: 10px 12px; border-bottom: 1px solid #262b38; text-align: left; vertical-align: top; }
th { background: #1b202c; color: #93c5fd; font-weight: 600; }
.score { font-weight: 700; color: #6ee7b7; }
.prompt { font-size: 12px; color: #9ca3af; line-height: 1.4; }
"""


def build():
    os.makedirs(f"{BASE}/detail", exist_ok=True)
    cards_html = []

    for f in FILMS:
        slug = f["slug"]
        has_mp4 = os.path.exists(f"{BASE}/{f['mp4']}")
        yt_frames = sorted(glob.glob(f"{BASE}/refs/yt/{slug}/*.jpg"))
        ref_frames = sorted(glob.glob(f"{BASE}/refs/{slug}/*.jpg"))

        jobs_path = f"{BASE}/scripts/{slug}_jobs.json"
        script_path = f"{BASE}/scripts/{slug}_script.json"
        jobs = json.load(open(jobs_path)) if os.path.exists(jobs_path) else []
        script = json.load(open(script_path)) if os.path.exists(script_path) else {}
        shots_by_id = {s["shot_id"].lower(): s for s in script.get("shots", [])}

        # Card for index.html
        video_block = ""
        dl_btn = ""
        if has_mp4:
            video_block = f'<video controls playsinline src="{f["mp4"]}"></video>'
            dl_btn = f'<a class="btn" href="{f["mp4"]}" download="{os.path.basename(f["mp4"])}">Download 1080p MP4</a>'

        cards_html.append(f"""
    <div class="card">
      <span class="badge {f['status_cls']}">{html_mod.escape(f['status'])}</span>
      <h2>{f['num']}. {html_mod.escape(f['title'])}</h2>
      <div class="meta">{html_mod.escape(f['subtitle'])}<br/>
        Ingredients: {len(jobs) or len(ref_frames)} shots · {len(yt_frames)} YouTube refs · Prep: {html_mod.escape(f['prep_time'])} · Render: {html_mod.escape(f['render_time'])}
      </div>
      {video_block}
      <div class="actions">
        {dl_btn}
        <a class="btn sec" href="detail/{slug}.html">References &amp; QA Audit →</a>
      </div>
    </div>""")

        # Detail page
        yt_cards = []
        for yp in yt_frames:
            rel = f"../refs/yt/{slug}/{os.path.basename(yp)}"
            yt_cards.append(f'<div class="card"><img src="{rel}" alt="{os.path.basename(yp)}" /><div class="meta">{os.path.basename(yp)}</div></div>')
        if not yt_cards:
            yt_cards.append('<div class="card"><div class="meta">Pilot prototype (pre-YouTube sampler).</div></div>')

        mm_cards = []
        if jobs:
            for j in jobs:
                sid = j["prefix"].split("_", 1)[1] if "_" in j["prefix"] else j["prefix"]
                smeta = shots_by_id.get(sid, {})
                img_name = j["images"][0]
                rel = f"../refs/{slug}/{img_name}"
                dur_s = j["length"] / 24.0
                spk = smeta.get("speaker", "")
                line = smeta.get("exact_dialogue", "")
                mm_cards.append(f"""
      <div class="card">
        <img src="{rel}" alt="{html_mod.escape(img_name)}" />
        <h3>{html_mod.escape(j['prefix'].upper())} · {html_mod.escape(spk)} ({dur_s:.1f}s)</h3>
        <div class="meta"><b>Keyframe:</b> {html_mod.escape(img_name)}</div>
        <div class="meta"><b>Line:</b> "{html_mod.escape(line)}"</div>
        <div class="prompt"><b>Prompt:</b> {html_mod.escape(j['prompt'])}</div>
      </div>""")
        else:
            for rp in ref_frames:
                rel = f"../refs/{slug}/{os.path.basename(rp)}"
                mm_cards.append(f'<div class="card"><img src="{rel}" alt="{os.path.basename(rp)}" /><div class="meta">{os.path.basename(rp)}</div></div>')

        audit_rows = []
        for a in f["audit"]:
            audit_rows.append(f"""
        <tr>
          <td><b>{html_mod.escape(a['shot'])}</b></td>
          <td class="score">{a['quality']}/10</td>
          <td class="score">{a['physics']}/10</td>
          <td class="score">{a['similarity']}/10</td>
          <td class="score">{a['lipsync']}/10</td>
          <td>{html_mod.escape(a['notes'])}</td>
          <td>{html_mod.escape(a['revisions'])}</td>
        </tr>""")
        if not audit_rows:
            audit_rows.append('<tr><td colspan="7" class="meta">Pending render — clip-by-clip QA scores and revision notes will populate as each shot finishes.</td></tr>')

        detail_video = f'<video controls playsinline src="../{f["mp4"]}" style="max-width:760px;margin:16px 0;"></video>' if has_mp4 else ""

        detail_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{f['num']}. {html_mod.escape(f['title'])} — Ingredients &amp; QA</title>
  <style>{CSS}</style>
</head>
<body>
  <p><a href="../index.html">← Back to Studio Hub</a></p>
  <span class="badge {f['status_cls']}">{html_mod.escape(f['status'])}</span>
  <h1 style="margin-top:8px;">{f['num']}. {html_mod.escape(f['title'])}</h1>
  <p class="sub">{html_mod.escape(f['subtitle'])} · Ingredient Prep: {html_mod.escape(f['prep_time'])} · Render Time: {html_mod.escape(f['render_time'])}</p>
  {detail_video}

  <h2>1. YouTube Reference Frame Extraction ({len(yt_frames)} shots sampled)</h2>
  <p class="sub">Original movie frames extracted directly from the scene to match camera angles, lenses, lighting contrast, and color palette.</p>
  <div class="ref-grid">{''.join(yt_cards)}</div>

  <h2>2. MiniMax H3 Reference Frames &amp; Shot Ingredients ({len(jobs) or len(ref_frames)} shots)</h2>
  <p class="sub">Every keyframe, spoken line, duration, and prompt queued for MiniMax H3 prior to rendering.</p>
  <div class="ref-grid">{''.join(mm_cards)}</div>

  <h2>3. Director's QA Audit &amp; Revision History</h2>
  <table>
    <thead>
      <tr><th>Shot</th><th>Quality</th><th>Physics</th><th>Movie Match</th><th>Lip Sync</th><th>Inspection Notes</th><th>Revisions</th></tr>
    </thead>
    <tbody>{''.join(audit_rows)}</tbody>
  </table>
</body>
</html>"""
        open(f"{BASE}/detail/{slug}.html", "w").write(detail_html)

    index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Nomad Cinema Parodies — 1080p Studio Hub</title>
  <style>{CSS}</style>
</head>
<body>
  <h1>Nomad Cinema Parodies</h1>
  <p class="sub">Shot-for-shot 1080p iconic movie scene recreations starring the Nomads · MiniMax H3 + ElevenLabs + YouTube Frame Sampling</p>
  <div class="grid" id="films">{''.join(cards_html)}
  </div>
</body>
</html>"""
    open(f"{BASE}/index.html", "w").write(index_html)
    print("SITE_BUILT_SUCCESSFULLY")


if __name__ == "__main__":
    build()
