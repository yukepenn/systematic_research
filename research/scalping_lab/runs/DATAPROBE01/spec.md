# DATAPROBE01 — NT8 tick-data capability probe (no P&L, no selection)

Date: 2026-08-07. Type: capability probe (Tier −1); reads NO strategy profitability.

**Questions:** (1) historical tick timestamp resolution (ms? s?); (2) do historical Bid/Ask
1-tick series exist on the NT server for NQ (AddDataSeries MarketDataType.Bid/Ask); (3)
per-tick volume fidelity; (4) event counts per series in a liquid RTH hour.

**Design:** strategy `SWScalpDataProbe_v1` (no orders ever; realtime fail-closed). Primary =
NQ 09-26 1-tick Last; added series = 1-tick Bid and 1-tick Ask. Every OnBarUpdate appends
`bip,barIdx,timestamp(.fffffff),price,volume` to CSV. Window: 2026-07-15 09:25–10:35 ET
(13:25–14:35 UTC) — inside the development period, outside the seal. Output:
`research/scalping_lab/runs/DATAPROBE01/out/probe_ticks.csv`.

**Interpretation rules (fixed in advance):** all-zero sub-second digits across the RTH hour
⇒ second-resolution timestamps ⇒ latency grid truncates at 1s and all sub-second horizons
are re-labeled "next-event" horizons. Bid/Ask series failing to load or loading empty ⇒ L2
explicit-series path dead; L2 then depends only on the Tick-Replay-stamp path (separate
probe; MCP cannot enable Tick Replay, so that check runs in the NT8 UI or via bid/ask
columns if present). Volume all-1 or all-0 ⇒ volume aggregation unreliable at tick level.
