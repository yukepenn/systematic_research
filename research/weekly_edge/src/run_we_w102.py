"""WE_W102 - DOES `XM_CONFLICT` SURVIVE BECOMING AN ENGINE?

Spec: runs/WE_W102_XMENGINE/spec.yaml, committed BEFORE this ran.

W101 measured a FORECAST: one entry at 09:46, one exit at 15:45, no stop, no box, no sizing, and
an adverse excursion nobody ever looked at. This wave gives it an exit policy and re-measures.

    X0_HOLD     hold to 15:45                                    (W101, the control)
    X2_ORSTOP   exit at the opposite extreme of the 09:30-09:45 opening range   [0 parameters]
    X3_FLIP     exit if price closes back through the 09:30 open                [0 parameters]
    X1_ATR2     exit at entry -/+ 2.0 x ATR20 at 09:45                          [1 parameter]
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
from we_fastctx import fast_build_context                                # noqa: E402
from we_lab import spread_profile                                        # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W102_XMENGINE", "out")
os.makedirs(OUT, exist_ok=True)
W76OUT = os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out")
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
DDT = 20245.0
TICKV = 5.0
MV = 585           # 09:45 decision
ENT = 586          # 09:46 fill
EXITM = 945        # 15:45
XM = {"ES": "runs/SM1M_ES_SUBSTRATE/out/es_1m_2022_2026.parquet",
      "RTY": "runs/SM1M_RTY_SUBSTRATE/out/rty_1m_2022_2026.parquet",
      "YM": "runs/SM1M_YM_SUBSTRATE/out/ym_1m_2022_2026.parquet"}
ARMS = ("X0_HOLD", "X2_ORSTOP", "X3_FLIP", "X1_ATR2")


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "engine.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    prof = spread_profile()
    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr, sid, lb, fb = D["n"], D["t"], D["sid"], D["lb"], D["fb"]
    o, c, h, l, v = D["o"], D["c"], D["h"], D["l"], D["v"]
    st_, en_, _ = session_frames(D)
    klass = classify(D, st_, en_)
    mod = ((tarr - tarr.astype("datetime64[D]")).astype("timedelta64[s]")
           .astype(np.int64) // 60).astype(np.int32)
    NSESS = D["n_sess"]
    sdate = pd.to_datetime(D["sess_date"])
    iso = sdate.isocalendar()
    wkall = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).to_numpy()
    win = np.array([A <= tarr[st_[s]] < B for s in range(NSESS)])
    sess_in = np.flatnonzero(win)
    bidx = np.arange(n) - st_[sid]
    nq = pd.DataFrame({"time": pd.to_datetime(tarr), "nq": c}).set_index("time")
    XD = {}
    for k, path in XM.items():
        d_ = pd.read_parquet(os.path.join(ROOT, path), columns=["time", "close"])
        d_["time"] = pd.to_datetime(d_["time"])
        XD[k] = nq.join(d_.set_index("time")["close"].rename(k), how="left")[k].to_numpy()

    def at(mv, arr):
        r = np.full(NSESS, np.nan); ix = np.full(NSESS, -1)
        m_ = mod == mv
        r[sid[m_]] = arr[m_]; ix[sid[m_]] = np.flatnonzero(m_)
        return r, ix
    p0930, i0930 = at(570, o)
    p0945, i0945 = at(MV, c)
    pent, ient = at(ENT, o)
    pexit, iexit = at(EXITM, c)
    # opening range 09:30-09:45 inclusive of the decision bar
    orh = np.full(NSESS, -np.inf); orl = np.full(NSESS, np.inf)
    ii = np.flatnonzero((mod >= 570) & (mod <= MV))
    np.maximum.at(orh, sid[ii], h[ii]); np.minimum.at(orl, sid[ii], l[ii])
    # ATR20 at 09:45
    tr_ = np.maximum(h, np.r_[c[0], c[:-1]]) - np.minimum(l, np.r_[c[0], c[:-1]])
    tr_[fb] = (h - l)[fb]
    atr = pd.Series(tr_).rolling(20, min_periods=20).mean().to_numpy()
    atr[bidx < 19] = np.nan
    atr45, _ = at(MV, atr)

    def xm_sign():
        acc = np.zeros(NSESS); cnt = np.zeros(NSESS)
        for k in XM:
            a_, _ = at(570, XD[k]); b_, _ = at(MV, XD[k])
            r_ = np.log(b_ / a_)
            s_ = pd.Series(r_).rolling(60, min_periods=20).std().shift(1).to_numpy()
            z = r_ / np.maximum(s_, 1e-12)
            g = np.isfinite(z)
            acc[g] += z[g]; cnt[g] += 1
        return np.sign(np.where(cnt > 0, acc / np.maximum(cnt, 1), np.nan))
    xs = xm_sign()
    drive = np.sign(p0945 - p0930)
    ok = (win & np.isfinite(p0930) & np.isfinite(p0945) & np.isfinite(pent) &
          np.isfinite(pexit) & np.isfinite(atr45) & np.isfinite(xs) & (drive != 0) & (xs != 0))
    take = ok & (xs != drive)
    P_(f"    substrate {n:,} bars / {int(win.sum()):,} in-window sessions; "
       f"XM_CONFLICT fires on {int(take.sum()):,} ({100*take.sum()/max(ok.sum(),1):.1f} % of "
       f"{int(ok.sum()):,} eligible)  [{_time.time()-t0:.0f}s]")

    # ------------------------------------------------------------------ the four arms
    def build(arm):
        """one trade per firing session; returns per-session dicts with MAE/MFE and exit reason"""
        rows = []
        for s in np.flatnonzero(take):
            d_ = int(drive[s]); a_, b_ = int(ient[s]), int(iexit[s])
            if a_ < 0 or b_ < a_:
                continue
            epx = o[a_]
            hh, ll = h[a_:b_ + 1], l[a_:b_ + 1]
            run_max = np.maximum.accumulate(hh); run_min = np.minimum.accumulate(ll)
            stop = None
            if arm == "X2_ORSTOP":
                stop = orl[s] if d_ > 0 else orh[s]
            elif arm == "X1_ATR2":
                stop = epx - d_ * 2.0 * atr45[s]
            xi, xpx, why = b_, c[b_], "TIME"
            if stop is not None:
                hit = np.flatnonzero(ll <= stop) if d_ > 0 else np.flatnonzero(hh >= stop)
                if len(hit):
                    j = a_ + int(hit[0])
                    xi = j
                    xpx = min(o[j], stop) if d_ > 0 else max(o[j], stop)
                    why = "STOP"
            elif arm == "X3_FLIP":
                cc = c[a_:b_ + 1]
                bad = np.flatnonzero(cc < p0930[s]) if d_ > 0 else np.flatnonzero(cc > p0930[s])
                if len(bad):
                    j = a_ + int(bad[0])
                    if j + 1 <= b_:
                        xi, xpx, why = j + 1, o[j + 1], "FLIP"
            k = xi - a_
            mae = (run_min[k] - epx) * d_ * PV if d_ > 0 else (epx - run_max[k]) * PV
            mfe = (run_max[k] - epx) * d_ * PV if d_ > 0 else (epx - run_min[k]) * PV
            cst = COMM_RT + TICKV * (float(prof.loc[int(mod[a_])]) +
                                     float(prof.loc[int(mod[xi])])) / 2.0
            rows.append(dict(sess=int(s), d=d_, ei=a_, xi=xi, epx=epx, xpx=xpx,
                             pnl=d_ * (xpx - epx) * PV - cst, mae=mae, mfe=mfe, why=why,
                             mins=xi - a_, cost=cst))
        return rows
    ENGB = {a_: build(a_) for a_ in ARMS}
    # determinism
    det = all(build(a_) == ENGB[a_] for a_ in ARMS)
    P_(f"    LIVE-CHECK determinism: rebuilding every arm reproduces it exactly ... "
       f"{'PASS' if det else 'FAIL'}")
    P_(f"    LIVE-CHECK no lookahead: entry index is the 09:46 bar and its price is that bar's "
       f"OPEN; every stop level (opening-range extreme, 09:30 open, ATR20 at 09:45) is fixed")
    P_(f"                 before 09:46; exits fill at the breaching bar's open or the level, "
       f"whichever is worse for us.")
    P_(f"    LIVE-CHECK inputs at 09:45 are ES / RTY / YM LAST prices - available in real time, "
       f"no vendor file, no daily download.")

    # ------------------------------------------------------------------ dashboard
    def ser_of(rows):
        s_ = np.zeros(NSESS)
        for r in rows:
            s_[r["sess"]] += r["pnl"]
        return s_

    def dash(rows, name, mask=None):
        s_ = ser_of(rows)
        m = np.ones(len(sess_in), bool) if mask is None else mask
        wv = pd.Series(s_[sess_in][m]).groupby(wkall[sess_in][m]).sum().to_numpy()
        dp = dd_profile(wv)
        stk = max((len(list(g)) for k_, g in itertools.groupby(wv < 0) if k_), default=0)
        cq = max(1, int(round(0.05 * len(wv))))
        pn = np.array([r["pnl"] for r in rows])
        mins = np.array([r["mins"] for r in rows])
        return dict(name=name, trades=len(rows), net=float(pn.sum()),
                    per_trade=float(pn.mean()), hit=100 * float((pn > 0).mean()),
                    weekly=float(wv.mean()),
                    weekly_fixdd=float(wv.mean()) * DDT / max(dp["maxdd"], 1e-9),
                    poswk=100 * float((wv > 0).mean()),
                    posday=100 * float((s_[sess_in][m] > 0).mean()),
                    maxdd=dp["maxdd"], top5=dp["dd_mean_top5"], worst_wk=float(wv.min()),
                    cvar5=float(np.sort(wv)[:cq].mean()), streak=int(stk),
                    worst_trade=float(pn.min()), best_trade=float(pn.max()),
                    mae_mean=float(np.mean([r["mae"] for r in rows])),
                    mae_worst=float(np.min([r["mae"] for r in rows])),
                    mfe_mean=float(np.mean([r["mfe"] for r in rows])),
                    ctrmin=float(mins.sum()), meanmin=float(mins.mean()),
                    ppcm=float(pn.sum()) / max(mins.sum(), 1e-9),
                    t=float(wv.mean()) / max(wv.std(ddof=1) / np.sqrt(max(len(wv), 2)), 1e-9))
    P_("")
    P_("=" * 126)
    P_("=== THE FOUR EXIT ARMS. MAE is the number W101 never reported.")
    P_("=" * 126)
    P_(f"{'arm':<11}{'trades':>7}{'$/trade':>9}{'hit%':>7}{'net $':>10}{'wk$':>8}"
       f"{'wk$@fixDD':>11}{'wk+%':>7}{'maxDD':>9}{'top5':>9}{'worst wk':>10}"
       f"{'mean MAE':>10}{'worst MAE':>11}{'mean min':>10}{'t':>6}")
    rows = []
    for a_ in ARMS:
        dd = dash(ENGB[a_], a_)
        rows.append(dd)
        P_(f"{a_:<11}{dd['trades']:>7,}{dd['per_trade']:>9,.0f}{dd['hit']:>6.1f}%"
           f"{dd['net']:>10,.0f}{dd['weekly']:>8,.0f}{dd['weekly_fixdd']:>11,.0f}"
           f"{dd['poswk']:>6.1f}%{dd['maxdd']:>9,.0f}{dd['top5']:>9,.0f}"
           f"{dd['worst_wk']:>10,.0f}{dd['mae_mean']:>10,.0f}{dd['mae_worst']:>11,.0f}"
           f"{dd['meanmin']:>10.0f}{dd['t']:>6.2f}")
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "arms.csv"), index=False)
    P_("")
    P_(f"{'arm':<11}{'exit reasons':<40}{'worst trade':>13}{'best trade':>12}"
       f"{'mean MFE':>10}{'$/ctr-min':>11}")
    for a_ in ARMS:
        rr = ENGB[a_]
        why = pd.Series([r["why"] for r in rr]).value_counts()
        dd = [x for x in rows if x["name"] == a_][0]
        P_(f"{a_:<11}{', '.join(f'{k} {v}' for k, v in why.items()):<40}"
           f"{dd['worst_trade']:>13,.0f}{dd['best_trade']:>12,.0f}{dd['mfe_mean']:>10,.0f}"
           f"{dd['ppcm']:>11.2f}")

    # ------------------------------------------------------------------ P1 and the portfolio
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
    sP1 = np.zeros(NSESS)
    for x in trP:
        si = int(sid[i_of(x["et"])])
        if win[si]:
            sP1[si] += x["pnl"] - rP * x["u"]

    def wkv(x):
        return pd.Series(x[sess_in]).groupby(wkall[sess_in]).sum().to_numpy()
    wp = wkv(sP1)
    dpP = dd_profile(wp)
    P_("")
    P_("=" * 126)
    P_("=== THE PRIMARY: marginal portfolio value against P1/PCT alone, income-matched")
    P_("=" * 126)
    P_(f"    P1/PCT alone (spread ${rP:.2f}/ctrRT): wk ${wp.mean():,.0f}  "
       f"wk+ {100*(wp>0).mean():.1f}%  maxDD ${dpP['maxdd']:,.0f}  top5 ${dpP['dd_mean_top5']:,.0f}"
       f"  wk$@fixDD ${wp.mean()*DDT/max(dpP['maxdd'],1e-9):,.0f}")
    P_("")
    P_(f"{'arm':<11}{'rho wk':>9}{'scale':>8}{'wk$':>9}{'wk+%':>8}{'maxDD':>10}{'top5':>9}"
       f"{'CVaR5':>9}{'strk':>6}{'wk$@fixDD':>11}{'vs P1 alone':>13}")
    base_fix = wp.mean() * DDT / max(dpP["maxdd"], 1e-9)
    prows = []
    for a_ in ARMS:
        wc = wkv(ser_of(ENGB[a_]))
        rho = float(np.corrcoef(wc, wp)[0, 1])
        s_ = wp.mean() / wc.mean() if wc.mean() else np.nan
        tot = wp + wc * s_
        dt = dd_profile(tot)
        stk = max((len(list(g)) for k_, g in itertools.groupby(tot < 0) if k_), default=0)
        cq = max(1, int(round(0.05 * len(tot))))
        fx = tot.mean() * DDT / max(dt["maxdd"], 1e-9)
        P_(f"{a_:<11}{rho:>9.4f}{s_:>8.3f}{tot.mean():>9,.0f}{100*(tot>0).mean():>7.1f}%"
           f"{dt['maxdd']:>10,.0f}{dt['dd_mean_top5']:>9,.0f}"
           f"{np.sort(tot)[:cq].mean():>9,.0f}{stk:>6}{fx:>11,.0f}"
           f"{100*(fx/base_fix-1):>12.1f}%")
        prows.append(dict(arm=a_, rho=rho, scale=s_, wk=float(tot.mean()),
                          poswk=100 * float((tot > 0).mean()), maxdd=dt["maxdd"],
                          top5=dt["dd_mean_top5"], streak=int(stk), fixdd=float(fx),
                          vs_p1=100 * (fx / base_fix - 1)))
    pd.DataFrame(prows).to_csv(os.path.join(OUT, "portfolio.csv"), index=False)

    # ------------------------------------------------------------------ per-year / recency
    P_("")
    P_("=" * 126)
    P_("=== PER-YEAR and RECENCY, $/trade (2026 is partly BURNED: 2026-05-31 -> 07-31)")
    P_("=" * 126)
    yr = sdate.year.to_numpy()
    P_(f"{'arm':<11}" + "".join(f"{y:>12}" for y in (2022, 2023, 2024, 2025, 2026)) +
       f"{'t12m':>12}{'t6m':>12}")
    yrows = []
    for a_ in ARMS:
        line = f"{a_:<11}"
        rec = {}
        for y in (2022, 2023, 2024, 2025, 2026):
            pn = [r["pnl"] for r in ENGB[a_] if yr[r["sess"]] == y]
            line += f"{np.mean(pn) if pn else np.nan:>12,.0f}"
            rec[y] = float(np.mean(pn)) if pn else np.nan
        for wn, lo_ in (("t12m", "2025-08-01"), ("t6m", "2026-02-01")):
            pn = [r["pnl"] for r in ENGB[a_]
                  if sdate.to_numpy()[r["sess"]] >= np.datetime64(lo_)]
            line += f"{np.mean(pn) if pn else np.nan:>12,.0f}"
            rec[wn] = float(np.mean(pn)) if pn else np.nan
        P_(line)
        yrows.append(dict(arm=a_, **{str(k): v for k, v in rec.items()}))
    pd.DataFrame(yrows).to_csv(os.path.join(OUT, "peryear.csv"), index=False)

    P_("")
    P_("=== RISK LIMITS, from evidence, for a kill switch")
    for a_ in ARMS:
        dd = [x for x in rows if x["name"] == a_][0]
        s_ = ser_of(ENGB[a_])
        P_(f"    {a_:<11} worst trade ${dd['worst_trade']:>9,.0f}   worst day "
           f"${s_[sess_in].min():>9,.0f}   worst week ${dd['worst_wk']:>9,.0f}   "
           f"worst MAE ever ${dd['mae_worst']:>9,.0f}   longest losing-week streak {dd['streak']}")
    P_(f"\n[done {_time.time()-t0:.0f}s]")
    out.close()


if __name__ == "__main__":
    main()
