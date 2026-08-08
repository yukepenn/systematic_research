# W8-1 — B-MOM: intraday momentum family build (readout)

Spec: `research/scalping_lab/specs/W8_programs_final.md` §W8-1 (frozen, cf7041f).
Code: `research/scalping_lab/src/python/w8_bmom.py`. Seed 20260808, 1000 bootstrap
reps, day-clustered CIs. Dev window: 3-min CSV 2022-01 → 2026-05-31 only; rows
≥ 2026-06-01 dropped at load (sealed holdout, never read). Costs: C1 = 2.872
NQ ticks/round-trip, C2 = 4.872 stress; 1 tick = 0.25 pt = $5, 1 NQ throughout.
Every number below appears in `w8bmom_stdout.txt` / `w8bmom_stats.json`.

**Bottom line: NOT PROMOTED. 4 of 5 frozen gate criteria pass; ρ_full = +0.347 vs
Solar net_v1 fails the ρ_full < 0.3 requirement.** The family is profitable
in-sample with near-zero losing-day correlation, but its full-sample daily P&L is
too correlated with Solar to qualify as a diversifier under the frozen gate.

## 1. Implementation of the frozen rule (FACT)

- RTH bars 09:30–16:00 on END-stamped 3-min bars (stamps 09:33..16:00). Every one
  of the 1,136 RTH sessions has its first RTH bar END-stamped 09:33, whose `open`
  is the 09:30 open (asserted at load).
- Noise band: upper/lower = open0930 ± m_tod; m_tod = trailing 14-day mean of
  |close(slot) − open0930| for the SAME 3-min slot-of-day, prior days only
  (per-slot rolling over that slot's prior observations; half-day sessions simply
  lack afternoon slots).
- **No-same-day-leakage assertions PASSED** (from stdout): 300 random (date, slot)
  manual recomputations of the prior-14 mean; per-slot first-14-observation NaN
  check; perturbation test (scaling all closes of 2024-03-15 by 1.5 leaves that
  day's own band bit-identical).
- RTH-anchored VWAP = cum(close×volume)/cum(volume), includes current bar.
- LONG when close > max(upper, VWAP); SHORT when close < min(lower, VWAP);
  otherwise persistence — hold until opposite signal or the 15:57 close-out (flat
  overnight always; asserted flat after close-out every session). Early-close
  sessions (holiday 13:00/13:15 ends): force-flat at the last RTH bar stamped
  ≤ 15:57 — 40 such sessions in the included window.
- Fills at signal-bar close (family convention, as in prior Program-B specs);
  entries/flips allowed on END stamps 09:33..15:54 only. One position, 1 NQ.
- **First 14 sessions of the CSV excluded (no band history): 14 sessions,
  2022-01-03..2022-01-20.** Included: 1,122 sessions, 2022-01-21..2026-05-29.
  After the exclusion, 58 decision bars still had NaN bands (afternoon slots that
  accumulate 14 observations later because 2022-01-17 was a half day) — no signal
  taken on those bars.

## 2. Headline results — frozen 14-day rule (IN-SAMPLE CHARACTERIZATION)

1,333 trades over 1,122 sessions (1.188 trades/day; 84 zero-trade days).
Exits: 1,038 close-out / 295 flip. Sides: 650 long / 683 short; net C1 by side:
long +42,054.2t, short +21,770.4t.

| Metric | C1 (2.872t) | C2 stress (4.872t) |
|---|---|---|
| Net/trade (ticks) | **+47.880** | +45.880 |
| Net/trade 95% CI, day-clustered (t) | [+13.059, +85.320] | [+11.059, +83.320] |
| PF (trade-level, net) | **1.2148** | 1.2049 |
| PF (daily-level) | 1.2605 | 1.2482 |
| Win rate (trades) | 0.5116 | 0.5086 |
| Total net | +63,824.6t ($+319,123) | +61,158.6t ($+305,793) |
| Mean daily P&L | $+284.42 | $+272.54 |
| Daily 95% CI (1000 boot reps, days) | [+78.35, +500.06] | [+66.34, +488.34] |
| Daily std | $3,576.55 | $3,579.26 |
| Ann. Sharpe (daily) | 1.262 | 1.209 |
| Max drawdown (daily closes) | $43,325 (8,665t) | $43,485 (8,697t) |
| Top-5-day share of total net | **29.89%** ($95,393.84) | 31.18% |
| Net excluding best 5 days | $+223,729.28 | $+210,459.28 |

Yearly split, C1 (IN-SAMPLE CHARACTERIZATION):

| Year | Sessions | Trades | Trades/day | Net (t) | Net ($) | Net/trade (t) | PF | Win |
|---|---|---|---|---|---|---|---|---|
| 2022 | 244 | 299 | 1.225 | +19,973.3 | +99,866 | +66.80 | 1.265 | 0.545 |
| 2023 | 257 | 313 | 1.218 | +5,780.1 | +28,900 | +18.47 | 1.108 | 0.492 |
| 2024 | 259 | 310 | 1.197 | +10,858.7 | +54,293 | +35.03 | 1.182 | 0.481 |
| 2025 | 257 | 283 | 1.101 | +22,094.2 | +110,471 | +78.07 | 1.303 | 0.530 |
| 2026 (Jan–May) | 105 | 128 | 1.219 | +5,118.4 | +25,592 | +39.99 | 1.143 | 0.516 |

Positive every calendar year; weakest year 2023 (PF 1.108). No single year
dominates, though 2022+2025 carry ~66% of the total.

## 3. The two deciding diversification numbers (FACT, measured on C1 daily $ vs Solar net_v1, Pearson, N = 1,122 overlapping sessions 2022-01-21..2026-05-29; zero-trade days included at $0)

- **ρ_full = +0.346530**
- **losing-day ρ (Solar net_v1 < 0 subset, N = 661) = +0.045930**

## 4. Frozen promotion gate (C1, 14-day frozen rule) — VERDICT: **NOT PROMOTED**

| Criterion (frozen) | Measured | Verdict |
|---|---|---|
| Daily net C1 > 0 with CI_lo > 0 | mean $+284.42/day, CI95 [+78.35, +500.06] | **PASS** |
| PF ≥ 1.10 | PF(trade) = 1.2148 | **PASS** |
| ρ_full < 0.3 | ρ_full = +0.3465 | **FAIL** |
| Losing-day ρ ≤ 0.1 | ρ_losing = +0.0459 | **PASS** |
| Top-5-day concentration < 40% | 29.89% | **PASS** |

The candidate does NOT freeze for engine parity + Tier-1.

## 5. Neighbors — REPORTED, NEVER SELECTED (IN-SAMPLE CHARACTERIZATION)

Each neighbor excludes its own first-W sessions (10 / 20); all other rules identical.

| Metric (C1) | w10 | **w14 (frozen)** | w20 |
|---|---|---|---|
| Included sessions | 1,126 | 1,122 | 1,116 |
| Trades (trades/day) | 1,373 (1.219) | 1,333 (1.188) | 1,327 (1.189) |
| Net/trade (t) | +40.107 | +47.880 | +46.179 |
| PF (trade) | 1.1786 | 1.2148 | 1.2067 |
| Win rate | 0.5091 | 0.5116 | 0.5087 |
| Mean daily $ [CI95] | +244.52 [+35.04, +462.75] | +284.42 [+78.35, +500.06] | +274.55 [+63.20, +489.47] |
| Max DD ($) | 49,665 | 43,325 | 43,429 |
| Top-5 share | 34.65% | 29.89% | 31.61% |
| ρ_full vs net_v1 | +0.3493 | +0.3465 | +0.3665 |
| ρ_losing | +0.0574 | +0.0459 | +0.0730 |

The family is plateau-like across the window (all three variants profitable, PF
1.18–1.21, CI_lo > 0) — the frozen 14-day setting is not a lucky spike. But the
gate-failing number is also stable: **every neighbor has ρ_full ≥ 0.34**; the
correlation failure is a property of the construction, not of the 14-day window.

## 6. Interpretation (INFERENCE)

- The always-monitoring breakout construction is, mechanically, an intraday trend
  follower on NQ — the same underlying exposure Solar monetizes. The W5-B2 pregate
  probe (a cruder 15:30→16:45 Gao-style hold) measured ρ_full = +0.134 and
  permitted this build; the full always-monitoring family, which is in the market
  most of the day, comes in at +0.347. The pregate probe under-estimated the
  family's Solar overlap because it only sampled 75 minutes of the day.
- The losing-day correlation (+0.046) says the family does NOT systematically lose
  when Solar loses — as tail insurance it would actually be attractive, and the
  standalone economics (CI_lo > 0 at C1 and C2, concentration 29.9%, positive
  every year) are the strongest Program-B numbers produced so far. But the frozen
  gate requires both correlation conditions, and ρ_full fails with no neighbor
  rescuing it.
- Per the frozen spec there is no re-specification within this wave: the rule was
  frozen before readout, the gate is binary, and the verdict is NOT PROMOTED.
  Any successor (e.g., a Solar-residual-weighted or regime-gated variant aimed at
  the ρ_full term) requires a NEW preregistered spec in a future wave; nothing
  here licenses tuning against the correlation number we just observed.
- All standalone P&L numbers above are in-sample characterization on the dev
  window with idealized signal-bar-close fills; they are not confirmation.

## 7. Artifacts

All under `research/scalping_lab/artifacts/w8_bmom/`:
- `w8bmom_stdout.txt` — full run log (leakage assertions, all printed numbers)
- `w8bmom_stats.json` — every statistic in this report, machine-readable
- `w8bmom_w14_trades.csv`, `w8bmom_w14_daily.csv`, `w8bmom_w14_joined_daily.csv`
  (daily P&L joined with Solar net_v1/net_v2)
- `w8bmom_w10_trades.csv` / `w8bmom_w10_daily.csv`,
  `w8bmom_w20_trades.csv` / `w8bmom_w20_daily.csv` (neighbors)
