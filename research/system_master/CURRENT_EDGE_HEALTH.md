# CURRENT_EDGE_HEALTH — Product B current-regime health, future-readiness

Written 2026-08-09 per the owner's ADDENDUM — CURRENT-REGIME HEALTH AND FUTURE-READINESS.
Scope: Product B shared decision core (BEST_ONE_NQ/BEST_ONE_MNQ), same object studied throughout
SA0. Product A gets its own current-health pass inside PA0 (deferred; light context only below).
Full evidence/scripts: `runs/SA0_SYSTEM_STRUCTURE/current_health/`.

## Two distinct windows — do not conflate them

- **Canonical comparison window** (frozen, used for every formal metric/gate in this campaign):
  2022-01-03 → 2026-05-29, 1,139 sessions. Net $301,915.92, Sharpe 1.1131 (`BASELINE_MODELS.md`).
- **Current-health window** (observational monitoring only, NOT used for tuning or promotion
  gates): extended to **2026-07-31**, the latest bar data already present in this repo's own
  price file that is not still locked-forward (`research/operational/LOCKED_FORWARD.md` seals
  ≥2026-08-01). 2026-06-01→2026-07-31 was already read once for a different purpose in
  `SM11_HOLDOUT_READ` (`CURRENT_TRUTH.md` Wave-18: "nothing left to seal" for that window), so
  reusing it here for health monitoring is consistent with that prior determination, not a new
  breach. This is a CONTINUATION run from the same 2022-01-03 start (no fresh-start warmup
  artifact) — verified byte-exact against the certified canonical net when sliced back
  (`health_substrate.py`'s own correctness gate, and independently against P0's certified
  block-level summary in `02_extended_block_ledger.py`). No external data was acquired; nothing
  beyond what this repo already had loaded.

## Headline answer to the owner's core question

**As of the latest available (non-locked) data, the system looks healthier than the canonical
window's own recent stretch suggested — including specifically on the short side the owner's own
April review flagged.** The picture is NOT "2026 is broken" — it is "2026 had a genuinely weak
Jan-May stretch (already well-studied in R2V1/CURRENT_TRUTH), followed by a real recovery in
June-July that the canonical window's own end-date (2026-05-29) cuts off before it's visible."

## 1. Current rolling dashboard (as of 2026-07-31)

| window | net | Sharpe | net percentile | Sharpe percentile | n trades | expectancy/trade | win rate |
|---|---:|---:|---:|---:|---:|---:|---:|
| rolling 20 | +$20,289.96 | 3.197 | 86.5th | 78.4th | 39 | $526.30 | 41.0% |
| rolling 60 | +$34,606.68 | 1.308 | 81.9th | 50.4th | 112 | $313.85 | 40.2% |
| rolling 120 | +$22,110.80 | 0.481 | 36.2nd | 23.1st | 220 | $105.91 | 40.5% |

Current drawdown: **$5,625.20** (34.0th percentile of all historical daily drawdown readings —
unremarkable, not deep). Current time-underwater: 36 sessions. Current losing-session streak: 1
(i.e. the latest session was a winner). **The rolling-120 window is still weak (23rd percentile
Sharpe) because it still contains the Jan-May 2026 stretch; the rolling-20/60 windows, which are
dominated by June-July, are strong-to-very-strong.** This is exactly the "recent recovery inside
a still-recovering longer window" pattern, not a contradiction.

Latest-60-session split: **short ($22,954.20) actually OUTPERFORMED long ($12,197.02)** —
directly counter to the full-history pattern (SA0: shorts Sharpe 0.18 vs longs 1.54) and to the
Jan-May 2026 stub pattern (short -$57,958). Overnight P&L (+$42,057.40) dominated RTH
(-$7,450.72) in the same window — a session-mix observation, not yet enough data (60 trades) to
treat as a structural finding on its own.

## 2. 2026 decomposition (2022-2025 pooled vs 2026 extended thru Jul-31)

| | 2022-2025 pooled | 2026 extended |
|---|---:|---:|
| win rate | 41.7% | 42.3% |
| avg win | $2,477.49 | $3,913.15 |
| avg loss | -$1,475.12 | -$2,471.58 |
| reversal rate | 4.2% | 6.2% |
| giant-winner (≥95th pct) rate | 4.30% of blocks | 9.93% of blocks |
| long-side mean pnl | $263.24 | $614.42 |
| short-side mean pnl | $97.35 | -$100.87 |

**2026 has a HIGHER win rate and a LARGER average win than 2022-2025 — the picture is not
uniformly worse.** Average loss is larger (-$2,472 vs -$1,475) and reversal rate is somewhat
higher (6.2% vs 4.2%), both consistent with the elevated-volatility regime this year, not with a
broad quality collapse. Long-side mean pnl is actually the best of any recent comparison; the
negative in the pooled table is entirely a short-side effect (see sec18 below — resolved as
temporary).

**Giant-winner arrival rate is the HIGHEST of any year on record** (44.70 per 250 sessions,
annualized, vs 2022=26.16, 2023=4.84, 2024=14.48, 2025=29.07) and **1 day has elapsed since the
last giant winner as of 2026-07-31** — directly refuting a naive "the right tail stopped arriving"
story (Hypothesis A). See sec4 below.

## 3. Hypothesis A (right-tail arrival) vs Hypothesis B (conditional edge decay)

**Hypothesis A (fewer/smaller giant winners) is REFUTED for 2026 as a whole**: giant-winner
arrival rate is the highest on record (above), not the lowest.

**Hypothesis B (same signal state, worse outcome) — mixed, no clear decay.** Conditional mean pnl
by M-strength tercile by year:

| M-strength | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---:|---:|---:|---:|---:|
| weak | $149.66 | $50.93 | $100.40 | -$126.75 | **$289.65** |
| mid | $176.60 | $122.66 | $113.27 | -$174.28 | -$50.79 (n=47, sparse) |
| strong | $547.68 | $50.28 | $285.32 | $872.71 | $280.76 |

2026's weak-tercile is the BEST of any year; strong-tercile ($280.76) sits in the middle of the
2022-2025 range ($50-$873) — no monotonic degradation. **No evidence of a stable structural
relationship-shift (payoff-given-state decay).**

## 4. Distribution shift vs relationship shift (sec9)

`P(M-strength tercile | year)` is remarkably stable: weak 49-54%, mid 17%, strong 29-34% in
EVERY year including 2026. **The market is not presenting a different mix of entry-quality
opportunities to Product B in 2026** — whatever drove the Jan-May 2026 weakness is not an
opportunity-frequency effect either. Combined with sec3's finding, this narrows the Jan-May 2026
weakness to something more specific than either a broad right-tail drought or a broad conditional-
edge decay — the short-side deep dive (sec6 below) localizes it further.

## 5. Historical regime analogs

A 5-feature rolling-60-session state vector (mean sigma460, mean |M|, B-MOM activity fraction,
reversal rate, mean entry |M|) finds the CURRENT window's 10 nearest historical analogs are
**overwhelmingly April 2025** (7 of 10 dates, 2025-04-17 through 2025-04-24 — the well-documented
tariff-crash volatility period already flagged elsewhere in this campaign) plus 3 near-duplicate
June 2026 dates (trivially close to the current window itself, not independent evidence). Forward
60-session net P&L following these analog windows averaged **-$19,200.59** — on its face
concerning, but disclosed with two real caveats rather than reported as decisive: (1) 7 of 10
analogs are near-duplicate dates within one 8-day span (effectively 1-2 independent historical
events, not 10), so this is a much smaller-sample statistic than it looks; (2) the 3 June-2026
analogs' "forward 60 sessions" are truncated to whatever data exists through 2026-07-31 (as little
as ~35 sessions), biasing their contribution. **This is a real, disclosed, moderate-confidence
signal that the current regime resembles a historically volatile, subsequently-choppy period — not
a confident forecast.** It is consistent with, not independent confirmation of, the already-known
fact that mid-2025 was a weak stretch for this system.

## 6. Short-side 2026 — the central localized finding

| period | n | mean pnl | sum pnl | win rate |
|---|---:|---:|---:|---:|
| 2026 Jan-May (stub, already studied in R2V1/SA0) | 104 | -$557.28 | -$57,957.62 | 33% |
| **2026 Jun-Jul (new, this run)** | 43 | **+$1,003.02** | **+$43,129.72** | **44%** |

Exact match to SA0's already-reported 2026-stub short figure (-$57,957.62), confirming
consistency across independent constructions. **The short-side weakness is temporally localized to
Jan-May 2026 and has substantially reversed in the newly-available June-July data** — 43 short
trades averaging +$1,003 each, comparable to or better than most historical years' short-side
averages ($97 pooled 2022-2025). This is the single most decision-relevant new fact in this
addendum: **the owner's April manual-review concern about shorts appears to describe a real but
temporary episode, not an ongoing structural deterioration** — though 43 trades over ~2 months is
still a modest sample and this should be treated as encouraging, not conclusive.

## 7. Persistence / lumpiness

64.7% / 77.4% / 88.8% of rolling 20/60/120-session windows (full extended history) are positive —
the system is profitable a clear majority of the time at every horizon, more so at longer
horizons (expected lumpiness for a right-tail-dependent system, not a red flag). Giant-winner
waiting time: mean 16.2 calendar days, median 7.0, max 162 (historical). Top-10%-of-blocks share
of total net_pnl is **375.3%** — confirming (consistent with SA0's day-level finding of ~52-55%
top-10-day share) that the bottom 90% of trades are net NEGATIVE in aggregate; this system's
entire structure is and always has been about capturing a concentrated right tail, not smooth
edge — current lumpiness is not new or unusual.

## 8. Edge-health indicators and flags

Calibration (fixed in advance, not tuned to flatter 2026): percentile of the relevant historical
distribution — **>50th HEALTHY, 25-50th NORMAL_WEAK_REGIME, 10-25th WATCH, 5-10th POSSIBLE_DECAY,
<5th STRUCTURAL_BREAK_EVIDENCE**. Non-percentile indicators use their own stated logic.

| indicator | current value | basis | flag |
|---|---:|---|---|
| Rolling-60 Sharpe | 1.308 | 50.4th percentile | **HEALTHY** |
| Rolling-120 Sharpe | 0.481 | 23.1st percentile | **WATCH** (still absorbing Jan-May 2026) |
| Current drawdown | $5,625 | 34.0th percentile | **HEALTHY** |
| Giant-winner arrival rate (2026 ann.) | 44.70/250 sessions | highest of 5 years | **HEALTHY** |
| Conditional edge, strong-M tercile | $280.76 | mid-range of 2022-2025 ($50-$873) | **HEALTHY** |
| Short-side rolling (most recent 2mo) | +$1,003/trade | reversed from -$557/trade stub | **RECOVERING / HEALTHY** |
| State-mix stability (distribution shift) | stable 2022-2026 | no shift detected | **HEALTHY** |
| Rolling-60 window positivity | 77.4% | historical, all-time | **HEALTHY** |

**Overall assessment: HEALTHY, with one WATCH flag (rolling-120 Sharpe, mechanically explained by
window composition, not by any new evidence of decay) and no POSSIBLE_DECAY or
STRUCTURAL_BREAK_EVIDENCE flags anywhere.** These are research diagnostics, not live-trading
signals — no live-trading authorization exists or is implied by this document (per standing
campaign rule).

## What would change this assessment

Per the addendum's own standing principle (sec14, same standard R2V1 already established): any
future finding of decay must generalize beyond a single recent window, not be a 2026-only or
June-July-only artifact. Specifically, this assessment would need revision if: (a) the short-side
June-July recovery fails to hold up over the next 1-2 months of genuinely new data; (b) the
rolling-120 Sharpe fails to climb back toward the historical median as the Jan-May 2026 stretch
rolls out of the window; (c) a future analog-regime forward-return check (sec5) with a larger,
less-autocorrelated sample of historical analogs shows a robust negative relationship, not the
disclosed-but-caveated one found here.

## Disposition

This is an observational monitoring layer, not a new research family with a promotion gate — no
candidate is constructed or proposed here. Integrated into SA0's evidence base per the owner's
addendum; does not alter SA0's CLOSED disposition or any other family's verdict. Continuing the
MEGA DIRECTIVE's priority queue (R4 next) per the addendum's explicit "do not stop" instruction.
