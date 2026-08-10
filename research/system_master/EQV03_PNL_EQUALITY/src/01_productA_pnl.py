"""EQV03 (Product A) -- PnL equality between CURRENT_FORM and CANONICAL_FORM, feeding EACH
form's already-proven-identical (EQV02) operational target array through the campaign's own
established execution/pricing convention, under BOTH price bases still part of current research
truth (legacy NQ-proxy, genuine MNQ).

GATED ON:
  research/system_master/EQV01_BEHAVIORAL_CANONICALIZATION/REPORT.md (Product A: 243/243
    EXACT_EQUIVALENCE, finite-state decoder proof)
  research/system_master/EQV02_FULL_HISTORY_ARRAY_EQUALITY/REPORT.md +
    out/productA_array_equality.json (Product A: full-history, bar-by-bar, SHA256-verified
    EXACT_EQUIVALENCE of the raw target array, the operational (post-overlay) target array, the
    physical position array, and the exposure-change event sequence, both canonical and fuller
    windows -- READ DIRECTLY below and used as the pass/fail reference for the decision-layer
    ground this script does NOT re-litigate).

THIS SCRIPT DOES NOT RECOMPUTE THE DECISION LAYER FROM SCRATCH. It re-derives tgtRaw
(CURRENT_FORM) and target_A (CANONICAL_FORM) using the EXACT SAME verbatim formulas EQV02 used
(same constants, same grid_core.py substrate, same array objects for T/Tpp/bmomPos/
entry_blocked/forced_flat) and immediately SHA256-checks the result against EQV02's own recorded,
already-verified hashes (out/productA_array_equality.json) BEFORE trusting anything downstream --
if that check fails, this script stops and reports it as a genuine discrepancy, not a rounding
footnote. Only once that gate passes does this script add its own genuinely new contribution:
running BOTH forms' operational target arrays through the identical execution/pricing loop TWICE
(legacy NQ-proxy pricing, genuine MNQ pricing) and comparing the resulting PnL series bit-for-bit.

EXECUTION CONVENTION: reused verbatim from EQV02's `simulate_overlay()`
(research/system_master/EQV02_FULL_HISTORY_ARRAY_EQUALITY/src/01_productA_full_history.py,
itself -- per that script's own docstring -- "a verbatim-structure copy of grid_core.
product_a_exec's own loop (itself a verbatim copy of U0's product_a_exec_generalized, itself
matching SolarWaveSMMaster_v4.cs lines 366-397 exactly)"), which is the SAME execution loop
runs/PRICE01_PRODUCT_A_GENUINE_MNQ/src/01_dual_truth_repricing.py's
`product_a_exec_generalized()` uses internally (pend/p position walk, 1-tick adverse-slip fill
via sm01_solarsim._fill, session-close backstop, PV_MNQ_A=2.0/COMM_MNQ_A=0.65 MNQ pricing,
NinjaTrader Brokerage Lifetime-equivalent commission) -- copied here verbatim (not retyped from
memory) because EQV02's variant already takes a raw target array as input rather than fusing
decode+execute, which is exactly the "feed the operational target array in" shape this task asks
for and lets the SAME loop run under two different price-array arguments without any change to
the execution/commission logic itself.

DUAL-TRUTH GENUINE-MNQ PRICE ALIGNMENT: reused verbatim from PRICE01's pattern (mnq_3m_raw.csv
reindexed onto the bars time axis, NQ-proxy fallback for the small number of bars with no genuine
MNQ quote, e.g. earliest history before MNQ liquidity).

Data boundary: runs/AUDIT03_BARS/nq_3m_2022_2026.csv ends 2026-07-31T16:57, strictly before the
2026-08-01 LOCKED_FORWARD boundary. Nothing >=2026-08-01 is read anywhere in this script.
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

OUT_DIR = os.path.join(ROOT, "research", "system_master", "EQV03_PNL_EQUALITY", "out")
os.makedirs(OUT_DIR, exist_ok=True)

EQV02_JSON = os.path.join(ROOT, "research", "system_master", "EQV02_FULL_HISTORY_ARRAY_EQUALITY",
                           "out", "productA_array_equality.json")

T0 = time.time()

print("[EQV03-A] importing grid_core (heavy: builds the 13-member Solar ensemble, the B-MOM leg, "
      "and self-checks BOTH certified dev-window nets before returning) ...", flush=True)
import grid_core as GC  # noqa: E402
from sm01_solarsim import _fill  # noqa: E402  -- verbatim reuse, not modified

print(f"[EQV03-A] grid_core imported + self-checked in {time.time() - T0:.1f}s", flush=True)

print(f"[EQV03-A] reading EQV02's already-verified result JSON: {EQV02_JSON}", flush=True)
with open(EQV02_JSON, "r", encoding="utf-8") as f:
    eqv02 = json.load(f)
assert eqv02["verdict"]["canonical_window_verdict"] == "EXACT_EQUIVALENCE", (
    "EQV02 canonical-window verdict is not EXACT_EQUIVALENCE -- STOP, do not proceed to PnL "
    "comparison on top of an unproven decision layer.")
assert eqv02["verdict"]["fuller_history_verdict"] == "EXACT_EQUIVALENCE", (
    "EQV02 fuller-history verdict is not EXACT_EQUIVALENCE -- STOP.")
print("[EQV03-A] EQV02 gate confirmed: canonical_window_verdict=EXACT_EQUIVALENCE, "
      "fuller_history_verdict=EXACT_EQUIVALENCE -- proceeding.", flush=True)

# =========================================================================================
# constants -- identical source as EQV02 (grid_core module-level constants, not re-typed)
# =========================================================================================
KSOLAR, KBMOM = GC.KSOLAR, GC.KBMOM
TILTRESCALE, TILTMULT, SHORTHALF = GC.TILTRESCALE, GC.TILTMULT, GC.SHORTHALF
PV_MNQ_A, COMM_MNQ_A = GC.PV_MNQ_A, GC.COMM_MNQ_A
Q_COEF_CANON = 4
K_CANON = 0.73
# IMPORTANT WINDOW-TERMINOLOGY NOTE (discovered and reconciled by THIS script -- see
# certified_figure_crosscheck below): the campaign uses "canonical" for TWO DIFFERENT windows
# depending on context. (1) CLAUDE.md's frozen "canonical window" 2023-01-01..2025-02-02 applies
# to the ORIGINAL SolarWaveRKReplicaV0 baseline elsewhere in this repo (net $146,440.60) -- EQV02
# reused that same date range as its own "primary_claude_canonical" label purely for the
# array-equality comparison, NOT as a claim that Product A's certified PnL figure lives on that
# window. (2) Product A / system_master's OWN "canonical dev window" is 2022-01-03..2026-05-29
# (BASELINE_MODELS.md "Performance battery" section; grid_core.py's DEV_END=2026-05-31,
# health_substrate.py's CANONICAL_END=2026-05-31 -- both bound the SAME window from the data's
# earliest loaded bar through 2026-05-31/29) and THAT is the window $177,924.40 (legacy) /
# $178,687.40 (PRICE01 genuine-MNQ) are certified on -- confirmed by direct read of
# BASELINE_MODELS.md line ~290 ("Canonical dev window 2022-01-03 -> 2026-05-29 ... Net profit
# $177,924.40") and health_substrate.py line 34 (CANONICAL_END = 2026-05-31, "matches
# substrate.py exactly", which is what PRICE01's own CANONICAL_END/canon_mask uses). This script
# cross-checks against the CORRECT (dev-window) mask below, not the CLAUDE.md date range.
CERTIFIED_A_DEVWIN_NET = 177924.40          # BASELINE_MODELS.md "canonical dev window" legacy net
CERTIFIED_A_GENUINE_DEVWIN_NET = 178687.40  # PRICE01 out/price01_recon.json "canonical.genuine" (same dev window)
CERTIFIED_A_LEGACY_EXT_NET = 212894.50      # PRICE01 out/price01_recon.json "extended...legacy"
CERTIFIED_A_GENUINE_EXT_NET = 213657.50     # PRICE01 out/price01_recon.json "extended...genuine"

CANON_START, CANON_END = GC.CANON_START, GC.CANON_END   # CLAUDE.md date range (array-equality window only)
DEV_END = GC.DEV_END                                     # Product A's own certified-PnL dev-window boundary
FULLER_END = GC.HEALTH_END


def rha(x):
    return np.sign(x) * np.floor(np.abs(x) + 0.5)


def sha256_int_array(arr):
    return hashlib.sha256(np.asarray(arr, dtype=np.int8).tobytes()).hexdigest()


def sha256_float_array(arr):
    # exact IEEE-754 byte representation -- this is a bit-identity check, not a
    # rounded/approximate comparison
    return hashlib.sha256(np.asarray(arr, dtype=np.float64).tobytes()).hexdigest()


# =========================================================================================
# 0. SUBSTRATE -- identical arrays EQV02 used (same grid_core module-level objects)
# =========================================================================================
bars = GC._bars
n = GC.N
open_, high, low, close = GC.OPEN_, GC.HIGH, GC.LOW, GC.CLOSE
last = GC.LAST
sd = GC.SD
times = pd.to_datetime(bars["time"]).to_numpy()

PEND = GC._PEND0
T = GC._T0.astype(int)
tiltState = GC.TILT_STATE
bmomPos = np.asarray(GC.B_LEG)
entry_blocked = GC.ENTRY_BLOCKED_C4
forced_flat = GC.FORCED_FLAT_C4

sd_dt = pd.to_datetime(pd.Series(sd))
mask_canonical = ((sd_dt >= CANON_START) & (sd_dt <= CANON_END)).to_numpy()  # CLAUDE.md date range (array-equality only)
mask_dev_window = (sd_dt <= DEV_END).to_numpy()  # Product A's own certified-PnL window (2022-01-03..2026-05-31)
mask_fuller = np.ones(n, dtype=bool)

print(f"[EQV03-A] substrate: n={n} bars, {bars['time'].min()} .. {bars['time'].max()}; "
      f"canonical-window bars={int(mask_canonical.sum())}", flush=True)

# =========================================================================================
# 1. CURRENT_FORM / CANONICAL_FORM raw target arrays -- EXACT verbatim formulas EQV02 used
#    (research/system_master/EQV02_FULL_HISTORY_ARRAY_EQUALITY/src/01_productA_full_history.py
#    steps 2-3). Immediately hash-checked against EQV02's own recorded, already-verified
#    hashes below -- this is the "reuse EQV02's arrays directly" gate, made an explicit,
#    checked assertion rather than an assumption.
# =========================================================================================
m_arr = np.where((T != 0) & (tiltState != 0) & (np.sign(T) == tiltState), TILTMULT, 1.0)
s_arr = np.where((T < 0) & (tiltState > 0), SHORTHALF, 1.0)
Tpp_raw = T * m_arr * s_arr * TILTRESCALE
Tpp = np.clip(rha(Tpp_raw), -13, 13).astype(int)
M_current = KSOLAR * Tpp + KBMOM * bmomPos
tgtRaw = np.clip(rha(M_current), -13, 13).astype(int)  # CURRENT_FORM raw target

Q_A = Tpp + Q_COEF_CANON * bmomPos
target_A_raw = K_CANON * Q_A
target_A = np.clip(rha(target_A_raw), -13, 13).astype(int)  # CANONICAL_FORM raw target

reproduction_check = {}
for win_key, mask in [("primary_claude_canonical", mask_canonical), ("secondary_fuller_history", mask_fuller)]:
    eqv02_win = eqv02["window_reports"][win_key]
    my_h_current = sha256_int_array(tgtRaw[mask])
    my_h_canonical = sha256_int_array(target_A[mask])
    reproduction_check[win_key] = {
        "raw_target_current_matches_eqv02": my_h_current == eqv02_win["raw_target_array"]["sha256_current_tgtRaw"],
        "raw_target_canonical_matches_eqv02": my_h_canonical == eqv02_win["raw_target_array"]["sha256_canonical_target_A"],
        "my_sha256_current": my_h_current, "eqv02_sha256_current": eqv02_win["raw_target_array"]["sha256_current_tgtRaw"],
        "my_sha256_canonical": my_h_canonical, "eqv02_sha256_canonical": eqv02_win["raw_target_array"]["sha256_canonical_target_A"],
    }

reproduction_ok = all(v["raw_target_current_matches_eqv02"] and v["raw_target_canonical_matches_eqv02"]
                      for v in reproduction_check.values())
assert reproduction_ok, (
    "This script's re-derivation of tgtRaw/target_A does NOT reproduce EQV02's own recorded "
    "hashes -- STOP, this is a genuine reproduction failure, investigate before any PnL "
    "comparison is trusted. See reproduction_check.")
print(f"[EQV03-A] reproduction gate PASS: this script's tgtRaw/target_A are bit-identical to "
      f"EQV02's own recorded arrays, both windows.", flush=True)

# =========================================================================================
# 2. GENUINE-MNQ price alignment -- PRICE01's pattern, reused verbatim (mnq_3m_raw.csv
#    reindexed onto the bars time axis; NQ-proxy fallback for bars with no genuine MNQ quote)
# =========================================================================================
mnq_raw = pd.read_csv(os.path.join(ROOT, "runs", "PRODUCTB_ONECONTRACT_FINAL", "out", "mnq_3m_raw.csv"), comment="#")
mnq_raw["time"] = pd.to_datetime(mnq_raw["time"])
mnq_idx = mnq_raw.set_index("time")
aligned_raw = mnq_idx.reindex(bars["time"])
is_mnq_genuine = aligned_raw["close"].notna().to_numpy()
o_mnq = np.where(is_mnq_genuine, aligned_raw["open"].to_numpy(), open_)
h_mnq = np.where(is_mnq_genuine, aligned_raw["high"].to_numpy(), high)
l_mnq = np.where(is_mnq_genuine, aligned_raw["low"].to_numpy(), low)
c_mnq = np.where(is_mnq_genuine, aligned_raw["close"].to_numpy(), close)
print(f"[EQV03-A] MNQ genuine bars: {int(is_mnq_genuine.sum())} / {n} "
      f"(NQ-proxy fallback bars: {int((~is_mnq_genuine).sum())})", flush=True)

# =========================================================================================
# 3. EXECUTION LOOP -- verbatim copy of EQV02's simulate_overlay() (itself, per that script's
#    own docstring, a verbatim-structure copy of grid_core.product_a_exec's loop / U0's
#    product_a_exec_generalized / PRICE01's product_a_exec_generalized inner loop). NOT
#    reinvented here: same pend/p walk, same forced_flat/entry_blocked gating, same 1-tick
#    adverse-slip _fill, same session-close backstop, same PV/commission application.
# =========================================================================================
def simulate_overlay(tgt_raw_arr, forced_flat_, entry_blocked_, last_, o, h, l, c, pv, comm, n_):
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


# =========================================================================================
# 4. RUN: 2 forms x 2 price bases = 4 runs, identical execution loop, only tgt_raw_arr and
#    the (o,h,l,c) price arrays differ between runs.
# =========================================================================================
print("[EQV03-A] running LEGACY_NQ_PROXY price basis (CURRENT_FORM) ...", flush=True)
pos_cur_leg, ops_cur_leg, pnl_cur_leg, bs_cur_leg = simulate_overlay(
    tgtRaw, forced_flat, entry_blocked, last, open_, high, low, close, PV_MNQ_A, COMM_MNQ_A, n)

print("[EQV03-A] running LEGACY_NQ_PROXY price basis (CANONICAL_FORM) ...", flush=True)
pos_can_leg, ops_can_leg, pnl_can_leg, bs_can_leg = simulate_overlay(
    target_A, forced_flat, entry_blocked, last, open_, high, low, close, PV_MNQ_A, COMM_MNQ_A, n)

print("[EQV03-A] running GENUINE_MNQ price basis (CURRENT_FORM) ...", flush=True)
pos_cur_gen, ops_cur_gen, pnl_cur_gen, bs_cur_gen = simulate_overlay(
    tgtRaw, forced_flat, entry_blocked, last, o_mnq, h_mnq, l_mnq, c_mnq, PV_MNQ_A, COMM_MNQ_A, n)

print("[EQV03-A] running GENUINE_MNQ price basis (CANONICAL_FORM) ...", flush=True)
pos_can_gen, ops_can_gen, pnl_can_gen, bs_can_gen = simulate_overlay(
    target_A, forced_flat, entry_blocked, last, o_mnq, h_mnq, l_mnq, c_mnq, PV_MNQ_A, COMM_MNQ_A, n)

# =========================================================================================
# 5. Sanity: target-exposure / operational-target sequences must be identical to EQV02's
#    already-certified hashes (position depends only on the decision layer, never on price --
#    confirmed structurally here across BOTH price bases, matching PRICE01's own assertion)
# =========================================================================================
ops_price_invariance = {
    "current_form_ops_identical_across_price_bases": bool(np.array_equal(ops_cur_leg, ops_cur_gen)),
    "canonical_form_ops_identical_across_price_bases": bool(np.array_equal(ops_can_leg, ops_can_gen)),
    "current_form_pos_identical_across_price_bases": bool(np.array_equal(pos_cur_leg, pos_cur_gen)),
    "canonical_form_pos_identical_across_price_bases": bool(np.array_equal(pos_can_leg, pos_can_gen)),
}
assert all(ops_price_invariance.values()), (
    "Price basis leaked into the decision/position layer -- STOP, investigate. "
    f"{ops_price_invariance}")
print(f"[EQV03-A] price-invariance check PASS: {ops_price_invariance}", flush=True)

ops_vs_eqv02 = {}
for win_key, mask in [("primary_claude_canonical", mask_canonical), ("secondary_fuller_history", mask_fuller)]:
    eqv02_win = eqv02["window_reports"][win_key]
    h_ops_cur = sha256_int_array(ops_cur_leg[mask])
    h_ops_can = sha256_int_array(ops_can_leg[mask])
    h_pos_cur = sha256_int_array(pos_cur_leg[mask])
    h_pos_can = sha256_int_array(pos_can_leg[mask])
    ops_vs_eqv02[win_key] = {
        "ops_current_matches_eqv02": h_ops_cur == eqv02_win["operational_target_array"]["sha256_current"],
        "ops_canonical_matches_eqv02": h_ops_can == eqv02_win["operational_target_array"]["sha256_canonical"],
        "pos_current_matches_eqv02": h_pos_cur == eqv02_win["physical_position_array_bonus"]["sha256_current"],
        "pos_canonical_matches_eqv02": h_pos_can == eqv02_win["physical_position_array_bonus"]["sha256_canonical"],
    }
ops_vs_eqv02_ok = all(v["ops_current_matches_eqv02"] and v["ops_canonical_matches_eqv02"]
                      and v["pos_current_matches_eqv02"] and v["pos_canonical_matches_eqv02"]
                      for v in ops_vs_eqv02.values())
assert ops_vs_eqv02_ok, f"operational target / position arrays diverge from EQV02's recorded hashes: {ops_vs_eqv02}"
print(f"[EQV03-A] this script's operational target + physical position arrays reproduce EQV02's "
      f"own recorded hashes exactly, both windows -- proceeding to PnL comparison.", flush=True)

# =========================================================================================
# 6. PnL EQUALITY -- the genuinely new question this script answers: CURRENT_FORM vs
#    CANONICAL_FORM, per-bar and per-day, both price bases.
# =========================================================================================
def daily_pnl(bar_pnl, sess_dates):
    return pd.DataFrame({"sess": sess_dates, "pnl": bar_pnl}).groupby("sess")["pnl"].sum()


def compare_pnl(label, pnl_cur, pnl_can, mask, sess_dates):
    bar_cur = pnl_cur[mask]
    bar_can = pnl_can[mask]
    bar_equal = np.array_equal(bar_cur, bar_can)  # exact float equality, not np.isclose
    n_bar_mismatch = int(np.sum(bar_cur != bar_can))
    max_abs_bar_diff = float(np.max(np.abs(bar_cur - bar_can))) if len(bar_cur) else 0.0

    d_cur = daily_pnl(pnl_cur[mask], sess_dates[mask])
    d_can = daily_pnl(pnl_can[mask], sess_dates[mask])
    d_cur, d_can = d_cur.align(d_can, fill_value=0.0)
    daily_equal = np.array_equal(d_cur.to_numpy(), d_can.to_numpy())
    n_daily_mismatch = int(np.sum(d_cur.to_numpy() != d_can.to_numpy()))
    max_abs_daily_diff = float(np.max(np.abs(d_cur.to_numpy() - d_can.to_numpy()))) if len(d_cur) else 0.0

    net_cur = float(bar_cur.sum())
    net_can = float(bar_can.sum())

    sha_bar_cur = sha256_float_array(bar_cur)
    sha_bar_can = sha256_float_array(bar_can)
    sha_daily_cur = sha256_float_array(d_cur.to_numpy())
    sha_daily_can = sha256_float_array(d_can.to_numpy())

    mismatch_examples = []
    if n_bar_mismatch:
        idxs = np.where(bar_cur != bar_can)[0][:25]
        for i in idxs:
            mismatch_examples.append({
                "bar_offset_in_window": int(i), "pnl_current": float(bar_cur[i]),
                "pnl_canonical": float(bar_can[i]), "diff": float(bar_cur[i] - bar_can[i]),
            })

    return {
        "label": label,
        "n_bars": int(mask.sum()),
        "n_sessions": int(len(d_cur)),
        "bar_pnl": {
            "bit_identical": bool(bar_equal), "n_mismatches": n_bar_mismatch,
            "max_abs_diff": max_abs_bar_diff,
            "sha256_current": sha_bar_cur, "sha256_canonical": sha_bar_can,
        },
        "daily_pnl": {
            "bit_identical": bool(daily_equal), "n_mismatches": n_daily_mismatch,
            "max_abs_diff": max_abs_daily_diff,
            "sha256_current": sha_daily_cur, "sha256_canonical": sha_daily_can,
        },
        "net_total": {
            "current": round(net_cur, 10), "canonical": round(net_can, 10),
            "diff": round(net_cur - net_can, 10), "bit_identical": net_cur == net_can,
        },
        "mismatch_examples_capped_25": mismatch_examples,
    }


sess_dates_arr = sd  # numpy array of session dates, aligned to bars

comparisons = {
    "legacy_nq_proxy": {
        "primary_claude_canonical": compare_pnl("legacy_nq_proxy / CLAUDE.md canonical window (2023-01-01..2025-02-02)",
                                                 pnl_cur_leg, pnl_can_leg, mask_canonical, sess_dates_arr),
        "certified_dev_window": compare_pnl("legacy_nq_proxy / Product A certified dev window (..2026-05-31)",
                                             pnl_cur_leg, pnl_can_leg, mask_dev_window, sess_dates_arr),
        "secondary_fuller_history": compare_pnl("legacy_nq_proxy / fuller history",
                                                 pnl_cur_leg, pnl_can_leg, mask_fuller, sess_dates_arr),
    },
    "genuine_mnq": {
        "primary_claude_canonical": compare_pnl("genuine_mnq / CLAUDE.md canonical window (2023-01-01..2025-02-02)",
                                                 pnl_cur_gen, pnl_can_gen, mask_canonical, sess_dates_arr),
        "certified_dev_window": compare_pnl("genuine_mnq / Product A certified dev window (..2026-05-31)",
                                             pnl_cur_gen, pnl_can_gen, mask_dev_window, sess_dates_arr),
        "secondary_fuller_history": compare_pnl("genuine_mnq / fuller history",
                                                 pnl_cur_gen, pnl_can_gen, mask_fuller, sess_dates_arr),
    },
}

all_bit_identical = all(
    comparisons[basis][win]["bar_pnl"]["bit_identical"] and comparisons[basis][win]["daily_pnl"]["bit_identical"]
    for basis in comparisons for win in comparisons[basis]
)
print(f"[EQV03-A] PnL equality (CURRENT_FORM vs CANONICAL_FORM), all bases/windows bit-identical: "
      f"{all_bit_identical}", flush=True)
for basis in comparisons:
    for win, rep in comparisons[basis].items():
        print(f"  {basis}/{win}: bar_pnl bit_identical={rep['bar_pnl']['bit_identical']} "
              f"daily_pnl bit_identical={rep['daily_pnl']['bit_identical']} "
              f"net_current={rep['net_total']['current']:.2f} net_canonical={rep['net_total']['canonical']:.2f}",
              flush=True)

# =========================================================================================
# 7. CROSS-CHECK vs campaign certified figures -- must pass BEFORE trusting the comparison
#    above (a bug that shifted both forms identically would still pass bit-identity but fail
#    this external check).
# =========================================================================================
devwin_leg_cur = comparisons["legacy_nq_proxy"]["certified_dev_window"]["net_total"]["current"]
devwin_leg_can = comparisons["legacy_nq_proxy"]["certified_dev_window"]["net_total"]["canonical"]
devwin_gen_cur = comparisons["genuine_mnq"]["certified_dev_window"]["net_total"]["current"]
devwin_gen_can = comparisons["genuine_mnq"]["certified_dev_window"]["net_total"]["canonical"]
claude_canon_leg_cur = comparisons["legacy_nq_proxy"]["primary_claude_canonical"]["net_total"]["current"]
claude_canon_leg_can = comparisons["legacy_nq_proxy"]["primary_claude_canonical"]["net_total"]["canonical"]
ext_leg_cur = comparisons["legacy_nq_proxy"]["secondary_fuller_history"]["net_total"]["current"]
ext_leg_can = comparisons["legacy_nq_proxy"]["secondary_fuller_history"]["net_total"]["canonical"]
ext_gen_cur = comparisons["genuine_mnq"]["secondary_fuller_history"]["net_total"]["current"]
ext_gen_can = comparisons["genuine_mnq"]["secondary_fuller_history"]["net_total"]["canonical"]

certified_crosscheck = {
    "note": "The certified $177,924.40 / $178,687.40 figures are Product A's OWN 'canonical dev "
            "window' (2022-01-03..2026-05-31, BASELINE_MODELS.md + health_substrate.py "
            "CANONICAL_END + grid_core.py DEV_END) -- NOT the CLAUDE.md 2023-01-01..2025-02-02 "
            "date range EQV02 borrowed for its array-equality window label. Both are reported "
            "below; only the dev-window figures are checked against the certified $ amounts.",
    "legacy_dev_window_vs_certified_177924_40": {
        "current_form": devwin_leg_cur, "canonical_form": devwin_leg_can,
        "certified": CERTIFIED_A_DEVWIN_NET,
        "current_within_1usd": abs(devwin_leg_cur - CERTIFIED_A_DEVWIN_NET) < 1.0,
        "canonical_within_1usd": abs(devwin_leg_can - CERTIFIED_A_DEVWIN_NET) < 1.0,
    },
    "genuine_mnq_dev_window_vs_price01_178687_40": {
        "current_form": devwin_gen_cur, "canonical_form": devwin_gen_can,
        "certified": CERTIFIED_A_GENUINE_DEVWIN_NET,
        "current_within_1usd": abs(devwin_gen_cur - CERTIFIED_A_GENUINE_DEVWIN_NET) < 1.0,
        "canonical_within_1usd": abs(devwin_gen_can - CERTIFIED_A_GENUINE_DEVWIN_NET) < 1.0,
    },
    "claude_md_canonical_window_net_for_reference_only_no_certified_figure_exists": {
        "current_form": claude_canon_leg_cur, "canonical_form": claude_canon_leg_can,
        "note": "No campaign-certified $ figure exists for this specific narrower date range for "
                "Product A -- reported for transparency only, not used as a pass/fail gate.",
    },
    "legacy_extended_vs_price01_212894_50": {
        "current_form": ext_leg_cur, "canonical_form": ext_leg_can,
        "certified": CERTIFIED_A_LEGACY_EXT_NET,
        "current_within_1usd": abs(ext_leg_cur - CERTIFIED_A_LEGACY_EXT_NET) < 1.0,
        "canonical_within_1usd": abs(ext_leg_can - CERTIFIED_A_LEGACY_EXT_NET) < 1.0,
    },
    "genuine_mnq_extended_vs_price01_213657_50": {
        "current_form": ext_gen_cur, "canonical_form": ext_gen_can,
        "certified": CERTIFIED_A_GENUINE_EXT_NET,
        "current_within_1usd": abs(ext_gen_cur - CERTIFIED_A_GENUINE_EXT_NET) < 1.0,
        "canonical_within_1usd": abs(ext_gen_can - CERTIFIED_A_GENUINE_EXT_NET) < 1.0,
    },
}
_gated_keys = [k for k, v in certified_crosscheck.items() if isinstance(v, dict) and "certified" in v]
certified_crosscheck_all_pass = all(
    certified_crosscheck[k]["current_within_1usd"] and certified_crosscheck[k]["canonical_within_1usd"]
    for k in _gated_keys)
print(f"[EQV03-A] certified-figure cross-check all_pass={certified_crosscheck_all_pass}", flush=True)
for k in _gated_keys:
    v = certified_crosscheck[k]
    print(f"  {k}: current={v['current_form']:.2f} canonical={v['canonical_form']:.2f} "
          f"certified={v['certified']:.2f} pass={v['current_within_1usd'] and v['canonical_within_1usd']}",
          flush=True)

# =========================================================================================
# 8. FINAL VERDICT
# =========================================================================================
verdict = {
    "eqv02_gate": "PASS -- both EQV02 canonical_window_verdict and fuller_history_verdict are EXACT_EQUIVALENCE",
    "reproduction_of_eqv02_arrays": "PASS" if reproduction_ok and ops_vs_eqv02_ok else "FAIL",
    "certified_figure_crosscheck": "PASS" if certified_crosscheck_all_pass else "FAIL -- see certified_crosscheck",
    "pnl_equality_current_vs_canonical": "EXACT_EQUIVALENCE (bit-identical)" if all_bit_identical else "MISMATCH_FOUND -- see comparisons",
    "overall": ("PASS -- PnL is bit-identical between CURRENT_FORM and CANONICAL_FORM under both "
                "price bases, and matches campaign-certified net figures"
                if (all_bit_identical and certified_crosscheck_all_pass and reproduction_ok and ops_vs_eqv02_ok)
                else "FAIL -- see individual gates above"),
    "interpretation": (
        "Since EQV02 already proved the operational target arrays are SHA256-identical between "
        "CURRENT_FORM and CANONICAL_FORM (both windows), and PnL is a deterministic function of "
        "(target array, price array, execution convention) via the shared simulate_overlay() "
        "loop, bit-identical PnL was the expected and required outcome -- confirmed here "
        "explicitly, not assumed, under BOTH the legacy NQ-proxy and genuine-MNQ price bases, "
        "with cross-checks against the campaign's independently-certified net figures passing "
        "in all four (form x basis) combinations before this comparison was trusted."
        if all_bit_identical and certified_crosscheck_all_pass else
        "See comparisons and certified_crosscheck above -- do not treat this as a clean pass; "
        "a PnL divergence on top of an already-proven-identical decision array would indicate a "
        "genuine bug in the PnL-computation layer (e.g. price/quantity read inconsistently "
        "between the two nominally-identical code paths), not a rounding artifact, and must be "
        "investigated to root cause before this task is considered complete."
    ),
}
print(f"[EQV03-A] VERDICT: {verdict['overall']}", flush=True)

# =========================================================================================
# 9. WRITE OUTPUT
# =========================================================================================
result = {
    "task": "EQV03 Product A -- PnL equality (CURRENT_FORM vs CANONICAL_FORM), fed from EQV02's "
            "already-proven-identical operational target arrays, under legacy NQ-proxy and "
            "genuine MNQ pricing",
    "generated": "2026-08-10",
    "gated_on": {
        "eqv01": "research/system_master/EQV01_BEHAVIORAL_CANONICALIZATION/REPORT.md "
                 "(Product A: 243/243 EXACT_EQUIVALENCE, finite-state)",
        "eqv02": "research/system_master/EQV02_FULL_HISTORY_ARRAY_EQUALITY/REPORT.md + "
                 "out/productA_array_equality.json (Product A: full-history EXACT_EQUIVALENCE, "
                 "raw target / operational target / physical position / exposure-event arrays, "
                 "canonical + fuller windows)",
    },
    "execution_convention_source": "research/system_master/EQV02_FULL_HISTORY_ARRAY_EQUALITY/"
                                    "src/01_productA_full_history.py simulate_overlay() -- itself "
                                    "a verbatim-structure copy of grid_core.product_a_exec / U0's "
                                    "product_a_exec_generalized / "
                                    "runs/PRICE01_PRODUCT_A_GENUINE_MNQ/src/01_dual_truth_"
                                    "repricing.py's product_a_exec_generalized inner loop",
    "price_bases_tested": ["legacy_nq_proxy (NQ OHLC, MNQ $2/pt applied directly to NQ price levels)",
                            "genuine_mnq (genuine MNQU6 OHLC, PRICE01 alignment pattern, NQ-proxy "
                            "fallback for bars with no genuine MNQ quote)"],
    "constants_used": {
        "KSolar": KSOLAR, "KBmom": KBMOM, "TiltRescale": TILTRESCALE, "TiltMult": TILTMULT,
        "ShortHalf": SHORTHALF, "K_canonical": K_CANON, "Q_coef_canonical": Q_COEF_CANON,
        "PV_MNQ_A": PV_MNQ_A, "COMM_MNQ_A": COMM_MNQ_A,
    },
    "windows": {
        "primary_claude_canonical": {"start": str(CANON_START.date()), "end": str(CANON_END.date())},
        "secondary_fuller_history": {"start": "2022-01-02", "end": "2026-07-31"},
    },
    "n_bars_total": int(n),
    "n_mnq_genuine_bars": int(is_mnq_genuine.sum()),
    "reproduction_check_vs_eqv02_recorded_hashes": reproduction_check,
    "ops_and_position_vs_eqv02_recorded_hashes": ops_vs_eqv02,
    "price_invariance_of_decision_layer": ops_price_invariance,
    "backstop_events": {
        "current_legacy": len(bs_cur_leg), "canonical_legacy": len(bs_can_leg),
        "current_genuine": len(bs_cur_gen), "canonical_genuine": len(bs_can_gen),
    },
    "pnl_comparisons": comparisons,
    "certified_figure_crosscheck": certified_crosscheck,
    "verdict": verdict,
    "runtime_seconds": round(time.time() - T0, 1),
}

out_path = os.path.join(OUT_DIR, "productA_pnl_equality.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, default=str)

print(f"[EQV03-A] wrote {out_path} (total runtime {time.time() - T0:.1f}s)", flush=True)
