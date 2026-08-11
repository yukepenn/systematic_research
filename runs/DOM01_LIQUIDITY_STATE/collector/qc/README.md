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

## Suggested cadence

Run this at least once per collection session before treating any of that session's
data as a "QC-passed independent session" for the purposes of
`DOM01_PROSPECTIVE_PROTOCOL.md`'s readiness rule. A `FAIL` verdict on a run means that
run's data does not count toward the readiness threshold until the cause is understood
and, if it's a parser/collector defect (not a market fact), fixed per the engineering
correction discipline in `CLAUDE.md` (never redesign the hypothesis in response to an
observed market outcome — only fix genuine parsing/engineering defects).
