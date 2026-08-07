# DR-C — Execution Realism & False Backtest Profitability (DR-S10 + DR-S12)

Role: EXECUTION_SKEPTIC deep-research deliverable. Date: 2026-08-07.
Scope: scalp execution realism for retail-speed 1-lot NQ trading (DR-S10) and the catalogue
of causes of spuriously profitable short-horizon backtests (DR-S12).
Constraints respected: audited commission $2.18/side NQ; C1 screen = commission + 1 tick
slippage per execution = $14.36/RT = 2.872 ticks; C2 stress = 4.872 ticks; passive fills are
NOT modeled without queue-quality data (mandate §24, EXECUTION_MODEL.md).

Method note: findings below are from published papers and practitioner sources located
2026-08-07 (links inline). Where a number is a practitioner claim rather than a measured
study, it is flagged `[practitioner]`. No data analysis was run for this document; every
claim we can verify on our own tick data is turned into a checklist test in §2 or a
hypothesis in §4.

---

## 1. Quantitative findings

### 1.1 NQ top-of-book spread behavior (DR-S10a)

**No published study reports an exact "% of time NQ BBO is 1 tick wide" figure.** This is a
measurable gap we can close ourselves with our own L1/BBO probe (H-EXEC-1, §4). What the
literature and practitioner record does establish:

- **RTH baseline: 1 tick is the norm, 2 ticks common in vol.** Practitioner references
  consistently describe NQ RTH top-of-book as 0.25–0.50 points (1–2 ticks) with hundreds of
  contracts within a few ticks of the inside
  ([TradeAlgo NQ guide](https://www.tradealgo.com/trading-guides/futures/nq-futures-trading-guide) `[practitioner]`).
  Academic LOB studies of E-mini index futures describe the spread as sitting at the minimum
  tick with substantial depth relative to event size during active hours
  ([Reduced form modeling of limit order markets, arXiv:1006.4517](https://arxiv.org/pdf/1006.4517);
  [Market Liquidity and Depth on Floor-Traded and E-Mini Index Futures](https://www.researchgate.net/publication/265449645)).
- **NQ is materially thinner than ES.** ES RTH spread is described as "almost always one
  tick"; NQ is the faster, thinner, more momentum-sensitive contract
  ([Bookmap NQ instrument page](https://bookmap.com/content/instruments/nq);
  [thortradecopier ES vs NQ](https://thortradecopier.com/blog/es-vs-nq-vs-mes-vs-mnq-which-to-day-trade) `[practitioner]`).
  Expect NQ's 1-tick fraction to be visibly below ES's, especially off-RTH and in vol spikes.
- **ETH/overnight: 2–6 ticks.** Practitioner measurements put overnight NQ spreads at
  1.00–1.50 points (4–6 ticks) vs 0.25–0.50 RTH, with the thinnest conditions in the Asia
  session, the midday lull, and the minutes around the 17:00 ET maintenance break
  ([QuantVPS NQ market hours](https://www.quantvps.com/blog/nq-mnq-futures-market-hours) `[practitioner]`;
  [TradeFundrr session guide](https://tradefundrr.com/blog/futures-session-times) `[practitioner]`).
- **Intraday shape: U-shaped activity, spread tightening into the close.** Frequency of
  trades, volume and spreads exhibit consistent intraday patterns — spreads decrease and
  depth increases over the RTH day; order-flow-imbalance volatility is U-shaped with
  heightened open/close activity
  ([Returns and Order Flow Imbalances, arXiv:2508.06788](https://arxiv.org/pdf/2508.06788)).
- **Implication for our cost model:** a flat 1-tick spread assumption is only defensible
  RTH-ex-events. Any strategy whose profit concentrates in ETH, the first minutes of RTH, or
  scheduled-release windows must carry a wider spread state (C2 or exclusion).

### 1.2 Market-order slippage, 1-lot NQ at retail latency (DR-S10b)

- **Structural floor: half-spread.** A marketable order pays (at minimum) half the quoted
  spread vs mid. With NQ 1 tick wide, that is 0.5 tick = $2.50/side even with zero latency
  and zero impact. A 1-lot does not sweep levels in RTH — top-of-book depth is typically
  tens to hundreds of contracts — so *price impact* is ~0 for our size; the risk is
  **latency drift**: the market moving between decision and exchange receipt.
- **Practitioner consensus for 1-lot ES/NQ in active hours: 0–1 tick beyond the touch.**
  0.25–0.5 ticks/side average is described as normal-to-acceptable; fast NQ moves can eat
  2 ticks ([Optimus Futures price impact](https://learn.optimusfutures.com/price-impact-analysis) `[practitioner]`;
  [chartmini scalping math](https://chartmini.com/blog/scalping-strategies-guide) `[practitioner]`).
  Off-hours and news windows: 1–2+ ticks routinely
  ([TradeFundrr](https://tradefundrr.com/blog/best-futures-to-trade-at-night) `[practitioner]`).
- **Our C1 (1 tick per execution) therefore decomposes as ≈ 0.5 tick half-spread + 0.5 tick
  latency drift/queue-jump** in RTH conditions — a *median-realistic, not conservative*
  assumption for RTH market orders; it is optimistic for ETH/news. Never double-count: if a
  future model prices half-spread explicitly from BBO data, the slip allowance must drop to
  the residual (EXECUTION_MODEL.md convention).

### 1.3 Retail latency distributions (DR-S10d)

Concrete figures found (all `[practitioner]`, none vendor-audited):

| Path | Round-trip | Source |
|---|---|---|
| Network floor NYC ↔ CME Aurora | ~12 ms | [PickMyTrade Rithmic latency](https://blog.pickmytrade.io/rithmic-latency-secrets-live-sim-fills-2025/) |
| Network floor Seattle ↔ Aurora | 14–18 ms | same |
| Network floor Europe ↔ Aurora | 100–150 ms | same |
| Co-located Chicago VPS, Rithmic | ~0.5–5 ms | same |
| Dedicated NYC server, Rithmic order round-trip | ~77 ms | [NinjaTrader forum, market order execution times](https://forum.ninjatrader.com/forum/ninjatrader-8/platform-technical-support-aa/1119171-market-order-execution-times) |
| Live MNQ market-order round-trip via Rithmic (retail) | ~170 ms | same thread |
| Standard VPS under load (opens/news) | spikes 250 ms+ | PickMyTrade |
| CQG vs Rithmic | comparable; CQG a few ms slower | [DamnPropFirms comparison](https://damnpropfirms.com/trading-guides/rithmic-vs-cqg-futures-data-feeds-compared/) |

Add NinjaTrader's own strategy-thread processing (OnBarUpdate scheduling, order submission
overhead): platform round-trips of 100–300 ms are the realistic planning number for our
stack, with fat right tails (>500 ms) exactly when volatility is highest — latency spikes
are *positively correlated with the moments a scalp signal fires*. Consequences:

- At NQ's RTH tick frequency (multiple book/trade events per second), 100–300 ms latency
  means **1–3+ price-relevant events occur between decision and arrival**. The Stoikov–Waeber
  result quantifies the decay: an imbalance-informed execution edge worth ~1/3 of the spread
  at 1 ms latency dissipates rapidly as latency grows
  ([Reducing Transaction Costs with Low-Latency Trading Algorithms, QF 2016](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2661618)).
  Any signal whose half-life is < ~1 s is **not retail-executable**; our latency grid
  {0, next-event, 250ms, 500ms, 1s, 2s, 5s} must treat 250–500 ms as the realistic center,
  not the stress case.

### 1.4 Queue position, fill probability, adverse selection of passive fills (DR-S10c)

NQ matches **pure FIFO price-time priority**
([CME supported matching algorithms](https://cmegroupclientsite.atlassian.net/wiki/x/r5lAGw);
[Databento CME matching algorithms](https://databento.com/blog/cme-matching-algorithms-explained)).
A retail order joining the best bid joins the *back* of the queue. The literature is
unambiguous that back-of-queue passive fills are toxic:

- **Queue value ~ half-spread.** Moallemi & Yuan model queue position value in FIFO books;
  for large-tick instruments queue position value is of the same order of magnitude as the
  half-spread, and adverse selection cost *increases with queue position* (back of queue is
  filled disproportionately when the level is about to trade through)
  ([A Model for Queue Position Valuation in a Limit Order Book](https://moallemi.com/ciamac/papers/queue-value-2016.pdf);
  [SSRN 2996221](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2996221)).
- **Measured adverse-fill rates in CME futures, April 2024, basic join-the-touch strategy:
  NQ 65.8% of passive fills adverse (1,269/1,929); ES 81.5%; CL 82.9%; ZN 88.8%** — where
  "adverse" = first post-fill quote move is against the position
  ([Market Simulation under Adverse Selection, arXiv:2409.12721](https://arxiv.org/html/2409.12721v2)).
  The same paper's central point: simulators that draw fills independently of price moves
  systematically underestimate adverse fills, because in reality **price cannot trade
  through your limit without filling it first** — the fills you are guaranteed to get are
  exactly the bad ones. They calibrate a realistic non-adverse fill probability of only
  ρ ≈ 0.2 for touched-but-not-traded-through levels.
- **Negative drift theorem.** Limit-order fills *coincide with* adverse price moves; the
  assumption of "low-cost random fills" in classic market-making models is wrong in sign
  ([The Negative Drift of a Limit Order Fill, arXiv:2407.16527](https://arxiv.org/abs/2407.16527), ZN empirics).
- **Front vs back of queue measured:** front-of-queue fills average ≈ −0.06 bp post-fill,
  back-of-queue ≈ −0.78 bp — an order of magnitude worse
  ([The Market Maker's Dilemma, arXiv:2502.18625](https://arxiv.org/pdf/2502.18625), crypto
  perp data, but the FIFO mechanism argument transfers).
- **Conclusion (locks in mandate §24):** "limit touched ⇒ filled" converts the *worst*
  subset of fills you would actually receive into the *full* set of fills at zero cost. On a
  1-tick-wide book this manufactures ~1 tick of phantom edge per fill (you book the spread
  you did not earn) *plus* omits the adverse-selection drift. Passive execution stays
  banned from our backtests until we have queue-quality (MBO/L3) data; hftbacktest-style
  probabilistic queue models (power/log advancement between L2 snapshots) are the minimum
  credible machinery if we ever go there
  ([hftbacktest queue models](https://hftbacktest.readthedocs.io/en/latest/tutorials/Probability%20Queue%20Models.html)).

### 1.5 Minimum gross edge for a retail NQ scalper (DR-S10f)

No peer-reviewed "minimum ticks" estimate exists for retail futures scalping; the arithmetic
and practitioner numbers converge tightly, though:

- Dead cost per RT, market orders both ways, RTH: commission 0.872 ticks + spread ~1 tick +
  latency slip ~0.5–1 tick ⇒ **≈ 2–3 ticks/RT** — exactly our C1 = 2.872 ticks.
  Practitioner sources: "1 tick spread + 0.5 tick slippage each way = 2 ticks dead cost; a
  2-tick target is already eaten; experienced NQ tick-scalpers rarely work below 4-tick
  targets" ([chartmini](https://chartmini.com/blog/scalping-strategies-guide) `[practitioner]`;
  [ForTraders tick scalping](https://fortraders.com/blog/tick-scalping) `[practitioner]`).
- Breakeven win-rate arithmetic: with a 4-tick target/stop and ~1.5–2.9 ticks RT cost, the
  required win rate is 57–68% *before* any adverse selection — a hurdle very few signals
  clear ([myfundedfutures scalping guide](https://myfundedfutures.com/blog/scalping-futures-trading) `[practitioner]`).
- A 55%-accurate direction signal with 0.75-tick average slippage per fill (vs 0.25
  assumed) flips to net-negative — the entire P&L of a marginal scalp lives inside the
  slippage assumption ([journalplus slippage analysis](https://journalplus.co/metrics/slippage-analysis/) `[practitioner]`).
- **Campaign rule this implies:** any candidate whose *gross* mean edge per RT is below
  ~3 ticks (C1) is dead on arrival; survivors must hold positive expectancy at C2
  (4.872 ticks) to claim robustness. MNQ (C1 = 6.6 ticks/RT) is not a scalp research
  vehicle — confirmed independently by the friction arithmetic above.

### 1.6 The catalogue of short-horizon backtest illusions (DR-S12)

1. **Bid-ask bounce / Roll mechanism.** Trade prints alternate between bid and ask, inducing
   negative lag-1 autocorrelation in trade-price returns even when mid is a random walk
   (Roll 1984; [Ødegaard lecture notes](https://ba-odegaard.no/teach/notes/liquidity_estimators/roll_spread_estimator/roll_lectures.pdf);
   [Princeton microstructure-noise notes](https://www.princeton.edu/~yacine/liquidity.pdf)).
   Roll: spread s ⇒ cov(Δp₁,Δp₂) = −s²/4. On NQ with s = 1 tick, last-trade bars carry ~½
   tick of *mechanical* mean reversion per print — the same order as our entire cost budget.
   Any 1–2 bar mean-reversion "edge" measured on Last-trade data is presumed bounce until
   proven otherwise. Zero-cost backtests of short-horizon mean reversion routinely show
   ~50% annualized returns that are pure microstructure
   ([arXiv:2305.08241](https://arxiv.org/pdf/2305.08241)).
2. **Bar-close fantasy fills.** Signal computed on bar N's close, fill assumed *at* bar N's
   close. The close is the last print of the bar — it is known only after the bar ends, and
   the fill additionally crosses the spread. Earliest honest fill: next bar/event open +
   latency + half-spread ([ForTraders bias guide](https://fortraders.com/blog/how-to-avoid-bias-in-backtesting)).
   At scalp horizons the close-to-next-open drift is the *signal itself* in many spurious
   strategies (it embeds the bounce of item 1).
3. **Touched-limit-assumed-filled.** See §1.4: on NQ ~66% of real touch fills are adverse;
   non-adverse fill probability at a touched level ≈ 0.2. Platforms fill at any touch by
   default (TradingView `backtest_fill_limits_assumption = 0`,
   [TradingCode explanation](https://www.tradingcode.net/tradingview/limit-fill-assumption/);
   NT8 fills limits on OHLC touch at default resolution). Phantom edge ≈ spread + adverse
   drift per passive fill.
4. **Same-bar stop/target ambiguity.** OHLC bars destroy intra-bar path. Measured on NQ: for
   a 10-point bracket, **18.47% of bars are ambiguous, and best-case vs worst-case ordering
   differs by 3,695 NQ points ($73,900) per 1,000 trades**
   ([When Backtests Guess, SSRN 6240638](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6240638)).
   NT8 default assumes Open→High→Low→Close traversal — an *optimistic* convention for
   longs with tight brackets ([NT8 forum](https://forum.ninjatrader.com/forum/ninjatrader-8/strategy-development/1087741-stop-and-profit-on-same-daily-bar-during-back-test)).
   Tighter brackets at scalp scale push the ambiguous fraction far higher.
5. **Lookahead in bar construction.** Renko/range/volume bars are built from completed
   future paths (a renko brick's close time and even existence depends on where price went);
   platform-rebuilt synthetic bars can backfill from higher timeframes; bars stamped at
   close-time but indexed as if known at open. Freqtrade ships an automated lookahead
   analyzer precisely because this is endemic
   ([freqtrade lookahead analysis](https://www.freqtrade.io/en/stable/lookahead-analysis/);
   [QuantifiedStrategies on renko backtests](https://www.quantifiedstrategies.com/renko-trading-strategy/)).
   Our Solar campaign's hot-reload/versioning discipline exists for a sibling reason.
6. **Back-adjustment artifacts on continuous contracts (our NQ series is back-adjusted).**
   The Panama splice adds a constant to all history at each roll; historical *levels* are
   fiction ([QuantPedia continuous futures](https://quantpedia.com/continuous-futures-contracts-methodology-for-backtesting/);
   [QuantStart](https://www.quantstart.com/articles/Continuous-Futures-Contracts-for-Backtesting-Purposes/)).
   Quantification for NQ 2023–2025: quarterly carry ≈ price × (r − d) × 0.25. With r ≈ 5%,
   d ≈ 0.8%, NQ 15,000–21,000 ⇒ **~150–220 points per roll**; the canonical window spans
   ~8–9 rolls ⇒ **cumulative offset ≈ 1,200–1,900 points** between adjusted and true prices
   at the start of the window. Consequences: (i) every *level-based* signal — round hundreds
   (NQ 100-point handles), 25/50-point grids, prior-day settlement, gap fills, "psychological"
   levels — is displaced by a non-round offset for all history except the current contract
   segment: **a round-number study on back-adjusted data is testing pseudo-levels ~1,000
   points away from what traders actually saw**; (ii) tick-grid alignment survives (offsets
   are multiples of 0.25) but percentage/log returns are distorted at old, offset-shrunken
   price levels; (iii) roll-gap bars can print phantom 1-bar moves if splice timing is off.
   **Correct handling:** compute level signals on *unadjusted single-contract prices* (per
   DATA_INVENTORY open item — our tick probes already use single contracts), or carry the
   per-segment cumulative offset and de-adjust before any modular/level arithmetic; returns
   and P&L may still be computed on the adjusted series. Round-number/level clustering is a
   real documented phenomenon in true prices (Osler on FX stop/TP clustering; Donaldson &
   Kim on DJIA 100s; [Tradeciety summary](https://tradeciety.com/the-order-clustering-effect-around-round-numbers)),
   which is exactly why testing it on adjusted prices is silently fatal — the effect exists,
   and the adjusted series cannot see it.
7. **Session-boundary artifacts.** CME equity-index Globex: halt 16:00–16:30 ET? No —
   NQ trades 18:00→17:00 ET with the 16:15–16:30 pause removed in current schedule; daily
   settlement 16:00 ET, maintenance 17:00–18:00 ET. Liquidity dries up and spreads widen
   into 16:59 and around the 18:00 reopen, which can gap
   ([CME trading hours](https://www.cmegroup.com/trading-hours.html);
   [session guides](https://proptradingvibes.com/blog/futures-market-hours) `[practitioner]`).
   Exit-on-session-close backtest fills assume normal liquidity at exactly the thinnest
   minute of the day. Also ours specifically: NT8 counts a data-end open position in
   totals while the serialized trade list may omit the boundary exit (CLAUDE.md known
   quirk) — reconcile counts, and never let a scalp study's edge concentrate in the
   17:00/18:00 or 09:30 boundary bars without a dedicated liquidity stress.
8. **Volume leakage.** (i) Using the forming bar's volume/high/low in the signal that
   trades that same bar; (ii) "relative volume" filters normalized by full-day volume not
   yet known intraday; (iii) roll-week volume splits between two contracts, so
   continuous-series volume collapses/doubles around rolls, corrupting volume filters;
   (iv) volume-derived bars (volume/renko) re-timestamped at completion embed future flow.
9. **Selection bias / multiple testing.** The best of N tried configs has an inflated
   Sharpe even under pure noise. Corrections: Deflated Sharpe Ratio, PBO, haircut Sharpe
   ([Bailey & López de Prado, SSRN 2460551](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551);
   [Harvey & Liu, Backtesting](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2345489);
   White 2000 Reality Check). Our registry (every tested config sequence-numbered) is the
   precondition for computing these; the Solar campaign already measured PBO 0.48–0.90 on
   parameter selection — scalp-lab candidate counts will be far larger, so DSR/PBO
   reporting is mandatory at candidate promotion.
10. **Uniform-cost fantasy.** Applying RTH costs to ETH/news trades. With ETH spreads 4–6
    ticks `[practitioner]`, a strategy that "earns" 2 ticks/trade overnight under a 1-tick
    spread assumption is losing money in reality. Cost must be *state-dependent* or the
    strategy must be session-restricted.
11. **Last-trade-only data illusion (our L1 reality).** With Last-tick data and no BBO, we
    cannot see which side a print hit, nor the spread state at decision time. Any fill
    price derived from a *trade print* rather than the *opposing quote* understates cost by
    ~half-spread on average, and trade-print mid-estimates inherit bounce noise (item 1).
    This makes the BBO probe (DATAPROBE01 path b) strategically valuable.

---

## 2. RED-TEAM CHECKLIST — failure modes with mechanical detection tests

Run every test on any scalp backtest before it may enter the candidate registry. Each test
names its pass/fail rule. "Backtest" = event-study or strategy P&L stream with trade list.

| # | Failure mode | Mechanical detection test | Fail rule |
|---|---|---|---|
| R1 | Bid-ask bounce edge | Re-run with every entry price moved 1 tick against trade direction and every exit price 1 tick against (total +2 ticks/RT beyond modeled cost). Separately: compute lag-1 autocorr of 1-event and 1-bar Last-price returns over the sample; compute strategy P&L by holding-time decile. | Net ≤ 0 after the 1-tick-against shift, OR >60% of gross P&L in holding times ≤ 2 events/bars while lag-1 autocorr < −0.05 ⇒ presumed bounce; reject or re-derive on mid/quote data. |
| R2 | Bar-close fantasy fill | Re-run with fills moved from signal bar close to next bar open (next tick event for tick studies) with latency grid {250ms, 500ms, 1s}. Report P&L decay curve. | >40% gross-edge decay from t=0 to t=500ms ⇒ signal is latency-fragile; not retail-executable; reject for market-order track. |
| R3 | Touched-limit fills | Static scan of strategy code/spec: any limit order whose fill is granted without price trading ≥1 tick through the limit. | Any occurrence ⇒ automatic reject (mandate §24). No exceptions until MBO data exists. |
| R4 | Same-bar stop/target ambiguity | Count trades where bracket target and stop both lie within the execution bar's high-low range. Re-run under worst-case ordering (stop first). Report both bounds. | Ambiguous trades >5% of total, or worst-case bound flips net sign ⇒ move to tick-resolution execution or widen bar granularity; never report the optimistic bound alone. |
| R5 | Lookahead in bar construction | Truncation replay: recompute the full signal stream using only data ≤ t for each t on a 1% sample of events; diff against vectorized signals. Renko/synthetic bars: verify brick timestamps are completion-stamped and signals lag ≥1 brick. | Any signal value difference ⇒ lookahead; fix before any result is read. |
| R6 | Back-adjustment level corruption | For any level-based signal: recompute on unadjusted single-contract prices. Placebo: re-run on adjusted series with levels shifted by +37 points (arbitrary non-round offset). | Effect present on adjusted but absent on true prices ⇒ artifact. Effect equal at placebo levels ⇒ artifact. Level signals on adjusted series are banned regardless of outcome. |
| R7 | Roll-gap phantom bars | Flag all bars within 1 session of each roll date in the merge; recompute headline stats excluding them. | Headline edge drops >20% ⇒ roll artifact; investigate splice timing before proceeding. |
| R8 | Session-boundary liquidity fantasy | P&L attribution by 30-min bucket across the session. Flag trades entered/exited in 16:45–17:00, 17:59–18:05, 09:28–09:35 ET. Re-run with those trades at +2 ticks extra cost/side. | >30% of net P&L from boundary buckets AND sign flips under the stress ⇒ session-restrict the strategy or reject. |
| R9 | Volume leakage | Static scan: any use of forming-bar volume/high/low/close before completion; any day-normalized volume feature. Truncation replay (as R5) on volume features. Exclude roll weeks and re-test volume-filtered variants. | Any forming-bar usage ⇒ fix. Roll-week exclusion changes edge >20% ⇒ volume filter is roll-corrupted. |
| R10 | ETH cost fantasy | Split all results RTH (09:30–16:00 ET) vs ETH. Re-cost ETH trades at spread 4 ticks + slip (≈ C2+2). | Strategy only survives via ETH trades under RTH costs ⇒ session-restrict to RTH or re-prove at ETH stress costs. |
| R11 | Cost-sensitivity cliff | Sweep per-RT cost 0→6 ticks in 0.5-tick steps; find breakeven cost b*. | b* < 2.872 ticks (C1) ⇒ dead on arrival. 2.872 ≤ b* < 4.872 ⇒ C1-pass only; flag fragile. Report b* on every candidate card. |
| R12 | Multiple-testing inflation | From registry counts (all sequence-numbered configs in the family), compute DSR and PBO (CSCV) at promotion time. | DSR p > 0.05 or PBO > 0.5 ⇒ not promotable regardless of headline stats. |
| R13 | News-window slippage | Tag entries within ±2 min of scheduled releases (CPI, FOMC, NFP, 10:00 ET data). Re-run excluding tagged trades; re-cost tagged trades at C2. | Edge concentrated in tagged windows and dies at C2 ⇒ the "edge" is unexecutable volatility capture; reject for market-order track. |
| R14 | Trade-list / engine reconciliation | Reconcile TradesCount and NetProfit from engine totals vs serialized trade list (known NT8 boundary quirk); hash raw payloads per runlib. | Any unreconciled trade ⇒ resolve before results are read (existing campaign discipline; applies unchanged to scalp lab). |
| R15 | Last-print price staleness | For tick studies: measure time gap between signal event timestamp and the next trade print used as fill. Distribution of gaps by session bucket. | Median gap > 1s in the strategy's active window ⇒ fills are stale; move fill to next print AND add gap-scaled slippage, or restrict to active hours. |

---

## 3. Recommended EXECUTION MODEL for event studies (L1-only), and what L2 buys

### 3.1 The rule (L1 = last-trade tick events, our confirmed data level)

**Signal at time t → fill assumption:**

1. **Decision timestamp discipline.** A signal computed from data up to and including event
   i (timestamp tᵢ) may not act before tᵢ + L, L drawn from the latency grid; the
   **primary reported case is L = 250 ms**, with {next-event, 500 ms, 1 s} always reported
   alongside (decay curve, per R2). L = 0 may be computed only as a diagnostic bound.
2. **Fill price (market orders only).** Fill = **first trade print at or after tᵢ + L**,
   adjusted against the trade direction by the spread/slip allowance:
   `fill = P_next + dir × slip_ticks × 0.25`, where the *price component of C1 already
   equals slip_ticks = 1 per execution* (≈ half-spread 0.5 + latency drift 0.5). Do not
   also shift the print — C1's 1 tick/execution IS the shift; state this in every spec to
   avoid double counting (EXECUTION_MODEL.md convention).
3. **Cost states.** RTH (09:30–16:00 ET): C1 primary, C2 stress. ETH: C2 primary,
   C2 + 2 ticks stress — or exclude ETH trades entirely (preferred for Tier-0 screens).
   Trades within ±2 min of scheduled releases: C2 mandatory (R13).
4. **Exits symmetric.** Every exit is also a market order under rules 1–3. Brackets are
   evaluated on the tick stream (no OHLC bracket logic at scalp scale, per R4); a
   stop/target "triggers" when a *trade prints* at or through the level, and then fills as
   a market order per rules 1–2 (stops get the through-print price, not the level, when
   the gap-through print is worse).
5. **No passive fills. No exceptions.** Limit orders may be *studied* only as event markers
   (what happened after price touched X), never as executed trades, until queue-quality
   data exists (mandate §24). If a strategy concept requires earning the spread, it is
   parked in the passive-track backlog, not approximated.
6. **Event-study gross-edge convention.** The measured object is
   `E[dir × (M(t+h) − fill)] − cost`, where M(t+h) is the *next trade print* at horizon
   t+h (accepting print noise symmetrically), fill is per rule 2, and cost is the C-state.
   Report the edge in ticks at h ∈ {1s, 5s, 30s, 1m, 5m} so the horizon at which edge
   exceeds C1 is explicit. An edge that never clears 2.872 ticks gross at any h is dead
   (R11).
7. **Level-based signals** are computed on unadjusted single-contract prices only (R6).

Rationale: with Last-trade data only, the honest fill proxy is the next print plus a
priced-in half-spread+drift allowance; anything anchored to the signal-bar close or to a
touched price imports illusions 1–3 of §1.6. This model is deliberately *median-realistic*
(not worst-case) at C1, with C2 carrying the stress role — matching the frozen screen
design.

### 3.2 What L2 (BBO) data would buy — and what it would not

If DATAPROBE01 confirms downloadable historical Bid/Ask series (or bid/ask-stamped Last
ticks via Tick Replay):

- **Observed spread state at decision time** — replaces the flat 1-tick RTH assumption with
  the actual spread; fills become `opposing quote ± residual slip (0–0.5 tick)`; C1's price
  component splits into measured half-spread + small residual. Immediately kills/validates
  H-EXEC-1/2 below and makes ETH tradability an empirical question instead of an exclusion.
- **Quote-mid reference** — event-study edges measured against mid instead of next print,
  removing ~½ tick of bounce noise from every measurement (§1.6.1) and roughly halving the
  sample size needed to resolve a 0.5-tick edge.
- **Trade signing** (Lee-Ready against the quote) — order-flow features become available as
  *signals*, and adverse-selection measurement (post-fill mid drift) becomes possible.
- What BBO does **not** buy: queue position. Fill simulation for passive orders needs
  top-of-book *sizes* (L3) at minimum — probabilistic queue advancement models
  (hftbacktest power/log models) — and honestly needs MBO. The passive track stays closed
  under L2-only. No depth data = no book-shape families (S6–S8 remain BLOCKED_BY_DATA).

---

## 4. Testable hypotheses — NQ spread/liquidity state

### H-EXEC-1: NQ top-of-book is reliably 1 tick wide only in a definable RTH-ex-events state

Claim: P(spread = 1 tick) > 95% during 09:35–15:55 ET outside ±2 min of scheduled macro
releases; P(spread = 1 tick) < 60% in ETH (with a 2–6 tick mode), with transitions
concentrated at 09:30, 16:00, 17:00/18:00 ET and release timestamps.

- ECONOMIC MECHANISM: market-maker inventory and adverse-selection risk set the spread; in
  deep two-sided RTH flow, competition compresses to the tick floor; overnight, fewer
  liquidity providers and higher information asymmetry per trade widen quotes.
- OBSERVABLE VARIABLES: BBO spread per event (needs L2 probe success); proxy at L1: gap
  between consecutive opposing-direction trade prints (bounce amplitude) per 5-min bucket.
- EXPECTED HORIZON: state persistence minutes–hours (session-driven), not a trading signal
  per se — an execution-cost state model.
- EXPECTED SIGN: 1-tick fraction RTH ≫ ETH; spread widens with realized vol and around
  releases.
- REQUIRED DATA: historical Bid/Ask tick (DATAPROBE01 path b) over ≥ 60 sessions; fallback
  L1 bounce-amplitude proxy on existing NQ Last tick (2025-08 → 2026-07).
- RETAIL EXECUTABILITY: n/a directly — this calibrates the cost model all other candidates
  are screened under.
- SIMPLE NULL: spread state is constant (1 tick always) across sessions and vol states.
- FALSIFICATION EXPERIMENT: tabulate P(spread=1 tick | 5-min bucket × realized-vol tercile
  × release flag) over ≥60 sessions; hypothesis falsified if RTH-ex-events fraction < 90%
  or if ETH fraction is statistically indistinguishable from RTH.
- PRIORITY: 1 (gates the entire cost model; cheap once L2 probe lands).

### H-EXEC-2: Effective 1-lot market-order cost is ≤ 0.75 ticks/side RTH and ≥ 1.5 ticks/side in ETH/news states

Claim: realized cost vs decision-time reference (mid if L2; last print if L1) for a 1-lot
marketable order at 250–500 ms latency averages 0.5–0.75 ticks RTH, and ≥ 2× that in ETH
and within ±2 min of releases — i.e., C1's price component is median-correct for RTH and
optimistic elsewhere.

- ECONOMIC MECHANISM: cost = half-spread + latency drift; drift scales with local
  volatility per unit time × latency; spread state (H-EXEC-1) sets the floor.
- OBSERVABLE VARIABLES: simulated marketable fills on the tick stream: reference price at
  t, first print ≥ t+L; distribution of (fill − reference) × dir by session bucket, vol
  tercile, release flag.
- EXPECTED HORIZON: instantaneous (execution cost, not alpha).
- EXPECTED SIGN: cost strictly positive; increasing in latency, vol, and ETH state.
- REQUIRED DATA: existing NQ Last tick (sufficient for the drift component); L2 upgrades
  reference to mid and adds the true half-spread term.
- RETAIL EXECUTABILITY: directly defines it; also yields the empirical latency-decay curve
  mandated by R2.
- SIMPLE NULL: (fill − reference) has zero mean beyond the mechanical half-spread and does
  not vary by session/vol state.
- FALSIFICATION EXPERIMENT: run the R2/R15 machinery over the full tick year (~10⁶
  simulated executions on a 1-min grid + at random event times); falsified if RTH cost
  > 1 tick/side (C1 too optimistic — escalate C1) or if state dependence is absent
  (uniform cost is fine — simplifies model).
- PRIORITY: 1 (directly validates/updates the frozen C1 constant with our own data).

### H-EXEC-3: Touch-fill inflation — a touched-limit backtest on NQ overstates passive P&L by ≥ 1 tick per fill

Claim: replaying any simple passive strategy (join best bid/ask proxy = limit at last print
± 1 tick) under (a) fill-on-touch vs (b) fill-only-on-trade-through-by-1-tick produces a
per-fill P&L gap ≥ 1 tick, and (b) itself still overstates reality (queue position
unmodeled); consistent with the measured 65.8% NQ adverse-fill rate (arXiv:2409.12721).

- ECONOMIC MECHANISM: FIFO queue — price cannot trade through a resting limit without
  filling it, so guaranteed fills are adverse; touch-without-through fills occur with
  probability ≈ 0.2 and are the only benign ones.
- OBSERVABLE VARIABLES: touch events, through events, post-event drift at 1s–1m on the
  Last-tick stream.
- EXPECTED HORIZON: fill-level (seconds); aggregate over ≥ 10⁵ touch events.
- EXPECTED SIGN: (a) − (b) ≥ +1 tick per fill; post-touch drift conditional on
  trade-through is negative for the passive side.
- REQUIRED DATA: existing NQ Last tick; L2 would sharpen touch identification.
- RETAIL EXECUTABILITY: establishes the *size of the lie* we avoid by banning passive
  fills; not a tradable edge.
- SIMPLE NULL: touch-fill and through-fill replays produce statistically equal P&L.
- FALSIFICATION EXPERIMENT: the two replays on 60 sessions; if the gap < 0.5 tick/fill,
  the mandate §24 ban is over-cautious and a through-fill passive model could be
  considered; if ≥ 1 tick, ban is confirmed quantitatively and documented.
- PRIORITY: 2 (confirms a standing rule with our own numbers; informs the future passive
  track's data requirements).

### H-EXEC-4: Round-number level effects exist only in true contract prices; the back-adjusted series cannot detect them

Claim: conditional behavior (touch frequency, stall/bounce probability, post-touch drift)
at NQ 100/50/25-point levels is measurable on unadjusted single-contract prices and is
*absent by construction* at the same nominal levels of the back-adjusted series (which sit
~1,200–1,900 points from true levels over our window); placebo levels on the adjusted
series show effects indistinguishable from its "round" levels.

- ECONOMIC MECHANISM: clustering of resting stop/take-profit orders and human limit orders
  at round numbers (Osler; Donaldson & Kim) creates locally distinct liquidity — a real
  price-level phenomenon tied to *displayed* prices, which back-adjustment destroys.
- OBSERVABLE VARIABLES: distance of price to nearest true round level; touch/stall/burst
  statistics at levels, on single-contract tick data.
- EXPECTED HORIZON: seconds–minutes around level interactions.
- EXPECTED SIGN: on true prices: excess stall probability at levels and elevated burst
  probability after clean breaks; on adjusted prices at nominal levels: zero effect vs
  placebo.
- REQUIRED DATA: existing single-contract NQ Last tick (already unadjusted per contract);
  contract roll calendar to exclude roll-week contamination (R7).
- RETAIL EXECUTABILITY: any resulting signal is minutes-horizon and market-order
  compatible if edge > C1; the artifact half of the test protects every future level
  study.
- SIMPLE NULL: touch/stall/drift statistics at round levels equal those at uniformly
  random placebo levels (same distance distribution), on both series.
- FALSIFICATION EXPERIMENT: paired level-vs-placebo comparison on true prices (≥ 10⁴ level
  interactions) and on adjusted prices; hypothesis falsified if true-price effects are
  null; the methodological claim is falsified if adjusted-series "effects" survive the
  placebo (would imply grid artifacts, not levels).
- PRIORITY: 2 (one experiment simultaneously tests a candidate signal family and installs
  the R6 guardrail with campaign-specific evidence).

---

## Appendix — source index (primary load-bearing citations)

- Market Simulation under Adverse Selection — arXiv:2409.12721 (NQ 65.8% adverse fills; ρ≈0.2)
- Moallemi & Yuan, Queue Position Valuation — moallemi.com/ciamac/papers/queue-value-2016.pdf
- The Negative Drift of a Limit Order Fill — arXiv:2407.16527
- The Market Maker's Dilemma — arXiv:2502.18625 (front vs back-of-queue post-fill returns)
- Stoikov & Waeber, Reducing Transaction Costs with Low-Latency Trading Algorithms — SSRN 2661618
- Roll spread estimator lecture notes — ba-odegaard.no (Roll 1984 mechanics)
- When Backtests Guess — SSRN 6240638 (NQ same-bar ambiguity: 18.47%, $73,900/1,000 trades)
- Bailey & López de Prado, Deflated Sharpe Ratio — SSRN 2460551; Harvey & Liu, Backtesting — SSRN 2345489
- CME matching algorithms — cmegroupclientsite.atlassian.net; databento.com/blog/cme-matching-algorithms-explained
- Rithmic/CQG latency — blog.pickmytrade.io (2025); NinjaTrader forum thread 1119171; damnpropfirms.com
- Continuous-contract methodology — quantpedia.com; quantstart.com
- Practitioner cost/spread arithmetic — chartmini.com; fortraders.com; quantvps.com; tradefundrr.com
