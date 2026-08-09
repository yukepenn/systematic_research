"""U8B -- build the Product-B block-level table shared by outcomes (a) MFE, (b) MAE, (d)
bars_to_mfe, (e) top-decile-winner probability. One row per Product-B block (long+short,
canonical+health-only), feature measured at the block's own entry bar (age_bars_B==1, strictly
precedes all of the block's own P&L), outcomes measured from the block's own FINAL running
values (U0's own already-certified MFE_B_dollars/MAE_B_dollars/run_pnl_B_dollars columns) or, for
bars_to_mfe, the argmax of the block's own real run_pnl_B_dollars path (checked
block_level_summary.csv first -- no reusable timing-to-peak column there, so built here from the
real per-bar running P&L, matching SHADOW01's own argmax convention but on real, not proxy,
pricing)."""
import os
import json
import numpy as np
import pandas as pd

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
FEATURES = ["perm_entropy_transition", "reversal_rate_transition", "run_persistence_transition"]
LEVEL_FEATURES = ["perm_entropy_20", "reversal_rate_20", "run_persistence_20",
                   "perm_entropy_10", "reversal_rate_10", "run_persistence_10"]

COLS = ["t_idx", "sess_date", "year", "is_health_only_bar", "is_rth", "M", "sigma460_atr_proxy_pts",
        "position_B", "action_B", "block_id_B", "age_bars_B", "run_pnl_B_dollars",
        "MFE_B_dollars", "MAE_B_dollars"] + FEATURES + LEVEL_FEATURES

df = pd.read_parquet(os.path.join(OUT, "u8b_bars_with_transition.parquet"), columns=COLS)
df = df.sort_values("t_idx").reset_index(drop=True)
n = len(df)
assert (df["t_idx"].to_numpy() == np.arange(n)).all()

nz = df[df["position_B"] != 0]
block_ids = nz["block_id_B"].unique()
print(f"building Product-B block table (all blocks, long+short): {len(block_ids)} blocks")

g = nz.groupby("block_id_B")
entry = df[(df["age_bars_B"] == 1) & (df["position_B"] != 0)].set_index("block_id_B")
last_idx = g["t_idx"].idxmax()
last = df.loc[last_idx].set_index("block_id_B")

# bars_to_mfe: argmax (first occurrence) of the block's own real run_pnl_B_dollars path,
# 0-offset from block entry (age_bars_B==1 -> offset 0), matching SHADOW01's own convention.
bars_to_mfe = {}
for bid, grp in g:
    grp_sorted = grp.sort_values("t_idx")
    pnl_path = grp_sorted["run_pnl_B_dollars"].to_numpy()
    bars_to_mfe[bid] = int(np.argmax(pnl_path))

block = pd.DataFrame(index=block_ids)
block["side"] = entry["position_B"]
block["entry_year"] = entry["year"]
block["entry_is_health_only"] = entry["is_health_only_bar"]
block["entry_is_rth"] = entry["is_rth"]
block["entry_M"] = entry["M"]
block["entry_abs_M"] = entry["M"].abs()
block["entry_sigma460"] = entry["sigma460_atr_proxy_pts"]
block["net_pnl"] = last["run_pnl_B_dollars"]
block["mfe_final"] = last["MFE_B_dollars"]
block["mae_final"] = last["MAE_B_dollars"]
block["mae_abs"] = -last["MAE_B_dollars"]  # non-negative magnitude, "lower mae_abs" = smaller drawdown
for f in FEATURES + LEVEL_FEATURES:
    block[f"entry_{f}"] = entry[f]
block = block.reset_index().rename(columns={"index": "block_id_B"})
block["bars_to_mfe"] = block["block_id_B"].map(bars_to_mfe)

# outcome (e): top-decile winner, threshold frozen on CANONICAL rows only, applied to all rows
canon_mask = ~block["entry_is_health_only"]
p90 = block.loc[canon_mask, "net_pnl"].quantile(0.90)
block["top_decile_winner"] = (block["net_pnl"] >= p90).astype(float)

print(f"  n={len(block)}  net sum ${block['net_pnl'].sum():,.2f}  "
      f"(canonical-only net sum ${block.loc[canon_mask,'net_pnl'].sum():,.2f})")
print(f"  canonical p90 net_pnl threshold = ${p90:,.2f}  "
      f"canonical top-decile rate = {block.loc[canon_mask,'top_decile_winner'].mean():.4f}")
print(f"  mfe_final: mean=${block['mfe_final'].mean():,.2f} median=${block['mfe_final'].median():,.2f}")
print(f"  mae_abs:   mean=${block['mae_abs'].mean():,.2f} median=${block['mae_abs'].median():,.2f}")
print(f"  bars_to_mfe: mean={block['bars_to_mfe'].mean():.2f} median={block['bars_to_mfe'].median():.1f}")

block.to_csv(os.path.join(OUT, "productB_block_table.csv"), index=False)
with open(os.path.join(OUT, "productB_block_table_meta.json"), "w") as fh:
    json.dump({"n_blocks": int(len(block)), "n_canonical": int(canon_mask.sum()),
                "canonical_p90_net_pnl_threshold": float(p90),
                "canonical_net_pnl_sum": float(block.loc[canon_mask, "net_pnl"].sum())}, fh, indent=2)
print("\nProduct-B block table build complete.")
