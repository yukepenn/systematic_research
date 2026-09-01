# -*- coding: utf-8 -*-
"""CAP01 -- capital adequacy and ruin probability for the live MNQ book.

Spec: runs/CAP01_CAPITAL_RUIN_20260901/spec.yaml, committed before this file produced a number.
EVIDENCE STATUS: DISCOVERY_CONSUMED. In-sample, post-selection. Every output is a LOWER BOUND.

Gates G1-G4 reproduce the repo's recorded figures BEFORE any new number is quoted. The
GATE/SPEC/OBSERVED/PASS-FAIL table is printed by this program and never assembled by hand.
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

SRC = os.path.join(REPO, "runs", "G2_AUG_INCUMBENT_READ_20260830", "out")
EQUITY = 10206.86                       # machine-read 2026-09-01 05:04 ET
SEED = 20260901
DRAWS = 20000
HORIZONS = {"1y": 252, "2y": 504}
BLOCKS = [5, 10, 21]

COST_BASES = [                          # (name, p1 spread add $/ctrRT, xm spread add)
    ("NT8", 0.00, 0.00),
    ("RESEARCH_MODEL", 14.44, 12.50),
    ("MEASURED", 20.65, 18.42),
    ("HOSTILE", 28.69, 28.69),
]

L = []
def P(s=""):
    print(s)
    L.append(s)


# ------------------------------------------------------------------ load & session-map
def load(name):
    df = pd.read_csv(os.path.join(SRC, name + ".csv"))
    df["et"] = pd.to_datetime(df["et"])
    df["xt"] = pd.to_datetime(df["xt"])
    # session boundary 18:00 ET: a stamp at/after 18:00 belongs to the NEXT session.
    # A trade is attributed to the session containing its EXIT (spec).
    df["sess"] = (df["xt"] + pd.Timedelta(hours=6)).dt.normalize()
    return df


def sess_series(p1, xm, p1_add, xm_add):
    """Combined M_11 session P&L at FULL SIZE, on one cost basis.

    `pnl` already includes commission. Spread is an ADDEND charged per contract round turn
    (research_sdk/cost_model.py: SPREAD_ONLY figures are addends, never totals).
    """
    a = p1.assign(v=p1["pnl"] - p1_add * p1["qty"])
    b = xm.assign(v=xm["pnl"] - xm_add * xm["qty"])
    s = pd.concat([a[["sess", "v"]], b[["sess", "v"]]]).groupby("sess")["v"].sum()
    return s.sort_index()


def maxdd(x):
    """Peak-to-trough on the cumulative curve, in dollars. Positive number."""
    c = np.cumsum(np.asarray(x, float))
    return float(np.max(np.maximum.accumulate(np.concatenate([[0.0], c])) -
                        np.concatenate([[0.0], c])))


# ------------------------------------------------------------------------- bootstrap
def stationary_boot_maxdd(x, horizon, mean_block, draws, rng, chunk=4000):
    """Politis-Romano stationary bootstrap. Geometric block lengths, circular wrap.

    Sessions are resampled as WHOLE UNITS so the regime-dependent P1/XM correlation
    survives. IID shuffling is forbidden as the primary model -- it destroys the clustering
    that makes drawdowns, and this book's worst month is four consecutive joint-loss days.
    """
    x = np.asarray(x, float)
    n = len(x)
    p = 1.0 / mean_block
    out = np.empty(draws, float)
    done = 0
    while done < draws:
        k = min(chunk, draws - done)
        idx = np.empty((k, horizon), np.int64)
        idx[:, 0] = rng.integers(0, n, k)
        for j in range(1, horizon):
            newblk = rng.random(k) < p
            idx[:, j] = np.where(newblk, rng.integers(0, n, k), (idx[:, j - 1] + 1) % n)
        v = x[idx]
        c = np.cumsum(v, axis=1)
        run = np.maximum.accumulate(np.concatenate([np.zeros((k, 1)), c], axis=1), axis=1)
        out[done:done + k] = np.max(run - np.concatenate([np.zeros((k, 1)), c], axis=1), axis=1)
        done += k
    return out


def moving_block_maxdd(x, horizon, block, draws, rng, chunk=4000):
    x = np.asarray(x, float)
    n = len(x)
    nb = int(np.ceil(horizon / block))
    out = np.empty(draws, float)
    done = 0
    while done < draws:
        k = min(chunk, draws - done)
        starts = rng.integers(0, n, (k, nb))
        idx = (starts[:, :, None] + np.arange(block)[None, None, :]) % n
        idx = idx.reshape(k, -1)[:, :horizon]
        v = x[idx]
        c = np.cumsum(v, axis=1)
        z = np.zeros((k, 1))
        run = np.maximum.accumulate(np.concatenate([z, c], axis=1), axis=1)
        out[done:done + k] = np.max(run - np.concatenate([z, c], axis=1), axis=1)
        done += k
    return out


# ------------------------------------------------------------------------------- main
def main():
    rng = np.random.default_rng(SEED)
    p1, xm = load("p1_trades_full"), load("xm_trades_full")

    P("=" * 96)
    P("CAP01 -- CAPITAL ADEQUACY AND RUIN PROBABILITY   (spec committed before results)")
    P("EVIDENCE STATUS: DISCOVERY_CONSUMED -- in-sample, post-selection. LOWER BOUND on risk.")
    P("=" * 96)
    P("P1 trades %d   XM trades %d   account $%s" % (len(p1), len(xm), format(EQUITY, ",.2f")))

    base = {n: sess_series(p1, xm, a, b) for n, a, b in COST_BASES}
    s_nt8 = base["NT8"]
    P("sessions %d   %s -> %s" % (len(s_nt8), s_nt8.index[0].date(), s_nt8.index[-1].date()))

    # ---------------------------------------------------------------- GATES
    warm = s_nt8.iloc[37:]
    g = [
        ("CAP01-G1", "full trade-level max DD == $51,891 (1%)", 51891.0, maxdd(s_nt8)),
        ("CAP01-G2", "warm-only max DD == $36,943 (1%)", 36943.0, maxdd(warm)),
        ("CAP01-G3", "combined net == $537,353 (1%)", 537353.0, float(s_nt8.sum())),
    ]
    P("")
    P("%-10s %-42s %14s %14s  %s" % ("GATE", "SPEC", "SPEC VAL", "OBSERVED", "VERDICT"))
    P("-" * 96)
    gate_ok = True
    for gid, desc, spec, obs in g:
        ok = abs(obs - spec) / abs(spec) <= 0.01
        gate_ok &= ok
        P("%-10s %-42s %14s %14s  %s"
          % (gid, desc, format(spec, ",.0f"), format(obs, ",.0f"), "PASS" if ok else "FAIL"))

    # ---------------------------------------------------------------- OBSERVED
    P("")
    P("OBSERVED, FULL SIZE (1 NQ + 1 NQ), by cost basis")
    P("%-16s %12s %12s %12s %12s %12s" %
      ("BASIS", "NET", "maxDD_sess", "worst_day", "worst_wk", "worst_20d"))
    rows = []
    for n, _, _ in COST_BASES:
        s = base[n]
        wk = s.groupby(pd.Series(s.index).dt.to_period("W").values).sum()
        r20 = s.rolling(20).sum().min()
        rows.append(dict(basis=n, net=s.sum(), maxdd=maxdd(s), worst_day=s.min(),
                         worst_week=wk.min(), worst_20d=r20))
        P("%-16s %12s %12s %12s %12s %12s" %
          (n, format(s.sum(), ",.0f"), format(maxdd(s), ",.0f"), format(s.min(), ",.0f"),
           format(wk.min(), ",.0f"), format(r20, ",.0f")))
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "cap01_observed.csv"), index=False)

    # per-leg and joint structure (NT8 basis)
    sp = p1.groupby("sess")["pnl"].sum().sort_index()
    sx = xm.groupby("sess")["pnl"].sum().sort_index()
    both = pd.concat([sp.rename("p1"), sx.rename("xm")], axis=1).fillna(0.0)
    aligned = both[(both["p1"] != 0) & (both["xm"] != 0)]
    joint_loss = ((aligned["p1"] < 0) & (aligned["xm"] < 0)).mean()
    either_loss = ((aligned["p1"] < 0) | (aligned["xm"] < 0)).mean()
    P("")
    P("PER-LEG (NT8 basis):  P1 maxDD $%s   XM maxDD $%s   sum-of-legs $%s   combined $%s"
      % (format(maxdd(sp), ",.0f"), format(maxdd(sx), ",.0f"),
         format(maxdd(sp) + maxdd(sx), ",.0f"), format(maxdd(s_nt8), ",.0f")))
    P("JOINT (both legs active, n=%d):  P(both lose) %.3f   P(either loses) %.3f   "
      "P(both | either) %.3f   corr %.3f"
      % (len(aligned), joint_loss, either_loss, joint_loss / either_loss,
         aligned["p1"].corr(aligned["xm"])))
    P("WORST 5 JOINT DAYS: " + ", ".join(
        "%s $%s" % (d.date(), format(v, ",.0f"))
        for d, v in s_nt8.nsmallest(5).items()))

    # year cuts
    P("")
    P("BY YEAR (NT8 basis):  " + "   ".join(
        "%s net $%s dd $%s" % (y, format(v.sum(), ",.0f"), format(maxdd(v), ",.0f"))
        for y, v in s_nt8.groupby(pd.Series(s_nt8.index).dt.year.values)))

    # ---------------------------------------------------------------- BOOTSTRAP
    P("")
    P("=" * 96)
    P("DEPENDENCE-AWARE RESAMPLING -- stationary bootstrap, sessions as whole units")
    P("%d draws, seed %d. A bootstrap tail is NOT a bound." % (DRAWS, SEED))
    P("=" * 96)
    P("%-16s %-4s %-5s %10s %10s %10s %10s %10s" %
      ("BASIS", "HOR", "BLOCK", "p50", "p75", "p90", "p95", "p99"))
    boot = []
    for n, _, _ in COST_BASES:
        x = base[n].values
        for hname, h in HORIZONS.items():
            for b in BLOCKS:
                d = stationary_boot_maxdd(x, h, b, DRAWS, rng)
                q = np.percentile(d, [50, 75, 90, 95, 99])
                boot.append(dict(basis=n, horizon=hname, block=b, method="stationary",
                                 p50=q[0], p75=q[1], p90=q[2], p95=q[3], p99=q[4]))
                P("%-16s %-4s %-5d %10s %10s %10s %10s %10s"
                  % (n, hname, b, *[format(v, ",.0f") for v in q]))
    # cross-check with a different resampler on the headline basis
    for hname, h in HORIZONS.items():
        d = moving_block_maxdd(base["MEASURED"].values, h, 10, DRAWS, rng)
        q = np.percentile(d, [50, 75, 90, 95, 99])
        boot.append(dict(basis="MEASURED", horizon=hname, block=10, method="moving_block",
                         p50=q[0], p75=q[1], p90=q[2], p95=q[3], p99=q[4]))
        P("%-16s %-4s %-5s %10s %10s %10s %10s %10s"
          % ("MEASURED(mvblk)", hname, 10, *[format(v, ",.0f") for v in q]))
    pd.DataFrame(boot).to_csv(os.path.join(OUT, "cap01_bootstrap.csv"), index=False)

    bdf = pd.DataFrame(boot)
    q50 = float(bdf[(bdf.basis == "NT8") & (bdf.horizon == "1y") &
                    (bdf.block == 10) & (bdf.method == "stationary")]["p50"].iloc[0])
    g.append(("CAP01-G4", "resampled p50 1y DD finite, >0, <= sample max", maxdd(s_nt8), q50))
    ok4 = 0 < q50 <= maxdd(s_nt8)
    gate_ok &= ok4
    P("")
    P("%-10s %-42s %14s %14s  %s" % ("CAP01-G4", "p50 1y DD finite,>0,<= sample max",
                                      format(maxdd(s_nt8), ",.0f"), format(q50, ",.0f"),
                                      "PASS" if ok4 else "FAIL"))

    # ---------------------------------------------------------------- RUIN TABLE
    P("")
    P("=" * 96)
    P("THE OWNER-FACING TABLE -- risk of each size. NO SIZE IS RECOMMENDED HERE.")
    P("account $%s   live scale = MnqPerNq / 10" % format(EQUITY, ",.2f"))
    P("=" * 96)
    ruin = []
    for n, _, _ in COST_BASES:
        x = base[n].values
        for hname, h in HORIZONS.items():
            d = stationary_boot_maxdd(x, h, 10, DRAWS, rng)
            for mpn in (1, 2, 3):
                sc = mpn / 10.0
                sd = d * sc
                ruin.append(dict(
                    basis=n, horizon=hname, mnq_per_nq=mpn,
                    p50_pct=100 * np.percentile(sd, 50) / EQUITY,
                    p90_pct=100 * np.percentile(sd, 90) / EQUITY,
                    p99_pct=100 * np.percentile(sd, 99) / EQUITY,
                    p_gt25=float((sd > 0.25 * EQUITY).mean()),
                    p_gt50=float((sd > 0.50 * EQUITY).mean()),
                    p_gt75=float((sd > 0.75 * EQUITY).mean()),
                    p_gt100=float((sd > 1.00 * EQUITY).mean()),
                    observed_sample_max_pct=100 * maxdd(base[n]) * sc / EQUITY))
    rdf = pd.DataFrame(ruin)
    rdf.to_csv(os.path.join(OUT, "cap01_ruin_table.csv"), index=False)

    for hname in HORIZONS:
        P("")
        P("--- horizon %s, block 10 sessions ---" % hname)
        P("%-16s %4s %9s %9s %9s %8s %8s %8s %8s" %
          ("BASIS", "MNQ", "p50 %eq", "p90 %eq", "p99 %eq",
           "P>25%", "P>50%", "P>75%", "P>100%"))
        for _, r in rdf[rdf.horizon == hname].iterrows():
            P("%-16s %4d %8.0f%% %8.0f%% %8.0f%% %8.3f %8.3f %8.3f %8.3f" %
              (r.basis, r.mnq_per_nq, r.p50_pct, r.p90_pct, r.p99_pct,
               r.p_gt25, r.p_gt50, r.p_gt75, r.p_gt100))

    # the size at which 2y p90 first exceeds the account, on the MEASURED basis
    m = rdf[(rdf.horizon == "2y") & (rdf.basis == "MEASURED")]
    P("")
    for _, r in m.iterrows():
        P("MEASURED basis, 2-year: MnqPerNq=%d -> p90 DD = %.0f%% of the account, "
          "P(lose the account) = %.1f%%" % (r.mnq_per_nq, r.p90_pct, 100 * r.p_gt100))

    P("")
    P("ALL GATES PASS" if gate_ok else "*** GATE FAILURE -- numbers above are not trustworthy ***")
    with open(os.path.join(OUT, "cap01.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    return 0 if gate_ok else 1


if __name__ == "__main__":
    sys.exit(main())
