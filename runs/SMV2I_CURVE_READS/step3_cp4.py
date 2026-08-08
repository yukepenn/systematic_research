"""Seq 363 (real) + 364 (placebo) — C-P4 drought tilt.

Rule (spec-frozen): monthly rebalance; delta_w = min(10, 2.5*z_TUW) percentage points TOWARD
the engine deeper in drought; floors w_solar in [0.35, 0.65]; total exposure unchanged
(w_solar + w_bmom = 1).

Implementation choices (documented, spec-silent details):
  - Legs: A = DUAL (solar), B = vm(BM) (rerank vol-matched bmom leg). TUW is scale-invariant.
  - TUW_t = trading days since the leg's own EOD equity high. gap_t = TUW_A - TUW_B.
  - z_TUW at each rebalance = (gap_dec - expanding_mean(gap)) / expanding_std(gap, ddof=1),
    expanding over ALL daily gap obs up to and including the decision date (last session of
    the prior month). Burn-in: tilt active only when decision date - first session >= 365 cal
    days AND expanding std > 0; otherwise w = 0.60 (champion weight).
  - Tilt is applied to the CHAMPION baseline each month (memoryless):
    w_solar(m) = clip(0.60 + sign(z)*min(10, 2.5*|z|)/100, 0.35, 0.65).
    z > 0 (solar deeper in drought vs its own baseline) tilts toward solar.
  - Portfolio: p_t = vm_outer(w_m(t)*DUAL_t + (1-w_m(t))*vmBM_t), outer vol-match to SIG —
    identical treatment to the champion (equal-vol basis, program convention).
  - Placebo (seq 364): seeds 1..200, same monthly magnitudes, direction = rng.choice([-1,+1]).
Pass gate: real dTUW(longest, champ - policy) AND dSharpe(policy - champ) each exceed
placebo median by > 2x placebo IQR AND leave-2022-out (eval on 2023-01-01+) keeps sign AND
RTC floor >= 0.97 on champion top-decile up-days (full dev window).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd
from smv2i_lib import OUT, repro_gate, tuw_series, rtc_ratio
from smv2_common import dd_battery

res, DUAL, BM, SIG, vm, cal, champ = repro_gate()
assert res["gate_60_40_atol1e-6"]

vmBM = vm(BM)
A = DUAL.values
Bv = vmBM.values
gap = tuw_series(A).astype(float) - tuw_series(Bv).astype(float)
gap_s = pd.Series(gap, index=cal)

# ---- monthly schedule: decision at last session strictly before each month start
months = pd.period_range(cal[0].to_period("M"), cal[-1].to_period("M"), freq="M")
first_date = cal[0]
sched = []
for m in months:
    m_start = m.to_timestamp()
    prior = cal[cal < m_start]
    if len(prior) == 0:  # first month: no history -> champion weight
        sched.append({"month": str(m), "dec_date": None, "gap": np.nan, "z": np.nan,
                      "mag_pp": 0.0, "dir_real": 0, "active": False})
        continue
    dec = prior[-1]
    hist = gap_s.loc[:dec]
    burn_ok = (dec - first_date).days >= 365
    mu, sd = hist.mean(), hist.std(ddof=1)
    if burn_ok and sd > 0:
        z = (hist.iloc[-1] - mu) / sd
        mag = min(10.0, 2.5 * abs(z))
        d = int(np.sign(z)) if z != 0 else 0
        active = True
    else:
        z, mag, d, active = np.nan, 0.0, 0, False
    sched.append({"month": str(m), "dec_date": dec.date(), "gap": hist.iloc[-1],
                  "z": z, "mag_pp": mag, "dir_real": d, "active": active})
sched = pd.DataFrame(sched)

month_of_day = cal.to_period("M").astype(str)
mag_by_month = dict(zip(sched["month"], sched["mag_pp"]))
dir_by_month = dict(zip(sched["month"], sched["dir_real"]))


def build_curve(direction_by_month):
    w = np.array([np.clip(0.60 + direction_by_month[m] * mag_by_month[m] / 100.0, 0.35, 0.65)
                  for m in month_of_day])
    raw = w * A + (1.0 - w) * Bv
    return vm(pd.Series(raw, index=cal)), w


pol, w_real = build_curve(dir_by_month)
sched["w_solar"] = [np.clip(0.60 + dir_by_month[m] * mag_by_month[m] / 100.0, 0.35, 0.65)
                    for m in sched["month"]]

post22 = cal >= pd.Timestamp("2023-01-01")


def deltas(policy_vals):
    bp = dd_battery(cal, policy_vals)
    bc = dd_battery(cal, champ.values)
    d_tuw = bc["longest_TUW_days"] - bp["longest_TUW_days"]
    d_shp = bp["sharpe"] - bc["sharpe"]
    bp2 = dd_battery(cal[post22], policy_vals[post22])
    bc2 = dd_battery(cal[post22], champ.values[post22])
    d_tuw2 = bc2["longest_TUW_days"] - bp2["longest_TUW_days"]
    d_shp2 = bp2["sharpe"] - bc2["sharpe"]
    return d_tuw, d_shp, d_tuw2, d_shp2, bp


d_tuw, d_shp, d_tuw2, d_shp2, batt_pol = deltas(pol.values)
rr, k = rtc_ratio(pol.values, champ.values)
batt_ch = dd_battery(cal, champ.values)

# ---- placebos: seeds 1..200, same magnitudes, random direction per month
prows = []
for seed in range(1, 201):
    rng = np.random.default_rng(seed)
    dirs = {m: int(rng.choice([-1, 1])) for m in sched["month"]}
    pv, _ = build_curve(dirs)
    t1, s1, t2, s2, _ = deltas(pv.values)
    prows.append({"seed": seed, "d_tuw": t1, "d_sharpe": s1,
                  "d_tuw_ex22": t2, "d_sharpe_ex22": s2})
plc = pd.DataFrame(prows)

med_t, med_s = plc["d_tuw"].median(), plc["d_sharpe"].median()
iqr_t = plc["d_tuw"].quantile(0.75) - plc["d_tuw"].quantile(0.25)
iqr_s = plc["d_sharpe"].quantile(0.75) - plc["d_sharpe"].quantile(0.25)

summary = pd.DataFrame([{
    "champ_sharpe": batt_ch["sharpe"], "champ_longest_TUW": batt_ch["longest_TUW_days"],
    "champ_maxDD": batt_ch["maxDD_eod"], "champ_net": batt_ch["net"],
    "pol_sharpe": batt_pol["sharpe"], "pol_longest_TUW": batt_pol["longest_TUW_days"],
    "pol_maxDD": batt_pol["maxDD_eod"], "pol_net": batt_pol["net"],
    "real_d_tuw": d_tuw, "real_d_sharpe": d_shp,
    "real_d_tuw_ex22": d_tuw2, "real_d_sharpe_ex22": d_shp2,
    "placebo_median_d_tuw": med_t, "placebo_iqr_d_tuw": iqr_t,
    "placebo_median_d_sharpe": med_s, "placebo_iqr_d_sharpe": iqr_s,
    "gate_tuw": bool(d_tuw > med_t + 2 * iqr_t),
    "gate_sharpe": bool(d_shp > med_s + 2 * iqr_s),
    "gate_ex22_sign": bool((d_tuw2 > 0) and (d_shp2 > 0)),
    "rtc_ratio": rr, "gate_rtc": bool(rr >= 0.97),
    "n_active_months": int(sched["active"].sum()),
    "n_months": len(sched),
    "PASS": bool((d_tuw > med_t + 2 * iqr_t) and (d_shp > med_s + 2 * iqr_s)
                 and (d_tuw2 > 0) and (d_shp2 > 0) and (rr >= 0.97)),
}])

sched.to_csv(os.path.join(OUT, "c_p4_tilt.csv"), index=False)
plc.to_csv(os.path.join(OUT, "c_p4_placebo.csv"), index=False)
summary.to_csv(os.path.join(OUT, "c_p4_summary.csv"), index=False)
pd.DataFrame({"sess": cal, "champ": champ.values, "tilt": pol.values, "w_solar": w_real}
             ).to_csv(os.path.join(OUT, "c_p4_curves.csv"), index=False)

print(sched.tail(20).to_string())
print()
print(summary.T.to_string())
