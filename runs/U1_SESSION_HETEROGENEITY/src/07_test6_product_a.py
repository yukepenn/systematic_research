"""U1 test 6 -- lightest version of tests 1-3 for Product A's ENTRY (trip-level net_pnl) and
SCALE_IN (forward-1/5-bar proxy) action states, by session_phase/is_rth. Canonical window only."""
import os, json
import numpy as np, pandas as pd

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
PHASE_ORDER = ["ETH_ASIA", "ETH_EUROPE", "US_PREMARKET", "RTH_OPEN", "RTH_MID", "RTH_CLOSE", "POST_RTH"]

entry_A = pd.read_csv(os.path.join(OUT, "block_entry_A.csv"))
scalein_A = pd.read_csv(os.path.join(OUT, "scalein_fwd_A.csv"))
entry_A_c = entry_A[~entry_A["is_health_only_bar"]].copy()
scalein_A_c = scalein_A[~scalein_A["is_health_only_bar"]].copy()

print("=" * 100)
print("TEST 6a -- Product A ENTRY (trip-level net_pnl) by session_phase / RTH-ETH")
print("=" * 100)
g1 = entry_A_c.groupby("session_phase", observed=True).agg(
    n=("net_pnl", "size"), mean_pnl=("net_pnl", "mean"), sum_pnl=("net_pnl", "sum"),
    win_rate=("net_pnl", lambda x: float((x > 0).mean()))).reindex(PHASE_ORDER)
print(g1.round(2).to_string())
g1.to_csv(os.path.join(OUT, "t6a_entry_A_by_phase.csv"))
g1b = entry_A_c.groupby("is_rth").agg(
    n=("net_pnl", "size"), mean_pnl=("net_pnl", "mean"), sum_pnl=("net_pnl", "sum"))
print("\nby RTH vs ETH:")
print(g1b.round(2).to_string())
g1b.to_csv(os.path.join(OUT, "t6a_entry_A_by_rth.csv"))

print("\n" + "=" * 100)
print("TEST 6b -- Product A SCALE_IN forward-1/5-bar continuation value by session_phase / RTH-ETH")
print("=" * 100)
g2 = scalein_A_c.groupby("session_phase", observed=True).agg(
    n=("forward1_pnl", "size"),
    mean_fwd1=("forward1_pnl", "mean"), mean_fwd5=("forward5_pnl", "mean"),
    sum_fwd5=("forward5_pnl", "sum")).reindex(PHASE_ORDER)
print(g2.round(3).to_string())
g2.to_csv(os.path.join(OUT, "t6b_scalein_A_by_phase.csv"))
g2b = scalein_A_c.groupby("is_rth").agg(
    n=("forward1_pnl", "size"),
    mean_fwd1=("forward1_pnl", "mean"), mean_fwd5=("forward5_pnl", "mean"),
    sum_fwd5=("forward5_pnl", "sum"))
print("\nby RTH vs ETH:")
print(g2b.round(3).to_string())
g2b.to_csv(os.path.join(OUT, "t6b_scalein_A_by_rth.csv"))

print("\n" + "=" * 100)
print("TEST 6c -- interaction OLS (lightest version): net_pnl ~ M_abs + vol_tercile_code + is_rth")
print("+ M_abs:is_rth  (Product A ENTRY, M_abs = |M_A_raw| at entry, Product A's own raw score)")
print("=" * 100)
sub = entry_A_c.dropna(subset=["M_abs", "vol_tercile", "is_rth", "net_pnl"]).copy()
sub["vol_z"] = pd.Categorical(sub["vol_tercile"], categories=["low", "mid", "high"]).codes.astype(float)
sub["is_rth_num"] = sub["is_rth"].astype(float)
X = sub[["M_abs", "vol_z", "is_rth_num"]].to_numpy(dtype=float)
inter = sub["M_abs"].to_numpy() * sub["is_rth_num"].to_numpy()
X_full = np.column_stack([X, inter])
y = sub["net_pnl"].to_numpy(dtype=float)


def ols_fit(Xc, yc):
    X1 = np.column_stack([np.ones(len(Xc)), Xc])
    coef, *_ = np.linalg.lstsq(X1, yc, rcond=None)
    yhat = X1 @ coef
    ss_res = np.sum((yc - yhat) ** 2); ss_tot = np.sum((yc - yc.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan
    n, k = X1.shape
    dof = max(n - k, 1)
    sigma2 = ss_res / dof
    try:
        se = np.sqrt(np.diag(sigma2 * np.linalg.inv(X1.T @ X1)))
    except np.linalg.LinAlgError:
        se = np.full(k, np.nan)
    return coef, se, r2, n


coef, se, r2, n = ols_fit(X_full, y)
names = ["intercept", "M_abs", "vol_tercile_code", "is_rth", "M_abs:is_rth"]
print(f"n={n}  R^2={r2:.5f}")
for nm, c, s in zip(names, coef, se):
    t = c / s if s and s > 0 else np.nan
    print(f"  {nm:20s} coef={c:10.3f}  se={s:9.3f}  t={t:7.2f}")
result_ols = {"n": int(n), "r2": float(r2), "coef": {nm: float(c) for nm, c in zip(names, coef)},
              "se": {nm: float(s) for nm, s in zip(names, se)}}

print("\n" + "=" * 100)
print("TEST 6d -- residualized RTH vs ETH within M-strength x vol buckets (Product A ENTRY)")
print("=" * 100)
entry_A_c["bucket"] = entry_A_c["M_strength_tercile"].astype(str) + "_" + entry_A_c["vol_tercile"].astype(str)
entry_A_c["bucket_mean_pnl"] = entry_A_c.groupby("bucket")["net_pnl"].transform("mean")
entry_A_c["resid_pnl"] = entry_A_c["net_pnl"] - entry_A_c["bucket_mean_pnl"]
MIN_RELIABLE_N = 15
rows = []
for bucket, g in entry_A_c.groupby("bucket", observed=True):
    row = {"bucket": bucket, "bucket_n": len(g)}
    for label, mask in [("RTH", g["is_rth"]), ("ETH", ~g["is_rth"])]:
        sub_g = g[mask]
        row[f"{label}_n"] = len(sub_g)
        row[f"{label}_mean_resid"] = float(sub_g["resid_pnl"].mean()) if len(sub_g) else np.nan
        row[f"{label}_reliable"] = bool(len(sub_g) >= MIN_RELIABLE_N)
    rows.append(row)
tbl = pd.DataFrame(rows).sort_values("bucket")
print(tbl.round(2).to_string(index=False))
tbl.to_csv(os.path.join(OUT, "t6d_residual_bucket_A.csv"), index=False)
n_sparse = int((~tbl["RTH_reliable"] | ~tbl["ETH_reliable"]).sum())
print(f"\n{n_sparse}/{len(tbl)} buckets have at least one side with n<{MIN_RELIABLE_N} -- flagged, not reliable.")
print("note: Product-A M_A_raw is near-discrete, 90.2% of ENTRY events at |M_A_raw|=1 (see "
      "01_build_tables.py comment) -- fixed cutoffs used for M_strength_tercile instead of qcut, "
      "so 'weak' dominates by construction; this is disclosed, not a qcut artifact.")

print("\n" + "=" * 100)
print("TEST 6e -- right-tail check: top-20 all-time winning Product-A trips, session_phase/RTH-ETH")
print("=" * 100)
top20_A = entry_A_c.sort_values("net_pnl", ascending=False).head(20)
print(top20_A[["t_idx", "sess_date", "side", "M_abs", "vol_tercile", "session_phase", "is_rth", "net_pnl"]]
      .round(2).to_string(index=False))
top20_A.to_csv(os.path.join(OUT, "t6e_top20_winners_A.csv"), index=False)
n_rth_top = int(top20_A["is_rth"].sum())
base_rth_A = float(entry_A_c["is_rth"].mean())
print(f"\ntop-20 Product-A winners: {n_rth_top}/20 RTH  (base rate {base_rth_A:.1%} RTH)")

summary = {
    "entry_A_ols": result_ols,
    "top20_A_n_rth": n_rth_top, "base_rate_rth_A": base_rth_A,
    "n_sparse_buckets_6d": n_sparse, "n_buckets_total_6d": int(len(tbl)),
}
json.dump(summary, open(os.path.join(OUT, "t6_summary.json"), "w"), indent=2)
print("\ntest6 complete.")
