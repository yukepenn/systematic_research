# W2B_EQMR_20260906 — REPORT

**Trial G00063, family `CROSS_ASSET_NATIVE`.** Stage-5 falsifier of Wave-2's strongest lead: the
raw equity-index daily mean-reversion engine (ES lead; YM, RTY extension). POINTS basis,
additively back-adjusted (DELEV01), 2022-07-01 → 2026-07-31 daily RTH. Judged to the P1 bar
(in-sample + robust, **no forward freeze**). **NO deploy. DISCOVERY_CONSUMED.**

Program: `src/eqmr.py`. Machine-printed gate table: `out/gate_table.txt`. Full log: `out/run_log.txt`.

---

## Verdict: **FAIL** — but *not* the drift-explained failure, and this distinction is the finding

No instrument survives the pre-registered falsifier. `survives = False` for ES, YM, RTY.
The engine is **not** carried to portfolio assembly. The reason it fails is **statistical power
plus non-orthogonality**, *not* captured equity drift — the CO-PRIMARY drift-control kill test
actually **vindicated** the reversion mechanism. Calling this "DRIFT-EXPLAINED" would be a
mislabeled statistic (the CAP01 rule, CLAUDE.md §4).

| gate | ES | YM | RTY |
|---|---|---|---|
| G0 reproduce raw-ES control | **PASS** ($370.2158/wk, Sharpe 0.7769 vs target $370.22 / 0.777) | — | — |
| G1 spread MDE (before observed) | $597/wk (obs $409, **BELOW**) | $393/wk (obs $348, **BELOW**) | $307/wk (obs $206, **BELOW**) |
| **G2 drift-control spread (CO-PRIMARY KILL)** | **FAIL** | **FAIL** | **FAIL** |
| G3 neighborhood plateau (>=60% spread>0) | PASS (12/12) | PASS (12/12) | PASS (12/12) |
| G4 weekly-vol edge (fixed-DD w/ placebo) | PASS | PASS | PASS |
| G5 both walk-forward eras spread>0 | PASS | PASS | PASS |
| **G6 PnL-rho-to-P1 (CO-PRIMARY VALUE)** | +0.226 | +0.201 | +0.131 |
| G7 cost-robust {1,2}tk | FAIL (G2 fails at both) | FAIL | FAIL |

---

## G0 — reproduce first (the port-validation discipline)

The Wave-2 `raw-ES MR control` (W2_EQRESID G00061, primary W=60 z=1.5 cost=1tk) reproduces to
the cent: **$370.2158/wk, Sharpe 0.7769** (target $370.22/wk, Sharpe 0.777; dwk -$0.004,
dSharpe -0.0001), 37 trades over 1,053 aligned ES RTH sessions. The lead is trustworthy; the run
is valid. Same mechanism, same seal, same P1 bench (P1/PCT reproduced at 2,401 trades,
$14.436/ctrRT, $1,393.57/wk). See `out/reproduce.txt`.

## G2 — the CO-PRIMARY kill test, and why it is not drift

The engine's **net signed exposure `c = mean(pos)` is negative on all three instruments**
(ES -0.102, YM -0.247, RTY -0.035): over 2022-2026 the raw fade is net-**short**-biased. The
exposure-matched always-long control (a constant `c`-position buy-and-hold) therefore *loses*
money — **-$38.55/wk (ES), -$82.88 (YM), -$3.60 (RTY)** — because holding net-short into an
up-drifting equity tape bleeds drift. The drift-free timing **spread** = engine - control is thus
*larger* than the engine's own return:

| | engine $/wk | drift-control $/wk | **spread $/wk** | spread Sharpe | p_block | Bonf-lo (1.67pct) | p_circ (2000-shift) |
|---|---|---|---|---|---|---|---|
| ES | 370.22 | -38.55 | **408.76** | 0.839 | 0.041 | -$61 | **0.012 (clears)** |
| YM | 265.44 | -82.88 | **348.32** | 1.089 | 0.025 | **+$15** | **0.0005 (clears)** |
| RTY | 202.13 | -3.60 | **205.73** | 0.822 | 0.038 | -$21 | 0.0195 (misses) |

This is the **opposite** of the GC-MR drift-explained mode (where the control captures the
engine's return and the spread collapses to ~0). Here the drift is a *drag* and the spread is the
whole story — genuine reversion *timing* covariance `cov(pos,ret)*PV`.

**Why it still FAILS G2:** the block-bootstrap CI of the weekly spread does **not** exclude 0 at
the family-Bonferroni bar (alpha = 0.05/3 = 0.0167 one-sided). Spread Sharpe ~0.8-1.1 over 214
weeks is a t ~ 1.7, short of the Bonferroni t ~ 2.13; observed spreads sit **below** their own
80%-power MDE ($307-597/wk). The circular-shift null — a *second, independent* computation of the
same "timing-beyond-drift" event (its null centers exactly on the drift-capture level) — **is
cleared for ES (0.012) and YM (0.0005)** but the block-boot leg is the binding one, and the
pre-registered rule requires **both**. RTY additionally misses the circ-null (0.0195 > 0.0167).
Underpowered near-miss, recorded as failed — the population is never redefined after the result.

## G6 — the value test: not a diversifier

PnL-rho to the reproduced P1 daily series is **positive** everywhere: **ES +0.226, YM +0.201,
RTY +0.131**. Even a net-short equity fade comoves *with* the long-NQ momentum book, because its
profitable long-side days (buy the dip -> bounce) coincide with P1's up-days. RTY is the least
correlated but still positive and its edge is the weakest/least significant. **None delivers the
low/negative rho that would make it portfolio-additive.** The diversification prize is not won.

## G3 / G4 / G5

Robust on the descriptive bases (these are *not* the binding gates): every one of the 12 W×k×cost
cells per instrument shows spread>0 (plateau, no magic cell); the edge is present on weekly-vol
(vol-matched spread +$13 to +$169/wk), not a fixed-DD artifact (fixed-DD reported *with* its
side-blind random-thinning placebo — the thinning lift is *negative*, so the DD figure is not
manufactured); and the spread is positive in both walk-forward eras (notably stronger in
2025-2026: ES $865/wk, YM $633/wk). A genuinely suggestive but uncertifiable signal.

---

## Classification & disposition

- **Improvement class:** would-be NEW INFORMATION (daily reversion timing), but **unproven** at
  this N. Not promoted.
- **DRIFT-EXPLAINED?** No. Drift is a -$4 to -$83/wk drag; the spread exceeds the engine. The
  kill test cleared the mechanism.
- **Diversifier?** No. rho-to-P1 = +0.13 to +0.23, positive.
- **FAILURE_MEMORY row:** raw equity-index daily fade — drift-free timing spread $206-409/wk,
  Sharpe 0.8-1.1, circ-null cleared (ES/YM) — **underpowered at N=214wk vs family-Bonferroni AND
  positively correlated with P1**. Reversion is real but small and not orthogonal; a longer or
  pooled cross-sectional formulation, or a genuinely orthogonal (index-neutral) construction,
  would be the only way to revisit. DISCOVERY_CONSUMED; no deploy.
- **Best instrument (formal, for the would-be portfolio step):** **YM** — closest to surviving
  the CO-PRIMARY kill (block-boot p 0.025, circ-null 0.0005, Bonf-lo **positive** +$15/wk, the
  only instrument with neighborhood G2 passes: 2/12 cells). A diversifier without an edge is
  useless, so significance leads the tie-break; note RTY has the lowest rho (+0.131) but the
  weakest, non-circ-null-clearing edge. `out/daily_pnl_YM.csv`.

## Deliverables

`out/reproduce.txt` - `out/gate_table.txt` - `out/neighborhood.csv` -
`out/daily_pnl_ES.csv` - `out/daily_pnl_YM.csv` - `out/daily_pnl_RTY.csv` - this `REPORT.md`.

Seal: every bar >= 2026-08-01 hard-dropped at load and asserted (all substrates end 2026-07-31).
Costs ALL_IN single-leg: comm $4.36/ctrRT **MODELED (flagged)** + spread {1,2} ticks
(ES $12.50/tk, YM $5.00/tk, RTY $5.00/tk).
