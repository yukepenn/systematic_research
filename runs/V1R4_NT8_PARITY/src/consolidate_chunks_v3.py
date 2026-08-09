"""FINAL, correct chunked full-history consolidation for NQ/MNQ: entry-time-consistent
ROUND-TRIP comparison on BOTH sides (not notional legs, not mixed entry-time-vs-bar-marking --
both of those were tried and shown to be biased/buggy, see git history of consolidate_chunks.py
and _v2.py for the diagnostic trail). Python round trips are built by simple sequential
entry/exit pairing of the already-verified leg CSVs (NQ/MNQ are strictly alternating single-
position entry/exit, so this pairing is unambiguous and was independently proven exact against
live NT8 output on the Q1-2025 window earlier this session).
"""
import os, json
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
CHUNKS = os.path.join(ROOT, "runs", "V1R4_NT8_PARITY", "out", "chunks")
EVENTS = os.path.join(ROOT, "runs", "V1R4_NT8_PARITY", "out", "one_nq_events")

EVAL_BOUNDS = [
    ("E1", "2022-01-03", "2022-09-01"), ("E2", "2022-09-01", "2023-05-01"),
    ("E3", "2023-05-01", "2024-01-01"), ("E4", "2024-01-01", "2024-09-01"),
    ("E5", "2024-09-01", "2025-05-01"), ("E6", "2025-05-01", "2026-01-01"),
    ("E7", "2026-01-01", "2026-05-29"),
]
PV = {"NQ": 20.0, "MNQ": 2.0}


def python_round_trips(leg_csv, pv, has_cash):
    df = pd.read_csv(leg_csv, parse_dates=["time"])
    # STABLE sort required: same-bar reversals emit an exit leg then an entry leg at the
    # IDENTICAL timestamp (t_idx tie); pandas' default quicksort is not stable and can swap
    # tied rows, breaking the exit-before-entry order and corrupting round-trip pairing.
    df = df.sort_values(["time"], kind="stable").reset_index(drop=True)
    trips = []
    cur = None
    for _, r in df.iterrows():
        if r["kind"] == "entry":
            cur = r
        elif r["kind"] == "exit" and cur is not None:
            if has_cash:
                pnl = df.loc[df["time"] == cur["time"]].iloc[0]  # placeholder, unused
            entry_cash = -cur["side"] * cur["qty"] * cur["price"] * pv - cur["commission"]
            exit_cash = -r["side"] * r["qty"] * r["price"] * pv - r["commission"]
            trips.append({"entry_t": cur["time"], "exit_t": r["time"], "pnl": entry_cash + exit_cash})
            cur = None
    return pd.DataFrame(trips)


def nt8_round_trips(obj, tag):
    trades = json.load(open(os.path.join(CHUNKS, f"{obj}_{tag}_trades.json"), encoding="utf-8"))
    return pd.DataFrame([{"entry_t": pd.Timestamp(t["entry_t"]), "exit_t": pd.Timestamp(t["exit_t"]),
                           "pnl": t["pnl"]} for t in trades])


leg_files = {"NQ": (os.path.join(EVENTS, "python_NQ_legs_full.csv"), False),
             "MNQ": (os.path.join(EVENTS, "python_mnq_events_full.csv"), False)}

rows = []
totals = {"NQ": {"nt8": 0.0, "py": 0.0}, "MNQ": {"nt8": 0.0, "py": 0.0}}
for obj in ["NQ", "MNQ"]:
    leg_csv, has_cash = leg_files[obj]
    py_all = python_round_trips(leg_csv, PV[obj], has_cash)
    for tag, e0, e1 in EVAL_BOUNDS:
        nt8_all = nt8_round_trips(obj, tag)
        e0t, e1t = pd.Timestamp(e0), pd.Timestamp(e1)
        nt8_win = nt8_all[(nt8_all["entry_t"] >= e0t) & (nt8_all["entry_t"] <= e1t)]
        py_win = py_all[(py_all["entry_t"] >= e0t) & (py_all["entry_t"] <= e1t)]
        nt8_net = float(nt8_win["pnl"].sum()); py_net = float(py_win["pnl"].sum())
        diff = nt8_net - py_net
        rel = diff / abs(py_net) * 100 if py_net else float("nan")
        rows.append({"object": obj, "chunk": tag, "eval_start": e0, "eval_end": e1,
                      "n_nt8_trades": len(nt8_win), "n_py_trades": len(py_win),
                      "nt8_net": round(nt8_net, 2), "py_net": round(py_net, 2),
                      "diff": round(diff, 2), "rel_pct": round(rel, 3)})
        totals[obj]["nt8"] += nt8_net; totals[obj]["py"] += py_net

df = pd.DataFrame(rows)
print(df.to_string(index=False))
print("\nFULL-HISTORY TOTALS (entry-time-consistent round-trip comparison, both sides same convention):")
for obj in ["NQ", "MNQ"]:
    t = totals[obj]; diff = t["nt8"] - t["py"]; rel = diff / abs(t["py"]) * 100
    print(f"{obj:4s}  NT8={t['nt8']:>14,.2f}  Python={t['py']:>14,.2f}  diff={diff:>10,.2f}  rel={rel:6.3f}%")

df.to_csv(os.path.join(CHUNKS, "full_history_chunk_report_FINAL.csv"), index=False)
json.dump({k: {"nt8_total": v["nt8"], "py_total": v["py"], "diff": v["nt8"] - v["py"],
                "rel_pct": (v["nt8"] - v["py"]) / abs(v["py"]) * 100} for k, v in totals.items()},
          open(os.path.join(CHUNKS, "full_history_totals_FINAL_nqmnq.json"), "w"), indent=2)
