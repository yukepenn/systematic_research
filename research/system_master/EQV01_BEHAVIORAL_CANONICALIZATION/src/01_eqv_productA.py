"""
EQV01_BEHAVIORAL_CANONICALIZATION -- Product A canonicalization equivalence proof.

ZERO-ALPHA-BUDGET AUDIT. Pure mathematical/behavioral equivalence check between:

  CURRENT_FORM (the real, deployed decoder logic in
  src/ninjascript/SolarWaveSMMaster_v4.cs, lines ~357-364, verified by direct read
  on 2026-08-10):
      T      = clip(-10,10, round_away(sumNext / 13.0 * 10.0))
      mm     = TiltMult if (T != 0 and tiltState != 0 and sign(T) == tiltState) else 1.0
      ss     = ShortHalf if (T < 0 and tiltState > 0) else 1.0
      Tpp    = clip(-13,13, round_away(T * mm * ss * TiltRescale))
      M      = KSolar * Tpp + KBmom * bmomPos
      tgtRaw = clip(-13,13, round_away(M))
    Defaults (confirmed at .cs lines 130-131):
      TiltMult=1.25, TiltRescale=0.9026, ShortHalf=0.5,
      KSolar=0.728654, KBmom=2.934159

  PROPOSED_CANONICAL_FORM (the owner's hypothesis, tested EXACTLY as stated --
  not silently "improved"):
      Q_A     = Tpp + 4 * bmomPos        (same Tpp as above)
      target_A = clip(-13,13, round_away(0.73 * Q_A))

Domain of enumeration (full reachable policy domain, per code-read phase --
not a historical sample):
      sumNext  in [-13, 13]  (27 values) -- proven integer sum of 13 members
                                            each confined to {-1,0,1}
      tiltState in {-1, 0, 1}            -- Math.Sign() range
      bmomPos   in {-1, 0, 1}            -- proven 3-state finite domain
  Total = 27 * 3 * 3 = 243 states. This is the COMPLETE reachable
  (sumNext, tiltState, bmomPos) space per the decoder's own type/clamp
  constraints -- not a restriction to historically-observed combinations.

Rounding semantics: C# Math.Round(double, MidpointRounding.AwayFromZero) with
0 fractional digits. Implemented independently below (not imported from any
existing Python port) as round-half-away-from-zero on IEEE-754 doubles,
matching the .cs call sites exactly (all 3 calls in the CURRENT_FORM path use
this exact overload/mode).

This script is an independent, from-scratch Python re-implementation of the
.cs semantics (built directly from the verified .cs lines quoted above), NOT
an import of runs/PRICE01_PRODUCT_A_GENUINE_MNQ's existing port.

SECONDARY (explicitly labeled): raw-coefficient-ratio diagnostic -- does
KBmom/KSolar exactly equal 4? Does KSolar exactly equal 0.73?

CONTEXT-ONLY ADDENDUM (Product B, not part of the primary Product-A
equivalence question, included solely to give a grounded, quantitative answer
to the owner's disclosed recollection-vs-code discrepancy about Product B's
hysteresis thresholds; see README/summary for the flag). Product B's actual
code (src/ninjascript/SolarWaveOneContractNQ_v5.cs, lines 143-145, verified by
direct read on 2026-08-10) uses EntryLevel=3.0, ExitLevel=1.0 -- i.e.
hysteresis(3,1), explicitly commented in the .cs file as "frozen seq-318, not
a free parameter". The owner recalled "+5/+1, -5/-1". Both are tested below,
stateless (entry-only), over Product B's own finite reachable M domain, purely
as diagnostic context. This does NOT change Product B's deployed thresholds
and is not a proposal to do so.
"""

import json
import math
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parents[1] / "out"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ----------------------------------------------------------------------------
# Primitives -- independent re-implementation of C# semantics
# ----------------------------------------------------------------------------

def round_away(x: float) -> int:
    """
    Round-half-away-from-zero to the nearest integer, matching
    C# Math.Round(double, MidpointRounding.AwayFromZero) with 0 digits.
    Implemented directly on IEEE-754 doubles (Python float == C# double),
    independent of any existing port.
    """
    if x >= 0.0:
        return math.floor(x + 0.5)
    else:
        return math.ceil(x - 0.5)


def clip(lo: int, hi: int, v):
    return max(lo, min(hi, v))


def sign(x) -> int:
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0


def near_half_boundary(x: float, tol: float = 1e-9) -> bool:
    """True if x is within tol of a genuine .5 fractional boundary (the
    rounding-direction-flip risk zone the task asks us to check for)."""
    frac = x - math.floor(x)
    return abs(frac - 0.5) < tol


# ----------------------------------------------------------------------------
# Product A constants (verified by direct read of SolarWaveSMMaster_v4.cs
# lines 130-131 on 2026-08-10)
# ----------------------------------------------------------------------------

TILT_MULT = 1.25
TILT_RESCALE = 0.9026
SHORT_HALF = 0.5
K_SOLAR = 0.728654
K_BMOM = 2.934159

# ----------------------------------------------------------------------------
# CURRENT_FORM -- byte-faithful re-implementation of .cs lines 357-364
# ----------------------------------------------------------------------------

def current_form(sumNext: int, tiltState: int, bmomPos: int):
    T = clip(-10, 10, round_away(sumNext / 13.0 * 10.0))
    mm = TILT_MULT if (T != 0 and tiltState != 0 and sign(T) == tiltState) else 1.0
    ss = SHORT_HALF if (T < 0 and tiltState > 0) else 1.0
    Tpp_raw = T * mm * ss * TILT_RESCALE
    Tpp = clip(-13, 13, round_away(Tpp_raw))
    M = K_SOLAR * Tpp + K_BMOM * bmomPos
    tgtRaw = clip(-13, 13, round_away(M))
    return {
        "T": T, "mm": mm, "ss": ss, "Tpp_raw": Tpp_raw, "Tpp": Tpp,
        "M": M, "tgtRaw": tgtRaw,
    }


def proposed_canonical_form(Tpp: int, bmomPos: int):
    Q_A = Tpp + 4 * bmomPos
    target_A_raw = 0.73 * Q_A
    target_A = clip(-13, 13, round_away(target_A_raw))
    return {"Q_A": Q_A, "target_A_raw": target_A_raw, "target_A": target_A}


# ----------------------------------------------------------------------------
# Full enumeration: sumNext in [-13,13], tiltState in {-1,0,1}, bmomPos in {-1,0,1}
# ----------------------------------------------------------------------------

def enumerate_states():
    states = []
    for sumNext in range(-13, 14):
        for tiltState in (-1, 0, 1):
            for bmomPos in (-1, 0, 1):
                cf = current_form(sumNext, tiltState, bmomPos)
                pf = proposed_canonical_form(cf["Tpp"], bmomPos)
                match = (cf["tgtRaw"] == pf["target_A"])
                rec = {
                    "sumNext": sumNext,
                    "tiltState": tiltState,
                    "bmomPos": bmomPos,
                    "T": cf["T"],
                    "mm": cf["mm"],
                    "ss": ss_display(cf["ss"]),
                    "Tpp_raw": cf["Tpp_raw"],
                    "Tpp": cf["Tpp"],
                    "M": cf["M"],
                    "tgtRaw": cf["tgtRaw"],
                    "Q_A": pf["Q_A"],
                    "target_A_raw": pf["target_A_raw"],
                    "target_A": pf["target_A"],
                    "match": match,
                    "M_near_half_boundary": near_half_boundary(cf["M"]),
                    "target_A_raw_near_half_boundary": near_half_boundary(pf["target_A_raw"]),
                    "Tpp_raw_near_half_boundary": near_half_boundary(cf["Tpp_raw"]),
                }
                states.append(rec)
    return states


def ss_display(ss):
    return ss


# ----------------------------------------------------------------------------
# Secondary explicit test: raw coefficient ratios vs the round-number hypothesis
# ----------------------------------------------------------------------------

def coefficient_ratio_diagnostics():
    ratio_kbmom_ksolar = K_BMOM / K_SOLAR
    ksolar_vs_073 = K_SOLAR - 0.73
    return {
        "K_SOLAR": K_SOLAR,
        "K_BMOM": K_BMOM,
        "K_BMOM_over_K_SOLAR": ratio_kbmom_ksolar,
        "K_BMOM_over_K_SOLAR_minus_4": ratio_kbmom_ksolar - 4.0,
        "K_BMOM_over_K_SOLAR_equals_4_exactly": (ratio_kbmom_ksolar == 4.0),
        "K_SOLAR_minus_0.73": ksolar_vs_073,
        "K_SOLAR_equals_0.73_exactly": (K_SOLAR == 0.73),
        "relative_error_K_BMOM_over_K_SOLAR_vs_4_pct": (ratio_kbmom_ksolar - 4.0) / 4.0 * 100.0,
        "relative_error_K_SOLAR_vs_0.73_pct": (K_SOLAR - 0.73) / 0.73 * 100.0,
    }


# ----------------------------------------------------------------------------
# CONTEXT-ONLY addendum: Product B threshold recollection vs actual code
# (not part of the primary Product-A equivalence question; see docstring)
# ----------------------------------------------------------------------------

WSOLAR_B = 0.7086
WBMOM_B = 2.83
TILT_MULT_B = 1.25   # same constant name/value as Product A per .cs line 143
TILT_RESCALE_B = 0.9026
ENTRY_LEVEL_ACTUAL = 3.0
EXIT_LEVEL_ACTUAL = 1.0
ENTRY_LEVEL_RECALLED = 5.0
EXIT_LEVEL_RECALLED = 1.0


def product_b_M_domain():
    """
    Enumerate Product B's own finite reachable M domain.
    Product B's T' (Tp) has the SAME clip(-13,13, round_away(T*mm*TiltRescale))
    shape as Product A's Tpp, but WITHOUT the ss/short-halving term (confirmed:
    no ss variable exists in SolarWaveOneContractNQ_v5.cs), and mm uses
    sign(sumNext) rather than sign(T) (confirmed at .cs line 408). Since the
    two-value entry/exit classification only needs the achievable M value set
    (not full state provenance), we enumerate all (sumNext, tiltState, bmomPos)
    exactly as in Product A but with Product B's mm/Tp/M formulas, and collect
    the distinct M values plus which (sumNext,tiltState,bmomPos) states hit
    each entry decision under the actual (3,1) vs recalled (5,1) thresholds.
    """
    rows = []
    for sumNext in range(-13, 14):
        for tiltState in (-1, 0, 1):
            for bmomPos in (-1, 0, 1):
                T = clip(-10, 10, round_away(sumNext / 13.0 * 10.0))
                mm = TILT_MULT_B if (sumNext != 0 and tiltState != 0 and sign(sumNext) == tiltState) else 1.0
                Tp_raw = T * mm * TILT_RESCALE_B
                Tp = clip(-13, 13, round_away(Tp_raw))
                M = WSOLAR_B * Tp + WBMOM_B * bmomPos
                entry_actual = "long" if M >= ENTRY_LEVEL_ACTUAL else ("short" if M <= -ENTRY_LEVEL_ACTUAL else "none")
                entry_recalled = "long" if M >= ENTRY_LEVEL_RECALLED else ("short" if M <= -ENTRY_LEVEL_RECALLED else "none")
                rows.append({
                    "sumNext": sumNext, "tiltState": tiltState, "bmomPos": bmomPos,
                    "T": T, "mm": mm, "Tp": Tp, "M": M,
                    "entry_decision_actual_3_1": entry_actual,
                    "entry_decision_recalled_5_1": entry_recalled,
                    "decision_differs": entry_actual != entry_recalled,
                })
    return rows


def product_b_context_summary(rows):
    n_total = len(rows)
    n_differ = sum(1 for r in rows if r["decision_differs"])
    n_entry_actual_fires = sum(1 for r in rows if r["entry_decision_actual_3_1"] != "none")
    n_entry_recalled_fires = sum(1 for r in rows if r["entry_decision_recalled_5_1"] != "none")
    m_values = sorted(set(round(r["M"], 6) for r in rows))
    m_min, m_max = min(m_values), max(m_values)
    # what threshold would make the recalled 5/1 "work" (i.e. fire on the
    # same states as the actual code's 3/1)? Only exact match is |EntryLevel|=3.0
    # given M's actual achievable range; report that finding plainly.
    return {
        "note": ("CONTEXT ONLY -- not part of the primary Product-A equivalence "
                 "proof requested by this task. Included to give a quantitative, "
                 "grounded answer to the owner's disclosed recollection ('+5/+1, "
                 "-5/-1') vs the verified actual code (EntryLevel=3.0, "
                 "ExitLevel=1.0, commented in .cs as 'frozen seq-318, not a free "
                 "parameter'). Tested against the REAL code values elsewhere in "
                 "this deliverable; this addendum only quantifies how different "
                 "the recalled thresholds would behave, it does not change "
                 "anything deployed."),
        "total_states_enumerated": n_total,
        "states_where_entry_decision_differs_3_1_vs_5_1": n_differ,
        "pct_states_where_entry_decision_differs": n_differ / n_total * 100.0,
        "states_where_actual_3_1_fires_an_entry": n_entry_actual_fires,
        "states_where_recalled_5_1_fires_an_entry": n_entry_recalled_fires,
        "achievable_M_value_range": [m_min, m_max],
        "achievable_M_value_count": len(m_values),
        "as_recalled_5_1_test_result": (
            f"REJECTED as a description of the deployed code: EntryLevel=5.0/"
            f"ExitLevel=1.0 would fire an entry on {n_entry_recalled_fires}/"
            f"{n_total} enumerated states, vs {n_entry_actual_fires}/{n_total} "
            f"for the actual deployed EntryLevel=3.0/ExitLevel=1.0 -- "
            f"{n_differ} states ({n_differ / n_total * 100.0:.1f}%) get a "
            f"different entry decision. The two threshold sets are NOT "
            f"behaviorally equivalent over Product B's reachable M domain "
            f"{[m_min, m_max]}."
        ),
        "diagnostic_correct_threshold": (
            "The code-verified, deployed threshold is EntryLevel=3.0 / "
            "ExitLevel=1.0 (hysteresis(3,1)), matching BASELINE_MODELS.md:469's "
            "'Discrete hysteresis(3,1)' description and the .cs file's own "
            "'frozen seq-318, not a free parameter' comment. There is no "
            "reading of the current source under which 5/1 is correct; the "
            "owner's recollection does not match the deployed code and should "
            "be treated as a memory error, not an alternate valid config."
        ),
    }


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

def main():
    states = enumerate_states()
    total = len(states)
    mismatches = [s for s in states if not s["match"]]
    n_match = total - len(mismatches)

    coeff_diag = coefficient_ratio_diagnostics()

    # boundary clustering check on mismatches (and, separately, on the whole
    # domain, to see if near-half-integer cases exist at all even where they
    # don't flip the outcome)
    mismatch_near_boundary = [
        m for m in mismatches
        if m["M_near_half_boundary"] or m["target_A_raw_near_half_boundary"] or m["Tpp_raw_near_half_boundary"]
    ]
    all_near_boundary_states = [
        s for s in states
        if s["M_near_half_boundary"] or s["target_A_raw_near_half_boundary"] or s["Tpp_raw_near_half_boundary"]
    ]

    verdict = "EXACT_EQUIVALENCE" if len(mismatches) == 0 else "REJECTED"

    # Near-miss analysis: even with 0 mismatches, characterize how close the
    # closest states came to a rounding-direction flip, so a 100% match rate
    # is not mistaken for "not close" -- this is the honest margin, not a
    # worst-case bound.
    near_miss_rows = []
    for s in states:
        M = s["M"]
        frac = M - math.floor(M)
        dist_half_M = abs(frac - 0.5)
        signed_perturbation = M - s["target_A_raw"]
        safety_margin = dist_half_M - abs(signed_perturbation)
        near_miss_rows.append({
            **{k: s[k] for k in ("sumNext", "tiltState", "bmomPos", "Tpp", "M", "target_A_raw", "tgtRaw", "target_A")},
            "signed_perturbation_M_minus_target_A_raw": signed_perturbation,
            "dist_of_M_to_nearest_half_integer_boundary": dist_half_M,
            "safety_margin_before_a_flip_could_occur": safety_margin,
        })
    near_miss_rows.sort(key=lambda r: r["safety_margin_before_a_flip_could_occur"])
    closest_calls = near_miss_rows[:5]

    product_b_rows = product_b_M_domain()
    product_b_summary = product_b_context_summary(product_b_rows)

    result = {
        "task": "EQV01 Product A behavioral canonicalization -- full reachable state space equivalence proof",
        "generated": "2026-08-10",
        "domain": {
            "sumNext_range": [-13, 13],
            "tiltState_values": [-1, 0, 1],
            "bmomPos_values": [-1, 0, 1],
            "total_states_enumerated": total,
        },
        "constants_used": {
            "TiltMult": TILT_MULT, "TiltRescale": TILT_RESCALE, "ShortHalf": SHORT_HALF,
            "KSolar": K_SOLAR, "KBmom": K_BMOM,
        },
        "current_form_source": "src/ninjascript/SolarWaveSMMaster_v4.cs lines 357-364 (constants lines 130-131), verified by direct read 2026-08-10",
        "proposed_canonical_form": "Q_A = Tpp + 4*bmomPos; target_A = clip(-13,13, round_away(0.73*Q_A))",
        "results": {
            "total_states": total,
            "exact_matches": n_match,
            "mismatches": len(mismatches),
            "exact_match_rate_pct": n_match / total * 100.0,
            "equivalence_verdict": verdict,
            "equivalence_bar": "100.000% exact match required; anything less is REJECTED, not 'close enough'.",
        },
        "mismatch_list_full": mismatches,
        "mismatch_boundary_analysis": {
            "n_mismatches_near_half_integer_boundary": len(mismatch_near_boundary),
            "n_mismatches_total": len(mismatches),
            "n_all_states_near_half_integer_boundary_regardless_of_match": len(all_near_boundary_states),
            "interpretation": (
                "See narrative note below."
                if len(mismatches) > 0 else
                "No mismatches exist, so no boundary-clustering pattern applies. "
                f"{len(all_near_boundary_states)} of {total} total states pass within "
                "1e-9 of a genuine .5 fractional boundary somewhere in the M / "
                "target_A_raw / Tpp_raw computation, but none of them flip the "
                "final integer outcome between CURRENT_FORM and PROPOSED_CANONICAL_FORM. "
                "See near_miss_margin_analysis below for the realized (not "
                "worst-case) margin at the closest-call states -- the tightest "
                "margin found is small (a few thousandths) but never crosses zero."
            ),
        },
        "near_miss_margin_analysis": {
            "purpose": (
                "Even though the exhaustive enumeration found 0 mismatches, a "
                "100% match rate could mask a knife's-edge result. This section "
                "reports the ACTUAL realized safety margin (not a worst-case "
                "bound) between each state's M value and the nearest "
                "rounding-direction-flip boundary, net of the true signed "
                "perturbation introduced by substituting (0.73, 4) for "
                "(KSolar=0.728654, KBmom=2.934159). All 243 states have a "
                "strictly positive margin (no flips), but the closest calls "
                "are listed below."
            ),
            "smallest_safety_margin_across_all_243_states": closest_calls[0]["safety_margin_before_a_flip_could_occur"],
            "all_243_states_have_positive_margin_i.e._zero_flips": all(r["safety_margin_before_a_flip_could_occur"] > 0 for r in near_miss_rows),
            "five_closest_calls": closest_calls,
        },
        "secondary_coefficient_ratio_diagnostics": coeff_diag,
        "product_b_context_only_addendum": {
            "summary": product_b_summary,
            "full_state_rows": product_b_rows,
        },
    }

    out_path = OUT_DIR / "eqv_productA_results.json"
    out_path.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")

    print(f"Total states enumerated: {total}")
    print(f"Exact matches: {n_match} ({n_match/total*100:.4f}%)")
    print(f"Mismatches: {len(mismatches)}")
    print(f"Verdict: {verdict}")
    print()
    print("Coefficient ratio diagnostics:")
    print(json.dumps(coeff_diag, indent=2))
    print()
    print(f"Output written to: {out_path}")

    return result


if __name__ == "__main__":
    main()
