# G3_FOMCDRIFT_20260906 -- slow-capital post-FOMC drift in bonds (world-scan #6).
# Preregistered: runs/G3_FOMCDRIFT_20260906/spec.yaml (committed before results).
# Ledger trial G00084, family GENESIS3_EVENT.
#
# ---------------------------------------------------------------------------
# PREREGISTERED DESIGN CONSTANTS (recorded BEFORE any result is computed)
# ---------------------------------------------------------------------------
# Events: FOMC scheduled decision days from the repo calendar artifact
#   runs/GENESIS_H2_CALENDAR_20260828/out/calendar_artifacts/fomc_meetings_2006_2026.csv
#   (fetched from federalreserve.gov, sha printed), decision_date in
#   [2009-01-01, 2026-07-31]; assert ~140 (band 135..145). Cross-checked for
#   identity against the calendar embedded in runs/G2_F12_MC55_FOMCCRUSH_20260906/
#   src/run_mc55.py (the other repo user of the same calendar).
# Data: runs/G3_AUCTCYCLE_20260906/out/{zb_daily,zn_daily}.parquet reused AS-IS;
#   sha256 asserted equal to that run's inputs_manifest.json values (certified
#   causal roll, identity gate 0.0 err, seal max 2026-07-31). POINTS math on the
#   roll-adjusted economic-return column ret_points (DELEV01).
# Signal (causal at D0 close): sign of ZB close(D-1)->close(D0) = sign of
#   ret_points at D0 (roll-adjusted). sign==0 -> NO TRADE (listed).
# PRIMARY: hold ZB in the signal direction close(D0)->close(D+5):
#   x_i = sign_i * sum(ret_points[p+1..p+5]) - COST_PRIMARY_PTS.
# SECONDARY (reported, no gate): mean signal-aligned cumulative path h=1..15.
# ZN mirror (reported, no gate): identical construction on zn_daily with ZN's
#   own signal and ZN tick costs.
# Exclusion rules (mechanical, all listed): decision day before first ZB return
#   day = BEFORE_SERIES; decision day absent from the session calendar =
#   SESSION_MISSING_DATA_HOLE; p+5 beyond the last sealed session =
#   WINDOW_BEYOND_SEAL; ret_points[D0]==0 = ZERO_SIGNAL_NO_TRADE.
# Costs (mirrors G3_ZBMACRO_FALSIFIER cost block; BASIS tagged, never "all-in"):
#   ZB PRIMARY = MODELED $4.36/ctrRT commission + 1 tick/side spread
#     (2*0.03125/2 pt = $62.50 RT) -> $66.86 RT = 0.066860 pt.
#   ZB STRESS  = 2 ticks/side -> $129.36 RT = 0.129360 pt.
#   ZN PRIMARY = $4.36 + 1 tick/side (2*0.015625/2 = $31.25 RT) -> $35.61 RT
#     = 0.035610 pt; ZN STRESS = 2 ticks/side -> $66.86 RT = 0.066860 pt.
#   BASIS = COMMISSION+SPREAD (MODELED); point value $1000/pt both.
# Null (G2): shared-draw circular shift of the WHOLE event-position family along
#   the ZB session-return calendar (one shared offset per draw; dependence
#   preserved); 999 offsets drawn once without replacement from 1..M-1, seed
#   20260906; circular indexing for shifted windows; the frozen rule (incl.
#   zero-signal drop) re-applied at shifted positions; statistic = mean
#   after-cost PRIMARY points. Two-sided p with add-one correction.
# MDE (G1): MDE80 = (1.959964+0.841621) * null_sd, printed BEFORE the observed
#   statistic (null computed first; offset 0 never evaluated).
# CI (G2): event-block bootstrap -- events are non-overlapping blocks (~27+
#   sessions apart; min gap asserted > 5); 10,000 iid resamples of the N event
#   after-cost returns, percentile CI95, seed 20260906. Student-t CI printed as
#   descriptive cross-check only; THE GATE READS THE BOOTSTRAP CI.
# G2 pass = (mean > 0) AND (bootstrap CI95 lower bound > 0) AND (p_two < 0.05).
# G3 control: pool = every non-FOMC ZB session q (q>=1, q+5<=M-1, ret[q]!=0,
#   q not any calendar decision day), same rule, same PRIMARY cost; matched by
#   D0 WEEKDAY (spec-literal). diff_i = x_i - ctrlmean[weekday_i]; pass =
#   mean(diff) > 0. Era x weekday matched version printed as descriptive only.
# G4 eras (mandated): ZLB 2009-2015 / hiking-normalization 2016-2021 /
#   inflation 2022-2026 by D0 year. modern-negative (inflation-era after-cost
#   mean < 0) = FAIL; ZLB-only (+ZLB, <=0 both others) = REGIME-LOCAL-DEAD;
#   else PASS. Signs printed from the program.
# G5: {1,2}-tick/side band printed; procedural gate.
# G6 battery: daily $ mark-to-market series (accrue sign*ret*$1000 on D+1..D+5,
#   cost booked at D+5 exit); weekly-vol annualized Sharpe is the LEAD metric;
#   maxDD/CDaR95 printed as PATH DESCRIPTIVES ONLY (no DD-normalized income --
#   eval_battery thinning-placebo guard honored by never reading those bases as
#   denominators). rho-to-P1: runs/WE_W56_BREADTH/out/p1_daily.csv AS-IS (sha
#   printed; DISCLOSED ~2.0% optimistic Python-chain), zero-filled joint ZB
#   session calendar over the span intersection; daily + weekly rho.
#   rho-to-ZBMACRO01: runs/G3_ZBMACRO_FALSIFIER_20260906/out/trades.csv,
#   profit_net_primary_usd summed by session_date (exit-day attribution: trades
#   are same-session 08:45->15:00), zero-filled joint calendar; daily + weekly.
# DECISION RULE (mechanical): G2 PASS and G3 PASS and G4 PASS ->
#   FOMCDRIFT01 candidate (Class-P). Else CLOSED AT SCOPE (s.28).
# Evidence status of every number below: DISCOVERY_CONSUMED.
# ---------------------------------------------------------------------------

import hashlib
import json
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as sps

RUN = Path(__file__).resolve().parents[1]
REPO = RUN.parents[1]
SPEC = RUN / "spec.yaml"
assert SPEC.exists(), "prereg violation: spec.yaml missing"

import sys
sys.path.insert(0, str(REPO))
from research_sdk.eval_battery import max_drawdown, cdar  # noqa: E402

SEED = 20260906
N_SHIFTS = 999
N_BOOT = 10_000
SEAL = pd.Timestamp("2026-08-01")          # never touch >= this
Z_ALPHA, Z_POWER = 1.959964, 0.841621
POINT_VALUE = 1000.0                        # $/pt, ZB and ZN
EVSTAT = "DISCOVERY_CONSUMED"

COST = {  # $/ctrRT and points/RT; BASIS = COMMISSION+SPREAD (MODELED)
    "ZB": {"tick": 0.03125, "primary_usd": 66.86, "stress_usd": 129.36},
    "ZN": {"tick": 0.015625, "primary_usd": 35.61, "stress_usd": 66.86},
}
for k in COST:
    COST[k]["primary_pts"] = COST[k]["primary_usd"] / POINT_VALUE
    COST[k]["stress_pts"] = COST[k]["stress_usd"] / POINT_VALUE

ERA_DEF = [("ZLB_2009_2015", 2009, 2015),
           ("hiking_2016_2021", 2016, 2021),
           ("inflation_2022_2026", 2022, 2026)]

OUT = RUN / "out"
OUT.mkdir(exist_ok=True)
_log = []


def log(s=""):
    print(s)
    _log.append(s)


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


gate_rows = []


def gate(name, spec_txt, obs_txt, pf):
    gate_rows.append((name, spec_txt, obs_txt, pf))


log("=" * 110)
log("G3_FOMCDRIFT_20260906  slow-capital post-FOMC drift in ZB  |  ledger G00084  |  seed=%d  shifts=%d" % (SEED, N_SHIFTS))
log("evidence status of EVERY number in this file: %s" % EVSTAT)
log("=" * 110)

# ---------------------------------------------------------------- inputs + seal
MANIFEST = REPO / "runs/G3_AUCTCYCLE_20260906/out/inputs_manifest.json"
man = json.loads(MANIFEST.read_text())
ZB_PQ = REPO / "runs/G3_AUCTCYCLE_20260906/out/zb_daily.parquet"
ZN_PQ = REPO / "runs/G3_AUCTCYCLE_20260906/out/zn_daily.parquet"
CAL_CSV = REPO / "runs/GENESIS_H2_CALENDAR_20260828/out/calendar_artifacts/fomc_meetings_2006_2026.csv"
P1_CSV = REPO / "runs/WE_W56_BREADTH/out/p1_daily.csv"
ZBM_CSV = REPO / "runs/G3_ZBMACRO_FALSIFIER_20260906/out/trades.csv"
F12_SRC = REPO / "runs/G2_F12_MC55_FOMCCRUSH_20260906/src/run_mc55.py"

log("\n-- INPUT CERTIFICATION (reused AS-IS; shas printed; seal asserted) --")
zb_sha, zn_sha = sha256(ZB_PQ), sha256(ZN_PQ)
log(f"  zb_daily.parquet sha256 {zb_sha}")
log(f"    manifest ZB sha       {man['ZB']['parquet_sha256']}  match={zb_sha == man['ZB']['parquet_sha256']}")
log(f"  zn_daily.parquet sha256 {zn_sha}")
log(f"    manifest ZN sha       {man['ZN']['parquet_sha256']}  match={zn_sha == man['ZN']['parquet_sha256']}")
assert zb_sha == man["ZB"]["parquet_sha256"], "ZB parquet does not match certified manifest"
assert zn_sha == man["ZN"]["parquet_sha256"], "ZN parquet does not match certified manifest"
log(f"  fomc_meetings_2006_2026.csv sha256 {sha256(CAL_CSV)}")
log(f"  p1_daily.csv sha256 {sha256(P1_CSV)}")
log(f"  zbmacro trades.csv sha256 {sha256(ZBM_CSV)}")

zb = pd.read_parquet(ZB_PQ)
zn = pd.read_parquet(ZN_PQ)
for nm, df in (("ZB", zb), ("ZN", zn)):
    assert df["date"].max() < SEAL, f"SEAL BREACH: {nm} max {df['date'].max()}"
    assert df["ret_points"].isna().sum() == 0
log(f"  seal assert: ZB max {zb['date'].max().date()}, ZN max {zn['date'].max().date()}  (< 2026-08-01)  PASS")
log(f"  ZB rows {len(zb)} span {zb['date'].min().date()}..{zb['date'].max().date()}; "
    f"ZN rows {len(zn)} span {zn['date'].min().date()}..{zn['date'].max().date()}")
log("  certification carried from G3_AUCTCYCLE: causal roll unit tests ALL PASS, identity gate max err 0.0 (both)")

# ---------------------------------------------------------------- FOMC calendar
cal_full = pd.read_csv(CAL_CSV, parse_dates=["start_date", "decision_date"])
ev = cal_full[(cal_full["decision_date"] >= "2009-01-01")
              & (cal_full["decision_date"] <= "2026-07-31")].reset_index(drop=True)
n_cal = len(ev)
log("\n-- FOMC CALENDAR (the repo artifact; scheduled decisions only -- conference calls/unscheduled excluded at parse) --")
log(f"  calendar rows 2006..2026: {len(cal_full)}; events in window 2009-01-01..2026-07-31: {n_cal}")
per_yr = ev["decision_date"].dt.year.value_counts().sort_index()
log(f"  per-year: {dict(per_yr)}   (2020 has 7: the 2020-03 meeting was cancelled)")
assert 135 <= n_cal <= 145, f"coverage assert failed: {n_cal} events, expected ~140"
assert ev["decision_date"].min() == pd.Timestamp("2009-01-28")
assert ev["decision_date"].max() == pd.Timestamp("2026-07-29")
log("  coverage assert PASS: 140-band [135,145], first 2009-01-28, last 2026-07-29")

# cross-check vs the calendar embedded in G2_F12 (run_mc55.py _CAL dict)
f12_txt = F12_SRC.read_text(encoding="utf-8")
blk = re.search(r"_CAL = \{(.*?)\n\}", f12_txt, re.S).group(1)
f12_dates = set()
for yr, body in re.findall(r"(\d{4}): \[([^\]]*)\]", blk):
    for token in re.findall(r'"(\d{2}-\d{2})P?"', body):
        f12_dates.add(pd.Timestamp(f"{yr}-{token}"))
csv_cmp = set(cal_full.loc[cal_full["decision_date"] <= "2026-04-30", "decision_date"])
f12_cmp = {d for d in f12_dates if d <= pd.Timestamp("2026-04-30")}
sym = csv_cmp.symmetric_difference(f12_cmp)
log(f"  cross-check vs G2_F12 embedded calendar (2006..2026-04): csv={len(csv_cmp)} f12={len(f12_cmp)} "
    f"symmetric-diff={sorted(str(d.date()) for d in sym) if sym else 'NONE -- identical'}")

# ------------------------------------------------- event realization on ZB
zb_dates = pd.DatetimeIndex(zb["date"])
ret = zb["ret_points"].to_numpy()
clean = zb["clean_daily"].to_numpy()
M = len(zb)
pos_of = {d: i for i, d in enumerate(zb_dates)}
fomc_all_in_cal = {pos_of[d] for d in cal_full["decision_date"] if d in pos_of}  # every decision day present

excluded, events = [], []
for d in ev["decision_date"]:
    if d not in pos_of:
        reason = "BEFORE_SERIES" if d < zb_dates[0] else "SESSION_MISSING_DATA_HOLE"
        excluded.append((d, reason))
        continue
    p = pos_of[d]
    if p < 1:
        excluded.append((d, "NO_SIGNAL_HISTORY"))
        continue
    if p + 5 > M - 1:
        excluded.append((d, "WINDOW_BEYOND_SEAL"))
        continue
    events.append(p)
events = np.array(sorted(events))
sig_raw = ret[events]
zero_mask = sig_raw == 0.0
zero_listed = [(zb_dates[p], "ZERO_SIGNAL_NO_TRADE") for p in events[zero_mask]]
tr_pos = events[~zero_mask]
N = len(tr_pos)
gaps = np.diff(tr_pos)
log("\n-- EVENT REALIZATION (ZB) --")
log(f"  excluded ({len(excluded)}):")
for d, r in excluded:
    log(f"    {d.date()}  {r}")
log(f"  zero-signal no-trade ({len(zero_listed)}):" + (" none" if not zero_listed else ""))
for d, r in zero_listed:
    log(f"    {d.date()}  {r}")
log(f"  realized traded events N = {N}  (calendar 140 -> -{len(excluded)} excluded -> -{len(zero_listed)} zero-signal)")
assert gaps.min() > 5, "event 5-day windows overlap -- design assumption violated"
log(f"  min gap between consecutive events = {gaps.min()} sessions (> 5: windows never overlap)  PASS")

sign = np.sign(ret[tr_pos])
CP = COST["ZB"]["primary_pts"]
CS = COST["ZB"]["stress_pts"]

# window helper (non-circular, only valid p+5 <= M-1 by construction)
cum5 = np.array([ret[p + 1:p + 6].sum() for p in tr_pos])
gross = sign * cum5
x_primary = gross - CP
x_stress = gross - CS
wd = np.array([zb_dates[p].dayofweek for p in tr_pos])
yr = np.array([zb_dates[p].year for p in tr_pos])
era_idx = np.array([next(i for i, (_, a, b) in enumerate(ERA_DEF) if a <= y <= b) for y in yr])
nonclean_ct = np.array([int((~clean[p:p + 6]).sum()) for p in tr_pos])

# ------------------------------------------------- G1: null FIRST, MDE printed
rng = np.random.default_rng(SEED)
offsets = rng.choice(M - 1, size=N_SHIFTS, replace=False) + 1


def stat_at(k):
    q = (tr_pos + k) % M
    s = np.sign(ret[q])
    idx = np.arange(1, 6)[None, :]
    win = ret[(q[:, None] + idx) % M]
    x = s * win.sum(axis=1) - CP
    return x[s != 0].mean()


null_T = np.array([stat_at(k) for k in offsets])
null_sd = null_T.std(ddof=1)
mde80 = (Z_ALPHA + Z_POWER) * null_sd

log("\n-- G1: MDE (printed BEFORE the observed statistic; null computed first; offset 0 never evaluated) --")
log("  SEMANTIC (what the p-value is over): the population is the %d scheduled FOMC decision days 2009-04..2026-06" % N)
log("  that trade on the certified ZB calendar with a nonzero D-1->D0 move and a complete D+5 window; the event is")
log("  'mean after-cost points of holding ZB 5 sessions in the direction of the announcement-day move'; the p is the")
log("  two-sided probability, under %d shared circular shifts of the whole event family along the %d-session" % (N_SHIFTS, M))
log("  calendar (dependence preserved; rule incl. zero-signal drop re-applied at shifted positions), of |T| >= |T_obs|.")
log(f"  null sd = {null_sd:.4f} pt   MDE80 (two-sided alpha .05, 80% power) = {mde80:.4f} pt  (${mde80 * POINT_VALUE:,.0f}/ct at $1000/pt)")
gate("G1_MDE_first", "MDE printed before observed (~140 events)",
     f"N={N} traded of {n_cal} calendar; MDE80={mde80:.4f} pt (${mde80 * POINT_VALUE:,.0f}); printed first (procedural)", "PASS")

# ------------------------------------------------- observed + G2
T_obs = x_primary.mean()
p_two = (1 + int(np.sum(np.abs(null_T) >= abs(T_obs)))) / (N_SHIFTS + 1)
boot = rng.choice(x_primary, size=(N_BOOT, N), replace=True).mean(axis=1)
ci_lo, ci_hi = np.percentile(boot, [2.5, 97.5])
tcrit = sps.t.ppf(0.975, N - 1)
se = x_primary.std(ddof=1) / math.sqrt(N)
tci = (T_obs - tcrit * se, T_obs + tcrit * se)
hit = float((x_primary > 0).mean())

log("\n-- G2: PRIMARY after-cost edge --")
log(f"  gross mean          = {gross.mean():+.4f} pt  (${gross.mean() * POINT_VALUE:+,.0f}/ct)")
log(f"  after-cost mean     = {T_obs:+.4f} pt  (${T_obs * POINT_VALUE:+,.0f}/ct)   [PRIMARY cost {CP:.5f} pt = $66.86 RT, BASIS COMMISSION+SPREAD MODELED]")
log(f"  event-block bootstrap CI95 = [{ci_lo:+.4f}, {ci_hi:+.4f}] pt   (10,000 draws, events are non-overlapping blocks)")
log(f"  [descriptive cross-check, NOT the gate: t-CI95 = [{tci[0]:+.4f}, {tci[1]:+.4f}]; t = {T_obs / se:+.2f}]")
log(f"  shift-null two-sided p = {p_two:.4f}  (add-one, {N_SHIFTS} shifts)")
log(f"  hit rate = {hit:.3f}   per-event sd = {x_primary.std(ddof=1):.4f} pt")
g2 = (T_obs > 0) and (ci_lo > 0) and (p_two < 0.05)
gate("G2_edge", "after-cost mean > 0 AND event-block CI95 excludes 0 AND shift-null p < 0.05",
     f"mean {T_obs:+.4f} pt, CI [{ci_lo:+.4f},{ci_hi:+.4f}], p {p_two:.4f}", "PASS" if g2 else "FAIL")
underpowered = (not g2) and (mde80 > 3 * abs(T_obs))
log(f"  power language: MDE80={mde80:.4f} vs 3x|obs|={3 * abs(T_obs):.4f} -> "
    + ("UNDERPOWERED_STILL" if underpowered else ("n/a (G2 PASS)" if g2 else "FAIL is powered (MDE <= 3x|obs|)")))

# ------------------------------------------------- G3 control
pool = np.array([q for q in range(1, M - 5)
                 if q not in fomc_all_in_cal and ret[q] != 0.0])
psig = np.sign(ret[pool])
pidx = np.arange(1, 6)[None, :]
pwin = ret[pool[:, None] + pidx]        # non-circular; q+5 <= M-1 by range
px = psig * pwin.sum(axis=1) - CP
pwd = np.array([zb_dates[q].dayofweek for q in pool])
pyr = np.array([zb_dates[q].year for q in pool])
pera = np.array([next(i for i, (_, a, b) in enumerate(ERA_DEF) if a <= y <= b) for y in pyr])

wd_names = ["Mon", "Tue", "Wed", "Thu", "Fri"]
ctrl_wd = {w: px[pwd == w].mean() for w in range(5)}
diff = x_primary - np.array([ctrl_wd[w] for w in wd])
ctrl_matched_mean = T_obs - diff.mean()
log("\n-- G3: matched non-FOMC same-weekday control (same rule, same 5-day window, same cost) --")
log(f"  control pool: {len(pool)} non-FOMC sessions (every calendar decision day excluded); by weekday: "
    + ", ".join(f"{wd_names[w]} {int((pwd == w).sum())}" for w in range(5)))
log(f"  event weekday mix: " + ", ".join(f"{wd_names[w]} {int((wd == w).sum())}" for w in range(5) if (wd == w).any()))
log(f"  ctrl mean by weekday (after-cost pt): " + ", ".join(f"{wd_names[w]} {ctrl_wd[w]:+.4f}" for w in range(5)))
log(f"  FOMC after-cost mean {T_obs:+.4f} vs weekday-matched control {ctrl_matched_mean:+.4f}  ->  diff {diff.mean():+.4f} pt")
era_wd_note = []
ctrl_ew = {}
for e in range(3):
    for w in range(5):
        m = (pera == e) & (pwd == w)
        if m.any():
            ctrl_ew[(e, w)] = px[m].mean()
diff_ew = x_primary - np.array([ctrl_ew[(e, w)] for e, w in zip(era_idx, wd)])
log(f"  [descriptive, NOT the gate: era x weekday matched diff = {diff_ew.mean():+.4f} pt]")
g3 = diff.mean() > 0
gate("G3_control", "beats matched non-FOMC same-weekday days (same 5-day window)",
     f"diff {diff.mean():+.4f} pt (FOMC {T_obs:+.4f} vs ctrl {ctrl_matched_mean:+.4f})", "PASS" if g3 else "FAIL")

# ------------------------------------------------- G4 era split (mandated)
log("\n-- G4: era split (mandated: ZLB 2009-15 / hiking-normalization 2016-21 / inflation 2022-26) --")
era_rows = []
for e, (nm, a, b) in enumerate(ERA_DEF):
    m = era_idx == e
    n_e = int(m.sum())
    gm, am = gross[m].mean(), x_primary[m].mean()
    era_rows.append(dict(era=nm, n=n_e, gross_mean_pts=round(gm, 4), aftercost_mean_pts=round(am, 4),
                         aftercost_mean_usd=round(am * POINT_VALUE, 2), sign="pos" if am > 0 else "neg",
                         hit=round(float((x_primary[m] > 0).mean()), 3), evidence_status=EVSTAT))
    log(f"  {nm:22s} n={n_e:3d}  gross {gm:+.4f}  after-cost {am:+.4f} pt (${am * POINT_VALUE:+,.0f}/ct)  "
        f"sign={'pos' if am > 0 else 'neg'}  hit={float((x_primary[m] > 0).mean()):.3f}")
era_df = pd.DataFrame(era_rows)
era_df.to_csv(OUT / "era_table.csv", index=False)
am_by = {r["era"]: r["aftercost_mean_pts"] for r in era_rows}
modern_neg = am_by["inflation_2022_2026"] < 0
zlb_only = (am_by["ZLB_2009_2015"] > 0) and (am_by["hiking_2016_2021"] <= 0) and (am_by["inflation_2022_2026"] <= 0)
if modern_neg:
    g4_status, g4_pf = "FAIL (modern-negative)", "FAIL"
elif zlb_only:
    g4_status, g4_pf = "REGIME-LOCAL-DEAD (ZLB-only; the regime ended)", "FAIL"
else:
    g4_status, g4_pf = "PASS (not modern-negative, not ZLB-only)", "PASS"
log(f"  G4 classification: {g4_status}")
gate("G4_era_mandated", "signs printed; modern-negative = FAIL; ZLB-only = REGIME-LOCAL-DEAD",
     f"{', '.join(r['era'] + ':' + r['sign'] for r in era_rows)} -> {g4_status}", g4_pf)

# ------------------------------------------------- G5 cost band
log("\n-- G5: cost band ({1,2} ticks/side + $4.36/ctrRT commission; BASIS COMMISSION+SPREAD MODELED, not all-in) --")
log(f"  PRIMARY rung (1 tick/side): $66.86 RT = {CP:.5f} pt  -> after-cost mean {T_obs:+.4f} pt")
log(f"  STRESS  rung (2 ticks/side): $129.36 RT = {CS:.5f} pt -> after-cost mean {x_stress.mean():+.4f} pt")
log(f"  cost is {CP / gross.std(ddof=1) * 100:.1f}% of the per-event gross sd ({gross.std(ddof=1):.3f} pt) -- trivial at 5d hold")
sign_flip = (T_obs > 0) != (x_stress.mean() > 0)
log(f"  stress rung flips the sign of the mean: {'YES' if sign_flip else 'NO'}")
gate("G5_cost", "trivial at 5d; {1,2}-tick band printed",
     f"primary {T_obs:+.4f}, stress {x_stress.mean():+.4f} pt; flip={'YES' if sign_flip else 'NO'}", "PASS")

# ------------------------------------------------- G6 battery
daily = pd.Series(0.0, index=zb_dates)
for p, s in zip(tr_pos, sign):
    daily.iloc[p + 1:p + 6] += s * ret[p + 1:p + 6] * POINT_VALUE
    daily.iloc[p + 5] -= COST["ZB"]["primary_usd"]
wk = daily.groupby(daily.index.to_period("W")).sum()
wk_mean, wk_sd = float(wk.mean()), float(wk.std(ddof=1))
sharpe_wk = wk_mean / wk_sd * math.sqrt(52) if wk_sd > 0 else float("nan")
yrs = len(wk) / 52.0
log("\n-- G6: battery (net PRIMARY $/ct; weekly-vol LEAD; %s) --" % EVSTAT)
log(f"  weekly grid: {len(wk)} calendar weeks ({yrs:.2f} yr), zeros where flat")
log(f"  LEAD  weekly-vol annualized Sharpe = {sharpe_wk:.2f}  (mean ${wk_mean:.1f}/wk, sd ${wk_sd:.1f}/wk)")
log(f"  native: total net ${float(daily.sum()):,.0f} over {yrs:.2f} yr = ${float(daily.sum()) / yrs:,.0f}/yr "
    f"on {N / yrs:.1f} trades/yr (${T_obs * POINT_VALUE:+.1f}/trade)")
log(f"  path descriptives ONLY (research_sdk.eval_battery): weekly maxDD ${max_drawdown(wk.to_numpy()):,.0f}, "
    f"CDaR95 ${cdar(wk.to_numpy()):,.0f}; daily maxDD ${max_drawdown(daily.to_numpy()):,.0f}")
log("  NO fixed-DD- or CDaR-normalized income figure is quoted; the eval_battery thinning-placebo guard is")
log("  honored by never reading those bases as a denominator.")

p1 = pd.read_csv(P1_CSV, index_col=0, parse_dates=True)["p1_usd"]
assert p1.index.max() < SEAL, "SEAL VIOLATION: P1 daily"
cal_j = zb_dates[(zb_dates >= p1.index.min()) & (zb_dates <= p1.index.max())]
p1_al = p1.reindex(cal_j).fillna(0.0)
fd_al = daily.reindex(cal_j).fillna(0.0)
rho_p1_d = float(np.corrcoef(p1_al, fd_al)[0, 1])
rho_p1_w = float(np.corrcoef(p1_al.groupby(p1_al.index.to_period('W')).sum(),
                             fd_al.groupby(fd_al.index.to_period('W')).sum())[0, 1])
log(f"  rho to P1 (runs/WE_W56_BREADTH/out/p1_daily.csv AS-IS; DISCLOSED ~2.0% optimistic Python chain;")
log(f"    zero-filled joint ZB-session calendar {cal_j.min().date()}..{cal_j.max().date()}, {len(cal_j)} sessions, "
    f"{int((fd_al != 0).sum())} active days ours):")
log(f"    daily rho = {rho_p1_d:+.4f}   weekly rho = {rho_p1_w:+.4f}")

zbm = pd.read_csv(ZBM_CSV, parse_dates=["session_date"])
assert zbm["session_date"].max() < SEAL, "SEAL VIOLATION: ZBMACRO trades"
zbm_daily = zbm.groupby("session_date")["profit_net_primary_usd"].sum()
cal_z = zb_dates[(zb_dates >= zbm_daily.index.min()) & (zb_dates <= min(zbm_daily.index.max(), zb_dates.max()))]
zbm_al = zbm_daily.reindex(cal_z).fillna(0.0)
fdz_al = daily.reindex(cal_z).fillna(0.0)
rho_zbm_d = float(np.corrcoef(zbm_al, fdz_al)[0, 1])
rho_zbm_w = float(np.corrcoef(zbm_al.groupby(zbm_al.index.to_period('W')).sum(),
                              fdz_al.groupby(fdz_al.index.to_period('W')).sum())[0, 1])
n_zbm_in = int((zbm_al != 0).sum())
log(f"  rho to ZBMACRO01 (runs/G3_ZBMACRO_FALSIFIER_20260906/out/trades.csv, profit_net_primary_usd summed by")
log(f"    session_date = EXIT-DAY attribution [same-session 08:45->15:00 trades]; zero-filled joint calendar")
log(f"    {cal_z.min().date()}..{cal_z.max().date()}, {len(cal_z)} sessions; {n_zbm_in}/{len(zbm)} ZBMACRO trades in overlap):")
log(f"    daily rho = {rho_zbm_d:+.4f}   weekly rho = {rho_zbm_w:+.4f}   (same-market stacking question)")
gate("G6_battery", "weekly-vol lead; rho-to-P1 and rho-to-ZBMACRO01 printed",
     f"Sharpe_wk {sharpe_wk:.2f}; rho_P1 d {rho_p1_d:+.3f}/w {rho_p1_w:+.3f}; "
     f"rho_ZBM d {rho_zbm_d:+.3f}/w {rho_zbm_w:+.3f}", "PASS")

# ------------------------------------------------- SECONDARY: D+1..D+15 path
log("\n-- SECONDARY (reported, no gate): mean signal-aligned cumulative path, h = 1..15 sessions after D0 --")
log("   h | n   | gross mean pt | after-cost(1-tick) pt")
path_cols = {}
for h in range(1, 16):
    ok = tr_pos + h <= M - 1
    cum = np.array([np.sign(ret[p]) * ret[p + 1:p + h + 1].sum() for p in tr_pos[ok]])
    path_cols[h] = (int(ok.sum()), cum.mean(), cum.mean() - CP)
    log(f"  {h:2d} | {int(ok.sum()):3d} | {cum.mean():+.4f}       | {cum.mean() - CP:+.4f}")

# ------------------------------------------------- ZN mirror (reported)
zn_dates = pd.DatetimeIndex(zn["date"])
retn = zn["ret_points"].to_numpy()
Mn = len(zn)
pos_n = {d: i for i, d in enumerate(zn_dates)}
zn_excl, zn_pos = [], []
for d in ev["decision_date"]:
    if d not in pos_n:
        zn_excl.append((d, "BEFORE_SERIES" if d < zn_dates[0] else "SESSION_MISSING_DATA_HOLE"))
    elif pos_n[d] < 1:
        zn_excl.append((d, "NO_SIGNAL_HISTORY"))
    elif pos_n[d] + 5 > Mn - 1:
        zn_excl.append((d, "WINDOW_BEYOND_SEAL"))
    elif retn[pos_n[d]] == 0.0:
        zn_excl.append((d, "ZERO_SIGNAL_NO_TRADE"))
    else:
        zn_pos.append(pos_n[d])
zn_pos = np.array(sorted(zn_pos))
sn = np.sign(retn[zn_pos])
grossn = sn * np.array([retn[p + 1:p + 6].sum() for p in zn_pos])
CPN = COST["ZN"]["primary_pts"]
xn = grossn - CPN
rng_n = np.random.default_rng(SEED)
off_n = rng_n.choice(Mn - 1, size=N_SHIFTS, replace=False) + 1


def stat_zn(k):
    q = (zn_pos + k) % Mn
    s = np.sign(retn[q])
    win = retn[(q[:, None] + np.arange(1, 6)[None, :]) % Mn]
    x = s * win.sum(axis=1) - CPN
    return x[s != 0].mean()


null_n = np.array([stat_zn(k) for k in off_n])
p_n = (1 + int(np.sum(np.abs(null_n) >= abs(xn.mean())))) / (N_SHIFTS + 1)
boot_n = rng_n.choice(xn, size=(N_BOOT, len(xn)), replace=True).mean(axis=1)
ci_n = np.percentile(boot_n, [2.5, 97.5])
yrn = np.array([zn_dates[p].year for p in zn_pos])
log("\n-- ZN MIRROR (reported, no gate; ZN's own signal; ZN costs $35.61/$66.86 RT) --")
log(f"  excluded: {[(str(d.date()), r) for d, r in zn_excl]}")
log(f"  n={len(xn)}  gross mean {grossn.mean():+.4f} pt  after-cost mean {xn.mean():+.4f} pt "
    f"(${xn.mean() * POINT_VALUE:+,.0f}/ct)  CI95 [{ci_n[0]:+.4f},{ci_n[1]:+.4f}]  shift-null p {p_n:.4f}")
for nm, a, b in ERA_DEF:
    m = (yrn >= a) & (yrn <= b)
    log(f"    {nm:22s} n={int(m.sum()):3d}  after-cost {xn[m].mean():+.4f} pt  sign={'pos' if xn[m].mean() > 0 else 'neg'}")

# ------------------------------------------------- event table
rows = []
for i, p in enumerate(tr_pos):
    r = dict(date=str(zb_dates[p].date()), weekday=wd_names[wd[i]], era=ERA_DEF[era_idx[i]][0],
             signal_pts=round(float(ret[p]), 5), side="LONG" if sign[i] > 0 else "SHORT",
             gross_pts_5d=round(float(gross[i]), 5),
             aftercost_primary_pts=round(float(x_primary[i]), 5),
             aftercost_stress_pts=round(float(x_stress[i]), 5),
             net_primary_usd=round(float(x_primary[i]) * POINT_VALUE, 2),
             ctrl_mean_weekday_pts=round(float(ctrl_wd[wd[i]]), 5),
             diff_vs_ctrl_pts=round(float(diff[i]), 5),
             nonclean_days_in_window=int(nonclean_ct[i]),
             status="TRADED", evidence_status=EVSTAT)
    for h in range(1, 16):
        r[f"cum_gross_pts_h{h}"] = (round(float(np.sign(ret[p]) * ret[p + 1:p + h + 1].sum()), 5)
                                    if p + h <= M - 1 else "")
    rows.append(r)
for d, reason in excluded + zero_listed:
    rows.append(dict(date=str(d.date()), weekday=wd_names[d.dayofweek], era="", signal_pts="", side="",
                     gross_pts_5d="", aftercost_primary_pts="", aftercost_stress_pts="", net_primary_usd="",
                     ctrl_mean_weekday_pts="", diff_vs_ctrl_pts="", nonclean_days_in_window="",
                     status="EXCLUDED_" + reason, evidence_status=EVSTAT))
ev_df = pd.DataFrame(rows).sort_values("date")
ev_df.to_csv(OUT / "event_table.csv", index=False)

# ------------------------------------------------- gate table + verdict
log("\n" + "=" * 110)
log("GATE TABLE (program-printed)")
log("=" * 110)
w1 = max(len(g[0]) for g in gate_rows)
log(f"{'GATE':<{w1}} | {'PASS-FAIL':<9} | SPEC | OBSERVED")
log("-" * 110)
for name, sp, ob, pf in gate_rows:
    log(f"{name:<{w1}} | {pf:<9} | {sp} | {ob}")
log("-" * 110)
g4_ok = g4_pf == "PASS"
if g2 and g3 and g4_ok:
    verdict = "FOMCDRIFT01 CANDIDATE (Class-P; natural stack-sibling of ZBMACRO01 if low rho)"
else:
    why = []
    if not g2:
        why.append("G2 FAIL" + (" UNDERPOWERED_STILL" if underpowered else ""))
    if not g3:
        why.append("G3 FAIL")
    if not g4_ok:
        why.append("G4 " + g4_status)
    verdict = "CLOSED AT SCOPE (s.28): " + "; ".join(why)
log(f"VERDICT: {verdict}")
log(f"Every number above: evidence status {EVSTAT}.")

(OUT / "gate_table.txt").write_text("\n".join(_log) + "\n", encoding="utf-8")
print(f"\nwrote {OUT / 'gate_table.txt'}, event_table.csv ({len(ev_df)} rows), era_table.csv")
