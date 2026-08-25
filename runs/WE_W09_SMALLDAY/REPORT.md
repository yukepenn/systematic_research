# WE_W09 — SMALL-DAY DEFENSE · REPORT

Spec preregistered. Base = S4.narrow6 + lagged delta gate. **3 throttles QUALIFY** under the
preregistered rule (small-day points > base AND big-day capture ≥ 16.0 % AND weekly
Sharpe ≥ 0.193 AND stress > 0) — the campaign's first qualified improvement in three waves.

## Result

| variant | capture | **big-day** | small-day | small pts | wk mean | wk pos | worst | Sharpe | stress | tr/wk |
|---|---|---|---|---|---|---|---|---|---|---|
| BASE | 4.68 % | 17.55 % | −1.87 % | −5,100 | $1,373 | 59.1 % | −$28,985 | 0.193 | $1,132 | 24.1 |
| **A_range0.8** | **4.87 %** | **17.58 %** | **−1.60 %** | **−4,369** | **$1,431** | 59.1 % | **−$24,417** | **0.210** | **$1,250** | **18.1** |
| A_range0.6 | 4.77 % | 17.53 % | −1.73 % | −4,718 | $1,400 | 57.8 % | −$29,345 | 0.201 | $1,180 | 22.0 |
| A_range1.0 | 4.41 % | 16.31 % | −1.65 % | −4,505 | $1,280 | 56.1 % | −$19,895 | 0.204 | $1,140 | 14.0 |
| B_pnl1300 | 3.56 % | **11.60 %** | −0.53 % | −1,453 | $1,170 | 53.0 % | −$15,339 | 0.191 | $982 | 18.8 |
| C_move0.5 / 1.0 | 4.56 / 4.46 % | 17.4 / 17.1 % | −1.97 % | −5,356 | — | — | — | 0.190 / 0.188 | — | — |
| D_combo (A0.8+B1300) | 3.88 % | 12.20 % | **−0.36 %** | **−983** | $1,232 | 53.5 % | −$15,339 | 0.210 | $1,089 | 14.4 |

**A_range0.8 improves every dimension simultaneously**: +4 % capture, big-day edge intact
(17.55 → 17.58 %), bleed cut by 731 points (≈ $14,620), Sharpe +0.017, worst week +$4,568
better, stress +$118, and it does it while **trading 25 % less**. Holdout Sharpe unchanged
(0.665 vs 0.669) — no holdout selection involved.

## The mechanism lesson

**Throttle the REGIME VARIABLE, not the P&L SYMPTOM.** B_pnl (the S1 D-gate ported to S4) cuts
the bleed hardest (−983 pts in D_combo, an 81 % reduction) but collapses big-day capture to
11.6–12.2 %: a session P&L halt fires after the first adverse swing of a big trending day and
takes you out of exactly the move you needed. The range throttle targets what actually
distinguishes the two regimes and therefore costs nothing on big days.

C (distance from session open) fails: committing *direction* early is not the same as the day
having *range*, and it slightly worsens the bleed.

## Causality audit (standing rule since W03 am.1)

`norm[i]` is the median of the same minute-of-day's realized range over the trailing ≤60
sessions, populated **before** the current session's values are appended; `rng[i]` is the
session range through bar **i−1**. Both carry decision-bar information only. Verified in code
(`intraday_features`, the two-pass loop).

## Standing after nine waves

Best object: `S4.narrow6.gdl + A_range0.8` — dev capture 4.87 %, big-day 17.58 %, weekly
$1,431 / 59.1 % / −$24,417 / Sharpe 0.210, stress-positive, 18 trades/week. Still no promotion:
the arbiter is the virgin ≥ 2026-11-01 read.
