# REVISION_HISTORY — OTR campaign #6 claim authority

Append-only. Newest entry first. Every entry records what **changed**, not what is true; the
current state always lives in `CLAIM_REGISTRY.csv` → `CURRENT_KNOWN.md` /
`CURRENT_HYPOTHESES.md` / `FALSIFIED_HYPOTHESES.md`.

---

# 2026-08-24 — Directive v4.0 epistemic reset

**Trigger**: OWNER MASTER DIRECTIVE v4.0. Prior work stated inferences as facts; every claim in the
campaign was re-read and assigned exactly one of FACT / REPRODUCED / INFERENCE / UNKNOWN /
FALSIFIED, with observation and interpretation split into separate sentences.

**Artifacts created in this pass** (all under
`research/original_trader_reconstruction/`):
`CLAIM_REGISTRY_early.csv` (36 rows) · `CLAIM_REGISTRY_2026.csv` (105 rows) ·
`CLAIM_REGISTRY.csv` (141 rows, merged + severity-sorted) · `CURRENT_KNOWN.md` ·
`CURRENT_HYPOTHESES.md` · `FALSIFIED_HYPOTHESES.md` · `REVISION_HISTORY.md` (this file) ·
`RUN_PROVENANCE.csv` (29 runs) · `MODEL_REGISTRY.yaml` (76 model identities) ·
`TERMINOLOGY_SWEEP.md` (102 hits, plan only — **no live doc has been edited yet**) ·
`vwap_flux_family/2026_PANEL_TOPOLOGY.md` + `2026_panel_rows.csv`.

**Post-merge status distribution**: FACT 46 · REPRODUCED 24 · INFERENCE 30 · UNKNOWN 30 ·
FALSIFIED 11 = 141.

**Registry-merge conventions applied** (recorded so they are auditable, not silent):
- The two half-registries were written by different agents with different headers. The merged file
  uses an 18-column superset; no field content was altered, dropped or re-worded. `registry_half`
  records which half each row came from.
- The early header's `object` and the 2026 header's `layer` are merged into `object_or_layer`;
  `raw_observation` and `basis` into `raw_observation_or_basis`; `competing_hypotheses` and
  `live_competitors` into `competing_hypotheses`; `endpoints_if_parity` and `parity_endpoints` into
  `parity_endpoints`. The early half's four evidence columns are kept separate from the 2026 half's
  single `evidence_refs`; empties are genuine, not lost data.
- `last_reviewed = 2026-08-24` was **assigned** to all 105 V-rows (the early half carried the field;
  the 2026 half did not). This is a convention of this pass, not a datum read from the source file.
- Sort order: status severity (FACT → REPRODUCED → INFERENCE → UNKNOWN → FALSIFIED), then id.

---

## 1. Claims whose status or wording CHANGED in this pass (55)

Format: `claim_id | old wording | new status | why`.

### 1.1 Early half — Solar / CAND2 era (20)

| claim_id | old wording | new status | why |
|---|---|---|---|
| **E-001** | "values approximate" (EV-001, owner-relayed precursor); rounded notes in `TARGET_WINDOWS.csv` row EARLY_LONG | **FACT** | The panel was re-read pixel-by-pixel; a full-precision direct read supersedes an owner-relayed approximation. |
| **E-002** | "SelTime window is HARD-CODED" — `CURRENT_TRUTH.md` 2026-08-24e, asserted with no inference marker | **INFERENCE** | Hard-coding is a reading of an *absence* in a panel group. Three rivals stay live (TradingHours template; `SelTime` names something else; boxes below the crop). |
| **E-004** | "Solar vendor indicator 100% reverse-engineered", endpoints never named | **REPRODUCED** | Relabelled IMPLEMENTATION_PARITY with both endpoints named (our `solarwave.py` ↔ the vendor indicator's own exported series). It says nothing about the trader's build. |
| **E-005** | any wording asserting his engine **is** the vendor Solar Wave RK indicator | **UNKNOWN** | No frame shows his indicator output, his source body, or any per-bar series of his. |
| **E-006** | rounded target values (292000 / −32700 / 67 / 94) in `TARGET_WINDOWS.csv` + `CURRENT_TRUTH.md` paraphrase | **FACT** | Cent-precision transcription of the Summary($) grid supersedes the rounded paraphrase. |
| **E-008** | wording presenting the band-edge master fit as a match / as "reproducing the trader" | **REPRODUCED** | Recorded as a **distance**: +5.7% trades, −9.3% net, residual +247 trades / −$27.2k. The numbers differ; this is not parity. |
| **E-009** | "R6 parity BIT-EXACT" / "R6 PARITY: PASS" — `CURRENT_TRUTH.md` 2026-08-24j and `runs/OTR_R6_NT8_PARITY/REPORT.md` verdict 1, no endpoints named | **REPRODUCED** | Relabelled **IMPLEMENTATION_PARITY**: our Python ↔ our NinjaScript ↔ the NT8 engine. The trader is not an endpoint of the test. |
| **E-010** | "OTR-S-CAND2 (verified model class)" — `CURRENT_TRUTH.md` 2026-08-24g; "the verified model class" in `OriginalTraderSolarCAND2_v2.cs` header lines 11–12 | **UNKNOWN** | ORIGINAL_PARITY has never been tested: no test in the campaign has the trader as an endpoint. All comparisons are aggregate-vs-aggregate. |
| **E-012** | "verified model class"; "model CLASS, not a point" (`OTR_CONVERGENCE_PRESTATE.md` line 6); `.cs` header lines 10–13 | **INFERENCE** | The code read (E-011) shows A1 assigned once and read nowhere, `weak` never reaching `signalTradeVal`, and no A5 input at all — CAND2 is not parameter-faithful to the visible A1–A5 panel. |
| **E-014** | "42/42 cent-certain daily labels held"; "42/42 cent-certain labels"; "STRUCTURE CONFIRMED (42/42 labels)" | **INFERENCE** | Retitled **CONDITIONAL_LATENT_LABELS**. R1e generated *our* candidate universe and solved for removals; `OTR_R11_INVERSE` shows six different universes each admit exactly one solution on 01-09/10/11. |
| **E-017** | "D-gate constants X=1600 X2=2500 C=700 K=3 cap=20 cooldown=3" quoted as identified values | **UNKNOWN** | No corpus frame shows any of them; K3 has an equally label-consistent rival (ALT_loss_side_K4); the four separating days are absent from the corpus. |
| **E-018** | "STRUCTURE CONFIRMED (42/42 labels)"; "structure CONFIRMED by independent re-implementation" | **INFERENCE** | Its entire support is the CONDITIONAL_LATENT_LABELS plus a re-implementation that reproduces the same *latent* assignments. Necessity is necessity **within our universe**. |
| **E-020** | "B1: no entry decision on a session's first bar (matches his visible code line)" | **INFERENCE** | The if-block body is unseen. Our own file uses the same predicate for two different purposes (lines 236–247 vs 290–291) — exactly the ambiguity the old wording erased. |
| **E-023** | "hp-machine weeks are a sibling build", stated as a finding | **INFERENCE** | Counterexample on record: OTRIMG-0081 (hp week) fits CAND2 at 50/50 trades, −$3,310 vs −$3,330, distance 0.153. The split is partly era-confounded. |
| **E-024** | "[90,180?,3,6,9] = second Solar panel" | **FACT** | Corrected reading: it is the same A-group after the 2025-11-07 retune, bracketed between two dated captures. |
| **E-026** | "the trader's build contains an ACTIVE pullback layer"; "his hard-coded pullback/resume signal layer"; "pullback layer proven" | **INFERENCE** | Nothing in evidence names the layer, and in the recovered core A3/A4 move **T3** far more than T2 — so "pullback" is the wrong name. A cosmetic or abandoned retune is not excluded, so "MUST" is unsupported. |
| **E-030** | "the 2/27 n90 row is likely a ONE-OFF experiment build", no inference marker | **INFERENCE** | Marker added; five rivals kept, including a genuine volatility-triggered tight-risk layer. |
| **E-032** | earlier oscillator-threshold reading of [65,30,75,20,46,36] as MFI / RSI / Stochastic levels | **FACT** | Corrected: they are St-group stop values with legible label initials `In..` / `Tr..` / `I..` / `M..`. |
| **E-035** | "stop 65→75 (11/9 week)" read as a change to the **initial** stop (`OTR_CONVERGENCE_PRESTATE.md` version-timeline anchor) | **INFERENCE** | Exact −1,300.00 caps persist in target weeks *after* 11/14, so row 3 is not row 1. Both members kept; no unique rule forced. |
| **E-036** | "always-on 30-pt trail", carried as part of the stop group | **FALSIFIED** | `OTR_R2_STOPGROUP` G2: an always-on 30-pt trail forces largest loss to ≈−$600 in every week whose target is exactly −$1,300. |

### 1.2 2026 half — VWAP-Flux, account, method (35)

| claim_id | old wording | new status | why |
|---|---|---|---|
| **V-004** | read as "the licensed component is embedded" | **INFERENCE** | Identifies the **parameter surface** at layout level only; embedding is V-013/V-014. |
| **V-005** | "the manual shows 4/80/30" | **FACT** (corrected) | Misread: "4" is a §2.11 example sentence, "80" is a Level:Max value. Close Threshold 70 is universal in public presets. |
| **V-008** | "the tiny thumb proves ~300 hidden rows" | **FALSIFIED** | Arithmetic check against measured thumb fraction. ⚠ **This falsifier is itself contested the same day** by `2026_PANEL_TOPOLOGY.md` §0 — see `FALSIFIED_HYPOTHESES.md` F-04. V-008's status was **not** edited; both readings stand. |
| **V-013** | EV-039 read as establishing reimplementation | **INFERENCE** (NARROWED) | It rules out **one** embedding scenario — a directly-embedded licensed VWAP Flux running in the displayed mode — and nothing else. |
| **V-014** | "custom strategy embedding licensed ninZa VWAP Flux" **and**, later, "own-implementation (H3/H4) now leads" | **UNKNOWN** (REOPENED) | No image, artifact, statement or measurement identifies the engine. H1–H5 each given its own live row (V-015..V-019). Supersedes **both** prior wordings. |
| **V-021** | local-artifact absence cited as evidence about the trader | **FALSIFIED** | Structural: the researcher's machine is not the trader's environment. Recorded as INVALID EVIDENCE; must not be cited for H3/H4 or against H1/H2. |
| **V-022** | "EV-039 proves the trader reimplemented the whole VWAP Flux indicator" | **FALSIFIED** | EV-039's content is exactly one manual sentence about one mode with Tick Replay off. |
| **V-024** | "solved-to-class / ACTIVE incumbent (strong)" — `CONVERGENCE_PASS_ANSWERS_20260824.md` answer I | **UNKNOWN** (REOPENED) | Vendor product-page natural language (V-023) describes per-segment recalculation. Morphology measurements (V-025/026/027) are retained as **evidence for** ACTIVE, not as a class decision. |
| **V-033** | used as a clean rail-formula discriminator | **REPRODUCED + caveat** | The FVP-midspan discriminator was computed under the ANCHOR construction; V-024's reopening **weakens (does not void)** the min-max rejection. |
| **V-035** | "Rails = percentile linear interpolation — **RESOLVED at vendor level without purchase**" | **INFERENCE** | It is an image-geometry inference from EV-040 chart PNGs, and it inherits the V-024 lifecycle caveat. |
| **V-036** | folded into "rails resolved" | **UNKNOWN** (newly isolated) | Whether the *trader's* build uses the vendor formula depends entirely on V-014. |
| **V-037** | `percentile_linear` used throughout as if settled | **UNKNOWN** (newly isolated) | Linear vs nearest-rank was never tested against any observed series; it is an assumption inside the runs, not a finding of them. |
| **V-038** | "FVP = Q50 — RESOLVED (vendor level)" | **INFERENCE** | Three documented, undiscriminated rivals (volume-weighted centre, recency-weighted centre, combined 5-segment VWAP). |
| **V-041** | leader ranking read as an identification | **REPRODUCED + contamination flag** | Ranking retained as a measurement; produced under the V-060 defect. |
| **V-045** | cluster distances read as properties of his system | **REPRODUCED + contamination flag** | Same defect. Naming a cluster is not identifying a system. |
| **V-047** | "R8-A TRUE OOS" / "fully OOS" | **REPRODUCED**, relabelled **HELD_OUT_RECONSTRUCTION_WINDOW** | We had already seen the period's outcomes; the windows were held out from *fitting*, not from *knowledge*. |
| **V-048** | "VF-CAND1 survives TRUE OOS" | **FALSIFIED** | The OOS label itself is invalid for this campaign. The prediction discipline survives; the OOS claim does not. |
| **V-055** | H1a treated as *the* CloseThreshold orientation | **UNKNOWN** | H-MANUAL (=H1c) and H-STRICT (=H1a) are maximally different at T=10, which is exactly why the panel value cannot arbitrate. Both kept. |
| **V-056** | ranking read as evidence of vendor semantics | **REPRODUCED**, demoted to a measurement | It measures **our composite wrapper's** fit, not the vendor filter's definition. |
| **V-057** | "H1a's better fit ⇒ H1a is the vendor's semantics" | **FALSIFIED** | The fit is joint over five layers, all carrying the V-060 defect; the manual's wording is the inverse of H1a. |
| **V-060** | R7/R7b/R8 QtyPerTrend + Split described in `spec.yaml` as signal-level semantics | **FALSIFIED** (known implementation defect) | Code inspection: `run_r7_signal_id.py` increments counters only at line 147 (SAR) and line 154 (flat entry), so the counters gate executed entries, not indicator signals — contrary to V-059. |
| **V-065** | "STOP/RISK: **solved** (130-pt fixed)" — `vendor_forensics/PURCHASE_GATE.md:9` | **INFERENCE** | The −$2,600 row is FACT; that one 130-pt stop produced it rather than any other configuration yielding the same row is an inference from a **two-candidate** test. |
| **V-067** | "the −$2,600 cap is universal across all 2026 builds" | **FALSIFIED** | OTRIMG-0150 shows no −2,600 signature; OTRIMG-0162 shows a short-side −2,820 exceeding the cap. |
| **V-071** | "he did not **use** the zone module" | **INFERENCE** | Downgraded to "did not **expose**" — a `Zone Period` row could sit in the never-labelled head (V-009). |
| **V-084** | prior wording naming specific sleeve carriers for the June TP totals | **UNKNOWN** | No SA slice frame overlaps the 6/7–6/18 TP weeks, so no sleeve subtraction is possible. |
| **V-085** | "H1 (each sleeve qty 1, account gross = sum) is favored" | **UNKNOWN** | A preference is not evidence. H1–H4 all live; TP report filters are themselves unknown. |
| **V-086** | June TP frames treated as live-account evidence | **UNKNOWN** | No account tag is visible; NT8 sim accounts can carry a commission template. |
| **V-090** | "hp weeks are a sibling build" | **UNKNOWN** | Machine tags are readable (E-021, FACT); what they imply about distinct builds is not established. |
| **V-091** | the dev-vs-hp fit read as a "sibling build" conclusion | **REPRODUCED** (measurement only) | The measurement stands; the interpretation moves into V-090's competitor list. |
| **V-097** | "no discretionary layer in his system" | **INFERENCE** | Excludes discretion at **runtime** only. V-098 shows he re-tunes between runs. |
| **V-098** | contemporaneity read as walk-forward purity | **FACT** + explicit non-implication | 58/70 at lag 0 defeats bulk retrospective fabrication; the series is a development log of a live-iterated system. |
| **V-100** | gate EVI downgrade grounded on "his stack is most plausibly his OWN implementation" | **INFERENCE** (conditional) | That ground is itself UNKNOWN under V-014. Under H1/H2 a vendor oracle would answer his build directly and the EVI rises — so the downgrade is **provisional**. |
| **V-102** | vendor-level resolutions used as if they transfer to his build | **INFERENCE** (newly isolated) | The transfer assumption ("he mirrored what the vendor plots showed him") is load-bearing across V-024/V-035/V-038 and has never been tested. |
| **V-103** | bare "parity" used across both halves of the campaign | **FACT** | Inventory: the VF half has **no** IMPLEMENTATION_PARITY at all — Python only, no NinjaScript port, no NT8 cross-check. R6 covers CAND2/Solar only. |
| **V-105** | the 2026 flagship assumed to be one strategy running one VF model | **UNKNOWN** | Never established; the strategy name is never visible in any 2026 frame. Every OTR-VF-CAND1 distance rests on this assumption. |

---

## 2. Terminology relabels applied to immutable run records

Per the run-directory rule, no file under `runs/OTR_*/` was edited. Two relabels are recorded in
`RUN_PROVENANCE.csv` and `MODEL_REGISTRY.yaml` where the source text is now invalid:

| Run | Invalid source text | Correct term |
|---|---|---|
| `OTR_R8_JUNE2026` | Part A "TRUE OOS" (`spec.yaml:11`, `REPORT.md:1,6`) | `HELD_OUT_RECONSTRUCTION_WINDOW` |
| `OTR_R6_NT8_PARITY` | bare "parity" / "bit-exact" (`REPORT.md:9,14,31`) | `IMPLEMENTATION_PARITY` — explicitly **not** ORIGINAL_PARITY |

`TERMINOLOGY_SWEEP.md` proposes one `TERMINOLOGY_ADDENDUM_v4.md` per affected run (7 runs) plus 65
live-doc rewrites (38 SAFE_RENAME, 27 NEEDS_HUMAN_JUDGEMENT). **None of those edits has been
applied.** The sweep is a plan; the live docs still carry the retired vocabulary.

---

## 3. Model-identity changes (from `MODEL_REGISTRY.yaml`)

Not status changes, but changes to **what a name refers to** — which is upstream of every claim
that uses the name. 76 model identities were minted across 13 families to break 11 cases of name
reuse for materially different configurations. The load-bearing ones:

- **"OTR-S-CAND2" named two different D-gates**: registered as `INTEGRATED_X1600_K3_C1000`
  (sensitivity C ∈ {500,1000,1300}) but frozen everywhere afterwards as **C=700 + X2=2500 + cap=20
  + cd=3** — constants that arrived later from the `v_mg` master-gap hunter and were never in the
  registered sensitivity set. Ids: `CAND2_GATE_C1000_COMM418` vs
  `CAND2_GATE_C700_X2_CAP20_CD3_COMM418`.
- **"OTR-S-CAND2" at two commission bases is two different trade streams**: in
  `run_r1j_gatesemantics.py` the commission term feeds the running equity the gate reads, so
  `n=4,598` (comm 2.09/side) and `n=4,592` (comm 0) are different models, not the same model
  differently accounted.
- **"CAND2 era B"** ran at stop 75 in R5 and stop 65 in R6 Layer C / R8; **"CAND2"** exists both
  with and without a protective stop at all.
- **"the VF4 clone"** names a percent-interpolation build in the VF4 spec (PRIMARY) but the
  **QLEV quantile** build in everything carried into R3/R7/R8.
- **"OTR-VF-CAND1" is a 4-member cluster, not a model** — any claim about it must name the member.
- **R10 says "D-gate inherited frozen" but sets `cap=1000`** (`run_r10_fast.py:40`) where the frozen
  gate uses `cap=20`.

---

## 4. What did NOT change

- No run directory, `spec.yaml`, `out/` artifact, `REPORT.md`, screenshot, or falsified hypothesis
  was modified or deleted. `original_screenshot/` was opened read-only.
- No backtest was run; no code under `src/` or `research/**/src/` was touched.
- No FACT was demoted on the strength of an interpretation. Every downgrade above removes an
  interpretive layer and leaves the underlying observation intact and still cited.
- Two provenance gaps are **carried forward unresolved**, not papered over:
  1. **V-023** — the ninZa product-page verbatim strings that reopen V-024 are quoted from the
     owner directive and are **not archived in this repo** (zero grep hits; not in the manual PDF,
     the changelog extraction, or the 2026-01-14 microsite capture). Needs a re-fetch-and-archive
     pass.
  2. **V-018 (H4)** — the supporting detail "code editor visible in OTRIMG-0053-era frames" was
     carried second-hand from `VF_PANEL_COMPLETENESS_NOTE.md §1 H4` and was not verified against
     `IMAGE_MASTER.csv` or the image. (E-019 independently establishes the editor in OTRIMG-0053;
     the "era-frames" plural is the unverified part.)
- **Open reconciliation debt**: `2026_PANEL_TOPOLOGY.md` (written the same day) contradicts V-008
  and undercuts the "sibling build" readings behind V-076 / V-077 / V-090. Its claims have **not**
  been merged into `CLAIM_REGISTRY.csv` and carry no `E-`/`V-` ids yet.
- `CLAIM_REGISTRY.csv` and its four derived documents are **written but not committed**; no
  `spec.yaml` exists for this pass (`research_sdk/prereg_guard.py` governs spec-first commits).

---

## 5. The five most consequential downgrades in this pass

1. **E-010 + E-009 — "OTR-S-CAND2 (verified model class)" / "R6 parity BIT-EXACT" → UNKNOWN +
   IMPLEMENTATION_PARITY.** The campaign's headline claim is gone. R6 compared three artifacts we
   built; ORIGINAL_PARITY has never been tested, because no test anywhere in the campaign has the
   trader as an endpoint. Everything downstream that read as "we matched him" now reads as "we
   matched ourselves, and we are 5.7% / −9.3% away from his aggregates".
2. **E-014 — "42/42 cent-exact ground-truth labels" → CONDITIONAL_LATENT_LABELS (INFERENCE).**
   These were never observed labels: R1e generated *our* trades and solved for which to remove.
   `OTR_R11_INVERSE` then showed six different candidate universes each admit exactly one solution
   on the three testable days. Everything the D-gate rests on (E-017, E-018) inherits that
   conditionality — the gate's "necessity" is necessity **inside our own universe**.
3. **V-060 — QtyPerTrend/Split → FALSIFIED as a known implementation defect.** Our counters gate
   executed entries and SAR flips, not indicator signals. This contaminates **every**
   OTR-VF-CAND1 number — V-041, V-045, V-047, V-049, V-050, V-052, V-056 — including the
   held-out-window result that was the strongest thing the VF half had. The cluster's rank ordering
   must be re-derived before any of it is a claim about the trader.
4. **V-014 — the 2026 engine → UNKNOWN, REOPENED with five live hypotheses.** This single row
   supersedes both prior campaign positions ("embedded licensed VWAP Flux" and "own implementation
   H3/H4 leads"). It drags V-036, V-100 and V-102 open with it: the rail formula's transfer, the
   purchase-gate EVI downgrade, and the whole vendor→trader transfer assumption are all now
   conditional on a question with no evidence on either side.
5. **V-024 — VWAP layer lifecycle → UNKNOWN, REOPENED.** "Solved-to-class / ACTIVE incumbent
   (strong)" is withdrawn; ACTIVE-ANCHOR and SEGMENT/BLOCK are both live. It is the most fragile
   reopening in the set, because the evidence that reopened it (V-023, vendor product-page
   language) is the one FACT row in the registry with **no repo-archived source**.

*Honourable mentions*: **V-048** (the "TRUE OOS" label FALSIFIED outright — the correct term is
HELD_OUT_RECONSTRUCTION_WINDOW), and **E-026** (the "active pullback layer" → INFERENCE, with
"pullback" removed as a name because A3/A4 move T3, not T2).
