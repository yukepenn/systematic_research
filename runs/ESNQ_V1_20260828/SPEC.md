# SPEC — `ESNQ_V1` · does **cross-market** ES↔NQ sub-minute information carry after-cost NQ alpha?

**Committed BEFORE any export, any feature, any result.** ⚠️ **EXPORT-GATED — the run does not start
until the substrate exists and the Phase-0 gates below pass.**

| | |
|---|---|
| **family** | **CROSS-MARKET MICROSTRUCTURE** — information transfer between two correlated liquid contracts |
| **explicitly NOT** | a repair, rerun, or variant of `MS-BBO-CANDIDATE-1`. **Its feature set is forbidden here** |
| development | **44 sessions** — ES∩NQ overlap whose **NQ side is already outcome-consumed** |
| **blind confirmation** | **15 sessions** — ES∩NQ overlap with **BOTH sides unread**. One shot, unlocked only if development passes **every** gate |
| **claim ceiling** | **`DEVELOPMENT-SUPPORTED + BLIND-FALSIFICATION-SURVIVED`**. **Never "validated"** — n=15 cannot validate |
| **LIVE ENABLED** | **NO** |

---

## 1. The question, re-posed honestly

The previous question — *"does ES add incremental value **beyond the frozen NQ-only BBO
candidate**?"* — is **VOID**, because that candidate read the future and its causal version earns
**−$1,785.88/session at OOF corr 0.0072**. There is no baseline to be incremental to, and its
preregistration is **not** reused.

**The new question:**

> ### Does causally-observed **cross-market** ES↔NQ price-side microstructure contain after-cost
> ### predictive information for 60-second **NQ executable** return?

**Why this is a genuinely different mechanism**, and not the void lane wearing a hat:

| | |
|---|---|
| the void lane asked | do **NQ's own** quote dynamics predict NQ? → corrected answer ≈ **no** (corr 0.0072) |
| this asks | does **ES's** state predict **NQ**, i.e. is there information *transfer* between two contracts on the same underlying economy? |
| why the null does not transfer | a single-instrument null says nothing about a **cross-instrument lead-lag**. Different information set, different economic story, different failure modes |
| what is already closed | **W122 closed the 1-MINUTE ES→NQ family.** Sub-minute is untested — and 60 s is where a lead-lag between the deepest and second-deepest index future would live if anywhere |

## 2. Feature budget — **11, fixed. Relative by construction.**

**The `MS-BBO-V1` 20-feature set may not be used**, in whole or in part. That surface has paid its
discovery budget. The core features here are **differences between the two markets**, which cannot
be a rerun of an NQ-only construction.

Both legs are converted to **unit-free fractional returns** before differencing, because ES and NQ
have different index levels and point values ($50 vs $20) and a raw point difference would encode
scale, not divergence.

| family | count | features |
|---|---:|---|
| **F1 cross-market divergence** | **4** | `rel_move_{1,5,15,30}s` = `ES_ret_w / ES_mid − NQ_ret_w / NQ_mid` |
| **F2 ES state** | **4** | `es_spread_tk` · `es_rvol_30s` · `es_bid_upd_30s` · `es_ask_upd_30s` |
| **F3 NQ execution context** | **2** | `nq_spread_tk` (also the causal cost threshold) · `nq_rvol_30s` |
| **F4 time** | **1** | `tod` |

**Declared and counted:** F3 reuses two NQ constructions. That is deliberate — a divergence measure
is meaningless without the local state it diverges from, and `nq_spread_tk` is required by the cost
threshold regardless. **2 of 11 is the entire overlap with the retired set, and it is stated here
rather than discovered later.**

⛔ **No quote size** (never certified — MS01A). ⛔ **No same-millisecond event ordering** (81.1 % of
adjacent events share a millisecond; exchange sequence inside a ms is unrecoverable). Every feature
is built from **prior DISTINCT timestamps** and must be permutation-invariant within a millisecond.

## 3. Information and execution clocks — unchanged, and now machine-enforced

```
FEATURES   events with timestamp STRICTLY < t          (both instruments)
EXECUTION  first NQ quote at a DISTINCT timestamp > t  (entry) and > t+60s (exit)
same-ms    mean by side within one identical timestamp; row order NEVER used
```

**All time offsets are constructed through `research_sdk/timegrid.py`.** `lookback_offsets_s`
returns `int64`, asserts every offset is strictly negative, and verifies count/min/max against
declared intent. **The defect that voided the last candidate is unreachable from this code path.**

## 4. Model budget — **ONE primary, ZERO challengers**

`Ridge(alpha=10.0)`. **No GBM.** A second model doubles the multiplicity for a lane whose whole
purpose is a clean claim, and the previous wave's max-stat null over `{Ridge, GBM}` is exactly the
complication being avoided. **If Ridge cannot see it, this specification says it is not there.**

## 5. Target, policy and costs — the executable object, not a correlation

```
long_gross  = (NQ_bid_{t+60}  - NQ_ask_t)     * 20
short_gross = (NQ_bid_t       - NQ_ask_{t+60}) * 20
threshold   = nq_spread_tk * 0.25 * 20 + 4.36      (causal: spread observable strictly before t)
action      = LONG if pred > thr ; SHORT if pred < -thr ; else FLAT
```

Commission **$4.36** round-turn, charged once. `MAX_FILL_WAIT = 1000 ms`, the frozen fill contract.
Stress ladder **0 / +0.5 / +1.0 tick per side**. **NQ is the traded instrument; ES is informational
only.** Nothing is traded in ES, so no ES execution model is needed or claimed.

## 6. ⚠️ PRE-CANDIDATE GATES — new order of operations, adopted after the void

**No result may be called a candidate until these pass. They run BEFORE any P&L is reported.**

| gate | requirement |
|---|---|
| **P0-1 causality, two-sided** | `research_sdk/causality.py`. **NEGATIVE**: corrupt every ES and NQ event strictly after `t` → features **bit-identical**. **POSITIVE**: perturb inside each of F1/F2/F3's information set → **that family must move**. A family that does not respond is not certified |
| **P0-2 rolling-path timestamps** | every path feature **emits** its min/max source timestamp; `max_source_ts < decision_ts` asserted **row-by-row** on all sessions, and the window must reach as far back as declared |
| **P0-3 independent streaming parity** | a **second, independent** streaming implementation reproduces the feature vector and **100 % of LONG/SHORT/FLAT actions**. **Not** correlation — action parity |

> ### **P0-3 is now a PRE-CANDIDATE gate, not a deployment afterthought.** An independent
> ### re-implementation is the only thing that found the last defect: nulls, placebos and mirrors
> ### all recompute the same features and inherit any leak. **If parity fails, there is no
> ### candidate — the P&L is not reported as a finding.**

## 7. Development gates — frozen now, all must pass

Development = the **44** overlap sessions whose NQ side is already outcome-consumed. Chronological
out-of-fold only; training-only scaling; **session is the dependence unit** (never trade count).

| gate | requirement |
|---|---|
| **X1** | joint after-cost OOF net **> 0** |
| **X2** | **> 95th percentile** of a **refitted session-block null** — whole-session outcome blocks circularly shifted, model refit from scratch inside every replicate, **≥ 2 distinct values asserted** |
| **X3** | beats an **activity-matched placebo** at the realised trade rate |
| **X4** | beats the **same-trigger mirror** (same decisions, inverted side) |
| **X5** | STRESS **+0.5 tick/side** net **> 0** (+1.0 reported as a mandatory diagnostic) |
| **X6** | top-5 sessions ≤ **50 %** of positive cumulative net |
| **X7** | net **> 0** in **≥ 3 of 4** equal chronological quartiles |
| **X8** | **NQ-only control** run on the identical folds/sample. Reported always. The **increment** is a declared **secondary diagnostic, not a gate** — its paired variance is unknown in advance and a level-variance shortcut would be the wrong denominator |

**Power, stated honestly.** Session sd from the consumed sessions is **$5,250.81**.
Development n=44 → se **$792**, **MDE(80 %) ≈ $1,969/session**. Against a ~$246/session incumbent
yardstick this is **~8× short**, so **development can only detect a large effect.** That is a
property of the data, declared now, and it is not repaired by counting trades instead of sessions.

## 8. Blind confirmation — one shot, and its true strength

**Unlocked only if every P0 and X gate passes.** The **15** overlap sessions with **both sides
unread**, frozen inside `BBO_BLIND_POOL_MANIFEST.csv` (`84a8575a…0931`).

| | |
|---|---|
| **B1** | after-cost net **> 0** |
| **B2** | STRESS +0.5 tick/side net **> 0** |
| **B3** | one-sided 95 % lower bound on mean session net **reported** — **not required to exceed 0** |

**B3 is deliberately not a pass/fail gate, and the reason is arithmetic.** At n=15, se is **$1,356**
and MDE(80 %) is **$3,372/session**. Requiring a positive lower bound would demand an effect **14×**
the incumbent's per-session scale, which would make the gate unfalsifiable in practice and turn a
genuine falsification test into theatre.

> ### **What this pool actually is: a FALSIFIER.** Against a claimed **+$5,125** that is truly
> ### **−$1,786**, the gap is **5.1 σ** at n=15 — power ≈ **1.0**. It is well powered against exactly
> ### the failure this campaign has experienced, and badly underpowered to establish a modest edge.
> ### **It must be described that way in every report that uses it.**

**Cost of spending it, stated before spending:** the NQ blind pool is 19 sessions; 15 lie in the ES
overlap. Running this consumes those 15 and leaves **4** for any future NQ-only object. That is a
real, irreversible price and it is the reason the pool is gated behind a full development pass.

## 9. Outcomes — fixed in advance

| outcome | class |
|---|---|
| any P0 gate fails | **NO CANDIDATE.** Fix the implementation; the P&L is not a finding |
| any X gate fails | **`ESNQ_V1` CLOSED.** Blind pool **NOT** spent. Move on |
| X all pass, B1/B2 pass | **`DEVELOPMENT-SUPPORTED + BLIND-FALSIFICATION-SURVIVED`** — the strongest class this campaign can currently reach for microstructure. **Not "validated"** |
| X all pass, B1 or B2 fails | **FALSIFIED FORWARD OF DISCOVERY.** Recorded, not retuned |

**Forbidden on failure**, pre-committed: other horizons · other lookbacks · adding the retired NQ
feature set · a GBM challenger · dropping ES features that hurt · re-splitting development/blind ·
substituting sessions · re-running on the 4 remaining NQ-blind sessions. **Those are a search after
failure.** Default: **move on and re-rank.**

## 10. Execution order — SPEC, then substrate, then runner, then result

1. this SPEC committed ✅
2. **export gate** — ES+NQ tick export for 59 sessions, ~3.7 GB to **D:** (170 GB free; **C: is not
   touched**). Bounded, per-session, hashed into a manifest with QA
3. runner committed **before** any result exists
4. P0 gates → X gates → only then B

**Nothing in this SPEC authorizes reading the sealed pool, spending the 141-session Last-only pool,
or sending any order.**
