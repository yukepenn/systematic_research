# WE_W18 — ALL-WEATHER ATTEMPT · REPORT (windows re-cut inside the modern regime, am.1)

## FAIL per spec — the quiet regime is not tradeable by mean reversion

BUILD = 2022–2023. All three quiet engines are negative before the selection rule can even run:

| quiet engine | BUILD Sharpe | TEST | CONFIRM |
|---|---|---|---|
| Q1 fade-VWAP k=1.0 / 1.5 / 2.0 | −0.193 / −0.157 / −0.190 | −0.199 / −0.239 / −0.214 | −0.093 / −0.125 / −0.148 |
| Q2 fade prior-day rail → open | −0.148 | +0.104 | −0.030 |
| Q3 Bollinger(20,2σ) mean reversion | −0.145 | −0.085 | −0.213 |

This is the **third independent confirmation** (W11 on the pooled modern sample, W18 on the
deep sample's design intent, W18 here inside the regime) that the quiet regime is
**defence-only**. Q2's single positive window (TEST +0.104) does not survive its own selection
rule, which requires BUILD first.

## The trend engine is positive in every modern sub-window

| | BUILD 2022–23 | TEST 2024–25H1 | CONFIRM 25H2–26 |
|---|---|---|---|
| T both sides | 0.152 | 0.262 | 0.228 |
| **T long-only** | 0.161 | 0.223 | **0.334** (70.8 % weeks, worst −$15,089) |

Long-only is the strongest object in the most recent window and was the only W17 finding to
replicate across eras. But **all three sub-windows share parameters chosen by looking at
2022–2026 as a whole**, so this is not out-of-sample evidence. That is precisely what W19
walk-forward exists to settle.

## Standing description of what we own (unchanged by this wave)
A long-volatility trend harvester on NQ: it earns in active-range sessions, is throttled out
of quiet ones, and no complementary quiet-regime engine has been found in three attempts.
"Every day profitable" is not achievable by adding a mean-reversion sleeve; the honest path is
to maximise the active-regime edge and stand aside otherwise.
