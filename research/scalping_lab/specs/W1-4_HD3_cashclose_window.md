# W1-4 — H-D3 (≈Z4): Cash-Close Imbalance-Leak Window (Tier-0, preregistered)

Date: 2026-08-07. Zone: ADJACENT_INTRADAY (6-min hold). Spec frozen BEFORE readout.

## Hypothesis (DR-D)
NOII/NYSE closing-imbalance publication begins 15:50 ET; index-arb hedging of MOC flow
leaks into NQ. The futures move just after publication proxies the imbalance sign and
predicts continuation into the 16:00 cash close. Expected sign: positive.

## Frozen design (3-min-resolution construction — resolution caveat below)
- Data: `runs/AUDIT03_BARS/nq_3m_2022_2026.csv`, sessions ≤ 2026-05-31, days having all
  bar stamps {15:48, 15:54, 16:00}.
- ONE charged predictor: r_pre = ln(P1554/P1548) (the 15:48→15:54 move, straddling the
  15:50 publication start — the closest 3-min mapping to DR-D's 15:50→15:55).
- Target: r_moc = ln(P1600/P1554).
- Tests: OLS slope + HC1 t; sign agreement (binomial); trading transform 1 NQ,
  sign(r_pre) entered at the 15:54 bar close, exit 16:00 close, BENCHMARK_C1; net
  ticks/day overall, by year, era split 2022-23 vs 2024-26.

## Frozen interpretation
- t ≥ 2 AND net > 0 after C1 in ≥ 3 of 4 full years → Tier-1 escalation (new spec, 1-min
  prices, exact 15:50/15:55 boundaries, BBO_EXEC).
- Significant but uneconomic → role-B eligible only, standalone closed.
- Not significant → **CLOSED AT 3-MIN RESOLUTION**. Because this mapping is crude (the
  predictor window includes 2 pre-publication minutes), one — and only one — preregistered
  1-min reconstruction remains permitted later; its spec must cite this readout.

DoF: 1. Deliverables: artifacts/hd3/hd3_report.md (+ per-day csv); registry row at readout.
