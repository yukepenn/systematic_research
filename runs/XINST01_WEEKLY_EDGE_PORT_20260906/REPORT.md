# XINST01 - WEEKLY_EDGE cross-instrument port of P1/PCT (ES / RTY / YM / ZB)

**Run:** `XINST01_WEEKLY_EDGE_PORT_20260906` - registered 2026-09-06 - spec committed before results.
**Stage:** DISCOVERY on new instruments. A per-instrument PASS is **INFORMATION-SUPPORTED at best**
(in-sample, `DISCOVERY_CONSUMED`); it licenses a forward-validation queue entry, never a promotion or
a live deploy. **Nothing here promotes, sizes, or enables anything.**

---

## G0 - PORT VALIDATION (the hard gate, PASSED)

The parameterized bench (`src/xinst_bench.py`) is **not a fork** - it imports the incumbent's exact
building blocks (`sm14_1m` 13-member ratchet, `votes`, `fills_daily`, `causal_score`, `gfills`,
`fast_build_context`) and substitutes only per-instrument scalars. Instantiated on NQ with NQ's own
PV/commission/spread, it reproduces the committed P1/PCT figures **exactly** (`out/port_validation.txt`):

| metric | REBUILT | COMMITTED (WE_W103) | rel diff |
|---|---:|---:|---:|
| weekly $ | 1393.573663 | 1393.573663 | **0.0000%** |
| max DD $ | 22930.665853 | 22930.665853 | **0.0000%** |
| t | 4.163612 | 4.163612 | **0.0000%** |
| trades | 2401 | 2401 | **0.0000%** |
| spread $/ctrRT | 14.436483 | 14.436483 | **0.0000%** |

Rebuilt `mem`/`bmom`/`tilt` ratchet arrays are **bit-identical** to the committed `WE_W76/mem_ext.npz`
cache (0 / 21,060,572 mismatches). Reproducing the incumbent is the whole license to trust the ports.

---

## The no-mining transfer rule

**Kept identical (never refit):** every ATR-normalized Solar feature, the day/quantile params
(EntryLevel=3/ExitLevel=1, range-throttle quantiles, QualWindow=250/QualMinHist=100, ForcedFlat=21,
tilt params, VolPeriod=460, WSolar/WBmom), the causal-score quantiles, the 09:31/16:00 RTH B-MOM
clock, flat-at-close. **NOTHING in the signal is per-instrument optimized.**

**Transferred by PERCENTILE (recorded BEFORE any port P&L):** the session box. On NQ,
**65 pts halt = 0.57th percentile** and **50 pts target = 0.19th percentile** of NQ's session
point-range distribution (median 294.8 pts). Each instrument's box is set to the SAME percentiles of
ITS OWN session point-range distribution:

| root | halt pts ($) | target pts ($) | session-range median (pts) |
|---|---:|---:|---:|
| ES | 12.00 ($600) | 9.49 ($475) | 63.4 |
| RTY | 9.19 ($459) | 7.59 ($380) | 38.4 |
| YM | 107.59 ($538) | 88.80 ($444) | 453.0 |
| ZB | 0.375 ($375) | 0.282 ($282) | 1.0625 |

**Per-instrument scale facts (not tuned):** PV, tick, commission $4.36/ctrRT, modeled spread (1 tick
realistic; 0/1/2/3-tick band reported). ZB is on a **POINTS (32nds) basis**: 1 pt = 32 ticks,
$/tick = PV*tick = $31.25, additively back-adjusted (DELEV01) - asserted.

---

## Per-instrument verdicts

Family: N = 4, Bonferroni bar **p <= 0.0125** on the primary (weekly-vol net, t vs a
dependence-preserving moving-block bootstrap L=4, 20k). Lead statistic is **weekly-vol** matched to
NQ P1/PCT's weekly volatility (so $/wk is comparable to the incumbent $1,394). fixed-DD is shown only
beside its side-blind random-thinning placebo (eval_battery raises otherwise).

### ES - CLOSED-BY-POWER
weekly-vol **+$193.50/wk**, native +$110.67/wk, t 0.578, bootstrap p **0.244** (FAIL Bonferroni),
below MDE ($590/wk @ 80% power). Cost-robust through 1 tick (2-tick negative). **Daily-PnL rho vs P1
= +0.654** (weekly +0.645, both-traded-day 50.2%, DD overlap 0.20). Positive point estimate the
sample cannot separate from zero, and it is **largely NQ beta** - generalization, not diversification.

### RTY - COST-FRAGILE
weekly-vol **-$211/wk at 1 tick**, positive **only at 0-tick (+$32)**. native -$64/wk, t -0.63,
p 0.78. Survives only at zero spread => not a candidate. rho vs P1 daily +0.274.

### YM - CLOSED-BY-POWER
weekly-vol **+$154.48/wk**, native +$56.65/wk, t 0.460, bootstrap p **0.303** (FAIL Bonferroni),
below MDE ($380/wk). Cost-robust through 1 tick. rho vs P1 daily +0.239. Same as ES: small,
insignificant, NQ-correlated positive drift.

### ZB - FAIL  (the a-priori diversification prize)
weekly-vol **-$4,179/wk**, native **-$796/wk**, t **-10.02**, bootstrap p **1.000** - a **powered,
highly significant NEGATIVE** edge (negative even at 0-tick, -$1,099). **ZB is genuinely orthogonal to
P1** (daily rho **-0.048**, weekly rho -0.139, DD-overlap Jaccard **0.032**) - exactly the
diversification profile the run hunted for - **but the mechanism anti-transfers to rates**: the
volatility-ratchet momentum engine loses money robustly on Treasuries. Orthogonality is real and
useless because the edge is negative. **No XM replacement emerges from this known mechanism.**

---

## G6 semantic sentences (population - window - what the number is - evidence tag)

- **ES:** Over 213 ISO weeks in 2022-07-01..2026-08-01 on ES 1-min bars (pre-seal, DISCOVERY_CONSUMED,
  in-sample), the after-cost weekly-vol-matched net (levered to NQ P1's weekly vol) is **+$193.50/wk**;
  it is the mean weekly P&L of the ported P1/PCT mechanism, **not** a forward or live figure.
- **RTY:** Same population/window (212 wk); weekly-vol net **-$211/wk at 1-tick spread** (+$32 only at
  0-tick); in-sample DISCOVERY_CONSUMED; not a forward/live figure.
- **YM:** Same population/window (212 wk); weekly-vol net **+$154.48/wk**; in-sample DISCOVERY_CONSUMED;
  not a forward/live figure.
- **ZB:** Over 161 ISO weeks in 2023-07-01..2026-08-01 on ZB 1-min bars (POINTS/32nds basis, pre-seal,
  DISCOVERY_CONSUMED, in-sample), the after-cost weekly-vol-matched net is **-$4,179/wk**; it is the
  mean weekly P&L of the ported mechanism, **not** a forward or live figure.

---

## What this run establishes (FAILURE_MEMORY)

**P1/PCT's edge is NQ-specific / equity-index-shaped and NQ-strongest. It does not transfer as a
positive, significant, cost-robust edge to any of ES, RTY, YM, or ZB at scale, and it inverts hard on
rates (ZB).** The two equity indices most like NQ (ES, YM) show a small positive drift that is (a)
statistically indistinguishable from zero on 4+ years, and (b) mostly the same NQ move (rho 0.24-0.65)
- generalization, not diversification. The genuinely orthogonal instrument (ZB) carries a large
negative edge. **The diversification the XM withdrawal removed is NOT restored by porting this
mechanism.** Clean answer to the spec's "structure or NQ-specific" question: **substantially NQ-specific.**

**Decision:** zero INFORMATION-SUPPORTED candidates -> **no forward-validation queue entry, no
promotion, no live deploy, no sizing change.** All four recorded, corrected (Bonferroni + BH), whatever
the outcome. Evidence status **DISCOVERY_CONSUMED, in-sample** throughout.

---

## Deviations / interpretations from the literal spec (transparent)

1. **Ratchet volatility clamps SMIN/SMAX/STOPM were scaled by the instrument's volatility ratio**
   (V_inst/V_nq, V = mean |1-min dClose| in-session). The spec named only the box as scale-dependent,
   but sm14_1m's clamps are POINTS-denominated (NQ 10/300/44.75 pts) and the W43 hook
   (smin_pts/smax_pts/stopm_pts) exists precisely so a non-NQ instrument passes its own volatility-
   derived values. Leaving them fixed is itself a scale-dependent choice that breaks scale-invariance -
   catastrophically for ZB (a 10-pt NQ clamp = 320 ZB ticks would freeze the ratchet). Scaling by the
   volatility ratio makes the clamps the SAME multiple of typical volatility on every instrument - a
   scale normalization with **zero free parameters**, computed once and recorded before P&L. Faithful
   extension of the spec's scale-invariance ethos, not a per-instrument fit.
   Ratios: ES 0.216, RTY 0.130, YM 1.507, ZB 0.0045.
2. **Weekly-vol reference = NQ P1/PCT weekly series**, so reported $/wk is comparable to the $1,394
   incumbent. Sign and t are scale-invariant, so this cannot change any gate verdict.
3. **Dependence-preserving null = moving-block bootstrap (L=4 weeks, 20k draws) of the centered weekly
   series** - the spec's "circular-shift / block-bootstrap" option (a per-draw signal circular-shift
   over 1.6M bars x thousands of draws was infeasible; weekly PnL autocorrelation is low so the block
   bootstrap is close to and slightly more conservative than the analytic t).
4. **Commission +-50% sensitivity computed post-hoc** (each trade's P&L shifts by (4.36-c)*u); the
   second-order box-trigger shift is negligible and ignored.
5. **ZB analysis window starts 2023-07-01** (6-month warmup from the 2022-12-26 data start), mirroring
   NQ's ~6-month warmup before its 2022-07-01 window; ES/RTY/YM use 2022-07-01 identically to NQ.
6. ES caveat carried per spec seal note: ES cross-market was consumed by the closed ESNQ scope, so ES
   results are not cited for/against ESNQ.

## Deliverables
- out/port_validation.txt - exact NQ reproduction proof (G0).
- out/gate_table.txt - program-printed GATE/SPEC/OBSERVED/PASS-FAIL per instrument.
- out/per_instrument.csv - weekly net by basis, t, MDE, cost band, orthogonality.
- out/orthogonality.csv - daily/weekly rho vs P1, trade & DD overlap.
- out/run_log.txt - full program transcript.
- src/xinst_bench.py, src/g0_validate.py, src/run_xinst.py - the parameterized bench and drivers.
