# MC-55: post-FOMC uncertainty-resolution vol crush -- CORE RV-contraction leg.
# Preregistered: runs/G2_F12_MC55_FOMCCRUSH_20260906/spec.yaml (committed before results).
# Ledger trial G00053.
#
# ---------------------------------------------------------------------------
# PREREGISTERED DESIGN CONSTANTS (recorded BEFORE any RV is computed)
# ---------------------------------------------------------------------------
# Release-time anchors (per actual public Fed release practice, verified against
# federalreserve.gov/monetarypolicy pages on 2026-09-06 before computing):
#   * 14:15 ET -- all scheduled decisions 2006-01-31 .. 2013-01-30, EXCEPT the
#                 eight 2011-2012 press-conference meetings.
#   * 12:30 ET -- the eight 2011-2012 press-conference meetings (statement at
#                 12:30 ET, presser at 14:15 ET): 2011-04-27, 2011-06-22,
#                 2011-11-02, 2012-01-25, 2012-04-25, 2012-06-20, 2012-09-13,
#                 2012-12-12.
#   * 14:00 ET -- all scheduled decisions from 2013-03-20 onward.
# Windows move RIGIDLY with the anchor T: pre = [T-120m, T-30m], post = [T+5m,
# T+90m]. At T=14:00 this reproduces the spec's literal windows 12:00-13:30 /
# 14:05-15:30 exactly.
# Bars are END-stamped (CLAUDE.md #6): the window [a,b] uses closes of bars
# stamped a..b inclusive; returns are consecutive log-close diffs (n_bars-1
# returns spanning exactly the window; the release-minute spike 14:00-14:05
# is excluded because the first post return starts at the T+5 close anchor).
# Completeness (pre-stated): a session is eligible only if, at ALL THREE
# anchors, each window has >= 90% of expected bars (pre: >=82 of 91, post:
# >=78 of 86) and RV > 0 in both windows. Symmetric across treatment/control;
# needed so the circular-shift null (labels carry their anchor) is defined on
# every eligible session.
# Population: scheduled FOMC decision sessions falling on Tue/Wed (the spec's
# control and null designs are Tue/Wed-only). Scheduled decisions on other
# weekdays are EXCLUDED AND LISTED (7 Thursdays; pre-stated here, before
# results). Unscheduled/intermeeting action dates are EXCLUDED from BOTH the
# treatment set and the control pool, and listed.
# Statistic: T = mean over FOMC sessions i of [ ratio(i, a_i) - mean of
# ratio(c, a_i) over non-FOMC sessions c in the same (era-bucket, weekday)
# cell ], i.e. mean(ratio|FOMC) - matched-control mean (weekday x era).
# Null: circular shift of the WHOLE label family (one shared offset per
# shift -- dependence preserved) along the chronological calendar of eligible
# Tue/Wed sessions; labels carry their anchors; 401 offsets drawn once,
# without replacement, seed 20260906; two-sided p with add-one correction.
# MDE at 80% power (two-sided alpha=.05, normal approx on the null sd) is
# computed from the null distribution and printed BEFORE the observed value.
# PLAUSIBLE EFFECT (pre-stated for the N-BOUND declaration): |delta| = 0.30
# log-units (event-vol literature puts post-event RV shifts at ~1.3-2x in
# variance terms, log 0.26-0.69; 0.30 is the conservative low end).
# N-BOUND iff MDE > 3 x 0.30 = 0.90.
# Pre-stated direction: contraction => T_obs NEGATIVE (FOMC ratio lower).
# ---------------------------------------------------------------------------

import math
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

RUN = Path(__file__).resolve().parents[1]
REPO = RUN.parents[1]
SPEC = RUN / "spec.yaml"
assert SPEC.exists(), "prereg violation: spec.yaml missing"

SEED = 20260906
N_SHIFTS = 401
DEV_END = pd.Timestamp("2026-05-29")
PLAUSIBLE_EFFECT = 0.30
Z_ALPHA, Z_POWER = 1.959964, 0.841621  # two-sided 5%, 80% power

OUT = RUN / "out"
OUT.mkdir(exist_ok=True)
_log_lines = []


def log(s=""):
    print(s)
    _log_lines.append(s)


# ---------------------------------------------------------------------------
# FOMC scheduled-decision calendar 2006 -> 2026-05 (decision day = last meeting
# day). Verified 2026-09-06 against federalreserve.gov fomchistorical<year>.htm
# (2006-2020) and fomccalendars.htm (2021-2026). P = 12:30 presser release.
# ---------------------------------------------------------------------------
_CAL = {
    2006: ["01-31", "03-28", "05-10", "06-29", "08-08", "09-20", "10-25", "12-12"],
    2007: ["01-31", "03-21", "05-09", "06-28", "08-07", "09-18", "10-31", "12-11"],
    2008: ["01-30", "03-18", "04-30", "06-25", "08-05", "09-16", "10-29", "12-16"],
    2009: ["01-28", "03-18", "04-29", "06-24", "08-12", "09-23", "11-04", "12-16"],
    2010: ["01-27", "03-16", "04-28", "06-23", "08-10", "09-21", "11-03", "12-14"],
    2011: ["01-26", "03-15", "04-27P", "06-22P", "08-09", "09-21", "11-02P", "12-13"],
    2012: ["01-25P", "03-13", "04-25P", "06-20P", "08-01", "09-13P", "10-24", "12-12P"],
    2013: ["01-30", "03-20", "05-01", "06-19", "07-31", "09-18", "10-30", "12-18"],
    2014: ["01-29", "03-19", "04-30", "06-18", "07-30", "09-17", "10-29", "12-17"],
    2015: ["01-28", "03-18", "04-29", "06-17", "07-29", "09-17", "10-28", "12-16"],
    2016: ["01-27", "03-16", "04-27", "06-15", "07-27", "09-21", "11-02", "12-14"],
    2017: ["02-01", "03-15", "05-03", "06-14", "07-26", "09-20", "11-01", "12-13"],
    2018: ["01-31", "03-21", "05-02", "06-13", "08-01", "09-26", "11-08", "12-19"],
    2019: ["01-30", "03-20", "05-01", "06-19", "07-31", "09-18", "10-30", "12-11"],
    2020: ["01-29", "04-29", "06-10", "07-29", "09-16", "11-05", "12-16"],  # 03-17/18 CANCELLED
    2021: ["01-27", "03-17", "04-28", "06-16", "07-28", "09-22", "11-03", "12-15"],
    2022: ["01-26", "03-16", "05-04", "06-15", "07-27", "09-21", "11-02", "12-14"],
    2023: ["02-01", "03-22", "05-03", "06-14", "07-26", "09-20", "11-01", "12-13"],
    2024: ["01-31", "03-20", "05-01", "06-12", "07-31", "09-18", "11-07", "12-18"],
    2025: ["01-29", "03-19", "05-07", "06-18", "07-30", "09-17", "10-29", "12-10"],
    2026: ["01-28", "03-18", "04-29"],  # through 2026-05
}

ANCHOR_1400_START = pd.Timestamp("2013-03-20")  # first 14:00 ET release

fomc_rows = []
for yr, days in _CAL.items():
    for dstr in days:
        presser1230 = dstr.endswith("P")
        d = pd.Timestamp(f"{yr}-{dstr.rstrip('P')}")
        if presser1230:
            anchor = "12:30"
        elif d >= ANCHOR_1400_START:
            anchor = "14:00"
        else:
            anchor = "14:15"
        fomc_rows.append((d, anchor))
fomc_cal = pd.DataFrame(fomc_rows, columns=["date", "anchor"]).sort_values("date").reset_index(drop=True)
fomc_cal["weekday"] = fomc_cal["date"].dt.day_name()

# Unscheduled / intermeeting FOMC actions (public release dates), 2006 -> 2026-05.
# Excluded from treatment AND from the control pool; listed per spec G0.
INTERMEETING = [
    ("2007-08-10", "Fri", "liquidity statement (unscheduled)"),
    ("2007-08-17", "Fri", "intermeeting discount-rate cut statement (call 08-16)"),
    ("2008-01-22", "Tue", "intermeeting -75bp cut, released ~08:20 ET (call 01-21)"),
    ("2008-03-11", "Tue", "TSLF statement, released ~08:30 ET (call 03-10)"),
    ("2008-10-08", "Wed", "coordinated intermeeting -50bp cut, released ~07:00 ET (call 10-07)"),
    ("2010-05-09", "Sun", "swap-line reopening statement (unscheduled)"),
    ("2019-10-11", "Fri", "bill-purchase statement (call 10-04)"),
    ("2020-03-03", "Tue", "intermeeting -50bp cut, released 10:00 ET"),
    ("2020-03-15", "Sun", "intermeeting -100bp cut, released 17:00 ET"),
    ("2020-03-19", "Thu", "notation vote: swap lines"),
    ("2020-03-23", "Mon", "unscheduled statement: open-ended QE, released ~08:00 ET"),
    ("2020-03-31", "Tue", "notation vote: FIMA repo facility"),
    ("2020-08-27", "Thu", "framework statement via notation vote (Jackson Hole)"),
    ("2025-08-22", "Fri", "notation vote (per fomccalendars.htm)"),
]
intermeeting_dates = {pd.Timestamp(d) for d, _, _ in INTERMEETING}

# ---------------------------------------------------------------------------
# Load NQ 1m substrate; G0 seal
# ---------------------------------------------------------------------------
nq = pd.read_parquet(REPO / "research/scalping_lab/substrate/minute/NQ/nq1m_2005_202605.parquet")
nq["time"] = pd.to_datetime(nq["time"])
nq_max = nq["time"].max()
assert nq_max <= DEV_END + pd.Timedelta(hours=23, minutes=59), f"SEAL BREACH: NQ max ts {nq_max}"
nq["date"] = nq["time"].dt.normalize()
nq["ck"] = nq["time"].dt.hour * 60 + nq["time"].dt.minute

ANCHORS = ["14:00", "14:15", "12:30"]  # column order of matrices
A_IDX = {a: i for i, a in enumerate(ANCHORS)}


def hhmm(m):
    return f"{m // 60:02d}:{m % 60:02d}"


def windows_for(anchor):
    t = int(anchor[:2]) * 60 + int(anchor[3:])
    return (t - 120, t - 30), (t + 5, t + 90)


def win_stats(lo, hi):
    m = nq[(nq["ck"] >= lo) & (nq["ck"] <= hi)].sort_values("time")
    lr = np.log(m["close"]).groupby(m["date"]).diff()
    rv = (lr ** 2).groupby(m["date"]).sum()
    n = m.groupby("date").size()
    return pd.DataFrame({"n": n, "rv": rv})


sess = pd.DataFrame(index=sorted(nq["date"].unique()))
for a in ANCHORS:
    (plo, phi), (qlo, qhi) = windows_for(a)
    pre = win_stats(plo, phi)
    post = win_stats(qlo, qhi)
    k = a.replace(":", "")
    sess[f"npre_{k}"] = pre["n"]
    sess[f"rvpre_{k}"] = pre["rv"]
    sess[f"npost_{k}"] = post["n"]
    sess[f"rvpost_{k}"] = post["rv"]
sess = sess.fillna(0.0)
sess["weekday"] = pd.DatetimeIndex(sess.index).dayofweek  # Mon=0

MIN_PRE, MIN_POST = 82, 78  # >= 90% of 91 / 86 expected bars
ok = pd.Series(True, index=sess.index)
for a in ANCHORS:
    k = a.replace(":", "")
    ok &= (sess[f"npre_{k}"] >= MIN_PRE) & (sess[f"npost_{k}"] >= MIN_POST)
    ok &= (sess[f"rvpre_{k}"] > 0) & (sess[f"rvpost_{k}"] > 0)

elig = sess[ok & sess["weekday"].isin([1, 2]) & ~sess.index.isin(intermeeting_dates)].copy()
elig = elig.sort_index()
M = len(elig)
edates = pd.DatetimeIndex(elig.index)


def era_of_year(y):
    return 0 if y <= 2012 else (1 if y <= 2019 else 2)


ERA_NAMES = ["2006-2012", "2013-2019", "2020-2026.05"]
era_arr = np.array([era_of_year(d.year) for d in edates])
wed_arr = (elig["weekday"].to_numpy() == 2).astype(int)
cell_arr = era_arr * 2 + wed_arr  # 6 cells: era x {Tue,Wed}

ratio_mat = np.column_stack([
    np.log(elig[f"rvpost_{a.replace(':', '')}"].to_numpy() / elig[f"rvpre_{a.replace(':', '')}"].to_numpy())
    for a in ANCHORS
])

# ---------------------------------------------------------------------------
# Assemble the FOMC label set
# ---------------------------------------------------------------------------
pos_of_date = {d: i for i, d in enumerate(edates)}
thursday_excl, data_excl, labels = [], [], []
for _, r in fomc_cal.iterrows():
    d, a = r["date"], r["anchor"]
    if r["weekday"] not in ("Tuesday", "Wednesday"):
        thursday_excl.append((d, r["weekday"], a))
    elif d in pos_of_date:
        labels.append((pos_of_date[d], A_IDX[a]))
    else:
        data_excl.append((d, r["weekday"], a))

lab_pos = np.array([p for p, _ in labels])
lab_anc = np.array([q for _, q in labels])
N_F = len(lab_pos)

cellcount = np.bincount(cell_arr, minlength=6).astype(float)
cellsum = np.zeros((6, 3))
for c in range(6):
    cellsum[c, :] = ratio_mat[cell_arr == c, :].sum(axis=0)


def diffs_for(pos, anc):
    """Per-label matched difference: ratio(label) - mean ratio of non-label
    sessions in the label's (era, weekday) cell, at the label's anchor."""
    cells_l = cell_arr[pos]
    ctrl_mean = np.zeros((6, 3))
    for c in range(6):
        in_c = pos[cells_l == c]
        denom = cellcount[c] - len(in_c)
        ctrl_mean[c, :] = (cellsum[c, :] - ratio_mat[in_c, :].sum(axis=0)) / denom
    return ratio_mat[pos, anc] - ctrl_mean[cells_l, anc]


def stat_for(pos, anc):
    return diffs_for(pos, anc).mean()


# ---------------------------------------------------------------------------
# Gate table machinery
# ---------------------------------------------------------------------------
gate_rows = []


def gate(name, spec_txt, obs_txt, ok_txt):
    gate_rows.append((name, spec_txt, obs_txt, ok_txt))


log("=" * 100)
log("MC-55  post-FOMC RV-contraction test  |  run G2_F12_MC55_FOMCCRUSH_20260906  |  ledger trial G00053")
log("seed=20260906  shifts=401  dev_end=2026-05-29")
log("=" * 100)

log("\n-- PREREGISTERED ANCHOR RECORD (fixed before any RV computation; see src header) --")
for a in ANCHORS:
    (plo, phi), (qlo, qhi) = windows_for(a)
    log(f"  anchor {a} ET -> pre [{hhmm(plo)}-{hhmm(phi)}], post [{hhmm(qlo)}-{hhmm(qhi)}]  "
        + {"14:00": "(2013-03-20 ..)", "14:15": "(2006 .. 2013-01-30 non-presser)",
           "12:30": "(eight 2011-2012 press-conference releases)"}[a])
log(f"  windows are rigid translates of the spec's 14:00-era windows; ratio = log(RV_post/RV_pre)")

# ---- G0 ----
per_yr = fomc_cal["date"].dt.year.value_counts().sort_index()
log("\n-- G0: seal & calendar --")
log(f"  NQ substrate max timestamp: {nq_max}  (assert <= 2026-05-29 23:59: PASS)")
log(f"  scheduled decisions on calendar 2006->2026-05: {len(fomc_cal)}  "
    f"({len(_CAL)} years; per-year counts: {dict(per_yr)})")
log(f"  cross-check vs ~8/yr expectation: {len(fomc_cal)} decisions / {len(_CAL)} calendar years "
    f"= {len(fomc_cal) / len(_CAL):.2f}/yr (2020 has 7: the 2020-03-17/18 meeting was CANCELLED; 2026 partial year)")
log(f"  EXCLUDED unscheduled/intermeeting actions ({len(INTERMEETING)}), by public release date:")
for d, wd, why in INTERMEETING:
    log(f"    {d} ({wd}): {why}")
log(f"  EXCLUDED scheduled decisions NOT on Tue/Wed ({len(thursday_excl)}) [Tue/Wed control+null design]:")
for d, wd, a in thursday_excl:
    log(f"    {d.date()} ({wd}, anchor {a})")
log(f"  EXCLUDED scheduled Tue/Wed decisions failing data-completeness ({len(data_excl)}):")
for d, wd, a in data_excl:
    log(f"    {d.date()} ({wd}, anchor {a})")
log(f"  realized FOMC N = {N_F} (vs ~160 expected); eligible Tue/Wed session calendar M = {M}")
seal_pass = nq_max <= DEV_END + pd.Timedelta(hours=23, minutes=59)
gate("G0_seal", "max date <= 2026-05-29; print N + excluded lists",
     f"max_ts={nq_max}; N={N_F}; {len(INTERMEETING)} intermeeting + {len(thursday_excl)} non-Tue/Wed "
     f"+ {len(data_excl)} data-incomplete excluded (listed above)", "PASS" if seal_pass else "FAIL")

# ---- G1 ----
sem = (f"Population: the {N_F} scheduled FOMC decision sessions falling on Tue/Wed, 2006-01-31 .. 2026-04-29, "
       f"vs the {M - N_F} other eligible Tue/Wed RTH sessions 2006->2026-05-29, matched by weekday and era "
       f"({'/'.join(ERA_NAMES)}). Event: the difference in mean per-session log(RV in the 85-min post-release "
       f"window / RV in the 90-min pre-release window), windows anchored at each era's actual release time; "
       f"the p-value is the two-sided probability, under 401 whole-family circular shifts of the FOMC label "
       f"along the eligible-session calendar, of a |difference| at least as large as observed.")
log("\n-- G1: semantic statement --")
log("  " + sem)
gate("G1_semantic", "one printed sentence: population + event", "printed above", "PASS")

# ---- Null distribution FIRST (so the MDE is printed before the observed value) ----
rng = np.random.default_rng(SEED)
offsets = rng.choice(M - 1, size=N_SHIFTS, replace=False) + 1  # drawn once, no 0 offset
null_T = np.empty(N_SHIFTS)
for j, k in enumerate(offsets):
    null_T[j] = stat_for((lab_pos + k) % M, lab_anc)
null_sd = null_T.std(ddof=1)
mde80 = (Z_ALPHA + Z_POWER) * null_sd

log("\n-- G2: MDE (printed BEFORE the observed statistic; null computed first, offset 0 never evaluated) --")
log(f"  null: one shared circular offset per shift across the whole {N_F}-label family (dependence preserved),")
log(f"        401 offsets drawn once without replacement, seed {SEED}; labels carry their anchors.")
log(f"  null sd = {null_sd:.4f} log-units")
log(f"  MDE at 80% power (two-sided alpha=0.05, normal approx) = {mde80:.4f} log-units")
log(f"  pre-stated plausible effect = {PLAUSIBLE_EFFECT:.2f} log-units; 3x plausible = {3 * PLAUSIBLE_EFFECT:.2f}")
nbound = mde80 > 3 * PLAUSIBLE_EFFECT
log(f"  N-BOUND declaration: {'N-BOUND (MDE > 3x plausible)' if nbound else 'NOT N-BOUND (MDE <= 3x plausible effect)'}")
gate("G2_MDE_first", "MDE at 80% power printed before observed; N-BOUND declared if MDE > 3x plausible (0.90)",
     f"MDE80={mde80:.4f}; {'N-BOUND' if nbound else 'not N-BOUND'}", "PASS")

# ---- Observed statistic (computed only now) ----
obs_diffs = diffs_for(lab_pos, lab_anc)
T_obs = obs_diffs.mean()
p_two = (1 + np.sum(np.abs(null_T) >= abs(T_obs))) / (N_SHIFTS + 1)
fomc_mean = ratio_mat[lab_pos, lab_anc].mean()
ctrl_mean_matched = fomc_mean - T_obs

log("\n-- G3: primary statistic --")
log(f"  mean ratio | FOMC            = {fomc_mean:+.4f}")
log(f"  matched control mean         = {ctrl_mean_matched:+.4f}")
log(f"  OBSERVED difference T        = {T_obs:+.4f} log-units  (ratio of RVs: x{math.exp(T_obs):.3f})")
log(f"  two-sided p vs label-shift null = {p_two:.4f}   (event: |T_shift| >= |T_obs| under the 401 shifts)")
log(f"  preregistered direction: contraction => T < 0; observed sign: {'NEGATIVE (contraction)' if T_obs < 0 else 'POSITIVE (EXPANSION - opposite)'}")
# descriptive cross-check, different computation path (not a gate):
t_stat = T_obs / (obs_diffs.std(ddof=1) / math.sqrt(N_F))
p_t = math.erfc(abs(t_stat) / math.sqrt(2))
log(f"  [descriptive cross-check, NOT the gate: one-sample t on the {N_F} matched diffs: t={t_stat:+.2f}, "
    f"normal-approx two-sided p={p_t:.2e}]")
g3_pass = (p_two <= 0.05) and (T_obs < 0)
gate("G3_primary", "two-sided p <= 0.05 AND sign = contraction (negative)",
     f"T={T_obs:+.4f}, p={p_two:.4f}, sign={'neg' if T_obs < 0 else 'POS'}", "PASS" if g3_pass else "FAIL")

# ---- G4 era stability ----
log("\n-- G4: era stability --")
era_rows = []
for e, en in enumerate(ERA_NAMES):
    m_e = era_arr[lab_pos] == e
    d_e = obs_diffs[m_e]
    n_e = int(m_e.sum())
    f_e = ratio_mat[lab_pos[m_e], lab_anc[m_e]].mean() if n_e else np.nan
    T_e = d_e.mean() if n_e else np.nan
    nctrl = int(((era_arr == e)).sum()) - n_e
    era_rows.append(dict(era=en, n_fomc=n_e, n_ctrl_sessions=nctrl, mean_ratio_fomc=round(f_e, 4),
                         mean_ratio_ctrl_matched=round(f_e - T_e, 4), diff=round(T_e, 4),
                         sign="neg" if T_e < 0 else "pos"))
    log(f"  {en:12s}: N_FOMC={n_e:3d}  N_ctrl={nctrl:4d}  mean_ratio_FOMC={f_e:+.4f}  "
        f"matched_ctrl={f_e - T_e:+.4f}  diff={T_e:+.4f}  sign={'neg' if T_e < 0 else 'pos'}")
era_df = pd.DataFrame(era_rows)
era_df.to_csv(OUT / "era_table.csv", index=False)
obs_sign = "neg" if T_obs < 0 else "pos"
n_agree = int((era_df["sign"] == obs_sign).sum())
g4_pass = n_agree >= 2
log(f"  eras agreeing with pooled sign ({obs_sign}): {n_agree}/3")
gate("G4_era_stability", "sign agrees with pooled sign in >= 2 of 3 eras",
     f"{n_agree}/3 agree ({', '.join(era_df['sign'])})", "PASS" if g4_pass else "FAIL")

# ---- G5 power language ----
underpowered = (not g3_pass) and (mde80 > 3 * abs(T_obs))
log("\n-- G5: power language --")
log(f"  MDE80={mde80:.4f} vs 3x|observed|={3 * abs(T_obs):.4f}")
log(f"  {'UNDERPOWERED_STILL' if underpowered else ('n/a (G3 PASS)' if g3_pass else 'FAIL is powered: MDE <= 3x|observed|')}")
gate("G5_power", "print UNDERPOWERED_STILL verbatim on any FAIL with MDE > 3x|observed|",
     "UNDERPOWERED_STILL" if underpowered else ("G3 PASS -> n/a" if g3_pass else "FAIL but MDE <= 3x|obs|"), "PASS")

# ---- G6 descriptive VIX leg (NOT a gate on the verdict) ----
log("\n-- G6: DESCRIPTIVE CONTEXT ONLY -- daily dVIX on FOMC vs control dates (joins VIX to DATES; not a gate,")
log("        cannot change the verdict) --")
try:
    vix = pd.read_parquet(REPO / "research/breadth_lab/BREADTH03_VRP/data/_VIX.parquet",
                          columns=["date", "close"],
                          filters=[("date", "<=", date(2026, 5, 29))])
    vix["date"] = pd.to_datetime(vix["date"])
    assert vix["date"].max() <= DEV_END, "VIX seal filter failed"
    vix = vix.sort_values("date").reset_index(drop=True)
    vix["dvix"] = vix["close"].diff()
    dv = vix.set_index("date")["dvix"]
    fdates = edates[lab_pos]
    cmask = np.ones(M, bool)
    cmask[lab_pos] = False
    cdates = edates[cmask]
    fd = dv.reindex(fdates).dropna()
    cd = dv.reindex(cdates).dropna()
    log(f"  source: research/breadth_lab/BREADTH03_VRP/data/_VIX.parquet, truncated at load to <= 2026-05-29 "
        f"(parquet row filter; post-seal rows never materialized); certification: as-found store")
    log(f"  mean dVIX on FOMC decision days:   {fd.mean():+.3f} pts (n={len(fd)})")
    log(f"  mean dVIX on control Tue/Wed days: {cd.mean():+.3f} pts (n={len(cd)})")
    for e, en in enumerate(ERA_NAMES):
        f_e = dv.reindex(edates[lab_pos[era_arr[lab_pos] == e]]).dropna()
        c_e = dv.reindex(edates[cmask & (era_arr == e)]).dropna()
        log(f"    {en:12s}: FOMC {f_e.mean():+.3f} (n={len(f_e)})  vs ctrl {c_e.mean():+.3f} (n={len(c_e)})")
    log("  dVX (VX futures daily): NO certified local VX daily store exists in this repo -- leg omitted; "
        "descriptive only, so this omission cannot affect any gate.")
    g6_obs = f"dVIX FOMC {fd.mean():+.3f} vs ctrl {cd.mean():+.3f}; dVX unavailable locally"
except Exception as ex:  # descriptive leg must never kill the run
    log(f"  VIX leg unavailable: {ex}")
    g6_obs = f"unavailable ({ex})"
gate("G6_descriptive_only", "dVIX/dVX printed as DESCRIPTIVE CONTEXT ONLY; explicitly not a gate",
     g6_obs, "PASS")

# ---- verdict ----
if g3_pass and g4_pass:
    verdict = "PASS"
elif g3_pass:
    verdict = "REGIME_LOCAL"
elif underpowered:
    verdict = "FAIL (UNDERPOWERED_STILL)"
else:
    verdict = "FAIL"
if (not g3_pass) and p_two <= 0.05 and T_obs > 0:
    verdict += " -- significant in the OPPOSITE (expansion) direction"

log("\n" + "=" * 100)
log("GATE TABLE (program-printed)")
log("=" * 100)
w1 = max(len(g[0]) for g in gate_rows)
log(f"{'GATE':<{w1}} | {'PASS-FAIL':<9} | SPEC | OBSERVED")
log("-" * 100)
for name, sp, ob, pf in gate_rows:
    log(f"{name:<{w1}} | {pf:<9} | {sp} | {ob}")
log("-" * 100)
log(f"VERDICT: {verdict}")
log(f"Every number above: evidence status DISCOVERY_CONSUMED.")

# ---- per-day table ----
rows = []
for (p, q) in zip(lab_pos, lab_anc):
    d = edates[p]
    a = ANCHORS[q]
    k = a.replace(":", "")
    r = elig.loc[d]
    cells_l = cell_arr[p]
    rows.append(dict(
        date=str(d.date()), weekday=["Mon", "Tue", "Wed", "Thu", "Fri"][int(r["weekday"])],
        era=ERA_NAMES[era_arr[p]], anchor=a,
        n_pre=int(r[f"npre_{k}"]), n_post=int(r[f"npost_{k}"]),
        rv_pre=float(r[f"rvpre_{k}"]), rv_post=float(r[f"rvpost_{k}"]),
        log_ratio=round(float(ratio_mat[p, q]), 4),
        matched_diff=round(float(obs_diffs[list(lab_pos).index(p)]), 4),
        status="INCLUDED",
    ))
for d, wd, a in thursday_excl:
    rows.append(dict(date=str(d.date()), weekday=wd[:3], era=ERA_NAMES[era_of_year(d.year)], anchor=a,
                     n_pre="", n_post="", rv_pre="", rv_post="", log_ratio="", matched_diff="",
                     status="EXCLUDED_NON_TUE_WED"))
for d, wd, a in data_excl:
    rows.append(dict(date=str(d.date()), weekday=wd[:3], era=ERA_NAMES[era_of_year(d.year)], anchor=a,
                     n_pre="", n_post="", rv_pre="", rv_post="", log_ratio="", matched_diff="",
                     status="EXCLUDED_DATA_INCOMPLETE"))
fomc_df = pd.DataFrame(rows).sort_values("date")
fomc_df.to_csv(OUT / "fomc_table.csv", index=False)

(OUT / "gate_table.txt").write_text("\n".join(_log_lines) + "\n", encoding="utf-8")
print(f"\nwrote {OUT / 'gate_table.txt'}, fomc_table.csv ({len(fomc_df)} rows), era_table.csv")
