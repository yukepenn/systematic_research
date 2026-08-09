"""primary_objective.py — the campaign's PRIMARY objective function (O1 + O1a).

A single scalar that can express a trade-off, replacing the deadlocked
"Sharpe AND CDaR AND top-10-retention" triple of hard gates:

    J(L) = CE_g(L) - lambda * P_ruin(L)

    CE_g   expected (== certainty-equivalent, under log utility) log growth rate,
           annualized, at the stated target leverage L, on ABSORBING paths
    P_ruin probability of hitting the stated ruin barrier within the stated horizon,
           estimated by bootstrap, reported under EACH of the three methods used by
           this repo's committed capital map, headline = the WORST (max) of the three

Everything pre-registered lives in runs/W17_C4_COMPLIANCE/O1_OBJECTIVE.md section 1.
The defaults below ARE that pre-registration; do not tune them.

The legacy triple (daily Sharpe, CDaR_0.95, top-10-day retention/share) is still computed
and returned, under the key `legacy_diagnostics_NOT_GATES`. It is a DIAGNOSTIC. It is not a
gate, not a threshold, and not a selection input.

O1a: the tail and ruin terms are computed BOTH on the daily-close series AND on the
bar-by-bar intraday mark-to-market path, on identical resampled session sequences, and the
GAP between them is returned explicitly.

Determinism: every bootstrap takes a fresh np.random.default_rng(seed). Given a seed the
module is bit-reproducible. Seed and resample count are echoed in the returned dict.

Nothing in this module establishes that future profitability is achievable. Every number is
a statistic of a fixed historical sample, or of resamples of that sample.
"""
from __future__ import annotations

import math
import os
from pathlib import Path

import numpy as np
import pandas as pd

# --------------------------------------------------------------------------------------
# PRE-REGISTERED CONSTANTS  (runs/W17_C4_COMPLIANCE/O1_OBJECTIVE.md section 1)
# --------------------------------------------------------------------------------------
SEED = 20260808                 # house default seed (smv2_common / sm_metrics / smv2i / smv2f)
N_BOOT = 2000                   # capital map / smv2f convention
HORIZON_SESSIONS = 504          # 2 years; matches C-P3 (runs/SMV2I_CURVE_READS/step2_cp3.py)
ANN = 252
DEFAULT_CAPITAL = 100_000.0     # sm_metrics.BASE / smv2f.CAP
DEFAULT_LEVERAGE = 1.0          # deployed champion size; the point C-P3 contests
DEFAULT_RUIN_DD_FRAC = 0.25     # capital-map mid-grid tolerance == the funded DD budget
DEFAULT_LAMBDA = 1.0            # out-of-horizon franchise opportunity cost, per yr
DEFAULT_CDAR_ALPHA = 0.95       # CDaR_0.95 == mean of the worst 5% of the drawdown series
DEFAULT_METHODS = ("moving5", "moving20", "stationary60")   # the committed capital map's trio
DIAGNOSTIC_METHODS = ("iid",)   # NOT one of the three headline methods; diagnostic only
LEVERAGE_GRID = (0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 3.0)
LAMBDA_GRID = (0.0, 0.5, 1.0, 2.0, 5.0)

# broker facts (research/operational/, W17 context) -- used only for the SECONDARY R2 read
MNQ_DAY_MARGIN = 100.0
MNQ_INITIAL_MARGIN = 4_343.38
PRE_RELEASE_MARGIN_MULT = 4.0   # "intraday margin may be set to 4X before key releases"
PRODUCT_A_MAX_CONTRACTS = 11    # measured from runs/SMV2M_MASTER_BUILD/out/nt8/smm_v2_bars.csv

# data-window guards
DEV_END = pd.Timestamp("2026-05-29")
LOCKED_FORWARD_START = pd.Timestamp("2026-08-01")

_EPS = 1e-12


# ======================================================================================
# loading
# ======================================================================================
def _read_tabular(src):
    p = str(src)
    if p.lower().endswith(".parquet"):
        return pd.read_parquet(p)
    return pd.read_csv(p)


def load_daily_pnl(src, *, date_col=None, pnl_col=None, dev_window="truncate"):
    """Load a daily $ P&L series.

    `src` may be:
      - a filesystem path to .csv / .parquet
      - a pd.Series (index = session dates)
      - a pd.DataFrame (date_col / pnl_col, or a 2-column [date, pnl] frame)
      - a 1-D array-like (no dates; window guards are skipped and that is flagged)

    dev_window:
      "truncate" (default) drop sessions after DEV_END (2026-05-29), record the drop
      "raise"              raise if any session is after DEV_END
      "off"                keep everything (data >= LOCKED_FORWARD_START still raises)

    Returns (pd.Series, dict of load provenance/flags).
    """
    flags = {"source": None, "dated": True, "n_truncated_post_dev": 0,
             "truncated_from": None, "warnings": []}

    if isinstance(src, pd.Series):
        s = src.astype(float).copy()
        flags["source"] = "pd.Series"
    elif isinstance(src, pd.DataFrame):
        s = _series_from_frame(src, date_col, pnl_col)
        flags["source"] = "pd.DataFrame"
    elif isinstance(src, (str, os.PathLike, Path)):
        flags["source"] = str(src)
        df = _read_tabular(src)
        s = _series_from_frame(df, date_col, pnl_col)
    else:
        arr = np.asarray(src, dtype=float).ravel()
        s = pd.Series(arr)
        flags["source"] = "array-like"

    if isinstance(s.index, pd.DatetimeIndex) or _index_is_datelike(s.index):
        s.index = pd.to_datetime(s.index)
        s = s.sort_index()
        if s.index.max() >= LOCKED_FORWARD_START:
            raise ValueError(
                f"LOCKED-FORWARD VIOLATION: series contains sessions on/after "
                f"{LOCKED_FORWARD_START.date()} (max = {s.index.max().date()}). "
                "research/operational/LOCKED_FORWARD.md forbids using this data here.")
        if s.index.max() > DEV_END:
            if dev_window == "raise":
                raise ValueError(f"series extends past dev end {DEV_END.date()} "
                                 f"(max = {s.index.max().date()})")
            if dev_window == "truncate":
                keep = s.index <= DEV_END
                flags["n_truncated_post_dev"] = int((~keep).sum())
                flags["truncated_from"] = str(s.index.max().date())
                flags["warnings"].append(
                    f"truncated {int((~keep).sum())} post-dev sessions "
                    f"(> {DEV_END.date()}) -- dev window only")
                s = s[keep]
    else:
        flags["dated"] = False
        flags["warnings"].append(
            "series has no date index -- LOCKED_FORWARD / dev-window guards NOT applied")

    s = s.astype(float)
    if s.isna().any():
        flags["warnings"].append(f"{int(s.isna().sum())} NaN days zero-filled")
        s = s.fillna(0.0)
    return s, flags


def _index_is_datelike(idx):
    try:
        pd.to_datetime(idx[:5])
        return True
    except Exception:
        return False


def _series_from_frame(df, date_col, pnl_col):
    df = df.copy()
    if pnl_col is not None:
        vals = df[pnl_col]
        if date_col is not None:
            return pd.Series(vals.to_numpy(float), index=pd.to_datetime(df[date_col]))
        return pd.Series(vals.to_numpy(float), index=df.index)
    if date_col is not None:
        other = [c for c in df.columns if c != date_col]
        if len(other) != 1:
            raise ValueError(f"ambiguous pnl column among {other}; pass pnl_col=")
        return pd.Series(df[other[0]].to_numpy(float), index=pd.to_datetime(df[date_col]))
    if df.shape[1] == 1:
        return pd.Series(df.iloc[:, 0].to_numpy(float), index=df.index)
    if df.shape[1] == 2:
        return pd.Series(df.iloc[:, 1].to_numpy(float), index=pd.to_datetime(df.iloc[:, 0]))
    raise ValueError(f"cannot infer date/pnl columns from {list(df.columns)}; "
                     "pass date_col= and pnl_col=")


# ======================================================================================
# bootstrap index generators
#   moving5 / moving20 / stationary60 are VERBATIM the three used by the committed
#   capital map (runs/PRODUCTB_ONECONTRACT_FINAL/build_parity_and_metrics.py::capital_map,
#   itself lifted from runs/SMV2F_LEVERAGE_ROBUST/smv2f.py).
#   stationary_pr* is the Politis-Romano *block-length* form used by
#   runs/SMV2I_CURVE_READS/smv2i_lib.py (the C-P3 disclosure), kept so that published
#   figure can be reproduced exactly.
#   iid is a DIAGNOSTIC only (validation.bootstrap_risk precedent), never a headline.
# ======================================================================================
def _idx_moving_block(n, path_len, block, n_boot, rng):
    k = int(np.ceil(path_len / block))
    starts = rng.integers(0, n, size=(n_boot, k))
    idx = (starts[:, :, None] + np.arange(block)[None, None, :]) % n
    return idx.reshape(n_boot, -1)[:, :path_len]


def _idx_stationary_step(n, path_len, mean_block, n_boot, rng):
    """capital-map / smv2f `idx_stationary`: at each step, restart with prob 1/mean_block."""
    p = 1.0 / mean_block
    idx = np.empty((n_boot, path_len), dtype=np.int64)
    cur = rng.integers(0, n, size=n_boot)
    for t in range(path_len):
        jump = rng.random(n_boot) < p
        cur = np.where(jump, rng.integers(0, n, size=n_boot), (cur + 1) % n)
        idx[:, t] = cur
    return idx


def _idx_stationary_pr(n, path_len, mean_block, n_boot, rng):
    """smv2i_lib.maxdd_dist_stationary: geometric block LENGTHS, uniform circular starts."""
    p = 1.0 / mean_block
    out = np.empty((n_boot, path_len), dtype=np.int64)
    for b in range(n_boot):
        pieces, filled = [], 0
        while filled < path_len:
            L = int(min(rng.geometric(p), path_len))
            s = int(rng.integers(0, n))
            take = min(L, path_len - filled)
            pieces.append(np.arange(s, s + take) % n)
            filled += take
        out[b] = np.concatenate(pieces)
    return out


def _idx_iid(n, path_len, n_boot, rng):
    return rng.integers(0, n, size=(n_boot, path_len))


def parse_method(method):
    """'moving5' -> ('moving', 5); 'stationary60' -> ('stationary', 60);
    'stationary_pr20' -> ('stationary_pr', 20); 'iid' -> ('iid', None)."""
    m = method.strip().lower()
    if m == "iid":
        return "iid", None
    for pre in ("stationary_pr", "stationary", "moving"):
        if m.startswith(pre):
            tail = m[len(pre):]
            if tail == "":
                raise ValueError(f"method '{method}' needs a block length, e.g. '{pre}20'")
            return pre, int(tail)
    raise ValueError(f"unknown bootstrap method '{method}'")


def make_indices(method, n, path_len, n_boot=N_BOOT, seed=SEED):
    """(n_boot, path_len) int matrix of resampled positions into a length-n series.

    Fresh np.random.default_rng(seed) per call -> deterministic and independently
    reproducible per method. With seed=20260808 this reproduces smv2i_lib's index draws
    for 'moving5' at path_len=504 exactly.
    """
    kind, blk = parse_method(method)
    rng = np.random.default_rng(seed)
    if kind == "moving":
        return _idx_moving_block(n, path_len, blk, n_boot, rng)
    if kind == "stationary":
        return _idx_stationary_step(n, path_len, blk, n_boot, rng)
    if kind == "stationary_pr":
        return _idx_stationary_pr(n, path_len, blk, n_boot, rng)
    return _idx_iid(n, path_len, n_boot, rng)


# ======================================================================================
# legacy diagnostics  (NOT gates)
# ======================================================================================
def daily_sharpe(x, ann=ANN):
    x = np.asarray(x, float)
    sd = x.std(ddof=1)
    return float(x.mean() / sd * math.sqrt(ann)) if sd > 0 else 0.0


def dollar_dd_series(x):
    eq = np.cumsum(np.asarray(x, float))
    return np.maximum.accumulate(eq) - eq


def cdar_dollar(x, alpha=DEFAULT_CDAR_ALPHA):
    """House convention (smv2i_lib.cdar / smv2_common CDaR5): mean of the worst
    (1-alpha) fraction of the end-of-day dollar drawdown series."""
    dd = np.sort(dollar_dd_series(x))[::-1]
    k = max(1, int((1.0 - alpha) * len(dd)))
    return float(dd[:k].mean())


def top10_day_share(x):
    x = np.asarray(x, float)
    net = x.sum()
    if len(x) < 10 or net <= 0:
        return float("nan")
    return float(np.sort(x)[-10:].sum() / net)


def top10_day_retention(x, baseline):
    """Retention of the BASELINE's ten best days: the evaluated series' P&L summed over the
    baseline's top-10 day positions, / the baseline's own top-10 sum. Requires aligned
    series (same calendar)."""
    b = np.asarray(baseline, float)
    v = np.asarray(x, float)
    if len(b) != len(v) or len(b) < 10:
        return float("nan")
    idx = np.argsort(b)[-10:]
    denom = b[idx].sum()
    return float(v[idx].sum() / denom) if denom != 0 else float("nan")


def legacy_diagnostics(x, baseline=None, alpha=DEFAULT_CDAR_ALPHA):
    x = np.asarray(x, float)
    out = {
        "_flag": "REPORTED DIAGNOSTIC ONLY -- NOT A GATE, NOT A SELECTION INPUT",
        "daily_sharpe_ann": daily_sharpe(x),
        "cdar_0.95_dollar": cdar_dollar(x, alpha),
        "max_dd_dollar": float(dollar_dd_series(x).max()),
        "top10_day_share": top10_day_share(x),
        "top10_day_retention_vs_baseline": (
            top10_day_retention(x, baseline) if baseline is not None else None),
        "net_dollar": float(x.sum()),
        "n_sessions": int(len(x)),
    }
    return out


# ======================================================================================
# core: levered log paths
# ======================================================================================
def log_increments_fixed_fraction(x, capital, leverage):
    """ell_d = log1p(L * x_d / C). Returns (loginc, n_nonpositive_equity_steps)."""
    r = leverage * np.asarray(x, float) / capital
    bad = r <= -1.0
    if bad.any():
        r = np.where(bad, -1.0 + _EPS, r)
    return np.log1p(r), int(bad.sum())


def _path_stats(loginc, ruin_log_thr, path_len, absorbing=True,
                cdar_alpha=DEFAULT_CDAR_ALPHA):
    """loginc: (n_paths, T) log increments. Returns per-path arrays."""
    cum = np.cumsum(loginc, axis=1)
    peak = np.maximum.accumulate(cum, axis=1)
    np.maximum(peak, 0.0, out=peak)             # equity starts at its own high-water mark
    dd = peak - cum                              # log drawdown, >= 0
    ruined = dd >= ruin_log_thr
    any_ruin = ruined.any(axis=1)
    T = cum.shape[1]
    first = np.where(any_ruin, ruined.argmax(axis=1), T - 1)
    rows = np.arange(cum.shape[0])
    term_abs = cum[rows, first]
    term_free = cum[:, -1]
    term = term_abs if absorbing else term_free
    maxdd_log = dd.max(axis=1)
    k = max(1, int((1.0 - cdar_alpha) * T))
    worst = -np.partition(-dd, k - 1, axis=1)[:, :k]
    cdar_log = worst.mean(axis=1)
    years = path_len / ANN
    return {
        "ruined": any_ruin,
        "first_ruin_step": first,
        "g_ann": term * (1.0 / years),
        "g_ann_nonabsorbing": term_free * (1.0 / years),
        "maxdd_log": maxdd_log,
        "maxdd_frac": 1.0 - np.exp(-maxdd_log),
        "cdar_log": cdar_log,
        "cdar_frac": 1.0 - np.exp(-cdar_log),
        "terminal_log_wealth": term,
    }


def _summ(arr, prefix=""):
    a = np.asarray(arr, float)
    return {
        f"{prefix}mean": float(a.mean()),
        f"{prefix}median": float(np.median(a)),
        f"{prefix}q05": float(np.quantile(a, 0.05)),
        f"{prefix}q95": float(np.quantile(a, 0.95)),
    }


# ======================================================================================
# intraday machinery (O1a)
# ======================================================================================
def build_session_logpath(intraday_df, col, capital, leverage,
                          sess_col="sess_id", last_col="is_last_of_sess"):
    """Padded (n_sess, max_bars) matrix of WITHIN-SESSION log increments.

    intraday_df must carry, in time order, a per-session cumulative-from-session-open
    mark-to-market column `col` whose value on the session's last bar equals that
    session's daily P&L. Position size is set at the session open and unchanged during
    the session, so

        E(t) = E_open * (1 + L * mtm_t / C)   ->  within-session log path = log1p(L*mtm/C)

    Padding is with ZERO increments after the session's last bar, which leaves running
    max / running min / drawdown untouched.

    Returns (loginc_matrix, session_net_log, info).
    """
    df = intraday_df
    codes, uniq = pd.factorize(df[sess_col], sort=False)
    n_sess = len(uniq)
    pos = np.zeros(len(df), dtype=np.int64)
    # position-within-session (data is in time order)
    counts = np.bincount(codes, minlength=n_sess)
    order = np.argsort(codes, kind="stable")
    starts = np.concatenate([[0], np.cumsum(counts)[:-1]])
    pos[order] = np.arange(len(df)) - np.repeat(starts, counts)
    max_bars = int(counts.max())

    mtm = df[col].to_numpy(float)
    r = leverage * mtm / capital
    bad = r <= -1.0
    n_bad = int(bad.sum())
    if n_bad:
        r = np.where(bad, -1.0 + _EPS, r)
    ell = np.log1p(r)                       # cumulative-from-open log level

    M = np.zeros((n_sess, max_bars), dtype=float)
    M[codes, pos] = ell                     # levels, padded with 0 tail
    # convert levels -> increments within each session, then zero the padded tail
    D = np.diff(M, axis=1, prepend=0.0)
    tail = np.arange(max_bars)[None, :] >= counts[:, None]
    D[tail] = 0.0

    if last_col in df.columns:
        last_rows = df[last_col].to_numpy(bool)
        sess_net_log = np.zeros(n_sess)
        sess_net_log[codes[last_rows]] = ell[last_rows]
    else:
        sess_net_log = M[np.arange(n_sess), counts - 1]

    info = {"n_sessions": n_sess, "max_bars": max_bars,
            "total_bars": int(len(df)), "padded_bars": int(n_sess * max_bars),
            "n_bars_equity_nonpositive": n_bad,
            "bars_per_session_min": int(counts.min()),
            "bars_per_session_max": int(counts.max())}
    return D, sess_net_log, info


def _intraday_path_stats(loginc_sessions, idx, ruin_log_thr, path_len, absorbing=True,
                         cdar_alpha=DEFAULT_CDAR_ALPHA, chunk=16):
    """Evaluate bootstrap paths on the bar-by-bar intraday grid, chunked over paths."""
    n_boot = idx.shape[0]
    max_bars = loginc_sessions.shape[1]
    T = path_len * max_bars
    k_bar = max(1, int((1.0 - cdar_alpha) * T))
    k_day = max(1, int((1.0 - cdar_alpha) * path_len))

    ruined = np.empty(n_boot, dtype=bool)
    g_ann = np.empty(n_boot)
    g_ann_free = np.empty(n_boot)
    maxdd_log = np.empty(n_boot)
    cdar_log_bar = np.empty(n_boot)
    cdar_log_daymax = np.empty(n_boot)
    years = path_len / ANN

    for lo in range(0, n_boot, chunk):
        hi = min(lo + chunk, n_boot)
        sub = loginc_sessions[idx[lo:hi]]                 # (c, path_len, max_bars)
        c = sub.shape[0]
        flat = sub.reshape(c, T)
        cum = np.cumsum(flat, axis=1)
        peak = np.maximum.accumulate(cum, axis=1)
        np.maximum(peak, 0.0, out=peak)
        dd = peak - cum
        rr = dd >= ruin_log_thr
        anyr = rr.any(axis=1)
        first = np.where(anyr, rr.argmax(axis=1), T - 1)
        rows = np.arange(c)
        ruined[lo:hi] = anyr
        g_ann[lo:hi] = cum[rows, first] / years if absorbing else cum[:, -1] / years
        g_ann_free[lo:hi] = cum[:, -1] / years
        maxdd_log[lo:hi] = dd.max(axis=1)
        w = -np.partition(-dd, k_bar - 1, axis=1)[:, :k_bar]
        cdar_log_bar[lo:hi] = w.mean(axis=1)
        # frequency-matched: one observation per session = that session's worst drawdown
        daymax = dd.reshape(c, path_len, max_bars).max(axis=2)
        wd = -np.partition(-daymax, k_day - 1, axis=1)[:, :k_day]
        cdar_log_daymax[lo:hi] = wd.mean(axis=1)
        del sub, flat, cum, peak, dd, rr, daymax

    return {
        "ruined": ruined,
        "g_ann": g_ann,
        "g_ann_nonabsorbing": g_ann_free,
        "maxdd_log": maxdd_log,
        "maxdd_frac": 1.0 - np.exp(-maxdd_log),
        "cdar_log": cdar_log_bar,
        "cdar_frac": 1.0 - np.exp(-cdar_log_bar),
        "cdar_log_daymax": cdar_log_daymax,
        "cdar_frac_daymax": 1.0 - np.exp(-cdar_log_daymax),
    }


def historical_intraday_vs_daily(intraday_df, col, daily, capital, leverage,
                                 ruin_dd_frac=DEFAULT_RUIN_DD_FRAC,
                                 cdar_alpha=DEFAULT_CDAR_ALPHA,
                                 sess_col="sess_id", last_col="is_last_of_sess"):
    """Single-path (no bootstrap) intraday-vs-daily-close tail comparison. DIRECT evidence."""
    D, sess_net_log, info = build_session_logpath(intraday_df, col, capital, leverage,
                                                  sess_col, last_col)
    n_sess, max_bars = D.shape
    flat = D.reshape(1, n_sess * max_bars)
    ruin_log = -math.log(1.0 - ruin_dd_frac)
    ib = _path_stats(flat, ruin_log, n_sess, absorbing=True, cdar_alpha=cdar_alpha)
    # frequency-matched intraday CDaR on the single path
    cum = np.cumsum(flat[0])
    peak = np.maximum.accumulate(cum)
    peak = np.maximum(peak, 0.0)
    dd = (peak - cum).reshape(n_sess, max_bars).max(axis=1)
    k = max(1, int((1.0 - cdar_alpha) * n_sess))
    cdar_daymax_log = float(np.sort(dd)[::-1][:k].mean())

    dlog, _ = log_increments_fixed_fraction(np.asarray(daily, float), capital, leverage)
    db = _path_stats(dlog.reshape(1, -1), ruin_log, len(daily), absorbing=True,
                     cdar_alpha=cdar_alpha)
    return {
        "n_sessions": n_sess,
        "daily_close": {
            "max_dd_frac": float(db["maxdd_frac"][0]),
            "cdar_frac": float(db["cdar_frac"][0]),
            "ruin_hit": bool(db["ruined"][0]),
        },
        "intraday": {
            "max_dd_frac": float(ib["maxdd_frac"][0]),
            "cdar_frac_bar_level": float(ib["cdar_frac"][0]),
            "cdar_frac_daymax_matched": float(1.0 - math.exp(-cdar_daymax_log)),
            "ruin_hit": bool(ib["ruined"][0]),
        },
        "gap": {
            "max_dd_frac_diff": float(ib["maxdd_frac"][0] - db["maxdd_frac"][0]),
            "max_dd_ratio": float(ib["maxdd_frac"][0] / db["maxdd_frac"][0])
            if db["maxdd_frac"][0] > 0 else float("nan"),
            "cdar_matched_ratio": float((1.0 - math.exp(-cdar_daymax_log)) / db["cdar_frac"][0])
            if db["cdar_frac"][0] > 0 else float("nan"),
        },
        "construction": info,
    }


# ======================================================================================
# THE PUBLIC API
# ======================================================================================
def primary_objective(pnl_path,
                      capital=DEFAULT_CAPITAL,
                      leverage=DEFAULT_LEVERAGE,
                      *,
                      intraday_path=None,
                      intraday_col=None,
                      intraday_sess_col="sess_id",
                      intraday_last_col="is_last_of_sess",
                      ruin_dd_frac=DEFAULT_RUIN_DD_FRAC,
                      lam=DEFAULT_LAMBDA,
                      horizon_sessions=HORIZON_SESSIONS,
                      n_boot=N_BOOT,
                      seed=SEED,
                      methods=DEFAULT_METHODS,
                      diagnostic_methods=DIAGNOSTIC_METHODS,
                      leverage_mode="fixed_fraction",
                      absorbing=True,
                      cdar_alpha=DEFAULT_CDAR_ALPHA,
                      baseline_daily=None,
                      date_col=None, pnl_col=None,
                      dev_window="truncate",
                      cp3_dollar_cap=25_000.0,
                      margin_floor_per_unit=PRODUCT_A_MAX_CONTRACTS * MNQ_DAY_MARGIN
                      * PRE_RELEASE_MARGIN_MULT,
                      min_unit=None,
                      intraday_chunk=16,
                      label=None):
    """Evaluate the primary objective on a daily $ P&L path.

    Returns a dict (JSON-serializable) with, at minimum:
      primary.objective_J            THE scalar
      primary.ce_log_growth_ann      expected (certainty-equivalent) log growth, annualized
      primary.p_ruin                 headline ruin probability (worst of the three methods)
      ruin.daily_close / ruin.intraday / ruin.gap
      tail.daily_close / tail.intraday / tail.gap
      legacy_diagnostics_NOT_GATES   Sharpe, CDaR_0.95, top-10-day share/retention

    See runs/W17_C4_COMPLIANCE/O1_OBJECTIVE.md for every modelling choice.
    """
    daily, load_flags = load_daily_pnl(pnl_path, date_col=date_col, pnl_col=pnl_col,
                                       dev_window=dev_window)
    x = daily.to_numpy(float)
    n = len(x)
    if horizon_sessions is None:
        horizon_sessions = n
    ruin_log = -math.log(1.0 - ruin_dd_frac)
    years = horizon_sessions / ANN


    out = {
        "label": label,
        "spec": {
            "PREREGISTERED_IN": "runs/W17_C4_COMPLIANCE/O1_OBJECTIVE.md section 1",
            "capital_dollars": float(capital),
            "target_leverage": float(leverage),
            "leverage_mode": leverage_mode,
            "leverage_applied_as": ("constant multiplier in RETURN space; contract count reset "
                                    "each session open in proportion to equity"
                                    if leverage_mode == "fixed_fraction"
                                    else "constant contract count; equity drifts, no compounding"),
            "ruin_definition_R1": (f"drawdown from running high-water mark reaches "
                                   f"{ruin_dd_frac:.0%} (== the capital map's funded DD budget), "
                                   f"ABSORBING"),
            "ruin_dd_frac": float(ruin_dd_frac),
            "absorbing": bool(absorbing),
            "horizon_sessions": int(horizon_sessions),
            "horizon_years": float(years),
            "lambda_ruin_per_yr": float(lam),
            "bootstrap_methods_headline": list(methods),
            "bootstrap_methods_diagnostic": list(diagnostic_methods),
            "n_boot": int(n_boot),
            "seed": int(seed),
            "cdar_alpha": float(cdar_alpha),
            "ann": ANN,
            "min_unit": min_unit,
            "no_look_ahead": ("all statistics are functions of the realized in-sample series; "
                              "block resampling draws only from realized observations"),
        },
        "input": {
            "n_sessions": int(n),
            "date_min": str(daily.index.min()) if load_flags["dated"] else None,
            "date_max": str(daily.index.max()) if load_flags["dated"] else None,
            "net_dollars": float(x.sum()),
            "load_flags": load_flags,
        },
        "integrity": {"warnings": list(load_flags["warnings"])},
    }

    # ---------------- daily-close leg ----------------
    bad_day = np.zeros(n, dtype=bool)
    if leverage_mode == "fixed_fraction":
        loginc, n_bad = log_increments_fixed_fraction(x, capital, leverage)
        bad_day = (leverage * x / capital) <= -1.0
        out["integrity"]["n_days_equity_nonpositive"] = n_bad
        if n_bad:
            out["integrity"]["warnings"].append(
                f"{n_bad} day(s) had 1 + L*x/C <= 0 and were clipped -- growth figures at "
                f"leverage {leverage} are UNRELIABLE")
    elif leverage_mode == "fixed_contracts":
        loginc = None
        out["integrity"]["n_days_equity_nonpositive"] = 0
    else:
        raise ValueError("leverage_mode must be 'fixed_fraction' or 'fixed_contracts'")
    if min_unit and leverage_mode != "fixed_fraction":
        raise NotImplementedError("min_unit rounding is implemented for fixed_fraction only")

    idx_bank = {}
    ruin_daily, growth_by_method, tail_daily = {}, {}, {}
    r3_by_method, bankrupt_by_method, margin_by_method = {}, {}, {}
    all_methods = list(methods) + list(diagnostic_methods)
    for m in all_methods:
        idx = make_indices(m, n, horizon_sessions, n_boot=n_boot, seed=seed)
        idx_bank[m] = idx
        if leverage_mode == "fixed_fraction":
            if min_unit:
                st = _fixed_fraction_rounded_stats(
                    x[idx], capital, leverage, ruin_dd_frac, horizon_sessions,
                    absorbing, cdar_alpha, min_unit)
            else:
                st = _path_stats(loginc[idx], ruin_log, horizon_sessions,
                                 absorbing=absorbing, cdar_alpha=cdar_alpha)
            bankrupt_by_method[m] = float(bad_day[idx].any(axis=1).mean())
        else:
            st, bank = _fixed_contract_stats(x[idx], capital, leverage, ruin_dd_frac,
                                             horizon_sessions, absorbing, cdar_alpha,
                                             margin_floor_per_unit)
            bankrupt_by_method[m] = bank["p_equity_nonpositive"]
            margin_by_method[m] = bank["p_margin_floor"]
        ruin_daily[m] = float(st["ruined"].mean())
        growth_by_method[m] = {
            **_summ(st["g_ann"], "g_ann_"),
            "g_ann_nonabsorbing_mean": float(st["g_ann_nonabsorbing"].mean()),
        }
        tail_daily[m] = {
            "cdar_frac": float(st["cdar_frac"].mean()),
            "cdar_dollar_at_capital": float(st["cdar_frac"].mean() * capital),
            "maxdd_frac_mean": float(st["maxdd_frac"].mean()),
            "maxdd_frac_p95": float(np.quantile(st["maxdd_frac"], 0.95)),
        }
        # R3: C-P3 comparability -- max $ drawdown of the UNLEVERED cumsum path
        eq = np.cumsum(x[idx], axis=1)
        mdd = (np.maximum.accumulate(eq, axis=1) - eq).max(axis=1)
        r3_by_method[m] = {
            "p_maxdd_gt_cap": float((mdd * leverage > cp3_dollar_cap).mean()),
            "p95_maxdd_dollar": float(np.percentile(mdd, 95)),
            "capital_needed_at_thr": float(np.percentile(mdd, 95) / ruin_dd_frac),
        }

    head = [ruin_daily[m] for m in methods]
    p_ruin_daily = float(max(head))
    p_ruin_method = methods[int(np.argmax(head))]
    ce_g = float(np.mean([growth_by_method[m]["g_ann_mean"] for m in methods]))
    J = ce_g - lam * p_ruin_daily

    out["ruin"] = {
        "definition": out["spec"]["ruin_definition_R1"],
        "daily_close": {
            **{m: ruin_daily[m] for m in all_methods},
            "headline_worst_of_three": p_ruin_daily,
            "headline_method": p_ruin_method,
            "spread_max_minus_min_over_three": float(max(head) - min(head)),
            "_note": "iid is a DIAGNOSTIC method, not one of the three headline methods",
        },
        "R2_margin_floor": {
            "floor_dollars_per_unit_4x_stress": float(margin_floor_per_unit),
            "binding": (leverage_mode == "fixed_contracts"),
            "p_hit": (margin_by_method if leverage_mode == "fixed_contracts" else None),
            "_note": ("in fixed_fraction mode margin/equity is CONSTANT, so R2 is a static "
                      "feasibility test (L <= C / floor), not a crossing event"),
            "static_feasible_max_leverage": float(capital / margin_floor_per_unit),
        },
        "R3_cp3_comparability": {
            "dollar_cap": float(cp3_dollar_cap),
            "per_method": r3_by_method,
            "_note": "P(max $ drawdown over the horizon > cap) at this leverage, on the "
                     "un-compounded cumsum path -- directly comparable to the published "
                     "C-P3 disclosure",
        },
        "p_equity_nonpositive": {
            "per_method": bankrupt_by_method,
            "_note": ("fixed_fraction: fraction of resampled paths containing a day where "
                      "1 + L*x/C <= 0 (equity would cross zero and the log is clipped). "
                      "fixed_contracts: fraction of paths whose equity actually reached <= 0. "
                      "This is TRUE bankruptcy and must not be conflated with R1 ruin."),
        },
    }
    out["growth"] = {
        "per_method": growth_by_method,
        "ce_log_growth_ann_pooled_over_three": ce_g,
        "historical_single_path": _historical_growth(x, capital, leverage, leverage_mode,
                                                     ruin_log, absorbing, cdar_alpha),
    }
    out["tail"] = {"daily_close": tail_daily}
    out["primary"] = {
        "objective_J": float(J),
        "ce_log_growth_ann": ce_g,
        "p_ruin": p_ruin_daily,
        "p_ruin_basis": "daily_close",
        "p_ruin_method_used": p_ruin_method,
        "lambda_ruin_per_yr": float(lam),
        "formula": "J = CE_g - lambda * P_ruin",
    }
    out["primary"]["objective_J_by_lambda"] = {
        str(l_): float(ce_g - l_ * p_ruin_daily) for l_ in LAMBDA_GRID}

    # ---------------- O1a: intraday leg ----------------
    if intraday_path is not None:
        if leverage_mode != "fixed_fraction":
            raise NotImplementedError("intraday leg is implemented for fixed_fraction only")
        idf = (intraday_path if isinstance(intraday_path, pd.DataFrame)
               else _read_tabular(intraday_path))
        if intraday_col is None:
            raise ValueError("intraday_col= must name the cumulative-from-session-open "
                             "mark-to-market column")
        D, sess_net_log, info = build_session_logpath(
            idf, intraday_col, capital, leverage, intraday_sess_col, intraday_last_col)
        recon = float(np.abs(sess_net_log - loginc).max()) if len(sess_net_log) == n else None
        out["integrity"]["intraday_construction"] = info
        out["integrity"]["intraday_vs_daily_sessionend_maxabs_logdiff"] = recon
        if recon is not None and recon > 1e-9:
            out["integrity"]["warnings"].append(
                f"intraday session-end log returns disagree with the daily series by "
                f"{recon:.3e} -- the two legs are NOT the same object")

        ruin_intra, tail_intra, growth_intra = {}, {}, {}
        for m in all_methods:
            st = _intraday_path_stats(D, idx_bank[m], ruin_log, horizon_sessions,
                                      absorbing=absorbing, cdar_alpha=cdar_alpha,
                                      chunk=intraday_chunk)
            ruin_intra[m] = float(st["ruined"].mean())
            tail_intra[m] = {
                "cdar_frac_bar_level": float(st["cdar_frac"].mean()),
                "cdar_frac_daymax_matched": float(st["cdar_frac_daymax"].mean()),
                "cdar_dollar_daymax_at_capital": float(st["cdar_frac_daymax"].mean() * capital),
                "maxdd_frac_mean": float(st["maxdd_frac"].mean()),
                "maxdd_frac_p95": float(np.quantile(st["maxdd_frac"], 0.95)),
            }
            growth_intra[m] = _summ(st["g_ann"], "g_ann_")

        head_i = [ruin_intra[m] for m in methods]
        p_ruin_intra = float(max(head_i))
        out["ruin"]["intraday"] = {
            **{m: ruin_intra[m] for m in all_methods},
            "headline_worst_of_three": p_ruin_intra,
            "spread_max_minus_min_over_three": float(max(head_i) - min(head_i)),
        }
        out["ruin"]["gap"] = {
            "per_method_abs": {m: float(ruin_intra[m] - ruin_daily[m]) for m in all_methods},
            "per_method_rel": {m: (float(ruin_intra[m] / ruin_daily[m] - 1.0)
                                   if ruin_daily[m] > 0 else None) for m in all_methods},
            "headline_abs": float(p_ruin_intra - p_ruin_daily),
            "headline_rel": (float(p_ruin_intra / p_ruin_daily - 1.0)
                             if p_ruin_daily > 0 else None),
            "MATERIALITY_BAR": "abs >= 0.02 OR rel >= 0.20 (pre-registered)",
            "material": bool((p_ruin_intra - p_ruin_daily) >= 0.02 or
                             (p_ruin_daily > 0 and p_ruin_intra / p_ruin_daily - 1.0 >= 0.20)),
        }
        out["tail"]["intraday"] = tail_intra
        out["tail"]["gap"] = {
            "cdar_matched_ratio_per_method": {
                m: (float(tail_intra[m]["cdar_frac_daymax_matched"] /
                          tail_daily[m]["cdar_frac"]) if tail_daily[m]["cdar_frac"] > 0
                    else None) for m in all_methods},
            "cdar_barlevel_ratio_per_method": {
                m: (float(tail_intra[m]["cdar_frac_bar_level"] / tail_daily[m]["cdar_frac"])
                    if tail_daily[m]["cdar_frac"] > 0 else None) for m in all_methods},
            "maxdd_ratio_per_method": {
                m: float(tail_intra[m]["maxdd_frac_mean"] / tail_daily[m]["maxdd_frac_mean"])
                for m in all_methods},
            "MATERIALITY_BAR": "matched CDaR ratio >= 1.20 (pre-registered)",
        }
        ratios = [out["tail"]["gap"]["cdar_matched_ratio_per_method"][m] for m in methods]
        ratios = [r for r in ratios if r is not None]
        out["tail"]["gap"]["cdar_matched_ratio_worst"] = float(max(ratios)) if ratios else None
        out["tail"]["gap"]["material"] = bool(ratios and max(ratios) >= 1.20)
        out["growth"]["per_method_intraday_absorbing"] = growth_intra
        ce_g_i = float(np.mean([growth_intra[m]["g_ann_mean"] for m in methods]))
        out["primary"]["objective_J_intraday_barrier"] = float(ce_g_i - lam * p_ruin_intra)
        out["primary"]["ce_log_growth_ann_intraday_barrier"] = ce_g_i
        out["primary"]["p_ruin_intraday_barrier"] = p_ruin_intra
        out["primary"]["_intraday_note"] = (
            "objective_J_intraday_barrier applies the SAME barrier but checks it at every "
            "3-minute bar instead of only at the close. It is the leverage-relevant number "
            "if margin pressure is what binds.")

    # ---------------- legacy diagnostics ----------------
    base = None
    if baseline_daily is not None:
        b, _ = load_daily_pnl(baseline_daily, dev_window=dev_window)
        base = b.to_numpy(float)
    out["legacy_diagnostics_NOT_GATES"] = legacy_diagnostics(x, base, cdar_alpha)
    out["legacy_diagnostics_NOT_GATES"]["capital_map_rule_capital_needed_at_thr"] = {
        m: r3_by_method[m]["capital_needed_at_thr"] for m in methods}
    return out


def _historical_growth(x, capital, leverage, mode, ruin_log, absorbing, cdar_alpha):
    """Realized single-path growth/tail read (no resampling). DIRECT evidence."""
    n = len(x)
    if mode == "fixed_fraction":
        loginc, _ = log_increments_fixed_fraction(x, capital, leverage)
        st = _path_stats(loginc.reshape(1, -1), ruin_log, n, absorbing=absorbing,
                         cdar_alpha=cdar_alpha)
    else:
        st, _ = _fixed_contract_stats(x.reshape(1, -1), capital, leverage, 1 - math.exp(-ruin_log),
                                      n, absorbing, cdar_alpha, np.inf)
    return {
        "g_ann_log": float(st["g_ann"][0]),
        "g_ann_pct_equivalent": float(math.expm1(st["g_ann"][0]) * 100.0),
        "max_dd_frac": float(st["maxdd_frac"][0]),
        "cdar_frac": float(st["cdar_frac"][0]),
        "ruin_hit": bool(st["ruined"][0]),
        "_note": "ONE realized path. Not a distribution. Not evidence about the future.",
    }


def _fixed_fraction_rounded_stats(paths_dollar, capital, leverage, ruin_dd_frac, path_len,
                                  absorbing, cdar_alpha, min_unit):
    """Fixed-fraction sizing with CONTRACT GRANULARITY: units are floored to a multiple of
    `min_unit`, so the equity recursion is path-dependent and must be stepped. Vectorized
    over paths, loops over time. Disclosed approximation of real lot granularity."""
    n_paths, T = paths_dollar.shape
    eq = np.full(n_paths, float(capital))
    peak = eq.copy()
    dd = np.empty((n_paths, T))
    eqs = np.empty((n_paths, T))
    for t in range(T):
        u = leverage * eq / capital
        u = np.floor(u / min_unit) * min_unit
        eq = eq + u * paths_dollar[:, t]
        np.maximum(peak, eq, out=peak)
        eqs[:, t] = eq
        dd[:, t] = 1.0 - eq / peak
    ruined = dd >= ruin_dd_frac
    anyr = ruined.any(axis=1)
    first = np.where(anyr, ruined.argmax(axis=1), T - 1)
    rows = np.arange(n_paths)
    term = eqs[rows, first] if absorbing else eqs[:, -1]
    term = np.maximum(term, _EPS * capital)
    years = path_len / ANN
    k = max(1, int((1.0 - cdar_alpha) * T))
    worst = -np.partition(-dd, k - 1, axis=1)[:, :k]
    mdd = dd.max(axis=1)
    return {
        "ruined": anyr,
        "g_ann": np.log(term / capital) / years,
        "g_ann_nonabsorbing": np.log(np.maximum(eqs[:, -1], _EPS * capital) / capital) / years,
        "maxdd_frac": mdd,
        "maxdd_log": -np.log1p(-np.clip(mdd, None, 1 - _EPS)),
        "cdar_frac": worst.mean(axis=1),
        "cdar_log": -np.log1p(-np.clip(worst.mean(axis=1), None, 1 - _EPS)),
        "terminal_log_wealth": np.log(term / capital),
    }


def _fixed_contract_stats(paths_dollar, capital, leverage, ruin_dd_frac, path_len,
                          absorbing, cdar_alpha, margin_floor_per_unit):
    """Constant contract count: E = C + L*cumsum(x). Drawdown measured on E."""
    eq = capital + leverage * np.cumsum(paths_dollar, axis=1)
    peak = np.maximum.accumulate(eq, axis=1)
    np.maximum(peak, capital, out=peak)
    dd_frac = 1.0 - eq / peak
    ruined = dd_frac >= ruin_dd_frac
    anyr = ruined.any(axis=1)
    T = eq.shape[1]
    first = np.where(anyr, ruined.argmax(axis=1), T - 1)
    rows = np.arange(eq.shape[0])
    term = eq[rows, first] if absorbing else eq[:, -1]
    term = np.maximum(term, _EPS * capital)
    years = path_len / ANN
    k = max(1, int((1.0 - cdar_alpha) * T))
    worst = -np.partition(-dd_frac, k - 1, axis=1)[:, :k]
    floor = margin_floor_per_unit * leverage
    st = {
        "ruined": anyr,
        "g_ann": np.log(term / capital) / years,
        "g_ann_nonabsorbing": np.log(np.maximum(eq[:, -1], _EPS * capital) / capital) / years,
        "maxdd_frac": dd_frac.max(axis=1),
        "maxdd_log": -np.log1p(-np.clip(dd_frac.max(axis=1), None, 1 - _EPS)),
        "cdar_frac": worst.mean(axis=1),
        "cdar_log": -np.log1p(-np.clip(worst.mean(axis=1), None, 1 - _EPS)),
        "terminal_log_wealth": np.log(term / capital),
    }
    extra = {
        "p_equity_nonpositive": float((eq.min(axis=1) <= 0).mean()),
        "p_margin_floor": float((eq.min(axis=1) < floor).mean()) if np.isfinite(floor) else None,
    }
    return st, extra


# ======================================================================================
# convenience: leverage curve
# ======================================================================================
def leverage_curve(pnl_path, capital=DEFAULT_CAPITAL, grid=LEVERAGE_GRID, **kw):
    """J, CE_g and P_ruin over a leverage grid. Reported for SHAPE. Not a recommendation."""
    rows = []
    for L in grid:
        r = primary_objective(pnl_path, capital=capital, leverage=L, **kw)
        row = {"leverage": L,
               "J": r["primary"]["objective_J"],
               "ce_log_growth_ann": r["primary"]["ce_log_growth_ann"],
               "p_ruin_daily_close": r["primary"]["p_ruin"],
               "p_ruin_method": r["primary"]["p_ruin_method_used"],
               "p_ruin_spread": r["ruin"]["daily_close"]["spread_max_minus_min_over_three"]}
        if "p_ruin_intraday_barrier" in r["primary"]:
            row["p_ruin_intraday"] = r["primary"]["p_ruin_intraday_barrier"]
            row["J_intraday_barrier"] = r["primary"]["objective_J_intraday_barrier"]
        rows.append(row)
    return pd.DataFrame(rows)


# ======================================================================================
# verification helpers -- reproduce this repo's own published bootstrap figures
# ======================================================================================
def reproduce_capital_map(x, stress_mults=(1.0,), thrs=(0.10, 0.15, 0.20, 0.25, 0.30),
                          nb=2000, seed=SEED):
    """Byte-for-byte replication of
    runs/PRODUCTB_ONECONTRACT_FINAL/build_parity_and_metrics.py::capital_map, including its
    SHARED rng draw order (L5, then L20, then stat60 from one default_rng(seed)).
    Used to prove this module's generators are the repo's generators."""
    x = np.asarray(x, float)
    n_ = len(x)
    rng = np.random.default_rng(seed)

    def idx_moving_block(L):
        nb_ = int(np.ceil(n_ / L))
        starts = rng.integers(0, n_, size=(nb, nb_))
        idx = (starts[:, :, None] + np.arange(L)[None, None, :]) % n_
        return idx.reshape(nb, -1)[:, :n_]

    def idx_stationary(mean_L):
        p = 1.0 / mean_L
        idx = np.empty((nb, n_), dtype=np.int64)
        cur_i = rng.integers(0, n_, size=nb)
        for t in range(n_):
            jump = rng.random(nb) < p
            cur_i = np.where(jump, rng.integers(0, n_, size=nb), (cur_i + 1) % n_)
            idx[:, t] = cur_i
        return idx

    methods = {"L5": idx_moving_block(5), "L20": idx_moving_block(20),
               "stat60": idx_stationary(60)}
    rows = []
    for m in stress_mults:
        xs = x * m
        for mname, idx in methods.items():
            eq = np.cumsum(xs[idx], axis=1)
            mdd = (np.maximum.accumulate(eq, axis=1) - eq).max(axis=1)
            p95 = float(np.percentile(mdd, 95))
            for thr in thrs:
                rows.append({"stress_mult": m, "method": mname, "thr": thr,
                             "p95_maxdd_dollar": p95, "capital_needed": p95 / thr})
    return pd.DataFrame(rows)


def reproduce_cp3(x, cap=25_000.0, path_len=504, n_boot=5000, seed=SEED):
    """Reproduce the published C-P3 disclosure probabilities using this module's generators:
    stationary_pr20 (published 0.142) and moving5 (published 0.430)."""
    x = np.asarray(x, float)
    n = len(x)
    out = {}
    for name, meth in (("A_stationary20", "stationary_pr20"), ("B_moving5", "moving5")):
        idx = make_indices(meth, n, path_len, n_boot=n_boot, seed=seed)
        eq = np.cumsum(x[idx], axis=1)
        mdd = (np.maximum.accumulate(eq, axis=1) - eq).max(axis=1)
        out[name] = float((mdd > cap).mean())
    return out
