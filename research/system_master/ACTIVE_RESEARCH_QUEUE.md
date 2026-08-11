# ACTIVE_RESEARCH_QUEUE

**Last updated:** 2026-08-10, post-structural-invariance master directive, wave 1. Rolling document
per master directive sec103/143-144 — re-ranked after every major result, not rewritten from
scratch. Queues: `ACTIVE` (currently running), `READY` (next up, nothing blocking), `BLOCKED`
(owner or evidence gated), `DEFERRED` (lower EVI, not started), `CLOSED` (done this wave).

---

## ACTIVE

*(none right now)*

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
*(nothing else currently ready — see CLOSED below)*

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
| P3 ACTIONMAP01 (Auction M5 action-value decomposition) | `CLOSED_NO_ACTION_MAPPING` (`db1cb92`). Key finding: Q_add(t) is mechanically identical to Q_hold(t), and Q_reduce(t) to −Q_hold(t), by construction — the per-contract markout formula has no size term, so no fill-level/marginal-contract data exists in this dataset to ever separate a 3-way add/hold/reduce decomposition. Only a univariate relationship (M5's own abs_value_dist_ticks → deterioration) can be tested, and it is: direction-robust (symmetric long/short, 100% leave-one-session-out sign-stable) but significance-fragile (fails removing the 3 most-influential of 36 discovery sessions, not significant in low-vol regime or the confirmation pool). Reversal is not economically attractive at H=1 (+0.84× the C1 cost hurdle, not significant) — evidence favors reduce/de-risk over reverse, if any mapping is ever built. **No policy spec was frozen — the SPEC/EXEC phases never ran** because the diagnostic itself found no stable separation to act on (correctly, per sec38/146: do not force a mapping the data can't support). Auction M5 remains a preserved, valid clean information state for future interaction with DOM/execution data (per sec146) — this closure is exactly the kind of information gap DOM collection is positioned to eventually fill (fill-level data would supply the missing size/marginal-contract dimension this task lacked). Protected pool: zero sessions opened. |

**P4 (Auction protected confirmation) does not proceed** — it was explicitly conditional on P3
passing (`ACTIVE_RESEARCH_QUEUE.md`'s own prior entry), and P3 found no stable mapping to confirm.

---

## Standing priority order (re-ranked after ACTIONMAP01's closure)

P0 governance (done) → P1 EQV04 (built, owner-gated on F5) → P2 B1 (built, owner-gated on F5) →
~~P3 ACTIONMAP01~~ (closed null) → ~~P4 Auction protected confirmation~~ (does not proceed, no
mapping to confirm) → P5 DOM operationalization (owner-gated on entitlement) → ~~P6 options/
dealer-state feasibility~~ (closed prior wave, DATA_LIMITED) → P7 cross-market EVI (no specific
mechanism identified yet) → P8 capital/portfolio science (nothing new to fold in yet) → P9
bounded new engine (only if new information supports it).

**Current honest state: every lane with concrete, ready synchronous work is either owner-gated
(P1/P2 on one F5 press, P5 on entitlement confirmation) or has no specific next action until new
evidence/a new mechanism appears (P7, P8).** This is not a stall — per master directive sec156-157,
a wave that closes false leads, ships governance infrastructure, and builds two owner-gated
executable objects without inventing busywork to fill idle lanes is a legitimate outcome, not a
gap. Two lanes (P1, P2) share the exact same physical unblock (one F5 press in NT8); a third (P5)
needs a separate, unrelated confirmation. Next synchronous work resumes once any of those three
owner actions happens, or once a genuinely new information class or mechanism is identified for
P7-P9.
