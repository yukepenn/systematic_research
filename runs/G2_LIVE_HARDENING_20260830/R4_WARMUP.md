# R4 — WARM-UP GUARANTEE + LIFECYCLE

**Run** `G2_LIVE_HARDENING_20260830` · task R4 · written 2026-08-30
**Owner's question:** *"How do you guarantee the LIVE strategy is correct, given the backtest needs a
year of pre-load?"*

**Scope discipline.** `WeeklyEdgeP1PCT_v1.cs` and `WeeklyEdgeXMConflict_v2.cs` were **read only** — not
edited, not recompiled, not redeployed. The two running paper deployments
(`dep_306e11dfc8eb`, `dep_5a914d070687`) were **queried read-only** and left enabled. No order, no
account action, no git. No `.cs` was written: this task is the **design**, and every code block below
is a shape to be built into a **new, uncertified class**, never a patch to a certified one.

**Evidence tags.** `VERIFIED(source)` = read from the NT8 Help Guide or from this install's own
reflection/runtime surface. `INFERRED(reasoning)` = derived, and the derivation is shown.

**Sibling document.** `runs/G2_NT8_OPS_20260830/NT8_OPERATIONS_RULES.md` covers the same lifecycle from
the operations side. This document **agrees with it except on one point (§2.1), which it corrects with
direct runtime evidence**, and adds the assertion design, which is not in it.

---

## 0. The answer, in one paragraph

You cannot guarantee correctness by *believing* the pre-load happened. NT8 gives the strategy exactly
one deterministic instant at which the whole pre-load is complete and nothing live has been traded yet
— `State.Transition` / `State.Realtime` — and at that instant the strategy can **read its own
accumulators and count them**. So the guarantee is mechanical and self-administered: at the transition
the strategy prints a GATE / SPEC / OBSERVED / PASS-FAIL table *from the program*, writes it to disk as
a certificate, and **refuses to open new positions until every window is genuinely full**, while never
blocking an exit. The year of pre-load stops being an assumption and becomes a measured, logged,
falsifiable precondition — re-measured automatically on every restart, because a restart re-pays the
warm-up over a *different* year.

---

# PART A — THE WARM-UP ASSERTION (the owner's question)

## 1.1 What "warm" actually means, accumulator by accumulator

`BarsRequiredToTrade = 20` is **not** the warm-up requirement for either strategy. It is a formality
that both satisfy in the first 20 minutes. The real requirement is the state carried in ordinary .NET
collections inside each class, and it is **longer than a year in one case and event-driven rather than
time-driven**. Derived by reading the source; line numbers are cited.

### P1 — `WeeklyEdgeP1PCT_v1.cs`

| # | Accumulator | Field (line) | Research length | Degenerate below | What happens when short — **the direction matters** |
|---|---|---|---|---|---|
| 1 | Ratchet sigma | `diffs` / `volSum` (112, 314) | `VolPeriod = 460` bars | `< 30` → `Sigma()` returns NaN (216) | `ResolveS` falls back to a **fixed** `StopMultiplier·TickSize` = 179 ticks for all 13 members (221). Every ratchet stop is wrong. |
| 2 | HTF tilt | `sessCloses` (116, 393-397) | `TiltSma = 50` → needs `Count > 50`, i.e. **51 completed sessions** | any `Count ≤ 50` | `tilt` stays `0` (395) ⇒ `mm = 1.0` always (410) ⇒ `Tp` differs ⇒ `M` differs. The tilt multiplier is simply absent. |
| 3 | B-MOM band | `slotHist`, `rthDays` (123, 125, 383) | `rthDays ≥ BmomBandDays = 14`; each slot list grows to 60 (381) | `rthDays < 14` | The whole B-MOM branch is skipped (360) ⇒ `bmom ≡ 0` ⇒ `M` loses the `WBmom·bmom = ±2.83` term (415) against `EntryLevel = 3.0`. **The single largest term in the score is missing.** |
| 4 | Range throttle | `rngHist[tod]` (138, 288-292) | `MedianLast(hist, 60)` → **60 sessions** | `hist.Count < 20` → `norm = 0` (442) | ⚠️ **FAILS OPEN.** `norm ≤ 0` makes all three throttle clauses pass (446-448) ⇒ `nThr = 4` ⇒ the vote threshold `nMemLong·nThr·(1+dL) ≥ 16` (452) is far easier. **An under-warm P1 trades MORE than the certified object, not less.** |
| 5 | ATR | `trQ` (147, 531) | 14 bars | `< 14` | Quality features `fDistOpen` / `fDistVwap` are divided by a wrong ATR (460-464). |
| 6 | Volume norm | `volQ` (148, 548) | 240 bars, `≥ 30` else `1.0` (550) | `< 30` | `fDeltaMag` is computed against a denominator of 1.0. |
| 7 | **Quality quantiles** | `qDistOpen…qDeltaMag`, `qCount` (151-154, 477-478) | **`QualWindow = 250` ENTRY EVENTS** | `qCount < QualMinHist = 100` (467) | `qCount < 100` ⇒ `size ≡ 1`, `lastScore ≡ 0` — **the 2-lot never fires**, and the entire W98 per-contract-box rationale (which exists *because* 18.3 % of trades are size 2) is inoperative. `100 ≤ qCount < 250` ⇒ quantiles taken over a short sample ⇒ different size decisions. |

**Row 7 is the one that breaks the usual mental model.** `qCount` increments *only* inside
`if (myQty == 0 && wantLong && UseQualitySize)` (458, 478) — i.e. **once per entry, not once per bar
and not once per session.** No quantity of calendar warm-up *guarantees* it; a quiet year fills it more
slowly than a busy one. It must be **measured**, never assumed. This is the technical heart of the
owner's question.

*How long is 250 entries?* `INFERRED` — `CURRENT_BASELINE.md` §3c (corrected 2026-08-27) gives P1
≈ 3.04 trades on losing sessions and ≈ 2.42 on winning sessions, with 282 flat (`p1_trades == 0`)
sessions in the sample; blended ≈ 1.9–2.0 entries per calendar session. 250 / 1.95 ≈ **128 sessions
≈ 183 calendar days**. `DaysToLoad = 365` therefore carries roughly **2× headroom** on the binding
gate — comfortable, but the margin is an estimate over a *past* activity rate, which is exactly why the
gate reads `qCount` instead of trusting the estimate. (Source statistic is `DISCOVERY_CONSUMED`; used
here only for sizing a safety margin, never quoted as a result.)

**Binding warm-up for P1 = max(51 sessions, 60 sessions, 14 RTH sessions, 250 entry events)
= 250 entry events ≈ 183 calendar days.** `INFERRED`.

### XM — `WeeklyEdgeXMConflict_v2.cs`

| # | Accumulator | Field (line) | Research length | Degenerate below | What happens when short |
|---|---|---|---|---|---|
| 1 | Per-series sigma history | `hist[ES]`, `hist[RTY]`, `hist[YM]` (120, 300) | `SigmaLookback = 60` **qualifying sessions per series** | `SigmaMinHist = 20` → `SampleStd` returns NaN (211) | ⚠️ **FAILS SILENT AND ASYMMETRIC.** A market whose sigma is NaN is skipped by `if (!double.IsNaN(sg) …)` (299) — it contributes to neither `acc` nor `cnt`. `comp = acc / cnt` (302) is then the mean over a **subset** of {ES, RTY, YM}. The strategy still trades, on a **different composite than the one certified**, with no error anywhere. If `cnt == 0`, `comp` is NaN ⇒ `xs = 0` ⇒ never a conflict ⇒ silently never trades. |
| 2 | Series presence | `CurrentBars[i]` (235) | ≥ 1 | 0 | Already hard-guarded — returns. Not a gap. |
| 3 | Instrument identity | `instrumentMismatch` (175-188) | — | — | Already hard-blocks orders (320). Not a gap. |

Note `hist[i].Add(r)` fires **once per qualifying session at the decision bar** (300) — sessions that
are disqualified for staleness (274, 288) or that lack a 09:31/09:45 bar never append. So the count is
again **event-driven**, and 60 *qualifying* sessions ≈ 84 calendar days plus whatever was skipped.
`DaysToLoad = 365` gives ≈ 4× headroom. `INFERRED`.

**Binding warm-up for XM = 60 qualifying sessions in EACH of three series, checked per-series, not in
aggregate.** `INFERRED`.

### The two failure directions, side by side

An under-warm **P1 over-trades** (throttle disabled ⇒ looser vote) and **under-sizes** (no 2-lots).
An under-warm **XM trades a different signal** (composite over a subset). Neither raises an error,
neither shows in the position, and neither is visible in `ListDeployedStrategies`. **Both would look
exactly like a working strategy.** That is the entire case for a mechanical gate.

## 1.2 Recommendation: **REFUSE TO TRADE.** Warn-only is not acceptable here.

**RECOMMENDED: block new entries; never block exits; latch one-way.**

Three reasons, in order of weight:

1. **A warning does not stop the wrong object from trading — it only records that it did.** §1.1 shows
   an under-warm P1 is not a slightly-degraded P1; it is a *looser* strategy taking *more* trades at
   *smaller* size, and an under-warm XM is a *different signal*. Campaign doctrine already settles the
   classification: the parity bands say `< 90 %` decision agreement is "not the object". A strategy
   whose windows are empty is by construction not the object, so it must not hold capital.
2. **The gate is free in the normal case and only bites in the abnormal one.** At `DaysToLoad = 365`
   every gate in §1.1 is satisfied at the transition with 2–4× margin, so a correctly configured
   deployment never notices the gate exists. It fires only when something has actually gone wrong —
   a truncated backfill, a missing secondary series, a contract roll onto a contract with no history,
   a `DaysToLoad` reset to the NT8 default of 5. Those are precisely the events that must not be
   silent.
3. **The cost of refusing is bounded, visible and recoverable; the cost of warning is unbounded and
   invisible.** Refusing costs some flat sessions, logged. Warning costs an unknown number of trades
   that are not the certified object and that will later contaminate the live evidence record.

**But the refusal must be surgical:**

- **Block entries only.** Never gate an exit, never gate the disaster stop, never gate the
  session-close flatten. A strategy that refuses to *close* is a worse failure than the one being
  prevented.
- **Latch one-way.** Evaluate at `State.Realtime` for the certificate, then re-evaluate each realtime
  bar **while disarmed only**; the first time every gate passes, arm **permanently** and never disarm.
  This gives "refuse now, start the moment you are genuinely ready" instead of "dead until a human
  notices" — a strategy started with a short window heals itself and logs the exact bar at which it
  did. A gate that can *close* again mid-position could strand a position; it must not exist.
- **Two tiers, and the second is owner-gated, not code-gated.**

| Verdict | Condition | Behaviour |
|---|---|---|
| **GO** | every gate at its **research** length (row "Research length" in §1.1) | arm; `Log(…, LogLevel.Information)` |
| **DEGRADED** | every **minimum** met but at least one window short of research length | **entries still blocked** unless the owner has explicitly set `AllowDegradedWarmup = true`; `Log(…, LogLevel.Warning)` + `Alert(Priority.High)` either way |
| **NO-GO** | any minimum unmet | entries blocked **unconditionally** — the property cannot override; `Log(…, LogLevel.Error)` + `Alert(Priority.High)` |

`AllowDegradedWarmup` defaults to **false** and is a `[NinjaScriptProperty]`, so choosing to run a
short-window object is a recorded owner decision that appears in the strategy's `DisplayParameters`
string and in every `GetStrategyState` probe — never a default, never invisible.

## 1.3 The NinjaScript shapes

### (a) Where the verdict is computed

```csharp
protected override void OnStateChange()
{
    // … existing SetDefaults / Configure / DataLoaded blocks unchanged …

    else if (State == State.Transition)
    {
        // "Transition is called once as the object has finished processing historical data
        //  but before it starts to process realtime data."  VERIFIED(onstatechange.htm)
        // Every historical OnBarUpdate has run; nothing live has been submitted. This is the
        // only instant at which the pre-load is both COMPLETE and UNSPENT.
        warmupRows    = BuildWarmupTable();     // pure read of the accumulators
        warmupVerdict = ClassifyWarmup(warmupRows);
        armed         = (warmupVerdict == "GO")
                     || (warmupVerdict == "DEGRADED" && AllowDegradedWarmup);
    }
    else if (State == State.Realtime)
    {
        ReportWarmup();      // Print + Log + Alert + certificate file  (see (c))
    }
}
```

`Alert()` is placed in `State.Realtime`, not `State.Transition`, because
**VERIFIED**([alert.htm](https://ninjatrader-live.ninjatrader.com/support/helpguides/nt8/alert.htm)):
*"This method can only be called once the State has reached State.Realtime. Calls to this method in
any other State will be silently ignored."*

### (b) The one-way re-arm, and the two traps

```csharp
protected override void OnBarUpdate()
{
    if (BarsInProgress != 0) return;
    // … the entire certified decision stack runs UNCHANGED, including every accumulator
    //     append.  Nothing below the gate is skipped while disarmed.  See TRAP 2.

    if (!armed && State == State.Realtime)          // one-way: only ever false -> true
    {
        warmupRows = BuildWarmupTable();
        if (ClassifyWarmup(warmupRows) == "GO") { armed = true; ReportWarmup("REARM"); }
    }
```

P1 — gate at the **order site only** (`WeeklyEdgeP1PCT_v1.cs:496`):

```csharp
    // BEFORE:  else if (myQty == 0 && wantLong && pendingAct == ACT_NONE)
    else if (myQty == 0 && wantLong && armed && pendingAct == ACT_NONE)
    { pendingSize = size; EnterLong(size, "L"); pendingAct = ACT_ENTER; }
```

XM — gate at the **order site only** (`WeeklyEdgeXMConflict_v2.cs:320`):

```csharp
    // BEFORE:  if (lastDesired != 0 && myPos == 0 && !forceFlat && !instrumentMismatch)
    if (lastDesired != 0 && myPos == 0 && armed && !forceFlat && !instrumentMismatch)
```

Leave `WeeklyEdgeXMConflict_v2.cs:329` (disaster stop) and `:341` (clock exit) **untouched**, and
leave `WeeklyEdgeP1PCT_v1.cs:482` (session-close flatten) and `:492` (intra-session exit) **untouched**.

> ### ⚠️ TRAP 1 — do not gate `wantLong`. It would break the exit.
> In P1, `wantLong` is read twice: at line 492 `else if (myQty > 0 && !wantLong)` — **that is the
> exit** — and at line 496 — that is the entry. Writing `wantLong = wantLong && armed` inverts the
> exit condition whenever the gate is shut and silently changes the meaning of the `voteOK` / `size`
> columns in the parity export. Gate the `else if` at the order site, never the predicate.

> ### ⚠️ TRAP 2 — do not gate the accumulator writes, or the gate can never open.
> P1's `qCount` increments inside `if (myQty == 0 && wantLong && UseQualitySize)` at line 458 —
> *before* the order site. If the gate is placed there instead, `qCount` freezes at its historical
> value and a strategy that starts one entry short of 250 stays disarmed **forever**: a deadlock.
> The same applies to `hist[i].Add(r)` at `WeeklyEdgeXMConflict_v2.cs:300`. Both are already
> upstream of their order sites, so gating only the order site is correct **and** is the only
> placement that preserves the self-healing re-arm.

### (c) Reporting channels — what actually works for a **headless account strategy**

`VERIFIED` (live probe of both deployments): `isChartHosted: false`, `hasChartControl: false`,
`ChartPanel: null`, `ChartBars: null`, `isHeadless: true`. That determines the channel list:

| Channel | Verified signature / status | Use it for | Verdict |
|---|---|---|---|
| `Log(string, LogLevel)` | `NinjaTrader.NinjaScript.NinjaScript.Log(string message, LogLevel logLevel)`, `LogLevel = {Alert, Information, Warning, Error}` — `VERIFIED`(reflection, this install) | the one-line verdict + every failing row | ✅ **PRIMARY.** The Control Center **Log** tab is the only channel that persists and is reviewable after an unattended overnight. |
| `Print(string)` | standard; NinjaScript **Output** window | the full GATE/SPEC/OBSERVED table | ✅ secondary — ephemeral, and only visible if an Output window happens to be open |
| `Alert(id, Priority, message, soundLocation, rearmSeconds, backBrush, foreBrush)` | `VERIFIED`(reflection: `NinjaScriptBase.Alert`; [alert.htm](https://ninjatrader-live.ninjatrader.com/support/helpguides/nt8/alert.htm)) — **silently ignored outside `State.Realtime`** | DEGRADED / NO-GO only, `Priority.High`, `soundLocation = ""` | ✅ use, and note it cannot report anything about the historical phase itself |
| `Draw.TextFixed` / any `Draw.*` | — | — | ❌ **USELESS HERE.** No chart surface exists on these deployments. Do not build the alarm on it. |
| certificate file (`StreamWriter`) | already the proven pattern in both files (`ExportDir`, 194-200 / 189-201) | the durable audit artifact | ✅ **REQUIRED** — see (d) |

### (d) The certificate — the artifact that makes this auditable

The table must be **printed by the program**, never assembled by hand (campaign method §4). One
certificate is written per lifecycle, at `State.Realtime` and again on any re-arm:

```
WarmupCertDir\warmup_<Tag>_<yyyyMMdd_HHmmssZ>.csv     # UTC-stamped: a restart must NEVER overwrite
```

with a fixed header and one row per gate:

```
strategy,tag,utc,verdict,gate,spec,observed,pass
WeeklyEdgeP1PCTW_v1,p1pct,2026-08-30T10:48:52Z,GO,sigma_diffs,460,460,1
WeeklyEdgeP1PCTW_v1,p1pct,2026-08-30T10:48:52Z,GO,tilt_sessions,51,255,1
WeeklyEdgeP1PCTW_v1,p1pct,2026-08-30T10:48:52Z,GO,rng_sessions,60,255,1
WeeklyEdgeP1PCTW_v1,p1pct,2026-08-30T10:48:52Z,GO,bmom_rth_days,14,254,1
WeeklyEdgeP1PCTW_v1,p1pct,2026-08-30T10:48:52Z,GO,atr_bars,14,14,1
WeeklyEdgeP1PCTW_v1,p1pct,2026-08-30T10:48:52Z,GO,volnorm_bars,240,240,1
WeeklyEdgeP1PCTW_v1,p1pct,2026-08-30T10:48:52Z,GO,qual_entries,250,<measured>,?
```

plus a **provenance block** written from the API surface in §3, so the certificate proves *what data
arrived*, not merely what the accumulators reached:

```
env,DaysToLoad,365
env,bars_first_time,2025-08-31 18:01:00
env,bars_last_time,<at transition>
env,bars_count,<Bars.Count>
env,current_bar,<CurrentBar>
env,trading_hours,CME US Index Futures ETH
env,series_1_count,<BarsArray[1].Count>          # XM only, one row per added series
env,series_1_first_time,<BarsArray[1].GetTime(0)>
```

The exact gate list for XM replaces rows 1–7 with, **per series**:
`xm_hist_ES` spec 60 / min 20, `xm_hist_RTY` spec 60 / min 20, `xm_hist_YM` spec 60 / min 20,
observed `hist[i].Count`. **Check each series separately** — an aggregate would hide exactly the
subset-composite failure described in §1.1.

## 1.4 The obligation that comes with building this

The gate cannot be added to `WeeklyEdgeP1PCT_v1.cs` or `WeeklyEdgeXMConflict_v2.cs`. Campaign rule:
*rename the class on every functional iteration; never rename a class that has already been
parity-certified.* So:

1. Build **new classes** — `WeeklyEdgeP1PCTW_v1` / `WeeklyEdgeXMConflictW_v1` — as byte-copies plus
   the gate, the report and the two new properties. The certified files stay on disk untouched.
2. **The new classes are not certified.** Run each against its certified parent with the gate forced
   open (`RequireWarmup = false`) over the same window, and require the binding bands: decision-series
   agreement **≥ 99 %** and trade counts within **2 %**. Compare decisions before dollars.
3. Only after that verdict may a gated class replace a certified one in the deployment. Until then the
   gated class is a *shadow*, not a replacement.
4. `RequireWarmup = false` exists solely for step 2 and for Strategy Analyzer runs (where `DaysToLoad`
   does not apply at all — §2.3). It must be **true** in every live/paper deployment.

---

# PART B — THE LIFECYCLE FINDINGS

## 2. `DaysToLoad` semantics, and its interaction with `BarsRequiredToTrade` (Q1)

### 2.1 ⚠️ CORRECTION: the Help Guide says "trading days"; this install loads a **calendar** window

**VERIFIED (doc)**
([daystoload.htm](https://ninjatrader-live.ninjatrader.com/support/helpguides/nt8/daystoload.htm)):
*"Determines the number of trading days which will be configured when loading the strategy from the
Strategies Grid"*, with the note *"A trading day is defined by a Trading Hour template."* Default **5**.
Applies **only** to the Strategies Grid — not charts, not the Strategy Analyzer.

**VERIFIED (this install, runtime)** — `GetStrategyState(DEMO8383477, 399550060)`, the live
`WeeklyEdgeP1PCT_v1` deployment created 2026-08-30T10:48:00Z with `DaysToLoad = 365`:

```
DaysToLoad : 365
From       : 2025-08-30T06:48:00.8555168      <-- To minus 365 CALENDAR days, to the tick
To         : 2026-08-30T06:48:00.8555168      <-- the deployment instant (06:48 ET = 10:48 UTC)
BarsToLoad : 0                                <-- bar-count path unused; this is a date window
Bars       : From='2025-08-30' To='2026-08-30' period='1 Minute' Count='352672'
             firstTime = 8/31/2025 6:01:00.000 PM   lastTime = 8/28/2026 5:00:00.000 PM
TradingHours: CME US Index Futures ETH
```

`From` is `To − 365 × 24 h` **exactly**, and the first bar delivered is the first session open *after*
`From` (Sunday 2025-08-31 18:01), not 365 trading days back. **`DaysToLoad = N` requests the calendar
window `[now − N days, now]`.** The number of *sessions* you receive is whatever falls inside it.

**This resolves an open question in the sibling document** (`NT8_OPERATIONS_RULES.md` §3, "Bar count
sanity check — INFERRED, worth confirming", and its open item "confirm whether 365 trading days were
genuinely loaded"). Its arithmetic used 365 *trading* days ≈ 503,700 possible minutes and concluded we
were seeing "~70 %", raising the possibility of a silent truncation. **The denominator was the wrong
quantity.** Against the correct denominator: 352,672 bars ÷ 1,380 minutes per 18:00→17:00 session
= **255.6 sessions**, which is exactly the number of CME index-futures sessions in the 362 elapsed days
from 2025-08-31 to 2026-08-28 (362 × 5/7 ≈ 258.6, less the handful of full closures). The load was
**not** truncated: essentially every minute of every session is present. `VERIFIED`(arithmetic on the
runtime probe).

Corollary, also worth recording: `NQU6` (NQ 09-26) carries continuous 1-minute data back to
2025-08-31 with ~1,380 bars per session. A deferred quarterly contract cannot have traded every minute
a year before it became front month, so the series is **merged / back-adjusted** by the instrument's
default merge policy. `INFERRED`(a genuinely thin deferred contract would show a fraction of these
bars). This dissolves the sibling's related worry that a single quarterly contract could not satisfy a
365-day request.

**Practical rules.**
- `sessions_received ≈ DaysToLoad × 0.70`. `INFERRED`(255.6 / 365 = 0.700).
- To guarantee **S sessions**, set `DaysToLoad ≈ ⌈S / 0.68⌉` and then **verify with the assertion** —
  the ratio is not a contract.
- P1's binding gate (250 entry events, §1.1) needs ≈ 183 calendar days; `DaysToLoad = 365` is right,
  with margin. Do not reduce it.

### 2.2 Interaction with `BarsRequiredToTrade`

**VERIFIED**([barsrequiredtotrade.htm](https://ninjatrader-live.ninjatrader.com/support/helpguides/nt8/barsrequiredtotrade.htm)):
*"The number of historical bars required before the strategy starts processing order methods called in
the `OnBarUpdate()` method."* Default 20. In multi-series strategies *"the restriction applies only to
the primary Bars object"* — *"should your strategy logic intertwine calculations across different Bars
objects please ensure all Bars objects have met the `BarsRequiredToTrade` requirement before
proceeding."*

They are **orthogonal knobs**: `DaysToLoad` sets *how much history is replayed*; `BarsRequiredToTrade`
sets *how far into that replay order methods are allowed*. `BarsRequiredToTrade = 20` does not shorten
a 365-day load, and a large `DaysToLoad` does not delay live trading. Both strategies set 20, both
observe `current_bar = 352670` — the constraint is irrelevant here and **is not a warm-up mechanism**.
XM's own guard `for (i=1;i<4;i++) if (CurrentBars[i] < 1) return;` (line 235) is the multi-series
protection the doc asks for; the assertion in Part A extends it from *1 bar* to *60 sessions*.

### 2.3 Does historical processing run the full `OnBarUpdate` path? **YES.**

**VERIFIED (doc)** — the `BarsRequiredToTrade` definition itself presupposes it: `OnBarUpdate()` is
called during historical processing, and what the setting gates is *order-method processing within
it*, not the call. `State.Historical` is defined as *"begins to process historical data"* and
`State.Transition` as *"finished processing historical data"*
([state.htm](https://ninjatrader-live.ninjatrader.com/support/helpguides/nt8/state.htm),
[onstatechange.htm](https://ninjatrader-live.ninjatrader.com/support/helpguides/nt8/onstatechange.htm)).

**VERIFIED (this install, runtime)** — and this is the decisive evidence, because it shows the *order
methods* ran too, not merely the calculations:

| deployment | `state` | `current_bar` | `trade_count` | `net_profit_currency` | `position` |
|---|---|---|---|---|---|
| `dep_306e11dfc8eb` P1PCT | Realtime | 352,670 | 0 | **70,585.0** | Flat |
| `dep_5a914d070687` XM | Realtime | 352,670 | 0 | **43,705.0** | Flat |

Non-zero P&L with zero real-time trades, a flat position and an untouched account is exactly the
documented split between the **virtual** Strategy Position built by replaying history and the real
Account Position. `EnterLong`/`ExitLong`/`EnterShort` all executed across the warm-up.

⚠️ **Those two dollar figures are warm-up artifacts, not paper-account performance.** They are the
replayed result over a window that spans BURNED (2026-05-31→07-31) and VIRGIN (≥2026-08-01) data. They
are not quotable as a result at any level. (Concurs with `NT8_OPERATIONS_RULES.md`.)

⇒ **Rolling windows DO fill during the historical phase, before `State.Realtime`.** The premise behind
the owner's question is sound; what was missing was the proof that they filled *far enough*.

### 2.4 One configuration caveat found while probing

`MaximumBarsLookBack : 0` on the live P1 deployment; `VERIFIED`(reflection) the enum is
`{TwoHundredFiftySix, Infinite}`, so 0 = **TwoHundredFiftySix**. This truncates `Series<T>` /
`Close[n]` lookback beyond 256 bars. **Neither certified strategy is affected** — both keep their state
in plain `List`/`Queue`/`Dictionary` and only ever index `[0]`. But any *new* warm-up diagnostic that
tries to measure history by reading `Close[300]` or `Time[500]` will throw. Measure history with
`Bars.GetTime(0)` and `Bars.Count` (§3), never by deep bar indexing.

## 3. Can a strategy know how much history it received? (Q2) — **YES, and precisely**

### 3.1 Canonical transition detection

`OnStateChange()` with `State == State.Transition` (prepare / evaluate) and `State == State.Realtime`
(report / alert). Inside `OnBarUpdate()`, `State == State.Realtime` discriminates a live bar from a
replayed one.

`VERIFIED`(reflection, this install) the enum is
`{Undefined, SetDefaults, Configure, Active, DataLoaded, Historical, Transition, Realtime, Terminated, Finalized}`,
and the live P1 probe returns `"State": 7` alongside `"state": "Realtime"` — confirming the ordinals
`Historical = 5`, `Transition = 6`, `Realtime = 7` on this install.
`VERIFIED`([onstatechange.htm](https://ninjatrader-live.ninjatrader.com/support/helpguides/nt8/onstatechange.htm)):
`Transition` is *"called once as the object has finished processing historical data but before it
starts to process realtime data"* — which is what makes it the correct evaluation point: complete, and
unspent.

**Not valid discriminators — do not use any of these:**

- `IsFirstTickOfBar` — `VERIFIED`(live probe returns `IsFirstTickOfBar: true` on a
  `Calculate.OnBarClose` strategy). With `OnBarClose` it is *always* true, historical and realtime
  alike. It marks a bar boundary, never a data-origin boundary.
- `Bars.IsFirstBarOfSession` / `IsLastBarOfSession` — session boundaries; both fire throughout the
  historical replay.
- `Bars.IsInReplayMode` — Market Replay only (and Replay is PAUSED under owner risk-control anyway).

### 3.2 The measurement surface — all `VERIFIED` present on `NinjaTrader.Data.Bars` in this install

| Member | Type | What it answers |
|---|---|---|
| `Bars.GetTime(0)` | `DateTime` | **the single most useful number** — the timestamp of the *first* bar loaded |
| `Bars.Count` | `int` | total bars in the series (352,672 observed) |
| `CurrentBar` / `Bars.CurrentBar` | `int` | 0-based index of the bar being processed |
| `CurrentBars[i]` | `int[]` | per-series bar index — **the multi-series answer**; XM observed `[352670, 352609, 346437, 347670]`, i.e. RTY runs 6,233 bars thinner than NQ |
| `BarsArray[i].Count` / `.GetTime(0)` | | the same two facts, per added series |
| `Bars.FromDate` / `Bars.ToDate` | `DateTime` | the requested window |
| `Bars.DayCount` | `int` | trading days in the series |
| `Bars.BarsSinceNewTradingDay` | `int` | position within the current session |
| `Bars.GetSessionEndTime(i)` | `DateTime` | session end at a given index |
| `Bars.TradingHours` | `TradingHours` | the template that defines "a trading day" |
| `DaysToLoad` | `int` | `VERIFIED` settable on `StrategyBase` **and readable at runtime** — so the certificate can record what was actually requested, not what someone believes was requested |

Everything the certificate in §1.3(d) needs is available at `State.Transition`.

## 4. Restart persistence (Q4)

### 4.1 Do Control-Center account strategies survive an NT8 restart? **UNDOCUMENTED.**

I read the Help Guide pages that would have to say so and they do not:
[strategies_tab.htm](https://ninjatrader-live.ninjatrader.com/support/helpguides/nt8/strategies_tab.htm)
(documents the grid, the `Enabled` checkbox and the `Workspace` column — silent on restart),
[syncing_account_positions.htm](https://ninjatrader-live.ninjatrader.com/support/helpguides/nt8/syncing_account_positions.htm)
(silent on platform restart),
[running_a_ninjascript_strategy.htm](https://ninjatrader-live.ninjatrader.com/support/helpguides/nt8/running_a_ninjascript_strategy.htm)
(chart-hosted only). `workspaces.htm` returns HTTP 500 from the doc host.
**Status: UNDOCUMENTED — must be observed, never assumed.** (Concurs with `NT8_OPERATIONS_RULES.md`.)

Only hard clue, `VERIFIED`(runtime): the strategy object carries `Workspace: "Default Yuke"`, tying the
grid row to workspace persistence. That suggests the **row** returns; it says nothing about whether the
**`Enabled` checkbox** returns checked — the only part that matters. Both failure modes are bad and
they are opposite: silently resuming live trading unattended, or silently *not* resuming while we
believe it is running.

### 4.2 The exact experiment to run — **while flat**

Preconditions: strategy position **and** account position flat on `DEMO8383477`; no active orders;
outside RTH is preferable but any flat moment works; save the workspace first.

```
STEP 0  ListDeployedStrategies                     -> record for each deployment:
        ListStrategies(account="DEMO8383477")         state, isEnabled, current_bar, currentBars[],
        GetStrategyState(acct, 399550060)              net_profit_currency, DaysToLoad,
        GetStrategyState(acct, 399550061)              From, To, Bars.firstTime, Bars.lastTime
STEP 1  Confirm Flat / qty 0 / active_order_count = 0 on BOTH.  ABORT if not.
STEP 2  Note the workspace name ("Default Yuke") and save the workspace.
STEP 3  Shut NinjaTrader down normally (File -> Exit).  Do NOT kill the process:
        a clean exit and a crash are DIFFERENT experiments (see 4.4).
STEP 4  Restart NinjaTrader.  Do NOT touch the Strategies tab.
STEP 5  Wait for the connection to come up, then re-run every STEP 0 call.
```

**Decision rule — three distinguishable outcomes:**

| Observation | Meaning | Consequence |
|---|---|---|
| rows present, `isEnabled = true`, `state = Realtime`, **`From`/`To` slid forward to the restart instant**, `net_profit_currency` changed | strategies auto-resume **and** re-pay the warm-up | unattended overnight is viable — *but* every restart is a fresh warm-up over a different year ⇒ Part A is mandatory |
| rows present, `isEnabled = false` (or `state` not Realtime) | grid persists, enablement does not | a restart silently stops trading; a monitoring check is mandatory before we can claim "it is running" |
| rows absent | nothing persists | the deployment must be re-created after every restart |

**The `From` / `To` / `Bars.firstTime` triple is the measurement that makes this experiment
conclusive.** If those values slid forward, the strategy demonstrably re-ran its historical phase; if
they are byte-identical to STEP 0, it did not.

Repeat once as a **crash** experiment (kill the process while flat) only if the clean-exit result is
"auto-resumes" — the two paths can differ, and the crash path is the one that will actually happen at
03:00.

### 4.3 What state is lost, and what the strategy sees

`INFERRED`(from §2.3 + the documented lifecycle; no Help Guide page states it directly, and none was
found that contradicts it): the strategy object is **reconstructed**. It re-enters
`SetDefaults → Configure → DataLoaded → Historical → Transition → Realtime`. **Every instance field in
§1.1 resets to its declared initial value** — `diffs`, `sessCloses`, `slotHist`, `rthDays`, `rngHist`,
`qDistOpen…qDeltaMag`, `qCount`, `mAnchor`, `mS`, `mPend`, `tgtPrev`, `myEntryPx`, `myQty`, `sessPnl`,
`sessStopped`, and XM's `hist[]`, `anchorX[]`, `myPos`, `realizedPnl` — and is rebuilt **solely** by
replaying `DaysToLoad` calendar days ending at the **restart** instant.

Two consequences that matter more than they look:

1. **The window slides.** `From`/`To` are stamped from the clock at start (§2.1). A restart on a later
   date warms over a *different* year, so the post-restart accumulators are **not** the pre-restart
   accumulators. The object is deterministic *given its window*, and the window moved. Anyone
   reconciling live behaviour across a restart must reconcile against the new window.
2. **The warm-up is re-paid every time, so the assertion must re-run every time.** Because it lives in
   `OnStateChange(State.Transition/Realtime)`, it does — automatically, with no operator action. That
   is the strongest single argument for putting the check in the strategy rather than in a checklist.

Also `VERIFIED`(doc,
[syncing_account_positions.htm](https://ninjatrader-live.ninjatrader.com/support/helpguides/nt8/syncing_account_positions.htm)):
on start the strategy *"will check for any active orders previously generated by the strategy on your
account and cancel those first"*, and *"should the strategy be unable to cancel and receive
confirmation on the cancellation of these orders within 40 seconds the strategy will not start and an
alert will be issued."* A restart is therefore also a 40-second order-cancellation race.

### 4.4 Lifecycle settings observed on the live deployments (`VERIFIED`, runtime)

`StartBehavior = WaitUntilFlat` (=3), `ConnectionLossHandling = Recalculate` (=1),
`DisconnectDelaySeconds = 10`, `NumberRestartAttempts = 4`, `RestartsWithinMinutes = 5`,
`RealtimeErrorHandling = 2`, `IsWaitUntilFlat = false`, `IsAdoptAccountPositionAware = false`.
`VERIFIED`(reflection) `ConnectionLossHandling = {KeepRunning, Recalculate, StopStrategy}` and
`StartBehavior = {AdoptAccountPosition, ImmediatelySubmit, ImmediatelySubmitSynchronizeAccount, WaitUntilFlat, WaitUntilFlatSynchronizeAccount}`.

Warm-up-relevant reading of these:

- `Recalculate` + up to 4 restarts in 5 minutes means a flaky connection can trigger **up to four full
  warm-up replays in five minutes**, each one a fresh `Transition`. The assertion must therefore be
  cheap (it is: a handful of `.Count` reads) and its certificate filename must be UTC-stamped so the
  four events do not overwrite each other.
- `WaitUntilFlat` interacts with the warm-up: the replay ends with the strategy holding whatever
  *virtual* position the last replayed bar left. Both objects flatten at every session end — P1 at
  `lastBar` (482) and XM at the clock/`forceFlat` (341) — so **starting between sessions guarantees a
  flat virtual position**, while starting mid-session can leave the strategy waiting.
  ⇒ *Operational rule: prefer to start or restart between sessions.* `INFERRED`.

## 5. Strategy-level persistence between sessions/restarts (Q5)

**NT8 offers no documented mechanism for persisting arbitrary strategy runtime state across a
restart.** What exists, and what it is not:

- `[NinjaScriptProperty]` inputs persist **as configuration** with the grid row / workspace. They are
  not a runtime-state channel; writing to them from `OnBarUpdate` is unsupported and would also mutate
  the certified parameter record that `GetStrategyState` reports.
- `UserData` exists on the Cbi object (`VERIFIED`, live probe returns
  `"<NinjaTrader>\r\n  <_Impl></_Impl>\r\n</NinjaTrader>"`). It is undocumented for NinjaScript use.
  **Do not use it.**
- `NinjaTrader.Core.Globals.UserDataDir` (`VERIFIED`, reflection — read-only `string`) is the correct
  anchor for any file a strategy writes.
- **What practitioners do:** serialize state to a file — write in `OnStateChange(State.Terminated)`
  *and* periodically (a hard crash never reaches `Terminated`), read it back in `State.DataLoaded`.
  Occasionally a `static` class is used to survive a strategy restart within one NT8 process; that
  survives nothing if the process dies.

### RECOMMENDATION: **do not persist decision state. Persist evidence only.**

Persisting `qCount`, `rngHist`, `hist[]` and the rest to disk would create a **second source of truth**
for the strategy's state — one that no backtest ever reads and that can silently disagree with the
replay. A live object whose behaviour depends on a file on disk is, by construction, not the object
that was certified, and the disagreement would be undiscoverable: it produces no error, only different
trades. That is precisely the class of silent-divergence failure this campaign keeps paying for.

The replay is **deterministic, reproducible and auditable**; a snapshot is none of those. So the answer
to *"the backtest needs a year of pre-load"* is not "cache the year" — it is **"give it the year, then
make the strategy prove it got it."** Write the warm-up certificate (§1.3(d)) to disk, never the
accumulators.

---

## 6. Claims register

| # | Claim | Status |
|---|---|---|
| 1 | `DaysToLoad` documented as "trading days", Strategies-Grid only, default 5 | `VERIFIED`([daystoload.htm](https://ninjatrader-live.ninjatrader.com/support/helpguides/nt8/daystoload.htm)) |
| 2 | **This install requests a 365-CALENDAR-day window**: `From = To − 365 d` exactly; first bar 2025-08-31 18:01 | `VERIFIED`(runtime `GetStrategyState`, this install) |
| 3 | 352,672 bars ÷ 1,380 min = 255.6 sessions = the full session count in the window ⇒ **not truncated** | `VERIFIED`(arithmetic on runtime probe) |
| 4 | `NQU6` series is merged / back-adjusted (a deferred contract cannot show ~1,380 bars/session a year early) | `INFERRED` |
| 5 | `sessions ≈ DaysToLoad × 0.70` | `INFERRED`(255.6 / 365) |
| 6 | `BarsRequiredToTrade` = historical bars before **order methods** run; primary series only; default 20 | `VERIFIED`([barsrequiredtotrade.htm](https://ninjatrader-live.ninjatrader.com/support/helpguides/nt8/barsrequiredtotrade.htm)) |
| 7 | Historical processing runs the full `OnBarUpdate` path **including order methods** | `VERIFIED`(runtime: `net_profit_currency` 70,585 / 43,705 with `trade_count = 0`, Flat, untouched account) |
| 8 | State enum + ordinals `Historical=5, Transition=6, Realtime=7` | `VERIFIED`(reflection + live `"State": 7` ⇄ `"Realtime"`) |
| 9 | `Transition` = historical finished, before realtime begins | `VERIFIED`([onstatechange.htm](https://ninjatrader-live.ninjatrader.com/support/helpguides/nt8/onstatechange.htm)) |
| 10 | `IsFirstTickOfBar` is **not** a historical/realtime discriminator | `VERIFIED`(live probe `true` under `Calculate.OnBarClose`) |
| 11 | `Bars.Count/GetTime(0)/DayCount/BarsSinceNewTradingDay/FromDate/ToDate/GetSessionEndTime`, `CurrentBars[]` all present | `VERIFIED`(reflection, this install) |
| 12 | `Alert()` is silently ignored outside `State.Realtime` | `VERIFIED`([alert.htm](https://ninjatrader-live.ninjatrader.com/support/helpguides/nt8/alert.htm)) |
| 13 | `Log(string, LogLevel)`; `LogLevel = {Alert, Information, Warning, Error}` | `VERIFIED`(reflection, this install) |
| 14 | Both deployments are **headless** — `Draw.*` has no surface | `VERIFIED`(runtime: `isChartHosted:false`, `ChartPanel:null`) |
| 15 | `MaximumBarsLookBack = TwoHundredFiftySix` (probe value 0) | `VERIFIED`(reflection + runtime) |
| 16 | Strategy cancels its prior orders on start; 40 s or it will not start | `VERIFIED`([syncing_account_positions.htm](https://ninjatrader-live.ninjatrader.com/support/helpguides/nt8/syncing_account_positions.htm)) |
| 17 | Control-Center strategy **restart persistence is UNDOCUMENTED** | `VERIFIED`(absence, by direct reading of strategies_tab.htm and syncing_account_positions.htm; workspaces.htm returns HTTP 500) |
| 18 | On restart all instance state is lost and rebuilt by replay over a **slid** window | `INFERRED`(lifecycle + claim 2 + claim 7) |
| 19 | P1's binding gate is 250 **entry events**, not a bar or day count | `VERIFIED`(source: `WeeklyEdgeP1PCT_v1.cs:458,467-478`) |
| 20 | Under-warm P1 **fails open** (`norm=0 ⇒ nThr=4`, throttle disabled) | `VERIFIED`(source: lines 442-448) |
| 21 | Under-warm XM trades a **subset composite**, silently | `VERIFIED`(source: lines 296-302) |
| 22 | 250 entries ≈ 128 sessions ≈ 183 calendar days | `INFERRED`(CURRENT_BASELINE §3c activity rate; the gate measures it rather than trusting it) |
| 23 | No NT8 mechanism persists arbitrary strategy runtime state across a restart | `VERIFIED`(absence in doc) + `INFERRED` |
| 24 | `Globals.UserDataDir`, `StrategyBase.DaysToLoad`, `IsAdoptAccountPositionAware` exist here | `VERIFIED`(reflection) |

## 7. Open items handed forward

1. **Run the §4.2 restart experiment while flat.** Nothing about unattended operation can be claimed
   until its three-way outcome is recorded. It is the only item here that cannot be settled from a
   document or a probe.
2. **Build `WeeklyEdgeP1PCTW_v1` / `WeeklyEdgeXMConflictW_v1`** and run the §1.4 parity certification
   (≥ 99 % decision agreement, trade counts within 2 %) with the gate forced open, before any gated
   class replaces a certified one.
3. **Measure P1's actual `qCount` at the transition** on the live deployment — it is the one gate in
   §1.1 whose satisfaction is currently an estimate rather than an observation. The assertion produces
   it as a by-product on its first run.
4. **Contract roll.** A `DaysToLoad = 365` window on a newly added contract restarts the whole warm-up
   from zero. Roll planning must treat the roll as a restart event and wait for a `GO` certificate.
5. The 365-day warm-up window spans **BURNED** (2026-05-31→07-31) and **VIRGIN** (≥2026-08-01) data.
   The warm-up *replay* is unavoidable and is not a research read, but **no figure produced by it —
   `net_profit_currency` above all — is quotable at any level.**
