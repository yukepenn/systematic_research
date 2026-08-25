# WE_W11 — THREE UNTOUCHED DIMENSIONS · REPORT

## Axis 1 — TIME OF DAY: a real, cross-engine finding (FA does not fire)

Entry-segment attribution, two independent engines:

| segment | S1 net | S1 $/tr | S4n.A0.8 net | S4n $/tr |
|---|---|---|---|---|
| ASIA 18:00–02:59 | +$106,681 | 48.7 | **+$160,913 (40.2 %)** | **176.6** |
| EUROPE | +$35,066 | 12.6 | +$44,657 | 40.2 |
| PREOPEN | +$54,999 | 65.9 | +$9,507 | 28.7 |
| RTH_AM | +$101,567 | 20.6 | +$146,010 (36.5 %) | 97.9 |
| RTH_PM | +$97,703 | 42.9 | +$51,044 | 105.7 |
| **CLOSE 16:00–17:00** | **−$9,718** | **−35.2** | **−$11,930** | **−220.9** |

**Both engines lose in the CLOSE hour** — independent architectures agreeing on the same
segment is strong evidence, not a fitted slice. Dropping it: S1 Sharpe 0.176→0.179, stress
+$51; S4n.A0.8 Sharpe 0.210→**0.214**, weekly mean $1,431→**$1,484**, stress $1,250→$1,305.
Modest, free, and mechanically sensible (the last hour of a 23-hour session is thin and the
engines are forced flat into it).

Second finding: **the Asia session carries 40 % of S4n's net at $176.6/trade on 911 trades** —
the highest per-trade segment anywhere in the campaign.

## Axis 2 — MULTI-INSTRUMENT: the edge is NQ-SPECIFIC (axis closed)

Same engine, same throttle, own point values:

| instrument | trades | net | wk Sharpe |
|---|---|---|---|
| NQ | 4,383 | +$400k-class | 0.210 |
| ES | 3,685 | **−$30,529** | −0.037 |
| RTY | 2,285 | **−$16,358** | −0.013 |
| YM | 4,504 | **−$28,292** | −0.057 |

Weekly correlations are genuinely low (max off-diagonal 0.55, so FB does not fire) — but
diversifying into three losers is pointless: the equal-weight 4-instrument portfolio Sharpe is
**0.115 versus NQ-alone 0.210**. **Closed.** Recorded as a real constraint: whatever the
engine exploits is a property of NQ, not of index futures.

## Axis 3 — LOW-RANGE FADE: FC FIRED (final word on small days)

| k | trades | net | $/trade | wk Sharpe |
|---|---|---|---|---|
| 1.0 | 2,511 | −$76,471 | −30.5 | −0.208 |
| 1.5 | 2,447 | −$90,099 | −36.8 | −0.204 |
| 2.0 | 2,401 | −$112,016 | −46.7 | −0.216 |

Mean reversion to session VWAP in the low-range regime loses money at every threshold.
**The small-day regime is defensive-only** — W09's stand-aside is the correct and final
treatment, not a placeholder.

## New best object
`S4.narrow6.gdl + A_range0.8 + drop CLOSE segment`: dev weekly $1,484 / 59.6 % / −$25,032 /
Sharpe 0.214 / stress $1,305; holdout Sharpe 0.666.
