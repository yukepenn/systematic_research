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

## In flight at checkpoint time (Wave 3)

Six preregistered runs executing (specs committed at `f952593`/`6409d79`; agents write into
their run dirs; partial `out/` may be present at any checkpoint):

| run | trial | done-marker to check |
|---|---|---|
| `runs/G3_AUCTCYCLE_20260906` | G00073 | out/gate_table.txt with final DECISION line |
| `runs/G3_ZNZB_SLOPE_20260906` | G00074 | same |
| `runs/G3_BASISMOM_20260906` | G00075 | same |
| `runs/G3_FTQGATE_20260906` | G00076 | same |
| `runs/G3_MEREBAL_20260906` | G00077 | same |
| `runs/G3_ZBMACRO_CLASSP_20260906` | G00078 | same |

**Recovery rule if the session died mid-wave:** for each run, if the final gate table +
decision exist → coordinator writes REPORT.md if missing (from artifacts, program-printed
tables only), records the ledger result, updates tracker/matrix, commits. If not complete →
re-execute that spec EXACTLY (specs are frozen; do not redesign). Never re-run a run whose
gate table already printed an evidence-window statistic if its spec is one-shot (only
CARRY_SIGC was one-shot; it is DONE and its windows are SPENT).

## Queue after Wave 3 (EVI order)

1. Integrate Wave-3 verdicts (ledger, tracker, matrix, FAILURE_MEMORY §28 blocks) → commit+push.
2. If G00078 = STACK-MEMBER → ZBMACRO01 engine construction + adversarial skeptic spec
   (then FT0-FT10 fast track only if it survives the skeptic).
3. World-scan card #2 (P1 passive-entry policy, Class-X): needs a BBO governance pre-check
   vs `runs/G2_WAVE5_CARDS_20260906/BBO_GOVERNANCE_MEMO.md` (NOTE: the memo lives THERE,
   not in research/genesis2/ — path drift found by the LIQREV pod) before any spec.
4. Next world-scan survivors by EVI (`survivors.json`, ranks 6+), re-screened against the
   freshest closures first.

## Standing duties every session

- ⏰ **Recreate the roll-quote cron** (4-hourly, through 2026-09-22): GetQuote on
  "NQ 09-26"/"NQ 12-26"/"MNQ 09-26"/"MNQ 12-26" → `research_sdk.quote_sampler.record` →
  commit. CME closed = skip silently. (Memory: roll-crossover-sampling-20260906.)
- Read `research/operational/CURRENT_LIVE_TRUTH.md` before anything NT8-adjacent. Live book:
  P1-only on `2047681`; roll guard blocks new entries from 09-08; redeploy ≥ 09-21 owner-only.
- Commit+push after every: spec freeze, ledger registration, wave integration, doc update.
  Verify `HEAD == origin/main` clean. Never leave results only in a session.
