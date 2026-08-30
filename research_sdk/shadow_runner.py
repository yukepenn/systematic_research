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
  - v1 limitations (disclosed): NT8 tick times assumed machine-local ET (verified at weekly
    maintenance); one outcome per decision (first fill); P1/ABS is ledger-only and handled at
    weekly maintenance sessions, not by this runner.
"""
from __future__ import annotations
import json, os, shutil, sqlite3, sys, tempfile, traceback
from datetime import datetime, timedelta
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
    dt = datetime(1, 1, 1) + timedelta(microseconds=ticks / 10)
    return dt.replace(tzinfo=ET).isoformat(timespec="seconds")


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
                SL.append_outcome(
                    OUT, decision_path=DEC, decision_seq=seq, ts_outcome=ts,
                    gross_pnl="", costs=e["Commission"], net_pnl="",
                    data_quality="OK", entry_fill=e["Price"],
                    note=f"exec:{e['ExecutionId']} qty:{e['Quantity']} mp:{e['MarketPosition']}")
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


if __name__ == "__main__":
    try:
        sys.exit(run(dry="--dry-run" in sys.argv))
    except Exception:
        log("FATAL " + traceback.format_exc().replace("\n", " | "))
        sys.exit(1)
