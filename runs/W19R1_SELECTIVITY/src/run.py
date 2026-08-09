"""W19R1_SELECTIVITY — run the frozen spec.yaml UNCHANGED (owner directive §5 S1: "Run the
already-frozen W19R1 spec unchanged first. Do not rewrite history."). D7-boundary split reporting
is added via a SEPARATE addendum section below, not by modifying gate logic.
"""
import os, sys, json, datetime as dt
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "runs", "W18R1_M1_VOLSEASON", "src"))
import sm01_solarsim as sm
from smv2_common import dd_battery
import common as C1
sys.path.insert(0, os.path.join(ROOT, "runs", "W19R1_SELECTIVITY", "src"))
import scores_transform as ST

RUN = os.path.join(ROOT, "runs", "W19R1_SELECTIVITY")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
DEV_END = dt.date(2026, 5, 29)
SEED, BLOCK, NBOOT = 20260809, 5, 10000   # Wave-19 seed convention (D7 used the same)

D7_BOUNDARY = "2024-08-05"   # weakly-identified CANDIDATE (red-team corrected); NOT authoritative
STUB_START = "2026-01-02"    # calendar convention, the 106-session P&L-concentration window


def battery(x):
    eqd = np.cumsum(x); dd = np.maximum.accumulate(eqd) - eqd
    k = max(1, int(0.05 * len(x)))
    sd = x.std(ddof=1)
    return {"n_days": len(x), "net": float(x.sum()),
            "sharpe": float(x.mean() / sd * np.sqrt(252)) if sd > 0 and len(x) > 1 else np.nan,
            "maxDD": float(dd.max()) if len(dd) else 0.0,
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
    idx = ((starts[:, :, None] + np.arange(block)[None, None, :]) % n).reshape(nboot, -1)[:, :n]
    return idx


def top10_retention(ctrl, arm):
    """House (control's top-10 dates) AND arm's-own (arm's top-10 dates) retention, both as
    arm-sum/control-sum ratios over the chosen date set — the W18R1 red team's disclosure."""
    idx_c = np.argsort(ctrl)[-10:]
    house = float(arm[idx_c].sum() / ctrl[idx_c].sum()) if ctrl[idx_c].sum() != 0 else np.nan
    idx_a = np.argsort(arm)[-10:]
    own = float(arm[idx_a].sum() / ctrl[idx_a].sum()) if ctrl[idx_a].sum() != 0 else np.nan
    return house, own


# ============================================================== 1. NQ bars, control T
bars = C1.load_dev_bars()
n = len(bars)
sess = bars["sess_date"].to_numpy()
close = bars["close"].to_numpy()
sig460 = sm.sigma_series(close)
PEND_ctrl = C1.build_pend(bars, sig460)
T = sm.e10_target(PEND_ctrl)   # unmodified incumbent E10 target, UNCHANGED by either arm

daily_ctrl, barpos_ctrl, barpnl_ctrl = C1.e10_exec(bars, T)
# cross-check vs the frozen reference curve (spec §2 control clause)
ref_path = os.path.join(ROOT, "runs", "SMV2AD_VOLMULT_CEILING", "out", "e10_daily_dev_control_1200.csv")
ref = pd.read_csv(ref_path)
ref["sess"] = pd.to_datetime(ref["sess"]).dt.date.astype(str)
mine = daily_ctrl.copy(); mine["sess"] = mine["sess"].astype(str)
mrg = mine.merge(ref, on="sess", suffixes=("", "_ref"))
crosscheck = {"n_matched": int(len(mrg)), "n_mine": int(len(mine)), "n_ref": int(len(ref)),
              "max_abs_diff": float((mrg["net"] - mrg["net_ref"]).abs().max()) if len(mrg) else None,
              "PASS": bool(len(mrg) == len(mine) == len(ref) and
                           (mrg["net"] - mrg["net_ref"]).abs().max() < 0.01)}
json.dump(crosscheck, open(os.path.join(OUT, "control_crosscheck.json"), "w"), indent=2)
print("=== CONTROL CROSSCHECK ===\n" + json.dumps(crosscheck, indent=2), flush=True)
assert crosscheck["PASS"], "control does not reproduce the frozen reference curve — STOP"

# ============================================================== 2. scores
s_ER = ST.er150_score(bars)
s_TOD, tod_disclosure, tod_score_by_cohort, tod_avg_frac = ST.tod_score_from_xinst(bars, DEV_END)
np.save(os.path.join(OUT, "scores.npy"), np.column_stack([s_ER, s_TOD]))
tod_disclosure.to_csv(os.path.join(OUT, "tod_source_cohorts.csv"), index=False)
print("=== arm_TOD cohort scores (from ES/RTY/YM P&L only) ===")
print(json.dumps({"avg_pnl_fraction": tod_avg_frac, "rank_score": tod_score_by_cohort}, indent=2), flush=True)

# ============================================================== 3. transforms + execution
ARMS_META = {}
T_ER, g_raw_ER, g_final_ER, sbar_ER = ST.exposure_neutral_transform(sess, T, s_ER)
T_TOD, g_raw_TOD, g_final_TOD, sbar_TOD = ST.exposure_neutral_transform(sess, T, s_TOD)

daily_ER, barpos_ER, barpnl_ER = C1.e10_exec(bars, T_ER)
daily_TOD, barpos_TOD, barpnl_TOD = C1.e10_exec(bars, T_TOD)

for label, d in (("control", daily_ctrl), ("arm_ER", daily_ER), ("arm_TOD", daily_TOD)):
    d.to_csv(os.path.join(OUT, f"daily_{label}.csv"), index=False)

CURVES = {
    "control": daily_ctrl.set_index(daily_ctrl["sess"].astype(str))["net"],
    "arm_ER": daily_ER.set_index(daily_ER["sess"].astype(str))["net"],
    "arm_TOD": daily_TOD.set_index(daily_TOD["sess"].astype(str))["net"],
}
CAL = CURVES["control"].index

# ============================================================== 4. GATE 0 — exposure neutrality
exp_rows = []
for label, Tp in (("arm_ER", T_ER), ("arm_TOD", T_TOD)):
    ratio_sumT = float(np.abs(Tp).sum() / np.abs(T).sum())
    dctr = {"arm_ER": daily_ER, "arm_TOD": daily_TOD}[label]
    mean_contracts_arm = float(dctr["contracts"].mean())
    mean_contracts_ctrl = float(daily_ctrl["contracts"].mean())
    ratio_contracts = mean_contracts_arm / mean_contracts_ctrl
    clamp_pinned_arm = float((np.abs(Tp) == 10).mean() * 100)
    clamp_pinned_ctrl = float((np.abs(T) == 10).mean() * 100)
    valid = bool(abs(ratio_sumT - 1) <= 0.05 and abs(ratio_contracts - 1) <= 0.05)
    exp_rows.append({
        "arm": label, "sum_absT_ratio_vs_control": ratio_sumT,
        "mean_contracts_per_day_arm": mean_contracts_arm,
        "mean_contracts_per_day_control": mean_contracts_ctrl,
        "contracts_ratio_vs_control": ratio_contracts,
        "clamp_pinned_pct_arm": clamp_pinned_arm, "clamp_pinned_pct_control": clamp_pinned_ctrl,
        "GATE_0_VALID_SELECTIVITY_TEST": valid,
    })
    ARMS_META[label] = {"valid_gate0": valid}
exposure_check_df = pd.DataFrame(exp_rows)
exposure_check_df.to_csv(os.path.join(OUT, "exposure_check.csv"), index=False)
print("\n=== GATE 0: EXPOSURE NEUTRALITY (INVALIDATION, checked first) ===")
print(exposure_check_df.to_string(index=False), flush=True)

# ============================================================== 5. GATE A — legacy triple
ctrl_x = CURVES["control"].to_numpy()
gate_rows = []
for label in ("arm_ER", "arm_TOD"):
    x = CURVES[label].reindex(CAL).to_numpy()
    bc = battery(ctrl_x); ba = battery(x)
    house_ret, own_ret = top10_retention(ctrl_x, x)
    g_sharpe = bool(ba["sharpe"] > bc["sharpe"])
    g_cdar = bool(ba["CDaR_0.95"] < bc["CDaR_0.95"])
    g_top10 = bool(house_ret >= 0.95)
    gate_rows.append({
        "arm": label, "sharpe_arm": ba["sharpe"], "sharpe_control": bc["sharpe"],
        "d_sharpe": ba["sharpe"] - bc["sharpe"],
        "CDaR_arm": ba["CDaR_0.95"], "CDaR_control": bc["CDaR_0.95"],
        "d_CDaR_pos_is_better": bc["CDaR_0.95"] - ba["CDaR_0.95"],
        "top10_retention_HOUSE_control_dates": house_ret,
        "top10_retention_arm_own_dates": own_ret,
        "net_arm": ba["net"], "net_control": bc["net"],
        "gate_sharpe": g_sharpe, "gate_CDaR": g_cdar, "gate_top10_house": g_top10,
        "GATE_0_VALID": ARMS_META[label]["valid_gate0"],
        "GATE_A_AND_RULE_PASS": bool(g_sharpe and g_cdar and g_top10 and ARMS_META[label]["valid_gate0"]),
    })
gates_A = pd.DataFrame(gate_rows)
print("\n=== GATE A: LEGACY TRIPLE ===")
print(gates_A.to_string(index=False), flush=True)

# ============================================================== 6. GATE B — chronology
def yearly_dsharpe(ctrl_s, arm_s):
    df = pd.DataFrame({"c": ctrl_s, "a": arm_s})
    df.index = pd.to_datetime(df.index)
    df["year"] = df.index.year
    rows = []
    for y, g in df.groupby("year"):
        bc = battery(g["c"].to_numpy()); ba = battery(g["a"].to_numpy())
        rows.append({"year": int(y), "n_days": len(g), "sharpe_control": bc["sharpe"],
                     "sharpe_arm": ba["sharpe"], "d_sharpe": ba["sharpe"] - bc["sharpe"],
                     "sign_positive": bool(ba["sharpe"] - bc["sharpe"] > 0)})
    return pd.DataFrame(rows)

yearly_all = {}
gate_B_rows = []
for label in ("arm_ER", "arm_TOD"):
    x = CURVES[label].reindex(CAL)
    yt = yearly_dsharpe(CURVES["control"], x)
    yearly_all[label] = yt
    agree = int(yt["sign_positive"].sum()); total = len(yt)
    # excise final 106 sessions, re-check gate A survives
    cal_sorted = sorted(CAL)
    trimmed_cal = cal_sorted[:-106]
    bc_t = battery(CURVES["control"].reindex(trimmed_cal).to_numpy())
    ba_t = battery(x.reindex(trimmed_cal).to_numpy())
    survives_trim = bool(ba_t["sharpe"] > bc_t["sharpe"] and ba_t["CDaR_0.95"] < bc_t["CDaR_0.95"])
    gate_B_rows.append({
        "arm": label, "yearly_sign_agree": agree, "yearly_total": total,
        "yearly_bar_4of5": bool(agree >= 4),
        "survives_excising_final_106_sessions": survives_trim,
        "GATE_B_PASS": bool(agree >= 4 and survives_trim),
    })
gates_B = pd.DataFrame(gate_B_rows)
print("\n=== GATE B: CHRONOLOGY ===")
print(gates_B.to_string(index=False), flush=True)
pd.concat([yt.assign(arm=lbl) for lbl, yt in yearly_all.items()]).to_csv(
    os.path.join(OUT, "yearly.csv"), index=False)

# ============================================================== 7. bootstrap disclosure
idx = block_bootstrap_idx(len(CAL), BLOCK, NBOOT, SEED)
boot = {}
for label in ("arm_ER", "arm_TOD"):
    xc = CURVES["control"].reindex(CAL).to_numpy()
    xa = CURVES[label].reindex(CAL).to_numpy()
    k5 = max(1, int(0.05 * len(xc)))
    sc, dc = path_stats(xc, idx, k5)
    sa, da = path_stats(xa, idx, k5)
    d_sh = sa - sc
    d_cdr_ratio = (dc - da) / dc
    boot[label] = {
        "P_dSharpe_gt0": float((d_sh > 0).mean()), "P_dCDaR_ratio_gt0": float((d_cdr_ratio > 0).mean()),
        "q05_dSharpe": float(np.quantile(d_sh, 0.05)), "q95_dSharpe": float(np.quantile(d_sh, 0.95)),
        "q05_dCDaR_ratio": float(np.quantile(d_cdr_ratio, 0.05)),
        "q95_dCDaR_ratio": float(np.quantile(d_cdr_ratio, 0.95)),
        "seed": SEED, "block": BLOCK, "nboot": NBOOT,
    }
json.dump(boot, open(os.path.join(OUT, "bootstrap.json"), "w"), indent=2)
print("\n=== BOOTSTRAP (block=5, B=10000, seed=20260809) ===\n" + json.dumps(boot, indent=2), flush=True)

# ============================================================== 8. recency tiers (disclosure)
tiers = {"full_dev": ("2022-01-03", "2026-05-29"),
         "trailing_2yr": ("2024-05-30", "2026-05-29"),
         "trailing_1yr": ("2025-05-30", "2026-05-29")}
tr = []
for label in ("control", "arm_ER", "arm_TOD"):
    s = CURVES[label]
    for tname, (a, b) in tiers.items():
        x = s[(s.index >= a) & (s.index <= b)].to_numpy()
        bt = battery(x)
        tr.append({"arm": label, "tier": tname, "basis": "CONTINUATION (V7 §F)",
                   "n_days": len(x), "net": bt["net"], "sharpe": bt["sharpe"], "CDaR_0.95": bt["CDaR_0.95"]})
pd.DataFrame(tr).to_csv(os.path.join(OUT, "recency_tiers.csv"), index=False)

# ============================================================== 9. GATE C — cross-instrument (arm_ER only)
# NQ row uses the standard incumbent MNQ-E10-executable economics (C1.e10_exec defaults) — the
# SAME economics as the main control/arm_ER curves above — so it doubles as an internal
# consistency cross-check (recomputed independently here; must match the main gate_A row).
xinst_rows = []
for name in ("NQ",) + tuple(ST.XINST.keys()):
    old_tick = None
    if name == "NQ":
        b_i, sig_i, Ti = bars, sig460, T
        comm_i, pv_i = sm.MNQ_COMM_SIDE, sm.MNQ_POINT_VALUE
    else:
        path, tick, pv = ST.XINST[name]
        b_i = sm.load_bars_3m(path); b_i = b_i[b_i["sess_date"] <= DEV_END].reset_index(drop=True)
        sig_i = sm.sigma_series(b_i["close"].to_numpy())
        old_tick = sm.TICK; sm.TICK = tick
        PEND_i = C1.build_pend(b_i, sig_i)
        Ti = sm.e10_target(PEND_i)
        comm_i, pv_i = ST.COMM_SIDE_XINST, pv
    try:
        s_ER_i = ST.er150_score(b_i)
        sess_i = b_i["sess_date"].to_numpy()
        Tp_i, *_ = ST.exposure_neutral_transform(sess_i, Ti, s_ER_i)
        d_ctrl_i, _, _ = C1.e10_exec(b_i, Ti, comm_side=comm_i, point_value=pv_i)
        d_arm_i, _, _ = C1.e10_exec(b_i, Tp_i, comm_side=comm_i, point_value=pv_i)
    finally:
        if old_tick is not None:
            sm.TICK = old_tick
    bc_i = battery(d_ctrl_i["net"].to_numpy()); ba_i = battery(d_arm_i["net"].to_numpy())
    xinst_rows.append({
        "instrument": name, "role": "KNOWN" if name == "NQ" else "NEW",
        "sharpe_control": bc_i["sharpe"], "sharpe_arm": ba_i["sharpe"], "d_sharpe": ba_i["sharpe"] - bc_i["sharpe"],
        "CDaR_control": bc_i["CDaR_0.95"], "CDaR_arm": ba_i["CDaR_0.95"],
        "d_CDaR_ratio": (bc_i["CDaR_0.95"] - ba_i["CDaR_0.95"]) / bc_i["CDaR_0.95"] if bc_i["CDaR_0.95"] else np.nan,
        "sign_agree_both": bool((ba_i["sharpe"] - bc_i["sharpe"]) > 0 and
                                 ((bc_i["CDaR_0.95"] - ba_i["CDaR_0.95"]) / bc_i["CDaR_0.95"] > 0 if bc_i["CDaR_0.95"] else False)),
    })
xinst_df = pd.DataFrame(xinst_rows)
xinst_df.to_csv(os.path.join(OUT, "xinst.csv"), index=False)
_nq_row = xinst_df.set_index("instrument").loc["NQ"]
_main_row = gates_A.set_index("arm").loc["arm_ER"]
assert abs(_nq_row["d_sharpe"] - _main_row["d_sharpe"]) < 1e-6, (
    "internal consistency check FAILED: gate C's independently-recomputed NQ arm_ER result "
    f"({_nq_row['d_sharpe']}) does not match the main gate_A d_sharpe ({_main_row['d_sharpe']})")
new_sign_agree = int(xinst_df.loc[xinst_df.role == "NEW", "sign_agree_both"].sum())
gate_C_pass = bool(new_sign_agree >= 2)
print("\n=== GATE C: CROSS-INSTRUMENT (arm_ER only; NQ is KNOWN, excluded from the count) ===")
print(xinst_df.to_string(index=False), flush=True)
print(f"new_instruments_sign_agree={new_sign_agree}/3  GATE_C_PASS={gate_C_pass}", flush=True)

# ============================================================== 10. VERDICT (frozen rule)
verdicts = {}
for label in ("arm_ER", "arm_TOD"):
    a_row = gates_A.set_index("arm").loc[label]
    b_row = gates_B.set_index("arm").loc[label]
    if label == "arm_ER":
        passed = bool(a_row["GATE_A_AND_RULE_PASS"] and b_row["GATE_B_PASS"] and gate_C_pass)
        gate_c_note = f"BINDING: new-instrument sign agreement {new_sign_agree}/3, bar 2/3"
    else:
        passed = bool(a_row["GATE_A_AND_RULE_PASS"] and b_row["GATE_B_PASS"])
        gate_c_note = "NON-BINDING for arm_TOD (circular by construction, declared in spec §3)"
    verdicts[label] = {
        "gate_0": bool(a_row["GATE_0_VALID"]), "gate_A": bool(a_row["GATE_A_AND_RULE_PASS"]),
        "gate_B": bool(b_row["GATE_B_PASS"]), "gate_C_note": gate_c_note,
        "VERDICT": "CANDIDATE" if passed else "CONFIRMED-NOT-BENEFICIAL",
    }
json.dump(verdicts, open(os.path.join(OUT, "verdict.json"), "w"), indent=2)
print("\n=== VERDICT (frozen rule) ===\n" + json.dumps(verdicts, indent=2), flush=True)

# ============================================================== 11. ADDENDUM — D7-boundary split
# Preregistered SEPARATELY (owner directive §5 S1), NOT a modification of the frozen gates above.
addendum_rows = []
for label in ("arm_ER", "arm_TOD"):
    xa_full = CURVES[label].reindex(CAL)
    xc_full = CURVES["control"].reindex(CAL)
    splits = {
        "pre_D7_boundary_2024-08-05": (None, "2024-08-04"),
        "post_D7_boundary_2024-08-05": ("2024-08-05", None),
        "pre_2026-01-02_convention": (None, "2026-01-01"),
        "post_2026-01-02_convention_stub": ("2026-01-02", None),
    }
    for sname, (a, b) in splits.items():
        idx_ = xa_full.index
        if a: idx_ = idx_[idx_ >= a]
        if b: idx_ = idx_[idx_ <= b]
        if len(idx_) < 5:
            continue
        bc = battery(xc_full.reindex(idx_).to_numpy()); ba = battery(xa_full.reindex(idx_).to_numpy())
        addendum_rows.append({"arm": label, "split": sname, "n_days": len(idx_),
                               "sharpe_control": bc["sharpe"], "sharpe_arm": ba["sharpe"],
                               "d_sharpe": ba["sharpe"] - bc["sharpe"],
                               "CDaR_control": bc["CDaR_0.95"], "CDaR_arm": ba["CDaR_0.95"]})
    # calendar-year splits already in yearly.csv (yearly_all[label]); referenced, not duplicated.
addendum_df = pd.DataFrame(addendum_rows)
addendum_df.to_csv(os.path.join(OUT, "addendum_d7_split.csv"), index=False)
print("\n=== ADDENDUM: D7-BOUNDARY / STUB SPLIT (separate preregistration, not a gate) ===")
print(addendum_df.to_string(index=False), flush=True)

print("\n=== DONE ===", flush=True)
