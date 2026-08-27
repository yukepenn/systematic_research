# ALPHA EVIDENCE CLASSIFICATION

**Authoritative for _how deep the evidence is_ behind every alpha object. 2026-08-27.**

Two axes, kept separate (§44): **LADDER STATUS** — how far a component has come — and **EVIDENCE
CLASS** — how deep the evidence behind it is. **Merging them is how a modern-window result gets
treated as a multi-era fact.**

> ## ⚠️ CORRECTION — this file's first version was wrong and is replaced
> Its first version flattened `P1/PCT`, `XM_CONFLICT_v2`, `Portfolio B` and multi-market TSMOM all
> to **STRUCTURAL**. That **contradicted `CURRENT_BASELINE`**, which already recorded the opposite
> in plain text. Caught by adversarial review before it became canonical. **The composite objects
> below now carry composite classes, and an untested prior is no longer called evidence.**

---

## Two standing rules

> ### **1. A STRUCTURAL PRIOR IS NOT STRUCTURAL EVIDENCE.**
> That a mechanism is well-supported in the literature, or economically plausible, is a **prior**.
> It says nothing about what *this repo* has measured. Until a preregistered result exists in this
> repo, the empirical class is **UNTESTED** — no matter how respectable the mechanism.

> ### **2. A COMPOSITE OBJECT INHERITS THE SHALLOWEST EVIDENCE IT DEPENDS ON.**
> A portfolio containing a modern-window-only component is **not** structural because its other leg
> has deep history. Evidence does not average; the weakest dependency binds.

**EVIDENCE CLASSES (§1):** `STRUCTURAL` · `REGIME-LOCAL` · `MICROSTRUCTURE-CURRENT` ·
`EMERGING/SHADOW` · `UNTESTED` · `FALSIFIED` · `NULL` · `CLOSED-BY-POWER` · `CLOSED-BY-DATA`.

**LADDER (§44):** `IDEA → DATA-CAPABLE → INFORMATION-SUPPORTED → AFTER-COST ALPHA-SUPPORTED →
PORTFOLIO-ADDITIVE → EXECUTABLE → PARITY-CERTIFIED → SHADOW-VALIDATED → LIVE-ELIGIBLE → LIVE-ENABLED`

---

## Register

| object | ladder status | **evidence class** | the reason, in one line |
|---|---|---|---|
| **`P1/PCT`** | **PARITY-CERTIFIED** · not live | **STRUCTURAL CORE + REGIME-LOCAL `PCT` POLICY** | the Solar/B-MOM core has deep-history support; **the `PCT` sizing layer reverses −31.4 % on 2006–2021** and 90.8 % of its gross difference lives in 53 of 1,058 sessions. **`ABS` is retained beside `PCT` in every table** |
| **`XM_CONFLICT_v2`** | **PARITY-CERTIFIED** · not live | **REGIME-LOCAL by data availability** | ES/RTY/YM substrates **begin 2022-01-02**, so no 2006–2021 test exists *or can be built*. Strong modern evidence + coherent mechanism ≠ structural evidence. N = 348, discovery-consumed |
| `Portfolio B` (P1+XM inverse-vol) | **RESEARCH ONLY** | **REGIME-LOCAL** *(inherited)* | contains XM and is measured only on the modern common window — **rule 2**. Also: **no integer-contract mapping exists** (`OQ-6`) |
| `PAIR23` | research challenger | STRUCTURAL *(economics)*, but see reason | economics stand over 16 unseen years; **`RR_W003` showed its `X9a` leg *contains* P1**, making it the most double-counted component, not the least |
| **Microstructure standalone** | **DATA-CAPABLE** | **MICROSTRUCTURE-CURRENT** | `MS01` feasibility only. **No model, no signal, no economic result.** See the gate note below |
| Multi-market TSMOM | **IDEA** | **UNTESTED** | universe inventoried (24 roots, 2016–2025). **No substrate, no roll, no signal, no backtest.** The literature's structural prior is a **prior**, not this repo's evidence — **rule 1** |
| Internals → direct RTH NQ return | **IDEA** | **UNTESTED** | not closed by `INT01` (§41) — different target, different variance |
| Internals → P1 action value | **CLOSED** | **NULL / CLOSED-BY-POWER** | `INT01`: 37.5th pctile of its own refitted null; G3 and G5 fail |
| Order flow → P1 action value | **CLOSED** | **CLOSED-BY-POWER** | needs **998 sessions; 713 exist**. Unreachable at any coverage |
| Event response | **CLOSED** | **CLOSED-BY-DATA** | underpowered on sample; **not** falsified |
| Higher-timeframe | **CLOSED** | **NULL** | `RR_W004`: negative control beat both real arms |
| NQ-path action-value information | **CLOSED** | **NULL** | `RR_W002A`: 51.0th pctile; known-null control scored higher |
| ES tick/BBO → NQ short horizon | **IDEA** | **UNTESTED** | W122's NULL was a **1-minute** family; tick-level interaction is untested |
| Options / dealer gamma | **BLOCKED** | — | **no option-chain surface exists in the tool set at all** |
| DOM / Level-II | **BLOCKED** | — | owner risk-control pause; no history exists anyway |

---

## ⚠️ `54.16 %` is a descriptive heuristic, NOT an admission gate

`MS01` derived `p* = 0.5 + friction / (2·E|move|)` → **54.16 % at 60 s**. That figure is **retired
as a promotion criterion** and survives only as a descriptive heuristic **under a stated symmetry
assumption**: it is valid only if the magnitude of correct predictions is comparable to the
magnitude of wrong ones.

**Accuracy does not determine trading P&L.** A strategy right 60 % of the time that is wrong on the
big moves loses money. **The admission object is direct executable net P&L**, built from
`Ask_t → Bid_{t+h}` for longs and `Bid_t → Ask_{t+h}` for shorts, which carries entry spread, exit
spread, spread variation, direction and magnitude automatically. Accuracy is reported as a
diagnostic only.

## What this session added to the *admitted* book: **nothing**

The session built a 780 M-event substrate, three data assets, a measured registry, an incumbent
freeze and an empirical forward protocol — and **admitted zero new alpha components**. Two mappings
closed, one lane opened with no model, one universe inventoried but not built.

**Infrastructure is not alpha**, and **negative information is progress when the experiment was
capable of succeeding** (§34).

## The standing question (§52)

> **What observation would make `P1/PCT + XM` no longer the best current book?**

1. a microstructure expert with **positive executable net P&L** at 60 s on the uniform substrate,
   surviving a session-block refitted null and a same-trigger mirror control;
2. a multi-market TSMOM book with low or negative correlation to P1 **in P1's worst decile**,
   improving fixed-DD income on the common window;
3. internals predicting **direct RTH NQ return** where they failed on P1's action value;
4. the sealed pool putting P1 below its **empirical** CPB/CPC `INVALIDATION` band.

**1–3 runnable now. 4 calendar-gated. None assumed.**

## Binding admission rules

- **Same-window comparison mandatory** (§19) — never a 98-session candidate against a 20-year headline.
- **Same-window profit insufficient** (§20) — needs subperiod stability, multiplicity-aware null,
  concentration diagnostics, realistic costs, and an **exposure/activity-matched placebo**.
- **Admission ≠ capital weight** (§21).
- **Replacement is on the table** (§47) — incumbency carries **zero** statistical privilege.
