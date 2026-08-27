"""WE_W120 - is W118's MIRROR CONTINUATION a new engine, or more of what P1 already owns?

Spec: runs/WE_W120_MOMMARGINAL/spec.yaml, committed BEFORE this ran (5677472).

Section 23: do NOT build ten continuation strategies. Section 24: run ONE portfolio diagnostic and
decide redundancy before engineering. The object is W118's construction with the direction FLIPPED
and NOTHING else changed - no threshold, level, gate, exit or window is re-chosen here.

The three conditioning slices (P1 losing, XM losing, book losing) are EX-POST OUTCOMES used as
DIAGNOSTIC SLICES. No rule in this wave conditions on them.
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
from run_we_w51c import dd_profile                                       # noqa: E402
from run_we_w114 import Win, RTH0                                        # noqa: E402
from run_we_w118 import scan, econ, stats, RETR, RATES, EXIT_M           # noqa: E402
from we_harness import causal_trailing                                   # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W120_MOMMARGINAL", "out")
os.makedirs(OUT, exist_ok=True)
LEDGER = os.path.join(ROOT, "runs", "WE_W119_BOOKLOSS", "out", "book_loss_ledger.csv")
W110W = os.path.join(ROOT, "runs", "WE_W110_XMDIVERSE", "out", "weekly.csv")
DDT = 20245.0
SEED = 120
NSHIFT = 1000


def acc_of(mv, d):
    g = np.isfinite(mv) & (np.sign(mv) != 0) & (d != 0)
    return float((np.sign(mv[g]) == d[g]).mean()) if g.sum() else np.nan


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "mommarginal.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    rng = np.random.default_rng(SEED)
    W = Win("2022-07-01", "2026-07-31 17:00", True, "MODERN")

    def thr_at(feat, rate):
        return pd.Series(feat).rolling(250, min_periods=60).quantile(1 - rate).shift(1).to_numpy()

    _, _, exc12 = scan(W)
    SC = {g: scan(W, thr_at(exc12, g)) for g in RATES}
    ALL = np.ones(W.NS, bool)
    P_(f"    {len(W.sess_in):,} sessions, W118 triggers rebuilt [{_time.time()-t0:.0f}s]")

    # the object: W118 with the direction FLIPPED. Nothing else changed.
    tg, dg, _ = SC[0.50]
    R = econ(W, tg[0.50], -dg[0.50], ALL)          # R=0.50, gate=0.50 - W118's primary cell
    s0 = stats(W, R)
    P_(f"    MIRROR_CONT (R=0.50, gate=0.50): N={s0['n']}, ${s0['per_trade']:,.0f}/trade, "
       f"net ${s0['net']:,.0f}")

    # ================================================================== 1. dashboard
    P_("")
    P_("=" * 124)
    P_("=== 1. STANDALONE DASHBOARD (section 29). All standardised windows together.")
    P_("=" * 124)
    dts = W.sdate[W.sess_in]
    ser = R["pnl"][W.sess_in]; tk = R["take"][W.sess_in]
    mvw = R["mv"][W.sess_in]; dw = (-dg[0.50])[W.sess_in]
    cw = R["cost"][W.sess_in]
    last = dts.max()
    WINS = [("t3m", dts >= last - pd.Timedelta(days=91)),
            ("t6m", dts >= last - pd.Timedelta(days=182)),
            ("t12m", dts >= last - pd.Timedelta(days=365)),
            ("YTD 2026", dts.year == 2026), ("prior yr 2025", dts.year == 2025),
            ("t24m", dts >= last - pd.Timedelta(days=730)),
            ("2022-current", np.ones(len(dts), bool))]
    P_(f"{'window':<16}{'N':>6}{'$/trade':>10}{'edge pp':>10}{'hit%':>8}{'net $':>12}{'wk $':>9}")
    for lab, m_ in WINS:
        mm = m_ & tk
        if mm.sum() < 10:
            continue
        pn = ser[mm]
        em = float(np.abs(mvw[mm]).mean()); cc = float(cw[mm].mean())
        ps = 0.5 * (1 + cc / max(em, 1e-9))
        s3 = np.zeros(len(dts)); s3[mm] = pn
        wv = pd.Series(s3).groupby(W.wk).sum().to_numpy()
        P_(f"{lab:<16}{int(mm.sum()):>6}{pn.mean():>10,.0f}"
           f"{100*(acc_of(mvw[mm], dw[mm])-ps):>9.2f}pp{100*float((pn>0).mean()):>7.1f}%"
           f"{pn.sum():>12,.0f}{wv.mean():>9,.0f}")
    O = Win("2006-01-05", "2021-12-31 17:00", False, "OLD")
    _, _, eO = scan(O)
    tO, dO, _ = scan(O, thr_at(eO, 0.50))
    Ro = econ(O, tO[0.50], -dO[0.50], np.ones(O.NS, bool))
    so = stats(O, Ro)
    P_(f"{'2006-2021 [diag]':<16}{so['n']:>6}{so['per_trade']:>10,.0f}{'':>11}"
       f"{so['hit']:>7.1f}%{so['net']:>12,.0f}")

    # ================================================================== 2. redundancy
    P_("")
    P_("=" * 124)
    P_("=== 2. REDUNDANCY - does it earn only when the book already earns? (section 24)")
    P_("===    The three slices are EX-POST OUTCOMES used as diagnostics. Not inputs.")
    P_("=" * 124)
    L = pd.read_csv(LEDGER)
    L["date"] = pd.to_datetime(L["date"]).dt.date
    d2i = {W.sdate[s].date(): s for s in range(W.NS)}
    mc = np.zeros(W.NS); mt = np.zeros(W.NS, bool)
    mc[R["take"]] = R["pnl"][R["take"]]; mt = R["take"]
    L["mirror"] = [mc[d2i[d]] if d in d2i else 0.0 for d in L["date"]]
    L["mtaken"] = [bool(mt[d2i[d]]) if d in d2i else False for d in L["date"]]
    T = L[L["mtaken"]]
    P_(f"    MIRROR_CONT trades on {len(T)} of {len(L)} in-window sessions ({100*len(T)/len(L):.1f} %)")
    P_("")
    P_(f"{'correlation (session-level, on MIRROR trade days)':<52}{'rho':>9}")
    for lab, col in (("with P1/PCT", "p1_pnl"), ("with XM_CONFLICT", "xm_pnl"),
                     ("with the research book", "book_pnl")):
        P_(f"{'   ' + lab:<52}{T['mirror'].corr(T[col]):>9.3f}")
    P_("")
    P_(f"{'slice':<44}{'N':>7}{'MIRROR $/trade':>17}{'unconditional':>16}{'difference':>13}")
    base = float(T["mirror"].mean())
    for lab, msk in (("ALL MIRROR trade sessions", np.ones(len(T), bool)),
                     ("... where P1/PCT lost that session", (T["p1_pnl"] < 0).to_numpy()),
                     ("... where XM lost that session", ((T["xm_active"]) & (T["xm_pnl"] < 0)).to_numpy()),
                     ("... where the BOOK lost that session", (T["book_pnl"] < 0).to_numpy()),
                     ("... where the BOOK won that session", (T["book_pnl"] > 0).to_numpy())):
        v = T["mirror"].to_numpy()[msk]
        if len(v) < 5:
            continue
        P_(f"{lab:<44}{len(v):>7}{v.mean():>17,.0f}{base:>16,.0f}{v.mean()-base:>+13,.0f}")

    # ================================================================== 3. portfolio
    P_("")
    P_("=" * 124)
    P_("=== 3. PORTFOLIO - the SAME FOUR GATES W116 applied to FOLLOW_MORNING (section 28)")
    P_("=" * 124)
    WK = pd.read_csv(W110W)
    mw = pd.Series(mc[W.sess_in]).groupby(W.wk).sum()
    J = WK.set_index("week")[["p1", "xm"]].copy()
    J["mc"] = mw
    J = J.fillna({"mc": 0.0})
    sp, sx = J["p1"].std(ddof=1), J["xm"].std(ddof=1)
    w1 = (1 / sp) / ((1 / sp) + (1 / sx))
    J["book"] = w1 * J["p1"] + (1 - w1) * J["xm"]
    NW = len(J)
    bookv = J["book"].to_numpy(); mcv = J["mc"].to_numpy()
    lose = bookv < 0

    def dstats(a, b):
        m = a < 0
        qa, qb = np.percentile(a, 10), np.percentile(b, 10)
        lo = a <= qa
        return {"rho": float(np.corrcoef(a, b)[0, 1]),
                "rho | book losing": float(np.corrcoef(a[m], b[m])[0, 1]) if m.sum() > 5 else np.nan,
                "P(cand<0 | book<0)": float((b[m] < 0).mean()) if m.sum() else np.nan,
                "worst-decile overlap": float(((a <= qa) & (b <= qb)).mean()),
                "$ on book-losing weeks": float(b[m].mean()) if m.sum() else np.nan,
                "tail beta": float(np.polyfit(a[lo], b[lo], 1)[0]) if lo.sum() > 5 else np.nan}
    real = dstats(bookv, mcv)
    NN = pd.DataFrame([dstats(bookv, np.roll(mcv, k)) for k in range(1, min(NSHIFT, NW))])
    P_(f"    {NW} weeks. Unconditional P(MIRROR<0) = {float((mcv<0).mean()):.3f}")
    P_(f"{'statistic':<26}{'REAL':>11}{'null mean':>11}{'null p95':>11}{'pctile':>9}")
    for k in real:
        nv = NN[k].to_numpy()
        P_(f"{k:<26}{real[k]:>11.3f}{np.nanmean(nv):>11.3f}{np.nanpercentile(nv,95):>11.3f}"
           f"{100*float(np.nanmean(nv < real[k])):>8.1f}th")

    def summ(v):
        vv = np.asarray(v, float); dp = dd_profile(vv); srt = np.sort(vv)
        return dict(wk=vv.mean(), maxdd=dp["maxdd"],
                    fixdd=vv.mean() * DDT / max(dp["maxdd"], 1e-9),
                    poswk=100 * float((vv > 0).mean()),
                    cvar=float(srt[:max(1, int(0.05 * len(srt)))].mean()))
    P_("")
    P_(f"{'book':<34}{'conv':<10}{'wk $':>9}{'maxDD':>10}{'wk$@fixDD':>11}{'pos wk%':>9}{'CVaR5':>9}")
    inc = {}
    for how in ("invvol", "income"):
        for lab, cols in (("P1/PCT + XM (incumbent)", ["p1", "xm"]),
                          ("P1/PCT + XM + MIRROR_CONT", ["p1", "xm", "mc"])):
            if how == "invvol":
                w = np.array([1 / max(J[c].std(ddof=1), 1e-9) for c in cols])
            else:
                w = np.array([1 / max(abs(J[c].mean()), 1e-9) for c in cols])
            w = w / w.sum() * len(cols)
            v = sum(w[i] * J[cols[i]] for i in range(len(cols))) / len(cols)
            s4 = summ(v.to_numpy()); inc[(how, lab)] = s4
            P_(f"{lab:<34}{how:<10}{s4['wk']:>9,.0f}{s4['maxdd']:>10,.0f}{s4['fixdd']:>11,.0f}"
               f"{s4['poswk']:>8.1f}%{s4['cvar']:>9,.0f}")
        P_("")
    d_iv = (inc[("invvol", "P1/PCT + XM + MIRROR_CONT")]["fixdd"]
            - inc[("invvol", "P1/PCT + XM (incumbent)")]["fixdd"])
    d_im = (inc[("income", "P1/PCT + XM + MIRROR_CONT")]["fixdd"]
            - inc[("income", "P1/PCT + XM (incumbent)")]["fixdd"])
    P_(f"    INCREMENTAL fixed-DD weekly $: inverse-vol {d_iv:+,.0f}, income-matched {d_im:+,.0f}"
       f"   -> RANGE {min(d_iv,d_im):+,.0f} to {max(d_iv,d_im):+,.0f}")

    # ================================================================== 4. verdict
    P_("")
    P_("=" * 124)
    P_("=== 4. THE FOUR GATES, applied identically to how W116 applied them to FOLLOW_MORNING")
    P_("=" * 124)
    nv = NN["$ on book-losing weeks"].to_numpy()
    g1 = real["$ on book-losing weeks"] > 0
    g2 = real["$ on book-losing weeks"] > float(np.nanpercentile(nv, 95))
    g3 = (d_iv > 0) or (d_im > 0)
    wd = NN["worst-decile overlap"].to_numpy()
    g4 = real["worst-decile overlap"] <= float(np.nanpercentile(wd, 95))
    for lab, g in (("earns > 0 on book-losing weeks", g1),
                   ("beats its circular-shift null there", g2),
                   ("incremental fixed-DD > 0 at either convention", g3),
                   ("worst-decile overlap NOT worse than the null's 95th", g4)):
        P_(f"    {lab:<58}{'PASS' if g else 'FAIL'}")
    div = g1 and g2 and g3 and g4
    P_("")
    P_(f"    CLASSIFICATION: {'DIVERSIFYING CANDIDATE' if div else 'REDUNDANT / NOT DIVERSIFYING'}")
    P_(f"    (FOLLOW_MORNING failed gates 2 and 4 in W116, for direct comparison.)")
    J.to_csv(os.path.join(OUT, "weekly_joint.csv"))
    L.to_csv(os.path.join(OUT, "sessions.csv"), index=False)
    P_(f"\n[done {_time.time()-t0:.0f}s]")
    out.close()


if __name__ == "__main__":
    main()
