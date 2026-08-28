# `ESNQ_V1` — SPEC AMENDMENT **A1**. Committed **before any ES price is read**.

**Amends, does not replace, `SPEC.md`.** Where `SPEC.md` is already stronger than requested, that is
demonstrated rather than duplicated.

| unchanged, explicitly | |
|---|---|
| economic hypothesis · 60 s target · decision schedule · the frozen 11 features · Ridge as sole primary · cost model · development/blind session identities · blind manifest · global seal · the forbidden MS-BBO surface | **all carried forward untouched** |

| new blocking content | |
|---|---|
| **§A1-1** `ESNQ_CLOCK_CONTRACT_V1` — cross-instrument clock certification | **blocks the run** |
| **§A1-2** contract / roll alignment, exclusion rule fixed **now** | **blocks the run** |
| **§A1-3** physical dev/blind isolation + blocking assertion | **implemented** |
| **§A1-5** `ES-PAIRING NULL` — a mechanism gate, not an outcome gate | **new gate X9** |
| **§A1-7** blind-spend admissibility | **new blocking gate, threshold $3,371/session** |

---

## §A1-0. What is already in `SPEC.md` and is not duplicated

| requested | status |
|---|---|
| two-sided causality (P0-1) | ✅ present |
| rolling-path timestamp emission + row-wise `max_source_ts < decision_ts` (P0-2) | ✅ present |
| independent implementation, **100 % action parity**, pre-candidate (P0-3) | ✅ present — and already stronger than "verify later": failure means **no candidate and the P&L is not reported** |
| session as the dependence unit; no pseudo-N from 331 decisions | ✅ present in §7 |
| ONE primary, zero challengers | ✅ present |
| no quote size, no same-ms ordering | ✅ present |
| forbidden-on-failure list | ✅ present in §9 |

## §A1-1. `ESNQ_CLOCK_CONTRACT_V1` — **BLOCKING, before any feature or P&L**

`feature_ts < decision_ts` **within** each file is necessary and **not sufficient** for a
cross-market claim. The failure mode this gate exists for:

> ### A systematic difference in ES vs NQ timestamp semantics, feed latency, or historical-store
> ### alignment can manufacture an apparent "ES leads NQ" while **every within-instrument causality
> ### assertion passes.** The void candidate is proof that all-gates-green is compatible with a
> ### fatal clock defect.

**Must be answered from provenance and data, never assumed. `UNKNOWN` is a permitted answer and is
preferred to an invented one.**

| | |
|---|---|
| **A** | what the timestamp in each ES/NQ `Bid`/`Ask`/`Last` record represents — exchange event time · provider time · local receipt · NT8 store time · **UNKNOWN** |
| **B** | whether ES and NQ share provider · historical API path · storage format · timezone conversion · millisecond precision · session-label rule · download mechanism |
| **C** | timezone/session alignment verified against metadata and known market boundaries. **No alpha outcome is used** |
| **D** | pathology **without asking whether it predicts NQ**: duplicate-timestamp fraction per stream · event-density distribution · clock granularity · backwards timestamps · session-open and maintenance-boundary alignment · systematic whole-stream offset · missing-interval structure · contract-transition alignment |
| **E** | **a timing-only falsification with teeth**: inject a known ±Δ offset into one stream and **prove the diagnostic detects it**, then run the same diagnostic on the untouched streams. **Δ is fixed in advance and never chosen by alpha performance** |
| **F** | **high price correlation is NOT evidence of clock synchrony.** Correlation is precisely what conceals misalignment |

| verdict | consequence |
|---|---|
| `CLOCK-CERTIFIED` | proceed |
| `CLOCK-COMPATIBLE-BUT-SEMANTICS-UNKNOWN` | proceed **only** if the independent implementation uses the **same** information contract, and **no lead-lag claim stronger than the data supports** is made |
| **`CLOCK-UNSAFE`** | **BLOCKS `ESNQ_V1`.** Not a warning |

## §A1-2. Contract / roll alignment — exclusion rule fixed **now**

For **every** development and blind session, reported before features exist: ES full contract ID ·
NQ full contract ID · expiry month/year · same quarterly cycle? · either instrument in roll
transition? · intra-session active-contract change? · can the pairing create an **artificial
fractional-return divergence**?

> **Declared now, from contract identity and roll metadata only — never from P&L:**
> a session is **EXCLUDED** if (i) either instrument's active contract changes intra-session, or
> (ii) the ES and NQ legs sit in **different quarterly cycle months**. The rule is applied
> **identically** to development and blind, and **power and counts are recomputed before any
> result** if the admissible population changes.

**No date may be dropped after P&L exists for any reason.**

## §A1-3. Physical dev/blind isolation — implemented, not merely promised

Two frozen, disjoint manifests. **No bulk export into one alpha-readable directory.**

| manifest | n | normalized sha256 |
|---|---:|---|
| `manifests/ESNQ_DEV_44.csv` | **44** | `cb6d2eca…59cd` |
| `manifests/ESNQ_BLIND_15.csv` | **15** | `f4a8090e…3c8a` |

For the blind 15: raw cache stays where NinjaTrader already keeps it. **No materialization into the
ESNQ substrate. No features. No labels. No returns. No QA that exposes a price path** beyond the
predeclared metadata eligibility already computed from file names and hour labels.

`research_sdk/blindguard.py` implements two independent mechanisms, both self-tested:

```
assert_no_blind_contamination(inputs, blind_manifest)   BLOCKING, called before any read
require_authorization(auth_path, blind_manifest)        blind runner refuses without it,
                                                        and re-checks the manifest hash so a
                                                        session cannot be substituted after a
                                                        decision
```

**Hashes are normalized (LF) content hashes.** The BBO pool manifest hashed differently in the
working tree (CRLF) than in the committed blob while the content was identical — a tamper-evidence
hash that moves with a checkout setting is a weak one.

## §A1-4. Chronological OOF contract — made explicit

`SPEC.md` §7 says *"chronological out-of-fold only; training-only scaling; session is the dependence
unit."* That is directionally right and **under-specified**. Fixed now, before any result:

- folds split at **session** boundaries; a session is never split across folds;
- every test session is **chronologically after** every training session in its fold;
- **no random row split**; no future session enters training for an earlier OOF prediction;
- **all** normalization/scaling computed on training rows only, **inside** each fold;
- the model is **refit from scratch** per fold — no warm start, no carried coefficients;
- any policy-threshold input requiring estimation is training-only (the causal spread threshold is
  observed, not estimated, so this binds vacuously — stated so it cannot later be relaxed);
- a 60 s decision horizon **never crosses** a fold or session boundary: the last decision of a
  session is `15:30:00`, its exit `15:31:00`, both inside the same session.

**Fold count and locations are fixed before any P&L and may not be chosen after inspecting it.**
**5 chronological folds**, equal session counts, matching the existing convention.

## §A1-5. `ES-PAIRING NULL` — new gate **X9**, a *mechanism* falsification

> ### A profitable model does not establish cross-market information transfer merely because ES
> ### columns appear in it. The model could be exploiting NQ's own state, or ES's marginal
> ### distribution, or intraday seasonality shared by both.

**Construction, fixed before the ES data are read:**

- **unchanged:** every NQ session, its feature path, its outcomes, its decision times, its execution
  quotes, its intraday structure;
- **preserved:** each ES session **internally** — its intraday seasonality and marginal feature
  distribution survive intact;
- **destroyed:** the true **same-day ES↔NQ pairing**, by a **session-level circular shift** whose
  offsets are fixed independently of P&L (all non-zero shifts, exhaustively, up to the session
  count);
- **fully refit** for every replicate — the entire Ridge pipeline including normalization. **No
  fitted coefficient or scaler may be reused from the real pairing;**
- **assert ≥ 2 distinct values** in the resulting null distribution.

**This is NOT an outcome-shift null.** It asks: *would a similarly distributed but **incorrectly
paired** ES path produce as much apparent NQ alpha?*

| **X9** | correctly-paired ESNQ **> 95th percentile** of the ES-pairing null |
|---|---|

**If X9 fails, the claim `CROSS-MARKET INFORMATION TRANSFER` FAILS even if standalone P&L is
positive.** No alternative permutation scheme may be tried afterwards.

## §A1-6. Independent implementation — one clause added

P0-3 stands. Added: **the independent implementation must not import or call the batch
feature-construction function it verifies.** Sharing certified low-level utilities
(`research_sdk/timegrid.py`) is permitted and desirable; sharing **feature logic** is not, because
both implementations would then inherit the same mistake — which is the entire failure mode P0-3
exists to catch.

On mismatch: **localize the discrepancy first. Do not explain it economically. Do not report the
P&L as alpha evidence.**

## §A1-7. Blind-spend admissibility — **NEW BLOCKING GATE**

Implemented and committed **now**, before any development number exists:
`src/blind_spend_power.py`.

**Declared in advance and not re-selectable:** σ = **$5,250.81**/session (the frozen
consumed-session sd — *not* an ESNQ-derived sd), n = 15, one-sided α = 0.05, **minimum power 0.80**
to reject a collapse to zero.

```
SE_blind   $1,355.75/session
MDE(80%)   $3,371.05/session
```

| μ_dev $/session | power vs 0 | vs sign reversal | vs $246 | authorize? |
|---:|---:|---:|---:|---|
| 246 | 0.072 | 0.100 | 0.000 | **NO — UNSPENT** |
| 1,000 | 0.182 | 0.433 | 0.138 | **NO — UNSPENT** |
| 1,969 *(dev MDE)* | 0.424 | 0.896 | 0.354 | **NO — UNSPENT** |
| 3,000 | 0.715 | 0.997 | 0.650 | **NO — UNSPENT** |
| **3,372** | **0.800** | 1.000 | 0.746 | **YES** |
| 5,125 | 0.984 | 1.000 | 0.975 | YES |

> ### **THE AUTHORIZATION THRESHOLD IS μ_dev ≥ $3,371/session — 13.7× the incumbent yardstick.**
>
> **Stated plainly, because it is the point:** applied honestly, this rule means the **most likely
> outcome is `BLIND UNSPENT`.** A development effect large enough to authorize the spend would
> itself be extraordinary — the *void* candidate claimed $5,125. **That is the correct behaviour.**
> The pool's job is to falsify a large claim; if the claim is modest the pool cannot adjudicate it,
> and spending it would destroy an irreversible asset while learning nothing.
>
> `blindguard.write_authorization` **refuses** to write `AUTHORIZED` when power < 0.80. The rule is
> enforced in code, not in prose.

**If development is positive but modest:** verdict is
**`DEVELOPMENT-SUPPORTED / BLIND-UNDERPOWERED / BLIND UNSPENT`**, the object is frozen if warranted,
and its next evidence requirement moves to **prospective accumulation** rather than burning a pool
that cannot adjudicate it.

## §A1-8. Development interpretation — predeclared

44 independent session clusters. Pre-read MDE **$1,969/session** against a **~$246/session**
yardstick — **~8× short**.

- a weak or modest positive estimate is **NOT "promising"**;
- **failure to reject zero does not prove absence** — report the one-sided bound and the MDE;
- **decision-level row count never replaces session-level dependence.** No 331-decisions/session
  pseudo-N may be used to claim power, anywhere, for any statistic;
- accuracy is **diagnostic only**.

**Mandatory report contents:** net/session · total net · stress net · session t and CI ·
positive-session fraction · directional accuracy · trade rate · turnover · cost/gross ·
top-1 and top-5 session concentration · quartile stability · long vs short · time-of-day
contribution · contract-quarter contribution · **ES-pairing-null position** · session-block null
position · causality status · independent parity status.

**No narrative may be built around a positive point estimate whose uncertainty is enormous.**

## §A1-9. The prior — literature may not promote

External work supports **only** that electronic equity-index futures participate strongly in price
discovery and that lead-lag relationships can exist. It does **not** establish that ES leads NQ,
that NQ leads ES, that any delay is stable at 60 s, or that anything is exploitable after costs in
2025–2026. Modern price-discovery studies typically operate at **millisecond-to-second** resolution,
which is **not** this horizon.

| | |
|---|---|
| worth **one** clean test | yes |
| prior | **not high** |
| a spectacular 60 s result earns | **more** engineering scrutiny, not less |
| a 60 s failure closes | **only this frozen formulation** |

**Literature may not be cited in any promotion argument.**

## §A1-10. Execution order — and the hard stop

1. this amendment committed ✅
2. export **ONLY the 44 development sessions** — the blind 15 are never materialized
3. certify data quality → **§A1-1 clock contract** → **§A1-2 contract alignment**
4. P0-1, P0-2, P0-3
5. **only then** development OOF P&L
6. adjudicate X1–X9
7. compute blind-spend power against the **actual** μ_dev using **this committed formula**
8. **STOP AND REPORT.**

> ### **The 15 blind sessions are NOT read in this wave, whatever the development result.**
> A reviewer checkpoint sits between `DEVELOPMENT RESULT` and `IRREVERSIBLE BLIND SPEND`. This is
> information-budget discipline, not hesitation.

---

# AMENDMENT **A2** — pre-P&L final hardening. Committed **before any feature, label, fit or P&L**.

Extends A1. Nothing in A1 is weakened. **No ESNQ alpha result exists**, so these are pre-result
safeguards, not post-hoc tuning.

| § | addition | status |
|---|---|---|
| **A2-1** | blind incident classified; **price-derived leakage scan across every artifact** | **0 structured leaks** |
| **A2-2** | exporter frozen as research evidence, hashed like strategy source | byte-identical |
| **A2-3** | blind guard proven at **three independent levels**, manifests re-loaded per level | **A/B/C all PASS** |
| **A2-4** | `ESNQ_CLOCK_CONTRACT_V1` executed with a **timing-only positive control** | **CLOCK-COMPATIBLE-BUT-SEMANTICS-UNKNOWN** |
| **A2-5** | contract alignment reproduced **from the exported substrate** | 44/44 |
| **A2-6** | blind spend hardened against **winner's curse** — `mu_claim`, not `mu_hat_dev` | threshold rises to **~$4,385/session** |
| **A2-7** | inference is **session-clustered**; 331×44 rows may never be an inferential N | binding |
| **A2-8** | `PIPELINE_FREEZE.json` — every hash that exists, runner hash **PENDING** | frozen |
| **A2-9** | **blind is NOT run in this wave**, whatever development shows | binding |

## A2-6 — the winner's-curse rule, stated so it cannot be softened later

```
mu_claim = max(0, mu_hat_dev - 1.2815515655 * SE_dev)      SE_dev SESSION-CLUSTERED
```

A development mean is itself noisy. Authorizing on the raw point estimate would spend the pool
**precisely when the estimate was luckiest**. Blind spend now requires **all seven**: development
gates · ES-pairing mechanism null · causality · independent parity · stress economics ·
`mu_claim > 0` · **power at `mu_claim` ≥ 0.80**.

| `mu_hat_dev` | `SE_dev` | `mu_claim` | power | authorize? |
|---:|---:|---:|---:|---|
| 3,371 | 792 | 2,357 | 0.537 | **NO — UNSPENT** |
| 4,000 | 792 | 2,986 | 0.711 | **NO — UNSPENT** |
| 5,000 | 792 | 3,986 | 0.902 | YES |

> **`mu_hat_dev` must now reach ≈ $4,385/session — about 18× the incumbent yardstick.** Stated
> plainly: **`BLIND UNSPENT` is the overwhelmingly likely outcome, and that is the intended
> behaviour.** The rule may not be weakened after seeing development results.

## A2-4 — clock contract verdict, and what it licenses

**`CLOCK-COMPATIBLE-BUT-SEMANTICS-UNKNOWN`.** Therefore, binding on everything downstream:

- the independent implementation **must** use the same information contract;
- **no lead-lag claim finer than 100 ms** may be made — that is the probe's resolution;
- a **sub-100 ms mechanism claim is OUT OF SCOPE** for this object;
- timestamp semantics are recorded as **UNKNOWN**, not invented.

## A2-8 — what is frozen, and the one thing that is not

`PIPELINE_FREEZE.json`, sha256 **`ec7d5682…66c7`**: both specs · all four manifests · the exporter ·
**88 per-file substrate hashes** · the clock verdict · alignment · audit · the blind-spend module ·
the declared feature names, target, model, folds, execution, costs, threshold, nulls, seed and
software versions.

> ⚠️ **`feature_source_sha256` is `PENDING`. The runner does not exist and was deliberately not
> written in this wave.** It must be committed, with its hash added to the freeze, **before any
> development result is generated.**
