"""M4_ANCHOR — CLOSE (control) vs HILO_RAW vs CLOSE_CONFIRMED. Frozen spec.yaml, committed
BEFORE this code."""
import os, sys, json, datetime as dt
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "runs", "W18R1_M1_VOLSEASON", "src"))
import sm01_solarsim as sm
import common as C1
sys.path.insert(0, os.path.join(ROOT, "runs", "M4_ANCHOR", "src"))
import m4_common as M4

RUN = os.path.join(ROOT, "runs", "M4_ANCHOR")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
DEV_END = dt.date(2026, 5, 29)


def battery(x):
    eqd = np.cumsum(x); dd = np.maximum.accumulate(eqd) - eqd
    k = max(1, int(0.05 * len(x)))
    sd = x.std(ddof=1)
    return {"sharpe": float(x.mean() / sd * np.sqrt(252)) if sd > 0 and len(x) > 1 else np.nan,
            "CDaR_0.95": float(np.sort(dd)[::-1][:k].mean()) if len(dd) else 0.0,
            "net": float(x.sum())}


def top10_retention(ctrl, arm):
    idx_c = np.argsort(ctrl)[-10:]
    return float(arm[idx_c].sum() / ctrl[idx_c].sum()) if ctrl[idx_c].sum() != 0 else np.nan


bars = C1.load_dev_bars()
n = len(bars)
sess = bars["sess_date"].to_numpy()
close = bars["close"].to_numpy()
sig460 = sm.sigma_series(close)

print("=== PARITY ASSERTION (mode=CLOSE vs sm01_solarsim original) ===", flush=True)
ok, detail = M4.verify_parity(bars, sig460)
json.dump({"PASS": ok, "detail": detail}, open(os.path.join(OUT, "parity_assertion.json"), "w"), indent=2)
print(json.dumps({"PASS": ok}, indent=2), flush=True)
assert ok, "M4 parity assertion FAILED. STOP."

PEND_ctrl = C1.build_pend(bars, sig460)
T_ctrl = sm.e10_target(PEND_ctrl)
daily_ctrl, barpos_ctrl, barpnl_ctrl = C1.e10_exec(bars, T_ctrl)
ref_path = os.path.join(ROOT, "runs", "SMV2AD_VOLMULT_CEILING", "out", "e10_daily_dev_control_1200.csv")
ref = pd.read_csv(ref_path); ref["sess"] = pd.to_datetime(ref["sess"]).dt.date.astype(str)
mine = daily_ctrl.copy(); mine["sess"] = mine["sess"].astype(str)
mrg = mine.merge(ref, on="sess", suffixes=("", "_ref"))
crosscheck_ok = bool(len(mrg) == len(mine) == len(ref) and (mrg["net"] - mrg["net_ref"]).abs().max() < 0.01)
print(f"control crosscheck: {crosscheck_ok}", flush=True)
assert crosscheck_ok
daily_ctrl.to_csv(os.path.join(OUT, "daily_control.csv"), index=False)
ctrl_curve = daily_ctrl.set_index(daily_ctrl["sess"].astype(str))["net"]
CAL = ctrl_curve.index
bc = battery(ctrl_curve.to_numpy())
ctrl_flips_total = int(np.sum([np.count_nonzero(sm.member_states(close, sig460, float(vm))[1]) for vm in sm.VMS]))

# ============================================================== HILO_RAW / CLOSE_CONFIRMED
results = {}
curves = {}
flip_totals = {"CLOSE": ctrl_flips_total}
for mode in ("HILO_RAW", "CLOSE_CONFIRMED"):
    PEND, FLIPS = M4.build_pend_anchor(bars, sig460, mode)
    T = sm.e10_target(PEND)
    daily, barpos, barpnl = C1.e10_exec(bars, T)
    daily.to_csv(os.path.join(OUT, f"daily_{mode.lower()}.csv"), index=False)
    curve = daily.set_index(daily["sess"].astype(str))["net"].reindex(CAL)
    curves[mode] = curve
    ba = battery(curve.to_numpy())
    house_ret = top10_retention(ctrl_curve.to_numpy(), curve.to_numpy())
    g_sharpe = bool(ba["sharpe"] > bc["sharpe"]); g_cdar = bool(ba["CDaR_0.95"] < bc["CDaR_0.95"])
    g_top10 = bool(house_ret >= 0.95)
    n_false_reversal = 0
    for col in range(FLIPS.shape[1]):
        idx = np.where(FLIPS[:, col] != 0)[0]
        if len(idx) > 1:
            gaps = np.diff(idx)
            signs = FLIPS[idx, col]
            n_false_reversal += int(np.sum((gaps <= 5) & (signs[1:] != signs[:-1])))
    flip_totals[mode] = int(np.count_nonzero(FLIPS))
    top1pct_k = max(1, int(0.01 * n))
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

    df_y = pd.DataFrame({"c": ctrl_curve, "a": curve}); df_y.index = pd.to_datetime(df_y.index)
    df_y["year"] = df_y.index.year
    yrows = []
    for y, g in df_y.groupby("year"):
        bcy = battery(g["c"].to_numpy()); bay = battery(g["a"].to_numpy())
        yrows.append({"mode": mode, "year": int(y), "n_days": len(g), "d_sharpe": bay["sharpe"] - bcy["sharpe"],
                      "sign_positive": bool(bay["sharpe"] - bcy["sharpe"] > 0)})
    yearly = pd.DataFrame(yrows)
    agree = int(yearly["sign_positive"].sum())
    cal_sorted = sorted(CAL); trimmed_cal = cal_sorted[:-106]
    bc_t = battery(ctrl_curve.reindex(trimmed_cal).to_numpy()); ba_t = battery(curve.reindex(trimmed_cal).to_numpy())
    survives_trim = bool(ba_t["sharpe"] > bc_t["sharpe"] and ba_t["CDaR_0.95"] < bc_t["CDaR_0.95"])
    gate_B_pass = bool(agree >= 4 and survives_trim)

    verdict = "CANDIDATE" if (g_sharpe and g_cdar and g_top10 and gate_B_pass and gate_C_pass) else "CONFIRMED-NOT-BENEFICIAL"
    results[mode] = {
        "mode": mode, "sharpe": ba["sharpe"], "d_sharpe": ba["sharpe"] - bc["sharpe"],
        "CDaR": ba["CDaR_0.95"], "d_CDaR_pos_better": bc["CDaR_0.95"] - ba["CDaR_0.95"],
        "net": ba["net"], "top10_retention": house_ret,
        "gate_sharpe": g_sharpe, "gate_CDaR": g_cdar, "gate_top10": g_top10, "GATE_A_PASS": bool(g_sharpe and g_cdar and g_top10),
        "yearly_sign_agree": agree, "survives_trim": survives_trim, "GATE_B_PASS": gate_B_pass,
        "top1pct_retention": top1pct_ret, "top20_retention": top20_ret, "beta_drift_pp": beta_drift, "GATE_C_PASS": gate_C_pass,
        "n_flips_total": flip_totals[mode], "n_flips_vs_control_pct": flip_totals[mode] / ctrl_flips_total * 100,
        "n_false_reversal_within_5bars": n_false_reversal,
        "VERDICT": verdict,
    }
    yearly.to_csv(os.path.join(OUT, f"yearly_{mode.lower()}.csv"), index=False)
    print(f"\n=== {mode} ===\n" + json.dumps(results[mode], indent=2), flush=True)

grid_df = pd.DataFrame(list(results.values()))
grid_df.to_csv(os.path.join(OUT, "gates.csv"), index=False)
pd.DataFrame([{"mode": k, **v} for k, v in flip_totals.items()]).to_csv(os.path.join(OUT, "flip_decomposition.csv"), index=False)
json.dump({k: v["VERDICT"] for k, v in results.items()}, open(os.path.join(OUT, "verdict.json"), "w"), indent=2)
print("\n=== M4 DONE ===", flush=True)
