"""U8B outcome (f) -- Product-A incremental scale value: IDENTICAL construction to U8 outcome
(d) / U6's own fwd20_pnl_per_contract (copied verbatim): forward-20-bar bar_pnl_A_dollars summed
and divided by |target_exposure_A delta|, evaluated ONLY at action_A=='SCALE_IN' bars, feature =
organization TRANSITION measured at that same bar, m_abs = |M_A_raw| (matching U6's own
conviction-magnitude convention for this product)."""
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
FWD = 20  # PA0/U6/U8's own forward window

COLS = ["t_idx", "sess_date", "year", "is_health_only_bar", "is_rth", "M_A_raw",
        "sigma460_atr_proxy_pts", "target_exposure_A", "action_A", "bar_pnl_A_dollars"] + FEATURES

df = pd.read_parquet(os.path.join(OUT, "u8b_bars_with_transition.parquet"), columns=COLS)
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
      f"(cross-check vs U6/PA0/U8's own +$14.43 SCALE_IN headline)")
ev.to_csv(os.path.join(OUT, "outcome_f_scalein_table.csv"), index=False)

stage1 = []
for f in FEATURES:
    res = run_cell(ev, f, "fwd20_pnl_per_contract", "abs_M_A", "sigma460_atr_proxy_pts", "year",
                    "is_health_only_bar", label=f"(f) Product-A scale value: {f} vs fwd20_pnl_per_contract")
    print_cell(res)
    stage1.append(res)

stage2 = []
for f in INDEPENDENT_FEATURES:
    res2 = interaction_cell(ev, f, "fwd20_pnl_per_contract", "abs_M_A", "sigma460_atr_proxy_pts",
                             "is_health_only_bar", label=f"(f) Product-A scale value: {f} x |M_A_raw| interaction")
    print_interaction_cell(res2)
    stage2.append(res2)

with open(os.path.join(OUT, "outcome_f_stage1.json"), "w") as fh:
    json.dump(stage1, fh, indent=2, default=str)
with open(os.path.join(OUT, "outcome_f_stage2.json"), "w") as fh:
    json.dump(stage2, fh, indent=2, default=str)
print("\noutcome (f) complete.")
