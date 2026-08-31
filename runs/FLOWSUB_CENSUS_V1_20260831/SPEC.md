# SPEC — `FLOWSUB_CENSUS_V1` · verify the flow-substrate count, then STAGE 0. **DATA-ONLY + CORRELATIONS.**

> ⚠️ **PROVENANCE HONESTY.** This file was written **after** the run, transcribed verbatim from the
> docstrings of `src/flowsub_census.py`, `src/reconcile.py` and `src/stage0.py`, where every
> definition was frozen **before** the corresponding numbers were produced. It is therefore a
> **RULE RECORD, not a preregistration**, and must not be cited as one. The scripts are the
> authority; this file is a pointer.

| | |
|---|---|
| **question 1** | Is the claim "NQ tick store = **319** trade-bearing dates (**196** quote-bearing + **123** Last-only)" true, and is it the same object as `DATA_CENSUS_20260826`'s credited **48**? |
| **question 2 (STAGE 0)** | Can a trade-only proxy (CLV) reproduce BBO-measured signed flow? Can a tick-rule classification extend signed flow into Last-only dates? How much information is BBO-exclusive? |
| **run class** | question 1 = **metadata only** (file names + sizes; plus the `i64 firstTicks` header field on pre-burn already-consumed files, to verify the hour-label map). question 2 = correlations on **already-materialized, already-outcome-consumed** sessions. |
| **forbidden and not done** | no P&L, no cost model, no position, no threshold search, no candidate. Nothing `>= 2026-08-01` opened. No file in the frozen blind BBO pool opened (asserted in `stage0.guard()`). The 141-session Last-only pool not opened. No DOM/L2/Replay collection. No order, no deploy, no strategy state change. |

## Definitions frozen in code before the numbers

1. `db/tick/<INSTRUMENT>/yyyyMMddHH00.<Last|Bid|Ask>.ncd`, hourly buckets.
2. **hour label → exchange time**: label `L` on stem date `C` covers ET hour `L-1` of `C`;
   `L=0` covers ET 23:00–23:59 of `C-1`. Verified this run against 24 file headers.
3. **payload**: header is 28 bytes; `size <= 32` ⇒ EMPTY RESIDUE ⇒ counted ABSENT.
4. **session** `s(D)` = ET `D-1` 18:00 → `D` 17:00 = 23 hour slots: labels 19–23 on `D-1`,
   label 00 and labels 01–17 on `D`. Label 18 (ET 17:00) is the maintenance break.
5. **RTH** = ET 09:30–16:00 ⇒ labels 10–16.
6. **eras**: `PRE_BURN < 2026-05-31`; `BURNED 2026-05-31..2026-07-31`; `SEALED >= 2026-08-01`.
7. **quote rule (Lee-Ready)**: prevailing bid/ask = last Bid/Ask event strictly earlier in the
   as-recorded stream; `sign(price − mid)`; ties fall back to the tick rule.
   **tick rule**: sign of the change vs the previous *different* trade price.
8. **bar** = 1 minute of ET time built from trades only; `CLV = (C−L)/(H−L) − 0.5`, `0` when `H==L`.

## Artifacts

| file | what |
|---|---|
| `out/tick_file_inventory.csv` | every `.ncd` in `db/tick`: root, instrument, stem date, hour label, series, bytes, payload flag |
| `out/sessions_{NQ,MNQ,ES}.csv` | session-level coverage table |
| `out/reconcile_dates.csv` · `out/reconcile.txt` | every circulating count recomputed against one inventory |
| `out/census.txt` | census log incl. label-map verification and file health |
| `out/stage0_*.csv` · `out/stage0.txt` | STAGE 0 diagnostics, pooled and per-session |
