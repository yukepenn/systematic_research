# BACKTEST vs LIVE audit (directive §8, §26) — post-first-pass, QC'd

## Classification of every result object

| Class | Count | Objects | Verdict |
|---|---|---|---|
| STRATEGY_ANALYZER_BACKTEST | 69 weekly/period summaries + 1 master (OTRIMG-0002) + 2 Analysis views | the whole weekly series 2025-02→2026-08 | SINGLE-STRATEGY backtest slices. Author admission (OTRIMG-0098, verbatim): "同时run了几个strategy, 所以只有通过strategy analyzer来分析单个strategy performance" — SA was his per-sleeve inspection tool |
| TRADE_PERFORMANCE (execution) | OTRIMG-0005 (2/3/2025, 35 tr, −$616.30), OTRIMG-0152 + OTRIMG-0154 (Jun 2026, +$11,860.30 / +$8,503.24, real commissions $141.20/$96.76) | actual executed trades (live or sim — account tag not visible) | STRONGEST live-evidence class |
| SOCIAL_NOTE headline cards | ~50 | weekly PnL claims | Every checkable card matches an SA (or TP) report to the dollar → cards = report summaries, NOT independent account statements |
| AUTHOR_REPORTED (text) | ~$150k+ full-year 2025; ~$500-600/day normal; $10-13k/mo normal (Nov 2025); $22k single trade (Jun 2026) | comment statements | Class A statements about claims, Class C about reality |

## Key findings

1. **Contemporaneity is proven for the weekly series**: 58/70 reports have capture-lag
   = 0 days (dual OS clocks: macOS menu bar + remote Windows taskbar agree in every
   frame); 66/70 ≤ 3 days. The three >3d exceptions are the Jul-6-2025 session batch-
   documenting 3/15→4/30 (+67d) and 5/1→6/27 (+9d), and OTRIMG-0138 (+5d).
   → The weekly numbers were generated at week-end on a Friday/Saturday ritual, not
   reconstructed later. This defeats the bulk retrospective-fabrication scenario.
2. **Contemporaneous ≠ frozen-parameter forward test.** The settings panes show the
   strategy was RE-TUNED repeatedly (see PARAMETER_VERSION_TIMELINE). A week's SA
   report is run with THAT week's current parameters; nothing proves the parameters
   were fixed before the week started. Risk classification: report-level honesty HIGH,
   walk-forward purity UNKNOWN → the series is best read as "development log of a
   live-iterated system", not an audited track record.
3. **Live execution confirmed at three points**: 2/3/2025 (day after master backtest,
   SolarWindRK running on NQ MAR25, tab visible), and Jun 2026 TP frames with real
   commissions; author statements (12/27/2025: several strategies live on $60k,
   day-margin ~3k; 5/10/2026: daily auto-flatten 16:59:30 ET) corroborate continuous
   live operation between those points.
4. **What is NOT proven**: account-level PnL for any period (no account statements,
   no NT8 account tab with balances); that posted weekly numbers equal account
   results (they are single-strategy, $0-commission from ~2025-02-28 onward);
   sim-vs-live for the TP frames.
5. **Author's own reconciliation** (OTRIMG-0098): real ≈ posted ×0.9 when winning,
   ×1.1 when losing (commission ~$2/RT + slippage). TP frames show ≈$1.04/side
   ($2.08/RT) — consistent with his estimate; the Feb-2025 SA template rate $4.18/RT
   and the $5.68/RT runs (2/23-24) were template experiments, later abandoned for $0.
