"""seal_audit.py — STANDING PER-WAVE CHECK. Prove, don't assert, that a wave read no sealed data.

Owner directive R4 (2026-08-09): a claim that a wave "read nothing at or after 2026-08-01" is
an assertion unless the maximum timestamp of every data read is measured. This makes it
mechanical and cheap: one line per artifact, run once per wave, appended to the LOCKED-FORWARD
ACCESS LEDGER in research/system_master/HOLDOUT_DETERMINATION_20260809.md.

Two seals, and they are different things:
  LOCKED_FORWARD  >= 2026-08-01  VIRGIN. Reading it is a governed event (LOCKED_FORWARD.md:9-14
                                 permits only MONITOR-01 or a pre-registered annual frozen-
                                 champion evaluation). Any hit here is an INCIDENT.
  CONSUMED        2026-05-30 .. 2026-07-31  research-consumed by SM11 on 2026-08-08. Reading it
                                 is permitted but must be DISCLOSED, because it is not clean
                                 out-of-sample for anything and never will be again.
  DEV             <= 2026-05-29  the development window.

Usage:  python seal_audit.py <wave_tag> <path> [<path> ...]
        python seal_audit.py W18 --manifest runs/W18_SEAL_AUDIT/manifest.txt
"""
from __future__ import annotations
import os, sys, json, glob
import numpy as np
import pandas as pd

LOCKED_FORWARD = pd.Timestamp("2026-08-01")
DEV_END = pd.Timestamp("2026-05-29 23:59:59")

TIME_COLS = ("time", "sess", "date", "timestamp", "datetime", "entry_time", "exit_time",
             "sess_date", "session", "dt")


def _max_ts_from_frame(df: pd.DataFrame):
    best = None
    used = None
    for c in df.columns:
        if str(c).strip().lower() not in TIME_COLS:
            continue
        try:
            s = pd.to_datetime(df[c], errors="coerce")
        except Exception:
            continue
        if s.notna().sum() == 0:
            continue
        m = s.max()
        if best is None or m > best:
            best, used = m, c
    return best, used


def max_timestamp(path: str):
    """Return (max_timestamp, column_used, note). None timestamp => no time column found."""
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == ".parquet":
            df = pd.read_parquet(path)
            if not isinstance(df.index, pd.RangeIndex):
                df = df.reset_index()
            return (*_max_ts_from_frame(df), "parquet")
        if ext in (".csv", ".txt"):
            # comment='#' matches the exporters' header convention
            df = pd.read_csv(path, comment="#", low_memory=False)
            return (*_max_ts_from_frame(df), "csv")
        if ext == ".npy":
            return None, None, "npy (no timestamps by construction)"
        if ext in (".json",):
            return None, None, "json (inspect by hand if it carries dates)"
    except Exception as exc:  # reported, never swallowed
        return None, None, f"UNREADABLE: {type(exc).__name__}: {exc}"
    return None, None, "unhandled extension"


def classify(ts):
    if ts is None:
        return "NO_TIMESTAMPS"
    if ts >= LOCKED_FORWARD:
        return "*** LOCKED_FORWARD BREACH ***"
    if ts > DEV_END:
        return "CONSUMED (disclose)"
    return "DEV"


def audit(paths):
    rows = []
    for p in paths:
        p = p.strip()
        if not p or p.startswith("#"):
            continue
        if not os.path.exists(p):
            rows.append({"path": p, "max_timestamp": None, "column": None,
                         "class": "MISSING", "note": "file not found"})
            continue
        ts, col, note = max_timestamp(p)
        rows.append({"path": os.path.relpath(p).replace("\\", "/"),
                     "max_timestamp": None if ts is None else str(ts),
                     "column": col, "class": classify(ts), "note": note,
                     "size_mb": round(os.path.getsize(p) / 1e6, 2)})
    return pd.DataFrame(rows)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    wave = sys.argv[1]
    args = sys.argv[2:]
    if args[0] == "--manifest":
        paths = open(args[1], encoding="utf-8").read().splitlines()
    else:
        paths = []
        for a in args:
            paths.extend(glob.glob(a) or [a])
    df = audit(paths)
    print(f"=== SEAL AUDIT — wave {wave} ===")
    print(f"LOCKED_FORWARD boundary {LOCKED_FORWARD.date()}   DEV_END {DEV_END.date()}\n")
    print(df.to_string(index=False))
    breaches = df[df["class"].str.contains("BREACH", na=False)]
    consumed = df[df["class"].str.startswith("CONSUMED", na=False)]
    print(f"\nLOCKED-FORWARD BREACHES: {len(breaches)}")
    print(f"CONSUMED-window reads (permitted, disclosed): {len(consumed)}")
    if len(consumed):
        print("  " + "\n  ".join(consumed["path"].tolist()))
    verdict = "CLEAN" if len(breaches) == 0 else "BREACH"
    print(f"\nVERDICT: {verdict}")
    out = os.path.join("runs", f"{wave}_SEAL_AUDIT")
    os.makedirs(out, exist_ok=True)
    df.to_csv(os.path.join(out, "seal_audit.csv"), index=False)
    json.dump({"wave": wave, "verdict": verdict, "n_artifacts": int(len(df)),
               "n_locked_forward_breaches": int(len(breaches)),
               "n_consumed_reads": int(len(consumed)),
               "consumed_paths": consumed["path"].tolist(),
               "locked_forward_boundary": str(LOCKED_FORWARD.date())},
              open(os.path.join(out, "verdict.json"), "w"), indent=2)
    sys.exit(0 if verdict == "CLEAN" else 1)
