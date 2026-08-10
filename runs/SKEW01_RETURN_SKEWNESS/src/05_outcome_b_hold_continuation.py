"""SKEW01 outcome (b) -- hold continuation: forward-5-bar realized P&L (bar_pnl_B_nq_dollars
summed over t+1..t+5, U3's/U8's own forward_fixed construction) at every action_B=='HOLD' bar.
BOTH raw skewness_20/10 (not direction-aligned) and aligned_skewness (aligned to the currently-
held position's side) are tested, per orchestrator instruction -- forward-only outcome, no
sunk-P&L confound (the outcome starts strictly AFTER the bar the feature is measured on)."""
import os
import sys
import json
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from stats_lib import run_cell, print_cell

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")

COLS = ["t_idx", "sess_date", "year", "is_health_only_bar", "M", "sigma460_atr_proxy_pts",
        "position_B", "action_B", "bar_pnl_B_nq_dollars", "skewness_10", "skewness_20"]

df = pd.read_parquet(os.path.join(OUT, "skew01_bars_with_features.parquet"), columns=COLS)
df = df.sort_values("t_idx").reset_index(drop=True)
n = len(df)
assert (df["t_idx"].to_numpy() == np.arange(n)).all()

cum = np.concatenate([[0.0], np.cumsum(np.nan_to_num(df["bar_pnl_B_nq_dollars"].to_numpy()))])


def fwd5(t_idx):
    hi = t_idx + 1 + 5
    valid = hi <= n
    out = np.full(len(t_idx), np.nan)
    out[valid] = cum[hi[valid]] - cum[t_idx[valid] + 1]
    return out


hold = df[df["action_B"] == "HOLD"].copy()
hold["fwd_5"] = fwd5(hold["t_idx"].to_numpy())
hold["abs_M"] = hold["M"].abs()
for W in [10, 20]:
    hold[f"aligned_skewness_{W}"] = hold[f"skewness_{W}"] * np.sign(hold["position_B"])
print(f"HOLD bars: {len(hold)}  (canonical {(~hold.is_health_only_bar).sum()}, "
      f"health-only {hold.is_health_only_bar.sum()})")
print(f"baseline fwd_5 mean (canonical) = {hold.loc[~hold.is_health_only_bar,'fwd_5'].mean():.4f}")
hold.to_csv(os.path.join(OUT, "outcome_b_hold_table.csv"), index=False)

results = []
for f in ["aligned_skewness_20", "skewness_20"]:
    res = run_cell(hold, f, "fwd_5", "abs_M", "sigma460_atr_proxy_pts", "year",
                    "is_health_only_bar", label=f"(b) hold-continuation: {f} vs fwd_5")
    print_cell(res)
    results.append(res)

print("\n" + "=" * 100 + "\n10-BAR ROBUSTNESS (not a required cell, cross-check only)\n" + "=" * 100)
results_10bar = []
for f in ["aligned_skewness_10", "skewness_10"]:
    res = run_cell(hold, f, "fwd_5", "abs_M", "sigma460_atr_proxy_pts", "year",
                    "is_health_only_bar", label=f"(b)-10bar hold-continuation: {f} vs fwd_5")
    print_cell(res)
    results_10bar.append(res)

with open(os.path.join(OUT, "outcome_b_results.json"), "w") as fh:
    json.dump({"primary_20bar": results, "robustness_10bar": results_10bar}, fh, indent=2, default=str)
print("\noutcome (b) complete.")
