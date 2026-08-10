"""EXP01 -- Product-A marginal exposure value shape. Tests whether per-contract forward value
varies systematically with exposure LEVEL (1-13) after controlling for |M_A_raw| conviction
(the confound U6 already found mediates PA0's raw exposure-band pattern), and fits a simple
linear-vs-quadratic curvature test to characterize the shape.
"""
import os, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

u0 = pd.read_parquet(os.path.join(ROOT, "runs", "U0_UNIFIED_STATE", "out", "u0_state_table.parquet"),
                      columns=["t_idx", "target_exposure_A", "M_A_raw", "bar_pnl_A_dollars",
                               "action_A", "is_health_only_bar", "year"])
canon = u0[~u0["is_health_only_bar"]].copy()
n = len(canon)

bpnl_A = canon.set_index("t_idx")["bar_pnl_A_dollars"]
tidx_arr = canon["t_idx"].to_numpy()
exposure = canon["target_exposure_A"].to_numpy()
level = np.abs(exposure)

# forward-20-bar P&L per contract, at every nonzero-exposure bar (not just SCALE_IN, to cover
# the full exposure range 1-13 with enough density per level)
print("[EXP01] computing forward-20-bar P&L per contract at every nonzero-exposure bar ...", flush=True)
mask = level > 0
idx_nonzero = tidx_arr[mask]
fwd20 = np.full(len(idx_nonzero), np.nan)
bpnl_dict = bpnl_A.to_dict()
max_tidx = tidx_arr.max()
for i, t in enumerate(idx_nonzero):
    s = 0.0
    any_val = False
    for k in range(t + 1, min(t + 21, max_tidx + 1)):
        v = bpnl_dict.get(k)
        if v is not None:
            s += v
            any_val = True
    fwd20[i] = s if any_val else np.nan

df = pd.DataFrame({
    "t_idx": idx_nonzero, "level": level[mask], "M_abs": np.abs(canon.loc[mask, "M_A_raw"].to_numpy()),
    "year": canon.loc[mask, "year"].to_numpy(), "fwd20_pnl": fwd20,
})
df["fwd20_per_contract"] = df["fwd20_pnl"] / df["level"]
df = df.dropna(subset=["fwd20_per_contract"])
print(f"[EXP01] {len(df)} usable nonzero-exposure bars, levels 1-{int(df['level'].max())}", flush=True)

# ---------------------------------------------------------------- raw per-level value (PA0-style, for continuity)
print("\n" + "=" * 90 + "\nRAW PER-LEVEL MARGINAL VALUE (PA0-style, unconditional)\n" + "=" * 90)
raw_by_level = df.groupby("level")["fwd20_per_contract"].agg(["mean", "median", "count"])
print(raw_by_level.round(3))

# ---------------------------------------------------------------- residualize against |M| tercile
df["M_tercile"] = pd.qcut(df["M_abs"], 3, labels=["weak", "mid", "strong"], duplicates="drop")
df["bucket_mean"] = df.groupby("M_tercile", observed=True)["fwd20_per_contract"].transform("mean")
df["resid_value"] = df["fwd20_per_contract"] - df["bucket_mean"]

print("\n" + "=" * 90 + "\nRESIDUALIZED PER-LEVEL MARGINAL VALUE (after removing M-tercile bucket mean)\n" + "=" * 90)
resid_by_level = df.groupby("level")["resid_value"].agg(["mean", "median", "count"])
print(resid_by_level.round(3))

# ---------------------------------------------------------------- curvature test (linear vs quadratic)
print("\n" + "=" * 90 + "\nCURVATURE TEST (interpretable OLS: resid_value ~ level + level^2)\n" + "=" * 90)


def ols(df_, X_cols, y_col):
    d = df_.dropna(subset=X_cols + [y_col])
    X = d[X_cols].to_numpy(dtype=float)
    Xc = np.column_stack([np.ones(len(X)), X])
    y = d[y_col].to_numpy(dtype=float)
    coef, *_ = np.linalg.lstsq(Xc, y, rcond=None)
    resid = y - Xc @ coef
    n_, k_ = Xc.shape
    sigma2 = (resid @ resid) / max(n_ - k_, 1)
    se = np.sqrt(np.maximum(np.diag(sigma2 * np.linalg.pinv(Xc.T @ Xc)), 0))
    ss_res = np.sum(resid ** 2); ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan
    return coef, se, r2, len(d)


df["level_sq"] = df["level"] ** 2
coef, se, r2, n_used = ols(df, ["level", "level_sq"], "resid_value")
for nm, c, s in zip(["intercept", "level (linear term)", "level_sq (curvature term)"], coef, se):
    t = c / s if s > 0 else np.nan
    print(f"  {nm}: coef={c:.4f}  se={s:.4f}  t={t:.2f}")
print(f"  R^2={r2:.5f}  n={n_used}")
curvature_sign = "CONVEX (increasing marginal value)" if coef[2] > 0 else "CONCAVE (diminishing marginal value)"
print(f"\nInterpretation: quadratic coefficient sign indicates {curvature_sign} "
      f"once |M| conviction is controlled for.")

# ---------------------------------------------------------------- year-by-year stability of curvature sign
print("\n" + "=" * 90 + "\nYEAR-BY-YEAR STABILITY of the curvature term\n" + "=" * 90)
yby = []
for yr, g in df.groupby("year"):
    if len(g) < 100:
        continue
    c, s, r2_yr, n_yr = ols(g, ["level", "level_sq"], "resid_value")
    yby.append({"year": int(yr), "n": n_yr, "curvature_coef": float(c[2]),
                "t": float(c[2] / s[2]) if s[2] > 0 else None})
yby_df = pd.DataFrame(yby)
print(yby_df.round(5).to_string(index=False))

# ---------------------------------------------------------------- right-tail check: where do top-20 blocks spend their exposure?
print("\n" + "=" * 90 + "\nRIGHT-TAIL CHECK: exposure-level distribution of top-20 vs bottom-20 Product-A blocks\n" + "=" * 90)
u0_blocks = pd.read_parquet(os.path.join(ROOT, "runs", "U0_UNIFIED_STATE", "out", "u0_state_table.parquet"),
                             columns=["t_idx", "block_id_A", "run_pnl_A_dollars", "is_health_only_bar", "target_exposure_A"])
canon_b = u0_blocks[~u0_blocks["is_health_only_bar"]]
block_net = canon_b.groupby("block_id_A")["run_pnl_A_dollars"].last()
top20_blocks = block_net.nlargest(20).index
bot20_blocks = block_net.nsmallest(20).index
top20_levels = canon_b[canon_b["block_id_A"].isin(top20_blocks) & (canon_b["target_exposure_A"] != 0)]["target_exposure_A"].abs()
bot20_levels = canon_b[canon_b["block_id_A"].isin(bot20_blocks) & (canon_b["target_exposure_A"] != 0)]["target_exposure_A"].abs()
print(f"top-20 blocks: mean exposure level = {top20_levels.mean():.2f}, max = {top20_levels.max()}")
print(f"bottom-20 blocks: mean exposure level = {bot20_levels.mean():.2f}, max = {bot20_levels.max()}")
print(f"population: mean exposure level = {df['level'].mean():.2f}")

summary = {
    "n_usable": len(df), "raw_by_level": raw_by_level.reset_index().to_dict("records"),
    "resid_by_level": resid_by_level.reset_index().to_dict("records"),
    "curvature_coef": float(coef[2]), "curvature_se": float(se[2]),
    "curvature_t": float(coef[2] / se[2]) if se[2] > 0 else None, "r2": float(r2),
    "curvature_sign": curvature_sign,
    "year_by_year": yby_df.to_dict("records"),
    "righttail": {"top20_mean_level": float(top20_levels.mean()), "bot20_mean_level": float(bot20_levels.mean()),
                  "population_mean_level": float(df["level"].mean())},
}
json.dump(summary, open(os.path.join(OUT, "exp01_summary.json"), "w"), indent=2, default=str)
df.to_csv(os.path.join(OUT, "marginal_value_by_bar.csv"), index=False)
print("\nEXP01 marginal value shape analysis complete.")
