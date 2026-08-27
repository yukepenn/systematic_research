"""WE_W106 - LANE A, the MORN residual.

Spec: runs/WE_W106_MORN/spec.yaml, committed BEFORE this ran.

Five participation/structure mechanisms as DIRECTIONS, decided at 10:01, filled at 10:02, held to
11:29. W104 already measured this exact geometry as NEGATIVE on plain drive (-$59/trade), so any
positive result is attributable to the information and not to the shape.

The rate calibration is OUTCOME-BLIND by construction: thresholds come from trailing causal
quantiles of the FEATURE, and the distribution table is printed BEFORE any economics.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import ROOT                                              # noqa: E402
from we_lanes import LaneBench, RATES                                    # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W106_MORN", "out")
os.makedirs(OUT, exist_ok=True)
DEC, EXIT = 601, 689           # decide 10:01, hold to 11:29
OPEN_A, OPEN_B = 571, 585      # the 09:31-09:45 opening range
MORN_A = 571
SEED = 106


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "morn.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    L = LaneBench()
    NS = L.NS
    P_(f"    substrate {L.n:,} bars / {len(L.sess_in):,} in-window sessions "
       f"[{_time.time()-t0:.0f}s]")

    # ---------------------------------------------------------------- features (no P&L anywhere)
    p_anch = L.at(OPEN_A, use_open=True)
    p_dec = L.at(DEC)
    orh, orl = L.agg(OPEN_A, OPEN_B, "high"), L.agg(OPEN_A, OPEN_B, "low")
    vol_win = L.agg(MORN_A, DEC, "vol")
    absmove = L.agg(MORN_A, DEC, "absmove")
    net = p_dec - p_anch
    drive = np.sign(net)

    # per-bar volume series inside 09:31-10:01, for the decay / effort tests
    m = (L.mod >= MORN_A) & (L.mod <= DEC)
    ii = np.flatnonzero(m)
    df = pd.DataFrame(dict(s=L.sid[ii], mod=L.mod[ii], v=L.v[ii],
                           body=np.abs(L.c[ii] - L.o[ii]), rng=L.h[ii] - L.l[ii],
                           sgn=np.sign(L.c[ii] - L.o[ii]),
                           clv=np.where(L.h[ii] > L.l[ii],
                                        (L.c[ii] - L.l[ii]) / np.maximum(L.h[ii] - L.l[ii], 1e-9),
                                        0.5)))
    decay_run = np.zeros(NS); decay_dir = np.zeros(NS)
    enr_score = np.zeros(NS); enr_dir = np.zeros(NS)
    for s, g in df.groupby("s"):
        if s >= NS or len(g) < 6:
            continue
        vv = g["v"].to_numpy(); sg = g["sgn"].to_numpy()
        bd = g["body"].to_numpy(); rg = g["rng"].to_numpy(); cl = g["clv"].to_numpy()
        # VOL_DECAY: longest tail run of same-sign bars with strictly falling volume
        k = 0
        for i in range(len(vv) - 1, 0, -1):
            if sg[i] != 0 and sg[i] == sg[i - 1] and vv[i] < vv[i - 1]:
                k += 1
            else:
                break
        decay_run[s] = k
        decay_dir[s] = -sg[-1] if k >= 2 else 0.0            # exhaustion -> FADE the run
        # EFFORT_NO_RESULT: max volume, non-max body, non-max range, close near the bar mid
        j = int(np.argmax(vv))
        if vv[j] > 0:
            eff = (1.0 - bd[j] / max(bd.max(), 1e-9)) + (1.0 - rg[j] / max(rg.max(), 1e-9)) \
                  + (1.0 - abs(cl[j] - 0.5) * 2.0)
            enr_score[s] = eff * (vv[j] / max(np.median(vv), 1e-9))
            enr_dir[s] = -sg[j] if sg[j] != 0 else 0.0       # absorption -> FADE the effort
    disp_per_vol = np.abs(net) / np.maximum(vol_win, 1e-9)
    vol_z = vol_win.copy()
    # OPEN_ACCEPT: closes beyond the opening range over the last 15 bars before the decision
    acc = np.zeros(NS)
    m2 = (L.mod > OPEN_B) & (L.mod <= DEC)
    i2 = np.flatnonzero(m2)
    above = (L.c[i2] > orh[L.sid[i2]]).astype(float)
    below = (L.c[i2] < orl[L.sid[i2]]).astype(float)
    na = np.zeros(NS); nb = np.zeros(NS); nt = np.zeros(NS)
    np.add.at(na, L.sid[i2], above); np.add.at(nb, L.sid[i2], below)
    np.add.at(nt, L.sid[i2], 1.0)
    acc_frac = (na - nb) / np.maximum(nt, 1)
    acc_dir = np.sign(acc_frac)
    acc_score = np.abs(acc_frac)

    MECH = {
        "VOL_DECAY":     (decay_run.astype(float), decay_dir),
        "EFFORT_NO_RES": (enr_score, enr_dir),
        "DISP_PER_VOL":  (disp_per_vol, drive),          # cheap movement -> CONTINUE
        "VOL_SURPRISE":  (vol_z, drive),                 # high participation -> CONTINUE
        "OPEN_ACCEPT":   (acc_score, acc_dir),
    }

    # ---------------------------------------------------------------- STEP 1: outcome-blind
    P_("")
    P_("=" * 122)
    P_("=== STEP 1 - FEATURE DISTRIBUTIONS ONLY. No P&L has been computed at this point.")
    P_("=" * 122)
    P_(f"{'mechanism':<16}{'defined':>9}{'nonzero dir':>13}{'p25':>11}{'p50':>11}{'p75':>11}"
       f"{'p90':>11}{'long/short of dir':>20}")
    for k, (sc, di) in MECH.items():
        d = L.win & np.isfinite(sc)
        nz = d & (di != 0)
        P_(f"{k:<16}{int(d.sum()):>9}{int(nz.sum()):>13}"
           f"{np.nanpercentile(sc[d], 25):>11.4f}{np.nanpercentile(sc[d], 50):>11.4f}"
           f"{np.nanpercentile(sc[d], 75):>11.4f}{np.nanpercentile(sc[d], 90):>11.4f}"
           f"{f'{int((di[nz]>0).sum())} / {int((di[nz]<0).sum())}':>20}")
    P_("")
    P_("    Thresholds are now FROZEN as trailing causal quantiles at 25/50/75 % acceptance.")
    P_("    Only after this line is any economics computed.")

    # ---------------------------------------------------------------- STEP 2: economics
    P_("")
    P_("=" * 122)
    P_("=== STEP 2 - ECONOMICS. Decide 10:01, fill 10:02, hold to 11:29, size 1, no stop.")
    P_("=" * 122)
    pe_probe = L.at(DEC + 1, use_open=True)
    px_probe = L.at(EXIT)
    elig = L.win & np.isfinite(pe_probe) & np.isfinite(px_probe)
    P_(f"    eligible sessions {int(elig.sum())}")
    P_("")
    P_(f"{'mechanism':<16}{'rate':>7}{'N':>6}{'accept%':>9}{'hit%':>8}{'p*':>8}{'vs p*':>8}"
       f"{'$/trade':>10}{'net $':>11}{'wk$@fixDD':>11}{'t':>6}")
    rows = []
    cells = []
    prim_cells = []
    rng = np.random.default_rng(SEED)
    for k, (sc, di) in MECH.items():
        for r in RATES:
            ok = LaneBench.accept(sc, r)
            des = np.where(ok & (di != 0), di, 0).astype(np.int8)
            pnl, take, cost, emove = L.trade(des, DEC, EXIT)
            st = L.stats(pnl, take, cost, emove)
            if st is None:
                P_(f"{k:<16}{r:>7.2f}   too few"); continue
            P_(f"{k:<16}{r:>7.2f}{st['n']:>6}{100*take.sum()/max(elig.sum(),1):>8.1f}%"
               f"{st['hit']:>7.2f}%{st['p_star']:>8.4f}{100*(st['hit']/100-st['p_star']):>8.2f}"
               f"{st['per_trade']:>10,.0f}{st['net']:>11,.0f}{st['fixdd']:>11,.0f}{st['t']:>6.2f}")
            rows.append(dict(mech=k, rate=r, **st))
            mv = ((L.at(EXIT) - L.at(DEC + 1, use_open=True)) * 20.0)[take]
            cells.append((mv, cost))
            if abs(r - 0.50) < 1e-9:
                prim_cells.append((mv, cost))
        P_("")
    DF = pd.DataFrame(rows)
    DF.to_csv(os.path.join(OUT, "cells.csv"), index=False)

    # ---------------------------------------------------------------- the primary
    prim = float(DF[np.isclose(DF["rate"], 0.50)]["per_trade"].mean())
    mn, _ = LaneBench.coin_null(prim_cells, rng)
    _, mx = LaneBench.coin_null(cells, rng)
    p95m, p95x = float(np.nanpercentile(mn, 95)), float(np.nanpercentile(mx, 95))
    P_("=" * 122)
    P_("=== THE PRIMARY: equal-weight mean of $/trade across the five mechanisms at the 50 % arm")
    P_("=" * 122)
    P_(f"    real ${prim:,.0f}/trade")
    P_(f"    coin null on the same statistic: mean ${np.nanmean(mn):,.0f} "
       f"sd ${np.nanstd(mn, ddof=1):,.0f}  p95 ${p95m:,.0f}"
       f"   -> {100*float(np.nanmean(mn < prim)):.1f}th percentile")
    P_(f"    VERDICT: {'PASSES' if prim > p95m else 'FAILS'}")
    P_("")
    P_(f"    best-of-{len(cells)} coin null for reading individual cells: p95 ${p95x:,.0f}")
    P_(f"{'mechanism':<16}{'rate':>7}{'$/trade':>10}{'own p* cleared':>17}{'beats best-of-K':>18}")
    for _, r_ in DF.sort_values("per_trade", ascending=False).head(8).iterrows():
        P_(f"{r_['mech']:<16}{r_['rate']:>7.2f}{r_['per_trade']:>10,.0f}"
           f"{('YES' if r_['hit']/100 > r_['p_star'] else 'no'):>17}"
           f"{('YES' if r_['per_trade'] > p95x else 'no'):>18}")

    # ---------------------------------------------------------------- class split
    P_("")
    P_("=" * 122)
    P_("=== BY SESSION CLASS, 50 % arm ($/trade, n)")
    P_("=" * 122)
    P_(f"{'mechanism':<16}" + "".join(f"{k:>17}" for k in
                                      ("TREND-UP", "TREND-DOWN", "REVERSAL", "RANGE", "MIXED")))
    for k, (sc, di) in MECH.items():
        ok = LaneBench.accept(sc, 0.50)
        des = np.where(ok & (di != 0), di, 0).astype(np.int8)
        pnl, take, _, _ = L.trade(des, DEC, EXIT)
        bc = L.by_class(pnl, take)
        P_(f"{k:<16}" + "".join(f"{bc[c][0]:>6} {bc[c][1]:>10,.0f}" for c in
                                ("TREND-UP", "TREND-DOWN", "REVERSAL", "RANGE", "MIXED")))
    P_(f"\n[done {_time.time()-t0:.0f}s]")
    out.close()


if __name__ == "__main__":
    main()
