# C01T1_EXPOSURE — Tier-1 lag-1 vol-surprise exposure rule on E10

_Executed 2026-08-07 per frozen `runs/C01T1_EXPOSURE/spec.yaml` (committed before execution).
Counts as trials: 3 (seq 285-287, one per arm — registry rows due). Pure Python on committed
vectors; no NT8. Seed 20260807 (T0-4's frozen seed, reused for permutation and bootstrap;
recorded here, not tuned). Capital base $100,000. Script: scratchpad `c01_t1exp_run.py`._

## Verdict: **REJECT** — effect not robust at Tier-1 gate (H1 sign fails; Romano-Wolf p >= 0.05)

## 1. Input validation (all BEFORE arms were run)

| check | result |
|---|---|
| E10 vector join (`e_variant_daily_vectors.csv` E10_round_session, NaN=0) vs table `pnl` | max abs diff **0.000000** |
| Stored `lagU` == `Uterc` shifted 1 session | exact, 1,001 defined rows |
| Recomputed expanding terciles (>=60 prior obs, quantile 1/3–2/3 linear, <=q1 lo / >q2 hi) vs stored `Uterc` | **100.00%** (1,002/1,002) — method validated, then applied unchanged to logrv for ARM_C |
| Universe | n = 1,001, 2022-09-16 → 2026-07-31; terciles lo/mid/hi = 308/323/370 |
| **T0-4 headline reproduction** | hi−lo diff **+$396.4** (target +396.4); 10k-permutation one-sided p **0.0157** (T0-4: 0.0177; RNG draw-sequence differs, same test) — **OK** |
| Tail diagnostic reproduction | 28,806 pooled trades, top 1% = 289, lo-state share 13/289 = 4.0% vs 30.8% — identical to T0-4 §6 |

ARM_C lag-1 RV LEVEL terciles (same frozen method on `logrv`, breakpoints from all prior RV obs):
defined on 100% of universe; counts lo/mid/hi = 501/277/223; agreement with lag-U terciles 51.8%.

## 2. Per-arm results (universe n = 1,001; halves H1 n = 461, H2 n = 517, 23 sessions after 2026-06-30 in neither)

| arm | net $ | ΔlogG vs flat | 95% CI (block bootstrap) | RW p (1-sided) | Sharpe | maxDD $ | DD vs flat | MAR | ΔlogG H1 / H2 |
|---|---|---|---|---|---|---|---|---|---|
| FLAT (E10) | 147,029 | — | — | — | 0.950 | −41,252 | — | 0.897 | — |
| ARM_A (1.5 hi-U) | 209,175 | **+0.4305** | [−0.059, +0.944] | 0.1001 | 1.049 | −48,640 | +17.9% | 1.083 | **−0.0032** / +0.3497 |
| ARM_B (1.5 hi / 0.5 lo U) | 218,488 | **+0.5544** | [−0.015, +1.139] | **0.0556** | 1.132 | −44,966 | +9.0% | 1.223 | **−0.0035** / +0.4208 |
| ARM_C (control: RV level) | 189,552 | +0.2962 | [−0.265, +0.878] | 0.1551 | 1.017 | −47,230 | +14.5% | 1.010 | −0.1189 / +0.3022 |

Bootstrap: circular session-block, block = 5, B = 10,000, joint resampling across arms;
Romano-Wolf non-studentized stepdown, one-sided H0 ΔlogG ≤ 0.

## 3. ARM_B down-weight tail retention (hard gate)

Top-1% member-trade P&L share in down-weighted (lag-U-lo) sessions **4.0%** (13/289 trades,
of 28,806 pooled round trips from `runs/AUDIT02_V3_SWEEP_B/ledgers/`, exits inside universe)
vs lo-session share **30.8%** → retention ≥ proportional: **PASS**.

## 4. Frozen-gate scorecard

| criterion (spec verbatim) | ARM_A | ARM_B |
|---|---|---|
| ΔlogG > 0 | YES (+0.4305) | YES (+0.5544) |
| RW p < 0.05 | **NO (0.1001)** | **NO (0.0556)** |
| same sign both halves | **NO (H1 −0.0032)** | **NO (H1 −0.0035)** |
| maxDD not worsened > 20% | YES (+17.9%) | YES (+9.0%) |
| tail retention ≥ proportional (B only) | — | YES (4.0% ≤ 30.8%) |
| beats ARM_C on ΔlogG | YES (+0.43 > +0.30) | YES (+0.55 > +0.30) |
| **arm verdict** | FAIL | FAIL |

**REJECT.** Exactly the failure T0-4's fragility caveat predicted: H1 (2022-09 → 2024-06) ΔlogG is
economically zero but *negative* for both U-arms; the entire effect is H2 (mid-2024 onward). ARM_B
misses RW significance by a hair (0.0556) — with H1 sign also failed, no near-miss appeal applies.
Positive notes for the record (not gate-relevant): both U-arms beat the vol-level control (surprise
framing does add something beyond level), ARM_B improves Sharpe 0.950 → 1.132 and MAR 0.897 → 1.223
with only +9% DD, and the down-weight leg is structurally tail-safe. If lag-U conditioning returns,
it must arrive with a mechanism for why the effect only exists post-2024 — otherwise it is regime
overfit.

## Files

- `research/04_complementary_family/c01_t1exp_arm_results.csv` — per-arm metric table (incl. FLAT).
- `research/04_complementary_family/c01_t1exp_session_weights.csv` — per-session pnl, terciles, multipliers, half flags.
- `research/04_complementary_family/c01_t1exp_machine.json` — machine-readable results + gates.
- Registry: 3 trial rows (seq 285-287) due in `research/registry/tested_configs.csv`; rejected-idea
  entry due in `rejected_ideas.md` (lag-1 U exposure scaling — H1-dead, RW-insignificant).
