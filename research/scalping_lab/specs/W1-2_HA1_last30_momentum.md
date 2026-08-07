# W1-2 — H-A1/H-D5: Last-30-Minute Hedging Momentum (Tier-0, preregistered)

Date: 2026-08-07. Zone: **ADJACENT_INTRADAY** (30-min hold — can never claim a scalp title).
Spec frozen BEFORE any statistic is read.

## Hypothesis
Gamma / leveraged-ETF rebalancing makes the NQ cash-session direction persist into the last
half-hour: rest-of-day return predicts the 15:30→16:00 ET return (Gao-Han-Li-Zhou form;
Baltussen et al futures-panel form). Expected sign: positive.

## Frozen design
- Data: `runs/AUDIT03_BARS/nq_3m_2022_2026.csv` (3-min closes, committed artifact).
  Sessions with dates ≤ 2026-05-31 ONLY (holdout 2026-06/07 excluded; ≥2026-08 sealed).
  Days lacking both the 15:30 and 16:00 bar stamps (early closes) are skipped.
- Prices: closes of bars stamped 09:30, 10:00, 15:30, 16:00 ET.
- Predictors (2, both charged): P1 rest-of-day r_rod = ln(P1530/P0930); P2 first-30
  r_f30 = ln(P1000/P0930). Target: r_last = ln(P1600/P1530).
- Tests per predictor: (a) OLS slope + robust (HC1) t (1 obs/day, n≈1,080); (b) sign-
  agreement rate vs 50% (binomial); (c) trading transform: 1 NQ, enter sign(predictor) at
  the 15:30 bar close, exit 16:00 bar close, BENCHMARK_C1 costs ($4.36 + 2×1 tick slip =
  $14.36/RT); report gross & net ticks/day, PF, by year and by session-|r_rod| tercile.
  (BBO_EXEC not applicable at 3-min resolution — noted per Amendment §3; if this escalates,
  Tier-1 runs on minute/tick data with BBO_EXEC.)
- Conditioning diagnostic (not charged, no gating): vol-tercile of trailing 20-session
  realized vol.

## Frozen interpretation
- Slope t ≥ 2 (either predictor) AND net ticks/day > 0 after C1 with same sign in ≥ 3 of 4
  full years → escalate to Tier-1 (new spec: 1-min prices, 2005+ history, BBO_EXEC).
- Slope significant but net ≤ 0 → information-without-economics: record, close standalone,
  eligible only as a role-B conditioning feature later.
- Neither significant → H-A1 CLOSED for NQ (record; the literature prior failed local test).
- 0DTE-era check (reporting only): 2022-23 vs 2024-26 slope halves reported side by side.

DoF: 2. Deliverables: artifacts/ha1/ha1_last30.csv + ha1_report.md; registry row at readout.
