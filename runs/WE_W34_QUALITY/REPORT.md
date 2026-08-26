# WE_W34 — QUALITY SIZING · REPORT

**The campaign's first adopted sizing rule, and its largest production gain.**
(Amendment 1: a one-bar look-ahead in feature F2 was found in the mandatory causality review
and corrected before write-up. Run 1's 0.338 / 16.19 became 0.331 / 15.86 — the finding stands
and the suspended numbers are superseded.)

## Result

| | base | **quality-sized (score ≥ 3 → 2 contracts)** |
|---|---|---|
| pts/session | 10.62 | **15.86 (+49 %)** |
| $/trade | $103.9 | **$165.2 (+59 %)** |
| weekly | $1,060 | **$1,583** |
| % weeks positive | 59.1 % | 59.6 % |
| worst week | −$7,487 | **−$7,418** (better) |
| Sharpe | 0.305 | **0.331** |
| **average contracts** | 1.00 | **1.19** |
| circular-shift null | — | **98th percentile, p = 0.020 — EVIDENCE** |

**+49 % production for +19 % average exposure** — 2.6× the production per unit of exposure —
with the tail slightly improved and Sharpe up. Filtering on the same score was rejected
(it cuts production to 2.86–5.32 pts/session): the quality signal must be used to **size**,
never to **select**.

## The leverage law, restated correctly

This campaign rejected exposure sizing three times and recorded it as a law. The law was
stated too broadly. All three rejected rules scaled with information **the object already
trades on**:

| rejected rule | scaled with | already used as |
|---|---|---|
| W06 pyramid | the same trade's unrealised profit | the position itself |
| W10 range-proportional | the realised-range ratio | the throttle |
| W22 vote-conviction | the vote fraction | the entry rule |

Doubling down on a signal you already act on is leverage. **F5 (distance from session open),
F11 (prior-session return — a contrarian conditioner on a trend system), F14 (run length),
F4 (distance from VWAP) and F2 (delta magnitude) are used nowhere in the object.** Sizing on
genuinely new information is a different proposition, and it passes the same Sharpe test the
other three failed.

Feature independence was verified before use: maximum pairwise |r| at the entry bars is 0.68
(F5 vs F4), below the 0.7 collapse threshold, so all five count separately.

## New best objects

| portfolio | max contracts | pts/session | weekly | % weeks + | % days + | worst week | Sharpe |
|---|---|---|---|---|---|---|---|
| E5 box (previous best, 1c) | 1 | 10.62 | $1,060 | 59.1 % | 46.1 % | −$7,487 | 0.305 |
| **E5 quality-sized** | 2 | **15.86** | **$1,583** | 59.6 % | 45.1 % | **−$7,418** | **0.331** |
| + S1 | 3 | 29.91 | $2,956 | 60.0 % | 52.5 % | −$19,016 | 0.293 |
| **+ S1 + short box** | 4 | **35.90** | **$3,548** | **65.4 %** | 52.1 % | −$23,579 | 0.308 |

The four-sleeve object delivers **$3,548/week at 65.4 % positive weeks** — the highest
positive-week rate the campaign has produced — against the previous best of $3,030 at 64.9 %.
