# W18R1_M1_VOLSEASON — **arm_FULL FAILS all three gates.** The premise is right; the implementation of it, through the frozen state machine, is not.

> ⚠ **THE SECOND HALF OF THE TITLE IS WITHDRAWN (2026-08-09, post red team).** The reviewer ran
> both de-confounded constructions this report queued as future work, and **both are worse**.
> The axis closes **unconditionally**, not "pending a better implementation". The title and body
> are left in place per C7 — nothing is rewritten — but read **RED-TEAM INGESTION** at the foot
> of this file before anything else.

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

---

# RED-TEAM INGESTION — appended 2026-08-09. **Two headline-flipping corrections. Read this before anything above.**

Verdict: **CONFIRMED-WITH-CORRECTIONS.** 17 defects — 2 headline-flipping, 7 material,
6 disclosure, 2 cosmetic. Full verdict filed verbatim at
`red_team/RED_TEAM_m1_volseason.md`; nothing in it was edited. Corrections are ingested here
and never into the frozen spec (C6). I verified the three load-bearing findings myself before
accepting them (`src/diagnostics_post.py`, `out/redteam_verification.json`,
`out/yearly_breakdown.csv`) rather than taking the reviewer at face value.

## 1. RETRACTED — "the null is CONDITIONAL". It is not. The axis closes unconditionally.

The section above hedges the null on the S-freeze confound and queues two de-confounded
constructions as future work. **The reviewer ran both.** They take eight seconds each, and I
should have run them rather than queueing them.

| construction | Sharpe | CDaR₀.₉₅ | gates |
|---|---:|---:|:--:|
| control (sigma460) | 0.709 | $27,162 | — |
| `arm_FULL` (as run) | 0.558 | $35,498 | 0/3 |
| `f / E[f given flip]` — exposure-neutral by construction; flips restored to 67,765 vs control's 58,701 | **0.411** | **$40,759** | **0/3** |
| per-bar `S` resampling in BOTH arms — the clean re-allocation test; mean `s_eff` confirmed unchanged (114.97 vs 109.49) | ΔSharpe **−0.303** | ΔCDaR **+$19,353**, P(ΔSharpe>0) = **0.116** | fails |

**Removing the confound makes the mechanism WORSE, not better.** Both of the "structurally
different constructions" I queued for a later wave are therefore **CLOSED here, on evidence**,
and they must not be carried into Wave 19 as a ranked lead. Intraday seasonal normalization of
the Solar threshold is dead on this substrate, full stop — not "dead pending a better
estimator".

The reviewer's counterfactual also **strengthens** the root-cause diagnosis well beyond the
evidence I offered: with per-bar `S` resampling the flip count moves **+8.1%** instead of
−45.9%, and re-allocates exactly as the mechanism predicted — EVENING **+181%**, OVERNIGHT
**+39%**, RTH **−31%**. The diagnosis was right; the conclusion I drew from it was not.

## 2. RETRACTED — the §5 axis declaration. In effect this WAS an exposure change.

The spec declares (and the section above repeats) that nothing in M1 touches position size.
Measured, `arm_FULL`:

| | control | arm_FULL | Δ |
|---|---:|---:|---:|
| mean ensemble absolute target | 2.741 | 1.894 | **−30.9%** |
| fraction of bars flat | 18.9% | 35.3% | +16.4 pts |
| contracts/day | 43.9 | 25.7 | −41% |
| net | $119,009 | $87,107 | −26.8% |

Net falls **26.8%** against **31%** less exposure — **net per unit of exposure is essentially
unchanged.** A threshold change that removes a third of the exposure is a de-risking rule
implemented through a threshold, whatever its stated intent. That is the axis §5 presumes
exhausted, and this result is entirely consistent with that presumption. The declaration was
made in good faith and it was wrong in effect; the honest reading is that M1 tested the
exposure axis by accident, twice over (this, and the 64% threshold widening).

## 3. RETRACTED — "fails all three prongs with wide margins."

The section above says no uncertainty quantification was needed because the margins were wide.
That was wrong, and it repeats the exact error the Wave-17 red team caught on the 2026 claim.
My own bootstrap (block=5, B=10,000, seed=20260808), independent of the reviewer's:

- **ΔSharpe = −0.150, 5–95% [−0.637, +0.331], P(ΔSharpe>0) = 0.303.** Not distinguishable
  from zero. (The reviewer reports 0.277 on their own construction; same conclusion.)
- **74.5% of the −$31,902 gap sits in the 106-day 2026 stub.** `arm_FULL` **beats** the
  incumbent in 2024 (Sharpe 0.967 vs 0.770) and in 2025 (1.290 vs 1.206); 2023 and 2026 carry
  the whole deficit.
- A structurally uniform mechanism cannot produce a gap 75%-concentrated in 9% of the days.
  I measured a **mechanism** and presented it as a **P&L attribution**.

The verdict itself is unchanged — the AND rule is a point-estimate screen on pre-registered
definitions and `arm_FULL` fails all three as defined — but its **strength** is much weaker
than the report claimed, and correction 1 is what actually closes the axis, not this.

## 4. The top-10 retention gate is a date-matching artifact; the number to quote is 100.9%

`arm_FULL`'s own ten best days sum to **$119,005** against the control's **$117,986** —
**100.9%**. The 80.5% figure comes from re-reading `arm_FULL`'s P&L **on the control's dates**.
The gate is the house-frozen definition and the verdict stands under it, but "M1 destroys
right-tail capture" is **not** what the data says: it says M1's big days land on different
days. This figure was sitting unremarked in the run's own `metrics.csv`.

## 5. The best headline in the run, and I never stated it

**81% of the loss is in the OVERNIGHT cohort — the one the mechanism was designed to fix**
(+$33,379 → +$7,548). The intervention did its most damage precisely where its author expected
its benefit. That is a cleaner and more damning statement of the failure than anything in the
original write-up.

## 6. The premise test is close to tautological, and the 1.5 bar was a straw man

Across slots, `corr(r_s, mean|Δclose|) = 0.9985` — `r_s` is very nearly the raw volatility
profile divided by a near-constant, so the "premise test" largely re-measures the thing it was
meant to test independently. A pure-noise series with the same variance profile reproduces
**9.79×** of the 11.04× headline. Intraday volatility seasonality in index futures was never in
dispute; a falsification bar of 1.5 could not have failed. **The D4 profile stands as a
descriptive result** — the cohort P&L table is measured, not inferred — but it should never
have been framed as a stringent test of anything.

## 7. Corrections to specific numbers

- **"flips fall 46% in every cohort"** (as written in `CURRENT_TRUTH.md`) is wrong. The −46% is
  the total; per cohort it is **−32.6% / −19.7% / −57.5%**. The REPORT above states both
  correctly; the truth-doc summary compressed them into a false claim.
- **"mean S +64%"** is weighted by time-in-trend and is therefore partly an *effect* of the flip
  collapse rather than a cause of it. **Flip-weighted — the threshold the machine actually
  chooses — it is 79.58 → 110.52 points, +38.9%.** Both are now in
  `out/root_cause_S_freeze.csv`.
- **Clamp contamination, quantified for the first time:** member-bars pinned at the 1,200-tick
  ceiling rise from **4.0% to 29.7%**. Nearly a third of `arm_FULL`'s decisions are made at the
  clamp, not by the mechanism — a further confound nobody had measured.
- **The SMV2AD analogy is imperfect** and the report overstates it: clamp-widening *raised*
  Sharpe in SMV2AD, whereas this lowers it. Related, not identical.

## 8. Process defects, and they are mine

- `root_cause_S_freeze.csv` and `warmup_convergence.csv` were produced by inline shell commands
  with no committed script. Fixed: `src/diagnostics_post.py` regenerates both, plus the
  verification above. `control_crosscheck.json` likewise carried a key the committed script did
  not emit, because I fixed the dtype bug inline before fixing the script.
- `REPORT.md` did not exist when the reviewer began, though `CURRENT_TRUTH.md` and the registry
  already cited it as where the C6 correction was filed. It was written afterwards. The
  citation was true when the reader got there and false when it was made.

## 9. What the reviewer tried to break and could NOT

The causality of the seasonal estimator, which was the highest-value target. It was
re-implemented from scratch with a structurally different algorithm and compared bar-for-bar:
**maximum absolute difference 0.0 across all 519,714 bars**, zero bars differing by more than
1e-12. Session boundaries, the 60-session warmup (exactly 27,440 bars), the 43 early closes,
the 13 gapped sessions, unobserved slots and `E[f] = 1` all check out. Gates reproduce to the
last decimal. The control rebuild matches SMV2AD to the cent including contract counts. The
dtype fix is real and **no other merge in the codebase has the same latent bug** — all 16 sites
were audited. `arm_HALF`'s disclosure-only status was honoured with no leakage into any
conclusion.

## Revised disposition

**Intraday seasonal normalization of the Solar decision threshold is CLOSED, unconditionally**,
across all three constructions tested (multiplicative session-mean-1, exposure-neutral
flip-normalised, and per-bar resampled). No further bite without a mechanism that is not a
re-weighting of the same threshold. **The "when is S sampled" lead that this report proposed
for Wave 19 is withdrawn** — the reviewer already tested it and it is worse.

What survives, and it is not nothing: the **D4 cohort structure** (RTH is 34.6% of bars and
81.2% of P&L; the evening quarter loses $10,989), the **clamp-contamination measurement**, and
the finding that the incumbent's exposure and its net scale together almost exactly — which is
independent support for §5's presumption that the exposure axis is exhausted.
