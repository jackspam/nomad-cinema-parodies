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
        "data_slug": "02_dark_knight_v2",
        "num": "02",
        "title": "The Dark Knight — The Interrogation Room (v2)",
        "subtitle": "35mm Panavision Scope · Hooman, Damon, Gigi, Deron & Zach",
        "status": "In Progress — 14/40 Shots Verified",
        "status_cls": "done",
        "hide_video": True,
        "preview_url": "preview.html",
        "mp4": "films/02_dark_knight_1080p.mp4",
        "prep_time": "v2 Rebuild Active",
        "render_time": "14/40 SyncNet + Expression Verified (LTX-2.5 + InfiniteTalk Hybrid)",
        "audit": [
            {"shot": "DK2_01..04", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 9, "notes": "Act 1 opening Gigi & Hooman dark interrogation table confrontation.", "revisions": "LTX-2.5 VERIFIED (LSE-C 5.61, 7.53, 6.52, 7.34)."},
            {"shot": "DK2_05..10", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Hooman Encino escrow pitch, Gigi closing night shift, and fluorescent reveal.", "revisions": "Hybrid LTX-2.5 + InfiniteTalk VERIFIED (LSE-C 7.69, 8.38, 6.19, 6.70, 4.95, 7.21)."},
            {"shot": "DK2_11..12, 17, 19", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Cowl-less Damon confrontation & Hooman Beverly Hills hair-plugs retort.", "revisions": "VERIFIED (LSE-C 7.23, 6.56, 7.07, 6.75). Remaining 26 shots rendering now."},
        ],
    },
    {
        "slug": "03_breaking_bad",
        "num": "03",
        "title": "Breaking Bad — Say My Name (New Mexico Desert)",
        "subtitle": "35mm High-Noon To'hajiilee Desert Standoff · Damon, Zach, Ajay, Hooman, Walter White & Gus Fring",
        "status": "Rejected — Queued for v2 Rebuild",
        "status_cls": "rejected",
        "hide_video": True,
        "mp4": "films/03_breaking_bad_1080p.mp4",
        "prep_time": "v1 Archived",
        "render_time": "Queued for v2 rebuild with Nomads-only casting & SyncNet gating",
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
        "status": "Rejected — Queued for v2 Rebuild",
        "status_cls": "rejected",
        "hide_video": True,
        "mp4": "films/04_goodfellas_1080p.mp4",
        "prep_time": "v1 Archived",
        "render_time": "Queued for v2 rebuild with Nomads-only casting & SyncNet gating",
        "audit": [
            {"shot": "GF_01 (LTX-2.5)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Smooth Scorsese booth push-in across Henry Hill under Copacabana tungsten lamp.", "revisions": "Approved (10/10)."},
            {"shot": "GF_02 (LTX-2.5)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Deron between Paulie and Henry with calamari plate & chopsticks.", "revisions": "Approved (10/10)."},
            {"shot": "GF_03 (LTX-2.5)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Explosive Tommy DeVito 'Emperor of Monterey Park!' glare with verbatim v4 lip sync.", "revisions": "Approved (10/10)."},
            {"shot": "GF_04 (LTX-2.5 130.1s v2)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "v1 mouthed by center gangster; locked solo-left Zach prompt fixed lip sync cleanly to Zach scrolling X.", "revisions": "v2 APPROVED (10/10)."},
            {"shot": "GF_05 (LTX-2.5)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Damon gripping stomach in open tuxedo over singlet under warm booth lamp.", "revisions": "Approved (10/10)."},
            {"shot": "GF_06 (LTX-2.5)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Deron lifting calamari ring with chopsticks praising Din Tai Fung soup dumplings.", "revisions": "Approved (10/10)."},
            {"shot": "GF_07 (LTX-2.5)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Wide 6-person Copacabana booth shot; all cast steady while Damon pitches Deron's joke.", "revisions": "Approved (10/10)."},
            {"shot": "GF_08 (LTX-2.5)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Signature Joe Pesci slow menace push-in ('Funny how?! Am I a clown to you?').", "revisions": "Approved (10/10)."},
            {"shot": "GF_09 (LTX-2.5)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Damon calm smug smile across table ('LA County jail—jail, never prison').", "revisions": "Approved (10/10)."},
            {"shot": "GF_10 (LTX-2.5)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Deron beaming between Paulie and Henry comparing Tommy to a Stephen Chow movie.", "revisions": "Approved (10/10)."},
            {"shot": "GF_11 (LTX-2.5)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Tommy erupting over fake Rolex with whiskey glass raised.", "revisions": "Approved (10/10)."},
            {"shot": "GF_12 (LTX-2.5 50.0s v2)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "v1 Tommy echoed mouthing; v2 locks ONLY Zach speaking while Tommy glares silently.", "revisions": "v2 APPROVED (10/10)."},
            {"shot": "GF_13 (LTX-2.5)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Hooman in burgundy waiter jacket carrying glowing Magic Cone on silver tray.", "revisions": "Approved (10/10)."},
            {"shot": "GF_14 (LTX-2.5)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Henry squinting across booth asking who put a Persian cable channel on TV.", "revisions": "Approved (10/10)."},
            {"shot": "GF_15 (LTX-2.5)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Hooman pitching 50/50 Copacabana Magic Cone deal beside booth.", "revisions": "Approved (10/10)."},
            {"shot": "GF_16 (LTX-2.5)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Tommy yelling 'Take that bronze cylinder out of here right now!'.", "revisions": "Approved (10/10)."},
            {"shot": "GF_17 (LTX-2.5)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Damon standing hurriedly clutching Zone-5 CGM flare-up.", "revisions": "Approved (10/10)."},
            {"shot": "GF_18 (LTX-2.5)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Deron waving calamari with fake Rolex gag.", "revisions": "Approved (10/10)."},
            {"shot": "GF_19 (LTX-2.5 95.1s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Hooman slams silver tray beside table shouting Encino pitch right in Tommy's face.", "revisions": "Approved (trimmed cleanly at 10.90s with GF_19_clean.mp3 to remove trailing gibberish)."},
            {"shot": "GF_20 (LTX-2.5 85.0s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Damon closes out with Copacabana booth confession.", "revisions": "Approved (trimmed cleanly at 7.95s with GF_20_clean.mp3 to drop ElevenLabs repeat)."},
        ],
    },
    {
        "slug": "05_pulp_fiction",
        "num": "05",
        "title": "Pulp Fiction — Ezekiel 25:17 (Brett's Apartment)",
        "subtitle": "Tarantino 35mm Panavision · Damon, Deron, Zach, Jules Winnfield & Vincent Vega",
        "status": "Rejected — Queued for v2 Rebuild",
        "status_cls": "rejected",
        "hide_video": True,
        "mp4": "films/05_pulp_fiction_1080p.mp4",
        "prep_time": "v1 Archived",
        "render_time": "Queued for v2 rebuild with Nomads-only casting & SyncNet gating",
        "audit": [
            {"shot": "PF_01 (LTX-2.5 191.0s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Jules Winnfield doorway interrogation ('Royale with Cheese') with dead-on Samuel L. Jackson cadence.", "revisions": "Approved (10/10)."},
            {"shot": "PF_02 (LTX-2.5 420.4s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Damon holding stomach in apartment hallway next to Vincent Vega.", "revisions": "Approved (trimmed cleanly at 7.50s with PF_02_clean.mp3)."},
            {"shot": "PF_03 (LTX-2.5 195.2s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Jules scowling in morning blinds ('7:22 in the AM! Discuss hospitality!').", "revisions": "Approved (10/10)."},
            {"shot": "PF_04 (LTX-2.5 140.1s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Deron in dragon silk robe biting Big Kahuna Burger by Sprite cup.", "revisions": "Approved (10/10)."},
            {"shot": "PF_05 (LTX-2.5 115.1s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Vincent Vega baffled beside Jules ('Who ordered dim sum at 7am?').", "revisions": "Approved (10/10)."},
            {"shot": "PF_06 (LTX-2.5 140.2s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Deron critiquing dry burger bun vs Monterey Park dumplings.", "revisions": "Approved (10/10)."},
            {"shot": "PF_07 (LTX-2.5 145.1s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Jules eyeing Big Kahuna Burger ('Mmmm! This IS a tasty burger!').", "revisions": "Approved (10/10)."},
            {"shot": "PF_08 (LTX-2.5 210.1s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Zach leaning in brown Alo jacket against vintage green kitchen counter laughing on X.", "revisions": "Approved (10/10)."},
            {"shot": "PF_09 (LTX-2.5 155.1s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Vincent glaring at Zach's UPS jacket seed-oil lecture.", "revisions": "Approved (10/10)."},
            {"shot": "PF_10 (LTX-2.5 165.3s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Damon asking for Miranda warning & bathroom key in apartment hallway.", "revisions": "Approved (10/10)."},
            {"shot": "PF_11 (LTX-2.5 140.1s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Explosive Jules Winnfield 'Does he look like a BITCH?!' close-up.", "revisions": "Approved (10/10)."},
            {"shot": "PF_12 (LTX-2.5 145.1s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Deron comparing Marsellus Wallace to Clippers coach with zero rings.", "revisions": "Approved (10/10)."},
            {"shot": "PF_13 (LTX-2.5 195.1s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Zach cheerfully announcing 30% off olive trees from ChatGPT at kitchen sink.", "revisions": "Approved (10/10)."},
            {"shot": "PF_14 (LTX-2.5 110.0s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Deron eating burger mid-standoff calmly pitching Magic Cone to Jules.", "revisions": "Approved (10/10)."},
            {"shot": "PF_15 (LTX-2.5 45.0s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Vincent checking collar wondering why a Persian briefcase salesman interrupted.", "revisions": "Approved (10/10)."},
            {"shot": "PF_16 (LTX-2.5)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Zach in kitchen corner pitching 50/50 pocket bidet on briefcase.", "revisions": "Approved (10/10)."},
            {"shot": "PF_17 (LTX-2.5 50.0s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Jules reciting Ezekiel 25:17 verbatim with booming v4 thunder SFX cleared.", "revisions": "Approved (10/10)."},
            {"shot": "PF_18 (LTX-2.5 65.0s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Damon briskly excusing himself ('Excuse me, Ezekiel. Moving on.').", "revisions": "Approved (10/10)."},
            {"shot": "PF_19 (LTX-2.5 40.0s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Deron nodding politely off to Alhambra soup dumplings after bathroom.", "revisions": "Approved (10/10)."},
            {"shot": "PF_20 (LTX-2.5 v2 silent-reaction)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Jules & Vincent stare silently with mouths locked closed while off-screen Hooman calls from Encino.", "revisions": "v2 APPROVED (speaker EQ + PF_20_clean.mp3 at 6.30s)."},
            {"shot": "PF_21 (LTX-2.5 45.1s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Vincent shrugging 'Let's go get a Royale with Cheese' closing beat.", "revisions": "Approved (10/10)."},
        ],
    },
    {
        "slug": "06_jurassic_park",
        "num": "06",
        "title": "Jurassic Park — T-Rex Paddock Attack",
        "subtitle": "1993 Spielberg Tropical Night Storm · Damon, Gigi, Ajay, Sheren & T-Rex",
        "status": "Rejected — Queued for v2 Rebuild",
        "status_cls": "rejected",
        "hide_video": True,
        "mp4": "films/06_jurassic_park_1080p.mp4",
        "prep_time": "v1 Archived",
        "render_time": "Queued for v2 rebuild with Nomads-only casting & SyncNet gating",
        "audit": [
            {"shot": "JP_01 (LTX-2.5 95.0s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Ajay with glowing LED headlamp diagnosing visible ripples in plastic water cups inside wet Explorer.", "revisions": "Approved (seismic bass thump layered)."},
            {"shot": "JP_02 (LTX-2.5 20.0s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Sheren behind Explorer #04 steering wheel ('No brakes!') with wipers sweeping rain.", "revisions": "Approved (10/10)."},
            {"shot": "JP_03 (LTX-2.5 215.4s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Gigi clutching glowing yellow flashlight by Explorer door scolding Sheren's speed.", "revisions": "Approved (10/10)."},
            {"shot": "JP_04 (LTX-2.5)", "quality": 9, "physics": 9, "similarity": 10, "lipsync": 10, "notes": "Sheren tossing flare light glow past wipers ('way too orange, watch this').", "revisions": "Approved (9/10)."},
            {"shot": "JP_05 (LTX-2.5 25.0s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Damon in wet yellow slicker with Freestyle Libre sensor inside amber palm-thatch stall.", "revisions": "Approved (10/10)."},
            {"shot": "JP_07 (LTX-2.5 160.1s action test)", "quality": 9, "physics": 9, "similarity": 10, "lipsync": 10, "notes": "First LTX-2.5 T-Rex action stress test: 40ft predator whips head & snaps paddock storm cables with off-camera Ajay VO.", "revisions": "Action Test APPROVED + booming T-Rex roar SFX."},
            {"shot": "JP_08 (LTX-2.5 25.0s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Sheren cranking Explorer wheel ('90 in reverse!') with rain-lashed glass glare.", "revisions": "Approved (10/10)."},
            {"shot": "JP_09 (LTX-2.5 195.3s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Gigi shining bright yellow flashlight into downpour ('1-2-3, eyes on me!').", "revisions": "Approved (10/10)."},
            {"shot": "JP_11 (LTX-2.5 25.0s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Damon inside shaking thatch stall ('locked inside with zero TP').", "revisions": "Approved (10/10)."},
            {"shot": "JP_12 (LTX-2.5 25.0s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Hero wide shot: Gigi pointing sternly under lightning as T-Rex towers behind Explorer ('runs worse than Elon's dumpster truck!').", "revisions": "Approved (10/10 + roar SFX)."},
            {"shot": "JP_13 (LTX-2.5 20.0s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Ajay offering 130 Hz thalamic DBS to T-Rex through windshield mist.", "revisions": "Approved (10/10)."},
            {"shot": "JP_14 (LTX-2.5 270.3s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Damon pointing deadpan upward from wooden stall ('LA County jail—jail, never prison').", "revisions": "Approved (10/10)."},
            {"shot": "JP_15 (LTX-2.5 135.2s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Sheren honking impatiently from Explorer wheel in storm.", "revisions": "Approved (car horn SFX)."},
            {"shot": "JP_16 (LTX-2.5 35.0s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Gigi holding Boonton clipboard below roaring T-Rex ('Your clip is on RED!').", "revisions": "Approved (10/10 + roar SFX)."},
            {"shot": "JP_17 (LTX-2.5 20.0s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Ajay beaming beside water cups celebrating Gigi curing dinosaur aggression.", "revisions": "Approved (10/10)."},
            {"shot": "JP_18 (LTX-2.5 170.1s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Damon back inside dry Explorer cabin beside water cup ('Zone-4 adrenaline cleared me').", "revisions": "Approved (10/10)."},
            {"shot": "JP_19 (LTX-2.5)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Sheren grinning maniacally peeling Explorer out in reverse.", "revisions": "Approved (horn & wet gravel SFX)."},
            {"shot": "JP_20 (LTX-2.5 160.1s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Gigi closing storm warning ('nobody tells Zach about that road flare!').", "revisions": "Approved (final T-Rex storm roar SFX)."},
        ],
    },
    {
        "slug": "07_matrix",
        "num": "07",
        "title": "The Matrix — Red Pill / Magic Cone",
        "subtitle": "1999 Emerald-Green Noir · Damon, Deron, Hooman, Zach & Morpheus",
        "status": "Rejected — Queued for v2 Rebuild",
        "status_cls": "rejected",
        "hide_video": True,
        "mp4": "films/07_matrix_1080p.mp4",
        "prep_time": "v1 Archived",
        "render_time": "Queued for v2 rebuild with Nomads-only casting & SyncNet gating",
        "audit": [
            {"shot": "MX_01 (LTX-2.5)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Morpheus in alligator leather armchair inside crumbling emerald Lafayette Hotel.", "revisions": "Approved (10/10)."},
            {"shot": "MX_02 (LTX-2.5)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Damon hunched in crimson chair gripping stomach ('Zion shrimp burrito mile 56').", "revisions": "Approved (10/10)."},
            {"shot": "MX_03 (LTX-2.5 25.0s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Morpheus holding up glowing coppertop battery in leather glove.", "revisions": "Approved (10/10)."},
            {"shot": "MX_04 (LTX-2.5)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Zach in brown UPS hoodie on emerald hotel divan holding bright iPhone.", "revisions": "Approved (10/10)."},
            {"shot": "MX_05 (LTX-2.5 25.0s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Morpheus glaring over pince-nez glasses at earth-brown joggers & flip-phone.", "revisions": "Approved (10/10)."},
            {"shot": "MX_06 (LTX-2.5 v2)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "v1 spawned bystander; v2 locked solo Deron with steaming tea by lightning window.", "revisions": "v2 APPROVED (10/10)."},
            {"shot": "MX_07 (LTX-2.5)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Iconic Red Pill vs Blue Pill palms framed sharply under storm lightning.", "revisions": "Approved (10/10)."},
            {"shot": "MX_08 (LTX-2.5)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Damon squinting anxiously ('contain loperamide? Municipal court at nine').", "revisions": "Approved (10/10)."},
            {"shot": "MX_09 (LTX-2.5)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Deron waving warm teacup pitching two-vial Po Chai Pills against red pill.", "revisions": "Approved (10/10)."},
            {"shot": "MX_10 (LTX-2.5)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Zach lounging with phone asking if Nebuchadnezzar irrigates olive trees.", "revisions": "Approved (10/10)."},
            {"shot": "MX_11 (LTX-2.5 60.0s v2)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "v1 grew floating TV over Hooman; v2 keeps Hooman crisp holding glowing cone + pill for full 14.8s.", "revisions": "v2 APPROVED (CRT bandpass EQ applied)."},
            {"shot": "MX_12 (LTX-2.5 20.3s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Morpheus snapping open Nokia slider yelling 'Kill that monitor immediately!'.", "revisions": "Approved (10/10)."},
            {"shot": "MX_13 (LTX-2.5)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Hooman chanting 'No spoon! Only cone!' with glowing Magic Cone.", "revisions": "Approved (CRT EQ applied)."},
            {"shot": "MX_14 (LTX-2.5)", "quality": 9, "physics": 9, "similarity": 10, "lipsync": 10, "notes": "Damon inspecting red capsule ('why am I sweating through a wetsuit?').", "revisions": "Approved (9/10)."},
            {"shot": "MX_15 (LTX-2.5)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Morpheus leaning forward intently ('Your mind makes it real, Damon').", "revisions": "Approved (10/10)."},
            {"shot": "MX_16 (LTX-2.5 25.0s v2)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "v1 cloned conical-hat twin; v2 locked solo Deron cheering over hot teacup.", "revisions": "v2 APPROVED (10/10)."},
            {"shot": "MX_17 (LTX-2.5 25.0s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Damon surging out of red armchair clutching stomach heading for bathroom.", "revisions": "Approved (10/10)."},
            {"shot": "MX_18 (LTX-2.5 30.0s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Zach warning nervously from divan ('ChatGPT says unplug right now!').", "revisions": "Approved (10/10)."},
            {"shot": "MX_19 (LTX-2.5 30.0s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Hooman wildly pitching Encino Matrix plumber through CRT monitor.", "revisions": "Approved (CRT EQ applied)."},
            {"shot": "MX_20 (LTX-2.5 25.0s)", "quality": 10, "physics": 10, "similarity": 10, "lipsync": 10, "notes": "Morpheus dark smirk closing out scene ('Disconnect the construct!').", "revisions": "Approved (10/10)."},
        ],
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
.badge.rejected { background: #7f1d1d; color: #fca5a5; }
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
        data_slug = f.get("data_slug", slug)
        has_mp4 = (not f.get("hide_video")) and os.path.exists(f"{BASE}/{f['mp4']}")
        yt_frames = sorted(glob.glob(f"{BASE}/refs/yt/{data_slug}/*.jpg")) or sorted(glob.glob(f"{BASE}/refs/yt/{data_slug}/sheets/*.jpg"))
        ref_frames = sorted(glob.glob(f"{BASE}/refs/{data_slug}/*.jpg"))

        jobs_path = f"{BASE}/scripts/{data_slug}_jobs.json"
        script_path = f"{BASE}/scripts/{data_slug}_script.json"
        jobs = json.load(open(jobs_path)) if os.path.exists(jobs_path) else []
        script = json.load(open(script_path)) if os.path.exists(script_path) else {}
        shots_by_id = {s["shot_id"].lower(): s for s in script.get("shots", [])}

        # Card for index.html
        video_block = ""
        dl_btn = ""
        if has_mp4:
            video_block = f'<video controls playsinline src="{f["mp4"]}"></video>'
            dl_btn = f'<a class="btn" href="{f["mp4"]}" download="{os.path.basename(f["mp4"])}">Download 1080p MP4</a>'
        preview_btn = f'<a class="btn" href="{f["preview_url"]}">Preview Passed Shots (14/40) →</a>' if f.get("preview_url") else ""

        cards_html.append(f"""
    <div class="card">
      <span class="badge {f['status_cls']}">{html_mod.escape(f['status'])}</span>
      <h2>{f['num']}. {html_mod.escape(f['title'])}</h2>
      <div class="meta">{html_mod.escape(f['subtitle'])}<br/>
        Ingredients: {len(jobs) or len(ref_frames)} shots · {len(yt_frames)} YouTube refs · Prep: {html_mod.escape(f['prep_time'])} · Render: {html_mod.escape(f['render_time'])}
      </div>
      {video_block}
      <div class="actions">
        {preview_btn}
        {dl_btn}
        <a class="btn sec" href="detail/{slug}.html">References &amp; QA Audit →</a>
      </div>
    </div>""")

        # Detail page
        yt_cards = []
        for yp in yt_frames:
            sub = "sheets/" if f"{os.sep}sheets{os.sep}" in yp else ""
            rel = f"../refs/yt/{data_slug}/{sub}{os.path.basename(yp)}"
            yt_cards.append(f'<div class="card"><img src="{rel}" alt="{os.path.basename(yp)}" /><div class="meta">{os.path.basename(yp)}</div></div>')
        if not yt_cards:
            yt_cards.append('<div class="card"><div class="meta">Pilot prototype (pre-YouTube sampler).</div></div>')

        mm_cards = []
        if jobs:
            for j in jobs:
                if "shot_id" in j:
                    sid = j["shot_id"].lower()
                    title_id = j["shot_id"]
                    img_name = j["start_image"]
                    dur_txt = f"{j.get('ltx_length', 121)/24.0:.1f}s"
                    prompt_txt = j.get("ltx_prompt", "")
                else:
                    sid = j["prefix"].split("_", 1)[1] if "_" in j["prefix"] else j["prefix"]
                    title_id = j["prefix"].upper()
                    img_name = j["images"][0]
                    dur_txt = f"{j['length']/24.0:.1f}s"
                    prompt_txt = j.get("prompt", "")
                smeta = shots_by_id.get(sid, {})
                rel = f"../refs/{data_slug}/{img_name}"
                spk = smeta.get("speaker", "")
                line = smeta.get("exact_dialogue", "")
                mm_cards.append(f"""
      <div class="card">
        <img src="{rel}" alt="{html_mod.escape(img_name)}" />
        <h3>{html_mod.escape(title_id)} · {html_mod.escape(spk)} ({dur_txt})</h3>
        <div class="meta"><b>Keyframe:</b> {html_mod.escape(img_name)}</div>
        <div class="meta"><b>Line:</b> "{html_mod.escape(line)}"</div>
        <div class="prompt"><b>Prompt:</b> {html_mod.escape(prompt_txt)}</div>
      </div>""")
        else:
            for rp in ref_frames:
                rel = f"../refs/{data_slug}/{os.path.basename(rp)}"
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
