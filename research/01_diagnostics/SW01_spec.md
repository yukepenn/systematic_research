# SW01_EPISODE_AND_EXIT_ATTRIBUTION — Preregistered Spec

_Committed before results are read. 2026-08-06. Thesis Experiment 2. No trading-logic changes; pure instrumentation._

## Hypothesis (H-004)
A deterministic per-bar state ledger (vendor signal series + reconstructed trend episodes) joined to the R01 trade ledger will localize where P&L, giveback, and losing clusters arise (by episode, wave, flip regime, path efficiency, volatility, session). Falsified (integrity failure) if the export is nondeterministic or state values are inconsistent with executed trades (e.g., a Type-1 entry bar whose Signal_Trade ≠ ±1).

## Instrument: `SolarWaveRKLedgerV1` (new strategy class; trades nothing)
- Instantiates `RenkoKings_SolarWaveRK(Close, 90, 179, 5, 10, true, 10)` exactly as the baseline does.
- OnBarUpdate (BarsInProgress 0 only): appends CSV row — `time,close,signal_trade,signal_trend,signal_wave,trailing_stop,trend_vector`.
- Buffered StreamWriter; opened lazily; flushed+closed in State.Terminated. Export path is a [NinjaScriptProperty] (default under research/01_diagnostics/).
- Never calls an order method. Vendor assembly untouched.

## Runs
- L01: export over canonical window (2023-01-01T06:00:00Z → 2025-02-02T22:59:59Z), 1-min Last.
- L02: identical rerun → **determinism gate: byte-identical file hash** (excluding any timestamp header, which the exporter must not write).

## Derived analytics (Python, src/analytics/sw01_ledger.py)
- Trend-episode reconstruction: episode = maximal run of constant sign(Signal_Trend); episode ID, bars-since-start, wave count within episode (|Signal_Wave| transitions), flip count in trailing 60/120 bars, path efficiency |ΔClose|/Σ|ΔClose| over 60/120 bars, close-to-TrailingStop distance in ticks.
- Join to R01 trades on entry bar time → every trade tagged with: episode ID, entry wave, entry flip-count, entry efficiency, entry stop-distance, plus existing MAE/MFE/exit-reason/session tags.
- Preregistered decompositions: PnL by episode (concentration: share of net from top decile of episodes), by wave at entry, by flip-count bucket (0-1/2/3+), by efficiency quartile, by stop-distance quartile, by volatility (60-min realized, terciles), MFE-giveback by exit reason, opposite-Type-1 sequence analysis (false-start clusters: thesis failure mode 1).

## Preregistered gates
- **PASS (integrity):** L01/L02 byte-identical; 100% of R01 entry bars have |Signal_Trade| = 1 (Type-1) matching trade direction sign; bar count = 737,708.
- **FAIL:** any mismatch between exported signals and executed trades → STOP, diagnose signal-timing before any Phase-2 experiment (constitution §19 analog for historical/export parity).
- This experiment produces NO candidate and NO promotion; outputs feed SW02/SW03/SW05 designs.
