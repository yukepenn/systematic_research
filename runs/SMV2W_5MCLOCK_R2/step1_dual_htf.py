"""SMV2W_5MCLOCK_R2 STEP 1 -- DUAL_HTF transform applied to the 5m core's T output,
using smv2h.py's / gate_AD.py's EXACT formula (tilt x1.25 / c1_50 / x0.9026 / clip13):

    agree = sign(T) != 0 & st_bar == sign(T)
    m = 1.25 if agree else 1.0
    s = 0.5 if (T < 0 and st_bar > 0) else 1.0
    Tpp = clip(rha(T * m * s * 0.9026), -13, 13)

HTF state (st_bar): prior-SESSION close vs SMA50 of session closes, causal (.shift(1)),
computed from the 3m bars' session-close series (session closes are clock-invariant --
the last bar of a session has the same close price whether the session is diced into
3m or 5m bars, since both are aggregated from the same underlying 1-min ticks up to the
same session boundary) -- verified below bar-for-bar, not assumed.

Applied to BOTH:
  - the 5m core (T5, 13-member, VolPeriod=276, clip +-10 via e10_target) -- the NEW
    challenger DUAL leg, built here for the first time this wave.
  - the 3m incumbent core (T_all, 13-member, clip +-10) -- REUSED from the
    already-committed, already-cross-checked DUAL_ALL leg (SMV2H_ONECONTRACT's
    solar_dual_htf_daily.csv / SMV2H2's tdd_dev_from_tgt.npy), NOT recomputed from
    scratch, per CODE MAP's reuse instruction and mirroring SMV2T gate_AD.py's own
    two integrity checks.

Both DUAL legs are then run through the SAME MNQ E10 executor (common_exec.e10_exec,
verbatim) on their OWN clock's OHLC bars.
"""
import sys, os, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "runs", "SMV2W_5MCLOCK_R2")
OUT = os.path.join(RUN, "out")
sys.path.insert(0, os.path.join(ROOT, "runs", "SMV2R_SOLAR_CORE_1"))
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
from common_exec import e10_exec  # noqa: E402
import sm01_solarsim as sm  # noqa: E402

DEV_END = pd.Timestamp("2026-05-31")
SMV2U_OUT = os.path.join(ROOT, "runs", "SMV2U_CLOCK_CHALLENGE", "out")
SMV2H_OUT = os.path.join(ROOT, "runs", "SMV2H_ONECONTRACT", "out")
SMV2H2_OUT = os.path.join(ROOT, "runs", "SMV2H2_ONELOT_CONFIRM", "out")


def rha(x):
    return np.sign(x) * np.floor(np.abs(x) + 0.5)


def dual_htf(T, st_bar):
    agree = (np.sign(T) != 0) & (st_bar == np.sign(T))
    m = np.where(agree, 1.25, 1.0)
    s = np.where((T < 0) & (st_bar > 0), 0.5, 1.0)
    return np.clip(rha(T * m * s * 0.9026), -13, 13)


# ---------------------------------------------------------------- HTF state (from 3m session closes)
bars3 = sm.load_bars_3m(os.path.join(ROOT, "runs", "AUDIT03_BARS", "nq_3m_2022_2026.csv"))
bars3_dev = bars3[bars3["sess_date"] <= DEV_END.date()].reset_index(drop=True)
sclose = bars3_dev.loc[bars3_dev["is_last_of_sess"], ["sess_date", "close"]].set_index("sess_date")["close"]
htf = np.sign(sclose - sclose.rolling(50).mean()).shift(1).to_dict()
st_bar_3m = np.array([htf.get(d, np.nan) for d in bars3_dev["sess_date"]])

bars5 = pd.read_parquet(os.path.join(SMV2U_OUT, "bars_5m_dev.parquet"))
st_bar_5m = np.array([htf.get(d, np.nan) for d in bars5["sess_date"]])

# integrity check: session close prices agree between 3m-file and 5m-file last bars
sclose5 = bars5.loc[bars5["is_last_of_sess"], ["sess_date", "close"]].set_index("sess_date")["close"]
sclose_join = pd.DataFrame({"c3": sclose, "c5": sclose5}).dropna()
sess_close_max_dev = float((sclose_join["c3"] - sclose_join["c5"]).abs().max())
print(f"session-close cross-check (3m file vs 5m file, {len(sclose_join)} sessions): "
      f"max|dev| = {sess_close_max_dev}", flush=True)
assert sess_close_max_dev < 1e-9, "session close mismatch between 3m and 5m bar files"

# ---------------------------------------------------------------- 5m challenger DUAL leg (NEW this wave)
cache5 = np.load(os.path.join(OUT, "cache_5m_core.npz"))
T5 = cache5["tgt"].astype(float)
assert len(T5) == len(bars5), "5m core cache / bars length mismatch"

Tpp5 = dual_htf(T5, st_bar_5m)
daily_dual5, bar_pos_dual5, bar_pnl_dual5 = e10_exec(bars5, Tpp5.astype(int))
daily_dual5["sess"] = pd.to_datetime(daily_dual5["sess"])
print(f"DUAL_5M built: {len(daily_dual5)} sessions, net={daily_dual5['net'].sum():.1f}, "
      f"tgt range [{Tpp5.min()},{Tpp5.max()}]", flush=True)

# ---------------------------------------------------------------- 3m incumbent DUAL leg (REUSE + cross-check)
tdd_ref_path = os.path.join(SMV2H2_OUT, "tdd_dev_from_tgt.npy")
Tpp_all_ref = np.load(tdd_ref_path)
assert len(Tpp_all_ref) == len(bars3_dev), "Tpp_all ref / 3m dev bars length mismatch"

# rebuild Tpp_all here (independent recomputation) using the SAME dual_htf() to confirm
# our transform function reproduces the already-committed SMV2H2 gate-A T-dd bit-for-bit
inc_cache = np.load(os.path.join(ROOT, "runs", "SMV2R_SOLAR_CORE_1", "out", "cache_incumbent.npz"))
T_all = sm.e10_target(inc_cache["pend"]).astype(float)
Tpp_all_mine = dual_htf(T_all, st_bar_3m)
tpp_all_match = bool((Tpp_all_mine == Tpp_all_ref).all())
print(f"Tpp_all (rebuilt here) matches SMV2H2 gate-A saved tdd_dev_from_tgt.npy "
      f"bit-for-bit on all {len(Tpp_all_ref)} dev bars: {tpp_all_match}", flush=True)

daily_dual_all, _, _ = e10_exec(bars3_dev, Tpp_all_ref.astype(int))
daily_dual_all["sess"] = pd.to_datetime(daily_dual_all["sess"])

ref_dual = pd.read_csv(os.path.join(SMV2H_OUT, "solar_dual_htf_daily.csv"))
ref_dual.columns = ["sess", "net"]
ref_dual["sess"] = pd.to_datetime(ref_dual["sess"]).dt.date
da = daily_dual_all.copy(); da["sess"] = pd.to_datetime(da["sess"]).dt.date
j = ref_dual.merge(da, on="sess", suffixes=("_ref", "_my"))
dual_all_max_dev = float(np.abs(j["net_ref"] - j["net_my"]).max())
print(f"DUAL_ALL (3m incumbent) executed curve matches SMV2H's solar_dual_htf_daily.csv "
      f"max|dev| = {dual_all_max_dev} $ over {len(j)}/{len(ref_dual)} sessions", flush=True)

assert (daily_dual5["sess"].to_numpy() == daily_dual_all["sess"].to_numpy()).all(), \
    "calendar mismatch: DUAL_5M vs DUAL_ALL"

# ---------------------------------------------------------------- writeout
curves = pd.DataFrame({
    "sess": daily_dual_all["sess"],
    "DUAL_ALL": daily_dual_all["net"].to_numpy(),
    "DUAL_5M": daily_dual5["net"].to_numpy(),
    "diff_5m_minus_all": daily_dual5["net"].to_numpy() - daily_dual_all["net"].to_numpy(),
})
curves.to_csv(os.path.join(OUT, "curves.csv"), index=False)

np.save(os.path.join(OUT, "tpp_all_dev.npy"), Tpp_all_ref)
np.save(os.path.join(OUT, "tpp_5m_dev.npy"), Tpp5)

summary = {
    "sess_close_3m_vs_5m_max_abs_dev": sess_close_max_dev,
    "tpp_all_matches_smv2h2_tdd_bitforbit": tpp_all_match,
    "dual_all_executed_curve_max_abs_dev_vs_smv2h_$": dual_all_max_dev,
    "n_dev_days": int(len(curves)),
    "net_DUAL_ALL": float(curves["DUAL_ALL"].sum()),
    "net_DUAL_5M": float(curves["DUAL_5M"].sum()),
}
with open(os.path.join(OUT, "step1_dual_htf_verify.json"), "w") as f:
    json.dump(summary, f, indent=2)
print("\n" + json.dumps(summary, indent=2))
print("\ndone step1", flush=True)
