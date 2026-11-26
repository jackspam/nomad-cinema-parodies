"""Crop any 16:9 keyframe cleanly to 1920x832 Scope, save to refs/02_dark_knight_v2, and build side-by-side QA sheet."""
import os
import sys
from PIL import Image

BASE = "/Users/jack/.gemini/antigravity/scratch/nomad-cinema-parodies"
sys.path.insert(0, f"{BASE}/scripts")
from qa_keyframe_sheet import make_qa_sheet


def prep(src_path: str, yt_frame_name: str, out_rel: str, label: str = ""):
    dst = f"{BASE}/refs/02_dark_knight_v2/{out_rel}"
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    im = Image.open(src_path).convert("RGB")
    if im.size != (1920, 832):
        # Resize width to 1920 preserving aspect, then center-crop to 832 height
        new_h = int(round(1920 * im.height / im.width))
        if new_h >= 832:
            im = im.resize((1920, new_h), Image.Resampling.LANCZOS)
            top = (new_h - 832) // 2
            im = im.crop((0, top, 1920, top + 832))
        else:
            im = im.resize((1920, 832), Image.Resampling.LANCZOS)
    im.save(dst, quality=95)
    yt_path = f"{BASE}/refs/yt/02_dark_knight_v2/frames/{yt_frame_name}"
    qa_out = f"{BASE}/refs/02_dark_knight_v2/qa/{os.path.splitext(out_rel)[0]}_qa.png"
    make_qa_sheet(yt_path, dst, qa_out, label or out_rel)


if __name__ == "__main__":
    prep(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "")
