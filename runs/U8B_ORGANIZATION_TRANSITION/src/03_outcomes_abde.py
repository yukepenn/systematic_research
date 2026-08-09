"""U8B outcomes (a) MFE, (b) MAE, (d) bars_to_mfe, (e) top-decile-winner probability.
Stage 1 (bucket-residualized) for all 3 transition features x 4 outcomes = 12 cells.
Stage 2 (explicit interaction with |M|) for the 2 independent features x 4 outcomes = 8 cells."""
import os
import sys
import json
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from stats_lib import run_cell, print_cell, interaction_cell, print_interaction_cell

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
FEATURES = ["perm_entropy_transition", "reversal_rate_transition", "run_persistence_transition"]
INDEPENDENT_FEATURES = ["perm_entropy_transition", "reversal_rate_transition"]

OUTCOMES = [
    ("a_mfe", "mfe_final", "(a) MFE (bigger eventual MFE = better)"),
    ("b_mae", "mae_abs", "(b) MAE magnitude (lower = better)"),
    ("d_bars_to_mfe", "bars_to_mfe", "(d) bars-to-MFE (lower = faster follow-through)"),
    ("e_top_decile", "top_decile_winner", "(e) P(top-decile winner)"),
]

block = pd.read_csv(os.path.join(OUT, "productB_block_table.csv"))
block["entry_is_health_only"] = block["entry_is_health_only"].astype(bool)
block["entry_is_rth"] = block["entry_is_rth"].astype(bool)
print(f"Product-B block table: n={len(block)}")

stage1_results = {}
stage2_results = {}

for key, outcome_col, outcome_label in OUTCOMES:
    print("\n" + "=" * 100)
    print(f"OUTCOME {outcome_label}  (outcome_col={outcome_col})")
    print("=" * 100)
    s1 = []
    for f in FEATURES:
        res = run_cell(block, f"entry_{f}", outcome_col, "entry_abs_M", "entry_sigma460",
                        "entry_year", "entry_is_health_only",
                        label=f"{outcome_label}: {f} vs {outcome_col}")
        print_cell(res)
        s1.append(res)
    stage1_results[key] = s1

    s2 = []
    for f in INDEPENDENT_FEATURES:
        res2 = interaction_cell(block, f"entry_{f}", outcome_col, "entry_abs_M", "entry_sigma460",
                                 "entry_is_health_only", label=f"{outcome_label}: {f} x |M| interaction")
        print_interaction_cell(res2)
        s2.append(res2)
    stage2_results[key] = s2

with open(os.path.join(OUT, "outcomes_abde_stage1.json"), "w") as fh:
    json.dump(stage1_results, fh, indent=2, default=str)
with open(os.path.join(OUT, "outcomes_abde_stage2.json"), "w") as fh:
    json.dump(stage2_results, fh, indent=2, default=str)
print("\noutcomes (a)/(b)/(d)/(e) complete.")
