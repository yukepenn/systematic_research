"""MOM01 -- intraday momentum (Baltussen et al. JFE 2021) diagnostic on this campaign's own NQ
data. Reads runs/U0_UNIFIED_STATE/out/u0_state_table.parquet only. No new backtest engine, no
new pricing convention -- pure re-expression of already-certified columns."""
import os, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
U0 = os.path.join(ROOT, "runs", "U0_UNIFIED_STATE", "out", "u0_state_table.parquet")
OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

COLS = ["t_idx", "time", "sess_date", "hm", "year", "is_health_only_bar", "open", "close",
        "is_rth", "minutes_since_rth_open", "minutes_to_rth_close", "session_phase",
        "T", "Tp", "HTF_tilt_state", "B", "M", "M_slope_20", "vwap_dist_pts",
        "close_slope_20", "close_slope_20_atr", "ret_1", "ret_5", "ret_20",
        "sigma460_atr_proxy_pts", "position_B", "action_B", "block_id_B",
        "bar_pnl_B_nq_dollars"]

print("loading u0_state_table.parquet ...", flush=True)
df = pd.read_parquet(U0, columns=COLS)
rth = df[df["is_rth"] == True].copy()
print(f"total bars={len(df)}, rth bars={len(rth)}, sessions with is_rth bars={rth['sess_date'].nunique()}")

# ---- STEP 1: per-session price marks ----------------------------------------------------
opens = rth[rth["minutes_since_rth_open"] == 3.0][["sess_date", "open"]].rename(columns={"open": "p_open"})
opens = opens.drop_duplicates("sess_date")

mid = rth[rth["minutes_to_rth_close"] == 30.0][["sess_date", "close", "M", "T", "Tp", "B",
    "HTF_tilt_state", "vwap_dist_pts", "close_slope_20", "close_slope_20_atr", "ret_1", "ret_5",
    "ret_20", "sigma460_atr_proxy_pts", "position_B", "is_health_only_bar", "year"]]
mid = mid.rename(columns={"close": "p_1530"}).drop_duplicates("sess_date")

closep = rth[rth["minutes_to_rth_close"] == 0.0][["sess_date", "close"]].rename(columns={"close": "p_close"})
closep = closep.drop_duplicates("sess_date")

sess = opens.merge(mid, on="sess_date", how="inner").merge(closep, on="sess_date", how="inner")
n_all_sessions = rth["sess_date"].nunique()
print(f"sessions with all 3 marks (open, T-30, close): {len(sess)} of {n_all_sessions} total RTH sessions "
      f"({n_all_sessions - len(sess)} dropped as short/gapped)")

sess["rROD"] = np.log(sess["p_1530"] / sess["p_open"])
sess["rLH"] = np.log(sess["p_close"] / sess["p_1530"])
sess["year"] = sess["year"].astype(int)
sess.to_csv(os.path.join(OUT, "mom01_sessions.csv"), index=False)

canon = sess[sess["is_health_only_bar"] == False].copy()
ext = sess[sess["is_health_only_bar"] == True].copy()
print(f"canonical-window sessions: {len(canon)}, health-only-extension sessions: {len(ext)}")


def ols_1d(x, y):
    x = np.asarray(x, dtype=float); y = np.asarray(y, dtype=float)
    mask = np.isfinite(x) & np.isfinite(y)
    x = x[mask]; y = y[mask]; n = len(x)
    X = np.column_stack([np.ones(n), x])
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    yhat = X @ coef
    resid = y - yhat
    ss_res = np.sum(resid ** 2); ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan
    dof = n - 2
    sigma2 = ss_res / dof if dof > 0 else np.nan
    xc = x - x.mean()
    se_slope = np.sqrt(sigma2 / np.sum(xc ** 2)) if dof > 0 else np.nan
    t_stat = coef[1] / se_slope if se_slope and se_slope > 0 else np.nan
    return {"intercept": coef[0], "slope": coef[1], "t_stat": t_stat, "r2": r2, "n": n}


def ols_multi(df_, xcols, ycol):
    sub = df_.dropna(subset=xcols + [ycol])
    X = sub[xcols].to_numpy(dtype=float)
    X = np.column_stack([np.ones(len(X)), X])
    y = sub[ycol].to_numpy(dtype=float)
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    yhat = X @ coef
    ss_res = np.sum((y - yhat) ** 2); ss_tot = np.sum((y - y.mean()) ** 2)
    return (1 - ss_res / ss_tot if ss_tot > 0 else np.nan), len(sub)


print("\n" + "=" * 90 + "\nSTEP 2: rLH ~ rROD, canonical window\n" + "=" * 90)
r_step2 = ols_1d(canon["rROD"], canon["rLH"])
pearson = float(canon["rROD"].corr(canon["rLH"], method="pearson"))
spearman = float(canon["rROD"].corr(canon["rLH"], method="spearman"))
print(f"n={r_step2['n']}  slope(beta_ROD)={r_step2['slope']:.4f}  t={r_step2['t_stat']:.3f}  "
      f"R^2={r_step2['r2']:.5f}  pearson={pearson:.4f}  spearman={spearman:.4f}")
print("literature cross-check (Baltussen et al. Table B1, NQ): beta_ROD=6.36, t=7.97 (their units; "
      "sign/direction is the load-bearing comparison, not exact magnitude given data/period/frequency differences)")

print("\nyear-by-year (canonical window):")
yby_step2 = []
for yr, g in canon.groupby("year"):
    if len(g) < 20:
        continue
    r = ols_1d(g["rROD"], g["rLH"])
    sp = float(g["rROD"].corr(g["rLH"], method="spearman"))
    yby_step2.append({"year": int(yr), "n": r["n"], "slope": r["slope"], "t_stat": r["t_stat"],
                       "r2": r["r2"], "spearman": sp})
    print(f"  {yr}: n={r['n']:4d}  slope={r['slope']:+.4f}  t={r['t_stat']:+.3f}  "
          f"R^2={r['r2']:.5f}  spearman={sp:+.4f}")

print("\nhealth-only extension (2026-06..2026-07), reported separately, NOT blended:")
r_ext = ols_1d(ext["rROD"], ext["rLH"]) if len(ext) >= 20 else None
if r_ext:
    sp_ext = float(ext["rROD"].corr(ext["rLH"], method="spearman"))
    print(f"  n={r_ext['n']}  slope={r_ext['slope']:+.4f}  t={r_ext['t_stat']:+.3f}  "
          f"R^2={r_ext['r2']:.5f}  spearman={sp_ext:+.4f}")
else:
    print(f"  n={len(ext)} too small / no result")
    sp_ext = None

print("\n" + "=" * 90 + "\nSTEP 3: redundancy of rROD with existing state at the 15:30 bar (canonical window)\n" + "=" * 90)
redund_cols = ["M", "Tp", "T", "B", "HTF_tilt_state", "vwap_dist_pts", "close_slope_20",
               "close_slope_20_atr", "ret_20", "ret_5"]
redund = {}
for c in redund_cols:
    sub = canon.dropna(subset=["rROD", c])
    pear = float(sub["rROD"].corr(sub[c], method="pearson"))
    spear = float(sub["rROD"].corr(sub[c], method="spearman"))
    redund[c] = {"pearson": pear, "spearman": spear, "n": len(sub)}
    print(f"  rROD vs {c:20s}: pearson={pear:+.4f}  spearman={spear:+.4f}  (n={len(sub)})")

print("\n" + "=" * 90 + "\nSTEP 4: forward value of Product B's own last-30-min action (canonical window)\n" + "=" * 90)
# window_pnl_B: sum bar_pnl_B_nq_dollars for bars with 0<=minutes_to_rth_close<=30, per session
win = rth[(rth["minutes_to_rth_close"] >= 0.0) & (rth["minutes_to_rth_close"] <= 30.0)]
window_pnl = win.groupby("sess_date")["bar_pnl_B_nq_dollars"].sum().rename("window_pnl_B")
n_bars_in_window = win.groupby("sess_date").size().rename("n_window_bars")
canon = canon.merge(window_pnl, on="sess_date", how="left").merge(n_bars_in_window, on="sess_date", how="left")
canon["side"] = np.sign(canon["position_B"])
canon["rROD_aligned"] = canon["rROD"] * canon["side"]

print(f"window bar count check (expect 11 per full session: hm 1530,1533,...,1557,1600): "
      f"{canon['n_window_bars'].value_counts().to_dict()}")

full_n = len(canon.dropna(subset=["window_pnl_B"]))
held_n = int((canon["side"] != 0).sum())
print(f"full sample n={full_n}, position_B_1530 != 0 subsample n={held_n}")

for label, sub_base in [("FULL (incl. flat)", canon), ("HELD ONLY (position_B_1530 != 0)", canon[canon["side"] != 0])]:
    sub = sub_base.dropna(subset=["window_pnl_B", "M", "sigma460_atr_proxy_pts", "rROD"])
    if len(sub) < 30:
        print(f"\n{label}: n too small ({len(sub)}), skipping")
        continue
    sub = sub.copy()
    sub["M_abs"] = sub["M"].abs()
    try:
        sub["vol_tercile"] = pd.qcut(sub["sigma460_atr_proxy_pts"], 3, labels=["low", "mid", "high"], duplicates="drop")
        sub["M_tercile"] = pd.qcut(sub["M_abs"], 3, labels=["weak", "mid", "strong"], duplicates="drop")
        sub["bucket"] = sub["M_tercile"].astype(str) + "_" + sub["vol_tercile"].astype(str)
        sub["bucket_mean"] = sub.groupby("bucket")["window_pnl_B"].transform("mean")
        sub["resid_pnl"] = sub["window_pnl_B"] - sub["bucket_mean"]
        sub["vol_z"] = sub["vol_tercile"].cat.codes
    except ValueError:
        sub["resid_pnl"] = sub["window_pnl_B"] - sub["window_pnl_B"].mean()
        sub["vol_z"] = 0.0

    raw_rho = float(sub["rROD"].corr(sub["window_pnl_B"], method="spearman"))
    resid_rho = float(sub["rROD"].corr(sub["resid_pnl"], method="spearman"))
    aligned_raw_rho = float(sub["rROD_aligned"].corr(sub["window_pnl_B"], method="spearman"))
    aligned_resid_rho = float(sub["rROD_aligned"].corr(sub["resid_pnl"], method="spearman"))

    r2_base, n_base = ols_multi(sub, ["M_abs", "vol_z"], "window_pnl_B")
    r2_ext, n_ext = ols_multi(sub, ["M_abs", "vol_z", "rROD"], "window_pnl_B")
    r2_ext_aligned, n_ext_a = ols_multi(sub, ["M_abs", "vol_z", "rROD_aligned"], "window_pnl_B")

    print(f"\n{label} (n={len(sub)}):")
    print(f"  raw Spearman(rROD, window_pnl_B)          = {raw_rho:+.4f}")
    print(f"  residualized Spearman(rROD, resid_pnl)     = {resid_rho:+.4f}")
    print(f"  raw Spearman(rROD_aligned, window_pnl_B)   = {aligned_raw_rho:+.4f}")
    print(f"  residualized Spearman(rROD_aligned, resid) = {aligned_resid_rho:+.4f}")
    print(f"  OLS baseline R^2 (M_abs+vol_z)              = {r2_base:.5f} (n={n_base})")
    print(f"  OLS extended R^2 (+rROD)                    = {r2_ext:.5f}  delta={r2_ext - r2_base:+.5f}")
    print(f"  OLS extended R^2 (+rROD_aligned)             = {r2_ext_aligned:.5f}  delta={r2_ext_aligned - r2_base:+.5f}")

    print("  year-by-year (residualized Spearman, rROD_aligned):")
    yby4 = []
    for yr, g in sub.groupby("year"):
        if len(g) < 20:
            continue
        rho = float(g["rROD_aligned"].corr(g["resid_pnl"], method="spearman"))
        yby4.append({"year": int(yr), "n": len(g), "rho": rho})
        print(f"    {yr}: n={len(g):4d}  rho={rho:+.4f}")

held_sub_for_json = canon[canon["side"] != 0].dropna(subset=["window_pnl_B", "M", "sigma460_atr_proxy_pts", "rROD"])

summary = {
    "step2": {"canonical": r_step2, "pearson": pearson, "spearman": spearman,
              "year_by_year": yby_step2,
              "health_extension": (r_ext | {"spearman": sp_ext}) if r_ext else None},
    "step3_redundancy": redund,
    "n_sessions_total_rth": int(n_all_sessions),
    "n_sessions_with_all_marks": int(len(sess)),
    "n_sessions_canonical": int(len(canon)),
    "n_sessions_health_ext": int(len(ext)),
    "n_sessions_held_at_1530_canonical": int(held_n),
}
with open(os.path.join(OUT, "mom01_summary.json"), "w") as f:
    json.dump(summary, f, indent=2, default=str)

print("\nMOM01 analysis complete.")
