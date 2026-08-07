# FINAL SYSTEMATIC SYSTEM — decision document

_2026-08-07 · branch `post_campaign_audit` · constitution: `research/Research_Thesis.txt`
v2 (`3bc5a3a`), final-questions analog · campaign CLOSED at the §23(B) stop condition
(`research/CAMPAIGN_STATE.md` §9b), POST_CAMPAIGN_AUDIT_01 PASS (`research/audit/AUDIT_EXECUTIVE.md`),
Wave B01 FALSIFIED (`research/registry/rejected_ideas.md`), PORTABILITY-01 0/3
(`runs/PORT01_SWEEPS/PORT01_VERDICT.md`). Every number here is sourced from committed evidence;
risk metrics are labeled REALIZED_ONLY or TRUE_MTM per constitution §10._

---

## 0. The claim, stated exactly once and exactly right

This document freezes the **best robust historical system found under the defined research
universe and evidence constraints** (NQ, 2022-01-01 → 2026-07-31, NT8 Standard fills, verified
cost stack, committed-ledger evidence only).

It is **NOT forward-validated**. It is **NOT deployment-ready**. **NO clean out-of-sample window
exists** — every session through 2026-07-31 was consumed during discovery. **External portability
is refuted**, not merely untested: 0-for-4 across ES, YM, RTY, CL. The honest classification,
binding per constitution §20 penalty (`PORT01_VERDICT.md` §4):
**"NQ-specific historical edge, 2022–2026, tail-concentrated, externally unvalidated."**

## 1. What is the champion

**Executable R5-E10** — the Family-A executable reference frozen by POST_CAMPAIGN_AUDIT_01
(`research/audit/EXECUTABLE_ENSEMBLE.md`, `FINALIST_SCORECARDS.md`, `research/frontier.yaml`
`FAMILY_A_EXECUTABLE_REFERENCE`):

> 13 × `SolarWaveOpenV3` **virtual** members (StartUp=**false**, ThresholdMode 1, VolPeriod 460,
> clamp 40–1200 ticks, VolMult 6, 8, …, 30) → per-bar target = **round(10 × mean member
> position) MNQ, max 10** → net-change execution at next bar open → session-close flatten →
> MNQ Lifetime commission $0.65/side (empirically verified) + 1 tick slippage per execution per
> contract on net target changes.

Headline (session-basis **TRUE_MTM**, 2022-01 → 2026-07-31): **net $179,361.36, Sharpe 0.9671,
max DD −$41,252.20 (daily-sampled)**, daily correlation with the theoretical ensemble 0.9985,
top-10-day retention 98.6%, mean |exposure| 0.2783 NQ-equivalents (no hidden leverage).

The champion passed ALL preregistered AUDIT-04 executability gates. The pass margin is **thin
(0.003 Sharpe on the session basis)** and is permanently reported as thin; it is robust to the
unpreregistered micro-choices — round and floor rules pass on BOTH session and calendar bases
(margins 0.003–0.012), only the cost-maximizing ceil rule fails (`research/audit/e10_sensitivity.csv`,
`SECOND_RED_TEAM.md` §2/§4).

Why this and not the theoretical ensemble: the audit separated R5 from R4 **on execution
economics** — the first ranking-relevant separation that does not rest on an insignificant point
estimate (R5 vs R4 ΔSharpe +0.087, P = 0.358, never resolved). R5's lower turnover survives the
MNQ fee schedule; every discrete R4 executable fails its Sharpe gate by 0.17–0.24.

## 2. Pareto alternatives (audited status)

Full table with tier labels: `reports/FINAL_PARETO_FRONTIER.md`. Summary:

| candidate | role | key numbers | status |
|---|---|---|---|
| **R5-E10 executable** | CHAMPION | above | passes all gates; margin thin |
| **R5 theoretical** (strict 1/N, NQ $4.36/RT) | research proxy of the champion (corr 0.9985) | session TRUE_MTM net $198,058.82, Sharpe 1.0642, DD −$39,853.39 daily / **−$42,204.42 bar-level** | STRONG_HISTORICAL_CANDIDATE — REPRODUCED 13/13 fill-by-fill |
| **R4-21 theoretical** (fixed SM 170–880, 21 cells) | simplicity/robustness reference; smallest max DD at every granularity | session TRUE_MTM net $159,423.70, Sharpe 0.9704, DD −$36,360.30 daily / −$39,493.63 bar-level | NOT EXECUTABLE at acceptable cost (all discrete variants fail by 0.17–0.24 Sharpe) |
| **ccHL anchor** (close-confirmed High/Low, 10 cells) | historical alternative | campaign-reported: net $215,137, Sharpe 0.912, DD −$47,698 (REALIZED_ONLY, 1,424-calendar) | **INCONCLUSIVE — NOT RE-AUDITED** (no re-execution, no MTM/executable work; numbers remain campaign-reported) |

Rejected/invalidated (never Pareto-alternatives going forward): C2 Type-3 re-entry sleeve
(interaction test: −0.402 Sharpe on the adaptive core, P = 0.879), R4b 8-cell plateau (boundary
was an in-sample selection), every discrete R4 executable, and every Family-B candidate (§3).

## 3. Families contained: one

**Family A only.** The mandated second family (Family B — failed directional change + value
reacceptance, DR-05) was built, preregistered, and **FALSIFIED** on 2022–2026 NQ under frozen
gates (Wave B01, seq 230–232, `research/registry/rejected_ideas.md`):

- **B01a / DR05-H1(b)**: failed-flip conditioning carries no reversion information (diff −2.0
  ticks vs required ≤ −10; sign stable 3/5 years vs ≥4; p = 0.171 vs < 0.05). DR05-H2 dead unbuilt.
- **B01c / DR05-H3** (seq 230): ORB-failure fade net **−$22,534** at slip-1 (PF 0.839), negative
  even at slip-0. FAIL on the first gate.
- **B01e/B02** (seq 231–232): gap-fade null control rejected its null (633 fades, avg $118.63
  slip-1) but the escalation FAILED 3/6 gates — top-1% of trades = **90.1%** of net, worst trade
  −$8,544, stopless left tail, 52.7% of active months positive. Genuinely independent of Family A
  (losing-day corr −0.08) but not a system. Axis CLOSED.

Consequence: **no diversification exists in the delivered system.** There is no portfolio layer,
because there is only one return stream to hold.

## 4. Exact implementation and state machines

Reference semantics: `src/ninjascript/SolarWaveOpenV3.cs` (sha256
`60d584c5c820d8fe131eb889a37d1e07d6e746ed5f3919b8d47d0ba7d74df167`), the class that produced
every committed R5 member ledger (audit-verified; V4 was never the measured class).

**Member state machine (each of the 13 virtual members, identical except VolMult):**
1. State: trend direction (up/down), `anchor` = running extreme of the CLOSE since trend start
   (AnchorMode 0), episode threshold `sEff`.
2. At trend birth, `sEff = ResolveS()` — ThresholdMode 1: `S = VolMult × sigma`, sigma = causal
   mean |close − close[1]| over the trailing 460 bars (VolPeriod), clamped to
   [SMinTicks, SMaxTicks] = [40, 1200] ticks — **frozen for the episode** (sampled once at birth).
3. Trailing level = anchor ∓ S. Flip on a **strict** close-break of the level; the flip is
   simultaneously the exit of the old position and the Type-1 entry of the new one
   (ExitMultiplier 0: exit and reversal share one distance — H-007 established splitting them
   degrades monotonically).
4. Initialization: `StartUp = false` seeds the first trend direction (the audited truth; the
   published recipe said `true` and does NOT reproduce the ledgers —
   `research/audit/R5_REPRODUCTION.md`).
5. Flat at every session close (exit-on-session-close); flat-at-close is what makes
   session-realized P&L identically TRUE_MTM (proven to the cent for all members,
   `research/audit/MTM_RECONCILIATION.md`).

**Ensemble target layer (E10, on top of the 13 member positions ∈ {−1, 0, +1}):**
1. Each bar close: `mean = (1/13) Σ member_position_i`.
2. Target = `round(10 × mean)` MNQ contracts, capped at ±10 (= 1 NQ-equivalent).
3. Execute only the **net change** vs the current position, at the next bar open.
4. Session close: flatten everything (session-close-phase execution, distinct from open-phase —
   `src/analytics/audit04_executable.py`).

**WARNING (binding disclosure):** no master-strategy NinjaScript implementation of the E10 layer
has been written or validated. The E10 numbers come from the audited Python simulator
(`src/analytics/audit04_executable.py`, physical-instant timeline, slippage-cap-aware raw prices)
over the 13 exactly-reproduced member ledgers. Writing and gate-checking that master strategy is
open work — see `reports/FINAL_EXECUTION_SPEC.md`.

## 5. Exact parameters (all effective, none omitted)

From the audited run specs (`runs/PORT01_SWEEPS/spec.yaml` schema, NQ configuration):

```
Strategy        : SolarWaveOpenV3  (src/ninjascript/SolarWaveOpenV3.cs)
Instrument      : NQ 09-26 back-adjusted merge, 3-minute bars, Last
StartUp         : false            (audit-corrected; true does NOT reproduce)
TrendMultiplier : 90               (inert for Type-1 — derived, not merely measured)
StopMultiplier  : 179              (inert under ThresholdMode 1)
SlowdownScan    : 5   WeakWeakSplit: 10   (inert for Type-1)
AnchorMode      : 0                (running CLOSE extreme — vendor behaviour)
ThresholdMode   : 1                (S = VolMult × sigma, frozen at trend birth)
VolPeriod       : 460 bars         (~1 session; H-012: not load-bearing, lags
                                    0.13–7.96 sessions all give Sharpe 0.769–1.494)
SMinTicks       : 40   SMaxTicks : 1200
ExitMultiplier  : 0                (no split exit — H-007)
EntrySignalType : 1                (Type-1 flips only)
EnableLong/Short: true / true      UseTimeFilter: false
VolMult         : {6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30}  — 13 members
Weighting       : strict 1/N, flat days count as zero. DO NOT select a member
                  (PBO for that choice is 0.898).
Engine          : NT8 8.1.8.1 / CrossTrade v1.13.9, fingerprint sha256:b4255f1b0dd7fba1
```

## 6. Router and risk logic

**Router: none.** A router requires ≥2 families; Family B was falsified (§3). PORT-02 (router)
never unlocked (`research/audit/NEXT_RESEARCH_ROADMAP.md` ordering).

**Risk logic: none beyond the structural 1-NQ-equivalent cap** (max 10 MNQ, embedded in the E10
target rule). Sizing, volatility targeting, and leverage research were never unlocked — thesis
§21 lists 14 prerequisites (two-family portfolio, locked-forward data, tail/margin stress, …) and
at least half do not exist. Any leverage discussion before those exist violates the constitution.

**Contract mapping:** target = round(10 × mean member position) × MNQ, max 10 MNQ = 1 NQ-eq.
Rounding is a non-issue: mean rounding error 0.024 NQ-eq (max 0.046), position-path corr 0.9974,
top-10-day retention 98.6%. The entire executable penalty is the MNQ commission multiple
(10 × $1.30 = $13.00/RT vs $4.36/RT on NQ, 2.98×), ≈ $22.4k ≈ 11% of net ≈ 0.10 Sharpe. At K > 1
NQ-equivalents the penalty shrinks (whole-NQ blocks at $4.36; the E10 figures are the all-micro
worst case) — arithmetic, not a result (`EXECUTABLE_ENSEMBLE.md`).

## 7. Commissions and slippage (verified, not assumed)

| item | value | verification |
|---|---|---|
| MNQ commission | **$0.65/side, $1.30/RT** | empirical, constant across 704 fills, `runs/AUDIT04_MNQ_PROBE` |
| NQ commission (members/theory) | $2.18/side, $4.36/RT | Lifetime template, frozen-baseline gate |
| Slippage model | 1 tick/execution/contract on net target changes | campaign convention; NT8 caps modeled slip by bar range |
| E10 realized costs 2022–2026 | commission $33,881.90 + slippage $26,063.00 on 52,126 contracts | `executable_ensemble_metrics.csv` |
| External slippage evidence | retail NQ 0.7–1.2 ticks RTH | `research/01_diagnostics/external_review.md` (cited in `FILL_AND_TAIL_AUDIT.md` §4) |
| Fill resolution | Standard is fair and on-balance slightly conservative: High-res changes net ≤1.1%, both signs, tails untouched | `FILL_AND_TAIL_AUDIT.md` §2 |

## 8. Results — TRUE_MTM

**Champion, R5-E10 executable (session basis = TRUE_MTM, proven identity):**

| metric | value | source |
|---|---|---|
| Net (2022-01-01 → 2026-07-31) | **$179,361.36** (90.6% of theory) | `executable_ensemble_metrics.csv` |
| Sharpe (session TRUE_MTM) | **0.9671** (Δ vs theory −0.097; gate −0.10) | same |
| Sharpe (calendar basis) | 0.8883 (gate margin larger there) | `e10_sensitivity.csv` |
| Max DD (daily-sampled TRUE_MTM) | **−$41,252.20** (+3.5% vs theory) | `executable_ensemble_metrics.csv` |
| ES5 (5% of sessions) | −$4,028.34 | same |
| Time under water | 1,120 of 1,184 sessions | same |
| Worst day | −$12,723.70 | same |
| Mean \|exposure\| | 0.2783 NQ-eq (max 1.0) | same + `EXECUTABLE_ENSEMBLE.md` |
| Contracts traded | 52,126 MNQ (≈44/session, arithmetic) | same |

**Bar-level drawdown disclosure.** Bar-level TRUE_MTM max DD was computed for the theoretical
ensembles: **R5 −$42,204.42** (7.9% deeper than the daily figure), R4 −$39,493.63. An E10-specific
bar-level DD was not separately published; capital and margin sizing must use at least the
bar-level numbers, noting 3-minute bar-close marking still bounds true tick-level excursion from
below by an unmeasured margin (`MTM_RECONCILIATION.md` §3, `SECOND_RED_TEAM.md` §4).

**Theoretical proxy (R5 E0, session TRUE_MTM; corr with champion 0.9985):** net $198,058.82,
Sharpe 1.0642, **Sortino 2.2246, Calmar 1.0577**, DD −$39,853.39 daily, ES5 −$3,983.04, TUW 1,112,
worst day −$13,004.76, worst week −$12,463.11, worst quarter −$8,612.61
(`mtm_reconciliation_metrics.csv`). E10 Sortino/Calmar/PF were not separately published — quote
the proxy, labeled as proxy. Trade-level statistics (REALIZED_ONLY, theoretical R5 on the
1,424-session campaign calendar, `reports/solar_family_finalists.md`): PF 1.107, win rate 39.6%,
turnover 1.84 trades/session, exposure 93.5% of days with P&L, avg trade $5.80/ensemble-unit
(that statistic must never again be compared with full-contract costs — `EXECUTABLE_ENSEMBLE.md`).

**Annual results** (session TRUE_MTM, computed from the committed daily vectors
`research/audit/e_variant_daily_vectors.csv`; E0 column reconciles exactly with the published
per-year sheet):

| year | R5-E10 executable | R5 theoretical (E0) |
|---|---:|---:|
| 2022 | $37,911.03 | $41,065.97 |
| 2023 | $8,015.56 | $12,159.88 |
| 2024 | $24,018.92 | $29,300.96 |
| 2025 | $56,688.76 | $60,459.36 |
| 2026 (→07-31) | $52,727.08 | $55,072.65 |
| total | **$179,361.36** | $198,058.82 |

Positive in all five calendar years, including the 2022 bear year — the strongest temporal
evidence the campaign has. Note the 2025–26 weight: 8 of the top-10 and 7 of the worst-10 days
fall in 2025–26 (`FILL_AND_TAIL_AUDIT.md` §3).

**Long/short contribution** (REALIZED_ONLY, theoretical R5): long 15,071 trades, $147,453,
PF 1.178; short 19,077 trades, $50,606, PF 1.049. **The short side has no standalone edge**:
ex-2022/2025 it is net −$8,397, Sharpe −0.113. The long side carries the system
(`solar_family_finalists.md`).

## 9. Tail dependence — the dominant risk

- Top **1% of trades ≈ 160%** of net (bottom 99% lose in aggregate) — REALIZED_ONLY, theoretical
  R5 (`solar_family_finalists.md`; predicted by DC01 from the exponential overshoot distribution).
- **Ex-top-10-days: $71,923 of $198,059 retained = 36%.** Daily removal, not trade removal, is
  the correct stress and it is much harsher.
- E10 preserves the tail: top-10-day retention 98.6%; top-day P&L is fill-model-independent
  (2 of the top 10 days contain any differing fill under High resolution, each exactly one tick).
- Consequence, binding: any filter, target, cap, or fill degradation must be checked for
  right-tail retention before anything else.

## 10. Cost stress

**2-tick slippage: 87.4% of net retained** ($173,084 vs $198,059 on the 13 NQ member cells);
trade paths identical in all 13 cells (slippage cannot alter paths). Per-cell retention is
turnover-driven (vm6 51.6% → vm30 96.6%). Slip-3 ≈ 75% floor (linear extrapolation is a floor
because the NT8 bar-range cap binds more often at larger slippage). The campaign-era "slip-2
halves net / slip-3 erases it" language is corrected: it described 1-minute-era high-turnover
plateau cells, not R5 (`FILL_AND_TAIL_AUDIT.md` §1).

## 11. Cross-market evidence — 0-for-4, NQ-SPECIFIC

Identical VolMult 6–30 grid, sigma-scaled thresholds, tick-value-normalized clamps,
per-instrument Lifetime commissions, slip-1, no per-instrument fitting permitted
(`PORT01_VERDICT.md`, preregistered at `b139cbb`):

| market | ensemble net (1/N) | positive cells | shape vs NQ (Spearman) |
|---|---:|---:|---:|
| NQ (reference) | +$198,059 | 13/13 | 1.000 |
| ES (campaign) | −$12,455 | 8/13 | 0.780 |
| YM | −$21,947 | 6/13 | mid-grid positive, narrow catastrophic |
| RTY | −$17,006 | 4/13 | 0.341 (p = 0.26) |
| CL | −$12,218 | 0/13 | 0.231 (p = 0.45) |

Preregistered rule: ≥2/3 = universal-mechanism support. **Result 0/3** (plus the prior ES
failure). The "shape travels" consolation does not generalize; there is no evidence of a
transportable structural law. All structural-alpha language is removed from final claims.

## 12. Multiple-testing burden

- Campaign: **229 R1 trials** on the preregistered rule-R1 basis; honest bracket **229–383**
  (every seq-assigned ledger); best consistent strict relabel **295–335**, disclosed
  (`research/audit/REGISTRY_GAP_ASSESSMENT.md` (b)).
- Post-audit: audit itself **0** R1 trials; Wave B01 **3** (seq 230–232); PORTABILITY-01 **39**
  (seq 233–271); DM01 **13** operational-variant configs (seq 272–284, descriptive, in flight).
- **DSR is INCONCLUSIVE by the preregistered rule** (`TRIAL_ACCOUNTING_RULE.md`, written before
  computation): every candidate scores 0.45–0.55 against a 0.90 bar; Harvey–Liu haircut Sharpe
  **0.000** at every point of the 229–383 bracket; a defensible alternative variance pool gives
  0.96. Deflation adjudicates nothing here in either direction — the promotion case rests on
  structure (H-014 mechanism control, p = 0.009, the campaign's only clean significance result),
  absolute-edge bootstrap (P(Sharpe ≤ 0) = 0.0020), and executability, exactly as the
  preregistered rule anticipated.
- Waves 1c–3 carry a registry-gap discount: reproducible from 296 committed ledgers, but
  criteria not provably fixed in advance (H-014 criteria-level excepted). Mostly negative
  verdicts, which post-hoc flexibility inflates less.

## 13. Complexity

Deliberately minimal, and the campaign's central finding is why: one signal family (Type-1
directional-change flips), one live axis (VolMult, held as an unselected 13-member 1/N ensemble
precisely because selection has PBO 0.48–0.90 with negative IS→OOS slopes), zero conditioning
(every sleeve, filter, anchor, exit-split, wave-index, and stop-execution variant tested and
rejected), no router, no sizing. Total free parameters chosen by the researcher and defended:
the grid endpoints {6…30} and the clamp [40, 1200] — both stress-tested (H-012; V4 tick-snap
ΔSharpe +0.019, P = 0.33).

## 14. Strongest failure mode, invalidating regime, monitoring

- **Strongest failure mode: right-tail drought + friction** (thesis final answer M): a future
  shortage of large directional overshoots while false-start and execution costs continue. The
  bottom 99% of trades lose money; the system starves quickly without its tail.
- **Invalidating regime: persistent low-volatility two-way chop** (thesis final answer N) —
  frequent threshold flips, no large trend days; the edge lives at δ/σ ≈ 10–18 above a fixed
  dollar friction floor, and a durable low-vol regime pushes it onto that floor (the mechanism
  behind part of the ES failure).
- **Monitoring statistic: the quarterly overshoot ratio r = E[ω]/δ.** The edge IS r exceeding
  1.0 by ~3% (t = 31 → 2.1 across thresholds, DC01); r → 1.0 removes it outright. Measurable
  quarterly at zero cost, no trading, no new configurations — the system's own early-warning
  statistic and the single cheapest next action. Additional monitoring hook: re-verify the MNQ
  commission whenever the broker plan changes — a ≥$0.10/side worsening fails E10's gate
  (`SECOND_RED_TEAM.md` §4).

## 15. What this document does not establish

No forward validation, no deployment readiness, no clean OOS, no external validity, no second
family, no portfolio, no sizing. Nothing here may be traded, and the constitution's hard safety
boundary (research/backtest only) remains in force. The adversarial companion is
`reports/FINAL_SYSTEMATIC_RED_TEAM.md`; the execution recipe is
`reports/FINAL_EXECUTION_SPEC.md`; evidence chains are in `reports/FINAL_EVIDENCE_MAP.md`.
