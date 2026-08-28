# PROSPECTIVE SHADOW — the only evidence class this project does not yet own

| | |
|---|---|
| **status** | ✅ **RE-PROMOTED 2026-08-28 for the INCUMBENT, by owner directive.** Superseding the same-day demotion, which was scoped to a void object |
| created | 2026-08-28 · demoted · **re-promoted the same day, for a different and better reason** |
| **LIVE ENABLED** | **NO.** Shadow is evidence accumulation, never authorization to trade. **No live order. No simulated order. No Sim101. No account modification.** |

> ## **THE REASON FOR RE-PROMOTION — and it is not a new candidate.**
> ### **The project must stop waiting for a magical new candidate before it begins accumulating
> ### genuinely future evidence.**
> Every result this campaign owns is **discovery-consumed, validation-consumed, one-sided blind, or
> parity-only. The project has ZERO prospective evidence.** That is its single largest structural
> gap, and **no amount of further historical work closes it.** The incumbent alone justifies the
> architecture: `P1/PCT` and `XM_CONFLICT_v2` are frozen, parity-certified objects **today**, and
> every week that passes without a ledger is a week of forward evidence permanently lost.
>
> The earlier demotion argued that ~1.6 decisions/week did not justify *streaming* infrastructure.
> **That argument was right about streaming and wrong about logging.** A weekly append-only ledger
> costs essentially nothing to run and is the only thing that converts calendar time into evidence.

---

## 1. The one rule that makes this worth doing

> ### **NO BACKFILL. EVER.**
>
> A shadow ledger's entire value is that its rows were written **before** the outcome was known.
> One backfilled row destroys that property for the whole file, and it **cannot be repaired by
> labelling**. **Historical Playback is not prospective** — if a row's outcome existed before the
> row did, it is not shadow evidence.

### **`SHADOW_START = 2026-09-01 18:00 ET`** — unchanged.

> ### ⚠️ **IT IS NOT MOVED BACKWARD BECAUSE AUGUST DATA IS NOW AVAILABLE.**
> The ≥ 2026-08-01 sealed pool is **not** a substitute for prospective shadow. It may be read only
> through an already-existing, explicitly authorized locked-forward protocol —
> [`LOCKED_FORWARD.md`](LOCKED_FORWARD.md) and [`MONITORING_CALENDAR.md`](MONITORING_CALENDAR.md) —
> and never as a shortcut to "start the shadow earlier".

**This rule is now MECHANICAL, not advisory.** `research_sdk/shadow_ledger.py` **refuses** any row
at or before `SHADOW_START`, and refuses any decision whose timestamp does not strictly advance the
previous one.

## 2. Roster — the objects that actually exist

| object | source sha256 | status |
|---|---|---|
| **`P1/PCT`** — `WeeklyEdgeP1PCT_v1.cs` | `ee4c765bc5cab230…76e87b2` | incumbent, **parity-certified**. The benchmark. Parity proves implementation fidelity, **not** forward alpha validity |
| **`XM_CONFLICT_v2`** — `WeeklyEdgeXMConflict_v2.cs` | `2ec00dd4d0a11b99…4c910dde` | incumbent sleeve, **parity-certified**. Its **hedge mechanism has inverted** (ρ 0.086 → 0.369; payoff when P1 loses **+$598 → −$1,243**). Forward data is the only way to learn whether it still earns its place |
| **`P1/ABS`** — `WeeklyEdgeP1_v3.cs` | `e8bb9caface37462…e0a3d630` | **challenger / control**. PCT beats ABS on direction overwhelmingly (176/213 weeks, sign test p 7.1e-23) but **not** on paired magnitude (p 0.058). Burned data cannot settle it; running both from a common future timestamp can |

**Excluded, each for a recorded reason:**

| ⛔ | why |
|---|---|
| ~~`MS-BBO-CANDIDATE-1`~~ | **VOID** — features read up to **+2.065 s past** the decision instant (`int32` overflow). Causal object **−$1,785.88/session** |
| ~~`ESNQ_V1`~~ | **CLOSED** — development net **−$18,113.79**, 0 of 4 quartiles positive |
| ~~`TSMOM V2 / TAIL-H1`~~ | **CLOSED** — both roles failed on two protected windows |
| ~~`CARRY_V1`~~ | **CLOSED** — C6/C7, `SI` alone 84.1 % of positive contribution |
| ~~`VOLUME_LIQUIDITY_V1`~~ | **CLOSED** — development failed; see `runs/VOLUME_LIQUIDITY_V1_20260828/`. **It does not join the roster.** A candidate joins only after surviving every historical gate, and it did not reach the first one |

**A new candidate joins only after its definition is frozen**, never before.

## 3. ⭐ Decision-first architecture — **BUILT 2026-08-28**, `research_sdk/shadow_ledger.py`

Previously specified and deliberately not built. The owner directive requires it, so it exists.

> ### **TWO FILES. A DECISION IS NEVER EDITED TO CARRY ITS OUTCOME**, because editing it is exactly
> ### the act that destroys the evidence class.

| | `DECISION LEDGER` | `OUTCOME LEDGER` |
|---|---|---|
| written | **before the outcome exists** | later, appended |
| links | — | **references** a decision by `seq`; never rewrites it |
| fields | `seq · ts_decision · strategy_id · source_hash · config_hash · data_cutoff · input_dataset_version · input_source_hashes · action · intended_qty · expected_costs · quality_status · blocked_reason · prev_hash · row_hash` | `seq · decision_seq · ts_outcome · entry_fill · exit_fill · gross_pnl · costs · net_pnl · data_quality · note · prev_hash · row_hash` |

**Hash chain.** Every row carries `prev_hash` and a `row_hash` over its canonical JSON form.
Rewriting any earlier row breaks every hash after it, and `verify()` recomputes the whole chain.

**`quality_status` is mandatory and a blocked decision is RECORDED, with its reason.** A ledger that
silently drops bad rows becomes a filtered sample — the exact failure mode it exists to avoid.

### Self-test: **9 / 9 PASS**, and it includes a deliberate tamper

A check that cannot fail is useless, so the self-test **edits an already-written decision row** and
asserts that verification catches it.

| | |
|---|---|
| refuse a row at/before `SHADOW_START` | ✅ |
| refuse a non-advancing timestamp | ✅ |
| refuse a `BLOCKED` row with no reason | ✅ |
| refuse an outcome for a nonexistent decision | ✅ |
| refuse a **second** outcome for the same decision | ✅ |
| clean decision / outcome chains verify | ✅ ✅ |
| outcomes strictly post-date their decisions | ✅ |
| **TAMPER DETECTED** — edited decision row | ✅ |

## 4. First-read rules — no peeking, and no newly invented checkpoints

> **Distinction that is easy to blur:** *logging* shadow rows is not *reading* them for a verdict.
> Rows accumulate continuously; **reading them for a verdict requires its own preregistration.**

| roster | governing first-read rule |
|---|---|
| **incumbent NQ objects** (`P1/PCT`, `XM_CONFLICT_v2`, `P1/ABS`) | the **already-existing** [`LOCKED_FORWARD.md`](LOCKED_FORWARD.md) and [`MONITORING_CALENDAR.md`](MONITORING_CALENDAR.md) rules. ⛔ **No new checkpoint is invented because a result is currently interesting** |
| **a WEEKLY candidate, if one ever exists** | frozen **before** its first shadow decision: **S26** — 26 completed prospective weekly decisions, *early falsification only*; **S52** — the primary first meaningful annual checkpoint; **S104** — stronger confirmation. **Before S26: NO aggregate shadow P&L read.** Operational and data-quality monitoring is allowed; performance monitoring is not |

⚠️ **S26/S52/S104 are specified but NOT ARMED**, because there is no weekly candidate.
`VOLUME_LIQUIDITY_V1` failed development and does not join.

**No object's shadow may be read to decide whether to keep accumulating. That is peeking.**

## 5. Account-safety preconditions — blocking, and unchanged

Before any simulated order is emitted, the runner must **programmatically assert** that the target
account is a simulation/backtest/playback account. **If account identity is not positively verified,
no order is sent.** There is no fallback path to a real account and none may be added.
`LIVE ENABLED = NO` is binding and is **not** a per-strategy setting.

⚠️ **The current architecture emits NO ORDERS AT ALL.** It is a decision/outcome logger. §5 applies
the moment anyone adds an execution leg, and adding one is an owner decision.

## 6. What is built, and what is honestly still an owner action

| ✅ built and tested | 🔲 owner action |
|---|---|
| `research_sdk/shadow_ledger.py` — append-only, hash-chained, backfill-refusing, tamper-detecting, 9/9 self-test | **starting the accumulation.** The emitter must run on the owner's machine at a wall-clock time on live NT8 data from 2026-09-01 18:00 ET. Nothing in this repo can schedule that |
| the two-file schema and the `SHADOW_START` guard | attaching an execution leg, if ever wanted (then §5 binds) |
| roster and source hashes, frozen above | authorizing any read of the ≥2026-08-01 seal outside `LOCKED_FORWARD.md` |
| the **streaming engine** in `MSBBO_DEPLOYMENT_FREEZE`, certified against the corrected batch (19/20 features at exactly `0.000e+00`) — reusable the day a real sub-minute candidate exists | — |

**Still not built, and the reason is recorded so it is not mistaken for an oversight:**
`shadow_health.py`, the C#/NinjaScript cross-language parity harness, and the S60/S126/S252 gates of
`MSBBO_PROSPECTIVE_PROTOCOL_V1` — **each was specified for an object that turned out to read the
future.** They are re-openable in full the moment a candidate earns them.
