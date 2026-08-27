# TOMORROW PRODUCTION CANDIDATE — 2026-08-27

> # 🔒 **LIVE ENABLED: NO.** This document answers *"what is ready?"*. It authorises nothing.
> Real-money enablement is **owner-only** and is not requested here.

**The question (§22):** *if real trading had to start with the strongest defensible book using
information available today, what exactly would it contain?*

---

## ⚠️ The answer, stated plainly

> ### The candidate book is **`P1/PCT` + `XM_CONFLICT_v2`** — **unchanged from 2026-08-27 morning.**
> ### **Nothing discovered today earned admission.** Not because the work failed, but because
> ### **closing questions and building substrate is not the same as producing a component.**

I am not padding this document with things that exist. Directive §22: *"Do NOT force inclusion just
because a component exists."*

## 1. Layers

### CORE — parity-certified, execution-reproducing

| component | class | status | evidence |
|---|---|---|---|
| **`WeeklyEdgeP1PCT_v1`** | STRUCTURAL | **PARITY-CERTIFIED**, frozen `ee4c765bc5cab230` | 2,131 vs 2,137 trades (+0.28 %), matched 99.672 %, weekly ρ 0.9852, **1,908 of 2,124 matched trades to $0.00** |
| **`WeeklyEdgeXMConflict_v2`** | STRUCTURAL | **PARITY-CERTIFIED**, frozen `2ec00dd4d0a11b99` | direction 99.715 %, 347 vs 346 trades, composite max\|diff\| **0.000000** |

### EXPERIMENTAL — research-supported, **not** production-admissible

| component | why it is not in CORE |
|---|---|
| Microstructure standalone (15–60 s) | `MS01` says friction is **payable** and break-even is **54–58 %** accuracy. **No model exists.** DATA-CAPABLE only |
| Multi-market TSMOM | universe inventoried (24 roots, 6 sectors, 2016–2025). **No substrate, no roll process, no signal, no result** |
| Internals → direct RTH NQ return | untested. `INT01` closed the *routing* mapping, not this one |

### SHADOW ONLY — nothing

No component has execution evidence short of parity. **The shadow ledger is empty and is not
back-filled** (§21: prospective only).

### CLOSED — not carried forward

`internals → P1 routing` (NULL) · `order flow → P1 action value` (CLOSED-BY-POWER, needs 998
sessions of 713 that exist) · `higher-timeframe` (NULL) · `NQ-path action-value information` (NULL) ·
`event response` (CLOSED-BY-DATA).

## 2. ⚠️ What the candidate book is **not**

> **It is a CERTIFIED COMPONENT SET, not an implementation of research Portfolio B.**
> B is **inverse-volatility weighted**. The integer-contract mapping that would implement it **has
> not been selected** and is an owner capital decision (`OQ-6`). **Running both legs at quantity 1
> is not that mapping and does not reproduce B's $2,012/wk economics.** Quoting B's figure for this
> book would be wrong.

## 3. Historical economics — on every window honestly measurable

| object | weekly $ at fixed $20,245 DD | positive weeks | max DD | t |
|---|---:|---:|---:|---:|
| `P1/PCT` | **$1,230** ($1,394 raw) | 56.3 % | $22,931 | 4.16 |
| Portfolio B *(research weighting, not this book)* | $2,012 | 59.2 % | $11,489 | 4.90 |

Cost model: **$4.36/ctrRT commission + modelled spread** (P1 $14.44, XM $12.50). **NT8 nets are a
different quantity** and are not interchangeable with these.

**A measurement worth recording:** `MS01` independently measured the RTH median quoted spread at
**3.000 ticks** against the frozen convention's **2.888 ticks** — agreement to 0.112 ticks, by a
completely different route. **The cost model this book is priced on holds up under independent
measurement.**

## 4. Recent-regime evidence

⚠️ **There is none yet, and that is the honest answer.** The forward pool opened **2026-08-01** and
holds ~19 sessions against a 60-session first checkpoint. **`CPA` is not due.**

**Nothing in this document is supported by post-freeze evidence.** Everything rests on the
pre-2026-08-01 record. That is a real limitation, and the fix is calendar time, not more analysis.

## 5. Risk

| | |
|---|---|
| max DD (research) | $22,931 P1 · $11,489 B |
| simultaneous exposure | both legs in market **0.9 %** of all minutes |
| opposing directions | **0.3 %** of all minutes (28.0 % of both-time) |
| max gross \|P1\|+\|XM\| | **3 contracts** · max netted **3** |
| netting changes exposure | **1.85 %** of in-market minutes |
| forward tail | **empirical bootstrap**, skew +1.888, excess kurtosis 8.717 |

> **A master allocator is NOT required for these two components** — internal crossover is 1.85 % of
> in-market minutes. ⚠️ **That result is specific to these two.** §23: it must **not** be generalised
> to a third NQ sleeve, and a high-frequency microstructure expert trading while P1/XM hold
> positions would change net exposure, crossing, duplicate commission and order sequencing. **Measure
> before adding, do not assume.**

## 6. Capital mapping

**Not selected. Owner decision (`OQ-6`).** What would have to be compared: NQ vs MNQ execution,
integer approximation of inverse-vol, capital requirement, gross exposure, margin, worst historical
stress, XM tail risk, commission drag, rounding error. **§22 says build this only after the forward
machinery is stable; it is not.**

## 7. Owner decisions outstanding

| # | decision | blocking |
|---|---|---|
| 1 | **Real-money enablement** | everything live |
| 2 | **Integer-contract capital mapping** (`OQ-6`) | any book that claims B's economics |
| 3 | **Options data purchase** | `GAMMA00` — no option surface exists in the tool set at all |
| 4 | Order-flow acquisition, **re-scoped** | now *"is a mean-scale effect on the SESSION-SCOPED target worth ~455 sessions?"*, **not** *"buy order flow?"* |

**Nothing else is blocked on you.** Microstructure modelling, multi-market substrate construction,
the internals direct-return question and shadow engineering are all runnable without spend.

## 8. What would change this document

Per §52, the next promotion most likely comes from **microstructure at 60 s** — it is the only lane
with a measured, payable friction bar and no model yet built. **If it clears 54.2 % net accuracy
under a session-block null and a same-trigger mirror control, it enters as `MICROSTRUCTURE-CURRENT`
/ `REGIME-LOCAL` at an uncertainty-aware weight — never as a structural claim on 58 sessions.**
