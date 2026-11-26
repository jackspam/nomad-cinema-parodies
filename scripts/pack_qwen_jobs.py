"""Pack the 21 remaining / Hooman-likeness refinement keyframes for Qwen/Qwen-Image-Edit-2509 on dk2-g4."""
import json
import os
import shutil
import tarfile

BASE = "/Users/jack/.gemini/antigravity/scratch/nomad-cinema-parodies"
WORK = f"{BASE}/_tmp_qwen_dk2"
IN_DIR = f"{WORK}/in"
if os.path.exists(WORK):
    shutil.rmtree(WORK)
os.makedirs(IN_DIR, exist_ok=True)

HOOMAN_LIKENESS = (
    "Make the Joker's face unmistakably match the man in the final portrait image (Hooman: dark-brown eyes, wide nose, thick dark brows, "
    "shorter dark curly hair dyed streaked dark-green—NOT long blond hair—with his short dark mustache and chin goatee stubble subtly visible through "
    "patchy flaky cracked white theater greasepaint, smudged dark charcoal eye black, and rough smeared crimson mouth scars). "
    "Preserve the exact camera framing, greenish-beige cinderblock walls or shadows, cool fluorescent light, shirt/vest/coat, real skin pores, and 2008 35mm film grain. Zero waxy skin, mouth gently closed."
)
DAMON_LIKENESS = (
    "Remove the Batman cowl mask cleanly so the man from the portrait image (Damon: bald head, heavy black-framed glasses, tanned skin pores, forehead lines, salt-and-pepper stubble) "
    "sits naturally atop the high matte-black Batsuit armor collar and cape in the exact framing, greenish-beige interrogation walls, clinical fluorescent lighting, and 2008 35mm film grain. Zero waxy skin, mouth gently closed."
)

# Copy all needed local files into IN_DIR
def stage(rel_src, name=None):
    fn = name or os.path.basename(rel_src)
    shutil.copy2(f"{BASE}/{rel_src}", f"{IN_DIR}/{fn}")
    return fn

hooman_p = stage("refs/hooman-face-hd.png")
damon_p = stage("refs/damon-face-hd.png")
gigi_p = stage("refs/gigi-face-hd.png")
deron_p = stage("refs/deron-face-hd.png")
zach_p = stage("refs/zach-face-hd.png")

specs = [
    # 5 Hooman-likeness refinements (pass generated frame + Hooman portrait!)
    ("dk2_shot05_start.jpg", [stage("refs/02_dark_knight_v2/dk2_shot05_end.jpg", "ref_05_end.jpg"), hooman_p],
     "Slight angle shift matching dark interrogation shadows, dark purple coat over vest. " + HOOMAN_LIKENESS),
    ("dk2_shot29_end.jpg", [stage("refs/02_dark_knight_v2/dk2_shot29_end.jpg", "cur_29_end.jpg"), hooman_p],
     "Keep Damon's bald head on right and white brick wall identical; swap ONLY the pinned Joker face on the left. " + HOOMAN_LIKENESS),
    ("dk2_shot31_start.jpg", [stage("refs/02_dark_knight_v2/dk2_shot31_start.jpg", "cur_31_start.jpg"), hooman_p],
     "Keep Damon gripping Joker on the right and white brick wall identical; swap ONLY the left profile Joker face. " + HOOMAN_LIKENESS),
    ("dk2_shot31_end.jpg", [stage("refs/02_dark_knight_v2/dk2_shot31_end.jpg", "cur_31_end.jpg"), hooman_p],
     "Keep Damon gripping Joker on the right and white brick wall identical; swap ONLY the left profile Joker face. " + HOOMAN_LIKENESS),
    ("dk2_shot34_start.jpg", [stage("refs/02_dark_knight_v2/dk2_shot34_start.jpg", "cur_34_start.jpg"), hooman_p],
     "Keep the sprawled body pose across brushed steel table and hex shirt/green vest identical; refine ONLY the Joker head/face. " + HOOMAN_LIKENESS),

    # 16 remaining un-generated frames
    ("dk2_shot21_start.jpg", [stage("refs/yt/02_dark_knight_v2/frames/dk2_yt_0162.jpg"), damon_p],
     "Over-the-shoulder past blurred green-streaked foreground curls on left onto Damon-Batman on right. " + DAMON_LIKENESS),
    ("dk2_shot21_end.jpg", [stage("refs/yt/02_dark_knight_v2/frames/dk2_yt_0165.jpg"), damon_p],
     "Same bright OTS angle leaning closer toward foreground curls. " + DAMON_LIKENESS),
    ("dk2_shot22_start.jpg", [stage("refs/yt/02_dark_knight_v2/frames/dk2_yt_0166.jpg"), hooman_p],
     "Bright clinical medium CU coatless Joker in grey-lavender hex shirt & green vest leaning back. " + HOOMAN_LIKENESS),
    ("dk2_shot22_end.jpg", [stage("refs/yt/02_dark_knight_v2/frames/dk2_yt_0172.jpg"), hooman_p],
     "Same coatless bright CU tilting head sideways with raised hand near chest. " + HOOMAN_LIKENESS),
    ("dk2_shot28_start.jpg", [stage("refs/yt/02_dark_knight_v2/frames/dk2_yt_0242.jpg"), zach_p, gigi_p],
     "Dark cyan-shadowed police observation room profile watching glass to the right: replace foreground right man in open jacket looking at phone with Zach in dark brown jacket holding smartphone; replace center-left glasses cop with Gigi in charcoal trench coat and red glasses; keep silent background officers quietly in shadow. Exact 2008 35mm grain, mouths closed."),
    ("dk2_shot32_start.jpg", [stage("refs/yt/02_dark_knight_v2/frames/dk2_yt_0243.jpg"), gigi_p, deron_p],
     "Dark cyan-shadowed police observation room profile looking toward glass on right: place Gigi (red glasses, dark trench coat) leaning forward intensely with Deron (woven bamboo conical hat and red dragon silk robe) beside her and silent background officers in shadow. Exact 2008 35mm grain, mouths closed."),
    ("dk2_shot35_start.jpg", [stage("refs/yt/02_dark_knight_v2/frames/dk2_yt_0287.jpg"), deron_p, gigi_p],
     "Dark precinct corridor outside frosted glass interrogation door: place Deron in woven bamboo conical hat and red silk dragon robe gripping the jammed steel doorknob alongside Gigi in dark trench coat & red glasses. Exact night fluorescent corridor lighting, 35mm grain, mouths closed."),
    ("dk2_shot36_start.jpg", [stage("refs/yt/02_dark_knight_v2/frames/dk2_yt_0291.jpg"), hooman_p],
     "Coatless Act 3 Joker (grey-lavender hex shirt, green vest) slumped against white painted brick wall looking up. " + HOOMAN_LIKENESS),
    ("dk2_shot36_end.jpg", [stage("refs/yt/02_dark_knight_v2/frames/dk2_yt_0292.jpg"), hooman_p],
     "Same white brick wall shot with coatless Joker tilting chin slightly higher upward. " + HOOMAN_LIKENESS),
    ("dk2_shot37_start.jpg", [stage("refs/yt/02_dark_knight_v2/frames/dk2_yt_0298.jpg"), damon_p],
     "Low up-angle medium shot of Damon-Batman towering over floor in black cape & armor against cinderblocks. " + DAMON_LIKENESS),
    ("dk2_shot37_end.jpg", [stage("refs/yt/02_dark_knight_v2/frames/dk2_yt_0306.jpg"), damon_p],
     "Downward-glaring Damon-Batman leaning closer into frame over floor. " + DAMON_LIKENESS),
    ("dk2_shot38_start.jpg", [stage("refs/yt/02_dark_knight_v2/frames/dk2_yt_0317.jpg"), hooman_p],
     "Bright floor corner past dark Batsuit glove/forearm on left onto coatless Hooman-Joker slumped grinning against white brick. " + HOOMAN_LIKENESS),
    ("dk2_shot38_end.jpg", [stage("refs/yt/02_dark_knight_v2/frames/dk2_yt_0322.jpg"), hooman_p],
     "Same bright floor corner leaning back against brick past dark gloved hand on left. " + HOOMAN_LIKENESS),
    ("dk2_shot39_start.jpg", [stage("refs/yt/02_dark_knight_v2/frames/dk2_yt_0319.jpg"), damon_p],
     "Tight furious close-up of Damon-Batman glaring downward before storming out. " + DAMON_LIKENESS),
    ("dk2_shot40_start.jpg", [stage("refs/yt/02_dark_knight_v2/frames/dk2_yt_0330.jpg"), hooman_p],
     "Low up-angle tight OTS past dark receding Batman shoulder on left onto coatless Hooman-Joker smiling softly up. " + HOOMAN_LIKENESS),
    ("dk2_shot40_end.jpg", [stage("refs/yt/02_dark_knight_v2/frames/dk2_yt_0343.jpg"), hooman_p],
     "Closing low up-angle OTS past Batman silhouette left onto Hooman-Joker gazing up in triumph. " + HOOMAN_LIKENESS),
]

jobs = [{"out_name": out_n, "images": ims, "prompt": pr, "seed": 6100 + i} for i, (out_n, ims, pr) in enumerate(specs)]
json.dump(jobs, open(f"{WORK}/qwen_jobs.json", "w"), indent=2)

tar_path = f"{BASE}/dk2_qwen_bundle.tar.gz"
with tarfile.open(tar_path, "w:gz") as tf:
    tf.add(f"{WORK}/qwen_jobs.json", arcname="qwen_jobs.json")
    for fn in os.listdir(IN_DIR):
        tf.add(f"{IN_DIR}/{fn}", arcname=f"in/{fn}")

print(f"PACKED {len(jobs)} Qwen jobs -> {tar_path} ({os.path.getsize(tar_path)/1024/1024:.1f} MB)")
