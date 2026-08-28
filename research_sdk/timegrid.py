"""timegrid.py -- SAFE TIME ARITHMETIC for causal feature engines.  ENGINEERING_ONLY / ZERO_ALPHA.

WHY THIS EXISTS, in one line of code:

    step = np.arange(-30, 0) * NS          # bbo_v1.py:119, 2026-08-28

`np.arange(-30, 0)` has dtype **int32 on Windows**. `NS = 1_000_000_000` fits in int32, so NumPy's
value-based casting keeps the product in int32, and `-30 * 1e9 = -3e10` OVERFLOWS. Silently: NumPy
raises no warning for integer overflow in an array-scalar product. The intended offsets
`[-30s, -1s]` became `[-2.115s, +2.065s]`, FIFTEEN OF THIRTY POSITIVE, so seven features read up to
2.065 s PAST the decision instant. The result looked spectacular -- $5,124.76/session, t 6.76, and
it beat a real refitted null at the 100.0th percentile, because every null replicate recomputed the
same leaky features. Causally corrected it earns -$1,785.88/session.

THE RULE THIS MODULE ENFORCES:

    NEVER let NumPy infer the dtype of a time offset. Declare int64 and ASSERT the result.

Every constructor here returns int64 and verifies its own output against the DECLARED intent:
count, exact min, exact max, and sign. A helper that silently returns the wrong thing is exactly
what was already survived once.
"""
from __future__ import annotations

import numpy as np

NS_PER_US = 1_000
NS_PER_MS = 1_000_000
NS_PER_S = 1_000_000_000
NS_PER_MIN = 60 * NS_PER_S
NS_PER_HOUR = 3600 * NS_PER_S

INT64_MAX = np.iinfo(np.int64).max
INT64_MIN = np.iinfo(np.int64).min


class TimeArithmeticError(AssertionError):
    """Raised when a time computation is not provably safe. Never caught inside a feature engine."""


def safe_scale(values, scale) -> np.ndarray:
    """Multiply integer `values` by integer `scale` in int64, and PROVE no overflow occurred.

    The proof is a round-trip division rather than a bound estimate: if `out // scale` does not
    return the original value for every element, the product wrapped.
    """
    a = np.asarray(values)
    if not np.issubdtype(a.dtype, np.integer):
        raise TimeArithmeticError(f"safe_scale expects an integer array, got dtype {a.dtype}")
    s = int(scale)
    if s == 0:
        raise TimeArithmeticError("scale of 0 is never a valid time scale")
    a64 = a.astype(np.int64, copy=False)
    out = a64 * np.int64(s)
    if a64.size and not np.array_equal(out // np.int64(s), a64):
        raise TimeArithmeticError(
            f"INTEGER OVERFLOW scaling by {s}: round-trip failed. This is the bbo_v1.py:119 class.")
    lim = INT64_MAX // abs(s)
    if a64.size and int(np.max(np.abs(a64))) > lim:
        raise TimeArithmeticError(f"magnitude {int(np.max(np.abs(a64)))} exceeds int64/{s} = {lim}")
    return out


def _verify(off: np.ndarray, n: int, lo_ns: int, hi_ns: int, sign: str, what: str) -> np.ndarray:
    if off.dtype != np.int64:
        raise TimeArithmeticError(f"{what}: dtype is {off.dtype}, must be int64")
    if off.size != n:
        raise TimeArithmeticError(f"{what}: produced {off.size} offsets, declared {n}")
    if sign == "past" and not np.all(off < 0):
        bad = int(np.sum(off >= 0))
        raise TimeArithmeticError(
            f"{what}: {bad} of {off.size} LOOKBACK offsets are >= 0 -- these would read the FUTURE. "
            f"observed range [{off.min()}, {off.max()}] ns")
    if sign == "future" and not np.all(off > 0):
        bad = int(np.sum(off <= 0))
        raise TimeArithmeticError(f"{what}: {bad} of {off.size} HORIZON offsets are <= 0")
    if int(off.min()) != lo_ns or int(off.max()) != hi_ns:
        raise TimeArithmeticError(
            f"{what}: DECLARED range [{lo_ns}, {hi_ns}] ns but GENERATED "
            f"[{int(off.min())}, {int(off.max())}] ns. Declared and generated must match exactly.")
    return off


def lookback_offsets_s(first_s: int, last_s: int, step_s: int = 1) -> np.ndarray:
    """Strictly-past offsets in NANOSECONDS, int64, inclusive of both endpoints.

    `lookback_offsets_s(30, 1)` -> 30 offsets, -30e9 .. -1e9. Both bounds are given as POSITIVE
    seconds-into-the-past, so a sign slip cannot silently produce a future read.
    """
    if not (isinstance(first_s, int) and isinstance(last_s, int) and isinstance(step_s, int)):
        raise TimeArithmeticError("bounds must be Python ints, so no dtype can be inferred")
    if first_s < last_s:
        raise TimeArithmeticError(f"first_s ({first_s}) must be the FURTHEST back, >= last_s")
    if last_s <= 0:
        raise TimeArithmeticError(f"last_s ({last_s}) must be > 0; a 0-second lookback IS the "
                                  f"decision instant, which is not strictly past")
    secs = np.arange(-first_s, -last_s + 1, step_s, dtype=np.int64)
    off = safe_scale(secs, NS_PER_S)
    return _verify(off, secs.size, -first_s * NS_PER_S, -last_s * NS_PER_S, "past",
                   f"lookback_offsets_s({first_s}, {last_s}, {step_s})")


def horizon_offsets_s(*seconds: int) -> np.ndarray:
    """Strictly-future offsets in NANOSECONDS, int64."""
    for s in seconds:
        if not isinstance(s, int):
            raise TimeArithmeticError("horizon seconds must be Python ints")
        if s <= 0:
            raise TimeArithmeticError(f"horizon {s} must be > 0")
    v = np.array(sorted(seconds), dtype=np.int64)
    off = safe_scale(v, NS_PER_S)
    return _verify(off, v.size, int(v.min()) * NS_PER_S, int(v.max()) * NS_PER_S, "future",
                   f"horizon_offsets_s{seconds}")


def session_grid_ns(day_ns: int, start_hhmmss: str, end_hhmmss: str, step_s: int) -> np.ndarray:
    """Decision grid in absolute int64 nanoseconds, inclusive of both endpoints.

    Asserts strict monotonicity and that the step is exactly as declared everywhere.
    """
    if not isinstance(day_ns, (int, np.integer)):
        raise TimeArithmeticError("day_ns must be an integer nanosecond timestamp")
    t0 = int(day_ns) + hhmmss_to_ns(start_hhmmss)
    t1 = int(day_ns) + hhmmss_to_ns(end_hhmmss)
    if t1 <= t0:
        raise TimeArithmeticError(f"end {end_hhmmss} is not after start {start_hhmmss}")
    step = int(step_s) * NS_PER_S
    g = np.arange(t0, t1 + 1, step, dtype=np.int64)
    if g.dtype != np.int64:
        raise TimeArithmeticError(f"grid dtype {g.dtype}")
    d = np.diff(g)
    if g.size > 1 and (not np.all(d == step)):
        raise TimeArithmeticError("grid step is not uniform")
    if not np.all(np.diff(g) > 0):
        raise TimeArithmeticError("grid is not strictly increasing")
    return g


def hhmmss_to_ns(hhmmss: str) -> int:
    h, m, s = (int(v) for v in hhmmss.split(":"))
    if not (0 <= h < 24 and 0 <= m < 60 and 0 <= s < 60):
        raise TimeArithmeticError(f"bad time-of-day {hhmmss}")
    return ((h * 60 + m) * 60 + s) * NS_PER_S


def assert_strictly_before(source_ts, decision_ts, label: str = "feature") -> None:
    """ROW-BY-ROW proof that no source event at or after the decision instant was used.

    `source_ts` is the MAX source timestamp actually consumed per decision. This is the assertion
    that `bbo_v1.py` never made about its path offsets, and it is the whole reason the leak
    survived four leak probes and a refitted null.
    """
    s = np.asarray(source_ts, dtype=np.int64)
    d = np.asarray(decision_ts, dtype=np.int64)
    if s.shape != d.shape:
        raise TimeArithmeticError(f"{label}: shape mismatch {s.shape} vs {d.shape}")
    bad = np.where(s >= d)[0]
    if bad.size:
        i = int(bad[0])
        raise TimeArithmeticError(
            f"{label}: CAUSALITY VIOLATION on {bad.size} of {s.size} decisions. "
            f"first at index {i}: max source ts {s[i]} >= decision ts {d[i]} "
            f"(+{(s[i] - d[i]) / 1e9:.6f} s into the future)")


def describe_offsets(off) -> dict:
    """Emit the declared/generated summary a report must show, rather than assert privately."""
    o = np.asarray(off, dtype=np.int64)
    return {"n": int(o.size), "dtype": str(o.dtype),
            "min_s": float(o.min()) / 1e9, "max_s": float(o.max()) / 1e9,
            "n_positive": int(np.sum(o > 0)), "n_zero": int(np.sum(o == 0)),
            "n_negative": int(np.sum(o < 0))}
