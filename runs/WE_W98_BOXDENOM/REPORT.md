# WE_W98 — SHOULD THE SESSION RISK BUDGET SCALE WITH POSITION SIZE? · REPORT

Preregistered (`spec.yaml`, committed at `eeff522` before any result was read). Owner directive
V4 §5 / TASK 2. Supplement `W98b` (mechanism, null, era diagnostic) written after W98's arms were
read and committed with them; it is labelled as a supplement, not as preregistered.

> ## THE ANSWER: **YES — and it is a specification defect, not a tuning choice.**
> ## The four preregistered conditions are all met. The Tier-3 stress **reverses**, so the object
> ## is adopted as **REGIME_LOCAL**, exactly as the decision rule said in advance.

---

## 0. Harness first (all printed before any arm was read)

| | |
|---|---|
| H-A | `gfills(per_ctr=False)` == `sfills`, byte for byte — **PASS** |
| H-B | BMOM `ABS` == `PCT` byte for byte (0 % size-2, so the denominator cannot bite) — **PASS** |
| H-C1 | `gfills/ABS` reproduces `fills_qexit` on P1, byte for byte — **PASS** |
| H-C2 | ABS trade/contract counts == W89's committed table: P1 2,002/2,368 · BMOM 1,043/1,043 · X9a 1,946/2,299 — **PASS** |
| H-D | W82 spread profile, 1,380 minutes — **the spec's own check was WRONG** and is corrected below |
| H-E | every fill minute of P1/X9a/BMOM is covered by the profile; the $3.00 fallback never fires — **PASS** |

> `CORRECTION` The spec wrote H-D as "1,440 minutes 0..1439". The committed profile has **1,380**.
> The 60 absent minutes are exactly **17:00–17:59**, the CME maintenance break — the profile is
> right and the assertion was wrong. It was replaced with the stronger form (assert 1,380 *and*
> that the missing block is exactly 1020–1079) plus a new H-E that no fill can land outside it.
> A check that fails for the wrong reason is a check that would have passed for the wrong reason.

## 1. `FACT` — the primary, and the control that decides whether anything was learned

Full modern window 2022-07-01 → 2026-08-01, 1,058 sessions / 213 weeks. Weekly $ at a **fixed
$20,245 max drawdown**, net of each arm's own contract-weighted spread friction. That metric is
**algebraically scale-invariant** (W97/M1), so none of this is an exposure effect.

| P1 arm | trades | ctr | wk $ | **wk $ @ fixed DD** | wk + % | max DD | top-5 DD | t |
|---|---|---|---|---|---|---|---|---|
| **ABS** (incumbent) | 2,002 | 2,368 | $1,154 | **$885** | 53.1 % | $26,388 | $18,421 | 3.58 |
| **PCT** (per contract) | 2,131 | 2,556 | $1,394 | **$1,231  (+39.0 %)** | **56.3 %** | **$22,928** | **$17,832** | **4.16** |
| `ABS_LOOSE` (the null) | 2,165 | 2,547 | $1,160 | **$837  (−5.4 %)** | 52.6 % | $28,034 | $19,631 | 3.48 |
| `PCT_MATCH` (budget held) | 2,009 | 2,415 | $1,307 | **$1,236  (+39.6 %)** | 54.0 % | $21,420 | $16,963 | 3.94 |
| `NOBOX` | 2,945 | 3,370 | $1,604 | $642 (−27.5 %) | 58.2 % | $50,618 | $24,263 | 3.61 |

**The two controls are the whole result:**

> `ABS_LOOSE` raises the average dollar budget by exactly the factor `PCT` does (k = 1.183),
> applied **uniformly** instead of **per size**. It is worth **+$6/week, paired p = 0.940**.
> `PCT_MATCH` takes the extra budget back out again and keeps **+39.6 %**.
>
> **So none of the gain is "the box was too tight". All of it is that the box was denominated in
> the wrong unit.** W95 had already shown a box-*level* scan's argmax sits at the 87.5th percentile
> of pure noise; this wave says the level was never the question.

`NOBOX` settles a live doubt in the other direction: removing the box entirely costs **−27.5 %**
and takes max drawdown to $50,618. The box is worth having. It was worth having in the wrong units.

## 2. `FACT` — the two negative controls fire exactly as predicted

| | PCT − ABS | ABS_LOOSE − ABS | PCT_MATCH − ABS |
|---|---|---|---|
| **BMOM** (100 % size 1) | **$0.00** | $0.00 | $0.00 |
| **NETFUSE_1** (100 % size 1) | **$0.00** | $0.00 | $0.00 |

Both are structurally incapable of showing an effect and both show exactly none, to the last cent,
on all 213 weeks. That is the harness certifying itself.

## 3. ⚠️ `CORRECTION` to how the object count should be read

The spec's condition (iii) was "sign ≥ 0 on at least 4 of the 7 objects". It is met — **5 positive,
2 exactly zero, 0 negative**. But the count overstates the evidence and I found the reason while
reading the paired table:

| object | PCT − ABS | SE | t | p |
|---|---|---|---|---|
| **P1** | +$240/wk | $126 | **1.90** | **0.057** |
| **X9a** | +$261/wk | $104 | **2.52** | **0.012** |
| NETFUSE_Q | +$295/wk | $182 | 1.62 | 0.105 |
| 1:1 | +$131/wk | $52 | 2.52 | 0.012 |
| 1:2 | +$174/wk | $69 | 2.52 | 0.012 |
| 2:3 | +$157/wk | $62 | 2.52 | 0.012 |

> The three basket rows carry **t = 2.52 and p = 0.012 — identical to X9a's, to two decimals.**
> That is not agreement, it is algebra: the BMOM sleeve contributes exactly zero difference, so
> (basket PCT − basket ABS) = (b/(a+b)) · (X9a PCT − X9a ABS), a pure positive rescaling of one
> difference series. And NETFUSE_Q is built from **P1's own votes**.
>
> **There are TWO semi-independent tests here, not seven — P1 and X9a — and they share thirteen
> ratchet members, the range throttle, the delta gate and the sizing layer.** Anyone quoting
> "5 of 7 objects agree" is quoting one and a half.

On raw weekly dollars the effect is **p = 0.057** on P1. The +39 % is money *and* drawdown together.

## 4. `REPRODUCED` — the mechanism, and where the preregistered prediction only half held

W98b, P1, 1,058 sessions:

| arm | loss-halts | target-halts | no box | **pts at loss-halt, size-1 sessions** | **pts at loss-halt, size-2 sessions** |
|---|---|---|---|---|---|
| ABS | 194 (18.3 %) | 219 | 645 | **55.68** | **37.18** |
| PCT | 166 (15.7 %) | 213 | 679 | 55.68 | **42.11** |

The spec predicted "roughly HALF … and under PCT the two are equal". **Neither is exactly true.**
37.18 is 33 % earlier than 55.68, not 50 % earlier, and PCT moves it to 42.11, not to parity.

> `INFERENCE`, and it is identifiable rather than hand-waved: the box accumulates **across trades**
> within a session, and `maxu ≥ 2` labels a *session* that held size 2 at some point — not
> necessarily on the trade that tripped the halt. So the point-excursion of the halting trade is
> only partly determined by its own size. The direction is confirmed; the magnitude is diluted by
> the labelling. **Recorded as PARTIALLY MET, not as confirmation.**

## 5. `FACT` — the null says this is not merely accounting

Permute **which** entries carry size 2, count preserved (366 of 2,002 entry bars), 200 draws,
seed 98. Everything else byte-identical.

| | wk $ @ fixed DD gap, PCT − ABS |
|---|---|
| **real (score-driven sizing)** | **+$346** |
| null: mean / sd | +$77 / $129 |
| null: min / max | −$389 / +$423 |
| **percentile of the real gap** | **99.0th of 200** |

> A random assignment of the same number of size-2 entries recovers only about **22 %** of the gap.
> **The quality score interacts with the box**: the size-2 trades the dollar box was cutting short
> are specifically the ones that were worth not cutting short. Had this come back at the 50th, the
> fix would still be right on correctness grounds but would have had to be described as recovering
> a mis-metered budget rather than as recovering alpha.

## 6. ⚠️ `FACT` — the fragility, stated because nobody else will

| | |
|---|---|
| sessions where ABS and PCT halt differently | **53 of 1,058 (5.0 %)** |
| gross P&L difference PCT − ABS, all sessions | **+$53,600** |
| … of which comes from those 53 sessions | **+$48,670 (90.8 %)** |

**Ninety-one per cent of the entire result lives in fifty-three sessions.** The effect is real, the
null is clean, and it is still concentrated enough that a different fifty-three sessions could have
told a different story. This belongs beside every quotation of the +39 %.

## 7. ⚠️ `REGIME_LOCAL` — the Tier-3 stress reverses, and W98b says why

2006–2021, 4,279 sessions the object has never traded (directive §3: recorded, **not** a veto):

| | net $ | wk $ @ fixed DD | wk + % | max DD | top-5 DD |
|---|---|---|---|---|---|
| P1 / ABS | $79,076 | **$49** | 44.5 % | $39,555 | $18,925 |
| **P1 / PCT** | **$52,986** | **$33  (−31.4 %)** | 44.0 % | $38,627 | $19,918 |
| P1 / PCT_MATCH | $36,989 | $22 (−53.6 %) | 43.8 % | $39,908 | $18,830 |
| X9a / PCT | $116,451 | $74 (+3.1 %) | 44.2 % | $38,388 | $15,812 |
| BMOM / PCT | $58,645 | $36 (**+0.0 %**) | 51.2 % | $39,743 | $28,361 |
| 2:3 / PCT | $93,329 | $98 (+3.8 %) | 48.2 % | $23,196 | $12,180 |

**On P1 the sign flips.** X9a, BMOM and the pair do not, but P1 loses a third of its deep money.
W98b measured the reason:

| era | loss-halt rate | pts at halt, size-1 | pts at halt, size-2 | **mean session range** |
|---|---|---|---|---|
| 2006–2021 | **3.2 %** | 48.28 | 33.37 | **77.7 pts** |
| 2022–2026 | **18.3 %** | 55.68 | 37.18 | **350.2 pts** |

> A $1,300 box is 65 NQ points in both eras. In 2006–2021 that was **84 % of a typical session's
> entire range** — an extreme event, and being 37 points offside was a genuine catastrophe signal
> worth halting on. In 2022–2026 it is **19 %** of the range — an ordinary wiggle. The box fires
> **5.7× more often** now. Letting a size-2 trade run past it is a different decision in the two
> eras, and the data says it paid in one and not the other.
>
> This is a **real** regime difference, not an artefact I can explain away. What it does establish
> is that **the box's units are wrong in a second way too**: a budget denominated in dollars is not
> comparable across volatility regimes any more than it is across position sizes. That motivates a
> volatility-denominated box — directive §5's variant D, which said "if mechanistically justified".
> **It is now mechanistically justified by measurement rather than by a grid.** Opened as the next
> wave.

## 8. Decision

| preregistered condition | result |
|---|---|
| (i) PCT > ABS on P1's primary | **✔** $1,231 vs $885 |
| (ii) PCT > ABS_LOOSE — scaling, not loosening | **✔** $1,231 vs $837; loosening alone p = 0.940 |
| (iii) sign ≥ 0 on ≥ 4 of 7 objects, BMOM exactly 0 | **✔** 5 / 2 zero / 0 negative — *read with §3* |
| (iv) self-consistent rebuild does not reverse it | **✔** identical to the last dollar ($1,231, 56.34 %, $17,832, 2,131 trades) |

**The rule fires. The box denominator is changed in the instrument, as `PCT`, labelled
`REGIME_LOCAL` per the rule's Tier-3 clause.** The incumbent `ABS` is **not deleted** — every
future table carries both, because a result that reverses on sixteen years is not a result you get
to stop showing the other side of.

The independent argument, which does not depend on any of the above: **a dollar-denominated stop on
a variable-size position halts a 2-lot at half the adverse point move of a 1-lot. That is a
mis-specification by construction.** The backtest can only tell us whether the mis-specification
happened to help. In 2006–2021 it happened to help. That does not make it correct.

### What this changes elsewhere
Every P1 and pair headline in the campaign was produced under `ABS`. They are not withdrawn — they
are correct for the object that produced them — but **`PCT` is now the reference build for W99+**,
and the paired numbers are: P1 $885 → **$1,231** /wk at fixed DD, positive weeks 53.1 % → **56.3 %**,
max DD $26,388 → **$22,928**.

### Not done here, and why
No box **level** was tuned (−$1,300/+$1,000 and k were all fixed before the run), so there is no
best-of-K and no scan null is owed. A level scan is a separate wave with the family-wise null W95
already built.
