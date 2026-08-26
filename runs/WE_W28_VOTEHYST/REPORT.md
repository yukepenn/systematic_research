# WE_W28 — VOTE HYSTERESIS / OWED NULLS / 2025 · REPORT

## H — vote hysteresis looks good and is REJECTED by its own null

| H_in / H_out | trades | weekly | % weeks | worst | Sharpe |
|---|---|---|---|---|---|
| 0.50 / 0.50 (baseline) | 2,334 | $1,060 | 59.1 % | −$7,487 | 0.305 |
| **0.60 / 0.40** | 1,641 | $1,098 | 58.9 % | **−$6,863** | **0.324** |
| 0.50 / 0.30 | 1,900 | $1,064 | 58.6 % | −$9,571 | 0.293 |
| 0.60 / 0.30 | 1,255 | $1,054 | 58.9 % | −$11,281 | 0.298 |

(0.60/0.40) beats the baseline on Sharpe *and* tail on 30 % fewer trades — and its
circular-shift null puts the gain at the **63rd percentile, p = 0.370: NOT EVIDENCE.**
Rejected. Vote-level hysteresis does not inherit the member-level result of W04. This is the
fourth improvement this campaign has killed with its own null.

## N — the owed session-halt null is PAID and PASSES

| mechanism | real gain | null mean | null p95 | percentile | p | verdict |
|---|---|---|---|---|---|---|
| **session halt −$1,300** | **+0.059** | −0.002 | +0.048 | **98.0** | **0.020** | **EVIDENCE** |
| session target +$1,000 (W27) | +0.032 | −0.005 | +0.041 | 88.0 | 0.120 | weak |
| vote hysteresis 0.6/0.4 | +0.019 | +0.003 | +0.061 | 63.0 | 0.370 | NOT EVIDENCE |

**Three mechanisms now clear their nulls at ≥95 %**: the vote itself (98th, W21), the range
throttle (95th, W13), and the session halt (98th). That is the audited core.

## Y — CORRECTION: 2025 is not a weak year; my earlier claim measured the un-boxed version

| 2025 | net | Sharpe | % weeks + |
|---|---|---|---|
| **with the session box** | **$70,346** | **0.311** | 53.8 % |
| without the box (what W20/W21 reported) | $40,895 | 0.113 | 61.5 % |

The "weak 2025" cited in W20, W21 and the state document was the **pre-box** object. With the
box the year is in line with every other. Corrected everywhere it appears.

## Per-trade expectancy has risen monotonically for five years

| year | trades | net | **$/trade** | win % | avg win | avg loss | wk Sharpe |
|---|---|---|---|---|---|---|---|
| 2022 | 489 | $17,443 | $35.7 | 35.6 % | $941 | −$464 | 0.102 |
| 2023 | 582 | $23,967 | $41.2 | 37.3 % | $705 | −$353 | 0.189 |
| 2024 | 628 | $65,437 | $104.2 | 36.8 % | $829 | −$317 | 0.376 |
| 2025 | 457 | $73,532 | $160.9 | 40.7 % | $1,047 | −$447 | 0.326 |
| **2026 (7 mo)** | 178 | $36,919 | **$207.4** | 39.9 % | $1,498 | −$649 | **0.454** |

**$207/trade in 2026 is double his $103 gross.** Honest attribution: NQ's price level rose
~2.4× over the span, which scales point moves in dollars, so roughly 2.4× of the 5.8× is price
and the remainder is genuine improvement; and 2022 was a bear year, structurally the worst case
for a long-biased system. The weak year of this object is **2022 (0.102)**, not 2025 — and that
is exactly what a long-biased trend harvester should look like.
