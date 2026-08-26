# WE_W45 — THE QUALITY LAYER ON THE PRODUCT'S OWN CLOCK · REPORT

Spec preregistered. **B1 PASS** (1-min full object reproduced at 14.72 pts/session).
Full window 2022-07 → 2026-08, net $4.36/RT, stress $14.36/RT.

**Verdict: the preregistered falsifier fires. The quality layer is specific to the 1-minute
event stream — and that explains why W41's adopted basket has the shape it does.**

---

## 1. The full object on each clock

| arm | trades | pts/session | $/trade | weekly | worst week | CVaR5 | Sharpe | eff | cvEff | corr | corrDD |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **C0 1-min (incumbent)** | 1,950 | **14.72** | $153.0 | $1,470 | **−$7,418** | −$5,398 | **0.311** | **0.198** | **0.272** | 1.00 | 1.00 |
| C1 3-min, σ = 460 bars | 1,298 | 11.02 | **$172.0** | $1,100 | −$15,410 | −$9,916 | 0.209 | 0.071 | 0.111 | 0.48 | 0.20 |
| C2 3-min, σ = 153 bars | 1,019 | 8.58 | $170.5 | $856 | −$17,486 | −$8,872 | 0.171 | 0.049 | 0.096 | 0.42 | 0.17 |
| C3 3-min, no pre-close block *(diagnostic)* | 1,300 | 11.34 | $176.7 | $1,131 | −$15,410 | −$9,916 | 0.214 | 0.073 | 0.114 | 0.49 | 0.22 |

C2 losing to C1 independently confirms W44's finding that **σ counted in BARS (460) is what the
code does**, not the wall-clock equivalent. C3 shows the pre-close block is not the issue.

## 2. The finding: the quality layer does not transfer (`FALSIFIED`)

| clock | base sleeve (W41) | + quality layer | effect on eff |
|---|---|---|---|
| **1-minute** | 10.62 pts, eff 0.142 | **14.72 pts, eff 0.198** | **+39 %** |
| **3-minute** | 9.40 pts, eff 0.079 | 11.02 pts, eff **0.071** | **−10 %** |

On the 3-minute clock the layer buys +17 % production and pays for it with a **30 % worse worst
week** (−$11,842 → −$15,410). Per year C1 is negative in 2022 (−$315/week) where C0 is +$1,024.

**Mechanism (`INFERENCE`, and it follows from W42's diagnostic).** The score forecasts
*excursion size*, so sizing up concentrates the week's P&L into the trades it picks. On the
1-minute clock that bet is spread over 1,950 short holds; on the 3-minute clock the object
already holds fewer, longer positions, so doubling a subset of them concentrates risk instead
of diversifying it. **Quality sizing needs a high enough event rate for the sizing bet itself
to be diversified.**

## 3. And at no weight does the 3-minute FULL object help

| pair, constant total exposure | weekly | worst week | Sharpe | eff | cvEff |
|---|---|---|---|---|---|
| w = 0.00, 1-min alone | $1,470 | −$7,418 | 0.311 | **0.198** | **0.272** |
| w = 0.10 | $1,424 | −$7,490 | 0.316 | 0.190 | 0.271 |
| w = 0.20 | $1,378 | −$8,234 | 0.318 | 0.167 | 0.257 |
| w = 0.50 | $1,241 | −$10,464 | 0.301 | 0.119 | 0.198 |
| w = 1.00, 3-min alone (scaled) | $1,012 | −$14,182 | 0.209 | 0.071 | 0.111 |

Monotone degradation. Contrast W41, where the 3-min **BASE** sleeve at w = 0.05 improved all
four metrics.

## 4. Why this matters — it validates W41's construction after the fact

W41's adopted basket is `1-min QUALITY object + 3-min BASE sleeve + range BASE sleeve`. It was
built that way because W41 was testing clocks as base sleeves, not because anyone had shown the
clock sleeves should skip the quality layer. **W45 shows they must**: adding the layer to the
3-minute sleeve turns a +5.6 % eff contribution into a −10 % one. The adopted shape is now
supported by evidence rather than by the order the waves happened to run in.

## 5. What is now known about the layer's domain
- LONG side only (W38: on shorts the same construction behaves like leverage)
- **1-minute event stream only** (this wave)
- it forecasts excursion size, not hit rate (W42)
- it beats both a count-matched random-sizing control and a random-five-feature control
  (W39 amendment 2: 97th/100th and 95th/97th percentiles)

That is a narrow, well-mapped domain — and everything outside it has now been measured rather
than assumed.
