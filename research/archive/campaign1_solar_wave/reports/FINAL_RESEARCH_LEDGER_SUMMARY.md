# FINAL RESEARCH LEDGER SUMMARY — trial accounting, falsifications, and open unknowns

_DRAFT 2026-08-07 · branch `post_campaign_audit`. Counting rule: R1
(`research/registry/TRIAL_ACCOUNTING_RULE.md`) — a configuration counts as a trial when its P&L
is inspected; slip/cost re-runs of an inspected config do not re-count. The campaign block's
count is a disclosed bracket, never a single number
(`research/audit/REGISTRY_GAP_ASSESSMENT.md` (b))._

## 1. Trial accounting by block

| block | seq | R1 trials | preregistration status |
|---|---|---:|---|
| Campaign Phase 0–Wave 1b (PARITY, SW00–SW02a, W1, W1b) | 1–90 (+ seq-0 instrumentation) | 90 | **Contemporaneous**: registry rows + `runs/<id>/spec.yaml` through `RE01_open_parity`; H-001…H-005 commit-verifiably preregistered |
| Campaign Waves 1c–3 (plateaus, H-006…H-014, ES, C2/C4, wavecond) | 91–229 | 139 | **Backfilled 2026-08-07** (`tested_configs_backfill.csv`, 296 ledgers, `reconstructed=yes`). Criteria not provably fixed in advance, except: H-006/H-007 hypotheses (1h49m commit lead) and H-014 criteria-level (4h25m lead — "the campaign's only clean significance result", with exactly that qualifier). Reviewer discount applies; the discount asymmetry favors the record (nearly all verdicts were negative) |
| **Campaign total** | 1–229 | **229** (honest bracket **229–383** counting every seq-assigned ledger; best consistent strict relabel **295–335** — the backfill collapsed five swept axes and mislabeled rule variants as slip stress, disclosed row-by-row in `reconstructed_trials.csv`) | Downstream-insensitive: Harvey–Liu haircut Sharpe 0.000 at every point of the bracket; DSR keys on N_eff (5 clusters / participation ratio ≈ 7), not raw N |
| POST_CAMPAIGN_AUDIT_01 | — | **0** | Fully preregistered (`counts_as_trial: no` in every audit spec); reproductions/stresses/instrumentation only; E10 designation recorded as a design-choice event with committed sensitivity, not a trial |
| Wave B01 (Family B) | 230–232 | **3** (of ≤12 budget) | **Fully preregistered**: wave spec `a5f6ef3`, per-arm driver commits before result reads (`20b7612`/`a407e58`/`9ccbfe9`), frozen DR-05 constants, gates fixed before any P&L. B01a = seq 0 instrumentation (no trial) |
| PORTABILITY-01 (YM/RTY/CL) | 233–271 | **39** (13 cells × 3 instruments; 3 preregistered family reads) | **Fully preregistered** at `b139cbb`: instruments thesis-preselected, identical grid, pass rule ≥2/3, no-rescue clause honored |
| DM01 day-margin variant | 272–284 | **13 operational configs** (descriptive measurement, not an alpha axis; disclosed in ledger) | **Preregistered** at `b9e7686` (single policy arm D — reconfirmation — chosen ex ante; immediate-restore arms explicitly not run). **IN FLIGHT at draft time**; report `reports/DAY_MARGIN_VARIANT.md` owed by the controller |
| **Grand totals** | 1–284 | **271 R1 trials** (arithmetic: 229+3+39; strict-relabel bracket 337–377) **+ 13 operational** | Registry lag disclosed: rows for 233–284 are spec-declared but not yet appended to `tested_configs.csv` (`reports/FINAL_EVIDENCE_MAP.md`) |

## 2. What was tried and rejected (the complete falsification ledger, compact)

Campaign (each with committed evidence; none deleted — `research/registry/rejected_ideas.md`,
`research/CAMPAIGN_STATE.md` §6/§9, `reports/final_system_design.md` §5, `registry/hypotheses.md`):

1. Single-parameter selection in any form — PBO 0.48–0.90, negative IS→OOS slope everywhere;
   walk-forward argmax $16,131 vs median-config $121,373.
2. 16:30 timed-exit dominance — FALSE (wins 4/28 matched pairs, median −$12,476).
3. The 46% untaken Type-1 signals as an opportunity set — FALSE (−$9.04/marginal trade, 54,151
   trades).
4. H-011 resting stop orders at the ladder — FALSE (negative 10/10 cells, −$1.88M); with H-008
   mode-1, establishes the close-basis crossing excess (89% of all friction) is NOT recoverable.
5. H-007 / DR03-H1 split exit ≠ reversal distance — FALSE (monotone degradation; no-split best
   everywhere).
6. H-008 raw High/Low anchor — FALSE (Sharpe 0.527); close-confirmed HL passes standalone but is
   redundant with H-006 (combo 1.011 vs 1.010).
7. C4 adding Type-2 — FALSE (−0.33 Sharpe).
8. C2 Type-3 re-entry sleeve — REJECTED on the interaction test (−0.402 Sharpe on the adaptive
   core, P = 0.879) despite the campaign's best point estimates.
9. Wave-index conditioning — FALSE (non-monotone 0.54–0.93 across MinWave 1–8; screen effect died
   in the engine).
10. Price-proportional threshold — FALSE (Sharpe 0.250; significantly worse than plain fixed
    ticks, p = 0.999) — the control that CONFIRMED H-006's volatility mechanism (+0.728, p = 0.009).
11. DR06-H5 (iid understates tail risk) — FALSE (block/iid DD ratio 0.987).
12. Original SW05 chop veto — INVERTED (would delete 74% of profit).
13. H-006 "adaptive beats fixed" — INCONCLUSIVE after fair scoring (+0.087, P = 0.358); resolved
    only by execution economics in the audit.
14. DSR as a promotion criterion — ABANDONED under the preregistered rule (0.45–0.55 vs 0.90 bar;
    Harvey–Liu 0.000; judgement-dominated in either direction).
15. ES portability — FAIL (−$12,455, Sharpe −0.329, P(Sharpe ≤ 0) = 0.829).
16. Thesis-§14 seed rejections (never opened): unrestricted A1–A5 optimization, MA alignment
    gates, fixed profit targets, immediate breakeven, optimized minute windows, treating
    1m/2m/3m/5m as independent strategies, tuning to the vendor's screenshots.

Post-audit:

17. Family B, all preregistered high-value arms — **FALSIFIED** (Wave B01): DR05-H1(b)
    failed-flip conditioning (diff −2.0 vs ≤ −10, p = 0.171); DR05-H2 dead unbuilt by the frozen
    gate; B01c ORB-failure fade −$22,534 slip-1 (negative even slip-0); B01d dead by dependency;
    B01e gap-fade null REJECTED its null but the B02 escalation FAILED 3/6 gates (top-1% = 90.1%
    of net, stopless −$8,544 left tail, 52.7% months positive). Axes CLOSED; re-tests require
    genuinely new hypotheses, not re-tuned constants.
18. External portability, three more markets — **FAIL 0/3** (YM −$21,947, RTY −$17,006,
    CL −$12,218; CL 0/13 cells positive). Family verdict: 0-for-4 external, NQ-SPECIFIC.
19. R4 as an executable — REJECTED (every discrete variant fails the Sharpe gate by 0.17–0.24);
    R5 discrete alternates E13/E20/E3 — published with FAIL verdicts.

Recorded as not-run, not failures: H-013 ensemble weighting (1/N stands on preregistered
complexity grounds), C3/C5/C6 (no mechanism remained after C4/wavecond died), Playback parity
(nil information for market-only orders).

## 3. What remains genuinely unknown

1. **Tick-level intraday drawdown.** Best committed bound: bar-level TRUE_MTM −$42,204.42 (R5
   theoretical) / −$41,252.20 daily-sampled (E10) — 3-minute bar-close marking bounds the true
   excursion from below by an unmeasured margin. (E10's own bar-level DD was never separately
   published.)
2. **Live slippage.** 1 tick/execution is an assumption (external retail evidence 0.7–1.2 ticks
   RTH); 2-tick stress retains 87.4%, slip-3 ≈ 75% floor. No live or Playback evidence exists,
   by design.
3. **Forward behavior.** Zero forward, paper, sim, or shadow sessions exist. Nothing is known
   about the system after 2026-07-31, and the monitoring statistic (quarterly overshoot ratio r)
   is defined but has produced no forward readings.
4. **F04/F05/F07/F08** (overnight-range failure, prior-day-range failure, balanced-value
   reversion, session handoff) — untested; deprioritized below PORTABILITY-01 because they
   inherit negative evidence from B01a/B01c, not because they were run.
5. **The ML program was never run** — per the roadmap ordering (ML overlays only after
   interpretable-state research matures, constitution §17), and justified twice over: no second
   family exists to diversify what ML would overlay, and the campaign's own sample-size verdict
   (nothing comparative is separable from noise on 4.6 years of one instrument) applies a
   fortiori to higher-variance learners.
6. **A validated master-strategy implementation** of the E10 layer (the champion is certified as
   an audited simulation over exactly-reproduced ledgers, not as a compiled strategy).
7. **ccHL under audit-grade scrutiny** (INCONCLUSIVE — NOT RE-AUDITED; campaign numbers only).
8. **DM01's answer** (in flight): the opportunity cost of the 16:45 ET day-margin cutoff.
9. **Whether history erasure of the vendor blob will be executed** (HUMAN ACTION pending;
   governance, not research).

## 4. The one-line ledger

271 R1 trials (bracket-honest: campaign 229–383, strict 295–335, plus 42 fully preregistered
post-audit) + 13 operational configs bought: one exactly-recovered indicator, one NQ-specific
tail-concentrated historical edge held as an unselected 13-member ensemble with a costed
executable form, four external-market falsifications, one falsified complementary family, and a
complete, append-only record of everything that failed. **Every absolute-edge test passed; every
comparative test failed** — the deliverable is the region, the ensemble, and the ledger itself.
