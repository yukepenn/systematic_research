# DOM01 QC monitor

`dom01_qc_monitor.py` — the minimum robust health/QC monitor for DOM01 collection,
built 2026-08-11 per owner directive. **ENGINEERING ONLY.** It checks whether the feed
and collector are working correctly; it does not look at whether the data predicts
anything. See the module docstring for the exact scope boundary (data/feed integrity
only — never future returns, markouts, PnL, or any outcome/predictive computation).

## Run it

```
python runs/DOM01_LIQUIDITY_STATE/collector/qc/dom01_qc_monitor.py
```

Defaults to `--out-dir runs/DOM01_LIQUIDITY_STATE/collector/out` (the live collector
output) and writes one JSON + one Markdown report per discovered run, plus a cross-run
rollup, to `--report-dir runs/DOM01_LIQUIDITY_STATE/collector/qc/reports` (default).
Read-only against `out/` — safe to run repeatedly against an in-progress run, including
while the collector is still writing.

Exit code 0 = no FAIL-level check across any discovered run. Exit code 1 = at least one
FAIL somewhere (see the printed per-run verdict line and the Markdown report for detail).

## What it checks (and what it deliberately doesn't)

File/session presence, first/last timestamps, `RecordedUtc`/`SeqLocal` monotonicity and
duplicates, malformed CSV rows (stdlib `csv` structural pass, independent of pandas'
more forgiving parser), impossible/negative sizes, depth-level validity, crossed/locked
top-of-book incidence, heartbeat cadence and `SecondsSinceLast{Depth,Tob}Event` gaps,
manifest/schema-version consistency, connection status
(`DataConnectionDisableL2Data`/`DataConnectionStatusAtInit`), contract identity/rollover
across runs, and `FileChecksumsSha256` verification once a run reaches `State.Terminated`.

It also surfaces (as an `INFO`-level, explicitly-hedged finding, never asserted as fact)
the empirical `RecordedUtc` − `EventTime` offset, since `EventTimeKind` is `Unspecified`
in the manifest and `SCHEMA.md` already discloses this as unverified — see
`depth:eventtime_semantics` in any report. This is a feed-semantics integrity check, not
an interpretation of what the data means.

`events:cap_reached_rows` checks for `CAP_REACHED` rows in `_events.csv` specifically
because the manifest's own `CapReached` field is written once at `State.DataLoaded` and
not rewritten until `State.Terminated` (confirmed by reading
`ninjascript/Dom01DepthRecorder_v1.cs`) — for an in-progress run, `events.csv` is the
*only* live signal that a stream has silently started dropping rows.

## `dom01_storage_monitor.py` — disk capacity, separate concern from data QC

```
python runs/DOM01_LIQUIDITY_STATE/collector/qc/dom01_storage_monitor.py
```

Per-run file sizes, realized bytes/hour since `StartUtc`, a coarse projected GB for one
full 23h session at that rate, row counts vs. `MaxRowsPerStreamFile` (read from
`_heartbeat.csv`'s own last row, not by scanning `_depth.csv`), free disk space on the
drive hosting `out/`, and a WARN/FAIL alert on projected days-until-full (defaults: WARN
<30 days or <50 GiB free, FAIL <7 days or <15 GiB free — override with `--warn-days`
etc.). Also lists `Terminated` runs as compression candidates with the verified-safe
procedure (see below). Same non-outcome scope discipline as the QC monitor — bytes and
row counts only, never anything about what the data says about the market.

It computes zero of: future returns, markouts, PnL, predictive correlations, alpha by
DOM state, conditional price response, or candidate performance. If a future
predictive/outcome analysis is wanted, that is a separate, separately-preregistered
question — see `research/data_forward_sealed/DOM01/DOM01_PROSPECTIVE_PROTOCOL.md`.

## `reports/` is not committed

Reports are regenerated from the live, uncommitted `out/` directory (itself
deliberately untracked while collection is in progress — see
`research/data_forward_sealed/DOM01/README.md`'s governance rule). A committed report
would go stale within minutes of a still-running collector, so `qc/reports/` is treated
the same way as `collector/out/`: reproducible from the script, not committed as
evidence. Re-run the script to get a current read.

## File rotation — verified, not assumed

**The collector does NOT rotate files per CME trading session.** One file set (5 files,
one `RunId`) is opened per `State.DataLoaded` event and stays open until
`State.Terminated` — i.e. one chart-attach lifecycle, which can span many trading
sessions if the indicator/chart is never detached and NT8 never restarts. Confirmed by
reading `ninjascript/Dom01DepthRecorder_v1.cs`: `InitializeRun()` (creates the 5
`StreamWriter`s) fires only at `State.DataLoaded`; there is no session-boundary check
anywhere in the file. The only two things that end a run are (a) `State.Terminated`
(chart/indicator removed, NT8 shutdown, or a connection-loss termination), or (b) each
stream independently hitting `MaxRowsPerStreamFile` (default 20,000,000 rows) — which
does **not** open a new file, it drops further rows for that stream for the rest of the
run (logged as a `CAP_REACHED` event, not silent, but still real loss if unnoticed).
Practical consequence: `_depth.csv` grows without bound across sessions unless someone
periodically restarts the collector — `dom01_storage_monitor.py` is how you'd notice
before that becomes a disk or row-cap problem.

## Compression — verified safe, with one hard rule

Gzip round-trip was tested this session against a real `_topofbook.csv` sample:
sha256-identical before compression and after a full compress/decompress cycle (11.76x
smaller, 91.5% size reduction — CSV of repetitive numeric/text fields compresses very
well). Lossless and reversible, confirmed empirically, not just assumed from gzip's
general reputation.

**Hard rule: only compress a run after its manifest shows `EndUtc` is set
(`State.Terminated`).** An in-progress run's `StreamWriter` still owns an open file
handle on that exact path — compressing (or otherwise touching) a file NT8 is actively
appending to risks reading a torn/incomplete state or interfering with the writer.
Verified-safe procedure for a `Terminated` run (see `dom01_storage_monitor.py`'s own
printed instructions): recompute each CSV's sha256 and confirm it matches the manifest's
`FileChecksumsSha256` *before* compressing; `gzip -k` (keep original) each CSV;
decompress to a temp path and recompute sha256 again to confirm the round-trip is still
identical; only then delete the uncompressed original. This changes storage bytes, never
the logical content — the manifest's existing checksums remain the provenance record and
verify against the decompressed output at every step.

## Suggested cadence

Run this at least once per collection session before treating any of that session's
data as a "QC-passed independent session" for the purposes of
`DOM01_PROSPECTIVE_PROTOCOL.md`'s readiness rule. A `FAIL` verdict on a run means that
run's data does not count toward the readiness threshold until the cause is understood
and, if it's a parser/collector defect (not a market fact), fixed per the engineering
correction discipline in `CLAUDE.md` (never redesign the hypothesis in response to an
observed market outcome — only fix genuine parsing/engineering defects).
