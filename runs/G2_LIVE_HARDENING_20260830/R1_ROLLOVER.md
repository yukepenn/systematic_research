# R1 — NT8 Instrument & Rollover Semantics

**Run:** `G2_LIVE_HARDENING_20260830` · **Date:** 2026-08-30 · **Task:** R1 (read-only research)
**Install probed:** NT8 8.1.8.1, `D:\NinjaTrader8\bin`, user data `C:\Users\Yuke Zhang\Documents\NinjaTrader 8`
**Constraint compliance:** no git; no orders; no account touched; running deployments `dep_306e11dfc8eb` /
`dep_5a914d070687` left enabled and untouched; parity-certified `.cs` files not opened for write; all NT8
database access was against a **copy** (`scratchpad\nt.sqlite`) opened `Read Only=True`.

Every claim below is tagged **VERIFIED(source)** or **INFERRED(reasoning)**.

---

## 0. Headline — does a restart re-resolve the front month?

**NO. A disable/re-enable does not re-resolve. An NT8 restart does not re-resolve. The expiry is
resolved once, at configuration-commit time, and is then frozen as a foreign key.**

The roll procedure is therefore **reconfigure**, not **restart**. This directly contradicts the owner's
hypothesis and confirms (and strengthens) the earlier pass.

The decisive evidence is not documentary — it is structural, from this install's own database.

---

## 1. When is the expiry resolved? (Q1)

### 1.1 The published statement

> "NinjaScript strategies are not rolled forward and must be manually rolled over."

**VERIFIED** — NT8 Help Guide, *Rolling Over Futures Contracts*,
<https://ninjatrader.com/support/helpGuides/nt8/rolling_over_a_futures_contrac.htm>
(server 301-redirects to `ninjatrader-live.ninjatrader.com`; same path).

This appears as a note attached to the **Batch Rollover** procedure (Tools > Database Management), whose
other notes say updates "apply across all instrument lists and open workspace windows, requiring manual
saves to preserve changes." So the batch roller explicitly *excludes* strategies while including windows.

That statement establishes that strategies do not roll. It does **not** by itself say *when* resolution
happens, and there is **no** published statement anywhere in the Help Guide about restart-time
re-resolution. **VERIFIED(absence)** — the *Strategies tab* page
(<https://ninjatrader.com/support/helpGuides/nt8/strategies_tab.htm>) describes the Instrument column only
as "The instrument on which the strategy is enabled", says nothing about expiry, and the
*Searching for Instruments* page
(<https://ninjatrader.com/support/helpGuides/nt8/searching_for_instruments.htm>) documents only the
Instruments-window text filter, not selector→contract resolution.

Because the docs are silent, the question was settled empirically against this install.

### 1.2 The structural proof: NT8 stores a resolved foreign key, not a name

NT8's own database is `…\Documents\NinjaTrader 8\db\NinjaTrader.sqlite`. Its schema:

```sql
CREATE TABLE Strategy2Instrument (
    Instrument  integer not null references Instruments on delete cascade,
    Strategy    integer not null references Strategies on delete cascade,
    Nr          integer not null,
    primary key (Strategy, Instrument, Nr)
);

CREATE TABLE Instruments (
    Id               integer not null primary key,
    Exchange         integer,
    Expiry           integer,            -- DateTime ticks
    MasterInstrument integer not null references MasterInstruments on delete cascade,
    ...
);
```

**VERIFIED(sqlite_master on this install).**

A configured strategy is bound to an `Instruments.Id` — a row that carries a **concrete `Expiry`**. It is
*not* bound to a `MasterInstruments.Id` (which is the generic "NQ") and *not* to a string.

Live rows for the two running strategies:

| Strategies.Id | Classname | Nr | Instruments.Id | MasterInstrument | Expiry |
|---|---|---|---|---|---|
| 399550060 | `…Strategies.WeeklyEdgeP1PCT_v1` | 0 | 699839150764821 | 135 (NQ) | **2026-09-01** |
| 399550061 | `…Strategies.WeeklyEdgeXMConflict_v2` | 0 | 699839150764458 | 75 (ES) | **2026-09-01** |
| 399550061 | `…Strategies.WeeklyEdgeXMConflict_v2` | 1 | 699839150764821 | 135 (NQ) | **2026-09-01** |
| 399550061 | `…Strategies.WeeklyEdgeXMConflict_v2` | 2 | 699839150766712 | 188 (YM) | **2026-09-01** |
| 399550061 | `…Strategies.WeeklyEdgeXMConflict_v2` | 3 | 699839150768283 | 699839150753731 (RTY) | **2026-09-01** |

**VERIFIED(query on read-only copy).** Expiry ticks `639238176000000000` → `2026-09-01`.

Two things follow, and both matter operationally:

1. **There is no generic name to re-resolve.** Restart rehydrates `Strategy2Instrument` → the same
   `Instruments.Id` → the same expiry. Re-resolution is not merely disabled; it is **unrepresentable**,
   because the persisted state contains no root-only reference. **VERIFIED(schema + rows).**

2. **Every `AddDataSeries` leg is independently pinned.** `WeeklyEdgeXMConflict_v2` has four rows
   (`Nr` 0–3), one per series, each a resolved contract. A roll must move **all four**, not just the
   primary. **VERIFIED.**

### 1.3 Corroboration: the serialized strategy blob contains no instrument at all

`Strategies.Userdata` for Id 399550060 is the XML property bag (10,880 bytes). It was dumped in full. It
contains `BarsPeriodSerializable`, `DaysToLoad` (365), `From`/`To`
(`2025-08-30T06:48:00` → `2026-08-30T06:48:00`), `BarsRequiredToTrade` (20), `StartBehavior`
(`WaitUntilFlat`), `ConnectionLossHandling` (`Recalculate`), and every user parameter
(`VolPeriod` 460, `StopMultiplier` 179, `HaltDollars` 1300, `Tag` `p1pct`, …).

It contains **no `Instrument` element and no `InstrumentOrInstrumentList` element**.
**VERIFIED(blob dump).**

So the instrument genuinely lives only in the relational FK. `StrategyBase.InstrumentOrInstrumentList`
(a `string`, read/write — **VERIFIED** by reflection) is a UI/Strategy-Analyzer binding surface, not the
persisted truth for an enabled Control Center strategy.

### 1.4 Corroboration: CrossTrade's deployment record agrees

`ListDeployedStrategies` reports both live deployments with `"instrument": "NQ 09-26"` — already resolved,
with `last_engine: "StrategiesGrid.StrategyAdd+StrategyEnable(worker)"`. **VERIFIED(MCP).**

### 1.5 So what *does* resolve, and when?

**Config-commit time.** If an operator types a bare root into an instrument selector, the selector resolves
it to a concrete contract *before* the strategy is committed, and the resolved `Instruments.Id` is what gets
written. Thereafter it is inert. **INFERRED** — from §1.2/§1.3 (nothing generic survives the commit) plus
§1.6 (a bare root is not itself a usable data-series identity).

Workspace windows behave the same way: `workspaces\Default Yuke.xml` stores `<Instrument>NQU6</Instrument>`
— a fully-qualified contract code, not "NQ". **VERIFIED(file).**

### 1.6 A bare root is not a data series

Empirical, this install, via `GetBars`:

| Request | Resolved to | Bars returned |
|---|---|---|
| `NQ` | *(unresolved)* | **0** |
| `NQ 09-26` | `NQU6` | 3 |
| `NQ 12-26` | `NQZ6` | 3 |

**VERIFIED(MCP `GetBars`).** `GetQuote("NQ")` likewise failed with `Market data unavailable for 'NQ'`,
while `GetQuote("NQ 09-26")` normalized to `NQU6`. A bare master name is a *catalogue* entry, not a
tradable/loadable series.

*(Caveat, marked: `MarketInfo(root:"NQ")` **did** return `NQU6`. That is CrossTrade's own root→front-month
convenience resolution, not NT8's strategy-binding path. It should not be read as evidence that NT8
resolves bare roots for strategies.)* **VERIFIED(MCP) + INFERRED(interpretation).**

### 1.7 Operating-procedure consequence

> **The roll is a reconfigure, and it costs an enable cycle.**

- Restarting NT8: **no effect** on the contract. **VERIFIED.**
- Disabling and re-enabling: **no effect** on the contract. **VERIFIED** (nothing generic persists to
  re-resolve; §1.2).
- Tools > Database Management batch rollover: rolls instrument lists and open windows, **skips
  strategies**. **VERIFIED(Help Guide).**
- Changing the instrument requires editing the strategy, and *"Only disabled strategies can be edited."*
  **VERIFIED(Help Guide, strategies_tab.htm).** So the roll necessarily = disable → edit instrument (×4
  series for XMConflict) → re-enable. There is no in-place, no-downtime path.

---

## 2. What determines "front month"? (Q2)

**Answer: a stored, per-contract-month Rollover *date*. Not volume. Not open interest. Not computed live.**

### 2.1 Definition and eligibility rule

> "A contract is eligible to be rolled when today's date is greater then or equal to the rollover date
> defined for the instruments next contract month." *(sic — "then")*

> Rollover date is "the date to roll **into** the selected contract month and **NOT** out of."

**VERIFIED** — Help Guide *Rolling Over Futures Contracts* and *Editing Instruments*
(<https://ninjatrader.com/support/helpGuides/nt8/editing_instruments.htm>).

The date is **downloaded from NinjaTrader's server** ("downloads automatically from NinjaTrader's server
when connected to live data feeds or simulated connections") and is user-editable. **VERIFIED.**
`Rollover.WasEdited` (bool) exists precisely to mark operator overrides. **VERIFIED(reflection).**

Volume/OI presumably inform NinjaTrader's *server-side* choice of these dates, but NT8 the client does **not**
consult volume or OI at runtime. **INFERRED** — nothing in the client surface reads volume for this purpose;
the eligibility rule quoted above is purely a date comparison.

### 2.2 Where it is edited

**Tools > Instruments > (select instrument) > Edit → "Contract Months"** grid, which shows
"the contract months with associated rollover dates"; months can be added, removed, or copied between
instruments. Batch view: **Tools > Database Management > Rollover futures instruments** grid (columns
include *Update* and *New Expiry*). **VERIFIED(Help Guide).**

### 2.3 Reading it programmatically — yes, fully

Reflection against this install (`NinjaTrader.Core`, 8.1.8.1) — **VERIFIED**:

```csharp
// NinjaTrader.Cbi.MasterInstrument
public RolloverCollection RolloverCollection { get; set; }
public DateTime GetNextRolloverDate(DateTime date);
public DateTime GetNextExpiry(DateTime afterDate);
public void     UpdateRolloverCollection(IProgress progress, DateTime earliestRolloverToUpdate);
public static Instrument GetInstrumentByDate(Instrument instrument, DateTime date,
                                             bool getActualExiry,          // sic — NT8's typo
                                             bool suppressCalculateRollOvers,
                                             IProgress progress);
public static Collection<MasterInstrument> All { get; }   // static

// NinjaTrader.Cbi.Rollover  (element type)
public DateTime ContractMonth { get; set; }
public DateTime Date          { get; set; }   // the rollover date
public double   Offset        { get; set; }
public bool     IsRiskManagementOnly { get; set; }
public bool     WasEdited     { get; set; }

// NinjaTrader.Cbi.RolloverCollection : Collection<Rollover>
public double GetOffsetSum(DateTime expiry, DateTime atDate);

// NinjaTrader.Cbi.Instrument
public DateTime Expiry { get; set; }
public double   GetRolloverOffset(Instrument toInstrument);
public static Instrument GetInstrument(string instrumentName, bool create = false);
public static Instrument GetInstrumentFuzzy(string instrumentName);
```

`MasterInstrument.GetNextRolloverDate(DateTime)` is the single call that answers "when do I roll?" and
`GetInstrumentByDate(...)` is the single call that answers "which contract is active on date D?".
Both are **public and static-reachable from NinjaScript** (`NinjaTrader.Cbi` is in the default using set).

### 2.4 The actual stored table for our four instruments

`MasterInstruments.UserData` is a binary snapshot blob holding the `RolloverCollection`. Decoded (record =
`ContractMonth` ticks, `Date` ticks, `Offset` double):

| Contract month | NQ (id 135) | ES (id 75) | RTY (id …3731) | YM (id 188) |
|---|---|---|---|---|
| 2026-03 | 2025-12-15 (off 256.50) | 2025-12-15 (59.75) | 2025-12-15 (20.30) | 2025-12-15 (391.00) |
| 2026-06 | 2026-03-16 (off 208.75) | 2026-03-16 (49.75) | 2026-03-16 (15.70) | 2026-03-16 (290.00) |
| 2026-09 | 2026-06-12 (off 282.25) | 2026-06-12 (61.25) | 2026-06-12 (20.40) | 2026-06-12 (378.00) |
| **2026-12** | **2026-09-16** (NaN) | **2026-09-14** (NaN) | **2026-09-15** (NaN) | **2026-09-18** (NaN) |
| 2027-03 | 2026-12-18 (NaN) | 2026-12-14 (NaN) | 2026-12-08 (NaN) | 2026-12-18 (NaN) |
| 2027-06 | 2027-03-09 (NaN) | 2027-03-15 (NaN) | 2027-03-17 (NaN) | 2027-03-19 (NaN) |

**VERIFIED(blob decode from read-only DB copy).**

**Three operational consequences, all sharp:**

1. **The next roll is 2026-09-16 for NQ — 17 calendar days from today.** Both live paper strategies are
   pinned to `NQ 09-26`.
2. **The four legs of `WeeklyEdgeXMConflict_v2` roll on four different dates**: ES 09-14, RTY 09-15,
   NQ 09-16, YM 09-18. A single "roll day" for that strategy does not exist. Rolling all four on one date
   means at least one leg is deliberately off-front for up to 4 days. This is a **decision the owner must
   make**, not a detail.
3. `Offset` is `NaN` for all future rolls — it is populated at/after the roll (server-supplied, else
   computed locally from "closing prices one day before the rollover date"). **VERIFIED(Help Guide +
   blob).** Anything that consumes offsets must tolerate `NaN` prospectively.

---

## 3. MergePolicy (Q3)

### 3.1 The enum — and what "3" actually is

Reflected from `D:\NinjaTrader8\bin\NinjaTrader.Core.dll`, `NinjaTrader.Cbi.MergePolicy`
(underlying type `int`) — **VERIFIED**:

| Value | Name |
|---|---|
| 0 | `DoNotMerge` |
| 1 | `MergeBackAdjusted` |
| 2 | `MergeNonBackAdjusted` |
| **3** | **`UseGlobalSettings`** |
| 4 | `UseDefault` |

> ⚠️ **Correction to the framing of the question.** `MergePolicy = 3` on NQ/ES/RTY/YM does **not** mean a
> merge mode. It means **"defer to the global setting."** It is the factory default and carries no
> instrument-specific intent.

`MasterInstruments.MergePolicy = 3` confirmed in the DB for ES (id 75), NQ (135), RTY
(699839150753731), YM (188). **VERIFIED(query).**

### 3.2 Resolving the deferral

`…\Documents\NinjaTrader 8\Config.xml`:

```xml
<GlobalMergePolicy>MergeBackAdjusted</GlobalMergePolicy>
```

**VERIFIED(file, line 116).** Corresponds to `MarketDataOptions.GlobalMergePolicy` (**VERIFIED** by
reflection), set at **Tools > Options > Market Data**.

> **Therefore the effective policy for NQ/ES/RTY/YM on this install is `MergeBackAdjusted` (1).**
> "3" resolves to "1". Any note in repo docs recording "MergePolicy=3" as if it were the mode is
> ambiguous at best and should be restated as *"UseGlobalSettings → MergeBackAdjusted"*.

### 3.3 What it does

Help Guide: Merge Policy is "The merge settings applied to historical data." Rollover dates are what
"NinjaTrader uses ... to automatically merge historical data." The `Offset` is "used to connect the last
value of a contract month with the next one"; NT8 downloads it from the data server, and when unavailable
"calculates them locally by comparing closing prices one day before the rollover date between expiring and
new contracts." **VERIFIED(editing_instruments.htm).**

The clearest published statement of the *price* effect is in the rollover page's drawing-objects note:

> "If a Merge Policy of MergeBackAdjusted is being used, this will result in the adjusted bars moving the
> price away from the original placement of the drawing objects." — whereas `MergeNonBackAdjusted`
> "preserves previous contract prices."

**VERIFIED.** So: `MergeBackAdjusted` splices prior contracts in and **shifts the older bars** by the
cumulative offset so the seam is continuous; `MergeNonBackAdjusted` splices them in **raw**, leaving a
price gap at each seam; `DoNotMerge` splices nothing.

- **(a) Historical bars a strategy loads** — a strategy requesting *N* days of `NQ 09-26` gets, for the
  portion of that window preceding `NQ 09-26`'s own rollover date (2026-06-12), data drawn from the
  then-front contracts, back-adjusted by `RolloverCollection.GetOffsetSum(...)`. Both live strategies run
  `DaysToLoad = 365` (**VERIFIED**, blob), i.e. a window starting 2025-08-30 — which spans **three** prior
  seams (2025-12-15, 2026-03-16, 2026-06-12) and a cumulative NQ offset of 256.50 + 208.75 + 282.25 =
  **747.50 points**. **INFERRED** — see §3.5, this was *not* directly confirmed and is the single most
  important open test.
- **(b) Backtests spanning a roll** — the merged, back-adjusted series is what Strategy Analyzer sees, so a
  backtest runs on a synthetic continuous price. Absolute price levels in the far past are *not* the prices
  that traded; point-differences and returns are continuous by construction. **INFERRED(from (a) + the
  drawing-objects note).**
- **(c) Price continuity / back-adjustment** — continuous by construction under `MergeBackAdjusted`, at the
  cost of historical price levels being fictional. **VERIFIED(Help Guide).**

### 3.4 Empirical check that *was* performed

At the 2026-06-12 NQ seam, `NQ 09-26` daily bars are the contract's **own thin bars**, not merged NQM6 bars:

| 2026-06-10 | Open | High | Low | Close | Volume |
|---|---|---|---|---|---|
| `NQ 09-26` → NQU6 | 29387.00 | 29537.00 | 28688.50 | 28831.25 | **11,058** |
| `NQ 06-26` → NQM6 | 29094.75 | 29250.00 | 28409.00 | 28554.00 | **745,136** |

Close spread 277.25 pts ≈ the stored 2026-09 offset of 282.25 (the residual is expected: the stored value
is server-supplied and struck one day before the roll — on 2026-06-11 the raw spread was
29751.75 − 29464.75 = 287.00). **VERIFIED(MCP `GetBars`).**

Critically, **passing `mergePolicy: mergeBackAdjust` and `mergePolicy: doNotMerge` produced byte-identical
output.** **VERIFIED.**

### 3.5 ⚠️ Limit of this evidence — the open test

The `GetBars` MCP path returned unmerged, contract-native bars **and ignored its own `mergePolicy`
argument**. That means §3.4 characterises *the MCP bars path*, **not** what `Strategy.OnBarUpdate` receives.
NT8's internal `Instrument.RequestBars(...)` takes distinct `isRolloverAdjusted` and `calculateRollOvers`
flags (**VERIFIED**, reflection) which a strategy load sets from the instrument's MergePolicy, and which
this MCP path evidently does not.

> **Do not conclude from §3.4 that the live strategies are running on unmerged data.** The governing
> setting is `UseGlobalSettings → MergeBackAdjusted`, which says they are merged.

**Recommended decisive test (cheap, allowed, Backtest account only):** run `RunStrategyBacktest` on
`NQ 09-26` over a window straddling 2026-06-12 and inspect whether the pre-seam bars carry NQM6's ~745k
volume (merged) or NQU6's ~11k volume (unmerged). Volume is the discriminator that price alone cannot give,
because back-adjustment is designed to make price look continuous. Until that runs, treat (a)/(b) as
**INFERRED**.

---

## 4. Supported NinjaScript patterns for trading the continuously-active contract (Q4)

### 4.1 What is NOT possible

- **A strategy cannot change its own `Instrument` at runtime.** `NinjaScriptBase.Instrument` and
  `StrategyBase.Instrument` are technically `{ get; set; }` (**VERIFIED**, reflection), but the setter is a
  host/serialization hook: the instrument is consumed during `State.Configure`/`State.DataLoaded` to build
  `BarsArray`, and by `State.Realtime` the data pipeline and the account subscription are already bound.
  Assigning it in `OnBarUpdate` does not re-request data or re-point orders. **INFERRED(state machine +
  §4.2).**
- **`AddDataSeries` cannot be used to reach the front month dynamically.** The Help Guide is explicit:
  *"This method should ONLY be called from the OnStateChange() method during State.Configure"*, arguments
  *"must be hardcoded and NOT dependent on run-time variables which cannot be reliably obtained during
  State.Configure"*, and *"Attempting to add a data series dynamically is NOT guaranteed."*
  **VERIFIED** — <https://ninjatrader.com/support/helpGuides/nt8/adddataseries.htm>.
- **`AddDataSeries` with a bare master name is not documented and does not resolve here.** The Help Guide
  defines `instrumentName` only as *"A string determining instrument name such as 'MSFT'"* and shows the
  qualified futures form `"ES 09-16"`; it *"does not describe how NinjaTrader resolves generic symbols to
  specific contracts."* **VERIFIED(absence).** Consistent with §1.6, where bare `NQ` yielded zero bars.
- **The instrument cannot be edited while the strategy runs:** *"Only disabled strategies can be edited."*
  **VERIFIED(strategies_tab.htm).**
- **There is no continuous/rolling contract symbol in NT8.** No such instrument type or symbol convention
  appears in `InstrumentType`, in the Instruments schema, or in the Help Guide. **INFERRED(absence across
  reflection + schema + docs).**
- **Batch rollover will not help.** It explicitly excludes strategies (§1.1). **VERIFIED.**

### 4.2 What IS possible — the expiry-aware self-disable

The only pattern that is both supported and safe is **not** to make the strategy roll itself, but to make it
**detect that it is stale and stand down loudly**. All the primitives exist and are reachable:

```csharp
// State.DataLoaded — compute once, no runtime dependency
DateTime rollDate = Instrument.MasterInstrument.GetNextRolloverDate(DateTime.Now);
// -> NQ: 2026-09-16 on this install

// OnBarUpdate — cheap date guard
if (Time[0].Date >= rollDate.Date)
{
    // 1. refuse new entries
    // 2. flatten any open position via the managed exit already in the strategy
    // 3. Log(..., LogLevel.Alert) so it surfaces in the Control Center Log tab
}
```

`GetNextRolloverDate` is a public instance method on `MasterInstrument`, and `Instrument.MasterInstrument`
is reachable from any NinjaScript. **VERIFIED(reflection).** `MasterInstrument.GetInstrumentByDate(...)`
can additionally name *which* contract should be active, for the alert text. **VERIFIED(reflection).**

> ⚠️ **This must not be retro-fitted into `WeeklyEdgeP1PCT_v1` or `WeeklyEdgeXMConflict_v2`.** They are
> parity-certified, and CLAUDE.md §6 forbids renaming a parity-certified class while any functional change
> requires a rename. An expiry guard is a functional change. If the owner wants it, it belongs in a new
> `_v2`/`_v3` class that must be re-certified — a separate decision with a real cost.

### 4.3 What the vendor recommends

The Help Guide's only prescription for automated strategies across a roll is the manual one: strategies
"must be manually rolled over", and manual rollover is done "by entering the next contract expiry directly
in the instrument selector (e.g., changing 'ES 09-16' to 'ES 12-16')". **VERIFIED.**

**No forum sources are cited.** The session's WebSearch budget was exhausted (200/200) before forum threads
could be located, and fabricating or guessing forum URLs would violate the sourcing rule. Everything above
rests on the primary Help Guide plus direct reflection and database inspection of this install — which is
the stronger evidence base anyway. **Gap acknowledged, not papered over.**

---

## 5. Running strategy and open position at/after expiry (Q5)

**No documented auto-flatten, no documented auto-liquidation, no documented auto-roll.**
**VERIFIED(absence across rolling_over_a_futures_contrac.htm and strategies_tab.htm).**

A concrete, install-specific finding: `MasterInstruments.AutoLiquidation = 0` for **all four** of
ES (75), NQ (135), RTY (699839150753731), YM (188). **VERIFIED(query).** The corresponding surface is
`MasterInstrument.IsAutoLiquidationEnabled` (**VERIFIED**, reflection). NT8 will therefore **not**
auto-liquidate these contracts at expiry on this install.

Expected sequence after the contract stops trading — **INFERRED(mechanism)**:

1. The strategy stays enabled and stays in `State.Realtime`. Nothing disables it.
2. The feed stops publishing for the expired contract, so no new bars arrive → **`OnBarUpdate` stops
   firing**. This is the dangerous part: **time-based and price-based exits silently stop evaluating.**
   A strategy that would have flattened on a stop, a target, or `ForcedFlatMin` simply never gets the
   chance.
3. An open Sim position **persists**, marked at the last known price. Unrealized P&L freezes rather than
   settling.
4. `ExitOnSessionClose` cannot rescue this — both live strategies have
   `IsExitOnSessionCloseStrategy = false` (**VERIFIED**, blob), so there is no session-close flatten at all.
5. `ConnectionLossHandling = Recalculate` and `StartBehavior = WaitUntilFlat` (**VERIFIED**, blob) do not
   address expiry; `WaitUntilFlat` would in fact **stall a re-enable** while a stranded position is open.

> **Bottom line for Q5: the failure mode is silent, not loud.** The strategy does not error, does not
> disable, and does not flatten — it simply stops receiving data while still holding risk. Nothing in NT8
> will tell you. This is why the roll must be a *scheduled operator action*, and why §4.2's self-disable
> guard has real value.

Both strategies are currently **Flat** (`quantity: 0`) — **VERIFIED(`ListDeployedStrategies`)** — so there
is no stranded position today. The exposure is prospective, from 2026-09-16.

---

## 6. Summary of operating procedure implied

| Question | Answer | Status |
|---|---|---|
| Restart re-resolves front month? | **No** | VERIFIED |
| Disable/re-enable re-resolves? | **No** | VERIFIED |
| Roll procedure | **Reconfigure** (disable → edit instrument → re-enable) | VERIFIED |
| Front month determined by | Stored per-contract-month **Rollover date**, server-supplied, user-editable | VERIFIED |
| Readable in NinjaScript? | Yes — `MasterInstrument.GetNextRolloverDate` / `RolloverCollection` / `GetInstrumentByDate` | VERIFIED |
| MergePolicy 3 | `UseGlobalSettings` → **`MergeBackAdjusted`** here | VERIFIED |
| Next NQ roll | **2026-09-16** (ES 09-14, RTY 09-15, YM 09-18) | VERIFIED |
| Legs to roll | 1 for P1PCT, **4** for XMConflict | VERIFIED |
| Position at expiry | Stranded, silent, no auto-flatten (`AutoLiquidation = 0`) | VERIFIED + INFERRED |

**Recommended, in priority order:**

1. **Schedule the roll for 2026-09-16** (NQ) and decide the XMConflict multi-date policy — 09-14 → 09-18 is
   a 5-day window and there is no single correct day.
2. **Run the §3.5 volume test** before quoting any figure that depends on what history the live strategies
   loaded. `DaysToLoad = 365` spans three seams and 747.50 NQ points of cumulative offset; whether that
   history is merged is currently **INFERRED, not VERIFIED**, and it bears directly on the
   research-vs-execution parity question.
3. **Restate "MergePolicy=3" in repo docs** as *"UseGlobalSettings → MergeBackAdjusted"*.
4. **Treat any expiry-guard code as a new, re-certifiable class** — never an edit to the certified two.

---

## Appendix — sources

**Primary (NT8 Help Guide, `ninjatrader.com/support/helpGuides/nt8/`; 301 → `ninjatrader-live.ninjatrader.com`)**
- `rolling_over_a_futures_contrac.htm` — strategies not rolled forward; eligibility rule; batch/manual rollover; drawing-object/merge note
- `editing_instruments.htm` — Merge Policy, Contract Months, rollover date semantics, Offset derivation
- `adddataseries.htm` — State.Configure restriction; hardcoded-arguments requirement
- `strategies_tab.htm` — Instrument column; "Only disabled strategies can be edited"
- `searching_for_instruments.htm` — Instruments-window search (silent on selector resolution)
- `instruments.htm`, `operations.htm` — navigation/TOC

**This install (authoritative for local state)**
- Reflection via `LookupNinjaScriptSymbol` / `SearchNinjaScriptSymbols` on `MasterInstrument`, `Instrument`,
  `Rollover`, `RolloverCollection`, `MergePolicy`, `StrategyBase`, `NinjaScriptBase`
- `[Reflection.Assembly]::LoadFrom("D:\NinjaTrader8\bin\NinjaTrader.Core.dll")` → `MergePolicy` integer values
- `…\Documents\NinjaTrader 8\db\NinjaTrader.sqlite` — **read-only copy** at
  `…\scratchpad\nt.sqlite`; tables `MasterInstruments`, `Instruments`, `Strategies`, `Strategy2Instrument`
- `…\Documents\NinjaTrader 8\Config.xml` line 116 — `GlobalMergePolicy`
- `…\Documents\NinjaTrader 8\workspaces\Default Yuke.xml` — `<Instrument>NQU6</Instrument>`
- `…\Documents\NinjaTrader 8\log\*.txt` — no rollover/expiry entries to date
- MCP: `ListDeployedStrategies`, `GetBars`, `GetQuote`, `MarketInfo`
