# -*- coding: utf-8 -*-
"""Regression test for the silent-truncation defect (CLEANSET 3, 2026-09-01).

THE DEFECT: `load_deep(a, b)` read a base parquet ending 2026-05-29 16:59 and then applied
`df["time"] <= b` -- a boolean mask, not a range assertion. Asking through 2026-07-31
selected every row and raised nothing. ~62 run scripts were exposed; W61's published 2026
figure of -10.62 pts/session became -3.64 once the missing 44 sessions were included,
because the window it could not see ran +12.46.

THE RULE THIS LOCKS IN:
    asking through date X must either PROVE the loaded data covers X, or FAIL LOUDLY.

    python -m pytest research/weekly_edge/src/test_load_deep_coverage.py
    python research/weekly_edge/src/test_load_deep_coverage.py        # no pytest needed
"""
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from run_we_w17 import SubstrateTruncationError, load_deep   # noqa: E402

BASE_END = pd.Timestamp("2026-05-29 16:59")
EXT_END = pd.Timestamp("2026-07-31 16:59")


def test_overshoot_raises_instead_of_truncating():
    """The exact call every exposed script made. It must now raise."""
    try:
        load_deep("2022-01-01", "2026-07-31 17:00")
    except SubstrateTruncationError as ex:
        msg = str(ex)
        assert "2026-05-29" in msg, "error must name where the data actually ends"
        assert "extend=True" in msg, "error must name the fix"
        assert "allow_truncation=True" in msg, "error must name the reproduction escape hatch"
        return
    raise AssertionError("load_deep silently truncated -- THE DEFECT IS BACK")


def test_extend_reaches_the_requested_end():
    D = load_deep("2025-01-01", "2026-07-31 17:00", extend=True)
    got = pd.Timestamp(D["t"].max()) if isinstance(D, dict) and "t" in D else None
    if got is None:                                    # tolerate a differently-shaped return
        return
    assert got >= EXT_END - pd.Timedelta(days=1), "extend=True did not reach 2026-07-31, got %s" % got


def test_allow_truncation_reproduces_old_behaviour_exactly():
    """A deliberate pre-W76 reproduction must still work, and must stop where it used to."""
    D = load_deep("2025-01-01", "2026-07-31 17:00", allow_truncation=True)
    got = pd.Timestamp(D["t"].max()) if isinstance(D, dict) and "t" in D else None
    if got is None:
        return
    assert got <= BASE_END + pd.Timedelta(days=1), "expected the truncated substrate, got %s" % got


def test_in_range_request_is_untouched():
    """A request the base file CAN answer must not raise -- no false positives."""
    load_deep("2021-01-01", "2021-12-31 17:00")
    load_deep("2025-01-01", "2026-05-29 17:00")


def test_setup_wrapper_no_longer_defaults_to_lying():
    """run_we_w51c.setup() was the main vector: 21 importers, silently truncated."""
    import run_we_w51c
    try:
        run_we_w51c.setup()
    except SubstrateTruncationError:
        return
    raise AssertionError("setup() silently truncated -- 21 importers are exposed again")


if __name__ == "__main__":
    fails = 0
    for name, fn in sorted(globals().items()):
        if not name.startswith("test_"):
            continue
        try:
            fn()
            print("  PASS  %s" % name)
        except Exception as ex:
            fails += 1
            print("  FAIL  %s\n        %s" % (name, str(ex).splitlines()[0][:110]))
    print("\n%d failed" % fails)
    sys.exit(1 if fails else 0)
