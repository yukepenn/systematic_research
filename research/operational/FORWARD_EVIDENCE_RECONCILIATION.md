# FORWARD EVIDENCE RECONCILIATION — `OWNER_FORWARD_START` vs `LEGACY_FORMAL_SHADOW_START`

Opened 2026-08-31 under the NQ ALPHA MASTER DIRECTIVE §0. **Established mechanically from the
machine, not from memory.** Written for the two PAPER clocks; §4's "complete" is scoped to those.
🔴 **A THIRD, HIGHER-GRADE STREAM EXISTS as of 2026-09-01**: the LIVE MNQ book on real-money account
`2047681`, logging to `C:\NT8_ForwardLogs\mnq\`. **Its fills are the campaign's first non-simulated
execution evidence** and must never be filed under the paper book's `SIMULATED_FILL_NON_EVIDENTIAL`
label. ✅ **RESOLVED 2026-09-01**: `LIVE_FORWARD_START` is pinned mechanically at **2026-09-01
00:42:00 ET** and the ledger is built — `research/operational/FORWARD_EVIDENCE_LEDGER_V2.md`,
`research_sdk/forward_ledger_v2.py` (21/21 adversarial tests). This section's §6 specification
was the design input; treat V2 as the implementation of it.

> The owner considers the demo/paper deployment to be the beginning of real forward observation.
> The pre-existing ledger contract says forward evidence starts 2026-09-01 18:00 ET.
> **Both are true. They are different claims and this file keeps them apart. NO BACKFILL.**

---

## 1. `OWNER_FORWARD_START` = **2026-08-30 18:00:00 ET**

**Evidence class: `FORWARD_DECISION_FIRST`.**

The earliest machine-verifiable timestamp at which a **currently-deployed frozen instance** made a
genuine real-time decision. At the 2026-08-30 18:00 ET session open both legs processed their first
realtime bar and each emitted a decision-time artifact **before any outcome existed**:

```
2026-08-30 18:00:00:198 [HD WeeklyEdgeP1PCT_v2 p1pct]   ROLL-PLAN blockNewEntriesFrom=2026-09-08 …
2026-08-30 18:00:00:201 [HD WeeklyEdgeP1PCT_v2 p1pct]   WARMUP-CARRY-FLAT ledger=0 strategyPosition=0
2026-08-30 18:00:00:203 [HD WeeklyEdgeXMConflict_v3 xm2] ROLL-PLAN blockNewEntriesFrom=2026-09-06 …
2026-08-30 18:00:00:203 [HD WeeklyEdgeXMConflict_v3 xm2] WARMUP-CARRY-FLAT ledger=0 strategyPosition=0
```

`ResolveRollDates` is gated `if (State != State.Realtime) return;` and latches on first call, so these
lines **can only be produced by a first realtime bar** — they are proof of live-data processing, not
of historical replay. The instances are the ones still running (`399562867` / `399562868`).

### Why not an earlier date

| candidate | class | why it is not the start |
|---|---|---|
| 2026-08-30 06:15:38 | `FORWARD_OPERATIONAL_ONLY` | first `Enabling NinjaScript strategy` in the entire retained log history — but the **certified v1/v2** classes, since superseded, and the market was closed |
| 2026-08-30 09:16–09:44 | `FORWARD_OPERATIONAL_ONLY` | `HD05` instrument-guard lines (incl. a real `CROSS-SERIES-MISMATCH` catch at 09:20:21). Proves the engine ran; **market closed, Sunday** |
| **2026-08-30 09:51:30 / 09:51:38** | `FORWARD_OPERATIONAL_ONLY` | the **currently deployed** instances arm and print `WARMUP START verdict=GO blocked=False`. Engine operation, **not** a market decision |
| 2026-08-31 00:58:00 | `FORWARD_EXECUTION_OBSERVED` | first order. **Later** than the first decision — choosing it would silently discard the flat decisions that preceded it, and it is also the first *profitable* trade, which §0 forbids as a selection criterion |

⚠️ **Deliberately not chosen: the first profitable trade.** Every bar close from 18:00:00 onward is a
decision, including the decision **not** to enter. Flat decisions are evidence.

## 2. `LEGACY_FORMAL_SHADOW_START` = **2026-09-01 18:00:00 ET** — UNCHANGED

Preregistered in `PROSPECTIVE_SHADOW.md` and enforced **mechanically**: `shadow_ledger.py` refuses any
row at or before `SHADOW_START`, and the runner was watermark-initialised (orders 584 / execs 852) so
pre-existing account history can never be ingested. **This date is not moved backward.** A
preregistered boundary that moves when it becomes convenient is worth less than the sessions it buys.

## 3. 🔴 THE CONSEQUENCE NOBODY HAD NOTICED — the first live trade will be REFUSED

`GENESIS_ShadowRunner` last ran **2026-08-30 17:10** (`nothing new`), i.e. **before** the first trade.
Its next run is 2026-08-31 17:10, at which point it will encounter the 00:58/03:51 round trip —
**and correctly refuse it as pre-`SHADOW_START` backfill.**

⇒ **Genuine forward evidence exists that the formal ledger is designed to reject.** That is not a bug;
it is the two clocks doing their jobs. But it means:

> ⚠️ **The 2026-08-30 18:00 → 2026-09-01 18:00 observations must be preserved in a separate,
> explicitly-labelled record, and must NEVER be injected into the hash-chained ledger.**

**This file is that record.** See §4.

## 4. THE FORWARD RECORD SO FAR (complete, from `OWNER_FORWARD_START`)

| # | when (ET) | what | class |
|---|---|---|---|
| 1 | 2026-08-30 18:00:00 | both legs' first realtime bar; roll plan resolved; ledger↔position reconciled flat | `FORWARD_DECISION_FIRST` |
| 2 | 08-30 18:00 → 08-31 00:58 | ~7 h of bar-close decisions, all **no-entry** | `FORWARD_DECISION_FIRST` |
| 3 | **2026-08-31 00:58:00** | **entry** `581992641240` Buy **2** NQU6 @ **29,421.00**, signal `L`, `isBacktestOrder=false` | `FORWARD_EXECUTION_OBSERVED` |
| 4 | 08-31 00:59:02 | `FILLPX assumed=29420 actual=29421` — **1.00 pt adverse** | `FORWARD_EXECUTION_OBSERVED` |
| 5 | **2026-08-31 03:51:00** | **exit** `581992641251` Sell 2 @ **29,501.25**, signal `XL` (the engine's own alpha exit, not the box latch, not a forced flat) | `FORWARD_EXECUTION_OBSERVED` |
| 6 | 08-31 03:52:14 | `FILLPX assumed=29502.5 actual=29501.25` — **1.25 pt adverse** | `FORWARD_EXECUTION_OBSERVED` |
| 7 | 08-31 (ongoing) | XM flat throughout — **correct by construction**, it cannot act before 09:45 ET | `FORWARD_DECISION_FIRST` |

**Round trip: +80.25 pts × 2 × $20 = +$3,210.00 gross, ~$8.72 commission, hold 2 h 53 m.**
**Round-trip slippage: 2.25 pts = $45/ctrRT** against $14.44 modelled and $20.65 previously measured.

### What this does and does not prove (directive §2, §60)

| | |
|---|---|
| ✅ **Question C — execution** | the engine arms, warms, decides, orders, fills, exits and reconciles. Two operational arguments confirmed on the first trade: it **sized 2 contracts** (only reachable with a warm 250-entry quality window) and it **traded entirely outside RTH** (an RTH template would have deleted it). |
| ❌ **Question A — historical alpha** | nothing. One trade. |
| ❌ **Question B — persistence** | nothing. N = 1, no tail event observed, one strategy version, one market state. |
| ⚠️ **Cost** | $45/ctrRT is n=1, in the **thinnest hours of the session**, and is a **SIMULATED fill on a demo account** — it measures NT8's fill simulator, not a broker. Directionally interesting, not yet evidence. |

## 5. WHAT `FORWARD_EVIDENCE_LEDGER_V2` MUST DO

Superset of the current shadow ledger, ingesting from `OWNER_FORWARD_START`:

- **Decision rows and outcome rows in SEPARATE files.** Never edit a decision row to add its outcome.
- Each decision preserves: strategy version + **source hash** + config hash, contract, UTC timestamp,
  `session_id`, intended side/qty, decision price, expected-fill model, paper fill, live fill if any,
  quality status, warm-up status, data-health, connection health, current P1 state, current XM state,
  reason code, **and blocked-reason if blocked**.
- Hash-chained. **No silent dropping.** A blocked decision is data. A disconnect is data. A rejected
  order is data. An out-of-range fill is data. A restart is data. A rollover is data.
- **Two clocks carried explicitly on every row**: whether it falls inside
  `LEGACY_FORMAL_SHADOW_START` or only inside `OWNER_FORWARD_START`. The pre-09-01 rows are real
  evidence at their stated class and must be **queryable but separable** — never merged into the
  formal chain, never used to claim preregistered prospective status.

## 6. STATUS

`OWNER_FORWARD_START` is **pinned with evidence**. `LEGACY_FORMAL_SHADOW_START` is **untouched**.
The gap window is **preserved in §4 of this file** and will be refused by the formal ledger as
designed. `FORWARD_EVIDENCE_LEDGER_V2` is **specified but not yet built** — building it is an
engineering task, not a research decision. 🔴 **It is now TOP of the engineering queue:** since
2026-09-01 it is the **only** specified home for the LIVE book's fills, which the hash-chained
shadow refuses both by account (`TARGET_ACCOUNTS` excludes `2047681`) and by `SHADOW_START`.
A third clock, **`LIVE_FORWARD_START`**, must be pinned to the live legs' first realtime bar —
read it from the warm-up certificates at `0430` / `0431` / `044132Z` UTC on 2026-09-01 in
`C:\NT8_ForwardLogs\mnq\warmup\` — and carry its own evidence class (proposed:
`FORWARD_EXECUTION_REAL`), **kept separable from both paper clocks. NO BACKFILL, and no merge.**
