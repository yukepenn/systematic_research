# EXECUTION_MANIFEST — what is actually installed and executable

_Authoritative for **execution** truth. Created 2026-08-27 (operational reset §28)._
_`research/weekly_edge/CURRENT_BASELINE.md` answers "what does research support?"_
_**This file answers "what exactly is installed and reproducible?"** They are different questions._

> # 🔒 LIVE ENABLED: **NO** — for every object below, without exception.
> **No live order authorization exists.** Nothing is deployed, started, or attached to any account.
> Every backtest here ran on NinjaTrader's isolated **Backtest** scratch account. `Sim101` and all
> real accounts were never touched.

## Environment

| | |
|---|---|
| NinjaTrader | **8.1.8.1** |
| CrossTrade add-on | **v1.13.9** · features `[compile, strategy_state, alert_relay, backtest]` |
| engine | `nt8_strategy_analyzer`, fingerprint `sha256:b4255f1b0dd7fba1` |
| account | `Backtest` (isolated, reset per run) |
| NT8 strategies folder | `C:\Users\Yuke Zhang\Documents\NinjaTrader 8\bin\Custom\Strategies` |

## The four baselines

| | baseline | object | status |
|---|---|---|---|
| **A** | RESEARCH_SINGLE | `P1/PCT` | research object — see `CURRENT_BASELINE.md` §0 |
| **B** | RESEARCH_PORTFOLIO_FRONTIER | `{P1/PCT + XM_CONFLICT}` inverse-vol | research object — see `CURRENT_BASELINE.md` §0 |
| **C** | **EXECUTABLE_SINGLE** | **`WeeklyEdgeP1PCT_v1`** | **EXECUTABLE · PARITY-CERTIFIED · NOT ENABLED** |
| **D** | **EXECUTABLE_COMPONENT_SET** | **`WeeklyEdgeP1PCT_v1` + `WeeklyEdgeXMConflict_v2`** | **both legs individually PARITY-CERTIFIED · NOT ENABLED** — a component set, **not** an executable implementation of B |

## Certified objects

### `WeeklyEdgeP1PCT_v1` — executable single baseline

| | |
|---|---|
| repo source | `research/weekly_edge/ninjascript/WeeklyEdgeP1PCT_v1.cs` |
| sha256[0:16] | `ee4c765bc5cab230` (installed copy **verified identical**) |
| git | certified at `fc8cf85` |
| compile | ✅ resolves as `NinjaTrader.NinjaScript.Strategies.WeeklyEdgeP1PCT_v1` |
| parity | ✅ **CERTIFIED** — `runs/WE_P1PCT_PARITY_20260827/` |
| result | 2,131 Python vs **2,137** NT8 trades (+0.28 %) · net −1.05 % · matched rate 99.672 % · weekly ρ **0.9852** · **1,908 of 2,124 matched trades reproduce to $0.00** |
| comparator | `WeeklyEdgeP1_v3` (§18 control) — keep installed |

### `WeeklyEdgeXMConflict_v2` — active portfolio component

| | |
|---|---|
| repo source | `research/weekly_edge/ninjascript/WeeklyEdgeXMConflict_v2.cs` |
| sha256[0:16] | `2ec00dd4d0a11b99` (installed copy **verified identical**) |
| git | certified at `fc8cf85` |
| compile | ✅ resolves; NT8 auto-compiled the dropped file, no F5 |
| parity | ✅ **VALIDATED** — `runs/WE_XM_PARITY_20260827/` |
| result | `desired_direction` **99.715 %** · 347 vs 346 trades (+0.29 %) · `broad_composite` max \|diff\| **0.000000** |
| series | primary **NQ 09-26**; secondaries in fixed order **ES 09-26 · RTY 09-26 · YM 09-26** |
| **`v1` is SUPERSEDED** | it armed on early-close holidays the research object drops (15 trades, −$225/trade). Retained in repo as the evidence; **must not be run** |

## Analyzer settings — the exact reproducible configuration

```
instrument       NQ 09-26            (resolves NQU6)
bars             1-Minute, Last
trading hours    CME US Index Futures ETH
commission       NinjaTrader Brokerage Lifetime      ($4.36 / contract round turn)
fill             Standard, slippage 0 ticks
account          Backtest (isolated, reset)
from             2022-01-03T00:00:00Z                (2022-01 → 06 is warm-up only)
to               2026-07-31T21:59:59Z                (one second before the next 18:00 ET open)
```

`to` stops **strictly before** the ≥ 2026-08-01 VIRGIN seal. **No sealed data has been touched.**

> ### ⚠️ Cost models differ and the numbers are not interchangeable
> Research charges $4.36/ctrRT commission **plus** a modelled spread (P1 **$14.44**, XM **$12.50**
> per ctrRT). NinjaTrader charges the commission template and **zero** slippage. Parity is measured
> **commission-only on both sides**. Putting a research weekly figure beside an NT8 net compares two
> different cost models. $14.44/ctrRT is 2.888 NQ ticks round turn — not an integer per side — so it
> is deliberately **not** pushed into NT8's `slippage_ticks`.

## Portfolio execution semantics (§26) — measured, not assumed

Both legs on one account, 2022-07 → 2026-08 at minute resolution:

| | |
|---|---|
| minutes P1/PCT in market | 187,010 (8.7 %) |
| minutes XM in market | 125,883 (5.9 %) |
| **both in market simultaneously** | 19,361 — **0.9 %** of all minutes, 15.4 % of XM's time |
| **holding opposing directions** | 5,418 — **0.3 %** of all minutes, 28.0 % of both-time |
| max gross \|P1\|+\|XM\| | **3 contracts** |
| max netted \|P1+XM\| | **3 contracts** |
| netted position distribution | −1: 57,290 · 0: 1,858,861 · +1: 170,752 · +2: 56,740 · +3: 4,838 |
| **minutes where netting changes gross exposure** | **5,418 = 1.85 % of in-market minutes** |

> ### **A master strategy is NOT required.** Internal crossover is 1.85 % of in-market minutes and
> peak exposure is 3 contracts netted or gross — netting never *raises* exposure. Two ordinary NT8
> strategies on one account is sufficient.
>
> ⚠️ **But two things must be understood before any forward run.** (1) On those 5,418 minutes each
> strategy believes it holds its own position while the *account* holds the net — margin and
> account-level position differ from either strategy's view. (2) **Both legs pay their own
> commission even when their fills net**; that duplicate cost is already inside each certified
> backtest, so it is priced, not missing.

### ⚠️ Weighting — why D is a COMPONENT SET and not portfolio B

Baseline B is the **inverse-volatility** research weighting. The certified executable legs are each
**quantity 1** (P1/PCT additionally sizes 2 on ~20 % of entries via its own causal quality layer).

> ### **Running both legs at their default quantity 1 is NOT an implementation of B and does NOT
> ### reproduce B's economics.**
> B's **$2,012/wk at fixed $20,245 DD** is a *research* figure computed under **inverse-vol weights**
> and the **research cost model** (commission **plus** modelled spread). A 1 + 1 contract book is a
> different allocation under a different cost model, and quoting B's number for it would be wrong in
> both directions at once.
>
> **What IS established:** each leg reproduces its own research object inside NinjaTrader. **What is
> NOT established:** any executable allocation that reproduces the portfolio.

**The research weighting has not been silently changed.** Mapping inverse-vol weights onto integer
contract counts is an open **owner capital-allocation decision**, and no such mapping is asserted
anywhere in this repo. Until it is selected, **`EXECUTABLE_PORTFOLIO` proper remains PENDING** and
what exists is the certified component set above.

## Active NT8 strategy set

**Keep active (4):** `WeeklyEdgeP1PCT_v1` · `WeeklyEdgeXMConflict_v2` · `WeeklyEdgeP1_v3`
(comparator, §38) · `@Sample*` (NT8 built-ins, not ours).
Full inventory and removals: `research/operational/REPO_CONSOLIDATION_20260827.md`.

## Forward logging — not yet started

No forward SIM run has occurred, so no forward ledger rows exist. **Historical backtest rows must
never be backfilled into a forward ledger.** Before any forward run, record: strategy version +
sha256, git hash, instrument, account, every parameter, session template, quantity, risk settings.

## Not certified / not installed

`WeeklyEdgeBmom_v1.cs`, `WeeklyEdgeX9a_v1.cs`, `WeeklyEdgeP1_v1.cs`, `WeeklyEdgeP1_v2.cs` — repo
sources only. Campaign-#3 historical shipped objects (`SolarWaveSMMaster_v4`,
`SolarWaveOneContractNQ_v5`, `SolarWaveOneContractMNQ_v5`) are documented in
`research/archive/campaign3_system_master/BASELINE_MODELS.md`; they are **not** part of campaign #7
and are not in the active NT8 set.
