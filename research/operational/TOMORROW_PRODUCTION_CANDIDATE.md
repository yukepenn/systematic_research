# TOMORROW PRODUCTION CANDIDATE — 2026-08-27

> # 🔒 **LIVE ENABLED: NO.** This document answers *"what is ready?"*. It authorises nothing.
> Real-money enablement is **owner-only** and is not requested here.

**The question (§22):** *if real trading had to start with the strongest defensible book using
information available today, what exactly would it contain?*

---

## The answer

> ### **`P1/PCT` + `XM_CONFLICT_v2` — the CURRENT PARITY-CERTIFIED INCUMBENT COMPONENT SET.**
> ### **Nothing discovered today earned admission.** Closing questions and building substrate is
> ### not the same as producing a component. §22: *do not force inclusion just because a component exists.*

### ⚠️ Component set ≠ fully specified executable portfolio (§32)

| | |
|---|---|
| **CURRENT PARITY-CERTIFIED INCUMBENT COMPONENT SET** | ✅ two objects, each independently reproducing its research decisions. ⚠️ **Parity proves IMPLEMENTATION REPRODUCTION, not forward alpha validity** |
| **FULLY SPECIFIED EXECUTABLE PORTFOLIO** | ❌ **PENDING OWNER ALLOCATION** — no integer-contract mapping exists (`OQ-6`) |

**Do not quote Portfolio B's $2,012/wk for any unspecified P1+XM quantity combination.** B is
inverse-volatility weighted; running both legs at quantity 1 is a *different object*.

## 1. Layers

### CORE — parity-certified

| component | evidence class | frozen hash | parity |
|---|---|---|---|
| **`WeeklyEdgeP1PCT_v1`** | **STRUCTURAL CORE + REGIME-LOCAL `PCT` policy** | `ee4c765bc5cab230` | 2,131 vs 2,137 trades (+0.28 %), matched 99.672 %, **1,908 of 2,124 matched trades to $0.00** |
| **`WeeklyEdgeXMConflict_v2`** | **REGIME-LOCAL by data availability** | `2ec00dd4d0a11b99` | direction 99.715 %, composite max\|diff\| **0.000000** |

⚠️ Neither is `STRUCTURAL` as a whole. `PCT` **reverses −31.4 % on 2006–2021**; XM's ES/RTY/YM
substrates **begin 2022-01-02**, so no earlier test exists *or can be built*.

### EXPERIMENTAL — research-supported, not admissible

Microstructure standalone (`MS01` feasibility only — **no model exists**) · Multi-market TSMOM
(universe inventoried; **no substrate, roll, signal or result**) · Internals → direct RTH return
(untested).

### SHADOW ONLY — **empty**. No component has execution evidence short of parity, and the shadow
ledger is prospective-only and is not back-filled.

### CLOSED — `internals → P1 routing` (NULL) · `order flow → P1 action value` (CLOSED-BY-POWER) ·
`higher-timeframe` (NULL) · `NQ-path action-value information` (NULL) · `event response` (CLOSED-BY-DATA).

## 2. ⚠️ PANEL A — RECENT HISTORICAL evidence (BURNED, but still evidence)

The previous version of this document said *"recent-regime evidence: there is none."* **That was
wrong in scope.** There is substantial recent evidence; it is `DISCOVERY_CONSUMED` / `BURNED`
rather than clean prospective confirmation. **`RECENT ≠ FORWARD`, and burned current-regime
evidence is still evidence.**

Fixed standard windows, declared before computing. Scaled at the **corrected `k = 0.836124`** (`runs/FWD_DD_RECONCILIATION/`).
Source: `runs/RECENT_REGIME_PANEL_20260827/`.

| object | window | mean $/wk | positive wks | t |
|---|---|---:|---:|---:|
| **`P1/PCT`** | **last 13w** | **−$241** | **38.5 %** | **−0.19** |
| | last 26w | $508 | 50.0 % | 0.54 |
| | last 52w | $1,054 | 51.9 % | 1.73 |
| | last 104w | $1,618 | 56.7 % | 3.27 |
| | FULL 213w | **$1,166** | 57.7 % | 4.17 |
| **`XM`** | last 13w | $480 | 53.8 % | 0.31 |
| | last 26w | $1,474 | 53.8 % | 1.42 |
| | FULL 213w | $784 | 48.8 % | 3.13 |
| **P1+XM** *(unweighted sum, NOT Portfolio B)* | last 13w | $239 | 38.5 % | 0.10 |
| | FULL 213w | $1,950 | 60.1 % | 4.96 |

**Two validations:** the FULL P1 row reproduces the **corrected** baseline **$1,166 / t 4.16**, and
XM's full total scales back to **$199,760 raw**, reproducing the independently corrected
**$199,766** ($577.36/trade × 346).

> ### ⚠️ **The incumbent's recent-regime evidence is WEAK, and this is the honest reading.**
> `P1/PCT` is **negative over the last 13 weeks** and its trailing mean **declines monotonically as
> the window shortens** — $1,618 (104w) → $1,054 (52w) → $508 (26w) → −$241 (13w). That is the
> shape of decay, or of normal variation, and **13 weeks cannot distinguish them** (the forward
> protocol puts P(losing quarter) at 14.5 % with nothing wrong).
>
> **It is recorded here rather than omitted**, and it is **not** a trigger: §5 of the forward
> protocol makes a negative quarter an explicit NON-trigger.

> ### ⚠️ **The diversification argument has deteriorated in the current regime.**
> | window | ρ(P1, XM) | mean XM **when P1 loses** |
> |---|---:|---:|
> | FULL | **+0.098** | **+$569** |
> | last 104w | +0.198 | −$205 |
> | last 52w | +0.268 | −$548 |
> | last 26w | +0.410 | −$586 |
> | last 13w | **+0.393** | **−$1,368** |
>
> XM's role in the book was to pay *when P1 does not*. **Over the full record it does (+$569). Over
> the last year it does the opposite.** Correlation has risen roughly 4× and the conditional payoff
> has flipped sign. **This directly weakens Portfolio B's rationale in the current regime** and must
> be carried into any capital decision.

**Concentration is severe recently:** P1's last-26w net is **92.8 % from one week**, and its top-5
weeks are **293.6 %** of net — i.e. everything else is negative. XM's last-26w top-1 is 31.0 %.

### One number I could not reproduce
The review quoted XM's last ~14 weeks as *~$499/wk, **35.7 %** positive, t ~0.25*. I measure
**$480/wk, 53.8 % positive, t 0.31** over 13 weeks (at the corrected `k`; $507 at the old one). **Mean and t agree; the positive-week rate does
not.** My convention counts XM's silent weeks as **$0** (non-positive) rather than dropping them —
dropping them would condition on having traded and inflate both statistics. The residual gap is
likely window length (13 vs 14) or a different silent-week convention. **Flagged, not reconciled.**

## 3. PANEL B — PROSPECTIVE / POST-FREEZE evidence

> ### **NONE YET**, and no analysis can create it.
The seal opened **2026-08-01** and holds **~19 sessions** against a **60-session** CPA trigger.
**This is the only clean prospective evidence and it is calendar-gated.** Panel A was fully
available while these objects were being built and cannot be upgraded into confirmation.

## 4. Risk

| | |
|---|---|
| max DD (research) | **$24,213 P1 (corrected)** · ⚠️ $11,489 B **SUSPECT, unaudited** |
| both legs in market | **0.9 %** of all minutes · opposing directions **0.3 %** |
| max gross / netted | **3 / 3 contracts** · netting changes exposure on **1.85 %** of in-market minutes |
| forward tail | empirical bootstrap: skew **+1.888**, excess kurtosis **8.717** |

> **A master allocator is NOT required for these two** (crossover 1.85 %). ⚠️ **That is specific to
> these two** (§23–24) and must not be generalised to a third, high-frequency NQ sleeve.

✅ **Defect CLOSED.** `runs/FWD_DD_RECONCILIATION/` established the canonical $22,931 was a **commission-only** drawdown
while the numerator is **net of the modelled spread**. Corrected to `k = 0.836124` → **$1,166/wk**.
⚠️ **Portfolio B was NOT audited and remains SUSPECT.**

## 5. Owner decisions outstanding

| # | decision |
|---|---|
| 1 | **Real-money enablement** |
| 2 | **Integer-contract capital mapping** (`OQ-6`) — a sensitivity menu is being prepared, not chosen |
| 3 | **Options data purchase** — no option surface exists in the tool set at all |
| 4 | Order-flow acquisition, **re-scoped**: *"is a mean-scale effect on the SESSION-SCOPED target worth ~455 sessions?"* |

**Nothing else is blocked on you.**

## 6. What would change this document

The next promotion most likely comes from **microstructure at 60 s** — the only lane with measured,
payable friction and no model built. **Admission is on direct executable net P&L**
(`Ask_t → Bid_{t+h}` long, `Bid_t → Ask_{t+h}` short), **not on directional accuracy**: the
`54.16 %` figure is a descriptive heuristic under a symmetry assumption and is **retired as a gate**.
If it earns admission it enters as `MICROSTRUCTURE-CURRENT` at an uncertainty-aware weight — never
as a structural claim on ~99 sessions.
