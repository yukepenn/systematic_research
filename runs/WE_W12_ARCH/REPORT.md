# WE_W12 — ARCHITECTURE & UNUSED SIGNALS · REPORT

## FA FIRED — averaging before the decision is the right architecture

Per-member sleeves (each ±1, own throttle, positions summed), exposure-normalised:

| variant | k | capture | big-day | wk mean | Sharpe | stress |
|---|---|---|---|---|---|---|
| BASE ensemble narrow6 | 1 | 5.01 % | 17.77 % | $1,484 | **0.214** | $1,305 |
| A1 members k3 | 3 | 3.33 % | 14.64 % | $980 | 0.192 | $809 |
| A1 members k5 | 5 | 3.21 % | 15.24 % | $934 | 0.193 | $788 |
| A1 members k7 | 7 | 2.91 % | 14.63 % | $828 | 0.171 | $705 |

Every multi-sleeve variant is worse per unit of exposure. The AS-1 "several strategies at
once" analogy is **closed for us** — the ensemble's pre-decision averaging is doing real work
that independent sleeves cannot reproduce. (Their holdout Sharpes are high, 0.95–1.00, but the
holdout is exhausted and dev governs; not chased.)

## FB did NOT fire — two never-used Solar signal types qualify

Both come from vendor math the campaign already owns (`solarwave.py`), at zero cost:

| variant | capture | big-day | wk mean | wk pos | Sharpe | stress | holdout |
|---|---|---|---|---|---|---|---|
| base | 5.01 % | 17.77 % | $1,484 | 59.6 % | 0.214 | $1,305 | 0.666 |
| A2 strong-trend-only (`\|signal_trend\|==2`) | 5.11 % | 17.62 % | $1,518 | 58.3 % | 0.222 | $1,358 | 0.674 |
| **A4 wave-agreement gate (`signal_wave` sign)** | **5.18 %** | 17.73 % | **$1,542** | 58.7 % | **0.225** | **$1,376** | 0.678 |
| A3 + strengthen (T3) pulses | 4.76 % | 18.01 % | $1,377 | 57.4 % | 0.197 | $962 | 0.726 |

A3 (adding T3 "strengthen" entries) more than doubles trade count and dilutes: rejected.

## Cumulative single-sleeve progression (each step has a mechanism)

0.160 (W01 raw S4) → 0.193 (delta gate, W03) → 0.210 (range throttle, W09) → 0.214 (drop
CLOSE hour, W11) → **0.225 (wave gate, W12)**.

## MANDATORY NEXT: null calibration

Twelve waves have evaluated 250+ variants on one dev sample. Compounding small qualified
improvements is exactly the pattern that produces a fitted stack. W13 is a **discipline wave,
not an improvement wave**: null-calibrated gate testing, per-year stability, and parameter
sensitivity of the accumulated stack.
