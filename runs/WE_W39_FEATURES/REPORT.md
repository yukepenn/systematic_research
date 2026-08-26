# WE_W39 — FEATURE DISCOVERY · REPORT

Spec + amendments 1 and 2, each appended before its own arm was read.
**B1 PASS** on all three reads: W37's P1 reproduced at exactly 14.72 pts/session, Sharpe 0.311.
42 causal candidates in 8 information classes (`we_features.py`, lagged inside the module so a
caller cannot forget). Net $4.36/RT; stress $14.36/RT. No data ≥ 2026-08-01.

---

## Headline: the preregistered falsifier fired — and then the amendment found the result

**The quality layer is limited by its SCORING FORM's information content, not by feature
count.** Every way of using more features lost to the incumbent five. But amendment 2's
controls — run because the short side had just shown that a circular-shift pass can be
overturned — established what the layer actually is, which no earlier wave had done.

## 1. The universe is not empty (`FACT`)
7 of 42 long-side features clear |t| ≥ 2 against a chance expectation of 1.9. Three of the
incumbent five are in the top seven (`dist_open` +1 t 2.69, `prev_ret` −1 t 2.27,
`dist_vwap` +1 t 2.01); the strongest genuinely new ones are `body_share` (−1, t 2.58) and
`rv_expansion` (−1, t 2.22). *(Full-window screen — DIAGNOSTIC ONLY; no adopted arm uses it.)*

## 2. Feature selection is noise, and it is not the ranking's fault (`SUPPORTED`)

| arm (adoption window 2023-07 → 2026-08) | pts/session | worst week | Sharpe | wk÷\|worst\| |
|---|---|---|---|---|
| **Q0 incumbent five** | **16.91** | −$7,418 | **0.331** | **0.229** |
| Q1 quarterly top-5 re-selection (**62 % churn**) | 16.03 | −$9,888 | 0.305 | 0.163 |
| Q5 quarterly t ≥ 2 admission (**80 % churn**) | 13.33 | −$9,700 | 0.309 | 0.138 |
| Q6 core five + admitted | 15.69 | −$9,700 | 0.326 | 0.162 |
| Q2 all 42, continuous, zero thresholds | 16.22 | −$9,070 | 0.282 | 0.180 |
| Q3 continuous size, cap 3 (avg 2.00 contracts) | 21.44 | −$10,698 | 0.314 | 0.201 |
| BASE no quality layer | 11.94 | −$7,487 | 0.321 | 0.160 |

My own hypothesis in amendment 1 — that Q1's churn was an artifact of forcing a top-5 pick
among near-ties — was **refuted**: threshold admission churns *worse* (80 %) and admits **zero**
features in 2 of 12 quarters. Feature information itself is unstable quarter to quarter.

## 3. A refinement of the W19/W20 aggregation prior (`INFERENCE`, mechanism)
Q2 aggregated over all 42 features with no selection and **lost** — the opposite of what
aggregating over 32 configs did in W20. The distinction is not "aggregate vs select":

> **Aggregation helps when the members are noisy estimates of the SAME quantity** (32 variants
> of one working rule). **It hurts when the members are candidates for DIFFERENT quantities**
> (42 heterogeneous features, most of which carry nothing) — the informative few get diluted.

The prior "selection is noise, aggregate instead" is scoped to the former case from now on.

## 4. Continuous size is leverage — 4th confirmation, new form (`REPRODUCED`)
Q3 has the highest production of any arm (21.44 pts/session) — at avg **2.00** contracts, with
eff 0.201 against Q0's 0.229 at 1.19. More size resolution bought exposure, not edge.

## 5. Class attribution: no class is load-bearing, and FLOW is harmful (`SUPPORTED`)
Leave-one-class-out on Q2: dropping any of 7 classes moves it within ±0.6 pts, but dropping
**flow** (6 features) *lifts* it 13.69 → 15.93 pts and eff 0.151 → 0.172. Consistent with W13's
"delta gate is weak (p = 0.10)" and W15's finding that our delta proxy correlates only 0.28
with true BidAsk delta.

## 6. What the layer actually is — amendment 2's controls (`FACT`, this is the wave's value)

The layer had only ever faced circular-shift nulls. Two controls it had never faced:

| control (full window, 100 draws) | pts/session | eff | Sharpe |
|---|---|---|---|
| base, all size 1 | 10.62 | 0.142 | 0.305 |
| **C1 null** — random 20 % sized up | 12.03 | 0.141 | 0.279 |
| **C2 null** — five RANDOM features, identical rule | 12.62 | 0.152 | 0.284 |
| **real quality layer** | **14.72** | **0.198** | **0.311** |
| percentile vs C1 | **97.0** (p 0.030) | **100.0** (p 0.000) | 94.0 (weak) |
| percentile vs C2 | **95.0** (p 0.050) | **97.0** (p 0.030) | 90.0 (weak) |

Reading, in the order the amendment declared:
- **C1 passes → the layer is NOT leverage.** Sizing up the *right* 20 % of flips beats sizing
  up a *random* 20 % at the 97th–100th percentile. The 14.72 headline stands.
- **C2 passes → the specific five features do work**, and they carry **most** of the genuine
  gain: random sizing alone reaches 12.03 (pure exposure), a random five-feature score reaches
  only 12.62, the incumbent five reach 14.72. On the owner's metric the split is starker —
  0.141 (leverage) → 0.152 (random features) → 0.198 (incumbent).
- **Sharpe is only "weak" against both controls (94th, 90th)** — exactly as W36 predicted:
  Sharpe penalises the upside variance this layer deliberately adds, so it is the wrong gate.

**Residual caveat that must travel with C2** (`WEAK`, stated plainly): the incumbent five were
selected on the full window in W33, so part of their 97th-percentile margin is that selection.
C2 cannot separate "these features carry information" from "these features were picked on this
sample". What *is* independent: W36's quarterly walk-forward kept the same features and refit
only thresholds, reaching 14.41 — so the features transfer across time inside the sample.
And §2 shows re-picking them destroys more than it gains.

## 7. Short side, better powered, and rejected on the binding null (`FALSIFIED`)
2,225 short entries (vs W38's 1,298 SEL): **5 of 42 clear t ≥ 2**, led by
**`delta_accel` (−1, t = 3.83)** — the strongest single feature t on either side — then
`path_eff` +1, `prev_range_rel` −1, `skew60` −1, `rv_expansion` +1.
The continuous short arm looked adoptable under the corrected (exposure-neutral) criteria:
$1,118/wk vs $875/wk for the base scaled to the same 1.46 contracts, eff 0.094 vs 0.073.
Then:

| null | verdict |
|---|---|
| N1 circular shift | 100th percentile, p = 0.000 — EVIDENCE |
| **N2 count-matched random sizing** | **69th percentile, p = 0.310 — NOT EVIDENCE** |

Randomly sizing up the same number of short entries does as well. **Rejected.** W38's short
conclusion stands unchanged — and this is the case that justified running C1/C2 on the long
side at all.

## 8. Portfolio, at time-weighted matched exposure (contract-minutes)

| full-window object | weekly | wk + % | worst week | CVaR5 | Sharpe | eff |
|---|---|---|---|---|---|---|
| long Q0 ×1 | $1,470 | 58.6 % | −$7,418 | −$5,398 | 0.311 | **0.198** |
| **long Q0 ×1.91 (matched)** | **$2,807** | 58.6 % | −$14,170 | −$10,311 | 0.311 | **0.198** |
| long Q0 + S-cont short | $2,557 | **64.4 %** | −$14,606 | −$10,097 | **0.337** | 0.175 |
| long Q0 + S0 short | $2,048 | 63.4 % | −$12,588 | −$8,636 | 0.320 | 0.163 |

Third independent confirmation of W38: **scaling the long object beats adding a short sleeve**
on both money and tail; the pair buys weekly consistency and Sharpe only.

## 9. Two corrections this wave made to its own method
- **The worst-week gate was exposure-naive** and rejected an arm that beat its reference at
  matched exposure. Primary criteria are now eff and CVaR efficiency (both exposure-invariant);
  the absolute worst week is reported, never gated.
- **Exposure matching is now time-weighted** (contract-minutes), not trade-count-weighted.

## 10. Where this sends the campaign
Feature mining is **not** the lever: the incumbent five already sit at the 97th percentile of
what feature choice can deliver, and every re-selection scheme loses. The remaining route to
the owner's objective is **diversification that lowers the tail**, which is W40 — and the
arithmetic says so plainly: at today's eff of 0.198–0.232, $10,000/week means a worst week
near −$43k. Raising eff, not raising contracts, is the research job.
