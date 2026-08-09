"""U8 outcome (a) -- entry value: net_pnl of ALL Product-B blocks (long+short), feature measured
at the block's own entry bar (age_bars_B==1). Feature strictly precedes all of the block's own
P&L (no sunk-P&L confound possible), matching R4's exact block-entry pairing."""
import os
import sys
import json
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from stats_lib import run_cell, print_cell

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
FEATURES_20 = ["reversal_rate_20", "run_persistence_20", "perm_entropy_20"]
FEATURES_10 = ["reversal_rate_10", "run_persistence_10", "perm_entropy_10"]

COLS = ["t_idx", "sess_date", "year", "is_health_only_bar", "M", "sigma460_atr_proxy_pts",
        "position_B", "action_B", "block_id_B", "age_bars_B", "run_pnl_B_dollars"] + FEATURES_10 + FEATURES_20

df = pd.read_parquet(os.path.join(OUT, "u8_bars_with_features.parquet"), columns=COLS)
df = df.sort_values("t_idx").reset_index(drop=True)

nz = df[df["position_B"] != 0]
block_ids = nz["block_id_B"].unique()
print(f"building Product-B block table (all blocks, long+short): {len(block_ids)} blocks")

g = nz.groupby("block_id_B")
entry = df[(df["age_bars_B"] == 1) & (df["position_B"] != 0)].set_index("block_id_B")
last_idx = g["t_idx"].idxmax()
last = df.loc[last_idx].set_index("block_id_B")

block = pd.DataFrame(index=block_ids)
block["side"] = entry["position_B"]
block["entry_year"] = entry["year"]
block["entry_is_health_only"] = entry["is_health_only_bar"]
block["entry_M"] = entry["M"]
block["entry_abs_M"] = entry["M"].abs()
block["entry_sigma460"] = entry["sigma460_atr_proxy_pts"]
block["net_pnl"] = last["run_pnl_B_dollars"]
for f in FEATURES_10 + FEATURES_20:
    block[f"entry_{f}"] = entry[f]
block = block.reset_index().rename(columns={"index": "block_id_B"})

print(f"  n={len(block)}  net sum ${block['net_pnl'].sum():,.2f}  "
      f"(canonical-only net sum ${block.loc[~block.entry_is_health_only,'net_pnl'].sum():,.2f})")
block.to_csv(os.path.join(OUT, "outcome_a_block_table.csv"), index=False)

results = []
for f in FEATURES_20:
    res = run_cell(block, f"entry_{f}", "net_pnl", "entry_abs_M", "entry_sigma460",
                    "entry_year", "entry_is_health_only", label=f"(a) entry-value: {f} vs block net_pnl")
    print_cell(res)
    results.append(res)

# 10-bar robustness (not part of the required 12-cell table, reported alongside)
print("\n" + "=" * 100 + "\n10-BAR ROBUSTNESS (not a required cell, cross-check only)\n" + "=" * 100)
results_10bar = []
for f in FEATURES_10:
    res = run_cell(block, f"entry_{f}", "net_pnl", "entry_abs_M", "entry_sigma460",
                    "entry_year", "entry_is_health_only", label=f"(a)-10bar entry-value: {f} vs block net_pnl")
    print_cell(res)
    results_10bar.append(res)

with open(os.path.join(OUT, "outcome_a_results.json"), "w") as fh:
    json.dump({"primary_20bar": results, "robustness_10bar": results_10bar}, fh, indent=2, default=str)
print("\noutcome (a) complete.")
