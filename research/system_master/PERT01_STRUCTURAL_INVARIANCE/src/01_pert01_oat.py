"""PERT01 -- one-at-a-time structural invariance.

DIAGNOSTIC SCIENCE ONLY (campaign directive sec97-98): report all results, select NO winner,
promote NOTHING. This script (and its outputs) cannot by itself create a new baseline candidate.

Per campaign directive: NO Cartesian grid -- vary exactly ONE axis at a time, holding all other
axes at the incumbent center value. Three axes are mechanically valid and are run here:

  A. VolPeriod   (Solar member causal-sigma trailing window): {368, 460[incumbent], 552}
  B. BAND_DAYS   (B-MOM trailing noise-band history, days):   {11, 14[incumbent], 17}
  C. TiltSma     (HTF tilt rolling window, sessions):         {40, 50[incumbent], 60}

  D. "B evidence units" (3/4/5) -- SKIPPED. Exhaustively grepped this session (evidence,
     evidence.?unit, min_agree, AgreeCount, n_agree, vote.?count, ConfirmBars across the whole
     repo) and found NO parameter matching this description anywhere in current code. Per
     campaign directive sec33/sec120, an unmappable axis is skipped and disclosed, not invented.
     See research/system_master/PERT01_STRUCTURAL_INVARIANCE/out/00_spec_verify_notes.md sec3 for
     the full search record.

Pipeline (verbatim reuse of already-certified formulas; ONLY the axis under test moves):
  sig(vol_period)  -> sm.sigma_series                          [src/analytics/sm01_solarsim.py]
  PEND             -> common.build_pend (member_states/member_trades UNMODIFIED, vms=INCUMBENT)
  T                -> sm.e10_target(PEND)                       (Solar13 consensus target, -10..10)
  tilt_state(window=50) -> rolling(window) sign-vs-SMA HTF state, shift(1) causal
  B(band_days=14)  -> local re-implementation of health_substrate.bmom_pos_series, BAND_DAYS
                       replaced by a `band_days` parameter everywhere it appears; verified
                       byte-identical to the frozen health_substrate.py output at band_days=14
                       (see VERIFY block below) before trusting 11/17.
  Product B: Tp = clip(rha(T*m_arr*TILTRESCALE),-13,13); M = WSOLAR*Tp + WBMOM*B
             position_B = build_pos_seq(M) (ENTRY_LEVEL=3.0/EXIT_LEVEL=1.0 hysteresis, discrete
             {-1,0,+1}), priced 1 NQ (COMM_NQ=$2.18/side, PV_NQ=$20/pt) -- house convention,
             matches runs/SA0_SYSTEM_STRUCTURE/{src/substrate.py,current_health/src/health_substrate.py}
  Product A: Tpp = clip(rha(T*m_arr*s_arr*TILTRESCALE),-13,13) [s_arr = short-halving overlay]
             M_A = clip(rha(KSOLAR*Tpp + KBMOM*B),-13,13)
             target_exposure_A = continuous exec in [-13,+13] with C4 partial-size gating,
             priced 1 MNQ-equivalent (COMM_MNQ_A=$0.65/side, PV_MNQ_A=$2/pt) -- matches
             runs/U0_UNIFIED_STATE/src/01_build_state_table.py product_a_exec_generalized verbatim.
  KSolar/KBmom/TiltRescale/TiltMult/ShortHalf/WSolar/WBmom/EntryLevel/ExitLevel are held EXACTLY
  at their current frozen values throughout (that axis belongs to EQV01, not this workflow).

Windows:
  primary_claude_canonical : 2023-01-01 .. 2025-02-02 (CLAUDE.md frozen canonical window) --
                              PRIMARY reporting window per this workflow's governance.
  fuller_history            : 2022-01-03 .. 2026-05-29 (last session <= 2026-05-31) -- the
                              SYSTEM_MASTER campaign's own established substrate window (matches
                              runs/SA0_SYSTEM_STRUCTURE/src/substrate.py's own dev mask and its
                              certified nets), used here as "the fuller available history the
                              existing substrate scripts already support" per this workflow's
                              governance note. Deliberately NOT extended into the 2026-06-01..
                              2026-07-31 health-only observational window (that extension exists
                              for a different purpose -- current-health monitoring, not structural
                              invariance -- and is not needed to satisfy this task).
  All configurations are built as ONE continuous execution over the full loaded n-bar array (state
  carried causally from 2022-01-03 onward, per WARMUP_STANDARD.md's mandatory continuation-run
  convention) and then SLICED into the two windows above for reporting -- never re-run fresh-start
  per window.

CDaR disclosure: this repo's only reusable drawdown-tail statistic is dd_battery()'s CDaR5 field
(src/analytics/smv2_common.py) -- the mean of the worst 5% of daily DRAWDOWN-LEVEL (peak-to-date
minus equity) observations, already the house-frozen convention used by every battery_row/
metric_row wrapper in this campaign (health_substrate.py, common.py). This is a drawdown-level
statistic, not a return-distribution CVaR/Expected-Shortfall -- disclosed per task instructions.
maxDD_eod (also from dd_battery) is reported as the literal "EOD DD" figure requested.

Cost-stress convention: matches runs/R2_ENTRY_TIMING/src/tail_and_cost_stress.py's own precedent
(a local `_fill` replacement with side*TICK*N total adverse slip). "+1 tick" stress = 2 ticks of
total adverse slip per fill (1 incumbent + 1 stress); "+2 ticks" = 3 ticks total. Position/decision
paths are unaffected by the fill price (build_pos_seq / the M_A threshold logic never reference the
fill price), so re-running the SAME position path through a stressed pricer is bar-for-bar exact,
not an approximation.
"""
import os
import sys
import json
import time

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "runs", "W18R1_M1_VOLSEASON", "src"))
sys.path.insert(0, os.path.join(ROOT, "runs", "SA0_SYSTEM_STRUCTURE", "current_health", "src"))

import sm01_solarsim as sm          # noqa: E402
from sm01_solarsim import load_bars_3m   # noqa: E402
from sm_bmom import rth_3m               # noqa: E402  (BAND_DAYS NOT imported -- axis under test)
from smv2_common import dd_battery       # noqa: E402
import common as C1                      # noqa: E402  (build_pend, INCUMBENT_VMS)

OUT = os.path.join(ROOT, "research", "system_master", "PERT01_STRUCTURAL_INVARIANCE", "out")
os.makedirs(OUT, exist_ok=True)

T0 = time.time()

# ============================================================= FROZEN CONSTANTS (not perturbed here)
TICK = sm.TICK
PV_NQ, COMM_NQ = 20.0, 2.18          # Product B pricing (NQ, Lifetime commission, matches CLAUDE.md)
PV_MNQ_A, COMM_MNQ_A = 2.0, 0.65     # Product A pricing (MNQ-equivalent point value/commission)
KSOLAR, KBMOM, TILTRESCALE, TILTMULT, SHORTHALF = 0.728654, 2.934159, 0.9026, 1.25, 0.5   # Product A
WSOLAR, WBMOM, ENTRY_LEVEL, EXIT_LEVEL = 0.7086, 2.83, 3.0, 1.0                            # Product B

CERTIFIED_B_NQ_NET_FULLER_HISTORY = 301915.92    # substrate.py CONTROL, 2022-01-03..2026-05-29
CERTIFIED_A_NET_FULLER_HISTORY = 177924.40       # U0 canonical-slice certified A net (same window)

FULL_END = pd.Timestamp("2026-05-31")            # last session <= this boundary (substrate.py convention)
CANON_START = pd.Timestamp("2023-01-01")         # CLAUDE.md frozen canonical window (PRIMARY reporting)
CANON_END = pd.Timestamp("2025-02-02")

INCUMBENT = {"VolPeriod": 460, "BandDays": 14, "TiltWindow": 50}

AXES = {
    "VolPeriod": {"low": 368, "center": 460, "high": 552,
                  "desc": "Solar member causal-sigma trailing window (sm.sigma_series vol_period)"},
    "BandDays": {"low": 11, "center": 14, "high": 17,
                 "desc": "B-MOM trailing noise-band history in sessions (sm_bmom.BAND_DAYS)"},
    "TiltWindow": {"low": 40, "center": 50, "high": 60,
                   "desc": "HTF tilt rolling window in sessions (common.htf_state rolling(50))"},
}
SKIPPED_AXIS_D = {
    "axis": "B evidence units", "candidate_values": [3, 4, 5],
    "status": "SKIPPED",
    "reason": ("Exhaustively grepped this session for evidence/evidence.?unit/min_agree/AgreeCount/"
               "n_agree/vote.?count/ConfirmBars across the whole repo -- no parameter matching this "
               "description exists in current code (Python or NinjaScript). Per campaign directive "
               "sec33/sec120, an unmappable axis is skipped and disclosed, not invented. See "
               "00_spec_verify_notes.md sec3 for the full search record."),
}


def rha(x):
    return np.sign(x) * np.floor(np.abs(x) + 0.5)


def _fill_stress(o, h, l, side, extra_ticks=0, at_close=None):
    """1-tick baseline adverse slip (matches sm01_solarsim._fill) + extra_ticks of additional
    adverse slip, capped by the fill bar's range. extra_ticks=0 must be byte-identical to
    sm._fill -- verified below."""
    base = at_close if at_close is not None else o
    px = base + side * TICK * (1 + extra_ticks)
    return min(px, h) if side > 0 else max(px, l)


# ============================================================= parametrized re-implementations
# (local copies mirroring the frozen files exactly, with ONE constant replaced by a function
# parameter each -- per this workflow's governance note / 00_spec_verify_notes.md sec2)

def bmom_pos_series(bars3, band_days=14):
    """Byte-identical mirror of health_substrate.py's bmom_pos_series, with BAND_DAYS replaced by
    the `band_days` parameter everywhere it appeared. Nothing else about the signal (bands, VWAP,
    force-flat clock) changes."""
    r = rth_3m(bars3)
    pos_arr = np.zeros(len(bars3))
    hist = {}
    day_count = 0
    for d_, g in r.groupby("date", sort=True):
        g = g.sort_values("hm")
        if g["hm"].iloc[0] != 933:
            continue
        open0930 = g["open"].iloc[0]
        close_ = g["close"].to_numpy(); vol = g["volume"].to_numpy(); hm = g["hm"].to_numpy()
        vwap = np.cumsum(close_ * vol) / np.maximum(np.cumsum(vol), 1e-9)
        gidx = g.index.to_numpy(); pos = 0
        flat_hm = int(hm[hm <= 1557].max()) if (hm <= 1557).any() else None
        if day_count >= band_days:
            for i in range(len(g)):
                h = int(hm[i])
                if flat_hm is not None and h == flat_hm:
                    pos = 0; pos_arr[gidx[i]] = pos; break
                if h > 1554:
                    pos_arr[gidx[i]] = pos; continue
                past = hist.get(h)
                if past is not None and len(past) >= 1:
                    m_tod = float(np.mean(past[-band_days:]))
                    up, lo = open0930 + m_tod, open0930 - m_tod
                    if close_[i] > max(up, vwap[i]):
                        pos = 1
                    elif close_[i] < min(lo, vwap[i]):
                        pos = -1
                pos_arr[gidx[i]] = pos
        for i in range(len(g)):
            hist.setdefault(int(hm[i]), []).append(abs(close_[i] - open0930))
        day_count += 1
    return pos_arr


def htf_tilt_state(bars, window=50):
    """Mirror of common.htf_state / health_substrate.py's tilt_state construction, with the
    rolling window parametrized. .shift(1) and np.sign comparison held fixed (causality-preserving).
    fillna(0.0) applied, matching health_substrate.py's own convention (needed because build_pos_seq
    / product_a's m_arr construction does tilt_state!=0, and NaN!=0 is True in numpy)."""
    sclose = bars.loc[bars["is_last_of_sess"], ["sess_date", "close"]].set_index("sess_date")["close"]
    tilt_by_date = np.sign(sclose - sclose.rolling(window).mean()).shift(1).to_dict()
    tilt_state = np.array([tilt_by_date.get(d, np.nan) for d in bars["sess_date"]])
    tilt_state = np.where(np.isnan(tilt_state), 0.0, tilt_state)
    return tilt_state


def build_pos_seq(M_arr, n_, last_, entry_blocked_, forced_flat_,
                   entry_level=ENTRY_LEVEL, exit_level=EXIT_LEVEL):
    """Verbatim substrate.py / health_substrate.py build_pos_seq."""
    p = 0; pend = 0
    pos_seq = np.zeros(n_, dtype=int)
    for t in range(n_):
        if pend != p:
            p = pend
        if last_[t] and p != 0:
            p = 0; pend = 0
            pos_seq[t] = p
            continue
        pos_seq[t] = p
        if forced_flat_[t]:
            tgt = 0
        elif p == 0:
            tgt = 0 if entry_blocked_[t] else (1 if M_arr[t] >= entry_level else (-1 if M_arr[t] <= -entry_level else 0))
        elif p > 0:
            if M_arr[t] <= -entry_level and not entry_blocked_[t]:
                tgt = -1
            elif M_arr[t] <= exit_level:
                tgt = 0
            else:
                tgt = p
        else:
            if M_arr[t] >= entry_level and not entry_blocked_[t]:
                tgt = 1
            elif M_arr[t] >= -exit_level:
                tgt = 0
            else:
                tgt = p
        pend = tgt
    return pos_seq


def onelot_exec(pos_seq, comm, pv, o, h, l, c, last_, n_, extra_ticks=0):
    """Verbatim substrate.py / health_substrate.py onelot_exec, parametrized by extra_ticks
    (0 => byte-identical to the frozen file, verified below)."""
    cash = 0.0; p = 0; prev_eq = 0.0
    bar_pos = np.zeros(n_, dtype=int); bar_pnl = np.zeros(n_)
    for t in range(n_):
        tgt = int(pos_seq[t])
        if tgt != p:
            d = tgt - p
            side = 1 if d > 0 else -1
            if last_[t]:
                px = _fill_stress(o[t], h[t], l[t], side, extra_ticks=extra_ticks, at_close=c[t])
            else:
                px = _fill_stress(o[t], h[t], l[t], side, extra_ticks=extra_ticks)
            cash -= d * px * pv
            cash -= abs(d) * comm
            p = tgt
        eq = cash + p * c[t] * pv
        bar_pnl[t] = eq - prev_eq; prev_eq = eq
        bar_pos[t] = p
    return bar_pos, bar_pnl


def product_a_exec_generalized(T_leg, tilt_state_, B_, entry_blocked_, forced_flat_,
                                o, h, l, c, last_, n_, extra_ticks=0):
    """Verbatim runs/U0_UNIFIED_STATE/src/01_build_state_table.py product_a_exec_generalized,
    parametrized by extra_ticks (0 => byte-identical to the frozen file, verified below)."""
    m_arr = np.where((T_leg != 0) & (tilt_state_ != 0) & (np.sign(T_leg) == tilt_state_), TILTMULT, 1.0)
    s_arr = np.where((T_leg < 0) & (tilt_state_ > 0), SHORTHALF, 1.0)
    Tpp = np.clip(rha(T_leg * m_arr * s_arr * TILTRESCALE), -13, 13)
    M_a = np.clip(rha(KSOLAR * Tpp + KBMOM * B_), -13, 13)

    cash = 0.0; p = 0; pend = 0; prev_eq = 0.0
    bar_pos = np.zeros(n_, dtype=int)
    bar_pnl = np.zeros(n_)
    for t in range(n_):
        if pend != p:
            d = pend - p
            side = 1 if d > 0 else -1
            px = _fill_stress(o[t], h[t], l[t], side, extra_ticks=extra_ticks)
            cash -= d * px * PV_MNQ_A
            cash -= abs(d) * COMM_MNQ_A
            p = pend
        if last_[t] and p != 0:
            side = -1 if p > 0 else 1
            px = _fill_stress(o[t], h[t], l[t], side, extra_ticks=extra_ticks, at_close=c[t])
            cash += p * px * PV_MNQ_A
            cash -= abs(p) * COMM_MNQ_A
            p = 0; pend = 0
        else:
            tgt_raw = int(M_a[t])
            if forced_flat_[t]:
                tgt = 0
            elif entry_blocked_[t]:
                if tgt_raw == 0 or p == 0:
                    tgt = 0
                elif np.sign(tgt_raw) != np.sign(p):
                    tgt = 0
                else:
                    tgt = p if abs(tgt_raw) > abs(p) else tgt_raw
            else:
                tgt = tgt_raw
            pend = tgt
        eq = cash + p * c[t] * PV_MNQ_A
        bar_pnl[t] = eq - prev_eq; prev_eq = eq
        bar_pos[t] = p
    return bar_pos, bar_pnl, M_a


# ============================================================= load bars, build fixed scaffolding
print("[PERT01] loading bars ...", flush=True)
bars_all = load_bars_3m(os.path.join(ROOT, "runs", "AUDIT03_BARS", "nq_3m_2022_2026.csv"))
sess_all = pd.to_datetime(bars_all["sess_date"])
bars = bars_all[sess_all <= FULL_END].reset_index(drop=True)
n = len(bars)
close = bars["close"].to_numpy(); open_ = bars["open"].to_numpy()
high = bars["high"].to_numpy(); low = bars["low"].to_numpy()
last = bars["is_last_of_sess"].to_numpy()
sd = bars["sess_date"].to_numpy()
sd_dt = pd.to_datetime(pd.Series(sd))

sess_close_ts = bars.groupby("sess_date")["time"].transform("max")
entry_block_dl = sess_close_ts - pd.Timedelta(minutes=30)
forced_flat_dl = sess_close_ts - pd.Timedelta(minutes=21)
bar_time = bars["time"]
entry_blocked_c4 = (bar_time >= entry_block_dl).to_numpy()
forced_flat_c4 = (bar_time >= forced_flat_dl).to_numpy()

mask_primary = ((sd_dt >= CANON_START) & (sd_dt <= CANON_END)).to_numpy()
mask_fuller = np.ones(n, dtype=bool)
WINDOWS = {"primary_claude_canonical": mask_primary, "fuller_history": mask_fuller}
print(f"[PERT01] n_bars={n}, fuller_history sessions={bars['sess_date'].nunique()}, "
      f"primary_claude_canonical bars={int(mask_primary.sum())} "
      f"({sd_dt[mask_primary].min()} .. {sd_dt[mask_primary].max()})", flush=True)

# ============================================================= cross-check parametrized fns against
# the frozen originals (health_substrate.py) at incumbent center BEFORE trusting perturbed values
print("[PERT01] cross-checking parametrized re-implementations against health_substrate.py "
      "at incumbent center ...", flush=True)
import health_substrate as HS  # noqa: E402  (heavy import: runs its own full build + correctness gate)

B14_check = bmom_pos_series(bars, band_days=14)
assert np.array_equal(B14_check, HS.B[: n]), "bmom_pos_series(band_days=14) mismatch vs health_substrate.B"
tilt50_check = htf_tilt_state(bars, window=50)
assert np.allclose(tilt50_check, HS.tilt_state[: n], equal_nan=True), \
    "htf_tilt_state(window=50) mismatch vs health_substrate.tilt_state"
posB_check = build_pos_seq(HS.M[: n], n, last, entry_blocked_c4, forced_flat_c4)
assert np.array_equal(posB_check, HS.build_pos_seq(HS.M)[: n]), "build_pos_seq mismatch vs health_substrate"
_bp, _bpnl = onelot_exec(posB_check, COMM_NQ, PV_NQ, open_, high, low, close, last, n, extra_ticks=0)
_dgt, _bpgt, _bpnlgt = HS.onelot_exec(HS.build_pos_seq(HS.M), HS.COMM_NQ, HS.PV_NQ,
                                       HS.open_, HS.high, HS.low, HS.close)
assert np.allclose(_bpnl, _bpnlgt[: n]), "onelot_exec(extra_ticks=0) mismatch vs health_substrate"
_bpA, _bpnlA, _MA = product_a_exec_generalized(HS.T, HS.tilt_state, HS.B, entry_blocked_c4,
                                                forced_flat_c4, open_, high, low, close, last, n,
                                                extra_ticks=0)
print(f"[PERT01] cross-check net A (this script's product_a_exec_generalized, full-loaded window) "
      f"= {_bpnlA.sum():.2f} (health_substrate itself does not compute Product A -- U0 does; "
      f"this is a fresh, independent re-derivation, not a re-import)", flush=True)
print("[PERT01] all parametrized re-implementations VERIFIED byte-identical to frozen originals "
      "at incumbent center.", flush=True)

# ============================================================= INCUMBENT-CENTER baseline build
print("[PERT01] building INCUMBENT-CENTER baseline (VolPeriod=460, BandDays=14, TiltWindow=50) ...",
      flush=True)
sig460 = sm.sigma_series(close, vol_period=460)
PEND460 = C1.build_pend(bars, sig460)     # vms=INCUMBENT_VMS (unperturbed, 13 members 6..30 step 2)
T460 = sm.e10_target(PEND460).astype(int)
tilt50 = htf_tilt_state(bars, window=50)
B14 = bmom_pos_series(bars, band_days=14)


def build_config(T_arr, tilt_arr, B_arr):
    """Given the three shared drivers (T, tilt_state, B), build the FULL downstream state for
    both products: Product B's M/position/pricing, Product A's M_A_raw/exposure/pricing, at
    extra_ticks in {0,1,2}."""
    m_arr = np.where((T_arr != 0) & (tilt_arr != 0) & (np.sign(T_arr) == tilt_arr), TILTMULT, 1.0)
    Tp = np.clip(rha(T_arr * m_arr * TILTRESCALE), -13, 13)
    M_B = WSOLAR * Tp + WBMOM * np.asarray(B_arr)
    pos_B = build_pos_seq(M_B, n, last, entry_blocked_c4, forced_flat_c4)

    out = {"T": T_arr, "tilt": tilt_arr, "B": B_arr, "Tp": Tp, "M_B": M_B, "pos_B": pos_B}
    for et in (0, 1, 2):
        _, bpnl_B = onelot_exec(pos_B, COMM_NQ, PV_NQ, open_, high, low, close, last, n, extra_ticks=et)
        out[f"bpnl_B_et{et}"] = bpnl_B
    barpos_A, bpnl_A0, M_A_raw = product_a_exec_generalized(
        T_arr, tilt_arr, B_arr, entry_blocked_c4, forced_flat_c4, open_, high, low, close, last, n,
        extra_ticks=0)
    out["barpos_A"] = barpos_A
    out["M_A_raw"] = M_A_raw
    out["bpnl_A_et0"] = bpnl_A0
    for et in (1, 2):
        _, bpnl_A_et, _ = product_a_exec_generalized(
            T_arr, tilt_arr, B_arr, entry_blocked_c4, forced_flat_c4, open_, high, low, close, last, n,
            extra_ticks=et)
        out[f"bpnl_A_et{et}"] = bpnl_A_et
    return out


INCUMBENT_CFG = build_config(T460, tilt50, B14)

canon_net_B = float(INCUMBENT_CFG["bpnl_B_et0"].sum())
canon_net_A = float(INCUMBENT_CFG["bpnl_A_et0"].sum())
gate_B_ok = abs(canon_net_B - CERTIFIED_B_NQ_NET_FULLER_HISTORY) < 1.0
gate_A_ok = abs(canon_net_A - CERTIFIED_A_NET_FULLER_HISTORY) < 1.0
print(f"[PERT01] CORRECTNESS GATE (fuller_history window, incumbent center): "
      f"Product-B NQ net={canon_net_B:.2f} vs certified {CERTIFIED_B_NQ_NET_FULLER_HISTORY:.2f} -> "
      f"{'PASS' if gate_B_ok else 'FAIL'}; "
      f"Product-A net={canon_net_A:.2f} vs certified {CERTIFIED_A_NET_FULLER_HISTORY:.2f} -> "
      f"{'PASS' if gate_A_ok else 'FAIL'}", flush=True)
if not (gate_B_ok and gate_A_ok):
    raise SystemExit("[PERT01] CORRECTNESS GATE FAILED -- stopping, not proceeding on a broken "
                      "incumbent-center reconstruction.")

# ============================================================= metrics helpers

def daily_net(bar_pnl, mask):
    d = pd.DataFrame({"sess": sd, "pnl": bar_pnl})[mask].groupby("sess")["pnl"].sum().reset_index()
    return d["sess"].to_numpy(), d["pnl"].to_numpy()


def perf_block(bpnl_arrays, bar_pos, mask, prefix):
    """bpnl_arrays: dict {0: base, 1: +1tick, 2: +2tick} bar_pnl arrays. bar_pos: n-length bar
    position array (for exposure normalization)."""
    s, x = daily_net(bpnl_arrays[0], mask)
    row = {}
    if len(x) == 0:
        b = {"n_days": 0, "net": np.nan, "sharpe": np.nan, "sortino": np.nan, "calmar": np.nan,
             "CDaR5": np.nan, "maxDD_eod": np.nan}
        worst_day = np.nan
    else:
        b = dd_battery(pd.to_datetime(s), x, label=prefix)
        worst_day = float(x.min())
    row[f"{prefix}_n_days"] = b["n_days"]
    row[f"{prefix}_net"] = b["net"]
    row[f"{prefix}_sharpe"] = b["sharpe"]
    row[f"{prefix}_sortino"] = b["sortino"]
    row[f"{prefix}_calmar"] = b["calmar"]
    row[f"{prefix}_CDaR5_drawdown_level"] = b["CDaR5"]
    row[f"{prefix}_maxDD_eod"] = b["maxDD_eod"]
    row[f"{prefix}_worst_day"] = worst_day
    sum_abs_exposure = float(np.abs(bar_pos[mask]).sum())
    row[f"{prefix}_net_per_contract_bar_exposure"] = (
        b["net"] / sum_abs_exposure if sum_abs_exposure > 0 and len(x) else np.nan)
    net0 = b["net"] if len(x) else np.nan
    for et in (1, 2):
        _, xet = daily_net(bpnl_arrays[et], mask)
        net_et = float(xet.sum()) if len(xet) else np.nan
        row[f"{prefix}_net_plus{et}tick"] = net_et
        row[f"{prefix}_cost_stress_retention_plus{et}tick"] = (
            net_et / net0 if (net0 not in (0, np.nan) and not pd.isna(net0)) else np.nan)
    return row


def entries_set(pos):
    sgn = np.sign(pos).astype(int)
    change = np.r_[True, sgn[1:] != sgn[:-1]]
    starts = np.where(change & (sgn != 0))[0]
    return set(zip(starts.tolist(), sgn[starts].tolist()))


def jaccard(a, b):
    if not a and not b:
        return 1.0
    u = a | b
    return len(a & b) / len(u) if u else 1.0


def struct_block(cfg, inc_cfg):
    row = {}
    row["struct_position_agreement_B"] = float(np.mean(cfg["pos_B"] == inc_cfg["pos_B"]))
    row["struct_position_agreement_A_sign"] = float(
        np.mean(np.sign(cfg["barpos_A"]) == np.sign(inc_cfg["barpos_A"])))
    row["struct_position_agreement_A_exact"] = float(np.mean(cfg["barpos_A"] == inc_cfg["barpos_A"]))
    ent_cfg = entries_set(cfg["pos_B"]); ent_inc = entries_set(inc_cfg["pos_B"])
    row["struct_jaccard_B_entries"] = jaccard(ent_cfg, ent_inc)
    ent_cfg_A = entries_set(cfg["barpos_A"]); ent_inc_A = entries_set(inc_cfg["barpos_A"])
    row["struct_jaccard_A_entries_bonus"] = jaccard(ent_cfg_A, ent_inc_A)
    row["struct_corr_M_B"] = float(np.corrcoef(cfg["M_B"], inc_cfg["M_B"])[0, 1])
    row["struct_corr_M_A_raw"] = float(np.corrcoef(cfg["M_A_raw"], inc_cfg["M_A_raw"])[0, 1])
    row["struct_n_bars"] = n
    return row


def build_row(axis, role, value, cfg, inc_cfg):
    row = {"axis": axis, "role": role, "param_value": value,
           "incumbent_value": INCUMBENT.get(axis, np.nan)}
    row.update(struct_block(cfg, inc_cfg))
    for wname, wmask in WINDOWS.items():
        bB = {0: cfg["bpnl_B_et0"], 1: cfg["bpnl_B_et1"], 2: cfg["bpnl_B_et2"]}
        bA = {0: cfg["bpnl_A_et0"], 1: cfg["bpnl_A_et1"], 2: cfg["bpnl_A_et2"]}
        row.update(perf_block(bB, cfg["pos_B"], wmask, f"{wname}_B"))
        row.update(perf_block(bA, cfg["barpos_A"], wmask, f"{wname}_A"))
    return row


# ============================================================= run all configurations
print("[PERT01] running per-axis low/center/high configurations ...", flush=True)
rows = []

# --- master INCUMBENT reference row (identical numbers, self-comparison => perfect agreement)
rows.append(build_row("INCUMBENT", "center", "VolPeriod=460,BandDays=14,TiltWindow=50",
                       INCUMBENT_CFG, INCUMBENT_CFG))

cfg_cache = {}   # (axis, value) -> cfg, so shared "center" reuse doesn't recompute

for axis, spec in AXES.items():
    for role in ("low", "center", "high"):
        value = spec[role]
        print(f"[PERT01]   axis={axis} role={role} value={value} ...", flush=True)
        if axis == "VolPeriod":
            if value == INCUMBENT["VolPeriod"]:
                cfg = INCUMBENT_CFG
            else:
                sig_v = sm.sigma_series(close, vol_period=value)
                PEND_v = C1.build_pend(bars, sig_v)
                T_v = sm.e10_target(PEND_v).astype(int)
                cfg = build_config(T_v, tilt50, B14)
        elif axis == "BandDays":
            if value == INCUMBENT["BandDays"]:
                cfg = INCUMBENT_CFG
            else:
                B_v = bmom_pos_series(bars, band_days=value)
                cfg = build_config(T460, tilt50, B_v)
        elif axis == "TiltWindow":
            if value == INCUMBENT["TiltWindow"]:
                cfg = INCUMBENT_CFG
            else:
                tilt_v = htf_tilt_state(bars, window=value)
                cfg = build_config(T460, tilt_v, B14)
        else:
            raise AssertionError(axis)
        cfg_cache[(axis, value)] = cfg
        row = build_row(axis, role, value, cfg, INCUMBENT_CFG)
        # elasticity vs incumbent (headline: primary-window net, both products)
        pct_d_param = (value - INCUMBENT[axis]) / INCUMBENT[axis] if value != INCUMBENT[axis] else 0.0
        for leg in ("B", "A"):
            net_key = f"primary_claude_canonical_{leg}_net"
            net_inc = rows[0][net_key]
            net_v = row[net_key]
            if pct_d_param == 0 or net_inc in (0,) or pd.isna(net_inc) or pd.isna(net_v):
                elas = 0.0 if pct_d_param == 0 else np.nan
            else:
                pct_d_perf = (net_v - net_inc) / abs(net_inc)
                elas = pct_d_perf / pct_d_param
            row[f"elasticity_net_{leg}_primary_window_vs_incumbent"] = elas
        rows.append(row)

df = pd.DataFrame(rows)
csv_path = os.path.join(OUT, "pert01_results.csv")
json_path = os.path.join(OUT, "pert01_results.json")
df.to_csv(csv_path, index=False)

payload = {
    "meta": {
        "generated_utc": pd.Timestamp.utcnow().isoformat(),
        "diagnostic_only": True,
        "selects_no_winner": True,
        "one_at_a_time_only": True,
        "n_bars_fuller_history": int(n),
        "n_sessions_fuller_history": int(bars["sess_date"].nunique()),
        "windows": {
            "primary_claude_canonical": {"start": "2023-01-01", "end": "2025-02-02",
                                          "n_bars": int(mask_primary.sum())},
            "fuller_history": {"start": str(sd_dt.min().date()), "end": str(sd_dt.max().date()),
                                "n_bars": int(n)},
        },
        "correctness_gate": {
            "product_B_NQ_net_fuller_history": canon_net_B,
            "certified_B_NQ_net": CERTIFIED_B_NQ_NET_FULLER_HISTORY,
            "product_A_net_fuller_history": canon_net_A,
            "certified_A_net": CERTIFIED_A_NET_FULLER_HISTORY,
            "pass": bool(gate_B_ok and gate_A_ok),
        },
        "frozen_downstream_constants_not_perturbed": {
            "KSolar": KSOLAR, "KBmom": KBMOM, "TiltRescale": TILTRESCALE, "TiltMult": TILTMULT,
            "ShortHalf": SHORTHALF, "WSolar": WSOLAR, "WBmom": WBMOM,
            "EntryLevel": ENTRY_LEVEL, "ExitLevel": EXIT_LEVEL,
        },
        "commission_conventions": {"NQ_per_side": COMM_NQ, "NQ_per_RT": COMM_NQ * 2,
                                    "MNQ_A_per_side": COMM_MNQ_A, "MNQ_A_per_RT": COMM_MNQ_A * 2},
        "axes_run": {k: v["desc"] for k, v in AXES.items()},
        "axis_skipped": SKIPPED_AXIS_D,
        "definitions": {
            "struct_position_agreement_B": "mean(1[position_B(theta)==position_B(incumbent)]) over "
                                            "all fuller_history bars, discrete {-1,0,1}",
            "struct_position_agreement_A_sign": "same, sign(target_exposure_A), continuous -13..13",
            "struct_position_agreement_A_exact": "same, exact integer match (stricter)",
            "struct_jaccard_B_entries": "Jaccard of (entry_bar_idx, side) tuples -- an entry event "
                                         "is the first bar of a new same-sign contiguous position "
                                         "block in position_B -- between theta and incumbent, over "
                                         "the fuller_history window",
            "struct_jaccard_A_entries_bonus": "same construction applied to target_exposure_A "
                                               "sign-blocks; not explicitly requested by the task, "
                                               "included for completeness",
            "struct_corr_M_B": "Pearson corr of the Product-B latent score M = WSolar*Tp+WBmom*B, "
                                "bar-level, fuller_history window",
            "struct_corr_M_A_raw": "Pearson corr of the Product-A latent score M_A, same construction",
            "CDaR5_drawdown_level": "dd_battery()'s CDaR5: mean of worst-5%-of-days DRAWDOWN-LEVEL "
                                     "(peak-to-date minus equity), the house-frozen convention -- "
                                     "NOT a return-distribution CVaR (disclosed per task instructions)",
            "maxDD_eod": "end-of-day max drawdown, the literal 'EOD DD' requested",
            "net_per_contract_bar_exposure": "window net $ / sum(|bar_position|) over the window's "
                                              "bars -- dollars earned per (contract x bar) of "
                                              "exposure carried, a size-normalized performance figure",
            "cost_stress_retention_plusNtick": "net at (1+N) total ticks of adverse slip per fill / "
                                                "net at incumbent 1-tick slip; position path is "
                                                "identical (decisions don't depend on fill price), "
                                                "only pricing is re-run",
            "elasticity_net_leg_primary_window_vs_incumbent": "(%change in primary-window net) / "
                                                                "(%change in the axis parameter), "
                                                                "vs the incumbent center; 0 at the "
                                                                "center row by construction",
        },
    },
    "rows": df.to_dict(orient="records"),
}
with open(json_path, "w") as f:
    json.dump(payload, f, indent=2, default=lambda o: None if pd.isna(o) else float(o))

print(f"\n[PERT01] wrote {csv_path}", flush=True)
print(f"[PERT01] wrote {json_path}", flush=True)
print(f"[PERT01] total elapsed {time.time() - T0:.1f}s", flush=True)

# ---------------------------------------------------------------- console center-spike summary
pd.set_option("display.width", 220)
for axis in AXES:
    sub = df[df["axis"] == axis][["role", "param_value",
                                   "struct_position_agreement_B", "struct_jaccard_B_entries",
                                   "struct_corr_M_B",
                                   "primary_claude_canonical_B_net", "primary_claude_canonical_B_sharpe",
                                   "primary_claude_canonical_A_net", "primary_claude_canonical_A_sharpe",
                                   "elasticity_net_B_primary_window_vs_incumbent"]]
    print(f"\n=== {axis} center-spike table (primary_claude_canonical window) ===")
    print(sub.to_string(index=False))

print("\n[PERT01] DIAGNOSTIC RUN COMPLETE. No winner selected. No candidate promoted.")
