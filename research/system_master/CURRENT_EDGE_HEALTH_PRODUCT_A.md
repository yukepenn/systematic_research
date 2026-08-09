# CURRENT_EDGE_HEALTH_PRODUCT_A — Product-A current-regime health, future-readiness

Written 2026-08-09 as the Product-A mirror of `CURRENT_EDGE_HEALTH.md` (Product B's panel), per
the H0 diagnostic run. Scope: Product A (`SolarWaveSMMaster_v4`, continuous exposure in
[-13,+13] MNQ contracts, K-coefficient mapping + short-halving overlay + C4 partial-size gating),
same object studied structurally in PA0 (`runs/PA0_PRODUCT_A_STRUCTURE/REPORT.md`). This document
extends PA0's canonical-window structural findings into the current-health question PA0's own
spec deferred ("Product A gets its own current-health pass" — this is that pass). Full
evidence/scripts: `runs/H0_PRODUCT_A_HEALTH/`.

## Two distinct windows — do not conflate them

- **Canonical comparison window** (frozen, used for every formal metric/gate in this campaign):
  2022-01-03 → 2026-05-29, 1,139 sessions. Net **$177,924.40** (`BASELINE_MODELS.md`, PA0). This
  document's own correctness gate independently re-reads `runs/U0_UNIFIED_STATE/out/
  u0_state_table.parquet` and reproduces that net exactly (`sum(bar_pnl_A_dollars)` over
  `is_health_only_bar==False` = $177,924.40, matched to the cent) before any analysis below ran.
- **Current-health window** (observational monitoring only, NOT used for tuning or promotion
  gates): extended to **2026-07-31** — the same 45-session health-only extension Product B's panel
  used, reused here for Product A under the same prior determination
  (`SM11_HOLDOUT_READ`/`CURRENT_TRUTH.md` Wave-18: "nothing left to seal" for this window). Data
  ≥2026-08-01 remains sealed per `research/operational/LOCKED_FORWARD.md` and was not read.

## Headline answer

**Product A's current-regime picture is HEALTHY and, on Product A's own numbers, shows the same
qualitative shape Product B's panel already found: a genuinely weak 2026 Jan-May stretch followed
by a real June-July recovery.** This is an independent confirmation on a different P&L stream
(continuous exposure, different decision thresholds, its own K-coefficients and short-halving
overlay), not a re-statement of Product B's finding — Product A's Jan-May weakness and June-July
recovery are visible in Product A's own trade ledger and were not assumed. One indicator among
eight — exposure-band top-end monotonicity in the health-only extension — reads POSSIBLE_DECAY on
a genuinely thin sample (331 bars, 7 of 45 sessions) and is disclosed rather than smoothed over;
it does not, on its own, change the overall verdict.

## 1. Window summary table (dd_battery, same metric function as Product B's panel)

| window | n sessions | net | Sharpe | Sortino | Calmar | maxDD (EOD) | CDaR5 | worst day | worst month | %+ days |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FULL-HISTORY (2022-01-03..2026-07-31) | 1,184 | $212,894.50 | 1.307 | 2.614 | 2.366 | $19,149.00 | $14,533.55 | -$7,408.60 | -$7,495.50 | 44.5% |
| PRE-2026 (2022-2025) | 1,033 | $167,570.20 | 1.260 | 2.565 | 2.378 | $17,192.90 | $13,787.70 | -$6,481.50 | -$5,531.30 | 44.3% |
| 2026-YTD (thru 2026-07-31) | 151 | $45,324.30 | 1.603 | 3.202 | 3.950 | $19,149.00 | $16,624.50 | -$7,408.60 | -$7,495.50 | 45.7% |
| LATEST-20 | 20 | $15,360.80 | 4.335 | 13.651 | 61.666 | $3,138.60 | $3,138.60 | -$2,668.70 | +$15,360.80 | 50.0% |
| LATEST-60 | 60 | $18,285.90 | 1.436 | 2.730 | 4.242 | $18,106.80 | $16,415.27 | -$7,408.60 | -$16,684.20 | 45.0% |
| LATEST-120 | 120 | $22,462.70 | 0.979 | 1.917 | 2.463 | $19,149.00 | $16,795.90 | -$7,408.60 | -$7,495.50 | 45.0% |
| ANALOGS (pooled fwd-60 after 10 nearest regime analogs)† | 464 (pooled) | $4,674.00 (mean) | 0.801 | 1.369 | n/a | n/a | n/a | -$6,082.70 | n/a | 43.5% |

† **ANALOGS row is not a contiguous equity curve** — it is the mean forward-60-session Product-A
net P&L following the 10 historical 60-session windows whose Product-A-flavored regime state
(mean sigma460, mean|M|, B-MOM active fraction, trip FLIP-rate, mean |entry M_A_raw|) is nearest
to the current window. The 10 analogs are dominated by 3 near-duplicate June-2026 dates (trivially
close to the current window itself) and 2025-04-24/-05-12/-05-13/-05-14/-05-15 (5 of 10, the
already-documented tariff-crash volatility period) — effectively 2 independent historical events,
not 10, same caveat class SA0's own sec10 disclosed. Forward-60 mean +$4,674.00 (median $6,041.95)
is positive but well below the current rolling-60 reading (+$18,285.90); range across the 10
analogs was -$14,890.10 to +$13,260.50 — wide, low-confidence, directionally mildly encouraging,
not a forecast.

**Product A's canonical-window Sharpe (1.177, sliced to exactly 2022-01-03..2026-05-29) matches
PA0's certified figure exactly.** Full-history Sharpe (1.307) exceeds pre-2026 Sharpe (1.260) —
**2026-YTD Sharpe (1.603) is the best of any window above pre-2026**, driven almost entirely by
the June-July recovery (see below); the 2026 Jan-May stub alone, isolated from the health-only
extension, has Sharpe **0.584** — genuinely weak versus the pre-2026 baseline, confirming Product
A independently saw the same 2026 Jan-May softness Product B's panel documented, before the
June-July rebound pulled 2026-YTD back above the historical baseline.

## 2. Monthly + quarterly 2026 net P&L

| month | n sessions | net | win rate |
|---|---:|---:|---:|
| 2026-01 | 21 | -$195.30 | 43% |
| 2026-02 | 20 | +$21,153.30 | 50% |
| 2026-03 | 22 | +$3,992.50 | 45% |
| 2026-04 | 22 | -$7,495.50 | 41% |
| 2026-05 | 21 | -$7,100.80 | 33% |
| 2026-06 | 22 | +$20,562.70 | 55% |
| 2026-07 | 23 | +$14,407.40 | 52% |

| quarter | n sessions | net | win rate |
|---|---:|---:|---:|
| 2026-Q1 | 63 | +$24,950.50 | 46% |
| 2026-Q2 | 65 | +$5,966.40 | 43% |
| 2026-Q3 (partial, Jul only) | 23 | +$14,407.40 | 52% |

**Without February's outsized +$21,153.30, Jan+Mar+Apr+May 2026 sums to -$10,798.60** — the
Jan-May stub's positive headline total ($10,354.20) is carried almost entirely by one strong
month, with April and May both meaningfully negative and May the worst win-rate month of the
year (33%). June and July are both solidly positive with win rates above the full-history average
(44.5%) — the recovery is broad (two consecutive good months, not one lucky day inflating the
period), consistent with, and independently corroborating, Product B's own June-July recovery
finding.

## 3. Rolling 20/60/120-session dashboard, with historical-percentile context

| window | net | Sharpe (pctile) | n trips | expectancy/trip (pctile) | trip win rate (pctile) | avg win | avg loss | turnover/session (pctile) | long P&L | short P&L |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| rolling 20 | $15,360.80 (94.3th) | 4.335 (89.7th) | 85 | $182.21 (93.6th) | 29.4% (79.3th) | $1,791.82 | -$488.46 | 38.9 (91.8th) | $2,198.05 | **$13,289.90** |
| rolling 60 | $18,285.90 (81.4th) | 1.436 (53.6th) | 248 | $74.94 (81.9th) | 30.2% (94.0th) | $1,569.50 | -$572.99 | 35.2 (83.8th) | $2,157.90 | **$16,427.15** |
| rolling 120 | $22,462.70 (64.6th) | 0.979 (31.2th) | 530 | $43.61 (60.8th) | 27.4% (87.2th) | $1,376.97 | -$458.56 | 34.5 (80.8th) | **$25,457.05** | -$2,342.05 |

Percentiles are each rolling-window reading's rank against the FULL historical distribution of all
rolling-windows-of-that-length ever observed (e.g. "94.3th" for rolling-20 net means the current
20-session net P&L exceeds 94.3% of all historical 20-session net readings). All three windows
currently sit in the upper half to upper quartile of their own historical distributions on every
metric — a genuinely strong current reading, not merely "not-bad."

**Current drawdown: $1,928.50 (29.1th percentile of all historical daily-drawdown readings —
shallow).** Current time-underwater: 1 session. Current losing-session streak: 1 (the latest
session, 2026-07-31, was a loser after a string of winners).

**Rolling-20/60 short P&L strongly dominates long P&L ($13,289.90 and $16,427.15 vs $2,198.05 and
$2,157.90), while rolling-120 shows the OPPOSITE (long $25,457.05 dominant, short -$2,342.05
negative).** This means the short-side strength is concentrated specifically in the most recent 60
sessions (June-July), with the 61st-120th session lookback (roughly April-May) showing long
dominant and short negative — **the exact same "short-side outperformed long in the latest
60-session window, counter to the historical pattern and to the Jan-May 2026 stub" finding Product
B's panel reported, independently reproduced on Product A's own P&L.**

## 4. Exposure-band P&L contribution + scale-in reconciliation

### 4a. Exposure-band contribution

| band | canonical n bars | canonical $/bar/contract | health-ext n bars | health-ext $/bar/contract | full n bars | full $/bar/contract |
|---|---:|---:|---:|---:|---:|---:|
| 0 (flat) | 119,512 | — | 3,491 | — | 123,003 | — |
| 1-3 | 265,855 | **-$0.042** | 9,187 | **+$0.842** | 275,042 | -$0.010 |
| 4-6 | 96,962 | +$0.036 | 4,721 | +$0.818 | 101,683 | +$0.073 |
| 7-9 | 34,118 | +$0.460 | 2,788 | +$0.341 | 36,906 | +$0.451 |
| 10-13 | 3,267 | **+$1.878** | 331 | **-$0.173** | 3,598 | +$1.691 |

**Canonical-window figures reconcile exactly against PA0's own published `sec31_pnl_by_exposure_
band.csv`** (n_bars and sum_pnl match to the cent on all 5 bands — max absolute difference
$0.00). PA0's finding of strict monotonic per-contract quality (1-3 worst, 10-13 best) holds
exactly on the canonical window.

**The health-only extension does NOT continue that ordering at the top end.** 1-3 and 4-6 are both
strongly positive and roughly tied (+$0.842 / +$0.818, versus canonical's negative/near-zero), but
7-9 is lower (+$0.341) and **10-13 is net NEGATIVE (-$0.173)** — the band that was by far the best
performer in the canonical window (+$1.878/contract) is the worst performer in the extension.
Disclosed with its own sample-size caveat: only 331 bars across 7 of the 45 extension sessions
ever reached the 10-13 band, total dollar impact is small (-$605.00, against a $34,970.10
extension net), and the pattern is not a single blowup — two sessions (2026-06-08, -$1,631.70;
2026-07-02, -$1,880.15) account for the negative tilt while three sessions (07-16, 07-24, 07-31)
were positive in that band. **This reads as a genuine pattern-break worth monitoring, not yet
evidence the sizing scheme itself has degraded** — see indicator 7 below.

### 4b. Scale-in vs fresh-entry (forward-20-bar $/contract)

| window | n fresh | fresh $/contract (fwd20) | n scale-in | scale-in $/contract (fwd20) | multiple |
|---|---:|---:|---:|---:|---:|
| CANONICAL | 3,483 | $2.025 | 8,137 | $14.432 | **7.127x** |
| HEALTH-ONLY EXT | 121 | $90.641 | 344 | $74.944 | 0.827x |
| FULL HISTORY | 3,604 | $5.000 | 8,481 | $16.886 | 3.377x |

**Canonical figures reconcile exactly against PA0's published `sec31_33_summary.json`** (fresh
$2.03 vs PA0's $2.03; scale-in $14.43 vs PA0's $14.43). PA0's "scale-in is ~7x more valuable than
fresh entries" finding is confirmed to the third decimal (7.127x here).

**In the health-only extension, both fresh entries and scale-ins are far MORE valuable in absolute
terms than in the canonical window ($90.64 and $74.94/contract vs $2.03 and $14.43) — consistent
with a stronger-trending, higher-realized-move regime — but the RATIO inverts: fresh entries are
now slightly MORE valuable than scale-ins (0.827x), not less.** Scale-out also flips from
near-neutral in canonical (-$0.55/contract) to strongly positive in the extension (+$98.51/
contract) — de-risking was rewarded in this window too, another signature of a volatile,
mean-reverting-within-trend regime. Sample is thin (121 fresh / 344 scale-in transitions vs
16,152 canonical) — treated as NORMAL_WEAK_REGIME (indicator 8 below), not structural evidence.

## 5. Tail-arrival

**Top-10-day contribution to full-history total net: 54.2%** ($115,462.10 of $212,894.50) —
closely matching SA0's own reported ~52-55% top-10-day share for Product B, an independent
confirmation that Product A is built on the same right-tail-dependent structure, not a smoother
edge. Top-20-day contribution: 90.8%. Bottom-10-day drag: -26.8% of total net.

**Top-10%-of-trips (n=498 of 4,989) explain 515.0% of total trip net_pnl** (i.e. the bottom 90% of
trips are net NEGATIVE in aggregate, by a wide margin) — same qualitative structure SA0 found for
Product B (top-10-day share ~52-55%, bottom-90%-of-trades net negative). Confirmed independently
on Product A's own continuous-exposure trade ledger.

**Giant-winner (trip net_pnl ≥ 95th percentile, cutoff $1,564.46) arrival rate by year, annualized
per 250 sessions:**

| year | rate |
|---|---:|
| 2022 | 66.86 |
| 2023 | 32.95 |
| 2024 | 43.44 |
| 2025 | 55.23 |
| **2026** | **74.50 (highest of 5 years)** |

Days since the last giant-winner trip (as of 2026-07-31): **1**. Waiting time between giant
winners: mean 6.7 calendar days, median 5.0, max 59.0. **Directly consistent with Product B's own
finding that 2026's right tail is arriving MORE often than any prior year, not drying up** —
independently confirmed on Product A's own trade ledger.

**Is the current regime tail-rich or tail-poor vs history?** Rolling-60-session top-10%-of-trips
share of window net: current 519.4% → **63.6th percentile** of all historical rolling-60 readings.
Rolling-120: current 740.2% → **74.8th percentile**. **The current regime is MORE tail-dependent
than the historical norm at both horizons**, not less — consistent with an unusually strong,
concentrated recent right tail (the June-July recovery itself is disproportionately carried by a
handful of large trips), not a broadening of edge into steadier, less lumpy P&L.

## 6. Short-side deep dive (Product A's own short-halving overlay)

| year | n trips | mean pnl | sum pnl | win rate |
|---|---:|---:|---:|---:|
| 2022 | 530 | $56.18 | $29,772.85 | 26% |
| 2023 | 527 | -$24.74 | -$13,038.70 | 23% |
| 2024 | 525 | $9.62 | $5,050.90 | 23% |
| 2025 | 581 | $70.49 | $40,957.55 | 22% |
| 2026 | 349 | $22.04 | $7,692.90 | 23% |

2026 short-side, split (matching SA0's Jan-May-stub vs Jun-Jul-extension split, Product-A version):

| period | n | mean pnl | sum pnl | win rate |
|---|---:|---:|---:|---:|
| 2026 Jan-May (stub, canonical) | 253 | -$73.06 | -$18,484.00 | 20% |
| **2026 Jun-Jul (health-only ext)** | 96 | **+$272.68** | **+$26,176.90** | **31%** |

The Jan-May-stub short figure (-$18,484.00) matches PA0's own published year-by-year short figure
for 2026-thru-May exactly (PA0 sec33: "-$18,484"). **Product A's short side independently shows the
same weak-Jan-May / recovered-Jun-Jul shape Product B's panel found** — though the recovery's
per-trade magnitude is more modest for Product A ($272.68/trip) than for Product B ($1,003.02/
trip on Product B's own June-July shorts), and Product A's June-July short mean ($272.68) is well
above its own full-history short mean ($28.04), a genuine above-normal reading, not merely
"less negative." Long-side 2026, for context: Jan-May stub $29,443.30 (237 trips), Jun-Jul $9,032.15
(84 trips) — long-side actually contributed LESS in June-July than in the Jan-May stub, meaning
the recent recovery's composition is short-led, not simply "everything got better."

## 7. State-mix stability

P(entry conviction tercile | year) — fixed bins (weak=|M_A_raw|=1, mid=2-3, strong≥4; a standard
qcut tercile split is degenerate here because 82% of all trip entries occur at exactly
|M_A_raw|=1, the natural minimal-conviction Product-A entry, since Product A has no analog to
Product B's ENTRY_LEVEL=3 hysteresis — any nonzero rounded score triggers entry):

| year | weak (\|M\|=1) | mid (\|M\|=2-3) | strong (\|M\|≥4) |
|---|---:|---:|---:|
| 2022 | 83.6% | 8.3% | 8.2% |
| 2023 | 82.6% | 8.9% | 8.5% |
| 2024 | 82.7% | 9.3% | 7.9% |
| 2025 | 83.2% | 7.7% | 9.1% |
| 2026 | 80.9% | 9.4% | 9.7% |

**Stable across all 5 years (weak-tercile share range 80.9%-83.6%, a 2.7-point spread) — the
market is not presenting Product A a different mix of entry-quality opportunities in 2026 than in
any prior year**, the same distribution-shift-absent finding SA0 reported for Product B.

Conditional mean trip pnl by tercile by year (does 2026 pay worse for the same entry state?):

| tercile | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---:|---:|---:|---:|---:|
| weak (\|M\|=1) | $50.32 | $23.40 | $32.44 | -$6.84 | **$59.24** |
| mid (\|M\|=2-3, n=63-99/yr, sparse) | $97.50 | -$45.00 | $52.49 | $124.80 | -$65.56 |
| strong (\|M\|≥4) | -$46.40 | $19.11 | -$1.40 | $671.19 | $279.86 |

**2026's weak-tercile reading is the BEST of any year** (matching Product B's own finding that its
2026 weak-tercile was the best on record). Strong-tercile ($279.86) sits comfortably inside the
2022-2025 range (-$46.40 to $671.19) — no monotonic degradation. Mid-tercile is the smallest-n
bucket every year (63-99 trips) and 2026's reading is the worst on record there, but on this
sample size that reads as noise, not signal — flagged, not treated as evidence.

## 8. Edge-health indicators and flags

Thresholds fixed and printed BEFORE any reading was computed (`runs/H0_PRODUCT_A_HEALTH/src/
07_indicators_flags.py` prints its threshold block first, then computes). Percentile-type
indicators reuse `CURRENT_EDGE_HEALTH.md`'s own fixed scale verbatim (**>50th HEALTHY, 25-50th
NORMAL_WEAK_REGIME, 10-25th WATCH, 5-10th POSSIBLE_DECAY, <5th STRUCTURAL_BREAK_EVIDENCE**), with
the drawdown indicator's "bad-is-high" direction made explicit (inverted scale — matching how
Product B's own panel implicitly flagged a 34.0th-percentile drawdown HEALTHY). Non-percentile
indicators (5-8) use their own stated-in-advance logic (full text in the script).

| indicator | current value | basis | flag |
|---|---:|---|---|
| Rolling-60-session Sharpe | 1.436 | 53.6th percentile | **HEALTHY** |
| Rolling-120-session Sharpe | 0.979 | 31.2nd percentile | **NORMAL_WEAK_REGIME** |
| Current drawdown | $1,928.50 | 29.1st percentile (inverted scale) | **HEALTHY** |
| Giant-winner arrival rate (2026 ann.) | 74.50/250 sess | rank 1 of 5 years (highest) | **HEALTHY** |
| Conditional edge, strong-conviction entries (\|M_A_raw\|≥4) | $279.86/trip | within 2022-2025 range [-$46.40, $671.19] | **HEALTHY** |
| Short-side latest-2-month (Jun-Jul) mean trip pnl | $272.68/trip | above full-history mean $28.04/trip | **HEALTHY** |
| Exposure-band top-end monotonicity (health-only ext.) | 0.842 / 0.818 / 0.341 / **-0.173** | top band flips negative, lower bands stay positive | **POSSIBLE_DECAY** |
| Scale-in-vs-fresh premium (health-only ext.) | 0.827x | canonical 7.127x; both legs still positive in $ | **NORMAL_WEAK_REGIME** |

**Flag counts: 5 HEALTHY, 2 NORMAL_WEAK_REGIME, 1 POSSIBLE_DECAY, 0 WATCH, 0 STRUCTURAL_BREAK_
EVIDENCE.**

**Overall assessment: HEALTHY.** Six of eight indicators are unambiguously healthy, independently
confirming the same weak-Jan-May/strong-Jun-Jul shape, the same still-elevated-tail-arrival-rate
story, and the same short-side-recovery story Product B's panel already established — on Product
A's own, differently-constructed P&L stream, which is meaningfully stronger evidence than either
panel alone. The rolling-120 Sharpe's NORMAL_WEAK_REGIME reading is mechanically explained by
window composition (still absorbing April-May 2026), the same explanation Product B's panel gave
for its own analogous WATCH-flagged indicator — Product A's version is one bucket milder
(NORMAL_WEAK_REGIME vs Product B's WATCH), consistent with Product A's Jan-May weakness being
somewhat less severe in Sharpe terms than Product B's. **The one POSSIBLE_DECAY flag — exposure-
band top-end monotonicity breaking down in the extension — is genuine and should not be
minimized, but it rests on 331 bars across 7 of 45 sessions and a $605 dollar swing against a
$34,970 extension-window net; it is disclosed as a real pattern-check for the next round of
health monitoring, not treated as evidence the sizing scheme itself has degraded.** No
STRUCTURAL_BREAK_EVIDENCE flag anywhere. These are research diagnostics, not live-trading
signals — no live-trading authorization exists or is implied by this document.

## What would change this assessment

Consistent with this campaign's standing principle (any decay finding must generalize beyond one
recent window, not be a June-July-only artifact): this assessment would need revision if (a) the
10-13 exposure band's negative reading in the extension persists or deepens as more health-only
data accrues, rather than reverting toward the canonical +$1.878/contract; (b) the scale-in/fresh
ratio stays below 1x (or turns negative) over the next 1-2 months of genuinely new data, rather
than being a small-sample artifact of an unusually trending regime; (c) the short-side June-July
recovery (both A's and B's) fails to hold up; (d) the rolling-120 Sharpe fails to climb back toward
the historical median as the Jan-May 2026 stretch rolls out of the window.

## Disposition

This is an observational monitoring layer, not a new research family with a promotion gate — no
candidate is constructed or proposed here, and PA0/PA1's disposition (diagnostic complete / CLOSED,
no candidate) is unchanged. See `research/system_master/PRODUCT_A_VS_B_CURRENT_HEALTH.md` for the
Product-A-vs-B comparison this same H0 run also produced.
