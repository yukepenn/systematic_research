"""WE_W108 - LANE C, REVERSAL / RANGE.

Spec: runs/WE_W108_REVRANGE/spec.yaml, committed BEFORE this ran.

Six mechanisms, decided 11:48, filled 11:49, held to 15:44. What is NEW versus the seven fades this
campaign already killed is a PARTICIPATION term and a PATH-EFFICIENCY term - every dead fade used
price structure alone. Outcome-blind rate calibration; results split by session class, because a
mechanism positive overall but negative on REVERSAL and RANGE has falsified its own claim.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import ROOT, PV                                          # noqa: E402
from we_lanes import LaneBench, RATES                                    # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W108_REVRANGE", "out")
os.makedirs(OUT, exist_ok=True)
MORN_A, MORN_B = 571, 689
DEC, EXIT = 708, 944            # decide 11:48, hold to 15:44
SEED = 108


def trail_med(x):
    return pd.Series(x).rolling(250, min_periods=60).median().shift(1).to_numpy()


def trail_mean(x):
    return pd.Series(x).rolling(250, min_periods=60).mean().shift(1).to_numpy()


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "revrange.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    L = LaneBench()
    NS = L.NS
    P_(f"    substrate {L.n:,} bars / {len(L.sess_in):,} in-window sessions "
       f"[{_time.time()-t0:.0f}s]")

    p0931 = L.at(MORN_A, use_open=True)
    p_dec = L.at(DEC)
    mh, ml = L.agg(MORN_A, MORN_B, "high"), L.agg(MORN_A, MORN_B, "low")
    mmid = (mh + ml) / 2.0
    absm = L.agg(MORN_A, MORN_B, "absmove")
    mvol = L.agg(MORN_A, MORN_B, "vol")
    morn_net = L.at(MORN_B) - p0931
    morn_dir = np.sign(morn_net)
    peff = np.abs(morn_net) / np.maximum(absm, 1e-9)

    rth = L.mod >= 571
    pv = np.where(rth, L.c * L.v, 0.0)
    vv = np.where(rth, L.v, 0.0)
    cpv = pd.Series(pv).groupby(L.sid).cumsum().to_numpy()
    cvv = pd.Series(vv).groupby(L.sid).cumsum().to_numpy()
    vwap = np.where(cvv > 0, cpv / np.maximum(cvv, 1e-9), L.c)
    vw_dec = L.at(DEC, arr=vwap)

    m2 = (L.mod > MORN_B) & (L.mod <= DEC)
    i2 = np.flatnonzero(m2)
    s2 = L.sid[i2]
    out_hi = np.zeros(NS); out_lo = np.zeros(NS); nbar = np.zeros(NS); above_vw = np.zeros(NS)
    np.add.at(out_hi, s2, (L.c[i2] > mh[s2]).astype(float))
    np.add.at(out_lo, s2, (L.c[i2] < ml[s2]).astype(float))
    np.add.at(nbar, s2, 1.0)
    np.add.at(above_vw, s2, (L.c[i2] > vwap[i2]).astype(float))
    vw_frac = above_vw / np.maximum(nbar, 1)
    inside = (p_dec <= mh) & (p_dec >= ml)

    mi = (L.mod >= MORN_A) & (L.mod <= MORN_B)
    ii = np.flatnonzero(mi)
    dfe = pd.DataFrame(dict(s=L.sid[ii], v=L.v[ii], h=L.h[ii], l=L.l[ii]))
    exz = np.zeros(NS); latevol = np.zeros(NS)
    for s, g in dfe.groupby("s"):
        if s >= NS or len(g) < 20:
            continue
        v_ = g["v"].to_numpy()
        md = float(np.median(v_)) or 1.0
        j = int(np.argmax(g["h"].to_numpy())) if morn_dir[s] > 0 else int(np.argmin(g["l"].to_numpy()))
        exz[s] = v_[j] / md
        latevol[s] = float(np.mean(v_[-10:])) / md if len(v_) >= 10 else 1.0

    MECH = {
        "VALUE_REACCEPT": (np.where(inside & ((out_hi + out_lo) > 0),
                                    (out_hi + out_lo) / np.maximum(nbar, 1), 0.0),
                           np.sign(mmid - p_dec)),
        "FAILED_BREAK":   (np.where(inside, (out_hi + out_lo) / np.maximum(nbar, 1), 0.0),
                           np.where(out_hi > out_lo, -1.0,
                                    np.where(out_lo > out_hi, 1.0, 0.0))),
        "EXHAUST_VOL":    (exz / np.maximum(latevol, 1e-9), -morn_dir),
        "EFFORT_NO_RES":  (mvol / np.maximum(trail_med(mvol), 1e-9) * (1.0 - peff), -morn_dir),
        "VWAP_RECLAIM":   (np.abs(vw_frac - 0.5) * 2.0, np.sign(p_dec - vw_dec)),
        "PATH_EFF_TRANS": ((1.0 - peff) * ((mh - ml) / np.maximum(trail_mean(mh - ml), 1e-9)),
                           np.sign(mmid - p_dec)),
    }

    P_("")
    P_("=" * 122)
    P_("=== STEP 1 - FEATURE DISTRIBUTIONS ONLY. No P&L has been computed at this point.")
    P_("=" * 122)
    P_(f"{'mechanism':<17}{'defined':>9}{'nonzero dir':>13}{'p25':>11}{'p50':>11}{'p75':>11}"
       f"{'long/short':>14}")
    for k, (sc, di) in MECH.items():
        d = L.win & np.isfinite(sc)
        nz = d & (np.nan_to_num(di) != 0)
        P_(f"{k:<17}{int(d.sum()):>9}{int(nz.sum()):>13}"
           f"{np.nanpercentile(sc[d], 25):>11.4f}{np.nanpercentile(sc[d], 50):>11.4f}"
           f"{np.nanpercentile(sc[d], 75):>11.4f}"
           f"{f'{int((di[nz] > 0).sum())} / {int((di[nz] < 0).sum())}':>14}")
    P_("")
    P_("    Thresholds now FROZEN as trailing causal quantiles. Economics follows.")

    P_("")
    P_("=" * 122)
    P_("=== STEP 2 - ECONOMICS. Decide 11:48, fill 11:49, hold 15:44, size 1, no stop.")
    P_("=" * 122)
    P_(f"{'mechanism':<17}{'rate':>6}{'N':>6}{'hit%':>8}{'p*':>8}{'vs p*':>7}{'$/trade':>10}"
       f"{'net $':>11}{'wk$@fixDD':>11}{'t':>6}")
    rows, cells, prim = [], [], []
    rng = np.random.default_rng(SEED)
    for k, (sc, di) in MECH.items():
        for r in RATES:
            ok = LaneBench.accept(sc, r)
            des = np.nan_to_num(np.where(ok, di, 0)).astype(np.int8)
            pnl, take, cost, em = L.trade(des, DEC, EXIT)
            st = L.stats(pnl, take, cost, em)
            if st is None:
                P_(f"{k:<17}{r:>6.2f}   too few"); continue
            P_(f"{k:<17}{r:>6.2f}{st['n']:>6}{st['hit']:>7.2f}%{st['p_star']:>8.4f}"
               f"{100*(st['hit']/100-st['p_star']):>7.2f}{st['per_trade']:>10,.0f}"
               f"{st['net']:>11,.0f}{st['fixdd']:>11,.0f}{st['t']:>6.2f}")
            rows.append(dict(mech=k, rate=r, **st))
            mv = ((L.at(EXIT) - L.at(DEC + 1, use_open=True)) * PV)[take]
            cells.append((mv, cost))
            if abs(r - 0.50) < 1e-9:
                prim.append((mv, cost))
        P_("")
    DF = pd.DataFrame(rows)
    DF.to_csv(os.path.join(OUT, "cells.csv"), index=False)

    P_("    CONTROLS - what an unconditional trade earns at this exact geometry:")
    for lab, d_ in (("always LONG", 1), ("always SHORT", -1)):
        pnl, take, cost, em = L.trade(np.where(L.win, d_, 0).astype(np.int8), DEC, EXIT)
        st = L.stats(pnl, take, cost, em)
        P_(f"{'CONTROL ' + lab:<17}{'':>6}{st['n']:>6}{st['hit']:>7.2f}%{st['p_star']:>8.4f}"
           f"{100*(st['hit']/100-st['p_star']):>7.2f}{st['per_trade']:>10,.0f}"
           f"{st['net']:>11,.0f}{st['fixdd']:>11,.0f}{st['t']:>6.2f}")

    pv_ = float(DF[np.isclose(DF["rate"], 0.50)]["per_trade"].mean())
    mn, _ = LaneBench.coin_null(prim, rng)
    _, mx = LaneBench.coin_null(cells, rng)
    p95m, p95x = float(np.nanpercentile(mn, 95)), float(np.nanpercentile(mx, 95))
    P_("")
    P_("=" * 122)
    P_("=== THE PRIMARY: equal-weight mean of $/trade across the six mechanisms at the 50 % arm")
    P_("=" * 122)
    P_(f"    real ${pv_:,.0f}/trade   coin null mean ${np.nanmean(mn):,.0f} p95 ${p95m:,.0f}"
       f"  -> {100*float(np.nanmean(mn < pv_)):.1f}th percentile")
    P_(f"    VERDICT: {'PASSES' if pv_ > p95m else 'FAILS'}"
       f"     best-of-{len(cells)} bar for individual cells ${p95x:,.0f}")
    P_("")
    P_(f"{'mechanism':<17}{'rate':>6}{'$/trade':>10}{'own p* cleared':>17}{'beats best-of-K':>18}")
    for _, r_ in DF.sort_values("per_trade", ascending=False).head(6).iterrows():
        P_(f"{r_['mech']:<17}{r_['rate']:>6.2f}{r_['per_trade']:>10,.0f}"
           f"{('YES' if r_['hit']/100 > r_['p_star'] else 'no'):>17}"
           f"{('YES' if r_['per_trade'] > p95x else 'no'):>18}")

    P_("")
    P_("=" * 122)
    P_("=== BY SESSION CLASS at the 50 % arm. A mechanism positive OVERALL but negative on")
    P_("===   REVERSAL and RANGE has FALSIFIED its own stated mechanism.")
    P_("=" * 122)
    P_(f"{'mechanism':<17}" + "".join(f"{k:>17}" for k in
                                      ("TREND-UP", "TREND-DOWN", "REVERSAL", "RANGE", "MIXED")))
    for k, (sc, di) in MECH.items():
        ok = LaneBench.accept(sc, 0.50)
        des = np.nan_to_num(np.where(ok, di, 0)).astype(np.int8)
        pnl, take, _, _ = L.trade(des, DEC, EXIT)
        bc = L.by_class(pnl, take)
        P_(f"{k:<17}" + "".join(f"{bc[c][0]:>6} {bc[c][1]:>10,.0f}" for c in
                                ("TREND-UP", "TREND-DOWN", "REVERSAL", "RANGE", "MIXED")))
    P_(f"\n[done {_time.time()-t0:.0f}s]")
    out.close()


if __name__ == "__main__":
    main()
