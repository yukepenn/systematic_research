# G3_FOMCDRIFT_20260906 — slow-capital post-FOMC drift in bonds — REPORT

**Ledger:** G00084, family GENESIS3_EVENT · **Evidence status of every number:** DISCOVERY_CONSUMED
**Verdict:** **CLOSED AT SCOPE (§28)** — G2 FAIL (UNDERPOWERED_STILL), G4 FAIL (modern-negative).
No FOMCDRIFT01 candidate.

## Frozen object (as preregistered)

FOMC scheduled decision days 2009-01-01..2026-07-31 from the repo calendar artifact
(`runs/GENESIS_H2_CALENDAR_20260828/out/calendar_artifacts/fomc_meetings_2006_2026.csv`, 140 events,
cross-checked IDENTICAL to the G2_F12 embedded calendar over 2006..2026-04). Signal = sign of ZB
close(D-1)→close(D0) (points, causal at D0 close). PRIMARY = hold ZB in the signal direction
close(D0)→close(D+5), after-cost (1 tick/side + $4.36/ctrRT = $66.86 RT, BASIS COMMISSION+SPREAD
MODELED). Data: certified causal-roll dailies reused AS-IS from `runs/G3_AUCTCYCLE_20260906/out/`
(ZB sha `9446e7f1…`, ZN sha `13fc5165…`, both asserted equal to that run's manifest; seal max
2026-07-31 asserted).

## Event realization

140 calendar events → 131 traded. Excluded and listed: 2 BEFORE_SERIES (2009-01-28, 2009-03-18),
4 SESSION_MISSING_DATA_HOLE (2014-01-29, 2015-12-16, 2018-12-19, 2024-12-18 — multi-day holes in
the TD raw daily store), 1 WINDOW_BEYOND_SEAL (2026-07-29), 2 ZERO_SIGNAL_NO_TRADE (2011-06-22,
2025-01-29). Min inter-event gap 17 sessions — 5-day windows never overlap.

## Gate table (program-printed; full text in out/gate_table.txt)

| Gate | Result | Spec | Observed |
|---|---|---|---|
| G1_MDE_first | PASS | MDE printed before observed (~140 events) | N=131; MDE80 = 0.4833 pt ($483/ct); printed before observed |
| G2_edge | **FAIL** | after-cost mean > 0 AND event-block CI95 excludes 0 AND shift-null p < 0.05 | mean −0.1529 pt, CI95 [−0.5274, +0.2242], p = 0.5000 |
| G3_control | PASS | beats matched non-FOMC same-weekday days (same 5-day window) | diff +0.1204 pt (FOMC −0.1529 vs ctrl −0.2732) |
| G4_era_mandated | **FAIL** | modern-negative = FAIL; ZLB-only = REGIME-LOCAL-DEAD | ZLB:pos, hiking:neg, inflation:neg → modern-negative |
| G5_cost | PASS | trivial at 5d; {1,2}-tick band printed | primary −0.1529, stress −0.2154 pt; no sign flip; cost = 3.0% of gross sd |
| G6_battery | PASS | weekly-vol lead; rho-to-P1 and rho-to-ZBMACRO01 printed | Sharpe_wk −0.19; ρ_P1 d −0.008 / w −0.015; ρ_ZBM d −0.034 / w −0.010 |

Power language on the G2 FAIL: **UNDERPOWERED_STILL** (MDE80 0.4833 > 3×|obs| 0.4586 — knife-edge).
Note the point estimate is the **wrong sign for the mechanism** (5-day continuation of the
announcement-day move is *negative*), so the closure does not hinge on power.

## Era table (out/era_table.csv)

| era | n | gross pt | after-cost pt | sign | hit |
|---|---|---|---|---|---|
| ZLB_2009_2015 | 51 | +0.2791 | +0.2122 | pos | 0.549 |
| hiking_2016_2021 | 46 | −0.5353 | −0.6022 | neg | 0.348 |
| inflation_2022_2026 | 34 | −0.0257 | −0.0926 | neg | 0.500 |

## Secondary path (reported, no gate)

Signal-aligned cumulative gross mean drifts from +0.06 pt at h=1 to **−0.63 pt at h=15**
(monotone deterioration past h≈5): at horizon the representation is a *reversal*, not a drift.

## ZN mirror (reported, no gate)

n=132 (2016-09-21 additionally a ZN data hole): after-cost +0.0082 pt, CI95 [−0.142, +0.161],
shift-null p 0.935; eras ZLB +0.131 / hiking −0.017 / inflation −0.141 — same modern-negative shape.

## Classification and reading

- **G3 PASS next to G2 FAIL is a classification, not a conflict**: the same-rule matched control is
  itself strongly negative (generic ZB 1-day-move 5-day continuation ≈ −0.27 pt after cost — the
  campaign law "everything else mean-reverts" showing up again). FOMC days are *less mean-reverting
  than a generic day*, but there is no positive drift to harvest.
- The NBER slow-capital drift mechanism, in this representation (D0-close direction, 5-day hold,
  2009+), is **not present in ZB after cost**; the ZLB-era positive sign is the regime that ended.
- ρ to P1 and to ZBMACRO01 ≈ 0 — moot after closure, printed as mandated.

## Anomalies

1. Four FOMC decision days are absent from the certified ZB session calendar (TD raw data holes);
   excluded-and-listed, N=131 vs ~140. ZN misses a fifth (2016-09-21).
2. UNDERPOWERED_STILL is knife-edge (0.4833 vs 0.4586); recorded verbatim, but the wrong-signed
   point estimate makes the closure interpretation power-robust.
3. Control-pool windows may overlap FOMC post-windows (spec-literal pool) — conservative for G3.
4. Bootstrap CI and t-CI agree to ~0.01 pt (second-computation cross-check consistent).
5. REPORT.md could not be written into the run directory (harness refused the Write); full report
   content returned in structured output instead, per pod rules.

## Outputs

`out/gate_table.txt` (full program log + gate table), `out/event_table.csv` (140 rows: 131 traded
with per-h path, 9 excluded/no-trade listed), `out/era_table.csv`. Program: `src/run_fomcdrift.py`
(seed 20260906, 999 shared-draw circular shifts, 10,000-draw event-block bootstrap).