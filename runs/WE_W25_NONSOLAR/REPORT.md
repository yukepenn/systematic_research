# WE_W25 — NON-SOLAR ENGINES · REPORT

## The unexamined assumption, tested

Every engine in 24 previous waves is Solar: S1 (T1 flips), S4 (the 13-member ratchet
ensemble), ASIA (S4 by clock), the E5 vote (32 configurations of the same state machine),
the mirror short. This wave built trend engines with **zero Solar content** inside the audited
wrapper (long-only, range throttle 0.8, session halt $1,300, next-open fills, session-flat).

| engine | trades | wk mean | % pos | worst | Sharpe | stress | **corr with E5** |
|---|---|---|---|---|---|---|---|
| N1 Donchian 60 | 38,176 | −$769 | 36.6 % | −$6,983 | **−0.341** | −$2,631 | **0.11** |
| N1 Donchian 240 | 20,084 | −$421 | 39.5 % | −$7,486 | −0.221 | −$1,400 | 0.11 |
| N2 EMA 20×100 | 7,272 | $676 | 50.2 % | −$12,573 | 0.113 | $322 | **0.55** |
| N2 EMA 60×480 | 3,226 | $861 | 55.1 % | −$15,417 | **0.134** | $704 | 0.47 |
| N3 momentum-of-momentum | 28,038 | $92 | 44.4 % | −$11,490 | 0.020 | −$1,276 | 0.46 |
| N4 range position | 15,550 | $238 | 46.3 % | −$11,248 | 0.056 | −$521 | 0.34 |
| N5 non-Solar vote | 20,554 | $49 | 45.4 % | −$11,855 | 0.011 | −$954 | 0.37 |

Combinations rejected: `E5halt+N5` gains 3.4 % production for 67.4 % more tail;
`E5halt+S1+N5` gains 2.0 % for 35.3 %. The N5 vote fails its circular-shift null
(71st percentile, p = 0.29) — **NOT EVIDENCE**.

## The pattern is the finding

**The orthogonal engines lose money; the profitable engines are not orthogonal.** Donchian is
genuinely uncorrelated (0.11) and deeply negative; EMA-cross is the only profitable non-Solar
form and it correlates 0.47–0.55 because it is following the same moves.

## MODEL-RISK STATEMENT (to be repeated in every future summary)

**This campaign owns exactly ONE model: the Solar volatility-scaled ratchet.** Everything
else is packaging. The measured 0.19 correlation between S1 and the S4 family understates the
true shared risk, because a decay in the ratchet's edge would take every sleeve at once. No
independent model was found in this wave.

## Mechanism information gained
A naive breakout (close above an N-bar high) **loses heavily** on 1-min NQ (−0.341) where the
ratchet earns. So the Solar edge is **not** breakout capture — it is a volatility-scaled
trailing-reversal detector that enters trend continuation *after* a confirmed retracement.
That two rules aimed at "trend" diverge this sharply is real information about what the
instrument pays for.
