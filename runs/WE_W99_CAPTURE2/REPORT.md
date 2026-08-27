# WE_W99 — CURRENT MOVEMENT CAPTURE LEDGER v2 · REPORT

> ⚠️ **LANGUAGE CORRECTION (2026-08-27, owner directive V4 §2), binding on every number below.**
> `SIGN_ORACLE` **knows the future direction of each segment.** It is
> `EX_POST_EXECUTION_FEASIBLE_ORACLE` — an upper bound after turnover and friction, **NOT causally
> available money** — and it must never be called a causal or executable opportunity. See
> `research/weekly_edge/OPPORTUNITY_LANGUAGE.md`. The durable finding of this wave is the **bar**,
> not the ceiling: for the one-trade-per-segment geometry, break-even directional accuracy is
> **≈50.5 %–51.4 %, MORN ≈50.48 %** — and that figure is **geometry-specific and does not
> generalise to other strategy shapes**.

Preregistered (`spec.yaml`, committed at `e3ba026` before any result was read). Owner directive V4
§2 / §6 / §13 — TASK 4, 5 and 7. `W99b` is a **repair supplement**, written after W99's own
denominator failed, and is labelled as such throughout.

> ## THE ONE NUMBER THAT SHOULD CHANGE WHAT WE DO NEXT
> ## **A one-trade-per-segment direction call on NQ breaks even at 50.5 %–51.4 % accuracy.**
> ## The morning session needs **50.48 %**. That is the friction bar, computed exactly, and it is
> ## far lower than this campaign has ever assumed.

---

## 0. B1, and it passed to the cent

The vectorised open-to-open engine was checked against a real object before any ceiling was issued:

| | |
|---|---|
| vectorised MTM on P1/PCT's realised position | **$333,730.8400** |
| the same object's committed trade list | **$333,730.8400** |
| difference | **0.000000 — PASS** |

Also corrected at run time: the quote profile has no 17:00–17:59 minutes (CME break) but the **bar**
file carries one bar stamped 17:00 in 1,136 of 1,187 sessions — the session's own last bar. It is
forward-filled from 16:59 and the count is printed (0.070 % of bars) rather than allowed to become
a silent NaN. W99's first run stopped on this rather than proceeding; that is the check working.

---

## 1. ⚠️ `CORRECTION` — W99's own preregistered denominator failed, and it is instructive

The spec fixed a family of 12 simple causal rules in advance and called the best of them "a
genuinely executable LOWER bound on causal opportunity". Run as specified — always-in, sign flips
on every bar — **all twelve lose money, catastrophically**:

| | MOM5 | MOM15 | MOM30 | MOM60 | VWAPMOM | OPENMOM | ORB |
|---|---|---|---|---|---|---|---|
| $/session | −5,540 | −3,214 | −2,305 | −1,440 | −809 | **−704** | −706 |

**0 of 12 positive.** The best of them loses $704/session, so the "capture %" the spec asked for
divided by a negative number and printed nonsense. The cause is turnover, not the market.

> `FACT`, and it is worth more than the ceiling it was supposed to produce: **an always-in causal
> rule on 1-minute NQ is destroyed by friction.** This is the quantitative justification for why
> this campaign's engines are latched, throttled and hysteretic rather than simple.

### The repair (W99b): bound the turnover

Same 12 rules, **at most one entry per segment, held to the segment's close**:

| | MOM15 | MOM30 | VWAPMOM | MOM5 | MOM60 | OPENMOM | ORB |
|---|---|---|---|---|---|---|---|
| $/session | +8 | **+71** | +62 | −72 | −35 | −451 | −518 |
| hit rate | 49.7 % | 50.0 % | 50.1 % | 49.6 % | 49.3 % | 48.2 % | 47.5 % |

**3 of 12 turn positive purely by removing turnover.** Note the hit rates: the three winners sit at
**exactly a coin flip**. They do not win by being right more often; they win because the winners are
larger than the losers. And +$71/session is the *best of twelve* — it is not an edge, it is a
selection artifact of a size consistent with noise.

---

## 2. ⭐ `FACT` — SIGN_ORACLE and p\*, the instrument that replaces the broken denominator

One entry at each segment's open, one exit at its close, with the segment's **true** direction.
Perfect direction forecasting at segment resolution, with realistic turnover. Its exact analytic
companion is the direction accuracy at which that trade breaks even:

$$p^* = \tfrac12\left(1 + \frac{\text{cost}}{\mathbb{E}|\text{net move}|}\right)$$

| segment | mins | E\|move\| pt | cost $/RT | SIGN_ORACLE $/session | **p\*** | our $ | in-market | **lag half-life** |
|---|---|---|---|---|---|---|---|---|
| ON_ASIA | 360 | 52.92 | 29.34 | 1,026 | 0.5139 | 58 | 12.4 % | **120 m** |
| **ON_EU** | 480 | 62.39 | 19.36 | **1,224** | 0.5078 | **39** | 18.6 % | **120 m** |
| PRE | 90 | 45.38 | 19.36 | 886 | 0.5107 | 51 | 16.0 % | 30 m |
| OPEN | 15 | 45.51 | 19.36 | 887 | 0.5106 | 34 | 20.8 % | **5 m** |
| **MORN** | 105 | **88.54** | 16.86 | **1,744** | **0.5048** | **34** | 19.6 % | 30 m |
| MID | 120 | 60.89 | 14.36 | 1,197 | 0.5059 | 49 | 18.4 % | 30 m |
| **AFT** | 135 | 61.73 | 14.36 | **1,170** | 0.5058 | **9** | 18.0 % | 60 m |
| CLOSE | 15 | 27.61 | 14.36 | 515 | 0.5130 | 3 | 16.0 % | 5 m |
| POST | 120 | 29.32 | 16.86 | 545 | 0.5144 | 3 | 4.1 % | 15 m |

**Read the p\* column first.** Nothing on NQ at segment resolution requires better than a **51.4 %**
direction call, and the morning requires **50.48 %**. The campaign has spent ninety-nine waves
building objects far more elaborate than "call the direction of the next 105 minutes once".

`ASSUMPTION`, stated because it is load-bearing: p\* assumes the size of the move is independent of
whether the call was right. A forecaster that is systematically right on *small* moves and wrong on
*large* ones faces a higher real bar. p\* is a floor on the requirement, not a promise.

---

## 3. `FACT` — the ranked missing-opportunity table (directive §6)

### By segment — residual = SIGN_ORACLE − ours

| rank | segment | available | ours | **residual** | p\* | lag half-life | data |
|---|---|---|---|---|---|---|---|
| 1 | **MORN** 09:45–11:29 | $1,744 | $34 | **$1,710** | **0.5048** | 30 m | ✔ |
| 2 | **ON_EU** 00:00–07:59 | $1,224 | $39 | **$1,185** | 0.5078 | **120 m** | ✔ |
| 3 | **AFT** 13:30–15:44 | $1,170 | $9 | **$1,160** | 0.5058 | 60 m | ✔ |
| 4 | MID 11:30–13:29 | $1,197 | $49 | $1,148 | 0.5059 | 30 m | ✔ |
| 5 | ON_ASIA 18:00–23:59 | $1,026 | $58 | $968 | 0.5139 | 120 m | ✔ |
| 6 | OPEN 09:30–09:44 | $887 | $34 | $853 | 0.5106 | **5 m** | ✔ |
| 7 | PRE 08:00–09:29 | $886 | $51 | $834 | 0.5107 | 30 m | ✔ |
| 8 | POST | $545 | $3 | $543 | 0.5144 | 15 m | ✔ |
| 9 | CLOSE | $515 | $3 | $512 | 0.5130 | 5 m | ✔ |

> **ON_EU is the most forgiving target in the whole table** — 120-minute recognition half-life,
> p\* = 0.5078, $1,185/session unclaimed, and we are in-market 18.6 % of it while taking $39.
> **OPEN and CLOSE are the least forgiving** — the entire move is gone in five minutes.

### ⭐ By session class — and this inverts an assumption the campaign has carried for fifty waves

| class | share | **E\|move\| pt** | SIGN_ORACLE $ | p\* | **ours** | residual |
|---|---|---|---|---|---|---|
| TREND-UP | 21.0 % | 49.72 | $8,610 | 0.5092 | **+$1,991** | $6,619 |
| **TREND-DOWN** | 14.5 % | **63.71** | **$11,115** | 0.5072 | **−$495** | **$11,609** |
| REVERSAL | 25.7 % | 52.07 | $9,096 | 0.5088 | −$64 | $9,160 |
| RANGE | 26.8 % | 50.28 | $8,765 | 0.5091 | −$217 | $8,982 |
| MIXED | 12.0 % | 52.76 | $9,063 | 0.5087 | +$69 | $8,994 |

> ### **The days we lose money on move MORE than the days we make money on.**
> TREND-DOWN carries **63.71 points** of segment-level movement per session against TREND-UP's
> **49.72** — 28 % more — and it is the one class where our object is negative. The campaign's
> standing story is that P1 is "an upward-persistence specialist"; that is true, but the corollary
> everyone has drawn from it — *the other days are where the money isn't* — is **false**. The other
> days are where the money is, and TREND-DOWN is the single largest untaken block in this repo:
> **$11,609 per session of that class, on 14.5 % of sessions, at a break-even accuracy of 50.72 %.**

---

## 4. `FACT` — what recognition lag costs

The same best swing, entered *h* minutes after its true start:

| segment | +0 m | +5 m | +15 m | +30 m | +60 m | +120 m | half-life |
|---|---|---|---|---|---|---|---|
| ON_ASIA | 95.0 | 81.6 | 73.1 | 64.3 | 52.4 | 33.3 | **120 m** |
| ON_EU | 125.1 | 114.7 | 106.2 | 96.8 | 84.0 | 61.0 | **120 m** |
| PRE | 80.6 | 61.7 | 45.6 | 27.3 | 7.0 | 0.0 | 30 m |
| **OPEN** | 73.8 | 25.7 | **0.0** | 0.0 | 0.0 | 0.0 | **5 m** |
| MORN | 159.3 | 123.5 | 94.1 | 64.9 | 26.3 | 0.0 | 30 m |
| MID | 114.5 | 91.7 | 73.6 | 54.9 | 28.9 | 0.0 | 30 m |
| AFT | 116.5 | 95.1 | 77.2 | 60.7 | 33.3 | 2.9 | 60 m |
| **CLOSE** | 42.5 | 17.2 | **0.0** | 0.0 | 0.0 | 0.0 | **5 m** |
| POST | 46.0 | 26.3 | 16.3 | 7.3 | 0.0 | 0.0 | 15 m |

This is a **recognition-lag** ceiling, not an information ceiling: it says how much is left once you
would plausibly have identified the move, and nothing about whether it was identifiable.

> Design consequence, and it is concrete: **an engine aimed at OPEN or CLOSE must decide within a
> couple of minutes or it has nothing to trade. An engine aimed at ON_EU can take an hour and keep
> two thirds of the move.** That is the opposite of where a 1-minute-bar system naturally wants to
> live, and it is the strongest argument yet found in this campaign for an overnight sleeve — a
> better one than W96's "different clock", which W97 falsified.

---

## 5. ⚠️ `WITHDRAWN` — the "value of a router", and a control of mine that was mis-specified

W99 reported ORACLE-OVER-FAMILY = **$13,981/session** and called the gap to the best fixed rule
"the value of a perfect router". Both are withdrawn.

| | $/session |
|---|---|
| one-shot best-of-12 chosen per group, **ex post** | $9,239 |
| a **random** rule choice per group (mean over the 12) | **−$213** |
| a **causal** router — best trailing record in that segment, K = 10 / 20 / 40 / 80 | **−$22 / −$193 / −$128 / −$195** |
| the single best fixed rule (MOM30) | +$71 |

> **The causal router loses money at every K and never beats the best fixed rule.** The entire
> $9,452 gap is a max over twelve series. **Routing over simple causal rules is worth nothing**,
> which is direct support for directive §12's ordering: build real engines first, and only then a
> router over *them*.

`CORRECTION` My first attempt at a control for this permuted **each rule's outcomes across groups
independently**. That destroys the correlation between rules, and a max over 12 independent series
is far larger than a max over 12 correlated ones — so the null came back **above** the real value
($23,325 vs $9,239) and reported an "excess" of −152 %. The control was inflating the null, not
measuring the statistic. A common permutation is degenerate for a sum. There is no useful null for
an ex-post max; the statistic is the wrong instrument and was withdrawn rather than repaired.

---

## 6. Why we miss it — and the caveat that has to travel with it

| code | groups | share | missed $/session |
|---|---|---|---|
| **NO_ENGINE** | 2,655 | **79.0 %** | 2,446 |
| OTHER | 369 | 11.0 % | 394 |
| WRONG_DIRECTION | 119 | 3.5 % | 131 |
| SESSION_BOX | 89 | 2.6 % | 125 |
| EXIT_EARLY | 70 | 2.1 % | 59 |
| ENTRY_LATE | 60 | 1.8 % | 86 |

**In 79 % of the groups where a simple causal rule made money, we had zero exposure at all.** The
flaws in the engine we have — bad direction, the box, early exits, late entries — account for
**10 %** of the deficient groups between them.

⚠️ The **dollar** column is selection-inflated: groups enter the table only when the reference rule
was *positive* there, so $2,446/session is what a positively-selected rule would have made where we
were flat, not a forecast. **The 79 % share is the durable finding; the dollars are not.**

---

## 7. Recency (directive §3) — opportunity is up and our capture is down

| window | sessions | ex-post oracle1 pt/session | P1/ABS | **P1/PCT** | 2:3/PCT |
|---|---|---|---|---|---|
| FULL | 1,058 | 841.7 | $231 | **$280** | $234 |
| 2024+ | 670 | 960.6 | $316 | $369 | $286 |
| 2025 | 259 | 976.7 | $433 | $421 | $227 |
| 2026 YTD | 152 | 1,331.2 | $57 | $250 | $251 |
| t12m | 261 | 1,134.6 | $150 | $247 | $263 |
| t6m ⚠️ | 131 | 1,391.1 | −$80 | $109 | $238 |
| t3m ⚠️ | 67 | **1,541.0** | −$248 | −$67 | $133 |

⚠️ t3m lies **entirely** inside the BURNED span 2026-05-31 → 07-31; t6m largely does.

> **Ex-post movement per session has risen 83 % (841.7 → 1,541.0 points) while P1's production has
> gone negative.** The owner's premise — that the market contains far more than we monetise, and
> increasingly so — is **confirmed on our own data**. The pair degrades far more gracefully
> ($234 → $133) than P1 does ($280 → −$67), and P1/PCT beats P1/ABS in **every** recency window,
> which is independent support for W98.

---

## 8. What this ledger says to do next

Ranked by (residual × frequency) ÷ (difficulty implied by p\* and lag half-life), restricted to
things testable with data already on disk:

1. **TREND-DOWN / bear persistence.** $11,609 per session of that class, 14.5 % of sessions, the
   **largest** per-session movement of any class, p\* = 0.5072, and we are *negative* there.
   Nothing else in the table is close.
2. **MORN (09:45–11:29).** $1,710/session unclaimed at the lowest p\* in the table (0.5048), with a
   30-minute recognition half-life. We are in-market 19.6 % of it and take $34.
3. **ON_EU (00:00–07:59).** $1,185/session at a **120-minute** half-life — by far the most forgiving
   entry timing available. Requires genuinely new overnight *information*, not a different clock
   (W97 falsified that rationale).
4. **AFT (13:30–15:44).** $1,160/session, 60-minute half-life, and we take **$9** — the lowest
   capture ratio of any segment (0.5 %).

Explicitly **not** on this list: a meta-router (measured worthless over simple rules, §5), and
anything aimed at OPEN or CLOSE (5-minute half-life makes them the hardest squares on the board for
a 1-minute-bar system, not the easiest).

Nothing is promoted here. This is the agenda, and it is now denominated in something a person can
actually trade against.
