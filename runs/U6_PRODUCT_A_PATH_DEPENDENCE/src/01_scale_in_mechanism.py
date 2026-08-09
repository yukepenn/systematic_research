"""U6 step1 -- WHY are scale-in contracts more valuable than fresh entries? Per spec.yaml plan
step1_scale_in_mechanism. Primary analysis on the canonical window (is_health_only_bar==False);
extended June-July-2026 window reported separately, never blended (U0's own mechanical split)."""
import os
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu

import u6_substrate as U

OUT = U.OUT
ev = pd.read_csv(os.path.join(OUT, "u6_entry_scale_events.csv"))
FEATS = U.CAUSAL_FEATURES_STEP1

ev_can = ev[~ev["is_health_only_bar"]].copy()
ev_ext = ev[ev["is_health_only_bar"]].copy()
print(f"canonical events: {len(ev_can)} ({(ev_can.action_A=='ENTRY').sum()} ENTRY / "
      f"{(ev_can.action_A=='SCALE_IN').sum()} SCALE_IN)")
print(f"extended (2026-06/07) events: {len(ev_ext)} ({(ev_ext.action_A=='ENTRY').sum()} ENTRY / "
      f"{(ev_ext.action_A=='SCALE_IN').sum()} SCALE_IN)  -- observational only, not blended below")

print("\n" + "=" * 95, "\nSTEP1a -- FEATURE DISTRIBUTION: ENTRY vs SCALE_IN bars (canonical window)\n", "=" * 95, sep="")
rows_a = []
for f in FEATS:
    if f == "m_abs_vs_entry":
        # trivially 0 at ENTRY by definition -- only meaningful within SCALE_IN, skip the 2-group compare
        continue
    e = ev_can.loc[ev_can.action_A == "ENTRY", f].dropna()
    s = ev_can.loc[ev_can.action_A == "SCALE_IN", f].dropna()
    u_stat, p = mannwhitneyu(s, e, alternative="two-sided")
    # rank-biserial effect size: 2*U/(n1*n2) - 1 (from SCALE_IN's perspective)
    reff = 2 * u_stat / (len(s) * len(e)) - 1
    rows_a.append({"feature": f, "entry_mean": e.mean(), "entry_median": e.median(),
                    "scalein_mean": s.mean(), "scalein_median": s.median(),
                    "mannwhitney_p": p, "rank_biserial_effect": reff,
                    "n_entry": len(e), "n_scalein": len(s)})
step1a = pd.DataFrame(rows_a)
print(step1a.round(5).to_string(index=False))
step1a.to_csv(os.path.join(OUT, "step1a_entry_vs_scalein_distributions.csv"), index=False)

print("\n" + "=" * 95, "\nSTEP1a(ii) -- m_abs_vs_entry within SCALE_IN only (descriptive)\n", "=" * 95, sep="")
mve = ev_can.loc[ev_can.action_A == "SCALE_IN", "m_abs_vs_entry"].dropna()
print(f"n={len(mve)}, mean={mve.mean():.4f}, median={mve.median():.4f}, "
      f"fraction > 0 (bigger |M| than at entry) = {(mve > 0).mean():.4f}")

print("\n" + "=" * 95, "\nSTEP1b -- MEDIATION-STYLE OLS: fwd20_pnl_per_contract ~ 1 + is_scale_in [+ feature]\n", "=" * 95, sep="")


def ols(X_cols, sub):
    d = sub.dropna(subset=X_cols + ["fwd20_pnl_per_contract"])
    X = d[X_cols].to_numpy(dtype=float)
    X = np.column_stack([np.ones(len(X)), X])
    y = d["fwd20_pnl_per_contract"].to_numpy(dtype=float)
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    yhat = X @ coef
    ss_res = np.sum((y - yhat) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan
    return coef, r2, len(d)


coef0, r2_0, n0 = ols(["is_scale_in"], ev_can)
b0_is_scale_in = coef0[1]
print(f"baseline: is_scale_in coef = {b0_is_scale_in:+.4f}  (R^2={r2_0:.5f}, n={n0})  "
      f"[PA0 cross-check: should be close to 14.43-2.03=+12.40]")

rows_b = []
for f in FEATS:
    if f == "m_abs_vs_entry":
        continue  # not defined for ENTRY rows (trivially 0) -- tested separately within-SCALE_IN in step1c
    coef, r2, n = ols(["is_scale_in", f], ev_can)
    b_mediated = coef[1]
    pct_explained = 100 * (1 - b_mediated / b0_is_scale_in) if b0_is_scale_in != 0 else np.nan
    rows_b.append({"feature": f, "is_scale_in_coef_mediated": b_mediated,
                    "pct_of_scale_in_premium_explained": pct_explained,
                    "feature_coef": coef[2], "R2": r2, "delta_R2_vs_baseline": r2 - r2_0, "n": n})
step1b = pd.DataFrame(rows_b).sort_values("delta_R2_vs_baseline", ascending=False)
print(step1b.round(5).to_string(index=False))
step1b.to_csv(os.path.join(OUT, "step1b_mediation_ols.csv"), index=False)

print("\n" + "=" * 95, "\nSTEP1c -- WITHIN-SCALE_IN residualized Spearman (bucket = |M_A_raw| tercile x sigma460 tercile)\n", "=" * 95, sep="")
si = ev_can[ev_can.action_A == "SCALE_IN"].copy()
si["m_tercile"] = pd.qcut(si["m_abs"], 3, labels=["weak", "mid", "strong"], duplicates="drop")
si["vol_tercile"] = pd.qcut(si["sigma460"], 3, labels=["low", "mid", "high"], duplicates="drop")
si["bucket"] = si["m_tercile"].astype(str) + "_" + si["vol_tercile"].astype(str)
si["bucket_mean"] = si.groupby("bucket")["fwd20_pnl_per_contract"].transform("mean")
si["resid"] = si["fwd20_pnl_per_contract"] - si["bucket_mean"]

rows_c = []
for f in FEATS:
    sub = si.dropna(subset=[f, "resid", "fwd20_pnl_per_contract"])
    raw_rho = float(sub[f].corr(sub["fwd20_pnl_per_contract"], method="spearman"))
    resid_rho = float(sub[f].corr(sub["resid"], method="spearman"))
    rows_c.append({"feature": f, "raw_spearman": raw_rho, "residualized_spearman": resid_rho, "n": len(sub)})
step1c = pd.DataFrame(rows_c).reindex(pd.DataFrame(rows_c)["residualized_spearman"].abs().sort_values(ascending=False).index)
print(step1c.round(5).to_string(index=False))
step1c.to_csv(os.path.join(OUT, "step1c_within_scalein_residualized_spearman.csv"), index=False)

best_feat = step1c.iloc[0]["feature"]
best_rho = step1c.iloc[0]["residualized_spearman"]
print(f"\nstrongest within-SCALE_IN residualized feature: {best_feat} (rho={best_rho:.4f})")

print("\n" + "=" * 95, f"\nYEAR-BY-YEAR STABILITY of {best_feat} (within-SCALE_IN residualized Spearman), canonical years\n", "=" * 95, sep="")
yby = []
for yr, g in si.dropna(subset=[best_feat, "resid"]).groupby("start_year"):
    if yr == 2026:
        continue  # canonical-2026 (Jan-May) reported on its own row below, not mixed with full years
    rho_yr = float(g[best_feat].corr(g["resid"], method="spearman"))
    yby.append({"year": int(yr), "n": len(g), "spearman_resid": rho_yr})
g2026 = si[(si.start_year == 2026)].dropna(subset=[best_feat, "resid"])
if len(g2026) > 5:
    yby.append({"year": "2026 (canonical Jan-May)", "n": len(g2026),
                "spearman_resid": float(g2026[best_feat].corr(g2026["resid"], method="spearman"))})
yby_df = pd.DataFrame(yby)
print(yby_df.round(4).to_string(index=False))
yby_df.to_csv(os.path.join(OUT, "step1_year_by_year_best_feature.csv"), index=False)

print("\n" + "=" * 95, "\nEXTENDED WINDOW (2026-06/07 health-only, OBSERVATIONAL ONLY -- not blended above)\n", "=" * 95, sep="")
si_ext = ev_ext[ev_ext.action_A == "SCALE_IN"].copy()
if len(si_ext) > 5:
    si_ext["m_tercile"] = pd.qcut(si_ext["m_abs"], 3, labels=["weak", "mid", "strong"], duplicates="drop")
    si_ext["vol_tercile"] = pd.qcut(si_ext["sigma460"], 3, labels=["low", "mid", "high"], duplicates="drop")
    si_ext["bucket"] = si_ext["m_tercile"].astype(str) + "_" + si_ext["vol_tercile"].astype(str)
    si_ext["bucket_mean"] = si_ext.groupby("bucket")["fwd20_pnl_per_contract"].transform("mean")
    si_ext["resid"] = si_ext["fwd20_pnl_per_contract"] - si_ext["bucket_mean"]
    sub = si_ext.dropna(subset=[best_feat, "resid"])
    rho_ext = float(sub[best_feat].corr(sub["resid"], method="spearman")) if len(sub) > 5 else np.nan
    print(f"n SCALE_IN events (extended)={len(si_ext)}, {best_feat} residualized Spearman = {rho_ext:.4f}")
else:
    rho_ext = np.nan
    print(f"n SCALE_IN events (extended) = {len(si_ext)} -- too few for a meaningful correlation")

summary = {
    "canonical_n_entry": int((ev_can.action_A == "ENTRY").sum()),
    "canonical_n_scalein": int((ev_can.action_A == "SCALE_IN").sum()),
    "canonical_entry_mean_fwd20_per_contract": float(ev_can.loc[ev_can.action_A == "ENTRY", "fwd20_pnl_per_contract"].mean()),
    "canonical_scalein_mean_fwd20_per_contract": float(ev_can.loc[ev_can.action_A == "SCALE_IN", "fwd20_pnl_per_contract"].mean()),
    "baseline_is_scale_in_coef": float(b0_is_scale_in),
    "baseline_R2": float(r2_0),
    "mediation_table": step1b.to_dict(orient="records"),
    "best_within_scalein_feature": best_feat,
    "best_within_scalein_residualized_spearman": float(best_rho),
    "extended_window_same_feature_spearman": None if np.isnan(rho_ext) else float(rho_ext),
    "extended_window_n_scalein": int(len(si_ext)),
}
import json
json.dump(summary, open(os.path.join(OUT, "step1_summary.json"), "w"), indent=2)
print("\nstep1 (scale-in mechanism) complete.")
