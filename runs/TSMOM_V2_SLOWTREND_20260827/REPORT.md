# TSMOM V2 (252d slow trend) — FAILED VALIDATION on V2-G3. Final holdout unspent.

| | |
|---|---|
| **verdict** | **BLOCKING GATE FAILED → TSMOM V2 STOPPED. No V2.1. Slow TSMOM CLOSED at this specification family** |
| spec committed | `1fe0091`, **before any validation return was read** |
| window | **2019-01-01 → 2022-12-31, one shot**, 1,033 trading days |
| **final holdout** | **2023-01-01 → 2026-05-30 — UNSPENT**, blocked by assertion |
| seal | ≥ 2026-08-01 untouched, blocked by assertion |

> ### ⚠️ **PROVENANCE, permanent:** DEVELOPMENT-DERIVED · SELECTED AFTER INSPECTING THE FOUR
> ### PREDECLARED V1 COMPONENTS · ONE-OF-FOUR DISCOVERY · NOT CLEAN DEVELOPMENT EVIDENCE.
> ### This window was the payment for that selection. **It was paid, and the candidate failed.**

---

## 1. The gates

| gate | observed | verdict |
|---|---:|---|
| V2-G1 PRIMARY net > 0 | **$15,080** | PASS |
| V2-G2 annualised Sharpe ≥ 0.30 | **0.577** | PASS |
| **V2-G3 positive in ≥ 3 of 4 years** | **2 of 4** | **FAIL** |
| V2-G4 STRESS net > 0 | $12,859 | PASS |
| V2-G5 top root ≤ 50 % of positive net | 13.7 % (ZF) | PASS |
| V2-G6 top sector ≤ 60 % of positive net | 47.1 % (rates) | PASS |

**Five of six pass, and V2 is a materially better object than V1 on every dimension it shares.**
That is real information and it is recorded. It does not change the outcome: G3 was declared
blocking before the read, and the continuation rule is absolute.

## 2. The failure is not "it lost money" — it is concentration in time

| year | net | Sharpe |
|---|---:|---:|
| 2019 | **−$1,265** | −0.25 |
| **2020** | **+$12,068** | **1.92** |
| 2021 | **−$1,835** | −0.24 |
| **2022** | **+$6,111** | **0.88** |

> ### **The entire validation result is 2020 and 2022 — the COVID dislocation and the
> ### inflation/rates repricing. The two calm years both lose money.**
>
> A window Sharpe of **0.577** is a genuinely attractive number and it is **carried by two macro
> regimes**. That is precisely what G3 exists to detect, and it is why a single window-level Sharpe
> is not sufficient evidence for a sleeve intended to run continuously.

## 3. What V2 fixed relative to V1, for the record

| | V1 (development) | **V2 (validation)** |
|---|---:|---:|
| Sharpe | 0.226 | **0.577** |
| cost drag | **47.2 %** of gross | **15.4 %** |
| top sector share | 72.3 % equity | **47.1 % rates** |
| top root share | 32.4 % | **13.7 %** |
| maxDD | $17,129 | $7,726 |

**Slower signal → far less turnover → cost drag falls from 47 % to 15 %**, and the concentration
problem that failed V1's G6 is gone: the winners are **rates $9,148 · energy $4,105 · equity
$2,768 · fx $2,091 · ags $1,304**, with metals **−$4,336**. It is no longer a long-equity-beta
result. Long +$13,574 vs short +$1,563; top-5 days are 38.8 % of net.

**None of that rescues it.** These are reported because they are true, not because they are an
argument.

## 4. The continuation rule, applied

**STOPPED.** Per `SPEC.md` §6 and the owner directive, the following are **not** attempted:
126d · a 126+252 blend · 189d · 300d · a rebalance-frequency change · dropping ags or metals ·
equal-weight sectors · long-only · trend-strength weighting · carry · breakout · V2.1.

> **Any of those would convert VALIDATION into DEVELOPMENT.** The window has now judged one
> candidate and is spent for this specification family.

**Slow TSMOM is CLOSED / DE-PRIORITISED at this specification family.**

## 5. What a future hypothesis could legitimately be — and what it would cost

The 2020/2022 pattern is a *finding*, not a rescue route: it says slow trend behaved here like a
**crisis-regime payoff rather than a steady premium**. A sleeve valued as a **tail hedge** —
judged on conditional behaviour in the incumbent's worst weeks rather than on standalone Sharpe —
is a **genuinely different hypothesis** with a different primary metric.

**It would need its own preregistration, and it cannot use 2019–2022 again**, which is now
consumed. Its only clean windows would be the final holdout (one read) or prospective time. That is
an expensive hypothesis, and it should compete against the other lanes on EVI rather than be
adopted because TSMOM is the object already in hand.

## 6. Verdict

| | |
|---|---|
| **what was measured** | one frozen 252-day-only slow-trend candidate on a completely untouched 2019–2022 window |
| **what passed** | 5 of 6 gates; the machinery, the cost model, both blocking assertions |
| **what failed** | **V2-G3 — 2 of 4 positive years.** Blocking |
| **what changed** | slow trend is **not** a steady premium here; on this window it is a two-regime payoff. V1's cost-drag and equity-concentration problems were real and the slower signal fixes both |
| **what did NOT change** | the incumbent; the final holdout; the seal; the 141-session Last-only blind pool |
| **evidence class** | **VALIDATION-CONSUMED.** The one-of-four selection debt was paid and the candidate did not survive |
| **ladder status** | **no candidate.** TSMOM does not become Alpha #2 |
| **data burned** | **2019–2022 for this specification family.** FINAL HOLDOUT UNSPENT |
| **next** | immediately: **internals → direct RTH NQ return** (§11), a genuinely independent surface `INT01` never tested |
