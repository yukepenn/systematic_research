# NT8 OPERATIONS RUNBOOK — the paper book on DEMO8383477

Evidence: `runs/G2_NT8_OPS_20260830/` (NT8_OPERATIONS_RULES.md — official-doc research;
STRATEGY_AUDIT.md — parameter/hazard audit). Written 2026-08-30, the day the book went to paper.

---

# 🔴 URGENT — CONTRACT ROLL BY 2026-09-10 (11 days)

> ## **VERIFIED, verbatim from NinjaTrader's own documentation:**
> ## *"NinjaScript strategies are not rolled forward and must be manually rolled over."*
> ([help guide: rolling over a futures contract](https://ninjatrader.com/support/helpGuides/nt8/rolling_over_a_futures_contrac.htm))

Nothing auto-rolls: not a strategy pinned to `NQ 09-26`, not one configured on the generic `NQ`,
not a chart-attached one. NT8's "Rollover" feature (Tools → Database Management) rolls
**chart/instrument labels and data stitching only** — not strategies, not positions.

> ### ⭐ **"Would a restart re-resolve the front month?" — NO. Settled structurally, 2026-08-30.**
> The Help Guide is silent on this, so it was settled against this install's own database:
> **`Strategy2Instrument.Instrument` is an integer FOREIGN KEY into `Instruments`** — NT8 stores
> the *resolved contract*, not the selector text. The expiry is bound once at
> configuration-commit time and frozen. **A disable/re-enable does not re-resolve. An NT8 restart
> does not re-resolve.**
> ⇒ **The roll is a RECONFIGURE, not a restart.** (`runs/G2_LIVE_HARDENING_20260830/R1_ROLLOVER.md`)

- **NQ 09-26 expires Friday 2026-09-18**; volume rolls to 12-26 around **Thursday 2026-09-10**.
- **The danger window is 09-10 → 09-18**: U6 still prints, so **no guard fires**, while liquidity
  drains to Z6. The book would trade on degrading data and nothing would announce it.
- After expiry it fails *safe*: XM's freshness check disqualifies every session; P1 stops
  receiving bars.

## 🐛 THE DEFECT THAT MAKES A PARTIAL ROLL DANGEROUS (found 2026-08-30, in a certified file)

`WeeklyEdgeXMConflict_v2.cs`'s instrument-verification guard — the one written specifically to
prevent trading a silently-wrong composite — compares only `want[i].Split(' ')[0]`. That reduces
`"ES 09-26"` to `"ES"`, and **`"ESZ6".StartsWith("ES")` is true**, so **the contract MONTH is
never checked**. Roll NQ to December while leaving ES/RTY/YM on September and the guard stays
`false`: the strategy would trade **December NQ against September secondaries** and report itself
healthy. This is the exact defect class the guard exists to prevent.

⛔ The file is **parity-certified and must not be edited** (a fix requires a new class + its own
re-certification). The operational control replaces it:

## ROLL PROCEDURE — all four instruments together, never partially

1. Before 2026-09-10, confirm the roll date in **Tools → Instruments → NQ** (NT8 stores a
   per-contract roll date; do not rely on the 8-day convention alone).
2. Verify the account is **FLAT** (`GetPosition` / Control Center). If not, wait for the
   strategies' own exits — do not hand-flatten a strategy position (see hazard H1).
3. **Stop both strategies** (`StopStrategy`), confirm 0 running.
4. Redeploy **both** with `DaysToLoad = 365`:
   - P1 on **NQ 12-26**
   - XM on **NQ 12-26** with parameters `EsInstrument="ES 12-26"`, `RtyInstrument="RTY 12-26"`,
     `YmInstrument="YM 12-26"` — **all three must be passed explicitly; the defaults are 09-26.**
5. Verify: state Realtime, `instruments` list shows **NQZ6/ESZ6/RTYZ6/YMZ6**, warm-up bars
   ≈350k, account flat, `ordersCount 0`.
6. Record the swap in `PAPER_DEPLOYMENT_20260830.md`.

---

# HAZARDS IN THE CERTIFIED FILES (recorded, not fixable without re-certification)

**H1 — CRITICAL: the internal ledger is never reconciled with actual fills.** Both engines
*assume* every order fills at the next bar's open and update `myQty` / `myPos` / `sessPnl` on that
assumption. Exact in a backtest; **unchecked in realtime**. A rejected entry still sets
`myQty = 1` → phantom position → fabricated `sessPnl` booked into the per-contract box →
`sessStopped` can disable the P1 sleeve on P&L that never happened. A rejected exit orphans a
real position. Neither file implements `OnOrderUpdate`, `OnExecutionUpdate`, or `OnPositionUpdate`,
and neither ever reads NT8's own `Position`. **A backtest could not have caught this.**
*Mitigations:* keep `StartBehavior = WaitUntilFlat` (current); **be flat before any NT8 restart**;
compare strategy position vs account position at each daily shadow-runner check.

**H2 — HIGH: no platform-level flatten.** `IsExitOnSessionCloseStrategy = false` is the *correct*
design (session-relative self-flatten avoids a hardcoded-16:00 bug), but if a strategy is
disabled, errors, or stalls while holding, **nothing flattens it**. Up to 3 contracts gross.

**H3 — HIGH: no stop on either leg.** P1's −$1,300 box accumulates only *closed* P&L — it cannot
truncate a trade mid-flight. XM's `DisasterStopPoints = 0` (OFF) is the certified value. Measured
worst intrabar excursion: **196.25 pts/contract**; recorded worst XM excursion −$10,865 (543 pts).

**H4 — MEDIUM: XM's staleness gate sits above its exit logic**, coupling the NQ exit to three
unrelated feeds. **H5 — MEDIUM: connection-loss behaviour is inherited and untested**
(`ConnectionLossHandling` defaults to `Recalculate`, which re-triggers H1).

---

# BACKTEST ≠ LIVE — five divergences measured 2026-08-30 (none previously recorded anywhere)

Source: `runs/G2_LIVE_HARDENING_20260830/R3_DIVERGENCE.md`. These are **properties of the objects**,
not defects to fix, and they bound how much the paper/shadow stream can be expected to match the
backtest.

| # | finding | why it matters |
|---|---|---|
| **N1** | **XM's cross-market composite is deterministic in backtest and a millisecond RACE in realtime.** Full-lag case moves **13.80% of sessions**; a 50/50 race moves 7.79% and opens a **34.4%-of-net** p5–p95 band | XM's live results can differ from its backtest by a third of net **without anything being broken**. Do not read a forward XM divergence as decay until this band is accounted for |
| **N2** | `OrderFillResolution.High` on multi-instrument XM returns **zero trades with no error** — a silent null backtest | never use High fill on XM; a "no trades" result there means nothing |
| **N3** | P1's decision is **delta-gate-pivotal on 9.4% of bars**, and that gate is a pure function of `Volume[0]` — the one input NT8 documents as differing between the realtime stream and the historical store | a structural source of live/backtest drift on ~1 bar in 10 |
| **N4** | **P1's ratchet state has no resynchronisation point — ever.** Not at session end, not at day end. Once live and backtest separate by a single bar close, they never re-converge | forward tracking error is expected to grow, not revert. Judge P1 forward on economics, never on "does it match the backtest path" |
| **N5** | Every documented NT8 remedy is unavailable here: High fill silently broken (N2), Tick Replay not settable via our tool surface and documented as not-for-strategy-backtests, Playback requires closing other connections (would stop the paper book) on Market-Replay data whose collection is owner-PAUSED | there is no way to make the backtest tick-accurate for these objects. Accept the band; do not chase it |

**One clean negative result:** the most likely silent certification error — whether the Analyzer
feeds the primary handler a *lagged* secondary bar — was tested and is **clean**.

# RESOLVED EMPIRICALLY (open questions closed 2026-08-30)

| question | answer |
|---|---|
| Are deployed params the certified ones? | **Yes — P1 29/29, XM 18/18, sha256 match repo** (`ee4c765b…`, `2ec00dd4…`) |
| Is the trading-hours template right despite `tradingHoursName: null`? | **Yes.** NT8's stored default for NQ/ES/RTY/YM **is** `CME US Index Futures ETH`; bar density (~1,282/session) confirms a 23-hour session, not RTH |
| Did the 365-day warm-up actually fill the rolling windows? | **Yes.** Matching the deployed warm-up P&L against the backtest dates the lookback: **P1 back to 2025-08-06 = 467 entries** (250-window full), **XM back to 2025-10-13 ≈ 220 sessions** (60-session sigma full) |
| Is the $70,585 / $43,705 real money? | **No — virtual warm-up P&L.** Historical bars run through `OnBarUpdate` but produce no account transactions; `ordersCount 0`, shadow-runner watermarks unchanged |

---

# MANUAL BACKTESTING — the rules that actually bite

1. **Strategy Analyzer IGNORES `DaysToLoad`.** It uses only its own Start/End dates and has **no
   warm-up setting**. ⇒ **Set the Start date at least ONE YEAR before the period you care about
   and discard that head.** P1 needs 250 prior entries (~7 months) for quality sizing; the
   certified protocol warms from **2022-01-03**.
   *This is not theoretical: a run started 2026-01 produced **+$15,115** for Jan–Jul where the
   correctly-warmed run produced **+$41,576**. The number was discarded before it was quoted.*
2. ⚠️ **`Maximum bars look back = 256`** (Analyzer default in some configs) can silently truncate
   long windows — set it to `Infinite` for these strategies.
3. Backtest evaluates **at bar close**; realtime is tick-by-tick. Same `Calculate.OnBarClose`
   setting, but fills differ in nature.
4. For the whole book in one run use **`WeeklyEdgeBookM11_v1`** (`EnableP1`/`EnableXM` toggles).
   Its leg-isolation was verified row-identical to both certified files. **Only TOTALS are
   comparable** — netting re-cuts every per-trade statistic.

# 🔴 ANSWERED THE HARD WAY 2026-08-30: **STRATEGIES DO NOT SURVIVE AN NT8 RESTART**

The owner restarted NT8 at ~09:4x ET. Immediately afterwards:

```
ListDeployedStrategies(DEMO8383477) -> total: 0
ListStrategies(DEMO8383477, includeTerminal=true) -> count: 0
```

**Both NT8's own strategy list AND the CrossTrade deployment registry were empty.** Neither NT8
restored the account-hosted strategies nor did the add-on replay them. This matches the disk probe
(`runs/G2_LIVE_HARDENING_20260830/R5_PERSISTENCE_PROBE.md`): the strategy names appear in **no**
workspace/config file, and the add-on registry is in-memory.

## What this means operationally — it is the single biggest availability risk

**Any NT8 restart — crash, Windows update, power event, or a deliberate one — silently stops the
book. Nothing announces it. Any open position is left with no manager** (and neither strategy has
a stop). The strategies were redeployed manually (`dep_68588bacd445` P1, `dep_7f22307847c2` XM,
both verified Realtime/flat, warm-up identical: 352,670 bars, $70,585 / $43,705).

## Standing rules that follow

1. **After ANY NT8 restart, redeploy both legs with `DaysToLoad = 365` and verify** — the shadow
   runner does not do this and cannot detect it.
2. **Be flat before any deliberate restart.**
3. A **daily availability check** belongs in the routine: `ListDeployedStrategies` must show two
   Realtime deployments. A silent zero is the failure mode to watch for.
4. This is an argument for eventually attaching the strategies via the NT8 UI (which persists in
   a saved workspace) rather than programmatically — **untested**, and a separate decision.

# STILL UNTESTED

- Behaviour across a real connection drop (H5) — inherited platform default, unverified.
