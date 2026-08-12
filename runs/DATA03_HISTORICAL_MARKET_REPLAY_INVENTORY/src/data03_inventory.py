"""
data03_inventory.py -- DATA03 Market Replay acquisition inventory. ENGINEERING ONLY.

Scans `db/replay/` READ-ONLY and builds a machine-readable manifest of what genuine NT8 Market
Replay data actually exists locally: per-file instrument/contract/date, size, SHA-256, a boundary
check against LOCKED_FORWARD.md, and a purely STRUCTURAL consistency check (file-size divisibility
against the 80-byte fixed-record stride established for the 2026-07-15 proof file -- a corruption/
truncation signal, not content decoding). Cross-references against `acquisition_plan.yaml`'s probe
list to report which planned dates are acquired vs. still missing.

This script NEVER triggers a download and NEVER reads price/size/depth field CONTENT from any
.nrd file -- only existence, size, checksum, and record-count-as-a-structural-fact. If you are
tempted to add anything that reads what a record actually says about price or depth, stop --
that belongs in a separately preregistered discovery run under DOM01_PROSPECTIVE_PROTOCOL.md's
governance, not here.

Usage:
    python runs/DATA03_HISTORICAL_MARKET_REPLAY_INVENTORY/src/data03_inventory.py
        [--replay-dir "C:\\Users\\Yuke Zhang\\Documents\\NinjaTrader 8\\db\\replay"]
        [--plan runs/DATA03_HISTORICAL_MARKET_REPLAY_INVENTORY/acquisition_plan.yaml]
        [--out-dir runs/DATA03_HISTORICAL_MARKET_REPLAY_INVENTORY/out]
        [--warn-free-gib 50] [--fail-free-gib 15]

Exit 0 = no LOCKED_FORWARD violation and no FAIL-level storage alert. Exit 1 otherwise. A
LOCKED_FORWARD violation here would mean a >=2026-08-01 .nrd file exists on disk -- this script
only ever REPORTS that (loudly, as a FAIL), it never reads such a file's content and never
deletes anything.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sys
from dataclasses import dataclass, asdict
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "research_sdk"))
from session_boundary import LOCKED_FORWARD_LAST_CONSUMED_SESSION  # noqa: E402

try:
    import yaml
except ImportError:
    yaml = None

PROVEN_RECORD_LEN = 80  # established structurally against the 2026-07-15 NQU6 proof file
PROVEN_HEADER_LEN = 1


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _fmt_bytes(n: float) -> str:
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if abs(n) < 1024.0:
            return f"{n:,.1f} {unit}"
        n /= 1024.0
    return f"{n:,.1f} PiB"


def _parse_contract_dir(name: str) -> tuple[str, str] | None:
    # e.g. "NQ 09-26" -> root="NQ", contract="09-26"
    parts = name.split(" ")
    if len(parts) == 2:
        return parts[0], parts[1]
    return None


@dataclass
class ReplayFile:
    instrument_dir: str
    root: str | None
    contract: str | None
    date_str: str | None
    path: str
    size_bytes: int
    sha256: str
    file_mtime_utc: str
    boundary_status: str        # AUTHORIZED / LOCKED_FORWARD_VIOLATION / UNPARSEABLE_DATE
    structural_record_count: int | None
    structural_consistency: str  # matches the proven 80-byte stride cleanly, or a note
    classification: str
    error: str | None


def scan_replay_dir(replay_dir: Path) -> list[ReplayFile]:
    results = []
    if not replay_dir.exists():
        return results
    for nrd_path in sorted(replay_dir.rglob("*.nrd")):
        instrument_dir = nrd_path.parent.name
        root_contract = _parse_contract_dir(instrument_dir)
        root, contract = root_contract if root_contract else (None, None)

        date_str = nrd_path.stem  # "20260715"
        boundary_status = "UNPARSEABLE_DATE"
        error = None
        try:
            d = date(int(date_str[0:4]), int(date_str[4:6]), int(date_str[6:8]))
            if d > LOCKED_FORWARD_LAST_CONSUMED_SESSION:
                boundary_status = "LOCKED_FORWARD_VIOLATION"
                error = (f"FILE DATED {d.isoformat()} IS PAST THE {LOCKED_FORWARD_LAST_CONSUMED_SESSION.isoformat()} "
                         f"BOUNDARY -- flagged, not read, not deleted. Escalate to owner.")
            else:
                boundary_status = "AUTHORIZED"
        except (ValueError, IndexError):
            error = f"could not parse a date from filename stem '{date_str}'"

        size = nrd_path.stat().st_size
        mtime = datetime.fromtimestamp(nrd_path.stat().st_mtime, tz=timezone.utc).isoformat()
        sha = _sha256(nrd_path)

        rec_count = None
        consistency = "not checked"
        if (size - PROVEN_HEADER_LEN) % PROVEN_RECORD_LEN == 0:
            rec_count = (size - PROVEN_HEADER_LEN) // PROVEN_RECORD_LEN
            consistency = f"clean ({rec_count:,} records @ {PROVEN_RECORD_LEN}B + {PROVEN_HEADER_LEN}B header, matches 2026-07-15 proof-file structure)"
        else:
            consistency = (f"DOES NOT divide cleanly by the proven {PROVEN_RECORD_LEN}B stride -- "
                            f"possibly a different record layout, a truncated/corrupted file, or a "
                            f"day whose format genuinely differs. Worth a closer look before trusting.")

        classification = ("GENUINE_NT8_MARKET_REPLAY_L1_PLUS_L2 (basis: official Get Market Replay "
                           "data workflow + NT8 documentation per owner; see spec.yaml)") if boundary_status == "AUTHORIZED" else "NOT_CLASSIFIED (boundary issue -- see error)"

        results.append(ReplayFile(
            instrument_dir=instrument_dir, root=root, contract=contract, date_str=date_str,
            path=str(nrd_path), size_bytes=size, sha256=sha, file_mtime_utc=mtime,
            boundary_status=boundary_status, structural_record_count=rec_count,
            structural_consistency=consistency, classification=classification, error=error,
        ))
    return results


def load_plan(plan_path: Path) -> dict:
    if yaml is None or not plan_path.exists():
        return {}
    return yaml.safe_load(plan_path.read_text(encoding="utf-8")) or {}


def cross_reference(files: list[ReplayFile], plan: dict) -> list[dict]:
    acquired_dates = {f.date_str for f in files if f.boundary_status == "AUTHORIZED"}
    rows = []
    for p in plan.get("probe_dates", []):
        d = p["date"].replace("-", "")
        rows.append({
            "planned_date": p["date"],
            "planned_instrument": p.get("instrument"),
            "acquired": d in acquired_dates,
            "plan_status_note": p.get("status", ""),
        })
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--replay-dir", default=r"C:\Users\Yuke Zhang\Documents\NinjaTrader 8\db\replay")
    ap.add_argument("--plan", default="runs/DATA03_HISTORICAL_MARKET_REPLAY_INVENTORY/acquisition_plan.yaml")
    ap.add_argument("--out-dir", default="runs/DATA03_HISTORICAL_MARKET_REPLAY_INVENTORY/out")
    ap.add_argument("--warn-free-gib", type=float, default=50.0)
    ap.add_argument("--fail-free-gib", type=float, default=15.0)
    args = ap.parse_args()

    replay_dir = Path(args.replay_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    files = scan_replay_dir(replay_dir)
    plan = load_plan(Path(args.plan))
    cross_ref = cross_reference(files, plan)

    overall_fail = False

    print(f"=== DATA03 replay inventory, generated {datetime.now(timezone.utc).isoformat()} ===\n")
    print(f"Scanned: {replay_dir}")
    print(f"Found {len(files)} .nrd file(s)\n")

    total_bytes = 0
    for f in files:
        print(f"-- {f.instrument_dir} / {f.date_str} --")
        print(f"   path: {f.path}")
        print(f"   size: {_fmt_bytes(f.size_bytes)} ({f.size_bytes:,} bytes)   sha256: {f.sha256[:16]}...")
        print(f"   file mtime (UTC): {f.file_mtime_utc}")
        print(f"   boundary: {f.boundary_status}")
        print(f"   structural: {f.structural_consistency}")
        print(f"   classification: {f.classification}")
        if f.error:
            print(f"   *** {f.error} ***")
            overall_fail = True
        total_bytes += f.size_bytes
        print()

    if cross_ref:
        print("=== Acquisition-plan cross-reference ===")
        missing = [r for r in cross_ref if not r["acquired"]]
        for r in cross_ref:
            mark = "ACQUIRED" if r["acquired"] else "missing"
            print(f"   [{mark}] {r['planned_date']} ({r['planned_instrument']})  -- {r['plan_status_note']}")
        print(f"   {len(cross_ref)-len(missing)}/{len(cross_ref)} planned probe dates acquired, "
              f"{len(missing)} still outstanding\n")

    total_b, used_b, free_b = shutil.disk_usage(str(replay_dir if replay_dir.exists() else Path(".").resolve()))
    free_gib = free_b / 1024**3
    n_sessions = len(files)
    mean_size = total_bytes / n_sessions if n_sessions else 0
    sizes_sorted = sorted(f.size_bytes for f in files)
    median_size = sizes_sorted[len(sizes_sorted)//2] if sizes_sorted else 0

    print("=== Storage ===")
    print(f"   cumulative replay size: {_fmt_bytes(total_bytes)} across {n_sessions} session(s)")
    print(f"   mean/session: {_fmt_bytes(mean_size)}   median/session: {_fmt_bytes(median_size)}")
    print(f"   disk free: {_fmt_bytes(free_b)} ({free_gib:.2f} GiB)")

    if n_sessions:
        remaining_sessions_at_mean = free_b / mean_size if mean_size else float("inf")
        print(f"   at the current mean session size, ~{remaining_sessions_at_mean:,.0f} more sessions "
              f"could fit before disk exhaustion (ignoring everything else also using this disk)")

    storage_status = "PASS"
    if free_gib < args.fail_free_gib:
        storage_status = "FAIL"
        overall_fail = True
    elif free_gib < args.warn_free_gib:
        storage_status = "WARN"
    print(f"   [{storage_status}] disk-space alert (warn<{args.warn_free_gib:.0f}GiB, fail<{args.fail_free_gib:.0f}GiB)")

    boundary_violations = [f for f in files if f.boundary_status == "LOCKED_FORWARD_VIOLATION"]
    if boundary_violations:
        overall_fail = True
        print(f"\n   *** {len(boundary_violations)} LOCKED_FORWARD BOUNDARY VIOLATION(S) DETECTED ON DISK ***")
        for f in boundary_violations:
            print(f"       {f.path}")

    manifest = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "replay_dir": str(replay_dir),
        "files": [asdict(f) for f in files],
        "acquisition_plan_cross_reference": cross_ref,
        "storage": {
            "cumulative_bytes": total_bytes, "session_count": n_sessions,
            "mean_bytes": mean_size, "median_bytes": median_size,
            "free_bytes": free_b, "free_gib": free_gib, "status": storage_status,
        },
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    with open(out_dir / "manifest.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(asdict(files[0]).keys()) if files else
                            ["instrument_dir", "root", "contract", "date_str", "path", "size_bytes",
                             "sha256", "file_mtime_utc", "boundary_status", "structural_record_count",
                             "structural_consistency", "classification", "error"])
        w.writeheader()
        for f in files:
            w.writerow(asdict(f))

    print(f"\nmanifest -> {out_dir / 'manifest.json'}  /  {out_dir / 'manifest.csv'}")
    return 1 if overall_fail else 0


if __name__ == "__main__":
    sys.exit(main())
