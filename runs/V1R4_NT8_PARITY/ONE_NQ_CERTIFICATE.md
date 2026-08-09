# BEST_ONE_NQ PARITY CERTIFICATE — SolarWaveOneContractNQ_v4

**STATUS: NOT CERTIFIED — warmup substantially improves agreement (decision/trade COUNT now
matches almost exactly), but a real, smaller residual dollar discrepancy remains and was not
driven to a confirmed first-divergence root cause this wave.**

## Identity

| field | value |
|---|---|
| strategy | SolarWaveOneContractNQ_v4 |
| source hash | repo `src/ninjascript/SolarWaveOneContractNQ_v4.cs` = 23,793 bytes |
| deployed NT8 hash | byte-identical (23,793 bytes), confirmed via `ReadNinjaScriptFile` this session |
| instrument | NQ 09-26 (NQU6), both signal and execution legs |
| bars | 3-minute |
| session | CME ETH, session-relative C4 flatten, 16:45 mandatory close honored |
| commission | NinjaTrader Brokerage Lifetime ($2.18/side NQ) |
| slippage | none added (Standard fill, no override) |
| fill mode | Standard |

## Warmup-corrected comparison (same methodology as Product A's certificate)

| test | Q1 2025 net |
|---|---:|
| NT8, warmed-up from 2024-04-01 (9 months warmup) | **-$6,661.52** |
| Python twin, continuation state from 2022 (full history) | **-$5,605.88** |

**Difference: -$1,055.64, 18.8% relative to the Python figure** -- both sides now agree on SIGN
(both negative) and rough magnitude, a large improvement from a hypothetical fresh-start
comparison, but the relative gap is materially larger than Product A's 0.71%. Disclosed candidate
explanation: the underlying quarter's net magnitude here (~$5-6k) is much smaller than Product
A's (~$9-12k), so a similarly-sized ABSOLUTE dollar gap reads as a larger PERCENTAGE -- this is a
real statistical effect (small-denominator amplification), not proof the underlying $ gap itself
is proportionally larger, but it is not, on its own, sufficient grounds to certify.

## Decision/trade-count agreement — strong, and directly checked

| | count |
|---|---:|
| NT8 Q1-2025 trade count (this window) | 107 |
| Python incumbent position-change events in Q1 2025 | 212 (~106 round trips) |

**Trade counts match almost exactly (106 vs 107, off by at most 1)** -- this is strong evidence
that the DECISION LOGIC (when to enter/exit/reverse) agrees closely between the real NT8 object
and the Python replica; the residual dollar gap is much more likely a smaller, cumulative
FILL-PRICE or rounding effect across ~107 trades than a structural decision-logic defect. This
was NOT carried further to an actual first-divergence trade-by-trade price comparison this wave.

## Residual discrepancy classification (partial, not completed)

Per the directive's classification taxonomy, the evidence gathered this wave is most consistent
with **FILL** or **ORDER_TIMING** (small, cumulative per-trade price differences) rather than
**SIGNAL**, **SESSION**, **WARMUP** (warmup's contribution is already isolated and mostly
resolved), **ROUNDING** (Python's `_fill()` 1-tick-adverse-slip approximation vs NT8's real
Standard-resolution fill could plausibly diverge more on a leaner-margin, higher-turnover object
like this one than on Product A's larger, more graded target). **Not proven** -- this is the
recommended starting hypothesis for a future session's continuation, not a closed finding.

## What remains open

Same CrossTrade long-job limitation as Product A's certificate (full multi-year not attempted for
NQ this wave, given the smaller residual already found on the shorter window warranted
prioritizing the classification work above over a longer run). A trade-by-trade (not just
count-level) comparison for this specific Q1-2025 window is the concrete, scoped next step.

## Final verdict

**NOT CERTIFIED.** The warmup fix resolves the majority of what a fresh-start comparison would
have shown, and decision-level (trade-count) agreement is strong, but an ~19%-relative,
un-root-caused residual on the tested window means this does not clear the bar. No object's
shipped status changes -- `_v4` was never claimed certified before this wave either.
