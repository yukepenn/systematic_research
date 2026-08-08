"""SMV2AG adaptive-ceiling machinery.

Implements the spec's mechanism EXACTLY:
  raw_m(t) = VolMult_m * sigma460(t)          (unclamped product, every bar)
  ceil_m(t) = max(300.0, P-th percentile of {raw_m(t-1), ..., raw_m(t-N)})
              (trailing N bars, STRICTLY causal -- bar t's own raw_m(t) excluded)
  warmup (t < N + min_count, min_count=30 matching sigma_series):
              ceil_m(t) = 300.0 (the fixed incumbent ceiling), matching the
              existing fallback-during-warmup philosophy already in the code
              for sigma itself.

member_states_adaptive() is a VERBATIM copy of sm01_solarsim.member_states()
(src/analytics/sm01_solarsim.py, read directly, not re-derived) with exactly one
change: resolve_s()'s upper bound is hi_arr[t] (a per-bar array) instead of the
scalar hi = smax_ticks*TICK. Every other line -- the flip state machine, anchor
tracking, S re-evaluation cadence (only at flip bars, per the spec's explicit
instruction that this is UNCHANGED) -- is untouched. member_trades() itself is
NOT modified at all (it only consumes s_eff, which is now array-driven upstream).

Scale-equivariance shortcut (verified): because raw_m(t) = vm * sigma(t) and vm>0
is a per-member positive scalar, the P-th percentile of {vm*sigma(t-1..t-N)} equals
vm * (P-th percentile of {sigma(t-1..t-N)}). So the trailing rolling percentile of
the SHARED sigma460 array is computed ONCE per (P,N) cell (independent of member),
then scaled by each member's vol_mult -- mathematically identical to computing each
member's raw_m rolling percentile separately, just far cheaper (13x fewer rolling-
quantile passes). This is a performance optimization only, not a mechanism change.
"""
import sys, os
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src", "analytics"))
import sm01_solarsim as sm
from common import CEILING_FLOOR_PTS

TICK = sm.TICK
MIN_COUNT = 30  # matches sm01_solarsim.sigma_series's min_count default


def rolling_percentile_sigma(sig: np.ndarray, N: int, P: float) -> np.ndarray:
    """Causal trailing-N-bar P-th percentile of the sigma460 array, computed ONCE
    per (P,N) and reused for every member via the vm-scaling shortcut above.
    rq[t] = percentile_P({sig[t-N], ..., sig[t-1]}) -- pandas .rolling(N).quantile(q)
    at position t covers indices [t-N+1, t], so .shift(1) moves that window to
    [t-N, t-1], which is exactly the spec's trailing-N-bars-excluding-bar-t window.
    min_periods=N enforces NaN (-> warmup fallback below) until a full window of
    valid sigma is available, i.e. for t < N+MIN_COUNT (sigma itself is NaN for
    t<MIN_COUNT=30), matching the spec's warmup threshold exactly."""
    s = pd.Series(sig)
    q = P / 100.0
    rq = s.rolling(window=N, min_periods=N).quantile(q, interpolation="linear").shift(1)
    return rq.to_numpy()


def ceiling_for_member(rq: np.ndarray, vol_mult: float, N: int, n: int) -> np.ndarray:
    """ceil_m(t) in POINTS (same units as sigma/S, matching the incumbent's
    hi=smax_ticks*TICK convention). Floored at CEILING_FLOOR_PTS=300.0pt (1200t)
    so it can only WIDEN relative to the incumbent (per spec, strict superset).
    Warmup (t < N+MIN_COUNT): fixed 300.0pt (also naturally satisfied by rq's NaN
    there, but the explicit index mask is the spec's literal instruction and is
    applied redundantly/defensively so no floating-point edge case at exactly
    t=N+MIN_COUNT can silently fall through)."""
    warm = np.arange(n) < (N + MIN_COUNT)
    raw_ceil = vol_mult * rq
    ceil_m = np.where(warm, CEILING_FLOOR_PTS, np.maximum(CEILING_FLOOR_PTS, raw_ceil))
    # defensive: any residual NaN outside the declared warmup window (should not
    # occur given the min_periods=N construction above) falls back to the floor,
    # never left as NaN feeding into resolve_s.
    resid_nan = ~warm & ~np.isfinite(ceil_m)
    if resid_nan.any():
        ceil_m = np.where(resid_nan, CEILING_FLOOR_PTS, ceil_m)
    return ceil_m


def member_states_adaptive(close: np.ndarray, sigma: np.ndarray, vol_mult: float,
                            hi_arr: np.ndarray, stop_mult_ticks: float = 179.0,
                            smin_ticks: float = 40.0, start_up: bool = False):
    """VERBATIM copy of sm01_solarsim.member_states (V3 state machine, AnchorMode 0,
    ThresholdMode 1) with ONLY the resolve_s() upper-bound term changed: hi is now
    hi_arr[t] (per-bar adaptive ceiling, points) instead of the scalar
    smax_ticks*TICK. Everything else -- including that S is re-evaluated ONLY at
    flip bars (resolve_s(t) is called exactly at the same call sites as the
    incumbent: bar 0 seed, and each flip bar) -- is byte-identical to the
    committed function."""
    n = close.size
    lo = smin_ticks * TICK
    fallback = stop_mult_ticks * TICK

    def resolve_s(t):
        s = sigma[t]
        if not np.isfinite(s) or s <= 0:
            return fallback
        return min(max(vol_mult * s, lo), hi_arr[t])

    is_up = np.zeros(n, dtype=bool)
    flip = np.zeros(n, dtype=np.int8)
    s_eff = np.empty(n)
    anchor_out = np.empty(n)

    up = bool(start_up)
    anchor = close[0]
    S = resolve_s(0)
    is_up[0] = up; s_eff[0] = S; anchor_out[0] = anchor

    for t in range(1, n):
        px = close[t]
        if up:
            if px >= anchor:
                anchor = px
            elif px < anchor - S:
                up = False
                S = resolve_s(t)
                anchor = px
                flip[t] = -1
        else:
            if px <= anchor:
                anchor = px
            elif px > anchor + S:
                up = True
                S = resolve_s(t)
                anchor = px
                flip[t] = 1
        is_up[t] = up; s_eff[t] = S; anchor_out[t] = anchor
    return is_up, flip, s_eff, anchor_out


def build_pend_adaptive(bars, sig, vms, N, P):
    """Adaptive-ceiling analogue of common.build_pend: rebuild the per-member
    `pend` matrix using member_states_adaptive + the (P,N)-cell rolling-percentile
    ceiling (shared rq computed once, scaled per member). Returns
    (pend_matrix, ceil_by_member dict[vm] -> ceil_m array, rq array)."""
    close = bars["close"].to_numpy()
    n = len(bars)
    rq = rolling_percentile_sigma(sig, N, P)
    PEND = []
    ceil_by_member = {}
    for vm_ in vms:
        ceil_m = ceiling_for_member(rq, float(vm_), N, n)
        ceil_by_member[vm_] = ceil_m
        is_up, flip, s_eff, anchor = member_states_adaptive(
            close, sig, float(vm_), ceil_m, smin_ticks=40.0)
        fills, pos, pend = sm.member_trades(bars, is_up, flip, s_eff, anchor)
        PEND.append(pend)
    return np.column_stack(PEND), ceil_by_member, rq
