"""WE_W78 - champion vs challenger: P1 alone against P1 + the short sleeve at w = 0.30.

Spec: runs/WE_W78_PAIR/spec.yaml, committed before this ran.

The pair beats P1 on seven metrics with no trade-off on the full extended window. So did four
previously-killed candidates. This runs the tests that killed them.
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
from run_we_w01 import ROOT, PV, STRESS_RT                              # noqa: E402
from run_we_w51c import dd_profile                                      # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W78_PAIR", "out")
os.makedirs(OUT, exist_ok=True)
W76OUT = os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out")
DD_TARGET = 20245.0
W_PRE = 0.30
RNG = np.random.default_rng(20260878)
NDRAW = 200


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "pair.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    d = pd.read_csv(os.path.join(W76OUT, "streams_extended.csv"))
    d["date"] = pd.to_datetime(d["date"])
    iso = d["date"].dt.isocalendar()
    wk = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).to_numpy()
    keys = sorted(set(wk)); wi = np.array([keys.index(x) for x in wk]); NW = len(keys)
    p1, sh = d["P1"].to_numpy(), d["SHORT"].to_numpy()
    dt = d["date"].to_numpy(); yr = d["date"].dt.year.to_numpy()
    P_(f"=== {len(d)} sessions, {NW} weeks, {d['date'].min().date()} -> "
       f"{d['date'].max().date()} (EXTENDED - all of it is now in-sample)")
    P_(f"    daily rho(P1, SHORT) = {np.corrcoef(p1, sh)[0,1]:+.4f}")

    def wkv(v, m=None):
        m = np.ones(len(v), bool) if m is None else m
        w_ = wi[m]
        cnt = np.bincount(w_, minlength=NW) > 0
        return np.bincount(w_, weights=v[m], minlength=NW)[cnt]

    def pan(v, m=None):
        w = wkv(v, m)
        if len(w) < 12:
            return None
        dp = dd_profile(w)
        k = DD_TARGET / max(dp["maxdd"], 1e-9)
        stk = max((len(list(g)) for kk, g in itertools.groupby(w < 0) if kk), default=0)
        return dict(nwk=len(w), wkpos=100 * float((w > 0).mean()), wstreak=int(stk),
                    medwk=float(np.median(w)), weekly=float(w.mean()),
                    weekly_dd=float(w.mean()) * k, dd5=dp["dd_mean_top5"] * k,
                    maxdd=float(dp["maxdd"]), worst=float(w.min()),
                    ulcer=dp["ulcer"] * k)

    def pair(w):
        return (1 - w) * p1 + w * sh

    HDR = (f"{'object':<26}{'wk+%':>7}{'wStrk':>7}{'medWk$':>9}{'weekly$':>9}"
           f"{'wk$@DD':>9}{'top5DD':>9}{'maxDD':>9}{'worst':>9}{'ulcer':>8}")
    P_(f"\n{'='*120}\n=== PHASE 0: the full-sample table that motivated the wave")
    P_(f"{'='*120}\n{HDR}")
    for lab, v in (("P1 alone (CHAMPION)", p1),
                   ("P1+SHORT w=0.30", pair(W_PRE)),
                   ("2 long : 1 short (w=1/3)", pair(1 / 3))):
        r = pan(v)
        P_(f"{lab:<26}{r['wkpos']:>6.1f}%{r['wstreak']:>7}{r['medwk']:>9,.0f}"
           f"{r['weekly']:>9,.0f}{r['weekly_dd']:>9,.0f}{r['dd5']:>9,.0f}{r['maxdd']:>9,.0f}"
           f"{r['worst']:>9,.0f}{r['ulcer']:>8,.0f}")

    # ---------------------------------------------------------------- PHASE 1: rolling
    P_(f"\n{'='*120}")
    P_("=== PHASE 1: ROLLING 24-MONTH WINDOWS. The test that has killed four candidates.")
    P_(f"{'='*120}")
    ds = pd.to_datetime(dt)
    ends = pd.date_range(ds.min() + pd.DateOffset(months=24), ds.max(), freq="ME")
    P_(f"   {len(ends)} candidate windows\n")
    P_(f"{'challenger':<26}{'n':>5}{'weekly$@DD':>13}{'wk+%':>9}{'top5DD':>10}"
       f"{'ALL THREE':>12}")
    roll = []
    for lab, w in (("P1+SHORT w=0.30", W_PRE), ("2 long : 1 short", 1 / 3),
                   ("P1+SHORT w=0.20", 0.20), ("P1+SHORT w=0.40", 0.40)):
        c1 = c2 = c3 = ca = nn = 0
        for e in ends:
            m = (ds > e - pd.DateOffset(months=24)) & (ds <= e)
            if m.sum() < 300:
                continue
            a_, b_ = pan(pair(w), m), pan(p1, m)
            if a_ is None or b_ is None:
                continue
            nn += 1
            x1 = a_["weekly_dd"] > b_["weekly_dd"]
            x2 = a_["wkpos"] > b_["wkpos"]
            x3 = a_["dd5"] < b_["dd5"]
            c1 += x1; c2 += x2; c3 += x3; ca += (x1 and x2 and x3)
        P_(f"{lab:<26}{nn:>5}{100*c1/max(nn,1):>12.0f}%{100*c2/max(nn,1):>8.0f}%"
           f"{100*c3/max(nn,1):>9.0f}%{100*ca/max(nn,1):>11.0f}%")
        roll.append(dict(arm=lab, n=nn, money=100 * c1 / max(nn, 1),
                         wkpos=100 * c2 / max(nn, 1), dd=100 * c3 / max(nn, 1),
                         all3=100 * ca / max(nn, 1)))
    RO = pd.DataFrame(roll); RO.to_csv(os.path.join(OUT, "rolling.csv"), index=False)
    a3 = float(RO[RO["arm"] == "P1+SHORT w=0.30"]["all3"].iloc[0])
    P_(f"\n   PREREGISTERED BAR: all three in a MAJORITY (>50 %) of windows. "
       f"w=0.30 scores {a3:.0f} % -> {'PASS' if a3 > 50 else 'FAIL'}")
    P_(f"   (W61 measured all-three at 5-14 % on the TRUNCATED window.)")

    # ---------------------------------------------------------------- PHASE 2: per year
    P_(f"\n{'='*120}\n=== PHASE 2: PER YEAR. The pair must not be carried by one year.")
    P_(f"{'='*120}")
    yrs = sorted(set(yr))
    P_(f"{'object':<26}" + "".join(f"{y:>12}" for y in yrs))
    for lab, v in (("P1 alone", p1), ("P1+SHORT w=0.30", pair(W_PRE))):
        line = f"{lab:<26}"
        for y in yrs:
            r = pan(v, yr == y)
            line += f"{(r['weekly'] if r else np.nan):>12,.0f}"
        P_(line + "   <- weekly $ (1 unit)")
    P_("")
    for lab, v in (("P1 alone", p1), ("P1+SHORT w=0.30", pair(W_PRE))):
        line = f"{lab:<26}"
        for y in yrs:
            r = pan(v, yr == y)
            line += f"{(r['wkpos'] if r else np.nan):>11.1f}%"
        P_(line + "   <- positive-week %")

    # ---------------------------------------------------------------- PHASE 3: null
    P_(f"\n{'='*120}")
    P_("=== PHASE 3: N1 NULL - is the gain WHEN it trades, or just a second stream?")
    P_(f"{'='*120}")
    P_("   Circularly shift the short sleeve's DAILY series against P1's: marginal distribution")
    P_("   preserved exactly, alignment destroyed. W74 already found the positive-week gain is")
    P_("   GENERIC, so a 'fail' here means 'the second stream is what matters', not 'no gain'.")
    real = pan(pair(W_PRE))
    ks = RNG.choice(np.arange(20, len(p1) - 20), size=NDRAW, replace=False)
    nv = [pan((1 - W_PRE) * p1 + W_PRE * np.roll(sh, int(k))) for k in ks]
    nv = [x for x in nv if x]
    P_(f"\n{'metric':<20}{'real':>12}{'null mean':>12}{'null p95':>12}{'pctile':>9}{'':>10}")
    nrows = []
    for key, lab, hi_good in (("weekly_dd", "weekly $ @ DD", True),
                              ("wkpos", "positive-week %", True),
                              ("dd5", "mean top-5 DD", False),
                              ("wstreak", "weekly streak", False)):
        vals = np.array([x[key] for x in nv])
        pct = 100 * float((vals < real[key]).mean()) if hi_good else \
            100 * float((vals > real[key]).mean())
        P_(f"{lab:<20}{real[key]:>12,.1f}{vals.mean():>12,.1f}"
           f"{np.percentile(vals, 95 if hi_good else 5):>12,.1f}{pct:>8.0f}%"
           f"{('SPECIFIC' if pct >= 95 else 'generic'):>10}")
        nrows.append(dict(metric=lab, real=real[key], null_mean=float(vals.mean()), pctile=pct))
    pd.DataFrame(nrows).to_csv(os.path.join(OUT, "nulls.csv"), index=False)

    # ---------------------------------------------------------------- PHASE 4: walk-forward
    P_(f"\n{'='*120}\n=== PHASE 4: WALK-FORWARD. Re-choose w quarterly on a trailing year.")
    P_(f"{'='*120}")
    GRID = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
    qs = pd.date_range(ds.min() + pd.DateOffset(months=12), ds.max(), freq="QS")
    wf = np.zeros(len(p1)); picks = []
    for q in qs:
        tr = (ds >= q - pd.DateOffset(months=12)) & (ds < q)
        te = (ds >= q) & (ds < q + pd.DateOffset(months=3))
        if tr.sum() < 150 or te.sum() < 20:
            continue
        best, bw = -1e18, 0.0
        for w in GRID:
            r = pan(pair(w), tr)
            if r and r["weekly_dd"] > best:
                best, bw = r["weekly_dd"], w
        wf[te] = pair(bw)[te]; picks.append(bw)
    m = wf != 0
    rw, rf = pan(wf, m), pan(pair(W_PRE), m)
    P_(f"   {len(picks)} refits, choices {picks}")
    churn = 100 * float(np.mean(np.array(picks[1:]) != np.array(picks[:-1]))) if len(picks) > 1 \
        else np.nan
    P_(f"   choice churn {churn:.0f} %, w=0.30 chosen in "
       f"{sum(1 for x in picks if abs(x-0.3) < 1e-9)} of {len(picks)} refits")
    P_(f"\n{'':<26}{'wk+%':>8}{'weekly$':>10}{'wk$@DD':>10}{'top5DD':>10}{'worst':>10}")
    for lab, r in (("walk-forward", rw), ("fixed w=0.30", rf), ("P1 alone", pan(p1, m))):
        P_(f"{lab:<26}{r['wkpos']:>7.1f}%{r['weekly']:>10,.0f}{r['weekly_dd']:>10,.0f}"
           f"{r['dd5']:>10,.0f}{r['worst']:>10,.0f}")
    ret = 100 * rw["weekly_dd"] / rf["weekly_dd"]
    P_(f"\n   retention {ret:.0f} % of the fixed quote (W29 bar: >= 80 %) -> "
       f"{'PASS' if ret >= 80 else 'FAIL'}")

    # ---------------------------------------------------------------- PHASE 5: exposure
    P_(f"\n{'='*120}\n=== PHASE 5: EXPOSURE and FRICTION")
    P_(f"{'='*120}")
    P_(f"   P1 trades 2,007 times / SHORT 2,331 on the extended window. At w = 0.30 the pair's")
    P_(f"   nominal exposure is 0.70 + 0.30 = 1.00 unit, matched to P1 by construction, so the")
    P_(f"   drawdown improvement is NOT an exposure cut.")
    ntr = 0.70 * 2007 + 0.30 * 2331
    P_(f"   weighted round turns: P1 2,007 vs pair {ntr:,.0f} (+{100*ntr/2007-100:.1f} %)")
    P_(f"   C1 stress line at $10/RT: P1 -${10*2007/NW:,.0f}/wk, pair -${10*ntr/NW:,.0f}/wk")
    rp, rc = pan(pair(W_PRE)), pan(p1)
    P_(f"   stress-adjusted weekly: P1 ${rc['weekly']-10*2007/NW:,.0f} vs "
       f"pair ${rp['weekly']-10*ntr/NW:,.0f}")

    # ---------------------------------------------------------------- VERDICT
    P_(f"\n{'='*120}\n=== PREREGISTERED VERDICT")
    P_(f"{'='*120}")
    ok1, ok2 = a3 > 50, ret >= 80
    P_(f"   (1) all three in a majority of rolling windows : {a3:>5.0f} %  -> "
       f"{'PASS' if ok1 else 'FAIL'}")
    P_(f"   (2) walk-forward retention >= 80 %             : {ret:>5.0f} %  -> "
       f"{'PASS' if ok2 else 'FAIL'}")
    P_(f"   (3) not carried by one year                    : see phase 2")
    if ok1 and ok2:
        P_(f"\n   -> BOTH BINDING GATES PASS. The pair is promoted to CHALLENGER-CONFIRMED and")
        P_(f"      becomes the recommended object, with its caveats attached.")
    else:
        P_(f"\n   -> DOES NOT CLEAR THE BAR. P1 remains the baseline; the pair is a documented")
        P_(f"      alternative carrying its own numbers, and the four prior rejections stand on")
        P_(f"      better grounds than they were given.")
    P_(f"\n=== STATUS: [{_time.time()-t0:.0f}s] ===")
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
