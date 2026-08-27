# WE_W112 — the first measurement of the CAUSAL_MODEL_FRONTIER · REPORT

Preregistered (`spec.yaml`, committed at `f678744` before any code was written).
Directive V5 §§15, 22, 17, 44. Coverage-matrix row #0 as re-ranked after W109.

> ## **BY THE LETTER OF MY PREREGISTERED FALSIFIER THIS PASSES — at the 95.2nd percentile against a 95.0 bar. I am recording it as a FAIL, and saying exactly why.**
> ## The fitted model's **out-of-sample R² is −0.024**, its **directional accuracy (53.58 %) is BELOW always-long's (55.04 %)**, an **unfitted one-line control beats it on dollars ($190 vs $181)**, and **all of its money is in one calendar year** (2025 +$615/trade; 2023, 2026 and the trailing six months negative).
> ## **The substantive finding is the valuable one, and it is a negative: the AFT residual is largely UNREACHABLE.** Against a level-2 oracle of $1,170/session, seventeen pre-decision features and a walk-forward protocol reach nothing an unfitted momentum rule does not already have.

## 1. Setup

938 usable sessions · 17 features · E∣move∣ = **$1,754** · cost **$14.36/RT** · **p\* = 0.5041**.
Walk-forward, expanding window, first fit at 250 sessions, 63-session blocks → **11 blocks, 688
out-of-sample sessions from 2023-08-07.** K-fold is used nowhere in this wave.

## 2. The grid — and the controls in the same table

| cell | N | dir acc | vs p\* | **OOS R²** | **$/ctr** | net $ | wk$@fixDD | t |
|---|---|---|---|---|---|---|---|---|
| M0_MEAN / P_SIGN | 688 | **55.04 %** | +4.63 | 0.0000 | $1 | $510 | $1 | 0.01 |
| M0_MEAN / P_WEIGHT | 688 | 55.04 % | +4.63 | 0.0000 | −$93 | −$1,827 | −$58 | −0.80 |
| **M1_RIDGE / P_SIGN** *(primary)* | 688 | **53.58 %** | +3.17 | **−0.0238** | **$181** | $124,610 | $395 | 1.52 |
| M1_RIDGE / P_WEIGHT | 688 | 53.58 % | +3.17 | −0.0238 | $199 | $157,523 | $365 | 1.43 |
| M2_GBT / P_SIGN | 688 | **47.74 %** | −2.67 | **−0.2304** | −$42 | −$28,690 | −$40 | −0.38 |
| M2_GBT / P_WEIGHT | 688 | 47.74 % | −2.67 | −0.2304 | $92 | $63,799 | $105 | 0.48 |
| *CONTROL always LONG* | 688 | *55.04 %* | *+4.63* | | *$1* | *$510* | *$1* | *0.01* |
| *CONTROL always SHORT* | 688 | *44.96 %* | *−5.45* | | *−$29* | *−$20,270* | *−$39* | *−0.31* |
| *CONTROL FADE morning dir* | 688 | *44.96 %* | *−5.45* | | *−$216* | *−$148,570* | *−$87* | *−1.64* |
| **CONTROL FOLLOW morning dir** | 688 | **55.04 %** | +4.63 | | **$190** | **$130,460** | **$246** | 1.44 |

**Primary:** $181/contract, coin null mean −$14 **p95 $180** → **95.2nd percentile.** Directional
accuracy 53.58 % > p\* 50.41 %. **Best-of-4 bar $321 — not cleared.**

## 3. Why I am calling this a FAIL

Four things, any one of which would be disqualifying, and they point the same way.

1. **The model is worse than a constant at direction.** `M0_MEAN` predicts a positive number every
   day, i.e. it *is* always-long, and it gets **55.04 %**. The fitted ridge gets **53.58 %**. The
   boosted trees get **47.74 %** — below a coin.
2. **Out-of-sample R² is negative for both fitted models** (−0.024 and −0.230). Neither beats
   predicting the trailing mean in squared error. There is no magnitude model here.
3. **An unfitted, parameter-free control beats the primary.** `FOLLOW morning direction` — one line,
   no features, no fitting, no walk-forward — earns **$190/contract against the ridge's $181**, on
   the identical sessions. Seventeen features and eleven refits add **nothing**.
4. **The result is one calendar year.**

| period | N | dir acc | $/trade | net $ |
|---|---|---|---|---|
| 2023 | 97 | 48.45 % | **−$134** | −$12,968 |
| 2024 | 231 | 55.41 % | $64 | $14,788 |
| **2025** | 229 | 56.83 % | **+$615** | **$140,822** |
| 2026 | 131 | 48.46 % | **−$138** | −$18,031 |
| t12m | 230 | 55.90 % | $259 | $59,507 |
| **t6m** | 114 | 51.33 % | **−$36** | −$4,147 |
| t3m | 55 | 49.09 % | $14 | $795 |

> Directive §5 makes recency primary. **The trailing six months are negative and 2026 is negative.**

### ⚠️ The spec defect this exposes

My preregistered falsifier was *"primary ≤ 0, OR ≤ the 95th percentile of a coin null, OR OOS
directional accuracy ≤ p\*"*. It **should have included "must beat the matched unconditional
control"** — a rule `W111b` made binding *in this same session*, and which the W112 spec lists as a
required **secondary** while failing to encode as a gate. That is my error in spec construction.
**I am not choosing a criterion after seeing the result; I am reporting both readings and stating
that the falsifier list was incomplete.** The nominal pass is at the 95.2nd percentile against a
95.0 bar — a margin of $1 per contract — and it does not clear its own best-of-4 bar.

## 4. ⭐ The frontier number, and why it must not be quoted as a frontier

| level | $/session | source |
|---|---|---|
| 1. `EX_POST_PATH_ORACLE` | not computed | |
| 2. `EX_POST_EXECUTION_FEASIBLE_ORACLE` | **$1,170** | W103 capture ledger v3, AFT |
| 3. `CAUSAL_MODEL_FRONTIER` — *best cell* | $229 | M1_RIDGE / P_WEIGHT, walk-forward |
| 3′. **what is actually defensible** | **≈ $190, and it needs no model at all** | the FOLLOW control |
| 4. `REAL_SYSTEM_CAPTURE` (P1/PCT) | **$3** | W103 capture ledger v3, AFT |

> ### **Do not quote $229 as the causal model frontier.** A model whose OOS R² is negative and whose directional accuracy is below always-long has not measured a frontier; it has recovered, badly, an effect a one-line control already carries. The honest statement is:
> ### **On AFT, with 17 pre-decision features and a clean walk-forward protocol, no fitted causal model reached anything beyond simple morning-continuation — and that itself is concentrated in 2025.**

**The consequence for priorities is the point of the wave.** Directive §16 warns against spending
research effort on a category worth little. The AFT gap of $1,167/session between the level-2 oracle
and real capture has been treated across three waves as *unmonetized opportunity*. This wave is the
first direct evidence that **most of it is the oracle's foreknowledge, not money we failed to
collect.** AFT should drop down the queue, not up it.

## 5. ⭐ The one thing worth taking forward — and it was sitting in the control column

`FOLLOW morning direction` — buy at 11:49 if the 11:29 close is above the 09:31 open, sell if below,
exit 15:44 — earns **$190/contract over 688 out-of-sample sessions at 55.04 %**, and **W111b
independently measured +$177/contract over all 1,008 in-window sessions**. Two overlapping but
differently-constructed reads agree.

It is not drift: `always LONG` has the **same** 55.04 % accuracy and earns **$1**. The money is in
the short leg — the afternoon continues a *down* morning too.

> **This is an OBSERVATION, not a result.** It appeared only as a control in two waves, it has never
> been preregistered, it has no null of its own, no cost sensitivity, no session-class split and no
> recency table. And it is the exact mirror of the fade family this campaign has killed seven times,
> which is itself a reason to test it properly rather than to believe it. **It gets its own
> preregistration (W114) and must clear its own bars from scratch.**

## 6. Decision

**NOTHING PROMOTED.**

1. **`CAUSAL_MODEL_FRONTIER` is now measured once, and the measurement is a negative.** The number
   goes into `OPPORTUNITY_LANGUAGE.md` with its protocol and its caveats attached — *"AFT, 17
   features, expanding-window walk-forward, 63-session blocks: no fitted model beat an unfitted
   momentum control; OOS R² negative; directional accuracy below always-long."*
2. **AFT is de-prioritised.** Four waves have now attacked it (W104 WEAK, W107 fail, W112 fail) and
   this one gives a reason rather than another null: the residual measured against a level-2 oracle
   is largely unreachable.
3. **The action-value formulation (§22) is tested and did not rescue anything here.** `P_WEIGHT`
   beat `P_SIGN` for both fitted models ($199 vs $181; $92 vs −$42), which is weak support for the
   idea that continuous weighting extracts more than a binary cut — but from models that have no
   predictive power to weight. Recorded, not claimed.
4. **`FOLLOW_MORNING` → W114**, preregistered separately.
