# DOM_PAUSE_CLEANUP_20260812

**Trigger**: a system/resource incident on 2026-08-12 during heavy DOM/Level-II/Market Replay
work; the machine became unstable and crashed, then recovered. Per owner directive, this is a
**risk-control pause**, not a finding that DOM work caused a hardware failure — the resource-heavy
workflow coincided with instability, no stronger causal claim is made anywhere in this document.

**Scope of this pass**: identify and (where safe) remove disposable DOM/Level-II capture data,
disable automatic DOM collection fail-closed, and record the pause policy. NinjaTrader was running
when this pass started (PID 28348), so nothing under NT8's own `db\` was touched — see the
NT8-open note per item below. Repo-local artifacts (not part of NT8's managed database) were
safe to act on immediately, confirmed by checking that both DOM01 collector runs had already
cleanly `Terminated` (manifest `EndUtc` set) and that NT8's restart today did not silently
reattach/resume the indicator (no third run exists).

## Classification table

| Path / Item | Type | Size | Last Modified | Action | Reason |
|---|---|---:|---|---|---|
| `runs/DOM01_LIQUIDITY_STATE/collector/ninjascript/Dom01DepthRecorder_v1.cs` | ACTIVE_COLLECTOR (source) | ~15 KB | committed | **DISABLE** | The only genuine DOM/Level-II collector anywhere in this repo. Adding a fail-closed guard (see Phase 6) so it refuses to start until explicitly re-authorized. Not deleted — it's the canonical implementation, needed if/when this is re-authorized. |
| `runs/DOM01_LIQUIDITY_STATE/collector/out/` (2 terminated runs × 5 files) | RAW_DOM_DATA | 1.4 GB | Aug 11 19:57 / Aug 12 00:29 (crash time) | **DELETE** | Raw, unpromoted Level-II capture CSVs. Both runs confirmed cleanly `Terminated` (`EndUtc` set in each manifest) — no live file handles. Never promoted past `ENGINEERING_BURNIN`/`SEALED_FORWARD` per `DOM01_DATA_GOVERNANCE.md` — explicitly disposable/re-collectable by that document's own design, not canonical evidence. Entirely within the repo filesystem, not NT8's managed `db\`. |
| `runs/DOM01_LIQUIDITY_STATE/collector/qc/reports/` | DERIVED_DOM_DATA | ~250 KB | Aug 11-12 | **DELETE** | QC/verdict reports describing the raw CSVs above; never git-committed (by design — regenerated from live data); would become stale/misleading pointers to deleted files if kept. The QC *script* that generates them is preserved (see below). |
| `runs/DOM01_LIQUIDITY_STATE/collector/qc/dom01_qc_monitor.py` | PASSIVE_RESEARCH_CODE | ~15 KB | committed | PRESERVE | Read-only inspection tool; does not collect or download anything itself. Useful again if/when collection is re-authorized. |
| `runs/DOM01_LIQUIDITY_STATE/collector/qc/dom01_storage_monitor.py` | PASSIVE_RESEARCH_CODE | ~10 KB | committed | PRESERVE | Same — read-only. |
| `runs/DATA03_HISTORICAL_MARKET_REPLAY_INVENTORY/src/data03_inventory.py` | PASSIVE_RESEARCH_CODE | ~9 KB | committed | PRESERVE | Read-only manifest generator; never triggers a download. |
| `runs/DATA03_HISTORICAL_MARKET_REPLAY_INVENTORY/{spec.yaml,REPORT.md,acquisition_plan.yaml,out/manifest.*}` | governance/evidence (not raw capture) | ~25 KB | committed | PRESERVE + AMEND | Canonical, already-committed acquisition-planning record. Amended (not deleted) with a pause notice — see Phase 8. |
| `C:\Users\Yuke Zhang\Documents\NinjaTrader 8\db\replay\NQ 09-26\20260715.nrd` | RAW_DOM_DATA (Market Replay L1+L2) | 153.5 MB | server-stamped 2026-07-16 | **AMBIGUOUS_PRESERVE** | Matches the DELETE list's "NinjaTrader Market Replay data containing Level-II event streams" by category — flagged, not silently kept. But: it is a single, deliberately-acquired proof artifact (not a bulk/disposable capture), already classified and tied to committed governance evidence (`DATA03_HISTORICAL_MARKET_REPLAY_INVENTORY`, sha256 on record), and modest in size — not the resource problem this pause addresses. Per "if ambiguous, preserve it, no destructive guessing," left in place. **Owner: say the word and I'll delete it too.** NinjaTrader was running, so this was not touched under `db\` regardless. |
| `C:\...\NinjaTrader 8\db\tick\*` (all contract folders) | ORDINARY_TICK_DATA | ~9.4 GB | various | PRESERVE | Explicit instruction: never delete `db\tick`. Ordinary L1 Bid/Ask/Last historical tick data, not full-depth DOM. |
| `C:\...\NinjaTrader 8\db\minute\`, `db\day\`, `db\cache\` | ordinary NT8 platform data | 142 MB / 1.3 MB / 348 MB | various | PRESERVE | Not DOM/depth-related. |
| `C:\...\NinjaTrader 8\db\snapshot\` | N/A (empty) | 0 bytes | — | PRESERVE (nothing present) | Confirmed empty both before and after this pass; unrelated NT8 feature, not the DOM01 collector's output. |
| `C:\...\NinjaTrader 8\log\`, `trace\`, `strategyanalyzerlogs\` | ordinary logs | 553 KB / 204 MB / 11 MB | various | PRESERVE | Not "clearly enormous/disposable"; ordinary platform operation logs. |
| `C:\...\NinjaTrader 8\out\*.csv` (ES/NQ/RTY/YM 1-minute bars, 2022-2026) | ORDINARY_TICK_DATA (bar data) | ~370 MB | Aug 8 | PRESERVE | Ordinary OHLCV bar exports for existing baseline research; predates and is unrelated to the DOM/Replay work; not DOM data by content (verified: plain OHLCV columns). |
| `research/scalping_lab/**` (all NinjaScript, `substrate/*.parquet`, `DATAPROBE01/`, `EXPORT01/`) | ORDINARY_TICK_DATA / PASSIVE_RESEARCH_CODE | several hundred MB | various, established since 2026-08 | PRESERVE | Verified directly: zero `OnMarketDepth`/`MarketDepth`/`DepthEventArgs` usage anywhere in scalping_lab's NinjaScript. All BBO/tick data (`AddDataSeries MarketDataType.Bid/Ask`), not depth. `DATAPROBE01/out_depthcheck/probe_ticks.csv`'s name refers to *diagnosing whether an L2 path was reachable* (it wasn't, via that path) — the file itself is 1-tick Bid/Ask/Last data, columns `bip,bar,time,price,volume`. Established, cited, closed research substrate (e.g. the C1=2.872-tick cost hurdle traces back to this campaign) — canonical, not disposable. |
| `research/data_forward_sealed/DOM01/{README.md,DOM01_PROSPECTIVE_PROTOCOL.md,DOM01_DATA_GOVERNANCE.md}` | governance docs | small | committed | PRESERVE + AMEND | Canonical governance record — vault itself confirmed still empty (no raw data ever promoted there). Amended with pause notice, not rewritten. |
| `research/system_master/{ACTIVE_RESEARCH_QUEUE.md,CURRENT_TRUTH.md}`, `RESEARCH_HANDOFF.md` | canonical truth docs | — | committed | PRESERVE + AMEND | Existing history untouched; pause-policy pointer appended. |
| Windows Task Scheduler | — | n/a | n/a | N/A | Checked directly (`Get-ScheduledTask` filtered for Ninja/DOM/Replay/Depth/Level2/L2) — zero matching entries exist. Nothing to disable at the OS scheduler level. |
| `C:\...\NinjaTrader 8\ninZa.co\` | third-party AddOn placeholder folder | 1.0 KB | pre-existing | PRESERVE (untouched) | Effectively empty; nothing was installed there this campaign; out of scope to modify a folder I didn't create. |

## Storage reclaimed

Deleting `runs/DOM01_LIQUIDITY_STATE/collector/out/` (1.4 GB) and
`runs/DOM01_LIQUIDITY_STATE/collector/qc/reports/` (~250 KB) frees approximately **1.4 GB** on
the D: drive (repo location). This does **not** touch the C: drive at all — `db\replay`'s 153.5 MB
proof file is preserved (see above), and `db\tick`/other NT8 data (~10 GB total) is untouched by
policy. C: drive relief, if any is still needed once NT8 is closed, would come only from the
already-preserved-by-instruction `db\tick` growth stopping going forward (collection paused), not
from deleting existing history.
