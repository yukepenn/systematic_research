"""X1X2_EXECUTION_FRICTION_AUDIT -- decision-lag degradation curve + friction stress with
breakeven-multiple estimation. Descriptive audit, implements frozen spec.yaml exactly.
"""
import os, sys, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "runs", "W18R1_M1_VOLSEASON", "src"))
import sm01_solarsim as sm
import common as C1

OUT = os.path.join(ROOT, "runs", "X1X2_EXECUTION_FRICTION_AUDIT", "out")

bars = C1.load_dev_bars()
close = bars["close"].to_numpy()
sig460 = sm.sigma_series(close)
PEND = C1.build_pend(bars, sig460)
T = sm.e10_target(PEND)


def battery(x):
    eqd = np.cumsum(x); dd = np.maximum.accumulate(eqd) - eqd
    k = max(1, int(0.05 * len(x))); sd = x.std(ddof=1)
    return {"n_days": len(x), "net": float(x.sum()),
            "sharpe": float(x.mean() / sd * np.sqrt(252)) if sd > 0 and len(x) > 1 else np.nan,
            "CDaR_0.95": float(np.sort(dd)[::-1][:k].mean()) if len(dd) else 0.0}


daily0, _, _ = C1.e10_exec(bars, T)
b0 = battery(daily0.set_index(daily0["sess"].astype(str))["net"].to_numpy())
print(f"BASELINE (k=0, slip=1tick, comm=$0.65)  net={b0['net']:.2f}  sharpe={b0['sharpe']:.4f}  CDaR={b0['CDaR_0.95']:.2f}", flush=True)

# ============================================================================ X1: decision lag
print("=" * 90); print("X1: decision-lag degradation curve"); print("=" * 90)
x1_rows = []
for k in (0, 1, 2, 4, 8):
    Tk = np.zeros_like(T)
    if k == 0:
        Tk = T
    else:
        Tk[k:] = T[:-k]
    daily, _, _ = C1.e10_exec(bars, Tk)
    b = battery(daily.set_index(daily["sess"].astype(str))["net"].to_numpy())
    x1_rows.append({"extra_lag_bars": k, "extra_lag_minutes": k * 3, **b,
                     "net_pct_of_baseline": float(b["net"] / b0["net"] * 100) if b0["net"] else np.nan,
                     "sharpe_pct_of_baseline": float(b["sharpe"] / b0["sharpe"] * 100) if b0["sharpe"] else np.nan})
    print(f"k={k:2d} ({k*3:3d}min extra)  net={b['net']:12.2f} ({b['net']/b0['net']*100:6.1f}% of baseline)  "
          f"sharpe={b['sharpe']:.4f} ({b['sharpe']/b0['sharpe']*100:6.1f}%)", flush=True)
x1_df = pd.DataFrame(x1_rows)
x1_df.to_csv(os.path.join(OUT, "x1_decision_lag.csv"), index=False)

# ============================================================================ X2: friction stress
print("\n" + "=" * 90); print("X2: friction stress"); print("=" * 90)


def run_friction(slip_ticks, comm_mult):
    old_tick = sm.TICK
    sm.TICK = 0.25 * slip_ticks
    try:
        daily, _, _ = C1.e10_exec(bars, T, comm_side=sm.MNQ_COMM_SIDE * comm_mult)
    finally:
        sm.TICK = old_tick
    return battery(daily.set_index(daily["sess"].astype(str))["net"].to_numpy())


x2_rows = []
print("-- (a) slip sweep at baseline commission --", flush=True)
for st_ in (1, 2, 3, 4):
    b = run_friction(st_, 1.0)
    x2_rows.append({"axis": "slip", "slip_ticks": st_, "comm_mult": 1.0, **b})
    print(f"slip={st_}tick  net={b['net']:12.2f}  sharpe={b['sharpe']:.4f}  CDaR={b['CDaR_0.95']:.2f}", flush=True)

print("-- (b) commission sweep at baseline slip --", flush=True)
for cm in (1.0, 1.5, 2.0, 3.0):
    b = run_friction(1, cm)
    x2_rows.append({"axis": "comm", "slip_ticks": 1, "comm_mult": cm, **b})
    print(f"comm_mult={cm}x (${0.65*cm:.3f}/side)  net={b['net']:12.2f}  sharpe={b['sharpe']:.4f}  CDaR={b['CDaR_0.95']:.2f}", flush=True)

print("-- (c) joint stress: slip=2tick AND comm_mult=1.5x --", flush=True)
b_joint = run_friction(2, 1.5)
x2_rows.append({"axis": "joint_stress", "slip_ticks": 2, "comm_mult": 1.5, **b_joint})
print(f"joint  net={b_joint['net']:12.2f}  sharpe={b_joint['sharpe']:.4f}  CDaR={b_joint['CDaR_0.95']:.2f}", flush=True)

x2_df = pd.DataFrame(x2_rows)
x2_df.to_csv(os.path.join(OUT, "x2_friction_stress.csv"), index=False)


def breakeven_multiple(axis_col, grid_df, baseline_sharpe):
    d = grid_df.sort_values(axis_col)
    xs = d[axis_col].to_numpy(); ys = d["sharpe"].to_numpy()
    if np.all(ys > 0):
        return None, "sharpe never crosses zero within tested grid"
    for i in range(len(xs) - 1):
        if ys[i] > 0 >= ys[i + 1]:
            frac = ys[i] / (ys[i] - ys[i + 1])
            return float(xs[i] + frac * (xs[i + 1] - xs[i])), "interpolated within grid"
    return None, "already <=0 at smallest grid point"


slip_grid = x2_df[x2_df["axis"] == "slip"]
comm_grid = x2_df[x2_df["axis"] == "comm"]
be_slip, be_slip_note = breakeven_multiple("slip_ticks", slip_grid, b0["sharpe"])
be_comm, be_comm_note = breakeven_multiple("comm_mult", comm_grid, b0["sharpe"])
print(f"\nbreakeven slip_ticks (Sharpe->0): {be_slip} ({be_slip_note})", flush=True)
print(f"breakeven comm_mult (Sharpe->0): {be_comm} ({be_comm_note})", flush=True)

summary = {
    "baseline": b0, "x1_decision_lag": x1_rows, "x2_friction_stress": x2_rows,
    "breakeven_slip_ticks": be_slip, "breakeven_slip_note": be_slip_note,
    "breakeven_comm_mult": be_comm, "breakeven_comm_note": be_comm_note,
}
json.dump(summary, open(os.path.join(OUT, "summary.json"), "w"), indent=2, default=str)
print("\ndone.", flush=True)
