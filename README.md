# systematic_research

Autonomous systematic research on NQ / MNQ futures.

> 🔴 **THIS REPO NOW HAS A LIVE REAL-MONEY BOOK.** Since **2026-09-01**, account `2047681`
> runs the M_11 pair executing on MNQ at `MnqPerNq = 3`. The line that used to stand here —
> *"nothing is authorized for live trading, and no live order has ever been placed"* — is
> **no longer true**. Read
> **[`CURRENT_LIVE_TRUTH.md`](research/operational/CURRENT_LIVE_TRUTH.md)** before touching
> anything. Enabling, disabling, resizing or ordering on that account is an **owner action**,
> never an agent one.

_Landing page. Current as of **2026-09-01**. It links; it does not duplicate._

---

## Read first — TIER 0, the whole bootstrap

| # | file | what it owns |
|---|---|---|
| 1 | **this page** | orientation |
| 2 | **[`CLAUDE.md`](CLAUDE.md)** | operating rules, safety boundary, conventions |
| 3 | 🔴 **[`research/operational/CURRENT_LIVE_TRUTH.md`](research/operational/CURRENT_LIVE_TRUTH.md)** | **what is running on real money right now** |
| 4 | **[`research/weekly_edge/CURRENT_BASELINE.md`](research/weekly_edge/CURRENT_BASELINE.md)** | **current research state** — objects, economics, evidence labels |

**That is the entire default read set.** **Do not recursively read `runs/` or `research/archive/`
"to understand the repo"** — there are 464 run directories and doing so is explicitly forbidden.

Most recent synthesis: **[`STATE_20260901.md`](research/operational/STATE_20260901.md)**.

## What this is

One repository, seven campaigns, one at a time. Six are closed. Campaign **#7 `WEEKLY_EDGE`** is
the only active build mission: find robust portfolio-level geometric growth on NQ from 1-minute
bars, and ship it as an executable NinjaScript object. **As of 2026-09-01 it has shipped one.**

Every experiment lives in an immutable `runs/<RUN_ID>/` directory with `spec.yaml` committed
**before** results exist. Failed and falsified experiments are never deleted — the record of what
does *not* work is the most reused asset here.

## Current state — four baselines, kept strictly apart

**Research truth and execution truth are different claims.** This repo does not mix them.

| | baseline | object |
|---|---|---|
| **A** | RESEARCH_SINGLE | **`P1/PCT`** |
| **B** | RESEARCH_PORTFOLIO_FRONTIER | **`{P1/PCT + XM_CONFLICT}`**, inverse-vol |
| **C** | EXECUTABLE_SINGLE | **`WeeklyEdgeP1PCT_v3`** |
| **D** | EXECUTABLE_COMPONENT_SET | **`WeeklyEdgeP1PCT_v3` + `WeeklyEdgeXMConflict_v4`** — both legs individually parity-certified |

Economics, evidence labels and caveats: **[`CURRENT_BASELINE.md`](research/weekly_edge/CURRENT_BASELINE.md)**.
Exactly what is installed, compiled and reproducible:
**[`EXECUTION_MANIFEST.md`](research/operational/EXECUTION_MANIFEST.md)**.

> **D is a certified COMPONENT SET, not an executable version of B.** B is inverse-vol weighted;
> that integer-contract mapping was never selected, and running both legs at quantity 1 does
> **not** reproduce B's economics. **Never quote a research-portfolio figure for a component set.**

### The live object — a fifth thing, and it is not A/B/C/D

**`WeeklyEdgeP1PCTMnq_v1` + `WeeklyEdgeXMConflictMnq_v1`** (`runs/MX01_MNQ_EXECUTION_PORT_20260831/`)
are the certified objects' **decisions** executing on a **different contract at 3/10 size**.

The design separates the **decision instrument** (NQ, primary series, every signal) from the
**execution instrument** (MNQ, added series, orders only). Decision drift is therefore **zero by
construction**, and measured: the per-bar decision exports are **byte-identical, same `sha256`,
over 61,600 bars**. All six MX01 gates pass.

> 🔴 **At `MnqPerNq = 3` the book's own already-observed worst drawdown rescales to $15,567 =
> 152.5 % of the $10,206.86 account.** 1 MNQ = 50.8 %, 2 MNQ = 101.7 %. This is a priced owner
> decision, not an oversight. `MnqPerNq` is a deployable input requiring no rebuild.

## What is running right now

- 🔴 **LIVE `2047681`** — `WeeklyEdgeP1PCTMnq_v1` + `WeeklyEdgeXMConflictMnq_v1`, NQ 09-26 decisions
  / MNQ 09-26 fills, `MnqPerNq = 3`. **The first real fill is the standing watch item** — the
  realtime reconcile guard is `State.Realtime`-gated and no backtest ever exercised it.
- **PAPER `DEMO8383477`** — the certified NQ book (`_v3` / `_v4`), the **forward-evidence** book.
  Its decisions are `FORWARD_DECISION_FIRST`; its fills remain `SIMULATED_FILL_NON_EVIDENTIAL`.
- 🔴 **ROLL RED ZONE `2026-09-06 → 2026-09-18`.** Re-enabling inside it latches the fail-safe
  **permanently** while every health check still reports green. The roll now involves **`MNQ 12-26`
  as well as `NQ 12-26`** — any instruction naming only NQ is incomplete.
- 🔴 **Strategy source must never go through the CrossTrade MCP** — it is a *remote* server whose
  terms owe the customer no confidentiality. `CompileNinjaScript` / `WriteNinjaScriptFile` /
  `ReadNinjaScriptFile` on our own classes are banned; see `CLAUDE.md` §1 and the local path in §6.
- **DOM / Level-II / Market Replay capture is PAUSED** (owner risk-control, 2026-08-12) and must
  not be resumed autonomously.
- Frontier, closures and open decisions: **[`GENESIS_III_VERDICT.md`](research/operational/GENESIS_III_VERDICT.md)**,
  **[`GENESIS_III_OPEN_STATE.md`](research/operational/GENESIS_III_OPEN_STATE.md)**,
  **[`OWNER_QUEUE.md`](research/operational/OWNER_QUEUE.md)**.

## Tier 1 — read only if the task needs it

| file | for |
|---|---|
| [`research/operational/STATE_20260901.md`](research/operational/STATE_20260901.md) | latest synthesis: what changed, what it cost to learn |
| [`runs/MX01_MNQ_EXECUTION_PORT_20260831/`](runs/MX01_MNQ_EXECUTION_PORT_20260831/) | the live object: spec, report, transforms, live deploy sheet |
| [`research/operational/EXECUTION_MANIFEST.md`](research/operational/EXECUTION_MANIFEST.md) | what is installed / compiled / certified |
| [`research/operational/NT8_OPERATING_MODEL.md`](research/operational/NT8_OPERATING_MODEL.md) · [`NT8_RUNBOOK.md`](research/operational/NT8_RUNBOOK.md) | NinjaTrader operations |
| [`research/weekly_edge/ninjascript/LIVE_READINESS.md`](research/weekly_edge/ninjascript/LIVE_READINESS.md) | NinjaScript design, risk limits, parity protocol |
| [`research/weekly_edge/INFORMATION_COVERAGE_20260827.md`](research/weekly_edge/INFORMATION_COVERAGE_20260827.md) | which information surfaces are measured / null / blocked |
| [`research/weekly_edge/MECHANISM_COVERAGE_20260826.md`](research/weekly_edge/MECHANISM_COVERAGE_20260826.md) | which mechanisms are closed, and why |
| [`research/weekly_edge/DATA_CENSUS_20260826.md`](research/weekly_edge/DATA_CENSUS_20260826.md) · [`research/operational/LOCKED_FORWARD.md`](research/operational/LOCKED_FORWARD.md) | what data exists; what is sealed |
| [`research/weekly_edge/OPPORTUNITY_LANGUAGE.md`](research/weekly_edge/OPPORTUNITY_LANGUAGE.md) | **binding** — how ceiling/oracle numbers may be quoted |
| [`research/operational/MONITORING_CALENDAR.md`](research/operational/MONITORING_CALENDAR.md) | scheduled forward reads |
| [`research/INDEX.md`](research/INDEX.md) | repository structure |

## Tier 2 — evidence, on demand

`runs/<RUN_ID>/spec.yaml` + `REPORT.md`. One directory per experiment, never overwritten.

## Tier 3 — archive. Not part of any bootstrap.

`research/archive/` holds closed-campaign truth. **They are correct, they are preserved, and they
are not the current frontier.** Closed campaigns keep their own in-place state docs; those say
"current" about a campaign that has ended.

## Safety

**Never place, modify or cancel an order. Never enable or start a strategy** — including on
`2047681`, and including when the owner asks; enabling is done by the owner in the NT8 UI. The
agent may **read** the live account freely. Never alter connections, credentials or licensing.
Never modify the licensed vendor assembly. Never send strategy source through the CrossTrade MCP.
No force-push, no history rewrites, no deletion of raw research evidence.
Full rules in [`CLAUDE.md`](CLAUDE.md).
