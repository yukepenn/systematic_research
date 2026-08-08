"""SMV2AF_1MIN_RESCALE_R2 -- step0: recompute the rescaled-1m-arm dev daily PnL curve
using the IDENTICAL code path as runs/SMV2AE_1MIN_RESCALE/step2_rescaled_ensemble.py
(same imports: common_exec.sm/e10_exec, same bars1 substrate, same R read verbatim from
SMV2AE's own committed scale_ratio.csv -- NOT re-measured here). SMV2AE's own run did not
persist the per-day curve to disk (only the aggregate metric_row), so this step reproduces
it bit-for-bit and cross-checks the aggregate stats against SMV2AE's committed
rescaled_ensemble.csv before anything downstream uses it.

Also pulls the 3m incumbent's dev daily curve (already-committed artifact, read verbatim,
not recomputed) for gate D's correlation/blend diagnostic.
"""
import os, sys, json
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "runs", "SMV2AF_1MIN_RESCALE_R2")
OUT = os.path.join(RUN, "out")
AE_OUT = os.path.join(ROOT, "runs", "SMV2AE_1MIN_RESCALE", "out")
sys.path.insert(0, os.path.join(ROOT, "runs", "SMV2R_SOLAR_CORE_1"))
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
from common_exec import sm, e10_exec, metric_row  # noqa: E402  (verbatim SMV2R/SMV2U/SMV2AE executor)
from smv2_common import dd_battery  # noqa: E402

TICK = sm.TICK
MNQ_PV = sm.MNQ_POINT_VALUE
MNQ_COMM = sm.MNQ_COMM_SIDE
FRICTION_PER_CONTRACT_SIDE = TICK * MNQ_PV + MNQ_COMM

DEV_END = pd.Timestamp("2026-05-31")

# ---- R: read verbatim from SMV2AE's own committed, pre-registered scale_ratio.csv (NOT re-measured)
scale_ratio = pd.read_csv(os.path.join(AE_OUT, "scale_ratio.csv"))
R = float(scale_ratio.loc[scale_ratio["scope"] == "whole_dev", "median_R"].iloc[0])
assert abs(R - 1.730064) < 1e-3, f"R mismatch vs frozen 1.730064: {R}"
print(f"R (reused verbatim from SMV2AE/out/scale_ratio.csv) = {R:.6f}", flush=True)

VMS_1M = [v * R for v in sm.VMS]

# ---- substrate (identical to SMV2AE step2)
bars1 = pd.read_parquet(os.path.join(ROOT, "runs", "SMV2U_CLOCK_CHALLENGE", "out",
                                     "bars_1m_dev.parquet"))
assert (bars1["sess_date"] <= DEV_END.date()).all()

inc_daily = pd.read_csv(os.path.join(ROOT, "runs", "SMV2R_SOLAR_CORE_1", "out",
                                     "e10_daily_dev_incumbent.csv"), parse_dates=["sess"])
CAL = inc_daily["sess"]
n_cal = len(CAL)

close = bars1["close"].to_numpy()
sig = sm.sigma_series(close, vol_period=1380)

PEND = []
for vm in VMS_1M:
    is_up, flip, s_eff, anchor = sm.member_states(close, sig, float(vm))
    fills, pos, pend = sm.member_trades(bars1, is_up, flip, s_eff, anchor)
    PEND.append(pend)
pend = np.column_stack(PEND)
tgt = sm.e10_target(pend)
daily, bar_pos, bar_pnl = e10_exec(bars1, tgt)
daily["sess"] = pd.to_datetime(daily["sess"])

assert len(daily) == n_cal, f"session count {len(daily)} != incumbent dev calendar {n_cal}"
assert list(pd.to_datetime(daily["sess"])) == list(CAL), "calendar mismatch vs incumbent dev calendar"

m = metric_row("1m_time_matched_RESCALED_R_recompute", daily)

# ---- cross-check against SMV2AE's committed aggregate (bit-for-bit reproduction test)
ref = pd.read_csv(os.path.join(AE_OUT, "rescaled_ensemble.csv")).iloc[0]
net_dev = abs(m["net"] - float(ref["net"]))
sharpe_dev = abs(m["sharpe"] - float(ref["sharpe"]))
print(f"recompute net={m['net']:.4f} vs SMV2AE committed net={ref['net']:.4f} (|dev|={net_dev:.6g})")
print(f"recompute sharpe={m['sharpe']:.6f} vs SMV2AE committed sharpe={ref['sharpe']:.6f} (|dev|={sharpe_dev:.2e})")
assert net_dev < 1e-3, "net does not reproduce SMV2AE's committed rescaled_ensemble.csv"
assert sharpe_dev < 1e-9, "sharpe does not reproduce SMV2AE's committed rescaled_ensemble.csv"

repro = {
    "R_used": R, "net_recompute": m["net"], "net_smv2ae_committed": float(ref["net"]),
    "net_abs_dev": net_dev, "sharpe_recompute": m["sharpe"],
    "sharpe_smv2ae_committed": float(ref["sharpe"]), "sharpe_abs_dev": sharpe_dev,
    "bitwise_reproduction_confirmed": bool(net_dev < 1e-3 and sharpe_dev < 1e-9),
}
json.dump(repro, open(os.path.join(OUT, "step0_repro_check.json"), "w"), indent=2)
print(json.dumps(repro, indent=2))

# ---- save the recovered daily curve (this is the artifact gates A/B/D consume)
curve = pd.DataFrame({
    "sess": pd.to_datetime(daily["sess"]),
    "net_1m_rescaled": daily["net"].to_numpy(),
    "net_3m_incumbent": inc_daily.set_index("sess").reindex(pd.to_datetime(daily["sess"]))["net"].to_numpy(),
})
curve.to_csv(os.path.join(OUT, "dev_daily_curves.csv"), index=False)
print(f"\nsaved dev_daily_curves.csv: {len(curve)} sessions "
      f"{curve['sess'].min().date()} -> {curve['sess'].max().date()}")
print("done step0")
