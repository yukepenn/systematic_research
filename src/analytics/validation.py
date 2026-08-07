"""validation.py — CSCV/PBO, DSR/PSR, block bootstrap and nested walk-forward.

Everything here consumes a T x N matrix of DAILY P&L vectors (rows = trading days,
columns = configurations), which every sweep archives. Nothing here re-runs a backtest.

References implemented (see research/deep_research/DR-06.md):
  Bailey, Borwein, Lopez de Prado, Zhu — CSCV / Probability of Backtest Overfitting
  Bailey & Lopez de Prado — Deflated and Probabilistic Sharpe Ratio
  Politis & Romano — stationary bootstrap
"""
from __future__ import annotations

import itertools
import math

import numpy as np
import pandas as pd
from scipy import stats


# ---------------------------------------------------------------- Sharpe helpers

def sharpe(x, ann=252):
    x = np.asarray(x, float)
    s = x.std(ddof=1)
    return float(x.mean() / s * math.sqrt(ann)) if s > 0 else 0.0


def psr(x, sr_benchmark=0.0, ann=252):
    """Probabilistic Sharpe Ratio with the empirical skew/kurtosis correction."""
    x = np.asarray(x, float)
    n = len(x)
    if n < 3 or x.std(ddof=1) == 0:
        return np.nan
    sr = x.mean() / x.std(ddof=1)                    # per-period
    srb = sr_benchmark / math.sqrt(ann)
    g3 = stats.skew(x, bias=False)
    g4 = stats.kurtosis(x, fisher=False, bias=False)
    denom = math.sqrt(max(1e-12, 1 - g3 * sr + (g4 - 1) / 4 * sr ** 2))
    return float(stats.norm.cdf((sr - srb) * math.sqrt(n - 1) / denom))


def dsr(x, n_trials, sr_variance=None, all_sr=None, ann=252):
    """Deflated Sharpe Ratio: PSR against the benchmark expected max SR of n_trials."""
    x = np.asarray(x, float)
    if sr_variance is None:
        if all_sr is None:
            raise ValueError("need sr_variance or all_sr")
        sr_variance = float(np.var(np.asarray(all_sr, float) / math.sqrt(ann), ddof=1))
    e = 0.5772156649015329
    z1 = stats.norm.ppf(1 - 1.0 / max(n_trials, 2))
    z2 = stats.norm.ppf(1 - 1.0 / (max(n_trials, 2) * math.e))
    sr0 = math.sqrt(sr_variance) * ((1 - e) * z1 + e * z2)     # per-period benchmark
    return psr(x, sr_benchmark=sr0 * math.sqrt(ann), ann=ann)


# ---------------------------------------------------------------- CSCV / PBO

def cscv_pbo(matrix, n_blocks=16, ann=252, metric=sharpe, max_combos=20000, seed=0):
    """Combinatorially Symmetric Cross-Validation -> Probability of Backtest Overfitting.

    matrix: DataFrame (T x N) of daily P&L, columns = configurations.
    Splits time into n_blocks contiguous blocks, forms every half/half split,
    picks the in-sample winner, records its out-of-sample rank.

    Returns dict with pbo, the logit series, and OOS-degradation regression stats.
    """
    rng = np.random.default_rng(seed)
    M = np.asarray(matrix, float)
    T, N = M.shape
    if N < 2:
        return {"pbo": np.nan, "n_splits": 0, "n_configs": N}
    n_blocks -= n_blocks % 2
    edges = np.linspace(0, T, n_blocks + 1).astype(int)
    blocks = [np.arange(edges[i], edges[i + 1]) for i in range(n_blocks)]

    combos = list(itertools.combinations(range(n_blocks), n_blocks // 2))
    if len(combos) > max_combos:
        idx = rng.choice(len(combos), max_combos, replace=False)
        combos = [combos[i] for i in idx]

    logits, is_perf, oos_perf = [], [], []
    for cis in combos:
        cis = set(cis)
        i_is = np.concatenate([blocks[b] for b in sorted(cis)])
        i_oos = np.concatenate([blocks[b] for b in range(n_blocks) if b not in cis])
        s_is = np.array([metric(M[i_is, j], ann) for j in range(N)])
        s_oos = np.array([metric(M[i_oos, j], ann) for j in range(N)])
        n_star = int(np.argmax(s_is))
        # relative rank of the IS winner within the OOS distribution
        r = (stats.rankdata(s_oos)[n_star]) / (N + 1)
        r = min(max(r, 1e-6), 1 - 1e-6)
        logits.append(math.log(r / (1 - r)))
        is_perf.append(s_is[n_star])
        oos_perf.append(s_oos[n_star])

    logits = np.asarray(logits)
    slope, intercept, rval, pval, _ = stats.linregress(is_perf, oos_perf)
    return {
        "pbo": float((logits <= 0).mean()),
        "n_splits": len(combos), "n_configs": N, "n_blocks": n_blocks,
        "median_logit": float(np.median(logits)),
        "oos_median": float(np.median(oos_perf)),
        "is_median": float(np.median(is_perf)),
        "p_oos_negative": float((np.asarray(oos_perf) < 0).mean()),
        "degradation_slope": float(slope), "degradation_r": float(rval),
        "degradation_p": float(pval),
    }


# ---------------------------------------------------------------- bootstraps

def stationary_bootstrap(x, n_boot=2000, mean_block=20, seed=0):
    """Politis-Romano stationary bootstrap of a daily P&L series."""
    rng = np.random.default_rng(seed)
    x = np.asarray(x, float)
    n = len(x)
    p = 1.0 / mean_block
    out = np.empty((n_boot, n))
    for b in range(n_boot):
        idx = np.empty(n, dtype=int)
        i = rng.integers(n)
        for t in range(n):
            idx[t] = i
            if rng.random() < p:
                i = rng.integers(n)
            else:
                i = (i + 1) % n
        out[b] = x[idx]
    return out


def max_drawdown(pnl):
    eq = np.cumsum(np.asarray(pnl, float))
    return float((eq - np.maximum.accumulate(eq)).min())


def bootstrap_risk(x, n_boot=2000, mean_block=20, seed=0):
    """Compare iid-shuffle vs block-bootstrap drawdown distributions (DR06-H5)."""
    rng = np.random.default_rng(seed)
    x = np.asarray(x, float)
    iid = np.array([max_drawdown(rng.permutation(x)) for _ in range(n_boot)])
    blk = np.array([max_drawdown(p) for p in
                    stationary_bootstrap(x, n_boot, mean_block, seed)])
    return {
        "observed_dd": max_drawdown(x),
        "iid_p05_dd": float(np.percentile(iid, 5)),
        "block_p05_dd": float(np.percentile(blk, 5)),
        "iid_median_dd": float(np.median(iid)),
        "block_median_dd": float(np.median(blk)),
        "understatement_ratio": float(np.percentile(blk, 5) / np.percentile(iid, 5)),
    }


# ---------------------------------------------------------------- walk-forward

def walk_forward(matrix, train_days, test_days, step_days, selector, ann=252,
                 embargo_days=1):
    """Nested chronological evaluation.

    selector(train_slice_df) -> column label chosen for that fold.
    Returns a DataFrame, one row per outer fold, with the chosen config's OOS stats.
    """
    df = matrix
    T = len(df)
    rows = []
    start = 0
    while start + train_days + embargo_days + test_days <= T:
        tr = df.iloc[start: start + train_days]
        te = df.iloc[start + train_days + embargo_days:
                     start + train_days + embargo_days + test_days]
        pick = selector(tr)
        rows.append({
            "fold": len(rows),
            "train_start": df.index[start], "train_end": df.index[start + train_days - 1],
            "test_start": te.index[0], "test_end": te.index[-1],
            "pick": pick,
            "oos_net": float(te[pick].sum()),
            "oos_sharpe": sharpe(te[pick], ann),
            "oos_dd": max_drawdown(te[pick]),
            "is_sharpe": sharpe(tr[pick], ann),
            "oos_best_possible": float(te.sum().max()),
            "oos_median_config": float(te.sum().median()),
        })
        start += step_days
    return pd.DataFrame(rows)


def selector_argmax(train):
    return train.sum().idxmax()


def make_selector_neighbourhood(order, width=1):
    """Neighbourhood-smoothed selection (DR06-H4): rank by the median of each
    config's net over its +/- `width` neighbours in the given parameter order."""
    pos = {c: i for i, c in enumerate(order)}

    def sel(train):
        tot = train.sum()
        scores = {}
        for c in train.columns:
            i = pos[c]
            nb = [order[j] for j in range(max(0, i - width), min(len(order), i + width + 1))
                  if order[j] in tot.index]
            scores[c] = np.median([tot[x] for x in nb])
        return max(scores, key=scores.get)

    return sel
