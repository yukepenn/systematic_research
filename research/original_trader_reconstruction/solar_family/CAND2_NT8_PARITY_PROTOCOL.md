# CAND2 → NinjaScript parity protocol (directive v3.0 §7-§8, PHASE C3)

Strategy: `src/ninjascript/OriginalTraderSolarCAND2_v1.cs` (research-only,
fail-closed realtime). Copy into NT8 `bin/Custom/Strategies/`, compile (F5).
If iterated, RENAME the class per iteration (_v2, _v3) — hot-reload rule.

## Execution status
NT8 Strategy Analyzer runs require the analyzer UI (CrossTrade is NOT part of
this campaign; directive §9 keeps it non-required). Everything below is ready
to execute the moment an analyzer session is available. No purchase, no live
account, backtest only.

## Fixed analyzer settings (all layers)
NQ back-adjusted merge series as in the frozen-truth parity (research/
solar_wave_parity/type1_2023_2025/parity_report.md); 1-Minute Last; Tick Replay
OFF; Break at EOD ✔; slippage 0; Standard fill; exit-on-session-close ✔ 30 s;
lookback 256; BarsRequired 20; DefaultQuantity 1. `To` dates per the CME
boundary rule (one second before next 18:00 ET open).

## Layer A — cent-exact daily labels (highest authority)
Window 2023-01-03 → 2023-01-17, commission $4.18/RT (Lifetime template),
defaults (gate on, stop OFF, resume OFF).
PASS = per-day W/L structure matches targets_perday_analysis.csv on the days
Python matches to the cent (1/10: 9 trades, 1/11: 4, plus subset-days).
Compare trade-by-trade timestamps/prices vs Python
(`runs/OTR_R1_SERIES/out/` reference streams).

## Layer B — two-year master
2023-01-01T06:00Z → 2025-02-02T22:59:59Z, commission $4.18/RT, defaults.
Python reference (CAND2 frozen): n 4598, net 264,955, WR 40.08, PF 1.152,
DD −31,934, hold 95.56 (109.6/81.9), consec 7/15.
Tolerance: trades ±1%, net ±2%, others band-per-CONVENTIONS. Any excess =
gate-timing divergence (see below), to be localized by date.

## Layer C — weekly windows (era-configured)
Pick 4 windows from runs/OTR_R5_CAND2_WEEKLY_VALIDATION: 10/26 and 11/23
(near-exact dev weeks), 1/4/2026 (DM-sensitive), 10/12 (high-count).
Commission $0. Era config: UseInitialStop ✔ StopPoints 65 (all four).
Compare against out/WEEKLY_FINGERPRINT_MATRIX.csv rows (variant old/new180
_s65_noDM) — NOT against the screenshots directly (that comparison lives in R5).

## Known semantic divergence to MEASURE (not assume away)
1. Gate timing: Python = fill-bar with same-bar exit realized; NT8 port =
   decision-close projection (Close[0] exit proxy; decision-bar clock).
   Count decision flips: expected rare (only threshold-boundary bars).
   If Layer B diverges >1% trades, re-run the Python engine in decision-close
   mode and re-verify the 42/42 labels — if labels still hold, ADOPT
   decision-close as the identified semantics (it is what NT8 code can
   natively express, hence what the trader's own code most plausibly did).
2. Session-close fill: port bookkeeping uses last-bar close (S0-certified);
   NT8 fills ~16:59:30 market. Engine totals may include a boundary trade the
   serialized list omits (known NT8 quirk).
3. Last-bar-decided entries: Python drops them; NT8 behavior re-verify
   (S0 certification says effectively dropped).

## Results recording
Create `runs/OTR_R6_NT8_PARITY/spec.yaml` BEFORE reading any analyzer output;
record per-layer verdicts in REPORT.md; ledger row OTR-R6-001.
