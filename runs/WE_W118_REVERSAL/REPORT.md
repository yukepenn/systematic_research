# WE_W118 — the reversal session, at the mechanism's own geometry · REPORT

Preregistered (`spec.yaml`, committed at `3ea0398` before any code was written).
POST-W115 owner directive §§6, 26, 27, 29, 38, 40, 44 LANE 4. Raised by W117.

> ## **FAILS all three preregistered conditions, and the third is the one that matters: at the EXACT entry bars the reversal rule produces, trading the PREVAILING move instead earns +$374/trade while the reversal earns −$405.** A delta of **$778 per trade**, and always-long / always-short at those same bars earn **−$9 and −$22**, so this is not drift.
> ## Per the decision rule fixed in advance, that **closes the CLASS, not just the clock** — this is an event-driven geometry with endogenous entries spread across 10:00–12:00, not W108's fixed midday clock.
> ## ⭐ **And the §6 diagnostic is the most valuable thing here: in 2006–2021 BOTH reversal and momentum are ≈ZERO at this geometry** (−$31 vs −$1). A third independent confirmation, from a completely different construction, that **intraday continuation is a modern-regime phenomenon that did not exist in the old era.**

## 1. ⚠️ The first run did not test the stated mechanism — defect and repair

**Median entry 09:32. Firing on 99.4 % of sessions.** At bar 572 the running excursion is a couple of
points, so a 25 % retracement of it triggers instantly. The wave was measuring *"fade the first
wiggle after the open and hold to 15:44"*, which is a different object entirely.

**Cause, and it is mine:** the spec required an excursion gate and said explicitly it exists because
*"without it the rule fires on noise excursions of a few points."* I applied that gate to each
session's **12:00** excursion, *after the fact* — which never constrained **when** the trigger could
fire. **The gate belongs at the trigger bar.**

**Repair (faithful to the spec, not a re-choice):** the running excursion `E` must exceed a
threshold built from the **prior 250 sessions** before any retracement can trigger. Entry time then
becomes endogenous and late, which *is* the mechanism. The defective output is preserved at
`out/reversal_DEFECTIVE_gate_at_1200.txt` and `out/grid_DEFECTIVE.csv`.

| | before repair | **after repair** |
|---|---|---|
| fire rate (R=0.50) | 97.2 % | **32.9 %** |
| median entry | 09:33 | **10:44** |
| p25 / p75 entry | 09:32 / 09:35 | **10:11 / 11:35** |

## 2. Fire rates and entry times — now genuinely event-driven

| retracement | sessions firing | rate | median entry | p25 | p75 | short / long |
|---|---|---|---|---|---|---|
| 0.25 | 476 | 44.9 % | 10:24 | 10:03 | 11:02 | 216 / 260 |
| 0.50 | 348 | 32.9 % | 10:44 | 10:11 | 11:35 | 154 / 194 |
| 0.75 | 226 | 21.3 % | 11:03 | 10:20 | 12:04 | 109 / 117 |

Median 12:00 excursion 140.5 points, so the gate is binding and the rule is waiting for a real move.
Entries are roughly balanced long/short.

## 3. Economics — every cell negative, every mirror positive

| cell | N | hit % | p\* | **$/trade** | net $ | **MOMENTUM same bars** | **delta** | coin p95 |
|---|---|---|---|---|---|---|---|---|
| R=0.25 gate 0.25 | 243 | 45.7 % | 0.5027 | −$485 | −$117,959 | **+$454** | −$940 | $435 |
| R=0.25 gate 0.50 | 472 | 42.8 % | 0.5030 | −$426 | −$201,200 | +$394 | −$821 | $293 |
| R=0.25 gate 0.75 | 713 | 42.9 % | 0.5032 | −$385 | −$274,431 | +$352 | −$737 | $220 |
| R=0.50 gate 0.25 | 148 | 45.9 % | 0.5026 | −$437 | −$64,673 | +$407 | −$844 | $640 |
| R=0.50 gate 0.50 | 347 | 44.1 % | 0.5028 | −$438 | −$151,948 | +$407 | −$845 | $339 |
| R=0.50 gate 0.75 | 568 | 44.9 % | 0.5031 | −$337 | −$191,359 | +$305 | −$642 | $253 |
| R=0.75 gate 0.25 | 84 | 54.8 % | 0.5025 | −$355 | −$29,861 | +$326 | −$681 | $953 |
| R=0.75 gate 0.50 | 225 | 48.9 % | 0.5027 | −$350 | −$78,814 | +$320 | −$670 | $464 |
| R=0.75 gate 0.75 | 399 | 48.6 % | 0.5030 | −$267 | −$106,510 | +$236 | −$502 | $299 |

**PRIMARY** (mean across the three retracement levels at gate 0.50):

| | |
|---|---|
| REAL reversal | **−$405/trade** |
| **MOMENTUM at the same bars** | **+$374/trade** — delta **−$778** |
| coin null (shared per-session sign) | mean −$15, **p95 $373** → **4.0th percentile** |
| conditions | positive ❌ · beats coin ❌ · **BEATS MOMENTUM ❌** |
| **VERDICT** | **FAILS** |

**And it is not drift.** At the same entry bars: **always-long −$9, always-short −$22.** The
momentum mirror's +$374 comes from *continuation*, not from the market's direction.

## 4. It also fails its own naming test, and does not fill the book's hole

| cell, gate 0.50 | TREND-UP | TREND-DOWN | **REVERSAL** | RANGE | MIXED |
|---|---|---|---|---|---|
| R=0.25 | −$1,528 | −$1,859 | **−$134** | +$592 | +$807 |
| R=0.50 | −$2,088 | −$1,506 | **−$216** | +$311 | +$625 |
| R=0.75 | −$2,609 | −$686 | **+$233** | +$139 | +$283 |

> The spec fixed in advance that *"a reversal mechanism not positive on REVERSAL sessions has
> falsified its own name."* At two of three levels it is **negative on REVERSAL sessions.**
> ⚠️ The rest of this table carries little information: **W111b established that the
> −TREND / +RANGE signature is definitional for any rule trading against the prevailing move.**
> The REVERSAL column is the only one the spec relied on, and it is ≈0.

**On the book's losing weeks** — the reason the wave exists: −$145, −$670, −$242 per week.
⚠️ R=0.25 sits at the 96.2nd percentile of its circular-shift null **while still being negative** —
"less bad than a random alignment" is not a pass, and must not be read as one.

## 5. ⭐ The §6 diagnostic — and it is the wave's most valuable output

**2006–2021, DIAGNOSTIC ONLY. Explicitly NOT a promotion veto (§5).**

| cell | N | hit % | reversal $/trade | **MOMENTUM $/trade** | delta |
|---|---|---|---|---|---|
| R=0.25 gate 0.50 | 1,939 | 47.9 % | −$31 | **−$1** | −$30 |
| R=0.50 gate 0.50 | 1,394 | 49.6 % | −$17 | **−$14** | −$2 |
| R=0.75 gate 0.50 | 965 | 48.7 % | −$28 | **−$2** | −$26 |

> ### In the old era **NEITHER side has an edge.** Reversal ≈ −$25, momentum ≈ −$6, delta ≈ −$20. In the modern era the same construction gives reversal −$405 and momentum **+$374**, a delta of **$778**.
> ### **This is the third independent confirmation that intraday continuation is a MODERN-REGIME phenomenon.** W114 found it at a fixed 11:49 clock. W111b found it as an unconditional control. W118 now finds it at an **event-driven geometry with endogenous entries spread across 10:00–12:00** — a completely different construction — and finds it absent in 2006–2021 at that geometry too.
> ### It materially strengthens the `FOLLOW_MORNING` regime story: **the effect is not an artifact of one clock.**

## 6. Decision

**NOTHING PROMOTED.**

1. **Per the preregistered decision rule, this closes the CLASS rather than the clock.** The exact
   wording, fixed before the run: *"If the mechanism fails to beat MOMENTUM_AT_SAME_BARS, the
   conclusion is that intraday momentum dominates reversal at EVERY geometry tested so far, not
   merely at W108's clock."* It failed by $778/trade.
   > **The defensible statement, stated at its true strength and no further:** at *every* geometry
   > this campaign has tested — a fixed midday clock (seven mechanisms, W108/W111) and now an
   > endogenous excursion-triggered entry (three depths × three gates, W118) — **momentum beats
   > reversal by $500–$1,100 per trade in the modern era, and both are flat in the old era.** That
   > is much stronger than the seven prior kills. It is still not "mean reversion is impossible on
   > NQ": one construction family was tested here, thoroughly.
2. **W117's named gap is NOT filled.** The book still loses when TREND-UP sessions are scarce and
   REVERSAL sessions are abundant, and nothing owned or built is positive on those weeks. **The gap
   is now better characterised AND harder** — the obvious mechanism for it has been tested at its
   own geometry and it is on the wrong side of a live momentum effect, just as the seven fades were.
3. **`REVERSAL` moves from PARKED to CLOSED-at-two-geometries** in the coverage matrix, with the
   quantifier attached. Reopening requires **new information**, not a new clock or a new retracement
   depth — §26's parked list and §39's wave budget both bind here.
4. **A methodological note that is now binding**: a high null percentile on a **negative** real value
   is not a pass. R=0.25's 96.2nd percentile on book-losing weeks is "less bad than random", and
   reporting that as a survivor would have been a live error.
