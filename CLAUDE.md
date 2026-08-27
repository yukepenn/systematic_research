# CLAUDE.md — agent bootstrap

**Active campaign: #7 `WEEKLY_EDGE`.** Rewritten 2026-08-27 from current truth. These rules
override default behaviour. Historical campaigns are archive; do not narrate them.

## 1. Hard safety boundary (never violate, no exception)

- **Research/backtest accounts only.** Never place, modify or cancel an order. Never enable, deploy
  or start a strategy. Never touch Sim101 or any real account. Never alter connections, credentials
  or licensing. Never modify the licensed RenkoKings vendor assembly.
- **No live enablement, ever, without an explicit recorded owner instruction.** "Executable" and
  "parity-certified" do **not** imply enabled.
- Never delete raw research evidence, erase failed experiments, rewrite historical results, or use
  locked-forward data for tuning.
- **No force-push. No history rewrites.** Never `git add -A` blindly.
- **DOM / Level-II / Market Replay collection is PAUSED** (owner risk-control, 2026-08-12).
  Do not resume without explicit recorded owner re-authorization —
  `research/system_master/DOM_PAUSE_CLEANUP_20260812.md`.

## 2. Read order

**Tier 0 (always):** `README.md` → this file → `research/weekly_edge/CURRENT_BASELINE.md`.
**Tier 1 (if the task needs it):** `research/operational/EXECUTION_MANIFEST.md`,
`ninjascript/LIVE_READINESS.md`, `INFORMATION_COVERAGE_*`, `DATA_CENSUS_*`, `LOCKED_FORWARD.md`,
`OPPORTUNITY_LANGUAGE.md`, `research/operational/OWNER_QUEUE.md`.
**Tier 2:** a specific `runs/<RUN_ID>/`. **Tier 3:** `research/archive/`.

**Do not recursively read Tier 2/3 to "understand the repo."**

## 3. Research truth vs execution truth — four baselines

Never collapse these. `CURRENT_BASELINE.md` §0 owns A and B; `EXECUTION_MANIFEST.md` owns C and D.

`RESEARCH_SINGLE` · `RESEARCH_PORTFOLIO_FRONTIER` · `EXECUTABLE_SINGLE` · `EXECUTABLE_PORTFOLIO`.

A baseline being empty does not erase the others. **EXECUTABLE · PARITY-CERTIFIED · LIVE-ENABLED
are three separate statuses.**

## 4. Method (non-negotiable — each rule was bought with a measured failure)

- **Spec first.** Every run gets `runs/<RUN_ID>/spec.yaml` **committed before results exist**.
  Never overwrite a run directory. Enforced by `research_sdk/prereg_guard.py`.
- **Decide the falsifier in advance**, code *every* clause of it, and print a
  GATE / SPEC / OBSERVED / PASS-FAIL table from the program — never assembled by hand.
- **Nulls must preserve dependence.** One shared draw per session across a family, circular shifts
  for time series, effective `K = K/(1+(K−1)ρ̄)`. Independent draws inside a correlated family give
  a bar that is far too high.
- **A class-conditional table requires its matched unconditional control in the same wave.**
- **Never redefine the population after seeing the result.** A gate that fails is recorded failed.
- **Every metric carries an evidence-status tag**: FORWARD / PRE-FROZEN / DISCOVERY_CONSUMED /
  DIRECTLY_BURNED / LEGACY_DIAGNOSTIC.
- **Never let leverage, sizing or a reduced risk denominator masquerade as information alpha.**
- Classify any improvement: NEW INFORMATION / MECHANISM-POLICY / REGIME ROUTING / DIVERSIFICATION /
  RISK SPECIFICATION / EXECUTION / LEVERAGE / SELECTION LUCK.
- `OPPORTUNITY_LANGUAGE.md` is **binding**: every ceiling figure names its level or is not quotable.
- **Old-regime failure is a RISK CLASSIFICATION, not a promotion veto** (owner doctrine, post-W115).

## 5. Data seals

- **≥ 2026-08-01 is VIRGIN.** Never touch it except through a scheduled read in
  `research/operational/MONITORING_CALENDAR.md`.
- **2026-05-31 → 2026-07-31 is BURNED.**
- Boundary math: `research_sdk/session_boundary.py`. Seal register:
  `research/operational/LOCKED_FORWARD.md`.

## 6. NinjaTrader / CrossTrade conventions

- **CrossTrade MCP can compile and backtest.** `GetMcpCapabilities` → add-on v1.13.9, NT8 8.1.8.1,
  `backtest_engine.available`. `RunStrategyBacktest` is the real Strategy Analyzer engine on the
  isolated **Backtest** account. **Never assert an action is "owner-only" without re-probing the
  tool surface today** — a stale capability claim cost this campaign a full day.
- Dropping a `.cs` into `Documents/NinjaTrader 8/bin/Custom/Strategies` is picked up without an F5.
  Verify by **resolving the class**, not by trusting a `compile_engine` flag.
- **Session boundary:** `to` = one second before the *next* 18:00 ET open. Never "end of day D".
- **Timestamps in payloads are exchange-session time (ET).** Sessions 18:00 → 17:00 ET.
- **Bars are END-stamped** in both the Python substrate and NT8. The bar stamped 09:31 opens at
  09:30:00. There is **no ±1-minute shift** — applying one *was* the original phase error (W52).
- Commission templates installed: `NinjaTrader Brokerage Free / Lifetime / Monthly`. Plain
  "NinjaTrader Brokerage" does not exist. Research uses **Lifetime, $4.36/ctrRT**.
- **Cost models differ.** Research charges commission **plus** a candidate-specific modelled spread
  (P1 $14.44, XM $12.50 per ctrRT); NT8 charges the template and zero slippage. **A research
  headline and an NT8 net are not the same quantity.**
- **Rename the class on every functional iteration** (`_v2`, `_v3`). NT8 may resolve a stale type,
  and deleting a `.cs` does not remove it from `NinjaTrader.Custom.dll`. **Never rename a class that
  has already been parity-certified.**
- Parity verdict bands (binding, from `WE_W52`): decision-series agreement **≥99 %** and trade
  counts within **2 %** = VALIDATED; 90–99 % = classify **every** mismatch; <90 % = not the object.
  **Compare decisions before dollars. Never tune until P&L matches.**

## 7. Repo and write discipline

- **Root stays minimal**: `README.md`, `CLAUDE.md`, `AGENTS.md`, `.gitignore` + the four directories.
  Do not add root docs. Do not create `*_FINAL2.md` / `*_NEW.md` / `*_LATEST.md`.
- **One authoritative source per fact, plus pointers.** Never five copies that can drift.
- `CURRENT_BASELINE.md` is a **state document, not a changelog.** Wave history belongs in
  `runs/WE_W*/REPORT.md`; the baseline links to them.
- **Atomic writes for any authoritative document**: build the full content in memory, encode to
  UTF-8 **before** opening the target, write bytes, verify non-empty, inspect `git diff`. Never
  truncate-then-write — that once zeroed `CURRENT_BASELINE.md`.
- Commit in coherent stages; push and verify `HEAD == origin/main` with a clean tree.

## 8. Where history lives

`research/archive/` — campaign #3 shipped baselines, campaign #1 reports, dated state snapshots,
retired handoffs. Closed campaigns also keep in-place state docs
(`research/CAMPAIGN_STATE.md` #1, `research/system_master/CURRENT_TRUTH.md` #3,
`research/scalping_lab/CAMPAIGN_STATE.md` #4, `research/original_trader_reconstruction/` #6).
**Those files say "current" about campaigns that have ended.** Only
`research/weekly_edge/` is live.
