# LIQREV01 — Stress-gated daily liquidity-provision reversal (FROZEN SPEC)

**Committed BEFORE any outcome is read.** Date 2026-08-19. Source: ENGINE3_SCOUT_20260819
gatekeeper rank-1 (Nagel RFS 2012 "Evaporating Liquidity"; Campbell-Grossman-Wang QJE 1993;
Brunnermeier-Pedersen funding-liquidity persistence mechanism). **This consumes the wave's 2nd
and FINAL alpha hypothesis (§15 cap = 2; HTFDIR01 was the 1st). No further alpha hypothesis may
be opened this wave regardless of outcome.**

Hypothesis: the return to SUPPLYING liquidity against large one-day index moves is positive
after costs ONLY in high-stress states (when intermediary capital withdraws), at a daily horizon.
The six dead repo reversion families were all unconditional, intraday, structure-anchored, and
tested on 2022-26 only; this is an interaction claim with a built-in calm-state falsifier, on a
20-year window containing ~8 independent stress clusters.

## Substrate & conventions (all frozen)

- `research/scalping_lab/substrate/minute/NQ/nq1m_2005_202605.parquet` (6,466,783 bars,
  sha256_16 dfd017ef, 2006-01-05 → 2026-05-29; nothing ≥ 2026-06 exists in the file).
- **Trading day**: calendar day with ≥ 200 minute bars in 09:30–15:58; `sess_close(d)` = close
  of the last bar ≤ 15:58 (handles early closes uniformly).
- **All price quantities in POINTS** (back-adjusted merge makes % returns era-distorted; point
  P&L × $20 is exact futures economics). Trailing-window percentiles make point-scale drift
  benign within any 63/252-session window.
- `ret(d)` = sess_close(d) − sess_close(d−1).
- **Vol state**: rv5(d) = sqrt(Σ over sessions d−4..d of Σ squared 1-min point returns in
  09:30–15:58). **Stress(d)** = percentile rank of rv5(d) within {rv5(d−251)..rv5(d)} ≥ 0.90.
- **Trigger thresholds from PRIOR days only**: q20/q80 of {ret(d−63)..ret(d−1)} (63 sessions,
  shift(1)). LONG iff Stress(d) AND ret(d) ≤ q20(d); SHORT iff Stress(d) AND ret(d) ≥ q80(d).
- **Execution**: enter at sess_close(d) + 1 tick adverse; exit at sess_close(d+1) + 1 tick
  adverse (next trading day, whatever its close time); 1 NQ; $2.18/side commission
  (C1 total $14.36/RT); consecutive signals = independent trades (conservative double-costing).
- **Roll/splice**: no exclusion (daily scale; back-adjustment removes roll gaps to first
  order). Robustness read per W10 convention: overnight-gap |z| > 6 (vs trailing 120-session
  mean/sd, shift(1)) days reported WITH/WITHOUT.

## Frozen gates (ALL required for PASS-SCREEN; constants are literature/repo defaults, untuned)

1. **N ≥ 300** trades (long + short pooled; cells also reported separately).
2. **Economics**: net $/trade with episode-block bootstrap CI_lo > 0 (episodes = maximal runs
   of stress sessions with gaps ≤ 5 sessions; resample episodes with replacement; 10,000 reps,
   seed 20260819). Plain trade-level iid bootstrap also reported.
3. **Cluster robustness**: pooled net positive in ≥ 5 of the 7 named stress clusters
   {2008-09, 2010, 2011, 2015-16, 2018, 2020, 2022} (cluster = trades with entry inside the
   calendar years listed; 2008-09 and 2015-16 are single clusters).
4. **Calm placebo**: identical quintile trigger with Stress(d) = FALSE must NOT be
   significantly positive (iid CI_lo ≤ 0). If the placebo is significantly positive the state
   variable is not doing the work and the family CLOSES regardless of gate 2.
5. **Plateau, not argmax**: 3×3 grid (stress percentile {85, 90, 95} × trigger quintile
   {20, 25, 30}) — pooled net/trade positive in sign in ALL 9 cells.
6. **Right-tail/tail safety**: top-1% of trades ≤ 50% of |net|; no single trade > 25% of
   |net|; ES5 (mean of worst 5% trades) reported with the full trade distribution.
7. **Correlation**: losing-day corr ≤ 0.25 vs the certified Solar B_SYM daily ledger
   (`HTFDIR01_DIRECTIONAL_TILT/out/daily_ledgers_dev.csv`, overlap 2022-01-03..2026-05-29);
   full-sample corr also reported; combined 50/50-vol portfolio right-tail retention reported.
8. **Robustness reads (reported, non-gating unless stated)**: (a) NFP/CPI-day exclusion using
   the committed `research/scalping_lab/data/hist_calendar_2005_2021.csv` plus the W8-2-era
   2022+ release dates where available (partial coverage disclosed) — demonstrates no
   re-expression of the closed 08:30-fade axis; (b) **2016-2026 subperiod must not be
   significantly NEGATIVE** (gating — forward-relevance); (c) 2-day-hold secondary read;
   (d) long-cell vs short-cell asymmetry; (e) WITH/WITHOUT roll-gap-flag days.

## Outcomes (frozen)

- **PASS-SCREEN**: all gates → candidate freeze; next step (portfolio integration study + NT8
  executable path) requires its own preregistration. NO promotion in this wave.
- **FAIL**: any gate → the stress-conditional reversal family is CLOSED on this substrate
  (one shot). The stress-state infrastructure (rv5 percentile series) is retained either way.
- **STATE-FAIL**: gate 4 trips → family CLOSED with the stronger conclusion that the
  conditioning claim itself failed on NQ.

Artifacts → `out/`. Registry: TESTING_LEDGER row after readout. Red team after readout,
before any candidate freeze. Data ends 2026-05-29 — the sealed/locked eras are untouchable and
untouched by construction.
