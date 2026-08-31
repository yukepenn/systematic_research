"""GENESIS shadow runner v1 — EOD ingestion of NT8 sim order/execution stream into the
hash-chained shadow ledger. Owner-authorized 2026-08-30 (research/operational/OWNER_DECISION_20260830.md).

DESIGN (amended protocol, see PROSPECTIVE_SHADOW.md 2026-08-30 block):
  - The decision-first property is carried by NT8's OWN platform timestamps (an order exists
    before its fill); this runner seals them into the append-only ledger once per day.
  - EMITS NO ORDERS. Reads a COPY of NinjaTrader.sqlite; writes only ledger/state/log files.
  - Target accounts: paper only (DEMO8383477, Sim101) — resolved by NAME each run; anything
    else is never ingested. There is no code path that touches a live account.
  - Rows the strict ledger refuses (same-second collisions, pre-start activity, partial fills
    beyond the first) go to a SPILLOVER file — recorded, never lost, never backfilled.
  - v2 (2026-08-31) FIXED TWO DEFECTS FOUND BEFORE THE LEDGER'S FIRST ROW — see ticks_to_iso and
    exec_costs for the evidence. Both were caught by the MASTER DIRECTIVE re-underwriting while
    decisions.csv/outcomes.csv did not yet exist, so no hash chain was harmed. Had they shipped,
    every row would have been 4-5 h mis-stamped (crossing session boundaries and able to admit
    pre-SHADOW_START activity past the no-backfill gate) and every row would have claimed $0.00 costs.
    ⚠️ v1's disclosed limitation "NT8 tick times assumed machine-local ET (verified at weekly
    maintenance)" is now DISPROVEN: they are UTC. The stated verification had never been performed.
  - remaining v2 limitations (disclosed): one outcome per decision (first fill); P1/ABS is
    ledger-only and handled at weekly maintenance, not by this runner; commission is MODELLED at the
    certified $4.36/ctrRT whenever the platform reports 0.0, and such rows carry
    data_quality=COSTS_MODELLED so a modelled cost can never be read as a measured one.
"""
from __future__ import annotations
import json, os, shutil, sqlite3, sys, tempfile, traceback
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "research_sdk"))
import shadow_ledger as SL  # noqa: E402

ET = ZoneInfo("America/New_York")
SHADOW_START = "2026-09-01T18:00:00-04:00"
TARGET_ACCOUNTS = {"DEMO8383477", "Sim101"}          # paper only, by explicit owner decision
NT8_DB = os.path.join(os.path.expanduser("~"), "Documents", "NinjaTrader 8", "db", "NinjaTrader.sqlite")
OUTDIR = os.path.join(REPO, "research", "operational", "shadow")
DEC, OUT = os.path.join(OUTDIR, "decisions.csv"), os.path.join(OUTDIR, "outcomes.csv")
STATE, SPILL = os.path.join(OUTDIR, "runner_state.json"), os.path.join(OUTDIR, "spillover.jsonl")
LOG = os.path.join(OUTDIR, "runner.log")

ACTION_MAP = {"Buy": "LONG", "BuyToCover": "LONG", "Sell": "SHORT", "SellShort": "SHORT"}


def log(msg: str) -> None:
    os.makedirs(OUTDIR, exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now(ET).isoformat(timespec='seconds')} {msg}\n")


def ticks_to_iso(ticks: int) -> str:
    """NT8 stores .NET ticks in **UTC**.  CONVERT, never relabel.

    ⚠️ v1 did ``dt.replace(tzinfo=ET)``, which LABELS a naive UTC value as ET and lands every row
    4-5 hours late.  DISPROVEN EMPIRICALLY 2026-08-31 against the first live round trip:
    Orders.Id=585 ticks 639237490803930000 -> naive 2026-08-31 04:58:00.393, while NT8's own log and
    order record put that fill at 00:58:00.393 ET.  Exactly 4 h, sub-second parts identical.
    Not cosmetic: it crosses date AND session boundaries, and it could ADMIT a genuinely
    pre-SHADOW_START decision past the no-backfill gate (a real 14:05 ET decision would be
    relabelled 18:05 ET and accepted).  Caught before the ledger's first row, so no chain was harmed.
    """
    dt = datetime(1, 1, 1, tzinfo=timezone.utc) + timedelta(microseconds=ticks / 10)
    return dt.astimezone(ET).isoformat(timespec="seconds")


# Certified research cost model: "NinjaTrader Brokerage Lifetime", $4.36 per contract ROUND TURN.
# One execution is ONE SIDE, so a side costs half that per contract.
COMMISSION_PER_CONTRACT_SIDE = 4.36 / 2.0


def exec_costs(e) -> tuple[float, str]:
    """Return (costs, data_quality) for one execution.

    ⚠️ This broker/account records **Commission = 0.0 and Fee = 0.0 on every row**, and the Orders
    table has no Commission column at all — verified 2026-08-31 across the two live executions
    (Id 853/854) where $8.72 was in fact charged.  v1 passed ``e["Commission"]`` straight through, so
    every outcome row would have claimed **$0.00 costs** and the ledger could never have supported an
    after-cost claim — the one thing it exists to support.

    Never silently record zero.  Use the observed value when the platform actually supplies one;
    otherwise fall back to the certified rate and SAY SO in data_quality, so no reader can ever
    mistake a modelled cost for a measured one.
    """
    observed = float(e["Commission"] or 0.0) + float(e["Fee"] or 0.0)
    if observed > 0.0:
        return observed, "OK"
    qty = abs(int(e["Quantity"] or 0))
    return qty * COMMISSION_PER_CONTRACT_SIDE, "COSTS_MODELLED"


def spill(kind: str, row: dict, reason: str) -> None:
    with open(SPILL, "a", encoding="utf-8") as f:
        f.write(json.dumps({"kind": kind, "reason": reason, "row": row}, default=str) + "\n")


def load_state() -> dict:
    if os.path.exists(STATE):
        return json.load(open(STATE, encoding="utf-8"))
    return {"last_order_id": None, "last_exec_id": None, "order_seq": {}}


def save_state(s: dict) -> None:
    tmp = STATE + ".tmp"
    json.dump(s, open(tmp, "w", encoding="utf-8"), indent=1)
    os.replace(tmp, STATE)


def run(dry: bool = False) -> int:
    os.makedirs(OUTDIR, exist_ok=True)
    st = load_state()
    tmp = os.path.join(tempfile.gettempdir(), "nt8_shadow_ro.sqlite")
    shutil.copy2(NT8_DB, tmp)                    # read a copy; never the live file
    con = sqlite3.connect(f"file:{tmp}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    accts = {r["Id"]: r["Name"] for r in con.execute("SELECT Id, Name FROM Accounts")}
    target_ids = {i for i, n in accts.items() if n in TARGET_ACCOUNTS}
    if not target_ids:
        log("ERROR: no target paper account found in Accounts table; nothing ingested")
        return 1
    # first run: watermark to CURRENT max ids so historical/manual rows are never ingested
    if st["last_order_id"] is None:
        st["last_order_id"] = con.execute("SELECT COALESCE(MAX(Id),0) FROM Orders").fetchone()[0]
        st["last_exec_id"] = con.execute("SELECT COALESCE(MAX(Id),0) FROM Executions").fetchone()[0]
        save_state(st)
        log(f"INIT watermarks orders={st['last_order_id']} execs={st['last_exec_id']} "
            f"targets={sorted(accts[i] for i in target_ids)}")
        return 0

    n_dec = n_out = n_sp = 0
    orders = list(con.execute(
        "SELECT * FROM Orders WHERE Id > ? ORDER BY Time, Id", (st["last_order_id"],)))
    for o in orders:
        if o["Account"] not in target_ids:
            st["last_order_id"] = max(st["last_order_id"], o["Id"]); continue
        ts = ticks_to_iso(o["Time"])
        action = ACTION_MAP.get(str(o["OrderAction"]), "NO_DECISION")
        row = {k: o[k] for k in o.keys()}
        if dry:
            print("DEC?", ts, accts[o["Account"]], o["Name"], action, o["Quantity"])
        else:
            try:
                d = SL.append_decision(
                    DEC, shadow_start=SHADOW_START, ts_decision=ts,
                    strategy_id=f"SIM:{accts[o['Account']]}:{o['Name'] or 'unnamed'}",
                    source_hash="NT8_SIM_STREAM_v1", config_hash=str(o["OrderId"]),
                    data_cutoff=ts, input_dataset_version="nt8_sqlite",
                    input_source_hashes=f"order:{o['OrderId']}|type:{o['OrderType']}|state:{o['OrderState']}",
                    action=action, intended_qty=o["Quantity"], expected_costs="nt8_template",
                    quality_status="OK")
                st["order_seq"][str(o["OrderId"])] = d["seq"]; n_dec += 1
            except SL.LedgerError as e:
                spill("order", row, str(e)); n_sp += 1
        st["last_order_id"] = max(st["last_order_id"], o["Id"])
        if not dry:
            save_state(st)

    execs = list(con.execute(
        "SELECT * FROM Executions WHERE Id > ? ORDER BY Time, Id", (st["last_exec_id"],)))
    for e in execs:
        if e["Account"] not in target_ids:
            st["last_exec_id"] = max(st["last_exec_id"], e["Id"]); continue
        ts = ticks_to_iso(e["Time"])
        row = {k: e[k] for k in e.keys()}
        seq = st["order_seq"].get(str(e["OrderId"]))
        if dry:
            print("OUT?", ts, accts[e["Account"]], e["Price"], "->seq", seq)
        elif seq is None:
            spill("execution", row, "no ledger decision for OrderId (manual trade or pre-start)")
            n_sp += 1
        else:
            try:
                costs, dq = exec_costs(e)
                SL.append_outcome(
                    OUT, decision_path=DEC, decision_seq=seq, ts_outcome=ts,
                    gross_pnl="", costs=costs, net_pnl="",
                    data_quality=dq, entry_fill=e["Price"],
                    note=f"exec:{e['ExecutionId']} qty:{e['Quantity']} mp:{e['MarketPosition']}"
                         f" comm_src:{'observed' if dq == 'OK' else 'modelled@4.36ctrRT'}")
                n_out += 1
            except SL.LedgerError as err:
                spill("execution", row, str(err)); n_sp += 1
        st["last_exec_id"] = max(st["last_exec_id"], e["Id"])
        if not dry:
            save_state(st)

    if not dry and os.path.exists(DEC):
        v1 = SL.verify(DEC, "decision")
        v2 = SL.verify(OUT, "outcome") if os.path.exists(OUT) else {"rows": 0}
        log(f"RUN decisions+{n_dec} outcomes+{n_out} spill+{n_sp} "
            f"verify dec={v1['rows']} out={v2['rows']} OK")
    elif not dry:
        log(f"RUN nothing new (spill+{n_sp})")
    return 0


def selftest() -> int:
    """Prove both v2 guards FIRE. Anchored on the first live round trip, not on invented data."""
    ok = fail = 0

    def check(name, got, want):
        nonlocal ok, fail
        if got == want:
            ok += 1; print(f"  PASS {name}")
        else:
            fail += 1; print(f"  FAIL {name}\n       got  {got!r}\n       want {want!r}")

    # --- Anchors: the two real executions of 2026-08-31, cross-checked against NT8's own log ---
    ENTRY_TICKS, EXIT_TICKS = 639237490803930000, 639237594601380000
    print("ticks_to_iso — UTC must be CONVERTED, not relabelled")
    check("entry -> 00:58 ET", ticks_to_iso(ENTRY_TICKS), "2026-08-31T00:58:00-04:00")
    check("exit  -> 03:51 ET", ticks_to_iso(EXIT_TICKS),  "2026-08-31T03:51:00-04:00")

    # teeth: the v1 formula must be demonstrably WRONG on the same input
    v1 = (datetime(1, 1, 1) + timedelta(microseconds=ENTRY_TICKS / 10)).replace(
        tzinfo=ET).isoformat(timespec="seconds")
    check("v1 formula is wrong (guard has teeth)", v1 != ticks_to_iso(ENTRY_TICKS), True)
    check("v1 error is exactly +4h", v1, "2026-08-31T04:58:00-04:00")

    # teeth: v1 would ADMIT a genuinely pre-SHADOW_START decision past the no-backfill gate
    start = datetime.fromisoformat(SHADOW_START)
    real_et = datetime(2026, 9, 1, 14, 5, tzinfo=ET)                    # 14:05 ET, BEFORE 18:00 start
    ticks_utc = int((real_et.astimezone(timezone.utc)
                     - datetime(1, 1, 1, tzinfo=timezone.utc)).total_seconds() * 1e7)
    check("v2 REFUSES the 14:05 ET decision",
          datetime.fromisoformat(ticks_to_iso(ticks_utc)) <= start, True)
    v1_stamp = (datetime(1, 1, 1) + timedelta(microseconds=ticks_utc / 10)).replace(tzinfo=ET)
    check("v1 would have ADMITTED it (the backfill hole)", v1_stamp > start, True)

    print("exec_costs — never silently record $0.00")
    check("zero-commission row -> modelled", exec_costs(
        {"Commission": 0.0, "Fee": 0.0, "Quantity": 2}), (4.36, "COSTS_MODELLED"))
    check("observed commission wins", exec_costs(
        {"Commission": 8.72, "Fee": 0.0, "Quantity": 2}), (8.72, "OK"))
    check("Fee counts as observed", exec_costs(
        {"Commission": 0.0, "Fee": 1.25, "Quantity": 2}), (1.25, "OK"))
    check("modelled matches the certified $4.36/ctrRT round turn",
          round(exec_costs({"Commission": 0, "Fee": 0, "Quantity": 2})[0] * 2, 2), 8.72)

    print(f"\nselftest {ok}/{ok + fail}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    try:
        sys.exit(run(dry="--dry-run" in sys.argv))
    except Exception:
        log("FATAL " + traceback.format_exc().replace("\n", " | "))
        sys.exit(1)
