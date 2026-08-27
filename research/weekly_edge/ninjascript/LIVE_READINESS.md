# LIVE_READINESS — `WeeklyEdgeP1PCT_v1` and `WeeklyEdgeXMConflict_v1`

_Owner directive V4 amendment §3 / §18. Written 2026-08-27, wave P0._
_**ENGINEERING status: LIVE_READY pending Strategy Analyzer reconciliation** (owner-only action).
**Neither strategy is enabled. Neither ever places an order without the owner doing it.**_

---

## 1. `WeeklyEdgeP1PCT_v1.cs` — the incumbent with the W98 box correction

**Derived mechanically from the parity-tested `WeeklyEdgeP1_v3.cs`.** The complete diff is
**14 non-comment lines**: 3 identity (class, `Name`, `Description`), 2 export-identity (`Tag`,
filename prefix), and **the session-box denominator at its two accumulation sites**.

```csharp
// BEFORE (P1_v3)                         // AFTER (P1PCT_v1)
sessPnl += myQty * (Open[0] - myEntryPx)  sessPnl += (Open[0] - myEntryPx)
         * PointValue                              * PointValue
         - CommissionRT * myQty;                   - CommissionRT;
```

Both the point term **and** the commission become per-contract, because the Python is
`spnl += pnl / u` where `pnl = u·(px−epx)·PV − COMM·u`. Dividing only one would be a third
convention. **Both sites must change together** or the box drifts between an intra-session exit and
the session-close flatten.

**Expected behaviour** vs `P1_v3` on 2022-07 → 2026-08: weekly $ at fixed $20,245 DD
**$885 → $1,231**, positive weeks **53.1 → 56.3 %**, max DD **$26,388 → $22,931**, trades
2,002 → 2,131.

**Known risk:** `REGIME_LOCAL`. On 2006–2021 the change **reverses (−31.4 %)**. Keep `P1_v3`
installed for comparison; do not delete it.

**Also fixed in the header:** the stale `PyTs = Time[0] − 1 minute` comment inherited from v1/v2 is
removed. The code never did that shift, and applying one *was* the original phase error.

---

## 2. `WeeklyEdgeXMConflict_v1.cs` — the first cross-market SIGNAL strategy in this repo

### Quantity semantics
Size **1 contract**, `EntriesPerDirection = 1`, at most **one trade per session**. Long and short
both occur (177 / 171 historically). `Qty` is a parameter; the research object is Qty = 1.

### Session semantics
`SessionIterator` on `BarsArray[0]`; `ForcedFlatMin` (21) **before `ActualSessionEnd`**, never a
hardcoded 16:00. An early close therefore flattens correctly — hardcoded end-of-RTH clocks are the
recurring bug in this repo (`SolarWaveOneContractNQ_v5.cs` DEFECT 3).

### Bar timestamping — verified, not assumed
Bars are **BAR-END stamped** in both the Python substrate and NinjaTrader
(`runs/WE_W52_NINJASCRIPT/REPORT.md`). The first RTH bar is the one stamped **09:31**, and its
**open is the 09:30:00 print**. The anchor is that open. **There is no −1 minute shift.**

### The exact 09:45 information set
At the bar stamped 09:45, in `BarsInProgress == 0`, using only indexed accessors:
`Closes[0][0]`, `Closes[1..3][0]`, the stored anchor, and each secondary's own sigma history
computed from **previous** sessions. Nothing from bar 09:46 or later is touched.

### Entry / exit bars
Decision on the **09:45** bar close → market order → fills at the **09:46 open**.
Exit submitted on the **15:45** bar close → fills at the **15:46 open**.

> ⚠️ **Convention difference, measured not assumed.** The research object exited at the **close of
> the 15:45 bar** (a same-bar-close convention) while entering next-bar-open. NinjaTrader with
> `Calculate.OnBarClose` can only do next-bar-open for both. Cost of the NT8-consistent form:
> **−$330 total, −$0.95/trade, 0.17 % of net, |max| $70.** Both are exported side by side in
> `reference/xm_reference_decisions.csv`.

### No secondary-series future leakage
All work happens in `BarsInProgress == 0`. **Unindexed accessors are forbidden in this file** —
`Time[0]`/`Close[0]` are BIP-relative in NinjaScript and reading them inside a non-zero BIP handler
cost an entire silent no-op version once already. Every read is `Times[i][0]` / `Closes[i][0]`, and
NinjaScript delivers the secondary's last bar **at or before** the primary's timestamp.

### No stale forward-fill
`SeriesFresh(i, nqTs)` requires the secondary's latest bar to be **within `MaxStaleMinutes` (3)**
and not in the future. A stale secondary at the anchor *or* at the decision **disqualifies the
whole session** — no trade. Historically **6 sessions of 1,058** are disqualified this way.

### Missing bars · holidays · early closes
`anchorReady` and `decisionReady` are explicit flags, never inferred from the clock. A session with
no 09:31 bar or no 09:45 bar simply never arms. A session that ends before 15:45 flattens at
`ForcedFlatMin`.

### CME rolls and live front-month mapping
The four instruments are **parameters, not literals** — `runs/WE_W44_NT8PARITY/amendment_2.yaml`
records a hardcoded instrument silently running a whole decision stack on a deferred contract
(net −$24,269 → +$8,326). They are additionally **verified at `State.DataLoaded`**, and a mismatch
sets `instrumentMismatch`, which hard-blocks every order.

> **The primary and all three secondaries must use the SAME roll/merge convention** (repo default:
> NT8 `MergeBackAdjusted` continuous). A mixed convention corrupts the composite silently. There is
> deliberately **no auto-roll** — an auto-roll disagreeing with the research substrate would be an
> unrecorded parameter.

### Hard risk limits and how to disable
| | |
|---|---|
| **kill switch** | set `Qty = 0`, or disable the strategy in the Strategies tab |
| **`DisasterStopPoints`** | **default 0 = OFF.** Operational, not alpha. Menu priced in `runs/WE_W105_XMAUDIT/`: **300 pts costs 0.7 %** of gross edge (13 historical triggers); 500 pts costs 4.1 % (2 triggers); 200 pts costs 15.9 % (50 triggers). **No level is selected — the owner sets capital risk.** |
| worst single trade | −$8,872 |
| worst day / worst week | −$8,872 / −$14,577 |
| **worst adverse excursion ever** | **−$10,865 (543 NQ pts)** — a **sample maximum, not a bound** |
| max concurrent exposure | 1 contract, ≤ 1 trade/session, flat by 15:46 |

### Logging fields (per bar, `ExportDir`)
`timestamp, nq_open/high/low/close, es_close, es_move, rty_close, rty_move, ym_close, ym_move,
nq_drive, broad_composite, conflict_flag, desired_direction, decision_ready, entry_request,
exit_request, position, realized_pnl`

---

## 3. The Python reference, and the full N reconciliation

`research/weekly_edge/src/export_xm_reference.py` →
`ninjascript/reference/xm_reference_decisions.csv` (1,058 sessions) and
`xm_reference_bars.csv` (353,637 bars, 2025-08-01 → 2026-07-31, 58.7 MB).

**Three trade counts exist in the record and all three are now explained:**

| N | anchor | sigma implementation | note |
|---|---|---|---|
| **342** | bar stamped **09:30** (= 09:29 price) | vectorised | W101/W102, superseded by W102c |
| **348** | bar stamped **09:31** (canonical) | vectorised pandas `rolling(60, min_periods=20).shift(1)` | W102c/W103/W105 headline |
| **346** | bar stamped **09:31** (canonical) | **sequential loop — what the NinjaScript can do** | **the reference and the C#** |

348 vs 346 differ on **exactly 2 sessions of 348 — 2023-04-10 and 2023-05-03 — i.e. 99.4 %
agreement**, above the 99 % VALIDATED bar. Cause: pandas' rolling window tolerates a NaN inside the
60-session window (`min_periods` counts non-NaN), while the loop **disqualifies** a session whose
secondary bar is missing. The loop is the stricter and more defensible rule; the C# implements it.

One defect found and fixed while building this: gating the sigma history on the study window made
the reference warm up late and cost 4 trades. **The history must be fed by every session the
platform loads, including pre-window months** — which is what the Analyzer will do.

---

## 4. Parity protocol — what must be run, and the verdict bands

Binding, from `runs/WE_W52_NINJASCRIPT/spec.yaml` phase 4. **Compare the DECISION series first,
not P&L.**

| agreement on `desired_direction` | verdict |
|---|---|
| ≥ 99 % **and** trade counts within 2 % | **VALIDATED** |
| 90–99 % | report bar-by-bar; **every mismatch classified** |
| < 90 % | the C# is not the object |

**Analyzer settings:** NQ 1-Minute Last · CME US Index Futures ETH · commission
**"NinjaTrader Brokerage Lifetime"** (plain "NinjaTrader Brokerage" does not exist and returns
`commission_template_unknown`) · **Standard** fill · isolated **Backtest** account.
`To` = **one second before the next 18:00 ET open** — never "end of day D".

**Expect a cold start.** The sigma needs 20 prior sessions per market, so an Analyzer window
shorter than that arms later than the reference. Run a window with ≥ 2 months of lead-in, or
compare only from the 21st session onward.

⚠️ **Standard fill is safe only while there are no intrabar orders.** If `DisasterStopPoints` is
ever set above 0, the fill resolution must be raised to **High (1 tick)** or the stop's fills are
not trustworthy (`research/deep_research/DR-07.md`).

---

## 5. Version and hash

Recorded at commit time in the same commit as this file. Per `src/ninjascript/NAMING.md`:
**rename the class on every functional iteration** (`_v2`, `_v3` …) — NT8 may resolve a stale type,
and deleting a `.cs` does not remove it from the compiled `NinjaTrader.Custom.dll`. **Never rename a
class that has already been parity-certified.** `_Final` is reserved for a file that has passed a
real Analyzer parity check; **neither of these has.**

## 6. What is NOT done

1. **Neither strategy has been compiled.** No NinjaTrader tool was called; compilation and the
   Analyzer run are the owner's interactive actions.
2. **No parity reconciliation has been performed** — the reference exists, the comparison does not.
3. **Neither is enabled**, and nothing here places an order.
4. `XM_CONFLICT`'s standing caveats are unchanged and are not resolved by any engineering:
   ~20 of 348 trades carry 85 % of the money; ρ with P1 is **+0.46 over the trailing six months**
   against +0.08 full-window; and it is **REGIME_LOCAL by data availability** — ES/RTY/YM begin
   2022-01-02 and no deep test can ever be built.
