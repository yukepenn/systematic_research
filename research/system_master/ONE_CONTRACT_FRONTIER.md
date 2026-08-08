# ONE_CONTRACT_FRONTIER — {-1,0,+1} rebuilt from first principles (SMV2H, seq 347-357)

_2026-08-08. State: DUAL_HTF Solar target T″ + frozen B-MOM pending position B;
day-only ops (forced exit decided 16:39, no entries 16:30-18:00); fills next bar open ±1t.
Dev 2022-2026/05; NO untouched holdout exists for one-contract objects (disclosed).
Code `runs/SMV2H_ONECONTRACT/smv2h.py`._

## Results (1 MNQ | 1 NQ)

| seq | policy | MNQ net / Sharpe / DD / worst-mo | NQ net / Sharpe / DD | crisis ret | TUW |
|---|---|---|---|---|---|
| 355 | **SM14 reference** (old M, hyst 3/1) | $28.7k / 1.06 / −$6.0k / −$2.3k | $303.9k / 1.12 / −$58.5k | 1.00 | 172d |
| 347 | C hyst(3,1) on new M′ | $29.1k / 1.10 / −$4.4k / −$2.0k | $305.2k / 1.16 / −$43.0k | 0.93 | 216d |
| 348 | C hyst(4,1) | $28.1k / 1.14 / −$4.0k / −$1.5k | $292.1k / 1.19 / −$39.7k | 0.92 | 267d |
| 349 | B sign-deadband | $25.0k / 0.92 / −$5.2k | $264.0k / 0.97 / −$51.1k | 0.89 | 243d |
| **350** | **A dominant (B-MOM first; Solar iff \|T″\|≥5)** | **$36.0k / 1.30 / −$4.7k / −$3.0k** | **$378.7k / 1.37 / −$47.0k** | 0.97 | 129d |
| 351 | A dominant (≥7) | $31.7k / 1.24 / −$4.0k / −$2.2k | $332.1k / 1.30 / −$39.9k | 0.93 | 137d |
| 357 | A dominant (≥9) | $33.1k / 1.29 / −$3.8k / −$1.8k | $344.5k / 1.34 / −$38.0k | 0.91 | 126d |
| 352 | E conflict-flat (≥5) | $28.0k / 1.14 / −$4.1k | $303.5k / 1.24 / −$41.0k | 0.94 | 134d |
| 353 | E conflict-flat (≥7) | $23.7k / 1.06 / −$4.1k | $256.9k / 1.15 / −$40.8k | 0.90 | 95d |
| 354 | G router (HTF-veto shorts) | $29.1k / 1.12 / −$4.2k / −$1.5k | $307.7k / 1.18 / −$41.4k | 0.92 | 221d |
| 356 | C hyst low-DD (5,2) | $18.9k / 1.00 / −$3.5k | $195.3k / 1.04 / −$34.4k | 0.76 | 421d |

All 10 new cells beat the SM14 reference on ≥3/5 risk metrics. Every cell 4-5/5 dev
years positive, H1/H2 same sign.

## Verdict — honest and by the letter of the frozen gate

- **Replacement gate NOT passed**: best daily-mean bootstrap P = 0.828 (350) vs required
  0.85. **SM14-form formally remains ONE_CONTRACT_FINAL** (last cleanly-gated holder).
- **A-dominant family = ONE_CONTRACT_CHALLENGER** (Level B+D evidence: preregistered,
  3-cell plateau 350/351/357 all Sharpe ≥1.24 and DD −$38-47k NQ vs −$58.5k, crisis
  retention 0.91-0.97). Post-hoc Level-F diagnostics: P(dSharpe>0) = 0.71-0.80,
  P(DD-better) = 0.57-0.64 — directionally consistent, underpowered on 4.4yr.
- Gate design error recorded: a daily-MEAN test cannot certify risk-shaped improvements
  (351/357 win all five risk metrics at similar net → mean-diff ≈ 0 by construction).
  Next one-contract wave must gate on ΔSharpe/ΔCDaR bootstrap, preregistered.
- Champion board slots: ONE_CONTRACT_MAX_SHARPE/MAX_GROWTH = **350**;
  ONE_CONTRACT_LOW_DD = **357** (dominates 356 everywhere); ONE_CONTRACT_SIMPLE = 350
  (one threshold, no hysteresis pair); ONE_CONTRACT_FINAL = SM14 (pending confirmation
  wave).

## Why the improvement happens (mechanism, from the SM14 top-10 DD autopsy)

`out/sm14_dd_autopsy.csv`: 6 of SM14's 10 worst episodes occurred with HTF
predominantly UP (0.65-0.94 of bars) while the policy still shorted 17-24% of the
time — counter-HTF shorts are the recurring drawdown mechanism (same finding as
SMV2E at portfolio scale; the DUAL state fixes exactly this). The remaining episodes
are fast HTF-DOWN shocks (2022-05, 2025-03) — the convexity events, untouched by the
DUAL rule (retention 0.91-0.97). B-MOM was active in only ~22-27% of DD bars: DDs are
Solar-bleed phenomena; the dominant-engine policy (B-MOM outranks weak Solar) removes
weak-consensus Solar exposure that contributed losses without carrying the big-winner
right tail (|T″|≥5 keeps 5/5 years positive).

## 1 MNQ vs 1 NQ (directive §9, settled)
Identical signals; friction only: 10×MNQ pays $13.00/RT vs NQ $4.36/RT per 10-MNQ-equiv
(slip identical). Over dev this is $17.2k ≈ all of the Sharpe gap (1.30 vs 1.37 at 350).
1 MNQ remains the correct risk unit for accounts <$60k; 1 NQ is strictly cheaper per
unit of exposure when the DD (−$38-47k range) is fundable.

## LOYO addendum (2026-08-08, from saved curves)
A-dominant vs SM14 reference, net delta by year — 350: 2022 −$2.2k, 2023 +$1.2k,
2024 +$1.0k, 2025 +$3.9k, 2026 +$3.4k (dSharpe −0.42/+0.24/+0.28/+0.44/+1.06).
4/5 years positive but magnitude concentrated 2025-26 (the counter-trend-short bleed
era the DUAL state targets); 2022 gives back ground because halved HTF-UP shorts missed
early-crash downlegs. Supports CHALLENGER status, not yet FINAL promotion.

## SMV2H2 confirmation wave (2026-08-08, seq 358-360) — A-DOMINANT CONFIRMATION FAILED
Preregistered dual gate (paired block bootstrap, block=5 B=10000 seed 20260808):
- Gate A center (s7): P(dSharpe>0) = 0.717 MNQ / 0.712 NQ; P(dCDaR>0) = 0.639 / 0.632 — all
  below the 0.85 bar. Every one of the 12 point estimates favors the challenger; the failure is
  a CONFIDENCE failure on 4.4y of dev data (INFERENCE: underpowered), not a sign reversal.
- Gate B old-regime (2006-2021, Solar-only, identical replay both policies): A_dom_s7 net
  $29,709 vs SM14 $46,866 — gap −$17,158 breaches the −$10k non-inferiority floor. The entire
  gap is 2020-21 melt-up capture; A_dom wins 11/16 years head-to-head with 0.36× the maxDD.
- Right-tail warning FIRED: A_dom_s7 retains only 77% of SM14's top-10-day PnL (< 90% bar).
**Verdict: family KILLED per frozen decision rule. SM14 oldM(3,1) RETAINED as
ONE_CONTRACT_FINAL.** Red-team: CONFIRMED (spec letter-exact, curves reproduce canonical
outputs to 0.0). Next per V4 §51: ONE new bounded discrete family in a future spec — the
autopsy directions worth encoding: keep B-MOM priority, but address the top-10-day retention
loss (the challenger's weakness is missing SM14's biggest winner days, e.g. 2024-08-08).

## OWNER ADDENDUM 2026-08-08 — Product B final deliverable definition (binding)
Product B is complete only when BOTH `BEST_ONE_NQ` and `BEST_ONE_MNQ` exist as separate,
fully-implemented, Strategy-Analyzer-parity-proven NinjaTrader strategies (final names like
SolarWaveOneContractNQ_Final.cs / SolarWaveOneContractMNQ_Final.cs), each with the full metric
battery + historical AND stressed capital maps, LIVE-READY-BUT-DISABLED (realtime fail-closed;
enablement is a separate explicit owner decision — see LIVE_READINESS_CHECKLIST.md).
KEY CONSEQUENCE for gate design: NQ and MNQ are separate economic products (friction/rounding/
discrete-risk differ), so FUTURE confirmation specs may promote DIFFERENT policies per
instrument. The frozen SMV2S spec (in flight) still requires both-instrument passes for a
joint replacement per its letter; its per-instrument results feed per-instrument follow-up
specs if the joint gate fails but one instrument dominates. BEST_ONE_CONTRACT_OVERALL is
selected only after both instrument products are resolved.

## SMV2S (seq 386-388): HTF-gated dominant KILLED — frontier PAUSED
Second consecutive family kill. Center thr5: gate A P(dSharpe)=0.64, P(dCDaR)=0.48 (<0.85);
gate B retention 0.841 vs 0.90 HARD bar (improved from A-dominant's 0.772 — the mechanism
moved the right lever, not far enough); gate C old-regime gap -$36.1k (2021 melt-up alone
-$55.7k). AGAIN pointwise better than SM14 everywhere on dev (MNQ Sharpe 1.169 vs 1.056,
NQ maxDD -$44.8k vs -$58.5k) and AGAIN unprovable at 0.85 confidence. Pattern across both
killed families (FACT): challengers dominate point estimates but 4.4y of daily data cannot
deliver 0.85 confidence for risk-shaped improvements of this size; and every Solar-side
filter loses 2020-21-style melt-up capture in the old regime. Per frozen spec: one-contract
frontier PAUSES for a mechanism-expansion pass. SM14 remains ONE_CONTRACT_FINAL; per the
owner addendum the eventual finals are per-instrument (BEST_ONE_NQ / BEST_ONE_MNQ).
