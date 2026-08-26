"""WE_W59 phase 2/3/4 - SELECT versus AGGREGATE over the object's outer parameters.

The campaign's own mechanism law 2 says selection is noise and members estimating the SAME
quantity should be aggregated. All 216 cells are the same object with different OUTER parameters
- same 32-config vote, same substrate, same fills - so they are exactly such members. The object
already aggregates its 32 INNER configs (W19) and has never aggregated its outer ones.

An aggregate also has a mechanical consistency benefit a single cell cannot have: DIFFERENT
BOXES FIRE ON DIFFERENT DAYS, so the halt and the target stop being all-or-nothing events for
the whole book.

Preregistered prediction (amendment_1): law 2 says the AGGREGATE beats the SELECTOR. If the
selector wins, the law's scope is narrower than stated and gets amended.

Runs entirely off the persisted daily series. No re-simulation.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import ROOT                                              # noqa: E402
from run_we_w51c import dd_profile                                       # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W59_REOPTIM", "out")
DD_TARGET = 20245.0
INC = "h1300_t1000_v0.500_c3"
NDRAW = 300
RNG = np.random.default_rng(20260859)


def streak(a):
    b = m = 0
    for z in a:
        b = b + 1 if z < 0 else 0
        m = max(m, b)
    return int(m)


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "reoptim2.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    S = pd.read_parquet(os.path.join(OUT, "cells_daily.parquet"))
    G = pd.read_csv(os.path.join(OUT, "grid.csv"))
    dates = pd.to_datetime(S["date"])
    cells = [c for c in S.columns if c != "date"]
    M = S[cells].values                       # sessions x cells, US dollars
    NSs, NC = M.shape
    iso = dates.dt.isocalendar()
    wkkey = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).values
    keys_w = sorted(set(wkkey))
    wk_idx = np.array([keys_w.index(k) for k in wkkey])
    NW = len(keys_w)
    P_(f"=== loaded {NC} cells x {NSs} sessions, {NW} weeks | incumbent column present: "
       f"{INC in cells}")
    if INC not in cells:
        out.close(); return

    def metrics(sp, name):
        v = np.bincount(wk_idx, weights=sp, minlength=NW)
        dp = dd_profile(v)
        k = DD_TARGET / max(dp["maxdd"], 1e-9)
        traded = sp != 0
        return dict(arm=name, daypos=100 * float((sp > 0).mean()),
                    trdpos=100 * float((sp[traded] > 0).mean()) if traded.any() else 0.0,
                    flat=100 * float((~traded).mean()),
                    wkpos=100 * float((v > 0).mean()),
                    dstreak=streak(sp), wstreak=streak(v),
                    medwk=float(np.median(v)) * k, weekly=float(v.mean()) * k,
                    worst=float(v.min()) * k, dd_top5=dp["dd_mean_top5"] * k,
                    ulcer=dp["ulcer"] * k, scale=k)
    HDR = (f"{'arm':<40}{'day+%':>7}{'trdD+%':>8}{'flat%':>7}{'wk+%':>7}{'dStrk':>7}{'wStrk':>7}"
           f"{'medWk$':>9}{'weekly$':>10}{'top5DD':>9}{'worst$':>9}{'avg pos':>9}")

    def show(r, pos=None):
        P_(f"{r['arm']:<40}{r['daypos']:>7.1f}{r['trdpos']:>8.1f}{r['flat']:>7.1f}"
           f"{r['wkpos']:>7.1f}{r['dstreak']:>7}{r['wstreak']:>7}{r['medwk']:>9,.0f}"
           f"{r['weekly']:>10,.0f}{r['dd_top5']:>9,.0f}{r['worst']:>9,.0f}"
           f"{(f'{pos:.2f}' if pos is not None else '1.00'):>9}")
    inc_sp = S[INC].values
    r_inc = metrics(inc_sp, "P1 INCUMBENT cell")

    # =====================================================================================
    # PHASE 2 - SELECT vs AGGREGATE
    # =====================================================================================
    P_(f"\n{'='*128}\n=== PHASE 2: SELECT vs AGGREGATE over the OUTER parameters")
    P_(f"{'='*128}")
    P_("'avg pos' is the arm's average position as a multiple of one cell's, before the")
    P_("fixed-drawdown rescaling - an aggregate of 216 cells is NOT 216 contracts.\n")
    P_(HDR)
    show(r_inc)

    # ---- S2: equal-weight aggregate of everything, selection-free -----------------------
    agg = M.mean(axis=1)
    r_agg = metrics(agg, "S2 AGGREGATE of all cells (no selection)")
    show(r_agg, 1.0)
    r_avgcell = dict(G[["daypos", "trdpos", "flat", "wkpos", "medwk", "weekly",
                        "worst", "dd_top5", "ulcer"]].mean())
    r_avgcell.update(arm="   (the AVERAGE single cell, for reference)",
                     dstreak=int(G["dstreak"].mean()), wstreak=int(G["wstreak"].mean()))
    show(r_avgcell)

    # ---- S3: aggregate each one-parameter family ----------------------------------------
    fam = {}
    ic = G[G.arm == INC].iloc[0]
    for pname in ("target", "halt", "vote", "cut"):
        others = [p for p in ("target", "halt", "vote", "cut") if p != pname]
        m = np.ones(len(G), bool)
        for p in others:
            m &= (G[p].values == ic[p])
        names = list(G.loc[m, "arm"].values)
        if len(names) < 2:
            continue
        fam[pname] = names
        show(metrics(S[names].values.mean(axis=1),
                     f"S3 aggregate over {pname.upper()} ({len(names)} cells)"), 1.0)

    # ---- S1: walk-forward quarterly selection -------------------------------------------
    q = dates.dt.to_period("Q")
    qs = sorted(q.unique())
    sel = np.zeros(NSs)
    picks, changes = [], 0
    prev = None

    def score(sp):
        """the consistency objective, as a single number, defined ONCE and never tuned:
        traded-day rate x weekly dollars at fixed drawdown, both of which the owner named."""
        v = np.bincount(wk_idx[:len(sp)], weights=sp, minlength=NW)
        dp = dd_profile(v)
        if dp["maxdd"] <= 0:
            return -1e18
        k = DD_TARGET / dp["maxdd"]
        traded = sp != 0
        if traded.sum() < 20:
            return -1e18
        return float((sp[traded] > 0).mean()) * float(v.mean()) * k
    for j, qq in enumerate(qs):
        m_now = (q == qq).values
        if j < 4:
            sel[m_now] = inc_sp[m_now]              # warm-up: hold the incumbent
            picks.append(INC)
            continue
        m_past = (q < qq).values
        best, bs = INC, -1e18
        for c in cells:
            s_ = score(M[m_past, cells.index(c)])
            if s_ > bs:
                bs, best = s_, c
        sel[m_now] = M[m_now, cells.index(best)]
        picks.append(best)
        if prev is not None and best != prev:
            changes += 1
        prev = best
    r_sel = metrics(sel, "S1 WALK-FORWARD quarterly selection")
    show(r_sel, 1.0)
    P_(f"      -> it changed its pick in {changes} of {len(qs)-4} live quarters "
       f"({100*changes/max(len(qs)-4,1):.0f} % turnover); "
       f"{len(set(picks[4:]))} distinct cells used; it held the incumbent in "
       f"{sum(1 for p in picks[4:] if p == INC)} of them")

    # ---- S4: hindsight best, NOT achievable ---------------------------------------------
    hs = [(score(M[:, k]), c) for k, c in enumerate(cells)]
    hs.sort(reverse=True)
    show(metrics(S[hs[0][1]].values, f"S4 hindsight best ({hs[0][1]}) - NOT ACHIEVABLE"), 1.0)

    P_(f"\n   PREREGISTERED PREDICTION (amendment_1): law 2 says the AGGREGATE beats the")
    P_(f"   SELECTOR. Result: aggregate weekly ${r_agg['weekly']:,.0f} vs selector "
       f"${r_sel['weekly']:,.0f}, traded-day {r_agg['trdpos']:.1f} % vs {r_sel['trdpos']:.1f} % -> "
       + ("LAW HOLDS" if r_agg["weekly"] >= r_sel["weekly"] else
          "SELECTOR WINS - law 2's scope is narrower than stated and must be amended"))

    # =====================================================================================
    # PHASE 3 - NULLS, different by arm as amendment_1 requires
    # =====================================================================================
    P_(f"\n{'='*128}\n=== PHASE 3: nulls. Different by arm, and not interchangeable.")
    P_(f"{'='*128}")
    P_("S1 is a SELECTOR: its null is a selector run on PERMUTED trailing performance, i.e.")
    P_("choosing at random from the same 216. S2 has NO selection, so a scan-matched null is")
    P_("meaningless for it - its test is simply whether it beats the incumbent and the average")
    P_("cell, which is reported above and needs no null.\n")
    n1 = []
    for _ in range(NDRAW):
        s_ = np.zeros(NSs)
        prev_ = None
        for j, qq in enumerate(qs):
            m_now = (q == qq).values
            if j < 4:
                s_[m_now] = inc_sp[m_now]; continue
            c = cells[int(RNG.integers(0, NC))]     # random pick from the same grid
            s_[m_now] = M[m_now, cells.index(c)]
            prev_ = c
        n1.append(metrics(s_, "")["weekly"])
    a1 = np.array(n1)
    p1 = 100 * float((a1 < r_sel["weekly"]).mean())
    P_(f"{'arm':<40}{'weekly$':>12}{'null mean':>12}{'null p95':>12}{'percentile':>12}"
       f"{'verdict':>10}")
    P_(f"{'S1 walk-forward selector':<40}{r_sel['weekly']:>12,.0f}{a1.mean():>12,.0f}"
       f"{np.percentile(a1, 95):>12,.0f}{p1:>11.1f}%"
       f"{('PASS' if p1 >= 95 else 'fail'):>10}")
    P_(f"{'S2 aggregate (no null needed)':<40}{r_agg['weekly']:>12,.0f}"
       f"{r_inc['weekly']:>12,.0f}{'-':>12}"
       f"{('beats incumbent' if r_agg['weekly'] > r_inc['weekly'] else 'loses to incumbent'):>24}")

    # =====================================================================================
    # PHASE 4 - THE MECHANISM: what does the profit target actually do?
    # =====================================================================================
    P_(f"\n{'='*128}\n=== PHASE 4: the profit target, by exact accounting on the measured days")
    P_(f"{'='*128}")
    P_("Compares each target level against the SAME cell with no target, session by session.")
    no_t = f"h1300_tinf_v0.500_c3"
    if no_t in cells:
        base_nt = S[no_t].values
        P_(f"\n{'target':<10}{'sessions saved':>16}{'sessions capped':>17}{'$ saved':>12}"
           f"{'$ given up':>13}{'net $':>12}{'net +days':>11}{'trdD+% delta':>14}")
        rows4 = []
        for tg in (500, 750, 1000, 1500, 2500):
            c = f"h1300_t{tg}_v0.500_c3"
            if c not in cells:
                continue
            sv = S[c].values
            saved = (base_nt <= 0) & (sv > 0)
            capped = (base_nt > 0) & (sv < base_nt)
            lost = (base_nt > 0) & (sv <= 0)
            tr_n = base_nt != 0
            tr_s = sv != 0
            d = (100 * float((sv[tr_s] > 0).mean())
                 - 100 * float((base_nt[tr_n] > 0).mean()))
            P_(f"{tg:<10}{int(saved.sum()):>16}{int(capped.sum()):>17}"
               f"{float(sv[saved].sum() - base_nt[saved].sum()):>12,.0f}"
               f"{float(base_nt[capped].sum() - sv[capped].sum()):>13,.0f}"
               f"{float(sv.sum() - base_nt.sum()):>12,.0f}"
               f"{int(saved.sum()) - int(lost.sum()):>11}{d:>+14.1f}")
            rows4.append(dict(target=tg, saved=int(saved.sum()), capped=int(capped.sum()),
                              net=float(sv.sum() - base_nt.sum()), trdpos_delta=d))
        pd.DataFrame(rows4).to_csv(os.path.join(OUT, "mechanism.csv"), index=False)
        P_(f"\n   'sessions saved' = red without the target, green with it. That is the")
        P_(f"   consistency mechanism, priced. 'sessions capped' is what it costs.")
    P_(f"\n=== STATUS: nothing adopted here. ===")
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
