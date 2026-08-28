# `VOLUME_LIQUIDITY_V1` — DEVELOPMENT · **`NO CANDIDATE / CLOSED AT EXACT SCOPE`**

One shot, gates frozen in `SPEC.md` at `4ef441d` **before any volume alpha P&L existed**.
Engine certified `PASS` on all five clauses at `d0d1997`, before the economics were read.

> ## **VERDICT: `VOLUME_LIQUIDITY_V1 — NO CANDIDATE / CLOSED AT EXACT SCOPE`**
> **10 of 12 gates fail. Gross P&L is `−$17,033.50` — negative BEFORE a single dollar of cost.**
> **Net `−$54,330.30` · Sharpe `−0.486` · 1 of 4 blocks positive · every leave-one-root-out
> negative · the real object sits at the 56.5th and 39.8th percentiles of its own two nulls.**

| | 2010-03-23 → 2018-12-31 |
|---|---|
| weeks · roots · sectors | **458** · **21** · **6** |
| (root, week) positions · daily rows | 8,942 · 44,608 |
| **gross P&L** | **−$17,033.50** |
| costs | $37,296.80 |
| **NET P&L** | **−$54,330.30** |
| weekly mean · median · sd | −$118.63 · −$27.27 · $1,758.65 |
| **annualized weekly Sharpe** | **−0.486** |
| max drawdown · duration | $56,805.34 · **438 of 458 weeks** |
| ES 5 % · positive-week rate | −$4,182.65 · 46.72 % |
| turnover | 4,782.3 sides = 2,391.2 contract RT · 10.44 sides/week |
| avg ex-ante gross risk | $3,031.81/day-sd |
| avg **net directional** risk | **−$1.64/day-sd = −0.054 % of gross** |

---

## 1. Gate table — D1–D11, frozen before the result

| gate | observed | |
|---|---:|:--|
| **D1** net > 0 | **−$54,330.30** | ⛔ **FAIL — decisive** |
| **D2** Sharpe ≥ 0.50 | **−0.486** | ⛔ FAIL |
| **D3** block-bootstrap lower 95 % > 0 | **−$241.95** | ⛔ FAIL |
| **D4** pure cost stress net > 0 | **−$81,201.66** | ⛔ FAIL |
| **D5** cost / \|gross\| ≤ 25 % | **218.96 %** | ⛔ FAIL — **and see §3** |
| **D6** net > 0 in ≥ 3 of 4 blocks | **1 of 4** | ⛔ FAIL |
| **D7a** top root ≤ 35 % of +root | 27.1 % (`ZW`) | ✅ pass — **NON-ADJUDICATIVE, §3** |
| **D7b** top sector ≤ 50 % of +sector | **100.0 %** (`fx`) | ⛔ FAIL — **NON-ADJUDICATIVE, §3** |
| **D8** every leave-one-root-out net > 0 | **min −$62,448**, all 21 negative | ⛔ FAIL |
| **D9** temporal null > 95th pctile | **56.5th** | ⛔ FAIL |
| **D10** identity placebo > 95th pctile | **39.8th** | ⛔ FAIL |
| **D11** top 10 positive weeks ≤ 50 % | 19.6 % | ✅ pass — **NON-ADJUDICATIVE, §3** |

**The decisive failures are D1, D8, D9 and D10.** D1 says it loses money; D8 says no root carries
it; D9 and D10 say it is indistinguishable from randomised versions of itself.

## 2. ⭐ The two nulls — the object is its own null

| null | construction | replicates | null p50 | null p95 | **REAL** |
|---|---|---:|---:|---:|---:|
| **1 · temporal** | ONE **shared** whole-week circular shift applied identically to every root — preserves the cross-sectional dependence of participation and the sector demean, destroys **only** the volume↔future-return alignment. **Exhaustive**: all 363 distinct shifts | 363 | −$62,388 | +$9,628 | **56.5th pctile** |
| **2 · identity placebo** | permute the frozen `S(i,d)` **across roots within sector** at each rebalance — preserves signal distribution, active-root count, per-root risk scaling, sector structure and turnover architecture | 500, all distinct | −$45,824 | +$7,157 | **39.8th pctile** |

> ### **The real strategy is at the MEDIAN of both nulls.** Randomly re-timing the volume series, or
> ### randomly reassigning which market's liquidity state belongs to which market, produces the same
> ### result. **There is no timing information and no identity information.**

## 3. Three gates are NON-ADJUDICATIVE on a negative object, and saying so is the point

`ESNQ_V1`'s closure sanitation established this and the lesson is applied here rather than
re-learned:

| gate | why its verdict carries no weight |
|---|---|
| **D5** | `cost / \|gross\|` exists to reject **a real edge eaten by friction**. Gross is **−$17,033.50**; there is no edge to eat, and the ratio's denominator is an absolute value of a negative number. It **mechanically fails**, and nothing turns on it |
| **D7a / D7b / D11** | concentration gates exist to reject a **positive** result carried by one root, one sector or a handful of weeks. On a **negative-total** object, "share of positive contribution" describes which markets lost least. `fx` is 100.0 % of positive sector contribution because it is **the only sector that made money at all** |

**Recorded as `MECHANICALLY EVALUATED / NON-ADJUDICATIVE ON A NEGATIVE-TOTAL OBJECT`.**
⛔ No gate was added, removed, altered or re-denominated after the result.

## 4. ⛔ NO MIRROR RESCUE — and the mirror loses too

| | net |
|---|---:|
| real | −$54,330.30 |
| **sign mirror** | **−$20,263.30** |

`SPEC` §8A forbids inverting after the fact regardless. **But the arithmetic removes even the
temptation:** the signal is continuous and symmetric, so the mirror holds the same |positions| and
pays the **identical** $37,296.80 of turnover. Its gross flips to +$17,033.50 and it still loses
$20,263.30. **Both directions lose. This is not a sign error — there is nothing to invert.**

The same fact appears in the sleeve decomposition: the **LOW-participation (long) sleeve loses
$14,921.32** *and* the **HIGH-participation (short) sleeve loses $39,092.47**. Both legs lose.

## 5. Where the loss lives

**Every leave-one-out is negative** — all 21 roots (best: drop `6J` → −$62,448; worst-case removal
`CL`/`NG` → −$29,688) and all 6 sectors (drop `energy` → −$29,688; drop `fx` → −$58,429). **No
single market and no single sector is responsible, and removing any of them does not rescue it.**

Chronologically: 7 of 9 development years negative, only 2012 (+$10,864) and 2013 (+$1,527)
positive; blocks −$17,426 / **+$5,294** / −$20,898 / −$21,300. **The drawdown lasts 438 of 458
weeks** — it is not a strategy with a bad patch, it is a strategy that never worked.

### `VOLUME00`'s declared residual risk materialised, and it is not the whole story

| distance to a causal roll | rows | net | share of the loss |
|---|---:|---:|---:|
| **≤ 1 session** | **2,245 (5.0 %)** | **−$23,214.93** | **42.7 %** |
| 2–3 | 3,378 | −$2,334.18 | 4.3 % |
| 4–5 | 3,661 | −$5,390.31 | 9.9 % |
| **> 5** | 35,324 (79.2 %) | **−$23,390.89** | **43.1 %** |

`VOLUME00` recorded the ±1 embargo ratio as **1.481 against a 1.5 gate — a near-miss — and refused
to move the ladder.** That was the right call and this is the consequence: **5 % of rows carry 42.7 %
of the loss.** ⚠️ **But excluding them does not save it** — the far-from-roll rows lose $23,390.89 on
their own. **A roll embargo is not a repair, and applying one now would be a post-hoc parameter
chosen from an outcome.** ⛔ Not done.

## 6. Not a static-long artifact, and the honest comparison is unflattering

| | |
|---|---:|
| avg net directional exposure | **−0.054 %** of gross risk |
| beta to an equal-risk long-only multi-market basket | **−0.0093** |
| R² | **0.0115** |
| intercept | **−$118.14/week** |
| **the equal-risk LONG-ONLY basket itself** | **+$23,924.86** |

The strategy is genuinely market-neutral — it is not a disguised long and it is not a disguised
short. **It is also worse than simply being long everything**, which earned +$23,924.86 over the
same window at the same risk convention. ⛔ **Not residualized after the fact**; this adjudicates
interpretation, not a repair.

## 7. Closure diagnostic — empty at this specification, with the residual BOUNDED

**Not a rescue.** Nothing fitted, tuned or re-specified; run after the verdict was fixed.

| association of the FROZEN signal with the subsequent weekly root return | week-clustered |
|---|---|
| `S` (clipped, sector-demeaned) | **r = −0.0060 ± 0.0101**, t **−0.59** |
| `RELZ` | r = +0.0053 ± 0.0102, t +0.52 |
| `ZVOL` (raw) | r = +0.0010 ± 0.0150, t +0.07 |

Quintile means of the subsequent return (σ units/week) are **non-monotone**:
`Q1 +0.0016 · Q2 −0.0224 · Q3 +0.1153 · Q4 −0.0645 · Q5 +0.0061`.
**`Q3` — where the signal is ~zero and the strategy takes no position — has by far the largest
forward return.** `Q5 − Q1 = +0.0046` σ/week is economically negligible and is not the shape a
premium makes.

> ### **READING, adjudicated explicitly rather than by the script's conservative auto-label:
> ### THE SURFACE IS EMPTY AS SPECIFIED.** No association survives a week-clustered standard error,
> ### the quintile pattern is non-monotone with the mass in the *inactive* bucket, and **gross P&L
> ### is negative before any friction.** Costs made a losing object lose more; they did not turn a
> ### winner into a loser.
>
> ### ⚠️ **BUT "EMPTY AS SPECIFIED" IS NOT "PROVEN NULL".** The week-clustered SE is **0.0101**, so
> ### a weekly cross-sectional correlation below roughly **\|r\| ≈ 0.02** is invisible at this
> ### sample. **The claim is bounded: this substrate contains no volume/liquidity effect large
> ### enough to detect at n = 444 weeks, and certainly none large enough to pay 219 % of gross in
> ### friction.** It is not a claim that participation carries no information anywhere.

## 8. What is CLOSED, and what is forbidden afterwards

**CLOSED at exact scope:** `ROOT_TOTAL` volume · `log1p` · **63**-session median/MAD · within-sector
**demean** · `clip ±3` · risk-scored sizing on lagged 63-day σ · 40 % sector cap · **weekly**
rebalance · $4.36 RT + 1 tick per side · 21 roots · 6 sectors · 2010-03-23 → 2018-12-31.

⛔ **Forbidden afterwards, per `SPEC` §9 — this list was written before the result and it stands:**
20d · 42d · 126d · daily rebalance · monthly rebalance · no sector demean · sector-only ·
energy-only · metals-only · equity-only · long-only · nonlinear volume transform · volume
acceleration · volume momentum · volume × trend · volume × carry · volume-confirms-price · open
interest · volume-price divergence · ML · **and — added by §5 above — a roll embargo chosen now
from the distance-to-roll table.**

**NOT read, NOT touched:** 2019–2022 held-back · 2023 → 2026-07-31 modern · **and no portfolio
additivity was computed**, because §13 is reachable only by a strategy that survives development.

## 9. What this run cost, and what it bought

| spent | preserved |
|---|---|
| the **first computation of a volume signal** on 2010–2018 — dates already outcome-consumed by TSMOM and CARRY, so **no new market outcome was burned** | ⛔ `ESNQ_BLIND_EFFECTIVE_14` — **unread, unspent** |
| one preregistered attempt from the family's budget | ⛔ NQ BBO **19** (18 pristine / 1 metadata-exposed) |
| ~15 minutes of compute | ⛔ the remaining unread **ES BBO** |
| | ⛔ the **141-session** Last-only pool |
| | ⛔ **all data ≥ 2026-08-01** — asserted in code, max evaluated date **2018-12-31** |

**Bought:** a `DATA-CAPABLE` verdict on the volume field that did not exist before, a certified
`ROOT_TOTAL` representation, a re-usable roll-entanglement audit, a second independent
implementation, and a **bounded** negative on the last free untested surface in the substrate.

> ## **`VOLUME_LIQUIDITY_V1 — NO CANDIDATE / CLOSED AT EXACT SCOPE`. LIVE ENABLED: NO.**
