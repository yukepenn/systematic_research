"""U9B step 2 -- redundancy check, residual-information test, right-tail check, and
session-block-bootstrap significance for the 6 preregistered microstructure features against
Product-B entry outcomes and Product-A scale-in forward outcomes. Small, exploratory Track-C
sample (n=62 / n=232) -- deliberately simple statistics (no tercile-bucket residualization,
which would fracture n=62 into unstable cells), explicit small-sample caveats throughout.
"""
import os, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")

feat_B = pd.read_csv(os.path.join(OUT, "event_features_B.csv"))
feat_A = pd.read_csv(os.path.join(OUT, "event_features_A.csv"))
FEATS = ["avg_spread_ticks", "signed_flow_aligned", "trade_intensity", "quote_intensity",
         "microprice_dev_aligned", "ret1s_vol"]

# ---------------------------------------------------------------- outcomes
u0 = pd.read_parquet(os.path.join(ROOT, "runs", "U0_UNIFIED_STATE", "out", "u0_state_table.parquet"),
                      columns=["t_idx", "block_id_B", "block_id_A", "run_pnl_B_dollars",
                               "bar_pnl_A_dollars", "action_A"])

# Product-B: block outcome = last bar's run_pnl_B_dollars within the block
block_net_B = u0.groupby("block_id_B")["run_pnl_B_dollars"].last()
feat_B["block_net_pnl"] = feat_B["block_id"].map(block_net_B)

# Product-A: forward-only 20-bar cumulative bar_pnl_A_dollars starting the bar AFTER the scale-in
bpnl_A = u0.set_index("t_idx")["bar_pnl_A_dollars"]
fwd20 = []
for t in feat_A["t_idx"]:
    idx = range(t + 1, t + 21)
    vals = bpnl_A.reindex(idx)
    fwd20.append(float(vals.sum()) if vals.notna().any() else np.nan)
feat_A["fwd20_pnl"] = fwd20

feat_B = feat_B.dropna(subset=["block_net_pnl"])
feat_A = feat_A.dropna(subset=["fwd20_pnl"])
print(f"[U9B] usable: Product-B n={len(feat_B)}, Product-A n={len(feat_A)}", flush=True)

# ---------------------------------------------------------------- redundancy check (vs existing U0 features)
print("\n" + "=" * 90 + "\nSTEP 0 -- REDUNDANCY vs existing OHLCV-derived U0 features\n" + "=" * 90)
redund = {}
for df, tag in [(feat_B, "B"), (feat_A, "A")]:
    for f in FEATS:
        for existing in ["sigma460_atr_proxy_pts", "vol_surprise", "vwap_disp_atr"]:
            sub = df.dropna(subset=[f, existing])
            if len(sub) < 10:
                continue
            rho = float(sub[f].corr(sub[existing], method="spearman"))
            key = f"{tag}:{f}_vs_{existing}"
            redund[key] = rho
            flag = "REDUNDANT" if abs(rho) > 0.7 else ""
            if abs(rho) > 0.3:
                print(f"  {key}: rho={rho:.3f} {flag}")
max_redund = max(abs(v) for v in redund.values())
print(f"\nmax |rho| across all redundancy checks: {max_redund:.3f} "
      f"({'FLAGGED' if max_redund > 0.7 else 'no feature flagged redundant'})")

# ---------------------------------------------------------------- residual-info test (simple: raw + OLS controlling for M_abs, no tercile buckets given small n)
print("\n" + "=" * 90 + "\nRESIDUAL-INFORMATION TEST (raw Spearman + OLS controlling for |M|, small-n simple form)\n" + "=" * 90)


def ols_r2(df, X_cols, y_col):
    sub = df.dropna(subset=X_cols + [y_col])
    if len(sub) < 15:
        return np.nan, len(sub)
    X = sub[X_cols].to_numpy(dtype=float)
    X = np.column_stack([np.ones(len(X)), X])
    y = sub[y_col].to_numpy(dtype=float)
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    yhat = X @ coef
    ss_res = np.sum((y - yhat) ** 2); ss_tot = np.sum((y - y.mean()) ** 2)
    return (1 - ss_res / ss_tot if ss_tot > 0 else np.nan), len(sub)


results = {}
for df, tag, ycol in [(feat_B, "ProductB_entry", "block_net_pnl"), (feat_A, "ProductA_scalein", "fwd20_pnl")]:
    df["M_abs"] = df["M"].abs()
    r2_base, n_base = ols_r2(df, ["M_abs"], ycol)
    print(f"\n{tag} (n={len(df)}): baseline R^2 (M_abs only) = {r2_base:.4f} (n={n_base})")
    for f in FEATS:
        sub = df.dropna(subset=[f, ycol])
        rho = float(sub[f].corr(sub[ycol], method="spearman")) if len(sub) >= 10 else np.nan
        r2_ext, n_ext = ols_r2(df, ["M_abs", f], ycol)
        delta = r2_ext - r2_base if (r2_ext == r2_ext and r2_base == r2_base) else np.nan
        results[f"{tag}:{f}"] = {"raw_rho": rho, "delta_r2": delta, "n": n_ext}
        print(f"  {f}: raw_rho={rho:.4f}  delta_R2={delta:+.5f}  n={n_ext}")

# ---------------------------------------------------------------- strongest cell + right-tail (small-n caveat)
best_key = max(results, key=lambda k: abs(results[k]["raw_rho"]) if results[k]["raw_rho"] == results[k]["raw_rho"] else 0)
print(f"\nStrongest cell by |raw rho|: {best_key} -> {results[best_key]}")

print("\n" + "=" * 90 + f"\nRIGHT-TAIL CHECK (SMALL-N CAVEAT: quartile-based, not top/bottom-20, given n)\n" + "=" * 90)
tag_sel, feat_sel = best_key.split(":")
df_sel, ycol_sel = (feat_B, "block_net_pnl") if tag_sel == "ProductB_entry" else (feat_A, "fwd20_pnl")
sub = df_sel.dropna(subset=[feat_sel, ycol_sel])
q75 = sub[ycol_sel].quantile(0.75)
q25 = sub[ycol_sel].quantile(0.25)
top_q = sub[sub[ycol_sel] >= q75]
bot_q = sub[sub[ycol_sel] <= q25]
print(f"n={len(sub)}, top-quartile n={len(top_q)} (>= ${q75:.2f}), bottom-quartile n={len(bot_q)} (<= ${q25:.2f})")
print(f"{feat_sel}: top-quartile mean={top_q[feat_sel].mean():.4f}, "
      f"bottom-quartile mean={bot_q[feat_sel].mean():.4f}, "
      f"population mean={sub[feat_sel].mean():.4f}")

# ---------------------------------------------------------------- session-block bootstrap (U9's frozen design)
print("\n" + "=" * 90 + f"\nSESSION-BLOCK BOOTSTRAP for {best_key} (1000 resamples, per U9's frozen design)\n" + "=" * 90)
rng = np.random.RandomState(20260809)
sessions = sub["sess_date"].unique()
sess_groups = {s: sub[sub["sess_date"] == s].index.to_numpy() for s in sessions}
obs_rho = float(sub[feat_sel].corr(sub[ycol_sel], method="spearman"))
boot_rhos = []
for _ in range(1000):
    sampled = rng.choice(sessions, size=len(sessions), replace=True)
    idx = np.concatenate([sess_groups[s] for s in sampled if len(sess_groups[s]) > 0])
    if len(idx) < 10:
        continue
    d = sub.loc[idx]
    r = d[feat_sel].corr(d[ycol_sel], method="spearman")
    if r == r:
        boot_rhos.append(r)
boot_rhos = np.array(boot_rhos)
ci_lo, ci_hi = np.percentile(boot_rhos, [2.5, 97.5]) if len(boot_rhos) else (np.nan, np.nan)
print(f"observed rho={obs_rho:.4f} (n_sessions={len(sessions)}), "
      f"session-block-bootstrap 95% CI=[{ci_lo:.4f}, {ci_hi:.4f}], "
      f"excludes 0: {ci_lo > 0 or ci_hi < 0 if ci_lo == ci_lo else 'N/A'}")

summary = {
    "n_productB_entries": len(feat_B), "n_productA_scaleins": len(feat_A),
    "n_sessions": int(sub["sess_date"].nunique()),
    "max_redundancy_rho": max_redund,
    "residual_info_results": results,
    "strongest_cell": best_key,
    "right_tail_quartile": {
        "top_quartile_mean": float(top_q[feat_sel].mean()), "bottom_quartile_mean": float(bot_q[feat_sel].mean()),
        "population_mean": float(sub[feat_sel].mean()), "n_top": len(top_q), "n_bottom": len(bot_q),
    },
    "session_block_bootstrap": {"observed_rho": obs_rho, "ci_lo": float(ci_lo), "ci_hi": float(ci_hi),
                                 "n_boot": len(boot_rhos), "n_sessions": len(sessions)},
}
json.dump(summary, open(os.path.join(OUT, "u9b_analysis_summary.json"), "w"), indent=2, default=str)
feat_B.to_csv(os.path.join(OUT, "event_features_B_with_outcomes.csv"), index=False)
feat_A.to_csv(os.path.join(OUT, "event_features_A_with_outcomes.csv"), index=False)
print("\nU9B analysis complete.")
