# WHAT P1 ACTUALLY DELIVERS — the honest decision table

Written 2026-08-26, after W76 corrected the substrate truncation. **Every figure here is on the
corrected, extended window** (2022-07-04 → 2026-07-31, 213 weeks) and is net of $4.36/RT
commission. The C1 stress line is quoted separately because it changes the answer materially.

This document exists because the owner asked a direct question — *"别人今年都十几二十万"* — and
the campaign's own reporting had been answering it with a number computed on a window that
stopped two months early.

---

## 1. P1 alone, per 1 unit (≈ 1.27 NQ contracts)

| period | weeks | weekly $ | median week | positive weeks | longest losing streak | max DD | worst week | **annualised** |
|---|---|---|---|---|---|---|---|---|
| **FULL 2022-07 → 2026-07** | 213 | $1,315 | $279 | 56.3 % | 8 | $24,225 | −$7,418 | **$68,389** |
| **TRAILING 12 MONTHS** | 53 | $879 | $81 | 50.9 % | 6 | $24,225 | −$6,344 | **$45,709** |
| **2026 YTD** | 31 | $412 | $189 | 51.6 % | 6 | $24,225 | −$6,344 | **$21,439** |
| held-out Jun–Jul 2026 | 9 | −$2,298 | −$2,855 | 11.1 % | 6 | $18,341 | −$5,015 | −$119,522 |

The trend across the first three rows is the thing to look at: **$68k → $46k → $21k annualised as
the window moves toward the present, against a maximum drawdown that does not fall at all.**

## 2. What $150,000 a year would cost — **at the MEASURED friction of $14.65/RT**

| at this period's realised rate | weekly $ net | annualised | **NQ contracts** | **implied max drawdown** |
|---|---|---|---|---|
| full-window rate | $1,152 | $59,895 | **3.2** | **$60,668** |
| **trailing-12-month rate** | **$716** | **$37,215** | **5.1** | **$97,640** |
| **2026 YTD rate** | **$249** | **$12,945** | **14.7** | **$280,711** |

At the pessimistic $24/RT bound the same rates are **$54,473 / $31,794 / $7,523** per unit per
year.

Read the last row plainly: **at the rate the object has actually produced in 2026, and at the
spread we have now measured, earning $150,000 a year would require ~15 NQ contracts and a
$280,711 drawdown.** That is not a configuration anyone should trade.

The middle row is the honest one to plan against, because a trailing year is the shortest window
containing more than one regime: **$150k/year at ≈5.1 NQ contracts with a ~$97,600 drawdown,
i.e. MAR ≈ 1.5.**

(The earlier version of this table — 2.8 / 4.2 / 8.9 contracts — assumed zero spread cost and is
superseded.)

## 3. ⚠️ THE FRICTION LINE — MEASURED IN W82, AND IT WAS OPTIMISTIC

**Superseded.** W82 audited 3.7 million two-sided second-quotes against P1's own fill
time-of-day distribution. The campaign's assumed 2-tick stress line is wrong:

> **Measured spread at P1's actual trading times: 2.93 ticks = $14.65 per round turn.**
> Overnight 3.19 ticks / $15.97 — and **61.6 % of P1's fills are overnight.**

At P1's 11.15 contract round turns per week that is **$163/week**, not $94:

| cost line | $/week | full window | trailing 12m | **2026** |
|---|---|---|---|---|
| headline (commission only) | $0 | $1,315 | $879 | $412 |
| old C1 stress line (assumed) | $112 | $1,204 | $767 | $301 |
| **MEASURED $14.65/RT** | **$163** | **$1,152** | **$716** | **$249** |

**Annualised per unit at the measured cost: full $59,888 · trailing 12m $37,209 · 2026 $12,938.**

A pessimistic bound of **$24/RT** comes from a direct per-fill measurement on a selected 35-fill
subsample; it agrees on direction and cannot establish magnitude. Carry $14.65 as the working
number and $24 as the bound.

⚠️ **Scope (W82 amendment 2)**: the estimate is measured on 45 sessions at **NQ 23,036–29,479**
and directly overlaps **2.5 %** of P1's contract round turns. It is applied to 2022–2026 only.
**It does not transport to 2006–2021** (NQ 1,600–16,000) and every deep-history re-quote made
with it is withdrawn.

**Every table below §3 that quotes the old $94/week line is superseded by this one.**

## 4. ⚠️ THIS DOCUMENT IS SUPERSEDED FOR THE FORWARD-LOOKING PARTS — READ §5

Everything above is P1's measured record and it stands. Everything that WAS below this line has
been retracted or superseded by W85–W88, and is replaced here rather than left to mislead:

- ~~"W76: the first genuinely held-out window this campaign has ever read"~~ — **FALSE**
  (W85 defect 2). `run_we_w01.py`'s own docstring reads *"holdout 2026-05-31 → 07-31, read once
  at the end"*, its report ranked objects on it, and the vol_period the campaign uses (460) ties
  on dev and **separates only there**. The −22.49 pts/session measurement stands; the label does
  not. That window is **burned**.
- ~~"six consecutive full-sample winners did not survive sub-period testing"~~ — **RETRACTED**
  (W85). The gate's drawdown leg was a shape ratio `top5/maxdd`; an oracle handed **$200 of free
  money every session scored ALL-THREE 0 %** while its raw drawdown improved in 100 % of windows.
  Four of those "failures" reverse on the corrected gate.
- ~~"we have one stream"~~ — superseded. On **weekly** ρ (the correct unit; every census used
  daily), the admissible set is P1, BMOM, X9a, and **{BMOM, X9a} at weekly ρ +0.009 is the one
  independent, recently-effective pair in the repository.**
- ~~"$150k on ~4 contracts with a ~$80k drawdown"~~ — superseded by §5.

## 5. WHAT TO ACTUALLY TRADE — the current answer (rewritten 2026-08-26 after W89–W93)

### 5.0 ⚠️ Three corrections to the version of this section that stood before W89

1. **`CORRECTION` — a row-mixing error I made verbally, never in this file.** In the session
   summary I wrote *"the candidate `2 BMOM : 3 X9a` = 3 contracts, $174,591/yr, $47,034 DD"*.
   That takes the **1:2** row's numbers and puts the **2:3** label on them. This file and
   `runs/WE_W88_TRADEABLE/REPORT.md` always had it right. **`2 BMOM : 3 X9a` is 5 nominal
   contracts and ≈$298k; `1 BMOM : 2 X9a` is 3 nominal contracts and ≈$175k.**
2. **`CORRECTION` (W89 H2) — the friction was charged per TRADE for X9a.** Its real rate is
   **10.79** contract round turns per week, not 9.35. Offsetting that, **BMOM is a 100 % RTH
   object and costs $12.99/ctrRT, not $14.65** — it structurally cannot trade overnight, where
   the spread is 3.00 ticks against RTH's 2.00. The two errors partly cancel: **−0.7 %** on the
   2:3 rung.
3. **⚠️ `CORRECTION` (W89 §5) — "contracts" meant two different things in the same table.**
   P1's "6.2 contracts" was 4.89 *units* × **1.27**, and 1.27 is P1's *mean position size while
   holding* — it is in a position on only **12 %** of minutes. The basket's "3 contracts" was a
   *nominal order count*. **Both sides are now reported as PEAK and TIME-WEIGHTED.**

### 5.1 The executable ladder, at candidate-specific cost

| basket | nominal | **PEAK ctr** | ALL-3 | weekly $ | **annual** | max DD | worst week | wk + % |
|---|---|---|---|---|---|---|---|---|
| 1 BMOM : 1 X9a | 2 | **3** | 64 % | $2,372 | **$123,329** | $42,644 | −$20,144 | **58.5 %** |
| 1 BMOM : 2 X9a | 3 | **5** | **52 %** | $3,327 | **$172,987** | $47,404 | −$23,318 | 54.7 % |
| **2 BMOM : 3 X9a** | **5** | **8** | **92 %** | $5,698 | **$296,317** | $86,651 | −$43,462 | **60.4 %** |

Trailing-12-month rate; drawdowns full-window. At the pessimistic (p75) cost profile the 2:3 rung
is **$287,590**. Note the **1:2 rung fell from 64 % to 52 % ALL-THREE** on the corrected cost —
it now sits on the bar rather than above it.

### 5.2 P1 at matched income — both sides in the same units

| target | object | **PEAK ctr** | time-wtd | **max DD** | worst week |
|---|---|---|---|---|---|
| **$175k** | P1 | **9.4** | 0.715 | **$127,984** | −$35,543 |
| | **1 BMOM : 2 X9a** | **5.1** | 0.503 | **$47,956** | −$23,589 |
| **$300k** | P1 | **16.1** | 1.226 | **$219,401** | −$60,932 |
| | **2 BMOM : 3 X9a** | **8.1** | 0.852 | **$87,728** | −$44,003 |

> **The corrected claim: ≈54 % of P1's peak contracts, ≈70 % of its time-weighted exposure, and
> ≈37 % of its maximum drawdown, at matched income.** *"Roughly half the contracts"* is true on
> peak and overstated on time-weighted. *"35–40 % of the drawdown"* stands.

### 5.3 TWO CHALLENGERS — and W97's audit response CHANGED THIS TABLE

| | specificity null | **deep 16 years (risk)** | **deep 16 years (return)** |
|---|---|---|---|
| **{BMOM + X9a} 2:3** | **FAIL** (92nd vs 95th) | **PASS — top-5 DD −34.6 %** (nominal), −43.5 % (ctr-min), −45.9 % (income) | **+$95,734** |
| **NETFUSE_1** (W92/W93) | **PASS** (98.5th–100th, three nulls) | **FAIL — top-5 DD +32.9 % WORSE** at nominal exposure | **−$8,951** |

> ⚠️ **`CORRECTION` (W97).** The previously published deep figures (−28.2 % and −11.4 %) were
> ratios against **two different P1 baselines**, and W87's was the wrong one. Rebuilt in one run:
> **the pair beats P1 on money, max drawdown, top-5 drawdown, positive-week rate AND losing
> streak simultaneously over sixteen unseen years** ($95,734 vs $79,076 · $24,686 vs $39,555 ·
> $12,384 vs $18,925 · 47.7 % vs 44.5 % · 6 vs 7). **The pair is stronger than the campaign
> believed; NETFUSE_1 is weaker.**
>
> ⚠️ Also withdrawn (W97): **"NETFUSE_1 beats P1 in 2026 / 2×"** — paired t = 0.48, p = 0.635 on
> 31 weeks. And the **ALL-THREE gate figures are divisor-dependent**: 2:3 is 92 % on nominal
> order count but **64 % income-matched and 36 % peak-matched**; 1:2 is the only rung stable
> across all four conventions (48–52 %).

**`NETFUSE_1`** is new and is a *single strategy*, not a basket: one target in {−1, 0, +1}, **one
session box, one ledger**, direct reversals — P1's long vote netted against P1's own mirrored
short vote. At matched contract-minutes against P1:

| | P1 | **NETFUSE_1** |
|---|---|---|
| weekly $ at fixed drawdown | $914 | **$1,148** (+26 %) |
| positive weeks | 54.0 % | **59.2 %** |
| longest losing streak | 8 | **5** |
| max drawdown | $26,642 | **$16,212** (−39 %) |
| mean top-5 drawdown | $17,882 | **$10,597** (−41 %) |
| 2026 weekly $ | $287 | **$575** |

It scored **4 of 5** preregistered conditions and is **the first object in this campaign ever to
clear a specificity null** — at the **100th percentile** on all three legs of the strongest null
available (hold the position schedule completely fixed, permute the direction of the 7,326 latched
runs: the real object earns $1,068/week at fixed drawdown, the null mean is **−$47**).

**It fails C4: over the sixteen unseen years it LOSES $5,970 while P1 makes $79,076**, and its
drawdown advantage does not replicate (11.4 % against a 25 % bar). The pair's does.

### 5.4 Everything wrong with both, in one place

**Shared:** all modern evidence is in-sample; there is **no unspent forward window** in this
campaign (2026-05-31 → 07-31 is burned, ≥2026-08-01 is sealed until the calendar allows).

**{BMOM + X9a}:** fails the specificity null (the drawdown gain is *"two independent streams"*,
W74's generic mechanism); **BMOM is regime-local** (2026 = **+$7/week**, W90) at 40 % weight;
**X9a is not a second engine** — W89 established it is *P1 with one gate swapped*, weekly ρ 0.613;
worst week worse than P1 in every period.

**NETFUSE_1:** deep-negative and its risk geometry does not replicate; **not an independent
stream** (ρ +0.556 with P1, +0.719 with SHORT) and may never be counted in a census; its
trailing-12-month positive-week rate is **52.8 %** against a full-window 59.2 % — decaying; and
an honest quarterly refit picks the incumbent `(1300, 1000)` constants in **0 of 12** refits.

### 5.5 The engineering answer (W92) — build nothing

**Do not build a master execution layer.** Two ordinary NT8 strategies on one account are the
algebraic portfolio: only **0.223 %** of gross contracts cross internally (40 of 17,966 over four
years), worth **$1.63/week**; there are **zero** phantom-flat minutes; and peak account exposure is
identical to the sum of the sleeves. Mark-to-market P&L is additive because both fill at the same
next-bar open.

## 6. Files
`runs/WE_W89_CANDCOST/` (candidate friction, the unit correction) ·
`runs/WE_W90_BMOMSIDES/` (B-MOM's two sides) · `runs/WE_W91_FUSEVSPORT/` (fusion vs portfolio,
+ amendment 1) · `runs/WE_W92_MASTER/` (netting + NETFUSE) · `runs/WE_W93_NETFUSE/` (the
challenge, + the null audit) · `runs/WE_W87_DEEPPAIR/` · `runs/WE_W88_TRADEABLE/` ·
`runs/WE_W85_GATEFIX/` · `runs/WE_W82_FILLAUDIT/`.
