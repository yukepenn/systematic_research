# W1-2 H-A1/H-D5 Readout — CLOSED (negative)

Date: 2026-08-07. Spec: `specs/W1-2_HA1_last30_momentum.md` (frozen 1cf4cb2 before readout).
Data: 1,094 sessions, 2022-01 → 2026-05-31 (holdout/seal excluded). Zone: ADJACENT_INTRADAY.

| | P1 rest-of-day → last-30 | P2 first-30 → last-30 |
|---|---|---|
| OLS slope (HC1 t) | +0.0113 (t = 1.04) | −0.0051 (t = −0.21) |
| Sign agreement | 49.3% (p = 0.67) | 47.5% (p = 0.12) |
| Gross ticks/day | −1.64 | −7.45 |
| **Net after C1** | **−4.51** | **−10.32** |
| Net by year 22/23/24/25/26 | +38.6 / −6.9 / −12.6 / −27.4 / −29.3 | −7.7 / −10.7 / −14.6 / +2.9 / −37.4 |
| Era split 2022-23 vs 2024-26 | +15.9 vs −21.5 | −9.2 vs −11.3 |
| \|r_rod\| tercile net (small/mid/large) | −6.4 / −3.8 / −3.4 | — |

**Verdict (frozen rule "neither significant"): H-A1 CLOSED for NQ.** The Gao-Han-Li-Zhou /
Baltussen intraday-momentum prior fails locally: whatever last-half-hour persistence NQ had
lived in 2022 and has been gone or inverted since 2023 — consistent with DR-A's predicted
0DTE-era weakening. Not eligible for retry on this axis without new preregistration and a
mechanically different construction. Conditioning-feature (role B) reuse would require its
own spec and a demonstrated interaction, which this readout does not suggest (tercile
gradient is mild and all-negative).

Honesty notes: 3-min close prices (not tradeable mid); C1 costs; entry at the 15:30 bar
close. None of these choices could flip a t=1.04 into a real effect. DoF charged: 2.
Artifacts: `ha1_last30.csv` (per-day returns).
