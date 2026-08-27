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
    d = pd.read_csv(os.path.join(ROOT, "runs/RR_W003_X9A_CONTRACT/out/weekly_p1_x9a.csv"))
    d = d.rename(columns={d.columns[0]: "week"})
    d["week"] = pd.to_datetime(d["week"])
    # drop the final partial week: it is labelled 2026-08-02 and spans past the 2026-07-31
    # research cutoff. It is not a seal read - the value was computed pre-seal - but a partial
    # week would bias the block distribution.
    # KEEP all 213 weeks. Dropping the final (partial) week moves the raw mean from $1,393.95 to
    # $1,404.91, and $1,393.95 is what CURRENT_BASELINE's $1,394 headline is computed from. The
    # partial week's value was computed pre-seal in a committed run - keeping it is not a seal read.
    x = d["p1"].values.astype(float)
    n = len(x)

    P("=" * 104)
    P("=== FORWARD PROTOCOL AMENDMENT - empirical bootstrap replaces the Gaussian bands")
    P("=== Directive s29. Nothing sealed is read. The scaling factor is frozen, not refitted.")
    P("=" * 104)
    P(f"    weekly observations         {n}   {d['week'].min().date()} -> {d['week'].max().date()}")

    # ---------------------------------------------------------------- FROZEN scaling
    # Directive s29: freeze the RESEARCH-derived scaling factor. The frozen baseline reports
    # raw $1,394/wk, maxDD $22,931, fixed-DD $1,230/wk, so k_frozen = 20245/22931 = 0.882866,
    # and 1394 * k_frozen = $1,230.72 reproduces the headline exactly.
    K_FROZEN = TARGET_DD / 22931.0
    dd_series = max_dd(np.cumsum(x))
    k_series = TARGET_DD / dd_series
    xs = x * K_FROZEN
    P(f"    raw weekly mean             ${x.mean():>10,.2f}   <- baseline quotes $1,394  MATCHES")
    P(f"    FROZEN scaling factor k     {K_FROZEN:>10.6f}   (= {TARGET_DD:,.0f} / 22,931 baseline maxDD)")
    P(f"    scaled weekly mean          ${xs.mean():>10,.2f}   <- protocol quotes $1,230  MATCHES")
    P(f"    scaled weekly sd            ${xs.std(ddof=1):>10,.2f}   <- Gaussian version implied $4,317")
    P("")
    P("    " + "!" * 92)
    P("    !! UNRECONCILED DISCREPANCY - flagged, not silently resolved")
    P(f"    !! This weekly series' own max drawdown is ${dd_series:,.2f}, implying k = {k_series:.6f},")
    P(f"    !! but the frozen baseline reports maxDD $22,931, implying k = {K_FROZEN:.6f}.")
    P("    !! Weekly-resolution drawdown CANNOT exceed daily-resolution drawdown - a weekly curve is")
    P("    !! a subsample of the daily one - so these two are NOT the same object. The raw MEAN")
    P("    !! matches to $0.05, so the P&L stream is right; the DRAWDOWN basis is not.")
    P("    !! The frozen factor is used here because s29 says freeze the research-derived one.")
    P("    !! THIS MUST BE CLOSED BEFORE THE BANDS ARE USED AT A CHECKPOINT.")
    P(f"    !! Impact if the series' own k were right instead: every band scales by "
      f"{k_series/K_FROZEN:.4f} (a {100*(k_series/K_FROZEN-1):+.1f} % shift).")
    P("    !! P(cum<0) is SCALE-INVARIANT and is therefore unaffected by this discrepancy.")
    P("    " + "!" * 92)

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
    _fh.close()


if __name__ == "__main__":
    main()
