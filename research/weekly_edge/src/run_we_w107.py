"""WE_W107 - LANE B, AFT. DIAGNOSTICS FIRST.

Spec: runs/WE_W107_AFT/spec.yaml, committed BEFORE this ran.

Stage 1 asks one question with no trade simulated: does ANY causal state known at 13:29 separate
the sign or size of the 13:30 -> 15:44 move? The survivor rule was fixed in the spec BEFORE the
table was produced - top-vs-bottom quintile sign-rate spread >= 8 pp AND monotone or single-peaked.

Stage 2 runs only on survivors. Stage 1 may legitimately end the wave.
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

OUT = os.path.join(ROOT, "runs", "WE_W107_AFT", "out")
os.makedirs(OUT, exist_ok=True)
MORN_A, MORN_B = 571, 689       # 09:31 - 11:29
MID_A, MID_B = 690, 809         # 11:30 - 13:29
DEC, EXIT = 830, 944            # decide 13:50, hold to 15:44
SPREAD_BAR = 8.0                # percentage points, fixed in the spec
SEED = 107


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "aft.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    L = LaneBench()
    NS = L.NS
    P_(f"    substrate {L.n:,} bars / {len(L.sess_in):,} in-window sessions "
       f"[{_time.time()-t0:.0f}s]")

    p0931 = L.at(MORN_A, use_open=True)
    p1129 = L.at(MORN_B)
    p1130 = L.at(MID_A, use_open=True)
    p1329 = L.at(MID_B)
    p1330 = L.at(810, use_open=True)
    p1544 = L.at(EXIT)
    mh, ml = L.agg(MORN_A, MORN_B, "high"), L.agg(MORN_A, MORN_B, "low")
    dh, dl = L.agg(MID_A, MID_B, "high"), L.agg(MID_A, MID_B, "low")
    orh, orl = L.agg(571, 585, "high"), L.agg(571, 585, "low")
    mv_ = L.agg(MORN_A, MORN_B, "vol")
    dv_ = L.agg(MID_A, MID_B, "vol")
    absm = L.agg(MORN_A, MID_B, "absmove")

    # session VWAP at 13:29, RTH-anchored
    rth = L.mod >= 571
    pv = np.where(rth, L.c * L.v, 0.0); vv = np.where(rth, L.v, 0.0)
    cpv = pd.Series(pv).groupby(L.sid).cumsum().to_numpy()
    cvv = pd.Series(vv).groupby(L.sid).cumsum().to_numpy()
    vwap = np.where(cvv > 0, cpv / np.maximum(cvv, 1e-9), L.c)
    vw1329 = L.at(MID_B, arr=vwap)
    sig = pd.Series(np.abs(p1329 - p0931)).rolling(60, min_periods=20).mean().shift(1).to_numpy()

    STATE = {
        "MORNING_DIR":   np.sign(p1129 - p0931),
        "MIDDAY_DIR":    np.sign(p1329 - p1130),
        "MID_RANGE_POS": (p1329 - dl) / np.maximum(dh - dl, 1e-9),
        "COMPRESSION":   (dh - dl) / np.maximum(mh - ml, 1e-9),
        "VWAP_SIDE":     np.sign(p1329 - vw1329),
        "VWAP_DIST":     (p1329 - vw1329) / np.maximum(sig, 1e-9),
        "PATH_EFF":      np.abs(p1329 - p0931) / np.maximum(absm, 1e-9),
        "VOL_REACCEL":   dv_ / np.maximum(mv_, 1e-9),
        "OPEN_RANGE_ST": np.where(p1329 > orh, 1.0, np.where(p1329 < orl, -1.0, 0.0)),
    }
    target = (p1544 - p1330) * PV
    elig = L.win & np.isfinite(target) & np.isfinite(p1329) & np.isfinite(p0931)
    P_(f"    eligible sessions for the diagnostic: {int(elig.sum())}")

    # ---------------------------------------------------------------- STAGE 1
    P_("")
    P_("=" * 122)
    P_("=== STAGE 1 - DIAGNOSTIC ONLY. Conditional mean and sign-rate of the 13:30 -> 15:44 move")
    P_("===   by QUINTILE of each causal state known at 13:29. NO TRADE IS SIMULATED HERE.")
    P_(f"===   Survivor rule, fixed in the spec BEFORE this table: top-vs-bottom sign-rate spread")
    P_(f"===   >= {SPREAD_BAR:.0f} pp AND monotone or single-peaked.")
    P_("=" * 122)
    P_(f"{'state':<16}" + "".join(f"{'Q'+str(i+1):>16}" for i in range(5)) +
       f"{'spread pp':>11}{'shape':>13}{'SURVIVES':>10}")
    P_(f"{'':16}" + "".join(f"{'n  sign% mean$':>16}" for _ in range(5)))
    surv = {}
    rows = []
    for k, x in STATE.items():
        d = elig & np.isfinite(x)
        if d.sum() < 200:
            P_(f"{k:<16} too few"); continue
        xv = x[d]
        if len(np.unique(xv)) <= 3:                       # a discrete state: use its own levels
            lv = np.unique(xv)
            bins = [(xv == v) for v in lv]
            labs = [f"{v:+.0f}" for v in lv]
        else:
            q = np.nanpercentile(xv, [20, 40, 60, 80])
            bins = [xv <= q[0], (xv > q[0]) & (xv <= q[1]), (xv > q[1]) & (xv <= q[2]),
                    (xv > q[2]) & (xv <= q[3]), xv > q[3]]
            labs = ["Q1", "Q2", "Q3", "Q4", "Q5"]
        tg = target[d]
        srate = [100 * float((tg[b] > 0).mean()) if b.sum() else np.nan for b in bins]
        mean_ = [float(tg[b].mean()) if b.sum() else np.nan for b in bins]
        cnt = [int(b.sum()) for b in bins]
        sp = (np.nanmax(srate) - np.nanmin(srate))
        arr = np.array(srate)
        mono = bool(np.all(np.diff(arr) >= -1e-9) or np.all(np.diff(arr) <= 1e-9))
        peak = int(np.nanargmax(arr))
        single = bool(np.all(np.diff(arr[:peak + 1]) >= -1e-9)
                      and np.all(np.diff(arr[peak:]) <= 1e-9))
        shape = "monotone" if mono else ("single-peak" if single else "irregular")
        ok = (sp >= SPREAD_BAR) and (mono or single)
        line = f"{k:<16}"
        for i in range(len(bins)):
            line += f"{cnt[i]:>5}{srate[i]:>6.1f}{mean_[i]:>7,.0f}" if i < 5 else ""
        line += " " * max(0, 5 - len(bins)) * 16
        P_(line + f"{sp:>11.1f}{shape:>13}{('YES' if ok else 'no'):>10}")
        rows.append(dict(state=k, spread_pp=sp, shape=shape, survives=ok,
                         **{f"q{i+1}_n": cnt[i] for i in range(len(cnt))},
                         **{f"q{i+1}_sign": srate[i] for i in range(len(srate))}))
        if ok:
            # the direction implied by the table, fixed here before any P&L
            surv[k] = (x, +1.0 if arr[-1] > arr[0] else -1.0)
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "stage1.csv"), index=False)
    P_("")
    P_(f"    STAGE-1 SURVIVORS: {len(surv)} of {len(STATE)}"
       + (f" -> {', '.join(surv)}" if surv else ""))
    if not surv:
        P_("")
        P_("    NO STATE VARIABLE SEPARATES THE AFTERNOON. Per the spec, stage 1 ends the wave.")
        P_("    This is a RESULT, not a failure to find one: it says the afternoon move is not")
        P_("    forecastable from anything the morning and midday leave behind, at this")
        P_("    resolution and with these nine variables.")
        P_(f"\n[done {_time.time()-t0:.0f}s]")
        out.close(); return

    # ---------------------------------------------------------------- STAGE 2
    P_("")
    P_("=" * 122)
    P_(f"=== STAGE 2 - the {len(surv)} survivor(s) only. Decide 13:50, fill 13:51, hold 15:44.")
    P_(f"===   Carrying {len(surv)} of {len(STATE)} variables IS a selection and is charged in the null.")
    P_("=" * 122)
    P_(f"{'state':<16}{'rate':>7}{'N':>6}{'hit%':>8}{'p*':>8}{'vs p*':>8}{'$/trade':>10}"
       f"{'net $':>11}{'wk$@fixDD':>11}{'t':>6}")
    rows2, cells, prim_cells = [], [], []
    rng = np.random.default_rng(SEED)
    for k, (x, sgn) in surv.items():
        for r in RATES:
            ok_ = LaneBench.accept(np.abs(x - np.nanmedian(x)), r)
            des = np.where(ok_, sgn * np.sign(x - np.nanmedian(x)), 0)
            des = np.nan_to_num(des).astype(np.int8)
            pnl, take, cost, emove = L.trade(des, DEC, EXIT)
            st = L.stats(pnl, take, cost, emove)
            if st is None:
                P_(f"{k:<16}{r:>7.2f}   too few"); continue
            P_(f"{k:<16}{r:>7.2f}{st['n']:>6}{st['hit']:>7.2f}%{st['p_star']:>8.4f}"
               f"{100*(st['hit']/100-st['p_star']):>8.2f}{st['per_trade']:>10,.0f}"
               f"{st['net']:>11,.0f}{st['fixdd']:>11,.0f}{st['t']:>6.2f}")
            rows2.append(dict(state=k, rate=r, **st))
            mv = ((L.at(EXIT) - L.at(DEC + 1, use_open=True)) * PV)[take]
            cells.append((mv, cost))
            if abs(r - 0.50) < 1e-9:
                prim_cells.append((mv, cost))
    if rows2:
        DF = pd.DataFrame(rows2); DF.to_csv(os.path.join(OUT, "stage2.csv"), index=False)
        prim = float(DF[np.isclose(DF["rate"], 0.50)]["per_trade"].mean())
        mn, _ = LaneBench.coin_null(prim_cells, rng)
        _, mx = LaneBench.coin_null(cells, rng)
        p95m, p95x = float(np.nanpercentile(mn, 95)), float(np.nanpercentile(mx, 95))
        P_("")
        P_(f"    PRIMARY (50 % arm, mean over survivors): ${prim:,.0f}/trade")
        P_(f"    coin null p95 ${p95m:,.0f}  -> "
           f"{100*float(np.nanmean(mn < prim)):.1f}th percentile   "
           f"VERDICT: {'PASSES' if prim > p95m else 'FAILS'}")
        P_(f"    best-of-{len(cells)} bar for individual cells: ${p95x:,.0f}")
        P_("")
        P_(f"{'state':<16}" + "".join(f"{k:>17}" for k in
                                      ("TREND-UP", "TREND-DOWN", "REVERSAL", "RANGE", "MIXED")))
        for k, (x, sgn) in surv.items():
            ok_ = LaneBench.accept(np.abs(x - np.nanmedian(x)), 0.50)
            des = np.nan_to_num(np.where(ok_, sgn * np.sign(x - np.nanmedian(x)), 0)).astype(np.int8)
            pnl, take, _, _ = L.trade(des, DEC, EXIT)
            bc = L.by_class(pnl, take)
            P_(f"{k:<16}" + "".join(f"{bc[c][0]:>6} {bc[c][1]:>10,.0f}" for c in
                                    ("TREND-UP", "TREND-DOWN", "REVERSAL", "RANGE", "MIXED")))
    P_(f"\n[done {_time.time()-t0:.0f}s]")
    out.close()


if __name__ == "__main__":
    main()
