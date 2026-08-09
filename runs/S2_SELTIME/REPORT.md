# S2_SELTIME Arm A — RESULTS

> ⚠ **CORRECTED 2026-08-09 (same day), after red team.** Every gate number below is verified
> correct — CONFIRMED, no headline-flipping defect. But the CANDIDATE label is a statement about
> this run's frozen pre-registration, not about the mechanism being market-structure-specific or
> understood. **A 24-window full-day sweep (in the RED-TEAM INGESTION section near the end) shows
> 19/24 windows produce a positive effect and several beat this run's decision cell — the "genuinely
> different, market-structure-justified mechanism" framing below does NOT hold up and must not be
> cited without that correction.** Read the ingestion section before citing this run's mechanism
> claims (its gate results and numbers are unaffected and can be cited as-is).

Run against `spec.yaml` (frozen `3c6f6cd`), Arm A only — Arm B was screened out and never
consumed an alpha-budget slot (spec §0). Control cross-check: 1,139/1,139 exact match. Code:
`src/run.py`.

## Headline: the first CANDIDATE this campaign has produced, with an important caveat that must
travel with it

**Arm A (block new entries/flips during 02:00-08:00 ET) passes gates A, B, and C outright, and
gate D marginally (3 of 4 boundary perturbations).** Per the frozen verdict rule this is a
**CANDIDATE** — the first mechanism in the entire SelTime/M-hypothesis line (M1, M5, arm_ER,
arm_TOD all failed) to clear the legacy triple, chronology, and tail-preservation bars together.
**It is not promoted this wave** (frozen rule: a CANDIDATE earns a capital-map + parity R2 later,
applied separately to Product A and Product B).

**The caveat, surfaced because it is required, not because it was looked for**: the D7-boundary
split shows almost the entire benefit is concentrated **after** 2024-08-05. Pre-boundary
(2022–2024-08-04, 669 days): ΔSharpe **−0.010**, CDaR essentially flat (−$199, i.e. very slightly
worse). Post-boundary (470 days): ΔSharpe **+0.106**, CDaR **+$3,215** better. The 106-session 2026
stub alone contributes the single largest improvement (ΔSharpe +0.219). **This is the same kind of
boundary-dependent result W19R1's addendum flagged for arm_TOD, and per R5 the flip in magnitude
(not sign, here — both halves are non-negative on CDaR, but Sharpe is flat-to-negative pre and
strongly positive post) is itself the finding, not the pooled full-window number.**

## What is and is not stable

**The underlying loss pattern IS stable**: Solar loses money in EUROPE_PREUS in 5 of 5 years,
tight range ($4.8k–$6.5k), including in the pre-boundary years — this was the entire justification
for freezing the arm (spec §0). **What is not stable is the arm's Sharpe/CDaR payoff from removing
that loss.** Removing a similarly-sized dollar loss every year produces a small-to-negative Sharpe
effect pre-2024-08 and a large positive one after. This is not fully understood by this run and is
disclosed as unexplained rather than rationalized: a plausible mechanical candidate is that
overall daily P&L variance rose in the back half of the sample (consistent with D7's own
market-variable findings around the same period), which would mechanically amplify the Sharpe
impact of removing a fixed-dollar loss source without the removed dollar amount itself changing —
**this is a hypothesis, not tested here, and is flagged as the natural next question rather than
asserted as the explanation** (the same falsification discipline D7 required of itself).

## Gate results

| gate | result |
|---|---|
| 0 (disclosure) | exposure ratio 0.929, contracts/day ratio 0.955, 8.2% of bars modified — this is a genuine eligibility change, not exposure-neutral by construction (expected: this arm is explicitly a de-risking-inside-one-window rule, distinguished from M1's failure mode by directive §5, not required to be exposure-neutral) |
| A (legacy triple) | **PASS** — Sharpe 0.709→0.756 (+0.047), CDaR $27,162→$24,334 (+$2,828 better), top-10 retention 101.8% house / 104.8% own |
| B (chronology) | **PASS** — 4/5 years positive (2022 is the one negative year, −0.064), survives excising final 106 sessions |
| C (tail preservation) | **PASS** — top-1% bar retention 97.6%, top-20-move retention 91.6%, long-share drift only 4.6pp (no long-only-beta conversion) |
| D (boundary stability) | **MARGINAL PASS** — 3 of 4 perturbations same-direction; the ±60min WIDE perturbation (07:00–15:00) flips Sharpe's sign (though not CDaR's), i.e. widening the window far enough erodes the effect. Narrow perturbations (±30/60 min tighter) all strengthen it directionally. |

Bootstrap (block=5, B=10000, seed=20260809): P(ΔSharpe>0) = **0.784**, P(ΔCDaR ratio>0) = **0.733**
— genuine, but below the informal 0.85 bar this program has used elsewhere for "strong" evidence.
Disclosed as moderate, not strong, confidence.

## Yearly table

| year | Δsharpe | sign |
|---|---:|---|
| 2022 | −0.064 | negative |
| 2023 | +0.009 | positive |
| 2024 | +0.172 | positive |
| 2025 | +0.018 | positive |
| 2026 (stub) | +0.219 | positive |

2022's negative year and 2024's outsized positive year both sit either side of a rough halfway
point in the dev window, consistent with the D7-boundary split's pattern above rather than
contradicting it.

## What this hands forward

1. **This is a genuinely different mechanism from everything closed so far** (M1's continuous
   volatility rescaling, arm_ER's ER150 continuous score, arm_TOD's cross-instrument score) — a
   hard discrete eligibility gate on a market-structure-justified, chronologically stable loss
   window. It should not be conflated with the closed generic-de-risking family (directive §2):
   the loss window itself, not exposure overall, was the target, and gate C confirms no beta
   conversion occurred.
2. **The boundary-dependence caveat must travel with any future citation of this result.** A
   capital-map/parity R2 (per the spec's own verdict rule) should report the same D7-split, not
   just the pooled number, and should investigate the variance-mechanical hypothesis above before
   treating the post-boundary Sharpe gain as durable.
3. Gate D's marginal pass (specifically the wide-perturbation sign flip on Sharpe) means this is
   not deep in a plateau — it is closer to an edge than the directive's promotion standard prefers.
   This alone does not fail the frozen rule, but it tempers how much weight the CANDIDATE label
   should carry pending red team.

Mandatory red team (V7 §G) queued next — this result could change a promotion decision.

---

# RED-TEAM INGESTION — appended 2026-08-09. **Point 1 of "What this hands forward" above is
WITHDRAWN as stated. All gate numbers are CONFIRMED correct. Read this before citing this run's
mechanism.**

Verdict verbatim at `red_team/RED_TEAM_s2_seltime.md`, unedited. Every gate/pre-check number in
this report was independently re-derived (three separate re-implementations, a 2,000-trial fuzz
test of the eligibility state machine, a full independent pipeline rebuild) and reproduces exactly
— **no headline-flipping defect, no coding bug found anywhere.** The corrections are entirely in
this report's *narrative interpretation*, which is exactly the part likely to be cited going
forward, so they are treated with full weight below.

## 1. WITHDRAWN — "genuinely different mechanism... market-structure-justified" is not
demonstrated, and a direct test argues against it.

The reviewer applied the identical `apply_entry_eligibility()` rule to **24 other 6-hour windows**
spanning the full day (hourly steps) on the same control series. **19 of 24 windows produce a
positive ΔSharpe; several beat the decision cell on every gate-A metric** (best: 14:00-20:00,
ΔSharpe +0.130 vs the decision cell's +0.047, spanning the RTH close and the evening Asia open —
no low-liquidity story at all). **The decision cell ranks 11th of 24 by ΔSharpe — essentially the
sweep's median, not an outlier.** At least 8 of 24 windows pass gate A's full three-prong test.

**This does not mean the result is vacuous** — the reviewer checked the strongest competitor
(14:00-20:00) against gate B's chronology bar and it **fails** (3/5 years positive, not 4/5). So
the full A+B+C+D battery does discriminate; gate A alone does not. But no test in this run checked
whether 02:00-08:00 is *uniquely* selected by the full battery among plausible alternatives — that
test was never run, and the report asserted a market-structure-specific mechanism instead of
demonstrating one.

**Corrected statement**: this looks structurally like it could be a generic new-commitment-
suppression / whipsaw-reduction effect — present at many times of day, not preferentially at
low-liquidity ones — that happens to also clear chronology at this particular window, rather than
a window-specific market mechanism. Downgraded from "established" to "open question pending a
B/C/D sweep across alternative windows," which is now the natural next step before any
capital-map/parity R2.

## 2. WITHDRAWN — "removing a similarly-sized dollar loss every year" is false.

The claim conflated the *window's* stable aggregate loss (S0's pre-check, confirmed exactly:
−$4.8k to −$6.5k/year, 5/5 years) with the *eligibility rule's own captured benefit*, which is a
much narrower and unstable quantity: **−$2,552 (2022, the rule makes it WORSE) / +$246 / +$4,834 /
+$464 / +$4,328 (2026 stub)** — negative in one of five years, ranging over $7,386, with **89%+ of
the entire multi-year benefit concentrated in 2 of 18 calendar quarters** (2024-Q3, which straddles
the D7 boundary itself, and 2026-Q2, the tail of the already-flagged-unusual stub). Pooled captured
fraction of the window's own loss: only 25.3%.

## 3. TESTED AND REFUTED — the hedged variance-mechanism hypothesis does not hold.

REPORT.md's §"What is and is not stable" proposed, properly hedged as untested, that rising
post-D7 daily P&L variance might mechanically amplify a stable dollar benefit into a larger Sharpe
gain. Directly tested: the arm/control **daily-P&L variance ratio barely moves** between periods
(1.0003 pre-D7 → 0.9916 post-D7, a 0.87pp shift) — there is no meaningful variance-channel effect.
The Sharpe swing is **essentially 100% a mean effect** (arm mean $1.27/day worse than control
pre-D7, $17.37/day better post-D7), consistent with the quarter-concentration in point 2. The
proposed mechanical direction was also backwards from Sharpe=μ/σ algebra (a larger σ dampens,
rather than amplifies, a fixed mean shift's Sharpe contribution). Mark this hypothesis TESTED AND
NOT SUPPORTED, not open, in any future citation.

## 4-6. Disclosure-level, no correction needed to the numbers

Gate D's four boundary perturbations are nested/monotonic in width around the same center, not
independent replications — the existing "3 of 4" disclosure is honest but a weaker stability signal
than 3 independent alternative windows would be (already-marginal result, now understood to be
even more marginal in spirit). Commit-timing gap (2m33s, spec→result) checked for leakage and
cleared — both pre-checks independently reproduce exactly from raw data, which would be an odd
thing to get right if fabricated after the fact. Gate C's 91.6% top-20 retention traced to exactly
2 large, partially-offsetting bars on one session (2025-04-09) — confirmed benign, not diluted
broad-based risk.

## What survives untouched

**All four gate results (A/B/C/D), the exposure disclosure, the bootstrap, and the D7-split table
are independently re-verified correct to full precision — no coding defect anywhere.** Both S0→S2
handoff pre-checks (Solar EUROPE_PREUS 5/5-years-negative; BMOM AFTERNOON 3/5-years-negative,
screened out) reproduce to the cent. The frozen verdict rule was applied correctly: **CANDIDATE
stands as a true statement about this run's specific frozen pre-registration** — it is not a false
positive. What it may not do, until a window-specificity sweep is run, is stand as evidence of a
market-structure-specific mechanism distinct from a generic whipsaw-reduction effect.

## Revised guidance for any capital-map/parity R2

1. Run gates B/C/D (not just A) across a modest sweep of alternative windows before treating
   02:00-08:00 as uniquely selected.
2. Cite the actual year-by-year and quarter-by-quarter dollar benefit (point 2 above), not a
   "similarly-sized loss removed" framing.
3. Drop the variance-mechanism hypothesis; the mean-shift concentration in 2024-Q3/2026-Q2 is the
   honest description of where the benefit comes from, and its overlap with D7's own boundary and
   the flagged-unusual stub is itself worth investigating before relying on the pooled number.
