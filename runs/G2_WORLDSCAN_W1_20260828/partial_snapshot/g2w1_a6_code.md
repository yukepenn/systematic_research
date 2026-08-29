# G2W1 A6 CODE SCOUT — full notes (accessed 2026-08-28)

## Method note
WebSearch budget was exhausted (200/200) before this agent ran a single query. All discovery was
done via WebFetch on site-native endpoints: GitHub search API (api.github.com/search/repositories),
GitHub repo pages, TradingView tag/browse pages (tradingview.com/scripts/openingrangebreakout/),
QuantConnect strategy-library article pages, and the NinjaTrader Discourse forum (including its
/search.json endpoint). One gh CLI read-only API call was used to probe QuantConnect/Lean code
search (returned 0; legacy code-search limitation on large repos). No logins, no downloads.

## Dead ends / domain observations
- NinjaTrader forum (discourse.ninjatrader.com, "Desktop SDK - Strategies" c/7): current listing is
  Q&A/troubleshooting; NO threads sharing complete NQ/ES strategy code with results. The one
  spec-review thread ("Balance Breakout Auto Entry", topic 7315, GARY_RITTENB, 2026-07-29) contains
  no actual rules in post 1; replies are skeptical ("If this was a viable strategy, you would not be
  sharing it" — Maverick). Not a lead.
- ninjatraderecosystem.com/user-app-share-download/ → HTTP 404 (page moved/retired).
- QuantConnect/Lean Algorithm.Python: no OpeningRange* file found via listing (truncated) or legacy
  code search; QC's strategy-library articles used instead (they attach clonable code).
- GitHub "ES futures scalping" query surfaced mostly zero-star prop-firm dashboard repos; skipped.
- jefrnc/strategy-orb15-momentum (16★): equities ORB w/ walk-forward harness but publishes no
  numbers and ships no data; below lead bar, noted here only.
- Big Daddy Max ORB boost count inconsistent between views (239 on tag listing vs ~5.5K on script
  page fetch); recorded as-is.

## Raw capture (key numbers, quotes)
- giovannibrusco/zarattini-2023-orb-qqq: paper repl $138,639 net (no slip), 1,775 trades, Sharpe
  1.06; with $0.02/sh slippage → $4,860, Sharpe 0.23; +NQ-agreement filter → $44,332, t=2.05,
  Sharpe 0.77, 844 trades; "PnL crosses zero at ~2.2¢/share"; "76% of the filtered PnL is 2022";
  loses in 2017, 2020, early 2023. Sizing min(1% eq/$R, 4x eq/entry). Stop = 9:30 bar extreme,
  target 10R (hit 2-3%), ~75% stopped, ~22% EOD.
- dws-data/nas-orb-backtester: OR 09:30-09:45 ET; VP (VAH/POC/VAL) from OR bars; break beyond OR
  extreme by min threshold w/ 1-min close confirm; entry on retrace touch of VP level inside range;
  stop OR extreme, target beyond OR extreme, EOD force-close. NQ.v.0 continuous 1m Databento
  2021-2026. Longs 198 tr, 42.9% WR, +0.417R exp; shorts 80 tr, 42.5% WR, +0.558R; combined
  +21.2R/yr @1% risk. NO costs/slippage/validation mentioned.
- prashanthaitha24/nq-strategy-b-bot: 5m Inverse FVG retest inside active 15m bull FVG; long-only;
  entry when 5m low dips into FVG then closes above; stop = 5m FVG bottom − 2 pts; target 2R; window
  09:30-12:00 ET; flat 15:45. Jan2023-May2026 5m Databento (data incl.): +$17,187 /1 MNQ, 432 tr,
  53.5% WR, PF ~2.3, maxDD $786, commissions in. Long/short asymmetry: shorts 42.5% WR dropped,
  longs 56.5%. Author expects live 50-55% WR, DD 2-3x worse. Tradovate exec / Schwab feed.
- jalv92/DriftVwapPullback: source = Matteo Conti YouTube interview (no code published). Session
  VWAP (anchored 09:30); long drift = 15m close > VWAP + rising VWAP + +0.10% past hour; entry on
  first counter-direction 5m candle, next-bar open. Transcribed spec: 80pt stop / 40pt tgt long /
  50pt short; project's alt config 50/75/85. RTH, entries 10:30-15:30, flatten 15:55. Conti claims
  ~64% WR; project MNQ Market Replay Jul-Aug 2026: 23 sessions, 67 trades, ~$6,852, ~47% WR, PF
  ~1.38. Did NOT pass its own "mirror gate"; <100 trades; single regime; Conti's PF 1.18 < 1.30
  acceptance bar; 80pt stop breaches eval-account loss limits.
- je-suis-tm/quant-trading (10.6k★): Dual Thrust — range = max(HH−LC, HC−LL) over prior days;
  cap = open + K1*range, floor = open − K2*range; breach → position, reverse at opposite threshold,
  EOD flat. Repo: "all trades are frictionless. No slippage, no surcharge, no illiquidity."
  Also London Breakout (Tokyo last hour GMT7-8 sets thresholds for London open).
- QC Dual Thrust article: K1=K2=0.5, 4-day history, SPY 2004-2017: Sharpe −0.17, MDD 41.1%. Code
  clonable.
- QC Intraday ETF Momentum article: Gao/Han/Li/Zhou (+Bogousslavsky cite); first 30-min return sign
  → hold last 30 min (entry 30min before close, MOC exit); SPY/IWM/IYR; 2015-01-01→2020-08-16
  Sharpe −0.628 (benchmark 0.582); 2020 crash window (2/19-3/23) Sharpe 1.452 vs −1.466. Code
  clonable.
- quantrocket-codeload/first-last (8★, Apache-2.0): long (short) S&P when first half-hour AND
  penultimate half-hour returns both positive (negative); VIX filter restricts to high-vol
  environments; 1-min SPY + 30-min VIX; Moonshot. No perf published.
- quantrocket-codeload/trend-day (28★, Apache-2.0): Ernie Chan *Algorithmic Trading*; buy (sell)
  leveraged ETF late session after significant intraday gain (loss), hold to close. No perf
  published.
- QC Overnight Anomaly article: buy SPY at close, sell next open; Quantpedia ref; "returns are
  canceled out once transaction costs are taken into account"; IB fee model ≈25% of initial cash
  over 20y backtest.
- TradingView tag page openingrangebreakout/: LuxAlgo "Ultimate Opening Range Breakout" 9.2K boosts,
  109,313 views, 1,919 comments, open-source, pub Apr 8 (est 2025); custom OR window; std or Fib
  (0.382/0.618/1.0) expansion targets; BULL/BEAR BREAK labels w/ volume tag (HV = >20-period avg
  vol); real-time hit-rate dashboard = % of historical sessions reaching T1/T2/T3; ATR trailing
  stop w/ 5-multiplier optimizer; intra-range VP w/ POC. No performance claims.
- TradingView "Big Daddy Max ORB Strategy" (MrWickTrading, strategy-type, open source, pub May 12
  est 2025): configurable OR window; continuation = close beyond OR extreme; reversal = break then
  close back inside (failed breakout) → opposite entry; stop = OR midpoint or opposite side; R:R
  target; daily trade limits; EOD close option. Author: goal "not to claim that the strategy is
  profitable out of the box." No perf claims. Pine not audited line-by-line (page fetch).
- TradingView "15-Min ORB Strategy for NQ" (Dryeye2006, 117 boosts, 3,330 views, pub Feb 15 est
  2026, open source): OR = 09:30-09:45 ET; entry on 5m close beyond OR H/L; TP1/TP2 custom R:R,
  TP3 runner; trailing stop; author's first script.
- Mrshahidali420/ORB-Multi-Model-Indicator (13★, MIT, Pine v6, indicator not strategy): 7 active
  models (M1 Classic Crabel; M3 5-min scalper; M4 15-min; M6 FVG ORB; M7 Gold ORB; M9 Failed-ORB
  reversal; M10 Phase state-machine breakout/retest/bounce); M2/M5/M8 REMOVED after poor backtests;
  8-factor confluence score; claims non-repainting ("all higher-timeframe data uses confirmed-bar
  values"); observations on US100/XAUUSD/AUDUSD, no hard perf claims.
- honoreaa/Futures-MeanReversion (6★): spread = ES − 0.2241·NQ (static full-sample β = lookahead);
  30-day rolling z-score, daily bars 2021-01-01→2025-07-22; claims $391,568 / ~86.25% ann / Sharpe
  1.67; NO costs; author self-flags "Overfitting & Look-Ahead Bias" as open issues.
- alfredoberlose/ORB-Day_Trading_Strategy-QQQ (5★) + pepgman/ORB_Zarattini + hsaeed22058 — more
  Zarattini replications (not separately leaded; giovannibrusco is the strongest).
- Ascensao/Intraday-momentum-strategy (6★): implements SSRN 4824172 "Beat the Market: An Effective
  Intraday Momentum Strategy for S&P500 ETF (SPY)" (Zarattini/Concretum, 2024); VWAP + dynamic
  "noise" bands from σ_open by time-of-day; UB/LB band cross → long/short w/ trailing; includes
  Pine port (concretum_bands_pine_code.txt); data 2019+ (Polygon); "replication aligns closely with
  the original paper's yearly returns" 2016-2024; exact metrics live in scripts, not README.
- Other repos logged, below bar: nessos666/nq-strategy-builder (6★), s583381747/nq-quant (ICT chain,
  5★), Aksee123/nq1_Scalping_Strategy (4★ Pine VP scalper), seady22/GambiTick-AI (DQL ES/NQ, 1★),
  kadennaj/nq-futures-strategy, johnsonyang567 NinjaScript top-down, quantrocket NSE/crypto items.

## Second-pass captures (verified by re-fetch 2026-08-28, same session)
- giovannibrusco/zarattini-2023-orb-qqq RE-VERIFIED: replicates Zarattini & Aziz 2023 SSRN 4416622,
  QQQ 5m ORB (trade first-bar direction, skip doji; stop = 09:30 bar extreme = 1R; target 10R;
  ~75% stopped, ~22% EOD flat; sizing min(1% eq/$R, 4x eq/entry)). No-slip $138,639 / Sharpe 1.06 /
  1,775 tr; $0.02/sh slip → $4,860 / 0.23; +NQ-09:25-agreement filter $44,332 / 0.77 / 844 tr;
  QQQ-premarket placebo $25,191 / 0.57. Break-even ~2.2c/sh slippage. 76% of filtered PnL = 2022;
  loses 2017, 2020, early 2023.
- prashanthaitha24/nq-strategy-b-bot RE-VERIFIED: 5m bull FVG unfilled, nested inside active 15m
  bull FVG (5-pt buffer); bar low dips into 5m FVG and closes back above FVG top → long; window
  09:30-12:00 ET; stop FVG bottom −2pts; target 2R; flat 15:45. Databento NQ 5m Jan2023-May2026,
  CSV INCLUDED in repo. 1 MNQ long-only: +$17,187, 432 tr, 53.5% WR, PF ~2.3, maxDD $786, 4/4 yrs
  positive, 13/14 qtrs. WR drifts UP by year: 46.5→52.5→57.3→68.1% (2023→2026) — regime dependence
  or leak-with-recency? Shorts 42.5% WR dropped. Author: real DD "2-3x worse", expect 50-55% WR.
- Ascensao/Intraday-momentum-strategy RE-VERIFIED: implements SSRN 4824172 (Zarattini/Barbon/Aziz
  'Beat the Market', SPY); VWAP + dynamic σ_open time-of-day noise bands, UB/LB signals; Polygon
  minute data 2019+; Pine port included (concretum_bands_pine_code.txt); "replication aligns
  closely with the original paper's yearly returns" 2016-2024.
- honoreaa/Futures-MeanReversion RE-VERIFIED: ES−0.2241·NQ spread (OLS β on FULL sample =
  structural lookahead), rolling z entries/exits, daily 2021-01→2025-07; claims $391,568 on $100k,
  ~86%/yr, Sharpe 1.67, NO costs; author: "I also assume that I have some slight look-ahead bias
  in my code."
- jalv92/DriftVwapPullback RE-VERIFIED: Conti (ex-Nordea MM) interview transcription; session VWAP
  09:30; drift long = 15m close > VWAP AND VWAP rising AND +0.10% past hour (mirror short); entry =
  first counter-direction 5m candle, market at next bar open; 50pt stop / 75pt long / 85pt short
  targets (recommended cfg); window 10:30-15:30, flatten 15:55. MNQ Market Replay Jul 7-Aug 6 2026:
  67 tr, +$6,852, ~47% WR, PF ~1.38. Mirror gate NOT passed; source PF 1.18 < 1.30 acceptance bar.
- QC Dual Thrust article RE-VERIFIED: range = max(HH−LC, HC−LL) N=4 days, K1=K2=0.5; SPY hourly
  2004-2017: Sharpe −0.17, MDD 41.1%; code clonable (partial in page).
- NEW this pass: nightshiftquant/-NSQ-Trading-Bots-NinjaTrader-8 — NSQ_OvernightBreakout.cs (NQ,
  range 00:00-02:30 ET, trade 02:30-04:00, 1 trade/session, hard exit 04:00; claims 2022-24
  +$22,840, 54.1% WR, PF 1.91, Sharpe 1.58, maxDD −$2,480, 312 tr) + NSQ_ATRChannelScalper.cs (ES
  04:00-09:15 EMA+ATR band premarket fade; +$18,620, PF 1.74). No commission/slippage disclosed;
  PnL/maxDD ~9:1 implausibly smooth; 1★; AI-slop suspicion — but code is NT8-native and rules exact.
- NEW: noahgniffke-sys/mes-smc-backtest — MES SMC suite (sweeps/BOS/IFVG/session flow, 13+ script
  versions); yfinance or local CSV 5m/1h/1d ~3y; claim "Asia-low sweep → BOS → FVG entry on the
  5-minute chart produced a 77-79% win rate at 2R" ⇒ ~+1.3R/tr expectancy = implausible; suspect
  sweep/BOS detection lookahead + touch fills + yfinance data quality.
- NEW: e49nana/lokus-research — MES/MNQ/MYM Databento; Phase 1a SMC "Perfect Confluence" M15 CLOSED
  no edge after fees (gross +$1.69/tr, t≈0.28); Phase 2a TORB (time-of-day reversal breakout,
  "replicating Wang et al. 2019", M1) pending; frozen params, Bonferroni α=0.0167, 10k bootstrap,
  sealed holdout 2024-07→2025-07, 428 tests. Governance-grade; mirrors our doctrine.
- NEW: alienblack/Intraday-Momentum-Strategy-SPY-ETF-Python- — second independent Zarattini-style
  SPY impl (time-of-day sigma gap-adjusted bands, semi-hourly decisions, session-VWAP trail,
  vol-target 4x cap, $0.0035+$0.001/sh costs); "Recent runs on 2024 data show weak Sharpe" —
  contrasts with Ascensao's alignment claim.
- NEW: robbyrobaz/nq-l2-scalping — "Strategy 020": NQ ORB 09:30-09:40 (10x1m bars), stop 16 ticks
  (4pt), target 128 ticks (32pt); claim "Validated Edge: PF 4.5, 50 trades, 36% WR (21-day
  backtest)"; IBKR 1m bars; PF math internally consistent but n=21 days; 1m bars cannot sequence
  4pt stop vs target intra-bar. Paper-trading phase.
- NEW: greybeard-code/gbBacktester — C# tick-level L1 backtester over NT Market Replay Parquet;
  "no look-ahead — fills happen before the strategy sees the bar"; limit fills on penetration not
  touch; stops trigger on last trade, fill at quote; Apex trailing-threshold prop sim; Monte Carlo
  tools; no perf claims. TOOLING lead only (our DOM/Market-Replay collection is PAUSED — do not
  read this as a data-collection prompt).
- NEW: Pikachunou/nq-quant-research — empty scaffold (EMA baseline, no results). Skipped.
- NEW: ninjatraderecosystem.com/?s=opening+range+breakout — TurnKeyORB + ORBie (paid, no rules
  disclosed → not leads), Opening Range Indicator + Accumulation Distribution Range Breakout
  (free UAS). Search works; user-app-share-download root 404s.
- NEW: tag page also fetched fresh: LuxAlgo Ultimate ORB 9.2K boosts / 1,919 comments / 109,324
  views; ATR trail "background optimization testing five multipliers simultaneously" = live
  in-sample selection displayed as feature; Hit Rate Dashboard = % sessions reaching each target
  (measurable distributional claim). Indicator, not strategy; no perf.

## Final lead selection (15)
A6-01 giovannibrusco ORB repl · A6-02 dws-data NQ ORB retrace · A6-03 nq-strategy-b-bot nested FVG
· A6-04 ict-cameron falsified · A6-05 lokus-research · A6-06 mes-smc 77-79% claim · A6-07 Ascensao
Zarattini-momentum repl (+alienblack cross-ref) · A6-08 QC Gao intraday momentum · A6-09 je-suis-tm
Dual Thrust/London Breakout (+QC Dual Thrust cross-ref) · A6-10 nightshiftquant NT8 overnight ·
A6-11 DriftVwapPullback · A6-12 honoreaa ES-NQ spread · A6-13 Big Daddy Max ORB reversal branch ·
A6-14 LuxAlgo hit-rate dashboard · A6-15 gbBacktester fill-mechanics tooling.
Dropped: Dryeye2006 15-min ORB NQ (first script, no perf — Big Daddy covers the mechanism),
Mrshahidali420 (indicator, models pre-culled), quantrocket first-last/trend-day (no perf published),
Pikachunou (scaffold).
