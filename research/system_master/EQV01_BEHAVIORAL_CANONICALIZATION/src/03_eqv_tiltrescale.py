"""
EQV01 -- Behavioral Canonicalization
Test 03: TiltRescale representational-precision test.

Question: is substituting TiltRescale=0.91 for the actual code constant
0.9026 EVER capable of changing the rounded, clipped integer output
(Tpp for Product A, Tp for Product B), across every reachable state?

Ground truth (verified by direct .cs reads, see out/00_code_read_notes.md
and the task's own KNOWN CODE FACTS):

Product A (SolarWaveSMMaster_v4.cs, ~L357-364):
    int T   = clip(-10,10, round_away(sumNext/13.0*10.0))
    mm = (T!=0 && tiltState!=0 && sign(T)==tiltState) ? TiltMult : 1.0
    ss = (T<0 && tiltState>0) ? ShortHalf : 1.0
    Tpp = clip(-13,13, round_away(T*mm*ss*TiltRescale))
    (left-to-right double evaluation: ((T*mm)*ss)*TiltRescale, single Round call)

Product B (SolarWaveOneContractNQ_v5.cs, ~L405-445; MNQ sibling identical):
    int T = clip(-10,10, round_away(sumNext/13.0*10.0))
    mm = (sumNext!=0 && tiltState!=0 && sign(sumNext)==tiltState) ? TiltMult : 1.0
    Tp = clip(-13,13, round_away(T*mm*TiltRescale))
    (no ss term at all for Product B -- confirmed genuine, disclosed asymmetry)
    NOTE: mm's gating condition uses sign(sumNext), not sign(T). Prior code-read
    phase proved (by induction over sumNext's integer domain) that sign(sumNext)
    and sign(T) never diverge, and sumNext==0 iff T==0. So driving mm off T's
    sign for this enumeration is behaviorally identical to driving it off
    sumNext's sign -- verified, not assumed (see divergence check below).

Domains used:
    T:         all integers in clip(-10,10)   -> 21 values
    tiltState: Math.Sign(double) range         -> {-1, 0, 1}
    mm, ss:    derived from (T, tiltState) per the real gating logic above,
               NOT assumed independent -- reachability is computed, not guessed.

Rounding: Math.Round(double, MidpointRounding.AwayFromZero), 0 digits, i.e.
    round_away(x) = floor(x+0.5) if x>=0 else ceil(x-0.5)
Python doubles are IEEE-754 binary64, same representation as C# double, and
CPython performs no extended-precision (x87) intermediate arithmetic on
x86-64 -- the left-to-right evaluation order below reproduces the exact
bit-for-bit C# arithmetic sequence (T*mm, then *ss (A only), then *TiltRescale,
then a single Round call).

Two enumerations are run and reported:
  (1) FULL CARTESIAN GRID exactly as specified in the task prompt:
        A: T in [-10,10] x mm in {1.0,1.25} x ss in {1.0,0.5}   (21*2*2 = 84)
        B: T in [-10,10] x mm in {1.0,1.25}                      (21*2   = 42)
      This is a superset of what real (T,tiltState) execution can produce
      (it includes cells that real code can never reach); if the full grid
      matches 100%, the reachable subset trivially matches 100% too. Testing
      the superset is strictly conservative, never less rigorous.
  (2) REACHABILITY-AWARE ENUMERATION via the real (T, tiltState) state space
      (21*3 = 63 states each), which computes mm/ss (or mm) from the actual
      gating conditions -- this is used only to ANNOTATE which cells of the
      cartesian grid are real-reachable vs. structurally impossible, and is
      reported explicitly rather than silently assumed.
"""
import itertools
import json
import math
import os

OUT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "out", "eqv_tiltrescale_results.json")

TILTRESCALE_ACTUAL = 0.9026
TILTRESCALE_TEST = 0.91

TILT_MULT = 1.25          # Product A & B TiltMult default
SHORT_HALF = 0.5           # Product A ShortHalf default (no B analog)

T_VALUES = list(range(-10, 11))          # 21 values, clip(-10,10) domain
TILTSTATE_VALUES = [-1, 0, 1]            # Math.Sign(double) range
MM_VALUES = [1.0, TILT_MULT]             # {1.0, 1.25}
SS_VALUES = [1.0, SHORT_HALF]            # {1.0, 0.5}


def round_away(x: float) -> int:
    """Math.Round(double, MidpointRounding.AwayFromZero), 0 digits."""
    if x >= 0.0:
        return int(math.floor(x + 0.5))
    else:
        return int(math.ceil(x - 0.5))


def clip(lo: int, hi: int, x: int) -> int:
    return max(lo, min(hi, x))


def tpp_productA(T: int, mm: float, ss: float, tilt_rescale: float) -> int:
    """Left-to-right double evaluation matching C#: ((T*mm)*ss)*TiltRescale."""
    raw = ((float(T) * mm) * ss) * tilt_rescale
    return clip(-13, 13, round_away(raw))


def tp_productB(T: int, mm: float, tilt_rescale: float) -> int:
    """Left-to-right double evaluation matching C#: (T*mm)*TiltRescale."""
    raw = (float(T) * mm) * tilt_rescale
    return clip(-13, 13, round_away(raw))


def mm_ss_productA(T: int, tiltState: int):
    """Real gating logic, driven off sign(T) per Product A's own decoder."""
    signT = (T > 0) - (T < 0)  # Math.Sign semantics: -1,0,1
    mm = TILT_MULT if (T != 0 and tiltState != 0 and signT == tiltState) else 1.0
    ss = SHORT_HALF if (T < 0 and tiltState > 0) else 1.0
    return mm, ss


def mm_productB(T: int, tiltState: int):
    """Real gating logic. Uses sign(sumNext) in the real code; driven here
    off sign(T) because sign(sumNext) and sign(T) are proven never to
    diverge (sumNext==0 iff T==0, and signs otherwise match -- see
    divergence_check below, verified independently in this script too)."""
    signT = (T > 0) - (T < 0)
    mm = TILT_MULT if (T != 0 and tiltState != 0 and signT == tiltState) else 1.0
    return mm


# ---------------------------------------------------------------------------
# Independent re-verification (inside this script, not just trusted from the
# prior phase) that sign(sumNext) never diverges from sign(T), and that
# sumNext==0 iff T==0. This licenses using sign(T) as a stand-in for
# sign(sumNext) in the Product B mm-gate above.
# ---------------------------------------------------------------------------
divergence_examples = []
for sumNext in range(-13, 14):
    T_from_sumNext = clip(-10, 10, round_away((sumNext / 13.0) * 10.0))
    sign_sumNext = (sumNext > 0) - (sumNext < 0)
    sign_T = (T_from_sumNext > 0) - (T_from_sumNext < 0)
    zero_mismatch = (sumNext == 0) != (T_from_sumNext == 0)
    if sign_sumNext != sign_T or zero_mismatch:
        divergence_examples.append({
            "sumNext": sumNext, "T": T_from_sumNext,
            "sign_sumNext": sign_sumNext, "sign_T": sign_T,
        })

divergence_check = {
    "claim": "sign(sumNext) never diverges from sign(T); sumNext==0 iff T==0",
    "sumNext_domain_tested": [-13, 13],
    "divergences_found": len(divergence_examples),
    "divergence_examples": divergence_examples,
    "verdict": "CONFIRMED_NO_DIVERGENCE" if not divergence_examples else "DIVERGENCE_FOUND",
}

# ===========================================================================
# (1) FULL CARTESIAN GRID -- exactly the enumeration specified in the prompt
# ===========================================================================

productA_grid_results = []
productA_grid_mismatches = []
for T, mm, ss in itertools.product(T_VALUES, MM_VALUES, SS_VALUES):
    actual = tpp_productA(T, mm, ss, TILTRESCALE_ACTUAL)
    test = tpp_productA(T, mm, ss, TILTRESCALE_TEST)
    match = (actual == test)
    row = {"T": T, "mm": mm, "ss": ss, "Tpp_actual": actual, "Tpp_test": test, "match": match}
    productA_grid_results.append(row)
    if not match:
        productA_grid_mismatches.append(row)

productB_grid_results = []
productB_grid_mismatches = []
for T, mm in itertools.product(T_VALUES, MM_VALUES):
    actual = tp_productB(T, mm, TILTRESCALE_ACTUAL)
    test = tp_productB(T, mm, TILTRESCALE_TEST)
    match = (actual == test)
    row = {"T": T, "mm": mm, "Tp_actual": actual, "Tp_test": test, "match": match}
    productB_grid_results.append(row)
    if not match:
        productB_grid_mismatches.append(row)

# ===========================================================================
# (2) REACHABILITY-AWARE ENUMERATION via real (T, tiltState) state space --
#     used to annotate which cartesian cells are actually reachable, and as
#     a second, independently-derived exhaustive test (should agree with (1)
#     on every state it covers).
# ===========================================================================

productA_reach_results = []
productA_reach_mismatches = []
reachable_A_cells = set()
for T, tiltState in itertools.product(T_VALUES, TILTSTATE_VALUES):
    mm, ss = mm_ss_productA(T, tiltState)
    reachable_A_cells.add((mm, ss))
    actual = tpp_productA(T, mm, ss, TILTRESCALE_ACTUAL)
    test = tpp_productA(T, mm, ss, TILTRESCALE_TEST)
    match = (actual == test)
    row = {"T": T, "tiltState": tiltState, "mm": mm, "ss": ss,
           "Tpp_actual": actual, "Tpp_test": test, "match": match}
    productA_reach_results.append(row)
    if not match:
        productA_reach_mismatches.append(row)

all_A_cells = set(itertools.product(MM_VALUES, SS_VALUES))
unreachable_A_cells = sorted(all_A_cells - reachable_A_cells)

productB_reach_results = []
productB_reach_mismatches = []
reachable_B_mm = set()
for T, tiltState in itertools.product(T_VALUES, TILTSTATE_VALUES):
    mm = mm_productB(T, tiltState)
    reachable_B_mm.add((T, mm))
    actual = tp_productB(T, mm, TILTRESCALE_ACTUAL)
    test = tp_productB(T, mm, TILTRESCALE_TEST)
    match = (actual == test)
    row = {"T": T, "tiltState": tiltState, "mm": mm,
           "Tp_actual": actual, "Tp_test": test, "match": match}
    productB_reach_results.append(row)
    if not match:
        productB_reach_mismatches.append(row)

all_B_cells = set(itertools.product(T_VALUES, MM_VALUES))
unreachable_B_cells = sorted(all_B_cells - reachable_B_mm)

# ===========================================================================
# Summary / classification
# ===========================================================================

productA_grid_n = len(productA_grid_results)
productA_grid_matches = sum(1 for r in productA_grid_results if r["match"])
productB_grid_n = len(productB_grid_results)
productB_grid_matches = sum(1 for r in productB_grid_results if r["match"])

productA_reach_n = len(productA_reach_results)
productA_reach_matches = sum(1 for r in productA_reach_results if r["match"])
productB_reach_n = len(productB_reach_results)
productB_reach_matches = sum(1 for r in productB_reach_results if r["match"])

total_states = productA_grid_n + productB_grid_n
total_matches = productA_grid_matches + productB_grid_matches

overall_exact = (
    productA_grid_matches == productA_grid_n
    and productB_grid_matches == productB_grid_n
    and productA_reach_matches == productA_reach_n
    and productB_reach_matches == productB_reach_n
)

classification = (
    "REPRESENTATIONAL_PRECISION"
    if overall_exact else
    "BEHAVIORAL_DEGREE_OF_FREEDOM (mismatch found -- NOT equivalent)"
)

results = {
    "test": "TiltRescale 0.9026 (actual) vs 0.91 (recalled/test) -- rounded+clipped output equivalence",
    "constants": {
        "TiltRescale_actual": TILTRESCALE_ACTUAL,
        "TiltRescale_test": TILTRESCALE_TEST,
        "TiltMult": TILT_MULT,
        "ShortHalf": SHORT_HALF,
    },
    "divergence_check_sumNext_vs_T_sign": divergence_check,
    "product_A": {
        "description": "Tpp = clip(-13,13, round_away(T*mm*ss*TiltRescale)), left-to-right double eval",
        "full_cartesian_grid": {
            "domain": "T in [-10,10] (21) x mm in {1.0,1.25} (2) x ss in {1.0,0.5} (2) = 84 states",
            "n_states": productA_grid_n,
            "n_matches": productA_grid_matches,
            "exact_match_rate": productA_grid_matches / productA_grid_n,
            "mismatches": productA_grid_mismatches,
        },
        "reachability_aware_enumeration": {
            "domain": "T in [-10,10] (21) x tiltState in {-1,0,1} (3) = 63 states; mm/ss derived from real gating logic",
            "n_states": productA_reach_n,
            "n_matches": productA_reach_matches,
            "exact_match_rate": productA_reach_matches / productA_reach_n,
            "mismatches": productA_reach_mismatches,
            "reachable_mm_ss_cells": sorted(reachable_A_cells),
            "unreachable_mm_ss_cells_in_full_grid": unreachable_A_cells,
            "unreachability_reason": (
                "(mm=1.25, ss=0.5) is structurally unreachable: ss=0.5 requires "
                "(T<0 AND tiltState>0) i.e. tiltState=1, but mm=1.25 requires "
                "sign(T)==tiltState; when T<0, sign(T)=-1 != tiltState=1, so mm "
                "collapses to 1.0 whenever ss=0.5. The full cartesian grid tests "
                "this unreachable cell anyway (strictly conservative superset)."
            ),
        },
    },
    "product_B": {
        "description": "Tp = clip(-13,13, round_away(T*mm*TiltRescale)), left-to-right double eval, NO ss term (disclosed asymmetry vs A, preserved)",
        "full_cartesian_grid": {
            "domain": "T in [-10,10] (21) x mm in {1.0,1.25} (2) = 42 states",
            "n_states": productB_grid_n,
            "n_matches": productB_grid_matches,
            "exact_match_rate": productB_grid_matches / productB_grid_n,
            "mismatches": productB_grid_mismatches,
        },
        "reachability_aware_enumeration": {
            "domain": "T in [-10,10] (21) x tiltState in {-1,0,1} (3) = 63 states; mm derived from real gating logic (sign(sumNext) proxied by sign(T), justified by divergence_check above)",
            "n_states": productB_reach_n,
            "n_matches": productB_reach_matches,
            "exact_match_rate": productB_reach_matches / productB_reach_n,
            "mismatches": productB_reach_mismatches,
            "unreachable_T_mm_cells_in_full_grid": [
                {"T": t, "mm": mm} for (t, mm) in unreachable_B_cells
            ],
            "unreachability_reason": (
                "(T=0, mm=1.25) is structurally unreachable: mm=1.25 requires T!=0. "
                "The full cartesian grid tests this unreachable cell anyway "
                "(strictly conservative superset)."
            ),
        },
    },
    "overall_summary": {
        "total_states_enumerated_full_grids": total_states,
        "total_matches_full_grids": total_matches,
        "exact_match_rate_full_grids": total_matches / total_states,
        "total_states_enumerated_all_four_passes": (
            productA_grid_n + productB_grid_n + productA_reach_n + productB_reach_n
        ),
        "total_matches_all_four_passes": (
            productA_grid_matches + productB_grid_matches + productA_reach_matches + productB_reach_matches
        ),
        "all_four_passes_100_percent": overall_exact,
        "classification": classification,
    },
}

os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
with open(OUT_PATH, "w") as f:
    json.dump(results, f, indent=2)

print(json.dumps(results["overall_summary"], indent=2))
print(f"\nWrote: {OUT_PATH}")
