"""test_timegrid.py -- the int32-overflow failure class, pinned so it cannot recur silently.

This test exists because the bug was ECONOMICALLY MATERIAL, not as ceremony. On 2026-08-28 a single
unguarded expression turned a -$1,785.88/session loser into a +$5,124.76/session "candidate" that
passed seven preregistered gates, four leak probes, and a genuine refitted null at the 100.0th
percentile.

Run: python research_sdk/test_timegrid.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from timegrid import (  # noqa: E402
    NS_PER_S, TimeArithmeticError, assert_strictly_before, describe_offsets,
    horizon_offsets_s, hhmmss_to_ns, lookback_offsets_s, safe_scale, session_grid_ns,
)

FAIL = []


def check(name, fn):
    try:
        fn()
        print(f"  PASS  {name}")
    except Exception as e:                                              # noqa: BLE001
        FAIL.append((name, e))
        print(f"  FAIL  {name}\n        {type(e).__name__}: {e}")


def test_the_exact_bug():
    """THE REGRESSION. Reproduce bbo_v1.py:119 and prove the safe path fixes it."""
    unsafe = np.arange(-30, 0) * NS_PER_S
    # On Windows/NumPy<2 this is int32 and overflows. Emulate deterministically so the test is
    # meaningful on ANY platform rather than silently vacuous on Linux/NumPy 2.
    emulated = (np.arange(-30, 0, dtype=np.int32) * np.int32(NS_PER_S)).astype(np.int64)
    for label, arr in (("native", unsafe), ("emulated int32", emulated)):
        d = describe_offsets(arr)
        print(f"        {label:<16} dtype {str(arr.dtype):<8} range "
              f"[{d['min_s']:+.6f}s, {d['max_s']:+.6f}s]  positive: {d['n_positive']}/30")
    assert describe_offsets(emulated)["n_positive"] == 15, (
        "the emulated int32 path must reproduce the historical failure: 15 positive offsets")
    assert describe_offsets(emulated)["max_s"] > 2.0, "must reach ~+2.065 s into the future"

    safe = lookback_offsets_s(30, 1)
    assert safe.dtype == np.int64
    assert safe.size == 30
    assert np.all(safe < 0), "every lookback offset must be strictly negative"
    assert int(safe.min()) == -30 * NS_PER_S and int(safe.max()) == -1 * NS_PER_S
    assert np.array_equal(safe, np.arange(-30, 0, dtype=np.int64) * NS_PER_S)
    print(f"        safe             dtype int64    exactly 30 offsets, "
          f"[-30.000000s, -1.000000s], 0 positive")


def test_safe_scale_catches_overflow():
    bad = np.arange(-30, 0, dtype=np.int32)
    try:
        safe_scale(bad, NS_PER_S)
    except TimeArithmeticError:
        raise AssertionError("safe_scale must UPCAST int32 input, not reject it")
    out = safe_scale(bad, NS_PER_S)
    assert out.dtype == np.int64 and np.all(out < 0)
    # a genuine overflow must be caught
    huge = np.array([2 ** 62], dtype=np.int64)
    try:
        safe_scale(huge, NS_PER_S)
    except TimeArithmeticError:
        return
    raise AssertionError("safe_scale failed to detect a real int64 overflow")


def test_lookback_rejects_bad_intent():
    for args in ((1, 30), (0, 0), (30, 0), (-5, -1)):
        try:
            lookback_offsets_s(*args)
        except TimeArithmeticError:
            continue
        raise AssertionError(f"lookback_offsets_s{args} should have been rejected")


def test_horizon_is_strictly_future():
    h = horizon_offsets_s(60)
    assert h.dtype == np.int64 and h[0] == 60 * NS_PER_S
    for bad in (0, -60):
        try:
            horizon_offsets_s(bad)
        except TimeArithmeticError:
            continue
        raise AssertionError(f"horizon_offsets_s({bad}) should have been rejected")


def test_grid():
    day = int(np.datetime64("2026-06-22T00:00:00", "ns").astype("int64"))
    g = session_grid_ns(day, "10:00:00", "15:30:00", 60)
    assert g.dtype == np.int64
    assert g.size == 331, f"10:00-15:30 at 60 s must be 331 decisions, got {g.size}"
    assert int(g[0]) == day + hhmmss_to_ns("10:00:00")
    assert int(g[-1]) == day + hhmmss_to_ns("15:30:00")
    assert np.all(np.diff(g) == 60 * NS_PER_S)


def test_row_by_row_causality_assertion():
    dec = np.arange(10, dtype=np.int64) * NS_PER_S + 10 ** 12
    assert_strictly_before(dec - 1, dec, "clean")
    for offending in (dec, dec + 1):
        try:
            assert_strictly_before(offending, dec, "leaky")
        except TimeArithmeticError:
            continue
        raise AssertionError("assert_strictly_before missed a violation")


def test_it_would_have_caught_the_real_bug():
    """End-to-end: feed the historical offsets through the guard and require rejection."""
    emulated = (np.arange(-30, 0, dtype=np.int32) * np.int32(NS_PER_S)).astype(np.int64)
    t = np.int64(10 ** 15)
    src = t + emulated.max()                     # the furthest-reaching source instant used
    try:
        assert_strictly_before(np.array([src]), np.array([t]), "bbo_v1 path features")
    except TimeArithmeticError as e:
        assert "+2.06" in str(e), f"expected the +2.065 s violation to be reported, got: {e}"
        return
    raise AssertionError("the guard failed to reject the exact historical defect")


if __name__ == "__main__":
    print("test_timegrid -- pinning the int32 time-overflow class")
    print(f"  numpy {np.__version__}   platform default int dtype: {np.array([1]).dtype}")
    check("THE REGRESSION: bbo_v1.py:119 int32 overflow", test_the_exact_bug)
    check("safe_scale upcasts and detects real overflow", test_safe_scale_catches_overflow)
    check("lookback rejects reversed/zero/negative intent", test_lookback_rejects_bad_intent)
    check("horizon offsets are strictly future", test_horizon_is_strictly_future)
    check("session grid is int64, uniform, 331 decisions", test_grid)
    check("row-by-row causality assertion has teeth", test_row_by_row_causality_assertion)
    check("the guard rejects the REAL historical offsets", test_it_would_have_caught_the_real_bug)
    print(f"\n  {'ALL PASS' if not FAIL else f'{len(FAIL)} FAILURE(S)'}")
    sys.exit(1 if FAIL else 0)
