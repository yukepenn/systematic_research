# V4 + V4a — FRICTION SHARE LEDGER AND COMMISSION SENSITIVITY BAND

Run: `W17_C4_COMPLIANCE` · Script: `runs/W17_C4_COMPLIANCE/src/v4_friction.py` (reproduces every
number below from committed artifacts; no NT8/CrossTrade call was made).
Window: dev only, **session dates 2022-01-03 .. 2026-05-29 (1,139 sessions)**.
Nothing at or after 2026-08-01 was read. Nothing from 2006-2021 was read. Product A's fill export
runs to 2026-07-31; the 1,056 post-dev fills (174 cycles) were **excluded from every figure here**.

This is a measurement report. **It establishes nothing about future profitability.**

---

## 0. Definitions (stated once, used everywhere)

| Symbol | Meaning |
|---|---|
| `slip_$` | **Measured** adverse fill displacement vs the fill bar's reference price (bar OPEN for a next-bar market fill; bar CLOSE for an ExitOnSessionClose backstop fill), signed so positive = cost. Not assumed — read off the bars. |
| `G_raw` | Gross P&L at unslipped reference prices = `G + slip_$` |
| `G` | Gross P&L after slippage, **before** commission = `net + commission` |
| `comm` | Commission actually charged in the backtest |
| `net` | P&L after slippage and commission (NT8 `ProfitCurrency` / fill-ledger cash) |
| **`FS_comm`** | **`comm / G`** — the narrow, commission-only friction share the directive asked for. `FS_comm >= 1.0` means commission alone exceeded the after-slippage gross, i.e. the object is net-negative. |
| **`FS_house`** | **`(comm + slip_$) / G_raw`** — the definition already in the repo (`runs/SMV2U_CLOCK_CHALLENGE/step1_clock_arms.py`, `runs/SMV2AE_1MIN_RESCALE/step2_rescaled_ensemble.py`), i.e. the one behind the **1.020 / 0.470** 1-minute numbers. Reported so this run is comparable to those. |

**Both ratios are only meaningful when the denominator is positive.** Any subset with
`G <= 0` prints `n/a (gross<=0)` rather than a ratio — see BEST_ONE_MNQ 2026, where gross is
negative and a friction ratio would be arithmetically defined but semantically meaningless.

**Daily aggregation.** Every Sharpe below is computed on **NT8 session dates (18:00 ET roll)**,
taken from each object's own 3-minute bar grid (session date = calendar date of the session's
*last* bar), **not** calendar date of the timestamp. Series are zero-filled across all 1,139 dev
sessions; `Sharpe = mean/std(ddof=1)*sqrt(252)` — the house convention in `src/analytics/sm_metrics.py`.
The NQ and MNQ grids independently yield 1,139 dev sessions; the MNQ raw grid and the Master-v2
decision-bar grid agree on the session date for **519,702 / 519,702 (100%)** overlapping bars.

**Recency tiers (trailing 2y / trailing 1y) are DISCLOSURE ONLY, never selection.** No parameter,
object, or ranking in this campaign is or may be chosen using them.

---

## 1. Headline ledger — full dev window

| | **Product A**<br>SolarWaveSMMaster_v2 | **BEST_ONE_NQ** | **BEST_ONE_MNQ**<br>*(PROVISIONAL)* |
|---|---:|---:|---:|
| Instrument executed | MNQ (multi-contract) | NQ (1 lot) | MNQ (1 lot) |
| Point value / tick $ | $2.00 / $0.50 | $20.00 / $5.00 | $2.00 / $0.50 |
| Coded round-turn commission | $1.30 /contract | $4.36 | $1.30 |
| Round turns | 4,711 flat-to-flat cycles<br>(**18,443 contract-RT**) | 1,975 | 1,561 |
| `G_raw` (before all friction) | $219,403.00 | $331,255.00 | $32,445.50 |
| `slip_$` (measured) | −$18,112.00 | −$19,195.00 | −$1,515.50 |
| `G` (after slip, before comm) | $201,291.00 | $312,060.00 | $30,930.00 |
| `comm` | −$23,975.90 | −$8,611.00 | −$2,029.30 |
| **`net`** | **$177,315.10** | **$303,449.00** | **$28,900.70** |
| **`FS_comm` = comm / G** | **0.1191** | **0.0276** | **0.0656** |
| **`FS_house` = (comm+slip)/G_raw** | **0.1918** | **0.0839** | **0.1093** |
| comm / gross winning P&L | 0.0210 | 0.0041 | 0.0093 |
| avg gross per round turn | $42.73 /cycle | $158.01 | $19.81 |
| avg commission per round turn | $5.09 /cycle | $4.36 | $1.30 |
| avg net per round turn | $37.64 /cycle | $153.65 | $18.51 |
| win rate (net) | 0.2534 | 0.4177 | 0.4676 |
| payoff (avg win / \|avg loss\|) | 3.4916 | 1.6301 | 1.3134 |
| profit factor (net) | 1.1854 | 1.1694 | 1.1538 |
| avg win / avg loss ($) | $949.61 / −$271.97 | $2,539.26 / −$1,557.78 | $296.99 / −$226.12 |
| daily vol ($) | $2,109.06 | $3,785.91 | $437.24 |
| **daily Sharpe** | **1.1717** | **1.1171** | **0.9212** |

**Same ledger denominated in ticks, per CONTRACT round turn** (this is the cleanest way to see the
edge-vs-friction geometry, because commission and slippage are fixed in ticks while gross is not):

| Object | gross_raw | − slip | − comm | = net | friction as % of gross_raw |
|---|---:|---:|---:|---:|---:|
| Product A (MNQ) | 23.793 t | 1.964 t | 2.600 t | **19.228 t** | 19.2% |
| BEST_ONE_NQ | 33.545 t | 1.944 t | 0.872 t | **30.729 t** | 8.4% |
| BEST_ONE_MNQ *(prov.)* | 41.570 t | 1.942 t | 2.600 t | **37.028 t** | 10.9% |

**Cross-checks (all pass exactly).** Product A's net rebuilt independently from the 26,881-row fill
ledger = **$177,315.10**, delta vs the committed `nt8_dev_battery.csv` `NT8_EXECUTABLE_dev` row =
**$0.00** (4.4e-08). BEST_ONE_NQ dev net $303,449.00 and BEST_ONE_MNQ dev net $28,900.70 both match
`parity_nq.json` / the trade files to the cent. My Product A daily vol is $2,109.058 vs the battery's
$2,109.452 (Sharpe 1.17173 vs 1.17153) — a 0.02% difference from session attribution of a handful of
boundary fills; **disclosed, not swept**. Net is identical.

---

## 2. Per-year and recency decomposition

*Recency tiers are DISCLOSURE ONLY, never selection. Trailing windows are anchored at the dev end
2026-05-29; "2026" is a partial year (106 sessions, through 2026-05-29).*

### Product A — SolarWaveSMMaster_v2

| Slice | Sess | Cycles | G_raw $ | slip $ | G $ | comm $ | net $ | FS_comm | FS_house | Sharpe | breakeven comm mult |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FULL DEV | 1139 | 4711 | 219,403 | 18,112 | 201,291 | 23,975.90 | **177,315.10** | 0.1191 | 0.1918 | **1.1717** | 8.40x |
| 2022 | 258 | 1048 | 57,322 | 4,505.5 | 52,816.5 | 5,964.40 | 46,852.10 | 0.1129 | 0.1827 | 1.2371 | 8.86x |
| 2023 | 258 | 1073 | 26,184 | 3,959.5 | 22,224.5 | 5,262.40 | 16,962.10 | 0.2368 | 0.3522 | 0.8359 | 4.22x |
| 2024 | 259 | 1033 | 41,774 | 3,945.5 | 37,828.5 | 5,226.00 | 32,602.50 | 0.1381 | 0.2196 | 1.2859 | 7.24x |
| 2025 | 258 | 1080 | 78,164.5 | 3,975.5 | 74,189.0 | 5,255.90 | 68,933.10 | 0.0708 | 0.1181 | 1.5600 | 14.12x |
| 2026 (partial) | 106 | 477 | 15,958.5 | 1,726.0 | 14,232.5 | 2,267.20 | 11,965.30 | 0.1593 | 0.2502 | 0.6763 | 6.28x |
| TRAILING 2Y *(disclosure only)* | 517 | 2145 | 122,926 | 7,963 | 114,963 | 10,522.20 | 104,440.80 | 0.0915 | 0.1504 | 1.3083 | 10.93x |
| TRAILING 1Y *(disclosure only)* | 259 | 1104 | 58,547.5 | 3,851.5 | 54,696.0 | 5,083.00 | 49,613.00 | 0.0929 | 0.1526 | 1.2523 | 10.76x |

### BEST_ONE_NQ

| Slice | Sess | RT | G_raw $ | slip $ | G $ | comm $ | net $ | FS_comm | FS_house | Sharpe | breakeven comm mult |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FULL DEV | 1139 | 1975 | 331,255 | 19,195 | 312,060 | 8,611.00 | **303,449.00** | 0.0276 | 0.0839 | **1.1171** | 36.24x |
| 2022 | 258 | 443 | 121,250 | 4,290 | 116,960 | 1,931.48 | 115,028.52 | 0.0165 | 0.0513 | 1.8710 | 60.56x |
| 2023 | 258 | 454 | 33,120 | 4,410 | 28,710 | 1,979.44 | 26,730.56 | 0.0689 | 0.1929 | 0.7196 | 14.50x |
| 2024 | 259 | 440 | 78,445 | 4,250 | 74,195 | 1,918.40 | 72,276.60 | 0.0259 | 0.0786 | 1.3963 | 38.68x |
| 2025 | 258 | 453 | 95,890 | 4,455 | 91,435 | 1,975.08 | 89,459.92 | 0.0216 | 0.0671 | 1.1368 | 46.29x |
| **2026 (partial)** | **106** | **185** | **2,550** | **1,790** | **760** | **806.60** | **−46.60** | **1.0613** | **1.0183** | **−0.0014** | **0.94x** |
| TRAILING 2Y *(disclosure only)* | 517 | 891 | 142,710 | 8,655 | 134,055 | 3,884.76 | 130,170.24 | 0.0290 | 0.0879 | 0.8809 | 34.51x |
| TRAILING 1Y *(disclosure only)* | 259 | 446 | 60,510 | 4,345 | 56,165 | 1,944.56 | 54,220.44 | 0.0346 | 0.1039 | 0.7799 | 28.88x |

### BEST_ONE_MNQ — **PROVISIONAL**

*This object never submits a voluntary exit order (KNOWN_ERRORS #7 arrangement): 67.6% of exits are
the 17:00 session-close backstop and 30.9% are managed auto-reversals. Measured here: 1,077 of 1,561
exits (69.0%) land on the session's last bar. Every number in this section is provisional.*

| Slice | Sess | RT | G_raw $ | slip $ | G $ | comm $ | net $ | FS_comm | FS_house | Sharpe | breakeven comm mult |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FULL DEV | 1139 | 1561 | 32,445.5 | 1,515.5 | 30,930.0 | 2,029.30 | **28,900.70** | 0.0656 | 0.1093 | **0.9212** | 15.24x |
| 2022 | 258 | 350 | 10,673.5 | 341.0 | 10,332.5 | 455.00 | 9,877.50 | 0.0440 | 0.0746 | 1.4239 | 22.71x |
| 2023 | 258 | 345 | 7,124.5 | 329.0 | 6,795.5 | 448.50 | 6,347.00 | 0.0660 | 0.1091 | 1.4465 | 15.15x |
| 2024 | 259 | 360 | 3,367.0 | 349.5 | 3,017.5 | 468.00 | 2,549.50 | 0.1551 | 0.2428 | 0.4109 | 6.45x |
| 2025 | 258 | 352 | 14,346.5 | 344.5 | 14,002.0 | 457.60 | 13,544.40 | 0.0327 | 0.0559 | 1.4866 | 30.60x |
| **2026 (partial)** | **106** | **154** | **−3,066.0** | **151.5** | **−3,217.5** | **200.20** | **−3,417.70** | **n/a (gross<=0)** | **n/a (gross<=0)** | **−0.9092** | **n/a** |
| TRAILING 2Y *(disclosure only)* | 517 | 712 | 12,614 | 696.0 | 11,918 | 925.60 | 10,992.40 | 0.0777 | 0.1286 | 0.6399 | 12.88x |
| TRAILING 1Y *(disclosure only)* | 259 | 359 | 5,343.5 | 351.0 | 4,992.5 | 466.70 | 4,525.80 | 0.0935 | 0.1530 | 0.5809 | 10.70x |

### The negative result that matters most

**BEST_ONE_NQ is net-negative in 2026 to date (−$46.60 over 106 sessions), and its 2026 friction
share exceeds 1.0 (`FS_comm` = 1.0613).** Gross before all friction was +$2,550 (2.757 ticks per
round turn); slippage took 1.935 ticks and commission 0.872 ticks, total 2.807 ticks — more than the
whole gross edge. This is exactly the regime the 1-minute unscaled arm was killed for
(friction share 1.020). It is a 106-session slice, so it is weak evidence about the mechanism — but
it is DIRECT evidence that this object's gross edge per trade can fall to the friction floor within
the dev window itself.

**BEST_ONE_MNQ 2026 is worse and differently worse: its gross is negative BEFORE any friction**
(−$3,066 at unslipped prices, −39.8 ticks per round turn). That is a signal failure, not a friction
failure, and no commission assumption rescues it. Product A is the only one of the three still
net-positive in 2026 (+$11,965.30, Sharpe 0.68 — its own weakest full-slice Sharpe after 2023).

---

## 3. Slippage — DIRECT evidence

**Question asked:** the Product B backtests were configured with 1-tick slippage
(`runs/PRODUCTB_ONECONTRACT_FINAL/spec.yaml`, sub_439b). Is that slippage actually embedded in the
fill prices in these trade lists?

**Answer: YES, and it is embedded in the PRICES, not netted out of `pnl`. DIRECT evidence, three
independent tests:**

1. **Tick-grid test — passes but is uninformative.** All 3,950 NQ prices and all 3,122 MNQ prices are
   exact multiples of 0.25 (0 off-grid). This confirms nothing on its own: a 1-tick shift keeps a
   price on the grid. Reported because the directive asked for it, and flagged as non-diagnostic.
2. **Arithmetic reconciliation — exact.** `(exit_px − entry_px) × dir × point_value` equals
   `pnl + commission` for every trade, max residual **9.1e-13 (NQ)** and **5.6e-17 (MNQ)**. So the
   trade-list `pnl` is the price-difference P&L minus exactly $4.36 / $1.30 per round turn and
   **nothing else** — no separate slippage line is subtracted.
3. **Fill-price vs bar-price test — the diagnostic one.** Comparing every fill price against the
   underlying 3-minute bar (OPEN for next-bar market fills, CLOSE for session-close backstop fills):

   | Object | fills at exactly +1 tick adverse | fills at 0 ticks | 0-tick fills explained by bar-range cap |
   |---|---:|---:|---:|
   | BEST_ONE_NQ entries | 1,918 / 1,975 | 57 | **57 / 57** |
   | BEST_ONE_NQ exits | 1,921 / 1,975 | 54 | **54 / 54** |
   | BEST_ONE_MNQ entries | 1,526 / 1,561 | 35 | **35 / 35** |
   | BEST_ONE_MNQ exits | 1,505 / 1,561 | 56 | **56 / 56** |
   | Product A fills *(25,825 in-window; the other 1,056 are post-dev, no bar reference, excluded)* | 25,297 | 528 | **527 / 527** non-backstop (the 528th is a session-close fill) |

   Every fill is displaced exactly one tick against the strategy, except where the bar's own range
   truncated it (buy whose fill bar opened at its high; sell whose fill bar opened at its low) —
   which is precisely NT8's documented slippage cap and matches `src/analytics/sm01_solarsim._fill`.
   No fill is displaced by anything other than 0 or 1 tick.

**Implied slippage cost per round turn, and its share:**

| Object | measured slip $ | analytic (2 ticks/RT) | measured / analytic | $ per round turn | ticks per contract-RT | slip share of `G_raw` |
|---|---:|---:|---:|---:|---:|---:|
| Product A | $18,112.00 | $18,443.00 | 0.9821 | $3.84 /cycle | 1.964 | 8.26% |
| BEST_ONE_NQ | $19,195.00 | $19,750.00 | 0.9719 | $9.72 | 1.944 | 5.79% |
| BEST_ONE_MNQ *(prov.)* | $1,515.50 | $1,561.00 | 0.9709 | $0.97 | 1.942 | 4.67% |

**INFERENCE, flagged as such:** slippage is 2.2x commission for BEST_ONE_NQ and comparable to it for
the two MNQ objects, so any future work on execution cost should attack slippage first for NQ and
commission first for MNQ. This is a within-backtest statement. The 1-tick assumption is itself an
assumption; real fills at 16:42 on a thin holiday session are not guaranteed to be 1 tick.

**Method note (worth recording).** My first pass used "the exit bar is the session's last bar" to
pick the CLOSE as reference. That mis-priced exactly two Product A fills — new SHORT entries on the
final bar of the 2022-02-21 (13:00) and 2025-12-24 (13:15) **holiday early-close sessions**, which
fill at the OPEN, not the close. Using the ledger's own `"Exit on session close"` label instead
resolved both. This is a small independent corroboration of the v1e early-close finding in
`spec.yaml`: the objects genuinely do transact on the last bar of early-close sessions.

---

## 4. V4a — commission sensitivity band

**The exact NinjaTrader Lifetime all-in NQ/MNQ rate is NOT confirmed.** The live filtered rate table
would not render. What IS confirmed is what was **coded**: the trade lists reconcile to exactly
**$4.36 NQ / $1.30 MNQ per round turn** ($2.18 / $0.65 per side), and Product A's fill ledger carries
a per-fill commission column that is **$0.65 x qty on 26,881 of 26,881 fills** — zero exceptions.
No current rate is invented here. Instead: a band.

All rows hold gross P&L fixed and scale only the commission (i.e. they assume the strategy's
decisions do not change when the rate changes — true for a bar-close signal rule, and stated so it
is not mistaken for a re-simulation).

### Product A — SolarWaveSMMaster_v2 (coded RT $1.30 / contract)

| mult | RT rate | commission $ | net $ | Sharpe (daily) | FS_comm |
|---:|---:|---:|---:|---:|---:|
| 0.50x | $0.65 | 11,987.95 | 189,303.05 | 1.2514 | 0.0596 |
| 0.75x | $0.98 | 17,981.93 | 183,309.08 | 1.2116 | 0.0893 |
| **1.00x** | **$1.30** | **23,975.90** | **177,315.10** | **1.1717** | **0.1191** |
| 1.50x | $1.95 | 35,963.85 | 165,327.15 | 1.0922 | 0.1787 |
| 2.00x | $2.60 | 47,951.80 | 153,339.20 | 1.0126 | 0.2382 |
| 3.00x | $3.90 | 71,927.70 | 129,363.30 | 0.8537 | 0.3573 |

- **Net reaches $0 at 8.396x → RT $10.91/contract.**
- **Sharpe falls below 0.50 at 5.230x → RT $6.80/contract.**

### BEST_ONE_NQ (coded RT $4.36)

| mult | RT rate | commission $ | net $ | Sharpe (daily) | FS_comm |
|---:|---:|---:|---:|---:|---:|
| 0.50x | $2.18 | 4,305.50 | 307,754.50 | 1.1332 | 0.0138 |
| 0.75x | $3.27 | 6,458.25 | 305,601.75 | 1.1252 | 0.0207 |
| **1.00x** | **$4.36** | **8,611.00** | **303,449.00** | **1.1171** | **0.0276** |
| 1.50x | $6.54 | 12,916.50 | 299,143.50 | 1.1010 | 0.0414 |
| 2.00x | $8.72 | 17,222.00 | 294,838.00 | 1.0849 | 0.0552 |
| 3.00x | $13.08 | 25,833.00 | 286,227.00 | 1.0527 | 0.0828 |

- **Net reaches $0 at 36.240x → RT $158.01.**
- **Sharpe falls below 0.50 at 20.322x → RT $88.61.**
- **But this whole-window robustness is not uniform:** the same breakeven multiple by year is
  60.6x (2022) / 14.5x (2023) / 38.7x (2024) / 46.3x (2025) / **0.94x (2026 partial)**. In 2026 a
  **6% reduction** in the round-turn rate would have flipped the slice from −$46.60 to positive,
  and a 6% increase deepens the loss. The commission assumption is irrelevant to the 5-year headline
  and decisive for the most recent slice.

### BEST_ONE_MNQ — PROVISIONAL (coded RT $1.30)

| mult | RT rate | commission $ | net $ | Sharpe (daily) | FS_comm |
|---:|---:|---:|---:|---:|---:|
| 0.50x | $0.65 | 1,014.65 | 29,915.35 | 0.9540 | 0.0328 |
| 0.75x | $0.98 | 1,521.98 | 29,408.03 | 0.9376 | 0.0492 |
| **1.00x** | **$1.30** | **2,029.30** | **28,900.70** | **0.9212** | **0.0656** |
| 1.50x | $1.95 | 3,043.95 | 27,886.05 | 0.8884 | 0.0984 |
| 2.00x | $2.60 | 4,058.60 | 26,871.40 | 0.8557 | 0.1312 |
| 3.00x | $3.90 | 6,087.90 | 24,842.10 | 0.7903 | 0.1968 |

- **Net reaches $0 at 15.242x → RT $19.81.**
- **Sharpe falls below 0.50 at 7.461x → RT $9.70.**

### The static-rate problem, quantified

**The schedule is dated 2026-07-01 and is updated quarterly. A single static rate applied across
2022-2026 is therefore NOT the historical truth** — over ~18 quarters the rate almost certainly
moved, and exchange/regulatory fees inside the all-in number certainly did. Every backtest in this
repo, including the three above, has been run at one frozen rate. How much does that matter?

A ±25% revision (a generous single quarterly step) moves:

| Object | net range | as % of base net | Sharpe range | base Sharpe |
|---|---|---:|---|---:|
| Product A | $171,321 .. $183,309 | **6.76%** | 1.1319 .. 1.2116 | 1.1717 |
| BEST_ONE_NQ | $301,296 .. $305,602 | **1.42%** | 1.1090 .. 1.1252 | 1.1171 |
| BEST_ONE_MNQ *(prov.)* | $28,393 .. $29,408 | **3.51%** | 0.9048 .. 0.9376 | 0.9212 |

**Reading:** at the 5-year window level the static-rate error is second-order — a ±25% rate error
moves headline net by 1.4-6.8% and Sharpe by <0.05 for all three objects, and none comes within a
factor of 5 of its Sharpe-0.5 threshold. **At the slice level it is first-order:** BEST_ONE_NQ's
2026 breakeven multiple is 0.94x, so the *sign* of that slice is decided by whether the true 2026
rate is above or below the coded $4.36. Product A's most friction-exposed year (2023, breakeven
4.22x, `FS_house` 0.352) is comfortable but is 3.3x closer to the edge than 2025 (14.1x).
The honest summary is: **the static assumption does not threaten the headline; it does prevent any
statement about a recent slice's sign from being treated as established.**

### Comparability to the existing 1-minute friction numbers

Using the house `FS_house` definition with the house's own **analytic** slip assumption
(1 tick x point value + commission, per contract-side):

| Arm | net | contract-sides | friction $ | gross $ | friction_share |
|---|---:|---:|---:|---:|---:|
| 1m time-matched UNSCALED (seq 390) | −3,163.40 | 140,526 | 161,604.90 | 158,441.50 | **1.0200** |
| 1m time-matched RESCALED (seq 418) | 77,747.90 | 59,824 | 68,797.60 | 146,545.50 | **0.4695** |
| 3m ensemble arm ("3m_incumbent", SMV2AE) | 119,008.90 | 49,964 | 57,458.60 | 176,467.50 | **0.3256** |
| **Product A (this run)** | 177,315.10 | 36,886 | 42,418.90 | 219,734.00 | **0.1930** |
| **BEST_ONE_MNQ (this run, prov.)** | 28,900.70 | 3,122 | 3,590.30 | 32,491.00 | **0.1105** |
| **BEST_ONE_NQ (this run)** | 303,449.00 | 3,950 | 28,361.00 | 331,810.00 | **0.0855** |

The three deliverable objects sit at **0.086-0.193**, i.e. 2-12x lower friction share than the
1-minute arms, driven almost entirely by turnover: BEST_ONE_NQ trades 3,950 contract-sides where the
1m unscaled arm trades 140,526.

**Correction to the framing of this task.** The task states friction share "has never been reported
for the 3-minute incumbent." That is *nearly* right and worth stating precisely: a
`3m_incumbent` friction share of **0.3256 already exists** in
`runs/SMV2AE_1MIN_RESCALE/out/friction_share.csv` — but it is a **different object** (a 13-member
MNQ ensemble arm, net $119,008.90 over 49,964 contract-sides), not any of the three here. This run
is the first friction ledger for **Product A, BEST_ONE_NQ and BEST_ONE_MNQ specifically**, and the
first with **measured** rather than assumed slippage.

---

## 5. Honest reading

The task's premise was that "win rate ~37-38% with payoff ~1.06-1.08" makes friction the
highest-sensitivity cost term. **The conclusion survives; the premise does not describe these three
objects, and I have to flag that.** The 37-38% / 1.06-1.08 figures come from
`research/03_reverse_engineering/SOLARWAVE_MATH.md` §84 and `DC01_DC02_RESULTS.md` §61, where they
describe the raw Type-1 persistence bet at the member/1-minute level — and where 1.06-1.08 is a
**profit factor**, not a payoff ratio. Measured here, on the actual deliverables: Product A wins
25.34% with payoff 3.49 and PF 1.185; BEST_ONE_NQ wins 41.77% with payoff 1.63 and PF 1.169;
BEST_ONE_MNQ wins 46.76% with payoff 1.31 and PF 1.154. So the shape is "thin PF, wide payoff, low
win rate" for A and "thin PF, moderate payoff, sub-coinflip win rate" for the Product B pair.
What the numbers actually show about friction sensitivity is this: **commission is not currently the
binding constraint on any of the three — it is 0.87 to 2.60 ticks against a gross edge of 23.8 to
41.6 ticks per contract round turn, and all three would survive a 5x commission increase with a
positive net.** The genuinely fragile term is not the rate, it is the **gross edge per trade**, which
is what actually collapsed: BEST_ONE_NQ's gross fell from 54.7 ticks/RT in 2022 to 2.76 ticks/RT in
2026, at which point a completely unchanged 2.81 ticks of friction was enough to make the slice
negative. Friction is a *fixed* cost in ticks and the edge is not; the thin-PF structure means the
object is not robust to edge decay, and the friction floor is simply where the failure becomes
visible. The correct reading of a low friction share is therefore **not** "friction is safely
handled" — it is "friction is currently small relative to a gross edge whose stability is the actual
open question," and the 2026 slices (NQ net −$46.60 with FS 1.06; MNQ gross negative before any
friction at all) are the first in-window evidence that the gross edge can reach that floor.

---

## 6. Caveats, flags, and what this does NOT establish

- **BEST_ONE_MNQ is PROVISIONAL throughout** (KNOWN_ERRORS #7: no voluntary exit order is ever
  submitted; 1,077/1,561 exits measured here land on the session's last bar). Its friction ledger is
  arithmetically correct for the trade list it was given, but the trade list is produced by a
  defective object.
- **Product A is compliant on normal sessions** but shares the C2 holiday-early-close defect; two of
  its fills in this ledger are new entries on the final bar of an early-close session.
- **Nothing here is a selection input.** Recency tiers are disclosure only. No parameter was tuned,
  no object ranked, no threshold moved.
- **No live rate was assumed or invented.** The band is a sensitivity analysis around a *coded* rate,
  not a forecast of costs.
- **Sensitivity rows hold behaviour fixed.** A genuinely different commission regime could change
  optimal turnover; that is not modelled and would require re-simulation.
- **2026 slices are 106 sessions.** They are DIRECT evidence about what happened, and weak evidence
  about what will happen. No mechanism claim is made from them.
- **Future profitability is not established by anything in this document.**

## 7. Reproduction

```
python runs/W17_C4_COMPLIANCE/src/v4_friction.py [optional_json_dump_path]
```

Inputs (all committed): `runs/SMV2M_MASTER_BUILD/out/nt8/smm_v2_fills.csv`,
`runs/SMV2M_MASTER_BUILD/out/nt8/smm_v2_bars.csv`, `runs/SMV2M_MASTER_BUILD/out/nt8_dev_battery.csv`,
`runs/PRODUCTB_ONECONTRACT_FINAL/out/nt_trades_nq.csv`,
`runs/PRODUCTB_ONECONTRACT_FINAL/out/nt_trades_mnq.csv`,
`runs/PRODUCTB_ONECONTRACT_FINAL/out/mnq_3m_raw.csv`, `runs/AUDIT03_BARS/nq_3m_2022_2026.csv`,
`runs/SMV2AE_1MIN_RESCALE/out/friction_share.csv`.
The script writes no files unless given a JSON dump path; all results are printed to stdout.
