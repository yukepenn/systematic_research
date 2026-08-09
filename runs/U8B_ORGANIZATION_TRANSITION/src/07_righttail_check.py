"""U8B right-tail check -- for the single strongest (feature x outcome) cell among all 18 Stage-1
cells (outcome (a) MFE x reversal_rate_transition, resid rho=-0.0756, largest |resid rho| and one
of the largest delta-R^2 of the whole family): check that feature's value distribution (at the
block entry bar) across the top-20 all-time winning canonical-window Product-B blocks (ranked by
net_pnl, same discipline as R1/R3/R4/R5/U3/U4/U5/U6/U8) vs bottom-20 vs population base rate."""
import os
import json
import numpy as np
import pandas as pd

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
WINNING_FEATURE = "entry_reversal_rate_transition"
WINNING_OUTCOME_LABEL = "(a) MFE: reversal_rate_transition vs mfe_final"

block = pd.read_csv(os.path.join(OUT, "productB_block_table.csv"))
block["entry_is_health_only"] = block["entry_is_health_only"].astype(bool)
canon = block[~block["entry_is_health_only"]].dropna(subset=[WINNING_FEATURE, "net_pnl"]).copy()
print(f"canonical Product-B blocks with valid {WINNING_FEATURE}: {len(canon)}")
print(f"population {WINNING_FEATURE}: mean={canon[WINNING_FEATURE].mean():.4f} "
      f"median={canon[WINNING_FEATURE].median():.4f} std={canon[WINNING_FEATURE].std():.4f}")

# negative correlation (more negative transition -> higher MFE) -> "bad" = top (least-negative /
# most-positive, i.e. NOT becoming more organized) tercile
terc = pd.qcut(canon[WINNING_FEATURE], 3, labels=["low(good,becoming-organized)", "mid",
                                                    "high(bad,becoming-disorganized)"])
canon["transition_tercile"] = terc
pop_bad_rate = (canon["transition_tercile"] == "high(bad,becoming-disorganized)").mean()
print(f"population base rate of 'bad' (high/becoming-disorganized) tercile: {pop_bad_rate:.3f}")

# right-tail check is defined on the WINNING outcome's own ranking of blocks; U8 ranked by
# net_pnl for all its Product-B checks even when the winning outcome was itself net_pnl -- here
# the winning outcome is MFE, so top/bottom-20 are ranked by net_pnl (the campaign's own standing
# all-time-winner definition) exactly as U8 did, for direct comparability across families.
top20 = canon.nlargest(20, "net_pnl")
bottom20 = canon.nsmallest(20, "net_pnl")

print("\n" + "=" * 100)
print(f"TOP-20 all-time winning Product-B blocks (canonical, ranked by net_pnl) -- {WINNING_FEATURE} distribution")
print("=" * 100)
cols = ["block_id_B", "side", "net_pnl", "mfe_final", WINNING_FEATURE, "transition_tercile"]
print(top20[cols].sort_values("net_pnl", ascending=False).to_string(index=False))
top20_bad = int((top20["transition_tercile"] == "high(bad,becoming-disorganized)").sum())
print(f"\n{top20_bad}/20 top winners are in the 'bad' (becoming-disorganized) tercile "
      f"(population base rate {pop_bad_rate:.1%})")
print(f"top-20 mean {WINNING_FEATURE} = {top20[WINNING_FEATURE].mean():.4f} "
      f"(population mean {canon[WINNING_FEATURE].mean():.4f})")

print("\n" + "=" * 100)
print(f"BOTTOM-20 all-time losing Product-B blocks (canonical) -- {WINNING_FEATURE} distribution")
print("=" * 100)
print(bottom20[cols].sort_values("net_pnl").to_string(index=False))
bottom20_bad = int((bottom20["transition_tercile"] == "high(bad,becoming-disorganized)").sum())
print(f"\n{bottom20_bad}/20 bottom losers are in the 'bad' (becoming-disorganized) tercile "
      f"(population base rate {pop_bad_rate:.1%})")
print(f"bottom-20 mean {WINNING_FEATURE} = {bottom20[WINNING_FEATURE].mean():.4f}")

n_top20_excluded_by_hard_filter = int((top20["transition_tercile"] != "low(good,becoming-organized)").sum())
print(f"\nA naive hard filter requiring 'good' (low/becoming-organized) tercile to enter would have "
      f"EXCLUDED {n_top20_excluded_by_hard_filter}/20 of these top winners (incl. the single largest: "
      f"${top20['net_pnl'].max():,.2f}, {WINNING_FEATURE}="
      f"{top20.loc[top20['net_pnl'].idxmax(), WINNING_FEATURE]:.4f}, tercile="
      f"{top20.loc[top20['net_pnl'].idxmax(), 'transition_tercile']})")

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
    "largest_winner_tercile": str(top20.loc[top20["net_pnl"].idxmax(), "transition_tercile"]),
}
top20.to_csv(os.path.join(OUT, "righttail_top20_blocks.csv"), index=False)
bottom20.to_csv(os.path.join(OUT, "righttail_bottom20_blocks.csv"), index=False)
with open(os.path.join(OUT, "righttail_summary.json"), "w") as fh:
    json.dump(summary, fh, indent=2)
print("\n" + json.dumps(summary, indent=2))
print("\nRight-tail check complete.")
