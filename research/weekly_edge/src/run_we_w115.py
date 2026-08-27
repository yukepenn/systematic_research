"""WE_W115 - WHY did intraday momentum strengthen eight-fold, and is the driver OBSERVABLE?

Spec: runs/WE_W115_MOMDRIVER/spec.yaml + AMENDMENT 1, both committed BEFORE this ran (8a18d71).

W114 measured FOLLOW_MORNING's implied directional edge at 0.70 % on 2006-2021 and 5.62 % on
2022-2026, monotone across four blocks, and showed the gap is NOT the cost hurdle. This wave asks
whether an OBSERVABLE market variable explains it.

THE TEST THAT DECIDES IT IS WITHIN-ERA ORDERING. A variable that only separates old years from
modern years is the calendar wearing a volume costume. Three explicit null drivers - price level,
calendar year, linear time index - are carried for exactly that reason.

CAUSALITY. Every volume driver is a trailing mean over COMPLETED PRIOR SESSIONS ONLY. No part of
the traded session's afternoon or closing volume enters its own driver value. Asserted below, not
assumed.
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
from run_we_w114 import Win, RTH0, MORN_B, DEC, EXIT                     # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W115_MOMDRIVER", "out")
os.makedirs(OUT, exist_ok=True)
RTH_A, RTH_B = 571, 960         # 09:31 -> 16:00, end-stamped
LH_A, LH_B = 901, 960           # 15:00 -> 16:00, the last hour
FH_A, FH_B = 571, 630           # 09:31 -> 10:30, the first hour
TRAIL = 60                      # sessions, for every volume driver
NPERM = 2000
SEED = 115
ERA_CUT = np.datetime64("2022-07-01")


def vol_between(W, a, b):
    m = (W.mod >= a) & (W.mod <= b)
    ii = np.flatnonzero(m)
    r = np.zeros(W.NS)
    np.add.at(r, W.sid[ii], W.v[ii])
    return r


def trail_mean(x, k=TRAIL, minp=None):
    """mean over the PRIOR k sessions. shift(1) is what makes it causal."""
    return pd.Series(x).rolling(k, min_periods=minp or max(10, k // 3)).mean().shift(1).to_numpy()


def acc_of(mv, d):
    g = np.isfinite(mv) & (np.sign(mv) != 0) & (d != 0)
    return float((np.sign(mv[g]) == d[g]).mean()) if g.sum() else np.nan


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "momdriver.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    rng = np.random.default_rng(SEED)
    W = Win("2006-01-05", "2026-07-31 17:00", True, "POOLED 2006-2026")
    W.v = W.D["v"]
    P_(f"    pooled substrate {W.n:,} bars / {len(W.sess_in):,} sessions [{_time.time()-t0:.0f}s]")

    # ------------------------------------------------------------------ the object
    md = W.morn_dir()
    R = W.run(DEC, EXIT, md)
    mv, take, cost = R["mv"], R["take"], R["cost"]
    dirv = np.nan_to_num(md)
    era_modern = np.array([W.t[W.st[s]] >= ERA_CUT for s in range(W.NS)])

    # ------------------------------------------------------------------ drivers
    v_lh = vol_between(W, LH_A, LH_B)
    v_rth = vol_between(W, RTH_A, RTH_B)
    v_fh = vol_between(W, FH_A, FH_B)
    raw_share = np.where(v_rth > 0, v_lh / np.maximum(v_rth, 1e-9), np.nan)
    raw_ratio = np.where(v_fh > 0, v_lh / np.maximum(v_fh, 1e-9), np.nan)
    med250 = pd.Series(v_rth).rolling(250, min_periods=60).median().shift(1).to_numpy()

    DRV = {
        "V_CLOSE_SHARE":    trail_mean(raw_share),
        "V_LASTHOUR_RATIO": trail_mean(raw_ratio),
        "SESSION_VOL_LEVEL": trail_mean(v_rth / np.maximum(med250, 1e-9)),
        "PRICE_LEVEL":      W.at(RTH0, use_open=True),
        "CAL_YEAR":         np.array([W.sdate[s].year for s in range(W.NS)], float),
        "TIME_IDX":         np.arange(W.NS, dtype=float),
    }
    NULLS = ("PRICE_LEVEL", "CAL_YEAR", "TIME_IDX")

    # ------------------------------------------------------------------ causality assertion
    P_("")
    P_("=" * 126)
    P_("=== 0. CAUSALITY ASSERTION - does any volume driver see its own session's afternoon?")
    P_("=" * 126)
    P_("    `CORRECTION` the first version of this check corrupted EVERY traded session at once and")
    P_("    then asked whether each session's driver moved. Of course it moved - session i's window")
    P_("    covers sessions i-60..i-1, most of which were also corrupted. The check fired on all")
    P_("    three drivers and the DEFECT WAS THE CHECK. Replaced with two tests that have teeth:")
    P_("    (a) a window identity, and (b) a SINGLE-session perturbation.")
    P_("")
    ok = True
    SRC = {"V_CLOSE_SHARE": raw_share, "V_LASTHOUR_RATIO": raw_ratio,
           "SESSION_VOL_LEVEL": v_rth / np.maximum(med250, 1e-9)}
    probes = [i for i in range(400, W.NS - 2, 617)][:8]
    for k, src in SRC.items():
        # (a) driver[i] must EQUAL the mean of raw[i-TRAIL : i] - a window that strictly precedes i
        ident = all(
            (not np.isfinite(DRV[k][i]))
            or np.isclose(DRV[k][i], np.nanmean(src[max(0, i - TRAIL):i]), rtol=1e-9, atol=1e-12)
            for i in probes)
        # (b) corrupt ONE session only. driver[i] must NOT move; driver[i+1] MUST move.
        selfsafe = nextmoves = True
        for i in probes:
            c = src.copy(); c[i] = (c[i] if np.isfinite(c[i]) else 1.0) * 1e3 + 7.0
            d2 = trail_mean(c)
            if np.isfinite(DRV[k][i]) and not np.isclose(DRV[k][i], d2[i], rtol=1e-12, atol=1e-15):
                selfsafe = False
            if np.isfinite(DRV[k][i + 1]) and np.isclose(DRV[k][i + 1], d2[i + 1],
                                                         rtol=1e-12, atol=1e-15):
                nextmoves = False
        ok &= (ident and selfsafe and nextmoves)
        P_(f"    {k:<20} window == mean(raw[i-{TRAIL}:i]): {str(ident):<5}   "
           f"own session cannot move it: {str(selfsafe):<5}   "
           f"NEXT session does move (teeth): {str(nextmoves):<5}")
    P_(f"    PRICE_LEVEL uses the 09:31 OPEN of the traded session, known at 11:48. CAL_YEAR and")
    P_(f"    TIME_IDX are pure calendar and are NULL DRIVERS ONLY (directive section 31).")
    if not ok:
        P_("    CAUSALITY CHECK FAILED. No table is issued.")
        out.close(); return
    P_("    PASS.")

    # ------------------------------------------------------------------ has it even risen?
    P_("")
    P_("=" * 126)
    P_("=== 1. DESCRIPTION - has late-session volume share actually risen? (no P&L here)")
    P_("=" * 126)
    P_(f"{'block':<14}{'sessions':>10}{'close share':>14}{'last/first hr':>15}"
       f"{'RTH vol (M)':>14}{'NQ level':>11}")
    for lo, hi in ((2006, 2010), (2011, 2015), (2016, 2019), (2020, 2021),
                   (2022, 2023), (2024, 2026)):
        m = np.array([lo <= W.sdate[s].year <= hi for s in range(W.NS)]) & W.win
        if not m.sum():
            continue
        P_(f"{f'{lo}-{hi}':<14}{int(m.sum()):>10}{np.nanmean(raw_share[m]):>14.4f}"
           f"{np.nanmean(raw_ratio[m]):>15.4f}{np.nanmean(v_rth[m])/1e6:>14.3f}"
           f"{np.nanmean(DRV['PRICE_LEVEL'][m]):>11,.0f}")

    P_("")
    P_("    PAIRWISE RANK CORRELATION of the six drivers - printed FIRST so nobody reads six")
    P_("    variables as six hypotheses:")
    ks = list(DRV)
    gg = W.win & np.all(np.isfinite(np.column_stack([DRV[k] for k in ks])), axis=1)
    C = pd.DataFrame({k: DRV[k][gg] for k in ks}).corr(method="spearman")
    P_(f"{'':<20}" + "".join(f"{k[:14]:>16}" for k in ks))
    for k in ks:
        P_(f"{k:<20}" + "".join(f"{C.loc[k, j]:>16.3f}" for j in ks))

    # ------------------------------------------------------------------ the quintile machinery
    def qtable(driver, mask, nq=5):
        """returns list of dicts per quantile bin, computed WITHIN `mask`."""
        d = mask & np.isfinite(driver) & take
        if d.sum() < 100:
            return None
        x = driver[d]
        qs = np.nanpercentile(x, np.linspace(0, 100, nq + 1)[1:-1])
        bidx = np.searchsorted(qs, x)
        rows = []
        for b in range(nq):
            sel = bidx == b
            if sel.sum() < 20:
                rows.append(None); continue
            mvq = mv[d][sel]; dq = dirv[d][sel]
            em = float(np.abs(mvq).mean())
            ps = 0.5 * (1 + cost / max(em, 1e-9))
            a = acc_of(mvq, dq)
            pnl = dq * mvq - cost
            rows.append(dict(n=int(sel.sum()), acc=a, pstar=ps, edge=100 * (a - ps),
                             per_trade=float(pnl.mean()), emove=em,
                             hit=100 * float((pnl > 0).mean())))
        return rows

    def spread_of(rows):
        if rows is None or rows[0] is None or rows[-1] is None:
            return np.nan
        return rows[-1]["edge"] - rows[0]["edge"]

    def show(name, rows):
        if rows is None:
            P_(f"{name:<20}  too few"); return
        line = f"{name:<20}"
        for r in rows:
            line += "        -      " if r is None else f"{r['n']:>6}{r['edge']:>8.2f}pp"
        P_(line + f"{spread_of(rows):>11.2f}")

    # ------------------------------------------------------------------ pooled (descriptive)
    P_("")
    P_("=" * 126)
    P_("=== 2. POOLED QUINTILES - DESCRIPTIVE ONLY. This split uses full-sample information and")
    P_("===    is not a tradeable state. Cell = n and (directional accuracy - that cell's own p*).")
    P_("=" * 126)
    P_(f"{'driver':<20}" + "".join(f"{'Q'+str(i+1):>14}" for i in range(5)) + f"{'Q5-Q1':>11}")
    pooled = {}
    for k in ks:
        rows = qtable(DRV[k], W.win)
        pooled[k] = spread_of(rows)
        show(k + ("  [NULL]" if k in NULLS else ""), rows)

    # ------------------------------------------------------------------ WITHIN ERA - the real test
    P_("")
    P_("=" * 126)
    P_("=== 3. ⭐ WITHIN-ERA ORDERING - THE TEST THAT DECIDES THE WAVE.")
    P_("===    Quintiles computed INSIDE each era, so the split itself cannot order the eras.")
    P_("===    A real driver orders the edge in BOTH. A calendar proxy orders neither.")
    P_("=" * 126)
    within = {}
    for era, m_, lab in ((0, W.win & ~era_modern, "OLD 2006-2022H1"),
                         (1, W.win & era_modern, "MODERN 2022H2-2026")):
        P_(f"    --- {lab}   ({int((m_ & take).sum())} traded sessions) ---")
        P_(f"{'driver':<20}" + "".join(f"{'Q'+str(i+1):>14}" for i in range(5)) + f"{'Q5-Q1':>11}")
        for k in ks:
            rows = qtable(DRV[k], m_)
            within.setdefault(k, {})[era] = spread_of(rows)
            show(k + ("  [NULL]" if k in NULLS else ""), rows)
        P_("")

    # ------------------------------------------------------------------ the primary + null
    P_("=" * 126)
    P_("=== 4. THE PRIMARY - V_CLOSE_SHARE pooled Q5-Q1 spread, against 2,000 label permutations")
    P_("=" * 126)
    real = pooled["V_CLOSE_SHARE"]
    d0 = W.win & np.isfinite(DRV["V_CLOSE_SHARE"]) & take
    nul = np.empty(NPERM)
    base = DRV["V_CLOSE_SHARE"].copy()
    idxd = np.flatnonzero(d0)
    for b in range(NPERM):
        sh = base.copy()
        sh[idxd] = base[rng.permutation(idxd)]
        nul[b] = spread_of(qtable(sh, W.win))
    p95 = float(np.nanpercentile(nul, 95))
    pc = 100 * float(np.nanmean(nul < real))
    P_(f"    REAL Q5-Q1 = {real:+.2f} pp    null mean {np.nanmean(nul):+.2f}  sd {np.nanstd(nul):.2f}"
       f"  p95 {p95:+.2f}  -> {pc:.1f}th percentile")
    beats_nulls = all(real > pooled[k] for k in NULLS)
    P_(f"    null drivers' pooled spreads: "
       + ", ".join(f"{k} {pooled[k]:+.2f}" for k in NULLS)
       + f"   -> volume driver larger than ALL: {beats_nulls}")
    both = (np.isfinite(within['V_CLOSE_SHARE'][0]) and np.isfinite(within['V_CLOSE_SHARE'][1])
            and within['V_CLOSE_SHARE'][0] > 0 and within['V_CLOSE_SHARE'][1] > 0)
    P_(f"    within-era spreads: OLD {within['V_CLOSE_SHARE'][0]:+.2f} pp, "
       f"MODERN {within['V_CLOSE_SHARE'][1]:+.2f} pp   -> same sign in BOTH: {both}")
    v = (real > 0) and (real > p95) and beats_nulls and both
    P_("")
    P_(f"    VERDICT: {'DRIVER IDENTIFIED' if v else 'NO DRIVER IDENTIFIED'}")
    if not v:
        why = []
        if not (real > 0 and real > p95):
            why.append("pooled spread does not clear its permutation null")
        if not beats_nulls:
            why.append("a CALENDAR/PRICE null driver orders the edge as well or better")
        if not both:
            why.append("the ordering does not hold WITHIN both eras")
        P_(f"    reason: {'; '.join(why)}")

    # ------------------------------------------------------------------ prequential
    P_("")
    P_("=" * 126)
    P_("=== 5. PREQUENTIAL ARM - the only state assignment here that is fully out of sample.")
    P_("===    Terciles from a TRAILING 250-session causal quantile, shifted one session.")
    P_("=" * 126)
    P_(f"{'driver':<20}{'LOW n':>8}{'LOW edge':>11}{'MID n':>8}{'MID edge':>11}"
       f"{'HIGH n':>8}{'HIGH edge':>11}{'HIGH-LOW':>11}")
    for k in ks:
        x = DRV[k]
        s = pd.Series(x)
        q33 = s.rolling(250, min_periods=100).quantile(1 / 3).shift(1).to_numpy()
        q67 = s.rolling(250, min_periods=100).quantile(2 / 3).shift(1).to_numpy()
        g = W.win & take & np.isfinite(x) & np.isfinite(q33) & np.isfinite(q67)
        cells = []
        for lo, hi in ((-np.inf, q33), (q33, q67), (q67, np.inf)):
            sel = g & (x > (lo if np.isscalar(lo) else lo)) & (x <= (hi if np.isscalar(hi) else hi))
            if sel.sum() < 30:
                cells.append(None); continue
            mvq, dq = mv[sel], dirv[sel]
            em = float(np.abs(mvq).mean())
            cells.append(dict(n=int(sel.sum()),
                              edge=100 * (acc_of(mvq, dq) - 0.5 * (1 + cost / max(em, 1e-9)))))
        line = f"{k + ('  [NULL]' if k in NULLS else ''):<20}"
        for c in cells:
            line += f"{'-':>8}{'-':>11}" if c is None else f"{c['n']:>8}{c['edge']:>10.2f}pp"
        hl = (cells[2]["edge"] - cells[0]["edge"]) if (cells[0] and cells[2]) else np.nan
        P_(line + f"{hl:>10.2f}pp")

    # ------------------------------------------------------------------ rolling
    P_("")
    P_("    ROLLING: 250-session correlation between each driver and the realised per-session")
    P_("    signed outcome (+1 if the afternoon continued the morning, -1 if not).")
    outc = np.where(take, np.where(np.sign(mv) == dirv, 1.0, -1.0), np.nan)
    P_(f"{'driver':<20}{'mean rho':>11}{'frac > 0':>11}{'last':>11}")
    for k in ks:
        s1 = pd.Series(np.where(W.win, DRV[k], np.nan))
        s2 = pd.Series(np.where(W.win, outc, np.nan))
        rr = s1.rolling(250, min_periods=150).corr(s2).dropna().to_numpy()
        if len(rr) < 10:
            continue
        P_(f"{k + ('  [NULL]' if k in NULLS else ''):<20}{np.nanmean(rr):>11.3f}"
           f"{100*float(np.nanmean(rr > 0)):>10.1f}%{rr[-1]:>11.3f}")

    pd.DataFrame({k: DRV[k] for k in ks} | dict(
        date=W.sdate, traded=take, mv=mv, dir=dirv, modern=era_modern)).to_csv(
        os.path.join(OUT, "drivers.csv"), index=False)
    P_(f"\n[done {_time.time()-t0:.0f}s]")
    out.close()


if __name__ == "__main__":
    main()
