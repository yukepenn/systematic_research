"""SKEW01 right-tail check -- for the single strongest (feature x outcome) cell among all 8
primary (20-bar) cells (determined in 08_toogoodtobetrue_check.py's scan): (c) reversal-hazard,
aligned_skewness_20, residualized Spearman = +0.0467 (largest magnitude of the 8; the next-
largest is (d) aligned_skewness_20 at +0.0266). Outcome (c) is a bar-level HOLD-bar hazard label,
not a block-level P&L outcome, so per spec.yaml's "at the bar-type the outcome uses" convention,
the right-tail check is performed at the BLOCK level using each canonical Product-B block's own
MEAN aligned_skewness_20 over its own HOLD bars (the same population outcome (c) draws its
per-bar observations from), ranked against block-level net_pnl (from outcome (a)'s block table) --
same discipline as R4/R5/U8/U8B."""
import os
import json
import numpy as np
import pandas as pd

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")

WINNING_FEATURE = "hold_mean_aligned_skewness_20"
WINNING_OUTCOME_LABEL = "(c) reversal-hazard: aligned_skewness_20 vs hazard_10 (strongest of 8 primary cells, resid rho=+0.0467)"

# block-level net_pnl + canonical flag, from outcome (a)'s already-built block table
block = pd.read_csv(os.path.join(OUT, "outcome_a_block_table.csv"))
block = block[["block_id_B", "side", "net_pnl", "entry_is_health_only"]]

# bar-level table for aligned_skewness_20 on this block's own HOLD bars
bars = pd.read_parquet(os.path.join(OUT, "skew01_bars_with_features.parquet"),
                        columns=["t_idx", "block_id_B", "action_B", "position_B",
                                 "is_health_only_bar", "skewness_20"])
hold = bars[bars["action_B"] == "HOLD"].copy()
hold["aligned_skewness_20"] = hold["skewness_20"] * np.sign(hold["position_B"])

per_block = hold.groupby("block_id_B")["aligned_skewness_20"].mean().rename(WINNING_FEATURE)
n_hold_per_block = hold.groupby("block_id_B").size().rename("n_hold_bars")

merged = block.merge(per_block, on="block_id_B", how="left").merge(n_hold_per_block, on="block_id_B", how="left")
canon = merged[~merged["entry_is_health_only"]].dropna(subset=[WINNING_FEATURE, "net_pnl"]).copy()
print(f"canonical Product-B blocks with >=1 HOLD bar and valid {WINNING_FEATURE}: {len(canon)} "
      f"(of {len(merged[~merged['entry_is_health_only']])} total canonical blocks -- blocks with "
      f"zero HOLD bars, i.e. entry immediately followed by exit, are excluded, consistent with "
      f"outcome (c)'s own HOLD-bar-only population)")
print(f"population {WINNING_FEATURE}: mean={canon[WINNING_FEATURE].mean():.4f} "
      f"median={canon[WINNING_FEATURE].median():.4f} std={canon[WINNING_FEATURE].std():.4f}")

# positive resid rho: higher aligned_skewness_20 (skew in the trade's own favor) -> HIGHER
# reversal hazard (an "exhaustion" story) -> "bad" = top (high aligned-skew) tercile
terc = pd.qcut(canon[WINNING_FEATURE], 3, labels=["low(good)", "mid", "high(bad,exhaustion-risk)"])
canon["skew_tercile"] = terc
pop_bad_rate = (canon["skew_tercile"] == "high(bad,exhaustion-risk)").mean()
print(f"population base rate of 'bad' (high aligned-skew, exhaustion-risk) tercile: {pop_bad_rate:.3f}")

top20 = canon.nlargest(20, "net_pnl")
bottom20 = canon.nsmallest(20, "net_pnl")

print("\n" + "=" * 100)
print(f"TOP-20 all-time winning Product-B blocks (canonical) -- {WINNING_FEATURE} distribution")
print("=" * 100)
cols = ["block_id_B", "side", "net_pnl", "n_hold_bars", WINNING_FEATURE, "skew_tercile"]
print(top20[cols].sort_values("net_pnl", ascending=False).to_string(index=False))
top20_bad = int((top20["skew_tercile"] == "high(bad,exhaustion-risk)").sum())
print(f"\n{top20_bad}/20 top winners are in the 'bad' (high aligned-skew) tercile "
      f"(population base rate {pop_bad_rate:.1%})")
print(f"top-20 mean {WINNING_FEATURE} = {top20[WINNING_FEATURE].mean():.4f} "
      f"(population mean {canon[WINNING_FEATURE].mean():.4f})")

print("\n" + "=" * 100)
print(f"BOTTOM-20 all-time losing Product-B blocks (canonical) -- {WINNING_FEATURE} distribution")
print("=" * 100)
print(bottom20[cols].sort_values("net_pnl").to_string(index=False))
bottom20_bad = int((bottom20["skew_tercile"] == "high(bad,exhaustion-risk)").sum())
print(f"\n{bottom20_bad}/20 bottom losers are in the 'bad' (high aligned-skew) tercile "
      f"(population base rate {pop_bad_rate:.1%})")
print(f"bottom-20 mean {WINNING_FEATURE} = {bottom20[WINNING_FEATURE].mean():.4f}")

n_top20_excluded_by_hard_filter = int((top20["skew_tercile"] != "low(good)").sum())
print(f"\nA naive hard filter requiring 'good' (low aligned-skew) tercile to hold through would "
      f"have flagged/excluded {n_top20_excluded_by_hard_filter}/20 of these top winners "
      f"(incl. the single largest: ${top20['net_pnl'].max():,.2f}, {WINNING_FEATURE}="
      f"{top20.loc[top20['net_pnl'].idxmax(), WINNING_FEATURE]:.4f}, tercile="
      f"{top20.loc[top20['net_pnl'].idxmax(), 'skew_tercile']})")

summary = {
    "winning_cell": WINNING_OUTCOME_LABEL,
    "winning_feature": WINNING_FEATURE,
    "n_canonical_blocks": len(canon),
    "population_bad_tercile_rate": float(pop_bad_rate),
    "top20_n_bad_tercile": top20_bad,
    "top20_n_excluded_by_hard_good_filter": n_top20_excluded_by_hard_filter,
    "bottom20_n_bad_tercile": bottom20_bad,
    "top20_mean_feature": float(top20[WINNING_FEATURE].mean()),
    "bottom20_mean_feature": float(bottom20[WINNING_FEATURE].mean()),
    "population_mean_feature": float(canon[WINNING_FEATURE].mean()),
    "largest_winner_net_pnl": float(top20["net_pnl"].max()),
    "largest_winner_feature_value": float(top20.loc[top20["net_pnl"].idxmax(), WINNING_FEATURE]),
    "largest_winner_tercile": str(top20.loc[top20["net_pnl"].idxmax(), "skew_tercile"]),
}
top20.to_csv(os.path.join(OUT, "righttail_top20_blocks.csv"), index=False)
bottom20.to_csv(os.path.join(OUT, "righttail_bottom20_blocks.csv"), index=False)
with open(os.path.join(OUT, "righttail_summary.json"), "w") as fh:
    json.dump(summary, fh, indent=2)
print("\n" + json.dumps(summary, indent=2))
print("\nRight-tail check complete.")
