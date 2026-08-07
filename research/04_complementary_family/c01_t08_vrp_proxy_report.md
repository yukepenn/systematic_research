# C01 T0-8 — VRP PROXY STUDY (Family E gate)

_Executed 2026-08-07. Tier-0 instrumentation (0 R1 trials). Spec: `C01_WAVE_SPEC.md` item T0-8,
frozen before this read. Comparator series: executable E10 (`E10_round_session`)._

## Verdict

**Literal frozen gate: PASS — 2 of 3 proxies (P2 short-VX1, P3 VIX−RV spread) satisfy
(a) corr ≤ 0 AND (b) mean > 0 on E10 bottom-quintile days AND (c) nonzero tail overlap.
Family E instrument-design phase unlocks** (out-of-pipeline; separate decision), **with a
material asymmetric-sizing warning** — see (c) below — **and an explicit significance caveat**:
under a Bonferroni-strict reading (each directional claim significant at α = .05/3 = .0167),
0 of 3 proxies pass, because condition (b) is not statistically distinguishable from zero for
any proxy. The frozen text gates on the stated inequalities; both readings are reported so the
unlock decision is made with eyes open.

## Data sources (acquired 2026-08-07; window 2022-01-01 → 2026-07-31)

| Proxy | Series | Source |
|---|---|---|
| P1 | Cboe PUT (PutWrite) index daily close → daily % return | `https://cdn.cboe.com/api/global/us_indices/daily_prices/PUT_History.csv` |
| P2 | SVXY total-return daily close → daily % return | Yahoo Finance chart API v8, adjusted close (`SVXY`, daily) |
| P3 | VIX daily close − 20d realized vol of NQ session closes (annualized, vol points) | VIX: `https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv`; NQ RV: repo `runs/AUDIT03_BARS/nq_3m_2022_2026.csv` |

**Documented substitutions (P2):**
1. The preregistered series, inverted SPVXSP (S&P 500 VIX Short-Term Futures index), is **not
   freely downloadable** (S&P DJI requires registration; no public CSV endpoint). Per the
   preregistered fallback, SVXY total-return daily closes were used instead. SVXY holds **−0.5×
   daily-rebalanced SPVXSP exposure** (post-Feb-2018 leverage), so it IS the short/inverted side
   already — no further inversion applied. Half leverage halves magnitudes but preserves the sign
   and correlation structure the gate tests; T-bill collateral yield and 0.95% ER are small
   positive/negative drifts that do not affect sign tests at this horizon.
2. The suggested source (stooq.com CSV) is blocked by a JavaScript proof-of-work challenge from
   this environment; Yahoo Finance's chart API supplied the identical series. Yahoo adjusted
   close handles SVXY's single in-window corporate action (2:1 split, 2024-04-11); SVXY paid no
   dividends in-window, so adjusted close = total return.

## Method (frozen conventions)

- **Session calendar**: E10 day index from `research/audit/e_variant_daily_vectors.csv`
  (`E10_round_session`), 1,184 sessions 2022-01-03 → 2026-07-31. NQ session closes rebuilt from
  the 3-min bar file via `first_bar_of_session` grouping, session labeled by its closing date —
  **0 mismatches** against the E10 day index.
- **NQ realized vol**: 20-session rolling std (ddof=1) of log close-to-close session returns,
  × √252 × 100 (annualized vol points). First valid value after 20-session warm-up (2022-02-01).
- **P3 is a level series** (annualized vol-point spread), the daily payoff scale of a VRP
  harvest; P1/P2 are daily returns. Each proxy is inner-joined to the E10 calendar on its own
  availability: n = 1,148 (P1, P2; 36 CME-open/NYSE-closed sessions drop) and n = 1,161 (P3;
  RV warm-up + 3 VIX holidays drop).
- Quantile thresholds (E10 quintiles/deciles, proxy deciles) computed within each proxy's joined
  sample. Tests: (a) Pearson corr, one-sided p for ρ < 0 (Spearman as robustness); (b) one-sample
  t-test, one-sided mean > 0; (c) binomial test of overlap fraction vs the 0.10 independence
  baseline. Bonferroni α = .05/3 = .0167 per proxy.

## Results

| | P1 PUT return | P2 SVXY return | P3 VIX−RV spread |
|---|---|---|---|
| n (joined days) | 1,148 | 1,148 | 1,161 |
| **(a) corr with E10 P&L** | **−0.039** (p₁=.093) | **−0.140** (p₁=9.7e-7 ✓sig) | **−0.014** (p₁=.32) |
| Spearman (robustness) | −0.039 | −0.117 | −0.005 |
| **(b) mean on E10 bottom-quintile days** | **−0.026%/d** (t=−0.57) | **+0.162%/d** (t=1.05, p₁=.148) | **+0.152 volpt** (t=0.33, p₁=.371) |
| **(c) proxy worst-decile days on E10 best-decile days** | **29/115 = 25.2%** (p=2.3e-6) | **30/115 = 26.1%** (p=7.2e-7) | **21/117 = 17.9%** (p=.0059) |
| (a) corr ≤ 0 | ✓ | ✓ | ✓ |
| (b) > 0 | ✗ | ✓ | ✓ |
| (c) nonzero | ✓ | ✓ | ✓ |
| **Passes literal gate** | **NO** | **YES** | **YES** |
| Passes Bonferroni-strict | no | no ((b) n.s.) | no ((a),(b) n.s.) |

p₁ = one-sided p-value in the claimed direction; ✓sig = significant at Bonferroni α=.0167.

Context: overall proxy means/day — P1 +0.035%, P2 +0.080%, P3 +0.415 volpt (median +1.14;
37.8% of days negative). Mean on **E10 best-decile** days — P1 −0.053%, P2 −0.659%, P3 −1.01
volpt: every proxy is on average losing/compressed on our best days.

Per-year Pearson corr with E10 P&L (`c01_t08_corr_by_year.csv`):

| year | P1 | P2 | P3 |
|---|---|---|---|
| 2022 | −0.098 | −0.188 | −0.001 |
| 2023 | −0.054 | −0.160 | −0.120 |
| 2024 | −0.091 | −0.228 | −0.028 |
| 2025 | −0.001 | −0.150 | +0.042 |
| 2026 (→07-31) | +0.039 | +0.021 | −0.048 |

P2's anti-correlation is present in 4/5 years (sign flips only in the 2026 partial year);
P1 and P3 hover near zero.

## Interpretation

- **The real Family E signal is P2 (short-VX1 carry)**: corr −0.140 highly significant, negative
  every full year, and positive (though individually insignificant) carry on our worst-quintile
  days. This is the classic trend/short-vol complementarity: vol carry earns while trend bleeds
  in chop, and gets destroyed exactly when trend pays.
- **P1 (put-writing) fails (b)**: PUT carries ≈0.5 equity beta, so on E10 bottom-quintile days
  (which include down-drift chop) it bleeds with the market (−0.026%/d). Put-writing is not a
  usable complement shape for this book.
- **P3 is diluted by a cross-index basis**: VIX is SPX implied while RV is NQ realized; NQ
  typically realizes above SPX implied (37.8% of days spread < 0), and a slow-moving level
  correlates weakly with daily P&L. Its tail behavior (spread −1.01 volpt on our best days,
  overlap 17.9%) still shows the expected crisis compression.
- **(c) asymmetric-sizing warning — material on all three proxies**: 18–26% of proxy worst-decile
  days land on E10 best-decile days, 1.8–2.6× the 10% independence baseline (all binomial
  p < .006). A short-vol sleeve sized too large would cancel precisely the right-tail sessions
  the Family A edge lives on (frozen campaign finding: the edge IS the right tail). Any Family E
  instrument design must cap sleeve size so its crisis loss cannot offset a material share of
  Family A's top-decile session P&L, and must be stress-tested jointly on those overlap days
  (flagged in `c01_t08_joined_daily.csv`).
- **Scope**: all tests are contemporaneous on daily closes — this is a complementarity gate, not
  a tradability claim. No lag structure, costs, margin, or instrument selection tested here;
  that is exactly what the (separate, out-of-pipeline) instrument-design phase is for.

## Files

- `c01_t08_metrics.csv` — all gate metrics and test statistics, one row per proxy.
- `c01_t08_joined_daily.csv` — aligned daily table (E10 P&L, all proxy series, VIX, RV20,
  per-proxy tail/quintile flags).
- `c01_t08_corr_by_year.csv` — per-year correlation breakdown.
- Raw source CSVs cached in the session scratchpad; sources and URLs above suffice for
  re-acquisition (Cboe endpoints are stable; Yahoo series verified against the 2024-04-11 split).
