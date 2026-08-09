# W19D7 — **There is no 2026 regime break.** The market's break is in mid-2024, the profile change is a three-year trend, and the incumbent is degraded in the stub too.

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
