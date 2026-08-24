"""IMG-1 census: enumerate original_screenshot/, hash, dims, EXIF, dHash -> IMAGE_MASTER.csv.

Originals are READ-ONLY: this script only reads bytes; all outputs go to
screenshot_forensics/. IDs OTRIMG-0001.. assigned in filename sort order (stable).
"""
import csv, hashlib, os, sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]  # original_trader_reconstruction/
SRC = ROOT / "original_screenshot"
OUT = ROOT / "screenshot_forensics" / "IMAGE_MASTER.csv"

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def dhash(img, size=8):
    g = img.convert("L").resize((size + 1, size), Image.LANCZOS)
    px = list(g.getdata())
    bits = 0
    for r in range(size):
        for c in range(size):
            bits = (bits << 1) | (1 if px[r * (size + 1) + c] > px[r * (size + 1) + c + 1] else 0)
    return f"{bits:016x}"

def exif_dt(img):
    try:
        ex = img.getexif()
        if not ex:
            return ""
        # 36867 DateTimeOriginal lives in the Exif IFD (34665); 306 = DateTime
        try:
            ifd = ex.get_ifd(0x8769)
            v = ifd.get(36867) or ifd.get(36868)
        except Exception:
            v = None
        return str(v or ex.get(306) or "")
    except Exception:
        return ""

files = sorted(p for p in SRC.iterdir() if p.is_file())
rows = []
for i, p in enumerate(files, 1):
    st = p.stat()
    try:
        with Image.open(p) as img:
            w, h = img.size
            dh = dhash(img)
            dt = exif_dt(img)
    except Exception as e:
        w = h = 0; dh = ""; dt = f"ERROR:{e}"
    rows.append({
        "image_id": f"OTRIMG-{i:04d}",
        "original_relative_path": f"original_screenshot/{p.name}",
        "filename": p.name,
        "extension": p.suffix.lower().lstrip("."),
        "byte_size": st.st_size,
        "width": w, "height": h,
        "sha256": sha256(p),
        "perceptual_hash": dh,
        "exif_datetime_original": dt,
        "filesystem_mtime": __import__("datetime").datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds"),
        "image_type_initial": "", "duplicate_group": "", "near_duplicate_group": "",
        "reviewed": "NO", "forensic_status": "PENDING", "notes": "",
    })

# exact-duplicate groups by sha256
by_sha = {}
for r in rows:
    by_sha.setdefault(r["sha256"], []).append(r)
gid = 0
for sha, grp in by_sha.items():
    if len(grp) > 1:
        gid += 1
        for r in grp:
            r["duplicate_group"] = f"DUP-{gid:03d}"

# near-duplicate groups by dHash hamming distance <= 6 (union-find)
def ham(a, b):
    return bin(int(a, 16) ^ int(b, 16)).count("1")
parent = list(range(len(rows)))
def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]; x = parent[x]
    return x
for i in range(len(rows)):
    for j in range(i + 1, len(rows)):
        if rows[i]["perceptual_hash"] and rows[j]["perceptual_hash"] and ham(rows[i]["perceptual_hash"], rows[j]["perceptual_hash"]) <= 6:
            parent[find(i)] = find(j)
clusters = {}
for i in range(len(rows)):
    clusters.setdefault(find(i), []).append(i)
ngid = 0
for root, members in sorted(clusters.items()):
    if len(members) > 1:
        ngid += 1
        for m in members:
            rows[m]["near_duplicate_group"] = f"NEAR-{ngid:03d}"

OUT.parent.mkdir(exist_ok=True)
with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)

print(f"files={len(rows)} exact_dup_groups={gid} near_dup_groups={ngid}")
print("exif_present=", sum(1 for r in rows if r["exif_datetime_original"] and not r["exif_datetime_original"].startswith("ERROR")))
dims = {}
for r in rows:
    dims[(r["width"], r["height"])] = dims.get((r["width"], r["height"]), 0) + 1
for d, n in sorted(dims.items(), key=lambda kv: -kv[1])[:12]:
    print("dim", d, n)
