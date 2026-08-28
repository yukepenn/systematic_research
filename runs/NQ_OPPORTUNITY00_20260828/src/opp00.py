"""NQ_OPPORTUNITY00 -- LANE A state census.  DATA / STATE CAPABILITY ONLY.

Executes runs/NQ_OPPORTUNITY00_20260828/SPEC.md, committed at f62575f before this file produced a
number.  NO candidate P&L.  NO rule ranked by subsequent return.  NO threshold chosen from a forward
outcome.  NO model.  The only P&L that appears anywhere is the ALREADY-PUBLISHED economics of the
frozen incumbent, used to define the population and to anchor the frozen excursion threshold.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(RUN))
WE = os.path.join(ROOT, "research", "weekly_edge", "src")
sys.path.insert(0, WE)
sys.path.insert(0, os.path.join(ROOT, "research_sdk"))
from run_we_w17 import load_deep                                          # noqa: E402
from run_we_w19 import MEMBERS, QS                                        # noqa: E402
from run_we_w97 import votes                                              # noqa: E402
from we_fastctx import fast_build_context                                 # noqa: E402
import test_session_unit as TSU                                           # noqa: E402

OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
L13 = [6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]

# ---- FROZEN IN THE SPEC, BEFORE ANY MEASUREMENT ----------------------------------------
T_TICKS = 40                  # 40 ticks = 10.00 NQ points = $200, from the INCUMBENT's cost/edge
TICK = 0.25
PV = 20.0
AC1_SHARE = 0.40              # >= 40 % of flat sessions must reach ...
AC1_FRAC = 0.60               # ... >= 60 % of the MEDIAN ACTIVE session's realised range
AC4_MIN_SESSIONS = 85         # 8.0 % of 1,058
NEAR_BAND = 0.10              # "near the boundary" = within 10 % of the arming threshold

_fh = open(os.path.join(OUT, "opp00.txt"), "w", encoding="utf-8")
R = {}


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)


P("=" * 112)
P("=== NQ_OPPORTUNITY00 -- LANE A STATE CENSUS.  NO P&L, NO MODEL, NO RULE RANKED BY RETURN.")
P("=" * 112)

# ================================================================ 1. substrate + context
D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
n, tarr, sid, fb = D["n"], D["t"], D["sid"], D["fb"]
o, c, h, l = D["o"], D["c"], D["h"], D["l"]
NSESS = D["n_sess"]
st_ = np.flatnonzero(fb)
sess_first = tarr[st_]
win = (sess_first >= A) & (sess_first < B)
sess_in = np.flatnonzero(win)
assert tarr.max() < np.datetime64("2026-08-01"), "SEAL VIOLATION"
P(f"    bars {n:,}   sessions {NSESS:,}   in-window sessions {len(sess_in):,}   "
  f"max bar {pd.Timestamp(tarr.max())}")

z = np.load(os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out", "mem_ext.npz"))
mem, bmom, tilt = z["mem"], z["bmom"], z["tilt"]
X = fast_build_context(D)

# ================================================================ 2. decompose the arming identity
P("")
P("--- A1  THE ARMING IDENTITY, DECOMPOSED  ->  K * g * (1+dL) >= 16")
sess_end = D["sess_end"]
blocked = tarr >= sess_end[sid] - np.timedelta64(30 * 60, "s")
flatm = tarr >= sess_end[sid] - np.timedelta64(21 * 60, "s")
idx = {v: k for k, v in enumerate(L13)}


def ra(x):
    return np.where(x >= 0, np.floor(x + 0.5), np.ceil(x - 0.5))


def hyst(M):
    tg = np.zeros(n, np.int8)
    for i in range(n):
        p = 0 if (i == 0 or fb[i]) else tg[i - 1]
        g = p
        if flatm[i]:
            g = 0
        elif p == 0:
            if not blocked[i]:
                g = 1 if M[i] >= 3.0 else (-1 if M[i] <= -3.0 else p)
        elif p > 0:
            g = -1 if (M[i] <= -3.0 and not blocked[i]) else (0 if M[i] <= 1.0 else p)
        else:
            g = 1 if (M[i] >= 3.0 and not blocked[i]) else (0 if M[i] >= -1.0 else p)
        tg[i] = g
    return tg


TG, MM = {}, {}
for name, vols in MEMBERS.items():
    cols = [idx[v] for v in vols]
    s_ = mem[:, cols].sum(axis=1).astype(np.int32)
    T_ = np.clip(ra(s_ / float(len(cols)) * 10.0), -10, 10)
    ag = (np.sign(s_) == tilt) & (s_ != 0) & (tilt != 0)
    Tp = np.clip(ra(T_ * np.where(ag, 1.25, 1.0) * 0.9026), -13, 13)
    M_ = 0.7086 * Tp + 2.83 * bmom.astype(float)
    MM[name] = M_
    TG[name] = hyst(M_)

K = np.zeros(n, np.int8)
for m_ in MEMBERS:
    K += (TG[m_] > 0).astype(np.int8)
g = np.zeros(n, np.int8)
for q in QS:
    okv = np.ones(n, bool) if q is None else ((X["norm"] <= 0) | (X["ratio"] >= q))
    g += okv.astype(np.int8)
dL = X["dL"].astype(np.int8)
prod = K.astype(np.int32) * g.astype(np.int32) * (1 + dL.astype(np.int32))
armed = prod >= 16

# ---- PARITY: the decomposition must reproduce the frozen votes() EXACTLY
vl, vs_ = votes(D, mem, bmom, tilt, X, bmom)
disagree = int((armed != vl).sum())
P(f"    decomposition vs frozen votes(): disagreements {disagree:,} of {n:,}   "
  f"{'PASS - identity reproduced EXACTLY' if disagree == 0 else '*** FAIL ***'}")
assert disagree == 0, "the K*g*(1+dL) decomposition does not reproduce votes()"
P(f"    long armed on {int(vl.sum()):,} bars ({vl.mean():.2%})   "
  f"short leg armed on {int(vs_.sum()):,} bars ({vs_.mean():.2%})   "
  f"overlap {int((vl & vs_).sum())}")
R["parity_disagreements"] = disagree

# ================================================================ 3. population
P("")
P("--- A0  POPULATION  (session_id, never session_date)")
led = pd.read_csv(os.path.join(ROOT, "runs", "RR_W001_ACTION_VALUE_LEDGER", "out",
                               "ledger_p1pct.csv"))
w = led[led["in_window_session"] == True]                                 # noqa: E712
book = pd.read_csv(os.path.join(ROOT, "runs", "WE_W119_BOOKLOSS", "out",
                                "book_loss_ledger.csv"))
rate = TSU.per_session_rate(w, total_sessions=1058, label="P1/PCT in-window")
active_ids = set(w["session_id"].astype(int))
all_ids = set(book["session"].astype(int))
flat_ids = all_ids - active_ids
assert len(all_ids) == 1058 and len(active_ids) == 638 and len(flat_ids) == 420
assert active_ids <= all_ids
assert int((book["p1_pnl"] != 0).sum()) == 638
P(f"    total {len(all_ids):,}   active {len(active_ids):,}   FLAT {len(flat_ids):,} "
  f"= {len(flat_ids)/len(all_ids):.1%}   (independently cross-checked on book p1_pnl != 0)")
P(f"    session-unit guard: {rate}")
R["population"] = dict(total=1058, active=638, flat=420)

# ---- map book session ids onto substrate session indices
sess_idx_of = {}
for k_, s_i in enumerate(sess_in):
    sess_idx_of[int(s_i)] = k_
inwin_ids = sorted(all_ids)
overlap = sorted(set(int(x) for x in sess_in) & all_ids)
P(f"    substrate in-window session indices {len(sess_in):,}; "
  f"intersect with ledger session ids: {len(overlap):,}")

# ================================================================ 4. per-session state
P("")
P("--- A1/A2/A3/A4  PER-SESSION STATE  (descriptive; no returns anywhere)")
starts = np.flatnonzero(fb)
ends = np.append(starts[1:], n)
rows = []
for si in range(NSESS):
    a_, b_ = starts[si], ends[si]
    if not (A <= tarr[a_] < B):
        continue
    sl = slice(a_, b_)
    hi, lo = float(h[sl].max()), float(l[sl].min())
    cl = c[sl]
    rng_pts = hi - lo
    # directional-change count at the FROZEN threshold (path geometry, not an oracle)
    # Directional-change count at the frozen threshold. NOTE: the mode==0 startup state must
    # track BOTH extremes, and must be handled separately -- a single shared `ext` there tracks
    # in whichever direction price moves and can therefore NEVER register a reversal. That defect
    # returned dc==0 for every session in the first run; caught because a 264-point session cannot
    # contain zero 10-point reversals.
    th = T_TICKS * TICK
    dc, mode = 0, 0
    mx = mn = ext = float(cl[0])
    for x in cl:
        x = float(x)
        if mode == 0:
            mx, mn = max(mx, x), min(mn, x)
            if x <= mx - th:
                dc += 1; mode = -1; ext = x
            elif x >= mn + th:
                dc += 1; mode = +1; ext = x
        elif mode > 0:
            if x > ext:
                ext = x
            elif x <= ext - th:
                dc += 1; mode = -1; ext = x
        else:
            if x < ext:
                ext = x
            elif x >= ext + th:
                dc += 1; mode = +1; ext = x
    rows.append(dict(
        sid=int(si), date=str(pd.Timestamp(tarr[a_]).date()), bars=int(b_ - a_),
        K_max=int(K[sl].max()), g_max=int(g[sl].max()), dL_max=int(dL[sl].max()),
        prod_max=int(prod[sl].max()), vote_max=float(prod[sl].max() / 16.0),
        M_max=float(max(MM[m_][sl].max() for m_ in MEMBERS)),
        armed_bars=int(armed[sl].sum()),
        short_armed_bars=int(vs_[sl].sum()),
        range_pts=rng_pts, range_usd=rng_pts * PV,
        path_pts=float(np.abs(np.diff(cl)).sum()),
        rv_pts=float(np.sqrt((np.diff(cl) ** 2).sum())),
        dc40=int(dc)))
S = pd.DataFrame(rows)
S["is_active"] = S["sid"].isin(active_ids)
S["is_flat"] = ~S["is_active"]
P(f"    per-session rows {len(S):,}   active {int(S.is_active.sum()):,}   "
  f"flat {int(S.is_flat.sum()):,}")
assert int(S.is_active.sum()) == 638 and int(S.is_flat.sum()) == 420, \
    "session mapping mismatch between substrate and ledger"

# ================================================================ 5. cause decomposition
P("")
P("--- A1  P1_FLAT_CAUSE_DECOMPOSITION  (mutually exclusive, fixed precedence)")
F = S[S.is_flat].copy()


def cause(r):
    if r["K_max"] == 0:
        return "1_K0_no_member_ever_long"
    if r["K_max"] == 1:
        return "2_K1_max_vote_0.25"
    if r["g_max"] == 1:
        return "3_throttle_wall"
    if r["K_max"] >= 2 and r["g_max"] >= 2:
        return "4_NEAR_product_never_reached_16"
    return "5_OTHER"


F["cause"] = F.apply(cause, axis=1)
cc = F["cause"].value_counts().sort_index()
P(f"      {'cause':<36}{'sessions':>10}{'share of 420':>14}{'median range $':>16}")
for k_, v in cc.items():
    sub = F[F.cause == k_]
    P(f"      {k_:<36}{v:>10}{v/420:>14.1%}{sub['range_usd'].median():>16,.0f}")
assert int(cc.sum()) == 420
P("")
P(f"    sessions where the SHORT leg was armed but P1 is flat: "
  f"{int((F['short_armed_bars'] > 0).sum())} of 420 "
  f"= {(F['short_armed_bars'] > 0).mean():.1%}")
P("      ^ already FALSIFIED five times (W38/39/61/75/78); builds NETFUSE_1, listed DEAD/FALSIFIED.")
P("        Recorded, NOT a lane.")
F.to_csv(os.path.join(OUT, "P1_FLAT_CAUSE_DECOMPOSITION.csv"), index=False)
R["cause_counts"] = {k_: int(v) for k_, v in cc.items()}
R["flat_with_short_armed"] = int((F["short_armed_bars"] > 0).sum())

# ================================================================ 6. arming distance
P("")
P("--- A2  ARMING DISTANCE  (frozen definitions; no alternative compared, none picked by return)")
AC = S[S.is_active]
P(f"      {'':<26}{'FLAT (420)':>16}{'ACTIVE (638)':>16}")
for lbl, col in (("vote_max (1.0 = armed)", "vote_max"), ("M_max (threshold 3.0)", "M_max"),
                 ("K_max", "K_max"), ("g_max", "g_max")):
    P(f"      {lbl:<26}{F[col].median():>16.3f}{AC[col].median():>16.3f}")
near = F[F["vote_max"] >= (1.0 - NEAR_BAND)]
P(f"    flat sessions within {NEAR_BAND:.0%} of the arming boundary: {len(near)} "
  f"= {len(near)/420:.1%}")
P(f"    flat sessions that NEVER reached M >= 3.0 on any member set: "
  f"{int((F['M_max'] < 3.0).sum())} = {(F['M_max'] < 3.0).mean():.1%}")
R["near_boundary_flat"] = int(len(near))
R["flat_never_M3"] = int((F["M_max"] < 3.0).sum())

# ================================================================ 7. movement capacity
P("")
P("--- A3/A4  MOVEMENT CAPACITY  (outcome-independent path geometry only)")
med_active_range = float(AC["range_pts"].median())
bar_ = AC1_FRAC * med_active_range
P(f"    median ACTIVE-session realised range   {med_active_range:.2f} pts "
  f"(${med_active_range*PV:,.0f})")
P(f"    A-C1 bar = {AC1_FRAC:.0%} of it          {bar_:.2f} pts (${bar_*PV:,.0f})")
P("")
P(f"      {'statistic':<30}{'FLAT median':>16}{'ACTIVE median':>16}{'ratio':>10}")
for lbl, col in (("realised range (pts)", "range_pts"), ("path length (pts)", "path_pts"),
                 ("realised variation (pts)", "rv_pts"),
                 (f"{T_TICKS}-tick DC count", "dc40"), ("bars", "bars")):
    fm, am = float(F[col].median()), float(AC[col].median())
    P(f"      {lbl:<30}{fm:>16.2f}{am:>16.2f}{(fm/am if am else np.nan):>10.2f}")
share = float((F["range_pts"] >= bar_).mean())
P("")
P(f"    >>> A-C1: share of FLAT sessions reaching the bar = {share:.1%}   "
  f"required >= {AC1_SHARE:.0%}   {'PASS' if share >= AC1_SHARE else '*** FAIL ***'}")
P(f"    flat sessions with >= 1  {T_TICKS}-tick directional change: "
  f"{int((F['dc40'] >= 1).sum())} = {(F['dc40'] >= 1).mean():.1%}")
P(f"    flat sessions with >= 3  {T_TICKS}-tick directional changes: "
  f"{int((F['dc40'] >= 3).sum())} = {(F['dc40'] >= 3).mean():.1%}")
R["movement"] = dict(median_active_range_pts=med_active_range, ac1_bar_pts=bar_,
                     flat_share_reaching_bar=share,
                     flat_median_range=float(F["range_pts"].median()),
                     active_median_range=float(AC["range_pts"].median()),
                     flat_dc_ge1=float((F["dc40"] >= 1).mean()),
                     flat_dc_ge3=float((F["dc40"] >= 3).mean()))

# ================================================================ 8. continuation gates
P("")
P("=" * 112)
P("=== LANE A CONTINUATION GATES  (frozen in SPEC f62575f before this measurement)")
P("=" * 112)
ac1 = share >= AC1_SHARE
G = [("A-C1  >=40% of flat sessions reach >=60% of median active range",
      f"{share:.1%}", ac1),
     ("A-C2  a state family that is NOT threshold-loosening AND NOT the falsified short leg",
      "see below", None),
     ("A-C3  computable causally from certified fields", "yes (K,g,dL,path)", True),
     ("A-C4  occurs on >= 85 of 1,058 sessions", "see A-C2", None),
     ("A-C5  a distinct mechanism stateable before seeing returns", "see A-C2", None)]
P(f"    {'GATE':<74}{'OBSERVED':>14}   VERDICT")
for nm, ob, ok in G:
    P(f"    {nm:<74}{ob:>14}   "
      f"{'PASS' if ok is True else ('*** FAIL ***' if ok is False else 'ADJUDICATE')}")
json.dump(R, open(os.path.join(OUT, "opp00.json"), "w", encoding="utf-8"), indent=2, default=str)
S.to_csv(os.path.join(OUT, "session_state_census.csv"), index=False)
P("")
P("    NO candidate P&L, no model, no rule ranked by subsequent return was computed.")
_fh.close()
