"""P4_CHURN_SELECTIVITY -- conditional stronger-agreement entry gate during a measured
same-session flip-count HIGH_CHURN state. Implements frozen spec.yaml exactly. No parameter
in this file was chosen after seeing a P&L number; the churn-state window/threshold came from
the flip-count histogram alone (out/churn_diagnostic.json, computed before spec.yaml froze).
"""
import os, sys, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "runs", "W18R1_M1_VOLSEASON", "src"))
import sm01_solarsim as sm
import common as C1

OUT = os.path.join(ROOT, "runs", "P4_CHURN_SELECTIVITY", "out")
W = 20
FLIP_THRESH = 3
GRID = [0.20, 0.30, 0.40]

bars = C1.load_dev_bars()
close = bars["close"].to_numpy()
sess = bars["sess_date"].to_numpy()
sig460 = sm.sigma_series(close)
PEND, FLIPS = C1.build_pend_with_flips(bars, sig460)
mean_pend = PEND.mean(axis=1)                      # in [-1,1], the E10 pre-round input
T_ctrl = sm.e10_target(PEND)                        # control: unconditional round(10*mean_pend)

daily_ctrl, barpos_ctrl, barpnl_ctrl = C1.e10_exec(bars, T_ctrl)
ctrl_curve = daily_ctrl.set_index(daily_ctrl["sess"].astype(str))["net"]
CAL = ctrl_curve.index

# ---------------------------------------------------------------- churn state (fixed, not swept)
flip_per_bar = (FLIPS != 0).sum(axis=1)


def rolling_same_session(x, sess, w):
    n = len(x); out = np.zeros(n, dtype=int); buf = []
    cur = sess[0]
    for t in range(n):
        if sess[t] != cur:
            buf = []; cur = sess[t]
        buf.append(x[t])
        if len(buf) > w:
            buf.pop(0)
        out[t] = sum(buf)
    return out


rolling_flips = rolling_same_session(flip_per_bar, sess, W)
HIGH_CHURN = rolling_flips >= FLIP_THRESH

# secondary disclosure-only cross-check vs S1's ER150 (not used in construction)
sys.path.insert(0, os.path.join(ROOT, "runs", "W19R1_SELECTIVITY", "src"))
import scores_transform as ST
er150 = ST.er150_score(bars)
corr_churn_vs_low_er = float(np.corrcoef(HIGH_CHURN.astype(float), 1.0 - er150)[0, 1])


def apply_stronger_agreement(T, mean_pend, high_churn, required_frac):
    n = len(T); Tp = np.empty(n, dtype=int); prev = 0
    n_suppressed = 0
    for t in range(n):
        cur = int(T[t])
        is_new = (cur != 0) and ((prev == 0) or (np.sign(cur) != np.sign(prev)))
        if is_new and high_churn[t] and abs(mean_pend[t]) < required_frac:
            Tp[t] = 0
            n_suppressed += 1
        else:
            Tp[t] = cur
        prev = Tp[t]
    return Tp, n_suppressed


def battery(x):
    eqd = np.cumsum(x); dd = np.maximum.accumulate(eqd) - eqd
    k = max(1, int(0.05 * len(x))); sd = x.std(ddof=1)
    return {"n_days": len(x), "net": float(x.sum()),
            "sharpe": float(x.mean() / sd * np.sqrt(252)) if sd > 0 and len(x) > 1 else np.nan,
            "CDaR_0.95": float(np.sort(dd)[::-1][:k].mean()) if len(dd) else 0.0}


bc = battery(ctrl_curve.to_numpy())
cal_sorted = sorted(CAL); trimmed_cal = cal_sorted[:-106]
bc_t = battery(ctrl_curve.reindex(trimmed_cal).to_numpy())

rows = []
cell_curves = {}
for rf in GRID:
    Tp, n_supp = apply_stronger_agreement(T_ctrl, mean_pend, HIGH_CHURN, rf)
    daily, barpos, barpnl = C1.e10_exec(bars, Tp)
    curve = daily.set_index(daily["sess"].astype(str))["net"].reindex(CAL)
    cell_curves[rf] = curve
    ba = battery(curve.to_numpy())

    g_sharpe = bool(ba["sharpe"] > bc["sharpe"])
    g_cdar = bool(ba["CDaR_0.95"] < bc["CDaR_0.95"])
    idx_c = np.argsort(ctrl_curve.to_numpy())[-10:]
    house = float(curve.to_numpy()[idx_c].sum() / ctrl_curve.to_numpy()[idx_c].sum())
    g_top10 = bool(house >= 0.95)
    gate_A = bool(g_sharpe and g_cdar and g_top10)

    df_y = pd.DataFrame({"c": ctrl_curve, "a": curve}); df_y.index = pd.to_datetime(df_y.index)
    df_y["year"] = df_y.index.year
    agree = 0
    for y, g in df_y.groupby("year"):
        bcy = battery(g["c"].to_numpy()); bay = battery(g["a"].to_numpy())
        agree += int(bay["sharpe"] - bcy["sharpe"] > 0)
    ba_t = battery(curve.reindex(trimmed_cal).to_numpy())
    survives_trim = bool(ba_t["sharpe"] > bc_t["sharpe"] and ba_t["CDaR_0.95"] < bc_t["CDaR_0.95"])
    gate_B = bool(agree >= 4 and survives_trim)

    rows.append({
        "REQUIRED_FRAC": rf, "n_suppressed_commitments": n_supp,
        "net": ba["net"], "sharpe": ba["sharpe"], "CDaR_0.95": ba["CDaR_0.95"],
        "d_sharpe": ba["sharpe"] - bc["sharpe"], "d_CDaR": bc["CDaR_0.95"] - ba["CDaR_0.95"],
        "top10_house_retention": house, "GATE_A": gate_A,
        "yearly_sign_agree": agree, "survives_trim": survives_trim, "GATE_B": gate_B,
    })
    print(f"REQUIRED_FRAC={rf}  n_supp={n_supp}  dSharpe={ba['sharpe']-bc['sharpe']:+.4f}  "
          f"A={gate_A}  B={gate_B}", flush=True)

grid_df = pd.DataFrame(rows)
n_gate_A_pass = int(grid_df["GATE_A"].sum())
gate_C_plateau = bool(n_gate_A_pass >= 2)   # >=2 of 3 cells beat control on gate_A

# gate D: symmetric outcome disclosure of what was suppressed (bar-level, using the widest cell)
rf_widest = max(GRID)
Tp_widest, n_supp_widest = apply_stronger_agreement(T_ctrl, mean_pend, HIGH_CHURN, rf_widest)
suppressed_mask = (Tp_widest == 0) & (T_ctrl != 0)
_, barpos_ctrl2, barpnl_ctrl2 = C1.e10_exec(bars, T_ctrl)
# bar-level PnL the suppressed commitment bar itself realized under control, as a directional proxy
suppressed_bar_pnl = barpnl_ctrl2[suppressed_mask]
gate_D_disclosure = {
    "cell_used_for_disclosure": rf_widest,
    "n_suppressed": int(suppressed_mask.sum()),
    "suppressed_bar_pnl_mean": float(suppressed_bar_pnl.mean()) if suppressed_mask.sum() else None,
    "suppressed_bar_pnl_positive_share": float((suppressed_bar_pnl > 0).mean()) if suppressed_mask.sum() else None,
    "note": "bar-level PnL on the commitment bar itself is a coarse proxy for 'would this have been "
            "a winner', not a full trade-level attribution -- disclosure only, not a gate criterion.",
}

promotion = "CANDIDATE" if (n_gate_A_pass >= 1 and any(r["GATE_A"] and r["GATE_B"] for r in rows) and gate_C_plateau) else "CONFIRMED-NOT-BENEFICIAL"
best_cell = max(rows, key=lambda r: r["d_sharpe"])

summary = {
    "churn_state": {"window_bars": W, "threshold": FLIP_THRESH,
                     "pct_bars_high_churn": float(HIGH_CHURN.mean()),
                     "corr_high_churn_vs_low_ER150": corr_churn_vs_low_er},
    "grid": rows, "n_gate_A_pass": n_gate_A_pass, "gate_C_plateau": gate_C_plateau,
    "gate_D_disclosure": gate_D_disclosure,
    "best_cell_by_d_sharpe": best_cell,
    "disposition": promotion,
}
grid_df.to_csv(os.path.join(OUT, "grid_results.csv"), index=False)
json.dump(summary, open(os.path.join(OUT, "summary.json"), "w"), indent=2)
print("\n=== SUMMARY ===\n" + json.dumps(summary, indent=2, default=str), flush=True)
