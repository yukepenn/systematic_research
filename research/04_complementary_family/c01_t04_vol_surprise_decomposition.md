# C01 T0-4 — Vol-surprise decomposition of the high-vol effect (SW08 refinement)

_Executed 2026-08-07 per `C01_WAVE_SPEC.md` §2 T0-4. All constants frozen in the spec before
any result was read. Implementation constants fixed BEFORE first run (recorded in the analysis
script header): expanding-tercile assignment requires ≥ 60 prior observations; permutation seed
20260807; the directional gate ("diff > 0, p < .05") is evaluated on the one-sided permutation
p, with the two-sided p reported alongside. Tier-0 instrumentation — 0 R1 trials consumed._

## Verdict: **PASS** — Tier-1 exposure-rule sim (m ∈ {0.5, 1.0, 1.5}, session-level, on E10) unlocked, with fragility caveats below

## 1. Data and model

| item | value |
|---|---|
| 3-min bars | `runs/AUDIT03_BARS/nq_3m_2022_2026.csv`, 2022-01-02 → 2026-07-31 |
| Sessions with RV (within-session squared 3-min log returns, 18:00→17:00 ET) | 1,184 (all kept; none < 100 bars) |
| HAR-RV on log RV: [1, lag-1, mean 1–5, mean 1–22], expanding OLS, ≥ 100 train obs | first forecast 2022-06-23; 1,062 forecasts |
| HAR out-of-sample pseudo-R² (1 − SS_res/SS_tot on expanding forecasts) | **0.477** |
| Tercile-assigned universe (F and U, expanding breakpoints, ≥ 60 prior obs) | 1,002 sessions, 2022-09-15 → 2026-07-31 |
| E10 daily P&L | `research/audit/e_variant_daily_vectors.csv` `E10_round_session`; 0 flat-NaN sessions inside the assigned window |
| E10 net over lag-universe window | $147,029 (mean $146.9/session, n = 1,001) |

U = log RV − HAR forecast. corr(U, log RV) = **0.69** (surprise and level are strongly collinear —
relevant to Test 3).

## 2. 3×3 sort — mean E10 P&L ($/session) by forecast tercile × surprise tercile (contemporaneous)

| | U lo | U mid | U hi | n (lo/mid/hi) |
|---|---|---|---|---|
| **F lo** | +10.6 | +113.5 | +241.7 | 141/145/176 |
| **F mid** | −238.6 | −217.4 | +74.5 | 89/98/105 |
| **F hi** | +284.3 | +199.4 | **+944.5** | 78/81/89 |

Best cell by far: high forecast × high surprise. Worst: mid-forecast, low/mid surprise.

## 3. Test 1 — contemporaneous U hi−lo within each F tercile (10k label shuffles)

| F tercile | diff ($) | p (one-sided) | p (two-sided) | n |
|---|---|---|---|---|
| lo | +231.1 | 0.132 | 0.264 | 462 |
| mid | +313.0 | 0.150 | 0.300 | 292 |
| hi | +660.2 | 0.120 | 0.238 | 248 |

Positive in all three cells but **not significant in any**. The effect is NOT contemporaneous-only
— the REJECT trigger does not fire.

## 4. Test 2 — TRADABILITY: today's P&L sorted by YESTERDAY'S U tercile

Tercile means (n = 1,001): lag-U lo **−$60.5** (308) | mid +$128.1 (323) | hi **+$335.9** (370) — monotone.

| window | hi−lo diff ($) | p (one-sided) | p (two-sided) | n |
|---|---|---|---|---|
| Full 2022-09-16 → 2026-07-31 | **+396.4** | **0.0177** | **0.0365** | 1,001 |
| H1 2022-09-16 → 2024-06-28 | +18.8 | 0.461 | — | 461 |
| H2 2024-07-01 → 2026-06-30 | +572.2 | 0.036 | — | 517 |

Sign agreement across halves: **both positive** → frozen criterion met.

**Fragility (disclosed, not gate-relevant under the frozen wording):** H1's diff is economically
zero (+$18.8) and its tercile profile is hump-shaped (lo +13 / mid +111 / hi +32); the whole
effect is carried by H2, i.e. mid-2024 onward. Yearly hi−lo diffs: 2022 +145, **2023 −165**,
2024 +41, 2025 +624, 2026 +1,593 (4/5 years positive). Any Tier-1 pass must show ΔlogG > 0 in
both halves per the spec gate — H1 will be the binding constraint.

## 5. Test 3 — is lagged U subsumed by lagged RV level? (OLS, Newey-West 5 lags, n = 1,001)

| model | coefficient | b | t | p |
|---|---|---|---|---|
| P&L ~ U₋₁ | lagU | +338.3 | +2.10 | **0.036** |
| P&L ~ logRV₋₁ | lagRV | +226.2 | +1.86 | 0.063 |
| P&L ~ U₋₁ + logRV₋₁ | lagU | +232.2 | +1.39 | 0.166 |
| | lagRV | +109.4 | +0.81 | 0.416 |

With corr(lagU, lagRV) = 0.70, the joint regression washes both out — but the level is NOT the
survivor: **U alone is significant, the level alone is not, and U keeps the larger t in the joint
fit (1.39 vs 0.81)**. "Subsumed by level" would require the level to remain significant while U
dies; the opposite ordering holds. REJECT trigger does not fire. Honest reading: U and level are
largely one signal at daily granularity; U is the (modestly) better-conditioned version of it.

## 6. Right-tail hard gate (would-be-downweighted state = lag-1 U lo)

Pooled round-trip trades from the 13 member ledgers with exit inside the state universe: 28,806
trades; top 1% = 289 trades, total +$3,570,165 (prices already include 1-tick slip; commissions
included).

| quantity | value |
|---|---|
| Share of top-1% trade P&L in lag-1 U-lo state | **4.0 %** (13/289 trades) |
| Session share of lag-1 U-lo state | **30.8 %** |
| Tail gate (P&L share ≤ session share) | **PASS — by a wide margin** |

The right tail actively avoids the post-low-surprise state: big trades cluster after vol
surprises. Down-weighting lag-U-lo sessions is structurally tail-safe at the diagnostic level.

## 7. Frozen-gate scorecard

| criterion | result |
|---|---|
| lag-1 U hi−lo diff > 0 | YES (+$396.4) |
| permutation p < .05 | YES (0.0177 one-sided; 0.0365 two-sided — passes either way) |
| same sign both halves | YES (+18.8 / +572.2) |
| REJECT: contemporaneous-only | NO (contemporaneous n.s., lagged significant) |
| REJECT: subsumed by lagged RV level | NO (level weaker alone and jointly) |
| Right-tail hard gate | PASS (4.0 % ≤ 30.8 %) |
| **VERDICT** | **PASS → Tier-1 unlocked** |

Caveats carried into Tier-1: (a) H1 effect ≈ 0 — the spec's Tier-1 gate (ΔlogG > 0, Romano-Wolf
p < .05, both halves, tail gate) is materially harder than this diagnostic and may well fail on
H1; (b) 2023 is a negative year; (c) U ≈ level at ρ = 0.70 — if the Tier-1 sim passes, a vol-level
control arm should confirm the surprise framing adds anything before promotion (echoes the T0-6
vol-only-control discipline). Raw p (0.0177) is subject to family-level Romano-Wolf stepdown at
wave close.

## Files

- `research/04_complementary_family/c01_t04_session_table.csv` — per-session RV, log RV, HAR
  forecast, U, F/U terciles (−1 = unassigned), lag-1 U tercile, E10 P&L.
- Analysis scripts (scratchpad, session wf): `t04_vol_surprise.py`, `t04_supp.py`; helpers reused
  from `src/analytics/audit_mtm.py` (session_date, fill parsing).
- Registry: seq-0 instrumentation row due in `research/registry/tested_configs.csv`
  (counts_as_trial: no) as C01-T0-4 on wave accounting.
