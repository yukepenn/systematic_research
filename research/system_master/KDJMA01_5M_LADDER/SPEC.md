# KDJMA01 — "5-min MA120 + KDJ + ladder rule" retail system (owner-directed, 2026-08-21)

**Status: FROZEN before any signal/P&L statistic. Run class: BOUNDED_SELECTION. Alpha budget
1/2, wave 2026-08-21. One shot.**

Owner direction: test the internet-claimed system ("5分钟图+120均线+KDJ+梯形法则,止损20点",
claimed 26×/31× monthly on a live account). Scientific scope: the claimed RETURNS are a
leverage/survivorship artifact by arithmetic (documented elite day-trader ceiling ≈ 8%/month
net, Taiwan top-0.1%; pyramiding scales expectancy, cannot create it). The testable object is
the BASE SIGNAL at 1 contract under honest costs. If base expectancy fails, no ladder/
pyramid can save it; if it passes, sizing is a separately preregistered question.

## 1. Construction (every ambiguity frozen here)

- Substrate: `nq1m_2005_202605.parquet`; 5-min bars resampled from 1m (OHLC, label = window
  end), full Globex session (18:00 ET → 17:00 ET, sess boundary at 18:00). PV $20, tick 0.25,
  commission $4.36/RT, 1t/side slippage.
- MA: SMA(120) of 5m closes (primary). MA(127) = disclosure arm only.
- KDJ, classic Chinese recursion, params (9,3,3): RSV_t = 100·(C−L9)/(H9−L9) over 9 5m bars;
  K_t = (2/3)K_{t−1} + (1/3)RSV_t; D_t = (2/3)D_{t−1} + (1/3)K_t (K,D init 50; H9=L9 ⇒ RSV
  carries forward). Golden cross: K crosses above D; death cross: K crosses below D.
- Entry (flat only; single contract; no pyramiding — see scope): on a 5m bar where
  close > MA120 AND golden cross → LONG at next 5m bar open +1t. close < MA120 AND death
  cross → SHORT at next 5m bar open −1t. No new entries within the last 30 min of a session.
- Exits (first hit wins), evaluated in 1-minute resolution between entry and session close:
  1. **Hard stop 20.00 pts** from entry fill; stop fill = level ∓1t, gap-through fills at
     the (worse) 1m bar open ∓1t.
  2. **Ladder rule** on 5m structure: swings = fractal-5 (a 5m bar whose low is strictly the
     lowest of the 2 bars either side = swing low; mirror for swing highs), confirmed 2 bars
     later. LONG exits when a confirmed swing low < the previous confirmed swing low
     (both formed after entry); SHORT mirror (swing high > previous swing high). Exit at the
     next 5m bar open after confirmation, ∓1t.
  3. Session close: exit at the last 5m bar's close before 17:00, ∓1t (house flat-at-close).
- Re-entry allowed immediately when flat and a fresh signal bar occurs.

## 2. Gates (primary arm MA120; ALL AND-required)

- **G1** N_trades ≥ 5,000 (a 5m cross system should fire multiples of this; if it fires
  fewer the construction reading of the rule is wrong — report, don't tune).
- **G2** net > 0 AND iid CI_lo > 0 AND year-block CI_lo > 0 (B=10,000, seed=20260821).
- **G3-SPLIT** standing per-event form.
- **G7** concentration: top-1% ≤ 50% |net|; single best/worst ≤ 25%.
- **G8** Solar losing-day ρ ≤ 0.25 AND net on Solar dev losing days > −$100k (LIQREV lesson).
- **G9** stress 2t/side + 3× commission: G2 holds.
- Disclosure: MA(127) arm battery; per-side; per-year; trades/day; win rate; avg
  win/loss; stop-hit vs ladder-exit vs close-exit shares; gross before costs (the "could any
  cost structure save it" number); RTH-entries-only slice (descriptive).

## 3. Decision rule (frozen)

ALL pass → red team → candidate path (and ONLY then would a pyramiding/sizing spec or a
Solar-combination question be preregistered). ANY fail → family CLOSED one-shot (MA length /
KDJ params / stop distance / swing-definition re-skins ineligible) and the OHLCV pause
resumes.

## 4. Honest prior

A 5m cross system trades several times a day; friction $14.36/trade demands a per-trade gross
edge that MOM01 (intraday momentum CLEAN_NULL), Zone-F's measured signal ladder (+1-2pp
conditional lifts vs 7-10pp needed), and B-MOM's regime-locality all argue is absent.
Trend-filter-plus-oscillator systems are the most back-tested retail class in existence;
published academic sweeps (Brock et al in-sample → out-of-sample failures) find nothing net
of costs on modern index futures. Prediction: significantly NEGATIVE net (churn), gross ≈ 0.
The value of the shot is the decisive, owner-cited number — and the demolition arithmetic of
the 26× claim it makes concrete.
