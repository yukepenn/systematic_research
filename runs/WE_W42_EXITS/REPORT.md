# WE_W42 — EXIT / PAYOFF ARCHITECTURE · REPORT

Spec + amendment 1 (look-ahead correction, appended before the corrected arms were read).
**B1 PASS**: P1 reproduced at 14.72 pts/session, and `fills_rest` with no exit rules is
byte-identical to the incumbent fill layer. Entries frozen in every arm. Net $4.36/RT.

**Verdict: the preregistered falsifier fires. No exit mechanism clears.** The structural exit
(opposite flip) plus the session box is already this object's efficient exit frontier.

---

## 1. PHASE 1 — the shape of our own payoff (`FACT`, the wave's real content)

1,950 trades of the frozen entry set, walked bar by bar:

| | all | winners | losers |
|---|---|---|---|
| share | 100 % | **37.8 %** | 62.2 % |
| MFE (ATR) | 1.87 | 6.62 | 1.01 |
| MAE (ATR) | −1.94 | −0.86 | −2.70 |
| capture = realised ÷ MFE | −0.384 | **0.414** | −1.616 |
| give-back of MFE | **1.384** | 0.586 | 2.616 |

**This is a low-hit-rate, high-payoff object.** It wins 37.8 % of the time, its winners keep
only 41 % of their favourable excursion, and the median trade gives back **more than its entire
MFE**. Any intuition built on "protect the profits" has to survive that arithmetic — and §3
shows none of the obvious ones do.

**Early adversity predicts failure, and it is decided by bar 5.** P(final win | MAE ≤ −x ATR
within m bars):

| x ATR | m=5 | m=10 | m=20 | m=40 |
|---|---|---|---|---|
| 0.25 | 32.4 % | 32.3 % | 32.7 % | 32.8 % |
| 0.50 | 29.0 % | 28.8 % | 29.2 % | 29.3 % |
| 0.75 | 26.9 % | 26.1 % | 25.8 % | 26.2 % |
| **1.00** | **24.0 %** | 23.8 % | 23.4 % | 23.7 % |

Unconditional 37.8 %. Monotone in the threshold and **flat in the horizon** — the information
is entirely in the first five bars, and waiting adds nothing. (§3 shows that knowing this is
not the same as being able to trade it.)

**The quality score forecasts EXCURSION SIZE, not hit rate** — the mechanism behind sizing:

| score | n | win % | MFE (ATR) | MAE (ATR) | $/trade |
|---|---|---|---|---|---|
| 0 | 550 | 36.4 | 1.51 | −1.58 | 30.5 |
| 1 | 673 | 35.1 | 1.30 | −1.69 | 37.9 |
| 2 | 369 | 39.8 | 2.89 | −2.46 | 97.8 |
| 3 | 266 | 39.8 | **3.10** | −2.86 | **503.5** |
| 4 | 82 | 53.7 | **5.45** | −2.45 | **874.1** |

Win rate is ~flat at 35–40 % across scores; **MFE doubles to triples**. So the score does not
find trades that are more likely to work — it finds trades that go **further when they do**.
That is exactly why *sizing* pays and *filtering* destroyed production (W34).

**Survival curve** — E[remaining]/ATR by bar-in-trade: 0.689 (t=0) → 1.029 (t=10) → 1.807
(t=60) → 2.454 (t=90). **Interpretive caution recorded with it**: this is survivorship, not an
argument to hold longer. Trades alive at t=90 are precisely the ones the ratchet has not
flipped; it says the structural exit is already selecting well.

## 2. The look-ahead, and what it was worth (`FALSIFIED`)

Read 1 updated the running MAE/MFE with **bar i's own high and low** and then exited at **bar
i's open**. Same class as W03's gate. It had already produced the highest Sharpe in campaign
history. Corrected to resting orders at levels known before the bar trades:

| arm | contaminated (read 1) | **causal (corrected)** |
|---|---|---|
| E2 MAE invalidation | 18.08 pts/session, Sharpe **0.465** | **6.03 pts/session, Sharpe 0.179** |
| E3 give-back cap | 15.53 pts/session, Sharpe 0.440 | **2.38 pts/session, Sharpe 0.083** |

**This is the largest look-ahead the campaign has found** — larger than W37's 3.05 pts/session.
Two further defects in the same arms: re-entry on the next bar turned the "stop" into a one-bar
skip (trade count 1,950 → 3,204), and E1 could only exit *earlier*, never later, so all three
of its rows were identical to the reference and nothing was tested.

## 3. The corrected arms — all reject

| arm | pts/session | weekly | worst week | CVaR5 | Sharpe | eff | cvEff |
|---|---|---|---|---|---|---|---|
| **P1 incumbent (reference)** | 14.72 | $1,470 | −$7,418 | −$5,398 | 0.311 | 0.198 | 0.272 |
| **P2 = + 23-bar causal cut** | 13.50 | $1,347 | **−$5,818** | **−$4,540** | 0.291 | **0.232** | **0.297** |
| E2 stop at winners' median MAE | 6.03 | $602 | −$7,531 | −$5,529 | 0.179 | 0.080 | 0.109 |
| E2b same, re-entry allowed | 11.65 | $1,163 | −$8,331 | −$6,082 | 0.287 | 0.140 | 0.191 |
| E3 trailing give-back stop | 2.38 | $238 | −$9,770 | −$5,880 | 0.083 | 0.024 | 0.040 |
| E3b same, re-entry allowed | 10.84 | $1,082 | −$6,545 | −$5,130 | 0.289 | 0.165 | 0.211 |
| E4 stops on high-score only | 7.66 | $764 | −$5,490 | −$4,721 | 0.230 | 0.139 | 0.162 |
| E5 partial at winners' median MFE | 10.96 | $1,094 | −$7,481 | −$5,305 | 0.293 | 0.146 | 0.206 |

**Why every stop fails, mechanistically**: phase 1 measured winners' median MAE at 0.86 ATR —
i.e. **the trades that eventually work routinely go against us by almost a full ATR first**. A
stop placed at the level winners typically endure necessarily cuts a large share of them, and
in a 37.8 %-hit-rate object the winners are the entire P&L. The give-back stop fails for the
mirror reason: winners give back 58.6 % of their MFE on the way to a *profitable* exit, so a
give-back cap set at that level exits winners before the ratchet does. **The path statistics
predict the result — the stops are not badly tuned, they are structurally incompatible with
this payoff.**

**E1 hysteresis is a genuine Pareto point, not an adoption**: holding while the vote ≥ 0.25
lifts production to **17.45 pts/session** (+18.5 %) and Sharpe to 0.337, and doubles the worst
week to −$14,621 (eff 0.119 vs 0.198). Recorded on the frontier as a PRODUCTION variant for an
owner who prefers Sharpe and production over tail; not adopted under the stated objective.

## 4. The incumbent cut, finally null-tested
P2's 23-bar causal cut had never faced a count-matched control. Against 100 draws with the stop
distance randomised from the same distribution: **100th percentile, p = 0.000 — EVIDENCE.**

## 5. Standing addition
> A stop or trailing rule must be implemented as a **resting order at a level known before the
> bar trades**, and every stop arm must be reported next to its **re-entry-allowed control** —
> without that control a "stop" can silently be a one-bar skip.

## 6. Where this leaves the campaign
Exit engineering is **closed** on this object. Entry information is closed (W39). The short
side is closed (W38). Four non-ratchet mechanisms are closed (W40). What remains open:
the multi-clock axis (W41, running), multi-instrument re-derivation with per-instrument
volatility scaling (W11 only transplanted NQ's tick-denominated clamp, which was structurally
wrong), and an independent-implementation check in NinjaTrader.
