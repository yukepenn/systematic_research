#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
G3_EVENT_ZB_20260906 — ledger G00067, family GENESIS3_EVENT.
ZB native EVENT diagnostic: 6-event catalog -> conditional forward-path tables with matched
unconditional controls, session-block bootstrap CIs, circular-shift nulls, K_eff multiplicity.

DIAGNOSTIC / DISCOVERY ONLY. Verdict per event: DEAD / DESCRIPTIVE / LEAD (screen, not promotion).

ALL operationalizations below are fixed BEFORE any result is computed (this file is the
executable preregistration of the spec's catalog; no threshold/horizon is added after results).

Data: runs/SM1M_ZB_SUBSTRATE/out/zb_1m_2023_2026.parquet — POINTS basis ONLY (additively
back-adjusted, DELEV01: point differences only; never % returns, never level thresholds).
Bars END-stamped; ET session time 18:00->17:00 (bar stamped hh>=18 belongs to next calendar day).

E1 calendar: the SAME macro-flag set used by G2_F10 (which G2_F13 mirrors with $0 rules):
runs/GENESIS_H2_CALENDAR_20260828/out/calendar_artifacts/daytype_sessions_{NFP,CPI}_DAY.csv
(both are 08:30 ET releases; FOMC is 14:00 and is NOT an 08:30 release, hence excluded from E1).

Cost band (G00062 / W2_ZB_NATIVE model, BASIS=MODELED): commission $4.36/RT + spread
{0.5,1,2} ticks -> ALL_IN $19.98 / $35.61 / $66.86. Conservative all-in = $66.86 (2-tick).
LEAD screen clause (ii): |delta| >= 2 x $66.86 = $133.72/contract = 0.13372 pt = 4.28 ticks.

PREREGISTERED SCREEN (from spec.method.lead_screen):
  cell is LEAD  iff  (i) p_corr = min(1, p_raw * K_eff) < 0.05   [circular-shift null]
                AND (ii) |delta_ctrl| * $1000 >= $133.72
                AND (iii) n_events >= 30.
  event verdict: LEAD if any cell LEAD;
                 DESCRIPTIVE if no LEAD but any cell has (p_raw < 0.05) OR
                             (|delta_ctrl|*$1000 >= $133.72 AND n>=30);
                 DEAD otherwise.

NULL: circular shift of the event-label series (the full label tuple: indicator + direction +
tercile + within-session window minute travels with the label; outcomes stay with the receiving
session) along each event family's chronologically ordered eligible-session calendar.
ONE SHARED DRAW: N_SHIFTS=2000 uniform u_k drawn once (seed 20260906) and shared across ALL
cells/events; per family offset_k = 1 + floor(u_k * (L_f - 1)). delta_ctrl = obs - mean(null).
E1 additionally gets a SECONDARY release-specificity null (shift the release flag only,
recompute sign/terciles from the receiving sessions' own moves) — printed, NOT in the screen.

K_eff: K = number of preregistered cells (55); rho_bar = mean over cell pairs of
max(0, corr(null-stat vectors)) — valid because the null draws are SHARED; K_eff = K/(1+(K-1)rho_bar).

CIs: session-block bootstrap (events are session-indexed units): moving blocks of length 5
over the chronologically ordered event contribution series, B=2000, percentile 95%.

AS-OF convention: price at clock time m = close of last bar <= m with staleness <= 15 min,
else missing (session ineligible for that anchor). Session anchors used:
open_sess = open of first bar (18:01); close_last = close of actual last bar;
settlement = as-of 15:00 close (CBOT treasuries settle 14:00 CT = 15:00 ET; spec E6 concurs).

Event operationalizations (fixed here):
 E1: releases = (NFP u CPI) n U1. r1 = c0845-c0830 (r1==0 events excluded, count printed).
     Terciles of |r1| over the nonzero-r1 event set (np.quantile 1/3, 2/3).
     Outcomes f = c1030-c0845 and c1500-c0845. Cells per horizon: sign(2, raw) +
     tercile(3, aligned by sign(r1)) + sign x tercile(6, raw) = 11; x2 horizons = 22.
 E2: on = c0800 - open_sess; sigma20 = std(ddof=1) of prior 20 sessions' on (>=16 non-NaN).
     Event(th): |on| >= th*sigma20, th in {1.5, 2.0}. Outcome f = c1500 - c0800.
     Cells per th: sign+(raw), sign-(raw), aligned = 3; x2 = 6.
 E3: high5/low5 = max/min of prior 5 sessions' highs/lows; range5 = high5-low5 (POINT range).
     Compression: range5 <= 20th pct of the trailing 60 range5 values (shift-1 rolling).
     Breach: first minute with bar-high > high5 (up) or bar-low < low5 (down); same-minute
     tie -> session dropped (count printed). Outcomes: rem = close_last - asof(breach_min);
     nxt = next session close_last - close_last. Cells: dir(2) x {rem,nxt} raw + aligned
     {rem,nxt} = 6.
 E4: event: close_last(t) > max(high, t-20..t-1) [up] or < min(low) [down].
     Outcomes fk = close_last(t+k) - close_last(t), k=1,2,3. Cells: dir x k raw (6) +
     aligned per k (3) = 9.
 E5: mv(t,m) = asof(m) - asof(m-30) on the 15-min-tolerance grid; sigma30(t) = pooled std of
     all mv values over the prior 20 sessions (pooled count >= 10000 required; overlapping,
     stated). Shock: first minute m* (31 <= m* <= 1320) with |mv| >= 2.5*sigma30.
     No-follow-through: sign(mv)*(asof(m*+60) - asof(m*)) < 0.25*|mv| (first shock decides;
     if its +60 anchor is missing or last bar < m*+60 the session is DROPPED, not re-scanned).
     Outcomes: to_close = close_last - asof(m*+60); nxt = next-session move. Cells: aligned
     to_close, aligned nxt, sign x {to_close,nxt} raw = 6.
 E6: s1 = c1500 - c1455; dnet = c1500 - open_sess (day's net move to settlement).
     Outcome f = close_last - c1500 (needs last bar >= 16:30). Cells: sign(s1) raw(2) +
     aligned-by-s1 (1) + sign(dnet) raw(2) + aligned-by-dnet (1) = 6. Zero-sign events are
     excluded per conditioning variable (counts printed).

Total preregistered cells K = 22+6+6+9+6+6 = 55. ALL are reported; none is selected out.
"""

import os
import sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RUN_DIR = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(RUN_DIR, os.pardir, os.pardir))

ZB_PARQUET = os.path.join(REPO, "runs", "SM1M_ZB_SUBSTRATE", "out", "zb_1m_2023_2026.parquet")
NFP_CSV = os.path.join(REPO, "runs", "GENESIS_H2_CALENDAR_20260828", "out",
                       "calendar_artifacts", "daytype_sessions_NFP_DAY.csv")
CPI_CSV = os.path.join(REPO, "runs", "GENESIS_H2_CALENDAR_20260828", "out",
                       "calendar_artifacts", "daytype_sessions_CPI_DAY.csv")
OUT = os.path.join(RUN_DIR, "out")
os.makedirs(OUT, exist_ok=True)

SEAL_MAX_SESSION = pd.Timestamp("2026-07-31").date()
POINT_VALUE = 1000.0          # ZB: $1000 per point; tick 1/32 = 0.03125 pt = $31.25
TICK = 1.0 / 32.0
COST_RUNGS = {"0.5tk": 19.98, "1tk": 35.61, "2tk": 66.86}   # G00062 ALL_IN model, MODELED
COST_CONSERVATIVE = 66.86
SCREEN_DOLLARS = 2.0 * COST_CONSERVATIVE                     # $133.72
N_MIN = 30
N_SHIFTS = 2000
SEED = 20260906
B_BOOT = 2000
BLOCK_L = 5
ASOF_LIMIT = 15               # minutes of allowed staleness for as-of anchors

rng_master = np.random.default_rng(SEED)
U_SHARED = rng_master.random(N_SHIFTS)          # ONE shared draw for every family/cell
rng_boot = np.random.default_rng(SEED + 1)

LINES = []
def say(s=""):
    print(s)
    LINES.append(s)

def two_sided_p(obs, null):
    null = np.asarray(null, dtype=float)
    null = null[np.isfinite(null)]
    k = len(null)
    p_hi = (1 + np.sum(null >= obs)) / (k + 1)
    p_lo = (1 + np.sum(null <= obs)) / (k + 1)
    return min(1.0, 2.0 * min(p_hi, p_lo))

def block_boot_ci(y, B=B_BOOT, L=BLOCK_L, rng=None):
    """Moving-block bootstrap 95% CI for the mean of chronological series y."""
    y = np.asarray(y, dtype=float)
    y = y[np.isfinite(y)]
    n = len(y)
    if n < 3:
        return (np.nan, np.nan)
    L = min(L, n)
    nblocks = int(np.ceil(n / L))
    starts_max = n - L + 1
    means = np.empty(B)
    for b in range(B):
        st = rng.integers(0, starts_max, size=nblocks)
        idx = (st[:, None] + np.arange(L)[None, :]).ravel()[:n]
        means[b] = y[idx].mean()
    return (float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5)))

# ==================================================================== load + seal
df = pd.read_parquet(ZB_PARQUET)
t = pd.to_datetime(df["time"])
hh = t.dt.hour.to_numpy(); mm = t.dt.minute.to_numpy()
sess_ts = t.dt.normalize() + pd.to_timedelta((hh >= 18).astype(int), unit="D")
sess_date = sess_ts.dt.date.to_numpy()

sessions = np.array(sorted(set(sess_date)))
NS = len(sessions)
sess_idx = {d: i for i, d in enumerate(sessions)}
code = np.fromiter((sess_idx[d] for d in sess_date), dtype=np.int64, count=len(df))

max_sess = sessions.max()
g0_pass = max_sess <= SEAL_MAX_SESSION
assert g0_pass, f"SEAL VIOLATION: max session {max_sess} > {SEAL_MAX_SESSION}"

# grid check (sanity for the POINTS basis: prices restored to the 1/32 grid)
frac = np.abs(df["close"].to_numpy() * 32 - np.round(df["close"].to_numpy() * 32))
g1_grid_share = float(np.mean(frac < 1e-6))

# ==================================================================== minute grids
# minute-of-session: 18:01 -> 1 ... 17:00 -> 1380
msess = ((hh * 60 + mm) - 1080) % 1440
assert msess.min() >= 1 and msess.max() <= 1380

closeA = np.full((NS, 1381), np.nan)
highA = np.full((NS, 1381), np.nan)
lowA = np.full((NS, 1381), np.nan)
closeA[code, msess] = df["close"].to_numpy()
highA[code, msess] = df["high"].to_numpy()
lowA[code, msess] = df["low"].to_numpy()

gridf = pd.DataFrame(closeA).ffill(axis=1, limit=ASOF_LIMIT).to_numpy()   # as-of closes

# per-session scalars
first_pos = np.array([np.flatnonzero(~np.isnan(closeA[i]))[0] for i in range(NS)])
last_pos = np.array([np.flatnonzero(~np.isnan(closeA[i]))[-1] for i in range(NS)])
open_first = np.full(NS, np.nan)
_openA = np.full((NS, 1381), np.nan)
_openA[code, msess] = df["open"].to_numpy()
open_first = _openA[np.arange(NS), first_pos]
close_last = closeA[np.arange(NS), last_pos]
high_s = np.nanmax(np.where(np.isnan(highA), -np.inf, highA), axis=1)
low_s = np.nanmin(np.where(np.isnan(lowA), np.inf, lowA), axis=1)

M0800, M0830, M0845, M1030, M1455, M1500 = 840, 870, 885, 990, 1255, 1260
c0800 = gridf[:, M0800]; c0830 = gridf[:, M0830]; c0845 = gridf[:, M0845]
c1030 = gridf[:, M1030]; c1455 = gridf[:, M1455]; c1500 = gridf[:, M1500]

nxt1 = np.full(NS, np.nan); nxt1[:-1] = close_last[1:] - close_last[:-1]
nxt2 = np.full(NS, np.nan); nxt2[:-2] = close_last[2:] - close_last[:-2]
nxt3 = np.full(NS, np.nan); nxt3[:-3] = close_last[3:] - close_last[:-3]

# ==================================================================== E1 calendar
nfp = set(pd.to_datetime(pd.read_csv(NFP_CSV)["session_date"]).dt.date)
cpi = set(pd.to_datetime(pd.read_csv(CPI_CSV)["session_date"]).dt.date)
rel_all = nfp | cpi
rel_in_window = {d for d in rel_all if sessions.min() <= d <= sessions.max()}

# ==================================================================== cell engine
CELLS = []   # dicts: event, cid, desc, fam (master idx), pos, align, kind, Y or win_m

def add_cell(event, cid, desc, fam, pos, align, kind, Y=None, win=None):
    CELLS.append(dict(event=event, cid=cid, desc=desc, fam=np.asarray(fam),
                      pos=np.asarray(pos, dtype=np.int64),
                      align=np.asarray(align, dtype=float),
                      kind=kind, Y=Y, win=(None if win is None else np.asarray(win, dtype=np.int64))))

def cell_values(c, k):
    """Contribution series (chronological in receiving order) for shift offset k (0 = observed)."""
    L = len(c["fam"])
    recv = (c["pos"] + k) % L
    if c["kind"] == "fixed":
        y = c["align"] * c["Y"][recv]
    else:
        mi = c["fam"][recv]
        y = c["align"] * (close_last[mi] - gridf[mi, c["win"]])
    return y

# -------------------------------------------------------------------- E1
u1 = np.flatnonzero(~np.isnan(c0830) & ~np.isnan(c0845) & ~np.isnan(c1030) & ~np.isnan(c1500))
fam1 = u1
fam1_dates = sessions[u1]
is_rel = np.array([d in rel_in_window for d in fam1_dates])
r1 = (c0845 - c0830)[fam1]
f1030 = (c1030 - c0845)[fam1]
f1500 = (c1500 - c0845)[fam1]

ev1_pos_all = np.flatnonzero(is_rel)
n_rel_zero = int(np.sum(r1[ev1_pos_all] == 0.0))
ev1_pos = ev1_pos_all[r1[ev1_pos_all] != 0.0]
s1sign_ev = np.sign(r1[ev1_pos])
absr = np.abs(r1[ev1_pos])
q33, q66 = np.quantile(absr, [1/3, 2/3])
terc_ev = np.where(absr <= q33, 1, np.where(absr <= q66, 2, 3))

for hname, Y in (("0845_1030", f1030), ("0845_1500", f1500)):
    for sg, sgn in (("+", 1.0), ("-", -1.0)):
        m = s1sign_ev == sgn
        add_cell("E1", f"E1_{hname}_sign{sg}", f"release, first-response sign {sg}, raw fwd {hname}",
                 fam1, ev1_pos[m], np.ones(m.sum()), "fixed", Y=Y)
    for tc in (1, 2, 3):
        m = terc_ev == tc
        add_cell("E1", f"E1_{hname}_terc{tc}_aligned", f"release, |resp| tercile {tc}, sign-aligned fwd {hname}",
                 fam1, ev1_pos[m], s1sign_ev[m], "fixed", Y=Y)
    for sg, sgn in (("+", 1.0), ("-", -1.0)):
        for tc in (1, 2, 3):
            m = (s1sign_ev == sgn) & (terc_ev == tc)
            add_cell("E1", f"E1_{hname}_sign{sg}_terc{tc}", f"release, sign {sg} x tercile {tc}, raw fwd {hname}",
                     fam1, ev1_pos[m], np.ones(m.sum()), "fixed", Y=Y)

# -------------------------------------------------------------------- E2
on_all = c0800 - open_first          # defined on every session that has both anchors
sig20 = np.full(NS, np.nan)
for i in range(NS):
    w = on_all[max(0, i - 20):i]
    w = w[np.isfinite(w)]
    if i >= 20 and len(w) >= 16:
        sig20[i] = np.std(w, ddof=1)
u2 = np.flatnonzero(np.isfinite(on_all) & np.isfinite(sig20) & ~np.isnan(c1500) & ~np.isnan(c0800))
fam2 = u2
on2 = on_all[fam2]
f2 = (c1500 - c0800)[fam2]
for th in (1.5, 2.0):
    evp = np.flatnonzero((np.abs(on2) >= th * sig20[fam2]) & (on2 != 0.0))
    sgn = np.sign(on2[evp])
    for sg, sv in (("+", 1.0), ("-", -1.0)):
        m = sgn == sv
        add_cell("E2", f"E2_th{th}_sign{sg}", f"|overnight|>={th}sig, sign {sg}, raw 0800->1500",
                 fam2, evp[m], np.ones(m.sum()), "fixed", Y=f2)
    add_cell("E2", f"E2_th{th}_aligned", f"|overnight|>={th}sig, overnight-sign-aligned 0800->1500",
             fam2, evp, sgn, "fixed", Y=f2)
n_e2_zero = int(np.sum(on2 == 0.0))

# -------------------------------------------------------------------- E3
hs = pd.Series(high_s); ls = pd.Series(low_s)
high5 = hs.shift(1).rolling(5).max().to_numpy()
low5 = ls.shift(1).rolling(5).min().to_numpy()
range5 = high5 - low5
pct20 = pd.Series(range5).shift(1).rolling(60).quantile(0.20).to_numpy()

u3 = np.flatnonzero(np.isfinite(range5) & np.isfinite(pct20) & np.isfinite(nxt1))
fam3 = u3
ev3_pos, ev3_dir, ev3_min = [], [], []
n_e3_tie = 0
for q, i in enumerate(fam3):
    if not (range5[i] <= pct20[i]):
        continue
    hu = highA[i] > high5[i]
    ld = lowA[i] < low5[i]
    fu = np.argmax(hu) if hu.any() else 10**9
    fd = np.argmax(ld) if ld.any() else 10**9
    if fu == 10**9 and fd == 10**9:
        continue
    if fu == fd:
        n_e3_tie += 1
        continue
    if fu < fd:
        d, mb = 1.0, fu
    else:
        d, mb = -1.0, fd
    if mb >= last_pos[i]:          # breach on the very last bar -> no remainder
        continue
    ev3_pos.append(q); ev3_dir.append(d); ev3_min.append(mb)
ev3_pos = np.array(ev3_pos, dtype=np.int64); ev3_dir = np.array(ev3_dir); ev3_min = np.array(ev3_min, dtype=np.int64)
nxt1_fam3 = nxt1[fam3]
for dg, dv in (("up", 1.0), ("down", -1.0)):
    m = ev3_dir == dv
    add_cell("E3", f"E3_rem_{dg}", f"compression break {dg}, raw break-day remainder",
             fam3, ev3_pos[m], np.ones(m.sum()), "window", win=ev3_min[m])
    add_cell("E3", f"E3_nxt_{dg}", f"compression break {dg}, raw next-session move",
             fam3, ev3_pos[m], np.ones(m.sum()), "fixed", Y=nxt1_fam3)
add_cell("E3", "E3_rem_aligned", "compression break, dir-aligned break-day remainder",
         fam3, ev3_pos, ev3_dir, "window", win=ev3_min)
add_cell("E3", "E3_nxt_aligned", "compression break, dir-aligned next-session move",
         fam3, ev3_pos, ev3_dir, "fixed", Y=nxt1_fam3)

# -------------------------------------------------------------------- E4
hi20 = hs.shift(1).rolling(20).max().to_numpy()
lo20 = ls.shift(1).rolling(20).min().to_numpy()
u4 = np.flatnonzero(np.isfinite(hi20) & np.isfinite(lo20) & np.isfinite(nxt3))
fam4 = u4
up4 = close_last[fam4] > hi20[fam4]
dn4 = close_last[fam4] < lo20[fam4]
ev4_pos = np.flatnonzero(up4 | dn4)
ev4_dir = np.where(up4[ev4_pos], 1.0, -1.0)
Y4 = {1: nxt1[fam4], 2: nxt2[fam4], 3: nxt3[fam4]}
for k in (1, 2, 3):
    for dg, dv in (("up", 1.0), ("down", -1.0)):
        m = ev4_dir == dv
        add_cell("E4", f"E4_next{k}_{dg}", f"20-sess extreme {dg}, raw next-{k}-session move",
                 fam4, ev4_pos[m], np.ones(m.sum()), "fixed", Y=Y4[k])
    add_cell("E4", f"E4_next{k}_aligned", f"20-sess extreme, dir-aligned next-{k}-session move",
             fam4, ev4_pos, ev4_dir, "fixed", Y=Y4[k])

# -------------------------------------------------------------------- E5
mvM = gridf[:, 31:1381] - gridf[:, 1:1351]        # col j <-> minute m=j+31
cnt = np.sum(np.isfinite(mvM), axis=1).astype(float)
s1_ = np.nansum(mvM, axis=1)
s2_ = np.nansum(mvM ** 2, axis=1)
sig30 = np.full(NS, np.nan)
for i in range(20, NS):
    C = cnt[i - 20:i].sum(); S1 = s1_[i - 20:i].sum(); S2 = s2_[i - 20:i].sum()
    if C >= 10000:
        var = (S2 - S1 * S1 / C) / (C - 1)
        sig30[i] = np.sqrt(var) if var > 0 else np.nan

u5 = np.flatnonzero(np.isfinite(sig30) & np.isfinite(nxt1))
fam5 = u5
ev5_pos, ev5_sign, ev5_min = [], [], []
n_e5_shock, n_e5_drop, n_e5_follow = 0, 0, 0
for q, i in enumerate(fam5):
    row = np.abs(mvM[i])
    mask = row >= 2.5 * sig30[i]
    mask[1320 - 31 + 1:] = False                     # need m* <= 1320 so m*+60 <= 1380
    if not mask.any():
        continue
    j = int(np.argmax(mask)); mstar = j + 31
    n_e5_shock += 1
    v = mvM[i, j]
    a60 = gridf[i, mstar + 60]
    if not np.isfinite(a60) or (mstar + 60) > last_pos[i]:
        n_e5_drop += 1
        continue
    further = np.sign(v) * (a60 - gridf[i, mstar])
    if further < 0.25 * abs(v):
        ev5_pos.append(q); ev5_sign.append(float(np.sign(v))); ev5_min.append(mstar + 60)
    else:
        n_e5_follow += 1
ev5_pos = np.array(ev5_pos, dtype=np.int64); ev5_sign = np.array(ev5_sign); ev5_min = np.array(ev5_min, dtype=np.int64)
nxt1_fam5 = nxt1[fam5]
add_cell("E5", "E5_toclose_aligned", "shock w/o follow-through, shock-aligned path (m*+60)->close",
         fam5, ev5_pos, ev5_sign, "window", win=ev5_min)
add_cell("E5", "E5_nxt_aligned", "shock w/o follow-through, shock-aligned next-session move",
         fam5, ev5_pos, ev5_sign, "fixed", Y=nxt1_fam5)
for dg, dv in (("up", 1.0), ("down", -1.0)):
    m = ev5_sign == dv
    add_cell("E5", f"E5_toclose_{dg}", f"shock {dg} w/o follow-through, raw path to close",
             fam5, ev5_pos[m], np.ones(m.sum()), "window", win=ev5_min[m])
    add_cell("E5", f"E5_nxt_{dg}", f"shock {dg} w/o follow-through, raw next-session move",
             fam5, ev5_pos[m], np.ones(m.sum()), "fixed", Y=nxt1_fam5)

# -------------------------------------------------------------------- E6
u6 = np.flatnonzero(~np.isnan(c1455) & ~np.isnan(c1500) & np.isfinite(open_first)
                    & (last_pos >= 1350))
fam6 = u6
s1_6 = (c1500 - c1455)[fam6]
dnet6 = (c1500 - open_first)[fam6]
f6 = (close_last - c1500)[fam6]
ev6a = np.flatnonzero(s1_6 != 0.0); sa = np.sign(s1_6[ev6a])
ev6b = np.flatnonzero(dnet6 != 0.0); sb = np.sign(dnet6[ev6b])
n_e6_zero_s1 = int(np.sum(s1_6 == 0.0)); n_e6_zero_dnet = int(np.sum(dnet6 == 0.0))
for sg, sv in (("+", 1.0), ("-", -1.0)):
    m = sa == sv
    add_cell("E6", f"E6_s1sign{sg}", f"settle-flurry 1455->1500 sign {sg}, raw 1500->close",
             fam6, ev6a[m], np.ones(m.sum()), "fixed", Y=f6)
add_cell("E6", "E6_s1_aligned", "settle-flurry-sign-aligned 1500->close",
         fam6, ev6a, sa, "fixed", Y=f6)
for sg, sv in (("+", 1.0), ("-", -1.0)):
    m = sb == sv
    add_cell("E6", f"E6_dnetsign{sg}", f"day-net (1800->1500) sign {sg}, raw 1500->close",
             fam6, ev6b[m], np.ones(m.sum()), "fixed", Y=f6)
add_cell("E6", "E6_dnet_aligned", "day-net-sign-aligned 1500->close",
         fam6, ev6b, sb, "fixed", Y=f6)

# ==================================================================== compute obs + nulls
K = len(CELLS)
null_mat = np.full((K, N_SHIFTS), np.nan)
results = []
for ci, c in enumerate(CELLS):
    L = len(c["fam"])
    offs = (1 + np.floor(U_SHARED * (L - 1))).astype(np.int64)
    y0 = cell_values(c, 0)
    n0 = int(np.sum(np.isfinite(y0)))
    obs = float(np.nanmean(y0)) if n0 else np.nan
    for k in range(N_SHIFTS):
        yk = cell_values(c, offs[k])
        null_mat[ci, k] = np.nanmean(yk) if np.any(np.isfinite(yk)) else np.nan
    nm = float(np.nanmean(null_mat[ci]))
    p_raw = two_sided_p(obs, null_mat[ci]) if n0 else np.nan
    lo, hi = block_boot_ci(y0, rng=rng_boot)
    results.append(dict(event=c["event"], cell=c["cid"], desc=c["desc"], n_events=n0,
                        obs_mean_pts=obs, null_mean_pts=nm,
                        delta_ctrl_pts=obs - nm, delta_ctrl_usd=(obs - nm) * POINT_VALUE,
                        ci95_lo_pts=lo, ci95_hi_pts=hi,
                        delta_ci95_lo_usd=(lo - nm) * POINT_VALUE if np.isfinite(lo) else np.nan,
                        delta_ci95_hi_usd=(hi - nm) * POINT_VALUE if np.isfinite(hi) else np.nan,
                        p_raw=p_raw))

# E1 secondary release-specificity null (shift the release FLAG only; conditioning recomputed
# from the receiving sessions' own r1; terciles recomputed per shift). Printed, not screened.
e1_cells = [(i, c) for i, c in enumerate(CELLS) if c["event"] == "E1"]
L1 = len(fam1)
offs1 = (1 + np.floor(U_SHARED * (L1 - 1))).astype(np.int64)
spec_null = {i: np.full(N_SHIFTS, np.nan) for i, _ in e1_cells}
relpos0 = np.flatnonzero(is_rel)
for k in range(N_SHIFTS):
    prel = (relpos0 + offs1[k]) % L1
    rr = r1[prel]
    keep = rr != 0.0
    prel = prel[keep]; rr = rr[keep]
    if len(prel) < 6:
        continue
    sg = np.sign(rr); ab = np.abs(rr)
    qa, qb = np.quantile(ab, [1/3, 2/3])
    tc = np.where(ab <= qa, 1, np.where(ab <= qb, 2, 3))
    for i, c in e1_cells:
        cid = c["cid"]
        hY = f1030 if "0845_1030" in cid else f1500
        if "_sign+" in cid and "_terc" not in cid:
            m = sg > 0; al = np.ones(m.sum())
        elif "_sign-" in cid and "_terc" not in cid:
            m = sg < 0; al = np.ones(m.sum())
        elif "_terc" in cid and "aligned" in cid:
            tt = int(cid.split("_terc")[1][0]); m = tc == tt; al = sg[m]
        else:
            sv = 1.0 if "sign+" in cid else -1.0
            tt = int(cid.split("_terc")[1][0])
            m = (sg == sv) & (tc == tt); al = np.ones(m.sum())
        if m.sum() == 0:
            continue
        spec_null[i][k] = np.mean(al * hY[prel[m]])
for i, c in e1_cells:
    r = results[i]
    r["p_release_specificity"] = two_sided_p(r["obs_mean_pts"], spec_null[i])

# ==================================================================== K_eff + screen
nm_c = null_mat - np.nanmean(null_mat, axis=1, keepdims=True)
sd = np.nanstd(null_mat, axis=1)
rho_sum, rho_n = 0.0, 0
CORR = np.corrcoef(np.nan_to_num(null_mat, nan=0.0))
for a in range(K):
    for b in range(a + 1, K):
        r_ab = CORR[a, b] if (sd[a] > 0 and sd[b] > 0) else 0.0
        rho_sum += max(0.0, r_ab); rho_n += 1
rho_bar = rho_sum / rho_n if rho_n else 0.0
K_eff = K / (1.0 + (K - 1) * rho_bar)
p_thresh = 0.05 / K_eff
min_p = 2.0 / (N_SHIFTS + 1)

for r in results:
    r["p_corr"] = min(1.0, r["p_raw"] * K_eff) if np.isfinite(r["p_raw"]) else np.nan
    r["gross_usd"] = abs(r["delta_ctrl_usd"]) if np.isfinite(r["delta_ctrl_usd"]) else np.nan
    r["pass_p"] = bool(np.isfinite(r["p_corr"]) and r["p_corr"] < 0.05)
    r["pass_cost"] = bool(np.isfinite(r["gross_usd"]) and r["gross_usd"] >= SCREEN_DOLLARS)
    r["pass_n"] = bool(r["n_events"] >= N_MIN)
    r["LEAD"] = r["pass_p"] and r["pass_cost"] and r["pass_n"]

verdicts = {}
for ev in ("E1", "E2", "E3", "E4", "E5", "E6"):
    rs = [r for r in results if r["event"] == ev]
    if any(r["LEAD"] for r in rs):
        v = "LEAD"
    elif any((np.isfinite(r["p_raw"]) and r["p_raw"] < 0.05) or (r["pass_cost"] and r["pass_n"])
             for r in rs):
        v = "DESCRIPTIVE"
    else:
        v = "DEAD"
    verdicts[ev] = v

# ==================================================================== controls.csv
ctrl_rows = []
def ctrl(event, name, arr, note):
    a = np.asarray(arr, dtype=float); a = a[np.isfinite(a)]
    ctrl_rows.append(dict(event=event, control=name, n=len(a),
                          mean_pts=float(a.mean()) if len(a) else np.nan,
                          sd_pts=float(a.std(ddof=1)) if len(a) > 1 else np.nan,
                          mean_usd=float(a.mean() * POINT_VALUE) if len(a) else np.nan,
                          note=note))
ctrl("E1", "uncond_0845_1030", f1030, "all eligible sessions, time-matched window")
ctrl("E1", "uncond_0845_1500", f1500, "all eligible sessions, time-matched window")
for sg, sv in (("+", 1.0), ("-", -1.0)):
    m = np.sign(r1) == sv
    ctrl("E1", f"allsession_sign{sg}_0845_1030", f1030[m],
         "ALL sessions conditioned on own 0830->0845 sign (generic-momentum reference)")
    ctrl("E1", f"allsession_sign{sg}_0845_1500", f1500[m],
         "ALL sessions conditioned on own 0830->0845 sign (generic-momentum reference)")
ctrl("E2", "uncond_0800_1500", f2, "all eligible sessions, time-matched window")
if len(ev3_min):
    w = np.array([np.nanmean(close_last[fam3] - gridf[fam3, m]) for m in ev3_min])
    ctrl("E3", "uncond_matched_remainder", w, "per-event breach-minute window averaged over ALL sessions")
ctrl("E3", "uncond_next_session", nxt1_fam3, "all eligible sessions")
ctrl("E4", "uncond_next1", Y4[1], "all eligible sessions")
ctrl("E4", "uncond_next2", Y4[2], "all eligible sessions")
ctrl("E4", "uncond_next3", Y4[3], "all eligible sessions")
if len(ev5_min):
    w = np.array([np.nanmean(close_last[fam5] - gridf[fam5, m]) for m in ev5_min])
    ctrl("E5", "uncond_matched_toclose", w, "per-event (m*+60)-minute window averaged over ALL sessions")
ctrl("E5", "uncond_next_session", nxt1_fam5, "all eligible sessions")
ctrl("E6", "uncond_1500_close", f6, "all eligible sessions, time-matched window")

pd.DataFrame(ctrl_rows).to_csv(os.path.join(OUT, "controls.csv"), index=False)
tab = pd.DataFrame(results)
tab.to_csv(os.path.join(OUT, "event_tables.csv"), index=False)

# ==================================================================== program-printed report
say("=" * 100)
say("G3_EVENT_ZB_20260906  (ledger G00067, family GENESIS3_EVENT)  ZB native EVENT diagnostic")
say(f"substrate: {os.path.relpath(ZB_PARQUET, REPO)}   sessions={NS}  "
    f"({sessions.min()} .. {sessions.max()})   POINTS basis, $1000/pt, tick $31.25")
say(f"E1 calendar: G2_F10 macro-flag set (NFP_DAY + CPI_DAY, GENESIS_H2_CALENDAR_20260828); "
    f"in-window releases={len(rel_in_window)} (NFP+CPI union)")
say(f"cost model (G00062, MODELED): ALL_IN rungs {COST_RUNGS}; conservative=${COST_CONSERVATIVE}; "
    f"screen 2x=${SCREEN_DOLLARS:.2f} = {SCREEN_DOLLARS/POINT_VALUE/TICK:.2f} ticks")
say(f"null: circular shift, ONE shared draw (seed={SEED}), N_SHIFTS={N_SHIFTS}; "
    f"delta_ctrl = obs - null-mean (the matched control for aligned cells)")
say(f"bootstrap: moving-block over chronological event series, L={BLOCK_L}, B={B_BOOT}")
say("")
say(f"event-family bookkeeping: E1 rel-events(nonzero r1)={len(ev1_pos)} (r1==0 dropped: {n_rel_zero}); "
    f"E2 universe={len(fam2)} (on==0: {n_e2_zero}); "
    f"E3 events={len(ev3_pos)} (same-minute ties dropped: {n_e3_tie}); "
    f"E4 events={len(ev4_pos)}; "
    f"E5 shocks={n_e5_shock} -> no-FT events={len(ev5_pos)} (dropped +60 missing: {n_e5_drop}, "
    f"followed-through: {n_e5_follow}); "
    f"E6 universe={len(fam6)} (s1==0: {n_e6_zero_s1}, dnet==0: {n_e6_zero_dnet})")
say("")
hdr = (f"{'cell':<26}{'n':>5}{'obs pts':>10}{'null pts':>10}{'delta $':>10}"
       f"{'CI95 $ lo':>11}{'hi':>9}{'p_raw':>8}{'p_corr':>8}{'p_spec':>8}"
       f"{'P':>3}{'C':>3}{'N':>3}{'LEAD':>6}")
for ev in ("E1", "E2", "E3", "E4", "E5", "E6"):
    say(f"---- {ev} " + "-" * 92)
    say(hdr)
    for r in [x for x in results if x["event"] == ev]:
        ps = r.get("p_release_specificity", np.nan)
        say(f"{r['cell']:<26}{r['n_events']:>5}{r['obs_mean_pts']:>10.4f}{r['null_mean_pts']:>10.4f}"
            f"{r['delta_ctrl_usd']:>10.1f}{r['delta_ci95_lo_usd']:>11.1f}{r['delta_ci95_hi_usd']:>9.1f}"
            f"{r['p_raw']:>8.4f}{r['p_corr']:>8.4f}"
            + (f"{ps:>8.4f}" if np.isfinite(ps) else f"{'--':>8}")
            + f"{'Y' if r['pass_p'] else '.':>3}{'Y' if r['pass_cost'] else '.':>3}"
            f"{'Y' if r['pass_n'] else '.':>3}{'LEAD' if r['LEAD'] else '--':>6}")
    say(f"  VERDICT {ev}: {verdicts[ev]}")
say("")

# ------------------------------------------------------- GATE table (program-printed)
gate_lines = []
def gate(gid, spec, obs, ok):
    gate_lines.append((gid, spec, obs, "PASS" if ok else "FAIL"))
gate("G0_SEAL", "max session <= 2026-07-31 (>=2026-08-01 VIRGIN untouched)",
     f"max session = {max_sess}", g0_pass)
gate("G1_BASIS", "POINTS basis only (DELEV01): point differences, no %/level thresholds; 1/32 grid",
     f"all stats are point diffs by construction; grid share(1/32)={g1_grid_share:.6f}",
     g1_grid_share > 0.999)
gate("G2_CALENDAR", "E1 calendar = the G2_F10/G2_F13 macro-flag set (NFP+CPI 08:30 files)",
     f"loaded {os.path.basename(NFP_CSV)} + {os.path.basename(CPI_CSV)}; "
     f"in-window union={len(rel_in_window)}; E1 usable events={len(ev1_pos)}",
     len(rel_in_window) > 0)
gate("G3_CONTROLS", "every conditional cell has a matched unconditional control in the same wave",
     f"cells={K}; control rows={len(ctrl_rows)} (per-horizon, time-matched; "
     f"null-mean is the matched center for every cell)", len(ctrl_rows) >= 12)
gate("G4_NULL", "circular-shift null, ONE shared draw across the family; label tuple travels",
     f"N_SHIFTS={N_SHIFTS}, seed={SEED}, offsets shared via one U(0,1) draw; "
     f"min attainable two-sided p={min_p:.5f}", True)
gate("G5_MULTIPLICITY", "print K and K_eff = K/(1+(K-1)rho_bar); screen at p_corr<0.05",
     f"K={K}, rho_bar={rho_bar:.4f}, K_eff={K_eff:.2f}, i.e. p_raw must be < {p_thresh:.5f}; "
     f"reachable={'YES' if min_p < p_thresh else 'NO (structurally underpowered)'}",
     True)
gate("G6_SCREEN", "LEAD iff p_corr<0.05 AND |delta|>=$133.72 (2x conservative ALL_IN) AND n>=30",
     f"applied to all {K} cells; LEAD cells={sum(r['LEAD'] for r in results)}", True)
gate("G7_VERDICTS", "per-event verdict DEAD/DESCRIPTIVE/LEAD per preregistered screen",
     "  ".join(f"{e}:{verdicts[e]}" for e in ("E1", "E2", "E3", "E4", "E5", "E6")), True)

say("=" * 100)
say(f"{'GATE':<16}{'SPEC':<62}{'PASS/FAIL':>10}")
say("-" * 100)
for gid, spec, obs, pf in gate_lines:
    say(f"{gid:<16}{spec:<62}{pf:>10}")
    say(f"{'':<16}OBSERVED: {obs}")
say("-" * 100)
n_lead = sum(1 for e in verdicts.values() if e == "LEAD")
n_desc = sum(1 for e in verdicts.values() if e == "DESCRIPTIVE")
n_dead = sum(1 for e in verdicts.values() if e == "DEAD")
say(f"CATALOG RESULT: {n_lead} LEAD / {n_desc} DESCRIPTIVE / {n_dead} DEAD "
    f"(LEAD graduates only via a separate preregistered falsifier spec)")
say("=" * 100)

with open(os.path.join(OUT, "gate_table.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(LINES) + "\n")
with open(os.path.join(OUT, "run_log.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(LINES) + "\n")
print("\nwrote out/event_tables.csv, out/controls.csv, out/gate_table.txt, out/run_log.txt")
