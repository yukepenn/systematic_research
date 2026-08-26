# WE_W78 — CHAMPION vs CHALLENGER: THE PAIR · REPORT

Preregistered. Champion P1; challenger `0.70 × P1 + 0.30 × SHORT` at W61's weight, **not
re-tuned**. Full extended window, 1,058 sessions / 213 weeks, all of it now in-sample.

> ## VERDICT: **BOTH BINDING GATES FAIL. P1 REMAINS THE BASELINE.**

---

## 1. The table that motivated the wave

| | week + % | wk streak | median week | weekly $ | **wk $ @ fixed $20,245 DD** | top-5 DD | max DD | worst week | Ulcer |
|---|---|---|---|---|---|---|---|---|---|
| **P1 alone — champion** | 56.3 % | 8 | $279 | $1,315 | $1,099 | $13,864 | $24,225 | −$7,418 | $5,749 |
| **P1 + SHORT w = 0.30** | **60.6 %** | **4** | **$622** | $1,108 | **$1,154** | **$11,004** | **$19,435** | **−$6,314** | **$4,899** |
| 2 long : 1 short (w = 1/3) | **62.0 %** | **4** | **$658** | $1,085 | $1,118 | **$10,471** | $19,642 | **−$6,311** | **$4,741** |

Seven metrics, no trade-off, at matched nominal exposure — and in W76's never-seen window it cut
the loss from −$20,686 to −$11,041. **So did four previously-killed candidates.** The tests below
are the ones that killed them.

## 2. Gate 1 — rolling 24-month windows. **FAIL** (`FACT`)

| challenger | weekly $ @ DD | positive-week % | mean top-5 DD | **ALL THREE** |
|---|---|---|---|---|
| **P1 + SHORT w = 0.30** | 84 % | **100 %** | **24 %** | **12 %** |
| 2 long : 1 short | 84 % | **100 %** | 24 % | **12 %** |
| P1 + SHORT w = 0.20 | 88 % | 72 % | 12 % | 12 % |
| P1 + SHORT w = 0.40 | 84 % | **100 %** | 20 % | 4 % |

Bar: all three in a **majority** of 25 windows. **12 %.**

The decomposition is the finding: the sleeve improves the positive-week rate in **100 %** of
windows and the money-at-fixed-drawdown in **84 %** — but the **drawdown distribution in only
24 %**. The full-sample −20 % maximum drawdown comes from a minority of periods. W61 measured
all-three at 5–14 % on the truncated window; **adding the regime turn did not change it.**

## 3. Gate 2 — walk-forward. **FAIL** (`FACT`)

Re-choosing `w` quarterly from {0, 0.1, …, 0.5} on a trailing year:

- choices: `0.5, 0.5, 0.5, 0.5, 0.4, 0.1, 0.5, 0.4, 0.4, 0.4, 0.0, 0.0` — churn **45 %**
- **w = 0.30 was chosen in 0 of 12 refits**
- retention **58 %** of the fixed quote, against W29's standing bar of **80 %**

| | week + % | weekly $ | wk $ @ DD | top-5 DD | worst |
|---|---|---|---|---|---|
| walk-forward | 59.5 % | $1,097 | **$872** | $8,934 | −$6,892 |
| fixed w = 0.30 | 62.8 % | $1,331 | $1,500 | $10,260 | −$6,314 |
| P1 alone | 56.8 % | $1,600 | $1,337 | $9,868 | −$7,418 |

**An honest quarterly refit cannot settle on a weight, and when it tries it does worse than the
champion.** That is the signature of a parameter with no stable optimum.

## 4. Per year — the pair costs money in **every single year** (`FACT`)

| weekly $ | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|
| P1 alone | $1,159 | $302 | $1,915 | $2,265 | $412 |
| P1 + SHORT w = 0.30 | $1,115 | $294 | $1,748 | $1,763 | $182 |

| positive-week % | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|
| P1 alone | 46.2 % | 59.6 % | 60.4 % | 58.5 % | 51.6 % |
| P1 + SHORT w = 0.30 | **50.0 %** | 59.6 % | **62.3 %** | **69.8 %** | 51.6 % |

Consistently better on the hit rate, consistently worse on the money, and **it does not help
2026 at all** — the year the owner cares about most.

## 5. The one thing that DID pass, and it is worth keeping (`FACT`)

N1 null, 200 draws: circularly shift the sleeve's daily series against P1's, preserving its
marginal distribution exactly and destroying only alignment.

| metric | real | null mean | null p95 | percentile | |
|---|---|---|---|---|---|
| weekly $ @ DD | $1,154 | $1,375 | $1,872 | 28 % | generic |
| positive-week % | 60.6 | 58.3 | 61.5 | 82 % | generic |
| **mean top-5 drawdown** | **$11,004** | $13,918 | $11,274 | **98 %** | **SPECIFIC** |
| weekly streak | 4.0 | 6.8 | 4.0 | 92 % | generic |

> `RECORDED`: **the sleeve's DRAWDOWN benefit is specific to when it trades — it is not
> reproducible by an arbitrarily-timed stream — while its positive-week and money benefits are
> generic**, exactly as W74 found. So the sleeve does carry real timing information about P1's
> drawdowns. **It is just not stable enough across sub-periods to trade on** (§2: 24 %).

## 6. Exposure and friction — the improvement is not an exposure cut

At w = 0.30 nominal exposure is 0.70 + 0.30 = 1.00 unit, matched to P1 by construction.
Weighted round turns 2,104 vs P1's 2,007 (**+4.8 %**). C1 stress line: −$94/wk for P1,
−$99/wk for the pair. Stress-adjusted weekly: **P1 $1,221 vs pair $1,009.**

## 7. What this settles

- **P1 remains the baseline.** The pair is a documented alternative that carries its own numbers.
- **The four prior rejections stand on better grounds than they were given.** They cited
  efficiency and recency; the real reasons are sub-period instability of the drawdown gain and
  the absence of a stable weight.
- **A mirrored ratchet is not a genuinely different stream.** It is the same engine with a sign
  flip: it shares the engine's regime dependence, which is why its benefit concentrates in a
  minority of periods and why an honest refit oscillates between w = 0 and w = 0.5.
- This **strengthens** W74/W75's brief rather than weakening it: we need streams from genuinely
  different **mechanisms**, and the mirror does not qualify.

## 8. Files
`out/pair.txt` `out/console.log` · `out/rolling.csv` `out/nulls.csv` ·
code `research/weekly_edge/src/run_we_w78.py`
