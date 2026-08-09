"""primary_objective_v2.py — REPAIRED primary objective (O1 + O1a), version 2.

v1 (`src/analytics/primary_objective.py`) is left on the record UNTOUCHED, per repo rule C7.
This module is a NEW file. It imports v1's bootstrap generators and path machinery **by
reference**, so the machinery-reproduction guarantees of v1's self-test (cases 3 and 4 —
byte-exact reproduction of `capital_map_nq.csv` and of the published C-P3 disclosure) carry
over to v2 without a copy that could silently drift. Everything v2 *changes* is redefined
here and listed below.

Full argument: `runs/W17_C4_COMPLIANCE/O1_REPAIR_PREREGISTRATION.md` (written before any
object was scored with this module).
Defect list being repaired: `runs/W17_C4_COMPLIANCE/red_team/RED_TEAM_o1_objective.md`.

======================================================================================
WHAT CHANGED VERSUS v1, AND WHY
======================================================================================

**D1 — aggregation over bootstrap methods (headline-flipping).**
v1: `P_ruin = max` over {moving5, moving20, stationary60} while `CE_g = arithmetic mean`
over the same three. That combination is not a functional of any probability distribution:
the growth term is read off one object and the penalty off another, so `J` is the objective
of no model of the world.

v2: ONE rule, applied to BOTH terms — the **equal-weight mixture** over the three
pre-registered methods. Because `CE_g` and `P_ruin` are both *expectations* under the
resampled path distribution, and `n_boot` is equal across methods, this is exactly:

        pool the 3 x n_boot resampled paths into one sample and compute J on the pool.

i.e. `J = J(Fbar)` where `Fbar = (F_m5 + F_m20 + F_s60)/3` is a single, explicitly named
probability model ("draw a resampling scheme uniformly, then draw a path from it"). No
max-based rule admits any such statement. See the pre-registration for the full argument
and for why the three methods are three *tunings of one estimator*, not three states of the
world.

Conservatism is NOT discarded — it is made explicit and coherent:
  * `aggregation.J_by_method`      — J_m for each method, each one internally consistent
  * `aggregation.J_worst`          — `min_m J_m`, the Gamma-minimax / worst-model reading
                                     (NEVER `min CE - lambda*max P`, which is incoherent)
  * `aggregation.model_determined_sign` — True when `J` and `J_worst` disagree in sign.
    When that flag is True the object's score is set by the choice of resampling method and
    must not be reported as a single number.

**D4 — lambda calibration convention mismatch (headline-flipping), plus a double-count the
red team did not catch.**
v1: `lambda = 1.0`, derived in O1_OBJECTIVE.md section 1.5 from the *non-compounded* house
`logG` convention (`g_ref = ln(1 + Net/C)/years = 0.2257/yr`) but multiplying `CE_g`, which
is the *compounded* fixed-fraction log growth rate. Units mismatch => lambda biased low.

v2: lambda is DERIVED, not a magic constant, from

        lambda = (H_f - H) / H * g_ref(convention matching CE_g)

with `H_f = 10 yr` (franchise horizon, as pre-registered) and `H` the evaluation horizon in
years. Two corrections are embedded:
  (a) `g_ref` is taken in the SAME growth convention as the `CE_g` it multiplies —
      compounded (0.341931/yr) in `fixed_fraction` mode, non-compounded (0.225668/yr) in
      `fixed_contracts` mode. Both are arithmetic on already-published committed figures.
  (b) the forfeited horizon is `H_f - H`, not `H_f - H/2`. The barrier is ABSORBING, so the
      growth lost between the ruin time `tau` and the end of the window is already inside
      `CE_g`; charging `(H_f - tau)` in lambda double-counts the interval `[tau, H]`. The
      corrected form does not depend on `tau` at all, which also removes the untestable
      "ruin happens near the middle of the window" assumption.
At H = 504 sessions this gives `lambda = 1.3678 /yr` in `fixed_fraction` mode (v1: 1.0) and
`0.9027 /yr` in `fixed_contracts` mode. lambda now moves correctly if the horizon changes,
and is 0 when `H >= H_f` (nothing left to forfeit).

**D9 — the shipped `min_unit` (contract-granularity) path.**
Three distinct defects in v1's `_fixed_fraction_rounded_stats`:
  (a) `np.floor(u / min_unit) * min_unit` is wrong in floating point:
      `floor(0.3/0.1) = 2`, so a 0.3-unit target rounds to 0.2 — a whole granule lost.
      (`0.29/0.01 -> 0.28`; `2.4/0.4 -> 2.0`.) v2 floors with a relative tolerance.
  (b) when equity goes negative the target `u = L*eq/C` goes negative and v1 *reverses the
      position*. v2 clamps the target at 0 before flooring.
  (c) the real trap: once `u` floors to 0 the equity stops moving, so `u` stays 0 forever —
      the path is frozen. On a synthetic fixture at the module's own advertised settings
      (C=$100k, L=1, min_unit=1) 90.8% of paths freeze; `P_ruin` collapses from 0.350 to
      0.0025, i.e. **granularity appears to reduce ruin risk**. v1 shipped that number and
      its own test asserted only `isfinite(J)`.
      v2 keeps the frozen-account model (an operator who cannot afford one lot really does
      stop) but DETECTS it, counts it, warns, and — above a pre-registered bar of 5% of
      paths — sets `primary.objective_J` to NaN with `objective_J_is_degenerate = True`.
      All components remain in the returned dict; nothing is hidden, but the artifact can no
      longer be quoted as a score.
      `p_equity_nonpositive` in `min_unit` mode is now computed from the actual stepped
      granular equity; v1 computed it from the *continuous* model's clip test, i.e. for a
      different model than the one it reported.

**D10 (partial, safety) — the LOCKED-FORWARD guard was vacuous on undated input.**
v1's `_index_is_datelike` did `pd.to_datetime(idx[:5])`, which SUCCEEDS on an integer
RangeIndex (ints read as nanoseconds since epoch), so a bare array was flagged `dated=True`
with no warning and the locked-forward guard never fired. v2 refuses numeric indices as
dates, and raises if an explicit date column parses to pre-1990 timestamps (the signature of
an integer `YYYYMMDD` or epoch-nanosecond misparse). Fixed because leaving a known-vacuous
safety guard in a NEW module would be indefensible.

**D3 (partial) — Monte-Carlo standard errors.**
v1 reported a 4-decimal scalar whose sign is the whole point with no band at all. v2 returns
`primary.monte_carlo_se` = `sd(g - lambda*1{ruin})/sqrt(N_pooled)` over the pooled sample,
and `n_pooled_paths`. **This is Monte-Carlo error only.** It goes to zero as `n_boot` grows
while the estimate stays conditioned on ONE realized 1,139-session sample; it is NOT a
confidence interval for the underlying process. The key is named accordingly.

**D11 / D12 (surfaced, not silently changed).** v2 additionally returns
`cdar_frac_arith` alongside v1's log-space `cdar_frac`, dollarizes the arithmetic one
(dollarizing a log-space mean was the actual complaint), and returns both an unlevered and a
levered `capital_needed_at_thr`. v1's keys keep v1's meanings.

New diagnostics that let a reader audit the lambda derivation:
`ruin.mean_first_ruin_years_given_ruin` (the quantity section 1.5 assumed to be H/2 and never
measured).

Determinism, seeds, generators, the intraday construction, the legacy diagnostics and the
pre-registered constants of O1_OBJECTIVE.md section 1 are otherwise unchanged.

Nothing in this module establishes that future profitability is achievable. Every number is
a statistic of a fixed historical sample, or of resamples of that sample.
"""
from __future__ import annotations

import math
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:                      # src/analytics is a flat module dir
    sys.path.insert(0, _HERE)

import primary_objective as _v1                # noqa: E402  (v1 is imported, never modified)

# --------------------------------------------------------------------------------------
# constants carried over UNCHANGED from v1 / O1_OBJECTIVE.md section 1
# --------------------------------------------------------------------------------------
SEED = _v1.SEED
N_BOOT = _v1.N_BOOT
HORIZON_SESSIONS = _v1.HORIZON_SESSIONS
ANN = _v1.ANN
DEFAULT_CAPITAL = _v1.DEFAULT_CAPITAL
DEFAULT_LEVERAGE = _v1.DEFAULT_LEVERAGE
DEFAULT_RUIN_DD_FRAC = _v1.DEFAULT_RUIN_DD_FRAC
DEFAULT_CDAR_ALPHA = _v1.DEFAULT_CDAR_ALPHA
DEFAULT_METHODS = _v1.DEFAULT_METHODS
DIAGNOSTIC_METHODS = _v1.DIAGNOSTIC_METHODS
LEVERAGE_GRID = _v1.LEVERAGE_GRID
LAMBDA_GRID = _v1.LAMBDA_GRID
MNQ_DAY_MARGIN = _v1.MNQ_DAY_MARGIN
MNQ_INITIAL_MARGIN = _v1.MNQ_INITIAL_MARGIN
PRE_RELEASE_MARGIN_MULT = _v1.PRE_RELEASE_MARGIN_MULT
PRODUCT_A_MAX_CONTRACTS = _v1.PRODUCT_A_MAX_CONTRACTS
DEV_END = _v1.DEV_END
LOCKED_FORWARD_START = _v1.LOCKED_FORWARD_START
_EPS = _v1._EPS

# generators and path machinery are v1's OBJECTS, not copies -- see test D0.
make_indices = _v1.make_indices
parse_method = _v1.parse_method
_path_stats = _v1._path_stats
_intraday_path_stats = _v1._intraday_path_stats
_fixed_contract_stats = _v1._fixed_contract_stats
build_session_logpath = _v1.build_session_logpath
log_increments_fixed_fraction = _v1.log_increments_fixed_fraction
historical_intraday_vs_daily = _v1.historical_intraday_vs_daily
legacy_diagnostics = _v1.legacy_diagnostics
daily_sharpe = _v1.daily_sharpe
cdar_dollar = _v1.cdar_dollar
top10_day_share = _v1.top10_day_share
top10_day_retention = _v1.top10_day_retention
reproduce_capital_map = _v1.reproduce_capital_map
reproduce_cp3 = _v1.reproduce_cp3
dollar_dd_series = _v1.dollar_dd_series
_summ = _v1._summ
_read_tabular = _v1._read_tabular

# --------------------------------------------------------------------------------------
# D1 -- the aggregation rule, pre-registered here
# --------------------------------------------------------------------------------------
AGGREGATION_RULE = "equal_weight_mixture_over_headline_methods"
AGGREGATION_RULE_NOTE = (
    "J = J(Fbar) with Fbar the equal-weight mixture of the three pre-registered resampling "
    "schemes. With equal n_boot this is identically 'pool all 3*n_boot resampled paths and "
    "compute CE_g and P_ruin on the pool'. The SAME rule is applied to BOTH terms. "
    "min_m J_m (Gamma-minimax) is reported alongside as aggregation.J_worst; a sign "
    "disagreement between them sets aggregation.model_determined_sign and the scalar must "
    "then not be quoted alone.")

# --------------------------------------------------------------------------------------
# D4 -- lambda calibration, pre-registered here
# --------------------------------------------------------------------------------------
FRANCHISE_HORIZON_YEARS = 10.0     # H_f, verbatim from O1_OBJECTIVE.md section 1.5

# g_ref in the NON-COMPOUNDED house `logG` convention: ln(1 + Net/C)/years on the published
# executable dev headline (CURRENT_TRUTH.md: net $177,315.10 over 1,139 sessions, C=$100k).
# This is the number O1_OBJECTIVE.md section 1.5 actually used.
G_REF_NONCOMPOUNDED = math.log(1.0 + 177_315.10 / 100_000.0) / (1139.0 / 252.0)   # 0.225668

# g_ref in the COMPOUNDED fixed-fraction convention -- the convention `CE_g` is actually in.
# Arithmetic on the figure published in RED_TEAM_o1_objective.md D4: the executable twin's
# fixed-fraction equity on the same $100k base over the same 1,139 dev sessions ends at
# $469,020. ln(469020/100000)/(1139/252) = 0.341931.
# DISCLOSED SUBSTITUTION: a compounded rate is path-dependent and cannot be recovered from a
# summary net, and no committed per-day artifact exists for the executable object itself, so
# the twin (dev net $179,288.70, 1.1% above the executable's $177,315.10) is the only
# available basis -- the same substitution O1_OBJECTIVE.md section 5.6 made. Direction of the
# residual error: g_ref, hence lambda, is marginally HIGH, i.e. marginally conservative.
G_REF_COMPOUNDED = math.log(469_020.0 / 100_000.0) / (1139.0 / 252.0)             # 0.341931

LAMBDA_DERIVATION = (
    "lambda = (H_f - H)/H * g_ref, H_f = 10 yr franchise horizon, H = evaluation horizon in "
    "years, g_ref in the SAME growth convention as CE_g (compounded for fixed_fraction, "
    "non-compounded for fixed_contracts). The forfeited horizon is H_f - H (NOT H_f - H/2): "
    "the barrier is absorbing, so growth lost between the ruin time and the end of the "
    "window is already inside CE_g, and charging it again in lambda double-counts.")


def franchise_lambda(horizon_sessions=HORIZON_SESSIONS,
                     leverage_mode="fixed_fraction",
                     franchise_years=FRANCHISE_HORIZON_YEARS,
                     g_ref=None,
                     ann=ANN):
    """lambda = (H_f - H)/H * g_ref, with g_ref in the convention CE_g is measured in.

    Returns 0.0 when the evaluation horizon already covers the franchise horizon (nothing
    out-of-window is left to forfeit).
    """
    H = float(horizon_sessions) / float(ann)
    if H <= 0:
        raise ValueError("horizon must be positive")
    if g_ref is None:
        g_ref = (G_REF_COMPOUNDED if leverage_mode == "fixed_fraction"
                 else G_REF_NONCOMPOUNDED)
    return max(float(franchise_years) - H, 0.0) / H * float(g_ref)


DEFAULT_LAMBDA_FIXED_FRACTION = franchise_lambda(HORIZON_SESSIONS, "fixed_fraction")
DEFAULT_LAMBDA_FIXED_CONTRACTS = franchise_lambda(HORIZON_SESSIONS, "fixed_contracts")

# --------------------------------------------------------------------------------------
# D9 -- contract granularity, pre-registered degeneracy bar
# --------------------------------------------------------------------------------------
MIN_UNIT_DEGENERACY_BAR = 0.05     # if > 5% of paths freeze at zero size, J is NaN'd


# ======================================================================================
# loading  (D10 fix: the date-likeness test)
# ======================================================================================
def _index_is_datelike(idx):
    """True only for indices that are genuinely dates.

    v1 used `pd.to_datetime(idx[:5])`, which SUCCEEDS on an integer RangeIndex (integers are
    read as nanoseconds since the epoch). A bare array was therefore reported as `dated=True`
    and the LOCKED-FORWARD guard silently never fired. Numeric and boolean indices are now
    rejected outright.
    """
    if isinstance(idx, (pd.DatetimeIndex, pd.PeriodIndex)):
        return True
    try:
        if pd.api.types.is_numeric_dtype(idx) or pd.api.types.is_bool_dtype(idx):
            return False
    except Exception:
        pass
    try:
        conv = pd.to_datetime(pd.Index(idx[:5]))
    except Exception:
        return False
    return isinstance(conv, pd.DatetimeIndex)


def _to_dates_checked(values, what):
    """Parse to datetimes and refuse an obvious epoch/YYYYMMDD misparse.

    `pd.to_datetime(20230103)` returns 1970-01-01 00:00:00.020230103. v1 would have accepted
    that and compared it against LOCKED_FORWARD_START, i.e. the guard would pass on garbage.
    """
    dt = pd.to_datetime(values)
    idx = pd.DatetimeIndex(dt)
    if len(idx) and idx.min() < pd.Timestamp("1990-01-01"):
        raise ValueError(
            f"{what} parsed to pre-1990 timestamps (min = {idx.min()}). This is the "
            "signature of an integer YYYYMMDD or epoch-nanosecond misparse. The "
            "LOCKED-FORWARD guard cannot be verified on such an index; pass a properly "
            "typed date column.")
    return idx


def _series_from_frame(df, date_col, pnl_col):
    df = df.copy()
    if pnl_col is not None:
        vals = df[pnl_col]
        if date_col is not None:
            return pd.Series(vals.to_numpy(float),
                             index=_to_dates_checked(df[date_col], f"date_col '{date_col}'"))
        return pd.Series(vals.to_numpy(float), index=df.index)
    if date_col is not None:
        other = [c for c in df.columns if c != date_col]
        if len(other) != 1:
            raise ValueError(f"ambiguous pnl column among {other}; pass pnl_col=")
        return pd.Series(df[other[0]].to_numpy(float),
                         index=_to_dates_checked(df[date_col], f"date_col '{date_col}'"))
    if df.shape[1] == 1:
        return pd.Series(df.iloc[:, 0].to_numpy(float), index=df.index)
    if df.shape[1] == 2:
        return pd.Series(df.iloc[:, 1].to_numpy(float),
                         index=_to_dates_checked(df.iloc[:, 0], "first column"))
    raise ValueError(f"cannot infer date/pnl columns from {list(df.columns)}; "
                     "pass date_col= and pnl_col=")


def load_daily_pnl(src, *, date_col=None, pnl_col=None, dev_window="truncate"):
    """Load a daily $ P&L series. Identical to v1 except for the D10 guard fixes.

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

    if _index_is_datelike(s.index):
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
            "series has no usable date index -- LOCKED_FORWARD / dev-window guards NOT "
            "applied (v2: numeric indices are correctly refused as dates; v1 accepted them)")

    s = s.astype(float)
    if s.isna().any():
        flags["warnings"].append(f"{int(s.isna().sum())} NaN days zero-filled")
        s = s.fillna(0.0)
    return s, flags


# ======================================================================================
# D9 -- contract granularity, repaired
# ======================================================================================
def floor_to_multiple(x, unit):
    """Floor `x` to a multiple of `unit`, correct in floating point.

    `np.floor(0.3/0.1)` is 2, not 3, because 0.3/0.1 == 2.9999999999999996 in IEEE double.
    v1 shipped the naive form; a 0.3-unit target became 0.2 -- a whole granule lost. The
    tolerance is relative so it also holds at large multiples.
    """
    q = np.asarray(x, float) / float(unit)
    tol = 1e-9 + 1e-12 * np.abs(q)
    return np.floor(q + tol) * float(unit)


def cdar_frac_arith_from_loginc(loginc_paths, cdar_alpha=DEFAULT_CDAR_ALPHA):
    """Per-path CDaR as the ARITHMETIC mean of the worst (1-alpha) drawdown FRACTIONS.

    D11 (surfaced, not silently changed): v1's `_path_stats` returns
    `cdar_frac = 1 - exp(-mean(worst-k LOG drawdowns))` on the continuous path but the
    arithmetic mean of drawdown fractions in the other two paths, and then dollarizes
    whichever it has. The two differ (0.023 pp on the realized path, per the red team). v2
    computes the arithmetic form explicitly so `cdar_frac_arith` means the same thing
    everywhere and is the one that may legitimately be multiplied by capital.
    """
    cum = np.cumsum(np.asarray(loginc_paths, float), axis=1)
    peak = np.maximum.accumulate(cum, axis=1)
    np.maximum(peak, 0.0, out=peak)
    dd_frac = -np.expm1(-(peak - cum))              # 1 - exp(-log drawdown)
    T = dd_frac.shape[1]
    k = max(1, int((1.0 - cdar_alpha) * T))
    worst = -np.partition(-dd_frac, k - 1, axis=1)[:, :k]
    return worst.mean(axis=1)


def fixed_fraction_rounded_stats(paths_dollar, capital, leverage, ruin_dd_frac, path_len,
                                 absorbing, cdar_alpha, min_unit):
    """Fixed-fraction sizing with CONTRACT GRANULARITY (repaired; see module header D9).

    `min_unit` is the minimum tradable size expressed in the SAME units as `leverage`, i.e.
    in multiples of the strategy's one-unit P&L series. If the deployed unit is K contracts
    and single contracts are tradable, `min_unit = 1/K`.

    Model: at each session open the target size is `u* = L * E / C`, clamped at 0 and floored
    to a multiple of `min_unit`. When `u*` falls below `min_unit` the account is FLAT; its
    equity then never changes, so `u*` never recovers -- the path is permanently de-sized.
    That is a real operator state, but it makes the path's drawdown and ruin statistics
    incomparable with the continuous model, so it is counted and flagged rather than reported
    as if it were a risk reduction.
    """
    if min_unit is None or not (float(min_unit) > 0):
        raise ValueError("min_unit must be a positive number (units of `leverage`)")
    min_unit = float(min_unit)
    n_paths, T = paths_dollar.shape
    eq = np.full(n_paths, float(capital))
    peak = eq.copy()
    dd = np.empty((n_paths, T))
    eqs = np.empty((n_paths, T))
    n_flat_steps = np.zeros(n_paths, dtype=np.int64)
    first_flat = np.full(n_paths, -1, dtype=np.int64)
    n_negative_unit_steps = 0
    flat = np.zeros(n_paths, dtype=bool)

    for t in range(T):
        u_target = leverage * eq / capital
        n_negative_unit_steps += int((u_target < 0).sum())
        u = floor_to_multiple(np.maximum(u_target, 0.0), min_unit)   # (b) clamp, (a) fp fix
        flat = u <= 0.0
        newly = flat & (first_flat < 0)
        first_flat[newly] = t
        n_flat_steps += flat
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
    cdar_arith = worst.mean(axis=1)

    ever_flat = first_flat >= 0
    # invariant: a flat account's equity never changes, so the recomputed target never
    # recovers -- "ever flat" and "flat on the last step" must be the same set. Asserted
    # rather than assumed, because the whole D9 defect lives in this absorption.
    if not np.array_equal(ever_flat, flat):
        raise AssertionError("granular sizing invariant violated: de-sizing to zero is not "
                             "absorbing under the current model")
    granularity = {
        "min_unit": min_unit,
        "p_desized_to_zero": float(ever_flat.mean()),
        "p_flat_on_final_step": float(flat.mean()),
        "mean_frac_steps_flat": float((n_flat_steps / T).mean()),
        "mean_first_flat_step_given_flat": (float(first_flat[ever_flat].mean())
                                            if ever_flat.any() else None),
        "n_negative_unit_steps": int(n_negative_unit_steps),
        "p_equity_nonpositive": float((eqs.min(axis=1) <= 0).mean()),
        "degeneracy_bar": MIN_UNIT_DEGENERACY_BAR,
        "degenerate": bool(float(ever_flat.mean()) > MIN_UNIT_DEGENERACY_BAR),
        "_note": ("a de-sized (flat) path's equity is frozen, so its drawdown and ruin "
                  "statistics are NOT comparable with the continuous model -- granularity "
                  "can make P_ruin fall for a reason that is not risk reduction"),
    }
    return {
        "ruined": anyr,
        "first_ruin_step": first,
        "g_ann": np.log(term / capital) / years,
        "g_ann_nonabsorbing": np.log(np.maximum(eqs[:, -1], _EPS * capital) / capital) / years,
        "maxdd_frac": mdd,
        "maxdd_log": -np.log1p(-np.clip(mdd, None, 1 - _EPS)),
        "cdar_frac": cdar_arith,
        "cdar_frac_arith": cdar_arith,
        "cdar_log": -np.log1p(-np.clip(cdar_arith, None, 1 - _EPS)),
        "terminal_log_wealth": np.log(term / capital),
        # UNCLIPPED equity, so a caller can see what actually happened on paths whose equity
        # went negative (the log-space figures above are floored at _EPS*capital).
        "terminal_equity": eqs[:, -1].copy(),
        "granularity": granularity,
    }


# ======================================================================================
# D1 -- aggregation helpers
# ======================================================================================
def _pool(per_method_arrays, methods):
    """Concatenate per-path arrays over the headline methods -> the mixture sample."""
    return np.concatenate([per_method_arrays[m] for m in methods])


def aggregate_mixture(g_by_method, ruin_by_method, methods, lam):
    """THE aggregation rule (D1). One rule, both terms, one named probability model.

    g_by_method[m]    : (n_boot,) per-path annualized log growth under method m
    ruin_by_method[m] : (n_boot,) per-path 0/1 ruin indicator under method m

    Returns a dict with the mixture CE_g / P_ruin / J, the per-method J_m, the
    Gamma-minimax J_worst = min_m J_m, and the Monte-Carlo se of J on the pooled sample.
    """
    g_pool = _pool(g_by_method, methods)
    r_pool = _pool(ruin_by_method, methods).astype(float)
    ce_g = float(g_pool.mean())
    p_ruin = float(r_pool.mean())
    j = ce_g - lam * p_ruin

    j_by_method = {m: float(g_by_method[m].mean() - lam * float(ruin_by_method[m].mean()))
                   for m in methods}
    j_worst_method = min(j_by_method, key=j_by_method.get)
    j_best_method = max(j_by_method, key=j_by_method.get)
    j_worst = j_by_method[j_worst_method]
    j_best = j_by_method[j_best_method]

    per_path_j = g_pool - lam * r_pool
    n = int(per_path_j.size)
    se = float(per_path_j.std(ddof=1) / math.sqrt(n)) if n > 1 else float("nan")

    signs = {np.sign(j), np.sign(j_worst), np.sign(j_best)}
    signs.discard(0.0)

    return {
        "rule": AGGREGATION_RULE,
        "rule_note": AGGREGATION_RULE_NOTE,
        "methods": list(methods),
        "ce_log_growth_ann": ce_g,
        "p_ruin": p_ruin,
        "J": float(j),
        "J_by_method": j_by_method,
        "J_worst": float(j_worst),
        "J_worst_method": j_worst_method,
        "J_best": float(j_best),
        "J_best_method": j_best_method,
        "model_determined_sign": bool(len(signs) > 1),
        "n_pooled_paths": n,
        "monte_carlo_se_NOT_a_CI_on_the_process": se,
        "_se_note": ("Monte-Carlo error of the pooled mean only. It shrinks as n_boot grows "
                     "while the estimate stays conditioned on ONE realized sample; it is NOT "
                     "a confidence interval for the underlying process."),
        "_identity": ("with equal n_boot per method the pooled mean equals the arithmetic "
                      "mean over methods, and J equals the mean of J_by_method"),
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
                      lam=None,
                      franchise_years=FRANCHISE_HORIZON_YEARS,
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
    """Evaluate the REPAIRED primary objective on a daily $ P&L path.

    Differences from v1 are listed in the module header. The two that move numbers:
      * `J = CE_g - lambda*P_ruin` with BOTH terms taken under the equal-weight mixture of
        the three pre-registered bootstrap methods (v1: mean growth, max ruin);
      * `lam=None` (the default) DERIVES lambda from (franchise horizon, evaluation horizon,
        reference growth in the matching convention) instead of hard-coding 1.0.

    Pass `lam=` explicitly to override; the derivation is echoed under `spec.lambda_*`.
    """
    daily, load_flags = load_daily_pnl(pnl_path, date_col=date_col, pnl_col=pnl_col,
                                       dev_window=dev_window)
    x = daily.to_numpy(float)
    n = len(x)
    if horizon_sessions is None:
        horizon_sessions = n
    ruin_log = -math.log(1.0 - ruin_dd_frac)
    years = horizon_sessions / ANN

    # ---- D4: lambda in the convention of the CE_g it multiplies ----
    lam_derived = franchise_lambda(horizon_sessions, leverage_mode, franchise_years)
    lam_source = "derived"
    if lam is None:
        lam = lam_derived
    else:
        lam = float(lam)
        lam_source = "caller_override"
    g_ref_used = (G_REF_COMPOUNDED if leverage_mode == "fixed_fraction"
                  else G_REF_NONCOMPOUNDED)

    out = {
        "label": label,
        "module": "primary_objective_v2",
        "spec": {
            "PREREGISTERED_IN": ("runs/W17_C4_COMPLIANCE/O1_OBJECTIVE.md section 1 "
                                 "as repaired by "
                                 "runs/W17_C4_COMPLIANCE/O1_REPAIR_PREREGISTRATION.md"),
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
            "aggregation_rule": AGGREGATION_RULE,
            "aggregation_rule_note": AGGREGATION_RULE_NOTE,
            "lambda_ruin_per_yr": float(lam),
            "lambda_source": lam_source,
            "lambda_derived_value": float(lam_derived),
            "lambda_derivation": LAMBDA_DERIVATION,
            "lambda_g_ref_used": float(g_ref_used),
            "lambda_g_ref_convention": ("compounded (fixed-fraction)"
                                        if leverage_mode == "fixed_fraction"
                                        else "non-compounded (house logG)"),
            "franchise_horizon_years": float(franchise_years),
            "bootstrap_methods_headline": list(methods),
            "bootstrap_methods_diagnostic": list(diagnostic_methods),
            "n_boot": int(n_boot),
            "seed": int(seed),
            "cdar_alpha": float(cdar_alpha),
            "ann": ANN,
            "min_unit": min_unit,
            "min_unit_degeneracy_bar": MIN_UNIT_DEGENERACY_BAR,
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
    if min_unit is not None and leverage_mode != "fixed_fraction":
        raise NotImplementedError("min_unit rounding is implemented for fixed_fraction only")

    idx_bank = {}
    ruin_daily, growth_by_method, tail_daily = {}, {}, {}
    r3_by_method, bankrupt_by_method, margin_by_method = {}, {}, {}
    g_paths, ruin_paths, ruintime_paths = {}, {}, {}
    granularity_by_method = {}
    all_methods = list(methods) + list(diagnostic_methods)
    for m in all_methods:
        idx = make_indices(m, n, horizon_sessions, n_boot=n_boot, seed=seed)
        idx_bank[m] = idx
        if leverage_mode == "fixed_fraction":
            if min_unit is not None:
                st = fixed_fraction_rounded_stats(
                    x[idx], capital, leverage, ruin_dd_frac, horizon_sessions,
                    absorbing, cdar_alpha, min_unit)
                granularity_by_method[m] = st["granularity"]
                # D9: the granular model's OWN equity path decides this, not the
                # continuous model's clip test (which is what v1 reported here).
                bankrupt_by_method[m] = st["granularity"]["p_equity_nonpositive"]
            else:
                st = _path_stats(loginc[idx], ruin_log, horizon_sessions,
                                 absorbing=absorbing, cdar_alpha=cdar_alpha)
                st["cdar_frac_arith"] = cdar_frac_arith_from_loginc(loginc[idx], cdar_alpha)
                bankrupt_by_method[m] = float(bad_day[idx].any(axis=1).mean())
        else:
            st, bank = _fixed_contract_stats(x[idx], capital, leverage, ruin_dd_frac,
                                             horizon_sessions, absorbing, cdar_alpha,
                                             margin_floor_per_unit)
            bankrupt_by_method[m] = bank["p_equity_nonpositive"]
            margin_by_method[m] = bank["p_margin_floor"]

        g_paths[m] = np.asarray(st["g_ann"], float)
        ruin_paths[m] = np.asarray(st["ruined"], bool)
        if "first_ruin_step" in st:
            ruintime_paths[m] = np.asarray(st["first_ruin_step"], float)
        ruin_daily[m] = float(st["ruined"].mean())
        growth_by_method[m] = {
            **_summ(st["g_ann"], "g_ann_"),
            "g_ann_nonabsorbing_mean": float(st["g_ann_nonabsorbing"].mean()),
        }
        cdar_arith = np.asarray(st.get("cdar_frac_arith", st["cdar_frac"]), float)
        tail_daily[m] = {
            "cdar_frac": float(np.asarray(st["cdar_frac"], float).mean()),
            "cdar_frac_arith": float(cdar_arith.mean()),
            "cdar_dollar_at_capital": float(cdar_arith.mean() * capital),
            "maxdd_frac_mean": float(st["maxdd_frac"].mean()),
            "maxdd_frac_p95": float(np.quantile(st["maxdd_frac"], 0.95)),
            "_cdar_note": ("D11: `cdar_frac` keeps v1's per-path convention (log-space in "
                           "the continuous path, arithmetic elsewhere); `cdar_frac_arith` "
                           "is the arithmetic mean of drawdown FRACTIONS in every path and "
                           "is the one dollarized here"),
        }
        # R3: C-P3 comparability -- max $ drawdown of the UNLEVERED cumsum path
        eq = np.cumsum(x[idx], axis=1)
        mdd = (np.maximum.accumulate(eq, axis=1) - eq).max(axis=1)
        p95 = float(np.percentile(mdd, 95))
        r3_by_method[m] = {
            "p_maxdd_gt_cap": float((mdd * leverage > cp3_dollar_cap).mean()),
            "p95_maxdd_dollar": p95,
            # D12: v1 shipped only the UNLEVERED figure under a name that reads as though it
            # respected `leverage`. Both are given, each labelled.
            "capital_needed_at_thr_unit": float(p95 / ruin_dd_frac),
            "capital_needed_at_thr_at_leverage": float(p95 * leverage / ruin_dd_frac),
            "capital_needed_at_thr": float(p95 / ruin_dd_frac),   # v1 key, v1 meaning
        }

    # ---------------- D1: ONE aggregation rule, BOTH terms ----------------
    agg = aggregate_mixture(g_paths, ruin_paths, list(methods), lam)
    ce_g = agg["ce_log_growth_ann"]
    p_ruin_daily = agg["p_ruin"]
    J = agg["J"]

    head = [ruin_daily[m] for m in methods]

    # lambda audit: the mean first-passage time to ruin, which section 1.5 ASSUMED was H/2
    # and never measured. The corrected lambda does not use it; it is reported so the old
    # assumption can be checked and so the double-count argument can be audited.
    ruin_time_years = None
    if ruintime_paths:
        rt = _pool(ruintime_paths, list(methods))
        rr = _pool(ruin_paths, list(methods))
        if rr.any():
            ruin_time_years = float((rt[rr] + 1.0).mean() / ANN)

    out["ruin"] = {
        "definition": out["spec"]["ruin_definition_R1"],
        "daily_close": {
            **{m: ruin_daily[m] for m in all_methods},
            "headline_mixture_over_three": p_ruin_daily,
            "worst_of_three": float(max(head)),
            "worst_method": methods[int(np.argmax(head))],
            "spread_max_minus_min_over_three": float(max(head) - min(head)),
            "_note": ("HEADLINE IS THE MIXTURE (D1). The worst-of-three value is reported "
                      "because the band matters, but it is NOT the headline and it is not "
                      "mixed with a growth term from a different method. iid is a "
                      "DIAGNOSTIC method, not one of the three headline methods."),
        },
        "mean_first_ruin_years_given_ruin": ruin_time_years,
        "_ruin_time_note": ("O1_OBJECTIVE.md section 1.5 assumed ruin lands 'near the middle' "
                            "of the H-year window and used it to set lambda. v2's lambda does "
                            "not depend on this quantity (see LAMBDA_DERIVATION); it is "
                            "measured here so the old assumption is auditable."),
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
            "_note": ("fixed_fraction (continuous): fraction of resampled paths containing a "
                      "day where 1 + L*x/C <= 0. fixed_fraction with min_unit: fraction of "
                      "paths whose STEPPED granular equity actually reached <= 0 (v1 wrongly "
                      "reported the continuous test here). fixed_contracts: fraction of paths "
                      "whose equity reached <= 0. This is TRUE bankruptcy and must not be "
                      "conflated with R1 ruin."),
        },
    }
    out["growth"] = {
        "per_method": growth_by_method,
        "ce_log_growth_ann_mixture_over_three": ce_g,
        "pooled_quantiles": _summ(_pool(g_paths, list(methods)), "g_ann_pooled_"),
        "historical_single_path": _historical_growth(x, capital, leverage, leverage_mode,
                                                     ruin_log, absorbing, cdar_alpha,
                                                     min_unit, ruin_dd_frac),
    }
    out["tail"] = {"daily_close": tail_daily}
    out["aggregation"] = agg
    out["primary"] = {
        "objective_J": float(J),
        "ce_log_growth_ann": ce_g,
        "p_ruin": p_ruin_daily,
        "p_ruin_basis": "daily_close",
        "aggregation_rule": AGGREGATION_RULE,
        "lambda_ruin_per_yr": float(lam),
        "formula": "J = CE_g - lambda * P_ruin, both terms under the same mixture model",
        "J_worst_over_methods": agg["J_worst"],
        "model_determined_sign": agg["model_determined_sign"],
        "monte_carlo_se_NOT_a_CI_on_the_process": agg["monte_carlo_se_NOT_a_CI_on_the_process"],
        "n_pooled_paths": agg["n_pooled_paths"],
    }
    if agg["model_determined_sign"]:
        out["integrity"]["warnings"].append(
            f"MODEL-DETERMINED SIGN: J = {J:+.4f} under the mixture but J ranges "
            f"{agg['J_worst']:+.4f} .. {agg['J_best']:+.4f} across the three methods. "
            "The scalar must not be quoted without the band.")
    out["primary"]["objective_J_by_lambda"] = {
        str(l_): float(ce_g - l_ * p_ruin_daily) for l_ in sorted(set(LAMBDA_GRID) | {lam})}

    # ---------------- D9: granularity degeneracy ----------------
    if min_unit is not None:
        p_des = max(granularity_by_method[m]["p_desized_to_zero"] for m in methods)
        degen = p_des > MIN_UNIT_DEGENERACY_BAR
        out["granularity"] = {
            "per_method": granularity_by_method,
            "worst_p_desized_to_zero": float(p_des),
            "degeneracy_bar": MIN_UNIT_DEGENERACY_BAR,
            "degenerate": bool(degen),
        }
        out["primary"]["objective_J_is_degenerate"] = bool(degen)
        out["primary"]["objective_J_before_degeneracy_nan"] = float(J)
        if degen:
            out["integrity"]["warnings"].append(
                f"MIN_UNIT DEGENERATE: {p_des:.1%} of resampled paths de-size to zero units "
                f"and freeze (min_unit={min_unit}, L={leverage}, C={capital:g}). A frozen "
                "account cannot draw down further, so P_ruin FALLS for a reason that is not "
                "risk reduction. objective_J is set to NaN; every component is still "
                "returned under `granularity` and `growth`/`ruin`.")
            out["primary"]["objective_J"] = float("nan")

    # ---------------- O1a: intraday leg ----------------
    if intraday_path is not None:
        if leverage_mode != "fixed_fraction":
            raise NotImplementedError("intraday leg is implemented for fixed_fraction only")
        if min_unit is not None:
            raise NotImplementedError(
                "the intraday leg models continuous within-session sizing; combining it with "
                "min_unit granularity is not implemented and must not be faked")
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
        g_paths_i, ruin_paths_i = {}, {}
        for m in all_methods:
            st = _intraday_path_stats(D, idx_bank[m], ruin_log, horizon_sessions,
                                      absorbing=absorbing, cdar_alpha=cdar_alpha,
                                      chunk=intraday_chunk)
            g_paths_i[m] = np.asarray(st["g_ann"], float)
            ruin_paths_i[m] = np.asarray(st["ruined"], bool)
            ruin_intra[m] = float(st["ruined"].mean())
            tail_intra[m] = {
                "cdar_frac_bar_level": float(st["cdar_frac"].mean()),
                "cdar_frac_daymax_matched": float(st["cdar_frac_daymax"].mean()),
                "cdar_dollar_daymax_at_capital": float(st["cdar_frac_daymax"].mean() * capital),
                "maxdd_frac_mean": float(st["maxdd_frac"].mean()),
                "maxdd_frac_p95": float(np.quantile(st["maxdd_frac"], 0.95)),
            }
            growth_intra[m] = _summ(st["g_ann"], "g_ann_")

        agg_i = aggregate_mixture(g_paths_i, ruin_paths_i, list(methods), lam)
        head_i = [ruin_intra[m] for m in methods]
        out["ruin"]["intraday"] = {
            **{m: ruin_intra[m] for m in all_methods},
            "headline_mixture_over_three": agg_i["p_ruin"],
            "worst_of_three": float(max(head_i)),
            "spread_max_minus_min_over_three": float(max(head_i) - min(head_i)),
        }
        d_abs = agg_i["p_ruin"] - p_ruin_daily
        out["ruin"]["gap"] = {
            "per_method_abs": {m: float(ruin_intra[m] - ruin_daily[m]) for m in all_methods},
            "per_method_rel": {m: (float(ruin_intra[m] / ruin_daily[m] - 1.0)
                                   if ruin_daily[m] > 0 else None) for m in all_methods},
            "headline_abs": float(d_abs),
            "headline_rel": (float(agg_i["p_ruin"] / p_ruin_daily - 1.0)
                             if p_ruin_daily > 0 else None),
            "MATERIALITY_BAR": "abs >= 0.02 OR rel >= 0.20 (pre-registered)",
            "material": bool(d_abs >= 0.02 or
                             (p_ruin_daily > 0 and agg_i["p_ruin"] / p_ruin_daily - 1.0 >= 0.20)),
            "_note": ("v2 evaluates the pre-registered bar on the MIXTURE headline, "
                      "consistently with D1. The per-method gaps are all reported so a "
                      "reader can apply the bar under any single method."),
        }
        out["tail"]["intraday"] = tail_intra
        out["tail"]["gap"] = {
            "cdar_matched_ratio_per_method": {
                m: (float(tail_intra[m]["cdar_frac_daymax_matched"] /
                          tail_daily[m]["cdar_frac_arith"])
                    if tail_daily[m]["cdar_frac_arith"] > 0 else None) for m in all_methods},
            "cdar_barlevel_ratio_per_method": {
                m: (float(tail_intra[m]["cdar_frac_bar_level"] /
                          tail_daily[m]["cdar_frac_arith"])
                    if tail_daily[m]["cdar_frac_arith"] > 0 else None) for m in all_methods},
            "maxdd_ratio_per_method": {
                m: float(tail_intra[m]["maxdd_frac_mean"] / tail_daily[m]["maxdd_frac_mean"])
                for m in all_methods},
            "MATERIALITY_BAR": "matched CDaR ratio >= 1.20 (pre-registered)",
        }
        ratios = [out["tail"]["gap"]["cdar_matched_ratio_per_method"][m] for m in methods]
        ratios = [r for r in ratios if r is not None]
        # D2 is NOT fixed here (see the repair pre-registration), but the labels are made
        # honest: `max` is the most FAVOURABLE method for the hypothesis, not the worst.
        out["tail"]["gap"]["cdar_matched_ratio_max_over_methods"] = (
            float(max(ratios)) if ratios else None)
        out["tail"]["gap"]["cdar_matched_ratio_min_over_methods"] = (
            float(min(ratios)) if ratios else None)
        out["tail"]["gap"]["cdar_matched_ratio_n_methods_over_bar"] = (
            int(sum(1 for r in ratios if r >= 1.20)))
        out["tail"]["gap"]["_D2_note"] = (
            "v1 called max(ratios) the 'worst method'. It is the most favourable method for "
            "the O1a hypothesis. v2 reports max, min and how many of the three clear the "
            "1.20 bar, and takes no verdict here -- see the repair pre-registration, D2.")
        out["growth"]["per_method_intraday_absorbing"] = growth_intra
        out["aggregation_intraday"] = agg_i
        out["primary"]["objective_J_intraday_barrier"] = agg_i["J"]
        out["primary"]["ce_log_growth_ann_intraday_barrier"] = agg_i["ce_log_growth_ann"]
        out["primary"]["p_ruin_intraday_barrier"] = agg_i["p_ruin"]
        out["primary"]["J_worst_over_methods_intraday_barrier"] = agg_i["J_worst"]
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
        m: r3_by_method[m]["capital_needed_at_thr_unit"] for m in methods}
    out["legacy_diagnostics_NOT_GATES"]["_D8_note"] = (
        "these are computed at the EVALUATION horizon (horizon_sessions), not at the "
        "full-sample length that O1_OBJECTIVE.md section 5.3 quoted. The two conventions "
        "give different capital-map bands; D8 is disclosed, not resolved, in the repair "
        "pre-registration.")
    return out


def _historical_growth(x, capital, leverage, mode, ruin_log, absorbing, cdar_alpha,
                       min_unit=None, ruin_dd_frac=DEFAULT_RUIN_DD_FRAC):
    """Realized single-path growth/tail read (no resampling). DIRECT evidence."""
    n = len(x)
    if mode == "fixed_fraction" and min_unit is None:
        loginc, _ = log_increments_fixed_fraction(x, capital, leverage)
        st = _path_stats(loginc.reshape(1, -1), ruin_log, n, absorbing=absorbing,
                         cdar_alpha=cdar_alpha)
    elif mode == "fixed_fraction":
        st = fixed_fraction_rounded_stats(x.reshape(1, -1), capital, leverage, ruin_dd_frac,
                                          n, absorbing, cdar_alpha, min_unit)
    else:
        st, _ = _fixed_contract_stats(x.reshape(1, -1), capital, leverage,
                                      1 - math.exp(-ruin_log), n, absorbing, cdar_alpha,
                                      np.inf)
    return {
        "g_ann_log": float(st["g_ann"][0]),
        "g_ann_pct_equivalent": float(math.expm1(st["g_ann"][0]) * 100.0),
        "max_dd_frac": float(st["maxdd_frac"][0]),
        "cdar_frac": float(np.asarray(st["cdar_frac"], float)[0]),
        "ruin_hit": bool(st["ruined"][0]),
        "_note": "ONE realized path. Not a distribution. Not evidence about the future.",
    }


# ======================================================================================
# convenience: leverage curve
# ======================================================================================
def leverage_curve(pnl_path, capital=DEFAULT_CAPITAL, grid=LEVERAGE_GRID, **kw):
    """J, CE_g and P_ruin over a leverage grid. Reported for SHAPE. Not a recommendation.

    NOTE (v2 disclosure): every grid point uses the SAME resampled index matrices (same seed,
    same n, same horizon), so DIFFERENCES across L are paired and reliable, but the LEVEL of
    the curve and the location of its turning point carry one draw's worth of Monte-Carlo
    noise that is common to the whole curve. `mc_se` is reported per point.
    """
    rows = []
    for L in grid:
        r = primary_objective(pnl_path, capital=capital, leverage=L, **kw)
        row = {"leverage": L,
               "J": r["primary"]["objective_J"],
               "J_worst_over_methods": r["primary"]["J_worst_over_methods"],
               "model_determined_sign": r["primary"]["model_determined_sign"],
               "mc_se": r["primary"]["monte_carlo_se_NOT_a_CI_on_the_process"],
               "ce_log_growth_ann": r["primary"]["ce_log_growth_ann"],
               "p_ruin_daily_close": r["primary"]["p_ruin"],
               "p_ruin_worst_of_three": r["ruin"]["daily_close"]["worst_of_three"],
               "p_ruin_spread": r["ruin"]["daily_close"]["spread_max_minus_min_over_three"],
               "lambda": r["primary"]["lambda_ruin_per_yr"]}
        if "p_ruin_intraday_barrier" in r["primary"]:
            row["p_ruin_intraday"] = r["primary"]["p_ruin_intraday_barrier"]
            row["J_intraday_barrier"] = r["primary"]["objective_J_intraday_barrier"]
        rows.append(row)
    return pd.DataFrame(rows)
