"""WE_W71 - the owner asked for h2000_t750 on the LAST TWO YEARS, and for the surrounding
structure. Every cell's daily series is already persisted by W59, so this is pure arithmetic.

THE DISCIPLINE PROBLEM, named first because it governs how the output may be read:
h2000_t750 was identified from response surfaces computed on the FULL window, which INCLUDES the
last two years. Evaluating it on the last two years is therefore NOT out-of-sample and cannot be
presented as confirmation. What IS informative is whether the improvement is STABLE ACROSS
PERIODS - full window, 3y, 2y, 1y, 6m - because an edge that appears only in the slice you look
at is a fit and an edge that holds across all of them is a direction.

So this file reports the WHOLE SURFACE by period, not a winner, and it reports how many of the
216 cells beat the incumbent in each period - which is the multiplicity context that makes any
single cell's number readable.
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
from run_we_w01 import ROOT, PV                                          # noqa: E402
from run_we_w51c import dd_profile                                       # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W71_PERIODGRID", "out")
os.makedirs(OUT, exist_ok=True)
W59 = os.path.join(ROOT, "runs", "WE_W59_REOPTIM", "out")
INC = "h1300_t1000_v0.500_c3"
CAND = "h2000_t750_v0.500_c3"
CONTRACTS = 2.6
RNG = np.random.default_rng(20260871)


def streak(a):
    return max((len(list(g)) for k, g in itertools.groupby(a < 0) if k), default=0)


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "periodgrid.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    S = pd.read_parquet(os.path.join(W59, "cells_daily.parquet"))
    dates = pd.to_datetime(S["date"])
    cells = [c for c in S.columns if c != "date"]
    iso = dates.dt.isocalendar()
    wk = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).values
    k = CONTRACTS / 1.27
    hi = dates.max()
    PERIODS = [("full window", dates.min() - pd.Timedelta(days=1), hi),
               ("last 3 years", hi - pd.DateOffset(months=36), hi),
               ("LAST 2 YEARS", hi - pd.DateOffset(months=24), hi),
               ("last 12 months", hi - pd.DateOffset(months=12), hi),
               ("last 6 months", hi - pd.DateOffset(months=6), hi)]
    P_(f"=== {len(cells)} persisted cells x {len(S)} sessions, no re-simulation. "
       f"All figures at {CONTRACTS} contracts. [{_time.time()-t0:.0f}s]")
    P_(f"\n   READ THIS FIRST: h2000_t750 was identified from response surfaces computed on the")
    P_(f"   FULL window, which CONTAINS the last two years. Evaluating it there is NOT")
    P_(f"   out-of-sample. What the table below can show is STABILITY ACROSS PERIODS, and how")
    P_(f"   many of the {len(cells)} cells beat the incumbent in each period - the multiplicity")
    P_(f"   context without which any single cell's number is unreadable.")

    def met(col, m):
        d = S[col].values[m] * k
        w = pd.Series(d).groupby(wk[m]).sum().values
        if len(w) < 6:
            return None
        dp = dd_profile(w)
        tr = d != 0
        return dict(pts=float(S[col].values[m].sum() / PV / max(m.sum(), 1)),
                    daypos=100 * float((d > 0).mean()),
                    trdpos=100 * float((d[tr] > 0).mean()) if tr.any() else 0.0,
                    wkpos=100 * float((w > 0).mean()), wstreak=streak(w),
                    dstreak=streak(d[tr]), medwk=float(np.median(w)),
                    meanwk=float(w.mean()), maxdd=dp["maxdd"],
                    dd_top5=dp["dd_mean_top5"], ulcer=dp["ulcer"], worst=float(w.min()))

    # =====================================================================================
    # 1 - THE CANDIDATE AGAINST THE INCUMBENT, BY PERIOD
    # =====================================================================================
    P_(f"\n{'='*140}\n=== 1: h2000_t750 against the incumbent, period by period")
    P_(f"{'='*140}")
    HDR = (f"{'period':<16}{'arm':<12}{'pts':>7}{'day+%':>7}{'trdD+%':>8}{'wk+%':>7}"
           f"{'wStrk':>7}{'dStrk':>7}{'medWk$':>10}{'meanWk$':>10}{'maxDD$':>10}"
           f"{'top5DD$':>10}{'ulcer$':>9}{'worstWk$':>11}")
    P_(HDR)
    rows = []
    for lab, lo, hi_ in PERIODS:
        m = ((dates > lo) & (dates <= hi_)).values
        a = met(INC, m); b = met(CAND, m)
        if a is None or b is None:
            continue
        for nm_, r in (("incumbent", a), ("h2000_t750", b)):
            P_(f"{lab if nm_ == 'incumbent' else '':<16}{nm_:<12}{r['pts']:>7.2f}"
               f"{r['daypos']:>7.1f}{r['trdpos']:>8.1f}{r['wkpos']:>7.1f}{r['wstreak']:>7}"
               f"{r['dstreak']:>7}{r['medwk']:>10,.0f}{r['meanwk']:>10,.0f}{r['maxdd']:>10,.0f}"
               f"{r['dd_top5']:>10,.0f}{r['ulcer']:>9,.0f}{r['worst']:>11,.0f}")
            rows.append(dict(period=lab, arm=nm_, **r))
        P_(f"{'':<16}{'DELTA':<12}{b['pts']-a['pts']:>+7.2f}{b['daypos']-a['daypos']:>+7.1f}"
           f"{b['trdpos']-a['trdpos']:>+8.1f}{b['wkpos']-a['wkpos']:>+7.1f}"
           f"{b['wstreak']-a['wstreak']:>+7}{b['dstreak']-a['dstreak']:>+7}"
           f"{b['medwk']-a['medwk']:>+10,.0f}{b['meanwk']-a['meanwk']:>+10,.0f}"
           f"{b['maxdd']-a['maxdd']:>+10,.0f}{b['dd_top5']-a['dd_top5']:>+10,.0f}"
           f"{b['ulcer']-a['ulcer']:>+9,.0f}{b['worst']-a['worst']:>+11,.0f}")
        P_("")
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "candidate_by_period.csv"), index=False)

    # =====================================================================================
    # 2 - THE MULTIPLICITY CONTEXT
    # =====================================================================================
    P_(f"{'='*140}\n=== 2: how many of the {len(cells)} cells beat the incumbent in each period?")
    P_(f"{'='*140}")
    P_("Without this a single cell's improvement is unreadable. If a third of the grid beats the")
    P_("incumbent in a period, one cell doing so is not evidence about that cell.\n")
    P_(f"{'period':<16}{'cells beating on meanWk':>26}{'on trdD+%':>12}{'on top5DD':>12}"
       f"{'on ALL THREE':>15}{'h2000_t750 rank (meanWk)':>26}")
    ctx = []
    for lab, lo, hi_ in PERIODS:
        m = ((dates > lo) & (dates <= hi_)).values
        a = met(INC, m)
        if a is None:
            continue
        n1 = n2 = n3 = n4 = 0
        mws = {}
        for c in cells:
            r = met(c, m)
            if r is None:
                continue
            mws[c] = r["meanwk"]
            x1 = r["meanwk"] > a["meanwk"]; x2 = r["trdpos"] > a["trdpos"]
            x3 = r["dd_top5"] < a["dd_top5"]
            n1 += x1; n2 += x2; n3 += x3; n4 += (x1 and x2 and x3)
        rank = 1 + sum(1 for v in mws.values() if v > mws.get(CAND, -1e18))
        P_(f"{lab:<16}{f'{n1} of {len(cells)}':>26}{n2:>12}{n3:>12}{n4:>15}"
           f"{f'{rank} of {len(cells)}':>26}")
        ctx.append(dict(period=lab, beat_meanwk=n1, beat_trdpos=n2, beat_dd=n3, beat_all3=n4,
                        cand_rank=rank))
    pd.DataFrame(ctx).to_csv(os.path.join(OUT, "multiplicity.csv"), index=False)

    # =====================================================================================
    # 3 - THE FULL SURFACE ON THE LAST TWO YEARS, so nothing is hidden
    # =====================================================================================
    P_(f"\n{'='*140}\n=== 3: the halt x target surface ON THE LAST TWO YEARS "
       f"(vote 0.5, quality cut 3)")
    P_(f"{'='*140}")
    m2 = ((dates > hi - pd.DateOffset(months=24)) & (dates <= hi)).values
    hdr_lab = "halt / target"
    P_(f"{hdr_lab:<16}" + "".join(f"{t:>13}" for t in
                                  ("500", "750", "1000", "1500", "2500", "inf")))
    for metric, lab2 in (("meanwk", "mean week $"), ("trdpos", "traded-day +%"),
                         ("wkpos", "week +%"), ("dd_top5", "mean top-5 DD $"),
                         ("wstreak", "worst weekly streak")):
        P_(f"\n   -- {lab2} --")
        for h in ("800", "1300", "2000", "inf"):
            line = f"{h:<16}"
            for t in ("500", "750", "1000", "1500", "2500", "inf"):
                c = f"h{h}_t{t}_v0.500_c3"
                r = met(c, m2) if c in cells else None
                if r is None:
                    line += f"{'-':>13}"
                else:
                    v = r[metric]
                    star = "*" if c == INC else ("+" if c == CAND else " ")
                    line += f"{v:>12,.1f}{star}" if metric != "wstreak" else f"{int(v):>12}{star}"
            P_(line)
    P_(f"\n   * = incumbent   + = h2000_t750")

    # =====================================================================================
    # 4 - THE HONEST TEST: is the direction stable, or is it a slice?
    # =====================================================================================
    P_(f"\n{'='*140}\n=== 4: is the h2000_t750 direction STABLE, or does it live in one slice?")
    P_(f"{'='*140}")
    P_("Each month-end, a trailing 12-month window. The candidate either beats the incumbent")
    P_("consistently across them or it does not. This is the only reading the data supports.\n")
    ends = pd.date_range(dates.min() + pd.DateOffset(months=12), hi, freq="ME")
    wins = {kk: 0 for kk in ("meanwk", "trdpos", "wkpos", "dd_top5")}
    tot = 0
    deltas = []
    for e in ends:
        m = ((dates > e - pd.DateOffset(months=12)) & (dates <= e)).values
        a, b = met(INC, m), met(CAND, m)
        if a is None or b is None:
            continue
        tot += 1
        wins["meanwk"] += b["meanwk"] > a["meanwk"]
        wins["trdpos"] += b["trdpos"] > a["trdpos"]
        wins["wkpos"] += b["wkpos"] > a["wkpos"]
        wins["dd_top5"] += b["dd_top5"] < a["dd_top5"]
        deltas.append(dict(end=e.date(), d_meanwk=b["meanwk"] - a["meanwk"],
                           d_trdpos=b["trdpos"] - a["trdpos"],
                           d_dd=b["dd_top5"] - a["dd_top5"]))
    P_(f"   {tot} trailing-12-month windows (they overlap 11/12, so the effective independent")
    P_(f"   count is about {max(1, tot // 12)}):")
    for kk, lab2 in (("trdpos", "traded-day +%"), ("wkpos", "week +%"),
                     ("meanwk", "mean week $"), ("dd_top5", "mean top-5 drawdown")):
        P_(f"      beats the incumbent on {lab2:<22} {100*wins[kk]/max(tot,1):>5.0f} % of windows")
    Dl = pd.DataFrame(deltas)
    Dl.to_csv(os.path.join(OUT, "rolling12.csv"), index=False)
    if len(Dl):
        P_(f"\n   median delta across those windows: traded-day "
           f"{Dl['d_trdpos'].median():+.1f} pp | mean week ${Dl['d_meanwk'].median():+,.0f} | "
           f"top-5 drawdown ${Dl['d_dd'].median():+,.0f}")
    P_(f"\n=== STATUS: reporting only. Nothing adopted. The surface and the multiplicity")
    P_(f"    context are the deliverable, not any single cell. ===")
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
