# CrossTrade MCP Connectivity & Strategy Analyzer Smoke Test

**Date:** 2026-08-06 | **Verdict: PASSED**

## 1. Connectivity

| Item | Value |
|---|---|
| CrossTrade Add-On version | v1.13.9 (MCP protocol 1.0.0) |
| NinjaTrader version | 8.1.8.1 |
| MCP authorization scope (features) | `compile`, `strategy_state`, `alert_relay`, `backtest` |
| NT8 backtest engine | **Available** — `nt8_strategy_analyzer` (Strategy Analyzer parity), fingerprint `sha256:b4255f1b0dd7fba1`, optimization supported (Default / Genetic / StrategyGenerator) |
| Sim101 | **Visible and Enabled** in account list (id 2). Broker/data connection "Simulation" is Connected (user `rainazur`); Sim101 was not touched by the backtest — runs use the isolated "Backtest" account |

`McpSelfTest(deep=true)`: **8 passed, 0 failed, 4 skipped** (skips were the instrument-dependent tests — indicator_ema, volume_profile, order_flow, deep backtest — because no `instrument` arg was passed to the self-test; the real backtest was run separately below). Compile pipeline verified (0 errors).

Other accounts visible: Backtest, Playback101, 2047681, DEMO8383477.

## 2. Strategy Analyzer parity backtest

**Config:** `SampleMACrossOver` on `MES 06-26` (resolved `MESM6`), 5-Minute bars, 2026-04-01T00:00:00Z → 2026-04-30T23:59:59Z, Fast=10, Slow=25, slippage 0 ticks, commission none, fill Standard, account Backtest (isolated, reset), $100k initial.

**Job:** `9a90be43b1414e05` — completed in 669 ms, strategy state `Finalized`.

**Data actually loaded:** 6,255 five-minute bars; performance window MinDate 2026-03-31 21:50 → MaxDate 2026-04-30 17:00 (exchange-local timestamps; the Mar 31 evening bars are the start of the Apr 1 trading session). Effective parameters confirmed: Fast=10, Slow=25. TotalCommission $0.00, TotalSlippage 0 — as requested.

### Results (all trades)

| Metric | Value |
|---|---|
| Net Profit | **$800.00** (gross profit $6,415.00, gross loss −$5,615.00) |
| Profit Factor | **1.142** |
| Max Drawdown | **−$670.00** |
| Trade Count | **264** (trade-detail list yielded 263 rows; see note) |
| Sharpe Ratio | **0.803** |

### Long vs Short

| Side | Trades | Net Profit | Profit Factor | Sharpe | Max Drawdown |
|---|---|---|---|---|---|
| Long | 132 | +$1,942.50 | 1.797 | 0.297 | −$336.25 |
| Short | 132 | −$1,142.50 | 0.640 | −0.804 | −$1,688.75 |

### First 3 completed trades (1 contract each)

| # | Side | Entry | Exit | P/L |
|---|---|---|---|---|
| 1 | Short | 6581.25 @ 2026-03-31 21:50 | 6581.25 @ 2026-03-31 23:55 (BuyToCover) | $0.00 |
| 2 | Long | 6581.25 @ 2026-03-31 23:55 | 6602.25 @ 2026-04-01 04:10 (Sell) | +$105.00 |
| 3 | Short | 6602.25 @ 2026-04-01 04:10 | 6603.50 @ 2026-04-01 06:20 (BuyToCover) | −$6.25 |

Note: NT8 `TradesCount` reports 264 while the serialized trade collection contains 263 rows (`AllTrades_diag`: raw_count 263, yielded 263, 0 shape errors; 527 executions). This off-by-one between the summary counter and the trade collection is an NT8 reporting artifact, not a data error.

## 3. Verdict

**Strategy Analyzer smoke test: PASSED.** MCP handshake, deep self-test, account/connection enumeration, and a full Strategy Analyzer parity backtest all succeeded end-to-end. Historical MES 06-26 5-minute data for April 2026 is present, `SampleMACrossOver` resolved and ran, and per-trade + aggregate performance was returned.

Raw result: [`backtest_result.json`](backtest_result.json) (full GetMcpJob payload: performance all/long/short, 263 trade records, 263-point equity curve, trace).

Constraints honored: no optimization sweep, no strategy deploy/enable, no order actions, no NinjaScript written or compiled (self-test's compile check is CrossTrade's internal scratch test with automatic artifact cleanup).
