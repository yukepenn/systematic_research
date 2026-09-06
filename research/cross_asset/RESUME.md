# GENESIS III — RESUME (session-resilience state, per directive §34)

**Purpose:** any fresh session (model switch, 5-hr limit, crash) reconstructs the campaign from
THIS file + HEAD and continues without loss. Workflow/task IDs are session-local — never wait on
them from a new session; recover from the committed run artifacts instead.

**Updated: 2026-09-06 ~09:20 ET (checkpoint while Wave 3 in flight). Update on every wave
integration; every update is committed and pushed immediately (owner checkpoint doctrine
2026-09-06: commit+push at every meaningful node so a killed session loses nothing).**

## Where the campaign stands

- Charter + results: `CAMPAIGN_STATE.md` (GENESIS III tracker at bottom) ·
  `REPRESENTATION_COVERAGE_MATRIX.md` · `MICRO_SURFACE_CENSUS.md` ·
  world scan slate `runs/G3_WORLDSCAN_20260906/out/{survivors,killed,raw_cards}.json`.
- Ledger: `research/genesis/SEARCH_LEDGER.jsonl` — trials through **G00078**; G00066-72 recorded
  (see CAMPAIGN_STATE tracker for verdicts); **G00073-78 registered, results pending Wave 3.**
- ⭐ Standing survivor: **ZBMACRO01** (G00072 PASS/selected) — engine candidate, Class-P
  pre-read = G00078.

## CAMPAIGN STATE: CONSOLIDATION (updated 2026-09-06 after Wave 7)

**Waves 1-7 complete and integrated. Ledger G00066-94 all recorded. No workflow in flight.**
The consolidated §33 print lives at the bottom of `CAMPAIGN_STATE.md`.

- ⭐ ZBMACRO01 = READY-FOR-09-21-WINDOW (`runs/G3_ZBMACRO_FT_20260906/DEPLOYMENT_PACKET.md`).
- The $0 frontier exhaustion is now SCOPED by `REPRESENTATION_COVERAGE_MATRIX.md` (the §16
  conditions are met and documented, not asserted).
- Remaining EV: the 09-21 window (owner-present) · roll-quote sampling (cron, through 09-22) ·
  forward-accrual reads (ZBMACRO monitor, RATESCARRY revival) · owner-gated data spends ·
  epsilon tail only on owner request.

**A fresh session:** read this file + the CAMPAIGN_STATE.md print + CURRENT_LIVE_TRUTH.md;
recreate the roll cron; no research work is owed unless the owner directs or the 09-21 window
opens.

## Standing duties every session

- ⏰ **Recreate the roll-quote cron** (4-hourly, through 2026-09-22): GetQuote on
  "NQ 09-26"/"NQ 12-26"/"MNQ 09-26"/"MNQ 12-26" → `research_sdk.quote_sampler.record` →
  commit. CME closed = skip silently. (Memory: roll-crossover-sampling-20260906.)
- Read `research/operational/CURRENT_LIVE_TRUTH.md` before anything NT8-adjacent. Live book:
  P1-only on `2047681`; roll guard blocks new entries from 09-08; redeploy ≥ 09-21 owner-only.
- Commit+push after every: spec freeze, ledger registration, wave integration, doc update.
  Verify `HEAD == origin/main` clean. Never leave results only in a session.
