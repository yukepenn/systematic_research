"""U8B Step 0 -- MANDATORY FIRST, run before any outcome test.
(A) transition features vs U8's own LEVEL features (perm_entropy_20, reversal_rate_20).
(B) transition features vs U0's own M_change, M_slope_20 (momentum's own rate-of-change).
(C) empirical mirror check: reversal_rate_transition vs run_persistence_transition.
Any |rho|>0.7 in (A) or (B) is flagged REDUNDANT."""
import os
import json
import numpy as np
import pandas as pd

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
TRANSITION_FEATURES = ["perm_entropy_transition", "reversal_rate_transition", "run_persistence_transition"]
LEVEL_TARGETS = ["perm_entropy_20", "reversal_rate_20"]
MOMENTUM_TARGETS = ["M_change", "M_slope_20"]

df = pd.read_parquet(os.path.join(OUT, "u8b_bars_with_transition.parquet"))
canon = df[~df["is_health_only_bar"]].copy()
print(f"canonical bars: {len(canon)}")

rows = []
for feat in TRANSITION_FEATURES:
    for tgt in LEVEL_TARGETS + MOMENTUM_TARGETS:
        sub = canon.dropna(subset=[feat, tgt])
        rho = float(sub[feat].corr(sub[tgt], method="spearman"))
        group = "A_level_adjacency" if tgt in LEVEL_TARGETS else "B_momentum_rate_of_change_adjacency"
        flagged = abs(rho) > 0.7
        rows.append({"group": group, "feature": feat, "target": tgt, "n": len(sub),
                      "spearman": rho, "redundant_flag": flagged})
        print(f"  [{group}] {feat} vs {tgt}: rho={rho:+.4f}  n={len(sub)}  "
              f"{'*** REDUNDANT (|rho|>0.7) ***' if flagged else ''}")

redund_df = pd.DataFrame(rows)
redund_df.to_csv(os.path.join(OUT, "step0_redundancy.csv"), index=False)

# (C) mirror check: empirical, not assumed
sub_mirror = canon.dropna(subset=["reversal_rate_transition", "run_persistence_transition"])
mirror_rho = float(sub_mirror["reversal_rate_transition"].corr(sub_mirror["run_persistence_transition"], method="spearman"))
print(f"\n(C) mirror check: reversal_rate_transition vs run_persistence_transition rho={mirror_rho:+.6f} "
      f"(n={len(sub_mirror)})  [U8's single-window level features were EXACTLY -1.000 by construction; "
      f"this is the transition (difference-of-two-windows) version, verified empirically, not assumed]")

any_redundant = bool(redund_df["redundant_flag"].any())
max_abs_rho = float(redund_df["spearman"].abs().max())
summary = {
    "n_canonical_bars": int(len(canon)),
    "max_abs_rho_vs_level_or_momentum": max_abs_rho,
    "any_flagged_redundant_gt_0.7": any_redundant,
    "mirror_check_reversal_rate_vs_run_persistence_transition_rho": mirror_rho,
}
with open(os.path.join(OUT, "step0_summary.json"), "w") as fh:
    json.dump(summary, fh, indent=2)
print("\n" + json.dumps(summary, indent=2))
print("\nStep 0 complete." + (" *** REDUNDANCY FLAGGED ***" if any_redundant else " No feature flagged redundant."))
