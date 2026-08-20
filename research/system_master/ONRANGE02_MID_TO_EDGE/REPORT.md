# ONRANGE02 — REPORT (readout 2026-08-20; spec frozen at 312b0f7 BEFORE any statistic)

**The owner's probability: 77.6% (short side) / 79.5% (long side) hit the nearer overnight
extreme. The owner's P&L: significantly NEGATIVE — −$27.0/trade, net −$138,347 over 5,122
trades, year-block CI [−47.2, −7.4] entirely below zero. FAIL; family CLOSED one-shot; the
OHLCV pause resumes.**

## Probability answers (frozen readouts)

- P(hit ONL | open below mid) = 0.776 (n=2,285); P(hit ONH | open above mid) = 0.795
  (n=2,837). P(hit before opposite break) = 0.705 / 0.725. Win rates 79.0% / 81.3%.
- Median time-to-target 09:38; median distance to target only 7.25 pts (median range 33.75).

## Why 80% win rate loses money (the shape, quantified)

- ~80% of days collect a ~7-pt scalp (~$145 gross, ~$131 net); ~20% of days the market runs
  the other way with no stop → hold-to-close losses up to ~$17.4k (single worst = 12.6% of
  |net|). Textbook negative skew.
- Depth quartiles (descriptive): the opens CLOSEST to the target hit most often (84.2%) and
  lose the most (−$69.8/trade) — proximity shrinks the win, not the loss.
- ARM_B (stop at opposite level): −$22.9/trade, 24.5% stopped — not rescued.
- Mirror arithmetic (exact, no new test): gross edge = −$12.65/trade, so the REVERSED rule
  grosses +$12.65 and nets ≈ −$1.7 after the $14.36 friction — both directions die on costs.
- Gates: G2 FAIL (year-block CI entirely negative), G3 FAIL (pre-2020 CI [−38.1, −8.7]
  entirely negative), G7 FAIL (top-1% share 1.05 on a near-zero |net| denominator —
  mechanical), G9 FAIL (stress −$45.7, both CIs negative). G8 letter-PASS with a notable
  disclosure: +$138k on Solar's dev losing days (ρ −0.17) — hedge-shaped but with
  significantly negative own expectancy: an overpriced insurance policy, not an engine.

## Closure

With ONRANGE01, the overnight-range axis is now mapped in all four quadrants on 20 years:
break probability TRUE (96.2%) / break continuation not tradable (+$29.8 insignificant,
tail-carried) / drift-to-nearer-edge significantly negative (−$27.0) / both mirrors dead on
costs. Family CLOSED (one shot; midpoint/target/exit re-skins ineligible). Wave 2026-08-20
alpha budget 2/2 spent. Artifacts: `out/onrange02_{results.json,trades.csv}`. No red team
(FAIL, nothing adopted).
