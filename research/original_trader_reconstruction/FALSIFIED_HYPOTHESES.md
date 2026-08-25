# FALSIFIED_HYPOTHESES — OTR campaign #6

**This file is a permanent record. It must never shrink.**
Nothing here may be deleted, merged away, or quietly reworded. A falsified hypothesis stays with
its falsifier forever, including when we later decide the falsifier itself was wrong — in that case
**both** are recorded (see F-04, which is currently contested).

**Authority**: `CLAIM_REGISTRY.csv` (141 rows, 2026-08-24). Section 1 holds the 11 rows whose
registry status is `FALSIFIED`. Sections 2 and 3 hold falsifications that exist in run records and
registry annotations but have not yet been minted as claim rows — they are listed so a future pass
can give them ids, not so they can be forgotten.

---

## Section 1 — Registry rows with status FALSIFIED (11)

### F-01 · E-027 — "The hp build = pure T2 (pullback-qualified) entries"
- **Ruled out**: pure-T2-only entry as a **complete** model of the hp-machine weekly reports.
- **Falsifying run**: `runs/OTR_R9_HP_BUILD` (`run_r9_hp.py`), preregistered discriminator **D4**
  including a dev-machine control.
- **The numbers that fired it**: dev weeks fit the T1 control at distance 0.284 versus 0.409 /
  0.413 for the two T2 modes; hp overall distances are T1 0.421 ≤ T2L 0.435 < T2E 0.495. The T1
  control beats both T2 modes on dev weeks and is not beaten on hp weeks.
- **What survives, explicitly**: partial pullback qualification. T2L cuts hp overtrade from +39.5%
  to +23.8%; T2E swings the two +$18.5k hp trend weeks by +8.5k and +17.9k toward target with
  larger average wins.
- **Still live, deliberately left unregistered**: a state-switching hybrid (T1 chains in chop,
  pullback-priced entries in trend); a suppression layer unrelated to pullbacks; a different
  strategy posted from hp.

### F-02 · E-031 — "The Feb-2025 fast build is a TrendVector-cycle machine (T1 entry + TV-cross exit + T2 re-entry)"
- **Ruled out**: the `F_TV2{E,L}` TrendVector-cycle family as the producer of the 2025-02-27 row.
- **Falsifying run**: `runs/OTR_R10_FEB2025_FAST` (`run_r10_fast.py`), members `F_TV2{E,L}` ×
  `LL{none,2500}` against the `F_T1` control. Decisive discriminator: the 2/27 count.
- **The numbers that fired it**: on 2/27 every TV-cycle member produced 26–31 trades (T1 control
  22) against a target of **90**, while the same members exploded on the wrong days (3/12-14: 145
  vs target 60; 3/4-5: 130 vs 70); holds 8–18 min against a target of 20–45; |n err| 50–112% versus
  the control's 43%. A literal LossLimit-2500 halt reduced counts without fixing the pattern.
- **Kept alive as separate open questions**: an armed-latch close-basis T2 layer; the June-2026 fast
  sleeve (independent).

### F-03 · E-036 — "Tr = 30 is an always-on 30-point trailing stop"
- **Ruled out**: an always-on 30-point trail anywhere in the 2025 St-group.
- **Falsifying run**: `runs/OTR_R2_STOPGROUP`, cell **G2** (`run_r2.py`).
- **The number that fired it**: an always-on 30-pt trail forces the simulated largest loss to
  ≈−$600 in **every** week whose target largest loss is exactly −$1,300.00 — contradicting every
  −1,300 week.
- **What survives**: **G3**, a trail armed after +20 points (row 4, M=20), remains viable and
  untested against a discriminator; the trail may exist but be wider than 30 points; row 2 may not
  be a trail at all.

### F-04 · V-008 — "Hidden-row COUNTS can be estimated from scrollbar thumb size" ⚠ **CONTESTED**
- **Ruled out (as recorded 2026-08-24)**: deriving hidden-row counts from thumb size. Falsifier:
  an arithmetic check — a 24–28-row viewport with 10–30 hidden rows implies a 45–70% thumb, but
  measured thumbs are 7–17%, so the NT8/WPF skin was read as rendering a near-minimum thumb.
  Source: `screenshot_forensics/VF_PANEL_COMPLETENESS_NOTE.md` §0 Q1b consequence 2. Effect: kills
  any "the tiny thumb proves ~300 hidden rows" reading.
- ⚠ **The falsifier is itself now contested, same day.**
  `vwap_flux_family/2026_PANEL_TOPOLOGY.md` §0 (2026-08-24) reports measured thumb heights of
  **35–251 px** across the 22 2026 panel frames — far above any WPF minimum — varying smoothly and
  monotonically with capture date, and reports that the proportional model reproduces the
  independently countable 26-row NT8 standard tail in **17 frames** with a **constant +3 to +5 row**
  bias (not a multiplicative one; error does not grow as extent goes 77 → 543 rows).
- **Status of the object right now: OPEN.** Both the falsification and its counter-measurement are
  retained verbatim. Neither has been withdrawn, and V-008's registry status has **not** been
  edited in this pass. Reconciling them requires a claim-registry pass over the topology document.

### F-05 · V-021 — "The absence of vendor artifacts on OUR research machine is evidence about what the ORIGINAL TRADER owned or ran"
- **Ruled out**: the inference itself. **Recorded as INVALID EVIDENCE.**
- **Falsifier (structural, adjudicated by owner under directive v4.0)**: the researcher's machine is
  not the trader's environment; the two populations are unrelated.
- **Binding consequence**: `vendor_forensics/LOCAL_ARTIFACT_SEARCH_20260824.md` §3 **must not be
  cited** in support of H3/H4 or against H1/H2 (V-015..V-018).
- **What survives**: V-020 (FACT) — the search happened and found nothing on **our** machine, which
  establishes only that no local oracle path exists short of purchase.

### F-06 · V-022 — "EV-039 proves the trader reimplemented the whole VWAP Flux indicator"
- **Ruled out**: the over-claim. Adjudicated by owner under directive v4.0.
- **Falsifier**: EV-039's content is **exactly V-011** — one sentence about one mode with Tick
  Replay off. It has no reach over the other four engine hypotheses.
- **Supersedes**: the `CURRENT_TRUTH.md` wording "own-implementation (H3/H4) now leads" **and** the
  earlier "custom wrapper on licensed VWAP Flux".
- **What survives**: V-013 (INFERENCE) — one embedding scenario is ruled out, nothing more.

### F-07 · V-048 — "The June-July 2026 window constitutes a true out-of-sample / 'fully OOS' test"
- **Ruled out**: the terminology, for this campaign, permanently.
- **Falsifier (structural, adjudicated by owner under directive v4.0)**: we had already seen the
  historical outcomes for this period before designing the members. The window is held out from
  **fitting**, not from **knowledge**.
- **Correct term everywhere**: `HELD_OUT_RECONSTRUCTION_WINDOW`.
- **What survives**: V-047 (REPRODUCED). The prediction discipline — frozen cluster, band committed
  before readout, zero knobs touched — still counts. The OOS claim does not.
- **Historical run text that carries the invalid wording** (immutable; addenda only):
  `runs/OTR_R8_JUNE2026/spec.yaml:11`, `runs/OTR_R8_JUNE2026/REPORT.md:1,6`,
  `runs/OTR_R5_CAND2_WEEKLY_VALIDATION/WEEKLY_VALIDATION_REPORT.md:20`.

### F-08 · V-057 — "H1a's better backtest fit is evidence that H1a is the vendor's CloseThreshold semantics"
- **Ruled out**: the inference from fit to semantics. Adjudicated by owner under directive v4.0.
- **Falsifier**: the fit is **joint** over trend construction, pullback depth, confirmation,
  orientation and exit, all carrying the V-060 defect; a better joint fit can be produced by a
  wrong orientation compensating elsewhere. The manual's own wording is the **inverse** of H1a.
- **What survives**: V-056 (REPRODUCED) stays as a measurement of our composite wrapper's fit, and
  must never be promoted to a semantics claim. V-055 keeps both orientations alive.

### F-09 · V-058 — "H1b: require the signal candle to close in the extreme 10% AGAINST the signal direction"
- **Ruled out**: the H1b orientation.
- **Falsifying run**: `runs/OTR_R7_VF_SIGNAL_ID` pass 1, verdict 1.
- **The result that fired it**: degenerate — near-zero trades across the grid; bottom of the ranking
  table.
- Kept with its falsifier per directive.

### F-10 · V-060 — "Our R7 / R7b / R8 implementation of QtyPerTrend and Split implements the vendor's signal-level semantics"
- **Ruled out**: our implementation, as a **KNOWN IMPLEMENTATION DEFECT**. Adjudicated by owner
  under directive v4.0 and confirmed in code.
- **Falsifier (fired, by code inspection)**: in `vwap_flux_family/src/run_r7_signal_id.py` the
  counters `cnt[sig]` / `last_sig[sig]` are incremented **only** at the SAR branch (line 147) and
  the flat-entry branch (line 154). A signal that fires while a position is open and is not acted
  on therefore neither consumes the per-trend quota nor sets the split clock. The counters gate
  **executed entries and SAR flips**, not indicator signals — conflating strategy execution with
  Signal_Trade generation, contrary to V-059 (FACT, vendor manual §2.11/§2.13).
  `runs/OTR_R7_VF_SIGNAL_ID/spec.yaml` claims signal-level semantics.
- **SCOPE OF CONTAMINATION — every one of these was produced under the defect**: V-045, V-047,
  V-049, V-050, V-052, V-056, and V-041's ranking. The OTR-VF-CAND1 cluster's rank ordering and its
  distances **must be re-derived** before any of them is treated as a property of the trader's
  system. V-061 is additionally blocked behind this.

### F-11 · V-067 — "The −$2,600 cap is universal across all 2026 builds"
- **Ruled out**: universality.
- **Falsifier (fired, image evidence)**: `OTRIMG-0150` (week 5/31-6/5) shows largest loss −1,890
  all/long and −1,790 short, with **no** −2,600 signature; `OTRIMG-0162` shows a short-side largest
  loss of **−2,820**, exceeding the cap.
- **Both readings kept**: the −2,820 is consistent with a gap-through beyond 130 pts; the −1,890
  week indicates a different (or absent) fixed stop.
- **What survives**: V-062 (FACT — 18 weekly reports do carry exactly −2,600) and V-063
  (REPRODUCED — a 130-pt intrabar stop reproduces those tails).

---

## Section 2 — Falsifications recorded in run outputs, not yet minted as registry rows

These are real, dated falsifications held in `RUN_PROVENANCE.csv` and the run reports. They have no
`E-`/`V-` id yet. **Listed here so the permanent record is complete; a future registry pass should
give each one an id rather than re-deriving it.**

| # | Falsified reading | Falsifying run | What exactly was ruled out |
|---|---|---|---|
| S-01 | RTH-only trading window for the early build | `OTR_S3_SELTIME` | RTH-only is **arithmetically** falsified against the observed avg-trades-per-day and in-market time |
| S-02 | Strict-cross flip-only exit (X1) as an improvement over the inclusive touch exit (X0) | `OTR_S4_EXITS` | hold 75.4 (strict-cross) vs 74.9 (touch) — no frontier move; recorded as non-improving mechanism pass #1 |
| S-03 | 04:00–16:00 SelTime window; T3 entry participation; first-bar-breakout as a **global** gate | `OTR_R1_SERIES` | three separate readings falsified inside one run series |
| S-04 | Literal D/M halts (M2000 / D4500) as part of the **dev** build | `OTR_R5_CAND2_WEEKLY_VALIDATION` | adding them moves dev error from +6.6% to −27.6% — rejected for the dev build |
| S-05 | 65-pt stop × 2 entries as the producer of the −$2,600 row | `OTR_R3_VF2026` | only a **single-lot 130-pt** stop can make a −$2,600 trade ROW (row-value discriminator) |
| S-06 | `LossLimit 2500` evaluated at bar close with next-open fill, as the 2026 risk mechanism | `OTR_VF1_FLUX_ARCH`, `OTR_VF2_STOP130` | produces −2,785 / −3,190 tails, inconsistent with the exact −2,600 evidence |
| S-07 | The segmented / frozen-staircase VWAP layer architecture | `OTR_VF1_FLUX_ARCH` → rejected by `OTR_VF4_ANCHORED_LAYERS` | rejected **on image evidence**, i.e. plot fidelity, not PnL. ⚠ Note the tension with V-024's reopening: the vendor product-page language (V-023) again describes segments |
| S-08 | The running intra-hour percentile ladder as the 2026 mechanism | `OTR_V1_PROXY` | holds 2–15 min against a 39.8 min target; all 12 cells FAIL, best D=5.203 (a degenerate scalper cell) |
| S-09 | Hourly-EMA20 trend reading on the V2 geometry winner | `OTR_V3_PROXY_FINAL` | falsified within the pass |
| S-10 | 2026 weeks as Family-S | `OTR_S8_CROSSWINDOW` | falsified **under the frozen S candidate only** (2× counts, half holds). A different S-family member is **not** excluded — `final/FINAL_PACKAGE.md:54` currently over-states this as "proven non-Family-S" |
| S-11 | A **removal-only** subset-diff solver as a global explanation of the Jan-2023 daily table | `OTR_R11_INVERSE` (OPEN, pre-spec diagnostic) | CAND2 produces **fewer** trades than target on 2023-01-13 and 2023-01-17 (4 vs 6), so no removal from our candidate stream can reach those rows. This is the formal reason to widen the event universe |
| S-12 | The "thumb size is untrustworthy" reading (see F-04) | `vwap_flux_family/2026_PANEL_TOPOLOGY.md` §0 | contested falsification of a falsifier — recorded at F-04, repeated here so neither direction is lost |

**Non-falsification recorded for completeness**: `OTR_S5_REENTRY_QUALITY` returned **VACUOUS** — a
self-declared spec-design error in which both gates are tautologies on T3 bars, 0 entries filtered,
results bit-identical to baseline. It does **not** count as a mechanism pass and must not be cited
as evidence in either direction.

---

## Section 3 — Superseded readings named inside registry rows

Prior readings that were falsified or corrected earlier and are carried in the `supersedes` /
`notes` fields of surviving rows. Recorded here so they cannot be re-proposed as if new.

| Superseded reading | Where it lived | Corrected by | What it got wrong |
|---|---|---|---|
| `[65,30,75,20,46,36]` read as MFI / RSI / Stochastic oscillator thresholds | earlier St-group analysis | E-032 (FACT), corrected in `CURRENT_TRUTH.md` 2026-08-24e | they are stop-group values with legible label initials `In..` / `Tr..` / `I..` / `M..` |
| `[90,180?,3,6,9]` read as a **second Solar panel** | earlier parameter-timeline reading | E-024 (FACT) | it is the same A-group after the 2025-11-07 retune |
| "the manual shows 4/80/30" as a vendor preset | earlier internal VF reading | V-005 (FACT) | "4" is a §2.11 example sentence and "80" is a Level:Max value; Close Threshold 70 is universal in public presets |
| "stop 65→75 (11/9 week)" read as a change to the **initial** stop | `OTR_CONVERGENCE_PRESTATE.md` version-timeline anchor | E-035 (INFERENCE) | exact −1,300 caps persist after 11/14, so row 3 is not row 1 |
| Scrollbar-thumb **position** conflated with thumb **size** | `VF_PANEL_COMPLETENESS_NOTE.md` §0 Q1b | V-007 (FACT, position) vs V-008/F-04 (size, contested) | position is used coherently; size is the disputed quantity |

---

## Cross-check

| Source | Count |
|---|---|
| Registry rows with status FALSIFIED | 11 (F-01 … F-11) |
| Run-recorded falsifications without an id | 12 (S-01 … S-12) |
| Superseded readings named in surviving rows | 5 |

The 11 registry rows are E-027, E-031, E-036, V-008, V-021, V-022, V-048, V-057, V-058, V-060,
V-067. Any future edit that reduces this list below 11 is a defect.
