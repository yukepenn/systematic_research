# W18R1_M1_VOLSEASON — **arm_FULL FAILS all three gates.** The premise is right; the implementation of it, through the frozen state machine, is not.

Wave 18 of the SYSTEM_MASTER campaign, MEGA PROMPT V7. Track R. Spec frozen and committed at
`d0b9f92` before any code existed. Alpha budget consumed: 1 of 2.

---

## Verdict against the pre-registered bar

| | Sharpe | CDaR₀.₉₅ | top-10 retention | net | gates |
|---|---:|---:|---:|---:|:--:|
| control (sigma460) | **0.7092** | **$27,162** | — | $119,009 | — |
| **arm_FULL** (decision cell) | 0.5577 | $35,498 | **80.5%** | $87,107 | **0 / 3** |
| arm_HALF (disclosure only) | 0.6142 | $26,888 | 92.1% | $97,897 | 1 / 3 |

`arm_FULL` fails Sharpe (−0.152), fails CDaR (+$8,336 worse), and fails right-tail retention
(80.5% against a ≥95% floor). Per the frozen rule this is **CONFIRMED-NOT-BENEFICIAL at the
screen level** for this estimator. `arm_HALF` was pre-registered as disclosure-only and
**cannot be promoted under any outcome**; it also fails, so the question does not arise.

## Step 1 (D4) — the premise is confirmed, hard, and it is a result in its own right

The pre-registered falsification was: if `r_s = mean(|Δclose_t| / sigma460_t)` over 3-minute
time-of-day slots has `max/min < 1.5` across slots with ≥200 bars, M1's premise is rejected.

**Measured spread: 11.04×.** `r_s` runs from **0.372 at 00:00 ET** to **4.105 at 09:33 ET**,
across 460 slots every one of which has ≥200 bars. The incumbent's threshold is mis-scaled
relative to local volatility by an order of magnitude across the trading day. The unconditional
volatility profile has a peak/trough ratio of 10.29×.

Cohort structure of the **unmodified incumbent** (cohorts defined in the spec before the run):

| cohort (ET) | share of bars | share of P&L | net | member flips/bar | mean `r_s` |
|---|---:|---:|---:|---:|---:|
| EVENING 18:00–23:59 | 26.0% | **−9.2%** | **−$10,989** | 0.044 | 0.613 |
| OVERNIGHT 00:00–08:59 | 39.4% | +28.0% | +$33,379 | 0.069 | 0.790 |
| RTH 09:00–16:59 | 34.6% | **+81.2%** | +$96,619 | 0.215 | **1.563** |

Two-thirds of the clock produces one-fifth of the money, and the evening third loses. That is a
genuine selectivity finding independent of whether M1 works, and it is the D4 deliverable §8
asked for.

**Pipeline validation before any gate was read**, as the spec required: the control was rebuilt
from the same code path as the arms rather than reused from a committed CSV, and it reproduces
`runs/SMV2AD_VOLMULT_CEILING/out/e10_daily_dev_control_1200.csv` **exactly** — 1,139 of 1,139
sessions matched, max absolute daily difference **$0.00**, contract counts identical.

## Step 2 — why it failed, measured rather than asserted

The spec claims, in its own mechanistic argument: *"Because E[f] = 1 by construction, the
AVERAGE threshold over a session is unchanged. This is a pure RE-ALLOCATION of threshold across
the trading day, not a net loosening or tightening."*

**That claim is FALSE, and this run establishes it.** Per C6 the correction lives here and not
in the frozen spec.

The incumbent resamples `S` **only at trend birth** (`sm01_solarsim.member_states`: `S` is
re-resolved inside the flip branch and nowhere else). So what governs the threshold is not
`E[f]` but **`E[f | flip bar]`** — and flips are not uniformly distributed across the day, they
concentrate in exactly the high-volatility slots where `f` is large:

| | mean `f` | median `f` |
|---|---:|---:|
| over all bars (by construction) | **1.000** | 0.806 |
| over bars where the incumbent flips | **1.536** | 1.426 |

Consequence, measured on the member state arrays:

| | control | arm_FULL | Δ |
|---|---:|---:|---:|
| mean `S` (points) | 122.43 | **201.31** | **+64%** |
| mean `S`, EVENING | 122.49 | 202.24 | +65% |
| mean `S`, OVERNIGHT | 122.47 | **193.61** | **+58%** |
| mean `S`, RTH | 122.35 | 209.38 | +71% |
| member flips | 58,701 | **31,766** | **−46%** |
| flips EVENING / OVERNIGHT / RTH | — | — | **−32.6% / −19.7% / −57.5%** |

Flips fell in **every** cohort, including overnight where the mechanism was supposed to
*tighten* the threshold and produce **more** flips. The overnight mean `S` rose 58%. M1 as
specified does not re-allocate the threshold across the day at all — **it widens the threshold
everywhere, by 64% on average.**

**And that means arm_FULL is, by accident, partly a repeat of an already-closed axis.** Uniform
clamp/threshold widening is the SMV2AD (fixed ceiling) and SMV2AG (adaptive ceiling) family,
closed in Waves 12–13 with the finding that widening buys Sharpe at the cost of CDaR. Here it
costs both, plus 19.5 points of right-tail retention — consistent with §5's unifying diagnosis
that the top 1% of trades carry 160% of net profit, since a 71% wider RTH threshold is
precisely a filter on the largest RTH moves.

## What is therefore established, and what is not

**Established (DIRECT):** intraday volatility seasonality is real and large in this substrate
(11× in `r_s`, 10× in the raw profile); the incumbent's P&L is overwhelmingly an RTH phenomenon
and its evening cohort loses money; and multiplying `sigma460` by a session-mean-1 seasonal
factor, fed through the incumbent's trend-birth-only `S` resampling, is a 64% threshold widening
that fails all three gates.

**NOT established (and the report would be dishonest to imply it):** that intraday seasonal
normalization of the decision threshold is a dead idea. This test is **confounded** by the
widening it did not intend, and that confound was knowable in advance from the state machine's
own semantics. The null is conditional on this estimator and this application point.

**Per the spec's own `kill_or_keep`**, a second bite requires a *structurally different*
seasonal construction, and a re-run at a different warmup floor or window length is explicitly
prohibited. Two constructions would qualify, and both are recorded as ranked ideas rather than
run, because §15's two-hypothesis cap for this wave is already spent:

1. **Exposure-neutral seasonal factor** — normalize so `E[f | flip] = 1` rather than `E[f] = 1`,
   estimated causally from the incumbent's own historical flip distribution. This makes the
   re-allocation claim true by construction instead of by assumption.
2. **Per-bar `S` re-resolution** — change *when* `S` is sampled rather than what it is sampled
   from. This is a change to the incumbent's core state machine, not to sigma, and is a larger
   and riskier proposition; it should be specified as a change to the Solar core and screened
   as such.

Neither may be run without its own frozen spec carrying a written mechanistic argument.

## Disclosures

- **Portfolio level (not a gate).** DAYONLY_DUAL6040 60/40 with the Solar leg swapped and the
  B-MOM leg unchanged: control Sharpe 1.264 / CDaR $14,322; arm_FULL 1.119 / $17,199; arm_HALF
  1.189 / $14,641. arm_FULL loses at portfolio level too.
- **Recency tiers (disclosure, not selection; every row a CONTINUATION number per §F).** Full
  dev / trailing 2yr / trailing 1yr Sharpe — control 0.709 / 0.671 / 0.580; arm_FULL 0.558 /
  0.545 / **−0.136**; arm_HALF 0.614 / 0.604 / 0.259. The trailing-1yr row is disclosure only
  and per §17 no candidate may be chosen on it.
- **Old-regime screen: N/A.** It was pre-registered as conditional on arm_FULL qualifying. It
  did not qualify, so no 2006-2021 data was read in this run.
- **A defect in this run's own diagnostic code, reported not tidied.** The first control
  cross-check returned `n_matched = 0` because `sess` is `datetime.date` in the rebuilt frame
  and `str` in the committed CSV, so the merge silently produced an empty join. The net sums
  were identical to the cent regardless, which is what exposed it. Fixed by casting both sides;
  the fix and the reason are in `src/step1_d4.py`. This is the **third** instance in two waves
  of a reconstruction/join defect in analysis code (after `c4_audit.py`'s position rebuild and
  `v4_friction.py`'s cycle counter) — that is a signal about the method, not about any one
  script, and it belongs in the standing cautions.
- **No uncertainty quantification is offered on the arm_FULL/control Sharpe gap** and none is
  needed for the verdict: the AND-rule is a point-estimate screen by design, and arm_FULL fails
  all three prongs in the same direction with wide margins. Had it failed narrowly this section
  would have to exist.
- **Nothing here says anything about future profitability**, of the incumbent or of any arm.

## Red team

Commissioned per V7 §G (Track-R numerical result bearing on a promotion decision). Verdict
filed verbatim under `red_team/`; corrections are ingested into this REPORT and never into the
frozen spec.
