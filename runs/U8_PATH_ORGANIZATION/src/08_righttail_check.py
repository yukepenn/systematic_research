"""U8 right-tail check -- for the single strongest (feature x outcome) cell among the 12 required
(20-bar primary) cells, per spec.yaml: check that feature's value distribution (at the bar-type
the winning outcome uses) across the top-20 all-time winning canonical-window blocks (Product-B:
sign(position_B) blocks for outcomes a/b/c; Product-A: sign(target_exposure_A) blocks for outcome
d), same discipline as every other family in this campaign (R1/R3/R4/R5/U3/U4/U5/U6).

Strongest cell determined by |residualized Spearman| across all 12 required cells (computed in
scripts 04-07): (a) entry-value perm_entropy_20 vs block net_pnl, residualized rho = -0.0698,
the largest magnitude and largest OLS delta-R^2 (+0.00547) of the 12. Right-tail check performed
on that cell below (Product-B, all blocks, canonical window)."""
import os
import json
import numpy as np
import pandas as pd

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")

WINNING_FEATURE = "entry_perm_entropy_20"
WINNING_OUTCOME_LABEL = "(a) entry-value: perm_entropy_20 vs block net_pnl"

block = pd.read_csv(os.path.join(OUT, "outcome_a_block_table.csv"))
canon = block[~block["entry_is_health_only"]].dropna(subset=[WINNING_FEATURE, "net_pnl"]).copy()
print(f"canonical Product-B blocks with valid {WINNING_FEATURE}: {len(canon)}")
print(f"population {WINNING_FEATURE}: mean={canon[WINNING_FEATURE].mean():.4f} "
      f"median={canon[WINNING_FEATURE].median():.4f} std={canon[WINNING_FEATURE].std():.4f}")

# negative correlation (higher entropy -> lower net_pnl) -> "bad" = top (high-entropy) tercile
terc = pd.qcut(canon[WINNING_FEATURE], 3, labels=["low_entropy(good)", "mid", "high_entropy(bad)"])
canon["entropy_tercile"] = terc
pop_bad_rate = (canon["entropy_tercile"] == "high_entropy(bad)").mean()
print(f"population base rate of 'bad' (high-entropy) tercile: {pop_bad_rate:.3f}")

top20 = canon.nlargest(20, "net_pnl")
bottom20 = canon.nsmallest(20, "net_pnl")

print("\n" + "=" * 100)
print(f"TOP-20 all-time winning Product-B blocks (canonical) -- {WINNING_FEATURE} distribution")
print("=" * 100)
cols = ["block_id_B", "side", "net_pnl", WINNING_FEATURE, "entropy_tercile"]
print(top20[cols].sort_values("net_pnl", ascending=False).to_string(index=False))
top20_bad = int((top20["entropy_tercile"] == "high_entropy(bad)").sum())
print(f"\n{top20_bad}/20 top winners are in the 'bad' (high-entropy) tercile "
      f"(population base rate {pop_bad_rate:.1%})")
print(f"top-20 mean {WINNING_FEATURE} = {top20[WINNING_FEATURE].mean():.4f} "
      f"(population mean {canon[WINNING_FEATURE].mean():.4f})")

print("\n" + "=" * 100)
print(f"BOTTOM-20 all-time losing Product-B blocks (canonical) -- {WINNING_FEATURE} distribution")
print("=" * 100)
print(bottom20[cols].sort_values("net_pnl").to_string(index=False))
bottom20_bad = int((bottom20["entropy_tercile"] == "high_entropy(bad)").sum())
print(f"\n{bottom20_bad}/20 bottom losers are in the 'bad' (high-entropy) tercile "
      f"(population base rate {pop_bad_rate:.1%})")
print(f"bottom-20 mean {WINNING_FEATURE} = {bottom20[WINNING_FEATURE].mean():.4f}")

# how many of the top-20 would be EXCLUDED by a naive hard filter requiring "good" (bottom
# tercile) entropy to enter -- the standard R1/R3/R4 style check
n_top20_excluded_by_hard_filter = int((top20["entropy_tercile"] != "low_entropy(good)").sum())
print(f"\nA naive hard filter requiring 'good' (low-entropy) tercile to enter would have EXCLUDED "
      f"{n_top20_excluded_by_hard_filter}/20 of these top winners (incl. the single largest: "
      f"${top20['net_pnl'].max():,.2f}, {WINNING_FEATURE}="
      f"{top20.loc[top20['net_pnl'].idxmax(), WINNING_FEATURE]:.4f}, tercile="
      f"{top20.loc[top20['net_pnl'].idxmax(), 'entropy_tercile']})")

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
    "largest_winner_tercile": str(top20.loc[top20["net_pnl"].idxmax(), "entropy_tercile"]),
}
top20.to_csv(os.path.join(OUT, "righttail_top20_blocks.csv"), index=False)
bottom20.to_csv(os.path.join(OUT, "righttail_bottom20_blocks.csv"), index=False)
with open(os.path.join(OUT, "righttail_summary.json"), "w") as fh:
    json.dump(summary, fh, indent=2)
print("\n" + json.dumps(summary, indent=2))
print("\nRight-tail check complete.")
