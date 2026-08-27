# WE_W102 — DOES `XM_CONFLICT` SURVIVE BECOMING AN ENGINE? · REPORT

Preregistered (`spec.yaml`, committed at `bdd7948` before any result was read). Owner directive V4
§4 / §18. `W102b` is a supplement written after the arms were read, for a reason stated in §2.

> ## **YES — and the engine turns out to be the forecast.**
> ## Every exit policy tested makes it worse. At fixed drawdown, adding it to P1/PCT is worth
> ## **+98.1 %** unstopped and **−21 % to −36 %** with any of the three stops. A stop-distance
> ## curve from 20 to 300 points never beats no stop at all.
> ## The price of that answer is that **the only intra-trade risk control is the clock.**

---

## 1. The four preregistered arms

342 trades, one per firing session, 1 contract, entry at the 09:46 open, all flat by 15:45.

| arm | $/trade | hit % | net $ | wk $ | **wk$ @ fixed DD** | wk + % | max DD | **mean MAE** | **worst MAE** | mean hold |
|---|---|---|---|---|---|---|---|---|---|---|
| **X0_HOLD** | **$675** | **57.3 %** | $230,989 | $1,084 | **$935** | 51.2 % | $23,480 | −$2,033 | **−$10,865** | 359 min |
| X2_ORSTOP *(0 params)* | $272 | 31.6 % | $93,094 | $437 | $479 | 34.3 % | $18,478 | −$1,014 | −$3,940 | 167 min |
| X3_FLIP *(0 params)* | $146 | 23.7 % | $49,854 | $234 | $335 | 26.8 % | $14,134 | −$864 | −$4,055 | 126 min |
| X1_ATR2 *(1 param)* | $244 | 24.0 % | $83,323 | $391 | $540 | 29.1 % | $14,666 | −$815 | −$2,650 | 122 min |

Exit reasons: X2 stops out **223 of 342**, X3 flips out **253**, X1 stops out **257**. Every policy
removes two thirds to three quarters of the holding time and, with it, most of the edge.

**MAE is the number W101 never reported and it is not small: mean −$2,033 (−102 points), worst ever
−$10,865 (−543 points).** The forecast held an unmanaged position for six hours; now we know how
far offside it went.

## 2. ⚠️ `CORRECTION` — one arm was mis-scaled by my own spec, and the missing arm was mine too

The spec called `X1_ATR2` "the conventional choice". Measured, on the sessions that fired:

| arm | mean stop distance | median | p10 | p90 |
|---|---|---|---|---|
| X1_ATR2 | **39.6 pts** | 34.9 | 25.3 | 61.6 |
| X2_ORSTOP | 59.3 pts | 51.9 | 23.0 | 109.7 |
| X3_FLIP | 37.6 pts | 28.1 | 5.0 | 78.8 |
| *(reference)* mean MFE of the unstopped hold | **137 pts** | | | |

> **`ATR20` here is the average true range of a ONE-MINUTE bar.** Two of them is a one-minute-scale
> distance placed behind a six-hour hold. `X1_ATR2` tested *"a very tight stop"*, not *"an ATR
> stop"*, and the table above must be read that way. The spec also **omitted the campaign's own
> natural stop** — −$1,300 per contract, the session-box level, which is 65 NQ points.

Both are repaired by measuring the whole curve rather than three arbitrary points on it.

## 3. `FACT` — the stop-distance curve, reported as a shape

A scan. **Nothing is selected from it.** −$1,300/contract = 65 points is marked.

| stop (pts) | $/trade | hit % | stopped % | wk $ | **wk$ @ fixed DD** | t |
|---|---|---|---|---|---|---|
| **none** | **$675** | 57.3 % | 0 % | $1,084 | **$935** | 3.81 |
| 20 | $39 | 13.5 % | 86.5 % | $62 | $92 | 0.52 |
| 40 | $221 | 25.7 % | 72.2 % | $355 | $563 | 1.83 |
| 50 | $277 | 31.0 % | 66.1 % | $445 | $696 | 2.14 |
| **65** *(session-box level)* | $281 | 36.8 % | 58.5 % | $451 | $692 | 2.05 |
| 80 | $313 | 41.5 % | 51.8 % | $503 | $640 | 2.11 |
| 100 | $396 | 46.5 % | 42.1 % | $636 | $620 | 2.46 |
| 130 | $414 | 50.6 % | 31.0 % | $665 | $848 | 2.50 |
| 170 | $422 | 52.3 % | 20.5 % | $677 | $615 | 2.41 |
| 220 | $574 | 56.1 % | 9.1 % | $922 | $820 | 3.31 |
| 300 | $666 | 57.3 % | 1.8 % | $1,069 | $906 | 3.74 |

> **No cell beats "none" on the risk-adjusted metric, at any distance from 20 to 300 points.**
> $/trade rises monotonically toward the unstopped value as the stop widens. The local bump at 130
> ($848) is below "none" ($935) and would in any case need its own family-wise null — W95 measured
> a box-level argmax at the **87.5th percentile of pure best-of-31 scan noise**, which is what an
> unguarded peak on a curve like this is worth.
>
> `FACT` **The object does not want a stop.** A stop truncates the right tail through whipsaw
> faster than it saves the left.

## 4. ⭐ The primary — marginal portfolio value, income-matched

P1/PCT alone (spread $14.44/ctrRT): wk $1,394 · wk+ 56.3 % · max DD $22,931 · top-5 $17,835 ·
**wk$ @ fixed $20,245 DD = $1,230**.

| arm added | weekly ρ vs P1 | scale | wk $ | wk + % | max DD | top-5 | CVaR5 | **wk$ @ fixed DD** | **vs P1 alone** |
|---|---|---|---|---|---|---|---|---|---|
| **X0_HOLD** | **−0.0048** | 1.285 | **$2,787** | **61.5 %** | **$23,146** | **$16,772** | −$9,624 | **$2,438** | **+98.1 %** |
| X2_ORSTOP | +0.0939 | 3.189 | $2,787 | 53.1 % | $71,612 | $34,483 | −$14,854 | $788 | −36.0 % |
| X3_FLIP | +0.0588 | 5.954 | $2,787 | 46.0 % | $64,751 | $57,785 | −$19,907 | $871 | −29.2 % |
| X1_ATR2 | +0.0769 | 3.562 | $2,787 | 49.8 % | $58,060 | $31,072 | −$13,924 | $972 | −21.0 % |

The mechanism of the collapse is visible in the `scale` column: a stopped arm earns so much less per
trade that matching P1's income needs **3.2 to 6.0 contracts**, and that multiplies its drawdown.
**Stopping this object does not reduce portfolio risk — it increases it,** because the risk budget
is spent on size instead of on room.

## 5. Live-readiness (directive §18) — what passed, and what a kill switch has to be set from

| check | result |
|---|---|
| determinism | **PASS** — every arm rebuilt reproduces its trade list exactly |
| no lookahead | **PASS by construction** — the decision uses bars ≤ 09:45, the fill is the **09:46 open**, every stop level is fixed before 09:46, and exits fill at the breaching bar's open **or the level, whichever is worse for us** |
| correct session reset | opening range, drive anchor and cross-market σ all reset at the session's own 09:30 |
| **inputs available live** | **YES** — ES / RTY / YM **last prices at 09:45**. No vendor file, no daily download, no data that arrives after the decision |
| cost model | candidate-specific: $4.36 commission + the minute's own spread from W82's committed profile, charged at both ends |
| Python reference | `research/weekly_edge/src/run_we_w102.py`, deterministic |

**Risk limits, from evidence, for the unstopped arm:**

| | |
|---|---|
| worst single trade | **−$6,467** |
| worst day | −$6,467 (one trade per day) |
| worst week | **−$10,069** |
| worst maximum adverse excursion ever seen | **−$10,865 (543 points)** |
| longest losing-week streak | 6 |

> ⚠️ **The only intra-trade risk control in this object is the clock.** History says the worst it
> ever went offside was 543 points; nothing bounds it. If a catastrophic stop is wanted for reasons
> that are not backtest reasons, **300 points costs 1.3 % of the edge** ($675 → $666/trade) and
> caps the tail — that is a cheap insurance premium and it is the owner's call, not a tuning result.

## 6. Per-year and recency — $/trade

| arm | 2022 | 2023 | 2024 | 2025 | 2026 ⚠️ | t12m | t6m ⚠️ |
|---|---|---|---|---|---|---|---|
| **X0_HOLD** | $186 | $628 | $583 | $758 | **$1,064** | **$1,093** | **$1,683** |
| X2_ORSTOP | −$73 | $320 | $412 | $228 | $120 | $232 | $251 |
| X3_FLIP | −$265 | $8 | $312 | $96 | $270 | $197 | $430 |
| X1_ATR2 | −$184 | $132 | $489 | $167 | $201 | $207 | $399 |

⚠️ 2026 and t6m overlap the BURNED span 2026-05-31 → 07-31. The unstopped arm is positive in every
year and strongest in the most recent; every stopped arm is **negative in 2022**.

## 7. Status and what is not claimed

| | |
|---|---|
| **EVIDENCE** | **STRONG (current regime) · REGIME_LOCAL by data availability** |
| **ENGINEERING** | **RESEARCH_ONLY** → the NinjaScript is the next wave; Strategy Analyzer reconciliation is the owner's interactive action |
| **ENABLED** | **NO.** Directive §18 reserves that for the owner alone and nothing here changes it |

Every W101 caveat travels verbatim and none of them is weakened by this wave:

- **N = 342 sessions**, one trade per day on a third of days.
- **The window is discovery-consumed** (2022-07 → 2026-08, mined for 102 waves).
- **ρ = +0.41 with B-MOM.** A diversifier against **P1** (ρ = −0.005); only partly against the pair.
- **REGIME_LOCAL by data availability, not by choice** — the ES/RTY/YM substrates begin
  **2022-01-02**. There is no 2006–2021 test and there cannot be one from anything on disk.
- It was **selected as the best of 27 cells** in W101; it cleared the best-of-27 coin null and a
  rate-matched subsample null at the 99.6th percentile, and the selection still happened.
- **The exit policy was chosen from four arms here**, and the honest reading is not "X0 won" but
  "no exit policy helps" — which the 11-point stop curve establishes far more strongly than the
  four-arm comparison did.
