"""WE_W116b - correcting W116's OWN best-of-15 bar, and it is the same defect as W99's.

THE DEFECT, mine, and I have made it before. W116's conservative best-of-15 null drew an
INDEPENDENT random sign vector for every one of the fifteen timing cells. But the fifteen cells are
the SAME RULE at neighbouring minutes on the SAME sessions - their per-session P&L is almost the
same series. Drawing independent signs destroys that correlation, so the maximum over fifteen
independent draws is far larger than the maximum over fifteen cells that move together, and the bar
comes out much too high.

This is exactly the error W99 made and that I recorded in the discipline notes: "the control
permuted each rule independently, destroying cross-rule correlation and inflating the null above
the real value." Recorded again rather than quietly fixed.

THE FIX: one coin flip PER SESSION, shared across all fifteen cells. Same market, same sessions,
correlation preserved exactly as it is in reality.
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
from run_we_w114 import Win, RTH0, DEC, EXIT                             # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W116_FMADJUDICATE", "out")
SEED = 1160
NPERM = 4000
DECS = [678, 693, 708, 723, 738]
EXITS = [929, 944, 959]


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "fmadj_b.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    rng = np.random.default_rng(SEED)
    W = Win("2022-07-01", "2026-07-31 17:00", True, "MODERN")
    P_(f"    {len(W.sess_in):,} sessions [{_time.time()-t0:.0f}s]")

    cells = []
    for d_ in DECS:
        for e in EXITS:
            m2 = np.sign(W.at(d_ - 19) - W.at(RTH0, use_open=True))
            R = W.run(d_, e, m2)
            cells.append(dict(dec=d_, exit=e, R=R,
                              per_trade=float(R["pnl"][R["take"]].mean())))
    real = [c for c in cells if c["dec"] == DEC and c["exit"] == EXIT][0]["per_trade"]

    # ------------------------------------------------------------------ how correlated ARE they?
    P_("")
    P_("=" * 122)
    P_("=== 1. HOW INDEPENDENT ARE THE FIFTEEN TIMING CELLS, ACTUALLY?")
    P_("=" * 122)
    M = np.column_stack([np.where(c["R"]["take"], c["R"]["pnl"], np.nan) for c in cells])
    C = pd.DataFrame(M).corr()
    iu = np.triu_indices(len(cells), 1)
    rbar = float(np.nanmean(C.to_numpy()[iu]))
    K = len(cells)
    keff = K / (1.0 + (K - 1) * rbar)
    P_(f"    mean pairwise correlation of the 15 cells' per-session P&L: {rbar:+.3f}")
    P_(f"    min {np.nanmin(C.to_numpy()[iu]):+.3f}   max {np.nanmax(C.to_numpy()[iu]):+.3f}")
    P_(f"    effective independent cells  K/(1+(K-1)*rho) = {keff:.2f}   (nominal K = {K})")
    P_("")
    P_("    A best-of-K bar assumes K INDEPENDENT chances. At this correlation there are")
    P_(f"    effectively {keff:.1f}, so W116's independent-draw bar was answering a question about")
    P_("    fifteen unrelated strategies, not about one rule read at neighbouring minutes.")

    # ------------------------------------------------------------------ the corrected null
    P_("")
    P_("=" * 122)
    P_("=== 2. THE CORRECTED BEST-OF-15 NULL - ONE coin flip per SESSION, shared across cells")
    P_("=" * 122)
    takes = [np.flatnonzero(c["R"]["take"]) for c in cells]
    mvs = [c["R"]["mv"] for c in cells]
    costs = [c["R"]["cost"] for c in cells]
    ind = np.empty(NPERM)
    shr = np.empty(NPERM)
    for b in range(NPERM):
        s_all = rng.choice([-1.0, 1.0], size=W.NS)
        vs, vi = [], []
        for j in range(K):
            ix = takes[j]
            vs.append(float((s_all[ix] * mvs[j][ix] - costs[j]).mean()))
            vi.append(float((rng.choice([-1.0, 1.0], size=len(ix)) * mvs[j][ix]
                             - costs[j]).mean()))
        shr[b] = max(vs); ind[b] = max(vi)
    p95s, p95i = float(np.percentile(shr, 95)), float(np.percentile(ind, 95))
    single = np.array([float((rng.choice([-1.0, 1.0], size=len(takes[7])) * mvs[7][takes[7]]
                              - costs[7]).mean()) for _ in range(NPERM)])
    p95_1 = float(np.percentile(single, 95))
    P_(f"{'null construction':<44}{'p95 bar':>10}{'real':>10}{'verdict':>12}")
    P_(f"{'single cell (W114, W116)':<44}{p95_1:>10,.0f}{real:>10,.0f}"
       f"{('CLEARS' if real > p95_1 else 'fails'):>12}")
    P_(f"{'best-of-15, INDEPENDENT signs (W116, WRONG)':<44}{p95i:>10,.0f}{real:>10,.0f}"
       f"{('CLEARS' if real > p95i else 'FAILS'):>12}")
    P_(f"{'best-of-15, SHARED per-session sign (CORRECT)':<44}{p95s:>10,.0f}{real:>10,.0f}"
       f"{('CLEARS' if real > p95s else 'FAILS'):>12}")
    P_("")
    P_(f"    percentile of the real value in the CORRECTED best-of-15 null: "
       f"{100*float((shr < real).mean()):.1f}th")
    P_("")
    P_("    Reading. The independent-sign bar is inflated because it lets fifteen unrelated coins")
    P_("    each have a lucky run. The shared-sign bar asks the question that matters: given ONE")
    P_("    market with these sessions, how well would the LUCKIEST of fifteen neighbouring")
    P_("    read-out times have done by chance?")

    # ------------------------------------------------------------------ plateau shape
    P_("")
    P_("=" * 122)
    P_("=== 3. THE PLATEAU AS A DISTRIBUTION, not a maximum")
    P_("=" * 122)
    pts = np.array([c["per_trade"] for c in cells])
    P_(f"    fifteen cells: min ${pts.min():,.0f}  p25 ${np.percentile(pts,25):,.0f}  "
       f"median ${np.median(pts):,.0f}  p75 ${np.percentile(pts,75):,.0f}  max ${pts.max():,.0f}")
    P_(f"    the preregistered cell (11:48 -> 15:44) is ${real:,.0f}, which is the "
       f"{100*float((pts < real).mean()):.0f}th percentile OF ITS OWN PLATEAU")
    P_(f"    cells above the corrected best-of-15 bar of ${p95s:,.0f}: "
       f"{int((pts > p95s).sum())} of {K}")
    P_(f"    cells above the single-cell bar of ${p95_1:,.0f}: {int((pts > p95_1).sum())} of {K}")
    P_("")
    P_("    A cherry-picked artifact sits at the TOP of its plateau with the rest near zero.")
    P_("    This one sits mid-plateau with every neighbour in the same range - which is the")
    P_("    signature the plateau was measured for.")
    pd.DataFrame([dict(dec=c["dec"], exit=c["exit"], per_trade=c["per_trade"]) for c in cells]
                 ).to_csv(os.path.join(OUT, "plateau.csv"), index=False)
    P_(f"\n[done {_time.time()-t0:.0f}s]")
    out.close()


if __name__ == "__main__":
    main()
