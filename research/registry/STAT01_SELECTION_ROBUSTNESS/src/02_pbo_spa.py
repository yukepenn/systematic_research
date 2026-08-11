"""02_pbo_spa.py -- STAT01: Probability of Backtest Overfitting (PBO / CSCV) defensibility
assessment on the VolMult-grid family, plus a Hansen SPA applicability assessment for the campaign's
GRID01/GRID02/PERT01/SIMPLE01 wave.

Per campaign directive sec61-66: do not select the assumption that gives the "best" (most flattering
or most alarming) answer. Per sec63-64 specifically: PBO requires a comparable candidate family AND
an adequate partition structure; if a family is too small/undiverse for a meaningful CSCV estimate,
say so and do NOT output a falsely precise PBO number just because code could compute one. Per sec65:
do not run one global SPA merely to manufacture a p-value if no candidate in the reviewed work was
ever presented as apparently superior to a benchmark.

REUSE, NOT REBUILD: the only candidate family in the registry with (a) a full daily-P&L pool and
(b) pre-existing candidate identities assembled before any scoring (sec63's own requirement) is the
7-config VolMult-grid family (GRID01 G7/G13/G25/G49 + GRID02's 3 endpoints). Its dedup/behavioral-
identity/participation-ratio work was already done by HASH01
(research/registry/HASH01_BEHAVIORAL_POLICY_REGISTRY/out/policy_hash_results.json) and is loaded
here VERBATIM -- this script does not re-run grid_core.py, does not rebuild the daily P&L, and does
not recompute the correlation matrices or eigenvalue participation ratios. It only asks a new
question of already-computed facts: is this family adequate for CSCV/PBO, and does SPA have a
natural target anywhere in this pass of the campaign.

WHY NO PBO NUMBER IS COMPUTED HERE: see the DEFENSIBILITY ASSESSMENT section below and
`out/pbo_spa_results.json["pbo"]["reasons"]`. Short version: N_unique=6 behaviorally-distinct
configs is below the resolution CSCV's rank statistic needs to be informative, AND those 6 configs
are, by HASH01's own participation-ratio measurement, nearly collinear (PR=1.015-1.070 out of a
maximum of 7) -- i.e. the family was never a search over 6 meaningfully different strategies, it was
a density probe around one incumbent. Running CSCV on a near-collinear 6-arm family would not
measure overfitting risk; it would measure how a rank statistic behaves when applied to six
almost-identical noise realizations of the same series, and by construction that returns numbers
that look like "50% overfit" regardless of the true (here: near-zero, because there was barely a
real search) selection process. Per sec64's explicit instruction, that is a reason to withhold a
number, not compute one anyway.
"""
from __future__ import annotations

import itertools
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[4]
assert (REPO / "CLAUDE.md").exists(), f"repo root resolution failed: {REPO}"

OUT_DIR = Path(__file__).resolve().parents[1] / "out"
OUT_DIR.mkdir(parents=True, exist_ok=True)

HASH01_OUT = REPO / "research" / "registry" / "HASH01_BEHAVIORAL_POLICY_REGISTRY" / "out"
HASH01_JSON = HASH01_OUT / "policy_hash_results.json"

SIMPLE01_REPORT = REPO / "research" / "system_master" / "SIMPLE01_MINIMUM_SYSTEM" / "REPORT.md"
GRID01_REPORT = REPO / "research" / "system_master" / "GRID01_SOLAR_RESOLUTION_CONVERGENCE" / "REPORT.md"
GRID02_REPORT = REPO / "research" / "system_master" / "GRID02_ENDPOINT_PERTURBATION" / "REPORT.md"
PERT01_REPORT = REPO / "research" / "system_master" / "PERT01_STRUCTURAL_INVARIANCE" / "REPORT.md"

S_TARGET = 16  # CSCV standard default (Bailey/Borwein/Lopez de Prado/Zhu 2014): C(16,8)=12,870 combos


# =====================================================================================
# Part 1 -- PBO / CSCV defensibility assessment on the VolMult-grid family
# =====================================================================================

def load_hash01():
    assert HASH01_JSON.exists(), f"HASH01 output not found -- expected at {HASH01_JSON}"
    with open(HASH01_JSON) as f:
        return json.load(f)


def unique_behavioral_configs(hash01: dict) -> list[str]:
    """N_raw=7 configs, one exact raw-tuple duplicate (GRID02 endpoint_6_30 == GRID01 G13).
    Collapse to the 6 behaviorally-distinct names HASH01 itself identified (Level 2/3/4 all
    agree on the same single duplicate pair -- see HASH01 REPORT.md Sec 2.3)."""
    names = [r["name"] for r in hash01["records"]]
    dupe_groups = hash01["duplicate_groups_by_level"]["level4_pnl_productA_full"]
    drop = set()
    for _, members in dupe_groups.items():
        # keep the first member of each duplicate group, drop the rest
        for m in members[1:]:
            drop.add(m)
    return [n for n in names if n not in drop]


def correlation_summary(hash01: dict, unique_names: list[str]) -> dict:
    """Off-diagonal pairwise-correlation summary restricted to the 6 BEHAVIORALLY-DISTINCT
    configs (i.e. dropping one member of the exact-duplicate pair, which would otherwise
    contribute a trivial r=1.0 and bias the summary toward "more collinear than it is
    already"). Uses HASH01's own stored full-history daily-P&L correlation matrices verbatim
    -- no P&L is re-loaded or recomputed here."""
    out = {}
    for prod, key in [("ProductA", "correlation_matrix_productA"), ("ProductB", "correlation_matrix_productB")]:
        corr_dict = hash01[key]
        C = pd.DataFrame(corr_dict).loc[unique_names, unique_names]
        iu = np.triu_indices(len(unique_names), k=1)
        offdiag = C.to_numpy()[iu]
        out[prod] = {
            "n_unique": len(unique_names),
            "n_pairs": len(offdiag),
            "min": float(offdiag.min()),
            "median": float(np.median(offdiag)),
            "max": float(offdiag.max()),
            "mean": float(offdiag.mean()),
            "n_pairs_r_ge_0.99": int((offdiag >= 0.99).sum()),
            "n_pairs_r_ge_0.95": int((offdiag >= 0.95).sum()),
        }
    return out


def subperiod_feasibility(s_target: int = S_TARGET) -> dict:
    """CSCV/PBO's OTHER precondition (sec63-64): is there enough daily P&L history to cut S=16
    sub-periods with a workable number of observations each? Uses session-count facts already
    on record in HASH01's own JSON (canonical_window / full_history_window) plus the session
    counts already published in GRID01's own out/grid01_full_detail.json performance rows
    (n_days per window) -- read, not recomputed. This check is reported for completeness even
    though Part 1's headline finding is that the BLOCKING constraint here is candidate-family
    size/diversity, not sub-period length -- disclosed explicitly below."""
    grid01_detail = REPO / "research" / "system_master" / "GRID01_SOLAR_RESOLUTION_CONVERGENCE" / "out" / "grid01_full_detail.json"
    with open(grid01_detail) as f:
        gd = json.load(f)
    n_days_by_window = {}
    for row in gd["performance"]:
        n_days_by_window.setdefault(row["window"], row["n_days"])

    out = {}
    for window, n_days in n_days_by_window.items():
        out[window] = {
            "n_days": n_days,
            "s_target": s_target,
            "days_per_subperiod_approx": round(n_days / s_target, 1),
            "n_combinations_C(S,S/2)": math.comb(s_target, s_target // 2),
            "length_adequate_for_S=16": bool(n_days / s_target >= 15),  # >=15 obs/sub-period is a
            # generous floor for a daily-Sharpe-type statistic per sub-period; both windows clear
            # it comfortably (539/16=33.7, 1184/16=74) -- length is NOT the binding constraint here.
        }
    return out


def pbo_defensibility_assessment(hash01: dict, unique_names: list[str], corr_summary: dict,
                                   subperiod: dict) -> dict:
    n_raw = hash01["n_raw_in_family_processed"]
    n_unique = len(unique_names)
    pr_a = hash01["participation_ratio_productA"]["participation_ratio"]
    pr_b = hash01["participation_ratio_productB"]["participation_ratio"]
    pr_max = hash01["participation_ratio_productA"]["n_series"]  # 7

    reasons = []

    # Reason 1 -- candidate count / rank resolution.
    reasons.append({
        "criterion": "candidate count / CSCV rank resolution",
        "finding": (
            f"N_raw={n_raw}, N_unique_behaviorally_distinct={n_unique} (HASH01 Level 2/3/4 all "
            f"agree on exactly one exact-duplicate pair: GRID02 endpoint_6_30 == GRID01 G13, same "
            f"raw vms tuple). CSCV's rank statistic (logit of relative out-of-sample rank of the "
            f"in-sample-best candidate among N) has at most N possible support values per split. "
            f"With N=6, the logit distribution used to estimate PBO is quantized into only 6 "
            f"possible values -- far coarser than the resolution needed to distinguish 'the "
            f"in-sample winner ranks below median out-of-sample more than half the time' from "
            f"noise. Published CSCV applications (Bailey/Borwein/Lopez de Prado/Zhu 2014 and "
            f"common practitioner use, e.g. Lopez de Prado's own worked examples) apply the method "
            f"to candidate pools ranging from dozens to thousands of configurations; N=6 is well "
            f"below the range the method was designed and validated for."
        ),
        "severity": "blocking",
    })

    # Reason 2 -- near-total collinearity (participation ratio + raw correlation).
    reasons.append({
        "criterion": "cross-sectional diversity (participation ratio + pairwise correlation)",
        "finding": (
            f"HASH01's own eigenvalue participation ratio over the full 7x7 daily-P&L correlation "
            f"matrix: PR_ProductA={pr_a:.4f}, PR_ProductB={pr_b:.4f}, out of a maximum possible "
            f"{pr_max} (all series orthogonal) and a minimum of 1 (all series identical). Restricted "
            f"to the 6 behaviorally-distinct configs only (dropping the trivial exact duplicate), "
            f"pairwise full-history P&L correlation is "
            f"ProductA median={corr_summary['ProductA']['median']:.4f} "
            f"(range [{corr_summary['ProductA']['min']:.4f}, {corr_summary['ProductA']['max']:.4f}]), "
            f"ProductB median={corr_summary['ProductB']['median']:.4f} "
            f"(range [{corr_summary['ProductB']['min']:.4f}, {corr_summary['ProductB']['max']:.4f}]); "
            f"{corr_summary['ProductA']['n_pairs_r_ge_0.99']}/{corr_summary['ProductA']['n_pairs']} "
            f"ProductA pairs and "
            f"{corr_summary['ProductB']['n_pairs_r_ge_0.99']}/{corr_summary['ProductB']['n_pairs']} "
            f"ProductB pairs already clear HASH01's own pre-disclosed r>=0.99 'near-identity' bar. "
            f"A family whose 6 members behave as ~1 effective independent dimension was never a "
            f"search over 6 meaningfully different strategies -- it was a density/robustness probe "
            f"around one incumbent (GRID01/GRID02's own stated, preregistered purpose; REPORT.md: "
            f"'diagnostic-only ... select no winner, promote nothing'). Running CSCV on near-"
            f"collinear arms does not measure overfitting risk from a real selection process; it "
            f"measures how a rank statistic behaves on ~1 series against itself under repeated "
            f"noise draws, which is mechanically pulled toward an uninformative answer regardless "
            f"of the true (here: essentially absent) selection process."
        ),
        "severity": "blocking",
    })

    # Reason 3 -- the family was never a genuine selection process.
    reasons.append({
        "criterion": "was a real backtest-selection process ever run on this family",
        "finding": (
            "GRID01_SOLAR_RESOLUTION_CONVERGENCE/REPORT.md and GRID02_ENDPOINT_PERTURBATION/"
            "REPORT.md both preregister and both restate at their conclusion: 'No winner is "
            "selected. No candidate is promoted or frozen.' GRID02's report explicitly notes two "
            "of its three configs numerically 'outperforming' the incumbent on one product each, "
            "and explicitly declines to treat that as a selection signal ('without treating either "
            "neighbor's outperformance as a signal to re-optimize endpoints, which is out of scope "
            "for this diagnostic task'). CSCV/PBO answers 'if the researcher HAD picked the best "
            "in-sample performer from this pool, how likely is that pick to disappoint "
            "out-of-sample' -- a coherent hypothetical even absent an actual pick. This reason is "
            "therefore SUPPORTING context, not independently blocking, but it reinforces that this "
            "family's own designers assessed it as too narrow/coarse a comparison to support a "
            "selection decision at all (GRID02 REPORT.md: 'a three-point comparison is far too "
            "coarse to support such a decision even if it were in scope')."
        ),
        "severity": "supporting",
    })

    # Reason 4 -- partition-length: explicitly NOT the blocking constraint (disclosed to avoid
    # over-claiming; sec64 asks for an honest assessment, not just a list of everything wrong).
    reasons.append({
        "criterion": "sub-period partition length (S=16)",
        "finding": (
            "NOT a blocking constraint, disclosed for completeness: both available windows "
            f"comfortably support S={S_TARGET} sub-periods with a defensible number of "
            "observations each -- "
            + "; ".join(
                f"{w}: n_days={d['n_days']}, ~{d['days_per_subperiod_approx']} obs/sub-period"
                for w, d in subperiod.items()
            )
            + f". C({S_TARGET},{S_TARGET//2})={math.comb(S_TARGET, S_TARGET//2):,} combinations is "
            "computationally trivial either way. The blocking constraints are Reasons 1-2 (candidate "
            "count and diversity), not data length -- stated explicitly so this assessment is not "
            "read as 'insufficient data' when the real issue is 'insufficient/insufficiently-varied "
            "candidates.'"
        ),
        "severity": "not_blocking",
    })

    verdict = "NOT_DEFENSIBLE"
    return {
        "verdict": verdict,
        "n_raw": n_raw,
        "n_unique_behaviorally_distinct": n_unique,
        "participation_ratio_productA": pr_a,
        "participation_ratio_productB": pr_b,
        "participation_ratio_max_possible": pr_max,
        "reasons": reasons,
        "conclusion": (
            "PBO is judged NOT DEFENSIBLE on the VolMult-grid family. Per campaign directive sec64's "
            "own explicit instruction ('if the assumptions are poor, report that limitation "
            "explicitly rather than outputting a falsely precise PBO number just because code can "
            "calculate one'), no CSCV is run and no PBO percentage is reported anywhere in this "
            "output. Two independent, individually-sufficient reasons block it: (1) N=6 "
            "behaviorally-distinct candidates gives CSCV's rank statistic only 6 possible support "
            "values -- too coarse for the method's own designed resolution; (2) those 6 candidates "
            "are, by the campaign's own already-computed participation ratio, nearly collinear "
            "(PR=1.015-1.070 out of a max of 7) -- the family was a density probe around one "
            "incumbent, not a search over meaningfully different strategies, so a CSCV estimate on "
            "it would not measure a real selection-induced overfitting risk. Sub-period length (S=16) "
            "is explicitly NOT the constraint -- both candidate windows have ample daily "
            "observations for S=16. This is a candidate-diversity problem, not a data-length "
            "problem, and is reported as such rather than blurred into one generic 'not enough "
            "data' excuse."
        ),
    }


# =====================================================================================
# Part 2 -- Hansen SPA: does it have a natural target in this pass of the campaign
# =====================================================================================

def spa_applicability_assessment() -> dict:
    """SPA (Hansen 2005, and its ancestor White's Reality Check) tests whether an ALTERNATIVE
    that appears superior to a REFERENCE/benchmark survives once the search over many candidates
    that produced it is accounted for. It requires, as an input, at least one candidate the
    researcher is treating as an apparent winner over a stated benchmark. This function reviews
    GRID01, GRID02, PERT01 and SIMPLE01's own final adjudications (all read directly from their
    REPORT.md files, quoted, not paraphrased-and-guessed) for any such candidate."""

    evidence = [
        {
            "source": "research/system_master/SIMPLE01_MINIMUM_SYSTEM/REPORT.md",
            "line_ref": "line 12 (headline) and Sec 8.3 (final, post-completion-pass verdict table)",
            "quote": "zero rungs pass, for either product.",
            "reading": (
                "SIMPLE01 tested whether SIMPLER rungs (fewer modules) were NON-INFERIOR to the "
                "existing FULL incumbents -- a non-inferiority framing, not a superiority claim. "
                "Zero of 5 rungs (A0, A1, A2, B0, B1) passed the full preregistered margin set, even "
                "after a completion pass added the previously-missing trade-level retention leg "
                "(Sec 8.3: 'Zero rungs pass overall... with every gap closed'). No rung was ever "
                "adjudicated as an apparently superior alternative to its incumbent; several rungs "
                "cleared INDIVIDUAL margins (e.g. A1's Sharpe non-inferiority, B1's day-leg "
                "retention) but the adjudicator explicitly rejects reading any partial-margin PASS as "
                "a promotion signal (Sec 8.4: 'passing this (or any) non-inferiority ladder does not "
                "auto-promote anything')."
            ),
        },
        {
            "source": "research/system_master/GRID01_SOLAR_RESOLUTION_CONVERGENCE/REPORT.md",
            "line_ref": "lines 3-5, 105-108",
            "quote": "Diagnostic-only sweep ... No winner is selected. No candidate is promoted or frozen. ... G49's underperformance is reported as a diagnostic observation about value-sensitivity, not as a [selection signal]",
            "reading": (
                "A resolution-density sweep (G7/G13/G25/G49) around the incumbent, explicitly "
                "preregistered and concluded as diagnostic-only. No config is ever framed as an "
                "apparently superior alternative to the G13 incumbent."
            ),
        },
        {
            "source": "research/system_master/GRID02_ENDPOINT_PERTURBATION/REPORT.md",
            "line_ref": "lines 75-90",
            "quote": "Both disclosed neighbors of [6,30] ([5,29] and [7,31]) match or beat the center on both products in both windows ... without treating either neighbor's outperformance as a signal to re-optimize endpoints, which is out of scope for this diagnostic task. ... No winner is selected. No candidate is promoted or frozen.",
            "reading": (
                "This is the one place in the reviewed set where a numeric 'outperformance' is even "
                "written down -- and the report itself explicitly refuses to treat it as a "
                "superiority claim, calling a three-point comparison 'far too coarse to support such "
                "a decision even if it were in scope.' There is no adjudicated apparently-superior "
                "candidate here to feed an SPA test."
            ),
        },
        {
            "source": "research/system_master/PERT01_STRUCTURAL_INVARIANCE/REPORT.md",
            "line_ref": "lines 3-5, 118-119",
            "quote": "Diagnostic-only one-at-a-time (OAT) perturbation study ... No winner is selected. No candidate is promoted or frozen. No parameter value in this study -- incumbent or perturbed -- is being recommended for adoption.",
            "reading": (
                "Same pattern: three structural axes perturbed one-at-a-time, explicitly diagnostic, "
                "explicitly no candidate ever adjudicated superior."
            ),
        },
    ]

    has_target = any(
        False for _ in evidence  # no evidence row asserts an adjudicated-superior candidate
    )

    return {
        "has_natural_target": has_target,
        "evidence": evidence,
        "conclusion": (
            "SPA has NO natural application in this pass of the campaign. Hansen's SPA test (and "
            "White's Reality Check before it) answers a specific question: 'this ONE alternative "
            "appears to beat this ONE benchmark -- does that survive once I account for having "
            "searched over many alternatives to find it?' That question presupposes an adjudicated "
            "apparently-superior alternative. Reviewing the four candidate-generating exercises in "
            "this wave (GRID01, GRID02, PERT01, SIMPLE01) against their own final adjudications: "
            "SIMPLE01's own headline is 'zero rungs pass, for either product' (a non-inferiority "
            "test, and even on that weaker bar nothing cleared it); GRID01/GRID02/PERT01 are each "
            "self-adjudicated as diagnostic-only with an explicit, restated 'no winner is selected, "
            "no candidate is promoted' conclusion, including the one case (GRID02) where a raw "
            "number nominally 'outperforms' the incumbent -- a case the report's own authors "
            "declined to read as a superiority claim. Per campaign directive sec65's own explicit "
            "instruction, this task does not manufacture an artificial 'apparently superior "
            "candidate' in order to have something to run SPA against and get a p-value. No SPA is "
            "computed. If a future task DOES produce a genuinely adjudicated apparently-superior "
            "candidate against a stated benchmark, SPA would be the right tool to reach for then, "
            "not retrofitted onto this wave's diagnostic-only results."
        ),
    }


# =====================================================================================
# main
# =====================================================================================

def main():
    hash01 = load_hash01()
    unique_names = unique_behavioral_configs(hash01)
    corr_summary = correlation_summary(hash01, unique_names)
    subperiod = subperiod_feasibility(S_TARGET)
    pbo = pbo_defensibility_assessment(hash01, unique_names, corr_summary, subperiod)
    spa = spa_applicability_assessment()

    payload = {
        "meta": {
            "task": "STAT01 -- PBO/CSCV defensibility assessment on the VolMult-grid family "
                     "(GRID01 G7/G13/G25/G49 + GRID02's 3 endpoints, 7 raw / 6 behaviorally-"
                     "distinct configs), and a Hansen SPA applicability assessment across "
                     "GRID01/GRID02/PERT01/SIMPLE01. Per campaign directive sec61-66/sec63-65: "
                     "no trial-count or assumption is cherry-picked; PBO is not force-computed if "
                     "the family/partition is inadequate; SPA is not manufactured against an "
                     "artificial 'superior' candidate.",
            "reuse_sources": {
                "hash01_dedup_and_participation_ratio": str(HASH01_JSON.relative_to(REPO)).replace("\\", "/"),
                "grid01_session_counts_for_subperiod_feasibility": "research/system_master/GRID01_SOLAR_RESOLUTION_CONVERGENCE/out/grid01_full_detail.json (performance[].n_days, read only, not recomputed)",
            },
            "no_pnl_recomputed": True,
            "no_dedup_recomputed": True,
            "no_participation_ratio_recomputed": True,
            "cscv_run": False,
            "spa_run": False,
        },
        "pbo": {
            "family": "VolMult-grid (GRID01 G7/G13/G25/G49 + GRID02 endpoint_5_29/6_30/7_31)",
            "family_source_experiments": hash01["family_source_experiments"],
            "unique_behaviorally_distinct_config_names": unique_names,
            "correlation_summary_excl_trivial_duplicate": corr_summary,
            "subperiod_feasibility_S16": subperiod,
            "computed": False,
            "value": None,
            "value_note": "No PBO percentage is reported anywhere in this file -- see pbo.assessment.conclusion / pbo.assessment.reasons for why.",
            "assessment": pbo,
        },
        "spa": spa,
        "governance_restatement_sec66": (
            "This task does not claim to restore lost preregistration, and does not claim that "
            "withholding a PBO number 'solves' the campaign's selection-bias exposure. It reports "
            "one honest methodological finding (this family is unsuitable for CSCV) and one honest "
            "scoping finding (SPA has no candidate to test against in this pass) -- nothing more."
        ),
    }

    json_path = OUT_DIR / "pbo_spa_results.json"
    with open(json_path, "w") as f:
        json.dump(payload, f, indent=2, default=str)

    # ---- flat CSV summary (long format: one row per disclosed fact/finding) ----
    rows = []
    rows.append({"section": "pbo", "item": "family", "value": payload["pbo"]["family"], "note": ""})
    rows.append({"section": "pbo", "item": "n_raw", "value": pbo["n_raw"], "note": ""})
    rows.append({"section": "pbo", "item": "n_unique_behaviorally_distinct", "value": pbo["n_unique_behaviorally_distinct"], "note": "HASH01 Level 2/3/4 dedup, reused verbatim"})
    rows.append({"section": "pbo", "item": "participation_ratio_productA", "value": round(pbo["participation_ratio_productA"], 4), "note": f"out of max {pbo['participation_ratio_max_possible']}, HASH01 reused verbatim"})
    rows.append({"section": "pbo", "item": "participation_ratio_productB", "value": round(pbo["participation_ratio_productB"], 4), "note": f"out of max {pbo['participation_ratio_max_possible']}, HASH01 reused verbatim"})
    for prod, s in corr_summary.items():
        rows.append({"section": "pbo", "item": f"pairwise_corr_median_{prod}_excl_duplicate", "value": round(s["median"], 4), "note": f"n_pairs={s['n_pairs']}, range=[{s['min']:.4f},{s['max']:.4f}]"})
    for window, d in subperiod.items():
        rows.append({"section": "pbo", "item": f"subperiod_feasibility_{window}", "value": d["days_per_subperiod_approx"], "note": f"n_days={d['n_days']}, S={S_TARGET}, adequate_length={d['length_adequate_for_S=16']}"})
    for r in pbo["reasons"]:
        rows.append({"section": "pbo_reason", "item": r["criterion"], "value": r["severity"], "note": r["finding"][:300]})
    rows.append({"section": "pbo", "item": "VERDICT", "value": pbo["verdict"], "note": "pbo.computed=False, pbo.value=None -- no CSCV run, see JSON for full reasoning"})

    rows.append({"section": "spa", "item": "has_natural_target", "value": spa["has_natural_target"], "note": ""})
    for e in spa["evidence"]:
        rows.append({"section": "spa_evidence", "item": e["source"], "value": e["line_ref"], "note": e["quote"][:300]})
    rows.append({"section": "spa", "item": "VERDICT", "value": "NO_NATURAL_TARGET" if not spa["has_natural_target"] else "HAS_TARGET", "note": "spa_run=False -- no SPA computed, see JSON for full reasoning"})

    df = pd.DataFrame(rows)
    csv_path = OUT_DIR / "pbo_spa_results.csv"
    df.to_csv(csv_path, index=False)

    # ---- console summary ----
    print("=" * 100)
    print("STAT01 02_pbo_spa.py -- PBO/CSCV defensibility + SPA applicability assessment")
    print("=" * 100)
    print(f"\nPBO family: VolMult-grid, N_raw={pbo['n_raw']}, N_unique_behavioral="
          f"{pbo['n_unique_behaviorally_distinct']}, PR_A={pbo['participation_ratio_productA']:.4f}, "
          f"PR_B={pbo['participation_ratio_productB']:.4f} (max={pbo['participation_ratio_max_possible']})")
    print(f"PBO verdict: {pbo['verdict']}  (no CSCV run, no PBO number reported)")
    for r in pbo["reasons"]:
        print(f"  [{r['severity']:>12}] {r['criterion']}")
    print(f"\nSPA verdict: {'NO_NATURAL_TARGET' if not spa['has_natural_target'] else 'HAS_TARGET'}")
    for e in spa["evidence"]:
        print(f"  {e['source']}: \"{e['quote'][:90]}...\"")
    print("\nWrote:")
    print(f"  {json_path}")
    print(f"  {csv_path}")


if __name__ == "__main__":
    main()
