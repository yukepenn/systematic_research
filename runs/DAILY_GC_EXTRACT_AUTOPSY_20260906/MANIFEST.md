# MANIFEST — GC (COMEX gold) DAILY series, `runs/DAILY_GC_EXTRACT_AUTOPSY_20260906/`

**Built 2026-09-06. Metals-pod Wave-1 extraction. DESCRIPTIVE / DISCOVERY_CONSUMED — no P&L object,
no ledger trial, no promotion.** Regenerate: `python src/gc_extract_autopsy.py` then
`python src/supplement_horizon.py`.

## Provenance — read WITHOUT NinjaTrader (no recompile)

- **Reader:** `research/multi_market/src/ncd_day.py::read_ncd_day` — pure-Python NumPy parser of the
  NT8 **48-byte DAILY record** (28-byte header `int32 ver | f64 tickSize | f64 firstPrice | i64
  firstTicks`; record `i64 .NET-ticks | f64 o,h,l,c | i64 volume`). This is VOLUME00's validated
  layout (matched GetBars close+volume exactly on ES 12-11). **No `Custom.dll` recompile, no
  CrossTrade, no NT8 round-trip** was used. The db/day store serves TRUE, unmerged per-contract data
  (unlike AddDataSeries/RunStrategyBacktest, which serve merge-back-adjusted).
- **Source store:** `~/Documents/NinjaTrader 8/db/day/GC 0M-YY/<YEAR>.Last.ncd`, 91 contracts read
  after seal (97 dirs on disk; 6 are ≥2026-08 sealed / empty).
- **Contract cycle:** GC even-months `[2,4,6,8,10,12]` (`ncd_day.CYCLES["GC"]`); tick 0.10; point
  value **$100/pt** ($10/tick).

## Seal (CLAUDE.md §5)

- Every session **≥ 2026-08-01 hard-dropped at load**. Raw panel max `2026-09-04` → retained max
  **`2026-07-31`**; assertion `retained_max < 2026-08-01` **PASS** (24 contract-day rows dropped).
- Discovery window `2009-03-30 → 2026-07-31` used fully (owner: in-sample robustness, no forward
  holdout for this deliverable).

## Roll / adjustment (causal)

- **Roll method: CAUSAL volume-crossover + pre-expiry safety override**, from
  `research/multi_market/src/roll.py` (the certified TSMOM roll). The active contract for day *t* is
  chosen from **t-1 volume only** (roll when next contract's prior-day volume exceeds current's);
  one-way (never rolls backward); a 5-day pre-expiry override forces the roll from contract
  mechanics (no future price/volume). Ledger: **71 volume-crossover, 19 pre-expiry, 1 init**.
  Causality assertion (every `info_cutoff` strictly < its `decision_date`, 90 rolls): **PASS**.
- **Return construction (`ret_points`)** is the self-financing point return
  `(old_open_t − old_close_{t-1}) + (tgt_close_t − tgt_open_t)` — it **never differences two
  contracts**, so the roll basis cannot enter as P&L. Verified by an **identity gate**: this run's
  `ret_points` equals `roll.economic_returns` to machine precision (max err 0.0).
- **TWO representations (DELEV01 discipline — additive back-adjustment distorts cross-era %):**
  - **(a) `close_radj` — ratio / returns-stitched.** `cumprod(1+ret_pct)`, rebased so the last value
    equals the true last close. **Use for % returns / cross-era work.** Absolute level is rebased
    (its 2009 value ≠ the true 2009 price).
  - **(b) `close_padj`, `open_padj`, `high_padj`, `low_padj` — point-difference back-adjusted.**
    Continuous; **point changes and ranges are exact**; absolute level is offset by the cumulative
    roll basis. **Use for level / range / ATR / point-move work** (never for cross-era % thresholds).
  - **RAW `open/high/low/close`** = TRUE as-traded prices of the held contract (correct absolute
    level, e.g. $925 in 2009 → $4107 on 2026-07-31), with a basis jump at each roll — do not
    difference across a roll; use `ret_points`/`ret_pct` instead.

## Output — `out/gc_daily.parquet`

- **Rows 4,347** (one per designated trading day), span **2009-03-31 → 2026-07-31**, 91 contracts.
- **sha256** `93ec562d3ebb3ce7021855945545b3bb60365e8b090c6d62de2a675f39ed98a1`
- **Data quality:** `ohlc_bad=0, vol_neg=0, vol_zero=0, dup_contract_dates=0`.
- **Coverage note:** the per-contract cache tiles a full daily series (~250–259 return-days/yr,
  2010–2025) but has **18 short coverage holes >5 cal-days at roll handoffs** (largest: 2009-10
  start-of-history 46d, 2026-07 near-seal 24d, and Dec→Feb year-turn gaps of 12–14d). Rows whose
  return spans such a hole are flagged **`clean_daily=False` (18 rows)** and excluded from all
  daily-return statistics (**4,329 clean returns used**). `usable_start` under the strict ≤3-bd-gap
  rule is 2023-04-17 (847 fully-contiguous days) — a data-availability fact, not a returns fact.

### Schema (24 columns)

| column | meaning |
|---|---|
| `date` | session date (ET, END-stamped) |
| `open/high/low/close` | **RAW** true held-contract OHLC (as-traded level; roll jumps present) |
| `volume` | held-contract daily volume |
| `held_contract` / `old_contract` | designated contract on *t* / on *t-1* |
| `rolled` | 1 if the designated contract changed on *t* (70 roll days) |
| `ret_points` | self-financing point return (basis-free; telescopes to Δclose on no-roll days) |
| `ret_pct` | `ret_points / old_close_prev` — **the causal daily % return** (use for all return work) |
| `overnight_pts/pct`, `intraday_pts/pct` | overnight (old contract) vs intraday (target) decomposition |
| `old_close_prev` | prior-day close of the contract held into *t* (the capital base) |
| `close_true` | = raw close (explicit) |
| `close_padj`, `open_padj`, `high_padj`, `low_padj` | **point-diff back-adjusted** continuous (level/range) |
| `close_radj` | **ratio/returns-stitched** continuous (cross-era %) |
| `cal_gap_days` | calendar days since prior return day |
| `clean_daily` | False if the return spans a coverage hole >5 cal-days (excluded from stats) |

### Sample (head / tail)

```
date        open    high    low     close   vol     held      rolled ret_pct   close_padj close_radj clean
2009-03-31  922.3   926.9   913.6   925.4   50355   GC 06-09  1      +0.00808  1619.7     1293.2     True
2009-04-01  928.3   935.8   920.5   928.0   44647   GC 06-09  0      +0.00281  1622.3     1296.8     True
2026-07-30  4126.7  4180.2  4085.0  4160.6  125491  GC 12-26  0      +0.01552  4160.6     4160.6     True
2026-07-31  4163.9  4170.7  4076.4  4107.0  101781  GC 12-26  0      -0.01288  4107.0     4107.0     True
```

## Other outputs

- `out/autopsy_*.csv` — 9 autopsy tables (dow, month, prev_magnitude, tails, variance_ratio,
  multiday_ac, efficiency_ratio, trend_maturation, nq_corr_by_year).
- `out/autopsy_log.txt` — full printed autopsy.
- `out/manifest.json` — machine-readable manifest.
- `REPORT.md` — findings + STEP 3 hypotheses.
- `src/gc_extract_autopsy.py`, `src/supplement_horizon.py` — the code.
