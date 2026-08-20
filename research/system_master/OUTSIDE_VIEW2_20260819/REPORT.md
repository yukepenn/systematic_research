# OUTSIDE_VIEW2 — How persistent systematic winners actually win, and where our gap really is

_2026-08-19. Owner challenge: "So many people run systematic (non-HFT) strategies with
persistent Sharpe, even many day traders persist — it cannot be that we are stuck. Search
deeply from a third party view." Method: 6-agent workflow — 4 web-enabled research lanes
(winners anatomy / single-market edge census / day-trader base rates / self-benchmark) →
registry dedup audit → adversarial gatekeeper with citation spot-checks. All 7 load-bearing
citations verified verbatim against paper PDFs. Raw structured output:
`out/workflow_raw_output.json`. Zero alpha budget consumed (EXPLORATORY_DISCOVERY; no outcome
reads on our data)._

## 1. The verified anatomy of persistent systematic Sharpe

- **Professional per-stream edge is small.** Median GROSS Sharpe of a single-market,
  single-engine trend stream: **0.34** (Babu-Levine-Ooi-Pedersen-Stamelos, "Trends
  Everywhere", JOIM 2020, Table 2 — verified from PDF); AQR century average ~0.4/market
  (Hurst-Ooi-Pedersen); Carver (ex-AHL) budgets 0.40 pre-cost.
- **Headline Sharpe is manufactured by breadth.** Portfolio Sharpe = stream-Sharpe ×
  √(N/(1+(N−1)ρ)); measured ρ between per-market trend streams is 0.04-0.07 → a 3-4.5×
  multiplier. 0.34/stream × 50 markets reproduces the observed 1.17 almost exactly (verified
  Table 2/4). Style stacking (carry 0.78/class → 1.20 diversified; Koijen et al JFE 2018,
  verified) adds another ~1.2-1.5×. SG Trend Index realizes **~0.61 net since 2000** at
  industry scale. Multi-manager platforms (Millennium 330+ pods, Citadel) are hundreds of
  capped, netted streams plus leverage — not one big edge.
- **Vol targeting is second-order and fragile** (Moreira-Muir +25% in-sample, verified;
  Cederburg et al JFE 2020: real-time versions generally do NOT beat unmanaged). Execution
  engineering PRESERVES ~0.1-0.3 Sharpe; it does not create edge.
- **The only documented no-breadth route to Sharpe >2** is capacity-capped short-horizon
  trading (Medallion: ~$10B cap, ~12.5× leverage) — a different business requiring the data
  classes we do not own.

## 2. The day-trader premise, measured

- Brazil futures (Chague et al, verified): of 1,551 who persisted 300+ sessions, **97% lost
  money net**; ~0.5% earned above minimum wage.
- Taiwan complete-market record 1992-2006 (Barber-Lee-Liu-Odean JFM 2014, verified verbatim):
  **<1% of ~450,000 annual day traders predictably profit net**; the top ~0.1% earn 37.9
  bps/day net out-of-sample — the persistent minority is REAL but is a 1-in-100/200 tail,
  and its documented edges are specialization + information-asymmetry timing + cost
  structure, not generic signal breadth.
- Prop-firm funnel (FPFX 300k+ accounts, verified): ~7% of challenge buyers ever see a
  payout, averaging ~4% of nominal size. Regulator disclosures: 74-89% of retail CFD
  accounts lose.

## 3. Self-benchmark: are we under-extracting NQ?

**No — we are at or above professional per-stream extraction.** Raw dev Sharpe 1.05-1.18 per
object (portfolio ~1.26) is 2-4× the professional per-single-market band; even after an
industry-standard 50% selection haircut it sits at parity with the SG CTA realized 0.56-0.61.
(Our own stricter multiplicity accounting says selection-adjusted evidence ≈ 0 — the honest
resolution is forward reads, first one ≥2026-11-01.) The gap to "persistent 1.5-2" is not
per-market extraction quality; it is breadth we structurally do not have: engine portability
0-for-4 (W18 ES/RTY/YM), engine-3 construction 0-for-18, A/B losing-day correlation 0.88,
measured diversification benefit 0.0%.

## 4. Census × kill-record × gatekeeper: 24 documented edges, adjudicated

Dedup audit classified 20 shortlisted items against the registry (every evidence pointer
gate-verified; one cosmetic row-label correction). Gatekeeper verdicts: **7 KILL,
2 OWNER_DECISION, 0 FUND_ELIGIBLE.** Highlights:

| edge | status |
|---|---|
| Overnight drift / session split | KILL — seq-370 + B1-overnight power catch-22 (~334y needed at honest effect) |
| Slow TSMOM 1-12m single-market | KILL — the monetizable slot IS the deployed HTF tilt (SM08); MA-gate form killed |
| Vol-managed exposure | KILL — tail-adverse (ARM_C 49.4% top-1% retention); SMV2Y/Z exhausted |
| VIX slope / VRP timing | KILL — c01_t08 Bonferroni 0/3, Family E HOLD; "not harvestable on NQ-only" |
| FOMC/announcement (incl. even-week cycle) | KILL — C01 closed both directions; seq-397; calendar axis closed |
| TOM / month-end / OPEX-week | KILL — TOMFLOW01/seq-379/seq-398 one-shots |
| RSI(2)-type daily mean reversion | KILL — six fade families dead, unconditional form significantly INVERTED (t=−2.35) |
| Intraday momentum / MOC flow | KILL — MOM01 CLEAN_NULL; TERMFLOW01 t=−0.06 |
| COT / sentiment surveys / megacap-earnings drift | PROTOCOL_BLOCKED (pause) + power/decay-fatal per gate |
| **Dealer-gamma conditioning (GAMMA00)** | **OWNER_DECISION** — genuinely new data class, $80-199/mo unlocks; modal outcome still "decisive null" |
| **Index futures basis/carry** | **OWNER_DECISION** — genuinely virgin locally, but power-fatal as NQ-only timing; only sensible inside a deliberate cross-asset breadth expansion |

## 5. Strategic conclusion (gate-confirmed)

The owner's intuition is **correct about the industry, wrong about the mechanism**. Persistent
systematic winners do not out-extract us per market — their per-stream quality is BELOW our
dev numbers — they industrialize breadth. At breadth = 1 (one market, one engine family, one
data class), every professional shop would plateau exactly where we are. The next unit of
Sharpe therefore lives in, in order:
1. **Forward time** (free): MONITOR-01 #2 ≥2026-11-01 — settles where in [0, 1.18] the true
   per-stream quality sits, and adjudicates two shadow candidates.
2. **A new information class** (priced): GAMMA00 options data ($80-199/mo) — the record's
   own top unlock; DOM re-auth; CrossTrade renewal (BBO accrual → U9B).
3. **Breadth as a deliberate program decision** (owner mandate change): a multi-market
   trend/carry book at per-stream 0.3-0.4 × √N — the industry's actual Sharpe factory. Our
   Solar engine does not port (0-for-4); this would be standard-engine breadth, a NEW product
   line beside the NQ book, not a polish of it.
4. NOT: more OHLCV-substrate engine hunting on NQ (0-for-18, pool exhausted, paused), more
   tuning, stops, or calendar/indicator families (all adjudicated).
