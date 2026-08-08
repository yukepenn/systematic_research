# W5 A1 — Robust sizing FRONTIER for R5-E10 v2 (Program A, ledger-only)

Date: 2026-08-07. Frozen spec: `research/scalping_lab/specs/W5_programs_wave.md` §A1.
Code: `research/scalping_lab/src/python/w5_a1_sizing.py`. Seed 20260808.
Every number below appears in `w5a1_stdout.txt` / `w5a1_frontier_continuous.csv` /
`w5a1_frontier_mnq_granular.csv` / `w5a1_kelly_capital.csv` / `w5a1_safe_c_sets.csv`.

## Headline (read this first)

- **Sizing creates NO alpha.** Everything in this file rescales one fixed daily edge
  and its risk. Larger c buys arithmetic growth with disproportionately fatter
  drawdown tails; **no single c is "the answer"** — the deliverable is the frontier,
  and the owner picks a point on it with eyes open.
- **The c range keeping P(maxDD > 40%) < 5% across ALL scenarios is c = 0.15 only**
  (of the frozen grid {0.15, 0.25, 0.35, 0.5, 0.75, 1.0}). This holds in the
  continuous idealization AND in every MNQ-granular variant (W0 = 25k/50k/100k),
  on both the v2 and v1 ledgers. c = 0.25 passes on the empirical scenario alone
  (P(DD>40) = 0.4%) but fails the stressed scenarios (worst 7.25%).
- **Full-Kelly capital (empirical, v2): K = sigma^2/mu = $53,984** — i.e. holding a
  constant 1 NQ is full Kelly at ≈ $54k of capital. That is **0.64x the ~$85k
  external estimate**: same order of magnitude (sanity passes), our K is smaller
  because this dev-window ledger's Sharpe (0.680 ann) is better per unit variance
  than the external estimate assumed. Note mu = $99.05/day has SE $68.52/day
  (mu/se = 1.45): K itself is a noisy estimate, which is exactly why the haircut
  scenarios are load-bearing and why "full Kelly" should never be traded.

## Data and method (what was actually done)

- **Ledger**: `runs/E10MASTER_V2/out/daily_v1_v2.csv` — daily P&L per 1-NQ-equivalent
  (the E10 master trades ±10 MNQ = 1 NQ). **Primary = `net_v2`** (Flatten1644,
  the live-operations default per E10MASTER_V2 CONFIRMED_ADOPT — sizing is an
  operations question, so the operations ledger is the right base). `net_v1`
  (frozen research champion) was run as a full sensitivity grid; conclusions
  identical (see safe-c table below).
- **Contamination rule enforced**: file has 1,183 sessions; truncated at 2026-05-31
  → **1,139 sessions used, 2022-01-03 .. 2026-05-29**. No sealed-holdout
  (2026-06-01+) row enters any statistic.
- **Bootstrap**: stationary block bootstrap (Politis–Romano), mean block 10 days
  (geometric block-length, restart p = 0.1, circular), **2,000 paths**, path length
  = 1,139 days (≈ 4.5 years), seed 20260808; identical index draws reused across
  c and W0 within a scenario (common random numbers).
- **Kelly machinery**: mu = $99.05/day, sigma = $2,312.34/day (v2, ddof=1);
  K = sigma^2/mu = $53,984. **K is estimated once from the empirical ledger and held
  fixed across scenarios** — the operator sizes on the edge they *believe*; the
  scenarios vary the edge they *get*. (v1: mu = $106.14, sigma = $2,339.10,
  K = $51,549.)
- **Continuous-c idealization** (scale-free): W_{t+1} = W_t · (1 + c·PnL_t/K).
- **MNQ-granular**: contracts_t = max(round(10·c·W_t/K), 0) MNQ (1 NQ = 10 MNQ; the
  spec's `c·W·mu/sigma² / (0.1·NQ_notional)` form with return-per-notional Kelly
  reduces algebraically to exactly this — the notional proxy cancels);
  W_{t+1} = W_t + (contracts_t/10)·PnL_t; W0 ∈ {25k, 50k, 100k}; W ≤ 0 = ruin.
- **Scenarios** (each over the full c grid): empirical; mu×0.75 and mu×0.5
  (additive shift, variance unchanged); top-5 profit days removed
  (v2: 2025-04-08 +$15,750, 2025-11-20 +$15,429, 2026-03-09 +$11,402,
  2026-02-06 +$10,748, 2025-10-10 +$10,420); and BOTH combined variants
  (top-5 removed, then ×0.75 / ×0.5 haircut of the post-removal mean).
  Worst single day in the ledger: −$10,046.

## FRONTIER TABLE — v2 primary, continuous-c idealization

geoAnn = median annualized geometric growth; medTW = median terminal wealth multiple
over the 1,139-day horizon; TUW = median fraction of days below the running peak;
maxUW_d = median longest underwater spell (days).

| scenario | c | geoAnn | medTW | P(DD>20) | P(DD>30) | P(DD>40) | TUW | maxUW_d |
|---|---|---|---|---|---|---|---|---|
| empirical | 0.15 | 6.6% | 1.33 | 4.0% | 0.1% | 0.0% | 95.4% | 339 |
| empirical | 0.25 | 10.6% | 1.58 | 37.6% | 5.5% | 0.4% | 95.5% | 350 |
| empirical | 0.35 | 14.2% | 1.83 | 76.7% | 25.9% | 5.6% | 95.7% | 359 |
| empirical | 0.50 | 18.9% | 2.19 | 98.4% | 67.6% | 28.5% | 96.0% | 375 |
| empirical | 0.75 | 24.5% | 2.70 | 100.0% | 97.7% | 77.1% | 96.4% | 416 |
| empirical | 1.00 | 27.2% | 2.97 | 100.0% | 100.0% | 96.9% | 96.8% | 456 |
| haircut_mu075 | 0.15 | 4.7% | 1.23 | 8.0% | 0.5% | 0.0% | 96.4% | 408 |
| haircut_mu075 | 0.25 | 7.3% | 1.38 | 51.8% | 10.9% | 1.6% | 96.6% | 421 |
| haircut_mu075 | 0.35 | 9.5% | 1.51 | 86.0% | 38.6% | 11.0% | 96.8% | 437 |
| haircut_mu075 | 0.50 | 12.1% | 1.68 | 99.7% | 79.2% | 42.4% | 97.0% | 459 |
| haircut_mu075 | 0.75 | 13.8% | 1.80 | 100.0% | 99.5% | 86.2% | 97.4% | 508 |
| haircut_mu075 | 1.00 | 12.6% | 1.71 | 100.0% | 100.0% | 99.0% | 97.6% | 558 |
| haircut_mu050 | 0.15 | 2.8% | 1.13 | 15.2% | 0.9% | 0.1% | 97.3% | 498 |
| haircut_mu050 | 0.25 | 4.2% | 1.20 | 62.8% | 20.1% | 3.7% | 97.5% | 523 |
| haircut_mu050 | 0.35 | 5.0% | 1.25 | 93.0% | 51.4% | 20.6% | 97.6% | 542 |
| haircut_mu050 | 0.50 | 5.5% | 1.28 | 99.8% | 88.6% | 55.0% | 97.8% | 578 |
| haircut_mu050 | 0.75 | 3.9% | 1.19 | 100.0% | 99.8% | 93.5% | 98.2% | 632 |
| haircut_mu050 | 1.00 | −0.5% | 0.98 | 100.0% | 100.0% | 99.5% | 98.4% | 702 |
| top5_removed | 0.15 | 2.6% | 1.12 | 13.5% | 1.0% | 0.1% | 97.1% | 496 |
| top5_removed | 0.25 | 3.8% | 1.19 | 59.6% | 17.5% | 3.4% | 97.3% | 514 |
| top5_removed | 0.35 | 4.7% | 1.23 | 88.9% | 46.6% | 17.9% | 97.4% | 536 |
| top5_removed | 0.50 | 5.2% | 1.26 | 99.6% | 84.2% | 50.3% | 97.6% | 567 |
| top5_removed | 0.75 | 4.2% | 1.21 | 100.0% | 99.5% | 89.0% | 98.0% | 627 |
| top5_removed | 1.00 | 0.8% | 1.04 | 100.0% | 100.0% | 99.2% | 98.2% | 696 |
| combined_top5_mu075 | 0.15 | 1.9% | 1.09 | 17.2% | 1.7% | 0.1% | 97.5% | 552 |
| combined_top5_mu075 | 0.25 | 2.6% | 1.12 | 65.1% | 21.5% | 6.0% | 97.6% | 578 |
| combined_top5_mu075 | 0.35 | 3.0% | 1.14 | 92.0% | 54.0% | 21.8% | 97.8% | 596 |
| combined_top5_mu075 | 0.50 | 2.8% | 1.13 | 99.6% | 86.8% | 57.8% | 98.0% | 630 |
| combined_top5_mu075 | 0.75 | 0.4% | 1.02 | 100.0% | 99.3% | 92.0% | 98.2% | 684 |
| combined_top5_mu075 | 1.00 | −4.1% | 0.83 | 100.0% | 100.0% | 99.2% | 98.5% | 753 |
| combined_top5_mu050 | 0.15 | 1.2% | 1.05 | 23.1% | 2.5% | 0.0% | 97.8% | 610 |
| combined_top5_mu050 | 0.25 | 1.5% | 1.07 | 71.4% | 28.0% | 7.2% | 98.0% | 629 |
| combined_top5_mu050 | 0.35 | 1.4% | 1.06 | 94.5% | 60.6% | 28.5% | 98.1% | 652 |
| combined_top5_mu050 | 0.50 | 0.4% | 1.02 | 99.8% | 91.0% | 64.5% | 98.2% | 685 |
| combined_top5_mu050 | 0.75 | −3.1% | 0.87 | 100.0% | 99.7% | 94.6% | 98.4% | 756 |
| combined_top5_mu050 | 1.00 | −8.5% | 0.67 | 100.0% | 100.0% | 99.6% | 98.6% | 819 |

**Internal consistency check (Kelly theory)**: at c = 1.0 under mu×0.5 the operator
is unknowingly betting ≈ 2× true Kelly, where theory predicts ~zero geometric
growth — observed −0.5%. The frontier behaves as the mathematics says it must.

## MNQ-granular results (integer contracts, W0 grid)

Full 6-scenario × 6-c × 3-W0 grid for both ledgers is in
`w5a1_frontier_mnq_granular.csv`. Representative v2 rows (empirical and the
harshest scenario), p_ruin = 0 in all rows shown:

| scenario | c | W0 | geoAnn | medTW | P(DD>20) | P(DD>30) | P(DD>40) | P(ever 0 contracts) |
|---|---|---|---|---|---|---|---|---|
| empirical | 0.15 | 25k | 8.5% | 1.45 | 12.9% | 1.8% | 0.0% | 1.1% |
| empirical | 0.15 | 50k | 5.4% | 1.27 | 2.0% | 0.1% | 0.0% | 0.0% |
| empirical | 0.15 | 100k | 6.5% | 1.33 | 4.2% | 0.1% | 0.0% | 0.0% |
| empirical | 0.25 | 25k | 8.1% | 1.42 | 24.0% | 2.9% | 0.2% | 0.1% |
| empirical | 0.25 | 50k | 9.7% | 1.52 | 35.1% | 4.6% | 0.4% | 0.0% |
| empirical | 0.25 | 100k | 10.5% | 1.57 | 37.4% | 5.6% | 0.5% | 0.0% |
| combined_top5_mu050 | 0.15 | 25k | 2.2% | 1.10 | 47.9% | 13.1% | 0.4% | 11.8% |
| combined_top5_mu050 | 0.15 | 50k | 0.7% | 1.03 | 9.2% | 0.4% | 0.0% | 0.0% |
| combined_top5_mu050 | 0.15 | 100k | 1.5% | 1.07 | 25.1% | 2.2% | 0.0% | 0.0% |
| combined_top5_mu050 | 0.25 | 25k | 2.1% | 1.10 | 53.6% | 17.6% | 5.4% | 0.3% |
| combined_top5_mu050 | 0.25 | 50k | 0.9% | 1.04 | 66.7% | 23.7% | 6.6% | 0.0% |
| combined_top5_mu050 | 0.25 | 100k | 1.5% | 1.07 | 71.8% | 28.3% | 7.5% | 0.0% |

Granularity note: at W0 = $25k and c = 0.15 the ideal position is 0.69 MNQ, which
rounds UP to 1 MNQ — a small structural over-size (higher growth AND higher
P(DD>20) than continuous), and 1.1–11.8% of paths touch 0 contracts (sizing-out)
at some point. At W0 ≥ $50k rounding effects are second-order.

## Safe-c determination (deliverable)

Worst-scenario P(maxDD > 40%) by c — must be < 5% in EVERY scenario
(full table incl. v1: `w5a1_safe_c_sets.csv`):

| mode | c=0.15 | c=0.25 | c=0.35 | c=0.5 | c=0.75 | c=1.0 | safe set |
|---|---|---|---|---|---|---|---|
| v2 continuous | 0.1% | 7.3% | 28.5% | 64.6% | 94.6% | 99.6% | **{0.15}** |
| v2 MNQ W0=25k | 0.4% | 5.4% | 24.5% | 62.2% | 94.3% | 99.6% | **{0.15}** |
| v2 MNQ W0=50k | 0.0% | 6.6% | 28.1% | 64.3% | 94.6% | 99.5% | **{0.15}** |
| v2 MNQ W0=100k | 0.1% | 7.5% | 28.6% | 64.5% | 94.7% | 99.5% | **{0.15}** |
| v1 continuous | 0.4% | 11.7% | 34.3% | 69.9% | 96.5% | 99.8% | **{0.15}** |
| v1 MNQ (all W0) | ≤1.5% | 6.9–11.5% | 31.7–33.9% | 67.6–69.8% | 96.6–96.8% | ≥99.8% | **{0.15}** |

**Result: c = 0.15 is the only grid point satisfying the frozen criterion.**
In dollar terms at c = 0.15: ideal exposure = 1 NQ per ≈ $360k (= K/0.15), i.e.
≈ 1 MNQ per $36k of wealth; expected geometric growth ~6.6%/yr empirical,
degrading to ~1.2%/yr under the harshest stress — but the account survives.

## Caveats (honest limits)

1. **TUW is high everywhere (95–98%)**: a Sharpe-0.68 strategy compounding at
   fractional Kelly spends almost all days marginally below some prior peak,
   with median longest underwater spells of 1.3–3.3 trading years. This is a
   property of the edge, not of the sizing; expect it psychologically.
2. The bootstrap resamples 10-day blocks of the 2022–2026 dev window: regimes
   longer than ~2 weeks (e.g. a year-long vol regime) are partially broken up,
   and no scenario manufactures losses worse than the window contains beyond
   the mean shifts specified.
3. Commissions scale linearly with contracts by construction (ledger embeds
   10-MNQ Lifetime costs); margin, funding-account rules and fill degradation
   at larger size are NOT modeled. The MNQ intraday-margin floor makes c = 0.15
   at W0 = $25k feasible on margin, but tick-level capacity was not tested.
4. K = $53,984 is a point estimate from a noisy mu (mu/se = 1.45). Treat the
   haircut rows as the realistic planning case, not the empirical rows.

**No alpha is created anywhere in this study; no single c is "the answer".**
