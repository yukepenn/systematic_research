"""WE_W105 - ONE AUTHORITATIVE XM_CONFLICT TABLE + THE RISK ARCHITECTURE.

Spec: runs/WE_W105_XMAUDIT/spec.yaml, committed BEFORE this ran.

Section 4 of the owner amendment: reconcile N=342 vs N=348, then one table per period with every
column the amendment names, plus the carrier tests (longs only, shorts only, drop the extremes,
early years, event days).

Section 5: separate the ALPHA EXIT (the clock, closed by W102) from the ACCOUNT-SURVIVAL STOP
(operational). Broad round levels, NO LEVEL SELECTED.

MEASUREMENT ONLY. Nothing here may create a parameter.
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
from run_we_w51 import session_frames                                    # noqa: E402
from run_we_w51c import dd_profile                                       # noqa: E402
from run_we_w97 import votes                                             # noqa: E402
from run_we_w98 import gfills, arm_kw                                    # noqa: E402
from we_fastctx import fast_build_context                                # noqa: E402
from we_lab import spread_profile                                        # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W105_XMAUDIT", "out")
os.makedirs(OUT, exist_ok=True)
W76OUT = os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out")
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
DDT = 20245.0
TICKV = 5.0
MNQ_PV = 2.0                       # MNQ is $2/point vs NQ's $20
ANCH_TRUE, ANCH_OLD, DEC, ENTM, EXITM = 571, 570, 585, 586, 945
DISASTER_PTS = [200, 300, 400, 500, 750, 1000]
XM = {"ES": "runs/SM1M_ES_SUBSTRATE/out/es_1m_2022_2026.parquet",
      "RTY": "runs/SM1M_RTY_SUBSTRATE/out/rty_1m_2022_2026.parquet",
      "YM": "runs/SM1M_YM_SUBSTRATE/out/ym_1m_2022_2026.parquet"}


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "xmaudit.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    prof = spread_profile()
    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr, sid = D["n"], D["t"], D["sid"]
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
    wk = wkall[sess_in]
    nq = pd.DataFrame({"time": pd.to_datetime(tarr), "nq": c}).set_index("time")
    XD = {}
    for k, path in XM.items():
        d_ = pd.read_parquet(os.path.join(ROOT, path), columns=["time", "close"])
        d_["time"] = pd.to_datetime(d_["time"])
        XD[k] = nq.join(d_.set_index("time")["close"].rename(k), how="left")[k].to_numpy()

    def at(mv, arr, uo=False):
        r = np.full(NSESS, np.nan); ix = np.full(NSESS, -1)
        m_ = mod == mv
        r[sid[m_]] = (o[m_] if uo else arr[m_]); ix[sid[m_]] = np.flatnonzero(m_)
        return r, ix

    def build(anchor):
        pa, _ = at(anchor, o, True)
        pdc, _ = at(DEC, c)
        pe, ient = at(ENTM, o, True)
        px, iexit = at(EXITM, c)
        dr = np.sign(pdc - pa)
        acc = np.zeros(NSESS); cnt = np.zeros(NSESS)
        for k in XM:
            aa, _ = at(anchor, XD[k]); bb, _ = at(DEC, XD[k])
            r_ = np.log(bb / aa)
            s_ = pd.Series(r_).rolling(60, min_periods=20).std().shift(1).to_numpy()
            zz = r_ / np.maximum(s_, 1e-12)
            g = np.isfinite(zz); acc[g] += zz[g]; cnt[g] += 1
        xs = np.sign(np.where(cnt > 0, acc / np.maximum(cnt, 1), np.nan))
        okm = (win & np.isfinite(pa) & np.isfinite(pdc) & np.isfinite(pe) & np.isfinite(px) &
               np.isfinite(xs) & (dr != 0) & (xs != 0))
        return dr, okm & (xs != dr), pe, px, ient, iexit

    # ------------------------------------------------------------------ N reconciliation
    P_("=" * 126)
    P_("=== 0. THE N RECONCILIATION - 342 and 348 are two ANCHORS, not a discrepancy")
    P_("=" * 126)
    _, cf_old, _, _, _, _ = build(ANCH_OLD)
    dr, cf, pent, pexit, ient, iexit = build(ANCH_TRUE)
    n_old, n_new = int(cf_old.sum()), int(cf.sum())
    P_(f"    anchor {ANCH_OLD} = the bar stamped 09:30, whose OPEN is the 09:29 price "
       f"(W101/W102) .... N = {n_old}")
    P_(f"    anchor {ANCH_TRUE} = the bar stamped 09:31, the TRUE RTH open under end-stamping "
       f"(W102c) ... N = {n_new}")
    ok = (n_old == 342 and n_new == 348)
    P_(f"    expected 342 and 348 -> {'PASS - both reproduce exactly' if ok else 'FAIL'}")
    if not ok:
        P_("    the record cannot be reconciled; no table is issued."); out.close(); return
    P_(f"    CANONICAL from here on: anchor {ANCH_TRUE}, N = {n_new}. Every number below uses it.")

    # ------------------------------------------------------------------ trade table
    cst = COMM_RT + TICKV * (float(prof.loc[ENTM]) + float(prof.loc[EXITM])) / 2.0
    idx = np.flatnonzero(cf)
    rows = []
    for s in idx:
        d_ = int(dr[s]); a_, b_ = int(ient[s]), int(iexit[s])
        hh, ll = h[a_:b_ + 1], l[a_:b_ + 1]
        epx = pent[s]
        mae = ((ll.min() - epx) if d_ > 0 else (epx - hh.max())) * PV
        mfe = ((hh.max() - epx) if d_ > 0 else (epx - ll.min())) * PV
        rows.append(dict(sess=int(s), date=sdate[s], year=int(sdate[s].year), d=d_,
                         pnl=d_ * (pexit[s] - epx) * PV - cst, mae=mae, mfe=mfe,
                         epx=float(epx), ei=a_, xi=b_))
    T = pd.DataFrame(rows)
    T.to_csv(os.path.join(OUT, "trades.csv"), index=False)

    # P1/PCT weekly, for the correlation column
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

    # rule-derivable calendar (deterministic, no external data)
    dts = sdate[sess_in]
    is_opex = (dts.day >= 15) & (dts.day <= 21) & (dts.dayofweek == 4)
    is_ff = (dts.day <= 7) & (dts.dayofweek == 4)            # first Friday - NFP PROXY
    mend = dts.to_period("M").to_timestamp("M")
    is_me = (mend - dts).days <= 2
    is_qe = is_me & dts.month.isin([3, 6, 9, 12])
    CAL = {"OPEX (3rd Fri)": is_opex, "NFP proxy (1st Fri)": is_ff,
           "month-end (<=2d)": is_me, "quarter-end": is_qe}
    s2i = {int(s): i for i, s in enumerate(sess_in)}

    def per(mask_dates=None, sub=None, wkmask=None):
        """`CORRECTION` the first run grouped every sub-period over ALL 213 weeks, so a one-year
        row was diluted by ~200 empty weeks and its positive-week rate was meaningless (2022 read
        5.2 %). The weekly series is now restricted to the weeks the period actually spans."""
        t = T if sub is None else sub
        if mask_dates is not None:
            t = t[mask_dates]
        if len(t) == 0:
            return None
        s_ = np.zeros(NSESS)
        for _, r_ in t.iterrows():
            s_[int(r_["sess"])] += r_["pnl"]
        ser = s_[sess_in]
        km = np.ones(len(sess_in), bool) if wkmask is None else wkmask
        wv = pd.Series(ser[km]).groupby(wk[km]).sum().to_numpy()
        dp = dd_profile(wv)
        pn = t["pnl"].to_numpy()
        srt = np.sort(pn)[::-1]
        wp = pd.Series(sP1[sess_in][km]).groupby(wk[km]).sum().to_numpy()
        return dict(N=len(t), nl=int((t["d"] > 0).sum()), ns=int((t["d"] < 0).sum()),
                    hit=100 * float((pn > 0).mean()), per_trade=float(pn.mean()),
                    net=float(pn.sum()), poswk=100 * float((wv > 0).mean()),
                    maxdd=dp["maxdd"], worst_trade=float(pn.min()),
                    worst_mae=float(t["mae"].min()),
                    top5=100 * float(srt[:5].sum() / max(pn.sum(), 1e-9)),
                    top10=100 * float(srt[:10].sum() / max(pn.sum(), 1e-9)),
                    rho=float(np.corrcoef(wv, wp)[0, 1]) if wv.std() > 0 else np.nan)
    P_("")
    P_("=" * 126)
    P_("=== 1. THE AUTHORITATIVE TABLE. Canonical anchor 09:31. MEASUREMENT ONLY.")
    P_("=" * 126)
    P_(f"{'period':<10}{'N':>5}{'long':>6}{'short':>6}{'hit%':>7}{'$/trade':>9}{'net $':>10}"
       f"{'wk+%':>7}{'maxDD':>9}{'worst tr':>10}{'worst MAE':>11}{'top5%':>8}{'top10%':>8}"
       f"{'rho P1':>8}")
    PER = [("2022", "2022-01-01", "2023-01-01"), ("2023", "2023-01-01", "2024-01-01"),
           ("2024", "2024-01-01", "2025-01-01"), ("2025", "2025-01-01", "2026-01-01"),
           ("2026YTD", "2026-01-01", "2026-08-01"), ("t12m", "2025-08-01", "2026-08-01"),
           ("t6m", "2026-02-01", "2026-08-01"), ("t3m", "2026-05-01", "2026-08-01"),
           ("FULL", "2022-07-01", "2026-08-01")]
    prows = []
    dcol = T["date"].to_numpy()
    for nm, a_, b_ in PER:
        m = (dcol >= np.datetime64(a_)) & (dcol < np.datetime64(b_))
        km = (sdate.to_numpy()[sess_in] >= np.datetime64(a_)) &              (sdate.to_numpy()[sess_in] < np.datetime64(b_))
        r_ = per(m, wkmask=km)
        if r_ is None:
            P_(f"{nm:<10} no trades"); continue
        burn = " BURNED" if nm in ("t6m", "t3m", "2026YTD") else ""
        P_(f"{nm:<10}{r_['N']:>5}{r_['nl']:>6}{r_['ns']:>6}{r_['hit']:>6.1f}%"
           f"{r_['per_trade']:>9,.0f}{r_['net']:>10,.0f}{r_['poswk']:>6.1f}%"
           f"{r_['maxdd']:>9,.0f}{r_['worst_trade']:>10,.0f}{r_['worst_mae']:>11,.0f}"
           f"{r_['top5']:>7.1f}%{r_['top10']:>7.1f}%{r_['rho']:>8.3f}{burn}")
        prows.append(dict(period=nm, **r_))
    pd.DataFrame(prows).to_csv(os.path.join(OUT, "by_period.csv"), index=False)

    # ------------------------------------------------------------------ carrier tests
    P_("")
    P_("=" * 126)
    P_("=== 2. WHAT CARRIES THE EDGE? Each is a question with a plain answer. NOTHING IS ACTED ON.")
    P_("=" * 126)
    full = per()
    P_(f"{'test':<34}{'N':>6}{'hit%':>8}{'$/trade':>10}{'net $':>11}{'vs full':>10}")

    def line(tag, r_):
        if r_ is None:
            P_(f"{tag:<34} no trades"); return
        P_(f"{tag:<34}{r_['N']:>6}{r_['hit']:>7.1f}%{r_['per_trade']:>10,.0f}"
           f"{r_['net']:>11,.0f}{100*(r_['per_trade']/full['per_trade']-1):>9.1f}%")
    line("ALL (canonical)", full)
    line("LONGS only", per(sub=T[T["d"] > 0]))
    line("SHORTS only", per(sub=T[T["d"] < 0]))
    srt = T.sort_values("pnl", ascending=False)
    line("drop the top 5 trades", per(sub=srt.iloc[5:]))
    line("drop the top 10 trades", per(sub=srt.iloc[10:]))
    line("drop the top 20 trades", per(sub=srt.iloc[20:]))
    line("2022 + 2023 only", per(sub=T[T["year"] <= 2023]))
    line("2024 onward only", per(sub=T[T["year"] >= 2024]))
    P_("")
    P_("    RULE FIXED IN ADVANCE: a carrier test that kills the edge is a reason to WITHDRAW the")
    P_("    candidate, never a reason to restrict it to the surviving subset. Nothing below is")
    P_("    turned into a filter.")

    # event days
    P_("")
    P_(f"{'rule-derivable event class':<34}{'N':>6}{'hit%':>8}{'$/trade':>10}{'net $':>11}"
       f"{'share of net':>14}")
    tot_net = full["net"]
    erows = []
    for nm, msk in CAL.items():
        sel = np.array([bool(msk[s2i[int(s)]]) if int(s) in s2i else False
                        for s in T["sess"]])
        r_ = per(sub=T[sel])
        if r_ is None:
            P_(f"{nm:<34} no trades"); continue
        P_(f"{nm:<34}{r_['N']:>6}{r_['hit']:>7.1f}%{r_['per_trade']:>10,.0f}"
           f"{r_['net']:>11,.0f}{100*r_['net']/tot_net:>13.1f}%")
        erows.append(dict(event=nm, **r_, share_of_net=100 * r_["net"] / tot_net))
        rr = per(sub=T[~sel])
        P_(f"{'   ... all OTHER sessions':<34}{rr['N']:>6}{rr['hit']:>7.1f}%"
           f"{rr['per_trade']:>10,.0f}{rr['net']:>11,.0f}{100*rr['net']/tot_net:>13.1f}%")
    pd.DataFrame(erows).to_csv(os.path.join(OUT, "event_days.csv"), index=False)
    P_("")
    P_("    CPI / FOMC / mega-cap earnings: **UNTESTED**. No causal calendar for them was located")
    P_("    on disk, and the spec forbids inventing an external label. OPEX, month-end,")
    P_("    quarter-end and the first-Friday NFP PROXY are rule-derivable and are computed here;")
    P_("    the NFP proxy is a PROXY and is labelled as one.")

    # ------------------------------------------------------------------ risk architecture
    P_("")
    P_("=" * 126)
    P_("=== 3. RISK ARCHITECTURE. TWO LAYERS, and they are not the same thing.")
    P_("=" * 126)
    P_("    ALPHA EXIT  = the 15:45 clock. CLOSED by W102's stop curve (20 -> 300 pts, 11 levels,")
    P_("                  none beat no-stop at fixed drawdown). Not reopened here.")
    P_("    DISASTER    = an OPERATIONAL account-survival control. Not an alpha device. Not")
    P_("                  expected to make money. Its job is to bound a tail the backtest cannot.")
    P_("")
    P_(f"{'level':>8}{'$ / NQ':>10}{'$ / MNQ':>10}{'triggers':>10}{'% of gross':>12}"
       f"{'net $ after':>13}{'worst trade left':>18}")
    gross = full["net"]
    drows = []
    for pts in DISASTER_PTS:
        pn2 = []
        trig = 0
        for _, r_ in T.iterrows():
            d_ = int(r_["d"]); a_, b_ = int(r_["ei"]), int(r_["xi"])
            epx = r_["epx"]
            stop = epx - d_ * pts
            hh, ll = h[a_:b_ + 1], l[a_:b_ + 1]
            hit = np.flatnonzero(ll <= stop) if d_ > 0 else np.flatnonzero(hh >= stop)
            if len(hit):
                j = a_ + int(hit[0])
                xpx = min(o[j], stop) if d_ > 0 else max(o[j], stop)
                pn2.append(d_ * (xpx - epx) * PV - cst); trig += 1
            else:
                pn2.append(r_["pnl"])
        pn2 = np.array(pn2)
        P_(f"{pts:>8}{pts*PV:>10,.0f}{pts*MNQ_PV:>10,.0f}{trig:>10}"
           f"{100*(1-pn2.sum()/gross):>11.1f}%{pn2.sum():>13,.0f}{pn2.min():>18,.0f}")
        drows.append(dict(pts=pts, usd_nq=pts * PV, usd_mnq=pts * MNQ_PV, triggers=trig,
                          pct_gross_lost=100 * (1 - pn2.sum() / gross), net_after=float(pn2.sum()),
                          worst_left=float(pn2.min())))
    P_(f"{'none':>8}{'-':>10}{'-':>10}{0:>10}{0.0:>11.1f}%{gross:>13,.0f}"
       f"{full['worst_trade']:>18,.0f}")
    pd.DataFrame(drows).to_csv(os.path.join(OUT, "disaster_levels.csv"), index=False)
    P_("")
    P_("    NO LEVEL IS SELECTED BY THIS WAVE. These are round numbers spanning the plausible")
    P_("    range, chosen for being round.")
    P_("")
    P_(f"    The historical worst adverse excursion is ${T['mae'].min():,.0f} "
       f"({abs(T['mae'].min())/PV:.0f} NQ points). THAT IS A SAMPLE MAXIMUM, NOT A BOUND.")
    P_("    'No stop' maximises historical P&L. That is NOT an argument that no stop is the")
    P_("    correct LIVE risk policy - a backtest cannot price the tail it never sampled, and")
    P_("    an object whose only intra-trade control is a clock has no bound on a single day.")
    P_("    The owner selects capital risk; this wave supplies the menu and its price.")
    P_(f"\n[done {_time.time()-t0:.0f}s]")
    out.close()


if __name__ == "__main__":
    main()
