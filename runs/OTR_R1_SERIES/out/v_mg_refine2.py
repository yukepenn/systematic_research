"""V3 MASTER-GAP HUNTER — stage 3: per-day Jan detail + finer search with the
Jan per-day table feasibility (nosol <= base=2, cents >= 5) as an added hard
constraint next to the 42/42 HARD labels.  Writes v_mg_refine2.json.
"""
import json
import os
import sys
from collections import defaultdict
from itertools import combinations

import numpy as np

OUT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, OUT)
# reuse everything from v_mg_refine by exec'ing its top half is messy; import as module
import importlib.util

spec = importlib.util.spec_from_file_location("vmg", os.path.join(OUT, "v_mg_refine.py"))
# executing v_mg_refine runs its full grid again (slow-ish but fine, ~1 min) — instead
# copy the needed pieces here by importing its functions after a guarded exec is not
# available; simplest robust path: re-exec its source up to the sanity block.
src = open(os.path.join(OUT, "v_mg_refine.py")).read()
cut = src.index("# ---------------------------------------------------------------- sanity")
ns = {"__name__": "vmg_core", "__file__": os.path.join(OUT, "v_mg_refine.py")}
exec(compile(src[:cut], "v_mg_refine_core", "exec"), ns)

replay = ns["replay"]
label_check = ns["label_check"]
agg = ns["agg"]
score = ns["score"]
LATE = ns["LATE"]
TGT = ns["TGT"]

BASE = {"X": 1600.0, "K": 3, "C": 1000.0}


def jan_detail(trades):
    by = defaultdict(list)
    for t in trades:
        if t["exit_day"] in TGT:
            by[t["exit_day"]].append(t)
    rows = []
    total_rm = cents = nosol = 0
    for day in sorted(TGT):
        nW, gW, nL, gL, LW, LL = TGT[day]
        ours = by.get(day, [])
        n_t = nW + nL
        k = len(ours) - n_t
        best = None
        if 0 <= k <= 7:
            for rem in combinations(range(len(ours)), k):
                keep = [t for jj, t in enumerate(ours) if jj not in rem]
                p = [t["pnl"] for t in keep]
                w = [x for x in p if x > 0]
                l = [x for x in p if x <= 0]
                if len(w) != nW or len(l) != nL:
                    continue
                if abs(max(w) - LW) > 75 or abs(min(l) - LL) > 75:
                    continue
                err = abs(sum(w) - gW) + abs(sum(l) - gL) + abs(max(w) - LW) + abs(min(l) - LL)
                if best is None or err < best[0]:
                    best = (err, rem)
        if best is None:
            nosol += 1
            rows.append(f"{day[-5:]}:n{len(ours)}/{n_t} NOSOL")
        else:
            total_rm += len(best[1])
            if best[0] < 0.02:
                cents += 1
            rows.append(f"{day[-5:]}:n{len(ours)}/{n_t} rm{len(best[1])} ${best[0]:.0f}")
    return total_rm, cents, nosol, " ".join(rows)


def run_cfg(extra, verbose=True):
    cfg = dict(BASE)
    cfg.update(extra)
    okN, bad = label_check(cfg)
    tk, _ = replay(LATE, cfg)
    a = agg(tk)
    rm, cents, nosol, detail = jan_detail(tk)
    if verbose:
        print(f"--- {extra} hard={okN}/42 score={score(a):.4f}")
        print(f"    n={a['n']} L{a['L']}/S{a['S']} net={a['net']} wr={a['wr']} pf={a['pf']} "
              f"dd={a['dd']} hold={a['hold']} ({a['holdL']}/{a['holdS']}) "
              f"lnet={a['lnet']} snet={a['snet']}")
        print(f"    jan rm={rm} cents={cents} nosol={nosol} | {detail}")
        if bad:
            print(f"    HARD FAILS: {bad[:6]}")
    return {"cfg": extra, "hard": okN, "agg": a, "score": round(score(a), 4),
            "jan": {"rm": rm, "cents": cents, "nosol": nosol, "detail": detail}}


print("=== per-day Jan detail: base and stage-2 leaders ===")
r_base = run_cfg({})
for extra in ({"X2": 2500.0}, {"X2": 2000.0}, {"lossN": 11}, {"cd": 15}, {"capM": 20},
              {"capM": 18}, {"X2": 2500.0, "cd": 15, "capM": 20},
              {"X2": 2500.0, "lossN": 11, "cd": 15}):
    run_cfg(extra)

print("\n=== stage 3: constrained search (hard 42/42 AND nosol<=2 AND cents>=5) ===")
cands = []
# finer X2
for X2 in (2100, 2200, 2300, 2400, 2500, 2600, 2800, 3000, 3200):
    cands.append({"X2": float(X2)})
# X2 + cap
for X2 in (2400, 2500, 3000):
    for capM in (17, 18, 20, 22):
        cands.append({"X2": float(X2), "capM": capM})
# X2 + lossN
for X2 in (2400, 2500, 3000):
    for lossN in (11, 12, 14, 16):
        cands.append({"X2": float(X2), "lossN": lossN})
# X2 + cap + lossN
for X2 in (2500, 3000):
    for capM in (18, 20):
        for lossN in (12, 14, 16):
            cands.append({"X2": float(X2), "capM": capM, "lossN": lossN})
# X2 + cd small
for X2 in (2500, 3000):
    for cd in (3, 5, 8, 15):
        cands.append({"X2": float(X2), "cd": cd})
# X2 + cap + cd
for X2 in (2500, 3000):
    for capM in (18, 20):
        for cd in (3, 5, 8, 15):
            cands.append({"X2": float(X2), "capM": capM, "cd": cd})
# stopN with re-enable + X2
for stopN in (4, 5, 6):
    for stopR in (60, 120, 240):
        cands.append({"X2": 2500.0, "stopN": stopN, "stopR": stopR})
# XC variants on top of X2
for X in (1550.0, 1700.0, 1800.0, 1900.0):
    cands.append({"X": X, "X2": 2500.0})
for C in (300.2, 500.0, 700.0, 1328.5):
    cands.append({"C": C, "X2": 2500.0})

results = []
for extra in cands:
    r = run_cfg(extra, verbose=False)
    results.append(r)

ok = [r for r in results if r["hard"] == 42 and r["jan"]["nosol"] <= 2 and r["jan"]["cents"] >= 5]
ok.sort(key=lambda r: r["score"])
print(f"{len(ok)}/{len(results)} pass constraints; top 15:")
for r in ok[:15]:
    a = r["agg"]
    print(f"score={r['score']:.4f} {str(r['cfg']):45} n={a['n']} net={a['net']:9.0f} "
          f"wr={a['wr']} pf={a['pf']} dd={a['dd']:.0f} hold={a['holdL']}/{a['holdS']} "
          f"jan rm={r['jan']['rm']} ns={r['jan']['nosol']}")

# also show best few that fail only the nosol constraint, for the report
loose = [r for r in results if r["hard"] == 42 and r not in ok]
loose.sort(key=lambda r: r["score"])
print("\nbest label-42/42 but Jan-degrading (for reference):")
for r in loose[:8]:
    a = r["agg"]
    print(f"score={r['score']:.4f} {str(r['cfg']):45} n={a['n']} net={a['net']:9.0f} "
          f"jan rm={r['jan']['rm']} cents={r['jan']['cents']} ns={r['jan']['nosol']}")

with open(os.path.join(OUT, "v_mg_refine2.json"), "w") as f:
    json.dump({"base": r_base, "constrained_top": ok[:25], "loose_top": loose[:15]},
              f, indent=1, default=str)
print("[v_mg_refine2] done", flush=True)
