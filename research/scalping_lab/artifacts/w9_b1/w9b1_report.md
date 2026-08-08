# W9-1 — B1 overnight premium: the 2006+ resolution (amended decay-aware verdict)

Spec: `research/scalping_lab/specs/W9_nq_minute_resolutions.md`, frozen at `d7dfdad`
(including the 2026-08-08 decay amendment) before this readout.
Code: `research/scalping_lab/src/python/w9_b1_resolution.py`.
Every number below appears in this directory (`w9b1_stdout.txt` + CSVs).
Substrate: `substrate/minute/NQ/nq1m_2005_202605.parquet` — 6,466,783 1-min bars,
actual range 2006-01-05 → 2026-05-29 (NT8 cache start), END-stamped ET (verified:
evening opens stamp 18:01, session closes 17:00). Nothing beyond 2026-05-31 read.

## Verdict

**PROMISING — all four amended clauses pass under the frozen procedure**
(seed 20260808, 1,000 night-clustered bootstrap reps), **with a verdict-level
fragility caveat on clause (a)** (below).

| Clause | Requirement | Result | Status |
|---|---|---|---|
| (a) power | full-sample net(2.0t) ≥ +4 t/night AND CI_lo > 0 | **+8.369 t/night**, CI [+0.121, +16.641] | PASS (marginal) |
| (b) trend | no significant negative time trend (HC1 t ≤ −1.96) | slope **+0.00657 t/night-step** (+1.66 t/yr), HC1 t = **+1.686** | PASS |
| (c) recency | 2022→2026-05 block point estimate > 0 | **+17.380 t/night** | PASS |
| (d) overlap | Pearson ρ vs Solar net_v1 (2022+ overlap) < 0.3 | **ρ = +0.0150** (n = 1,093) | PASS |

The amendment's kill-switch ("a pass driven by pre-2015 with a dying trend = FAIL")
does **not** bind: the premium is the opposite of dying — pre-2015 mean **+1.653 t**
vs 2015+ mean **+13.599 t**, and the time trend is *positive*. The effect is
recent-loaded, not a pre-2015 artifact.

### Verdict-level caveat: clause (a) is Monte-Carlo marginal

The plain t-stat of the full-sample mean is **+1.912** (mean +8.369 t, sd 310.962 t,
n = 5,048) — i.e., the true 95% CI edge sits almost exactly at zero, and the frozen
1,000-rep draw landed CI_lo at +0.121 t. The non-verdict fragility diagnostic
(`w9b1_ci_fragility.csv`): with 10,000 reps at the frozen seed, CI_lo = **−0.338 t**;
across seeds 1–10 at 1,000 reps, CI_lo > 0 in only **2/10** draws. Under the
W5-native 10,000-rep procedure clause (a) would FAIL. The frozen rule (task
directive: 1,000 reps, seed 20260808) governs, so the verdict stands as PROMISING,
but the Program-B candidate freeze should carry this caveat explicitly.

## Reconciliation vs W5-B1 (required gate — passed)

| | net(2.0t) mean | n | hit rate | median |
|---|---|---|---|---|
| W5-B1 frozen (3-min substrate) | +17.211 t/night | 1,092 | 0.5247 | +27.0 t |
| W9 2022+ subset (1-min substrate) | **+17.380 t/night** | 1,093 | 0.5252 | +27.0 t |

Difference **+0.169 t**, inside the declared ±1.5 t tolerance → **RECONCILED**
(`w9b1_reconcile_w5.csv`).

## Sample and construction

- 5,262 sessions → 5,066 accepted entries → **5,048 nights** (2006-01-06 → 2026-05-29);
  1,023 weekend/holiday spans (>24 h hold).
- Construction identical to W5-B1: long 1 NQ at the last bar end-stamped ≤ 16:45 ET
  (close); exit next session's first bar ≥ 09:30 ET (close, ≤ 17:00 guard).
  Friction 2.0 t primary / 2.872 t stress.
- **Minute-substrate adaptation (disclosed):** pre-Nov-2012 Fridays closed 16:15 ET;
  entries accepted with staleness ≤ 30 min (4,424 exact-16:45 stamps; 285 in (0,5];
  357 in (5,30], concentrated 2006–2012 ≈ Friday 16:15 closes); 126 sessions dropped
  as true early closes (13:00/13:15 holidays), matching W5-B1's exclusion.
- 8σ roll/outlier detector (full-sample σ = 310.962 t → threshold 2,487.7 t):
  **4 nights flagged** (2024-08-02 −3852 t; 2025-01-24 −3109 t; 2025-05-09 +3151 t;
  2026-04-07 +3139 t — all genuine vol events, none a roll artifact). Excl. outliers:
  full-sample net +8.510 t, CI [+0.302, +16.086] — headline barely moves.

## 4-year blocks and by-era medians (`w9b1_blocks.csv`)

| Block | n | net(2.0t) mean | 95% CI | median | net(2.872t) mean |
|---|---|---|---|---|---|
| 2006-2009 | 975 | −0.754 | [−3.637, +2.163] | +2.0 | −1.626 |
| 2010-2013 | 991 | +2.843 | [−0.395, +6.372] | +6.0 | +1.971 |
| 2014-2017 | 993 | +2.461 | [−3.728, +8.519] | +7.0 | +1.589 |
| 2018-2021 | 996 | +18.799 | [−2.176, +38.304] | +32.0 | +17.927 |
| 2022-2026-05 | 1,093 | +17.380 | [−17.724, +51.126] | +27.0 | +16.508 |

Medians are positive in every block after 2006-2009; the mean premium concentrates
in 2018+. Worst years: 2008 (−6.5 t), 2016 (−5.7 t), 2022 (−48.8 t).

## Other required readouts

- **Down-prior-RTH conditional:** prior RTH ret < 0 → +7.965 t (n 2,286) vs
  complement +8.703 t (n 2,762). No conditioning edge; the frozen conditional adds
  nothing.
- **Top-10-nights-removed sensitivity:** the 10 best nights sum +22,407 t = **53.0%**
  of total net +42,246 t; with them removed the mean drops to **+3.938 t/night**,
  CI [−4.609, +11.830] — below the +4 t bar. The premium is heavily
  crisis/vol-night concentrated (the frozen rule does not kill on this, but it is
  the second major caveat for any Tier-1 plan).
- **Stress friction (2.872 t):** full-sample +7.497 t, CI [−0.997, +15.421] — not
  significant at stress friction.
- **Rolling 2-year mean** (`w9b1_rolling_2y.csv`): min −29.442 t (2023-10-26), max
  +64.456 t (2025-10-29), last +50.522 t (2026-05-29); below zero in 33.5% of
  observations — multi-year droughts are part of the deal.
- **Correlation detail** (`w9b1_correlation.csv`): full overlap ρ = +0.015
  (Spearman +0.072); Solar losing days ρ = +0.162 — a genuine diversifier even on
  Solar's bad days.

## Disposition

Per the frozen spec: PROMISING → freeze as **Program-B candidate** → engine parity +
Tier-1 plan. The freeze should carry three explicit caveats: (1) clause-(a) CI is
Monte-Carlo marginal (t = 1.91; fails at 10k reps), (2) 53% of the edge lives in 10
nights (tail-harvest profile; expect long flat/negative stretches), (3) not
significant at 2.872 t stress friction. Per the amendment's standing principle, the
candidate gets a decay-monitoring protocol despite the currently *positive* trend.
