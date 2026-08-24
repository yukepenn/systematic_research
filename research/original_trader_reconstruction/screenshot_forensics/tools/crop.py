"""Crop+upscale regions of original screenshots for deep-read QC. Originals untouched.

Usage: python crop.py <IMAGE_ID> <left> <top> <right> <bottom> [scale]
       python crop.py <IMAGE_ID> right   -> right 22% strip, x3
"""
import csv, sys
from pathlib import Path
from PIL import Image

SF = Path(__file__).resolve().parents[1]
SRC = SF.parent / "original_screenshot"

def path_for(iid):
    for r in csv.DictReader(open(SF / "IMAGE_MASTER.csv", encoding="utf-8")):
        if r["image_id"] == iid:
            return SRC / r["filename"]
    raise SystemExit(f"unknown id {iid}")

iid = sys.argv[1]
p = path_for(iid)
img = Image.open(p)
W, H = img.size
if sys.argv[2] == "right":
    box = (int(W * 0.78), 0, W, H); scale = 3
else:
    box = tuple(int(x) for x in sys.argv[2:6])
    scale = int(sys.argv[6]) if len(sys.argv) > 6 else 3
c = img.crop(box)
c = c.resize((c.width * scale, c.height * scale), Image.LANCZOS)
out = SF / "derived" / "crops" / f"{iid}_{box[0]}_{box[1]}_{box[2]}_{box[3]}_x{scale}.png"
out.parent.mkdir(parents=True, exist_ok=True)
c.save(out)
print(out)
