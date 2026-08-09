"""R2 diagnostic phase -- entry persistence/overshoot/pullback vs eventual trade outcome.
Descriptive only, per frozen spec.yaml. Reuses P0's ledger (already reconciled exactly to the
certified incumbent net) -- no new decision-layer construction in this script."""
import os, sys, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "runs", "R2_ENTRY_TIMING")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
P0OUT = os.path.join(ROOT, "runs", "P0_TRADESTATE_AUTOPSY", "out")

ledger = pd.read_parquet(os.path.join(P0OUT, "ledger_full.parquet"),
                          columns=["t_idx", "time", "position", "M", "T", "block_id",
                                   "close", "sigma460_atr_proxy_pts", "roll_hi20", "roll_lo20",
                                   "n_bullish", "n_bearish", "B", "entry_price"])
blocks = pd.read_csv(os.path.join(P0OUT, "block_level_summary.csv"))
ENTRY_LEVEL = 3.0
M = ledger["M"].to_numpy()
n = len(ledger)

# entry bar = first bar of each position-block (t_idx = min within block, position!=0 group)
pos_blocks = ledger[ledger["position"] != 0]
entry_idx = pos_blocks.groupby("block_id")["t_idx"].min()
blocks = blocks.merge(entry_idx.rename("entry_t_idx"), on="block_id")

M_entry = []
M_p1 = []
M_p2 = []
overshoot = []
side = blocks["side"].to_numpy()
for i, row in blocks.iterrows():
    t0 = int(row["entry_t_idx"])
    m0 = M[t0]
    m1 = M[t0 + 1] if t0 + 1 < n else np.nan
    m2 = M[t0 + 2] if t0 + 2 < n else np.nan
    M_entry.append(m0); M_p1.append(m1); M_p2.append(m2)
    overshoot.append(abs(m0) - ENTRY_LEVEL)
blocks["M_entry"] = M_entry
blocks["M_p1"] = M_p1
blocks["M_p2"] = M_p2
blocks["overshoot"] = overshoot

s = blocks["side"].to_numpy()
blocks["persist_1bar"] = np.sign(blocks["M_p1"]) == s  # still same-signed 1 bar later (not necessarily still beyond ENTRY_LEVEL)
blocks["persist_1bar_strong"] = (s > 0) & (blocks["M_p1"] >= ENTRY_LEVEL) | (s < 0) & (blocks["M_p1"] <= -ENTRY_LEVEL)
blocks["persist_2bar_strong"] = (s > 0) & (blocks["M_p2"] >= ENTRY_LEVEL) | (s < 0) & (blocks["M_p2"] <= -ENTRY_LEVEL)
blocks["reverted_1bar"] = ~blocks["persist_1bar"]

blocks.to_csv(os.path.join(OUT, "entry_diagnostic_table.csv"), index=False)

print("=== R2-A: persistence vs outcome ===")
for col in ["persist_1bar", "persist_1bar_strong", "persist_2bar_strong"]:
    g = blocks.groupby(col)["net_pnl"].agg(["count", "mean", "sum"])
    print(f"\n-- {col} --")
    print(g)

print("\n=== R2-A: overshoot (signal strength beyond ENTRY_LEVEL) vs outcome ===")
blocks["overshoot_bucket"] = pd.cut(blocks["overshoot"], [-0.01, 0, 1, 2, 4, 100],
                                     labels=["0(exact)", "0-1", "1-2", "2-4", "4+"])
print(blocks.groupby("overshoot_bucket", observed=True)["net_pnl"].agg(["count", "mean", "sum"]))

print("\n=== R2-A: reverted-1-bar rate, and whether it correlates with eventual net_pnl decile ===")
n_tot = len(blocks)
blocks_sorted = blocks.sort_values("net_pnl")
bottom10 = blocks_sorted.iloc[:int(0.10 * n_tot)]
top10 = blocks_sorted.iloc[-int(0.10 * n_tot):]
print(f"reverted_1bar rate, bottom-decile losers: {bottom10['reverted_1bar'].mean()*100:.1f}%  "
      f"(n={len(bottom10)})")
print(f"reverted_1bar rate, top-decile winners:   {top10['reverted_1bar'].mean()*100:.1f}%  "
      f"(n={len(top10)})")
print(f"reverted_1bar rate, ALL trades:           {blocks['reverted_1bar'].mean()*100:.1f}%  "
      f"(n={n_tot})")

spearman_overshoot = float(blocks["overshoot"].corr(blocks["net_pnl"], method="spearman"))
spearman_persist1 = float(blocks["persist_1bar_strong"].astype(int).corr(blocks["net_pnl"], method="spearman"))
print(f"\nSpearman corr(overshoot, net_pnl) = {spearman_overshoot:.4f}")
print(f"Spearman corr(persist_1bar_strong, net_pnl) = {spearman_persist1:.4f}")

# ---- R2-A right-tail check: would a 1-bar confirmation rule have delayed/missed top winners?
# simulate: if we REQUIRE persist_1bar_strong to enter (i.e. only commit on t0+1 if still beyond
# ENTRY_LEVEL), what fraction of the TOP winners would have been delayed by exactly 1 bar
# (harmless, still captured, just entered 3 min later) vs actually REVERSED by t0+1 (would have
# been missed entirely under a "wait 1 bar, only enter if still valid" rule)?
top20 = blocks_sorted.iloc[-20:]
missed_if_confirm1 = top20[~top20["persist_1bar_strong"]]
print(f"\n=== R2-B/C tail-preservation pre-check: top-20 winners that would be MISSED entirely "
      f"under a naive '1-bar confirm, else skip' entry rule ===")
print(f"{len(missed_if_confirm1)} of 20 top winners have M reverting below ENTRY_LEVEL by t0+1 "
      f"(would be missed or need special-casing):")
print(missed_if_confirm1[["block_id", "side", "net_pnl", "M_entry", "M_p1", "overshoot"]].to_string(index=False))

diagnostics = {
    "n_entries": int(n_tot),
    "spearman_overshoot_vs_netpnl": spearman_overshoot,
    "spearman_persist1bar_strong_vs_netpnl": spearman_persist1,
    "reverted_1bar_rate_bottom10pct_losers": float(bottom10["reverted_1bar"].mean()),
    "reverted_1bar_rate_top10pct_winners": float(top10["reverted_1bar"].mean()),
    "reverted_1bar_rate_all": float(blocks["reverted_1bar"].mean()),
    "n_top20_winners_missed_under_naive_1bar_confirm": int(len(missed_if_confirm1)),
}
json.dump(diagnostics, open(os.path.join(OUT, "r2a_diagnostics.json"), "w"), indent=2)
print("\nsaved r2a_diagnostics.json, entry_diagnostic_table.csv")
