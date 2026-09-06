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

## In flight (Wave 4) — updated 2026-09-06 after Wave-3 integration

Wave 3 DONE and integrated (G00073-77 FAIL recorded with §28 blocks; G00078 PASS/STACK-MEMBER).
Wave 4 executing (specs frozen; launch = workflow `genesis3-wave4`):

| run | trial | object |
|---|---|---|
| `runs/G3_ZBMACRO_ENGINE_20260906` | G00079 | engine construction + skeptic; DELAY CURVE decisive (08:46 entry is the executable claim) |
| `runs/G3_AUCTCONC_20260906` | G00080 | concession-short, frozen ERA-UNREAD, x2 mirror debt, portfolio rendering carries G2 |
| `runs/G3_RATESCARRY_20260906` | G00081 | outright ZN/ZB carry-timing; 97.5-pct debt bar; static arms; 2022-26 bear decisive |
| `runs/G3_XPASS01_PASSIVE_ENTRY_REPLAY_20260906` | G00082 | Class-X passive-entry replay (gov pre-check DONE: CLEAN-PATH-EXISTS, 104 sessions; design frozen sha 3689e279) |

⚠️ 2026-09-06 ~10:10 ET: the first Wave-4 launch was killed by the 5-hr session limit (3 of 4
agents died pre-output; entrypolicy completed and is integrated). Relaunched fresh as
`genesis3-wave4-relaunch`. Recovery cost: zero (checkpoint doctrine held).

**Recovery rule:** same as before — finished (final DECISION line in out/gate_table.txt) →
integrate + record ledger; unfinished → re-execute the frozen spec exactly.

## Standing duties every session

- ⏰ **Recreate the roll-quote cron** (4-hourly, through 2026-09-22): GetQuote on
  "NQ 09-26"/"NQ 12-26"/"MNQ 09-26"/"MNQ 12-26" → `research_sdk.quote_sampler.record` →
  commit. CME closed = skip silently. (Memory: roll-crossover-sampling-20260906.)
- Read `research/operational/CURRENT_LIVE_TRUTH.md` before anything NT8-adjacent. Live book:
  P1-only on `2047681`; roll guard blocks new entries from 09-08; redeploy ≥ 09-21 owner-only.
- Commit+push after every: spec freeze, ledger registration, wave integration, doc update.
  Verify `HEAD == origin/main` clean. Never leave results only in a session.
