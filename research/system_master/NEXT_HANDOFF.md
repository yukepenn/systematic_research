# NEXT_HANDOFF — exact continuation state (2026-08-08, after wave-10 close / wave-11 launch)

_Written per V4.1 §0. If this session ends, the next invocation resumes HERE after the §4
repository-truth ritual. HEAD at write time: 2b2f88a (wave-11 specs frozen, pushed)._

## Owner pivot (2026-08-08, mid-session)
Owner flagged the smoothness/ML diagnostic run (waves 6-10) as having drifted from the actual
goal ("went too far? we only want best nq or mnq strategies") and directed a step-back:
investigate why 1-minute bars / non-90-179 params were abandoned (done, foreground Explore
agent, see wave-11 motivation below), then explicitly re-authorized full autonomous chaining
("我给你所有权限，不要问我问题了") with the standing goal restated: maximize risk-adjusted
growth (Sharpe/DD), single NQ/MNQ finals should be flat before 16:45 (already true for both
current deliverables), keep proposing genuinely NEW mechanism ideas (not just diagnostics),
"other indicators", "other bar intervals" explicitly invited. This supersedes the earlier
pause — resume auto-chaining per V4.1 §0, do NOT stop at close-out, do NOT ask before
launching the next wave unless genuinely blocked.

## In flight RIGHT NOW
1. **Wave-11 workflow** (`wf_dd749b21-786`, script smv2-wave11-wf_dd749b21-786.js), specs
   frozen at 2b2f88a before any read:
   - **SMV2AD_VOLMULT_CEILING** (seq 415-417): the 1200t/300pt upper clamp on the slowest
     member (VolMult=30) binds 39.2% of Jan-May 2026 bars vs 9.8%/0.2%/3.9%/18.3% in
     2022-2025 (SMV2R sub_381 clamp_audit.csv) — more binding NOW than any full historical
     year, never acted on. Tests ceiling sweep (1200/1600/2000/2400t) + extended slow cohort
     (VolMult 34-50, add-18 and replace-fastest-13 variants) + old-regime screen per
     candidate. R1_FAMILY_TEST — no adoption this wave; qualifying candidate → R2 spec next.
   - **SMV2AE_1MIN_RESCALE** (seq 418-419): SMV2U's 1-minute tests (both bar-matched and
     time-matched sigma windows) reused the 3m VMS=[6..30] constants and clamp bounds
     VERBATIM and both failed (friction 102-128% of gross). The one truly un-recalibrated
     axis — VolMult's point-scale itself (1m |dClose| not point-comparable to 3m |dClose|) —
     was never tested. Measures the actual empirical rescale ratio, re-tests with it. Screen
     gate only (Sharpe>0 AND friction<0.60); fail closes 1-minute definitively (2
     architectures × every calibration convention now exhausted).
   - **Mechanism-expansion research pass** (no spec, read-only): ranked list of genuinely new
     Solar-CORE (not Engine-3) adaptive-mechanism ideas analogous to what VolMult already
     proved works, explicitly deduped against rejected_ideas.md and every closed lead in
     CURRENT_TRUTH.md → `research/system_master/deep_research/DR_V4_SOLARCORE_EXPANSION_20260808.md`.
   Both numerical specs get independent red-team verification in the same workflow. On
   completion: ingest, correct any red-team-flagged issues in the run REPORTs (never spec.yaml),
   update registry (seq 415-419) + CURRENT_TRUTH/SCORECARD/FRONTIER docs, commit+push, then
   immediately freeze the next wave from whatever the expansion pass + SMV2AD/AE verdicts
   license (R2 confirmation spec(s) if any candidate qualified; otherwise the next-ranked
   expansion-pass idea). Auto-chain — do not stop at close-out.
2. **DONE**: ES/RTY/YM 1-minute cross-market context substrates all exported, verified, and
   committed (SM1M_ES/RTY/YM_SUBSTRATE, pushed at 3151800). Instrument names resolved cleanly
   as ESU6/RTYU6/YMU6. Engine-3 slate 4 (cross-market lead-lag, ranked candidates in
   research/system_master/deep_research/DR_V4_EXPANSION_PASSES_20260808.md pass D1 + D2#1) is
   now DATA-UNBLOCKED but has NO FROZEN SPEC YET — that is the next Engine-3 step whenever
   this or a future wave picks it up. NQ/MNQ remain the only traded instruments; ES/RTY/YM are
   read-only context (V4 §36).
3. Nothing else in flight besides wave-6 (item 1). 3m/1m NQ + 1m ES/RTY/YM substrates all
   committed (SM01/SM1M/SM1M_ES/SM1M_RTY/SM1M_YM).

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
