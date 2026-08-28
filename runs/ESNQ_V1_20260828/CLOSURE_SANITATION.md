# `ESNQ_V1` CLOSURE SANITATION — holding a negative result to the same standard as a positive one

**No rescue. No new alpha run.** Five defects in the *closure*, not in the verdict.

| # | issue | resolution |
|---|---|---|
| **1** | P0-3 was incomplete when the economics were computed | **44/44 now complete · ACTION DISAGREEMENTS = 0** · breach recorded, not hidden |
| **2** | stress net was non-monotone (−18.1k → −24.3k → −11.6k) | **CASE 2** — stress moves the *threshold*, so it is a **policy perturbation**, not a pure cost stress |
| **3** | A3 said `n = 44` OOF nets; the report said 36 | **SPEC INCONSISTENCY** — the frozen fold design structurally yields **36** |
| **4** | X6 stated as a clean failure | **NON-ADJUDICATIVE** on a negative-total object |
| **5** | "all structural gates passed before economics" | **false** — corrected |

**The verdict does not change: `NO CANDIDATE`, on X1.**

---

## 1. P0-3 — completed, and the ordering breach recorded

Both sources verified **byte-identical** to the versions frozen before the development result:
`esnq_batch.py f6cd1fe8…`, `esnq_stream.py 49fcc79e…`. No source was touched.

| | |
|---|---:|
| sessions completed | **44 / 44** |
| decision rows compared | **14,564** |
| OOF-evaluable rows compared | **11,916** |
| max abs feature difference | `es_rvol_30s` **6.66e−16** · `nq_rvol_30s` **2.84e−14** · **all other 9 features exactly 0.000e+00** |
| max **relative** feature difference | **4.29e−15** |
| NaN-pattern mismatches | **0** |
| max source-timestamp difference | **0 ns** (both ES and NQ) |
| label difference (`long_gross`/`short_gross`) | **0.000e+00** |
| `wait_ok` disagreement | **0** of 14,564 |
| max prediction difference | **4.97e−13** |
| **ACTION DISAGREEMENTS** | **0 / 11,916 at +0.0, +0.5 AND +1.0 tick** |
| net difference | **$0.000000** |

> ### **ORDER-OF-OPERATIONS BREACH — full P0-3 completion occurred after the economic computation,**
> ### although the parity job was launched before the result and both implementations were already
> ### frozen. The delayed completion found **zero action disagreement**, so the breach affects
> ### **process ordering, not the measured economic object.**

**The claim "all structural gates passed before economics" is retracted.** At the moment of the
economic read, P0-3 was **20/44 complete** and **X9 was never run**. What is true: P0-1 and P0-2
passed before the economics; P0-3 was *launched* before and *completed* after, with zero
disagreement.

## 2. Stress arithmetic — **CASE 2**, and the object is misnamed

Source-provenance first. `esnq_batch.policy_pnl` (inherited from the `bbo_v1` convention):

```python
thr = nq_spread_tk*TICK*DPP + COMMISSION_RT + 2*extra_ticks*TICK*DPP   # <-- threshold MOVES
act = where(pred > thr, 1, where(pred < -thr, -1, 0))                  # <-- so the ACTION SET moves
```

| stress | **as implemented** (threshold moves) | trades | **pure cost** (actions FIXED) | trades |
|---|---:|---:|---:|---:|
| +0.0 | **−$18,113.79** | 1,483 | **−$18,113.79** | 1,483 |
| +0.5 | **−$24,261.30** | **705** | **−$25,528.79** | 1,483 |
| +1.0 | **−$11,638.32** | **345** | **−$32,943.79** | 1,483 |

**There is no arithmetic bug.** The non-monotonicity is fully explained: raising the threshold
prunes trades (1,483 → 705 → 345), and on a *losing* strategy trading less loses less. The pure
execution-cost object is **exactly monotone** and its arithmetic closes to the cent:
`2 × 0.5 × 0.25 × 20 × 1,483 = $7,415.00` per half-tick step.

> ### **THE CURRENT STRESS OBJECT IS A POLICY PERTURBATION, NOT A PURE EXECUTION-COST STRESS.**

**Did the preregistration authorize the action set to change?** `SPEC.md` §5 lists the ladder under
**costs** and X5 says only *"STRESS +0.5 tick/side net > 0"*. **Neither reading is stated.** The
contract is **ambiguous**, not violated — so:

> **`X5 NOT ADJUDICATED — STRESS CONTRACT UNDER-SPECIFIED`.**

⚠️ **And it does not matter for the verdict: X5 fails under BOTH readings** (−$24,261.30 as
implemented, −$25,528.79 pure). No new stress gate is invented, because X1 already determines
`NO CANDIDATE`.

## 3. The 44-vs-36 OOF reconciliation

```
DEV sessions total          44
N_FOLD = 5  ->  array_split into 6 blocks:  [8, 8, 7, 7, 7, 7]
block 0 (8 sessions)        TRAINING-ONLY, never a test set
OOF-evaluable sessions      36
  fold 1: train  8 -> test 8      fold 4: train 30 -> test 7
  fold 2: train 16 -> test 7      fold 5: train 37 -> test 7
  fold 3: train 23 -> test 7
realised OOF session nets   36
```

The first block receives no OOF prediction because an **expanding** window has nothing to train on
before it. That is correct and was frozen before the result.

> ### **SPEC INCONSISTENCY — A3 stated `n = 44` OOF session nets, while the already-frozen
> ### expanding-window fold design structurally yields `n = 36` evaluable OOF sessions.**
> **A3 is NOT rewritten to pretend it always said 36**, and **no OOF prediction is manufactured for
> the training block.**

The block bootstrap was already computed on the **actual 36** — labelled here as
**`CORRECTED DIAGNOSTIC UNDER ACTUAL OOF POPULATION`**, not a retroactively preregistered test:
L=4, B=20,000, seed 20260828, 10th pctile, 20,000 distinct replicates →
`mu_hat_dev` **−$503.16**, **`mu_claim` $0.00**. It authorizes nothing regardless: **X1 < 0**.

## 4. X6 — corrected interpretation

The frozen formula is *"top-5 sessions ≤ 50 % of positive cumulative net"*. It exists to reject a
**positive** result carried by a handful of sessions. `SPEC.md` defines **no denominator for a
negative-total object**, and the computed 76.1 % is the top-5 share of the *positive sessions only*
inside a set whose total is **−$18,113.79**.

> **X6 = 76.1 % — `MECHANICALLY FAILS FROZEN FORMULA / NON-ADJUDICATIVE ON A NEGATIVE TOTAL-NET
> OBJECT`.** The numeric computation is preserved unchanged; only its interpretation is corrected.
> **This does not change the verdict.**

**Gate table, corrected:**

| gate | observed | status |
|---|---:|---|
| **X1** net > 0 | **−$18,113.79** | ⛔ **FAIL — decisive** |
| X2 refitted null | not run | n/a — tests a *positive* result |
| X3 activity placebo | not run | n/a — same |
| X4 same-trigger mirror | +$18,113.79 for the mirror | n/a — a loser's mirror wins by arithmetic |
| **X5** stress | −$24,261.30 / −$25,528.79 | **NOT ADJUDICATED** (contract under-specified) — **fails under both readings** |
| **X6** concentration | 76.1 % | **NON-ADJUDICATIVE** on negative total net |
| **X7** ≥3 of 4 quartiles | **0 of 4** | ⛔ **FAIL — independently adverse** |
| X8 NQ-only control | −$55.79/session | diagnostic |
| X9 ES-pairing mechanism null | **not run** | n/a — nothing positive to attribute |

**The decisive failures are X1 and X7.**

## 5. Final admissibility

| condition | |
|---|---|
| 44/44 independent parity, exact action agreement | ✅ **0 disagreements** |
| batch source unchanged | ✅ `f6cd1fe8…` identical |
| primary economic arithmetic reproduces | ✅ pure-cost decomposition closes to the cent |
| no new causal or data defect found | ✅ P0-1, P0-2 unchanged and passing |

> ## **`ESNQ_V1 CLOSED — NO CANDIDATE`**

**At exact scope:** ES↔NQ **price-side** cross-market · **60 s** target · the frozen **11** features ·
**Ridge** · frozen schedule · frozen NQ execution contract · **200 ms** ES embargo · this DEV
population · this policy/cost definition **as clarified in §2**.

**Explicitly NOT claimed:** that cross-market information is null, or that ES contains no useful
information. **Not opened:** 15 s / 30 s / 120 s · nonlinear models · more features · ES-only ·
reversed sign · event or TOD filters · threshold changes.

**`EFFECTIVE_14` remains unread and unspent.**
