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

## In flight (Wave 5) — updated 2026-09-06 after Wave-4 integration

Wave 4 DONE and integrated (G00079 PASS/FT0-licensed · G00080 FAIL/family-closed · G00081
DEFECT/not-cleared-at-debt-bar · G00082 NULL/facts-banked). ⭐ **ZBMACRO01 is on the FAST TRACK.**

Wave 5 (specs being frozen at this checkpoint):
- `runs/G3_ZBMACRO_FT_20260906` (G00083): FT0 freeze doc + FT1 independent reproduction +
  FT4 NinjaScript class WRITTEN OFFLINE (🔴 NOT copied into NT8 — a .cs copy rebuilds
  Custom.dll against the RUNNING live book; compile/Analyzer/parity happen at the 09-21
  window, precedent = the HD-23 offline certification) + FT10 owner packet draft.
- Falsifiers: post-FOMC sign-conditioned ZB drift (G00084) · close-hour hedging-flow momentum
  ES/RTY/YM vol-gated (G00085) · bond-index duration-extension day (G00086).

**Recovery rule:** unchanged.

## Standing duties every session

- ⏰ **Recreate the roll-quote cron** (4-hourly, through 2026-09-22): GetQuote on
  "NQ 09-26"/"NQ 12-26"/"MNQ 09-26"/"MNQ 12-26" → `research_sdk.quote_sampler.record` →
  commit. CME closed = skip silently. (Memory: roll-crossover-sampling-20260906.)
- Read `research/operational/CURRENT_LIVE_TRUTH.md` before anything NT8-adjacent. Live book:
  P1-only on `2047681`; roll guard blocks new entries from 09-08; redeploy ≥ 09-21 owner-only.
- Commit+push after every: spec freeze, ledger registration, wave integration, doc update.
  Verify `HEAD == origin/main` clean. Never leave results only in a session.
