"""WE_W29 FINALWF (spec preregistered): walk-forward the object as it now stands."""
from __future__ import annotations

import os
import sys
import time as _time
from collections import Counter

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_we_w01 as W1                                                  # noqa: E402
from run_we_w01 import ROOT, PV, COMM_RT, STRESS_RT, sm14_1m             # noqa: E402
from run_we_w03 import cd_signals                                        # noqa: E402
from run_we_w09 import intraday_features                                 # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w19 import MEMBERS, QS, weekly, sharpe                       # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W29_FINALWF", "out")
os.makedirs(OUT, exist_ok=True)
BIG = 10 ** 9


def main():
    t0 = _time.time()
    D = load_deep("2022-01-01", "2026-07-31 17:00")
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n = D["n"]
    rng_, dmove, atr, norm = intraday_features(D)
    ratio = np.where(norm > 0, rng_ / np.maximum(norm, 1e-9), 1.0)

    def lag_b(x):
        return np.concatenate([[True], x[:-1]])
    _, cd = cd_signals(D)
    dL = lag_b(cd >= 0)
    TG = {k: sm14_1m(D, 460, return_targets=True, volmults=v) for k, v in MEMBERS.items()}
    print(f"targets ready [{_time.time()-t0:.0f}s]", flush=True)
    tarr = D["t"]
    wkmap = {s: D["wk"][s] for s in range(D["n_sess"])}

    def wk_of(ts):
        i = int(min(np.searchsorted(tarr, ts), n - 1))
        return wkmap[int(D["sid"][i])]

    # per-q voting fractions (the 32 long-only configs are 4 members x 4 q x delta on/off,
    # but the throttle q is a CHOICE here, so the vote is rebuilt per q over
    # 4 members x delta on/off = 8 voters, matching the spec's choice set)
    FRAC = {}
    for q in (0.7, 0.8, 0.9):
        okq = (norm <= 0) | (ratio >= q)
        vs = []
        for mem in MEMBERS:
            tg = TG[mem]
            for dg in (True, False):
                a = okq & (dL if dg else True)
                vs.append(np.where((tg > 0) & a, 1, 0).astype(np.int8))
        FRAC[q] = np.vstack(vs).mean(axis=0)
    print(f"fractions ready [{_time.time()-t0:.0f}s]", flush=True)

    CFG = [(h, tg_, th, q)
           for h in (None, 1300, 2600)
           for tg_ in (None, 1000, 2000)
           for th in (0.40, 0.50, 0.60)
           for q in (0.7, 0.8, 0.9)]
    trades = {}
    for k, (h, tg_, th, q) in enumerate(CFG):
        pos = (FRAC[q] >= th).astype(np.int8)
        trades[(h, tg_, th, q)] = fills_daily(D, pos, halt=(h if h else BIG), target=tg_)
        if (k + 1) % 20 == 0:
            print(f"   configs {k+1}/{len(CFG)} [{_time.time()-t0:.0f}s]", flush=True)

    out = open(os.path.join(OUT, "wf2.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    bounds = pd.date_range("2022-07-01", "2026-07-01", freq="QS")
    P_(f"walk-forward: {len(bounds)} quarterly refits over {len(CFG)} configurations")
    P_(f"{'quarter':<12}{'chosen (halt,target,thresh,q)':<34}{'fitShrp':>9}{'oosNet':>10}"
       f"{'oosShrp':>9}")
    wf, picks = [], []
    for bnd in bounds:
        fa = np.datetime64(bnd - pd.DateOffset(months=12)); fb = np.datetime64(bnd)
        ob = np.datetime64(min(bnd + pd.DateOffset(months=3), pd.Timestamp("2026-08-01")))
        best, bs = None, -99
        for cfg, trl in trades.items():
            s, _, _ = sharpe(weekly(trl, wk_of, fa, fb))
            if s > bs:
                bs, best = s, cfg
        seg = [x for x in trades[best] if fb <= np.datetime64(x["et"]) < ob]
        wf += seg
        s2, net2, _ = sharpe(weekly(seg, wk_of))
        picks.append(best)
        P_(f"{str(bnd.date()):<12}{str(best):<34}{bs:>9.3f}{net2:>10,.0f}"
           f"{(s2 if s2 > -9 else float('nan')):>9.3f}")

    A = np.datetime64(bounds[0]); B = np.datetime64("2026-08-01")
    P_(f"\n{'object':<34}{'weeks':>7}{'net':>12}{'wkMean':>9}{'pos%':>8}{'worst':>10}"
       f"{'sharpe':>8}{'trades':>8}")

    def line(nm, trl):
        d = weekly(trl, wk_of, A, B)
        s, net, pos = sharpe(d)
        v = np.array(list(d.values()))
        ntr = len([x for x in trl if A <= np.datetime64(x["et"]) < B])
        P_(f"{nm:<34}{len(v):>7}{net:>12,.0f}{v.mean():>9,.0f}{pos:>8.1f}{v.min():>10,.0f}"
           f"{s:>8.3f}{ntr:>8}")
        return s, d
    wf_s, wf_d = line("WF_FINAL (walk-forward)", wf)
    fx_s, _ = line("FIXED_FINAL (1300/1000/0.5/0.8)", trades[(1300, 1000, 0.50, 0.8)])
    nv_s, _ = line("NAIVE (no box, 0.5, 0.8)", trades[(None, None, 0.50, 0.8)])
    bestcfg, bests = None, -99
    for cfg, trl in trades.items():
        s, _, _ = sharpe(weekly(trl, wk_of, A, B))
        if s > bests:
            bests, bestcfg = s, cfg
    bf_s, _ = line(f"BESTFIXED {bestcfg}", trades[bestcfg])

    P_("\n=== PREREGISTERED VERDICT ===")
    v = ("STRONG" if (wf_s >= 0.8 * fx_s and wf_s > nv_s)
         else ("WEAK" if wf_s > nv_s else "FAIL"))
    P_(f"WF {wf_s:.3f} | FIXED {fx_s:.3f} (0.8x = {0.8*fx_s:.3f}) | NAIVE {nv_s:.3f} | "
       f"BESTFIXED {bf_s:.3f}  ->  {v}")
    ch = sum(1 for a, b in zip(picks, picks[1:]) if a != b)
    P_(f"choice churn: {len(set(picks))} distinct over {len(picks)} refits, {ch} changes "
       f"({100*ch/max(len(picks)-1,1):.0f}%)")
    for cfg, k in Counter(picks).most_common(5):
        P_(f"   chosen {k:>2}x: {cfg}")
    P_("\nWF per-year:")
    for yr in ("2022", "2023", "2024", "2025", "2026"):
        vv = np.array([x for w, x in wf_d.items() if w.startswith(yr)])
        if len(vv) >= 5:
            P_(f"   {yr}: Sharpe {vv.mean()/vv.std(ddof=1):>6.3f}  net {vv.sum():>9,.0f}  "
               f"pos {100*(vv>0).mean():>5.1f}%")
    pd.DataFrame([dict(quarter=str(b.date()), cfg=str(p)) for b, p in zip(bounds, picks)]
                 ).to_csv(os.path.join(OUT, "summary.csv"), index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
