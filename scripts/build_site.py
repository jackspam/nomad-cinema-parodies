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
        "status": "1080p Ready",
        "status_cls": "done",
        "mp4": "films/02_dark_knight_1080p.mp4",
        "prep_time": "25m 37s",
        "render_time": "100% QA Passed (13 MiniMax H3 + 7 LTX-2.5 maniacal Joker & rescue shots, 2m 24s 1080p master)",
        "audit": [
            {"shot": "DK_01 (800.4s -> v2: 761.6s)", "quality": 9, "physics": 9, "similarity": 9, "lipsync": 8, "notes": "v1 rejected for 4-9s pan-right & dragon mascot; v2 locked camera cleanly on Gigi for all 10s with crisp SWAT movement behind glass.", "revisions": "v2 APPROVED. Clean DK_01.mp3 anchored at t=0."},
            {"shot": "DK_02 (LTX-2.5 207.5s cold · maniacal v4)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Upgraded to ElevenLabs v4 Maniacal Theatrical Joker voice + LTX-2.5 IA2V; crisp Heath Ledger posture, tongue-flick acting, verbatim audio lock.", "revisions": "LTX-2.5 v4 APPROVED (10/10 across all metrics)."},
            {"shot": "DK_03 (521.2s)", "quality": 9, "physics": 9, "similarity": 9, "lipsync": 8, "notes": "Damon Batsuit straight-on framing clean with zero face morph.", "revisions": "Approved (native voice muted, clean DK_03.mp3 anchored at t=0)."},
            {"shot": "DK_04 (LTX-2.5 105.1s · locked-cowl v2)", "quality": 9, "physics": 9, "similarity": 10, "lipsync": 10, "notes": "Locked two-shot profile keeping Batman's black cowl sealed cleanly without morphing while Joker leans in with manic intensity.", "revisions": "LTX-2.5 v2 APPROVED (trimmed cleanly at 8.15s)."},
            {"shot": "DK_05 (521.3s)", "quality": 9, "physics": 9, "similarity": 10, "lipsync": 8, "notes": "Overhead fluorescents slam on from dark to bright glare just like Nolan's cut.", "revisions": "Approved (overlay crisp DK_05.mp3 at t=0)."},
            {"shot": "DK_06 (330.8s)", "quality": 9, "physics": 9, "similarity": 9, "lipsync": 9, "notes": "Deron (conical hat & red dragon robe) holding siu mai in observation booth beside Gigi.", "revisions": "Approved with clean trim."},
            {"shot": "DK_07 (768.2s -> v2: 761.3s)", "quality": 9, "physics": 9, "similarity": 9, "lipsync": 8, "notes": "v1 rejected for red-line/scissors hallucination; v2 clean push-in on Gigi pointing chopsticks with crisp green glass reflection.", "revisions": "v2 APPROVED."},
            {"shot": "DK_08 (LTX-2.5 65.0s · maniacal v4)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Smooth Nolan table circle around Joker & Batman with accurate mirror reflections and expressive Joker voice.", "revisions": "LTX-2.5 v4 APPROVED."},
            {"shot": "DK_09 (done)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 9, "notes": "Batman slams Joker's head against metal table cleanly on 'Word.' while gripping stomach in Zone-5 pain.", "revisions": "Approved."},
            {"shot": "DK_10 (328.9s)", "quality": 8, "physics": 8, "similarity": 9, "lipsync": 9, "notes": "Deron enters doorway in red silk dragon robe & conical hat holding 99 Ranch takeout, iced boba, and Po Chai Pills.", "revisions": "Approved."},
            {"shot": "DK_11 (LTX-2.5 45.0s · maniacal v4)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Dead-on low angle of Joker resting chin on steel table staring up at Deron's straw hat brim; zero tail slur.", "revisions": "LTX-2.5 v4 APPROVED."},
            {"shot": "DK_12 (387.5s)", "quality": 9, "physics": 9, "similarity": 9, "lipsync": 8, "notes": "Deron leans by white cinderblock holding Po Chai Pills & Clippers line.", "revisions": "Approved (overlay crisp DK_12.mp3 at t=0)."},
            {"shot": "DK_13 (680.3s -> v2)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 9, "notes": "v1 rejected for foreground officer ghosting; v2 locked camera keeping all three officers 100% solid while Hooman animates crisply on CRT.", "revisions": "v2 APPROVED (CRT bandpass EQ applied)."},
            {"shot": "DK_14 (456.2s)", "quality": 9, "physics": 9, "similarity": 9, "lipsync": 9, "notes": "Gigi storms doorway swinging wooden pointer at ceiling CRT monitor delivering 'flushable wipes' line.", "revisions": "Approved."},
            {"shot": "DK_15 (600.3s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 9, "notes": "Crisp push-in on Hooman inside CRT monitor holding gilded Magic Cone and brochure with Joker parody graphic.", "revisions": "Approved (CRT bandpass EQ applied)."},
            {"shot": "DK_16 (457.0s -> v2: 456.3s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 8, "notes": "v1 ghosting resolved in locked-frame v2 keeping Gigi slamming hands across table cleanly.", "revisions": "v2 APPROVED."},
            {"shot": "DK_17 (LTX-2.5 65.0s · maniacal v4)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "MiniMax v1 hallucinated blonde stranger; LTX-2.5 v2 keeps solo Joker laughing hysterically over Gigi's rant.", "revisions": "LTX-2.5 v2 APPROVED (10/10)."},
            {"shot": "DK_18 (457.2s)", "quality": 9, "physics": 9, "similarity": 9, "lipsync": 8, "notes": "Damon lifts Batsuit sleeve checking white Freestyle Libre CGM sensor on tricep cleanly at table.", "revisions": "Approved."},
            {"shot": "DK_19 (LTX-2.5 40.0s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "MiniMax v1 spawned cape duplicate; LTX-2.5 renders solo Deron swinging door & tipping boba with zero extras.", "revisions": "LTX-2.5 APPROVED."},
            {"shot": "DK_20 (LTX-2.5 80.0s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Gigi pulls breaker switch & yanks plug in silence while CRT collapses to a dot during Hooman's Encino pitch.", "revisions": "LTX-2.5 APPROVED (trimmed cleanly at 6.75s with DK_20_clean.mp3 & CRT EQ)."},
        ],
        "bench": [
            {
                "shot": "DK_02 (7.5s · maniacal v4)",
                "ltx_time": "207.5s (cold load)",
                "mm_time": "457.2s (L4)",
                "ltx_scores": "10 / 10 / 10 / 10",
                "mm_scores": "9 / 9 / 9 / 9",
                "ltx_mp4": "../films/ltx25_bench/ltx25_dk_02.mp4",
                "mm_mp4": "../films/ltx25_bench/dk_dk_02.mp4",
                "notes": "Upgraded ElevenLabs v4 maniacal Joker voice locked verbatim in LTX-2.5 with crisp Heath Ledger posture & lip sync.",
            },
            {
                "shot": "DK_04 (8.4s · maniacal v4)",
                "ltx_time": "105.1s (4.3x faster)",
                "mm_time": "456.1s (L4)",
                "ltx_scores": "9 / 9 / 10 / 10",
                "mm_scores": "10 / 10 / 10 / 9",
                "ltx_mp4": "../films/ltx25_bench/ltx25_dk_04.mp4",
                "mm_mp4": "../films/ltx25_bench/dk_dk_04.mp4",
                "notes": "Locked two-shot profile keeping Batman's black cowl sealed cleanly while Joker delivers 'put a smile on that colon' verbatim.",
            },
            {
                "shot": "DK_05 (6.9s · 169f vs 192f)",
                "ltx_time": "50.0s (10.4x faster)",
                "mm_time": "521.3s (L4)",
                "ltx_scores": "9 / 10 / 9 / 10",
                "mm_scores": "9 / 9 / 10 / 8",
                "ltx_mp4": "../films/ltx25_bench/ltx25_dk_05.mp4",
                "mm_mp4": "../films/ltx25_bench/dk_dk_05.mp4",
                "notes": "50 seconds on A100; Damon slams gauntlets on table with crisp facial likeness & dead-on lip sync (no voice slurring).",
            },
        ],
    },
    {
        "slug": "03_breaking_bad",
        "num": "03",
        "title": "Breaking Bad — Say My Name (New Mexico Desert)",
        "subtitle": "35mm High-Noon To'hajiilee Desert Standoff · Damon, Zach, Ajay, Hooman, Walter White & Gus Fring",
        "status": "1080p Ready",
        "status_cls": "done",
        "mp4": "films/03_breaking_bad_1080p.mp4",
        "prep_time": "25m 37s",
        "render_time": "100% QA Passed (14 MiniMax H3 + 6 LTX-2.5 desert rescue & upgrade shots, 2m 18s 1080p master)",
        "audit": [
            {"shot": "BB_02 (LTX-2.5 110.1s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "MiniMax v1 spawned blue glare; LTX-2.5 keeps razor-sharp Heisenberg close-up in New Mexico desert with Chrysler & Land Cruiser behind.", "revisions": "LTX-2.5 APPROVED (10/10)."},
            {"shot": "BB_03 (168.0s)", "quality": 9, "physics": 10, "similarity": 10, "lipsync": 8, "notes": "Crisp 100% solid foreground Walter shoulder & Damon clutching sweaty tank top in harsh desert sun.", "revisions": "Approved (clean BB_03.mp3 at t=0)."},
            {"shot": "BB_04 (144.0s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 9, "notes": "Zach sits in brown Alo jacket holding iPhone with visible ChatGPT UI & Fleetwood RV behind him.", "revisions": "Approved."},
            {"shot": "BB_05 (144.0s)", "quality": 9, "physics": 9, "similarity": 10, "lipsync": 8, "notes": "Ajay in blue scrubs & headlamp beside red 1984 Porsche 911 & RV gesturing with surgical micro-drill.", "revisions": "Approved."},
            {"shot": "BB_06 (120.0s)", "quality": 10, "physics": 9, "similarity": 10, "lipsync": 8, "notes": "Tight 50mm intense Bryan Cranston glare with dusty black Chrysler 300 in desert behind him.", "revisions": "Approved."},
            {"shot": "BB_07 (120.0s)", "quality": 9, "physics": 9, "similarity": 10, "lipsync": 8, "notes": "Ajay grins warmly beneath LED headlamp holding surgical drill beside red 911.", "revisions": "Approved."},
            {"shot": "BB_08 (LTX-2.5 50.0s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "MiniMax v1 panned to wrong speaker; LTX-2.5 locks all 4 desert figures rock-solid while only Zach reacts with Starlink alert.", "revisions": "LTX-2.5 APPROVED (10/10)."},
            {"shot": "BB_09 (168.0s)", "quality": 9, "physics": 9, "similarity": 10, "lipsync": 8, "notes": "Damon gripping stomach in sweat-damp tank beside Walter White with black Escalade in sun.", "revisions": "Approved."},
            {"shot": "BB_10 (104.2s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Razor-sharp Giancarlo Esposito in mustard Los Pollos shirt beside black Escalade under To'hajiilee sun.", "revisions": "Approved."},
            {"shot": "BB_11 (LTX-2.5 55.0s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "MiniMax v1 cloned Gus Fring; LTX-2.5 locks wide 4-person desert standoff cleanly while Walter speaks.", "revisions": "LTX-2.5 APPROVED (10/10)."},
            {"shot": "BB_12 (104.0s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 9, "notes": "Rock-solid wide desert standoff framing all four cast motionless under cobalt sky.", "revisions": "Approved."},
            {"shot": "BB_13 (120.0s)", "quality": 9, "physics": 9, "similarity": 10, "lipsync": 8, "notes": "Zach smiling earnestly beside vintage RV holding ChatGPT phone.", "revisions": "Approved."},
            {"shot": "BB_14 (216.1s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 8, "notes": "Hooman in gleaming gold silk shoving white Magic Cone toward stone-faced Gus Fring beside Escalade.", "revisions": "Approved."},
            {"shot": "BB_15 (120.0s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 8, "notes": "Crisp Giancarlo Esposito reaction beside black Escalade squinting toward Hooman.", "revisions": "Approved."},
            {"shot": "BB_16 (160.3s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 8, "notes": "Hooman pitches animatedly with gold wallet and Magic Cone inches from stoic Gus Fring.", "revisions": "Approved."},
            {"shot": "BB_17 (120.0s)", "quality": 9, "physics": 9, "similarity": 10, "lipsync": 8, "notes": "Gus Fring coolly dismissive in high-noon Escalade shadow.", "revisions": "Approved."},
            {"shot": "BB_18 (LTX-2.5 80.0s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Damon speaks deadpan in wide 4-shot ('street tacos, Gustavo') with zero cloning or drift.", "revisions": "LTX-2.5 APPROVED (10/10)."},
            {"shot": "BB_19 (LTX-2.5 50.0s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Zach checks Olive Tree ChatGPT text in wide desert standoff while all other actors hold steady.", "revisions": "LTX-2.5 APPROVED (10/10)."},
            {"shot": "BB_20 (LTX-2.5 125.4s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Hooman pitches rattlesnake shovel & Encino SUVs holding Magic Cone with verbatim v4 audio lock.", "revisions": "LTX-2.5 APPROVED (trimmed cleanly at 8.45s with BB_20_clean.mp3)."},
            {"shot": "BB_21 (104.0s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 9, "notes": "Menacing Walter White desert finale looking dead down the barrel under red New Mexico mesas.", "revisions": "Approved."},
        ],
    },
    {
        "slug": "04_goodfellas",
        "num": "04",
        "title": "Goodfellas — \"Funny How?\" (Copacabana)",
        "subtitle": "Scorsese 1970s 35mm · Damon, Hooman, Deron, Zach, Tommy DeVito & Henry Hill",
        "status": "Ingredients Ready · Queued for LTX-2.5 (A100)",
        "status_cls": "",
        "mp4": "films/04_goodfellas_1080p.mp4",
        "prep_time": "25m 37s",
        "render_time": "Queued for LTX-2.5 on A100 (colab-gpu2)",
        "audit": [],
    },
    {
        "slug": "05_pulp_fiction",
        "num": "05",
        "title": "Pulp Fiction — Ezekiel 25:17 (Brett's Apartment)",
        "subtitle": "Tarantino 35mm Panavision · Damon, Deron, Zach, Jules Winnfield & Vincent Vega",
        "status": "Ingredients Ready · Rendering on L4 (colab-gpu3)",
        "status_cls": "",
        "mp4": "films/05_pulp_fiction_1080p.mp4",
        "prep_time": "25m 37s",
        "render_time": "Rendering on L4 (colab-gpu3)",
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

        bench_section = ""
        if f.get("bench"):
            b_cards = []
            for b in f["bench"]:
                b_cards.append(f"""
        <div class="card">
          <h3>{html_mod.escape(b['shot'])}</h3>
          <div class="meta"><b>LTX-2.5 (A100 40GB):</b> {html_mod.escape(b['ltx_time'])} · Scores (Q/P/M/L): <span class="score">{b['ltx_scores']}</span></div>
          <video controls playsinline src="{b['ltx_mp4']}"></video>
          <div class="meta"><b>MiniMax H3 (L4):</b> {html_mod.escape(b['mm_time'])} · Scores (Q/P/M/L): <span class="score">{b['mm_scores']}</span></div>
          <video controls playsinline src="{b['mm_mp4']}"></video>
          <div class="meta">{html_mod.escape(b['notes'])}</div>
        </div>""")
            bench_section = f"""
  <h2>4. LTX-2.5 vs MiniMax H3 Side-by-Side Speed &amp; Quality Benchmark</h2>
  <p class="sub">Direct A/B test at 1344×768 on Colab A100 (LTX-2.5 Distilled 8+3 steps with locked ElevenLabs audio latent) vs Colab L4 (MiniMax H3 4-step). LTX-2.5 rendered ~10× faster warm (45–50s vs 456–521s) with 100% verbatim ElevenLabs voice preservation.</p>
  <div class="grid">{''.join(b_cards)}</div>"""

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
  {bench_section}
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
