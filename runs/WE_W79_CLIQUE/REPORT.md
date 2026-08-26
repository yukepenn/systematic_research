# WE_W79 — THE THREE-STREAM CLIQUE, TESTED PROPERLY · REPORT

Preregistered. Members `{AXISB, BMOM, X9a}` at frozen parameters, rebuilt on the **extended**
window (1,058 sessions / 213 weeks, including W76's 46 never-previously-read sessions).
Equal-weight and inverse-vol only — no optimised weights.

> ## VERDICT: **FAILS gate 1 (ALL THREE = 0 %).** And it surfaced a correction that matters more
> ## than the verdict: **K_admissible is 1, not 2.**

---

## 0. A premise of mine, measured false before this wave was written

At the end of W78 I said the next move was an **overnight-only engine**, because P1 barely trades
18:00–09:29 so temporal disjointness would guarantee ρ ≈ 0. I measured it first:

| segment | in-market bars | share | entries | net | share of net |
|---|---|---|---|---|---|
| **OVERNIGHT 18:00–09:29** | 162,882 | **59.0 %** | 1,465 | **$167,064** | **59.7 %** |
| RTH 09:30–16:00 | 104,595 | 37.9 % | 793 | $110,458 | 39.5 % |
| POST 16:00–17:00 | 8,378 | 3.0 % | 14 | $2,231 | 0.8 % |

**The overnight tape is P1's primary venue, not empty space.** The structural argument is dead and
the wave was withdrawn unrun. (Second time this session that measuring before coding saved a
wasted wave.)

## 1. `CORRECTION` — AXISB fails the recency gate on the corrected data

W75's census admitted AXISB as P1's only partner on the strength of its 2026 figure of
**+$19,340**. That was measured on the **truncated** substrate. Rebuilt at frozen parameters on
the extended window:

| AXISB, weekly $ | 2022 | 2023 | 2024 | **2025** | **2026** |
|---|---|---|---|---|---|
| | **−$436** | **−$48** | **−$41** | **+$1,201** | **−$126** |

Full window net **$43,766** (was $66,581 truncated), weekly **$205**, max drawdown **$55,739**.
In W76's held-out 46 sessions it lost **$23,250** — worse than P1's −$20,686.

> **Every dollar AXISB has ever made is 2025.** It is negative in four of five years and negative
> in 2026. It does **not** pass the owner's binding 2025-AND-2026 recency gate.

> ### `RECORDED`: **K_admissible = 1.** On corrected data this repo has **no** stream that is both
> decorrelated from P1 (ρ < 0.2) and recently effective. W74 says the campaign's target needs
> **six**. W75's answer of 2 was an artifact of the truncated substrate.

The correlation structure itself survived re-measurement (max pairwise |ρ| among the three
members 0.156, still a clique) — the failure is recency, not independence.

## 2. The panel — the full-sample table still looks good

| object | net | week + % | wk streak | median week | weekly $ | **wk $ @ fixed DD** | top-5 DD | **max DD** | worst |
|---|---|---|---|---|---|---|---|---|---|
| AXISB | $43,766 | 52.6 % | 6 | $170 | $205 | $75 | $9,562 | $55,739 | −$14,329 |
| BMOM | $252,258 | 57.7 % | **4** | **$1,153** | $1,184 | $549 | $12,673 | $43,712 | −$16,907 |
| X9a | $233,781 | 53.5 % | 7 | $280 | $1,098 | $923 | $13,873 | $24,075 | −$8,658 |
| **clique equal-weight** | $176,602 | 57.3 % | 6 | $786 | $829 | **$1,080** | **$11,668** | **$15,548** | **−$5,976** |
| **clique inverse-vol** | $166,552 | **59.6 %** | 5 | $715 | $782 | **$1,112** | $12,372 | **$14,233** | **−$4,971** |
| P1 (reference) | $280,131 | 56.3 % | 8 | $279 | $1,315 | $1,099 | $13,864 | $24,225 | −$7,418 |

Max drawdown **$14,233 against P1's $24,225** and a worst week of **−$4,971 against −$7,418**.
That is what made this the best-looking object in the repo.

## 3. Gate 1 — rolling 24-month windows. **FAIL, at zero** (`FACT`)

| portfolio | weekly $ @ DD | positive-week % | mean top-5 DD | **ALL THREE** |
|---|---|---|---|---|
| clique equal-weight | **96 %** | 60 % | **4 %** | **0 %** |
| clique inverse-vol | 88 % | 68 % | **4 %** | **0 %** |
| drop AXISB | 80 % | 88 % | 4 % | **0 %** |
| drop BMOM | 20 % | 52 % | 4 % | **0 %** |
| drop X9a | 0 % | 32 % | 36 % | **0 %** |

The decomposition is decisive. The clique beats P1 on money-at-fixed-drawdown in **96 %** of
windows and on the positive-week rate in **60 %** — but on the **drawdown distribution in 4 %**.
**The full-sample −41 % maximum drawdown that motivated the whole wave is present in one window
out of twenty-five.** It is a single avoided episode, not a property.

## 4. The null — everything is GENERIC (`FACT`)

200 draws, each member's daily series shifted independently, every marginal preserved exactly:

| metric | real | null mean | percentile | |
|---|---|---|---|---|
| weekly $ @ DD | $1,080 | $1,027 | 60 % | generic |
| positive-week % | 57.3 | 59.1 | **15 %** | generic |
| mean top-5 DD | $11,668 | $13,632 | 83 % | generic |
| weekly streak | 6.0 | 4.8 | 9 % | generic |

**Not one metric reaches the 95th percentile, and two are BELOW the null's mean.** A randomly
re-timed version of the same three streams does as well or better. Exactly what W74 predicted:
the value is *three streams*, not *these three streams*.

## 5. What did pass, stated fairly

- **Walk-forward: 86 % retention** (bar 80 %), churn 27 %, and the quarterly choice **converges**
  to inverse-vol in the last five refits — better behaved than W78's pair, which oscillated.
- **2026 positive** on the extended window (+$15,914 vs P1's +$12,781).
- **Not carried by one member** — no two-member subset beats the three.
- In W76's held-out 46 sessions the clique lost **$8,167 against P1's $20,686** (−60 %), with
  22.2 % positive weeks against 11.1 %. Nine weeks ranks nothing, but it is the right sign.

## 6. The meta-finding, and it is the most useful thing here

This is the **sixth** consecutive object whose full-sample dominance evaporated under
sub-period testing: W40 axis B, W41 clock basket, W61 short sleeve, W66 C2r, W78 the pair, and
now W79 the clique.

> `RECORDED`: **in this campaign, full-sample dominance is nearly uninformative.** Six for six.
> The rolling-window and walk-forward tests are where the information is, and the honest
> workflow is to run them **first** — before writing a report around a full-sample table, and
> before telling the owner something looks good.

Note also which sub-metric keeps failing: **the drawdown distribution, at 4–24 % of windows,
every single time.** Money and hit-rate improvements replicate across sub-periods; drawdown
improvements do not. That is a specific, repeated, mechanical fact about this problem and it
should be treated as a prior, not rediscovered a seventh time.

## 7. Files
`out/clique.txt` `out/console.log` · `out/members.csv` `out/rolling.csv` `out/nulls.csv` ·
code `research/weekly_edge/src/run_we_w79.py`
