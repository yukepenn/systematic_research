# `PROSPECTIVE_SHADOW_PREFLIGHT` — **READY**

`ENGINEERING_ONLY`. **No real prospective outcome was recorded.** `SHADOW_START = 2026-09-01
18:00 ET` has not arrived; every artifact here is a `_preflight_*` **test file** in this run's
`out/`. **The real shadow ledger does not exist and was not created.**

> ## ⭐ **THE PREFLIGHT PAID FOR ITSELF: IT FOUND A REAL DEFECT BEFORE THE FIRST ROW WAS EVER
> ## WRITTEN — a DST ordering bug that would have silently corrupted the no-backfill guard.**

---

## 1. ⚠️ The defect, and the fix

`shadow_ledger.py` compared decision timestamps as **strings**. That is correct only while every
row carries the same UTC offset — and **the shadow starts in EDT (−04:00) and runs into EST
(−05:00)**.

```
a = 2026-11-02T08:30:00-05:00   = 13:30Z
b = 2026-11-02T09:00:00-04:00   = 13:00Z

STRING  compare  a > b :  False      <-- says a is EARLIER
INSTANT compare  a > b :  True       <-- a is genuinely LATER
```

**They disagree.** On the day the clocks change, a legitimately later decision would have been
**refused as backfill** — and the operator would have seen a `NO BACKFILL` error on a perfectly
valid row, or (worse, with the comparison the other way round) a genuinely out-of-order row would
have been **accepted**.

**Fixed in `research_sdk/shadow_ledger.py`:** comparison is now on the **parsed instant**, and a
**naive stamp with no UTC offset is REFUSED** rather than silently coerced. Self-test **11/11**
(was 9/9), including the DST case and the naive-stamp refusal.

> This is the pattern this repo keeps re-learning: **a guard that has never been made to fail is
> not a guard.** The bug was invisible to every test that only checked the happy path.

## 2. Roster — recovered from repo truth

| object | source | sha256 | bytes | status |
|---|---|---|---:|---|
| **`P1/PCT`** | `WeeklyEdgeP1PCT_v1.cs` | `ee4c765bc5cab230…` | 28,809 | incumbent, **parity-certified** |
| **`XM_CONFLICT_v2`** | `WeeklyEdgeXMConflict_v2.cs` | `2ec00dd4d0a11b99…` | 20,994 | incumbent sleeve, **parity-certified** |
| **`P1/ABS`** | `WeeklyEdgeP1_v3.cs` | `e8bb9caface37462…` | 26,544 | challenger / control |

All three resolve and hash. Evidence class of every object: **`DISCOVERY_CONSUMED`**
(`XM` additionally **`REGIME-LOCAL` by data availability**). **Account safety: no order path.**

## 3. Test results — every guard exercised in **both** directions

| test | result |
|---|---|
| **S0-1a** before `SHADOW_START` | ✅ **REJECTED** |
| **S0-1b** *exactly at* `SHADOW_START` | ✅ **REJECTED** — the contract is **strictly after** |
| **S0-1c** after `SHADOW_START` | ✅ accepted |
| **S0-2a** outcome for a nonexistent decision | ✅ REJECTED |
| **S0-2b** a *second* outcome for the same decision | ✅ REJECTED |
| **S0-2c** outcomes strictly post-date decisions | ✅ |
| **S0-2d** decision schema carries **no** result field | ✅ *structurally cannot hold its own outcome* |
| **S0-2e** non-advancing timestamp | ✅ REJECTED |
| **S0-3a** clean chain verifies | ✅ |
| **S0-3b** **edited** decision row | ✅ **DETECTED** |
| **S0-3c** verifies again after restore | ✅ |
| **S0-4a–c** ET/DST, and the string-vs-instant **disagreement** | ✅ **defect found** |
| **S0-4d** fixed ledger accepts the later instant that sorts earlier | ✅ |
| **S0-4e** timestamp with no UTC offset | ✅ REFUSED |
| **S0-4f** session unit: **1,058 sessions vs 1,056 dates** | ✅ |
| **S0-4g** date masquerading as a session | ✅ REJECTED |
| **S0-5a** a `BLOCKED` decision is **recorded, not dropped** | ✅ |
| **S0-5b** `BLOCKED` with no reason | ✅ REJECTED |
| **S0-5c** invalid `quality_status` | ✅ REJECTED |
| **S0-6a/b** **ZERO ORDER PATH** (AST, not grep) | ✅ **no banned module, no banned call** |

**`shadow_ledger.py` imports exactly: `csv`, `hashlib`, `json`, `os`, `datetime`, `typing`.**
No network stack. No broker client. **It cannot place, modify or cancel anything.**

## 4. WRITE vs READ — the restriction is code

The preflight ships `health()`, the **only** function the operator may call before an authorised
read. It never opens the P&L columns, so it is **structurally incapable** of returning performance:

```
alive · decisions · outcomes · blocked · quality_mix · chain_ok · head · first_ts · last_ts · strategies
```

Leak check for `pnl / net / gross / sharpe / equity / hit_rate / cum / return`: **none**.

⛔ **Governed reads** stay with `LOCKED_FORWARD.md` and `MONITORING_CALENDAR.md` for the incumbent
NQ objects. **S26/S52/S104 remain specified but NOT ARMED** — there is no weekly candidate.

## 5. What is ready, and what remains an owner action

| ✅ ready | 🔲 owner |
|---|---|
| ledger module, 11/11 self-test incl. tamper + DST | **starting accumulation** — the emitter must run on your machine at a wall-clock time from **2026-09-01 18:00 ET** |
| roster frozen and hashed | attaching an execution leg (would re-arm §5 of the shadow protocol) |
| no-backfill, decision-first, hash chain, fail-closed, zero-order-path — all **demonstrated to reject** | authorising any read of the ≥2026-08-01 seal outside `LOCKED_FORWARD` |

⚠️ **Recommendation carried forward, not silently applied:** the emitter should write **UTC (`…Z`)**
stamps. The ledger now handles mixed offsets correctly, but a single canonical offset removes the
class of problem rather than defending against it.

**`SHADOW_START = 2026-09-01 18:00 ET` — unchanged, not moved backward, no August backfill.**
**LIVE ENABLED = NO.**
