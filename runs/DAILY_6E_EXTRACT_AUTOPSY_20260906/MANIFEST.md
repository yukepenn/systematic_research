# MANIFEST — 6E (CME Euro FX) DAILY extract + autopsy

**Run:** `runs/DAILY_6E_EXTRACT_AUTOPSY_20260906/` · FX pod Wave-1 deliverable · 2026-09-06
**Class:** DISCOVERY_CONSUMED, DESCRIPTIVE. No ledger trial, no P&L claim, no promotion. $0 spent.

## Could the `.ncd` be read without NT8? — **YES**

Read with a **pure-Python** parser, no NT8 / no CrossTrade / no `Custom.dll` recompile. The 48-byte
DAY record layout (resolved by VOLUME00, validated against `GetBars` on ES 12-11 close+volume) is
`research/multi_market/src/ncd_day.py::read_ncd_day`:

```
header 28 bytes : int32 version | float64 tickSize | float64 firstPrice | int64 firstTicks
record 48 bytes : int64 .NET-ticks | float64 O | float64 H | float64 L | float64 C | int64 volume
```

We **reused** that reader plus the certified causal roll (`roll.py` s6) and the basis-invariant
self-financing return (`roll.py::economic_returns` s7). **Faithfulness check: our `ret_points`
reproduces `research/multi_market/out/economic_returns.parquet` (6E leg) to `max_abs_err = 0.0`
over 4,227 aligned days** — the certified transport was reused, not re-derived.

## Data seal

- Hard-dropped every session `>= 2026-08-01` at load. **Retained boundary: last session
  `2026-07-31`**; asserted `max(date) < 2026-08-01` (PASS).
- Discovery window `2009-03-30 → 2026-07-31` used fully (store floor is 2009-03-30, uniform across
  the multi-market day store — not 2009-01-01). No forward holdout withheld (engine judged on
  in-sample robustness, P1 doctrine).

## Series built (`out/6e_daily.parquet`)

| | |
|---|---|
| rows / sessions | **4,273** |
| span | 2009-03-30 → 2026-07-31 |
| contracts stitched | 71 (quarterly H/M/U/Z cycle) |
| point value | $125,000 per 1.00; tick 0.00005 = $6.25 |
| sha256 | `af70be2d857019b932be715feb8d3362233da6f9278f6e75687b121e8aa19eae` |
| NaN returns | 46 of 4,273 (1 first row + 45 at documented coverage gaps; **0 at rolls**) |
| largest coverage gap | 27 calendar days at 2016-01-04 (store outage; handled as flat, not interpolated) |

### Roll method (CAUSAL) — and the FX reality, named not implied

Causal volume-crossover roll on **t-1 volume only** + 5-day pre-expiry safety override, one-way
(`roll.py` s6; unit-tested: basis-invariance to ~1e-13, roll-causality has teeth + no leak). **6E
produces just 1 VOLUME_CROSSOVER roll and 69 PRE_EXPIRY_OVERRIDE rolls** — its stored contract
lives barely overlap (~3 sessions median), so the 6E roll is **effectively a fixed 5-day-pre-expiry
rule**. This is s6-sanctioned when volume cannot be trusted; it is stated, not implied (matches the
TSMOM_V1 caveat: "FX and CL never roll on volume").

### Two continuous series (why both — DELEV01)

- **POINT-DIFFERENCE (additive back-adjusted):** `close_add, open_add, high_add, low_add`. Daily
  point changes == `ret_points` exactly; ranges preserved; LEVELS in history shifted by the
  cumulative roll offset. Use for **level / range** work. Anchored so the most-recent value == the
  true front close (1.15500).
- **RATIO-STITCHED (multiplicative):** `close_ratio`, and `ret_pct` = the self-financing return in
  ratio form `(old_open/old_close₋₁)·(tgt_close/tgt_open) − 1`. Cross-era percent-safe. Use for
  **% / return** work. **DELEV01** (additive back-adjust distorts cross-era percent thresholds) is
  exactly why this second series exists — demonstrated: 2009 `close_add` 1.554 vs `close_ratio`
  1.606 for the identical raw front close 1.316.
- Also carried: raw held-front `open/high/low/close/volume` (true unadjusted prices),
  `overnight_points`/`intraday_points` decomposition, `contract`, `rolled`, `roll_dist`, `ret_usd`.

### Sample (head / tail)

```
2009-03-30  6E 06-09  O 1.3230 H 1.3288 L 1.3114 C 1.3164  vol 163052   (first bar; ret NaN)
2009-03-31  6E 06-09  C 1.3283  ret_pct +0.904%  ret_points +0.0119  ret_usd +1487.5
2026-07-30  6E 09-26  C 1.15550 ret_pct +0.710%  ret_points +0.00815 ret_usd +1018.75
2026-07-31  6E 09-26  C 1.15500 ret_pct -0.043%  ret_points -0.00050 ret_usd  -62.50
```

## Files

- `src/extract_6e.py` — STEP 1 (reuses `ncd_day`/`roll`/`contract_truth`; builds parquet + `extract_meta.json`; also emits `nq_daily_for_corr.parquet`).
- `src/autopsy_6e.py` — STEP 2 (all §9 tables; writes `autopsy.txt` + `autopsy_*.csv/json`).
- `out/6e_daily.parquet` — the deliverable series (19 cols, schema above).
- `out/autopsy_*.csv|json`, `out/autopsy.txt` — autopsy tables.
- `REPORT.md` — autopsy findings + STEP 3 preregisterable hypotheses.

## Guards honored

No git run · `research/genesis/SEARCH_LEDGER.jsonl` untouched · writes confined to this run dir ·
no NT8 recompile · seal asserted before any statistic · no order/strategy/live action of any kind.
