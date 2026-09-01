# -*- coding: utf-8 -*-
"""CAP01B -- the corrected ruin table. Spec committed before this produced a number.

CAP01 published P(maxDD from peak > starting equity) as "P(lose the account)". It is not.
This run reports BOTH quantities on every draw and never conflates them again.

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
from cap01 import load, maxdd                                    # noqa: E402

EQUITY = 10206.86
SEED = 20260901
DRAWS = 20000
MARGIN_FLOOR_PER_MNQ = 100.0          # NT8 day margin; peak exposure is 9 MNQ at MnqPerNq=3
MNQ_COMMISSION_PER_CTR_RT = 1.30      # AUDIT04_MNQ_PROBE, n = 704 fills
NQ_COMMISSION_PER_CTR_RT = 4.36       # the value already netted inside the CSV `pnl`

L = []
def P(s=""):
    print(s)
    L.append(s)


def series(p1, xm, p1_add, xm_add, mnq_per_nq=None):
    """Session P&L at FULL SIZE, one cost basis.

    [D3] If mnq_per_nq is given, the NQ commission already netted into `pnl` is REMOVED and
    the MNQ commission actually paid is charged instead, then the whole thing is expressed
    back at full-NQ size so the caller's scale factor stays exact.  Gross P&L scales exactly
    (3 MNQ = $6/pt vs 1 NQ = $20/pt = 0.30); commission does not, and CAP01 missed it.
    """
    def leg(df, add):
        v = df["pnl"] - add * df["qty"]
        if mnq_per_nq:
            paid_mnq = MNQ_COMMISSION_PER_CTR_RT * mnq_per_nq * df["qty"]      # actual $
            paid_nq_at_scale = NQ_COMMISSION_PER_CTR_RT * df["qty"] * (mnq_per_nq / 10.0)
            v = v - (paid_mnq - paid_nq_at_scale) * (10.0 / mnq_per_nq)        # back to full size
        return df.assign(v=v)[["sess", "v"]]
    return pd.concat([leg(p1, p1_add), leg(xm, xm_add)]).groupby("sess")["v"].sum().sort_index()


def boot(x, horizon, mean_block, draws, rng, chunk=4000):
    """Politis-Romano stationary bootstrap. Returns (maxdd_from_peak, worst_equity_loss).

    maxdd_from_peak : max(runmax(cum) - cum)   -- a DRAWDOWN statistic
    worst_equity    : -min(cum)                -- how close the ACCOUNT came to zero
    The zero-prepend anchors the first peak at starting equity, which is correct, and is
    exactly why maxdd >= worst_equity holds identically (gate G2).
    """
    x = np.asarray(x, float)
    n, p = len(x), 1.0 / mean_block
    dd = np.empty(draws); we = np.empty(draws)
    done = 0
    while done < draws:
        k = min(chunk, draws - done)
        idx = np.empty((k, horizon), np.int64)
        idx[:, 0] = rng.integers(0, n, k)
        for j in range(1, horizon):
            nb = rng.random(k) < p
            idx[:, j] = np.where(nb, rng.integers(0, n, k), (idx[:, j - 1] + 1) % n)
        c = np.cumsum(x[idx], axis=1)
        cz = np.concatenate([np.zeros((k, 1)), c], axis=1)
        dd[done:done + k] = np.max(np.maximum.accumulate(cz, axis=1) - cz, axis=1)
        we[done:done + k] = -np.min(cz, axis=1)
        done += k
    return dd, we


def main():
    rng = np.random.default_rng(SEED)
    p1, xm = load("p1_trades_full"), load("xm_trades_full")
    s_meas = series(p1, xm, 20.65, 18.42)
    s_nt8 = series(p1, xm, 0.0, 0.0)

    yrs = (s_meas.index[-1] - s_meas.index[0]).days / 365.25
    per_yr = len(s_meas) / yrs
    H1, H2 = int(round(per_yr)), int(round(2 * per_yr))

    P("=" * 100)
    P("CAP01B -- CORRECTED RUIN TABLE.  DISCOVERY_CONSUMED, in-sample, LOWER BOUND on risk.")
    P("=" * 100)
    P("%d traded sessions over %.3f calendar years  ->  %.1f traded sessions/year"
      % (len(s_meas), yrs, per_yr))
    P("TRUE horizons: 1 yr = %d units, 2 yr = %d units.  CAP01 used 252/504 = %.2f/%.2f yr."
      % (H1, H2, 252 / per_yr, 504 / per_yr))

    # ------------------------------------------------------------------ GATES
    dd_old, we_old = boot(s_meas.values, 504, 10, DRAWS, np.random.default_rng(SEED))
    g1 = float((dd_old * 0.30 > EQUITY).mean())
    g2 = bool(np.all(dd_old >= we_old - 1e-9))
    g3 = maxdd(s_nt8)
    P("")
    P("%-12s %-52s %12s %12s  %s" % ("GATE", "SPEC", "SPEC", "OBSERVED", "VERDICT"))
    P("-" * 100)
    gates = [("CAP01B-G1", "reproduce CAP01's P(maxDD>E)=0.662 at ITS horizon", "0.662",
              "%.3f" % g1, abs(g1 - 0.662) < 0.01),
             ("CAP01B-G2", "maxdd >= worst_equity on EVERY draw (the identity)", "True",
              str(g2), g2),
             ("CAP01B-G3", "full-pool trade-level max DD == $51,891", "51,891",
              format(g3, ",.0f"), abs(g3 - 51891) / 51891 <= 0.01),
             ("CAP01B-G4", "traded sessions/year == 188.1 (1%)", "188.1",
              "%.1f" % per_yr, abs(per_yr - 188.1) / 188.1 <= 0.01)]
    ok = True
    for gid, d, sp, obs, passed in gates:
        ok &= passed
        P("%-12s %-52s %12s %12s  %s" % (gid, d, sp, obs, "PASS" if passed else "FAIL"))

    P("")
    P("THE CORRECTION, in one line, at CAP01's own horizon and scale:")
    P("  P(maxDD from peak > equity) = %.3f      <- what CAP01 called 'P(lose the account)'" % g1)
    P("  P(equity actually reaches 0) = %.3f     <- what that phrase means"
      % float((we_old * 0.30 > EQUITY).mean()))
    P("  mean total P&L over the horizon = $%+.0f at 0.30 scale on a $%.2f account --"
      % (float(np.mean(np.cumsum(np.zeros(1)))) if False else 0.0, EQUITY))
    L.pop()
    P("  the drift is what separates them: the modelled peak runs far above the start.")

    # ------------------------------------------------------------------ MAIN TABLE
    rows = []
    pools = {"full": s_meas, "warm": s_meas.iloc[37:]}
    # [D3] MNQ-commission-corrected series, per size
    for pool_name, base in pools.items():
        for mpn in (1, 2, 3):
            s = series(p1, xm, 20.65, 18.42, mnq_per_nq=mpn)
            if pool_name == "warm":
                s = s.iloc[37:]
            dd, we = boot(s.values, H2, 10, DRAWS, rng)
            sc = mpn / 10.0
            floor = EQUITY - MARGIN_FLOOR_PER_MNQ * 3 * mpn
            rows.append(dict(
                pool=pool_name, mnq_per_nq=mpn, horizon="2y_true",
                p50_dd_pct=100 * np.percentile(dd, 50) * sc / EQUITY,
                p90_dd_pct=100 * np.percentile(dd, 90) * sc / EQUITY,
                p_dd_gt100=float((dd * sc > EQUITY).mean()),
                p_ruin=float((we * sc > EQUITY).mean()),
                p_margin_call=float((we * sc > floor).mean())))
    tab = pd.DataFrame(rows)

    P("")
    P("=" * 100)
    P("THE CORRECTED TABLE -- MEASURED basis, MNQ commission charged, TRUE 2-year horizon")
    P("account $%.2f.  NO SIZE IS RECOMMENDED." % EQUITY)
    P("=" * 100)
    P("%-6s %4s %10s %10s %14s %12s %14s" %
      ("POOL", "MNQ", "p50 DD", "p90 DD", "P(DD>acct)", "P(RUIN)", "P(margin call)"))
    for _, r in tab.iterrows():
        P("%-6s %4d %9.0f%% %9.0f%% %14.3f %12.3f %14.3f" %
          (r["pool"], r.mnq_per_nq, r.p50_dd_pct, r.p90_dd_pct,
           r.p_dd_gt100, r.p_ruin, r.p_margin_call))

    # ------------------------------------------------------------------ DRIFT SENSITIVITY
    P("")
    P("=" * 100)
    P("DRIFT SENSITIVITY -- the input CAP01 never varied, and its answer is dominated by it")
    P("in-sample drift is $%.0f/wk full size; the campaign's HONEST band is $900-1,900."
      % (s_meas.mean() * len(s_meas) / 243.0))
    P("=" * 100)
    s3 = series(p1, xm, 20.65, 18.42, mnq_per_nq=3)
    base_wk = s3.sum() / 243.0
    P("%-26s %12s %12s" % ("ASSUMED EDGE ($/wk full)", "P(RUIN)", "P(margin call)"))
    drift_rows = []
    for lab, wk in [("in-sample (as CAP01)", base_wk), ("honest HIGH 1900", 1900.0),
                    ("honest CENTRAL 1450", 1450.0), ("honest LOW 900", 900.0),
                    ("ZERO EDGE", 0.0)]:
        shift = (wk - base_wk) * 243.0 / len(s3)          # re-centre, variance untouched
        dd, we = boot((s3 + shift).values, H2, 10, DRAWS, rng)
        pr = float((we * 0.30 > EQUITY).mean())
        pm = float((we * 0.30 > EQUITY - 900).mean())
        drift_rows.append(dict(edge=lab, wk=wk, p_ruin=pr, p_margin=pm))
        P("%-26s %12.3f %12.3f" % (lab, pr, pm))
    P("")
    P("=> at MnqPerNq=3 the defensible 2-year RUIN band is roughly %.0f%%-%.0f%%,"
      % (100 * drift_rows[0]["p_ruin"], 100 * drift_rows[3]["p_ruin"]))
    P("   reaching %.0f%% only if the edge is zero (the campaign puts P(edge~0) at 10-30%%)."
      % (100 * drift_rows[4]["p_ruin"]))

    # ------------------------------------------------------------------ D4 the worst days
    P("")
    both = pd.concat([p1.groupby("sess")["pnl"].sum().rename("p1"),
                      xm.groupby("sess")["pnl"].sum().rename("xm")], axis=1).fillna(0.0)
    comb = both.sum(axis=1)
    P("[D4] THE FIVE WORST SESSIONS, decomposed -- CAP01 called all five 'JOINT'")
    P("%-12s %10s %10s   %s" % ("session", "P1", "XM", "verdict"))
    for d in comb.nsmallest(5).index:
        a, b = both.loc[d, "p1"], both.loc[d, "xm"]
        v = "joint" if (a < 0 and b < 0) else ("XM ONLY -- P1 did not trade" if a == 0 else "single-leg")
        P("%-12s %10.0f %10.0f   %s" % (str(d.date()), a, b, v))
    al = both[(both.p1 != 0) & (both.xm != 0)]
    xm_days = both[both.xm != 0]
    P("")
    P("[D5] correlation POPULATION matters: rho = %.3f on n=%d (both legs traded, CAP01's "
      "choice)" % (al.p1.corr(al.xm), len(al)))
    P("     rho = %.3f on n=%d (all days XM traded -- the repo's canonical population)"
      % (xm_days.p1.corr(xm_days.xm), len(xm_days)))
    P("     rho = %.3f on all %d sessions" % (both.p1.corr(both.xm), len(both)))
    P("")
    P("[D6] 'sum of the legs' sums NON-CONTEMPORANEOUS troughs: P1's max-DD trough is %s,"
      % str(both["p1"].cumsum().idxmin().date()))
    P("     XM's is %s. Adding them is not an attainable no-diversification benchmark."
      % str(both["xm"].cumsum().idxmin().date()))

    tab.to_csv(os.path.join(OUT, "cap01b_table.csv"), index=False)
    P("")
    P("ALL GATES PASS" if ok else "*** GATE FAILURE ***")
    with open(os.path.join(OUT, "cap01b.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
