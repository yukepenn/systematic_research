# PARKED, NOT DEAD — the recombination registry

Owner standing instruction (2026-08-25): *"strategy或者signal以后都可以变着法子combine，而不是
现在就一定不用然后放弃什么的。因为你现在做的系统也不一定是最佳的。说不定你哪个阶段又全部打散
然后从第一性原理重来。"*

Nothing below is deleted or forbidden. Each row records **why it stopped**, and **what would
revive it**. A future teardown-and-rebuild should start here rather than re-deriving.

| item | wave | why it stopped | what would revive it |
|---|---|---|---|
| Short-side vote | W23 | Sharpe 0.067 standalone; costs 0.011 Sharpe in the pair | a short engine designed for vol-expansion/breakdown instead of mirrored trend following (W24) |
| B-MOM (RTH breakout) | W01/W11 | decayed: negative on the 2026 holdout | a fresh decay re-read; it earned for years before decaying |
| Bolt-on skew exits (trail/target) | W01 F2 | destroy per-trade expectancy on our entries | an entry family whose winners are structurally longer-lived |
| Per-trade dollar caps | W02 | inert — our tail is intra-week accumulation | a higher-per-trade-risk engine where a cap has something to cut |
| Weekly loss limit | W01 | locks in losses, kills hit rate | a regime-conditional version, or a much larger limit |
| Multi-Osc overlap reversal | W03 | dead standalone (−0.159) | use as a GATE rather than an engine; or the licensed vendor series |
| CumDelta transition engine | W03 | marginal (0.137) | its information is better used as the delta gate; revisit with true tick delta |
| Pullback-into-trend family | W08 | capture 1.82 % vs 4.7 % | a different trend definition, or intrabar (tick) resumption detection |
| Cross-asset agreement (ES/RTY/YM) | W07 | zero effect (indices ~0.9 correlated) | a genuinely uncorrelated asset (rates, FX, VIX term structure) |
| Overnight / opening-range gates | W07 | RIGHT rate unchanged or worse | combined with a different base engine |
| Efficiency chop classifier | W07 | anti-selective (removed good over bad 2:1) | replaced by the realized-range ratio, which works — the idea was right, the estimator wrong |
| Low-range fade (VWAP / rails / Bollinger) | W11, W18 | negative in three independent tests | a genuinely mean-reverting instrument or a much finer clock |
| Multi-instrument (ES/RTY/YM engines) | W11 | the engine loses on all three | per-instrument re-derivation instead of transplanting NQ parameters |
| Per-member independent sleeves | W12 | worse than the averaged ensemble at equal exposure | different risk rules per member, not just split positions |
| `signal_wave` / strong-trend gates | W12/W13 | failed circular-shift null (73rd, 78th pctile) | more data, or as part of a vote rather than a solo gate |
| Segment sleeves (EUROPE/PREOPEN/RTH) | W16 | only ASIA is anti-correlated with the US session | a different segmentation (event-based rather than clock-based) |
| Conviction / range-proportional sizing | W06/W10/W22 | leverage three times over — money and tail scale together | never; this one is a law, not a parking |
| Deep-history calibration (2006-2021) | W17 | fixed stack ~zero there | owner scoped the campaign to the modern regime |
| Quarterly parameter selection | W19 | 88 % churn, +0.021 over naive | replaced by the vote; revive only with a stable selector |
| Tick-data acquisition | W15 | true delta missed the 25 % bar; his BidAsk mode is worst for us | a tick-native engine (not a 1-min engine fed better delta) |
