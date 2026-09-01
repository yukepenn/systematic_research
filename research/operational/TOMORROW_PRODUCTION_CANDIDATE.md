# TOMORROW PRODUCTION CANDIDATE — 2026-08-27

> # 🔴 **SUPERSEDED 2026-09-01 — the future this document plans for has arrived.**
> Its §5 decisions **1 (real-money enablement)** and **2 (integer-contract capital mapping)** are
> both **CLOSED**: `M_11` was owner-ratified 2026-08-30, and the book went live on account
> `2047681` on 2026-09-01 at `MnqPerNq = 3` (0.30 NQ-equivalent, MNQ execution).
> **Current answer: [`research/operational/CURRENT_LIVE_TRUTH.md`](CURRENT_LIVE_TRUTH.md).**
> §2's Panel A economics and §4's risk table are measurements and remain valid.
>
> _Written 2026-08-27. It answered "what is ready?". It authorised nothing then, and nothing now._

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

**MS-BBO** (discovery-grade only; no clean historical holdout exists) · multi-market **carry / term structure** (substrate built, family not opened) · **ES/NQ sub-minute interaction** (capability unmeasured)
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

Fixed standard windows, declared before computing. Scaled at the canonical **`k = 0.882879`**, on the `WE_W103`/`WE_W110` ISO-week series.
Source: `runs/RECENT_REGIME_PANEL_20260827/`.

| object | window | mean $/wk | positive wks | t |
|---|---|---:|---:|---:|
| **`P1/PCT`** | **last 13w** | **−$294** | **30.8 %** | **−0.24** |
| | last 26w | $495 | 53.8 % | 0.59 |
| | last 52w | $1,116 | 55.8 % | 1.90 |
| | last 104w | $1,713 | 56.7 % | 3.29 |
| | FULL 213w | **$1,230** | 56.3 % | 4.16 |
| **`XM`** | last 13w | $507 | 53.8 % | 0.31 |
| | last 26w | $1,557 | 53.8 % | 1.42 |
| | FULL 213w | $808 | 48.8 % | 3.05 |
| **P1+XM** *(unweighted sum, NOT Portfolio B)* | last 13w | $213 | 30.8 % | 0.09 |
| | FULL 213w | $2,039 | 59.6 % | 4.94 |

**Validation:** the FULL P1 row reproduces the canonical baseline **$1,230 / 56.3 % / t 4.16** exactly.

> ### ⚠️ **The incumbent's recent-regime evidence is WEAK, and this is the honest reading.**
> `P1/PCT` is **negative over the last 13 weeks** and its trailing mean **declines monotonically as
> the window shortens** — $1,713 (104w) → $1,116 (52w) → $495 (26w) → −$294 (13w). That is the
> shape of decay, or of normal variation, and **13 weeks cannot distinguish them** (the forward
> protocol puts P(losing quarter) at 13.9 % with nothing wrong — `FWD_BOOTSTRAP_V2`).
>
> **It is recorded here rather than omitted**, and it is **not** a trigger: §5 of the forward
> protocol makes a negative quarter an explicit NON-trigger.

> ### ⚠️ **The diversification argument has deteriorated in the current regime.**
> | window | ρ(P1, XM) | mean XM **when P1 loses** |
> |---|---:|---:|
> | FULL | **+0.081** | **+$622** |
> | last 104w | +0.193 | −$34 |
> | last 52w | +0.258 | −$321 |
> | last 26w | **+0.464** | **−$1,231** |
> | last 13w | +0.369 | **−$1,243** |
>
> XM's role in the book was to pay *when P1 does not*. **Over the full record it does (+$622). Over
> the last year it does the opposite.** Correlation has risen roughly 4× and the conditional payoff
> has flipped sign. **This directly weakens Portfolio B's rationale in the current regime** and must
> be carried into any capital decision.

**Concentration is severe recently:** P1's last-26w net is **88.1 % from one week**, and its top-5
weeks are **276.7 %** of net — i.e. everything else is negative. XM's last-26w top-1 is 31.0 %.

### One number I could not reproduce
The review quoted XM's last ~14 weeks as *~$499/wk, **35.7 %** positive, t ~0.25*. I measure
**$507/wk, 53.8 % positive, t 0.31** over 13 weeks. **Mean and t agree; the positive-week rate does
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
| max DD (research) | **$22,931** P1 · $11,489 B · ⚠️ both are **ISO-week** figures; a Sunday-ending label gives P1 **$24,213 (+5.6 %)** |
| both legs in market | **0.9 %** of all minutes · opposing directions **0.3 %** |
| max gross / netted | **3 / 3 contracts** · netting changes exposure on **1.85 %** of in-market minutes |
| forward tail | empirical bootstrap: skew **+1.888**, excess kurtosis **8.717** |

> **A master allocator is NOT required for these two** (crossover 1.85 %). ⚠️ **That is specific to
> these two** (§23–24) and must not be generalised to a third, high-frequency NQ sleeve.

✅ **No defect.** A claimed cost-model defect was **retracted the same day** — the canonical pair is
internally consistent. ⚠️ **Portfolio B's $2,012 is now QUANTIFIED, not merely cautioned** (`runs/PORTFOLIO_B_RECONCILIATION_20260827/`): it reproduces to **0.000000**, its causal-weighting optimism is only **$28.30/wk (1.4 %)**, but its **observable best-of-six selection optimism is $245.71/wk (13.9 %)**. **The historical $2,012 object stands as what it is — a selected, in-sample-weighted research figure. The honest forward-economic expectation is nearer $1,750–1,800/wk**, and it still inherits XM's REGIME-LOCAL evidence class.

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
