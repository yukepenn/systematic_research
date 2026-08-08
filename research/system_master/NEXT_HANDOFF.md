# NEXT_HANDOFF — exact continuation state (2026-08-08, after wave-3 close / wave-4 launch)

_Written per V4.1 §0. If this session ends, the next invocation resumes HERE after the §4
repository-truth ritual. HEAD at write time: 547d2d4 (+ wave-3 results at 140f76c, all pushed)._

## In flight RIGHT NOW
1. **Wave-8 workflow** (`wf_2376b0d3-a7e`, script smv2-wave8-wf_2376b0d3-a7e.js): SMV2AA
   Solar/BMOM mix-shift diagnostic+policy (seq 406-409), red-teamed. Spec frozen at f6fb7d1,
   unread. Wave-7 (SMV2Z) completed CLEANLY and is fully ingested/pushed at 4eda9af: the
   blanket exposure-cut policy on the SMV2Y viability states FAILED DECISIVELY (CDaR got
   WORSE at every cell) because the flagged weeks hold 30.3% of TOTAL net PnL on 9.9% of days
   — they are high-VARIANCE weeks, not just high-downside weeks. SMV2AA tests a structurally
   different mechanism: reallocating WEIGHT between Solar/BMOM during flagged weeks (equal-vol
   basis, total risk stays on) instead of cutting total exposure. It has a MANDATORY
   prerequisite diagnostic (406, leg-asymmetry) with an explicit honest-stop path — if the two
   legs respond symmetrically to the flag, the policy cells (407-409) do not run at all, and
   that is a complete, valid, spec-compliant outcome, not partial work. If BOTH this and the
   three prior exposure-based attempts (SMV2N/V/Z) end up failing, smoothness-policy work on
   this diagnostic family should be considered exhausted pending a genuinely new mechanism —
   but every one of these attempts has produced real, honestly-reported information regardless.
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
