# M4_ANCHOR — RESULTS

Run against `spec.yaml` (frozen `1b7f510`). Parity assertion (mode=CLOSE vs
`sm01_solarsim.member_states`/`member_trades` original, all 13 VolMults): **PASS**. Control
cross-check: **PASS**. Code: `src/m4_common.py`, `src/run.py`.

**Process note**: a cosmetic bug (unpacking a plain int as a dict when writing
`flip_decomposition.csv`, after all real results had already been computed and printed) crashed
the tail of the first run. Fixed in `run.py`; `gates.csv` and every substantive result had already
been written before the crash, so no results were lost or need re-verification.

## Headline: both variants fail cleanly and decisively — H-008's "chases wicks" finding replicates
under the current architecture, and close-confirmation does NOT rescue it here

| | Sharpe | ΔSharpe | CDaR | top10 | flips vs control | false reversals (≤5 bars) | VERDICT |
|---|---:|---:|---:|---:|---:|---:|---|
| CONTROL (close anchor) | 0.709 | — | $27,162 | 100% | 100% | — | — |
| HILO_RAW | 0.393 | **−0.316** | $29,463 | 75.0% | **169%** | 25,267 | CONFIRMED-NOT-BENEFICIAL |
| CLOSE_CONFIRMED | 0.409 | **−0.300** | $35,146 | 88.6% | 125% | 9,651 | CONFIRMED-NOT-BENEFICIAL |

**HILO_RAW replicates H-008's pre-SYSTEM_MASTER rejection almost exactly** (Sharpe 0.393 here vs
0.527 there — both far below their respective controls) **and does so more decisively under the
current 13-member architecture**: 69% more flips than control and 25,267 false reversals (an
opposite-direction flip within 5 bars of the prior one) — a direct mechanical confirmation of "the
ladder chases wicks." Every gate fails outright: Sharpe, CDaR, top-10 retention, chronology (0/5
years positive), and tail preservation (top-20-move retention only 46.8%, more than half the
largest moves lost).

**CLOSE_CONFIRMED — the construction that reportedly passed standalone in the old, pre-
SYSTEM_MASTER campaign — does NOT transfer to the current architecture.** It still trades 25% more
than control, still posts a large Sharpe deficit (−0.300), and its top-20-move retention is
actually the *worst* number in this table (22.4%) despite having fewer false reversals than
HILO_RAW — confirmation reduces whipsaw-driven churn (9,651 vs 25,267 false reversals, roughly a
third) but the intrabar-origin anchor itself still degrades trend capture badly enough that the
net effect is clearly worse than the incumbent, not merely "redundant" with it. **This corrects the
old campaign's finding for the current system**: whatever made close-confirmed redundant-but-
harmless in the original architecture does not hold under the current ensemble/aggregation stack.

## Why this happens (directive's own framing, confirmed mechanically not just by P&L)

Directive §6 frames this as a tail/selectivity hypothesis — intrabar extrema might define the true
excursion origin better than closes. The flip/false-reversal counts show the opposite is happening
here: moving the anchor to intrabar highs/lows makes the state machine *more* reactive to single-
bar noise, not less — anchor-tracking off `high`/`low` extends the running extreme further on every
favorable wick, which paradoxically makes the *subsequent* reversal threshold easier to clear from
a more extreme starting point in choppy conditions, at least as measured here. This is a genuinely
different failure mode from ATR's (which changes threshold *magnitude*, not anchor *origin*) and
the two remain appropriately un-combined per the frozen spec's discipline.

## What this closes

Both anchor constructions are now **CONFIRMED-NOT-BENEFICIAL under the current SYSTEM_MASTER
architecture**, joining H-008 (which established the same conclusion under the original campaign's
architecture) as a second, independent confirmation. The anchor-placement axis is closed for this
campaign; a future idea in this space needs a genuinely different construction (e.g., a damped or
partial intrabar anchor), not another close/high-low binary. No red team required (V7 §G — clean
negative results, no promotion proposed).
