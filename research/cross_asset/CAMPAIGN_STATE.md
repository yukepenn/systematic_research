# CROSS-ASSET FUTURES RESEARCH EXPANSION — campaign state

**Opened 2026-09-06 by owner supplemental directive.** Continues (does not reset) WEEKLY_EDGE /
GENESIS II. State document — wave history lives in `runs/`, this file links.

## The reframe that defines this campaign

> We are NOT porting P1 to other markets. We are transferring the **research PROCESS** that
> produced the NQ system, and letting **each market grow its own native engine**.

- **P1 transfer is ONE lane (Lane A, the Transfer Benchmark), not the campaign.** Its failure on a
  market means "P1 is not universal", never "this market has no alpha".
- **Orthogonality is a first-class product objective.** A Sharpe-0.8 engine with ~0 correlation to
  NQ can beat pushing NQ from 1.2→1.25. The prize is a **multi-engine low-correlation portfolio**.
- Accepted prior result (not reopened without new evidence): free incremental alpha *inside the
  existing NQ information surface* is credibly exhausted (56 trials, 0 live candidates).
- 🔴 **Owner decision, already made: DO NOT buy data/subscriptions.** Use extracted/extractable
  repo data, existing infra, free public data (with §24 rules), current tools. No purchase blocks
  this campaign. Live-book safety rules (CLAUDE.md §1) unchanged; nothing here touches `2047681`.

## The three durable assets this campaign must produce

1. **`FUTURES_ALPHA_MAP.md`** — per market: best mechanism, status, standalone quality, NQ corr,
   portfolio value. Populated ONLY from verified experiments; never invented cells.
2. **`MECHANISM_TRANSFER_MATRIX.md`** — which effects are universal / asset-class / market-native.
3. **The multi-engine portfolio** — the real prize; built from low-corr survivors under simple
   risk-budget rules (equal-risk / fixed-vol), evaluated vs NQ-alone.

## Four lanes per Tier-1 instrument

- **A — NQ mechanism transfer** (benchmark, minimal DoF, dimensionless transforms).
- **B — native market discovery** (first-principles; the market's own sessions/economics; may
  produce a completely different engine).
- **C — cross-asset / relative state** (strict chronology; predictor must precede the decision).
- **D — portfolio value** (vs NQ under simple fixed risk allocation).

## Data reality (PROVISIONAL — Wave 0 data agent confirms exactly)

| root | class | local 1-min | daily (inventory) | status for intraday P1-depth |
|---|---|---|---|---|
| NQ | equity idx | ✅ deep (2006+ spine, 2022+ SM1M) | — | ANCHOR (live P1) |
| ES | equity idx | ✅ 1,427 sess 2022+ | ✅ ~2009+ | intraday-ready |
| RTY | equity idx | ✅ 1,419 sess 2022+ | ✅ | intraday-ready |
| YM | equity idx | ✅ 1,419 sess 2022+ | ✅ | intraday-ready |
| ZB | rates | ✅ 1,114 sess 2022-12+ (back-adj) | ✅ | 🎯 intraday-ready, orthogonal class |
| CL | energy | ⏳ 1,481 sess ON DISK, unextracted (recompile-path) | ✅ | extract in a session break (Wave 2) |
| ZN | rates | ⚠️ ~185 sess only (2025-12+) | ✅ | daily-only for now |
| GC | metals | ❓ not confirmed local (only MGC ~184 sess) | ✅ ~2009+ | **daily-only** unless found/extracted |
| 6E | FX | ❓ not confirmed local (only 6J ~185 sess) | ✅ | **daily-only** unless found/extracted |
| MGC/6J/SI/HG/NG/6B/6A/ZF | mixed | thin/absent 1-min | ✅ via inventory | daily-only / Tier-2 |

**Honesty rule:** metals & FX get a **daily-resolution** autopsy + native/daily-swing engine lane
(legit: each market teaches its own mechanism); intraday P1-depth is reserved for the markets with
deep 1-min data. Do not fake intraday history that isn't there.

## Wave tracker

| wave | scope | status |
|---|---|---|
| **XINST01** (Lane A benchmark) | P1 transfer → ES/RTY/YM/ZB, no-mining, NQ-reproduction gate, orthogonality | 🟡 RUNNING `wf_d97689db-200` (trials G00056-59) |
| **Wave 0** (infra) | NQ Research Playbook · data/roll/cost inventory · pristine-data freeze · Tier-1 rank | 🟡 LAUNCHING |
| Wave 1 | parallel market autopsies (descriptive science, instrument-native sessions) | pending Wave 0 |
| Wave 2 | cheap screening: transfer + native mechanism families per market | pending |
| Wave 3 | deepen survivors (rules, neighborhood, chronology, cost stress) | pending |
| Wave 4 | independent engine construction (1-2 strong mechanisms, not 10 weak) | pending |
| Wave 5 | cross-asset skeptic (adversarial, per winner) | pending |
| Wave 6 | portfolio test (simple allocation; Sharpe/DD/tail/capital) | pending |
| Wave 7+ | secondary instruments by EV; implementation for strong candidates | pending |

## Discipline (non-negotiable, inherited)

- One hash-chained ledger (`research/genesis/SEARCH_LEDGER.jsonl`), cross-asset families; count
  failed searches, report all not just winners; family-wise correction across instruments.
- eval_battery led by weekly-vol; fixed-DD only with its random-thinning placebo.
- Roll/back-adjustment audit MANDATORY (§10) — a candidate resting on roll artifacts is invalid.
- Market-specific cost (tick/point/commission/spread) with an optimistic/base/conservative/stress
  band; a candidate that dies at +1 tick is fragile.
- Instrument-native sessions — **never copy NQ 09:30-16:00 to other futures.**
- Move HORIZONTALLY when a family is exhausted; never mutate a consumed dataset until it turns green.
- No promotion / no live deploy / no sizing change from research runs. $0.
