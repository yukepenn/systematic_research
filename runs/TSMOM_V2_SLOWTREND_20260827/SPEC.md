# TSMOM V2 — SLOW TREND (252-day only) · PREREGISTRATION

| | |
|---|---|
| **status** | **COMMITTED BEFORE ANY VALIDATION RETURN WAS READ** |
| date | 2026-08-27 |
| authorized by | owner directive §1 — exactly **ONE** V2 candidate |
| window | **VALIDATION 2019-01-01 → 2022-12-31, ONE SHOT** |
| final holdout | **2023-01-01 → 2026-05-30 — BLOCKED by assertion during validation** |
| global seal | **≥ 2026-08-01 — BLOCKED by assertion everywhere in this lane** |

---

## 1. ⚠️ Evidence provenance — permanent, and attached to every number V2 ever produces

```
DEVELOPMENT-DERIVED
SELECTED AFTER INSPECTING THE FOUR PREDECLARED V1 COMPONENTS
ONE-OF-FOUR DISCOVERY
NOT CLEAN DEVELOPMENT EVIDENCE
```

V1's development diagnostic for the 252-day component — net **$25,757**, Sharpe **0.479**, and it
would have cleared all six V1 gates — is **discovery, not evidence**. It is *why* this candidate
earns one further test; it is not a result in its favour.

**Why this candidate is legitimate rather than a rescue:** 252d was one of the four components
declared in V1's spec *before* V1 ran. It was not invented after seeing the failure. Slow trend has
a structural prior distinct from fast trend. And — decisively — **a completely untouched validation
window still exists.**

> ### **THE UNTOUCHED 2019–2022 WINDOW IS HOW THE POST-HOC SELECTION DEBT IS PAID.**
> Not by an arbitrary haircut on the Sharpe, not by a winner's-curse correction. By an actual
> independent read. If a selection-aware null is run it is *supporting context only*, must mimic the
> real one-of-four process, and **may not substitute for the validation.**

## 2. The candidate — exactly one thing differs from V1

| | V1 | **V2** |
|---|---|---|
| signal | `mean(sign(R21), sign(R63), sign(R126), sign(R252))` | **`sign(R252)`** |

**Everything else is inherited byte-for-byte** and is listed so that any deviation is auditable:
21 CORE roots · per-root/date eligibility (live contract today **and** ≥200 of the last 260
business days covered) · 252-day warmup · true unmerged `.ncd` substrate · causal volume-crossover
roll with the pre-expiry override · self-financing basis-safe economic return · 63-day trailing
realised-dollar-volatility estimator lagged one full day · inverse-vol → equal-risk-per-root →
equal-risk-per-sector sizing · daily rebalance · fractional research sizing · $4.36 commission ·
PRIMARY 1-tick and STRESS 2-tick spreads · long/short symmetry · sector membership.

**Explicitly NOT changed, and these are prohibitions, not oversights:**
no root removed for hurting V1 · no short leg removed because longs looked better · no equity
overlay because equities dominated V1 · no sector caps · no vol-estimator change · no rebalance-
frequency change · no cost change · no root selection · no roll-rule change · no carry, trend
strength, breakout, correlation filter or crash overlay. Those are **future hypotheses, not V2**.

## 3. Frozen artifact hashes

| artifact | sha256 |
|---|---|
| `ncd_day.py` | `17603bdc722d30f386b013d35a33f8b2cb510d8b7ea6fdbc07f0274bf01baec9` |
| `roll.py` | `b88a5176f8ed1dbc3903e300f6238993099046437c4b921293c9ba1d2eda837f` |
| `contract_truth.py` | `66b06867260dff8a09b2d78ed0bfe51927aa39a4e7994606e376413aca7c1b06` |
| `build_substrate.py` | `be756af2dec76ef80792cd84a6f26602e05043297ceb2a26820c02f68eeb4047` |
| `tsmom_v1.py` | `c7f5a0eb2c2f8fa0ae11c167d3951fd983a9ca139e1b32992868707955d7bebb` |
| **`tsmom_v2.py`** | `9da123e6fae7dd367cdbd320ccd0a4b571991a1016de9e9863b7f7099a9db6b8` |
| `economic_returns.parquet` | `9339386887bb15dbfb3a7cacb203c2db2860c73e91bd326cb95145a45edf1e21` |
| `ROLL_LEDGER.csv` | `4e8a822cddc45bf52e1c10520e55aa09063b6494ba561382d82d970d1cd9cefe` |

**Substrate**: 76,314 root-days, 21 roots, 2009-03-31 → 2024-01-19. Validation window carries
**20,893 eligible root-days across all 21 roots**.

> **The substrate was extended from expiry years 2009–2019 to 2009–2023 to cover validation. That
> is DATA COVERAGE ONLY.** Verified by regression: re-running V1 on the extended substrate
> reproduces the committed development figures **exactly** — days 2,265, net $10,167, Sharpe 0.226,
> gross $19,270, cost $9,102, maxDD $17,129. The extension is purely additive.

## 4. Blocking assertions in code

```python
assert substrate.date.max() < 2026-08-01      # global seal, everywhere in this lane
assert validation.date.max() < 2023-01-01     # FINAL HOLDOUT unreachable during validation
```

Both are in `src/tsmom_v2.py` and abort the run rather than warn.

## 5. Validation gates — fixed here, before the read

| gate | rule |
|---|---|
| **V2-G1** | PRIMARY-cost net > 0 |
| **V2-G2** | annualised Sharpe ≥ 0.30 |
| **V2-G3** | positive in ≥ 3 of the 4 complete validation calendar years |
| **V2-G4** | STRESS-cost net > 0 |
| **V2-G5** | no single root > 50 % of **positive** net |
| **V2-G6** | no single sector > 60 % of **positive** net |

**Concentration denominator, declared now** because total net may be near zero or negative:
share = `contributor / Σ(positive contributors)`. If Σ positive ≤ 0 the share is **undefined** and
the gate **FAILS** — an object with no positive contributors does not pass a concentration test by
technicality.

**Reported but NOT gated** (no post-hoc gate may be invented from these): long vs short, root and
sector tables, turnover, cost drag, maxDD, ES, underwater fraction, yearly decomposition, top-day
and top-5-day concentration.

**One shot.** No year-by-year peeking before the full preregistered result is computed.

## 6. Continuation rule — absolute

**IF ANY BLOCKING GATE FAILS → STOP TSMOM V2.**

Record: `TSMOM V1 = FAILED` · `TSMOM V2-252 = FAILED VALIDATION` · `FINAL HOLDOUT = UNSPENT`.

Then **do not** try 126d, blend 126+252, try 189d or 300d, change rebalance frequency, remove ags,
equal-weight sectors, go long-only, add trend strength, carry or breakout, or create a V2.1.
**That would convert VALIDATION into DEVELOPMENT.** Slow TSMOM is then **CLOSED / DE-PRIORITISED at
this specification family**, and the budget moves to internals → direct RTH NQ return.

**IF AND ONLY IF ALL GATES PASS** → freeze V2 source + config + cost model immediately, then
author the frozen portfolio protocol, and only then authorize **one** final-holdout read.

## 7. Final-holdout rule (applies only on a clean pass)

`2023-01-01 → 2026-05-30`, one read. **Current-regime evidence carries deployment weight**: a
17-year full-sample average may **never** rescue a failed 2023–2026 result. Equally, a clean modern
result is not rejected because 2015–2018 was ugly, since the candidate was not selected from the
modern outcome. The portfolio protocol — objects, causal allocator, primary utility
`Δ fixed-DD $/week` — must be frozen **before** that read.
