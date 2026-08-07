# Second red team — POST_CAMPAIGN_AUDIT_01

_2026-08-07. Four independent adversarial agents (reproduction-integrity,
simulation-correctness, statistical-claims, process/governance lenses) attacked
the audit's findings with their own code; the controller then adjudicated and
remediated. The reviewers did not produce any result they reviewed._

## 1. What the attack CONFIRMED (independent recomputation, all exact)

- **V3 B-arm reproduction**: reviewers re-diffed cells themselves — 0 mismatches
  (vm6: 16,984 fills; vm30: 1,786); h006 vm30 net recomputed from raw fills to the
  cent ($249,256.52).
- **V4 C-arm reproduction**: a reviewer independently diffed **all 13** C-arm
  ledgers vs committed v4verify: 13/13 EXACT. The StartUp confound is "proven, not
  asserted"; alternative explanations (data revision, engine change) REFUTED —
  they cannot produce 13/13 exactness while flipping only the seed direction.
- **Preregistration chronology**: every spec commit precedes its run's first
  ledger write (git times vs engine timestamps); no spec amended after commit.
- **No tampering**: `git diff research-campaign..post_campaign_audit` over all
  campaign evidence directories is empty.
- **MTM numbers**: R5 session Sharpe 1.0642 / calendar 1.0104 / bar-level DD
  −$42,204.42 / flat-at-close identity at 0.000000 for all 13 members — all
  reproduced exactly by a reviewer's independent rerun.
- **V3/V4 ensemble stats**: corr 0.9952, ΔSharpe +0.0189, bootstrap P = 0.3275
  seed-exact; reviewer-computed 95% CI for ΔSharpe [−0.064, +0.094] (supports
  PERFORMANCE_SIMILAR_ONLY).
- **Slip-2**: 87.39% retention confirmed; paths verified fill-timestamp-identical
  in 13/13 cells (stronger than the committed TradesCount check).
- **Registry recount**: 229 R1 trials reproduce exactly under independent recount
  (zero seq gaps); the strict-relabel arithmetic (295/335) is internally
  consistent and disclosed in three surfaces.
- **E10 arithmetic**: top-10 retention 0.9863, theoretical commission $11,452.71,
  gate table — all check out.
- **Governance**: repo PRIVATE re-verified; `SolarWaveRK/` untracked at local
  HEAD; no vendor path added by any audit commit; no EXPLICIT NON-RUNS item
  executed.

## 2. Findings and remediation (all applied same-day; none overturns a verdict)

| sev | finding | remediation |
|---|---|---|
| MAJOR | C-arm 13/13 EXACT claim had **no committed certificate**, and `v4_reproduction_diff.csv` actually held the B-arm-vs-v4verify comparison — readable as a FAILED reproduction | `v4c_reproduction_diff.csv` (C-arm certificate) committed; old file renamed `v4_startup_confound_diff.csv` with the rename disclosed in V3_V4_VERDICT.md; C-arm `sweep_summary.json` added |
| MAJOR | **All audit rerun ledgers were untracked** — EXACT verdicts unverifiable from a clone | all 72 evidence files (ledgers, bar exports, gate payloads) SHA-256-manifested in `audit_evidence_hashes.json` and committed with the ledgers |
| MAJOR | **E10 pass (margin 0.003) rested on unpreregistered micro-choices** (round vs floor, daily basis) and a 3-discretization menu; promised disclosure doc didn't exist yet | sensitivity computed and committed (`e10_sensitivity.csv`): round AND floor pass on BOTH session and calendar bases (margins 0.003–0.012); only cost-maximizing ceil fails. E-variant daily vectors committed (`e_variant_daily_vectors.csv`). The E10 designation is hereby recorded as a **design-choice event**: menu {E13, E10, E20} evaluated, E10 designated as the direct reading of the thesis prescription (target-then-round); alternates published with FAIL verdicts. Headline reworded to state the margin |
| MAJOR | Slip-2 "falsification" **misattributed the source claim**: the measured "halves" language came from WAVE1C 3-minute plateau cells (partially supported by vm6, 51.6%), the 1-minute table showed 63–78% retention; only the unmeasured extension to R5 in the final design package is falsified | FILL_AND_TAIL_AUDIT.md §1 rescoped precisely |
| MINOR | Vendor containment is **local-only**: `origin/research-campaign` tip still tracks the DLL | disclosed in VENDOR_BINARY_REMEDIATION.md §3b; branch push mitigates for the audit tip; `research-campaign` remediation added to HUMAN ACTION list |
| MINOR | Promised `final_system_design.md` §7 StartUp correction was not applied | applied (StartUp: false annotation) |
| MINOR | Gate basis not preregistered; E10 daily vectors uncommitted | vectors committed; gate now reported on both bases (passes both); future gates must preregister the basis (rule recorded in roadmap) |
| MINOR | "10–49%" member-move phrasing overstated (6/13 move ≤3.3%); "~5–6%" basis gap wrong for R4 (3.6%); R4 TUW 1113 typo (1110); "$1,770.52" unsourced ($1,770.00 from fills); "23%" fill coverage understated (32%) | all corrected in place |
| NOTE | Bar-close marking bounds true intraday DD from below | disclosed in MTM_RECONCILIATION.md |
| NOTE | Slip-3 linear extrapolation ignores the slippage cap (it is a floor on retention) | disclosed in FILL_AND_TAIL_AUDIT.md |
| NOTE | POST_AUDIT_TRANSITION consumed at machine speed during the review; its "compare against BOTH executable R4 and R5" requirement conflicts with the finding that executable R4 fails its gates | adjudication: the constitution mandates automatic transition without user confirmation; the comparator contradiction is resolved by B01_WAVE_SPEC's already-preregistered reading — executable R5-E10 primary, **theoretical** R4 secondary (its best cost-feasible research form). Flagged for the owner's attention in NEXT_HANDOFF.md rather than blocking the wave |

## 3. Design-choice ledger (selection-risk accounting, per reviewer demand)

Non-preregistered choices made by the audit, each with its committed sensitivity:

1. **E10 designation** among {E13, E10, E20} — sensitivity: all published; E13
   fails by 0.016 (pure commission), E20 by 0.029; verdict direction unchanged
   under round/floor × session/calendar (4/4 pass).
2. **Session basis for gate evaluation** — calendar basis passes by MORE
   (−0.088 vs −0.097); choice immaterial.
3. **B/C-arm StartUp correction after seeing A/B failures** — config
   identification, not tuning; each arm's spec disclosed the chain before running.
4. **High-res cells {6,18,30}** — chosen as narrowest/middle/widest before
   results; 32% fill coverage.

None of these creates an R1 trial (no new parameter set's P&L was inspected for
selection); the executable variants are implementations of one frozen signal set.

## 4. Standing dissent items (not remediable by wording)

- The E10 pass margin **is** thin (0.003–0.012 across passing combinations). If
  the MNQ fee schedule worsens by ≥$0.10/side, E10 fails the gate. Monitoring
  hook: re-verify MNQ commission whenever the broker plan changes.
- The audit's preregistration lead times are minutes, not days — procedurally
  clean but epistemically thin for anything other than reproduction runs (where
  expectations are the already-committed campaign ledgers, which is the case
  here).
- Tick-level intraday excursion remains unmeasured (3-minute bar-close bound).

## 5. Verdict on the audit

All four reviewers: **no finding overturns any audit verdict.** The reproduction,
MTM, fill, registry, and executable conclusions stand as remediated above.
POST_CAMPAIGN_AUDIT_01 = **PASS**, with the E10 headline carrying its margin
disclosure permanently.
