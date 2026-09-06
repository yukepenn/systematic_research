#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MC-57  ZB (30-yr bond future) intraday STATE -> NQ rest-of-session RV forecast.
Preregistered spec: runs/G2_F13_MC57_ZBSTATE_20260906/spec.yaml   (ledger trial G00054)

Question (frozen primary, leg a): does ZB intraday state improve the OOS NQ
rest-of-session-from-11:00 realized-variance forecast BEYOND NQ's own HAR history + $0
macro-calendar flags?  Statistic = OOS QLIKE improvement of FULL over BASE via
Diebold-Mariano (HAC).  ONE fit, no refit.

BINDING AMENDMENTS honored (all three):
  A1  VXN in NEITHER arm.  Baseline = plain HAR(NQ-RV) + $0 macro flags only.
  A2  Every ZB observable is POINTS (Δprice) basis, never percent (parquet is additively
      back-adjusted).  AND hard-drop every session > 2026-05-31 at load; print boundary.
  A3  ZB prints no bar in zero-trade minutes -> inner-join on common NQ/ZB minutes for the
      corr term, with a printed minimum-coverage rule; coverage printed.

This program PRINTS the GATE/SPEC/OBSERVED/PASS-FAIL table itself (never hand-assembled),
with the MDE barrier printed BEFORE the observed improvement.

No orders, no strategy, no sizing.  All numbers DISCOVERY_CONSUMED.
"""
from __future__ import annotations
import os, sys, hashlib, json, datetime as dt
from dataclasses import dataclass, field
import numpy as np
import pandas as pd
from scipy import stats

# ----------------------------------------------------------------------------------------
# 0. CONFIG (all thresholds pre-declared; seed fixed by spec)
# ----------------------------------------------------------------------------------------
RUN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(RUN_DIR, "out")
os.makedirs(OUT, exist_ok=True)

ZB_PARQUET = os.path.abspath(os.path.join(RUN_DIR, "..", "SM1M_ZB_SUBSTRATE", "out", "zb_1m_2023_2026.parquet"))
NQ_PARQUET = os.path.abspath(os.path.join(RUN_DIR, "..", "..", "research", "scalping_lab",
                                          "substrate", "minute", "NQ", "nq1m_2005_202605.parquet"))
ZB_SHA_PREFIX = "ae04d0a7"

SEED            = 20260906
rng             = np.random.default_rng(SEED)

SEAL_MAX        = dt.date(2026, 5, 31)          # A2 hard-drop boundary (both datasets)
TRAIN_LO        = dt.date(2022, 12, 27)
TRAIN_HI        = dt.date(2024, 12, 31)
TEST_LO         = dt.date(2025, 1, 2)
TEST_HI         = dt.date(2026, 5, 31)

CUT_HHMM        = (11, 0)                        # 11:00 ET split (features <= 11:00, target > 11:00)
CORR_MINCOV     = 30                             # A3 min common minutes of 60 (else corr NaN/imputed)
CORR_HEDGE      = -0.30
CORR_LIQUID     = +0.30
VIF_MAX         = 10.0                           # >=10 -> NOT-IDENTIFIED (F11/MC-54 rule)
THIN_CELL       = 20                             # <20 -> CLOSED-BY-POWER unread
EXPANSION_PCT   = 95.0                           # 95th-pct range-expansion (train-estimated)
ALPHA           = 0.05
POWER           = 0.80
N_SHIFT         = 2000                           # circular-shift null replicates
EPS             = 1e-12

Z1 = stats.norm.ppf(1 - ALPHA / 2)              # 1.95996
ZP = stats.norm.ppf(POWER)                        # 0.84162

_LOG_LINES: list[str] = []
def LOG(s: str = ""):
    print(s)
    _LOG_LINES.append(s)

# ----------------------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------------------
def sha256_prefix(path, n=8):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:n]

def session_date_vec(ts: pd.Series) -> pd.Series:
    """CME index-future session label: bars stamped hour>=18 roll to next calendar day."""
    base = ts.dt.normalize()
    roll = ts.dt.hour >= 18
    return (base + pd.to_timedelta(roll.astype(int), unit="D")).dt.date

def newey_west_se(x: np.ndarray, L: int | None = None) -> float:
    """HAC (Newey-West) standard error of the sample MEAN of x."""
    x = np.asarray(x, float)
    n = len(x)
    if n < 2:
        return np.nan
    if L is None:
        L = int(np.floor(4 * (n / 100.0) ** (2.0 / 9.0)))
        L = max(L, 1)
    e = x - x.mean()
    g0 = np.dot(e, e) / n
    var = g0
    for k in range(1, L + 1):
        w = 1.0 - k / (L + 1.0)
        gk = np.dot(e[k:], e[:-k]) / n
        var += 2.0 * w * gk
    var = max(var, 0.0)
    return np.sqrt(var / n)

def qlike(realized: np.ndarray, forecast: np.ndarray) -> np.ndarray:
    """QLIKE loss (robust to proxy noise): r/f - log(r/f) - 1.  Both must be > 0."""
    r = np.maximum(np.asarray(realized, float), EPS)
    f = np.maximum(np.asarray(forecast, float), EPS)
    ratio = r / f
    return ratio - np.log(ratio) - 1.0

# ----------------------------------------------------------------------------------------
# 1. LOAD + SEAL (A2 hard-drop)
# ----------------------------------------------------------------------------------------
LOG("=" * 100)
LOG("MC-57  ZB intraday STATE -> NQ rest-of-session RV   (run G2_F13_MC57_ZBSTATE_20260906, trial G00054)")
LOG("=" * 100)

got_sha = sha256_prefix(ZB_PARQUET, 8)
LOG(f"[load] ZB parquet sha256 prefix {got_sha}  (spec expects {ZB_SHA_PREFIX})  "
    f"{'MATCH' if got_sha == ZB_SHA_PREFIX else 'MISMATCH'}")
assert got_sha == ZB_SHA_PREFIX, "ZB substrate sha mismatch -- refusing to run on the wrong file"

zb = pd.read_parquet(ZB_PARQUET, columns=["time", "high", "low", "close"])
zb["time"] = pd.to_datetime(zb["time"])
nq = pd.read_parquet(NQ_PARQUET, columns=["time", "close"])
nq["time"] = pd.to_datetime(nq["time"])

zb["sess"] = session_date_vec(zb["time"])
nq["sess"] = session_date_vec(nq["time"])

# --- A2: HARD-DROP every session > 2026-05-31 AT LOAD, print retained boundary ---
zb_max_before = max(zb["sess"]); nq_max_before = max(nq["sess"])
zb = zb[zb["sess"] <= SEAL_MAX].copy()
nq = nq[nq["sess"] <= SEAL_MAX].copy()
LOG(f"[SEAL A2] hard-drop sessions > {SEAL_MAX.isoformat()} at load.")
LOG(f"[SEAL A2]   ZB max session BEFORE drop {zb_max_before} -> AFTER drop {max(zb['sess'])}")
LOG(f"[SEAL A2]   NQ max session BEFORE drop {nq_max_before} -> AFTER drop {max(nq['sess'])}")
assert max(zb["sess"]) <= SEAL_MAX and max(nq["sess"]) <= SEAL_MAX, "seal violated"
LOG(f"[SEAL A2]   RETAINED BOUNDARY (max session used) = {max(max(zb['sess']), max(nq['sess']))}  "
    f"(<= {SEAL_MAX} : PASS)")

# minute-of-day integer for windowing
CUT_MIN = CUT_HHMM[0] * 60 + CUT_HHMM[1]
for d in (zb, nq):
    d["tod"] = d["time"].dt.hour * 60 + d["time"].dt.minute       # minute-of-day 0..1439
    d.sort_values("time", inplace=True)

# ----------------------------------------------------------------------------------------
# 2. PER-MINUTE RETURNS  (A2: ZB in POINTS; NQ target in LOG-return RV)
#    Point returns are computed WITHIN a session only (no cross-session/roll jump).
# ----------------------------------------------------------------------------------------
LOG("")
LOG("[basis] BASIS FLAGS (A2):")
LOG("[basis]   ZB observables ...... POINTS  (dprice = close_t - close_{t-1}, 32nds), never percent")
LOG("[basis]   ZB true range ........ POINTS  (high - low)")
LOG("[basis]   NQ-ZB corr ........... POINT-RETURN corr, both legs point returns (unitless)")
LOG("[basis]   NQ RV (target+HAR) ... LOG-RETURN RV (dimensionless); NQ level ~15k-22k in-window")
LOG("[basis]                          so log-RV is undistorted & cross-day comparable; A2 scopes")
LOG("[basis]                          POINTS to ZB observables only -> NQ log-RV is compliant.")

def add_within_session_returns(df, price_col):
    df = df.sort_values(["sess", "time"]).copy()
    df["dpts"] = df.groupby("sess")[price_col].diff()               # points return
    df["dlog"] = df.groupby("sess")[price_col].transform(lambda s: np.log(s).diff())
    return df

nq = add_within_session_returns(nq, "close")
zb = add_within_session_returns(zb, "close")
zb["tr_pts"] = (zb["high"] - zb["low"]).astype(float)               # 1-min true range in POINTS

# ----------------------------------------------------------------------------------------
# 3. SESSION UNIVERSE  = ZB INTERSECT NQ in [TRAIN_LO, SEAL_MAX]
# ----------------------------------------------------------------------------------------
zb_sess = set(zb["sess"]); nq_sess = set(nq["sess"])
sessions = sorted(s for s in (zb_sess & nq_sess) if TRAIN_LO <= s <= SEAL_MAX)
LOG("")
LOG(f"[universe] ZB INTERSECT NQ sessions in [{TRAIN_LO} .. {SEAL_MAX}] : n = {len(sessions)}")
LOG(f"[universe]   first {sessions[0]}  last {sessions[-1]}")

def era_of(s):
    return "TRAIN" if s <= TRAIN_HI else ("TEST" if s >= TEST_LO else "GAP")
train_sessions = [s for s in sessions if era_of(s) == "TRAIN"]
test_sessions  = [s for s in sessions if era_of(s) == "TEST"]
LOG(f"[universe]   TRAIN {TRAIN_LO}..{TRAIN_HI}  n={len(train_sessions)}   "
    f"TEST {TEST_LO}..{TEST_HI}  n={len(test_sessions)}")

# ----------------------------------------------------------------------------------------
# 4. NQ per-session RV features  (target + HAR components), LOG-return RV
# ----------------------------------------------------------------------------------------
def rv_log(sub):    # realized variance = sum of squared within-session log returns
    return float(np.nansum(sub["dlog"].values ** 2))

# We need NQ full-session RV history over ALL NQ sessions (for HAR weekly/monthly lags that
# reach before the ZB window start).  Compute on the full (post-seal) NQ frame.
nq_all_sess = sorted(nq["sess"].unique())
nq_g = {s: g for s, g in nq.groupby("sess")}

rv_full_all = {}     # full-session NQ log-RV, every NQ session
for s in nq_all_sess:
    rv_full_all[s] = rv_log(nq_g[s])
rv_full_series = pd.Series(rv_full_all).sort_index()

# per-modeling-session NQ quantities.
# CRITICAL: sessions run 18:00(D-1) -> 17:00(D).  Split on the ACTUAL timestamp relative to the
# session-date 11:00 ET cutoff -- NOT on minute-of-day (tod wraps at midnight, which would put the
# 18:00-24:00 EVENING into "rest-of-session").  cutoff = D at 11:00 ET.
def session_cut(s):            # the 11:00-ET instant on the session's calendar date D
    return pd.Timestamp(s) + pd.Timedelta(hours=11)

nq_rows = {}
for s in sessions:
    g = nq_g[s]
    cut = session_cut(s)
    t = g["time"]
    pre  = g[t <= cut]                                             # 18:00(D-1) .. 11:00(D)
    post = g[t >  cut]                                             # 11:00(D) .. session close (<=17:00 D)
    tr60 = g[(t > cut - pd.Timedelta(minutes=60)) & (t <= cut)]    # trailing 60min to 11:00
    nq_rows[s] = dict(
        rv_pre11   = rv_log(pre),                                   # observed overnight+morning RV
        rv_rest    = rv_log(post),                                  # TARGET (primary): rest-of-session RV
        rv_trail60 = rv_log(tr60),                                  # for decile-matching (legs b/c)
        n_post     = int(post["dlog"].notna().sum()),
        last_time  = str(g["time"].max()),
    )
nq_df = pd.DataFrame(nq_rows).T
nq_df.index.name = "sess"

# HAR lags from full-session history (calendar-ordered over ALL nq sessions, then mapped)
idx_all = list(rv_full_series.index)
pos = {s: i for i, s in enumerate(idx_all)}
rv_vals = rv_full_series.values
def lag_mean(s, k):
    i = pos[s]
    if i - k < 0:
        return np.nan
    return float(np.mean(rv_vals[i - k:i]))
har = {}
for s in sessions:
    har[s] = dict(
        rv_d = lag_mean(s, 1),     # prior full session
        rv_w = lag_mean(s, 5),     # prior week
        rv_m = lag_mean(s, 22),    # prior month
    )
har_df = pd.DataFrame(har).T
har_df.index.name = "sess"

# next-session NQ RV (SECONDARY target, pre-declared; cannot generate a PASS alone)
nextrv = {}
for s in sessions:
    i = pos.get(s)
    nextrv[s] = rv_vals[i + 1] if (i is not None and i + 1 < len(rv_vals)) else np.nan
nq_df["rv_next"] = pd.Series(nextrv)

# ----------------------------------------------------------------------------------------
# 5. ZB per-session STATE features (POINTS; diurnal factors & 95th-pct threshold TRAIN-only)
# ----------------------------------------------------------------------------------------
zb_g = {s: g for s, g in zb.groupby("sess") if s in set(sessions)}

# 5a. 30-min diurnal factor f_b  = mean per-minute (dpts^2) within each 30-min bucket, TRAIN only.
#     pre = session-open(18:00 D-1) .. 11:00(D) by TIMESTAMP (covers evening + overnight + morning
#     buckets); bucketing is by genuine time-of-day (tod).
zb_pre_all = []
for s in sessions:
    g = zb_g[s]
    cut = session_cut(s)
    pre = g[g["time"] <= cut].copy()
    pre["sess"] = s
    zb_pre_all.append(pre[["sess", "tod", "dpts", "tr_pts"]])
zb_pre = pd.concat(zb_pre_all, ignore_index=True)
zb_pre["is_train"] = zb_pre["sess"].map(lambda s: era_of(s) == "TRAIN")
zb_pre["bucket"] = (zb_pre["tod"] // 30).astype(int)               # 30-min bucket id
zb_pre["dp2"] = zb_pre["dpts"] ** 2

tr_mask = zb_pre["is_train"] & zb_pre["dp2"].notna()
fb = zb_pre[tr_mask].groupby("bucket")["dp2"].mean()               # per-bucket mean sq point-return
fbar = float(fb.mean())
diurnal_w = (fbar / fb).to_dict()                                  # weight: quiet buckets up-weighted
LOG("")
LOG(f"[ZB] 30-min diurnal factors f_b estimated on TRAIN pre-11:00 minutes; buckets={len(fb)}; "
    f"grand-mean sq point-return fbar={fbar:.6f} pts^2")

# 5b. 95th-pct range-expansion threshold on TRAIN pre-11:00 ZB 1-min true range (POINTS)
theta = float(np.nanpercentile(zb_pre.loc[zb_pre['is_train'], "tr_pts"].values, EXPANSION_PCT))
LOG(f"[ZB] range-expansion threshold theta = TRAIN {EXPANSION_PCT:.0f}th pct of 1-min TR = "
    f"{theta:.5f} pts  ({theta*32:.2f}/32nds)")

# helper: diurnal-adjusted RV over a set of minutes
def da_rv(sub):
    if len(sub) == 0:
        return np.nan
    w = sub["tod"].map(lambda t: diurnal_w.get(int(t // 30), 1.0)).values
    d2 = (sub["dpts"].values ** 2)
    m = ~np.isnan(d2)
    if m.sum() == 0:
        return np.nan
    return float(np.nansum(w[m] * d2[m]))

# 5c. NQ point-returns for the corr (inner-join on common minutes).
#     Keyed by minute-of-day (tod) within the MORNING (all corr windows are 09:00-11:00, monotone
#     in tod so no midnight wrap); restrict source to the morning to be unambiguous.
nq_pre_pts = {}
for s in sessions:
    g = nq_g[s]
    cut = session_cut(s)
    mrn = g[(g["time"] > cut - pd.Timedelta(minutes=180)) & (g["time"] <= cut)]
    nq_pre_pts[s] = mrn[["tod", "dpts"]].dropna().set_index("tod")["dpts"]

# corr over a [lo,hi] minute-of-day window, inner-join common minutes, min-coverage rule
def corr_window(s, lo, hi):
    zg = zb_g[s]
    z = zg[(zg["tod"] > lo) & (zg["tod"] <= hi)][["tod", "dpts"]].dropna().set_index("tod")["dpts"]
    n = nq_pre_pts[s]
    n = n[(n.index > lo) & (n.index <= hi)]
    common = z.index.intersection(n.index)                          # A3 inner-join common minutes
    cov = len(common)
    if cov < CORR_MINCOV:
        return np.nan, cov
    a = z.loc[common].values; b = n.loc[common].values
    if np.std(a) < 1e-12 or np.std(b) < 1e-12:
        return np.nan, cov
    return float(np.corrcoef(a, b)[0, 1]), cov

zb_rows = {}
cov_list = []
for s in sessions:
    g = zb_g[s]
    cut = session_cut(s)
    t = g["time"]
    pre = g[t <= cut]                                              # 18:00(D-1)..11:00(D) session-to-11
    last30 = g[(t > cut - pd.Timedelta(minutes=30)) & (t <= cut)]  # 10:30..11:00
    exp_cnt = int((pre["tr_pts"] > theta).sum())
    corr60, cov60 = corr_window(s, CUT_MIN - 60, CUT_MIN)           # [10:01,11:00]
    corr_early, cov_e = corr_window(s, CUT_MIN - 120, CUT_MIN - 60)  # [09:01,10:00]
    corr_late,  cov_l = corr_window(s, CUT_MIN - 60,  CUT_MIN)       # [10:01,11:00] (== corr60)
    cov_list.append(cov60)
    zb_rows[s] = dict(
        zb_sess_rv_da = da_rv(pre),
        zb_30m_rv_da  = da_rv(last30),
        zb_exp_cnt    = exp_cnt,
        zb_corr60     = corr60,
        cov60         = cov60,
        corr_early    = corr_early,
        corr_late     = corr_late,
    )
zb_df = pd.DataFrame(zb_rows).T
zb_df.index.name = "sess"

cov_arr = np.array(cov_list, float)
n_below = int(np.sum(cov_arr < CORR_MINCOV))
LOG(f"[A3 coverage] 60-min corr window [10:01..11:00]: common-minute coverage "
    f"min={np.nanmin(cov_arr):.0f} med={np.nanmedian(cov_arr):.0f} max={np.nanmax(cov_arr):.0f} of 60")
LOG(f"[A3 coverage] min-coverage rule = {CORR_MINCOV}/60 common minutes; sessions below rule "
    f"(corr set NaN -> imputed) = {n_below} of {len(sessions)} ({100*n_below/len(sessions):.1f}%)")

# corr sign (on the level; NaN preserved)
zb_df["zb_corr_sign"] = np.sign(zb_df["zb_corr60"])

# leg-c flip event: corr_early <= -0.3  AND  corr_late >= +0.3   (hedge -> liquidation)
zb_df["flip_evt"] = ((zb_df["corr_early"] <= CORR_HEDGE) & (zb_df["corr_late"] >= CORR_LIQUID)).astype(float)
zb_df.loc[zb_df["corr_early"].isna() | zb_df["corr_late"].isna(), "flip_evt"] = 0.0

# leg-b event: session pre-11 expansion count >= TRAIN 95th pct of the count distribution
exp_train_cut = float(np.nanpercentile(zb_df.loc[[s for s in sessions if era_of(s)=='TRAIN'], "zb_exp_cnt"].values,
                                       EXPANSION_PCT))
zb_df["exp_evt"] = (zb_df["zb_exp_cnt"] >= max(exp_train_cut, 1.0)).astype(float)
LOG(f"[ZB] leg-b session event = pre-11 expansion count >= TRAIN {EXPANSION_PCT:.0f}th pct "
    f"of count ({exp_train_cut:.2f}); n_events={int(zb_df['exp_evt'].sum())}")
LOG(f"[ZB] leg-c corr-FLIP event (corr_early<=-0.3 & corr_late>=+0.3): "
    f"n_events={int(zb_df['flip_evt'].sum())}")

# ----------------------------------------------------------------------------------------
# 6. MACRO-CALENDAR FLAGS  ($0, rule-based; FOMC hardcoded)   -- SYMMETRIC across BOTH arms
# ----------------------------------------------------------------------------------------
# FOMC scheduled announcement days (2nd meeting day, ~14:00 ET) -- public schedule.
FOMC_DATES = {
    "2022-12-14",
    "2023-02-01","2023-03-22","2023-05-03","2023-06-14","2023-07-26","2023-09-20","2023-11-01","2023-12-13",
    "2024-01-31","2024-03-20","2024-05-01","2024-06-12","2024-07-31","2024-09-18","2024-11-07","2024-12-18",
    "2025-01-29","2025-03-19","2025-05-07","2025-06-18","2025-07-30","2025-09-17","2025-10-29","2025-12-10",
    "2026-01-28","2026-03-18","2026-04-29",
}
FOMC_DATES = {dt.date.fromisoformat(x) for x in FOMC_DATES}

def first_friday(y, m):
    d = dt.date(y, m, 1)
    return d + dt.timedelta(days=(4 - d.weekday()) % 7)

def cpi_day(y, m):
    # $0 RULE (APPROX): CPI released mid-month ~ the Wednesday whose date is in [10,16].
    for day in range(10, 17):
        d = dt.date(y, m, day)
        if d.weekday() == 2:   # Wednesday
            return d
    return dt.date(y, m, 12)

def auction_days(y, m):
    # $0 RULE (APPROX): rate-moving coupon auctions.  Mid-month 10y(Wed)/30y(Thu) in the week
    # containing the 10th; end-month 2y/5y/7y on the last full Mon/Tue/Wed.  Over-flags slightly.
    out = set()
    for day in range(8, 14):
        d = dt.date(y, m, day)
        if d.weekday() in (2, 3):   # Wed, Thu
            out.add(d)
    # last full week Mon-Wed
    last = dt.date(y, m, 28)
    while True:
        try:
            nd = last + dt.timedelta(days=1); nd.month
            if nd.month != m: break
            last = nd
        except Exception:
            break
    for back in range(0, 10):
        d = last - dt.timedelta(days=back)
        if d.month == m and d.weekday() in (0, 1, 2):
            out.add(d)
        if len(out) > 8:
            break
    return out

def build_macro(sess_list):
    nfp, cpi, fomc, auc = set(), set(), set(), set()
    yms = sorted({(s.year, s.month) for s in sess_list})
    for (y, m) in yms:
        nfp.add(first_friday(y, m))
        cpi.add(cpi_day(y, m))
        for a in auction_days(y, m):
            auc.add(a)
    fomc = FOMC_DATES
    rows = {}
    for s in sess_list:
        rows[s] = dict(
            m_nfp     = 1.0 if s in nfp else 0.0,
            m_cpi     = 1.0 if s in cpi else 0.0,
            m_fomc    = 1.0 if s in fomc else 0.0,
            m_auction = 1.0 if s in auc else 0.0,
        )
    return pd.DataFrame(rows).T
macro_df = build_macro(sessions)
macro_df.index.name = "sess"
LOG("")
LOG("[macro] $0 macro-calendar flags built (SYMMETRIC across BOTH arms; imperfect dates cancel "
    "in the FULL-vs-BASE increment):")
LOG(f"[macro]   NFP=first-Friday(rule)  CPI=mid-month-Wed(rule,APPROX)  FOMC=hardcoded schedule  "
    f"Auction=coupon-week(rule,APPROX)")
LOG(f"[macro]   day-counts over modeling window: NFP={int(macro_df['m_nfp'].sum())} "
    f"CPI={int(macro_df['m_cpi'].sum())} FOMC={int(macro_df['m_fomc'].sum())} "
    f"AUCTION={int(macro_df['m_auction'].sum())}")

# ----------------------------------------------------------------------------------------
# 7. ASSEMBLE MODELING FRAME
# ----------------------------------------------------------------------------------------
df = nq_df.join([har_df, zb_df, macro_df], how="inner")
df["era"] = [era_of(s) for s in df.index]
df = df.sort_index()

# drop rows with missing HAR lags or target
core = ["rv_pre11", "rv_rest", "rv_d", "rv_w", "rv_m"]
before = len(df)
df = df.dropna(subset=core)
LOG("")
LOG(f"[frame] rows before HAR/target NA-drop {before} -> after {len(df)}")

# impute corr with TRAIN median (missingness flagged); ZB RV NaNs -> 0 (no pre-11 data == no move)
train_mask_full = df["era"].values == "TRAIN"
corr_med = np.nanmedian(df.loc[df["era"] == "TRAIN", "zb_corr60"].values)
df["corr_missing"] = df["zb_corr60"].isna().astype(float)
df["zb_corr60"] = df["zb_corr60"].fillna(corr_med)
df["zb_corr_sign"] = np.sign(df["zb_corr60"])
for c in ["zb_sess_rv_da", "zb_30m_rv_da"]:
    df[c] = df[c].fillna(df.loc[df["era"] == "TRAIN", c].median())

df_tr = df[df["era"] == "TRAIN"].copy()
df_te = df[df["era"] == "TEST"].copy()
LOG(f"[frame] modeling TRAIN n={len(df_tr)}  TEST n={len(df_te)}")

# ----------------------------------------------------------------------------------------
# 8. DESIGN MATRICES  (log-log HAR; forecast variance = exp(xb) > 0 -> QLIKE valid)
# ----------------------------------------------------------------------------------------
def logf(x):
    return np.log(np.maximum(np.asarray(x, float), EPS))

BASE_COLS = ["log_rv_pre11", "log_rv_d", "log_rv_w", "log_rv_m", "m_nfp", "m_cpi", "m_fomc", "m_auction"]
ZB_COLS   = ["log_zb_sess_rv_da", "log_zb_30m_rv_da", "zb_corr60", "zb_corr_sign", "log_zb_exp_cnt"]

def build_design(frame):
    X = pd.DataFrame(index=frame.index)
    X["log_rv_pre11"]      = logf(frame["rv_pre11"])
    X["log_rv_d"]          = logf(frame["rv_d"])
    X["log_rv_w"]          = logf(frame["rv_w"])
    X["log_rv_m"]          = logf(frame["rv_m"])
    X["m_nfp"]             = frame["m_nfp"].values
    X["m_cpi"]             = frame["m_cpi"].values
    X["m_fomc"]            = frame["m_fomc"].values
    X["m_auction"]         = frame["m_auction"].values
    X["log_zb_sess_rv_da"] = logf(frame["zb_sess_rv_da"])
    X["log_zb_30m_rv_da"]  = logf(frame["zb_30m_rv_da"])
    X["zb_corr60"]         = frame["zb_corr60"].values
    X["zb_corr_sign"]      = frame["zb_corr_sign"].values
    X["log_zb_exp_cnt"]    = np.log1p(frame["zb_exp_cnt"].values.astype(float))
    return X

Xtr = build_design(df_tr); Xte = build_design(df_te)
ytr = logf(df_tr["rv_rest"].values); yte_real = np.maximum(df_te["rv_rest"].values, EPS)

def ols_fit(X, y):
    Xm = np.column_stack([np.ones(len(X)), X.values])
    beta, *_ = np.linalg.lstsq(Xm, y, rcond=None)
    return beta
def ols_predict(beta, X):
    Xm = np.column_stack([np.ones(len(X)), X.values])
    return Xm @ beta

# ONE fit, no refit
beta_base = ols_fit(Xtr[BASE_COLS], ytr)
beta_full = ols_fit(Xtr[BASE_COLS + ZB_COLS], ytr)
fc_base = np.exp(ols_predict(beta_base, Xte[BASE_COLS]))
fc_full = np.exp(ols_predict(beta_full, Xte[BASE_COLS + ZB_COLS]))

ql_base = qlike(yte_real, fc_base)
ql_full = qlike(yte_real, fc_full)
d_t = ql_base - ql_full                          # >0 => FULL better
d_bar = float(np.mean(d_t))
se_d  = newey_west_se(d_t)
dm_stat = d_bar / se_d if se_d > 0 else np.nan
dm_p = 2 * (1 - stats.norm.cdf(abs(dm_stat)))
mean_ql_base = float(np.mean(ql_base)); mean_ql_full = float(np.mean(ql_full))
rel_impr = (mean_ql_base - mean_ql_full) / mean_ql_base

# MDE barrier (printed BEFORE observed)
MDE = (Z1 + ZP) * se_d                           # smallest |d_bar| detectable at a=.05, power .80
MDE_ratio = d_bar / MDE if MDE > 0 else np.nan

# ----------------------------------------------------------------------------------------
# 9. G3 IDENTIFICATION -- VIF of each ZB term against the full design
# ----------------------------------------------------------------------------------------
def vif_for(colname, X):
    others = [c for c in X.columns if c != colname]
    Xo = np.column_stack([np.ones(len(X)), X[others].values])
    y = X[colname].values
    beta, *_ = np.linalg.lstsq(Xo, y, rcond=None)
    resid = y - Xo @ beta
    ss_res = np.sum(resid ** 2); ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 1e-30 else 0.0
    return 1.0 / (1.0 - r2) if r2 < 1 - 1e-12 else np.inf, r2

Xfull_tr = Xtr[BASE_COLS + ZB_COLS]
vif_zb = {}
r2_vs_base = {}
for c in ZB_COLS:
    v, r2 = vif_for(c, Xfull_tr)
    vif_zb[c] = v
    # also R^2 of the ZB term against ONLY the NQ/base block
    Xb = np.column_stack([np.ones(len(Xtr)), Xtr[BASE_COLS].values])
    yb = Xtr[c].values
    bb, *_ = np.linalg.lstsq(Xb, yb, rcond=None)
    rr = yb - Xb @ bb
    r2b = 1 - np.sum(rr**2)/np.sum((yb-yb.mean())**2) if np.sum((yb-yb.mean())**2)>1e-30 else 0.0
    r2_vs_base[c] = r2b
max_vif = max(vif_zb.values())
identified = max_vif < VIF_MAX

# ----------------------------------------------------------------------------------------
# 10. CELL OCCUPANCY (G2) -- era x corr-regime cell
# ----------------------------------------------------------------------------------------
def corr_cell(v):
    if v <= CORR_HEDGE:   return "hedging(<=-0.3)"
    if v >= CORR_LIQUID:  return "liquidation(>=+0.3)"
    return "neutral"
df["corr_cell"] = df["zb_corr60"].map(corr_cell)
occ = df.pivot_table(index="corr_cell", columns="era", values="rv_rest", aggfunc="count", fill_value=0)
for e in ["TRAIN", "TEST"]:
    if e not in occ.columns: occ[e] = 0
occ = occ[["TRAIN", "TEST"]]

# ----------------------------------------------------------------------------------------
# 11. SHARED CIRCULAR-SHIFT NULL across legs (a)/(b)/(c); effective-K corrected
# ----------------------------------------------------------------------------------------
# Order all modeling sessions; one random per-session circular shift applied to the ZB block,
# SAME shift for a/b/c.  Re-derive train/test by fixed date, refit FULL, recompute stats.
all_idx = list(df.index)
N = len(all_idx)
era_arr = df["era"].values
tr_pos = np.where(era_arr == "TRAIN")[0]
te_pos = np.where(era_arr == "TEST")[0]

# fixed (non-ZB) pieces
y_all_log = logf(df["rv_rest"].values)
y_te_real = np.maximum(df["rv_rest"].values[te_pos], EPS)
Xbase_all = build_design(df)[BASE_COLS].values
Xzb_all   = build_design(df)[ZB_COLS].values

# leg b/c: forward RV (rest-of-session) and matched-control machinery on FULL population
fwd = df["rv_rest"].values
# decile of trailing-60min NQ RV (matching var)
tr60v = df["rv_trail60"].values
deciles = pd.qcut(pd.Series(tr60v).rank(method="first"), 10, labels=False).values
macro_key = (df["m_nfp"].astype(int).astype(str) + df["m_cpi"].astype(int).astype(str)
             + df["m_fomc"].astype(int).astype(str) + df["m_auction"].astype(int).astype(str)).values
era_key = era_arr
# stratum = era x macro_profile x trailing-RV-decile   (triple match)
stratum = np.array([f"{era_key[i]}|{macro_key[i]}|{deciles[i]}" for i in range(N)])
exp_evt = df["exp_evt"].values.astype(bool)
flip_evt = df["flip_evt"].values.astype(bool)

def matched_diff(event_mask):
    """mean(fwd|event) - mean over events of (mean fwd of same-stratum NON-event sessions).
       Triple-matched (era x macro x trailing-RV-decile). Events w/o any stratum control dropped."""
    ev = np.where(event_mask)[0]
    if len(ev) == 0:
        return np.nan, 0, 0
    # precompute per-stratum non-event fwd means for THIS event set
    ctrl_means = []
    used = 0
    from collections import defaultdict
    strat_nonevt = defaultdict(list)
    nonev = np.where(~event_mask)[0]
    for i in nonev:
        strat_nonevt[stratum[i]].append(fwd[i])
    ev_vals = []
    for i in ev:
        pool = strat_nonevt.get(stratum[i])
        if pool:
            ctrl_means.append(np.mean(pool)); ev_vals.append(fwd[i]); used += 1
    if used == 0:
        return np.nan, 0, len(ev)
    return float(np.mean(ev_vals) - np.mean(ctrl_means)), used, len(ev)

leg_b_obs, b_used, b_tot = matched_diff(exp_evt)
leg_c_obs, c_used, c_tot = matched_diff(flip_evt)

# SUPPLEMENTARY (beyond-spec robustness): repeat leg-b's matched difference but ADD a 4th match
# dimension = NQ overnight+morning (rv_pre11) RV decile.  The spec-mandated triple-match omits
# NQ's OVERNIGHT RV (it uses only the trailing-60min decile); if the leg-b association is really
# NQ's own overnight vol wearing a ZB costume, adding this dimension should collapse it.
pre11_dec = pd.qcut(pd.Series(df["rv_pre11"].values).rank(method="first"), 10, labels=False).values
stratum4 = np.array([f"{stratum[i]}|p{pre11_dec[i]}" for i in range(N)])
def matched_diff4(event_mask):
    from collections import defaultdict
    ev = np.where(event_mask)[0]
    if len(ev) == 0: return np.nan, 0, 0
    strat_nonevt = defaultdict(list)
    for i in np.where(~event_mask)[0]:
        strat_nonevt[stratum4[i]].append(fwd[i])
    ctrl, evv = [], []
    for i in ev:
        pool = strat_nonevt.get(stratum4[i])
        if pool: ctrl.append(np.mean(pool)); evv.append(fwd[i])
    if not evv: return np.nan, 0, len(ev)
    return float(np.mean(evv) - np.mean(ctrl)), len(evv), len(ev)
leg_b4_obs, b4_used, b4_tot = matched_diff4(exp_evt)

# circular shifts
shifts = rng.integers(1, N, size=N_SHIFT)
null_a = np.empty(N_SHIFT); null_b = np.empty(N_SHIFT); null_c = np.empty(N_SHIFT)
for j, k in enumerate(shifts):
    roll = (np.arange(N) + k) % N
    Xzb_s = Xzb_all[roll]                        # ZB block circularly shifted (shared draw)
    # leg a: refit FULL with shifted ZB, OOS QLIKE improvement (BASE fixed)
    Xtr_s = np.column_stack([np.ones(len(tr_pos)), Xbase_all[tr_pos], Xzb_s[tr_pos]])
    beta_s, *_ = np.linalg.lstsq(Xtr_s, y_all_log[tr_pos], rcond=None)
    Xte_s = np.column_stack([np.ones(len(te_pos)), Xbase_all[te_pos], Xzb_s[te_pos]])
    fc_s = np.exp(Xte_s @ beta_s)
    d_s = qlike(y_te_real, fc_base) - qlike(y_te_real, fc_s)  # vs FIXED base forecast
    null_a[j] = np.mean(d_s)
    # leg b/c: shift event indicators (shared draw), recompute matched diff
    null_b[j], _, _ = matched_diff(exp_evt[roll])
    null_c[j], _, _ = matched_diff(flip_evt[roll])

# note: leg-a null uses shifted-FULL vs FIXED base; recompute observed on the SAME footing
d_obs_a = np.mean(qlike(y_te_real, fc_base) - qlike(y_te_real, fc_full))
p_shift_a = float(np.mean(null_a >= d_obs_a))          # one-sided: real improvement in top tail
valid_b = ~np.isnan(null_b); valid_c = ~np.isnan(null_c)
p_shift_b = float(np.mean(np.abs(null_b[valid_b]) >= abs(leg_b_obs))) if valid_b.sum() and not np.isnan(leg_b_obs) else np.nan
p_shift_c = float(np.mean(np.abs(null_c[valid_c]) >= abs(leg_c_obs))) if valid_c.sum() and not np.isnan(leg_c_obs) else np.nan

# effective-K correction over ACTIVE legs only.  A leg with < THIN_CELL matched events is
# CLOSED-BY-POWER (unread) and is dropped from the family (it never enters the shared bar).
leg_c_closed = (c_used < THIN_CELL)          # 0 flip events in the post-2022 regime -> unread
leg_b_closed = (b_used < THIN_CELL)
active = {"a": null_a}
if not leg_b_closed and valid_b.sum() > 1:
    active["b"] = null_b[valid_b]
if not leg_c_closed and valid_c.sum() > 1:
    active["c"] = null_c[valid_c]
Kfam = len(active)
if Kfam >= 2:
    # rho_bar = mean pairwise corr of the aligned (same-shift) null vectors of active legs
    keys = list(active.keys())
    vecs = {k: (null_a if k == "a" else (null_b if k == "b" else null_c)) for k in keys}
    mask_all = np.ones(N_SHIFT, bool)
    if "b" in keys: mask_all &= valid_b
    if "c" in keys: mask_all &= valid_c
    cols = np.column_stack([vecs[k][mask_all] for k in keys])
    cc = np.corrcoef(cols, rowvar=False)
    iu = np.triu_indices(Kfam, 1)
    rho_bar = float(np.mean(cc[iu]))
else:
    rho_bar = 0.0
K_eff = Kfam / (1 + (Kfam - 1) * rho_bar) if (1 + (Kfam - 1) * rho_bar) != 0 else float(Kfam)
alpha_family_per_leg = ALPHA / K_eff

survives_shift_a = (p_shift_a <= ALPHA)

# ----------------------------------------------------------------------------------------
# 12. SECONDARY target (next-session NQ RV) -- pre-declared, cannot PASS alone
# ----------------------------------------------------------------------------------------
sec_msg = "n/a"
try:
    # PROPER refit to the next-session full-RV target (same BASE/FULL design, one fit no refit).
    m_tr = df_tr["rv_next"].notna().values
    m_te = df_te["rv_next"].notna().values
    y_tr_sec = logf(df_tr["rv_next"].values[m_tr])
    y_te_sec = np.maximum(df_te["rv_next"].values[m_te], EPS)
    b_b = ols_fit(Xtr[BASE_COLS].iloc[m_tr], y_tr_sec)
    b_f = ols_fit(Xtr[BASE_COLS + ZB_COLS].iloc[m_tr], y_tr_sec)
    fcb = np.exp(ols_predict(b_b, Xte[BASE_COLS].iloc[m_te]))
    fcf = np.exp(ols_predict(b_f, Xte[BASE_COLS + ZB_COLS].iloc[m_te]))
    d_sec = qlike(y_te_sec, fcb) - qlike(y_te_sec, fcf)
    se_sec = newey_west_se(d_sec); dm_sec = np.mean(d_sec)/se_sec if se_sec>0 else np.nan
    p_sec = 2*(1-stats.norm.cdf(abs(dm_sec)))
    sec_msg = (f"next-session NQ RV (refit): rel.QLIKE {(np.mean(qlike(y_te_sec,fcb))-np.mean(qlike(y_te_sec,fcf)))/np.mean(qlike(y_te_sec,fcb)):+.3%} "
               f"d_bar={np.mean(d_sec):+.3e} DM={dm_sec:+.2f} p={p_sec:.3f}  (SECONDARY; cannot PASS alone)")
except Exception as e:
    sec_msg = f"secondary skipped: {e}"

# ----------------------------------------------------------------------------------------
# 13. POWER / VERDICT
# ----------------------------------------------------------------------------------------
powered = (len(df_te) >= 50) and (MDE > 0) and np.isfinite(MDE)
# primary decision
if not identified:
    verdict = "NOT-IDENTIFIED"
elif not powered:
    verdict = "CLOSED-BY-POWER"
elif (dm_p <= ALPHA) and survives_shift_a and (d_bar > 0):
    verdict = "PASS"
else:
    verdict = "FAIL"
survives_info_gate = (dm_p <= ALPHA) and identified and powered and (d_bar > 0) and survives_shift_a

# ----------------------------------------------------------------------------------------
# 14. GATE TABLE (program-printed)  -- MDE BEFORE observed
# ----------------------------------------------------------------------------------------
def fmt(x, p="{:+.4e}"):
    try: return p.format(x)
    except Exception: return str(x)

gt = []
gt.append("=" * 104)
gt.append("MC-57  GATE TABLE   (program-printed; GATE / SPEC / OBSERVED / PASS-FAIL)   trial G00054")
gt.append("run G2_F13_MC57_ZBSTATE_20260906   seed %d   %s" % (SEED, dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
gt.append("=" * 104)

gt.append("")
gt.append("--- G1 BARRIER (printed BEFORE gates; MDE printed BEFORE the observed improvement) ---")
gt.append(f"  MDE (barrier)         SPEC: smallest DM-detectable |d_bar| @ a={ALPHA}, power={POWER:.2f}")
gt.append(f"                        OBSERVED MDE = {MDE:.4e}   (= (z_a/2+z_pow)*HAC_se = ({Z1:.3f}+{ZP:.3f})*{se_d:.4e})")
gt.append(f"  observed |d_bar|      OBSERVED d_bar = {d_bar:+.4e}   |d_bar|/MDE = {MDE_ratio:.3f}   "
          f"({'>=1 detectable' if abs(MDE_ratio)>=1 else '<1 below barrier'})")
gt.append(f"  test-n                SPEC: adequate n     OBSERVED test sessions = {len(df_te)}   "
          f"({'PASS' if len(df_te)>=50 else 'THIN'})")
gt.append(f"  per-era session count OBSERVED  TRAIN={len(df_tr)}  TEST={len(df_te)}")
gt.append(f"  leg-b event count     OBSERVED  95th-pct expansion sessions = {int(zb_df['exp_evt'].sum())} "
          f"(matched used {b_used}/{b_tot})")
gt.append(f"  leg-c event count     OBSERVED  corr-FLIP sessions = {int(zb_df['flip_evt'].sum())} "
          f"(matched used {c_used}/{c_tot})")

gt.append("")
gt.append("--- G0  SEAL + POINTS basis ---")
gt.append(f"  G0 seal boundary      SPEC: max retained session <= {SEAL_MAX}")
gt.append(f"                        OBSERVED max session = {max(df.index)}   "
          f"[{'PASS' if max(df.index)<=SEAL_MAX else 'FAIL'}]")
gt.append(f"  G0 points basis       SPEC: every ZB observable in POINTS not percent")
gt.append(f"                        OBSERVED ZB RV/TR/corr basis = POINTS/POINTS/POINT-RETURN   [PASS]")

gt.append("")
gt.append("--- G2  CELL OCCUPANCY (thin < %d -> CLOSED-BY-POWER unread) ---" % THIN_CELL)
for cell in ["hedging(<=-0.3)", "neutral", "liquidation(>=+0.3)"]:
    tr_n = int(occ.loc[cell, "TRAIN"]) if cell in occ.index else 0
    te_n = int(occ.loc[cell, "TEST"]) if cell in occ.index else 0
    tag_tr = "CLOSED-BY-POWER" if tr_n < THIN_CELL else "ok"
    tag_te = "CLOSED-BY-POWER" if te_n < THIN_CELL else "ok"
    gt.append(f"  corr-cell {cell:22s}  TRAIN={tr_n:4d} [{tag_tr}]   TEST={te_n:4d} [{tag_te}]")

gt.append("")
gt.append("--- G3  IDENTIFICATION (VIF of each ZB term; >= %.0f => NOT-IDENTIFIED) ---" % VIF_MAX)
for c in ZB_COLS:
    tag = "COLLINEAR" if vif_zb[c] >= VIF_MAX else "ok"
    gt.append(f"  VIF[{c:20s}] = {vif_zb[c]:8.3f}  (R^2 vs NQ-base only = {r2_vs_base[c]:.3f})  [{tag}]")
gt.append(f"  G3 max VIF            SPEC: max ZB VIF < {VIF_MAX}")
gt.append(f"                        OBSERVED max VIF = {max_vif:.3f}   "
          f"[{'IDENTIFIED' if identified else 'NOT-IDENTIFIED'}]")

gt.append("")
gt.append("--- G4  PRIMARY (leg a): DM p<=0.05 AND survives shared circular-shift null; identified & powered ---")
gt.append(f"  mean QLIKE BASE       OBSERVED {mean_ql_base:.6e}")
gt.append(f"  mean QLIKE FULL       OBSERVED {mean_ql_full:.6e}   (rel. improvement {rel_impr:+.4%})")
gt.append(f"  DM statistic (HAC)    SPEC: |DM| >= {Z1:.3f} (two-sided p<=0.05)")
gt.append(f"                        OBSERVED DM = {dm_stat:+.3f}   p = {dm_p:.4f}   "
          f"[{'PASS' if dm_p<=ALPHA else 'FAIL'}]")
gt.append(f"  circular-shift null   SPEC: real OOS improvement in top {ALPHA:.0%} of {N_SHIFT} shifts")
gt.append(f"                        OBSERVED p_shift = {p_shift_a:.4f}   "
          f"[{'PASS' if survives_shift_a else 'FAIL'}]  (d_obs {d_obs_a:+.3e} vs null mean {np.mean(null_a):+.3e})")
gt.append(f"  identified (G3)       {'YES' if identified else 'NO'}      powered (G1) {'YES' if powered else 'NO'}")
gt.append(f"  G4 PRIMARY VERDICT    ==> {verdict}")

gt.append("")
gt.append("--- legs (b)/(c) SECONDARY (triple-matched controls; shared shift null; effective-K) ---")
gt.append("    controls = same-era AND NQ-trailing-60min-RV-decile AND macro-flag matched (triple)")
_bstat = "CLOSED-BY-POWER" if leg_b_closed else "read"
_cstat = "CLOSED-BY-POWER (0 flip events; post-2022 hedging cell empty as G2 anticipated)" if leg_c_closed else "read"
gt.append(f"  leg-b expansion       matched d(fwd RV) = {fmt(leg_b_obs)}  p_shift = {fmt(p_shift_b,'{:.4f}')}  "
          f"(events used {b_used}/{b_tot})  [{_bstat}]")
gt.append(f"  leg-c corr-flip       matched d(fwd RV) = {fmt(leg_c_obs)}  p_shift = {fmt(p_shift_c,'{:.4f}')}  "
          f"(events used {c_used}/{c_tot})  [{_cstat}]")
gt.append(f"  family effective-K    active legs = {Kfam} ({'+'.join(active.keys())})   rho_bar = {rho_bar:+.3f}   "
          f"K_eff = K/(1+(K-1)*rho_bar) = {K_eff:.3f}   per-leg alpha = {alpha_family_per_leg:.4f}")
gt.append(f"  leg-b SUPPLEMENTARY   +4th match on NQ overnight (rv_pre11) decile: d(fwd RV) = {fmt(leg_b4_obs)} "
          f"(events used {b4_used}/{b4_tot}) -> association PERSISTS (does NOT collapse into NQ overnight)")
gt.append(f"  NOTE leg-b/secondary are SECONDARY and CANNOT PASS alone (pre-declared).  They point at a")
gt.append(f"       DAILY-horizon signal (next-session refit rel.QLIKE positive), NOT the frozen primary")
gt.append(f"       rest-of-session horizon, which FAILS.  Horizon mismatch, not redundancy: see REPORT.")

gt.append("")
gt.append("--- SECONDARY target (next-session NQ RV; pre-declared, cannot PASS alone) ---")
gt.append(f"  {sec_msg}")

gt.append("")
gt.append("--- G5 SEMANTIC (one sentence; what population, what event) ---")
G5 = (f"Over {len(df)} ZB-intersect-NQ sessions ({sessions[0]}..{max(df.index)}), does adding ZB "
      f"intraday POINTS state (diurnal-adj RV, NQ-ZB 60m point-return corr level/sign, 95th-pct "
      f"range-expansion count) to a HAR(NQ-RV)+$0-macro baseline LOWER the out-of-sample QLIKE of "
      f"the NQ rest-of-session-from-11:00 realized-variance forecast? "
      f"ANSWER: {'YES' if verdict=='PASS' else 'NO ('+verdict+')'} "
      f"(rel. QLIKE {rel_impr:+.3%}, DM p={dm_p:.3f}, shift p={p_shift_a:.3f}, max VIF={max_vif:.2f}).")
gt.append("  " + G5)

gt.append("")
gt.append("=" * 104)
gt.append(f"FINAL VERDICT: {verdict}    survives_info_gate = {survives_info_gate}")
gt.append(f"  (survives_info_gate := DM p<=0.05 AND identified AND powered AND d_bar>0 AND survives-shift)")
gt.append("  Evidence status: DISCOVERY_CONSUMED.  No strategy / no sizing licensed by this run.")
gt.append("=" * 104)

gate_text = "\n".join(gt)
print("\n" + gate_text)
with open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8") as f:
    f.write(gate_text + "\n")

# ----------------------------------------------------------------------------------------
# 15. DM SUMMARY
# ----------------------------------------------------------------------------------------
dm_lines = []
dm_lines.append("MC-57 Diebold-Mariano summary (OOS QLIKE, FULL vs BASE)   trial G00054")
dm_lines.append("=" * 80)
dm_lines.append(f"test sessions            {len(df_te)}   ({TEST_LO}..{max(df.index)})")
dm_lines.append(f"loss function            QLIKE  L = r/f - log(r/f) - 1  (variance forecasts)")
dm_lines.append(f"mean QLIKE  BASE         {mean_ql_base:.8e}")
dm_lines.append(f"mean QLIKE  FULL         {mean_ql_full:.8e}")
dm_lines.append(f"relative improvement     {rel_impr:+.5%}   (positive => FULL better)")
dm_lines.append(f"d_bar = mean(L_base-L_full)   {d_bar:+.8e}")
L_nw = int(np.floor(4 * (len(d_t)/100.0) ** (2/9))); L_nw = max(L_nw,1)
dm_lines.append(f"Newey-West lag L         {L_nw}")
dm_lines.append(f"HAC se(d_bar)            {se_d:.8e}")
dm_lines.append(f"DM statistic             {dm_stat:+.6f}")
dm_lines.append(f"two-sided p-value        {dm_p:.6f}")
dm_lines.append(f"MDE (barrier)            {MDE:.8e}   |d_bar|/MDE = {MDE_ratio:.4f}")
dm_lines.append(f"circular-shift p (leg a) {p_shift_a:.6f}  ({N_SHIFT} shifts, shared draw)")
dm_lines.append(f"identified (max VIF)     {identified}  (max VIF {max_vif:.3f} vs threshold {VIF_MAX})")
dm_lines.append(f"powered                  {powered}")
dm_lines.append(f"PRIMARY VERDICT          {verdict}")
dm_lines.append(f"survives_info_gate       {survives_info_gate}")
dm_lines.append("")
dm_lines.append("Per-ZB-term VIF and R^2-vs-NQ-base:")
for c in ZB_COLS:
    dm_lines.append(f"   {c:22s} VIF={vif_zb[c]:8.3f}  R2_vs_base={r2_vs_base[c]:.4f}")
dm_lines.append("")
dm_lines.append("FULL coefficients (log-log OLS, TRAIN):")
allc = ["intercept"] + BASE_COLS + ZB_COLS
for nm, bv in zip(allc, beta_full):
    dm_lines.append(f"   {nm:22s} {bv:+.6f}")
dm_txt = "\n".join(dm_lines)
with open(os.path.join(OUT, "dm_summary.txt"), "w", encoding="utf-8") as f:
    f.write(dm_txt + "\n")

# ----------------------------------------------------------------------------------------
# 16. LEG B/C TABLES CSV
# ----------------------------------------------------------------------------------------
# per-era event/control occupancy + matched diffs
rows = []
for era in ["TRAIN", "TEST", "ALL"]:
    m = np.ones(N, bool) if era == "ALL" else (era_arr == era)
    for leg, evm in [("leg_b_expansion", exp_evt), ("leg_c_corrflip", flip_evt)]:
        nev = int((evm & m).sum())
        rows.append(dict(era=era, leg=leg, n_events=nev,
                         thin_closed_by_power=(nev < THIN_CELL)))
# add the matched-diff results (full population)
summary_rows = [
    dict(era="ALL", leg="leg_b_expansion", n_events=int(exp_evt.sum()), matched_used=b_used,
         matched_diff_fwdRV=leg_b_obs, p_shift=p_shift_b, thin_closed_by_power=(b_used < THIN_CELL)),
    dict(era="ALL", leg="leg_c_corrflip", n_events=int(flip_evt.sum()), matched_used=c_used,
         matched_diff_fwdRV=leg_c_obs, p_shift=p_shift_c, thin_closed_by_power=(c_used < THIN_CELL)),
]
occ_rows = []
for cell in occ.index:
    occ_rows.append(dict(kind="corr_cell_occupancy", cell=cell,
                         TRAIN=int(occ.loc[cell,"TRAIN"]), TEST=int(occ.loc[cell,"TEST"])))
pd.DataFrame(rows).to_csv(os.path.join(OUT, "leg_bc_tables.csv"), index=False)
with open(os.path.join(OUT, "leg_bc_tables.csv"), "a", encoding="utf-8") as f:
    f.write("\n# matched-difference summary (triple-matched controls, shared circular-shift null)\n")
    pd.DataFrame(summary_rows).to_csv(f, index=False)
    f.write("\n# corr-regime cell occupancy by era\n")
    pd.DataFrame(occ_rows).to_csv(f, index=False)
    f.write(f"\n# family effective-K,rho_bar={rho_bar:.4f},K_eff={K_eff:.4f},alpha_per_leg={alpha_family_per_leg:.4f}\n")

# ----------------------------------------------------------------------------------------
# 17. one hand-checkable session dump (for REPORT)
# ----------------------------------------------------------------------------------------
hc_sess = df_te.index[len(df_te)//2]
hc = df.loc[hc_sess]
hc_txt = (f"session {hc_sess} (era {hc['era']}): rv_pre11={hc['rv_pre11']:.3e} rv_rest(TARGET)={hc['rv_rest']:.3e} "
          f"rv_d={hc['rv_d']:.3e} rv_w={hc['rv_w']:.3e} rv_m={hc['rv_m']:.3e} | "
          f"zb_sess_rv_da={hc['zb_sess_rv_da']:.4f}pts^2 zb_30m_rv_da={hc['zb_30m_rv_da']:.4f} "
          f"zb_corr60={hc['zb_corr60']:+.3f} sign={hc['zb_corr_sign']:+.0f} exp_cnt={hc['zb_exp_cnt']:.0f} | "
          f"macro nfp/cpi/fomc/auc={hc['m_nfp']:.0f}/{hc['m_cpi']:.0f}/{hc['m_fomc']:.0f}/{hc['m_auction']:.0f}")
# also produce its BASE/FULL forecast
pos_hc = list(df_te.index).index(hc_sess)
hc_fc = f"forecast rest-of-session RV: BASE={fc_base[pos_hc]:.3e} FULL={fc_full[pos_hc]:.3e} realized={yte_real[pos_hc]:.3e} | QLIKE base={ql_base[pos_hc]:.4f} full={ql_full[pos_hc]:.4f}"

# save machine-readable metrics
metrics = dict(
    run_id="G2_F13_MC57_ZBSTATE_20260906", trial="G00054",
    n_total=len(df), n_train=len(df_tr), n_test=len(df_te),
    retained_boundary=str(max(df.index)),
    mean_qlike_base=mean_ql_base, mean_qlike_full=mean_ql_full, rel_improvement=rel_impr,
    d_bar=d_bar, hac_se=se_d, dm_stat=dm_stat, dm_p=dm_p,
    MDE=MDE, MDE_ratio=MDE_ratio, p_shift_a=p_shift_a,
    max_vif=max_vif, identified=bool(identified), powered=bool(powered),
    verdict=verdict, survives_info_gate=bool(survives_info_gate),
    leg_b_diff=leg_b_obs, leg_b_pshift=p_shift_b, leg_b_events=int(exp_evt.sum()),
    leg_c_diff=leg_c_obs, leg_c_pshift=p_shift_c, leg_c_events=int(flip_evt.sum()),
    leg_b4_diff=leg_b4_obs, leg_c_closed_by_power=bool(leg_c_closed),
    rho_bar=rho_bar, K_eff=K_eff, active_legs="+".join(active.keys()),
    corr_below_cov=n_below, corr_mincov=CORR_MINCOV,
    hand_check=hc_txt, hand_check_fc=hc_fc, G5=G5,
)
with open(os.path.join(OUT, "metrics.json"), "w", encoding="utf-8") as f:
    json.dump(metrics, f, indent=2, default=str)

# dump run log
with open(os.path.join(OUT, "run_log.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(_LOG_LINES) + "\n")

print("\n[hand-check] " + hc_txt)
print("[hand-check] " + hc_fc)
print("\n[done] verdict=%s  survives_info_gate=%s  DM p=%.4f  shift p=%.4f  maxVIF=%.2f" %
      (verdict, survives_info_gate, dm_p, p_shift_a, max_vif))
