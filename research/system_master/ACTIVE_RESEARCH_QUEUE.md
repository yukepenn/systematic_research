# ACTIVE_RESEARCH_QUEUE

**Last updated:** 2026-08-10, post-structural-invariance master directive, wave 1. Rolling document
per master directive sec103/143-144 — re-ranked after every major result, not rewritten from
scratch. Queues: `ACTIVE` (currently running), `READY` (next up, nothing blocking), `BLOCKED`
(owner or evidence gated), `DEFERRED` (lower EVI, not started), `CLOSED` (done this wave).

---

## ACTIVE

| Item | Lane | Started | Notes |
|---|---|---|---|
| ACTIONMAP01 (Auction M5 action-value decomposition) | C | 2026-08-10 | Background workflow: diagnostic → blind SPEC freeze → mechanical EXEC → synthesis. Runs entirely on consumed AUCTION04 data; opens no protected session. |

## BLOCKED_OWNER

| Item | Lane | Blocker | What unblocks it |
|---|---|---|---|
| EQV04 NT8 canonical parity (actual backtest comparison) | A | NT8 hasn't rebuilt `NinjaTrader.Custom.dll` — `WriteNinjaScriptFile` returned `compile_engine=file_only` for all 3 canonical objects | Owner presses F5 in NT8's NinjaScript Editor (or restarts NT8). Files already written, already compiled clean in-memory. |
| B1 NT8 implementation-parity check (vs. SIMPLE01's Python B1 candidate) | B | Same F5/restart blocker — B1's two `.cs` files are also `file_only` | Same owner action as EQV04 (can be done in one F5 press covering all 5 new files) |
| DOM01 live collection | E | Owner must confirm Level-II/Market Depth entitlement on the live data connection and attach the recorder to a chart | `runs/DOM01_LIQUIDITY_STATE/collector/DOM01_START_INSTRUCTIONS.md` — 5 steps, ~5 min, unchanged since Wave 5, still accurate as of this check |

## READY (next up once ACTIVE/BLOCKED clears)

| Item | Lane | Why ready | Depends on |
|---|---|---|---|
| EQV04 actual parity backtests (RunStrategyBacktest, incumbent vs canonical) | A | Code written, compiled clean; only needs the F5 step | Owner F5 |
| B1 implementation-parity backtest (NT8 B1 vs Python SIMPLE01 B1) | B | Code written, compiled clean; only needs the F5 step | Owner F5 |
| ACTIONMAP01 protected-pool power analysis + sequential protocol | C | Only if ACTIONMAP01's EXEC phase passes every consumed-data gate | ACTIONMAP01 completing with a PASS verdict (not assumed) |

## DEFERRED (lower EVI this wave, not started)

| Item | Lane | Why deferred |
|---|---|---|
| DOM data-quality monitor tooling (daily automated checks) | E | Collector isn't running yet (owner-gated) — building the monitor now would be speculative; revisit once DOM01 has ≥1 week of real data |
| Mechanistic cross-market EVI review | F | No specific mechanism currently identified as high-EVI (per sec71-73, generic "ES predicts NQ" is explicitly not authorized) |
| Capital/portfolio science refresh | G | `CAPITAL_FRONTIER.md` is current as of Wave 5; no new capital-relevant finding this wave to fold in yet |

## CLOSED prior wave, verified still current (no rework needed)

| Item | Verdict |
|---|---|
| GAMMA00 (options/dealer-gamma feasibility) | `DATA_LIMITED` — literature review complete, zero local SPX/NDX options data, purchase not authorized. Spun off MOM01. |
| MOM01 (Baltussen et al. intraday-momentum diagnostic) | `CLEAN_NULL` — does not replicate on NQ; redundant with existing substrate state. |

## CLOSED this wave (2026-08-10)

| Item | Verdict |
|---|---|
| P0 prereg_guard.py | Built, self-tested against real history, committed (`b6d688d`) |
| EQV04 canonical object construction | Built, compiled clean, committed (`89840f0`); actual parity test is `BLOCKED_OWNER` above |
| B1 frozen challenger construction | Built, compiled clean, committed (`12341ab`) |
| B1 future-confirmation spec | Frozen and committed BEFORE any future outcome read (`57e7078`) |

---

## Standing priority order (unchanged unless a result below re-ranks it)

P0 governance (done) → P1 EQV04 (built, owner-gated) → P2 B1 (built, owner-gated) → P3 ACTIONMAP01
(active) → P4 Auction protected confirmation (conditional on P3) → P5 DOM operationalization
(owner-gated) → P6 options/dealer-state feasibility → P7 cross-market EVI → P8 capital/portfolio
science → P9 bounded new engine (only if new information supports it).

Two lanes are simultaneously owner-gated on the exact same physical action (one F5 press in NT8),
so both EQV04 and B1's implementation-parity steps will very likely clear together the next time
the owner is at the NT8 desktop.
