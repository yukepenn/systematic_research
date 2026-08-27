# FROZEN INCUMBENT — 2026-08-27

> ## 🔒 **The champion definition is FIXED for forward adjudication as of 2026-08-27.**
> **This is not "forever untouchable."** A genuinely new information source, or an independently
> validated superior expert, may replace it — **through a new campaign, on new evidence, never by
> historical re-optimisation of these objects.**

> # 🔒 LIVE ENABLED: **NO.** Freezing a definition is not enabling it. Nothing is deployed,
> # started, or attached to any account. `Sim101` and every real account remain untouched.

---

## 1. What is frozen

| slot | object | status |
|---|---|---|
| **A** RESEARCH_SINGLE | `P1/PCT` | frozen |
| **B** RESEARCH_PORTFOLIO_FRONTIER | `{P1/PCT + XM_CONFLICT}` **inverse-vol** | frozen **as a research weighting convention** |
| **C** EXECUTABLE_SINGLE | `WeeklyEdgeP1PCT_v1` | frozen · PARITY-CERTIFIED · **NOT ENABLED** |
| **D** EXECUTABLE_COMPONENT_SET | `WeeklyEdgeP1PCT_v1` + `WeeklyEdgeXMConflict_v2` | frozen · both legs certified · **NOT ENABLED** |

⚠️ **D is a certified component set, NOT an executable implementation of B.** B is inverse-vol
weighted; the integer-contract mapping that would implement it **has not been selected** and is an
owner capital decision (`OQ-6`). Running both legs at quantity 1 is **not** that mapping and does
**not** reproduce B's economics. **This freeze does not resolve that and must not be read as doing so.**

## 2. Source hashes — verified at freeze time, repo against installed

| object | sha256[0:16] | repo == installed | certified at |
|---|---|---|---|
| `WeeklyEdgeP1PCT_v1` | **`ee4c765bc5cab230`** | ✅ verified 2026-08-27 | `fc8cf85` |
| `WeeklyEdgeXMConflict_v2` | **`2ec00dd4d0a11b99`** | ✅ verified 2026-08-27 | `fc8cf85` |

`WeeklyEdgeXMConflict_v1` is **SUPERSEDED and must not be run.** It armed on early-close holidays
the research object silently drops — 15 trades at **−$225/trade**. It is retained in the repo **as
the evidence**, not as a candidate.

> **Neither class may be renamed.** `CLAUDE.md` §6: never rename a class that has been
> parity-certified. Any functional change requires a **new** class name and a **new** parity run.

## 3. Environment — the configuration these hashes were certified against

```
NinjaTrader        8.1.8.1
CrossTrade add-on  v1.13.9
engine             nt8_strategy_analyzer   fingerprint sha256:b4255f1b0dd7fba1
account            Backtest (isolated, reset per run)
instrument         NQ 09-26  (resolves NQU6)
bars               1-Minute, Last
trading hours      CME US Index Futures ETH
commission         NinjaTrader Brokerage Lifetime   ($4.36 / contract round turn)
fill               Standard, slippage 0 ticks
from               2022-01-03T00:00:00Z   (2022-01 → 06 is warm-up only)
to                 2026-07-31T21:59:59Z   (one second before the next 18:00 ET open)
XM secondaries     ES 09-26 · RTY 09-26 · YM 09-26   — FIXED ORDER, part of the freeze
```

## 4. Signal and session semantics — frozen

- **`P1/PCT` is LONG-ONLY.** `p == −1` on **0.00 %** of bars. A short sleeve is not part of this
  object and its absence is **design, not omission** (`RR_W006`).
- **Bars are END-stamped** in both substrates. The bar stamped 09:31 opens at 09:30:00. There is
  **no ±1-minute shift**; applying one *was* the original W52 phase error.
- **Session boundary:** `to` is one second before the **next** 18:00 ET open — never "end of day D".
- **Two path-dependence channels, one-way, frozen as such:** the session box latch changes the
  **schedule** within a session; the `causal_score` trailing-250-entry window changes **size** across
  sessions. Under `per_ctr=True` the box accumulates `pnl/u`, which contains no `u`, so the schedule
  is **size-invariant** and there is no fixed point.
- **Session box:** −$1,300 / +$1,000 **per contract**. `RR_W005` measured every uniform relaxation as
  **16–41 % worse at fixed drawdown** with 11–26 % more exposure. **The box is frozen.**

## 5. Cost model — frozen, and the two are not interchangeable

| | research | NT8 |
|---|---|---|
| commission | $4.36 / ctrRT | $4.36 / ctrRT (Lifetime template) |
| spread | **modelled, candidate-specific** — P1 **$14.44**, XM **$12.50** per ctrRT | **none**, slippage 0 ticks |

⚠️ **A research headline and an NT8 net are different quantities.** Parity is measured
**commission-only on both sides**. $14.44/ctrRT is 2.888 NQ ticks round turn — not an integer per
side — so it is deliberately **not** pushed into NT8's `slippage_ticks`.

**Every weekly figure is quoted at a fixed $20,245 max drawdown**, which is algebraically
scale-invariant and therefore cannot be inflated by leverage.

## 6. Frozen reference values — the numbers forward evidence is measured against

| object | weekly $ at fixed DD | positive weeks | max DD | t |
|---|---:|---:|---:|---:|
| **A** `P1/PCT` | ⚠️ **$1,166** ($1,394 raw) | 56.3 % | **$24,213** | 4.16 |
| **B** `{P1/PCT + XM}` inverse-vol | ⚠️ **$2,012 SUSPECT — unaudited** | 59.2 % | $11,489 | 4.90 |

> ### ⚠️ **AMENDED 2026-08-27 — the freeze is RE-STAMPED, not broken.**
> `runs/FWD_DD_RECONCILIATION/` found the canonical **$22,931** drawdown was computed on a **commission-only**
> stream while the **$1,394** numerator is **net of the modelled spread**. A weekly curve is a
> subsample of the daily one, so its drawdown **cannot exceed** it — yet $22,931 sits *below*
> the weekly $24,212.92, which is impossible for one stream. Mixing the two cost models
> **flattered the fixed-DD headline by 5.2 %**.
>
> **Corrected: `k = 20,245 / 24,212.92 = 0.836124`, giving `$1,166/wk`.** The **source hashes,
> parameters, cost model and semantics are UNCHANGED** — only a derived reporting figure was
> wrong. **The seal was not read**, so this is legal **pre-read defect repair** (§29), not
> outcome-driven retuning.

Parity evidence, frozen as the executable claim:

- `WeeklyEdgeP1PCT_v1` — 2,131 Python vs **2,137** NT8 trades (+0.28 %), matched rate **99.672 %**,
  weekly ρ **0.9852**, **1,908 of 2,124 matched trades reproduce to $0.00**.
- `WeeklyEdgeXMConflict_v2` — `desired_direction` **99.715 %**, 347 vs 346 trades (+0.29 %),
  `broad_composite` max |diff| **0.000000**.

## 7. What this freeze forbids, and what it does not

**Forbidden while frozen**

- changing any parameter, threshold, window, weight or cost assumption **on historical evidence**
- re-optimising, re-fitting, re-tuning, or "improving" either object
- renaming either certified class
- reading the ≥ 2026-08-01 seal outside `WEEKLY_EDGE_FORWARD_PROTOCOL.md`
- treating a forward wobble as a reason to retune — see the protocol's explicit non-triggers

**Still permitted**

- **measuring** these objects against new information (that is the whole point of the freeze)
- building **new, independent** experts and judging them on **marginal portfolio value**
- fixing an outright **defect** — a genuine implementation bug, not a preference — which requires a
  new class name, a new parity run, and an entry here recording what was wrong

## 8. Pointers

`research/operational/EXECUTION_MANIFEST.md` (execution truth) ·
`research/weekly_edge/CURRENT_BASELINE.md` (research truth) ·
`research/weekly_edge/WEEKLY_EDGE_FORWARD_PROTOCOL.md` (how the seal gets read) ·
`research/operational/LOCKED_FORWARD.md` (seal register)
