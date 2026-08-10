"""grid_core.py -- shared substrate for GRID01 (Solar member-resolution convergence) and
GRID02 (endpoint perturbation). DIAGNOSTIC SCIENCE ONLY (campaign directive sec97-98): report
all results, select no winner, promote nothing. GRID/PERT results can never by themselves
create a new baseline candidate.

Every non-Solar-ensemble input is held EXACTLY at its current frozen value: the B-MOM leg
(BAND_DAYS=14), the HTF tilt state (rolling(50) of session closes), the C4 entry-block/
forced-flat clocks, and both product decoders' constants (KSolar=0.728654, KBmom=2.934159,
TiltRescale=0.9026, TiltMult=1.25, ShortHalf=0.5 for Product A; WSolar=0.7086, WBmom=2.83,
EntryLevel=3.0, ExitLevel=1.0 for Product B). ONLY the Solar member `vms` list fed into
common.build_pend() varies across grids -- member_states/member_trades themselves are
UNMODIFIED (reused verbatim from src/analytics/sm01_solarsim.py).

Product-A execution is a verbatim-formula copy of
runs/U0_UNIFIED_STATE/src/01_build_state_table.py's product_a_exec_generalized (generalized
further with a `ticks` adverse-slip parameter for the cost-stress test only; ticks=1
reproduces the canonical 1-tick convention exactly). Product-B execution is a verbatim-formula
copy of runs/SA0_SYSTEM_STRUCTURE/current_health/src/health_substrate.py's
build_pos_seq/onelot_exec, same generalization. Both are self-checked at import time against
the repo's own certified dev-window (2022-01-03..2026-05-31) nets before any grid is trusted.
"""
import os, sys
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "runs", "W18R1_M1_VOLSEASON", "src"))
import sm01_solarsim as sm
from sm01_solarsim import load_bars_3m
from sm_bmom import rth_3m, BAND_DAYS
from smv2_common import dd_battery
import common as C1

TICK = sm.TICK

# ---------------------------------------------------------------- frozen decoder constants
# EXACT current values (governance-verified). This workflow does NOT perturb any of these --
# that is EQV01's job, not GRID01/GRID02's.
PV_NQ, COMM_NQ = 20.0, 2.18          # Product-B primary report instrument (BEST_ONE_NQ)
PV_MNQ, COMM_MNQ = 2.0, 0.65         # Product-B MNQ leg (background reference)
PV_MNQ_A, COMM_MNQ_A = 2.0, 0.65     # Product-A execution economics (verbatim U0; NQ price levels)
ENTRY_LEVEL, EXIT_LEVEL = 3.0, 1.0
WSOLAR, WBMOM, TILTRESCALE, TILTMULT = 0.7086, 2.83, 0.9026, 1.25
KSOLAR, KBMOM, SHORTHALF = 0.728654, 2.934159, 0.5

# ---------------------------------------------------------------- windows
HEALTH_END = pd.Timestamp("2026-07-31")    # fullest already-available, not-locked-forward data
DEV_END = pd.Timestamp("2026-05-31")       # repo's own certified dev-window boundary (gate only)
CANON_START = pd.Timestamp("2023-01-01")   # CLAUDE.md canonical window, primary report
CANON_END = pd.Timestamp("2025-02-02")     # "last session ending <= D" convention


def rha(x):
    return np.sign(x) * np.floor(np.abs(x) + 0.5)


def _fill_n(o, h, l, side, ticks=1, at_close=None):
    """Generalization of sm01_solarsim._fill: `ticks` adverse-slip ticks instead of the
    hardcoded 1. ticks=1 reproduces sm._fill byte-for-byte (asserted at import time below)."""
    base = at_close if at_close is not None else o
    px = base + side * ticks * TICK
    return min(px, h) if side > 0 else max(px, l)


assert sm._fill(100.0, 101.0, 99.0, 1) == _fill_n(100.0, 101.0, 99.0, 1, ticks=1)
assert sm._fill(100.0, 101.0, 99.0, -1, at_close=100.5) == \
    _fill_n(100.0, 101.0, 99.0, -1, ticks=1, at_close=100.5)

# ------------------------------------------------------------------------- load bars ONCE
print("[grid_core] loading bars through 2026-07-31 ...", flush=True)
_bars = load_bars_3m()
_sess_dt_all = pd.to_datetime(_bars["sess_date"])
_bars = _bars[(_sess_dt_all <= HEALTH_END)].reset_index(drop=True)
N = len(_bars)

CLOSE = _bars["close"].to_numpy()
OPEN_ = _bars["open"].to_numpy()
HIGH = _bars["high"].to_numpy()
LOW = _bars["low"].to_numpy()
LAST = _bars["is_last_of_sess"].to_numpy()
SD = _bars["sess_date"].to_numpy()
SESS_DT = pd.to_datetime(_bars["sess_date"])
TIME = _bars["time"]

SIG460 = sm.sigma_series(CLOSE)   # vol_period=460 unchanged -- GRID01/GRID02 vary vms ONLY

print(f"[grid_core] {N} bars, {_bars['sess_date'].nunique()} sessions, "
      f"{_bars['time'].min()} .. {_bars['time'].max()}", flush=True)

# ---------------------------------------------------------------- HTF tilt state (unchanged)
_sclose = _bars.loc[_bars["is_last_of_sess"], ["sess_date", "close"]].set_index("sess_date")["close"]
_tilt_by_date = np.sign(_sclose - _sclose.rolling(50).mean()).shift(1).to_dict()
TILT_STATE = np.array([_tilt_by_date.get(d, np.nan) for d in _bars["sess_date"]])
TILT_STATE = np.where(np.isnan(TILT_STATE), 0.0, TILT_STATE)


# ---------------------------------------------------------------- B-MOM leg (BAND_DAYS=14, unchanged)
def bmom_pos_series(bars3):
    """Verbatim health_substrate.py / substrate.py bmom_pos_series. Not touched by GRID01/GRID02
    (BAND_DAYS is a PERT01 axis, not this workflow's)."""
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
        if day_count >= BAND_DAYS:
            for i in range(len(g)):
                h = int(hm[i])
                if flat_hm is not None and h == flat_hm:
                    pos = 0; pos_arr[gidx[i]] = pos; break
                if h > 1554:
                    pos_arr[gidx[i]] = pos; continue
                past = hist.get(h)
                if past is not None and len(past) >= 1:
                    m_tod = float(np.mean(past[-BAND_DAYS:]))
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


print("[grid_core] building B-MOM leg (BAND_DAYS=14, unchanged) ...", flush=True)
B_LEG = bmom_pos_series(_bars)

_sess_close_ts = _bars.groupby("sess_date")["time"].transform("max")
_entry_block_dl = _sess_close_ts - pd.Timedelta(minutes=30)
_forced_flat_dl = _sess_close_ts - pd.Timedelta(minutes=21)
ENTRY_BLOCKED_C4 = (TIME >= _entry_block_dl).to_numpy()
FORCED_FLAT_C4 = (TIME >= _forced_flat_dl).to_numpy()


# ------------------------------------------------------------------------- Solar ensemble
def build_grid(vms, sig=None):
    """Build the member ensemble for a given `vms` list (GRID01/GRID02's ONLY varied input).
    Returns (PEND, T, consensus): PEND = (N, n_members) per-member pending-position matrix
    (member_states/member_trades UNMODIFIED), T = e10_target(PEND) (int, +/-10, the discrete
    Solar E10 leg fed into both product decoders), consensus = PEND.mean(axis=1) (the raw
    continuous pre-rounding consensus score used for the state-correlation/sign-agreement
    metrics)."""
    sig = SIG460 if sig is None else sig
    PEND = C1.build_pend(_bars, sig, vms=list(vms))
    T = sm.e10_target(PEND).astype(int)
    consensus = PEND.mean(axis=1)
    return PEND, T, consensus


# ------------------------------------------------------------------------- Product A
def product_a_exec(T, ticks=1):
    """Verbatim-formula copy of U0's product_a_exec_generalized (KSolar/KBmom/TiltRescale/
    TiltMult/ShortHalf held EXACTLY at governed values). `ticks` generalizes the adverse-slip
    convention for the cost-stress test only; ticks=1 == canonical."""
    m_arr = np.where((T != 0) & (TILT_STATE != 0) & (np.sign(T) == TILT_STATE), TILTMULT, 1.0)
    s_arr = np.where((T < 0) & (TILT_STATE > 0), SHORTHALF, 1.0)
    Tpp = np.clip(rha(T * m_arr * s_arr * TILTRESCALE), -13, 13)
    M_a = np.clip(rha(KSOLAR * Tpp + KBMOM * np.asarray(B_LEG)), -13, 13)

    cash = 0.0; p = 0; pend = 0; prev_eq = 0.0
    bar_pos = np.zeros(N, dtype=int)
    bar_pnl = np.zeros(N)
    for t in range(N):
        if pend != p:
            d = pend - p
            side = 1 if d > 0 else -1
            px = _fill_n(OPEN_[t], HIGH[t], LOW[t], side, ticks=ticks)
            cash -= d * px * PV_MNQ_A
            cash -= abs(d) * COMM_MNQ_A
            p = pend
        if LAST[t] and p != 0:
            side = -1 if p > 0 else 1
            px = _fill_n(OPEN_[t], HIGH[t], LOW[t], side, ticks=ticks, at_close=CLOSE[t])
            cash += p * px * PV_MNQ_A
            cash -= abs(p) * COMM_MNQ_A
            p = 0; pend = 0
        else:
            tgt_raw = int(M_a[t])
            if FORCED_FLAT_C4[t]:
                tgt = 0
            elif ENTRY_BLOCKED_C4[t]:
                if tgt_raw == 0 or p == 0:
                    tgt = 0
                elif np.sign(tgt_raw) != np.sign(p):
                    tgt = 0
                else:
                    tgt = p if abs(tgt_raw) > abs(p) else tgt_raw
            else:
                tgt = tgt_raw
            pend = tgt
        eq = cash + p * CLOSE[t] * PV_MNQ_A
        bar_pnl[t] = eq - prev_eq; prev_eq = eq
        bar_pos[t] = p
    return bar_pos, bar_pnl, M_a


# ------------------------------------------------------------------------- Product B
def _build_pos_seq(M_arr, entry_level=ENTRY_LEVEL, exit_level=EXIT_LEVEL):
    """Verbatim health_substrate.py / substrate.py build_pos_seq."""
    p = 0; pend = 0
    pos_seq = np.zeros(N, dtype=int)
    for t in range(N):
        if pend != p:
            p = pend
        if LAST[t] and p != 0:
            p = 0; pend = 0
            pos_seq[t] = p
            continue
        pos_seq[t] = p
        if FORCED_FLAT_C4[t]:
            tgt = 0
        elif p == 0:
            tgt = 0 if ENTRY_BLOCKED_C4[t] else (
                1 if M_arr[t] >= entry_level else (-1 if M_arr[t] <= -entry_level else 0))
        elif p > 0:
            if M_arr[t] <= -entry_level and not ENTRY_BLOCKED_C4[t]:
                tgt = -1
            elif M_arr[t] <= exit_level:
                tgt = 0
            else:
                tgt = p
        else:
            if M_arr[t] >= entry_level and not ENTRY_BLOCKED_C4[t]:
                tgt = 1
            elif M_arr[t] >= -exit_level:
                tgt = 0
            else:
                tgt = p
        pend = tgt
    return pos_seq


def _onelot_exec(pos_seq, comm, pv, ticks=1):
    """Verbatim health_substrate.py / substrate.py onelot_exec, generalized with `ticks`."""
    cash = 0.0; p = 0; prev_eq = 0.0
    bar_pos = np.zeros(N, dtype=int)
    bar_pnl = np.zeros(N)
    for t in range(N):
        tgt = int(pos_seq[t])
        if tgt != p:
            d = tgt - p
            side = 1 if d > 0 else -1
            if LAST[t]:
                px = _fill_n(OPEN_[t], HIGH[t], LOW[t], side, ticks=ticks, at_close=CLOSE[t])
            else:
                px = _fill_n(OPEN_[t], HIGH[t], LOW[t], side, ticks=ticks)
            cash -= d * px * pv
            cash -= abs(d) * comm
            p = tgt
        eq = cash + p * CLOSE[t] * pv
        bar_pnl[t] = eq - prev_eq; prev_eq = eq
        bar_pos[t] = p
    return bar_pos, bar_pnl


def product_b_exec(T, ticks=1, comm=COMM_NQ, pv=PV_NQ):
    m_arr = np.where((T != 0) & (TILT_STATE != 0) & (np.sign(T) == TILT_STATE), TILTMULT, 1.0)
    Tp = np.clip(rha(T * m_arr * TILTRESCALE), -13, 13)
    M = WSOLAR * Tp + WBMOM * np.asarray(B_LEG)
    pos_seq = _build_pos_seq(M)
    bar_pos, bar_pnl = _onelot_exec(pos_seq, comm, pv, ticks=ticks)
    return pos_seq, bar_pos, bar_pnl, M


# ------------------------------------------------------------------------- reporting helpers
def daily_net(bar_pnl, mask):
    """Group bar-level P&L into per-session daily net, restricted to `mask`."""
    s = pd.Series(np.asarray(bar_pnl)[mask], index=pd.Index(SD[mask], name="sess"))
    return s.groupby(level=0).sum().sort_index()


def battery(bar_pnl, mask, label=""):
    d = daily_net(bar_pnl, mask)
    if len(d) == 0:
        return {"label": label, "n_days": 0, "net": 0.0}
    return dd_battery(pd.to_datetime(d.index), d.to_numpy(), label=label)


CANON_MASK = ((SESS_DT >= CANON_START) & (SESS_DT <= CANON_END)).to_numpy()
FULL_MASK = np.ones(N, dtype=bool)
DEV_MASK = (SESS_DT <= DEV_END).to_numpy()   # certified-net gate window only


# ------------------------------------------------------------------------- self-check
# Confirms this module reproduces the repo's own certified dev-window (2022-01-03..2026-05-31)
# nets EXACTLY on the incumbent grid (G13 = sm.VMS) before any GRID01/GRID02 result is trusted.
print("[grid_core] self-check: incumbent grid (G13) vs certified dev-window nets ...", flush=True)
_PEND0, _T0, _consensus0 = build_grid(list(sm.VMS))
_, _bpnl_A0, _ = product_a_exec(_T0, ticks=1)
_, _, _bpnl_B0, _ = product_b_exec(_T0, ticks=1)
_netA0 = float(_bpnl_A0[DEV_MASK].sum())
_netB0 = float(_bpnl_B0[DEV_MASK].sum())
assert abs(_netA0 - 177924.40) < 1.0, f"grid_core Product-A G13 dev-window net mismatch: {_netA0}"
assert abs(_netB0 - 301915.92) < 1.0, f"grid_core Product-B G13 dev-window net mismatch: {_netB0}"
print(f"[grid_core] SELF-CHECK PASSED: G13 dev-window net reproduces certified values exactly "
      f"(Product A={_netA0:.2f}, Product B={_netB0:.2f})", flush=True)

INCUMBENT_VMS = list(sm.VMS)

if __name__ == "__main__":
    print("grid_core self-test OK")
