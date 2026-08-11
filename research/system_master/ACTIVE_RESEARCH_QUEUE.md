# ACTIVE_RESEARCH_QUEUE

**Last updated:** 2026-08-11. Rolling document per master directive sec103/143-144 — re-ranked
after every major result, not rewritten from scratch. Queues: `ACTIVE` (currently running),
`READY` (next up, nothing blocking), `BLOCKED` (owner or evidence gated), `DEFERRED` (lower EVI,
not started), `CLOSED` (done this wave).

---

## ACTIVE

| Item | Lane | Started | Notes |
|---|---|---|---|
| DOM01 live collection | E | 2026-08-11 | Owner completed all 5 startup steps. Verified directly (not just owner report): `DataConnectionDisableL2Data=False`, `DataConnectionStatusAtInit=Connected` (via Tradovate, not Simulation), 17,000+ depth rows within the first minute, zero `FATAL_ERROR` events. Genuinely collecting real Level II data now. No completeness/quality checks run yet — per `DOM01_START_INSTRUCTIONS.md`, do not treat this data as research-usable until it passes the checks in `research/data_forward_sealed/DOM01/README.md`. |

## BLOCKED_OWNER

*(none right now — both prior F5-gated items closed this wave)*

## READY (next up)

| Item | Lane | Why ready | Depends on |
|---|---|---|---|
| DOM data-quality monitor tooling (daily automated checks) | E | Collector is now actually running — building the monitor is no longer speculative | Some accumulated collection history to validate the monitor against (a few days minimum) |

## DEFERRED (lower EVI this wave, not started)

| Item | Lane | Why deferred |
|---|---|---|
| Mechanistic cross-market EVI review | F | No specific mechanism currently identified as high-EVI (per sec71-73, generic "ES predicts NQ" is explicitly not authorized) |
| Capital/portfolio science refresh | G | `CAPITAL_FRONTIER.md` is current as of Wave 5; no new capital-relevant finding this wave to fold in yet |

## CLOSED prior wave, verified still current (no rework needed)

| Item | Verdict |
|---|---|
| GAMMA00 (options/dealer-gamma feasibility) | `DATA_LIMITED` — literature review complete, zero local SPX/NDX options data, purchase not authorized. Spun off MOM01. |
| MOM01 (Baltussen et al. intraday-momentum diagnostic) | `CLEAN_NULL` — does not replicate on NQ; redundant with existing substrate state. |

## CLOSED this wave (2026-08-10 to 2026-08-11)

| Item | Verdict |
|---|---|
| P0 prereg_guard.py | Built, self-tested against real history, committed (`b6d688d`) |
| P1 EQV04 (canonical object construction + NT8 executable parity) | **PASS, bit-identical.** Built+compiled (`89840f0`); owner F5 unblocked the actual NT8 backtest comparison (`0f2e09e` spec → `046961d` results). All three canonical/incumbent pairs match trades and net P&L to the cent on two windows; Product A additionally confirmed bit-identical bar-by-bar internal state across 165,861 bars, zero diffs. Closes the executable-level gap EQV01-03 left open. |
| P2 B1 (frozen challenger construction + NT8 implementation parity) | **Implementation-certified.** Built+compiled (`12341ab`), future-confirmation spec frozen before any outcome read (`57e7078`); NT8 parity run (`0f2e09e` spec → `046961d` results) confirms B1 diverges from the incumbent only and exactly where the one-line `mm`-forced-to-1.0 change predicts (identical fill index/date, both NQ and MNQ). Does not re-adjudicate B1's frozen historical verdict (still INCONCLUSIVE on Sharpe) or open protected/locked-forward data. |
| P3 ACTIONMAP01 (Auction M5 action-value decomposition) | `CLOSED_NO_ACTION_MAPPING` (`db1cb92`). Q_add(t)/Q_hold(t)/Q_reduce(t) are mechanically identical/negated by construction — no fill-level data exists to separate them. The one testable univariate relationship is direction-robust but significance-fragile. No policy spec frozen (SPEC/EXEC never ran — correctly, per sec38/146). Auction M5 preserved as a clean information state for future DOM/execution-data interaction. |

**P4 (Auction protected confirmation) does not proceed** — conditional on P3 passing; P3 found no
stable mapping to confirm.

**Process note from this wave, worth remembering:** NT8 requires an explicit F5 *inside the
NinjaScript Editor* to rebuild the custom assembly after new files are added — a plain application
restart alone did not pick up 5 newly-written `.cs` files (confirmed directly: a backtest attempt
right after restart returned `strategy_class_not_found` listing only pre-existing objects in
`compiled_strategies`). `compile_engine=file_only` from `WriteNinjaScriptFile` is a real, load-bearing
signal here, not just a formality — verify by attempting to resolve the class, not by trusting a
restart alone.

---

## Standing priority order (re-ranked after EQV04/B1 closure)

P0 governance (done) → ~~P1 EQV04~~ (PASS, closed) → ~~P2 B1~~ (implementation-certified, closed)
→ ~~P3 ACTIONMAP01~~ (closed null) → ~~P4 Auction protected confirmation~~ (does not proceed) →
**P5 DOM operationalization (ACTIVE — collecting)** → ~~P6 options/dealer-state feasibility~~
(closed prior wave) → P7 cross-market EVI (no specific mechanism identified yet) → P8
capital/portfolio science (nothing new to fold in yet) → P9 bounded new engine (only if new
information supports it).

**Current honest state: every owner-gated item from the prior wave is now closed.** DOM01 is the
one active lane, now genuinely collecting rather than blocked. P7/P8/P9 remain correctly idle —
no invented busywork — until a genuinely new mechanism or a few days of DOM data accumulate.
