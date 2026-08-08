# NEXT_HANDOFF — exact continuation state (2026-08-08, after wave-3 close / wave-4 launch)

_Written per V4.1 §0. If this session ends, the next invocation resumes HERE after the §4
repository-truth ritual. HEAD at write time: 547d2d4 (+ wave-3 results at 140f76c, all pushed)._

## In flight RIGHT NOW
1. **Wave-6 workflow** (`wf_3aad9fa9-e85`, script smv2-wave6-wf_3aad9fa9-e85.js): SMV2Y
   joint-loss/weekly-downside viability state test (seq 399-402), red-teamed. Spec frozen at
   51dbc45, unread. Genuinely new target (next-week portfolio downside / joint-loss status,
   not next-session Solar PnL) on 4 already-computed states (sigma460/ER150/flip-rate/VR).
2. **ES 1-minute export in flight** (job `6db86a69aac74f37`, `Tag=es1m_2022_2026`, writing to
   `Documents/NinjaTrader 8/out/es1m_2022_2026_1m.csv`). Once it lands: convert to
   `runs/SM1M_ES_SUBSTRATE/out/` parquet (mirror the SM1M NQ pattern exactly, incl.
   build_meta.json provenance), THEN launch RTY 1m and YM 1m the same way (sequentially, one
   NT8 job at a time — do not parallelize NT8 calls). This unblocks Engine-3 slate 4
   (cross-market lead-lag, 8 candidates already ranked in
   research/system_master/deep_research/DR_V4_EXPANSION_PASSES_20260808.md pass D1 + D2#1).
   IMPORTANT: NT8/CrossTrade tools are ORCHESTRATOR-ONLY — never delegate this step to a
   subagent (standing safety boundary; workflow agent prompts explicitly forbid it).
   Instrument-name convention for the other two: try "RTY 09-26" and "YM 09-26" first (same
   pattern as ES/NQ); if RunStrategyBacktest returns an instrument-not-found error, use
   ListNinjaScriptFiles/MarketInfo or CrossTrade's SearchNinjaScriptSymbols to find the exact
   resolved name before retrying — do not guess repeatedly.
3. Nothing else pending. 3m/1m NQ substrates committed (SM01/SM1M).

## On wave-4 completion (the standing loop)
1. Ingest exec + red-team results (journal.jsonl in the workflow transcript dir).
2. Registry rows 389-394 with results; docs: CURRENT_TRUTH, SCORECARD, SOLAR core answer to
   V4.1 §22 Q1-3 (clock verdict), ONE_CONTRACT/COMPLEMENTARY/INDICATOR frontier appends;
   fix any red-team prose issues IN the run REPORTs (annotated, never silently).
3. SMV2T PASS → champion-candidate core → master rebuild + parity spec (Stage 4) next wave.
   SMV2T FAIL → 13-member incumbent retained, lead closed.
4. Expansion passes → dedup vs registry/rejected lists → freeze engine slate 3 (max 3
   candidates) ONLY from mechanisms that fit the JL-state signature (low ER150 / high flip).
5. One-contract frontier stays PAUSED until an expansion pass yields a genuinely new discrete
   mechanism (2 families killed; per-instrument finals per owner addendum).
6. Commit + push after every block. Auto-chain the next wave; do NOT stop at close-out.

## Wave-4/5 close (folded into standing verdicts below): FAST-cohort lead CLOSED; ER150-damper
KILLED; 1m clock fails decisively; 5m bar-matched near-miss; **5m time-matched clock FAILED its
R2 confirmation** (SMV2W: gate A confidence 0.64/0.55<0.85, LOYO 3/5<4/5) — 3m incumbent
RETAINED, having now survived 5 independent core challenges (memory/cohort/MA/T2T3/clock).
**Engine-3 slate 3 (SMV2X) ALL KILLED** — 9/9 candidates across 3 slates now dead; NQ-only
3m-bar-horizon search space exhausted; cross-market export now in progress (see item 2 above).
Wave-6 (SMV2Y) tests a NEW target — joint-loss-week/weekly-downside prediction — not yet
attempted; this is the correct next axis per V4 s21, distinct from the 4x-killed
next-session-Solar-PnL target.

## Standing verdicts that bind future waves (do not relitigate)
- SM14 = ONE_CONTRACT_FINAL holder; challengers keep failing 0.85-confidence despite pointwise
  dominance — any new gate must be preregistered BEFORE seeing results; no gate shopping.
- Champion = DAYONLY_DUAL6040 via SolarWaveSMMaster_v2 (parity PASSED); executable headline
  net $177,315 / Sharpe 1.17 / maxDD −$18,894 dev; NT8 numbers are THE numbers.
- Killed (never revive without new mechanism): 6 reversion/rotation/calendar engines, 4 DSP
  states, T2/T3, MA confirmation, C-P7 policy, drought tilt, leverage adds (C-P3: P(2y
  DD>$25k)≥0.14 at current size).
- Solar core: 460 memory = plateau; SLOW cohort load-bearing; 40t floor irrelevant; 1200t cap
  binding (esp. 2026) = candidate state, not yet a spec.
- Smoothness lever = joint-loss weeks (50/230, −$159.6k, low-ER/high-flip signature).
- 2026 = path variation, not decay (r120 pctile 41st master); monitors MONITOR-01/SM13 rule.
- VIRGIN ≥2026-08-01 absolute. June/July 2026 CONSUMED. Dev ≤2026-05-31.
- Owner addendum: Product B finals are PER-INSTRUMENT (BEST_ONE_NQ + BEST_ONE_MNQ), live-ready-
  but-disabled, LIVE_READINESS_CHECKLIST.md gates activation, which is owner-only.

## Open V4.1 §22 questions not yet answered
Q1-3 (clock/MTF — wave-4), Q11 (engine-3 vs JL weeks — needs slate 3), Q13/Q14 (worst-month/
TUW improvement — no surviving lever yet except possibly no-FAST), Q15 (one-contract beyond
SM14 — paused), Q18 (next hypothesis — expansion passes), Q19 (smoothness Pareto — needs a
surviving overlay; all tested overlays died), Q20 (final product board — maturing).
