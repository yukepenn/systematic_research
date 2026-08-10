# Dom01DepthRecorder_v1 output schema (dom01-collector-schema-v1)

Full narrative documentation lives in `REPORT.md` at the repo root of this run
(`runs/DOM01_LIQUIDITY_STATE/collector/REPORT.md`, delivered by the agent that built this via
its structured output). This file is the quick machine-adjacent reference: column layouts only.

Every collector run (one State.DataLoaded -> State.Terminated lifecycle, i.e. one chart attach)
writes five files into `ExportDir`, all sharing one filename prefix:
`{Tag}_{StartUtc:yyyyMMdd_HHmmss}_{RunId[0:8]}_<stream>.<ext>`

## `<prefix>_manifest.json`
One JSON object. Written once at DataLoaded (partial, `EndUtc: null`), rewritten in place at
Terminated with final counts, cap-reached flags, and SHA-256 checksums of the four CSV files.
Fields: SchemaVersion, CollectorClass, RunId, StartUtc, EndUtc, Tag, InstrumentFullName,
InstrumentRoot, ContractExpiry, Exchange, TradingHoursTemplateName, TradingHoursTimeZoneDisplayName,
MachineLocalTimeZoneId, DataConnectionTypeName, DataConnectionOptionsTypeName,
DataConnectionDisableL2Data, DataConnectionStatusAtInit, DepthLevelClass, SequenceFieldNote,
EventTimeSemanticsNote, KnownLimitations[], and at Terminated: FinalCounts, CapReached,
FatalErrorOccurred, FileChecksumsSha256.

## `<prefix>_depth.csv`  (MBP depth-by-price-level events; the primary DOM01 stream)
`RunId,SeqLocal,RecordedUtc,EventTime,EventTimeKind,Side,Level,Price,Size,Operation,MarketMaker,IsReset,IsTopOfBook`
- `Side` = MarketDataType (Bid/Ask). `Level` = 0-based depth position (0 = top of book for that side).
- `Operation` in {Add, Update, Remove} -- price-level operations, not order-level (MBP, not MBO).
- `MarketMaker` is whatever the feed supplies (commonly empty for CME futures aggregated depth).
- `IsReset` is NinjaTrader's own book-reset flag -- the strongest native gap/restart signal available.
- No order ID, no queue-rank/priority field exists in the source API -- neither is fabricated here.

## `<prefix>_topofbook.csv`  (synchronized Last/Bid/Ask, for DOM/FLOW/AUCTION alignment)
`RunId,SeqLocal,RecordedUtc,EventTime,EventTimeKind,Type,Price,Size`
- `Type` in {Bid, Ask, Last}.

## `<prefix>_events.csv`  (low-frequency: state transitions, connection status, caps, fatal errors)
`RunId,SeqLocal,RecordedUtc,Category,Detail`
- `Category` in {STATE_TRANSITION, CONNECTION_STATUS, CAP_REACHED, FATAL_ERROR, WARN}.
- This is the primary gap-detection / restart-marker stream: a genuine connection drop, a
  DataLoaded->Realtime transition, or a Terminated shutdown all show up here.

## `<prefix>_heartbeat.csv`  (liveness beacon, independent of market activity)
`RunId,SeqLocal,RecordedUtc,BarTime,DepthRowsWritten,TopOfBookRowsWritten,SecondsSinceLastDepthEvent,SecondsSinceLastTobEvent`
- Written once per `HeartbeatEveryNBars` bar closes of whatever bar period the chart uses.
- Lets a downstream consumer tell "collector alive, market just quiet" apart from "collector died".

## Disclosed limitations (see REPORT.md for full rationale)
1. MBP depth, not MBO -- no per-order IDs, no order-level granularity.
2. No queue priority -- not exposed by NinjaScript's standard OnMarketDepth API.
3. `SeqLocal` is a collector-local monotonic counter, not an exchange sequence number.
4. Depth entitlement on whatever connection is used is unconfirmed at the platform level;
   `DataConnectionDisableL2Data` in the manifest is a direct queryable signal, not a substitute
   for a real License Manager / data-plan check.
5. `EventTime` timezone semantics for the live `OnMarketDepth`/`OnMarketData` callback path were
   NOT independently verified this pass (only the historical "Simulation" connection was
   available, and it does not deliver depth at all per the DOM01 finding). `EventTimeKind`
   records `DateTime.Kind` as delivered so this can be diagnosed on first live/replay attach.
