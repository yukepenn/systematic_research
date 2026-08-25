# TERMINOLOGY_SWEEP — directive v4.0 sections 32 and 41

**Status of this document: PLAN ONLY. Nothing has been edited.**
Generated 2026-08-24. Scope searched:
`research/original_trader_reconstruction/**` and `runs/OTR_*/**`
(file types `.md`, `.yaml`, `.yml`, `.csv`, plus `.py` docstrings/comments).
Search was read-only; no file outside this one was touched.

## Risk flag legend

| Flag | Meaning |
|---|---|
| `SAFE_RENAME` | Mechanical substitution. No claim changes, only its label. Can be scripted. |
| `NEEDS_HUMAN_JUDGEMENT` | The sentence mixes observation with interpretation, or the correct new status depends on a decision nobody has made yet. Must be rewritten by hand and re-graded. |
| `DO_NOT_EDIT_HISTORICAL` | Inside `runs/OTR_*/`. Preregistration or raw result. Propose an addendum file, never an edit. |

**Run-directory policy applied here.** The task names `runs/*/spec.yaml` and
`runs/*/out/` as immutable. The campaign workflow rule ("Never overwrite a run
dir") is broader, so this sweep treats *every* file under `runs/OTR_*/` —
including `REPORT.md` — as `DO_NOT_EDIT_HISTORICAL`. The proposed remedy for
all of them is one new file per affected run:
`runs/<run_id>/TERMINOLOGY_ADDENDUM_v4.md`, which restates the claim in v4.0
vocabulary and points back at the original line. The original text stays
verbatim.

---

## Summary counts

| Category | Live-doc hits (editable) | Historical hits (`runs/OTR_*`) | Benign / no change | Total occurrences |
|---|---|---|---|---|
| C1 — "true OOS" / "fully OOS" family | 14 | 4 | 10 | 28 |
| C2 — "ground truth" applied to labels | 2 | 2 | 1 | 5 |
| C3 — bare parity claims (no endpoints named) | 15 | 5 | 4 | 24 |
| C4 — "solved" / "CONFIRMED" on VWAP anchor lifecycle + rails | 18 | 0 | 0 | 18 |
| C5 — "proves" / "proven" on EV-039 or author reimplementation | 16 | 6 | 5 | 27 |
| **TOTAL** | **65** | **17** | **20** | **102** |

By risk flag (actionable hits only, benign excluded): `SAFE_RENAME` 38,
`NEEDS_HUMAN_JUDGEMENT` 27, `DO_NOT_EDIT_HISTORICAL` 17.

**Zero hits** for these searched phrases: `"L5 perfect"`, `"perfect parity"`,
`"exact replica"`, `"genuine OOS"`. `"verified model class"` returned exactly
one hit (C3-05). `"bit-exact"` / `"bit exact"` returned 6.

---

## C1 — "true OOS" / "fully OOS" / "fully out-of-sample"

Rule: `true OOS` / `fully OOS` / `TRUE OOS` -> `HELD_OUT_RECONSTRUCTION_WINDOW`.
Reason (directive v4.0): every window in this campaign sits in history whose
outcomes we have already read. A window can be held out from *fitting*; it
cannot be out-of-sample with respect to *us*.

| # | File | Line | Exact current text | Proposed replacement | Flag |
|---|---|---|---|---|---|
| C1-01 | `research/original_trader_reconstruction/CURRENT_TRUTH.md` | 46 | `## 2026-08-24j — NT8/CrossTrade UNLOCKED: R6 parity BIT-EXACT; June-July data ingested; VF-CAND1 survives TRUE OOS` | `## 2026-08-24j — NT8/CrossTrade UNLOCKED: R6 IMPLEMENTATION_PARITY (Python <-> NinjaScript <-> NT8 engine) bit-identical; June-July data ingested; VF-CAND1 survives HELD_OUT_RECONSTRUCTION_WINDOW test` | `NEEDS_HUMAN_JUDGEMENT` (header carries a C1 and a C3 defect at once) |
| C1-02 | `.../CURRENT_TRUTH.md` | 59 | `- **R8-A TRUE OOS: OTR-VF-CAND1 cluster survives** (preregistered prediction` | `- **R8-A HELD_OUT_RECONSTRUCTION_WINDOW: OTR-VF-CAND1 cluster survives** (preregistered prediction` | `SAFE_RENAME` |
| C1-03 | `.../CURRENT_TRUTH.md` | 62 | `swing on a +8.6k week). −2,600 stop reproduces OOS. Residual unchanged in` | `swing on a +8.6k week). −2,600 stop reproduces on the HELD_OUT_RECONSTRUCTION_WINDOW. Residual unchanged in` | `SAFE_RENAME` |
| C1-04 | `.../CURRENT_TRUTH.md` | 111 | `## 2026-08-24h — R5 WEEKLY VALIDATION: CAND2 passes dev-machine OOS; residual is MACHINE-correlated (directive v3.0 PHASE C1)` | `## 2026-08-24h — R5 WEEKLY VALIDATION: CAND2 passes dev-machine HELD_OUT_RECONSTRUCTION_WINDOWs; residual is MACHINE-correlated (directive v3.0 PHASE C1)` | `SAFE_RENAME` |
| C1-05 | `.../CURRENT_TRUTH.md` | 117 | `within ~7 min, LL structure correct — 9 windows, fully OOS.**` | `within ~7 min, LL structure correct — 9 HELD_OUT_RECONSTRUCTION_WINDOWs (held out from CAND2 fitting; outcomes previously seen).**` | `SAFE_RENAME` |
| C1-06 | `.../CONVERGENCE_PASS_ANSWERS_20260824.md` | 6 | `Δ$40) — fully OOS PASS. hp-machine weeks (19) do NOT fit (+39.5% overtrade):` | `Δ$40) — HELD_OUT_RECONSTRUCTION_WINDOW PASS. hp-machine weeks (19) do NOT fit (+39.5% overtrade):` | `SAFE_RENAME` |
| C1-07 | `.../HYPOTHESIS_LEDGER.csv` | 151 | field 5 of row `OTR-R8-001`: `TRUE OOS (identified on 1/25-5/29)` | `HELD_OUT_RECONSTRUCTION_WINDOW (fit on 1/25-5/29; outcomes previously seen)` | `SAFE_RENAME` |
| C1-08 | `.../HYPOTHESIS_LEDGER.csv` | 151 | status field: `OOS_CLASS_PASS_LEADER_STABLE` | `HELDOUT_CLASS_PASS_LEADER_STABLE` | `SAFE_RENAME` |
| C1-09 | `.../HYPOTHESIS_LEDGER.csv` | 141 | status field: `DEV_OOS_PASS_HP_SPLIT`; notes contain `...holds LL structure OOS...` | `DEV_HELDOUT_PASS_HP_SPLIT`; `...holds LL structure on held-out weeks...` | `SAFE_RENAME` |
| C1-10 | `.../HYPOTHESIS_LEDGER.csv` | 137 | method field: `independent re-implementation + rival search + OOS`; notes `armed rule never fires OOS` | `independent re-implementation + rival search + HELD_OUT_RECONSTRUCTION_WINDOW`; `armed rule never fires on the held-out windows` | `SAFE_RENAME` |
| C1-11 | `.../vwap_flux_family/OWNER_REPORT_RECONCILIATION.md` | 39 | `in-sample + 3 true-OOS windows (§40 distance, failure-week DQ, LOWO) —` | `in-sample + 3 HELD_OUT_RECONSTRUCTION_WINDOWs (§40 distance, failure-week DQ, LOWO) —` | `SAFE_RENAME` |
| C1-12 | `.../solar_family/TRACK_S_REPORT.md` | 150 | `OOS PASS (±7% counts, holds ~7min, LL structure right, several near-exact` | `HELD_OUT_RECONSTRUCTION_WINDOW PASS (±7% counts, holds ~7min, LL structure right, several near-exact` | `SAFE_RENAME` |
| C1-13 | `.../vwap_flux_family/src/run_r8_june.py` | 2 | `windows (TRUE OOS) + part B June TP overlay bound. No knobs touched."""` | `windows (HELD_OUT_RECONSTRUCTION_WINDOW) + part B June TP overlay bound. No knobs touched."""` | `SAFE_RENAME` (docstring, no logic) |
| C1-14 | `.../vwap_flux_family/src/run_r8_june.py` | 66 | `    print("=== R8-A: frozen cluster, TRUE OOS ===")` | `    print("=== R8-A: frozen cluster, HELD_OUT_RECONSTRUCTION_WINDOW ===")` | `SAFE_RENAME` (print string only; changes stdout of a re-run, not results) |
| C1-15 | `.../screenshot_forensics/per_image/OTRIMG-0029.md` | 106 | `- This is honest-loss evidence: the trader kept/captured a losing day; useful for reconstructing true out-of-sample behavior.` | Split per the hard rule. FACT: `the trader captured and posted a losing day`. INFERENCE: `a posted losing day reduces the survivorship concern in the weekly-report corpus`. Delete `true out-of-sample` entirely — it is not our window, it is his behavior. | `NEEDS_HUMAN_JUDGEMENT` |
| C1-16 | `runs/OTR_R8_JUNE2026/spec.yaml` | 11 | `part_A_r7_extension (TRUE OOS for OTR-VF-CAND1):` | Preregistration. Do not edit. Addendum: "the key `part_A_r7_extension (TRUE OOS ...)` means HELD_OUT_RECONSTRUCTION_WINDOW under directive v4.0; the windows were held out from fitting, not unseen." | `DO_NOT_EDIT_HISTORICAL` |
| C1-17 | `runs/OTR_R8_JUNE2026/REPORT.md` | 1 | `# OTR_R8 — June-July 2026 unlock: VF-CAND1 true OOS + TP overlay (2026-08-24)` | Addendum only, same wording as C1-16. | `DO_NOT_EDIT_HISTORICAL` |
| C1-18 | `runs/OTR_R8_JUNE2026/REPORT.md` | 6 | `## Part A — OTR-VF-CAND1 vs 6/21-7/31 flagship windows (TRUE OOS)` | Addendum only. | `DO_NOT_EDIT_HISTORICAL` |
| C1-19 | `runs/OTR_R5_CAND2_WEEKLY_VALIDATION/WEEKLY_VALIDATION_REPORT.md` | 20 | `across BOTH parameter eras — 9 windows, all fully out-of-sample w.r.t. CAND2's` | Addendum only: "read as HELD_OUT_RECONSTRUCTION_WINDOW w.r.t. CAND2's identification data." | `DO_NOT_EDIT_HISTORICAL` |

### C1 benign occurrences — no change proposed

These use "OOS" in a plain, non-overclaiming way, or already carry the correct
caveat. Listed so a later sweep does not re-flag them.

| File | Line | Note |
|---|---|---|
| `.../README.md` | 20 | `already-consumed history may be used freely for reconstruction (NOT as "pristine OOS")` — already correct. |
| `.../DATA_AUDIT.md` | 9, 17 | `usable for reconstruction, NOT clean OOS` / `pristine OOS` — already correct. |
| `.../CURRENT_TRUTH.md` | 407 | `reconstruction (not claimable as pristine OOS)` — already correct. |
| `.../solar_family/TRACK_S_REPORT.md` | 140 | `armed-noon rule untested out-of-sample` — a limitation statement, not a claim. |
| `.../solar_transition_family/FEB2025_FAST_BUILD.md` | 4, 37 | `R1 OOS note` — a cross-reference to a section title. |
| `runs/OTR_R1_SERIES/spec.yaml` | 93 | `W0204/09 out-of-sample` — plain, and historical. |
| `runs/OTR_R1_SERIES/REPORT.md` | 47 | `## Out-of-sample note` — plain, and historical. |
| `runs/OTR_R1_SERIES/out/v_av_3_oos.py` | 1 | `OUT-OF-SAMPLE` in docstring — plain, and raw result. |

---

## C2 — "ground truth" applied to trade labels

Rule: `ground-truth trade labels` -> `CONDITIONAL_LATENT_LABELS`.
Reason (directive v4.0): R1e generated OUR candidate trades and solved for
which to REMOVE so the daily aggregates matched. The TAKE/SKIP assignments are
latent variables under a candidate-universe assumption. They were never
observed.

| # | File | Line | Exact current text | Proposed replacement | Flag |
|---|---|---|---|---|---|
| C2-01 | `.../solar_family/src/run_r1f_features.py` | 25 | `# ground-truth labels from unique cent-exact subset diffs (entry time -> label)` | `# CONDITIONAL_LATENT_LABELS from unique cent-exact subset diffs (entry time -> label);` <br> `# latent under the T1-flip candidate-universe assumption, not observed trades` | `SAFE_RENAME` (comment; no logic) |
| C2-02 | `.../vendor_forensics/LOCAL_ARTIFACT_SEARCH_20260824.md` | 101 | `...which supports naming/structure inferences about VWAP Flux but provides no numerical ground truth.` | `...but provides no numerical oracle.` (This hit is about a *vendor output oracle*, not trade labels. The retired phrase should still go, because reusing "ground truth" anywhere in this campaign re-legitimises it.) | `SAFE_RENAME` |
| C2-03 | `runs/OTR_R6_NT8_PARITY/REPORT.md` | 37 | `chain now holds at every link that has ground truth.` | Addendum: "'ground truth' here meant the R1e/R1f CONDITIONAL_LATENT_LABELS plus the trader's own per-day table. The per-day table is FACT; the TAKE/SKIP assignment over our candidate stream is not." | `DO_NOT_EDIT_HISTORICAL` |
| C2-04 | `runs/OTR_R1_SERIES/out/hunt_C.py` | 6 | `with the ground-truth TAKE/SKIP labels from r12f_flip_features.csv, and scans` | Addendum only. Raw result under `out/`. | `DO_NOT_EDIT_HISTORICAL` |

### C2 adjacent — same defect, different wording (recommend folding into this sweep)

The literal phrase "ground truth" was mostly already avoided, but the same
epistemic claim survives under three synonyms. Flagging so the reset is not
cosmetic.

| File | Line | Text | Note |
|---|---|---|---|
| `.../CURRENT_TRUTH.md` | 145 | `Adversarially re-implemented: 42/42 cent-certain labels;` | "cent-certain labels" is the retired concept wearing a different coat. Proposed: `42/42 CONDITIONAL_LATENT_LABELS reproduced to the cent`. `NEEDS_HUMAN_JUDGEMENT` |
| `.../solar_family/TRACK_S_REPORT.md` | 115 | `42/42 cent-certain labels, all four components necessary` | same. `NEEDS_HUMAN_JUDGEMENT` |
| `.../HYPOTHESIS_LEDGER.csv` | 150 | `2023-01 labels + 2023-2025 master + 4 weekly windows` | "labels" unqualified. Proposed: `2023-01 CONDITIONAL_LATENT_LABELS + ...`. `SAFE_RENAME` |

---

## C3 — bare parity claims that do not name both endpoints

Rule: bare parity -> `IMPLEMENTATION_PARITY (Python <-> NinjaScript <-> NT8 engine)`.
Reason (directive v4.0 §1A): R6 compared three artefacts we built. It said
nothing about the original trader. `ORIGINAL_PARITY` (us <-> the trader) has
never been demonstrated and no line in this repo should imply it has.

| # | File | Line | Exact current text | Proposed replacement | Flag |
|---|---|---|---|---|---|
| C3-01 | `.../CURRENT_TRUTH.md` | 40 | `**Frontier statement**: with NT8 parity closed, June-July data ingested, and` | `**Frontier statement**: with IMPLEMENTATION_PARITY (Python <-> NinjaScript <-> NT8 engine) closed, June-July data ingested, and` | `SAFE_RENAME` |
| C3-02 | `.../CURRENT_TRUTH.md` | 46 | `R6 parity BIT-EXACT` (in the section header) | see C1-01 — one rewrite fixes both | `NEEDS_HUMAN_JUDGEMENT` |
| C3-03 | `.../CURRENT_TRUTH.md` | 50 | `- **R6 PARITY (PHASE C3 §8): PASS.** Layer A Jan-2023 cent-exact 91/91,` | `- **R6 IMPLEMENTATION_PARITY (Python <-> NinjaScript <-> NT8 engine) (PHASE C3 §8): PASS.** Layer A Jan-2023 cent-exact 91/91,` | `SAFE_RENAME` |
| C3-04 | `.../CURRENT_TRUTH.md` | 51 | `$6,815.00 == $6,815.00, trade-for-trade. Layer B two-year master BIT-EXACT:` | `$6,815.00 == $6,815.00, trade-for-trade between OUR Python and OUR NinjaScript. Layer B two-year master bit-identical between the same two endpoints:` | `SAFE_RENAME` |
| C3-05 | `.../CURRENT_TRUTH.md` | 132 | `## 2026-08-24g — R1-R4 RECONSTRUCTION EXECUTED; OTR-S-CAND1 RETIRED → OTR-S-CAND2 (verified model class)` | `(verified model class)` must go. It reads as ORIGINAL_PARITY. Proposed: `→ OTR-S-CAND2 (INFERENCE: model class consistent with the CONDITIONAL_LATENT_LABELS; members not separable)`. | `NEEDS_HUMAN_JUDGEMENT` |
| C3-06 | `.../HYPOTHESIS_LEDGER.csv` | 150 | hypothesis field `NT8 Strategy Analyzer parity (3 layers)`; status field `PARITY_PASS` | `NT8 Strategy Analyzer IMPLEMENTATION_PARITY (3 layers)`; `IMPLEMENTATION_PARITY_PASS` | `SAFE_RENAME` |
| C3-07 | `.../HYPOTHESIS_LEDGER.csv` | 150 | result field `Layer A cent-exact 91/91 $6815.00; Layer B bit-exact 4592/4592 $279655.00 ...` | prefix the field with `Python<->NinjaScript<->NT8:` so the endpoints ride with the numbers | `SAFE_RENAME` |
| C3-08 | `.../HYPOTHESIS_LEDGER.csv` | 145 | `parity divergence source 1 eliminated` | `IMPLEMENTATION_PARITY divergence source 1 eliminated` | `SAFE_RENAME` |
| C3-09 | `.../final/FINAL_PACKAGE.md` | 111 | `**20. Can each family run in NT8 with verified parity?**` | This is a verbatim owner-directive question. Do not rewrite the question; append the answer's endpoint naming instead. Proposed answer edit at line 112-114: `...Parity here means IMPLEMENTATION_PARITY (Python <-> NinjaScript <-> NT8 engine). ORIGINAL_PARITY is not in scope and has never been tested.` | `NEEDS_HUMAN_JUDGEMENT` |
| C3-10 | `.../ninjatrader_parity/PARITY_PLAN.md` | 28 | `3. Defer parity; the Python engines remain the certified reference (S0 proved the` | `certified reference` is a bare authority claim and `proved` is a C5 defect. Proposed: `3. Defer IMPLEMENTATION_PARITY; the Python engines remain the reference implementation (S0 REPRODUCED the ...` | `NEEDS_HUMAN_JUDGEMENT` |
| C3-11 | `.../ninjatrader_parity/PARITY_PLAN.md` | 33 | `totals. Compilation alone is not parity.` | `totals. Compilation alone is not IMPLEMENTATION_PARITY, and IMPLEMENTATION_PARITY is not ORIGINAL_PARITY.` | `SAFE_RENAME` |
| C3-12 | `.../FAMILY_MAP.md` | 73 | `proxy parity with exact parity.` | `proxy behavioral match with IMPLEMENTATION_PARITY.` | `SAFE_RENAME` |
| C3-13 | `.../volume_vwap_family/DATA_FEASIBILITY.md` | 23-24 | `ANY V-PROXY result carries the caveat: proxy parity is NOT exact parity (directive §17); a matching proxy mechanism is at best` | `...: a proxy behavioral match is NOT IMPLEMENTATION_PARITY and is certainly not ORIGINAL_PARITY (directive §17); a matching proxy mechanism is at best` | `SAFE_RENAME` |
| C3-14 | `.../COST_MODEL.md` | 3 | `## LAYER 1 — SCREENSHOT PARITY (behavioral reconstruction)` | "SCREENSHOT PARITY" is the closest thing in the repo to an `ORIGINAL_PARITY` claim and it is asserted as a routine layer name. Proposed: `## LAYER 1 — SCREENSHOT-ASSUMPTION MATCHING (behavioral reconstruction; this is an ORIGINAL_PARITY *attempt*, never an achieved parity)`. | `NEEDS_HUMAN_JUDGEMENT` |
| C3-15 | `.../COST_MODEL.md` | 11 | `- NEVER inject realistic costs into a parity comparison and then call the mismatch a` | `- NEVER inject realistic costs into an ORIGINAL_PARITY comparison and then call the mismatch a` | `SAFE_RENAME` |
| C3-16 | `.../solar_family/CAND2_NT8_PARITY_PROTOCOL.md` | 1 | `# CAND2 → NinjaScript parity protocol (directive v3.0 §7-§8, PHASE C3)` | `# CAND2 IMPLEMENTATION_PARITY protocol: our Python <-> our NinjaScript <-> NT8 engine (directive v3.0 §7-§8, PHASE C3)` | `SAFE_RENAME` |
| C3-17 | `.../vwap_flux_family/VF_CORE_PARITY_REPORT.md` | 1 (filename + title) | `# VF_CORE_PARITY_REPORT — V1/V2 lifecycle + formula falsification tests` | The filename says "parity" but the content is a formula-falsification study against vendor charts — no second endpoint exists. Proposed: retitle to `# VF_CORE_FORMULA_FALSIFICATION — V1/V2 lifecycle + rail-formula tests` and leave the filename (many inbound references) with a one-line note. | `NEEDS_HUMAN_JUDGEMENT` (rename breaks >= 6 inbound links) |
| C3-18 | `runs/OTR_R6_NT8_PARITY/REPORT.md` | 9 | `## Layer A — Jan-2023 window (comm 0): **PASS, cent-exact, trade-for-trade**` | Addendum only. | `DO_NOT_EDIT_HISTORICAL` |
| C3-19 | `runs/OTR_R6_NT8_PARITY/REPORT.md` | 14 | `## Layer B — two-year master 2023-01→2025-02 (comm 0): **PASS, bit-exact**` | Addendum only. | `DO_NOT_EDIT_HISTORICAL` |
| C3-20 | `runs/OTR_R6_NT8_PARITY/REPORT.md` | 31 | `Layer A/B prove LOGIC parity is bit-exact on identical data; Layer C deltas` | Addendum only (also a C5 hit: `prove`). | `DO_NOT_EDIT_HISTORICAL` |
| C3-21 | `runs/OTR_R6_NT8_PARITY/REPORT.md` | 36-37 | `1. **§51-E CLOSED: Python ↔ NinjaScript ↔ NT8 Strategy Analyzer are end-to-end consistent (bit-exact on shared data).**` | Note in the addendum that this line is the *one place in the corpus that already names all three endpoints correctly*, and that it is therefore the model wording for the C3 rewrites elsewhere. No correction needed to its substance. | `DO_NOT_EDIT_HISTORICAL` |
| C3-22 | `runs/OTR_V1_PROXY/spec.yaml` | 11 | `BEHAVIORALLY MATCHED - MECHANISM UNIDENTIFIED. Never conflate with exact parity.` | Addendum: "'exact parity' here means IMPLEMENTATION_PARITY." Substance is correct and cautious. | `DO_NOT_EDIT_HISTORICAL` |

### C3 benign occurrences — no change proposed

`runs/OTR_R9_HP_BUILD/spec.yaml:12`, `runs/OTR_R1_SERIES/spec.yaml:54, 88`,
`runs/OTR_R1_SERIES/out/hunt_C_stopentry.py:6, 87` — all use "cent-exact" to
describe a numeric agreement between two named series, which is a legitimate
`REPRODUCED` claim.

---

## C4 — "solved" / "CONFIRMED" applied to the VWAP anchor lifecycle and rails

Reason (directive v4.0): the lifecycle question was settled against *vendor*
material and *our own* morphology statistics, never against the trader's build.
"CONFIRMED" is not one of the five status values. Most of these are `INFERENCE`;
a few are `FACT` about the vendor and `UNKNOWN` about the trader, and that split
must be written out.

| # | File | Line | Exact current text | Proposed replacement | Flag |
|---|---|---|---|---|---|
| C4-01 | `.../vendor_forensics/PURCHASE_GATE.md` | 6 | `- CLOUD GEOMETRY: solved-to-class (VF-ANCHOR + percentile rails; VF_CORE_PARITY_REPORT;` | `- CLOUD GEOMETRY: INFERENCE, narrowed to a class (VF-ANCHOR + percentile rails; ...` | `SAFE_RENAME` |
| C4-02 | `.../vendor_forensics/PURCHASE_GATE.md` | 8 | `- TREND STATE: solved-to-cluster (T_C leader 13/17 LOWO; input bound 1.7%).` | `- TREND STATE: INFERENCE, narrowed to an inseparable cluster (T_C leader 13/17 LOWO; input bound 1.7%).` | `SAFE_RENAME` |
| C4-03 | `.../vendor_forensics/PURCHASE_GATE.md` | 9 | `- STOP/RISK: solved (130-pt fixed; pre-dates VF per 2026_VARIANT_LEDGER — wrapper-level).` | Split. FACT: `−$2,600 appears in 18 reports from wk 2026-02-01`. INFERENCE: `130-pt x qty-1 is the only tested microstructure that generates that row; 65-pt x 2 FALSIFIED (R3)`. Drop "solved". | `NEEDS_HUMAN_JUDGEMENT` |
| C4-04 | `.../vwap_flux_family/OWNER_REPORT_RECONCILIATION.md` | 9 | `\| Rolling anchored-VWAP population, oldest dropped \| very high \| CONFIRMED \| VF1-4 image-fidelity + vf_core morphology \|` | status cell -> `INFERENCE (vendor-level; trader-level UNKNOWN)` | `SAFE_RENAME` |
| C4-05 | `.../vwap_flux_family/OWNER_REPORT_RECONCILIATION.md` | 10 | `\| Lifecycle = ACTIVE anchors (all keep updating), not frozen blocks \| ~90-95% ... \| CONFIRMED-incumbent + falsifier defined \| ...` | status cell -> `INFERENCE (incumbent reading; falsifier defined and never observed)` | `SAFE_RENAME` |
| C4-06 | `.../vwap_flux_family/OWNER_REPORT_RECONCILIATION.md` | 11 | `\| Rails = percentile linear interpolation \| high, "not proven" \| **RESOLVED at vendor level without purchase** \| EV-040: ...` | `\| ... \| **INFERENCE at vendor level from EV-040 chart geometry; min-max FALSIFIED at vendor level; linear-vs-nearest-rank UNKNOWN** \|` | `NEEDS_HUMAN_JUDGEMENT` |
| C4-07 | `.../vwap_flux_family/OWNER_REPORT_RECONCILIATION.md` | 12 | `\| FVP = Q50 median \| ~95% \| RESOLVED (vendor level) \| EV-040 same geometry \|` | `\| ... \| INFERENCE (vendor level, EV-040 geometry) \|` | `SAFE_RENAME` |
| C4-08 | `.../vwap_flux_family/OWNER_REPORT_RECONCILIATION.md` | 24 | `1. Lifecycle (report's "largest unresolved part") — closed to incumbent+falsifier.` | `1. Lifecycle — narrowed to one incumbent INFERENCE plus a defined falsifier. Not closed: the trader-build lifecycle remains UNKNOWN.` | `NEEDS_HUMAN_JUDGEMENT` |
| C4-09 | `.../vwap_flux_family/PUBLIC_ANALOGUE_MAP.md` | 284 | `- Smooth intra-hour rail drift + discrete jumps on the hour → VF-ANCHOR confirmed (jump` | `- Smooth intra-hour rail drift + discrete jumps on the hour → VF-ANCHOR supported (jump` (this is a conditional discriminator, so the softening is enough) | `SAFE_RENAME` |
| C4-10 | `.../vwap_flux_family/VF_CORE_PARITY_REPORT.md` | 57 | `stretched-range midpoint → **percentile-family CONFIRMED, min-max REJECTED at the vendor level (EV-040)**` | `→ **percentile-family INFERENCE (vendor level), min-max FALSIFIED at the vendor level (EV-040); the trader's build is not addressed by this test**` | `NEEDS_HUMAN_JUDGEMENT` |
| C4-11 | `.../vwap_flux_family/VF_CORE_PARITY_REPORT.md` | 59 | `between confirm VF-ANCHOR visually. Signal arrows on both charts fire on` | `between support VF-ANCHOR visually. Signal arrows on both charts fire on` | `SAFE_RENAME` |
| C4-12 | `.../vwap_flux_family/SIGNAL_TREND_IDENTIFICATION.md` | 25 | `trend LAYER is effectively solved-to-cluster; remaining ambiguity does not` | `trend LAYER is narrowed to an inseparable cluster (INFERENCE); remaining ambiguity does not` | `SAFE_RENAME` |
| C4-13 | `.../vwap_flux_family/VENDOR_SIGNAL_USAGE_MODEL.md` | 49 | `the +2/+1/-1/-2 hypothesis for Signal_Trend is **CONFIRMED for the current build** and` | `... is **FACT for the current VENDOR build (manual + changelog), UNKNOWN for the trader's build** and` | `NEEDS_HUMAN_JUDGEMENT` |
| C4-14 | `.../vwap_flux_family/VF_CLEANROOM_SPEC.md` | 28 | `candle-close-location (CLV) filter — H1 family CONFIRMED; direction reading ambiguous` | `candle-close-location (CLV) filter — H1 family is FACT at vendor level (manual §2.12); direction reading UNKNOWN` | `SAFE_RENAME` |
| C4-15 | `.../CONVERGENCE_PASS_ANSWERS_20260824.md` | 56 | `**J. Percentile-linear or something else?** PERCENTILE family — RESOLVED at` | `**J.** PERCENTILE family — INFERENCE at vendor level (EV-040); trader build UNKNOWN, at` | `SAFE_RENAME` |
| C4-16 | `.../CONVERGENCE_PASS_ANSWERS_20260824.md` | 82 | `**O. Split=5 meaning?** SOLVED (manual): min bars between consecutive same-direction signals.` | `**O.** FACT (vendor manual §2.13): min bars between consecutive same-direction signals. INFERENCE: the trader's Split=5 carries the same semantics — untested against his build.` | `NEEDS_HUMAN_JUDGEMENT` |
| C4-17 | `.../CHANGEPOINT_MAP.md` | 24 | `\| **VWAP Flux params CONFIRMED (EV-006)** \| **V-family (CONFIRMED product)** \|` | `\| **VWAP Flux params FACT (readable in EV-006 frame)** \| **V-family (FACT: params visible)** \|` | `SAFE_RENAME` |
| C4-18 | `.../CHANGEPOINT_MAP.md` | 31 | `\| **VWAP Flux params CONFIRMED (EV-006)**; window LOCKED \| V-family (CONFIRMED product; data blocked) \|` | same mapping as C4-17 | `SAFE_RENAME` |

### C4 spillover — the wider `CONFIRMED` sprawl (recommend a second pass)

`CONFIRMED` appears **44 times across 21 files** in scope. The 18 above are the
VWAP-anchor/rails subset named by the task. The remaining 26 are mostly
`OTR_COMPONENT_PROBABILITY_MAP.md` (8), `CURRENT_TRUTH.md` (4),
`RISK_STATE_MACHINE_2025.md` (3), `HYPOTHESIS_LEDGER.csv` (3), and single hits
in `ARCHITECTURE_CANDIDATES.md`, `FINAL_PACKAGE.md`,
`OTR_CONVERGENCE_PRESTATE.md`, `SCREENSHOT_AUDIT_REPORT.md`,
`PRE_AUDIT_HYPOTHESES.md` (2), `VWAP_FLUX_VERSION_TIMELINE.md`,
`per_image/OTRIMG-0125.md`. Most of those are `CONFIRMED (Class A)`, which maps
mechanically to `FACT`. That mapping is the cheapest large win in the whole
reset and is safe to script — see the auto-rename list below.

---

## C5 — "proves" / "proven" applied to EV-039 or to author reimplementation

Reason (directive v4.0): EV-039 is a FACT about the *vendor manual*. Everything
downstream — that the trader's 2026 stack is his own reimplementation, that his
build contains an active pullback layer — is INFERENCE. Several sentences here
violate the no-mixing rule inside a single clause.

| # | File | Line | Exact current text | Proposed replacement | Flag |
|---|---|---|---|---|---|
| C5-01 | `.../vwap_flux_family/VF_CORE_PARITY_REPORT.md` | 51-52 | `Our bar-level clone is therefore the SAME input class as his build, not an approximation of it.` | Delete or fully re-hedge. Proposed: `INFERENCE: if the EV-039 reading holds, our bar-level clone shares an input class with his build rather than approximating a tick-level original. This is entailed only under the reading that his displayed mode was also his computing mode — itself UNKNOWN.` | `NEEDS_HUMAN_JUDGEMENT` |
| C5-02 | `.../vwap_flux_family/VF_CORE_PARITY_REPORT.md` | 48-50 | `→ his 2026 stack is most plausibly his OWN bar-data implementation with vendor-style parameter names (H4/H3 > H1).` | Already hedged ("most plausibly"). Add the status token: `INFERENCE: his 2026 stack is most plausibly ...` | `SAFE_RENAME` |
| C5-03 | `.../vendor_forensics/PURCHASE_GATE.md` | 15-18 | `His backtests therefore cannot be the licensed indicator in that mode, and the leading reading ... is his OWN implementation.` | Split. FACT (manual §2.1 p5): the licensed indicator computes nothing historically in that mode. FACT: his frames show that mode and full backtests. INFERENCE: therefore either the mode shown is not the mode used, or the indicator is not the licensed one; the second is the leading reading. | `NEEDS_HUMAN_JUDGEMENT` |
| C5-04 | `.../EVIDENCE_LEDGER.csv` | 40 | EV-039 notes field: `leading resolution: his 2026 stack is his OWN reimplementation (or heavily adapted variant) computing from bar data` | Prefix `INFERENCE (leading):`. The evidence-class column is already `A` and that is correct for the manual sentence — but the class letter is attached to the row, so an inference in the notes inherits an `A` by proximity. Add an explicit `INFERENCE` marker inside the field. | `NEEDS_HUMAN_JUDGEMENT` |
| C5-05 | `.../HYPOTHESIS_LEDGER.csv` | 149 | `H1 requires empty historical backtests - contradicted` / notes `... -> own implementation with vendor-style names is leading` | Add `INFERENCE:` before `own implementation ...`. The `H1 DISFAVORED` verdict itself is sound. | `SAFE_RENAME` |
| C5-06 | `.../vwap_flux_family/OWNER_REPORT_RECONCILIATION.md` | 34-36 | `EV-039: BidAskPrice_RealVolume + Tick Replay OFF computes NOTHING historically, yet his SA backtests are full → his stack is most plausibly his OWN bar-data implementation (H3/H4), not the embedded licensed indicator.` | Split the arrow: everything left of `→` is FACT, everything right is INFERENCE. Same one-line fix as C5-03. | `NEEDS_HUMAN_JUDGEMENT` |
| C5-07 | `.../CURRENT_TRUTH.md` | 3 | `## 2026-08-24l — IMG-16 chart-content pass: corpus label-surface EXHAUSTION now PROVEN; EV-041 recovered from the black frame` | `## 2026-08-24l — IMG-16 chart-content pass: corpus label-surface exhaustion REPRODUCED for the 164-image corpus at the 2026-08-24 sweep (endpoints: our sweep script <-> the 164 audit records); EV-041 recovered from the black frame` | `NEEDS_HUMAN_JUDGEMENT` |
| C5-08 | `.../CURRENT_TRUTH.md` | 17-18 | `- **Terminal frontier statement (proven, not assumed)**: corpus, local artifacts, public web, and bounded-member compute are ALL exhausted.` | `- **Terminal frontier statement (INFERENCE from four completed searches, not a proof)**: corpus, local artifacts, public web, and bounded-member compute returned nothing further on 2026-08-24. Exhaustion of a search is not exhaustion of the space.` | `NEEDS_HUMAN_JUDGEMENT` |
| C5-09 | `.../CURRENT_TRUTH.md` | 125-126 | `- **A3-A5 retune (→3/6/9, 11/7) is INVISIBLE to a T1-only model (old≡new179 streams bit-identical) → the trader's build contains an ACTIVE pullback layer**` | Mandatory split. REPRODUCED: `our old-param and new-param T1-only streams are bit-identical over the master window`. INFERENCE: `he would not retune a knob with no effect, so his build plausibly contains a layer those params control — assuming he retuned deliberately and that the retune was not cosmetic`. | `NEEDS_HUMAN_JUDGEMENT` |
| C5-10 | `.../CONVERGENCE_PASS_ANSWERS_20260824.md` | 16-19 | `NEW structural proof: the Nov A3-A5 retune (5/10/10→3/6/9) is bit-invisible to a T1-only stream (old≡new179), so his build MUST contain an active layer those knobs control.` | `NEW structural observation (REPRODUCED): the Nov A3-A5 retune is bit-invisible to a T1-only stream (old≡new179). INFERENCE: his build plausibly contains a layer those knobs control. "MUST" is not supported — a cosmetic or abandoned retune is not excluded.` | `NEEDS_HUMAN_JUDGEMENT` |
| C5-11 | `.../solar_family/RESIDUAL_EVENT_CLUSTERS.md` | 28-30 | `A3-A5 retune invisibility (R5 finding 2) proves an active pullback layer in his build;` | `A3-A5 retune invisibility (R5 finding 2) is consistent with an active pullback layer in his build (INFERENCE);` | `SAFE_RENAME` |
| C5-12 | `.../solar_family/TRACK_S_REPORT.md` | 152-153 | `A3-A5 retune proven invisible to T1-only stream → active pullback layer in his build (residual's home).` | `A3-A5 retune REPRODUCED as invisible to our T1-only stream. INFERENCE: active pullback layer in his build (residual's home).` | `NEEDS_HUMAN_JUDGEMENT` |
| C5-13 | `.../final/FINAL_PACKAGE.md` | 54 | `2026 weeks are proven non-Family-S (S8: 2× counts, half holds under the S candidate).` | `2026 weeks are FALSIFIED as Family-S *under the frozen S candidate* (S8: 2× counts, half holds). A different S-family member is not excluded.` | `NEEDS_HUMAN_JUDGEMENT` |
| C5-14 | `.../screenshot_forensics/BACKTEST_VS_LIVE_AUDIT.md` | 14 | `1. **Contemporaneity is proven for the weekly series**: 58/70 reports have capture-lag = 0 days` | `1. **Contemporaneity is FACT for 58/70 reports and INFERENCE for the series**: 58/70 reports have capture-lag = 0 days` | `SAFE_RENAME` |
| C5-15 | `.../multiblock_family/TRACK_B_STATUS.md` | 31 | `- S8 proved the Solar candidate cannot produce the 2026 window fingerprints — some non-Solar machinery traded 2026 [B].` | `- S8 FALSIFIED the frozen Solar candidate as a producer of the 2026 window fingerprints. INFERENCE: some non-Solar machinery traded 2026 [B].` | `SAFE_RENAME` |
| C5-16 | `.../solar_transition_family/FEB2025_FAST_BUILD.md` | 42-44 | `**This is the same layer family the S4 retune later touches**: R5 proved A3-A5 (5/10/10→3/6/9) only affect pullback/weak-state machinery, invisible to T1 flips` | `R5 REPRODUCED that A3-A5 affect only pullback/weak-state machinery in OUR engine, invisible to T1 flips. INFERENCE: same layer family as the S4 retune.` | `SAFE_RENAME` |
| C5-17 | `.../vendor_forensics/LOCAL_ARTIFACT_SEARCH_20260824.md` | 40-41 | `Its presence here proves the NAMING convention is shared across ninZa-packaged products; it is NOT a VWAP Flux artifact.` | `Its presence here is FACT: the NAMING convention is shared across ninZa-packaged products. It is NOT a VWAP Flux artifact.` (drop "proves"; the claim itself is a direct file-system observation and legitimately FACT) | `SAFE_RENAME` |
| C5-18 | `.../solar_family/src/run_s0.py` | 28 | `# ---- ARM_PYTHON series equality (signal engine already proven; cheap re-verify) ----` | `# ---- ARM_PYTHON series equality (signal engine already REPRODUCED vs vendor series; cheap re-verify) ----` | `SAFE_RENAME` (comment) |
| C5-19 | `.../CONVERGENCE_PASS_ANSWERS_20260824.md` | 31 | `the one NT8-forced semantic difference was proven a non-difference (R1.j).` | `the one NT8-forced semantic difference was REPRODUCED as a non-difference over the master window (R1.j: 0 stream differences, 4577 identical trades).` | `SAFE_RENAME` |
| C5-20 | `runs/OTR_R6_NT8_PARITY/REPORT.md` | 31 | `Layer A/B prove LOGIC parity is bit-exact on identical data;` | Addendum only. | `DO_NOT_EDIT_HISTORICAL` |
| C5-21 | `runs/OTR_R6_NT8_PARITY/spec.yaml` | 41 | `differences under test: none expected (R1.j proved gate-timing equivalence);` | Addendum only. Preregistration. | `DO_NOT_EDIT_HISTORICAL` |
| C5-22 | `runs/OTR_S8_CROSSWINDOW/spec.yaml` | 22 | `(signals recomputed via solar_wave_full — proven bit-equal to vendor; different` | Addendum only. Note that this line *does* name both endpoints (our code <-> vendor indicator) and is a legitimate `REPRODUCED`; only the verb is off. | `DO_NOT_EDIT_HISTORICAL` |
| C5-23 | `runs/OTR_R2_STOPGROUP/spec.yaml` | 11 | `PREREGISTERED STOP-SEMANTICS GRID (points; the -1300 caps prove point units):` | Addendum only. | `DO_NOT_EDIT_HISTORICAL` |
| C5-24 | `runs/OTR_R1_SERIES/out/hunt_B_result.md` | 72 | `destroys the account; the trader's aggregate proves his gate did NOT repeat weekly.` | Addendum only. Raw result. | `DO_NOT_EDIT_HISTORICAL` |
| C5-25 | `runs/OTR_R1_SERIES/out/hunt_B_result.md` | 136 | `trigger is unresolved; its entry bar carries no Solar event, which independently proves the` | Addendum only. Raw result. | `DO_NOT_EDIT_HISTORICAL` |

### C5 benign occurrences — no change proposed

`ARCHITECTURE_CANDIDATES.md:11` (`attractive, unproven`),
`EVIDENCE_LEDGER.csv:3, 6, 10` (`not proven invariant`, `UNPROVEN`,
`does not prove`), `FAMILY_MAP.md:17, 51`, `UNKNOWN_FIELDS.md:47`,
`VENDOR_SIGNAL_USAGE_MODEL.md:5, 77`, `VWAP_FLUX_VERSION_TIMELINE.md:7, 102`,
`VF_PANEL_COMPLETENESS_NOTE.md:48, 96, 97, 123`,
`PARAMETER_VERSION_TIMELINE.md:4`, `PRE_AUDIT_HYPOTHESES.md:57`,
`2026_VARIANT_LEDGER.csv:5`, `BACKTEST_VS_LIVE_AUDIT.md:22, 31`,
`per_image/OTRIMG-0104.md:109` — these use "proven/unproven" correctly, as
*negations* or explicit hedges. They are the house style the rest of the corpus
should be moved toward.

---

## Files safe to auto-rename

Every flagged hit in these files is `SAFE_RENAME`. A scripted substitution can
run against them without a reviewer, provided the script touches only the exact
strings listed above.

| File | Hits | Substitutions needed |
|---|---|---|
| `research/original_trader_reconstruction/vwap_flux_family/src/run_r8_june.py` | 2 | `TRUE OOS` -> `HELD_OUT_RECONSTRUCTION_WINDOW` (docstring + print string) |
| `research/original_trader_reconstruction/solar_family/src/run_r1f_features.py` | 1 | `ground-truth labels` -> `CONDITIONAL_LATENT_LABELS` (comment) |
| `research/original_trader_reconstruction/solar_family/src/run_s0.py` | 1 | `already proven` -> `already REPRODUCED vs vendor series` (comment) |
| `research/original_trader_reconstruction/vwap_flux_family/SIGNAL_TREND_IDENTIFICATION.md` | 1 | `solved-to-cluster` -> `narrowed to an inseparable cluster (INFERENCE)` |
| `research/original_trader_reconstruction/multiblock_family/TRACK_B_STATUS.md` | 1 | `S8 proved` -> `S8 FALSIFIED ... INFERENCE:` |
| `research/original_trader_reconstruction/solar_transition_family/FEB2025_FAST_BUILD.md` | 1 | `R5 proved` -> `R5 REPRODUCED ... INFERENCE:` |
| `research/original_trader_reconstruction/solar_family/RESIDUAL_EVENT_CLUSTERS.md` | 1 | `proves an active pullback layer` -> `is consistent with an active pullback layer (INFERENCE)` |
| `research/original_trader_reconstruction/volume_vwap_family/DATA_FEASIBILITY.md` | 1 | `proxy parity is NOT exact parity` -> `proxy behavioral match is NOT IMPLEMENTATION_PARITY` |
| `research/original_trader_reconstruction/FAMILY_MAP.md` | 1 | `proxy parity with exact parity` -> `proxy behavioral match with IMPLEMENTATION_PARITY` |
| `research/original_trader_reconstruction/CHANGEPOINT_MAP.md` | 2 | `CONFIRMED` -> `FACT` (both are readable-in-frame parameter claims) |
| `research/original_trader_reconstruction/OTR_COMPONENT_PROBABILITY_MAP.md` | 8 | `CONFIRMED (Class A)` -> `FACT`; `CONFIRMED (A)` -> `FACT`; `CONFIRMED-ATTRIBUTED (A)` -> `FACT (value) + INFERENCE (attribution)` |
| `research/original_trader_reconstruction/vendor_forensics/LOCAL_ARTIFACT_SEARCH_20260824.md` | 2 | `proves the NAMING convention` -> `is FACT: the NAMING convention`; `numerical ground truth` -> `numerical oracle` |
| `research/original_trader_reconstruction/solar_family/CAND2_NT8_PARITY_PROTOCOL.md` | 1 | title -> `IMPLEMENTATION_PARITY protocol: our Python <-> our NinjaScript <-> NT8 engine` |

**Not safe to auto-rename** (mixed flags or high blast radius, needs a human):
`CURRENT_TRUTH.md`, `CONVERGENCE_PASS_ANSWERS_20260824.md`,
`HYPOTHESIS_LEDGER.csv`, `EVIDENCE_LEDGER.csv`,
`vwap_flux_family/OWNER_REPORT_RECONCILIATION.md`,
`vwap_flux_family/VF_CORE_PARITY_REPORT.md`,
`vendor_forensics/PURCHASE_GATE.md`, `final/FINAL_PACKAGE.md`,
`ninjatrader_parity/PARITY_PLAN.md`, `COST_MODEL.md`,
`solar_family/TRACK_S_REPORT.md`,
`screenshot_forensics/per_image/OTRIMG-0029.md`,
`vwap_flux_family/VENDOR_SIGNAL_USAGE_MODEL.md`,
`vwap_flux_family/VF_CLEANROOM_SPEC.md`.

---

## Addenda to create under `runs/OTR_*` (no edits)

| Run | New file | Covers |
|---|---|---|
| `runs/OTR_R8_JUNE2026/` | `TERMINOLOGY_ADDENDUM_v4.md` | C1-16, C1-17, C1-18 |
| `runs/OTR_R6_NT8_PARITY/` | `TERMINOLOGY_ADDENDUM_v4.md` | C2-03, C3-18, C3-19, C3-20, C3-21, C5-20, C5-21 |
| `runs/OTR_R5_CAND2_WEEKLY_VALIDATION/` | `TERMINOLOGY_ADDENDUM_v4.md` | C1-19 |
| `runs/OTR_R1_SERIES/` | `TERMINOLOGY_ADDENDUM_v4.md` | C2-04, C5-24, C5-25 |
| `runs/OTR_S8_CROSSWINDOW/` | `TERMINOLOGY_ADDENDUM_v4.md` | C5-22 |
| `runs/OTR_R2_STOPGROUP/` | `TERMINOLOGY_ADDENDUM_v4.md` | C5-23 |
| `runs/OTR_V1_PROXY/` | `TERMINOLOGY_ADDENDUM_v4.md` | C3-22 |

Each addendum should carry the same header: *"This file adds directive-v4.0
vocabulary to an immutable run record. The original spec.yaml, REPORT.md and
out/ contents are unchanged and remain the authoritative history."*

---

## Top 10 most misleading single sentences found

Ranked by how far the sentence's grammar carries the reader past what the
evidence supports.

1. **`vwap_flux_family/VF_CORE_PARITY_REPORT.md:51-52`** — *"Our bar-level clone
   is therefore the SAME input class as his build, not an approximation of it."*
   A vendor-manual clause about Tick Replay is converted, in one "therefore",
   into a positive identity claim about a private build nobody has seen. The
   clause "not an approximation of it" actively forecloses the possibility it
   should be preserving.

2. **`CONVERGENCE_PASS_ANSWERS_20260824.md:16-19`** — *"NEW structural proof: the
   Nov A3-A5 retune ... is bit-invisible to a T1-only stream (old≡new179), so
   his build MUST contain an active layer those knobs control."*
   "Proof" plus "MUST" on an argument whose hidden premise is that the trader
   never made a cosmetic or abandoned parameter change.

3. **`CURRENT_TRUTH.md:125-126`** — *"A3-A5 retune ... is INVISIBLE to a T1-only
   model (old≡new179 streams bit-identical) → the trader's build contains an
   ACTIVE pullback layer"* — the same defect in the campaign's most-read file,
   and a textbook violation of the no-mixing rule: a REPRODUCED measurement and
   an INFERENCE joined by an arrow inside one bolded sentence.

4. **`CURRENT_TRUTH.md:46`** — *"R6 parity BIT-EXACT; ... VF-CAND1 survives TRUE
   OOS"* — a single header that asserts both retired claims. A reader skimming
   `CURRENT_TRUTH.md` takes away "we matched the trader exactly and confirmed it
   out-of-sample," when R6 compared three of our own artefacts and R8 scored
   held-out windows whose outcomes we had already read.

5. **`CURRENT_TRUTH.md:17-18`** — *"**Terminal frontier statement (proven, not
   assumed)**: corpus, local artifacts, public web, and bounded-member compute
   are ALL exhausted."* — the parenthesis explicitly claims proof status for
   what is a negative result from four finite searches. "Proven, not assumed" is
   the most self-certifying phrase in the corpus.

6. **`CURRENT_TRUTH.md:132`** — *"OTR-S-CAND1 RETIRED → OTR-S-CAND2 (verified
   model class)"* — "verified" against what? The parenthesis reads as
   ORIGINAL_PARITY. CAND2 was fitted to CONDITIONAL_LATENT_LABELS derived from
   our own candidate stream.

7. **`vendor_forensics/PURCHASE_GATE.md:9`** — *"STOP/RISK: solved (130-pt fixed;
   pre-dates VF ... — wrapper-level)."* — "solved" for a parameter inferred from
   the arithmetic of a largest-loss column. The −$2,600 row is FACT; that it was
   produced by one 130-point stop rather than any other configuration that
   yields the same row is INFERENCE, and R3 tested exactly two candidates.

8. **`final/FINAL_PACKAGE.md:54`** — *"2026 weeks are proven non-Family-S (S8: 2×
   counts, half holds under the S candidate)."* — the parenthesis quietly
   concedes "under the S candidate" while the main clause claims the whole
   family is excluded. What was falsified is one frozen member.

9. **`vwap_flux_family/OWNER_REPORT_RECONCILIATION.md:11`** — *"Rails = percentile
   linear interpolation | high, 'not proven' | **RESOLVED at vendor level without
   purchase**"* — the row prints the source's own "not proven" confidence in one
   column and our bolded **RESOLVED** in the next, so the table upgrades an
   external hedge into a settled result on sight.

10. **`runs/OTR_R6_NT8_PARITY/REPORT.md:31`** — *"Layer A/B prove LOGIC parity is
    bit-exact on identical data"* — immutable history, so it stays, but it is
    the origin sentence for the bare "bit-exact" that then propagated into
    `CURRENT_TRUTH.md` and `HYPOTHESIS_LEDGER.csv` with the qualifier "on
    identical data" progressively dropped. Line 36 of the same file names all
    three endpoints correctly; line 31 is what got quoted onward.

---

## Method note

Searches were run with ripgrep over `.md`, `.yaml`, `.yml`, `.csv` and `.py`
under the two scoped trees. The initial pattern set missed hyphenated variants
(`true-OOS` in `OWNER_REPORT_RECONCILIATION.md:39`) and required a second,
broader pass; any future sweep should search
`true[- ]?OOS`, `fully[- ]?OOS`, `ground.?truth`, `bit.?exact`, `prove[sndr]?`,
`\bsolved\b`, `CONFIRMED` rather than literal phrases.
`original_screenshot/` was not read or modified in this sweep.
