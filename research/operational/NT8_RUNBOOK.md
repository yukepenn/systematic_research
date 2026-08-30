# NT8 OPERATIONS RUNBOOK — the paper book on DEMO8383477

Evidence: `runs/G2_NT8_OPS_20260830/` (NT8_OPERATIONS_RULES.md — official-doc research;
STRATEGY_AUDIT.md — parameter/hazard audit). Written 2026-08-30, the day the book went to paper.

---

# 🔴 URGENT — CONTRACT ROLL BY 2026-09-10 (11 days)

> ## **VERIFIED, verbatim from NinjaTrader's own documentation:**
> ## *"NinjaScript strategies are not rolled forward and must be manually rolled over."*
> ([help guide: rolling over a futures contract](https://ninjatrader.com/support/helpGuides/nt8/rolling_over_a_futures_contrac.htm))

Nothing auto-rolls: not a strategy pinned to `NQ 09-26`, not one configured on the generic `NQ`
(the master resolves to an expiry **once**, at config time), not a chart-attached one. NT8's
"Rollover" feature (Tools → Database Management) rolls **chart/instrument labels and data
stitching only** — not strategies, not positions.

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

# STILL UNTESTED — do before leaving it unattended overnight

- **Does an account-hosted strategy survive an NT8 restart?** Undocumented. Test deliberately
  while flat, then write the answer here.
- Behaviour across a real connection drop (H5).
