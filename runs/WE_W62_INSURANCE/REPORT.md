# WE_W62 — INSURANCE, TIMEABLE, OR DECAYING? · REPORT

Preregistered; amendment 1 added the decisive phase **before** it ran.

**VERDICT: the hypothesis W61 ended on is `REFUTED` by the test built for it. The short sleeve's
contribution IS regime-shaped, and the premium in the wrong regime is unaffordable at the weight
that makes it attractive. W61's revival condition stands, re-framed.**

---

## 1. What could not be answered, said first

**Phase 2 is uninterpretable and the code said so itself.** 22 rolling 24-month windows inside a
four-year sample overlap by 23/24, so the **effective number of independent observations printed
by the run is about 1**. The loadings it produced —

| regime variable | corr with P1's t | corr with the short sleeve's t |
|---|---|---|
| realised volatility | +0.634 | **−0.683** |
| up-day share | +0.617 | **−0.407** |
| corr(t_P1, t_SHORT) across windows | | **−0.473** |

— have exactly the insurance shape, **and a correlation on one effective observation is not
evidence of anything.** Reported, not used.

**Phase 3 could not be run at all.** Lagging the regime variable by a full 24-month window
leaves too few windows. The predictive question is `UNKNOWN` on this sample, not negative.

## 2. Phase 4 — the regime split, which has real sample

Causal label (trailing 6-month NQ return > 0), 746 UP sessions and 266 DOWN, each subsample
rescaled to a $20,245 max drawdown:

| regime | arm | sessions | weekly $ | week + % | traded-day + % |
|---|---|---|---|---|---|
| UP | P1 alone | 746 | $2,362 | 58.3 | 47.7 |
| UP | P1 + short w=0.30 | 746 | $2,534 | **64.4** | 48.0 |
| DOWN | P1 alone | 266 | $768 | 44.6 | 41.3 |
| DOWN | P1 + short w=0.30 | 266 | **$1,142** | 49.2 | 44.4 |

Adding the sleeve is **+$172/wk in UP and +$374/wk in DOWN**, and the run printed *"insurance
that pays for itself"*.

**That printout is wrong, and the next phase is why.** The aggregate hides the dispersion.

## 3. Phase 5 — the decisive row (`FACT`)

Per year, each year rescaled to a $20,245 max drawdown within itself:

| year | sleeve standalone (pts/session) | P1 weekly $ | combo weekly $ | **delta** | P1 week + % | combo week + % | P1 maxDD | combo maxDD |
|---|---|---|---|---|---|---|---|---|
| 2022 | +10.11 | $1,818 | **$4,339** | **+$2,521** | 46.2 | 57.7 | $12,909 | **$5,593** |
| 2023 | +2.76 | $373 | $899 | +$527 | 59.6 | 59.6 | $16,388 | $7,120 |
| 2024 | +13.92 | $5,745 | $5,832 | +$87 | 60.4 | 66.0 | $6,747 | $6,461 |
| 2025 | +6.05 | $2,988 | $3,449 | +$460 | 58.5 | 69.8 | $15,344 | $10,637 |
| **2026** | **−10.62** | **$2,443** | **$845** | **−$1,598** | **68.2** | **59.1** | $12,607 | **$16,125** |

> **In 2026 the combination earns 65 % less than P1 alone, has 9.1 pp fewer positive weeks, and
> a 28 % LARGER drawdown.** Every metric worse, at once.

**The benefit tracks the sleeve's own expectancy exactly**, which is precisely what W61's null
already measured: a circularly-shifted sleeve delivered $1,767 of the $1,936, so ~91 % of the
combination's benefit was the sleeve's expectancy and only ~9 % its alignment with P1. When the
expectancy goes, so does the benefit.

**The insurance reading — "hold it through the premium-paying stretch because you cannot predict
the flip" — is refuted.** Not because the shape is absent (2022 +139 %, 2026 −65 % is exactly
the shape) but because **the premium is unaffordable at the weight that makes it attractive.**

## 4. What the year table actually establishes

`FACT`: **the sleeve's contribution is regime-shaped with real sample behind it.** The bear year
(2022) gains +139 % and halves the drawdown; the two strongest bull years give +1.5 % and −65 %.
That is a genuine structural property, not a correlation on one effective observation.

`INFERENCE`: capturing it would require **regime timing** — a conditional weight — and phase 3
could not even test whether that is possible on this sample. This campaign has failed at regime
identification four times (W03's gate, W37's thresholds, W40's regime band, W41's bar size were
all full-sample artifacts), so a conditional weight is not something to reach for casually.

`UNKNOWN`, and it is the obvious next question: **a much smaller unconditional weight.** At
w = 0.30 the 2026 damage is −$1,598/wk. The damage scales roughly with the weight while the
2022 benefit does too, so there may be a weight at which the worst year is tolerable and the
bear-year benefit still meaningful. That is a portfolio-sizing question, it is cheap, and it has
not been asked.

## 5. Correction to W61

W61 wrote: *"a long engine and its mirror decaying in opposite phases is what a directional
regime looks like… the short sleeve is insurance whose premium is currently being paid, not a
broken engine. That is a hypothesis, not a finding."*

**It was flagged as a hypothesis and it is now tested and refuted as a basis for holding the
sleeve.** The shape is real; the conclusion drawn from the shape was not. W61's revival
condition stands, re-framed:

> The short sleeve is **not** a decaying edge and **not** holdable insurance. It is a
> **bear-market hedge with a premium that is currently −65 % of weekly income.** The revival
> condition is unchanged in form — the trailing-24-month t returning toward its own median of
> +2.1 — but the reason is different: it is not that the edge must return, it is that the
> **premium must fall to something the book can carry.**

## 6. Files
`out/insurance.txt` `out/regimes.csv` `out/loadings.csv` ·
code `research/weekly_edge/src/run_we_w62.py`
