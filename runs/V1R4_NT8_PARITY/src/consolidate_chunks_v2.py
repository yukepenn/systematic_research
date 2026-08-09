"""Corrected chunked full-history consolidation: leg-cash-flow-in-window accounting on BOTH
sides (NT8 and Python), for all 3 objects. Fixes the entry-time-only trade filter's boundary
bias (a position opened near a chunk edge and closed after it got its FULL P&L attributed to the
entry chunk under the naive filter, which compounds directionally in a trending market -- this
was caught by comparing against Product A's independently-verified full-window total).
"""
import os, sys, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
CHUNKS = os.path.join(ROOT, "runs", "V1R4_NT8_PARITY", "out", "chunks")
EVENTS = os.path.join(ROOT, "runs", "V1R4_NT8_PARITY", "out", "one_nq_events")

EVAL_BOUNDS = [
    ("E1", "2022-01-03", "2022-09-01"),
    ("E2", "2022-09-01", "2023-05-01"),
    ("E3", "2023-05-01", "2024-01-01"),
    ("E4", "2024-01-01", "2024-09-01"),
    ("E5", "2024-09-01", "2025-05-01"),
    ("E6", "2025-05-01", "2026-01-01"),
    ("E7", "2026-01-01", "2026-05-29"),
]

PV = {"NQ": 20.0, "MNQ": 2.0, "A": 2.0}


def nt8_legs_for_chunk(obj, tag, pv):
    trades = json.load(open(os.path.join(CHUNKS, f"{obj}_{tag}_trades.json"), encoding="utf-8"))
    legs = []
    for tr in trades:
        for leg_key in ("entry", "exit"):
            t = pd.Timestamp(tr[f"{leg_key}_t"])
            px = tr[f"{leg_key}_px"]
            action = tr["side"] if leg_key == "entry" else None
            legs.append({"time": t, "px": px, "leg": leg_key, "trade_side": tr["side"], "pnl": tr["pnl"], "comm": tr["comm"]})
    return legs


def nt8_leg_cash(obj, tag, pv):
    """Recompute leg cash flow directly from the compact trade dump (entry/exit price+side+qty
    aren't separately stored per-leg in the compact dump, so recover qty from pnl/price delta is
    unreliable for multi-contract Product A trades -- instead, reload the FULL per-leg JSON we
    already have from the original job result, which does carry quantity per leg)."""
    full = json.load(open(os.path.join(CHUNKS, f"{obj}_{tag}_summary.json"), encoding="utf-8"))
    return full


def leg_window_sum(csv_path, pv, e0, e1, has_cash=True):
    df = pd.read_csv(csv_path, parse_dates=["time"])
    if not has_cash:
        df["cash"] = -df["side"] * df["qty"] * df["price"] * pv - df["commission"]
    m = (df["time"] >= pd.Timestamp(e0)) & (df["time"] <= pd.Timestamp(e1))
    return float(df.loc[m, "cash"].sum()), int(m.sum())


# ---- python side: full leg cash sums per window (already have full leg files for all 3) ----
py_leg_files = {
    "NQ": (os.path.join(EVENTS, "python_NQ_legs_full.csv"), True),
    "A": (os.path.join(EVENTS, "python_A_legs_full.csv"), True),
    "MNQ": (os.path.join(EVENTS, "python_mnq_events_full.csv"), False),
}

# ---- nt8 side: rebuild leg cash flow from the ORIGINAL raw job result files (need qty per leg,
# which the compact *_trades.json dump in chunk_helpers didn't retain in enough detail for
# Product A's multi-contract trades -- reparse from the saved raw job jsons where available) ----
RAW_JOB_FILES = {
    ("NQ", "E1"): None,  # single-lot objects: qty is always 1, compact dump suffices
}


def nt8_onelot_leg_cash(obj, tag, pv, comm_per_side):
    trades = json.load(open(os.path.join(CHUNKS, f"{obj}_{tag}_trades.json"), encoding="utf-8"))
    rows = []
    for tr in trades:
        side_sign = 1 if tr["side"] in ("Buy", "BuyToCover") else -1
        rows.append({"time": pd.Timestamp(tr["entry_t"]), "cash": -side_sign * tr["entry_px"] * pv - comm_per_side})
        rows.append({"time": pd.Timestamp(tr["exit_t"]), "cash": side_sign * tr["exit_px"] * pv - comm_per_side})
    return pd.DataFrame(rows)


rows = []
totals = {"A": {"nt8": 0.0, "py": 0.0}, "NQ": {"nt8": 0.0, "py": 0.0}, "MNQ": {"nt8": 0.0, "py": 0.0}}
COMM = {"NQ": 2.18, "MNQ": 0.65}

for obj in ["NQ", "MNQ"]:
    for tag, e0, e1 in EVAL_BOUNDS:
        nt8_df = nt8_onelot_leg_cash(obj, tag, PV[obj], COMM[obj])
        m = (nt8_df["time"] >= pd.Timestamp(e0)) & (nt8_df["time"] <= pd.Timestamp(e1))
        nt8_net = float(nt8_df.loc[m, "cash"].sum())
        pyfile, has_cash = py_leg_files[obj]
        py_net, n_py_legs = leg_window_sum(pyfile, PV[obj], e0, e1, has_cash)
        diff = nt8_net - py_net
        rel = diff / abs(py_net) * 100 if py_net else float("nan")
        rows.append({"object": obj, "chunk": tag, "eval_start": e0, "eval_end": e1,
                      "n_nt8_legs": int(m.sum()), "n_py_legs": n_py_legs,
                      "nt8_net": round(nt8_net, 2), "py_net": round(py_net, 2),
                      "diff": round(diff, 2), "rel_pct": round(rel, 3)})
        totals[obj]["nt8"] += nt8_net
        totals[obj]["py"] += py_net

df = pd.DataFrame(rows)
print(df.to_string(index=False))
print("\nNQ/MNQ leg-cash-flow totals:")
for obj in ["NQ", "MNQ"]:
    t = totals[obj]
    diff = t["nt8"] - t["py"]
    rel = diff / abs(t["py"]) * 100
    print(f"{obj:4s}  NT8={t['nt8']:>14,.2f}  Python={t['py']:>14,.2f}  diff={diff:>10,.2f}  rel={rel:6.3f}%")

def nt8_producta_leg_cash(tag):
    trades = json.load(open(os.path.join(CHUNKS, f"A_{tag}_trades.json"), encoding="utf-8"))
    rows = []
    for tr in trades:
        qty = round(tr["comm"] / 1.30)  # 0.65/side/contract * 2 sides; exact, no rounding ambiguity
        side_sign = 1 if tr["side"] in ("Buy", "BuyToCover") else -1
        comm_side = tr["comm"] / 2.0
        rows.append({"time": pd.Timestamp(tr["entry_t"]), "cash": -side_sign * qty * tr["entry_px"] * PV["A"] - comm_side})
        rows.append({"time": pd.Timestamp(tr["exit_t"]), "cash": side_sign * qty * tr["exit_px"] * PV["A"] - comm_side})
    return pd.DataFrame(rows)


a_rows = []
for tag, e0, e1 in EVAL_BOUNDS:
    nt8_df = nt8_producta_leg_cash(tag)
    m = (nt8_df["time"] >= pd.Timestamp(e0)) & (nt8_df["time"] <= pd.Timestamp(e1))
    nt8_net = float(nt8_df.loc[m, "cash"].sum())
    py_net, n_py_legs = leg_window_sum(os.path.join(EVENTS, "python_A_legs_full.csv"), PV["A"], e0, e1, True)
    diff = nt8_net - py_net
    rel = diff / abs(py_net) * 100 if py_net else float("nan")
    a_rows.append({"object": "A", "chunk": tag, "eval_start": e0, "eval_end": e1,
                    "n_nt8_legs": int(m.sum()), "n_py_legs": n_py_legs,
                    "nt8_net": round(nt8_net, 2), "py_net": round(py_net, 2),
                    "diff": round(diff, 2), "rel_pct": round(rel, 3)})
    totals["A"]["nt8"] += nt8_net
    totals["A"]["py"] += py_net

adf = pd.DataFrame(a_rows)
print("\nProduct A:")
print(adf.to_string(index=False))
t = totals["A"]
diff = t["nt8"] - t["py"]
rel = diff / abs(t["py"]) * 100
print(f"A     NT8={t['nt8']:>14,.2f}  Python={t['py']:>14,.2f}  diff={diff:>10,.2f}  rel={rel:6.3f}%")

full_df = pd.concat([df, adf], ignore_index=True)
full_df.to_csv(os.path.join(CHUNKS, "full_history_chunk_report_v2.csv"), index=False)
json.dump({k: {"nt8_total": v["nt8"], "py_total": v["py"], "diff": v["nt8"] - v["py"],
                "rel_pct": (v["nt8"] - v["py"]) / abs(v["py"]) * 100}
           for k, v in totals.items()},
          open(os.path.join(CHUNKS, "full_history_totals_v2.json"), "w"), indent=2)
print("\nsaved full_history_chunk_report_v2.csv and full_history_totals_v2.json")
