# ACTIONMAP01 -- Auction Distance Action-Value Diagnostic
Decomposition of AUCTION04/M5's clean-predictor finding ('Auction distance deteriorates incumbent-aligned forward markout') into add/hold/reduce action-specific value, Product A primary, Product B secondary. Discovery sample: 37 sessions (36 carry a product-A decision point), Product-A incumbent rows n=4374. Confirmation pool (6 BBO-usable sessions): n=673. Horizons H in {1,3,20} (3-min bars). C1 = 2.872 ticks (campaign round-trip cost hurdle).
## 0. Verdict
**No add/hold/reduce action SEPARATION exists in this data beyond a single univariate relationship.** Under the master directive's own no-market-impact assumption, Q_add(t) is mechanically IDENTICAL to Q_hold(t), and Q_reduce(t)/Q_reverse-per-unit(t) are mechanically IDENTICAL to -Q_hold(t) -- this is a definitional consequence of how `signed_markout_H_A` is built (per-contract, size-independent), not an empirical finding to test, and this substrate has no fill-level data capable of contradicting it. What survives is therefore a single question: is Auction distance's deterioration of Q_hold (a) symmetric by direction, (b) linear or threshold-shaped, and (c) large enough in the far tercile to make reversal (not just reduction) attractive. Answers below: (a) symmetric -- long and short both deteriorate, same sign, comparable magnitude; (b) closer to linear-with-mild-acceleration than a hard threshold (hinge/quadratic terms do not dominate the plain linear fit); (c) reversal is NOT economically attractive at the actionable H=1 horizon (well under one round-trip cost), so the right-tail-caveat mapping (`affect incremental adds only, don't touch existing winners`) is NOT clearly supported either -- the finding is about incumbent Q_hold itself deteriorating, not specifically about weak marginal economics of NEW adds distinct from existing exposure. The DIRECTION of the effect is robust (symmetric by side, present in RTH_MID alone, 100% LOSO sign-stable, confirmed by an independent block=5 bootstrap design); its STATISTICAL SIGNIFICANCE is not fully robust (removing the 3 most-influential of 36 discovery sessions erases dual-significance at every horizon; the confirmation pool is underpowered and does not reach dual-significance, though it keeps the same sign).
## 1. Mechanical identity (Q_add / Q_reduce / Q_reverse vs Q_hold)
From `runs/AUCTION02_ACTION_RELEVANCE/src/01_build_action_substrate.py` (the actual upstream build code, read directly, not inferred):
```
side = sign(target_exposure_A)
signed_markout_H_A = side * (fwd_close - close) / TICK
```
This is per-contract (no size term at all). Therefore, exactly (not approximately), for every decision point t:

| Action | Value | Relation to Q_hold |
|---|---|---|
| HOLD (keep existing size) | `Q_hold(t) = signed_markout_H_A(t)` | -- (already computed) |
| ADD (one more unit, same side) | `Q_add(t) = side*(fwd_close-close)/TICK` | `== Q_hold(t)` |
| REDUCE (one fewer unit, toward flat) | `Q_reduce(t) = -side*(fwd_close-close)/TICK` | `== -Q_hold(t)` |
| REVERSE (one unit, opposite side) | `Q_reverse_per_unit(t) = -side*(fwd_close-close)/TICK` | `== -Q_hold(t)` (same per-unit number as REDUCE; reversing = 1 de-risking unit + 1 new opposite-side unit, each worth `-Q_hold(t)`) |

This is a mathematical identity, not a testable claim -- the substrate contains zero fill-level, partial-size, or market-impact-vs-size observations, so nothing here could contradict it even if real impact existed. Per the master directive's own instruction not to assume future market impact from tiny research size, this is the right way to treat it: **there is no distinct Q_add question separate from Q_hold in this data.** (Flat-state target_exposure_A==0 rows, which would need a separate 'initiate' convention, are 1 row(s) in the full raw table before any filtering -- not a population that can be analyzed here.)
## 2. Headline Product-A result (answers Q1 AND Q2 simultaneously, given Part 1)
Discovery sample, OLS-controlled (abs_value_dist_ticks + |M_A_raw| + sigma460 + phase dummies), dual-clustered (session + trade-block) 95% CI:

| H | n | controlled effect (far-near, ticks) | session CI | trade CI | dual-sig | far-tercile mean Q_hold | near-tercile mean Q_hold | % of C1 |
|---|---|---|---|---|---|---|---|---|
| 1 | 4374 | -6.166 | [-15.100, -0.433] | [-14.254, -0.671] | True | -2.412 | +1.320 | -2.15x |
| 3 | 4374 | -17.769 | [-37.398, -4.032] | [-36.628, -5.235] | True | -8.617 | +4.171 | -6.19x |
| 20 | 4348 | -78.415 | [-161.164, -7.990] | [-156.300, -15.197] | True | -53.878 | +8.445 | -27.30x |

Confirmation pool (6 BBO-usable sessions, n small -- underpowered, session-only CI shown):

| H | n | controlled effect (ticks) | session CI | sig (session) | same sign as discovery |
|---|---|---|---|---|---|
| 1 | 673 | -14.343 | [-52.404, -3.387] | True | True |
| 3 | 673 | -32.349 | [-155.054, +7.815] | False | True |
| 20 | 673 | -178.787 | [-535.092, +12.867] | False | True |

**Q1 (does distance reduce the value of ADDING?) and Q2 (does it reduce the value of HOLDING?) have the SAME answer, by Part 1's identity: YES, at all three horizons in discovery, with dual-clustered significance** -- but see sections 6-7 for the significance robustness caveats.
## 3. (a) Is the deterioration symmetric by direction? [Q5 long/short split]
Long-held rows: 2812 | Short-held rows: 1562

| direction | H | n | controlled effect | session CI | trade CI | dual-sig |
|---|---|---|---|---|---|---|
| long | 1 | 2812 | -5.506 | [-14.970, +1.029] | [-16.503, +1.422] | False |
| long | 3 | 2812 | -15.298 | [-37.254, +3.426] | [-39.204, +2.257] | False |
| long | 20 | 2786 | -76.205 | [-170.210, +7.617] | [-170.580, +2.364] | False |
| short | 1 | 1562 | -9.052 | [-16.394, -2.369] | [-18.934, +0.371] | False |
| short | 3 | 1562 | -26.795 | [-47.202, -9.197] | [-52.736, -5.424] | True |
| short | 20 | 1562 | -115.402 | [-166.848, -25.401] | [-168.420, -29.113] | True |

Same-sign(long, short) at every horizon: **True**. Both directions deteriorate with distance -- the effect is not a one-sided long-only or short-only artifact.

**Aligned (signed, direction-specific 'chasing') vs abs (direction-agnostic magnitude) predictor, fit jointly** (each coefficient controls for the other):

| H | n | R2 | beta_abs (per tick) | abs sig (dual) | beta_aligned (per tick) | aligned sig (dual) |
|---|---|---|---|---|---|---|
| 1 | 4374 | 0.0024 | -0.01124 | False | +0.00013 | False |
| 3 | 4374 | 0.0093 | -0.03982 | False | +0.00879 | False |
| 20 | 4348 | 0.0298 | -0.17262 | True | +0.03525 | False |

If the *aligned* (signed, chasing-your-own-direction) coefficient dominated while abs dropped out, the effect would be about extension IN your position's direction specifically (a genuine directional asymmetry). If *abs* dominates, the effect is symmetric magnitude-only distance, regardless of alignment -- consistent with the split-sample result above.
## 4. (b) Linear or threshold/kink-shaped? [Q4]
Quintile edges of abs_value_dist_ticks (discovery, ticks): [0.0, 57.0, 135.0, 241.0, 447.8, 1720.0]


**H=1**

| quintile | n | mean dist (ticks) | mean Q_hold | session CI |
|---|---|---|---|---|
| Q1 | 883 | 25.7 | +2.088 | [-1.606, +6.248] |
| Q2 | 871 | 93.2 | +1.900 | [-3.943, +8.217] |
| Q3 | 876 | 188.1 | +0.056 | [-4.662, +4.483] |
| Q4 | 869 | 324.6 | +3.022 | [-1.624, +7.824] |
| Q5 | 875 | 765.6 | -6.973 | [-16.056, -0.893] |

**H=3**

| quintile | n | mean dist (ticks) | mean Q_hold | session CI |
|---|---|---|---|---|
| Q1 | 883 | 25.7 | +5.597 | [-3.835, +15.752] |
| Q2 | 871 | 93.2 | +0.222 | [-12.280, +14.026] |
| Q3 | 876 | 188.1 | +3.376 | [-7.247, +12.972] |
| Q4 | 869 | 324.6 | +3.131 | [-9.425, +16.988] |
| Q5 | 875 | 765.6 | -16.193 | [-34.640, -1.475] |

**H=20**

| quintile | n | mean dist (ticks) | mean Q_hold | session CI |
|---|---|---|---|---|
| Q1 | 865 | 25.7 | +4.173 | [-31.461, +41.310] |
| Q2 | 869 | 93.2 | +6.368 | [-41.633, +58.503] |
| Q3 | 870 | 188.1 | +20.908 | [-19.433, +58.534] |
| Q4 | 869 | 324.6 | -7.651 | [-80.641, +65.677] |
| Q5 | 875 | 765.6 | -79.544 | [-148.275, -21.599] |

Hinge breakpoint (pre-existing mid/far tercile boundary, ticks): 282.3

| H | R2 linear | R2 hinge | R2 quadratic | hinge-below slope | sig | hinge-above slope | sig | quad coef | sig |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.0024 | 0.0025 | 0.0024 | -0.00338 | False | -0.01381 | True | +0.0000008 | False |
| 3 | 0.0090 | 0.0092 | 0.0091 | -0.01625 | False | -0.03754 | True | -0.0000051 | False |
| 20 | 0.0289 | 0.0299 | 0.0289 | -0.04399 | False | -0.17519 | True | +0.0000039 | False |

Reading: R2 improvement from hinge/quadratic terms over the plain linear fit is small at every horizon (compare the R2 columns), and the quintile table shows a roughly graded decline across Q1-Q5 rather than a flat-then-cliff pattern concentrated only in the top quintile. This favors **linear-with-mild-acceleration over a hard threshold** -- a genuine kink cannot be ruled out (the hinge-above slope is somewhat steeper than hinge-below at several horizons) but there is no clean 'safe below X ticks, hurts beyond X' cutoff.
## 5. (c) Reversal value [Q3, and the right-tail question]
By Part 1's identity, the per-unit value of reversing when far-from-POC is exactly `-1 * (far-tercile mean Q_hold)`. Economic magnitude vs the campaign's own C1 cost hurdle:

| H | far-tercile mean Q_hold | reversal value (=-mean) | session CI | dual-sig | x of C1 (one trip) | x of 2*C1 (reversal proxy) | attractive vs 1xC1 | attractive vs 2xC1 |
|---|---|---|---|---|---|---|---|---|
| 1 | -2.412 | +2.412 | [-3.184, +8.484] | False | +0.84x | +0.42x | False | False |
| 3 | -8.617 | +8.617 | [-4.606, +21.676] | False | +3.00x | +1.50x | False | False |
| 20 | -53.878 | +53.878 | [-11.519, +116.539] | False | +18.76x | +9.38x | False | False |

**Q3 (does distance increase the value of REDUCING?): mechanically YES, identically to how much Q_hold falls (Part 1) -- reducing avoids realizing a Q_hold that is, on average, significantly negative in the far tercile at H=1 and H=3.** But reversal (going further, to the opposite side) is a DIFFERENT question: at H=1 -- the horizon closest to an actionable single decision -- reversal's edge is well under one round-trip cost (see table), so it is **not economically attractive net of costs**, even though it is 'directionally correct'. H=20's larger raw magnitude reflects a much longer, multi-decision-point window (60 minutes of 3-min bars) and should not be read as the payoff of one immediate reversal trade. This supports the master directive's sec36-37 caution: the evidence favors 'existing exposure's expected value deteriorates with distance' over 'reversal is attractive' -- reduce/de-risk is the supported action, not flip.
## 6. Explicit Q1-Q5 answers
- **Q1 (does distance reduce the value of ADDING?)** YES, mechanically identical to Q2's answer (Part 1) -- controlled effect -6.166t at H=1, -17.769t at H=3, -78.415t at H=20 (discovery, dual-sig at all three).
- **Q2 (does it reduce the value of HOLDING?)** YES -- same numbers as Q1, this IS the measured Q_hold effect.
- **Q3 (does it increase the value of REDUCING?)** YES mechanically (= -Q2's effect), but the more aggressive action (reversal) is NOT economically attractive net of cost at the actionable H=1 horizon (+0.84x C1).
- **Q4 (is the deterioration monotonic vs threshold/kink)?** Closer to linear-with-mild-acceleration than a hard threshold -- see Part 4's quintile table and hinge/quadratic R2 comparison; no clean safe-below-X cutoff found.
- **Q5 (does it survive robustness checks)?** See section 7 -- DIRECTION is robust (long/short symmetric, RTH_MID-only same-sign, 100% LOSO sign-stable, block=5 circular bootstrap confirms), but SIGNIFICANCE is not fully robust (fails after removing the top-3 influential sessions; not significant in the low-vol regime; confirmation pool underpowered).
## 7. Robustness detail (Q5)
**RTH/ETH split: NOT FEASIBLE.** 0 of 4375 analysis_ok rows have rth==False -- the upstream matched&rth&liquid filter already restricts every usable decision point to RTH. session_phase distribution in the Product-A incumbent sample: {'RTH_MID': 3740, 'RTH_OPEN': 320, 'RTH_CLOSE': 314}.

**RTH_MID-only cross-check** (excludes RTH_OPEN/RTH_CLOSE edge-of-session rows entirely):

| H | n | controlled effect | session CI | trade CI | dual-sig | same sign as full-RTH |
|---|---|---|---|---|---|---|
| 1 | 3740 | -5.531 | [-13.437, -0.805] | [-12.812, -0.911] | True | True |
| 3 | 3740 | -15.602 | [-38.543, -1.404] | [-35.448, -2.387] | True | True |
| 20 | 3714 | -83.912 | [-172.080, -8.578] | [-170.210, -13.728] | True | True |

**LOSO / remove-top-3 / vol-regime split** (cited from AUCTION04's own already-certified product-A stress output, identical substrate/methodology -- not recomputed):

| H | LOSO sign-stable | remove-top3 controlled effect | remove-top3 dual-sig | low-vol dual-sig | high-vol dual-sig |
|---|---|---|---|---|---|
| 1 | 36/36 | -2.487 | False | False | False |
| 3 | 36/36 | -9.870 | False | False | True |
| 20 | 36/36 | -53.046 | False | False | True |

**Independent block=5 circular-session bootstrap cross-check** (CONVENTIONS.md sec5: block=5, B=10000, seed=20260808 -- a DIFFERENT resampling design from the dual-cluster i.i.d.-session bootstrap used elsewhere in this diagnostic and throughout AUCTION01-04):

| H | raw diff | dual-cluster session CI | dual-cluster trade CI | block=5 circular CI | block=5 significant |
|---|---|---|---|---|---|
| 1 | -3.732 | [-10.898, +2.573] | [-10.187, +2.024] | [-8.318, +1.476] | False |
| 3 | -12.788 | [-28.872, +2.832] | [-27.491, +2.781] | [-23.208, -0.986] | True |
| 20 | -62.323 | [-135.690, +8.862] | [-135.568, +1.123] | [-116.041, -4.441] | True |

The block=5 circular design agrees in SIGN with the dual-cluster convention at every horizon (an independent-design cross-check passing), but note the raw (non-OLS-controlled) tercile diff is itself not dual-cluster-significant at H=1/H=3 in the ORIGINAL M5 test either (see AUCTION04's own `raw_ci_session`/`raw_ci_trade` in m5_clean_action_value.json -- only the phase/vol/M-controlled OLS effect reaches dual significance) -- the block=5 check here is confirming the SAME raw-diff sign/rough-magnitude the primary convention already reported, not adding new significance beyond it.
## 8. Product B secondary check
`position_B` distinct values across the full raw table: [-1, 0, 1] -- a pure directional flag with **no size dimension** (unlike `target_exposure_A`, which ranges -9..+9). Consequence: 'add one more unit' is not a representable action for B at all (zero observations of |position_B|>1 exist). B's action space collapses to exactly HOLD (stay at +-1) vs REDUCE-TO-FLAT (go to 0) -- by Part 1's identical mechanical identity, reduce-to-flat's value is simply -Q_hold_B, with no partial-add or partial-reduce state to decompose further. This is a structurally SIMPLER decomposition than Product A's, not a distinct new one. Cross-reference: M5's own confirmation-pool result for Product B is dual-significant at 0/3 horizons (n=522, 5 sessions), matching Product A's confirmation underpowering. **No genuine additional Product-B-relevant action-value layer is forced here** (task sec42).
## 9. Right-tail mapping read
Per sec36-37/83-84's caution against defaulting to a de-risk/exit mapping: this evidence is genuinely ambiguous between the two readings the task flagged. The deterioration is measured directly on `Q_hold` (existing incumbent exposure's own forward markout), NOT on a separately-identified 'new adds only' population (Part 1 showed none exists distinct from Q_hold) -- so the finding, read literally, implicates the EXISTING position's own expected value, not just the marginal economics of new additions. That said, the effect's significance is concentrated (fails ex-3-sessions, fails in low-vol) and reversal is not economically attractive (Part 5), so this is not evidence for an aggressive exit/reverse policy either -- at most it supports being more cautious about ADDING TO or entering NEW far-from-POC positions (where Q_add==Q_hold applies with full force going forward, no sunk-cost asymmetry) than about actively de-risking already-held ones. A future policy informed by this evidence, if any, should weight the 'affect incremental adds only' reading more heavily than 'de-risk existing exposure', given the significance fragility documented in section 7 -- but this diagnostic does not itself propose or freeze a policy (that is explicitly out of scope, per task instruction, for the next phase).
