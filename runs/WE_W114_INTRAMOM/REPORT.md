# WE_W114 — INTRADAY MOMENTUM: the afternoon continues the morning · REPORT

Preregistered (`spec.yaml`, committed at `d7889c7` before any code was written).
Directive V5 §§5, 19, 20, 24, 33, 44. Harness check **PASSED** — all four minute anchors present on
> 92 % of sessions in *both* windows, so the rule means the same thing in 2006 as in 2026.

> ## **THE PRIMARY FAILS ITS CONJUNCTION. The modern half passes at the 98.9th percentile; the 16-year half fails.**
> ## Per the spec that combination is **`REGIME_LOCAL`, which is a DEMOTION of confidence, not a result** — the same label and the same treatment P1/PCT's box denominator received.
> ## **And the 2006–2021 failure is BEHAVIOUR, not the cost hurdle.** Stripped of all spread, the implied directional edge is **5.62 % now against 0.70 % then** — an eight-fold difference in accuracy units, which no price-level argument can explain away.
> ## The modern evidence is nonetheless **the strongest single new object this campaign has produced since XM_CONFLICT**: genuinely two-sided, robust across a 15-cell decision-time plateau, positive in four of five calendar years, and **strongest in the most recent twelve months.**

## 1. The primary — both halves, independently

| window | N | hit % | p\* | vs p\* | **$/trade** | net $ | coin p95 | percentile | |
|---|---|---|---|---|---|---|---|---|---|
| **MODERN** 2022-07 → 2026-08 | 1,009 | **55.00 %** | 0.5042 | **+4.59** | **$179** | $180,651 | $131 | **98.9th** | **PASS** |
| **OUT-OF-WINDOW** 2006–2021 | 3,923 | 49.40 % | 0.5176 | **−2.36** | **−$9** | −$33,784 | $6 | 69.3rd | **FAIL** |

**PRIMARY VERDICT: FAILS.** There is no partial credit; the spec said so before the numbers existed.

## 2. ⭐ Is the old-window failure just the price level?

NQ traded near 1,700 in 2006 and near 20,000 in 2026, so a fixed dollar cost is a far higher hurdle
in the old window — visible in p\*, which is 0.5176 there against 0.5042 now. The spec required this
be separated from behaviour.

| window | E∣move∣ | cost | p\* − 0.5 | $/trade at **0× spread** | **implied directional edge** |
|---|---|---|---|---|---|
| MODERN | $1,721 | $4.36 | 0.13 % | **$189** | **5.62 %** |
| 2006–2021 | $409 | $4.36 | 0.53 % | **$1** | **0.70 %** |

> ### With **every cent of spread removed** and only commission charged, the old window earns **$1 per trade over 3,923 sessions.** The implied edge — in accuracy points, which are scale-free — is **0.70 % then against 5.62 % now.**
> ### **The rule did not exist in 2006–2021.** It is not that costs ate it.

And the transition is monotone, not a break:

| block | N | hit % | $/trade | net |
|---|---|---|---|---|
| 2006–2010 | 1,202 | 46.76 % | −$16 | −$18,786 |
| 2011–2015 | 1,231 | 49.88 % | −$21 | −$25,292 |
| 2016–2021 | 1,490 | 51.14 % | **+$7** | +$10,294 |
| **2022–2026** | 1,009 | **55.00 %** | **+$179** | **+$180,651** |

## 3. Two-sidedness survives — this is not the uptrend

The spec fixed in advance that a one-sided result would be a **withdrawal**, not a nuance.

| window / arm | N | hit % | $/trade | net $ | t |
|---|---|---|---|---|---|
| MODERN · FOLLOW **long leg** | 528 | 58.90 % | **+$198** | $104,743 | 1.63 |
| MODERN · FOLLOW **short leg** | 481 | 50.73 % | **+$158** | $75,908 | 1.36 |
| MODERN · FADE (mirror) | 1,009 | 44.50 % | −$208 | −$209,629 | −2.16 |
| *MODERN · control always LONG* | 1,013 | 54.29 % | *$21* | $21,133 | 0.29 |
| *MODERN · control always SHORT* | 1,013 | 45.21 % | −$50 | −$50,227 | −0.70 |
| 2006–21 · FOLLOW long leg | 2,095 | 54.80 % | +$9 | $19,791 | 0.67 |
| **2006–21 · FOLLOW short leg** | 1,828 | 43.22 % | **−$29** | −$53,575 | −1.63 |

> **Both modern legs are positive** while always-long earns $21 — so the money is not drift. In the
> old window the **short leg is the one that fails**, which is also where the modern edge is newest.

## 4. Recency — and a correction to my own spec

| period | N | hit % | $/trade | net $ |
|---|---|---|---|---|
| 2022 (H2) | 126 | 61.11 % | $379 | $47,791 |
| 2023 | 244 | 54.51 % | $73 | $17,721 |
| 2024 | 249 | 51.81 % | **−$22** | −$5,416 |
| 2025 | 246 | 56.10 % | $205 | $50,377 |
| **2026 YTD** | 144 | 54.17 % | **$487** | $70,177 |
| **t12m** | 249 | 53.01 % | **$236** | $58,699 |
| t6m | 125 | 55.20 % | $564 | $70,465 |
| t3m | 62 | 58.06 % | $661 | $41,010 |

> ⚠️ **CORRECTION to this wave's own spec.** The mechanism card stated *"W112's own stability table
> shows the effect concentrated in 2025"*. That table was the stability of **M1_RIDGE**, not of this
> rule, and I mis-attributed it when writing the spec. `FOLLOW_MORNING` is **positive in four of
> five calendar years and strongest in the most recent one.** The concern the spec raised does not
> apply; recorded because the spec is the record.
>
> ⚠️ **t6m and t3m fall inside the BURNED span** (2026-05-31 → 07-31). Those two rows are **not
> independent evidence** and must never be quoted as forward performance. The t12m figure of
> $236/trade is the defensible recent number.

## 5. Robustness — the plateau, and it is a plateau

| decide ↓ / exit → | 15:29 | **15:44** | 15:59 |
|---|---|---|---|
| 11:18 | $146 | $186 | $179 |
| 11:33 | $158 | $190 | $182 |
| **11:48** *(the primary)* | $155 | **$179** | $159 |
| 12:03 | $166 | **$196** | $186 |
| 12:18 | $82 | $111 | $98 |

> **Fourteen of fifteen cells fall between $146 and $196**, and the primary cell is *not* the
> maximum — 12:03/15:44 is. The preregistered geometry sits mid-plateau, which is what a real effect
> looks like and what an artifact does not. **Per the spec, the $196 cell may not be quoted,
> promoted, or substituted for the primary.** In the old window all fifteen cells are negative
> (−$0 to −$24), equally consistently.

## 6. Concentration and class (§25, diagnostic)

| window | median | trimmed | skew | worst | top1 % | top5 % | top10 % | top20 % |
|---|---|---|---|---|---|---|---|---|
| MODERN | **+$166** | **+$138** | 2.80 | −$16,354 | 20.2 % | 51.6 % | 76.6 % | **110.5 %** |
| 2006–2021 | −$4 | −$4 | −0.89 | −$8,684 | *n/a* | *n/a* | *n/a* | *n/a* |

> **Much healthier than XM_CONFLICT**: the **median trade is positive** and the **5 %-trimmed mean
> is +$138**, so the edge survives deleting both tails — something XM cannot claim. But **top-20
> contribution is 110.5 %**, meaning the other 989 trades sum to −10.5 % of net. Many small wins, a
> few enormous ones, and a few catastrophic losses (worst −$16,354).
> ⚠️ `CORRECTION`, mine: the first run divided contribution shares by `max(net, 1e-9)`, which for
> the **losing** old-window arm returned 1e-9 and printed shares of 6.2 × 10¹⁷ %. Fixed to use
> ∣net∣; contribution shares of a losing arm are **undefined** and are shown as n/a.

Session class (modern): TREND-UP **+$920**, TREND-DOWN **+$1,092**, REVERSAL +$110, RANGE −$499,
MIXED −$545 — the exact mirror of the fade signature, and **definitional** per `W111b`. It carries
no information and is shown only because the class table is a standing column.

## 7. Portfolio

ρ(FOLLOW, P1/PCT) = **+0.279** · ρ(FOLLOW, XM) = **+0.094** · ρ(P1, XM) = +0.081 (reproduces W110).

| book, inverse-vol | wk $ | max DD | **wk$@fixDD** | pos wk % | t |
|---|---|---|---|---|---|
| P1/PCT alone | $1,394 | $22,931 | $1,230 | 56.3 % | **4.16** |
| P1/PCT + XM | $1,142 | $11,489 | **$2,012** | 59.2 % | **4.90** |
| P1/PCT + FOLLOW | $1,158 | $14,976 | $1,566 | 62.4 % | 3.76 |
| **P1/PCT + XM + FOLLOW** | $1,063 | **$10,323** | **$2,085** | **62.9 %** | 4.58 |

> Adding it to the existing candidate portfolio is **modestly positive**: +3.6 % at fixed drawdown,
> max DD $11,489 → $10,323, positive weeks 59.2 → 62.9 %. But **t falls 4.90 → 4.58**, and it
> correlates +0.279 with P1 — far more than XM's +0.081, because P1 is itself a trend engine. It is
> **not** the second orthogonal information source the book needs.

## 8. Decision

**NOTHING PROMOTED. The object is `REGIME_LOCAL`, and per the spec that is a demotion of confidence.**

| | |
|---|---|
| EVIDENCE | **REGIME_LOCAL** — modern 98.9th percentile, 16-year out-of-window FAIL, and the failure is behavioural not cost |
| PORTFOLIO ROLE | **WATCH** — ρ +0.279 with the base; +3.6 % at fixed DD; not an orthogonal source |
| ENGINEERING | **RESEARCH_ONLY**. No C# exists and none is written by this wave |

**What it earns:**

1. **A place on the frontier, not in the book.** It is the strongest modern object since XM, it has
   no parameters at all, and it needs no data we do not own — but a rule that did not exist for
   sixteen years is a rule that can stop existing again.
2. **A named forward test with a real bar.** The sealed data from **2026-08-01** is virgin. This
   object is parameter-free, so a forward read requires no refitting and no judgement:
   *does `FOLLOW_MORNING` remain positive on sealed sessions?* Recorded in
   `research/operational/MONITORING_CALENDAR.md`.
3. **A hypothesis with a mechanism and a falsifier.** The implied edge rose monotonically
   (0.70 % → 5.62 %) across four blocks spanning twenty years. Either intraday momentum genuinely
   strengthened as index volumes concentrated into the close, **or** the modern window is a
   twenty-year excursion. The forward data decides it and nothing else can.
4. **A standing correction:** this campaign has killed seven fade mechanisms and called the family
   dead. `W114` shows the **mirror** of those fades earns $179/trade on the same sessions with the
   same costs. The fades were not failing because "mean reversion doesn't work on NQ" — **they were
   failing because they were on the wrong side of a live momentum effect.**
