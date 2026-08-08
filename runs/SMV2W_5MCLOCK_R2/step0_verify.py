"""SMV2W_5MCLOCK_R2 STEP ZERO -- REPRODUCTION GATE + reuse.

Per CODE MAP: build the 5m ensemble (VolPeriod=276 5m bars) EXACTLY as SMV2U's
step1_clock_arms.py did for the time-matched 5m arm -- reuse that code, verify it
reproduces SMV2U's out/clock_arms.csv numbers for this arm before proceeding.

This script:
  1. Loads SMV2U's already-committed, already-verified 5m dev bars
     (runs/SMV2U_CLOCK_CHALLENGE/out/bars_5m_dev.parquet) -- REUSED, not rebuilt
     (spec: "reuse SMV2U's verified aggregation + session-calendar-match code, do
     not rebuild from scratch").
  2. Rebuilds the 13-member V3 ensemble (sm01_solarsim.member_states/member_trades,
     verbatim) on those 5m bars with VolPeriod=276 (time-matched convention),
     IDENTICAL to SMV2U step1_clock_arms.py's CONFIGS entry ("5m", bars5,
     "time_matched", 276).
  3. Runs the E10 executor (SMV2R common_exec.e10_exec, verbatim) to get the daily
     curve and bar-level pos/pnl.
  4. REPRODUCTION GATE: compares net/sharpe/max_dd/CDaR5/friction_share/etc against
     the committed runs/SMV2U_CLOCK_CHALLENGE/out/clock_arms.csv row
     "5m_time_matched". Any nonzero deviation is investigated; only a clean
     (near-exact) reproduction licenses building on this object for the R2 gates.
  5. Loads the verified 3m incumbent core (SMV2R cache_incumbent.npz, already
     verified 100.0000% in SMV2R step0) for use as the reference leg downstream.

NO data >= 2026-08-01 read anywhere. Dev = sessions <= 2026-05-31 (frozen convention,
inherited unmodified from SMV2U's own dev filter on bars_5m_dev.parquet).
"""
import sys, os, json, time
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "runs", "SMV2W_5MCLOCK_R2")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.join(ROOT, "runs", "SMV2R_SOLAR_CORE_1"))
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
from common_exec import e10_exec, metric_row  # noqa: E402  (verbatim SMV2R executor)
import sm01_solarsim as sm  # noqa: E402
from smv2_common import dd_battery  # noqa: E402

DEV_END = pd.Timestamp("2026-05-31")
SMV2U_OUT = os.path.join(ROOT, "runs", "SMV2U_CLOCK_CHALLENGE", "out")
SMV2R_OUT = os.path.join(ROOT, "runs", "SMV2R_SOLAR_CORE_1", "out")

t0 = time.time()

# ---------------------------------------------------------------- 1. reuse SMV2U's verified 5m dev bars
bars5 = pd.read_parquet(os.path.join(SMV2U_OUT, "bars_5m_dev.parquet"))
assert (bars5["sess_date"] <= DEV_END.date()).all(), "bars_5m_dev.parquet has data past dev cutoff"
print(f"5m dev bars (REUSED from SMV2U step0): {len(bars5)} bars, "
      f"{bars5['sess_id'].nunique()} sessions, {bars5['sess_date'].min()} -> {bars5['sess_date'].max()}",
      flush=True)

# ---------------------------------------------------------------- 2. rebuild 13-member ensemble, VolPeriod=276
VMS = sm.VMS
assert list(VMS) == list(range(6, 31, 2)) and len(VMS) == 13
N = 276  # time-matched 5m convention (spec: VolPeriod=276 5m bars)

close5 = bars5["close"].to_numpy()
sig5 = sm.sigma_series(close5, vol_period=N)
PEND, POS = [], []
for vm in VMS:
    is_up, flip, s_eff, anchor = sm.member_states(close5, sig5, float(vm))
    fills, pos, pend = sm.member_trades(bars5, is_up, flip, s_eff, anchor)
    PEND.append(pend); POS.append(pos)
pend5 = np.column_stack(PEND)
pos5 = np.column_stack(POS)
tgt5 = sm.e10_target(pend5)

daily5, bar_pos5, bar_pnl5 = e10_exec(bars5, tgt5)
daily5["sess"] = pd.to_datetime(daily5["sess"])
n_cal5 = len(daily5)
print(f"5m_time_matched (VolPeriod={N}): {n_cal5} sessions built, tgt range "
      f"[{tgt5.min()},{tgt5.max()}]", flush=True)

# ---------------------------------------------------------------- 3. metric row (identical construction path)
m5 = metric_row("5m_time_matched", daily5)
n_tgt_changes = int((np.diff(tgt5) != 0).sum())
TICK = sm.TICK; MNQ_PV = sm.MNQ_POINT_VALUE; MNQ_COMM = sm.MNQ_COMM_SIDE
FRICTION_PER_CONTRACT_SIDE = TICK * MNQ_PV + MNQ_COMM
total_contracts = float(daily5["contracts"].sum())
total_friction = total_contracts * FRICTION_PER_CONTRACT_SIDE
gross = m5["net"] + total_friction
friction_share = total_friction / gross if gross != 0 else np.nan
m5.update({
    "clock": "5m", "convention": "time_matched", "vol_period_bars": N,
    "n_bars": len(bars5), "n_tgt_changes": n_tgt_changes,
    "tgt_changes_per_day": n_tgt_changes / n_cal5,
    "total_contracts_traded": total_contracts,
    "friction_per_contract_side_$": FRICTION_PER_CONTRACT_SIDE,
    "total_friction_$": total_friction, "gross_$": gross,
    "friction_share": friction_share,
})

# ---------------------------------------------------------------- 4. REPRODUCTION GATE vs SMV2U clock_arms.csv
ref = pd.read_csv(os.path.join(SMV2U_OUT, "clock_arms.csv"))
ref_row = ref[ref["arm"] == "5m_time_matched"].iloc[0]

check_fields = ["net", "sharpe", "max_dd", "CDaR5", "n_sessions", "n_bars",
                 "n_tgt_changes", "total_contracts_traded", "friction_share",
                 "vol_period_bars"]
repro = []
for f in check_fields:
    mine = float(m5[f]); theirs = float(ref_row[f])
    dev = abs(mine - theirs)
    repro.append({"field": f, "mine": mine, "smv2u_ref": theirs, "abs_dev": dev,
                   "match": bool(dev < 1e-6 * max(1.0, abs(theirs)))})
repro_df = pd.DataFrame(repro)
repro_all_pass = bool(repro_df["match"].all())
print("\n=== REPRODUCTION GATE vs runs/SMV2U_CLOCK_CHALLENGE/out/clock_arms.csv "
      "(row: 5m_time_matched) ===")
print(repro_df.to_string(index=False))
print(f"\nREPRO GATE: {'PASS' if repro_all_pass else 'FAIL'} "
      f"({repro_df['match'].sum()}/{len(repro_df)} fields exact)", flush=True)

if not repro_all_pass:
    print("BLOCKED: reproduction of SMV2U's 5m_time_matched arm FAILED -- per hard "
          "rules, this subtrack must be marked BLOCKED and no further gates run.",
          flush=True)

# also cross-check the daily curve itself against SMV2U's saved daily_curves.csv column
du = pd.read_csv(os.path.join(SMV2U_OUT, "daily_curves.csv"), parse_dates=["sess"])
du = du.set_index("sess")["5m_time_matched"]
mine_series = daily5.set_index("sess")["net"].reindex(du.index)
curve_max_dev = float(np.abs(mine_series.to_numpy() - du.to_numpy()).max())
print(f"daily curve max|dev| vs SMV2U out/daily_curves.csv[5m_time_matched]: "
      f"{curve_max_dev:.6e} $ over {len(du)} sessions", flush=True)

# ---------------------------------------------------------------- 5. reuse verified 3m incumbent core
inc_cache = np.load(os.path.join(SMV2R_OUT, "cache_incumbent.npz"))
inc_daily = pd.read_csv(os.path.join(SMV2R_OUT, "e10_daily_dev_incumbent.csv"),
                         parse_dates=["sess"])
CAL = inc_daily["sess"]
assert n_cal5 == len(CAL), f"session count mismatch: 5m={n_cal5} vs 3m incumbent={len(CAL)}"
assert list(daily5["sess"]) == list(CAL), "calendar mismatch: 5m core vs 3m incumbent"
print(f"\ncalendar check: 5m core session list EXACTLY matches 3m incumbent's "
      f"{len(CAL)}-session dev calendar: True", flush=True)

# ---------------------------------------------------------------- writeout
np.savez_compressed(os.path.join(OUT, "cache_5m_core.npz"),
                    pend=pend5, pos=pos5, tgt=tgt5, vol_period=N)
daily5.to_csv(os.path.join(OUT, "e10_daily_dev_5m_time_matched.csv"), index=False)
repro_df.to_csv(os.path.join(OUT, "step0_repro_gate.csv"), index=False)

verify = {
    "n_5m_dev_bars": int(len(bars5)), "n_5m_dev_sessions": int(n_cal5),
    "vol_period_bars": N,
    "repro_gate_all_fields_match": repro_all_pass,
    "repro_gate_n_fields_checked": int(len(repro_df)),
    "repro_gate_n_fields_matched": int(repro_df["match"].sum()),
    "daily_curve_max_abs_dev_vs_smv2u_$": curve_max_dev,
    "calendar_matches_3m_incumbent": True,
    "m5_net": m5["net"], "m5_sharpe": m5["sharpe"], "m5_CDaR5": m5["CDaR5"],
    "m5_max_dd": m5["max_dd"], "m5_friction_share": m5["friction_share"],
    "runtime_s": round(time.time() - t0, 1),
}
with open(os.path.join(OUT, "step0_verify.json"), "w") as f:
    json.dump(verify, f, indent=2)
print("\n" + json.dumps(verify, indent=2))
print("\ndone step0", flush=True)
