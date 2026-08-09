"""S2_SELTIME — Arm A: fixed broad-time NEW-ENTRY eligibility, EUROPE_PREUS (02:00-08:00 ET).
Frozen spec.yaml, committed 3c6f6cd, BEFORE this code was written.
"""
import os, sys, json, datetime as dt
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "runs", "W18R1_M1_VOLSEASON", "src"))
import sm01_solarsim as sm
from smv2_common import dd_battery
import common as C1

RUN = os.path.join(ROOT, "runs", "S2_SELTIME")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
DEV_END = dt.date(2026, 5, 29)
SEED, BLOCK, NBOOT = 20260809, 5, 10000


def since_1800_hours(bars):
    t = pd.to_datetime(bars["time"])
    hh = t.dt.hour.to_numpy() + t.dt.minute.to_numpy() / 60.0
    return (hh - 18.0) % 24.0


def apply_entry_eligibility(T, blocked_mask):
    """Sequential rule (spec §1): suppress NEW directional commitments (flat->nonzero or a
    flip) while `blocked_mask[t]` is True, relative to the MODIFIED prior position. Exits and
    same-direction continuation always pass through unchanged, in or out of the window."""
    n = len(T)
    Tp = np.empty(n, dtype=int)
    prev = 0
    for t in range(n):
        cur = int(T[t])
        is_new_commitment = (cur != 0) and (
            (prev == 0) or (np.sign(cur) != np.sign(prev))
        )
        if is_new_commitment and blocked_mask[t]:
            Tp[t] = 0
        else:
            Tp[t] = cur
        prev = Tp[t]
    return Tp


def battery(x):
    eqd = np.cumsum(x); dd = np.maximum.accumulate(eqd) - eqd
    k = max(1, int(0.05 * len(x)))
    sd = x.std(ddof=1)
    return {"n_days": len(x), "net": float(x.sum()),
            "sharpe": float(x.mean() / sd * np.sqrt(252)) if sd > 0 and len(x) > 1 else np.nan,
            "CDaR_0.95": float(np.sort(dd)[::-1][:k].mean()) if len(dd) else 0.0, "k": k}


def path_stats(x, idx, k5, chunk=2000):
    shp = np.empty(len(idx)); cdr = np.empty(len(idx))
    for i in range(0, len(idx), chunk):
        X = x[idx[i:i + chunk]]
        mu = X.mean(axis=1); sd = X.std(axis=1, ddof=1)
        shp[i:i + chunk] = mu / sd * np.sqrt(252)
        eq = np.cumsum(X, axis=1)
        dd = np.maximum.accumulate(eq, axis=1) - eq
        cdr[i:i + chunk] = (-np.partition(-dd, k5 - 1, axis=1)[:, :k5]).mean(axis=1)
    return shp, cdr


def block_bootstrap_idx(n, block, nboot, seed):
    nb = int(np.ceil(n / block))
    rng = np.random.default_rng(seed)
    starts = rng.integers(0, n, size=(nboot, nb))
    return ((starts[:, :, None] + np.arange(block)[None, None, :]) % n).reshape(nboot, -1)[:, :n]


def top10_retention(ctrl, arm):
    idx_c = np.argsort(ctrl)[-10:]
    house = float(arm[idx_c].sum() / ctrl[idx_c].sum()) if ctrl[idx_c].sum() != 0 else np.nan
    idx_a = np.argsort(arm)[-10:]
    own = float(arm[idx_a].sum() / ctrl[idx_a].sum()) if ctrl[idx_a].sum() != 0 else np.nan
    return house, own


# ============================================================== control
bars = C1.load_dev_bars()
n = len(bars)
sess = bars["sess_date"].to_numpy()
close = bars["close"].to_numpy()
sig460 = sm.sigma_series(close)
T = sm.e10_target(C1.build_pend(bars, sig460))
daily_ctrl, barpos_ctrl, barpnl_ctrl = C1.e10_exec(bars, T)

ref_path = os.path.join(ROOT, "runs", "SMV2AD_VOLMULT_CEILING", "out", "e10_daily_dev_control_1200.csv")
ref = pd.read_csv(ref_path); ref["sess"] = pd.to_datetime(ref["sess"]).dt.date.astype(str)
mine = daily_ctrl.copy(); mine["sess"] = mine["sess"].astype(str)
mrg = mine.merge(ref, on="sess", suffixes=("", "_ref"))
crosscheck = {"n_matched": int(len(mrg)), "PASS": bool(len(mrg) == len(mine) == len(ref) and
              (mrg["net"] - mrg["net_ref"]).abs().max() < 0.01)}
print("=== CONTROL CROSSCHECK ===\n" + json.dumps(crosscheck, indent=2), flush=True)
assert crosscheck["PASS"]
daily_ctrl.to_csv(os.path.join(OUT, "daily_control.csv"), index=False)

# ============================================================== Arm A (decision cell)
since = since_1800_hours(bars)
blocked = (since >= 8.0) & (since < 14.0)   # 02:00-08:00 ET == hours 8..14 since 18:00
T_A = apply_entry_eligibility(T, blocked)
daily_A, barpos_A, barpnl_A = C1.e10_exec(bars, T_A)
daily_A.to_csv(os.path.join(OUT, "daily_armA.csv"), index=False)

CAL = daily_ctrl.set_index(daily_ctrl["sess"].astype(str)).index
ctrl_s = daily_ctrl.set_index(daily_ctrl["sess"].astype(str))["net"]
armA_s = daily_A.set_index(daily_A["sess"].astype(str))["net"].reindex(CAL)

# ============================================================== gate 0 disclosure
exp_ratio = float(np.abs(T_A).sum() / np.abs(T).sum())
contracts_ratio = float(daily_A["contracts"].mean() / daily_ctrl["contracts"].mean())
n_suppressed_bars = int((T_A != T).sum())
exposure_disclosure = pd.DataFrame([{
    "sum_absT_ratio": exp_ratio, "contracts_per_day_ratio": contracts_ratio,
    "n_bars_modified": n_suppressed_bars, "pct_bars_modified": n_suppressed_bars / n * 100,
}])
exposure_disclosure.to_csv(os.path.join(OUT, "exposure_disclosure.csv"), index=False)
print("\n=== GATE 0 DISCLOSURE (not invalidation for an eligibility rule) ===")
print(exposure_disclosure.to_string(index=False), flush=True)

# ============================================================== gate A legacy triple
bc = battery(ctrl_s.to_numpy()); ba = battery(armA_s.to_numpy())
house_ret, own_ret = top10_retention(ctrl_s.to_numpy(), armA_s.to_numpy())
g_sharpe = bool(ba["sharpe"] > bc["sharpe"])
g_cdar = bool(ba["CDaR_0.95"] < bc["CDaR_0.95"])
g_top10 = bool(house_ret >= 0.95)
gate_A = {"sharpe_control": bc["sharpe"], "sharpe_arm": ba["sharpe"], "d_sharpe": ba["sharpe"] - bc["sharpe"],
          "CDaR_control": bc["CDaR_0.95"], "CDaR_arm": ba["CDaR_0.95"],
          "d_CDaR_pos_is_better": bc["CDaR_0.95"] - ba["CDaR_0.95"],
          "net_control": bc["net"], "net_arm": ba["net"],
          "top10_house": house_ret, "top10_own": own_ret,
          "gate_sharpe": g_sharpe, "gate_CDaR": g_cdar, "gate_top10": g_top10,
          "GATE_A_PASS": bool(g_sharpe and g_cdar and g_top10)}
print("\n=== GATE A ===\n" + json.dumps(gate_A, indent=2), flush=True)

# ============================================================== gate B chronology
df_y = pd.DataFrame({"c": ctrl_s, "a": armA_s}); df_y.index = pd.to_datetime(df_y.index)
df_y["year"] = df_y.index.year
yrows = []
for y, g in df_y.groupby("year"):
    bcy = battery(g["c"].to_numpy()); bay = battery(g["a"].to_numpy())
    yrows.append({"year": int(y), "n_days": len(g), "sharpe_control": bcy["sharpe"],
                  "sharpe_arm": bay["sharpe"], "d_sharpe": bay["sharpe"] - bcy["sharpe"],
                  "sign_positive": bool(bay["sharpe"] - bcy["sharpe"] > 0)})
yearly = pd.DataFrame(yrows)
yearly.to_csv(os.path.join(OUT, "yearly.csv"), index=False)
agree = int(yearly["sign_positive"].sum()); total = len(yearly)
cal_sorted = sorted(CAL); trimmed_cal = cal_sorted[:-106]
bc_t = battery(ctrl_s.reindex(trimmed_cal).to_numpy()); ba_t = battery(armA_s.reindex(trimmed_cal).to_numpy())
survives_trim = bool(ba_t["sharpe"] > bc_t["sharpe"] and ba_t["CDaR_0.95"] < bc_t["CDaR_0.95"])
gate_B = {"yearly_sign_agree": agree, "yearly_total": total, "bar_4of5": bool(agree >= 4),
          "survives_excising_final_106": survives_trim,
          "GATE_B_PASS": bool(agree >= 4 and survives_trim)}
print("\n=== GATE B ===\n" + json.dumps(gate_B, indent=2), flush=True)
print(yearly.to_string(index=False), flush=True)

# ============================================================== gate C tail preservation
top1pct_k = max(1, int(0.01 * n))
top1pct_idx = np.argsort(np.abs(barpnl_ctrl))[-top1pct_k:]
top1pct_retention = float(barpnl_A[top1pct_idx].sum() / barpnl_ctrl[top1pct_idx].sum()) \
    if barpnl_ctrl[top1pct_idx].sum() != 0 else np.nan
top20_idx = np.argsort(np.abs(barpnl_ctrl))[-20:]
top20_participation_ctrl = 20  # by construction, all 20 "participate" in control
top20_retention = float(barpnl_A[top20_idx].sum() / barpnl_ctrl[top20_idx].sum()) \
    if barpnl_ctrl[top20_idx].sum() != 0 else np.nan
long_ctrl = barpnl_ctrl[barpos_ctrl > 0].sum(); short_ctrl = barpnl_ctrl[barpos_ctrl < 0].sum()
long_A = barpnl_A[barpos_A > 0].sum(); short_A = barpnl_A[barpos_A < 0].sum()
share_long_ctrl = long_ctrl / (long_ctrl + abs(short_ctrl)) if (long_ctrl + abs(short_ctrl)) else np.nan
share_long_A = long_A / (long_A + abs(short_A)) if (long_A + abs(short_A)) else np.nan
beta_drift_pp = abs(share_long_A - share_long_ctrl) * 100
gate_C = {"top1pct_bar_retention": top1pct_retention, "top20_bar_retention": top20_retention,
          "long_share_control": float(share_long_ctrl), "long_share_arm": float(share_long_A),
          "beta_drift_pp": float(beta_drift_pp),
          "gate_top1pct": bool(top1pct_retention >= 0.90),
          "gate_top20": bool(top20_retention >= 0.90),
          "gate_no_beta_drift": bool(beta_drift_pp <= 15.0)}
gate_C["GATE_C_PASS"] = bool(gate_C["gate_top1pct"] and gate_C["gate_top20"] and gate_C["gate_no_beta_drift"])
print("\n=== GATE C: TAIL PRESERVATION ===\n" + json.dumps(gate_C, indent=2), flush=True)

# ============================================================== gate D boundary stability
perturbations = {
    "narrow_30min": (8.5, 13.5), "narrow_60min": (9.0, 13.0),
    "wide_30min": (7.5, 14.5), "wide_60min": (7.0, 15.0),
}
pert_rows = []
for name, (lo, hi) in perturbations.items():
    m = (since >= lo) & (since < hi)
    Tp = apply_entry_eligibility(T, m)
    dly, _, _ = C1.e10_exec(bars, Tp)
    s = dly.set_index(dly["sess"].astype(str))["net"].reindex(CAL)
    bp = battery(s.to_numpy())
    pert_rows.append({"perturbation": name, "window_hours_since_1800": f"{lo}-{hi}",
                       "d_sharpe": bp["sharpe"] - bc["sharpe"], "d_CDaR": bc["CDaR_0.95"] - bp["CDaR_0.95"],
                       "same_dir_sharpe": bool(np.sign(bp["sharpe"] - bc["sharpe"]) == np.sign(gate_A["d_sharpe"])),
                       "same_dir_CDaR": bool(np.sign(bc["CDaR_0.95"] - bp["CDaR_0.95"]) == np.sign(gate_A["d_CDaR_pos_is_better"]))})
pert_df = pd.DataFrame(pert_rows)
pert_df.to_csv(os.path.join(OUT, "boundary_perturbation.csv"), index=False)
n_stable = int((pert_df["same_dir_sharpe"] & pert_df["same_dir_CDaR"]).sum())
gate_D = {"n_perturbations_same_direction": n_stable, "n_perturbations_total": len(pert_df),
          "GATE_D_STABLE": bool(n_stable >= 3)}
print("\n=== GATE D: BOUNDARY STABILITY ===")
print(pert_df.to_string(index=False), flush=True)
print(json.dumps(gate_D, indent=2), flush=True)

# ============================================================== bootstrap
idx = block_bootstrap_idx(len(CAL), BLOCK, NBOOT, SEED)
k5 = max(1, int(0.05 * len(CAL)))
sc, dc = path_stats(ctrl_s.to_numpy(), idx, k5)
sa, da = path_stats(armA_s.to_numpy(), idx, k5)
d_sh = sa - sc; d_cdr_ratio = (dc - da) / dc
boot = {"P_dSharpe_gt0": float((d_sh > 0).mean()), "P_dCDaR_ratio_gt0": float((d_cdr_ratio > 0).mean()),
        "q05_dSharpe": float(np.quantile(d_sh, 0.05)), "q95_dSharpe": float(np.quantile(d_sh, 0.95)),
        "seed": SEED, "block": BLOCK, "nboot": NBOOT}
json.dump(boot, open(os.path.join(OUT, "bootstrap.json"), "w"), indent=2)
print("\n=== BOOTSTRAP ===\n" + json.dumps(boot, indent=2), flush=True)

# ============================================================== D7-boundary split
splits = {"pre_D7_2024-08-05": (None, "2024-08-04"), "post_D7_2024-08-05": ("2024-08-05", None),
          "pre_2026-01-02": (None, "2026-01-01"), "stub_2026-01-02_on": ("2026-01-02", None)}
d7_rows = []
for sname, (a, b) in splits.items():
    idx_ = CAL
    if a: idx_ = idx_[idx_ >= a]
    if b: idx_ = idx_[idx_ <= b]
    bcs = battery(ctrl_s.reindex(idx_).to_numpy()); bas = battery(armA_s.reindex(idx_).to_numpy())
    d7_rows.append({"split": sname, "n_days": len(idx_), "d_sharpe": bas["sharpe"] - bcs["sharpe"],
                     "d_CDaR": bcs["CDaR_0.95"] - bas["CDaR_0.95"]})
pd.DataFrame(d7_rows).to_csv(os.path.join(OUT, "d7_split.csv"), index=False)
print("\n=== D7-BOUNDARY / STUB SPLIT ===")
print(pd.DataFrame(d7_rows).to_string(index=False), flush=True)

# ============================================================== verdict
if gate_A["GATE_A_PASS"] and gate_B["GATE_B_PASS"] and gate_C["GATE_C_PASS"]:
    verdict = "CANDIDATE" if gate_D["GATE_D_STABLE"] else "REGIME-LOCAL/CLOCK-FIT (gates A/B/C pass, gate D fails)"
else:
    verdict = "CONFIRMED-NOT-BENEFICIAL"
gates_out = {"gate_0_disclosure": exposure_disclosure.to_dict("records")[0],
             "gate_A": gate_A, "gate_B": gate_B, "gate_C": gate_C, "gate_D": gate_D,
             "VERDICT": verdict}
json.dump(gates_out, open(os.path.join(OUT, "gates.csv").replace(".csv", ".json"), "w"), indent=2, default=str)
pd.DataFrame([{"gate": "A", **gate_A}]).to_csv(os.path.join(OUT, "gates.csv"), index=False)
print("\n=== VERDICT ===\n" + verdict, flush=True)
print("\n=== S2 ARM A DONE ===", flush=True)
