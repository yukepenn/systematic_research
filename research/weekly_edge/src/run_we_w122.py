"""WE_W122 - CROSS-MARKET INTRADAY SUPPORT AT THE P1 DECISION EVENT. STAGE A ONLY.

Spec: runs/WE_W122_XSUPPORT/spec.yaml, committed BEFORE this ran (b351fe4).

W119: the book's gap is not presence coverage. W121: it is not entry count either - the 4th entry
of a session is the BEST cell. So the missing variable is ENTRY QUALITY. XM proved cross-market
information can carry orthogonal value but only at the opening auction. This asks whether broad
support carries information at P1's OWN entry events, all day.

THE HEADLINE IS LEVEL 4 MINUS LEVEL 3, never LEVEL 4 alone (section 15). A cross-market feature is
new information only if it survives matching on NQ's own move, P1's state, time-of-day and ordinal.

NO POLICY IS TESTED HERE (section 23).
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_we_w01 as W1                                                  # noqa: E402
from run_we_w01 import ROOT, PV, COMM_RT                                 # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w51 import session_frames                                    # noqa: E402
from run_we_w97 import votes                                             # noqa: E402
from run_we_w98 import gfills, arm_kw                                    # noqa: E402
from we_fastctx import fast_build_context                                # noqa: E402
from we_lab import spread_profile                                        # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W122_XSUPPORT", "out")
os.makedirs(OUT, exist_ok=True)
W76OUT = os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out")
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
TICKV = 5.0
WINDOWS = (5, 15, 30)
PRIMS = ("A_SIGN_BREADTH", "B_SUPPORT_MAG", "C_DISPERSION", "D_NQ_IDIO", "E_DELAYED_CONF")
PRIMARY_CELL = ("B_SUPPORT_MAG", 15)
SIGN_N = 5000                    # bars for the causal sigma of each window return
NPERM = 2000
NBLOCK = 8
SEED = 122
XMP = {"ES": "runs/SM1M_ES_SUBSTRATE/out/es_1m_2022_2026.parquet",
       "RTY": "runs/SM1M_RTY_SUBSTRATE/out/rty_1m_2022_2026.parquet",
       "YM": "runs/SM1M_YM_SUBSTRATE/out/ym_1m_2022_2026.parquet"}


def wret(c, W):
    """W-bar log return ending at each bar. NaN where the window is not available."""
    r = np.full(len(c), np.nan)
    with np.errstate(divide="ignore", invalid="ignore"):
        r[W:] = np.log(c[W:] / c[:-W])
    return r


def causal_sigma(x, n=SIGN_N):
    return pd.Series(x).rolling(n, min_periods=n // 5).std().shift(1).to_numpy()


def matched_diff(q, strat, y, weights_out=False):
    """weighted mean over strata of (mean y in Q5 within stratum) - (mean y in Q1 within stratum).

    Only strata containing BOTH a Q1 and a Q5 member contribute. Weight = min(n_Q1, n_Q5).
    """
    m = np.isin(q, (1, 5)) & np.isfinite(y) & (strat >= 0)
    if m.sum() < 40:
        return np.nan, None
    s = strat[m]; hi = (q[m] == 5).astype(np.int64); yy = y[m]
    gid = s * 2 + hi
    G = 2 * (int(s.max()) + 1)          # MUST be even: gid = stratum*2 + hi, so the Q1 slice
    #                                     (0::2) and the Q5 slice (1::2) have equal length
    cnt = np.bincount(gid, minlength=G).astype(float)
    tot = np.bincount(gid, weights=yy, minlength=G)
    lo_c, hi_c = cnt[0::2], cnt[1::2]
    lo_t, hi_t = tot[0::2], tot[1::2]
    ok = (lo_c > 0) & (hi_c > 0)
    if ok.sum() == 0:
        return np.nan, None
    d = hi_t[ok] / hi_c[ok] - lo_t[ok] / lo_c[ok]
    w = np.minimum(lo_c[ok], hi_c[ok])
    val = float(np.sum(d * w) / np.sum(w))
    return (val, dict(gid=gid, G=G, ok=ok, w=w, mask=m)) if weights_out else (val, None)


def matched_diff_fast(pre, y):
    """recompute matched_diff for a NEW y using precomputed group ids."""
    gid, G, ok, w, m = pre["gid"], pre["G"], pre["ok"], pre["w"], pre["mask"]
    yy = y[m]
    cnt = np.bincount(gid, minlength=G).astype(float)
    tot = np.bincount(gid, weights=yy, minlength=G)
    lo_c, hi_c = cnt[0::2], cnt[1::2]
    lo_t, hi_t = tot[0::2], tot[1::2]
    d = hi_t[ok] / hi_c[ok] - lo_t[ok] / lo_c[ok]
    return float(np.sum(d * w) / np.sum(w))


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "xsupport.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    rng = np.random.default_rng(SEED)
    prof = spread_profile()
    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr, sid = D["n"], D["t"], D["sid"]
    o, c, h, l = D["o"], D["c"], D["h"], D["l"]
    st_, en_, _ = session_frames(D)
    mod = ((tarr - tarr.astype("datetime64[D]")).astype("timedelta64[s]")
           .astype(np.int64) // 60).astype(np.int32)
    NS = D["n_sess"]
    win = np.array([A <= tarr[st_[s]] < B for s in range(NS)])
    P_(f"    substrate {n:,} bars [{_time.time()-t0:.0f}s]")

    # ------------------------------------------------------------------ P1 events
    X = fast_build_context(D)
    z = np.load(os.path.join(W76OUT, "mem_ext.npz"))
    mem, bmom, tilt = z["mem"], z["bmom"], z["tilt"]

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))
    vl, _ = votes(D, mem, bmom, tilt, X, bmom)
    p1 = vl.astype(np.int8)
    bb = fills_daily(D, p1, halt=1300, target=1000)
    ee = np.array([i_of(x["et"]) for x in bb if A <= np.datetime64(x["et"]) < B])
    scq, _ = causal_score(X, ee, window=WIN)
    tr = gfills(D, p1, np.where(scq >= 3, 2, 1).astype(np.int8), **arm_kw("PCT", 1.183))
    wq = {}
    for x in tr:
        for ts in (x["et"], x["xt"]):
            pp = pd.Timestamp(ts); m2 = pp.hour * 60 + pp.minute
            wq[m2] = wq.get(m2, 0.0) + x["u"]
    rP = TICKV * sum(float(prof.get(m2, 3.0)) * q for m2, q in wq.items()) / max(sum(wq.values()), 1)

    ev = []
    bysess = {}
    for x in tr:
        ei = i_of(x["et"]); s = int(sid[ei])
        bysess.setdefault(s, []).append((ei, x))
    for s, xs in bysess.items():
        if not win[s]:
            continue
        xs.sort(key=lambda t: t[0])
        cum = 0.0
        for k, (ei, x) in enumerate(xs, start=1):
            xi = i_of(x["xt"]); u = int(x["u"]); d_ = int(x["d"])
            hh, ll = h[ei:xi + 1], l[ei:xi + 1]
            epx = o[ei]
            ev.append(dict(sess=s, ei=ei, xi=xi, date=pd.Timestamp(x["et"]).date(),
                           emin=int(mod[ei]), d=d_, u=u, ordinal=k,
                           net=x["pnl"] - rP * u, gross=x["pnl"] + COMM_RT * u,
                           hold=max((pd.Timestamp(x["xt"]) - pd.Timestamp(x["et"])).total_seconds()
                                    / 60.0, 0.0),
                           mfe=((hh.max() - epx) if d_ > 0 else (epx - ll.min())) * PV,
                           mae=((ll.min() - epx) if d_ > 0 else (epx - hh.max())) * PV,
                           qscore=float(scq[ei]) if ei < len(scq) else np.nan,
                           box_before=cum))
            cum += x["pnl"] / u
    E = pd.DataFrame(ev).sort_values("ei").reset_index(drop=True)
    P_(f"    {len(E):,} P1 entry events [{_time.time()-t0:.0f}s]")

    # ------------------------------------------------------------------ cross-market
    nqf = pd.DataFrame({"time": pd.to_datetime(tarr)}).set_index("time")
    CM = {}
    for k, pth in XMP.items():
        f = os.path.join(ROOT, pth)
        d_ = pd.read_parquet(f, columns=["time", "close"]); d_["time"] = pd.to_datetime(d_["time"])
        CM[k] = nqf.join(d_.set_index("time")["close"].rename(k), how="left")[k].to_numpy()
    P_(f"    ES/RTY/YM joined [{_time.time()-t0:.0f}s]")

    ei = E["ei"].to_numpy()
    dsign = E["d"].to_numpy().astype(float)
    same_sess = {}
    FEAT = {}
    for W in WINDOWS:
        rn = wret(c, W); sn = causal_sigma(rn)
        zn = rn / np.maximum(sn, 1e-12)
        zk = {}
        for k in CM:
            rk = wret(CM[k], W); sk = causal_sigma(rk)
            zk[k] = rk / np.maximum(sk, 1e-12)
        j = ei - 1                                  # the signal bar: strictly before the fill
        ok = (j - W >= 0) & (sid[np.maximum(j - W, 0)] == sid[j])
        same_sess[W] = ok
        znj = np.where(ok, zn[j], np.nan)
        Z = np.column_stack([np.where(ok, zk[k][j], np.nan) for k in ("ES", "RTY", "YM")])
        FEAT[("A_SIGN_BREADTH", W)] = np.sum(np.sign(Z) == dsign[:, None], axis=1).astype(float)
        FEAT[("B_SUPPORT_MAG", W)] = np.nanmean(Z, axis=1) * dsign
        FEAT[("C_DISPERSION", W)] = np.nanstd(Z, axis=1)
        FEAT[("D_NQ_IDIO", W)] = (znj - np.nanmean(Z, axis=1)) * dsign
        h3 = max(W // 3, 1)
        rn3 = {}
        for k in CM:
            rk3 = wret(CM[k], h3); sk3 = causal_sigma(rk3)
            rn3[k] = rk3 / np.maximum(sk3, 1e-12)
        late = np.nanmean(np.column_stack([np.where(ok, rn3[k][j], np.nan) for k in CM]), axis=1)
        early = np.nanmean(np.column_stack([np.where(ok, rn3[k][np.maximum(j - W + h3, 0)], np.nan)
                                            for k in CM]), axis=1)
        FEAT[("E_DELAYED_CONF", W)] = (late - early) * dsign
        FEAT[("NQ_OWN", W)] = znj * dsign            # the LEVEL-2 control
    P_(f"    features built. same-session availability: "
       + ", ".join(f"{W}m {100*same_sess[W].mean():.1f}%" for W in WINDOWS))

    # ------------------------------------------------------------------ strata
    nq15 = FEAT[("NQ_OWN", 15)]
    qnq = pd.qcut(pd.Series(nq15), 5, labels=False, duplicates="drop").to_numpy()
    tod = np.select([E["emin"] < 571, E["emin"] < 690, E["emin"] < 810],
                    [0, 1, 2], default=3)
    ordb = np.clip(E["ordinal"].to_numpy(), 1, 3) - 1
    strat = np.where(np.isfinite(qnq), qnq * 12 + tod * 3 + ordb, -1).astype(np.int64)
    y = E["net"].to_numpy()
    P_(f"    {int((strat>=0).sum())} events in {len(np.unique(strat[strat>=0]))} matched strata "
       f"(NQ-move quintile x 4 time buckets x 3 ordinal buckets)")

    # ------------------------------------------------------------------ the grid
    P_("")
    P_("=" * 126)
    P_("=== 1. THE 5 x 3 GRID. POOLED vs MATCHED. The matched column is the one that matters:")
    P_("===    it holds NQ's own pre-entry move, time-of-day and entry ordinal fixed (section 15).")
    P_("=" * 126)
    P_(f"{'primitive':<18}{'window':>8}{'n Q1':>7}{'n Q5':>7}{'POOLED Q5-Q1 $':>17}"
       f"{'MATCHED Q5-Q1 $':>18}{'matched/pooled':>16}")
    QQ, PRE, cells = {}, {}, []
    for p_ in PRIMS:
        for W in WINDOWS:
            x = FEAT[(p_, W)]
            g = np.isfinite(x)
            if g.sum() < 200:
                continue
            q = np.full(len(x), 0)
            q[g] = pd.qcut(pd.Series(x[g]), 5, labels=False, duplicates="drop").to_numpy() + 1
            QQ[(p_, W)] = q
            pooled = (float(np.nanmean(y[q == 5])) - float(np.nanmean(y[q == 1]))
                      if (q == 5).sum() and (q == 1).sum() else np.nan)
            mv, pre = matched_diff(q, strat, y, weights_out=True)
            PRE[(p_, W)] = pre
            cells.append((p_, W))
            P_(f"{p_:<18}{W:>7}m{int((q==1).sum()):>7}{int((q==5).sum()):>7}"
               f"{pooled:>17,.0f}{mv:>18,.0f}"
               f"{(mv/pooled if pooled and abs(pooled)>1e-9 else np.nan):>16.2f}")
        P_("")

    # ---- the LEVEL-2 control, in the same units
    xnq = FEAT[("NQ_OWN", 15)]
    gq = np.isfinite(xnq)
    qn = np.full(len(xnq), 0)
    qn[gq] = pd.qcut(pd.Series(xnq[gq]), 5, labels=False, duplicates="drop").to_numpy() + 1
    l2_pooled = float(np.nanmean(y[qn == 5])) - float(np.nanmean(y[qn == 1]))
    P_(f"    LEVEL 2 CONTROL - NQ's OWN standardised 15m pre-entry move, same quintile statistic:")
    P_(f"        pooled Q5-Q1 = ${l2_pooled:,.0f}/entry   (matched is undefined: it IS the strata)")

    # ------------------------------------------------------------------ the primary + nulls
    pcell = PRIMARY_CELL
    real, pre = matched_diff(QQ[pcell], strat, y, weights_out=True)
    P_("")
    P_("=" * 126)
    P_(f"=== 2. THE PRIMARY - {pcell[0]} at {pcell[1]}m, matched Q5-Q1 in net dollars per entry")
    P_("=" * 126)
    ynp = y.copy()
    nulls = {k: np.empty(NPERM) for k in cells}
    mx = np.empty(NPERM)
    for b in range(NPERM):
        yp = rng.permutation(ynp)
        vals = []
        for k in cells:
            v = matched_diff_fast(PRE[k], yp) if PRE[k] is not None else np.nan
            nulls[k][b] = v
            if np.isfinite(v):
                vals.append(v)
        mx[b] = max(vals) if vals else np.nan
    p95_own = float(np.nanpercentile(nulls[pcell], 95))
    p95_fam = float(np.nanpercentile(mx, 95))
    P_(f"    REAL matched Q5-Q1                     ${real:,.0f}/entry")
    P_(f"    own-cell null (outcome permutation)    mean ${np.nanmean(nulls[pcell]):,.0f}  "
       f"p95 ${p95_own:,.0f}  -> {100*float(np.nanmean(nulls[pcell] < real)):.1f}th pctile")
    P_(f"    DEPENDENCE-PRESERVING FAMILY null      p95 ${p95_fam:,.0f}   "
       f"(one outcome permutation shared by all {len(cells)} cells, so cross-feature and")
    P_("                                           cross-window correlation is retained)")

    # ------------------------------------------------------------------ prequential
    P_("")
    P_("=" * 126)
    P_(f"=== 3. PREQUENTIAL - {NBLOCK} chronological blocks. Quintile cuts from PRIOR events only.")
    P_("=" * 126)
    xq = FEAT[pcell]
    order = np.arange(len(E))
    bounds = np.linspace(0, len(E), NBLOCK + 1).astype(int)
    P_(f"{'block':<8}{'events':>8}{'dates':>26}{'matched Q5-Q1 $':>18}")
    preq = []
    for bI in range(1, NBLOCK):
        a_, b_ = bounds[bI], bounds[bI + 1]
        tr_m = order < a_
        te = (order >= a_) & (order < b_)
        xt = xq[tr_m]
        gt = np.isfinite(xt)
        if gt.sum() < 200:
            continue
        cuts = np.nanpercentile(xt[gt], [20, 80])
        qb = np.zeros(len(E), int)
        qb[te & np.isfinite(xq) & (xq <= cuts[0])] = 1
        qb[te & np.isfinite(xq) & (xq >= cuts[1])] = 5
        v, _ = matched_diff(qb, np.where(te, strat, -1), y)
        preq.append(v)
        P_(f"{bI:<8}{int(te.sum()):>8}"
           f"{str(E['date'].iloc[a_]) + ' -> ' + str(E['date'].iloc[b_-1]):>26}{v:>18,.0f}")
    pq = float(np.nanmean(preq)) if preq else np.nan
    P_("")
    P_(f"    prequential mean of the matched statistic: ${pq:,.0f}/entry   "
       f"({int(np.sum(np.array(preq) > 0))} of {len(preq)} blocks positive)")

    # ------------------------------------------------------------------ gates
    P_("")
    P_("=" * 126)
    P_("=== 4. GATES - every clause of the preregistered falsifier, checked in code (section 29)")
    P_("=" * 126)
    G = [("G1", "matched Q5-Q1 > 0", f"${real:,.0f}", real > 0),
         ("G2", f"> family-null p95 (${p95_fam:,.0f}), dependence-preserving",
          f"${real:,.0f}", np.isfinite(real) and real > p95_fam),
         ("G3", "survives prequential (mean > 0)", f"${pq:,.0f}", np.isfinite(pq) and pq > 0),
         ("G4", f"beats LEVEL-2 NQ-only control (${l2_pooled:,.0f})",
          f"${real:,.0f}", np.isfinite(real) and real > l2_pooled)]
    P_(f"{'gate':<6}{'spec':<62}{'observed':>14}{'verdict':>10}")
    for g, spec, obsv, ok in G:
        P_(f"{g:<6}{spec:<62}{obsv:>14}{('PASS' if ok else 'FAIL'):>10}")
    allok = all(g[3] for g in G)
    P_("")
    P_(f"    STAGE-A VERDICT: {'INFORMATION FOUND' if allok else 'NO INCREMENTAL INFORMATION'}")

    # ------------------------------------------------------------------ losing sessions
    P_("")
    P_("=" * 126)
    P_("=== 5. THE BOOK-LOSS TARGET - the same statistic on P1's LOSING sessions only")
    P_("=" * 126)
    sp1 = E.groupby("sess")["net"].transform("sum").to_numpy()
    for lab, m_ in (("P1 losing sessions", sp1 < 0), ("P1 winning sessions", sp1 >= 0)):
        v, _ = matched_diff(QQ[pcell], np.where(m_, strat, -1), y)
        P_(f"    {lab:<26}n={int((m_ & (strat>=0)).sum()):>5}   matched Q5-Q1 ${v:>9,.0f}/entry")

    E.to_csv(os.path.join(OUT, "decision_quality_ledger.csv"), index=False)
    pd.DataFrame([dict(prim=k[0], window=k[1],
                       matched=matched_diff(QQ[k], strat, y)[0],
                       null_p95=float(np.nanpercentile(nulls[k], 95))) for k in cells]
                 ).to_csv(os.path.join(OUT, "grid.csv"), index=False)
    P_("")
    P_("    EVIDENCE STATUS (section 9): the entire 2022-07 -> 2026-08 window is")
    P_("    DISCOVERY_CONSUMED; 2026-05-31 -> 07-31 is DIRECTLY_BURNED. Nothing here is FORWARD.")
    P_(f"\n[done {_time.time()-t0:.0f}s]")
    out.close()


if __name__ == "__main__":
    main()
