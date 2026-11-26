"""Pack all 42 Pulp Fiction v2 keyframes cleanly to exact 1920x832 Scope (stripping black letterbox bars & preserving headroom) and build 5 Continuity Grids."""
import os
import sys
import numpy as np
from PIL import Image, ImageDraw

BASE = "/Users/jack/.gemini/antigravity/scratch/nomad-cinema-parodies"
ART = "/Users/jack/.gemini/antigravity/brain/d62d3766-563e-480c-b794-3d9b49e38c01"
MASTERS_DIR = f"{BASE}/refs/05_pulp_fiction_v2/masters"
OUT_DIR = f"{BASE}/refs/05_pulp_fiction_v2"
GRIDS_DIR = f"{OUT_DIR}/grids"


def pack_scope(src_path: str, dst_path: str, top_bias: float = 0.5):
    im = Image.open(src_path).convert("RGB")
    arr = np.array(im)
    row_means = arr.mean(axis=(1, 2))
    active = np.where(row_means > 10.0)[0]
    if len(active) > int(im.height * 0.4):
        y0, y1 = int(active[0]), int(active[-1] + 1)
        im = im.crop((0, y0, im.width, y1))

    target_w, target_h = 1920, 832
    scale_w = target_w
    scale_h = int(round(im.height * (target_w / im.width)))
    if scale_h >= target_h:
        im = im.resize((scale_w, scale_h), Image.Resampling.LANCZOS)
        excess = scale_h - target_h
        top = int(round(excess * top_bias))
        im = im.crop((0, top, target_w, top + target_h))
    else:
        scale_h = target_h
        scale_w = int(round(im.width * (target_h / im.height)))
        im = im.resize((scale_w, scale_h), Image.Resampling.LANCZOS)
        left = (scale_w - target_w) // 2
        im = im.crop((left, 0, left + target_w, target_h))

    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    im.save(dst_path, quality=95)
    print(f"  PACKED {os.path.basename(src_path)} -> {os.path.relpath(dst_path, BASE)} ({im.size}, bias={top_bias})")


MASTER_MAP = {
    "master_A_car_wide.jpg": ("master_a_car_wide_1795704659830.jpg", 0.50),
    "master_B_car_damon.jpg": ("master_b_car_damon_1795704681189.jpg", 0.35),
    "master_C_car_hooman.jpg": ("master_c_car_hooman_1795704571981.jpg", 0.20),
    "master_D_hallway.jpg": ("master_d_hallway_1795704542285.jpg", 0.30),
    "master_E_apt_wide.jpg": ("master_e_apt_wide_final_1795704656779.jpg", 0.50),
    "master_F_hooman_blinds.jpg": ("master_f_hooman_blinds_1795704555756.jpg", 0.25),
    "master_G_damon_door.jpg": ("master_g_damon_door_1795704539827.jpg", 0.25),
    "master_H_deron_table.jpg": ("master_h_deron_table_1795704537653.jpg", 0.20),
    "master_I_zach_kitchen.jpg": ("master_i_zach_kitchen_1795704549691.jpg", 0.25),
    "master_J_ajay_sofa.jpg": ("master_j_ajay_sofa_1795704563353.jpg", 0.35),
    "master_K_gigi_door.jpg": ("master_k_gigi_door_v2_1795704610220.jpg", 0.25),
    "master_L_bathroom_fx.jpg": ("master_l_bathroom_fx_1795704550452.jpg", 0.45),
    "master_M_briefcase_gold.jpg": ("master_m_briefcase_gold_1795704582911.jpg", 0.12),
    "master_N_sheren_hallway.jpg": ("master_n_sheren_hallway_1795704547014.jpg", 0.20),
    "master_O_sheren_apartment.jpg": ("master_o_sheren_apartment_1795704560867.jpg", 0.25),
}

BESPOKE_SHOTS = {
    8:  ("pf2_08_damon_knob_1795704890231.jpg", 0.15),
    12: ("pf2_12_hooman_lean_1795705092641.jpg", 0.35),
    14: ("pf2_14_deron_pochai_1795705005405.jpg", 0.20),
    20: ("pf2_20_deron_sweat_1795705121471.jpg", 0.15),
    21: ("pf2_21_damon_charge_1795704947979.jpg", 0.45),
    23: ("pf2_23_zach_panic_1795704902021.jpg", 0.30),
    25: ("pf2_25_hooman_horror_1795705088064.jpg", 0.15),
    26: ("pf2_26_ajay_cramp_1795704933181.jpg", 0.40),
    27: ("pf2_27_damon_splattered_1795705105741.jpg", 0.40),
    28: ("pf2_28_zach_joggers_1795705120893.jpg", 0.12),
    29: ("pf2_29_hooman_puddle_wide_1795705517931.jpg", 0.50),
    30: ("pf2_30_bathroom_geyser2_1795705039874.jpg", 0.45),
    31: ("pf2_31_deron_chair_1795705073076.jpg", 0.30),
    32: ("pf2_32_ajay_keys_1795705088042.jpg", 0.35),
    34: ("pf2_34_hooman_gold_1795704912896.jpg", 0.08),
    35: ("pf2_35_gigi_steam_1795705099202.jpg", 0.30),
    36: ("pf2_36_damon_pills_1795705081300.jpg", 0.18),
    37: ("pf2_37_ajay_recovery_1795704944467.jpg", 0.40),
    41: ("pf2_41_hooman_climax_1795705033793.jpg", 0.35),
    42: ("pf2_42_exit_wide_1795705050616.jpg", 0.50),
}

SHOT_MASTER_MAP = {
    1: "master_A_car_wide.jpg",
    2: "master_B_car_damon.jpg",
    3: "master_C_car_hooman.jpg",
    4: "master_B_car_damon.jpg",
    5: "master_A_car_wide.jpg",
    6: "master_N_sheren_hallway.jpg",
    7: "master_D_hallway.jpg",
    9: "master_E_apt_wide.jpg",
    10: "master_F_hooman_blinds.jpg",
    11: "master_H_deron_table.jpg",
    13: "master_G_damon_door.jpg",
    15: "master_I_zach_kitchen.jpg",
    16: "master_F_hooman_blinds.jpg",
    17: "master_J_ajay_sofa.jpg",
    18: "master_G_damon_door.jpg",
    19: "master_F_hooman_blinds.jpg",
    22: "master_K_gigi_door.jpg",
    24: "master_L_bathroom_fx.jpg",
    33: "master_M_briefcase_gold.jpg",
    38: "master_O_sheren_apartment.jpg",
    39: "master_H_deron_table.jpg",
    40: "master_I_zach_kitchen.jpg",
}


def build_grid(shot_nums: list[int], out_name: str, title: str):
    cols = 3
    pw, ph = 640, 277
    rows = (len(shot_nums) + cols - 1) // cols
    canvas = Image.new("RGB", (cols * pw, rows * ph + 44), (16, 18, 24))
    draw = ImageDraw.Draw(canvas)
    draw.text((16, 12), title, fill=(245, 225, 130))
    for i, n in enumerate(shot_nums):
        p = f"{OUT_DIR}/pf2_shot{n:02d}_start.jpg"
        im = Image.open(p).resize((pw, ph), Image.Resampling.LANCZOS)
        x, y = (i % cols) * pw, 44 + (i // cols) * ph
        canvas.paste(im, (x, y))
        draw.rectangle([x + 8, y + 8, x + 120, y + 32], fill=(0, 0, 0))
        draw.text((x + 14, y + 12), f"PF2_{n:02d}", fill=(120, 240, 180))
    os.makedirs(GRIDS_DIR, exist_ok=True)
    out_p = f"{GRIDS_DIR}/{out_name}"
    canvas.save(out_p, quality=90)
    print(f"GRID -> {os.path.relpath(out_p, BASE)}")


def main():
    for out_name, (art_fn, bias) in MASTER_MAP.items():
        pack_scope(f"{ART}/{art_fn}", f"{MASTERS_DIR}/{out_name}", top_bias=bias)

    for n in range(1, 43):
        dst = f"{OUT_DIR}/pf2_shot{n:02d}_start.jpg"
        if n in BESPOKE_SHOTS:
            art_fn, bias = BESPOKE_SHOTS[n]
            pack_scope(f"{ART}/{art_fn}", dst, top_bias=bias)
        else:
            m_fn = SHOT_MASTER_MAP[n]
            Image.open(f"{MASTERS_DIR}/{m_fn}").save(dst, quality=95)
            print(f"  LINK {m_fn} -> refs/05_pulp_fiction_v2/pf2_shot{n:02d}_start.jpg")

    build_grid([1, 3, 5, 7, 10, 12, 16, 19, 25, 29, 34, 41], "grid_1_hooman.jpg", "GRID 1 — HOOMAN CONTINUITY (Car -> Hallway -> Blinds -> Briefcase)")
    build_grid([1, 2, 4, 7, 8, 13, 18, 21, 27, 36, 42], "grid_2_damon.jpg", "GRID 2 — DAMON CONTINUITY (Car -> Knob -> Door -> Bathroom -> Exit)")
    build_grid([11, 14, 20, 31, 39, 15, 23, 28, 33, 40], "grid_3_deron_zach.jpg", "GRID 3 — DERON & ZACH CONTINUITY (Table -> Kitchen -> Joggers -> Briefcase)")
    build_grid([17, 26, 32, 37, 22, 35, 6, 38], "grid_4_ajay_gigi_sheren.jpg", "GRID 4 — AJAY, GIGI & SHEREN CONTINUITY")
    build_grid([9, 24, 27, 28, 29, 30, 31, 32, 38, 42], "grid_5_wides_diarrhea_fx.jpg", "GRID 5 — WIDES & PRACTICAL-FX DIARRHEA SETUPS")
    print("ALL_42_PF2_KEYFRAMES_AND_5_GRIDS_READY")


if __name__ == "__main__":
    main()
