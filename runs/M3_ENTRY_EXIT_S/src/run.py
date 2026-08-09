"""M3_ENTRY_EXIT_S — 3x3 grid, frozen spec.yaml (committed 7565d1d) BEFORE this code."""
import os, sys, json, datetime as dt
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "runs", "W18R1_M1_VOLSEASON", "src"))
import sm01_solarsim as sm
import common as C1
sys.path.insert(0, os.path.join(ROOT, "runs", "M3_ENTRY_EXIT_S", "src"))
import m3_common as M3

RUN = os.path.join(ROOT, "runs", "M3_ENTRY_EXIT_S")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
DEV_END = dt.date(2026, 5, 29)
SEED, BLOCK, NBOOT = 20260809, 5, 10000

ENTRY_GRID = [1.0, 1.25, 1.5]
EXIT_GRID = [0.75, 1.0, 1.25]


def battery(x):
    eqd = np.cumsum(x); dd = np.maximum.accumulate(eqd) - eqd
    k = max(1, int(0.05 * len(x)))
    sd = x.std(ddof=1)
    return {"n_days": len(x), "net": float(x.sum()),
            "sharpe": float(x.mean() / sd * np.sqrt(252)) if sd > 0 and len(x) > 1 else np.nan,
            "CDaR_0.95": float(np.sort(dd)[::-1][:k].mean()) if len(dd) else 0.0}


def top10_retention(ctrl, arm):
    idx_c = np.argsort(ctrl)[-10:]
    return float(arm[idx_c].sum() / ctrl[idx_c].sum()) if ctrl[idx_c].sum() != 0 else np.nan


bars = C1.load_dev_bars()
n = len(bars)
sess = bars["sess_date"].to_numpy()
close = bars["close"].to_numpy()
sig460 = sm.sigma_series(close)

print("=== PARITY ASSERTION (entry_mult=exit_mult=1.0 vs sm01_solarsim original) ===", flush=True)
ok, detail = M3.verify_parity(bars, sig460)
json.dump({"PASS": ok, "detail": detail}, open(os.path.join(OUT, "parity_assertion.json"), "w"), indent=2)
print(json.dumps({"PASS": ok}, indent=2), flush=True)
assert ok, "M3 parity assertion FAILED — asymmetric state machine does not reduce to the original at (1,1). STOP."

# control (reused from the parity-verified (1.0,1.0) cell — but recomputed via the E10/e10_exec
# path independently here, and cross-checked against the frozen reference curve, same as every
# other run in this campaign)
PEND_ctrl = C1.build_pend(bars, sig460)
T_ctrl = sm.e10_target(PEND_ctrl)
daily_ctrl, barpos_ctrl, barpnl_ctrl = C1.e10_exec(bars, T_ctrl)
ref_path = os.path.join(ROOT, "runs", "SMV2AD_VOLMULT_CEILING", "out", "e10_daily_dev_control_1200.csv")
ref = pd.read_csv(ref_path); ref["sess"] = pd.to_datetime(ref["sess"]).dt.date.astype(str)
mine = daily_ctrl.copy(); mine["sess"] = mine["sess"].astype(str)
mrg = mine.merge(ref, on="sess", suffixes=("", "_ref"))
crosscheck_ok = bool(len(mrg) == len(mine) == len(ref) and (mrg["net"] - mrg["net_ref"]).abs().max() < 0.01)
print(f"control crosscheck vs frozen reference: {crosscheck_ok}", flush=True)
assert crosscheck_ok

daily_ctrl.to_csv(os.path.join(OUT, "daily_control.csv"), index=False)
ctrl_curve = daily_ctrl.set_index(daily_ctrl["sess"].astype(str))["net"]
CAL = ctrl_curve.index
bc = battery(ctrl_curve.to_numpy())

# ============================================================== grid
cell_results = {}
cell_curves = {}
cell_flipinfo = {}
for em in ENTRY_GRID:
    for xm in EXIT_GRID:
        label = f"E{em}_X{xm}"
        if em == 1.0 and xm == 1.0:
            T_cell = T_ctrl
            n_flips_total = int(np.sum([np.count_nonzero(sm.member_states(close, sig460, float(vm))[1])
                                         for vm in sm.VMS]))
        else:
            PEND = M3.build_pend_asym(bars, sig460, em, xm)
            T_cell = sm.e10_target(PEND)
            n_flips_total = 0
            for vm in sm.VMS:
                is_up, flip, s_e, s_x, anchor = M3.member_states_asym(close, sig460, float(vm), em, xm)
                n_flips_total += int(np.count_nonzero(flip))
        daily, barpos, barpnl = C1.e10_exec(bars, T_cell)
        daily.to_csv(os.path.join(OUT, f"daily_{label}.csv"), index=False)
        curve = daily.set_index(daily["sess"].astype(str))["net"].reindex(CAL)
        cell_curves[(em, xm)] = curve
        ba = battery(curve.to_numpy())
        house_ret = top10_retention(ctrl_curve.to_numpy(), curve.to_numpy())
        g_sharpe = bool(ba["sharpe"] > bc["sharpe"]); g_cdar = bool(ba["CDaR_0.95"] < bc["CDaR_0.95"])
        g_top10 = bool(house_ret >= 0.95)
        cell_results[(em, xm)] = {
            "entry_mult": em, "exit_mult": xm, "label": label,
            "sharpe": ba["sharpe"], "d_sharpe": ba["sharpe"] - bc["sharpe"],
            "CDaR": ba["CDaR_0.95"], "d_CDaR_pos_better": bc["CDaR_0.95"] - ba["CDaR_0.95"],
            "net": ba["net"], "top10_retention": house_ret,
            "gate_sharpe": g_sharpe, "gate_CDaR": g_cdar, "gate_top10": g_top10,
            "GATE_A_PASS": bool(g_sharpe and g_cdar and g_top10),
            "n_flips_total": n_flips_total,
            "n_flips_vs_control_pct": n_flips_total / cell_flipinfo.get("ctrl_flips", n_flips_total) * 100 if "ctrl_flips" in cell_flipinfo else 100.0,
        }
        if em == 1.0 and xm == 1.0:
            cell_flipinfo["ctrl_flips"] = n_flips_total
        print(f"{label:12s} sharpe {ba['sharpe']:.4f} (d={ba['sharpe']-bc['sharpe']:+.4f})  "
              f"CDaR {ba['CDaR_0.95']:>10,.0f}  top10 {house_ret:.3f}  "
              f"GATE_A {cell_results[(em,xm)]['GATE_A_PASS']}  flips {n_flips_total}", flush=True)

# fix up n_flips_vs_control_pct now that ctrl_flips is known for all cells
ctrl_flips = cell_flipinfo["ctrl_flips"]
for k in cell_results:
    cell_results[k]["n_flips_vs_control_pct"] = cell_results[k]["n_flips_total"] / ctrl_flips * 100

grid_df = pd.DataFrame(list(cell_results.values()))
grid_df.to_csv(os.path.join(OUT, "grid_metrics.csv"), index=False)
print("\n=== GRID SUMMARY ===")
print(grid_df[["label", "entry_mult", "exit_mult", "sharpe", "d_sharpe", "CDaR", "top10_retention",
                "GATE_A_PASS", "n_flips_vs_control_pct"]].to_string(index=False), flush=True)

# ============================================================== gate B chronology (best cell by d_sharpe among GATE_A passers, else best overall)
passers = grid_df[grid_df["GATE_A_PASS"]]
if len(passers):
    best_row = passers.sort_values("d_sharpe", ascending=False).iloc[0]
else:
    best_row = grid_df.sort_values("d_sharpe", ascending=False).iloc[0]
best_em, best_xm = best_row["entry_mult"], best_row["exit_mult"]
best_curve = cell_curves[(best_em, best_xm)]
print(f"\nBEST CELL: entry={best_em} exit={best_xm} (GATE_A_PASS={bool(best_row['GATE_A_PASS'])})", flush=True)

df_y = pd.DataFrame({"c": ctrl_curve, "a": best_curve}); df_y.index = pd.to_datetime(df_y.index)
df_y["year"] = df_y.index.year
yrows = []
for y, g in df_y.groupby("year"):
    bcy = battery(g["c"].to_numpy()); bay = battery(g["a"].to_numpy())
    yrows.append({"year": int(y), "n_days": len(g), "sharpe_control": bcy["sharpe"],
                  "sharpe_arm": bay["sharpe"], "d_sharpe": bay["sharpe"] - bcy["sharpe"],
                  "sign_positive": bool(bay["sharpe"] - bcy["sharpe"] > 0)})
yearly = pd.DataFrame(yrows)
yearly.to_csv(os.path.join(OUT, "yearly_by_cell.csv"), index=False)
agree = int(yearly["sign_positive"].sum())
cal_sorted = sorted(CAL); trimmed_cal = cal_sorted[:-106]
bc_t = battery(ctrl_curve.reindex(trimmed_cal).to_numpy()); ba_t = battery(best_curve.reindex(trimmed_cal).to_numpy())
survives_trim = bool(ba_t["sharpe"] > bc_t["sharpe"] and ba_t["CDaR_0.95"] < bc_t["CDaR_0.95"])
gate_B = {"best_cell": f"E{best_em}_X{best_xm}", "yearly_sign_agree": agree, "yearly_total": len(yearly),
          "bar_4of5": bool(agree >= 4), "survives_excising_final_106": survives_trim,
          "GATE_B_PASS": bool(agree >= 4 and survives_trim)}
print("\n=== GATE B (best cell) ===\n" + json.dumps(gate_B, indent=2), flush=True)
print(yearly.to_string(index=False), flush=True)

# ============================================================== gate C plateau
def neighbors(em, xm):
    ei = ENTRY_GRID.index(em); xi = EXIT_GRID.index(xm)
    out = []
    for de in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if de == 0 and dx == 0:
                continue
            nei, nxi = ei + de, xi + dx
            if 0 <= nei < len(ENTRY_GRID) and 0 <= nxi < len(EXIT_GRID):
                out.append((ENTRY_GRID[nei], EXIT_GRID[nxi]))
    return out

nbrs = neighbors(best_em, best_xm)
nbr_rows = []
n_direction_agree = 0
for (e, x) in nbrs:
    r = cell_results[(e, x)]
    agree_dir = bool(r["gate_sharpe"] and r["gate_CDaR"])  # both prongs same direction as best cell
    n_direction_agree += int(agree_dir)
    nbr_rows.append({"entry_mult": e, "exit_mult": x, "d_sharpe": r["d_sharpe"],
                      "d_CDaR_pos_better": r["d_CDaR_pos_better"], "both_prongs_positive": agree_dir})
nbr_df = pd.DataFrame(nbr_rows)
gate_C = {"best_cell": f"E{best_em}_X{best_xm}", "n_neighbors": len(nbrs),
          "n_neighbors_both_prongs_positive": n_direction_agree,
          "GATE_C_PLATEAU": bool(n_direction_agree >= 3)}
print("\n=== GATE C: PLATEAU (neighbor cells) ===")
print(nbr_df.to_string(index=False), flush=True)
print(json.dumps(gate_C, indent=2), flush=True)

# ============================================================== verdict
if bool(best_row["GATE_A_PASS"]) and gate_B["GATE_B_PASS"]:
    verdict = "CANDIDATE" if gate_C["GATE_C_PLATEAU"] else "REGIME-LOCAL/ISOLATED-OPTIMUM (gate C fails)"
else:
    verdict = "CONFIRMED-NOT-BENEFICIAL"
gates_out = {"best_cell": f"E{best_em}_X{best_xm}", "gate_A": bool(best_row["GATE_A_PASS"]),
             "gate_B": gate_B, "gate_C": gate_C, "VERDICT": verdict}
json.dump(gates_out, open(os.path.join(OUT, "gates.json"), "w"), indent=2)
grid_df.assign(is_best=lambda d: (d.entry_mult == best_em) & (d.exit_mult == best_xm)).to_csv(
    os.path.join(OUT, "gates.csv"), index=False)
print("\n=== VERDICT ===\n" + verdict, flush=True)
print("\n=== M3 DONE ===", flush=True)
