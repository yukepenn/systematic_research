# WE_W101 — THE DIRECTION QUESTION · REPORT

Preregistered (`spec.yaml`, committed at `5922a16` before any result was read). Target chosen from
W99's ranked table and W100's finding. Owner directive V4 §7 TRACK G / TASK 8–10.
`W101b` is a specificity supplement written after the battery was read.

> ## **The primary passes, and one cell clears every bar in the wave.**
> ## `XM_CONFLICT` — take NQ's own opening drive **only on the 34 % of sessions where ES, RTY and
> ## YM are moving the other way** — earns **$675/trade at a 57.6 % hit rate**, sits at the
> ## **99.6th percentile** of rate-matched random subsamples, has a weekly correlation with P1 of
> ## **−0.005**, and **doubles the portfolio's money at essentially unchanged drawdown**.
> ## It is a forecast, not an engine, its window is discovery-consumed, and it cannot be tested
> ## before 2022 because the cross-market data does not exist. All three caveats are load-bearing.

---

## 0. B1 — the check that makes any of this trustworthy

The repo has had four cross-substrate alignment defects (W44, W52, W76, W82). A one-bar ES lead
would manufacture every cross-market result in this wave.

| | joined minutes | lag −2 | lag −1 | **lag 0** | lag +1 | lag +2 | argmax |
|---|---|---|---|---|---|---|---|
| **ES** | 1,619,216 | −0.0004 | +0.0032 | **+0.9316** | +0.0068 | +0.0020 | **0 ✔** |
| **RTY** | 1,567,394 | +0.0002 | +0.0039 | **+0.7459** | +0.0205 | +0.0023 | **0 ✔** |
| **YM** | 1,594,897 | +0.0018 | +0.0007 | **+0.7650** | +0.0099 | +0.0037 | **0 ✔** |

All three peak at lag 0 by two orders of magnitude. **PASS.** 1,008 of 1,058 sessions usable.

---

## 1. The battery — 9 predictors × 3 decision times, one entry, hold to 15:45, size 1

`p*` is computed per decision time from E|move| and that minute's own spread, not assumed.

### Decision 09:45 — E|move| = $2,682, cost $16.86, **p\* = 0.5031**, N = 1,008

| predictor | N | hit % | 95 % CI | $/trade | net $ | 2024+ | 2025 | 2026 YTD |
|---|---|---|---|---|---|---|---|---|
| **DRIVE** *(primary)* | 1,005 | **53.93 %** | [50.85, 57.01] | **$255** | $256,146 | 277 | 484 | −15 |
| ON_RET | 1,006 | 49.80 % | [46.71, 52.89] | −$66 | −$66,626 | −86 | −668 | 577 |
| GAP | 1,007 | 49.75 % | [46.66, 52.84] | −$90 | −$90,648 | −113 | −864 | 500 |
| VWAP_SIDE | 1,008 | 51.39 % | [48.30, 54.47] | $103 | $103,320 | 102 | 139 | 482 |
| PREV_DAY | 1,007 | 49.55 % | [46.47, 52.64] | −$209 | −$210,363 | −249 | −590 | −119 |
| XM_AGREE | 1,008 | 48.71 % | [45.62, 51.80] | −$221 | −$222,390 | −287 | 2 | −777 |
| XM_CONFIRM | 664 | 51.96 % | [48.16, 55.76] | $34 | $22,480 | 1 | 361 | −602 |
| **XM_CONFLICT** | **341** | **57.77 %** | [52.53, 63.01] | **$685** | $233,666 | **741** | **758** | **1,064** |
| VOL_CONFIRM | 504 | 52.58 % | [48.22, 56.94] | $255 | $128,353 | 425 | 802 | −26 |

At 10:30 and 11:30 the pattern shifts: `DRIVE` strengthens (55.41 %, 55.71 %) but pays less per
trade as the remaining horizon shrinks, and `VOL_CONFIRM` becomes the strongest hit rate
(57.59 %, 57.92 %). Full tables in `out/battery.csv`.

### `FACT` — the PRIMARY clears, on one test with no selection

> **`DRIVE` at 09:45: 53.93 % against a computed bar of 50.31 %, $255/trade, $256,146 over 1,005
> sessions.** One preregistered test, chosen before the run. z = 2.30 on the hit rate alone.
> Intraday momentum from the opening print is real on NQ and it clears its own cost bar.

### The best-of-27 null, and what it does and does not license

| | mean | **p95** |
|---|---|---|
| best-of-27 hit rate under a fair coin | 53.95 % | **56.64 %** |
| best-of-27 $/trade under a fair coin | $240 | **$376** |

Note what that says about the whole exercise: **a fair coin, given 27 cells, produces a 53.95 %
hit rate and $240/trade on average.** `DRIVE`'s 53.93 % / $255 is *exactly* what selection noise
looks like — which is why it matters that `DRIVE` was the preregistered primary and needed no
selection correction at all.

**One cell beats both family-wise bars: `XM_CONFLICT` at 09:45 (57.77 % > 56.64 %, $685 > $376).**
`VOL_CONFIRM` at 11:30 and 10:30 beat the hit-rate bar but not the dollar bar → **WEAK**.

---

## 2. ⭐ `SUPPORTED` — `XM_CONFLICT` survives the specificity checks (W101b)

The coin null permutes *signs*. It does not test whether cross-market disagreement picks a
**special subset of sessions**. Two further nulls:

| null | real | null mean / sd | p95 | **percentile** |
|---|---|---|---|---|
| **rate-matched subsample** — 2,000 random 342-of-1,009 subsets of the `DRIVE` book, $/trade | **$675** | $235 / $171 | $513 | **99.6th** |
| the same, hit rate | **57.60 %** | 53.78 % / 2.18 | 57.31 % | **95.9th** |
| session-shift — the same construction landing on other days | **$675** | $241 / $128 | $436 | 100.0th ⚠️ |

⚠️ **The session-shift null is a weaker instrument and I am not leaning on it.** Shifting destroys
the ES–NQ correlation, so the shifted composite disagrees with NQ on ~49 % of sessions instead of
34 % — **492 sessions against the real 342**, a rate mismatch that makes the arms non-comparable.
The verdict rests on the rate-matched subsample null at the **99.6th percentile**.

### Per-year, and it does not decay

| year | n | hit % | $/trade | net $ |
|---|---|---|---|---|
| 2022 (H2) | 24 | 58.33 % | $186 | $4,475 |
| 2023 | 80 | 56.25 % | $628 | $50,236 |
| 2024 | 111 | 55.86 % | $583 | $64,734 |
| 2025 | 77 | 59.74 % | $758 | $58,337 |
| **2026** | 50 | **60.00 %** | **$1,064** | $53,207 |

Every year positive, hit rate 55.9–60.0 % in all five, and the best year is the most recent.

---

## 3. ⭐ `FACT` — it is not the incumbent in a hat, and the portfolio arithmetic is the point

| vs | weekly ρ | z | daily ρ |
|---|---|---|---|
| **P1** | **−0.0048** | −0.07 | +0.038 |
| X9a | +0.0456 | 0.66 | +0.055 |
| **BMOM** | **+0.4080** | **5.91** | +0.389 |
| PAIR 2:3 | +0.3145 | 4.56 | +0.305 |

> ρ with P1 is **indistinguishable from zero**. ρ with **B-MOM is +0.41** and must travel with every
> quotation — both are intraday-momentum-from-the-open objects on the RTH clock, and the 2:3 pair
> inherits +0.31 of it. This is a diversifier against **P1**, only partly against the **pair**.

Income-matched (W97's convention), every series net of its own contract-weighted spread —
**$14.44 P1, $12.50 + $4.36 XM_CONFLICT**:

| | wk $ | wk + % | max DD | top-5 DD | **wk $ @ fixed $20,245 DD** |
|---|---|---|---|---|---|
| P1 / PCT | $1,394 | 56.3 % | $22,931 | $17,835 | **$1,230** |
| XM_CONFLICT (scaled to P1's income) | $1,394 | 51.2 % | $30,173 | $17,682 | **$935** |
| **P1 / PCT + XM_CONFLICT** | **$2,787** | **61.5 %** | **$23,146** | **$16,772** | **$2,438 (+98 %)** |

> **Adding it doubles the money, raises positive weeks from 56.3 % to 61.5 %, moves max drawdown by
> +0.9 %, and *lowers* the top-5 drawdown.** That is what a genuine diversifier looks like — and
> note it is a **worse** object than P1 standalone ($935 vs $1,230 at fixed drawdown). Its entire
> value is marginal portfolio value, exactly as directive §14 says to measure.

`CORRECTION` The first version of this supplement compared P1 **gross of spread** against
XM_CONFLICT **net of spread** — the same gross/net mismatch W91/M6 was corrected for. Fixed before
any of the above was written; the corrected P1 row now reproduces W98's committed figures to the
dollar ($1,394 / 56.3 % / $22,931 / $17,835 / $1,230).

---

## 4. The mechanism, stated plainly

`XM_AGREE` alone is **negative** (48.71 %, −$221/trade). `XM_CONFIRM` — NQ's drive when the broad
index agrees — is **flat** ($34/trade over 664 sessions). `XM_CONFLICT` is **$685 over 341**. The
decomposition is exact: (664 × $34 + 341 × $685) / 1,005 = **$255** = `DRIVE`.

> ### **The entire intraday-momentum edge on NQ lives in the third of sessions where NQ is moving
> against ES, RTY and YM. When the broad index confirms, the move is already priced and there is
> nothing left. When NQ moves alone, it keeps moving.**
>
> This is the *opposite* of the hypothesis the directive floated ("does NQ/ES disagreement predict
> **failed** persistence"). Disagreement predicts **continued** persistence — the idiosyncratic,
> tech-specific move is the one with follow-through.

By session class at 09:45, $/trade:

| | TREND-UP | TREND-DOWN | REVERSAL | RANGE | MIXED |
|---|---|---|---|---|---|
| DRIVE | +$895 (211) | +$1,502 (146) | +$58 (260) | −$550 (271) | −$153 (117) |
| XM_CONFIRM | +$612 (139) | +$1,057 (101) | −$286 (182) | −$646 (169) | −$112 (73) |
| **XM_CONFLICT** | **+$1,441 (72)** | **+$2,501 (45)** | **+$861 (78)** | −$392 (102) | −$222 (44) |
| VOL_CONFIRM | +$812 (100) | +$1,658 (82) | −$30 (119) | −$624 (131) | −$49 (72) |

`XM_CONFLICT` is the only row positive on **REVERSAL** sessions — the class W50 found we capture
essentially nothing on — and it earns **+$2,501** on TREND-DOWN, the block W99 ranked #1.

---

## 5. ⚠️ What this is not, and the limits that must travel with it

1. **It is a forecast, not an engine.** One entry, one exit, no stop, no session box, no sizing, no
   management. Its adverse excursion is unmanaged and its standalone drawdown ($23,480 nominal) is
   worse than P1's. Everything above is the *information*, not a tradeable object.
2. **N = 342 sessions.** One trade per day on a third of days.
3. **The window is discovery-consumed.** 2022-07 → 2026-08 has been mined for 101 waves.
4. **`REGIME_LOCAL` by data availability, not by choice.** The ES/RTY/YM substrates begin
   **2022-01-02**. There is no 2006–2021 test and there cannot be one from what is on disk. Under
   directive §3 this is an allowed label; it is not a hidden weakness, it is a hard data limit.
5. **It was selected as the best of 27 cells.** It clears the best-of-27 coin null on both
   statistics *and* the rate-matched subsample null at the 99.6th, which is why it is called
   `SUPPORTED` rather than `WEAK` — but the selection happened and is disclosed.
6. **ρ = +0.41 with B-MOM.** Against the pair it is a partial diversifier, not an orthogonal one.
7. **Cross-market's prior is 0-for-15.** That record is on *standalone* cross-market engines. This
   is a *conditional* — cross-market never generates a signal here, it only decides whether NQ's
   own signal is taken. The prior is attached, and it is not overturned by one cell.

---

## 6. Decision

**Nothing is promoted.** Per the rule fixed in advance, a pass buys the right to build an engine on
this predictor in a later wave and nothing else.

What it does change is the frontier. `MECHANISM_COVERAGE` ranked cross-market #3 with the note
*"the 0-for-15 record is on standalone engines; the conditional form has never been run"*. It has
now been run, with the zero-lag test it demanded, and the conditional form is the first
cross-market result in this repo that clears a family-wise null.

**Next, in order:**
1. Build `XM_CONFLICT` as a real object — entry discipline, exit policy, per-contract box, sizing —
   and re-measure everything under the campaign's own conventions. A forecast that survives
   becoming an engine is worth something; most do not.
2. Re-run the specificity battery on that object, not on the forecast.
3. `VOL_CONFIRM` is `WEAK` at 10:30/11:30 and is the one live corner of the volume column after
   W100. It needs its own preregistration, not a footnote in this one.
