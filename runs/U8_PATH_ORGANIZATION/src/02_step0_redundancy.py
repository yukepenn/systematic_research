"""U8 Step 0 -- MANDATORY redundancy check (per spec.yaml / campaign standing rule): raw Spearman
correlation, bar level, canonical window only, of all 6 new path-organization features against
U0's own trend_efficiency_20 and range_efficiency_20. |rho|>0.7 => flag REDUNDANT."""
import os
import json
import pandas as pd

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
FEATURES = ["reversal_rate_10", "run_persistence_10", "perm_entropy_10",
            "reversal_rate_20", "run_persistence_20", "perm_entropy_20"]
EXISTING = ["trend_efficiency_20", "range_efficiency_20"]

df = pd.read_parquet(os.path.join(OUT, "u8_bars_with_features.parquet"),
                      columns=["is_health_only_bar"] + FEATURES + EXISTING)
canon = df[~df["is_health_only_bar"]].copy()
print(f"canonical bars: {len(canon)}")

rows = []
for f in FEATURES:
    for e in EXISTING:
        sub = canon[[f, e]].dropna()
        rho = float(sub[f].corr(sub[e], method="spearman"))
        rows.append({"feature": f, "existing_column": e, "n": len(sub), "spearman": rho,
                     "flag_redundant": bool(abs(rho) > 0.7)})

res = pd.DataFrame(rows)
print("=" * 100)
print("STEP 0 -- REDUNDANCY CHECK (raw Spearman, canonical window)")
print("=" * 100)
print(res.to_string(index=False))

# also feature-vs-feature (10 vs 20 bar version of the same construction), and cross-feature,
# for interpretive context only (not part of the redundancy gate against EXISTING columns)
print("\n--- context only: new-feature-vs-new-feature raw Spearman (canonical) ---")
corr_mat = canon[FEATURES].corr(method="spearman")
print(corr_mat.round(3).to_string())

any_flag = bool(res["flag_redundant"].any())
summary = {
    "n_canonical_bars": int(len(canon)),
    "any_redundant_flagged": any_flag,
    "flagged_pairs": res[res["flag_redundant"]][["feature", "existing_column", "spearman"]].to_dict("records"),
    "max_abs_rho": float(res["spearman"].abs().max()),
}
res.to_csv(os.path.join(OUT, "step0_redundancy.csv"), index=False)
corr_mat.to_csv(os.path.join(OUT, "step0_feature_intercorr.csv"))
with open(os.path.join(OUT, "step0_summary.json"), "w") as fh:
    json.dump(summary, fh, indent=2)
print("\n" + json.dumps(summary, indent=2))
print("\nStep 0 complete.")
