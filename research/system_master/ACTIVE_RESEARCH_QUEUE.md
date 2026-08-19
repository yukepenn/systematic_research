# ACTIVE_RESEARCH_QUEUE

**Last updated:** 2026-08-19 (engine-3 scout + LIQREV01 parked; wave alpha budget 2/2 exhausted).
Current READY queue for the NEXT wave, in order:
1. **CLOSEREV** (post-cash-close 16:00-16:14 pressure reversion — virgin window, scout rank 2;
   needs its own spec + the preregistered BBO slippage audit on the tick year). NOTE the
   2026-08-19 standing lesson: preregister a pre/post-2020 split CI as a PRIMARY gate.
2. **TOM-FLOW** (turn-of-month flow window — registry-distinct from killed seq 379; knife-edge
   power; same split-CI requirement).
3. **TERMFLOW** (repo's own DR_V4 designated next-step; weakest prior of the three).
4. Second literature-scout pass topics not yet mined; NDX-reconstitution waiver decision (owner).
Standing forward reads: MONITOR-01 #2 ≥2026-11-01 now carries TWO shadow constructions
(HTFDIR01 ARM_LONGONLY + LIQREV01) per `research/operational/MONITOR01_SHADOW_HTFDIR01.md`.
Blocked-on-one-owner-click: CrossTrade OAuth → confirmation-pool BBO archival resumes.

**2026-08-18 changes below retained:**
Changes vs the 2026-08-14 table below:
- Rank 2 (direction-conditioned HTF construction) — **DONE**: HTFDIR01 PASS-SCREEN on Product B
  with binding recency cautions / FAIL on Product A (`HTFDIR01_DIRECTIONAL_TILT/REPORT.md`).
  New READY item it spawns: **HTFDIR01 promotion step** (NT8 build + parity + full battery) —
  gated on its own preregistration AND owner go-ahead; recommended predecessor: owner-authorized
  candidate **shadow ledger at MONITOR-01 readings** (cheap forward evidence first).
- Rank 4 (second literature-scout pass) — now the top un-started READY item.
- Confirmed dead, do not re-queue: S-resampling (tested + CLOSED UNCONDITIONALLY by the Wave-18
  red team, seq 464-465 — the Wave-18 §7 "untouched surface" line was withdrawn there).
- OUTSIDE_VIEW's lever ranking (its §4) is the current cross-checked menu; its top actionable
  non-research item is OQ-4 (data-retention clocks) + running Product A at the $150k J-peak.

*(2026-08-14 queue below, retained; still accurate except as amended above.)*
Rolling document per master directive sec103/143-144 — re-ranked after every major result, not
rewritten from scratch. Queues: `ACTIVE` (currently running), `READY` (next up, nothing blocking),
`BLOCKED` (owner or evidence gated), `DEFERRED` (lower EVI, not started), `PAUSED` (owner
risk-control decision), `CLOSED` (done this wave).

## EVI-ranked non-DOM frontier (2026-08-14) — see `RESEARCH_FRONTIER.md` for full evidence per row

Explicitly excluded from ranking per owner instruction (not re-litigated): DOM/Market Replay
(`PAUSED`, see below), B1 historical tuning (frozen, calendar/protected-pool-gated only),
ACTIONMAP01 (`CLOSED_NO_ACTION_MAPPING`), U6B (`NOT_PROMOTED`), generic OHLCV feature mining
(8 independently-constructed feature families already show a consistent right-tail-unsafe-or-
too-small failure signature — diminishing EVI for more of the same kind of single-feature test).

| Rank | Item | EVI reasoning |
|---|---|---|
| 1 | HTF mechanism decomposition | Two independent methods (PLACEBO01 causal placebo, SIMPLE01 non-inferiority ladder) already flag HTF as the weakest-evidenced live component; `STRUCTURAL_INVARIANCE_MINIMUM_SYSTEM_SYNTHESIS.md` names it the explicit target for future work. Pure diagnostic, no new data, directly actionable. **DONE THIS WAVE — see `HTFMECH01_TILT_MECHANISM/`.** |
| 2 | Direction-conditioned HTF construction (future, separately preregistered) | HTFMECH01 sharpened the target further: HTF's cost concentrates on the short side (−$22,020 A / −$2,822 B), corroborated by SA0/PA0/PA1's independent long/short asymmetry findings. Real candidate for a future construction task — full gate battery required, not started here. |
| 3 | U9/U9B microstructure re-test at larger sample | Legitimate genuine order-flow (not OHLCV, not DOM/Replay) — closed null only for lack of statistical power (37+8 sessions). Gated on scalping_lab's tick/BBO history accumulating materially more sessions; ~6 calendar days have passed since closure, nowhere near enough. Not ready. |
| 4 | Second literature-scout pass (auction spillovers, intraday liquidity cycles) | Cheap, principled, hypothesis-first (not data-mining) — could surface a genuinely new, well-motivated mechanism. Untried topics per `FRONTIER_AUDIT_20260809.md`. Not started — lower urgency than 1-2, no specific candidate mechanism in hand yet. |
| 5 | Cross-market EVI review | Still no specific motivating mechanism (generic "ES predicts NQ" explicitly not authorized). Deferred until literature scout (rank 4) or another lead produces one. |
| 6 | Capital/portfolio science refresh | `CAPITAL_FRONTIER.md` current as of Wave 5; nothing new to fold in. |

---

## PAUSED (owner risk-control decision, 2026-08-12 — see `DOM_PAUSE_CLEANUP_20260812.md`)

| Item | Lane | Paused | Notes |
|---|---|---|---|
| DOM01 live collection | E | 2026-08-12 | Was `ACTIVE`; paused after a workstation resource-instability incident during heavy DOM/Replay work. Collector source now fail-closed (`DomCollectionEnabled=false` default) — will not record anything until explicitly re-enabled with recorded owner authorization. Raw captured CSVs (1.4 GB, never promoted past `ENGINEERING_BURNIN`) deleted; QC/storage-monitor tooling preserved for whenever this resumes. |
| DATA03 historical Market Replay acquisition (probe/batch plan) | E | 2026-08-12 | Was mid-planning (1 of 6 probe dates acquired: NQU6 2026-07-15, classified `GENUINE_NT8_MARKET_REPLAY_L1_PLUS_L2`, preserved). No further probing or batch acquisition until explicitly re-authorized — see `runs/DATA03_HISTORICAL_MARKET_REPLAY_INVENTORY/acquisition_plan.yaml`. |

## BLOCKED_OWNER

*(none right now)*

## READY (next up)

| Item | Lane | Why ready | Depends on |
|---|---|---|---|
| Direction-conditioned HTF construction (rank 2, see EVI table above) | A | HTFMECH01 sharpened the target with a real, corroborated mechanism (short-side concentration); diagnostic complete | Its own separate preregistration + full gate battery (chronology, tail-risk, right-tail-safety, NT8-executable proof) before any promotion — not started |
| Second literature-scout pass (rank 4) | F | Cheap, principled, could surface a genuinely new mechanism | Nothing — could start any time; lower urgency than rank 1-2 |

## DEFERRED (lower EVI this wave, not started)

| Item | Lane | Why deferred |
|---|---|---|
| Mechanistic cross-market EVI review | F | No specific mechanism currently identified as high-EVI (per sec71-73, generic "ES predicts NQ" is explicitly not authorized) |
| Capital/portfolio science refresh | G | `CAPITAL_FRONTIER.md` is current as of Wave 5; no new capital-relevant finding this wave to fold in yet |

## CLOSED this wave (2026-08-14, return to primary research program)

| Item | Verdict |
|---|---|
| HTFMECH01 (HTF marginal-contribution mechanism decomposition) | **Diagnostic complete, real finding, no promotion.** Whole-window totals reproduce PLACEBO01's certified figures exactly. Year decomposition: not uniform (2024 strongly positive for B). Side decomposition: strongly concentrated — HTF's up-weight mechanism is value-additive long, value-destructive short (Product A short-side cost −$22,020, 3.5× the whole-window net positive), corroborated by SA0/PA0/PA1's independent long/short asymmetry findings. Sharpens (does not resolve) the synthesis's own flagged HTF lead. See `HTFMECH01_TILT_MECHANISM/REPORT.md`. |

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

## CLOSED this wave (2026-08-11, scientific-preservation/prospective-setup pass)

| Item | Verdict |
|---|---|
| DOM01 collection-integrity QC monitor | Built (`runs/DOM01_LIQUIDITY_STATE/collector/qc/dom01_qc_monitor.py`), run clean against the live collection (0 FAIL, 1 descriptive WARN — heartbeat cadence outlier). Feed/collector integrity only, zero outcome computation. Also surfaced a genuine, appropriately-hedged feed-semantics finding (`EventTime` tracks `RecordedUtc` at a tight, consistent −4:00:00 offset despite `EventTimeKind=Unspecified`). |
| Canonical timezone-aware session-boundary utility | Built (`research_sdk/session_boundary.py`), 15/15 tests pass (DST spring/fall transitions, ordinary EST/EDT dates, the exact `LOCKED_FORWARD.md` boundary date, early-close session). Fixes the process-error class behind the EQV04 smoke-test near-miss — every future `RunStrategyBacktest`/data-read window can now be computed and mechanically asserted against `LOCKED_FORWARD.md` before any data is read, with no seasonal-offset branch for a caller to get wrong. |
| DOM01 prospective research protocol + data governance | Frozen and committed (`research/data_forward_sealed/DOM01/DOM01_PROSPECTIVE_PROTOCOL.md`, `DOM01_DATA_GOVERNANCE.md`) before any outcome analysis of DOM data. Exactly one mechanism frozen (DOM-M1: opposite-side depth withdrawal / adverse-selection quote-fade, conditional on the incumbent's own held direction) after reviewing Auction M5's surviving finding and ACTIONMAP01's identifiability failure; two other candidates explicitly reviewed and deferred. The one existing collector run is classified `ENGINEERING_BURNIN` (structurally inspected pre-freeze) and permanently excluded from discovery/confirmation tallies. Data stays `SEALED_FORWARD` even once readiness is met, pending explicit owner authorization. |
| Orientation-doc lint | `CURRENT_TRUTH.md` / `RESEARCH_HANDOFF.md` top snapshots predated this wave's EQV04/B1/ACTIONMAP01 closures and DOM01 going live — both updated (superseding sections prepended per each file's own convention, nothing rewritten/deleted). `MAP.md` checked, no DOM/EQV04/B1/ACTIONMAP01 references found stale (it doesn't track research status, only file layout) — left unchanged, no repo-wide cleanup campaign run. |

**Process note from this wave, worth remembering:** NT8 requires an explicit F5 *inside the
NinjaScript Editor* to rebuild the custom assembly after new files are added — a plain application
restart alone did not pick up 5 newly-written `.cs` files (confirmed directly: a backtest attempt
right after restart returned `strategy_class_not_found` listing only pre-existing objects in
`compiled_strategies`). `compile_engine=file_only` from `WriteNinjaScriptFile` is a real, load-bearing
signal here, not just a formality — verify by attempting to resolve the class, not by trusting a
restart alone.

---

## Standing priority order (re-ranked after EQV04/B1 closure)

> _Marker (2026-08-18): the "P5 DOM operationalization (ACTIVE — collecting)" line below and the
> 2026-08-11 "Current honest state" paragraph predate the 2026-08-12 DOM pause — the PAUSED table
> at the top of this file governs._

P0 governance (done) → ~~P1 EQV04~~ (PASS, closed) → ~~P2 B1~~ (implementation-certified, closed)
→ ~~P3 ACTIONMAP01~~ (closed null) → ~~P4 Auction protected confirmation~~ (does not proceed) →
**P5 DOM operationalization (ACTIVE — collecting)** → ~~P6 options/dealer-state feasibility~~
(closed prior wave) → P7 cross-market EVI (no specific mechanism identified yet) → P8
capital/portfolio science (nothing new to fold in yet) → P9 bounded new engine (only if new
information supports it).

**Current honest state (2026-08-11 pass): every owner-gated item from the prior wave is closed,
and the scientific-preservation lane requested this pass is also closed** — QC monitor built and
clean, the timezone-boundary error class fixed with tests, exactly one DOM mechanism frozen before
any outcome analysis, data governance frozen with a non-outcome readiness rule, orientation docs
delinted. DOM01 is the one active lane, genuinely collecting. Nothing was manufactured to stay
busy: no DOM alpha/outcome analysis ran, no historical B1/Auction/ACTIONMAP01 work was reopened,
no baseline changed. P7/P8/P9 remain correctly idle. The correct next state is **core frozen, B1
frozen, protected evidence untouched, DOM accumulating, prospective hypothesis committed, waiting
for independent evidence** — that is progress, not a stall, until either a QC-passed `SEALED_FORWARD`
batch is proposal-eligible per `DOM01_DATA_GOVERNANCE.md` sec3 AND the owner separately authorizes
opening it, or a genuinely new mechanism is identified elsewhere.
