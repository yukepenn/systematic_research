"""WE_W105b - THE EVENT-DAY TEST W105 REPORTED AS UNTESTED, NOW RUN.

W105 said "CPI / FOMC / mega-cap earnings: UNTESTED - no causal calendar was located on disk".
That was WRONG. `research/04_complementary_family/c01_announcement_calendar.csv` exists: 145 rows,
CPI 54 / NFP 54 / FOMC 37, 2022-01-07 -> 2026-07-29, zero rows past the seal, hand-committed from
official sources and already the labelling behind two prior waves (c01_t05 and the scalping lab's
B-FADE). It is reused here rather than reinvented.

MEASUREMENT ONLY. Nothing here may create a parameter or a filter.
"""
from __future__ import annotations
import os, sys, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run_we_w01 as W1
from run_we_w01 import ROOT, PV, COMM_RT
from run_we_w17 import load_deep
from run_we_w51 import session_frames
from we_lab import spread_profile

OUT = os.path.join(ROOT, "runs", "WE_W105_XMAUDIT", "out")
CAL = os.path.join(ROOT, "research", "04_complementary_family", "c01_announcement_calendar.csv")
A = np.datetime64("2022-07-01"); B = np.datetime64("2026-08-01"); TICKV = 5.0
ANCH, DEC, ENTM, EXITM = 571, 585, 586, 945
XM = {"ES": "runs/SM1M_ES_SUBSTRATE/out/es_1m_2022_2026.parquet",
      "RTY": "runs/SM1M_RTY_SUBSTRATE/out/rty_1m_2022_2026.parquet",
      "YM": "runs/SM1M_YM_SUBSTRATE/out/ym_1m_2022_2026.parquet"}

def main():
    out = open(os.path.join(OUT, "eventdays.txt"), "w", encoding="utf-8")
    def P_(*a): print(*a, flush=True); print(*a, file=out); out.flush()
    prof = spread_profile()
    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr, sid = D["n"], D["t"], D["sid"]; o, c = D["o"], D["c"]
    st_, _, _ = session_frames(D)
    mod = ((tarr - tarr.astype("datetime64[D]")).astype("timedelta64[s]").astype(np.int64)//60).astype(np.int32)
    NS = D["n_sess"]; sdate = pd.to_datetime(D["sess_date"])
    win = np.array([A <= tarr[st_[s]] < B for s in range(NS)])
    nq = pd.DataFrame({"time": pd.to_datetime(tarr), "nq": c}).set_index("time")
    XD = {k: nq.join(pd.read_parquet(os.path.join(ROOT,p),columns=["time","close"])
          .assign(time=lambda d: pd.to_datetime(d["time"])).set_index("time")["close"].rename(k),
          how="left")[k].to_numpy() for k, p in XM.items()}
    def at(mv, arr, uo=False):
        r = np.full(NS, np.nan); m = mod == mv; r[sid[m]] = (o[m] if uo else arr[m]); return r
    pa, pdc, pe, px = at(ANCH,o,True), at(DEC,c), at(ENTM,o,True), at(EXITM,c)
    dr = np.sign(pdc - pa); acc = np.zeros(NS); cnt = np.zeros(NS)
    for k in XM:
        r_ = np.log(at(DEC,XD[k]) / at(ANCH,XD[k]))
        s_ = pd.Series(r_).rolling(60, min_periods=20).std().shift(1).to_numpy()
        z = r_/np.maximum(s_,1e-12); g = np.isfinite(z); acc[g] += z[g]; cnt[g] += 1
    xs = np.sign(np.where(cnt>0, acc/np.maximum(cnt,1), np.nan))
    ok = (win & np.isfinite(pa) & np.isfinite(pdc) & np.isfinite(pe) & np.isfinite(px)
          & np.isfinite(xs) & (dr!=0) & (xs!=0))
    cf = ok & (xs != dr)
    cst = COMM_RT + TICKV*(float(prof.loc[ENTM])+float(prof.loc[EXITM]))/2.0
    pnl = dr*(px-pe)*PV - cst
    cal = pd.read_csv(CAL); cal["date"] = pd.to_datetime(cal["date"])
    sd = sdate.to_numpy()
    P_("="*118)
    P_("=== XM_CONFLICT x the COMMITTED announcement calendar (CPI/NFP/FOMC-statement)")
    P_("=== c01_announcement_calendar.csv - 145 rows, 2022-01-07 -> 2026-07-29, 0 past the seal.")
    P_("=== W105 called this UNTESTED. That was wrong: the calendar exists and is reused, not built.")
    P_("="*118)
    idx = np.flatnonzero(cf)
    tot_n, tot_net = len(idx), float(pnl[cf].sum())
    P_(f"    canonical book: N = {tot_n}, net ${tot_net:,.0f}, ${pnl[cf].mean():,.0f}/trade, "
       f"hit {100*float((pnl[cf]>0).mean()):.1f} %")
    P_("")
    P_(f"{'event class':<26}{'cal rows':>10}{'N traded':>10}{'hit%':>8}{'$/trade':>10}"
       f"{'net $':>11}{'% of net':>10}{'% of N':>9}")
    rows = []
    for ev in ("CPI", "NFP", "FOMC"):
        days = set(cal.loc[cal["event"]==ev, "date"].dt.normalize())
        m = cf & np.array([pd.Timestamp(x).normalize() in days for x in sd])
        if m.sum() == 0: P_(f"{ev:<26}{len(days):>10}{0:>10}   no trades"); continue
        P_(f"{ev:<26}{len(days):>10}{int(m.sum()):>10}{100*float((pnl[m]>0).mean()):>7.1f}%"
           f"{pnl[m].mean():>10,.0f}{pnl[m].sum():>11,.0f}"
           f"{100*pnl[m].sum()/tot_net:>9.1f}%{100*m.sum()/tot_n:>8.1f}%")
        rows.append(dict(event=ev, cal_rows=len(days), n=int(m.sum()),
                         hit=100*float((pnl[m]>0).mean()), per_trade=float(pnl[m].mean()),
                         net=float(pnl[m].sum()), pct_net=100*pnl[m].sum()/tot_net))
    alld = set(cal["date"].dt.normalize())
    mA = cf & np.array([pd.Timestamp(x).normalize() in alld for x in sd])
    P_(f"{'ANY announcement':<26}{len(alld):>10}{int(mA.sum()):>10}"
       f"{100*float((pnl[mA]>0).mean()):>7.1f}%{pnl[mA].mean():>10,.0f}{pnl[mA].sum():>11,.0f}"
       f"{100*pnl[mA].sum()/tot_net:>9.1f}%{100*mA.sum()/tot_n:>8.1f}%")
    mN = cf & ~np.array([pd.Timestamp(x).normalize() in alld for x in sd])
    P_(f"{'NON-announcement':<26}{'-':>10}{int(mN.sum()):>10}"
       f"{100*float((pnl[mN]>0).mean()):>7.1f}%{pnl[mN].mean():>10,.0f}{pnl[mN].sum():>11,.0f}"
       f"{100*pnl[mN].sum()/tot_net:>9.1f}%{100*mN.sum()/tot_n:>8.1f}%")
    rows.append(dict(event="ANY", cal_rows=len(alld), n=int(mA.sum()),
                     hit=100*float((pnl[mA]>0).mean()), per_trade=float(pnl[mA].mean()),
                     net=float(pnl[mA].sum()), pct_net=100*pnl[mA].sum()/tot_net))
    rows.append(dict(event="NONE", cal_rows=0, n=int(mN.sum()),
                     hit=100*float((pnl[mN]>0).mean()), per_trade=float(pnl[mN].mean()),
                     net=float(pnl[mN].sum()), pct_net=100*pnl[mN].sum()/tot_net))
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "event_calendar.csv"), index=False)
    P_("")
    P_("    THE READ THAT MATTERS: does the edge SURVIVE on non-announcement sessions? If the")
    P_("    non-announcement row is comfortably positive the object is not an event trade.")
    P_("")
    P_("    NOT actionable: the spec forbids turning any of this into a filter. FOMC MINUTES,")
    P_("    mega-cap earnings, CME roll dates and macro SURPRISE MAGNITUDES remain UNTESTED -")
    P_("    the agent confirmed none exists on disk. PCE exists only as a RULE_APPROX list with")
    P_("    3 of 12 misses >3 days and is not used.")
    out.close()

if __name__ == "__main__":
    main()
