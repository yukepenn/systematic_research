"""WE_W60 - the CONSISTENCY object, built only from what W59 licensed.

W59 forbade free selection over the 216 outer cells (the walk-forward selector sat at the 2.0th
percentile of random choice) and licensed two things: SELECTION-FREE aggregation over an axis
whose cells are near-exchangeable, and movement along a response surface that is MONOTONE.

The deliverable is the CURVE, in the owner's own units, with the exchange rate labelled at every
point. The owner picks his point; this file does not pick it for him.

Runs entirely off W59's persisted cell series.
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

OUT = os.path.join(ROOT, "runs", "WE_W60_CONSISTENCY", "out")
os.makedirs(OUT, exist_ok=True)
W59 = os.path.join(ROOT, "runs", "WE_W59_REOPTIM", "out")
DD_TARGET = 20245.0
INC = "h1300_t1000_v0.500_c3"
HALTS = ["800", "1300", "2000", "inf"]
TGS = ["500", "750", "1000", "1500", "2500", "inf"]
NDRAW = 300
RNG = np.random.default_rng(20260860)


def streak(a):
    b = m = 0
    for z in a:
        b = b + 1 if z < 0 else 0
        m = max(m, b)
    return int(m)


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "consistency.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    S = pd.read_parquet(os.path.join(W59, "cells_daily.parquet"))
    dates = pd.to_datetime(S["date"])
    cells = [c for c in S.columns if c != "date"]
    iso = dates.dt.isocalendar()
    wkkey = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).values
    keys_w = sorted(set(wkkey))
    wk_idx = np.array([keys_w.index(k) for k in wkkey])
    NW, NSs = len(keys_w), len(dates)
    P_(f"=== loaded {len(cells)} persisted cells x {NSs} sessions, {NW} weeks "
       f"(no re-simulation) [{_time.time()-t0:.0f}s]")

    def met(sp, name, mask=None):
        s = sp if mask is None else sp[mask]
        wi = wk_idx if mask is None else wk_idx[mask]
        if len(s) < 40:
            return None
        v = np.bincount(wi, weights=s, minlength=NW)
        v = v[np.bincount(wi, minlength=NW) > 0]
        dp = dd_profile(v)
        k = DD_TARGET / max(dp["maxdd"], 1e-9)
        tr = s != 0
        return dict(arm=name, daypos=100 * float((s > 0).mean()),
                    trdpos=100 * float((s[tr] > 0).mean()) if tr.any() else 0.0,
                    wkpos=100 * float((v > 0).mean()), wstreak=streak(v), dstreak=streak(s),
                    medwk=float(np.median(v)) * k, weekly=float(v.mean()) * k,
                    worst=float(v.min()) * k, dd_top5=dp["dd_mean_top5"] * k,
                    ulcer=dp["ulcer"] * k)
    HDR = (f"{'arm':<40}{'day+%':>7}{'trdD+%':>8}{'wk+%':>7}{'dStrk':>7}{'wStrk':>7}"
           f"{'medWk$':>9}{'weekly$':>10}{'top5DD':>9}{'ulcer':>8}{'worst$':>9}")

    def show(r, tag=""):
        P_(f"{r['arm']:<40}{r['daypos']:>7.1f}{r['trdpos']:>8.1f}{r['wkpos']:>7.1f}"
           f"{r['dstreak']:>7}{r['wstreak']:>7}{r['medwk']:>9,.0f}{r['weekly']:>10,.0f}"
           f"{r['dd_top5']:>9,.0f}{r['ulcer']:>8,.0f}{r['worst']:>9,.0f}{tag}")

    inc = S[INC].values
    A_cells = [f"h{h}_t1000_v0.500_c3" for h in HALTS]
    B_cells = [f"h{h}_t{t}_v0.500_c3" for h in HALTS for t in TGS]
    A_cells = [c for c in A_cells if c in cells]
    B_cells = [c for c in B_cells if c in cells]
    A = S[A_cells].values.mean(axis=1)
    Bv = S[B_cells].values.mean(axis=1)
    Dv = S["h2000_t750_v0.500_c3"].values if "h2000_t750_v0.500_c3" in cells else inc

    # ---- C: constrained walk-forward, one step per quarter on the two monotone axes ------
    q = dates.dt.to_period("Q")
    qs = sorted(q.unique())

    def score(sp):
        if (sp != 0).sum() < 20:
            return -1e18
        v = np.bincount(wk_idx[:len(sp)], weights=sp, minlength=NW)
        dp = dd_profile(v)
        if dp["maxdd"] <= 0:
            return -1e18
        tr = sp != 0
        return float((sp[tr] > 0).mean()) * float(v.mean()) * (DD_TARGET / dp["maxdd"])
    C = np.zeros(NSs)
    hi_, ti_ = HALTS.index("1300"), TGS.index("1000")
    moves = 0
    path = []
    for j, qq in enumerate(qs):
        m_now = (q == qq).values
        nm = f"h{HALTS[hi_]}_t{TGS[ti_]}_v0.500_c3"
        if j < 4:
            C[m_now] = S[nm].values[m_now]; path.append(nm); continue
        m_past = (q < qq).values
        cand = [(hi_, ti_)]
        for dh in (-1, 1):
            if 0 <= hi_ + dh < len(HALTS):
                cand.append((hi_ + dh, ti_))
        for dt in (-1, 1):
            if 0 <= ti_ + dt < len(TGS):
                cand.append((hi_, ti_ + dt))
        best, bs = (hi_, ti_), -1e18
        for h2, t2 in cand:
            c2 = f"h{HALTS[h2]}_t{TGS[t2]}_v0.500_c3"
            if c2 not in cells:
                continue
            s_ = score(S[c2].values[m_past])
            if s_ > bs:
                bs, best = s_, (h2, t2)
        if best != (hi_, ti_):
            moves += 1
        hi_, ti_ = best
        nm = f"h{HALTS[hi_]}_t{TGS[ti_]}_v0.500_c3"
        C[m_now] = S[nm].values[m_now]
        path.append(nm)

    P_(f"\n{'='*126}\n=== PHASE 0: the arms, full window, all at a fixed ${DD_TARGET:,.0f} "
       f"max drawdown")
    P_(f"{'='*126}")
    P_(HDR)
    r_inc = met(inc, "E  P1 INCUMBENT")
    show(r_inc)
    r_A = met(A, f"A  aggregate over HALT ({len(A_cells)} cells, selection-free)")
    show(r_A)
    r_B = met(Bv, f"B  aggregate over HALT x TARGET ({len(B_cells)} cells, selection-free)")
    show(r_B)
    r_C = met(C, "C  constrained walk-forward (1 step/qtr)")
    show(r_C, f"   moved {moves} of {len(qs)-4} quarters, ended at {path[-1]}")
    r_D = met(Dv, "D  fixed h2000_t750  [HINDSIGHT-FLAGGED]")
    show(r_D)
    pd.DataFrame([r_inc, r_A, r_B, r_C, r_D]).to_csv(os.path.join(OUT, "arms.csv"), index=False)

    # =====================================================================================
    # PHASE 1 - SUB-PERIOD STABILITY
    # =====================================================================================
    P_(f"\n{'='*126}\n=== PHASE 1: sub-period stability. A full-sample argmax proves nothing.")
    P_(f"{'='*126}")
    yrs = sorted(set(dates.dt.year))
    ARMS = {"A halt-agg": A, "B halt x target agg": Bv, "C constrained WF": C,
            "D h2000_t750 [hindsight]": Dv}
    P_(f"{'arm':<26}" + "".join(f"{y:>26}" for y in yrs))
    P_(f"{'':<26}" + "".join(f"{'trdD+% delta':>13}{'weekly% delta':>13}" for _ in yrs))
    for nm, sp in ARMS.items():
        line = f"{nm:<26}"
        for y in yrs:
            m = (dates.dt.year == y).values
            a, b_ = met(sp, "", m), met(inc, "", m)
            if a is None or b_ is None:
                line += f"{'-':>13}{'-':>13}"; continue
            line += (f"{a['trdpos']-b_['trdpos']:>+13.1f}"
                     f"{100*(a['weekly']/max(b_['weekly'],1e-9)-1):>+13.1f}")
        P_(line)
    # rolling 24-month
    P_(f"\n   rolling 24-month windows: fraction in which the arm BEATS the incumbent")
    ends = pd.date_range(dates.min() + pd.DateOffset(months=24), dates.max(), freq="ME")
    P_(f"{'arm':<26}{'windows':>9}{'trdD+% wins':>14}{'weekly$ wins':>15}"
       f"{'top5DD wins':>14}{'all three':>12}")
    subrows = []
    for nm, sp in ARMS.items():
        w1 = w2 = w3 = w4 = tot = 0
        for e in ends:
            b0 = e - pd.DateOffset(months=24)
            m = ((dates > b0) & (dates <= e)).values
            a, b_ = met(sp, "", m), met(inc, "", m)
            if a is None or b_ is None:
                continue
            tot += 1
            c1 = a["trdpos"] > b_["trdpos"]; c2 = a["weekly"] > b_["weekly"]
            c3 = a["dd_top5"] < b_["dd_top5"]
            w1 += c1; w2 += c2; w3 += c3; w4 += (c1 and c2 and c3)
            subrows.append(dict(arm=nm, end=e.date(), trd=a["trdpos"] - b_["trdpos"],
                                wk=a["weekly"] - b_["weekly"],
                                dd=a["dd_top5"] - b_["dd_top5"]))
        P_(f"{nm:<26}{tot:>9}{100*w1/max(tot,1):>13.0f}%{100*w2/max(tot,1):>14.0f}%"
           f"{100*w3/max(tot,1):>13.0f}%{100*w4/max(tot,1):>11.0f}%")
    pd.DataFrame(subrows).to_csv(os.path.join(OUT, "subperiod.csv"), index=False)

    # =====================================================================================
    # PHASE 2 - THE MECHANISM of the halt aggregate
    # =====================================================================================
    P_(f"\n{'='*126}\n=== PHASE 2: does the halt aggregate work the way I said it does?")
    P_(f"{'='*126}")
    Am = S[A_cells].values
    disagree = (Am != 0).any(axis=1) & ~np.all(np.isclose(Am, Am[:, [0]]), axis=1)
    agree = ~disagree & (Am != 0).any(axis=1)
    P_(f"   sessions where the 4 halt cells DISAGREE: {int(disagree.sum())} of {NSs} "
       f"({100*disagree.mean():.1f} %) - these are the sessions where a halt fired for some")
    P_(f"   halts and not others, i.e. exactly where a graded halt can act.")
    P_(f"{'':<28}{'sessions':>10}{'incumbent $':>14}{'aggregate $':>14}{'delta $':>12}"
       f"{'inc +day%':>11}{'agg +day%':>11}")
    for lab, m in (("halts DISAGREE", disagree), ("halts agree", agree),
                   ("all flat", ~((Am != 0).any(axis=1)))):
        if m.sum() == 0:
            continue
        P_(f"{lab:<28}{int(m.sum()):>10}{inc[m].sum():>14,.0f}{A[m].sum():>14,.0f}"
           f"{A[m].sum()-inc[m].sum():>12,.0f}"
           f"{100*float((inc[m] > 0).mean()):>10.1f}%{100*float((A[m] > 0).mean()):>10.1f}%")
    P_(f"\n   The stated mechanism requires the aggregate's gain to be concentrated on the")
    P_(f"   DISAGREE rows. If it is not, the mechanism sentence is wrong.")

    # =====================================================================================
    # PHASE 3 - NULLS, per arm
    # =====================================================================================
    P_(f"\n{'='*126}\n=== PHASE 3: nulls, chosen per arm")
    P_(f"{'='*126}")
    P_("A and B perform NO selection, so their null is a RANDOM-AXIS aggregate of the same size:")
    P_("does the HALT axis specifically beat an arbitrary set of cells? C is a constrained")
    P_("selector and gets a scan-matched null over its own constrained space.\n")
    P_(f"{'arm':<30}{'real trdD+%':>13}{'null mean':>11}{'pct':>8}"
       f"{'real weekly$':>14}{'null mean':>11}{'pct':>8}{'verdict':>10}")
    nrows = []
    for nm, real, k in (("A halt-agg", r_A, len(A_cells)), ("B halt x target agg", r_B,
                                                            len(B_cells))):
        t_, w_ = [], []
        for _ in range(NDRAW):
            pick = RNG.choice(len(cells), k, replace=False)
            m_ = met(S[[cells[i] for i in pick]].values.mean(axis=1), "")
            if m_:
                t_.append(m_["trdpos"]); w_.append(m_["weekly"])
        t_, w_ = np.array(t_), np.array(w_)
        pt = 100 * float((t_ < real["trdpos"]).mean())
        pw = 100 * float((w_ < real["weekly"]).mean())
        P_(f"{nm:<30}{real['trdpos']:>13.1f}{t_.mean():>11.1f}{pt:>7.1f}%"
           f"{real['weekly']:>14,.0f}{w_.mean():>11,.0f}{pw:>7.1f}%"
           f"{('PASS' if (pt >= 95 and pw >= 95) else 'fail'):>10}")
        nrows.append(dict(arm=nm, trd=real["trdpos"], trd_null=float(t_.mean()), trd_pct=pt,
                          wk=real["weekly"], wk_null=float(w_.mean()), wk_pct=pw))
    # C: scan-matched over its own space
    space = [c for c in cells if c.endswith("_v0.500_c3")]
    t_, w_ = [], []
    for _ in range(NDRAW):
        s_ = np.zeros(NSs)
        for j, qq in enumerate(qs):
            m_now = (q == qq).values
            c2 = space[int(RNG.integers(0, len(space)))]
            s_[m_now] = S[c2].values[m_now]
        m_ = met(s_, "")
        if m_:
            t_.append(m_["trdpos"]); w_.append(m_["weekly"])
    t_, w_ = np.array(t_), np.array(w_)
    pt = 100 * float((t_ < r_C["trdpos"]).mean())
    pw = 100 * float((w_ < r_C["weekly"]).mean())
    P_(f"{'C constrained WF':<30}{r_C['trdpos']:>13.1f}{t_.mean():>11.1f}{pt:>7.1f}%"
       f"{r_C['weekly']:>14,.0f}{w_.mean():>11,.0f}{pw:>7.1f}%"
       f"{('PASS' if (pt >= 95 and pw >= 95) else 'fail'):>10}")
    nrows.append(dict(arm="C constrained WF", trd=r_C["trdpos"], trd_null=float(t_.mean()),
                      trd_pct=pt, wk=r_C["weekly"], wk_null=float(w_.mean()), wk_pct=pw))
    pd.DataFrame(nrows).to_csv(os.path.join(OUT, "nulls.csv"), index=False)

    # =====================================================================================
    # PHASE 4 - THE CURVE. The owner picks the point.
    # =====================================================================================
    P_(f"\n{'='*126}\n=== PHASE 4: THE CURVE - the owner's own units. This wave does NOT pick "
       f"the point.")
    P_(f"{'='*126}")
    pts = []
    for c in cells:
        if not c.endswith("_v0.500_c3"):
            continue
        m_ = met(S[c].values, c)
        if m_:
            pts.append(m_)
    for extra in (r_A, r_B, r_C):
        pts.append(extra)
    Pf = pd.DataFrame(pts).sort_values("trdpos")
    front, bestw = [], -1e18
    for _, r in Pf[::-1].iterrows():           # walk from high traded-day rate downward
        if r["weekly"] > bestw:
            front.append(r); bestw = r["weekly"]
    Fr = pd.DataFrame(front).sort_values("trdpos", ascending=False)
    Fr.to_csv(os.path.join(OUT, "curve.csv"), index=False)
    P_(f"{'arm':<40}{'trdD+%':>9}{'weekly$':>10}{'vs incumbent':>14}"
       f"{'$ per extra green day':>24}")
    for _, r in Fr.iterrows():
        dtrd = r["trdpos"] - r_inc["trdpos"]
        dwk = r["weekly"] - r_inc["weekly"]
        # green days bought per year = delta traded-day rate x traded sessions per year
        gd = dtrd / 100.0 * (NSs * 0.6) / (NSs / 252.0)
        rate = (-dwk * 52.0 / gd) if abs(gd) > 1e-9 else np.nan
        P_(f"{r['arm']:<40}{r['trdpos']:>9.1f}{r['weekly']:>10,.0f}"
           f"{100*(r['weekly']/r_inc['weekly']-1):>+13.1f}%"
           f"{(f'{rate:,.0f}' if np.isfinite(rate) and dtrd > 0 else '-'):>24}")
    P_(f"\n   The incumbent sits at trdD+ {r_inc['trdpos']:.1f} % and ${r_inc['weekly']:,.0f}/wk.")
    P_(f"   Every row above it buys green days and pays for them at the rate in the last")
    P_(f"   column. THAT IS A PREFERENCE, NOT A FACT, and it is the owner's to set.")
    P_(f"\n=== STATUS: nothing adopted. Arms are RECOMMENDED or not; the point is the owner's. ===")
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
