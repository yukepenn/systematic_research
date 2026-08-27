"""WE_W110 - XM_CONFLICT forensic health, part 2: LOSS DIVERSIFICATION and TAIL-WINNER STATE.

Spec: runs/WE_W110_XMDIVERSE/spec.yaml, committed BEFORE this ran (f01b5fe).

W105 gave the authoritative period table, the concentration profile and the ordinary weekly
correlation. It left the two questions that actually decide whether the candidate portfolio
survives, and directive V5 names both:

  section 9 - rho rising to +0.464 over six months only matters economically if DOWNSIDE
              co-movement rose. If both engines simply earn in the same GOOD weeks, that is a
              different and much less serious fact.
  section 8 - 20 of 348 trades carrying 85 % of the money is only a disqualifier if those winners
              are unrelated accidents. If they share a causal PRE-ENTRY state, concentration is
              the mechanism working, not a warning.

MEASUREMENT ONLY. This wave may not create a parameter, a filter or a threshold.
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
from run_we_w51c import dd_profile                                       # noqa: E402
from run_we_w97 import votes                                             # noqa: E402
from run_we_w98 import gfills, arm_kw                                    # noqa: E402
from we_fastctx import fast_build_context                                # noqa: E402
from we_lab import spread_profile                                        # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W110_XMDIVERSE", "out")
os.makedirs(OUT, exist_ok=True)
W76OUT = os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out")
CAL = os.path.join(ROOT, "research", "04_complementary_family", "c01_announcement_calendar.csv")
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
DDT = 20245.0
TICKV = 5.0
ANCH_TRUE, ANCH_OLD, DEC, ENTM, EXITM = 571, 570, 585, 586, 945
ONSTART = 1081                  # 18:01, the first bar of a CME session
XM = {"ES": "runs/SM1M_ES_SUBSTRATE/out/es_1m_2022_2026.parquet",
      "RTY": "runs/SM1M_RTY_SUBSTRATE/out/rty_1m_2022_2026.parquet",
      "YM": "runs/SM1M_YM_SUBSTRATE/out/ym_1m_2022_2026.parquet"}


def maxdd(x):
    e = np.cumsum(x); return float(np.max(np.maximum.accumulate(e) - e))


def dd_dur(x):
    e = np.cumsum(x); pk = np.maximum.accumulate(e)
    under = e < pk - 1e-9
    best = cur = 0
    for u in under:
        cur = cur + 1 if u else 0
        best = max(best, cur)
    return best


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "xmdiverse.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    prof = spread_profile()
    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr, sid = D["n"], D["t"], D["sid"]
    o, c, h, l, v = D["o"], D["c"], D["h"], D["l"], D["v"]
    st_, en_, _ = session_frames(D)
    mod = ((tarr - tarr.astype("datetime64[D]")).astype("timedelta64[s]")
           .astype(np.int64) // 60).astype(np.int32)
    NS = D["n_sess"]
    sdate = pd.to_datetime(D["sess_date"])
    iso = sdate.isocalendar()
    wkall = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).to_numpy()
    win = np.array([A <= tarr[st_[s]] < B for s in range(NS)])
    sess_in = np.flatnonzero(win)
    wk = wkall[sess_in]
    P_(f"    substrate {n:,} bars / {len(sess_in):,} in-window sessions [{_time.time()-t0:.0f}s]")

    nqf = pd.DataFrame({"time": pd.to_datetime(tarr), "nq": c}).set_index("time")
    XD = {}
    for k, path in XM.items():
        d_ = pd.read_parquet(os.path.join(ROOT, path), columns=["time", "close"])
        d_["time"] = pd.to_datetime(d_["time"])
        XD[k] = nqf.join(d_.set_index("time")["close"].rename(k), how="left")[k].to_numpy()

    def at(mv, arr, uo=False):
        r = np.full(NS, np.nan); ix = np.full(NS, -1)
        m_ = mod == mv
        r[sid[m_]] = (o[m_] if uo else arr[m_]); ix[sid[m_]] = np.flatnonzero(m_)
        return r, ix

    def zof(arr, anchor):
        aa, _ = at(anchor, arr); bb, _ = at(DEC, arr)
        with np.errstate(divide="ignore", invalid="ignore"):
            r_ = np.log(bb / aa)
        s_ = pd.Series(r_).rolling(60, min_periods=20).std().shift(1).to_numpy()
        return r_ / np.maximum(s_, 1e-12), s_

    def build(anchor):
        pa, _ = at(anchor, o, True)
        pdc, _ = at(DEC, c)
        pe, ient = at(ENTM, o, True)
        px, iexit = at(EXITM, c)
        dr = np.sign(pdc - pa)
        acc = np.zeros(NS); cnt = np.zeros(NS)
        for k in XM:
            zz, _ = zof(XD[k], anchor)
            g = np.isfinite(zz); acc[g] += zz[g]; cnt[g] += 1
        comp = np.where(cnt > 0, acc / np.maximum(cnt, 1), np.nan)
        xs = np.sign(comp)
        okm = (win & np.isfinite(pa) & np.isfinite(pdc) & np.isfinite(pe) & np.isfinite(px) &
               np.isfinite(xs) & (dr != 0) & (xs != 0))
        return dr, okm & (xs != dr), pe, px, ient, iexit, comp

    # ------------------------------------------------------------------ reproduction gate
    P_("")
    P_("=" * 126)
    P_("=== 0. REPRODUCTION GATE - the canonical object, or no table is issued")
    P_("=" * 126)
    _, cf_old, *_ = build(ANCH_OLD)
    dr, cf, pent, pexit, ient, iexit, comp = build(ANCH_TRUE)
    n_old, n_new = int(cf_old.sum()), int(cf.sum())
    P_(f"    anchor {ANCH_OLD} (bar stamped 09:30) N = {n_old}   expected 342")
    P_(f"    anchor {ANCH_TRUE} (bar stamped 09:31, CANONICAL) N = {n_new}   expected 348")
    if not (n_old == 342 and n_new == 348):
        P_("    GATE FAILED - the substrate has moved. Nothing below would be quotable.")
        out.close(); return
    P_("    PASS.")

    cst = COMM_RT + TICKV * (float(prof.loc[ENTM]) + float(prof.loc[EXITM])) / 2.0
    xm_s = np.zeros(NS)
    idx = np.flatnonzero(cf)
    for s in idx:
        xm_s[s] = int(dr[s]) * (pexit[s] - pent[s]) * PV - cst

    # ------------------------------------------------------------------ P1/PCT
    X = fast_build_context(D)
    z = np.load(os.path.join(W76OUT, "mem_ext.npz"))
    mem, bmom, tilt = z["mem"], z["bmom"], z["tilt"]

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))
    vl, _ = votes(D, mem, bmom, tilt, X, bmom)
    p1 = vl.astype(np.int8)
    bb = fills_daily(D, p1, halt=1300, target=1000)
    ee = np.array([i_of(x["et"]) for x in bb if A <= np.datetime64(x["et"]) < B])
    sc, _ = causal_score(X, ee, window=WIN)
    trP = gfills(D, p1, np.where(sc >= 3, 2, 1).astype(np.int8), **arm_kw("PCT", 1.183))
    w_ = {}
    for x in trP:
        for ts in (x["et"], x["xt"]):
            pp = pd.Timestamp(ts); m2 = pp.hour * 60 + pp.minute
            w_[m2] = w_.get(m2, 0.0) + x["u"]
    rP = TICKV * sum(float(prof.get(m2, 3.0)) * q for m2, q in w_.items()) / max(sum(w_.values()), 1)
    p1_s = np.zeros(NS)
    for x in trP:
        si = int(sid[i_of(x["et"])])
        if win[si]:
            p1_s[si] += x["pnl"] - rP * x["u"]
    P_(f"    P1/PCT rebuilt: {len(trP):,} trades, spread ${rP:.2f}/ctrRT [{_time.time()-t0:.0f}s]")

    WP = pd.Series(p1_s[sess_in]).groupby(wk).sum()
    WX = pd.Series(xm_s[sess_in]).groupby(wk).sum()
    ACT = pd.Series((xm_s[sess_in] != 0).astype(float)).groupby(wk).sum()
    wkidx = WP.index.to_numpy()
    P1W, XMW, ACTW = WP.to_numpy(), WX.to_numpy(), ACT.to_numpy()
    NW = len(P1W)
    P_(f"    {NW} weeks. P1/PCT ${P1W.mean():,.0f}/wk, XM ${XMW.mean():,.0f}/wk, "
       f"XM active in {int((ACTW>0).sum())} of them.")
    pd.DataFrame(dict(week=wkidx, p1=P1W, xm=XMW, xm_trades=ACTW)).to_csv(
        os.path.join(OUT, "weekly.csv"), index=False)

    # ------------------------------------------------------------------ 1. rolling rho
    P_("")
    P_("=" * 126)
    P_("=== 1. ROLLING CORRELATION - the full path, per section 9, not one number")
    P_("=" * 126)
    sp, sx = pd.Series(P1W), pd.Series(XMW)
    P_(f"{'window':<10}{'last':>9}{'min':>9}{'p25':>9}{'median':>9}{'p75':>9}{'max':>9}"
       f"{'frac > +0.30':>14}")
    roll = {}
    for W_ in (13, 26, 52):
        rr = sp.rolling(W_).corr(sx).dropna().to_numpy()
        roll[W_] = rr
        P_(f"{str(W_)+'-week':<10}{rr[-1]:>9.3f}{rr.min():>9.3f}"
           f"{np.percentile(rr,25):>9.3f}{np.median(rr):>9.3f}{np.percentile(rr,75):>9.3f}"
           f"{rr.max():>9.3f}{100*float((rr>0.30).mean()):>13.1f}%")
    P_("")
    P_(f"    FULL-WINDOW rho = {np.corrcoef(P1W, XMW)[0,1]:+.3f}")
    P_(f"    TRAILING 26 WEEKS rho = {np.corrcoef(P1W[-26:], XMW[-26:])[0,1]:+.3f}   "
       f"(W105 reported +0.464)")
    pd.DataFrame({f"roll{k}": pd.Series(v) for k, v in roll.items()}).to_csv(
        os.path.join(OUT, "rolling_rho.csv"), index=False)

    # ------------------------------------------------------------------ 2. downside stats
    def stats_of(p1w, xmw, actw):
        g = np.isfinite(p1w) & np.isfinite(xmw)
        a, b = p1w[g], xmw[g]
        d = {}
        d["rho"] = float(np.corrcoef(a, b)[0, 1])
        m = a < 0
        d["rho|P1<0"] = float(np.corrcoef(a[m], b[m])[0, 1]) if m.sum() > 5 else np.nan
        m2 = b < 0
        d["rho|XM<0"] = float(np.corrcoef(a[m2], b[m2])[0, 1]) if m2.sum() > 5 else np.nan
        d["P(XM<0|P1<0)"] = float((b[m] < 0).mean()) if m.sum() else np.nan
        d["P(P1<0|XM<0)"] = float((a[m2] < 0).mean()) if m2.sum() else np.nan
        qa, qb = np.percentile(a, 10), np.percentile(b, 10)
        d["worst-decile overlap"] = float(((a <= qa) & (b <= qb)).mean())
        wa = set(np.argsort(a)[:10].tolist()); wb = set(np.argsort(b)[:10].tolist())
        d["joint worst-10"] = float(len(wa & wb))
        lo = a <= qa
        d["tail beta"] = (float(np.polyfit(a[lo], b[lo], 1)[0]) if lo.sum() > 5 else np.nan)
        d["all-week beta"] = float(np.polyfit(a, b, 1)[0])
        act = actw > 0
        d["rho|XM active"] = (float(np.corrcoef(a[act], b[act])[0, 1])
                              if act.sum() > 5 else np.nan)
        sa = a.std(ddof=1); sb = b.std(ddof=1)
        wgt = (1.0 / max(sa, 1e-9)) / ((1.0 / max(sa, 1e-9)) + (1.0 / max(sb, 1e-9)))
        cb = wgt * a + (1 - wgt) * b
        d["joint maxDD"] = maxdd(cb)
        d["joint DD weeks"] = float(dd_dur(cb))
        return d

    real = stats_of(P1W, XMW, ACTW)
    shifts = []
    for k in range(1, NW):
        shifts.append(stats_of(P1W, np.roll(XMW, k), np.roll(ACTW, k)))
    SH = pd.DataFrame(shifts)
    P_("")
    P_("=" * 126)
    P_("=== 2. LOSS DIVERSIFICATION - every statistic against a CIRCULAR-SHIFT null")
    P_(f"===    {NW-1} shifts of the XM weekly vector against P1's. Both marginals and both")
    P_("===    autocorrelation structures are preserved exactly; only the alignment is destroyed.")
    P_("=" * 126)
    P_(f"{'statistic':<24}{'REAL':>11}{'null mean':>11}{'null p5':>10}{'null p95':>10}"
       f"{'percentile':>12}{'reading':>26}")
    read = {
        "rho": "higher = more coupled",
        "rho|P1<0": "higher = losses coupled",
        "rho|XM<0": "higher = losses coupled",
        "P(XM<0|P1<0)": "higher = XM loses too",
        "P(P1<0|XM<0)": "higher = P1 loses too",
        "worst-decile overlap": "higher = tails coincide",
        "joint worst-10": "higher = tails coincide",
        "tail beta": "higher = worse in P1 tails",
        "all-week beta": "reference for tail beta",
        "rho|XM active": "the honest conditional",
        "joint maxDD": "LOWER is better",
        "joint DD weeks": "LOWER is better",
    }
    rows = []
    for k in read:
        rv = real[k]; nv = SH[k].to_numpy()
        pc = 100 * float(np.nanmean(nv < rv))
        P_(f"{k:<24}{rv:>11.3f}{np.nanmean(nv):>11.3f}{np.nanpercentile(nv,5):>10.3f}"
           f"{np.nanpercentile(nv,95):>10.3f}{pc:>11.1f}th{read[k]:>26}")
        rows.append(dict(stat=k, real=rv, null_mean=float(np.nanmean(nv)),
                         p5=float(np.nanpercentile(nv, 5)),
                         p95=float(np.nanpercentile(nv, 95)), pctile=pc))
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "downside.csv"), index=False)

    P_("")
    P_("    UNCONDITIONAL RATES, for reading the conditionals above:")
    P_(f"        P(P1 < 0) = {float((P1W<0).mean()):.3f}     P(XM < 0) = {float((XMW<0).mean()):.3f}")
    P_(f"        so independence would give P(XM<0|P1<0) = {float((XMW<0).mean()):.3f}")

    # ---- the same split, first half vs last half, to see whether coupling actually moved
    P_("")
    P_("    HAS THE COUPLING ACTUALLY MOVED? Same statistics on the first and last 26 weeks:")
    P_(f"{'statistic':<24}{'first 26w':>12}{'last 26w':>12}{'full':>12}")
    f26 = stats_of(P1W[:26], XMW[:26], ACTW[:26])
    l26 = stats_of(P1W[-26:], XMW[-26:], ACTW[-26:])
    for k in ("rho", "rho|P1<0", "P(XM<0|P1<0)", "worst-decile overlap", "tail beta"):
        P_(f"{k:<24}{f26[k]:>12.3f}{l26[k]:>12.3f}{real[k]:>12.3f}")

    # ------------------------------------------------------------------ 3. tail winners
    P_("")
    P_("=" * 126)
    P_("=== 3. THE TAIL WINNERS - is there a common CAUSAL PRE-ENTRY state?")
    P_("===    Every feature is known at or before 09:45 on the trade's own session. No MFE, no")
    P_("===    MAE, no realized move: using the future path would make the answer circular.")
    P_("=" * 126)
    znq, snq = zof(c, ANCH_TRUE)
    pa_, _ = at(ANCH_TRUE, o, True)
    pdc_, _ = at(DEC, c)
    drive_pts = np.abs(pdc_ - pa_)
    mvol = np.zeros(NS)
    mm = (mod >= ANCH_TRUE) & (mod <= DEC)
    np.add.at(mvol, sid[mm], v[mm])
    mvol_r = mvol / np.maximum(pd.Series(mvol).rolling(250, min_periods=60)
                               .median().shift(1).to_numpy(), 1e-9)
    prevc = np.full(NS, np.nan)
    lastc, _ = at(1020, c)                       # the 17:00 bar closes the prior session
    prevc[1:] = lastc[:-1]
    gap = np.abs(pa_ - prevc)
    onh = np.full(NS, -np.inf); onl = np.full(NS, np.inf)
    om = (mod >= ONSTART) | (mod < ANCH_TRUE)
    np.maximum.at(onh, sid[om], h[om]); np.minimum.at(onl, sid[om], l[om])
    onr = np.where(np.isfinite(onh) & np.isfinite(onl) & (onh > -np.inf), onh - onl, np.nan)
    onr_r = onr / np.maximum(pd.Series(onr).rolling(250, min_periods=60)
                             .median().shift(1).to_numpy(), 1e-9)
    cal = pd.read_csv(CAL)
    cald = set(pd.to_datetime(cal["date"]).dt.date.tolist())
    ann = np.array([sdate[s].date() in cald for s in range(NS)])

    F = pd.DataFrame(dict(
        sess=idx,
        pnl=xm_s[idx],
        drive_pts=drive_pts[idx],
        abs_comp_z=np.abs(comp[idx]),
        divergence=np.abs(znq[idx] - comp[idx]),
        nq_sigma=snq[idx],
        morn_vol_rel=mvol_r[idx],
        gap_pts=gap[idx],
        on_range_rel=onr_r[idx],
        is_long=(dr[idx] > 0).astype(float),
        dow=np.array([sdate[s].dayofweek for s in idx], float),
        is_ann=ann[idx].astype(float),
    ))
    F["date"] = [sdate[s].date() for s in idx]
    F.to_csv(os.path.join(OUT, "trade_features.csv"), index=False)
    FEATS = ["drive_pts", "abs_comp_z", "divergence", "nq_sigma", "morn_vol_rel",
             "gap_pts", "on_range_rel", "is_long", "dow", "is_ann"]
    rng = np.random.default_rng(110)

    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler

    for TOPK in (20, 10, 5):
        y = np.zeros(len(F), bool)
        y[np.argsort(-F["pnl"].to_numpy())[:TOPK]] = True
        P_("")
        P_(f"    --- TOP {TOPK} WINNERS ({100*F['pnl'].to_numpy()[y].sum()/F['pnl'].sum():.0f} % "
           f"of net) vs the other {len(F)-TOPK} ---")
        P_(f"{'feature':<16}{'top mean':>12}{'rest mean':>12}{'top med':>12}{'rest med':>12}"
           f"{'perm p':>9}")
        for f_ in FEATS:
            x = F[f_].to_numpy()
            g = np.isfinite(x)
            d0 = float(x[g & y].mean() - x[g & ~y].mean())
            nul = np.empty(2000)
            yy = y[g]; xx = x[g]
            for b in range(2000):
                p = rng.permutation(yy)
                nul[b] = float(xx[p].mean() - xx[~p].mean())
            pv = float(np.mean(np.abs(nul) >= abs(d0)))
            P_(f"{f_:<16}{x[g&y].mean():>12.3f}{x[g&~y].mean():>12.3f}"
               f"{np.median(x[g&y]):>12.3f}{np.median(x[g&~y]):>12.3f}{pv:>9.3f}"
               + ("  *" if pv < 0.05 else ""))

        Xf = F[FEATS].to_numpy()
        g = np.all(np.isfinite(Xf), axis=1)
        Xg, yg = Xf[g], y[g]
        sc_ = StandardScaler().fit(Xg)
        Xs = sc_.transform(Xg)
        pred = np.empty(len(yg))
        for i in range(len(yg)):
            m_ = np.ones(len(yg), bool); m_[i] = False
            if yg[m_].sum() < 2:
                pred[i] = np.nan; continue
            lr = LogisticRegression(C=0.5, max_iter=2000)
            lr.fit(Xs[m_], yg[m_])
            pred[i] = lr.predict_proba(Xs[i:i + 1])[0, 1]
        ok = np.isfinite(pred)

        def _auc(p, yy):
            r = pd.Series(p).rank().to_numpy()
            n1, n0 = int(yy.sum()), int((~yy).sum())
            return (r[yy].sum() - n1 * (n1 + 1) / 2.0) / max(n1 * n0, 1)
        a0 = _auc(pred[ok], yg[ok])
        nul = np.array([_auc(pred[ok], rng.permutation(yg[ok])) for _ in range(2000)])
        P_("")
        P_(f"    LEAVE-ONE-OUT logistic AUC = {a0:.3f}   permutation null mean "
           f"{nul.mean():.3f} p95 {np.percentile(nul,95):.3f}"
           f"  -> {100*float((nul<a0).mean()):.1f}th percentile   "
           f"{'MECHANISM-CONSISTENT' if a0 > np.percentile(nul,95) else 'NOT IDENTIFIABLE'}")

    P_("")
    P_(f"[done {_time.time()-t0:.0f}s]")
    out.close()


if __name__ == "__main__":
    main()
