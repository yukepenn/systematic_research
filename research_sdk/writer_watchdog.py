# -*- coding: utf-8 -*-
"""writer_watchdog -- prove that every live strategy's evidence writer is actually alive.

WHY THIS EXISTS
---------------
On 2026-09-01 the live real-money P1 leg (`WeeklyEdgeP1PCTMnq_v1` / `399562885`) ran for
4h24m writing NOTHING to its decision ledger while `ListAllStrategies` reported
`state: Realtime, isEnabled: true` and every warm-up gate reported PASS.  The export
handle had been lost to a same-file collision at startup and nulled by a SILENT catch
(`WeeklyEdgeP1PCTMnq_v1.cs:992`), which has no retry path.  Nothing in the system could
report it.  See `research/operational/OWNER_ACTION_20260901_P1_LEDGER_DEAD.md`.

WHAT IT CHECKS
--------------
The only trustworthy liveness signal is the **last data row inside the file**.

It is NOT file length and NOT LastWriteTime.  `WeeklyEdgeP1PCTMnq_v1.cs:1010-1021` records,
in the production source, that an earlier diagnosis from file length was WRONG: StreamWriter
spills to the OS long before the metadata updates.  This module therefore parses the final
line and compares its embedded bar timestamp against the wall clock.

It is also NOT a comparison against a sibling file: on 2026-09-01 three of four writers were
healthy, and a naive "are they all equal" check would have passed if the dead one had been
the only leg running.

STRICTLY READ-ONLY
------------------
Opens files for reading only.  Never writes to the log tree, never touches NinjaTrader,
never places/cancels/enables/disables anything.  Safe to run against a live book.

USAGE
-----
    python -m research_sdk.writer_watchdog                 # check the registered books
    python -m research_sdk.writer_watchdog --json          # machine-readable
    python -m research_sdk.writer_watchdog --max-stale 5   # tighter tolerance, minutes

EXIT CODES
----------
    0  all registered writers ALIVE (or legitimately IDLE outside session hours)
    1  at least one writer STALE or MISSING   <- this is the alarm
    2  configuration/usage error
"""
from __future__ import annotations

import argparse
import datetime as _dt
import io
import json
import os
import sys

# ---------------------------------------------------------------------------------------
# The registry.  One entry per (book, leg).  `dir` is the ExportDir the strategy was
# deployed with -- read it off `ListAllStrategies`, never guess it.
#
# NOTE the directory names are a known naming accident, kept because renaming them would
# require restarting a live strategy:  the LIVE MNQ book writes to `\mnq\`, and `\live_mnq\`
# is empty.  See CURRENT_LIVE_TRUTH.md's log-directory map.
# ---------------------------------------------------------------------------------------
REGISTRY = [
    # book        leg    account        class                        file
    ("LIVE-MNQ",  "P1",  "2047681",     "WeeklyEdgeP1PCTMnq_v1",
     r"C:\NT8_ForwardLogs\mnq\export\we_p1pct_p1pct.csv"),
    ("LIVE-MNQ",  "XM",  "2047681",     "WeeklyEdgeXMConflictMnq_v1",
     r"C:\NT8_ForwardLogs\mnq\export\we_xm_xm2.csv"),
    ("PAPER-NQ",  "P1",  "DEMO8383477", "WeeklyEdgeP1PCT_v3",
     r"C:\NT8_ForwardLogs\export\we_p1pct_p1pct.csv"),
    ("PAPER-NQ",  "XM",  "DEMO8383477", "WeeklyEdgeXMConflict_v4",
     r"C:\NT8_ForwardLogs\export\we_xm_xm2.csv"),
]

# Both export schemas put the bar timestamp in column 0, formatted `yyyy-MM-dd HH:mm:ss`
# in EXCHANGE SESSION TIME (ET).  P1 calls it `pyts`, XM calls it `timestamp`.
TS_COL = 0
TS_FMT = "%Y-%m-%d %H:%M:%S"

DEFAULT_MAX_STALE_MIN = 10.0


def _tail_line(path, probe=65536):
    """Return the last non-empty line without reading the whole (30-50 MB) file."""
    size = os.path.getsize(path)
    if size == 0:
        return None
    with io.open(path, "rb") as fh:
        step = min(probe, size)
        fh.seek(size - step)
        chunk = fh.read(step)
    lines = [ln for ln in chunk.split(b"\n") if ln.strip()]
    if not lines:
        return None
    return lines[-1].decode("utf-8", "replace").strip()


def _session_is_open(now_et):
    """CME equity-index ETH: 18:00 ET -> 17:00 ET next day, closed Fri 17:00 -> Sun 18:00.

    A writer that is silent because the market is shut is IDLE, not STALE.  Deliberately
    conservative: the daily 17:00-18:00 maintenance break is treated as closed, and any
    ambiguity resolves toward 'open' so a real outage is never excused as a weekend.
    """
    wd, hh = now_et.weekday(), now_et.hour            # Mon=0 .. Sun=6
    if wd == 5:                                        # Saturday
        return False
    if wd == 6:                                        # Sunday: opens 18:00
        return hh >= 18
    if wd == 4 and hh >= 17:                           # Friday after the close
        return False
    return not (hh == 17)                              # daily maintenance hour


def check(entries=None, max_stale_min=DEFAULT_MAX_STALE_MIN, now=None):
    """Return (rows, worst_status). Pure; performs no writes."""
    entries = REGISTRY if entries is None else entries
    now = now or _dt.datetime.now()
    open_now = _session_is_open(now)
    rows = []

    for book, leg, account, cls, path in entries:
        row = {"book": book, "leg": leg, "account": account, "class": cls, "file": path,
               "last_row": None, "age_min": None, "status": None, "detail": ""}

        if not os.path.exists(path):
            row["status"] = "MISSING"
            row["detail"] = "file does not exist"
            rows.append(row)
            continue

        line = _tail_line(path)
        if not line:
            row["status"] = "MISSING"
            row["detail"] = "file is empty"
            rows.append(row)
            continue

        field = line.split(",")[TS_COL]
        try:
            ts = _dt.datetime.strptime(field, TS_FMT)
        except ValueError:
            row["status"] = "MISSING"
            row["detail"] = "unparseable last row: %r" % field[:40]
            rows.append(row)
            continue

        age = (now - ts).total_seconds() / 60.0
        row["last_row"] = ts.strftime(TS_FMT)
        row["age_min"] = round(age, 1)

        if age <= max_stale_min:
            row["status"] = "ALIVE"
        elif not open_now:
            row["status"] = "IDLE"
            row["detail"] = "session closed; staleness not diagnostic"
        else:
            row["status"] = "STALE"
            row["detail"] = ("no row for %.0f min while the session is open -- the writer is "
                             "probably null (silent catch, no retry)" % age)
        rows.append(row)

    order = {"MISSING": 3, "STALE": 3, "IDLE": 1, "ALIVE": 0}
    worst = max((order[r["status"]] for r in rows), default=0)
    return rows, worst


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--max-stale", type=float, default=DEFAULT_MAX_STALE_MIN,
                    help="minutes before an open-session writer is STALE (default %(default)s)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    a = ap.parse_args(argv)

    now = _dt.datetime.now()
    rows, worst = check(max_stale_min=a.max_stale, now=now)

    if a.json:
        print(json.dumps({"checked_at": now.strftime(TS_FMT),
                          "session_open": _session_is_open(now),
                          "max_stale_min": a.max_stale,
                          "rows": rows}, indent=2))
    else:
        print("=" * 92)
        print("WRITER WATCHDOG  %s ET   session_open=%s   max_stale=%.0fmin"
              % (now.strftime(TS_FMT), _session_is_open(now), a.max_stale))
        print("=" * 92)
        print("%-10s %-4s %-13s %-21s %8s  %s" %
              ("BOOK", "LEG", "ACCOUNT", "LAST ROW", "AGE_MIN", "STATUS"))
        for r in rows:
            print("%-10s %-4s %-13s %-21s %8s  %s%s" %
                  (r["book"], r["leg"], r["account"], r["last_row"] or "-",
                   "-" if r["age_min"] is None else r["age_min"], r["status"],
                   ("  <- " + r["detail"]) if r["detail"] else ""))
        print("=" * 92)
        print("VERDICT: " + ("ALL WRITERS ACCOUNTED FOR" if worst == 0 else
                             "IDLE (session closed)" if worst == 1 else
                             "*** ALARM: a live evidence writer is not writing ***"))

    return 0 if worst <= 1 else 1


if __name__ == "__main__":
    sys.exit(main())
