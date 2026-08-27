"""WE_W118 - THE REVERSAL SESSION, at the mechanism's OWN geometry.

Spec: runs/WE_W118_REVERSAL/spec.yaml, committed BEFORE this ran (3ea0398).

Seven fade mechanisms were killed in this campaign. Every one was an AFTERNOON FADE AT A FIXED
MIDDAY CLOCK inherited from W108's LANE C spec, and W111b showed that clock sits on the wrong side
of a live momentum effect. THE KILLS CONSTRAIN THE CLOCK, NOT THE CLASS.

A reversal session is an early extreme followed by a return through it - a statement about a
SEQUENCE. The information that a reversal is underway does not exist at a fixed minute; it exists
the moment the retracement reaches a given depth. So this is EVENT-DRIVEN.

THE CONTROL DECIDES THE WAVE: at the exact entry bars this mechanism produces, trade the PREVAILING
move instead. If reversal does not beat momentum at its own entry bars, the CLASS is closed, not
just the clock.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import ROOT, PV, COMM_RT                                 # noqa: E402
from run_we_w51c import dd_profile                                       # noqa: E402
from run_we_w114 import Win, RTH0                                        # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W118_REVERSAL", "out")
os.makedirs(OUT, exist_ok=True)
W110W = os.path.join(ROOT, "runs", "WE_W110_XMDIVERSE", "out", "weekly.csv")
TICKV = 5.0
DDT = 20245.0
EXIT_M = 944                    # 15:44
T_EXTREME_MAX = 720             # 12:00 - the extreme must be set at or before this
T_TRIGGER_MAX = 870             # 14:30 - the retracement must fire at or before this
RETR = (0.25, 0.50, 0.75)
RATES = (0.25, 0.50, 0.75)
SEED = 118
CLASSES = ("TREND-UP", "TREND-DOWN", "REVERSAL", "RANGE", "MIXED")


def scan(W, thr=None):
    """One pass per session. Returns per-session trigger bar index and direction for each R,
    plus the 12:00 excursion used to BUILD the causal threshold.

    `CORRECTION` the first run passed thr=None and applied the excursion gate AFTER the fact, to
    each session's 12:00 excursion. That never constrained WHEN the trigger could fire, so it fired
    on the first 2-point wiggle: median entry 09:32, firing on 99.4 % of sessions. The spec says the
    gate exists precisely because "without it the rule fires on noise excursions of a few points" -
    which is exactly what happened. The gate belongs AT THE TRIGGER BAR: the running excursion E
    must exceed a threshold built from PRIOR sessions before any retracement can trigger. That makes
    the entry time endogenous and late, which IS the mechanism. Original output preserved as
    out/reversal_DEFECTIVE_gate_at_1200.txt.
    """
    NS = W.NS
    trig = {r: np.full(NS, -1, np.int64) for r in RETR}
    dire = {r: np.zeros(NS) for r in RETR}
    exc12 = np.full(NS, np.nan)
    order = np.argsort(W.sid, kind="stable")
    sid_s = W.sid[order]
    bounds = np.searchsorted(sid_s, np.arange(NS + 1))
    for s in range(NS):
        idx = order[bounds[s]:bounds[s + 1]]
        if len(idx) < 100:
            continue
        md = W.mod[idx]
        sel = (md >= RTH0) & (md <= EXIT_M)
        idx = idx[sel]; md = md[sel]
        if len(idx) < 60 or md[0] != RTH0:
            continue
        o0 = W.o[idx[0]]
        hh, ll, cc = W.h[idx], W.l[idx], W.c[idx]
        runH = -np.inf; runL = np.inf; tH = -1; tL = -1
        done = {r: False for r in RETR}
        for j in range(len(idx)):
            if hh[j] > runH:
                runH = hh[j]; tH = md[j]
            if ll[j] < runL:
                runL = ll[j]; tL = md[j]
            if md[j] == T_EXTREME_MAX:
                exc12[s] = max(runH - o0, o0 - runL)
            if md[j] > T_TRIGGER_MAX:
                break
            up = (runH - o0)
            dn = (o0 - runL)
            if up >= dn:
                E = up; tset = tH; ref = runH; sgn = -1.0
                retr = (runH - cc[j]) / E if E > 0 else 0.0
            else:
                E = dn; tset = tL; ref = runL; sgn = +1.0
                retr = (cc[j] - runL) / E if E > 0 else 0.0
            floor = 0.0 if thr is None else thr[s]
            if (E <= 0 or not np.isfinite(floor) or E < floor
                    or tset > T_EXTREME_MAX or j + 1 >= len(idx)):
                continue
            for r in RETR:
                if (not done[r]) and retr >= r:
                    done[r] = True
                    trig[r][s] = idx[j + 1]        # the NEXT bar - its open is the fill
                    dire[r][s] = sgn
        if not np.isfinite(exc12[s]):
            exc12[s] = max(runH - o0, o0 - runL)
    return trig, dire, exc12


def econ(W, trig, dire, gate, exit_m=EXIT_M):
    """pnl per session from an entry at the trigger bar's OPEN to `exit_m`'s CLOSE."""
    NS = W.NS
    px = W.at(exit_m)
    pnl = np.zeros(NS); take = np.zeros(NS, bool); mv = np.full(NS, np.nan)
    cst = np.full(NS, np.nan); emin = np.full(NS, np.nan)
    for s in range(NS):
        i = trig[s]
        if i < 0 or not W.win[s] or not gate[s] or dire[s] == 0 or not np.isfinite(px[s]):
            continue
        m2 = int(W.mod[i])
        pe = W.o[i]
        c_ = COMM_RT + TICKV * (float(W.prof.get(m2, 3.0)) + float(W.prof.loc[exit_m])) / 2.0
        mv[s] = (px[s] - pe) * PV
        pnl[s] = dire[s] * mv[s] - c_
        cst[s] = c_; emin[s] = m2; take[s] = True
    return dict(pnl=pnl, take=take, mv=mv, cost=cst, emin=emin)


def stats(W, R):
    t = R["take"]
    pn = R["pnl"][t]
    if len(pn) < 10:
        return None
    em = float(np.abs(R["mv"][t]).mean())
    c_ = float(R["cost"][t].mean())
    ser = np.zeros(W.NS); ser[t] = pn
    wv = pd.Series(ser[W.sess_in]).groupby(W.wk).sum().to_numpy()
    dp = dd_profile(wv)
    return dict(n=int(t.sum()), per_trade=float(pn.mean()), net=float(pn.sum()),
                hit=100 * float((pn > 0).mean()), emove=em, cost=c_,
                pstar=0.5 * (1 + c_ / max(em, 1e-9)),
                acc=float((np.sign(R["mv"][t]) == np.sign(np.where(pn + c_ >= 0, 1, -1) *
                                                          np.sign(R["mv"][t]))).mean()),
                wk=float(wv.mean()), fixdd=float(wv.mean()) * DDT / max(dp["maxdd"], 1e-9),
                t=float(wv.mean()) / max(wv.std(ddof=1) / np.sqrt(len(wv)), 1e-9))


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "reversal.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    rng = np.random.default_rng(SEED)
    W = Win("2022-07-01", "2026-07-31 17:00", True, "MODERN")
    P_(f"    {len(W.sess_in):,} sessions [{_time.time()-t0:.0f}s]")
    def thr_at(feat, rate):
        """causal threshold: quantile (1-rate) of the feature over the PRIOR 250 sessions."""
        return pd.Series(feat).rolling(250, min_periods=60).quantile(1 - rate).shift(1).to_numpy()

    _, _, exc12 = scan(W)                       # pass 0: build the threshold source only
    THR = {g: thr_at(exc12, g) for g in RATES}
    SC = {g: scan(W, THR[g]) for g in RATES}    # one scan per gate rate - the gate is now AT ENTRY
    trig, dire = SC[0.50][0], SC[0.50][1]
    P_(f"    event scans done [{_time.time()-t0:.0f}s]")
    P_("    THE GATE IS NOW APPLIED AT THE TRIGGER BAR, not after the fact - see the CORRECTION")
    P_("    note in scan(). The first run's output is preserved as reversal_DEFECTIVE_gate_at_1200.txt")

    # ------------------------------------------------------------------ step 1: fire rates
    P_("")
    P_("=" * 126)
    P_("=== 1. FIRE RATES AND ENTRY TIMES. No P&L yet. (The W111 specification gate in spirit.)")
    P_("=" * 126)
    P_(f"{'retracement':<14}{'sessions firing':>17}{'rate':>8}{'median entry':>14}"
       f"{'p25':>8}{'p75':>8}{'short/long':>13}")
    nw = int(W.win.sum())
    for r in RETR:
        tg, dg, _ = SC[0.50]
        m = W.win & (tg[r] >= 0)
        if not m.sum():
            P_(f"{r:<14}   none"); continue
        em = np.array([W.mod[tg[r][s]] for s in np.flatnonzero(m)], float)
        P_(f"{r:<14}{int(m.sum()):>17}{m.sum()/nw:>8.1%}"
           f"{f'{int(np.median(em))//60:02d}:{int(np.median(em))%60:02d}':>14}"
           f"{f'{int(np.percentile(em,25))//60:02d}:{int(np.percentile(em,25))%60:02d}':>8}"
           f"{f'{int(np.percentile(em,75))//60:02d}:{int(np.percentile(em,75))%60:02d}':>8}"
           f"{f'{int((dg[r][m]<0).sum())} / {int((dg[r][m]>0).sum())}':>13}")
    P_("")
    P_(f"    12:00 excursion: median {np.nanmedian(exc12[W.win]):.1f} pts, "
       f"p25 {np.nanpercentile(exc12[W.win],25):.1f}, p75 {np.nanpercentile(exc12[W.win],75):.1f}")

    # ------------------------------------------------------------------ step 2: economics
    P_("")
    P_("=" * 126)
    P_("=== 2. ECONOMICS. Entry at the trigger bar's OPEN, exit at the 15:44 close, size 1.")
    P_("===    MOMENTUM_AT_SAME_BARS is the control that decides the wave.")
    P_("=" * 126)
    P_(f"{'cell':<20}{'N':>6}{'hit%':>8}{'p*':>8}{'$/trade':>10}{'net $':>11}"
       f"{'MOMENTUM':>11}{'delta':>10}{'coin p95':>10}")
    grid, prim, cells = [], [], []
    ALLTRUE = np.ones(W.NS, bool)
    for r in RETR:
        for g in RATES:
            tg, dg, _ = SC[g]
            gate = ALLTRUE                      # the gate now lives inside scan(), at the trigger
            R = econ(W, tg[r], dg[r], gate)
            s1 = stats(W, R)
            if s1 is None:
                P_(f"{f'R={r} gate={g}':<20}   too few"); continue
            Rm = econ(W, tg[r], -dg[r], gate)
            sm = stats(W, Rm)
            nul = np.array([float((rng.choice([-1.0, 1.0], size=s1["n"]) * R["mv"][R["take"]]
                                   - R["cost"][R["take"]]).mean()) for _ in range(1000)])
            p95 = float(np.percentile(nul, 95))
            P_(f"{f'R={r} gate={g}':<20}{s1['n']:>6}{s1['hit']:>7.1f}%{s1['pstar']:>8.4f}"
               f"{s1['per_trade']:>10,.0f}{s1['net']:>11,.0f}{sm['per_trade']:>11,.0f}"
               f"{s1['per_trade']-sm['per_trade']:>10,.0f}{p95:>10,.0f}")
            grid.append(dict(retr=r, gate=g, **{k: s1[k] for k in
                                                ("n", "per_trade", "net", "hit", "pstar",
                                                 "wk", "fixdd", "t")},
                             mom=sm["per_trade"], p95=p95))
            cells.append(R)
            if abs(g - 0.50) < 1e-9:
                prim.append(R)
        P_("")
    DF = pd.DataFrame(grid)
    DF.to_csv(os.path.join(OUT, "grid.csv"), index=False)

    # ------------------------------------------------------------------ the primary
    P_("=" * 126)
    P_("=== 3. THE PRIMARY - mean $/trade across the three retracement levels at gate 0.50")
    P_("=" * 126)
    pv = float(DF[np.isclose(DF["gate"], 0.50)]["per_trade"].mean())
    mvo = float(DF[np.isclose(DF["gate"], 0.50)]["mom"].mean())
    nulm = np.empty(2000)
    for b in range(2000):
        s_all = rng.choice([-1.0, 1.0], size=W.NS)
        vals = []
        for R in prim:
            t = R["take"]
            vals.append(float((s_all[t] * R["mv"][t] - R["cost"][t]).mean()))
        nulm[b] = float(np.mean(vals))
    p95m = float(np.percentile(nulm, 95))
    mxk = np.empty(2000)
    for b in range(2000):
        s_all = rng.choice([-1.0, 1.0], size=W.NS)
        mxk[b] = max(float((s_all[R["take"]] * R["mv"][R["take"]]
                            - R["cost"][R["take"]]).mean()) for R in cells)
    p95k = float(np.percentile(mxk, 95))
    P_(f"    REAL reversal      ${pv:,.0f}/trade")
    P_(f"    MOMENTUM same bars ${mvo:,.0f}/trade      delta ${pv-mvo:+,.0f}")
    P_(f"    coin null (shared per-session sign) mean ${nulm.mean():,.0f}  p95 ${p95m:,.0f}"
       f"  -> {100*float((nulm < pv).mean()):.1f}th percentile")
    c1, c2, c3 = pv > 0, pv > p95m, pv > mvo
    P_(f"    conditions: positive {c1}   beats coin {c2}   BEATS MOMENTUM {c3}")
    P_(f"    VERDICT: {'PASSES' if (c1 and c2 and c3) else 'FAILS'}"
       f"     best-of-9 bar (shared sign) ${p95k:,.0f}")

    # ------------------------------------------------------------------ controls
    P_("")
    P_("    OTHER CONTROLS at the same entry bars (gate 0.50, R=0.50):")
    gate = ALLTRUE
    tg50, dg50, _ = SC[0.50]
    for lab, d_ in (("ALWAYS LONG", np.ones(W.NS)), ("ALWAYS SHORT", -np.ones(W.NS))):
        s2 = stats(W, econ(W, tg50[0.50], d_, gate))
        P_(f"        {lab:<16} ${s2['per_trade']:>7,.0f}/trade   N {s2['n']}")

    # ------------------------------------------------------------------ class + book weeks
    P_("")
    P_("=" * 126)
    P_("=== 4. DIAGNOSTIC - session class, and value ON THE BOOK'S LOSING WEEKS")
    P_("===    A reversal mechanism not positive on REVERSAL sessions has falsified its own name.")
    P_("=" * 126)
    P_(f"{'cell':<20}" + "".join(f"{c:>17}" for c in CLASSES))
    for r in RETR:
        R = econ(W, tg50[r], dg50[r], gate)
        line = f"{f'R={r} gate=0.50':<20}"
        for c in CLASSES:
            m = R["take"] & (W.klass == c)
            line += f"{int(m.sum()):>6} {float(R['pnl'][m].mean()) if m.sum() else np.nan:>10,.0f}"
        P_(line)

    WK = pd.read_csv(W110W)
    sp, sx = WK["p1"].std(ddof=1), WK["xm"].std(ddof=1)
    w1 = (1 / sp) / ((1 / sp) + (1 / sx))
    book = (w1 * WK["p1"] + (1 - w1) * WK["xm"])
    J = pd.DataFrame(dict(week=WK["week"], book=book)).set_index("week")
    P_("")
    P_(f"{'cell':<20}{'all weeks $':>14}{'BOOK-LOSING wks $':>20}{'null mean':>12}{'null p95':>12}"
       f"{'pctile':>9}")
    for r in RETR:
        R = econ(W, tg50[r], dg50[r], gate)
        s3 = np.zeros(W.NS); s3[R["take"]] = R["pnl"][R["take"]]
        wv = pd.Series(s3[W.sess_in]).groupby(W.wk).sum()
        JJ = J.join(wv.rename("cand"), how="inner").fillna({"cand": 0.0})
        lose = (JJ["book"] < 0).to_numpy()
        v = JJ["cand"].to_numpy()
        real = float(v[lose].mean())
        nul = np.array([float(np.roll(v, k)[lose].mean()) for k in range(1, len(JJ))])
        P_(f"{f'R={r} gate=0.50':<20}{v.mean():>14,.0f}{real:>20,.0f}"
           f"{np.nanmean(nul):>12,.0f}{np.nanpercentile(nul,95):>12,.0f}"
           f"{100*float(np.nanmean(nul < real)):>8.1f}th")

    # ------------------------------------------------------------------ section 6 diagnostic
    P_("")
    P_("=" * 126)
    P_("=== 5. 2006-2021 - SECTION 6 DIAGNOSTIC ONLY. NOT a promotion veto (section 5).")
    P_("=" * 126)
    O = Win("2006-01-05", "2021-12-31 17:00", False, "OLD")
    _, _, eO = scan(O)
    tO, dO, _ = scan(O, thr_at(eO, 0.50))
    gO = np.ones(O.NS, bool)
    P_(f"{'cell':<20}{'N':>7}{'hit%':>8}{'$/trade':>10}{'net $':>12}{'MOMENTUM':>11}{'delta':>10}")
    for r in RETR:
        Ro = econ(O, tO[r], dO[r], gO)
        so = stats(O, Ro)
        if so is None:
            continue
        sm = stats(O, econ(O, tO[r], -dO[r], gO))
        P_(f"{f'R={r} gate=0.50':<20}{so['n']:>7}{so['hit']:>7.1f}%{so['per_trade']:>10,.0f}"
           f"{so['net']:>12,.0f}{sm['per_trade']:>11,.0f}{so['per_trade']-sm['per_trade']:>10,.0f}")
    P_(f"\n[done {_time.time()-t0:.0f}s]")
    out.close()


if __name__ == "__main__":
    main()
