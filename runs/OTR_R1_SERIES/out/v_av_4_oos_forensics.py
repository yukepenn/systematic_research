"""TASK V1 part 3b — forensics on the Feb OOS subsets: uniqueness of the cent-exact
W0204 subset, hold-time implications, which gate sub-rule fired, session equity paths."""
import os
import sys
from itertools import combinations

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = os.path.join(ROOT, "runs", "OTR_R1_SERIES", "out")
sys.path.insert(0, OUT)
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
from v_av_1_reimpl import sim  # noqa: E402
from v_av_3_oos import make_bars, WINDOWS  # noqa: E402


def exact_subsets(trades, tgt, tol=0.005):
    n_t = tgt["n"]
    k = len(trades) - n_t
    sols = []
    for rem in combinations(range(len(trades)), k):
        keep = [t for j, t in enumerate(trades) if j not in rem]
        d = np.array([t["dir"] for t in keep])
        if int((d > 0).sum()) != tgt["L"] or int((d < 0).sum()) != tgt["S"]:
            continue
        p = np.array([t["pnl"] for t in keep])
        err = abs(p.sum() - tgt["net"])
        if "lw" in tgt and (abs(p.max() - tgt["lw"]) > 0.005 or abs(p.min() - tgt["ll"]) > 0.005):
            continue
        if err <= tol:
            h = np.mean([t["hold_min"] for t in keep])
            sols.append((err, rem, [f"{trades[j]['entry_time'][5:16]}{'L' if trades[j]['dir']>0 else 'S'}({trades[j]['pnl']:.0f})" for j in rem], round(float(h), 2)))
    return sols


for wname in ("W0204", "W0209"):
    lo, hi, tgt = WINDOWS[wname]
    bars, sig, ts = make_bars(lo, hi)
    tk, bk = sim(bars, sig, ts, use_b1=True, guard=0, use_gate=False)
    print("=" * 70)
    print(wname, "target:", tgt)
    tol = 0.005 if wname == "W0204" else 25.0
    sols = exact_subsets(tk, tgt, tol=tol)
    for err, rem, names, hold in sols:
        print(f"  err=${err:.2f} rm={names} kept_hold={hold} (tgt {tgt['hold']})")
    # session equity paths (no-gate)
    sid = np.cumsum(bars["first_bar"]) - 1
    t = bars["time"]
    for s in range(int(bars["first_bar"].sum())):
        st_trades = [x for x in tk if sid[x["entry_i"]] == s]
        cum = 0.0
        hi_run = 0.0
        path = []
        for x in st_trades:
            cum += x["pnl"]
            hi_run = max(hi_run, cum)
        print(f"  session {s}: n={len(st_trades)} net={cum:.2f} high_watermark={hi_run:.2f}"
              f"  (armed rule X=1600 {'COULD arm' if hi_run>=1600 else 'never arms'})")
print("done")
