"""WE_W19 WALKFORWARD (spec preregistered): quarterly refit on trailing 12m, trade next quarter.

Key efficiency fact used here: every sleeve is session-flat, so a config's trade list computed
once over the whole period can be sliced by session without any error. 64 configs are built
once; each refit then only re-scores precomputed trades on its trailing window.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_we_w01 as W1                                                  # noqa: E402
from run_we_w01 import ROOT, PV, COMM_RT, STRESS_RT, sm14_1m             # noqa: E402
from run_we_w03 import fills, cd_signals                                 # noqa: E402
from run_we_w09 import intraday_features                                 # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W19_WALKFORWARD", "out")
os.makedirs(OUT, exist_ok=True)
MEMBERS = {"narrow5": [6, 8, 10, 12, 14], "narrow6": [6, 8, 10, 12, 14, 16],
           "narrow7": [6, 8, 10, 12, 14, 16, 18],
           "all13": [6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]}
QS = [None, 0.7, 0.8, 0.9]


def weekly(trades, wk_of, a=None, b=None):
    d = {}
    for x in trades:
        ts = np.datetime64(x["et"])
        if (a is not None and ts < a) or (b is not None and ts >= b):
            continue
        w = wk_of(ts)
        d[w] = d.get(w, 0.0) + x["pnl"]
    return d


def sharpe(d):
    if len(d) < 8:
        return -9.0, 0.0, 0.0
    v = np.array(list(d.values()))
    s = v.mean() / v.std(ddof=1) if v.std(ddof=1) > 0 else 0.0
    return float(s), float(v.sum()), float((v > 0).mean() * 100)


def main():
    t0 = _time.time()
    D = load_deep("2022-01-01", "2026-07-31 17:00")
    print(f"bars {D['n']:,}  sessions {D['n_sess']:,} [{_time.time()-t0:.0f}s]", flush=True)
    rng_, dmove, atr, norm = intraday_features(D)
    ratio = np.where(norm > 0, rng_ / np.maximum(norm, 1e-9), 1.0)

    def lag_b(x):
        return np.concatenate([[True], x[:-1]])
    _, cd = cd_signals(D)
    dL, dS = lag_b(cd >= 0), lag_b(cd <= 0)
    TG = {k: sm14_1m(D, 460, return_targets=True, volmults=v) for k, v in MEMBERS.items()}
    print(f"targets ready [{_time.time()-t0:.0f}s]", flush=True)

    tarr = D["t"]
    wkmap = {}
    for s in range(D["n_sess"]):
        wkmap[s] = D["wk"][s]

    def wk_of(ts):
        i = int(min(np.searchsorted(tarr, ts), D["n"] - 1))
        return wkmap[int(D["sid"][i])]

    CFG = []
    for mem in MEMBERS:
        for q in QS:
            for dg in (True, False):
                for side in ("both", "long"):
                    CFG.append((mem, q, dg, side))
    trades = {}
    for k, (mem, q, dg, side) in enumerate(CFG):
        okq = np.ones(D["n"], bool) if q is None else ((norm <= 0) | (ratio >= q))
        aL = okq & (dL if dg else True)
        aS = (okq & (dS if dg else True)) if side == "both" else np.zeros(D["n"], bool)
        trades[(mem, q, dg, side)] = fills(D, TG[mem], allow_long=aL, allow_short=aS)
        if (k + 1) % 16 == 0:
            print(f"   configs {k+1}/{len(CFG)} [{_time.time()-t0:.0f}s]", flush=True)

    out = open(os.path.join(OUT, "wf.txt"), "w", encoding="utf-8")

    def P(*a):
        print(*a, flush=True); print(*a, file=out)

    bounds = pd.date_range("2022-07-01", "2026-07-01", freq="QS")
    P(f"walk-forward: {len(bounds)} quarterly refits, trailing 12-month fit, "
      f"{len(CFG)} configs per refit")
    P(f"{'quarter':<12}{'chosen config':<34}{'fitShrp':>9}{'oosNet':>10}{'oosShrp':>9}"
      f"{'oosPos%':>9}")
    wf_trades = []
    picks = []
    for i, bnd in enumerate(bounds):
        fit_a = np.datetime64(bnd - pd.DateOffset(months=12))
        fit_b = np.datetime64(bnd)
        nxt = bnd + pd.DateOffset(months=3)
        oos_b = np.datetime64(min(nxt, pd.Timestamp("2026-08-01")))
        best, bs = None, -99
        for cfg, trl in trades.items():
            s, _, _ = sharpe(weekly(trl, wk_of, fit_a, fit_b))
            if s > bs:
                bs, best = s, cfg
        seg = [x for x in trades[best]
               if fit_b <= np.datetime64(x["et"]) < oos_b]
        wf_trades += seg
        s2, net2, pos2 = sharpe(weekly(seg, wk_of))
        picks.append(best)
        P(f"{str(bnd.date()):<12}{str(best):<34}{bs:>9.3f}{net2:>10,.0f}"
          f"{s2 if s2 > -9 else float('nan'):>9.3f}{pos2:>9.1f}")

    P("\n=== COMPARISONS (all on the stitched walk-forward period) ===")
    wf_a = np.datetime64(bounds[0])
    wf_b = np.datetime64(pd.Timestamp("2026-08-01"))

    def line(nm, trl):
        d = weekly(trl, wk_of, wf_a, wf_b)
        s, net, pos = sharpe(d)
        v = np.array(list(d.values()))
        ntr = len([x for x in trl if wf_a <= np.datetime64(x["et"]) < wf_b])
        stress = float((v - STRESS_RT * ntr / max(len(v), 1)).mean())
        P(f"{nm:<28}{len(d):>7}{net:>12,.0f}{v.mean():>9,.0f}{pos:>8.1f}"
          f"{v.min():>10,.0f}{s:>8.3f}{ntr:>8}")
        return s, net

    P(f"{'object':<28}{'weeks':>7}{'net':>12}{'wkMean':>9}{'pos%':>8}{'worst':>10}"
      f"{'sharpe':>8}{'trades':>8}")
    wf_s, wf_net = line("WF walk-forward", wf_trades)
    fx_s, fx_net = line("FIXED (narrow6,0.8,dg,both)", trades[("narrow6", 0.8, True, "both")])
    nv_s, nv_net = line("NAIVE (narrow6,none,off,both)", trades[("narrow6", None, False, "both")])
    bestcfg, bests = None, -99
    for cfg, trl in trades.items():
        s, _, _ = sharpe(weekly(trl, wk_of, wf_a, wf_b))
        if s > bests:
            bests, bestcfg = s, cfg
    bf_s, bf_net = line(f"BESTFIXED {bestcfg}", trades[bestcfg])

    P("\n=== PREREGISTERED VERDICT ===")
    v = ("STRONG" if (wf_s >= 0.8 * fx_s and wf_s > nv_s)
         else ("WEAK" if wf_s > nv_s else "FAIL"))
    P(f"WF {wf_s:.3f} | FIXED {fx_s:.3f} (0.8x = {0.8*fx_s:.3f}) | NAIVE {nv_s:.3f} | "
      f"BESTFIXED {bf_s:.3f}  ->  {v}")
    uniq = len(set(picks))
    changes = sum(1 for a, b in zip(picks, picks[1:]) if a != b)
    P(f"choice instability: {uniq} distinct configs over {len(picks)} refits, "
      f"{changes} changes ({100*changes/max(len(picks)-1,1):.0f}% of boundaries)")
    from collections import Counter
    for cfg, k in Counter(picks).most_common(5):
        P(f"   chosen {k:>2}x: {cfg}")
    pd.DataFrame([dict(quarter=str(b.date()), cfg=str(p)) for b, p in zip(bounds, picks)]
                 ).to_csv(os.path.join(OUT, "summary.csv"), index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
