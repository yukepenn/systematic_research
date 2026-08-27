"""WE_W102b - THE ARM MY SPEC LEFT OUT, AND A SCALE ERROR IN THE ONE IT INCLUDED.

W102 found every exit policy makes XM_CONFLICT worse. Before that is written down as "the object
needs room", two things have to be checked:

  1. `X1_ATR2` was specified as "2.0 x ATR20 at 09:45". ATR20 on ONE-MINUTE bars is a one-minute
     volatility. Two of them is a very small number to put behind a six-hour hold. Print the actual
     stop distance in points; if it is tiny, the arm tested "a very tight stop", not "an ATR stop",
     and must be reported that way.
  2. The spec omitted the campaign's OWN natural stop: -$1,300 per contract, the session box's
     level, which is 65 NQ points. It is parameter-free by the repo's own convention and it
     belongs in the comparison.

Then a STOP-DISTANCE CURVE in points. It is a scan and is reported as a SHAPE, not an argmax -
nothing is selected from it.
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
from run_we_w51 import session_frames                                    # noqa: E402
from run_we_w51c import dd_profile                                       # noqa: E402
from we_lab import spread_profile                                        # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W102_XMENGINE", "out")
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
DDT = 20245.0
TICKV = 5.0
MV, ENT, EXITM = 585, 586, 945
XM = {"ES": "runs/SM1M_ES_SUBSTRATE/out/es_1m_2022_2026.parquet",
      "RTY": "runs/SM1M_RTY_SUBSTRATE/out/rty_1m_2022_2026.parquet",
      "YM": "runs/SM1M_YM_SUBSTRATE/out/ym_1m_2022_2026.parquet"}
PTS = [20, 30, 40, 50, 65, 80, 100, 130, 170, 220, 300]


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "stopcurve.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    prof = spread_profile()
    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr, sid, fb = D["n"], D["t"], D["sid"], D["fb"]
    o, c, h, l = D["o"], D["c"], D["h"], D["l"]
    st_, en_, _ = session_frames(D)
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
    p0930, _ = at(570, o)
    p0945, _ = at(MV, c)
    pent, ient = at(ENT, o)
    pexit, iexit = at(EXITM, c)
    orh = np.full(NSESS, -np.inf); orl = np.full(NSESS, np.inf)
    ii = np.flatnonzero((mod >= 570) & (mod <= MV))
    np.maximum.at(orh, sid[ii], h[ii]); np.minimum.at(orl, sid[ii], l[ii])
    tr_ = np.maximum(h, np.r_[c[0], c[:-1]]) - np.minimum(l, np.r_[c[0], c[:-1]])
    tr_[fb] = (h - l)[fb]
    atr = pd.Series(tr_).rolling(20, min_periods=20).mean().to_numpy()
    atr[bidx < 19] = np.nan
    atr45, _ = at(MV, atr)
    acc = np.zeros(NSESS); cnt = np.zeros(NSESS)
    for k in XM:
        a_, _ = at(570, XD[k]); b_, _ = at(MV, XD[k])
        r_ = np.log(b_ / a_)
        s_ = pd.Series(r_).rolling(60, min_periods=20).std().shift(1).to_numpy()
        z = r_ / np.maximum(s_, 1e-12)
        g = np.isfinite(z)
        acc[g] += z[g]; cnt[g] += 1
    xs = np.sign(np.where(cnt > 0, acc / np.maximum(cnt, 1), np.nan))
    drive = np.sign(p0945 - p0930)
    ok = (win & np.isfinite(p0930) & np.isfinite(p0945) & np.isfinite(pent) &
          np.isfinite(pexit) & np.isfinite(atr45) & np.isfinite(xs) & (drive != 0) & (xs != 0))
    take = np.flatnonzero(ok & (xs != drive))

    # ---------------------------------------------------------------- 1. the scale error
    P_("=" * 118)
    P_("=== 1. HOW BIG WAS EACH STOP, ACTUALLY? (in NQ points, on the sessions that fired)")
    P_("=" * 118)
    d_arr = drive[take]
    dist_atr = 2.0 * atr45[take]
    dist_or = np.where(d_arr > 0, pent[take] - orl[take], orh[take] - pent[take])
    dist_flip = np.abs(pent[take] - p0930[take])
    P_(f"{'arm':<12}{'mean pts':>11}{'median':>10}{'p10':>9}{'p90':>9}{'in $':>10}")
    for nm, dd in (("X1_ATR2", dist_atr), ("X2_ORSTOP", dist_or), ("X3_FLIP", dist_flip)):
        P_(f"{nm:<12}{np.nanmean(dd):>11.1f}{np.nanmedian(dd):>10.1f}"
           f"{np.nanpercentile(dd,10):>9.1f}{np.nanpercentile(dd,90):>9.1f}"
           f"{np.nanmean(dd)*PV:>10,.0f}")
    P_(f"{'(reference)':<12} mean |MFE| of the unstopped hold was 137 pts / $2,740; "
       f"mean MAE -102 pts / -$2,033")
    P_("")
    P_("    `CORRECTION` ATR20 here is the average TRUE RANGE OF A ONE-MINUTE BAR. Two of them is")
    P_("    a one-minute-scale distance placed behind a six-hour hold. X1_ATR2 therefore tested")
    P_("    'a very tight stop', NOT 'an ATR stop', and W102's table must be read that way.")

    # ---------------------------------------------------------------- 2. the stop curve
    def run_stop(pts=None, box=False):
        rows = []
        for s in take:
            d_ = int(drive[s]); a_, b_ = int(ient[s]), int(iexit[s])
            if a_ < 0 or b_ < a_:
                continue
            epx = o[a_]
            hh, ll = h[a_:b_ + 1], l[a_:b_ + 1]
            xi, xpx = b_, c[b_]
            if pts is not None:
                stop = epx - d_ * pts
                hit = np.flatnonzero(ll <= stop) if d_ > 0 else np.flatnonzero(hh >= stop)
                if len(hit):
                    j = a_ + int(hit[0])
                    xi = j
                    xpx = min(o[j], stop) if d_ > 0 else max(o[j], stop)
            cst = COMM_RT + TICKV * (float(prof.loc[int(mod[a_])]) +
                                     float(prof.loc[int(mod[xi])])) / 2.0
            rows.append((int(s), d_ * (xpx - epx) * PV - cst, xi - a_, xi != b_))
        return rows

    def pan(rows, wp=None):
        s_ = np.zeros(NSESS)
        for ss, pnl, _, _ in rows:
            s_[ss] += pnl
        wv = pd.Series(s_[sess_in]).groupby(wkall[sess_in]).sum().to_numpy()
        dp = dd_profile(wv)
        pn = np.array([r[1] for r in rows])
        d = dict(trades=len(rows), per_trade=float(pn.mean()),
                 hit=100 * float((pn > 0).mean()), stopped=100 * float(np.mean([r[3] for r in rows])),
                 weekly=float(wv.mean()), maxdd=dp["maxdd"], top5=dp["dd_mean_top5"],
                 poswk=100 * float((wv > 0).mean()), worst=float(wv.min()),
                 fixdd=float(wv.mean()) * DDT / max(dp["maxdd"], 1e-9),
                 t=float(wv.mean()) / max(wv.std(ddof=1) / np.sqrt(len(wv)), 1e-9))
        if wp is not None:
            sc = wp.mean() / wv.mean() if wv.mean() else np.nan
            tot = wp + wv * sc
            dt = dd_profile(tot)
            d["port_fixdd"] = float(tot.mean() * DDT / max(dt["maxdd"], 1e-9))
            d["port_poswk"] = 100 * float((tot > 0).mean())
            d["port_maxdd"] = float(dt["maxdd"])
        return d
    # P1/PCT weekly, rebuilt from W102's committed artifact to avoid re-running the ensemble
    pf = pd.read_csv(os.path.join(OUT, "portfolio.csv"))
    P_("")
    P_("=" * 118)
    P_("=== 2. THE STOP-DISTANCE CURVE. A SCAN, reported as a SHAPE. Nothing is selected from it.")
    P_("===    -$1,300/contract = 65 pts is the campaign's own session-box level.")
    P_("=" * 118)
    P_(f"{'stop pts':>9}{'$/trade':>10}{'hit%':>7}{'stopped%':>10}{'wk$':>8}"
       f"{'maxDD':>9}{'top5':>9}{'wk+%':>7}{'wk$@fixDD':>11}{'t':>6}")
    crows = []
    base = pan(run_stop(None))
    P_(f"{'none':>9}{base['per_trade']:>10,.0f}{base['hit']:>6.1f}%{0.0:>9.1f}%"
       f"{base['weekly']:>8,.0f}{base['maxdd']:>9,.0f}{base['top5']:>9,.0f}"
       f"{base['poswk']:>6.1f}%{base['fixdd']:>11,.0f}{base['t']:>6.2f}")
    crows.append(dict(stop_pts=np.nan, **base))
    for p_ in PTS:
        d = pan(run_stop(p_))
        mark = "  <- session-box level" if p_ == 65 else ""
        P_(f"{p_:>9}{d['per_trade']:>10,.0f}{d['hit']:>6.1f}%{d['stopped']:>9.1f}%"
           f"{d['weekly']:>8,.0f}{d['maxdd']:>9,.0f}{d['top5']:>9,.0f}"
           f"{d['poswk']:>6.1f}%{d['fixdd']:>11,.0f}{d['t']:>6.2f}{mark}")
        crows.append(dict(stop_pts=p_, **d))
    pd.DataFrame(crows).to_csv(os.path.join(OUT, "stop_curve.csv"), index=False)
    P_("")
    P_("    The shape is the finding, not any cell. If wk$@fixDD is monotone in the stop distance")
    P_("    right out to 300 points, the object simply does not want a stop and no cell of this")
    P_("    scan is adopted. If it peaks in the middle, that peak still needs its own wave with a")
    P_("    family-wise null - W95 measured a box-level argmax at the 87.5th percentile of pure")
    P_("    best-of-31 scan noise, which is what an unguarded peak is worth here.")
    P_(f"\n[done {_time.time()-t0:.0f}s]")
    out.close()


if __name__ == "__main__":
    main()
