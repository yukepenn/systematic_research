# DOM01 — Level-II liquidity state: DATA_LIMITED, no historical route, forward-collection scoped not built

**Disposition: DATA_LIMITED.** Per addendum E1: only genuine Market Replay/MBO/MBP evidence
qualifies for DOM01 — OHLCV or BBO-only proxies are explicitly invalid. DATA02's inventory
(`runs/DATA02_MICROSTRUCTURE_INVENTORY/`) confirms, independently and twice, that no such data
exists anywhere on this machine: `db/replay/` and `db/snapshot/` under the local NinjaTrader 8
installation are both empty, and NT8's own hosted historical-data servers (the "Simulation"
connection this campaign already uses for L0/L1/L2 top-of-book) supply only top-of-book Last/Bid/
Ask tick series — never multi-level book snapshots. This is a **pre-existing, already-documented
finding** (DATAPROBE01, 2026-08-07), reconfirmed here, not new information.

## Why this can't be worked around

History cannot be recovered retroactively — genuine Level-II depth was simply never recorded.
There is no vendor route through the existing NT8 install either: `bin/Custom` has no Volumetric/
Footprint chart type and no Order-Flow SuperDom columns, consistent with the platform's Order
Flow+ package (which includes a live Market Depth Map) not being licensed on this installation —
and even a licensed Market Depth Map is a **live-only** view per NinjaTrader's own documentation,
not a historical research tool. So DOM01 is blocked by both a data gap (no historical recordings)
and, for live-forward collection, an unconfirmed entitlement gap.

## Forward-collection is the only path — scoped here, not built this pass

Per addendum sec E5, the correct next step if local recording infrastructure doesn't exist is a
research-only Level-II logger (no trading decisions). This is architecturally straightforward in
principle (subscribe to market depth via a NinjaScript or CrossTrade-mediated feed, log ladder
changes to disk with a stable schema) but has two open preconditions this pass did not resolve:

1. **Entitlement is unconfirmed.** DATA02 found no evidence the Order Flow / Level-II depth
   package is currently licensed on this NT8 installation. Building a logger against a feed the
   account isn't entitled to would simply produce nothing (or requires a live broker/data-vendor
   connection — currently only a "Simulation" historical-replay connection is active, no "Live"
   feed). This needs an owner-level check (License Manager, or confirming Level-II is included in
   the current data-provider subscription) before any logger is worth writing.
2. **Scope.** A robust logger (schema, gap detection, session-completeness reporting, contract-
   roll handling, clock synchronization, reconnect handling) is a real engineering deliverable in
   its own right — per this campaign's "don't let engineering swallow research" discipline
   (directive sec87), it deserves its own dedicated, focused pass rather than being built inline
   as a sub-item of this already-large Wave-4 turn.

## Verdict

**CLOSED this pass — DATA_LIMITED, not CLOSED_INFORMATION_CLASS.** The mechanism (resting-
liquidity dynamics informing adverse-selection risk, continuation quality, entry/exit/scale
timing per addendum E4) remains a live, legitimate hypothesis — it simply has no historical
evidence to test against, and forward collection requires an entitlement check and a dedicated
build pass, both flagged here for the owner rather than assumed or silently skipped.

## RE-VERIFIED 2026-08-11 (direct filesystem forensics, after an owner Historical Data download)

Owner downloaded historical NQ data via NT8's Historical Data window (NQU6 tree showed Last/Ask/
Bid loaded; NQM6 was mid-download; the "Get Market Replay data" section was never expanded).
Direct recursive listing of `C:\Users\Yuke Zhang\Documents\NinjaTrader 8\db\replay\` and
`...\db\snapshot\` (the only two paths NT8 uses for Market Replay/depth-snapshot storage) both
returned **0 items** — unchanged from DATA02's 2026-08-09 finding. **CASE A confirmed: this
download only added/extended L1 `.ncd` Bid/Ask/Last tick files under `db\tick\`** (per-contract
folders, e.g. `NQ 09-26` now spans first=2026-06-08 01:00 through last=2026-08-11 20:00 by
filename timestamp only — filesystem metadata, never opened/parsed, per `LOCKED_FORWARD.md`;
`NQ 06-26` spans 2026-03-16 through 2026-06-12, fully inside the authorized ≤2026-07-31 window).
**No genuine historical Level-II/Market Replay data exists locally. This conclusion is
unchanged from DATA02.** `DATA03_HISTORICAL_MARKET_REPLAY_INVENTORY` is not created — its own
trigger condition (genuine L2 replay files existing for any ≤2026-07-31 date) is not met.

## MARKET REPLAY CONFIRMED AVAILABLE 2026-08-11 (dated correction, appended not rewritten)

**Correction to the "no historical Level-II route" conclusion above: it was correct at the time
strictly as a LOCAL-INVENTORY statement (`db/replay` was empty), not as a statement about NT8
server-side availability.** The owner subsequently used the previously-unexplored
`Historical Data -> Get Market Replay data` section and downloaded NQU6 2026-07-15, producing
`db\replay\NQ 09-26\20260715.nrd` (160,994,081 bytes). `db/replay` is no longer empty.

**Classification: `GENUINE_NT8_MARKET_REPLAY_L1_PLUS_L2`, acquisition proof = PASS.** Per the
owner, NinjaTrader's own documentation states Market Replay files store the synchronized Level I
+ Level II event sequence together, by design, to keep them in sync — this session's own local
structural inspection (byte-stride record counting only, no field-content decoding, per explicit
instruction not to reverse-engineer the proprietary `.nrd` format further) is consistent with,
but does not independently prove, that classification on its own; the classification rests on the
documented acquisition mechanism plus NT8's own stated file design, disclosed as such rather than
overclaimed as independently re-derived.

**DATA02's own conclusion — "no historical Level-II data exists or can be recovered
retroactively"** — is therefore superseded for the ≤2026-07-31 window specifically:
NinjaTrader's servers do retain and serve genuine Market Replay history via the documented UI
workflow, at least for 2026-07-15. `db/snapshot` remains empty (unrelated feature). Full
acquisition planning, batch-download mechanism research, and the live storage/retention findings:
`runs/DATA03_HISTORICAL_MARKET_REPLAY_INVENTORY/REPORT.md`.

**Unchanged**: entitlement/route for a *live* Level-II feed via the regular license was never in
question here — this correction is about historical Market Replay specifically, a separate NT8
feature from live Order Flow+/Market Depth Map entitlement. DOM01's own live forward collection is
untouched and continues to be the separate, `SEALED_FORWARD`-governed prospective evidence stream
— historical Replay and live DOM01 are not being mixed (see `DOM01_PROSPECTIVE_PROTOCOL.md`,
reconciliation with this new source explicitly deferred to a later step).

NT8's actual Market Replay connection type (`GetConnections`: `Playback`, provider id 13) is
currently `Disconnected` and distinct from both the regular Historical Data downloader and the
live/sim `Simulation` (Tradovate-backed) connection this campaign already uses — confirms the
UI path for genuine replay is a separate workflow the owner has not yet used, consistent with
"Get Market Replay data" being observed collapsed/unused in the screenshot.

Incidentally found while checking DOM01 was undisturbed (read-only, no action taken): the prior
collector run (`RunId 5c8ca242...`) cleanly `Terminated` at `23:57:02Z` and a fresh run
(`8c57389f...`) started half a second later — consistent with NT8 reloading NinjaScripts/charts
during the historical-data session, not anything this verification pass did. The terminated
run's manifest has one real, disclosed collector defect: `FileChecksumsSha256.events.csv` holds
a raw, JSON-unescaped `.NET` exception string ("process cannot access the file... used by
another process") instead of a checksum — a file-lock race between closing the `events.csv`
writer and hashing it at shutdown, which also makes that one manifest technically invalid JSON.
`dom01_qc_monitor.py` already catches this correctly (`FAIL`, gracefully skips the rest of that
run's manifest-dependent checks rather than crashing) — not fixed in the collector source this
pass, flagged here for a future dedicated engineering pass. `depth.csv`/`topofbook.csv`/
`heartbeat.csv` checksums for that run all wrote correctly; only `events.csv`'s was affected.
