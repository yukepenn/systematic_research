# NEXT_HANDOFF — exact continuation state (2026-08-08, after wave-12 close / wave-13 launch)

_Written per V4.1 §0. If this session ends, the next invocation resumes HERE after the §4
repository-truth ritual. HEAD at write time: wave-13 specs frozen (see git log), pushed._

## Wave-12 close (seq 420-425, both red-teamed, ingested at 8f0175e)
SMV2AF_1MIN_RESCALE_R2: **1-minute Solar CLOSED FOR GOOD** (Gate A/bootstrap passed thinly,
Gate B/LOYO FAILED 3/5 years, Gate C/old-regime — built on a native 1m 2006-2021 substrate
that turned out to exist — showed the construction losing money, Gate D confirmed high
correlation/no diversification value). SMV2AG_ADAPTIVE_CLAMP: CONFIRMED-NOT-BENEFICIAL,
CLOSED (0/6 cells; same Sharpe-for-CDaR tradeoff as the fixed-ceiling test). Both clamp-
ceiling mechanisms (fixed-raise, adaptive-widen) now exhausted. Mid-wave, owner asked about
stop-loss/day-loss-limit mechanisms — answered directly (audit: neither deployed strategy has
one in code; every classic exit/stop idea tested here is dead; loss-reactive cooldowns are
ANTI-EDGE per SM02B; genuine confirmed gap: a same-day circuit breaker was never tested).

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
1. **Wave-13 workflow**: specs frozen before any read (see git log for the freeze commit):
   - **SMV2AH_DAY_CIRCUIT_BREAKER** (seq 426-429): tests a genuinely new mechanism class — a
     PORTFOLIO-LEVEL, SAME-DAY running-P&L circuit breaker (halt for the rest of the session
     once today's cumulative MTM crosses a calibrated threshold), structurally different from
     every prior exit/stop idea (all of which were per-trade adverse-excursion stops, all DEAD
     because Solar's reversal logic already acts as one) and from SM02B's cross-day
     loss-streak throttle (found ANTI-EDGE). Requires building a genuinely new artifact — an
     intraday bar-by-bar cumulative MTM series — with a mandatory reconciliation check against
     existing EOD curves before any breaker logic runs. 2 halt modes (FREEZE vs FLATTEN) × 4
     percentile-calibrated thresholds × 2 objects (Solar-only, DAYONLY_DUAL6040 portfolio),
     each cell must beat a matched-placebo (random-bar halt, same trigger count) not just
     "no breaker" — mirrors SMV2N/V/Z/AA's established policy-test discipline. Disclosed prior
     risk (not to bias the test): every loss-reactive idea tested in this program so far has
     been anti-edge; this spec is honestly designed to find out if same-day is different, not
     to confirm either outcome.
   - **SMV2AI_ATR_BLEND** (seq 430-432): expansion-pass candidate #3. sigma460 is close-only
     and structurally blind to intrabar wicks; tests replacing/blending it with a rescaled
     ATR (true-range) estimator (measure the ATR/sigma460 scale ratio first, SMV2AE-style
     discipline, then arm_REPLACE + 3 blend weights). Same AND-rule as every clamp/cohort test
     this wave-class. Different axis from everything closed so far — changes what sigma
     MEASURES, not the clock or the clamp ceiling.
   Both get independent red-team verification. On completion: ingest, correct any red-team-
   flagged issues in the run REPORTs (never spec.yaml), update registry (seq 426-432) +
   CURRENT_TRUTH/INDICATOR_FRONTIER, commit+push, then immediately freeze the next wave (volume
   bars — expansion-pass EVI rank #2, a new clock mechanism — is the natural next pick if both
   wave-13 specs close cleanly; also revisit SM14's missing realtime-fail-closed code guard,
   flagged this wave as a risk-hygiene item, not yet actioned). Auto-chain — do not stop at
   close-out, do not ask before launching the next wave unless genuinely blocked.
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
