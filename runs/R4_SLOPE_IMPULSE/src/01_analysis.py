"""R4 -- slope + impulse residual-information tests. Per spec.yaml: information-addition tests
only, interpretable OLS + residualized Spearman, no black-box model."""
import os, sys, json
import numpy as np, pandas as pd

SA0_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                        "SA0_SYSTEM_STRUCTURE", "src")
sys.path.insert(0, SA0_SRC)
import substrate as S

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

ledger = pd.read_parquet(S.LEDGER_PATH, columns=[
    "t_idx", "close", "open", "high", "low", "sigma460_atr_proxy_pts", "sess_date"])
block_sum = pd.read_csv(S.BLOCKSUM_PATH)

# recompute entry_t_idx the same way SA0's other scripts do (age_bars==1, first bar of a block)
er = pd.read_parquet(S.LEDGER_PATH, columns=["t_idx", "age_bars", "position", "block_id"])
entry_map = er[(er["age_bars"] == 1) & (er["position"] != 0)].set_index("block_id")["t_idx"]
block_sum["entry_t_idx"] = block_sum["block_id"].map(entry_map)
block_sum = block_sum.dropna(subset=["entry_t_idx"])
block_sum["entry_t_idx"] = block_sum["entry_t_idx"].astype(int)

close = ledger["close"].to_numpy()
open_ = ledger["open"].to_numpy()
high = ledger["high"].to_numpy()
low = ledger["low"].to_numpy()
sig = ledger["sigma460_atr_proxy_pts"].to_numpy()
sess_date_arr = ledger["sess_date"].to_numpy()
n = len(ledger)

LOOKBACK = 20


def causal_slope(t0):
    if t0 < LOOKBACK:
        return np.nan
    y = close[t0 - LOOKBACK + 1: t0 + 1]
    x = np.arange(LOOKBACK)
    slope = np.polyfit(x, y, 1)[0]
    return slope


print("computing causal slope + impulse features at each entry bar ...", flush=True)
slopes, ranges_atr, bodies_atr, clvs = [], [], [], []
for t0 in block_sum["entry_t_idx"]:
    slopes.append(causal_slope(int(t0)))
    s = sig[t0] if sig[t0] > 0 else np.nan
    ranges_atr.append((high[t0] - low[t0]) / s if s else np.nan)
    bodies_atr.append(abs(close[t0] - open_[t0]) / s if s else np.nan)
    hl = high[t0] - low[t0]
    clvs.append((close[t0] - low[t0]) / hl if hl > 0 else np.nan)

block_sum["slope_raw"] = slopes
block_sum["slope_atr_norm"] = block_sum["slope_raw"] / sig[block_sum["entry_t_idx"].to_numpy()]
block_sum["range_atr"] = ranges_atr
block_sum["body_atr"] = bodies_atr
block_sum["clv"] = clvs
block_sum["side"] = block_sum["side"].astype(int)
# orient slope/impulse in the TRADE's own direction (positive = aligned with the side taken)
block_sum["slope_aligned"] = block_sum["slope_atr_norm"] * block_sum["side"]
block_sum["clv_aligned"] = np.where(block_sum["side"] > 0, block_sum["clv"], 1 - block_sum["clv"])

block_sum["M_abs"] = block_sum["entry_T"].abs()  # proxy already in block_sum from P0
block_sum["M_strength_tercile"] = pd.qcut(block_sum["M_abs"], 3, labels=["weak", "mid", "strong"], duplicates="drop")
block_sum["vol_tercile"] = pd.qcut(sig[block_sum["entry_t_idx"].to_numpy()], 3, labels=["low", "mid", "high"], duplicates="drop")
entry_sess_date = ledger.set_index("t_idx").loc[block_sum["entry_t_idx"], "sess_date"].to_numpy()
block_sum["year"] = pd.to_datetime(entry_sess_date).year

block_sum.to_csv(os.path.join(OUT, "r4_features.csv"), index=False)

print("=" * 90, "\nRAW CORRELATION: slope / impulse features vs net_pnl\n", "=" * 90, sep="")
for col in ["slope_aligned", "range_atr", "body_atr", "clv_aligned"]:
    sub = block_sum.dropna(subset=[col, "net_pnl"])
    rho = float(sub[col].corr(sub["net_pnl"], method="spearman"))
    print(f"  Spearman({col}, net_pnl) = {rho:.4f}  (n={len(sub)})")

print("\n" + "=" * 90, "\nRESIDUALIZED CORRELATION (after removing M_strength x vol_tercile bucket mean)\n", "=" * 90, sep="")
block_sum["bucket"] = block_sum["M_strength_tercile"].astype(str) + "_" + block_sum["vol_tercile"].astype(str)
block_sum["bucket_mean_pnl"] = block_sum.groupby("bucket")["net_pnl"].transform("mean")
block_sum["resid_pnl"] = block_sum["net_pnl"] - block_sum["bucket_mean_pnl"]
for col in ["slope_aligned", "range_atr", "body_atr", "clv_aligned"]:
    sub = block_sum.dropna(subset=[col, "resid_pnl"])
    rho = float(sub[col].corr(sub["resid_pnl"], method="spearman"))
    print(f"  Spearman({col}, RESIDUAL net_pnl | M-strength x vol bucket) = {rho:.4f}  (n={len(sub)})")

print("\n" + "=" * 90, "\nOLS R^2 IMPROVEMENT TEST (interpretable linear regression, not a black box)\n", "=" * 90, sep="")


def ols_r2(X_cols, y_col="net_pnl"):
    sub = block_sum.dropna(subset=X_cols + [y_col])
    X = sub[X_cols].to_numpy(dtype=float)
    X = np.column_stack([np.ones(len(X)), X])
    y = sub[y_col].to_numpy(dtype=float)
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    yhat = X @ coef
    ss_res = np.sum((y - yhat) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan
    return r2, coef, len(sub)


baseline_cols = ["M_abs"]
block_sum["vol_z"] = (block_sum["vol_tercile"].cat.codes if hasattr(block_sum["vol_tercile"], "cat") else 0)
baseline_cols2 = ["M_abs", "vol_z"]
r2_base, coef_base, n_base = ols_r2(baseline_cols2)
print(f"baseline R^2 (net_pnl ~ M_abs + vol_tercile_code): {r2_base:.5f}  (n={n_base})")

for feat in ["slope_aligned", "range_atr", "body_atr", "clv_aligned"]:
    r2_ext, coef_ext, n_ext = ols_r2(baseline_cols2 + [feat])
    print(f"  + {feat}: R^2 = {r2_ext:.5f}  (delta R^2 = {r2_ext - r2_base:+.5f}, n={n_ext}, "
          f"feature coef sign = {'+' if coef_ext[-1] > 0 else '-'})")

print("\n" + "=" * 90, "\nYEAR-BY-YEAR STABILITY of the strongest residualized relationship\n", "=" * 90, sep="")
best_feat = None
best_abs_rho = 0
for col in ["slope_aligned", "range_atr", "body_atr", "clv_aligned"]:
    sub = block_sum.dropna(subset=[col, "resid_pnl"])
    rho = float(sub[col].corr(sub["resid_pnl"], method="spearman"))
    if abs(rho) > best_abs_rho:
        best_abs_rho = abs(rho); best_feat = col
print(f"strongest residualized feature: {best_feat} (|rho|={best_abs_rho:.4f})")
yby = []
for yr, g in block_sum.dropna(subset=[best_feat, "resid_pnl"]).groupby("year"):
    rho_yr = float(g[best_feat].corr(g["resid_pnl"], method="spearman"))
    yby.append({"year": yr, "n": len(g), "spearman_resid": rho_yr})
yby_df = pd.DataFrame(yby)
print(yby_df.round(4).to_string(index=False))
yby_df.to_csv(os.path.join(OUT, "r4_year_by_year_best_feature.csv"), index=False)

summary = {
    "best_feature": best_feat, "best_feature_abs_rho": best_abs_rho,
    "n_years_same_sign": int((np.sign(yby_df["spearman_resid"]) == np.sign(yby_df["spearman_resid"].iloc[0])).sum()),
    "n_years_total": len(yby_df),
}
json.dump(summary, open(os.path.join(OUT, "r4_summary.json"), "w"), indent=2)
print("\n" + json.dumps(summary, indent=2))
print("\nR4 analysis complete.")
