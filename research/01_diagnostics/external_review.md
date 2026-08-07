# External Review: Campaign Methodology & Forward-Profit Assessment

## 1. Verdict summary

**Are you doing the right things?** Mostly yes, procedurally — the preregistration-before-results discipline, append-only registries, quarantine convention, no-rescue rules, and zero-DoF null experiments (SW01b/SW01c) are genuinely above the norm of published quant research (protocol audit grade: B−). But process cannot manufacture significance the sample does not contain, and three substantive findings dominate everything else:

1. **The baseline is not statistically significant even at N=1 trials.** Sharpe 1.39 with SE ~0.97 is t ≈ 1.43, one-sided p ≈ 0.076, PSR(0) ≈ 92% < 95%. Every promotion gate in the current protocol is economic; none is statistical. After any honest deflation for the vendor's unknown prior optimization of 90/179, the Deflated Sharpe is approximately zero.
2. **The entire net edge (+$189.6k, PF 10.8, 279 trades) is realized by a fill mechanism that does not exist live.** NinjaTrader's Strategy Analyzer fills exit-on-session-close at the last bar's close print; live, the same strategy sends a market order at 16:59:30 into the thinnest tradable half-hour of the day, time-synchronized with Apex's 4:59 PM forced flattening and every other default-EOSC NinjaTrader strategy. The penny-exact UI parity cannot detect this because both sides share the same fill model.
3. **The published literature supports exactly one intraday effect that looks like this strategy — end-of-day momentum (Gao 2018; Baltussen 2021) — and its flagship version demonstrably disappeared out-of-sample after publication (Rosa 2022).** Minute-scale index-futures horizons are a documented mean-reversion/microstructure-noise regime, and the only same-instrument systematic study (MNQ, 2021–2025) found gross OHLCV edges of 0.07–1.50 points/trade against a ~2-point friction floor, with 0 of 14 signal families surviving. There is no credible published case of sustained after-cost 1-minute trend-following profitability in NQ/ES for small traders.

**Honest probability that the current baseline nets positive over the next 12 months at 1-tick costs: 35–55%, point estimate ~45%.** The naive frequentist read from Sharpe 1.39 (~90%) is inadmissible: t ≈ 1.4 with unbudgetable vendor multiplicity, base-rate haircuts from every relevant population (26% for vetted academic anomalies, median 73% for bank-engineered strategies, R² < 0.025 IS→OOS predictivity in the closest retail-algo cohort) push forward Sharpe into the 0.3–0.7 band, where one year is close to a coin flip. **Probability the strategy possesses genuine transferable entry alpha (as opposed to conditional long-drift capture plus a decayed end-of-day flow effect plus luck): roughly 10–20%.** The modal scenario is "positive if NQ drifts up, negative if it doesn't."

**Bottom line: expected forward edge should be treated as near zero until (a) SW01b shows Type-1 entries beat session-close-matched random entries, (b) the 2022 bear and 2025-03→2026-07 windows survive as clean OOS, and (c) the 16:59:30 exit prices are shown achievable via timed-exit variants and measured MNQ shadow fills.** Those three are decidable pre-capital. No deployment before all three.

## 2. What the evidence supports keeping

- **Preregistration with mechanism, committed to git before results** (grade A−) — add external timestamping (below), but the practice itself is best-in-class.
- **The six no-rescue-tuning rules.** The literature on strategy decay (Suhonen 73% median deterioration; Wiecki R² < 0.025) is precisely the population that rescue-tuning creates. Do not soften them.
- **SW01b/SW01c as zero-DoF nulls.** The drift-matched random-entry control is exactly the right competitor model — the base-rates brief independently arrived at the same design.
- **Day-block + episode bootstraps** — correct dependence structure for episode-clustered losses (grade B+). Preregister block length and stationary-bootstrap p; add a day-of-week-stratified variant for the Thursday 41% concentration.
- **Determinism and parity verification** — sufficient for pipeline integrity. Understand its limit: it reproduces the same simulation bias identically; it says nothing about fill realism.
- **The slip-1 honest-cost basis and the locked-forward concept** — but reframed per §6.

## 3. What the evidence says to change or add (prioritized)

1. **Fix the session-close fill mechanic before anything else.** Preregister a variant exiting via explicit timed market order at 16:58/16:59 (same mechanism backtest and live, same price bar), and measure the edge-decay curve when the exit moves to 16:55, 16:45, 16:30. If the +$189.6k concentration collapses at 16:55, the edge is a last-print marking artifact, not capturable price. This single test can falsify the whole campaign for ~zero cost.
2. **Archive the full daily P&L vector per config from the next Tier-1 sweep onward.** Summary-payload archiving permanently destroys the T×N matrix CSCV/PBO requires (Bailey et al.). Everything already swept is unrecoverable for PBO; stop the bleeding now.
3. **Run the 2022 bear and 2018–2022 extension, plus a one-shot preregistered read of 2025-03→2026-07.** The latter is the *only* data plausibly postdating the vendor's optimization — the only clean OOS with respect to the vendor's hidden trials. A long-PF-1.20/short-PF-1.07 machine must show what it does when NQ falls 33%.
4. **Replace the WFO centerpiece.** 18/6 yields exactly one test fold (void); 12/3 yields ~4 folds (too few for CSCV). Use CPCV on ~12 monthly blocks (~66 splits), with the hysteresis state machine's warm-up preregistered per fold — the real fold-boundary leak is indicator state, not trade spans (trades never cross sessions).
5. **Add the beta-carry decomposition and exposure-hour audit** (see §4) as freeze-gating analyses.
6. **Add a statistical gate:** PSR computed with empirical skew/kurtosis of daily MTM, plus a bracketed Harvey-Liu haircut at N ∈ {10, 100, 1000} reported with every promotion — display the vendor-DoF uncertainty rather than hide it behind "configs consumed: 1."
7. **State-dependent slippage overlay in the registry:** ~1 tick RTH, ~2 ticks for 16:30–17:00 exits and ETH executions, 5–10 ticks within ±2 minutes of CPI/FOMC/NFP (at 5.5 trades/day, event-window hits are guaranteed). Rerun DSR/PBO on the overlay. Separately: targeted stress applying 2–4 ticks only to the 279 session-close fills.
8. **Freeze integrity:** checksum and archive the raw bar series before the September roll (back-adjustment mutates the entire historical path at every roll, making archived ledger hashes irreproducible); push signed freeze/prereg tags to a remote or OpenTimestamps before results exist (local git history is rewritable).
9. **Define the SPA benchmark family in writing before SW02 results are read:** drift-matched random-entry control, intraday-long-only, hold-into-close (enter on rest-of-day direction, no trailing logic), frozen Type-1.
10. **2–3 months of MNQ live-sim shadow** specifically to measure the realized slippage distribution at 16:59:30 and on entries; feed the empirical distribution into the locked-forward evaluation. Realized slippage > ~1.5 ticks/execution mechanically eliminates the $40.83 average trade regardless of signal quality.

## 4. The drift question

**Pure repackaged drift does not arithmetically explain the headline number, but drift-timing plausibly explains a large minority, and one unverified channel could explain far more.**

The arithmetic (QQQ unadjusted OHLC, Dec-2022→Feb-2025, 541 sessions, dollarized to 1 NQ contract): 24h buy-and-hold ≈ +$198.8k; overnight-only ≈ +$149.6k (75%); **always-long RTH-intraday-only ≈ +$49.2k (25%)** — one-third of the $146.4k slip-0 net, and that requires 100% long exposure every RTH minute. A two-sided state machine with trailing stops has net-long time exposure plausibly 10–40%, capping *unconditional* drift capture at roughly **$5–20k, ≤15% of net**. Moreover, ~45% of net (2024Q3 + 2024Aug + 2025Jan) was earned in quarters where intraday drift was *negative* (−$27.7k, −$15.9k) — pure long-drift cannot produce that.

Two drift-shaped risks survive:

- **Conditional drift-timing:** long trend-start entries held to the close in a +91% tape capture far more than TWAP drift. This fits the long/short PF gap (1.20 vs 1.07), the session-close bucket (~$680/trade ≈ 19 bps of notional), and 2023's anomalous intraday-dominant year (intraday +38.9%), which means "flat overnight" did not immunize the 2023 P&L. It also fits the literature exactly: the session-close bucket looks like a decayed, regime-dependent, two-sided Baltussen-style gamma-flow effect (which *reverts* next day — consistent with the Thursday/2024Q3 concentration) stacked on bull drift.
- **Premise flaw — "flat at 17:00 ET" is the Globex session close, not an intraday-only guarantee.** Unless the session template is RTH-only, the strategy can legally hold through 16:00→9:30, the window carrying 75% (~$150k/contract) of drift, concentrated 2–3 AM ET. Until contract-hours of exposure are audited by clock hour from timestamps, drift confounding of **one-third to one-half of net cannot be excluded.**

**Implications for SW01b:** the design is correct and necessary but must be strengthened. (a) Random entries must use the *identical* session-close exit machinery, day-block bootstrapped — if Type-1 entries don't beat them, the alpha claim dies even with positive P&L. (b) Add the beta-carry regression as a co-gate: daily MTM P&L on same-day close-to-close, overnight, and RTH NQ components; report beta, beta×mean (drift carry in $), alpha, alpha t-stat, per year and pooled; gate the freeze on alpha surviving carry removal. (c) Add hold-into-close and intraday-long-only benchmarks to the SPA family — if Solar Wave RK doesn't beat "enter on rest-of-day direction, hold to close" after costs, the 1-minute machinery is costume. (d) Run the detrended synthetic (subtract per-bar mean drift, re-run) and long-only/short-only splits. Only the locked-forward period or a bear/flat regime can fully separate drift-timing from genuine trend capture.

## 5. Execution realism verdict

**1 tick/execution is a defensible central estimate for RTH 1-lot market orders — measured retail fills average 0.7–1.2 ticks in peak hours — but it is not conservative for *this* strategy, and the tick count is not even the main risk.**

- Entries occur across the full ETH session, where spreads run 2–5× RTH (measured NQ trade-time spreads: ~2.3–2.7 ticks in liquid cash hours, 5.5 at the 18:00 reopen); NQ's book is structurally thin (a handful of contracts per level vs hundreds on ES).
- The profit concentrates in the post-settlement 16:30–17:00 window — the thinnest tradable half-hour of the listed day, 45+ minutes after the NQ settlement VWAP window (16:14:30–16:15:00 ET), and the exit second (16:59:30) is crowded with correlated flatting flow.
- **The dominant issue is the fill-mechanism mismatch** (§1, item 2): last-print fill at 17:00:00 in backtest vs a spread-crossing market order at 16:59:30 live. This is untested by any current protocol item and undetectable by parity checks.
- Mechanical arithmetic: each extra tick/execution ≈ $29k over the sample; break-even at ~5 ticks/execution. So slippage alone does not kill the strategy — even pessimistic close-window slippage (2–4 extra ticks on 279 trades ≈ $3–6k) leaves the concentration intact. But **statistical significance dies far before mechanical break-even**: PF is already 1.081 at 2 ticks.
- The sample contains no stress regime; April 2025 saw ~90% depth decline in index futures. Bear-regime slippage will be materially worse than anything in 2023–2025.

**Use instead:** treat the **2-tick line (net $91.9k, PF 1.081) as the realistic planning case** and 1-tick as optimistic; adopt the state-dependent overlay (§3.7); gate the freeze on the timed-exit decay curve and measured MNQ shadow fills; log live-vs-backtest fill deltas as a first-class parity metric from day one.

## 6. Protocol gaps (top 5, actionable)

1. **No statistical gate anywhere in the promotion path.** t ≈ 1.43; PSR(0) ≈ 92%; DSR at any honest trial count ≈ 0; HLZ's t ≳ 3 bar needs ~9 years at this SR. Action: add PSR (empirical moments) + bracketed Harvey-Liu haircuts to every promotion report, and state in the freeze doc that the promotion case rests on mechanism evidence (SW01b, SW02, clean OOS), not significance.
2. **The trial-count denominator is fiction.** "Configs consumed: 1" ignores that 90/179/5/10/true/10 is the argmax of the vendor's unknown search, and Type-1-of-3, 1-min-of-many, session-close-exit, and NQ-of-many were chosen after vendor exposure. MinBTL on 2.1 years tolerates only a handful of independent trials; the vendor's hidden search alone plausibly exceeds it. Action: report DSR under bracketed N; treat 2025-03→2026-07 as the only vendor-clean OOS.
3. **WFO geometry infeasible and CSCV data being destroyed.** 18/6 = 1 fold; 12/3 ≈ 4 folds; Tier-1 sweeps archive summaries only. Action: CPCV on monthly blocks, full per-config daily P&L retention, per-fold indicator warm-up preregistered.
4. **Freeze integrity holes.** Back-adjusted series mutates at every quarterly roll (archived hashes become irreproducible after September); local git tags prove nothing un-pushed; roll schedule and session template are absent from the registry as data-contract DoF. Action: checksum bar data now, external timestamping ritual, register the data contract.
5. **The locked-forward is framed as confirmation, which it mathematically cannot deliver** (6–12 months at SR-SE ≈ 1.2–1.7 cannot confirm SR 1.4). Action: reframe it as a disconfirmation tripwire with preregistered max-DD/losing-streak stop bounds; any live allocation exists to be falsified, sized off forward Sharpe 0.3–0.7 and a DD assumption materially worse than −$22k (the in-sample DD is a lower bound — no bear regime).

## 7. Sources (deduplicated)

**Peer-reviewed, high credibility**

- Gao, Han, Li, Zhou (2018), "Market Intraday Momentum," *JFE* 129:394–414 — first half-hour predicts last half-hour; half-hour scale only, not minute-scale. [sciencedirect.com/science/article/abs/pii/S0304405X18301351]
- Rosa (2022), "Understanding Intraday Momentum Strategies," *J. Futures Markets* 42(12):2218–2234 — the key post-publication test: Gao et al.'s predictability disappears out-of-sample. [onlinelibrary.wiley.com/doi/abs/10.1002/fut.22375]
- Baltussen, Da, Lammers, Martens (2021), "Hedging Demand and Market Intraday Momentum," *JFE* — last-30-min continuation across 60+ futures, gamma-hedging mechanism, two-sided, mean-reverting next day. Strongest surviving intraday-momentum evidence. [ssrn.com/abstract=3760365]
- Lou, Polk, Skouras (2019), "A Tug of War," *JFE* — canonical overnight/intraday decomposition; index drift accrues overwhelmingly overnight. [sciencedirect.com/science/article/abs/pii/S0304405X19300650]
- McLean & Pontiff (2016), *J. Finance* — 26% OOS / 58% post-publication decay across 97 predictors; the most charitable haircut available. [ssrn.com/abstract=2156623]
- Harvey & Liu (2015), "Backtesting," *JPM* — nonlinear multiple-testing haircuts; t ≈ 3 norm. [ssrn.com/abstract=2345489]
- Bailey & López de Prado (2014), "The Deflated Sharpe Ratio," *JPM* — False Strategy Theorem; canonical DSR. [ssrn.com/abstract=2460551]
- Bailey, Borwein, López de Prado, Zhu (2017), "The Probability of Backtest Overfitting," *J. Comp. Finance* — CSCV design and its T×N data-retention requirement. [ssrn.com/abstract=2326253]; author preprint with split geometry at davidhbailey.com/dhbpapers/backtest-prob.pdf
- Bailey et al. (2014), "Pseudo-Mathematics and Financial Charlatanism," *Notices of the AMS* — MinBTL bound. [ams.org/notices/201405/rnoti-p458.pdf]
- Suhonen, Lennkh, Perez (2017), *JPM* — 215 bank-engineered strategies; median 73% backtest→live Sharpe deterioration, worse for complex strategies. [ssrn.com/abstract=2757113]
- Wiecki et al. (2016), *J. Investing* — 888 Quantopian algos; IS Sharpe R² < 0.025 for OOS. [ssrn.com/abstract=2745220]
- Chague, De-Losso, Giovannetti (2020), "Day Trading for a Living?" — regulator census, 19,646 traders; 97% of persistent futures day traders lose; no learning. [ssrn.com/abstract=3423101]
- Intraday time series momentum: global evidence, *J. Financial Markets* — confirms the effect internationally, half-hour scale only. [sciencedirect.com/science/article/abs/pii/S138641812100001X]

**Official/exchange/platform documentation, high credibility for mechanics**

- CME settlement documentation — NQ daily settlement VWAP 15:14:30–15:15:00 CT (Client Systems Wiki); equity-index settlement course; NQ-vs-ETF TCA (~10.4 bps institutional round trip). [cmegroup.com]
- NinjaTrader Support Forum (official staff answers) — ExitOnSessionCloseSeconds is real-time only; backtests fill at last bar close; 30-second default. [forum.ninjatrader.com threads 1101608, 1092998]
- NY Fed Liberty Street Economics — overnight drift decomposition, S&P futures 1998–2019, 2–3 AM concentration. [libertystreeteconomics.newyorkfed.org]

**Preprints and practitioner sources, medium credibility**

- Safari & Schmidhuber (2025), arXiv 2501.16772 — trending regime only from hours to years; minutes are reversion regime. Medium-high; not journal-verified.
- Falck, Rej, Thesmar, arXiv 2105.01380 — Sharpe roughly halves post-publication across 72 strategies. Medium-high (CFM).
- Mesfin (2026), arXiv 2605.04004 — MNQ 5-min OHLCV falsification study; 0/14 signal families survive; gross-edge ceiling 0.07–1.50 pts vs 2-pt friction. Medium: not peer-reviewed, self-reported positive controls, but transparent methodology and the only study on our exact instrument/platform family.
- Zarattini, Aziz, Barbon (2024), SSRN 4824172 — SPY intraday momentum claims. Low-medium: independent QuantConnect replication found Sharpe ~0.40 at 1× leverage.
- PickMyTrade slippage aggregation (~1,000 live fills: 0.7–1.5 ticks by broker, 5–20 at events); Astreka hourly spread data (2.3–5.5 ticks; methodology unverified — upper-bound evidence); Bookmap/edgeful/TradeAlgo NQ depth characterizations; Optimus event-liquidity education; prop-firm flattening rules (Apex 4:59 PM ET). Medium to medium-low: vendor/practitioner sources, mutually consistent.
- Global Trading — S&P futures depth −90% in April 2025 stress. Medium-high (trade press, headline figure only).
- CXO Advisory Collective2 review (~18% of tracked systems beat benchmark; dated); CME CTA survival study (~7–20% annual attrition). Moderate.
- Yahoo Finance QQQ daily OHLC — primary data for our own window-exact overnight/intraday decomposition (541 sessions); Cacciatore and Robot Wealth practitioner analyses corroborate; Slickcharts for annual-return corroboration only.