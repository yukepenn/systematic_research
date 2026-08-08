# SMV2AJ_ATR_BLEND_R2 — REPORT

_Frozen spec: `runs/SMV2AJ_ATR_BLEND_R2/spec.yaml` (committed 8c030f8 before any read).
Authored by the orchestrator from the execution agent's structured output — subagent Write
tool refused REPORT.md; every number independently reproduced bit-exact by red-team (verdict:
CONFIRMED, two prose-only corrections applied below, no numeric or decision impact)._

## Bottom line
**1 of 5 required gates FAILS (A, on its CDaR_0.95 bootstrap-significance prong).** Per the
frozen decision rule ("pass ALL of A-E → CHAMPION-CANDIDATE; fail ANY → incumbent retained,
lead closed"), the ATR-blended DUAL candidate (arm_BLEND_75, w=0.75) does **not** become
CHAMPION-CANDIDATE core. The incumbent sigma460-only core is retained. **This came far closer
than any prior R2 confirmation in this program** — gates B, C, D, E all pass, several with real
margin — but the single required-and-AND-gated bootstrap prong that fails is dispositive per
the spec's own rule, applied with no discount for a lead that looked promising.

## Step 0 — construction and reuse integrity
`R_ATR_SELECTED = 2.025539235146222` reused verbatim from SMV2AI (not re-derived anywhere,
including on hist). Raw target construction and the DUAL_HTF transform (`dual_htf()`: tilt
×1.25 HTF-agree, c1_50 short-halving, ×0.9026, clip ±13) both reused via direct import of
prior runs' committed code, not reimplemented — verified byte-identical across the reuse chain
SMV2T→SMV2AD→SMV2AI→this run.

**Five integrity checks, all PASS to sub-cent precision** (raw control/BLEND75 vs SMV2AI's
committed curves; DUAL-transformed control/BLEND75 vs SMV2AI's own internal columns;
DUAL_control vs the independently-sourced true incumbent champion leg from
`SMV2H_ONECONTRACT/out/solar_dual_htf_daily.csv`) — a three-way independent cross-check,
confirmed unusually rigorous by red-team.

**Methodological fact-check (spec explicitly required this, not assumed)**: direct read of
`runs/SMV2AI_ATR_BLEND/src/step3_old_regime.py` confirms SMV2AI's own sub_432 old-regime
screen tested the **raw pre-DUAL-transform target**, not the DUAL decision object — no
`dual_htf()` call exists anywhere in that file. **Gate C in this run is therefore a genuine
re-test of an unseen object, not a duplicate** — independently confirmed by red-team via the
same direct source read.

## Gate A — dev paired bootstrap on DUAL-transformed legs — **FAIL**
Paired moving-block bootstrap (block=5, B=10,000, seed=20260808) on daily diffs of
DUAL_BLEND75 − DUAL_CONTROL, 1,139 dev sessions.

| | DUAL_CONTROL (incumbent) | DUAL_BLEND75 (challenger) | point delta |
|---|---:|---:|---:|
| net $ | 138,280.0 | 144,815.2 | +6,535.2 |
| Sharpe | 0.8992 | 0.9431 | +0.0439 |
| CDaR_0.95 $ | 20,447.5 | 19,158.2 | +1,289.2 (improvement) |

**P(dSharpe>0) = 0.9316 (passes the 0.85 bar). P(dCDaR>0) = 0.7529 (fails the 0.85 bar).
Gate A FAILS on the CDaR prong** (both prongs AND-required). Newey-West (lag 5) t-stat on the
diff series = 1.446 — mild, not decisive, consistent with the bootstrap picture. The 5th
percentile of the bootstrapped CDaR delta is −$1,120.4, i.e. materially worse in a non-trivial
share of resampled paths.

## Gate B — chronology — **PASS**
LOYO: 2022 +0.0233, 2023 −0.0014, 2024 +0.0372, 2025 +0.0637, 2026(partial) +0.1245 — **4/5
years same sign**, passing the bar. Fit 2022-24 dSharpe +0.0198; eval 2025-26 dSharpe **+0.0806**
point-positive, dNet **+$5,096.9** point-positive. **Passes cleanly** — and unlike the SMV2T
precedent (fragile edge, sole negative year offsetting an otherwise-thin signal), the delta
here is monotonically improving into the most recent years, the opposite of a decaying edge.

## Gate C — old regime, DUAL-transformed, 2006-2021 — **PASS**
Both DUAL-transformed objects rebuilt on the SM06 hist substrate (1,764,049 3m bars, 16 years).
`R_ATR_SELECTED` reused verbatim (not re-derived on hist, matching SMV2AI's own discipline).
Integrity: reconstructed vote_pend matches the committed hist substrate on 100.00% of bars; the
raw (pre-DUAL) hist nets recomputed here match SMV2AI's own committed screen exactly,
isolating the DUAL transform as the sole methodological delta this gate newly tests.

| | DUAL_CONTROL | DUAL_BLEND75 | |
|---|---:|---:|---:|
| net $ (2006-2021) | 447,134.7 | 533,138.9 | gap **+$86,004.2** |
| Sharpe | 0.2945 | 0.3504 | |
| maxDD $ | 246,834.0 | 213,326.8 | ratio 0.864 |

**c1 (net ≥ incumbent−$10k) PASSES with wide margin** (net is better, not just non-inferior).
**c2 (maxDD ≤ 1.25×) PASSES** (challenger has less drawdown pre-2022). **Gate C passes both
prongs, by a larger margin than SMV2AI's own raw-level screen** (+$71,543.9 there vs +$86,004.2
here) — the DUAL/HTF overlay does not erode the old-regime advantage.

## Gate D — right-tail retention — **PASS**
DUAL_BLEND75's PnL on DUAL_CONTROL's own top-10 days = $113,297.0 vs control's own top-10 sum
$113,139.5 → **retention 100.14%** (≥100% required, same bar SMV2T applied). All 10 of
control's top-10 days are also among BLEND75's own top-10 days; 8/10 are PnL-identical, the
right tail is essentially untouched with small net improvement in 2 of 10 days.

## Gate E — portfolio rebuild, DAYONLY_DUAL6040 — **PASS**
`SIG_old` (incumbent DUAL std) = 2,143.28 → `SIG_new` (BLEND75 DUAL std) = 2,139.99, essentially
unchanged (−0.15%). Reconstructed incumbent champion curve matches the committed
`DAYONLY_DUAL_BMOM_60_40` row exactly, confirming construction fidelity before comparison.

| | incumbent 60/40 | BLEND75 rebuild 60/40 | point delta |
|---|---:|---:|---:|
| net $ | 194,416.0 | 199,160.4 | +4,744.3 |
| Sharpe | 1.2642 | 1.2971 | **+0.0328 (pass)** |
| CDaR_0.95 $ | 14,322.2 | 14,004.1 | **+318.2 (pass)** |

**Gate E passes both AND-required prongs.** Unlike SMV2T's own challenger (whose 13%-larger
leg vol forced more B-MOM exposure at the same nominal target, worsening portfolio CDaR),
BLEND75's leg vol is essentially unchanged from the incumbent — the portfolio rebuild does not
carry the same sizing confound, and the improvement looks structurally cleaner.

## Gate F — blend-weight robustness at w=0.70/0.80 (disclosure-only, not pass/fail)

| w | Sharpe | CDaR_0.95 $ | P(dSharpe>0) | P(dCDaR>0) | passes 0.75 soft bar |
|---|---:|---:|---:|---:|---|
| 0.70 | 0.9268 | 19,169.5 | 0.8086 | 0.6563 | No |
| **0.75 (chosen)** | **0.9431** | **19,158.2** | **0.9316** | **0.7529** | Barely |
| 0.80 | 0.9313 | 19,429.6 | 0.8824 | 0.7266 | No |

**Flagged, precisely characterized (not rounded off in either direction)**: point estimates at
w=0.70/0.75/0.80 form a smooth, mild local hump (Sharpe spread only 0.016) — w=0.75 is **not**
a dramatic outlier or cherry-picked spike. But bootstrap CDaR significance is weak across the
**whole neighborhood** — neither adjacent weight clears even the softer 0.75 bar, and w=0.75
itself only barely does. The honest read: this is not a "mis-picked single point" story, it's
"the mechanism (modest, fairly stable point improvement across w=0.70-0.80) looks real, but its
statistical confirmation on tail risk specifically is thin everywhere nearby" — reinforcing,
not contradicting, gate A's own CDaR failure.

## Decision

| Gate | Requirement | Result | Verdict |
|---|---|---|---|
| A (dev bootstrap) | P(dSharpe>0)≥0.85 AND P(dCDaR>0)≥0.85 | 0.9316 / 0.7529 | **FAIL** |
| B (chronology) | LOYO≥4/5 AND eval point-positive | 4/5, +0.0806/+$5,096.9 | PASS |
| C (old regime, DUAL) | net≥incumbent−$10k AND maxDD≤1.25× | +$86,004 / 0.864 | PASS |
| D (right tail) | retention ≥1.00 | 1.00139 | PASS |
| E (portfolio) | dSharpe AND dCDaR point-positive | +0.0328 / +$318.2 | PASS |
| F (weight robustness) | disclosure only | neighborhood-wide fragility | DISCLOSED |

**1 of 5 required gates fails (A, CDaR prong only). Decision: FAIL ANY → incumbent sigma460-
only core retained.** No master rebuild or parity stage triggered. The ATR/range-blend lead
opened by SMV2AI is recorded **CLOSED at the DUAL-transformed/decision-object level**: B, C, D,
E all pass, several with real margin (gate C's old-regime gap widened vs SMV2AI's raw-level
screen; gate E shows a structurally clean portfolio improvement with almost no sizing
confound) — but the dev-level bootstrap CDaR-significance test this wave specifically added
does not clear its bar, and gate F shows the weakness is neighborhood-wide, not a mis-picked
weight. Per spec: no third bite without a new mechanism (e.g., a different construction
expected to strengthen the CDaR-tail effect specifically, not a re-test of the same blend at a
different weight).

## Red-team disposition
Verdict: **CONFIRMED**. Every gate independently re-executed from raw data and reproduced bit-
exact, including gate A's bootstrap quantiles and gate C's isolation of the DUAL transform as
the sole delta from SMV2AI's own raw-level screen. Anti-gate-shopping checks passed: the
4-point blend-weight grid and R_SELECTED were both pre-registered before SMV2AI's sub_431 ran;
arm_BLEND_75 was the sole passer of 4 arms, no cherry-picking among multiple passers; all six
gate thresholds in code match spec.yaml verbatim. Two corrections applied (both prose-only, no
numeric or decision impact): (1) gate F's code-level `is_narrow_spike` boolean is algebraically
degenerate (reduces to a different condition than its name implies) — the report's own prose
characterization above is the correct, careful treatment, not the buggy field; (2) the original
comparison to SMV2T_NOFAST_R2's gate-A failure overstated the parallel — SMV2T's Sharpe prong
actually FAILED (0.8033<0.85), unlike this run's Sharpe prong which clearly passes (0.9316);
only the "CDaR is the binding constraint" pattern is genuinely shared between the two runs
(corrected in this REPORT's gate-A section above, which now states this precisely).

## Files
`out/step0_verify.json`, `out/curves.csv`, `out/gate_A.csv`, `out/gate_A_summary.json`,
`out/gate_B.csv`, `out/gate_B_loyo.csv`, `out/gate_B_fit_eval.csv`, `out/gate_B_summary.json`,
`out/gate_C.csv`, `out/gate_C_yearly.csv`, `out/gate_C_hist_curves.csv`,
`out/gate_C_summary.json`, `out/gate_D.csv`, `out/gate_D_top10_detail.csv`, `out/gate_E.csv`,
`out/gate_E_curves.csv`, `out/gate_E_summary.json`, `out/gate_F_seed_robustness.csv`,
`out/gate_F_summary.json`, `out/tgt_control_raw_dev.npy`, `out/tgt_blend75_raw_dev.npy`,
`out/tpp_control_dev.npy`, `out/tpp_blend75_dev.npy`. Code: `src/step0_verify.py`,
`src/gate_A.py` through `src/gate_F.py`.
