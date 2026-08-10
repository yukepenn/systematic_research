#!/usr/bin/env python3
"""
EQV01 -- Product B behavioral canonicalization audit.

ZERO-ALPHA-BUDGET AUDIT. Pure mathematical/behavioral equivalence proof over the
FULL reachable finite state space of Product B's decoder + hysteresis state
machine (SolarWaveOneContractNQ_v5.cs, lines ~405-445, re-read and re-verified
against the file this session -- see verification block below).

Ground truth constants, re-read from src/ninjascript/SolarWaveOneContractNQ_v5.cs
this session (lines 143-145, 405-445):
    TiltSma = 50; TiltMult = 1.25; TiltRescale = 0.9026;
    WSolar = 0.7086; WBmom = 2.83; BmomBandDays = 14;
    EntryLevel = 3.0; ExitLevel = 1.0;   // frozen seq-318, comment says "not a free parameter"

    int T   = clip(-10,10, round_away(sumNext/13.0*10.0))
    mm      = (sumNext!=0 && tiltState!=0 && sign(sumNext)==tiltState) ? TiltMult : 1.0
              [confirmed: uses sign(sumNext), NOT sign(T) -- line 408 in the real file]
    Tp      = clip(-13,13, round_away(T*mm*TiltRescale))
    M       = WSolar*Tp + WBmom*bmomPos     [continuous double, never rounded/clamped -- confirmed,
                                              no Math.Round/Max/Min call on M anywhere in the file]

Hysteresis (forceFlat and entryBlocked both assumed false for this enumeration, per task
instructions: both are session-boundary time gates, orthogonal to the Q_B canonicalization
question, not part of the decoder/state-machine math under test):
    p==0:  M>=EntryLevel -> 1 ; M<=-EntryLevel -> -1 ; else 0
    p==1:  M<=-EntryLevel -> -1 (reversal) ; elif M<=ExitLevel -> 0 ; else 1 (hold)
    p==-1: M>=EntryLevel -> 1  (reversal) ; elif M>=-ExitLevel -> 0 ; else -1 (hold)

*** DISCLOSED DISCREPANCY: the owner recalled Product B's hysteresis thresholds as
"+5/+1, -5/-1". The REAL code (re-verified this session, line 145) is
EntryLevel=3.0, ExitLevel=1.0 -- i.e. hysteresis(3,1), matching BASELINE_MODELS.md:469's own
"Discrete hysteresis(3,1)" description. This script tests the owner's recollection EXACTLY AS
RECALLED (part a, entry=5/exit=1) against the REAL code's true state machine (which itself
always uses EntryLevel=3.0/ExitLevel=1.0 on M -- never on 5/1). It does NOT substitute 5/1 into
the real code. Part (b) is a separate, explicitly-diagnostic derivation of what a threshold on
Q_B = Tp + 4*bmomPos would need to be to best approximate the *real* 3.0/1.0-on-M state machine.
***

Reachable state space (per prior-phase code-read facts, independently re-derivable from the .cs
domains established in this session's grep/read):
    sumNext  in [-13, 13]  (integer, 27 values -- sum of 13 members each in {-1,0,1})
    tiltState in {-1, 0, 1}                          (Math.Sign(double) range)
    bmomPos   in {-1, 0, 1}                          (proven 3-state int, both files)
    p (prior physical position) in {-1, 0, 1}
Full Cartesian product = 27 * 3 * 3 * 3 = 729 states. All four axes are structurally independent
state variables in the .cs (no cross-axis domain restriction is implied by any of the decoder
math), so the full product is the reachable enumeration space for this audit.
"""

import json
import math
from itertools import product
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants -- re-verified against src/ninjascript/SolarWaveOneContractNQ_v5.cs
# lines 143-145 and 405-445 in this session (Grep + Read, see task transcript).
# ---------------------------------------------------------------------------
TILT_MULT = 1.25
TILT_RESCALE = 0.9026
W_SOLAR = 0.7086
W_BMOM = 2.83
ENTRY_LEVEL = 3.0
EXIT_LEVEL = 1.0

# Owner's exact recollection, tested AS RECALLED (not silently corrected).
RECALLED_BMOM_COEF = 4.0
RECALLED_ENTRY = 5.0
RECALLED_EXIT = 1.0

# Diagnostic-only derived thresholds: if M ~= WSolar * Q_B (using the SAME approximate
# coefficient 4, not the exact WBmom/WSolar ratio), then the M-space boundaries EntryLevel=3.0 /
# ExitLevel=1.0 correspond to Q_B-space boundaries of EntryLevel/WSolar, ExitLevel/WSolar.
DIAG_ENTRY = ENTRY_LEVEL / W_SOLAR
DIAG_EXIT = EXIT_LEVEL / W_SOLAR

TRUE_BMOM_RATIO = W_BMOM / W_SOLAR  # the *exact* ratio Q_B's "4" is standing in for


def round_away(x: float) -> int:
    """Replicate C# Math.Round(double, MidpointRounding.AwayFromZero) to 0 digits."""
    if x >= 0:
        return math.floor(x + 0.5)
    else:
        return math.ceil(x - 0.5)


def clip(lo: int, hi: int, x: int) -> int:
    return max(lo, min(hi, x))


def sign(x) -> int:
    return (x > 0) - (x < 0)


def decode_M(sumNext: int, tiltState: int, bmomPos: int):
    """Product B decoder, byte-for-byte per .cs lines 405-410."""
    T = clip(-10, 10, round_away(sumNext / 13.0 * 10.0))
    mm = TILT_MULT if (sumNext != 0 and tiltState != 0 and sign(sumNext) == tiltState) else 1.0
    Tp = clip(-13, 13, round_away(T * mm * TILT_RESCALE))
    M = W_SOLAR * Tp + W_BMOM * bmomPos
    return T, mm, Tp, M


def hysteresis_next(value: float, entry: float, exitL: float, p: int) -> int:
    """Generic hysteresis state machine, parameterized on (entry, exit) thresholds applied
    to `value`. Structurally identical to .cs lines 428-445 (forceFlat/entryBlocked assumed
    false, per task scope)."""
    if p == 0:
        if value >= entry:
            return 1
        elif value <= -entry:
            return -1
        else:
            return 0
    elif p > 0:
        if value <= -entry:
            return -1
        elif value <= exitL:
            return 0
        else:
            return 1
    else:
        if value >= entry:
            return 1
        elif value >= -exitL:
            return 0
        else:
            return -1


def main():
    out_dir = Path(__file__).resolve().parent.parent / "out"
    out_dir.mkdir(parents=True, exist_ok=True)

    sumNext_range = range(-13, 14)
    tilt_range = (-1, 0, 1)
    bmom_range = (-1, 0, 1)
    p_range = (-1, 0, 1)

    all_states = []
    mismatches_a = []  # AS-RECALLED (entry=5, exit=1, coef=4) vs TRUE (M-based, 3/1)
    mismatches_b = []  # DIAGNOSTIC (entry=DIAG_ENTRY, exit=DIAG_EXIT, coef=4) vs TRUE

    n = 0
    match_a = 0
    match_b = 0

    for sumNext, tiltState, bmomPos, p in product(sumNext_range, tilt_range, bmom_range, p_range):
        n += 1
        T, mm, Tp, M = decode_M(sumNext, tiltState, bmomPos)
        next_true = hysteresis_next(M, ENTRY_LEVEL, EXIT_LEVEL, p)

        Q_B = Tp + RECALLED_BMOM_COEF * bmomPos  # shared Tp, per task's PROPOSED_CANONICAL_FORM

        next_recalled = hysteresis_next(Q_B, RECALLED_ENTRY, RECALLED_EXIT, p)
        next_diag = hysteresis_next(Q_B, DIAG_ENTRY, DIAG_EXIT, p)

        rec = dict(
            sumNext=sumNext, tiltState=tiltState, bmomPos=bmomPos, p=p,
            T=T, mm=mm, Tp=Tp, M=round(M, 10), Q_B=Q_B,
            next_true=next_true, next_as_recalled=next_recalled, next_diag=next_diag,
        )
        all_states.append(rec)

        if next_recalled == next_true:
            match_a += 1
        else:
            mismatches_a.append(rec)

        if next_diag == next_true:
            match_b += 1
        else:
            mismatches_b.append(rec)

    assert n == 27 * 3 * 3 * 3 == 729

    # ------------------------------------------------------------------
    # Structural diagnostic: can ANY threshold pair on Q_B = Tp + 4*bmomPos ever exactly
    # reproduce the true M-based state machine? Because WBmom/WSolar = 3.99379... != 4
    # exactly, distinct (Tp, bmomPos) pairs sharing the same Q_B can map to slightly
    # different M values. If those M values ever straddle a decision boundary
    # ({-3,-1,+1,+3}), then Q_B is not a sufficient statistic for the true decision and
    # NO threshold choice (on Q_B alone) can achieve exact equivalence, regardless of (a)/(b).
    # ------------------------------------------------------------------
    boundaries = [-ENTRY_LEVEL, -EXIT_LEVEL, EXIT_LEVEL, ENTRY_LEVEL]
    qb_groups = {}
    for Tp in range(-13, 14):
        for bmomPos in bmom_range:
            Q = Tp + RECALLED_BMOM_COEF * bmomPos
            M = W_SOLAR * Tp + W_BMOM * bmomPos
            qb_groups.setdefault(Q, []).append((Tp, bmomPos, M))

    collisions = []
    for Q, members in sorted(qb_groups.items()):
        if len(members) < 2:
            continue
        m_values = [m for (_, _, m) in members]
        lo, hi = min(m_values), max(m_values)
        straddled = [b for b in boundaries if lo < b < hi]
        if straddled:
            collisions.append(dict(
                Q_B=Q,
                members=[dict(Tp=t, bmomPos=b, M=round(m, 10)) for (t, b, m) in members],
                M_range=[round(lo, 10), round(hi, 10)],
                boundaries_straddled=straddled,
            ))

    structural_equivalence_possible = (len(collisions) == 0)

    exact_match_rate_a = match_a / n
    exact_match_rate_b = match_b / n

    # Boundary-clustering check for part (a) mismatches: distance from Q_B to nearest of
    # {-RECALLED_ENTRY, -RECALLED_EXIT, RECALLED_EXIT, RECALLED_ENTRY} and to nearest of the
    # TRUE M boundaries {-3,-1,1,3} expressed back in Q_B units (M boundary / WSolar).
    true_boundaries_in_qb_units = [b / W_SOLAR for b in boundaries]

    def nearest_dist(x, pts):
        return min(abs(x - b) for b in pts)

    mism_a_near_recalled_boundary = sum(
        1 for r in mismatches_a
        if nearest_dist(r["Q_B"], [-RECALLED_ENTRY, -RECALLED_EXIT, RECALLED_EXIT, RECALLED_ENTRY]) <= 1.0
    )
    mism_a_near_true_boundary = sum(
        1 for r in mismatches_a
        if nearest_dist(r["Q_B"], true_boundaries_in_qb_units) <= 1.0
    )

    # ------------------------------------------------------------------
    # Report
    # ------------------------------------------------------------------
    report = dict(
        meta=dict(
            task="EQV01 Product B canonicalization -- Q_B = Tp + 4*bmomPos vs real hysteresis(3,1) on M",
            constants=dict(
                TiltMult=TILT_MULT, TiltRescale=TILT_RESCALE, WSolar=W_SOLAR, WBmom=W_BMOM,
                EntryLevel=ENTRY_LEVEL, ExitLevel=EXIT_LEVEL,
                WBmom_over_WSolar=TRUE_BMOM_RATIO,
            ),
            recalled_hypothesis=dict(
                bmom_coef=RECALLED_BMOM_COEF, entry=RECALLED_ENTRY, exit=RECALLED_EXIT,
                note="Owner recollection, tested EXACTLY AS RECALLED -- not silently corrected.",
            ),
            real_code_thresholds=dict(
                entry=ENTRY_LEVEL, exit=EXIT_LEVEL,
                note=("DISCLOSED DISCREPANCY: real EntryLevel/ExitLevel are 3.0/1.0 "
                      "(re-verified src/ninjascript/SolarWaveOneContractNQ_v5.cs line 145, "
                      "matches BASELINE_MODELS.md:469 'Discrete hysteresis(3,1)'), NOT the "
                      "recalled 5/1. This script tests the owner's 5/1 recollection against "
                      "the real 3.0/1.0-on-M state machine, does not substitute 5/1 into the "
                      "real code."),
            ),
            diagnostic_thresholds=dict(
                entry=DIAG_ENTRY, exit=DIAG_EXIT,
                derivation="EntryLevel/WSolar , ExitLevel/WSolar (only valid if WBmom/WSolar ~= 4, which it is not exactly)",
            ),
            state_space=dict(
                sumNext_domain=[-13, 13], tiltState_domain=[-1, 0, 1],
                bmomPos_domain=[-1, 0, 1], prior_position_domain=[-1, 0, 1],
                total_states=n,
                forceFlat_assumed=False, entryBlocked_assumed=False,
                assumption_note=("Both flags are session-boundary time gates orthogonal to the "
                                  "decoder/hysteresis math under test, per task scope; assumed "
                                  "false for all 729 states, matching the task's own "
                                  "CURRENT_FORM / PROPOSED_CANONICAL_FORM pseudocode (which "
                                  "itself omits both flags)."),
            ),
        ),
        part_a_as_recalled=dict(
            description="Q_B = Tp + 4*bmomPos, hysteresis(entry=5.0, exit=1.0) vs TRUE M-based hysteresis(3.0,1.0)",
            total_states=n,
            exact_matches=match_a,
            mismatches=n - match_a,
            exact_match_rate=exact_match_rate_a,
            verdict="EXACT_EQUIVALENCE" if match_a == n else "REJECTED",
            mismatches_near_recalled_boundary_within_1Q=mism_a_near_recalled_boundary,
            mismatches_near_true_boundary_within_1Q=mism_a_near_true_boundary,
        ),
        part_b_diagnostic=dict(
            description=(
                f"Diagnostic only (NOT a proposed equivalence test): Q_B = Tp + 4*bmomPos, "
                f"hysteresis(entry={DIAG_ENTRY:.6f}, exit={DIAG_EXIT:.6f}) -- thresholds "
                f"derived as EntryLevel/WSolar and ExitLevel/WSolar -- vs TRUE M-based "
                f"hysteresis(3.0,1.0). Shows what threshold WOULD be needed for a simple "
                f"Tp+4B statistic to best approximate the real state machine, and how close "
                f"it gets."
            ),
            total_states=n,
            exact_matches=match_b,
            mismatches=n - match_b,
            exact_match_rate=exact_match_rate_b,
            verdict="EXACT_EQUIVALENCE" if match_b == n else "REJECTED",
        ),
        structural_diagnostic=dict(
            description=(
                "Because WBmom/WSolar = 2.83/0.7086 = 3.993791... (NOT exactly 4), Q_B = Tp + "
                "4*bmomPos is not always a lossless sufficient statistic for M = WSolar*Tp + "
                "WBmom*bmomPos: distinct (Tp,bmomPos) pairs sharing the same Q_B can map to "
                "slightly different M values (max spread ~2*WSolar*|4-ratio| = "
                f"{2*W_SOLAR*abs(4-TRUE_BMOM_RATIO):.6f}). This checks whether that spread "
                "is ever large enough to straddle a real decision boundary {-3,-1,1,3} -- if "
                "so, NO threshold on Q_B (any value) can achieve exact equivalence, "
                "independent of parts (a)/(b)."
            ),
            true_bmom_over_solar_ratio=TRUE_BMOM_RATIO,
            recalled_coefficient=RECALLED_BMOM_COEF,
            max_M_spread_per_QB_bucket=2 * W_SOLAR * abs(4 - TRUE_BMOM_RATIO),
            num_QB_values_with_multiple_source_pairs=sum(1 for m in qb_groups.values() if len(m) > 1),
            num_boundary_straddling_collisions=len(collisions),
            structural_equivalence_possible=structural_equivalence_possible,
            collisions=collisions,
        ),
        mismatches_part_a_full_list=mismatches_a,
        mismatches_part_b_full_list=mismatches_b,
    )

    out_path = out_dir / "eqv_productB_results.json"
    out_path.write_text(json.dumps(report, indent=2, default=str))

    # ------------------------------------------------------------------
    # Console summary
    # ------------------------------------------------------------------
    print(f"Total states enumerated: {n}")
    print()
    print("=== PART (a) AS-RECALLED: Q_B=Tp+4*bmomPos, hysteresis(5,1) vs TRUE hysteresis(3,1) on M ===")
    print(f"  exact matches: {match_a}/{n} ({exact_match_rate_a*100:.4f}%)")
    print(f"  mismatches: {n - match_a}")
    print(f"  verdict: {'EXACT_EQUIVALENCE' if match_a==n else 'REJECTED'}")
    print()
    print(f"=== PART (b) DIAGNOSTIC: Q_B=Tp+4*bmomPos, hysteresis({DIAG_ENTRY:.4f},{DIAG_EXIT:.4f}) vs TRUE ===")
    print(f"  exact matches: {match_b}/{n} ({exact_match_rate_b*100:.4f}%)")
    print(f"  mismatches: {n - match_b}")
    print(f"  verdict: {'EXACT_EQUIVALENCE' if match_b==n else 'REJECTED'}")
    print()
    print("=== STRUCTURAL DIAGNOSTIC ===")
    print(f"  WBmom/WSolar exact ratio: {TRUE_BMOM_RATIO:.6f} (recalled coef used: {RECALLED_BMOM_COEF})")
    print(f"  QB buckets with >1 source (Tp,bmomPos) pair: {sum(1 for m in qb_groups.values() if len(m)>1)}")
    print(f"  boundary-straddling collisions found: {len(collisions)}")
    print(f"  structural_equivalence_possible (any threshold): {structural_equivalence_possible}")
    print()
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
