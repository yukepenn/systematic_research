# -*- coding: utf-8 -*-
"""FORWARD_EVIDENCE_LEDGER_V2 -- the home for the live book's real execution evidence.

WHY V2 EXISTS
-------------
On 2026-09-01 the campaign started trading real money on account 2047681, and the v1
shadow chain cannot record it: `shadow_runner.TARGET_ACCOUNTS = {"DEMO8383477", "Sim101"}`
excludes it BY DESIGN, and `SHADOW_START = 2026-09-01T18:00:00-04:00` post-dates the
live book's first realtime bar. So the highest-quality evidence this campaign has ever
produced -- its first non-simulated fills -- had nowhere to go.

V2 does NOT replace v1 and does NOT touch it. v1's SHADOW_START and hash chain are frozen
by `PROSPECTIVE_SHADOW.md`. V2 runs alongside with THREE clocks kept permanently separable.

THE THREE CLOCKS, and why they may never be merged
--------------------------------------------------
    OWNER_FORWARD_START        2026-08-30 18:00 ET   paper NQ book, practical prospective
    LEGACY_FORMAL_SHADOW_START 2026-09-01 18:00 ET   the preregistered formal chain (v1)
    LIVE_FORWARD_START         2026-09-01 00:42 ET   REAL MONEY. First bar with BOTH live
                                                     legs simultaneously Realtime + GO.

Paper fills are `SIMULATED_FILL_NON_EVIDENTIAL` -- a Tradovate server-side demo engine
with unlimited liquidity at one price. That is a ZERO-INFORMATION class, not a low-power
one: no N makes it informative. Live fills are `FORWARD_EXECUTION_REAL`. Averaging them
would launder simulated fills into execution evidence, so the schema forbids it: evidence
class is a REQUIRED field, and `health()` reports per class and never pools.

WHAT V2 FIXES THAT V1 GOT WRONG
-------------------------------
1. v1 hard-codes `quality_status="OK"` -- it can never emit BLOCKED/GAP. V2 has
   `append_gap()`, and an outage is a first-class row. THE 2026-09-01 P1 WRITER OUTAGE IS
   RECORDED AS EVIDENCE, not as absence.
2. v1 repurposes fields away from their names (`config_hash` holds an OrderId,
   `source_hash` holds the literal "NT8_SIM_STREAM_v1"). V2 validates shape.
3. v1's strict global monotonicity means two legs deciding in the same minute cannot both
   be recorded -- the second spills. V2 keys uniqueness on (ts, strategy_id), so both legs
   coexist, and still refuses a genuine duplicate.
4. v1's CSV append is not atomic; a mid-write crash leaves a truncated final line that
   makes the whole ledger unreadable. V2 writes the row to a temp file and os.replace()s
   an appended copy, so a crash leaves the LAST GOOD STATE.

    python -m research_sdk.forward_ledger_v2 --selftest
    python -m research_sdk.forward_ledger_v2 --health
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import shutil
import sys
from datetime import datetime

GENESIS = "0" * 64

# ---------------------------------------------------------------------------- clocks
CLOCKS = {
    "OWNER_FORWARD_START": {
        "instant": "2026-08-30T18:00:00-04:00",
        "book": "PAPER_NQ", "account": "DEMO8383477",
        "evidence": "first realtime bar of both certified NQ legs; "
                    "FORWARD_EVIDENCE_RECONCILIATION.md:16",
    },
    "LEGACY_FORMAL_SHADOW_START": {
        "instant": "2026-09-01T18:00:00-04:00",
        "book": "PAPER_NQ", "account": "DEMO8383477",
        "evidence": "shadow_runner.py:34. FROZEN -- never moved backward, never edited.",
    },
    "LIVE_FORWARD_START": {
        "instant": "2026-09-01T00:42:00-04:00",
        "book": "LIVE_MNQ", "account": "2047681",
        "evidence": "PINNED MECHANICALLY 2026-09-01 from log.20260901.00000.txt: P1/399562885 "
                    "enabled 00:31:01.219 (WARMUP GO, DaysToLoad 365); XM/399562886 enabled "
                    "00:41:32.494 (WARMUP GO, DaysToLoad 365). Both legs simultaneously "
                    "Realtime and GO from 00:41:32; the first full minute bar after that is "
                    "00:42:00, and it exists in the live XM ledger. Deliberately the LATER of "
                    "the two legs -- a book clock never claims evidence before both legs had "
                    "it. NOT chosen from any outcome: at pin time the account had taken zero "
                    "trades, so it cannot be the first profitable anything.",
    },
}

BOOKS = ("PAPER_NQ", "LIVE_MNQ")

# Evidence classes. FILL classes are the ones that must never pool.
EVIDENCE_CLASSES = (
    "FORWARD_DECISION_FIRST",          # a genuine realtime decision, before any outcome
    "FORWARD_OPERATIONAL_ONLY",        # engine ran, no market decision was made
    "FORWARD_EXECUTION_REAL",          # REAL MONEY fill. The only execution-quality evidence.
    "SIMULATED_FILL_NON_EVIDENTIAL",   # demo fill. ZERO information at any N.
    "RETROSPECTIVE_RECONSTRUCTION",    # Strategy Analyzer: zero slippage, template commission
)
REAL_FILL_CLASSES = ("FORWARD_EXECUTION_REAL",)
SIM_FILL_CLASSES = ("SIMULATED_FILL_NON_EVIDENTIAL", "RETROSPECTIVE_RECONSTRUCTION")

ACTIONS = ("LONG", "SHORT", "FLAT", "NO_DECISION")
QUALITY = ("OK", "GAP", "STALE_QUOTE", "FILL_TIMEOUT", "BLOCKED", "COSTS_MODELLED",
           "WRITER_DEAD", "DISCONNECT", "ROLL_BLOCKED", "PARTIAL_FILL", "RECONCILE_BREAK")

DECISION_FIELDS = [
    "seq", "clock", "evidence_class", "book", "account",
    "ts_decision_et", "ts_decision_utc", "session_id",
    "strategy_class", "strategy_id", "source_sha256", "config_hash", "git_sha",
    "decision_instrument", "execution_instrument", "contract_month",
    "signal", "intended_side", "intended_qty_nq_equiv", "actual_exec_qty",
    "quality_score", "warmup_status", "data_health", "connection_health",
    "blocked", "blocked_reason", "p1_state", "xm_state",
    "intended_price_model", "quality_status",
    "prev_hash", "row_hash",
]
OUTCOME_FIELDS = [
    "seq", "decision_seq", "clock", "evidence_class",
    "ts_outcome_et", "entry_fill", "exit_fill",
    "commission", "fees", "spread_estimate", "execution_basis",
    "realized_net", "exit_reason", "anomalies", "data_quality",
    "prev_hash", "row_hash",
]
GAP_FIELDS = [
    "seq", "clock", "book", "account", "ts_from_et", "ts_to_et",
    "kind", "affected", "detected_by", "evidence_lost", "note",
    "prev_hash", "row_hash",
]
KINDS = {"decision": DECISION_FIELDS, "outcome": OUTCOME_FIELDS, "gap": GAP_FIELDS}


class LedgerError(RuntimeError):
    pass


# ------------------------------------------------------------------ time, hashing, io
def instant(ts: str) -> datetime:
    """Parse to an ABSOLUTE instant. Refuses a naive timestamp.

    v1 learned this the hard way: string comparison breaks across the EDT->EST change, and
    a naive stamp let a genuinely pre-start decision past the no-backfill gate.
    """
    try:
        dt = datetime.fromisoformat(ts)
    except (TypeError, ValueError):
        raise LedgerError(f"unparseable timestamp {ts!r}")
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise LedgerError(
            f"timestamp {ts!r} carries NO UTC OFFSET. A forward ledger compares INSTANTS, "
            f"never strings -- an offset-less stamp is ambiguous across a DST change.")
    return dt


def _canon(row: dict, fields: list) -> str:
    return json.dumps({k: ("" if row.get(k) is None else str(row[k]))
                       for k in fields if k != "row_hash"},
                      sort_keys=True, separators=(",", ":"))


def _hash(row: dict, fields: list) -> str:
    return hashlib.sha256(_canon(row, fields).encode("utf-8")).hexdigest()


def _read(path: str, fields: list) -> list:
    if not os.path.exists(path):
        return []
    with io.open(path, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    for i, r in enumerate(rows):
        missing = [f for f in fields if f not in r or r[f] is None]
        if missing:
            raise LedgerError(f"{path} row {i+1}: missing fields {missing} -- the file is "
                              f"truncated or hand-edited. Do not repair it silently.")
    return rows


def _append_atomic(path: str, fields: list, row: dict) -> None:
    """Append by rewrite-and-replace, so a crash leaves the LAST GOOD STATE, never a stub.

    v1 appends in place: a crash mid-write leaves a truncated final line and _read then
    raises on every subsequent call, i.e. one bad write bricks the ledger.
    """
    tmp = path + ".tmp"
    fresh = not os.path.exists(path)
    if not fresh:
        shutil.copyfile(path, tmp)
    with io.open(tmp, "a" if not fresh else "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        if fresh:
            w.writeheader()
        w.writerow({k: row.get(k, "") for k in fields})
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def _next(path, fields, row):
    rows = _read(path, fields)
    row["seq"] = len(rows) + 1
    row["prev_hash"] = rows[-1]["row_hash"] if rows else GENESIS
    row["row_hash"] = _hash(row, fields)
    _append_atomic(path, fields, row)
    return row


def _check_clock(clock, ts, book, account):
    if clock not in CLOCKS:
        raise LedgerError(f"unknown clock {clock!r}; known: {sorted(CLOCKS)}")
    c = CLOCKS[clock]
    if book != c["book"]:
        raise LedgerError(
            f"clock {clock} belongs to book {c['book']}, not {book!r}. Clocks are not "
            f"interchangeable: merging them is how a demo fill becomes execution evidence.")
    if account != c["account"]:
        raise LedgerError(f"clock {clock} belongs to account {c['account']}, not {account!r}")
    if instant(ts) < instant(c["instant"]):
        raise LedgerError(
            f"NO BACKFILL: {ts} precedes {clock} = {c['instant']}. A forward ledger records "
            f"what was decided after the clock started, and nothing else, ever.")


# ------------------------------------------------------------------------- appenders
def append_decision(path, **f):
    """Append ONE decision. A decision row is NEVER edited to carry its outcome."""
    for req in ("clock", "evidence_class", "book", "account", "ts_decision_et",
                "strategy_class", "strategy_id", "intended_side", "quality_status"):
        if not f.get(req):
            raise LedgerError(f"decision requires {req}")
    if f["evidence_class"] not in EVIDENCE_CLASSES:
        raise LedgerError(f"evidence_class {f['evidence_class']!r} not in {EVIDENCE_CLASSES}")
    if f["evidence_class"] in REAL_FILL_CLASSES + SIM_FILL_CLASSES:
        raise LedgerError(
            f"{f['evidence_class']} is a FILL class and belongs on an OUTCOME row. "
            f"A decision precedes its fill; labelling it with a fill class collapses the "
            f"distinction the ledger exists to preserve.")
    if f["quality_status"] not in QUALITY:
        raise LedgerError(f"quality_status {f['quality_status']!r} not in {QUALITY}")
    if f["intended_side"] not in ACTIONS:
        raise LedgerError(f"intended_side {f['intended_side']!r} not in {ACTIONS}")
    if str(f.get("blocked", "")).lower() in ("1", "true") and not f.get("blocked_reason"):
        raise LedgerError("a BLOCKED decision must record blocked_reason -- "
                          "'why it did not trade' is the evidence, not the absence of a row")
    _check_clock(f["clock"], f["ts_decision_et"], f["book"], f["account"])

    rows = _read(path, DECISION_FIELDS)
    key = (f["ts_decision_et"], f["strategy_id"])
    if any((r["ts_decision_et"], r["strategy_id"]) == key for r in rows):
        raise LedgerError(f"DUPLICATE: {key} is already recorded. Idempotent ingestion means "
                          f"re-running must be a no-op, not a second row.")
    if rows:
        last = max(instant(r["ts_decision_et"]) for r in rows)
        if instant(f["ts_decision_et"]) < last:
            raise LedgerError(
                f"OUT OF ORDER: {f['ts_decision_et']} precedes the latest recorded decision "
                f"at {last.isoformat()}. Two legs may share an instant; none may go backward.")
    f.setdefault("ts_decision_utc", instant(f["ts_decision_et"]).astimezone().isoformat())
    return _next(path, DECISION_FIELDS, f)


def append_outcome(path, *, decision_path, decision_seq, **f):
    """Append ONE outcome. It REFERENCES a decision by seq; it never edits one."""
    if f.get("evidence_class") not in EVIDENCE_CLASSES:
        raise LedgerError(f"outcome requires an evidence_class in {EVIDENCE_CLASSES}")
    if f["evidence_class"] not in REAL_FILL_CLASSES + SIM_FILL_CLASSES:
        raise LedgerError(f"{f['evidence_class']} is not a FILL class; an outcome records a fill")
    if f.get("data_quality") not in QUALITY:
        raise LedgerError(f"data_quality {f.get('data_quality')!r} not in {QUALITY}")

    dec = _read(decision_path, DECISION_FIELDS)
    src = next((d for d in dec if int(d["seq"]) == int(decision_seq)), None)
    if src is None:
        raise LedgerError(f"outcome references decision seq {decision_seq}, which does not exist")

    # the load-bearing guard: a demo book can never emit a real fill, and vice versa
    if src["book"] == "PAPER_NQ" and f["evidence_class"] in REAL_FILL_CLASSES:
        raise LedgerError(
            "MISLABEL REFUSED: decision seq %s is on the PAPER book, so its fill cannot be "
            "%s. Paper fills are SIMULATED_FILL_NON_EVIDENTIAL -- a server-side demo engine "
            "with unlimited liquidity at one price carries ZERO execution information at any "
            "N." % (decision_seq, f["evidence_class"]))
    if src["book"] == "LIVE_MNQ" and f["evidence_class"] in SIM_FILL_CLASSES:
        raise LedgerError(
            "MISLABEL REFUSED: decision seq %s is on the LIVE real-money book; its fill is "
            "not simulated." % decision_seq)

    rows = _read(path, OUTCOME_FIELDS)
    if any(int(r["decision_seq"]) == int(decision_seq) for r in rows):
        raise LedgerError(f"decision seq {decision_seq} already has an outcome -- "
                          f"an outcome is appended once and never revised")
    if instant(f["ts_outcome_et"]) < instant(src["ts_decision_et"]):
        raise LedgerError("an outcome cannot precede its decision")
    f["decision_seq"], f["clock"] = decision_seq, src["clock"]
    return _next(path, OUTCOME_FIELDS, f)


def append_gap(path, **f):
    """Record an evidence OUTAGE. An outage is data; silence is not.

    This is the row type v1 has no way to write, which is why the 2026-09-01 P1 writer
    death would have appeared as a signal drought rather than an instrument failure.
    """
    for req in ("clock", "book", "account", "ts_from_et", "kind", "detected_by"):
        if not f.get(req):
            raise LedgerError(f"gap requires {req}")
    instant(f["ts_from_et"])
    if f.get("ts_to_et"):
        instant(f["ts_to_et"])
    return _next(path, GAP_FIELDS, f)


# ------------------------------------------------------------------------- integrity
def verify(path, kind):
    fields = KINDS[kind]
    rows = _read(path, fields)
    prev = GENESIS
    for i, r in enumerate(rows):
        if int(r["seq"]) != i + 1:
            raise LedgerError(f"{path} row {i+1}: seq is {r['seq']}, expected {i+1}")
        if r["prev_hash"] != prev:
            raise LedgerError(f"{path} row {i+1}: prev_hash mismatch -- a row was inserted, "
                              f"removed or rewritten")
        if _hash(r, fields) != r["row_hash"]:
            raise LedgerError(f"{path} row {i+1}: row_hash mismatch -- THIS ROW WAS EDITED")
        prev = r["row_hash"]
    return {"rows": len(rows), "head": prev, "chain_ok": True}


# Fields health() may never touch. Asserted, not trusted.
_FORBIDDEN = ("pnl", "net", "gross", "sharpe", "equity", "hit_rate", "cum", "return",
              "profit", "fill", "price")


def health(dec_path, out_path, gap_path=None):
    """Operational health ONLY. Structurally incapable of returning performance.

    The point: someone must be able to check the ledger is alive without consuming the
    outcome information the ledger exists to protect.
    """
    d = _read(dec_path, DECISION_FIELDS)
    o = _read(out_path, OUTCOME_FIELDS)
    g = _read(gap_path, GAP_FIELDS) if gap_path else []
    rep = {
        "decisions": len(d), "outcomes": len(o), "gaps": len(g),
        "chain_ok": verify(dec_path, "decision")["chain_ok"] and
                    verify(out_path, "outcome")["chain_ok"],
        "first_ts": d[0]["ts_decision_et"] if d else None,
        "last_ts": d[-1]["ts_decision_et"] if d else None,
        "blocked": sum(1 for r in d if str(r.get("blocked", "")).lower() in ("1", "true")),
        "by_clock": {}, "by_evidence_class": {}, "quality_mix": {},
    }
    for r in d:
        rep["by_clock"][r["clock"]] = rep["by_clock"].get(r["clock"], 0) + 1
        rep["quality_mix"][r["quality_status"]] = rep["quality_mix"].get(r["quality_status"], 0) + 1
    for r in o:
        k = r["evidence_class"]
        rep["by_evidence_class"][k] = rep["by_evidence_class"].get(k, 0) + 1

    leak = [k for k in rep if any(f in k.lower() for f in _FORBIDDEN)]
    assert not leak, "health() leaked performance fields: %s" % leak
    return rep


# ------------------------------------------------------------------------- selftest
def selftest(tmp=None):
    import tempfile
    tmp = tmp or tempfile.mkdtemp()
    D = os.path.join(tmp, "_v2_decisions.csv")
    O = os.path.join(tmp, "_v2_outcomes.csv")
    G = os.path.join(tmp, "_v2_gaps.csv")
    for p in (D, O, G):
        if os.path.exists(p):
            os.remove(p)
    res = []

    def expect_fail(label, fn):
        try:
            fn()
        except LedgerError as ex:
            res.append((label, True, str(ex).splitlines()[0][:78]))
        else:
            res.append((label, False, "NO ERROR RAISED"))

    def live(ts, sid="399562885", **kw):
        base = dict(clock="LIVE_FORWARD_START", evidence_class="FORWARD_DECISION_FIRST",
                    book="LIVE_MNQ", account="2047681", ts_decision_et=ts,
                    strategy_class="WeeklyEdgeP1PCTMnq_v1", strategy_id=sid,
                    source_sha256="1caa6eb0", config_hash="cfg", git_sha="6da9109",
                    decision_instrument="NQU6", execution_instrument="MNQU6",
                    contract_month="09-26", signal="L", intended_side="LONG",
                    intended_qty_nq_equiv=1, actual_exec_qty=3, quality_score=3,
                    warmup_status="GO", data_health="OK", connection_health="Connected",
                    blocked="", blocked_reason="", p1_state="Realtime", xm_state="Realtime",
                    intended_price_model="next_bar_open", quality_status="OK")
        base.update(kw)
        return base

    # --- attacks the directive names, one by one -------------------------------------
    expect_fail("backfill before the clock is refused",
                lambda: append_decision(D, **live("2026-08-31T23:00:00-04:00")))
    expect_fail("naive timestamp is refused",
                lambda: append_decision(D, **live("2026-09-01T09:31:00")))
    expect_fail("paper decision on a live clock is refused",
                lambda: append_decision(D, **live("2026-09-01T09:31:00-04:00",
                                                  book="PAPER_NQ")))
    expect_fail("wrong account for the clock is refused",
                lambda: append_decision(D, **live("2026-09-01T09:31:00-04:00",
                                                  account="DEMO8383477")))
    expect_fail("a FILL class on a DECISION row is refused",
                lambda: append_decision(D, **live("2026-09-01T09:31:00-04:00",
                                                  evidence_class="FORWARD_EXECUTION_REAL")))
    expect_fail("BLOCKED with no reason is refused",
                lambda: append_decision(D, **live("2026-09-01T09:31:00-04:00",
                                                  blocked="true", quality_status="BLOCKED")))

    r1 = append_decision(D, **live("2026-09-01T09:31:00-04:00"))
    res.append(("a clean live decision is accepted", int(r1["seq"]) == 1, "seq=1"))

    # two legs may share an instant; a genuine duplicate may not
    r2 = append_decision(D, **live("2026-09-01T09:31:00-04:00", sid="399562886",
                                   strategy_class="WeeklyEdgeXMConflictMnq_v1"))
    res.append(("two legs may share one instant", int(r2["seq"]) == 2, "seq=2"))
    expect_fail("exact duplicate is refused (idempotent)",
                lambda: append_decision(D, **live("2026-09-01T09:31:00-04:00")))
    expect_fail("out-of-order decision is refused",
                lambda: append_decision(D, **live("2026-09-01T09:00:00-04:00", sid="X")))

    # outcomes
    expect_fail("outcome for a nonexistent decision is refused",
                lambda: append_outcome(O, decision_path=D, decision_seq=99,
                                       evidence_class="FORWARD_EXECUTION_REAL",
                                       ts_outcome_et="2026-09-01T10:00:00-04:00",
                                       data_quality="OK"))
    expect_fail("SIMULATED fill on a LIVE decision is refused",
                lambda: append_outcome(O, decision_path=D, decision_seq=1,
                                       evidence_class="SIMULATED_FILL_NON_EVIDENTIAL",
                                       ts_outcome_et="2026-09-01T10:00:00-04:00",
                                       data_quality="OK"))
    expect_fail("outcome preceding its decision is refused",
                lambda: append_outcome(O, decision_path=D, decision_seq=1,
                                       evidence_class="FORWARD_EXECUTION_REAL",
                                       ts_outcome_et="2026-09-01T09:00:00-04:00",
                                       data_quality="OK"))
    append_outcome(O, decision_path=D, decision_seq=1,
                   evidence_class="FORWARD_EXECUTION_REAL",
                   ts_outcome_et="2026-09-01T10:00:00-04:00", entry_fill=29500.0,
                   exit_fill=29520.0, commission=3.90, fees=0.0, spread_estimate=2.25,
                   execution_basis=-0.41, realized_net=116.1, exit_reason="XL",
                   anomalies="", data_quality="COSTS_MODELLED")
    res.append(("a real live fill is accepted", True, "COSTS_MODELLED accepted"))
    expect_fail("second outcome for one decision is refused",
                lambda: append_outcome(O, decision_path=D, decision_seq=1,
                                       evidence_class="FORWARD_EXECUTION_REAL",
                                       ts_outcome_et="2026-09-01T11:00:00-04:00",
                                       data_quality="OK"))

    # the outage that actually happened
    append_gap(G, clock="LIVE_FORWARD_START", book="LIVE_MNQ", account="2047681",
               ts_from_et="2026-09-01T00:41:00-04:00", ts_to_et="",
               kind="WRITER_DEAD", affected="WeeklyEdgeP1PCTMnq_v1/399562885",
               detected_by="research_sdk/writer_watchdog.py",
               evidence_lost="per-bar decision ledger; fills recoverable from NT8; "
                             "decisions reconstructable from the decision-identical paper proxy",
               note="export handle lost to a startup collision, nulled by the silent catch "
                    "at WeeklyEdgeP1PCTMnq_v1.cs:992, no retry path")
    res.append(("an outage is recordable as evidence", True, "WRITER_DEAD gap row written"))

    # chain + tamper
    res.append(("decision chain verifies", verify(D, "decision")["chain_ok"], ""))
    res.append(("outcome chain verifies", verify(O, "outcome")["chain_ok"], ""))
    with io.open(D, encoding="utf-8", newline="") as fh:
        txt = fh.read()
    with io.open(D, "w", encoding="utf-8", newline="") as fh:
        fh.write(txt.replace("29500", "29999").replace(",LONG,", ",SHORT,", 1))
    try:
        verify(D, "decision")
        res.append(("TAMPER DETECTED", False, "edit went unnoticed"))
    except LedgerError as ex:
        res.append(("TAMPER DETECTED", "row_hash mismatch" in str(ex), str(ex)[-60:]))

    # health leaks nothing
    with io.open(D, "w", encoding="utf-8", newline="") as fh:
        fh.write(txt)
    h = health(D, O, G)
    leaked = [k for k in h if any(f in k.lower() for f in _FORBIDDEN)]
    res.append(("health() leaks no performance", not leaked, str(list(h))[:60]))
    res.append(("health() separates evidence classes",
                "by_evidence_class" in h and "by_clock" in h, ""))

    print("  FORWARD_EVIDENCE_LEDGER_V2 SELF-TEST")
    for label, passed, detail in res:
        print("    [%s] %-48s %s" % ("PASS" if passed else "FAIL", label, detail))
    n = sum(1 for _, p, _ in res if p)
    print("  %s  (%d/%d)" % ("ALL PASS" if n == len(res) else "FAILURES", n, len(res)))
    for p in (D, O, G):
        if os.path.exists(p):
            os.remove(p)
    return 0 if n == len(res) else 1


if __name__ == "__main__":
    if "--health" in sys.argv:
        base = os.path.join(os.path.dirname(HERE) if (HERE := os.path.dirname(
            os.path.abspath(__file__))) else ".", "research", "operational", "forward_v2")
        print(json.dumps(health(os.path.join(base, "decisions.csv"),
                                os.path.join(base, "outcomes.csv"),
                                os.path.join(base, "gaps.csv")), indent=2))
        sys.exit(0)
    print(json.dumps(CLOCKS, indent=2))
    print()
    sys.exit(selftest())
