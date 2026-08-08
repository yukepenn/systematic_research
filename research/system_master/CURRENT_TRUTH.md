# CURRENT_TRUTH — single page, updated after every wave

_Last update: 2026-08-08, end of V4 wave-2 (SMV2H2/I/J/K + SMV2M master build). Supersedes
the "FINAL" framing of V1 docs (FINAL_NQ_SYSTEM.md remains as the V1 historical record)._

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
