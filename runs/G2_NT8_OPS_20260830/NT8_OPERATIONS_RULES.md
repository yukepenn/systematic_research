# NT8 OPERATIONS RULES — paper deployment reference

Run: `G2_NT8_OPS_20260830` · compiled 2026-08-30 · read-only investigation (no orders, no
enable/disable, no backtest, no git).

**Our setup under study:** two strategies (`WeeklyEdgeP1PCT_v1`, `WeeklyEdgeXMConflict_v2`) on
`NQ 09-26`, 1-Minute, account `DEMO8383477`, deployed 2026-08-30 with `DaysToLoad=365`.

Every claim below is tagged **VERIFIED(url)** — stated in the official NT8 Help Guide or read by
reflection from *this* install — or **INFERRED(reasoning)**.

> Note on sources: `ninjatrader.com/support/helpGuides/nt8/*` 301-redirects to
> `ninjatrader-live.ninjatrader.com/support/helpGuides/nt8/*`. Both forms cited; the live host is
> what actually served the text. That host returns **HTTP 500 for non-existent pages**, so a 500 is
> evidence a topic filename does not exist, not that the topic is unavailable.

### Live state read from this install at compile time

`ListDeployedStrategies` (read-only) returned, for both deployments:
`state=Realtime`, `is_trading=true`, `position=Flat qty 0`, `active_order_count=0`,
`current_bar=352670`, `bars_required_to_trade=20`, `trade_count=0`,
`net_profit_currency=70585` (P1PCT) / `43705` (XMConflict).

⚠️ **Those `net_profit` figures are historical virtual P&L**, not account money — see §3. With
`trade_count=0` and a flat position, zero real orders have been sent to `DEMO8383477`.

`MarketInfo("NQ 09-26")` → resolves to `NQU6`, `timeZone=Central Standard Time`, session
`17:00 → 16:00` local CT. This is the 23-hour session with a 60-minute daily break (§6).

---

## 1. Contract rollover

### 1a. Strategy on a SPECIFIC contract ("NQ 09-26") — NO AUTO-ROLL

**VERIFIED** — the Help Guide states this in one unambiguous sentence:

> "NinjaScript strategies are not rolled forward and must be manually rolled over."

— [rolling_over_a_futures_contrac.htm](https://ninjatrader.com/support/helpGuides/nt8/rolling_over_a_futures_contrac.htm)

This is the operationally urgent fact. A strategy pinned to `NQ 09-26` keeps trading `NQ 09-26`
through the volume roll and into expiry. Nothing in NT8 moves it.

### 1b. Strategy on the generic master instrument "NQ"

**INFERRED**, but resting on a VERIFIED foundation. NT8 distinguishes `MasterInstrument` (the
product, "NQ") from `Instrument` (a specific expiry). **VERIFIED (this install)**:
`NinjaTrader.Cbi.MasterInstrument` and `NinjaTrader.Cbi.Instrument` are distinct types, and
`MasterInstrument.GetInstrumentByDate(Instrument, DateTime, ...)` exists — i.e. resolution from
product to expiry is a *point-in-time* operation, not a live subscription.

When you type "NQ" into the strategy configuration, NT8 resolves it to the front contract **at that
moment** and stores the concrete expiry. **VERIFIED (this install)**: our deployment registry stores
`"instrument": "NQ 09-26"` even though the deployment was expressed against NQ — the resolved expiry
is what persisted.

⇒ There is **no such thing as a strategy that runs on the perpetual master instrument.** "Generic
NQ" is a lookup convenience at configuration time, not a continuously-rolling series. It does not
auto-roll either. **(a) and (b) have the same answer: you roll it by hand, or it does not roll.**

### 1c. Chart-attached strategy

**INFERRED.** The Rollover feature *does* touch charts — **VERIFIED**: rollover "will update the
expiry of the instruments across all instrument lists and windows using the instruments on all open
workspaces" ([rolling_over_a_futures_contrac.htm](https://ninjatrader.com/support/helpGuides/nt8/rolling_over_a_futures_contrac.htm)).
A chart is such a window. But the same page's NinjaScript note is not carved out for charts.

So the chart's *instrument* rolls while the *strategy* does not roll itself. The inferred consequence
is worse than case (a), not better: changing a chart's instrument forces a data-series reload, which
restarts the attached strategy on the new contract with **completely fresh internal state**, and
`StartBehavior` (§5) then applies to a strategy whose historical replay is now on `NQ 12-26` while
any real position it holds is still in `NQ 09-26`. That position is orphaned — no strategy is
managing it.

**Not applicable to us**: our two strategies run from the Strategies tab, not charts. **VERIFIED**:
"strategies launched from the Strategies tab do not display on charts"
([running_a_ninjascript_strateg2.htm](https://ninjatrader.com/support/helpGuides/nt8/running_a_ninjascript_strateg2.htm)).

### What the Rollover feature actually is

**VERIFIED** ([rolling_over_a_futures_contrac.htm](https://ninjatrader.com/support/helpGuides/nt8/rolling_over_a_futures_contrac.htm),
[instruments.htm](https://ninjatrader.com/support/helpGuides/nt8/instruments.htm)):

- **Location**: Control Center → **Tools → Database Management** (the Instruments window links to the
  same "Rolling Over Futures Contracts" topic).
- **Batch Rollover**: updates every eligible instrument with its "Update" column checked to the
  "New Expiry" contract month.
- **Manual Rollover**: type the next expiry directly into a window's instrument selector
  (documented example: "ES 09-16" → "ES 12-16").
- **Eligibility rule (verbatim)**: "A contract is eligible to be rolled when today's date is greater
  then or equal to the rollover date defined for the instruments next contract month." *(sic —
  "greater then" is the Help Guide's own typo.)*
- **Persistence caveat (verbatim)**: "These changes on workspaces will need to be saved should you
  wish to preserve them."
- **Drawing objects / back-adjustment (verbatim)**: "If a Merge Policy of MergeBackAdjusted is being
  used, this will result in the adjusted bars moving the price away from the original placement of
  the drawing objects."

**What it rolls**: the *expiry label* of instruments referenced by lists and open workspace windows
(charts, Market Analyzer, DOMs), and — via Merge Policy + rollover Offset — how historical series
are stitched.
**What it does NOT roll**: NinjaScript strategies (VERIFIED, explicit) and **open positions**
(**INFERRED**: rollover is a data/UI/database operation; the page never mentions positions, and no
order-submitting behaviour is described anywhere in it. A position in `NQ 09-26` is a real holding in
a real contract — no database edit can transform it into `NQ 12-26`. Rolling a position requires
trading out of the old contract and into the new one).

### Documented best practice at roll

The Help Guide gives no single "systematic trader checklist". **INFERRED** from the composition of
VERIFIED facts — strategies don't roll; manual cancels break strategies; the Close button disables a
strategy (§6) — the safe order of operations is:

1. **Disable** the strategy from the Strategies tab (do not touch its orders by hand).
2. **Flatten** the residual `NQ 09-26` position deliberately, as a separate act.
3. **Roll** the instrument (Tools → Database Management → Rollover), save workspaces.
4. **Re-add** the strategy on `NQ 12-26` and let it re-run its `DaysToLoad` warm-up from scratch.
5. Confirm `state=Realtime` and `Sync` is clean before walking away.

Do this **at or before the rollover date, while both contracts are liquid** — not on expiry day.

---

## 2. Roll date rule for CME equity index futures (NQ)

**VERIFIED** ([editing_instruments.htm](https://ninjatrader.com/support/helpGuides/nt8/editing_instruments.htm)):
NT8's roll date is **neither a volume trigger nor a computed days-before-expiry formula.** It is a
**stored date per contract month**, held in the instrument's rollover collection:

- Each rollover row holds a **Contract Month**, an **Offset**, and a **Rollover date**.
- Verbatim: *"The rollover date is the date to roll into the selected contract month and NOT out of."*
- Verbatim: *"The Offset field is used to connect the last value of a contract month with the next
  one"* (this is the back-adjustment constant, not a date rule). Leave Offset blank for automatic
  calculation.
- Verbatim: *"This information is automatically downloaded from the NinjaTrader server whenever you
  are connected to your live data feed."*
- Users may add/remove rows, edit Offsets, and copy a rollover definition from another instrument.

**Where configured**: Control Center → Tools → Instruments → select **NQ** → Edit → rollover section.

**VERIFIED (this install, by reflection)** — the API backing all of the above is present:

| Symbol | Signature |
|---|---|
| `MasterInstrument.RolloverCollection` | `RolloverCollection` (read/write) |
| `MasterInstrument.GetNextRolloverDate` | `public DateTime GetNextRolloverDate(DateTime date)` |
| `MasterInstrument.UpdateRolloverCollection` | `public void UpdateRolloverCollection(IProgress, DateTime)` |
| `MasterInstrument.GetNextExpiry` | `public DateTime GetNextExpiry(DateTime afterDate)` |
| `Instrument.GetRolloverOffset` | `public double GetRolloverOffset(Instrument toInstrument)` |
| `Bars.IsRolloverAdjusted` | `bool` (read-only) |
| `GetBarsParameter.CalculateRollovers` | `bool` (read/write) |
| `MarketAnalyzerColumns.DaysUntilRollover` | Market Analyzer column class |

`GetNextRolloverDate` taking a date and returning a date — rather than consulting any volume series —
is direct structural confirmation that the roll date is a **lookup, not a market-driven trigger**.

### Concrete expected date for NQ 09-26 → 12-26

⚠️ **INFERRED — DO NOT TREAT AS FACT. READ IT FROM THE INSTALL BEFORE ACTING.**

September 2026 expiry is Friday **2026-09-18** (third Friday). The CME equity-index convention is to
roll **8 calendar days before expiry**, i.e. the **Thursday preceding expiry week's Friday** →
**Thursday 2026-09-10**. Volume typically migrates to `NQ 12-26` across 09-10 → 09-11.

This is an industry convention, **not** something the NT8 Help Guide states, and NT8's actual stored
date is server-supplied and locally editable — so it can differ. **Authoritative reads available to
us, in preference order:**

1. Tools → Instruments → **NQ** → Edit → rollover rows: read the date for contract month **12-26**.
2. Add the **Days Until Rollover** column to a Market Analyzer row for NQ.
3. `MasterInstrument.GetNextRolloverDate(DateTime.Now)` from a scratch NinjaScript.

Treat **2026-09-10** as the planning assumption and the *earliest* date to have completed the roll;
verify against (1) before the first week of September.

---

## 3. Warm-up / history for a running strategy

**VERIFIED** ([daystoload.htm](https://ninjatrader.com/support/helpGuides/nt8/daystoload.htm)) —
`StrategyBase.DaysToLoad`:

- Controls "the number of trading days which will be configured when loading the strategy from the
  Strategies Grid."
- **Trading days, not calendar days** — and "a trading day is defined by a Trading Hour template."
- Default **5**.
- **Does NOT affect** strategies on a Chart, and **does NOT affect** the Strategy Analyzer.

**VERIFIED** ([barsrequiredtotrade.htm](https://ninjatrader.com/support/helpGuides/nt8/barsrequiredtotrade.htm)) —
`BarsRequiredToTrade`:

- "the number of historical bars required before the strategy starts processing order methods called
  in the OnBarUpdate() method." Default **20**.
- Multi-series: the restriction applies **only to the primary Bars object** — check the `CurrentBars`
  array so secondary series are also ready.
- Settable only from `OnStateChange()` during `State.SetDefaults` or `State.Configure`.

**How the two interact**: `DaysToLoad` decides *how much history is fetched and replayed*;
`BarsRequiredToTrade` decides *how far into that replay order methods are permitted*. They are
independent knobs — `BarsRequiredToTrade=20` does **not** shorten the 365-day load, and a large
`DaysToLoad` does not by itself delay trading.

**Do historical bars run through OnBarUpdate — do rolling windows fill before realtime?**
**YES. VERIFIED** ([strategy_position_vs_account_p.htm](https://ninjatrader.com/support/helpGuides/nt8/strategy_position_vs_account_p.htm)):
the strategy "runs the strategy against all loaded historical data to determine the current position
state", and "This position state then becomes the Strategy Position for your strategy." A strategy
starting mid-session processes prior market data first. Internal rolling windows, indicator buffers
and accumulators therefore **do** fill during the historical phase, before `State.Realtime`.

**Do historical bars generate real account orders? NO — they are virtual. VERIFIED** (same page):
the Strategy Position is "a virtual position that is created by the entry and exit executions
generated by a strategy and is independent from any other running strategy's position or an Account
Position", and the historical phase establishes what the strategy "would hypothetically hold"
**"without any real account transactions occurring."** Real orders begin only once live data starts.

⚠️ **This explains our reading.** `net_profit_currency` of 70585 / 43705 alongside `trade_count=0`
and `Flat` is exactly the documented split: those dollars are the **virtual** result of replaying 365
days of history, and **DEMO8383477 has transacted nothing.** Never quote those numbers as paper-account
performance — they are a backtest artifact of the warm-up, and they are `DISCOVERY_CONSUMED`-grade at
best since the window overlaps burned and virgin data.

**Bar count sanity check — INFERRED, worth confirming.** `current_bar=352670` on a 1-minute series.
365 trading days × ~1380 session-minutes ≈ 503,700 *possible* minutes, so we observe ~70 % of that.
The benign explanation is that NT8 emits a 1-minute bar only for minutes that actually traded, and
NQ's overnight minutes are frequently empty — ~966 bars/day is plausible for a 23-hour instrument.
The adverse explanation is that `NQ 09-26` simply lacks 365 trading days of its own history and the
load was silently truncated. **These are distinguishable and must be distinguished** (§"WHAT WE MUST
DO"), because any strategy whose internal window is measured in *bars* rather than *time* would be
warmed to a different depth than intended.

---

## 4. Strategy Analyzer vs live

**VERIFIED** ([daystoload.htm](https://ninjatrader.com/support/helpGuides/nt8/daystoload.htm)):
`DaysToLoad` **does not affect strategies run in the Strategy Analyzer.** It is a Strategies-Grid
property only.

**VERIFIED** ([backtest_a_strategy.htm](https://ninjatrader.com/support/helpGuides/nt8/backtest_a_strategy.htm)):
the Analyzer uses its own **Time frame** section — **Start date** ("Sets the start date for the test
period") and **End date** ("Sets the end date for the test period"). `DaysToLoad` appears nowhere in
the backtest properties.

**Is there a "warm-up bars" setting? NO — and this is the trap.** The Analyzer exposes:

- **"Bars required to trade"** — "Sets the minimum number of bars required before orders will be
  allowed to be submitted." This gates *order submission*, and it is a **bar count**, not a date.
- **"Maximum bars look back"** — "Max number of bars used for calculating an indicator's value", with
  `TwoHundredFiftySix` the most memory-efficient option.

⇒ **If a strategy needs N months of internal state, the user MUST set the Start date earlier by at
least N months and disregard the early portion.** (**INFERRED**, but tightly: no warm-up-period
setting exists, `Bars required to trade` only withholds orders rather than excluding the period from
the reported statistics, and the Analyzer's bar supply is bounded by Start date alone.)

⚠️ **`Maximum bars look back = TwoHundredFiftySix` will silently truncate any rolling window longer
than 256 bars.** For a 1-minute series that is ~4 hours. Any multi-week internal window requires
`Infinite`. This is a correctness issue, not a memory preference.

⚠️ **Analyzer ≠ live, structurally. VERIFIED**
([discrepancies_real-time_vs_bac.htm](https://ninjatrader.com/support/helpGuides/nt8/discrepancies_real-time_vs_bac.htm)):
"During backtest, strategies can ONLY be processed at the close of each bar", whereas realtime runs
tick-by-tick — so a condition true intrabar but false at bar close produces different behaviour live
than in the Analyzer. Fills in backtest "are determined based on 4 data points, OHLC of a bar since
that is the only information that is known during a backtest"; realtime uses actual bid/ask and
available volume. This compounds the repo's existing rule that a research headline and an NT8 net are
different quantities.

---

## 5. Restart persistence

### Start behavior — all five values

**VERIFIED** ([startbehavior.htm](https://ninjatrader.com/support/helpGuides/nt8/startbehavior.htm),
[syncing_account_positions.htm](https://ninjatrader.com/support/helpGuides/nt8/syncing_account_positions.htm)).
Default = **`StartBehavior.WaitUntilFlat`**. Set in `OnStateChange()` under `State.SetDefaults`.

| Value | Documented behaviour |
|---|---|
| **WaitUntilFlat** *(default)* | Assumes the account is flat. Cancels previous orders, then operates **virtually** until the strategy position reaches flat, at which point it syncs. Least disruptive. |
| **WaitUntilFlatSynchronizeAccount** | For beginning "off a flat state with minimal user interaction". If the account is not flat, **submits reconciliatory market orders to flatten it** before live trading. |
| **ImmediatelySubmit** | Only when "you are sure your Account Position is the way you want it to be". Unmatched previous orders cancelled, matching orders mapped, remaining strategy orders go live immediately. |
| **ImmediatelySubmitSynchronizeAccount** | Trade immediately "while not worrying about your Account Position prior to start"; after order matching, **reconciliatory market orders** sync positions. |
| **AdoptAccountPosition** | "disregard the historical virtual Strategy Position and to start in the same position as the real-world Account Position." **Only one such strategy per account/instrument is permitted.** Requires `IsAdoptAccountPositionAware` = true (VERIFIED: this property exists on `StrategyBase` in this install) and a strategy written to handle it. |

Plus **Synchronize All Strategies**: aggregates all enabled strategies' positions (excluding
`WaitUntilFlat` ones) and submits market orders to align the account with the combined position.

**VERIFIED warnings** (same page):
- The settings "only help synchronize positions once at startup" — "These options will not guarantee
  your Account Position remains in sync afterward."
- Synchronize functions "can close or place live trades to your account."
- Reconciliatory market orders operate **outside** strategy control methods like `OnOrderUpdate()`.
- Historical order references transitioning to realtime must be updated via `GetRealtimeOrder()`.

### Which is safest for a strategy that may hold a position across a restart?

**INFERRED**, and the honest answer is *none of them is safe for our configuration.*

`AdoptAccountPosition` is the value designed for "carry the position across the restart" — but
**VERIFIED**: only **one** strategy per account/instrument may use it. We run **two** strategies on
`NQ 09-26` in `DEMO8383477`. The account holds one netted NQ position that is the *sum* of two
strategies' intents; there is no way to attribute it, and at most one strategy could legally adopt
it. **`AdoptAccountPosition` is therefore unavailable to us.**

Any `...SynchronizeAccount` variant **sends live market orders at startup, outside `OnOrderUpdate()`**
— unacceptable as an automatic behaviour on a deployment we are still validating.

⇒ **Keep the default `WaitUntilFlat`, and make "flat before restart" an operational precondition
rather than relying on the setting.** `WaitUntilFlat` sends no surprise orders; its cost is that a
real position left open across a restart goes **unmanaged** (the strategy trades virtually until its
own virtual position returns to flat). That cost is only acceptable if we guarantee flatness first.

### What happens to strategy internal state on restart

**INFERRED** (no Help Guide page states it directly; follows from §3 + the NinjaScript lifecycle).
The strategy object is **reconstructed** — it re-enters `State.SetDefaults` → `Configure` →
`DataLoaded` → `Historical` → `Realtime`. All instance fields reset to their initial values and are
rebuilt **solely** by replaying `DaysToLoad` trading days of history. **Nothing persists across a
restart except what the strategy itself writes to disk.** Consequences: the warm-up is re-paid on
every restart; and because the replay window slides forward, a restart on a later date warms up over
a *different* 365 days than the original deployment did.

### Do Control Center strategies survive an NT8 restart?

**INFERRED — NOT ESTABLISHED. THIS MUST BE TESTED, NOT ASSUMED.**

The Help Guide pages for the Strategies tab and for running a strategy from it **do not address
restart persistence at all** (verified by direct reading of
[strategies_tab.htm](https://ninjatrader.com/support/helpGuides/nt8/strategies_tab.htm) and
[running_a_ninjascript_strateg2.htm](https://ninjatrader.com/support/helpGuides/nt8/running_a_ninjascript_strateg2.htm)).

The one hard clue is **VERIFIED**: the Strategies grid has a **Workspace** column, and the rollover
topic warns that workspace changes "will need to be saved should you wish to preserve them." That
ties grid entries to workspace persistence and suggests entries reappear when the workspace is
restored — but it says nothing about whether the **Enabled** checkbox is restored *checked*, which is
the only part that matters. The two failure modes are opposite and both bad: silently resuming live
trading unattended, or silently not resuming while we believe it is running. **Determine this by
observation on the paper account before any unattended overnight run.**

---

## 6. Other operationally important items for a 23-hour NQ strategy

**Connection loss — VERIFIED**
([connectionlosshandling.htm](https://ninjatrader.com/support/helpGuides/nt8/connectionlosshandling.htm),
[options_strategies.htm](https://ninjatrader.com/support/helpGuides/nt8/options_strategies.htm)).
`ConnectionLossHandling` default = **`Recalculate`**. Confirmed present on `StrategyBase` in this
install, along with `DisconnectDelaySeconds` and `RestartsWithinMinutes`.

| Value | Documented behaviour |
|---|---|
| `KeepRunning` | "Keeps the strategy running. When the connection is reestablished the strategy will resume as if no disconnect occurred." |
| `Recalculate` *(default)* | Attempts to recalculate position on reconnect — only if the strategy stopped due to a data-feed disconnect exceeding `DisconnectDelaySeconds`, an order-feed disconnect while placing orders, or both feeds exceeding the threshold. |
| `StopStrategy` | "Automatically stops the strategy when disconnected for more than DisconnectDelaySeconds. No action will be taken when a connection is reestablished." |

Global equivalents live at **Tools → Options → Strategies** (VERIFIED): *On connection loss –
Handling* (Keep Running / Recalculate / Stop Strategy), *Disconnect delay seconds* ("the number of
seconds a disconnection must persist before it is recognized"), *Number of restart attempts*, and
*Restarts within x minutes*.

**Order-cancellation policy — VERIFIED** ([options_strategies.htm](https://ninjatrader.com/support/helpGuides/nt8/options_strategies.htm)):
*Cancel entry orders when a strategy is disabled* and *Cancel exit orders when a strategy is
disabled* are separate toggles. ⚠️ Know their state before disabling anything — leaving **exit**
orders live after disabling a strategy, or cancelling them and stranding a naked position, are both
real outcomes depending on these two checkboxes.

**Manual interference — VERIFIED**
([running_a_ninjascript_strateg2.htm](https://ninjatrader.com/support/helpGuides/nt8/running_a_ninjascript_strateg2.htm),
[running_a_ninjascript_strategy.htm](https://ninjatrader.com/support/helpGuides/nt8/running_a_ninjascript_strategy.htm)):

- "Orders generated are live and not virtual."
- "Cancelling strategy generated orders manually can cause your strategy to stop executing as you
  designed it" — disable the strategy *first*, then cancel.
- "Clicking the 'Close' button to close a position on an account/instrument that has a strategy
  running will disable the strategy." ⚠️ The convenient flatten button is also a strategy kill switch.

**Sync / position mismatch — VERIFIED**
([strategies_tab.htm](https://ninjatrader.com/support/helpGuides/nt8/strategies_tab.htm)): the grid
carries both **Position** ("The Strategy Position (independent of the Account Position)") and
**Acct. Position** ("The Account Position (includes positions not entered by the strategy)"), plus a
**Sync** column comparing the two. Also **Connection** ("blank for disabled strategies") — a
blank Connection cell is a fast disabled-strategy check. Row colour: green = active, **orange = "the
strategy is waiting until it reaches a flat position to be in sync with the account position before
fully starting"**, black = disabled. Orange is the visible signature of `WaitUntilFlat` still
trading virtually.

⚠️ **Two strategies, one instrument, one account.** The account nets them. `Acct. Position` will
routinely disagree with either strategy's `Position`, and the Sync column may flag legitimately. This
is expected, not a fault — but it means **the Sync column cannot be used as a health check for us**,
and no `SynchronizeAccount` start behaviour is safe (§5).

**Daily maintenance window — VERIFIED (this install)**: `MarketInfo("NQ 09-26")` reports
`timeZone = Central Standard Time` with session `17:00 → 16:00` local. So NQ is 23 hours with a
**60-minute daily break, 16:00–17:00 CT = 17:00–18:00 ET**. This matches the repo's standing
convention that sessions run 18:00 → 17:00 ET and that `to` is one second before the *next* 18:00 ET
open. A strategy must expect a daily gap, and `DisconnectDelaySeconds` should not be so short that a
routine maintenance break trips `Recalculate`.

**IncludeTradeHistoryInBacktest — VERIFIED**
([strategies_tab.htm](https://ninjatrader.com/support/helpGuides/nt8/strategies_tab.htm)): "set to
false by default when a strategy is applied directly in the Strategies tab"; may be set true in the
Configure state. If either strategy inspects its own trade history for sizing or state, it sees an
**empty** history in this deployment mode — a silent behavioural difference from the Analyzer.

---

## WHAT WE MUST DO

Specific to: `WeeklyEdgeP1PCT_v1` + `WeeklyEdgeXMConflict_v2`, `NQ 09-26`, 1-Min, `DEMO8383477`,
`DaysToLoad=365`, deployed 2026-08-30.

**A. Rollover (deadline-driven — the urgent one)**

- [ ] **Read the actual stored rollover date** for NQ contract month **12-26**: Tools → Instruments →
      NQ → Edit → rollover rows. Do not act on the inferred 2026-09-10 until confirmed.
- [ ] Put the confirmed date in `research/operational/MONITORING_CALENDAR.md` with a **T-3 business
      day** alarm. Planning assumption until then: **roll on or before Thu 2026-09-10**; expiry is
      Fri 2026-09-18.
- [ ] Accept as settled: **NT8 will not roll these strategies.** No setting changes this. Do not
      wait for automatic behaviour that does not exist.
- [ ] Execute the roll in the fixed order: **disable → verify flat → roll instrument → save
      workspace → re-add on `NQ 12-26` → confirm `state=Realtime` → confirm both strategies present.**
- [ ] Treat the re-add as a **new deployment**: new `runs/` entry, spec committed before results, and
      a fresh 365-day warm-up is re-paid on the new contract.
- [ ] Before rolling, decide and record whether the 09-26 → 12-26 discontinuity invalidates any
      cross-roll internal state. A 365-day window on a **single contract** cannot span the roll —
      confirm what Merge Policy the loaded series actually used.

**B. Warm-up integrity (do this week — it may already be wrong)**

- [ ] Resolve the `current_bar=352670` question. Confirm whether 365 trading days were genuinely
      loaded or the load was truncated by `NQ 09-26`'s own contract history. Compare the strategy's
      earliest processed bar timestamp against 365 trading days before 2026-08-30.
- [ ] Verify **Merge Policy** on NQ (Tools → Instruments → NQ). If not back-adjusted/merged, the
      365-day request cannot have been satisfied from a single quarterly contract.
- [ ] Confirm every rolling window in both strategies is shorter than the history actually loaded —
      and that no window silently exceeds **Maximum bars look back** if it is set to `256`.
- [ ] Re-state the 365-day warm-up window against the data seals. It spans **burned**
      (2026-05-31 → 2026-07-31) and **virgin** (≥ 2026-08-01) data. Warm-up is not tuning, so this is
      not a seal violation — but record it explicitly so no one later mistakes the replay for a test.

**C. P&L hygiene (immediate, one line in the log)**

- [ ] Record that `net_profit_currency` = 70585 / 43705 is **virtual historical warm-up P&L**, tag it
      `LEGACY_DIAGNOSTIC`, and never quote it as paper-trading performance. Real account P&L starts at
      **$0** with `trade_count=0`. The first genuine forward datapoint is the first realtime fill.

**D. Restart and connection posture (before the first unattended overnight)**

- [ ] **Empirically test restart persistence** on `DEMO8383477`: note grid state, restart NT8, observe
      whether both rows return and whether **Enabled** returns checked. Record the answer — the Help
      Guide does not document it.
- [ ] **Keep `StartBehavior = WaitUntilFlat`** (the default) on both. Do **not** adopt
      `AdoptAccountPosition` — illegal with two strategies on one account/instrument — and do **not**
      adopt any `SynchronizeAccount` variant, which would fire live market orders outside
      `OnOrderUpdate()`.
- [ ] Make **"flat before any planned restart"** a written precondition. `WaitUntilFlat` protects us
      from surprise orders, not from an orphaned position.
- [ ] Read and record the current **Tools → Options → Strategies** values: *On connection loss*,
      *Disconnect delay seconds*, *restart attempts / within x minutes*, and both *Cancel entry/exit
      orders when a strategy is disabled* toggles. Ensure the disconnect delay comfortably exceeds
      the routine **16:00–17:00 CT** maintenance break.
- [ ] Confirm each strategy's own `ConnectionLossHandling` (default `Recalculate`) is what we intend,
      given `Recalculate` may re-derive a position on reconnect.

**E. Standing operational cautions**

- [ ] Never use the **Close** button on `NQ 09-26` in this account — it disables the strategy.
- [ ] Never cancel a strategy order by hand without disabling the strategy first.
- [ ] Expect **Sync** to flag: two strategies net into one account position. Do not use Sync as a
      health check; use `state`, `Connection`, and row colour (orange = still waiting for flat).
- [ ] Nothing here authorizes enabling, ordering, or live deployment. Status remains
      **LIVE = NO**; this is a paper account under observation.
