"""SKEW01 Step 0 -- MANDATORY redundancy check (per spec.yaml / campaign standing rule): raw
Spearman correlation, bar level, canonical window only, of skewness_10/skewness_20 against
(a) U8's own already-computed perm_entropy_20/reversal_rate_20/run_persistence_20 (reused via
merge, not re-derived) and (b) U0's own trend_efficiency_20/range_efficiency_20/M_slope_20/
sigma460_atr_proxy_pts. |rho|>0.7 => flag REDUNDANT."""
import os
import json
import pandas as pd

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
FEATURES = ["skewness_10", "skewness_20"]
EXISTING_U8 = ["perm_entropy_20", "reversal_rate_20", "run_persistence_20"]
EXISTING_U0 = ["trend_efficiency_20", "range_efficiency_20", "M_slope_20", "sigma460_atr_proxy_pts"]
EXISTING = EXISTING_U8 + EXISTING_U0

df = pd.read_parquet(os.path.join(OUT, "skew01_bars_with_features.parquet"),
                      columns=["is_health_only_bar"] + FEATURES + EXISTING)
canon = df[~df["is_health_only_bar"]].copy()
print(f"canonical bars: {len(canon)}")

rows = []
for f in FEATURES:
    for e in EXISTING:
        sub = canon[[f, e]].dropna()
        rho = float(sub[f].corr(sub[e], method="spearman"))
        rows.append({"feature": f, "existing_column": e, "n": len(sub), "spearman": rho,
                     "flag_redundant": bool(abs(rho) > 0.7),
                     "source": "U8 (reused, not re-derived)" if e in EXISTING_U8 else "U0 (native)"})

res = pd.DataFrame(rows)
print("=" * 100)
print("STEP 0 -- REDUNDANCY CHECK (raw Spearman, canonical window)")
print("=" * 100)
print(res.to_string(index=False))

print("\n--- context only: skewness_10 vs skewness_20 raw Spearman (canonical) ---")
sub = canon[FEATURES].dropna()
print(f"rho(skewness_10, skewness_20) = {sub['skewness_10'].corr(sub['skewness_20'], method='spearman'):.4f}  n={len(sub)}")

any_flag = bool(res["flag_redundant"].any())
summary = {
    "n_canonical_bars": int(len(canon)),
    "any_redundant_flagged": any_flag,
    "flagged_pairs": res[res["flag_redundant"]][["feature", "existing_column", "spearman"]].to_dict("records"),
    "max_abs_rho": float(res["spearman"].abs().max()),
    "max_abs_rho_pair": res.loc[res["spearman"].abs().idxmax(), ["feature", "existing_column"]].to_dict(),
}
res.to_csv(os.path.join(OUT, "step0_redundancy.csv"), index=False)
with open(os.path.join(OUT, "step0_summary.json"), "w") as fh:
    json.dump(summary, fh, indent=2)
print("\n" + json.dumps(summary, indent=2))
print("\nStep 0 complete.")
