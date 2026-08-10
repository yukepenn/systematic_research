"""EVIDENCE01 STEP 2/3 -- independently recompute the headline number(s) of each of the 4 audited
runs directly from their own out/*.csv, out/*.json, out/*.parquet, NOT from REPORT.md prose.

Audited runs:
  1. U6B_PRODUCT_A_SCALE_RATE (mandatory)   -- control canonical net; 2022-2025-only deltas F0.5/F0.7
  2. AUCTION01_VALUE_STATE (mandatory)      -- D4 pooled Spearman rho, poc_share vs range_60, and n
  3. ICT0102_EVENT_SEQUENCE (seeded pick)   -- correctness-gate net; ICT02 full-6-feature-block dR2;
                                                ICT01 SWEEP+MSS dR2 vs SWEEP-ONLY
  4. U6_PRODUCT_A_PATH_DEPENDENCE (seeded)  -- Part 3 right-tail check (load-bearing per the
                                                report's own Verdict section): top-20/bottom-20
                                                net_pnl range and fraction starting in a
                                                1-3-contract state

Every number below is computed from raw artifacts using code written independently of each run's
own src/*.py (except where noted "re-derivation using the run's own OLS helper on its own
persisted feature CSV", which is still a fresh execution against a raw artifact, not a read of
REPORT.md prose).

Reproduce: python runs/EVIDENCE01_REPORT_TRACEABILITY/src/02_recompute_headline_numbers.py
"""
import json
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
results = {}

# =====================================================================================
# 1. U6B_PRODUCT_A_SCALE_RATE (mandatory)
# =====================================================================================
print("=" * 100)
print("U6B_PRODUCT_A_SCALE_RATE")
print("=" * 100)

u6b_summary = json.load(open(f"{ROOT}/runs/U6B_PRODUCT_A_SCALE_RATE/out/u6b_summary.json"))
ctrl_canon_json = u6b_summary["canonical_net"]["CONTROL"]
f05_canon_json = u6b_summary["canonical_net"]["F0.5"]
f07_canon_json = u6b_summary["canonical_net"]["F0.7"]
delta_f05_json = u6b_summary["delta_2022_2025_vs_control"]["F0.5"]
delta_f07_json = u6b_summary["delta_2022_2025_vs_control"]["F0.7"]

# Independent recompute from u6b_year_by_year.csv (a different artifact than u6b_summary.json,
# both produced by the same run's src/01_construct_and_validate.py but summed here with fresh code)
yby = pd.read_csv(f"{ROOT}/runs/U6B_PRODUCT_A_SCALE_RATE/out/u6b_year_by_year.csv")
ctrl_full = yby[yby["candidate"] == "CONTROL"]["net"].sum()
f05_full = yby[yby["candidate"] == "F0.5"]["net"].sum()
f07_full = yby[yby["candidate"] == "F0.7"]["net"].sum()

ctrl_2225 = yby[(yby["candidate"] == "CONTROL") & (yby["year"].between(2022, 2025))]["net"].sum()
f05_2225 = yby[(yby["candidate"] == "F0.5") & (yby["year"].between(2022, 2025))]["net"].sum()
f07_2225 = yby[(yby["candidate"] == "F0.7") & (yby["year"].between(2022, 2025))]["net"].sum()
delta_f05_recomp = f05_2225 - ctrl_2225
delta_f07_recomp = f07_2225 - ctrl_2225

print(f"CONTROL canonical net (u6b_summary.json)        : {ctrl_canon_json:.2f}")
print(f"CONTROL canonical net (sum of u6b_year_by_year)  : {ctrl_full:.2f}")
print(f"F0.5 canonical net (u6b_summary.json)            : {f05_canon_json:.2f}")
print(f"F0.5 canonical net (sum of u6b_year_by_year)      : {f05_full:.2f}")
print(f"F0.7 canonical net (u6b_summary.json)            : {f07_canon_json:.2f}")
print(f"F0.7 canonical net (sum of u6b_year_by_year)      : {f07_full:.2f}")
print(f"CONTROL 2022-2025 net (recomputed)                : {ctrl_2225:.2f}")
print(f"delta F0.5 2022-2025 (u6b_summary.json)           : {delta_f05_json:.2f}")
print(f"delta F0.5 2022-2025 (recomputed)                 : {delta_f05_recomp:.2f} ({delta_f05_recomp/ctrl_2225*100:.3f}%)")
print(f"delta F0.7 2022-2025 (u6b_summary.json)           : {delta_f07_json:.2f}")
print(f"delta F0.7 2022-2025 (recomputed)                 : {delta_f07_recomp:.2f} ({delta_f07_recomp/ctrl_2225*100:.3f}%)")

results["U6B_PRODUCT_A_SCALE_RATE"] = {
    "ctrl_canonical_net_report": 177924.40,
    "ctrl_canonical_net_recomputed": round(ctrl_full, 2),
    "f05_canonical_net_report": 178213.70,
    "f05_canonical_net_recomputed": round(f05_full, 2),
    "f07_canonical_net_report": 178531.30,
    "f07_canonical_net_recomputed": round(f07_full, 2),
    "delta_f05_2022_2025_report_pct": 0.503,
    "delta_f05_2022_2025_recomputed_pct": round(delta_f05_recomp / ctrl_2225 * 100, 3),
    "delta_f07_2022_2025_report_pct": 0.579,
    "delta_f07_2022_2025_recomputed_pct": round(delta_f07_recomp / ctrl_2225 * 100, 3),
}

# =====================================================================================
# 2. AUCTION01_VALUE_STATE (mandatory)
# =====================================================================================
print()
print("=" * 100)
print("AUCTION01_VALUE_STATE")
print("=" * 100)

diag = json.load(open(f"{ROOT}/runs/AUCTION01_VALUE_STATE/out/diagnostics_summary.json"))
d4_json = diag["D4"]["poc_share__range_60"]

# Independent recompute directly from decision_outcomes.parquet (raw artifact) using scipy,
# not the run's own bootstrap code
df = pd.read_parquet(f"{ROOT}/runs/AUCTION01_VALUE_STATE/out/decision_outcomes.parquet",
                      columns=["poc_share", "range_60", "sess_tag"])
sub = df.dropna(subset=["poc_share", "range_60"])
rho, p = spearmanr(sub["poc_share"], sub["range_60"])
n = len(sub)
n_sessions = sub["sess_tag"].nunique()

print(f"D4 poc_share vs range_60 -- diagnostics_summary.json : rho={d4_json['rho']:.6f}, n={d4_json['n']}, n_sessions={d4_json['n_sessions']}")
print(f"D4 poc_share vs range_60 -- recomputed (scipy)        : rho={rho:.6f}, n={n}, n_sessions={n_sessions}")

results["AUCTION01_VALUE_STATE"] = {
    "d4_rho_report": -0.353,
    "d4_rho_recomputed": round(rho, 6),
    "d4_n_report": 27293,
    "d4_n_recomputed": n,
}

# =====================================================================================
# 3. ICT0102_EVENT_SEQUENCE (seeded pick)
# =====================================================================================
print()
print("=" * 100)
print("ICT0102_EVENT_SEQUENCE")
print("=" * 100)


def ols_r2(df_, X_cols, y_col):
    d = df_.dropna(subset=X_cols + [y_col])
    X = d[X_cols].to_numpy(dtype=float)
    X = np.column_stack([np.ones(len(X)), X])
    y = d[y_col].to_numpy(dtype=float)
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    yhat = X @ coef
    ss_res = np.sum((y - yhat) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan
    return r2, len(d)


# 3a. correctness-gate net (independent full recompute from u0_state_table.parquet)
u0 = pd.read_parquet(f"{ROOT}/runs/U0_UNIFIED_STATE/out/u0_state_table.parquet",
                      columns=["is_health_only_bar", "bar_pnl_B_nq_dollars"])
canon_net_recomp = u0.loc[~u0["is_health_only_bar"], "bar_pnl_B_nq_dollars"].sum()
print(f"Correctness gate: canonical B-NQ net -- report claim: 301915.92")
print(f"Correctness gate: canonical B-NQ net -- recomputed  : {canon_net_recomp:.2f}")

# 3b. ICT02 full 6-feature block dR2, recomputed from ict02_features.csv (persisted feature CSV,
# a raw output artifact) using a fresh OLS implementation
ict02 = pd.read_csv(f"{ROOT}/runs/ICT0102_EVENT_SEQUENCE/out/ict02_features.csv")
baseline_cols = ["M_abs", "vol_z"]
feat_cols = ["dist_favorable_atr", "dist_unfavorable_atr", "swept_favorable",
             "swept_unfavorable", "accepted_favorable", "rejected_favorable"]
r2_base, n_base = ols_r2(ict02, baseline_cols, "fwd20_pnl")
r2_full, n_full = ols_r2(ict02, baseline_cols + feat_cols, "fwd20_pnl")
dr2_full_recomp = r2_full - r2_base
ict02_json = json.load(open(f"{ROOT}/runs/ICT0102_EVENT_SEQUENCE/out/ict02_summary.json"))
print(f"ICT02 full 6-feature block dR2 -- ict02_summary.json : {ict02_json['full_block_dr2']:.6f}")
print(f"ICT02 full 6-feature block dR2 -- recomputed (fresh OLS on ict02_features.csv) : {dr2_full_recomp:.6f}")

# 3c. ICT01 SWEEP+MSS dR2 vs SWEEP-ONLY, recomputed from ict01_events.csv
ict01 = pd.read_csv(f"{ROOT}/runs/ICT0102_EVENT_SEQUENCE/out/ict01_events.csv")
r2_base1, _ = ols_r2(ict01, baseline_cols, "fwd20_pnl")
r2_sweep, _ = ols_r2(ict01, baseline_cols + ["sweep_with_position"], "fwd20_pnl")
r2_mss, _ = ols_r2(ict01, baseline_cols + ["sweep_with_position", "confirmed_mss"], "fwd20_pnl")
dr2_mss_recomp = r2_mss - r2_sweep
ict01_json = json.load(open(f"{ROOT}/runs/ICT0102_EVENT_SEQUENCE/out/ict01_summary.json"))
print(f"ICT01 SWEEP+MSS dR2 vs SWEEP-ONLY -- ict01_summary.json : {ict01_json['sweep_mss_dr2_vs_sweep_only']:.6f}")
print(f"ICT01 SWEEP+MSS dR2 vs SWEEP-ONLY -- recomputed          : {dr2_mss_recomp:.6f}")

results["ICT0102_EVENT_SEQUENCE"] = {
    "correctness_gate_net_report": 301915.92,
    "correctness_gate_net_recomputed": round(canon_net_recomp, 2),
    "ict02_full_block_dr2_report": 0.00045,
    "ict02_full_block_dr2_recomputed": round(dr2_full_recomp, 6),
    "ict01_sweep_mss_dr2_report": 0.00003,
    "ict01_sweep_mss_dr2_recomputed": round(dr2_mss_recomp, 6),
}

# =====================================================================================
# 4. U6_PRODUCT_A_PATH_DEPENDENCE (seeded pick)
# =====================================================================================
print()
print("=" * 100)
print("U6_PRODUCT_A_PATH_DEPENDENCE")
print("=" * 100)

# Report's own Verdict section names Part 3 (right-tail check) "the load-bearing constraint":
# top-20/bottom-20 all-time blocks' net_pnl range and fraction starting in a 1-3-contract state.
# Recomputed here directly from u6_block_table.csv (the raw block table), NOT from the already-
# filtered step3_top20_blocks.csv/step3_bottom20_blocks.csv persisted outputs.
bt = pd.read_csv(f"{ROOT}/runs/U6_PRODUCT_A_PATH_DEPENDENCE/out/u6_block_table.csv")
canon = bt[~bt["start_is_health_only"]].copy()
canon["abs_start_exposure"] = canon["start_exposure"].abs()
top20 = canon.nlargest(20, "net_pnl")
bot20 = canon.nsmallest(20, "net_pnl")
top20_low_frac = (top20["abs_start_exposure"] <= 3).sum()
bot20_low_frac = (bot20["abs_start_exposure"] <= 3).sum()

print(f"n canonical nonzero blocks -- recomputed: {len(canon)} (report: 4,809)")
print(f"TOP-20 net_pnl range  -- recomputed: [{top20['net_pnl'].min():.2f}, {top20['net_pnl'].max():.2f}] "
      f"(report: [6563.90, 18352.15])")
print(f"BOTTOM-20 net_pnl range -- recomputed: [{bot20['net_pnl'].min():.2f}, {bot20['net_pnl'].max():.2f}] "
      f"(report: [-4934.45, -2509.65])")
print(f"TOP-20 started in 1-3-contract state -- recomputed: {top20_low_frac}/20 (report: 14/20, 70%)")
print(f"BOTTOM-20 started in 1-3-contract state -- recomputed: {bot20_low_frac}/20 (report: 15/20, 75%)")

results["U6_PRODUCT_A_PATH_DEPENDENCE"] = {
    "n_canonical_blocks_report": 4809,
    "n_canonical_blocks_recomputed": int(len(canon)),
    "top20_started_low_report": "14/20 (70%)",
    "top20_started_low_recomputed": f"{top20_low_frac}/20 ({top20_low_frac/20*100:.0f}%)",
    "bottom20_started_low_report": "15/20 (75%)",
    "bottom20_started_low_recomputed": f"{bot20_low_frac}/20 ({bot20_low_frac/20*100:.0f}%)",
    "top20_net_pnl_range_report": [6563.90, 18352.15],
    "top20_net_pnl_range_recomputed": [round(float(top20["net_pnl"].min()), 2), round(float(top20["net_pnl"].max()), 2)],
    "bottom20_net_pnl_range_report": [-4934.45, -2509.65],
    "bottom20_net_pnl_range_recomputed": [round(float(bot20["net_pnl"].min()), 2), round(float(bot20["net_pnl"].max()), 2)],
}

# =====================================================================================
out_path = f"{ROOT}/runs/EVIDENCE01_REPORT_TRACEABILITY/out/step2_3_recompute_results.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)
print(f"\nWrote {out_path}")
