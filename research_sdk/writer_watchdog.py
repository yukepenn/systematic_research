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

try:
    from zoneinfo import ZoneInfo
    ET = ZoneInfo("America/New_York")
except Exception:                                      # pragma: no cover
    ET = None


def now_et():
    """Wall clock IN EXCHANGE TIME, explicitly.

    ⚠️ v1 of this module used a NAIVE `datetime.now()` and compared it against ET bar
    stamps while printing the result labelled "ET". It worked only because this box
    happens to run Eastern time. On any other machine -- or if the TZ ever changes --
    every age would be silently wrong by the offset and a DEAD WRITER WOULD READ ALIVE,
    which is the one thing this module exists to prevent. Caught by an adversarial review
    on 2026-09-01. Same defect class as the DST string-vs-instant bug the shadow ledger's
    preflight found before its first row.
    """
    if ET is None:
        return _dt.datetime.now()                      # last resort; documented, not silent
    return _dt.datetime.now(_dt.timezone.utc).astimezone(ET).replace(tzinfo=None)

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


def _session_is_open(t_et):
    """CME equity-index ETH: 18:00 ET -> 17:00 ET next day, closed Fri 17:00 -> Sun 18:00.

    A writer that is silent because the market is shut is IDLE, not STALE.  Deliberately
    conservative: the daily 17:00-18:00 maintenance break is treated as closed, and any
    ambiguity resolves toward 'open' so a real outage is never excused as a weekend.
    """
    wd, hh = t_et.weekday(), t_et.hour            # Mon=0 .. Sun=6
    if wd == 5:                                        # Saturday
        return False
    if wd == 6:                                        # Sunday: opens 18:00
        return hh >= 18
    if wd == 4 and hh >= 17:                           # Friday after the close
        return False
    return not (hh == 17)                              # daily maintenance hour


# =========================================================================================
# [F-A2] HALT SCANNER. A latched leg has NO machine-readable surface anywhere.
#
# HdEnvRows() -- the only structured self-report, feeding the warm-up certificate and the
# TEMPLATE log line -- does not emit haltEntries, haltReason, warmupBlocked or mxExecBlocked.
# A halt latched AFTER start (RECONCILE-BREAK, PARTIAL-FILL, a reject, the XLsess shadow leak)
# surfaces ONLY as a one-off LogErr in NinjaTrader's own log. Meanwhile ListAllStrategies
# still reports Realtime/enabled/flat, and this watchdog's writer check still reports ALIVE,
# because the export keeps writing -- only ENTRIES stop.
#
# At 1.68 entries/session a latched leg is indistinguishable from a quiet week until someone
# greps. This makes the grep automatic. Read-only: it opens NT8's log file for reading.
# =========================================================================================
HALT_PATTERNS = [
    "RECONCILE-BREAK", "PARTIAL-FILL", "ZERO-FILL", "NON-TERMINAL",
    "ENTRIES LATCHED", "HALT", "ROLL-BLOCK", "MX-EXEC-BLOCKED",
    "DEAD-SERIES", "ROLL-RESOLVE-FAILED", "SESSIONEND-STALE", "config_fault",
]

# `config_fault` appears on EVERY healthy TEMPLATE line as `config_fault,none`, and a bare
# substring match on it flagged 11 perfectly healthy startup lines on the first run. An alarm
# that cries wolf is worse than no alarm -- it is how the export outage went unnoticed for
# five hours. Suppress the benign form explicitly rather than dropping the pattern, because
# a REAL config fault is exactly what this must catch.
BENIGN = ["config_fault,none"]


def _is_benign(line):
    return any(b in line for b in BENIGN)
NT8_LOG_DIR = os.path.join(os.path.expanduser("~"), "Documents", "NinjaTrader 8", "log")


def scan_halts(log_dir=NT8_LOG_DIR, days=2):
    """Return NT8 log lines matching any halt/latch pattern, newest file first."""
    hits = []
    if not os.path.isdir(log_dir):
        return [{"file": log_dir, "line": "LOG DIRECTORY NOT FOUND", "pattern": "SETUP"}]
    files = sorted((f for f in os.listdir(log_dir)
                    if f.startswith("log.") and f.endswith(".txt") and ".en." not in f),
                   reverse=True)[:days]
    for fn in files:
        p = os.path.join(log_dir, fn)
        try:
            with io.open(p, encoding="utf-8", errors="replace") as fh:
                for ln in fh:
                    if _is_benign(ln):
                        continue
                    for pat in HALT_PATTERNS:
                        if pat in ln:
                            hits.append({"file": fn, "pattern": pat, "line": ln.strip()[:220]})
                            break
        except Exception as ex:                                   # pragma: no cover
            hits.append({"file": fn, "pattern": "READ-ERROR", "line": str(ex)})
    return hits


def check(entries=None, max_stale_min=DEFAULT_MAX_STALE_MIN, now=None):
    """Return (rows, worst_status). Pure; performs no writes."""
    entries = REGISTRY if entries is None else entries
    now = now or now_et()
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
    ap.add_argument("--halts", action="store_true",
                    help="also scan the NT8 log for halts/latches (see HALT_PATTERNS)")
    a = ap.parse_args(argv)

    now = now_et()
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

    halt_hits = []
    if a.halts:
        halt_hits = scan_halts()
        if not a.json:
            print()
            print("HALT SCAN of the NT8 log -- the ONLY channel a latched leg appears on")
            if not halt_hits:
                print("  no halt/latch line found. Entries are not blocked by a latch.")
            else:
                for h in halt_hits[:40]:
                    print("  [%-18s] %s" % (h["pattern"], h["line"]))
                print("  *** %d halt/latch line(s). A LATCHED LEG STILL REPORTS Realtime/enabled/flat"
                      " AND ITS WRITER STILL READS ALIVE. ***" % len(halt_hits))

    return 0 if (worst <= 1 and not halt_hits) else 1


if __name__ == "__main__":
    sys.exit(main())
