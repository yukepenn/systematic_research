# BREADTH01 — Time-series momentum replication on a 15-ETF multi-asset universe

**Campaign #5 (breadth_lab) opening spec. Status: FROZEN before any return statistic is
computed. Run class: PROTECTED_CONFIRMATION (replication of a published rule; zero fitted
parameters; exactly 2 preregistered arms).**

## 0. Authorization and scope

Owner directive 2026-08-19: "我给你所有权限,不要停不要问我,一直push … 用我们过去地各种数据,
以及你能搜索到的不同的各种指标 … 互补的思考各种" — recorded here as superseding, for RESEARCH
ONLY, the 2026-08-08 NQ-only scope ruling. Nothing here touches NT8, accounts, or any live
system; this is data analysis on free public daily data. Motivation: OUTSIDE_VIEW2 (commit
fd3ea1d, verified citations) — the industry's persistent Sharpe is manufactured by breadth
(per-stream ~0.34 gross × √N at ρ≈0.05-0.07); our program is at the breadth-1 frontier. This
spec tests the industry's own workhorse on the cheapest honest universe we can hold today.

## 1. Hypothesis

The diversified time-series-momentum book (Moskowitz-Ooi-Pedersen JFE 2012; Babu et al
"Trends Everywhere" JOIM 2020; Hurst-Ooi-Pedersen century evidence) is net-positive on a
15-asset ETF universe over ~20 years INCLUDING the documented post-2012 decay, and is
complementary to our NQ book (losing-day ρ ≤ 0.25) — which would make it the program's first
qualified complementary-engine candidate after 0-for-18 constructed attempts on NQ data.

## 2. Data (downloaded AFTER this spec commits; manifest with sha256 required)

- Source: Yahoo Finance v8 chart API, daily, adjusted closes (auto-adjusted), full history.
- Universe (15 ETFs, real tradable instruments, no futures-splice artifacts):
  equities SPY QQQ IWM EFA EEM; bonds TLT IEF; metals GLD SLV; energy USO UNG;
  broad commodity DBC; FX FXE FXY UUP.
- Risk-free: ^IRX (13-week T-bill discount yield) → daily rf = yield/100/252.
- **Analysis mask: ≤ 2026-05-31** (aligned with the house dev mask; downloaded data after
  that date is stored but NOT read by this spec — it is the book's own forward window for
  future monitoring reads).
- Assets enter the book 252 trading days after their first data date (signal warm-up).

## 3. Engine (verbatim from literature; NO fitted constants)

- Signal, computed on the LAST trading day of each month per asset: sign of trailing
  252-trading-day total (excess) return.
- Position for the following month: sign × (0.10 / σ_i), σ_i = annualized EWMA(60-day
  center-of-mass) daily vol as of signal date (ex-ante). Position capped at 4× notional
  (thin-vol guard, standard in the literature implementations).
- Execution: positions effective at the close of the FIRST trading day of the next month
  (t+1 lag after the signal date — no look-ahead).
- Stream daily return: position × (asset daily total return − rf_daily). Book daily return =
  equal-weight mean of live streams. Sharpe reported on book daily returns × √252.
- Costs: 5 bps per side of traded notional at each monthly rebalance (conservative for these
  ETFs), applied to |Δposition|; 3× cost stress arm.

## 4. Arms (exactly two, both frozen here)

- **ARM_FULL (primary)**: all 15 assets.
- **ARM_EXUSEQ (preregistered fallback, reported regardless)**: drop SPY QQQ IWM (US-equity
  streams most redundant with our NQ book); 12 assets.
No other universe, lookback, vol-window, or cost variant may be computed. Multiplicity = 2.

## 5. Gates (adjudicated on ARM_FULL; ARM_EXUSEQ adjudicated only if ARM_FULL fails G5/G6)

- **G1** ≥10 assets with ≥15 years of usable data; book history ≥ 18 years.
- **G2** book net Sharpe > 0 AND year-block bootstrap (B=10,000, seed=20260819) CI_lo of
  annualized mean return > 0.
- **G3-SPLIT (standing)**: pre/post-2020 book mean daily return both > 0; iid bootstrap CI
  each: ≥1 CI_lo>0, neither CI_hi<0.
- **G4** halves (first vs second half of book history): both Sharpe same sign.
- **G5 complementarity (the reason this exists)**: against the Solar E10 ledger
  (`runs/SM06_SOLAR_HISTORY/out/e10_daily_hist.csv` 2006-2021 +
  `runs/SM01_SUBSTRATE/out/e10_daily_py.csv` 2022-2026-05, overlapping days):
  full-sample daily ρ ≤ 0.25 AND Solar-losing-day ρ ≤ 0.25 AND book net on Solar losing
  days ≥ 0.
- **G6 marginal value (fixed weights, no search)**: 50/50 risk-weighted blend (each leg
  scaled to equal realized vol over the overlap) vs Solar alone: blend Sharpe > Solar-alone
  Sharpe AND blend maxDD/CDaR5 (as fraction of leg vol) not worse than Solar-alone by >2%.
- **G7** cost stress: gates G2-G3 hold at 3× costs.
- Disclosure only: per-asset stream Sharpes (predicted band 0.1-0.5 per Trends Everywhere);
  per-year book returns; turnover; 2020-03 and 2022 episode behavior.

## 6. Decision rule (frozen)

- ALL gates pass (on ARM_FULL, or on ARM_EXUSEQ under §5's fallback clause) → adversarial
  red team → if confirmed, the book becomes **BREADTH-CANDIDATE-1**: forward-monitored
  (monthly, on the stored >2026-05-31 data at scheduled reads), spec'd toward an
  implementable form (futures/ETF mix, capital, margin) in a SEPARATE preregistered step.
  No deployment, no baseline change — candidate status only.
- G2/G3/G4/G7 fail → the replication itself fails on our data → record and close (this
  would itself be publishable-grade information given the literature).
- Only G5/G6 fail on both arms → book is real but redundant → record as
  REAL_NOT_COMPLEMENTARY; park.

## 7. Honest prior

Literature says the diversified book earned Sharpe ~1.0 gross pre-2010 and materially less
after (SG Trend net ~0.61 since 2000; post-2012 decade was weak; 2022 was a record trend
year). An ETF universe is smaller (15 vs 50+) and includes correlated sleeves → expected
book Sharpe 0.4-0.8 net, NOT 1.0+. ρ vs Solar: Solar is intraday NQ with session-close
flat; TSMOM holds overnight across 15 assets at monthly horizon — mechanically distinct;
prior ρ_losing ≈ 0.0-0.2 but the equity sleeve on trending-down months is the risk (G5
exists for exactly this). PASS is genuinely plausible here — this is the first candidate in
the program's history whose reference class has POSITIVE published out-of-sample evidence at
scale. FAIL on complementarity (G5) is the most likely failure mode.
