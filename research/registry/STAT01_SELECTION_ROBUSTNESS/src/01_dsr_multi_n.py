"""01_dsr_multi_n.py -- STAT01: DSR / R6 Harvey-Liu haircut recomputed under every
defensible campaign trial-count assumption.

Per campaign directive sec61-66: this script does NOT select the trial-count assumption
that gives the best DSR. It reports all defensible assumptions side by side, changing
NOTHING else about the calculation as N varies. It does not claim to restore lost
preregistration (sec66) -- it is a sensitivity disclosure on top of an already-disclosed
governance gap (REGISTRY_GAP_NOTE.md, HASH01 REPORT.md).

REUSE, NOT REIMPLEMENTATION: every DSR/PSR/Harvey-Liu number below is produced by calling
`src/analytics/trials.py` and `src/analytics/validation.py` verbatim (import, not copy-paste).
Those modules implement research/registry/TRIAL_ACCOUNTING_RULE.md exactly and are the
ONLY DSR/R6 implementation found in this repository (grepped for Harvey|haircut|deflated|DSR
across the full tree; the only executable code, as opposed to prose report tables, is
src/analytics/trials.py + src/analytics/validation.py).

Candidates: Product A_FULL (`SolarWaveSMMaster_v4.cs`) and Product B_FULL
(`SolarWaveOneContractNQ_v5.cs`), the campaign's two live incumbents -- per task framing,
the relevant "candidate" for a selection-bias question here, since Wave 3 / SIMPLE01
produced no new promotable candidate (SIMPLE01 REPORT.md: "zero rungs pass, for either
product"). Daily P&L: research/system_master/SIMPLE01_MINIMUM_SYSTEM/out/
daily_pnl_{A,B}_FULL_base_cost_full_history_through_20260731.csv, full available history
2022-01-03 -> 2026-07-31 (n=1184 sessions; superset of SIMPLE01's own 2022-01-01->2026-05-31
dev-window gating basis). Full history is used here (more data, not less) because this task
is not re-litigating SIMPLE01's gate, only asking how DSR moves with N.

Two statistics are reported per (candidate, N), exactly as TRIAL_ACCOUNTING_RULE.md's own R5/R6
pairing prescribes ("R6 ... always reported alongside" the DSR proper):

  (1) R6 Harvey-Liu Bonferroni / BHY haircut  -- trials.harvey_liu_haircut(series, n_raw=N)
      Needs only N and the candidate's own daily series (no cross-sectional variance pool).
      This is the exact function the campaign used to produce "haircut Sharpe = 0.000" in
      REGISTRY_GAP_NOTE.md / CAMPAIGN_STATE.md / WAVE3_report.md at N_raw=316 and at the
      229-383 bracket. Reused verbatim here, only N is swept.

  (2) Bailey-Lopez de Prado Deflated Sharpe Ratio proper -- trials.deflated_sharpe(series,
      v_ann, n_eff=N). This needs a second input, V (the cross-sectional variance of trial
      Sharpes), which is NOT a function of N alone -- it was computed once, campaign-wide,
      under the preregistered R2-R4 clustering pipeline in WAVE3_report.md Sec 4: N_eff=5,
      V=0.645 (std 0.803), on the pool of 213 trials inspected at that point. No comparable
      V exists for any of the other N assumptions in this sweep (no full daily-P&L pool for
      N=499-653 has been assembled -- see HASH01 REPORT.md, which explicitly found no
      full-registry pool). Per "changing NOTHING else about the calculation each time", V is
      HELD FIXED at the campaign's own last preregistered value (0.645) while N is swept --
      this isolates the effect of the trial-count dial exactly as TRIAL_ACCOUNTING_RULE.md's
      own motivating example did (moving DSR from 0.16 to 0.83 by changing only the dial).
      This is explicitly flagged AS a sensitivity, not a claim that N_eff genuinely equals
      90...653 for any candidate (participation-ratio N_eff is, by construction, always far
      below raw N; this row answers "if we mechanically substituted raw N counts for the
      benchmark's trial-count parameter, holding the campaign's own last V fixed, what would
      the number read" -- a diagnostic, not an endorsed alternative estimator).
      A secondary V-sensitivity grid (V in {0.027, 0.40, 0.50, 0.645}, the full disclosed
      range across TRIAL_ACCOUNTING_RULE.md + WAVE3_report.md) is also produced so no single V
      choice is silently privileged either.

N_eff via participation ratio (the third option in the task): the KNOWN FACTS establish there
is NO full-registry correlation matrix / behaviorally-unique-count available (HASH01 covered
only the 7-config VolMult-grid family, ~1.1-1.4% of the registry). No campaign-wide N_eff is
computed here. HASH01's own narrow-family PR (1.015-1.070) is carried through as CONTEXT ONLY,
explicitly labeled not representative of the full registry, and is not used to produce any
DSR number for A_FULL / B_FULL.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

REPO = Path(__file__).resolve().parents[4]
assert (REPO / "CLAUDE.md").exists(), f"repo root resolution failed: {REPO}"

sys.path.insert(0, str(REPO / "src" / "analytics"))
import trials as R6MOD          # noqa: E402  -- the actual, reused R6/DSR implementation
import validation as VALMOD     # noqa: E402  -- psr(), sharpe() reused by trials.py

OUT_DIR = Path(__file__).resolve().parents[1] / "out"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SIMPLE01_OUT = REPO / "research" / "system_master" / "SIMPLE01_MINIMUM_SYSTEM" / "out"
HASH01_OUT = REPO / "research" / "registry" / "HASH01_BEHAVIORAL_POLICY_REGISTRY" / "out"

ANN = 252  # research/system_master/CONVENTIONS.md line 39: "ann = 252, std ddof=1"

# ---------------------------------------------------------------------------------------
# Trial-count assumptions under test (task sec spec, all defensible, none preferred)
# ---------------------------------------------------------------------------------------
N_ASSUMPTIONS = [
    {"N": 90, "label": "contemporaneously registered (lower bound)",
     "source": "REGISTRY_GAP_NOTE.md: tested_configs.csv seq 1-90, Wave 1+1b, before the "
               "registry-convention lapse. The only N with an unbroken, contemporaneous, "
               "committed-before-results paper trail for every row."},
    {"N": 229, "label": "gap note R1 basis (contemporaneous + reconstructed-distinct-param)",
     "source": "REGISTRY_GAP_NOTE.md 'campaign total, R1 basis' = 90 (Wave1/1b) + 139 "
               "(Waves 1c-3 backfill, distinct parameter sets, reconstructed=yes). This is "
               "also the same basis WAVE3_report.md's own N_raw=255/316 figures were drawn "
               "from at earlier snapshots of the same growing ledger."},
    {"N": 383, "label": "gap note upper bound (every ledger row incl. slip re-runs)",
     "source": "REGISTRY_GAP_NOTE.md upper bound: 90 + 293 (every backfilled ledger row "
               "minus parity gates, i.e. counting cost-stress re-runs of the same config as "
               "separate trials)."},
    {"N": 499, "label": "HASH01 updated lower bound (as of 2026-08-10)",
     "source": "HASH01 REPORT.md Sec 1.3: 90 (Wave1/1b) + 139 (backfill distinct-param) + "
               "270 (post-gap-note tested_configs.csv seq 230-498, distinct seq/letter-id "
               "slots) = 499. Supersedes the 2026-08-07 229-383 bracket because 270 "
               "additional trial-slots were logged in the interim."},
    {"N": 653, "label": "HASH01 updated upper bound (as of 2026-08-10)",
     "source": "HASH01 REPORT.md Sec 1.3: 90 + 293 (backfill upper bound, every ledger row) "
               "+ 270 (post-gap-note) = 653."},
]

# V (cross-sectional SR variance) options for the Bailey-DSR sensitivity grid.
V_OPTIONS = [
    {"V": 0.645, "label": "campaign's last preregistered value (WAVE3_report.md Sec 4, "
                          "N_eff=5, 213 trials pool) -- PRIMARY / held fixed for the main N sweep"},
    {"V": 0.027, "label": "WAVE3 'mechanically-broken arms removed' sensitivity -- explicitly "
                          "reported by WAVE3_report.md as NOT used for promotion"},
    {"V": 0.40, "label": "TRIAL_ACCOUNTING_RULE.md 'honest pool' lower bound"},
    {"V": 0.50, "label": "TRIAL_ACCOUNTING_RULE.md 'honest pool' upper bound"},
]

CANDIDATES = {
    "A_FULL": {
        "file": SIMPLE01_OUT / "daily_pnl_A_FULL_base_cost_full_history_through_20260731.csv",
        "real_name": "SolarWaveSMMaster_v4.cs (Product A incumbent)",
    },
    "B_FULL": {
        "file": SIMPLE01_OUT / "daily_pnl_B_FULL_base_cost_full_history_through_20260731.csv",
        "real_name": "SolarWaveOneContractNQ_v5.cs (Product B incumbent)",
    },
}


def load_series(path: Path) -> pd.Series:
    df = pd.read_csv(path, parse_dates=["session_date"]).sort_values("session_date")
    s = df.set_index("session_date")["pnl"].astype(float)
    assert s.notna().all(), f"NaNs in {path}"
    return s


def skew_kurt(x: np.ndarray) -> tuple[float, float]:
    """Same estimators trials.py/validation.py use internally (psr()), surfaced explicitly
    per task requirement to report skew/excess-kurtosis alongside every DSR figure."""
    g3 = float(stats.skew(x, bias=False))
    g4_excess = float(stats.kurtosis(x, fisher=True, bias=False))  # excess kurtosis (fisher=True)
    return g3, g4_excess


def main():
    candidate_series = {name: load_series(c["file"]) for name, c in CANDIDATES.items()}

    rows = []
    context = {}

    # ---- HASH01 narrow-family PR: context only, never turned into a DSR number ----
    hash01_report = REPO / "research" / "registry" / "HASH01_BEHAVIORAL_POLICY_REGISTRY" / "REPORT.md"
    context["N_eff_via_participation_ratio"] = {
        "status": "NOT COMPUTED campaign-wide -- no defensible campaign-wide daily-P&L pool exists",
        "reason": (
            "KNOWN FACT (this session, HASH01 REPORT.md): the only participation-ratio "
            "computation performed anywhere in the registry covers 7 raw configurations in "
            "the VolMult-grid family (GRID01 G7/G13/G25/G49 + GRID02 endpoint sweep), "
            "'under 1.4% of the lower-bound 499-trial-slot registry' (HASH01 REPORT.md Part 3 "
            "item 5). HASH01's own report explicitly warns: 'No \"N_unique\" figure in this report "
            "should ever be quoted as if it describes the full ~499-653-trial-slot registry.' "
            "This script does not override that warning. No full-registry correlation matrix "
            "was assembled for this task (would require re-pulling daily P&L for 499-653 "
            "trial-slots spanning multiple substrates, cost models, and instruments -- out of "
            "scope for a reuse-the-existing-implementation task)."
        ),
        "hash01_narrow_family_PR_context_only": {
            "family": "VolMult-grid (GRID01 G7/G13/G25/G49 + GRID02 endpoint sweep), 7 raw configs",
            "PR_ProductA": 1.0151, "PR_ProductB": 1.0699, "PR_max_possible": 7,
            "explicitly_NOT_representative_of_full_registry": True,
            "explicitly_NOT_the_same_candidate_family_as_A_FULL_B_FULL": True,
            "source": str(hash01_report.relative_to(REPO)).replace("\\", "/"),
        },
        "conclusion": "Per task instruction: do NOT force a campaign-wide N_eff number. "
                      "No DSR row is produced under this assumption.",
    }

    for cand_name, series in candidate_series.items():
        x = series.to_numpy(dtype=float)
        n_days = len(x)
        skew_val, kurt_excess = skew_kurt(x)
        sharpe_val = VALMOD.sharpe(x, ANN)
        date_start, date_end = str(series.index.min().date()), str(series.index.max().date())

        for n_assump in N_ASSUMPTIONS:
            N = n_assump["N"]

            # (1) R6 Harvey-Liu haircut, reused verbatim, only N varies
            hl = R6MOD.harvey_liu_haircut(x, n_raw=N, ann=ANN)

            # (2) Bailey DSR proper, reused verbatim, V held fixed at campaign's own last
            #     preregistered value (0.645); N substituted for n_eff as the swept dial.
            v_primary = V_OPTIONS[0]["V"]
            dsr_val, sr0_ann = R6MOD.deflated_sharpe(x, v_ann=v_primary, n_eff=N, ann=ANN)

            row = {
                "candidate": cand_name,
                "candidate_real_name": CANDIDATES[cand_name]["real_name"],
                "date_start": date_start, "date_end": date_end,
                "n_days": n_days,
                "sharpe_annualized": sharpe_val,
                "skew": skew_val,
                "excess_kurtosis": kurt_excess,
                "N_assumption": N,
                "N_assumption_label": n_assump["label"],
                "N_assumption_source": n_assump["source"],
                # R6 Harvey-Liu (function of N and the series only, no V needed)
                "R6_t_stat": hl["t"],
                "R6_p_two_sided": hl["p"],
                "R6_p_bonferroni": hl["p_bonferroni"],
                "R6_haircut_sharpe_bonferroni": hl["haircut_sharpe_bonferroni"],
                "R6_bhy_threshold": hl["bhy_threshold"],
                "R6_passes_bhy": hl["passes_bhy"],
                # Bailey DSR proper, V held fixed at 0.645 (primary), N swept as n_eff
                "DSR_V_fixed_at": v_primary,
                "DSR_benchmark_sr0_ann": sr0_ann,
                "DSR_bailey_psr_against_benchmark": dsr_val,
                "DSR_promotable_by_R7_ge_0.90": bool(dsr_val >= 0.90) if not math.isnan(dsr_val) else None,
            }
            rows.append(row)

    df = pd.DataFrame(rows)

    # ---- V-sensitivity grid (Bailey DSR at every disclosed V, every N) -- secondary output ----
    v_rows = []
    for cand_name, series in candidate_series.items():
        x = series.to_numpy(dtype=float)
        for n_assump in N_ASSUMPTIONS:
            N = n_assump["N"]
            for v_opt in V_OPTIONS:
                dsr_val, sr0_ann = R6MOD.deflated_sharpe(x, v_ann=v_opt["V"], n_eff=N, ann=ANN)
                v_rows.append({
                    "candidate": cand_name, "N_assumption": N, "N_assumption_label": n_assump["label"],
                    "V": v_opt["V"], "V_label": v_opt["label"],
                    "DSR_benchmark_sr0_ann": sr0_ann, "DSR_bailey_psr_against_benchmark": dsr_val,
                })
    v_df = pd.DataFrame(v_rows)

    # ---- write outputs ----
    csv_path = OUT_DIR / "dsr_results.csv"
    df.to_csv(csv_path, index=False)

    v_csv_path = OUT_DIR / "dsr_v_sensitivity.csv"
    v_df.to_csv(v_csv_path, index=False)

    payload = {
        "meta": {
            "task": "STAT01 -- DSR recomputed under every defensible campaign trial-count "
                     "assumption, reusing src/analytics/trials.py (R6 Harvey-Liu) and "
                     "src/analytics/validation.py (psr/sharpe) verbatim.",
            "r6_implementation_source": "src/analytics/trials.py (functions harvey_liu_haircut, "
                                          "deflated_sharpe, psr/sharpe from src/analytics/validation.py)",
            "ann_convention": ANN,
            "candidates": {k: v["real_name"] for k, v in CANDIDATES.items()},
            "note_governance": "Per campaign directive sec61-66: no trial-count assumption is "
                                "selected or highlighted as preferred. This is a sensitivity "
                                "disclosure, not a restoration of lost preregistration.",
        },
        "N_assumptions": N_ASSUMPTIONS,
        "V_options_for_bailey_dsr_sensitivity": V_OPTIONS,
        "context_N_eff_participation_ratio": context["N_eff_via_participation_ratio"],
        "results": rows,
        "v_sensitivity_grid": v_rows,
    }
    json_path = OUT_DIR / "dsr_results.json"
    with open(json_path, "w") as f:
        json.dump(payload, f, indent=2, default=str)

    # ---- console summary ----
    print("=" * 100)
    print("STAT01 -- DSR / R6 Harvey-Liu haircut across trial-count assumptions")
    print("=" * 100)
    for cand_name in CANDIDATES:
        sub = df[df.candidate == cand_name]
        print(f"\n{cand_name} ({CANDIDATES[cand_name]['real_name']})")
        print(f"  n_days={sub.n_days.iloc[0]}  window={sub.date_start.iloc[0]}..{sub.date_end.iloc[0]}"
              f"  Sharpe(ann)={sub.sharpe_annualized.iloc[0]:.4f}"
              f"  skew={sub['skew'].iloc[0]:.4f}  excess_kurt={sub.excess_kurtosis.iloc[0]:.4f}")
        for _, r in sub.iterrows():
            print(f"    N={r.N_assumption:>4} ({r.N_assumption_label[:45]:45s}) | "
                  f"R6 haircut_sharpe={r.R6_haircut_sharpe_bonferroni:8.4f} passes_bhy={str(r.R6_passes_bhy):5s} | "
                  f"Bailey DSR(V=0.645)={r.DSR_bailey_psr_against_benchmark:.4f}")
    print("\nWrote:")
    print(f"  {csv_path}")
    print(f"  {v_csv_path}")
    print(f"  {json_path}")


if __name__ == "__main__":
    main()
