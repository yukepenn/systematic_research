# WE_W82 — WHAT A ROUND TURN ACTUALLY COSTS · REPORT

Preregistered + amendment 1 (a defect found in read 1's secondary estimate, diagnosed and fixed).
3.7 million two-sided second-quotes, 45 usable sessions, 2025-08 → 2026-05.

> ## **The measured all-in spread cost at P1's own trading times is 2.93 ticks = $14.65 per round
> ## turn.** The campaign's headline assumes **$0**. Its "stress line" assumes **$10**.
> ## **The conservative column has been optimistic for 82 waves.**

---

## 1. Why this was the highest-value measurement left

Every figure this campaign has produced is *"net of $4.36/RT commission"*, with fills simulated as
a market order at the next 1-minute bar's **open** and **no spread cost at all**. The C1 stress
line adds $10/RT, described in `run_we_w01.py:37` as *"2 NQ ticks on top of commission"*. **That
2-tick figure was an assumption and had never been checked against a quote in 82 waves.**

And W79 had just measured that **P1 takes 59.7 % of its net overnight** — precisely where the
spread is widest.

## 2. The spread, measured (`FACT`)

| segment | seconds | **median (ticks)** | mean | p90 | median $/RT |
|---|---|---|---|---|---|
| **OVERNIGHT 18:00–09:29** | 2,511,000 | **3.00** | 3.87 | 5.00 | **$15.00** |
| RTH 09:30–16:00 | 1,029,565 | **2.00** | 2.51 | ~~4.00~~ **3.00** | $10.00 |
| POST 16:00–17:00 | 149,227 | 2.00 | 2.64 | 4.00 | $10.00 |
| **ALL** | 3,689,792 | **3.00** | ~~3.44~~ **3.22** | 5.00 | $15.00 |

> **Amendment 2**: four sessions carry frozen forward-filled feeds that the `bid>0` filter cannot
> see (a dead quote scores 1.00); 6 % of all second-quotes sit in runs longer than 60 s. The
> **means and the RTH p90 above are corrected** for that. **The medians — and therefore the
> headline — are unchanged**, because the weighted estimate is built from per-minute medians.

**NQ is not 1 tick wide.** Even in RTH the median is 2 ticks; overnight it is 3, with a 90th
percentile of 5.

And P1's fills sit where it is worst — **61.6 % overnight**, 35.5 % RTH, 2.9 % post.

### The weighted estimate — the one the spec named as decisive

P1's own fill time-of-day distribution (all 4,020 fills over 1,058 sessions) applied to the
spread profile from all 3.7 M seconds:

> **2.93 ticks = $14.65 per round turn**
> overnight-only **3.19 ticks / $15.97** · RTH-only **2.55 ticks / $12.76**

This estimate uses **only differences** (`ask − bid`) and never a price level, which is what makes
it immune to the defect in §4.

## 3. P1 re-quoted (`FACT`)

P1 trades **11.15 contract round turns per week**.

| cost line | extra $/RT | $/week | **full window** | **trailing 12m** | **2026** |
|---|---|---|---|---|---|
| headline (commission only) | $0.00 | $0 | $1,315 | $879 | $412 |
| C1 stress line (assumed 2 tk) | $10.00 | $112 | $1,204 | $767 | $301 |
| **MEASURED (2.93 tk)** | **$14.65** | **$163** | **$1,152** | **$716** | **$249** |

**Annualised per unit (≈1.27 NQ contracts) at the measured cost:**
full window **$59,888** · trailing 12 months **$37,209** · **2026 $12,938**.

The haircut is **−12 % on the full window, −19 % on the trailing year and −40 % on 2026** — the
cost is fixed per trade while the edge has shrunk, so it bites hardest exactly where it hurts.

> ⚠️ **WITHDRAWN (amendment 2).** This paragraph originally read *"at $14.65 it is roughly
> −$81,000"* and it was wrong twice. (a) It charged the stress line **per trade** (9,557) when
> W80 charges it **per contract** (11,557) — the correct arithmetic is **−$90,234**. (b) More
> importantly, **the whole extrapolation is unsupported**: the $14.65 is measured at NQ
> 23,036–29,479 and 2006–2021 traded at NQ 1,600–16,000. A point-denominated spread does not
> transport across a 10× price level. **No deep-history re-quote is made.**

## 4. `CORRECTION` — the secondary estimate was void, and why the headline is not

Read 1 reported *"the simulated open sits outside the quote on **100.0 %** of fills"*. 100 % is not
disagreement, it is systematic misalignment, and the spec required diagnosis rather than averaging.

> **The 1-minute substrate is BACK-ADJUSTED CONTINUOUS; the 1-second grid is the RAW FRONT MONTH.**
> Measured across 1,379 overlapping minutes on 2026-05-20: minute-close minus 1-second-last is
> **median +282.25, mean +282.25, sd 0.18** — a constant additive roll offset.

A second, smaller defect: read 1 read the quote at `T−60s` for a bar end-stamped `T`; the grids
align as `(T−59s … T]`, so a bar's open is at `T−59s`. Both grids are bar-END stamped, confirmed
by the offset matching exactly.

**The headline is unaffected**: a spread is a difference of two prices from the *same* raw series,
so an additive offset cancels exactly. Nothing in §2 or §3 used a level.

**Corrected direct measurement** (per-session offset removed, alignment fixed):

| | read 1 | corrected |
|---|---|---|
| open inside the quote | **0.0 %** | **29.2 %** |
| median spread at those fills | — | **4.00 ticks** |
| cost omitted per side | — | median 2.00 tk / mean 2.40 tk |
| **per round turn** | — | **$24.00** |

`CAUTION, and it is why this is not the headline`: only 35 of 120 overlapping fills have the open
inside the quote, so this is a **selected** subsample of ~35 fills from 45 sessions. It suggests
the true cost may be **higher** than $14.65 — but it cannot establish it. The two estimates agree
on direction and differ on magnitude; **the campaign should carry $14.65 as the working number and
treat $24 as the pessimistic bound.**

## 5. Microstructure predictive power — **UNDERPOWERED**, stated in the heading

Power computed before the measurement, per method rule 25. Only **64 of 2,010 entries** have quote
coverage, so the smallest |Spearman| detectable at t = 2 is **2/√64 = 0.250** — against W55's
measured ceiling of **|ρ| < 0.11** across 16 minute-level features.

**This test cannot resolve effects of the size this problem is known to produce.** Descriptive
only:

| feature | ρ | \|t\| |
|---|---|---|
| 1s realised vol | −0.147 | 1.17 |
| trade intensity | −0.127 | 1.01 |
| spread | +0.123 | 0.98 |
| quote imbalance | −0.104 | 0.82 |
| signed flow | −0.039 | 0.31 |
| quote-update intensity | −0.034 | 0.27 |

Nothing reaches |t| = 2 and nothing could have. **Forty-five sessions cannot answer whether
microstructure information is worth buying.** What they *can* answer — and did — is what the fills
cost.

## 6. Consequences

1. **Every stress-net figure for 2022–2026 is overstated** — the C1 line is 32 % too cheap
   against the working estimate. ⚠️ **Amendment 2 narrows this**: the original sentence said
   *"every stress-net figure in the repository"*, which over-reached. The estimate covers
   **2.5 %** of P1's contract round turns, all at 2025–26 price levels, and **does not transport
   to 2006–2021**.
2. **`WHAT_P1_ACTUALLY_DELIVERS.md` is re-quoted** at the measured cost.
3. **The fourth cross-substrate alignment defect in this repository's history** (W44's basis check
   on the wrong series, W52's timestamp shift, W76's truncated loader, now this). The rule that
   keeps catching them: **assert the join, never assume it.** Read 1 printed its disagreement rate
   only because the spec demanded it — without that line, a correct $14.65 headline would have
   shipped beside a silently nonsensical secondary estimate.

## 7. Files
`out/fillaudit.txt` `out/console.log` · `out/spread_by_minute.csv` `out/power.csv` ·
`amendment_1.yaml` · code `research/weekly_edge/src/run_we_w82.py`
