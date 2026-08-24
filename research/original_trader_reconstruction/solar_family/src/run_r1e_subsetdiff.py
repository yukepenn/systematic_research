"""R1.2e: per-day subset-diff — which of our P6 trades must be REMOVED to match the
target day structure (nW, grossW, nL, grossL, LW, LL) exactly. Session-based grouping.
"""
import os
import sys
from itertools import combinations

import numpy as np

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from otr_engine import load_ledger, run_wrapper, WrapperPolicy  # noqa: E402

full = load_ledger(os.path.join(ROOT, "research", "03_reverse_engineering", "ledgers", "t2_canonical_1m.csv"))
cut = np.searchsorted(full["time"], np.datetime64("2023-01-21T00:00:00"))
bars = {k: (v[:cut] if isinstance(v, np.ndarray) else v) for k, v in full.items()}
bars["n"] = int(cut)
bars["last_bar"] = bars["last_bar"].copy()
bars["last_bar"][-1] = True

# session end date for each bar index: date of the session's LAST bar
sess_id = bars["session_id"]
last_idx = {}
for i in range(bars["n"]):
    last_idx[sess_id[i]] = i
sess_end_date = {sid: str(bars["time"][i])[:10] for sid, i in last_idx.items()}

# target day structures: (nW, grossW, nL, grossL, LW, LL)  [$4.18/RT net basis]
TGT = {
 "2023-01-03": (4, 5863.28, 8, -6163.44, 3050.82, -1179.18),
 "2023-01-04": (5, 3859.10, 9, -5007.60, 1865.82, -899.18),
 "2023-01-05": (2, 2611.64, 4, -2641.72, 2310.82, -889.18),
 "2023-01-06": (5, 6314.10, 5, -3320.90, 4210.82, -1384.18),
 "2023-01-09": (2, 6116.64, 1, -854.18, 3170.82, -854.18),
 "2023-01-10": (5, 3744.10, 4, -2551.72, 1370.82, -1084.18),
 "2023-01-11": (2, 3106.64, 2, -1338.36, 2190.82, -749.18),
 "2023-01-12": (5, 4704.10, 11, -8025.98, 1535.82, -1204.18),
 "2023-01-13": (3, 3337.46, 3, -1912.54, 1885.82, -809.18),
 "2023-01-16": (2, 641.64, 1, -34.18, 555.82, -34.18),
 "2023-01-17": (3, 1322.46, 3, -1737.54, 590.82, -1089.18),
}

pol = WrapperPolicy(comm_side=2.09, entry_types=(1, 3), reverse_on_flip=True)
r = run_wrapper(bars, pol)
st = bars["signal_trade"]

by_day = {}
for t in r["trades"]:
    d = sess_end_date[sess_id[t["exit_i"]]]
    by_day.setdefault(d, []).append(t)


def match_day(day, trades, tgt):
    nW, gW, nL, gL, LW, LL = tgt
    n_tgt = nW + nL
    sols = []
    for k in range(0, min(8, len(trades) - n_tgt + 1) + 1):
        if len(trades) - k != n_tgt:
            continue
        for rem in combinations(range(len(trades)), k):
            keep = [t for j, t in enumerate(trades) if j not in rem]
            p = [t["pnl"] for t in keep]
            w = [x for x in p if x > 0]
            l = [x for x in p if x <= 0]
            if len(w) != nW or len(l) != nL:
                continue
            if abs(sum(w) - gW) > 0.011 or abs(sum(l) - gL) > 0.011:
                continue
            if w and abs(max(w) - LW) > 0.005:
                continue
            if l and abs(min(l) - LL) > 0.005:
                continue
            sols.append(rem)
    return sols


print("day | ours n | tgt n | exact-removal solutions")
for day in sorted(TGT):
    ours = by_day.get(day, [])
    sols = match_day(day, ours, TGT[day])
    print(f"=== {day}: ours={len(ours)} tgt={TGT[day][0]+TGT[day][2]} sols={len(sols)}")
    for s in sols[:3]:
        for j in s:
            t = ours[j]
            ei = t["entry_i"]
            print(f"    REMOVE {'L' if t['dir']>0 else 'S'} entry {str(t['entry_time'])[11:16]} "
                  f"sig={st[ei-1]:+d} exit {str(t['exit_time'])[5:16]} kind={t['exit_kind'][:8]} "
                  f"pnl {t['pnl']:9.2f} hold {t['hold_min']:5.0f}")
        if len(sols) > 1:
            print("    ---")
