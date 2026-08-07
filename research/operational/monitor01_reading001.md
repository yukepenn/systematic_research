# MONITOR-01 reading #1 — BASELINE (2026-08-07)

Per `MONITOR01_PROTOCOL.md` (frozen 2026-08-07) and `LOCKED_FORWARD.md`. Reading #1 is the
baseline on committed, research-consumed data (through 2026-07-31): **zero virgin data consumed**.

## Basis (stated per protocol)

- Data: `runs/B01A_BARS_1M/nq_1m_2022_2026.csv` (1,620,044 engine-exact 1-min bars,
  2022-01-02 18:01 .. 2026-07-31 16:59 ET session time).
- Window: trailing 4 quarters, segments assigned by exit-bar timestamp (`i_next`) in
  2025-08-01 00:00 .. 2026-07-31 23:59:59 ET → 6,595 theta=179 segments.
- Engine: `src/analytics/dc_overshoot.dc_segments` verbatim, theta=179 ticks, tick=0.25.
- **Sigma basis: 1-min** — trailing mean |dclose| over 460 one-minute bars, in ticks/bar,
  causal, includes current bar (same construction as `u4_overshoot_invariance.py`, applied to
  the 1-min series of `u4_check_1m.py`). Note DC02b's published band r values are 3-min-basis
  (3-min omega runs ~5-10% higher); cross-basis r levels are NOT directly comparable, so drift
  is measured against the same-basis (1-min, theta=179) full-history baseline.
- theta/sigma at segment birth (`i_flip`). Yearly mean sigma_1m (ticks/bar):
  2022 16.34, 2023 10.31, 2024 12.94, 2025 17.92, 2026 25.11.

## Band definition (DC02b reconstruction — verified)

Re-running the DC02b edge construction (3-min pooled, 9 thetas, geomspace of ratio
q0.005..q0.995, 11 points, rounded 0.1) reproduces the frozen artifacts exactly:
edges `[0.6, 0.9, 1.4, 2.0, 3.0, 4.3, 6.4, 9.4, 13.7, 20.2, 29.7]`; mass bands
theta/sigma in [2.0, 9.4] = (2.0,3.0], (3.0,4.3], (4.3,6.4], (6.4,9.4] with n=103,031 and
year-CVs 0.0132 / 0.0135 / 0.0202 / 0.0142 (the documented "CV 0.013-0.020, 103k segments").
Pipeline validation: 1-min theta=179 yearly r = 1.165/1.145/1.199/1.212/1.218 (2022-2026),
reproducing DC02b's 1.145-1.218 exactly.

## Reading #1 results (1-min, theta=179, trailing 4Q)

| band (theta/sigma) | r (window) | SE | n | r full-hist 1m | rel. drift | 3x DC02b CV | flag |
|---|---|---|---|---|---|---|---|
| (2.0, 3.0] | 1.2558 | 0.1094 | 197 | 1.3753 | -8.7% | 3.96% | drift_flag (see below) |
| (3.0, 4.3] | 1.2278 | 0.0519 | 848 | 1.2518 | -1.9% | 4.05% | none |
| (4.3, 6.4] | 1.2021 | 0.0308 | 2,179 | 1.2006 | +0.1% | 6.06% | none |
| (6.4, 9.4] | 1.1966 | 0.0323 | 1,882 | 1.1816 | +1.3% | 4.26% | none |
| **pooled [2.0, 9.4]** | **1.2064** | 0.0202 | 5,106 | 1.2072 | -0.1% | — | none |

Out-of-band window segments: 12 below 2.0, 1,477 above 9.4 (excluded from banded statistic).
Tick-basis check: window r = 1.2060, mean omega = 215.9 ticks, n = 6,595 — at the top of the
2022-2026 yearly range (1.145-1.218), consistent with the high-sigma regime (low theta/sigma
=> higher r per DC02b).

## Alarm rules applied

1. **Banded r < 1.05?** NO band is below 1.05 (minimum 1.1966). Rule needs two consecutive
   quarters; count = 0.
2. **Drift > 3x DC02b band CV?** Bands 2-4: no (-1.9%, +0.1%, +1.3% vs thresholds
   4.05%/6.06%/4.26%). Band (2.0,3.0] exceeds numerically (-8.7% vs 3.96%) but the cell holds
   only 197 segments (3.9% of in-band mass): the deviation is 0.1195 in r = **1.1 SE** — pure
   sampling noise territory. The 3xCV threshold was calibrated on pooled ~103k-segment DC02b
   cells and is far inside sampling noise for a thin theta=179-only cell. Logged as
   `drift_flag / WATCH`, not an alarm; recheck at reading #2.

## VERDICT: NO ALARM — baseline established, edge intact (pooled banded r = 1.21 >> 1.05).

Baseline values for future drift comparison are the `r full-hist 1m` column above
(2022-01..2026-07, same basis).

## Next

- **Reading #2 due on/after 2026-11-01** — requires a FRESH engine-exact 1-min bar export
  (AuditBarExport1 pattern) extending through 2026-10-31; the export itself consumes nothing.
  Window: 2025-11-01..2026-10-31. Compare per-band r against the baselines above; the
  two-consecutive-quarter clock for rule 1 starts only if a band prints < 1.05.
- Log: `research/operational/monitor01_log.csv` (one row per band + pooled summary row).
- Reproduction script (scratch, deterministic from repo artifacts): dc_segments(close_1m, 179),
  sigma_1m rolling-460 mean |dclose|, bands [2.0, 3.0, 4.3, 6.4, 9.4], window filter on i_next.
