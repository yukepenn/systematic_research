# R4 — slope + impulse residual-information tests — RESULTS

Per `spec.yaml`'s information-addition framework (directive sec35). **Disposition: R4-A (slope)
CLOSED — REDUNDANT. R4-B (impulse/CLV) finds a real, stable, incremental signal — CLOSED WITHOUT
CONSTRUCTION this run (deferred), not because the finding is false, but because the effect is
modest and demonstrably right-tail-risky if naively thresholded.**

## R4-A — regression slope: CLOSED, REDUNDANT WITH INCUMBENT STATE

Causal 20-bar linear-regression slope of close price, ATR-normalized, oriented in the trade's own
direction (`slope_aligned`): raw Spearman vs net_pnl **0.0204**; after residualizing against the
existing M-strength × vol-tercile bucket structure, **0.0111** — statistically negligible, and OLS
R² improvement over the M_abs+vol baseline is **+0.00025** (essentially zero). **The trend
architecture already knows what a short-term price slope would tell it** — Solar13's own 13-member
directional-change ensemble is, functionally, a more sophisticated multi-horizon slope detector,
so this null result is mechanistically unsurprising, not merely a data-mining miss. Per spec.yaml's
falsification condition, R4-A is closed as redundant. No construction attempted.

## R4-B — explosive candle / impulse: a real, stable, but modest incremental signal

Three impulse features tested at the entry bar: `range_atr` (bar range / ATR), `body_atr`
(body size / ATR), and `clv_aligned` (close-location-value, oriented to trade direction — a
strong, decisive close at the extreme of its own bar, in the trade's favor). `range_atr` and
`body_atr` show no meaningful residual relationship (Spearman -0.043 and -0.038, both essentially
noise, OLS ΔR² ≈0 and +0.0014 respectively) — "big candle = buy" is NOT supported.

**`clv_aligned` is different**: raw Spearman **0.1099**, residualized (after removing M-strength ×
vol bucket effects) **0.1056** — the relationship survives conditioning on existing state, i.e. it
is genuinely incremental, not a restatement of "the entry was already strong." OLS R² improves from
0.00470 (M_abs + vol alone) to **0.01379** with `clv_aligned` added (+0.0091, roughly 3x the
baseline explanatory power, though both remain small in absolute terms — typical and expected for
single-trade financial outcome prediction). **Year-by-year: positive in all 5 years** (2022 +0.031,
2023 +0.140, 2024 +0.127, 2025 +0.099, 2026 +0.163) — a genuinely stable, non-sign-flipping,
multi-year relationship, the exact bar directive sec41/sec43 hold every other finding in this
campaign to.

## Why this is NOT constructed this run: right-tail risk, checked directly

Per this campaign's standing right-tail discipline, `clv_aligned` was checked against the top-20
all-time winners before any construction was considered: **3 of 20 (15%) have a "poor" CLV
(<0.3)**, including the **3rd-largest winner in the campaign's history** ($16,267.82, CLV=0.186)
and a **$13,257.82** winner (CLV=0.264). A naive hard filter requiring good CLV to enter would have
excluded these specific, real, large winners — the same class of mistake R1's giveback overlay and
R3's weak-M-tercile lead were both disqualified for. The bottom-20 losers show a statistically
similar CLV distribution to the population at large (mean 0.45 vs population mean 0.48) — CLV does
NOT cleanly separate the worst losers either.

**This does not mean the finding is false — the aggregate correlation (0.10-0.16, stable across 5
years) is real and would very likely survive further testing as a SIZING or soft-weighting signal
(e.g., a small score adjustment) rather than a hard entry gate.** But building and validating that
correctly (avoiding the exact naive-threshold mistake this campaign has now made and caught twice
this session — R2B's look-ahead bug, and conceptually here the same right-tail-blindness pattern
R1/R3 already failed on) is a materially larger undertaking than this run's diagnostic scope, and
the effect size (ΔR² ≈0.009) is modest enough that the expected payoff does not clearly justify
displacing the remaining, still-larger R5/R6/PA0/PA1/synthesis work in this finite campaign queue.

## Disposition

**R4-A (slope): CLOSED — REDUNDANT.** **R4-B (impulse/CLV): a real, disclosed, stable positive
finding, explicitly NOT constructed this run** — recorded as a well-evidenced lead for a future,
separately preregistered soft-weighting/sizing study, not silently dropped and not forced into a
premature construction. No candidate built, no NinjaScript touched. Continuing automatically to
R5 per directive priority order.
