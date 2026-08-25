"""WE_W08 amendment 1 (diagnostic, preregistered in spec as the BIG-DAY analysis):
big/small-day capture for the INCUMBENT engines, and regime-complementarity of the pullback
engine with them. No selection, no new hypotheses.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import ROOT, PV, COMM_RT, STRESS_RT, load, week_table, summarize, sm14_1m
from run_we_w03 import fills, cd_signals                                 # noqa: E402
from run_we_w06a import available_move                                   # noqa: E402
from run_we_w07 import session_metrics                                   # noqa: E402
from run_we_w08 import pullback_trades                                   # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "research", "original_trader_reconstruction",
                                "solar_family", "src"))
from solarwave import SolarWaveParams                                    # noqa: E402
import inverse_core as IC                                                # noqa: E402
from run_r13_strict_master import run_master                             # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W08_PULLBACK", "out")


def main():
    t0 = _time.time()
    D = load()
    n_sess, tarr = D["n_sess"], D["t"]
    idx = np.arange(D["n"])
    starts = np.zeros(n_sess, np.int64); ends = np.zeros(n_sess, np.int64)
    for s in range(n_sess):
        m = idx[D["sid"] == s]
        starts[s], ends[s] = m[0], m[-1] + 1
    avail = np.zeros(n_sess); adir = np.zeros(n_sess, np.int8)
    for s in range(n_sess):
        avail[s], adir[s], _, _ = available_move(D["c"], starts[s], ends[s])
    big = avail >= 500

    def lag_i8(a):
        return np.concatenate([[0], a[:-1]]).astype(np.int8)

    def lag_b(a):
        return np.concatenate([[True], a[:-1]])
    _, cd_arr = cd_signals(D)
    aL, aS = lag_b(cd_arr >= 0), lag_b(cd_arr <= 0)

    NARROW = [6, 8, 10, 12, 14, 16]
    tgn = sm14_1m(D, 460, return_targets=True, volmults=NARROW)
    tga = sm14_1m(D, 460, return_targets=True)
    bb = IC.prepare(D["df"], SolarWaveParams())
    S = {}
    S["S1"] = [dict(d=x["d"], pnl=x["pnl"], et=str(bb["t"][x["ei"]]),
                    xt=str(bb["t"][x["xi"]]))
               for x in run_master(bb, exit_strict=False, gate=True, comm=COMM_RT)]
    S["S4n.gdl"] = fills(D, tgn, allow_long=aL, allow_short=aS)
    S["S4a.h1300.gdl"] = fills(D, tga, halt=1300, allow_long=aL, allow_short=aS)
    trs = lag_i8(np.sign(tgn).astype(np.int8))
    S["PB.R236.trail80"] = pullback_trades(D, trs, 0.236, "X_TRAIL_PTS", 80,
                                           allow_long=aL, allow_short=aS)
    S["PB.R236.trend"] = pullback_trades(D, trs, 0.236, "X_TREND", None,
                                         allow_long=aL, allow_short=aS)
    print(f"sleeves ready [{_time.time()-t0:.0f}s]", flush=True)

    out = open(os.path.join(OUT, "regime.txt"), "w", encoding="utf-8")

    def P(*a):
        print(*a, flush=True); print(*a, file=out)

    P(f"big days (avail>=500pts): {big.sum()} of {n_sess} ({100*big.mean():.1f}%), "
      f"carrying {100*avail[big].sum()/avail.sum():.1f}% of all available points\n")
    P(f"{'sleeve':<20}{'CAPT%':>8}{'bigCAP':>8}{'smlCAP':>8}{'bigPts':>10}{'smlPts':>10}"
      f"{'ratio':>8}")
    capv = {}
    for nm, trl in S.items():
        v = np.zeros(n_sess)
        for x in trl:
            i = int(min(np.searchsorted(tarr, np.datetime64(x["et"])), D["n"] - 1))
            v[int(D["sid"][i])] += x["pnl"] / PV
        capv[nm] = v
        b = 100 * v[big].sum() / avail[big].sum()
        s_ = 100 * v[~big].sum() / avail[~big].sum()
        P(f"{nm:<20}{100*v.sum()/avail.sum():>8.2f}{b:>8.2f}{s_:>8.2f}"
          f"{v[big].sum():>10,.0f}{v[~big].sum():>10,.0f}{b/s_ if s_ else float('nan'):>8.2f}")

    P("\nWEEKLY-NET CORRELATIONS (dev+hold pooled weeks)")
    wk = {nm: week_table(trl, D, lambda x: x["xt"]) for nm, trl in S.items()}
    wv = {}
    for nm, t_ in wk.items():
        d = {}
        for s, (net, _) in t_.items():
            d[D["wk"][s]] = d.get(D["wk"][s], 0.0) + net
        wv[nm] = d
    keys = list(S)
    allw = sorted(set().union(*[set(wv[k]) for k in keys]))
    M = np.array([[wv[k].get(w, 0.0) for w in allw] for k in keys])
    C = np.corrcoef(M)
    P("            " + "".join(f"{k[:14]:>16}" for k in keys))
    for i, k in enumerate(keys):
        P(f"{k:<12}" + "".join(f"{C[i, j]:>16.2f}" for j in range(len(keys))))

    P("\nPORTFOLIOS (dev | holdout)")
    combos = {
        "S1+S4n": ["S1", "S4n.gdl"],
        "S1+S4n+PBtrail": ["S1", "S4n.gdl", "PB.R236.trail80"],
        "S1+S4n+PBtrend": ["S1", "S4n.gdl", "PB.R236.trend"],
        "S4n+PBtrail": ["S4n.gdl", "PB.R236.trail80"],
        "S1+S4a.h1300+PBtrail": ["S1", "S4a.h1300.gdl", "PB.R236.trail80"],
    }
    for cn, parts in combos.items():
        p = {}
        for nm in parts:
            for s, (net, ntr) in wk[nm].items():
                a = p.setdefault(s, [0.0, 0]); a[0] += net; a[1] += ntr
        rd, rh = summarize(p, D, "dev"), summarize(p, D, "hold")
        sd = np.array(rd["_net"]) - STRESS_RT * np.array(rd["_ntr"])
        P(f"{cn:<24} dev mean {rd['mean']:>7,.0f} pos {rd['pos']:>5.1f}% "
          f"worst {rd['worst']:>9,.0f} shrp {rd['sharpe']:>6.3f} strs {sd.mean():>7,.0f}"
          f"  |  hold mean {rh['mean']:>7,.0f} pos {rh['pos']:>5.1f}% shrp {rh['sharpe']:>6.3f}")
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
