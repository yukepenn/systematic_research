"""SMV2AK sub_440 -- ensemble test (1 arm vs 3m-incumbent control).
VMS_volbar = VMS_3m * R_volbar (13 members, same relative spacing), clamp
bounds [40,1200] ticks UNCHANGED (absolute price-space bounds, not
sigma-relative -- same reasoning as every prior rescale in this program),
sigma window = N from sub_439 (fed via sub_439's own sigma_volbar_dev.npy,
not recomputed), MNQ E10 executor, session flatten.

Reports standalone net/Sharpe/maxDD/CDaR_0.95/top10-day-sum/turnover/
friction-share vs the 3m-incumbent control; portfolio blend (DAYONLY_DUAL6040
60/40, Solar leg swapped via the DUAL_HTF transform -- common.py's
dual_htf()/vm()/build_portfolio_6040(), reused verbatim from
runs/SMV2AD_VOLMULT_CEILING/src/common.py, B-MOM leg unchanged).

verdict rule (CANDIDATE): standalone Sharpe AND CDaR_0.95 improve vs the 3m
control AND top-10-day retention >=95% (same AND-rule as every core-challenge
spec this wave-class). No adoption this wave regardless of outcome.

Calendar note (disclosed): the volume-bar dev calendar carries 1 extra
session-date fragment (2022-11-06, a 60-minute gap-split artifact of the raw
1m feed around the US fall DST transition -- see sub_438's disclosure) that
the 3m control's calendar does not have. All comparison metrics below are
computed on the INTERSECTION (the control's 1139-session calendar); the extra
fragment is dropped from the volume-bar arm for apples-to-apples comparison,
not silently included or used to inflate any metric.
"""
import os, sys, json, time
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from common import (ROOT, OUT, load_dev_bars_3m, build_pend, e10_exec, metric_row,
                     INCUMBENT_VMS, build_portfolio_6040, champion_curve, dd_battery)
import sm01_solarsim as sm

TICK = sm.TICK
MNQ_PV = sm.MNQ_POINT_VALUE
MNQ_COMM = sm.MNQ_COMM_SIDE
FRICTION_PER_CONTRACT_SIDE = TICK * MNQ_PV + MNQ_COMM  # SAME def as SMV2AE: 1-tick adverse slip $ + commission, per side

t0 = time.time()

# ------------------------------------------------------------------ 0. R_volbar, N from sub_439 (frozen)
meta_v = json.load(open(os.path.join(OUT, "scale_ratio_volbar_meta.json")))
R_volbar = meta_v["R_SELECTED_whole_dev_median"]
N_volbar = meta_v["N_volume_bars"]
print(f"R_volbar (sub_439 whole-dev median, pre-registered) = {R_volbar:.6f}, N = {N_volbar}",
      flush=True)

meta_V = json.load(open(os.path.join(OUT, "V_frozen.json")))
V = meta_V["V_frozen"]
print(f"V (sub_438 pre-registered) = {V:.4f}", flush=True)

VMS_VOLBAR = [v * R_volbar for v in sm.VMS]
print(f"VMS_volbar (rescaled, 13 members) = {[round(v, 4) for v in VMS_VOLBAR]}", flush=True)

# ------------------------------------------------------------------ 1. load substrates
bars3_dev = load_dev_bars_3m()
n3 = len(bars3_dev)
CAL = pd.to_datetime(sorted(bars3_dev["sess_date"].unique()))
n_cal = len(CAL)
print(f"3m dev control calendar: {n_cal} sessions ({CAL.min().date()} -> {CAL.max().date()})",
      flush=True)

volbars = pd.read_parquet(os.path.join(OUT, "volbars_dev.parquet"))
sig_volbar = np.load(os.path.join(OUT, "sigma_volbar_dev.npy"))
sig3_cached = np.load(os.path.join(ROOT, "runs", "SMV2R_SOLAR_CORE_1", "out",
                                    "cache_incumbent.npz"))["sigma460"]
assert len(sig3_cached) == n3 and len(sig_volbar) == len(volbars)

# ------------------------------------------------------------------ 2. control (3m incumbent), recomputed + cross-checked
pend_ctrl = build_pend(bars3_dev, sig3_cached, INCUMBENT_VMS, smax_ticks=1200.0, smin_ticks=40.0)
tgt_ctrl = sm.e10_target(pend_ctrl)
daily_ctrl, _, _ = e10_exec(bars3_dev, tgt_ctrl)
daily_ctrl["sess"] = pd.to_datetime(daily_ctrl["sess"])

reused_ctrl = pd.read_csv(os.path.join(ROOT, "runs", "SMV2AD_VOLMULT_CEILING", "out",
                                        "e10_daily_dev_control_1200.csv"))
reused_ctrl["sess"] = pd.to_datetime(reused_ctrl["sess"])
j = reused_ctrl.merge(daily_ctrl, on="sess", suffixes=("_reused", "_recompute"))
max_dev_ctrl = float(np.abs(j["net_reused"] - j["net_recompute"]).max())
print(f"control cross-check vs SMV2AD reused csv: {len(j)}/{len(reused_ctrl)} sessions matched, "
      f"max|dev|=${max_dev_ctrl:.6f}", flush=True)
assert max_dev_ctrl < 1.0, f"control recompute does not match reused csv (max abs dev ${max_dev_ctrl:.2f})"

ctrl_series = daily_ctrl.set_index("sess")["net"].reindex(CAL)
assert ctrl_series.isna().sum() == 0, "control missing dev calendar sessions"
m_ctrl = metric_row("3m_incumbent_control", daily_ctrl, tgt_ctrl)

# ------------------------------------------------------------------ 3. volume-bar arm
pend_vb = build_pend(volbars, sig_volbar, VMS_VOLBAR, smax_ticks=1200.0, smin_ticks=40.0)
tgt_vb = sm.e10_target(pend_vb)
daily_vb, _, _ = e10_exec(volbars, tgt_vb)
daily_vb["sess"] = pd.to_datetime(daily_vb["sess"])

n_vb_sessions = daily_vb["sess"].nunique()
extra_dates = sorted(set(daily_vb["sess"]) - set(CAL))
print(f"volume-bar arm calendar: {n_vb_sessions} sessions; dates NOT in control calendar "
      f"(dropped for comparison, see module docstring) = {[d.date() for d in extra_dates]}",
      flush=True)

vb_full_series = daily_vb.set_index("sess")["net"]
vb_series = vb_full_series.reindex(CAL)
assert vb_series.isna().sum() == 0, "volume-bar arm missing a control-calendar session"
daily_vb_aligned = pd.DataFrame({"sess": CAL, "net": vb_series.values})
# turnover/tgt-change stats are computed on the FULL (unaligned) bar-level tgt array
# (dropping the extra session doesn't remove any bars, it's a bar-level series);
# contracts are re-derived on the aligned calendar for a like-for-like avg/day figure
daily_vb_aligned["contracts"] = daily_vb.set_index("sess")["contracts"].reindex(CAL).values
m_vb = metric_row("volbar_arm", daily_vb_aligned, tgt_vb)

print(f"\ncontrol (3m incumbent): net={m_ctrl['net']:.1f} sharpe={m_ctrl['sharpe']:.4f} "
      f"CDaR_0.95={m_ctrl['CDaR_0.95']:.1f} turnover%={m_ctrl['turnover_tgt_change_bars_pct']:.3f}",
      flush=True)
print(f"volbar arm:             net={m_vb['net']:.1f} sharpe={m_vb['sharpe']:.4f} "
      f"CDaR_0.95={m_vb['CDaR_0.95']:.1f} turnover%={m_vb['turnover_tgt_change_bars_pct']:.3f}",
      flush=True)

# ------------------------------------------------------------------ 4. friction share
for label, m, daily in [("3m_incumbent_control", m_ctrl, daily_ctrl),
                         ("volbar_arm", m_vb, daily_vb_aligned)]:
    total_contracts = float(daily["contracts"].sum())
    total_friction = total_contracts * FRICTION_PER_CONTRACT_SIDE
    gross = m["net"] + total_friction
    friction_share = total_friction / gross if gross != 0 else np.nan
    m.update({"total_contracts_traded_aligned_cal": total_contracts,
              "total_friction_$": total_friction, "gross_$": gross,
              "friction_share": friction_share})

# ------------------------------------------------------------------ 5. top-10-day retention (control's top10, same convention as SMV2AI)
top10 = ctrl_series.nlargest(10)
ret_vb = float(vb_series.reindex(top10.index).sum())
retention = ret_vb / float(top10.sum())
print(f"\ntop-10-day retention (control's top10 days, volbar arm's PnL on those SAME dates / "
      f"control's top10 sum) = {retention:.4f}", flush=True)

# ------------------------------------------------------------------ 6. verdict
d_sharpe = m_vb["sharpe"] - m_ctrl["sharpe"]
d_cdar = m_ctrl["CDaR_0.95"] - m_vb["CDaR_0.95"]  # + = challenger better (lower CDaR)
pass_sharpe = m_vb["sharpe"] > m_ctrl["sharpe"]
pass_cdar = m_vb["CDaR_0.95"] < m_ctrl["CDaR_0.95"]
pass_retention = retention >= 0.95
is_candidate = bool(pass_sharpe and pass_cdar and pass_retention)

ensemble_test = pd.DataFrame([
    {**m_ctrl, "role": "control"},
    {**m_vb, "role": "challenger",
     "d_sharpe_vs_control": d_sharpe, "d_CDaR_vs_control": d_cdar,
     "top10_day_retention_vs_control": retention,
     "pass_sharpe_improves": pass_sharpe, "pass_cdar_improves": pass_cdar,
     "pass_retention_ge_95pct": pass_retention, "CANDIDATE": is_candidate,
     "R_volbar_used": R_volbar, "N_volbar_used": N_volbar, "V_used": V},
])
ensemble_test.to_csv(os.path.join(OUT, "ensemble_test.csv"), index=False)
daily_ctrl.to_csv(os.path.join(OUT, "daily_control_3m.csv"), index=False)
daily_vb.to_csv(os.path.join(OUT, "daily_volbar_arm_full.csv"), index=False)
daily_vb_aligned.to_csv(os.path.join(OUT, "daily_volbar_arm_aligned.csv"), index=False)

print("\n=== ensemble_test.csv ===")
print(ensemble_test.to_string(index=False), flush=True)

sub440_verdict = {
    "rule": "CANDIDATE iff standalone Sharpe improves AND CDaR_0.95 improves (lower) vs the "
            "3m control AND top-10-day retention >= 95%.",
    "sharpe_control": m_ctrl["sharpe"], "sharpe_volbar": m_vb["sharpe"], "d_sharpe": d_sharpe,
    "cdar_control": m_ctrl["CDaR_0.95"], "cdar_volbar": m_vb["CDaR_0.95"], "d_cdar": d_cdar,
    "top10_day_retention": retention,
    "pass_sharpe_improves": bool(pass_sharpe), "pass_cdar_improves": bool(pass_cdar),
    "pass_retention_ge_95pct": bool(pass_retention),
    "CANDIDATE": bool(is_candidate),
}
with open(os.path.join(OUT, "sub440_verdict.json"), "w") as f:
    json.dump(sub440_verdict, f, indent=2)
print("\n=== sub440_verdict.json ===")
print(json.dumps(sub440_verdict, indent=2))

# ------------------------------------------------------------------ 7. portfolio blend (DAYONLY_DUAL6040)
DUAL_ctrl, port_ctrl, SIG_ctrl, Tpp_ctrl = build_portfolio_6040(bars3_dev, tgt_ctrl, "control_3m")
DUAL_vb, port_vb, SIG_vb, Tpp_vb = build_portfolio_6040(volbars, tgt_vb, "volbar_arm")

cal_ctrl = DUAL_ctrl.index
cal_vb = DUAL_vb.index
champ = champion_curve(cal_ctrl)

b_port_ctrl = dd_battery(cal_ctrl, port_ctrl.reindex(cal_ctrl).to_numpy(), label="PORT_control_3m")
b_port_vb = dd_battery(cal_vb, port_vb.reindex(cal_vb).to_numpy(), label="PORT_volbar_arm")
b_champ = dd_battery(cal_ctrl, champ.to_numpy(), label="PORT_INCUMBENT_CHAMPION")

d_sharpe_vb_champ = b_port_vb["sharpe"] - b_champ["sharpe"]
d_cdar_vb_champ = b_champ["CDaR5"] - b_port_vb["CDaR5"]

portfolio_blend = pd.DataFrame([
    {"arm": "control_3m_DUAL6040", "SIG_DUAL_leg_std": SIG_ctrl,
     "net_portfolio_6040": b_port_ctrl["net"], "sharpe_portfolio_6040": b_port_ctrl["sharpe"],
     "CDaR5_portfolio_6040": b_port_ctrl["CDaR5"], "maxDD_portfolio_6040": b_port_ctrl["maxDD_eod"]},
    {"arm": "volbar_arm_DUAL6040", "SIG_DUAL_leg_std": SIG_vb,
     "net_portfolio_6040": b_port_vb["net"], "sharpe_portfolio_6040": b_port_vb["sharpe"],
     "CDaR5_portfolio_6040": b_port_vb["CDaR5"], "maxDD_portfolio_6040": b_port_vb["maxDD_eod"],
     "d_sharpe_vs_champion": d_sharpe_vb_champ, "d_CDaR_vs_champion": d_cdar_vb_champ,
     "portfolio_beats_champion": bool(d_sharpe_vb_champ > 0 and d_cdar_vb_champ > 0)},
    {"arm": "incumbent_champion_60_40_reference", "net_portfolio_6040": b_champ["net"],
     "sharpe_portfolio_6040": b_champ["sharpe"], "CDaR5_portfolio_6040": b_champ["CDaR5"],
     "maxDD_portfolio_6040": b_champ["maxDD_eod"]},
])
portfolio_blend.to_csv(os.path.join(OUT, "portfolio_blend.csv"), index=False)
print("\n=== portfolio_blend.csv ===")
print(portfolio_blend.to_string(index=False), flush=True)

print(f"\ndone sub_440, {round(time.time()-t0, 1)}s", flush=True)
