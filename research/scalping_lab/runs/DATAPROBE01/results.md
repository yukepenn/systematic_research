# DATAPROBE01 Results — 2026-08-07

Engine: NT8 8.1.8.1 via RunStrategyBacktest (jobs b54859c5fc5347d1, 34a721751b794840).
Probe strategy: `SWScalpDataProbe_v1` (src committed a53dbaa before execution; no orders).
Outputs: `out/probe_ticks.csv`, `out_depthcheck/probe_ticks.csv` (3M lines each, capped;
local only — not committed, too large; regenerate with the committed source).

## Findings (all four spec questions answered)

1. **Timestamp resolution: millisecond-class (~4ms quantization).** 250 distinct sub-second
   values (= 1000/4), e.g. `.0400000`, `.0440000`, `.0480000`. Latency surface can honestly
   test 250ms/500ms/1s/2s/5s. Duplicate timestamps: 46% (Last), 61% (Bid/Ask) — same-ms
   bursts are common; event ORDER within a millisecond is preserved by series order, and
   same-timestamp cross-series ordering must be treated as unknown (±4ms sync ambiguity).
2. **Historical Bid/Ask 1-tick series EXIST and download on demand** via
   `AddDataSeries(new BarsPeriod { MarketDataType = Bid/Ask, Tick, 1 })`:
   - NQ 09-26, session 2026-07-14/15: Bid 1.46M, Ask 1.44M events (vs 98.5k Last ticks —
     BBO updates ≈ 15× trade frequency).
   - NQ 12-25, session 2025-10-14/15: Bid 1.40M, Ask 1.41M — **L2 depth matches L1 depth**
     (at least back to 2025-10; assume ≈ 2025-08 pending spot check).
3. **Per-tick trade volume is real** (Last: min 1, max 50, mean 1.10, zero-volume 0%).
4. Event rates: ~98.5k trades + ~2.9M BBO updates per session → full-year L2 dataset ≈
   0.7B rows. Export-to-parquet pipeline required; hourly `.ncd` cache persists downloads.

## Open semantics (flagged, not assumed)

- Bid/Ask series `Volume` field (mean ≈ 1.8, max ≈ 112): could be BBO size, size delta, or
  update aggregation. **L3 status stays UNKNOWN until a dedicated check** (e.g. compare
  against Last-tick trade sizes at identical timestamps; or NT documentation).
- Engine loads bars from session start regardless of `from` (trace: requested 09:25 ET,
  loaded from 18:00 ET) — exports must session-filter downstream; MaxLines cap hit both runs
  (truncation at 09:36 ET / 10:16 ET respectively). Fine for capability probing; the real
  export pipeline needs per-hour chunking or per-day runs with higher caps.

## Level determination (final for P1)

| Level | Status |
|---|---|
| L0 OHLCV | CONFIRMED (minute to 2005) |
| L1 last-trade events | **CONFIRMED**, ms-class, ~12 months (2025-08 → seal) |
| L2 BBO quotes | **CONFIRMED**, same depth as L1 |
| L3 top-of-book sizes | UNKNOWN (field-semantics check pending) |
| L4 multi-level depth | BLOCKED_BY_DATA (no replay recordings; paid data banned) |

Families S6/S7 remain gated on the L3 check; S8 (microprice/queue) partially unlocked
(price-level microprice needs sizes → gated; imbalance-free BBO features unlocked);
S9 (OFI via signed trades + BBO), S10 (spread state) fully unlocked at L2.
