"""keysafe.py -- KEY AND JOIN SAFETY across pandas / NumPy / Python type boundaries.

WHY THIS EXISTS:

    dates  = np.sort(panel["date"].unique())          -> numpy.datetime64
    bydate = {d: set(g) for d, g in panel.groupby("date")["contract_id"]}   -> pandas.Timestamp keys
    bydate.get(dates[i])                              -> ALWAYS None

`numpy.datetime64` and `pandas.Timestamp` do not hash equal, so every lookup missed. CARRY00's first
run reported ZERO simultaneously-live contract pairs for ALL 25 roots and would have returned a
completely plausible `CLOSED-BY-DATA` verdict. It was caught only because ES, with 71 contracts over
4,433 active days, cannot truly have zero overlap -- i.e. by a human expectation, not by the code.

THE RULE: canonicalise keys at every boundary, and ASSERT that lookups actually resolve. Never
infer correctness from a plausible row count -- a plausible row count is exactly what a silent
key mismatch produces.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


class KeyIntegrityError(AssertionError):
    """Raised when a join/lookup cannot be shown to have matched what it should have."""


def canon_ts(x):
    """Canonical timestamp key: a pandas.Timestamp, from anything date-like."""
    if isinstance(x, pd.Timestamp):
        return x
    return pd.Timestamp(x)


def canon_index(values) -> list:
    return [canon_ts(v) for v in values]


def build_lookup(keys, values, *, name: str = "lookup") -> dict:
    """Dict keyed by canonical timestamps, with a uniqueness assertion."""
    ks = canon_index(keys)
    if len(set(ks)) != len(ks):
        dup = len(ks) - len(set(ks))
        raise KeyIntegrityError(f"{name}: {dup} duplicate keys -- a dict would silently drop them")
    return dict(zip(ks, values))


def assert_resolves(lookup: dict, probe_keys, *, min_frac: float = 1.0, name: str = "lookup"):
    """Assert that probing `lookup` with `probe_keys` actually finds entries.

    This is the guard CARRY00 lacked. `min_frac=1.0` means every probe key must resolve.
    """
    ks = canon_index(probe_keys)
    hit = sum(1 for k in ks if k in lookup)
    frac = hit / max(len(ks), 1)
    if frac < min_frac:
        kt = type(next(iter(lookup))).__name__ if lookup else "EMPTY"
        pt = type(ks[0]).__name__ if ks else "EMPTY"
        raise KeyIntegrityError(
            f"{name}: only {hit}/{len(ks)} probe keys resolved ({frac:.4f} < {min_frac}). "
            f"lookup key type={kt}, probe key type={pt}. "
            f"A silent type mismatch returns a plausible-looking empty result.")
    return frac


def safe_merge(left: pd.DataFrame, right: pd.DataFrame, on, *, how: str = "inner",
               expect_rows: int | None = None, max_unmatched: int = 0,
               name: str = "merge") -> pd.DataFrame:
    """Merge with row-count preservation and unmatched-count assertions."""
    cols = [on] if isinstance(on, str) else list(on)
    for c in cols:
        for df, side in ((left, "left"), (right, "right")):
            if c not in df.columns:
                raise KeyIntegrityError(f"{name}: key '{c}' missing from {side}")
        if str(left[c].dtype) != str(right[c].dtype):
            raise KeyIntegrityError(
                f"{name}: key '{c}' dtype differs -- left {left[c].dtype}, right {right[c].dtype}. "
                f"Canonicalise before merging; mismatched dtypes match zero rows silently.")
    out = left.merge(right, on=cols, how=how, indicator=True)
    unmatched = int((out["_merge"] != "both").sum())
    if unmatched > max_unmatched:
        raise KeyIntegrityError(f"{name}: {unmatched} unmatched rows (max {max_unmatched})")
    if expect_rows is not None and len(out) != expect_rows:
        raise KeyIntegrityError(f"{name}: produced {len(out)} rows, expected {expect_rows}")
    if len(out) == 0 and len(left):
        raise KeyIntegrityError(f"{name}: EMPTY result from a non-empty left frame -- "
                                f"the classic silent key-type mismatch")
    return out.drop(columns="_merge")


def known_match_control(lookup: dict, known_key, *, name: str = "lookup"):
    """A DELIBERATE known-match control: a key that MUST be present.

    Passing a probe on data alone can be vacuous. This asserts against an externally known fact.
    """
    k = canon_ts(known_key)
    if k not in lookup:
        raise KeyIntegrityError(
            f"{name}: known-match control FAILED -- {k} must be present and is not")
    return True


def assert_unique_index(df: pd.DataFrame, cols, *, name: str = "frame"):
    d = df.duplicated(subset=list(cols) if not isinstance(cols, str) else [cols]).sum()
    if d:
        raise KeyIntegrityError(f"{name}: {int(d)} duplicate rows on {cols}")
    return True


def canon_datetime_column(df: pd.DataFrame, col: str) -> pd.DataFrame:
    out = df.copy()
    out[col] = pd.to_datetime(out[col])
    return out


def ns(x) -> np.int64:
    """Absolute nanoseconds as int64, from anything date-like. The other canonical form."""
    return np.int64(canon_ts(x).value)
