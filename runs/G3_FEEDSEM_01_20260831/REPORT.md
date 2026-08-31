# G3_FEEDSEM_01 — what "Simulation" actually means on DEMO8383477

**Forensic run, 2026-08-31. READ-ONLY: no order, strategy, connection or setting was touched.**
Closes the open question recorded at `research/operational/GENESIS_III_OPEN_STATE.md:161,196`.

> **Headline.** The connection named "Simulation" is a **real NinjaTrader Brokerage (Tradovate)
> connection carrying real CME market data**. The account `DEMO8383477` is a **broker-side,
> server-hosted demo account**, and its fills are produced by a **server-side demo matching engine** —
> not by NinjaTrader's local Sim101 simulator, and not by CME. **Signal decisions are prospective on
> real data; fills and slippage are not market execution evidence.**

Two independent lines of evidence agree: primary machine forensics (adapter traces, config, logs, and
the feed itself) and NinjaTrader's own published documentation. Where they disagreed, the machine won
and **two of this run's own first-pass arguments were retracted** — see §2.

---

## 0. THE PROVIDER, NAMED

`Provider31` was never decoded in this repo. It is **Tradovate** — NinjaTrader Brokerage's execution
platform. Every order on `DEMO8383477` is handled by `Tradovate.Adapter`:

```
trace.20260831.00000.txt:44  (Simulation) Tradovate.Adapter.Submit0: count=1
trace.20260831.00000.txt:45  (Simulation) Tradovate.Adapter.Submit1: orderId='6a337c0de667450f9a36a26bcbae1a0f' account='DEMO8383477' ...
```

Adapter-class census of the whole day's trace: `Tradovate.Adapter` 229 lines, `Cbi.Account` 113,
`Cbi.AuthenticatedUser` 45. **Zero** NinjaTrader-internal simulator fill activity.

`Config.xml:11-12` ties the account to the brokerage identity — non-secret fields only:
`CachedUserId = 8383477` (⇒ `DEMO` + `8383477` = `DEMO8383477`), `CachedUserOrg = NTB`
(NinjaTrader Brokerage). *(Credential/token fields in that block exist and were not read or recorded;
see `out/config_excerpt_sanitized.txt`.)*

> ⚠️ **A premise in the directive is corrected.** NinjaTrader has **transitioned off Continuum**, and
> Continuum was **CQG**-powered, not Rithmic. The current stack is the **Tradovate**-derived
> NinjaTrader connection — which is exactly what the trace shows.

### The critical distinction the directive asked for, settled

| | connection | provider | status | what it is |
|---|---|---|---|---|
| **"Simulated Data Feed"** | locally defined, `Config.xml:20-35` | `Simulator` (15) | **Disconnected** | NT8's **synthetic price generator**. NinjaTrader documents it as *"a **random internally generated market** and has **NO correlation to real market data**"*, with a manual Trend slider. Its knobs are visible in our config: `TicksPerSecond=2`, `TimerMilliseconds=500` |
| **"Simulation"** | **not in `ConnectOptions` at all** — provisioned by the NTB login | `Provider31` (50) | **Connected**, user `rainazur` | **real Tradovate/NTB connection**. NT8's post-login **Trading Mode** dialog offers exactly *Live Trading* vs *Simulation*; NinjaTrader states the simulator *"streams real-time prices from the actual futures markets into your simulated account"* |

**These are different objects and only the second one feeds `DEMO8383477`.** The synthetic generator
is disconnected and plays no part.

A same-box control makes the separation cleaner still: `GetAccountSummary` shows **`Sim101` on the
very same `connectionName: "Simulation"` but with `provider: "Simulator"`**, while `DEMO8383477` on
that connection has `provider: "Provider31"`. One connection, two fill mechanisms — **the connection
name never determined the fill engine**, which is precisely the conflation that generated this question.

---

## 1. THREE-ROW VERDICT TABLE

| # | question | **verdict** | confidence | evidence |
|---|---|---|---|---|
| 1 | **MARKET DATA** | ✅ **REAL** — live CME L1 (trade + BBO) via Tradovate's real-time feed. **Not** synthetic. | **HIGH** | `MarketDataSubscribeResponse: instrument='NQU6' mode='RealTime'` (`trace.20260831:24`, +11 CME instruments); 5,156 NQU6 BBO samples with realistic microstructure (median spread 2.25 pt, median top-of-book size **2**, max 46 bid / 20 ask — `out/nqu6_bbo_depth_stats.json`); independent market-data WebSocket with heartbeats that drops separately from the trade socket (`trace.20260831:2` — `mdStatus='ConnectionLost'` while `tradeStatus='Connected'`); the synthetic "Simulated Data Feed" is **Disconnected** (`GetConnections`) and is documented as having *no correlation to real market data*. |
| 2 | **ORDER FILL** | ⚠️ **BROKER-SIDE SIMULATED** — a server-side demo matching engine. **Not** NT8's internal Sim101 engine; **not** a real CME match. | **HIGH** | *Off-machine, not NT8-local:* local GUID clOrdId replaced by a **server-assigned** numeric orderId after a 165 ms round trip (`trace.20260831:41→47,72`); server risk pipeline `Pending → RiskPassed → AtExecution` carrying `senderId:8383477`, `accountId:58110790`, `userSessionId:3136315196` (`:61-116`); only `Tradovate.Adapter` touches orders. Corroborated by NinjaTrader's KB: the Demo account is *"a **server-side** simulation account… hosted on NinjaTrader's servers rather than stored on your computer"*, explicitly contrasted with local Sim101. *Simulated, not matched:* **100 contracts filled in ONE execution at ONE price** — `cumQty:100, avgPx:29577.25, lastQty:100, lastPx:29577.25`, exactly **one** `ProcessFillEntity`, zero partial fills (`trace.20260818:402-418`), repeated 08-19 (100 @ 29749.75), against a book whose top-of-book size **never reached 100 in 5,156 samples** (P = 0.00 %); `"external": false` on both order and fill entities; execution ids are **random floats** (`"name":"1.7000283115486512"`, `"externalClOrdId":"0.4710442344600391"`), not exchange-assigned; server decision-to-fill = **3 ms** (04:58:00.390Z → .393Z). |
| 3 | **SLIPPAGE EVIDENCE** | ⛔ **NOT market execution evidence.** Teaches us **nothing** about real broker or exchange fill quality. One sub-component (latency drift) *may* be partially real — **UNRESOLVED**, see §4. | **HIGH** on the prohibition; **UNRESOLVED** on the residual | The engine that priced these fills demonstrably supplies **unlimited liquidity at a single price** (row 2). An engine that fills 100 lots where 2 rest cannot inform queue position, depth, impact, partial fills or adverse selection. The one round trip's 2.25 pt figure is n=1, measured against the strategy's **bar-close** reference rather than the touch, in the thinnest hours. |

### Why the 100-lot fill is decisive, and why the obvious objection fails

CME documents that a marketable order is allocated against **individual resting orders**, and that
when *"the aggressing order quantity is greater than the entire resting quantity at a price level…
remaining aggressing unmatched quantity becomes a new bid/offer at the appropriate price level."*
So at a real match, 100 lots fill at **one price only if ≥100 contracts rested at that one level**.
Measured on this very feed, NQU6 top-of-book reached 100 in **0 of 5,156 samples** (max ever: 46).

**The objection** — *platforms often aggregate same-price fills into one report* — is real but does not
survive the numbers: `avgPx = lastPx = 29577.25`. Had the order swept levels, the average would differ
from the last. Aggregation could hide *how many* resting orders were hit; it cannot hide a **price
range**, and there is none. Verified directly: exactly one `ProcessFillEntity` for the order.

---

## 2. 🔴 THREE CORRECTIONS — including two to this run's own reasoning

### 2.1 A repo claim is wrong in mechanism (conclusion stands)

`research/operational/FORWARD_EVIDENCE_RECONCILIATION.md:86` currently reads:

> "…is a **SIMULATED fill on a demo account** — it measures **NT8's fill simulator**, not a broker."

**The conclusion is right; the mechanism is wrong**, and the error is consequential:

- NT8's local simulator controls (`SimulatorEnforcePartialFills`, `SimulatorEnforceImmediateFills`,
  `Config.xml:202-203`) are **inert for this account**. No local knob makes these fills more realistic.
- **The inversion worth noting:** NinjaTrader documents its *local* Sim101 engine as deliberately
  sophisticated — *"not a simple algorithm that fills your order once the market trades at your order
  price… includes ask/bid volume, trade volume, **time (to simulate order queue position)**, and random
  time delays"*. The **server-side demo engine that actually filled our orders showed none of that**
  (100 lots at one price, 3 ms). We are not merely using a simulator; we are using the **less realistic
  of the two simulators available on this machine**.
- Realism here is set by an engine we neither control nor can configure ⇒ better paper fills are
  **unavailable at any price on this account**; they require a funded account or an offline cost model.

### 2.2 ⚠️ RETRACTED: "Global simulation mode disabled" proves nothing

This run's first pass cited `IsGlobalSimulationMode=false` (`Config.xml:196`) and the log line
`Global simulation mode disabled` as evidence that NT8's internal engine was not interposed.
**That inference is withdrawn.** NinjaTrader documents Global Simulation Mode as an **order-entry
account-picker restriction**, not an order interceptor:

> "all order entry interfaces… will only allow **selection of a simulation account**… **Enabling this
> is not necessary in order to route orders through simulation**, because you can still set any order
> entry interface to the Sim101 account individually."

Routing is decided **per order, by the account selected**. So the flag says only that the UI was not
locked to sim accounts. **It is not a routing statement in either direction.** The ORDER FILL verdict
does not depend on it and is unchanged — it rests on the Tradovate network round trip and the 100-lot
fill.

### 2.3 ⚠️ RETRACTED AS A TELL: `Exchange=Default` / `exchange=Globex`

The trace reports `exchange=Globex` (`trace.20260831:191`) while the NT8 log prints `Exchange=Default`
for the **same** execution (`log.20260831.00000:8`). Documentation resolves the contradiction: the
NinjaScript `Execution` class has **no `Exchange` property at all**, and `Instrument.Exchange` is
documented only as *"the exchange which is selected for the current instrument"* — an **instrument
configuration attribute, not a fill-venue attribute**. (Community corroboration: an internally-filled
`Playback101` execution also prints `exchange=Default`.)

**Neither field is usable as routing evidence, in either direction.** `exchange=Globex` is *not*
proof the order reached Globex, and `Exchange=Default` is *not* proof it did not. Recorded here
because it is exactly the field a future reader would seize on.

---

## 3. WHAT FORWARD OBSERVATIONS ON THIS ACCOUNT MAY AND MAY NOT BE USED FOR

### ✅ MAY be used

- **Signal / decision evidence.** Decisions are computed on **real, live CME data** arriving
  prospectively. A decision logged before its outcome is genuine forward evidence.
- **Direction, timing and entry/exit logic** — did the strategy fire when it should have.
- **Operational and engineering truth** — warm-up gates, roll plans, instrument binding, reconciliation,
  restart behaviour, connection-loss handling, ledger↔position agreement.
- **Gross P&L attributable to the price path**, understood as *"what the real market did between two
  timestamps"* — with the explicit caveat that both endpoint prices are simulator-chosen.

### ⛔ MAY NOT be used

- **Any broker or exchange fill-quality claim.** No slippage, spread cost, or transaction-cost figure
  from this account may be quoted as measured execution cost, or compared against the $14.44 / $12.50
  modelled spreads as though it were the same quantity.
- **Any capacity, size or scaling claim.** The engine filled 100 lots where 2 rest. This account
  cannot detect the size ceiling that `OQ-6` integer-contract mapping needs.
- **Queue position, partial fills, depth exhaustion, market impact, adverse selection on limit orders.**
  None are exhibited by the engine that filled us.
- **Net P&L as a live-readiness figure.** `realizedProfitLoss = 3201.28` is gross $3,210.00 minus
  $8.72 template commission on simulator-chosen prices — not what real money would have earned.
- **Stress behaviour.** No real reject, margin call, thin-book gap or venue outage has been exercised.

---

## 4. UNRESOLVED — and the exact observation that settles it

**UNRESOLVED: what reference price does the demo engine use for a market order?**

It matters because the ~165–300 ms between decision and fill is **genuine** network + server time, and
the real market genuinely moved during it. If the engine prices fills at the **real touch**, the
latency-drift-plus-spread component is real *for size at or below top-of-book* and is worth recording.
If it prices at **last** or **mid**, the paper stream systematically **understates** cost and no
slippage figure from it is usable even directionally.

Current data cannot decide it: the two round-trip fills are n = 1 each, and the trace happens to carry
no BBO samples at 00:58:00 or 03:51:00. The observed 1.00 pt and 1.25 pt adverse moves are *consistent*
with crossing a real 2.25 pt median spread — and equally consistent with 1 pt of drift.
**Suggestive, not evidence.** Note the documentation is silent here too: NinjaTrader publishes no
market-order pricing rule even for its own local engine, so this cannot be closed from docs.

> ### THE SETTLING OBSERVATION
> For each fill, capture the Tradovate BBO — `b`, `a`, `bs`, `as` — at the **same millisecond** as the
> fill, from the same `MarketDataReceive` stream that already carries it, and compare `lastPx` to the
> touch. **N ≥ 30 fills**, both directions, session-hour recorded.
> - Buys at `a` and sells at `b` ⇒ engine crosses the real spread; the latency+spread component is real
>   at top-of-book size and may be quoted **as such, with the size caveat**.
> - Fills at last / mid / anything inside the spread ⇒ the paper stream understates cost; **no**
>   slippage figure from this account is quotable, even directionally.
>
> Free, no new data, no owner authorization — a read of a stream already flowing.
> **Until it is done, treat every paper slippage number as unquotable.**

A deliberate depth probe is **not** proposed: it would place orders, which this run is forbidden from
doing and which the owner has not authorized. Note the decisive 100-lot evidence was **accidental** —
a leftover manual probe from 08-18/08-19, not a designed test.

---

## 5. EVIDENCE-CLASS RECOMMENDATION

Replace the `UNCLASSIFIED pending G3_FEEDSEM_01` row in
`research/operational/GENESIS_III_OPEN_STATE.md:161` with a **split** class — because the decision and
the fill on one and the same trade carry *different* evidential weight, and collapsing them is exactly
the error this run existed to prevent:

| object | recommended class | meaning |
|---|---|---|
| a **decision** on `DEMO8383477` | `FORWARD_DECISION_FIRST` *(unchanged)* | real data, prospective, decision logged before outcome |
| a **fill / price / slippage / P&L** on `DEMO8383477` | 🔴 **`SIMULATED_FILL_NON_EVIDENTIAL`** | server-side demo engine with unlimited liquidity at one price; **carries no execution-quality information at any N** |

**`SIMULATED_FILL_NON_EVIDENTIAL` is not a low-power class — it is a zero-information class.**
This distinction is load-bearing: `CLOSED-BY-POWER` invites "collect more sessions", and here more
sessions **cannot** help. Accumulating 500 paper fills from an infinite-liquidity engine yields 500
observations of the engine, not of the market. The class must be immune to the N-argument, in the same
way the campaign already ruled that macro surprise magnitude "cannot be moved with money".

Per the two standing rules in `ALPHA_EVIDENCE_CLASSIFICATION.md` — a composite object inherits the
shallowest evidence it depends on — **any forward P&L figure built on these fills inherits
`SIMULATED_FILL_NON_EVIDENTIAL`**, however real the decisions underneath it are.

---

## 6. ANSWERS TO THE THREE QUESTIONS, IN ONE LINE EACH

1. **Market data** — REAL live CME L1 via Tradovate; the synthetic "Simulated Data Feed" is disconnected.
2. **Order fill** — routed off-machine to a **server-side demo** engine; neither NT8-local Sim101 nor a
   real matching engine.
3. **Slippage evidence** — **nothing** about real fill quality; one residual sub-component is
   UNRESOLVED pending the §4 observation.

**The directive's own anticipated answer was very nearly right and is adopted, with one correction:**
signal decisions *are* prospective on real market data, and fills *are* simulator-generated and are
*not* market execution evidence — but the simulator is **the broker's server-side one, not
NinjaTrader's local one**.

---

## 7. ARTIFACTS (`out/`)

| file | what |
|---|---|
| `trace_20260831_entry_581992641240.txt` | full entry lifecycle: local GUID → Tradovate submit → server orderId → RiskPassed → AtExecution → ExecutionReport → Fill |
| `trace_20260831_exit_581992641251.txt` | exit lifecycle + `OnAddTrade profitCurrencyBeforeCommissionAndFees=3210` |
| `trace_20260818_100lot_581992641208.txt` | **the decisive artifact** — 100 contracts, one execution, one price, `avgPx = lastPx` |
| `nqu6_bbo_depth_stats.json` | 5,156 NQU6 BBO samples: spread and depth distribution, P(top-of-book ≥ 100) = 0.00 % |
| `log_20260831_roundtrip.txt` | NT8 log for the round trip incl. both `FILLPX assumed/actual` rows |
| `log_20260830_startup.txt` | connection establishment, HDS/IS servers *(note: its `Global simulation mode disabled` line is **not** evidence — §2.2)* |
| `trace_20260831_connection_evidence.txt` | market-data vs trade WebSocket lifecycle, `mode='RealTime'` subscriptions |
| `config_excerpt_sanitized.txt` | Config.xml non-secret fields; **all tokens redacted and never recorded** |
| `executions_record.txt` | consolidated execution record with server timestamps |

**Credential handling:** `Config.xml:5-18` contains encrypted token blobs. Their existence is recorded;
no value was read into any artifact or into this report.

---

## 8. DOCUMENTATION SOURCES

Primary verdicts rest on machine evidence; these corroborate and supplied §2.2/§2.3.

- Simulated Data Feed is synthetic — https://ninjatrader.com/support/helpGuides/nt8/simulated_data_feed_connection.htm
- Sim101 internal fill engine (queue position, latency, bid/ask volume) — https://ninjatrader.com/support/helpGuides/nt8/simulation.htm
- **Global Simulation Mode is a UI account-picker lock** — https://ninjatrader.com/support/helpGuides/nt8/global_simulation_mode.htm
- Routing is per-order by selected account — https://ninjatrader.com/support/helpGuides/nt8/trading_in_simulation.htm
- Live vs Simulation Trading Mode dialog — https://ninjatrader.com/support/helpGuides/nt8/trading-mode.htm
- Simulator streams real futures prices — https://ninjatrader.com/trading-platform/trading-simulator/
- **`Execution` class has no `Exchange` property** — https://ninjatrader.com/support/helpGuides/nt8/execution.htm
- `Instrument.Exchange` is instrument config — https://docs.ninjatrader.com/ninjascript/exchange
- Simulator settings (only 3; no slippage/latency knob in NT8) — https://ninjatrader.com/support/helpGuides/nt8/options_trading.htm
- Demo account is **server-side**, contrasted with local Sim101 — https://support.ninjatrader.com/eu/s/article/How-Can-I-Change-Balance-in-My-Demo-Account *(search-snippet verified; page does not render for a fetcher)*
- Sim101 is stored locally — https://support.ninjatrader.com/s/article/How-Can-I-Reset-My-Sim101-Account-in-NinjaTrader-Desktop *(snippet verified)*
- CME Globex matching / sweep behaviour — https://cmegroupclientsite.atlassian.net/wiki/display/EPICSANDBOX/CME+Globex+Matching+Algorithm+Steps
- NinjaTrader off Continuum (CQG-powered) — https://discourse.ninjatrader.com/t/transition-off-continuum/6147

**Not establishable from documentation** (hence §4 UNRESOLVED, and why the depth argument was settled
by measurement instead): market-order pricing rule; limit trade-through vs touch; whether any sim
engine models finite depth; adverse selection (never mentioned by NinjaTrader); published NQ
top-of-book size.
