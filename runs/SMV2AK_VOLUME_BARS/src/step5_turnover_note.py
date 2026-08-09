"""SMV2AK sub_442 -- turnover mechanism note (DIAGNOSTIC, always reported,
regardless of whether sub_440 produced a CANDIDATE). Compares volume-bar
turnover (E10 target-change frequency, and total contracts traded) directly
against the 3m incumbent's, and against SMV2U_CLOCK_CHALLENGE's own 5-minute-
bar turnover figures (read verbatim from runs/SMV2U_CLOCK_CHALLENGE/out/
clock_arms.csv, NOT re-simulated).

Motivating hypothesis (SMV2U/W's own inference, restated in this spec's
class comment): "5-minute nearly beat 3-minute via TURNOVER-DAMPING, not
faster information" -- if volume bars implement activity-adaptive damping
without a fixed slower clock, the specific mechanistic signature predicted is
volume-bar turnover landing SOMEWHERE BETWEEN the 3m incumbent's and the 5m
arms' (damped vs 3m, but not as damped as a fixed-slower clock since volume
bars still run FAST during high-activity bursts). Reported below whether this
pattern holds or not -- it does not have to hold for sub_442 to be complete.
"""
import os, json
import pandas as pd

import sys
sys.path.insert(0, os.path.dirname(__file__))
from common import ROOT, OUT

ens = pd.read_csv(os.path.join(OUT, "ensemble_test.csv"))
ctrl = ens[ens["role"] == "control"].iloc[0]
vb = ens[ens["role"] == "challenger"].iloc[0]

n_days_ctrl = int(ctrl["n_days"])
n_days_vb = int(vb["n_days"])

ctrl_tgt_changes_per_day = float(ctrl["n_tgt_changes"]) / n_days_ctrl
vb_tgt_changes_per_day = float(vb["n_tgt_changes"]) / n_days_vb

clock_arms = pd.read_csv(os.path.join(ROOT, "runs", "SMV2U_CLOCK_CHALLENGE", "out", "clock_arms.csv"))
row_3m = clock_arms[clock_arms["arm"] == "3m_incumbent"].iloc[0]
row_5m_bm = clock_arms[clock_arms["arm"] == "5m_bar_matched"].iloc[0]
row_5m_tm = clock_arms[clock_arms["arm"] == "5m_time_matched"].iloc[0]

# cross-check: this run's own control recompute should match SMV2U's cached 3m_incumbent
# tgt_changes_per_day (both are the SAME 13-member/clamp[40,1200]/sigma460 3m construction)
xcheck_dev = abs(ctrl_tgt_changes_per_day - float(row_3m["tgt_changes_per_day"]))
print(f"cross-check: this run's control tgt_changes/day={ctrl_tgt_changes_per_day:.4f} vs "
      f"SMV2U's cached 3m_incumbent tgt_changes/day={row_3m['tgt_changes_per_day']:.4f} "
      f"(abs dev {xcheck_dev:.4f}, expected ~0 -- same construction)", flush=True)

comparison = pd.DataFrame([
    {"clock": "5m_bar_matched (SMV2U)", "tgt_changes_per_day": float(row_5m_bm["tgt_changes_per_day"]),
     "total_contracts_traded": float(row_5m_bm["total_contracts_traded"]),
     "avg_contracts_per_day": float(row_5m_bm["avg_contracts_per_day"])},
    {"clock": "5m_time_matched (SMV2U)", "tgt_changes_per_day": float(row_5m_tm["tgt_changes_per_day"]),
     "total_contracts_traded": float(row_5m_tm["total_contracts_traded"]),
     "avg_contracts_per_day": float(row_5m_tm["avg_contracts_per_day"])},
    {"clock": "3m_incumbent (this run's control, dev-recomputed)",
     "tgt_changes_per_day": ctrl_tgt_changes_per_day,
     "total_contracts_traded": float(ctrl["total_contracts_traded_aligned_cal"]),
     "avg_contracts_per_day": float(ctrl["avg_contracts_per_day"])},
    {"clock": "3m_incumbent (SMV2U cached, cross-check)",
     "tgt_changes_per_day": float(row_3m["tgt_changes_per_day"]),
     "total_contracts_traded": float(row_3m["total_contracts_traded"]),
     "avg_contracts_per_day": float(row_3m["avg_contracts_per_day"])},
    {"clock": "volume_bars (this run, SMV2AK sub_440)",
     "tgt_changes_per_day": vb_tgt_changes_per_day,
     "total_contracts_traded": float(vb["total_contracts_traded_aligned_cal"]),
     "avg_contracts_per_day": float(vb["avg_contracts_per_day"])},
])

lower = min(float(row_5m_bm["tgt_changes_per_day"]), float(row_5m_tm["tgt_changes_per_day"]))
upper = ctrl_tgt_changes_per_day
between_3m_and_5m = bool(lower <= vb_tgt_changes_per_day <= upper)

comparison.to_csv(os.path.join(OUT, "turnover_comparison.csv"), index=False)
print("\n=== turnover_comparison.csv ===")
print(comparison.to_string(index=False), flush=True)

if between_3m_and_5m:
    finding = "PATTERN HOLDS: volume-bar turnover lands between 3m and 5m."
else:
    finding = (
        "PATTERN DOES NOT HOLD at this calibration: volume-bar turnover "
        f"({vb_tgt_changes_per_day:.2f} tgt-changes/day) is HIGHER than the 3m incumbent's "
        f"({ctrl_tgt_changes_per_day:.2f}/day), i.e. in the OPPOSITE direction from both 5m "
        f"arms ({row_5m_bm['tgt_changes_per_day']:.2f} / {row_5m_tm['tgt_changes_per_day']:.2f}"
        "/day, both well BELOW the 3m incumbent). Total contracts traded tell the same story "
        f"({vb['total_contracts_traded_aligned_cal']:.0f} for volume bars vs "
        f"{ctrl['total_contracts_traded_aligned_cal']:.0f} for the 3m control, MORE not fewer). "
        "The activity-adaptive-damping mechanism this spec's motivating hypothesis predicted "
        "(fewer, wider bars in quiet periods -> less churn) is contradicted by this V "
        "calibration's bar-width distribution: sub_438 found volume bars are heavily right-"
        "skewed (median elapsed width 1.00min, well BELOW the 3-minute fixed cadence, because "
        "V was calibrated to the incumbent's AVERAGE 3m-bar volume and volume itself is "
        "right-skewed intra-session -- most bars close in <=1 minute during normal/elevated "
        "activity, with only the quiet tail stretching out to the p90=10min width). The mean "
        "width (3.68min) is close to 3.00min as calibrated, but the MEDIAN bar is far narrower "
        "than 3 minutes, so on a typical (median) bar the volume clock trades MORE often than "
        "the fixed 3-minute clock, not less -- net effect is higher churn, not damping."
    )

verdict = {
    "hypothesis": "volume-bar turnover lands BETWEEN 3m incumbent's and 5m arms' (activity-"
                   "adaptive damping without a fixed slower clock)",
    "tgt_changes_per_day_3m_incumbent": ctrl_tgt_changes_per_day,
    "tgt_changes_per_day_volume_bars": vb_tgt_changes_per_day,
    "tgt_changes_per_day_5m_bar_matched": float(row_5m_bm["tgt_changes_per_day"]),
    "tgt_changes_per_day_5m_time_matched": float(row_5m_tm["tgt_changes_per_day"]),
    "pattern_holds_volbar_between_3m_and_5m": between_3m_and_5m,
    "finding": finding,
}

with open(os.path.join(OUT, "turnover_mechanism_meta.json"), "w") as f:
    json.dump(verdict, f, indent=2)
print("\n=== turnover_mechanism_meta.json ===")
print(json.dumps(verdict, indent=2))
print("\ndone sub_442")
