# G3_FXOVERSHOOT_20260906 -- delayed FX overshooting after FOMC (world-scan #20; opens the 6E row).
# Preregistered: runs/G3_FXOVERSHOOT_20260906/spec.yaml (committed before results, git cd14e0e).
# Ledger trial G00089, family GENESIS3_EVENT.
#
# ---------------------------------------------------------------------------
# PREREGISTERED DESIGN CONSTANTS (recorded BEFORE any result is computed)
# ---------------------------------------------------------------------------
# Events: FOMC scheduled decision days from the same repo calendar artifact G00084 used
#   (runs/GENESIS_H2_CALENDAR_20260828/out/calendar_artifacts/fomc_meetings_2006_2026.csv,
#   sha printed), decision_date in [2009-01-01, 2026-07-31] (assert exactly 140, as realized
#   by G00084), MINUS the 4 data-hole dates G00084 recorded (SESSION_MISSING_DATA_HOLE in
#   its REPORT.md): 2014-01-29, 2015-12-16, 2018-12-19, 2024-12-18 -> 136 calendar events.
# Data (reused AS-IS, shas printed and asserted):
#   6E: runs/DAILY_6E_EXTRACT_AUTOPSY_20260906/out/6e_daily.parquet, sha asserted equal to
#     the value recorded in that run's extract_meta.json (causal 5-day-pre-expiry roll,
#     point-return reproduction vs certified s7 construction max err 0.0). POINTS math on
#     ret_points (DELEV01); point value $125,000/pt; span 2009-03-30..2026-07-31.
#   ZN: runs/G3_AUCTCYCLE_20260906/out/zn_daily.parquet, sha asserted equal to that run's
#     inputs_manifest.json (certified causal roll, identity gate 0.0 err); signal only.
#   Seal: both series max date < 2026-08-01 asserted.
# Signal (causal at D0 close): sign of ZN close(D-1)->close(D0) = sign of ZN ret_points at
#   D0 (roll-adjusted). SIGN CONVENTION (stated in spec.yaml BEFORE results): rates DOWN =
#   ZN price UP = dovish = USD-negative => 6E UP expected under delayed overshooting, so
#   6E position side = sign(ZN ret_points[D0]). sign==0 -> ZERO_SIGNAL_NO_TRADE (listed).
# PRIMARY: hold 6E in the signal-implied direction close(D0)->close(D+10) on the 6E session
#   calendar: x_i = side_i * sum(6e ret_points[q+1..q+10]) - COST_PRIMARY_PTS.
# SECONDARY (reported, no gate): {D+5, D+20} after-cost means; full h=1..20 path printed.
# Exclusion rules (mechanical, FIRST failing check names the reason, all listed):
#   1. decision day before first ZN session = ZN_BEFORE_SERIES; absent from ZN calendar =
#      SIGNAL_SESSION_MISSING; ZN position 0 = NO_SIGNAL_HISTORY.
#   2. decision day before first 6E session = 6E_BEFORE_SERIES; absent from 6E calendar =
#      6E_SESSION_MISSING.
#   3. q+10 beyond last sealed 6E session = WINDOW_BEYOND_SEAL.
#   4. ZN ret_points[D0]==0 = ZERO_SIGNAL_NO_TRADE.
# Costs (BASIS = COMMISSION+SPREAD, MODELED -- never called "all-in"):
#   6E tick 0.00005 pt = $6.25. PRIMARY = $4.36/ctrRT commission + 1 tick/side spread
#     (2 ticks RT = $12.50) -> $16.86 RT = 0.00013488 pt.
#   STRESS = 2 ticks/side (4 ticks RT = $25.00) + $4.36 -> $29.36 RT = 0.00023488 pt.
# Null (G2): shared-draw circular shift of the WHOLE traded-event family along the 6E
#   session calendar (one shared offset per draw; dependence preserved, including the
#   contemporaneous ZN<->6E linkage: the shifted signal is ZN's ret on the SHIFTED DATE);
#   999 offsets drawn once without replacement from 1..M6-1, seed 20260906; circular
#   indexing for shifted 6E windows; frozen rule re-applied at shifted positions (pseudo-
#   date absent from ZN calendar -> drop, zero ZN signal -> drop); statistic = mean
#   after-cost PRIMARY points. Two-sided p with add-one correction.
# MDE (G1): MDE80 = (1.959964+0.841621) * null_sd, printed BEFORE the observed statistic
#   (null computed first; offset 0 never evaluated).
# CI (G2): event-block bootstrap -- events are non-overlapping blocks (min 6E-session gap
#   asserted > 10); 10,000 iid resamples of the N event after-cost returns, percentile
#   CI95, seed 20260906 (same stream, drawn after the null). Student-t CI printed as the
#   SECOND COMPUTATION of the same event (descriptive cross-check; THE GATE READS THE
#   BOOTSTRAP CI).
# G2 pass = (mean > 0) AND (bootstrap CI95 lower bound > 0) AND (p_two < 0.05).
# G3 control -- TWO clauses, BOTH required to pass (spec: "beats matched ... AND survives
#   drift-residualization"):
#   (a) pool = every 6E session q with q+10 <= M6-1, whose date is in the ZN calendar at
#       ZN position >= 1 with ZN ret != 0, and which is NOT any calendar decision day
#       (full 2006..2026 artifact); same rule (side = sign of ZN ret that day), same
#       10-day window, same PRIMARY cost; matched by D0 WEEKDAY.
#       diff_i = x_i - ctrlmean[weekday_i]; clause pass = mean(diff) > 0.
#   (b) drift-residualization: drift60_i = mean(6e ret_points[q-60..q-1]) (60 sessions
#       strictly before D0, causal, uncontaminated by the event day); resid_i =
#       side_i * (cum10_i - 10*drift60_i) - COST_PRIMARY_PTS, computed on the subset with
#       full 60-session history (events lacking it listed RESID_INSUFFICIENT_HISTORY,
#       still in PRIMARY); clause pass = mean(resid) > 0.
#   LIMITATION (stated, never hidden): full rate-differential carry is not locally
#   computable (no EUR-USD short-rate differential series in the local store); the
#   trailing-60d unconditional drift is the reachable residualization.
# G4 (Scholl-Uhlig subsample fragility, the card's own clause): traded events sorted by
#   date, split into three contiguous near-equal-count thirds (np.array_split). After-cost
#   mean and sign printed per third. FAIL iff EXACTLY ONE third has after-cost mean > 0
#   (the effect lives in one third); PASS otherwise. Written to out/era_thirds.csv.
# G5: {1,2}-tick/side band printed; 10-day hold; procedural gate.
# DECISION RULE (mechanical, from spec.yaml): G2 PASS and G3 PASS and G4 PASS ->
#   FXOVERSHOOT01 candidate (first 6E object). Else CLOSED AT SCOPE (S28 block) -- either
#   way the 6E event-transition cell gets its first entry.
# AMENDMENT (recorded on input inspection, BEFORE any outcome was computed; disclosed in
#   REPORT.md): the certified 6E store contains 46 structural roll-gap sessions with NaN
#   ret_points (contract lives barely overlap -- named in extract_meta.json; its certified
#   s7 reproduction is over the 4,227 defined rows). NaN handling rule, applied uniformly:
#   - a 6E economic return that is NaN is NOT COMPUTABLE; any event whose D+1..D+HOLD
#     window contains one is excluded and listed (WINDOW_ROLL_GAP) -- never zero-filled;
#   - the same drop is re-applied to shifted pseudo-events inside the null and to
#     control-pool sessions (frozen rule re-applied everywhere);
#   - secondary h-paths: per-h, events with a NaN inside D+1..D+h are dropped from that
#     h's mean (n printed per h);
#   - drift60 (auxiliary residualizer, not the traded object): nanmean over the trailing
#     60 sessions, requiring >= 50 defined values (counts printed).
# Evidence status of every number below: DISCOVERY_CONSUMED.
# ---------------------------------------------------------------------------

import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as sps

RUN = Path(__file__).resolve().parents[1]
REPO = RUN.parents[1]
SPEC = RUN / "spec.yaml"
assert SPEC.exists(), "prereg violation: spec.yaml missing"

SEED = 20260906
N_SHIFTS = 999
N_BOOT = 10_000
SEAL = pd.Timestamp("2026-08-01")
Z_ALPHA, Z_POWER = 1.959964, 0.841621
POINT_VALUE = 125_000.0                     # $/pt, 6E (extract_meta.json)
EVSTAT = "DISCOVERY_CONSUMED"
HOLD = 10                                   # PRIMARY horizon, 6E sessions

TICK = 0.00005                              # $6.25
COST_PRIMARY_USD = 4.36 + 2 * 6.25          # 1 tick/side spread + commission = $16.86 RT
COST_STRESS_USD = 4.36 + 4 * 6.25           # 2 ticks/side + commission = $29.36 RT
CP = COST_PRIMARY_USD / POINT_VALUE         # 0.00013488 pt
CS = COST_STRESS_USD / POINT_VALUE          # 0.00023488 pt

# the 4 data-hole dates recorded by G00084 (its REPORT.md, SESSION_MISSING_DATA_HOLE)
G84_HOLES = [pd.Timestamp(d) for d in ("2014-01-29", "2015-12-16", "2018-12-19", "2024-12-18")]

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


log("=" * 112)
log("G3_FXOVERSHOOT_20260906  delayed FX overshooting after FOMC (6E, ZN-implied direction)  |  ledger G00089")
log("seed=%d  shifts=%d  boot=%d  |  evidence status of EVERY number in this file: %s" % (SEED, N_SHIFTS, N_BOOT, EVSTAT))
log("=" * 112)

# ---------------------------------------------------------------- inputs + seal
E6_PQ = REPO / "runs/DAILY_6E_EXTRACT_AUTOPSY_20260906/out/6e_daily.parquet"
E6_META = REPO / "runs/DAILY_6E_EXTRACT_AUTOPSY_20260906/out/extract_meta.json"
ZN_PQ = REPO / "runs/G3_AUCTCYCLE_20260906/out/zn_daily.parquet"
ZN_MANIFEST = REPO / "runs/G3_AUCTCYCLE_20260906/out/inputs_manifest.json"
CAL_CSV = REPO / "runs/GENESIS_H2_CALENDAR_20260828/out/calendar_artifacts/fomc_meetings_2006_2026.csv"

log("\n-- INPUT CERTIFICATION (reused AS-IS; shas printed; seal asserted) --")
e6_sha = sha256(E6_PQ)
meta = json.loads(E6_META.read_text())
log(f"  6e_daily.parquet sha256 {e6_sha}")
log(f"    extract_meta recorded  {meta['sha256_6e_daily_parquet']}  match={e6_sha == meta['sha256_6e_daily_parquet']}")
assert e6_sha == meta["sha256_6e_daily_parquet"], "6E parquet does not match its recorded extract sha"
assert meta["point_value"] == POINT_VALUE
zn_sha = sha256(ZN_PQ)
man = json.loads(ZN_MANIFEST.read_text())
log(f"  zn_daily.parquet sha256 {zn_sha}")
log(f"    manifest ZN sha        {man['ZN']['parquet_sha256']}  match={zn_sha == man['ZN']['parquet_sha256']}")
assert zn_sha == man["ZN"]["parquet_sha256"], "ZN parquet does not match certified manifest"
log(f"  fomc_meetings_2006_2026.csv sha256 {sha256(CAL_CSV)}")

e6 = pd.read_parquet(E6_PQ)
zn = pd.read_parquet(ZN_PQ)
for nm, df in (("6E", e6), ("ZN", zn)):
    assert df["date"].max() < SEAL, f"SEAL BREACH: {nm} max {df['date'].max()}"
assert zn["ret_points"].isna().sum() == 0
n_nan6 = int(e6["ret_points"].isna().sum())
log(f"  6E NaN ret_points sessions: {n_nan6} (structural roll gaps, named in extract_meta; certified s7")
log(f"    reproduction is over the {len(e6) - n_nan6} defined rows). Handling per the recorded amendment:")
log(f"    NaN = NOT COMPUTABLE -> window-containing events excluded (WINDOW_ROLL_GAP), never zero-filled;")
log(f"    same rule inside the null and the control pool; drift60 = nanmean (>= 50 of 60 required).")
assert n_nan6 == 46
log(f"  seal assert: 6E max {e6['date'].max().date()}, ZN max {zn['date'].max().date()}  (< 2026-08-01)  PASS")
log(f"  6E rows {len(e6)} span {e6['date'].min().date()}..{e6['date'].max().date()}; "
    f"ZN rows {len(zn)} span {zn['date'].min().date()}..{zn['date'].max().date()}")
log("  certification carried: 6E point-return reproduction vs certified s7 max err 0.0 (extract_meta);")
log("  ZN causal roll unit tests ALL PASS, identity gate max err 0.0 (G3_AUCTCYCLE manifest)")

# ---------------------------------------------------------------- FOMC calendar
cal_full = pd.read_csv(CAL_CSV, parse_dates=["start_date", "decision_date"])
win = cal_full[(cal_full["decision_date"] >= "2009-01-01")
               & (cal_full["decision_date"] <= "2026-07-31")].reset_index(drop=True)
assert len(win) == 140, f"expected the G00084 window realization of exactly 140, got {len(win)}"
for d in G84_HOLES:
    assert (win["decision_date"] == d).any(), f"hole date {d.date()} not in the 140-event window"
ev = win[~win["decision_date"].isin(G84_HOLES)].reset_index(drop=True)
n_cal = len(ev)
log("\n-- FOMC CALENDAR (the G00084 calendar, minus its 4 recorded data-hole dates) --")
log(f"  window 2009-01-01..2026-07-31: 140 events; minus holes "
    f"{[str(d.date()) for d in G84_HOLES]} -> {n_cal} calendar events")
assert n_cal == 136
assert 130 <= n_cal <= 140, "spec band ~130 violated"

# ---------------------------------------------------------------- event realization
e6_dates = pd.DatetimeIndex(e6["date"])
ret6 = e6["ret_points"].to_numpy()
M6 = len(e6)
pos6 = {d: i for i, d in enumerate(e6_dates)}
zn_dates = pd.DatetimeIndex(zn["date"])
retn = zn["ret_points"].to_numpy()
posn = {d: i for i, d in enumerate(zn_dates)}
znret_by_date = dict(zip(zn_dates, retn))
fomc_all_in_6e = {pos6[d] for d in cal_full["decision_date"] if d in pos6}

excluded, traded = [], []
for d in ev["decision_date"]:
    if d not in posn:
        excluded.append((d, "ZN_BEFORE_SERIES" if d < zn_dates[0] else "SIGNAL_SESSION_MISSING"))
        continue
    if posn[d] < 1:
        excluded.append((d, "NO_SIGNAL_HISTORY"))
        continue
    if d not in pos6:
        excluded.append((d, "6E_BEFORE_SERIES" if d < e6_dates[0] else "6E_SESSION_MISSING"))
        continue
    q = pos6[d]
    if q + HOLD > M6 - 1:
        excluded.append((d, "WINDOW_BEYOND_SEAL"))
        continue
    if np.isnan(ret6[q + 1:q + HOLD + 1]).any():
        excluded.append((d, "WINDOW_ROLL_GAP"))
        continue
    if retn[posn[d]] == 0.0:
        excluded.append((d, "ZERO_SIGNAL_NO_TRADE"))
        continue
    traded.append(q)
tr_pos = np.array(sorted(traded))
N = len(tr_pos)
gaps = np.diff(tr_pos)
log("\n-- EVENT REALIZATION (signal on ZN, position on 6E) --")
log(f"  excluded ({len(excluded)}):")
for d, r in excluded:
    log(f"    {d.date()}  {r}")
log(f"  realized traded events N = {N}  (calendar {n_cal} -> -{len(excluded)} excluded)")
assert gaps.min() > HOLD, "event 10-day windows overlap -- design assumption violated"
log(f"  min gap between consecutive events = {gaps.min()} 6E sessions (> {HOLD}: windows never overlap)  PASS")

zn_sig = np.array([znret_by_date[e6_dates[q]] for q in tr_pos])
side = np.sign(zn_sig)                       # ZN up = dovish -> LONG 6E (prereg sign)
cum10 = np.array([ret6[q + 1:q + HOLD + 1].sum() for q in tr_pos])
gross = side * cum10
x_primary = gross - CP
x_stress = gross - CS
wd = np.array([e6_dates[q].dayofweek for q in tr_pos])
wd_names = ["Mon", "Tue", "Wed", "Thu", "Fri"]

# ---------------------------------------------------- G1: null FIRST, MDE printed
rng = np.random.default_rng(SEED)
offsets = rng.choice(M6 - 1, size=N_SHIFTS, replace=False) + 1


def stat_at(k):
    q = (tr_pos + k) % M6
    x = []
    for qq in q:
        d = e6_dates[qq]
        s = znret_by_date.get(d)
        if s is None or s == 0.0:            # frozen rule re-applied at shifted positions
            continue
        win = ret6[(qq + np.arange(1, HOLD + 1)) % M6]
        if np.isnan(win).any():              # WINDOW_ROLL_GAP re-applied
            continue
        x.append(np.sign(s) * win.sum() - CP)
    return float(np.mean(x)), len(x)


null_res = [stat_at(k) for k in offsets]
null_T = np.array([t for t, _ in null_res])
null_n = np.array([n for _, n in null_res])
null_sd = null_T.std(ddof=1)
mde80 = (Z_ALPHA + Z_POWER) * null_sd

log("\n-- G1: MDE (printed BEFORE the observed statistic; null computed first; offset 0 never evaluated) --")
log("  SEMANTIC (what the p-value is over): the population is the %d scheduled FOMC decision days 2009-04..2026-06" % N)
log("  (G00084 calendar minus its 4 hole dates) that trade on the certified 6E calendar with a nonzero ZN D-1->D0")
log("  move and a complete D+10 window; the event is 'mean after-cost points of holding 6E %d sessions in the" % HOLD)
log("  ZN-implied (dovish=long-EUR) direction'; the p is the two-sided probability, under %d shared circular" % N_SHIFTS)
log("  shifts of the whole event family along the %d-session 6E calendar (dependence preserved, incl. the" % M6)
log("  contemporaneous ZN<->6E linkage: the shifted signal is ZN's ret on the SHIFTED date; rule incl. missing/")
log("  zero-signal drop re-applied), of |T| >= |T_obs|.")
log(f"  null sd = {null_sd:.6f} pt   MDE80 (two-sided alpha .05, 80% power) = {mde80:.6f} pt  "
    f"(${mde80 * POINT_VALUE:,.0f}/ct at $125,000/pt)")
log(f"  null draws: {N_SHIFTS}; base family size {N}; shifted-family survivors per draw: "
    f"min {null_n.min()}, mean {null_n.mean():.1f}, max {null_n.max()}")
gate("G1_MDE_first", "printed (~130 events)",
     f"N={N} traded of {n_cal} calendar; MDE80={mde80:.6f} pt (${mde80 * POINT_VALUE:,.0f}/ct); printed first (procedural)",
     "PASS")

# ---------------------------------------------------- observed + G2
T_obs = x_primary.mean()
p_two = (1 + int(np.sum(np.abs(null_T) >= abs(T_obs)))) / (N_SHIFTS + 1)
boot = rng.choice(x_primary, size=(N_BOOT, N), replace=True).mean(axis=1)
ci_lo, ci_hi = np.percentile(boot, [2.5, 97.5])
tcrit = sps.t.ppf(0.975, N - 1)
se = x_primary.std(ddof=1) / math.sqrt(N)
tci = (T_obs - tcrit * se, T_obs + tcrit * se)
hit = float((x_primary > 0).mean())
n_long = int((side > 0).sum())

log("\n-- G2: PRIMARY after-cost edge (D0 close -> D+10 close) --")
log(f"  sides: LONG 6E (dovish) {n_long}, SHORT 6E (hawkish) {N - n_long}")
log(f"  gross mean          = {gross.mean():+.6f} pt  (${gross.mean() * POINT_VALUE:+,.0f}/ct)")
log(f"  after-cost mean     = {T_obs:+.6f} pt  (${T_obs * POINT_VALUE:+,.0f}/ct)   "
    f"[PRIMARY cost {CP:.6f} pt = $16.86 RT, BASIS COMMISSION+SPREAD MODELED]")
log(f"  event-block bootstrap CI95 = [{ci_lo:+.6f}, {ci_hi:+.6f}] pt   (10,000 draws, events are non-overlapping blocks)")
log(f"  [descriptive second computation, NOT the gate: t-CI95 = [{tci[0]:+.6f}, {tci[1]:+.6f}]; t = {T_obs / se:+.2f}]")
log(f"  shift-null two-sided p = {p_two:.4f}  (add-one, {N_SHIFTS} shifts)")
log(f"  hit rate = {hit:.3f}   per-event sd = {x_primary.std(ddof=1):.6f} pt")
g2 = (T_obs > 0) and (ci_lo > 0) and (p_two < 0.05)
gate("G2_edge", "after-cost mean > 0 AND event-block CI95 excludes 0 AND shift-null p < 0.05",
     f"mean {T_obs:+.6f} pt, CI [{ci_lo:+.6f},{ci_hi:+.6f}], p {p_two:.4f}", "PASS" if g2 else "FAIL")
underpowered = (not g2) and (mde80 > 3 * abs(T_obs))
log(f"  power language: MDE80={mde80:.6f} vs 3x|obs|={3 * abs(T_obs):.6f} -> "
    + ("UNDERPOWERED_STILL" if underpowered else ("n/a (G2 PASS)" if g2 else "FAIL is powered (MDE <= 3x|obs|)")))

# ---------------------------------------------------- G3 clause (a): weekday-matched control
pool, psig_l = [], []
for q in range(0, M6 - HOLD):
    d = e6_dates[q]
    if q in fomc_all_in_6e:
        continue
    s = znret_by_date.get(d)
    if s is None or s == 0.0:
        continue
    if d not in posn or posn[d] < 1:
        continue
    if np.isnan(ret6[q + 1:q + HOLD + 1]).any():   # WINDOW_ROLL_GAP re-applied
        continue
    pool.append(q)
    psig_l.append(s)
pool = np.array(pool)
psig = np.sign(np.array(psig_l))
pcum = np.array([ret6[q + 1:q + HOLD + 1].sum() for q in pool])
px = psig * pcum - CP
pwd = np.array([e6_dates[q].dayofweek for q in pool])
ctrl_wd = {w: px[pwd == w].mean() for w in range(5)}
diff = x_primary - np.array([ctrl_wd[w] for w in wd])
ctrl_matched_mean = T_obs - diff.mean()
g3a = diff.mean() > 0

log("\n-- G3 clause (a): matched non-FOMC same-weekday control (same ZN-sign rule, same 10-day window, same cost) --")
log(f"  control pool: {len(pool)} non-FOMC 6E sessions (every calendar decision day excluded; ZN signal available");
log(f"    and nonzero); by weekday: " + ", ".join(f"{wd_names[w]} {int((pwd == w).sum())}" for w in range(5)))
log(f"  event weekday mix: " + ", ".join(f"{wd_names[w]} {int((wd == w).sum())}" for w in range(5) if (wd == w).any()))
log(f"  ctrl mean by weekday (after-cost pt): " + ", ".join(f"{wd_names[w]} {ctrl_wd[w]:+.6f}" for w in range(5)))
log(f"  FOMC after-cost mean {T_obs:+.6f} vs weekday-matched control {ctrl_matched_mean:+.6f}  ->  diff {diff.mean():+.6f} pt")
log(f"  clause (a): {'PASS' if g3a else 'FAIL'} (mean diff > 0 required)")

# ---------------------------------------------------- G3 clause (b): drift-residualization
drift60 = np.full(N, np.nan)
drift_cnt = np.zeros(N, dtype=int)
for i, q in enumerate(tr_pos):
    if q >= 60:
        w = ret6[q - 60:q]
        drift_cnt[i] = int((~np.isnan(w)).sum())
        if drift_cnt[i] >= 50:
            drift60[i] = np.nanmean(w)
has_hist = ~np.isnan(drift60)
resid = side[has_hist] * (cum10[has_hist] - HOLD * drift60[has_hist]) - CP
g3b = resid.mean() > 0
log("\n-- G3 clause (b): drift-residualization (subtract 6E trailing-60d unconditional drift over the window) --")
log(f"  drift60_i = mean(6E ret_points over the 60 sessions strictly before D0); resid_i = side_i*(cum10_i - 10*drift60_i) - cost")
log(f"  drift window = nanmean over trailing 60 (roll-gap NaNs skipped, >= 50 defined required); defined counts: "
    f"min {drift_cnt[has_hist].min() if has_hist.any() else 0}, max {drift_cnt[has_hist].max() if has_hist.any() else 0}")
log(f"  n with usable history = {int(has_hist.sum())} of {N}; lacking (listed RESID_INSUFFICIENT_HISTORY, still in PRIMARY): "
    + (", ".join(str(e6_dates[q].date()) for q in tr_pos[~has_hist]) if (~has_hist).any() else "none"))
log(f"  residualized after-cost mean = {resid.mean():+.6f} pt  (${resid.mean() * POINT_VALUE:+,.0f}/ct)  "
    f"vs raw {T_obs:+.6f}")
log(f"  clause (b): {'PASS' if g3b else 'FAIL'} (residualized mean > 0 required)")
log("  LIMITATION (stated, never hidden): full rate-differential carry is NOT locally computable (no EUR-USD")
log("  short-rate differential series in the local store); trailing-60d drift is the reachable residualization.")
g3 = g3a and g3b
gate("G3_control", "beats matched non-FOMC same-weekday days AND survives drift-residualization",
     f"(a) diff {diff.mean():+.6f} pt {'PASS' if g3a else 'FAIL'}; "
     f"(b) resid mean {resid.mean():+.6f} pt {'PASS' if g3b else 'FAIL'}", "PASS" if g3 else "FAIL")

# ---------------------------------------------------- G4: Scholl-Uhlig era thirds
thirds = np.array_split(np.arange(N), 3)
third_rows = []
log("\n-- G4: Scholl-Uhlig subsample fragility (contiguous near-equal-count temporal thirds) --")
for t, idx in enumerate(thirds):
    d0, d1 = e6_dates[tr_pos[idx[0]]].date(), e6_dates[tr_pos[idx[-1]]].date()
    am, gm = x_primary[idx].mean(), gross[idx].mean()
    third_rows.append(dict(third=t + 1, span=f"{d0}..{d1}", n=len(idx),
                           gross_mean_pts=round(gm, 6), aftercost_mean_pts=round(am, 6),
                           aftercost_mean_usd=round(am * POINT_VALUE, 2),
                           sign="pos" if am > 0 else "neg",
                           hit=round(float((x_primary[idx] > 0).mean()), 3),
                           evidence_status=EVSTAT))
    log(f"  third {t + 1}: {d0}..{d1}  n={len(idx):3d}  gross {gm:+.6f}  after-cost {am:+.6f} pt "
        f"(${am * POINT_VALUE:+,.0f}/ct)  sign={'pos' if am > 0 else 'neg'}  "
        f"hit={float((x_primary[idx] > 0).mean()):.3f}")
pd.DataFrame(third_rows).to_csv(OUT / "era_thirds.csv", index=False)
n_pos_thirds = sum(1 for r in third_rows if r["aftercost_mean_pts"] > 0)
g4 = not (n_pos_thirds == 1)
g4_status = (f"{'PASS' if g4 else 'FAIL'} (positive thirds = {n_pos_thirds}; "
             + ("effect lives in ONE third" if not g4 else "not one-third-concentrated") + ")")
log(f"  G4 classification: {g4_status}")
gate("G4_subsample_fragility", "era thirds printed; effect living in ONE third = FAIL",
     f"signs {'/'.join(r['sign'] for r in third_rows)} -> {g4_status}", "PASS" if g4 else "FAIL")

# ---------------------------------------------------- G5: cost band
log("\n-- G5: cost band ({1,2} ticks/side + $4.36/ctrRT commission; BASIS COMMISSION+SPREAD MODELED, not all-in) --")
log(f"  6E tick 0.00005 pt = $6.25")
log(f"  PRIMARY rung (1 tick/side): $16.86 RT = {CP:.6f} pt  -> after-cost mean {T_obs:+.6f} pt")
log(f"  STRESS  rung (2 ticks/side): $29.36 RT = {CS:.6f} pt -> after-cost mean {x_stress.mean():+.6f} pt")
log(f"  cost is {CP / gross.std(ddof=1) * 100:.1f}% of the per-event gross sd ({gross.std(ddof=1):.6f} pt) -- trivial at {HOLD}d hold")
sign_flip = (T_obs > 0) != (x_stress.mean() > 0)
log(f"  stress rung flips the sign of the mean: {'YES' if sign_flip else 'NO'}")
gate("G5_cost", "6E tick $6.25, 10-day hold -- trivial; printed",
     f"primary {T_obs:+.6f}, stress {x_stress.mean():+.6f} pt; flip={'YES' if sign_flip else 'NO'}", "PASS")

# ---------------------------------------------------- SECONDARY: {D+5, D+20} + path
log("\n-- SECONDARY (reported, no gate): signal-aligned cumulative path, h = 1..20 sessions after D0 --")
log("   h | n   | gross mean pt | after-cost(1-tick/side) pt |")
sec = {}
for h in range(1, 21):
    cum = []
    for i, q in enumerate(tr_pos):
        if q + h > M6 - 1:
            continue
        w = ret6[q + 1:q + h + 1]
        if np.isnan(w).any():                # per-h WINDOW_ROLL_GAP drop, n printed
            continue
        cum.append(side[i] * w.sum())
    cum = np.array(cum)
    sec[h] = (len(cum), cum.mean(), cum.mean() - CP)
    tag = "  <- PRIMARY" if h == HOLD else ("  <- reported" if h in (5, 20) else "")
    log(f"  {h:2d} | {len(cum):3d} | {cum.mean():+.6f}     | {cum.mean() - CP:+.6f}{tag}")
log(f"  D+5  after-cost mean = {sec[5][2]:+.6f} pt (${sec[5][2] * POINT_VALUE:+,.0f}/ct, n={sec[5][0]})")
log(f"  D+20 after-cost mean = {sec[20][2]:+.6f} pt (${sec[20][2] * POINT_VALUE:+,.0f}/ct, n={sec[20][0]})")

# ---------------------------------------------------- event table
rows = []
for i, q in enumerate(tr_pos):
    r = dict(date=str(e6_dates[q].date()), weekday=wd_names[wd[i]],
             third=next(t + 1 for t, idx in enumerate(thirds) if i in idx),
             zn_signal_pts=round(float(zn_sig[i]), 6),
             side="LONG_6E" if side[i] > 0 else "SHORT_6E",
             gross_pts_10d=round(float(gross[i]), 6),
             aftercost_primary_pts=round(float(x_primary[i]), 6),
             aftercost_stress_pts=round(float(x_stress[i]), 6),
             net_primary_usd=round(float(x_primary[i]) * POINT_VALUE, 2),
             ctrl_mean_weekday_pts=round(float(ctrl_wd[wd[i]]), 6),
             diff_vs_ctrl_pts=round(float(diff[i]), 6),
             drift60_pts_per_day=(round(float(drift60[i]), 8) if not np.isnan(drift60[i]) else ""),
             resid_aftercost_pts=(round(float(side[i] * (cum10[i] - HOLD * drift60[i]) - CP), 6)
                                  if not np.isnan(drift60[i]) else ""),
             status="TRADED", evidence_status=EVSTAT)
    for h in range(1, 21):
        if q + h <= M6 - 1 and not np.isnan(ret6[q + 1:q + h + 1]).any():
            r[f"cum_gross_pts_h{h}"] = round(float(side[i] * ret6[q + 1:q + h + 1].sum()), 6)
        else:
            r[f"cum_gross_pts_h{h}"] = ""
    rows.append(r)
for d, reason in excluded:
    rows.append(dict(date=str(d.date()), weekday=wd_names[d.dayofweek], third="", zn_signal_pts="",
                     side="", gross_pts_10d="", aftercost_primary_pts="", aftercost_stress_pts="",
                     net_primary_usd="", ctrl_mean_weekday_pts="", diff_vs_ctrl_pts="",
                     drift60_pts_per_day="", resid_aftercost_pts="",
                     status="EXCLUDED_" + reason, evidence_status=EVSTAT))
ev_df = pd.DataFrame(rows).sort_values("date")
ev_df.to_csv(OUT / "event_table.csv", index=False)

# ---------------------------------------------------- gate table + verdict
log("\n" + "=" * 112)
log("GATE TABLE (program-printed)")
log("=" * 112)
w1 = max(len(g[0]) for g in gate_rows)
log(f"{'GATE':<{w1}} | {'PASS-FAIL':<9} | SPEC | OBSERVED")
log("-" * 112)
for name, sp, ob, pf in gate_rows:
    log(f"{name:<{w1}} | {pf:<9} | {sp} | {ob}")
log("-" * 112)
if g2 and g3 and g4:
    verdict = "FXOVERSHOOT01 CANDIDATE (first 6E object)"
else:
    why = []
    if not g2:
        why.append("G2 FAIL" + (" UNDERPOWERED_STILL" if underpowered else " (powered)"))
    if not g3:
        why.append("G3 FAIL (" + ("a" if not g3a else "") + ("b" if not g3b else "") + ")")
    if not g4:
        why.append("G4 FAIL (one-third-concentrated)")
    verdict = "CLOSED AT SCOPE (S28): " + "; ".join(why)
log(f"VERDICT: {verdict}")
log(f"Every number above: evidence status {EVSTAT}.")

(OUT / "gate_table.txt").write_text("\n".join(_log) + "\n", encoding="utf-8")
print(f"\nwrote {OUT / 'gate_table.txt'}, event_table.csv ({len(ev_df)} rows), era_thirds.csv")
