# systematic_research

Autonomous systematic research on NQ / MNQ futures. Backtest and research only.
**Nothing here is authorized for live trading, and no live order has ever been placed by this repo.**

_Landing page. Current as of **2026-08-28**. It links; it does not duplicate._

---

## Read first — TIER 0, the whole bootstrap

| # | file | what it owns |
|---|---|---|
| 1 | **this page** | orientation |
| 2 | **[`CLAUDE.md`](CLAUDE.md)** | operating rules, safety boundary, conventions |
| 3 | **[`research/weekly_edge/CURRENT_BASELINE.md`](research/weekly_edge/CURRENT_BASELINE.md)** | **current research state** — objects, economics, evidence labels |

**That is the entire default read set.** A competent agent should recover ~95 % of current
operational truth from those three files. **Do not recursively read `runs/` or `research/archive/`
"to understand the repo".**

## What this is

One repository, seven campaigns, one at a time. Six are closed. Campaign **#7 `WEEKLY_EDGE`** is
the only active build mission: find robust portfolio-level geometric growth on NQ from 1-minute
bars, and ship it as an executable NinjaScript object.

Every experiment lives in an immutable `runs/<RUN_ID>/` directory with `spec.yaml` committed
**before** results exist. Failed and falsified experiments are never deleted — the record of what
does *not* work is the most reused asset here.

## Current state — four baselines, kept strictly apart

**Research truth and execution truth are different claims.** This repo does not mix them.

| | baseline | object |
|---|---|---|
| **A** | RESEARCH_SINGLE | **`P1/PCT`** |
| **B** | RESEARCH_PORTFOLIO_FRONTIER | **`{P1/PCT + XM_CONFLICT}`**, inverse-vol |
| **C** | EXECUTABLE_SINGLE | **`WeeklyEdgeP1PCT_v1`** — parity-certified 2026-08-27 |
| **D** | EXECUTABLE_COMPONENT_SET | **`WeeklyEdgeP1PCT_v1` + `WeeklyEdgeXMConflict_v2`** — both legs individually parity-certified 2026-08-27 |

Economics, evidence labels and caveats: **[`CURRENT_BASELINE.md`](research/weekly_edge/CURRENT_BASELINE.md)**.
Exactly what is installed, compiled and reproducible:
**[`EXECUTION_MANIFEST.md`](research/operational/EXECUTION_MANIFEST.md)**.

> **EXECUTABLE ≠ ENABLED.** Both objects reproduce inside NinjaTrader's Strategy Analyzer. Neither
> is deployed, started, or connected to any account. Live enablement is an owner action that has
> **not** been taken.
>
> **D is a certified COMPONENT SET, not an executable version of B.** B is inverse-vol weighted;
> the integer-contract / capital mapping has **not** been selected, and running both legs at
> quantity 1 does **not** reproduce B's economics. **The executable implementation of B is PENDING**
> an owner capital-allocation decision.

## What is running / blocked right now

- **`ESNQ_V1` is the ACTIVE research object — PRE-DEVELOPMENT-RESULT.** Cross-market ES↔NQ
  sub-minute information for 60 s NQ executable return. **No ESNQ alpha evidence exists yet**:
  the `DEV_44` substrate is built (44 NQ + 44 ES sessions) and the feature runner and result are
  pending. ⚠️ *(Superseded 2026-08-28: "new alpha discovery is PAUSED / next wave is EVENT
  RESPONSE" was the 2026-08-27 state. **`EVENT RESPONSE` is `CLOSED-BY-DATA`**, not deferred —
  `runs/DATAGATE_EVENTRESPONSE_20260827/`.)*
- **Blind populations, stated precisely.** ESNQ original blind manifest **15**, `OUTCOME_CONSUMED
  0`, `PRICE_DERIVED_INFORMATION_READ 0`, but **one session (`2025-08-13`) was transiently
  materialized and metadata-exposed** during a recorded exporter incident, so the **EFFECTIVE ESNQ
  blind population is 14** after an operational quarantine. The NQ BBO 19-session asset is **19
  outcome-unconsumed · 18 pristine-never-materialized · 1 metadata-exposed**.
- **`MS-BBO` VOID · `CARRY_V1` CLOSED · `TSMOM` CLOSED.** The campaign has **no candidate**.
- **DOM / Level-II / Market Replay capture is PAUSED** (owner risk-control, 2026-08-12) and must
  not be resumed autonomously.
- **LIVE ENABLED: NO.**
- Open owner decisions: **[`OWNER_QUEUE.md`](research/operational/OWNER_QUEUE.md)**.

## Tier 1 — read only if the task needs it

| file | for |
|---|---|
| [`research/operational/EXECUTION_MANIFEST.md`](research/operational/EXECUTION_MANIFEST.md) | what is installed / compiled / certified |
| [`research/weekly_edge/ninjascript/LIVE_READINESS.md`](research/weekly_edge/ninjascript/LIVE_READINESS.md) | NinjaScript design, risk limits, parity protocol |
| [`research/weekly_edge/INFORMATION_COVERAGE_20260827.md`](research/weekly_edge/INFORMATION_COVERAGE_20260827.md) | which information surfaces are measured / null / blocked |
| [`research/weekly_edge/MECHANISM_COVERAGE_20260826.md`](research/weekly_edge/MECHANISM_COVERAGE_20260826.md) | which mechanisms are closed, and why |
| [`research/weekly_edge/DATA_CENSUS_20260826.md`](research/weekly_edge/DATA_CENSUS_20260826.md) · [`research/operational/LOCKED_FORWARD.md`](research/operational/LOCKED_FORWARD.md) | what data exists; what is sealed |
| [`research/weekly_edge/OPPORTUNITY_LANGUAGE.md`](research/weekly_edge/OPPORTUNITY_LANGUAGE.md) | **binding** — how ceiling/oracle numbers may be quoted |
| [`research/operational/MONITORING_CALENDAR.md`](research/operational/MONITORING_CALENDAR.md) | scheduled forward reads |
| [`research/INDEX.md`](research/INDEX.md) | repository structure |

## Tier 2 — evidence, on demand

`runs/<RUN_ID>/spec.yaml` + `REPORT.md`. One directory per experiment, never overwritten.
Campaign #7 runs are `runs/WE_W*`. Parity runs are `runs/WE_*_PARITY_*`.

## Tier 3 — archive. Not part of any bootstrap.

`research/archive/` holds closed-campaign truth: campaign #3's shipped baselines
(`campaign3_system_master/BASELINE_MODELS.md`), campaign #1's reports, dated state snapshots, and
retired handoffs. **They are correct, they are preserved, and they are not the current frontier.**
Closed campaigns keep their own in-place state docs (`research/CAMPAIGN_STATE.md`,
`research/system_master/CURRENT_TRUTH.md`, `research/scalping_lab/CAMPAIGN_STATE.md`); those say
"current" about a campaign that has ended.

## Safety

Research/backtest accounts only. Never place, modify or cancel orders. Never enable or deploy a
strategy. Never touch Sim101 or a real account. Never alter connections, credentials or licensing.
Never modify the licensed vendor assembly. No force-push, no history rewrites, no deletion of raw
research evidence. Full rules in [`CLAUDE.md`](CLAUDE.md).
