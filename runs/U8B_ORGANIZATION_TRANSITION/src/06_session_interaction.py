"""U8B session interaction (addendum's own explicit emphasis) -- for the single strongest Stage-1
cell among all 18 (outcome (a) MFE x reversal_rate_transition, resid rho=-0.0756, delta R^2=
+0.00305, 5/5 sign-stability, determined by 03_outcomes_abde.py's printed results), repeat the
Stage-1 test split by U0's own is_rth column (RTH vs ETH), report BOTH halves' n / raw+resid
Spearman / OLS delta-R^2 separately -- not one blended number."""
import os
import sys
import json
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from stats_lib import run_cell, print_cell

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
WINNING_FEATURE = "entry_reversal_rate_transition"
WINNING_OUTCOME_COL = "mfe_final"
WINNING_LABEL = "(a) MFE: reversal_rate_transition vs mfe_final"

block = pd.read_csv(os.path.join(OUT, "productB_block_table.csv"))
block["entry_is_health_only"] = block["entry_is_health_only"].astype(bool)
block["entry_is_rth"] = block["entry_is_rth"].astype(bool)

print(f"Winning cell: {WINNING_LABEL}")
print(f"Full-sample (blended) result, for reference:")
full_res = run_cell(block, WINNING_FEATURE, WINNING_OUTCOME_COL, "entry_abs_M", "entry_sigma460",
                     "entry_year", "entry_is_health_only", label=f"{WINNING_LABEL} (BLENDED, all sessions)")
print_cell(full_res)

results = {"blended": full_res}
for phase_name, phase_mask_val in [("RTH", True), ("ETH", False)]:
    sub = block[block["entry_is_rth"] == phase_mask_val].copy()
    print(f"\n{'=' * 100}\n{phase_name} only (entry_is_rth == {phase_mask_val})  n_total={len(sub)}\n{'=' * 100}")
    res = run_cell(sub, WINNING_FEATURE, WINNING_OUTCOME_COL, "entry_abs_M", "entry_sigma460",
                    "entry_year", "entry_is_health_only", label=f"{WINNING_LABEL} ({phase_name} only)")
    print_cell(res)
    results[phase_name] = res

with open(os.path.join(OUT, "session_interaction.json"), "w") as fh:
    json.dump(results, fh, indent=2, default=str)

print("\n" + "=" * 100)
print("SESSION-SPLIT SUMMARY (not blended)")
print("=" * 100)
for name in ["blended", "RTH", "ETH"]:
    r = results[name]
    print(f"  {name:10s} n={r['n_canonical']:5d}  raw_rho={r['raw_spearman']:+.4f}  "
          f"resid_rho={r['residualized_spearman']:+.4f}  delta_r2={r['ols_delta_r2']:+.5f}")
print("\nSession interaction test complete.")
