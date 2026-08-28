"""SESSION-UNIT REGRESSION TEST.  The 23-hour NQ TRADING SESSION is the scientific unit here.

WHY THIS FILE EXISTS -- a real defect, on this programme's own headline quantity.  Program B's first
density measurement counted "active sessions" with `session_date.nunique()` and got 712.  The
correct unit, `session_id`, gives 638.  NQ trades 18:00 -> 17:00 ET, so ONE TRADING SESSION SPANS
TWO CALENDAR DATES; grouping by date splits every overnight session in two and silently understates
per-session density by ~12 %.  The same slip inflated trades/session by ~13 % via a second route
(a warm-up-inclusive numerator over an in-window denominator).

The tests below are STRUCTURAL and do not depend on any one artifact staying on disk: each builds a
synthetic session panel with a known answer and asserts the checker catches the error.  Two of them
additionally run against the real ledger IF it is present, and SKIP rather than fail if it is not,
so the guard survives repo reorganisation.
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.path.join(REPO, "runs", "RR_W001_ACTION_VALUE_LEDGER", "out", "ledger_p1pct.csv")
BOOK = os.path.join(REPO, "runs", "WE_W119_BOOKLOSS", "out", "book_loss_ledger.csv")


class SessionUnitError(AssertionError):
    pass


# ---------------------------------------------------------------- the guard itself
def assert_session_unit(df: pd.DataFrame, *, session_col: str = "session_id",
                        date_col: str = "session_date", label: str = "frame") -> dict:
    """Refuse a frame whose session column is really a calendar-date column.

    An NQ trading session opens 18:00 ET and closes 17:00 ET the next calendar day, so a genuine
    session key must be able to map ONE session onto TWO dates.  If every session maps to exactly
    one date AND the counts are equal, the 'session' column is a date in disguise.
    """
    if session_col not in df.columns:
        raise SessionUnitError(f"{label}: no '{session_col}' column -- refusing to count sessions "
                               f"by date. The unit of this programme is the trading session.")
    n_sess = int(df[session_col].nunique())
    out = {"label": label, "sessions": n_sess}
    if date_col in df.columns:
        n_date = int(df[date_col].nunique())
        out["dates"] = n_date
        out["spanning"] = int((df.groupby(session_col)[date_col].nunique() > 1).sum())
        if n_date == n_sess and out["spanning"] == 0 and n_sess > 50:
            raise SessionUnitError(
                f"{label}: sessions ({n_sess}) == dates ({n_date}) and NO session spans two dates. "
                f"For a 18:00->17:00 ET instrument that is impossible over {n_sess} sessions -- "
                f"'{session_col}' is a calendar date in disguise.")
    return out


def per_session_rate(df: pd.DataFrame, *, session_col="session_id", total_sessions=None,
                     label="frame") -> dict:
    """Rate per session, with the denominator stated. Refuses a mismatched population."""
    assert_session_unit(df, session_col=session_col, label=label)
    active = int(df[session_col].nunique())
    d = {"rows": len(df), "active_sessions": active,
         "per_active_session": len(df) / active if active else float("nan")}
    if total_sessions is not None:
        if active > total_sessions:
            raise SessionUnitError(
                f"{label}: {active} active sessions exceeds the stated population of "
                f"{total_sessions}. The numerator and denominator come from different populations "
                f"-- this is exactly the 2,401-over-1,058 defect.")
        d["total_sessions"] = total_sessions
        d["flat_sessions"] = total_sessions - active
        d["flat_share"] = (total_sessions - active) / total_sessions
        d["per_calendar_session"] = len(df) / total_sessions
    return d


# ---------------------------------------------------------------- tests
def _synthetic(n_sessions=200, overnight=True, seed=3):
    """Sessions opening 18:00 ET.  When overnight=True every session is GUARANTEED to carry at
    least one trade after midnight, so it provably spans two calendar dates."""
    rng = np.random.default_rng(seed)
    rows = []
    for s in range(n_sessions):
        open_ts = pd.Timestamp("2024-01-02 18:00") + pd.Timedelta(days=s)
        offs = [int(rng.integers(0, 300)) for _ in range(int(rng.integers(1, 5)))]
        if overnight:
            offs.append(int(rng.integers(400, 1300)))    # forced post-midnight trade
        for off in offs:
            ts = open_ts + pd.Timedelta(minutes=off)
            rows.append(dict(session_id=s, session_date=ts.normalize(), ts=ts))
    return pd.DataFrame(rows)


def test_guard_catches_date_masquerading_as_session():
    """A frame whose 'session_id' is really a date must be REFUSED. A guard that cannot fire is
    worthless, so this asserts the failure rather than the success."""
    d = _synthetic(overnight=False)
    d = d.assign(session_id=d["session_date"])       # the defect, injected deliberately
    try:
        assert_session_unit(d, label="date-as-session")
    except SessionUnitError as e:
        assert "disguise" in str(e)
        return True
    raise AssertionError("GUARD DID NOT FIRE -- it has no teeth")


def test_guard_accepts_a_real_session_panel():
    d = _synthetic(overnight=True)
    r = assert_session_unit(d, label="synthetic overnight")
    assert r["sessions"] == 200, r
    assert r["spanning"] > 0, "synthetic panel should have sessions spanning two dates"
    return True


def test_date_grouping_understates_density():
    """The concrete arithmetic of the real defect.

    ⚠ The invariant is NOT `dates > sessions` in general -- the real book ledger has 1,058 sessions
    against only 1,056 dates, i.e. FEWER dates, because holidays and weekends let one calendar date
    host parts of two sessions.  The invariant that actually holds, and the one that caused the
    defect, is: when sessions span two dates, grouping a TRADE panel by date produces MORE groups
    than there are sessions, and therefore a SMALLER trades-per-group figure.  That is exactly what
    turned 3.340 into 2.993 on the real ledger (638 sessions vs 712 dates)."""
    d = _synthetic(overnight=True)
    n_sess, n_date = d["session_id"].nunique(), d["session_date"].nunique()
    spanning = int((d.groupby("session_id")["session_date"].nunique() > 1).sum())
    assert spanning == n_sess, f"every synthetic session should span 2 dates, got {spanning}"
    by_sess, by_date = len(d) / n_sess, len(d) / n_date
    assert n_date > n_sess, f"a trade panel of spanning sessions must touch more dates ({n_date}) than sessions ({n_sess})"
    assert by_date < by_sess, "date grouping must understate per-session density"
    return dict(sessions=n_sess, dates=n_date,
                by_session=round(by_sess, 3), by_date=round(by_date, 3))


def test_population_mismatch_is_refused():
    """The 2,401-over-1,058 defect: a numerator from a wider population than the denominator."""
    d = _synthetic(n_sessions=300, overnight=True)
    try:
        per_session_rate(d, total_sessions=200, label="warm-up-inclusive numerator")
    except SessionUnitError as e:
        assert "different populations" in str(e)
        return True
    raise AssertionError("GUARD DID NOT FIRE on a population mismatch")


def test_real_ledger_if_present():
    if not os.path.exists(LEDGER):
        return "SKIP (ledger absent)"
    d = pd.read_csv(LEDGER)
    w = d[d["in_window_session"] == True]                                    # noqa: E712
    r = per_session_rate(w, total_sessions=1058, label="P1/PCT in-window")
    assert r["active_sessions"] == 638, r
    assert r["flat_sessions"] == 420, r
    assert abs(r["per_active_session"] - 3.340) < 0.002, r
    assert abs(r["per_calendar_session"] - 2.014) < 0.002, r
    assert w["session_date"].nunique() == 712, "the WRONG unit should still give 712"
    return r


def test_real_book_ledger_if_present():
    """The independent confirmation: 1,058 sessions against only 1,056 dates."""
    if not os.path.exists(BOOK):
        return "SKIP (book ledger absent)"
    b = pd.read_csv(BOOK)
    ns, nd = b["session"].nunique(), b["date"].nunique()
    assert ns == 1058 and nd == 1056, (ns, nd)
    return dict(sessions=ns, dates=nd,
                note="sessions > dates proves the session is not a calendar date")


TESTS = [test_guard_catches_date_masquerading_as_session,
         test_guard_accepts_a_real_session_panel,
         test_date_grouping_understates_density,
         test_population_mismatch_is_refused,
         test_real_ledger_if_present,
         test_real_book_ledger_if_present]


def main() -> int:
    print("  SESSION-UNIT REGRESSION TEST")
    bad = 0
    for t in TESTS:
        try:
            r = t()
            print(f"    [PASS] {t.__name__:<46} {r if r is not True else ''}")
        except Exception as e:                                               # noqa: BLE001
            bad += 1
            print(f"    [*** FAIL ***] {t.__name__:<40} {e}")
    print(f"  {'ALL PASS' if not bad else f'{bad} FAILURE(S)'}  ({len(TESTS)-bad}/{len(TESTS)})")
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(main())
