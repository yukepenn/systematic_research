# `MS-BBO-CANDIDATE-1` IS **VOID**. It read the future. The streaming-parity run found it.

| | |
|---|---|
| **verdict** | ⛔ **VOID — LOOK-AHEAD / FEATURE TIMESTAMP VIOLATION.** Directive §12, first listed condition |
| **also void** | `MS-BBO-CANDIDATE-1-DEPLOY` — it inherits the contaminated features |
| **the cause** | `bbo_v1.py:119` · `step = np.arange(-30, 0) * NS` · **silent int32 overflow** |
| **what it did** | features at `t` read quote state up to **+2.065 seconds AFTER `t`** |
| **the leak was worth** | **$6,910.64/session = 134.8 %** of the reported result |
| **what survives causally** | **−$1,785.88/session**, OOF corr **0.0072**, t **−3.57**, 25 % positive sessions |
| **Alpha #2** | **NONE.** Unchanged, and now for a much better-established reason |

> ### The campaign's only surviving candidate was an artifact. **The engineering step that was
> ### supposed to be a formality — proving the object could exist in real time — is what killed it.**

---

## 1. What happened, in the order it happened

The deployment freeze passed cleanly: **all five self-parity gates**, `D1` at exactly `0.000e+00`,
`D2` action parity exact on 19,194 decisions, and the OOF discovery figure **reproduced** to
$5,124.76/session. Nothing there was wrong. A model was serialized and hashed.

Then the streaming engine replayed one session, and **13 of the 20 features matched at exactly
`0.000e+00` while 7 disagreed by hundreds of dollars.** The 7 were precisely those built from the
30-sample mid/spread path — and, decisively, **`midret_30s` matched exactly** even though it reads
the *same instant* `t−30s` through different arithmetic.

A partial mismatch confined to one code path, with a same-instant control matching exactly, has one
kind of explanation.

```python
bbo_v1.py:119        step = np.arange(-30, 0) * NS          # NS = 1_000_000_000
```

**On Windows with NumPy 1.26, `np.arange(-30, 0)` has dtype `int32`.** `NS` fits in int32, so
value-based casting keeps the product in int32 — and `-30 × 1e9 = -3e10` **overflows**. NumPy raises
**no warning** for integer overflow in an array-scalar product.

| | |
|---|---|
| intended offsets | `[−30 s, −1 s]`, all strictly in the past |
| **actual offsets** | **`[−2.115 s, +2.065 s]`** — scrambled, and **15 of 30 POSITIVE** |

The four `midret_*` features escaped because they use `w * NS` with **Python** ints, which have
arbitrary precision. The same accident is why the bug was visible at all: it left a matched control
inside the same feature block.

## 2. Three independent proofs, because "the offsets look wrong" is not a finding

### V1 — direct timestamp assertion on the *actual* offsets

15 of 30 sample points lie **after** the decision instant, the furthest at **+2.064771 s**.

> **This is the probe `L1` should have made.** L1 asserted `feature_ts < t < execution_ts` for the
> quote lookups *at* `t` — and passed, 0 violations, correctly. It never examined the **path
> offsets**. The audit had a blind spot in exactly the place the defect lived.

### V2 — perturbation: corrupt **only** events strictly after `t`

Session `s20260622`, decision `12:45:00`, **3,098,663** post-`t` events shifted by +50 points.

| feature | unperturbed | future corrupted | Δ |
|---|---:|---:|---:|
| `rvol_30s` | 20.538232 | 664.065599 | **+643.53** |
| `range_30s` | 48.750000 | 1039.375000 | **+990.63** |
| `dist_hi_30s` | 41.250000 | 1033.750000 | **+992.50** |
| `dist_lo_30s` | 7.500000 | 5.625000 | **−1.88** |
| every other feature | | | **0.000000** |

> **A causal feature cannot move when future data changes.** Four did.

⚠️ **V2 under-detects, and the reason matters.** The perturbation shifts bid and ask by the *same*
amount, so it leaves every **spread** unchanged — which is why `spread_chg_30s`, `spread_minfrac`
and `spread_pctile` show 0.000000 here. They are built from the **same contaminated `step`** and are
contaminated too; this particular probe simply cannot see it. V1 and the parity mismatch table both
show all seven. **A probe that returns zero has not proved absence — it has proved only that this
probe could not see it.**

### V3 — the size of the leak: the frozen pipeline with the offsets corrected to `int64`

| arm | $/session | net | sessions | trade % | OOF corr | t | positive % |
|---|---:|---:|---:|---:|---:|---:|---:|
| **AS-FROZEN (leaky)** | **5,124.76** | 245,989 | 48 | 61.4 | **0.1702** | **6.76** | 87.5 |
| **FIXED (causal)** | **−1,785.88** | −85,722 | 48 | 24.8 | **0.0072** | **−3.57** | **25.0** |

**The look-ahead was worth $6,910.64/session — 134.8 % of the reported result.** The causal object
does not merely lose the edge; it **loses money**, and its OOF correlation of **0.0072** is
indistinguishable from nothing.

## 3. ⚠️ The lesson, and it is the expensive one: **L2 was the bug announcing itself**

`L2` lagged every feature by one 60-second step and the result went **+$5,125 → −$1,490/session**.
That is a bizarre outcome for a genuine forecast, and it was flagged as an anomaly at the time —
correctly. It then drove a fifth probe, `L5`, which tested the **stale-quote reconstruction**
hypothesis and **rejected** it on good measurements.

**And then the anomaly was treated as explained.** The write-up said the result was *"consistent
with a genuine fast-decaying signal."*

Compare the numbers now:

| | |
|---|---:|
| L2, features lagged 60 s | **−$1,490/session** |
| V3, look-ahead removed | **−$1,786/session** |

**Those are the same object.** Lagging every feature by 60 s moved the contaminated window from
`[t, t+2.065s]` to `[t−60s, t−57.9s]` — which **removes the look-ahead**. L2 was not a strange
property of a fast signal. **L2 was a clean measurement of the strategy without its leak, and it was
sitting in the report the whole time.**

> ### Rule, bought at full price: **rejecting one hypothesis for an anomaly does not explain the
> ### anomaly.** L5 refuted staleness — and staleness was never the only candidate. The anomaly
> ### stayed open and should have been treated as open. "Consistent with X" was written up as
> ### "explained by X", which is the precise move this project forbids everywhere else.

A second rule: **a partial mismatch is more informative than a total one.** Had all 20 features
disagreed, the natural diagnosis would have been a broken re-implementation. Because 13 matched to
`0.000e+00` and a same-instant control was among them, the defect was localised in minutes.

## 4. Why the other audits missed it

| audit | why it passed | why that was not enough |
|---|---|---|
| **L1** timestamp assertion | asserted `feature_ts < t < execution_ts` **at `t`** | never examined the 30 path offsets |
| **L3** ablation | dropping mid-returns cost little ($5,125 → $4,873) | correct, and now **explained** — the edge was in the *contaminated* path features, not the clean mid-returns |
| **L4** mismatched execution | −$3,692/session | tests the **label**; the leak was in the **features** |
| **L5** staleness | rejected on measurement | tested the wrong hypothesis for the right anomaly |
| **B2/B3** refitted nulls, 100.0th pctile | genuinely computed | **a null distribution built from the same leaky features cannot detect the leak.** Every replicate carried it too |

> **Nulls, placebos and mirrors cannot detect a look-ahead in the feature construction**, because
> they all inherit it. Only a direct causality probe or an independent re-implementation can.
> **The independent re-implementation is what worked**, and it worked on its first run.

## 5. What is void, what survives

| | |
|---|---|
| ⛔ **VOID** | `MS-BBO-CANDIDATE-1` · `MS-BBO-CANDIDATE-1-DEPLOY` · every figure in `MSBBO_V1/REPORT.md` §1 and §3 |
| ⛔ **VOID** | the 7 gates, the 4+1 leak probes, $5,124.76/session, t 6.76, OOF corr 0.170 |
| ✅ **survives — and is certified** | the **streaming engine**. Against the corrected batch it matches **19 of 20 features at exactly `0.000e+00`**, `rvol_30s` at `1.4e-14` (float summation order), both labels exact, `wait_ok` **331/331** |
| ✅ survives | the deployment-freeze **method** (D1–D5), the fill contract, the same-ms discipline, `MS01A`'s semantics audit, the shadow architecture |
| ✅ survives | **the 141-session Last-only blind pool — never touched.** The **≥2026-08-01 seal — never touched** |

**Is the corrected object a new candidate? No.** At **−$1,786/session** with OOF correlation
**0.0072**, there is nothing to preregister. And per §12 a repaired definition would be a **NEW
discovery object on already-consumed data**, inheriting every unit of selection debt already spent
on these 48 sessions. It is recorded as consumed and closed, not carried forward.

**Not inverted either (§76).** A negative result is not an anti-alpha: the inversion was not
predeclared, and no independent evidence supports the opposite sign.

## 6. Blast radius — checked, and it is one line

```
grep -rn "np.arange(...) * NS"  across the whole repo  ->  ONE hit: bbo_v1.py:119
```

Every other `np.arange` in the repo indexes **bars or rows**, never nanosecond offsets. **No other
run in this repository is contaminated by this defect.** `MS-LAST-V1`, `INT01`, `INT02`, the TSMOM
family and the weekly-edge waves all use Python-int or `pd.Timedelta` time arithmetic.

## 7. Consequences

- **`MS-BBO-CANDIDATE-1` is removed from the prospective-shadow roster.** There is no BBO object to
  shadow. The shadow's remaining roster (`P1/PCT`, `P1/ABS`, `XM_CONFLICT_v2`) accrues at ~1.6
  decisions/week, so **the shadow's EVI drops sharply** and it is no longer rank 1.
- **Alpha #2 = NONE**, now on much firmer ground than yesterday.
- **The 48 consumed BBO sessions are further consumed** by V3. Recorded in the attempt registry.
- **`bbo_v1.py` is NOT edited.** Its hash is referenced by the frozen manifest and by this
  refutation. A void object must stay readable exactly as it was.
- **LIVE ENABLED: NO** — unchanged, and never at risk: no order path was ever built.
