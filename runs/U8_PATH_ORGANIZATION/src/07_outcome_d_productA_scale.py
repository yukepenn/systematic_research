"""U8 outcome (d) -- Product-A scale value: forward-20-bar bar_pnl_A_dollars summed and divided
by |target_exposure_A delta| (contracts_changed), U6's own exact fwd20_pnl_per_contract
construction, evaluated ONLY at action_A=='SCALE_IN' bars, feature measured at that same bar
(forward-only outcome, no sunk-P&L confound)."""
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
FWD = 20  # PA0/U6's own forward window

COLS = ["t_idx", "sess_date", "year", "is_health_only_bar", "M_A_raw", "sigma460_atr_proxy_pts",
        "target_exposure_A", "action_A", "bar_pnl_A_dollars"] + FEATURES_10 + FEATURES_20

df = pd.read_parquet(os.path.join(OUT, "u8_bars_with_features.parquet"), columns=COLS)
df = df.sort_values("t_idx").reset_index(drop=True)
n = len(df)
assert (df["t_idx"].to_numpy() == np.arange(n)).all()

pos = df["target_exposure_A"].to_numpy()
bpnl = df["bar_pnl_A_dollars"].to_numpy()

is_scalein = (df["action_A"] == "SCALE_IN").to_numpy()
idx = np.where(is_scalein)[0]
idx = idx[idx > 0]

contracts_changed = np.abs(pos[idx] - pos[idx - 1])
fwd20 = np.array([bpnl[t: min(t + FWD, n)].sum() for t in idx])
per_contract = fwd20 / contracts_changed

ev = df.iloc[idx].copy()
ev["fwd20_pnl_per_contract"] = per_contract
ev["abs_M_A"] = ev["M_A_raw"].abs()

print(f"Product-A SCALE_IN events: {len(ev)}  (canonical {(~ev.is_health_only_bar).sum()}, "
      f"health-only {ev.is_health_only_bar.sum()})")
canon = ev[~ev.is_health_only_bar]
print(f"baseline fwd20_pnl_per_contract mean (canonical) = ${canon['fwd20_pnl_per_contract'].mean():.2f}  "
      f"(cross-check vs U6/PA0's own +$14.43 SCALE_IN headline)")
ev.to_csv(os.path.join(OUT, "outcome_d_scalein_table.csv"), index=False)

results = []
for f in FEATURES_20:
    res = run_cell(ev, f, "fwd20_pnl_per_contract", "abs_M_A", "sigma460_atr_proxy_pts", "year",
                    "is_health_only_bar", label=f"(d) Product-A scale value: {f} vs fwd20_pnl_per_contract")
    print_cell(res)
    results.append(res)

print("\n" + "=" * 100 + "\n10-BAR ROBUSTNESS (not a required cell, cross-check only)\n" + "=" * 100)
results_10bar = []
for f in FEATURES_10:
    res = run_cell(ev, f, "fwd20_pnl_per_contract", "abs_M_A", "sigma460_atr_proxy_pts", "year",
                    "is_health_only_bar", label=f"(d)-10bar Product-A scale value: {f} vs fwd20_pnl_per_contract")
    print_cell(res)
    results_10bar.append(res)

with open(os.path.join(OUT, "outcome_d_results.json"), "w") as fh:
    json.dump({"primary_20bar": results, "robustness_10bar": results_10bar}, fh, indent=2, default=str)
print("\noutcome (d) complete.")
