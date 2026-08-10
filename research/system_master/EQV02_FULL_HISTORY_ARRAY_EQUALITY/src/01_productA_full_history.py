"""EQV02 (Product A) -- full-history array equality between CURRENT_FORM (the real
SolarWaveSMMaster_v4.cs decoder) and CANONICAL_FORM (EQV01's proven-exact
Q_A = Tpp + 4*bmomPos; target_A = clip(-13,13,round_away(0.73*Q_A)) representation),
run bar-by-bar over the true historical (sumNext, tiltState, bmomPos) time series --
not the finite-state enumeration EQV01 used.

GATED ON: research/system_master/EQV01_BEHAVIORAL_CANONICALIZATION/REPORT.md (Product-A
hypothesis: 243/243 EXACT_EQUIVALENCE over the full reachable finite state space). This
script asks: (a) does every historical bar's (sumNext,tiltState,bmomPos) actually fall
inside that 243-state domain (a domain-completeness check EQV01 itself could not run,
since it enumerated the abstract state space, not real market history), and (b) does the
NEW ground EQV02 owns -- the operational overlay (EntryBlockMinutesBeforeClose=30,
ForcedFlatMinutesBeforeClose=21) and the resulting TIME-SEQUENCED physical-position walk,
never tested by EQV01's pure single-step decoder enumeration -- preserve exact equivalence
once real session clocks and a real, causal, path-dependent position history are involved.

REUSE, NOT REIMPLEMENTATION, of the campaign's own already-certified substrate:
  research/system_master/GRID01_SOLAR_RESOLUTION_CONVERGENCE/src/grid_core.py
    ("or equivalent" per task instructions to health_substrate.py -- grid_core.py is the
    Product-A-native sibling: it already exposes T/TILT_STATE/B_LEG/ENTRY_BLOCKED_C4/
    FORCED_FLAT_C4 built from src/analytics/sm01_solarsim.py's member_states/member_trades
    (13-member ensemble) + sm_bmom.py's rth_3m/BAND_DAYS-driven bmom_pos_series, AND already
    self-checks at import time against BOTH certified dev-window nets: Product A
    $177,924.40, Product B $301,915.92 -- so importing it is itself a live correctness gate
    on the whole upstream substrate before this script adds a single line of its own logic).
  Nothing in grid_core.py, sm01_solarsim.py, sm_bmom.py, or health_substrate.py is modified
  by this script -- everything is imported and called.

CURRENT_FORM / CANONICAL_FORM formulas: verified 2026-08-10 by direct read of
src/ninjascript/SolarWaveSMMaster_v4.cs lines 94-95 (EntryBlockMinutesBeforeClose=30,
ForcedFlatMinutesBeforeClose=21) and lines 356-383 (T/mm/ss/Tpp/M/tgtRaw + the operational
overlay itself) -- both cited verbatim in the module docstring below and cross-checked
against research/system_master/CANONICAL_MATHEMATICAL_SPEC.md.

Data boundary: runs/AUDIT03_BARS/nq_3m_2022_2026.csv ends 2026-07-31T16:57 -- strictly
before the 2026-08-01 LOCKED_FORWARD boundary (research/operational/LOCKED_FORWARD.md).
Nothing >=2026-08-01 is read anywhere in this script or its dependencies.
"""
import os
import sys
import json
import hashlib
import time

import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "research", "system_master",
                                 "GRID01_SOLAR_RESOLUTION_CONVERGENCE", "src"))
# grid_core.py inserts src/analytics and runs/W18R1_M1_VOLSEASON/src itself on import.

OUT_DIR = os.path.join(ROOT, "research", "system_master",
                        "EQV02_FULL_HISTORY_ARRAY_EQUALITY", "out")
os.makedirs(OUT_DIR, exist_ok=True)

T0 = time.time()

print("[EQV02-A] importing grid_core (heavy: builds the 13-member Solar ensemble, the "
      "B-MOM leg, and self-checks BOTH certified dev-window nets before returning) ...",
      flush=True)
import grid_core as GC  # noqa: E402  (heavy import, runs its own correctness gates)
from sm01_solarsim import _fill  # noqa: E402  (verbatim reuse, not modified)

print(f"[EQV02-A] grid_core imported + self-checked in {time.time() - T0:.1f}s", flush=True)

# ---------------------------------------------------------------------------------------
# CURRENT_FORM constants -- verified by direct read of SolarWaveSMMaster_v4.cs
# lines 130-131 (defaults) and 357-364 (formula). Pulled from grid_core (module-level
# constants there, not re-typed independently, so there is exactly one place in this
# campaign's Python code where these numbers live).
# ---------------------------------------------------------------------------------------
KSOLAR, KBMOM = GC.KSOLAR, GC.KBMOM
TILTRESCALE, TILTMULT, SHORTHALF = GC.TILTRESCALE, GC.TILTMULT, GC.SHORTHALF
PV_MNQ_A, COMM_MNQ_A = GC.PV_MNQ_A, GC.COMM_MNQ_A
CERTIFIED_A_DEV_NET = 177924.40  # grid_core.py / U0's own gate, same window+pricing convention

# CANONICAL_FORM representational substitutes -- EQV01 REPORT.md sec.1 / CANONICAL_MATHEMATICAL_SPEC.md
Q_COEF_CANON = 4
K_CANON = 0.73

# Operational overlay constants -- verified by direct read of SolarWaveSMMaster_v4.cs lines 94-95:
#   private const int EntryBlockMinutesBeforeClose = 30;   // == 16:30 on a 17:00 close
#   private const int ForcedFlatMinutesBeforeClose  = 21;   // == 16:39 on a 17:00 close
ENTRY_BLOCK_MIN_CS = 30
FORCED_FLAT_MIN_CS = 21
# grid_core.py's own ENTRY_BLOCKED_C4/FORCED_FLAT_C4 (lines 141-144 there) are built with
# EXACTLY these same two offsets against SessionIterator.ActualSessionEnd's Python analogue
# (per-session max bar time) -- verified by direct read of that file above; reused verbatim
# below, not re-derived.

CANON_START, CANON_END = GC.CANON_START, GC.CANON_END  # CLAUDE.md frozen canonical window
FULLER_END = GC.HEALTH_END  # 2026-07-31, the fullest already-consumed, non-locked-forward data


def rha(x):
    """Round-half-away-from-zero, vectorized -- the exact formula used throughout this
    campaign's Python substrate (grid_core.py, U0, PERT01) for C# Math.Round(...,
    MidpointRounding.AwayFromZero) with 0 digits."""
    return np.sign(x) * np.floor(np.abs(x) + 0.5)


def sha256_int_array(arr):
    return hashlib.sha256(np.asarray(arr, dtype=np.int8).tobytes()).hexdigest()


def sha256_events(events):
    payload = json.dumps(events, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


# =========================================================================================
# 0. SUBSTRATE (reused verbatim from grid_core, which itself reuses sm01_solarsim /
#    sm_bmom / common.py -- nothing recomputed here except cheap vectorized formulas)
# =========================================================================================
bars = GC._bars
n = GC.N
open_, high, low, close = GC.OPEN_, GC.HIGH, GC.LOW, GC.CLOSE
last = GC.LAST
sd = GC.SD
times = pd.to_datetime(bars["time"]).to_numpy()
time_str = bars["time"].astype(str).to_numpy()

PEND = GC._PEND0                       # (n, 13) member pending-position matrix, incumbent VMS grid
T = GC._T0.astype(int)                 # Solar13-consensus T, already e10_target(PEND)
tiltState = GC.TILT_STATE              # float array, values in {-1.0, 0.0, 1.0} by construction
bmomPos = np.asarray(GC.B_LEG)         # float array, values in {-1.0, 0.0, 1.0} by construction
entry_blocked = GC.ENTRY_BLOCKED_C4
forced_flat = GC.FORCED_FLAT_C4

sd_dt = pd.to_datetime(pd.Series(sd))
mask_canonical = ((sd_dt >= CANON_START) & (sd_dt <= CANON_END)).to_numpy()
mask_fuller = np.ones(n, dtype=bool)   # entire loaded array: 2022-01-02 .. 2026-07-31

print(f"[EQV02-A] substrate: n={n} bars, {bars['time'].min()} .. {bars['time'].max()}; "
      f"canonical-window bars={int(mask_canonical.sum())} "
      f"({sd_dt[mask_canonical].min()} .. {sd_dt[mask_canonical].max()})", flush=True)

# =========================================================================================
# 1. DOMAIN VERIFICATION -- does every historical bar's (sumNext,tiltState,bmomPos) fall
#    inside EQV01's claimed 243-state reachable domain (sumNext in [-13,13], tiltState in
#    {-1,0,1}, bmomPos in {-1,0,1})? This is a genuinely new check: EQV01 enumerated the
#    abstract domain, it never confirmed real history stays inside it.
# =========================================================================================
sumNext = PEND.sum(axis=1).astype(int)
T_mine = np.clip(rha(sumNext / 13.0 * 10.0), -10, 10).astype(int)
T_cross_match = bool(np.array_equal(T_mine, T))

sumNext_bad = np.where((sumNext < -13) | (sumNext > 13))[0]
tilt_bad = np.where(~np.isin(tiltState, [-1.0, 0.0, 1.0]))[0]
bmom_bad = np.where(~np.isin(bmomPos, [-1.0, 0.0, 1.0]))[0]

domain_violation_examples = []
for idx_arr, field in [(sumNext_bad, "sumNext"), (tilt_bad, "tiltState"), (bmom_bad, "bmomPos")]:
    for i in idx_arr[:25]:
        domain_violation_examples.append({
            "bar": int(i), "time": str(times[i]), "field": field,
            "sumNext": int(sumNext[i]), "tiltState": float(tiltState[i]), "bmomPos": float(bmomPos[i]),
        })

n_domain_violations = int(len(sumNext_bad) + len(tilt_bad) + len(bmom_bad))
domain_report = {
    "eqv01_claimed_domain": {"sumNext_range": [-13, 13], "tiltState_values": [-1, 0, 1],
                              "bmomPos_values": [-1, 0, 1], "total_enumerated_states": 243},
    "n_bars_checked": int(n),
    "observed_sumNext_range": [int(sumNext.min()), int(sumNext.max())],
    "observed_tiltState_values": sorted(set(int(v) for v in tiltState)),
    "observed_bmomPos_values": sorted(set(int(v) for v in bmomPos)),
    "n_distinct_states_actually_visited": int(pd.DataFrame(
        {"sumNext": sumNext, "tiltState": tiltState.astype(int), "bmomPos": bmomPos.astype(int)}
    ).drop_duplicates().shape[0]),
    "n_domain_violations": n_domain_violations,
    "domain_violation_examples_capped_25_each": domain_violation_examples,
    "verdict": ("ALL_HISTORICAL_STATES_WITHIN_EQV01_DOMAIN" if n_domain_violations == 0
                else "EQV01_DOMAIN_CLAIM_VIOLATED_BY_REAL_HISTORY -- see domain_violation_examples"),
    "T_recompute_cross_check_vs_grid_core_T": {
        "note": "T independently recomputed here from sumNext=PEND.sum(axis=1) via the exact "
                "clip(-10,10,round_away(sumNext/13*10)) formula, then compared to grid_core's own "
                "e10_target(PEND) output -- a from-scratch cross-check, not a trust assumption.",
        "match": T_cross_match,
        "n_mismatch": int(np.sum(T_mine != T)) if not T_cross_match else 0,
    },
}
print(f"[EQV02-A] domain check: {domain_report['verdict']}  "
      f"(T cross-check match={T_cross_match})", flush=True)

# =========================================================================================
# 2. CURRENT_FORM -- verbatim SolarWaveSMMaster_v4.cs formula (lines 357-364)
# =========================================================================================
m_arr = np.where((T != 0) & (tiltState != 0) & (np.sign(T) == tiltState), TILTMULT, 1.0)
s_arr = np.where((T < 0) & (tiltState > 0), SHORTHALF, 1.0)
Tpp_raw = T * m_arr * s_arr * TILTRESCALE
Tpp = np.clip(rha(Tpp_raw), -13, 13).astype(int)
M_current = KSOLAR * Tpp + KBMOM * bmomPos
tgtRaw = np.clip(rha(M_current), -13, 13).astype(int)

# cross-check against grid_core's OWN product_a_exec (independently self-checked at import
# time against the certified $177,924.40 dev-window net) -- confirms this script's from-
# scratch CURRENT_FORM re-derivation is not silently diverging from the certified twin.
_gc_bar_pos, _gc_bar_pnl, _gc_M_a = GC.product_a_exec(T, ticks=1)
gc_tgtRaw = np.asarray(_gc_M_a).astype(int)
tgtRaw_vs_gc_match = bool(np.array_equal(tgtRaw, gc_tgtRaw))
gc_dev_net = float(_gc_bar_pnl[GC.DEV_MASK].sum())
print(f"[EQV02-A] CURRENT_FORM tgtRaw vs grid_core.product_a_exec's own M_a: "
      f"match={tgtRaw_vs_gc_match}; grid_core dev-window net={gc_dev_net:.2f} "
      f"(certified {CERTIFIED_A_DEV_NET})", flush=True)

# =========================================================================================
# 3. CANONICAL_FORM -- Q_A = Tpp + 4*bmomPos; target_A = clip(-13,13,round_away(0.73*Q_A))
#    SAME Tpp array object as step 2 (not recomputed) -- per EQV01's own scope, only the
#    Tpp -> target step changes.
# =========================================================================================
Q_A = Tpp + Q_COEF_CANON * bmomPos
target_A_raw = K_CANON * Q_A
target_A = np.clip(rha(target_A_raw), -13, 13).astype(int)

# T/Tpp/bmomPos identity check (trivial by construction -- both forms consume the SAME
# arrays -- confirmed explicitly per task step 5's instruction to compare these too)
identity_check = {
    "T_is_shared_array": True, "Tpp_is_shared_array": True, "bmomPos_is_shared_array": True,
    "note": "CURRENT_FORM and CANONICAL_FORM both read T, Tpp, bmomPos from the identical "
            "numpy arrays constructed once in step 2 above -- there is no separate "
            "CANONICAL_FORM computation of these upstream quantities to diverge from.",
}

# =========================================================================================
# 4. RAW (pre-overlay) target array comparison: tgtRaw (CURRENT_FORM) vs target_A (CANONICAL_FORM)
# =========================================================================================
raw_match = (tgtRaw == target_A)
raw_mismatch_idx_all = np.where(~raw_match)[0]


def raw_mismatch_detail(i):
    return {
        "bar": int(i), "time": str(times[i]), "sess_date": str(sd[i]),
        "sumNext": int(sumNext[i]), "tiltState": float(tiltState[i]), "bmomPos": float(bmomPos[i]),
        "T": int(T[i]), "Tpp": int(Tpp[i]), "M_current": float(M_current[i]),
        "tgtRaw": int(tgtRaw[i]), "Q_A": int(Q_A[i]), "target_A_raw": float(target_A_raw[i]),
        "target_A": int(target_A[i]),
    }


raw_mismatch_examples = [raw_mismatch_detail(i) for i in raw_mismatch_idx_all[:50]]

# historical rounding-margin analysis (same diagnostic EQV01 ran on the enumerated domain,
# now run on the ACTUAL historical M values -- how close did real history ever come to a
# rounding-direction-flip boundary?)
frac = M_current - np.floor(M_current)
dist_half_M = np.abs(frac - 0.5)
signed_perturbation = M_current - target_A_raw
safety_margin = dist_half_M - np.abs(signed_perturbation)
worst_margin_idx = int(np.argmin(safety_margin))
margin_analysis = {
    "purpose": "Same near-miss diagnostic as EQV01's own script, evaluated on the REAL "
               "historical M_current values (not the enumerated domain) -- the tightest "
               "margin any actual historical bar came to a rounding-direction flip.",
    "min_safety_margin_across_all_historical_bars": float(safety_margin[worst_margin_idx]),
    "all_bars_positive_margin_i.e_zero_flips": bool(np.all(safety_margin > 0)),
    "worst_bar": raw_mismatch_detail(worst_margin_idx) if len(raw_mismatch_idx_all) == 0 else None,
    "worst_bar_index_and_time": {"bar": worst_margin_idx, "time": str(times[worst_margin_idx])},
    "eqv01_enumerated_worst_case_margin_for_reference": 0.00591,
}

# =========================================================================================
# 5. OPERATIONAL OVERLAY -- the genuinely NEW ground EQV02 owns. Verbatim-structure copy of
#    grid_core.product_a_exec's own loop (itself a verbatim copy of U0's
#    product_a_exec_generalized, itself matching SolarWaveSMMaster_v4.cs lines 366-397
#    exactly), generalized to accept EITHER raw-target array (tgtRaw or target_A) so the
#    identical code path runs both forms -- not two hand-typed copies of the overlay logic.
# =========================================================================================
def simulate_overlay(tgt_raw_arr, forced_flat_, entry_blocked_, last_, o, h, l, c, pv, comm, n_):
    """Returns:
      bar_pos   -- physical position AT each bar (post any fill this bar), i.e. "exposure"
      tgt_ops   -- the per-bar overlay DECISION ("tgt" in the .cs / barLog column), computed
                   every bar exactly as .cs lines 366-383 do (forceFlat/entryBlocked gating
                   against the CAUSALLY-PRIOR physical position) -- 0 in the special
                   session-close-backstop branch below, matching what forceFlat would compute
                   there anyway (see backstop_events).
      bar_pnl   -- MNQ-equivalent P&L (PV_MNQ_A/COMM_MNQ_A pricing, matches grid_core/U0 exactly)
      backstop_events -- bars where the ENGINE's own IsExitOnSessionCloseStrategy backstop
                   (not the strategy's own tgt=0 overlay decision) was the thing that actually
                   zeroed a still-open position at the session's last bar. Given
                   ForcedFlatMinutesBeforeClose=21 min (7 bars of 3-min lag before the last
                   bar), this is expected to be EMPTY for every normal and early-close session
                   -- a nonzero count here would be a genuine, reportable finding about the
                   overlay's own robustness, not an A-vs-canonical discrepancy (both forms
                   run through this identical function).
    """
    cash = 0.0
    p = 0
    pend = 0
    prev_eq = 0.0
    bar_pos = np.zeros(n_, dtype=np.int8)
    tgt_ops = np.zeros(n_, dtype=np.int8)
    bar_pnl = np.zeros(n_)
    backstop_events = []
    for t in range(n_):
        if pend != p:
            d = pend - p
            side = 1 if d > 0 else -1
            px = _fill(o[t], h[t], l[t], side)
            cash -= d * px * pv
            cash -= abs(d) * comm
            p = pend
        if last_[t] and p != 0:
            backstop_events.append((t, int(p)))
            side = -1 if p > 0 else 1
            px = _fill(o[t], h[t], l[t], side, at_close=c[t])
            cash += p * px * pv
            cash -= abs(p) * comm
            p = 0
            pend = 0
            tgt_ops[t] = 0
        else:
            tr = int(tgt_raw_arr[t])
            if forced_flat_[t]:
                tgt = 0
            elif entry_blocked_[t]:
                if tr == 0 or p == 0:
                    tgt = 0
                elif np.sign(tr) != np.sign(p):
                    tgt = 0
                else:
                    tgt = p if abs(tr) > abs(p) else tr
            else:
                tgt = tr
            pend = tgt
            tgt_ops[t] = tgt
        eq = cash + p * c[t] * pv
        bar_pnl[t] = eq - prev_eq
        prev_eq = eq
        bar_pos[t] = p
    return bar_pos, tgt_ops, bar_pnl, backstop_events


print("[EQV02-A] running the SAME operational-overlay simulator on tgtRaw (CURRENT_FORM) ...",
      flush=True)
bar_pos_current, tgt_ops_current, bar_pnl_current, backstop_current = simulate_overlay(
    tgtRaw, forced_flat, entry_blocked, last, open_, high, low, close, PV_MNQ_A, COMM_MNQ_A, n)

print("[EQV02-A] running the SAME operational-overlay simulator on target_A (CANONICAL_FORM) ...",
      flush=True)
bar_pos_canonical, tgt_ops_canonical, bar_pnl_canonical, backstop_canonical = simulate_overlay(
    target_A, forced_flat, entry_blocked, last, open_, high, low, close, PV_MNQ_A, COMM_MNQ_A, n)

# correctness gate: CURRENT_FORM's own dev-window net must reproduce grid_core's certified
# $177,924.40 (proves this script's independently-written simulate_overlay() is faithful to
# the certified original before its CANONICAL_FORM twin run is trusted at all)
my_dev_net_current = float(bar_pnl_current[GC.DEV_MASK].sum())
overlay_selfcheck = {
    "certified_dev_window_net": CERTIFIED_A_DEV_NET,
    "this_script_simulate_overlay_current_form_dev_net": my_dev_net_current,
    "match_within_1usd": bool(abs(my_dev_net_current - CERTIFIED_A_DEV_NET) < 1.0),
    "grid_core_product_a_exec_dev_net_cross_check": gc_dev_net,
    "bar_pos_matches_grid_core_bar_pos": bool(np.array_equal(
        np.asarray(bar_pos_current, dtype=int), np.asarray(_gc_bar_pos, dtype=int))),
}
print(f"[EQV02-A] overlay self-check: {overlay_selfcheck}", flush=True)

# =========================================================================================
# 6. OPERATIONAL target-array comparison (post-overlay decisions) + physical-position comparison
# =========================================================================================
ops_match = (tgt_ops_current == tgt_ops_canonical)
ops_mismatch_idx_all = np.where(~ops_match)[0]
pos_match = (bar_pos_current == bar_pos_canonical)
pos_mismatch_idx_all = np.where(~pos_match)[0]


def ops_mismatch_detail(i):
    d = raw_mismatch_detail(i)
    d.update({
        "tgt_ops_current": int(tgt_ops_current[i]), "tgt_ops_canonical": int(tgt_ops_canonical[i]),
        "bar_pos_current": int(bar_pos_current[i]), "bar_pos_canonical": int(bar_pos_canonical[i]),
        "forced_flat": bool(forced_flat[i]), "entry_blocked": bool(entry_blocked[i]),
    })
    return d


ops_mismatch_examples = [ops_mismatch_detail(i) for i in ops_mismatch_idx_all[:50]]

# =========================================================================================
# 7. EXPOSURE-CHANGE EVENTS -- derived from the physical position walk (bar_pos), the
#    economically meaningful "did the held contract count actually change" signal. Derived
#    once over the FULL continuous array (matches WARMUP_STANDARD.md's mandatory
#    continuation-run convention), then filtered per reporting window below.
# =========================================================================================
def exposure_events(bar_pos_arr):
    prev = np.concatenate(([0], bar_pos_arr[:-1].astype(int)))
    delta = bar_pos_arr.astype(int) - prev
    idx = np.where(delta != 0)[0]
    return [{"bar": int(i), "time": time_str[i], "sess_date": str(sd[i]),
             "quantity": int(delta[i]), "resulting_position": int(bar_pos_arr[i])}
            for i in idx]


events_current_full = exposure_events(bar_pos_current)
events_canonical_full = exposure_events(bar_pos_canonical)


def filter_events(events, mask):
    idxset = set(np.where(mask)[0].tolist())
    return [e for e in events if e["bar"] in idxset]


# =========================================================================================
# 8. PER-WINDOW REPORTING (canonical primary window is the pass/fail verdict; fuller
#    history is the secondary/bonus check, per task instructions)
# =========================================================================================
def window_report(mask, label):
    n_bars = int(mask.sum())
    raw_m = raw_match[mask]
    ops_m = ops_match[mask]
    pos_m = pos_match[mask]
    ev_cur = filter_events(events_current_full, mask)
    ev_can = filter_events(events_canonical_full, mask)
    ev_seq_equal = (ev_cur == ev_can)
    qty_cur = [e["quantity"] for e in ev_cur]
    qty_can = [e["quantity"] for e in ev_can]

    h_raw_current = sha256_int_array(tgtRaw[mask])
    h_raw_canonical = sha256_int_array(target_A[mask])
    h_ops_current = sha256_int_array(tgt_ops_current[mask])
    h_ops_canonical = sha256_int_array(tgt_ops_canonical[mask])
    h_pos_current = sha256_int_array(bar_pos_current[mask])
    h_pos_canonical = sha256_int_array(bar_pos_canonical[mask])
    h_ev_current = sha256_events(ev_cur)
    h_ev_canonical = sha256_events(ev_can)
    h_qty_current = hashlib.sha256(np.asarray(qty_cur, dtype=np.int8).tobytes()).hexdigest()
    h_qty_canonical = hashlib.sha256(np.asarray(qty_can, dtype=np.int8).tobytes()).hexdigest()

    return {
        "label": label,
        "n_bars": n_bars,
        "date_range": [str(sd[mask].min()), str(sd[mask].max())] if n_bars else None,
        "raw_target_array": {
            "exact_matches": int(raw_m.sum()), "mismatches": int((~raw_m).sum()),
            "exact_match_rate_pct": float(raw_m.mean() * 100.0) if n_bars else None,
            "sha256_current_tgtRaw": h_raw_current, "sha256_canonical_target_A": h_raw_canonical,
            "bit_identical": h_raw_current == h_raw_canonical,
        },
        "operational_target_array": {
            "exact_matches": int(ops_m.sum()), "mismatches": int((~ops_m).sum()),
            "exact_match_rate_pct": float(ops_m.mean() * 100.0) if n_bars else None,
            "sha256_current": h_ops_current, "sha256_canonical": h_ops_canonical,
            "bit_identical": h_ops_current == h_ops_canonical,
        },
        "physical_position_array_bonus": {
            "exact_matches": int(pos_m.sum()), "mismatches": int((~pos_m).sum()),
            "exact_match_rate_pct": float(pos_m.mean() * 100.0) if n_bars else None,
            "sha256_current": h_pos_current, "sha256_canonical": h_pos_canonical,
            "bit_identical": h_pos_current == h_pos_canonical,
        },
        "exposure_change_events": {
            "n_events_current": len(ev_cur), "n_events_canonical": len(ev_can),
            "full_event_sequence_identical_incl_timestamps": ev_seq_equal,
            "sha256_full_event_sequence_current": h_ev_current,
            "sha256_full_event_sequence_canonical": h_ev_canonical,
            "sha256_quantity_sequence_only_current": h_qty_current,
            "sha256_quantity_sequence_only_canonical": h_qty_canonical,
            "quantity_sequence_bit_identical": h_qty_current == h_qty_canonical,
            "total_abs_quantity_traded_current": int(np.sum(np.abs(qty_cur))) if qty_cur else 0,
            "total_abs_quantity_traded_canonical": int(np.sum(np.abs(qty_can))) if qty_can else 0,
            "first_5_events_current": ev_cur[:5], "last_5_events_current": ev_cur[-5:],
            "first_5_events_canonical": ev_can[:5], "last_5_events_canonical": ev_can[-5:],
        },
    }


report_canonical = window_report(mask_canonical, "primary_claude_canonical_2023-01-01_to_2025-02-02")
report_fuller = window_report(mask_fuller, "secondary_fuller_history_2022-01-02_to_2026-07-31")

# =========================================================================================
# 9. FINAL VERDICT
# =========================================================================================
all_bit_identical_canonical = all([
    report_canonical["raw_target_array"]["bit_identical"],
    report_canonical["operational_target_array"]["bit_identical"],
    report_canonical["physical_position_array_bonus"]["bit_identical"],
    report_canonical["exposure_change_events"]["quantity_sequence_bit_identical"],
    report_canonical["exposure_change_events"]["full_event_sequence_identical_incl_timestamps"],
])
all_bit_identical_fuller = all([
    report_fuller["raw_target_array"]["bit_identical"],
    report_fuller["operational_target_array"]["bit_identical"],
    report_fuller["physical_position_array_bonus"]["bit_identical"],
    report_fuller["exposure_change_events"]["quantity_sequence_bit_identical"],
    report_fuller["exposure_change_events"]["full_event_sequence_identical_incl_timestamps"],
])

verdict = {
    "domain_verdict": domain_report["verdict"],
    "canonical_window_verdict": ("EXACT_EQUIVALENCE" if all_bit_identical_canonical
                                  else "MISMATCH_FOUND -- see raw/operational mismatch examples"),
    "fuller_history_verdict": ("EXACT_EQUIVALENCE" if all_bit_identical_fuller
                                else "MISMATCH_FOUND -- see raw/operational mismatch examples"),
    "backstop_events_current_form": {"n": len(backstop_current), "examples": backstop_current[:10]},
    "backstop_events_canonical_form": {"n": len(backstop_canonical), "examples": backstop_canonical[:10]},
    "interpretation": (
        "Every historical bar's (sumNext,tiltState,bmomPos) falls inside EQV01's enumerated "
        "243-state domain (see domain_check), so EQV01's finite-state proof mechanically "
        "covers every bar's RAW decoder output by construction. This script's contribution is "
        "(a) confirming that mechanical implication empirically bar-by-bar rather than trusting "
        "it, and (b) running the operational overlay's real, TIME-SEQUENCED, path-dependent "
        "position walk (never tested by EQV01's single-step enumeration) against real session "
        "clocks and real historical fills, on BOTH forms through the identical simulate_overlay() "
        "code path -- confirming the equivalence survives statefulness, not just the stateless "
        "decoder step."
        if (n_domain_violations == 0 and all_bit_identical_canonical) else
        "See mismatch details and domain_check above -- do not treat this as a clean pass."
    ),
}

print(f"[EQV02-A] VERDICT: domain={verdict['domain_verdict']}  "
      f"canonical_window={verdict['canonical_window_verdict']}  "
      f"fuller_history={verdict['fuller_history_verdict']}", flush=True)
print(f"[EQV02-A] raw target: {report_canonical['raw_target_array']['exact_matches']}/"
      f"{report_canonical['n_bars']} canonical-window bars match "
      f"({report_canonical['raw_target_array']['exact_match_rate_pct']:.6f}%)", flush=True)

# =========================================================================================
# 10. WRITE OUTPUT
# =========================================================================================
result = {
    "task": "EQV02 Product A -- full-history array equality (CURRENT_FORM vs CANONICAL_FORM), "
            "including the operational overlay layer never tested by EQV01",
    "generated": "2026-08-10",
    "gated_on": "research/system_master/EQV01_BEHAVIORAL_CANONICALIZATION/REPORT.md "
                "(Product A: 243/243 EXACT_EQUIVALENCE, finite-state)",
    "source_files_reused_by_import_not_modified": [
        "research/system_master/GRID01_SOLAR_RESOLUTION_CONVERGENCE/src/grid_core.py",
        "src/analytics/sm01_solarsim.py (member_states/member_trades, via grid_core/common.py)",
        "src/analytics/sm_bmom.py (rth_3m/BAND_DAYS, via grid_core.bmom_pos_series)",
        "runs/W18R1_M1_VOLSEASON/src/common.py (build_pend, via grid_core)",
    ],
    "cs_source_verified": {
        "file": "src/ninjascript/SolarWaveSMMaster_v4.cs",
        "decoder_formula_lines": "357-364",
        "operational_overlay_lines": "366-397",
        "constants_lines": "94-95 (EntryBlockMinutesBeforeClose=30, ForcedFlatMinutesBeforeClose=21), "
                            "130-131 (TiltSma=50, TiltMult=1.25, TiltRescale=0.9026, ShortHalf=0.5, "
                            "KSolar=0.728654, KBmom=2.934159)",
    },
    "constants_used": {
        "KSolar": KSOLAR, "KBmom": KBMOM, "TiltRescale": TILTRESCALE, "TiltMult": TILTMULT,
        "ShortHalf": SHORTHALF, "K_canonical": K_CANON, "Q_coef_canonical": Q_COEF_CANON,
        "EntryBlockMinutesBeforeClose": ENTRY_BLOCK_MIN_CS, "ForcedFlatMinutesBeforeClose": FORCED_FLAT_MIN_CS,
        "PV_MNQ_A": PV_MNQ_A, "COMM_MNQ_A": COMM_MNQ_A,
    },
    "windows": {
        "primary_claude_canonical": {"start": str(CANON_START.date()), "end": str(CANON_END.date()),
                                      "convention": "session date (last-bar-of-session ET calendar date) "
                                                     "in [start,end] inclusive -- matches CLAUDE.md's "
                                                     "'To=D means last session ENDING <= D' convention"},
        "secondary_fuller_history": {"start": "2022-01-02", "end": "2026-07-31",
                                      "note": "entire already-loaded, non-locked-forward array; "
                                              "data file itself ends 2026-07-31T16:57, strictly before "
                                              "the 2026-08-01 LOCKED_FORWARD boundary"},
    },
    "n_bars_total": int(n),
    "n_sessions_total": int(bars["sess_date"].nunique()),
    "domain_check": domain_report,
    "current_form_cross_checks": {
        "tgtRaw_vs_grid_core_product_a_exec_M_a": tgtRaw_vs_gc_match,
        "grid_core_dev_window_net": gc_dev_net,
        "certified_dev_window_net": CERTIFIED_A_DEV_NET,
        "grid_core_gate_passed": bool(abs(gc_dev_net - CERTIFIED_A_DEV_NET) < 1.0),
    },
    "identity_check_T_Tpp_bmomPos_shared_between_forms": identity_check,
    "raw_target_historical_margin_analysis": margin_analysis,
    "overlay_simulator_selfcheck_vs_certified_net": overlay_selfcheck,
    "raw_target_mismatches": {
        "n_total_mismatches_full_history": int(len(raw_mismatch_idx_all)),
        "examples_capped_50": raw_mismatch_examples,
    },
    "operational_target_mismatches": {
        "n_total_mismatches_full_history": int(len(ops_mismatch_idx_all)),
        "examples_capped_50": ops_mismatch_examples,
    },
    "physical_position_mismatches": {
        "n_total_mismatches_full_history": int(len(pos_mismatch_idx_all)),
    },
    "window_reports": {
        "primary_claude_canonical": report_canonical,
        "secondary_fuller_history": report_fuller,
    },
    "verdict": verdict,
    "runtime_seconds": round(time.time() - T0, 1),
}

out_path = os.path.join(OUT_DIR, "productA_array_equality.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, default=str)

print(f"[EQV02-A] wrote {out_path}  (total runtime {time.time() - T0:.1f}s)", flush=True)
