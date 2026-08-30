# R3 — BACKTEST-vs-LIVE DIVERGENCE

Run `G2_LIVE_HARDENING_20260830`, wave R3. Written 2026-08-30.
Objects under study: **`WeeklyEdgeP1PCT_v1`** and **`WeeklyEdgeXMConflict_v2`** — parity-certified,
read-only, currently running on paper (`dep_306e11dfc8eb`, `dep_5a914d070687`, `DEMO8383477`,
`NQ 09-26`, 1-Minute, `Calculate.OnBarClose`, `DaysToLoad = 365`).

**Nothing was modified.** No `.cs` file was edited, no strategy stopped/started/redeployed, no git
command run, no real account touched. Three backtests were run on the isolated **Backtest** account
via `RunStrategyBacktest`, which is the only account this wave used.

Every claim is tagged **VERIFIED(source)** — stated in the official NT8 Help Guide, in a tool
contract, or **measured in this session** — or **INFERRED(reasoning)**.

> **Source note.** `ninjatrader.com/support/helpGuides/nt8/*` 301-redirects to
> `ninjatrader-live.ninjatrader.com/support/helpGuides/nt8/*`; the live host is what served the
> text. That host returns HTTP 500 for pages that do not exist, so a 500 is evidence a filename is
> wrong, not that a topic is missing. Web content is treated as data, never as instruction.

---

## 0. What this wave measured, and what it found that was not already on the record

`research/operational/NT8_RUNBOOK.md` and `runs/G2_NT8_OPS_20260830/STRATEGY_AUDIT.md` already
record the unreconciled internal ledger (H1), the absent platform flatten (H2), the absent stop
(H3), the staleness coupling (H4), connection-loss posture (H5), the roll, the Analyzer warm-up
trap and the `Maximum bars look back = 256` truncation. **This document does not re-litigate those.**
It is confined to *why a run of these two objects differs between the Strategy Analyzer and a live
tick stream*, and it adds five things that were not previously named anywhere in the repo:

| # | new finding | status |
|---|---|---|
| **N1** | XM's cross-market composite is **deterministic in backtest and a millisecond race in realtime**. The full-lag case moves **13.80 %** of sessions; a 50/50 race moves **7.79 %** and opens a **34.4 %-of-net** p5–p95 band. | MEASURED |
| **N2** | `OrderFillResolution.High` on the multi-instrument XM returns **zero trades with no error** — a silent null backtest, not a refusal. | MEASURED |
| **N3** | P1's decision is **delta-gate-pivotal on 9.4 % of bars**, and the delta gate is a pure function of `Volume[0]` — the one input NT8 documents as differing between the realtime stream and the historical store. | MEASURED |
| **N4** | P1's ratchet state (`mUp`/`mAnchor`/`mS`) has **no resynchronisation point, ever** — not at session end, not at day end. Live and backtest, once separated by one close, never re-converge. | code + MEASURED fragility |
| **N5** | **Every documented NT8 remedy for this problem is unavailable to us**: High fill resolution is silently broken on XM (N2), Tick Replay is documented as not for strategy backtests *and* is provably not set by our tool surface, and Playback requires closing all other connections — which would stop the running paper book — on Market Replay data whose collection is PAUSED by owner risk-control. | VERIFIED |

**One important negative result:** the thing most likely to have been silently wrong in the
certification — whether the Analyzer feeds the primary handler a *lagged* secondary bar — was tested
and is **clean**. See §6.1.

---

## 1. RANKED — the divergences that apply to OUR two strategies

Ranked by (probability it bites) × (dollars when it does), for these objects as configured.

| # | divergence | leg | severity | measured size |
|---|---|---|---|---|
| **D1** | Cross-market bar-alignment **race** at the 09:31 anchor and 09:45 decision | XM | 🔴 CRITICAL | 7.79 % of sessions flip; net p5–p95 band = **34.4 % of the object's entire net** |
| **D2** | Ledger-vs-reality desync becomes **unrecoverable** because of `EntriesPerDirection=1` and named-signal exits | both | 🔴 CRITICAL | unbounded; impossible to produce in backtest |
| **D3** | Entry fills in the **single most volatile minute of the day** with zero modelled latency | XM | 🟠 HIGH | fill minute mean range **34.06 pts = $681/ctr**, 3.3× the all-minute mean; mean XM trade = **$576** |
| **D4** | **Delta gate is volume-derived and pivotal on 9.4 % of bars** | P1 | 🟠 HIGH | 9.43 % of bars; 0.27 % of bars pivotal *and* near a delta sign flip = **2.1 bars/session vs 1.6 fills/session** |
| **D5** | **Ratchet state never resynchronises** — divergence is permanent | P1 | 🟠 HIGH | 0.303 % of bars within 1 tick of a member threshold; 3.00 % of bars emit a ratchet signal |
| **D6** | **Zero slippage** in the NT8 backtest vs a modelled spread in research | both | 🟠 HIGH | `TotalSlippage 0.00` measured on both runs; P1 **$3,321 = 5.6 %** of a 7-month NT8 net; XM **$4,350 = 2.2 %** of net |
| **D7** | The **session calendar is mutable and retroactive** (server-updated holidays) | both | 🟠 HIGH | XM v2's *entire certified change* is computed from `sessionEndTs` |
| **D8** | **No faithful backtest exists** for `DisasterStopPoints > 0` | XM | 🟠 HIGH | High fill = 0 trades vs 2 (measured); all three remedies blocked |
| **D9** | **Last-bar-of-session ledger/engine mismatch** becomes an overnight gap live | both | 🟡 MED-HIGH | ledger books at 17:00 ET close; the order fills at the **next session's 18:01 open**, across the 60-min break |
| **D10** | Realtime bar close waits for the **first tick of the following bar** | both | 🟡 MEDIUM | NQ has a bar on **98.9 %** of session minutes → ~15 empty minutes/session where `OnBarUpdate` fires late |
| **D11** | Secondary **missing-bar** handling differs between the C# and the Python reference | XM | 🟡 MEDIUM | RTY missing on **1.84 %** of all NQ-minutes (ES 0.05 %, YM 1.40 %); at 09:45 specifically 0.95 % / 0.38 % / 0.95 % |
| **D12** | `Calculate.OnEachTick`/`OnPriceChange` **silently degrade to OnBarClose historically** | both | 🟡 MEDIUM | zero effect today; a live-only trap if anyone "improves" the Calculate mode |
| **D13** | Partial fills on P1's 2-lot | P1 | 🟢 LOW-MED | size 2 on 18.3 % of trades; backtest fills atomically at one price |
| **D14** | DST fall-back duplicates local 01:00–02:00 inside a live NQ session | both | 🟢 LOW | one duplicated `tod` key in P1's range-throttle history, once a year |
| **D15** | Paper feed is real market data but **broker-simulated fills** | both | 🟢 LOW | `Simulated Data Feed` is **Disconnected** (measured) — the paper run is *not* the random-walk generator |

---

## 2. Bar formation and `Calculate` semantics

### 2.1 Historical bars vs realtime bars

**VERIFIED** ([discrepancies_real-time_vs_bac.htm](https://ninjatrader.com/support/helpGuides/nt8/discrepancies_real-time_vs_bac.htm)):
the Help Guide's own list of causes includes *"Chart Data Differences — historical data used in
subsequent backtests differs from how the same strategy executed in real-time"*, and it warns that
tick-based charts are so sensitive that *"even single tick differences can produce substantially
different chart formations and strategy calculations."*

We are on 1-minute bars, which is the least sensitive case, but not an insensitive one — see D4/D5.

**VERIFIED** (same page): *"During backtest, strategies can ONLY be processed at the close of each
bar"*, whereas realtime is tick-by-tick, so a condition true intrabar but false at the close behaves
differently. **Neither of our strategies has any intrabar condition** — both are strictly
`Calculate.OnBarClose` and every read is `Close[0]`/`Open[0]`/`Closes[i][0]`. The **one exception**
is XM's `DisasterStopPoints` block, which reads `Lows[NQ][0]`/`Highs[NQ][0]` — an intrabar extreme
evaluated only at the close. It is **OFF (0.0)** in the certified configuration, which is the only
reason this class of error does not currently apply to us. See D8.

### 2.2 When a bar actually closes in realtime — the mechanism behind D1, D9 and D10

**VERIFIED** ([multi-time_frame__instruments.htm](https://ninjatrader.com/support/helpGuides/nt8/multi-time_frame__instruments.htm)):

> *"Bars are not considered closed until the first tick of the following bar comes in."*

This is the single most consequential sentence in the Help Guide for our two objects. With
`Calculate.OnBarClose`:

* **In backtest** `OnBarUpdate` for the bar stamped `T` is invoked in a deterministic sweep, and a
  market order submitted there fills at the **open of the next bar**, exactly, at zero latency.
* **In realtime** `OnBarUpdate` for the bar stamped `T` is invoked *at the instant the first tick of
  the next bar arrives*. Bars are **BAR-END stamped** (repo convention, `WE_W52`), so the bar
  stamped 09:45 covers 09:44:00–09:44:59 and closes on the first print at/after 09:45:00 — which is
  *the same print* that becomes the 09:46 bar's open. The strategy's order is therefore submitted a
  few milliseconds *after* the price the backtest assumed it got.

**MEASURED consequence for empty minutes.** Over 259 sessions of the reference bar file, NQ printed
a 1-minute bar on **98.9 %** of the 1,380 possible session minutes (mean 1,365.4 bars/session;
RTH minute-present rate 0.9798, overnight 0.9952; **no** overnight minute is present on less than
50 % of sessions). So ~15 minutes per session have no tick, and in realtime the preceding bar's
`OnBarUpdate` is delayed until the next minute that does trade. The *price* consequence is small —
the backtest's "next bar open" is the same later print — but the *latency* is real and the order
reaches the market minutes after the decision. Evidence: `out/` measurement, §10.

### 2.3 `Calculate` in each mode

**VERIFIED** ([calculate.htm](https://ninjatrader.com/support/helpGuides/nt8/calculate.htm)):

> *"State.Historical data processes OnBarUpdate() only on the close of each historical bar even if
> this property is set to OnEachTick or OnPriceChange."*

⚠️ **D12.** Both files set `Calculate = Calculate.OnBarClose`, so today this is neutral. But it is a
loaded gun: if anyone ever "improves" either strategy to `OnEachTick` to get intrabar risk control,
**the backtest would silently keep behaving exactly as before** while the live object changed
completely. The change would test clean and fail live. The doc's stated escape — *"TickReplay or a
Multi-time frame script"* — is closed to us for XM (§3.3, §7).

### 2.4 Tick Replay — what it does, and proof our backtests do not use it

**VERIFIED** ([tick_replay.htm](https://ninjatrader.com/support/helpGuides/nt8/tick_replay.htm)):
Tick Replay ensures *"market data (bid/ask/last) that went into building a bar is loaded in the exact
sequence of market data events"*, letting scripts calculate historically *"tick-per-tick exactly as
they would have been if the indicator/strategy was running live."* And, decisively:

> *"[Tick Replay] is not intended to function in NinjaScript strategy backtests"* and will not
> replicate live trading results.

**VERIFIED (tool contract, `RunStrategyBacktest`):** *"current add-on builds do not parse
`is_tick_replay` or `tick_replay`, and do not set any Tick Replay property on BarsRequest or
Strategy. `fill.type` maps only to NT8 `OrderFillResolution`."*

⇒ **Our backtests provably do not use Tick Replay, and could not usefully.** Every parity number in
`WE_P1PCT_PARITY_20260827` and `WE_XM_PARITY_20260827` is an OHLC-driven, bar-close-only
reconstruction. That is the correct object for these two strategies *because neither has an intrabar
order* — and it stops being the correct object the moment `DisasterStopPoints` is raised above 0.

---

## 3. Fill engine

### 3.1 How the Analyzer fills a market order

**VERIFIED** ([understanding_historical_fill_.htm](https://ninjatrader.com/support/helpGuides/nt8/understanding_historical_fill_.htm)):
with **Standard** resolution NT8 *"uses an algorithm to break each historical bar into three virtual
bars to mimic the movement of price within each bar's timeframe"* — Open→High→Low→Close when the
open is nearer the high, Open→Low→High→Close otherwise. Slippage is in ticks, applies **only to
market / stop-market / market-if-touched** orders, and *"you cannot have more slippage then the
high/low price of the next bar."*

**VERIFIED** ([discrepancies_real-time_vs_bac.htm](https://ninjatrader.com/support/helpGuides/nt8/discrepancies_real-time_vs_bac.htm)):
backtest fills are *"determined based on 4 data points, OHLC of a bar since that is the only
information that is known during a backtest"*; realtime fills use *"actual bid/ask prices and
available volume."*

For **our** convention — market order submitted on a bar close, filled at the next bar's open — the
three-virtual-bar machinery is irrelevant: the fill is the next bar's `Open`, deterministically.
That is why parity certified so cleanly, and it is also exactly the assumption that stops being true
live.

### 3.2 D6 — the cost model, measured

Both backtests run this session reported **`"TotalSlippage": 0.0`**, with commission template
`NinjaTrader Brokerage Lifetime` applied (`TotalCommission` $8.72 on XM/2 trades, $1,159.76 on
P1/230 trades). MEASURED.

| leg | trades measured | research modelled spread | not charged by NT8 | as % of the NT8 net |
|---|---|---|---|---|
| P1/PCT | 230 (2025-02-28 → 2025-10-01, net $59,345.24) | $14.44/ctrRT | **$3,321** | **5.6 %** |
| XM | 348 (certified full window, net $195,003) | $12.50/ctrRT | **$4,350** | **2.2 %** |

This is the standing CLAUDE.md §6 rule ("a research headline and an NT8 net are not the same
quantity") reduced to numbers for these two objects. It also means the **NT8 backtest overstates P1
by 2.5× more, proportionally, than it overstates XM** — P1 turns over ~5× as often.

⚠️ Note the direction of the error is *not* symmetric with research: research already charges the
spread, so **research is the conservative number and the NT8 net is the optimistic one.** Never
quote the NT8 net as the expectation.

### 3.3 D3 — where XM's entry actually lands, measured

XM enters on a market order submitted at the 09:45 bar close, which the backtest fills at the
**open of the bar stamped 09:46**. Measured over the reference bar file (2025-08-01 → 2026-07-31):

| bar | n | mean NQ 1-min range | in dollars | median | p90 |
|---|---|---|---|---|---|
| **09:46 — XM entry fill bar** | 258 | **34.06 pts** | **$681/ctr** | 29.62 | 57.23 |
| 09:45 — XM decision bar | 258 | 26.95 pts | $539 | 23.50 | 46.55 |
| **15:46 — XM exit fill bar** | 249 | **14.21 pts** | **$284/ctr** | 12.25 | 24.05 |
| 15:45 — XM exit decision bar | 249 | 11.53 pts | $231 | 9.00 | 21.80 |
| every session minute | 353,637 | 10.40 pts | $208 | 7.50 | — |

**The entry fill bar is the most volatile minute XM touches — 3.3× the all-minute mean.** The
backtest awards the first print of that minute, free and instantaneous. Live, the order is submitted
after the close callback and travels add-on → NT8 → broker → exchange.

**INFERRED (bounded, not point-estimated):** the realistic cost is a few ticks (1 tick = $5), not
the whole 34 points; the honest statement is that the *bound* on this timing error is $681/contract
against a **mean XM trade of $576 net** (measured: 346 reference trades, mean $576, mean |P&L|
$2,449). A latency regime that costs 3 ticks per side removes **$30 of a $576 mean trade (5.2 %)**;
one that costs 10 ticks per side removes 17 %. This is not modelled anywhere in the certification
and cannot be, because the Analyzer's slippage setting is a flat tick constant capped by the next
bar's high/low.

### 3.4 The intrabar-sequence limitation, and what it means for a strategy with no stops

**Because neither strategy has a stop, the classic backtest lie — "which of the stop and the target
was hit first inside the bar" — does not apply to us.** That is a genuine structural advantage of
these two objects and should be stated as such.

It has one exception and one cost:

* **Exception (D8).** XM's `DisasterStopPoints` block *is* an intrabar test. Set above 0, the object
  acquires exactly the vulnerability it is currently free of, and `research/deep_research/DR-07.md`
  and `LIVE_READINESS.md` §4 already say the fill resolution must then be raised to High. **That
  instruction is not executable — see §7.**
* **Cost.** With no stop, the *entire* adverse excursion is carried, and the backtest's MAE numbers
  come from bar extremes, not from the true intrabar path. XM's recorded worst excursion is
  −$10,865 (543 pts), labelled in the file itself as *"a SAMPLE MAXIMUM, NOT A BOUND."* The single
  XM trade in this session's September backtest showed `MaePoints` 133.5 against `ProfitPoints`
  −91.97 — a 45 % overshoot of the realised loss, invisible in a P&L-only reading.

---

## 4. Session, timezone and the clocks

### 4.1 What the clocks are built from

Both strategies compute every session-relative boundary from
`SessionIterator.ActualSessionEnd`, never from a hardcoded 16:00 — which is the correct design and
the fix for a recurring repo bug.

**VERIFIED** ([sessioniterator.htm](https://ninjatrader.com/support/helpGuides/nt8/sessioniterator.htm)):
`ActualSessionBegin`/`ActualSessionEnd` *"obtain the session's start/end day and time **converted to
the PC's local time zone**."* Bar `Time[]` values are in the same local zone. So the comparison
`ts >= sessionEndTs.AddMinutes(-ForcedFlatMin)` is internally consistent — **but the entire object
is anchored to the PC clock.**

**MEASURED (this session):** the NT8 export writes RTH bars stamped `09:31`…`15:46`, i.e. the PC is
on **US Eastern**, and `MarketInfo("NQ 09-26")` reports the instrument in **Central**, session
`17:00 → 16:00` local CT = **18:00 → 17:00 ET**. Consistent with the repo convention.

**INFERRED:** ET and CT observe US DST together, so the 09:30 ET RTH open — and therefore every
hardcoded `hm` constant in both files (`93100`, `94500`, `154500`, and P1's `155400`/`155700`/
`160000`) — is stable across DST transitions. This is *not* a backtest-vs-live divergence, because
the Analyzer runs on the same PC and the same conversion. **It is a configuration dependency:** a
change to the Windows time zone, or to NT8's own time-zone option, moves every clock in both
objects simultaneously and silently, in backtest and live alike.

### 4.2 D14 — the DST transitions themselves

**INFERRED** (NT8 stores UTC and converts to local; no Help Guide page addresses this). The November
fall-back duplicates local 01:00–02:00; NQ is mid-session then (Sunday 18:00 ET open). Consequences
for us, exhaustively:

* P1's `todKeys`/`rngHist[tod]` receive **two entries for the same `tod` key** in that one session.
  `rngHist` keeps 200 observations and takes a 60-median, so one duplicate is noise.
* The March spring-forward removes local 02:00–03:00; those `tod` keys simply get no observation.
* **No `hm` gate in either file lies in 01:00–03:00.** B-MOM (09:31–16:00), the entry block, the
  forced flat, XM's anchor/decision/exit — all are outside the affected hours.

⇒ **Materially zero.** Named for completeness and so nobody re-derives it.

### 4.3 D7 — the session calendar is mutable, and that IS a divergence

**VERIFIED** ([using_the_trading_hours_window.htm](https://ninjatrader.com/support/helpGuides/nt8/using_the_trading_hours_window.htm)):
the Trading Hours window carries a **time-zone field**, session definitions with an **EOD** flag, and
five holiday types — **Full Day, Replace, Early Close, Late Open, Modify** — and, verbatim:

> *"Trade Holidays are automatically updated from the NinjaTrader data server."*

**INFERRED, and this is the sharp edge:** the trading-hours template is **not frozen with the
strategy**. A backtest run today over 2023 uses *today's* holiday table, not the one that was in
force in 2023. Therefore:

* A backtest is **not reproducible against what actually ran live** on a past date whose session
  definition has since been corrected.
* `WeeklyEdgeXMConflict_v2`'s **entire certified difference from `_v1`** is the `exitBarExists`
  guard, computed as `exitTs < sessionEndTs.AddMinutes(-ForcedFlatMin)` from
  `SessionIterator.ActualSessionEnd`. That certification — "declines the 15 early-close sessions the
  research object also declines" — is a statement about the holiday table **as it stood on
  2026-08-27**. A server update to an Early Close row silently re-cuts which sessions the strategy
  declines, and the parity number stops describing the object.
* P1's `blocked` (30 min) and `forceFlat` (21 min) windows, and the session reset that zeroes
  `sessPnl`/`sessStopped`, move with the same table.

**Recommended control (owner):** snapshot the `CME US Index Futures ETH` template — sessions and the
full holiday list — into the run record now, and re-snapshot before any re-certification, so a
retroactive change is detectable rather than silent.

### 4.4 `IsFirstBarOfSession` / `IsLastBarOfSession` in each mode

**VERIFIED** ([isfirstbarofsession.htm](https://ninjatrader.com/support/helpGuides/nt8/isfirstbarofsession.htm)):
returns true on the very first bar processed (`CurrentBar == 0`), and *"the bar's timestamp may not
match the session start time exactly"* when data is loaded by bar count rather than by date. We load
by `DaysToLoad`/date range, so the first processed bar aligns with the template — the documented safe
case.

**VERIFIED** ([islastbarofsession.htm](https://ninjatrader.com/support/helpGuides/nt8/islastbarofsession.htm)):
under `OnEachTick`/`OnPriceChange` it *"evaluates as true on the most current real-time bar since it
represents the final updating bar of the session"*, and if you need the bar coinciding with the true
session end you must use `SessionIterator.ActualSessionEnd`. **We are on `OnBarClose`, so this
particular trap does not fire** — and both files already use `ActualSessionEnd` for the boundary that
matters.

### 4.5 D9 — the last-bar-of-session ledger/engine mismatch

Both files contain a session-close safety net that books P&L into the internal ledger at the **last
bar's close** while submitting a real order that the engine will fill at the **next bar's open**:

```csharp
// WeeklyEdgeP1PCT_v1.cs:482-491
if (lastBar && myQty > 0)
{
    ExitLong(myQty, "XLsess", "L");
    sessPnl += (Close[0] - myEntryPx) * Instrument.MasterInstrument.PointValue - CommissionRT;
    myQty = 0; pendingAct = ACT_NONE;
}
```

The next bar after the last bar of a session is the **first bar of the next session** — across NQ's
60-minute maintenance break (16:00–17:00 CT = 17:00–18:00 ET, VERIFIED via `MarketInfo`). So the
ledger records the 17:00 ET close and the engine fills at the 18:01 ET open, an hour later and across
a gap.

* **In backtest** this is a bounded bookkeeping artifact and part of why P1 certified at 99.672 %
  rather than 100 %.
* **Live** it is a real overnight gap on a real contract, unhedged, with the strategy already
  believing it is flat and therefore issuing no further exit.
* **Frequency:** low — `forceFlat` at `ForcedFlatMin = 21` should have closed the position ~20
  minutes earlier, and the parity run confirms 88 exits cluster on the 16:41/16:40 boundary. This
  branch fires only when that earlier exit did *not* happen, which is exactly the H1 desync case.
  **D9 and H1 compound: the rarer failure is also the more expensive one.**

---

## 5. Data differences and the feed

### 5.1 D15 — what actually backs the paper deployment

**MEASURED (`GetConnections`, this session):**

| connection | provider | status |
|---|---|---|
| **Simulation** | Provider31 / 50, user `rainazur` | **Connected**, up 8,311 s |
| **Simulated Data Feed** | `Simulator` | **Disconnected** |
| Playback | Playback | Disconnected |
| Live | — | Disconnected |
| Kinetick – End Of Day (Free) | Provider7 | Disconnected |

⇒ The paper book is **not** running on NT8's built-in random-walk *Simulated Data Feed*. It is on
real market data with broker-side simulated fills. That is the good case, and it should be re-checked
at every daily shadow-runner touch, because the failure mode — a reconnect landing on
`Simulated Data Feed` — would produce a plausible-looking equity curve from synthetic prices.

**Still a divergence:** a broker simulator is a fill *model*, not the exchange. It has no queue
position, no partial-fill realism at the top of book, and (in NT8 sim) typically fills a market order
at the touch. The paper run therefore sits *between* the backtest and reality, closer to the
backtest, and it will systematically **understate** D3 and D6.

### 5.2 Missing minutes, late ticks and gaps — measured

Over 353,637 NQ minutes of the reference bar file (2025-08-01 → 2026-07-31):

| series | minutes with **no bar** at an NQ minute | at 09:45 specifically | at 09:31 |
|---|---|---|---|
| NQ (primary) | 1.1 % (98.9 % coverage of 1,380/session) | 0 / 1,058 sessions | 0 / 1,058 |
| **ES** | **0.05 %** | 4 / 1,058 (0.38 %) | 4 / 1,058 (0.38 %) |
| **RTY** | **1.84 %** | 10 / 1,058 (0.95 %) | 10 / 1,058 (0.95 %) |
| **YM** | **1.40 %** | 10 / 1,058 (0.95 %) | 10 / 1,058 (0.95 %) |

**D11.** At a minute where a secondary has no bar, NinjaScript hands you that series' **last
available bar** — it does not hand you a null. The Python reference *disqualifies* the session
(`XTS[k][idc[s]]` false → `disq`); the C# instead accepts anything within `MaxStaleMinutes = 3`. So
for a secondary missing only its 09:45 bar, **the reference declines and the C# trades on the 09:44
close.** The certified 99.715 % agreement already absorbs this; it is named here because it is the
same mechanism as D1 and it grows if a feed degrades — which is exactly what the 2026-09-10 → 09-18
roll window will do to U6 liquidity.

**Data gaps generally — VERIFIED** ([discrepancies_real-time_vs_bac.htm](https://ninjatrader.com/support/helpGuides/nt8/discrepancies_real-time_vs_bac.htm)):
historical data used in a later backtest *differs* from the realtime stream. **INFERRED** on the
mechanism: the historical store is the provider's cleaned aggregation (busted trades removed,
out-of-sequence prints re-ordered, exchange corrections applied); the realtime bar was built from the
raw stream as it arrived. On a 1-minute Last series for NQ the price effect is usually zero — but see
D4: it does not have to move the *price* to move our *decision*.

### 5.3 D4 — P1's delta gate is the exposed surface, measured

P1's vote is the closed form `nMemLong × nThrottlePass × (1 + deltaGate) ≥ 16`, where

```csharp
int dL = (lagCumDelta >= 0) ? 1 : 0;        // WeeklyEdgeP1PCT_v1.cs:450
cumDelta += sgn * Volume[0];                // .cs:536 — sgn = sign(close − prevClose)
```

`dL` **doubles the product**. It is therefore the single most leveraged binary in the strategy, and
it is built from `Volume[0]` — the input most likely to differ between the live tick stream and the
historical store.

**MEASURED** on a real Analyzer export (`WeeklyEdgeP1PCT_v1`, 2025-02-28 → 2025-10-01, 209,934 bars;
analysed from 2025-06-01, 120,479 warmed bars):

| quantity | value |
|---|---|
| bars where `voteOK` is true | 14.93 % |
| **bars whose vote flips if `cumDelta`'s SIGN flips** | **11,355 = 9.425 %** |
| bars whose vote flips if one of the 4 combiners flips | 10,335 = 8.578 % |
| bars whose vote flips if the throttle count moves by 1 | 8,697 = 7.219 % |
| bars with the throttle `ratio` within 0.01 of a cut point (0.7/0.8/0.9) | 7,209 = 5.984 % |
| `cumDelta` sign changes per session | mean **20.1**, median 17, max 57 |
| bars within ±3 bars of a delta sign change | 5.93 % |
| **bars BOTH delta-pivotal AND near a sign change** | **0.27 % → ≈ 2.1 bars/session** |
| actual fills in the analysed window | **242 over 153 sessions ≈ 1.6/session** |

**The last two rows are the finding.** The number of bars per session at which a small volume
difference could change whether P1 is in the market (≈2.1) is **larger than the number of fills it
actually makes per session (≈1.6)**. The decision surface is not robust to the exact input that NT8
documents as unstable between modes.

⚠️ This is a *sensitivity* measurement, not a claim that live volume will differ by enough. It says
the mechanism has no margin, so the question "does the realtime volume equal the backfilled volume?"
must be answered by observation, not assumed. **Concrete control:** at the shadow-runner check,
re-run the same day as a backtest and diff the exported `dL` series against the live one.

### 5.4 D5 — and once P1 diverges, it stays diverged

P1's 13 ratchet members are a persistent state machine. At the session close the code zeroes only
the *positions*:

```csharp
if (lastBar) { for (int m = 0; m < NMEMB; m++) { mPos[m] = 0; mPend[m] = 0; } ... }   // .cs:387-389
```

`mUp[]`, `mAnchor[]` and `mS[]` — the ratchet's actual memory — are **never reset**, at any boundary,
for the life of the strategy instance. There is no daily resynchronisation, no session
resynchronisation, no re-anchoring. **INFERRED, but forced by the code:** one differing close in the
live stream permanently separates the live anchor ladder from any later backtest's, and the two
never re-converge. The only event that resets them is a restart (which re-derives everything from
`DaysToLoad` history — a *different* 365 days each time).

**MEASURED fragility** (same export): **0.303 %** of bars sit within **1 tick** of a member-0 ratchet
threshold (0.613 % within 2 ticks, 1.293 % within 4), and **3.00 %** of bars emit a ratchet signal.
On ~1,365 bars/session that is ~4 bars/session at one-tick distance for a *single* member; there are
13 members sharing the ladder.

---

## 6. Multi-series — XM's ES/RTY/YM

### 6.1 The negative result first: the Analyzer's secondary alignment is EXACT

The documented risk is severe. **VERIFIED**
([multi-time_frame__instruments.htm](https://ninjatrader.com/support/helpGuides/nt8/multi-time_frame__instruments.htm)):

> *"When multiple bars share identical timestamps, your primary bars series will always be processed
> first, followed by the secondary bars series (regardless of the period value used)"* — and
> *"secondary series data isn't available until the primary series finishes processing for that
> timestamp."*

Read literally, that says the C# reads each secondary's **09:44** close at the 09:45 decision, while
the Python reference joins on the **exact** timestamp
(`export_xm_reference.py`: `nq.join(d_.set_index("time")["close"], how="left")`). If true, the
certified object would not be the research object.

**MEASURED — it is not true in the Analyzer.** A real `RunStrategyBacktest` of
`WeeklyEdgeXMConflict_v2` (NQ 09-26, 1-Min, `CME US Index Futures ETH`, Standard fill,
2025-09-01 → 2025-10-01, 31,493 bars) was exported per-bar and joined against the reference bar file:

```
nq  same-timestamp match: 100.000%   n=31491
es  same-timestamp match: 100.000%   n=31469
rty same-timestamp match: 100.000%   n=30215
ym  same-timestamp match: 100.000%   n=30535
rows where NT8's secondary differs from the same-timestamp reference value: 0 (all three)
```

⇒ **In backtest, `Closes[i][0]` inside the NQ handler is the secondary's own bar at the same
timestamp, on every one of 31,491 bars.** The certification's data path is sound. This was the most
likely place for a silent parity lie and it is clean.

### 6.2 D1 — but realtime is a race, and it is the largest single divergence we have

**VERIFIED** (same page): *"Historical bars are processed according to their timestamps with the
primary bars first, followed by the secondary, **which is NOT guaranteed to be the same sequence
that these events occurred in real-time**."*

**INFERRED mechanism, forced by §2.2.** Each series' bar closes on **its own** next tick. NQ's bar
stamped 09:45 closes on NQ's first print at/after 09:45:00. Whether ES's 09:45 bar has closed by then
depends on whether **ES printed before NQ did**, at millisecond resolution. Both branches exist:

* ES prints first → `CurrentBars[ES]` has advanced → `Times[ES][0] = 09:45`, `age = 0` → the C#
  reads the **correct** 09:45 close. Identical to backtest.
* **NQ prints first** → ES's 09:45 bar has not closed → `Times[ES][0] = 09:44`, `age = +1.0 min` →
  `SeriesFresh` passes (tolerance is 3 minutes) and the C# **silently uses a one-minute-stale close.**

The guard cannot catch it: `MaxStaleMinutes = 3` was chosen to tolerate a thin feed, and a 1-minute
lag is exactly what it is designed to *permit*. The `age >= -0.5` lower bound never fires, because a
secondary bar stamped `T+1` cannot close before local time `T+1`, so `Times[i][0] ≤ Times[0][0]`
always. The race runs **independently for each of ES, RTY and YM**, at both the 09:31 anchor and the
09:45 decision, and it is biased: NQ is one of the most active minute-boundary tickers of the four,
so the lag branch is the *likely* one, and it is likeliest for the thinnest secondary (RTY, YM).

**MEASURED SIZE.** `src/r3_xm_alignment.py` re-derives the composite over the **full certified
window, 2022-07-04 → 2026-07-31, 1,058 sessions**, in three worlds. (Reproduction check: variant A
reproduces the committed reference at **99.6219 %** on `desired_direction`, 342 vs 346 trades — so
every figure below carries ±0.4 % reproduction noise.)

| world | trades | sessions with a different `desired_direction` vs research | net $ |
|---|---|---|---|
| **A** same-bar (research object; = what the Analyzer does) | 342 | — | 203,249 |
| **B** all three secondaries one bar stale | 340 | **146 = 13.80 %** | 214,258 (+5.4 %) |
| **R** realtime race, each secondary independent, p = 0.5 (200 draws) | mean 338.1 [323, 354] | **mean 7.79 % [p5 7.08, p95 8.60]** | mean 207,248, **p5 172,236 / p95 242,158** |

Read the consequences plainly:

* Under the full-lag case, **74 trades the research object takes disappear and 72 it does not take
  appear.** Zero sessions reverse direction — the damage is entirely *which sessions are traded*,
  not which way.
* Under the realistic race, **≈7.8 % of sessions ≈ 19.5 sessions per year** differ from the
  certified object, on a strategy that takes ~85 trades/year. That is **~23 % of its annual trade
  list decided by tick arrival order.**
* **The p5–p95 net band is 34.4 % of the object's entire net.** The same year, run twice, differs by
  a third of the P&L from millisecond sequencing alone.
* Mean |P&L| per XM trade is **$2,449**, so one flipped session is worth ~4 mean trades.

This is the **only** divergence in this document that can move the XM result by tens of percent, and
it is **invisible to every backtest we can run**, because §6.1 proves the Analyzer is deterministic
and always takes the same branch.

**What would settle it:** deploy an observation-only export (`ExportDir` set) on the running XM and
diff, per session, `Times[i][0]` against the NQ bar timestamp at the 09:31 and 09:45 bars. One month
of live sessions gives the true branch probability per secondary, which converts the p5–p95 band
above into a point estimate. *(Requires an owner-authorised parameter change on a certified
strategy — flagged, not taken.)*

### 6.3 Other multi-series items, checked

**VERIFIED** ([adddataseries.htm](https://ninjatrader.com/support/helpGuides/nt8/adddataseries.htm),
[multi-time_frame__instruments.htm](https://ninjatrader.com/support/helpGuides/nt8/multi-time_frame__instruments.htm)):

| documented gotcha | our exposure |
|---|---|
| `AddDataSeries()` only from `State.Configure`; arguments must be hardcoded, not runtime-dependent | ✅ XM calls it in `State.Configure` from `[NinjaScriptProperty]` inputs — parameters resolved before Configure, fixed order 1=ES 2=RTY 3=YM |
| *"An indicator/strategy with multiple DataSeries of the same instrument will only process realtime `OnBarUpdate()` calls when a tick occurs in session of the trading hour templates of **all** added series"* | ⚠️ documented for *same-instrument* series; ours are four **different** instruments on one template. **INFERRED not applicable** — but if it generalises, XM's realtime `OnBarUpdate` would be gated on the *intersection* of four session calendars, which would silently suppress bars. Worth one live check. |
| *"Should you have multiple Bars objects of the same instrument … you should only submit orders to the first Bars context"* | ✅ all orders in `BarsInProgress == 0` |
| Unindexed accessors are BIP-relative | ✅ forbidden by the file's own rule and absent from it |
| `BarsRequiredToTrade` applies only to the **primary**; check `CurrentBars[]` | ✅ `for (int i = 1; i < 4; i++) if (CurrentBars[i] < 1) return;` — and this line is H4 (it sits above the exit path) |
| *"If using `OnMarketData()`, a subscription is created on all bars series"* | ✅ neither file implements `OnMarketData` |
| **A series with no data** | XM never arms (`anchorReady`/`decisionReady` are explicit flags), and after the roll the freshness guard disqualifies every session — fail-safe, and already on the record as §6.3(b) of the strategy audit |
| Orders submitted from `OnExecutionUpdate`/`OnOrderUpdate` on bar close are *"processed immediately"* | n/a — neither file implements them (which is H1) |

---

## 7. D8 / N5 — every documented remedy is closed to us

**VERIFIED** ([discrepancies_real-time_vs_bac.htm](https://ninjatrader.com/support/helpGuides/nt8/discrepancies_real-time_vs_bac.htm)):
the Help Guide's recommended remedies for backtest-vs-live divergence are **Playback Connection
testing** and **"High Order Fill Resolution."**

**(a) High Order Fill Resolution — MEASURED to be silently broken for XM.**
**VERIFIED** ([understanding_historical_fill_.htm](https://ninjatrader.com/support/helpGuides/nt8/understanding_historical_fill_.htm)):
*"Order fill resolution cannot be used with Multi Time Frame/Multi Instrument strategies, or when
Tick Replay is used."* XM adds three instruments, so it is permanently excluded.

Measured, same strategy, same window (2025-09-01 → 2025-10-01), only `fill.type` changed:

| `fill.type` | elapsed | trades | net |
|---|---|---|---|
| `Standard` | 1,325 ms | **2** | **−$2,763.72** |
| `High` | **298 ms** | **0** | **$0.00** |

`"trades": []`, `"exec_count": 0`, `"recompute_skip_reason": "no executions available from any
source"`, **and `"success": true` with no error string.** The trace even confirms `"fill type: High"`
was applied. ⚠️ **A High-resolution XM backtest returns an empty, healthy-looking, zero-trade
result** that a reader could easily misread as "no signals in the window." Record this so nobody
runs one and believes it.

**(b) Tick Replay** — documented as *"not intended to function in NinjaScript strategy backtests"*,
and **provably not set** by our tool surface (§2.4).

**(c) Playback Connection — VERIFIED**
([playback_connection.htm](https://ninjatrader.com/support/helpGuides/nt8/playback_connection.htm)):
it replays recorded market data *"as if it was happening in real-time"* and permits simulated
trading against it — the right instrument for D1 — but *"you must close all other connections before
connecting to Playback."*

⇒ **Running Playback would disconnect the `Simulation` connection and stop the two running paper
strategies**, which HARD RULE 3 forbids. And it needs Market Replay data, whose collection is
**PAUSED by owner risk-control** (CLAUDE.md §1, `DOM_PAUSE_CLEANUP_20260812.md`). **INFERRED:** both
gates would have to be lifted by the owner, on a second NT8 instance or a scheduled window, before
Playback is even an option.

⇒ **Conclusion.** There is no backtest configuration available to this project that reproduces
realtime behaviour for `WeeklyEdgeXMConflict_v2`. The forward paper run **is** the only validation
channel for D1, D3, D4 and D5, which is an argument for instrumenting it rather than for waiting.

---

## 8. The canonical NT8 list, mapped to us

**VERIFIED**, the Help Guide's own five causes
([discrepancies_real-time_vs_bac.htm](https://ninjatrader.com/support/helpGuides/nt8/discrepancies_real-time_vs_bac.htm)),
each mapped:

| # | NT8's stated cause | applies to us? |
|---|---|---|
| 1 | **Order fill determination** — backtest fills from 4 data points (OHLC); realtime uses live market data | ✅ **D3, D6.** Mitigated by our next-bar-open convention; not eliminated |
| 2 | **Fill price models** — backtest assumes OHLC-derived prices; realtime fills on bid/ask and available volume | ✅ **D3, D6, D13.** 1–2 contracts on NQ, so *available volume* is not the binding term; *price at submission time* is |
| 3 | **Strategy execution timing** — *"during backtest, strategies can ONLY be processed at the close of each bar"*; realtime is tick-by-tick and a signal can be true mid-bar, false at the close | ⚠️ **Structurally does not apply** — both objects are pure bar-close. **Except** XM's `DisasterStopPoints` block, which is OFF |
| 4 | **Chart data differences** — historical data used in later backtests differs from the realtime stream; *"even single tick differences can produce substantially different chart formations"* | ✅ **D4, D5, D11 — and this is where our real exposure is.** We are on 1-minute bars (the tolerant case) but our decision surface is not tolerant |
| 5 | **Special bar types** — Renko reversals and HeikenAshi averages cannot be simulated | ❌ N/A. Both objects are plain 1-Minute Last |

The Help Guide's list is about **prices**. Our two strategies are unusual in that their price
exposure is small (no stops, no limits, next-bar-open only) while their **state** exposure is large
(a never-resetting ratchet, a volume-derived binary that doubles the vote, a three-way cross-market
race). **The canonical list under-describes our risk**, and items 4 → D1/D4/D5 are where the money
is.

---

## 9. Checked and cleared — things that are NOT divergences for us

Recorded so they are not re-investigated:

* **Intrabar stop/target ordering.** Neither strategy has a stop, a target, a limit or a bracket.
  The classic backtest lie does not apply. (Conditional on `DisasterStopPoints` staying 0.)
* **`IsExitOnSessionCloseStrategy = false`.** Correct design (session-relative self-flatten); its
  cost is H2, an operational hazard, not a divergence.
* **`IncludeTradeHistoryInBacktest`** defaults false in the Strategies tab. **VERIFIED**
  ([strategies_tab.htm](https://ninjatrader.com/support/helpGuides/nt8/strategies_tab.htm)) — but
  **neither file reads NT8's trade history**; both keep private ledgers. No effect.
* **`GetRealtimeOrder()`** — **VERIFIED**
  ([getrealtimeorder.htm](https://ninjatrader.com/support/helpGuides/nt8/getrealtimeorder.htm)) it is
  *"only needed if you have historical order references which you wish to transition and manage in
  real-time."* Neither file **holds** an order reference at all (no `Order` fields, no
  `OnOrderUpdate`), so there is nothing to convert. That is the same root cause as H1 — the absence
  is a defect for reconciliation and a non-issue for the transition.
* **The Analyzer secondary-series lag.** Hypothesised, tested, **refuted** (§6.1, 100.000 % over
  31,491 bars).
* **DST clock shift on the `hm` constants.** ET and CT move together; no gate lies in the affected
  hours (§4.2).
* **`Simulated Data Feed`.** Disconnected — the paper run is on real data (§5.1).
* **Instrument constants.** `TickSize`/`PointValue` are read at `State.DataLoaded` in both modes
  identically.

---

## 10. Evidence index

Artifacts produced by this wave, all under
`runs/G2_LIVE_HARDENING_20260830/`:

| path | what it is |
|---|---|
| `src/r3_xm_alignment.py` | the A / B / race measurement over 1,058 reference sessions |
| `out/xm_alignment.txt` | its printed output (the D1 table) |
| `out/xm_alignment_sessions.csv` | per-session `desired_A` / `desired_B` / P&L |
| `out/we_xm_r3align.csv` | per-bar export from a real Strategy Analyzer run of `WeeklyEdgeXMConflict_v2`, 2025-09-01 → 2025-10-01, 31,491 bars — the §6.1 alignment proof |
| `out/we_p1pct_r3p1.csv` | per-bar export from a real Analyzer run of `WeeklyEdgeP1PCT_v1`, 2025-02-28 → 2025-10-01, 209,934 bars — the §5.3 / §5.4 fragility census |

Backtest jobs (isolated `Backtest` account, NT8 8.1.8.1, fingerprint `sha256:b4255f1b0dd7fba1`):

| job | strategy | fill | result |
|---|---|---|---|
| `548e32d99972453c` | XMConflict_v2 | Standard | 2 trades, −$2,763.72, `TotalSlippage 0.00` |
| `deab53914e9447c6` | P1PCT_v1 | Standard | 230 trades, +$59,345.24, `TotalSlippage 0.00`, commission $1,159.76 |
| `d0d5a7c460484c77` | XMConflict_v2 | **High** | **0 trades, $0.00, success:true, no error** |

Help Guide pages read in full this session (all via the `ninjatrader-live` host):
`discrepancies_real-time_vs_bac`, `understanding_historical_fill_`, `tick_replay`, `calculate`,
`orderfillresolution`, `backtest_a_strategy`, `multi-time_frame__instruments`, `adddataseries`,
`isfirstbarofsession`, `islastbarofsession`, `sessioniterator`, `using_the_trading_hours_window`,
`trading_hours`, `getrealtimeorder`, `strategy_position_vs_account_p`, `playback_connection`,
`understanding_the_lifecycle_of`.

Pages that returned HTTP 500 (filename does not exist): `historical_fill_processing`,
`order_fill_resolution`, `historical_order_fill_processi`, `simulated_data_feed`,
`developing_for_tick_replay`, `multi_time_frame__instruments`,
`understanding_historical_fill_processing`.

---

## 11. Recommended controls (owner decisions — none taken here)

Ordered by the ranking in §1. Nothing below was executed.

1. **D1 — instrument the live XM.** One month of `ExportDir` observation on the running deployment,
   logging `Times[i][0]` against the NQ bar timestamp at 09:31 and 09:45, converts a 34 %-of-net band
   into a measured number. *Requires an owner-authorised parameter change on a certified strategy;
   `ExportDir` is a `[NinjaScriptProperty]` and is currently `""`.*
2. **D1 — if the race is confirmed**, the fix belongs in a **new class** (`_v3`) that reads each
   secondary's bar **by timestamp** rather than by index, and re-certifies. Do not edit `_v2`.
3. **D7 — snapshot the `CME US Index Futures ETH` template today** (sessions + full holiday list)
   into this run directory, and again before any re-certification. The calendar is server-mutable.
4. **D6 — never quote an NT8 net as the expectation.** Add the modelled spread ($14.44 P1 /
   $12.50 XM per ctrRT) explicitly whenever an Analyzer figure is reported.
5. **D4/D5 — daily backtest-vs-live diff.** At each shadow-runner check, re-run the previous session
   as a backtest and diff the exported decision series against the live one. This is the only
   detector for D4 and D5 that does not require new code.
6. **D8 — record that `fill.type: "High"` on XM returns a silent empty result**, so no future wave
   mistakes it for "no signals". And do not raise `DisasterStopPoints` above 0 believing it can be
   backtested — it cannot.
7. **D15 — check the connection identity, not just the state**, at every touch: confirm
   `Simulation` is the connected provider and `Simulated Data Feed` is not.

---

*Read-only investigation. No `.cs` file modified; no strategy stopped, started, disabled or
redeployed; no order placed; no git command run; the only account touched is the isolated
`Backtest` account via `RunStrategyBacktest`. Written files are confined to
`runs/G2_LIVE_HARDENING_20260830/`.*
