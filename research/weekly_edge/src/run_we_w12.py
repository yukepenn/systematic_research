"""WE_W12 ARCH (spec preregistered): per-member sleeves vs averaged ensemble; unused Solar types."""
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
from run_we_w09 import intraday_features                                 # noqa: E402
from run_we_w11 import seg_of                                            # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "research", "original_trader_reconstruction",
                                "solar_family", "src"))
from solarwave import SolarWaveParams, solar_wave_full                   # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W12_ARCH", "out")
os.makedirs(OUT, exist_ok=True)


def main():
    t0 = _time.time()
    D = load()
    n_sess, tarr = D["n_sess"], D["t"]
    idx = np.arange(D["n"])
    avail = np.zeros(n_sess)
    for s in range(n_sess):
        m = idx[D["sid"] == s]
        avail[s], _, _, _ = available_move(D["c"], m[0], m[-1] + 1)
    big = avail >= 500
    rng, dmove, atr, norm = intraday_features(D)
    ratio = np.where(norm > 0, rng / np.maximum(norm, 1e-9), 1.0)
    ok08 = (norm <= 0) | (ratio >= 0.8)
    mod = ((D["t"] - D["t"].astype("datetime64[D]")).astype("timedelta64[s]")
           .astype(np.int64) // 60)
    not_close = seg_of(mod) != "CLOSE"

    def lag_b(a):
        return np.concatenate([[True], a[:-1]])
    _, cd_arr = cd_signals(D)
    aL = lag_b(cd_arr >= 0) & ok08 & not_close
    aS = lag_b(cd_arr <= 0) & ok08 & not_close
    print(f"features ready [{_time.time()-t0:.0f}s]", flush=True)

    out = open(os.path.join(OUT, "arch.txt"), "w", encoding="utf-8")

    def P(*a):
        print(*a, flush=True); print(*a, file=out)

    rows = []

    def rep(nm, trl, k=1):
        v = np.zeros(n_sess)
        for x in trl:
            i = int(min(np.searchsorted(tarr, np.datetime64(x["et"])), D["n"] - 1))
            v[int(D["sid"][i])] += x["pnl"] / PV
        wt = week_table(trl, D, lambda x: x["xt"])
        wtn = {s: [net / k, ntr] for s, (net, ntr) in wt.items()}
        r = summarize(wtn, D, "dev"); rh = summarize(wtn, D, "hold")
        st = float((np.array(r["_net"]) - STRESS_RT * np.array(r["_ntr"]) / k).mean())
        bcap = 100 * v[big].sum() / avail[big].sum() / k
        P(f"{nm:<28}{k:>3}{len(trl):>8}{100*v.sum()/avail.sum()/k:>8.2f}{bcap:>8.2f}"
          f"{r['mean']:>9,.0f}{r['pos']:>7.1f}{r['worst']:>10,.0f}{r['sharpe']:>8.3f}"
          f"{st:>8,.0f}{rh['sharpe']:>8.3f}")
        rows.append(dict(name=nm, k=k, n=len(trl),
                         capture=round(100 * v.sum() / avail.sum() / k, 2),
                         big=round(bcap, 2), wk_mean=round(r["mean"]),
                         wk_pos=round(r["pos"], 1), wk_worst=round(r["worst"]),
                         wk_sharpe=round(r["sharpe"], 3), stress=round(st),
                         hold_sharpe=round(rh["sharpe"], 3)))
        return wt

    P(f"{'variant':<28}{'k':>3}{'n':>8}{'CAPT%':>8}{'bigCAP':>8}{'wkMean':>9}{'wkPos':>7}"
      f"{'wkWorst':>10}{'wkShrp':>8}{'strs':>8}{'hShrp':>8}")
    P("(CAPT/bigCAP/wkMean/worst are EXPOSURE-NORMALISED: divided by k)")
    tgn = sm14_1m(D, 460, return_targets=True, volmults=[6, 8, 10, 12, 14, 16])
    base_wt = rep("BASE ensemble narrow6", fills(D, tgn, allow_long=aL, allow_short=aS))
    base = rows[-1]

    P("--- Q1: per-member sleeves, positions summed ---")
    memtg = {}
    for m in (6, 10, 14, 18, 22, 26, 30):
        memtg[m] = sm14_1m(D, 460, return_targets=True, volmults=[m])
        print(f"   member {m} targets [{_time.time()-t0:.0f}s]", flush=True)
    for tag, ms in (("k3", [6, 14, 22]), ("k5", [6, 10, 14, 22, 30]),
                    ("k7", [6, 10, 14, 18, 22, 26, 30])):
        allt = []
        for m in ms:
            allt += fills(D, memtg[m], allow_long=aL, allow_short=aS)
        rep(f"A1_members_{tag}", allt, k=len(ms))

    P("--- Q2: unused Solar signal types (on the raw 1-min Solar model) ---")
    sw = solar_wave_full(D["o"], D["h"], D["l"], D["c"], SolarWaveParams())
    st_, tr_, wv_ = sw.signal_trend, sw.signal_trade, sw.signal_wave

    def lag_i(a):
        return np.concatenate([[0], a[:-1]])
    st_l, wv_l = lag_i(st_), lag_i(wv_)
    # A2 strong-only: keep the ensemble but require |signal_trend|==2 agreeing in direction
    strongL = (st_l == 2) | (st_l == 0)
    strongS = (st_l == -2) | (st_l == 0)
    rep("A2_strong_only", fills(D, tgn, allow_long=aL & strongL, allow_short=aS & strongS))
    # A3 strengthen: T3 pulses as an extra entry trigger, merged into the target array
    tg3 = tgn.copy()
    t3 = np.where(np.abs(tr_) == 3, np.sign(tr_), 0).astype(np.int8)
    add = (tg3 == 0) & (t3 != 0)
    tg3[add] = t3[add]
    rep("A3_plus_strengthen", fills(D, tg3, allow_long=aL, allow_short=aS))
    # A4 wave agreement gate
    wL, wS = (wv_l >= 0), (wv_l <= 0)
    rep("A4_wave_gate", fills(D, tgn, allow_long=aL & wL, allow_short=aS & wS))

    sm = pd.DataFrame(rows)
    sm.to_csv(os.path.join(OUT, "summary.csv"), index=False)
    qual = sm[(sm["wk_sharpe"] > base["wk_sharpe"]) & (sm["stress"] > 0)
              & (sm["big"] >= 0.9 * base["big"]) & (sm["name"] != base["name"])]
    P(f"\nQUALIFYING (exposure-normalised Sharpe > {base['wk_sharpe']}, stress>0, "
      f"big>=90% of base): {len(qual)}")
    P(qual.to_string(index=False) if len(qual) else
      "NONE -> FA/FB fire for the axes that produced nothing.")
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
