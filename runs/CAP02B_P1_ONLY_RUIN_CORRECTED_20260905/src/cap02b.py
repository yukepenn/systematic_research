# -*- coding: utf-8 -*-
"""CAP02B -- the P1-ONLY ruin table, CORRECTED REPRODUCTION GATE.

CAP02-G1 FAILED and stays failed. It named "warm pool = 0.065", but 0.06535 is CAP01B's
FULL-pool figure and its WARM-pool figure is 0.0167. CAP02 observed 0.016 -- it reproduced
the warm pool correctly against a target that named the wrong pool. The target is corrected
here ONLY under a strictly HARDER gate: BOTH pools must reproduce.

Both pools are also reported for BOTH objects, because the pair spread is 0.065 full vs
0.017 warm -- a factor of four that a single-pool answer hides.

EVIDENCE STATUS: DISCOVERY_CONSUMED. In-sample, post-selection. LOWER BOUND on risk.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(RUN))
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.join(REPO, "runs", "CAP01_CAPITAL_RUIN_20260901", "src"))
sys.path.insert(0, os.path.join(REPO, "runs", "CAP01B_RUIN_CORRECTION_20260901", "src"))
sys.path.insert(0, os.path.join(REPO, "runs", "CAP02_P1_ONLY_RUIN_20260905", "src"))
from cap01 import load                                              # noqa: E402
from cap01b import boot, series as pair_series                      # noqa: E402
from cap02 import leg_series, absorbing_ruin                        # noqa: E402

EQUITY = 10260.14           # GetAccount 2026-09-05 06:03 ET
EQUITY_CAP01B = 10206.86    # what CAP01B used; the reproduction gates run at THIS equity
SEED = 20260905
DRAWS = 20000
MARGIN_FLOOR_PER_MNQ = 100.0
SC3 = 0.30

L = []
def P(s=""):
    print(s)
    L.append(s)


def horizons(s):
    y = (s.index[-1] - s.index[0]).days / 365.25
    r = len(s) / y
    return int(round(r)), int(round(2 * r)), r, y


def main():
    p1, xm = load("p1_trades_full"), load("xm_trades_full")
    s_p1 = leg_series(p1, 20.65, mnq_per_nq=3)
    s_pair = pair_series(p1, xm, 20.65, 18.42, mnq_per_nq=3)

    P("=" * 104)
    P("CAP02B -- P1-ONLY RUIN TABLE.  The live object since 2026-09-03 is P1 ALONE at MnqPerNq=3.")
    P("EVIDENCE: DISCOVERY_CONSUMED, in-sample, post-selection.  A LOWER BOUND ON RISK.")
    P("=" * 104)
    P("")
    P("WHAT THE HEADLINE PROBABILITY IS OVER  [G4, in words, before any number]")
    P("  P(ruin) = P( the cumulative realised P&L path reaches or passes below -EQUITY at ANY")
    P("            point within the horizon ), i.e. THE ACCOUNT IS WIPED OUT.")
    P("  It is NOT P(max drawdown from peak > equity): the modelled peak runs far above the")
    P("  start, so that number is strictly larger.  Calling it ruin is the 10x error CAP01")
    P("  published on 2026-09-01.  Both are printed side by side in every table below.")
    P("  It is NOT P(margin call), reported separately on the day-margin floor.")
    P("")
    P("EQUITY = $%s (netLiquidation, 2026-09-05 06:03 ET).  Reproduction gates use CAP01B's $%s."
      % (format(EQUITY, ",.2f"), format(EQUITY_CAP01B, ",.2f")))
    P("The P1-only series is NOT padded with XM-only days: padding would add flat sessions,")
    P("cut per-session variance and UNDERSTATE ruin.")

    # ------------------------------------------------------------------ POOLS
    # [G3] the WARM trim is by CALENDAR DATE, not ordinal index. CAP01B cut the PAIR at
    # iloc[37:]; both objects must be cut at the SAME INSTANT IN TIME. Trimming P1 at index
    # 37 would remove a different amount of history, because the legs trade different
    # session counts (726 vs 873).
    warm_start = s_pair.index[37]
    p_p1 = {"full": s_p1, "warm": s_p1[s_p1.index >= warm_start]}
    p_pr = {"full": s_pair, "warm": s_pair.iloc[37:]}

    B = {}
    for obj, pools in (("P1", p_p1), ("PAIR", p_pr)):
        for pool, s in pools.items():
            h1, h2, r, y = horizons(s)
            d2, w2 = boot(s.values, h2, 10, DRAWS, np.random.default_rng(SEED))
            d1, w1 = boot(s.values, h1, 10, DRAWS, np.random.default_rng(SEED + 7))
            B[(obj, pool)] = dict(s=s, h1=h1, h2=h2, rate=r, yrs=y,
                                  dd=d2, we=w2, dd1=d1, we1=w1)

    P("")
    P("POOLS.  warm = sessions on/after %s, the date CAP01B's iloc[37:] cut falls on."
      % warm_start.date())
    P("%-6s %-6s %8s %9s %9s %10s" % ("OBJ", "POOL", "n", "yrs", "sess/yr", "2y units"))
    P("-" * 104)
    for k in [("P1", "full"), ("P1", "warm"), ("PAIR", "full"), ("PAIR", "warm")]:
        b = B[k]
        P("%-6s %-6s %8d %9.3f %9.1f %10d"
          % (k[0], k[1], len(b["s"]), b["yrs"], b["rate"], b["h2"]))

    # ------------------------------------------------------------------ GATES
    g1a = float((B[("PAIR", "full")]["we"] * SC3 >= EQUITY_CAP01B).mean())
    g1b = float((B[("PAIR", "warm")]["we"] * SC3 >= EQUITY_CAP01B).mean())
    g2 = all(bool(np.all(B[k]["dd"] >= B[k]["we"] - 1e-9)) for k in B)
    n_expect = int(p1[p1["qty"] > 0].groupby("sess").size().shape[0])
    g3 = (len(p_p1["full"]) == n_expect
          and p_p1["warm"].index[0] >= warm_start
          and p_pr["warm"].index[0] == warm_start)
    b3 = B[("P1", "full")]
    p_we = float((b3["we"] * SC3 >= EQUITY).mean())
    p_dd = float((b3["dd"] * SC3 > EQUITY).mean())
    g4 = (abs(p_dd - p_we) > 0.02)
    p_abs = absorbing_ruin(p_p1["full"].values, b3["h2"], 10, DRAWS,
                           np.random.default_rng(SEED + 1), EQUITY, SC3)
    g5 = (abs(p_we - p_abs) <= 0.010)

    P("")
    P("%-12s %-56s %10s %10s  %s" % ("GATE", "SPEC", "SPEC", "OBSERVED", "VERDICT"))
    P("-" * 104)
    gates = [
        ("CAP02B-G1a", "REPRODUCTION: pair FULL 2yr 3MNQ == CAP01B 0.06535", "0.0654",
         "%.4f" % g1a, abs(g1a - 0.06535) <= 0.010),
        ("CAP02B-G1b", "REPRODUCTION: pair WARM 2yr 3MNQ == CAP01B 0.0167", "0.0167",
         "%.4f" % g1b, abs(g1b - 0.0167) <= 0.010),
        ("CAP02B-G2", "IDENTITY: maxdd >= worst_equity, all 4 obj x pool", "True",
         str(g2), g2),
        ("CAP02B-G3", "POPULATION: P1 unpadded; warm cut by DATE not index", str(n_expect),
         str(len(p_p1["full"])), g3),
        ("CAP02B-G4", "SEMANTIC: reported P(ruin) is worst_equity, NOT maxdd", ">0.02",
         "%.3f" % abs(p_dd - p_we), g4),
        ("CAP02B-G5", "SECOND METHOD: absorbing-barrier walk agrees", "<=0.010",
         "%.4f" % abs(p_we - p_abs), g5),
    ]
    ok = True
    for gid, d, sp, obs, passed in gates:
        ok &= bool(passed)
        P("%-12s %-56s %10s %10s  %s" % (gid, d, sp, obs, "PASS" if passed else "FAIL"))
    P("-" * 104)
    P("ALL GATES PASS" if ok
      else "*** GATE FAILED -- the table below is NOT quotable ***")

    # ------------------------------------------------------------------ THE TABLE
    rows = []
    for pool in ("full", "warm"):
        bp, bq = B[("P1", pool)], B[("PAIR", pool)]
        P("")
        P("P1-ONLY, %s POOL  (MEASURED spread, MNQ commission, true horizons, E=$%s)"
          % (pool.upper(), format(EQUITY, ",.0f")))
        P("%-5s %10s %8s %11s %11s %12s %12s %14s"
          % ("MNQ", "medDD$", "medDD%", "P(ruin)1y", "P(ruin)2y", "P(dd>E)2y",
             "P(margin)2y", "PAIR P(ruin)2y"))
        P("-" * 104)
        for k in [1, 2, 3, 4, 5]:
            sc = k / 10.0
            med = float(np.median(bp["dd"] * sc))
            r1 = float((bp["we1"] * sc >= EQUITY).mean())
            r2 = float((bp["we"] * sc >= EQUITY).mean())
            pdd = float((bp["dd"] * sc > EQUITY).mean())
            pmg = float((bp["we"] * sc >= EQUITY - MARGIN_FLOOR_PER_MNQ * 3 * k).mean())
            pr2 = float((bq["we"] * sc >= EQUITY).mean())
            P("%-5d %10s %7.0f%% %11.3f %11.3f %12.3f %12.3f %14.3f%s"
              % (k, format(med, ",.0f"), 100 * med / EQUITY, r1, r2, pdd, pmg, pr2,
                 "  <- LIVE" if k == 3 else ""))
            rows.append(dict(pool=pool, mnq_per_nq=k, median_dd=med, p_ruin_1y=r1,
                             p_ruin_2y=r2, p_dd_gt_equity_2y=pdd, p_margin_2y=pmg,
                             pair_p_ruin_2y=pr2))

    # ------------------------------------------------------------------ G6
    P("")
    P("[G6] EMPIRICAL ANCHOR -- the SINGLE realised path at 3 MNQ, no resampling.  n=1, NOT gated.")
    for name, s in (("P1 full", p_p1["full"]), ("P1 warm", p_p1["warm"]),
                    ("PAIR full", p_pr["full"]), ("PAIR warm", p_pr["warm"])):
        c = np.concatenate([[0.0], np.cumsum(s.values * SC3)])
        trough = -float(np.min(c))
        i = int(np.argmin(c))
        when = str(s.index[max(0, i - 1)].date())
        P("  %-10s worst equity trough $%9s (%6.1f%% of equity) at %s  -> %s"
          % (name, format(trough, ",.0f"), 100 * trough / EQUITY, when,
             "WOULD HAVE BEEN WIPED OUT" if trough >= EQUITY else "survived"))
    P("  One path cannot estimate a tail probability. It exists so the bootstrap has an")
    P("  assumption-free anchor beside it, and because a realised path can be checked by hand.")

    # ------------------------------------------------------------------ DRIFT
    P("")
    P("DRIFT SENSITIVITY (full pools) -- the input that dominates the answer, varied not assumed.")
    P("%-24s %16s %16s" % ("edge assumption", "P1 P(ruin)2y", "PAIR P(ruin)2y"))
    P("-" * 104)
    s1, s2 = p_p1["full"], p_pr["full"]
    h1_2, h2_2 = B[("P1", "full")]["h2"], B[("PAIR", "full")]["h2"]
    mu1, mu2 = float(np.mean(s1.values)), float(np.mean(s2.values))
    for lab, f in (("in-sample (as is)", 1.0), ("70% of in-sample", 0.7),
                   ("40% of in-sample", 0.4), ("edge is ZERO", 0.0)):
        _, w1 = boot(s1.values - (1 - f) * mu1, h1_2, 10, DRAWS,
                     np.random.default_rng(SEED + 11))
        _, w2 = boot(s2.values - (1 - f) * mu2, h2_2, 10, DRAWS,
                     np.random.default_rng(SEED + 11))
        P("%-24s %16.3f %16.3f" % (lab, float((w1 * SC3 >= EQUITY).mean()),
                                   float((w2 * SC3 >= EQUITY).mean())))
    P("")
    P("NO SIZE IS RECOMMENDED.  That is the owner's decision, and this run may not make it.")
    P("=" * 104)

    pd.DataFrame(rows).to_csv(os.path.join(OUT, "cap02b_table.csv"), index=False)
    with open(os.path.join(OUT, "cap02b.txt"), "wb") as fh:
        fh.write(("\n".join(L) + "\n").encode("utf-8"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
