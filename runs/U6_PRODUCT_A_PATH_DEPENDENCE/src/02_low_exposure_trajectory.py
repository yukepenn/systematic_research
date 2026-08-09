"""U6 step2 -- path-dependence of low-exposure states: at the FIRST bar of a block that starts
with |target_exposure_A|<=3, can any causal feature distinguish blocks that will LATER scale to
>=7 contracts ("low-to-high") from blocks that never exceed 3 for the rest of their life
("stayed-low")? Per spec.yaml plan step2/3/4. Also step3 right-tail check, step4 chronology."""
import os, json
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu

import u6_substrate as U

OUT = U.OUT
RNG = np.random.default_rng(20260809)
FEATS = U.CAUSAL_FEATURES_STEP2  # age_bars_A dropped -- degenerate (==1) at every row tested here

block = pd.read_csv(os.path.join(OUT, "u6_block_table.csv"))
feat = pd.read_parquet(os.path.join(OUT, "u6_causal_features.parquet")).set_index("t_idx")

block["abs_start_exposure"] = block["start_exposure"].abs()
low = block[block["abs_start_exposure"] <= 3].copy()
low_feat = feat.loc[low["t_idx_start"].to_numpy()].reset_index(drop=True)
for f in FEATS:
    low[f] = low_feat[f].to_numpy()

low["trajectory"] = np.select(
    [low["max_abs_exposure"] >= 7, low["max_abs_exposure"] <= 3],
    ["low_to_high", "stayed_low"], default="mid")

print(f"low-starting blocks (|start_exposure|<=3): {len(low)} total "
      f"({(~low.start_is_health_only).sum()} canonical / {low.start_is_health_only.sum()} extended)")

low_can = low[~low["start_is_health_only"]].copy()
print(low_can["trajectory"].value_counts())

print("\n" + "=" * 95, "\nSTEP2 -- MANN-WHITNEY U + BOOTSTRAP: low_to_high vs stayed_low, features AS OF the block's FIRST bar (canonical)\n", "=" * 95, sep="")


def bootstrap_mean_diff(a, b, n_boot=2000):
    a = a.to_numpy(); b = b.to_numpy()
    diffs = np.empty(n_boot)
    for i in range(n_boot):
        diffs[i] = RNG.choice(a, size=len(a), replace=True).mean() - RNG.choice(b, size=len(b), replace=True).mean()
    return np.percentile(diffs, [2.5, 97.5])


rows = []
lh = low_can[low_can.trajectory == "low_to_high"]
sl = low_can[low_can.trajectory == "stayed_low"]
for f in FEATS:
    a = lh[f].dropna(); b = sl[f].dropna()
    u_stat, p = mannwhitneyu(a, b, alternative="two-sided")
    reff = 2 * u_stat / (len(a) * len(b)) - 1
    ci_lo, ci_hi = bootstrap_mean_diff(a, b)
    rows.append({"feature": f, "low_to_high_mean": a.mean(), "low_to_high_median": a.median(),
                 "stayed_low_mean": b.mean(), "stayed_low_median": b.median(),
                 "mean_diff": a.mean() - b.mean(), "boot_ci95_lo": ci_lo, "boot_ci95_hi": ci_hi,
                 "ci_excludes_0": not (ci_lo <= 0 <= ci_hi),
                 "mannwhitney_p": p, "rank_biserial_effect": reff, "n_lh": len(a), "n_sl": len(b)})
step2 = pd.DataFrame(rows).reindex(pd.DataFrame(rows)["rank_biserial_effect"].abs().sort_values(ascending=False).index)
print(step2.round(5).to_string(index=False))
step2.to_csv(os.path.join(OUT, "step2_low_to_high_vs_stayed_low.csv"), index=False)

print("\n" + "=" * 95, "\nSTEP2(ii) -- ROBUSTNESS: continuous Spearman, feature (first bar) vs eventual max|exposure| (all low-starting canonical blocks incl. mid)\n", "=" * 95, sep="")
rows2 = []
for f in FEATS:
    sub = low_can.dropna(subset=[f, "max_abs_exposure"])
    rho = float(sub[f].corr(sub["max_abs_exposure"], method="spearman"))
    rows2.append({"feature": f, "spearman_vs_eventual_maxabs": rho, "n": len(sub)})
step2b = pd.DataFrame(rows2).reindex(pd.DataFrame(rows2)["spearman_vs_eventual_maxabs"].abs().sort_values(ascending=False).index)
print(step2b.round(5).to_string(index=False))
step2b.to_csv(os.path.join(OUT, "step2b_continuous_spearman_vs_maxabs.csv"), index=False)

best_feat = step2.iloc[0]["feature"]
best_reff = step2.iloc[0]["rank_biserial_effect"]
best_p = step2.iloc[0]["mannwhitney_p"]
top3_feats = step2["feature"].tolist()[:3]
print(f"\nstrongest separating feature (by |rank-biserial effect|): {best_feat} "
      f"(effect={best_reff:.4f}, p={best_p:.4g})")
print(f"top-3 by |rank-biserial effect|: {top3_feats}")

print("\n" + "=" * 95, f"\nSTEP4 -- CHRONOLOGY of top-3 features' separation, year-by-year (canonical) + extended (2026-06/07) separate\n", "=" * 95, sep="")
all_yby = []
for feat_name in top3_feats:
    yby = []
    for yr, g in low_can.groupby("start_year"):
        if yr == 2026:
            continue
        a = g.loc[g.trajectory == "low_to_high", feat_name].dropna()
        b = g.loc[g.trajectory == "stayed_low", feat_name].dropna()
        if len(a) < 5 or len(b) < 5:
            yby.append({"feature": feat_name, "year": int(yr), "n_lh": len(a), "n_sl": len(b),
                        "mean_diff": np.nan, "note": "n too small"})
            continue
        u_stat, p = mannwhitneyu(a, b, alternative="two-sided")
        reff = 2 * u_stat / (len(a) * len(b)) - 1
        yby.append({"feature": feat_name, "year": int(yr), "n_lh": len(a), "n_sl": len(b),
                    "mean_diff": a.mean() - b.mean(), "rank_biserial_effect": reff, "mannwhitney_p": p, "note": ""})
    g26 = low_can[low_can.start_year == 2026]
    a26 = g26.loc[g26.trajectory == "low_to_high", feat_name].dropna()
    b26 = g26.loc[g26.trajectory == "stayed_low", feat_name].dropna()
    if len(a26) >= 5 and len(b26) >= 5:
        u_stat, p = mannwhitneyu(a26, b26, alternative="two-sided")
        reff = 2 * u_stat / (len(a26) * len(b26)) - 1
        yby.append({"feature": feat_name, "year": "2026 (canonical Jan-May)", "n_lh": len(a26), "n_sl": len(b26),
                    "mean_diff": a26.mean() - b26.mean(), "rank_biserial_effect": reff, "mannwhitney_p": p, "note": ""})
    else:
        yby.append({"feature": feat_name, "year": "2026 (canonical Jan-May)", "n_lh": len(a26), "n_sl": len(b26),
                    "mean_diff": np.nan, "note": "n too small"})
    yby_df_f = pd.DataFrame(yby)
    print(f"\n--- {feat_name} ---")
    print(yby_df_f.round(4).to_string(index=False))
    all_yby.append(yby_df_f)
yby_df = pd.concat(all_yby, ignore_index=True)
yby_df.to_csv(os.path.join(OUT, "step4_year_by_year_top3_features.csv"), index=False)

low_ext = low[low.start_is_health_only].copy()
print(f"\nextended window (2026-06/07): {len(low_ext)} low-starting blocks -- "
      f"{(low_ext.trajectory=='low_to_high').sum()} low_to_high / {(low_ext.trajectory=='stayed_low').sum()} stayed_low / "
      f"{(low_ext.trajectory=='mid').sum()} mid")
a_ext = low_ext.loc[low_ext.trajectory == "low_to_high", best_feat].dropna()
b_ext = low_ext.loc[low_ext.trajectory == "stayed_low", best_feat].dropna()
if len(a_ext) >= 5 and len(b_ext) >= 5:
    u_stat, p_ext = mannwhitneyu(a_ext, b_ext, alternative="two-sided")
    reff_ext = 2 * u_stat / (len(a_ext) * len(b_ext)) - 1
    print(f"{best_feat}: low_to_high mean={a_ext.mean():.4f} (n={len(a_ext)}), "
          f"stayed_low mean={b_ext.mean():.4f} (n={len(b_ext)}), effect={reff_ext:.4f}, p={p_ext:.4g}")
else:
    reff_ext, p_ext = np.nan, np.nan
    print(f"n too small for a meaningful test (n_lh={len(a_ext)}, n_sl={len(b_ext)})")

print("\n" + "=" * 95, "\nSTEP3 -- RIGHT-TAIL CHECK: did the best/worst blocks START in the 1-3-contract low-exposure state?\n", "=" * 95, sep="")
canon_blocks = block[~block["start_is_health_only"]].copy()
top20 = canon_blocks.nlargest(20, "net_pnl")
bot20 = canon_blocks.nsmallest(20, "net_pnl")
top20_low_frac = (top20["abs_start_exposure"] <= 3).mean()
bot20_low_frac = (bot20["abs_start_exposure"] <= 3).mean()
print(f"top-20 all-time winning blocks (canonical window): net_pnl range "
      f"${top20['net_pnl'].min():,.2f} to ${top20['net_pnl'].max():,.2f}")
print(f"  -> {int((top20['abs_start_exposure']<=3).sum())}/20 ({top20_low_frac:.0%}) STARTED in the 1-3-contract low-exposure state")
print(f"bottom-20 all-time losing blocks (canonical window): net_pnl range "
      f"${bot20['net_pnl'].min():,.2f} to ${bot20['net_pnl'].max():,.2f}")
print(f"  -> {int((bot20['abs_start_exposure']<=3).sum())}/20 ({bot20_low_frac:.0%}) STARTED in the 1-3-contract low-exposure state")
top20.to_csv(os.path.join(OUT, "step3_top20_blocks.csv"), index=False)
bot20.to_csv(os.path.join(OUT, "step3_bottom20_blocks.csv"), index=False)
print(f"\n(for reference, {(canon_blocks['abs_start_exposure']<=3).mean():.1%} of ALL {len(canon_blocks)} "
      f"canonical nonzero blocks start in the 1-3-contract state)")

summary = {
    "n_low_starting_blocks_canonical": int(len(low_can)),
    "n_low_to_high": int((low_can.trajectory == "low_to_high").sum()),
    "n_stayed_low": int((low_can.trajectory == "stayed_low").sum()),
    "n_mid": int((low_can.trajectory == "mid").sum()),
    "top3_features_by_effect": top3_feats,
    "step2_full_table": step2.to_dict(orient="records"),
    "best_separating_feature": best_feat,
    "best_feature_rank_biserial_effect": float(best_reff),
    "best_feature_mannwhitney_p": float(best_p),
    "extended_window_same_feature_effect": None if np.isnan(reff_ext) else float(reff_ext),
    "extended_window_same_feature_p": None if np.isnan(p_ext) else float(p_ext),
    "top20_started_low_frac": float(top20_low_frac),
    "bottom20_started_low_frac": float(bot20_low_frac),
    "all_canonical_blocks_started_low_frac": float((canon_blocks['abs_start_exposure'] <= 3).mean()),
}
json.dump(summary, open(os.path.join(OUT, "step2_3_4_summary.json"), "w"), indent=2)
print("\n" + json.dumps(summary, indent=2))
print("\nstep2/3/4 complete.")
