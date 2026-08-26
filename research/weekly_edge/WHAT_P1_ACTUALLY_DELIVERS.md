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

## 5. WHAT TO ACTUALLY TRADE — the current answer

**`2 BMOM : 3 X9a`** (= 0.400 / 0.600, the executable form of the preregistered inverse-vol
weights). Trailing-12-month rate, net of the measured $14.65/RT:

| basket | contracts | ALL-3 | weekly $ | **annual** | max DD | worst week | week + % |
|---|---|---|---|---|---|---|---|
| 1 BMOM : 1 X9a | **2** | 64 % | $2,383 | **$123,918** | $42,485 | −$20,133 | **58.5 %** |
| 1 BMOM : 2 X9a | **3** | 64 % | $3,358 | **$174,591** | $47,034 | −$23,287 | 56.6 % |
| **2 BMOM : 3 X9a** | **5** | **92 %** | $5,741 | **$298,509** | $86,272 | −$43,420 | **60.4 %** |

**P1 for the same income:** ~$175k needs **6.2 contracts and a $133,647 drawdown**; ~$300k needs
**10.4 contracts and $223,235**. **Half the contracts, roughly 35–40 % of the drawdown.**

Evidence: 5 of 6 preregistered conditions (rolling gate ALL-THREE **96 %** fractional / **92 %**
tradeable; walk-forward stable on 2 of 3 objectives; positive in 2026; and **not P1 in disguise** —
P1 scaled to the basket's own top-5 drawdown gives 52.6 % / $696 / ALL-THREE 0 % against the
basket's 57.7 % / $1,044 / 96 %). Plus **W87**: at frozen weights over the 16 years the
combination had never touched, its top-5 drawdown is **28.2 % smaller than P1's** and its max
drawdown **34.5 % smaller** — the preregistered bar was ≥25 %.

**It is NOT adopted, and here is everything wrong with it:**

- it **fails** the specificity null (92nd percentile against a 95th bar) — the drawdown gain is
  "two independent streams", W74's mechanism, not these two specifically;
- **BMOM is regime-local** (flat pre-2022, t = 0.93, latest window at the 98th percentile of its
  own history) and carries 40 % of the weight;
- **X9a is weekly ρ 0.613 with P1** and W81 found them statistically indistinguishable as
  objects — so this is *P1's cousin plus the B-MOM leg run standalone*, not two new engines;
- its **2026 hit rate is worse** than P1's (48.4 % vs 51.6 %) despite 3.6× the money, and its
  **worst week is worse in every period**;
- **everything is in-sample.** The forward window and the deep window are both spent.

**Switching the baseline is the owner's decision.** The honest one-line summary:

> *the same money on roughly half the contracts and 35–40 % of the drawdown, at a slightly worse
> worst week, built from two components this repository has itself flagged, evidenced on a fully
> in-sample modern window plus a sixteen-year risk test it passed at frozen weights.*

## 6. Files
`runs/WE_W85_GATEFIX/REPORT.md` (the broken gate) · `runs/WE_W87_DEEPPAIR/REPORT.md` (the
candidate) · `runs/WE_W88_TRADEABLE/REPORT.md` (contracts + the weekly-ρ recount) ·
`runs/WE_W82_FILLAUDIT/` (the fill cost, + amendments 1–2).
