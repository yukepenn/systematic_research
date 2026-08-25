# WE_W15 — TRUE DELTA vs PROXY · REPORT

Sample: 48 NQ tick sessions (2025-08-11 … 2026-05-20), 63,327 covered 1-min bars, 19,036
available points. Per spec, **no Sharpe is quoted** from ~8 weeks.

| gate | trades | net | $/trade | capture | long $ | short $ |
|---|---|---|---|---|---|---|
| G0 no gate | 263 | $27,588 | 104.9 | 7.25 % | +41,543 | −13,955 |
| G1 **proxy** (current) | 214 | $24,992 | 116.8 | 6.56 % | +41,699 | −16,707 |
| G2 **true UpDownTick** | 198 | **$30,577** | **154.4** | **8.03 %** | +41,460 | −10,883 |
| G3 **true BidAsk** (his panel's mode) | 163 | $22,024 | 135.1 | 5.78 % | +42,519 | −20,495 |

## Preregistered decision: TICK DATA IS NOT WORTH ACQUIRING

- true UpDownTick vs proxy: **$/trade +32.2 %**, total **+22.3 %** → clears the per-trade bar,
  misses the total bar (it trades less). **Does not clear the declared 25 %-on-both rule.**
- true BidAsk vs proxy: $/trade +15.7 %, **total −11.9 %** → worse.

The delta axis is closed at its null-calibrated status: **weak evidence (p = 0.10)**. The gate
stays in the stack on its leave-one-out cost (+0.041 Sharpe on the full 4.6-year sample, which
is far better evidence than 48 sessions), but it is not a understood, high-confidence
mechanism and must never be described as one.

## Two non-obvious consequences

1. **The mode the trader's own VF panel was set to (BidAsk real volume) does not help our
   engine** — on this sample it is the worst of the three. Whatever VF contributes to HIS
   system, our engine does not extract value from BidAsk delta. This **weakens** one of the
   arguments for the VWAP Flux purchase: if VF is worth buying, it is for Fair Value, the
   rails and `Signal_Trade`, not for its delta.
2. All gates lose money on the short side on this sample (−$11k to −$20k) while the long book
   is stable at ~+$41.5k. Short-side handling is a separate, unsolved problem and is now on
   the open list.

## Owner framing adopted
This is the difference from p-hacking: every gate must state a mechanism, survive a
circular-shift null, and show a leave-one-out cost. Two of this campaign's own headlines
(the `signal_wave` gate, the CLOSE-hour drop) were killed by exactly that pipeline, and the
tick-data spend was refused by a rule written before the numbers were seen.
