"""WE_W70 - the owner's questions, answered with numbers instead of adjectives.

Four questions, asked directly:
  1. Do we make money almost every day and every week IN THE LAST TWO YEARS specifically?
     Every consistency figure this campaign has published is a FULL-WINDOW figure.
  2. What do we actually do - is it trend?
  3. Did we catch the BIG trends, the multi-day ones, or only the intraday ones?
  4. Why the -$1,300 halt and the +$1,000 target, and has anything else been tried?

Runs off the series persisted in W56 plus the NQ substrate. No re-simulation.
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
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w51 import session_frames, classify, A, B                    # noqa: E402
from run_we_w51c import dd_profile                                       # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W70_OWNERQ", "out")
os.makedirs(OUT, exist_ok=True)
P1D = os.path.join(ROOT, "runs", "WE_W56_BREADTH", "out", "p1_daily.csv")
CONTRACTS = 2.6


def streak(a):
    return max((len(list(g)) for k, g in itertools.groupby(a < 0) if k), default=0)


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "ownerq.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    D = load_deep("2022-01-01", "2026-07-31 17:00")
    st, en, elapsed = session_frames(D)
    sess_date = pd.to_datetime(D["sess_date"])
    sess_in = np.array([s for s in range(D["n_sess"])
                        if A <= D["t"][st[s]] < B])
    all_dates = sess_date[sess_in]
    p1 = pd.read_csv(P1D, index_col=0, parse_dates=True).iloc[:, 0]
    p1 = p1.groupby(p1.index).sum()                       # defensive: collapse any duplicates
    all_dates = pd.DatetimeIndex(pd.Series(all_dates).drop_duplicates().values)
    # every session in the window, zero on the ones P1 did not trade
    daily = p1.reindex(all_dates).fillna(0.0)
    traded = daily != 0
    iso = daily.index.isocalendar()
    wk = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).values
    P_(f"=== {len(daily):,} sessions {daily.index.min().date()} -> {daily.index.max().date()} | "
       f"P1 traded {int(traded.sum()):,} of them ({100*traded.mean():.1f} %) | "
       f"net ${daily.sum():,.0f} at ~1.27 contracts")

    # =====================================================================================
    # Q1 - CONSISTENCY BY PERIOD, and the last two years on their own
    # =====================================================================================
    P_(f"\n{'='*126}\n=== Q1: do we make money almost every day and every week - "
       f"AND SPECIFICALLY IN THE LAST TWO YEARS?")
    P_(f"{'='*126}")
    P_(f"All figures at {CONTRACTS} contracts, the size at which the FULL-WINDOW average is "
       f"~$3,000/week.\n")
    k = CONTRACTS / 1.27
    hi = daily.index.max()
    PERIODS = [("full window", daily.index.min(), hi),
               ("last 3 years", hi - pd.DateOffset(months=36), hi),
               ("LAST 2 YEARS", hi - pd.DateOffset(months=24), hi),
               ("last 12 months", hi - pd.DateOffset(months=12), hi),
               ("last 6 months", hi - pd.DateOffset(months=6), hi)]
    P_(f"{'period':<16}{'sessions':>10}{'day+%':>8}{'tradedDay+%':>13}{'weeks':>7}{'week+%':>9}"
       f"{'worst wk streak':>17}{'worst day streak':>18}{'median week $':>15}{'mean week $':>13}")
    rows = []
    for lab, lo, hi_ in PERIODS:
        m = (daily.index > lo) & (daily.index <= hi_)
        d = daily[m].values * k
        w = pd.Series(daily[m].values * k).groupby(wk[m]).sum().values
        tr = d != 0
        r = dict(period=lab, sessions=int(m.sum()),
                 daypos=100 * float((d > 0).mean()),
                 trdpos=100 * float((d[tr] > 0).mean()) if tr.any() else 0.0,
                 weeks=len(w), wkpos=100 * float((w > 0).mean()),
                 wstreak=streak(w), dstreak=streak(d[tr]),
                 medwk=float(np.median(w)), meanwk=float(w.mean()))
        P_(f"{lab:<16}{r['sessions']:>10}{r['daypos']:>7.1f}%{r['trdpos']:>12.1f}%"
           f"{r['weeks']:>7}{r['wkpos']:>8.1f}%{r['wstreak']:>17}{r['dstreak']:>18}"
           f"{r['medwk']:>15,.0f}{r['meanwk']:>13,.0f}")
        rows.append(r)
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "consistency.csv"), index=False)
    P_(f"\n   'worst day streak' counts consecutive LOSING TRADED sessions, skipping the days")
    P_(f"   the object sits out - it is the run of red days you would actually experience.")

    # =====================================================================================
    # Q2/Q3 - WHAT DO WE DO, AND DID WE CATCH THE BIG TRENDS?
    # =====================================================================================
    c = D["c"]
    # one date in the window carries two sessions; take the later close for that date so the
    # swing algorithm sees one price per date, matching the daily P&L series above
    dclose = (pd.Series([c[en[s] - 1] for s in sess_in],
                        index=pd.DatetimeIndex(sess_date[sess_in]))
              .groupby(level=0).last().reindex(all_dates))
    P_(f"\n{'='*126}\n=== Q2/Q3: what do we actually do, and did we catch the BIG "
       f"multi-day trends?")
    P_(f"{'='*126}")
    P_("Big up-moves found by a swing algorithm on session closes: a run ends when price")
    P_("retraces more than RETR of the run so far. Nothing about P1 is used to find them.\n")
    for RETR in (0.20, 0.33):
        px = dclose.values
        runs, i0, lo_i = [], 0, 0
        peak_i = 0
        for i in range(1, len(px)):
            if px[i] < px[lo_i]:
                if px[peak_i] > px[lo_i]:
                    runs.append((lo_i, peak_i))
                lo_i = i; peak_i = i
            elif px[i] > px[peak_i]:
                peak_i = i
            elif px[peak_i] > px[lo_i] and (px[peak_i] - px[i]) > RETR * (px[peak_i] - px[lo_i]):
                runs.append((lo_i, peak_i)); lo_i = i; peak_i = i
        if px[peak_i] > px[lo_i]:
            runs.append((lo_i, peak_i))
        runs = [(a_, b_) for a_, b_ in runs if b_ > a_ and (px[b_] - px[a_]) > 0]
        runs.sort(key=lambda r: -(px[r[1]] - px[r[0]]))
        top = runs[:10]
        tot_move = sum(px[b_] - px[a_] for a_, b_ in runs)
        got_all = sum(daily.values[a_:b_ + 1].sum() for a_, b_ in runs) / PV
        P_(f"   retracement threshold {RETR:.0%}: {len(runs)} up-runs, "
           f"{tot_move:,.0f} points of total up-movement, we captured {got_all:,.0f} points "
           f"= {100*got_all/max(tot_move,1e-9):.1f} %")
        if RETR == 0.20:
            P_(f"\n{'rank':<6}{'from':>12}{'to':>12}{'sessions':>10}{'move (pts)':>12}"
               f"{'we made (pts)':>15}{'capture':>10}{'we were long % of it':>22}")
            for j, (a_, b_) in enumerate(top, 1):
                mv = px[b_] - px[a_]
                got = daily.values[a_:b_ + 1].sum() / PV
                nse = b_ - a_ + 1
                inm = 100 * float((daily.values[a_:b_ + 1] != 0).mean())
                P_(f"{j:<6}{str(all_dates[a_].date()):>12}{str(all_dates[b_].date()):>12}"
                   f"{nse:>10}{mv:>12,.0f}{got:>15,.1f}{100*got/mv:>9.1f}%{inm:>21.0f}%")
            pd.DataFrame([dict(rank=j, start=str(all_dates[a_].date()),
                               end=str(all_dates[b_].date()), sessions=b_ - a_ + 1,
                               move=float(px[b_] - px[a_]),
                               got=float(daily.values[a_:b_ + 1].sum() / PV))
                          for j, (a_, b_) in enumerate(top, 1)]).to_csv(
                os.path.join(OUT, "bigtrends.csv"), index=False)
        P_("")
    kl_all = classify(D, st, en)[sess_in]
    klass = (pd.Series(kl_all, index=pd.DatetimeIndex(sess_date[sess_in]))
             .groupby(level=0).last().reindex(all_dates).values)
    P_(f"   and the intraday picture (W50's classes), for comparison:")
    for kk in ("TREND-UP", "TREND-DOWN", "REVERSAL", "RANGE", "MIXED"):
        m = klass == kk
        P_(f"      {kk:<12}{100*m.mean():>6.1f} % of sessions   "
           f"{daily.values[m].sum()/PV/len(daily):>7.2f} pts/session of the total")

    # =====================================================================================
    # Q4 - THE SESSION BOX, and what else was tried
    # =====================================================================================
    P_(f"\n{'='*126}\n=== Q4: why -$1,300 and +$1,000? What else was tried?")
    P_(f"{'='*126}")
    grid = os.path.join(ROOT, "runs", "WE_W59_REOPTIM", "out", "grid.csv")
    if os.path.exists(grid):
        G = pd.read_csv(grid)
        inc = G[(G.halt == 1300.0) & (G.target == 1000.0) & (G.vote == 0.5) & (G.cut == 3)]
        P_(f"   W59 scanned {len(G)} cells: halt x target x vote threshold x quality cut.")
        P_(f"   The incumbent's RANK among them, on each metric the owner named:\n")
        P_(f"{'metric':<26}{'incumbent':>12}{'best in the grid':>18}{'rank':>16}{'best cell':>28}")
        for key, hi_ in (("trdpos", True), ("wkpos", True), ("medwk", True), ("weekly", True),
                         ("dd_top5", False), ("ulcer", False), ("wstreak", False)):
            col = G[key].values
            v = float(inc[key].iloc[0])
            rank = int((col > v).sum()) + 1 if hi_ else int((col < v).sum()) + 1
            bi = int(np.argmax(col)) if hi_ else int(np.argmin(col))
            P_(f"{key:<26}{v:>12,.2f}{col[bi]:>18,.2f}{f'{rank} of {len(G)}':>16}"
               f"{G.iloc[bi]['arm']:>28}")
        P_(f"\n   The two response surfaces, holding everything else at the incumbent:")
        P_(f"{'target':<10}{'traded-day +%':>16}{'week +%':>10}{'weekly$':>10}{'top5DD':>10}")
        for _, r in G[(G.halt == 1300.0) & (G.vote == 0.5) & (G.cut == 3)].sort_values("target").iterrows():
            P_(f"{('none' if r.target > 1e11 else f'{int(r.target)}'):<10}{r.trdpos:>15.1f}%"
               f"{r.wkpos:>9.1f}%{r.weekly:>10,.0f}{r.dd_top5:>10,.0f}"
               + ("   <- INCUMBENT" if r.target == 1000.0 else ""))
        P_(f"\n{'halt':<10}{'traded-day +%':>16}{'week +%':>10}{'weekly$':>10}{'top5DD':>10}")
        for _, r in G[(G.target == 1000.0) & (G.vote == 0.5) & (G.cut == 3)].sort_values("halt").iterrows():
            P_(f"{('none' if r.halt > 1e11 else f'{int(r.halt)}'):<10}{r.trdpos:>15.1f}%"
               f"{r.wkpos:>9.1f}%{r.weekly:>10,.0f}{r.dd_top5:>10,.0f}"
               + ("   <- INCUMBENT" if r.halt == 1300.0 else ""))
    P_(f"\n=== STATUS: reporting only. Nothing adopted. ===")
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
