"""Pixel extraction of VWAP Flux rail geometry from the vendor's OWN manual charts.

Directive v4.0 sections 21/34. The VF architecture re-audit named these plates as a FREE,
in-repo, never-exploited vendor-side surface: they are the vendor's own rendered output,
the closest thing to vendor ground truth obtainable without a licence.

The question the geometry can answer:

  Q-LIFECYCLE  Between rail rotations, are the outer rails FLAT?
               A SEGMENT/BLOCK VWAP is frozen once its window closes, so the rail it
               defines is EXACTLY horizontal until the population rotates.
               An ACTIVE anchored VWAP keeps accumulating, so its rail keeps moving.

Method notes (why this is not naive colour matching):
  * the plates contain other cyan/magenta furniture -- an S/R rectangle set, VF arrows, a
    blue marketing banner, pink horizontal S/R lines. Colour thresholds alone pick all of
    it up, which produced a first pass with 216 spurious "jumps" at 0.3-minute spacing.
  * the rails are alpha-blended over a #222222 background, so their RGB is muted
    (~(148,94,146) magenta, ~(45,128,155) cyan) rather than vivid.
  * so: classify by HUE RATIO (cyan needs G~=B >> R, magenta needs R~=B >> G, which
    excludes the blue banner and the pink S/R lines), then TRACK the line column by column
    choosing the candidate nearest the previous y. A tracked line cannot teleport onto
    unrelated furniture.
"""
import os
import sys

import numpy as np
from PIL import Image


def masks(a):
    r = a[:, :, 0].astype(int); g = a[:, :, 1].astype(int); b = a[:, :, 2].astype(int)
    cyanness = np.minimum(g, b) - r
    magness = np.minimum(r, b) - g
    cyan = (cyanness > 45) & (np.abs(g - b) < 40) & (np.maximum(g, b) > 100)
    mag = (magness > 40) & (np.abs(r - b) < 30) & (np.maximum(r, b) > 100)
    return cyan, mag


def track(mask, x0, x1, y0, y1, seed_x=None, max_step=14):
    """Follow one line left-to-right, choosing the nearest candidate each column."""
    W = x1 - x0
    y = np.full(W, np.nan)
    cols = []
    for x in range(x0, x1):
        ys = np.flatnonzero(mask[y0:y1, x]) + y0
        cols.append(ys)
    # seed at the column with a single tight cluster
    start = None
    for i, ys in enumerate(cols):
        if len(ys) and (ys.max() - ys.min()) < 8:
            start = i; break
    if start is None:
        return y
    y[start] = float(ys_mean(cols[start]))
    for i in range(start + 1, W):
        y[i] = pick(cols[i], y[i - 1], max_step)
    for i in range(start - 1, -1, -1):
        y[i] = pick(cols[i], y[i + 1], max_step)
    return y


def ys_mean(ys):
    """Mean of the tightest contiguous cluster."""
    if not len(ys):
        return np.nan
    groups, cur = [], [ys[0]]
    for v in ys[1:]:
        if v - cur[-1] <= 3:
            cur.append(v)
        else:
            groups.append(cur); cur = [v]
    groups.append(cur)
    g = max(groups, key=len)
    return float(np.mean(g))


def pick(ys, prev, max_step):
    if not len(ys) or not np.isfinite(prev):
        return prev
    groups, cur = [], [ys[0]]
    for v in ys[1:]:
        if v - cur[-1] <= 3:
            cur.append(v)
        else:
            groups.append(cur); cur = [v]
    groups.append(cur)
    cands = [float(np.mean(g)) for g in groups]
    best = min(cands, key=lambda c: abs(c - prev))
    return best if abs(best - prev) <= max_step else prev


def analyse(y, px_per_pt, min_jump_pt, label, bars_per_px):
    y = np.asarray(y, float)
    ok = np.isfinite(y)
    if ok.sum() < 100:
        print(f"  {label}: insufficient coverage ({ok.sum()} cols)")
        return
    y = np.interp(np.arange(len(y)), np.flatnonzero(ok), y[ok])
    p = -y / px_per_pt                      # px -> points, y grows downward
    d = np.diff(p)
    thr = min_jump_pt
    ji = np.flatnonzero(np.abs(d) > thr)
    print(f"  {label}: {ok.sum()} usable cols, {len(ji)} jumps > {thr} pt")
    if len(ji):
        print(f"     jump sizes: median {np.median(np.abs(d[ji])):.2f} pt, "
              f"max {np.max(np.abs(d[ji])):.2f} pt")
        gaps = np.diff(ji) * bars_per_px
        if len(gaps):
            print(f"     spacing between jumps (bars): median {np.median(gaps):.0f}, "
                  f"values {np.round(gaps).astype(int).tolist()[:16]}")
    bounds = [0] + [int(i) + 1 for i in ji] + [len(p)]
    runs = []
    for a, b in zip(bounds[:-1], bounds[1:]):
        seg = p[a:b]
        if len(seg) >= 15:
            runs.append((len(seg), float(seg.max() - seg.min()),
                         float(np.mean(np.abs(np.diff(seg))))))
    if not runs:
        print("     no runs >=15 columns between jumps")
        return
    pk = np.array([r[1] for r in runs])
    sl = np.array([r[2] for r in runs])
    flat = int((pk < 0.30).sum())
    print(f"     {len(runs)} runs >=15 cols between jumps:")
    print(f"       peak-to-peak: median {np.median(pk):.2f} pt   min {pk.min():.2f}   max {pk.max():.2f}")
    print(f"       mean |step| : median {np.median(sl):.3f} pt/col")
    print(f"       runs FLAT within 0.30 pt: {flat}/{len(runs)}")
    verdict = ("SEGMENT/BLOCK (frozen between rotations)" if flat > 0.6 * len(runs)
               else "ACTIVE (rails keep moving between rotations)")
    print(f"       => supports {verdict}")


def main():
    SP = (r"C:\Users\YUKEZH~1\AppData\Local\Temp\claude"
          r"\D--OneDrive---Washington-University-in-St--Louis-TradingResearch-systematic-research"
          r"\707cc7ae-84f9-46b7-afb5-a583c39f5b2d\scratchpad\vfimg")
    PLATES = [
        ("p03_0_1219x657.png", "NQ MAR26, 1 Minute", (10, 1175, 45, 605), 4.86, 1 / 3.55),
        ("p02_0_1220x653.png", "NQ MAR26, 100 Tick", (10, 1175, 45, 605), 4.86, 1 / 3.55),
        ("p04_0_1222x654.png", "plate p4", (10, 1175, 45, 605), 4.86, 1 / 3.55),
        ("p07_0_1220x656.png", "plate p7", (10, 1175, 45, 605), 4.86, 1 / 3.55),
    ]
    for fn, label, (x0, x1, y0, y1), ppp, bpp in PLATES:
        path = os.path.join(SP, fn)
        if not os.path.exists(path):
            continue
        a = np.asarray(Image.open(path).convert("RGB"))
        cy, mg = masks(a)
        print(f"\n=== {label}  ({fn}) ===")
        print(f"    cyan pixels {int(cy[y0:y1, x0:x1].sum()):,}   "
              f"magenta pixels {int(mg[y0:y1, x0:x1].sum()):,}")
        analyse(track(cy, x0, x1, y0, y1), ppp, 1.5, "cyan  ", bpp)
        analyse(track(mg, x0, x1, y0, y1), ppp, 1.5, "magenta", bpp)


if __name__ == "__main__":
    main()
