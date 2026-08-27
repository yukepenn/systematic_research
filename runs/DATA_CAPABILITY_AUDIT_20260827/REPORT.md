# DATA CAPABILITY AUDIT — 2026-08-27

| | |
|---|---|
| **run class** | **AUDIT** — no hypothesis, no model, no promotion, nothing tuned |
| code | `src/enumerate_nt8_store.py` · `src/bbo_session_gap.py` |
| evidence | `out/capabilities.json` · `out/connections.json` · `out/instrument_matrix.csv` · `out/retention_matrix.csv` · `out/tick_session_availability.csv` · `probes/getbars_probes.csv` |
| seal | **untouched** — filenames and sizes only; every probe window ends **before 2026-08-01** |
| data acquired | **none.** No download, no purchase, no new charge |

> ### **`"NO RUNNABLE ROW REMAINS"` WAS TRUE OF LEVEL 1 AND FALSE OF LEVEL 2.**
> ### The order-flow lane **reopens at zero cost** — the data is already on this disk.
> ### **262 NQ tick sessions have been sitting in the local NT8 store, never extracted.**

---

## 1. The distinction that made this audit worth running

The closing statement of the `RR_W000`–`RR_W006` programme was:

> *"Every question this repo can answer with data it holds has been asked."*

That sentence is **true and much narrower than it sounds**. It quantifies over *materialized
substrate files*. It says nothing about what the owner's already-paid, already-connected data
sources can serve. Those are different populations, and the second was never probed.

Per directive §25 the correct hierarchy is:

| level | question | status **after** this audit |
|---|---|---|
| **1** | answerable from **materialized substrates** | **largely exhausted** — unchanged |
| **2** | answerable from **existing connected sources** | ⚠️ **NOT exhausted. The main finding below.** |
| **3** | requires **new paid data** | owner-gated — and **smaller than it was**, see §6 |
| **4** | requires **calendar time** | calendar-gated — unchanged |

## 2. What the tool surface actually is — probed, not inferred

`GetMcpCapabilities` → add-on **v1.13.9**, NT8 **8.1.8.1**, `backtest_engine.available = true`,
fingerprint `sha256:b4255f1b0dd7fba1`, optimization supported.
`McpSelfTest` → **11 pass / 0 fail / 1 skip** with an instrument; the one skip is the deep backtest,
deliberately not run here.

### ⚠️ A correction I have to make against myself

Early in this audit I wrote that `GetOrderFlow` and `GetVolumeProfile` **"do not exist."** Then
`McpSelfTest` returned:

```
{"name": "volume_profile", "status": "pass", "extra": {"poc": 29575.4}}
{"name": "order_flow",     "status": "pass", "extra": {"delta": 97211}}
```

**The add-on computes both.** They had merely *skipped* for want of an instrument argument. The
accurate claim is narrower than the one I made:

> **The add-on backend has order-flow and volume-profile capability. No callable MCP tool in this
> session exposes it.** That is a **`TOOL_LIMIT`, not a `PROVIDER_LIMIT`** — and the two have
> completely different remedies. Verified by two independent `ToolSearch` sweeps, which returned
> only order-management and strategy-lifecycle tools.

This is exactly the failure mode `CLAUDE.md` §6 warns about — *"never assert an action is
owner-only without re-probing the tool surface today"* — arrived at from the opposite direction.
I asserted absence from a *name list* rather than from a *probe*.

### `GetBars` — hard limits, server-enforced

| capability | verdict |
|---|---|
| `periodType` ∈ {day, minute, month, week, year} | **enforced.** `Tick`, `Second`, `Volumetric` all → `rpc_error: Invalid periodType` |
| historical **Bid** / **Ask** series | **impossible** — there is no `marketDataType` parameter |
| continuous `NQ ##-##` | resolves, returns **0 rows** in every window. Contract-level only |

**The only route to tick / bid / ask is NinjaScript inside the backtest engine** — where
`bars_period.market_data_type` and `period_type: "Tick"` both exist. The repo **already has that
exporter** (§4).

## 3. Instruments and retention — the multi-market universe is provider-backed

The decisive probe: **roots absent from the local store were served anyway.** `6E`, `ZC`, `ZN`,
`GC` all returned real bars with real volume (~160–250 ms, versus ~6 ms for locally cached NQ —
consistent with on-demand provider fetch).

| probe | result |
|---|---|
| daily depth | **≥ 15 years** — `ES 12-11` and `ZN 12-16` both served |
| intraday depth | **≥ 5 years** on NQ vintages; local `db/minute` NQ runs **2006-01-05 → 2026-07-31**, 6,459 sessions |
| breadth | equity index, **rates, FX, metals, agriculture** all reachable |
| negative control | `ES 12-26` in 2018 → **0 rows, correctly** — the contract did not exist. Contract semantics are sane |

**Local `db/minute` roots with real depth:** NQ 6,459 · ES 1,486 · CL 1,481 · MNQ 1,479 · RTY 1,472 ·
YM 1,458 · ZB 1,161 sessions. Everything beyond that is fetched on demand.

## 4. ⚠️ THE MAIN FINDING — the order-flow lane reopens, and it is free

`DATAGATE_ORDERFLOW_20260827` recorded **48 sessions ⇒ 71 of 2,131 P1 entries (3.3 %)**,
`UNDERPOWERED`, and `OWNER_QUEUE` OQ-5 priced the remedy as *"CrossTrade renewal + capture time —
the largest current gap."*

**That gate measured the substrate. It did not measure the disk.** The local NT8 tick store holds:

| NQ, seal excluded | sessions | |
|---|---:|---|
| `Last` present | **310** | 2025-08-10 → 2026-07-31 |
| `Bid` present | 168 | |
| `Ask` present | 168 | |
| **BBO-COMPLETE (Last+Bid+Ask)** | **168** | governs every quote-based feature |
| Last-only, no quotes | 142 | still fine for tick-rule signed flow |

**Cross-validation:** of the substrate's 48 session files, **45 are BBO-complete** in the store —
which independently reproduces `DATA_CENSUS`'s *"quotes are missing on 3 of the 48."* The
enumeration and the committed census agree without being tuned to.

### The gap, and the two lanes it splits into

| lane | now | extractable | ~300-session target |
|---|---:|---:|---|
| **signed flow** (tick rule, `Last` only) | 48 | **310** | ✅ **MEETS IT** |
| **BBO / quote** (microprice, spread, imbalance) | 45 | **168** | ❌ **still short — 3.7× better, not solved** |

> **262 NQ sessions with `Last`, and 123 BBO-complete sessions, are already on this disk and have
> never been extracted.** ES adds **103 BBO-complete** sessions for the cross-market leg.

**Do not collapse these two lanes.** The headline "310" is `Last`-only. Quoting it for a
microprice or spread-imbalance study would overstate that lane by ~1.8×. The honest statement is:
**the signed-flow question becomes answerable; the quote-imbalance question becomes better-powered
but still short of its own preregistered target.**

### Why 48 and not 310 — and why that constraint is now gone

The exporter (`SWScalpTickExport_v3.cs`) requires **one NT8 Strategy Analyzer run per session**,
driven by hand. There is no capture loop anywhere in the repo. **`RunStrategyBacktest` removes
exactly that constraint** — the same lesson as the "owner-only F5" blocker that never existed.
The bottleneck was never entitlement, provider limits, or money. **It was manual labour.**

## 5. Market internals — `"no data"` is falsified

`INFORMATION_COVERAGE` L29 records *market internals (TICK/ADD/TRIN)* as **`✗ no data`**.

| symbol | verdict |
|---|---|
| `$TICK` | ✅ 1-minute, served back to **2018-07-10** — **8 years** |
| `$TRIN` | ✅ 1-minute, served back to **2022-07-11** — 4 years |
| `$VIX` | ✅ daily; empty at 2021 and 2011 → depth ~2–3 years |
| `$ADD` | ❌ resolves, serves nothing → `PROVIDER_LIMIT` |
| `$VXN` | ❌ `Instrument '^VXN' not found` |

**`$TICK` at 1-minute over 8 years is a genuinely new information surface**, at zero cost, on a
horizon that overlaps the entire research window. Volume is 0 on all of these — they are indices,
not traded contracts, and must never be treated as having flow.

## 6. What is *still* owner-gated — the honest remainder

| lane | status after audit |
|---|---|
| **Options / dealer gamma** (`GAMMA00`) | **still owner-gated.** No option-chain surface exists in this tool set at all |
| **DOM / Level-II** | **still blocked.** Only **one** replay day exists (`20260715.nrd`); the pause stands and this audit did not extend it |
| **Wider macro calendar** | **not probed here** — free-source construction, deferred to its own lane |
| **`$ADD`, `$VXN`** | `PROVIDER_LIMIT`, evidenced by actual failed probes |
| **BBO lane reaching 300+** | 168 is the ceiling of this disk. Closing the rest **would** need acquisition |

**OQ-5's order-flow row is now partly answered without payment.** It is not fully answered: the
quote-based half remains short. That row should be **re-scoped, not closed.**

## 7. Resource safety — checked before anything, per directive §1

| | |
|---|---|
| free disk `C:` | **25 GB free** of 300 GB (**92 % used**) — the NT8 store lives here and is already 11 GB |
| free disk `D:` | 173 GB free of 631 GB (73 % used) — the repo lives here, 7.2 GB |
| this audit's footprint | **~0 bytes.** Filenames and sizes only |

> ⚠️ **`C:` is the binding constraint at 25 GB free.** Any extraction must write CSV to a
> **`D:` target**, convert to parquet, and delete the CSV per session — which is exactly what the
> existing `csv_to_parquet.py` already does. **No unbounded capture. No full-depth DOM.** The
> 2026-08-12 resource pause is respected: reading files that already exist is not collection.

## 8. Continuation

| | |
|---|---|
| **Level 2 verdict** | **NOT exhausted.** Three lanes reopen at zero cost: signed flow, BBO (partial), market internals |
| **next** | extract the 262 `Last` / 123 BBO-complete NQ sessions via `RunStrategyBacktest` + the existing exporter, QA, then a **Stage-A information test** — information before policy |
| **promoted / demoted** | **nothing.** This audit measures capability, not edge |
| **acquired** | **nothing.** No purchase, no new charge, no sealed data read |
