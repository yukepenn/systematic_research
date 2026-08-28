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
| **`MS-BBO-CANDIDATE-1`** | ⛔ **VOID** | **FALSIFIED — LOOK-AHEAD** | ⚠️ **CORRECTED 2026-08-28. This row previously read "CANDIDATE — FROZEN / DISCOVERY-GRADE ONLY, 7/7 gates + 4/4 leak probes, $5,125/session, t 6.76". All of it is void.** `np.arange(-30,0) * NS` overflows **int32**, so 15 of 30 feature offsets were **positive** — features read up to **+2.065 s after the decision instant**. The leak was **134.8 %** of the result; the causal object earns **−$1,785.88/session, OOF corr 0.0072**. **Not repaired in place** (§12): a corrected definition is a new object on consumed data · `runs/MSBBO_DEPLOYMENT_FREEZE_20260828/` |
| **`CARRY_V1`** (curve/term structure) | **CLOSED — GATES FAILED** | **DEVELOPMENT-ONLY, DISCOVERY-CONSUMED** | 6 of 8 gates passed (net $71,413, Sharpe 0.719, 7/9 positive years, cost drag 7.9 %, two-sided causality clean) but **C6 84.1 %** and **C7 98.5 %** fail: the result is **SI alone**. ⚠️ **Does NOT close curve information generally** — one frozen object, one universe, and `n_sector = 2` degenerates the rank to ±1 in three of four sectors. **2019–2022 and 2023–2026-05-30 NEVER READ** · `runs/CARRY_V1_20260828/` |
| Curve **data capability** | **DATA-CAPABLE** | **measured, no alpha** | `CARRY00`: 11 roots, 4 of 6 sectors. **FX closed-by-data** (deferred listed for only 33–39 % of the near's life); RTY/RB/HO/HG **closed-by-cache**, recoverable free · `runs/CARRY00_CURVE_DATA_CAPABILITY_20260828/` |
| **ES ↔ NQ sub-minute** | **PREREGISTERED — EXPORT-GATED** | **runnable, blind-confirmable** | ⚠️ **CORRECTED 2026-08-28 (later): the *incremental* question is void with its baseline, and has been RE-POSED as a CROSS-MARKET question** — a single-instrument null says nothing about information transfer between two contracts. **59 overlapping RTH-complete sessions; 44 development (substrate BUILT) + blind confirmation at EFFECTIVE n = 14** after the pre-outcome operational quarantine of `2025-08-13` (original frozen manifest 15, preserved byte-for-byte). **`CROSS_MARKET_ES_EMBARGO = 200 ms`, frozen and unsearchable.** 11 relative-by-construction features; ONE Ridge, zero challengers; the `MS-BBO-V1` feature set is **forbidden**. Pre-candidate gates now include **independent streaming parity at 100 % action agreement** · `runs/ESNQ_V1_20260828/SPEC.md` |
| **`BBO_BLIND_POOL` (19 sessions)** | **FROZEN ASSET** | **BLIND HISTORICAL — FALSIFIER-GRADE** | **19 outcome-unconsumed RTH-complete pre-seal NQ BBO sessions — of which 18 pristine-never-materialized and 1 (`2025-08-13`) METADATA-EXPOSED** (its NQ CSV was transiently written and deleted unread in the exporter incident; no outcome status changes because metadata was exposed), **ELIGIBILITY RULE FROZEN AT `022c543`** (tree contains only `SPEC.md`), **REALIZED MANIFEST FIRST MATERIALIZED AND HASH-FROZEN AT `17bbb2d`**; normalized-content sha256 `92010fc6…2b8e` (the as-recorded `84a8575a…` was the CRLF working-tree hash — same content). **Returns NOT read**. The 99-vs-123 gap was **entirely a definition difference** (97 both · 19 RTH-only · 2 full-session-only) and the old "no pool exists" verdict was **correct under its own 23-hour criterion**. ⚠️ **MDE $2,996/session at n=19 — it can FALSIFY a large claim at 5.7 σ and cannot CONFIRM a modest one.** Governance: a genuinely different mechanism, frozen without reading it, one shot · `runs/BBO_COMPLETENESS_RECENSUS_V1_20260828/` |
| **ES BBO price-side (64 sessions)** | **UNREAD ASSET** | **ZERO OUTCOME-CONSUMED** | the largest fully-unread quote-bearing asset the project owns; the only code that has ever touched it reads file names, not prices. ⚠️ **Low prior as a standalone lane** — it is the same hypothesis class that returned corr 0.0072 on NQ in the same market structure · `runs/ASSET_CENSUS_20260828/` |
| **Multi-market VOLUME / liquidity** | **IDEA** | **PERMANENTLY DISCOVERY-GRADE** | volume is in every `.ncd` record and has only ever been the roll criterion — genuinely different surface, but on **outcome-consumed dates**, so no blind window can ever exist for it. "Add more roots" is **CLOSED-BY-DATA**: 10 of 13 extra `db/day` roots are **micros of existing roots** · `runs/ASSET_CENSUS_20260828/` |
| **`P1/ABS`** | **PROSPECTIVE CHALLENGER** | **BURNED / DISCOVERY-CONSUMED** | PCT ahead in every fixed window and the mechanism is isolated (`ABS_LOOSE` control, p 0.940), but the paired **magnitude** test is p 0.058. Direction overwhelming, dollars not established. Forward data decides · `runs/ABS_PCT_ADJUDICATION_20260827/` |
| **TSMOM (all roles)** | **CLOSED** | **VALIDATION- AND HOLDOUT-CONSUMED** | steady-premium failed (V2-G3); tail-diversifier failed (H1, 4 of 5). ρ = 0.013 but no return — **ballast, not a hedge**. Carry/term structure remains a **separate untested family** |
| **Multi-market TSMOM V1** | **CLOSED — GATES FAILED** | **DEVELOPMENT-ONLY, DISCOVERY-CONSUMED** | substrate, causal roll and basis-safe P&L now EXIST and passed their unit tests; V1 then **failed 3 of 6 preregistered DEVELOPMENT gates** (Sharpe 0.226, 5/9 positive years, 72.3 % equity concentration). Cost drag **47.2 % of gross**, scale-invariant. VALIDATION and FINAL HOLDOUT **unread** · `research/multi_market/TSMOM_V1_DEVELOPMENT.md` |
| **TSMOM V2 (252d slow trend)** | **CLOSED — FAILED VALIDATION** | **VALIDATION-CONSUMED** | failed preregistered **G3** (2 of 4 positive years); **5 of 6 gates passed** (net $15,080, Sharpe 0.577, stress positive, low concentration). 2020 and 2022 carry everything; both calm years lose. **The STEADY-PREMIUM claim is CLOSED at this specification.** ⚠️ **CORRECTED 2026-08-28 — this row previously read "2023–2026 TSMOM outcomes unspent". That is now FALSE: `TSMOM-TAIL-H1` spent exactly that window.** Current truth: **V2 2019–2022 validation CONSUMED · H1 2023–2026 TSMOM outcome holdout CONSUMED · TSMOM all tested roles CLOSED** · `runs/TSMOM_V2_SLOWTREND_20260827/` · `runs/TSMOM_TAIL_H1_20260828/` |
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

> ⚠️ **CORRECTED 2026-08-28.** The four answers below were the 2026-08-27 list. **Three of them have
> since been asked and answered**, and leaving them as "runnable" would have re-run closed work:
> (1) a microstructure expert with positive executable net P&L — **`MS-BBO-CANDIDATE-1` now exists**,
> discovery-grade, so the question moves from *"is there one"* to *"does it survive forward"*;
> (2) a multi-market TSMOM book improving fixed-DD income — **asked and FAILED** (`TSMOM-TAIL-H1`,
> 4 of 5 gates); (3) internals → direct RTH NQ return — **asked and produced NO CANDIDATE**
> (`INT02`). Only the calendar-gated one is unchanged.

**The current list, replacing it:**

> ⚠️ **CORRECTED AGAIN, same day.** The list written this morning has been overtaken by the same
> day's results: (1) `MS-BBO-CANDIDATE-1` is **VOID**, so "does it survive a shadow" has no object;
> (2) carry was asked and **CARRY_V1 failed C6/C7**; (3) the ES question **lost its baseline** when
> BBO was voided. **A standing-questions list that survives its own wave unchanged is not being
> maintained.**

**The current list:**

1. **Is there any information surface this repo can still reach that it has not closed?** Action
   value, HTF, internals ×2, Last-only, BBO, TSMOM ×3 and carry are all closed. **This is now an
   acquisition / re-census question, not a modelling one**;
2. **Is the BBO quote-complete ceiling materially larger than 99?** A file-level census finds 123 NQ
   RTH-complete days (116 pre-seal) against the split's 99-all-consumed. Different criteria, so
   **nothing is claimed** — but it decides whether a future BBO-class object could ever be
   blind-confirmed;
3. **Do ES and NQ sub-minute quote states JOINTLY predict 60 s NQ return?** Deliberately *not* the
   incremental form any more, because the baseline is void. Data-capable at 59 sessions,
   export-gated, power open;
4. **Does curve information survive a universe with ≥3 roots per sector?** `CARRY_V1` failed on
   concentration, and `n_sector = 2` forces a ±1 binary weight in three of four sectors — a
   structural defect of *this* universe, not a verdict on curve information;
5. the sealed pool putting P1 below its **empirical** CPB/CPC `INVALIDATION` band.

**2 is runnable now and cheap. 3–4 need new preregistration and 3 needs a multi-GB export. 1 is a
standing question. 5 is calendar-gated. None assumed.**

## Binding admission rules

- **Same-window comparison mandatory** (§19) — never a 98-session candidate against a 20-year headline.
- **Same-window profit insufficient** (§20) — needs subperiod stability, multiplicity-aware null,
  concentration diagnostics, realistic costs, and an **exposure/activity-matched placebo**.
- **Admission ≠ capital weight** (§21).
- **Replacement is on the table** (§47) — incumbency carries **zero** statistical privilege.
