"""Consolidates the 21 chunk summaries (7 evaluation blocks x 3 objects) into full-history
net-profit certification tables, stitching evaluation-only P&L (warmup discarded) to cover the
canonical window 2022-01-03..2026-05-29 exactly once, then compares against each object's
independently-verified Python twin over the identical windows.
"""
import os, sys, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
from sm01_solarsim import load_bars_3m

CHUNKS = os.path.join(ROOT, "runs", "V1R4_NT8_PARITY", "out", "chunks")

EVAL_BOUNDS = [
    ("E1", "2022-01-03", "2022-09-01"),
    ("E2", "2022-09-01", "2023-05-01"),
    ("E3", "2023-05-01", "2024-01-01"),
    ("E4", "2024-01-01", "2024-09-01"),
    ("E5", "2024-09-01", "2025-05-01"),
    ("E6", "2025-05-01", "2026-01-01"),
    ("E7", "2026-01-01", "2026-05-29"),
]

bars = load_bars_3m()
sess = pd.to_datetime(bars["sess_date"])
dev = (sess <= pd.Timestamp("2026-05-31")).to_numpy()
bars = bars[dev].reset_index(drop=True)
bt = pd.to_datetime(bars["time"])

PY_ARR = {
    "NQ": os.path.join(ROOT, "runs", "S2_SELTIME", "out", "r2", "barpnl_NQ_incumbent.npy"),
    "MNQ": os.path.join(ROOT, "runs", "V1R4_NT8_PARITY", "out", "one_nq_events", "barpnl_MNQ_incumbent_genuine.npy"),
    "A": os.path.join(ROOT, "runs", "S2_SELTIME", "out", "r2", "barpnl_A_incumbent.npy"),
}

rows = []
totals = {"NQ": {"nt8": 0.0, "py": 0.0}, "MNQ": {"nt8": 0.0, "py": 0.0}, "A": {"nt8": 0.0, "py": 0.0}}
for obj, pyfile in PY_ARR.items():
    pnl = np.load(pyfile)
    for tag, e0, e1 in EVAL_BOUNDS:
        name = f"{obj}_{tag}"
        s = json.load(open(os.path.join(CHUNKS, f"{name}_summary.json"), encoding="utf-8"))
        nt8_net = s["net_eval"]
        m = (bt >= pd.Timestamp(e0)) & (bt <= pd.Timestamp(e1))
        py_net = float(pnl[m].sum())
        diff = nt8_net - py_net
        rel = diff / abs(py_net) * 100 if py_net != 0 else float("nan")
        rows.append({
            "object": obj, "chunk": tag, "eval_start": e0, "eval_end": e1,
            "n_bars_eval": int(m.sum()), "n_trades_eval": s["n_trades_eval"],
            "nt8_net": round(nt8_net, 2), "py_net": round(py_net, 2),
            "diff": round(diff, 2), "rel_pct": round(rel, 3),
        })
        totals[obj]["nt8"] += nt8_net
        totals[obj]["py"] += py_net

df = pd.DataFrame(rows)
df.to_csv(os.path.join(CHUNKS, "full_history_chunk_report.csv"), index=False)
print(df.to_string(index=False))

print("\n" + "=" * 90)
print("FULL-HISTORY STITCHED TOTALS (2022-01-03 .. 2026-05-29, all 7 chunks, evaluation-only)")
print("=" * 90)
for obj in ["A", "NQ", "MNQ"]:
    t = totals[obj]
    diff = t["nt8"] - t["py"]
    rel = diff / abs(t["py"]) * 100
    print(f"{obj:4s}  NT8={t['nt8']:>14,.2f}  Python={t['py']:>14,.2f}  diff={diff:>12,.2f}  rel={rel:6.3f}%")

json.dump({k: {"nt8_total": v["nt8"], "py_total": v["py"], "diff": v["nt8"] - v["py"],
                "rel_pct": (v["nt8"] - v["py"]) / abs(v["py"]) * 100}
           for k, v in totals.items()},
          open(os.path.join(CHUNKS, "full_history_totals.json"), "w"), indent=2)
