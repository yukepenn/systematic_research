# NinjaScript naming & lifecycle convention

_Written 2026-08-09, after a Strategy Analyzer "Add Strategy" list cleanup. Governs everything
under `src/ninjascript/` and the live NT8 `Documents\NinjaTrader 8\bin\Custom\Strategies\`
folder going forward._

## Why this exists

By 2026-08-09 the live NT8 Strategies folder held 30 files — 5 are NT8's own stock samples,
25 were ours, and roughly half of those 25 were dead: superseded iterations, single-use null
controls, or bugged predecessors of a file sitting right next to them. Nothing was lost (every
non-trivial one was already git-committed evidence), but finding "the current one" meant reading
mtimes and cross-checking docs. This file exists so that stops happening again.

## Naming pattern

`<Lineage><Role>_v<N>` or `<Lineage><Role>_Final`, e.g. `SolarWaveOneContractNQ_Final`,
`SWScalpTickExport_v3`.

- **Lineage**: which campaign/product this belongs to — `SolarWave` (core signal / campaign #1
  math), `SolarWaveSM`/`SolarWaveE10`/`SolarWaveOneContract` (SYSTEM_MASTER campaign #3
  products), `SW` (Scalping Lab campaign #4 utilities), `BarExport`/`AuditBarExport` (cross-
  campaign export tools — no trading logic, name them for what they export, not which wave asked
  for them).
- **Role**: what it does — `Master` (portfolio/consolidated), `OneLot`/`OneContract` (single-
  contract sizing — these two words now mean the same thing in this repo, see below),
  `LedgerV*` (comparison/verification harness), `Export`/`Probe` (data tools, never place
  orders), `RandomEntry`/`*Control*` (null-control instrumentation).
- **Suffix**: `_v1`, `_v2`, ... while iterating (HOT-RELOAD forces this — NT8 can resolve a
  stale compiled type under an unchanged class name). Reserve **`_Final`** exclusively for a
  file that has passed a real Strategy Analyzer parity check against its Python reference and is
  the actual shipped deliverable — never use `_Final` on a research iteration.

## Lineage note: "OneLot" vs "OneContract" are the same concept

`SolarWaveSMOneLot_v1` (SM14, the original one-contract hysteresis policy, independently
parity-certified) and `SolarWaveOneContractNQ_Final` / `SolarWaveOneContractMNQ_Final` (Product
B's packaged, instrument-guarded refactor of the same policy) are **the same underlying rule**,
named with two different English words for "single contract" because they were written in
different waves. Both are kept under their own certified names rather than renamed to match —
renaming a file that has already passed Analyzer parity under a specific class name would
invalidate that certification's paper trail for zero behavioral benefit. New work should say
"one-contract" and use the `OneContract` stem; `OneLot` is legacy spelling, not wrong, just not
to be used for anything new.

## Lifecycle rule (new)

1. Any strategy actually used to produce evidence cited in a committed report **must** have its
   `.cs` committed to `src/ninjascript/` under its exact live class name — no more silent gaps
   like `BarExportV1` (used for the Product B MNQ export, only committed retroactively
   2026-08-09).
2. Once a superseded iteration's replacement exists AND is git-committed AND no queued task
   depends on the old one, delete the **live NT8 copy** (not the git history — git keeps it
   forever regardless). Don't let the live folder accumulate an unbounded version tail.
3. Before deleting a live copy, confirm: (a) it's git-tracked or truly disposable scratch, (b) no
   `NEXT_HANDOFF.md` / `CURRENT_TRUTH.md` / campaign queue entry names it as a pending
   dependency (e.g. `SWScalpTickExport_v3`'s deferred re-export blocked `v1`/`v2` from deletion
   until `v3` existed and was confirmed bug-fixed).
4. Deleting a live `.cs` file does not remove it from NT8's already-compiled
   `NinjaTrader.Custom.dll` — a NinjaScript Editor recompile or NT8 restart is still needed
   before it disappears from the Strategy Analyzer "Add Strategy" list (same hot-reload
   limitation as building new strategies).

## 2026-08-09 cleanup record

**Kept — current/final deliverables:** `SolarWaveOneContractNQ_Final`,
`SolarWaveOneContractMNQ_Final`, `SolarWaveSMMaster_v2`, `SolarWaveSMOneLot_v1`,
`SolarWaveE10Master_v2`.

**Kept — frozen/pinned by name in governing docs, never delete:** `SolarWaveRKReplicaV0` (the
CLAUDE.md frozen baseline itself), `SolarWaveOpenV3` (the only source of every published R5
figure).

**Kept — pending task dependency:** `SWScalpTickExport_v3` (2026-08-08's commit explicitly
deferred an `s20251117` re-export to "next natural restart" — not done yet).

**Kept — NT8 stock samples, not ours, one is load-bearing:** `@SampleAtmStrategy`,
`@SampleMultiInstrument`, `@SampleMultiTimeFrame`, `@Strategy`, and `@SampleMACrossOver`
specifically — CrossTrade's own `RunStrategyBacktest` tool uses it as its internal parity
self-test reference; deleting it could break the MCP tool, not just clutter.

**Kept, lower confidence, left alone rather than guessed at:** `SolarWaveRKLedgerV2` (latest of
its verification-harness lineage, possible future regression-check value), `SWMinuteExport_v1`
(possible ongoing 1-minute-substrate utility — Wave-12's `SMV2AF` used a "native 1-minute
2006-2021 substrate" whose export tool wasn't identified with certainty), `SWScalpDataProbe_v1`
(Scalping Lab is dormant, not closed — could resume).

**Deleted (superseded, git-archived or disposable scratch, zero ongoing dependency — see this
file's own commit for the exact list and each one's one-line reason):** `SolarWaveE10Master_v1`,
`SolarWaveOpenV1`, `SolarWaveOpenV1X`, `SolarWaveOpenX2`, `SolarWaveOpenV4`, `SolarWaveRK1`,
`SolarWaveRKLedgerV1`, `SolarWaveSleeveV1`, `SolarWaveSMMaster_v1`, `SolarWaveStopExecV1`,
`SW01bRandomEntryV1`, `SWScalpTickExport_v1`, `SWScalpTickExport_v2`.

**Provenance gap fixed:** `BarExportV1` existed live since 2026-08-06/07 and was used to produce
committed evidence (`runs/PRODUCTB_ONECONTRACT_FINAL/out/mnq_3m_raw.csv`) without ever being
committed itself — added to `src/ninjascript/` this pass. It is a different tool from the
already-committed `AuditBarExport1` (audit-campaign-specific, different output columns), not a
duplicate of it — both are kept.
