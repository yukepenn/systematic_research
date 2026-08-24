"""R1.2c grid: window x suppression axes on Jan-2023 slice; metric = cent-matches then L1.

Spec amendment 1 (2d2f528) committed before this readout.
"""
import json
import os
import sys
from collections import defaultdict
from itertools import product

import numpy as np

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from otr_engine import load_ledger, run_wrapper, WrapperPolicy  # noqa: E402

OUT = os.path.join(ROOT, "runs", "OTR_R1_SERIES", "out")
full = load_ledger(os.path.join(ROOT, "research", "03_reverse_engineering", "ledgers", "t2_canonical_1m.csv"))

# slice: bars through 2023-01-21 (master state is fresh at 1/1/2023)
cut = np.searchsorted(full["time"], np.datetime64("2023-01-21T00:00:00"))
bars = {k: (v[:cut] if isinstance(v, np.ndarray) else v) for k, v in full.items()}
bars["n"] = int(cut)
bars["last_bar"] = bars["last_bar"].copy()
bars["last_bar"][-1] = True

TGT = {"2023-01-03": (12, -300.16), "2023-01-04": (14, -1148.52), "2023-01-05": (6, -30.08),
       "2023-01-06": (10, 2993.20), "2023-01-09": (3, 5262.46), "2023-01-10": (9, 1192.38),
       "2023-01-11": (4, 1768.28), "2023-01-12": (16, -3321.88), "2023-01-13": (6, 1424.92),
       "2023-01-16": (3, 607.46), "2023-01-17": (6, -415.08)}
TGT_LGL = {"2023-01-03": (3050.82, -1179.18), "2023-01-04": (1865.82, -899.18),
           "2023-01-05": (2310.82, -889.18), "2023-01-06": (4210.82, -1384.18),
           "2023-01-09": (3170.82, -854.18), "2023-01-10": (1370.82, -1084.18),
           "2023-01-11": (2190.82, -749.18), "2023-01-12": (1535.82, -1204.18),
           "2023-01-13": (1885.82, -809.18), "2023-01-16": (555.82, -34.18),
           "2023-01-17": (590.82, -1089.18)}


def wm(a, b):
    return lambda m: (m >= a) & (m < b)


def score(pol):
    r = run_wrapper(bars, pol)
    per = defaultdict(list)
    for t in r["trades"]:
        d = str(t["exit_time"])[:10]
        if d in TGT:
            per[d].append(t["pnl"])
    l1 = 0
    cents = 0
    net_err = 0.0
    for d in sorted(TGT):
        p = per.get(d, [])
        l1 += abs(len(p) - TGT[d][0])
        net_err += abs((np.sum(p) if p else 0.0) - TGT[d][1])
        if p:
            if abs(max(p) - TGT_LGL[d][0]) < 0.005:
                cents += 1
            if abs(min(p) - TGT_LGL[d][1]) < 0.005:
                cents += 1
    return cents, l1, round(net_err, 2), len(r["trades"])


WINDOWS = [None, (0, 960), (120, 960), (240, 960), (0, 930), (0, 945), (None, 960), (None, 945), (None, 930)]
# (None, b) = entries unrestricted, force-flat [b, 1020)
rows = []
for win, mep, cd, t3rt, rce in product(
        WINDOWS, [None, 2, 3, 4], [0, 5, 10, 15, 30, 60], [False, True], [False, True]):
    kw = dict(entry_types=(1, 3), reverse_on_flip=True, comm_side=2.09,
              max_entries_per_trend=mep, reentry_cooldown_bars=cd,
              t3_requires_t2=t3rt, reverse_counts_entry=rce)
    if win is None:
        pass
    elif win[0] is None:
        kw["flat_time_mask"] = wm(win[1], 1020)
    else:
        kw["entry_time_mask"] = wm(*win)
        kw["flat_time_mask"] = lambda m, w=win: ~wm(*w)(m)
    cents, l1, nerr, ntot = score(WrapperPolicy(**kw))
    rows.append({"win": str(win), "max_epr": mep, "cooldown": cd, "t3_req_t2": t3rt,
                 "rev_counts": rce, "cents": cents, "L1": l1, "net_err": nerr, "n_slice": ntot})

rows.sort(key=lambda r: (-r["cents"], r["L1"], r["net_err"]))
with open(os.path.join(OUT, "r12c_grid.json"), "w") as f:
    json.dump(rows, f, indent=1)
print(f"grid cells: {len(rows)}")
for r in rows[:25]:
    print(r, flush=True)
