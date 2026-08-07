# FINAL EVIDENCE MAP — claim → commit/artifact chains, through the post-audit waves

_DRAFT 2026-08-07 · branch `post_campaign_audit`. This document EXTENDS
`research/audit/AUDIT_EVIDENCE_MAP.md` (claims 1–17, audit era — not duplicated here; that file
remains authoritative for them). Chronology guarantee carried forward: every post-audit run spec
and driver is committed in a parent commit of the commit that first contains its results
(verify: `git log --oneline --follow -- <path>`)._

## Audit-era claims (1–17)

See `research/audit/AUDIT_EVIDENCE_MAP.md`. Notables inherited by the final package: R5
EXACT_REPRODUCTION (claim 4), StartUp recipe defect (5), V3/V4 verdict (6–7), TRUE_MTM identity
and bar-level DD (9–10), MNQ $0.65/side (11), E10 gates (12), slip-2 87.4% (13), no fill
artifact (14), registry bracket 229–383 / strict 295–335 (15), zero audit R1 trials (16),
SHA-256 evidence manifests (16b), day-margin facts (17).

## Post-audit waves (18–27)

| # | Claim | Evidence chain |
|---|---|---|
| 18 | Wave B01 preregistered before any result: arms, frozen constants (DR-05), gates, ≤12-trial budget, Family-A comparators (executable R5-E10 primary, theoretical R4 secondary) | `a5f6ef3` → `research/04_complementary_family/B01_WAVE_SPEC.md`; data export preregistered at `647b996` → `runs/B01A_BARS_1M/spec.yaml` (1,620,044 one-minute closes) |
| 19 | **B01a / DR05-H1: arm (a) PASS** (yearly mean overshoot 204.7–217.9 ticks, in band [89.5, 268.5] all five years 2022–2026 — the scaling-law unit transfers), **arm (b) FAIL** (failed-flip continuation diff −2.0 ticks vs ≤ −10 required; 3/5 years vs ≥4; Mann-Whitney p = 0.171 vs < 0.05) ⇒ DR05-H2 dead unbuilt | driver `20b7612` → `src/analytics/b01a_h1.py` (constants frozen in `research/deep_research/DR-05.md`) → results `879846c` → `research/04_complementary_family/b01a_h1_report.md` + `b01a_h1_ledger.csv.gz` (19,311 DC segments, θ=179); registry: `research/registry/hypotheses.md` DR05-H1 entry (seq 0, instrumentation — no R1 trial) |
| 20 | **B01c / DR05-H3 FAIL (seq 230)**: ORB-failure + reacceptance fade net −$22,534 slip-1 (PF 0.839, avg −$66.08), −$19,124 at slip-0, 2/5 positive years — fails gate 1 (net > 0); 1,037 events, 696 vetoed by the frozen Solar-alignment veto (67%), 341 traded; B01d dies by dependency | prereg + driver `a407e58` → `src/analytics/b01c_orb.py` → results `81f03b6` → `research/04_complementary_family/b01c_event_census.csv`, `b01c_trades_slip1.csv`; registry row seq 230 (`research/registry/tested_configs.csv`), `rejected_ideas.md` |
| 21 | **B01e / DR05-H5 null control NULL-REJECTED (seq 231)**: gap-fade shows unexpected edge (633 fades, avg $118.63 slip-1, 4/5 years) ⇒ preregistered escalation B02 on unseen facets | driver `9ccbfe9` → `src/analytics/b01e_gapnull.py` → result + B02 preregistration in `2f81f05` → `research/04_complementary_family/b01e_gap_trades.csv`; registry row seq 231 (status `NULL_REJECTED_escalate`) |
| 22 | **B02 escalation FAIL 3/6 gates (seq 232)**: net_slip1 $75,095.12 but top-1% of trades = 90.1% of net (< 50% required), worst trade −$8,544.36 / trade-ES5 −$5,389.98 (bounds −$4,000/−$1,500), 52.7% of active months positive (≥ 60% required); PASSED slip-2 ($68,765.12, avg $108.63), roll-artifact (Δ0.8%); losing-day corr with Family A −0.0783, Family-A top-10 retention 1.0171 (genuinely independent event class, not a system). Axis CLOSED | driver `src/analytics/b02_gap_escalation.py` (prereg in `2f81f05`) → results `82d19e4` → `research/04_complementary_family/b02_gap_escalation_result.csv`, `b02_gap_trades_slip1.csv`; registry row seq 232 |
| 23 | **Wave B01 conclusion: Family B FALSIFIED** in its preregistered high-value forms (failed-DC reversion, ORB-failure reacceptance, gap rejection) on 2022–2026 NQ under frozen gates; 3 R1 trials of the ≤12 budget consumed; F04/F05/F07/F08 inherit negative evidence, deprioritized | `82d19e4` → `research/registry/rejected_ideas.md` "WAVE B01 CONCLUSION (2026-08-07)" |
| 24 | **PORTABILITY-01 preregistered** before any result: YM+RTY+CL (thesis-preselected, no cherry-picking), identical VolMult 6–30 grid, sigma-scaled thresholds, tick-value-normalized clamps (CL halved: 20–600), per-instrument Lifetime commissions, slip-1, pass rule ≥2/3 positive, no rescue permitted, seq 233–271 | **`b139cbb`** → `runs/PORT01_SWEEPS/spec.yaml` (source_commit `82d19e4`, strategy sha256 `60d584c5…`, engine sha256:b4255f1b0dd7fba1) |
| 25 | **PORTABILITY-01 verdict 0/3 — NQ-SPECIFIC ALPHA CONFIRMED**: YM −$21,947 (6/13 cells positive), RTY −$17,006 (4/13, Spearman 0.341 p=0.26), CL −$12,218 (0/13, Spearman 0.231 p=0.45); with the prior ES failure the family is 0-for-4 external; constitution §20 penalty binds all final claims | engine jobs **5e4cdbefeb834edf** (YM), **07477199a89246b4** (RTY), **aff52fd49e79499d** (CL) → ledgers `runs/PORT01_SWEEPS/ledgers_ym/` (13), `ledgers_rty/` (13), `ledgers_cl/` (13) + `ym_summary.json` → interim `b9e7686` (YM read) → verdict `a18f6d9` → `runs/PORT01_SWEEPS/PORT01_VERDICT.md` |
| 26 | **DM01 day-margin variant MEASURED**: 13 cells (seq 272–284, operational, descriptive-only), V3 native time filter EndTime 16:40 ET (5-min buffer before the verified 16:45 cutoff), policy arm D (reconfirmation) only. Result: net $188,605.25 = **95.2% retention**, Sharpe 0.9726 vs 1.0104 (calendar REALIZED_ONLY), max DD −$40,110.34 (+2.5%), **top-10 unconstrained-day retention 96.2%**. Does NOT replace the champion (thesis §24 dominance test not met) | spec preregistered in `b9e7686` → `runs/DM01_DAYMARGIN_SWEEP/spec.yaml`; engine job **59a1405f7ec442fd**; 13 ledgers + result commit `d6faa54` → `reports/DAY_MARGIN_VARIANT.md`; margin facts `research/operational/day_margin_variant/MARGIN_RULES.md` (claim 17) |
| 27 | **Final package trial accounting**: campaign 229 R1 (bracket 229–383, strict relabel 295–335) + audit 0 + B01 3 (230–232) + PORT01 39 (233–271) = 271 R1; DM01 13 operational (272–284) | `research/audit/REGISTRY_GAP_ASSESSMENT.md` + `reconstructed_trials.csv` (campaign block) + registry rows/specs cited in 20–26; full accounting: `reports/FINAL_RESEARCH_LEDGER_SUMMARY.md` |

## Registry status

`research/registry/tested_configs.csv` carries contemporaneous rows through seq 284: the PORT01
(233–271) and DM01 (272–284) rows were appended at `04c2684`, after their preregistered specs
(`b139cbb`, `b9e7686`) and results; the brief lag between spec commit and row append is on the
record via the commit chain.

## Standing HUMAN ACTION items (unchanged from the audit)

Vendor-blob history erasure (filter-repo + force-push + GitHub Support GC) and remediation of the
remote `research-campaign` tip, which still tracks the vendor package —
`research/audit/VENDOR_BINARY_REMEDIATION.md` §4. Repository must remain PRIVATE at minimum
until complete.
