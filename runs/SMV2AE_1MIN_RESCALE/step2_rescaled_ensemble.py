"""SMV2AE step2 -- seq 419 (rescaled ensemble, 1 arm) + comparison to SMV2U's original unscaled
1m time-matched result.

Starting point: SMV2U_CLOCK_CHALLENGE/step1_clock_arms.py's 1m time-matched arm construction,
reused verbatim (VolPeriod=1380 1-minute bars, sm01_solarsim member_states/member_trades/e10_target/
E10 executor, MNQ costs, session flatten, same friction-share definition) -- the ONLY change is
VMS_1m = [v * R for v in sm.VMS] in place of sm.VMS unscaled, where R = sub_418's pre-registered
whole-dev-period median (read from out/scale_ratio.csv, NOT re-derived or re-picked here). Clamp
bounds [40,1200] ticks are left UNCHANGED (absolute price-space bounds on S itself, not on
VolMult, per the code -- they do not get rescaled). Fallback constant (179t stop_mult_ticks) is
also UNCHANGED (member_states default).
"""
import os, sys, json
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "runs", "SMV2AE_1MIN_RESCALE")
OUT = os.path.join(RUN, "out")
sys.path.insert(0, os.path.join(ROOT, "runs", "SMV2R_SOLAR_CORE_1"))
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
from common_exec import sm, e10_exec, metric_row  # noqa: E402  (verbatim SMV2R/SMV2U executor)
from smv2_common import dd_battery  # noqa: E402

TICK = sm.TICK
MNQ_PV = sm.MNQ_POINT_VALUE
MNQ_COMM = sm.MNQ_COMM_SIDE
FRICTION_PER_CONTRACT_SIDE = TICK * MNQ_PV + MNQ_COMM   # SAME def as SMV2U: 1-tick adverse slip $ + commission, per side

DEV_END = pd.Timestamp("2026-05-31")

# ------------------------------------------------------------------ 0. R from sub_418 (frozen, pre-registered)
scale_ratio = pd.read_csv(os.path.join(OUT, "scale_ratio.csv"))
R = float(scale_ratio.loc[scale_ratio["scope"] == "whole_dev", "median_R"].iloc[0])
print(f"R (sub_418 whole-dev median, pre-registered) = {R:.6f}", flush=True)

VMS_1M = [v * R for v in sm.VMS]
print(f"VMS_1m (rescaled, 13 members) = {[round(v, 4) for v in VMS_1M]}", flush=True)

# ------------------------------------------------------------------ 1. load substrate (reused, not rebuilt)
bars1 = pd.read_parquet(os.path.join(ROOT, "runs", "SMV2U_CLOCK_CHALLENGE", "out",
                                     "bars_1m_dev.parquet"))
assert (bars1["sess_date"] <= DEV_END.date()).all()
n_cal_expected = 1139  # SMV2U's dev calendar session count (cross-check)

inc_cache = np.load(os.path.join(ROOT, "runs", "SMV2R_SOLAR_CORE_1", "out", "cache_incumbent.npz"))
inc_daily = pd.read_csv(os.path.join(ROOT, "runs", "SMV2R_SOLAR_CORE_1", "out",
                                     "e10_daily_dev_incumbent.csv"), parse_dates=["sess"])
CAL = inc_daily["sess"]
n_cal = len(CAL)
inc_series = inc_daily.set_index("sess")["net"]
inc_metric = metric_row("3m_incumbent", inc_daily)

# SMV2U's original unscaled 1m time-matched arm (ground truth for comparison, read verbatim from
# its committed output -- NOT re-simulated here)
smv2u_arms = pd.read_csv(os.path.join(ROOT, "runs", "SMV2U_CLOCK_CHALLENGE", "out", "clock_arms.csv"))
smv2u_1m_tm = smv2u_arms[smv2u_arms["arm"] == "1m_time_matched"].iloc[0]

# ------------------------------------------------------------------ 2. build the rescaled arm
close = bars1["close"].to_numpy()
sig = sm.sigma_series(close, vol_period=1380)   # time-matched, SMV2U's better-performing convention

PEND = []; POS = []
for vm in VMS_1M:
    is_up, flip, s_eff, anchor = sm.member_states(close, sig, float(vm))   # clamp/fallback UNCHANGED (defaults)
    fills, pos, pend = sm.member_trades(bars1, is_up, flip, s_eff, anchor)
    PEND.append(pend); POS.append(pos)
pend = np.column_stack(PEND); pos_mat = np.column_stack(POS)
tgt = sm.e10_target(pend)
daily, bar_pos, bar_pnl = e10_exec(bars1, tgt)
daily["sess"] = pd.to_datetime(daily["sess"])
arm_series = daily.set_index("sess")["net"]

assert len(daily) == n_cal, f"session count {len(daily)} != incumbent dev calendar {n_cal}"
assert list(pd.to_datetime(daily["sess"])) == list(CAL), "calendar mismatch vs incumbent dev calendar"
assert n_cal == n_cal_expected, f"dev calendar session count {n_cal} != SMV2U's {n_cal_expected}"

label = "1m_time_matched_RESCALED_R"
m = metric_row(label, daily)
b = dd_battery(CAL, arm_series.reindex(CAL).to_numpy(), label=label)

# ---- turnover + friction share (SAME definition SMV2U used)
n_tgt_changes = int((np.diff(tgt) != 0).sum())
total_contracts = float(daily["contracts"].sum())
total_friction = total_contracts * FRICTION_PER_CONTRACT_SIDE
gross = m["net"] + total_friction
friction_share = total_friction / gross if gross != 0 else np.nan
m.update({
    "R_scale_used": R,
    "clock": "1m", "convention": "time_matched_RESCALED", "vol_period_bars": 1380,
    "n_bars": len(bars1), "n_tgt_changes": n_tgt_changes,
    "tgt_changes_per_day": n_tgt_changes / n_cal,
    "total_contracts_traded": total_contracts,
    "friction_per_contract_side_$": FRICTION_PER_CONTRACT_SIDE,
    "total_friction_$": total_friction, "gross_$": gross,
    "friction_share": friction_share,
    "CDaR5": b["CDaR5"], "maxDD_eod": b["maxDD_eod"], "sortino_dd_battery": b["sortino"],
    "longest_TUW_days": b["longest_TUW_days"],
})

print(f"\nnet={m['net']:.1f} sharpe={m['sharpe']:.4f} CDaR5={m['CDaR5']:.1f} "
      f"friction_share={friction_share:.4f} tgt_changes/day={m['tgt_changes_per_day']:.1f}",
      flush=True)

rescaled_ensemble = pd.DataFrame([m])
rescaled_ensemble.to_csv(os.path.join(OUT, "rescaled_ensemble.csv"), index=False)

# ------------------------------------------------------------------ 3. friction_share.csv (verbatim column reused)
friction_df = pd.DataFrame([
    {"arm": "3m_incumbent", "net": inc_metric["net"], "total_contracts_traded":
        float(inc_daily["contracts"].sum()),
     "total_friction_$": float(inc_daily["contracts"].sum()) * FRICTION_PER_CONTRACT_SIDE,
     "gross_$": inc_metric["net"] + float(inc_daily["contracts"].sum()) * FRICTION_PER_CONTRACT_SIDE,
     "friction_share": (float(inc_daily["contracts"].sum()) * FRICTION_PER_CONTRACT_SIDE) /
                       (inc_metric["net"] + float(inc_daily["contracts"].sum()) * FRICTION_PER_CONTRACT_SIDE)},
    {"arm": "1m_time_matched_UNSCALED_smv2u_seq390", "net": float(smv2u_1m_tm["net"]),
     "total_contracts_traded": float(smv2u_1m_tm["total_contracts_traded"]),
     "total_friction_$": float(smv2u_1m_tm["total_friction_$"]),
     "gross_$": float(smv2u_1m_tm["gross_$"]),
     "friction_share": float(smv2u_1m_tm["friction_share"])},
    {"arm": label, "net": m["net"], "total_contracts_traded": total_contracts,
     "total_friction_$": total_friction, "gross_$": gross, "friction_share": friction_share},
])
friction_df.to_csv(os.path.join(OUT, "friction_share.csv"), index=False)

# ------------------------------------------------------------------ 4. before/after comparison vs SMV2U original
comparison = pd.DataFrame([
    {"arm": "SMV2U_1m_time_matched_UNSCALED (seq 390, VMS unscaled)",
     "net_$": float(smv2u_1m_tm["net"]), "sharpe": float(smv2u_1m_tm["sharpe"]),
     "CDaR5_$": float(smv2u_1m_tm["CDaR5"]), "friction_share": float(smv2u_1m_tm["friction_share"]),
     "tgt_changes_per_day": float(smv2u_1m_tm["tgt_changes_per_day"]),
     "total_contracts_traded": float(smv2u_1m_tm["total_contracts_traded"])},
    {"arm": f"SMV2AE_1m_time_matched_RESCALED (seq 419, VMS x R={R:.4f})",
     "net_$": m["net"], "sharpe": m["sharpe"], "CDaR5_$": m["CDaR5"],
     "friction_share": friction_share, "tgt_changes_per_day": m["tgt_changes_per_day"],
     "total_contracts_traded": total_contracts},
    {"arm": "3m_incumbent (reference, not a rescale target)",
     "net_$": inc_metric["net"], "sharpe": inc_metric["sharpe"], "CDaR5_$": inc_metric["CDaR5"],
     "friction_share": friction_df.loc[friction_df["arm"] == "3m_incumbent", "friction_share"].iloc[0],
     "tgt_changes_per_day": np.nan, "total_contracts_traded":
         float(inc_daily["contracts"].sum())},
])
comparison["delta_vs_unscaled_net_$"] = comparison["net_$"] - float(smv2u_1m_tm["net"])
comparison["delta_vs_unscaled_sharpe"] = comparison["sharpe"] - float(smv2u_1m_tm["sharpe"])
comparison.to_csv(os.path.join(OUT, "comparison_vs_smv2u.csv"), index=False)

# ------------------------------------------------------------------ 5. screen_gate verdict (frozen rule)
sharpe_val = m["sharpe"]
friction_val = friction_share
pass_screen = bool((sharpe_val > 0) and (friction_val < 0.60))
verdict = {
    "rule": "PASS-SCREEN if standalone Sharpe > 0 AND friction_share < 0.60; else FAIL-SCREEN.",
    "standalone_sharpe": sharpe_val, "friction_share": friction_val,
    "sharpe_gt_0": bool(sharpe_val > 0), "friction_share_lt_060": bool(friction_val < 0.60),
    "screen_gate_verdict": "PASS-SCREEN" if pass_screen else "FAIL-SCREEN",
    "consequence": ("queue an R2_CONFIRMATION spec (full bootstrap/LOYO/old-regime/"
                     "portfolio-contribution battery, SMV2T-style) in a later wave" if pass_screen
                    else "1-minute bars are CLOSED per the house rule -- no further 1-minute tests "
                         "without a structurally new mechanism (not a further recalibration attempt)"),
}
with open(os.path.join(OUT, "screen_gate_verdict.json"), "w") as f:
    json.dump(verdict, f, indent=2)

print("\n=== screen_gate verdict ===")
print(json.dumps(verdict, indent=2))
print("done")
