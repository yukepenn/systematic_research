# CURRENT_TRUTH — single page, updated after every wave

_Last update: 2026-08-08, end of V4.1 wave-14 (SMV2AJ ATR-blend R2 confirmation — CLOSED,
closest miss of any R2 in this program). Supersedes the "FINAL" framing of V1 docs
(FINAL_NQ_SYSTEM.md remains the V1 record)._

## Wave-14 verdict (spec 8c030f8; red-team CONFIRMED, 2 prose-only corrections, no numeric/
## decision impact) — the closest an R2 confirmation has come to passing in this program
**SMV2AJ_ATR_BLEND_R2 (seq 433-437) — CLOSED, incumbent retained.** R2 confirmation of
SMV2AI's arm_BLEND_75 lead (75% incumbent sigma460 / 25% properly-rescaled ATR estimator),
tested at the actual DUAL-transformed decision object (confirmed via direct code read that
SMV2AI's own old-regime screen tested the raw pre-DUAL target, so this was a genuine unseen
re-test, not a duplicate). **Result: 1 of 5 required gates fails — Gate A (dev bootstrap),
and only on its CDaR_0.95 prong** (P(dSharpe>0)=0.932 clearly passes the 0.85 bar; P(dCDaR>0)
=0.753 falls short). **Gates B (LOYO 4/5, improving into 2025-26), C (old-regime, net gap
+$86,004 vs a −$10k floor, wider than SMV2AI's own raw-level screen), D (right-tail retention
100.14%), and E (portfolio: dSharpe +0.033/dCDaR +$318, both point-positive, with almost no
leg-vol sizing confound unlike SMV2T's challenger) all PASS, several with real margin** — this
is the strongest performance any core-challenge R2 has produced in this program (SMV2T failed
3/5 gates outright; this failed only 1, and only one prong of it). Gate F (new this wave:
bootstrap at neighbor blend weights w=0.70/0.80, disclosure-only) showed the point estimates
form a smooth, non-spiky local hump across w=0.70-0.80, but CDaR bootstrap significance is
weak across the WHOLE neighborhood, not just at w=0.75 — reinforcing, not contradicting, gate
A's failure: the mechanism looks real but its tail-risk improvement is not yet statistically
distinguishable from noise on 4.4 years of daily data. Per the frozen AND-rule, applied with
no discount for how close this came: **incumbent sigma460-only core retained. Lead CLOSED —
no third bite without a new mechanism that specifically targets the CDaR-tail effect** (not a
re-test of the same blend at a different weight). This is a genuinely different failure
pattern from every other closed core challenge in this program (which mostly failed on
old-regime melt-up capture or right-tail retention) — the mechanism itself may be real; only
its statistical confirmation on tail risk specifically fell short.

## Wave-13 verdict (specs d927ec6; red-team CONFIRMED-with-corrections on both — SMV2AH had 2

## Wave-13 verdict (specs d927ec6; red-team CONFIRMED-with-corrections on both — SMV2AH had 2
## narrative corrections [gate-1 object-attribution breakdown, a FLATTEN-worst-day
## overgeneralization], SMV2AI had 5 corrections [4 cosmetic/typo, 1 real prose mischaracterization
## of arm_BLEND_25's CDaR — none change either verdict]; both runs' only other gap was a missing
## REPORT.md, now written) — **arm_BLEND_75 is the first genuinely new Solar-core mechanism to
## pass a standalone AND-rule screen since the clamp-ceiling/clock-challenge series began closing.**
**SMV2AI_ATR_BLEND (seq 430-432) — QUEUE_R2_CONFIRMATION.** sigma460 is close-only and
structurally blind to intrabar wicks (99.3% of dev bars carry TR > |Δclose|, i.e. real wick
information sigma460 cannot see). Blending it 75/25 with a properly rescaled ATR (true-range)
estimator — `sigma_ATR_eff = ATR460/2.0255`, R measured with the same discipline SMV2AE used —
**uniquely qualifies**: standalone Sharpe 0.746 vs 0.709 control, CDaR₀.₉₅ $25,183 vs $27,162
(better), top-10-day retention 100.2% (comfortable margins, not borderline). The a priori churn
concern (ATR is noisier intrabar) is NOT confirmed — flip-count rises only 0.09%. At the
portfolio level (DAYONLY_DUAL6040 60/40) it also beats the champion (Sharpe 1.297 vs 1.264,
CDaR $14,004 vs $14,322). **Old-regime screen (2006-2021) passes with real margin, not
marginally** — net gap +$71,544 vs a −$10k floor, maxDD ratio 0.954 vs a 1.25× ceiling — the
exact floor that killed 3 of 5 prior core-challenge candidates in this program. Pure-ATR
replacement (arm_REPLACE, w=0) has the single best standalone CDaR of all 5 arms but fails on
Sharpe alone; w=0.25/0.50 both fail outright; the w-relationship is non-monotonic, disclosed
not explained. **No adoption this wave** — queues a full SMV2T-style R2_CONFIRMATION
(bootstrap significance, LOYO, right-tail, formal portfolio gate) next wave, the natural top
priority.
**SMV2AH_DAY_CIRCUIT_BREAKER (seq 426-429) — KILLED, CONFIRMED-NOT-BENEFICIAL.** Directly
answers the owner's stop-loss/day-loss-limit question from mid-wave-12: a same-day, portfolio-
level running-P&L circuit breaker (2 halt modes × 4 percentile-calibrated thresholds × 2
objects, 16 cells) was built and tested for the first time in this program (required new
intraday bar-by-bar MTM machinery, reconciled exactly against existing EOD curves before any
breaker logic ran). **0/16 cells qualify.** Decisive failure: in every single cell, the real
threshold-triggered rule's CDaR is *worse* than a matched placebo that halts the same number of
sessions at a random bar instead of the actual loss-triggered bar — a reactive rule structurally
captures less protection than random truncation, because it can only act after the loss has
already partly happened. This is now the THIRD distinct time-scale where loss-reactivity has
tested anti-edge in this program (per-trade MAE stops SM03/SM03B — dead, Solar's own reversal
already acts as one; cross-day streak throttle SM02B — anti-edge; now same-day — anti-edge, for
a cleaner mechanistic reason). Leg attribution: the deployed portfolio's triggers are genuinely
mixed (67-83% joint Solar+B-MOM negative days), not chasing one engine's noise.

## Wave-12 verdict (specs db39d56; red-team CONFIRMED-with-corrections on both — SMV2AF had one

## Wave-12 verdict (specs db39d56; red-team CONFIRMED-with-corrections on both — SMV2AF had one
## factual labeling fix in a comparison table (does not change the conclusion), SMV2AG had zero
## numeric corrections; both runs' only other gap was a missing REPORT.md, now written)
**SMV2AF_1MIN_RESCALE_R2 (seq 420-423) — 1-minute Solar is now CLOSED FOR GOOD.** R2
confirmation of SMV2AE's screen-level pass (rescaled 1m Sharpe 0.439). Gate A (dev bootstrap
significance) passed by a thin margin (P(Sharpe>0)=0.853 vs 0.85 bar, not corroborated by
Newey-West t=1.08). Gate B (LOYO chronology) **FAILED**: only 3/5 years same-sign (bar is
4/5). Gate C (old regime, newly built on a native 1-minute 2006-2021 substrate that turned out
to exist, a genuine finding of its own) showed the rescaled construction **losing money**
(net −$20,583, Sharpe −0.119, friction exceeding gross) — worse than even the mediocre,
already-REGIME_LOCAL 3m incumbent's own historical result. Gate D confirmed the a priori
expectation of high correlation with the deployed 3m signal (0.897) and found no
diversification value (a 50/50 blend beats neither Sharpe nor CDaR of the 3m-only leg). Per
the spec's own rule, a Gate B failure downgrades the screen result to noise-level: **1-minute
Solar is closed under every calibration convention this program has tried** (fixed-
StopMultiplier family, VolMult unscaled ×2 sigma-window conventions, VolMult rescaled) — no
further attempts without a structurally new signal-generation mechanism.
**SMV2AG_ADAPTIVE_CLAMP (seq 424-425) — CONFIRMED-NOT-BENEFICIAL, lead CLOSED.** The
mechanism-expansion pass's #1-ranked idea (a causal rolling-percentile clamp ceiling, floored
at the incumbent 1200t so it can only widen) hit the identical Sharpe-for-CDaR tradeoff SMV2AD
found for a fixed higher ceiling: every one of 6 cells (P∈{90,95,99}×N∈{460,920}) improved
Sharpe (+0.11 to +0.14), but only one cell also improved CDaR (+$138, the smallest possible
win) — and that cell failed the top-10-day retention floor (87.6% vs ≥95%). 0/6 qualify. The
ceiling genuinely widens more in high-vol periods (2025's tail is the most extreme on file) but
only as a thin upper-tail effect, not a broad regime shift — explaining why it buys Sharpe
without reliably buying CDaR. **Both the fixed-raise and adaptive-widen-only clamp-ceiling
mechanisms are now exhausted**; any future clamp idea needs a genuinely different shape (e.g.
one that can also tighten) to be worth a spec.
**Owner follow-up (mid-wave-12, addressed directly, no new autonomous wave launched for it
yet)**: owner asked what stop-loss/day-loss-limit mechanisms exist and whether they matter.
Audit confirmed: neither deployed strategy has a resting stop-loss, daily loss limit, or
kill-switch in code (only session-close flatten + the 16:39-18:00 ET margin-cliff ops rule).
Every classic stop/exit-engineering idea ever tested in this program (SM03/SM03B disaster
stops, split exits, resting stops, timed exits, trailing/break-even — `STOP_OVERLAY_FRONTIER.md`)
is DEAD, because the Solar state machine's own reversal logic already acts as a stop. Loss-
reactive cooldowns are ANTI-EDGE (SM02B: next-day expectancy is HIGHER after a loss day, not
lower). Windfall give-back (profit-lock) was KILLED at the policy level (C-P7). **Genuine,
confirmed-never-tested gap**: a same-day intraday circuit breaker (halt trading for the rest of
the session after a running-loss threshold) has never been built or backtested here under any
name — queued for a future wave. **Separately flagged risk-hygiene finding**: `SolarWaveSMMaster_v2.cs`
is coded realtime-fail-closed (never submits live orders); `SolarWaveSMOneLot_v1.cs` (SM14) has
no equivalent code-level guard — its fail-closed posture currently rests entirely on the
LIVE_READINESS_CHECKLIST's operating discipline, not on a safeguard inside the file itself.

## Wave-11 verdict (specs 2b2f88a; red-team SMV2AD CONFIRMED-with-corrections [2, both

## Wave-11 verdict (specs 2b2f88a; red-team SMV2AD CONFIRMED-with-corrections [2, both
## applied to the run REPORT — a missing-file deliverable gap and a tautology-framing fix,
## neither numeric], SMV2AE CONFIRMED with zero corrections) — owner-directed pivot back to
## genuinely new Solar-core mechanism ideas after the owner flagged wave 6-10 diagnostics as
## scope drift ("went too far? we only want best nq or mnq strategies"), then re-authorized
## full autonomy with the standing goal restated.
**SMV2AD_VOLMULT_CEILING (seq 415-417) — CONFIRMED-OPTIMAL-IN-RANGE, lead CLOSED.** The
1200t/300pt clamp on the slowest member (VolMult=30) binds 39.2% of Jan-May 2026 bars vs
9.8%/0.2%/3.9%/18.3% in 2022-2025 (SMV2R sub_381) — more binding now than any full historical
year, never before acted on. Raising the ceiling (1200/1600/2000/2400t) DOES mechanically
relieve the bind (10.93%→0.57% at 2400t) and DOES lift Sharpe monotonically (0.709→0.863
standalone) — but CDaR_0.95 (tail drawdown) worsens at every ceiling tested (+4.9-5.0%): the
unclamped slow member trades rarer, larger, fatter-tailed trend moves. 0/3 ceiling arms and
0/2 extended-slow-cohort arms (VolMult 34-50, add-18 or replace-fastest-13) qualify as
candidates (must improve Sharpe AND CDaR AND retain >=95% top-10-day sum). The current
1200t/VMS-6-30 design is a genuine local optimum on the Sharpe/CDaR frontier, not a historical
accident. Closed — no third bite at a *fixed*-value ceiling/cohort change without a new
mechanism. (Does NOT close the *adaptive*/percentile-ceiling idea — structurally different,
ranked #1 in the same-wave mechanism-expansion pass below, still open.)
**SMV2AE_1MIN_RESCALE (seq 418-419) — PASS-SCREEN, queues R2_CONFIRMATION.** SMV2U's two
prior 1-minute tests reused the 3m VolMult constants VERBATIM on 1m-scale sigma (confirmed by
code read) and both failed decisively (friction 102-128% of gross). The un-recalibrated axis —
VolMult's point-scale itself, since 1m |dClose| isn't point-comparable to 3m |dClose| even over
an identical time window — was measured directly (R=1.7301, tight and regime-stable across 5
years, medians 1.721-1.742) and applied. Result: net flips from -$3,163/Sharpe -0.018 (unscaled)
to **net $77,748/Sharpe 0.439**, friction share drops from 1.020 to 0.470. Clears the
pre-registered screen (Sharpe>0 AND friction<0.60) with a comfortable margin — but still trails
the 3m incumbent (Sharpe 0.709) on every metric, and NO bootstrap/LOYO/old-regime/portfolio
battery has been run yet (this was a screen, not a promotion attempt). Queued for R2 next wave.
**Mechanism-expansion research pass** (no spec, `deep_research/DR_V4_SOLARCORE_EXPANSION_
20260808.md`): 9 ranked Solar-CORE (not Engine-3) candidates, deduped against every closed
lead. Top 3 by EVI: (1) percentile/rolling-adaptive clamp ceiling (replaces the now-closed
FIXED ceiling idea with a genuinely different adaptive one), (2) volume bars as a new clock
mechanism (distinct from the 3x-killed fixed-time 1m/3m/5m family), (3) ATR/range-based
threshold estimator blended with sigma460 (captures intrabar wicks sigma460 structurally
cannot see). Candidates 4-9 ranked lower (thinner data, higher duplication risk vs closed
leads, or explicitly flagged as possible re-skins of killed ideas — one (#9) requires reviving
the T2/T3 layer already shown to add zero information and is included only to honestly close
the question, not as a promising lead).

## Wave-9 verdict (spec 0da78b6; red-team CONFIRMED, 2 trivial arithmetic corrections applied)
First cross-market Engine-3 slate — ES/NQ dispersion catch-up, duration-spread shock reaction,
quarterly roll basis convergence — **ALL THREE KILLED** (none clears its significance gate;
none shows the targeted joint-whipsaw complementarity). Combined with the three NQ-only slates:
**12 of 12 Engine-3 candidates across 4 slates now dead.**
**Refinement to the joint-whipsaw understanding**: the 23 SMV2Z-flagged weeks are NOT simply
losing weeks — champion mean weekly PnL is actually HIGHER there (+$2,465.90/wk vs +$652.10/wk
elsewhere), driven by high dispersion including some very large positive weeks. These are
high-variance, regime-uncertain weeks that have, on net, been GOOD for the champion so far —
sharpening (not contradicting) the wave-7/8 finding that they cannot be cheaply de-risked
without giving back disproportionate upside. Data note: RTY/YM substrates share a genuine
11-day gap (2023-04-06..04-14, consistent with the known boundary irregularity) that does not
touch any of the 23 flagged weeks. Remaining unexplored cross-market candidates (D1 ranks
3/4/6, D2 rank 1) are the next place to look before declaring cross-market exhausted.

## Wave-8 verdict (spec f6fb7d1; red-team CONFIRMED, zero issues) — smoothness-policy family
## closed with a coherent explanation, not four unrelated failures
Mandatory prerequisite diagnostic (does Solar respond differently from B-MOM during the
sigma460+ER150-flagged weeks?) FAILED before any policy cell ran: asymmetry ratio 1.04, far
short of the 1.3 bar. Both legs scale UP TOGETHER in flagged weeks (Solar vol +76%, B-MOM vol
+69% vs unflagged) — this is a JOINT whipsaw, not one engine misbehaving while the other holds
steady. Per the spec's own honest-stop design, the mix-shift policy cells were correctly never
run — a complete, valid, non-wasteful outcome.
**SYNTHESIS across all four smoothness-policy attempts (SMV2N, SMV2V, SMV2Z, SMV2AA — all
independently designed, all honestly killed):** the flagged/joint-loss weeks are periods where
Solar and B-MOM behave as CORRELATED expressions of the same underlying modern-regime
breakout-persistence factor, not diversifying ones. You cannot cheaply de-risk by cutting total
exposure (SMV2Z: costs more upside than downside saved) or by reallocating between the two
engines (SMV2AA: they move together, nothing to reallocate toward). This directly answers V4
§58 Q22 ("are Solar and B-MOM merely two expressions of the same regime factor?") for at least
this specific state — **yes, during these weeks they are.** Per V4 §51: this exposure/
reallocation-timing mechanism family is EXHAUSTED; a genuinely different mechanism (e.g. a
THIRD, structurally uncorrelated return source — which is exactly what Engine-3 has been
searching for) is required to actually shorten these episodes, not a smarter way to time the
existing two engines.

## Wave-7 verdict (spec fdd0e65; red-team CONFIRMED) — the KEY reason smoothness is hard here
The simplest possible policy on wave-6's finding (cut exposure when sigma460 AND ER150 both
sit in their historically-worse top tercile) **FAILED DECISIVELY at every scale tested**: CDaR
got WORSE (not better) at every cell, TUW was unchanged, and net retention/RTC collapsed
(0.85-0.96 / 0.89-0.97). The mechanism (FACT): the flagged weeks — only 9.9% of all days — hold
**30.3% of the strategy's TOTAL NET PnL**. The states that flag elevated downside risk ALSO
flag elevated total variance/opportunity — they are not "bad weeks," they are HIGH-VARIANCE
weeks, and cutting exposure into them gives back far more upside than it saves in downside.
This is the THIRD consecutive downside/smoothness policy to fail (after SMV2N windfall,
SMV2V ER-damper) — three independent, honestly-tested attempts, three failures, each for a
different underlying reason. The SMV2Y diagnostic finding itself (sigma460/ER150 forecast
next-week downside) still stands as valid information — it just cannot be cheaply monetized
into a risk-reduction policy without a disproportionate cost to the right tail. Per V4.1 §21,
this specific escalation path (sigma460/ER150 pair → exposure policy) is now EXHAUSTED.

## Wave-6 verdict (spec 51dbc45; red-team CONFIRMED) — FIRST VIABILITY STATE TO PASS
**sigma460 and ER150 both causally predict next-WEEK portfolio downside** (t_NW=−2.30/−3.05,
bootstrap same-sign 0.99/0.998, monotonic, same-sign on an E10-only old-regime proxy). This is
the first state test in the whole program (16 prior cells: VR/ER/Kalman/BOCPD, all killed) to
pass — the difference is the TARGET: next-week portfolio downside, not next-session Solar PnL.
No new data or features — same computed series, different (and correct, per V4 §21) dependent
variable. One open question flagged INFERENCE: ER150's FORWARD sign (high efficiency this week
→ worse NEXT week) is opposite SMV2Q's CONCURRENT finding (joint-loss weeks have low ER150
DURING themselves) — not a contradiction (different timing), but unexplained mechanistically.
**No policy has been tested yet** — this is DIAGNOSTIC only; a bounded 0/0.5/1 exposure policy
per V4 §21 is the natural next step, queued.

## Wave-5 verdicts (specs 7abeb79; both red-team CONFIRMED)
- **5m clock lead CLOSED**: SMV2W's confirmation FAILED 2 of 4 available gates (dev bootstrap
  confidence 0.64/0.55 < 0.85; LOYO only 3/5 years < 4/5-year bar) despite passing right-tail
  retention (0.924) and portfolio point-positivity. Old-regime gate BLOCKED-BY-DATA (5m is not
  causally derivable from the committed 3m hist substrate — a real data-coverage gap, not a
  dodge). **3m incumbent RETAINED — 5th consecutive challenge survived** (memory length,
  cohort structure, MA confirmation, T2/T3 signal layers, now clock).
- **Engine-3 is exhausted at the NQ-only, 3m-bar horizon**: slate 3 (shock-day continuation,
  post-FOMC/CPI drift, post-expiration breakout) — ALL THREE KILLED. Combined with slates 1-2,
  **9 candidates across 3 slates, 0 survivors**. Shock-continuation was even significantly
  NEGATIVE (−$29.2k, t=−2.22) — trading with a 3-sigma shock loses money at this horizon.
  Per V4 §51: next step is an ES/RTY/YM data export (mirroring the SM1M NQ 1m export) before
  any 4th slate — the remaining high-EVI candidates (cross-market lead-lag, 8 of them) all
  require it and are queued, not dropped.

## Wave-4 verdicts (specs 547d2d4; all red-team-verified — 3 CONFIRMED, 3 CONFIRMED-with-prose-fixes)
- **FAST-cohort removal lead CLOSED**: SMV2T's R2 confirmation FAILED 3/5 gates (dev bootstrap
  confidence 0.80/0.39 < 0.85; old-regime net gap −$16.7k breaches the floor; portfolio-level
  dCDaR actually worsens by $1,653). 13-member incumbent core RETAINED. No third bite.
- **ER150-damper policy KILLED**: risk metrics (CDaR/TUW) fail to beat count-matched random
  damping at every cell; the underlying information result (ER150-agreement → lower next-day
  Solar PnL, sign-preserved pre-2022) stands as a diagnostic, converts to no policy.
- **Clock challenge: 1m fails decisively** (friction exceeds gross PnL); **5m bar-matched
  near-misses** (LOYO only 3/5); **5m time-matched (VolPeriod=276, ~23h memory) EARNS an R2
  confirmation** — standalone Sharpe 0.793 vs 0.709, portfolio Sharpe 1.156 vs 1.120, CDaR
  better on both bases, LOYO 5/5 including leave-2022-out, and LOWER turnover than the 3m
  incumbent. R2 spec SMV2W frozen (same 0.85-confidence bar as every other core challenger —
  no double standard for a lead that looks good). One live MTF hypothesis logged (not policy):
  1m-vote disagreement AT ENTRY predicts a −$78/episode PnL gap (t=−2.09), unreplicated on the
  time-matched convention.
- **Engine-3 slate 2 obituary closes with 3 mechanism-expansion passes** (24 candidates,
  archived in full at deep_research/DR_V4_EXPANSION_PASSES_20260808.md). Slate 3 (SMV2X, frozen)
  selects the 3 highest-EVI NQ-only-computable, calendar-anchored CONTINUATION engines: vol-
  shock-day continuation, post-FOMC/CPI drift continuation, post-expiration gamma-unclamp
  breakout. Cross-market candidates (the largest remaining slice) are queued behind an ES/RTY/
  YM data export — not dropped.

## Wave-3 verdicts (specs 58dc2d2; 6/6 red-teams: 5 CONFIRMED, 1 CONFIRMED-with-prose-fixes)
- **C-P7 windfall policy KILLED** (risk reduction indistinguishable from random same-duration
  de-risking; info result stands). **Kalman + BOCPD KILLED** → the whole ranked DSP JOB1 slate
  is dead. **Engine-3 slate 2 ALL KILLED** (VA rotation significantly negative AND
  anti-complementary) → six-for-six reversion families dead; 3 mechanism-expansion passes now
  REQUIRED. **One-lot family #2 KILLED** (retention 0.84 vs 0.90 hard bar; 2nd consecutive) →
  one-contract frontier PAUSED for mechanism expansion; SM14 stays FINAL. **T2/T3 and MA30/59
  KILLED** (MA hard-confirmation costs 22% of net + 6.2% of right tail — pure lag).
- **Solar core re-earned most of its incumbency** (V4.1 §20): vol memory 460 = CONFIRMED
  PLATEAU; SLOW cohort load-bearing; clamp floor irrelevant / 1200t cap an active regularizer.
  ONE live lead: **removing the FAST cohort (vm6-12) improves Sharpe 0.768 vs 0.709 with
  churn halved and top-10-day retention 105.9%** — R2 confirmation spec next wave (thin CDaR
  margin flagged). Plus one HYPOTHESIS: ER150-damper (t=−3.27, over-extended efficiency
  mean-reverts next day).
- **Smoothness truth (permanent scorecard)**: master exec = 44.1% days / 56.1% weeks / 64.2%
  months / 83.3% quarters positive; the negative-period cause is IDENTIFIED — 50/230 joint-loss
  weeks own −$159.6k with a causal signature (LOW path efficiency t=−6.5, HIGH flip rate t=+3.0).
- **2026 recency (owner question)**: rolling-120 Sharpe percentiles at dev end — BMOM 52nd /
  MASTER 41st / DUAL 35th / SM14 27th / E10 17th, none near historical minima; Apr-May 2026 was
  a ~1x/yr-class joint-loss episode; consumed June was +$20.6k. INFERENCE: path variation, not
  decay evidence. Monitors MONITOR-01/SM13 remain the tripwires.

## Wave-2 verdicts (all red-team CONFIRMED; specs frozen at 0a9cf3f before any read)
- **A-dominant one-lot CONFIRMATION FAILED** (gate A P≈0.71/0.63 < 0.85 both instruments;
  gate B old-regime net floor breached; right-tail retention 77% < 90%). **SM14 retained as
  ONE_CONTRACT_FINAL.** All 12 point estimates favored the challenger — confidence failed, not sign.
- **C-P3 leverage disclosure**: at CURRENT champion size, P(2y maxDD > $25k) = 0.14-0.43 across
  bootstrap methods — the historical −$18k is one path. L* < 1.0; leverage add-ons dead.
- **60/40 retained** (C-P1 fit optima 0.50-0.55 but eval ordering not preserved — no move).
- **Killed**: drought-tilt (placebo-indistinguishable), VR + ER trend-quality states (0/12
  cells), Engine-3 slate 1 (failed-break fade SIGNIFICANTLY NEGATIVE t=−2.35 — sweep-reversal
  premium does not exist on modern NQ; small-gap fade negative; overnight drift ~zero).
- **Survivor**: C-P7 windfall give-back pre-test PASSED (fwd-10d −$136/d vs base +$162/d,
  p=0.0012) → bounded trim policy earns a frozen spec.
- **SMV2M master PARITY PASSED**: SolarWaveSMMaster_v2 (one consolidated strategy, fail-closed
  realtime) reconciled vs the true Strategy Analyzer engine — decision-path 99.99% ex the 23
  documented holiday-template days, daily corr 0.9992, net +0.33% ex-holiday. **EXECUTABLE
  HEADLINE (dev): net $177,315 / Sharpe 1.17 / maxDD −$18,894 / CDaR −$14,905 / worst month
  −$7,523** — these replace the research fractional numbers (V4 §16). Genuinely flat before the
  16:45 margin cliff (the research curve never was). New residual class documented: data-gap
  overnight hold (1 episode/4.6y, Δ≈$407). v1 arrangement bug = KNOWN_ERRORS #7.

## The system, in one paragraph
Solar (13-member SolarWave ensemble on NQ 3-min, graded 0-10 MNQ by vote) is the return
backbone. Its exposure is shaped by ONE daily HTF state (prior-session close vs SMA50):
agreement ×1.25 (SM08, passed), counter-HTF shorts ×0.5 (SMV2E c1_50, passed) —
together "SOLAR_DUAL_HTF". B-MOM (noise-band + VWAP intraday momentum, frozen W8-1,
causal-execution-audited) is the diversifying second engine. Best current portfolio:
**60/40 DUAL/B-MOM, day-only, flat before 16:45** — equal-vol maxDD −$18.1k vs the V1
champion's −$25.0k, Sharpe 1.26, worst month −$6.9k. B1 overnight was DEMOTED (failed
its ablation gate). One-contract: SM14 hysteresis rule remains FINAL holder; the
A-dominant policy family (B-MOM first, Solar only at strong consensus, on the DUAL
state) is the strong CHALLENGER (NQ DD −$38-47k vs −$58.5k, Sharpe 1.24-1.37).

## What was verified/corrected this wave
- −$27.2k (PORT_TILT_532) and −$58.5k (OneLot NQ) both REAL but never comparable:
  OneLot NQ runs 1.62× the vol. Equal-vol: −$27.2k vs −$36.2k. ~75% of the gap = size.
- B-MOM edge is NOT an execution artifact (E2 causal = E0 to 0.01t/trade; survives
  +2t/side). Realistic live band = E3-E4 (~Sharpe 1.20-1.26 standalone).
- Old leverage claim trimmed: 22.5% → 21.4%/yr worst-method (L5 was the conservative
  method; ordering PORT > day-only > OneLot > Solar robust across 7 block schemes).
- HTF tilt is a MECHANISM (7/8 neighbor states improve), not an SMA50 cell.
- SM14's original script was never committed; canonical replay differs ≤2.5% (logged).
- June/July 2026 is NOT pristine OOS for anything; no untouched holdout exists.

## Claim taxonomy (Directive V2 §2 labels, current)
- SOLAR_E10: ESTABLISHED HISTORICAL FAMILY-A REFERENCE (regime-local pre-2022).
- HTF_TILT / DUAL_HTF: conditional exposure enhancement, MECHANISM-CONFIRMED. Not alpha.
- BMOM: RECENT_REGIME INDEPENDENT-ENGINE — execution audit PASSED; regime risk stands.
- SOLAR_PLUS_BMOM (DAYONLY_DUAL6040): PRIMARY DAY-ONLY CHAMPION, candidate composition.
- B1_OVERNIGHT: EXPERIMENTAL DIVERSIFIER (demoted from CORE, SMV2C P=0.737).
- PORT_TILT_532: SUPERSEDED as champion; remains the V1 reference composite.
- SolarWaveSMOneLot_v1 (SM14): ONE_CONTRACT_FINAL holder; A-dominant family CHALLENGER.
- Nothing here is "robustly validated / production ready / OOS proven / optimal".

## Standing risks (unchanged)
Both engines are current-regime (post-2020 fuel). Regime death is the true risk model;
MONITOR-01 + SM13 decay floor are load-bearing. Right-tail concentration: B-MOM top-1%
trades = 56-63% of net; Solar winner-drought DDs are normal path statistics.

## Where everything lives
DRAWDOWN_RECONCILIATION / BMOM_EXECUTION_AUDIT / B1_ABLATION / LONG_SHORT_FRONTIER /
LEVERAGE_ROBUSTNESS / ONE_CONTRACT_FRONTIER / DAY_ONLY_FRONTIER / SYSTEM_SCORECARD /
KNOWN_ERRORS_AND_CORRECTIONS / SUPERSEDED_CONCLUSIONS / NEXT_RESEARCH_QUEUE (all in
this directory). Machine state: SYSTEM_FRONTIER.yaml. Specs+outputs: runs/SMV2*.
