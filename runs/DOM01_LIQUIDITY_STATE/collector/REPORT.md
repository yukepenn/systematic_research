
# DOM01 forward-collection infrastructure — BUILT, compile-verified, not yet running

**Scope**: build the *forward* (prospective) Level-II collection path that
`runs/DOM01_LIQUIDITY_STATE/REPORT.md` (the existing DATA_LIMITED finding) explicitly deferred.
That finding stands unchanged: there is no historical Level-II data anywhere on this machine and
none can be recovered. This pass does not touch that conclusion — it builds the logger the prior
pass scoped but did not write.

**RESEARCH-ONLY.** Nothing in this pass placed, modified, or cancelled an order; nothing enabled
live trading; nothing connected a recorder to a live order strategy; the recorder was never
attached to a chart, never started, never given an account.

## Step 1 — audit of what's actually available

**crosstrade MCP tools: available.** Loaded via `ToolSearch`, called read-only.

`GetConnections(refresh=true)` (verbatim, `runs/DOM01_LIQUIDITY_STATE/collector/compile_evidence.json` step1):

| Connection | Provider | Status | PriceStatus |
|---|---|---|---|
| Kinetick – End Of Day (Free) | Provider7 | Disconnected | Disconnected |
| Live | Unknown | Disconnected | Disconnected |
| Playback | Playback | Disconnected | Disconnected |
| Simulated Data Feed | Simulator | Disconnected | Disconnected |
| **Simulation** | Provider31 | **Connected** | **Connected** |

Only "Simulation" is connected (user `rainazur`, established 2026-08-09T21:06:24Z). This is the
same historical-replay connection DOM01/DATA02 already established supplies **top-of-book only**
— never multi-level depth. No live feed is connected. This is a plain restatement of what the
tool returned, not an inference.

**Existing NinjaScript inventory** (`Grep` over `src/ninjascript/` and
`research/scalping_lab/src/ninjascript/` for `MarketDepth|OnMarketDepth|Level2|Level II|DOM|SuperDom`):
zero existing depth-related indicators or strategies. Nothing to duplicate; this is genuinely new
infrastructure.

**NT8 API surface, confirmed by reflection against this exact install (not assumed from training
data)** — `LookupNinjaScriptSymbol` / `SearchNinjaScriptSymbols` against the live NT8 8.1.8.1
AppDomain (crosstrade add-on v1.13.9):

- `OnMarketDepth(MarketDepthEventArgs)` and `OnMarketData(MarketDataEventArgs)` are both defined
  on `NinjaTrader.NinjaScript.IndicatorBase` (and `StrategyBase`) — an **Indicator** can receive
  market depth exactly like a Strategy can, with no order-management surface attached to it.
- `NinjaTrader.Data.MarketDepthEventArgs` properties (the complete set, by reflection):
  `Instrument, IsReset, MarketDataType, MarketMaker, Operation, Position, Price, Time, Volume`.
  **There is no order-ID field and no queue-rank/priority field.** This is the structural proof,
  not an assumption, that the standard NinjaScript depth feed is **MBP (price-level aggregated
  depth), not MBO**, and that **queue priority is not available** — both are disclosed explicitly
  in the schema below, not silently omitted.
- `NinjaTrader.Cbi.Operation` enum = `{Add, Update, Remove}` — again, price-level operations, not
  order-level (confirms MBP semantics).
- `NinjaTrader.Cbi.ConnectOptions.DisableL2Data` (bool) exists and is directly queryable per
  connection — the collector reads this automatically at attach time and writes it to its
  manifest, giving a concrete, no-extra-effort signal on the depth-entitlement question the prior
  DOM01 pass flagged as unconfirmed (it is *not* a substitute for a real License Manager check,
  and is disclosed as such).
- Version-specific caveat worth noting explicitly: subscribing to `OnMarketDepth` requires no
  separate manual subscription call in NinjaScript — NinjaTrader auto-subscribes the primary
  instrument to depth once a script overriding that method reaches `State.Realtime`, *provided*
  the connected feed actually serves Level II for that instrument. That "provided" clause is
  exactly DOM01's still-open entitlement question; this pass cannot resolve it without a real
  live/replay attach, which is out of scope here (see Step 4).

## Step 2 — what was built

`runs/DOM01_LIQUIDITY_STATE/collector/ninjascript/Dom01DepthRecorder_v1.cs` (503 lines) — a
NinjaScript **Indicator** (deliberately not a Strategy: the order-management method surface
`EnterLong/EnterShort/ExitLong/ExitShort/SetStopLoss/SetProfitTarget/SubmitOrderUnmanaged` etc.
does not exist at all on the `Indicator` base class — this is a structural guarantee, not just a
coding discipline). Verified by `Grep` for all of those method names plus
`CancelOrder|ChangeOrder|Account.|GetAccount`: zero real matches, only the disclaimer comment
block that lists them.

It overrides four NinjaScript event handlers and writes append-only CSV/JSON evidence to disk:

- `OnMarketDepth(MarketDepthEventArgs e)` → depth stream (the DOM01 payload)
- `OnMarketData(MarketDataEventArgs e)` → synchronized top-of-book Last/Bid/Ask (so future
  DOM/FLOW/AUCTION work can align against it, per the task spec)
- `OnConnectionStatusUpdate(ConnectionStatusEventArgs e)` → connection-identity / gap-boundary log
- `OnBarUpdate()` → a periodic heartbeat beacon, independent of market activity

### File layout (5 files per collector run — one run = one `State.DataLoaded → State.Terminated`
lifecycle, i.e. one chart attach)

All under `ExportDir` (default `runs/DOM01_LIQUIDITY_STATE/collector/out`), sharing one prefix
`{Tag}_{StartUtc:yyyyMMdd_HHmmss}_{RunId[0:8]}`:

| File | Content | Columns |
|---|---|---|
| `..._manifest.json` | Run-level metadata, written at start, finalized at end | SchemaVersion, RunId, StartUtc/EndUtc, InstrumentFullName/Root, ContractExpiry, Exchange, TradingHoursTemplateName/TimeZoneDisplayName, MachineLocalTimeZoneId, DataConnectionTypeName/OptionsTypeName/DisableL2Data/StatusAtInit, DepthLevelClass, SequenceFieldNote, EventTimeSemanticsNote, KnownLimitations[], and at Terminated: FinalCounts, CapReached, FatalErrorOccurred, **FileChecksumsSha256** |
| `..._depth.csv` | MBP depth events — the primary DOM01 stream | `RunId,SeqLocal,RecordedUtc,EventTime,EventTimeKind,Side,Level,Price,Size,Operation,MarketMaker,IsReset,IsTopOfBook` |
| `..._topofbook.csv` | Synchronized Last/Bid/Ask | `RunId,SeqLocal,RecordedUtc,EventTime,EventTimeKind,Type,Price,Size` |
| `..._events.csv` | State transitions, connection status changes, cap-reached, fatal errors — **the gap-detection / restart-marker stream** | `RunId,SeqLocal,RecordedUtc,Category,Detail` |
| `..._heartbeat.csv` | Liveness beacon, one row per `HeartbeatEveryNBars` bar closes | `RunId,SeqLocal,RecordedUtc,BarTime,DepthRowsWritten,TopOfBookRowsWritten,SecondsSinceLastDepthEvent,SecondsSinceLastTobEvent` |

Full column-level reference: `runs/DOM01_LIQUIDITY_STATE/collector/SCHEMA.md`.

### Addressing each addendum sec28 field explicitly

| Requested | Where |
|---|---|
| Timestamp, exchange/local if available | `EventTime` = `e.Time` verbatim + `EventTimeKind` (`DateTime.Kind`) for diagnosis, plus `RecordedUtc` = collector wall-clock UTC on every row (see timezone caveat below) |
| Instrument, contract month | `InstrumentFullName`, `InstrumentRoot`, `ContractExpiry` in the manifest |
| Bid/ask side, depth level | `Side` (Bid/Ask), `Level` (0-based `Position`) |
| Price, size | `Price` (`.ToString("R")`, full round-trip precision), `Size` |
| Operation type | `Operation` ∈ {Add, Update, Remove} — this is the complete set the API exposes |
| Sequence/order metadata where available | `SeqLocal` — disclosed explicitly as collector-local, **not** an exchange sequence number (none is exposed) |
| Top-of-book state | `IsTopOfBook` flag on every depth row (`Level==0`), plus the whole separate `_topofbook.csv` stream |
| Session identifier | Deliberately **not** included as a derived column this pass — see "what was intentionally left out" below |
| Schema version | `SchemaVersion` in every manifest |
| Data-source identity | `DataConnectionTypeName`/`DataConnectionOptionsTypeName` (via `Instrument.GetMarketDataConnection()`, reflection-confirmed) |
| Connection identity | Same, refreshed live on every `OnConnectionStatusUpdate` into `_events.csv` |
| Timezone | `MachineLocalTimeZoneId`, `TradingHoursTimeZoneDisplayName` (the instrument's configured session-template timezone, read via `TradingHours.TimeZoneDisplayName`, not guessed) |
| Gap detection | `IsReset` (native NT8 book-reset flag) per depth row, connection-status transitions, and the heartbeat's `SecondsSinceLastDepthEvent` |
| Restart markers | New file-prefix per run (new `RunId`, new `StartUtc`) is itself the restart marker; `STATE_TRANSITION` rows in `_events.csv` at DataLoaded/Realtime/Terminated |
| Checksums | SHA-256 of all 4 CSVs, computed at `State.Terminated`, written into the final manifest |

### What was intentionally left out, and why (honesty over false precision)

**No derived `SessionId` column.** The addendum asks for a session identifier; a naive one is easy
to compute (this repo's own convention: CME/Globex sessions run 18:00→17:00 ET, so "if ET
hour≥18, roll to next calendar date"). The problem: I could not verify this pass whether
`MarketDepthEventArgs.Time`/`MarketDataEventArgs.Time` for the **live** callback path is delivered
already in exchange/session time, in UTC, or in machine-local time — only the historical
"Simulation" connection was available to test against, and per the pre-existing DOM01 finding it
delivers no depth at all, so there was no live event to inspect. Baking in a wrong timezone
assumption as a first-class schema column would be exactly the kind of unsupported hand arithmetic
this campaign's own discipline forbids in canonical evidence. Instead: `EventTime` is logged
**verbatim**, `EventTimeKind` records `.Kind` for diagnosis, and `EventTimeSemanticsNote` in the
manifest tells the owner exactly how to check it on first live/replay attach (compare `EventTime`
to `RecordedUtc` for the first few rows — near-zero offset means UTC/local delivery, an offset
matching the session template's UTC offset means exchange-local delivery). A session ID can be
computed downstream in one line once this is confirmed, correctly, rather than shipped now,
possibly wrong, inside the recorder itself.

**No queue priority, no MBO.** Per task instruction, not claimed because the API does not expose
it — confirmed by reflection (`MarketDepthEventArgs`'s full property list, above), not by
recollection.

## Step 3 — compile result

1. **In-memory compile** (`CompileNinjaScript(in_memory=true)`, job `239b8afff5884f1b`, against the
   live NT8 8.1.8.1 AppDomain via crosstrade add-on v1.13.9, 133 referenced assemblies):
   **`compiled: true`, `errors: []`, `warnings: []`.** Clean.
2. **Written into NT8's real NinjaScript source folder**
   (`WriteNinjaScriptFile(kind="indicator", name="Dom01DepthRecorder_v1", overwrite=true,
   trigger_compile=true)`) →
   `C:\Users\Yuke Zhang\Documents\NinjaTrader 8\bin\Custom\Indicators\Dom01DepthRecorder_v1.cs`
   (confirmed present via `ListNinjaScriptFiles`, 24,917 bytes, byte-identical to the repo copy
   modulo a UTF-8 BOM the write tool adds — verified with `diff` after stripping CR).
3. **`compile_engine: "file_only"`.** The reflection-based auto-recompile trigger was unavailable
   this call — per the tool's own documentation this is "an expected fallback, not an error": the
   file is on disk and syntax-verified (step 1), but NT8 has **not yet rebuilt
   `NinjaTrader.Custom.dll`** against it through its own native path. **This is the one
   prerequisite owner action, described exactly in Step 4.**

The indicator was never attached to a chart, never started, never given an account, never
connected to anything — compile/build verification only, exactly as scoped.

Full machine-readable evidence (raw tool args/responses, reproduce steps):
`runs/DOM01_LIQUIDITY_STATE/collector/compile_evidence.json`.

**Reproduce this pass:**
```
mcp__crosstrade__GetConnections(refresh=true)
mcp__crosstrade__CompileNinjaScript(in_memory=true, name="Dom01DepthRecorder_v1", source=<contents of ninjascript/Dom01DepthRecorder_v1.cs>)
mcp__crosstrade__GetMcpJob(job_id=<returned job_id>)
mcp__crosstrade__WriteNinjaScriptFile(kind="indicator", name="Dom01DepthRecorder_v1", overwrite=true, trigger_compile=true, source=<same source>)
mcp__crosstrade__ListNinjaScriptFiles(kind="indicator", filter="Dom01")
```

## Step 4 — the single owner action required to actually begin collection

Nothing further was done automatically, per instructions: attaching this to a running chart is a
live-adjacent UI action, and this pass does not perform it. In order, under 5 minutes:

1. **Compile it into NT8 for real.** In NinjaTrader 8: **Tools → Edit NinjaScript → Indicator**
   (or open the NinjaScript Editor), find `Dom01DepthRecorder_v1`, press **F5** (or just restart
   NT8 — either rebuilds `NinjaTrader.Custom.dll`). Confirm the Output window shows 0 errors (it
   should — the in-memory compile above already validated the exact same source against this
   install).
2. **Pick/confirm a data connection that actually serves Level II depth for NQ.** Per the existing
   DOM01 finding, "Simulation" (the only currently-connected feed) does **not** — it is
   historical/top-of-book replay only. This step is squarely the open item DOM01 already flagged:
   confirm in NinjaTrader's **Connections → Connection Guide / License Manager** (or whatever the
   live/data-vendor connection is) that Level II / Order Flow depth is actually included in the
   current plan, **then connect it**. (`ConnectOptions.DisableL2Data`, if `true` once connected,
   is now automatically captured in the manifest on first attach — a quick post-hoc sanity check,
   not a substitute for checking the plan itself first.)
3. **Open an NQ chart** on that connection (any bar type/period works — `OnMarketDepth`/
   `OnMarketData` fire independently of `Calculate`/bar period; a period like 1-minute or lower is
   recommended only so the heartbeat beacon in Step 2's design has a meaningful cadence).
4. **Add the indicator**: right-click the chart → Indicators → find `Dom01DepthRecorder_v1` → Add.
   Defaults are pre-set (`ExportDir` points at
   `runs/DOM01_LIQUIDITY_STATE/collector/out`, `Tag = "dom01"`) — no parameters need to be changed
   to start. Click OK.
5. **Confirm it's running**: within a few seconds a new `dom01_<timestamp>_<runid>_manifest.json`
   plus 4 CSVs should appear in `runs/DOM01_LIQUIDITY_STATE/collector/out/`. Check
   `DataConnectionDisableL2Data` and `DataConnectionStatusAtInit` in the manifest, and watch
   `_depth.csv` for rows — if it stays empty while `_heartbeat.csv` grows, that is the direct
   signature of "collector alive, feed not serving depth" (i.e., the Step 4.2 entitlement question
   resolved negatively), not a bug in this file.

**No indicator plot/visual output is expected** — this is a pure logger by design; an empty-looking
chart pane after adding it is correct behavior, not a sign of failure.

## Safety statement

No order was placed, modified, or cancelled. No strategy was enabled or deployed. Sim101/real
accounts were never touched. No connection, credential, or licensing setting was altered. The
licensed RenkoKings vendor assembly was not touched. The indicator was never attached to a chart,
never started, and is not connected to anything as of the end of this pass — it exists only as
compiled-verifiable source on disk, in both the repo (version-controlled evidence) and NT8's own
NinjaScript folder (build target), per Step 3's exact compile record above.

## Files delivered

- `runs/DOM01_LIQUIDITY_STATE/collector/ninjascript/Dom01DepthRecorder_v1.cs` — the recorder source (canonical, checked into the repo)
- `runs/DOM01_LIQUIDITY_STATE/collector/SCHEMA.md` — column-level schema reference
- `runs/DOM01_LIQUIDITY_STATE/collector/compile_evidence.json` — machine-readable compile/reflection evidence + reproduce steps
- `C:\Users\Yuke Zhang\Documents\NinjaTrader 8\bin\Custom\Indicators\Dom01DepthRecorder_v1.cs` — the build target inside the live NT8 install (byte-identical to the repo copy, modulo BOM)
