# TSMOM DATA CONTRACT — NT8 serves different data through different paths for the same contract name

| | |
|---|---|
| **status** | **BINDING.** No TSMOM number may be computed on a path this document marks unusable |
| date | 2026-08-27 |
| evidence | `research/multi_market/src/ncd_day.py` · `runs/TSMOM_DEPTH_CHRONOLOGY_20260827/` |
| cost | **$0** |

> ### **`AddDataSeries` returns MERGE-BACK-ADJUSTED series. `GetBars` and the `db/day` `.ncd`
> ### store return TRUE, UNMERGED contract data. The same contract name yields different
> ### numbers depending on which door you walk through.**
>
> ### **Building TSMOM on the first would have manufactured trend returns out of futures
> ### basis — precisely the failure §7 exists to prevent.**

---

## 1. How it was found, and how it was proved

The export path was built first (`SWBarExport_v3`, one `AddDataSeries` per contract). Its manifest
looked healthy — four ES contracts, hundreds of rows each, no errors. **The tell was that every
contract began on `2010-01-04`, the backtest window start**, while `GetBars` reported `ES 12-11`'s
first bar as `2011-05-30`.

Three measurements settled it. All on ES 03-11 / 06-11 / 09-11 / 12-11 across 2010:

| test | result | reading |
|---|---|---|
| volume on 2010-01-04 | **identical across all four contracts** (1,098,424) | they are one front-month bar wearing four names |
| `ES 12-11 − ES 03-11`, Jan–Jun 2010 | **exactly −16.000, sd 0.0000** (n = 127) | a constant offset — the definition of back-adjustment, and **that constant is the roll basis** |
| same, Jan–Mar 2011 | mean −16.191, **sd 1.5545** | the series only diverge once the contracts genuinely trade separately |

**Where the merged series is and is not the truth**, checked bar by bar against `GetBars`:

| date | merged close | true close | merged volume | true volume | |
|---|---:|---:|---:|---:|---|
| 2011-06-01 | 1302.25 | 1307.00 | 2,323,510 | **167** | ✗ back-adjusted |
| 2011-08-08 | 1106.25 | 1106.50 | 5,142,632 | **4,940** | ✗ back-adjusted |
| **2011-09-08** | 1180.50 | 1180.50 | 776,096 | 776,096 | ✓ front month begins |
| 2011-10-03 | 1087.00 | 1087.00 | 3,064,940 | 3,064,940 | ✓ |

> **The merged series equals the true contract ONLY from the day that contract becomes front
> month.** Before that it carries the *then-front* contract's prices and volume, shifted by a
> constant.

## 2. Why that is fatal here, not merely untidy

**§6's causal roll compares the current contract's prior-day volume against the next contract's
prior-day volume.** In the merged path the next contract's volume *is a copy of the current
front's*, so the two series are identical until the roll and the crossover **can never fire**. The
rule is not merely inaccurate there — it is undefined.

**§7's self-financing accounting needs the NEW contract's true price on the roll day.** The merged
path does not contain it: on the day before a contract becomes front, its "price" is the old
contract back-adjusted. Differencing across the switch would book the basis as P&L.

## 3. The usable path

`GetBars` never merges. Asked for `ES 03-11` over 2010-01-01→2010-01-12 it returns **0 bars** under
both `doNotMerge` and `mergeBackAdjust` — the contract simply did not trade yet. That is the truth
we want.

**Transport.** A `GetBars` call **caches** the downloaded range to
`db/day/<CONTRACT>/<YEAR>.Last.ncd`, and `limit` shrinks only the *response*, not the download. The
same cache is filled by `BarsRequest` with `MergePolicy.DoNotMerge`, which `SWContractFetch_v1`
issues in bounded batches — **without mutating any NT8 instrument or global setting.** Python then
reads the `.ncd` files locally.

**The `.ncd` daily format**, reverse-engineered and validated against `GetBars` on close *and*
volume at four dates:

```
header  28 bytes : int32 version | float64 tickSize | float64 firstPrice | int64 firstTicks
record  48 bytes : int64 ticks | float64 O | float64 H | float64 L | float64 C | int64 volume
                   (ticks = .NET DateTime ticks, 100 ns since 0001-01-01)
```

**Identity, and §5 satisfied by construction.** The cache directory is named by the **full requested
contract ID** (`ES 12-11`), not by the display symbol — and the display symbol is
**decade-ambiguous**: `ESZ1` is both Dec-2011 and Dec-2021, `ESZ6` both Dec-2006 and Dec-2016.
**The directory name is the key.** Tick size arrives free in the header.

## 4. ⚠️ Consequences for existing artifacts

**`runs/MULTIMARKET_INVENTORY_20260827/` used `SWBarExport_v2`, i.e. the merged path.** Therefore:

- its per-contract **bar counts** measure the backtest window, not contract life;
- its **"median daily dollar volume" per root is the FRONT MONTH's volume**, not the named
  contract's.

**The inventory's conclusion survives** — these markets are liquid, and front-month volume is
arguably the right liquidity measure — **but the mechanism was mislabelled**, and its numbers may
not be read as contract-level facts. Corrected here rather than in place, since that run's report
is immutable.

## 5. Binding rules

1. **TSMOM reads the `db/day` `.ncd` store only.** `AddDataSeries` output is barred from the return
   construction.
2. **`contract_id` is the key.** The display symbol may be recorded, never joined on.
3. **The roll needs true per-contract volume**, which exists only on the unmerged path.
4. **A synthetic basis test is mandatory before any P&L**: two contracts differing by a large
   constant basis with identical daily changes must produce the *same* economic return.
   **If changing the roll spread changes alpha, the simulator is wrong.**
5. **A completed job with missing output is FAIL.** Verified from the artifact on disk, never from
   a returned status flag — `WriteNinjaScriptFile` reported `compile_engine: file_only` while the
   class resolved fine, and `SWBarExport_v3`'s first run reported success while writing nothing
   (the cause was that `D:\` root is not writable, so `Directory.CreateDirectory` threw inside
   `DataLoaded`).
