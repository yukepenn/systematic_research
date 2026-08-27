# WE_W111 — VOL-EXHAUST / ABSORB, third attempt · REPORT

Preregistered (`spec.yaml`, committed at `f01b5fe` before any code was written).
Directive V5 §18 LANE B/F, P1-A. Coverage-matrix row **#1**, the one ranked highest and untested
after two prior failures. `W111b` is the control that **corrects W108**, run before this was reported.

> ## **VOLUME IS FINALLY TESTED, AND IT FAILS. −$233/trade at the 0.0th percentile of its coin null.**
> ## All five mechanisms cleared the specification gate — 89–99 % of sessions carry a direction, against W106's 0.3 %. **Three of the five are WORSE than a volume-decile-matched random draw** with the same direction rule.
> ## ⚠️ And the control this wave ran has forced a **CORRECTION TO W108's HEADLINE**: the "−TREND / +RANGE class signature" that W108 called *"exactly what the mechanisms predict"* is produced **identically by an unconditional fade with no mechanism at all.** It is a property of the taxonomy, not evidence about anything.

## 1. The specification gate — the mechanism is measurable at last

| mechanism | defined | non-zero direction | rate | gate |
|---|---|---|---|---|
| V1_DECAY_SLOPE | 1,052 | 1,050 | 99.2 % | PASS |
| V2_DECAY_RATIO | 1,052 | 1,050 | 99.2 % | PASS |
| V3_EFFORT_NO_RES | 1,051 | 1,050 | 99.2 % | PASS |
| V4_ABSORB_BAR | 1,052 | 1,052 | 99.4 % | PASS |
| V5_EXHAUST_EXTREME | 944 | 944 | 89.2 % | PASS |

> **5 of 5, against W106's `VOL_DECAY` firing on 3 of 1,058 sessions and W100's gates accepting
> 92 %.** Making every score continuous and letting the trailing causal quantile do the binding is
> what fixed it. **The volume column of the coverage matrix can finally be marked from evidence.**

## 2. Economics — decide 11:48, fill 11:49, hold to 15:44, size 1, no stop

p\* = **0.5042**, computed not assumed. 1,012 eligible sessions.

| mechanism | 0.25 | 0.50 | 0.75 | hit % @0.50 | vs p\* |
|---|---|---|---|---|---|
| V1_DECAY_SLOPE | −$76 | **−$268** | −$261 | 45.09 % | −5.33 |
| V2_DECAY_RATIO | −$193 | **−$213** | −$244 | 45.29 % | −5.13 |
| V3_EFFORT_NO_RES | −$361 | **−$340** | −$217 | 44.88 % | −5.54 |
| V4_ABSORB_BAR | −$137 | **−$187** | −$168 | 51.38 % | +0.96 |
| V5_EXHAUST_EXTREME | −$135 | **−$156** | −$196 | 43.20 % | −7.22 |
| *control: always LONG* | | *+$19* | | *54.25 %* | *+3.83* |
| *control: always SHORT* | | *−$48* | | *45.26 %* | *−5.16* |

| | |
|---|---|
| **PRIMARY** (equal-weight mean, 50 % arm) | **−$233/trade** |
| coin null | mean −$19, **p95 $79** |
| **percentile** | **0.0th** |
| **VERDICT** | **FAILS** |

**All 15 cells are negative.** Best-of-15 bar $359 — nothing is within $500 of it.

## 3. The mandated confound test — volume-decile-matched null

500 draws matching the accepted set's total-volume decile histogram exactly, same direction rule.

| mechanism | real $/tr | matched null mean | null p5 | null p95 | percentile | |
|---|---|---|---|---|---|---|
| V1_DECAY_SLOPE | −$268 | −$156 | −$260 | −$39 | 3.8th | **WORSE** |
| V2_DECAY_RATIO | −$213 | −$117 | −$209 | −$22 | 4.0th | **WORSE** |
| V3_EFFORT_NO_RES | −$340 | −$219 | −$296 | −$136 | 0.2th | **WORSE** |
| V4_ABSORB_BAR | −$187 | −$100 | −$218 | +$16 | 11.0th | MATCHED |
| V5_EXHAUST_EXTREME | −$156 | −$73 | −$158 | +$18 | 6.2th | MATCHED |

> Note the precise reading, which is **not** the mild "it was only measuring session size". Three of
> five sit **below the 5th percentile**: these mechanisms select sessions on which their own fade
> direction does **worse** than a volume-matched random draw. The participation signal is
> **anti-predictive** at this geometry, not merely absent.

## 4. Secondary geometry (10:01 → 11:29) — and a defect of mine, repaired

> ⚠️ `DEFECT`. The first run hardcoded a 40-bar minimum inside the per-session loop. That is fine
> for the 138-bar primary window but is **longer than the entire 31-bar secondary window**, so four
> of the five secondary cells were reported UNTESTED when they had never been given a chance to
> compute. Same family as W104's ON_ASIA cell. Repaired; the primary is bit-identical.

Repaired result: **$6/trade, 71.0th percentile of its coin null. FAILS.** Best cells V2@0.50 $70,
V4@0.75 $51, V3@0.50 $59 — against a best-of-15 bar of $312.

## 5. ⚠️⚠️ THE CORRECTION — W108's class signature is definitional

W108 reported, and the coverage matrix records, that all five of its fades are positive on
RANGE/MIXED and negative on both TREND classes, and called this *"the signs are exactly what the
mechanisms predict"*. W111 reproduced the same signature with five more mechanisms from an entirely
different information source. Nine of nine is either a structural fact or an identity. **The
control W108 never ran settles it:**

| arm, 11:49 → 15:44, no mechanism at all | N | $/trade | TREND-UP | TREND-DOWN | REVERSAL | RANGE | MIXED |
|---|---|---|---|---|---|---|---|
| **FADE morning direction, unconditional** | 1,008 | **−$206** | **−$943** | **−$1,121** | −$138 | **+$470** | **+$516** |
| FOLLOW morning direction, unconditional | 1,008 | +$177 | +$914 | +$1,092 | +$110 | −$499 | −$545 |
| always LONG | 1,012 | +$19 | +$1,579 | −$2,012 | −$63 | +$61 | −$175 |
| always SHORT | 1,012 | −$48 | −$1,607 | +$1,983 | +$34 | −$90 | +$147 |

> ### **An unconditional fade — no volume term, no path-efficiency term, no structure, no filter — produces the identical signature at the identical magnitudes.**
>
> The W51 taxonomy defines TREND-UP as |close − open| ≥ 0.60 × range over the whole session and
> RANGE as ≤ 0.25 × range. The afternoon close finishes on the same side of 09:31 as the 11:29
> close on **86.1 %** of TREND-UP sessions and **73.3 %** of RANGE sessions. **Any rule that trades
> against the morning direction MUST lose on the first and win on the second.** The signature is a
> property of the labels, not evidence about a mechanism.

### What is withdrawn, and what survives

**WITHDRAWN:** W108's interpretive claim that the five fades *"work where they claim to"* and that
*"the signs are exactly what the mechanisms predict"*. They carry no information. Also note the
matched control W108 did not report: **the unconditional fade earns −$206/trade, and the mean of
W108's five mechanisms at the 50 % arm is −$183.** Two of the five beat it (VALUE_REACCEPT −$21,
PATH_EFF_TRANS −$38) and three are worse. **None of the six mechanisms was ever shown to beat
simply fading the morning direction.**

**SURVIVES:** the *target* W108 pointed at is still the right one, but for a different reason than
it gave. An unconditional afternoon fade loses $206/trade and its losses **are** concentrated on
trending sessions; a causal veto would still be the object that changes that. And **W109 has now
measured the informative half properly**: three pre-11:48 causal states predict the ex-post class
at **AUC 0.61–0.62**, decisively above their permutation nulls — which is *not* definitional,
because the detectors see only the morning and the label sees the whole session. What W109 also
showed is that a **binary veto** on information that weak removes good and bad sessions in equal
proportion.

## 6. Decision

**NOTHING PROMOTED.**

1. **The volume column is now marked from evidence, not from absence.** Volume decay, decay ratio,
   effort-without-result, absorption and extreme-exhaustion are **TESTED-NULL as directions at
   11:48 held to 15:44** — with three of five *anti-predictive* against a volume-matched control.
   The quantifier travels with it: *as a fade direction, at this geometry.* Volume as a **confidence
   weight**, as a **threshold scale inside an existing channel**, or on any other horizon remains
   untested.
2. **Coverage-matrix row #1 moves from UNTESTED to NULL** after three attempts, the first two of
   which were specification failures of mine and are recorded as such.
3. **W108's class-signature finding is corrected** and the coverage-matrix footnote is rewritten.
   This is the second time in this campaign that a striking class-conditional table turned out to
   be reproduced by a matched unconditional control (the first was `VWAP_RECLAIM`'s 54.20 % against
   an always-long 54.25 %). **A class-conditional table now requires its matched unconditional
   control in the same wave — that rule is binding from here.**
4. `V4_ABSORB_BAR` is the one mechanism without the fade signature (positive on REVERSAL +$313,
   negative on RANGE −$57 and MIXED −$165) and is also the only one whose hit rate clears p\*
   (51.38 % vs 50.42 %) while still losing money — its selected sessions have a worse payoff ratio.
   Recorded, not pursued.
