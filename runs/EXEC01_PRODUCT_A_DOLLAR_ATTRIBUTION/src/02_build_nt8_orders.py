"""EXEC01 step 2 -- reconstruct NT8-side ORDER-level (not Trade/FIFO-slice-level) events for
Product A, for the 9 selected periods, from already-on-disk NT8 output only. No new NT8 job run.

Why order-level, not Trade-level: NT8's own "Trades" list FIFO-matches entry lots against exit
lots, so a single real order (e.g. "buy 3 to scale in") can be split across MULTIPLE Trade
records if it gets closed out in pieces by different later exits (verified empirically below --
see docstring in build_rich_orders()). Order-level reconstruction collapses these FIFO splits
back to the actual fill NT8 placed, which is the correct unit to compare against Python's
one-order-per-bar-transition event log (python_orders_periods.csv from step 1).

Two NT8 source formats in play:
  RICH  (producta_v4_2024apr_2025mar.json, periods P3-P6): full Trade objects with explicit
        entry.order_id / exit.order_id / entry.quantity / exit.quantity / entry.commission /
        exit.commission -- order-level fields are already explicit on every Trade record (repeated
        identically across every FIFO-split sharing that order_id). Dedup by order_id recovers the
        exact original order.
  CHUNK (A_E{1,3,5,6,7}_trades.json, periods P1/P2/P7/P8/P9): round-trip Trade records only
        (entry_t, exit_t, entry_px, exit_px, side, pnl, comm) -- no order_id, no explicit quantity.
        Per 00_period_selection.md (verified exact against the RICH overlap window, not re-derived
        here): quantity_of_this_FIFO_slice = comm / 0.65 / 2 (MNQ Lifetime commission, $0.65/side).
        Order-level reconstruction: group Trade records by (entry_t, entry_px, side) and SUM the
        inferred slice quantities to recover the entry order's total size (mirrors what RICH's
        entry.quantity already gives directly); same for (exit_t, exit_px, opposite side) -> exit
        order size. This is valid because a single order fills at ONE price at ONE bar (verified
        directly in the RICH job: every entry.quantity/entry.price pair is IDENTICAL across all
        Trade records sharing that entry.order_id).

Both entry-side and exit-side order events are then combined: NT8 represents a same-bar REVERSAL
as TWO separate order objects sharing an identical (time, price) -- one exit order (closing the
old side) and one entry order (opening the new, opposite side) -- confirmed empirically below by
inspecting the RICH job's own same-timestamp order pairs. These are merged into ONE combined order
per (time, price) group (side must be uniform within the group; asserted) so the NT8 side has the
same one-order-per-decision-event granularity as the Python side.
"""
import json, os, sys
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
V1R4_OUT = os.path.join(ROOT, "runs", "V1R4_NT8_PARITY", "out")
OUT = os.path.join(ROOT, "runs", "EXEC01_PRODUCT_A_DOLLAR_ATTRIBUTION", "out")
os.makedirs(OUT, exist_ok=True)

COMM_MNQ_A = 0.65
BUY_ACTIONS = ("Buy", "BuyToCover")


def side_of(action):
    return 1 if action in BUY_ACTIONS else -1


def build_rich_orders(json_path, win_start=None, win_end=None):
    """Extract order-level events from a RICH (explicit-Quantity) NT8 trades JSON by dedup on
    order_id. Optionally pre-filter by time window (perf only)."""
    d = json.load(open(json_path, encoding="utf-8"))
    trades = d["trades"]
    entries, exits = {}, {}
    for tr in trades:
        e, x = tr["entry"], tr["exit"]
        et = pd.Timestamp(e["time"])
        if win_start is not None and not (win_start - pd.Timedelta(days=1) <= et <= win_end + pd.Timedelta(days=1)):
            continue
        entries[e["order_id"]] = e
        xt = pd.Timestamp(x["time"])
        exits[x["order_id"]] = x
    rows = []
    for oid, e in entries.items():
        rows.append({"order_id": oid, "time": pd.Timestamp(e["time"]), "price": e["price"],
                     "side": side_of(e["order_action"]), "qty": e["quantity"], "comm": e["commission"],
                     "leg_kind": "entry", "name": e["name"]})
    for oid, x in exits.items():
        rows.append({"order_id": oid, "time": pd.Timestamp(x["time"]), "price": x["price"],
                     "side": side_of(x["order_action"]), "qty": x["quantity"], "comm": x["commission"],
                     "leg_kind": "exit", "name": x["name"]})
    raw = pd.DataFrame(rows).drop_duplicates(subset=["order_id"]).reset_index(drop=True)
    return raw


def build_chunk_orders(json_path, win_start, win_end):
    """Extract order-level events from a CHUNK (comm-inferred-quantity) NT8 trades JSON by
    grouping FIFO slices back to (entry_t, entry_px, side) / (exit_t, exit_px, -side)."""
    trs = json.load(open(json_path, encoding="utf-8"))
    df = pd.DataFrame(trs)
    df["entry_t"] = pd.to_datetime(df["entry_t"])
    df["exit_t"] = pd.to_datetime(df["exit_t"])
    m = (df["entry_t"] >= win_start - pd.Timedelta(days=2)) & (df["entry_t"] <= win_end + pd.Timedelta(days=2)) | \
        (df["exit_t"] >= win_start - pd.Timedelta(days=2)) & (df["exit_t"] <= win_end + pd.Timedelta(days=2))
    df = df.loc[m].copy()
    df["entry_side"] = df["side"].map({"Buy": 1, "SellShort": -1})
    df["qty_slice"] = (df["comm"] / COMM_MNQ_A / 2.0).round().astype(int)
    # sanity: comm should be an exact multiple of COMM_MNQ_A*2 (verified exact per 00_period_selection.md)
    resid = (df["comm"] - df["qty_slice"] * COMM_MNQ_A * 2.0).abs()
    assert resid.max() < 1e-6, f"comm-inference not exact, max residual {resid.max()}"

    entry_g = df.groupby(["entry_t", "entry_px", "entry_side"])["qty_slice"].sum().reset_index()
    entry_g = entry_g.rename(columns={"entry_t": "time", "entry_px": "price", "entry_side": "side", "qty_slice": "qty"})
    entry_g["comm"] = entry_g["qty"] * COMM_MNQ_A
    entry_g["order_id"] = "CHUNK_ENTRY_" + entry_g["time"].astype(str) + "_" + entry_g["price"].astype(str) + "_" + entry_g["side"].astype(str)
    entry_g["leg_kind"] = "entry"
    entry_g["name"] = np.where(entry_g["side"] > 0, "L", "S")

    df["exit_side"] = -df["entry_side"]
    exit_g = df.groupby(["exit_t", "exit_px", "exit_side"])["qty_slice"].sum().reset_index()
    exit_g = exit_g.rename(columns={"exit_t": "time", "exit_px": "price", "exit_side": "side", "qty_slice": "qty"})
    exit_g["comm"] = exit_g["qty"] * COMM_MNQ_A
    exit_g["order_id"] = "CHUNK_EXIT_" + exit_g["time"].astype(str) + "_" + exit_g["price"].astype(str) + "_" + exit_g["side"].astype(str)
    exit_g["leg_kind"] = "exit"
    exit_g["name"] = "Close/Exit"

    raw = pd.concat([entry_g, exit_g], ignore_index=True, sort=False)
    return raw[["order_id", "time", "price", "side", "qty", "comm", "leg_kind", "name"]]


def combine_same_bar(raw):
    """Combine entry+exit legs sharing an identical (time, price) -- NT8's representation of a
    same-bar reversal as two separate orders -- into ONE order-level event per (time, price)."""
    g = raw.groupby(["time", "price"])
    rows = []
    for (t, px), sub in g:
        sides = sub["side"].unique()
        # same-bar entry+exit pair from a reversal always pushes the SAME direction (both legs are
        # market orders in the direction the position is moving); assert this rather than assume it.
        assert len(sides) == 1, (
            f"same-bar (time={t}, price={px}) group has MIXED side signs {sides} -- "
            f"unexpected, needs manual inspection:\n{sub}")
        rows.append({
            "time": t, "price": px, "side": int(sides[0]), "qty": int(sub["qty"].sum()),
            "comm": float(sub["comm"].sum()), "n_legs_combined": len(sub),
            "leg_kinds": "+".join(sorted(sub["leg_kind"].unique())),
            "order_ids": ";".join(sub["order_id"].astype(str)),
        })
    out = pd.DataFrame(rows).sort_values("time").reset_index(drop=True)
    return out


RICH_PATH = os.path.join(V1R4_OUT, "producta_v4_2024apr_2025mar.json")
CHUNK_PATHS = {
    "E1": os.path.join(V1R4_OUT, "chunks", "A_E1_trades.json"),
    "E3": os.path.join(V1R4_OUT, "chunks", "A_E3_trades.json"),
    "E5": os.path.join(V1R4_OUT, "chunks", "A_E5_trades.json"),
    "E6": os.path.join(V1R4_OUT, "chunks", "A_E6_trades.json"),
    "E7": os.path.join(V1R4_OUT, "chunks", "A_E7_trades.json"),
}

# bar-time -> sess_date lookup (built by step 01 from the SAME health_substrate bars table the
# Python side uses to bucket by TRADING SESSION, not calendar date -- required because a session
# starting 18:00 ET on day D-1 is dated D; a bare calendar-midnight filter on order timestamps
# would wrongly drop the evening bars of every session's first few hours). Exact-match lookup:
# NT8 order timestamps always coincide with a 3-min bar's own open time (verified empirically),
# so this is not an approximation.
lookup_df = pd.read_csv(os.path.join(OUT, "bar_time_to_sess_date.csv"), parse_dates=["time"])
time_to_sess = dict(zip(lookup_df["time"], lookup_df["sess_date"]))


def attach_sess_date(df):
    df = df.copy()
    sess = df["time"].map(time_to_sess)
    n_missing = sess.isna().sum()
    if n_missing:
        # fallback: nearest bar time within 2 minutes (should be rare/never)
        lookup_sorted = lookup_df.sort_values("time")
        for idx in df.index[sess.isna()]:
            t = df.loc[idx, "time"]
            pos = lookup_sorted["time"].searchsorted(t)
            cand = lookup_sorted.iloc[max(0, pos - 1):pos + 1]
            if len(cand):
                nearest = cand.iloc[(cand["time"] - t).abs().values.argmin()]
                if abs((nearest["time"] - t).total_seconds()) <= 120:
                    sess.loc[idx] = nearest["sess_date"]
        print(f"    [warn] {n_missing} order timestamps not exact bar matches; "
              f"{sess.isna().sum()} still unresolved after +/-2min fallback")
    df["sess_date"] = sess
    return df


periods = pd.read_csv(os.path.join(OUT, "periods_selected.csv"))

all_combined = []
for _, r in periods.iterrows():
    # wide calendar pad for the raw-extraction pass only (perf pre-filter); TRUE period membership
    # is decided below by sess_date, not by this raw timestamp window.
    win_start, win_end = pd.Timestamp(r["start"]), pd.Timestamp(r["end"]) + pd.Timedelta(days=1)
    pad_start, pad_end = win_start - pd.Timedelta(days=2), win_end + pd.Timedelta(days=2)
    if bool(r["rich_source"]):
        raw = build_rich_orders(RICH_PATH, pad_start, pad_end)
        raw = raw[(raw["time"] >= pad_start) & (raw["time"] <= pad_end)].reset_index(drop=True)
        src = "RICH:producta_v4_2024apr_2025mar.json"
    else:
        cpath = CHUNK_PATHS[r["chunk"]]
        raw = build_chunk_orders(cpath, pad_start, pad_end)
        raw = raw[(raw["time"] >= pad_start) & (raw["time"] <= pad_end)].reset_index(drop=True)
        src = f"CHUNK:A_{r['chunk']}_trades.json (comm-inferred qty)"
    combined = combine_same_bar(raw)
    combined = attach_sess_date(combined)
    # true period membership: SESSION date within [period start, period end], matching exactly
    # how step 01 bucketed the Python side (ev["sess_dt"] >= start & <= end)
    combined = combined[(combined["sess_date"] >= r["start"]) & (combined["sess_date"] <= r["end"])].reset_index(drop=True)
    combined.insert(0, "period", r["id"])
    combined["source"] = src
    all_combined.append(combined)
    n_reversal_pairs = int((combined["n_legs_combined"] == 2).sum())
    print(f"  {r['id']} ({src}): {len(raw)} raw entry/exit orders -> {len(combined)} combined "
          f"order-events ({n_reversal_pairs} same-bar reversal pairs merged), "
          f"nt8_cash_would_need_price=... n_qty_total={int(combined['qty'].sum())}")

nt8 = pd.concat(all_combined, ignore_index=True)
nt8.to_csv(os.path.join(OUT, "nt8_orders_periods.csv"), index=False)
print(f"\n[EXEC01/02] wrote nt8_orders_periods.csv ({len(nt8)} combined order-events across 9 periods)")
print("[EXEC01/02] done.")
