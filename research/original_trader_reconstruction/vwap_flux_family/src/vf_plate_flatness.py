"""Vendor-plate lifecycle test WITH a rasterised synthetic control.

The discriminator: a SEGMENT/BLOCK VWAP is frozen once its window closes, so the rail it
defines is exactly horizontal until the population rotates. An ACTIVE anchored VWAP keeps
accumulating, so its rail keeps moving.

Naive pixel flatness is confounded by quantisation: at ~4.9 px/pt a rail sloping 0.1 pt/bar
already repeats its y on half of all columns. So the vendor plate is compared against OUR
OWN anchor and block rails RASTERISED AT THE SAME SCALE, which makes quantisation act
identically on all three. The statistic is only meaningful as a three-way comparison.

Free, in-repo, vendor-side. Nothing is fitted.
"""
import os
import sys

import numpy as np
import pandas as pd
from PIL import Image

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vf_core import vf_levels  # noqa: E402


def rail_masks(a):
    r = a[:, :, 0].astype(int); g = a[:, :, 1].astype(int); b = a[:, :, 2].astype(int)
    cyan = ((np.minimum(g, b) - r) > 45) & (np.abs(g - b) < 40) & (np.maximum(g, b) > 100)
    mag = ((np.minimum(r, b) - g) > 40) & (np.abs(r - b) < 30) & (np.maximum(r, b) > 100)
    return cyan, mag


def hrun_stats(mask, x0, x1, y0, y1):
    """Distribution of maximal horizontal run lengths in a rail mask.

    A frozen rail paints a long horizontal run at one y. A sloping rail cannot.
    """
    sub = mask[y0:y1, x0:x1]
    runs = []
    for row in sub:
        idx = np.flatnonzero(row)
        if not len(idx):
            continue
        cur = 1
        for k in range(1, len(idx)):
            if idx[k] == idx[k - 1] + 1:
                cur += 1
            else:
                runs.append(cur); cur = 1
        runs.append(cur)
    runs = np.array(runs) if runs else np.array([0])
    return dict(n_runs=len(runs), median=float(np.median(runs)),
                p90=float(np.percentile(runs, 90)), p99=float(np.percentile(runs, 99)),
                max=int(runs.max()),
                frac_ge_15=float((runs >= 15).mean()),
                frac_ge_30=float((runs >= 30).mean()))


def rasterize(vals, px_per_pt, px_per_bar, height=560):
    """Draw a price series into a boolean raster at the plate's scale."""
    v = np.asarray(vals, float)
    ok = np.isfinite(v)
    if ok.sum() < 10:
        return None
    v = v[ok]
    W = int(len(v) * px_per_bar)
    img = np.zeros((height, W), bool)
    ref = np.nanmedian(v)
    xs = (np.arange(len(v)) * px_per_bar).astype(int)
    ys = (height / 2 - (v - ref) * px_per_pt).astype(int)
    for k in range(len(v) - 1):
        x0, x1 = xs[k], max(xs[k + 1], xs[k] + 1)
        y0, y1 = ys[k], ys[k + 1]
        for x in range(x0, min(x1, W)):
            f = (x - x0) / max(x1 - x0, 1)
            y = int(round(y0 + f * (y1 - y0)))
            for dy in (-1, 0, 1):                    # NT8 draws ~3px-wide lines
                if 0 <= y + dy < height:
                    img[y + dy, x] = True
        # vertical connector, as any line renderer would draw
        lo, hi = sorted((y0, y1))
        for y in range(max(lo, 0), min(hi + 1, height)):
            if 0 <= xs[k] < W:
                img[y, xs[k]] = True
    return img


def main():
    SP = (r"C:\Users\YUKEZH~1\AppData\Local\Temp\claude"
          r"\D--OneDrive---Washington-University-in-St--Louis-TradingResearch-systematic-research"
          r"\707cc7ae-84f9-46b7-afb5-a583c39f5b2d\scratchpad\vfimg")
    PX_PER_PT = 4.86
    # p3 spans ~15:20..20:35 of 1-minute bars across ~1165 px of plot width
    PX_PER_BAR = 1165.0 / 300.0

    print("=== VENDOR PLATE (p3, NQ MAR26, 1 Minute) ===")
    a = np.asarray(Image.open(os.path.join(SP, "p03_0_1219x657.png")).convert("RGB"))
    cy, mg = rail_masks(a)
    for nm, m in (("cyan", cy), ("magenta", mg)):
        s = hrun_stats(m, 10, 1175, 45, 605)
        print(f"  {nm:<8} runs={s['n_runs']:<6} median={s['median']:.0f} "
              f"p90={s['p90']:.0f} p99={s['p99']:.0f} max={s['max']:<5} "
              f"frac>=15px={s['frac_ge_15']:.4f}  frac>=30px={s['frac_ge_30']:.4f}")

    print("\n=== SYNTHETIC CONTROLS (our vf_core, same rasterisation scale) ===")
    df = pd.read_parquet(os.path.join(ROOT, "research", "scalping_lab", "substrate",
                                      "minute", "NQ", "nq1m_2005_202605.parquet"))
    df["time"] = pd.to_datetime(df["time"])
    seg = df[(df["time"] >= "2026-01-26 09:00") &
             (df["time"] <= "2026-01-26 15:00")].reset_index(drop=True)
    t = seg["time"].values.astype("datetime64[s]")
    c = seg["close"].values
    v = seg["volume"].values.astype(float)
    print(f"  control bars: {len(seg)}  {seg['time'].iloc[0]} .. {seg['time'].iloc[-1]}")
    for lc in ("anchor", "block"):
        lv = vf_levels(t, c, v, 60, 5, lifecycle=lc, formula="percentile_linear")
        for k, nm in ((4, "MAX rail"), (0, "MIN rail")):
            img = rasterize(lv[:, k], PX_PER_PT, PX_PER_BAR)
            if img is None:
                continue
            s = hrun_stats(img, 0, img.shape[1], 0, img.shape[0])
            print(f"  {lc:<7} {nm:<9} runs={s['n_runs']:<6} median={s['median']:.0f} "
                  f"p90={s['p90']:.0f} p99={s['p99']:.0f} max={s['max']:<5} "
                  f"frac>=15px={s['frac_ge_15']:.4f}  frac>=30px={s['frac_ge_30']:.4f}")

    print("\nREADING: 'frac>=15px' is the share of horizontal runs at least 15 px long.")
    print("A frozen (block) rail should show a MUCH larger share than an active one;")
    print("the vendor plate sits with whichever control it resembles.")


if __name__ == "__main__":
    main()
