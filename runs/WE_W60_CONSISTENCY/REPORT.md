# WE_W60 — THE CONSISTENCY CURVE · REPORT

Preregistered. Built only from what W59 licensed, entirely off W59's persisted cell series.
Reported consistency-first per Charter Amendment 2.

**VERDICT: nothing adopted. The wave establishes a DIRECTION that is stable in 100 % of
sub-periods, prices it, finds where it stops being cheap, and refutes my own stated mechanism
for one of the arms.**

---

## 1. The arms

All at a fixed **$20,245** max drawdown, so weekly dollars compare directly.

| arm | day + % | **traded-day + %** | week + % | wk streak | median week | **weekly $** | mean top-5 DD | **Ulcer** |
|---|---|---|---|---|---|---|---|---|
| **E  P1 incumbent** | 27.6 | 46.0 | 58.3 | 8 | $455 | **$1,475** | $14,266 | $6,183 |
| A  aggregate over HALT (4 cells, **no selection**) | 29.0 | 48.3 | 59.3 | 7 | $336 | $1,249 | $12,297 | **$4,222** |
| B  aggregate over HALT × TARGET (24 cells, **no selection**) | 28.4 | 47.3 | 57.8 | 7 | $364 | $1,127 | **$11,246** | **$3,899** |
| C  constrained walk-forward (1 step/quarter) | 30.2 | 50.4 | **60.3** | 8 | $461 | $791 | $10,659 | $4,866 |
| D  fixed h2000_t750 **[hindsight-flagged]** | **30.5** | **50.9** | 59.8 | **5** | **$767** | $1,445 | $12,455 | $4,308 |

## 2. Sub-period stability — the test that decides, and it is brutal

Fraction of the 22 rolling 24-month windows in which each arm beats the incumbent:

| arm | traded-day + % | weekly $ | mean top-5 DD | **all three** |
|---|---|---|---|---|
| A halt-aggregate | **100 %** | 36 % | 59 % | **0 %** |
| B halt × target | 91 % | 36 % | 64 % | **0 %** |
| C constrained WF | **100 %** | 36 % | 59 % | **0 %** |
| D h2000_t750 | **100 %** | 41 % | 36 % | **0 %** |

> `FACT`: **not one arm beats the incumbent on all three metrics in a single rolling 24-month
> window.** The traded-day improvement is perfectly stable — 100 % of windows for three
> independent constructions — and it is *always* paid for.

Per year, arm A's weekly-dollar delta is +41.5 %, +135.1 %, **−28.7 %, −47.3 %**, +54.8 %. The
money side is unstable in both directions; the consistency side is not.

That 100 %-in-every-window traded-day gain across three different constructions is what
separates this from a grid fit: **the direction is real. Only the price is uncertain.**

## 3. `REFUTED` — my own mechanism for the halt aggregate

I claimed the aggregate would help because *different halts fire on different days, so the halt
stops being all-or-nothing*. The check I preregistered for exactly this:

| sessions | count | incumbent $ | aggregate $ | **delta** | incumbent + day % | aggregate + day % |
|---|---|---|---|---|---|---|
| the 4 halts **DISAGREE** | 254 (25.1 %) | −$116,767 | −$121,560 | **−$4,792** | 23.2 % | **28.7 %** |
| the halts agree | 353 | $417,584 | $417,584 | **$0** | 62.3 % | 62.3 % |
| all flat | 405 | — | — | — | — | — |

The graded halt does act exactly where I said it would — the entire effect is on the 254
disagree sessions and the delta on agreeing sessions is exactly zero. **But it does not produce
a free gain there. It LOSES $4,792 on those sessions while raising their positive-day rate from
23.2 % to 28.7 %.** The mechanism is a consistency-for-money trade, not an improvement, and my
framing of it as a free benefit is withdrawn.

## 4. The nulls

| arm | traded-day + % | null mean | pct | weekly $ | null mean | pct | verdict |
|---|---|---|---|---|---|---|---|
| A halt-aggregate | 48.3 | 44.3 | **95.3 %** | $1,249 | $917 | **98.0 %** | **PASS** |
| B halt × target | 47.3 | 43.8 | **99.7 %** | $1,127 | $911 | **100.0 %** | **PASS** |
| C constrained WF | 50.4 | 46.4 | 99.3 % | $791 | $1,208 | **18.7 %** | fail |

`FACT`: against 300 random aggregates of the same size drawn from all 216 cells, **the HALT axis
specifically is the right axis** — A and B both clear on both metrics. That is a genuine
finding: aggregating over the halt is not the same as aggregating over anything.

`REPRODUCED`: even a *constrained* selector — one step per quarter on two monotone axes, a
hypothesis space of 24 rather than 216 — still sits at the **18.7th percentile on money**.
Selection loses at every scale tested in this campaign.

## 5. The curve — the deliverable

| arm | traded-day + % | weekly $ | vs incumbent | **$ per extra green day** |
|---|---|---|---|---|
| hinf_t500 | 55.8 | $782 | −47.0 % | $2,411 |
| hinf_t750 | 54.4 | $844 | −42.8 % | $2,580 |
| h2000_t500 | 52.9 | $1,066 | −27.7 % | $2,029 |
| **h2000_t750** | **50.9** | **$1,445** | **−2.0 %** | **$207** |
| **h1300_t1000 — the incumbent** | **46.0** | **$1,475** | — | — |
| h1300_t1500 | 44.0 | $1,522 | +3.2 % | — |
| h800_t750 | 43.2 | $1,657 | +12.3 % | — |

> `FACT`, and it is the most useful shape in the wave: **the curve has a kink.** Moving from the
> incumbent to h2000_t750 buys **+4.9 pp of traded-day rate at $207 per extra green day**.
> Every step beyond it costs **$2,029–$2,580 per green day — an order of magnitude more.**

**The cheap green days run out at h2000_t750.**

### What can honestly be said about that point

- **+4.9 pp traded-day rate, stable in 100 % of rolling 24-month windows** — and the same
  direction is 100 % stable for two other constructions, so it is the *direction* that is
  established, not one cell.
- **−2.0 % weekly dollars, and it beats the incumbent on money in 41 % of windows** — i.e. the
  cost is indistinguishable from zero.
- **Its −13 % drawdown improvement is NOT stable** (36 % of windows) and must not be claimed.
- It remains a **hindsight-selected cell**. What licenses the *direction* is the monotone
  surface and the 100 % sub-period stability across three constructions; what does not have an
  out-of-sample warrant is the specific stopping point.

## 6. The unifying result of W59 + W60

Four independent routes to higher consistency were tested on this one object — lowering the
profit target, raising the halt, aggregating the halt axis, and constrained selection — and
**every one of them buys green days with money at a stable rate, and none of them produces
consistency for free.** W59's exact accounting priced the target at ~$860 per green day; W60's
mechanism check found the halt aggregate losing $4,792 on precisely the sessions where it acts.

> `INFERENCE`, and it is the wave's real conclusion: **on a single engine, consistency and
> production are conjugate. You buy one with the other.** Getting both requires a second engine
> whose green days are not this one's — which is exactly what W58 concluded from the other
> direction when it measured that P1 is flat on 40 % of sessions by design and that the
> consistency objective and the breadth objective are the same problem.

## 7. Files
`out/consistency.txt` `out/arms.csv` `out/subperiod.csv` `out/nulls.csv` `out/curve.csv` ·
code `research/weekly_edge/src/run_we_w60.py`
