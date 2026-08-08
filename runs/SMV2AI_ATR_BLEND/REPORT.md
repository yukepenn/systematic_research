# SMV2AI_ATR_BLEND — REPORT

_Frozen spec: `runs/SMV2AI_ATR_BLEND/spec.yaml` (committed d927ec6 before any read). Authored
by the orchestrator from the execution agent's structured output — subagent Write tool refused
REPORT.md; every number independently reproduced bit-for-bit by red-team (verdict: CONFIRMED-
with-corrections, five corrections applied below, all cosmetic/prose — **none changes the
verdict or arm_BLEND_75's qualification**). Dev window 2022-01-03 → 2026-05-29 (519,714
3-min bars, 1,139 sessions). Simulator: `src/analytics/sm01_solarsim.py`, UNMODIFIED except
the sigma input swap this spec directs._

## Bottom line
**One arm, arm_BLEND_75 (75% incumbent close-only sigma460 / 25% ATR-based estimator),
qualifies as a CANDIDATE** under the pre-registered AND-rule — the first genuinely new Solar-
core mechanism to pass a sub_431/sub_416-style standalone screen since this program's clamp-
ceiling and clock challenges began closing out. It also **passed the conditional old-regime
screen comfortably, not marginally** (net gap +$71.5k vs a −$10k floor; maxDD ratio 0.954 vs a
1.25× ceiling). **Verdict: QUEUE_R2_CONFIRMATION.** No adoption this wave, per spec.

## Motivation (from spec)
sigma460 is a trailing mean of `|Δclose|` and structurally cannot see intrabar wicks — a fast
intrabar spike-and-reversal shows up one bar late or not at all if price round-trips within a
single 3-min bar. An ATR-style true-range estimator captures this directly. Different axis from
SMV2AD/AG (clamp ceiling) and SMV2AE/AF (the clock) — this changes what sigma *measures*,
holding VolMult, clamp bounds, and the 3-minute clock fixed.

## sub_430 — ATR construction + scale measurement (DIAGNOSTIC)
`ATR460_t` = causal trailing-460-bar mean of `TR_t = max(high_t−low_t, |high_t−close_{t−1}|,
|low_t−close_{t−1}|)`, built with the identical warmup/expanding-then-rolling/min_count=30
convention as `sigma_series()`.

**Integrity checks (all passed, independently reproduced by red-team)**: recomputed sigma460
matches SMV2AD's cached series exactly; `TR_t ≥ |Δclose_t|` holds pointwise for every bar;
`ATR460_t ≥ sigma460_t` holds wherever both are finite; 0.72% of bars have `TR == |Δclose|`
exactly (99.3% of bars carry genuine wick information |Δclose| alone cannot see — the premise).

**R_atr = ATR460/sigma460, whole-dev + per-year:**

| scope | n_obs | mean R | p1 | p10 | **p50 (median)** | p90 | p99 |
|---|---:|---:|---:|---:|---:|---:|---:|
| whole_dev | 519,684 | 2.0298 | 1.8610 | 1.9324 | **2.0255** | 2.1333 | 2.2258 |
| 2022 | 117,762 | 2.0143 | 1.8144 | 1.9162 | 2.0138 | 2.1129 | 2.2026 |
| 2023 | 117,715 | 2.0238 | 1.8762 | 1.9328 | 2.0174 | 2.1252 | 2.2202 |
| 2024 | 118,344 | 2.0421 | 1.8547 | 1.9395 | 2.0405 | 2.1527 | 2.2238 |
| 2025 | 117,522 | 2.0382 | 1.8700 | 1.9424 | 2.0324 | 2.1387 | 2.2463 |
| 2026 (partial) | 48,341 | 2.0322 | 1.8706 | 1.9376 | 2.0261 | 2.1367 | 2.2323 |

_(Red-team correction: 2022's p90 corrected from 2.1130 to 2.1129, a rounding fix, immaterial.)_

Regime-stable (per-year medians 2.014–2.041, ~1.3% band across 5 years). `R_atr > 1` throughout,
pre-disclosed as expected (ATR structurally ≥ |Δclose| via the high-low term), not treated as a
result.

**R_SELECTED = 2.025539** (whole-dev median, pre-registered, frozen before sub_431 ran — file
mtimes independently confirmed by red-team as consistent with this ordering).

`sigma_ATR_eff = ATR460 / R_SELECTED`. Scale-isolation check: median(sigma460) = 5.7489pt vs
median(sigma_ATR_eff) = 5.7309pt (ratio 0.9969) — confirms the rescale isolates "does capturing
intrabar range help" from "is a bigger number always going to change behavior."

## sub_431 — replace/blend sweep (4 arms + control)
`sig_arm = w·sigma460 + (1−w)·sigma_ATR_eff`, 13-member VMS unchanged, clamp [40,1200]t
unchanged. Control (w=1.00) reused verbatim from `runs/SMV2AD_VOLMULT_CEILING/out/`; cross-
checked against an independent recompute, max|dev| = $0.000000.

**Standalone battery:**

| arm | w(σ460) | net $ | Sharpe | maxDD $ | CDaR₀.₉₅ $ | top10-day $ | top10 retention | CANDIDATE |
|---|---|---:|---:|---:|---:|---:|---:|---|
| control (σ460 only) | 1.00 | 119,008.9 | 0.7092 | 40,207.6 | 27,161.8 | 117,986.2 | 100.0% | — |
| arm_REPLACE (ATR only) | 0.00 | 118,132.6 | 0.7024 | 35,906.0 | 24,327.2 | 118,700.6 | 100.6% | No |
| arm_BLEND_25 | 0.25 | 111,740.4 | 0.6626 | 37,319.1 | 26,145.2 | 119,192.3 | 101.0% | No |
| arm_BLEND_50 | 0.50 | 113,643.2 | 0.6782 | 42,669.4 | 27,843.9 | 119,138.0 | 101.0% | No |
| **arm_BLEND_75** | **0.75** | **124,968.5** | **0.7455** | 37,250.5 | **25,183.0** | 118,246.7 | **100.2%** | **YES** |

**Verdict rule** (Sharpe AND CDaR₀.₉₅ improve vs control AND top10-retention ≥95%): **only
arm_BLEND_75 qualifies**, with a comfortable margin on every leg (Sharpe 0.7455>0.7092, CDaR
$25,183<$27,162, retention 100.2%). arm_REPLACE has the *best* CDaR of all five arms ($24,327)
but fails on Sharpe alone (0.7024<0.7092, barely). **arm_BLEND_25 fails via Sharpe alone — red-
team correction applied: the original prose claimed arm_BLEND_25's CDaR was "worse than
control," which is factually wrong (its CDaR $26,145.2 is BETTER/lower than control's
$27,161.8, a ~$1,017 improvement — visible in its own adjacent table); only its net and Sharpe
are worse than control.** arm_BLEND_50 fails on all three legs. The relationship across w is
non-monotonic (net: 119,009→124,969→113,643→111,740→118,133 as w goes 1.00→0.75→0.50→
0.25→0.00) — disclosed as a genuine, pre-registered pattern across all 4 arms, not explained
further this wave.

**Churn/flip diagnostic** ("flip-count" = member-level trend-flip count summed over all 13
members and dev bars, from `member_states()`'s own `flip` array — disclosed interpretive call):

| arm | mean flips/member | Δ vs control | mean holding period (bars) | % change vs control |
|---|---:|---:|---:|---:|
| arm_REPLACE | 4,541.5 | +26.1 | 114.44 | +0.58% |
| arm_BLEND_25 | 4,538.8 | +23.4 | 114.50 | +0.52% |
| arm_BLEND_50 | 4,525.5 | +10.0 | 114.84 | +0.22% |
| **arm_BLEND_75** | 4,519.6 | +4.2 | 114.99 | **+0.09%** |
| control | 4,515.5 | — | 115.10 | — |

**The a priori churn concern is NOT confirmed**: even arm_REPLACE (pure ATR, noisiest case)
shows only a 0.58% flip-count increase; arm_BLEND_75 shows a negligible 0.09%. Whatever drives
arm_BLEND_75's improvement, it is not mechanical over-trading from intrabar noise.

**Portfolio blend** (DAYONLY_DUAL6040 60/40, Solar leg swapped, B-MOM unchanged). Control-leg
rebuild reproduces the incumbent champion curve exactly (net $194,416.04 both sides, confirming
correct wiring before trusting any delta):

| arm | net $ | Sharpe | CDaR5 $ | maxDD $ | d_Sharpe vs champion | d_CDaR vs champion | beats champion |
|---|---:|---:|---:|---:|---:|---:|---|
| champion (incumbent) | 194,416.0 | 1.2642 | 14,322.2 | 18,131.7 | — | — | — |
| arm_REPLACE | 196,460.3 | 1.2754 | 13,749.8 | 18,354.5 | +0.0112 | +$572.4 | **Yes** |
| arm_BLEND_25 | 194,221.0 | 1.2570 | 14,373.6 | 19,242.9 | −0.0072 | −$51.3 | No |
| arm_BLEND_50 | 193,135.5 | 1.2582 | 14,969.0 | 19,772.4 | −0.0061 | −$646.8 | No |
| **arm_BLEND_75** | **199,160.4** | **1.2971** | **14,004.1** | 17,956.1 | **+0.0328** | **+$318.2** | **Yes** |

arm_BLEND_75 beats the champion portfolio on both legs. **Flagged observation (does not change
the formal verdict)**: arm_REPLACE also beats the champion at the portfolio level despite
failing the standalone AND-rule — the same pattern SMV2AD saw with its arm_ADD, independently
confirmed by red-team against SMV2AD's own committed artifacts.

## sub_432 — old-regime screen (conditional, triggered by arm_BLEND_75)
**Data check first**: the SM06 hist substrate carries full OHLC (confirmed present, not
close-only) — sub_432 is NOT BLOCKED-BY-DATA.

Rebuilt on 2006-01-05 → 2021-12-31 (1,764,049 **3-minute** post-resample bars — red-team
correction: the original prose said "1,764,049 1m bars," mislabeling its own correctly-tagged
JSON field `n_hist_bars_3m`; the underlying number and every downstream calculation were
unaffected). SMV2H2 gate-B executor convention verbatim. `R_SELECTED = 2.025539` applied as-is
(frozen from dev sub_430, not re-derived on hist — a disclosed methodological choice: re-
deriving R on hist would defeat the purpose of an out-of-sample structural check, mirroring
SMV2AE's own discipline of freezing a rescale factor once).

**Independent cross-check**: the control (w=1.00) hist rebuild reproduces
`runs/SMV2T_NOFAST_R2`'s own committed gate-C incumbent number exactly (net $318,534.28,
Sharpe 0.1846, maxDD $370,365.72) — matched to the last printed digit by red-team's own
independent resimulation, giving high confidence in the pipeline before trusting arm_BLEND_75's
delta.

| arm | net_hist $ | net_incumbent $ | net_gap $ | sharpe_hist | maxDD_hist $ | maxDD_ratio | floor c1 (≥incumbent−$10k) | floor c2 (≤1.25×) | screen |
|---|---:|---:|---:|---:|---:|---:|---|---|---|
| **arm_BLEND_75** | **390,078.2** | 318,534.3 | **+71,543.9** | 0.2256 | 353,212.9 | 0.9537 | **PASS** | **PASS** | **PASS** |

**arm_BLEND_75 passes the old-regime screen comfortably, not marginally** — net gap +$71.5k vs
a −$10k floor, and maxDD is actually *lower* than the incumbent's on the old regime (ratio
0.954, floor allowed up to 1.25×). Per house history, 3 of 5 prior core-challenge candidates
died specifically on this floor — this one clears it with margin on both legs. (DIAGNOSTIC/non-
adoption this wave — informs the priority of the queued R2_CONFIRMATION only.)
_(Red-team correction: the JSON's `hist_window` end date typo "2021-12-21" corrected to
"2021-12-31," matching the prose and the actual reproduced window — no computation affected.)_

## kill_or_keep
**1/4 arms qualified in sub_431 (arm_BLEND_75), which also cleared sub_432's old-regime screen
with margin.** Per spec: this queues a full SMV2T-style R2_CONFIRMATION battery (bootstrap
significance, LOYO chronology, right-tail retention, formal portfolio gate) in a later wave.
**No adoption is claimed or implied this wave.**

## Honest scope limits
- Only w=0.75/0.50/0.25/0.00 tested (a small, pre-registered 4-cell grid) — no finer search
  around w=0.75 was attempted, and none should be inferred as "the optimum."
- The non-monotonic net/Sharpe pattern across w is disclosed, not explained.
- Bootstrap significance, LOYO year-by-year robustness, and a formal (non-diagnostic) portfolio
  gate were NOT run this wave — explicitly the queued R2_CONFIRMATION's job.
- R_SELECTED applied to hist without re-derivation, a disclosed methodological choice, not a
  sensitivity-tested one.
- No data ≥2026-06-01 read anywhere.

## Red-team disposition
Verdict: **CONFIRMED-with-corrections**. Every quantitative claim independently re-derived from
raw data using the unmodified core simulator — ATR/sigma construction and causality, the full
4-arm sweep (standalone + portfolio + churn), AND-rule application, and the full old-regime
rebuild — reproduced exactly. No lookahead, no leakage, no gate-shopping, no placebo tricks.
arm_BLEND_75 genuinely and uniquely qualifies and genuinely clears the old-regime screen with
margin; QUEUE_R2_CONFIRMATION is the correct verdict. Five corrections applied above (all
cosmetic/prose — the arm_BLEND_25 CDaR mischaracterization is the only substantive one, and it
does not change that arm's correct non-candidate status); this REPORT.md resolves the missing-
deliverable gap red-team flagged.

## Files
`out/atr_construction.csv`, `out/atr_construction_meta.json`, `out/scale_ratio_atr.csv`,
`out/replace_blend_sweep.csv`, `out/churn_comparison.csv`, `out/portfolio_blend.csv`,
`out/portfolio_curves_431.csv`, `out/old_regime_screen.csv`, `out/gates.csv`,
`out/sub431_verdict.json`, `out/daily_arm_*.csv`, `out/daily_control_w1.00.csv`,
`out/sigma460_dev.npy`, `out/atr460_dev.npy`, `out/sigma_atr_eff_dev.npy`. Code: `src/common.py`,
`src/step1_atr_construction.py`, `src/step2_sweep.py`, `src/step3_old_regime.py`, `src/finalize.py`.
