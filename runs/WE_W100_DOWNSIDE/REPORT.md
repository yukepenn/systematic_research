# WE_W100 — TRACK A, DOWNSIDE PERSISTENCE · REPORT

Preregistered (`spec.yaml`, committed at `82b9d6d` before any result was read). Target chosen from
W99's ranked table. Owner directive V4 §7 TRACK A / TASK 8.

> ## **BOTH PREREGISTERED HYPOTHESES ARE FALSIFIED.**
> ## And the reason is partly my own design: **both filters turned out nearly non-binding on the
> ## leg they were aimed at** — 93.1 % and 92.0 % acceptance. A filter that keeps 92 % of the
> ## trades cannot separate much, and I fixed the constants without first checking their rate.

---

## 1. The battery — SHORT leg (the target)

B-MOM's own short leg, traded alone, size 1, per-contract box. Primary is **mean $ per contract
round turn**, the only statistic a filter cannot flatter by changing exposure. Each treatment
carries **200 random filters accepting exactly the same number of triggers**.

| arm | accept % | trades | **$/ctrRT** | net $ | wk$ @ fixed DD | wk + % | **null p95** | **percentile** |
|---|---|---|---|---|---|---|---|---|
| BASE | 100.0 % | 692 | **85.71** | $59,310 | $109 | 46.5 % | — | — |
| **F_VOL** | 93.1 % | 652 | **63.32** | $41,287 | $71 | 44.1 % | 148.02 | **25.5th** |
| **F_SEMI** | 92.0 % | 673 | **116.07** | $78,113 | $121 | 47.9 % | 145.61 | **77.5th** |
| F_BOTH | 85.8 % | 629 | 72.85 | $45,820 | $76 | 45.5 % | 184.03 | 35.0th |

| falsifier | result |
|---|---|
| **H1 volume** — `relvol ≥ 1.0` | **FALSIFIED.** $63.32 vs a base of $85.71 — it makes the book *worse* — and sits at the **25.5th percentile** of rate-matched random filters. |
| **H2 semivariance** — `rsv_share ≥ trailing-250-session median` | **FALSIFIED.** $116.07 is a real-looking +35 % lift on the base, and it is at the **77.5th percentile** of random filters at the same acceptance rate. A random filter that drops 8 % of trades does this a quarter of the time. |

> `FACT` **Neither axis separates a good downside continuation from a bad one on this schedule.**
> The +35 % that `F_SEMI` appears to add is indistinguishable from dropping 8 % of trades at random.

## 2. ⚠️ `CORRECTION` to my own preregistered test — H3 passed its letter and is uninformative

The spec's H3 said: if `F_SEMI` improves the short leg more than the long leg, the information is
downside-specific; if it improves both equally it is a volatility filter in costume. It "passed":

| | accept % | trades | $/ctrRT | vs base |
|---|---|---|---|---|
| SHORT base | — | 692 | 85.71 | — |
| SHORT F_SEMI | **92.0 %** | 673 | 116.07 | **+$30.36** |
| LONG base | — | 677 | 180.50 | — |
| LONG F_SEMI | **3.5 %** | **26** | −1,247.63 | **−$1,428.13** |

> **The two arms are not comparable and the test cannot mean what it was written to mean.**
> `rsv_share ≥ its median` accepts **92 % of short triggers and 3.5 % of long triggers**. It is not
> a filter that happens to favour shorts — it is **nearly collinear with the channel's own
> direction**, which in hindsight is obvious: when price is falling enough to trigger a short, the
> last 30 bars' downside semivariance is of course above its median.
>
> A 26-trade arm cannot be set against a 673-trade arm. **H3 is recorded as VOID, not SUPPORTED.**
> The generalisable lesson: *any* "downside-volatility-share" gate applied to a directional channel
> is largely a restatement of the direction, and must be rate-matched across legs before it means
> anything.

## 3. One control arm fired — and it is `WEAK`, not a finding

| | accept % | trades | $/ctrRT | null p95 | Bonferroni p99.17 | percentile |
|---|---|---|---|---|---|---|
| **LONG F_VOL** | 89.8 % | 614 | **260.38** | 249.97 | **265.69** | **98.5th** |

`relvol ≥ 1.0` on the **long** leg clears its 95th-percentile bar and **does not clear the
Bonferroni bar for the family of six tests**. Per the decision rule fixed in advance that is
**WEAK**, and it was a *control*, not a hypothesis — I ran six tests and one landed at the 98.5th,
which is roughly what six tests do. **Not pursued without a fresh preregistration.**

It is, however, the one direction in which the volume column is not yet dead: high-participation
*upside* continuations. Noted in the coverage matrix as WEAK, not as SUPPORTED.

## 4. `FACT` — where the short book's money actually is, and it is not subtle

Mean $/ctrRT by session class, SHORT leg:

| class | share | BASE | F_VOL | F_SEMI | F_BOTH |
|---|---|---|---|---|---|
| TREND-UP | 21.0 % | **−2,163** | −2,159 | −2,188 | −2,185 |
| **TREND-DOWN** | 14.5 % | **+3,111** | +3,195 | +3,102 | +3,213 |
| REVERSAL | 25.7 % | −243 | −254 | **−58** | −159 |
| RANGE | 26.8 % | −597 | −576 | −622 | −595 |
| MIXED | 12.0 % | −460 | −563 | −460 | −563 |

> **The entire short book is one question asked 1,058 times: is today a down day?** +$3,111/ctrRT
> when it is, −$2,163 when it is not. Neither of the two filters moves any class by more than a few
> per cent — they are not touching the variable that matters.
>
> This is the same question W99 priced: **a direction call on TREND-DOWN breaks even at 50.72 %.**
> The problem is not the trigger, the exit, the sizing or the box. It is that we have no causal
> statement about the day's direction, and the two cheapest candidate sources for one have now been
> tested and did not provide it *in this form*.

## 5. Recency — the short leg has gone negative

| window | BASE | F_VOL | F_SEMI | F_BOTH |
|---|---|---|---|---|
| FULL | 85.71 | 63.32 | 116.07 | 72.85 |
| 2024+ | 87.52 | 63.96 | 128.14 | 71.27 |
| 2025 | **237.76** | 279.05 | 305.14 | 259.62 |
| t12m | 261.99 | 233.44 | 261.71 | 234.36 |
| 2026 YTD | **−51.87** | −152.13 | −80.14 | −191.14 |
| t6m ⚠️ BURNED | **−59.74** | −180.67 | −69.16 | −199.95 |

Every filter makes 2026 **worse**, not better.

## 6. `FINDING` — a data hole, found by a harness check that was looking for something else

B1 compared `we_channels`' vectorised reconstruction of B-MOM against the engine's own cached array
and returned **99.9775 %** on the extended substrate, against the **99.992 %** W72 recorded on the
shorter one. 365 divergent bars across 34 of 1,187 sessions, and **238 of them in one session**:

> **2026-07-17 is a truncated session in the extended substrate — it ends at 10:53 with 83 RTH bars
> against a normal 390.** It is a data hole, not a channel defect, and it lies inside the BURNED
> span. Recorded because **X9a is built by the same module and inherits the same path**, and
> because every wave since W76 uses `extend=True`.

This wave sidestepped it by using the engine's own cached array as the base rather than a
reconstruction. B1b (`gfills_fast` == `gfills`, byte for byte, on both legs) **PASS**.

## 7. What is now closed, and what is precisely NOT closed

**Closed** — record in the coverage matrix as **TESTED-NULL**:
- `relvol ≥ 1.0` as an acceptance gate on B-MOM's short-leg triggers.
- `rsv_share ≥ trailing-250-session median` as an acceptance gate on the same.

**NOT closed** — the quantifier matters and this wave tested a narrow one:
- Volume as a **signal** (this tested it as a near-non-binding *gate* at one threshold).
- Volume in any of the forms the vendor corpus and `intraday_system` actually propose — monotone
  volume **decay** across a run, effort-without-result, volume **spikes** at extremes. None of
  those is `relvol ≥ 1.0`.
- Semivariance as a **threshold scale** inside the channel (the original card 20/7 proposal:
  σ_down for short legs, σ_up for long legs). This wave tested it as a *gate*, which is a
  different object.
- Any **rate-matched** version of either. Both filters here accepted ~92 % of the target leg.

## 8. Decision

Nothing promoted. Nothing to promote. The wave did what a well-designed negative is supposed to do:
it spent one afternoon to remove the top two entries from a twelve-row frontier, and it produced
two facts worth more than the hypotheses did —

1. **The short book is a single unanswered question about daily direction** (+$3,111 vs −$2,163
   per contract RT), and no gate on the trigger touches it.
2. **A downside-volatility gate on a directional channel is mostly a restatement of the direction**
   (92 % vs 3.5 % acceptance across the two legs), so every future gate of that shape must be
   rate-matched across legs before it is interpreted.

**Next**: the spec forbids adjusting a constant after seeing a result, so the rate-matched version
is a new wave with its thresholds fixed as **quantiles** — guaranteed binding, guaranteed
comparable across legs — and it tests the axes in the forms this one did not.
