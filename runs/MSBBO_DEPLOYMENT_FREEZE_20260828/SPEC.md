# SPEC — `MSBBO_DEPLOYMENT_FREEZE` · turning a surviving candidate into ONE deployable object

**Committed BEFORE any deployment coefficient exists.** Enforced by the prereg guard.

| | |
|---|---|
| **what this is** | **ENGINEERING / DEPLOYMENT DEFINITION** |
| **what this is NOT** | **new alpha evidence.** Nothing here can promote, demote, or re-open `MS-BBO-CANDIDATE-1` |
| produces | `MS-BBO-CANDIDATE-1-DEPLOY` — one fitted mathematical object |
| **LIVE ENABLED** | **NO.** Unchanged, and nothing in this run touches that |

---

## 1. The defect this run exists to fix

`MS-BBO-CANDIDATE-1` is frozen as a **family + feature set + policy + cost model**. That is not a
fitted model. `bbo_v1.py` evaluates **chronological out-of-fold, fold-specific Ridge fits** — five
different coefficient vectors, none of them designated as *the* model. Nothing in the frozen
artifact uniquely determines the prediction for

```
2026-09-02 10:00:00 ET
```

> ### **Two honest implementations of the frozen candidate could produce different future
> ### predictions. That means the object is not yet falsifiable prospectively**, and a shadow ledger
> ### built on it would be recording an ambiguous quantity.

## 2. The resolution rule — ONE rule, declared before fitting

```
FULL FIT OF THE FROZEN PRIMARY ESTIMATOR
ON THE FROZEN CONSUMED DISCOVERY POPULATION.
```

- estimator: the preregistered **PRIMARY**, `Ridge(alpha=10.0)`. Not the GBM challenger.
- fit **exactly once**, on **all** admissible consumed discovery decisions.
- the exact frozen feature list **and order**; the exact frozen target; the exact frozen
  normalization convention (train-set mean/sd, `sd == 0 → 1`).

**Explicitly forbidden, and this is the whole point of declaring it first:** we do **not** compare
full-fit Ridge against average-fold Ridge, last-fold Ridge, a fold ensemble, a recalibrated Ridge, or
a different alpha, and then keep whichever has the better historical P&L. That comparison is a
selection machine wearing engineering clothes. **The full fit is chosen because it is the canonical
and least-selection-loaded resolution of the OOF→deployment ambiguity, not because of how it scores.**

> ### The deployment model's historical **in-sample** result has **ZERO evidentiary weight**.
> It is not reported as a performance figure, it is not compared to $5,124.76, and it may not be used
> to reconsider candidate admission. It exists only to define the future executable object.

## 3. Data boundary — BLOCKING

```
assert max(training_source_timestamp) < 2026-08-01
```

Already-consumed BBO discovery data only. **No seal data. No 8/1–8/31 data. No shadow data.** The
assertion is in the runner and aborts rather than warns.

## 4. Nothing may change

No new feature · threshold · horizon · TOD window · model family · Ridge alpha · policy rule · fill
rule. The 20 features, the 60 s grid, 10:00–15:30 ET, `MAX_FILL_WAIT = 1000 ms`, the causal
threshold `spread_tk·TICK·DPP + 4.36`, and the stress ladder all carry over unmodified. The
deployment runner **imports `bbo_v1.py` unmodified** rather than restating it, so drift is
structurally impossible and the frozen sha256 stays valid.

## 5. The serialized artifact — `model.json` is authoritative

A plain deterministic JSON representation, not an opaque pickle. Minimum contents:

```
strategy_id · candidate_id · training_start · training_end · exact session manifest
source-file hashes · feature-code hash · exact ORDERED feature names
feature means · feature standard deviations · Ridge alpha · coefficient vector · intercept
sklearn / numpy / pandas / pyarrow / Python versions
target definition · decision schedule · threshold formula
commission · tick size · point value · fill rules · max fill wait · stress definitions
information timestamp rule · SHA256 of the entire artifact
```

Prediction must be reconstructable, by anyone, as

```
z_j        = (x_j - mean_j) / std_j              std_j == 0  ->  z_j := 0
prediction = intercept + SUM_j coefficient_j * z_j
```

with declared handling of zero-sd, NaN and ±inf, and a **fixed feature order**. A `.joblib` may exist
as a convenience; if it ever disagrees with `model.json`, **the JSON wins**.

## 6. Self-parity gates — all must pass, declared before the fit

| gate | requirement |
|---|---|
| **D1** | `sklearn.predict()` vs the manual JSON formula on **all** consumed discovery decisions: `max abs difference <= 1e-9` |
| **D2** | **action parity exact** — LONG/SHORT/FLAT identical on **100 %** of decisions between the sklearn path and the serialized-inference path |
| **D3** | training-source timestamp assertion holds (§3) |
| **D4** | artifact hashes recorded; re-hashing the written file reproduces the recorded digest |
| **D5** | the frozen `bbo_v1.py` sha256 still equals `36dee22c…dc6d`, i.e. the alpha definition was not edited by this run |

**If D1 or D2 fails, there is no deployable object and the shadow does not start.** A prediction
difference is not "close enough": the policy is a threshold, so an arbitrarily small numerical
disagreement can flip an action, and the action is what gets recorded as evidence.

## 7. What is recorded about provenance, permanently

> This full-fit model was created **AFTER** the discovery candidate survived its gates, **solely to
> define the future executable object.** Its historical performance must not appear in any promotion
> argument, at any checkpoint, ever.

## 8. Reproduction of the discovery figure — a fidelity check, not a result

The run additionally re-executes the **unmodified** OOF discovery path and asserts it reproduces
`$5,124.76/session`. This closes the `out/bbo_v1.txt` 0-byte logging gap recorded in
`MSBBO_V1/CORRECTION_20260828.md` §1D-b **without editing the frozen file**. It is a fidelity check
on an already-reported number, not a new measurement, and it changes no evidence class.
