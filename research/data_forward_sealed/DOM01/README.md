# DOM01 forward-data vault — SEALED, receiving data as of 2026-08-11

**UPDATE 2026-08-11: collection is live** (`runs/DOM01_LIQUIDITY_STATE/collector/out/`, one run
in progress). Before any of it is read for research, see the two governance documents this update
adds:

- `DOM01_PROSPECTIVE_PROTOCOL.md` — the one frozen DOM mechanism (DOM-M1, opposite-side depth
  withdrawal), full preregistration template, feed-semantics verification. No outcome analysis has
  happened under it yet.
- `DOM01_DATA_GOVERNANCE.md` — chronological data states (`ENGINEERING_BURNIN` ->
  `SEALED_FORWARD` -> `PROSPECTIVE_DISCOVERY`/`PROTECTED_CONFIRMATION`), the readiness rule (QC
  completion + structural incidence only, never observed effect size), and why reaching readiness
  does not itself authorize a read.
- QC monitor: `runs/DOM01_LIQUIDITY_STATE/collector/qc/dom01_qc_monitor.py` — run this against any
  batch before it can even be proposed for promotion.

Everything below this line predates live collection and is retained for history.

---

**Status as of 2026-08-10 (superseded above): this directory is empty and no collector has ever
run.** It is created now, ahead of collection start, purely to fix the destination path, schema
contract, and governance rule before any bytes land here. See
`runs/DOM01_LIQUIDITY_STATE/collector/REPORT.md` and
`runs/DOM01_LIQUIDITY_STATE/collector/DOM01_START_INSTRUCTIONS.md` for the collector build state
and the exact remaining owner steps to start it.

## What this vault is for

Once an owner completes the manual start steps, `Dom01DepthRecorder_v1` (or whatever compiled
version succeeds it — rename-on-recompile per this repo's hot-reload convention, e.g. `_v2`,
`_v3`) will write its live output to
`runs/DOM01_LIQUIDITY_STATE/collector/out/`. This vault directory
(`research/data_forward_sealed/DOM01/`) is the intended longer-term **cold storage / sealed
archive** location: completed collector-run file sets (5 files per run: manifest + depth +
topofbook + events + heartbeat) get moved or copied here once a run is finalized
(`State.Terminated`, manifest has `FinalCounts`/`FileChecksumsSha256` populated), to keep the
live/working collector output directory separate from the durable, checksum-verified archive.

## Governance rule — read before touching anything in this directory

**Collection is not research consumption.** Data landing in this vault is raw forward-collected
Level-II/top-of-book evidence only. It must **NOT** be opened, loaded, or read for alpha research,
hypothesis testing, or any Auction/DOM/FLOW analysis until:

1. A completeness/integrity audit (per the conventions below) has been run and passed for the
   date range in question, and
2. The data has been formally promoted into a numbered run directory under `runs/` with its own
   `spec.yaml` written and committed **before** results are read, per this repo's standard
   workflow (`CLAUDE.md` → Workflow section), and
3. Any promotion is logged in `research/registry/experiments.yaml` and reflected in
   `research/CAMPAIGN_STATE.md` / `research/frontier.yaml`, same as every other tested config.

Treat this directory the same way the campaign already treats forward-locked data: **arriving
here is not the same event as being cleared for use.** Do not glob, grep, or read files under this
directory as an input to any research script or notebook until the promotion step above has
happened. This mirrors the existing rule elsewhere in this campaign that already-collected-but-
not-yet-cleared data (e.g. forward-locked seals, protected confirmation pools) is read-only-by-
audit, not read-for-alpha, until explicitly released.

## Schema version and instrument/contract

- **Schema version**: `dom01-collector-schema-v1` (see `SchemaVersion` field written into every
  run's `_manifest.json`; full column reference in
  `runs/DOM01_LIQUIDITY_STATE/collector/SCHEMA.md`). Any future schema change gets a new version
  string, not a silent field change — check `SchemaVersion` on every file before assuming column
  layout.
- **Instrument**: NQ (Nasdaq-100 E-mini futures). The specific front-month contract in force at
  collection time is recorded per-run in the manifest (`InstrumentFullName`, `InstrumentRoot`,
  `ContractExpiry`) — it is **not** fixed at build time and will roll over a multi-month collection
  window. Do not assume a single contract code; read it from each run's manifest.
- **Data class**: MBP (market-by-price, depth-by-level), **not** MBO — no per-order IDs, no queue
  priority. This is a structural limitation of the NinjaScript `OnMarketDepth` API, confirmed by
  reflection against this exact NT8 install (see `compile_evidence.json`), not a collector bug.

## Fields that will be recorded (summary — full detail in SCHEMA.md)

Each collector run (one chart-attach lifecycle) produces 5 files sharing one prefix
`{Tag}_{StartUtc:yyyyMMdd_HHmmss}_{RunId[0:8]}`:

| File | Purpose | Key columns |
|---|---|---|
| `..._manifest.json` | Run identity, connection/instrument/timezone context, disclosed limitations, final checksums | `SchemaVersion, RunId, StartUtc/EndUtc, InstrumentFullName/Root, ContractExpiry, DataConnectionTypeName, DataConnectionDisableL2Data, KnownLimitations[], FinalCounts, FileChecksumsSha256` |
| `..._depth.csv` | MBP depth-by-price-level events — the primary DOM01 stream | `RunId, SeqLocal, RecordedUtc, EventTime, EventTimeKind, Side, Level, Price, Size, Operation, MarketMaker, IsReset, IsTopOfBook` |
| `..._topofbook.csv` | Synchronized Last/Bid/Ask, for cross-referencing against depth | `RunId, SeqLocal, RecordedUtc, EventTime, EventTimeKind, Type, Price, Size` |
| `..._events.csv` | State transitions / connection status / cap-reached / fatal errors — the gap-detection stream | `RunId, SeqLocal, RecordedUtc, Category, Detail` |
| `..._heartbeat.csv` | Liveness beacon independent of market activity | `RunId, SeqLocal, RecordedUtc, BarTime, DepthRowsWritten, TopOfBookRowsWritten, SecondsSinceLastDepthEvent, SecondsSinceLastTobEvent` |

Disclosed, structural limitations (not omissions — see `SCHEMA.md` for full rationale): MBP not
MBO; no queue priority; `SeqLocal` is collector-local, not an exchange sequence number; depth
entitlement on whatever connection is used is unconfirmed until an owner checks the data plan;
`EventTime` timezone semantics for the live callback path are unverified until first live/replay
attach (check `EventTime` vs. `RecordedUtc` on the first few rows of the first real run).

## Daily-checksum / completeness-report conventions (to follow once data starts arriving)

These conventions are not yet exercised (no data has arrived), but are fixed here in advance so
the first real day of collection already has a process to follow rather than improvising one
under time pressure:

1. **Per-run checksum is already built in.** Every finalized run's manifest carries
   `FileChecksumsSha256` for all 4 CSVs, computed by the collector itself at `State.Terminated`.
   Before trusting any archived file, recompute its SHA-256 and diff against the manifest value —
   a mismatch means the file was truncated, corrupted, or edited after the fact and must not be
   used.
2. **Daily completeness pass** (once collection is a daily-recurring activity): for each trading
   session date, enumerate all collector runs whose `StartUtc`/`EndUtc` overlap that session
   (there may be more than one, e.g. after a restart), and confirm:
   - the `_events.csv` STATE_TRANSITION rows show a clean `DataLoaded → Realtime → Terminated`
     sequence with no unexplained `FATAL_ERROR` rows, and
   - the `_heartbeat.csv` beacon cadence has no gap larger than a small, documented multiple of
     `HeartbeatEveryNBars` bars' worth of wall-clock time (a gap larger than that, with
     `_depth.csv` also silent underneath it, indicates a collector or connection outage, not just
     a quiet market), and
   - `CapReached`/`FatalErrorOccurred` in the manifest are both `false` (or, if `true`, that fact
     is carried forward explicitly rather than silently dropped).
   Write the result as a short per-day (or per-batch) completeness report next to the archived
   files — do not fold a completeness verdict into a research report without a written audit trail
   behind it, per this campaign's "every number must be reproducible from a script + output file"
   discipline (`CLAUDE.md`).
3. **Promotion, not silent consumption.** Once a date range passes the completeness pass, promote
   it into a proper `runs/<RUN_ID>/` directory with its own `spec.yaml` (per the standard workflow)
   before any research script reads it — this vault stays the sealed archive, not a working
   research input directory.

## Directory contents

Empty as of creation (2026-08-10). No collector run has ever executed; see
`runs/DOM01_LIQUIDITY_STATE/collector/DOM01_START_INSTRUCTIONS.md` for the exact remaining owner
steps.
