"""WE_W20 ENSEMBLE (spec preregistered): aggregate instead of select."""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import ROOT, PV, COMM_RT, STRESS_RT, sm14_1m             # noqa: E402
from run_we_w03 import fills, cd_signals                                 # noqa: E402
from run_we_w09 import intraday_features                                 # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w19 import MEMBERS, QS, weekly, sharpe                       # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W20_ENSEMBLE", "out")
os.makedirs(OUT, exist_ok=True)


def main():
    t0 = _time.time()
    D = load_deep("2022-01-01", "2026-07-31 17:00")
    rng_, dmove, atr, norm = intraday_features(D)
    ratio = np.where(norm > 0, rng_ / np.maximum(norm, 1e-9), 1.0)

    def lag_b(x):
        return np.concatenate([[True], x[:-1]])
    _, cd = cd_signals(D)
    dL, dS = lag_b(cd >= 0), lag_b(cd <= 0)
    TG = {k: sm14_1m(D, 460, return_targets=True, volmults=v) for k, v in MEMBERS.items()}
    print(f"targets ready [{_time.time()-t0:.0f}s]", flush=True)
    tarr = D["t"]
    wkmap = {s: D["wk"][s] for s in range(D["n_sess"])}

    def wk_of(ts):
        i = int(min(np.searchsorted(tarr, ts), D["n"] - 1))
        return wkmap[int(D["sid"][i])]

    CFG, paths, trades = [], {}, {}
    for mem in MEMBERS:
        for q in QS:
            for dg in (True, False):
                for side in ("both", "long"):
                    CFG.append((mem, q, dg, side))
    for k, (mem, q, dg, side) in enumerate(CFG):
        okq = np.ones(D["n"], bool) if q is None else ((norm <= 0) | (ratio >= q))
        aL = okq & (dL if dg else True)
        aS = (okq & (dS if dg else True)) if side == "both" else np.zeros(D["n"], bool)
        tg = TG[mem]
        # the config's realised target path (what it would hold), used for voting
        p = np.where(tg > 0, np.where(aL, 1, 0), np.where(tg < 0, np.where(aS, -1, 0), 0))
        paths[(mem, q, dg, side)] = p.astype(np.int8)
        trades[(mem, q, dg, side)] = fills(D, tg, allow_long=aL, allow_short=aS)
        if (k + 1) % 16 == 0:
            print(f"   configs {k+1}/{len(CFG)} [{_time.time()-t0:.0f}s]", flush=True)

    A = np.datetime64("2022-07-01"); B = np.datetime64("2026-08-01")
    out = open(os.path.join(OUT, "ens.txt"), "w", encoding="utf-8")

    def P(*a):
        print(*a, flush=True); print(*a, file=out)

    def rep(nm, wkd, ntr=None, note=""):
        s, net, pos = sharpe(wkd)
        v = np.array(list(wkd.values()))
        P(f"{nm:<24}{len(v):>7}{net:>12,.0f}{v.mean():>9,.0f}{pos:>8.1f}{v.min():>10,.0f}"
          f"{s:>8.3f}{(ntr if ntr is not None else -1):>8}  {note}")
        return s, wkd

    P(f"{'object':<24}{'weeks':>7}{'net':>12}{'wkMean':>9}{'pos%':>8}{'worst':>10}"
      f"{'sharpe':>8}{'trades':>8}")
    # references from W19
    ref = {}
    for nm, cfg in (("FIXED", ("narrow6", 0.8, True, "both")),
                    ("NAIVE", ("narrow6", None, False, "both")),
                    ("BESTFIXED", ("narrow5", 0.8, True, "long"))):
        d = weekly(trades[cfg], wk_of, A, B)
        n_ = len([x for x in trades[cfg] if A <= np.datetime64(x["et"]) < B])
        ref[nm] = rep(nm, d, n_)[0]

    # E1-E3 exposure-normalised P&L averages (not tradeable, benchmark only)
    def avg(sub, tag):
        acc = {}
        for cfg in sub:
            for w, v in weekly(trades[cfg], wk_of, A, B).items():
                acc[w] = acc.get(w, 0.0) + v / len(sub)
        return rep(tag, acc, note="(benchmark, not tradeable)")[0]
    e1 = avg(CFG, "E1 pnl-avg ALL/64")
    e2 = avg([c for c in CFG if c[3] == "long"], "E2 pnl-avg LONG/32")
    e3 = avg([c for c in CFG if c[2]], "E3 pnl-avg DELTA/32")

    # E4-E6 tradeable votes, 1 contract
    def vote(sub, thresh, tag):
        M = np.vstack([paths[c] for c in sub])
        s = M.sum(axis=0)
        need = thresh * len(sub)
        tgt = np.where(s >= need, 1, np.where(s <= -need, -1, 0)).astype(np.int8)
        trl = fills(D, tgt, allow_long=None, allow_short=None)
        d = weekly(trl, wk_of, A, B)
        n_ = len([x for x in trl if A <= np.datetime64(x["et"]) < B])
        return rep(tag, d, n_)[0], d
    e4, d4 = vote(CFG, 0.5, "E4 vote ALL >=50%")
    e5, d5 = vote([c for c in CFG if c[3] == "long"], 0.5, "E5 vote LONG >=50%")
    e6, d6 = vote(CFG, 0.75, "E6 vote ALL >=75%")

    P("\n=== PREREGISTERED VERDICT ===")
    WF = 0.171
    best_tradeable = max((e4, "E4"), (e5, "E5"), (e6, "E6"))
    P(f"WF {WF:.3f} | NAIVE {ref['NAIVE']:.3f} | FIXED {ref['FIXED']:.3f} | "
      f"BESTFIXED {ref['BESTFIXED']:.3f}")
    P(f"best tradeable aggregate: {best_tradeable[1]} at {best_tradeable[0]:.3f}")
    nd = weekly(trades[("narrow6", None, False, "both")], wk_of, A, B)
    nw = min(nd.values())
    bd = {"E4": d4, "E5": d5, "E6": d6}[best_tradeable[1]]
    v = ("WIN" if (best_tradeable[0] > WF and best_tradeable[0] > ref["NAIVE"]
                   and min(bd.values()) > nw)
         else ("NEUTRAL" if best_tradeable[0] > ref["NAIVE"] else "LOSE"))
    P(f"  -> {v}")

    P("\nper-year Sharpe of the best tradeable aggregate:")
    for yr in ("2022", "2023", "2024", "2025", "2026"):
        vv = np.array([x for w, x in bd.items() if w.startswith(yr)])
        if len(vv) >= 5:
            P(f"   {yr}: {vv.mean()/vv.std(ddof=1):>6.3f}  net {vv.sum():>9,.0f}  "
              f"pos {100*(vv>0).mean():>5.1f}%")
    P("\ncorrelation with the WF selector's weekly nets: computed on shared weeks")
    # rebuild WF weekly quickly from the same trades by re-running the selector rule
    bounds = pd.date_range("2022-07-01", "2026-07-01", freq="QS")
    wf_tr = []
    for bnd in bounds:
        fa = np.datetime64(bnd - pd.DateOffset(months=12)); fb = np.datetime64(bnd)
        ob = np.datetime64(min(bnd + pd.DateOffset(months=3), pd.Timestamp("2026-08-01")))
        best, bs = None, -99
        for cfg, trl in trades.items():
            s, _, _ = sharpe(weekly(trl, wk_of, fa, fb))
            if s > bs:
                bs, best = s, cfg
        wf_tr += [x for x in trades[best] if fb <= np.datetime64(x["et"]) < ob]
    wfd = weekly(wf_tr, wk_of)
    ws = sorted(set(wfd) & set(bd))
    a = np.array([wfd[w] for w in ws]); b = np.array([bd[w] for w in ws])
    P(f"   corr {np.corrcoef(a, b)[0, 1]:.2f} over {len(ws)} shared weeks")
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
