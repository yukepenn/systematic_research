"""SCOPING ONLY - engineering reconnaissance, no inference, no gate, no promotion.

Frontier row 1 is "is SELECTIVE box un-latching worth anything?". Before spending a wave on it,
measure the thing it turns on: what is the CAUSAL VALUE OF THE LATCH ITSELF? One counterfactual per
latched session - "what if the box had not latched?" - using RR_W001's certified session replay.

This produces a scoping number, not a result. Nothing is selected or promoted.
"""
import os
import sys
import time

import numpy as np
import pandas as pd

SRC = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\research\weekly_edge\src"
sys.path.insert(0, SRC)
import run_we_w01 as W1                                                   # noqa: E402
from run_we_w01 import ROOT, COMM_RT, PV                                  # noqa: E402
from run_we_w17 import load_deep                                          # noqa: E402
from run_we_w26 import fills_daily                                        # noqa: E402
from run_we_w37 import causal_score                                       # noqa: E402
from run_we_w39 import WIN                                                # noqa: E402
from run_we_w97 import votes                                              # noqa: E402
from run_we_w98 import gfills, TICKV                                      # noqa: E402
from we_fastctx import fast_build_context                                 # noqa: E402
from run_rr_w001 import gfills_sess, score_to_size                        # noqa: E402

INF = 1e18
A, B = np.datetime64("2022-07-01"), np.datetime64("2026-08-01")
t0 = time.time()

D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
W1.DEV_END = pd.Timestamp("2026-07-31").date()
X = fast_build_context(D)
z = np.load(os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out", "mem_ext.npz"))
vl, _ = votes(D, z["mem"], z["bmom"], z["tilt"], X, z["bmom"])
p = vl.astype(np.int8)
n, tarr, sid, fb, lb = D["n"], D["t"], D["sid"], D["fb"], D["lb"]
NS = D["n_sess"]
sess_lo = {int(sid[i]): int(i) for i in np.flatnonzero(fb)}
sess_hi = {int(sid[i]): int(i) for i in np.flatnonzero(lb)}
prof = pd.read_csv(os.path.join(ROOT, "runs", "WE_W82_FILLAUDIT", "out",
                                "spread_by_minute.csv")).set_index("mod")["sp_tk"]
pd_ = {int(k): float(v) for k, v in prof.items()}
mod = np.array([pd.Timestamp(x).hour * 60 + pd.Timestamp(x).minute for x in tarr])
spk = np.array([pd_.get(int(m), 3.0) for m in mod])


def net(t):
    return t["pnl"] - t["u"] * TICKV * (spk[t["eti"]] + spk[t["xti"]]) / 2.0


def i_of(ts):
    return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))


in_win = np.zeros(NS, bool)
for s in range(NS):
    if A <= tarr[sess_lo[s]] < B:
        in_win[s] = True

bb = fills_daily(D, p, halt=1300, target=1000)
ee = np.array([i_of(x["et"]) for x in bb if A <= np.datetime64(x["et"]) < B])
s_, _ = causal_score(X, ee, window=WIN)
sz = score_to_size(s_, n)

print(f"[{time.time()-t0:5.0f}s] baseline built")
rows = []
for s in range(NS):
    if not in_win[s]:
        continue
    lo, hi = sess_lo[s], sess_hi[s]
    base = gfills_sess(D, p, sz, lo, hi, halt=1300.0, target=1000.0, per_ctr=True)
    if not base:
        continue
    # did the box latch? replay with an infinite box and see whether the schedule changes
    free = gfills_sess(D, p, sz, lo, hi, halt=INF, target=None, per_ctr=True)
    latched = len(free) != len(base) or any(
        a["et"] != b["et"] or a["xt"] != b["xt"] for a, b in zip(base, free))
    if not latched:
        continue
    rows.append(dict(session=s, date=str(pd.Timestamp(tarr[lo]).date()),
                     base_net=sum(net(t) for t in base), free_net=sum(net(t) for t in free),
                     base_n=len(base), free_n=len(free)))

R = pd.DataFrame(rows)
R["latch_value"] = R["base_net"] - R["free_net"]          # value OF latching
print()
print("=" * 96)
print("=== SCOPING - the CAUSAL VALUE OF THE SESSION BOX LATCH.  Ex post.  Nothing promoted.")
print("=" * 96)
print(f"    in-window sessions where the box CHANGED the schedule : {len(R):,}")
print(f"    total value of latching                               ${R['latch_value'].sum():,.0f}")
print(f"    mean per latched session                              ${R['latch_value'].mean():,.2f}")
print(f"    median                                                ${R['latch_value'].median():,.2f}")
print(f"    sessions where latching HELPED                        "
      f"{int((R['latch_value'] > 0).sum()):,}  ({100*(R['latch_value'] > 0).mean():.1f} %)")
print(f"    sessions where latching HURT                          "
      f"{int((R['latch_value'] < 0).sum()):,}  ({100*(R['latch_value'] < 0).mean():.1f} %)")
print()
print(f"    EX-POST ceiling of perfect selective un-latching      "
      f"${-R.loc[R['latch_value'] < 0, 'latch_value'].sum():,.0f}")
print(f"    (i.e. never latch on exactly the sessions where it hurt - a LEVEL-A action oracle,")
print(f"     not available money)")
print()
print(f"    for scale: P1/PCT realised net over the same window is $296,911")
R.to_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "latch_scope.csv"), index=False)
print(f"[{time.time()-t0:5.0f}s] done")
