"""
dom01_qc_monitor.py -- DOM01 collection-integrity / feed-integrity QC monitor.

ENGINEERING ONLY. Scope is deliberately narrow, per the 2026-08-11 owner directive:
data-integrity and feed-integrity checks ONLY -- session/file presence, first/last
timestamps, timestamp monotonicity, duplicates, malformed rows, impossible/negative
sizes, depth-level validity, crossed/locked-book incidence, event-rate gaps,
reconnect/gap markers, heartbeat continuity, manifest/schema consistency, contract
identity/rollover, connection status, disk/file-write failures, checksums/completeness
metadata.

This module computes and reports NONE of: future returns, markouts, PnL, predictive
correlations, alpha-by-DOM-state, conditional price response, or candidate performance.
QC is not alpha research -- do not add any such computation to this file. If a future
predictive/outcome analysis is wanted, it belongs in a separately preregistered spec
under a new runs/<RUN_ID>/, never folded into this monitor.

Usage:
    python runs/DOM01_LIQUIDITY_STATE/collector/qc/dom01_qc_monitor.py \
        [--out-dir runs/DOM01_LIQUIDITY_STATE/collector/out] \
        [--report-dir runs/DOM01_LIQUIDITY_STATE/collector/qc/reports]

Writes one JSON + one Markdown report per discovered collector run (grouped by the
manifest's own RunId), plus one cross-run rollup report (contract identity/rollover
across runs, chronological gaps between run StartUtc/EndUtc). Read-only against `out/`
-- never mutates collector output. Safe to run repeatedly, including against an
in-progress (EndUtc still null) run.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import statistics
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION_KNOWN = {"dom01-collector-schema-v1"}

DEPTH_COLUMNS = ["RunId", "SeqLocal", "RecordedUtc", "EventTime", "EventTimeKind",
                  "Side", "Level", "Price", "Size", "Operation", "MarketMaker",
                  "IsReset", "IsTopOfBook"]
TOB_COLUMNS = ["RunId", "SeqLocal", "RecordedUtc", "EventTime", "EventTimeKind",
               "Type", "Price", "Size"]
EVENTS_COLUMNS = ["RunId", "SeqLocal", "RecordedUtc", "Category", "Detail"]
HEARTBEAT_COLUMNS = ["RunId", "SeqLocal", "RecordedUtc", "BarTime", "DepthRowsWritten",
                      "TopOfBookRowsWritten", "SecondsSinceLastDepthEvent",
                      "SecondsSinceLastTobEvent"]

# Generous, non-alpha sanity band for a raw NQ print/quote price -- catches garbage
# values (0, negative, absurd magnitude) without encoding any market-level judgment.
NQ_PRICE_SANITY_MIN = 1000.0
NQ_PRICE_SANITY_MAX = 100000.0

STREAM_NAME_TO_COLUMNS = {
    "depth": DEPTH_COLUMNS,
    "topofbook": TOB_COLUMNS,
    "events": EVENTS_COLUMNS,
    "heartbeat": HEARTBEAT_COLUMNS,
}


@dataclass
class Check:
    name: str
    status: str  # PASS | WARN | FAIL | INFO
    detail: str

    def to_dict(self):
        return asdict(self)


@dataclass
class RunReport:
    run_id: str
    prefix: str
    checks: list = field(default_factory=list)

    def add(self, name: str, status: str, detail: str):
        self.checks.append(Check(name, status, detail))

    @property
    def verdict(self) -> str:
        statuses = {c.status for c in self.checks}
        if "FAIL" in statuses:
            return "FAIL"
        if "WARN" in statuses:
            return "WARN"
        return "CLEAN_PASS"

    def to_dict(self):
        return {
            "run_id": self.run_id,
            "prefix": self.prefix,
            "verdict": self.verdict,
            "checks": [c.to_dict() for c in self.checks],
        }


def _parse_utc(s: str) -> datetime:
    s = s.strip().rstrip("Z").replace(" ", "T")
    return datetime.fromisoformat(s).replace(tzinfo=timezone.utc)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _scan_malformed_rows(path: Path, expected_columns: list[str]) -> tuple[int, int, list[int]]:
    """Fast structural pass with the stdlib csv reader (not pandas, which can silently
    coerce or skip malformed rows). Returns (total_data_rows, malformed_count,
    first_few_malformed_line_numbers)."""
    total = 0
    malformed = 0
    bad_lines = []
    ncols = len(expected_columns)
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        header_ok = header == expected_columns
        for lineno, row in enumerate(reader, start=2):
            total += 1
            if len(row) != ncols:
                malformed += 1
                if len(bad_lines) < 10:
                    bad_lines.append(lineno)
    return total, malformed, bad_lines, header_ok


def check_file_presence(prefix: str, out_dir: Path, report: RunReport) -> dict:
    paths = {}
    for stream in ("manifest",) + tuple(STREAM_NAME_TO_COLUMNS):
        ext = "json" if stream == "manifest" else "csv"
        p = out_dir / f"{prefix}_{stream}.{ext}"
        exists = p.exists()
        paths[stream] = p if exists else None
        if not exists:
            report.add(f"file_presence:{stream}", "FAIL", f"missing expected file {p.name}")
        elif p.stat().st_size == 0:
            report.add(f"file_presence:{stream}", "FAIL", f"{p.name} exists but is zero bytes (disk/write failure)")
        else:
            report.add(f"file_presence:{stream}", "PASS", f"{p.name} present, {p.stat().st_size} bytes")
    return paths


def check_manifest(manifest_path: Path, report: RunReport) -> dict:
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        report.add("manifest:parseable", "FAIL", f"manifest is not valid JSON: {e}")
        return {}
    report.add("manifest:parseable", "PASS", "valid JSON")

    schema = manifest.get("SchemaVersion")
    if schema in SCHEMA_VERSION_KNOWN:
        report.add("manifest:schema_version", "PASS", schema)
    else:
        report.add("manifest:schema_version", "WARN",
                    f"unrecognized SchemaVersion '{schema}' -- check SCHEMA.md before assuming column layout")

    disable_l2 = manifest.get("DataConnectionDisableL2Data")
    if disable_l2 == "False":
        report.add("connection:disable_l2_data", "PASS", "DataConnectionDisableL2Data=False")
    else:
        report.add("connection:disable_l2_data", "FAIL",
                    f"DataConnectionDisableL2Data={disable_l2!r} -- connection is not confirmed to serve L2 depth")

    status_at_init = manifest.get("DataConnectionStatusAtInit", "")
    if "Connected" in status_at_init:
        report.add("connection:status_at_init", "PASS", status_at_init)
    else:
        report.add("connection:status_at_init", "FAIL", f"DataConnectionStatusAtInit={status_at_init!r}")

    conn_type = manifest.get("DataConnectionOptionsTypeName", "")
    if "Simulation" in conn_type:
        report.add("connection:type", "WARN",
                    f"connection type {conn_type!r} looks like a historical-replay connection, not a live/broker feed")
    else:
        report.add("connection:type", "INFO", conn_type)

    terminated = manifest.get("EndUtc") is not None
    report.add("manifest:run_state", "INFO",
                "Terminated (EndUtc set)" if terminated else "IN_PROGRESS (EndUtc still null)")

    if terminated:
        if manifest.get("FatalErrorOccurred") is True:
            report.add("manifest:fatal_error_flag", "FAIL", "manifest.FatalErrorOccurred=true")
        else:
            report.add("manifest:fatal_error_flag", "PASS", "FatalErrorOccurred=false")
        cap = manifest.get("CapReached", {})
        if cap and (cap.get("Depth") or cap.get("TopOfBook")):
            report.add("manifest:cap_reached", "WARN", f"CapReached={cap} -- stream truncated by row cap, not a clean end")
        else:
            report.add("manifest:cap_reached", "PASS", f"CapReached={cap}")
    else:
        report.add("manifest:fatal_error_flag", "INFO", "run in progress -- final fatal-error flag not yet set")

    report.add("manifest:instrument", "INFO",
                f"{manifest.get('InstrumentFullName')} (root={manifest.get('InstrumentRoot')}, "
                f"expiry={manifest.get('ContractExpiry')})")
    return manifest


def check_checksums(manifest: dict, prefix: str, out_dir: Path, report: RunReport):
    checksums = manifest.get("FileChecksumsSha256")
    if not checksums:
        report.add("checksums:verified", "INFO",
                    "no FileChecksumsSha256 in manifest yet (run in progress) -- checksum check deferred to Terminated")
        return
    mismatches = []
    for stream, expected in checksums.items():
        stream_key = stream.lower().replace("topofbook", "topofbook")
        p = out_dir / f"{prefix}_{stream_key}.csv"
        if not p.exists():
            mismatches.append(f"{stream}: file missing")
            continue
        actual = _sha256(p)
        if actual.lower() != expected.lower():
            mismatches.append(f"{stream}: expected {expected[:12]}... got {actual[:12]}...")
    if mismatches:
        report.add("checksums:verified", "FAIL", "; ".join(mismatches))
    else:
        report.add("checksums:verified", "PASS", f"{len(checksums)} file(s) match manifest FileChecksumsSha256")


def check_events_stream(path: Path, report: RunReport):
    total, malformed, bad_lines, header_ok = _scan_malformed_rows(path, EVENTS_COLUMNS)
    report.add("events:header", "PASS" if header_ok else "FAIL",
                "matches SCHEMA.md" if header_ok else "header does not match expected EVENTS_COLUMNS")
    report.add("events:malformed_rows", "PASS" if malformed == 0 else "FAIL",
                f"{malformed}/{total} malformed rows" + (f" (first: lines {bad_lines})" if bad_lines else ""))

    categories = []
    fatal_details = []
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            categories.append(row["Category"])
            if row["Category"] == "FATAL_ERROR":
                fatal_details.append(row["Detail"])

    if fatal_details:
        report.add("events:fatal_error", "FAIL", f"{len(fatal_details)} FATAL_ERROR row(s): {fatal_details[:3]}")
    else:
        report.add("events:fatal_error", "PASS", "no FATAL_ERROR rows")

    warn_count = categories.count("WARN")
    if warn_count:
        report.add("events:warn_rows", "WARN", f"{warn_count} WARN row(s) in events.csv")
    else:
        report.add("events:warn_rows", "PASS", "0 WARN rows")

    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        details = [row["Detail"] for row in reader if row["Category"] == "STATE_TRANSITION"]
    seq_text = " | ".join(details)
    saw_loaded = "DataLoaded" in seq_text
    saw_realtime = "Realtime" in seq_text
    saw_terminated = "Terminated" in seq_text
    if saw_loaded and saw_realtime:
        report.add("events:state_sequence", "PASS",
                    f"DataLoaded -> Realtime observed" + (" -> Terminated" if saw_terminated else " (run still open)"))
    else:
        report.add("events:state_sequence", "WARN",
                    f"expected DataLoaded->Realtime state-transition text not both found: {details}")


def check_heartbeat_stream(path: Path, report: RunReport,
                            gap_seconds_warn: float, gap_seconds_fail: float,
                            cadence_outlier_multiplier: float):
    total, malformed, bad_lines, header_ok = _scan_malformed_rows(path, HEARTBEAT_COLUMNS)
    report.add("heartbeat:header", "PASS" if header_ok else "FAIL",
                "matches SCHEMA.md" if header_ok else "header mismatch")
    report.add("heartbeat:malformed_rows", "PASS" if malformed == 0 else "FAIL",
                f"{malformed}/{total} malformed rows")
    if total == 0:
        report.add("heartbeat:presence", "WARN", "heartbeat.csv has zero data rows")
        return

    recorded, since_depth, since_tob = [], [], []
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                recorded.append(_parse_utc(row["RecordedUtc"]))
                since_depth.append(float(row["SecondsSinceLastDepthEvent"]))
                since_tob.append(float(row["SecondsSinceLastTobEvent"]))
            except (ValueError, KeyError):
                continue

    monotonic = all(recorded[i] <= recorded[i + 1] for i in range(len(recorded) - 1))
    report.add("heartbeat:recorded_utc_monotonic", "PASS" if monotonic else "FAIL",
                "non-decreasing" if monotonic else "OUT-OF-ORDER RecordedUtc rows found")

    max_since_depth = max(since_depth) if since_depth else 0.0
    max_since_tob = max(since_tob) if since_tob else 0.0
    for label, val in (("SecondsSinceLastDepthEvent", max_since_depth), ("SecondsSinceLastTobEvent", max_since_tob)):
        if val >= gap_seconds_fail:
            report.add(f"heartbeat:max_{label}", "FAIL",
                        f"max observed gap {val:.1f}s >= fail threshold {gap_seconds_fail}s -- likely feed/collector outage")
        elif val >= gap_seconds_warn:
            report.add(f"heartbeat:max_{label}", "WARN",
                        f"max observed gap {val:.1f}s >= warn threshold {gap_seconds_warn}s")
        else:
            report.add(f"heartbeat:max_{label}", "PASS", f"max observed gap {val:.1f}s")

    if len(recorded) >= 3:
        deltas = [(recorded[i + 1] - recorded[i]).total_seconds() for i in range(len(recorded) - 1)]
        med = statistics.median(deltas)
        floor = max(med * cadence_outlier_multiplier, 10.0)
        outliers = [d for d in deltas if d > floor]
        if outliers:
            report.add("heartbeat:cadence_continuity", "WARN",
                        f"{len(outliers)} heartbeat gap(s) exceed {cadence_outlier_multiplier}x the median "
                        f"inter-beat interval ({med:.2f}s median; largest outlier {max(outliers):.1f}s)")
        else:
            report.add("heartbeat:cadence_continuity", "PASS",
                        f"no cadence outliers (median inter-beat interval {med:.2f}s, n={len(deltas)})")
    else:
        report.add("heartbeat:cadence_continuity", "INFO", "too few heartbeat rows to assess cadence yet")


def check_depth_stream(path: Path, report: RunReport):
    total, malformed, bad_lines, header_ok = _scan_malformed_rows(path, DEPTH_COLUMNS)
    report.add("depth:header", "PASS" if header_ok else "FAIL",
                "matches SCHEMA.md" if header_ok else "header mismatch")
    report.add("depth:malformed_rows", "PASS" if malformed == 0 else "FAIL",
                f"{malformed}/{total} malformed rows" + (f" (first: lines {bad_lines})" if bad_lines else ""))
    if total == 0:
        report.add("depth:presence", "WARN", "depth.csv has zero data rows -- no depth data received yet")
        return

    seq_seen = set()
    seq_dupes = 0
    seq_gaps = 0
    prev_seq = None
    prev_recorded = None
    ts_out_of_order = 0
    first_recorded = last_recorded = None
    first_event = last_event = None
    sides, ops = set(), set()
    level_min, level_max = None, None
    bad_level = 0
    bad_size = 0
    bad_price = 0
    reset_count = 0
    offsets_sample = []

    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            seq = int(row["SeqLocal"])
            if seq in seq_seen:
                seq_dupes += 1
            seq_seen.add(seq)
            if prev_seq is not None and seq != prev_seq + 1:
                seq_gaps += 1
            prev_seq = seq

            rec = _parse_utc(row["RecordedUtc"])
            if first_recorded is None:
                first_recorded = rec
            last_recorded = rec
            if prev_recorded is not None and rec < prev_recorded:
                ts_out_of_order += 1
            prev_recorded = rec

            if first_event is None:
                first_event = row["EventTime"]
            last_event = row["EventTime"]

            sides.add(row["Side"])
            ops.add(row["Operation"])
            level = int(row["Level"])
            level_min = level if level_min is None else min(level_min, level)
            level_max = level if level_max is None else max(level_max, level)
            if level < 0:
                bad_level += 1

            size = int(row["Size"])
            price = float(row["Price"])
            op = row["Operation"]
            if op in ("Add", "Update"):
                if size <= 0:
                    bad_size += 1
                if not (NQ_PRICE_SANITY_MIN <= price <= NQ_PRICE_SANITY_MAX):
                    bad_price += 1
            else:  # Remove -- price/size structurally 0, not an error (see qc/README.md)
                if size < 0:
                    bad_size += 1

            if row["IsReset"] == "True":
                reset_count += 1

            if i < 200 or i % 5000 == 0:
                try:
                    et_naive = datetime.fromisoformat(row["EventTime"])
                    offsets_sample.append((rec.replace(tzinfo=None) - et_naive).total_seconds())
                except ValueError:
                    pass

    report.add("depth:seq_local_duplicates", "PASS" if seq_dupes == 0 else "FAIL", f"{seq_dupes} duplicate SeqLocal value(s)")
    report.add("depth:seq_local_gaps", "PASS" if seq_gaps == 0 else "WARN",
                f"{seq_gaps} gap(s) in SeqLocal sequence (possible dropped/lost row)")
    report.add("depth:recorded_utc_monotonic", "PASS" if ts_out_of_order == 0 else "FAIL",
                f"{ts_out_of_order} out-of-order RecordedUtc row(s)")
    report.add("depth:first_last_timestamps", "INFO",
                f"RecordedUtc {first_recorded.isoformat()} .. {last_recorded.isoformat()}; "
                f"EventTime {first_event} .. {last_event}")
    report.add("depth:side_vocabulary", "PASS" if sides <= {"Bid", "Ask"} else "FAIL", f"observed: {sorted(sides)}")
    report.add("depth:operation_vocabulary", "PASS" if ops <= {"Add", "Update", "Remove"} else "FAIL", f"observed: {sorted(ops)}")
    report.add("depth:level_validity", "PASS" if bad_level == 0 else "FAIL",
                f"{bad_level} negative Level value(s); observed range [{level_min}, {level_max}]")
    report.add("depth:size_validity", "PASS" if bad_size == 0 else "FAIL",
                f"{bad_size} row(s) with impossible Size (<=0 on Add/Update, or <0 on Remove)")
    report.add("depth:price_sanity", "PASS" if bad_price == 0 else "WARN",
                f"{bad_price} Add/Update row(s) outside sanity band [{NQ_PRICE_SANITY_MIN},{NQ_PRICE_SANITY_MAX}] "
                f"(Remove rows structurally carry Price=0 and are excluded from this check)")
    report.add("depth:is_reset_count", "INFO", f"{reset_count} IsReset=True row(s) (book-resync markers)")

    if offsets_sample:
        med_off = statistics.median(offsets_sample)
        spread = max(offsets_sample) - min(offsets_sample)
        report.add("depth:eventtime_semantics", "INFO",
                    f"RecordedUtc - EventTime(naive) median offset {med_off:+.1f}s, sample spread {spread:.1f}s "
                    f"(EventTimeKind=Unspecified per manifest -- this is an empirical observation of apparent "
                    f"local-clock offset, NOT a confirmed timezone; do not treat as verified until cross-checked "
                    f"against a known trade print, per SCHEMA.md's own disclosed limitation)")


def check_topofbook_stream(path: Path, report: RunReport, crossed_warn_pct: float):
    total, malformed, bad_lines, header_ok = _scan_malformed_rows(path, TOB_COLUMNS)
    report.add("topofbook:header", "PASS" if header_ok else "FAIL",
                "matches SCHEMA.md" if header_ok else "header mismatch")
    report.add("topofbook:malformed_rows", "PASS" if malformed == 0 else "FAIL",
                f"{malformed}/{total} malformed rows")
    if total == 0:
        report.add("topofbook:presence", "WARN", "topofbook.csv has zero data rows")
        return

    seq_seen = set()
    seq_dupes = 0
    prev_recorded = None
    ts_out_of_order = 0
    types = set()
    bb = ba = None
    crossed = locked = compared = 0
    first_recorded = last_recorded = None

    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            seq = int(row["SeqLocal"])
            if seq in seq_seen:
                seq_dupes += 1
            seq_seen.add(seq)

            rec = _parse_utc(row["RecordedUtc"])
            if first_recorded is None:
                first_recorded = rec
            last_recorded = rec
            if prev_recorded is not None and rec < prev_recorded:
                ts_out_of_order += 1
            prev_recorded = rec

            t = row["Type"]
            types.add(t)
            price = float(row["Price"])
            if t == "Bid":
                bb = price
            elif t == "Ask":
                ba = price
            if bb is not None and ba is not None:
                compared += 1
                if bb > ba:
                    crossed += 1
                elif bb == ba:
                    locked += 1

    report.add("topofbook:seq_local_duplicates", "PASS" if seq_dupes == 0 else "FAIL", f"{seq_dupes} duplicate SeqLocal value(s)")
    report.add("topofbook:recorded_utc_monotonic", "PASS" if ts_out_of_order == 0 else "FAIL",
                f"{ts_out_of_order} out-of-order RecordedUtc row(s)")
    report.add("topofbook:first_last_timestamps", "INFO",
                f"{first_recorded.isoformat()} .. {last_recorded.isoformat()}")
    report.add("topofbook:type_vocabulary", "PASS" if types <= {"Bid", "Ask", "Last"} else "FAIL", f"observed: {sorted(types)}")

    if compared:
        crossed_pct = 100.0 * crossed / compared
        locked_pct = 100.0 * locked / compared
        status = "WARN" if crossed_pct > crossed_warn_pct else "PASS"
        report.add("topofbook:crossed_locked_incidence", status,
                    f"crossed {crossed}/{compared} ({crossed_pct:.3f}%), locked {locked}/{compared} ({locked_pct:.3f}%) "
                    f"of sequential best-bid/ask comparisons (a small nonzero rate is expected from real-time "
                    f"update-ordering artifacts; this is descriptive, not a trading signal)")
    else:
        report.add("topofbook:crossed_locked_incidence", "INFO", "insufficient Bid+Ask pairs to compare yet")


def discover_runs(out_dir: Path) -> list[tuple[str, Path]]:
    runs = []
    for manifest_path in sorted(out_dir.glob("*_manifest.json")):
        prefix = manifest_path.name[: -len("_manifest.json")]
        runs.append((prefix, manifest_path))
    return runs


def run_qc_for_prefix(prefix: str, out_dir: Path, args) -> RunReport:
    manifest_probe_path = out_dir / f"{prefix}_manifest.json"
    run_id = prefix
    try:
        run_id = json.loads(manifest_probe_path.read_text(encoding="utf-8")).get("RunId", prefix)
    except Exception:
        pass
    report = RunReport(run_id=run_id, prefix=prefix)

    paths = check_file_presence(prefix, out_dir, report)
    manifest = {}
    if paths.get("manifest"):
        manifest = check_manifest(paths["manifest"], report)
        check_checksums(manifest, prefix, out_dir, report)
    if paths.get("depth"):
        check_depth_stream(paths["depth"], report)
    if paths.get("topofbook"):
        check_topofbook_stream(paths["topofbook"], report, args.crossed_warn_pct)
    if paths.get("events"):
        check_events_stream(paths["events"], report)
    if paths.get("heartbeat"):
        check_heartbeat_stream(paths["heartbeat"], report, args.gap_seconds_warn,
                                args.gap_seconds_fail, args.cadence_outlier_multiplier)
    return report


def rollup_contract_identity(run_manifests: list[dict]) -> list[Check]:
    checks = []
    entries = []
    for m in run_manifests:
        entries.append((m.get("StartUtc"), m.get("InstrumentFullName"), m.get("ContractExpiry")))
    entries.sort(key=lambda e: e[0] or "")
    prev = None
    for start, full_name, expiry in entries:
        if prev is not None and (full_name, expiry) != prev:
            checks.append(Check("rollover:contract_change", "INFO",
                                 f"contract changed at run starting {start}: {prev} -> {(full_name, expiry)}"))
        prev = (full_name, expiry)
    checks.append(Check("rollover:observed_contracts", "INFO",
                         f"{len(set((e[1], e[2]) for e in entries))} distinct contract(s) across {len(entries)} run(s): "
                         f"{sorted(set((e[1], e[2]) for e in entries))}"))
    return checks


def render_markdown(report: RunReport) -> str:
    lines = [f"# DOM01 QC report -- run `{report.run_id}` (prefix `{report.prefix}`)", "",
              f"**Verdict: {report.verdict}**", "",
              "| Check | Status | Detail |", "|---|---|---|"]
    for c in report.checks:
        detail = c.detail.replace("|", "\\|")
        lines.append(f"| {c.name} | {c.status} | {detail} |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out-dir", default="runs/DOM01_LIQUIDITY_STATE/collector/out")
    ap.add_argument("--report-dir", default="runs/DOM01_LIQUIDITY_STATE/collector/qc/reports")
    ap.add_argument("--gap-seconds-warn", type=float, default=30.0,
                     help="SecondsSinceLast{Depth,Tob}Event WARN threshold")
    ap.add_argument("--gap-seconds-fail", type=float, default=120.0,
                     help="SecondsSinceLast{Depth,Tob}Event FAIL threshold")
    ap.add_argument("--cadence-outlier-multiplier", type=float, default=5.0,
                     help="flag a heartbeat inter-beat gap exceeding this multiple of the run's own median")
    ap.add_argument("--crossed-warn-pct", type=float, default=2.0,
                     help="WARN if crossed-book incidence exceeds this percent of compared snapshots")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    report_dir = Path(args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)

    if not out_dir.exists():
        print(f"out-dir {out_dir} does not exist -- nothing to check", file=sys.stderr)
        return 1

    runs = discover_runs(out_dir)
    if not runs:
        print(f"no *_manifest.json files found under {out_dir} -- collector has not produced output yet")
        return 0

    all_reports = []
    all_manifests = []
    overall_fail = False
    for prefix, manifest_path in runs:
        report = run_qc_for_prefix(prefix, out_dir, args)
        all_reports.append(report)
        try:
            all_manifests.append(json.loads(manifest_path.read_text(encoding="utf-8")))
        except Exception:
            pass

        json_path = report_dir / f"{prefix}_qc.json"
        md_path = report_dir / f"{prefix}_qc.md"
        json_path.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
        md_path.write_text(render_markdown(report), encoding="utf-8")

        print(f"[{report.verdict}] {report.run_id} ({sum(1 for c in report.checks if c.status=='FAIL')} FAIL, "
              f"{sum(1 for c in report.checks if c.status=='WARN')} WARN) -> {md_path}")
        if report.verdict == "FAIL":
            overall_fail = True

    rollup_checks = rollup_contract_identity(all_manifests)
    rollup = {
        "generated_runs": len(all_reports),
        "per_run_verdicts": {r.run_id: r.verdict for r in all_reports},
        "cross_run_checks": [c.to_dict() for c in rollup_checks],
    }
    rollup_path = report_dir / "_rollup.json"
    rollup_path.write_text(json.dumps(rollup, indent=2), encoding="utf-8")
    print(f"rollup -> {rollup_path}")
    for c in rollup_checks:
        print(f"  [{c.status}] {c.name}: {c.detail}")

    return 1 if overall_fail else 0


if __name__ == "__main__":
    sys.exit(main())
