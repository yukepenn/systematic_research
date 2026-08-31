# XM_CONFLICT — EXECUTION BUDGET

**Run** `G3_XMLAT_01_20260831` · preregistered `spec.yaml`, committed before any result existed
**Status** RESEARCH ONLY. `live_enabled: NO` · `spend: 0` · `orders_placed: NO` · no CrossTrade/NT8 call was made
**Every figure here is printed by** `src/g3_xmlat.py` **into** `out/console.txt` **and** `out/gates.json`.

This document answers one question: *how late can an XM order be before its edge is gone, and what
does the market actually charge for being late?* It is a budget, not a permission.

---

## 1. The causally admissible decision time

| item | value | source |
|---|---|---|
| anchor | OPEN of the bar stamped 09:31 = the 09:30:00 print | `WeeklyEdgeXMConflict_v4.cs:33` |
| decision | CLOSE of the bar stamped 09:45 = last print before **09:45:00.000** | `.cs:34`, `export_xm_reference.py:38` |
| **earliest causally admissible order instant** | **09:45:00.000 ET** | derived; the decision uses no data after it |
| modelled fill | OPEN of the bar stamped 09:46 = **first print at or after 09:45:00.000** | `.cs:40` |
| exit decision | 15:45:00.000 ET; modelled fill = first print at or after it | `.cs:41` |

The modelled fill is **not a fill from the future.** It is the first causally eligible price, and it
assumes **exactly zero latency** between the bar-close event and the exchange match. Gate **X1-NEG**
proves this directly: with every NQ/ES/RTY/YM price from 09:46 onward replaced by volatility-matched
white noise on all 1,187 sessions, the decision series (`nq_drive`, `broad_composite`,
`conflict_flag`, `desired_direction`) is **bit-identical on 100.0000 % of 1,186 in-window sessions**,
composite max |diff| exactly `0.000e+00`, while the entry price itself changed on 100 % of sessions.
There is no look-ahead. The whole question is what happens in the milliseconds after 09:45:00.000.

---

## 2. Signal half-life and the measured decay curve

Two instruments, two populations. They are never mixed without saying so.

### 2a. Sub-second, from tick+BBO (n = 33 XM-decision sessions, 2025-08-11 → 2026-07-31)

Slippage = `−dir × (P(delay) − P(+0 ms)) × $20`. Negative = the delay cost money.
Bootstrap 95 % CI, 20,000 resamples.

| delay | mean $/contract | 95 % CI | median | mean ticks | p(adverse) | MID-only (bounce removed) |
|---|---|---|---|---|---|---|
| +50 ms | **+2.73** | [−7.58, +11.82] | +5.00 | +0.55 | 0.333 | +9.92 |
| +100 ms | **+2.27** | [−8.48, +13.48] | +5.00 | +0.45 | 0.364 | −6.08 |
| **+250 ms** | **−11.06** | [−36.52, +10.00] | −10.00 | −2.21 | 0.545 | **−13.92** |
| +500 ms | −24.55 | [−53.18, +1.36] | −20.00 | −4.91 | 0.606 | −21.83 |
| **+1 s** | **−27.73** | [−63.03, +3.49] | −25.00 | −5.55 | 0.606 | **−21.42** |
| +2 s | −47.88 | [−102.42, +2.12] | −30.00 | −9.58 | 0.697 | −51.92 |
| +5 s | −119.24 | [−203.64, −34.55] | −95.00 | −23.85 | 0.667 | −117.58 |
| +10 s | −63.18 | [−161.06, +28.64] | −75.00 | −12.64 | 0.576 | −58.92 |
| +30 s | −73.18 | [−212.73, +64.40] | −30.00 | −14.64 | 0.576 | −78.33 |
| +60 s | −132.27 | [−324.55, +51.21] | −120.00 | −26.45 | 0.606 | −158.67 |

**n = 33 on every row.** Only the +5 s CI excludes zero, and the ladder is not monotone at +10 s /
+30 s. This curve establishes an ORDER OF MAGNITUDE, not a point.

### 2b. Across minutes, from 1-minute bars (n = 371 trades, 239 ISO weeks, 2022-01-03 → 2026-07-31)

| fill | delay | net $/wk | $/trade | Δ$/wk | t | block-bootstrap p |
|---|---|---|---|---|---|---|
| open(09:46) *incumbent* | +0 s | 730.13 | 470.35 | — | — | — |
| close(09:46) | +59 s | 679.75 | 437.90 | −50.38 | −1.89 | 0.1282 |
| open(09:47) | +60 s | 679.75 | 437.90 | −50.38 | −1.91 | 0.1246 |
| open(09:48) | +120 s | 691.95 | 445.75 | −38.18 | −1.10 | 0.2857 |
| open(09:50) | +240 s | 678.01 | 436.78 | −52.11 | −1.11 | 0.2328 |
| WORST within 09:46 | — | 328.66 | 211.72 | −401.46 | −14.59 | 0.0000 |
| BEST within 09:46 | — | 1070.92 | 689.89 | +340.79 | +14.68 | 0.0000 |

`close(09:46)` and `open(09:47)` are distinct prices on **81.4 %** of armed sessions — two
measurements, not one printed twice.

### 2c. Half-life

Population-matched on the same 33 tick sessions: the **first second costs 21 %** of what the first
**minute** costs, and the first **250 ms costs 8 %**. Against those sessions' own $435.72/trade
after-cost edge, the loss is **2.5 % at 250 ms, 6.4 % at 1 s, 30.4 % at 60 s**.

**There is no clean exponential half-life.** The surface is sub-linear in time, closer to
√t (diffusive) than to exponential decay. The honest statement is the shape, not a half-life
constant: *the market does not run away from this signal on a millisecond clock; it runs away on a
minute clock.*

---

## 3. Break-even latency

The delay at which XM's expected after-cost edge reaches zero. Three functional forms × two
populations, all printed because none of them is right on its own.

| population | after-cost edge | LINEAR | **√t (diffusive)** | LOCAL@1 s (most pessimistic) |
|---|---|---|---|---|
| tick subsample, n = 33 | $435.72/trade | 197 s (3.3 min) | **636 s (10.6 min)** | **16 s (0.3 min)** |
| all trades, n = 371 | $470.35/trade | 2,743 s (45.7 min) | 35,672 s (594 min) | 69 s (1.2 min) |

**Span: 16 s to 35,672 s.**

The tightest figure, **16 seconds**, is the most pessimistic construction that can be built from
this data: it takes the steepest measured local slope, on the most latency-sensitive session set we
own, and extrapolates it *linearly* when the measured surface is visibly sub-linear.

**Even 16 s is 63× a 250 ms fill.** A 250 ms order path spends **1.6 % of the pessimistic budget**
and 0.0007 % of the optimistic one. Latency is not the binding constraint on this strategy.

---

## 4. Measured spread at the decision instant

93 owned tick sessions, 87 with a reconstructable BBO at 09:45:00.000; 85 at 15:45:00.000.

| instant | measured spread (instantaneous) | measured (1 s median) | W82 committed model | charged |
|---|---|---|---|---|
| 09:45:00.000 (entry) | **3.00 tk** median, 5.15 mean, 8.00 p90 | 4.00 tk | 3.0 tk at minute 586 | $7.50/leg |
| 15:45:00.000 (exit) | **3.00 tk** median | 3.00 tk | 2.0 tk at minute 946 | $5.00/leg |
| round turn | **$15.00/ctrRT** | $17.50/ctrRT | **$12.50/ctrRT** | $12.50 + $4.36 comm = $16.86 |

The W82 entry-minute spread is **corroborated to the tick** by an independent measurement made from
a different data store. The exit minute is under-modelled by 1 tick.

Two caveats stated rather than buried:
- Bid and Ask arrive as two independent event streams on a 4 ms clock. Forward-filling one against
  the other produces occasional crossed reconstructions (median crossed fraction 0.002 over the
  preceding second) — an artefact of interleaving, not a crossed market. Hence three estimators.
- `XM_EXEC_COST_AUDIT_V1_20260831` measured $18.42/ctrRT from *realised fills*; this run measures
  $15.00–$17.50/ctrRT from *quoted BBO*. Different estimators of the same object; both say the
  $12.50 model is mildly optimistic and the economic size is single-digit dollars per week.

**The one execution cost the incumbent really does under-book, and it is not latency:** the modelled
fill is a PRINT, but a market order fills at the FAR SIDE of the quote. Measured
V1 − V0 = **−$11.50/contract** (median −$5.00, n = 30) against $7.50 charged for the entry leg —
an unbooked residue of **$4.00/contract = $6.21/week**.

---

## 5. Recommended order semantics

Recommendations about *how* to send the order the strategy already decides to send. **Nothing here
changes which trades occur, and nothing here is a promotion.**

1. **Send a market order at the 09:45 bar close, exactly as the certified class does.** Measured
   quote-crossing cost is $11.50/contract against a per-trade edge of $470. The strategy's problem
   is not the spread.
2. **Do not add a limit price to chase the modelled print.** The three policy variants measured
   (immediate marketable; marketable limit at the causally known 09:45:00 quote ± 1 tick; limit at
   the touch with a 60 s give-up) all filled 30/30 on quotable sessions, so none of them changed
   which trades occur *in this sample* — but n = 30, and "limit at the touch" was scored with
   **no queue model**, so its +$12.67/contract apparent gain is an upper bound produced by a
   fill rule that cannot be relied on. Any variant that ever declines a trade becomes a POLICY
   CHANGE and inherits the full challenger burden on its own population.
3. **Budget: 250 ms end-to-end is comfortable; 1 s is comfortable; 60 s is not.** The measured cost
   at 60 s is 30 % of the per-trade edge on the sessions where we can see it.
4. **The exit is not the exposure.** +1 minute on the exit costs $-11.43/wk (t −0.84, bootstrap
   p 0.36) on the source population and $-13.74/wk (t −1.08, p 0.24) on the wider one. Neither is
   distinguishable from zero.

---

## 6. Monitoring threshold

A live threshold that can be evaluated from the strategy's own export, without new instrumentation.

| what to watch | threshold | why that number |
|---|---|---|
| wall-clock delay from the 09:45 bar-close callback to the exchange fill timestamp | **alert > 1 s, halt-and-review > 5 s** | 1 s costs 6.4 % of the per-trade edge; 5 s is the first delay whose measured cost CI excludes zero (−$119.24, [−203.64, −34.55]) |
| realised fill price vs the 09:45:00 far-side quote | **alert if the 20-trade rolling mean is worse than −$25/contract** | measured V1 − V0 is −$11.50 ± ; −$25 is a doubling |
| age of the ES/RTY/YM secondary series at 09:45:00 | **any secondary older than 1 bar at the decision instant** | see §7 — this is the real open risk, and `MaxStaleMinutes = 3` is a SESSION-level rule that does not see it |
| quoted spread at 09:45:00 | **alert > 8 ticks** (the measured p90) | above the 90th percentile of the 87 sessions measured here |

---

## 7. The open execution risk that this run did NOT close

The 09:45 decision reads ES, RTY and YM. In NT8 these are separate `BarsInProgress` series. **If a
secondary series is stale at 09:45:00 live, the live decision differs from the backtest decision for
a reason that has nothing to do with latency.** The staleness rule
(`MAXSTALE = 3`, `export_xm_reference.py:39,:89-93`; `MaxStaleMinutes` in the `.cs`) is a
**SESSION-level** disqualification and does not protect against intraday staleness.

Gate **X1-POS** shows exactly how much this matters: perturbing ONE market's 09:45 close by
±0.5 σ of its own 60-session sigma flips `desired_direction` on **17.40 %** of the 1,155 sessions
with a computable composite (23.45 % of armed sessions). A structural note worth recording: the
flip rate is **identically 17.40 % for ES, RTY and YM**, and that is not a coincidence. The
composite is `mean_k( r_k / σ_k )`, so a ±0.5 σ_k shock to any market moves it by exactly
±0.5/count. **Every cross-market leg has exactly equal marginal influence on the action.** A stale
YM feed is as dangerous as a stale ES feed.

This risk is *larger* than the latency risk measured in this document and is not addressed by any
order-routing choice. It is reported as an open item.

---

## 8. The honest limits of what simulated fills can teach us

1. **A shallow price decay does not prove the fill is achievable.** It proves the PRICE does not move
   much. Queue position, order rejection and partial fills are separate risks, measured by no price
   series in this run and not claimed to be.
2. **The tick sample is not a random sample of history.** 93 sessions, all in
   2025-08-11 → 2026-07-31, selected by what happened to be exported. Gate **X3-C** quantifies the
   damage: on the *identical* 1-minute +60 s measurement the tick subsample is **4.08× as
   latency-sensitive** as the full trade population. Every sub-second number extrapolated from it
   inherits that factor, and the run states the adjusted value beside the raw one everywhere.
3. **n = 33 clears the spec's n ≥ 20 bar but is still thin.** Only the +5 s CI excludes zero.
4. **The remedy is extraction, not purchase.** The NT8 native store holds **187 pre-seal NQ sessions
   with Last + Bid + Ask payload**; only **93** have been extracted to parquet. Intersecting the 187
   with XM's trade dates gives **59** — so extraction would raise the conditional n from **33 to 59**,
   a 79 % increase (≈1.34× narrowing of the CI), at **$0**. Extraction requires a NinjaScript export
   through `RunStrategyBacktest` and is forbidden in this run; it is named here as a scoped next task.
5. **This is an in-sample object.** The 1-minute side is DIRECTLY_BURNED across the whole window.
   The tick side is a slice that was never used to fit XM. The product is a mixture and is quoted as
   an estimate, never as an out-of-sample result.
6. **Sub-second |Δ price| is mostly bid-ask bounce, not drift.** Median |ΔLAST| at +50 ms is 3.00
   ticks — exactly the median quoted spread. Reading the LAST-price ladder as if it were a drift
   measurement would roughly triple the apparent latency cost. Both ladders are printed.

---

## 9. Data provenance and exclusions

| store | files | used | excluded |
|---|---|---|---|
| `research/data_microstructure_v2/raw/NQ/` | 58 | 58 | `s20260525` — `QUARANTINE:short_span` in `quality/qa.csv`, absent from `MANIFEST.csv`, no parquet present. **Excluded, and the exclusion is asserted rather than assumed.** |
| `research/scalping_lab/substrate/raw/NQ/` | 61 (48 base + 13 `_rth`) | 35 | 13 base files at **exactly 12,000,000 rows** — the old export cap. `s20251117 s20251124 s20260206 s20260220 s20260223 s20260303 s20260312 s20260320 s20260423 s20260428 s20260506 s20260519 s20260520`. The truncation is a TAIL truncation (files stop 13:28–16:45 ET) and does not touch 09:45, but they are excluded as instructed. |
| union, deduplicated by session date | — | **93** | 0 date collisions after the truncation filter |

**SEAL.** Nothing at or after 2026-08-01 was read. The 1-minute substrate is loaded to
`2026-07-31 17:00` and the loader asserts no bar ≥ 2026-08-01 exists. The tick index refuses any
session dated 2026-08-01 or later. **Explicitly excluded by the seal:** the 9 NQ full-BBO tick
sessions dated 2026-08-01 → 2026-08-11 in `NT8_CAPABILITY_CENSUS.csv` (196 total − 187 pre-seal).
