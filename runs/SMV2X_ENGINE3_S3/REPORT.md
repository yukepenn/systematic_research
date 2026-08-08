# SMV2X_ENGINE3_S3 — Engine #3 slate 3 (seq 396-398): ALL KILLED

_Frozen spec: `runs/SMV2X_ENGINE3_S3/spec.yaml` (committed 7abeb79 before any read). Authored
by the orchestrator from the execution agent's structured output — the subagent's Write tool
refused a direct REPORT.md write ("subagents should return findings as text"); every number
below traces to a committed `out/` artifact, per the spec's own requirement._

## Engine 396 — shock-day continuation (KILLED)
3-sigma daily shock threshold on trailing 60-session realized vol (12mo burn-in, causal):
only **N=12 events** clear the bar after burn-in (14 with no burn-in, 64 at a looser 2-sigma
threshold — confirmed a genuinely sparse event definition, not a bug). Gate N≥40 fails
structurally regardless of the economics.

| hold (sessions) | n | mean/event | net | t_NW | p_boot | WF same-sign |
|---|---|---|---|---|---|---|
| 1 | 12 | −$1,788.53 | −$21,462.32 | −1.48 | 0.108 | pass |
| 2 (center) | 12 | −$2,429.36 | −$29,152.32 | −2.22 | 0.014 | pass |
| 3 | 12 | −$7,306.03 | −$87,672.32 | −3.39 | 0.000 | pass |

The point estimate is significantly NEGATIVE at every hold — continuation trades AGAINST
sparse 3-sigma shocks lose money, not make it. **KILLED** (N gate fails; direction also fails).
One event (2024-07-31, −$20,599.36) is 71% of the center cell's total loss; excluding it, the
remaining 11 events average **−$777.54/event** (recomputed from `out/e396_events.csv`:
(−$29,152.32 − (−$20,599.36)) / 11 = −$777.54 — corrects an earlier draft figure of −$984,
caught by red-team). It is NOT excluded from the reported gate numbers (no ad hoc trimming);
this is context only, and the sign stays negative either way.

## Engine 397 — post-macro-announcement drift (KILLED, both cells)
FOMC and CPI reported SEPARATELY per spec (never pooled). NFP/PCE explicitly deferred (not
silently dropped — pooling all three would need ~150-160 events across two release schedules
without a single clean canonical page; documented in `out/calendar_sources.md`).

| cell | n | mean/event | t_NW | WF same-sign |
|---|---|---|---|---|
| FOMC (35 dates, entry 14:00 bar open, held to session close) | 35 | −$255.93 | −0.31 | FAIL (sign flips: 2022-24 −$480 vs 2025-26 +$233) |
| CPI (52 dates, entry first-RTH-30min open, 60min hold) | 52 | +$159.39 | +0.59 | pass (both mildly positive) |

Both flat/noise — neither clears |t_NW|≥2. **KILLED** (economic significance gate fails both
cells; FOMC also fails chronology). FOMC calendar sourced live from federalreserve.gov (high
confidence). CPI 2025-26 dates cross-checked against the 2025 government-shutdown disruption
(Sep-CPI delayed to 2025-10-24; Oct-CPI never published; Nov-CPI rescheduled to 2025-12-18);
2022-24 dates spot-verified against 4 live bls.gov archive pages.

## Engine 398 — post-expiration gamma-unclamp breakout (KILLED)
53 3rd-Friday expirations (2022-01..2026-05), 2 excluded as Good Friday holidays (2022-04-15,
2025-04-18, confirmed against the run's own session calendar) → 51 valid; only 28 produced an
actual T+1 breakout beyond the T-3..T RTH range (the other 23 stayed inside — the compression
constraint held, as designed).

| hold | n | mean/event | t_NW | WF same-sign |
|---|---|---|---|---|
| T+1 only (center) | 28 | +$325.64 | +0.68 | pass |
| T+1..T+3 | 28 | +$905.46 | +1.25 | pass |

Point estimates are positive but neither clears |t_NW|≥2, and N=28 < the 40-event gate.
**KILLED** (both the N gate and the significance gate fail; direction is at least not wrong,
unlike 396).

## Joint-loss-week complementarity (V4.1 §14, reported per spec regardless of engine failure)
None of the three engines earn meaningfully in the champion's 50 joint-loss weeks (mean
−$3,206/wk for the champion there): e396 −$246/wk, FOMC −$222/wk, CPI +$36/wk, opex +$11/wk —
all near-zero or mildly anti-complementary, none close to offsetting the champion's joint-loss
drag. This reinforces that these mechanisms, even if they had passed the standalone gates,
were not attacking the actual smoothness lever identified in SMV2Q (low path efficiency / high
flip rate weeks).

## Verdict
**ALL THREE ENGINES KILLED.** This closes Engine-3 slate 3 — the third and final NQ-only,
3m-bar-horizon slate (slate 1 = SMV2K seq 368-370, slate 2 = SMV2P seq 377-379, slate 3 = this
run), **9 candidates total, all killed**. Per the frozen `verdict_rule` and V4 §51: the
calendar/event-driven engine family is exhausted at the NQ-only 3m-bar horizon. Next step is a
cross-market data export (ES/RTY/YM, mirroring the SM1M NQ 1-minute export) before attempting
a 4th NQ-only slate — the highest-EVI remaining candidates from the wave-4 expansion passes
(cross-index dispersion, cap-tier catch-up, 6 others) all require that data and were deferred,
not dropped (see `research/system_master/deep_research/DR_V4_EXPANSION_PASSES_20260808.md`).

## Outputs
`out/e396_events.csv`, `out/e397_events.csv`, `out/e398_events.csv`, `out/e396_summary.csv`,
`out/e397_summary.csv`, `out/e398_summary.csv`, `out/e398_expiry_calendar.csv`,
`out/jointloss_complementarity.csv`, `out/calendar_sources.md`, `out/gates.csv`,
`out/verdicts.json`, `out/session_table.csv`, `out/redteam_notes.md`.
