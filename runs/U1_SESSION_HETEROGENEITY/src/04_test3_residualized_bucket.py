"""U1 test 3 -- residualized RTH vs ETH comparison within (M-strength tercile x vol tercile)
buckets, same bucketing R4/R5 used. Product-B ENTRY table, canonical window only."""
import os, json
import numpy as np, pandas as pd

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
MIN_RELIABLE_N = 15  # per-cell threshold below which we flag, not report as reliable

entry_B = pd.read_csv(os.path.join(OUT, "block_entry_B.csv"))
entry_B = entry_B[(~entry_B["is_health_only_bar"]) & (entry_B["action_B"] == "ENTRY")].copy()

entry_B["bucket"] = entry_B["M_strength_tercile"].astype(str) + "_" + entry_B["vol_tercile"].astype(str)
entry_B["bucket_mean_pnl"] = entry_B.groupby("bucket")["net_pnl"].transform("mean")
entry_B["resid_pnl"] = entry_B["net_pnl"] - entry_B["bucket_mean_pnl"]
entry_B["rth_label"] = np.where(entry_B["is_rth"], "RTH", "ETH")

print("=" * 100)
print("TEST 3 -- residual net_pnl (net_pnl - bucket mean) by RTH vs ETH, within each M-strength x vol bucket")
print("=" * 100)
rows = []
for bucket, g in entry_B.groupby("bucket", observed=True):
    row = {"bucket": bucket, "bucket_n": len(g), "bucket_mean_pnl": float(g["net_pnl"].mean())}
    for label in ["RTH", "ETH"]:
        sub = g[g["rth_label"] == label]
        n = len(sub)
        mean_resid = float(sub["resid_pnl"].mean()) if n else np.nan
        row[f"{label}_n"] = n
        row[f"{label}_mean_resid"] = mean_resid
        row[f"{label}_reliable"] = bool(n >= MIN_RELIABLE_N)
    if row["RTH_n"] and row["ETH_n"]:
        row["RTH_minus_ETH_resid"] = row["RTH_mean_resid"] - row["ETH_mean_resid"]
    else:
        row["RTH_minus_ETH_resid"] = np.nan
    rows.append(row)
tbl = pd.DataFrame(rows).sort_values("bucket")
pd.set_option("display.width", 160)
print(tbl.round(2).to_string(index=False))
tbl.to_csv(os.path.join(OUT, "t3_residual_bucket_rth_vs_eth.csv"), index=False)

n_sparse = int((~tbl["RTH_reliable"] | ~tbl["ETH_reliable"]).sum())
print(f"\n{n_sparse}/{len(tbl)} buckets have at least one side (RTH or ETH) with n<{MIN_RELIABLE_N} "
      f"-- flagged 'reliable'=False in the table, NOT to be read as informative even if the gap looks large.")

reliable = tbl[tbl["RTH_reliable"] & tbl["ETH_reliable"]]
print(f"\nAmong the {len(reliable)} buckets with n>={MIN_RELIABLE_N} on both sides:")
print(reliable[["bucket", "RTH_n", "ETH_n", "RTH_mean_resid", "ETH_mean_resid", "RTH_minus_ETH_resid"]]
      .round(2).to_string(index=False))

pooled_rth_resid = float(entry_B.loc[entry_B["rth_label"] == "RTH", "resid_pnl"].mean())
pooled_eth_resid = float(entry_B.loc[entry_B["rth_label"] == "ETH", "resid_pnl"].mean())
summary = {
    "min_reliable_n": MIN_RELIABLE_N,
    "n_buckets_total": int(len(tbl)), "n_buckets_reliable_both_sides": int(len(reliable)),
    "pooled_resid_RTH_mean": pooled_rth_resid, "pooled_resid_ETH_mean": pooled_eth_resid,
    "pooled_RTH_minus_ETH": pooled_rth_resid - pooled_eth_resid,
    "reliable_buckets_RTH_minus_ETH_mean_of_means": float(reliable["RTH_minus_ETH_resid"].mean()) if len(reliable) else None,
    "reliable_buckets_all_same_sign": bool((np.sign(reliable["RTH_minus_ETH_resid"]) == np.sign(reliable["RTH_minus_ETH_resid"].iloc[0])).all()) if len(reliable) else None,
}
json.dump(summary, open(os.path.join(OUT, "t3_summary.json"), "w"), indent=2)
print("\n" + json.dumps(summary, indent=2))
print("\ntest3 complete.")
