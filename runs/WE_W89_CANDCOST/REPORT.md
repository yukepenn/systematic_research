# WE_W89 — CANDIDATE-SPECIFIC FRICTION · REPORT

Preregistered (`spec.yaml`, committed before the read). Owner directive §4.

> ## **Three defects found, and the third is the one that changes what the owner is told.**
> ## 1. `FACT` BMOM's cost is **$12.99/ctrRT, not $14.65** — it is a **100 % RTH** object.
> ## 2. `FACT` W88 charged X9a **per trade** — its real rate is **10.79** contract RT/week, not 9.35.
> ## 3. `FACT` W88's headline compared P1's **mean-size-while-holding (1.27)** against the basket's
> ##    **nominal order count**. Two different units. Restated properly, the claim survives on
> ##    peak contracts (54 %) and **weakens on time-weighted exposure (70 %, not "half")**.

---

## 0. Precondition — the join was asserted, not assumed

The per-minute spread profile was rebuilt from the raw `grid1s` parquets and compared to W82's
committed `spread_by_minute.csv`: **max |difference| over 1,380 minutes = 0.0000000000**. This
repo has had four cross-substrate alignment defects (W44, W52, W76, W82); the rule that catches
them is to assert the join.

The three daily P&L series were likewise rebuilt from scratch and asserted against the committed
`streams_extended.csv` / `members.csv`: **max |diff| = 0.000000 on all three.** Nothing here is
compared against a series it did not reproduce.

## 1. `FACT` — what the three candidates actually are, and what they trade

| | trades | contract RT | ctrRT/trade | **ctrRT/week** | W88 used | size-2 share |
|---|---|---|---|---|---|---|
| P1 | 2,002 | 2,368 | 1.183 | **11.12** | 11.15 ✔ | 18.3 % |
| **BMOM** | 1,043 | 1,043 | 1.000 | **4.90** | 4.95 ✔ | 0.0 % |
| **X9a** | 1,946 | 2,299 | **1.181** | **10.79** | **9.35 ✘** | 18.1 % |

> **`CORRECTION` (H2 CONFIRMED).** X9a carries the size-2 quality layer, so its contract round
> turns exceed its trade count by 18.1 %. W88 fed the ladder its **trade** rate. Its friction was
> understated by **15.4 %**.

And a naming correction that has to travel with every future sentence about the challenger:

> `FACT` **"X9a" is not a second engine.** It is `long_obj(TG_for(X9a_channel))` — the **full P1
> object** (13 shared ratchet members, four combiners, range throttle, delta gate, causal quality
> sizing, session box) with the **X9a channel substituted into the OR slot** in place of B-MOM.
> That is what `streams_extended.csv` calls `w72:X9a`. It is why weekly ρ(P1, X9a) = 0.613 and why
> W81 found them indistinguishable as objects. The campaign has repeatedly described the pair as
> "two engines"; it is **one engine with two different OR gates, plus that gate run bare.**

## 2. `FACT` — the cost, measured per candidate

Each candidate's **own** contract-weighted fill minute-of-day distribution × the per-minute
spread profile from all 3.69 M second-quotes:

| | OVERNIGHT | RTH | POST | **ticks** | **$/ctrRT** | vs $14.65 | p75 profile |
|---|---|---|---|---|---|---|---|
| P1 | 61.1 % | 35.6 % | 3.3 % | 2.904 | **$14.52** | −0.9 % | $18.88 |
| **BMOM** | **0.0 %** | **100.0 %** | 0.0 % | 2.598 | **$12.99** | **−11.3 %** | $15.72 |
| X9a | 62.6 % | 33.8 % | 3.6 % | 2.910 | **$14.55** | −0.7 % | $18.91 |

**H1 fires for BMOM and only for BMOM.** P1 reproduces W82's $14.65 to within 0.9 % (the residual
is contract-weighting vs W82's trade-weighting), X9a is P1's twin, and **BMOM is 11.3 % cheaper
because it is structurally incapable of trading overnight** — the channel resets at 09:31 and is
killed at 15:57, so `sfills` holds nothing outside RTH, and RTH's median spread is 2.00 ticks
against overnight's 3.00.

### `SUPPORTED` — and this is a mechanism, not a footnote

> **BMOM and X9a are substantially disjoint IN TIME.** BMOM trades 09:31–15:57 and nothing else;
> X9a takes **62.6 %** of its fills overnight. That is a *structural* reason for their weekly
> ρ = +0.009, and it is the property W75's live brief named as the thing to go looking for —
> *"an engine restricted to the OVERNIGHT session, where ρ ≈ 0 is guaranteed by temporal
> disjointness rather than by luck."* We already had the mirror image of it and had not noticed.
>
> `INFERENCE`, and it is the honest reading of W86's failed specificity null: the null said *"the
> gain is 'two independent streams', not these two specifically"*, and this is **why** they are
> independent. It does not make them a better pair — it makes the mechanism nameable and
> **tells us where to look for streams three and four: the session clock.**

### Sample coverage — restated, because everything here inherits it

| | fills in the quote window | contract-weighted |
|---|---|---|
| P1 | 206 of 4,004 (5.1 %) | 5.0 % |
| BMOM | 118 of 2,086 (5.7 %) | 5.7 % |
| X9a | 228 of 3,892 (5.9 %) | 5.7 % |

45 sessions, 2025-08 → 2026-05, **NQ 23,036–29,479**. Applied to 2022–2026 and to nothing else.
A profile measured on 45 sessions and applied to 1,058 is an extrapolation in time even inside
the modern era. `UNKNOWN`: what the spread was in 2022–2024.

## 3. The ladder, repriced (`FACT`)

Trailing-12-month rate; drawdowns are full-window.

| basket | nominal | $/wk cost | wk $ | **annual** | wk + % | max DD | worst week |
|---|---|---|---|---|---|---|---|
| **W88 blanket $14.65 on trade-rates** | | | | | | | |
| 1 BMOM : 1 X9a | 2 | $209 | $2,383 | $123,911 | 58.5 % | $42,487 | −$20,133 |
| 1 BMOM : 2 X9a | 3 | $346 | $3,358 | $174,614 | 56.6 % | $47,029 | −$23,287 |
| 2 BMOM : 3 X9a | 5 | $556 | $5,741 | $298,525 | 60.4 % | $86,269 | −$43,420 |
| **candidate-specific WORKING** | | | | | | | |
| 1 BMOM : 1 X9a | 2 | $221 | $2,372 | **$123,329** | 58.5 % | $42,644 | −$20,144 |
| 1 BMOM : 2 X9a | 3 | $378 | $3,327 | **$172,987** | **54.7 %** | $47,404 | −$23,318 |
| **2 BMOM : 3 X9a** | **5** | $598 | $5,698 | **$296,317** | **60.4 %** | $86,651 | −$43,462 |
| **candidate-specific PESSIMISTIC (p75 profile)** | | | | | | | |
| 1 BMOM : 1 X9a | 2 | $281 | $2,311 | $120,189 | 58.5 % | $43,489 | −$20,205 |
| 1 BMOM : 2 X9a | 3 | $485 | $3,219 | $167,401 | 54.7 % | $48,693 | −$23,426 |
| 2 BMOM : 3 X9a | 5 | $766 | $5,531 | $287,590 | 58.5 % | $88,162 | −$43,630 |

**The two errors partly cancel** — BMOM was charged 11 % too much, X9a 15 % too little — so the
headline moves **−0.7 %** on the 2:3 rung. The decision rule's 10 % reissue trigger is **not**
met by the cost correction. It *is* met by §5.

New standalone rows, never published before:

| | wk $ t12 | **annual t12** | wk + % t12 | max DD | worst week |
|---|---|---|---|---|---|
| BMOM alone (1 contract) | $1,417 | **$73,671** | **60.4 %** | $44,603 | −$16,970 |
| X9a alone (1 unit) | $955 | $49,658 | 47.2 % | $26,648 | −$8,815 |
| P1 (1 unit) | $718 | $37,317 | 49.1 % | $27,291 | −$7,579 |

> `FACT` **BMOM alone earns roughly twice P1's trailing-year rate from one contract, at a 60.4 %
> positive-week rate** — and carries a **$44,603** max drawdown, 63 % worse than P1's. It is the
> single most productive and least safe object in the repository.

## 4. The gate, re-scored at real costs — with the oracle precondition run first

Oracle battery (W85's rule — a gate that cannot pass a strictly-better object issues no verdicts):
**all four oracles score 100 %. Gate USABLE.**

Exposure-matched to P1's one nominal unit, 25 rolling 24-month windows:

| basket | money | wk + % | top-5 DD | **ALL THREE** | W88 |
|---|---|---|---|---|---|
| **2 BMOM : 3 X9a** | 92 % | 100 % | 96 % | **92 %** | 92 % |
| 1 BMOM : 1 X9a | 92 % | 100 % | 64 % | 64 % | 64 % |
| **1 BMOM : 2 X9a** | 52 % | 100 % | 92 % | **52 %** | ~~64 %~~ |
| 1 BMOM : 3 X9a | 44 % | 100 % | 72 % | 44 % | 44 % |
| 2 BMOM : 1 X9a | 44 % | 92 % | 20 % | 20 % | 20 % |
| **BMOM alone** | 12 % | 100 % | **0 %** | **0 %** | — |
| **X9a alone** | 16 % | 52 % | 28 % | **8 %** | — |

Two things worth naming:

- **the 1:2 rung falls from 64 % to 52 %** on the corrected cost — it is now sitting on the >50 %
  bar rather than comfortably above it;
- **neither component passes anything on its own** (0 % and 8 %). Whatever the pair is, it is not
  one good object carrying a passenger. `REPRODUCED` — this is the same conclusion W86's
  condition 5 reached by a different route.

## 5. ⚠️ `CORRECTION` — the owner-facing headline mixed two units

W88 wrote: *"P1 earning ~$175k needs **6.2 contracts**"* and *"the basket earning ~$175k is
**3 contracts**"*. Those numbers are not in the same unit.

- **6.2** = 4.89 *units* × **1.27**, and 1.27 is P1's **mean position size while it is holding
  something** — measured here at 1.273, in a position on only **12.0 %** of in-window minutes.
- **3** = a **nominal order count** — and because X9a runs size 2 on 18 % of its trades, the
  1:2 basket's account can actually be **long 5 contracts**, and the 2:3 basket **8**.

| basket | nominal | **PEAK contracts** | time-weighted |
|---|---|---|---|
| 1 BMOM : 1 X9a | 2 | **3** | 0.344 |
| 1 BMOM : 2 X9a | 3 | **5** | 0.498 |
| 2 BMOM : 3 X9a | 5 | **8** | 0.842 |
| P1 (1 unit) | 1 | **2** | 0.152 |

Restated at matched income, both sides in the same units, at candidate-specific working cost:

| target | object | **PEAK ctr** | time-wtd | **max DD** | worst week |
|---|---|---|---|---|---|
| **$175k** | P1 | **9.4** | 0.715 | **$127,984** | −$35,543 |
| | 1 BMOM : 1 X9a | 4.3 | 0.488 | $60,510 | −$28,584 |
| | **1 BMOM : 2 X9a** | **5.1** | 0.503 | **$47,956** | −$23,589 |
| | 2 BMOM : 3 X9a | 4.7 | 0.497 | $51,175 | −$25,668 |
| **$300k** | P1 | **16.1** | 1.226 | **$219,401** | −$60,932 |
| | 1 BMOM : 1 X9a | 7.3 | 0.837 | $103,731 | −$49,001 |
| | **1 BMOM : 2 X9a** | **8.7** | 0.863 | **$82,210** | −$40,439 |
| | 2 BMOM : 3 X9a | 8.1 | 0.852 | $87,728 | −$44,003 |

> **The corrected claim.** At matched income the basket runs **≈54 % of P1's peak contracts**,
> **≈70 % of its time-weighted exposure**, and **≈37 % of its maximum drawdown**.
> W88's *"roughly half the contracts"* is **true on peak and overstated on time-weighted**.
> *"35–40 % of the drawdown"* **stands.**

And a tension the gate hides, stated rather than smoothed over:

> **At matched income the 1:2 rung has strictly less drawdown and a better worst week than 2:3 at
> every income level tested** ($47,956 vs $51,175 at $175k) — while the rolling gate prefers 2:3
> (92 % vs 52 %). They are measuring different things: the gate is 25 rolling 24-month windows,
> the matched-income table is one full-window number. `UNKNOWN` which is the better guide to the
> future. Both are reported; neither is suppressed.

## 6. What this wave does NOT change

The challenger's status is **STRONGEST CHALLENGER / NOT PROMOTED**, unchanged. It still fails the
specificity null at the 92nd percentile against a 95th bar; BMOM is still regime-local at 40 %
weight; X9a is still weekly ρ 0.613 with P1 and is now known to be *P1 with one gate swapped*;
every modern block is discovery-consumed; the deep window validates risk geometry, not modern
expected return. A cost measurement cannot promote anything.

## 7. Files
`out/candcost.txt` (full log) · `out/candidate_cost.csv` · `out/ladder.csv` ·
`out/gate_candcost.csv` · `out/matched_income.csv` · code
`research/weekly_edge/src/run_we_w89.py`
