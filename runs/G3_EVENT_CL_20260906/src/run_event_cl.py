"""
G3_EVENT_CL_20260906 -- CL native EVENT diagnostic (ledger G00068, family GENESIS3_EVENT).

DIAGNOSTIC / DISCOVERY. Event -> conditional-forward-path tables with matched unconditional
controls. NO strategy object is tested. Verdict per event: DEAD / DESCRIPTIVE / LEAD.

Contract implemented EXACTLY from runs/G3_EVENT_CL_20260906/spec.yaml (committed before results):
  E1 EIA response path   : EIA Wed 10:30 ET (holiday weeks -> Thu); sign x size-tercile of the
                           10:30->10:45 move; horizons 10:45->12:00, 10:45->14:30.
  E2 settlement transition: sign x size-tercile of 14:00->14:30 drift; horizons 14:30->17:00,
                           next-session 09:00->10:30.
  E3 overnight-pit handoff: |18:00->09:00| >= {1.5,2.0} x trailing-20 overnight sigma; by sign;
                           horizons 09:00->10:30, 09:00->14:30.
  E4 shock-day next path : |session net| >= 2.5 x trailing-20 daily sigma; close-location-in-range
                           tercile (fixed thirds); horizons next 1/2/3 sessions.
  E5 compression break   : (as ZB E3) trailing-5-session range in bottom quintile of trailing-60
                           AND session breaches prior 5-session high/low; break-day remainder
                           (from first breach bar) + next session; by breach direction.
  E6 multisession extreme: close breaches trailing-20-session high/low; next 1/2/3 sessions.
  E7 expansion failure   : session range >= 2 x trailing-20 median range AND |net| <= 25% of
                           range; next session.

Method: matched unconditional control per cell (time-matched where time-locked); session-block
bootstrap CIs (shared draws, circular blocks L=10, B=1000); circular-shift null for the LEAD
screen (EXHAUSTIVE shared offset set, one draw for the whole family); K_eff = K/(1+(K-1)*rhobar)
printed; LEAD screen = K_eff-corrected p<0.05 AND |delta$| >= 2x conservative all-in cost AND
n >= 30.

Basis: POINTS ONLY (additively back-adjusted substrate, DELEV01). Gate G4 proves translation
invariance of the whole pipeline by recomputing every cell with all prices shifted +1000.0.

Cost basis tag: MODELED / ALL_IN = commission $4.36 RT + modeled spread {1,2,3} ticks x $10.
Conservative all-in = $34.36 RT; screen threshold 2x = $68.72 = 0.06872 pts. Evidence: DISCOVERY.

UNITS: all internal price arithmetic is on the exact $0.01 CENT grid (integer cent values held in
float64; the substrate build proved 100.000% of prices on-grid). Differences of exact integers are
exact, so the G4 translation-invariance gate is EXACT (a first draft on raw float prices FAILED G4
via boundary-tie flips of ~1 ulp; cents remove the failure mode rather than papering over it with
a tolerance). Points = cents/100 at output only.
"""
import hashlib
import io
import sys
import os
from dataclasses import dataclass, field
from datetime import date, timedelta

import numpy as np
import pandas as pd

RUN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(RUN_DIR, "out")
os.makedirs(OUT_DIR, exist_ok=True)
REPO = os.path.dirname(os.path.dirname(RUN_DIR))
PARQUET = os.path.join(os.path.dirname(RUN_DIR), "SM1M_CL_SUBSTRATE", "out", "cl_1m_2022_2026.parquet")

SPEC_SHA256 = "e587486c23f5b61184b6a49aaeebc77f1a3e74e0731d8d0f4192087587adc137"
SPEC_SESSIONS = 1182
SEAL_DATE = date(2026, 8, 1)          # sessions must be < this
COMMISSION_RT = 4.36                   # $ per contract round trip (MODELED, Lifetime template)
TICK_USD = 10.0                        # CL $0.01 tick = $10
POINT_USD = 1000.0                     # CL 1.00 point = $1000
SPREAD_RUNGS_TICKS = [1, 2, 3]         # modeled spread band per RT
COST_ALLIN = [COMMISSION_RT + s * TICK_USD for s in SPREAD_RUNGS_TICKS]   # 14.36 / 24.36 / 34.36
COST_CONSERVATIVE = COST_ALLIN[-1]     # $34.36
SCREEN_USD = 2.0 * COST_CONSERVATIVE   # $68.72
SCREEN_CENTS = SCREEN_USD / TICK_USD   # 6.872 cents (1 cent = 1 tick = $10)
MIN_EVENTS_LEAD = 30
B_BOOT = 1000
BLOCK_L = 10
SEED = 20260906
STALE_MIN = 30                         # anchor price staleness tolerance (minutes)

# anchor minutes-from-session-date-midnight (evening bars are negative)
A0900, A1030, A1045, A1200, A1400, A1430 = 540, 630, 645, 720, 840, 870

TEE = io.StringIO()
def P(*args):
    s = " ".join(str(a) for a in args)
    print(s)
    TEE.write(s + "\n")

# ----------------------------------------------------------------------------------------------
# EIA calendar: Wednesdays 10:30 ET; if a federal holiday (observed) falls Mon/Tue/Wed of the
# week, the release shifts to Thursday (same 10:30 anchor per spec E1 -- see anomalies note).
# ----------------------------------------------------------------------------------------------
def _observed(d: date) -> date:
    if d.weekday() == 5:   # Sat -> Fri
        return d - timedelta(days=1)
    if d.weekday() == 6:   # Sun -> Mon
        return d + timedelta(days=1)
    return d

def _nth_weekday(y, m, weekday, n):
    d1 = date(y, m, 1)
    first = d1 + timedelta(days=(weekday - d1.weekday()) % 7)
    return first + timedelta(days=7 * (n - 1))

def _last_weekday(y, m, weekday):
    if m == 12:
        dl = date(y, 12, 31)
    else:
        dl = date(y, m + 1, 1) - timedelta(days=1)
    return dl - timedelta(days=(dl.weekday() - weekday) % 7)

def federal_holidays(years):
    hol = set()
    for y in years:
        hol.add(_observed(date(y, 1, 1)))               # New Year's Day
        hol.add(_nth_weekday(y, 1, 0, 3))               # MLK: 3rd Mon Jan
        hol.add(_nth_weekday(y, 2, 0, 3))               # Washington's Birthday: 3rd Mon Feb
        hol.add(_last_weekday(y, 5, 0))                 # Memorial Day: last Mon May
        hol.add(_observed(date(y, 6, 19)))              # Juneteenth (federal since 2021)
        hol.add(_observed(date(y, 7, 4)))               # Independence Day
        hol.add(_nth_weekday(y, 9, 0, 1))               # Labor Day: 1st Mon Sep
        hol.add(_nth_weekday(y, 10, 0, 2))              # Columbus Day: 2nd Mon Oct
        hol.add(_observed(date(y, 11, 11)))             # Veterans Day
        hol.add(_nth_weekday(y, 11, 3, 4))              # Thanksgiving: 4th Thu Nov
        hol.add(_observed(date(y, 12, 25)))             # Christmas
    return hol

def eia_calendar(first_session: date, last_session: date):
    hol = federal_holidays(range(first_session.year - 1, last_session.year + 2))
    releases, shifted = [], []
    w = first_session - timedelta(days=first_session.weekday())   # Monday of first week
    while w <= last_session:
        week_mtw = {w, w + timedelta(days=1), w + timedelta(days=2)}
        if week_mtw & hol:
            rel = w + timedelta(days=3)   # Thursday
            shifted.append(rel)
        else:
            rel = w + timedelta(days=2)   # Wednesday
        if first_session <= rel <= last_session:
            releases.append(rel)
        w += timedelta(days=7)
    return releases, shifted

# ----------------------------------------------------------------------------------------------
# Session-array build (parametrized by a price translation to prove POINTS-basis invariance, G4)
# ----------------------------------------------------------------------------------------------
def build_arrays(df, price_offset_cents=0.0):
    t = df["time"]
    h = t.dt.hour.to_numpy()
    m = t.dt.minute.to_numpy()
    evening = h >= 18
    mins = h * 60 + m - evening.astype(np.int64) * 1440         # 18:01 -> -359 ... 17:00 -> 1020
    sess_date = (t.dt.normalize() + pd.to_timedelta(evening.astype(np.int64), unit="D")).dt.date.to_numpy()

    codes, uniques = pd.factorize(sess_date, sort=False)
    assert (np.diff(codes) >= 0).all(), "session codes must be non-decreasing in time order"
    u = np.array(uniques)
    assert all(u[i] < u[i + 1] for i in range(len(u) - 1)), "session dates strictly increasing"
    N = len(u)

    # exact $0.01 grid: integer cent values held in float64 (exact); translation is exact
    def cents(col):
        raw = df[col].to_numpy() * 100.0
        snapped = np.round(raw)
        assert np.max(np.abs(raw - snapped)) < 1e-6 * 100, f"{col} off the 0.01 grid"
        return snapped + price_offset_cents

    opens = cents("open")
    highs = cents("high")
    lows = cents("low")
    closes = cents("close")

    starts = np.searchsorted(codes, np.arange(N), side="left")
    ends = np.append(starts[1:], len(codes)) - 1

    A = {}
    A["N"] = N
    A["dates"] = u
    A["open18"] = opens[starts]
    A["close"] = closes[ends]
    A["high"] = np.maximum.reduceat(highs, starts)
    A["low"] = np.minimum.reduceat(lows, starts)
    A["net"] = A["close"] - A["open18"]
    A["range"] = A["high"] - A["low"]
    A["starts"], A["ends"] = starts, ends
    A["bar_mins"], A["bar_codes"] = mins, codes
    A["bar_high"], A["bar_low"], A["bar_close"] = highs, lows, closes

    key = codes.astype(np.int64) * 3000 + (mins + 1000)
    assert (np.diff(key) > 0).all(), "bar key must be strictly increasing"
    A["_key"] = key

    def price_at(anchor_min):
        qs = np.arange(N, dtype=np.int64) * 3000 + (anchor_min + 1000)
        pos = np.searchsorted(key, qs, side="right") - 1
        posc = np.clip(pos, 0, len(key) - 1)
        ok = (pos >= 0) & (key[posc] >= qs - STALE_MIN) & (key[posc] <= qs)
        out = np.where(ok, closes[posc], np.nan)
        return out
    A["price_at"] = price_at

    for name, am in [("p0900", A0900), ("p1030", A1030), ("p1045", A1045),
                     ("p1200", A1200), ("p1400", A1400), ("p1430", A1430)]:
        A[name] = price_at(am)
    return A

# ----------------------------------------------------------------------------------------------
# Cells
# ----------------------------------------------------------------------------------------------
@dataclass
class Cell:
    cid: str
    event: str
    cond: str
    horizon: str
    ev_idx: np.ndarray        # session indices of events
    e_arr: np.ndarray         # length-N: event outcome at event sessions, NaN elsewhere
    c_arr: np.ndarray         # length-N: matched-control outcome (NaN = invalid/ineligible)
    Q: np.ndarray = None      # (n_ev x N) event-time-specific outcomes (E5 remainder only)
    control_desc: str = ""

def roll_prior(x, w, fn, minp=None):
    s = pd.Series(x)
    r = getattr(s.rolling(w, min_periods=(minp or w)), fn)()
    return r.shift(1).to_numpy()

def tercile_of_abs(vals, mask):
    """empirical terciles of |vals| within mask; returns labels 1/2/3 (0 outside mask/invalid)"""
    lab = np.zeros(len(vals), dtype=int)
    v = np.abs(vals)
    sel = mask & np.isfinite(v)
    if sel.sum() < 3:
        return lab
    q1, q2 = np.nanpercentile(v[sel], [100 / 3, 200 / 3])
    lab[sel & (v <= q1)] = 1
    lab[sel & (v > q1) & (v <= q2)] = 2
    lab[sel & (v > q2)] = 3
    return lab

def build_cells(A, eia_idx):
    N = A["N"]
    cells = []
    notes = {}

    def evarr(idx, outcome):
        e = np.full(N, np.nan)
        e[idx] = outcome[idx]
        return e

    # windows (POINT differences only)
    m_1030_1045 = A["p1045"] - A["p1030"]
    m_1045_1200 = A["p1200"] - A["p1045"]
    m_1045_1430 = A["p1430"] - A["p1045"]
    m_1400_1430 = A["p1430"] - A["p1400"]
    m_1430_close = A["close"] - A["p1430"]
    m_0900_1030 = A["p1030"] - A["p0900"]
    m_0900_1430 = A["p1430"] - A["p0900"]
    ov = A["p0900"] - A["open18"]
    nxt = {}
    for hh in (1, 2, 3):
        arr = np.full(N, np.nan)
        arr[: N - hh] = A["close"][hh:] - A["close"][: N - hh]
        nxt[hh] = arr
    next_0900_1030 = np.append(m_0900_1030[1:], np.nan)

    # ---- E1: EIA response path -------------------------------------------------------------
    eia_mask = np.zeros(N, dtype=bool)
    eia_mask[eia_idx] = True
    e1_valid = eia_mask & np.isfinite(m_1030_1045)
    sgn = np.sign(m_1030_1045)
    ter = tercile_of_abs(m_1030_1045, e1_valid)
    notes["E1_zero_move"] = int((e1_valid & (sgn == 0)).sum())
    for s_lab, s_val in [("up", 1), ("dn", -1)]:
        for tv in (1, 2, 3):
            sel = e1_valid & (sgn == s_val) & (ter == tv)
            idx = np.where(sel)[0]
            for h_lab, h_arr in [("1045-1200", m_1045_1200), ("1045-1430", m_1045_1430)]:
                cells.append(Cell(
                    cid=f"E1_{s_lab}_t{tv}_{h_lab}", event="E1_eia_response_path",
                    cond=f"EIA day; 10:30->10:45 {s_lab}, |move| tercile {tv}",
                    horizon=h_lab, ev_idx=idx, e_arr=evarr(idx, h_arr), c_arr=h_arr.copy(),
                    control_desc=f"unconditional {h_lab} move, all sessions (time-matched)"))

    # ---- E2: settlement transition (all sessions, sign x tercile of 14:00->14:30) ----------
    e2_valid = np.isfinite(m_1400_1430)
    sgn2 = np.sign(m_1400_1430)
    ter2 = tercile_of_abs(m_1400_1430, e2_valid)
    notes["E2_zero_move"] = int((e2_valid & (sgn2 == 0)).sum())
    for s_lab, s_val in [("up", 1), ("dn", -1)]:
        for tv in (1, 2, 3):
            sel = e2_valid & (sgn2 == s_val) & (ter2 == tv)
            idx = np.where(sel)[0]
            for h_lab, h_arr in [("1430-close", m_1430_close), ("next0900-1030", next_0900_1030)]:
                cells.append(Cell(
                    cid=f"E2_{s_lab}_t{tv}_{h_lab}", event="E2_settlement_transition",
                    cond=f"14:00->14:30 drift {s_lab}, |drift| tercile {tv}",
                    horizon=h_lab, ev_idx=idx, e_arr=evarr(idx, h_arr), c_arr=h_arr.copy(),
                    control_desc=f"unconditional {h_lab} move, all sessions (time-matched)"))

    # ---- E3: overnight -> pit handoff ------------------------------------------------------
    sig_ov = roll_prior(ov, 20, "std", minp=15)
    e3_elig = np.isfinite(ov) & np.isfinite(sig_ov)
    for k in (1.5, 2.0):
        for s_lab, s_val in [("up", 1), ("dn", -1)]:
            sel = e3_elig & (np.abs(ov) >= k * sig_ov) & (np.sign(ov) == s_val)
            idx = np.where(sel)[0]
            for h_lab, h_arr in [("0900-1030", m_0900_1030), ("0900-1430", m_0900_1430)]:
                c = np.where(e3_elig, h_arr, np.nan)
                cells.append(Cell(
                    cid=f"E3_{k}x_{s_lab}_{h_lab}", event="E3_overnight_pit_handoff",
                    cond=f"|18:00->09:00| >= {k} x trail-20 overnight sigma, gap {s_lab}",
                    horizon=h_lab, ev_idx=idx, e_arr=evarr(idx, c), c_arr=c,
                    control_desc=f"unconditional {h_lab} move, eligible sessions (time-matched)"))

    # ---- E4: shock day next path -----------------------------------------------------------
    sig_net = roll_prior(A["net"], 20, "std")
    e4_elig = np.isfinite(sig_net)
    shock = e4_elig & (np.abs(A["net"]) >= 2.5 * sig_net) & (A["range"] > 0)
    closeloc = np.where(A["range"] > 0, (A["close"] - A["low"]) / A["range"], np.nan)
    loclab = np.where(closeloc < 1 / 3, 1, np.where(closeloc > 2 / 3, 3, 2))  # 1=bottom 2=mid 3=top
    for l_lab, l_val in [("bottom", 1), ("mid", 2), ("top", 3)]:
        sel = shock & (loclab == l_val)
        idx = np.where(sel)[0]
        for hh in (1, 2, 3):
            c = np.where(e4_elig, nxt[hh], np.nan)
            cells.append(Cell(
                cid=f"E4_{l_lab}_next{hh}", event="E4_shock_day_next_path",
                cond=f"|net| >= 2.5 x trail-20 sigma, close-location {l_lab} third",
                horizon=f"next{hh}", ev_idx=idx, e_arr=evarr(idx, c), c_arr=c,
                control_desc=f"unconditional next-{hh}-session net, eligible sessions"))

    # ---- E5: compression break (as ZB E3) --------------------------------------------------
    h5 = roll_prior(A["high"], 5, "max")
    l5 = roll_prior(A["low"], 5, "min")
    r5 = h5 - l5
    q20 = pd.Series(r5).rolling(60).quantile(0.20).shift(1).to_numpy()
    e5_elig = np.isfinite(r5) & np.isfinite(q20)
    compressed = e5_elig & (r5 <= q20)
    up_evs, dn_evs = [], []   # (session_idx, breach_min, remainder)
    ties = 0
    for s in np.where(compressed)[0]:
        sl = slice(A["starts"][s], A["ends"][s] + 1)
        bh, bl, bm = A["bar_high"][sl], A["bar_low"][sl], A["bar_mins"][sl]
        iu = np.argmax(bh > h5[s]) if (bh > h5[s]).any() else -1
        idn = np.argmax(bl < l5[s]) if (bl < l5[s]).any() else -1
        if iu < 0 and idn < 0:
            continue
        if iu >= 0 and idn >= 0 and iu == idn:
            ties += 1
            continue
        if iu >= 0 and (idn < 0 or iu < idn):
            up_evs.append((s, int(bm[iu])))
        else:
            dn_evs.append((s, int(bm[idn])))
    notes["E5_same_bar_tie_excluded"] = ties
    notes["E5_compressed_sessions"] = int(compressed.sum())

    def rem_cell(evs, d_lab):
        idx = np.array([s for s, _ in evs], dtype=int)
        tms = [t for _, t in evs]
        n_e = len(evs)
        Q = np.full((n_e, N), np.nan)
        uniq = {}
        for t in set(tms):
            uniq[t] = A["close"] - A["price_at"](t)          # close - price@t, per session
        for i, (s, t) in enumerate(evs):
            Q[i] = np.where(e5_elig, uniq[t], np.nan)
        e = np.full(N, np.nan)
        for i, (s, t) in enumerate(evs):
            e[s] = Q[i, s]
        if n_e > 0:
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                g = np.nanmean(Q, axis=0)          # time-dist-matched control
        else:
            g = np.full(N, np.nan)
        return Cell(
            cid=f"E5_{d_lab}brk_remainder", event="E5_compression_break",
            cond=f"compressed (trail-5 range <= q20 of trail-60) + {d_lab}-breach of prior-5 extreme",
            horizon="breach-bar->session close", ev_idx=idx, e_arr=e, c_arr=g, Q=Q,
            control_desc="close - price@t averaged over the event breach-time distribution, "
                         "eligible sessions (time-distribution-matched)")

    for evs, d_lab in [(up_evs, "up"), (dn_evs, "dn")]:
        cells.append(rem_cell(evs, d_lab))
        idx = np.array([s for s, _ in evs], dtype=int)
        c = np.where(e5_elig, nxt[1], np.nan)
        cells.append(Cell(
            cid=f"E5_{d_lab}brk_next1", event="E5_compression_break",
            cond=f"compressed + {d_lab}-breach of prior-5 extreme",
            horizon="next1", ev_idx=idx, e_arr=evarr(idx, c), c_arr=c,
            control_desc="unconditional next-1-session net, eligible sessions"))

    # ---- E6: multisession extreme ----------------------------------------------------------
    h20 = roll_prior(A["high"], 20, "max")
    l20 = roll_prior(A["low"], 20, "min")
    e6_elig = np.isfinite(h20) & np.isfinite(l20)
    for d_lab, sel in [("up", e6_elig & (A["close"] > h20)), ("dn", e6_elig & (A["close"] < l20))]:
        idx = np.where(sel)[0]
        for hh in (1, 2, 3):
            c = np.where(e6_elig, nxt[hh], np.nan)
            cells.append(Cell(
                cid=f"E6_{d_lab}_next{hh}", event="E6_multisession_extreme",
                cond=f"close breaches trailing-20-session {'high' if d_lab=='up' else 'low'}",
                horizon=f"next{hh}", ev_idx=idx, e_arr=evarr(idx, c), c_arr=c,
                control_desc=f"unconditional next-{hh}-session net, eligible sessions"))

    # ---- E7: expansion failure -------------------------------------------------------------
    med20 = roll_prior(A["range"], 20, "median")
    e7_elig = np.isfinite(med20) & (A["range"] > 0)
    sel = e7_elig & (A["range"] >= 2.0 * med20) & (np.abs(A["net"]) <= 0.25 * A["range"])
    idx = np.where(sel)[0]
    c = np.where(e7_elig, nxt[1], np.nan)
    cells.append(Cell(
        cid="E7_all_next1", event="E7_expansion_failure",
        cond="range >= 2 x trail-20 median range AND |net| <= 25% of range",
        horizon="next1", ev_idx=idx, e_arr=evarr(idx, c), c_arr=c,
        control_desc="unconditional next-1-session net, eligible sessions"))

    return cells, notes

# ----------------------------------------------------------------------------------------------
# Statistics
# ----------------------------------------------------------------------------------------------
def observed_delta(cell):
    ev = cell.e_arr[cell.ev_idx] if len(cell.ev_idx) else np.array([np.nan])
    n = int(np.isfinite(ev).sum())
    mean_ev = np.nanmean(ev) if n else np.nan
    ctl_n = int(np.isfinite(cell.c_arr).sum())
    mean_c = np.nanmean(cell.c_arr) if ctl_n else np.nan
    return n, mean_ev, ctl_n, mean_c, mean_ev - mean_c

def bootstrap_deltas(cell, IDX):
    E = cell.e_arr[IDX]     # (B,N)
    C = cell.c_arr[IDX]
    with np.errstate(invalid="ignore"):
        ne = np.isfinite(E).sum(axis=1)
        me = np.where(ne > 0, np.nansum(np.nan_to_num(E), axis=1) / np.maximum(ne, 1), np.nan)
        nc = np.isfinite(C).sum(axis=1)
        mc = np.where(nc > 0, np.nansum(np.nan_to_num(C), axis=1) / np.maximum(nc, 1), np.nan)
    return me - mc, int((ne == 0).sum())

def null_deltas(cell, offsets, N):
    if len(cell.ev_idx) == 0:
        return np.full(len(offsets), np.nan)
    ctl = np.nanmean(cell.c_arr)
    pos = (cell.ev_idx[:, None] + offsets[None, :]) % N          # (n_e, S)
    if cell.Q is not None:
        M = cell.Q[np.arange(len(cell.ev_idx))[:, None], pos]
    else:
        M = cell.c_arr[pos]
    with np.errstate(invalid="ignore", divide="ignore"):
        cnt = np.isfinite(M).sum(axis=0)
        mu = np.where(cnt > 0, np.nansum(np.nan_to_num(M), axis=0) / np.maximum(cnt, 1), np.nan)
    return mu - ctl

# ----------------------------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------------------------
def main():
    gates = []   # (gate, spec, observed, passfail)

    with open(PARQUET, "rb") as f:
        sha = hashlib.sha256(f.read()).hexdigest()
    df = pd.read_parquet(PARQUET)
    df = df.sort_values("time").reset_index(drop=True)

    A = build_arrays(df, 0.0)
    N = A["N"]
    dates = A["dates"]
    gates.append(("G1_DATA_SHA256", SPEC_SHA256[:16] + "...", sha[:16] + "...", sha == SPEC_SHA256))
    max_sess = dates[-1]
    gates.append(("G2_SEAL_MAX_SESSION", f"< {SEAL_DATE}", str(max_sess), max_sess < SEAL_DATE))
    assert max_sess < SEAL_DATE, "SEAL VIOLATION"
    gates.append(("G3_SESSION_COUNT", str(SPEC_SESSIONS), str(N), N == SPEC_SESSIONS))

    # EIA calendar
    releases, shifted = eia_calendar(dates[0], dates[-1])
    date_to_idx = {d: i for i, d in enumerate(dates)}
    eia_idx, eia_unmatched = [], []
    for r in releases:
        if r in date_to_idx:
            eia_idx.append(date_to_idx[r])
        else:
            eia_unmatched.append(r)
    eia_idx = np.array(sorted(eia_idx), dtype=int)
    shifted_in = [r for r in shifted if dates[0] <= r <= dates[-1]]
    seal_ok = all(r < SEAL_DATE for r in releases)
    gates.append(("G10_EIA_CAL_SEAL", "all release dates < 2026-08-01",
                  f"{len(releases)} dates, max {max(releases)}", seal_ok))

    cells, notes = build_cells(A, eia_idx)
    K = len(cells)
    gates.append(("G5_CELLS_REPORTED", "52 preregistered", f"{K} emitted", K == 52))

    # G4: POINTS-basis translation invariance (+1000.00 points = +100000 cents, full rebuild)
    A2 = build_arrays(df, 100000.0)
    cells2, _ = build_cells(A2, eia_idx)
    d0 = np.array([observed_delta(c)[4] for c in cells])
    d2 = np.array([observed_delta(c)[4] for c in cells2])
    ev_same = all(np.array_equal(a.ev_idx, b.ev_idx) for a, b in zip(cells, cells2))
    max_dev = np.nanmax(np.abs(d0 - d2))
    gates.append(("G4_POINTS_INVARIANCE", "event sets identical & max|d(delta)|=0 under +1000.00-pt price shift",
                  f"ev_same={ev_same}, max_dev={max_dev:.2e} cents", ev_same and max_dev == 0.0))

    # shared draws
    rng = np.random.default_rng(SEED)
    n_blocks = int(np.ceil(N / BLOCK_L))
    starts_mat = rng.integers(0, N, size=(B_BOOT, n_blocks))
    IDX = ((starts_mat[:, :, None] + np.arange(BLOCK_L)[None, None, :]) % N).reshape(B_BOOT, -1)[:, :N]
    offsets = np.arange(30, N - 30, dtype=int)                    # EXHAUSTIVE shared shift set
    S = len(offsets)

    rows = []
    NULLS = np.full((S, K), np.nan)
    for j, c in enumerate(cells):
        n, mean_ev, ctl_n, mean_c, delta = observed_delta(c)
        bd, degen = bootstrap_deltas(c, IDX)
        ci_lo, ci_hi = np.nanpercentile(bd, [2.5, 97.5])
        p_boot = 2 * min(np.nanmean(bd <= 0), np.nanmean(bd >= 0))
        p_boot = max(p_boot, 2.0 / (B_BOOT + 1))
        nd = null_deltas(c, offsets, N)
        NULLS[:, j] = nd
        p_raw = (1 + np.sum(np.abs(nd) >= abs(delta))) / (S + 1) if np.isfinite(delta) else np.nan
        rows.append(dict(cell=c.cid, event=c.event, condition=c.cond, horizon=c.horizon,
                         n_events=n, mean_pts=mean_ev / 100.0, control_n=ctl_n,
                         control_mean_pts=mean_c / 100.0,
                         delta_pts=delta / 100.0, delta_usd=delta * TICK_USD,
                         ci95_lo_pts=ci_lo / 100.0, ci95_hi_pts=ci_hi / 100.0,
                         degen_boot_draws=degen,
                         p_raw_shift=p_raw, p_boot=p_boot, control_desc=c.control_desc))

    # K_eff from shared null draws
    ok_rows = ~np.isnan(NULLS).any(axis=1)
    CM = np.corrcoef(NULLS[ok_rows].T)
    rhobar = float(np.mean(CM[np.triu_indices(K, 1)]))
    rhobar_c = max(0.0, rhobar)
    K_eff = K / (1 + (K - 1) * rhobar_c)
    p_thresh = 0.05 / K_eff
    gates.append(("G7_NULL_SHARED_DRAW", f"one exhaustive offset set for all {K} cells; K,K_eff printed",
                  f"S={S} offsets shared; K={K}, rhobar={rhobar:.4f}, K_eff={K_eff:.2f}", True))

    # LEAD screen
    tab = pd.DataFrame(rows)
    tab["abs_delta_usd"] = tab["delta_usd"].abs()
    tab["screen_p"] = tab["p_raw_shift"] < p_thresh
    tab["screen_cost"] = tab["abs_delta_usd"] >= SCREEN_USD
    tab["screen_n"] = tab["n_events"] >= MIN_EVENTS_LEAD
    tab["LEAD"] = tab["screen_p"] & tab["screen_cost"] & tab["screen_n"]

    # verdicts per event
    verdicts = {}
    for ev, g in tab.groupby("event"):
        if g["LEAD"].any():
            verdicts[ev] = "LEAD"
        elif g["screen_p"].any():
            verdicts[ev] = "DESCRIPTIVE"
        else:
            verdicts[ev] = "DEAD"

    gates.append(("G6_CONTROLS_MATCHED", "every cell has a matched control row",
                  f"{int(tab['control_n'].notna().sum())}/{K} control rows", int(tab["control_n"].notna().sum()) == K))

    # probability-meaning gates
    words = ("p_raw_shift is the probability, over the exhaustive shared set of "
             f"{S} circular session-shifts decoupling each event's conditioning from the outcome "
             "series, that the shifted conditional-mean-minus-control delta is >= the observed "
             "|delta| (two-sided). It is a per-cell alignment-null probability, NOT a P(profit) "
             "and NOT corrected for the family; the family correction is the printed "
             f"p < 0.05/K_eff = {p_thresh:.5f} threshold.")
    gates.append(("G8_PROB_MEANING_WORDS", "p-value event stated in words in output", "printed below", True))

    minp = tab.loc[tab["p_raw_shift"].idxmin()]
    lead_cells = tab[tab["LEAD"]]
    if len(lead_cells):
        second_ok = bool((lead_cells["p_boot"] < 0.05).all())
        obs9 = f"{len(lead_cells)} LEAD cells; all p_boot<0.05: {second_ok}"
    else:
        second_ok = True
        obs9 = (f"no LEAD; min-p cell {minp['cell']}: p_shift={minp['p_raw_shift']:.5f}, "
                f"p_boot(2nd way)={minp['p_boot']:.5f}")
    gates.append(("G9_PROB_SECOND_WAY", "LEAD p recomputed via block-bootstrap sign test agrees (<0.05)",
                  obs9, second_ok))
    gates.append(("G11_COST_CONSTANTS", "comm 4.36 + spread{1,2,3}x$10; conservative 34.36; screen 2x=68.72",
                  f"all-in band {COST_ALLIN}; screen {SCREEN_USD:.2f} USD = {SCREEN_USD/POINT_USD:.5f} pts",
                  abs(SCREEN_USD - 68.72) < 1e-9))
    gates.append(("G12_MIN_EVENTS_ENFORCED", f"every LEAD cell n>={MIN_EVENTS_LEAD}",
                  "vacuous (no LEAD)" if not len(lead_cells) else f"min n={int(lead_cells['n_events'].min())}",
                  bool((lead_cells["n_events"] >= MIN_EVENTS_LEAD).all()) if len(lead_cells) else True))

    # ---------------- outputs ----------------
    tab_out = tab.drop(columns=["control_desc"])
    tab_out.to_csv(os.path.join(OUT_DIR, "event_tables.csv"), index=False)
    tab[["cell", "event", "horizon", "control_n", "control_mean_pts", "control_desc"]].to_csv(
        os.path.join(OUT_DIR, "controls.csv"), index=False)

    P("=" * 110)
    P("G3_EVENT_CL_20260906 -- CL EVENT DIAGNOSTIC (ledger G00068)  [DISCOVERY; cost MODELED/ALL_IN]")
    P("=" * 110)
    P(f"substrate: {os.path.relpath(PARQUET, REPO)}  sessions={N}  {dates[0]} .. {dates[-1]}")
    P(f"EIA calendar: {len(releases)} releases ({len(eia_idx)} matched to sessions, "
      f"{len(eia_unmatched)} unmatched->dropped), {len(shifted_in)} holiday-shifted to Thursday")
    P(f"notes: {notes}")
    P("")
    P("PROBABILITY MEANING (gate G8): " + words)
    P("")
    P(f"family: K={K} cells, rhobar(null)={rhobar:.4f}, K_eff={K_eff:.2f}, "
      f"corrected screen threshold p < {p_thresh:.5f}; shift draws S={S} (exhaustive, shared); "
      f"bootstrap B={B_BOOT} block L={BLOCK_L} (shared); seed={SEED}")
    P(f"LEAD screen: p_raw < {p_thresh:.5f} AND |delta| >= ${SCREEN_USD:.2f} "
      f"({SCREEN_USD/POINT_USD:.5f} pts) AND n >= {MIN_EVENTS_LEAD}")
    P("")
    hdr = (f"{'cell':<26}{'n':>5}{'mean':>9}{'ctlmean':>9}{'delta':>9}{'d$':>8}"
           f"{'ci95lo':>9}{'ci95hi':>9}{'p_shift':>9}{'p_boot':>8}{'P':>2}{'C':>2}{'N':>2}{'LEAD':>6}")
    P(hdr)
    P("-" * len(hdr))
    for _, r in tab.iterrows():
        P(f"{r['cell']:<26}{r['n_events']:>5}{r['mean_pts']:>9.4f}{r['control_mean_pts']:>9.4f}"
          f"{r['delta_pts']:>9.4f}{r['delta_usd']:>8.0f}{r['ci95_lo_pts']:>9.4f}{r['ci95_hi_pts']:>9.4f}"
          f"{r['p_raw_shift']:>9.5f}{r['p_boot']:>8.4f}"
          f"{'Y' if r['screen_p'] else '.':>2}{'Y' if r['screen_cost'] else '.':>2}"
          f"{'Y' if r['screen_n'] else '.':>2}{'LEAD' if r['LEAD'] else '':>6}")
    P("")
    P("raw-p<0.05 cells (uncorrected, expected ~2.6 by chance): "
      f"{int((tab['p_raw_shift'] < 0.05).sum())}/{K}")
    P("")
    P("VERDICTS (DEAD = no cell clears K_eff-corrected p<0.05; DESCRIPTIVE = clears corrected p "
      "but fails cost/n legs; LEAD = full screen):")
    for ev in sorted(verdicts):
        g = tab[tab["event"] == ev]
        P(f"  {ev:<28} {verdicts[ev]:<12} (cells={len(g)}, min p_shift={g['p_raw_shift'].min():.5f}, "
          f"max |d$|={g['abs_delta_usd'].max():.0f}, n range {int(g['n_events'].min())}-{int(g['n_events'].max())})")
    P("")
    P("GATE TABLE (program-printed)")
    gt = f"{'GATE':<26}{'SPEC':<64}{'OBSERVED':<62}{'PASS-FAIL':<9}"
    P(gt)
    P("-" * len(gt))
    order = ["G1_DATA_SHA256", "G2_SEAL_MAX_SESSION", "G3_SESSION_COUNT", "G4_POINTS_INVARIANCE",
             "G5_CELLS_REPORTED", "G6_CONTROLS_MATCHED", "G7_NULL_SHARED_DRAW", "G8_PROB_MEANING_WORDS",
             "G9_PROB_SECOND_WAY", "G10_EIA_CAL_SEAL", "G11_COST_CONSTANTS", "G12_MIN_EVENTS_ENFORCED"]
    gd = {g[0]: g for g in gates}
    all_pass = True
    for k in order:
        g = gd[k]
        all_pass &= bool(g[3])
        P(f"{g[0]:<26}{str(g[1])[:62]:<64}{str(g[2])[:60]:<62}{'PASS' if g[3] else 'FAIL':<9}")
    P("-" * len(gt))
    P(f"ALL GATES: {'PASS' if all_pass else 'FAIL'}")

    with open(os.path.join(OUT_DIR, "gate_table.txt"), "w", encoding="utf-8") as f:
        f.write(TEE.getvalue())
    with open(os.path.join(OUT_DIR, "console.txt"), "w", encoding="utf-8") as f:
        f.write(TEE.getvalue())

    # machine-readable extras for the report
    import json
    extras = dict(K=K, rhobar=rhobar, K_eff=K_eff, p_thresh=p_thresh, S=S, B=B_BOOT,
                  n_sessions=N, eia_releases=len(releases), eia_matched=len(eia_idx),
                  eia_unmatched=[str(d) for d in eia_unmatched],
                  eia_shifted_thu=len(shifted_in), notes=notes,
                  verdicts=verdicts, all_gates_pass=bool(all_pass),
                  raw_sig=int((tab['p_raw_shift'] < 0.05).sum()),
                  shifted_dates=[str(d) for d in shifted_in])
    with open(os.path.join(OUT_DIR, "run_extras.json"), "w", encoding="utf-8") as f:
        json.dump(extras, f, indent=2, default=str)

if __name__ == "__main__":
    main()
