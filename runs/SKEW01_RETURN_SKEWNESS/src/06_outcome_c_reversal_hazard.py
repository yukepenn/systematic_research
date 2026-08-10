"""SKEW01 outcome (c) -- reversal hazard: binary label = 1 if, within bars t+1..t+10 after a HOLD
bar t with position_B[t]=s (nonzero), EITHER action_B=='REVERSAL' occurs OR sign(M)=-s at any bar
in that window (M crosses against the held position); else 0. Same HOLD-bar population as outcome
(b). Forward-only by construction (window starts at t+1), no sunk-P&L confound. Feature =
aligned_skewness_20/10 (aligned to the currently-held side), primary; raw also reported."""
import os
import sys
import json
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from stats_lib import run_cell, print_cell

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
N = 10

COLS = ["t_idx", "sess_date", "year", "is_health_only_bar", "M", "sigma460_atr_proxy_pts",
        "position_B", "action_B", "skewness_10", "skewness_20"]

df = pd.read_parquet(os.path.join(OUT, "skew01_bars_with_features.parquet"), columns=list(dict.fromkeys(COLS)))
df = df.sort_values("t_idx").reset_index(drop=True)
n = len(df)
assert (df["t_idx"].to_numpy() == np.arange(n)).all()

M = df["M"].to_numpy()
action_B = df["action_B"].to_numpy()
reversal_flag = (action_B == "REVERSAL")
against_long = M < 0    # M crosses against a LONG position
against_short = M > 0   # M crosses against a SHORT position
event_long = reversal_flag | against_long
event_short = reversal_flag | against_short


def any_within(event, t_idx, N):
    n_ = len(event)
    flag = np.zeros(len(t_idx), dtype=bool)
    checked = np.zeros(len(t_idx), dtype=bool)
    for k in range(1, N + 1):
        shifted = t_idx + k
        ok = shifted < n_
        flag[ok] |= event[shifted[ok]]
        checked |= ok
    out = flag.astype(float)
    out[~checked] = np.nan
    return out


hold = df[df["action_B"] == "HOLD"].copy()
assert (hold["position_B"] != 0).all()
t = hold["t_idx"].to_numpy()
s = np.sign(hold["position_B"].to_numpy())

hazard = np.full(len(hold), np.nan)
mask_long = s > 0
mask_short = s < 0
hazard[mask_long] = any_within(event_long, t[mask_long], N)
hazard[mask_short] = any_within(event_short, t[mask_short], N)
hold["hazard_10"] = hazard
hold["abs_M"] = hold["M"].abs()
for W in [10, 20]:
    hold[f"aligned_skewness_{W}"] = hold[f"skewness_{W}"] * s

print(f"HOLD bars: {len(hold)}  (canonical {(~hold.is_health_only_bar).sum()}, "
      f"health-only {hold.is_health_only_bar.sum()})")
canon = hold[~hold.is_health_only_bar]
print(f"baseline P(hazard_10=1) canonical = {canon['hazard_10'].mean():.4f}  "
      f"(long {canon[canon.position_B>0]['hazard_10'].mean():.4f}, "
      f"short {canon[canon.position_B<0]['hazard_10'].mean():.4f})")
hold.to_csv(os.path.join(OUT, "outcome_c_hazard_table.csv"), index=False)

results = []
for f in ["aligned_skewness_20", "skewness_20"]:
    res = run_cell(hold, f, "hazard_10", "abs_M", "sigma460_atr_proxy_pts", "year",
                    "is_health_only_bar", label=f"(c) reversal-hazard: {f} vs hazard_10")
    print_cell(res)
    results.append(res)

print("\n" + "=" * 100 + "\n10-BAR ROBUSTNESS (not a required cell, cross-check only)\n" + "=" * 100)
results_10bar = []
for f in ["aligned_skewness_10", "skewness_10"]:
    res = run_cell(hold, f, "hazard_10", "abs_M", "sigma460_atr_proxy_pts", "year",
                    "is_health_only_bar", label=f"(c)-10bar reversal-hazard: {f} vs hazard_10")
    print_cell(res)
    results_10bar.append(res)

with open(os.path.join(OUT, "outcome_c_results.json"), "w") as fh:
    json.dump({"primary_20bar": results, "robustness_10bar": results_10bar}, fh, indent=2, default=str)
print("\noutcome (c) complete.")
