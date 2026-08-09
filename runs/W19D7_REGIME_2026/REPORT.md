# W19D7 — **There is no 2026 regime break.** The market's break is in mid-2024, the profile change is a three-year trend, and the incumbent is degraded in the stub too.

> ⚠ **HEADLINES 1 AND 2 ARE WITHDRAWN (2026-08-09, post red team), AND THE ESTIMATED BOUNDARY IS
> 2024-08-05, NOT 2024-07-09.** The changepoint procedure's frozen 10% edge exclusion placed the
> entire 2026 stub outside the candidate set, so "no changepoint in 2026" was true by
> construction; a BIC comparison prefers a STEP over a trend for both profile variables; and an
> off-by-19 index bug shifted PC1's date. The title and body are left exactly as written per C7 —
> nothing is rewritten — but read **RED-TEAM INGESTION** at the foot of this file first. The
> corrected top-line finding is *stronger* than the original, not weaker.

Wave 19, Track R, **diagnostic — alpha budget 0**. Spec frozen and committed at `c345ada`
before any code existed. Owner directive R2.

---

## The answer, in five lines

1. **No market variable places a changepoint in 2026.** Six of eight detect a break; the latest
   is **2025-04-02** and the panel's principal component breaks at **2024-07-09**. The 106-session
   stub is not where the market changed.
2. **What the profile variables actually show is a monotone three-year trend, not a break** —
   and a step model fitted to a ramp lands in the middle of the ramp, which is what happened.
3. **The member-collapse hypothesis is REJECTED.** Effective ensemble diversity in 2026 is 3.52
   of 13, squarely mid-range against 3.37 / 3.61 / 3.93 / 3.78 for 2022-2025. The clamp binds
   far harder and the ensemble does not collapse.
4. **The incumbent IS degraded in the stub, and badly.** The Solar leg's 2026 Sharpe is
   **−0.387**; BEST_ONE_NQ's is **+0.073**; all three cross-instrument controls are negative.
   Only Product A stays clearly positive (**+0.659**), and that is a finding about diversification.
5. **The period is NOT novel.** Its nearest analog is **2025-04-25 .. 2025-09-19**, at the 88.6th
   percentile of nearest-neighbour distances against a 95th-percentile novelty bar.

**Against the pre-registered null**, this is a partial null and it must be read as one: the data
*can* locate boundaries, but **none of them is where the P&L concentration is**. The
concentration remains **UNEXPLAINED by a market-structure break**. What replaces the break story
is a slower and less dramatic one — a multi-year drift plus a hard-binding clamp — and the
report is careful below not to promote that from description to cause.

---

## (a) Where is the boundary? Estimated, and it is not 2026-01-01

Max-CUSUM single-shift model, block-bootstrap null (block 5, 1,000 replicates), location CI from
400 replicates of the fitted model, candidate locations restricted to the interior 10-90%.

| variable | max CUSUM | 95% null crit | p | detected | changepoint | 5-95% location CI | shift (sd) |
|---|---:|---:|---:|:--:|---|---|---:|
| v1 realised vol | 13.18 | 5.60 | 0.000 | ✓ | **2022-11-15** | 2022-10-31 .. 2022-12-23 | −0.98 |
| v2 vol-of-vol | 7.16 | 6.57 | 0.027 | ✓ | 2024-12-27 | **2023-05-16 .. 2025-07-31** | +0.46 |
| v3 range/close | 5.48 | 3.78 | 0.000 | ✓ | 2024-03-20 | 2023-11-03 .. 2024-10-22 | +0.32 |
| v4 return autocorr | 1.27 | 2.87 | 0.889 | ✗ | — | — | −0.10 |
| v5 excursion length | 2.57 | 2.88 | 0.102 | ✗ | — | — | −0.17 |
| v6 profile Spearman | 13.37 | 4.10 | 0.000 | ✓ | **2025-04-02** | 2025-03-12 .. 2025-04-14 | −0.90 |
| v6b profile peak/trough | 8.56 | 3.39 | 0.000 | ✓ | 2024-07-31 | 2024-06-20 .. 2024-09-20 | −0.51 |
| **PC1** (27.3% of variance) | 10.28 | 3.64 | 0.000 | ✓ | **2024-07-09** | 2024-06-14 .. 2024-08-01 | +0.62 |

Six of eight detect, so the spec's "the data cannot locate a boundary" clause does not fire and
the estimated boundary is **2024-07-09**, used for every downstream split. The 2026-01-02 cut is
retained alongside it and is **labelled a calendar convention throughout, never a finding.**

**The methodological caveat, and it is important enough to be part of the result.** The two
strongest detections are both profile-shape variables, and the yearly table shows them moving
**monotonically**, not stepping:

| | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---:|---:|---:|---:|---:|
| v6 profile Spearman vs the 2022-25 reference | 0.4446 | 0.4866 | 0.4505 | 0.3928 | **0.3370** |
| v6b profile peak/trough | 10.66 | 11.12 | 9.85 | 8.46 | **7.79** |
| v1 realised vol | 0.2320 | 0.1387 | 0.1378 | 0.1724 | 0.1813 |
| v5 excursion length (bars) | 22.65 | 23.16 | 22.85 | 22.07 | 21.88 |

A single-changepoint mean-shift model fitted to a ramp places its estimate near the ramp's
midpoint, and PC1's 2024-07-09 is consistent with exactly that. **The honest description is a
three-year flattening of the intraday volatility profile, continuing into 2026, not a
discontinuity anywhere.** The changepoint machinery answered the question it was asked; the
question turns out to have been slightly the wrong one, and the spec's insistence on estimating
rather than assuming the boundary is what exposed that.

The one variable with a genuinely large, sharp, tightly-bounded break is **v1 realised vol at
2022-11-15** (−0.98 sd, CI six weeks wide) — the end of the 2022 high-volatility period. It is
nowhere near the window under investigation.

## (b) What actually changed, from market variables only

The D5 rule binds hardest here and was obeyed: every variable above is a function of the NQ
price series alone. None touches any strategy's P&L, position, target, trade or fill — because
the thing being explained *is* a P&L pattern, and a P&L-derived feature would define the regime
as "the period where the strategy did badly" and be circular by construction.

Split at the estimated 2024-07-09 boundary, the shifts that clear |Welch t| > 4 are
**v6 profile Spearman (−0.75 sd, t = −13.1)**, **v6b peak/trough (−0.48 sd, t = −8.5)**,
**v2 vol-of-vol (+0.38 sd, t = +5.8)** and **v3 range/close (+0.25 sd, t = +4.1)**. Realised
volatility itself is flat across that boundary (t = −0.30) and return autocorrelation is flat
(t = −0.06).

So: **the level of volatility did not change; its intraday shape flattened and its variability
rose.** That is a coherent picture and it is consistent with what W18R1 found — the intraday
profile spans 11× — but it is a description of a slow drift, not an explanation of a 106-session
P&L episode, and this report does not offer it as one.

## (c) D1 — the ensemble does NOT collapse, and the clamp figure is now pinned down

| period | effective members (participation ratio, 13 = diverse) | all-13-agree | mean \|target\| | target at ±10 cap |
|---|---:|---:|---:|---:|
| 2022 | 3.370 | 0.894 | 2.852 | 2.76% |
| 2023 | 3.605 | 0.860 | 2.698 | 1.68% |
| 2024 | 3.933 | 0.885 | 2.586 | 1.62% |
| 2025 | 3.776 | 0.822 | 2.751 | 1.79% |
| **2026** | **3.521** | 0.808 | **2.933** | 2.21% |

**The pre-registered hypothesis is REJECTED.** If the clamp had collapsed effective diversity,
the participation ratio would fall materially in 2026 and the all-agree fraction would rise.
Neither happens: diversity is mid-range and agreement is at its *lowest*. Exposure does not
shrink either — 2026's mean |target| of 2.933 is the **highest of any year**.

**The clamp binding rate, reconciled across three definitions that were being used
interchangeably.** The standing figure quoted in the directives (9.8 / 0.2 / 3.9 / 18.3 / 39.2%)
had no written definition anywhere in the repo. It is now identified exactly:

| definition | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---:|---:|---:|---:|---:|
| member-bars pinned at the 1200t ceiling (all 13) | 3.39 | 0.22 | 2.22 | 6.59 | **12.94** |
| bars where **any** member is pinned | 13.61 | 2.81 | 7.96 | 21.41 | **50.64** |
| **bars where the widest member's uncapped 30×σ460 exceeds the ceiling** | **9.82** | **0.16** | **3.93** | **18.26** | **39.21** |

The third row reproduces the standing figure to two decimals. **It is the widest member's rate,
not the ensemble's**, and quoting it as "the clamp binding rate" overstates the ensemble-level
effect by roughly 3×. Filed as a standing caution.

What is true on any definition: in 2026 **half of all bars have at least one member pinned**,
against 2.8% in 2023 — an 18-fold change. The clamp is squeezing the ensemble from the top
without collapsing it: the widest members are truncated toward a common value while enough
distinct members remain below the ceiling to preserve diversity.

## (d) Is the incumbent degraded in the stub? **Yes — and that is the sentence the spec demanded.**

| object | 2022 | 2023 | 2024 | 2025 | **2026 stub (106 sess)** |
|---|---:|---:|---:|---:|---:|
| E10 Solar leg — Sharpe | 0.920 | 0.337 | 0.770 | 1.206 | **−0.387** |
| BEST_ONE_NQ v4 — Sharpe | 1.901 | 0.731 | 1.409 | 1.176 | **+0.073** |
| Product A v3 — Sharpe | 1.229 | 0.838 | 1.268 | 1.550 | **+0.659** |
| ES control — Sharpe | −0.218 | −0.995 | 0.643 | 0.585 | **−1.046** |
| RTY control — Sharpe | −0.711 | −1.364 | −1.632 | 0.384 | −0.090 |
| YM control — Sharpe | −0.738 | −1.758 | −0.574 | 0.583 | **−1.020** |

**The Solar core is materially degraded in the stub on every instrument it is run on.** This is
the single most consequential finding here, because it changes how Wave 18's two failures must
be read: challenger-versus-incumbent comparisons inside the stub are **low-power against a
degraded reference**, not evidence of specific challenger fragility.

**And it produces an unexpected positive.** Product A — the 60/40 blend of the tilted Solar leg
with the unchanged B-MOM leg — holds **+0.659 Sharpe and +$11,657** in the same window where the
Solar leg alone runs −0.387 and −$7,638. The diversification is doing its job precisely when the
primary engine is at its worst. That was never the design's stated purpose and it has never been
demonstrated before.

**Challenger-minus-incumbent, decomposed:**

| comparison | total | in stub | stub share | before break | after break, excl. stub |
|---|---:|---:|---:|---:|---:|
| M1 arm_FULL − control | −$31,902 | −$23,782 | **0.75** | −$16,194 | **+$8,073** |
| M5 NQ blend − control | +$59,579 | +$22,429 | 0.38 | −$11,094 | +$48,243 |
| M5 ES blend − control | +$33,545 | +$19,306 | 0.58 | +$15,506 | −$1,267 |
| M5 RTY blend − control | +$15,508 | +$12,128 | 0.78 | +$5,043 | −$1,662 |
| M5 YM blend − control | −$6,014 | −$7,295 | **1.21** | −$18,785 | **+$20,066** |

M1 was **helping** between the market break and the stub (+$8,073). YM — the instrument whose
negative sign decided M5's 2-of-3 sign count — is **positive** in that same interval (+$20,066)
and negative before the break and in the stub. That independently corroborates the M5 red team's
finding that *which* instruments agree is period-dependent, and it means the sign count was never
a stable property.

## (e) Is this period novel? No — it has a named, recent analog

Rolling 106-session windows, mean standardized market-variable vector, Euclidean distance,
non-overlapping earlier windows only. Nearest analogs to 2026-01-02 .. 2026-05-29:

| rank | window | distance |
|---|---|---:|
| 1 | **2025-04-25 .. 2025-09-19** | 0.683 |
| 2 | 2025-04-23 .. 2025-09-17 | 0.687 |
| 3 | 2025-04-24 .. 2025-09-18 | 0.688 |

The top five are all the same episode shifted by a day or two. The stub's nearest-neighbour
distance sits at the **88.6th percentile** of all windows' nearest-neighbour distances, below the
pre-registered 95th-percentile novelty bar: **NOT NOVEL**.

**Disclosed asymmetry in the test, in the conservative direction:** the target's nearest
neighbour is searched only among *earlier* non-overlapping windows, while the reference
distribution allows each window to look both ways. That biases the target's distance upward,
i.e. toward *more* apparent novelty. It came out not-novel anyway.

**What the analog buys, and it is the most actionable thing in this run.** Since no clean
out-of-sample data exists anywhere for this program (owner directive R1), a prior occurrence of
the same market state is the only route to out-of-sample evidence about this period's effect that
can be constructed. **Whether M1 and M5 also break in 2025-04-25 .. 2025-09-19 is a directly
testable question**, and it is proposed for Wave 20 — not run here, not scored here.

## What this run does NOT establish

- **No causation.** A market description co-occurring with a P&L pattern is co-occurrence. With
  one episode there is no way to separate "this market state breaks these mechanisms" from "these
  mechanisms broke and this market state is concurrent". Every statement above is descriptive and
  is meant to be read that way; any causal reading is a misreading, and the red team is instructed
  to hunt for causal language that slipped in.
- **No regime story was manufactured.** The pre-registered prohibitions were honoured: the
  boundary was estimated rather than chosen to maximise a P&L contrast, the variable list was
  fixed in the spec before any of it was computed, and the two variables that fail to detect
  (autocorrelation, excursion length) are reported with the same prominence as the six that pass.
- **PC1 explains only 27.3% of panel variance.** A single principal component is a weak summary
  of seven variables that are not strongly co-moving, and its changepoint should be read as one
  summary among several rather than as the regime date.
- **Nothing about future profitability**, of any object, on any instrument.

## Consequences, stated for the successor spec to inherit

1. **The successor selectivity spec must split at 2024-07-09, and must additionally report the
   2026 stub separately as a calendar convention.** The market boundary and the P&L boundary are
   different dates and conflating them is exactly the error this run exists to prevent.
2. **In-stub challenger comparisons are low-power, not adverse.** Any arm's in-stub result must be
   reported against a reference that is itself degraded, and the power implication must be stated
   before the run rather than discovered after.
3. **The 2025-04-25 .. 2025-09-19 analog is the Wave-20 test** and the only quasi-out-of-sample
   check this program can construct for this question.
4. **Standing caution:** "the clamp binding rate" has three definitions in circulation differing
   by ~3×; the figure quoted in the directives is the *widest member's* rate. Any future use must
   name which one it means.

## Seal audit

Run over this run's read manifest per owner directive R4; verdict and table in
`out/seal_audit.csv`, appended to the LOCKED-FORWARD ACCESS LEDGER.

## Red team

MANDATORY per the frozen spec, and commissioned. The reviewer is instructed to hunt for causal
language, attack the changepoint significance with alternative null models, test whether the
boundary survives variable selection, and **run** any de-confounding experiment it identifies
rather than flagging it — the practice that made Wave 18's reviews decisive.

---

# RED-TEAM INGESTION — appended 2026-08-09. **Two of the five headline lines are WITHDRAWN. Read this before anything above.**

Verdict: **CONFIRMED-WITH-CORRECTIONS, at the edge of REFUTED.** 18 defects — **3 headline-flipping**,
8 material, 6 disclosure, 1 cosmetic. Verdict verbatim at `red_team/RED_TEAM_d7_regime.md`,
unedited. The reviewer did what the brief asked and what makes these reviews decisive: it *ran*
the de-confounding experiments rather than flagging them. I re-verified every load-bearing claim
myself before accepting it.

## 1. WITHDRAWN — headline 1. The procedure **could not** have placed a break in 2026.

`src/panel.py:20` freezes `EDGE = 0.10`, so with n = 1,139 the last admissible changepoint index
is **1,024**. The 2026 stub begins at index **1,033**. **The entire 106-session window sits
outside the candidate set before any data is read.** Verified independently:

```
n 1139   EDGE 0.10 -> admissible [113, 1025]
index of 2026-01-02 = 1033   last admissible = 1024
STUB ENTIRELY OUTSIDE CANDIDATE SET: True
```

"No market variable places a changepoint in 2026" was therefore **true by construction**, and
the report stated it as an empirical finding. That is the single worst defect in this run and it
is mine: the edge exclusion was frozen in the spec on a legitimate statistical ground (the CUSUM
statistic blows up at the boundary) without anyone noticing it deleted the exact region under
investigation.

**The conclusion survives, for a reason the report never gave.** The reviewer re-ran at 2% and
5% edges and **every argmax is unchanged** — so no variable's best changepoint is in 2026 even
when 2026 is admissible.

**But a sharper correction comes with it.** Evaluated *at* the 2026 boundary rather than at the
argmax, the same statistic gives v6 **9.89** (crit 4.10), PC1 **5.87** (3.64), v6b **4.49**
(3.39). Three tests would "detect" a break there. **"The argmax is elsewhere" is not "nothing
happened here"**, and the report conflated them.

## 2. WITHDRAWN — headline 2. The model comparison says STEP, not trend.

The report asserts a "monotone three-year trend, not a break" and offers the ramp-fitted-by-a-step
argument to explain PC1's mid-2024 estimate. It never tested it. The reviewer did, and so did I:

| variable | BIC step | BIC trend | preferred |
|---|---:|---:|---|
| v6 profile Spearman | −5249.13 | −5175.32 | **STEP by 73.8** |
| v6b profile peak/trough | 3715.09 | 3744.42 | **STEP by 29.3** |
| v1 realised vol | −5744.77 | −5602.35 | **STEP by 142.4** |

(The reviewer reports 66.8 and 22.3 under its own BIC parameterisation; same direction, same
magnitude class.) A ramp-null simulation puts v6's estimate at the **93rd percentile** of where a
step estimator lands on a genuine ramp — i.e. v6 does not look like a ramp. PC1 and v6b are
consistent with the ramp reading; **v6, the strongest detection, is not.**

And the word "monotonically" is contradicted **by the report's own yearly table two lines below
it**: v6 runs 0.4446 → **0.4866** → 0.4505 → 0.3928 → 0.3370 and v6b runs 10.66 → **11.12** →
9.85 → 8.46 → 7.79. Both *rise* into 2023 before falling. The trend claim holds for 2023-2026 and
was overstated as a description of the whole window.

## 3. WITHDRAWN — the Product A "diversification" interpretation.

The report attributes Product A's stub performance (+0.659 Sharpe, +$11,657, against the Solar
leg's −0.387 and −$7,638) to the 60/40 diversification. The reviewer decomposed it from the
committed per-bar ledger (`smm_v3_bars.csv`: T / Tpp / B / phys) using the exact aggregation in
`SolarWaveSMMaster_v3.cs:348`:

- **The Solar leg *inside* Product A is +$6,079 / Sharpe +0.456 in the stub — positive**, not
  negative. It is not the same object as the plain E10 control.
- B-MOM contributes **+$8,886**.
- Of the ~$9k gap versus the plain E10 control, **+$7,243 comes from the short-halving overlay
  alone** (−$2,885 → +$4,358) against **+$1,721 from the tilt**.

The short-halving constant is a **fitted in-sample parameter**, not a diversification effect. So
the correct statement is: *Product A's stub resilience is roughly half a fitted overlay and half
a genuinely uncorrelated second engine, and the report attributed all of it to the second engine.*
The narrower claim that survives — B-MOM contributes positively in a window where Solar does not
— stands, but it is one of two mechanisms of comparable size, not the explanation.

## 4. A real index bug: the estimated boundary is **2024-08-05**, not 2024-07-09.

`panel.py:135-137` drops NaN rows before fitting PC1 (`Zf = Z.dropna()`), and `:154-156` maps the
resulting index back through the **full 1,139-row panel**. `v2_vol_of_vol` has 19 leading NaNs
from its 20-session rolling window, so the offset is exactly **19**. Verified:

| series | reported | **corrected** |
|---|---|---|
| PC1 | 2024-07-09 | **2024-08-05** (CI 2024-07-11 .. 2024-08-28) |
| v2 vol-of-vol | 2024-12-27 | **2025-01-24** |

The six variables with no NaNs are unaffected. **`REPORT.md`'s instruction to the successor spec
mandates the wrong date**, and two rows of the challenger-difference table flip sign at the
corrected boundary. Corrected here; the frozen spec is untouched per C6.

## 5. The detection rate is inflated, and there is no family-wise correction

The block-5 bootstrap null is **under-sized**. On no-change synthetic series with the same
autocorrelation, the exact procedure's false-positive rate is **0.30 at ρ = 0.7** and **0.99 at
ρ = 0.98**. `v2_vol_of_vol` — a 20-session rolling standard deviation with lag-1 autocorrelation
0.98 — detects only at block lengths below 10 and **fails Bonferroni**. Under a HAC-corrected
null, only **v6 and v6b** survive of the four shifts the report cites at the period split.

Eight tests were run at individual 95% bars with **no family-wise correction anywhere**. That is
a gap in the frozen spec, not an implementation error, and it is recorded as such. "Six of eight
detect" should be read as **two robust detections plus four that do not survive correction.**

## 6. The boundary is not robust to variable selection

Leave-one-variable-out re-estimation of the PC1 changepoint moves it by up to **545 days** —
dropping either v6 or v6b sends it to **February 2023** — against a location CI only **49 days**
wide. A quantity whose CI is 49 days and whose leave-one-out spread is 545 days is **weakly
identified**, and the report presented it as an estimate without saying so.

**Consequence for the successor spec, which supersedes what `REPORT.md` §"Consequences" says:**
the successor should split at the calendar year boundaries and at the 2026-01-02 convention,
report 2024-08-05 as a **weakly-identified** candidate boundary, and must not treat any single
estimated date as authoritative.

## 7. The "all-13-agree" statistic was the wrong one

`REPORT.md` says all-13-agree is "at its *lowest*" in 2026 (0.808). That is the **conditional**
statistic — conditioned on all 13 members being non-zero, which holds on only **2.7%** of bars.
On the spec's own **unconditional** definition it is **2.21% in 2026 — the second highest, +23%
over 2025 — which is the direction the member-collapse hypothesis predicts.**

**The rejection still stands**, on the participation ratio alone (3.52 in 2026 against
3.37/3.61/3.93/3.78, and the reviewer confirmed it survives bootstrap bands and an
equal-sample-size comparison, with the metric calibrating correctly at 1.00 for a fully collapsed
ensemble and 13.00 for a fully diverse one). But the supporting sentence was wrong and pointed
the opposite way from the honest statistic.

## 8. Two things the report should have found and did not — and the second is stronger than anything it did claim

**(a) My own pre-registered null had a second half that was never computed.** The spec requires a
test of whether "the period's standardized feature vector is an outlier against the rest of the
dev window". Mahalanobis D² of the stub window's mean vector = **11.29**, the **93.7th
percentile** among all 106-session windows — **not an outlier at the 95% bar.** (The reviewer gets
11.62 / 93.6th on its own centering; same conclusion.) The null's second half therefore also
returns *not unusual*, and the report omitted a test it had promised.

**(b) The market variables point the WRONG WAY.** Regressing the Solar leg's daily net on the
seven panel variables, fitted on 2022-2025 and used to predict the stub:

| | $/session |
|---|---:|
| in-sample mean actual (2022-2025) | **+110.68** |
| stub **predicted** from market variables | **+172.14** |
| stub **actual** | **−72.05** |

**The panel says the stub should have been better than average, and it was the worst period on
record.** That is a materially stronger result than "unexplained": the market state is not merely
uninformative about the concentration, it is *mildly favourable*, and the strategy lost money in
it anyway. Every regime-story reading is now excluded, not just unsupported.

## 9. What the reviewer tried to break and could NOT

- **`daily_from_fills` reconciles EXACTLY** — $175,798.80 for Product A and $303,239.64 for
  BEST_ONE_NQ against the committed NT8 nets — with flat-at-close verified (net quantity exactly
  zero at all 1,139 / 1,078 session ends) and the `hour >= 18` roll rule verified (no fill at
  18:00). The entire §(d) incumbent-decomposition table is sound, which is the highest-severity
  thing that could have failed and did not.
- **The v6 circularity attack failed completely.** Four alternative reference profiles, including
  one built from 2022 alone, reproduce the same yearly pattern. The trend is not an artifact of
  2022-2025 sessions contributing to their own reference.
- **The clamp identification is correct and unique among 28 candidate definitions tested.**
- **NOT NOVEL holds** at every window length from 40 to 180 sessions and under four distributional
  summaries — not just the mean-vector summary the run used.
- **Member-collapse rejection survives** bootstrap bands and equal-sample-size comparison.
- Location-CI coverage measured at **0.80-0.885** against a nominal 0.90 — mildly under-covering,
  disclosed rather than corrected.

## Revised disposition

**Headline 5 (not novel) and headline 4's factual core (the incumbent is degraded in the stub) are
untouched and are what this run establishes.** Headlines 1 and 2 are withdrawn as stated;
headline 3's rejection stands on a different statistic than the one cited.

**The corrected top-line finding is stronger than the original.** Not "no market break where the
P&L broke", which was an artifact of the candidate set, but: **the 2026 stub is not a multivariate
outlier (93.7th percentile, below the bar), is not novel (a named 2025 analog), and by a
regression on its own market variables should have been a mildly *better*-than-average period —
and it was the worst on record.** The concentration is not merely unexplained by market structure;
it runs opposite to what market structure predicts.

The one honest caveat on all of this, which the reviewer also raises: the panel explains little,
the detections are mostly not robust, and a seven-variable description of a market is a thin
instrument. "The variables point the wrong way" is a statement about *these* variables.
