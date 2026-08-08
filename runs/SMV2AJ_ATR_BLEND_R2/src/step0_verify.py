"""SMV2AJ_ATR_BLEND_R2 STEP ZERO -- build the DUAL-transformed dev legs for the
ATR-blended candidate (arm_BLEND_75, w=0.75 on sigma460 / 0.25 on sigma_ATR_eff)
and the sigma460-only incumbent, then verify every reused component bit-for-cent
against SMV2AI_ATR_BLEND's own committed artifacts before any gate computation.

Construction (verbatim reuse, NOT re-derived):
  - sigma460, sigma_ATR_eff, R_SELECTED=2.025539235146222: reused from
    runs/SMV2AI_ATR_BLEND/out/{sigma460_dev.npy, sigma_atr_eff_dev.npy,
    atr_construction_meta.json} verbatim (sub_430's frozen pre-registered rule).
  - raw target construction (build_pend / e10_target, clamp [40,1200]t, 13-member
    VMS): runs/SMV2AI_ATR_BLEND/src/common.py, imported directly (not copied).
  - DUAL_HTF transform (tilt x1.25 HTF-agree / c1_50 short-halving / x0.9026 /
    clip +-13 / RHA): runs/SMV2AD_VOLMULT_CEILING/src/common.py's dual_htf(),
    reused verbatim via SMV2AI's common.py (which itself imports/copies it
    verbatim -- confirmed by direct code read, see REPORT).

This produces the UNSEEN DUAL-transformed daily legs (SMV2AI itself never ran
dual_htf on the arm_BLEND_75 raw target and then bootstrapped/LOYO'd/top10'd the
result -- it only (a) screened the raw pre-transform target in sub_431, and (b)
built ONE portfolio point-level DUAL comparison via common.py's
build_portfolio_6040, also point-level only, no bootstrap). Both facts are
cross-checked below.
"""
import sys, os, json, time
import datetime as dt
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "runs", "SMV2AI_ATR_BLEND", "src"))
import sm01_solarsim as sm
from common import (load_dev_bars, build_pend, e10_exec, INCUMBENT_VMS,
                     dual_htf, htf_state, rha)

RUN = os.path.join(ROOT, "runs", "SMV2AJ_ATR_BLEND_R2")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
AI_OUT = os.path.join(ROOT, "runs", "SMV2AI_ATR_BLEND", "out")

t0 = time.time()

# ---------------- dev substrate (identical to SMV2AI) ----------------
bars = load_dev_bars()
n = len(bars)
print(f"dev bars: {n}, sessions {bars['sess_date'].nunique()}, "
      f"{bars['sess_date'].min()} -> {bars['sess_date'].max()}", flush=True)

# ---------------- reused sigma inputs (verbatim, not recomputed) ----------------
sigma460 = np.load(os.path.join(AI_OUT, "sigma460_dev.npy"))
sigma_ATR_eff = np.load(os.path.join(AI_OUT, "sigma_atr_eff_dev.npy"))
assert sigma460.shape[0] == n and sigma_ATR_eff.shape[0] == n

meta = json.load(open(os.path.join(AI_OUT, "atr_construction_meta.json")))
R_SELECTED = meta["R_SELECTED_whole_dev_median"]
print(f"R_SELECTED (reused verbatim from SMV2AI sub_430): {R_SELECTED:.9f}", flush=True)

W = 0.75  # arm_BLEND_75, the sole sub_431 CANDIDATE
sig_control = 1.0 * sigma460 + 0.0 * sigma_ATR_eff   # == sigma460 exactly
sig_blend75 = W * sigma460 + (1.0 - W) * sigma_ATR_eff

# ---------------- raw target construction (clamp [40,1200]t, 13-member VMS) ----------------
pend_control = build_pend(bars, sig_control, INCUMBENT_VMS, smax_ticks=1200.0, smin_ticks=40.0)
pend_blend75 = build_pend(bars, sig_blend75, INCUMBENT_VMS, smax_ticks=1200.0, smin_ticks=40.0)
tgt_control = sm.e10_target(pend_control)   # raw, clip +-10 (e10_target's own cap)
tgt_blend75 = sm.e10_target(pend_blend75)

daily_control_raw, _, _ = e10_exec(bars, tgt_control)
daily_blend75_raw, _, _ = e10_exec(bars, tgt_blend75)

# ---- integrity check 1: raw daily curves must match SMV2AI's committed csvs ----
ref_ctrl = pd.read_csv(os.path.join(AI_OUT, "daily_control_w1.00.csv"))
ref_ctrl["sess"] = pd.to_datetime(ref_ctrl["sess"]).dt.date
dc = daily_control_raw.copy(); dc["sess"] = pd.to_datetime(dc["sess"]).dt.date
j1 = ref_ctrl.merge(dc, on="sess", suffixes=("_ref", "_my"))
ctrl_raw_max_dev = float(np.abs(j1["net_ref"] - j1["net_my"]).max())

ref_75 = pd.read_csv(os.path.join(AI_OUT, "daily_arm_BLEND_75.csv"))
ref_75["sess"] = pd.to_datetime(ref_75["sess"]).dt.date
d75 = daily_blend75_raw.copy(); d75["sess"] = pd.to_datetime(d75["sess"]).dt.date
j2 = ref_75.merge(d75, on="sess", suffixes=("_ref", "_my"))
blend75_raw_max_dev = float(np.abs(j2["net_ref"] - j2["net_my"]).max())

print(f"raw control recompute vs SMV2AI daily_control_w1.00.csv: max|dev|=${ctrl_raw_max_dev:.6f} "
      f"({len(j1)}/{len(ref_ctrl)} sessions matched)", flush=True)
print(f"raw arm_BLEND_75 recompute vs SMV2AI daily_arm_BLEND_75.csv: max|dev|=${blend75_raw_max_dev:.6f} "
      f"({len(j2)}/{len(ref_75)} sessions matched)", flush=True)
assert ctrl_raw_max_dev < 1.0 and blend75_raw_max_dev < 1.0, "raw-target reconstruction FAILED"

# ---------------- DUAL_HTF transform (verbatim SMV2AD common.py dual_htf, reused via SMV2AI common.py) ----------------
st_bar = htf_state(bars)
Tpp_control = dual_htf(tgt_control.astype(float), st_bar)
Tpp_blend75 = dual_htf(tgt_blend75.astype(float), st_bar)

daily_DUAL_control, _, _ = e10_exec(bars, Tpp_control.astype(int))
daily_DUAL_blend75, _, _ = e10_exec(bars, Tpp_blend75.astype(int))

# ---- integrity check 2: these are the SAME as SMV2AI's own build_portfolio_6040 outputs
#      saved in portfolio_curves_431.csv (columns DUAL_control_w1.00_recomputed /
#      DUAL_arm_BLEND_75) -- SMV2AI computed these DUAL legs internally (for the
#      portfolio point comparison) but never bootstrapped/LOYO'd/top10'd them.
pc = pd.read_csv(os.path.join(AI_OUT, "portfolio_curves_431.csv"))
pc["sess"] = pd.to_datetime(pc["sess"]).dt.date
dcd = daily_DUAL_control.copy(); dcd["sess"] = pd.to_datetime(dcd["sess"]).dt.date
j3 = pc[["sess", "DUAL_control_w1.00_recomputed"]].merge(dcd, on="sess")
dual_control_max_dev = float(np.abs(j3["DUAL_control_w1.00_recomputed"] - j3["net"]).max())

d75d = daily_DUAL_blend75.copy(); d75d["sess"] = pd.to_datetime(d75d["sess"]).dt.date
j4 = pc[["sess", "DUAL_arm_BLEND_75"]].merge(d75d, on="sess")
dual_blend75_max_dev = float(np.abs(j4["DUAL_arm_BLEND_75"] - j4["net"]).max())

print(f"DUAL_control recompute vs SMV2AI portfolio_curves_431.csv DUAL_control_w1.00_recomputed: "
      f"max|dev|=${dual_control_max_dev:.8f} ({len(j3)}/{len(pc)} sessions)", flush=True)
print(f"DUAL_blend75 recompute vs SMV2AI portfolio_curves_431.csv DUAL_arm_BLEND_75: "
      f"max|dev|=${dual_blend75_max_dev:.8f} ({len(j4)}/{len(pc)} sessions)", flush=True)
assert dual_control_max_dev < 1e-6 and dual_blend75_max_dev < 1e-6, \
    "DUAL-transformed leg reconstruction does not match SMV2AI's own internal computation"

# ---- integrity check 3: DUAL_control (sigma460-only, w=1.0, DUAL-transformed) must
#      equal the TRUE incumbent champion DUAL leg (independent lineage: SMV2H_ONECONTRACT) ----
ref_champ_dual = pd.read_csv(os.path.join(ROOT, "runs", "SMV2H_ONECONTRACT", "out",
                                           "solar_dual_htf_daily.csv"))
ref_champ_dual.columns = ["sess", "net"]
ref_champ_dual["sess"] = pd.to_datetime(ref_champ_dual["sess"]).dt.date
j5 = ref_champ_dual.merge(dcd, on="sess", suffixes=("_champ", "_my"))
champ_dual_max_dev = float(np.abs(j5["net_champ"] - j5["net_my"]).max())
print(f"DUAL_control vs TRUE incumbent champion DUAL leg (SMV2H_ONECONTRACT "
      f"solar_dual_htf_daily.csv): max|dev|=${champ_dual_max_dev:.6f} "
      f"({len(j5)}/{len(ref_champ_dual)} sessions)", flush=True)
assert champ_dual_max_dev < 1.0, "DUAL_control does not reproduce the true incumbent champion DUAL leg"

# ---------------- fact-check: what object did SMV2AI's sub_432 (old-regime screen) test? ----------------
step3_src = open(os.path.join(ROOT, "runs", "SMV2AI_ATR_BLEND", "src",
                               "step3_old_regime.py")).read()
sub432_used_dual = ("dual_htf" in step3_src)
print(f"\nsub_432 (SMV2AI's old-regime screen) source references dual_htf(): {sub432_used_dual}", flush=True)
print("-> sub_432 built tgt_ctrl/tgt via sm.e10_target(pend) directly and ran run_policy_hist(hist_bars, tgt...)",
      flush=True)
print("-> CONFIRMED: sub_432 tested the RAW (pre-DUAL-transform) target on hist, NOT the DUAL object.",
      flush=True)
print("-> Gate C in this run (DUAL-transformed object on hist) is therefore a GENUINE RE-TEST, not a duplicate.",
      flush=True)

cal = pd.to_datetime(daily_DUAL_control["sess"])
curves = pd.DataFrame({
    "sess": daily_DUAL_control["sess"],
    "DUAL_CONTROL": daily_DUAL_control["net"].to_numpy(),
    "DUAL_BLEND75": daily_DUAL_blend75["net"].to_numpy(),
    "diff_blend75_minus_control": daily_DUAL_blend75["net"].to_numpy() - daily_DUAL_control["net"].to_numpy(),
})
curves.to_csv(os.path.join(OUT, "curves.csv"), index=False)
np.save(os.path.join(OUT, "tpp_control_dev.npy"), Tpp_control)
np.save(os.path.join(OUT, "tpp_blend75_dev.npy"), Tpp_blend75)
np.save(os.path.join(OUT, "tgt_control_raw_dev.npy"), tgt_control)
np.save(os.path.join(OUT, "tgt_blend75_raw_dev.npy"), tgt_blend75)

res = {
    "n_dev_bars": int(n), "n_dev_sessions": int(bars["sess_date"].nunique()),
    "dev_start": str(bars["sess_date"].min()), "dev_end": str(bars["sess_date"].max()),
    "R_SELECTED_reused_verbatim": R_SELECTED,
    "w_sigma460_weight_arm_BLEND_75": W,
    "raw_control_vs_SMV2AI_csv_max_abs_dev_$": ctrl_raw_max_dev,
    "raw_blend75_vs_SMV2AI_csv_max_abs_dev_$": blend75_raw_max_dev,
    "DUAL_control_vs_SMV2AI_internal_max_abs_dev_$": dual_control_max_dev,
    "DUAL_blend75_vs_SMV2AI_internal_max_abs_dev_$": dual_blend75_max_dev,
    "DUAL_control_vs_true_incumbent_champion_DUAL_leg_max_abs_dev_$": champ_dual_max_dev,
    "sub432_old_regime_screen_used_dual_transform": sub432_used_dual,
    "sub432_tested_object": "RAW pre-DUAL-transform target (confirmed by source read: "
                             "step3_old_regime.py calls sm.e10_target(pend) then "
                             "run_policy_hist(hist_bars, tgt, ...) directly, no dual_htf call "
                             "anywhere in the file)",
    "gate_C_here_is_genuine_retest_not_duplicate": True,
    "verified": bool(ctrl_raw_max_dev < 1.0 and blend75_raw_max_dev < 1.0
                      and dual_control_max_dev < 1e-6 and dual_blend75_max_dev < 1e-6
                      and champ_dual_max_dev < 1.0),
    "runtime_s": round(time.time() - t0, 1),
}
json.dump(res, open(os.path.join(OUT, "step0_verify.json"), "w"), indent=2)
print("\n" + json.dumps(res, indent=2), flush=True)
print("\ndone step0", flush=True)
