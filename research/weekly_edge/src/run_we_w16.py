"""WE_W16 SEGSLEEVES (spec preregistered): per-segment sleeves, the short book, S1 throttle."""
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
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "research", "original_trader_reconstruction",
                                "solar_family", "src"))
from solarwave import SolarWaveParams                                    # noqa: E402
import inverse_core as IC                                                # noqa: E402
from run_r13_strict_master import run_master                             # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W16_SEGSLEEVES", "out")
os.makedirs(OUT, exist_ok=True)
SEG = {"ASIA": lambda m: (m >= 1080) | (m <= 179), "EUROPE": lambda m: (m >= 180) & (m <= 509),
       "PREOPEN": lambda m: (m >= 510) & (m <= 569),
       "RTH_AM": lambda m: (m >= 570) & (m <= 749),
       "RTH_PM": lambda m: (m >= 750) & (m <= 959)}


def main():
    t0 = _time.time()
    D = load()
    n_sess, tarr = D["n_sess"], D["t"]
    idx = np.arange(D["n"])
    avail = np.zeros(n_sess)
    for s in range(n_sess):
        m = idx[D["sid"] == s]
        avail[s], _, _, _ = available_move(D["c"], m[0], m[-1] + 1)
    rng_, dmove, atr, norm = intraday_features(D)
    ratio = np.where(norm > 0, rng_ / np.maximum(norm, 1e-9), 1.0)
    ok08 = (norm <= 0) | (ratio >= 0.8)
    ok07 = (norm <= 0) | (ratio >= 0.7)
    mod = ((D["t"] - D["t"].astype("datetime64[D]")).astype("timedelta64[s]")
           .astype(np.int64) // 60)

    def lag_b(a):
        return np.concatenate([[True], a[:-1]])
    _, cd_arr = cd_signals(D)
    dL, dS = lag_b(cd_arr >= 0), lag_b(cd_arr <= 0)
    tgn = sm14_1m(D, 460, return_targets=True, volmults=[6, 8, 10, 12, 14, 16])
    bb = IC.prepare(D["df"], SolarWaveParams())
    s1 = [dict(d=x["d"], pnl=x["pnl"], et=str(bb["t"][x["ei"]]), xt=str(bb["t"][x["xi"]]))
          for x in run_master(bb, exit_strict=False, gate=True, comm=COMM_RT)]
    s4 = fills(D, tgn, allow_long=dL & ok08, allow_short=dS & ok08)
    print(f"bases ready [{_time.time()-t0:.0f}s]", flush=True)

    out = open(os.path.join(OUT, "seg.txt"), "w", encoding="utf-8")

    def P(*a):
        print(*a, flush=True); print(*a, file=out)

    def wt_of(trl):
        return week_table(trl, D, lambda x: x["xt"])

    def wv_of(wt):
        d = {}
        for s, (net, _) in wt.items():
            d[D["wk"][s]] = d.get(D["wk"][s], 0.0) + net
        return d

    def merge(*wts):
        p = {}
        for w in wts:
            for s, (net, ntr) in w.items():
                a = p.setdefault(s, [0.0, 0]); a[0] += net; a[1] += ntr
        return p

    def stats(wt, tag):
        rd = summarize(wt, D, "dev"); rh = summarize(wt, D, "hold")
        st = float((np.array(rd["_net"]) - STRESS_RT * np.array(rd["_ntr"])).mean())
        P(f"{tag:<30}{rd['mean']:>8,.0f}{rd['pos']:>7.1f}{rd['worst']:>10,.0f}"
          f"{rd['sharpe']:>8.3f}{st:>8,.0f}{rd['tpw']:>7.1f}{rh['sharpe']:>8.3f}"
          f"{rh['pos']:>7.1f}")
        return rd, rh, st

    asia = fills(D, tgn, allow_long=dL & ok08 & SEG["ASIA"](mod),
                 allow_short=dS & ok08 & SEG["ASIA"](mod))
    wt1, wt4, wtA = wt_of(s1), wt_of(s4), wt_of(asia)
    P(f"{'object':<30}{'wkMean':>8}{'wkPos':>7}{'wkWorst':>10}{'wkShrp':>8}{'strs':>8}"
      f"{'tpw':>7}{'hShrp':>8}{'hPos':>7}")
    base_port = merge(wt1, wt4, wtA)
    rp, _, _ = stats(base_port, "PORTFOLIO S1+S4n+ASIA (base)")

    # ---------- Q1 segment sleeves ----------
    P("\n=== Q1: per-segment sleeves ===")
    segwt = {}
    for nm, fn in SEG.items():
        m = fn(mod)
        trl = fills(D, tgn, allow_long=dL & ok08 & m, allow_short=dS & ok08 & m)
        segwt[nm] = wt_of(trl)
        stats(segwt[nm], f"  SEG_{nm} (n={len(trl)})")
    ks = list(SEG)
    wvs = {k: wv_of(segwt[k]) for k in ks}
    allw = sorted(set().union(*[set(v) for v in wvs.values()]))
    M = np.array([[wvs[k].get(w, 0.0) for w in allw] for k in ks])
    C = np.corrcoef(M)
    P("\nsegment weekly-net correlations:")
    P("           " + "".join(f"{k:>10}" for k in ks))
    for i, k in enumerate(ks):
        P(f"{k:<11}" + "".join(f"{C[i, j]:>10.2f}" for j in range(len(ks))))
    P(f"max off-diagonal {max(C[i, j] for i in range(len(ks)) for j in range(len(ks)) if i != j):.2f}")
    seg_port = merge(*segwt.values())
    P("")
    rs, _, _ = stats(seg_port, "SEGMENT PORTFOLIO (all 5)")
    r4, _, _ = stats(wt4, "single all-hours S4n (ref)")
    P(f"  falsifier: segment portfolio {'BEATS' if rs['sharpe'] > r4['sharpe'] else 'does NOT beat'}"
      f" the all-hours sleeve ({rs['sharpe']:.3f} vs {r4['sharpe']:.3f})")

    # ---------- Q2 short book ----------
    P("\n=== Q2: long vs short book, full 4.6 years ===")
    P(f"{'sleeve/side':<30}{'n':>7}{'net':>12}{'$/trade':>10}")
    for nm, trl in (("S1", s1), ("S4n", s4), ("ASIA", asia)):
        for side, sg in (("long", 1), ("short", -1)):
            xs = [x for x in trl if x["d"] == sg]
            if xs:
                p = np.array([x["pnl"] for x in xs])
                P(f"{nm+'.'+side:<30}{len(p):>7}{p.sum():>12,.0f}{p.mean():>10.1f}")
    P("")
    P(f"{'variant':<30}{'wkMean':>8}{'wkPos':>7}{'wkWorst':>10}{'wkShrp':>8}{'strs':>8}"
      f"{'tpw':>7}{'hShrp':>8}{'hPos':>7}")
    lo4 = fills(D, tgn, allow_long=dL & ok08, allow_short=np.zeros(D["n"], bool))
    stats(wt_of(lo4), "S4n LONG-ONLY (halves opportunity)")
    # short gated by HTF tilt agreement: 50-session SMA sign, as in the product
    idx2 = np.arange(D["n"])
    sess_close = np.zeros(n_sess)
    for s in range(n_sess):
        sess_close[s] = D["c"][idx2[D["sid"] == s][-1]]
    tilt = np.zeros(n_sess, np.int8)
    for s in range(52, n_sess):
        tilt[s] = int(np.sign(sess_close[s - 1] - sess_close[s - 51:s - 1].mean()))
    tiltbar = tilt[D["sid"]]
    st4 = fills(D, tgn, allow_long=dL & ok08, allow_short=dS & ok08 & (tiltbar <= 0))
    stats(wt_of(st4), "S4n SHORT-gated-by-tilt")

    # ---------- Q3 S1 throttle + portfolio ----------
    P("\n=== Q3: S1 with its own q=0.7 throttle, in the full portfolio ===")
    s1t = [x for x in s1
           if ok07[int(min(np.searchsorted(tarr, np.datetime64(x["et"])), D["n"] - 1))]]
    wt1t = wt_of(s1t)
    stats(wt1t, "S1+q0.7 standalone")
    for tag, wts in (("S1+S4n+ASIA (base)", (wt1, wt4, wtA)),
                     ("S1q07+S4n+ASIA", (wt1t, wt4, wtA)),
                     ("S1q07+S4n+ASIA+shortTilt", (wt1t, wt_of(st4), wtA))):
        stats(merge(*wts), tag)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
