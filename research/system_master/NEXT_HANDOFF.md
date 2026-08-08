# NEXT_HANDOFF — exact continuation state (2026-08-08, after wave-11 close / wave-12 launch)

_Written per V4.1 §0. If this session ends, the next invocation resumes HERE after the §4
repository-truth ritual. HEAD at write time: wave-12 specs frozen (see git log), pushed._

## Wave-11 close (seq 415-419, both red-teamed, ingested at b2bb4d4)
SMV2AD_VOLMULT_CEILING: CONFIRMED-OPTIMAL-IN-RANGE, CLOSED (0/5 arms beat the 1200t/VMS-6-30
incumbent on Sharpe AND CDaR simultaneously — raising the ceiling always trades one for the
other). SMV2AE_1MIN_RESCALE: PASS-SCREEN (rescaling VolMult's point-scale by the measured
3m/1m ratio R=1.7301 flips 1-minute from net -$3.2k/Sharpe -0.018 to net $77.7k/Sharpe 0.439,
friction share 1.02→0.47 — still well below the 3m incumbent's 0.709 but clears the screen).
Mechanism-expansion pass produced a 9-candidate ranked list for the Solar CORE (not Engine-3).

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
1. **Wave-12 workflow**: specs frozen before any read (see git log for the freeze commit):
   - **SMV2AF_1MIN_RESCALE_R2** (seq 420-423): R2 confirmation of SMV2AE's PASS-SCREEN. Gate A
     (dev bootstrap Sharpe significance, 0.85 bar), Gate B (LOYO/chronology, ≥4/5), Gate C
     (old-regime — likely BLOCKED-BY-DATA, SM06 hist substrate is 3m-only, same wall SMV2W hit
     for 5m; report explicitly, do not improvise around it), Gate D (DIAGNOSTIC, not gated:
     correlation of the rescaled-1m arm's daily PnL vs the 3m incumbent's — a priori expectation
     is HIGH correlation since it's the same mechanism at a finer clock on the same price
     series; if correlation is instead low, an exploratory 50/50 vol-matched blend is tested for
     Sharpe/CDaR improvement vs the 3m-only leg, flagged as an R3 candidate if it wins, no
     adoption either way this wave). No replacement/promotion path exists here by construction
     (0.439 Sharpe << 3m's 0.709) — outcome is either "1-minute construction validated as real,
     not noise" + possible diversification lead, or "downgraded to noise-level, 1-minute CLOSED
     for good across every calibration convention this program can motivate."
   - **SMV2AG_ADAPTIVE_CLAMP** (seq 424-425): mechanism-expansion pass's #1-ranked idea. Tests
     a CAUSAL rolling-percentile clamp ceiling (P∈{90,95,99} × N∈{460,920} bars, 6 cells, floor
     at the incumbent's 1200t so it can only widen, never tighten below it) instead of SMV2AD's
     now-closed FIXED-value ceiling raise — hypothesis: captures the Sharpe upside from relieving
     the 2026-concentrated clamp bind without SMV2AD's permanent CDaR cost, since it only widens
     when the recent realized-threshold distribution actually calls for it. Same AND-rule
     (Sharpe AND CDaR AND ≥95% top-10 retention) — no adoption this wave, qualifying candidate →
     R2 spec next.
   Both get independent red-team verification. On completion: ingest, correct any red-team-
   flagged issues in the run REPORTs (never spec.yaml), update registry (seq 420-425) +
   CURRENT_TRUTH/INDICATOR_FRONTIER, commit+push, then immediately freeze the next wave (the
   next-ranked expansion-pass idea — volume bars as a new clock, EVI rank #2 — is the natural
   next pick if both wave-12 specs close cleanly). Auto-chain — do not stop at close-out, do
   not ask before launching the next wave unless genuinely blocked.
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
