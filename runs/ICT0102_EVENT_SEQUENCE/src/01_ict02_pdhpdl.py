"""ICT02 -- Prior-Day-High/Low (PDH/PDL) objective test. Directive: CONTINUOUS_EVOLUTION addendum
task ICT01+ICT02 (research/system_master/CONTINUOUS_EVOLUTION_WAVE4_PLAN.md row "ICT01+ICT02").

At every bar, compute the CAUSALLY-KNOWN prior-COMPLETE-session's high (PDH) and low (PDL) --
never the current in-progress session's own high/low. Test whether distance-to-PDH/PDL and
sweep/rejection/acceptance state predict forward-20-bar Product-B P&L beyond what M-strength x
vol-tercile alone predict (R4/R5/EXP01 information-addition methodology, reused verbatim).
"""
import os, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

cols = ["t_idx", "sess_date", "high", "low", "close", "M", "position_B", "session_phase",
        "sigma460_atr_proxy_pts", "bar_pnl_B_nq_dollars", "year", "is_health_only_bar"]
u0 = pd.read_parquet(os.path.join(ROOT, "runs", "U0_UNIFIED_STATE", "out", "u0_state_table.parquet"),
                      columns=cols)
n_all = len(u0)
print(f"[ICT02] loaded {n_all} bars", flush=True)

# ---------------------------------------------------------------- correctness gate
canon = u0[~u0["is_health_only_bar"]]
canon_net = canon["bar_pnl_B_nq_dollars"].sum()
print(f"[ICT02] correctness gate: canonical B-NQ net = {canon_net:.2f} (must be 301915.92)", flush=True)
assert abs(canon_net - 301915.92) < 0.01, "CORRECTNESS GATE FAILED -- do not proceed"

# ---------------------------------------------------------------- PDH/PDL construction (causal, shift-by-1-session)
sess_summary = u0.groupby("sess_date", sort=True).agg(sess_high=("high", "max"), sess_low=("low", "min"))
sess_summary = sess_summary.sort_index()
sess_summary["pdh"] = sess_summary["sess_high"].shift(1)
sess_summary["pdl"] = sess_summary["sess_low"].shift(1)
u0 = u0.merge(sess_summary[["pdh", "pdl"]], left_on="sess_date", right_index=True, how="left")
u0 = u0.sort_values("t_idx").reset_index(drop=True)
n_no_pdh = u0["pdh"].isna().sum()
print(f"[ICT02] {n_no_pdh} bars in the first session have no PDH/PDL (dropped)", flush=True)

sig = u0["sigma460_atr_proxy_pts"].replace(0, np.nan)
u0["dist_to_pdh_pts"] = u0["close"] - u0["pdh"]          # >0 = price above PDH
u0["dist_to_pdl_pts"] = u0["close"] - u0["pdl"]          # >0 = price above PDL
u0["dist_to_pdh_atr"] = u0["dist_to_pdh_pts"] / sig
u0["dist_to_pdl_atr"] = u0["dist_to_pdl_pts"] / sig

# causal running intraday extremes (within the CURRENT session, cumulative, so no lookahead)
u0["run_hi"] = u0.groupby("sess_date")["high"].cummax()
u0["run_lo"] = u0.groupby("sess_date")["low"].cummin()
u0["swept_pdh_today"] = u0["run_hi"] > u0["pdh"]
u0["swept_pdl_today"] = u0["run_lo"] < u0["pdl"]

def state(swept, close_beyond):
    return np.where(~swept, "not_swept", np.where(close_beyond, "accepted", "rejected"))

u0["state_pdh"] = state(u0["swept_pdh_today"].to_numpy(), (u0["close"] >= u0["pdh"]).to_numpy())
u0["state_pdl"] = state(u0["swept_pdl_today"].to_numpy(), (u0["close"] <= u0["pdl"]).to_numpy())

print("\n" + "=" * 90 + "\nDESCRIPTIVE: PDH/PDL sweep-state frequency (all bars with a defined PDH/PDL)\n" + "=" * 90)
desc = u0.dropna(subset=["pdh", "pdl"])
print("state_pdh:\n", desc["state_pdh"].value_counts(normalize=True).round(4))
print("state_pdl:\n", desc["state_pdl"].value_counts(normalize=True).round(4))

print("\n" + "=" * 90 + "\nDESCRIPTIVE: mean dist-to-PDH/PDL (ATR units) by M-sign x vol-tercile\n" + "=" * 90)
desc2 = desc.copy()
desc2["M_sign"] = np.where(desc2["M"] > 0, "M+", np.where(desc2["M"] < 0, "M-", "M0"))
desc2["vol_tercile"] = pd.qcut(desc2["sigma460_atr_proxy_pts"], 3, labels=["low", "mid", "high"], duplicates="drop")
piv = desc2.groupby(["M_sign", "vol_tercile"], observed=True)[["dist_to_pdh_atr", "dist_to_pdl_atr"]].mean()
print(piv.round(3))

print("\n" + "=" * 90 + "\nDESCRIPTIVE: sweep-state rate by session_phase\n" + "=" * 90)
print(desc2.groupby("session_phase", observed=True)[["swept_pdh_today", "swept_pdl_today"]].mean().round(4))

# ---------------------------------------------------------------- trade-aligned features (position_B != 0 bars)
sub = u0[(u0["position_B"] != 0) & u0["pdh"].notna() & (~u0["is_health_only_bar"])].copy()
side = sub["position_B"].to_numpy()  # +1 / -1
pdh = sub["pdh"].to_numpy(); pdl = sub["pdl"].to_numpy(); close = sub["close"].to_numpy()
sigv = sub["sigma460_atr_proxy_pts"].replace(0, np.nan).to_numpy()

dist_fav = np.where(side > 0, (pdh - close), (close - pdl)) / sigv
dist_unfav = np.where(side > 0, (close - pdl), (pdh - close)) / sigv
state_fav = np.where(side > 0, sub["state_pdh"], sub["state_pdl"])
state_unfav = np.where(side > 0, sub["state_pdl"], sub["state_pdh"])

sub["dist_favorable_atr"] = dist_fav
sub["dist_unfavorable_atr"] = dist_unfav
sub["swept_favorable"] = (state_fav != "not_swept").astype(int)
sub["swept_unfavorable"] = (state_unfav != "not_swept").astype(int)
sub["accepted_favorable"] = (state_fav == "accepted").astype(int)
sub["rejected_favorable"] = (state_fav == "rejected").astype(int)

print(f"\n[ICT02] {len(sub)} position_B!=0 canonical bars with defined PDH/PDL for the forward-value test", flush=True)

# ---------------------------------------------------------------- forward-20-bar P&L (vectorized cumsum, whole table so
# the outcome window can legitimately look past the canonical/health-only boundary into already-consumed 2026-06/07
# data -- never into the sealed >=2026-08-01 region, which does not exist in this table)
bpnl_full = u0.sort_values("t_idx")["bar_pnl_B_nq_dollars"].to_numpy()
cs = np.concatenate([[0.0], np.cumsum(bpnl_full)])
t_idx_all = u0.sort_values("t_idx")["t_idx"].to_numpy()
max_t = t_idx_all.max()

t_sub = sub["t_idx"].to_numpy()
fwd20 = np.full(len(t_sub), np.nan)
valid = t_sub + 20 <= max_t
fwd20[valid] = cs[t_sub[valid] + 21] - cs[t_sub[valid] + 1]
sub["fwd20_pnl"] = fwd20
sub = sub.dropna(subset=["fwd20_pnl"])
print(f"[ICT02] {len(sub)} bars with a complete forward-20-bar window", flush=True)

sub["M_abs"] = sub["M"].abs()
sub["M_tercile"] = pd.qcut(sub["M_abs"], 3, labels=["weak", "mid", "strong"], duplicates="drop")
sub["vol_tercile"] = pd.qcut(sub["sigma460_atr_proxy_pts"], 3, labels=["low", "mid", "high"], duplicates="drop")
sub["vol_z"] = sub["vol_tercile"].cat.codes
sub["bucket"] = sub["M_tercile"].astype(str) + "_" + sub["vol_tercile"].astype(str)
sub["bucket_mean"] = sub.groupby("bucket", observed=True)["fwd20_pnl"].transform("mean")
sub["resid_pnl"] = sub["fwd20_pnl"] - sub["bucket_mean"]

sub.to_csv(os.path.join(OUT, "ict02_features.csv"), index=False)

def ols_r2(df_, X_cols, y_col):
    d = df_.dropna(subset=X_cols + [y_col])
    X = d[X_cols].to_numpy(dtype=float)
    X = np.column_stack([np.ones(len(X)), X])
    y = d[y_col].to_numpy(dtype=float)
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    yhat = X @ coef
    ss_res = np.sum((y - yhat) ** 2); ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan
    return r2, coef, len(d)

baseline_cols = ["M_abs", "vol_z"]
r2_base, coef_base, n_base = ols_r2(sub, baseline_cols, "fwd20_pnl")
print(f"\n[ICT02] baseline R^2 (fwd20_pnl ~ M_abs + vol_z): {r2_base:.5f} (n={n_base})")

feat_cols = ["dist_favorable_atr", "dist_unfavorable_atr", "swept_favorable", "swept_unfavorable",
             "accepted_favorable", "rejected_favorable"]
results = []
print("\n" + "=" * 90 + "\nRAW / RESIDUALIZED CORRELATION + OLS DELTA-R^2 (trade-direction-aligned PDH/PDL features)\n" + "=" * 90)
for col in feat_cols:
    d = sub.dropna(subset=[col, "fwd20_pnl", "resid_pnl"])
    rho_raw = float(d[col].corr(d["fwd20_pnl"], method="spearman"))
    rho_res = float(d[col].corr(d["resid_pnl"], method="spearman"))
    r2_ext, coef_ext, n_ext = ols_r2(sub, baseline_cols + [col], "fwd20_pnl")
    print(f"  {col}: raw Spearman={rho_raw:+.4f}  resid Spearman={rho_res:+.4f}  "
          f"R^2={r2_ext:.5f} (dR2={r2_ext - r2_base:+.5f}, n={n_ext}, coef_sign={'+' if coef_ext[-1] > 0 else '-'})")
    results.append({"feature": col, "rho_raw": rho_raw, "rho_resid": rho_res,
                     "r2_ext": r2_ext, "d_r2": r2_ext - r2_base, "n": n_ext,
                     "coef_sign": "+" if coef_ext[-1] > 0 else "-"})

# combined "full PDH/PDL block" model
r2_full, coef_full, n_full = ols_r2(sub, baseline_cols + feat_cols, "fwd20_pnl")
print(f"\n  FULL PDH/PDL block (all 6 features): R^2={r2_full:.5f} (dR2={r2_full - r2_base:+.5f}, n={n_full})")

# ---------------------------------------------------------------- year-by-year stability of the strongest feature
best = max(results, key=lambda r: abs(r["rho_resid"]))
print(f"\n[ICT02] strongest residualized feature: {best['feature']} (rho_resid={best['rho_resid']:+.4f})")
yby = []
for yr, g in sub.dropna(subset=[best["feature"], "resid_pnl"]).groupby("year"):
    if len(g) < 50:
        continue
    rho_yr = float(g[best["feature"]].corr(g["resid_pnl"], method="spearman"))
    yby.append({"year": int(yr), "n": len(g), "spearman_resid": rho_yr})
yby_df = pd.DataFrame(yby)
print(yby_df.round(4).to_string(index=False))

# ---------------------------------------------------------------- 2022-2025-only delta vs control / chronology
print("\n" + "=" * 90 + "\nCHRONOLOGY: does the FULL PDH/PDL block change 2022-2025 realized fwd20_pnl sum vs raw M/vol baseline?\n" + "=" * 90)
sub_2225 = sub[sub["year"].between(2022, 2025)]
ctrl_2225_sum = sub_2225["fwd20_pnl"].sum()
print(f"2022-2025 sum fwd20_pnl over position_B!=0 bars (control, no PDH/PDL info used to change the policy): "
      f"${ctrl_2225_sum:,.2f} over {len(sub_2225)} bars")

# ---------------------------------------------------------------- right-tail audit: PDH/PDL state at entry of top/bottom-20 blocks
print("\n" + "=" * 90 + "\nRIGHT-TAIL AUDIT: PDH/PDL sweep-state at ENTRY of top-20 / bottom-20 all-time Product-B blocks\n" + "=" * 90)
u0b = pd.read_parquet(os.path.join(ROOT, "runs", "U0_UNIFIED_STATE", "out", "u0_state_table.parquet"),
                       columns=["t_idx", "block_id_B", "run_pnl_B_dollars", "action_B", "is_health_only_bar"])
canon_b = u0b[~u0b["is_health_only_bar"]]
block_net = canon_b.groupby("block_id_B")["run_pnl_B_dollars"].last()
top20 = block_net.nlargest(20).index
bot20 = block_net.nsmallest(20).index
entries = canon_b[canon_b["action_B"] == "ENTRY"].set_index("block_id_B")["t_idx"]
u0_idx = u0.set_index("t_idx")

def tail_state_summary(block_ids, label):
    rows = []
    for bid in block_ids:
        if bid not in entries.index:
            continue
        t = entries.loc[bid]
        if isinstance(t, pd.Series):
            t = t.iloc[0]
        if t in u0_idx.index:
            rows.append({"block_id": bid, "net": float(block_net.loc[bid]),
                         "state_pdh": u0_idx.loc[t, "state_pdh"], "state_pdl": u0_idx.loc[t, "state_pdl"]})
    d = pd.DataFrame(rows)
    print(f"\n{label} (n={len(d)}):")
    print(d[["state_pdh", "state_pdl"]].apply(lambda c: c.value_counts()).fillna(0).astype(int))
    return d

top_d = tail_state_summary(top20, "TOP-20 blocks")
bot_d = tail_state_summary(bot20, "BOTTOM-20 blocks")

summary = {
    "n_all_bars": int(n_all), "n_test_bars": int(len(sub)),
    "baseline_r2": float(r2_base), "full_block_r2": float(r2_full), "full_block_dr2": float(r2_full - r2_base),
    "feature_results": results,
    "best_feature": best["feature"], "best_feature_rho_resid": best["rho_resid"],
    "year_by_year_best_feature": yby_df.to_dict("records"),
    "state_pdh_freq": desc["state_pdh"].value_counts(normalize=True).to_dict(),
    "state_pdl_freq": desc["state_pdl"].value_counts(normalize=True).to_dict(),
    "ctrl_2225_fwd20_sum": float(ctrl_2225_sum), "ctrl_2225_n": int(len(sub_2225)),
}
json.dump(summary, open(os.path.join(OUT, "ict02_summary.json"), "w"), indent=2, default=str)
top_d.to_csv(os.path.join(OUT, "ict02_top20_states.csv"), index=False)
bot_d.to_csv(os.path.join(OUT, "ict02_bottom20_states.csv"), index=False)
print("\nICT02 analysis complete.")
