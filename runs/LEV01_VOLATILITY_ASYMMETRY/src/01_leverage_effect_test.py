"""LEV01 step 1 -- does NQ's own realized volatility (sigma460_atr_proxy_pts) exhibit the
classic finance-literature leverage effect (asymmetric response to negative vs positive
returns)? Session-level test, Engle-Ng-style sign-asymmetry regression: forward vol CHANGE
regressed on signed trailing return + an interaction with a negative-return dummy. A
significantly negative interaction coefficient is the standard leverage-effect signature
(negative returns provoke a LARGER vol response than positive returns of the same magnitude).
"""
import os, sys, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

u0 = pd.read_parquet(os.path.join(ROOT, "runs", "U0_UNIFIED_STATE", "out", "u0_state_table.parquet"),
                      columns=["t_idx", "sess_date", "close", "sigma460_atr_proxy_pts", "year",
                               "is_health_only_bar", "is_rth"])
u0["sess_date"] = pd.to_datetime(u0["sess_date"])

# session-level series: last bar's close and sigma460 (as-of session close), canonical window only
canon = u0[~u0["is_health_only_bar"]].copy()
sess = canon.groupby("sess_date").agg(close=("close", "last"), sigma460=("sigma460_atr_proxy_pts", "last"),
                                       year=("year", "last")).reset_index().sort_values("sess_date").reset_index(drop=True)
n = len(sess)
print(f"[LEV01] {n} canonical sessions, {sess['sess_date'].min().date()} .. {sess['sess_date'].max().date()}", flush=True)

close = sess["close"].to_numpy()
sigma = sess["sigma460"].to_numpy()
session_ret_pts = np.r_[np.nan, np.diff(close)]
session_ret_atr = session_ret_pts / sigma  # normalized by that session's own vol level (causal, trailing)

FWD_K = 5  # forward-looking window in sessions, economically motivated (~1 trading week)
fwd_vol = pd.Series(sigma).shift(-FWD_K).rolling(FWD_K, min_periods=FWD_K).mean().to_numpy()
# fwd_vol[s] = mean sigma460 over sessions s+1..s+FWD_K (forward, causal-consistent labeling: this
# is a DESCRIPTIVE label using future vol, standard practice in this campaign for diagnostic
# labeling, e.g. R1's giveback labels -- not a lookahead bug in a trading rule since none is built)
vol_change = fwd_vol - sigma

sess["session_ret_atr"] = session_ret_atr
sess["vol_change"] = vol_change
sess["neg_dummy"] = (sess["session_ret_atr"] < 0).astype(float)
sess["ret_x_neg"] = sess["session_ret_atr"] * sess["neg_dummy"]

sub = sess.dropna(subset=["session_ret_atr", "vol_change"])
print(f"[LEV01] {len(sub)} sessions usable after forward/backward window trim", flush=True)


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
    ss_res = np.sum(resid ** 2); ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan
    return coef, se, r2, len(d)


print("\n" + "=" * 90 + "\nTEST 1 -- LEVERAGE-EFFECT ASYMMETRY (Engle-Ng-style sign regression)\n" + "=" * 90)
coef, se, r2, n_used = ols(sub, ["session_ret_atr", "ret_x_neg"], "vol_change")
names = ["intercept", "session_ret_atr", "ret_x_neg (asymmetry term)"]
for nm, c, s in zip(names, coef, se):
    t = c / s if s > 0 else np.nan
    print(f"  {nm}: coef={c:.4f}  se={s:.4f}  t={t:.2f}")
print(f"  R^2={r2:.5f}  n={n_used}")
print("\nInterpretation: a NEGATIVE 'ret_x_neg' coefficient means forward volatility responds "
      "MORE (increases more, or falls less) after a negative return than a positive return of "
      "equal magnitude -- the classic leverage-effect signature.")

print("\n" + "=" * 90 + "\nSIMPLE SPLIT CHECK (non-parametric corroboration)\n" + "=" * 90)
pos = sub[sub["session_ret_atr"] > 0]
neg = sub[sub["session_ret_atr"] < 0]
print(f"positive-return sessions (n={len(pos)}): mean vol_change = {pos['vol_change'].mean():.4f}")
print(f"negative-return sessions (n={len(neg)}): mean vol_change = {neg['vol_change'].mean():.4f}")
print(f"mean |session_ret_atr| pos={pos['session_ret_atr'].mean():.4f} "
      f"neg={neg['session_ret_atr'].mean():.4f}  (should be roughly symmetric in magnitude)")

print("\n" + "=" * 90 + "\nYEAR-BY-YEAR STABILITY of the asymmetry term\n" + "=" * 90)
yby = []
for yr, g in sub.groupby("year"):
    if len(g) < 30:
        yby.append({"year": int(yr), "n": len(g), "coef": np.nan, "t": np.nan})
        continue
    c, s, r2_yr, n_yr = ols(g, ["session_ret_atr", "ret_x_neg"], "vol_change")
    t_yr = c[2] / s[2] if s[2] > 0 else np.nan
    yby.append({"year": int(yr), "n": n_yr, "coef": float(c[2]), "t": float(t_yr)})
yby_df = pd.DataFrame(yby)
print(yby_df.round(4).to_string(index=False))

summary = {
    "n_sessions": n, "n_used_test1": n_used,
    "asymmetry_coef": float(coef[2]), "asymmetry_se": float(se[2]),
    "asymmetry_t": float(coef[2] / se[2]) if se[2] > 0 else None,
    "r2": float(r2),
    "split_check": {"pos_mean_vol_change": float(pos["vol_change"].mean()),
                     "neg_mean_vol_change": float(neg["vol_change"].mean()),
                     "n_pos": len(pos), "n_neg": len(neg)},
    "year_by_year": yby_df.to_dict("records"),
}
json.dump(summary, open(os.path.join(OUT, "test1_leverage_effect.json"), "w"), indent=2, default=str)
sess.to_csv(os.path.join(OUT, "session_series.csv"), index=False)
print("\nLEV01 test 1 complete.")
