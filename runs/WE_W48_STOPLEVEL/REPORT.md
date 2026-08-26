# WE_W48 — THE STOP LEVEL, MEASURED EXACTLY · REPORT

Spec preregistered. **B1 PASS** (14.72 pts/session). Full window 2022-07 → 2026-08.

**My hypothesis was WRONG and the wave was still necessary.** I suspected W42 had killed stops
on a badly chosen level. It had chosen the worst possible level — and no other level works
either. W42's conclusion survives, now with the entire surface measured instead of one point.

---

## 1. Phase 1 — exact accounting, no backtest (`FACT`)

1,950 trades, 37.8 % winners. Winners' MAE quantiles: q50 = 0.86, q75 = 1.76, q90 = 3.36,
q95 = 4.92, q99 = 9.23 ATR. Losers' median MAE = 2.70 ATR.

| stop (ATR) | winners cut | losers cut | **cut ratio** | $ saved | $ lost | **net $** | worst week after |
|---|---|---|---|---|---|---|---|
| 0.86 (W42's choice) | 50.2 % | 91.2 % | 1.82 | 347,125 | 579,873 | **−232,748** | **−3,732** |
| 1.76 | 25.0 % | 71.2 % | 2.85 | 197,501 | 398,098 | −200,597 | −6,828 |
| 3.36 | 10.0 % | 39.4 % | **3.92** | 74,718 | 186,696 | −111,978 | −7,034 |
| 4.92 | 4.9 % | 21.9 % | **4.49** | 22,699 | 100,908 | −78,209 | −7,514 |
| 7.61 | 1.5 % | 7.2 % | **4.81** | 10,418 | 45,161 | −34,743 | −7,418 |
| 12.77 | 0.5 % | 1.3 % | 2.43 | 5,684 | 14,416 | −8,732 | −7,418 |

**The separation the campaign hoped for is real: a stop cuts losers 1.8× to 4.8× more often
than winners.** And it does not matter. **Net P&L is negative at every level**, because the
count asymmetry is overwhelmed by the VALUE asymmetry — the winners a stop cuts are worth far
more than the losers it saves. At the most aggressive level: $347k saved, $579k lost.

**And the trade-off has no middle.** Either you halve the worst week (−$7,418 → −$3,732) and
give up **78 % of all the money** ($232,748 of ~$299k over 203 weeks), or you keep the money and
the worst week does not move at all. Every intermediate level is worse on both counts than the
two ends.

## 2. Phase 2 — the backtests confirm the accounting

| arm | pts/session | weekly | worst week | Sharpe | eff | cvEff |
|---|---|---|---|---|---|---|
| **P1 incumbent** | **14.72** | $1,470 | −$7,418 | **0.311** | **0.198** | **0.272** |
| stop @ q50 (0.81 ATR) = W42's | 6.03 | $602 | −$7,531 | 0.179 | 0.080 | 0.109 |
| **stop @ q75 (1.72 ATR)** | 7.62 | $761 | **−$5,777** | 0.214 | 0.132 | 0.154 |
| stop @ q90 (3.33 ATR) | 9.37 | $935 | −$6,920 | 0.240 | 0.135 | 0.171 |
| stop @ q95 (4.91 ATR) | 11.82 | $1,180 | −$7,515 | 0.259 | 0.157 | 0.212 |
| stop @ q99 (8.73 ATR), re-entry allowed | 13.83 | $1,381 | −$7,418 | 0.302 | 0.186 | 0.261 |

Monotone: as the stop moves away, production recovers toward the incumbent and the tail
benefit vanishes. **The best defensive point is q75: the worst week improves 22 % (−$7,418 →
−$5,777) for 48 % of the production.** Recorded on the Pareto frontier as a DEFENSIVE object;
not adopted, because eff falls 0.198 → 0.132 and eff is the owner's metric.

## 3. What this settles, and the bound it puts on the campaign

`SUPPORTED`, and now with the full surface rather than one point:
> **The tail of this object cannot be attacked at the trade level.** It is not a tuning
> problem. The payoff structure that produces the expectancy — 37.8 % winners carrying
> everything — is the same structure that makes the tail irreducible by stops.

Consequence for the owner's objective, stated plainly:
- eff is 0.198. $10,000/week at a −$15,000 worst week needs eff ≈ 0.67.
- Contracts cannot move eff (it is exposure-invariant).
- Nine signal families and eight structural axes are falsified (W25, W27, W38–W43, W45–W48).
- Trade-level risk control is now measured to be impossible on this payoff.
- **Session-level truncation already works** and is already in the object (the box: halt
  −$1,300, target +$1,000 — the only mechanism that ever improved both the tail and Sharpe).

So the remaining routes to a materially higher eff are: **a different payoff structure with a
genuinely higher hit rate**, or **genuinely new information** (VWAP Flux, order flow). Both are
outside what has been searched, and one of them costs $300 and is the owner's decision.

## 4. Method note
Phase 1 cost no backtest and answered the question more completely than phase 2 did. **Exact
accounting on already-measured paths should precede any parameter sweep** where the mechanism
can be written down — it produces the whole surface, including the levels a sweep would never
think to try, and it makes the reason visible rather than inferred.
