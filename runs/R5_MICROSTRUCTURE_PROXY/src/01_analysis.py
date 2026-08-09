"""R5 -- OHLCV-derived microstructure-like proxies. Same information-addition framework as R4."""
import os, sys, json
import numpy as np, pandas as pd

SA0_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                        "SA0_SYSTEM_STRUCTURE", "src")
sys.path.insert(0, SA0_SRC)
import substrate as S

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

ledger = pd.read_parquet(S.LEDGER_PATH, columns=[
    "t_idx", "close", "open", "high", "low", "volume", "sigma460_atr_proxy_pts",
    "vwap_dist_pts", "roll_hi20", "roll_lo20"])
block_sum = pd.read_csv(S.BLOCKSUM_PATH)
er = pd.read_parquet(S.LEDGER_PATH, columns=["t_idx", "age_bars", "position", "block_id"])
entry_map = er[(er["age_bars"] == 1) & (er["position"] != 0)].set_index("block_id")["t_idx"]
block_sum["entry_t_idx"] = block_sum["block_id"].map(entry_map)
block_sum = block_sum.dropna(subset=["entry_t_idx"])
block_sum["entry_t_idx"] = block_sum["entry_t_idx"].astype(int)
block_sum["side"] = block_sum["side"].astype(int)

close = ledger["close"].to_numpy(); open_ = ledger["open"].to_numpy()
high = ledger["high"].to_numpy(); low = ledger["low"].to_numpy()
volume = ledger["volume"].to_numpy()
sig = ledger["sigma460_atr_proxy_pts"].to_numpy()
vwap_dist = ledger["vwap_dist_pts"].to_numpy()
roll_hi20 = ledger["roll_hi20"].to_numpy(); roll_lo20 = ledger["roll_lo20"].to_numpy()
n = len(ledger)

print("computing OHLCV-derived proxy features at each entry bar ...", flush=True)
vol_avg20 = pd.Series(volume).rolling(20, min_periods=5).mean().to_numpy()
bar_range = high - low
range20 = pd.Series(bar_range).rolling(20, min_periods=5).sum().to_numpy()
range100 = pd.Series(bar_range).rolling(100, min_periods=20).sum().to_numpy()

rows = []
for _, r in block_sum.iterrows():
    t0 = int(r["entry_t_idx"])
    side = int(r["side"])
    va = vol_avg20[t0 - 1] if t0 >= 1 else np.nan  # prior-bar trailing avg (causal, excludes bar t0 itself)
    vol_surprise = volume[t0] / va if va and va > 0 else np.nan
    # failed-breakout/rejection: broke prior 20-bar extreme intrabar but closed back inside it
    prior_hi = roll_hi20[t0 - 1] if t0 >= 1 else np.nan
    prior_lo = roll_lo20[t0 - 1] if t0 >= 1 else np.nan
    if side > 0:
        broke_extreme = high[t0] > prior_hi if prior_hi == prior_hi else False
        rejected = broke_extreme and close[t0] < prior_hi
    else:
        broke_extreme = low[t0] < prior_lo if prior_lo == prior_lo else False
        rejected = broke_extreme and close[t0] > prior_lo
    vwap_disp_atr = (vwap_dist[t0] / sig[t0] * side) if sig[t0] > 0 else np.nan
    short_term_vol_ratio = (bar_range[t0-4:t0+1].sum() / 5) / sig[t0] if t0 >= 4 and sig[t0] > 0 else np.nan
    dxv = np.sign(close[t0] - open_[t0]) * side * (vol_surprise if vol_surprise == vol_surprise else np.nan)
    compression_ratio = (range20[t0 - 1] / 20) / (range100[t0 - 1] / 100) if (t0 >= 1 and range100[t0-1] and range100[t0-1] > 0) else np.nan
    rows.append({
        "block_id": r["block_id"], "net_pnl": r["net_pnl"], "side": side,
        "entry_T": r["entry_T"], "entry_t_idx": t0,
        "vol_surprise": vol_surprise, "failed_breakout_rejection": bool(rejected),
        "vwap_disp_atr_aligned": vwap_disp_atr, "short_term_vol_ratio": short_term_vol_ratio,
        "direction_x_volume": dxv, "vol_compression_ratio": compression_ratio,
    })
feat = pd.DataFrame(rows)
feat["M_abs"] = feat["entry_T"].abs()
feat["M_strength_tercile"] = pd.qcut(feat["M_abs"], 3, labels=["weak", "mid", "strong"], duplicates="drop")
feat["vol_tercile"] = pd.qcut(sig[feat["entry_t_idx"].to_numpy()], 3, labels=["low", "mid", "high"], duplicates="drop")
entry_sess_date = pd.read_parquet(S.LEDGER_PATH, columns=["t_idx", "sess_date"]).set_index("t_idx").loc[feat["entry_t_idx"], "sess_date"].to_numpy()
feat["year"] = pd.to_datetime(entry_sess_date).year
feat["bucket"] = feat["M_strength_tercile"].astype(str) + "_" + feat["vol_tercile"].astype(str)
feat["bucket_mean_pnl"] = feat.groupby("bucket")["net_pnl"].transform("mean")
feat["resid_pnl"] = feat["net_pnl"] - feat["bucket_mean_pnl"]
feat.to_csv(os.path.join(OUT, "r5_features.csv"), index=False)

print("=" * 90, "\nFAILED BREAKOUT / REJECTION: categorical outcome split\n", "=" * 90, sep="")
g = feat.groupby("failed_breakout_rejection").agg(
    n=("net_pnl", "size"), mean_pnl=("net_pnl", "mean"), win_rate=("net_pnl", lambda x: float((x > 0).mean())))
print(g.round(2))
g_resid = feat.groupby("failed_breakout_rejection")["resid_pnl"].mean()
print("\nresidualized mean (after M-strength x vol bucket):")
print(g_resid.round(2))

print("\n" + "=" * 90, "\nCONTINUOUS FEATURES: raw + residualized Spearman, OLS delta-R^2\n", "=" * 90, sep="")


def ols_r2(df, X_cols, y_col):
    sub = df.dropna(subset=X_cols + [y_col])
    X = sub[X_cols].to_numpy(dtype=float)
    X = np.column_stack([np.ones(len(X)), X])
    y = sub[y_col].to_numpy(dtype=float)
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    yhat = X @ coef
    ss_res = np.sum((y - yhat) ** 2); ss_tot = np.sum((y - y.mean()) ** 2)
    return (1 - ss_res / ss_tot if ss_tot > 0 else np.nan), len(sub)


feat["vol_z"] = feat["vol_tercile"].cat.codes
r2_base, n_base = ols_r2(feat, ["M_abs", "vol_z"], "net_pnl")
print(f"baseline R^2 (M_abs + vol_tercile_code): {r2_base:.5f} (n={n_base})")

cont_feats = ["vol_surprise", "vwap_disp_atr_aligned", "short_term_vol_ratio",
              "direction_x_volume", "vol_compression_ratio"]
results = {}
for c in cont_feats:
    sub = feat.dropna(subset=[c, "net_pnl", "resid_pnl"])
    rho_raw = float(sub[c].corr(sub["net_pnl"], method="spearman"))
    rho_resid = float(sub[c].corr(sub["resid_pnl"], method="spearman"))
    r2_ext, n_ext = ols_r2(feat, ["M_abs", "vol_z", c], "net_pnl")
    results[c] = {"rho_raw": rho_raw, "rho_resid": rho_resid, "delta_r2": r2_ext - r2_base, "n": n_ext}
    print(f"  {c}: raw_rho={rho_raw:.4f} resid_rho={rho_resid:.4f} delta_R2={r2_ext - r2_base:+.5f} (n={n_ext})")

print("\n" + "=" * 90, "\nYEAR-BY-YEAR STABILITY of each feature's residualized Spearman\n", "=" * 90, sep="")
yby_all = {}
for c in cont_feats:
    yby = []
    for yr, g in feat.dropna(subset=[c, "resid_pnl"]).groupby("year"):
        yby.append({"year": yr, "n": len(g), "rho": float(g[c].corr(g["resid_pnl"], method="spearman"))})
    yby_df = pd.DataFrame(yby)
    same_sign = int((np.sign(yby_df["rho"]) == np.sign(yby_df["rho"].iloc[0])).sum()) if len(yby_df) else 0
    yby_all[c] = yby_df.to_dict("records")
    print(f"\n{c} (same sign in {same_sign}/{len(yby_df)} years):")
    print(yby_df.round(4).to_string(index=False))

json.dump({"results": results, "year_by_year": yby_all}, open(os.path.join(OUT, "r5_summary.json"), "w"), indent=2, default=str)
print("\nR5 analysis complete.")
