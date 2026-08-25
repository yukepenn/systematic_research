"""WE_W09 SMALLDAY (spec preregistered): intraday-observed throttles vs the small-day bleed.

Never predicts the regime — every throttle reads state that is already realized at bar i-1.
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

OUT = os.path.join(ROOT, "runs", "WE_W09_SMALLDAY", "out")
os.makedirs(OUT, exist_ok=True)


def intraday_features(D):
    """Causal per-bar session state: realized range so far (through i-1), |c-open| through
    i-1, ATR14 at i-1, and the trailing-60-session median range at the same time-of-day."""
    n, sid, n_sess = D["n"], D["sid"], D["n_sess"]
    t, o, h, l, c = D["t"], D["o"], D["h"], D["l"], D["c"]
    hm = ((t - t.astype("datetime64[D]")).astype("timedelta64[s]").astype(np.int64) // 60)
    idx = np.arange(n)
    rng = np.zeros(n)          # realized range through i-1 within the session
    dmove = np.zeros(n)        # |c[i-1] - session open|
    sess_of_bar = sid
    for s in range(n_sess):
        m = idx[sid == s]
        hh = np.maximum.accumulate(h[m])
        ll = np.minimum.accumulate(l[m])
        r = hh - ll
        rng[m] = np.concatenate([[0.0], r[:-1]])
        op = o[m[0]]
        dm = np.abs(c[m] - op)
        dmove[m] = np.concatenate([[0.0], dm[:-1]])
    tr = np.maximum(h - l, np.maximum(np.abs(h - np.roll(c, 1)), np.abs(l - np.roll(c, 1))))
    tr[0] = h[0] - l[0]
    atr = pd.Series(tr).rolling(14, min_periods=1).mean().values
    atr = np.concatenate([[atr[0]], atr[:-1]])
    # time-of-day norm: median of rng at the same minute-of-day over the trailing 60 sessions
    tod = hm
    norm = np.zeros(n)
    hist = {}                                  # tod -> list of (session, value)
    for s in range(n_sess):
        m = idx[sid == s]
        for i in m:
            lst = hist.get(tod[i])
            if lst and len(lst) >= 20:
                norm[i] = float(np.median(lst[-60:]))
        for i in m:                            # append AFTER the session is used (causal)
            hist.setdefault(tod[i], []).append(rng[i])
            if len(hist[tod[i]]) > 200:
                hist[tod[i]].pop(0)
    return rng, dmove, atr, norm


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
    print(f"features ready [{_time.time()-t0:.0f}s]", flush=True)

    def lag_b(a):
        return np.concatenate([[True], a[:-1]])
    _, cd_arr = cd_signals(D)
    aL0, aS0 = lag_b(cd_arr >= 0), lag_b(cd_arr <= 0)
    tgn = sm14_1m(D, 460, return_targets=True, volmults=[6, 8, 10, 12, 14, 16])

    out = open(os.path.join(OUT, "smallday.txt"), "w", encoding="utf-8")

    def P(*a):
        print(*a, flush=True); print(*a, file=out)

    def evaluate(nm, aL, aS, halt=None):
        trl = fills(D, tgn, halt=halt, allow_long=aL, allow_short=aS)
        v = np.zeros(n_sess)
        for x in trl:
            i = int(min(np.searchsorted(tarr, np.datetime64(x["et"])), D["n"] - 1))
            v[int(D["sid"][i])] += x["pnl"] / PV
        b = 100 * v[big].sum() / avail[big].sum()
        s_ = 100 * v[~big].sum() / avail[~big].sum()
        sm_ = session_metrics(D, trl, avail, adir, tarr)
        wt = week_table(trl, D, lambda x: x["xt"])
        r = summarize(wt, D, "dev")
        rh = summarize(wt, D, "hold")
        stress = float((np.array(r["_net"]) - STRESS_RT * np.array(r["_ntr"])).mean())
        P(f"{nm:<20}{100*v.sum()/avail.sum():>7.2f}{b:>8.2f}{s_:>8.2f}{v[~big].sum():>9,.0f}"
          f"{sm_['RIGHT']:>7}{r['mean']:>8,.0f}{r['pos']:>7.1f}{r['worst']:>9,.0f}"
          f"{r['sharpe']:>8.3f}{stress:>7,.0f}{r['tpw']:>7.1f}{rh['sharpe']:>8.3f}")
        return dict(name=nm, capture=round(100 * v.sum() / avail.sum(), 2),
                    big=round(b, 2), small=round(s_, 2), small_pts=round(v[~big].sum()),
                    RIGHT=sm_["RIGHT"], wk_mean=round(r["mean"]), wk_pos=round(r["pos"], 1),
                    wk_worst=round(r["worst"]), wk_sharpe=round(r["sharpe"], 3),
                    stress=round(stress), tpw=round(r["tpw"], 1),
                    hold_sharpe=round(rh["sharpe"], 3))

    P(f"{'variant':<20}{'CAPT%':>7}{'bigCAP':>8}{'smlCAP':>8}{'smlPts':>9}{'RIGHT':>7}"
      f"{'wkMean':>8}{'wkPos':>7}{'wkWorst':>9}{'wkShrp':>8}{'strs':>7}{'tpw':>7}{'hShrp':>8}")
    rows = [evaluate("BASE", aL0, aS0)]
    base = rows[0]

    ratio = np.where(norm > 0, rng / np.maximum(norm, 1e-9), 1.0)
    for q in (0.6, 0.8, 1.0):
        ok = (norm <= 0) | (ratio >= q)
        rows.append(evaluate(f"A_range{q}", aL0 & ok, aS0 & ok))
    for lim in (1300, 2600):
        rows.append(evaluate(f"B_pnl{lim}", aL0, aS0, halt=lim))
    for m in (0.5, 1.0):
        ok = dmove >= m * atr
        rows.append(evaluate(f"C_move{m}", aL0 & ok, aS0 & ok))

    sm = pd.DataFrame(rows)
    # D_COMBO by the preregistered rule: best A by small-day points, best B by small-day points
    bestA = sm[sm["name"].str.startswith("A_")].sort_values("small_pts").iloc[-1]["name"]
    bestB = sm[sm["name"].str.startswith("B_")].sort_values("small_pts").iloc[-1]["name"]
    q = float(bestA.replace("A_range", "")); lim = int(bestB.replace("B_pnl", ""))
    ok = (norm <= 0) | (ratio >= q)
    rows.append(evaluate(f"D_combo({bestA}+{bestB})", aL0 & ok, aS0 & ok, halt=lim))
    sm = pd.DataFrame(rows)
    sm.to_csv(os.path.join(OUT, "summary.csv"), index=False)

    qual = sm[(sm["small_pts"] > base["small_pts"]) & (sm["big"] >= 16.0)
              & (sm["wk_sharpe"] >= 0.193) & (sm["stress"] > 0) & (sm["name"] != "BASE")]
    P(f"\nQUALIFYING (small_pts>base AND big>=16.0 AND wkSharpe>=0.193 AND stress>0): "
      f"{len(qual)}")
    if len(qual):
        P(qual.to_string(index=False))
    else:
        P("F1 FIRED: no throttle separates the small-day bleed from the big-day edge.")
        P("\nclosest attempts (by small-day points):")
        P(sm.sort_values("small_pts", ascending=False).head(6).to_string(index=False))
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
