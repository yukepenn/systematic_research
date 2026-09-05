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

Most recent synthesis: **[`CLEANSET_20260901.md`](research/operational/CLEANSET_20260901.md)** — the 2026-09-01 clean-set closeout: what was found, what was fixed, what is still open, and the three owner actions. Prior: [`STATE_20260901.md`](research/operational/STATE_20260901.md).

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
| **C** | EXECUTABLE_SINGLE | **`WeeklyEdgeP1PCT_v1`** — the PARITY-CERTIFIED class |
| **D** | EXECUTABLE_COMPONENT_SET | **`WeeklyEdgeP1PCT_v1` + `WeeklyEdgeXMConflict_v2`** — both legs individually parity-certified |

> ⚠️ **CORRECTED 2026-09-01: this table previously named `_v3`/`_v4` as C and D.** Those are the
> **hardened deployed descendants**, not the certified objects — the parity certificates
> (`EXECUTION_MANIFEST.md`) belong to `_v1`/`_v2`, and `_v3`/`_v4`'s own source headers still say
> `NOT CERTIFIED`. Calling them "parity-certified" here collapsed the exact distinction
> `CLAUDE.md` §3 exists to protect: **EXECUTABLE · PARITY-CERTIFIED · LIVE-ENABLED are three
> separate statuses.**

Economics, evidence labels and caveats: **[`CURRENT_BASELINE.md`](research/weekly_edge/CURRENT_BASELINE.md)**.
Exactly what is installed, compiled and reproducible:
**[`EXECUTION_MANIFEST.md`](research/operational/EXECUTION_MANIFEST.md)**.

> **D is a certified COMPONENT SET, not an executable version of B.** B is inverse-vol weighted;
> that integer-contract mapping was never selected, and running both legs at quantity 1 does
> **not** reproduce B's economics. **Never quote a research-portfolio figure for a component set.**

### The live object — and it is not A/B/C/D

🔴 **Since 2026-09-03 the live book is ONE LEG: `WeeklyEdgeP1PCTMnq_v1` `399562885` alone, at
`MnqPerNq = 3`.** The XM leg was **withdrawn to OBSERVATION by owner decision 2026-09-05**
([`OWNER_DECISION_20260905_XM_WITHDRAWN.md`](research/operational/OWNER_DECISION_20260905_XM_WITHDRAWN.md)) —
an **operational** withdrawal that changes no research baseline.
**Dropping a leg does not make a smaller `M_11`; it makes a different object.**

`WeeklyEdgeP1PCTMnq_v1` (`runs/MX01_MNQ_EXECUTION_PORT_20260831/`) is a certified object's
**decisions** executing on a **different contract at 3/10 size**.

The design separates the **decision instrument** (NQ, primary series, every signal) from the
**execution instrument** (MNQ, added series, orders only). Decision drift is therefore **zero by
construction**, and measured: the per-bar decision exports are **byte-identical, same `sha256`,
over 61,600 bars**. All six MX01 gates pass.

> 🔴 **RISK OF THE OBJECT THAT IS ACTUALLY LIVE (P1 alone, 3 MNQ), `CAP02B`, 6/6 gates PASS:**
> two-year **P(losing the account) = 2.5 %** (full pool) / 0.8 % (warm), **honest band ~2 %–20 %**,
> and **48 % if the edge is zero**. Median two-year drawdown **76 %** of the $10,260 account.
> ⭐ Assumption-free anchor (n=1, the realised path at 3 MNQ): P1 alone troughed at **69 %** of
> equity and **survived**; the **pair** troughed at **140 %** and **would have been wiped out.**
>
> ⚠️ **The numbers below are the PAIR's and no longer describe the live book.** Kept because the
> pair may return. At `MnqPerNq = 3` the pair's median two-year drawdown is 108 % of the
> $10,206.86 account and its two-year P(losing the account) is 6.5 % in-sample — 9.7 % central,
> 21.6 % low, 60 % if the edge is zero. At 1 MNQ, 0.1 %. The older single line —
> *0.30 × $51,891 = 152.5 %* — is one draw from that distribution and not the middle one.
> ⚠️ **An earlier version of this paragraph said 66 %.** That figure is
> `P(drawdown from peak > equity)`, which is **not** the probability of losing the account — the
> modelled peak runs far above the starting balance. Corrected in
> `runs/CAP01B_RUIN_CORRECTION_20260901/`; authority `CURRENT_LIVE_TRUTH.md` §CAPITAL.
> This is a priced owner decision, not an oversight. `MnqPerNq` is a deployable input.

## What is running right now

*(verified from `ListAllStrategies` 2026-09-05 — never from `ListStrategies(account)`, which
returned 2 of 4 rows on 09-01 and produced a confidently wrong audit.)*

- 🔴 **LIVE `2047681` — ONE leg.** `WeeklyEdgeP1PCTMnq_v1` `399562885`, Realtime, enabled, flat,
  NQ 09-26 decisions / MNQ 09-26 fills, `MnqPerNq = 3`. **Its roll guard blocks new entries from
  2026-09-08.** Exits are never gated.
- 🔴 **NOT RUNNING: live XM** — withdrawn to OBSERVATION 2026-09-05 (owner decision).
- 🔴 **NOT RUNNING: the PAPER book** (`_v3` / `_v4`) — NT8 auto-disabled every leg on 2026-09-03
  19:06:41 after 8 price-feed flaps, a 22:23 restart then removed all strategy rows, and
  `DEMO8383477` reports `connection: null`. **The uncontaminated forward-evidence book is dark.**
- ⭐ **The standing watch item is CLOSED and a new one replaced it.** The first real fill
  (2026-09-01 09:45) did **not** trip `RECONCILE-BREAK`. But on 2026-09-03 a P1 exit **opened a
  naked short 6 MNQ** because all three witnesses describe what the *instance* did and none
  describes what the *account* holds —
  [`INCIDENT_20260903_GHOST_POSITION.md`](research/operational/INCIDENT_20260903_GHOST_POSITION.md).
  Fixed offline as HD-20..23 (32/32 certified); **not deployed** —
  [`DEPLOY_HD23_20260921.md`](research/operational/DEPLOY_HD23_20260921.md).
- 🔴 **ROLL RED ZONE `2026-09-06 → 2026-09-18`.** Re-enabling inside it latches the fail-safe
  **permanently** while every health check still reports green. The roll now involves **`MNQ 12-26`
  as well as `NQ 12-26`** — any instruction naming only NQ is incomplete, **including the dates:
  both legs are safe only `≥ 2026-09-19`.** Single authority: `research/operational/CURRENT_LIVE_TRUTH.md` §ROLL.
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
| 🔴 [`research/operational/OWNER_ACTION_20260901_P1_LEDGER_DEAD.md`](research/operational/OWNER_ACTION_20260901_P1_LEDGER_DEAD.md) | **OPEN owner action** — the live P1 decision ledger is dead |
| 🔴 [`research/operational/LIVE_SAFETY_FINDINGS_20260901.md`](research/operational/LIVE_SAFETY_FINDINGS_20260901.md) | adversarial live-safety review: a **second latching bug**, and what survived |
| ⭐ [`research/operational/COST_MODEL.md`](research/operational/COST_MODEL.md) | **the single cost authority.** Every figure carries a basis and an evidence tag |
| ⭐ [`runs/CAP01B_RUIN_CORRECTION_20260901/`](runs/CAP01B_RUIN_CORRECTION_20260901/REPORT.md) | **the capital/ruin distribution** — supersedes CAP01's headline |
| [`research/operational/FORWARD_EVIDENCE_LEDGER_V2.md`](research/operational/FORWARD_EVIDENCE_LEDGER_V2.md) | where the **live** book's real fills are recorded; the three clocks |
| [`research/operational/TRUNCATION_BLAST_RADIUS_20260901.md`](research/operational/TRUNCATION_BLAST_RADIUS_20260901.md) | the silent-truncation defect: complete caller inventory + the loud fix |
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
