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
| **`MS-LAST-V1`** | **CLOSED at its own scope** | **FALSIFIED-NULL-CLOSED** *(narrow)* | certified order-invariant Last-only family + 60 s + frozen Ridge/GBM budget + frozen policy/cost. Refitted session-block null not beaten (1.0th pctile); upper 95 % bound −$569/session rules out a $49/session materiality declared in advance. ⚠️ **Does NOT close Last-only alpha generally, other horizons, other feature classes, or 60 s predictability as such** · `runs/MSLAST_CONTRACT_20260827/` |
| **`MS-BBO-CANDIDATE-1`** | **CANDIDATE — FROZEN** | **DISCOVERY-GRADE ONLY** | 7/7 preregistered gates + 4/4 leak probes (timestamps, mismatched execution, ablation, staleness). $5,125/session, t 6.76, OOF corr **0.170**, stress-positive to +1.0 tk/side. ⚠️ **48 consumed sessions; no clean BBO holdout exists or can be built, so prospective shadow is its ONLY remaining test** · `runs/MSBBO_V1_20260828/` |
| **`P1/ABS`** | **PROSPECTIVE CHALLENGER** | **BURNED / DISCOVERY-CONSUMED** | PCT ahead in every fixed window and the mechanism is isolated (`ABS_LOOSE` control, p 0.940), but the paired **magnitude** test is p 0.058. Direction overwhelming, dollars not established. Forward data decides · `runs/ABS_PCT_ADJUDICATION_20260827/` |
| **TSMOM (all roles)** | **CLOSED** | **VALIDATION- AND HOLDOUT-CONSUMED** | steady-premium failed (V2-G3); tail-diversifier failed (H1, 4 of 5). ρ = 0.013 but no return — **ballast, not a hedge**. Carry/term structure remains a **separate untested family** |
| **Multi-market TSMOM V1** | **CLOSED — GATES FAILED** | **DEVELOPMENT-ONLY, DISCOVERY-CONSUMED** | substrate, causal roll and basis-safe P&L now EXIST and passed their unit tests; V1 then **failed 3 of 6 preregistered DEVELOPMENT gates** (Sharpe 0.226, 5/9 positive years, 72.3 % equity concentration). Cost drag **47.2 % of gross**, scale-invariant. VALIDATION and FINAL HOLDOUT **unread** · `research/multi_market/TSMOM_V1_DEVELOPMENT.md` |
| **TSMOM V2 (252d slow trend)** | **CLOSED — FAILED VALIDATION** | **VALIDATION-CONSUMED** | failed preregistered **G3** (2 of 4 positive years); **5 of 6 gates passed** (net $15,080, Sharpe 0.577, stress positive, low concentration). 2020 and 2022 carry everything; both calm years lose. **The STEADY-PREMIUM claim is CLOSED at this specification.** 2019–2022 consumed; **2023–2026 TSMOM outcomes unspent** · `runs/TSMOM_V2_SLOWTREND_20260827/` |
| **`INT02` internals → direct RTH NQ return** | **CLOSED — NO CANDIDATE** | **NO DETECTED SIGNAL** *(partial)* | all 4 gates fail; ridge −$66.73/session, directional accuracy **49.5 %**, 66.7th pctile of a real refitted null. ⚠️ **A strong-materiality ($246/session) effect is closed; a WEAK $49/session effect is NOT** — upper 95 % bound **+$68.16**. Other mappings, horizons and feature classes untested · `runs/INT02_DIRECT_RTH_20260827/` |
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
