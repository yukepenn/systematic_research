"""WIN01 follow-up -- P&L by exit-reason bucket for qualified/relaxed Product-B blocks (the C4
interaction check, sec30)."""
import os, sys, importlib.util
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
MOD_PATH = os.path.join(ROOT, "runs", "WIN01_WINNER_EXIT_RELAXATION", "src", "01_product_b_winner_relax.py")
spec = importlib.util.spec_from_file_location("win01b", MOD_PATH)
win01b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(win01b)  # re-runs the whole script (correctness gates etc.) -- fast, seconds

for name in ["WINB_RELAX_050", "WINB_RELAX_000"]:
    r = win01b.results[name]
    blk = win01b.block_table(r["pos"], r["bpnl"], r["blk"], win01b.canon_mask)
    blk["reason"] = blk["blk"].map(r["reason"]).fillna("OPEN_AT_DATA_END")
    qual_blocks = set(r["blk"][r["qual"] & win01b.canon_mask])
    blk_q = blk[blk["blk"].isin(qual_blocks)]
    print(f"\n=== {name}: P&L by exit reason (qualified/relaxed blocks only, n={len(blk_q)}) ===")
    g = blk_q.groupby("reason")["net"].agg(["count", "mean", "sum", lambda s: (s > 0).mean() * 100])
    g.columns = ["count", "mean_pnl", "sum_pnl", "win_rate_pct"]
    print(g.round(2))
