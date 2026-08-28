"""GENESIS search ledger — append-only, hash-chained log of every evaluated object.

Charter §25: no invisible failed trials. Discovery is free; hiding the search path is not.
Two record kinds:
  TRIAL  — registered BEFORE evaluation (family, hypothesis, params, data, ranges, cost model)
  RESULT — appended after evaluation, referencing the trial id

Integrity: every record carries sha256(prev_hash + canonical_json(record_body)).
`verify()` re-walks the chain; any edit or deletion breaks every downstream hash.
The ledger file is never rewritten, only appended (open mode 'a', binary, single line per record).
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone

LEDGER_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "research", "genesis", "SEARCH_LEDGER.jsonl",
)
GENESIS_HASH = "0" * 64


class LedgerError(RuntimeError):
    pass


def _canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def _git_sha() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=os.path.dirname(LEDGER_PATH), capture_output=True, text=True, timeout=15,
        )
        return out.stdout.strip() if out.returncode == 0 else "UNKNOWN"
    except Exception:
        return "UNKNOWN"


def hash_files(paths) -> str:
    """Order-stable sha256 over the byte content of the input data files."""
    h = hashlib.sha256()
    for p in sorted(str(p) for p in paths):
        h.update(os.path.basename(p).encode())
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
    return h.hexdigest()


def _read_all(path=None):
    path = path or LEDGER_PATH
    if not os.path.exists(path):
        return []
    with open(path, "rb") as f:
        return [json.loads(line) for line in f.read().splitlines() if line.strip()]


def _append(body: dict, path=None) -> dict:
    path = path or LEDGER_PATH
    rows = _read_all(path)
    prev = rows[-1]["hash"] if rows else GENESIS_HASH
    body = dict(body)
    body["seq"] = len(rows)
    body["prev_hash"] = prev
    body["hash"] = hashlib.sha256(prev.encode() + _canonical({k: v for k, v in body.items() if k != "hash"})).hexdigest()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "ab") as f:
        f.write(_canonical(body) + b"\n")
    return body


def new_trial(family: str, hypothesis: str, params: dict, features, target: str,
              train_range: str, val_range: str, cost_model: str,
              data_hash: str = "UNHASHED", parent: str | None = None, path=None) -> str:
    """Register a trial BEFORE its evaluation runs. Returns the immutable trial id."""
    for name, v in [("family", family), ("hypothesis", hypothesis), ("target", target),
                    ("train_range", train_range), ("cost_model", cost_model)]:
        if not str(v).strip():
            raise LedgerError(f"empty required field: {name}")
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rows = _read_all(path)
    trial_id = f"G{len([r for r in rows if r['kind'] == 'TRIAL']):05d}"
    _append({
        "kind": "TRIAL", "trial_id": trial_id, "ts_utc": ts, "git_sha": _git_sha(),
        "family": family, "hypothesis": hypothesis, "params": params,
        "features": list(features), "target": target,
        "train_range": train_range, "val_range": val_range,
        "cost_model": cost_model, "data_hash": data_hash, "parent": parent,
    }, path)
    return trial_id


def record_result(trial_id: str, metrics: dict, result: str, selected: bool = False, note: str = "", path=None):
    """Append the outcome for a registered trial. result: one of PASS/FAIL/NULL/DEFECT/ABORTED."""
    rows = _read_all(path)
    trials = {r["trial_id"] for r in rows if r["kind"] == "TRIAL"}
    if trial_id not in trials:
        raise LedgerError(f"result for unregistered trial {trial_id} — register the trial FIRST")
    if result not in ("PASS", "FAIL", "NULL", "DEFECT", "ABORTED"):
        raise LedgerError(f"invalid result {result!r}")
    if any(r["kind"] == "RESULT" and r["trial_id"] == trial_id for r in rows):
        raise LedgerError(f"trial {trial_id} already has a result — results are immutable")
    _append({
        "kind": "RESULT", "trial_id": trial_id,
        "ts_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "metrics": metrics, "result": result, "selected": bool(selected), "note": note,
    }, path)


def verify(path=None) -> dict:
    """Re-walk the whole chain. Raises LedgerError on any break; returns summary counts."""
    rows = _read_all(path)
    prev = GENESIS_HASH
    for i, r in enumerate(rows):
        if r["seq"] != i:
            raise LedgerError(f"seq gap at record {i}: found {r['seq']} — a record was removed or reordered")
        if r["prev_hash"] != prev:
            raise LedgerError(f"chain break at record {i}")
        expect = hashlib.sha256(prev.encode() + _canonical({k: v for k, v in r.items() if k != "hash"})).hexdigest()
        if r["hash"] != expect:
            raise LedgerError(f"tampered record at {i}")
        prev = r["hash"]
    trials = [r for r in rows if r["kind"] == "TRIAL"]
    results = [r for r in rows if r["kind"] == "RESULT"]
    return {"records": len(rows), "trials": len(trials), "results": len(results),
            "open": len(trials) - len(results),
            "selected": sum(1 for r in results if r["selected"])}


def _selftest():
    """Positive tests included: every guard is shown to FIRE (charter §8/J)."""
    import tempfile
    ok = 0
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "ledger.jsonl")
        t1 = new_trial("SELFTEST", "ledger works", {"a": 1}, ["f1"], "ret_1d",
                       "2020..2021", "2022", "commission_only", path=p)
        assert t1 == "G00000"; ok += 1
        record_result(t1, {"sharpe": 0.0}, "NULL", path=p); ok += 1
        assert verify(p) == {"records": 2, "trials": 1, "results": 1, "open": 0, "selected": 0}; ok += 1
        # guard 1 FIRES: result for unregistered trial
        try:
            record_result("G99999", {}, "FAIL", path=p); raise AssertionError("guard 1 silent")
        except LedgerError: ok += 1
        # guard 2 FIRES: second result for same trial
        try:
            record_result(t1, {}, "PASS", path=p); raise AssertionError("guard 2 silent")
        except LedgerError: ok += 1
        # guard 3 FIRES: invalid result token
        t2 = new_trial("SELFTEST", "x", {}, [], "y", "r", "v", "c", path=p)
        try:
            record_result(t2, {}, "GREAT", path=p); raise AssertionError("guard 3 silent")
        except LedgerError: ok += 1
        # guard 4 FIRES: tamper with a historical record body
        rows = open(p, "rb").read().splitlines()
        bad = json.loads(rows[0]); bad["hypothesis"] = "edited after the fact"
        with open(p, "wb") as f:
            f.write(_canonical(bad) + b"\n" + b"\n".join(rows[1:]) + b"\n")
        try:
            verify(p); raise AssertionError("guard 4 silent")
        except LedgerError: ok += 1
        # guard 5 FIRES: delete a record
        with open(p, "wb") as f:
            f.write(rows[0] + b"\n" + b"\n".join(rows[2:]) + b"\n")
        try:
            verify(p); raise AssertionError("guard 5 silent")
        except LedgerError: ok += 1
        # guard 6 FIRES: empty required field
        try:
            new_trial("", "h", {}, [], "t", "r", "v", "c", path=p); raise AssertionError("guard 6 silent")
        except LedgerError: ok += 1
    print(f"genesis_ledger selftest: {ok}/9 PASS (6 guards shown to fire)")


if __name__ == "__main__":
    _selftest()
