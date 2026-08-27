"""SCOPING part 2 - does the box removal survive the FIXED-DRAWDOWN metric?

Engineering reconnaissance only. The campaign's headline is weekly $ at a FIXED $20,245 max
drawdown, which is scale-invariant and cannot be inflated by leverage. A change that adds raw
dollars while raising drawdown can be WORSE at fixed DD, and CLAUDE.md forbids letting a reduced
risk denominator masquerade as alpha - so the reverse must be checked too.

No selection, no gate, no promotion. One UNIFORM comparison per arm.
"""
import os
import sys
import time

import numpy as np
import pandas as pd

SRC = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\research\weekly_edge\src"
sys.path.insert(0, SRC)
import run_we_w01 as W1                                                   # noqa: E402
from run_we_w01 import ROOT                                               # noqa: E402
from run_we_w17 import load_deep                                          # noqa: E402
from run_we_w26 import fills_daily                                        # noqa: E402
from run_we_w37 import causal_score                                       # noqa: E402
from run_we_w39 import WIN                                                # noqa: E402
from run_we_w97 import votes                                              # noqa: E402
from run_we_w98 import gfills, TICKV                                      # noqa: E402
from we_fastctx import fast_build_context                                 # noqa: E402
from run_rr_w001 import score_to_size                                     # noqa: E402

INF = 1e18
DDT = 20245.0
A, B = np.datetime64("2022-07-01"), np.datetime64("2026-08-01")
t0 = time.time()

D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
W1.DEV_END = pd.Timestamp("2026-07-31").date()
X = fast_build_context(D)
z = np.load(os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out", "mem_ext.npz"))
vl, _ = votes(D, z["mem"], z["bmom"], z["tilt"], X, z["bmom"])
p = vl.astype(np.int8)
n, tarr, sid, fb = D["n"], D["t"], D["sid"], D["fb"]
NS = D["n_sess"]
prof = pd.read_csv(os.path.join(ROOT, "runs", "WE_W82_FILLAUDIT", "out",
                                "spread_by_minute.csv")).set_index("mod")["sp_tk"]
pd_ = {int(k): float(v) for k, v in prof.items()}
mod = np.array([pd.Timestamp(x).hour * 60 + pd.Timestamp(x).minute for x in tarr])
spk = np.array([pd_.get(int(m), 3.0) for m in mod])
lo_of = {int(sid[i]): int(i) for i in np.flatnonzero(fb)}
in_win = {s: (A <= tarr[lo_of[s]] < B) for s in range(NS)}


def i_of(ts):
    return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))


bb = fills_daily(D, p, halt=1300, target=1000)
ee = np.array([i_of(x["et"]) for x in bb if A <= np.datetime64(x["et"]) < B])
s_, _ = causal_score(X, ee, window=WIN)
sz = score_to_size(s_, n)


def arm(halt, target, label):
    tr = gfills(D, p, size_at_entry=sz, halt=halt, target=target, per_ctr=True)
    rows = []
    for t in tr:
        e = i_of(t["et"])
        if not in_win[int(sid[e])]:
            continue
        x = i_of(t["xt"])
        rows.append(dict(et=pd.Timestamp(t["et"]), u=t["u"],
                         net=t["pnl"] - t["u"] * TICKV * (spk[e] + spk[x]) / 2.0,
                         cm=t["u"] * (x - e)))
    T = pd.DataFrame(rows)
    iso = T["et"].dt.isocalendar()
    key = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).to_numpy()
    w = T.groupby(key)["net"].sum()
    eq = T["net"].cumsum().to_numpy()
    dd = float((np.maximum.accumulate(eq) - eq).max())
    return dict(label=label, n=len(T), net=float(T["net"].sum()), weeks=len(w),
                wmean=float(w.mean()), maxdd=dd, fixdd=float(w.mean()) * DDT / max(dd, 1e-9),
                poswk=100 * float((w > 0).mean()), ctrmin=float(T["cm"].sum()),
                t=float(w.mean()) / max(w.std(ddof=1) / np.sqrt(len(w)), 1e-9))


ARMS = [arm(1300.0, 1000.0, "BASELINE (halt -1300 / target +1000)"),
        arm(INF, None, "NO BOX AT ALL"),
        arm(INF, 1000.0, "no halt, keep target"),
        arm(1300.0, None, "keep halt, no target"),
        arm(2600.0, 2000.0, "box x2 (uniformly looser)")]

print()
print("=" * 118)
print("=== SCOPING 2 - the box at the FIXED-DRAWDOWN metric.  UNIFORM arms only, no selection.")
print("=" * 118)
print(f"{'arm':<38}{'trades':>8}{'raw net':>12}{'maxDD':>11}{'wk $ @fixDD':>13}"
      f"{'pos wk':>9}{'t':>7}{'ctr-min':>11}")
for a in ARMS:
    print(f"{a['label']:<38}{a['n']:>8,}{a['net']:>12,.0f}{a['maxdd']:>11,.0f}"
          f"{a['fixdd']:>13,.0f}{a['poswk']:>8.1f}%{a['t']:>7.2f}{a['ctrmin']:>11,.0f}")
b = ARMS[0]
print()
print("    vs BASELINE:")
for a in ARMS[1:]:
    print(f"      {a['label']:<34} raw {a['net']-b['net']:>+10,.0f}   "
          f"maxDD {a['maxdd']-b['maxdd']:>+10,.0f}   "
          f"wk@fixDD {a['fixdd']-b['fixdd']:>+8,.0f} ({100*(a['fixdd']/b['fixdd']-1):>+6.1f} %)   "
          f"exposure {100*(a['ctrmin']/b['ctrmin']-1):>+6.1f} %")
print()
print("    CLAUDE.md: never let leverage, sizing or a reduced risk denominator masquerade as")
print("    information alpha. The fixed-DD column is the one that decides, not raw net.")
print(f"[{time.time()-t0:5.0f}s] done")
