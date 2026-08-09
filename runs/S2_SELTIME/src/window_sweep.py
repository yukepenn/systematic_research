"""S2_SELTIME — window-specificity sweep, run directly per the mandatory red team's explicit
recommendation ("run gates B/C/D, not just A, across a modest window sweep"). This is a
robustness/specificity check on the ALREADY-FROZEN Arm A rule (apply_entry_eligibility), not a
new alpha hypothesis or a re-optimization -- no threshold or construction is changed, only the
WINDOW is swept, exactly reproducing the red team's own 24-window methodology (hourly steps,
6-hour width) for direct comparability, then extended with gates B and C (which the red team
did not run for all 24, only for the single strongest gate-A competitor).
"""
import os, sys, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "runs", "W18R1_M1_VOLSEASON", "src"))
import sm01_solarsim as sm
import common as C1

OUT = os.path.join(ROOT, "runs", "S2_SELTIME", "out")


# Verbatim copies of run.py's helpers (NOT imported as a module -- run.py is a top-level script
# that executes its whole pipeline on import; duplicating these four small, already-red-team-
# verified functions avoids re-running S2's entire original pipeline as an import side effect).
def since_1800_hours(bars):
    t = pd.to_datetime(bars["time"])
    hh = t.dt.hour.to_numpy() + t.dt.minute.to_numpy() / 60.0
    return (hh - 18.0) % 24.0


def apply_entry_eligibility(T, blocked_mask):
    n = len(T)
    Tp = np.empty(n, dtype=int)
    prev = 0
    for t in range(n):
        cur = int(T[t])
        is_new_commitment = (cur != 0) and ((prev == 0) or (np.sign(cur) != np.sign(prev)))
        Tp[t] = 0 if (is_new_commitment and blocked_mask[t]) else cur
        prev = Tp[t]
    return Tp


def battery(x):
    eqd = np.cumsum(x); dd = np.maximum.accumulate(eqd) - eqd
    k = max(1, int(0.05 * len(x)))
    sd = x.std(ddof=1)
    return {"n_days": len(x), "net": float(x.sum()),
            "sharpe": float(x.mean() / sd * np.sqrt(252)) if sd > 0 and len(x) > 1 else np.nan,
            "CDaR_0.95": float(np.sort(dd)[::-1][:k].mean()) if len(dd) else 0.0}


def top10_retention(ctrl, arm):
    idx_c = np.argsort(ctrl)[-10:]
    house = float(arm[idx_c].sum() / ctrl[idx_c].sum()) if ctrl[idx_c].sum() != 0 else np.nan
    return house, house


class S2:
    since_1800_hours = staticmethod(since_1800_hours)
    apply_entry_eligibility = staticmethod(apply_entry_eligibility)
    battery = staticmethod(battery)
    top10_retention = staticmethod(top10_retention)

bars = C1.load_dev_bars()
close = bars["close"].to_numpy()
sig460 = sm.sigma_series(close)
T = sm.e10_target(C1.build_pend(bars, sig460))
daily_ctrl, barpos_ctrl, barpnl_ctrl = C1.e10_exec(bars, T)
ctrl_curve = daily_ctrl.set_index(daily_ctrl["sess"].astype(str))["net"]
CAL = ctrl_curve.index
bc = S2.battery(ctrl_curve.to_numpy())
since = S2.since_1800_hours(bars)
cal_sorted = sorted(CAL); trimmed_cal = cal_sorted[:-106]

rows = []
for start_h in range(0, 24):  # hourly offsets, 6-hour width, matching the red team's sweep exactly
    lo, hi = float(start_h), float(start_h + 6) % 24 if start_h + 6 != 24 else 24.0
    if start_h + 6 <= 24:
        mask = (since >= start_h) & (since < start_h + 6)
        window_label = f"{start_h:02d}00-{(start_h+6)%24:02d}00"
    else:
        mask = (since >= start_h) | (since < (start_h + 6) - 24)
        window_label = f"{start_h:02d}00-{(start_h+6)%24:02d}00"
    Tp = S2.apply_entry_eligibility(T, mask)
    daily, barpos, barpnl = C1.e10_exec(bars, Tp)
    curve = daily.set_index(daily["sess"].astype(str))["net"].reindex(CAL)
    ba = S2.battery(curve.to_numpy())
    house_ret, _ = S2.top10_retention(ctrl_curve.to_numpy(), curve.to_numpy())
    g_sharpe = bool(ba["sharpe"] > bc["sharpe"]); g_cdar = bool(ba["CDaR_0.95"] < bc["CDaR_0.95"])
    g_top10 = bool(house_ret >= 0.95)
    gate_A_pass = bool(g_sharpe and g_cdar and g_top10)

    df_y = pd.DataFrame({"c": ctrl_curve, "a": curve}); df_y.index = pd.to_datetime(df_y.index)
    df_y["year"] = df_y.index.year
    agree = 0
    for y, g in df_y.groupby("year"):
        bcy = S2.battery(g["c"].to_numpy()); bay = S2.battery(g["a"].to_numpy())
        agree += int(bay["sharpe"] - bcy["sharpe"] > 0)
    bc_t = S2.battery(ctrl_curve.reindex(trimmed_cal).to_numpy())
    ba_t = S2.battery(curve.reindex(trimmed_cal).to_numpy())
    survives_trim = bool(ba_t["sharpe"] > bc_t["sharpe"] and ba_t["CDaR_0.95"] < bc_t["CDaR_0.95"])
    gate_B_pass = bool(agree >= 4 and survives_trim)

    top1pct_k = max(1, int(0.01 * len(bars)))
    top1pct_idx = np.argsort(np.abs(barpnl_ctrl))[-top1pct_k:]
    top1pct_ret = float(barpnl[top1pct_idx].sum() / barpnl_ctrl[top1pct_idx].sum()) if barpnl_ctrl[top1pct_idx].sum() else np.nan
    top20_idx = np.argsort(np.abs(barpnl_ctrl))[-20:]
    top20_ret = float(barpnl[top20_idx].sum() / barpnl_ctrl[top20_idx].sum()) if barpnl_ctrl[top20_idx].sum() else np.nan
    long_c = barpnl_ctrl[barpos_ctrl > 0].sum(); short_c = barpnl_ctrl[barpos_ctrl < 0].sum()
    long_a = barpnl[barpos > 0].sum(); short_a = barpnl[barpos < 0].sum()
    share_c = long_c / (long_c + abs(short_c)) if (long_c + abs(short_c)) else np.nan
    share_a = long_a / (long_a + abs(short_a)) if (long_a + abs(short_a)) else np.nan
    beta_drift = abs(share_a - share_c) * 100 if np.isfinite(share_c) and np.isfinite(share_a) else np.nan
    gate_C_pass = bool(top1pct_ret >= 0.90 and top20_ret >= 0.90 and beta_drift <= 15.0)

    rows.append({
        "window": window_label, "start_hour_since_1800": start_h,
        "is_decision_cell": bool(start_h == 8),
        "d_sharpe": ba["sharpe"] - bc["sharpe"], "d_CDaR": bc["CDaR_0.95"] - ba["CDaR_0.95"],
        "top10_house": house_ret, "GATE_A_PASS": gate_A_pass,
        "yearly_sign_agree": agree, "survives_trim": survives_trim, "GATE_B_PASS": gate_B_pass,
        "top1pct_ret": top1pct_ret, "top20_ret": top20_ret, "beta_drift_pp": beta_drift, "GATE_C_PASS": gate_C_pass,
        "FULL_BATTERY_PASS": bool(gate_A_pass and gate_B_pass and gate_C_pass),
    })
    print(f"{window_label}  dSharpe={ba['sharpe']-bc['sharpe']:+.4f}  A={gate_A_pass}  B={gate_B_pass}  C={gate_C_pass}  FULL={gate_A_pass and gate_B_pass and gate_C_pass}", flush=True)

sweep = pd.DataFrame(rows)
sweep.to_csv(os.path.join(OUT, "window_sweep_full_battery.csv"), index=False)
n_full_pass = int(sweep["FULL_BATTERY_PASS"].sum())
rank = int((sweep["d_sharpe"] > sweep.loc[sweep.is_decision_cell, "d_sharpe"].iloc[0]).sum()) + 1
summary = {
    "n_windows_tested": 24, "n_gate_A_pass": int(sweep["GATE_A_PASS"].sum()),
    "n_gate_B_pass_among_A_passers": int(sweep.loc[sweep.GATE_A_PASS, "GATE_B_PASS"].sum()),
    "n_full_battery_pass": n_full_pass,
    "decision_cell_rank_by_dSharpe": rank,
    "windows_passing_full_battery": sweep.loc[sweep.FULL_BATTERY_PASS, "window"].tolist(),
}
json.dump(summary, open(os.path.join(OUT, "window_sweep_summary.json"), "w"), indent=2)
print("\n=== SUMMARY ===\n" + json.dumps(summary, indent=2), flush=True)
