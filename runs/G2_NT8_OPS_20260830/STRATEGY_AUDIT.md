# STRATEGY CORRECTNESS AUDIT — deployed NT8 objects vs the certified record

Audit date **2026-08-30** · read-only · no repo file modified · no git command run · no order,
enable, disable, deploy, stop, account, connection or backtest tool called.
Tools used: `GetMcpCapabilities`, `ListAccounts`, `GetConnections`, `ListDeployedStrategies`,
`ListAllStrategies`, `MarketInfo`, plus local file reads and `sha256sum`.

> ## VERDICT: **NO PARAMETER DIFFS.** Every certified parameter on both strategies matches, in the
> ## source defaults **and** in NT8's live read-back. Both `.cs` files are byte-identical to the repo.
> ## The exposure is **not** parameter drift — it is **four unguarded live-trading hazards** and a
> ## **contract roll ~11 days away that nothing in the system will announce.**

---

## 0. What is actually deployed (verified in-session, not assumed)

`ListDeployedStrategies` + `ListAllStrategies(includeTerminal=true)`:

| deployment | class | strategy id | account | instrument | period | state | enabled | position |
|---|---|---|---|---|---|---|---|---|
| `dep_306e11dfc8eb` | `WeeklyEdgeP1PCT_v1` | 399550060 | DEMO8383477 | NQU6 | 1-min Last | **Realtime** | **true** | Flat |
| `dep_5a914d070687` | `WeeklyEdgeXMConflict_v2` | 399550061 | DEMO8383477 | NQU6 | 1-min Last | **Realtime** | **true** | Flat |

Both `hostMode: account`, `isHeadless: true`, `Calculate: OnBarClose`, `StartBehavior: WaitUntilFlat`,
`EntriesPerDirection: 1`, `EntryHandling: AllEntries`, `BarsRequiredToTrade: 20`,
`currentBar: 352670`, `activeOrderCount: 0`, `DaysToLoad: 365`.

XM resolved its three secondaries correctly and **in the frozen order**:
`BarsArray = [NQU6, ESU6, RTYU6, YMU6]`, `currentBars = [352670, 352609, 346437, 347670]`.

Environment: NT8 **8.1.8.1**, CrossTrade add-on **v1.13.9**, backtest fingerprint
`sha256:b4255f1b0dd7fba1` — identical to the fingerprint in `FROZEN_INCUMBENT_20260827.md` §3.
Only connection **Connected** is `Simulation` (user `rainazur`, up 6,592 s). `Live` is
**Disconnected**. DEMO8383477 is a paper account on the Simulation connection.

**Governance:** enablement is **recorded and authorized** —
`research/operational/OWNER_DECISION_20260830.md` §3 authorizes simulation deployment of both
certified strategies on DEMO8383477 at M_11 quantities, and `EXECUTION_MANIFEST.md` §D records
**LIVE (real money) ENABLED = NO**. This audit finds no governance violation in the fact of
deployment. It is a paper account, and `Live` is disconnected.

⚠️ **Do not read the deployment's `net_profit_currency` as live P&L.** P1/PCT reports **$70,585**
and XM **$43,705** with `trade_count: 0`. Those are the *historical backfill* simulations produced
by the 365-day load at strategy start. **Zero real orders have been placed.** `ordersCount: 0` on
both.

---

## 1. Source integrity — sha256, both sides

| class | NT8 `bin/Custom/Strategies/` | repo `research/weekly_edge/ninjascript/` | spec records | |
|---|---|---|---|---|
| `WeeklyEdgeP1PCT_v1` | `ee4c765bc5cab23096f4009943ef6a79e03c3d2d7c671a2285f6cec2676e87b2` | **identical** | `ee4c765bc5cab230` | ✅ **MATCH** |
| `WeeklyEdgeXMConflict_v2` | `2ec00dd4d0a11b999b649dcf358b63f92bc09f4edf1d2cec77c076b64c910dde` | **identical** | `2ec00dd4d0a11b99` | ✅ **MATCH** |

Full 64-hex digests agree between the NT8 workspace and the repo, and both 16-char prefixes agree
with `WE_P1PCT_PARITY_20260827/spec.yaml:31`, `c1_incumbent_anatomy.md:165-167`. **No hand edit
exists in the NT8 workspace.**

Supporting: the two structural diffs were recomputed rather than trusted.

- `WeeklyEdgeP1_v3.cs` → `WeeklyEdgeP1PCT_v1.cs`: header block, class name, `Name`, `Description`,
  `Tag`, export filename, and **the two `sessPnl` accumulation sites only**. The parameter block is
  untouched. The header's claim "everything else is byte-identical to the parity-tested v3" is
  **verified true**, so W52's decision-layer certification transfers intact.
- `WeeklyEdgeXMConflict_v1.cs` → `_v2.cs`: header, class name, `Name`, `Tag`, and **one** inserted
  causal guard (`exitBarExists`). No parameter changed. Matches `WE_XM_PARITY_20260827/REPORT.md` §4.

`WeeklyEdgeXMConflict_v1` (superseded, "must not be run") is **not loaded on any account.** ✅

---

## 2. Parameter-by-parameter — `WeeklyEdgeP1PCT_v1`

"Deployed default" = `SetDefaults` in the installed `.cs`. "NT8 read-back" = the `parameters`
object returned live by `ListAllStrategies` — this is the stronger check, because it would expose a
UI-level override of a source default. Certified = `c1_incumbent_anatomy.md` §1 (RAW-FACT cites to
`.cs:179-184` and to `run_we_w97/w19/w98`), `FROZEN_INCUMBENT_20260827.md` §4,
`WE_P1PCT_PARITY_20260827/`.

| # | parameter | deployed default | NT8 read-back | certified value | |
|---|---|---|---|---|---|
| 1 | `VolPeriod` | 460 | 460 | 460 | ✅ MATCH |
| 2 | `SMinTicks` | 40 | 40.0 | 40 | ✅ MATCH |
| 3 | `SMaxTicks` | 1200 | 1200.0 | 1200 | ✅ MATCH |
| 4 | `StopMultiplier` | 179 | 179.0 | 179 | ✅ MATCH |
| 5 | `TiltSma` | 50 | 50 | 50 | ✅ MATCH |
| 6 | `TiltMult` | 1.25 | 1.25 | 1.25 | ✅ MATCH |
| 7 | `TiltRescale` | 0.9026 | 0.9026 | 0.9026 | ✅ MATCH |
| 8 | `WSolar` | 0.7086 | 0.7086 | 0.7086 | ✅ MATCH |
| 9 | `WBmom` | 2.83 | 2.83 | 2.83 | ✅ MATCH |
| 10 | `BmomBandDays` | 14 | 14 | 14 | ✅ MATCH |
| 11 | `EntryLevel` | 3.0 | 3.0 | 3.0 (hysteresis ±3.0) | ✅ MATCH |
| 12 | `ExitLevel` | 1.0 | 1.0 | 1.0 | ✅ MATCH |
| 13 | `EntryBlockMin` | 30 | 30 | 30 | ✅ MATCH |
| 14 | `ForcedFlatMin` | 21 | 21 | 21 | ✅ MATCH |
| 15 | `HaltDollars` | 1300.0 | 1300.0 | −$1,300 **per contract** | ✅ MATCH |
| 16 | `TargetDollars` | 1000.0 | 1000.0 | +$1,000 **per contract** | ✅ MATCH |
| 17 | `CommissionRT` | 4.36 | 4.36 | 4.36 | ✅ MATCH |
| 18 | `QualWindow` | 250 | 250 | 250 | ✅ MATCH |
| 19 | `QualMinHist` | 100 | 100 | 100 | ✅ MATCH |
| 20 | `UseQualitySize` | true | true | true (size 2 when score ≥ 3) | ✅ MATCH |
| 21 | `UseSessionBox` | true | true | true | ✅ MATCH |
| 22 | `ExportDir` | `""` | `""` | `""` (ledger off) | ✅ MATCH |
| 23 | `Tag` | `"p1pct"` | `"p1pct"` | `"p1pct"` | ✅ MATCH |
| 24 | `Calculate` | OnBarClose | OnBarClose | OnBarClose | ✅ MATCH |
| 25 | `EntriesPerDirection` | 1 | 1 | 1 | ✅ MATCH |
| 26 | `EntryHandling` | AllEntries | AllEntries | AllEntries | ✅ MATCH |
| 27 | `IsExitOnSessionCloseStrategy` | false | — | false (self-flatten) | ✅ MATCH |
| 28 | `IncludeCommission` | true | — | true | ✅ MATCH |
| 29 | `BarsRequiredToTrade` | 20 | 20 | 20 | ✅ MATCH |

**29/29 MATCH. Zero diffs.** The hard-coded ladder `VOLM = {6,8,…,30}` and `SETLEN = {5,6,7,13}`
(`.cs:97-98`) also match `run_we_w19.py:26-28` as recorded in the anatomy report §1.

## 3. Parameter-by-parameter — `WeeklyEdgeXMConflict_v2`

Certified = `c1_incumbent_anatomy.md` §2 (which enumerates the `.cs` defaults explicitly),
`FROZEN_INCUMBENT_20260827.md` §3, `WE_XM_PARITY_20260827/spec.yaml`.

| # | parameter | deployed default | NT8 read-back | certified value | |
|---|---|---|---|---|---|
| 1 | `EsInstrument` | `"ES 09-26"` | `"ES 09-26"` → **ESU6** | `ES 09-26`, fixed order | ✅ MATCH |
| 2 | `RtyInstrument` | `"RTY 09-26"` | `"RTY 09-26"` → **RTYU6** | `RTY 09-26` | ✅ MATCH |
| 3 | `YmInstrument` | `"YM 09-26"` | `"YM 09-26"` → **YMU6** | `YM 09-26` | ✅ MATCH |
| 4 | `AnchorHm` | 93100 | 93100 | 93100 | ✅ MATCH |
| 5 | `DecisionHm` | 94500 | 94500 | 94500 | ✅ MATCH |
| 6 | `ExitHm` | 154500 | 154500 | 154500 | ✅ MATCH |
| 7 | `SigmaLookback` | 60 | 60 | 60 | ✅ MATCH |
| 8 | `SigmaMinHist` | 20 | 20 | 20 | ✅ MATCH |
| 9 | `MaxStaleMinutes` | 3 | 3 | 3 | ✅ MATCH |
| 10 | `ForcedFlatMin` | 21 | 21 | 21 | ✅ MATCH |
| 11 | `CommissionRT` | 4.36 | 4.36 | 4.36 | ✅ MATCH |
| 12 | `DisasterStopPoints` | 0.0 | 0.0 | **0 = OFF** (§24, deliberate) | ✅ MATCH — see H3 |
| 13 | `Qty` | 1 | 1 | 1 | ✅ MATCH |
| 14 | `ExportDir` | `""` | `""` | `""` | ✅ MATCH |
| 15 | `Tag` | `"xm2"` | `"xm2"` | `"xm2"` | ✅ MATCH |
| 16 | `Calculate` | OnBarClose | OnBarClose | OnBarClose | ✅ MATCH |
| 17 | `IsExitOnSessionCloseStrategy` | false | — | false | ✅ MATCH |
| 18 | `BarsRequiredToTrade` | 20 | 20 | 20 | ✅ MATCH |

**18/18 MATCH. Zero diffs.** `DisasterStopPoints = 0` is the *certified* value — parity was
explicitly forbidden from choosing a stop (`spec.yaml:58`). It matches the record **and** it is a
live-risk hazard; those are two different statements and §5/H3 keeps them apart.

---

## 4. Environment deviations from the certified configuration (NOT parameter diffs)

The parameters are clean. The *environment* the certification was measured in is not fully
reproduced by the deployment, and three items should be recorded rather than assumed equivalent.

| item | certified | deployed | assessment |
|---|---|---|---|
| account | `Backtest` (isolated) | `DEMO8383477` (Simulation) | **Expected** — owner-authorized paper deployment |
| history loaded | `from 2022-01-03` (~4.6 yr) | **`DaysToLoad = 365`** | ⚠️ **E1 below** |
| trading hours | `CME US Index Futures ETH` | read-back `tradingHoursName: null` | ⚠️ **E2 below — UNVERIFIED** |
| commission | `NinjaTrader Brokerage Lifetime` | not exposed on the read-only surface | ⚠️ **E3 — UNVERIFIED** |

**E1 · `DaysToLoad = 365` is a shorter warm-up than the certified object was measured with.**
The certified record is emphatic that warm-up is part of the object
(`c1_incumbent_anatomy.md` §8.3 item 5: *"load from 2022-01-03; … gating the σ history on the study
window cost 4 trades"*). 365 days is comfortably enough for every stateful window to fill —
P1's σ (460 bars), tilt SMA-50, B-MOM slot history (60 sessions, band 14), range throttle
(200 kept / 60-median / ≥20 obs), quality quantiles (250 entries, min 100); XM's σ (60 sessions,
min 20). So this is **decaying and small** — the parity run measured exactly this class of effect
and found it symmetric, worth $27 across 123 trades, and gone by 2026 (`REPORT.md` §5a). But it is
a deviation: **the certified trade list was not produced under a 365-day warm-up**, and any
comparison of the paper run against the certified numbers must carry that tag rather than assume
equivalence.

**E2 · The trading-hours template is unverified, and every clock in both strategies depends on it.**
`ListAllStrategies` returned `tradingHoursName: null` for both. This matters more than it looks:
`sessionEndTs` comes from `sessIter.ActualSessionEnd`, and it drives **P1's** `blocked`
(`EntryBlockMin` 30) and `forceFlat` (`ForcedFlatMin` 21) plus the session reset that zeroes
`sessPnl`/`sessStopped`; and **XM's** `forceFlat` *and* its v2 `exitBarExists` guard — the single
functional change that earned v2 its certification. If the deployed instance resolved a template
other than `CME US Index Futures ETH` (e.g. `Default 24 x 7`), `IsFirstBarOfSession` /
`IsLastBarOfSession` / `ActualSessionEnd` all move, the session box never resets on the intended
boundary, and **v2's early-close guard silently stops matching the research object.** This cannot
be confirmed through the read-only surface. **Recommend the owner confirm the template on both
deployments before the 2026-09-01 shadow start.**

**E3 · Commission template not verifiable read-only.** Note also that P1's internal session box
charges a hard-coded `CommissionRT = 4.36`/contract regardless of what the account actually
charges, so the box's halt/target trigger points are unaffected by the account template — correct
and intended, but it means NT8's reported net and the internal box use different commission
figures. Not a defect; a reconciliation note.

---

## 5. Live-trading hazards, ranked

Verified absent from **both** files by grep: `OnOrderUpdate`, `OnExecutionUpdate`,
`OnPositionUpdate`, `ConnectionLossHandling`, `RealtimeErrorHandling`, `IsUnmanaged`,
`StartBehavior`, `SetStopLoss`, `SetProfitTarget`, and **any read of NT8's own `Position` /
`PositionAccount`**. The only match in either file is the `IsExitOnSessionCloseStrategy = false`
line itself. This single fact generates H1, H2 and H4.

### 🔴 H1 — CRITICAL · The internal fill ledger is never reconciled against reality

Both strategies keep their own ledger and **assume every submitted order fills at the next bar's
open**:

```csharp
// P1PCT_v1.cs:261-276
if (pendingAct == ACT_EXIT) { sessPnl += (Open[0] - myEntryPx) * PointValue - CommissionRT; myQty = 0; }
else if (pendingAct == ACT_ENTER) { myEntryPx = Open[0]; myQty = pendingSize; }
```

```csharp
// XMConflict_v2.cs:243-254 — same pattern on myPos / myEntryPx / realizedPnl
```

In the Strategy Analyzer this is exact, which is why parity certified. **In realtime it is an
unchecked assumption.** Nothing reads the actual execution. If an order is rejected, unfilled,
partially filled, or filled at a different price, the ledger diverges permanently and there is no
path back — no `OnExecutionUpdate` to correct it, no `Position.MarketPosition` cross-check, no
resync at session start.

Two concrete failure modes, both silent:

1. **Phantom long.** `EnterLong` is rejected (margin, connection blip, or `StartBehavior =
   WaitUntilFlat` holding submission during sync). `pendingAct` is already `ACT_ENTER`, so next bar
   `myQty = 1` regardless. The strategy now believes it holds a position it does not. It later
   issues `ExitLong` against nothing, NT8 ignores it, and **it books a fabricated `sessPnl` into the
   per-contract box** — which can trip `sessStopped` and disable the P1 sleeve for the rest of the
   session on P&L that never happened.
2. **Orphaned real position.** The exit is rejected or unfilled. `myQty` is zeroed anyway, so the
   strategy stops trying to exit, while the account is still long. Combined with H2 (no session-close
   safety net) the position rides indefinitely with no stop.

`StartBehavior: WaitUntilFlat` makes mode 1 materially more likely on any restart or reconnect than
it looks on paper. **This is the highest-severity finding in the audit** and it is invisible in
backtest by construction — the certification could not have caught it.

### 🟠 H2 — HIGH · `IsExitOnSessionCloseStrategy = false` on a 23-hour strategy removes the last safety net

Setting it false is the **correct and deliberate design** — the self-flatten at
`ForcedFlatMin = 21` before `ActualSessionEnd` is session-relative, which is precisely what avoids
the hardcoded-16:00 bug the repo lists as recurring (`XMConflict_v2.cs:56-59`). The parity run
confirms it works (`REPORT.md` §5b: 88 exits cluster on one bar at the 16:41/16:40 boundary).

The hazard is what it costs when the strategy is *not* running normally: **there is no
platform-level flatten.** The self-flatten only fires if `OnBarUpdate` executes. If the strategy is
disabled, errored, disconnected, or stalled while holding, NT8 will not close it at session close.
The position carries across the boundary — up to **2 NQ contracts** for P1, **1 NQ** for XM, and per
`EXECUTION_MANIFEST` §D max gross across both legs = 3 contracts.

Related, lower-severity: `sessionEndTs` is refreshed **only on `IsFirstBarOfSession`**
(`P1PCT_v1.cs:278-282`). If the 18:01 first bar is missed, `sessionEndTs` stays at the *previous*
session's end, making `blocked` and `forceFlat` true all day → P1 refuses to trade for the entire
session, and the session box never resets. This fails in the **safe** direction (no trades) but it
is a silent all-day outage with no alert.

### 🟠 H3 — HIGH · Neither strategy has any stop, and the two things that look like stops are not

- **P1 has no per-trade stop of any kind.** The `$1,300` `HaltDollars` is **not** a stop. It is a
  per-session *realized* budget, evaluated only when a trade closes (`.cs:269`, gated on
  `pendingAct == ACT_EXIT`). The anatomy report states this outright (§7 of the parity REPORT:
  *"A session box cannot truncate a trade mid-flight — `spnl` only accumulates when a trade
  closes"*). An open P1 position can run arbitrarily far against the account within a session. Its
  only truncations are the vote flipping off and the 21-minute clock. Mean hold ≈ 88 min, size up
  to 2.
- **XM's `DisasterStopPoints = 0` means OFF**, as certified. Recorded worst adverse excursion is
  **−$10,865 (543 points)**, and the file's own header labels that *"a SAMPLE MAXIMUM, NOT A
  BOUND"* (`.cs:31`). Mean hold ≈ 359 min with the clock as the sole risk control.
- **Even if the disaster stop were switched on, it is not a resting order.** It is evaluated at bar
  close and exits at the next bar's open (`.cs:329-338`). It offers no protection against a gap or a
  fast move, and none at all if the strategy stops receiving bars.

**Net: there is no protective order resting in the exchange book for either leg.** All risk control
is market-on-next-bar-open, conditional on the strategy process being alive and receiving data.
Raising `DisasterStopPoints` is an owner capital-risk decision the parity runs were explicitly
forbidden from making (`WE_XM_PARITY_20260827/spec.yaml:58`); this audit flags the exposure and
selects nothing.

### 🟡 H4 — MEDIUM · Stale / dead data series

**XM handles staleness well at the decision points and not at all after them.** `SeriesFresh()`
(3-minute tolerance) guards the anchor and the decision bar, and a stale secondary *disqualifies the
session* rather than forward-filling — this is genuinely good engineering and the parity run
confirmed it reproduces the reference's 6 disqualifications. But:

```csharp
// XMConflict_v2.cs:235
for (int i = 1; i < 4; i++) if (CurrentBars[i] < 1) return;
```

This early-return sits **above the exit logic**. If any one of ES/RTY/YM never produces a first bar
— a lapsed market-data subscription, an unavailable contract after a roll (see §6) — the entire
`OnBarUpdate` returns and **the exit path never runs**, coupling the ability to close an NQ position
to the health of three unrelated feeds. The strategy also does nothing at all, with no error and no
alert. Once a series has ≥ 1 bar `CurrentBars[i]` stays ≥ 1 even if the feed dies, so the stranding
window is narrow — but it is the *entry* path that then keeps evaluating on a dead feed, protected
only by `SeriesFresh`, which is not applied outside the anchor/decision bars.

**P1 has no staleness guard at all.** It is single-series so there is nothing to cross-check, but a
frozen NQ feed means `OnBarUpdate` simply stops firing: no forced flatten, no session box
evaluation, no exit. Same exposure as H2.

### 🟡 H5 — MEDIUM · Connection-loss behaviour was never chosen

Neither file sets `ConnectionLossHandling` or `RealtimeErrorHandling`, so both inherit whatever the
NT8 8.1.8.1 defaults are. That behaviour is **undeclared, untested, and unrecorded** in the parity
runs. It matters specifically because a recalculate-on-reconnect path re-runs `OnBarUpdate` over
historical bars and rebuilds `myQty`/`myPos` from scratch — which is precisely the H1 desync, now
triggered by an ordinary network event rather than a rejected order. Recommend the owner decide
these explicitly rather than inherit them.

---

## 6. The roll — the time-critical finding

### 6.1 The deployed months are correct **today**

`MarketInfo` per root, 2026-08-30:

| root | resolves to | deployed parameter | |
|---|---|---|---|
| NQ | **NQU6** | primary `NQ 09-26` | ✅ correct front month |
| ES | **ESU6** | `EsInstrument = "ES 09-26"` | ✅ correct front month |
| RTY | **RTYU6** | `RtyInstrument = "RTY 09-26"` | ✅ correct front month |
| YM | **YMU6** | `YmInstrument = "YM 09-26"` | ✅ correct front month |

All four match `FROZEN_INCUMBENT_20260827.md` §3 exactly, and NT8 confirms the live resolution.

### 6.2 The question is not "December" — the roll is **~11 days away**

**U6 (September 2026) expires Friday 2026-09-18** (third Friday; verified — September 2026 Fridays
are 4, 11, 18, 25). The CME equity-index roll is the Thursday eight days prior:
**Thursday 2026-09-10.** Volume migrates to **Z6 (December 2026)** then. The *December* roll into
March is 2026-12-18, a full quarter later; the exposure that matters is **the September→December
roll, inside two weeks**, and it lands directly on top of the 2026-09-01 shadow start.

The file states the design decision plainly (`XMConflict_v2.cs:66-69`):
*"set the four instrument parameters to the CURRENT front contracts … **There is no auto-roll here
by design** — an auto-roll that disagrees with the research substrate would be an unrecorded
parameter."* That is a defensible choice. Its consequence is that **the roll is a manual owner
action and nothing in the system will announce that it is due.**

### 6.3 What breaks, in order of when it happens

**(a) 2026-09-10 → 09-18 — the dangerous window: it trades on degrading data and no guard fires.**
U6 still prints bars, so `SeriesFresh` is satisfied and nothing disqualifies. But liquidity has
moved to Z6, so XM builds its cross-market composite from progressively thinner ES/RTY/YM U6
quotes while measuring NQ's drive on a thinning U6. The signal degrades **silently** — this is the
only window in which the system trades on bad data rather than simply stopping.

**(b) After 2026-09-18 — silent permanent shutdown (fail-safe).** U6 stops trading. The named
contracts still *resolve* in NT8 (expired instruments remain in the master list) but produce no new
bars. Then:
- **XM:** `SeriesFresh` computes `age = (nqTs - Times[i][0]).TotalMinutes` against
  `MaxStaleMinutes = 3`. With the secondaries frozen at expiry, age grows without bound →
  `fresh = false` → `sessionDisqualified = true` **every session, forever.** XM never trades again,
  with no error and no alert. **The staleness guard is what turns this from "trades a stale
  composite" into "stops" — it is doing exactly its job**, and it is the reason (b) is safe while
  (a) is not.
- **P1/PCT:** the primary `NQ 09-26` stops printing, so `OnBarUpdate` stops firing entirely. P1
  silently stops trading — and per H2/H4, if it were holding at that moment it could never exit
  through its own logic.

**(c) ⚠️ The instrument-verification guard does not check the month — a real defect.**
The guard exists specifically to prevent the W44 defect (a hardcoded instrument silently running
the stack on a deferred contract, −$24,269 vs +$8,326, cited at `.cs:39-43`). But:

```csharp
// XMConflict_v2.cs:183-186
string got = BarsArray[i].Instrument.FullName;              // e.g. "ESU6"
if (... || !got.StartsWith(want[i].Split(' ')[0], StringComparison.OrdinalIgnoreCase))
{ instrumentMismatch = true; break; }
```

`want[i].Split(' ')[0]` reduces `"ES 09-26"` to **`"ES"`**. `"ESZ6".StartsWith("ES")` is **true**.
**The contract month is never checked.** So if the primary is re-pointed to `NQ 12-26` while any of
`EsInstrument`/`RtyInstrument`/`YmInstrument` is left at `09-26` — or vice versa — the composite
silently mixes a December NQ against September secondaries and **`instrumentMismatch` stays false,
so orders are not blocked.** The guard that was written to prevent exactly this class of failure
will not catch it at the one moment it is most likely to occur: a partial manual roll. Note the
root check is still doing real work (it would catch ES↔RTY transposition); it is only the month
that is unverified.

**(d) Certification scope: rolling the contract invalidates the environment clause.**
Both parity specs pin `instrument: NQ 09-26 (resolves NQU6)` and
`secondary_order_fixed_in_State_Configure: ["ES 09-26","RTY 09-26","YM 09-26"]`, and
`FROZEN_INCUMBENT` §3 lists them as *"part of the freeze."* The deployment uses **explicit contract
months, not continuous back-adjusted symbols** — so there is no back-adjustment, and at the roll the
price level steps. Everything price-level-dependent in P1 restarts cold on the new contract:
ratchet anchors `mAnchor`/`mS`, σ (460-bar mean |Δclose|), the tilt SMA-50 of session closes, and
B-MOM's `open0930` slot history. That is the *safe* direction (cold restart, not corrupted state),
but it means **the certified parity numbers do not describe the post-roll instance** until
re-certified. Switching instead to a continuous `MergeBackAdjusted` symbol would change the
substrate and is a different, larger change — the spec requires all four series on the same
convention, and mixing is called out as silently corrupting the composite.

### 6.4 Recommended (owner actions — none taken here)

1. Decide and schedule the roll **before 2026-09-10**; it is not automatic and nothing will remind.
2. Roll **all four** instrument parameters together, or none — (c) means a partial roll is not
   detected.
3. Treat the post-roll instance as requiring re-verification against the certified record; the
   environment clause names `09-26`.
4. Confirm the trading-hours template (**E2**) at the same time.

---

## 7. Other strategies loaded or enabled anywhere — none

`ListAllStrategies(includeTerminal = true)` across every account:

| account | connection | strategyCount |
|---|---|---|
| Backtest | null | **0** |
| Playback101 | null | **0** |
| **Sim101** | Simulation | **0** ✅ |
| **2047681** | null | **0** ✅ |
| DEMO8383477 | Simulation | **2** (the two audited) |

**`count: 2` total.** Nothing stray is loaded or enabled on any account. Specifically:
**Sim101 is clean** (CLAUDE.md §1 names it explicitly), the numbered account **2047681 is clean and
has no connection**, and `Live` is **Disconnected**. The superseded `WeeklyEdgeXMConflict_v1`, the
comparator `WeeklyEdgeP1_v3`, and every other `.cs` in the workspace
(`WeeklyEdgeBmom_v1`, `WeeklyEdgeBookM11_v1`, `WeeklyEdgeP1_v1/v2`, `WeeklyEdgeX9a_v1`) are
**present as source but not loaded on any account.** ✅

Also clean: the earlier deployment pair referenced in `OWNER_DECISION_20260830.md:37`
(`dep_01b21182696c`, strategy id 399550058) is **no longer present** — no orphaned duplicate is
running alongside the current 399550060/399550061.

---

## 8. Summary

| area | result |
|---|---|
| P1/PCT parameters (29) | **0 diffs** |
| XM v2 parameters (18) | **0 diffs** |
| sha256, NT8 vs repo, both files | **identical**, and both match the spec-recorded prefixes |
| structural diffs vs certified predecessors | recomputed, exactly as documented |
| stray strategies on any account | **none**; Sim101 and 2047681 clean; Live disconnected |
| front months today | **correct** (NQU6/ESU6/RTYU6/YMU6) |
| environment deviations | 1 recorded (`DaysToLoad=365`), 2 unverified (hours template, commission) |
| live-trading hazards | **5**, led by the unreconciled internal ledger (H1) |
| time-critical | **September→December roll, roll date 2026-09-10 (~11 days)** |

**The configuration is correct. The exposure is in what the code does not do — it never checks
whether its orders actually filled, it has no stop, and it has no idea a roll is coming.**

*Audit performed read-only. No repo file modified; this document is the only file written. No git
command run. No order, enable, disable, deploy, stop, account, connection or backtest tool called.*
