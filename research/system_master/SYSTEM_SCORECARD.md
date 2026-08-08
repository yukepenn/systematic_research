# SYSTEM_SCORECARD — live champion board (Directive V2 §44)

_2026-08-08 post-SMV2 wave-1. All portfolio rows on equal-vol basis (DUAL-Solar dev σ);
one-contract rows native. "cc" = candidate composition (separately-gated parts)._

| slot | holder | key stats (dev 2022-2026/05) | evidence |
|---|---|---|---|
| SOLAR_REFERENCE | E10 graded ensemble | $119k, Shp 0.71, DD −$40.2k | A (parity-exact) |
| CORE_BASELINE | SOLAR_DUAL_HTF | $138k, Shp 0.90, DD −$25.7k, crisis ret 0.78 | B components, cc |
| BEST_RAW_RETURN | DUAL+BMOM 50/50 | $203k at equal vol, Shp 1.32 | D plateau |
| BEST_SHARPE | DUAL+BMOM 50/50 | Shp 1.32 | D |
| BEST_CALMAR | DUAL+BMOM 50/50 | 2.38 (60/40: 2.37) | D |
| BEST_LOW_DD | DUAL+BMOM 60/40 | maxDD −$18.1k, CDaR −$14.3k | D |
| BEST_SMOOTH_MONTHS | DUAL+BMOM 80/20 | pos-months 70%, worst −$8.1k | D |
| BEST_DAY_ONLY | **DAYONLY_DUAL6040** | Shp 1.26, DD −$18.1k, worst-mo −$6.9k | cc/D |
| BEST_FULL_PORTFOLIO | = BEST_DAY_ONLY (B1 demoted; P3 tracked as variant) | P3: Shp 1.22, DD −$25.0k | SMV2C |
| BEST_ONE_NQ | A-dominant(≥5) challenger | $378.7k, Shp 1.37, DD −$47.0k | B/D, ch |
| BEST_ONE_MNQ | A-dominant(≥5) challenger | $36.0k, Shp 1.30, DD −$4.7k | B/D, ch |
| BEST_ONE_CONTRACT (FINAL) | SM14 hyst(3,1) — gate holder | $28.7k, Shp 1.06, DD −$6.0k MNQ | B (gated) |
| BEST_COMPLEMENTARY_ENGINE | B-MOM (E2) | Shp 1.31 standalone, losing-day ρ≈0.04 | B |
| BEST_SIMPLE_SYSTEM | A-dominant(≥5) one-lot | one threshold + B-MOM priority | B/D, ch |

ch = challenger, replacement gate not formally passed (P=0.83 vs 0.85 required).
Never read this table as "same winner everywhere": slots differ by objective and risk basis.

## Smoothness battery (PERMANENT columns per V4.1 §12; SMV2Q seq 380, dev <=2026-05-31)
| system | pos-day% | pos-wk% | pos-mo% | pos-qtr% | worst wk | worst mo | worst qtr* | streaks d/w/m | TUW | rec med/p95 |
|---|---|---|---|---|---|---|---|---|---|---|
| MASTER_EXEC (NT8) | 44.1 | 56.1 | 64.2 | 83.3 | -10,307 | -7,523 (2026-04) | -14,300 | 10/4/3 | 131 | 5/62 |
(*partial edge quarters included and tagged; full table incl. E10/DUAL/BMOM/SM14: runs/SMV2Q_DIAGNOSTICS/out/smoothness_battery.csv)
Interpretation guard (V4.1 §16): 44% positive days is EXPECTED for a right-tail trend book;
weekly/monthly quality is the owner-relevant axis. 64% positive months / 4-month worst losing
streak / 83% positive quarters is the current champion baseline to beat.

## Joint-loss truth (SMV2Q): the smoothness lever is IDENTIFIED
50/230 dev weeks are Solar+BMOM joint-loss; they are 100% master-negative, are HALF of all
negative weeks, and own -$159.6k of week-sums. Their market-state signature is causal and
measurable: LOW path efficiency (ER150 0.0855 vs 0.0960, t=-6.5) and HIGH flip rate (t=+3.0).
Engine #3 / router work should target exactly this state — but all six externally-sourced
reversion/rotation/calendar engines are now dead; next step is mechanism expansion (V4 §51).

## 2026 recency (owner question, SMV2Q): FACT + INFERENCE
Rolling-120-session Sharpe percentile vs each system's own history, at dev end: BMOM 52nd,
MASTER 41st, DUAL 35th, SM14 27th, E10 17th — none near historical minima. The master sat at
its 95th percentile in Feb 2026; Apr-May 2026 was a joint-loss episode (DD #2, -$16.5k) of the
kind that occurs ~1x/yr in-sample. CONSUMED June 2026: +$20.6k. INFERENCE: 2026 weakness is
one JL episode within normal path variation, not decay evidence; E10 standalone is the weakest
component (17th pctile) and the composed system is mid-range. The preregistered decay monitors
(MONITOR-01, SM13 floor) remain the tripwires — no tuning from this read.

## Smoothness policy attempts — 0 for 3, but the reason why is now understood (2026-08-08)
Three independent, honestly-tested attempts to convert downside/joint-loss information into a
risk-reduction policy have now failed: SMV2N (windfall give-back, indistinguishable from
random de-risking), SMV2V (ER150-exhaustion damper on Solar alone, same failure mode), SMV2Z
(sigma460+ER150 AND-gate portfolio scale, FAILED WORSE than the other two — CDaR got worse,
not just "not better"). SMV2Z's finding explains the pattern for all three: the market states
that identify elevated downside risk in this system ALSO identify elevated total variance —
the flagged periods hold a hugely disproportionate share of total net PnL (30.3% of net on
9.9% of days in SMV2Z). This is a coherent, causal explanation for why simple exposure-timing
policies keep failing here, not three unrelated dead ends. Any future smoothness attempt
should design explicitly around this constraint (e.g., a policy that changes ENGINE MIX during
flagged weeks rather than cutting total exposure, since mix changes could theoretically retain
upside participation while changing risk composition) rather than repeating a fourth blanket
exposure-scaling variant.
