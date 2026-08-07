# MONITOR-01 — quarterly overshoot-ratio health check (frozen 2026-08-07, per C01 T0-11)

Free, zero-trial, no trading. Run once per calendar quarter on fresh 1-min NQ closes.

1. Export engine-exact 1-min bars for the trailing 4 quarters (AuditBarExport1 pattern).
2. Compute DC segments (src/analytics/dc_overshoot.py) at theta=179 ticks AND pooled sigma bands
   theta/sigma in [2.0, 9.4] (sigma = trailing mean |dclose| over 460 bars, ticks/bar — see
   src/analytics/u4_overshoot_invariance.py).
3. Statistic: r = mean(omega)/theta per band, trailing-4-quarter window.
4. Baseline (2022-01..2026-07, DC02b): sigma-banded r year-CV 0.013-0.020; theta=179 1-min yearly
   r 1.145-1.218.
5. ALARM (either): sigma-banded r < 1.05 for two consecutive quarters; or drift of banded r
   exceeding 3x the DC02b band CV. Alarm consequence: freeze any deployment intent, re-run
   FILL_AND_TAIL-style attribution before any decision. The edge IS r > 1; r -> 1.0 removes it.
6. Log each reading in research/operational/monitor01_log.csv (date, window, band, r, verdict).
