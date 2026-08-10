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
