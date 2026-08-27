"""WE_W101b - IS `XM_CONFLICT` SPECIFIC, OR IS IT ANY 34 % OF SESSIONS?

W101's best-of-27 coin null replaced predictor SIGNS. It does not test the thing that actually
needs testing about XM_CONFLICT: whether the cross-market DISAGREEMENT picks a special subset of
sessions, or whether any 341-of-1,005 subsample of DRIVE sessions would look like this.

Four checks, and any one of them can kill it:
  1. RATE-MATCHED SUBSAMPLE null - 2,000 random 341-session subsets of the DRIVE book.
  2. SESSION-SHIFT null - shift the ES/RTY/YM series by whole sessions and rebuild the signal.
     This destroys WHICH day the disagreement lands on while preserving its own distribution.
  3. Per-year stability and the weekly risk profile it was never measured on.
  4. Correlation with P1 and with the pair - a standalone number is worth nothing if it is the
     incumbent in a hat.
"""
from __future__ import annotations

import itertools
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
from run_we_w51 import classify, session_frames                          # noqa: E402
from run_we_w51c import dd_profile                                       # noqa: E402
from run_we_w97 import votes                                             # noqa: E402
from run_we_w98 import gfills, arm_kw                                    # noqa: E402
from we_channels import build_channels                                   # noqa: E402
from we_fastctx import fast_build_context                                # noqa: E402
from we_lab import spread_profile                                        # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W101_DIRECTION", "out")
W76OUT = os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out")
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
DDT = 20245.0
TICKV = 5.0
NSUB = 2000
NSHIFT = 200
SEED = 1011
XM = {"ES": "runs/SM1M_ES_SUBSTRATE/out/es_1m_2022_2026.parquet",
      "RTY": "runs/SM1M_RTY_SUBSTRATE/out/rty_1m_2022_2026.parquet",
      "YM": "runs/SM1M_YM_SUBSTRATE/out/ym_1m_2022_2026.parquet"}


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "specificity.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    prof = spread_profile()
    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr, sid, lb, fb = D["n"], D["t"], D["sid"], D["lb"], D["fb"]
    o, c, v = D["o"], D["c"], D["v"]
    st_, en_, _ = session_frames(D)
    klass = classify(D, st_, en_)
    mod = ((tarr - tarr.astype("datetime64[D]")).astype("timedelta64[s]")
           .astype(np.int64) // 60).astype(np.int32)
    NSESS = D["n_sess"]
    sdate = pd.to_datetime(D["sess_date"])
    nq = pd.DataFrame({"time": pd.to_datetime(tarr), "nq": c}).set_index("time")
    XD = {}
    for k, path in XM.items():
        d_ = pd.read_parquet(os.path.join(ROOT, path), columns=["time", "close"])
        d_["time"] = pd.to_datetime(d_["time"])
        XD[k] = nq.join(d_.set_index("time")["close"].rename(k), how="left")[k].to_numpy()

    def px_at(mv, arr=None):
        r = np.full(NSESS, np.nan)
        m_ = mod == mv
        r[sid[m_]] = (c if arr is None else arr)[m_]
        return r

    def open_at(mv):
        r = np.full(NSESS, np.nan)
        m_ = mod == mv
        r[sid[m_]] = o[m_]
        return r
    MV = 585                                        # 09:45
    p0930, pT, p1545 = open_at(570), px_at(MV), px_at(945)
    entry = np.full(NSESS, np.nan)
    m_ = mod == MV + 1
    entry[sid[m_]] = o[m_]
    win = np.array([A <= tarr[st_[s]] < B for s in range(NSESS)])
    use = win & np.isfinite(p0930) & np.isfinite(pT) & np.isfinite(p1545) & np.isfinite(entry)
    cst = COMM_RT + TICKV * (float(prof.loc[MV + 1]) + float(prof.loc[945])) / 2.0
    move = (p1545 - entry) * PV
    drive = np.sign(pT - p0930)

    def xm_sign(shift=0):
        """the cross-market composite drive 09:30 -> 09:45, optionally shifted by whole sessions"""
        acc = np.zeros(NSESS); cnt = np.zeros(NSESS)
        for k in XM:
            a_ = px_at(570, XD[k]); b_ = px_at(MV, XD[k])
            r_ = np.log(b_ / a_)
            s_ = pd.Series(r_).rolling(60, min_periods=20).std().shift(1).to_numpy()
            z = r_ / np.maximum(s_, 1e-12)
            if shift:
                z = np.roll(z, shift)
            g = np.isfinite(z)
            acc[g] += z[g]; cnt[g] += 1
        return np.sign(np.where(cnt > 0, acc / np.maximum(cnt, 1), np.nan))
    xs = xm_sign(0)
    base = use & np.isfinite(drive) & (drive != 0) & np.isfinite(xs)
    conf = base & (xs == drive)
    conflict = base & (xs != drive) & (xs != 0)
    real_pt = float((drive[conflict] * move[conflict] - cst).mean())
    real_hit = float((drive[conflict] * move[conflict] > 0).mean())
    K = int(conflict.sum())
    P_("=" * 118)
    P_(f"=== XM_CONFLICT at 09:45: {K} of {int(base.sum())} sessions ({100*K/base.sum():.1f} %), "
       f"${real_pt:,.0f}/trade, hit {100*real_hit:.2f} %")
    P_("=" * 118)

    # ---------------------------------------------------------------- 1. subsample null
    rng = np.random.default_rng(SEED)
    idx = np.flatnonzero(base)
    pnl_all = drive[base] * move[base] - cst
    sub_pt = np.empty(NSUB); sub_hit = np.empty(NSUB)
    for b_ in range(NSUB):
        pick = rng.choice(len(idx), size=K, replace=False)
        sub_pt[b_] = pnl_all[pick].mean()
        sub_hit[b_] = float((pnl_all[pick] + cst > 0).mean())
    p_pt = 100 * float((sub_pt < real_pt).mean())
    p_hit = 100 * float((sub_hit < real_hit).mean())
    P_("")
    P_("  1. RATE-MATCHED SUBSAMPLE NULL - 2,000 random 341-of-1,005 subsets of the DRIVE book.")
    P_(f"     $/trade  real ${real_pt:,.0f}   null mean ${sub_pt.mean():,.0f} "
       f"sd ${sub_pt.std(ddof=1):,.0f}   p95 ${np.percentile(sub_pt,95):,.0f}"
       f"   -> {p_pt:.1f}th percentile")
    P_(f"     hit %    real {100*real_hit:.2f} %  null mean {100*sub_hit.mean():.2f} % "
       f"sd {100*sub_hit.std(ddof=1):.2f}   p95 {100*np.percentile(sub_hit,95):.2f} %"
       f"   -> {p_hit:.1f}th percentile")

    # ---------------------------------------------------------------- 2. session-shift null
    sh_pt = np.empty(NSHIFT); sh_k = np.empty(NSHIFT)
    for b_ in range(NSHIFT):
        s_ = int(rng.integers(20, NSESS - 20))
        xz = xm_sign(s_)
        cf = base & np.isfinite(xz) & (xz != drive) & (xz != 0)
        sh_k[b_] = cf.sum()
        sh_pt[b_] = float((drive[cf] * move[cf] - cst).mean()) if cf.sum() > 30 else np.nan
    good = np.isfinite(sh_pt)
    p_sh = 100 * float((sh_pt[good] < real_pt).mean())
    P_("")
    P_("  2. SESSION-SHIFT NULL - the SAME cross-market construction, landing on other days.")
    P_(f"     null $/trade mean ${np.nanmean(sh_pt):,.0f} sd ${np.nanstd(sh_pt, ddof=1):,.0f}"
       f"   p95 ${np.nanpercentile(sh_pt,95):,.0f}   real ${real_pt:,.0f}"
       f"   -> {p_sh:.1f}th percentile of {int(good.sum())}")
    P_(f"     null selects {sh_k[good].mean():.0f} sessions on average vs the real {K} "
       f"- {'rate-comparable' if abs(sh_k[good].mean()-K) < 0.15*K else 'RATE MISMATCH, read with care'}")

    # ---------------------------------------------------------------- 3. stability + risk
    P_("")
    P_("  3. PER-YEAR and the weekly risk profile it has never been measured on.")
    yr = sdate.year.to_numpy()
    P_(f"     {'year':<7}{'n':>6}{'hit %':>9}{'$/trade':>11}{'net $':>12}")
    yrows = []
    for y in sorted(set(yr[conflict])):
        m2 = conflict & (yr == y)
        pn = drive[m2] * move[m2] - cst
        P_(f"     {y:<7}{int(m2.sum()):>6}{100*float((pn+cst>0).mean()):>8.2f}%"
           f"{pn.mean():>11,.0f}{pn.sum():>12,.0f}")
        yrows.append(dict(year=int(y), n=int(m2.sum()), hit=float((pn + cst > 0).mean()),
                          per_trade=float(pn.mean()), net=float(pn.sum())))
    pd.DataFrame(yrows).to_csv(os.path.join(OUT, "xmconflict_year.csv"), index=False)

    iso = sdate.isocalendar()
    wkall = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).to_numpy()
    sess_in = np.flatnonzero(win)
    ser = np.zeros(NSESS)
    ser[conflict] = drive[conflict] * move[conflict] - cst
    wv = pd.Series(ser[sess_in]).groupby(wkall[sess_in]).sum().to_numpy()
    dp = dd_profile(wv)
    stk = max((len(list(g)) for k_, g in itertools.groupby(wv < 0) if k_), default=0)
    P_("")
    P_(f"     weeks {len(wv)}   weekly ${wv.mean():,.0f}   wk+ {100*(wv>0).mean():.1f} %   "
       f"maxDD ${dp['maxdd']:,.0f}   top5DD ${dp['dd_mean_top5']:,.0f}   worst ${wv.min():,.0f}"
       f"   streak {stk}")
    P_(f"     wk$ @ fixed $20,245 DD = ${wv.mean()*DDT/max(dp['maxdd'],1e-9):,.0f}   "
       f"t = {wv.mean()/max(wv.std(ddof=1)/np.sqrt(len(wv)),1e-9):.2f}")

    # ---------------------------------------------------------------- 4. correlation with P1
    P_("")
    P_("  4. IS IT THE INCUMBENT IN A HAT? Weekly correlation with P1 and with the 2:3 pair.")
    X = fast_build_context(D)
    z = np.load(os.path.join(W76OUT, "mem_ext.npz"))
    mem, bmom, tilt = z["mem"], z["bmom"], z["tilt"]
    CH = build_channels(D, which=["X9a_disp_sessanchor"])
    flatm = tarr >= D["sess_end"][sid] - np.timedelta64(21 * 60, "s")

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    def net_series(tr):
        """`CORRECTION` the first version of this supplement summed x['pnl'] only, which is NET of
        commission but GROSS of spread, and then set it beside XM_CONFLICT which was net of BOTH.
        That is exactly the gross/net mismatch W91/M6 was corrected for. Every series here now
        carries its own contract-weighted spread."""
        w_ = {}
        for x in tr:
            for ts in (x["et"], x["xt"]):
                p_ = pd.Timestamp(ts); m2 = p_.hour * 60 + p_.minute
                w_[m2] = w_.get(m2, 0.0) + x["u"]
        rate = TICKV * sum(float(prof.get(m2, 3.0)) * q for m2, q in w_.items()) /             max(sum(w_.values()), 1e-9)
        s_ = np.zeros(NSESS)
        for x in tr:
            si = int(sid[i_of(x["et"])])
            if win[si]:
                s_[si] += x["pnl"] - rate * x["u"]
        return s_, rate

    def obj(chan):
        vl, _ = votes(D, mem, bmom, tilt, X, chan)
        p = vl.astype(np.int8)
        bb = fills_daily(D, p, halt=1300, target=1000)
        ee = np.array([i_of(x["et"]) for x in bb if A <= np.datetime64(x["et"]) < B])
        sc, _ = causal_score(X, ee, window=WIN)
        return net_series(gfills(D, p, np.where(sc >= 3, 2, 1).astype(np.int8),
                                 **arm_kw("PCT", 1.183)))
    sP1, rP1 = obj(bmom)
    sX9, rX9 = obj(CH["X9a_disp_sessanchor"])
    sBM, rBM = net_series(gfills(D, np.where(flatm, 0, bmom).astype(np.int8), None,
                                 **arm_kw("PCT", 1.0)))
    P_(f"     spread charged per contract RT: P1 ${rP1:.2f}, X9a ${rX9:.2f}, BMOM ${rBM:.2f}, "
       f"XM_CONFLICT ${cst - COMM_RT:.2f} + ${COMM_RT:.2f} commission")
    sPAIR = (2 * sBM + 3 * sX9) / 5.0

    def wkv(x):
        return pd.Series(x[sess_in]).groupby(wkall[sess_in]).sum().to_numpy()
    wc = wkv(ser)
    crows = []
    P_(f"     {'vs':<10}{'weekly rho':>12}{'z':>8}{'daily rho':>12}")
    for nm2, s2 in (("P1", sP1), ("X9a", sX9), ("BMOM", sBM), ("PAIR 2:3", sPAIR)):
        w2 = wkv(s2)
        r_ = float(np.corrcoef(wc, w2)[0, 1])
        rd = float(np.corrcoef(ser[sess_in], s2[sess_in])[0, 1])
        P_(f"     {nm2:<10}{r_:>12.4f}{r_*np.sqrt(len(wc)-3):>8.2f}{rd:>12.4f}")
        crows.append(dict(vs=nm2, weekly_rho=r_, daily_rho=rd))
    pd.DataFrame(crows).to_csv(os.path.join(OUT, "xmconflict_corr.csv"), index=False)

    # portfolio marginal value: P1 + this, at matched income
    P_("")
    P_("     MARGINAL PORTFOLIO VALUE - P1/PCT alone vs P1/PCT + XM_CONFLICT scaled to")
    P_("     contribute the same weekly income as P1 does (income-matched, W97's convention):")
    wp = wkv(sP1)
    sc_ = wp.mean() / wc.mean() if wc.mean() else np.nan
    P_(f"     {'object':<26}{'wk$':>9}{'wk+%':>8}{'maxDD':>10}{'top5':>9}{'wk$@fixDD':>11}")
    for nm2, w2 in (("P1/PCT", wp), ("XM_CONFLICT (scaled)", wc * sc_),
                    ("P1/PCT + XM_CONFLICT", wp + wc * sc_)):
        d2 = dd_profile(w2)
        P_(f"     {nm2:<26}{w2.mean():>9,.0f}{100*(w2>0).mean():>7.1f}%{d2['maxdd']:>10,.0f}"
           f"{d2['dd_mean_top5']:>9,.0f}{w2.mean()*DDT/max(d2['maxdd'],1e-9):>11,.0f}")
    P_(f"\n[done {_time.time()-t0:.0f}s]")
    out.close()


if __name__ == "__main__":
    main()
