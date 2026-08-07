# Discovery Wave 1 — Results (full history 2022-01 → 2026-07-31)

2026-08-06/07 · Spec: DISCOVERY_WAVE1_spec.md (preregistered `1b14f9c`) · Cost basis: Lifetime commission included; "slip1" = analytic 1-tick overlay (net − trades×$9.53; validated against the real slip-1 run to within 0.3%).

## Headline structural discoveries

**D1 — The Type-1 core has exactly ONE strategy parameter.** TrendMultiplier {30,60,90,120} (S1: 4×7 grid), SlowdownScan {2..12} × WeakWeakSplit {5,10,15} (S3: 18 combos), and time-normalized Stage-B parameter sets (2m/3m/5m) ALL produce bit-identical results to canonical. For EntrySignalType=1 with trailing-stop exits, only **StopMultiplier** (plus timeframe and exit policy) matters. The vendor's 6-parameter surface collapses to 1D; TrendMultiplier/Slowdown/WWS/PullbackSplit shape Type-2/3 signals only. Consequences: (a) the Type-1 search space is tiny and mappable densely; (b) the vendor "90/179 ≈ 2:1 ratio" guidance is irrelevant to the Type-1 core; (c) multiple-testing burden for Type-1 ≈ number of SM×TF×exit points only.

**D2 — Path-chaos noise on single points is large.** SM=179 → $259,102 (10,183 trades) but SM=180 → $170,997 (10,082 trades): a 1-tick trailing-offset change moves full-history net by $88k (34%) via path divergence. Single-point results carry ±$40-90k noise → **all parameter conclusions must come from dense scans + neighborhood medians, never single points.** The canonical $259k is likely a favorable draw; the honest region estimate comes from the dense SM scan (Wave 1b, running).

**D3 — SM response is monotone toward wider stops (1m, full history, coarse grid):**

| SM | net0 | trades | PF | slip1 | avg1 |
|---|---|---|---|---|---|
| 60 | −$190,735 | 46,602 | 0.979 | −$634,852 | −$13.62 |
| 90 | −$156,072 | 27,630 | 0.978 | −$419,386 | −$15.18 |
| 120 | +$51,154 | 18,530 | 1.009 | −$125,437 | −$6.77 |
| 150 | +$101,084 | 13,420 | 1.020 | −$26,809 | −$2.00 |
| 180 | +$170,997 | 10,082 | 1.040 | +$74,916 | +$7.43 |
| 210 | +$212,323 | 7,974 | 1.056 | **+$136,331** | +$17.10 |
| 240 | +$189,646 | 6,463 | 1.056 | **+$128,054** | **+$19.81** |

Profitable plateau ≈ SM ∈ [180, 240+]; after-cost quality still improving at the grid edge → dense scan extended to SM 150–300 step 10 (1m and 3m, running as Wave 1b).

**D4 — Timeframes are highly non-monotonic; 3-minute is the standout at 90/179:**

| TF | net0 | trades | PF | slip1 (analytic) | avg1 | max DD (s0) | daily Sharpe |
|---|---|---|---|---|---|---|---|
| 1m | $259,102 | 10,183 | 1.060 | $161,567 (real) | $15.76 | −$51,898 | 1.01 |
| 2m | $165,914 | 8,654 | 1.043 | $83,442 | $9.64 | −$66,343 | 0.66 |
| **3m** | **$282,704** | **7,701** | **1.077** | **$209,314** | **$27.18** | −$67,402 | **1.08** |
| 5m | $94,825 | 6,632 | 1.027 | $31,622 | $4.77 | −$141,900 | 0.37 |

Given D2's noise scale, "3m best" needs its SM-curve (Wave 1b) rather than one point — but a +$48k slip-1 gap with better PF, fewer trades, and higher Sharpe is beyond the observed noise band and worth aggressive refinement.

**D5 — Signal types (full history): Type 1 is the only viable after-cost core.** T1: $259k/10,183 → slip1 $162k. T2: $316k/19,776 → slip1 $128k (cost-fragile as the thesis predicted). T0(all): $314k/19,965 → slip1 $123k. T3: $115k/9,313 → slip1 $27k. Type 2/3 belong in *conditional sleeves* (Wave 2), not as cores.

**D6 — Full-history canonical reference (1m/90-179/T1, REAL slip-1 run):** net $161,567, PF 1.037, avg $15.76, DD −$63,114, daily Sharpe 0.63, Calmar 0.56, worst quarter −$23,781, max TUW 315 days. Per-year slip-1: 2022 +$11.4k · 2023 +$34.1k · 2024 +$68.3k · 2025 +$42.6k · 2026(7mo) +$4.0k — positive every year, but 2025-26 economics are thin (2026 ≈ breakeven at 1 tick).

**D7 — SW02a (see SW02a_report.md): no session-close fill artifact** (16:58 timed market exit = 100.0% of baseline at slip-0 AND slip-1), and **exiting ~16:31 dominates the close** (102.4% net, smaller DD). 16:30-exit is a live exit-architecture option for Wave 2.

## What failed / was mapped as dead
- SM ≤ 150 on 1m: negative after realistic costs (tight trailing stops churn). 
- 5m at 90/179: near-dead after costs with 2.7× the drawdown.
- Unconditional Type 2/3/all-signal cores: cost-fragile.
- (Instrumentation conclusions from Phase 1 carry: flip-count veto inverted; low-efficiency quartile is the real dead weight.)

## Config accounting
Search-space points consumed this wave: 7 unique SM (S1) + 4 signal types (S4) + 4 timeframes×1 (S2; Stage-B and TM/temporal grids consumed 0 new points — inert) + SW02a exit ladder 4 + dense scans (Wave 1b: 16 + 16). Registry updated; DSR/PBO at promotion time will use these counts.

## Next sweeps (in order)
1. **Wave 1b (running):** dense SM 150–300 step 10 on 1m AND 3m → plateau map + noise band; pick center-of-plateau by neighborhood median slip-1 net.
2. **Wave 1c:** per-year decomposition (Tier-2 full runs) for the 3–5 best SM×TF cells + the 16:30-exit variant on each; ranking per the preregistered multi-metric table.
3. **Wave 2:** conditional sleeves on the winning core — T1+single same-episode T3 re-entry, selective early-wave T2 (temporal params become ACTIVE here), catastrophe stops, 16:30-exit; new strategy classes required.
