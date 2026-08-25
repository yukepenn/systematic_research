"""WE_W10 EXPOSURE (spec preregistered): mirror (size up on high range) + generality + portfolios."""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import ROOT, PV, COMM_RT, STRESS_RT, load, week_table, summarize, sm14_1m
from run_we_w03 import fills, cd_signals, halt_overlay_trades            # noqa: E402
from run_we_w06a import available_move                                   # noqa: E402
from run_we_w07 import session_metrics                                   # noqa: E402
from run_we_w09 import intraday_features                                 # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "research", "original_trader_reconstruction",
                                "solar_family", "src"))
from solarwave import SolarWaveParams                                    # noqa: E402
import inverse_core as IC                                                # noqa: E402
from run_r13_strict_master import run_master                             # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W10_EXPOSURE", "out")
os.makedirs(OUT, exist_ok=True)


def fills_sized(D, tgt_arr, size_arr, allow_long=None, allow_short=None):
    """Fills where position size is read from size_arr at the ENTRY bar (already causal)."""
    t, o, h, l, c = D["t"], D["o"], D["h"], D["l"], D["c"]
    fb, lb, n = D["fb"], D["lb"], D["n"]
    trades = []
    pos = 0; u = 0; epx = 0.0; eti = -1
    for i in range(n):
        want = int(tgt_arr[i - 1]) if i > 0 and not fb[i] else 0
        if want != pos and want != 0:
            blocked = ((want > 0 and allow_long is not None and not allow_long[i]) or
                       (want < 0 and allow_short is not None and not allow_short[i]))
            if blocked:
                want = 0 if pos == 0 or want == -pos else pos
        if want != pos:
            if pos != 0:
                trades.append(dict(d=pos, et=str(t[eti]), xt=str(t[i]),
                                   pnl=pos * u * (o[i] - epx) * PV - COMM_RT * u))
            pos = want
            if pos != 0:
                epx, eti, u = o[i], i, int(size_arr[i])
                if u < 1:
                    pos = 0
        if lb[i] and pos != 0:
            trades.append(dict(d=pos, et=str(t[eti]), xt=str(t[i]),
                               pnl=pos * u * (c[i] - epx) * PV - COMM_RT * u))
            pos = 0
    return trades


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
    rng, dmove, atr, norm = intraday_features(D)
    ratio = np.where(norm > 0, rng / np.maximum(norm, 1e-9), 1.0)
    print(f"features ready [{_time.time()-t0:.0f}s]", flush=True)

    def lag_b(a):
        return np.concatenate([[True], a[:-1]])
    _, cd_arr = cd_signals(D)
    aL0, aS0 = lag_b(cd_arr >= 0), lag_b(cd_arr <= 0)
    tgn = sm14_1m(D, 460, return_targets=True, volmults=[6, 8, 10, 12, 14, 16])
    tga = sm14_1m(D, 460, return_targets=True)
    tg5 = sm14_1m(D, 460, with_solar=False, with_bmom=True, return_targets=True)
    bb = IC.prepare(D["df"], SolarWaveParams())
    s1_trades = [dict(d=x["d"], pnl=x["pnl"], et=str(bb["t"][x["ei"]]),
                      xt=str(bb["t"][x["xi"]]))
                 for x in run_master(bb, exit_strict=False, gate=True, comm=COMM_RT)]
    print(f"bases ready [{_time.time()-t0:.0f}s]", flush=True)

    out = open(os.path.join(OUT, "exposure.txt"), "w", encoding="utf-8")

    def P(*a):
        print(*a, flush=True); print(*a, file=out)

    rows = []

    def rep(nm, trl):
        v = np.zeros(n_sess)
        for x in trl:
            i = int(min(np.searchsorted(tarr, np.datetime64(x["et"])), D["n"] - 1))
            v[int(D["sid"][i])] += x["pnl"] / PV
        b = 100 * v[big].sum() / avail[big].sum()
        s_ = 100 * v[~big].sum() / avail[~big].sum()
        wt = week_table(trl, D, lambda x: x["xt"])
        r = summarize(wt, D, "dev"); rh = summarize(wt, D, "hold")
        stress = float((np.array(r["_net"]) - STRESS_RT * np.array(r["_ntr"])).mean())
        P(f"{nm:<26}{100*v.sum()/avail.sum():>7.2f}{b:>8.2f}{s_:>8.2f}{v[~big].sum():>9,.0f}"
          f"{r['mean']:>8,.0f}{r['pos']:>7.1f}{r['worst']:>9,.0f}{r['sharpe']:>8.3f}"
          f"{stress:>7,.0f}{r['tpw']:>7.1f}{rh['sharpe']:>8.3f}{rh['pos']:>7.1f}")
        rows.append(dict(name=nm, capture=round(100 * v.sum() / avail.sum(), 2),
                         big=round(b, 2), small=round(s_, 2), small_pts=round(v[~big].sum()),
                         wk_mean=round(r["mean"]), wk_pos=round(r["pos"], 1),
                         wk_worst=round(r["worst"]), wk_sharpe=round(r["sharpe"], 3),
                         stress=round(stress), tpw=round(r["tpw"], 1),
                         hold_sharpe=round(rh["sharpe"], 3), hold_pos=round(rh["pos"], 1)))
        return wt

    P(f"{'variant':<26}{'CAPT%':>7}{'bigCAP':>8}{'smlCAP':>8}{'smlPts':>9}{'wkMean':>8}"
      f"{'wkPos':>7}{'wkWorst':>9}{'wkShrp':>8}{'strs':>7}{'tpw':>7}{'hShrp':>8}{'hPos':>7}")
    P("--- Q1 MIRROR: size 2 when ratio >= hi (base = A_range0.8 on S4n.gdl) ---")
    ok08 = (norm <= 0) | (ratio >= 0.8)
    wt_a08 = rep("S4n.gdl+A0.8 (base)", fills(D, tgn, allow_long=aL0 & ok08,
                                              allow_short=aS0 & ok08))
    for hi in (1.2, 1.5, 2.0):
        size = np.where(ratio >= hi, 2, 1)
        rep(f"P1_size2@{hi}", fills_sized(D, tgn, size, aL0 & ok08, aS0 & ok08))

    P("--- Q2 GENERALITY: same throttle on other sleeves ---")
    rep("S1 (base)", s1_trades)
    for q in (0.7, 0.8, 0.9):
        ok = (norm <= 0) | (ratio >= q)
        keep = []
        for x in s1_trades:
            i = int(min(np.searchsorted(tarr, np.datetime64(x["et"])), D["n"] - 1))
            if ok[i]:
                keep.append(x)
        rep(f"S1+q{q}", keep)
    rep("S4a.gdl (base)", fills(D, tga, allow_long=aL0, allow_short=aS0))
    for q in (0.8,):
        ok = (norm <= 0) | (ratio >= q)
        rep(f"S4a.gdl+q{q}", fills(D, tga, allow_long=aL0 & ok, allow_short=aS0 & ok))
    rep("S5.vf (base)", fills(D, tg5, allow_long=aL0, allow_short=aS0))
    ok = (norm <= 0) | (ratio >= 0.8)
    rep("S5+q0.8", fills(D, tg5, allow_long=aL0 & ok, allow_short=aS0 & ok))

    P("--- Q3 PORTFOLIOS ---")
    sm_ = pd.DataFrame(rows)
    bestS1 = sm_[sm_["name"].str.startswith("S1+q")].sort_values("wk_sharpe").iloc[-1]["name"]
    q1 = float(bestS1.replace("S1+q", ""))
    ok1 = (norm <= 0) | (ratio >= q1)
    s1_thr = [x for x in s1_trades
              if ok1[int(min(np.searchsorted(tarr, np.datetime64(x["et"])), D["n"] - 1))]]
    wt_s1 = week_table(s1_trades, D, lambda x: x["xt"])
    wt_s1t = week_table(s1_thr, D, lambda x: x["xt"])
    for cn, parts in (("S1 + S4n+A0.8", [wt_s1, wt_a08]),
                      (f"S1+q{q1} + S4n+A0.8", [wt_s1t, wt_a08])):
        p = {}
        for src in parts:
            for s, (net, ntr) in src.items():
                a = p.setdefault(s, [0.0, 0]); a[0] += net; a[1] += ntr
        v = np.zeros(n_sess)
        for s, (net, _) in p.items():
            v[s] = net / PV
        rd, rh = summarize(p, D, "dev"), summarize(p, D, "hold")
        sd = float((np.array(rd["_net"]) - STRESS_RT * np.array(rd["_ntr"])).mean())
        P(f"{cn:<26}{100*v.sum()/avail.sum():>7.2f}"
          f"{100*v[big].sum()/avail[big].sum():>8.2f}"
          f"{100*v[~big].sum()/avail[~big].sum():>8.2f}{v[~big].sum():>9,.0f}"
          f"{rd['mean']:>8,.0f}{rd['pos']:>7.1f}{rd['worst']:>9,.0f}{rd['sharpe']:>8.3f}"
          f"{sd:>7,.0f}{rd['tpw']:>7.1f}{rh['sharpe']:>8.3f}{rh['pos']:>7.1f}")
        rows.append(dict(name=cn, capture=round(100 * v.sum() / avail.sum(), 2),
                         big=round(100 * v[big].sum() / avail[big].sum(), 2),
                         small=round(100 * v[~big].sum() / avail[~big].sum(), 2),
                         small_pts=round(v[~big].sum()), wk_mean=round(rd["mean"]),
                         wk_pos=round(rd["pos"], 1), wk_worst=round(rd["worst"]),
                         wk_sharpe=round(rd["sharpe"], 3), stress=round(sd),
                         tpw=round(rd["tpw"], 1), hold_sharpe=round(rh["sharpe"], 3),
                         hold_pos=round(rh["pos"], 1)))
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "summary.csv"), index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
