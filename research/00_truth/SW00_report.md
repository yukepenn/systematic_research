# SW00_BASELINE_PARITY_COST — Result Report

**Decision: PASS** (all preregistered gates met) · 2026-08-06 · Spec: [SW00_spec.md](SW00_spec.md) · Full tables: [SW00_analysis.json](SW00_analysis.json)

## 1. Gate results (preregistered)

| Gate | Result |
|---|---|
| 1. Determinism: 7 canonical jobs (5 serial + 2 concurrent) + 1 extra serial observation, all bit-identical ledger/metrics/equity hashes (`fe395c14…`); matches parity run B economics exactly | ✅ PASS |
| 2. Effective parameters echoed exactly in every run (`params_hash 4e2e06a7…`) | ✅ PASS |
| 3a. Slip-1 positive: net $118,645.60, avg trade $40.83 | ✅ PASS |
| 3b. Slip-1 soft 2.5× cost target ($35.90): $40.83 | ✅ PASS (margin 14%) |
| 3c. Slip-2 not structurally destroyed: net $91,935.60 | ✅ PASS |
| 4. Slippage realism: 95.2% of entries / 95.5% of exits slipped the full tick; remainder capped at bar extremes (0 ticks). Effective cost $9.53/RT/tick vs naive $10. TotalSlippage accounting reconciles (points × $20) | ✅ PASS |
| 5. No impossible behavior: P&L ≡ Δprice×$20−commission (max err 9×10⁻¹³); 0 negative durations; 0 trades spanning sessions; all 12 non-17:00 session-close exits are CME holiday half-days (13:00/13:15/09:15 Good Friday) + one 16:59 fill from the 30s-before-close setting; 2 same-timestamp trades are final-bar entries closed by session-close on the same minute bar (benign) | ✅ PASS |
| 6. Fill-resolution probe: `High` accepted and ran; fills identical to Standard on all 89 matched trades — the expected result for a market-order-only strategy (fills at next-bar open regardless of intrabar granularity) | ✅ reported |

**Rejection criteria:** none triggered. Solar promotion may proceed to Phase 1.

## 2. Cost ladder (canonical window, NT8-native net/DD; daily-MTM risk stats)

| Slippage | Net | Avg trade | PF | Daily Sharpe | Sortino | Calmar | Max DD (trade-level) | ES95/day | Worst quarter | Max TUW (days) | %+months |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 ticks | $146,440.60 | $50.37 | 1.132 | 1.72 | 3.56 | 3.59 | −$22,066.60 | −$4,319 | −$2,427 | 69 | 72% |
| 1 tick | $118,645.60 | $40.83 | 1.106 | 1.39 | 2.83 | 2.56 | −$23,871.60 | −$4,415 | −$4,885 | 133 | 64% |
| 2 ticks | $91,935.60 | $31.67 | 1.081 | 1.08 | — | 1.67 | −$26,551.64 | — | −$8,155 | 160 | — |
| 3 ticks | $66,300.60 | $22.88 | 1.058 | 0.78 | — | 1.04 | −$30,691.64 | — | −$11,250 | 160 | — |

Slip-3 stays positive ($66.3k vs the thesis's naive $59.0k estimate — bar-capping makes realized slippage ~4.7% milder than linear). The realistic-cost picture (1 tick): PF 1.106, daily Sharpe ~1.4, Calmar ~2.6, but time-under-water doubles vs zero-slip. Every additional tick costs ≈ $27.4k over the window.

## 3. Where the P&L actually lives (slip-0 ledger, 2,914 serialized trades)

**By exit reason — the central Phase-0 discovery:**

| Exit | n | Net | Avg | Win% | PF |
|---|---|---|---|---|---|
| Exit on session close | 279 | **+$189,559** | $679.42 | 73.5% | 10.78 |
| L-SolarExit | 1,230 | −$26,478 | −$21.53 | 36.4% | 0.95 |
| S-SolarExit | 1,405 | −$16,311 | −$11.61 | 35.1% | 0.97 |

Trades still open at session close carry the entire net edge; Solar-trailing-exited trades are collectively negative after costs. Interpretation caution: this is intra-day survivorship (winners keep running into the close), NOT a license to only trade near the close. But it sharpens SW02's session-close question (flatten-vs-carry counterfactual is now clearly high-stakes) and SW01's giveback attribution (median MFE giveback is 1.34× — the median trade surrenders more than its full peak excursion before exiting).

**By year (no one-year dependence):** 2023: n=1107, +$42,148, PF 1.10 · 2024: n=1593, +$83,535, PF 1.14 · 2025 (Jan): n=214, +$21,087, PF 1.24. Positive every calendar year; 77.8% of quarters positive.

**By side (both positive, long-heavy):** Long n=1385, +$103,491, PF 1.20 · Short n=1529, +$43,279, PF 1.07.

**Right tail:** top-decile winners = 32.7% of gross profit; net stays positive after removing the top 1/3/5/10 trades ($139.1k / $124.7k / $112.7k / $87.4k). Largest 5 winners are distributed across 2023-10, 2025-01, 2023-08, 2024-07, 2024-12 and both directions (3 short / 2 long) — no single-trade dependence.

**Roll/session integrity:** exit-on-session-close ⇒ zero trades span the daily maintenance break, so no trade ever holds across a contract-roll gap; per-trade P&L identity holds to 10⁻¹³.

## 4. Pipeline benchmark → campaign execution modes

| Measurement | Value |
|---|---|
| Submission latency | ~0.15 ms (client) |
| Engine, full window (737,708 bars), serial | 4.0–6.1 s (median ≈ 4.1 s) |
| Engine, 3-month window (91k bars) | 1.0 s → ≈0.6 s fixed + ~4.7 ms/1k bars |
| Full-trade payload | 3.03 MB; local ingest ≈ 215 ms; polling round-trips dominate wall clock (~10–15 s/run end-to-end) |
| Native optimization (2 full-window combos) | 7.96 s total, single bars-load, ~5 KB summary payload; sweep iterations bit-identical to standalone runs; fixed `parameters` honored (v1.13.9) |
| Concurrent submission (2 jobs) | Safe — overlapping execution, results bit-identical; per-job engine time inflates ~2×, so gain is modest |
| High fill resolution | Available; no effect on market-order-only strategies; REQUIRED later for any stop/limit-order candidate (SW02 catastrophe stop) |

**Adopted modes:** Tier 1 discovery = native optimization sweeps (summary metrics, ~4 s marginal per combination, sweepable params must be `[NinjaScriptProperty]` numerics). Tier 2 confirmation = individual full-payload backtests. Tier 3 audit = High-fill for stop-order candidates + manual Playback (user action; MCP must not alter connections). Determinism-critical runs stay serial.

## 5. Run ledger

| Run | Job | Engine ms | Note |
|---|---|---|---|
| R01 | 98809e65e1a84afc | 6058 | canonical baseline, full artifacts |
| R02–R05 | 44e894ad, 6f946e95, 3c2fe5f2, b4abb6b9 | 4106/4159/4465/4096 | hash-identical (slim storage, dedup vs R01); one extra identical observation job 0e6ae180 (4029 ms) ingested transiently during R04 bookkeeping |
| R06–R08 | eeb0b9b4, 10bc5263, c7856904 | 4282/4122/4663 | slippage 1/2/3 |
| R09 | b83a084f | 150 | High-fill probe, 4-week subwindow (quarantined) |
| R10 | 346da1ef | 7956 | zero-info optimization sweep (2/2 iterations) |
| R11 | 0ba8ff39 | 1004 | 3-month scaling (quarantined) |
| R12/R13 | aa89089a, 1a7c850b | 7572/8997 | concurrent pair, hash-identical |

## 6. What was learned (beyond gates)
1. The realistic-cost baseline (1 tick) is the honest reference: **PF 1.106, avg $40.83, daily Sharpe 1.39, Calmar 2.56** — thin but real, exactly as the thesis warned.
2. The Solar trailing exit is a net-negative harvester; session-close exits carry the edge → SW01 attribution and SW02 session-close counterfactuals are the highest-information next steps, and right-tail protection matters even more than assumed.
3. Slippage in NT8 is bar-capped (≈95% full-tick realization) — cost stress here is mildly optimistic vs a hard $10/RT/tick assumption; keep the 1-tick gate but remember 2-tick numbers at promotion time.
4. Native optimization mode is validated as trustworthy (bit-identical to standalone) — large Tier-1 sweeps are cheap, but every combination still counts toward the multiple-testing registry.
5. Intrabar fill ambiguity is currently zero (market orders only). Introducing ANY stop order (SW02) changes this — High fill resolution becomes mandatory there.

## 7. Red-team review (independent adversarial pass, verbatim)

**Strongest reason "edge survives realistic costs" may be false.** This is an in-sample cost stress, not an edge test. The constitution itself classifies 2023-01..2025-02 as contaminated research data, and the parameters (TrendMultiplier 90, StopMultiplier 179) predate the spec. SW00 therefore demonstrates only that *already-selected* parameters clear 1-tick friction on the data they were selected against. PF 1.106 means net is the difference of $1.243M gross profit and $1.124M gross loss — a 9.5% residual; modest in-sample selection bias alone can manufacture that. "PASS" is a pipeline result; "edge survives" is an overclaim.

**Data/implementation artifacts.** The "central Phase-0 discovery" (session-close exits carry the edge, PF 10.78) is mostly conditioning on outcome. A trailing stop mechanically routes every adverse path to SolarExit and lets only never-stopped paths reach 17:00 — the close bucket is defined as survivors. Its MAE avg of $356 vs $615/$574 for the exit buckets confirms selection, not information. Also: 279 trades (9.6%) carry +$189,559 while the other 2,635 trades net −$42,789 — the strategy ex-close-carry is a loser, and every one of those 279 profit-carrying exits fills at 16:59:30–17:00 ET, the thinnest minute of the session, exactly where 1-tick-capped fills are least believable.

**Cost-model fragility.** Bar-capping is anti-conservative precisely on fast bars, and the biggest trades cluster on event days (2024-12-18 FOMC: +$5,195 in 20 min; 2024-08-06 open: −$1,649 in 3 min) where NQ market orders realistically slip 2+ ticks. Slip-2 is the honest floor there: Sharpe 1.08, Calmar 1.67, TUW 160/537 days. The short side is one tick from irrelevance: avg $28.31, PF 1.073 at slip-0 → ~$18.8/trade, PF ~1.05 at slip-1. Slip-3 net minus top-10 trades = $7,583 — 0.34% of trades away from zero under stress.

**Statistical concerns.** Daily Sharpe 1.39 over ~2.1 years has SE ≈ 0.97; the 95% CI reaches ~0. Avg trade $40.83 against per-trade σ ≥ $840 gives t ≈ 2.0–2.6 pre-clustering — marginal. "Positive every calendar year" counts 2025 = January only (n=214, the best month in the sample). The first six months (2023Q1 −$1,505, Q2 −$2,427) were negative; the sample never contains a bear regime.

**Internally inconsistent or too convenient.** (1) NT8 reports 2,915 trades / $146,440.60; the serialized ledger has 2,914 / $146,769.96 — a one-trade, $329.36 gap [controller: explained — data-boundary serialization artifact, documented penny-exact in the parity report and CLAUDE.md]. (2) TotalSlippage = 1,457.5 pts × $20 = $29,150 = full tick on all 5,830 executions, but the realized slip-0→slip-1 delta is $27,795; the counter reconciles to the *naive* number, not the fills — Gate 4's "reconciles" is technically true and substantively misleading. (3) NT8's own slip-1 SharpeRatio is 0.39 vs the reported daily-MTM 1.39; the methodology gap is undocumented and the flattering figure headlines.

**Concentration/regime risks.** 2024Q3 (+$43,951) is 30% of slip-0 net; ~45% of net sits in three windows. Thursday alone is +$59,649 (41% of net); Friday is +$833. Long PF 1.20 vs short 1.07 in a market that roughly doubled suggests drift beta, and the close-carry bucket is exactly the bucket that harvests intraday drift.

**Most important un-run check.** A drift-matched control on the same window: random (or time-shifted) entries with identical session-close exit machinery and trade-count/side mix, to test whether the close bucket and long-side edge beat what raw 2023–25 NQ drift hands any always-flat-at-close trend follower. Zero new DoF. (The same config over 2022's bear market is the regime complement.)

### Controller response (adopted changes)
1. **Language corrected:** SW00 PASS certifies *pipeline determinism + cost clearance on contaminated research data*. It is NOT edge validation — that is what WFO, the drift control, and locked-forward exist for. The leaderboard row is a reference benchmark, not evidence of alpha.
2. **Adopted as next diagnostics (added to frontier, Phase 1):** (a) SW01b drift-matched control — random/time-shifted entries with identical exit machinery; (b) SW01c 2022 regime complement — canonical config over never-examined 2022 bear-market data (legitimate research data, does not touch the locked-forward future). Both zero-DoF.
3. **Gate 4 wording amended:** NT8's TotalSlippage counter reports the naive tick count; realized fill adjustment is ~4.7% milder (bar-capped). Both are now stated.
4. **Sharpe methodology documented:** NT8 SharpeRatio (0.39–0.47) is computed on monthly account returns; our 1.39 is annualized daily-MTM on dollar PnL. Both are reported in metrics.json; neither headline stands alone.
5. **Acknowledged and carried:** session-close decomposition is conditioning-on-outcome (survivorship); it motivates SW02's matched counterfactual design, not any trading decision. Thursday/quarter concentration and short-side fragility are logged as review items for every future promotion.

## 8. Smallest justified next experiment
SW01_EPISODE_AND_EXIT_ATTRIBUTION: build the read-only signal/episode exporter (new class name `SolarWaveRKLedgerV1`, zero trading-logic changes, writes per-bar Signal_Trade/Signal_Trend/Signal_Wave/TrailingStop state to CSV) so trend-episode IDs, flip counts, and path efficiency can be joined to the R01 trade ledger. No candidate promotion decisions before that attribution exists.
