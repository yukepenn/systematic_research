# Type-0 attribution and controlled signal architectures

_2026-08-07 · evidence: `research/09_sleeves/` (C2, C2-adaptive, C4, wave conditioning) and the
Wave-1 S4 signal-type runs · engine confirmations on 3-minute NQ, real slip-1, SM 180–250,
8 matched cells each · attribution screens in Python via `solar_wave_full()` at zero
configuration budget._

## 1. What "Type 0" actually is

`Signal_Trade = 0` is **not a signal** — it is the absence of an event on that bar. The wrapper's
`EntrySignalType = 0` is a separate thing: **first non-zero signal while flat wins.**

It follows that raw Type-0 P&L is **not** decomposable:

```
PnL(Type 0)  !=  PnL(Type 1) + PnL(Type 2) + PnL(Type 3)
```

Whichever signal fires first while flat takes the position and **suppresses every other signal**
until the next exit. This is why attribution had to wait for the complete model: it requires
replaying the arbitration, and before Wave 2 the Type-2 arrival times were unknown.

## 2. Displacement — the core measurement

With `solar_wave_full()` exact, all three types can be generated in Python and the state machine
replayed exactly, at zero engine time.

| finding | value |
|---|---|
| Type-3 re-entries, marginal economics (Python screen) | **+$73.55 / marginal trade** |
| per-trade economics by wave index | $26 → $53 → $76 → $151 (waves 1 → 4) |
| Type-2 average trade | **$22.61** at a 28 % win rate |
| raw Type-0, full history, analytic slip-1 (Wave 1 S4) | ≈ **$123k** vs Type-1's ≈ $162k |

Raw Type-0 **underperforms the Type-1 core it contains.** First-eligible-wins lets a cheap Type-2
occupy the position and displace the Type-1 flip that would otherwise have caught the whole trend.
That is the displacement cost, and it is why "use all the signals" is worse than "use the good one".

## 3. Controlled architectures — what was actually run

| id | architecture | status | net | Sharpe | max DD | worst year |
|---|---|---|---|--:|--:|--:|
| **C0** | raw first-signal-wins Type 0 | **run** (Wave 1, full history, analytic slip-1) | ≈$123k | — | — | — |
| **C1** | Type-1 core (R4 plateau) | **run** | $180,479 | 0.784 | −$53,689 | +$7,796 |
| **C2** | C1 + one Type-3 re-entry per episode | **run** | **$233,628** | **0.862** | **−$47,413** | **+$19,801** |
| **C4** | C1 + one Type-2 *or* Type-3 re-entry | **run** | $141,303 | 0.450 | −$64,621 | +$9,988 |
| C3 | C1 + selective early-wave Type 2 | **NOT BUILT** | | | | |
| C5 | state-dependent priority | **NOT BUILT** | | | | |
| C6 | capped stacking on one risk budget | **NOT BUILT** | | | | |

**C3, C5 and C6 were never implemented.** They are not reported as failures — they were not run.
The reason is recorded rather than rationalised: C4 established that adding Type 2 to the core
costs 0.33 Sharpe, and the wave-conditioning sweep (below) found no usable structure to condition
a *selective* Type-2 rule on. With both the ingredient and the selector dead, C3/C5/C6 had no
remaining mechanism to test. That is a judgement call, and a different researcher could reasonably
have built C3 anyway.

## 4. C2 looked like the campaign's best finding — and then failed

C2 improved **every point estimate simultaneously**: +29 % net, +0.078 Sharpe, a *smaller*
drawdown, and a 2.5× better worst year. That is unusual here; most changes trade one against
another. Marginal economics: +10,838 trades earning $425,191 = **+$39.23 per marginal trade**,
above the core's own $34.44 average.

It still failed, for two independent reasons.

**It never cleared significance.** Tested on its own 19,606 marginal trades — a far
higher-powered test than comparing two correlated ensemble Sharpes:

| test | result |
|---|---|
| mean marginal trade | +$24.89 |
| naive iid t-test | t = 2.432, one-sided p = 0.0075 |
| **session-block bootstrap** (respects clustering) | **P(mean ≤ 0) = 0.1147** |
| ensemble ΔSharpe vs C1 | +0.078, P(Δ ≤ 0) = 0.413 |

The iid test clears 5 %; the block bootstrap, which is the correct one, does not.

**It failed its interaction test.** On the *adaptive* core, the same sleeve costs **0.40 Sharpe**
(ΔSharpe −0.402, P(Δ ≤ 0) = 0.879) and breaks the every-year-positive property. A sleeve whose
sign flips when the core's threshold rule changes is exploiting an interaction with one specific
core, not capturing an effect. **Rejected.**

Structural weaknesses already visible before that test: it loses **$98,220 in 2022**, and its gain
concentrates in the wide cells (SM 230/240/250 contribute $111k/$125k/$136k while SM 200 is
slightly negative).

## 5. Wave conditioning — the last available selector

The Python screen showed per-trade economics rising monotonically with wave index
($26 → $53 → $76 → $151), which is the single most promising conditioning signal in the model.
Taken to the engine across `MinWave` 1–8, it produced **Sharpe 0.54–0.93, non-monotone**. No usable
signal. The wave counter describes trend structure faithfully but is not an edge.

This is a clean example of a Python-screen effect not surviving the engine, and it is the reason
the campaign requires engine confirmation before any screen result is promoted.

## 6. Verdicts

| claim | verdict |
|---|---|
| Raw Type 0 beats Type 1 | **FALSE** — ≈$123k vs ≈$162k; displacement costs more than the extra signals earn |
| Type-0 P&L decomposes into its parts | **FALSE by construction** — path-dependent arbitration |
| Adding Type 2 to the core helps (C4) | **FALSE** — −0.33 Sharpe |
| Adding one Type-3 re-entry helps (C2) | **REJECTED** — best point estimates in the campaign, but P(mean ≤ 0) = 0.115 and the sign flips on an adaptive core |
| Wave index conditions expectancy | **FALSE** in the engine — 0.54–0.93, non-monotone |
| C3 / C5 / C6 | **NOT RUN** — no surviving mechanism after C4 and wave conditioning failed |

**Net conclusion: the Type-1 core stands alone.** Every attempt to add a second signal type to it
either lost money outright or failed to separate from noise. Signal arbitration is closed.
