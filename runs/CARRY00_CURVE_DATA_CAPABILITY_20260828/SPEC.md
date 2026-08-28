# SPEC — `CARRY00_CURVE_DATA_CAPABILITY` · can the curve be OBSERVED at all?

**Committed BEFORE the measurement.** No alpha P&L. No signal verdict. No backtest.

| | |
|---|---|
| **question** | For each root, does a **simultaneously observable** near/deferred contract pair exist in the true unmerged store, often enough and early enough to support a causal curve signal? |
| **what this is NOT** | a carry backtest, a carry signal, or a verdict on whether carry pays. **Not one dollar of P&L is computed in this run.** |
| **why it comes first** | **TSMOM needed ONE contract per root per day. Carry needs TWO, on the same day, both causally observable.** That is a strictly harder data requirement and it has not been measured |
| possible outcome | **`CLOSED-BY-DATA` is an allowed and respectable result** and must not be argued around |

---

## 1. The specific risk this run exists to find

The multi-market substrate was built and validated for **trend**, which reads one active contract.
A curve signal reads the **difference between two maturities at the same instant**. Known warning
from the substrate work: some roots — FX especially, and parts of the energy history — show
**short overlapping lives** between consecutive contracts. Where the deferred contract has no
usable bars while the near one is active, **curve carry is not merely weak, it is undefined**, even
though outright trend was perfectly computable.

> ### ⚠️ **A back-adjusted series must never be used to manufacture a second contract.**
> `TSMOM_DATA_CONTRACT.md` established that `AddDataSeries`/`RunStrategyBacktest` return
> **merge-back-adjusted** data in which four "contracts" report identical volume — they are the
> same front-month bar wearing four names, offset by a constant that **is the roll basis**.
> Differencing two of those would return the basis itself and call it carry. **Only the true
> unmerged `db/day/<FULL CONTRACT ID>` store is admissible here.**

## 2. Contract identity — decade-unambiguous by construction

The key is the **full requested contract ID** (`"ES 12-11"`), never the display symbol: `ESZ1`
denotes **both** Dec-2011 and Dec-2021. The cache directory name *is* the key, so §5 of the data
directive is satisfied structurally rather than by convention.

## 3. The curve data contract — declared now, so it cannot be chosen to suit a result

| leg | definition |
|---|---|
| **NEAR** | the contract the **existing causal active-contract engine** would legitimately hold on date `t`, using information available **through `t−1`** (`roll.build_roll_ledger`, unchanged) |
| **DEFERRED** | the **nearest later listed contract by contract month** — per the root's **declared** cycle — that has valid unmerged data at the same causal information timestamp |

> **The deferred leg is chosen by CONTRACT MONTH ORDER, never by future volume, future liquidity or
> future performance.** "Pick the deferred contract that trades best later" is a look-ahead, and it
> is the exact shape of error that voided the BBO candidate today.

## 4. Expiry / maturity normalization — do not invent precision

NT8 has **not** certified expiry or first-notice dates in this store. Therefore this run does **not**
fabricate them. Maturity distance is expressed as a **declared contract-month gap**:

```
month_gap = (year_def - year_near) * 12 + (month_def - month_near)
```

If certified expiry metadata ever becomes available, it may replace this **and must be hashed**.
Until then, `month_gap` is reported as what it is: a **contract-month gap, not a true time to
expiry**. **Agricultural first-notice risk stays explicit** and the existing pre-expiry safety
buffer (5 trading days) remains binding — there is no physical-delivery fantasy here.

## 5. What is measured, per root — coverage only

contract months available · exact requested IDs · date coverage · **simultaneous near/deferred
coverage** · median overlap days · p10/p50/p90 overlap · fraction of otherwise-eligible root-days
with **≥2** simultaneous contracts · fraction with **≥3** · missing-month patterns · delivery-month
cycle · price sanity · negative/zero-price dates · whether expiry metadata is **CERTIFIED or
inferred** (it is inferred) · the `month_gap` distribution actually available.

**Price sanity is not cosmetic.** April 2020 put CL below zero. Any curve formula that takes a log
or a ratio breaks there, so the run reports negative/zero prints per root **before** a formula is
chosen, and the formula is then chosen to survive them.

## 6. The eligibility rule — DATA ONLY, and declared before the numbers exist

A root may enter `CARRY_V1` **only** on observability. Declared now:

| clause | requirement |
|---|---|
| **E1** | ≥ **1,500** root-days with a simultaneously observable near/deferred pair (~6 years) |
| **E2** | ≥ **60 %** of the root's otherwise-eligible trend days carry a valid pair |
| **E3** | pair coverage present in **≥ 60 %** of the calendar years the root spans |
| **E4** | zero negative/zero closes on either leg on days used, or the root is flagged and the formula must survive them |

**A root is never admitted because its carry backtest looks good, and never dropped because it looks
bad — no carry P&L exists when this rule is applied.** Sector participation needs **≥ 2**
carry-capable roots (§40); a sector with fewer is `CASH`, and **no root is borrowed across sectors**.

## 7. Continuation — fixed in advance

| outcome | verdict | next |
|---|---|---|
| a multi-sector universe survives E1–E4 | **CARRY-CAPABLE** | preregister exactly ONE `CARRY_V1` |
| coverage exists but collapses to one or two sectors | **CARRY = CLOSED-BY-DATA** (breadth) | do **not** force it → ES↔NQ sub-minute |
| simultaneous pairs are largely absent | **CARRY = CLOSED-BY-DATA** | → ES↔NQ sub-minute |

**No parameter of this run may be relaxed after seeing the coverage numbers.** If E1–E4 turn out to
be too strict, that is recorded as a measured fact about the data, not repaired by lowering a
threshold — which would make the eligibility rule a function of the outcome it is meant to precede.
