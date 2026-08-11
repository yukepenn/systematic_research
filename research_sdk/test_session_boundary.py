"""test_session_boundary.py -- verifies research_sdk/session_boundary.py against
independently-verified reference UTC offsets, so the DST-offset error class that
produced the 2026-08-11 EQV04 near-miss cannot recur silently.

Run: python research_sdk/test_session_boundary.py

Reference offsets below were independently computed (datetime.utcoffset() against the
real America/New_York zoneinfo database, not re-derived from this module's own logic)
and cross-checked against the documented US DST rule (2nd Sunday of March -> 1st Sunday
of November): 2026 spring-forward = 2026-03-08, fall-back = 2026-11-01.
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from session_boundary import (  # noqa: E402
    BoundaryError,
    LOCKED_FORWARD_LAST_CONSUMED_SESSION,
    assert_not_locked_forward,
    authorized_backtest_window,
    session_close_boundary_utc,
    to_nt8_iso,
)

FAILURES = []


def check(name, cond, detail=""):
    ok = bool(cond)
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"  -- {detail}" if detail and not ok else ""))
    if not ok:
        FAILURES.append(name)
    return ok


def boundary_iso(d: date) -> str:
    return to_nt8_iso(session_close_boundary_utc(d))


print("== A. Ordinary dates, both DST seasons ==")
check("ordinary EST date (2026-01-15, mid-winter)",
      boundary_iso(date(2026, 1, 15)) == "2026-01-15T22:59:59Z",
      boundary_iso(date(2026, 1, 15)))
check("ordinary EDT date (2026-07-15, mid-summer)",
      boundary_iso(date(2026, 7, 15)) == "2026-07-15T21:59:59Z",
      boundary_iso(date(2026, 7, 15)))

print("== B. DST spring transition (2026-03-08, 2nd Sunday of March) ==")
check("day before spring-forward is still EST (2026-03-07)",
      boundary_iso(date(2026, 3, 7)) == "2026-03-07T22:59:59Z",
      boundary_iso(date(2026, 3, 7)))
check("spring-forward day itself is already EDT by 18:00 ET (2026-03-08)",
      boundary_iso(date(2026, 3, 8)) == "2026-03-08T21:59:59Z",
      boundary_iso(date(2026, 3, 8)))

print("== C. DST fall transition (2026-11-01, 1st Sunday of November) ==")
check("day before fall-back is still EDT (2026-10-31)",
      boundary_iso(date(2026, 10, 31)) == "2026-10-31T21:59:59Z",
      boundary_iso(date(2026, 10, 31)))
check("fall-back day itself is already EST by 18:00 ET (2026-11-01)",
      boundary_iso(date(2026, 11, 1)) == "2026-11-01T22:59:59Z",
      boundary_iso(date(2026, 11, 1)))

print("== D. LOCKED_FORWARD boundary date itself (2026-07-31, EDT) ==")
check("2026-07-31 boundary is 21:59:59Z -- matches EQV04's own re-derivation, catches "
      "the exact original DST-offset mistake (22:59:59Z would be wrong here)",
      boundary_iso(date(2026, 7, 31)) == "2026-07-31T21:59:59Z",
      boundary_iso(date(2026, 7, 31)))
check("constant LOCKED_FORWARD_LAST_CONSUMED_SESSION matches LOCKED_FORWARD.md",
      LOCKED_FORWARD_LAST_CONSUMED_SESSION == date(2026, 7, 31))

print("== E. Early-close session does not shift the boundary formula ==")
check("2025-11-28 (day after Thanksgiving, 13:00 ET early close) still anchors off "
      "18:00 ET, unaffected by the earlier same-day close",
      boundary_iso(date(2025, 11, 28)) == "2025-11-28T22:59:59Z",
      boundary_iso(date(2025, 11, 28)))

print("== F. Mechanical pre-execution assertion (must raise, not just warn) ==")
try:
    assert_not_locked_forward(date(2026, 8, 1))
    check("assert_not_locked_forward raises on first virgin session (2026-08-01)", False)
except BoundaryError:
    check("assert_not_locked_forward raises on first virgin session (2026-08-01)", True)

try:
    assert_not_locked_forward(date(2026, 7, 31))
    check("assert_not_locked_forward passes silently on the boundary date itself", True)
except BoundaryError:
    check("assert_not_locked_forward passes silently on the boundary date itself", False)

try:
    authorized_backtest_window(date(2026, 1, 1), date(2026, 8, 1))
    check("authorized_backtest_window raises before returning a window that reaches "
          "past LOCKED_FORWARD", False)
except BoundaryError:
    check("authorized_backtest_window raises before returning a window that reaches "
          "past LOCKED_FORWARD", True)

w = authorized_backtest_window(date(2026, 1, 1), date(2026, 5, 31))
check("authorized_backtest_window returns a usable window when fully in-bounds",
      w.to_utc_iso == "2026-05-31T21:59:59Z", w.to_utc_iso)

try:
    authorized_backtest_window(date(2026, 6, 1), date(2026, 1, 1))
    check("authorized_backtest_window rejects from > to", False)
except BoundaryError:
    check("authorized_backtest_window rejects from > to", True)

try:
    authorized_backtest_window(
        date(2026, 1, 1), date(2026, 3, 1),
        max_authorized_session_date_et=date(2026, 2, 1),
    )
    narrow_raised = False
except BoundaryError:
    narrow_raised = True
check("narrower max_authorized_session_date_et overrides the LOCKED_FORWARD default "
      "(e.g. a specific preregistered protected-pool batch's own session list)",
      narrow_raised)

print()
if FAILURES:
    print(f"{len(FAILURES)} FAILURE(S): {FAILURES}")
    sys.exit(1)
else:
    print("ALL PASS")
    sys.exit(0)
