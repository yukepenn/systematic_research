# -*- coding: utf-8 -*-
"""CAP02 -- the P1-ONLY ruin table. Spec committed 2026-09-05 before this produced a number.

The live object changed on 2026-09-03: only P1 is deployed, at MnqPerNq = 3. That is not a
smaller M_11, it is a DIFFERENT OBJECT, and CAP01B's 6.5%-at-3-MNQ is a PAIR number.

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
from cap01 import load                                              # noqa: E402
from cap01b import boot, series as pair_series                      # noqa: E402

EQUITY = 10260.14           # GetAccount 2026-09-05 06:03 ET
EQUITY_CAP01B = 10206.86    # what CAP01B used, printed so the two runs are comparable
SEED = 20260905
DRAWS = 20000
MARGIN_FLOOR_PER_MNQ = 100.0
MNQ_COMM = 1.30
NQ_COMM = 4.36

L = []
def P(s=""):
    print(s)
    L.append(s)


def leg_series(df, add, mnq_per_nq=None):
    """ONE leg's session P&L at FULL SIZE. [G3] Only sessions this leg actually traded.

    Deliberately NOT reindexed onto the union of both legs' sessions. Adding XM-only days as
    zero rows would pad the P1 series with flat sessions, which lowers the per-session
    variance and therefore UNDERSTATES ruin. The horizon is expressed in P1-traded sessions,
    so the two must be consistent.
    """
    v = df["pnl"] - add * df["qty"]
    if mnq_per_nq:
        paid_mnq = MNQ_COMM * mnq_per_nq * df["qty"]
        paid_nq_at_scale = NQ_COMM * df["qty"] * (mnq_per_nq / 10.0)
        v = v - (paid_mnq - paid_nq_at_scale) * (10.0 / mnq_per_nq)
    return df.assign(v=v).groupby("sess")["v"].sum().sort_index()


def absorbing_ruin(x, horizon, mean_block, draws, rng, equity, scale):
    """[G5] THE SECOND METHOD. Same event, different computation.

    Walks each path forward one session at a time and stops it the FIRST time cumulative P&L
    reaches -equity, counting stopped paths. The headline uses -min(cumsum) over the whole
    path, which is a different code path reaching the same event. Agreement is evidence the
    implementation is right; it is NOT evidence the STATEMENT is right -- that is G4's job.
    """
    x = np.asarray(x, float) * scale
    n, p = len(x), 1.0 / mean_block
    ruined = np.zeros(draws, bool)
    cum = np.zeros(draws)
    idx = rng.integers(0, n, draws)
    for _ in range(horizon):
        cum = cum + x[idx]
        ruined |= (cum <= -equity)          # absorbing: once true, stays true
        nb = rng.random(draws) < p
        idx = np.where(nb, rng.integers(0, n, draws), (idx + 1) % n)
    return float(ruined.mean())


def main():
    p1, xm = load("p1_trades_full"), load("xm_trades_full")

    # headline: MEASURED spread basis, MNQ commission substituted, expressed at full NQ size
    s_p1 = leg_series(p1, 20.65, mnq_per_nq=3)
    s_pair = pair_series(p1, xm, 20.65, 18.42, mnq_per_nq=3)

    yrs_p1 = (s_p1.index[-1] - s_p1.index[0]).days / 365.25
    rate_p1 = len(s_p1) / yrs_p1
    H1, H2 = int(round(rate_p1)), int(round(2 * rate_p1))

    P("=" * 104)
    P("CAP02 -- P1-ONLY RUIN TABLE.  The live object since 2026-09-03 is P1 ALONE at MnqPerNq=3.")
    P("EVIDENCE: DISCOVERY_CONSUMED, in-sample, post-selection.  A LOWER BOUND ON RISK.")
    P("=" * 104)
    P("")
    P("WHAT THE HEADLINE PROBABILITY IS OVER  [G4, in words, before any number]")
    P("  P(ruin) = P( the cumulative realised P&L path reaches or passes below -EQUITY at ANY")
    P("            point within the horizon ), i.e. THE ACCOUNT IS WIPED OUT.")
    P("  It is NOT P(max drawdown from peak > equity): the modelled peak runs far above the")
    P("  start, so that number is strictly larger.  Calling it ruin is the 10x error CAP01")
    P("  published on 2026-09-01.  Both are printed below, side by side, every time.")
    P("  It is NOT P(margin call), which is reported separately on the day-margin floor.")
    P("")
    P("EQUITY = $%s (netLiquidation, GetAccount 2026-09-05 06:03 ET).  CAP01B used $%s."
      % (format(EQUITY, ",.2f"), format(EQUITY_CAP01B, ",.2f")))
    P("P1-only pool: %d P1-traded sessions over %.3f years -> %.1f/yr.  1yr=%d, 2yr=%d units."
      % (len(s_p1), yrs_p1, rate_p1, H1, H2))
    P("Pair pool (control): %d sessions.  The P1-only series is NOT padded with XM-only days;"
      % len(s_pair))
    P("  padding would add flat sessions, cut per-session variance and UNDERSTATE ruin.")

    # ---------------------------------------------------------------- GATES
    dd1, we1 = boot(s_p1.values, H2, 10, DRAWS, np.random.default_rng(SEED))
    dd2, we2 = boot(s_pair.values, H2, 10, DRAWS, np.random.default_rng(SEED))

    sc3 = 0.30
    p_we_p1 = float((we1 * sc3 >= EQUITY).mean())
    p_dd_p1 = float((dd1 * sc3 > EQUITY).mean())

    # G1 reproduction: the PAIR, warm pool, CAP01B's own equity and horizon convention
    yrs_pr = (s_pair.index[-1] - s_pair.index[0]).days / 365.25
    H2_pr = int(round(2 * len(s_pair) / yrs_pr))
    _, we_pr_warm = boot(s_pair.iloc[37:].values, H2_pr, 10, DRAWS,
                         np.random.default_rng(20260901))
    g1 = float((we_pr_warm * sc3 >= EQUITY_CAP01B).mean())

    g2 = bool(np.all(dd1 >= we1 - 1e-9))
    n_expect = int(p1[p1["qty"] > 0].groupby("sess").size().shape[0])
    g3 = (len(s_p1) == n_expect)
    g4 = (abs(p_dd_p1 - p_we_p1) > 0.02)
    p_abs = absorbing_ruin(s_p1.values, H2, 10, DRAWS, np.random.default_rng(SEED + 1),
                           EQUITY, sc3)
    g5 = (abs(p_we_p1 - p_abs) <= 0.010)

    P("")
    P("%-12s %-56s %10s %10s  %s" % ("GATE", "SPEC", "SPEC", "OBSERVED", "VERDICT"))
    P("-" * 104)
    gates = [
        ("CAP02-G1", "REPRODUCTION: pair, warm, 2yr, 3 MNQ == CAP01B 0.065", "0.065",
         "%.3f" % g1, abs(g1 - 0.065) <= 0.010),
        ("CAP02-G2", "IDENTITY: maxdd >= worst_equity on EVERY draw", "True", str(g2), g2),
        ("CAP02-G3", "POPULATION: P1 series == P1-traded sessions only", str(n_expect),
         str(len(s_p1)), g3),
        ("CAP02-G4", "SEMANTIC: reported P(ruin) is worst_equity, NOT maxdd", ">0.02 apart",
         "%.3f" % abs(p_dd_p1 - p_we_p1), g4),
        ("CAP02-G5", "SECOND METHOD: absorbing-barrier walk agrees", "<=0.010",
         "%.4f" % abs(p_we_p1 - p_abs), g5),
    ]
    ok = True
    for gid, d, sp, obs, passed in gates:
        ok &= bool(passed)
        P("%-12s %-56s %10s %10s  %s" % (gid, d, sp, obs, "PASS" if passed else "FAIL"))
    P("-" * 104)
    P("ALL GATES PASS" if ok else "*** AT LEAST ONE GATE FAILED -- the table below is NOT quotable ***")

    # ---------------------------------------------------------------- THE TABLE
    P("")
    P("THE P1-ONLY TABLE   (MEASURED spread basis, MNQ commission charged, true horizons)")
    P("%-6s %10s %10s %12s %12s %12s %12s" % ("MNQ", "medDD$", "medDD%", "P(ruin) 1y",
                                              "P(ruin) 2y", "P(dd>E) 2y", "P(margin) 2y"))
    P("-" * 104)
    rows = []
    dd1y, we1y = boot(s_p1.values, H1, 10, DRAWS, np.random.default_rng(SEED + 7))
    for k in [1, 2, 3, 4, 5]:
        sc = k / 10.0
        med = float(np.median(dd1 * sc))
        pr1 = float((we1y * sc >= EQUITY).mean())
        pr2 = float((we1 * sc >= EQUITY).mean())
        pdd = float((dd1 * sc > EQUITY).mean())
        pmg = float((we1 * sc >= EQUITY - MARGIN_FLOOR_PER_MNQ * 3 * k).mean())
        mark = "  <- LIVE" if k == 3 else ""
        P("%-6d %10s %9.0f%% %12.3f %12.3f %12.3f %12.3f%s"
          % (k, format(med, ",.0f"), 100 * med / EQUITY, pr1, pr2, pdd, pmg, mark))
        rows.append(dict(mnq_per_nq=k, median_dd=med, p_ruin_1y=pr1, p_ruin_2y=pr2,
                         p_dd_gt_equity_2y=pdd, p_margin_2y=pmg))

    # ---------------------------------------------------------------- CONTROL
    P("")
    P("MATCHED CONTROL -- the PAIR, same draws, same equity, same horizon.  A class-conditional")
    P("table requires its unconditional control in the same wave (CLAUDE.md section 4).")
    P("%-6s %14s %14s %14s %14s" % ("MNQ", "P1 P(ruin)2y", "PAIR P(ruin)2y",
                                    "P1 medDD$", "PAIR medDD$"))
    P("-" * 104)
    for k in [1, 2, 3, 4, 5]:
        sc = k / 10.0
        a = float((we1 * sc >= EQUITY).mean()); b = float((we2 * sc >= EQUITY).mean())
        P("%-6d %14.3f %14.3f %14s %14s%s"
          % (k, a, b, format(float(np.median(dd1 * sc)), ",.0f"),
             format(float(np.median(dd2 * sc)), ",.0f"), "  <- LIVE" if k == 3 else ""))
        rows[k - 1]["pair_p_ruin_2y"] = b
        rows[k - 1]["pair_median_dd"] = float(np.median(dd2 * sc))

    # ---------------------------------------------------------------- G6 EMPIRICAL ANCHOR
    P("")
    P("[G6] EMPIRICAL ANCHOR -- the SINGLE realised path, no resampling, n=1.  Reported, NOT gated.")
    for name, s in (("P1-only", s_p1), ("PAIR", s_pair)):
        c = np.concatenate([[0.0], np.cumsum(s.values * sc3)])
        trough = -float(np.min(c))
        i = int(np.argmin(c))
        when = str(s.index[max(0, i - 1)].date())
        P("  %-8s worst equity trough $%9s (%5.1f%% of equity) at %s   -> %s"
          % (name, format(trough, ",.0f"), 100 * trough / EQUITY, when,
             "WOULD HAVE BEEN WIPED OUT" if trough >= EQUITY else "survived"))
    P("  n=1. One path cannot estimate a tail probability; it exists so the bootstrap has an")
    P("  assumption-free anchor beside it, and because a realised path can be checked by hand.")

    # ---------------------------------------------------------------- DRIFT
    P("")
    P("DRIFT SENSITIVITY -- the input that dominates the answer, varied rather than assumed.")
    P("%-22s %14s %14s" % ("edge assumption", "P1 P(ruin)2y", "PAIR P(ruin)2y"))
    P("-" * 104)
    mu1, mu2 = float(np.mean(s_p1.values)), float(np.mean(s_pair.values))
    for lab, f in (("in-sample (as is)", 1.0), ("70% of in-sample", 0.7),
                   ("40% of in-sample", 0.4), ("edge is ZERO", 0.0)):
        a1 = s_p1.values - (1 - f) * mu1
        a2 = s_pair.values - (1 - f) * mu2
        _, w1 = boot(a1, H2, 10, DRAWS, np.random.default_rng(SEED + 11))
        _, w2 = boot(a2, H2, 10, DRAWS, np.random.default_rng(SEED + 11))
        P("%-22s %14.3f %14.3f" % (lab, float((w1 * sc3 >= EQUITY).mean()),
                                   float((w2 * sc3 >= EQUITY).mean())))
    P("")
    P("NO SIZE IS RECOMMENDED.  That is the owner's decision, and this run may not make it.")
    P("=" * 104)

    pd.DataFrame(rows).to_csv(os.path.join(OUT, "cap02_table.csv"), index=False)
    with open(os.path.join(OUT, "cap02.txt"), "wb") as fh:
        fh.write(("\n".join(L) + "\n").encode("utf-8"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
