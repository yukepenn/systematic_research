# CURRENT_TRUTH — single page, updated after every wave

_Last update: 2026-08-08, end of V4.1 wave-7 (SMV2Z viability-state policy). Supersedes the
"FINAL" framing of V1 docs (FINAL_NQ_SYSTEM.md remains the V1 record)._

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
