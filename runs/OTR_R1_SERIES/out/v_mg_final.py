"""V3 MASTER-GAP HUNTER — micro-refinement around {X2,capM,cd} winner + full
fingerprint (monthly table, direction split, exit kinds, per-session dist).
Writes v_mg_final.json.
"""
import json
import os
import sys
from collections import defaultdict
from itertools import combinations

import numpy as np

OUT = os.path.dirname(os.path.abspath(__file__))
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
sess_end_day = ns["sess_end_day"]
sess_id = ns["sess_id"]
first_bar = ns["first_bar"]
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
        k = len(ours) - (nW + nL)
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
            rows.append(f"{day[-5:]}:n{len(ours)} NOSOL")
        else:
            total_rm += len(best[1])
            if best[0] < 0.02:
                cents += 1
            rows.append(f"{day[-5:]}:rm{len(best[1])} ${best[0]:.0f}")
    return total_rm, cents, nosol, " ".join(rows)


print("=== micro-grid around {X2:2500, capM:20, cd:3} ===")
micro = []
for X2 in (2490.0, 2500.0, 2600.0, 2750.0, 3000.0):
    for capM in (19, 20, 21, 22):
        for cd in (2, 3, 4):
            micro.append({"X2": X2, "capM": capM, "cd": cd})
# also with XC tweaks + lossN16 on the center
for X in (1550.0, 1700.0, 1800.0, 1900.0):
    micro.append({"X": X, "X2": 2500.0, "capM": 20, "cd": 3})
for C in (300.2, 500.0, 700.0, 1328.5):
    micro.append({"C": C, "X2": 2500.0, "capM": 20, "cd": 3})
micro.append({"X2": 2500.0, "capM": 20, "cd": 3, "lossN": 16})
micro.append({"X2": 2500.0, "capM": 20, "cd": 3, "lossN": 14})
micro.append({"X2": 2500.0, "capM": 20, "cd": 3, "eveP": 3000.0})

rows = []
for extra in micro:
    cfg = dict(BASE)
    cfg.update(extra)
    okN, bad = label_check(cfg)
    tk, _ = replay(LATE, cfg)
    a = agg(tk)
    rm, cents, nosol, detail = jan_detail(tk)
    rows.append({"cfg": extra, "hard": okN, "agg": a, "score": round(score(a), 4),
                 "jan": {"rm": rm, "cents": cents, "nosol": nosol}})
ok = [r for r in rows if r["hard"] == 42 and r["jan"]["nosol"] <= 2 and r["jan"]["cents"] >= 5]
ok.sort(key=lambda r: r["score"])
for r in ok[:15]:
    a = r["agg"]
    print(f"score={r['score']:.4f} {str(r['cfg']):50} n={a['n']} net={a['net']:9.0f} "
          f"wr={a['wr']} pf={a['pf']} dd={a['dd']:.0f} hold={a['holdL']}/{a['holdS']} "
          f"jan rm={r['jan']['rm']} ns={r['jan']['nosol']}")

best = ok[0]
print(f"\n=== FINAL: {best['cfg']} ===")
cfg = dict(BASE)
cfg.update(best["cfg"])
tk, _ = replay(LATE, cfg)
a = agg(tk)
rm, cents, nosol, detail = jan_detail(tk)
p = np.array([t["pnl"] for t in tk])
d = np.array([t["dir"] for t in tk])
h = np.array([t["hold_min"] for t in tk])

print(f"n={a['n']} L{a['L']}/S{a['S']} net={a['net']} wr={a['wr']} pf={a['pf']} dd={a['dd']}")
print(f"hold={a['hold']} ({a['holdL']}/{a['holdS']}) lw={a['lw']} ll={a['ll']}")
print(f"lnet={a['lnet']} snet={a['snet']}")
for lbl, mask in (("LONG", d > 0), ("SHORT", d < 0)):
    pp = p[mask]
    w = pp > 0
    gl = pp[~w].sum()
    print(f"{lbl}: n={mask.sum()} net={pp.sum():.2f} wr={w.mean()*100:.2f} pf={pp[w].sum()/-gl:.3f}")
wins = p > 0
print(f"avg={p.mean():.2f} avgW={p[wins].mean():.2f} avgL={p[~wins].mean():.2f} "
      f"wl={p[wins].mean()/-p[~wins].mean():.3f}")
# consec runs
cw = cl = mw = ml = 0
for x in p:
    if x > 0:
        cw += 1
        cl = 0
    else:
        cl += 1
        cw = 0
    mw = max(mw, cw)
    ml = max(ml, cl)
print(f"consecW={mw} consecL={ml} (target 8 / 15)")
n_sessions = int(first_bar.sum())
print(f"trades/day={len(tk)/n_sessions:.2f} (target 8.26)")
print(f"jan rm={rm} cents={cents} nosol={nosol} | {detail}")

sess_per_month = defaultdict(int)
for sid in set(int(s) for s in sess_id):
    sess_per_month[sess_end_day[sid][:7]] += 1
bym = defaultdict(list)
for t in tk:
    bym[sess_end_day[t["session"]][:7]].append(t)
print("\nmonth  sess    n  t/day      net   (base-model n)")
month_rows = []
for m in sorted(bym):
    ts_ = bym[m]
    pp = np.array([t["pnl"] for t in ts_])
    ns_ = sess_per_month[m]
    month_rows.append({"month": m, "n": len(ts_), "tpd": round(len(ts_) / ns_, 2),
                       "net": round(float(pp.sum()), 2)})
    print(f"{m} {ns_:>4} {len(ts_):>5} {len(ts_)/ns_:>6.2f} {pp.sum():>9.0f}")

# attribution: what each rule removed (vs base D-gate taken set)
tk_base, _ = replay(LATE, BASE)
base_keys = {(t["entry_i"], t["exit_i"]) for t in tk_base}
fin_keys = {(t["entry_i"], t["exit_i"]) for t in tk}
removed = base_keys - fin_keys
added = fin_keys - base_keys
rem_tr = [t for t in tk_base if (t["entry_i"], t["exit_i"]) in removed]
rp = np.array([t["pnl"] for t in rem_tr]) if rem_tr else np.array([0.0])
print(f"\nvs base D-gate: removed {len(removed)} legs (sum pnl {rp.sum():.0f}, "
      f"avg {rp.mean():.1f}), newly-taken {len(added)} legs")
rem_bym = defaultdict(int)
for t in rem_tr:
    rem_bym[sess_end_day[t["session"]][:7]] += 1
print("removed by month:", dict(sorted(rem_bym.items(), key=lambda kv: -kv[1])[:8]))

with open(os.path.join(OUT, "v_mg_final.json"), "w") as f:
    json.dump({"micro_ok": ok, "final_cfg": cfg, "final_agg": a,
               "final_jan": {"rm": rm, "cents": cents, "nosol": nosol, "detail": detail},
               "months": month_rows}, f, indent=1, default=str)
print("[v_mg_final] done", flush=True)
