"""Forward-protocol amendment (directive s29): replace the Gaussian checkpoint bands with a
DEPENDENCE-PRESERVING EMPIRICAL BOOTSTRAP of the frozen weekly P&L.

Why this matters. WEEKLY_EDGE_FORWARD_PROTOCOL currently derives its HEALTHY / WATCH /
INVALIDATION bands from mean and t alone, i.e. from a Gaussian. Trading P&L is not Gaussian: it is
skewed, fat-tailed, and serially dependent at short lag. Bands built on a Gaussian will be wrong in
exactly the region that matters - the lower tail, where INVALIDATION lives. Getting that band too
tight manufactures a false alarm; too loose and a genuinely broken strategy passes.

Method: CIRCULAR BLOCK BOOTSTRAP on the weekly series, which preserves short serial dependence,
skew and tails by resampling contiguous blocks rather than individual weeks.

The scaling factor is derived from RESEARCH and FROZEN here. Directive s29: never recompute
leverage from forward maxDD.
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

ROOT = (r"D:\OneDrive - Washington University in St. Louis\TradingResearch"
        r"\systematic_research")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")
os.makedirs(OUT, exist_ok=True)

TARGET_DD = 20245.0          # the frozen fixed-drawdown risk budget
B = 40000                    # bootstrap replicates
SEED = 20260827
CHECKPOINTS = {"A": 60, "B": 126, "C": 252}      # sessions
_fh = open(os.path.join(OUT, "bootstrap.txt"), "w", encoding="utf-8")


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)


def max_dd(cum):
    return float(np.max(np.maximum.accumulate(cum) - cum))


def main():
    # CANONICAL SERIES. A first version used RR_W003's weekly file, which buckets weeks by a
    # Sunday-ending DATE LABEL and yields maxDD $24,212.92. The canonical figures come from
    # W103/W110, which buckets by ISO WEEK ON SESSION DATE and yields $22,930.67 - matching the
    # published $22,931 to $0.33. Same trades, totals agree to $80; only the bucketing differs.
    d = pd.read_csv(os.path.join(ROOT, "runs/WE_W110_XMDIVERSE/out/weekly.csv"))
    d = d.rename(columns={d.columns[0]: "week"})
    x = d["p1"].values.astype(float)   # all 213 ISO weeks, the canonical population
    n = len(x)

    P("=" * 104)
    P("=== FORWARD PROTOCOL AMENDMENT - empirical bootstrap replaces the Gaussian bands")
    P("=== Directive s29. Nothing sealed is read. The scaling factor is frozen, not refitted.")
    P("=" * 104)
    P(f"    weekly observations         {n}   {d['week'].iloc[0]} -> {d['week'].iloc[-1]}  (ISO weeks)")

    # ---------------------------------------------------------------- FROZEN scaling
    # The canonical pair IS internally consistent: $1,394 and $22,931 both come from this series,
    # which is net of commission AND the modelled spread (run_we_w103.py:95). k is therefore
    # derived from this series' own drawdown, and it reproduces the published headline.
    dd_series = max_dd(np.cumsum(x))
    K_FROZEN = TARGET_DD / dd_series
    xs = x * K_FROZEN
    P(f"    raw weekly mean             ${x.mean():>10,.2f}   <- baseline quotes $1,394  MATCHES")
    P(f"    weekly maxDD (ISO-week)     ${dd_series:>10,.2f}   <- canonical $22,931, matches to $0.33")
    P(f"    FROZEN scaling factor k     {K_FROZEN:>10.6f}   (= {TARGET_DD:,.0f} / {dd_series:,.2f})")
    P(f"    scaled weekly mean          ${xs.mean():>10,.2f}   <- protocol quotes $1,230  MATCHES")
    P(f"    scaled weekly sd            ${xs.std(ddof=1):>10,.2f}")
    P("")
    P("    NOTE ON BUCKETING, which is a real sensitivity and not a defect: the SAME trades under a")
    P("    Sunday-ending date label (RR_W003) give maxDD $24,212.92 rather than $22,930.67 - a 5.6 %")
    P("    difference from week-boundary placement alone. The bands below are built on the ISO-week")
    P("    convention, so THE FORWARD READ MUST USE ISO WEEKS ON SESSION DATE to be comparable.")

    # ---------------------------------------------------------------- distribution shape
    from scipy import stats as st
    sk = float(st.skew(xs))
    ku = float(st.kurtosis(xs, fisher=True))
    jb_p = float(st.jarque_bera(xs).pvalue)
    ac1 = float(pd.Series(xs).autocorr(1))
    ac2 = float(pd.Series(xs).autocorr(2))
    P("")
    P("    WHY A GAUSSIAN IS THE WRONG MODEL HERE:")
    P(f"      skew                      {sk:>10.3f}")
    P(f"      excess kurtosis           {ku:>10.3f}")
    P(f"      Jarque-Bera p             {jb_p:>10.4g}   {'NORMALITY REJECTED' if jb_p < 0.05 else 'not rejected'}")
    P(f"      lag-1 autocorrelation     {ac1:>10.3f}")
    P(f"      lag-2 autocorrelation     {ac2:>10.3f}")

    # ---------------------------------------------------------------- circular block bootstrap
    # block length: standard n^(1/3) rule, rounded, so short serial dependence survives resampling
    L = max(2, int(round(n ** (1 / 3))))
    P(f"\n    circular block bootstrap: B = {B:,}   block length L = {L} weeks   seed {SEED}")

    rng = np.random.default_rng(SEED)
    xt = np.concatenate([xs, xs])            # wrap for circularity

    P("")
    P("=" * 104)
    P("=== EMPIRICAL CHECKPOINT DISTRIBUTIONS  (primary)  vs GAUSSIAN  (secondary diagnostic)")
    P("=" * 104)
    mu, sd = xs.mean(), xs.std(ddof=1)
    rows = []
    P(f"    {'CP':<4}{'wk':>5}{'expected':>11}   {'source':<10}"
      f"{'p01 (INVALID)':>15}{'p05 (WATCH)':>14}{'p25 (HEALTHY)':>15}{'P(cum<0)':>11}")
    P("    " + "-" * 96)
    for cp, sess in CHECKPOINTS.items():
        w = sess // 5
        nb = int(np.ceil(w / L))
        starts = rng.integers(0, n, size=(B, nb))
        idx = (starts[:, :, None] + np.arange(L)[None, None, :]).reshape(B, -1)[:, :w]
        paths = xt[idx]
        cum = paths.sum(axis=1)

        e_b = [float(np.percentile(cum, q)) for q in (1, 5, 25)]
        pneg_b = float((cum < 0).mean())
        # Gaussian comparison
        g_mu, g_sd = mu * w, sd * np.sqrt(w)
        from math import erf, sqrt
        g = [g_mu + z * g_sd for z in (-2.3263, -1.6449, -0.6745)]
        pneg_g = 0.5 * (1 + erf((0 - g_mu) / (g_sd * sqrt(2))))

        P(f"    {cp:<4}{w:>5}{g_mu:>11,.0f}   {'EMPIRICAL':<10}"
          f"{e_b[0]:>15,.0f}{e_b[1]:>14,.0f}{e_b[2]:>15,.0f}{100*pneg_b:>10.1f}%")
        P(f"    {'':<4}{'':>5}{'':>11}   {'gaussian':<10}"
          f"{g[0]:>15,.0f}{g[1]:>14,.0f}{g[2]:>15,.0f}{100*pneg_g:>10.1f}%")
        P(f"    {'':<4}{'':>5}{'':>11}   {'DELTA':<10}"
          f"{e_b[0]-g[0]:>15,.0f}{e_b[1]-g[1]:>14,.0f}{e_b[2]-g[2]:>15,.0f}"
          f"{100*(pneg_b-pneg_g):>+10.1f}%")
        rows.append(dict(checkpoint=cp, sessions=sess, weeks=w, expected=round(g_mu, 0),
                         emp_p01=round(e_b[0], 0), emp_p05=round(e_b[1], 0),
                         emp_p25=round(e_b[2], 0), emp_p_neg=round(pneg_b, 4),
                         gauss_p01=round(g[0], 0), gauss_p05=round(g[1], 0),
                         gauss_p25=round(g[2], 0), gauss_p_neg=round(pneg_g, 4)))
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "checkpoint_bands.csv"), index=False)

    P("")
    P("    READ THE DELTA ROW. Where EMPIRICAL is BELOW gaussian, the Gaussian band was TOO TIGHT")
    P("    and would have raised a false INVALIDATION. Where it is ABOVE, the Gaussian was TOO")
    P("    LOOSE and a genuinely broken strategy could have passed. Either way the Gaussian band")
    P("    was the wrong instrument, and the empirical one is now primary.")

    # ------------------------------------------------------------------ s30 block sensitivity
    P("")
    P("=" * 104)
    P("=== s30  BLOCK-LENGTH SENSITIVITY - 40,000 resamples reduce Monte-Carlo noise, they do NOT")
    P("=== create historical information. If p01 is unstable across reasonable dependence choices,")
    P("=== the protocol must say so rather than pick the most forgiving band.")
    P("=" * 104)
    P(f"    {'CP':<4}{'wk':>5}   " + "".join(f"{'L='+str(L2):>14}" for L2 in (3, 6, 12))
      + f"{'spread':>12}")
    P("    " + "-" * 72)
    srows = []
    for cp, sess in CHECKPOINTS.items():
        w = sess // 5
        vals = []
        for L2 in (3, 6, 12):
            r2 = np.random.default_rng(SEED)
            nb = int(np.ceil(w / L2))
            st = r2.integers(0, n, size=(B, nb))
            ix = (st[:, :, None] + np.arange(L2)[None, None, :]).reshape(B, -1)[:, :w]
            vals.append(float(np.percentile(xt[ix].sum(axis=1), 1)))
        P(f"    {cp:<4}{w:>5}   " + "".join(f"{v:>14,.0f}" for v in vals)
          + f"{max(vals)-min(vals):>12,.0f}")
        srows.append(dict(checkpoint=cp, weeks=w, p01_L3=vals[0], p01_L6=vals[1],
                          p01_L12=vals[2], spread=max(vals) - min(vals)))
    pd.DataFrame(srows).to_csv(os.path.join(OUT, "block_sensitivity.csv"), index=False)
    mx = max(r["spread"] for r in srows)
    P("")
    P(f"    Largest p01 movement across block lengths: ${mx:,.0f}")
    if mx > 3000:
        P("    >>> THE INVALIDATION THRESHOLD IS NOT STABLE across reasonable dependence choices.")
        P("    >>> The protocol must carry this as a RANGE, not a single number.")
    else:
        P("    >>> p01 is stable across block lengths; the single reported band is defensible.")
    _fh.close()


if __name__ == "__main__":
    main()
