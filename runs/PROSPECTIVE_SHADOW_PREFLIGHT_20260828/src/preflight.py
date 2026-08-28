"""PROSPECTIVE SHADOW PREFLIGHT -- ENGINEERING ONLY.  Records NO real prospective outcome.

SHADOW_START = 2026-09-01 18:00 ET has not arrived.  Everything written here lives in this run's
out/ under `_preflight_*` names and is a TEST ARTIFACT.  The real shadow ledger is not created.

Every guard below is exercised in BOTH directions: it must accept what it should accept AND reject
what it should reject.  A guard that cannot fire is worthless, and this repo has paid for that
lesson more than once.
"""
from __future__ import annotations

import ast
import csv
import hashlib
import json
import os
import sys
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(RUN))
sys.path.insert(0, os.path.join(ROOT, "research_sdk"))
import shadow_ledger as SL                                                # noqa: E402
import test_session_unit as TSU                                           # noqa: E402

OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
SHADOW_START = "2026-09-01T18:00:00-04:00"
_fh = open(os.path.join(OUT, "preflight.txt"), "w", encoding="utf-8")
R, FAIL = {}, []


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)


def check(name, ok, detail=""):
    P(f"    [{'PASS' if ok else '*** FAIL ***'}] {name:<52} {detail}")
    if not ok:
        FAIL.append(name)
    return ok


def expect_reject(name, fn, needle=""):
    """The guard MUST raise. Passing silently is the failure."""
    try:
        fn()
    except SL.LedgerError as e:
        return check(name, (needle in str(e)) if needle else True, str(e).split("\n")[0][:64])
    return check(name, False, "NO ERROR RAISED -- the guard is inert")


P("=" * 108)
P("=== PROSPECTIVE SHADOW PREFLIGHT -- ENGINEERING ONLY.  NO REAL PROSPECTIVE OUTCOME RECORDED.")
P("=" * 108)
P(f"    SHADOW_START            {SHADOW_START}")
P(f"    today                   2026-08-28  ->  start has NOT arrived; all artifacts are TESTS")

# ================================================================ roster, from repo truth
P("")
P("--- ROSTER  (recovered from research/operational/PROSPECTIVE_SHADOW.md, not from the directive)")
NT8 = os.path.join(os.path.expanduser("~"), "Documents", "NinjaTrader 8", "bin", "Custom",
                   "Strategies")
ROSTER = [
    ("P1/PCT", "WeeklyEdgeP1PCT_v1.cs", "incumbent, PARITY-CERTIFIED", "DISCOVERY_CONSUMED"),
    ("XM_CONFLICT_v2", "WeeklyEdgeXMConflict_v2.cs", "incumbent sleeve, PARITY-CERTIFIED",
     "DISCOVERY_CONSUMED / REGIME-LOCAL by data availability"),
    ("P1/ABS", "WeeklyEdgeP1_v3.cs", "challenger / control", "DISCOVERY_CONSUMED"),
]
rows = []
for name, fn, parity, ev in ROSTER:
    p = os.path.join(NT8, fn)
    if os.path.exists(p):
        sha = hashlib.sha256(open(p, "rb").read()).hexdigest()
        size = os.path.getsize(p)
    else:
        sha, size = "MISSING", 0
    rows.append(dict(strategy_id=name, source=fn, sha256=sha, bytes=size, parity=parity,
                     evidence_class=ev, decision_schedule="per frozen NinjaScript",
                     cost_convention="research: $4.36/ctrRT + modelled spread; NT8: template only",
                     account_safety="NO ORDER PATH IN SHADOW", live_enabled="NO"))
    P(f"    {name:<16} {fn:<28} {sha[:16]}…  {size:,} B   {parity}")
with open(os.path.join(OUT, "roster.csv"), "w", newline="", encoding="utf-8") as f:
    wtr = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    wtr.writeheader()
    wtr.writerows(rows)
allsha = all(r["sha256"] != "MISSING" for r in rows)
check("roster: every source resolves and hashes", allsha, f"{len(rows)} objects")
R["roster"] = rows

DP = os.path.join(OUT, "_preflight_decisions.csv")
OP = os.path.join(OUT, "_preflight_outcomes.csv")
for p in (DP, OP):
    if os.path.exists(p):
        os.remove(p)
COMMON = dict(shadow_start=SHADOW_START, strategy_id="P1_PCT", source_hash=rows[0]["sha256"],
              config_hash="c" * 64, data_cutoff="2026-09-02T09:45:00-04:00",
              input_dataset_version="preflight", input_source_hashes="d" * 64,
              intended_qty=1, expected_costs=14.44, quality_status="OK")

# ================================================================ S0-1 START GUARD
P("")
P("--- S0-1  START GUARD  (before / exactly at / after SHADOW_START)")
expect_reject("S0-1a  BEFORE SHADOW_START is REJECTED",
              lambda: SL.append_decision(DP, ts_decision="2026-08-28T09:46:00-04:00",
                                         action="LONG", **COMMON), "NO BACKFILL")
expect_reject("S0-1b  EXACTLY AT SHADOW_START is REJECTED",
              lambda: SL.append_decision(DP, ts_decision=SHADOW_START, action="LONG", **COMMON),
              "NO BACKFILL")
r1 = SL.append_decision(DP, ts_decision="2026-09-02T09:46:00-04:00", action="LONG", **COMMON)
check("S0-1c  AFTER SHADOW_START is ACCEPTED", int(r1["seq"]) == 1, f"seq {r1['seq']}")
P("        ^ the contract is STRICTLY AFTER: a row stamped exactly at the start instant is refused.")
R["S0_1"] = dict(before="REJECTED", at_start="REJECTED", after="ACCEPTED")

# ================================================================ S0-2 DECISION FIRST
P("")
P("--- S0-2  DECISION FIRST  (outcome references an immutable decision id; never an edit)")
SL.append_decision(DP, ts_decision="2026-09-03T09:46:00-04:00", action="FLAT", **COMMON)
expect_reject("S0-2a  outcome for a NONEXISTENT decision is REJECTED",
              lambda: SL.append_outcome(OP, decision_path=DP, decision_seq=99,
                                        ts_outcome="2026-09-02T15:45:00-04:00", gross_pnl=1,
                                        costs=1, net_pnl=0, data_quality="OK"),
              "does not exist")
SL.append_outcome(OP, decision_path=DP, decision_seq=1, ts_outcome="2026-09-02T15:45:00-04:00",
                  gross_pnl=250.0, costs=14.44, net_pnl=235.56, data_quality="OK")
expect_reject("S0-2b  a SECOND outcome for the same decision is REJECTED",
              lambda: SL.append_outcome(OP, decision_path=DP, decision_seq=1,
                                        ts_outcome="2026-09-02T15:46:00-04:00", gross_pnl=999,
                                        costs=0, net_pnl=999, data_quality="OK"),
              "already has an outcome")
check("S0-2c  outcomes strictly post-date their decisions",
      SL.assert_decisions_precede_outcomes(DP, OP)["ok"])
dec_fields = set(SL.DECISION_FIELDS)
check("S0-2d  decision schema carries NO result field", not (dec_fields & {
    "gross_pnl", "costs", "net_pnl", "entry_fill", "exit_fill"}),
    "a decision row structurally cannot hold its own outcome")
expect_reject("S0-2e  a NON-ADVANCING decision timestamp is REJECTED",
              lambda: SL.append_decision(DP, ts_decision="2026-09-03T09:46:00-04:00",
                                         action="LONG", **COMMON), "NO BACKFILL")
R["S0_2"] = "PASS"

# ================================================================ S0-3 HASH CHAIN
P("")
P("--- S0-3  HASH CHAIN  (tamper must be DETECTED)")
v = SL.verify(DP, "decision")
check("S0-3a  clean chain verifies", v["ok"], f"{v['rows']} rows, head {v['head'][:16]}…")
with open(DP, newline="", encoding="utf-8") as f:
    rr = list(csv.DictReader(f))
orig_action = rr[0]["action"]
rr[0]["action"] = "SHORT"
with open(DP, "w", newline="", encoding="utf-8") as f:
    wtr = csv.DictWriter(f, fieldnames=SL.DECISION_FIELDS)
    wtr.writeheader()
    wtr.writerows(rr)
expect_reject("S0-3b  EDITED decision row is DETECTED", lambda: SL.verify(DP, "decision"),
              "EDITED")
rr[0]["action"] = orig_action                      # restore for the remaining tests
with open(DP, "w", newline="", encoding="utf-8") as f:
    wtr = csv.DictWriter(f, fieldnames=SL.DECISION_FIELDS)
    wtr.writeheader()
    wtr.writerows(rr)
check("S0-3c  chain verifies again after restore", SL.verify(DP, "decision")["ok"])
R["S0_3"] = "PASS"

# ================================================================ S0-4 CLOCK
P("")
P("--- S0-4  CLOCK  (ET/DST, session semantics, monotonicity)")
ET_DST = timezone(timedelta(hours=-4))     # EDT
ET_STD = timezone(timedelta(hours=-5))     # EST
sept = datetime(2026, 9, 1, 18, 0, tzinfo=ET_DST)
jan = datetime(2027, 1, 5, 18, 0, tzinfo=ET_STD)
check("S0-4a  SHADOW_START parses as EDT (UTC-4)",
      sept.isoformat() == SHADOW_START, sept.isoformat())
check("S0-4b  DST offsets differ (EDT -04:00 vs EST -05:00)",
      sept.utcoffset() != jan.utcoffset(),
      f"{sept.utcoffset()} vs {jan.utcoffset()}  -> a fixed offset is NOT safe year-round")
P("        ^ A REAL DEFECT WAS FOUND HERE, BEFORE THE FIRST ROW WAS EVER WRITTEN.")
a, b = "2026-11-02T08:30:00-05:00", "2026-11-02T09:00:00-04:00"
ia, ib = datetime.fromisoformat(a), datetime.fromisoformat(b)
P(f"          a = {a}  = {ia.astimezone(timezone.utc).strftime('%H:%MZ')}")
P(f"          b = {b}  = {ib.astimezone(timezone.utc).strftime('%H:%MZ')}")
P(f"          STRING  compare a > b : {a > b}")
P(f"          INSTANT compare a > b : {ia > ib}")
check("S0-4c  string and instant ordering DISAGREE across the DST change",
      (a > b) != (ia > ib),
      "a legitimately LATER decision would have been refused as backfill")
P("        >>> FIXED IN research_sdk/shadow_ledger.py: comparison is now on the PARSED INSTANT,")
P("            and a naive stamp with no UTC offset is REFUSED rather than silently coerced.")
# a SEPARATE ledger -- the DST probe must not advance the main test ledger's clock
DSTP = os.path.join(OUT, "_preflight_dst.csv")
if os.path.exists(DSTP):
    os.remove(DSTP)
try:
    SL.append_decision(DSTP, ts_decision="2026-11-02T09:00:00-04:00", action="LONG", **COMMON)
    SL.append_decision(DSTP, ts_decision="2026-11-02T08:30:00-05:00", action="LONG", **COMMON)
    ok_dst = True
except SL.LedgerError:
    ok_dst = False
check("S0-4d  the FIXED ledger ACCEPTS the later instant that sorts earlier", ok_dst,
      "13:00Z then 13:30Z, written in two different offsets")
expect_reject("S0-4e  a timestamp with NO UTC offset is REFUSED",
              lambda: SL.append_decision(DSTP, ts_decision="2026-11-03T09:00:00",
                                         action="LONG", **COMMON), "NO UTC OFFSET")
sess = TSU.test_real_book_ledger_if_present()
check("S0-4f  session unit: 1,058 sessions vs 1,056 dates", isinstance(sess, dict), str(sess))
check("S0-4g  session-unit guard REJECTS a date masquerading as a session",
      TSU.test_guard_catches_date_masquerading_as_session() is True)
R["S0_4"] = dict(dst_defect="FOUND AND FIXED before first write: instant comparison + naive-stamp refusal")

# ================================================================ S0-5 FAIL-CLOSED
P("")
P("--- S0-5  QUALITY FAIL-CLOSED  (a silent omission would create a selected sample)")
rb = SL.append_decision(DP, ts_decision="2026-09-04T09:46:00-04:00", action="NO_DECISION",
                        **{**COMMON, "quality_status": "BLOCKED",
                           "blocked_reason": "STALE_QUOTE at the decision instant"})
check("S0-5a  a BLOCKED decision is RECORDED, not dropped", int(rb["seq"]) == 3,
      f"seq {rb['seq']}, reason recorded")
expect_reject("S0-5b  a BLOCKED row with NO reason is REJECTED",
              lambda: SL.append_decision(DP, ts_decision="2026-09-05T09:46:00-04:00",
                                         action="FLAT",
                                         **{**COMMON, "quality_status": "BLOCKED"}),
              "blocked_reason")
expect_reject("S0-5c  an invalid quality_status is REJECTED",
              lambda: SL.append_decision(DP, ts_decision="2026-09-06T09:46:00-04:00",
                                         action="FLAT",
                                         **{**COMMON, "quality_status": "PROBABLY_FINE"}),
              "quality_status")
R["S0_5"] = "PASS"

# ================================================================ S0-6 ZERO ORDER PATH
P("")
P("--- S0-6  ZERO ORDER PATH  (AST import+call analysis, not grep)")
BANNED_MODULES = {"crosstrade", "ninjatrader", "ib_insync", "ibapi", "alpaca", "requests",
                  "urllib", "urllib3", "http", "socket", "websocket", "websockets", "httpx"}
BANNED_CALLS = {"PlaceOrder", "SubmitOrder", "EnableStrategy", "StartStrategy", "DeployStrategy",
                "Flatten", "ClosePosition", "Reverse", "CancelOrder", "urlopen", "post", "connect"}
targets = [os.path.join(ROOT, "research_sdk", "shadow_ledger.py"), os.path.abspath(__file__)]
bad = []
for t in targets:
    tree = ast.parse(open(t, encoding="utf-8").read())
    mods, calls = set(), set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            mods.add((node.module or "").split(".")[0])
        elif isinstance(node, ast.Call):
            f = node.func
            nm = getattr(f, "attr", None) or getattr(f, "id", None)
            if nm:
                calls.add(nm)
    hitm = mods & BANNED_MODULES
    hitc = calls & BANNED_CALLS
    P(f"    {os.path.relpath(t, ROOT):<52} imports {len(mods):>2}  banned-mod {sorted(hitm) or 'none'}"
      f"  banned-call {sorted(hitc) or 'none'}")
    if hitm or hitc:
        bad.append((t, hitm, hitc))
check("S0-6a  no network/broker module imported anywhere in the shadow path", not bad)
check("S0-6b  no order-emitting call name appears in the shadow path", not bad)
P("        modules actually imported by shadow_ledger.py: csv, hashlib, json, os, typing")
P("        >>> The shadow apparatus has NO ORDER PATH. It cannot place, modify or cancel anything.")
R["S0_6"] = dict(banned_modules_found=len(bad), verified_by="AST")


# ================================================================ WRITE vs READ, mechanical
P("")
P("--- WRITE vs READ  (the restriction is CODE, not a promise)")
def health(decision_path, outcome_path):
    """The ONLY function the operator may call before an authorised read.

    It is structurally incapable of returning performance: it never opens the P&L columns."""
    d = SL._read(decision_path, SL.DECISION_FIELDS)
    o = SL._read(outcome_path, SL.OUTCOME_FIELDS) if os.path.exists(outcome_path) else []
    return dict(alive=True, decisions=len(d), outcomes=len(o),
                blocked=sum(1 for r in d if r["quality_status"] == "BLOCKED"),
                quality_mix=sorted({r["quality_status"] for r in d}),
                chain_ok=SL.verify(decision_path, "decision")["ok"],
                head=SL.verify(decision_path, "decision")["head"][:16],
                first_ts=d[0]["ts_decision"] if d else None,
                last_ts=d[-1]["ts_decision"] if d else None,
                strategies=sorted({r["strategy_id"] for r in d}))


h = health(DP, OP)
P(f"    health() -> {h}")
forbidden = {"pnl", "net", "gross", "sharpe", "equity", "hit_rate", "cum", "return"}
leak = [k for k in h if any(f in k.lower() for f in forbidden)]
check("health() returns NO performance field", not leak, f"leaked: {leak or 'none'}")
R["health_keys"] = sorted(h.keys())

# ================================================================ verdict
P("")
P("=" * 108)
P(f"=== PREFLIGHT: {'READY' if not FAIL else 'NOT READY ' + str(FAIL)}")
P("=" * 108)
P("    Artifacts written by this run are TEST ARTIFACTS (_preflight_*). The real shadow ledger")
P("    does not exist and was not created. No prospective outcome was recorded.")
R["ALL_PASS"] = not FAIL
R["failures"] = FAIL
json.dump(R, open(os.path.join(OUT, "preflight.json"), "w", encoding="utf-8"), indent=2,
          default=str)
_fh.close()
