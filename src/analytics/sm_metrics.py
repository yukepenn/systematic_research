"""sm_metrics.py — SYSTEM_MASTER frozen metric suite (CONVENTIONS.md §4).

One implementation for every track. Daily vectors are session-keyed (18:00 ET roll),
computed on ALL sessions of the supplied calendar (flat days = 0), ann = 252,
std ddof = 1. logG uses a $100k base.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

ANN = 252
BASE = 100_000.0


def _dd_series(cum: np.ndarray) -> np.ndarray:
    peak = np.maximum.accumulate(cum)
    return cum - peak


def metrics(daily: pd.Series, base: float = BASE) -> dict:
    """daily: pd.Series indexed by session date (datetime-like), $ P&L, zero-filled."""
    x = daily.to_numpy(dtype=float)
    idx = pd.to_datetime(daily.index)
    n = x.size
    if n == 0:
        return {}
    mu, sd = x.mean(), x.std(ddof=1)
    downside = x[x < 0].std(ddof=1) if (x < 0).sum() > 1 else np.nan
    cum = np.cumsum(x)
    dd = _dd_series(cum)
    maxdd = dd.min()
    # drawdown episodes
    in_dd = dd < 0
    episodes = []
    start = None
    for i in range(n):
        if in_dd[i] and start is None:
            start = i
        elif not in_dd[i] and start is not None:
            episodes.append((start, i))
            start = None
    if start is not None:
        episodes.append((start, n))
    ep_depths = [dd[s:e].min() for s, e in episodes] if episodes else [0.0]
    ep_lens = [e - s for s, e in episodes] if episodes else [0]
    # log growth on base
    eq = base + cum
    logG = np.log(eq[-1] / base) if eq.min() > 0 else -np.inf
    # calendar aggregations
    s = pd.Series(x, index=idx)
    wk = s.resample("W").sum()
    mo = s.resample("ME").sum()
    qt = s.resample("QE").sum()

    def longest_neg_streak(v):
        best = cur = 0
        for val in v:
            cur = cur + 1 if val < 0 else 0
            best = max(best, cur)
        return best

    def roll_min(v, w):
        if len(v) < w:
            return np.nan
        c = np.concatenate([[0.0], np.cumsum(v)])
        return (c[w:] - c[:-w]).min()

    es5 = np.mean(np.sort(x)[: max(1, int(np.floor(0.05 * n)))])
    ulcer = np.sqrt(np.mean((dd / base) ** 2)) * 100.0
    ann_ret = mu * ANN
    return {
        "n_sessions": n,
        "net": float(cum[-1]),
        "logG_100k": float(logG),
        "ann_geo_pct": float((np.exp(logG * ANN / n) - 1) * 100) if np.isfinite(logG) else np.nan,
        "sharpe": float(mu / sd * np.sqrt(ANN)) if sd > 0 else 0.0,
        "sortino": float(mu / downside * np.sqrt(ANN)) if downside and downside > 0 else np.nan,
        "calmar": float(ann_ret / abs(maxdd)) if maxdd < 0 else np.inf,
        "max_dd": float(maxdd),
        "median_dd_episode": float(np.median(ep_depths)),
        "p95_dd_episode": float(np.percentile(ep_depths, 5)),  # 5th pct = deep tail
        "ulcer_pct_100k": float(ulcer),
        "tuw_frac": float(in_dd.mean()),
        "longest_recovery_sessions": int(max(ep_lens)) if ep_lens else 0,
        "es5_daily": float(es5),
        "worst_day": float(x.min()),
        "worst_week": float(wk.min()) if len(wk) else np.nan,
        "worst_month": float(mo.min()) if len(mo) else np.nan,
        "worst_quarter": float(qt.min()) if len(qt) else np.nan,
        "pos_day_frac": float((x > 0).mean()),
        "pos_week_frac": float((wk > 0).mean()) if len(wk) else np.nan,
        "pos_month_frac": float((mo > 0).mean()) if len(mo) else np.nan,
        "longest_losing_day_streak": longest_neg_streak(x),
        "longest_losing_week_streak": longest_neg_streak(wk.to_numpy()),
        "longest_losing_month_streak": longest_neg_streak(mo.to_numpy()),
        "roll20_min": float(roll_min(x, 20)),
        "roll60_min": float(roll_min(x, 60)),
        "roll120_min": float(roll_min(x, 120)),
        "top10_day_share": float(np.sort(x)[-10:].sum() / cum[-1]) if cum[-1] > 0 and n >= 10 else np.nan,
    }


def vol_match_scale(daily: pd.Series, target_vol: float) -> float:
    """Scalar that equalizes realized daily std to target_vol."""
    sd = daily.std(ddof=1)
    return float(target_vol / sd) if sd > 0 else np.nan


def block_bootstrap_delta(a: np.ndarray, b: np.ndarray, block: int = 5,
                          n_boot: int = 10_000, seed: int = 20260808,
                          stat=None) -> dict:
    """P(stat(a) - stat(b) <= 0) under circular session-block bootstrap of the
    paired daily vectors. Default stat = mean."""
    if stat is None:
        stat = lambda v: v.mean()
    n = len(a)
    rng = np.random.default_rng(seed)
    nblocks = int(np.ceil(n / block))
    deltas = np.empty(n_boot)
    for i in range(n_boot):
        starts = rng.integers(0, n, nblocks)
        idx = (starts[:, None] + np.arange(block)[None, :]).ravel() % n
        idx = idx[:n]
        deltas[i] = stat(a[idx]) - stat(b[idx])
    point = stat(a) - stat(b)
    return {"delta": float(point), "p_leq_0": float((deltas <= 0).mean()),
            "ci_lo": float(np.percentile(deltas, 2.5)),
            "ci_hi": float(np.percentile(deltas, 97.5))}


def right_tail_retention(trades_base: pd.DataFrame, trades_new: pd.DataFrame,
                         key=("entry_time", "vm"), net_col="net") -> dict:
    """Top-1% trade retention: sum of the NEW P&L captured on the trades that were
    the BASE's top-1% winners (matched by key), / base top-1% sum."""
    b = trades_base.copy()
    thresh = b[net_col].quantile(0.99)
    top = b[b[net_col] >= thresh]
    kb = list(key)
    merged = top.merge(trades_new, on=kb, how="left", suffixes=("_b", "_n"))
    base_sum = top[net_col].sum()
    new_sum = merged[net_col + "_n"].fillna(0.0).sum()
    return {"top1pct_trades": len(top), "base_sum": float(base_sum),
            "new_sum": float(new_sum),
            "retention": float(new_sum / base_sum) if base_sum else np.nan}
