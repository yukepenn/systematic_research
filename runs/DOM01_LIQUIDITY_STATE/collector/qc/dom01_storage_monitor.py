"""
dom01_storage_monitor.py -- DOM01 disk-capacity / storage-growth monitor.

ENGINEERING ONLY, same scope discipline as dom01_qc_monitor.py: file sizes, growth
rates, disk free space, and row-count-vs-cap tracking only. This module computes and
reports NONE of: prices, returns, PnL, or anything derived from what the DOM data
actually says about the market -- it only measures how many bytes/rows the collector
has written and how fast. "Predictive" here means capacity planning (bytes/hour ->
days until disk fills), never market prediction.

Row counts are read from `_heartbeat.csv`'s own last row (`DepthRowsWritten`,
`TopOfBookRowsWritten`), NOT by scanning `_depth.csv` itself -- the heartbeat stream
already carries these counters at negligible file size, and reading `_depth.csv`
directly on every capacity check would mean fully scanning a multi-hundred-MB, always-
growing file just to count rows. This also matters because the collector's own
manifest.json is written ONCE at State.DataLoaded and not rewritten until
State.Terminated (confirmed by reading Dom01DepthRecorder_v1.cs -- WriteManifest(false)
at init, WriteManifest(true) only at FinalizeRun) -- so `CapReached` in the manifest is
always stale for an in-progress run. The heartbeat counters are the only live-updated
signal available without scanning the big file, so this module treats them as
authoritative for in-progress cap tracking.

Usage:
    python runs/DOM01_LIQUIDITY_STATE/collector/qc/dom01_storage_monitor.py \
        [--out-dir runs/DOM01_LIQUIDITY_STATE/collector/out] \
        [--warn-days 30] [--fail-days 7] [--warn-free-gib 50] [--fail-free-gib 15] \
        [--cap-warn-pct 80]

Exit 0 = no FAIL-level condition. Exit 1 = at least one FAIL (see printed detail).
"""
from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_MAX_ROWS_PER_STREAM = 20_000_000  # Dom01DepthRecorder_v1.cs SetDefaults default


def _parse_utc(s: str) -> datetime:
    s = s.strip().rstrip("Z")
    return datetime.fromisoformat(s).replace(tzinfo=timezone.utc)


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _fmt_bytes(n: float) -> str:
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if abs(n) < 1024.0:
            return f"{n:,.1f} {unit}"
        n /= 1024.0
    return f"{n:,.1f} PiB"


@dataclass
class RunStorage:
    prefix: str
    run_id: str
    start_utc: datetime
    end_utc: datetime | None
    terminated: bool
    file_sizes: dict  # stream -> bytes
    total_bytes: int
    depth_rows_written: int | None
    tob_rows_written: int | None
    max_rows_per_stream: int


def discover_run_storage(out_dir: Path) -> list[RunStorage]:
    runs = []
    for manifest_path in sorted(out_dir.glob("*_manifest.json")):
        prefix = manifest_path.name[: -len("_manifest.json")]
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:
            continue

        file_sizes = {}
        for stream in ("depth", "topofbook", "events", "heartbeat"):
            p = out_dir / f"{prefix}_{stream}.csv"
            file_sizes[stream] = p.stat().st_size if p.exists() else 0
        file_sizes["manifest"] = manifest_path.stat().st_size
        total = sum(file_sizes.values())

        depth_rows = tob_rows = None
        hb_path = out_dir / f"{prefix}_heartbeat.csv"
        if hb_path.exists() and hb_path.stat().st_size > 0:
            last_row = None
            with open(hb_path, "r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    last_row = row
            if last_row:
                try:
                    depth_rows = int(last_row["DepthRowsWritten"])
                    tob_rows = int(last_row["TopOfBookRowsWritten"])
                except (KeyError, ValueError):
                    pass

        runs.append(RunStorage(
            prefix=prefix,
            run_id=manifest.get("RunId", prefix),
            start_utc=_parse_utc(manifest["StartUtc"]),
            end_utc=_parse_utc(manifest["EndUtc"]) if manifest.get("EndUtc") else None,
            terminated=manifest.get("EndUtc") is not None,
            file_sizes=file_sizes,
            total_bytes=total,
            depth_rows_written=depth_rows,
            tob_rows_written=tob_rows,
            max_rows_per_stream=manifest.get("MaxRowsPerStreamFile", DEFAULT_MAX_ROWS_PER_STREAM),
        ))
    return runs


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out-dir", default="runs/DOM01_LIQUIDITY_STATE/collector/out")
    ap.add_argument("--warn-days", type=float, default=30.0,
                     help="WARN if projected days-until-disk-full (at current combined growth rate) drops below this")
    ap.add_argument("--fail-days", type=float, default=7.0,
                     help="FAIL if projected days-until-disk-full drops below this")
    ap.add_argument("--warn-free-gib", type=float, default=50.0,
                     help="WARN if absolute free space drops below this many GiB, regardless of rate")
    ap.add_argument("--fail-free-gib", type=float, default=15.0,
                     help="FAIL if absolute free space drops below this many GiB, regardless of rate")
    ap.add_argument("--cap-warn-pct", type=float, default=80.0,
                     help="WARN when a stream's row count reaches this percent of MaxRowsPerStreamFile")
    ap.add_argument("--session-hours", type=float, default=23.0,
                     help="assumed CME session length (18:00 ET open -> 17:00 ET close) for the per-session GB projection")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    if not out_dir.exists():
        print(f"out-dir {out_dir} does not exist", file=sys.stderr)
        return 1

    runs = discover_run_storage(out_dir)
    now = _now_utc()
    overall_fail = False

    print(f"=== DOM01 storage report, generated {now.isoformat()} ===\n")

    total_out_dir_bytes = sum(r.total_bytes for r in runs)
    print(f"out-dir total: {_fmt_bytes(total_out_dir_bytes)} across {len(runs)} run(s)\n")

    combined_active_bytes_per_hour = 0.0

    for r in runs:
        print(f"-- run {r.run_id} (prefix {r.prefix}) --")
        print(f"   StartUtc={r.start_utc.isoformat()}  EndUtc={r.end_utc.isoformat() if r.end_utc else 'null (IN PROGRESS)'}")
        for stream, sz in r.file_sizes.items():
            print(f"   {stream:10s} {_fmt_bytes(sz):>12s}  ({sz:,} bytes)")
        print(f"   TOTAL      {_fmt_bytes(r.total_bytes):>12s}  ({r.total_bytes:,} bytes)")

        reference_end = r.end_utc or now
        elapsed_h = max((reference_end - r.start_utc).total_seconds() / 3600.0, 1e-9)
        bytes_per_hour = r.total_bytes / elapsed_h
        print(f"   elapsed: {elapsed_h:.2f}h  -> avg growth rate: {_fmt_bytes(bytes_per_hour)}/hour")

        projected_session_gb = bytes_per_hour * args.session_hours / 1e9
        print(f"   projected size for one full {args.session_hours:.0f}h session at this rate: {projected_session_gb:.2f} GB "
              f"(coarse extrapolation from realized throughput only -- actual rate varies with market activity)")

        if not r.terminated:
            combined_active_bytes_per_hour += bytes_per_hour

        if r.depth_rows_written is not None:
            for label, count in (("depth", r.depth_rows_written), ("topofbook", r.tob_rows_written)):
                pct = 100.0 * count / r.max_rows_per_stream
                status = "PASS"
                if pct >= args.cap_warn_pct:
                    status = "WARN"
                print(f"   [{status}] {label} rows written: {count:,} / {r.max_rows_per_stream:,} ({pct:.1f}% of MaxRowsPerStreamFile)")
                if status == "WARN":
                    print(f"        -- approaching the row cap; further rows are DROPPED (not rotated) once hit. "
                          f"Restart the collector (detach/reattach the indicator) to open a new run before that happens.")

        if r.terminated:
            print(f"   TERMINATED -- eligible for lossless-compression-after-close (see section below)")
        print()

    # Disk free space
    disk_path = out_dir.resolve()
    total_b, used_b, free_b = shutil.disk_usage(str(disk_path))
    free_gib = free_b / 1024**3
    print(f"=== Disk (drive hosting {disk_path}) ===")
    print(f"   total={_fmt_bytes(total_b)}  used={_fmt_bytes(used_b)}  free={_fmt_bytes(free_b)} ({free_gib:.2f} GiB)")

    disk_status = "PASS"
    reasons = []
    if free_gib < args.fail_free_gib:
        disk_status = "FAIL"
        reasons.append(f"free space {free_gib:.1f} GiB < fail floor {args.fail_free_gib:.0f} GiB")
    elif free_gib < args.warn_free_gib:
        disk_status = "WARN"
        reasons.append(f"free space {free_gib:.1f} GiB < warn floor {args.warn_free_gib:.0f} GiB")

    if combined_active_bytes_per_hour > 0:
        hours_to_full = free_b / combined_active_bytes_per_hour
        days_to_full = hours_to_full / 24.0
        print(f"   combined growth rate across {sum(1 for r in runs if not r.terminated)} in-progress run(s): "
              f"{_fmt_bytes(combined_active_bytes_per_hour)}/hour")
        print(f"   at this rate: disk full in ~{hours_to_full:,.0f} hours (~{days_to_full:.1f} days)")
        if days_to_full < args.fail_days:
            disk_status = "FAIL"
            reasons.append(f"projected {days_to_full:.1f} days-to-full < fail threshold {args.fail_days:.0f} days")
        elif days_to_full < args.warn_days and disk_status == "PASS":
            disk_status = "WARN"
            reasons.append(f"projected {days_to_full:.1f} days-to-full < warn threshold {args.warn_days:.0f} days")
    else:
        print("   no in-progress runs -- no active growth rate to project from")

    print(f"\n   [{disk_status}] disk-space alert" + (f": {'; '.join(reasons)}" if reasons else ": no threshold crossed"))
    if disk_status == "FAIL":
        overall_fail = True

    terminated_runs = [r for r in runs if r.terminated]
    if terminated_runs:
        print(f"\n=== Compression candidates ({len(terminated_runs)} Terminated run(s)) ===")
        print("   Lossless gzip verified this session (round-trip sha256-identical, ~11.8x smaller on a real")
        print("   topofbook.csv sample). Safe procedure for a Terminated run's 4 CSVs:")
        print("     1. Recompute sha256 of each CSV, confirm it matches manifest.FileChecksumsSha256.")
        print("     2. gzip -k (keep original) each CSV.")
        print("     3. gunzip -c the .gz to a temp path, recompute sha256, confirm it still matches the manifest.")
        print("     4. Only after step 3 passes, delete the uncompressed original (never before verifying).")
        print("   Never compress a run before EndUtc is set -- an in-progress writer still owns that file handle.")
        for r in terminated_runs:
            print(f"   - {r.prefix} ({_fmt_bytes(r.total_bytes)})")

    return 1 if overall_fail else 0


if __name__ == "__main__":
    sys.exit(main())
