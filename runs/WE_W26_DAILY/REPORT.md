# WE_W26 — DAILY CONSISTENCY · REPORT

## M1 — the daily truth, stated plainly

| object | traded days | **% days positive** | median day | **top 5 % of days deliver** | longest losing streak |
|---|---|---|---|---|---|
| E5halt1300 (1 contract) | 683 | **43.2 %** | **−$279** | **109.2 %** of all P&L | 17 days |
| E5halt + S1 (≤2) | 1,134 | 51.9 % | +$187 | 119.9 % | 10 days |
| E5halt + S1 + short (≤3) | 1,136 | 50.5 % | +$59 | 128.9 % | 9 days |

**This system does not make money every day, and it never will in this architecture.** It wins
43–52 % of the days it trades, its median day is around break-even, and the best 5 % of days
deliver *more than 100 %* of total profit — meaning the other 95 % of days are collectively
negative. Longest losing streak: 9–17 consecutive trading days. Any claim of daily consistency
from a trend harvester would be false, and this table is why.

## M3 — but the session PROFIT TARGET is a genuine four-way improvement

| lever on E5halt1300 | % days pos | wk Sharpe | worst week | top 5 % share |
|---|---|---|---|---|
| base | 43.2 % | 0.273 | −$8,769 | 109.2 % |
| **+ session target +$1,000** | **46.1 %** | **0.305** | **−$7,487** | **96.8 %** |
| + session target +$2,000 | 44.1 % | 0.284 | −$8,769 | 93.1 % |
| partial profit +30 / +60 pts | 43.6 / 39.1 % | 0.222 / 0.236 | −$14,517 / −$10,905 | rejected |
| early flat 15:00 ET | 43.1 % | 0.245 | −$7,510 | rejected (streak 21) |

**ADOPTED: stop trading the session once realised session P&L reaches +$1,000.** Daily hit rate
up, weekly Sharpe up to the campaign's best (0.305), worst week better, and concentration falls
(top-5 % share 109.2 % → 96.8 %). Mechanically it is the other half of the session halt: the
**session box** — stop at −$1,300, stop at +$1,000. Both truncate the same accumulation process.

Note on selection: the target was chosen from two declared values and the response is
monotone (none 0.273 → $2,000 0.284 → $1,000 0.305), not a spike. A circular-shift null on
this lever is queued.

## The campaign's best objects after this wave

| object | contracts | % days pos | weekly | **% weeks pos** | worst week | Sharpe |
|---|---|---|---|---|---|---|
| **E5 (halt −$1,300 + target +$1,000)** | 1 | 46.1 % | $1,060 | 59.1 % | **−$7,487** | **0.305** |
| **E5box + S1 + short box** | ≤3 | 52.7 % | **$3,030** | **64.9 %** | −$23,374 | 0.285 |
| (previous reference) E5halt + S1 | ≤2 | 51.9 % | $2,508 | 59.5 % | −$21,514 | 0.259 |

The three-sleeve box version beats the previous reference on every axis at once: +20.8 %
weekly, +5.4 pp positive weeks, +0.026 Sharpe, and an 8.6 % smaller tail.
