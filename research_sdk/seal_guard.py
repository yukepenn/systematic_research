"""GENESIS data seal — structural enforcement of the >= 2026-08-01 virgin-data boundary.

CLAUDE.md §5 / research/operational/LOCKED_FORWARD.md: everything through session
2026-07-31 is research-consumed; 2026-08-01 onward is VIRGIN and may not be read, printed
or persisted outside a scheduled MONITORING_CALENDAR read. This module makes that seal a
mechanical property of any DataFrame passing through it, instead of a per-call-site
judgment call (the same failure class session_boundary.py removed for backtest windows).

Session semantics (CLAUDE.md §6, session_boundary.py): CME index-future sessions run
18:00 ET -> 17:00 ET next day and bars are END-stamped. The session labeled 2026-08-01
therefore OPENS at 18:00 ET on calendar 2026-07-31, so:

  * a bar timestamped 2026-07-31 17:00:00 ET **or earlier** is pre-seal (it closed at or
    before the last consumed session's 17:00 close);
  * any timestamp AFTER 2026-07-31 17:00:00 ET belongs to (or sits in the maintenance
    halt immediately before) the sealed 2026-08-01 session and is treated as SEALED —
    the halt hour 17:00-18:00 is sealed too, conservatively;
  * a pure DATE (no time component) is a session/day label: sealed iff >= 2026-08-01.

Naive datetimes are interpreted as ET wall-clock time deliberately: every repo data
store and NT8/CrossTrade payload stamps exchange-session time (ET) without a tz marker
(CLAUDE.md §6 "Timestamps in payloads are exchange-session time (ET)"). Interpreting
naive as UTC would shift the boundary 4-5 hours EARLY-side open (letting sealed evening
bars through in summer), so ET is both the documented convention and the conservative
reading. tz-aware values are converted to ET before comparison.

Error messages and logs report COUNTS only, never the offending values — the seal
forbids printing sealed values, so the guard itself must not leak them while firing.
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd

try:
    from research_sdk.session_boundary import (
        ET,
        LOCKED_FORWARD_LAST_CONSUMED_SESSION,
    )
except ImportError:  # run as a loose script: python research_sdk/seal_guard.py
    import os
    import sys

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from research_sdk.session_boundary import (
        ET,
        LOCKED_FORWARD_LAST_CONSUMED_SESSION,
    )

#: First sealed session date (exchange-session ET label). Derived from — and asserted
#: against — session_boundary.LOCKED_FORWARD_LAST_CONSUMED_SESSION so the two can never
#: silently drift apart. Changes ONLY alongside LOCKED_FORWARD.md itself.
SEAL_DATE = date(2026, 8, 1)
assert SEAL_DATE == LOCKED_FORWARD_LAST_CONSUMED_SESSION + timedelta(days=1), (
    "seal_guard.SEAL_DATE disagrees with session_boundary."
    "LOCKED_FORWARD_LAST_CONSUMED_SESSION — resolve against LOCKED_FORWARD.md"
)

#: Last pre-seal instant, as naive ET wall-clock: the 17:00 ET close of session
#: 2026-07-31 (bars are END-stamped, so a bar stamped exactly 17:00:00 is pre-seal).
#: Strictly after this instant is sealed — including the 17:00-18:00 maintenance halt.
SEAL_CUTOFF_ET_WALLCLOCK = pd.Timestamp(
    datetime.combine(SEAL_DATE - timedelta(days=1), datetime.min.time())
) + pd.Timedelta(hours=17)


class SealError(RuntimeError):
    """Raised when data on/after the seal reaches an unauthorized read path.

    Raising (not returning a bool) is deliberate — a caller that forgets to check a
    return value still gets stopped (same doctrine as session_boundary.BoundaryError).
    The message NEVER contains the sealed values themselves, only counts.
    """


# --- override flag (module-level, set only by authorized_read) ---------------------
_OVERRIDE_TOKEN: str | None = None


@contextmanager
def authorized_read(token: str):
    """Explicit, LOUD seal-bypass context. The ONLY way assert_presealed can pass
    sealed data, and it can never happen silently: entering prints the token, and every
    bypassed assertion prints 'SEAL OVERRIDE: <token> <context>' as it happens.

    `token` should name the recorded authorization (e.g. a MONITORING_CALENDAR entry
    id). An empty/blank token is refused — an override must be attributable.
    """
    global _OVERRIDE_TOKEN
    if not isinstance(token, str) or not token.strip():
        raise SealError("authorized_read requires a non-empty token naming the recorded authorization")
    if _OVERRIDE_TOKEN is not None:
        raise SealError("nested authorized_read contexts are not allowed")
    print(f"SEAL OVERRIDE ACTIVE: token={token!r} — sealed reads inside this context will be announced per-call")
    _OVERRIDE_TOKEN = token
    try:
        yield
    finally:
        _OVERRIDE_TOKEN = None
        print(f"SEAL OVERRIDE ENDED: token={token!r}")


# --- normalization -----------------------------------------------------------------
def _wallclock_et_one(v):
    """Coerce a single value to a naive ET wall-clock pandas Timestamp (fail-closed)."""
    if v is None or (isinstance(v, float) and np.isnan(v)):
        raise SealError("null timestamp value — refusing to classify it as pre-seal")
    if isinstance(v, pd.Timestamp):
        return v.tz_convert(ET).tz_localize(None) if v.tzinfo is not None else v
    if isinstance(v, datetime):  # datetime is checked before date (datetime IS a date)
        return pd.Timestamp(v.astimezone(ET).replace(tzinfo=None) if v.tzinfo else v)
    if isinstance(v, date):
        return pd.Timestamp(datetime.combine(v, datetime.min.time()))
    if isinstance(v, str):
        try:
            ts = pd.Timestamp(v)
        except (ValueError, TypeError) as e:
            raise SealError(f"unparseable timestamp string in sealed-check column: {e}") from None
        if pd.isna(ts):
            raise SealError("NaT from timestamp string — refusing to classify it as pre-seal")
        return ts.tz_convert(ET).tz_localize(None) if ts.tzinfo is not None else ts
    raise SealError(f"unsupported timestamp type {type(v).__name__} — refusing to guess (fail closed)")


def _wallclock_et(series: pd.Series) -> pd.Series:
    """Coerce a whole column to naive ET wall-clock Timestamps.

    datetime64 (naive)    -> already ET wall-clock by repo convention, used as-is.
    datetime64 (tz-aware) -> converted to ET, tz marker dropped (wall-clock compare).
    object                -> element-wise: datetime / date / ISO-string, each handled;
                             anything else (or NaT/None) raises SealError — a value the
                             guard cannot date is treated as sealed, never waved through.
    """
    if pd.api.types.is_datetime64_any_dtype(series):
        if series.isna().any():
            raise SealError(f"{int(series.isna().sum())} NaT timestamp(s) — refusing to classify them as pre-seal")
        tz = getattr(series.dtype, "tz", None)
        if tz is not None:
            return series.dt.tz_convert(ET).dt.tz_localize(None)
        return series
    return series.map(_wallclock_et_one)


def _sealed_mask(df: pd.DataFrame, col: str) -> pd.Series:
    if col not in df.columns:
        raise SealError(f"column {col!r} not in DataFrame — cannot certify seal compliance")
    if len(df) == 0:
        return pd.Series(dtype=bool)
    return _wallclock_et(df[col]) > SEAL_CUTOFF_ET_WALLCLOCK


# --- public guards -----------------------------------------------------------------
def assert_presealed(df: pd.DataFrame, col: str, context: str) -> None:
    """Raise SealError if ANY value in df[col] falls on/after the seal.

    Empty df passes. An active authorized_read token bypasses the raise, but each
    bypass is announced: 'SEAL OVERRIDE: <token> <context>'. Returns None on success —
    there is nothing to silently ignore.
    """
    n_sealed = int(_sealed_mask(df, col).sum())
    if n_sealed == 0:
        return
    if _OVERRIDE_TOKEN is not None:
        print(f"SEAL OVERRIDE: {_OVERRIDE_TOKEN} {context} ({n_sealed} sealed row(s) passed under explicit token)")
        return
    raise SealError(
        f"SEAL VIOLATION [{context}]: {n_sealed} row(s) in column {col!r} fall on/after "
        f"{SEAL_DATE.isoformat()} (>= 2026-08-01 is VIRGIN — LOCKED_FORWARD.md). "
        f"Values withheld from this message by design. Use truncate_presealed() for a "
        f"mechanical cut, or authorized_read(<recorded token>) for a scheduled read."
    )


def truncate_presealed(df: pd.DataFrame, col: str, context: str) -> tuple[pd.DataFrame, int]:
    """Mechanically drop rows on/after the seal. Returns (df_kept, n_dropped).

    The dropped VALUES are never exposed: only the count is returned/logged, and the
    kept frame is a fresh copy so no view back onto sealed rows survives.
    """
    mask = _sealed_mask(df, col)
    n_dropped = int(mask.sum())
    kept = df.loc[~mask].copy() if len(df) else df.copy()
    print(f"seal_guard: truncated {n_dropped} post-seal row(s) [{context}] — kept {len(kept)}; dropped values not shown")
    return kept, n_dropped


# --- selftest ----------------------------------------------------------------------
def _selftest():
    """Positive tests: every guard is shown to FIRE (charter §8/J).

    All post-seal timestamps below are SYNTHETIC fixtures fabricated to exercise the
    guard — no market data value is read, printed or persisted.
    """
    import contextlib
    import io

    ok = 0
    ctx = "seal_guard._selftest"

    # 1. guard FIRES: naive datetime64 post-seal row raises
    df = pd.DataFrame({"ts": pd.to_datetime(["2026-07-30 09:31:00", "2026-08-02 09:31:00"])})
    try:
        assert_presealed(df, "ts", ctx); raise AssertionError("guard 1 silent")
    except SealError:
        ok += 1
    # 2. pre-seal naive datetimes pass, including the exact 17:00:00 boundary bar
    assert_presealed(pd.DataFrame({"ts": pd.to_datetime(["2026-07-31 17:00:00", "2026-07-31 09:31:00"])}), "ts", ctx); ok += 1
    # 3. guard FIRES: one second past the boundary close is sealed (halt hour is sealed)
    try:
        assert_presealed(pd.DataFrame({"ts": pd.to_datetime(["2026-07-31 17:00:01"])}), "ts", ctx); raise AssertionError("guard 3 silent")
    except SealError:
        ok += 1
    # 4. guard FIRES: 18:00 ET 2026-07-31 (open of sealed session 2026-08-01) is sealed
    try:
        assert_presealed(pd.DataFrame({"ts": pd.to_datetime(["2026-07-31 18:00:00"])}), "ts", ctx); raise AssertionError("guard 4 silent")
    except SealError:
        ok += 1
    # 5. tz-aware: 2026-07-31 20:00 UTC == 16:00 ET -> pre-seal (conversion matters)
    aware = pd.DataFrame({"ts": pd.to_datetime(["2026-07-31 20:00:00"]).tz_localize("UTC")})
    assert_presealed(aware, "ts", ctx); ok += 1
    # 6. guard FIRES: 2026-07-31 23:00 UTC == 19:00 ET -> sealed even though UTC date is 07-31
    aware_bad = pd.DataFrame({"ts": pd.to_datetime(["2026-07-31 23:00:00"]).tz_localize("UTC")})
    try:
        assert_presealed(aware_bad, "ts", ctx); raise AssertionError("guard 6 silent")
    except SealError:
        ok += 1
    # 7. ISO strings: pre-seal passes; guard FIRES on a post-seal string
    assert_presealed(pd.DataFrame({"ts": ["2026-07-31T16:59:00", "2026-07-31"]}), "ts", ctx); ok += 1
    try:
        assert_presealed(pd.DataFrame({"ts": ["2026-08-01T09:31:00"]}), "ts", ctx); raise AssertionError("guard 7 silent")
    except SealError:
        ok += 1
    # 8. date objects: 07-31 label passes; guard FIRES on the 08-01 label
    assert_presealed(pd.DataFrame({"d": [date(2026, 7, 31), date(2026, 6, 1)]}), "d", ctx); ok += 1
    try:
        assert_presealed(pd.DataFrame({"d": [date(2026, 8, 1)]}), "d", ctx); raise AssertionError("guard 8 silent")
    except SealError:
        ok += 1
    # 9. empty df passes
    assert_presealed(pd.DataFrame({"ts": pd.to_datetime([])}), "ts", ctx); ok += 1
    # 10. truncate drops EXACTLY the sealed rows, returns only the count
    mixed = pd.DataFrame({
        "ts": pd.to_datetime(["2026-07-30 12:00:00", "2026-08-01 09:31:00", "2026-07-31 17:00:00", "2026-08-15 10:00:00"]),
        "v": [1, 2, 3, 4],
    })
    kept, n_dropped = truncate_presealed(mixed, "ts", ctx)
    assert n_dropped == 2 and len(kept) == 2 and list(kept["v"]) == [1, 3]; ok += 1
    assert_presealed(kept, "ts", ctx); ok += 1  # the truncated frame is certified clean
    # 11. override: bypass works ONLY inside authorized_read and PRINTS loudly
    sealed_df = pd.DataFrame({"ts": pd.to_datetime(["2026-08-05 09:31:00"])})
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        with authorized_read("MONITOR-01-TESTTOKEN"):
            assert_presealed(sealed_df, "ts", "selftest-override")  # does NOT raise
    out = buf.getvalue()
    assert "SEAL OVERRIDE: MONITOR-01-TESTTOKEN selftest-override" in out, "override print missing"
    ok += 1
    # 12. guard FIRES again the moment the context exits (no leaked flag)
    try:
        assert_presealed(sealed_df, "ts", ctx); raise AssertionError("guard 12 silent")
    except SealError:
        ok += 1
    # 13. guard FIRES: blank override token refused
    try:
        with authorized_read("  "):
            pass
        raise AssertionError("guard 13 silent")
    except SealError:
        ok += 1
    # 14. guard FIRES: unparseable / untypable values fail closed
    try:
        assert_presealed(pd.DataFrame({"ts": ["not-a-date"]}), "ts", ctx); raise AssertionError("guard 14a silent")
    except SealError:
        ok += 1
    try:
        assert_presealed(pd.DataFrame({"ts": [12345]}), "ts", ctx); raise AssertionError("guard 14b silent")
    except SealError:
        ok += 1
    # 15. guard FIRES: NaT is never classified pre-seal
    try:
        assert_presealed(pd.DataFrame({"ts": pd.to_datetime(["2026-07-01", None])}), "ts", ctx); raise AssertionError("guard 15 silent")
    except SealError:
        ok += 1
    # 16. guard FIRES: missing column cannot be certified
    try:
        assert_presealed(pd.DataFrame({"x": [1]}), "ts", ctx); raise AssertionError("guard 16 silent")
    except SealError:
        ok += 1

    print(f"seal_guard selftest: {ok}/20 PASS (12 guards shown to fire)")


if __name__ == "__main__":
    _selftest()
