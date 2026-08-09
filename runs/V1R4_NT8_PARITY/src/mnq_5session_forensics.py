"""Reopens the 5 historically-named MNQ sessions (2025-04-07, 2025-04-09, 2025-04-11, 2025-11-18,
2026-04-08) against CURRENT SolarWaveOneContractMNQ_v5, using real NT8 trade output pulled via
CrossTrade (runs/V1R4_NT8_PARITY/out/mnq_sessions/*.json) vs the genuine-MNQ Python execution
reference (out/one_nq_events/python_mnq_events_full.csv). Classifies each session's first
divergence (if any) per the directive's taxonomy.
"""
import json, os
import pandas as pd, numpy as np

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = os.path.join(ROOT, "runs", "V1R4_NT8_PARITY", "out")
SESS_DIR = os.path.join(OUT, "mnq_sessions")

NAMED_SESSIONS = ["2025-04-07", "2025-04-09", "2025-04-11", "2025-11-18", "2026-04-08"]

nt8_files = ["mnq_v5_apr2025.json", "mnq_v5_nov2025.json", "mnq_v5_apr2026.json"]
nt8_legs = []
for f in nt8_files:
    d = json.load(open(os.path.join(SESS_DIR, f), encoding="utf-8"))
    for tr in d["trades"]:
        for kind in ("entry", "exit"):
            e = tr[kind]
            side = 1 if e["order_action"] in ("Buy", "BuyToCover") else -1
            nt8_legs.append({"time": pd.Timestamp(e["time"]), "kind": kind, "side": side,
                              "price": e["price"], "commission": e["commission"],
                              "order_action": e["order_action"], "trade_number": tr["TradeNumber"],
                              "source_file": f})
nt8 = pd.DataFrame(nt8_legs).sort_values("time").reset_index(drop=True)
nt8 = nt8.drop_duplicates(subset=["time", "kind", "side", "price", "trade_number", "source_file"]).reset_index(drop=True)

py = pd.read_csv(os.path.join(OUT, "one_nq_events", "python_mnq_events_full.csv"), parse_dates=["time"])
py = py.sort_values("time").reset_index(drop=True)


def matches(pr, nr):
    dt = abs((pr["time"] - nr["time"]).total_seconds())
    return dt <= 60 and pr["side"] == nr["side"]


results = []
for d0 in NAMED_SESSIONS:
    center = pd.Timestamp(d0)
    win_lo, win_hi = center - pd.Timedelta(hours=6), center + pd.Timedelta(hours=30)
    py_win = py[(py["time"] >= win_lo) & (py["time"] <= win_hi)].reset_index(drop=True)
    nt_win = nt8[(nt8["time"] >= win_lo) & (nt8["time"] <= win_hi)].reset_index(drop=True)
    print(f"\n{'='*90}\nSESSION {d0}\n{'='*90}")
    print(f"python legs in window: {len(py_win)}   nt8 legs in window: {len(nt_win)}")
    n = min(len(py_win), len(nt_win))
    first_div = None
    rows = []
    for i in range(n):
        pr = py_win.iloc[i]; nr = nt_win.iloc[i]
        dt = abs((pr["time"] - nr["time"]).total_seconds())
        dside = pr["side"] != nr["side"]
        dpx = abs(pr["price"] - nr["price"])
        rows.append((i, pr["time"], nr["time"], dt, pr["side"], nr["side"], pr["price"], nr["price"], dpx, pr["kind"]))
        if first_div is None and (dt > 60 or dside):
            first_div = rows[-1]
    print(f"aligned (positional) legs compared: {n}")
    if len(py_win) != len(nt_win):
        print(f"  ** LEG COUNT MISMATCH: python={len(py_win)} nt8={len(nt_win)} **")
    for r in rows:
        tick_flag = "" if abs(r[8] - 0.0) < 1e-9 or abs(r[8] - 0.50) < 1e-9 else "  <-- NON-STANDARD PRICE DIFF"
        print(f"  i={r[0]:2d} py={r[1]} nt={r[2]} dt={r[3]:.0f}s side(py={r[4]:+d},nt={r[5]:+d}) "
              f"px(py={r[6]:.2f},nt={r[7]:.2f},diff={r[8]:.2f}){tick_flag}")
    if first_div:
        print("FIRST DIVERGENCE (time/side beyond tolerance):", first_div)
    max_px_diff = max((r[8] for r in rows), default=None)
    results.append({
        "session": d0, "py_legs": len(py_win), "nt8_legs": len(nt_win),
        "leg_count_match": len(py_win) == len(nt_win),
        "max_price_diff": max_px_diff,
        "first_divergence": str(first_div) if first_div else None,
    })

pd.DataFrame(results).to_csv(os.path.join(OUT, "mnq_sessions", "5session_summary.csv"), index=False)
print("\n\nSUMMARY:")
print(pd.DataFrame(results).to_string(index=False))
