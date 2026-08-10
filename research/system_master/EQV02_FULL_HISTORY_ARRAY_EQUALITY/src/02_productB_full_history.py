#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EQV02 -- Product B FULL-HISTORY ARRAY EQUALITY.

Gated on EQV01 (research/system_master/EQV01_BEHAVIORAL_CANONICALIZATION/REPORT.md), which
proved Product B's single-step decoder+hysteresis equivalence EXACT over the full 729-state
reachable domain (sumNext x tiltState x bmomPos x priorPosition), with forceFlat/entryBlocked
held FALSE throughout (explicitly out of EQV01's scope).

THIS SCRIPT tests the genuinely new ground: a TIME-SEQUENCED, bar-by-bar walk through real
NQ 3-minute market data (not a finite-state enumeration), replaying the FULL operational
overlay -- forceFlat / entryBlocked session-timing gates, hysteresis carry-over across bars,
member-ensemble and B-MOM state persistence across session boundaries -- for both:

  CURRENT_FORM   : the real code's own M = WSolar*Tp + WBmom*bmomPos, hysteresis(EntryLevel=3.0,
                   ExitLevel=1.0) on M, forceFlat/entryBlocked exactly as coded
                   (src/ninjascript/SolarWaveOneContractNQ_v5.cs lines 224-448, re-read this
                   session and ported here bar-for-bar, control-flow-for-control-flow).
  CANONICAL_FORM : Q_B = Tp + 4*bmomPos (always integer), hysteresis(entry=5, exit=1) on Q_B,
                   the IDENTICAL forceFlat/entryBlocked boolean arrays applied with the
                   identical if/elif control-flow shape (CANONICAL_MATHEMATICAL_SPEC.md).

Ground truth re-read directly from src/ninjascript/SolarWaveOneContractNQ_v5.cs this session:
  TiltSma=50 TiltMult=1.25 TiltRescale=0.9026 WSolar=0.7086 WBmom=2.83 BmomBandDays=14
  EntryLevel=3.0 ExitLevel=1.0 (frozen seq-318) EntryBlockMinutesBeforeClose=30
  ForcedFlatMinutesBeforeClose=21 VolPeriod=460 SMinTicks=40 SMaxTicks=1200 StopMultiplier=179
  (fallback) BarsRequiredToTrade=20. VolMults = {6,8,...,30} (13 members).

PIPELINE REUSE ("same pipeline as Product A", per task instruction):
  - Raw bars: runs/AUDIT03_BARS/nq_3m_2022_2026.csv -- NT8-exported "NQ 09-26" 3-minute bars,
    2022-01-02..2026-07-31 (matches SolarWaveOneContractNQ_v5.cs's own SignalInstrument =
    "NQ 09-26"; ends before the 2026-08-01 LOCKED_FORWARD boundary -- asserted below).
  - 13-member trend-follower ensemble (UpdateMachine/Decide, .cs lines 224-255): reused from
    src/analytics/sm01_solarsim.py (member_states/member_trades) + runs/W18R1_M1_VOLSEASON/
    src/common.py (build_pend) -- the campaign's own validated port of this exact state
    machine (VolMults, SMinTicks/SMaxTicks/VolPeriod/StopMultiplier-fallback/
    BarsRequiredToTrade all match SolarWaveOneContractNQ_v5.cs's SetDefaults exactly). This
    reuse was spot-checked line-by-line against the .cs UpdateMachine/Decide functions during
    this session (anchor/is_up flip logic, xl exit threshold, session-close hard reset,
    "no new entry decided on the session's last bar" -- all confirmed structurally identical).
    sumNext[t] = sum of the 13 members' pending-position array at bar t (always in [-13,13]
    by construction: 13 members each in {-1,0,1}).
  - B-MOM (BmomBar/EndRthDay, .cs lines 257-305): NOT reused from health_substrate.py or any
    other prior script. Freshly bar-by-bar ported in THIS file directly from the .cs source
    re-read this session (see build_bmom_pos() below), including the v4 fix (bmomPos also
    flattens on the session's own last bar, not only hm>=155700).
  - tiltState: FRESHLY, LOCALLY computed in THIS file per Product B's own ">" convention
    (sessCloses.Count > TiltSma, .cs line 396), matching CANONICAL_MATHEMATICAL_SPEC.md's
    disclosed asymmetry. Deliberately NOT the shared health_substrate.py array (which reuses
    a single ">="-convention tilt_state array, flagged in EQV01 REPORT.md sec. "Cross-cutting
    notes" as an out-of-scope, previously undisclosed mismatch versus Product B's real code).
  - Operational overlay (forceFlat/entryBlocked/hysteresis, .cs lines 405-448): freshly
    bar-by-bar ported in THIS file, control-flow-for-control-flow (see hysteresis_walk()).

MNQ SIBLING: src/ninjascript/SolarWaveOneContractMNQ_v5.cs was diffed against the NQ file
byte-for-byte during this session (see report). The two files are IDENTICAL in every formula,
threshold, and control-flow branch of the decision layer (member ensemble, BmomBar, tiltState,
T/mm/Tp/M, Q_B, hysteresis, forceFlat/entryBlocked) -- MNQ_v5 differs ONLY in which BarsArray
index plays "signal" vs "execution" role (a wiring/instrument difference orthogonal to the
math under test here), consistent with "prior sessions' verification" that decision logic is
shared. This script tests the NQ object only; the MNQ sibling was spot-checked via diff, not
independently re-run bar-by-bar.

DATA-QUALITY CAVEAT CARRIED FORWARD (previously disclosed, not a new EQV02 finding): the NQ
09-26 3-minute series has a genuine feed gap on 2023-04-05 (bars jump 14:03 -> 20:03;
documented in runs/W17_C4_COMPLIANCE/src/v1d_late_entries.py PART 0). NT8's own
IsFirstBarOfSession/IsLastBarOfSession flags (exported verbatim into first_bar_of_session)
misread this gap as an early session close. Because sessionEndTs/forceFlat/entryBlocked and
the member/tiltState/BmomBar session-end reset are ALL driven off the SAME
IsFirstBarOfSession/IsLastBarOfSession signal in the real .cs, this script's data-driven
session grouping reproduces the REAL incumbent's own (bug-and-all) historical behavior on
that date exactly -- it is not a divergence introduced by this script. Because CURRENT_FORM
and CANONICAL_FORM consume the identical forceFlat/entryBlocked/sessEnd boolean arrays, this
artifact cannot by itself cause the two forms to disagree with each other (it can only affect
whether either form matches literal real-NT8 trade timestamps, which is not what is being
tested here).

Outputs: research/system_master/EQV02_FULL_HISTORY_ARRAY_EQUALITY/out/productB_array_equality.json
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "runs", "W18R1_M1_VOLSEASON", "src"))
import sm01_solarsim as sm          # noqa: E402  -- validated member-ensemble simulator
import common as C1                 # noqa: E402  -- build_pend()

OUT_DIR = Path(ROOT) / "research" / "system_master" / "EQV02_FULL_HISTORY_ARRAY_EQUALITY" / "out"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BARS_PATH = os.path.join(ROOT, "runs", "AUDIT03_BARS", "nq_3m_2022_2026.csv")

LOCKED_FORWARD = pd.Timestamp("2026-08-01T00:00:00Z")
CANON_START_UTC = pd.Timestamp("2023-01-01T06:00:00Z")
CANON_END_UTC = pd.Timestamp("2025-02-02T22:59:59Z")

# ---------------------------------------------------------------------------------------
# Constants -- re-verified against src/ninjascript/SolarWaveOneContractNQ_v5.cs this session
# (SetDefaults block, lines 143-146, and the ops-clock constants, lines 82-84).
# ---------------------------------------------------------------------------------------
TILT_SMA = 50
TILT_MULT = 1.25
TILT_RESCALE = 0.9026
W_SOLAR = 0.7086
W_BMOM = 2.83
ENTRY_LEVEL = 3.0
EXIT_LEVEL = 1.0
BMOM_BAND_DAYS = 14
ENTRY_BLOCK_MIN = 30
FORCED_FLAT_MIN = 21
BARS_REQUIRED = 20
VOL_PERIOD = 460
SMIN_TICKS = 40.0
SMAX_TICKS = 1200.0

CANON_Q_ENTRY = 5.0
CANON_Q_EXIT = 1.0
CANON_BMOM_COEF = 4.0


def rha(x):
    """C# Math.Round(x, MidpointRounding.AwayFromZero) to 0 digits, vectorized."""
    return np.sign(x) * np.floor(np.abs(x) + 0.5)


def sha256_of(obj) -> str:
    b = json.dumps(obj, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(b).hexdigest()


def sha256_of_intarray(arr: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(arr, dtype=np.int8).tobytes()).hexdigest()


# =========================================================================================
# 1. Load raw bars + build sumNext (13-member ensemble), byte-for-byte structural match to
#    UpdateMachine()/Decide() (.cs lines 224-255).
# =========================================================================================
def load_bars() -> pd.DataFrame:
    bars = sm.load_bars_3m(BARS_PATH)
    bars["time"] = pd.to_datetime(bars["time"])
    assert bars["time"].max() < LOCKED_FORWARD.tz_localize(None), (
        "raw bar file reaches >= 2026-08-01 LOCKED_FORWARD -- must not be read"
    )
    bars["sess_end_ts"] = bars.groupby("sess_id")["time"].transform("max")
    return bars


def build_sumNext(bars: pd.DataFrame) -> np.ndarray:
    close = bars["close"].to_numpy()
    sig = sm.sigma_series(close, vol_period=VOL_PERIOD, min_count=30)
    PEND = C1.build_pend(bars, sig, smin_ticks=SMIN_TICKS, smax_ticks=SMAX_TICKS)
    # sanity: build_pend uses the SAME BarsRequiredToTrade(=20)/VolPeriod/SMin/SMax defaults
    # as SolarWaveOneContractNQ_v5.cs's SetDefaults -- confirmed by reading
    # runs/W18R1_M1_VOLSEASON/src/common.py::build_pend -> sm.member_trades(bars_required=20)
    # default, matching .cs BarsRequiredToTrade=20 exactly.
    sumNext = PEND.sum(axis=1)
    return sumNext.astype(int)


# =========================================================================================
# 2. tiltState -- Product B's LOCAL ">" convention (.cs lines 393-402), freshly built here,
#    NOT reused from health_substrate.py's shared ">="-convention array.
# =========================================================================================
def build_tiltState_productB(bars: pd.DataFrame) -> np.ndarray:
    n = len(bars)
    is_last = bars["is_last_of_sess"].to_numpy()
    close = bars["close"].to_numpy()
    tiltState = np.zeros(n, dtype=np.int64)
    sess_closes: list[float] = []
    cur_tilt = 0
    for t in range(n):
        if is_last[t]:
            sess_closes.append(float(close[t]))
            # .cs: if (sessCloses.Count > TiltSma) -- strict ">", NOT ">=" (Product A's
            # convention, which the shared health_substrate.py array uses instead).
            if len(sess_closes) > TILT_SMA:
                window = sess_closes[-TILT_SMA:]
                s = sum(window)
                cur_tilt = int(np.sign(close[t] - s / TILT_SMA))
            if len(sess_closes) > 600:
                sess_closes.pop(0)
        # tiltState used for THIS bar's own mm/Tp/M (sessEnd block runs before the M
        # computation in the same OnBarUpdate call, .cs lines 392-410) -- so a just-updated
        # value on a sessEnd bar applies starting at that SAME bar, not the next one.
        tiltState[t] = cur_tilt
    return tiltState


# =========================================================================================
# 3. bmomPos -- fresh bar-by-bar port of BmomBar()/EndRthDay() (.cs lines 257-305), including
#    the v4 fix (bmomPos also flattens on sessEnd, not just hm>=155700).
# =========================================================================================
def build_bmom_pos(bars: pd.DataFrame) -> np.ndarray:
    n = len(bars)
    tcol = bars["time"]
    hm = (tcol.dt.hour * 10000 + tcol.dt.minute * 100).to_numpy()
    is_last = bars["is_last_of_sess"].to_numpy()
    openp = bars["open"].to_numpy()
    close = bars["close"].to_numpy()
    vol = bars["volume"].to_numpy()

    B = np.zeros(n, dtype=np.int64)

    rth_open = False
    open0930 = 0.0
    vwapPV = 0.0
    vwapV = 0.0
    today_slots: dict[int, float] = {}
    slot_hist: dict[int, list[float]] = {}
    rth_day_count = 0
    bmom_pos = 0

    def end_rth_day():
        nonlocal rth_open, rth_day_count
        if not rth_open:
            return
        for k, v in today_slots.items():
            lst = slot_hist.setdefault(k, [])
            lst.append(v)
            if len(lst) > 60:
                lst.pop(0)
        rth_day_count += 1
        rth_open = False

    for t in range(n):
        h = int(hm[t])
        sess_end = bool(is_last[t])

        if h == 93300:
            open0930 = float(openp[t])
            vwapPV = 0.0
            vwapV = 0.0
            rth_open = True
            today_slots.clear()
            bmom_pos = 0

        if (not rth_open) or h < 93300 or h > 160000:
            if sess_end:
                end_rth_day()
            B[t] = bmom_pos
            continue

        c = float(close[t])
        v = float(vol[t])
        vwapPV += c * v
        vwapV += v
        vwap = vwapPV / vwapV if vwapV > 0 else c
        today_slots[h] = abs(c - open0930)

        if h <= 155400 and rth_day_count >= BMOM_BAND_DAYS:
            past = slot_hist.get(h)
            if past is not None and len(past) >= 1:
                k = min(BMOM_BAND_DAYS, len(past))
                m_tod = sum(past[-k:]) / k
                upper = open0930 + m_tod
                lower = open0930 - m_tod
                sig = 0
                if c > max(upper, vwap):
                    sig = 1
                elif c < min(lower, vwap):
                    sig = -1
                if sig != 0:
                    bmom_pos = sig

        if h >= 155700 or sess_end:
            bmom_pos = 0

        if sess_end:
            end_rth_day()

        B[t] = bmom_pos

    return B


# =========================================================================================
# 4. Decoder: T, mm, Tp, M, Q_B -- exact .cs formulas (lines 405-410), vectorized.
# =========================================================================================
def build_decoder(sumNext: np.ndarray, tiltState: np.ndarray, B: np.ndarray):
    T = np.clip(rha(sumNext / 13.0 * 10.0), -10, 10).astype(int)
    mm = np.where(
        (sumNext != 0) & (tiltState != 0) & (np.sign(sumNext) == tiltState),
        TILT_MULT, 1.0,
    )
    Tp = np.clip(rha(T * mm * TILT_RESCALE), -13, 13).astype(int)
    M = W_SOLAR * Tp + W_BMOM * B
    Q_B = Tp + CANON_BMOM_COEF * B
    return T, mm, Tp, M, Q_B


# =========================================================================================
# 5. Operational overlay: forceFlat / entryBlocked (.cs lines 416-422), exact.
# =========================================================================================
def build_gates(bars: pd.DataFrame):
    now_ts = bars["time"]
    sess_end_ts = bars["sess_end_ts"]
    entry_blocked = (now_ts >= sess_end_ts - pd.Timedelta(minutes=ENTRY_BLOCK_MIN)).to_numpy()
    force_flat = (now_ts >= sess_end_ts - pd.Timedelta(minutes=FORCED_FLAT_MIN)).to_numpy()
    return entry_blocked, force_flat


# =========================================================================================
# 6. The hysteresis state-machine walk itself -- .cs lines 424-448, control-flow-for-
#    control-flow (elif chain, exactly). Used for BOTH CURRENT_FORM (signal=M,
#    entry=3.0/exit=1.0) and CANONICAL_FORM (signal=Q_B, entry=5/exit=1), so any
#    forceFlat/entryBlocked-interaction subtlety (e.g. a blocked reversal silently
#    downgrading to a plain exit, since M<=-EntryLevel implies M<=ExitLevel too) applies
#    identically to both forms by construction, not by assumption.
# =========================================================================================
def hysteresis_walk(signal: np.ndarray, entry: float, exit_: float,
                     force_flat: np.ndarray, entry_blocked: np.ndarray,
                     times: np.ndarray):
    n = len(signal)
    pos = np.zeros(n, dtype=np.int8)
    events = []  # dict per position-change event
    p = 0
    for t in range(n):
        ff = bool(force_flat[t])
        eb = bool(entry_blocked[t])
        s = signal[t]
        tgt = p
        if ff:
            tgt = 0
        elif p == 0:
            if not eb:
                if s >= entry:
                    tgt = 1
                elif s <= -entry:
                    tgt = -1
        elif p > 0:
            if s <= -entry and not eb:
                tgt = -1
            elif s <= exit_:
                tgt = 0
        else:
            if s >= entry and not eb:
                tgt = 1
            elif s >= -exit_:
                tgt = 0
        pos[t] = tgt
        if tgt != p:
            if p == 0:
                kind = "entry"
            elif tgt == 0:
                kind = "exit"
            else:
                kind = "reversal"
            events.append({
                "bar": int(t), "time": str(times[t]),
                "kind": kind, "from_pos": int(p), "to_pos": int(tgt),
                "direction": int(np.sign(tgt)) if tgt != 0 else int(np.sign(p)) * -1 if p != 0 else 0,
                "quantity": int(tgt) if tgt != 0 else int(-p),
                "forceFlat": ff, "entryBlocked": eb,
            })
        p = tgt
    return pos, events


# =========================================================================================
def main():
    print("[EQV02-B] loading raw NQ 3-min bars ...", flush=True)
    bars = load_bars()
    n = len(bars)
    print(f"[EQV02-B] {n} bars loaded, {bars['time'].min()} .. {bars['time'].max()}", flush=True)

    print("[EQV02-B] building 13-member ensemble -> sumNext ...", flush=True)
    sumNext = build_sumNext(bars)

    print("[EQV02-B] building Product-B-local tiltState (>' convention) ...", flush=True)
    tiltState = build_tiltState_productB(bars)

    print("[EQV02-B] building bmomPos (fresh BmomBar/EndRthDay port) ...", flush=True)
    B = build_bmom_pos(bars)

    print("[EQV02-B] decoding T/mm/Tp/M/Q_B ...", flush=True)
    T, mm, Tp, M, Q_B = build_decoder(sumNext, tiltState, B)

    print("[EQV02-B] building forceFlat/entryBlocked gates ...", flush=True)
    entry_blocked, force_flat = build_gates(bars)

    times = bars["time"].to_numpy()

    # -------------------------------------------------------------------------------
    # DOMAIN CHECK -- is every historical (sumNext, tiltState, bmomPos) state inside
    # EQV01's enumerated 729-state domain (sumNext in [-13,13], tiltState in {-1,0,1},
    # bmomPos in {-1,0,1})? Any violation is a MORE important finding than an array
    # mismatch (it would mean EQV01's "exhaustive" claim was wrong).
    # -------------------------------------------------------------------------------
    out_of_domain = []
    bad_sumNext = np.where((sumNext < -13) | (sumNext > 13))[0]
    bad_tilt = np.where(~np.isin(tiltState, [-1, 0, 1]))[0]
    bad_B = np.where(~np.isin(B, [-1, 0, 1]))[0]
    for idx, arrname, arr in [("sumNext", "sumNext", bad_sumNext),
                               ("tiltState", "tiltState", bad_tilt),
                               ("bmomPos", "B", bad_B)]:
        if len(arr) > 0:
            out_of_domain.append({
                "field": idx, "n_violations": int(len(arr)),
                "example_bars": [int(x) for x in arr[:10]],
                "example_times": [str(times[x]) for x in arr[:10]],
            })
    domain_clean = (len(out_of_domain) == 0)
    print(f"[EQV02-B] domain check: sumNext/tiltState/bmomPos all within EQV01's 729-state "
          f"domain = {domain_clean}", flush=True)

    # -------------------------------------------------------------------------------
    # CURRENT_FORM and CANONICAL_FORM walks, full extended history (2022-01..2026-07).
    # -------------------------------------------------------------------------------
    print("[EQV02-B] walking CURRENT_FORM (M, hysteresis(3.0,1.0)) ...", flush=True)
    pos_current_full, ev_current_full = hysteresis_walk(
        M, ENTRY_LEVEL, EXIT_LEVEL, force_flat, entry_blocked, times)

    print("[EQV02-B] walking CANONICAL_FORM (Q_B, hysteresis(5,1)) ...", flush=True)
    pos_canonical_full, ev_canonical_full = hysteresis_walk(
        Q_B, CANON_Q_ENTRY, CANON_Q_EXIT, force_flat, entry_blocked, times)

    # -------------------------------------------------------------------------------
    # RAW walks -- pure decoder+hysteresis, forceFlat/entryBlocked held OFF throughout
    # (EQV01's own scope), but now as a genuine TIME-SEQUENCED carry-over walk over real
    # data rather than a single-step finite-state enumeration. Isolates "does the
    # sequential carry-over of p across bars, by itself, ever break the equivalence"
    # from "does adding the forceFlat/entryBlocked overlay break it".
    # -------------------------------------------------------------------------------
    no_gate = np.zeros(n, dtype=bool)
    print("[EQV02-B] walking RAW (gates off) CURRENT_FORM ...", flush=True)
    pos_current_raw, ev_current_raw = hysteresis_walk(
        M, ENTRY_LEVEL, EXIT_LEVEL, no_gate, no_gate, times)
    print("[EQV02-B] walking RAW (gates off) CANONICAL_FORM ...", flush=True)
    pos_canonical_raw, ev_canonical_raw = hysteresis_walk(
        Q_B, CANON_Q_ENTRY, CANON_Q_EXIT, no_gate, no_gate, times)

    # domain check on priorPosition actually realized (should be trivially {-1,0,1})
    assert set(np.unique(pos_current_full)).issubset({-1, 0, 1})
    assert set(np.unique(pos_canonical_full)).issubset({-1, 0, 1})

    # -------------------------------------------------------------------------------
    # Canonical-window slice (2023-01-01T06:00:00Z .. 2025-02-02T22:59:59Z), converted to
    # ET (bar timestamps are exchange-session/ET-naive, per CLAUDE.md convention).
    # -------------------------------------------------------------------------------
    canon_start_et = CANON_START_UTC.tz_convert("America/New_York").tz_localize(None)
    canon_end_et = CANON_END_UTC.tz_convert("America/New_York").tz_localize(None)
    tser = bars["time"]
    canon_mask = ((tser >= canon_start_et) & (tser <= canon_end_et)).to_numpy()
    n_canon = int(canon_mask.sum())
    canon_idx = np.where(canon_mask)[0]
    print(f"[EQV02-B] canonical window ET bounds: {canon_start_et} .. {canon_end_et} "
          f"-> {n_canon} bars, {bars.loc[canon_mask, 'sess_date'].nunique()} sessions", flush=True)

    def slice_events(events, idx_set):
        lo, hi = idx_set.min(), idx_set.max()
        return [e for e in events if lo <= e["bar"] <= hi]

    pos_current_canon = pos_current_full[canon_mask]
    pos_canonical_canon = pos_canonical_full[canon_mask]
    ev_current_canon = slice_events(ev_current_full, canon_idx)
    ev_canonical_canon = slice_events(ev_canonical_full, canon_idx)

    # -------------------------------------------------------------------------------
    # Comparison + hashing -- CANONICAL WINDOW (primary, required verdict).
    # -------------------------------------------------------------------------------
    def compare(pos_a, pos_b, ev_a, ev_b, label):
        mism_mask = (pos_a != pos_b)
        n_mism = int(mism_mask.sum())
        first_mism = None
        if n_mism > 0:
            fi = int(np.where(mism_mask)[0][0])
            first_mism = {
                "array_index_within_slice": fi,
            }
        ev_a_compact = [(e["bar"], e["kind"], e["from_pos"], e["to_pos"]) for e in ev_a]
        ev_b_compact = [(e["bar"], e["kind"], e["from_pos"], e["to_pos"]) for e in ev_b]
        return {
            "label": label,
            "n_bars": int(len(pos_a)),
            "n_mismatched_bars": n_mism,
            "pct_match": float(1.0 - n_mism / max(1, len(pos_a))),
            "raw_array_hash_equal": sha256_of_intarray(pos_a) == sha256_of_intarray(pos_b),
            "hash_current_pos": sha256_of_intarray(pos_a),
            "hash_canonical_pos": sha256_of_intarray(pos_b),
            "event_sequence_equal": ev_a_compact == ev_b_compact,
            "hash_current_events": sha256_of(ev_a_compact),
            "hash_canonical_events": sha256_of(ev_b_compact),
            "n_events_current": len(ev_a), "n_events_canonical": len(ev_b),
            "first_mismatch": first_mism,
        }

    canon_cmp = compare(pos_current_canon, pos_canonical_canon,
                        ev_current_canon, ev_canonical_canon, "CANONICAL_WINDOW_OPERATIONAL")
    full_cmp = compare(pos_current_full, pos_canonical_full,
                       ev_current_full, ev_canonical_full, "FULL_HISTORY_OPERATIONAL_2022_2026")

    pos_current_raw_canon = pos_current_raw[canon_mask]
    pos_canonical_raw_canon = pos_canonical_raw[canon_mask]
    ev_current_raw_canon = slice_events(ev_current_raw, canon_idx)
    ev_canonical_raw_canon = slice_events(ev_canonical_raw, canon_idx)
    canon_raw_cmp = compare(pos_current_raw_canon, pos_canonical_raw_canon,
                            ev_current_raw_canon, ev_canonical_raw_canon,
                            "CANONICAL_WINDOW_RAW_GATES_OFF")
    full_raw_cmp = compare(pos_current_raw, pos_canonical_raw,
                           ev_current_raw, ev_canonical_raw,
                           "FULL_HISTORY_RAW_GATES_OFF_2022_2026")

    # -------------------------------------------------------------------------------
    # Root-cause investigation for ANY mismatch found (canonical window first, then full).
    # -------------------------------------------------------------------------------
    def investigate(pos_a_full, pos_b_full, mask, offset_idx):
        """mask/offset_idx select the slice under test within the FULL arrays."""
        sub_a = pos_a_full[offset_idx]
        sub_b = pos_b_full[offset_idx]
        mism = np.where(sub_a != sub_b)[0]
        report = []
        for j in mism[:25]:  # cap detail list
            gi = int(offset_idx[j])  # global bar index in the full arrays
            prior_a = int(pos_a_full[gi - 1]) if gi > 0 else 0
            prior_b = int(pos_b_full[gi - 1]) if gi > 0 else 0
            report.append({
                "global_bar_index": gi,
                "time": str(times[gi]),
                "sumNext": int(sumNext[gi]), "tiltState": int(tiltState[gi]), "bmomPos": int(B[gi]),
                "prior_pos_current": prior_a, "prior_pos_canonical": prior_b,
                "priors_agree": prior_a == prior_b,
                "T": int(T[gi]), "Tp": int(Tp[gi]), "M": round(float(M[gi]), 6),
                "Q_B": float(Q_B[gi]),
                "forceFlat": bool(force_flat[gi]), "entryBlocked": bool(entry_blocked[gi]),
                "pos_current": int(pos_a_full[gi]), "pos_canonical": int(pos_b_full[gi]),
            })
        return report

    canon_mismatch_detail = investigate(pos_current_full, pos_canonical_full,
                                        canon_mask, canon_idx) if canon_cmp["n_mismatched_bars"] else []
    full_mismatch_detail = investigate(pos_current_full, pos_canonical_full,
                                       np.ones(n, dtype=bool), np.arange(n)) \
        if full_cmp["n_mismatched_bars"] else []

    # For every mismatch where priors agree, cross-check against EQV01's OWN proven
    # single-step decoder equivalence at that exact (sumNext,tiltState,bmomPos,priorPos)
    # tuple -- if EQV01 already covered that tuple and found a match, a mismatch here with
    # agreeing priors would indicate a bug in THIS script, not a genuine new divergence.
    def eqv01_single_step_check(sumNext_v, tilt_v, B_v, p):
        """Re-derive both forms' single-bar decision exactly as EQV01's 02_eqv_productB.py
        did (forceFlat=entryBlocked=False, matching EQV01's own scope), for cross-reference
        only -- NOT a substitute for the real forceFlat/entryBlocked-aware bar under test."""
        T_v = int(np.clip(rha(sumNext_v / 13.0 * 10.0), -10, 10))
        mm_v = TILT_MULT if (sumNext_v != 0 and tilt_v != 0 and np.sign(sumNext_v) == tilt_v) else 1.0
        Tp_v = int(np.clip(rha(T_v * mm_v * TILT_RESCALE), -13, 13))
        M_v = W_SOLAR * Tp_v + W_BMOM * B_v
        Q_v = Tp_v + CANON_BMOM_COEF * B_v

        def step(s, entry, ex, pp):
            if pp == 0:
                if s >= entry: return 1
                if s <= -entry: return -1
                return 0
            elif pp > 0:
                if s <= -entry: return -1
                if s <= ex: return 0
                return pp
            else:
                if s >= entry: return 1
                if s >= -ex: return 0
                return pp

        nm = step(M_v, ENTRY_LEVEL, EXIT_LEVEL, p)
        nq = step(Q_v, CANON_Q_ENTRY, CANON_Q_EXIT, p)
        return nm == nq, nm, nq

    for rec in canon_mismatch_detail + full_mismatch_detail:
        if rec["priors_agree"]:
            ok, nm, nq = eqv01_single_step_check(rec["sumNext"], rec["tiltState"], rec["bmomPos"],
                                                  rec["prior_pos_current"])
            rec["eqv01_single_step_cross_check"] = {
                "would_match_with_gates_false": ok,
                "M_hysteresis_result": nm, "Q_B_hysteresis_result": nq,
            }

    # -------------------------------------------------------------------------------
    # entryBlocked / forceFlat coverage stats -- did the walk actually exercise the
    # genuinely-new overlay ground (not just trivially forceFlat=entryBlocked=False bars)?
    # -------------------------------------------------------------------------------
    overlay_stats = {
        "canonical_window": {
            "n_bars": n_canon,
            "n_entryBlocked_bars": int(entry_blocked[canon_mask].sum()),
            "n_forceFlat_bars": int(force_flat[canon_mask].sum()),
            "n_entryBlocked_not_forceFlat_bars": int((entry_blocked[canon_mask] & ~force_flat[canon_mask]).sum()),
        },
        "full_history": {
            "n_bars": n,
            "n_entryBlocked_bars": int(entry_blocked.sum()),
            "n_forceFlat_bars": int(force_flat.sum()),
            "n_entryBlocked_not_forceFlat_bars": int((entry_blocked & ~force_flat).sum()),
        },
    }

    # count how many CURRENT_FORM position-change events occurred while entryBlocked=True
    # (the "blocked reversal downgrades to plain exit" pattern) -- descriptive, not a defect.
    blocked_exit_events = [e for e in ev_current_full if e["entryBlocked"] and e["kind"] == "exit"]
    overlay_stats["current_form_exit_events_during_entryBlocked_full_history"] = len(blocked_exit_events)

    # -------------------------------------------------------------------------------
    # tiltState '>' vs '>=' warm-up divergence window (expected, immaterial to canonical
    # window per EQV01's own characterization) -- explicitly located and reported here.
    # -------------------------------------------------------------------------------
    is_last = bars["is_last_of_sess"].to_numpy()
    sess_close_bar_idx = np.where(is_last)[0]
    ge_convention_first_active_session = TILT_SMA  # 0-indexed session count == 50 -> >=50 true
    gt_convention_first_active_session = TILT_SMA + 1  # count == 51 -> >50 true
    tilt_warmup_note = {
        "ge_convention_(shared_health_substrate)_first_nonzero_eligible_at_session_index_0based": ge_convention_first_active_session,
        "gt_convention_(productB_real_code, this_script)_first_nonzero_eligible_at_session_index_0based": gt_convention_first_active_session,
        "n_sessions_of_divergence_window": gt_convention_first_active_session - ge_convention_first_active_session,
        "divergence_window_bar_range": [int(sess_close_bar_idx[ge_convention_first_active_session])
                                        if len(sess_close_bar_idx) > ge_convention_first_active_session else None,
                                        int(sess_close_bar_idx[gt_convention_first_active_session])
                                        if len(sess_close_bar_idx) > gt_convention_first_active_session else None],
        "divergence_window_time_range": [
            str(times[sess_close_bar_idx[ge_convention_first_active_session]])
            if len(sess_close_bar_idx) > ge_convention_first_active_session else None,
            str(times[sess_close_bar_idx[gt_convention_first_active_session]])
            if len(sess_close_bar_idx) > gt_convention_first_active_session else None,
        ],
        "falls_within_canonical_window": False,  # both land in ~Feb-Mar 2022, far before 2023-01-01
    }

    # -------------------------------------------------------------------------------
    # 2023-04-05 data-gap note -- confirm it exists in this pipeline's session grouping too,
    # and confirm it falls inside the canonical window (previously disclosed, not new).
    # -------------------------------------------------------------------------------
    gap_mask = (bars["time"] >= pd.Timestamp("2023-04-05T13:30:00")) & \
               (bars["time"] <= pd.Timestamp("2023-04-05T20:10:00"))
    gap_bars = bars.loc[gap_mask, ["time", "first_bar_of_session", "is_last_of_sess"]]
    known_gap_note = {
        "description": ("NQ 09-26 3-min feed gap 2023-04-05 14:03->20:03 ET, previously "
                        "disclosed in runs/W17_C4_COMPLIANCE/src/v1d_late_entries.py PART 0. "
                        "NT8's own IsFirstBarOfSession/IsLastBarOfSession misreads it as an "
                        "early session close; this script's session grouping (driven off the "
                        "same first_bar_of_session/is_last_of_sess columns) reproduces that "
                        "real incumbent behavior rather than diverging from it. Affects "
                        "CURRENT_FORM and CANONICAL_FORM identically (shared forceFlat/"
                        "entryBlocked/sessEnd inputs) so cannot by itself cause a mismatch "
                        "between the two forms."),
            "falls_within_canonical_window": bool(
            (pd.Timestamp("2023-04-05") >= canon_start_et) and
            (pd.Timestamp("2023-04-05") <= canon_end_et)),
        "bars_around_gap": gap_bars.astype(str).to_dict("records"),
    }

    # -------------------------------------------------------------------------------
    # Assemble + write report.
    # -------------------------------------------------------------------------------
    report = {
        "meta": {
            "task": "EQV02 -- Product B full-history array equality: CURRENT_FORM (real M-"
                    "hysteresis(3,1)+forceFlat/entryBlocked) vs CANONICAL_FORM "
                    "(Q_B=Tp+4*bmomPos, hysteresis(5,1), same gates)",
            "gated_on": "research/system_master/EQV01_BEHAVIORAL_CANONICALIZATION/REPORT.md "
                       "(Product B: 729/729 EXACT_EQUIVALENCE, forceFlat/entryBlocked=False)",
            "constants": {
                "TiltSma": TILT_SMA, "TiltMult": TILT_MULT, "TiltRescale": TILT_RESCALE,
                "WSolar": W_SOLAR, "WBmom": W_BMOM, "EntryLevel": ENTRY_LEVEL,
                "ExitLevel": EXIT_LEVEL, "BmomBandDays": BMOM_BAND_DAYS,
                "EntryBlockMinutesBeforeClose": ENTRY_BLOCK_MIN,
                "ForcedFlatMinutesBeforeClose": FORCED_FLAT_MIN,
                "BarsRequiredToTrade": BARS_REQUIRED, "VolPeriod": VOL_PERIOD,
                "SMinTicks": SMIN_TICKS, "SMaxTicks": SMAX_TICKS,
                "canonical_form": {"Q_B_entry": CANON_Q_ENTRY, "Q_B_exit": CANON_Q_EXIT,
                                   "bmom_coef": CANON_BMOM_COEF},
            },
            "data_source": BARS_PATH,
            "data_range": [str(bars["time"].min()), str(bars["time"].max())],
            "n_bars_full_history": int(n),
            "canonical_window_utc": [str(CANON_START_UTC), str(CANON_END_UTC)],
            "canonical_window_et": [str(canon_start_et), str(canon_end_et)],
            "n_bars_canonical_window": n_canon,
            "n_sessions_canonical_window": int(bars.loc[canon_mask, "sess_date"].nunique()),
            "mnq_sibling": ("SolarWaveOneContractMNQ_v5.cs diffed byte-for-byte against "
                            "SolarWaveOneContractNQ_v5.cs this session: decision-layer "
                            "formulas/thresholds/control-flow (member ensemble, BmomBar, "
                            "tiltState, T/mm/Tp/M, Q_B, hysteresis, forceFlat/entryBlocked) "
                            "are byte-identical; the only diffs are which BarsArray index "
                            "plays signal vs execution role (an instrument-wiring difference, "
                            "not a decision-logic difference). Spot-checked via diff this "
                            "session, not independently re-run bar-by-bar; relies on this "
                            "diff plus prior sessions' verification for the MNQ object itself."),
            "reuse_note": ("sumNext (13-member ensemble) reused from the campaign's own "
                           "validated sm01_solarsim.py/common.py port, spot-checked against "
                           "the .cs this session. tiltState and bmomPos and the full "
                           "forceFlat/entryBlocked/hysteresis overlay were freshly, "
                           "independently bar-by-bar ported directly from the .cs in THIS "
                           "script, per task instruction to give the operational overlay "
                           "real (not formality-pass) scrutiny."),
        },
        "domain_check": {
            "eqv01_domain": "sumNext in [-13,13] x tiltState in {-1,0,1} x bmomPos in {-1,0,1} "
                           "x priorPos in {-1,0,1} (729 states)",
            "all_historical_states_within_domain": domain_clean,
            "violations": out_of_domain,
        },
        "canonical_window_comparison_operational": canon_cmp,
        "full_history_comparison_operational": full_cmp,
        "canonical_window_comparison_raw_gates_off": canon_raw_cmp,
        "full_history_comparison_raw_gates_off": full_raw_cmp,
        "canonical_window_mismatch_detail": canon_mismatch_detail,
        "full_history_mismatch_detail_first25": full_mismatch_detail,
        "overlay_coverage_stats": overlay_stats,
        "tiltState_ge_vs_gt_warmup_divergence": tilt_warmup_note,
        "known_2023_04_05_data_gap": known_gap_note,
    }

    out_path = OUT_DIR / "productB_array_equality.json"
    out_path.write_text(json.dumps(report, indent=2, default=str))

    # -------------------------------------------------------------------------------
    print("\n" + "=" * 78)
    print("EQV02 PRODUCT B -- HEADLINE RESULT")
    print("=" * 78)
    print(f"Domain clean (all states within EQV01's 729-state domain): {domain_clean}")
    print(f"\nCANONICAL WINDOW  [{canon_start_et} .. {canon_end_et}]  "
          f"n_bars={n_canon}")
    print(f"  RAW (gates off)      array bit-identical : {canon_raw_cmp['raw_array_hash_equal']}  "
          f"mismatches {canon_raw_cmp['n_mismatched_bars']}  events-equal {canon_raw_cmp['event_sequence_equal']}")
    print(f"  OPERATIONAL (gates)  array bit-identical : {canon_cmp['raw_array_hash_equal']}  "
          f"mismatches {canon_cmp['n_mismatched_bars']}  events-equal {canon_cmp['event_sequence_equal']}")
    print(f"  n_events operational (current / canonical) : {canon_cmp['n_events_current']} / {canon_cmp['n_events_canonical']}")
    print(f"  hash(pos, current)   = {canon_cmp['hash_current_pos']}")
    print(f"  hash(pos, canonical) = {canon_cmp['hash_canonical_pos']}")
    print(f"  hash(events, current)   = {canon_cmp['hash_current_events']}")
    print(f"  hash(events, canonical) = {canon_cmp['hash_canonical_events']}")
    print(f"\nFULL HISTORY (secondary/bonus)  [{bars['time'].min()} .. {bars['time'].max()}]  "
          f"n_bars={n}")
    print(f"  RAW (gates off)      array bit-identical : {full_raw_cmp['raw_array_hash_equal']}  "
          f"mismatches {full_raw_cmp['n_mismatched_bars']}")
    print(f"  OPERATIONAL (gates)  array bit-identical : {full_cmp['raw_array_hash_equal']}  "
          f"mismatches {full_cmp['n_mismatched_bars']}")
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
