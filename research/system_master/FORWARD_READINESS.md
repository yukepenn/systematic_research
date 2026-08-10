# FORWARD_READINESS — uncertainty-aware current-regime panel for both baselines

**Frozen 2026-08-10.** Master Directive v4 sec8/sec32. No single "future Sharpe" point estimate is
presented as fact anywhere below — every forward-looking statistic carries an interval or an
explicit statement of why one couldn't be built.

## Product A (`SolarWaveSMMaster_v4`)

Full panel: `runs/U6B_PRODUCT_A_SCALE_RATE/forward_readiness/REPORT.md` (CONTROL rows — byte-
identical to unmodified Product A). Headline facts, genuine-MNQ pricing:

- **Full history** (2022-01-03..2026-05-29, n=1,139): Sharpe 1.1819, **95% CI [0.320, 2.036]** —
  a very wide interval; a future multi-year Sharpe reading anywhere in that band would be
  unremarkable.
- **Rolling-window distributions** (full available series incl. health-only extension): 20-session
  Sharpe has historically ranged **−5.92 to +7.94**; even the 252-session ("roughly annual")
  window has ranged **0.36 to 2.17**. A future 60-session stretch losing $15-16k would not be
  unprecedented — it has already happened (2026-03-10..2026-06-01, the single worst 60-session net
  stretch on record, straddling the most recent data).
- **2026 current-regime evidence**: Jan-May 2026 (canonical, complete) Sharpe 0.611, **95% CI
  [−2.554, 3.560]** — the widest, least precise slice of the whole panel; weighted per sec32 as the
  most recent complete evidence, it shows a genuinely weak stretch, not a strong one. The
  subsequent Jun-Jul health-only extension recovers (Sharpe 3.42) but carries no promotion/
  inference weight by this campaign's own standing convention, and its own CI [−1.128, 7.602] is
  far too wide to treat as a current-regime confirmation either way.
- **Quarter-by-quarter**: 2 of 18 canonical quarters were net-negative (2023Q1, 2024Q1); the single
  worst quarter in the whole history is the most recent complete one, 2026Q2 (−$14,567.30,
  Sharpe −2.579, partial: 43 of a normal ~64 sessions).
- **Tail concentration**: top-20 all-time blocks account for the large majority of net profit (a
  structural feature of this trend-following design, not new information this wave).

**Reading**: Product A's own forward-readiness evidence is not alarming (no mechanism-failure
signal, no structural break), but it is also not currently strong — the most recent complete
regime (2026 Jan-May) was weak, consistent with wide normal variation rather than degradation.

## Product B (`SolarWaveOneContractNQ_v5`/`_MNQ_v5`)

Full panel: `research/system_master/CURRENT_EDGE_HEALTH.md` (pre-existing, not rebuilt this wave —
reused per this campaign's own "don't duplicate existing work" discipline). Headline facts:

- **Overall assessment: HEALTHY**, 1 WATCH flag (rolling-120 Sharpe, 23rd percentile — mechanically
  explained by the Jan-May 2026 weak stretch still being inside that trailing window, not a new
  independent concern).
- Rolling-60 Sharpe: 1.308, 50.4th percentile (**HEALTHY**, squarely at the historical median).
- Current drawdown: $5,625, 34.0th percentile (**HEALTHY**, shallow).
- Giant-winner arrival rate (2026 annualized): 44.70/250 sessions, the **highest of the 5 tracked
  years** (**HEALTHY**).
- Short-side rolling (most recent 2 months): +$1,003/trade, a **recovery** from an earlier
  −$557/trade stub reading (**RECOVERING/HEALTHY**).
- Rolling-60-session window positivity: 77.4% historically (**HEALTHY** base rate for any given
  60-session stretch to be net-positive).

**Reading**: Product B shows the same qualitative 2026 pattern as Product A (a real Jan-May 2026
weak stretch, now recovering) but reads healthier overall on its own dedicated health panel — no
uncertainty-interval rebuild was performed for Product B this wave (out of scope; the existing
panel already provides percentile-based, historically-grounded context rather than a bare point
estimate, which satisfies this document's own "no bare point estimate" standard).

## What this document does not do

It does not predict future performance for either object, and it does not resolve whether the
2026 Jan-May weak stretch is early-stage degradation or ordinary variation — both baselines'
existing evidence is consistent with normal variation given how wide the historical rolling-window
distributions already are (see `FAILURE_CRITERIA.md` for the percentile-based thresholds that
would distinguish the two going forward).
