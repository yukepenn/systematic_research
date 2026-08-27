# WE_W107 — LANE B, AFT · REPORT

Preregistered (`spec.yaml`, committed before any result was read). Owner amendment §6 LANE B.
`W107b` is an adversarial correction to **this wave's own headline**, run before it was reported.

> ## **W107's stage-2 PASS is WITHDRAWN. One of its two "survivors" survived on a FOUR-SESSION bin.**
> ## Corrected: one genuine survivor, `PATH_EFF`, at **$53/trade, 78.5th percentile — FAILS.**

## 1. Stage 1 — the diagnostic. Nine causal states known at 13:29, no trade simulated

Survivor rule fixed in the spec **before** the table was produced: top-vs-bottom quintile sign-rate
spread ≥ 8 pp **and** monotone or single-peaked. 1,012 eligible sessions.

| state | Q1 → Q5 sign rate | spread | shape | survives |
|---|---|---|---|---|
| MORNING_DIR | 49.5 → 75.0 → 57.3 % | 25.5 pp | single-peak | **YES ⚠️ SPURIOUS** |
| **PATH_EFF** | 46.8 → 52.0 → 53.5 → **59.9** → 56.2 % | **13.1 pp** | single-peak | **YES ✅** |
| VWAP_DIST | 52.2 → 49.0 → 51.0 → 55.9 → 60.1 % | 11.1 pp | irregular | no |
| OPEN_RANGE_ST | 49.7 → 48.0 → 60.0 % | 12.0 pp | irregular | no |
| MIDDAY_DIR | 50.0 → 33.3 → 56.8 % | 23.4 pp | irregular | no |
| VOL_REACCEL | — | 7.9 pp | irregular | no |
| VWAP_SIDE | 49.9 → 56.5 % | 6.6 pp | monotone | no |
| MID_RANGE_POS | — | 5.9 pp | irregular | no |
| COMPRESSION | — | 3.0 pp | irregular | no |

## 2. ⚠️ `CORRECTION` (W107b) — two defects, both mine

### (a) The survivor rule had no minimum bin size

`MORNING_DIR` is a discrete ±1 variable. The binner detected ≤ 3 unique values and used the levels
{−1, 0, +1} — and the middle level holds **four sessions**, whose 75.0 % sign rate produced *both*
the 25.5 pp spread *and* the "single-peak" shape.

| MORNING_DIR level | n | sign % | mean $ |
|---|---|---|---|
| down morning | 481 | 49.5 % | −$154 |
| *flat* | **4** | **75.0 %** | $1,384 |
| up morning | 527 | 57.3 % | $105 |

> **On the two real levels the spread is 7.8 pp — below the 8 pp bar.** `MORNING_DIR` should never
> have survived stage 1, and the 25.5 pp figure is **withdrawn**.

### (b) The rate calibrator cannot bin a discrete variable

`MORNING_DIR`'s 25 / 50 / 75 % arms returned **481 / 485 / 485** trades. **No calibration happened
at all** — the whole point of the outcome-blind procedure was defeated for that variable.

### `PATH_EFF` re-checked

| quintile | Q1 | Q2 | Q3 | Q4 | Q5 |
|---|---|---|---|---|---|
| n | 203 | 202 | 202 | 202 | 203 |
| sign % | 46.8 | 52.0 | 53.5 | **59.9** | 56.2 |
| mean $ | −$247 | $2 | $97 | $121 | −$36 |

Every bin n ≈ 202, spread 13.1 pp, single-peaked. **It is the only genuine stage-1 survivor.**

## 3. The control W107 owed and did not run

NQ rose over 2022–2026, so an unconditional directional tilt would masquerade as a mechanism.

| arm | N | hit % | p\* | **$/trade** | t |
|---|---|---|---|---|---|
| **ALWAYS LONG** 13:51 → 15:44 | 1,013 | 50.15 % | 0.5067 | **−$66** | −1.39 |
| **ALWAYS SHORT** | 1,013 | 48.86 % | 0.5067 | **+$37** | 0.79 |

> The afternoon carries a mild **short** tilt over this window. **Any future afternoon mechanism
> must be measured against that, not against zero** — a mechanism earning $37/trade has added
> nothing at all.

## 4. Corrected result

| | N | hit % | $/trade | wk$ @ fixed DD | t |
|---|---|---|---|---|---|
| PATH_EFF @ 0.25 | 241 | 52.70 % | $66 | $63 | 0.71 |
| **PATH_EFF @ 0.50 (the corrected primary)** | 502 | 52.99 % | **$53** | $89 | 0.69 |
| PATH_EFF @ 0.75 | 752 | 52.39 % | $70 | $138 | 1.15 |

**Single-cell coin null p95 $115 → 78.5th percentile. FAILS.** Best-of-3 bar $181 — not cleared.

> **W107's headline of $99/trade at the 98.5th percentile is WITHDRAWN.** It averaged `PATH_EFF`
> with a variable that should never have been a survivor. The corrected figure is $53/trade and it
> does not clear its own null.

## 5. Decision

**Nothing promoted. AFT — $1,166/session of `EX_POST_EXECUTION_FEASIBLE_ORACLE`, the lowest capture
ratio of any segment at 0.3 % — remains untouched.**

What the wave bought:

1. **Eight of nine** causal states known at 13:29 carry no separating structure for the afternoon
   move. The ninth, path efficiency, separates 13.1 pp but is not significant as a trade.
2. **The afternoon's unconditional tilt is now measured** (−$66 long / +$37 short per trade), so
   the next attempt starts from the right baseline instead of from zero.
3. A methodological fix that is binding on every future lane: **a quintile survivor rule needs a
   minimum bin size, and a discrete variable cannot be rate-calibrated by quantile.** Both are now
   in the shared harness.
