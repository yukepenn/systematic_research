"""V1/V1a-d (MEGA PROMPT addendum) -- empirical flatten-time + near-cutoff-entry audit
on the REAL NT8 Strategy Analyzer trade lists already exported for BEST_ONE_NQ / BEST_ONE_MNQ.
No new backtest, no config change -- pure read of runs/PRODUCTB_ONECONTRACT_FINAL/out/.
"""
import sys
import numpy as np
import pandas as pd

REPO = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
NQ_COMM_RT = 4.36
MNQ_COMM_RT = 1.30

for name, path, comm_rt in [
    ("NQ", REPO + r"\runs\PRODUCTB_ONECONTRACT_FINAL\out\nt_trades_nq.csv", NQ_COMM_RT),
    ("MNQ", REPO + r"\runs\PRODUCTB_ONECONTRACT_FINAL\out\nt_trades_mnq.csv", MNQ_COMM_RT),
]:
    print(f"\n{'='*70}\n{name}\n{'='*70}")
    df = pd.read_csv(path, parse_dates=["entry_time", "exit_time"])
    print(f"trades={len(df)}  sum(pnl)={df.pnl.sum():,.2f}")

    # --- exit-time-of-day distribution ---
    exit_hm = df.exit_time.dt.hour * 100 + df.exit_time.dt.minute
    after_1645 = df[exit_hm > 1645]
    print(f"\nexit time-of-day: min={df.exit_time.dt.strftime('%H:%M').min()} "
          f"max={df.exit_time.dt.strftime('%H:%M').max()}")
    print(f"exits strictly after 16:45 ET: {len(after_1645)} / {len(df)} "
          f"({100*len(after_1645)/len(df):.3f}%)")
    if len(after_1645):
        vc = after_1645.exit_time.dt.strftime("%Y-%m-%d %H:%M").value_counts().sort_index()
        print("dates/times of >16:45 exits (first 20):")
        print(vc.head(20).to_string())
    print("\nexit-time histogram (16:00-17:00 ET, 1-min buckets, top 15 by count):")
    win = df[(exit_hm >= 1600) & (exit_hm <= 1700)]
    print(win.exit_time.dt.strftime("%H:%M").value_counts().sort_index().head(20).to_string())
    print(f"(n exits in 16:00-17:00 window: {len(win)} / {len(df)})")

    # --- V1b: trades whose ENTRY falls in the final N minutes of the session (session end 17:00 ET) ---
    entry_hm = df.entry_time.dt.hour * 100 + df.entry_time.dt.minute
    entry_min_from_1700 = (17 * 60) - (df.entry_time.dt.hour * 60 + df.entry_time.dt.minute)
    # sessions ending after midnight (shouldn't happen for RTH-anchored 17:00 close) -- guard
    df["_entry_min_before_close"] = entry_min_from_1700
    df["_year"] = df.entry_time.dt.year
    df["_comm"] = comm_rt

    print(f"\n--- V1b diagnostic: trades opened in final N minutes before 17:00 ET session close ---")
    print(f"{'N(min)':>7} {'count':>7} {'net_pnl':>12} {'pnl/trade':>10} {'win_rate':>9} {'friction_share':>14}")
    for N in [5, 10, 15, 20, 30, 45, 60]:
        cell = df[(df._entry_min_before_close > 0) & (df._entry_min_before_close <= N)]
        if len(cell) == 0:
            print(f"{N:>7} {0:>7} {'--':>12} {'--':>10} {'--':>9} {'--':>14}")
            continue
        net = cell.pnl.sum()
        per_trade = cell.pnl.mean()
        win_rate = (cell.pnl > 0).mean()
        gross = (cell.pnl.abs()).sum()  # proxy: |pnl| as gross-ish scale, commission on top
        total_comm = len(cell) * comm_rt
        friction_share = total_comm / (cell.pnl.sum() + total_comm) if (cell.pnl.sum() + total_comm) != 0 else float('nan')
        print(f"{N:>7} {len(cell):>7} {net:>12,.2f} {per_trade:>10,.2f} {win_rate:>9.3f} {friction_share:>14.3f}")

    print(f"\n--- same, split by year (N=30 fixed) ---")
    cell30 = df[(df._entry_min_before_close > 0) & (df._entry_min_before_close <= 30)]
    byyear = cell30.groupby("_year").agg(count=("pnl", "size"), net=("pnl", "sum"),
                                          per_trade=("pnl", "mean"),
                                          win_rate=("pnl", lambda s: (s > 0).mean()))
    print(byyear.round(2).to_string())

    # --- overall friction share (V4 preview, commission-only proxy from this CSV) ---
    total_comm_all = len(df) * comm_rt
    net_all = df.pnl.sum()
    gross_all = net_all + total_comm_all
    print(f"\n--- V4 preview (commission-only, this object) ---")
    print(f"gross(net+commission)={gross_all:,.2f}  commission={total_comm_all:,.2f}  "
          f"net={net_all:,.2f}  commission_share_of_gross={total_comm_all/gross_all:.4f}")
