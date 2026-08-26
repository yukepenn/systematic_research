"""WE_W69 - is P1's B-MOM the SAME signal the scalping lab parked as regime-local?

W67's warning rests on a premise I have not verified: that the B-MOM term inside P1 is the
signal the scalping lab judged REGIME-LOCAL (PF 1.013 over 16 unseen years) and that W57
re-measured as a 4-year in-sample result. The rule is the same - a 14-day slot-of-day noise band
around the 09:30 open plus the RTH-anchored VWAP - but the LAB'S VERSION RUNS ON 3-MINUTE BARS
AND P1'S RUNS ON 1-MINUTE BARS, and the lab's 20-year verdict was measured on the 3-minute one.

The 1-minute version's era profile has never been measured, and the NQ 1-minute file goes back
to 2006. So the decisive test is cheap and it is run here before W67's warning is relied on.

If the 1-minute B-MOM has an edge pre-2022, W67's warning softens. If it is flat like the
3-minute one, the warning stands as written.
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
from run_we_w01 import ROOT, PV, COMM_RT, STRESS_RT, sm14_1m             # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w38 import sfills                                            # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W69_BMOMERA", "out")
os.makedirs(OUT, exist_ok=True)
SPLIT = pd.Timestamp("2022-01-01")


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "bmomera.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    D = load_deep("2006-01-05", "2026-05-29 17:00")
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr, sid = D["n"], D["t"], D["sid"]
    P_(f"=== deep substrate {n:,} bars {tarr[0]} -> {tarr[-1]}, {D['n_sess']:,} sessions "
       f"[{_time.time()-t0:.0f}s]")

    # with_solar=False makes the members irrelevant (run_we_w01 amendment_2 routes the B-MOM
    # leg as a direct +-1 position), so one member is enough and the run is fast.
    tg = sm14_1m(D, 460, with_solar=False, with_bmom=True, return_targets=True, volmults=[6])
    P_(f"   P1's OWN B-MOM signal extracted on the 1-minute clock, "
       f"non-zero on {100*float((tg != 0).mean()):.1f} % of bars [{_time.time()-t0:.0f}s]")

    trl = sfills(D, tg, halt=1300.0, target=1000.0)
    P_(f"   {len(trl):,} trades at 1 NQ with the object's own session box "
       f"[{_time.time()-t0:.0f}s]")
    et = pd.to_datetime([x["et"] for x in trl])
    pnl = np.array([x["pnl"] for x in trl])
    sd = pd.to_datetime(D["sess_date"])
    ns_by_year = pd.Series(sd).dt.year.value_counts()

    df = pd.DataFrame(dict(et=et, pnl=pnl, yr=et.year))
    df.to_csv(os.path.join(OUT, "bmom_trades.csv"), index=False)

    P_(f"\n{'='*104}\n=== THE ERA TEST: P1's 1-minute B-MOM, standalone, net of ${COMM_RT}/RT")
    P_(f"{'='*104}")
    P_(f"{'era':<16}{'sessions':>10}{'trades':>9}{'net $':>14}{'$/trade':>10}{'SE':>9}"
       f"{'t':>8}{'win %':>8}{'PF':>7}")
    rows = []
    for lab, m in (("2006-2021", df["et"] < SPLIT), ("2022-2026", df["et"] >= SPLIT)):
        q = df[m]
        if not len(q):
            continue
        se = q["pnl"].std(ddof=1) / np.sqrt(len(q))
        gw = q.loc[q["pnl"] > 0, "pnl"].sum()
        gl = -q.loc[q["pnl"] < 0, "pnl"].sum()
        nsess = int(((sd >= (q["et"].min() if lab.startswith("2006") else SPLIT))
                     & (sd < (SPLIT if lab.startswith("2006") else pd.Timestamp("2027-01-01"))))
                    .sum())
        P_(f"{lab:<16}{nsess:>10,}{len(q):>9,}{q['pnl'].sum():>14,.0f}{q['pnl'].mean():>10,.1f}"
           f"{se:>9,.1f}{q['pnl'].mean()/se:>8.2f}"
           f"{100*float((q['pnl'] > 0).mean()):>7.1f}%{(gw/gl if gl else np.nan):>7.3f}")
        rows.append(dict(era=lab, sessions=nsess, trades=len(q), net=float(q["pnl"].sum()),
                         per_trade=float(q["pnl"].mean()), se=float(se),
                         t=float(q["pnl"].mean() / se), pf=float(gw / gl) if gl else np.nan))
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "eras.csv"), index=False)

    P_(f"\n   the scalping lab's 3-MINUTE B-MOM, for comparison (from its own artifacts):")
    P_(f"      2006-2021  4,077 sessions, net $18,156, $4.5/session, t = 0.27, PF 1.013")
    P_(f"      2022-2026  1,122 sessions, net $319,123, $284.4/session, t = 2.66, PF 1.215")

    P_(f"\n=== PER YEAR ===")
    P_(f"{'year':<8}{'trades':>9}{'net $':>13}{'$/trade':>10}{'t':>8}{'PF':>7}"
       f"{'$/session':>12}")
    yr_rows = []
    for y in sorted(df["yr"].unique()):
        q = df[df["yr"] == y]
        if len(q) < 10:
            continue
        se = q["pnl"].std(ddof=1) / np.sqrt(len(q))
        gw = q.loc[q["pnl"] > 0, "pnl"].sum(); gl = -q.loc[q["pnl"] < 0, "pnl"].sum()
        nse = int(ns_by_year.get(y, 1))
        P_(f"{y:<8}{len(q):>9}{q['pnl'].sum():>13,.0f}{q['pnl'].mean():>10,.1f}"
           f"{q['pnl'].mean()/se:>8.2f}{(gw/gl if gl else np.nan):>7.3f}"
           f"{q['pnl'].sum()/max(nse,1):>12,.1f}")
        yr_rows.append(dict(year=int(y), trades=len(q), net=float(q["pnl"].sum()),
                            per_trade=float(q["pnl"].mean()), t=float(q["pnl"].mean() / se),
                            per_session=float(q["pnl"].sum() / max(nse, 1))))
    pd.DataFrame(yr_rows).to_csv(os.path.join(OUT, "peryear.csv"), index=False)

    P_(f"\n=== ROLLING 24-MONTH t, and where the latest sits in its own history ===")
    ends = pd.date_range(df["et"].min() + pd.DateOffset(months=24), df["et"].max(), freq="ME")
    rr = []
    for e in ends:
        q = df[(df["et"] > e - pd.DateOffset(months=24)) & (df["et"] <= e)]
        if len(q) < 60:
            continue
        se = q["pnl"].std(ddof=1) / np.sqrt(len(q))
        rr.append(dict(end=e.date(), n=len(q), net=float(q["pnl"].sum()),
                       t=float(q["pnl"].mean() / se) if se > 0 else 0.0))
    RR = pd.DataFrame(rr)
    RR.to_csv(os.path.join(OUT, "rolling24.csv"), index=False)
    if len(RR):
        last = RR.iloc[-1]
        P_(f"   {len(RR)} windows | {100*float((RR['net'] > 0).mean()):.1f} % positive | "
           f"median t {RR['t'].median():+.2f} | latest t {last['t']:+.2f} at the "
           f"{100*float((RR['t'].values < last['t']).mean()):.0f}th percentile of its own history")
        P_(f"   (W58 measured the 3-minute version at the 98th percentile of ITS history)")

    P_(f"\n=== VERDICT ===")
    if len(rows) == 2:
        old, new = rows[0], rows[1]
        P_(f"   pre-2022 t = {old['t']:.2f} on {old['trades']:,} trades, "
           f"PF {old['pf']:.3f}")
        P_(f"   post-2022 t = {new['t']:.2f} on {new['trades']:,} trades, "
           f"PF {new['pf']:.3f}")
        if old["t"] >= 1.65 and old["per_trade"] > 0:
            P_(f"   -> P1's 1-MINUTE B-MOM HAS AN EDGE PRE-2022. It is NOT the same era profile")
            P_(f"      as the lab's 3-minute version, and W67's warning SOFTENS: the component")
            P_(f"      supplying 51 % of the object's net is not demonstrably in-sample.")
        else:
            P_(f"   -> P1's 1-MINUTE B-MOM IS FLAT PRE-2022, like the 3-minute one. W67's")
            P_(f"      warning STANDS AS WRITTEN: half the object's net comes from a component")
            P_(f"      with no edge outside the development era.")
    P_(f"\n=== STATUS: diagnostic. Nothing adopted. ===")
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
