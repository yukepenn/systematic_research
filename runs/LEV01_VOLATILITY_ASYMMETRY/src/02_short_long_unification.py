"""LEV01 step 2 -- does the leverage effect mechanistically unify the already-documented short/
long Sharpe asymmetry (SA0: 0.18 vs 1.54; PA0: 0.40 vs 1.38)? Two sub-tests: (a) are shorts
mechanically entered disproportionately following negative-return regimes (expected, since
short entries require M<0); (b) does post-entry volatility response (the leverage-effect-
predicted asymmetry) correlate with worse outcomes MORE for shorts than for longs (the actual
mechanistic unification claim, not just the mechanical entry-timing coincidence).
"""
import os, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")

u0 = pd.read_parquet(os.path.join(ROOT, "runs", "U0_UNIFIED_STATE", "out", "u0_state_table.parquet"),
                      columns=["t_idx", "sess_date", "action_B", "position_B", "block_id_B",
                               "run_pnl_B_dollars", "sigma460_atr_proxy_pts", "is_health_only_bar",
                               "year", "action_A", "target_exposure_A", "block_id_A", "bar_pnl_A_dollars"])
sess_series = pd.read_csv(os.path.join(OUT, "session_series.csv"))
sess_series["sess_date"] = pd.to_datetime(sess_series["sess_date"])
sess_ret_map = sess_series.set_index("sess_date")["session_ret_atr"]
vol_change_map = sess_series.set_index("sess_date")["vol_change"]

u0["sess_date"] = pd.to_datetime(u0["sess_date"])
canon = u0[~u0["is_health_only_bar"]].copy()

# ---------------------------------------------------------------- Product B block table
entries = canon[canon["action_B"] == "ENTRY"].copy()
entries["side"] = np.sign(entries["position_B"])
block_net = canon.groupby("block_id_B")["run_pnl_B_dollars"].last()
entries["block_net_pnl"] = entries["block_id_B"].map(block_net)
# "recent return regime" as of the entry's OWN session (causal: that session's own return, which
# is fully determined by the entry bar's own time since session_ret_atr is close-to-close of the
# PRIOR session vs current session's own last close -- for an entry occurring mid-session, use the
# PRIOR completed session's own return as the causal regime indicator)
entries["prior_sess_ret_atr"] = entries["sess_date"].map(
    lambda d: sess_ret_map.get(sess_series.loc[sess_series["sess_date"] < d, "sess_date"].max(), np.nan))
entries["post_entry_vol_change"] = entries["sess_date"].map(vol_change_map)

print(f"[LEV01] {len(entries)} Product-B ENTRY events (canonical)", flush=True)

print("\n" + "=" * 90 + "\nTEST 2a -- ARE SHORTS MECHANICALLY ENTERED FOLLOWING NEGATIVE-RETURN REGIMES?\n" + "=" * 90)
sub = entries.dropna(subset=["prior_sess_ret_atr"])
short_prior_ret = sub.loc[sub["side"] == -1, "prior_sess_ret_atr"]
long_prior_ret = sub.loc[sub["side"] == 1, "prior_sess_ret_atr"]
print(f"shorts (n={len(short_prior_ret)}): mean prior-session-return(ATR-norm) = {short_prior_ret.mean():.4f}, "
      f"median={short_prior_ret.median():.4f}")
print(f"longs  (n={len(long_prior_ret)}): mean prior-session-return(ATR-norm) = {long_prior_ret.mean():.4f}, "
      f"median={long_prior_ret.median():.4f}")
print(f"P(prior session negative | short entry) = {(short_prior_ret < 0).mean():.3f}")
print(f"P(prior session negative | long entry)  = {(long_prior_ret < 0).mean():.3f}")

print("\n" + "=" * 90 + "\nTEST 2b -- DOES POST-ENTRY VOL RESPONSE HURT SHORTS MORE THAN LONGS? (the real unification test)\n" + "=" * 90)
sub2 = entries.dropna(subset=["post_entry_vol_change", "block_net_pnl"])


def ols(df, X_cols, y_col):
    d = df.dropna(subset=X_cols + [y_col])
    X = d[X_cols].to_numpy(dtype=float)
    Xc = np.column_stack([np.ones(len(X)), X])
    y = d[y_col].to_numpy(dtype=float)
    coef, *_ = np.linalg.lstsq(Xc, y, rcond=None)
    resid = y - Xc @ coef
    n_, k_ = Xc.shape
    sigma2 = (resid @ resid) / max(n_ - k_, 1)
    XtX_inv = np.linalg.pinv(Xc.T @ Xc)
    se = np.sqrt(np.maximum(np.diag(sigma2 * XtX_inv), 0))
    return coef, se, len(d)


sub2["short_dummy"] = (sub2["side"] == -1).astype(float)
sub2["volchg_x_short"] = sub2["post_entry_vol_change"] * sub2["short_dummy"]
coef, se, n_used = ols(sub2, ["post_entry_vol_change", "short_dummy", "volchg_x_short"], "block_net_pnl")
names = ["intercept", "post_entry_vol_change", "short_dummy", "volchg_x_short (unification term)"]
for nm, c, s in zip(names, coef, se):
    t = c / s if s > 0 else np.nan
    print(f"  {nm}: coef={c:.3f}  se={s:.3f}  t={t:.2f}")
print(f"  n={n_used}")
print("\nInterpretation: a NEGATIVE 'volchg_x_short' term means rising post-entry volatility "
      "hurts SHORT block outcomes more than LONG block outcomes of the same vol-change magnitude "
      "-- the specific mechanistic unification claim.")

print("\n" + "=" * 90 + "\nSimple split (non-parametric corroboration): mean block_net_pnl by side x post-entry vol-change tercile\n" + "=" * 90)
sub2["vc_tercile"] = pd.qcut(sub2["post_entry_vol_change"], 3, labels=["falling", "flat", "rising"], duplicates="drop")
piv = sub2.groupby(["side", "vc_tercile"], observed=True)["block_net_pnl"].agg(["mean", "count"])
print(piv.round(2))

# ---------------------------------------------------------------- Product A mirror check (lightweight)
print("\n" + "=" * 90 + "\nTEST 2c -- PRODUCT-A LIGHTWEIGHT MIRROR CHECK\n" + "=" * 90)
scaleins_A = canon[canon["action_A"] == "SCALE_IN"].copy()
scaleins_A["side"] = np.sign(scaleins_A["target_exposure_A"])
bpnl_A = canon.set_index("t_idx")["bar_pnl_A_dollars"]
fwd20 = []
for t in scaleins_A["t_idx"]:
    idx = range(t + 1, t + 21)
    vals = bpnl_A.reindex(idx)
    fwd20.append(float(vals.sum()) if vals.notna().any() else np.nan)
scaleins_A["fwd20_pnl"] = fwd20
scaleins_A["post_vol_change"] = scaleins_A["sess_date"].map(vol_change_map)
subA = scaleins_A.dropna(subset=["post_vol_change", "fwd20_pnl"])
subA["short_dummy"] = (subA["side"] == -1).astype(float)
subA["volchg_x_short"] = subA["post_vol_change"] * subA["short_dummy"]
coefA, seA, nA = ols(subA, ["post_vol_change", "short_dummy", "volchg_x_short"], "fwd20_pnl")
for nm, c, s in zip(names, coefA, seA):
    t = c / s if s > 0 else np.nan
    print(f"  {nm}: coef={c:.4f}  se={s:.4f}  t={t:.2f}")
print(f"  n={nA}")

summary = {
    "test2a": {"n_short": len(short_prior_ret), "n_long": len(long_prior_ret),
               "p_neg_given_short": float((short_prior_ret < 0).mean()),
               "p_neg_given_long": float((long_prior_ret < 0).mean())},
    "test2b_productB": {"coef": [float(c) for c in coef], "se": [float(s) for s in se], "n": n_used,
                         "unification_term_t": float(coef[3] / se[3]) if se[3] > 0 else None},
    "test2c_productA": {"coef": [float(c) for c in coefA], "se": [float(s) for s in seA], "n": nA,
                         "unification_term_t": float(coefA[3] / seA[3]) if seA[3] > 0 else None},
}
json.dump(summary, open(os.path.join(OUT, "test2_short_long_unification.json"), "w"), indent=2, default=str)
entries.to_csv(os.path.join(OUT, "productB_entries_with_regime.csv"), index=False)
print("\nLEV01 test 2 complete.")
