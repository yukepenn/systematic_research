"""SMV2AF_1MIN_RESCALE_R2 -- Gate C: rebuild the rescaled 1m-clock ensemble on the
2006-2021 OLD REGIME, using the genuinely-native 1-minute raw substrate
(research/scalping_lab/substrate/minute/NQ/nq1m_2005_202605.parquet) -- the SAME raw file
SM06's own frozen build (runs/SM06_SOLAR_HISTORY/run_hist.py) reads before resampling to
3-minute. This is NOT deriving/approximating finer bars from coarser data (that would be
the SMV2W-blocked case) -- these ARE the native 1-minute bars, used directly.

FLAGGED HYPOTHESIS / INTERPRETIVE CALL (disclosed): the spec's gate C text (spec.yaml)
was written expecting (by analogy to SMV2W's 5-minute R2) that this gate would be
BLOCKED-BY-DATA, and explicitly names the COMMITTED "SM06 hist substrate" (the DERIVED
3-minute vote-state artifact) as the reason. gate_C_check_resolution.py verified that
premise is TRUE for the derived artifact but FALSE for the underlying committed raw
source -- a native 1-minute-resolution old-regime substrate DOES exist committed in the
repo. Unlike 5-minute (no common submultiple with 3-minute, and SMV2W's spec's OWN "data:"
field explicitly restricted scope to the 2022-2026 SM1M_SUBSTRATE only), SMV2AF's spec.yaml
carries no such data-scope restriction, and gate C's own stated condition
("IF a 1-minute-resolution old-regime substrate exists ... ") is satisfied. This run
therefore proceeds, flagging the deviation from the SMV2W-analogy explicitly rather than
mechanically reporting BLOCKED-BY-DATA against the actual evidence. If this interpretive
call is judged wrong, the correct fallback is BLOCKED-BY-DATA per the spec's fallback
instruction -- but the decision (A+B failed already, see gate_B_verdict.json) does not
change either way since gate C is diagnostic/reported, not gated.

Session tagging: applies the IDENTICAL gap>1hr heuristic sm01_solarsim.resample_3m()
already uses internally (out["time"].diff() > 1hr => first_bar_of_session) directly to the
native 1-minute timestamps, rather than resampling to 3-minute first -- i.e. the natural,
non-improvised extension of the SAME method SM06's own frozen hist substrate already uses,
just skipping the (now unnecessary) 3-minute aggregation step. Cross-checked below against
SM06's own committed session calendar.
"""
import os, sys, json, time as _time
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "runs", "SMV2AF_1MIN_RESCALE_R2")
OUT = os.path.join(RUN, "out")
AE_OUT = os.path.join(ROOT, "runs", "SMV2AE_1MIN_RESCALE", "out")
sys.path.insert(0, os.path.join(ROOT, "runs", "SMV2R_SOLAR_CORE_1"))
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
from common_exec import sm, e10_exec, metric_row  # noqa: E402
from smv2_common import dd_battery  # noqa: E402

t0 = _time.time()
TICK = sm.TICK
MNQ_PV = sm.MNQ_POINT_VALUE
MNQ_COMM = sm.MNQ_COMM_SIDE
FRICTION_PER_CONTRACT_SIDE = TICK * MNQ_PV + MNQ_COMM

# ---- R: reused verbatim (identical to step0/SMV2AE, NOT re-measured)
scale_ratio = pd.read_csv(os.path.join(AE_OUT, "scale_ratio.csv"))
R = float(scale_ratio.loc[scale_ratio["scope"] == "whole_dev", "median_R"].iloc[0])
VMS_1M = [v * R for v in sm.VMS]
print(f"R (reused verbatim) = {R:.6f}  VMS_1m = {[round(v,4) for v in VMS_1M]}", flush=True)

# ---- load native 1-minute raw substrate, old-regime window (identical filter to SM06's own build)
raw_path = os.path.join(ROOT, "research", "scalping_lab", "substrate", "minute", "NQ",
                        "nq1m_2005_202605.parquet")
h = pd.read_parquet(raw_path)
h["time"] = pd.to_datetime(h["time"])
h = h[h["time"] < "2022-01-01"].sort_values("time").reset_index(drop=True)
print(f"loaded {len(h)} native 1m hist bars, {h['time'].min()} -> {h['time'].max()}  "
      f"({_time.time()-t0:.1f}s)", flush=True)

# ---- session tagging: identical gap>1hr heuristic to sm01_solarsim.resample_3m's own
gap = h["time"].diff() > pd.Timedelta(hours=1)
h["first_bar_of_session"] = gap | (h.index == 0)
h["sess_id"] = h["first_bar_of_session"].cumsum()
last_time = h.groupby("sess_id")["time"].transform("max")
h["sess_date"] = last_time.dt.date
h["is_last_of_sess"] = h["time"].eq(last_time)
n_sess_1m = h["sess_id"].nunique()
print(f"session-tagged: {n_sess_1m} sessions ({_time.time()-t0:.1f}s)", flush=True)

# ---- cross-check vs SM06's own committed session calendar (integrity check, disclosed)
vote = pd.read_parquet(os.path.join(ROOT, "runs", "SM06_SOLAR_HISTORY", "out",
                                    "vote_state_3m_hist.parquet"), columns=["sess_date"])
sm06_sess_dates = set(pd.to_datetime(vote["sess_date"]).unique())
my_sess_dates = set(pd.to_datetime(h["sess_date"]).unique())
overlap = sm06_sess_dates & my_sess_dates
only_sm06 = sm06_sess_dates - my_sess_dates
only_mine = my_sess_dates - sm06_sess_dates
calendar_check = {
    "n_sessions_sm06_3m_hist": len(sm06_sess_dates), "n_sessions_native_1m_tagged": len(my_sess_dates),
    "n_overlap": len(overlap), "n_only_in_sm06": len(only_sm06), "n_only_in_mine": len(only_mine),
    "match_rate_vs_sm06": len(overlap) / len(sm06_sess_dates),
}
print(json.dumps(calendar_check, indent=2), flush=True)
json.dump(calendar_check, open(os.path.join(OUT, "gate_C_session_calendar_check.json"), "w"), indent=2)

# ---- simulate: sigma (1380-bar time-matched, IDENTICAL convention to dev's rescaled arm)
close = h["close"].to_numpy()
sig = sm.sigma_series(close, vol_period=1380)
print(f"sigma computed ({_time.time()-t0:.1f}s)", flush=True)

PEND = []
for i, vmv in enumerate(VMS_1M):
    is_up, flip, s_eff, anchor = sm.member_states(close, sig, float(vmv))
    fills, pos, pend = sm.member_trades(h, is_up, flip, s_eff, anchor)
    PEND.append(pend)
    print(f"  member {i+1}/13 (vm={vmv:.2f}) done ({_time.time()-t0:.1f}s)", flush=True)
pend = np.column_stack(PEND)
tgt = sm.e10_target(pend)
print(f"targets built ({_time.time()-t0:.1f}s)", flush=True)

daily, bar_pos, bar_pnl = e10_exec(h, tgt)
daily["sess"] = pd.to_datetime(daily["sess"])
print(f"e10_exec done: {len(daily)} sessions ({_time.time()-t0:.1f}s)", flush=True)

daily.to_csv(os.path.join(OUT, "gate_C_old_regime_daily.csv"), index=False)

m = metric_row("1m_time_matched_RESCALED_R_OLDREGIME_2006_2021", daily)
n_tgt_changes = int((np.diff(tgt) != 0).sum())
total_contracts = float(daily["contracts"].sum())
total_friction = total_contracts * FRICTION_PER_CONTRACT_SIDE
gross = m["net"] + total_friction
friction_share = total_friction / gross if gross != 0 else np.nan
m.update({
    "R_scale_used": R, "clock": "1m", "convention": "time_matched_RESCALED",
    "vol_period_bars": 1380, "n_bars": len(h), "n_sessions": len(daily),
    "n_tgt_changes": n_tgt_changes, "tgt_changes_per_day": n_tgt_changes / len(daily),
    "total_contracts_traded": total_contracts,
    "friction_per_contract_side_$": FRICTION_PER_CONTRACT_SIDE,
    "total_friction_$": total_friction, "gross_$": gross, "friction_share": friction_share,
})
pd.DataFrame([m]).to_csv(os.path.join(OUT, "gate_C_old_regime.csv"), index=False)

# ---- comparison vs SM06's OWN committed 3m-incumbent hist-period result (read verbatim)
sm06_res = json.load(open(os.path.join(ROOT, "runs", "SM06_SOLAR_HISTORY", "out", "result.json")))

# ---- block bootstrap on old-regime daily net (house convention, same construction as gate A)
SEED, BLOCK, NBOOT = 20260808, 5, 10000
x = daily["net"].to_numpy()
n = len(x)
rng = np.random.default_rng(SEED)
nb = int(np.ceil(n / BLOCK))
starts = rng.integers(0, n, size=(NBOOT, nb))
idx = ((starts[:, :, None] + np.arange(BLOCK)[None, None, :]) % n).reshape(NBOOT, -1)[:, :n]

def path_sharpe(x, idx, chunk=2000):
    shp = np.empty(len(idx))
    for i in range(0, len(idx), chunk):
        X = x[idx[i:i + chunk]]
        mu = X.mean(axis=1); sd_ = X.std(axis=1, ddof=1)
        shp[i:i + chunk] = mu / sd_ * np.sqrt(252)
    return shp

boot_sharpe = path_sharpe(x, idx)
P_gt0 = float((boot_sharpe > 0).mean())
q05, q50, q95 = np.quantile(boot_sharpe, [0.05, 0.50, 0.95])

# per-era Sharpe (matching SM06's own 4-block convention: 2006-09/2010-13/2014-17/2018-21)
d = pd.Series(daily["net"].to_numpy(), index=pd.to_datetime(daily["sess"]))
def sharpe(v):
    v = np.asarray(v, dtype=float)
    sd = v.std(ddof=1)
    return v.mean() / sd * np.sqrt(252) if sd > 0 else np.nan
eras = {"2006-09": d["2006":"2009"], "2010-13": d["2010":"2013"],
        "2014-17": d["2014":"2017"], "2018-21": d["2018":"2021"]}
era_stats = {k: {"n_days": len(v), "net": float(v.sum()), "sharpe": sharpe(v)} for k, v in eras.items()}

summary = {
    "gate_verdict": "NOT_BLOCKED -- native 1-minute raw substrate exists and was used directly "
                    "(see gate_C_resolution_check.json; this deviates from SMV2W's 5-minute "
                    "BLOCKED-BY-DATA precedent -- flagged interpretive call, disclosed in module docstring)",
    "old_regime_window": "2006-01-05 to 2021-12-31 (native 1m bars, gap>1hr session tagging)",
    "n_sessions": len(daily), "n_bars": len(h),
    "net_$": m["net"], "sharpe": m["sharpe"], "maxDD_eod": m["max_dd"], "CDaR5": m["CDaR5"],
    "friction_share": friction_share, "tgt_changes_per_day": m["tgt_changes_per_day"],
    "boot_sharpe_q05": float(q05), "boot_sharpe_q50": float(q50), "boot_sharpe_q95": float(q95),
    "boot_P_sharpe_gt0": P_gt0,
    "sm06_3m_incumbent_hist_2006_2021_net": sm06_res["net_total"],
    "sm06_3m_incumbent_hist_2006_2021_sharpe": sm06_res["sharpe"],
    "sm06_3m_incumbent_verdict": sm06_res["verdict"],
    "era_stats_1m_rescaled": era_stats,
    "session_calendar_match_rate_vs_sm06": calendar_check["match_rate_vs_sm06"],
    "runtime_s": round(_time.time() - t0, 1),
}
json.dump(summary, open(os.path.join(OUT, "gate_C_summary.json"), "w"), indent=2)
print(json.dumps(summary, indent=2, default=str))
print(f"\ndone gate C ({_time.time()-t0:.1f}s total)", flush=True)
