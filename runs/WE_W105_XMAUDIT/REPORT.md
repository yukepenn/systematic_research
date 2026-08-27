# WE_W105 — THE AUTHORITATIVE XM_CONFLICT TABLE + RISK ARCHITECTURE · REPORT

Preregistered (`spec.yaml`, committed at `3079bad` before any result was read). Owner directive V4
amendment §4 and §5. **Measurement only — no parameter was created.**

> ## **Two findings here lower the confidence in `XM_CONFLICT`, and both should be read before
> ## anything is enabled.**
> ## **1. Concentration.** Over the full window the top-10 trades are 50.5 % of net. **Inside
> ## individual years they are 106 %–204 % of net** — meaning the *other* trades in those years
> ## collectively lost money. Dropping the top 20 of 348 removes **84.8 %** of the edge.
> ## **2. The correlation that justifies the whole portfolio case is not stable.**
> ## ρ(XM, P1) is **0.081 full-window** but **+0.464 over the trailing six months** (z ≈ 2.2).
> ## The diversification benefit may already have degraded.
> ## The edge itself survives every carrier test: **both sides work, and it is not an early-sample
> ## artifact.**

---

## 0. The N reconciliation — 342 and 348 are two anchors, not a discrepancy

| anchor | what it is | **N** |
|---|---|---|
| bar stamped **09:30** — its *open* is the **09:29** price (W101/W102) | one minute inside the pre-open | **342** |
| bar stamped **09:31** — the **TRUE RTH open** under this repo's end-stamping (W102c) | canonical | **348** |

Both reproduce exactly. **PASS.** Everything below uses the canonical 09:31 anchor, N = 348.

## 1. The authoritative table

| period | N | long | short | hit % | $/trade | net $ | wk + % | max DD | worst trade | worst MAE | **top-5 %** | **top-10 %** | **ρ P1** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2022 (H2) | 25 | 13 | 12 | 56.0 % | $853 | $21,323 | 42.3 % | $5,122 | −$5,122 | −$5,205 | **145.0 %** | **183.2 %** | 0.018 |
| 2023 | 79 | 46 | 33 | 51.9 % | $441 | $34,813 | 42.3 % | $20,201 | −$4,702 | −$5,365 | 74.8 % | **126.8 %** | **−0.228** |
| 2024 | 113 | 48 | 65 | 54.0 % | $654 | $73,865 | 58.5 % | $15,302 | −$6,187 | −$9,720 | 67.1 % | **105.8 %** | 0.065 |
| 2025 | 77 | 35 | 42 | 55.8 % | $317 | $24,442 | 45.3 % | $14,577 | −$6,377 | −$8,965 | **125.2 %** | **203.9 %** | 0.072 |
| 2026 YTD ⚠️ | 54 | 35 | 19 | 55.6 % | $751 | $40,560 | 51.6 % | $18,445 | −$8,872 | −$10,865 | **107.2 %** | **178.2 %** | **0.312** |
| t12m | 97 | 50 | 47 | 56.7 % | $690 | $66,975 | 54.7 % | $18,445 | −$8,872 | −$10,865 | 65.3 % | **114.8 %** | **0.259** |
| t6m ⚠️ | 44 | 27 | 17 | 59.1 % | $1,042 | $45,838 | 53.8 % | $18,445 | −$8,872 | −$10,865 | 94.8 % | **156.4 %** | **0.464** |
| t3m ⚠️ | 23 | 14 | 9 | 56.5 % | $324 | $7,462 | 50.0 % | $17,936 | −$8,872 | −$10,865 | **469.8 %** | **691.3 %** | 0.369 |
| **FULL** | **348** | **177** | **171** | **54.3 %** | **$560** | **$195,003** | 48.8 % | $20,201 | −$8,872 | −$10,865 | 29.4 % | 50.5 % | **0.081** |

⚠️ 2026 YTD, t6m and t3m overlap the BURNED span 2026-05-31 → 07-31.

`CORRECTION` to my own first run of this table: sub-period rows were grouped over all 213 weeks, so
a one-year row was diluted by ~200 empty weeks and its positive-week rate was meaningless (2022 read
5.2 %). The weekly series is now restricted to the weeks each period actually spans.

### ⚠️ `CORRECTION` to W101b — the "monotone improvement" story does not survive the canonical anchor

W101b reported per-year $/trade of **$186 → $628 → $583 → $758 → $1,064**, described as improving
every year with the best being the most recent. At the canonical 09:31 anchor it is
**$853 → $441 → $654 → $317 → $751**. **There is no trend.** It is noise around ~$560. That story
was an artifact of the one-minute-early anchor and is withdrawn.

## 2. ⚠️ Concentration — the finding that most changes the confidence level

| test | N | hit % | $/trade | net $ | vs full |
|---|---|---|---|---|---|
| **ALL (canonical)** | 348 | 54.3 % | **$560** | $195,003 | — |
| drop the top **5** trades | 343 | 53.6 % | $401 | $137,622 | **−28.4 %** |
| drop the top **10** trades | 338 | 53.0 % | $285 | $96,476 | **−49.1 %** |
| drop the top **20** trades | 328 | 51.5 % | **$85** | $27,970 | **−84.8 %** |

> **Twenty trades out of 348 — 5.7 % of them — carry 85 % of the money.** And within individual
> years the top-10 contribution *exceeds 100 % of net* in 2022, 2023, 2025, 2026 YTD, t12m, t6m and
> t3m, which means in each of those periods **the trades outside the top ten collectively lost**.
>
> This does not falsify the edge — a six-hour hold with no stop is *designed* to have a long right
> tail, and the object still cleared a |drive|-decile-matched null at the 99.7th percentile.
> But it means the realised income figure is carried by a handful of sessions, and a live period
> that happens to miss those sessions will look nothing like the backtest. **Any income number
> quoted for this object must carry the phrase "carried by ~20 sessions in four years".**

## 3. What carries the edge — the other three answers

| | N | hit % | $/trade | vs full |
|---|---|---|---|---|
| **LONGS only** | 177 | **60.5 %** | **$701** | +25.1 % |
| **SHORTS only** | 171 | 48.0 % | **$415** | −26.0 % |
| 2022 + 2023 only | 104 | 52.9 % | $540 | −3.7 % |
| 2024 onward only | 244 | 54.9 % | $569 | +1.6 % |

> ✅ **It is genuinely two-sided.** Longs are better (60.5 % hit) but shorts are clearly positive at
> $415/trade despite a sub-50 % hit rate — their winners are larger. This is the only two-sided
> object this campaign has produced, and it is the reason the short-side block that W99/W100 ranked
> #1 finally moved.
> ✅ **Not an early-sample artifact.** $540 in 2022–23 against $569 from 2024 on — indistinguishable.

**Per the rule fixed in advance: none of this is turned into a filter.** A carrier test that killed
the edge would be a reason to withdraw the candidate, never to restrict it to the survivors.

## 4. Event days — what could be tested, and what could not

| rule-derivable class | N | hit % | $/trade | net $ | share of net |
|---|---|---|---|---|---|
| **NFP *proxy* (1st Friday)** | 13 | **69.2 %** | **$2,029** | $26,371 | **13.5 %** |
| … all other sessions | 335 | 53.7 % | $503 | $168,632 | 86.5 % |
| OPEX (3rd Friday) | 14 | 57.1 % | $1,001 | $14,019 | 7.2 % |
| quarter-end | 8 | 50.0 % | $1,529 | $12,235 | 6.3 % |
| month-end (≤ 2 d) | 32 | 56.2 % | $494 | $15,820 | 8.1 % |

**13 sessions — 3.7 % of trades — produce 13.5 % of the net at a 69.2 % hit rate.** Suggestive, and
**n = 13 of four classes tested**, so it is one cell of a small family and nothing more. Recorded,
not acted on.

> **CPI, FOMC and mega-cap earnings are `UNTESTED`.** No causal calendar for them was located on
> disk, and the spec forbids inventing an external label. The first-Friday NFP figure is a
> **PROXY** — a rule, not a release calendar — and is labelled as one everywhere it appears.

## 5. ⚠️ The correlation that justifies the portfolio is not stable

| period | ρ(XM weekly, P1/PCT weekly) |
|---|---|
| **FULL** | **+0.081** |
| 2023 | −0.228 |
| 2024 | +0.065 |
| 2025 | +0.072 |
| 2026 YTD ⚠️ | +0.312 |
| t12m | +0.259 |
| **t6m** ⚠️ | **+0.464** (26 weeks, z ≈ 2.2) |

> **The entire `P1 + XM` case rests on ρ ≈ 0.08. Over the trailing six months that number is
> +0.46.** On 26 weeks that is marginally significant, so it cannot be dismissed as noise — and it
> cannot be confirmed as decay either. It is exactly the quantity to watch, and it is the reason
> the drawdown-diversification claim should be stated for the **studied window** and not projected.

## 6. The risk architecture — two layers, and they are not the same thing

**`ALPHA EXIT` = the 15:45 clock.** Closed by W102's stop curve (20 → 300 points, eleven levels,
none beat no-stop at fixed drawdown). Not reopened.

**`DISASTER STOP` = an operational account-survival control.** Not an alpha device. Not expected to
make money. Its job is to bound a tail the backtest cannot bound.

| level | **$ / NQ** | **$ / MNQ** | historical triggers | **% of gross edge lost** | net $ after | worst trade left |
|---|---|---|---|---|---|---|
| 200 pts | $4,000 | $400 | 50 | **15.9 %** | $163,963 | −$4,017 |
| **300 pts** | **$6,000** | **$600** | 13 | **0.7 %** | $193,673 | −$6,017 |
| 400 pts | $8,000 | $800 | 5 | 4.9 % | $185,488 | −$8,017 |
| 500 pts | $10,000 | $1,000 | 2 | 4.1 % | $187,013 | −$10,017 |
| 750 pts | $15,000 | $1,500 | 0 | 0.0 % | $195,003 | −$8,872 |
| 1000 pts | $20,000 | $2,000 | 0 | 0.0 % | $195,003 | −$8,872 |
| none | — | — | 0 | 0.0 % | $195,003 | −$8,872 |

**NO LEVEL IS SELECTED BY THIS WAVE.** These are round numbers spanning the plausible range, chosen
for being round. The non-monotonicity between 300 and 400 is real and is small-sample noise on 5–13
events; it is not a signal that 300 is "better".

> The historical worst adverse excursion is **−$10,865 (543 NQ points)**. **That is a sample
> maximum, not a bound.**
>
> "No stop" maximises historical P&L. **That is not an argument that no stop is the correct live
> risk policy.** A backtest cannot price a tail it never sampled, and an object whose only
> intra-trade control is a clock has no bound on a single day. The owner selects capital risk; this
> wave supplies the menu and its price.

## 7. Status after this wave

`XM_CONFLICT` remains **EVIDENCE: STRONG (current regime) · REGIME_LOCAL** — but the confidence
band is wider than it was this morning. The three caveats that now travel with every quotation, in
addition to the standing ones:

1. **~20 sessions in four years carry 85 % of the money.**
2. **ρ with P1 is +0.46 over the trailing six months against +0.08 full-window.**
3. **The per-year improvement story is withdrawn** — there is no trend, only noise around $560.

Unchanged and still good: two-sided, not an early-sample artifact, and it survived a
|drive|-decile-matched null at the 99.7th percentile.
