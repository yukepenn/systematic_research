"""SHADOW01 step 2 -- tests whether recent shadow-event state carries information about the
NEXT shadow event's expected value (addendum B3-B6). Null: setup outcomes have no useful
memory. A real result must survive residualization against M-strength/vol/session/organization
(addendum B5) and block-clustered significance (addendum B2), not just a naive pooled Spearman.
"""
import os, sys, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "runs", "W18R1_M1_VOLSEASON", "src"))
sys.path.insert(0, os.path.join(ROOT, "runs", "SA0_SYSTEM_STRUCTURE", "src"))
import substrate as S
import sm01_solarsim as sm

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
ev = pd.read_csv(os.path.join(OUT, "shadow_events.csv")).sort_values("event_start_t_idx").reset_index(drop=True)
print(f"[SHADOW01] {len(ev)} shadow events loaded", flush=True)

sig460 = sm.sigma_series(S.close)
ev["vol_at_start"] = sig460[ev["event_start_t_idx"].to_numpy()]

# join organization/session columns from U0 (already verified state table, canonical+extension;
# restrict the join to canonical rows only -- this diagnostic uses the canonical window exclusively)
u0 = pd.read_parquet(os.path.join(ROOT, "runs", "U0_UNIFIED_STATE", "out", "u0_state_table.parquet"),
                      columns=["t_idx", "trend_efficiency_20", "range_efficiency_20", "session_phase"])
ev = ev.merge(u0, left_on="event_start_t_idx", right_on="t_idx", how="left")

LB = 10  # rolling lookback, tiny preregistered set per addendum B3
n_ev = len(ev)
side = ev["side"].to_numpy()
net_pnl = ev["net_pnl"].to_numpy()
mfe = ev["mfe"].to_numpy()
mae = ev["mae"].to_numpy()
bars_to_mfe = ev["bars_to_mfe"].to_numpy()

last_outcome_sign = np.full(n_ev, np.nan)
recent_wl_last3 = np.full(n_ev, np.nan)
rolling_expectancy_10 = np.full(n_ev, np.nan)
rolling_median_10 = np.full(n_ev, np.nan)
rolling_mfe_10 = np.full(n_ev, np.nan)
rolling_mae_10 = np.full(n_ev, np.nan)
loss_severity_10 = np.full(n_ev, np.nan)
follow_through_speed_10 = np.full(n_ev, np.nan)
loss_rate_10 = np.full(n_ev, np.nan)
right_tail_rate_10 = np.full(n_ev, np.nan)

LARGE_WINNER_THRESH = 1000.0  # fixed a priori, not fit to outcome (typical block scale is well
                               # documented in this campaign: hundreds to low-thousands, tail to $19k)

for i in range(LB, n_ev):
    hist = slice(i - LB, i)
    last_outcome_sign[i] = np.sign(net_pnl[i - 1])
    recent_wl_last3[i] = np.sum(net_pnl[i - 3:i] > 0)
    rolling_expectancy_10[i] = np.mean(net_pnl[hist])
    rolling_median_10[i] = np.median(net_pnl[hist])
    rolling_mfe_10[i] = np.mean(mfe[hist])
    rolling_mae_10[i] = np.mean(mae[hist])
    losers = net_pnl[hist][net_pnl[hist] < 0]
    loss_severity_10[i] = np.mean(losers) if len(losers) else 0.0
    follow_through_speed_10[i] = np.mean(bars_to_mfe[hist])
    loss_rate_10[i] = np.mean(net_pnl[hist] < 0)
    right_tail_rate_10[i] = np.mean(net_pnl[hist] > LARGE_WINNER_THRESH)

feat_cols = ["last_outcome_sign", "recent_wl_last3", "rolling_expectancy_10", "rolling_median_10",
             "rolling_mfe_10", "rolling_mae_10", "loss_severity_10", "follow_through_speed_10",
             "loss_rate_10", "right_tail_rate_10"]
for c, arr in zip(feat_cols, [last_outcome_sign, recent_wl_last3, rolling_expectancy_10,
                               rolling_median_10, rolling_mfe_10, rolling_mae_10,
                               loss_severity_10, follow_through_speed_10, loss_rate_10,
                               right_tail_rate_10]):
    ev[c] = arr

ev["V_next"] = ev["net_pnl"]  # the outcome IS this event's own net_pnl; features are from PRIOR events only
sub = ev.iloc[LB:].dropna(subset=feat_cols + ["V_next", "vol_at_start"]).copy()
print(f"[SHADOW01] {len(sub)} events usable after {LB}-event warmup", flush=True)

# ---------------------------------------------------------------- raw + residualized tests
sub["M_abs"] = sub["M_start"].abs()
sub["M_tercile"] = pd.qcut(sub["M_abs"], 3, labels=["weak", "mid", "strong"], duplicates="drop")
sub["vol_tercile"] = pd.qcut(sub["vol_at_start"], 3, labels=["low", "mid", "high"], duplicates="drop")
sub["bucket"] = sub["M_tercile"].astype(str) + "_" + sub["vol_tercile"].astype(str)
sub["bucket_mean"] = sub.groupby("bucket")["V_next"].transform("mean")
sub["resid_V_next"] = sub["V_next"] - sub["bucket_mean"]


def ols_r2(df, X_cols, y_col):
    d = df.dropna(subset=X_cols + [y_col])
    X = d[X_cols].to_numpy(dtype=float)
    X = np.column_stack([np.ones(len(X)), X])
    y = d[y_col].to_numpy(dtype=float)
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    yhat = X @ coef
    ss_res = np.sum((y - yhat) ** 2); ss_tot = np.sum((y - y.mean()) ** 2)
    return (1 - ss_res / ss_tot if ss_tot > 0 else np.nan), len(d)


sub["vol_z"] = sub["vol_tercile"].cat.codes
r2_base, n_base = ols_r2(sub, ["M_abs", "vol_z"], "V_next")
print(f"\nbaseline R^2 (M_abs + vol_tercile_code): {r2_base:.5f} (n={n_base})")

results = {}
print("\n" + "=" * 100)
print(f"{'feature':<26}{'raw_rho':>10}{'resid_rho':>12}{'delta_R2':>12}{'n':>8}")
print("=" * 100)
for c in feat_cols:
    d = sub.dropna(subset=[c, "V_next", "resid_V_next"])
    rho_raw = float(d[c].corr(d["V_next"], method="spearman"))
    rho_resid = float(d[c].corr(d["resid_V_next"], method="spearman"))
    r2_ext, n_ext = ols_r2(sub, ["M_abs", "vol_z", c], "V_next")
    results[c] = {"rho_raw": rho_raw, "rho_resid": rho_resid, "delta_r2": r2_ext - r2_base, "n": n_ext}
    print(f"{c:<26}{rho_raw:>10.4f}{rho_resid:>12.4f}{r2_ext - r2_base:>12.5f}{n_ext:>8}")

# ---------------------------------------------------------------- redundancy check (addendum B5)
print("\n" + "=" * 100 + "\nREDUNDANCY CHECK: does the strongest feature just proxy organization/session?\n" + "=" * 100)
best_feat = max(results, key=lambda k: abs(results[k]["rho_resid"]))
print(f"strongest feature by |residualized rho|: {best_feat} ({results[best_feat]['rho_resid']:.4f})")
for org_col in ["trend_efficiency_20", "range_efficiency_20"]:
    d = sub.dropna(subset=[best_feat, org_col])
    rho = float(d[best_feat].corr(d[org_col], method="spearman"))
    print(f"  Spearman({best_feat}, {org_col}) = {rho:.4f}  (n={len(d)})  "
          f"{'REDUNDANT (|rho|>0.5)' if abs(rho) > 0.5 else 'not redundant'}")
r2_org_base, n_org = ols_r2(sub, ["M_abs", "vol_z", "trend_efficiency_20", "range_efficiency_20"], "V_next")
r2_org_ext, _ = ols_r2(sub, ["M_abs", "vol_z", "trend_efficiency_20", "range_efficiency_20", best_feat], "V_next")
print(f"\nR^2 with M+vol+organization: {r2_org_base:.5f} (n={n_org})")
print(f"R^2 with M+vol+organization+{best_feat}: {r2_org_ext:.5f}  "
      f"(incremental delta_R2 beyond organization = {r2_org_ext - r2_org_base:+.5f})")

# session interaction for the strongest feature
print("\n" + "=" * 100 + "\nSESSION SPLIT of the strongest feature's residualized relationship\n" + "=" * 100)
for is_rth_label, mask in [("RTH", sub["session_phase"].isin(["RTH_OPEN", "RTH_MID", "RTH_CLOSE"])),
                            ("ETH", ~sub["session_phase"].isin(["RTH_OPEN", "RTH_MID", "RTH_CLOSE"]))]:
    d = sub[mask].dropna(subset=[best_feat, "resid_V_next"])
    rho = float(d[best_feat].corr(d["resid_V_next"], method="spearman")) if len(d) > 10 else np.nan
    print(f"  {is_rth_label}: n={len(d)}  Spearman(resid)={rho:.4f}" if len(d) > 10 else f"  {is_rth_label}: n={len(d)} (too small)")

# ---------------------------------------------------------------- chronology (year-by-year)
print("\n" + "=" * 100 + f"\nYEAR-BY-YEAR STABILITY of {best_feat} (residualized)\n" + "=" * 100)
yby = []
for yr, g in sub.dropna(subset=[best_feat, "resid_V_next"]).groupby("year_start"):
    rho_yr = float(g[best_feat].corr(g["resid_V_next"], method="spearman")) if len(g) > 10 else np.nan
    yby.append({"year": int(yr), "n": len(g), "rho": rho_yr})
yby_df = pd.DataFrame(yby)
print(yby_df.round(4).to_string(index=False))

# ---------------------------------------------------------------- session-block bootstrap significance
print("\n" + "=" * 100 + f"\nSESSION-BLOCK BOOTSTRAP significance for {best_feat} (1000 resamples, block=session_date_start)\n" + "=" * 100)
rng = np.random.RandomState(20260809)
sub_valid = sub.dropna(subset=[best_feat, "resid_V_next"]).reset_index(drop=True)
sessions = sub_valid["sess_date_start"].unique()
obs_rho = float(sub_valid[best_feat].corr(sub_valid["resid_V_next"], method="spearman"))
boot_rhos = []
sess_groups = {s: sub_valid[sub_valid["sess_date_start"] == s].index.to_numpy() for s in sessions}
for _ in range(1000):
    sampled_sessions = rng.choice(sessions, size=len(sessions), replace=True)
    idx = np.concatenate([sess_groups[s] for s in sampled_sessions if len(sess_groups[s]) > 0])
    if len(idx) < 20:
        continue
    d = sub_valid.iloc[idx]
    r = d[best_feat].corr(d["resid_V_next"], method="spearman")
    if r == r:
        boot_rhos.append(r)
boot_rhos = np.array(boot_rhos)
ci_lo, ci_hi = np.percentile(boot_rhos, [2.5, 97.5])
print(f"observed rho={obs_rho:.4f}, session-block-bootstrap 95% CI=[{ci_lo:.4f}, {ci_hi:.4f}], "
      f"excludes 0: {ci_lo > 0 or ci_hi < 0}")

# ---------------------------------------------------------------- right-tail check
print("\n" + "=" * 100 + "\nRIGHT-TAIL CHECK: strongest feature's value distribution across top-20 shadow events\n" + "=" * 100)
top20 = sub.nlargest(20, "net_pnl")
bottom20 = sub.nsmallest(20, "net_pnl")
print(f"top-20 {best_feat} mean={top20[best_feat].mean():.3f} median={top20[best_feat].median():.3f}")
print(f"bottom-20 {best_feat} mean={bottom20[best_feat].mean():.3f} median={bottom20[best_feat].median():.3f}")
print(f"population {best_feat} mean={sub[best_feat].mean():.3f} median={sub[best_feat].median():.3f}")

summary = {
    "n_events_usable": len(sub), "lookback": LB, "large_winner_threshold": LARGE_WINNER_THRESH,
    "baseline_r2": r2_base, "feature_results": results, "best_feature": best_feat,
    "redundancy_vs_organization": {"r2_org_only": r2_org_base, "r2_org_plus_best": r2_org_ext,
                                    "incremental_delta_r2": r2_org_ext - r2_org_base},
    "year_by_year": yby_df.to_dict("records"),
    "bootstrap": {"observed_rho": obs_rho, "ci_lo": float(ci_lo), "ci_hi": float(ci_hi),
                  "n_boot": len(boot_rhos)},
    "top20_vs_bottom20": {
        "top20_mean": float(top20[best_feat].mean()), "bottom20_mean": float(bottom20[best_feat].mean()),
        "population_mean": float(sub[best_feat].mean()),
    },
}
json.dump(summary, open(os.path.join(OUT, "serial_dependence_summary.json"), "w"), indent=2, default=str)
sub.to_csv(os.path.join(OUT, "shadow_events_with_features.csv"), index=False)
print("\nSHADOW01 serial-dependence diagnostic complete.")
