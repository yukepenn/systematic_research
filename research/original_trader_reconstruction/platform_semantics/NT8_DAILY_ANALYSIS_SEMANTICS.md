# NT8 Daily Analysis semantics — measured, not assumed

Directive v4.0 phase P1 / section 5. Run `runs/OTR_R11_INVERSE/`, script
`solar_family/src/run_r11a_maemfe_calib.py`, oracle
`runs/OTR_R6_NT8_PARITY/out/layerA_nt8_raw.json` (90 real Strategy Analyzer trades with
NT8's own `MaeCurrency` / `MfeCurrency` / `EtdCurrency` serialised per trade).

Status of everything below: **REPRODUCED** against the NT8 engine unless marked otherwise.

## 1. MAE / MFE — certified 90/90 exact

The winning definition, after testing 8 candidate variants:

> Scan bars **[entry_bar .. last_bar_held_through_close]** using the full bar **High/Low**,
> then fold in the **exit fill price**. Excursion is measured from the **entry fill price**,
> floored at 0, times $20/pt times quantity.
>
> `last_bar_held_through_close` = `exit_bar - 1` for a next-bar-**open** fill (the decision
> was taken at the previous bar's close), and `exit_bar` for an **at-close** fill (session
> close / exit-on-close).

| variant | MAE exact | MFE exact |
|---|---|---|
| bars [entry..exit] full H/L | 60/90 | 90/90 |
| bars (entry..exit] full H/L | 53/90 | 75/90 |
| bars [entry..exit) full H/L | 88/90 | 89/90 |
| bars [entry..exit) + exit price | **90/90** | 89/90 |
| closes only (any range) | 0–3/90 | 1/90 |
| **UNIFIED, fill-type aware (above)** | **90/90** | **90/90** |

Why the fill-type split is real and not a fudge: without Tick Replay NT8 has **no intrabar
path**. It can only have seen the bars whose *close* the position survived, plus the fill
price itself. An open-fill exit was decided at the previous close, so the exit bar's range
was never observed; an at-close fill happens *on* that bar, so its range was. The single
residual miss under the simpler rule was 2023-01-16 — MLK Day, an early 13:00 close, i.e.
exactly a session-close fill.

**Corollary (unplanned but load-bearing):** because MAE/MFE depend on High/Low while net
P&L does not, this simultaneously proves our parquet bar substrate reproduces NT8's
**High and Low** exactly over the test window, not merely its closes.

## 2. ETD carries no independent information

`ETD = MFE - ProfitCurrency` holds **90/90** in NT8's own output, and independently on all
11 of the trader's daily rows (e.g. 2023-01-03: 1015.00 − (−25.01) = 1040.01 ✓). Profit is
NET of commission; MFE is gross. So the ETD column is a derived display and must NOT be
counted as an extra constraint.

## 3. The $5 lattice — 22 new exact constraints

Every gross P&L on NQ qty-1 is an integer number of ticks (0.25 pt × $20 = **$5**).
Therefore `avg_MAE × n` and `avg_MFE × n` resolve to exact integer dollar sums that are
multiples of 5. Verified on **all 11** visible Jan-2023 days (e.g. 635.42 × 12 = 7625.04 →
7625; 1143.44 × 16 = 18295.04 → 18295). This converts two rounded display cells per day
into two exact integers per day.

The same lattice recovers every **cropped** cell exactly: a net aggregate over k trades has
magnitude `5m + comm_rt·k`, and the visible prefix pins a unique lattice point. Example:
`-6163.4?` with 8 losers and $4.18/RT → 5m ∈ [6129.96, 6130.05] → m = 1226 → **−6163.44**.
No cropped value in this run is fabricated; each is the unique lattice solution.

## 4. Commission basis, read off the report rather than assumed

| window | commission column ÷ n | basis |
|---|---|---|
| Jan-2023 rows (OTRIMG-0003) | 50.16/12, 12.54/3, 66.88/16 … | **$4.18 / round turn** |
| Feb-2025 rows (OTRIMG-0026) | 85.20/15, 511.20/90 | **$5.68 / round turn** |

The trader changed commission template between the two backtests. Note neither equals the
installed "NinjaTrader Brokerage Lifetime" $4.36/RT used by campaign #1's frozen truth.

## 5. Day assignment (Period = Daily, Time base = Exit Time) — NOT SEPARABLE

Two candidate rules: calendar date of the exit timestamp, vs the trading-session date.
They differ **only** for a trade exiting in the 18:00–23:59 ET evening block.

Measured: **0 of 90** trades in the certification window exit in that block, and grouping
the whole set under both rules gives byte-identical daily aggregates.

> STATUS **UNKNOWN / NOT SEPARABLE BY THE AVAILABLE LABEL SURFACE.** It is also **MOOT** for
> any strategy that is flat at every session close *and* whose evening exits are rare.
> Recorded rather than resolved: the corpus cannot decide it, so no downstream claim may
> depend on which rule holds. This is an honest negative answer to directive section 45 Q3.

## 6. Backtest window boundary, confirmed by trade evidence

The Jan-2023 report's first row is 1/3/2023, yet its uniquely-recovered path contains a
trade **entering 2023-01-02 21:39**. That is consistent with NT8's session-based boundary
convention (`From = D` loads the session *labelled* D, which opens 18:00 on D−1) and
inconsistent with a naive "00:00 on D" reading. Same family as the already-frozen
`To = D` rule.

## 7. Still UNKNOWN

- **`MTR` column** (values 558.00, 1.14, 317.00, 105.00, 939.00 …). NT8 exposes
  `MaxTimeToRecover` as a TimeSpan; the daily display appears to be minutes, but 1/4/2023's
  value of **1.14** does not fit a minutes reading and is unexplained. Not used as a
  constraint anywhere in R11.
- **`cum_max` vs `max_dd` columns.** `max_dd` behaves like the intra-day trade-sequence
  drawdown (1/9: −854.18 = that day's only loss). `cum_max` is not monotone across days
  (−4030.9, −5971.0, −4609.5, …) so it is not a running all-time drawdown. Semantics
  unresolved; **not used** as a constraint.
- **`% Traded`** appears to be this day's trade count over the window total (2/26–2/27/2025:
  14.29 % / 85.71 % ⇒ 15/105 and 90/105). Consistent but redundant given n.
