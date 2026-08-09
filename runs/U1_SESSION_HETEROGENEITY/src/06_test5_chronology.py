"""U1 test 5 -- year-by-year stability (2022-2025, 2026-canonical-Jan-May) of the heterogeneity
found in tests 1-3 (ENTRY net_pnl RTH vs ETH gap; HOLD forward-5 continuation-value RTH vs ETH
gap), reported separately from the June-July-2026 health-only extension per U0's mechanical split."""
import os, json
import numpy as np, pandas as pd

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")

entry_B = pd.read_csv(os.path.join(OUT, "block_entry_B.csv"))
hold_B = pd.read_csv(os.path.join(OUT, "hold_fwd_B.csv"))

print("=" * 100)
print("TEST 5a -- ENTRY net_pnl, RTH vs ETH, year-by-year (canonical 2022-2025 + 2026 Jan-May)")
print("=" * 100)
entries_only = entry_B[entry_B["action_B"] == "ENTRY"].copy()
canon = entries_only[~entries_only["is_health_only_bar"]]
rows = []
for yr, g in canon.groupby("year"):
    rth = g.loc[g["is_rth"], "net_pnl"]
    eth = g.loc[~g["is_rth"], "net_pnl"]
    rows.append({"year": int(yr), "n_rth": len(rth), "mean_rth": float(rth.mean()) if len(rth) else np.nan,
                 "n_eth": len(eth), "mean_eth": float(eth.mean()) if len(eth) else np.nan,
                 "eth_minus_rth": (float(eth.mean()) - float(rth.mean())) if len(rth) and len(eth) else np.nan})
yby_entry = pd.DataFrame(rows).sort_values("year")
print(yby_entry.round(2).to_string(index=False))
yby_entry.to_csv(os.path.join(OUT, "t5a_entry_yby_rth_eth.csv"), index=False)
n_years_eth_higher = int((yby_entry["eth_minus_rth"] > 0).sum())
print(f"\nETH entry mean > RTH entry mean in {n_years_eth_higher}/{len(yby_entry)} canonical years")

print("\n" + "=" * 100)
print("TEST 5b -- HOLD forward-5-bar continuation value, RTH vs ETH, year-by-year")
print("=" * 100)
canon_h = hold_B[~hold_B["is_health_only_bar"]]
rows2 = []
for yr, g in canon_h.groupby("year"):
    rth = g.loc[g["is_rth"], "forward5_pnl"].dropna()
    eth = g.loc[~g["is_rth"], "forward5_pnl"].dropna()
    rows2.append({"year": int(yr), "n_rth": len(rth), "mean_rth": float(rth.mean()) if len(rth) else np.nan,
                  "n_eth": len(eth), "mean_eth": float(eth.mean()) if len(eth) else np.nan,
                  "rth_minus_eth": (float(rth.mean()) - float(eth.mean())) if len(rth) and len(eth) else np.nan})
yby_hold = pd.DataFrame(rows2).sort_values("year")
print(yby_hold.round(3).to_string(index=False))
yby_hold.to_csv(os.path.join(OUT, "t5b_hold_yby_rth_eth.csv"), index=False)
n_years_rth_higher = int((yby_hold["rth_minus_eth"] > 0).sum())
print(f"\nRTH forward-5 continuation value > ETH in {n_years_rth_higher}/{len(yby_hold)} canonical years")

print("\n" + "=" * 100)
print("TEST 5c -- June-July-2026 health-only EXTENSION, reported separately (never blended)")
print("=" * 100)
ext_entry = entries_only[entries_only["is_health_only_bar"]]
ext_hold = hold_B[hold_B["is_health_only_bar"]]
ext_summary = {}
if len(ext_entry):
    rth = ext_entry.loc[ext_entry["is_rth"], "net_pnl"]
    eth = ext_entry.loc[~ext_entry["is_rth"], "net_pnl"]
    print(f"ENTRY (health-only, n={len(ext_entry)}): RTH n={len(rth)} mean={rth.mean():.2f} | "
          f"ETH n={len(eth)} mean={eth.mean():.2f}" if len(rth) and len(eth) else
          f"ENTRY (health-only, n={len(ext_entry)}): insufficient split")
    ext_summary["entry_rth_n"] = int(len(rth)); ext_summary["entry_rth_mean"] = float(rth.mean()) if len(rth) else None
    ext_summary["entry_eth_n"] = int(len(eth)); ext_summary["entry_eth_mean"] = float(eth.mean()) if len(eth) else None
else:
    print("no ENTRY events in the health-only extension window")
if len(ext_hold):
    rth = ext_hold.loc[ext_hold["is_rth"], "forward5_pnl"].dropna()
    eth = ext_hold.loc[~ext_hold["is_rth"], "forward5_pnl"].dropna()
    print(f"HOLD fwd5 (health-only, n={len(ext_hold)}): RTH n={len(rth)} mean={rth.mean():.3f} | "
          f"ETH n={len(eth)} mean={eth.mean():.3f}")
    ext_summary["hold_rth_n"] = int(len(rth)); ext_summary["hold_rth_mean"] = float(rth.mean()) if len(rth) else None
    ext_summary["hold_eth_n"] = int(len(eth)); ext_summary["hold_eth_mean"] = float(eth.mean()) if len(eth) else None

summary = {
    "n_years_eth_entry_higher_than_rth": n_years_eth_higher,
    "n_years_total_entry": len(yby_entry),
    "n_years_rth_hold_higher_than_eth": n_years_rth_higher,
    "n_years_total_hold": len(yby_hold),
    "extension_june_july_2026": ext_summary,
}
json.dump(summary, open(os.path.join(OUT, "t5_summary.json"), "w"), indent=2)
print("\n" + json.dumps(summary, indent=2))
print("\ntest5 complete.")
