# OTR_S0_TYPE1_REPRO — REPORT (2026-08-23)

**VERDICT: PASS. Pure-Python loop reproduces the frozen canonical Type-1 NT8 result
trade-for-trade.** All gates green (net diff −$305.00 fully explained, see below).

| Metric | Python (ARM_LEDGER) | NT8 canonical | Match |
|---|---|---|---|
| Trades | 2,915 | 2,915 | EXACT |
| Win rate | 39.3139% | 39.3139% | EXACT |
| Max DD | −$22,066.60 | −$22,066.60 | EXACT (cent) |
| Long/Short trades | 1,386 / 1,529 | 1,386 / 1,529 | EXACT |
| Short net | $43,278.56 | $43,278.56 | EXACT (cent) |
| Commission | $12,709.40 | $12,709.40 | EXACT |
| Net | $146,135.60 | $146,440.60 | −$305.00 (1 boundary trade) |
| PF | 1.131902 | 1.132213 | Δ 0.000311 (same trade) |

Per-trade diff vs the NT8 serialized list: **2,914 of 2,915 trades exact in entry time,
entry price, exit price, and PnL.** The single difference is the documented data-boundary
trade #2915 (entry 2025-01-31 16:08 @22990.25): the canonical ledger CSV ends at the
16:59 bar (737,707 rows) while the NT8 window contains 737,708 bars — NT8's session-close
exit filled on the missing final 17:00 bar @22974.00 (engine PnL −$329.36); Python exits
at the last available bar close 22958.75 (−$634.36). Δ = 15.25 pts = $305.00 exactly.
Non-mechanism, boundary-only, accepted.

## Load-bearing discovery (now CERTIFIED convention, was the source of a −84-trade error)

**V0's exit is `Close[0] <= TrailingStop[0]` / `>=` — an INCLUSIVE comparison against the
END-of-current-bar TrailingStop.** The vendor flip requires a STRICT cross, so a bar whose
close exactly TOUCHES the stop exits the position WITHOUT flipping the trend
(first observed instance: 2023-01-18 03:15, close = TS = 14807.25). Consequences:
- touch-exits leave the trend intact → the NEXT flip re-enters, producing consecutive
  same-direction trades (the NT8 list is full of them);
- because exit early-returns on its bar, a flip-exit consumes that flip's entry signal —
  direction chains persist until a touch/session-close exit changes parity.
This wrapper shape is Class B knowledge for all Track-S reconstruction (the original
SolarWindRKSelTime plausibly shares NT8 fill/exit conventions).

Other certified conventions (all required for exactness): market fills at next-bar open
slippage 0; exit checked before entry with early return; position open at session's last
bar exits at that bar's CLOSE; entries signaled on a session's last bar are dropped;
BarsRequiredToTrade=20; $2.18/side.

ARM_PYTHON: solar_wave_full signal series equality vs vendor ledger re-verified —
0 mismatches in signal_trade and signal_wave over 737,707 bars.

Artifacts: `out/results.json`, `out/trades_arm_ledger.csv`.
Engine: `research/original_trader_reconstruction/solar_family/src/otr_engine.py`.
