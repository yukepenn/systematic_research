"""EVIDENCE01 STEP 1 -- fixed, disclosed, non-cherry-picked selection of 2 additional prior runs
to audit, per Master Directive v4 sec29.

Method (stated plainly, fully mechanical, no per-row judgment calls):
  1. Read research/system_master/TESTING_LEDGER.csv (40 data rows).
  2. Remove the 2 mandatory rows: U6B_PRODUCT_A_SCALE_RATE, AUCTION01_VALUE_STATE.
  3. Remove every row whose hypothesis_class column literal value == "infrastructure".
     This is the exact, mechanical form of the directive's "except pure infrastructure/
     audit-only rows" instruction: the 3 named examples (WAVE4_TRUTH_AUDIT, DATA02, i.e.
     DATA02_MICROSTRUCTURE_INVENTORY, WAVE4_FRONTIER_O2_GAMMA_AUDIT) are EXACTLY the rows
     that carry hypothesis_class=="infrastructure" together with 3 more
     (U0_UNIFIED_STATE, WAVE1_SYNTHESIS, WAVE2_EVI) -- confirmed independently: none of
     these 6 rows has a runs/<family>/ directory on disk except U0_UNIFIED_STATE, and even
     that row's own key_finding is a state-table-construction confirmation, not a
     standalone tested hypothesis with a headline number of its own. Using the CSV's own
     hypothesis_class column (rather than manually curating a longer stop-list) keeps the
     exclusion rule mechanical/auditable rather than a per-row judgment call.
  4. Sort the remaining family names alphabetically (Python default string sort).
  5. random.seed(20260809); random.sample(sorted_list, 2).

Reproduce: python runs/EVIDENCE01_REPORT_TRACEABILITY/src/01_select_families.py
"""
import csv
import json
import random

LEDGER = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\research\system_master\TESTING_LEDGER.csv"
OUT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research\runs\EVIDENCE01_REPORT_TRACEABILITY\out\step1_selection.json"

MANDATORY_EXCLUDE = {"U6B_PRODUCT_A_SCALE_RATE", "AUCTION01_VALUE_STATE"}

rows = []
with open(LEDGER, newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        rows.append(row)

assert len(rows) == 40, f"expected 40 ledger rows, got {len(rows)}"

infra_exclude = sorted({r["family"] for r in rows if r["hypothesis_class"] == "infrastructure"})
print("Rows with hypothesis_class == 'infrastructure' (excluded as pure infrastructure/audit-only):")
for f in infra_exclude:
    print("  -", f)

candidates = [
    r["family"] for r in rows
    if r["family"] not in MANDATORY_EXCLUDE and r["family"] not in infra_exclude
]
sorted_list = sorted(candidates)
print(f"\nCandidate pool after exclusions: {len(sorted_list)} families")
for i, fam in enumerate(sorted_list):
    print(f"  [{i}] {fam}")

random.seed(20260809)
picks = random.sample(sorted_list, 2)
print("\nPICKS:", picks)

out = {
    "ledger_path": LEDGER,
    "n_ledger_rows": len(rows),
    "mandatory_excluded": sorted(MANDATORY_EXCLUDE),
    "infrastructure_excluded": infra_exclude,
    "n_candidates": len(sorted_list),
    "sorted_candidate_list": sorted_list,
    "seed": 20260809,
    "method": "random.seed(20260809); random.sample(sorted_list, 2)",
    "picks": picks,
}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2)
print(f"\nWrote {OUT}")
