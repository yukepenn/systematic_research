# `ESNQ_V1` — **NO CANDIDATE.** Cross-market ES↔NQ at 60 s loses money. Blind pool UNSPENT.

| | |
|---|---|
| **verdict** | ⛔ **NO CANDIDATE.** `ESNQ_V1` is **CLOSED** at its exact tested scope |
| blocking failures | **X1 · X5 · X6 · X7** |
| headline | net **−$18,113.79** · **−$503.16/session** · 30.6 % positive sessions · OOF corr **+0.0034** |
| structural gates | **P0-1 PASS · P0-2 PASS** (0 violations) · P0-3 reported below |
| **blind pool** | **UNSPENT.** `mu_claim = $0.00` → power **0.000** → **WITHHELD** |
| **LIVE ENABLED** | **NO** |

> ### The experiment was capable of producing a causal, reproducible answer. **The answer is that
> ### this formulation does not make money.** That is a result, not a failure of the process.

---

## A. Pre-run corrections

**Materialization wording.** `PIPELINE_FREEZE` said *"15 sessions, never materialized, never read."*
The second clause is true; **the first was false**. Replaced with the state taxonomy:

| | |
|---|---:|
| `ORIGINAL_FROZEN_BLIND_MANIFEST` | 15 |
| `OUTCOME_CONSUMED` | **0** |
| `PRICE_DERIVED_INFORMATION_READ` | **0** |
| `TRANSIENTLY_MATERIALIZED` | **1** |
| `METADATA_EXPOSED` | **1** |
| `CURRENT_BLIND_BYTES_IN_DEV_SUBSTRATE` | **0** |

**Quarantine provenance, resolved from the logs rather than guessed:** the incident export was
`NQ 09-25`; **ES `2025-08-13` was refused by the allow-list guard** and never materialized.
`2025-08-13` is excluded from ESNQ blind adjudication on an **operational data-integrity fact known
before any blind outcome was read** — not on outcomes. The original manifest is **preserved
byte-for-byte** (`f4a8090e…3c8a`); a derived `ESNQ_BLIND_EFFECTIVE_14.csv` (`00654d4f…4743`) is used
instead.

**The NQ BBO 19-session asset is reclassified exactly**, because `2025-08-13` belongs to it too:
**19 outcome-unconsumed · 18 pristine-never-materialized · 1 metadata-exposed.** No outcome status
changes because metadata was exposed.

**Current-truth repair** (bounded, in place, no second ranking): `README.md` no longer says new alpha
discovery is paused with `EVENT RESPONSE` next — that was the 2026-08-27 state and `EVENT RESPONSE`
is `CLOSED-BY-DATA`.

## B. Final data contract

| | |
|---|---|
| **`CROSS_MARKET_ES_EMBARGO`** | **200 ms**, frozen and unsearchable — 2× the clock probe's 100 ms resolution |
| clock verdict | **`CLOCK-COMPATIBLE-BUT-SEMANTICS-UNKNOWN`**; positive control detected a known +250 ms injection as +200 ms (one bin); untouched streams **0 ms on 100 % of sessions** |
| contract alignment | **44/44** both instruments, **44/44** same expiry cycle, **0** intraday contract changes |
| realised ES information lag | **min 200.0 ms**, median 228.0 ms — the embargo binds exactly as specified |

**P0-2, all 14,564 decisions, not a sample:**

```
max_es_source_ts <= t - 200ms     violations 0
max_nq_source_ts <  t             violations 0
entry_ts         >  t             violations 0
exit_ts          >  t + 60s       violations 0
```

## C. Reproducibility

| | |
|---|---|
| batch | `src/esnq_batch.py` · `f6cd1fe8…c656` |
| streaming | `src/esnq_stream.py` · `49fcc79e…f9ec` |
| **PIPELINE_FREEZE** | **`ab0b951e…0029`** — `PENDING` removed; committed **before** any result |
| manifests | DEV_44 `cb6d2eca…59cd` · BLIND_15 `f4a8090e…3c8a` · EFFECTIVE_14 `00654d4f…4743` · allow-list · BBO pool |
| substrate | **88** per-file sha256 in `substrate_qa.csv` |
| versions | Python 3.11.4 · numpy 1.26.4 · pandas 2.2.2 · sklearn 1.3.2 · pyarrow 16.1.0 · NT8 8.1.8.1 · addon v1.13.9 |

**Independence verified by AST, not grep:** `esnq_stream` imports `bisect, os, sys, collections,
numpy, pandas, pyarrow, timegrid` — **not `esnq_batch`**. (A grep matched the string inside the
docstring promising it does not — the same structured-vs-prose trap the leakage scanner hit.)

## D. Pre-candidate gates

**P0-1 two-sided causality — PASS.** ⚠️ **My first probe was wrong, and the engine was right.** It
used one global cutoff for a **per-decision** embargo, and perturbed both quote sides equally — which
cannot move a spread or an event count. Three families were recorded as "did not move" **by
construction**. Corrected to per-decision, with perturbations that can actually reach each family:

| clause | result |
|---|---|
| **NEG-A** corrupt NQ after `t` → NQ features must not move | **0.000e+00** |
| **NEG-B** corrupt ES after `t−200ms` → ES features must not move | **0.000e+00** |
| **POS-A** ES ask-only shift before cutoff | spread `2.0e+01`, rvol `1.6e−04` |
| **POS-B** delete ES events before cutoff | counts `3.3e+02`, `3.6e+02` |
| **POS-C** shift ES only in the last `w` s | all four `rel_move_w` `7.8e−04` |
| **family coverage** | **8 of 8 CERTIFIED** — each family responds to at least one probe that can reach it |

A uniform level shift cancels inside a return and cannot test `rel_move_w`; a price perturbation
cannot test a count. **Requiring every probe to move every family would be requiring an
impossibility.**

**P0-3 independent parity — the gate earned its keep before the result existed.** First run
**FAILED**: `nq_spread_tk` off by 2.58 ticks, `max_nq_source_ts` by 0.52 s — while labels were
exact. Localized before explaining: the streaming loop **decided before flushing the open
same-millisecond bucket**. Fixed to flush-then-decide. On the smoke session: **9 of 11 features
exactly `0.000e+00`**, rvol at `1.7e−16`/`7.1e−15`, labels and source timestamps exact, `wait_ok`
331/331. **No statistical test could have found that defect.**

## E. Development economics — ONE evaluation, frozen object

| gate | observed | |
|---|---:|---|
| **X1** joint after-cost OOF net > 0 | **−$18,113.79** | ⛔ **FAIL** |
| X2 refitted session-block null | NOT RUN | n/a |
| X3 activity-matched placebo | NOT RUN | n/a |
| X4 same-trigger mirror | +$18,113.79 *for the mirror* | n/a |
| **X5** STRESS +0.5 tk net > 0 | **−$24,261.30** | ⛔ **FAIL** |
| **X6** top-5 ≤ 50 % of positive net | **76.1 %** | ⛔ **FAIL** |
| **X7** net > 0 in ≥3 of 4 quartiles | **0 of 4** | ⛔ **FAIL** |
| X8 NQ-only control *(diagnostic)* | −$55.79/session | n/a |
| X9 ES-pairing mechanism null | NOT RUN | n/a |

> **X2/X3/X9 were not run, and the reason is not budget.** All three ask *"is this **positive**
> result real / genuinely cross-market?"* **There is no positive result to attribute.** A null
> percentile cannot rescue a losing object, and running them would answer a question nobody asked.

**Diagnostics:** 36 OOF sessions (the first fold block is training-only) · **11 positive (30.6 %)** ·
trade rate **12.45 %** (876 long / 607 short / 10,433 flat) · mean per trade **−$12.21** ·
maxDD **$21,421** · worst/best session −$4,070 / +$3,232 · quartiles all negative
(−$8,730 / −$6,515 / −$1,675 / −$1,194) · long −$4,361, short −$13,753 ·
**cost/|gross| 55.5 %** · STRESS +1.0 tk −$11,638.

**The economically decisive number is the correlation: OOF corr(pred, target) = +0.0034.** The model
carries essentially no information, and a 12.45 % trade rate against a **55.5 % cost drag** then
converts that nothing into a reliable loss. **The NQ-only control is also negative (−$55.79/session),
so this is not "ES ruined a working NQ model" — neither information set works at 60 s here.**

⚠️ **`X4` is reported as `n/a`, not as a pass.** The mirror of a losing strategy is profitable by
arithmetic. Reading `+$18,113.79` as evidence for an inverted strategy would be exactly the
post-hoc sign-flip this project forbids: the inversion was not predeclared, and no independent
evidence supports the opposite sign.

## F. Uncertainty — the frozen procedure, not a friendlier one

Circular block bootstrap over the **36** OOF session nets: **L = 4, B = 20,000, seed = 20260828,
10th percentile**, 20,000 distinct replicate values.

| | |
|---|---:|
| `mu_hat_dev` | **−$503.16**/session |
| bootstrap mean of means | −$503.52 |
| **`mu_claim` = max(0, 10th pctile)** | **$0.00** |
| *(diagnostic only)* IID session bootstrap 5th pctile | −$936.87 |

**Inference is session-clustered: n = 36 OOF clusters.** The 14,564 decisions are diagnostic only and
were never used as an inferential N.

## G. Blind option value — **NOT AUTHORIZED**

| | |
|---|---:|
| EFFECTIVE blind n | **14** |
| `sigma_blind` (frozen) | $5,250.81/session |
| SE_blind | **$1,403.34**/session |
| MDE(80 % power) | **$3,489.36**/session |
| power at `mu_claim = $0.00` | **0.000** (required ≥ 0.80) |

All seven conditions: development gates **False** · mechanism null **False** · causality **True** ·
parity **True** · stress **False** · `mu_claim > 0` **False** · power ≥ 0.80 **False**.

**Sessions that would have been irreversibly consumed:** the 14 in `ESNQ_BLIND_EFFECTIVE_14.csv`
(2025-08-18 → 2026-05-05). **None was read. None was exported. None was materialized.**

## H. Verdict

> ### **NO CANDIDATE.** `ESNQ_V1` is CLOSED at its exact tested scope.

**Forbidden and not done:** 30 s / 15 s / 120 s horizons · additional ES features · feature subsets ·
GBM or any nonlinear model · event / time-of-day / volatility filters · "ES-only" · an alternative
pairing null · threshold relaxation. A genuinely different future cross-market formulation requires
a **fresh EVI adjudication and fresh preregistration**.

**What is closed, precisely:** cross-market ES↔NQ **price-side** microstructure, **60 s** horizon,
**these 11** relative-by-construction features, **Ridge**, this policy and cost model, on **44
development sessions** under a **200 ms** ES embargo. **Not closed:** cross-market information at
other horizons, other feature classes, or with certified sub-100 ms timestamp semantics — none of
which this object tested, and none of which may be opened as a rescue.

## I. Protected assets

| asset | status |
|---|---|
| **ESNQ blind EFFECTIVE_14** | **UNREAD, UNSPENT, never exported** |
| ESNQ ORIGINAL_15 manifest | preserved **byte-for-byte**, unmutated |
| **NQ BBO 19-session asset** | **19 outcome-unconsumed · 18 pristine · 1 metadata-exposed** |
| **141-session Last-only pool** | **UNTOUCHED** |
| **≥ 2026-08-01 seal** | **VIRGIN** |
| **LIVE ENABLED** | **NO** — no order path exists; the export used NT8's isolated `Backtest` account and produced zero trades |
