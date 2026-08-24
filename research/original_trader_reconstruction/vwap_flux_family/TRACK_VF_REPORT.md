# TRACK VF — VWAP Flux report (passes 1-3, 2026-08-24)

## What is now IDENTIFIED (Class A)

1. **The vendor product.** The 2026 strategy's visible parameter block is ninZa **VWAP
   Flux**: 13/13 parameter labels match in exact settings-UI order (EV-019, official
   Trader Manual archived in `../vendor_docs/`). Release date 2026-01-09 coincides with
   the trader's 2026 system change. The trader ran CUSTOM values (Anchor 60 / Amount 5 /
   Trend EMA-20 / Levels 95-75-50-25-5 / Qty 3 / CloseThr 10 / Split 5) vs manual-shown
   20/5/14-EMA/100-70-50-30-0/4/80/30 — he tuned every group.
2. **The risk wrapper.** EV-017's repeated "largest loss ≈ −$2,600" is reproduced EXACTLY
   by an **intrabar protective stop 130 NQ points (=$2,600) from entry** (VF2/VF3 loss
   tails: −2600, −2600, −2600...). The alternative reading — LossLimit=2500 evaluated at
   bar close with next-open fill — produces overshoot tails (−2,785/−3,190) INCONSISTENT
   with the evidence and is REJECTED for the 2026 family. (Track SD's session-level
   LossLimit conclusion for the DSTM era is unaffected.)

## What remains BLOCKED (honest state after 3 bounded proxy passes)

The signal INTERNALS. The manual documents the architecture (segmented anchored VWAP
layers → 5-level cloud; trend = fair-value + cloud break + slope; signals = pullbacks
into the cloud, ≤N per trend, ≥split bars apart, close-position validity filter) but NOT
the math (level aggregation across layers, fair-value definition, trend triple-condition,
exact trigger). 21 bounded cells across VF1 (12), VF2 (6), VF3 (3):
- Trend-flip exits: WR 17-23%, catastrophic — wrong.
- Re-break exits: WR 76-91% scalps (hold 7-16m) — mirror of the target — wrong.
- Median/stop-only exits: intermediate, still D ≥ 21 — wrong.
- Closest count match: the pullback-entry stream itself (178 vs 183 in window A) — the
  ENTRY architecture reading is plausibly right; the outcome geometry (WR 37.7, W/L 1.58,
  hold 40m) is not reachable with any bounded exit on those entries → the true signal
  placement/trigger differs from all readings tried.
Per the amended stop rule: direct external evidence is CONSUMED; alternatives are NOT
observationally equivalent (they fail); the family is **BLOCKED BY MISSING MECHANISM
INFORMATION**, not closed.

## The unblock (owner decision, escalated per directive §50)

**Purchase VWAP Flux (ninza.co, $300 one-time).** Running the licensed indicator on our
NT8 minute data and reading its public NinjaScript series (Signal_Trade/Signal_Trend/
Signal_Cum_Delta — documented API, no decompilation) converts signal-internal
identification from unbounded guessing into direct observation: entries become known
exactly; only the trader's wrapper (stop 130 already identified + exit rule) remains to
fit. Same logic applies to ThunderZilla ($700) IF Track-B/TZ evidence firms up — currently
weaker (EV-020: parameter structure does not match the EV-007 blocks).

Alternative free path: none identified — the "No Tick Replay" historical approximation
(Dec-2025 vendor tech) is also undocumented.

Artifacts: runs/OTR_VF1_FLUX_ARCH, OTR_VF2_STOP130, OTR_VF3_MEDEXIT. The 08-23 V-proxy
(runs/OTR_V1..V3) stays preserved as a demoted behavioral-mimic artifact.
