"""
Canonical timezone-aware session-boundary utility for CME index-future data windows.

Fixes a real process failure class. On 2026-08-11 (EQV04_NT8_CANONICAL_PARITY), the NT8
Strategy Analyzer `to` cutoff for a smoke-test window was computed by hand-picking a
seasonal UTC offset (CLAUDE.md's own documented "22:59:59Z EST / 21:59:59Z EDT"
convention) and applying the EST-season value to a date that was actually in EDT season
-- a one-hour error. It was caught only by re-derivation from first principles during an
unrelated investigation, and it did no damage only because the erroneous hour fell inside
the CME Friday-17:00-to-Sunday-18:00 weekly gap (see runs/EQV04_NT8_CANONICAL_PARITY/
REPORT.md). That was luck of the calendar, not a safe process. This module removes the
seasonal-offset judgment call entirely: every boundary is computed by localizing a plain
ET wall-clock time via the IANA `America/New_York` tzdata rules through the stdlib
`zoneinfo` module, which resolves DST correctly by construction, and never by a remembered
manual rule. There is no seasonal branch anywhere in this file for a caller to get wrong.

Session convention (CLAUDE.md "Conventions that bite", src/analytics/runlib.py
`session_date`): a CME index-future session runs 18:00 ET -> 17:00 ET the next calendar
day. NT8 Strategy Analyzer's "To = D" means "last session ENDING <= D", which in absolute
time is one second before the *next* session opens -- i.e. one second before 18:00 ET on
calendar date D itself (session D+1's open), NOT "end of day D" and NOT D's own 17:00
close (early-close holidays close earlier than 17:00 but do not change when the *next*
session opens, so the boundary formula does not special-case them -- see
test_early_close_session_unaffected below).

18:00 ET is used as the anchor time deliberately: CME's DST transitions occur at 02:00
local time, so 18:00 ET is never inside a spring-forward gap or a fall-back fold on any
date -- there is exactly one unambiguous UTC instant for "18:00 ET" on every calendar day.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
UTC = ZoneInfo("UTC")

SESSION_OPEN_ET = time(18, 0, 0)

# LOCKED_FORWARD.md (declared 2026-08-07): everything through 2026-07-31 is
# research-consumed; 2026-08-01 onward is virgin, consumable only per that doc's own
# MONITOR-01 / annual-frozen-champion cadence. This constant must change ONLY alongside
# an update to research/operational/LOCKED_FORWARD.md itself (owner-directed door), never
# to make a specific run's window fit.
LOCKED_FORWARD_LAST_CONSUMED_SESSION = date(2026, 7, 31)


class BoundaryError(RuntimeError):
    """Raised when a requested data window would cross an authorized-window boundary.

    Raising (not returning a bool) is deliberate: a caller that forgets to check a
    return value still gets stopped. Call the assert_* functions BEFORE any data-read
    or backtest call -- catching this exception to "proceed anyway" defeats the point.
    """


def _localize_et(d: date, t: time = SESSION_OPEN_ET) -> datetime:
    return datetime.combine(d, t, tzinfo=ET)


def session_open_utc(session_date_et: date) -> datetime:
    """UTC instant at which the session labeled `session_date_et` OPENS.

    A session labeled D opens at 18:00 ET on the PRIOR calendar day and runs through
    17:00 ET on D itself (runlib.session_date's convention: timestamps with hour>=18
    roll forward to the next day's session label).
    """
    return _localize_et(session_date_et - timedelta(days=1)).astimezone(UTC)


def session_close_boundary_utc(last_included_session_date_et: date) -> datetime:
    """UTC instant one second before the NEXT session opens after
    `last_included_session_date_et` -- i.e. the correct NT8 Analyzer `to` value for
    "include every session through this date, inclusive, and nothing after."

    This is one second before 18:00 ET on `last_included_session_date_et` itself (that
    moment is when the following session opens), NOT that date's own 17:00 close.
    """
    next_open = _localize_et(last_included_session_date_et).astimezone(UTC)
    return next_open - timedelta(seconds=1)


def session_open_boundary_utc(first_included_session_date_et: date) -> datetime:
    """UTC instant the FIRST included session opens -- the correct NT8 Analyzer `from`
    value for "include this session and everything after."
    """
    return session_open_utc(first_included_session_date_et)


def to_nt8_iso(dt_utc: datetime) -> str:
    """Format a UTC datetime as the `...Z` ISO-8601 string NT8/CrossTrade tool calls
    expect (e.g. "2026-07-31T21:59:59Z")."""
    assert dt_utc.tzinfo is not None, "to_nt8_iso requires a timezone-aware datetime"
    dt_utc = dt_utc.astimezone(UTC)
    return dt_utc.strftime("%Y-%m-%dT%H:%M:%S") + "Z"


@dataclass(frozen=True)
class AuthorizedWindow:
    from_utc_iso: str
    to_utc_iso: str
    first_session: date
    last_session: date


def authorized_backtest_window(
    first_included_session_date_et: date,
    last_included_session_date_et: date,
    max_authorized_session_date_et: date = LOCKED_FORWARD_LAST_CONSUMED_SESSION,
    window_name: str = "LOCKED_FORWARD",
) -> AuthorizedWindow:
    """Compute a ready-to-use (`from`, `to`) NT8 Analyzer window AND mechanically assert
    it does not reach past an authorized boundary, in one call. Raises BoundaryError
    (does not return) if the requested window would cross the boundary -- this must be
    called, and allowed to raise uncaught, BEFORE any RunStrategyBacktest / GetBars /
    data-read call that could otherwise touch protected or locked-forward data.

    `max_authorized_session_date_et` defaults to LOCKED_FORWARD_LAST_CONSUMED_SESSION;
    pass a different (always more conservative, never more permissive without owner
    sign-off) boundary for a narrower authorization, e.g. a specific preregistered
    protected-pool batch's own session list.
    """
    if last_included_session_date_et > max_authorized_session_date_et:
        raise BoundaryError(
            f"{window_name} boundary violation: requested last session "
            f"{last_included_session_date_et.isoformat()} is after the authorized "
            f"boundary {max_authorized_session_date_et.isoformat()}. Refusing to "
            f"compute a backtest window that would read protected/locked-forward data. "
            f"This assertion ran BEFORE any data was read."
        )
    if first_included_session_date_et > last_included_session_date_et:
        raise BoundaryError(
            f"invalid window: first session {first_included_session_date_et.isoformat()} "
            f"is after last session {last_included_session_date_et.isoformat()}"
        )
    return AuthorizedWindow(
        from_utc_iso=to_nt8_iso(session_open_boundary_utc(first_included_session_date_et)),
        to_utc_iso=to_nt8_iso(session_close_boundary_utc(last_included_session_date_et)),
        first_session=first_included_session_date_et,
        last_session=last_included_session_date_et,
    )


def assert_not_locked_forward(
    last_included_session_date_et: date,
    max_authorized_session_date_et: date = LOCKED_FORWARD_LAST_CONSUMED_SESSION,
) -> None:
    """Standalone assertion form for call sites that already have their own `from`/`to`
    and just need the mechanical LOCKED_FORWARD check. Raises BoundaryError; returns
    None (no value) on success -- there is nothing to silently ignore."""
    if last_included_session_date_et > max_authorized_session_date_et:
        raise BoundaryError(
            f"LOCKED_FORWARD boundary violation: session "
            f"{last_included_session_date_et.isoformat()} is after "
            f"{max_authorized_session_date_et.isoformat()} (research/operational/"
            f"LOCKED_FORWARD.md). Refusing before any data was read."
        )
