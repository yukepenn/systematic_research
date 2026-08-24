"""R1.2 diagnostic: per-day (Jan-2023) counts/nets vs OTRIMG-0003 Daily Analysis targets.

Selection space per spec: window grid x entry_types x reverse. exit_touch variants are
DIAGNOSTIC-class (not selectable without spec amendment).
"""
import json
import os
import sys
from collections import defaultdict

import numpy as np

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from otr_engine import load_ledger, run_wrapper, WrapperPolicy  # noqa: E402

OUT = os.path.join(ROOT, "runs", "OTR_R1_SERIES", "out")
bars = load_ledger(os.path.join(ROOT, "research", "03_reverse_engineering", "ledgers", "t2_canonical_1m.csv"))

# targets: exit-day -> (trades, net) at $4.18/RT
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


def eval_policy(name, pol):
    r = run_wrapper(bars, pol)
    per = defaultdict(list)
    for t in r["trades"]:
        d = str(t["exit_time"])[:10]
        if d in TGT:
            per[d].append(t["pnl"])
    rows = []
    l1 = 0
    for d in sorted(TGT):
        n_t, net_t = TGT[d]
        p = per.get(d, [])
        n_s, net_s = len(p), round(float(np.sum(p)), 2) if p else 0.0
        l1 += abs(n_s - n_t)
        rows.append((d, n_s, n_t, net_s, net_t,
                     round(max(p), 2) if p else None, round(min(p), 2) if p else None,
                     TGT_LGL[d][0], TGT_LGL[d][1]))
    total_fp = r["fingerprint"]
    return {"name": name, "count_L1": l1, "days": rows,
            "master_trades": total_fp["trades"], "master_net": total_fp["net"],
            "master_hold": total_fp["avg_hold_min"]}


POLS = [
    ("P0_CAND1", WrapperPolicy(comm_side=2.09, entry_types=(1, 3), reverse_on_flip=True,
                               entry_time_mask=wm(240, 960), flat_time_mask=lambda m: ~wm(240, 960)(m))),
    ("P1_CAND1_strictcross[DIAG]", WrapperPolicy(comm_side=2.09, entry_types=(1, 3), reverse_on_flip=True,
                               exit_touch=False,
                               entry_time_mask=wm(240, 960), flat_time_mask=lambda m: ~wm(240, 960)(m))),
    ("P2_T1only_rev_win", WrapperPolicy(comm_side=2.09, entry_types=(1,), reverse_on_flip=True,
                               entry_time_mask=wm(240, 960), flat_time_mask=lambda m: ~wm(240, 960)(m))),
    ("P3_T13_norev_win", WrapperPolicy(comm_side=2.09, entry_types=(1, 3), reverse_on_flip=False,
                               entry_time_mask=wm(240, 960), flat_time_mask=lambda m: ~wm(240, 960)(m))),
    ("P4_win0600_1600", WrapperPolicy(comm_side=2.09, entry_types=(1, 3), reverse_on_flip=True,
                               entry_time_mask=wm(360, 960), flat_time_mask=lambda m: ~wm(360, 960)(m))),
    ("P5_win0930_1600", WrapperPolicy(comm_side=2.09, entry_types=(1, 3), reverse_on_flip=True,
                               entry_time_mask=wm(570, 960), flat_time_mask=lambda m: ~wm(570, 960)(m))),
    ("P6_nowin_T13_rev", WrapperPolicy(comm_side=2.09, entry_types=(1, 3), reverse_on_flip=True)),
    ("P7_V0_T1_nowin", WrapperPolicy(comm_side=2.09)),
]

results = []
for name, pol in POLS:
    res = eval_policy(name, pol)
    results.append(res)
    print(f"{name}: L1={res['count_L1']} master n={res['master_trades']} net={res['master_net']} hold={res['master_hold']}", flush=True)
    for d, ns, nt, nets, nett, lw, ll, lwt, llt in res["days"]:
        print(f"   {d}: n {ns:3d}/{nt:3d}  net {nets:9.2f}/{nett:9.2f}  LW {lw}/{lwt}  LL {ll}/{llt}", flush=True)

with open(os.path.join(OUT, "r12b_perday.json"), "w") as f:
    json.dump(results, f, indent=1, default=str)
print("done", flush=True)
