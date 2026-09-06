# W2B_GCVOL - vol-targeted long-gold DIVERSIFICATION SLEEVE (trial G00064)

**Run:** `W2B_GCVOL_20260906` - registered 2026-09-06, spec committed before results.
**Stage:** Stage-5 PORTFOLIO-DIVERSIFICATION test, **NOT an alpha test**. Judged on the portfolio delta.
**Family:** `CROSS_ASSET_NATIVE`, one trial (`G00064`).
**Verdict: NEUTRAL - gold does not earn a vol-managed sleeve.** `survives = False`.
Evidence status: **in-sample, DISCOVERY_CONSUMED. No deploy, no sizing change, no promotion.**

> This is a **diversification** question, never "alpha": does a vol-targeted long-gold sleeve add
> portfolio value to the NQ/P1 book? Gold's edge is its secular drift (buy-hold Sharpe ~0.42 here),
> not reversion (GC-MR / G00060 already failed that). The sleeve is labeled DIVERSIFICATION throughout.

---

## Reproduce-gate (the license to trust every portfolio number)

The NQ/P1 daily PnL is reproduced from the XINST01 parameterized bench (`xinst_bench.py`), which
imports the incumbent's exact building blocks. It reproduces the committed WE_W103 P1/PCT **exactly**:

| metric | rebuilt | committed WE_W103 | rel diff |
|---|---:|---:|---:|
| weekly $ | 1393.573663 | 1393.573663 | **0.0000%** |
| max DD $ | 22930.665853 | 22930.665853 | **0.0000%** |

Seal asserted on both series: gold max session **2026-07-31**, NQ max session **2026-07-31**, both
`< 2026-08-01`. Nothing virgin is materialized. `ret_pct` on the ratio-stitched (%-safe, DELEV01) GC
series, `clean_daily` rows only (4,329 returns, 2009-03-31 -> 2026-07-31).

---

## The sleeve mechanism (spec `mechanism_rule`, verbatim, fully causal)

`w_t = clip( target_vol_t / trailing-N-day realized vol_t , 0, 2 )`, long gold, `N in {21, 63}`.
Both terms strictly past-only:

- **trailing** `rv_N[t]` = std of returns over `[t-N, t-1]` (`.shift(1)`).
- **target** `[t]` = **expanding-window** std over `[0, t-1]` (`.shift(1)`) - the buy-hold's *own*
  realized vol, **NOT full-sample** (Cederburg discipline), **not tuned to returns**.
- Active only after >= 252 past obs (1yr) AND a full N-window: 4,077 days, 2010-05-07 -> 2026-07-31.

The expanding target makes mean exposure land near 1 by construction (N=21 mean w **1.225**, N=63
mean w **1.162**; clipped-at-2 3.9%/0.1%, never clipped-at-0). Because both terms scale by
`sqrt(252)`, annualization cancels in the ratio - zero free parameters.

---

## GATE / SPEC / OBSERVED / PASS-FAIL (program-printed - `out/gate_table.txt`)

| gate | observed | verdict |
|---|---|---|
| G0a seal (gold < 2026-08-01) | 2026-07-31, n=4329 clean | **PASS** |
| G0b NQ P1/PCT reproduced exactly | weekly $1393.5737, maxDD $22930.67 | **PASS** |
| G1[N=21] matched-exp beats buy-hold on ret/DD **and** worst-mo | ret/DD 0.108 v 0.131; worst-mo better | **FAIL** |
| G1[N=63] matched-exp beats buy-hold on ret/DD **and** worst-mo | ret/DD 0.124 v 0.131; worst-mo better | **FAIL** |
| G2[N=21] sleeve daily rho-to-P1 printed | **+0.106** | PASS (printed) |
| G2[N=63] sleeve daily rho-to-P1 printed | **+0.103** | PASS (printed) |
| G3[N=21] NQ+gold materially improves Sharpe **and** ret/DD | eq +0%/-21%, fx +7%/-8% | **FAIL** |
| G3[N=63] NQ+gold materially improves Sharpe **and** ret/DD | eq +5%/-12%, fx +10%/+8% | **FAIL** |

**SURVIVES = (G1 matched-exp beats buy-hold) AND (G3 portfolio-additive) = False.**

---

## G1 - the vol-management is NOT a better gold (leverage-masquerade guard, VOLSIZE01)

At **matched mean exposure** (sleeve rescaled so mean w = 1 = buy-hold), on compounded equity:

| series (N=63) | CAGR | maxDD | ret/DD | worst-month | Sharpe |
|---|---:|---:|---:|---:|---:|
| buy-hold gold | 5.79% | 44.18% | **0.131** | -12.39% | 0.418 |
| sleeve (raw, mean-exp 1.16) | 6.34% | 51.23% | 0.124 | -14.24% | 0.434 |
| sleeve (**MATCHED** exp) | 5.64% | 45.32% | **0.124** | **-12.26%** | 0.434 |

The vol-targeting buys a **slightly better worst-month** (-12.26% vs -12.39%) and a hair more Sharpe
(0.434 vs 0.418), but **loses on ret/DD** (0.124 < 0.131) because it sizes *up* into low-vol regimes
that then draw down (maxDD 45.3% > 44.2%). The raw sleeve's apparent edge is mostly the extra 16%
mean exposure; the guard removes it. **G1 FAIL both N.** N=21 is worse (matched ret/DD 0.108).

Eval battery (weekly grid, sleeve income risk-matched to buy-hold, return units, **weekly-vol lead**):
N=63 weekly-vol **0.001372/wk** > buy-hold - i.e. the sleeve earns slightly more per unit of weekly
vol, but that is a *vol-matched* statement; on the spec's stated basis (ret/DD + worst-month at matched
**exposure**) it does not clear buy-hold. fixed-DD shown only beside its placebo (N=63: 0.001271/wk vs
side-blind 10%-thin median 0.001363/wk, placebo pct 41.6 - the fixed-DD figure is *below* its own
thinning placebo, so no order-statistic illusion is helping it).

---

## G2 - orthogonality: rho-to-P1 is **+0.10, not the expected ~0.04**

Over the 1,009 shared trading days (2022-07 -> 2026-07), the **sleeve daily rho-to-P1 = +0.103** (N=63),
+0.106 (N=21); buy-hold gold rho-to-P1 = +0.102. The spec's "expect ~0.04" came from the **full-history
(2009-2026) gold-vs-NQ-index** correlation (manifest: pearson 0.0744 / spearman 0.0449). Two reasons it
reads higher here: (1) the actual overlap window is the P1 window **2022-2026**, where gold-equity
co-movement ran higher than the 17-yr average; (2) P1 is a long-biased NQ *strategy*, not the index.
Gold is still a *low*-correlation asset to P1 (rho ~0.10, worst-decile-day Jaccard **0.058-0.069**) -
just not as orthogonal as the pre-registered guess. Recorded as a deviation-from-expectation.

---

## G3 - portfolio delta (the actual deliverable): a sub-threshold, non-robust lift

NQ/P1-alone vs NQ/P1 + gold sleeve, two transparent (un-optimized) sizings. **Ratios are
scale-invariant, so they are identical on the research full-size and the live P1-object (MnqPerNq=3,
0.30x) bases**; only absolute $ differ by 0.30x. Research full-size $ shown:

| book (N=63) | Sharpe | maxDD $ | ret/DD | CDaR $ | worst-mo $ | roll-12m-min Sharpe |
|---|---:|---:|---:|---:|---:|---:|
| **NQ-alone** | 1.928 | 27,908 | **10.355** | 20,117 | -15,274 | **-0.102** |
| NQ+gold (equal-risk) | 2.026 (+5.1%) | 49,434 | 9.125 (-11.9%) | 35,255 | -24,888 | +0.318 |
| NQ+gold (fixed-vol 0.5x) | 2.123 (+10.1%) | 32,940 | 11.234 (+8.5%) | 26,283 | -16,497 | +0.188 |

Live P1-object basis (x0.30): NQ-alone maxDD **$8,372**, worst-mo **-$4,582**; NQ+gold(fixed-vol)
maxDD **$9,882**, worst-mo **-$4,949**. Same Sharpe/ret/DD.

**What is real:** adding an orthogonal, positive-drift asset lifts the combined Sharpe (+5% to +10%)
and flips the **worst rolling-12-month Sharpe from -0.10 to positive** (+0.19 to +0.32) - a genuine
return-**consistency** improvement, and exactly what any orthogonal positive-Sharpe asset would do.

**Why it is NOT additive:** the *material* bar (Sharpe **and** ret/DD both >= +10% relative, rolling-min
not worse, sleeve weekly-vol > 0) is cleared by **no** (N, sizing) corner. The single best cell
(N=63, fixed-vol 0.5x) is Sharpe +10.1% but ret/DD only **+8.5%** - it does not improve
capital-efficiency enough, and it is not robust: equal-risk *degrades* ret/DD (-12% to -21% as $
drawdown roughly doubles), and N=21 is worse on every axis. The lift is a diversification-by-addition
effect, not a capital-efficiency gain, and it survives at exactly one of four corners. **G3 NOT
PORTFOLIO-ADDITIVE.**

---

## Cost robustness

GC turnover friction (1-tick spread + $4.36 comm = $14.36 RT, per-day `|dw|` one-way) is **negligible**:
avg daily `|dw|` 0.015 (N=63), annual cost drag **0.023%**; the sleeve's after-cost weekly-vol stays
positive (0.001368/wk). **Cost is not the binding constraint** - the sleeve fails on gross merit (matched
ret/DD 0.124 < 0.131 buy-hold) *before* costs. So "cost-robust" in the usual sense (the number does not
evaporate under realistic friction) is **true**, but it does not rescue the verdict.

---

## Classification and decision

- **Improvement class:** DIVERSIFICATION (attempted) - and it is the *raw orthogonal drift* of gold that
  carries the small portfolio benefit, **not** the vol-management (G1 shows vol-management is not a
  better gold than buy-hold at matched exposure).
- **Decision:** per spec `decision_rule`, G1 fails and G3 is not additive -> **NEUTRAL: gold does not
  earn a sleeve.** DISCOVERY_CONSUMED. No forward queue entry, no promotion, no deploy, no sizing change.
- The four research baselines and the live P1 book are untouched.

---

## Deviations / interpretations from the literal spec (transparent)

1. **`ret_pct` (ratio-stitched %-return), `clean_daily` rows only** used as the return series - the
   %-safe DELEV01 basis named in the spec `data:` line. 18 gap-spanning rows dropped (manifest).
2. **rho-to-P1 came out +0.10, not the pre-registered ~0.04** - see G2. The ~0.04 was a full-history
   gold-vs-NQ-*index* figure; over the actual 2022-2026 P1 overlap and against the P1 *strategy* it is
   ~0.10. Recorded, not tuned away.
3. **Portfolio sizing constants (equal-risk, fixed-vol 0.5x)** use full-sample daily-$ vol over the
   shared window - an in-sample **construction device** for a diversification study, not a forward vol
   target. The **sleeve itself is causally vol-targeted** (Cederburg-clean); only the constant that puts
   the two legs on a comparable $ footing uses in-sample vol. All headline ratios are scale-invariant so
   this cannot flip any verdict.
4. **maxDD/CDaR/worst-month for the portfolio** are on the arithmetic-$ P&L path (eval_battery
   convention); the **sleeve-vs-buyhold** return/DD is on compounded equity (correct for a long asset
   over a 4x price move). Both stated where used.
5. **`material` threshold for PORTFOLIO-ADDITIVE** (Sharpe AND ret/DD both >= +10% relative, rolling-min
   not worse, across a transparent sizing) was chosen to make the guard bite on capital-efficiency, not
   merely on the automatic Sharpe lift any orthogonal asset gives. The best cell misses on ret/DD (+8.5%).
6. **fixed-DD shown only beside its side-blind random-thinning placebo** (eval_battery raises otherwise);
   weekly-vol led throughout. Day-as-trade thinning used for the sleeve's fixed-DD placebo.
7. **Ledger:** family `CROSS_ASSET_NATIVE`, one trial `G00064`. The genesis search ledger was **not
   written by this subagent** (write-scope restricted to the run dir); registration is the orchestrator's.

## Deliverables (all in `runs/W2B_GCVOL_20260906/`)
- `out/gate_table.txt` - program-printed GATE/SPEC/OBSERVED/PASS-FAIL.
- `out/sleeve_vs_buyhold.csv` - G1 matched-exposure table, both N.
- `out/portfolio.csv` - G3 book stats, both N x both sizings x both dollar bases.
- `out/daily_pnl.csv` - date, P1 (research + live 0.30x), gold sleeve return/$ (eq-risk & fixed-vol),
  and combined books, for N=21 and N=63.
- `out/run_log.txt` - full program transcript. `out/summary.json` - machine-readable.
- `src/run_w2b.py` - the implementation (imports the XINST01 bench for the exact P1 reproduction).
