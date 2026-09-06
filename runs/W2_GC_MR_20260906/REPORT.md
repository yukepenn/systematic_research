# W2_GC_MR_20260906 — GC daily buy-the-washout MEAN-REVERSION (trial G00060)

**2026-09-06 · CROSS_ASSET Wave-2 (native money-engines) · Stage-5 falsifier.**
Judged to the P1 bar: **in-sample + robustness, NO forward-freeze** (owner doctrine). Evidence
status **DISCOVERY_CONSUMED**. No P&L promotion, no deploy, no sizing change; live book `2047681`
untouched; $0. Substrate: `runs/DAILY_GC_EXTRACT_AUTOPSY_20260906/out/gc_daily.parquet`. Code:
`src/gc_mr.py`. Program-printed gates: `out/gate_table.txt`. Figures reproduce from `out/run_log.txt`.

## 0. Verdict — DRIFT-EXPLAINED. Does NOT survive.

**SURVIVES = False.** The dip-buy apparent money is the secular **+7.6 %/yr gold drift** harvested by
being long ~47 % of days, not a liquidation-overshoot timing edge. The primary kill test (G2, the
exposure-matched / drift-matched always-long control) is **not passed**, and three independent reads
agree. Cost is not the binding constraint — the autopsy called that correctly — but the edge itself is
not distinguishable from zero.

| Gate | Spec | Observed | Verdict |
|---|---|---|---|
| **G0** | seal `<2026-08-01`; returns=ratio, level=points | max `2026-07-31`, seal_ok, basis not mixed | **PASS** |
| **G1** | MDE(80%,a=.05) printed before observed | MDE **+3.152** vs obs **+1.574** bps/day | **FAIL** (below MDE) |
| **G2** | drift-control SPREAD: CI excl 0 and circular-shift null | 95% CI **[-0.54, +3.55]** bps/day (incl 0); shift-null p=0.026 | **FAIL** |
| **G3** | 3x3 (threshold x H) plateau, not a magic cell | 6/9 positive but incoherent; H=1 row not all-positive | **FAIL** |
| **G4** | edge on weekly-vol basis, not fixed-DD-only | vol-matched edge **-$111/wk**; engine underperforms control | **FAIL** |
| **G5** | positive spread in BOTH eras | +3.57%/yr (t 0.76) and +4.37%/yr (t 1.26) | PASS (sign-only, underpowered) |
| **G6** | cost-robust across {0.5,1,2} tick at realistic tick | point spread >0 through 2 tick; cost erodes only 0.25 bps | PASS (cost not binding) |
| **G7** | rho-to-P1 daily PnL printed | rho **+0.043** Pearson / +0.070 Spearman (1009 days) | PASS |

**Decision rule (G2+G3+G4+G6): NOT SUPPORTED.** G2, G3, G4 all fail. FAILURE_MEMORY row.

## 1. The mechanism, exactly as preregistered

Entry LONG at the close of a washout day; hold **H** days (capped single-unit — long iff a washout
fired in the last H days, so exposure <= 1 contract, no leverage creep); exit at close. Threshold in
{0 = any down day, -1s, -2s of trailing-63d daily return}; H in {1,2,3}. **Anchor cell = (any-down,
H=1)** — the autopsy directly-measured signal (prior-day-DOWN -> +6.98 bps, t 2.94). The reported edge
is the **SPREAD over the exposure-matched always-long control**: per in-market day, subtract the
unconditional mean daily return mu (= **+3.01 bps/day**, the +7.6%/yr drift). The control has ~zero
turnover and pays ~zero cost; the dip-buy pays its own transaction cost — the conservative comparison.

**Basis discipline:** signal sigma and returns on the ratio series (`ret_pct`); dollar P&L =
`ret_points x PV` = `ret_pct x (PV*close_prev)` — the actual era-correct P&L of 1 contract, never a
%-return manufactured from levels. Seal `>=2026-08-01` hard-dropped at load (asserted). PV=$100/point,
tick=$10, commission $4.36/RT (MODELED, FLAGGED — no GC cost is measured in this repo).

## 2. Why it is drift, not timing — the 3x3 surface is the tell

After-cost drift-control spread (bps/day), base cost $14.36/RT (1-tick spread + comm):

| threshold / hold | H=1 | H=2 | H=3 |
|---|---|---|---|
| **any-down** (f~47%) | **+1.57** | +1.36 | +0.47 |
| **-1 sigma** (f~12-33%) | +0.32 | +0.78 | +0.95 |
| **-2 sigma** (f~3-10%) | **-0.34** | -0.24 | -0.26 |

The hypothesis — forced-liquidation overshoots revert — predicts the deepest washouts (-2s) should
revert hardest. The data says the opposite: **-2s is negative at every hold** (136 events, next-day
continuation, consistent with the autopsy violent negatively-skewed down-tails). The only positive
spread lives at the shallow "any down day" threshold, which is exactly where you are simply long ~47%
of the time and harvesting drift. There is no contiguous plateau; the sign flips and the H-dependence
is incoherent across thresholds. **G3 FAIL, and it is a mechanism refutation, not a tuning miss.**

## 3. The primary kill test (G2) and the two-way disagreement it exposes

Anchor cell after-cost mean daily spread **+1.574 bps/day (+3.97%/yr)**, below the pre-printed
**MDE +3.152 bps/day** (underpowered to detect an effect this size at 80% power).

- **Block-bootstrap 95% CI (L=10, B=5000): [-0.54, +3.55] bps/day — includes 0.** => CI clause FAILS.
- **Circular-shift null (B=5000, dependence-preserving): two-sided p = 0.026** — nominally clears.
- Matched-count random-entry control: p = 0.010.

Per the CAP01 doctrine (a headline that is an edge/probability must be computed a second way, and when
the two disagree do not over-claim), the two nulls disagree: the shift-null asks "is the conditional
mean bigger than random signal placement gives?" (marginally yes), while the sampling-CI asks "is the
mean itself distinguishable from 0?" (no). The conservative, standard sampling read wins: **G2 FAIL**.
There may be a whisper of timing information, but it does not survive as a CI-clean, plateau-backed,
vol-efficient edge.

## 4. Weekly-vol basis (G4) — the engine is vol-inefficient vs just being long

`eval_battery`, LED WITH WEEKLY-VOL, engine (after cost) vs exposure-matched drift-control, 872 shared
ISO weeks:

- engine native **$333/wk**, but **weekly-vol-matched $8/wk** vs control native **$119/wk** ->
  **weekly-vol edge -$111/wk**. The engine only wins natively because it is more volatile (bunched
  in-market with big swings); equalize vol and the edge is negative.
- Weekly SPREAD series **+$214/wk** but sd **$3,359** (weekly-vol Sharpe ~0.46).
- Fixed-DD spread income **$238/wk** sits at only the **74.6th percentile** of its own side-blind
  10%-thinning placebo (shown only beside the placebo, per the T2 lesson) — not a robust separation.

Engine book (deployable, 1 GC contract, after cost): $333/wk, **Sharpe 0.72**, maxDD **$52,024**,
ret/DD 5.58, worst-week -$37,494, **worst-month -$17,006**, pos-week 59.5% — a modest long-gold book
whose Sharpe is essentially buy-and-hold (~0.45) plus a sliver, i.e. the drift.

## 5. Cost (G6) and orthogonality (G7)

- **Cost is not binding**, exactly as the autopsy predicted (~10x under the edge): the point-estimate
  spread stays positive through **2 ticks** (+1.66 -> +1.41 bps/day across 0.5->2 tick; cost removes
  only **0.25 bps/day**). The run misses a significance bar because of the G2 power failure, not
  friction — do not mislabel this COST-FRAGILE.
- **rho(GC-MR engine, P1) = +0.043 Pearson / +0.070 Spearman** over 1009 shared days (2022-07 ->
  2026-07), both-traded-day share 28.6%. The engine is near-orthogonal to the live P1 book — the
  diversification prize is real — but a book with no CI-distinguishable, drift-independent edge carries
  no marginal portfolio value; rho~0 to zero is still zero. `out/daily_pnl.csv` (engine after-cost $,
  plus the spread and control decompositions) is written for the Wave-6 portfolio step, which should
  treat this engine as **not carried** given the verdict.

## 6. Reproduction / provenance

P1 daily PnL reproduced exactly from the validated bench (`xinst_bench.build_p1pct`, NQ substrate, PV
20, box 65/50 pts) — 1056 days, spread **$14.436/ctrRT** matching the documented $14.44. GC substrate:
4,347 raw -> 18 gap-spanning dropped -> **4,329 clean** daily rows 2009-03-31 -> 2026-07-31; evaluation
window post-63d sigma warmup = 4,266 days. Deliverables: `out/gate_table.txt`, `out/neighborhood.csv`,
`out/walkforward.csv`, `out/daily_pnl.csv`, `out/summary.json`, `out/run_log.txt`.

_No deviations from spec.yaml. One reconciliation worth recording: the spec "cost-fragile" language and
the observed result decoupled — cost is robustly non-binding, so the failure is attributed to the
drift-control kill test (G2), not to friction._