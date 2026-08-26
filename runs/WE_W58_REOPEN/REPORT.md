# WE_W58 — REOPENED UNDER THE CORRECTED CRITERION · REPORT

Preregistered. Runs off the series persisted in W56, so it cost no re-simulation.
Reported **consistency-first** per Charter Amendment 2: Sharpe decides nothing.

**VERDICT: the corrected chronology gate passes all four candidates — and the rolling-window
test that the spec required alongside it fires the falsifier on two of the three sleeves.
Nothing adopted. But the wave produced the campaign's first consistency ledger and it changes
what the next object should look like.**

---

## 1. Phase 1 — "recent effectiveness" asked properly

"It works in the last two years" is trivially satisfiable, so the spec required every rolling
24-month window, compared on the **scale-free t** (NQ's price and daily range grew ~6× over this
sample, so comparing dollars across decades measures the instrument, not the edge):

| sleeve | windows | eff. independent | % positive | median t | latest t | **percentile of its own t-history** |
|---|---|---|---|---|---|---|
| **P1** | 31 | 1 | **100.0 %** | **2.76** | 3.57 | **74 %** |
| axis B | 37 | 2 | 43.2 % | −0.28 | 1.96 | **97 %** |
| B-MOM | 234 | 10 | 57.7 % | 0.25 | 2.14 | **98 %** |
| BREADTH01 | 255 | 11 | 82.0 % | 0.66 | 0.89 | **68 %** |

`FACT`, and it is the most reassuring number in the campaign: **P1 is positive in 100 % of its
rolling 24-month windows with a median t of 2.76, and its current run sits at only the 74th
percentile of its own history — it is not having an exceptional run, it is behaving normally.**

`FACT`, and it fires this wave's falsifier: **axis B (97th) and B-MOM (98th) are each having the
best two-year run of their own recorded history.** Their "recent effectiveness" is satisfied by
an exceptional stretch, not by a durable edge. Axis B is positive in only **43.2 %** of its
rolling windows with a **negative median t**; B-MOM in 57.7 % with a median t of **0.25**.

`FACT` — **BREADTH01 is the only sleeve whose recent run is representative** (68th percentile,
positive in 82 % of 255 windows). Its problem is not durability, it is size: median t = 0.66.

Caveat carried with all of it: 24-month windows stepped monthly overlap by 23/24, so the
effective number of independent observations is windows ÷ 24 — **1 for P1, 2 for axis B, 10 for
B-MOM, 11 for BREADTH01.** Axis B's "97th percentile" rests on two effectively independent
observations and should not be over-read.

## 2. Phase 2 — the consistency ledger, the campaign's first

Every row rescaled to the **same $20,245 max drawdown**, so weekly $ is comparable.

| arm | **day + %** | traded-day + % | flat % | **week + %** | worst wk-streak | **median week** | **weekly $** | mean top-5 DD | worst week |
|---|---|---|---|---|---|---|---|---|---|
| **P1 incumbent** | **27.6** | 46.0 | 40.0 | 58.0 | 8 | $433 | $1,467 | $14,266 | −$7,418 |
| P1 + axis B w=0.05 | 47.1 | 47.9 | 0.2 | 58.0 | 8 | $475 | $1,499 | $13,987 | −$7,130 |
| P1 + axis B w=0.10 | 47.3 | 47.9 | 0.2 | 59.0 | **4** | $620 | $1,535 | $13,690 | −$7,563 |
| P1 + B-MOM w=0.15 | 47.8 | 50.3 | 4.9 | **61.0** | 8 | $485 | $1,708 | $13,745 | −$7,647 |
| P1 + B-MOM w=0.40 | 49.1 | 51.7 | 4.9 | 60.0 | 6 | $965 | **$2,301** | $16,182 | −$13,782 |
| P1 + BREADTH w=0.35 | 48.5 | 49.4 | 2.1 | **61.5** | **4** | $555 | $832 | **$11,493** | −$7,176 |
| P1 + BREADTH w=0.50 | 50.1 | 51.0 | 2.1 | 58.0 | **4** | $418 | $487 | **$10,254** | −$5,652 |

**Exactly one row dominates the incumbent on all five of {positive days, positive weeks, weekly
dollars, mean top-5 drawdown, worst week}: P1 + axis B at w = 0.05.** It is a tiny allocation
and its gains are correspondingly tiny except on the day rate.

### The caveat that must travel with the positive-day column

**The jump from 27.6 % to ~47 % is mostly arithmetic, not edge, and it is available at w = 0.05
from any of the three sleeves.** P1 is flat on 40 % of sessions; adding *any* non-flat series
makes those days non-zero, and a coin flip would win about half of them:

> 0.60 × 46.0 % + 0.40 × 50 % = **47.6 %** — which is what every w = 0.05 row shows.

So **positive-day rate must never be optimised on its own** — it is gameable by adding noise. It
is meaningful only jointly with money and drawdown, which is how the table above is ordered.

### The mechanism, measured

| sleeve | both trade | **only the sleeve** | only P1 | both flat | sleeve's win rate on P1's flat days |
|---|---|---|---|---|---|
| axis B | 607 | **403** | 0 | 2 | 49.4 % |
| B-MOM | 574 | **355** | 33 | 50 | **56.9 %** |
| BREADTH01 | 597 | **384** | 10 | 21 | 52.3 % |

B-MOM is the only sleeve that wins materially more than a coin flip on the sessions P1 sits out
(56.9 %) — which is exactly where its portfolio value comes from, and exactly the claim its
in-sample status leaves unresolved.

## 3. Phase 3 — re-adjudication

Trailing 24 months, 2024-05-29 → 2026-05-29:

| candidate | sessions | daily mean ± SE | t | day + % | chronology gate | **remaining objection** |
|---|---|---|---|---|---|---|
| P1 | 311 | $696.80 ± $191.73 | 3.63 | 48.6 % | **PASS** | it is the incumbent |
| axis B | 517 | $171.32 ± $99.36 | 1.72 | 51.1 % | **PASS** | statistical: near-zero full-window expectancy, 92nd-pct count-matched null, **and now: 43 % of its rolling windows are positive with a negative median t** |
| B-MOM | 515 | $361.70 ± $179.71 | 2.01 | 51.1 % | **PASS** | **in-sample**: 2022–2026 is its own development window, **and now: latest run at the 98th percentile of 234 windows** |
| BREADTH01 | 501 | — | 1.02 | 53.7 % | **PASS** | statistical: 4th percentile of its own null in W56; edge is small (median t 0.66) |

**Chronological objections are void for all three** — that is what the corrected criterion
does, and it is a real change from W40's and W57's verdicts. What remains is statistical or
in-sample in every case, and the rolling-window evidence added here is *new* and adverse for
axis B and B-MOM.

## 4. Phase 4 — the positive-day ceiling, arithmetic

P1 trades **60.0 %** of sessions and wins **46.0 %** of those → 27.6 % of all sessions positive.

| if we could… | positive-day rate | gain |
|---|---|---|
| (current) | 27.6 % | |
| trade 80 % of sessions at the same win rate | 36.8 % | +9.2 |
| trade 100 % of sessions at the same win rate | 46.0 % | +18.4 |
| keep the same days but win 55 % of them | 33.0 % | +5.4 |
| keep the same days but win 60 % of them | 36.0 % | +8.4 |

> `FACT`: **no entry-side improvement can lift P1's all-session positive rate above 60 %,
> because it is flat on 40 % of sessions by design** (the range throttle and the session box).
> Raising it *requires* either trading more sessions or a sleeve that trades the ones P1 sits
> out. **The consistency objective and the breadth objective are the same problem.**

That is the specification for the CONSISTENCY object the charter has always named and this
campaign has never built.

## 5. What this changes

- **W40 axis B's chronological rejection is void** — but the rolling-window test replaces it
  with a *better* objection: 43 % positive windows, median t −0.28, current run at the 97th
  percentile of two effectively independent observations.
- **B-MOM's chronological objection is void**; its in-sample objection stands and is now joined
  by a 98th-percentile-of-234-windows result.
- **BREADTH01 is promoted in standing**, not because it earns more — it earns less — but because
  it is the only candidate whose current run is *representative*, and because at w = 0.35–0.50 it
  cuts the mean top-5 drawdown by **19–28 %** and the longest weekly losing streak from **8 to 4**.
- **P1 itself is the most robust thing here**: 100 % of rolling 24-month windows positive,
  current run at the 74th percentile.

## 6. Files
`out/reopen.txt` `out/rolling24.csv` `out/consistency.csv` `out/dayoverlap.csv` ·
code `research/weekly_edge/src/run_we_w58.py`
