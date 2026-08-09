"""R3 diagnostic part 2 -- reconciles a surprising divergence found in 01_diagnose.py: ENTRY-level
attribution (whole-block net_pnl assigned to the block's entry-hm) showed EUROPE_PREUS pooled
POSITIVE (+$79,924.82, 4/5 years positive) -- the opposite of S2 spec.yaml's own pre-screen
("Solar's EUROPE_PREUS net P&L by year: 5/5 years negative, -$4,847 to -$6,461"). This script
checks whether that pre-screen used BAR-LEVEL P&L attribution (each bar's own realized P&L
assigned to its own clock slot, regardless of when the position was entered -- the S0_TOD_AUTOPSY
convention) rather than entry-level, and if so, decomposes bar-level EUROPE_PREUS P&L by whether
the bar belongs to a block ENTERED inside vs outside the window."""
import os, sys, json
import numpy as np, pandas as pd

SA0_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                        "SA0_SYSTEM_STRUCTURE", "src")
sys.path.insert(0, SA0_SRC)
import substrate as S

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
ledger = pd.read_parquet(S.LEDGER_PATH)

hm = ledger["hm"].to_numpy()
in_window_bar = (hm >= 200) & (hm < 800)
bar_pnl = ledger["bar_pnl_dollars"].to_numpy()
year = pd.to_datetime(ledger["sess_date"]).dt.year.to_numpy()

print("=" * 90, "\nBAR-LEVEL P&L BY EUROPE_PREUS WINDOW (matches S0/S2's own convention)\n", "=" * 90, sep="")
df_bar = pd.DataFrame({"year": year, "in_window": in_window_bar, "pnl": bar_pnl})
g_bar = df_bar.groupby(["in_window"]).agg(n_bars=("pnl", "size"), sum_pnl=("pnl", "sum"), mean_pnl=("pnl", "mean"))
print(g_bar.round(2))
print("\nyear-by-year, IN_WINDOW bars only (bar-level, cross-check vs S2 spec.yaml pre-screen: "
      "2022 -4847, 2023 -6461, 2024 -6069, 2025 -5988, 2026stub -5550):")
yby_bar = df_bar[df_bar["in_window"]].groupby("year")["pnl"].sum()
print(yby_bar.round(2))

print("\n" + "=" * 90, "\nDECOMPOSE: bars in EUROPE_PREUS belonging to blocks ENTERED inside vs outside the window\n", "=" * 90, sep="")
block_sum = pd.read_csv(S.BLOCKSUM_PATH)
entry_rows = ledger[(ledger["age_bars"] == 1) & (ledger["position"] != 0)].copy()
entry_hm_by_block = entry_rows.set_index("block_id")["hm"]
ledger["entry_hm_of_block"] = ledger["block_id"].map(entry_hm_by_block)
ledger_pos = ledger[ledger["position"] != 0].copy()
ledger_pos["entry_in_window"] = (ledger_pos["entry_hm_of_block"] >= 200) & (ledger_pos["entry_hm_of_block"] < 800)
ledger_pos["bar_in_window"] = (ledger_pos["hm"] >= 200) & (ledger_pos["hm"] < 800)

decomp = ledger_pos[ledger_pos["bar_in_window"]].groupby("entry_in_window").agg(
    n_bars=("bar_pnl_dollars", "size"), sum_pnl=("bar_pnl_dollars", "sum"),
    n_blocks=("block_id", "nunique"))
decomp.index = decomp.index.map({True: "ENTERED_INSIDE_WINDOW", False: "ENTERED_OUTSIDE_carried_in"})
print("bars physically inside EUROPE_PREUS clock slot, split by where their BLOCK was entered:")
print(decomp.round(2))

# also: for blocks entered OUTSIDE the window but carrying bars INTO it, what's their fate --
# are these late-stage giveback/reversal bars from Solar's afternoon/evening trend fading overnight?
carried = ledger_pos[ledger_pos["bar_in_window"] & (~ledger_pos["entry_in_window"])]
carried_blocks = carried["block_id"].unique()
carried_block_summary = block_sum[block_sum["block_id"].isin(carried_blocks)]
print(f"\n{len(carried_blocks)} distinct blocks carry bars into EUROPE_PREUS from an entry made "
      f"outside it. Their FULL block (not just the in-window bars) net_pnl distribution:")
print(carried_block_summary["net_pnl"].describe().round(2))
print(f"win rate of these carried-over blocks (whole-block outcome): "
      f"{float((carried_block_summary['net_pnl'] > 0).mean()):.3f}")

summary = {
    "bar_level_pooled_in_window_sum": float(g_bar.loc[True, "sum_pnl"]) if True in g_bar.index else None,
    "bar_level_year_by_year_in_window": yby_bar.to_dict(),
    "decomposition_by_entry_location": decomp["sum_pnl"].to_dict(),
    "n_carried_over_blocks": int(len(carried_blocks)),
    "carried_over_blocks_win_rate": float((carried_block_summary["net_pnl"] > 0).mean()),
}
json.dump(summary, open(os.path.join(OUT, "diag2_bar_vs_entry_reconciliation.json"), "w"), indent=2, default=str)
print("\nR3 diagnostic part 2 complete.")
