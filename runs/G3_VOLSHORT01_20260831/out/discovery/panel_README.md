# `panel_pre2022.parquet` — G3_VOLSHORT01 discovery panel

**Evidence status: `DISCOVERY_CONTAMINATED`.** Nothing derived from this panel is a result.
It exists to produce a *rule proposal* that someone else freezes and commits **before** the
one-shot confirmation read of 2022-01-01 → 2026-07-31.

Built by `runs/G3_VOLSHORT01_20260831/src/discovery/panel.py`.
Build log: `panel_build_log.txt` (every assertion, verbatim).

## The wall

`2022-01-01` is a wall. Every frame in the builder is filtered to `< 2022-01-01` at load and the
filter is asserted and printed. Panel `max(session_date)` = **2021-12-31**.

The builder calls `load_deep(..., extend=False)`, **not** `extend=True`. `extend=True` reads
`runs/SM1M_SUBSTRATE/out/nq_1m_2022_2026.parquet` and appends only the bars stamped after
2026-05-29 16:59 — every one of them post-wall, and every one of them then discarded by the
`<= 2021-12-31` filter. It cannot change a value here; it can only put post-wall bars in memory.
Output over the requested window is bit-identical.

## Rows

One row per **NQ RTH session**: one row per calendar date on which at least one bar stamped in
`09:31 … 16:00` ET exists in the certified 1-minute substrate.

- rows: **4,106**
- span: **2006-01-05 … 2021-12-31**
- distinct `session_date`: 4,106 (duplicates: 0)
- `rth_full` (has both the 09:31 and the 16:00 bar): **3,947**

Sessions are keyed on the **calendar date of the RTH bars**, not on `load_deep`'s `sid`. A
>60-minute hole in the thin overnight tape splits one exchange session into two `sid`s; RTH lies
wholly inside one calendar day, so date-keying is immune to that. The cross-check against
`sess_date` is printed in the build log.

### `session_quality` — read this before you filter

| quality | rows | meaning |
|---|---|---|
| `FULL` | 3,947 | both anchor bars present — the clean population |
| `SHORT_SESSION` | 134 | exchange holiday / half day, tape stops before 15:00 ET |
| `GAPPY` | 25 | substrate hole inside a normal-length session |

The count is ~257/year, not ~252, because **NQ trades shortened sessions on several US equity
holidays** (MLK, Presidents' Day, Good Friday, Memorial Day, July 3/4, Labor Day, the Friday
after Thanksgiving, Christmas Eve). Those sessions stop at 11:30 / 13:00 / 13:15 ET, so they have
no 16:00 bar and the **strict** `rth_ret_pts` is `NaN` on them. They are exchange holidays, not
corrupt data. `GAPPY` is the small residue of genuine substrate holes (all but two in 2006–07).

**Default recommendation:** condition on `session_quality == "FULL"` and use the strict
`rth_ret_pts`. If you want the holiday sessions in, use `rth_ret_pts_any` — but say so, and note
that a holiday session's implied-vol reading is stale by 3–5 days.

## Bar convention (this is the one that has bitten this repo before)

Bars are **END-stamped**. The bar stamped `09:31` covers `09:30:00–09:30:59`, so **its `open` is
the 09:30:00 print**. The bar stamped `16:00` covers `15:59:00–15:59:59`, so **its `close` is the
last RTH print**. There is no ±1-minute shift. Timestamps are exchange-session time (ET).

## Columns — definition and the instant each becomes KNOWN

| column | definition | known at |
|---|---|---|
| `session_date` | calendar date (ET) of the RTH bars | — (label) |
| `rth_open` | `open` of the bar stamped `09:31` = the 09:30:00 print | 09:30:00 |
| `rth_close` | `close` of the bar stamped `16:00` = the last RTH print | 15:59:59 |
| `rth_open_any` / `rth_close_any` | open of the **first** / close of the **last** RTH bar actually present — half-day tolerant; identical to the strict pair on every `FULL` session | 09:30:00 / last print |
| `session_quality` | `FULL` \| `SHORT_SESSION` \| `GAPPY` (see above) | 15:59:59 |
| `rth_high` / `rth_low` | max/min over bars stamped `09:31…16:00` | 15:59:59 |
| `rth_range_pts` | `rth_high − rth_low` | 15:59:59 |
| `rth_volume` | sum of volume over bars stamped `09:31…16:00` | 15:59:59 |
| `n_rth_bars` | count of bars stamped `09:31…16:00` | 15:59:59 |
| `first_rth_min` / `last_rth_min` | minute-of-day of the first/last RTH bar stamp (571 = 09:31, 960 = 16:00) | 15:59:59 |
| `has_0931` / `has_1600` / `rth_full` | presence flags for the two anchor bars | 15:59:59 |
| `rth_ret_pts` | `rth_close − rth_open` — **the intraday window the mechanism is about** | 15:59:59 |
| `rth_ret_log` | `log(rth_close / rth_open)` | 15:59:59 |
| `rth_ret_pts_any` / `rth_ret_log_any` | same from the tolerant anchors | last print |
| `prev_session_date` | `session_date` of the previous panel row | 09:30:00 |
| `prev_rth_close` | previous row's `rth_close_any` — the prior session's **last RTH print**. Deliberately the tolerant column: after a 13:00 half day the economically correct prior close is the 13:00 print, and using the strict one would `NaN` out the following, perfectly normal, session. | prior last print |
| `prev_rth_close_is_1600` | whether that prior close was a true 16:00 bar | prior last print |
| `overnight_ret_log` | `log(rth_open / prev_rth_close)` — the **overnight** leg of the split | 09:30:00 |
| `overnight_ret_pts` | `rth_open − prev_rth_close` | 09:30:00 |
| `overnight_gap_days` | calendar days between `prev_session_date` and `session_date` | 09:30:00 |
| `realised_vol_21` | stdev (`ddof=1`) of `rth_ret_log` over the **21 prior** sessions with a defined `rth_ret_log`. **Causal — excludes today.** | 09:30:00 (in fact prior 15:59:59) |
| `vix` `vxn` `vix9d` `vix3m` `vvix` `skew` | **daily close of the latest Cboe session STRICTLY BEFORE `session_date`** | prior day 16:15 ET, hence available at 09:30:00 |
| `<name>_asof` | the Cboe trade date the value was taken from; `< session_date` is asserted | — (audit) |

`realised_vol_21` and the six vol columns are the only columns a signal may condition on, and
they are all known before 09:30:00. `rth_open` is known **at** 09:30:00 and is the entry price.
Everything else is realised after entry.

### Which vol index

`vxn` is the **Nasdaq-100** volatility index and is the appropriate ex-ante implied variance for
NQ. `vix` is the S&P 500 index; it starts 15+ years earlier and is the deeper history. Any
specification must say which it used, and the two are not interchangeable.

## Join audit (strictly-before, asserted)

| col | joined | NaN | source starts | median lag (days) | max lag (days) |
|---|---|---|---|---|---|
| `vix` | 4,106 | 0 | 1990-01-02 | 1.0 | 5 |
| `vxn` | 3,161 | 945 | 2009-09-14 | 1.0 | 5 |
| `vix9d` | 2,824 | 1,282 | 2011-01-04 | 1.0 | 5 |
| `vix3m` | 3,157 | 949 | 2009-09-18 | 1.0 | 5 |
| `vvix` | 4,066 | 40 | 2006-03-06 | 1.0 | 21 |
| `skew` | 4,106 | 0 | 1990-01-02 | 1.0 | 5 |

`NaN` counts are sessions preceding the index's own inception (VVIX 2006-03, VXN 2009-09,
VIX3M 2009-09, VIX9D 2011-01), **not** join failures — the `viol` (lag ≤ 0) count is 0 for every
column and the builder raises if it is not. Median lag is 1 day; max lag > 1 is a weekend or an
equity-market holiday that is not a CME holiday.

## Costs (for anyone computing dollars off this panel)

NQ point value **$20**. Measured all-in execution (G2_EXEC01, 113 real round turns) is
**$20.65/ctrRT** median $20.00, p90 $35.00. A full-session 09:30→16:00 round turn must therefore
clear **≈1.03 NQ points**, not 0.9. Report net at $4.36 (commission only — a **floor**, never a
headline), **$20.65 (primary)** and $25.01.

## Inference (binding — do not use session-level t)

High-vol sessions arrive in **episodes**. Use `common.episodes(...)`, report the **episode
count** beside every statistic, and do inference by **whole-episode block bootstrap**. Where a
count enters, use `K_eff = K / (1 + (K−1)·ρ̄)` with ρ̄ printed. A session-level t may be printed
only when labelled `DIAGNOSTIC ONLY`.

### The "8-14 episodes" prior does NOT hold on this panel - measure, don't assume

Measured (see `smoke_test.txt`, reproducible via `src/discovery/smoke_test.py`), on `FULL`
sessions with a causal rolling-252 tercile:

| high state | high sessions | K@gap10 | K@gap21 | K@gap42 | rho_bar | K_eff@gap10 | top-5 share |
|---|---|---|---|---|---|---|---|
| `vix` tercile | 1,199 | 59 | 43 | 30 | 0.034 | 19.8 | 51.3% |
| `vxn` tercile | 858 | 53 | 33 | 18 | 0.026 | 22.6 | 50.5% |
| `vix > 25` | 699 | 36 | 27 | - | - | - | - |
| `vix > 30` | 379 | 21 | 17 | - | - | - | - |

At `gap_days=10` the count is **~59, not 8-14**. But K alone misleads in the other direction too:
episode sizes run 1 -> 207 sessions and **five episodes carry half of all high-state sessions**,
so 59 badly overstates independence. Quote **K, rho_bar and K_eff together**, never K alone, and
let the whole-episode block bootstrap - not the count - carry the inference.
