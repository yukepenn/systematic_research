"""VAR01 -- multi-scale realized-variance signature vs Solar13 fast/slow cohort structure.
Frozen spec: runs/VAR01_VARIANCE_SIGNATURE/spec.yaml. Diagnostic only, no policy/exposure rule.
"""
import os, json
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "runs", "VAR01_VARIANCE_SIGNATURE")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)

CERTIFIED_B_NQ_NET = 301915.92

# ------------------------------------------------------------------ load + correctness gate
u0 = pd.read_parquet(os.path.join(ROOT, "runs", "U0_UNIFIED_STATE", "out", "u0_state_table.parquet"))
dev = u0[~u0["is_health_only_bar"]].reset_index(drop=True).copy()
n = len(dev)
assert (np.diff(dev["t_idx"].to_numpy()) == 1).all(), "t_idx not contiguous -- data assumption broken"

gate_net = float(dev["bar_pnl_B_nq_dollars"].sum())
gate_pass = abs(gate_net - CERTIFIED_B_NQ_NET) < 0.01
print(f"[GATE] sum(bar_pnl_B_nq_dollars) = {gate_net:.2f}  (certified {CERTIFIED_B_NQ_NET}) -> "
      f"{'PASS' if gate_pass else 'FAIL'}")
assert gate_pass, "CORRECTNESS GATE FAILED -- stop"

# ------------------------------------------------------------------ horizon-derivation facts (re-verify)
for col in ["fast_member", "slow_member"]:
    s = dev[col].to_numpy()
    chg = np.where(np.diff(s.astype(int)) != 0)[0] + 1
    runlen = np.diff(np.concatenate([[0], chg, [len(s)]]))
    print(f"[DERIVE] {col}: n_changes={len(chg)} median_run_bars={np.median(runlen):.1f} "
          f"mean_run_bars={np.mean(runlen):.2f} (median_min={np.median(runlen)*3:.0f} "
          f"mean_min={np.mean(runlen)*3:.0f})")

SHORT, FAST, SLOW, SESSION = 5, 20, 310, 460

# ------------------------------------------------------------------ returns, overnight flag, r2
close = dev["close"].to_numpy(float)
logc = np.log(close)
r = np.empty(n)
r[0] = np.nan
r[1:] = np.diff(logc)

sess = dev["sess_date"].to_numpy()
first_of_sess = np.zeros(n, dtype=bool)
first_of_sess[0] = True
first_of_sess[1:] = sess[1:] != sess[:-1]
print(f"[OVERNIGHT] {first_of_sess.sum()} first-of-session bars flagged/excluded "
      f"({first_of_sess.sum()/n:.4%} of dev bars)")

r2 = r ** 2
r2[first_of_sess] = np.nan
dev["r2_raw"] = r2

# ------------------------------------------------------------------ causal seasonal deseasonalization
phase = dev["session_phase"].astype(str).to_numpy()
dev["_phase"] = phase
# trailing (expanding, shift1) mean of r2 within each session_phase, in time order
trailing_phase_mean = (
    dev.groupby("_phase")["r2_raw"].apply(lambda s: s.expanding(min_periods=20).mean().shift(1))
)
trailing_phase_mean = trailing_phase_mean.reset_index(level=0, drop=True).sort_index()
trailing_grand_mean = dev["r2_raw"].expanding(min_periods=20).mean().shift(1)

seasonal_mult = (trailing_phase_mean / trailing_grand_mean).to_numpy()
r2_adj = r2 / seasonal_mult
r2_adj[~np.isfinite(r2_adj)] = np.nan
dev["r2_adj"] = r2_adj
print(f"[SEASONAL] usable r2_adj obs: {np.isfinite(r2_adj).sum()} / {n} "
      f"({np.isfinite(r2_adj).sum()/n:.2%})")


def trailing_rv(vals, H, min_frac=0.8):
    s = pd.Series(vals)
    cnt = s.notna().rolling(H, min_periods=1).sum()
    m = s.rolling(H, min_periods=1).mean()
    out = m.to_numpy()
    out[cnt.to_numpy() < min_frac * H] = np.nan
    return out


print("[RV] computing trailing RV at SHORT/FAST/SLOW/SESSION horizons ...")
RV_SHORT = trailing_rv(r2_adj, SHORT)
RV_FAST = trailing_rv(r2_adj, FAST)
RV_SLOW = trailing_rv(r2_adj, SLOW)
RV_SESSION = trailing_rv(r2_adj, SESSION)

with np.errstate(invalid="ignore", divide="ignore"):
    SPREAD_FAST_SLOW = np.log(RV_SLOW) - np.log(RV_FAST)
    SPREAD_SHORT_SESSION = np.log(RV_SESSION) - np.log(RV_SHORT)

dev["RV_SHORT"], dev["RV_FAST"], dev["RV_SLOW"], dev["RV_SESSION"] = RV_SHORT, RV_FAST, RV_SLOW, RV_SESSION
dev["SPREAD_FAST_SLOW"] = SPREAD_FAST_SLOW
dev["SPREAD_SHORT_SESSION"] = SPREAD_SHORT_SESSION

n_valid_spread = np.isfinite(SPREAD_FAST_SLOW).sum()
print(f"[SPREAD] SPREAD_FAST_SLOW valid obs: {n_valid_spread} / {n} ({n_valid_spread/n:.2%})")

results = {"gate_net": gate_net, "gate_pass": gate_pass}

# ------------------------------------------------------------------ persistence tests
print("\n" + "=" * 90 + "\nPERSISTENCE TESTS\n" + "=" * 90)

# daily (session-close snapshot)
last_idx = np.flatnonzero(np.r_[sess[1:] != sess[:-1], True])
daily_spread = pd.Series(SPREAD_FAST_SLOW[last_idx], index=pd.to_datetime(sess[last_idx])).dropna()
daily_ac1 = float(daily_spread.autocorr(lag=1))
print(f"daily session-close SPREAD_FAST_SLOW lag-1 autocorrelation: {daily_ac1:.4f}  (n={len(daily_spread)})")

bar_series = pd.Series(SPREAD_FAST_SLOW)
bar_ac_fast = float(bar_series.autocorr(lag=FAST))
bar_ac_slow = float(bar_series.autocorr(lag=SLOW))
print(f"bar-level SPREAD_FAST_SLOW autocorrelation at lag=FAST({FAST}): {bar_ac_fast:.4f}")
print(f"bar-level SPREAD_FAST_SLOW autocorrelation at lag=SLOW({SLOW}): {bar_ac_slow:.4f}")

results["persistence"] = {
    "daily_lag1_autocorr": daily_ac1, "daily_n": int(len(daily_spread)),
    "bar_lag_fast_autocorr": bar_ac_fast, "bar_lag_slow_autocorr": bar_ac_slow,
}

# ------------------------------------------------------------------ incremental-value tests
print("\n" + "=" * 90 + "\nINCREMENTAL VALUE vs sigma460 (bucket-residualize + Delta-R^2)\n" + "=" * 90)

sig460 = dev["sigma460_atr_proxy_pts"].to_numpy(float)
bpnl = dev["bar_pnl_B_nq_dollars"].to_numpy(float)
year_arr = dev["year"].to_numpy()


def forward_sum(vals, H):
    """forward sum over (t, t+H] -- causal-safe use (target only, never a feature)."""
    s = pd.Series(vals)
    fwd = s.shift(-1).rolling(H, min_periods=H).sum().shift(-(H - 1))
    return fwd.to_numpy()


incremental_rows = []
for H, hlabel in [(FAST, "FAST_20bar_1hr"), (SESSION, "SESSION_460bar_1session")]:
    fwd = forward_sum(bpnl, H)
    # non-overlapping subsample: every H-th bar index
    sel = np.arange(0, n, H)
    d = pd.DataFrame({
        "t_idx": sel, "fwd_pnl": fwd[sel], "sigma460": sig460[sel],
        "spread": SPREAD_FAST_SLOW[sel], "year": year_arr[sel],
    }).dropna(subset=["fwd_pnl", "sigma460", "spread"])
    print(f"\n--- horizon {hlabel}: non-overlapping n={len(d)} "
          f"({d['t_idx'].min()}..{d['t_idx'].max()}) ---")

    d["sigma_tercile"] = pd.qcut(d["sigma460"], 3, labels=["low", "mid", "high"], duplicates="drop")
    d["spread_z"] = (d["spread"] - d["spread"].mean()) / d["spread"].std(ddof=1)

    dum = pd.get_dummies(d["sigma_tercile"], prefix="sig", drop_first=True).astype(float)
    Xb = sm.add_constant(dum.to_numpy())
    yb = d["fwd_pnl"].to_numpy(float)
    res_base = sm.OLS(yb, Xb).fit(cov_type="HAC", cov_kwds={"maxlags": max(5, H // 4)})
    r2_base = res_base.rsquared

    Xe = np.column_stack([Xb, d["spread_z"].to_numpy(float)])
    res_ext = sm.OLS(yb, Xe).fit(cov_type="HAC", cov_kwds={"maxlags": max(5, H // 4)})
    r2_ext = res_ext.rsquared
    spread_coef = float(res_ext.params[-1])
    spread_t = float(res_ext.tvalues[-1])
    d_r2 = r2_ext - r2_base

    print(f"R^2 base (sigma460 tercile only) = {r2_base:.6f}")
    print(f"R^2 ext  (+ SPREAD_FAST_SLOW)    = {r2_ext:.6f}   Delta-R^2 = {d_r2:+.6f}")
    print(f"spread coef = {spread_coef:+.4f}  HAC t = {spread_t:+.3f}")

    # bucket-residualized Spearman
    d["bucket_mean"] = d.groupby("sigma_tercile", observed=True)["fwd_pnl"].transform("mean")
    d["resid_pnl"] = d["fwd_pnl"] - d["bucket_mean"]
    rho = float(d["spread"].corr(d["resid_pnl"], method="spearman"))
    print(f"bucket-residualized Spearman(spread, resid_fwd_pnl | sigma460 tercile) = {rho:.4f}")

    # year-by-year stability
    yby = []
    for yr, g in d.dropna(subset=["resid_pnl"]).groupby("year"):
        if len(g) < 20:
            continue
        rho_yr = float(g["spread"].corr(g["resid_pnl"], method="spearman"))
        yby.append({"year": int(yr), "n": len(g), "spearman_resid": rho_yr})
    yby_df = pd.DataFrame(yby)
    same_sign = int((np.sign(yby_df["spearman_resid"]) == np.sign(rho)).sum()) if len(yby_df) else 0
    print(yby_df.round(4).to_string(index=False) if len(yby_df) else "  (no year groups)")
    print(f"years same-sign as pooled: {same_sign}/{len(yby_df)}")

    d.to_csv(os.path.join(OUT, f"var01_bar_features_{hlabel}.csv"), index=False)
    yby_df.to_csv(os.path.join(OUT, f"var01_year_by_year_{hlabel}.csv"), index=False)

    incremental_rows.append({
        "horizon": hlabel, "H_bars": H, "n": len(d),
        "r2_base": r2_base, "r2_ext": r2_ext, "delta_r2": d_r2,
        "spread_coef": spread_coef, "spread_t_hac": spread_t,
        "resid_spearman": rho, "years_same_sign": same_sign, "years_total": len(yby_df),
    })

inc_df = pd.DataFrame(incremental_rows)
inc_df.to_csv(os.path.join(OUT, "var01_incremental_summary.csv"), index=False)
results["incremental"] = incremental_rows

# ------------------------------------------------------------------ secondary spread robustness (light touch)
print("\n" + "=" * 90 + "\nSECONDARY SPREAD (SHORT/SESSION anchor pair) -- robustness only\n" + "=" * 90)
sec_rows = []
for H, hlabel in [(FAST, "FAST_20bar_1hr"), (SESSION, "SESSION_460bar_1session")]:
    fwd = forward_sum(bpnl, H)
    sel = np.arange(0, n, H)
    d = pd.DataFrame({
        "fwd_pnl": fwd[sel], "sigma460": sig460[sel], "spread2": SPREAD_SHORT_SESSION[sel],
    }).dropna()
    d["sigma_tercile"] = pd.qcut(d["sigma460"], 3, labels=["low", "mid", "high"], duplicates="drop")
    d["bucket_mean"] = d.groupby("sigma_tercile", observed=True)["fwd_pnl"].transform("mean")
    d["resid_pnl"] = d["fwd_pnl"] - d["bucket_mean"]
    rho2 = float(d["spread2"].corr(d["resid_pnl"], method="spearman"))
    print(f"{hlabel}: bucket-residualized Spearman(SPREAD_SHORT_SESSION, resid) = {rho2:.4f}  (n={len(d)})")
    sec_rows.append({"horizon": hlabel, "n": len(d), "resid_spearman_secondary": rho2})
pd.DataFrame(sec_rows).to_csv(os.path.join(OUT, "var01_secondary_spread_summary.csv"), index=False)
results["secondary_spread"] = sec_rows

with open(os.path.join(OUT, "var01_results.json"), "w") as f:
    json.dump(results, f, indent=2, default=str)

print("\nVAR01 step2-3 analysis complete.")
