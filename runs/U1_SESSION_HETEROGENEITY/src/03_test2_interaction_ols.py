"""U1 test 2 -- interpretable OLS interaction tests (np.linalg.lstsq, matching R4/R5's pattern,
no black-box model). Product-B ENTRY table, canonical window only."""
import os, json
import numpy as np, pandas as pd

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
PHASE_ORDER = ["ETH_ASIA", "ETH_EUROPE", "US_PREMARKET", "RTH_OPEN", "RTH_MID", "RTH_CLOSE", "POST_RTH"]

entry_B = pd.read_csv(os.path.join(OUT, "block_entry_B.csv"))
entry_B = entry_B[(~entry_B["is_health_only_bar"]) & (entry_B["action_B"] == "ENTRY")].copy()
entry_B["vol_z"] = pd.Categorical(entry_B["vol_tercile"], categories=["low", "mid", "high"]).codes.astype(float)
entry_B["is_rth_num"] = entry_B["is_rth"].astype(float)
n_total = len(entry_B)


def ols_fit(X, y):
    X1 = np.column_stack([np.ones(len(X)), X])
    coef, *_ = np.linalg.lstsq(X1, y, rcond=None)
    yhat = X1 @ coef
    resid = y - yhat
    ss_res = np.sum(resid ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan
    # simple coefficient standard errors (homoskedastic OLS), for a sense of significance only
    n, k = X1.shape
    dof = max(n - k, 1)
    sigma2 = ss_res / dof
    try:
        XtX_inv = np.linalg.inv(X1.T @ X1)
        se = np.sqrt(np.diag(sigma2 * XtX_inv))
    except np.linalg.LinAlgError:
        se = np.full(k, np.nan)
    return coef, se, r2, n


print("=" * 100)
print("TEST 2a -- net_pnl ~ M_abs + vol_tercile_code + is_rth + M_abs:is_rth  (Product B ENTRY)")
print("=" * 100)
sub = entry_B.dropna(subset=["M_abs", "vol_z", "is_rth_num", "net_pnl"])
X = sub[["M_abs", "vol_z", "is_rth_num"]].to_numpy(dtype=float)
inter = sub["M_abs"].to_numpy() * sub["is_rth_num"].to_numpy()
X_full = np.column_stack([X, inter])
y = sub["net_pnl"].to_numpy(dtype=float)
coef, se, r2, n = ols_fit(X_full, y)
names = ["intercept", "M_abs", "vol_tercile_code", "is_rth", "M_abs:is_rth"]
print(f"n={n}  R^2={r2:.5f}")
for nm, c, s in zip(names, coef, se):
    tstat = c / s if s and s > 0 else np.nan
    print(f"  {nm:20s} coef={c:10.3f}  se={s:9.3f}  t={tstat:7.2f}")

# baseline (no interaction) for delta-R^2
coef0, se0, r2_0, n0 = ols_fit(X, y)
print(f"\nbaseline (no interaction) R^2={r2_0:.5f}  ->  with interaction R^2={r2:.5f}  "
      f"(delta R^2 = {r2 - r2_0:+.5f})")

interaction_coef = float(coef[-1])
# implied effect size: predicted M_abs-net_pnl slope in ETH vs RTH
slope_eth = float(coef[1])          # M_abs main effect (is_rth=0 -> ETH)
slope_rth = float(coef[1] + coef[-1])
print(f"\nimplied M_abs slope in ETH: {slope_eth:.2f} $/unit-M   "
      f"implied M_abs slope in RTH: {slope_rth:.2f} $/unit-M   (difference = interaction coef = {interaction_coef:.2f})")

result_2a = {
    "n": int(n), "r2": float(r2), "r2_baseline_no_interaction": float(r2_0),
    "delta_r2": float(r2 - r2_0),
    "coef": {nm: float(c) for nm, c in zip(names, coef)},
    "se": {nm: float(s) for nm, s in zip(names, se)},
    "slope_eth": slope_eth, "slope_rth": slope_rth,
}

print("\n" + "=" * 100)
print("TEST 2b -- net_pnl ~ M_abs + vol_tercile_code + C(session_phase) + M_abs:C(session_phase)")
print("(manual dummy encoding, baseline phase = ETH_ASIA -- largest ETH bucket)")
print("=" * 100)
sub2 = entry_B.dropna(subset=["M_abs", "vol_z", "session_phase", "net_pnl"]).copy()
baseline_phase = "ETH_ASIA"
dummy_phases = [p for p in PHASE_ORDER if p != baseline_phase and p in sub2["session_phase"].unique()]
X_cols = [sub2["M_abs"].to_numpy(dtype=float), sub2["vol_z"].to_numpy(dtype=float)]
col_names = ["M_abs", "vol_tercile_code"]
for p in dummy_phases:
    d = (sub2["session_phase"] == p).astype(float).to_numpy()
    X_cols.append(d)
    col_names.append(f"phase[{p}]")
for p in dummy_phases:
    d = (sub2["session_phase"] == p).astype(float).to_numpy()
    inter_p = sub2["M_abs"].to_numpy(dtype=float) * d
    X_cols.append(inter_p)
    col_names.append(f"M_abs:phase[{p}]")
X2 = np.column_stack(X_cols)
y2 = sub2["net_pnl"].to_numpy(dtype=float)
coef2, se2, r2b, n2 = ols_fit(X2, y2)
full_names = ["intercept"] + col_names
print(f"n={n2}  R^2={r2b:.5f}  (baseline phase = {baseline_phase})")
for nm, c, s in zip(full_names, coef2, se2):
    tstat = c / s if s and s > 0 else np.nan
    flag = "  <-- interaction" if nm.startswith("M_abs:phase") else ""
    print(f"  {nm:24s} coef={c:10.3f}  se={s:9.3f}  t={tstat:7.2f}{flag}")

# baseline w/o phase interactions (phase main effects only) for delta-R^2
X2_noint = np.column_stack([sub2["M_abs"].to_numpy(dtype=float), sub2["vol_z"].to_numpy(dtype=float)] +
                            [(sub2["session_phase"] == p).astype(float).to_numpy() for p in dummy_phases])
coef2b, se2b, r2b_noint, n2b = ols_fit(X2_noint, y2)
print(f"\nphase main-effects-only R^2={r2b_noint:.5f}  ->  with M_abs:phase interactions R^2={r2b:.5f}  "
      f"(delta R^2 = {r2b - r2b_noint:+.5f})")

result_2b = {
    "n": int(n2), "r2": float(r2b), "r2_phase_main_effects_only": float(r2b_noint),
    "delta_r2": float(r2b - r2b_noint), "baseline_phase": baseline_phase,
    "coef": {nm: float(c) for nm, c in zip(full_names, coef2)},
    "se": {nm: float(s) for nm, s in zip(full_names, se2)},
}

json.dump({"test2a_is_rth_interaction": result_2a, "test2b_session_phase_interaction": result_2b},
          open(os.path.join(OUT, "t2_interaction_ols.json"), "w"), indent=2)
print("\ntest2 complete.")
