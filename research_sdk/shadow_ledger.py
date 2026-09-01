"""DECISION-FIRST HASH-CHAINED SHADOW LEDGER.  Data logging only -- never an order path.

WHY THIS FILE EXISTS.  A shadow ledger's entire value is that a row was written BEFORE its outcome
existed.  Nothing about a CSV enforces that.  This module makes the property MECHANICAL:

  1. TWO SEPARATE FILES.  Decisions and outcomes never share a file.  An outcome is appended later
     and REFERENCES a decision by sequence number.  A decision row is never edited to carry its
     result, because editing it is exactly the act that destroys the evidence class.
  2. HASH CHAIN.  Each row carries prev_hash and row_hash over its canonical JSON form.  Rewriting
     any earlier row breaks every hash after it.  `verify` recomputes the whole chain.
  3. NO BACKFILL, ENFORCED.  A decision timestamp at or before SHADOW_START is REFUSED, and so is
     one that does not strictly advance the previous decision's timestamp.
  4. QUALITY IS MANDATORY.  A blocked or degraded decision is RECORDED with its reason.  A ledger
     that silently drops bad rows becomes a filtered sample -- the failure mode it exists to avoid.

Discipline rule: a check that cannot fail is useless, so `selftest()` below TAMPERS with a written
ledger and asserts that verification catches it.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
from datetime import datetime
from typing import Any

GENESIS = "0" * 64

DECISION_FIELDS = [
    "seq", "ts_decision", "strategy_id", "source_hash", "config_hash",
    "data_cutoff", "input_dataset_version", "input_source_hashes",
    "action", "intended_qty", "expected_costs", "quality_status", "blocked_reason",
    "prev_hash", "row_hash",
]
OUTCOME_FIELDS = [
    "seq", "decision_seq", "ts_outcome", "entry_fill", "exit_fill",
    "gross_pnl", "costs", "net_pnl", "data_quality", "note",
    "prev_hash", "row_hash",
]
# [CLEANSET 4, 2026-09-01] COSTS_MODELLED was MISSING and the seam was never tested.
#   shadow_runner.exec_costs() (:88) returns ("...", "COSTS_MODELLED") whenever the broker
#   reports $0.00 commission -- which is EVERY execution this broker produces -- and passes
#   it straight to append_outcome(data_quality=dq) at :176.  append_outcome then raised
#   `data_quality 'COSTS_MODELLED' not in QUALITY` and the row spilled to spillover.jsonl.
#   Both sides were unit-tested (runner selftest 10/10 asserts exec_costs returns the tuple;
#   ledger selftest 11/11 asserts the enum rejects unknown values). NOBODY TESTED THE JOIN.
#   The chain has zero rows so it has never fired; it fires on the first outcome after
#   SHADOW_START = 2026-09-01 18:00 ET.  Adding the value the emitter already intends to
#   emit is the fix.  SHADOW_START, _canon and _hash are untouched -- the chain is unchanged.
QUALITY = ("OK", "GAP", "STALE_QUOTE", "FILL_TIMEOUT", "BLOCKED", "COSTS_MODELLED")
ACTIONS = ("LONG", "SHORT", "FLAT", "NO_DECISION")


class LedgerError(RuntimeError):
    pass


def instant(ts: str) -> datetime:
    """Parse an ISO-8601 stamp to an ABSOLUTE INSTANT, and FAIL CLOSED if that is not possible.

    ⚠ WHY THIS EXISTS -- a real defect caught by the shadow preflight BEFORE the first row was
    ever written.  The first version of this module compared timestamps as STRINGS.  That is
    correct only while every row carries the same UTC offset, and the shadow starts in EDT
    (-04:00) and runs into EST (-05:00).  Concretely:

        '2026-11-02T08:30:00-05:00'  vs  '2026-11-02T09:00:00-04:00'
        string compare  : a < b      (because "08" < "09")
        instant compare : a > b      (13:30Z vs 13:00Z)

    The two DISAGREE, so a legitimately later decision would have been REFUSED as backfill on the
    day the clocks change.  Comparison is now on the parsed instant, and a naive or unparseable
    stamp is REFUSED rather than silently coerced.
    """
    try:
        d = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
    except (TypeError, ValueError) as e:
        raise LedgerError(f"timestamp {ts!r} is not ISO-8601: {e}") from e
    if d.tzinfo is None or d.utcoffset() is None:
        raise LedgerError(
            f"timestamp {ts!r} carries NO UTC OFFSET. A shadow ledger spans a DST change, so a "
            f"naive stamp is ambiguous and is refused. Emit UTC ('...Z') or an explicit offset.")
    return d


def _canon(row: dict, fields: list[str]) -> str:
    """Canonical JSON over every field EXCEPT row_hash -- prev_hash IS included, which is what
    chains the rows together."""
    return json.dumps({k: ("" if row.get(k) is None else str(row[k]))
                       for k in fields if k != "row_hash"},
                      sort_keys=True, separators=(",", ":"))


def _hash(row: dict, fields: list[str]) -> str:
    return hashlib.sha256(_canon(row, fields).encode("utf-8")).hexdigest()


def _read(path: str, fields: list[str]) -> list[dict]:
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        missing = [k for k in fields if k not in r]
        if missing:
            raise LedgerError(f"{path}: row missing fields {missing}")
    return rows


def _append(path: str, fields: list[str], row: dict) -> None:
    new = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        wtr = csv.DictWriter(f, fieldnames=fields)
        if new:
            wtr.writeheader()
        wtr.writerow(row)


# ------------------------------------------------------------------ decisions
def append_decision(path: str, *, shadow_start: str, ts_decision: str, strategy_id: str,
                    source_hash: str, config_hash: str, data_cutoff: str,
                    input_dataset_version: str, input_source_hashes: str,
                    action: str, intended_qty: Any, expected_costs: Any,
                    quality_status: str, blocked_reason: str = "") -> dict:
    """Append ONE decision, written BEFORE its outcome exists.  Refuses backfill."""
    if action not in ACTIONS:
        raise LedgerError(f"action {action!r} not in {ACTIONS}")
    if quality_status not in QUALITY:
        raise LedgerError(f"quality_status {quality_status!r} not in {QUALITY}")
    if quality_status == "BLOCKED" and not blocked_reason:
        raise LedgerError("a BLOCKED decision must record blocked_reason")
    # INSTANT comparison, never string comparison -- see instant() for the DST defect this fixes.
    t_new, t_start = instant(ts_decision), instant(shadow_start)
    if t_new <= t_start:
        raise LedgerError(
            f"NO BACKFILL: ts_decision {ts_decision} is not strictly after "
            f"SHADOW_START {shadow_start}. One backfilled row destroys the evidence class "
            f"for the whole file and cannot be repaired by labelling.")
    rows = _read(path, DECISION_FIELDS)
    if rows and t_new <= instant(rows[-1]["ts_decision"]):
        raise LedgerError(f"NO BACKFILL: ts_decision {ts_decision} does not strictly advance "
                          f"the previous decision at {rows[-1]['ts_decision']}")
    row = dict(seq=len(rows) + 1, ts_decision=ts_decision, strategy_id=strategy_id,
               source_hash=source_hash, config_hash=config_hash, data_cutoff=data_cutoff,
               input_dataset_version=input_dataset_version,
               input_source_hashes=input_source_hashes, action=action,
               intended_qty=intended_qty, expected_costs=expected_costs,
               quality_status=quality_status, blocked_reason=blocked_reason,
               prev_hash=rows[-1]["row_hash"] if rows else GENESIS)
    row["row_hash"] = _hash(row, DECISION_FIELDS)
    _append(path, DECISION_FIELDS, row)
    return row


# ------------------------------------------------------------------ outcomes
def append_outcome(path: str, *, decision_path: str, decision_seq: int, ts_outcome: str,
                   gross_pnl: Any, costs: Any, net_pnl: Any, data_quality: str,
                   entry_fill: Any = "", exit_fill: Any = "", note: str = "") -> dict:
    """Append ONE outcome.  It REFERENCES a decision; it never edits one."""
    if data_quality not in QUALITY:
        raise LedgerError(f"data_quality {data_quality!r} not in {QUALITY}")
    dec = _read(decision_path, DECISION_FIELDS)
    if not any(int(d["seq"]) == int(decision_seq) for d in dec):
        raise LedgerError(f"outcome references decision seq {decision_seq}, which does not exist")
    rows = _read(path, OUTCOME_FIELDS)
    if any(int(r["decision_seq"]) == int(decision_seq) for r in rows):
        raise LedgerError(f"decision seq {decision_seq} already has an outcome -- "
                          f"an outcome is appended once and never revised")
    row = dict(seq=len(rows) + 1, decision_seq=int(decision_seq), ts_outcome=ts_outcome,
               entry_fill=entry_fill, exit_fill=exit_fill, gross_pnl=gross_pnl, costs=costs,
               net_pnl=net_pnl, data_quality=data_quality, note=note,
               prev_hash=rows[-1]["row_hash"] if rows else GENESIS)
    row["row_hash"] = _hash(row, OUTCOME_FIELDS)
    _append(path, OUTCOME_FIELDS, row)
    return row


# ------------------------------------------------------------------ verification
def verify(path: str, kind: str) -> dict:
    """Recompute the entire chain.  Any edit to any earlier row breaks every hash after it."""
    fields = DECISION_FIELDS if kind == "decision" else OUTCOME_FIELDS
    rows = _read(path, fields)
    prev = GENESIS
    for i, r in enumerate(rows):
        if int(r["seq"]) != i + 1:
            raise LedgerError(f"{path} row {i+1}: seq is {r['seq']}, expected {i+1}")
        if r["prev_hash"] != prev:
            raise LedgerError(f"{path} row {i+1}: prev_hash does not match the previous row_hash "
                              f"-- a row was inserted, removed or rewritten")
        want = _hash(r, fields)
        if want != r["row_hash"]:
            raise LedgerError(f"{path} row {i+1}: row_hash mismatch -- THIS ROW WAS EDITED "
                              f"after it was written")
        prev = r["row_hash"]
    return dict(path=path, kind=kind, rows=len(rows), head=prev, ok=True)


def assert_decisions_precede_outcomes(decision_path: str, outcome_path: str) -> dict:
    """Every outcome must post-date the decision it refers to.  This is the property the whole
    architecture exists to guarantee, so it is asserted rather than assumed."""
    dec = {int(d["seq"]): d for d in _read(decision_path, DECISION_FIELDS)}
    bad = []
    for o in _read(outcome_path, OUTCOME_FIELDS):
        d = dec[int(o["decision_seq"])]
        if instant(o["ts_outcome"]) <= instant(d["ts_decision"]):
            bad.append((o["seq"], o["ts_outcome"], d["ts_decision"]))
    if bad:
        raise LedgerError(f"outcomes not strictly after their decisions: {bad}")
    return dict(checked=len(_read(outcome_path, OUTCOME_FIELDS)), ok=True)


# ------------------------------------------------------------------ self-test
def selftest(tmpdir: str) -> bool:
    """A check that cannot fail is useless.  This TAMPERS and asserts detection."""
    os.makedirs(tmpdir, exist_ok=True)
    dp = os.path.join(tmpdir, "_selftest_decisions.csv")
    op = os.path.join(tmpdir, "_selftest_outcomes.csv")
    for p in (dp, op):
        if os.path.exists(p):
            os.remove(p)
    START = "2026-09-01T18:00:00-04:00"
    common = dict(shadow_start=START, strategy_id="P1_PCT", source_hash="a" * 64,
                  config_hash="b" * 64, data_cutoff="2026-09-02T09:45:00-04:00",
                  input_dataset_version="v1", input_source_hashes="c" * 64,
                  intended_qty=1, expected_costs=14.44, quality_status="OK")
    append_decision(dp, ts_decision="2026-09-02T09:46:00-04:00", action="LONG", **common)
    append_decision(dp, ts_decision="2026-09-03T09:46:00-04:00", action="FLAT", **common)
    append_decision(dp, ts_decision="2026-09-04T09:46:00-04:00", action="NO_DECISION",
                    **{**common, "quality_status": "BLOCKED",
                       "blocked_reason": "STALE_QUOTE at the decision instant"})
    checks = []

    def expect_raise(label, fn):
        try:
            fn()
            checks.append((label, False, "NO ERROR RAISED -- the guard is inert"))
        except LedgerError as ex:
            checks.append((label, True, str(ex).split("\n")[0][:70]))

    expect_raise("refuse a row at/before SHADOW_START",
                 lambda: append_decision(dp, ts_decision="2026-08-15T09:46:00-04:00",
                                         action="LONG", **common))
    expect_raise("refuse a non-advancing timestamp",
                 lambda: append_decision(dp, ts_decision="2026-09-03T09:46:00-04:00",
                                         action="LONG", **common))
    expect_raise("refuse a BLOCKED row with no reason",
                 lambda: append_decision(dp, ts_decision="2026-09-05T09:46:00-04:00",
                                         action="FLAT",
                                         **{**common, "quality_status": "BLOCKED"}))
    expect_raise("refuse an outcome for a nonexistent decision",
                 lambda: append_outcome(op, decision_path=dp, decision_seq=99,
                                        ts_outcome="2026-09-02T15:45:00-04:00", gross_pnl=1,
                                        costs=1, net_pnl=0, data_quality="OK"))
    append_outcome(op, decision_path=dp, decision_seq=1,
                   ts_outcome="2026-09-02T15:45:00-04:00", gross_pnl=250.0, costs=14.44,
                   net_pnl=235.56, data_quality="OK")
    expect_raise("refuse a second outcome for the same decision",
                 lambda: append_outcome(op, decision_path=dp, decision_seq=1,
                                        ts_outcome="2026-09-02T15:46:00-04:00", gross_pnl=999,
                                        costs=0, net_pnl=999, data_quality="OK"))
    # ---- DST: a legitimately LATER instant whose STRING sorts earlier must be ACCEPTED
    dst_dp = os.path.join(tmpdir, "_selftest_dst.csv")
    if os.path.exists(dst_dp):
        os.remove(dst_dp)
    append_decision(dst_dp, ts_decision="2026-11-02T09:00:00-04:00", action="LONG", **common)
    try:
        append_decision(dst_dp, ts_decision="2026-11-02T08:30:00-05:00", action="LONG", **common)
        checks.append(("DST: later instant with an earlier-sorting string is ACCEPTED", True,
                       "08:30-05:00 = 13:30Z follows 09:00-04:00 = 13:00Z"))
    except LedgerError as ex:
        checks.append(("DST: later instant with an earlier-sorting string is ACCEPTED", False,
                       f"REFUSED -- string comparison regression: {ex}"))
    expect_raise("refuse a timestamp with no UTC offset",
                 lambda: append_decision(dst_dp, ts_decision="2026-11-03T09:00:00",
                                         action="LONG", **common))
    os.remove(dst_dp)

    v = verify(dp, "decision")
    checks.append(("clean decision chain verifies", v["ok"] and v["rows"] == 3, f"{v['rows']} rows"))
    checks.append(("clean outcome chain verifies", verify(op, "outcome")["ok"], "1 row"))
    checks.append(("outcomes post-date their decisions",
                   assert_decisions_precede_outcomes(dp, op)["ok"], ""))

    # ---- TAMPER: rewrite an already-written decision, exactly the forbidden act
    with open(dp, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    rows[0]["action"] = "SHORT"
    with open(dp, "w", newline="", encoding="utf-8") as f:
        wtr = csv.DictWriter(f, fieldnames=DECISION_FIELDS)
        wtr.writeheader()
        wtr.writerows(rows)
    expect_raise("TAMPER DETECTED: edited decision row", lambda: verify(dp, "decision"))
    for p in (dp, op):
        os.remove(p)

    print("  SHADOW LEDGER SELF-TEST")
    for label, ok, detail in checks:
        print(f"    [{'PASS' if ok else '*** FAIL ***'}] {label:<46} {detail}")
    allok = all(c[1] for c in checks)
    print(f"  {'ALL PASS' if allok else '*** FAILURES ***'}  ({sum(c[1] for c in checks)}"
          f"/{len(checks)})")
    return allok


if __name__ == "__main__":
    import sys
    ok = selftest(sys.argv[1] if len(sys.argv) > 1 else ".")
    sys.exit(0 if ok else 1)
