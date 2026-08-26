# WHAT P1 ACTUALLY DELIVERS — the honest decision table

Written 2026-08-26, after W76 corrected the substrate truncation. **Every figure here is on the
corrected, extended window** (2022-07-04 → 2026-07-31, 213 weeks) and is net of $4.36/RT
commission. The C1 stress line is quoted separately because it changes the answer materially.

This document exists because the owner asked a direct question — *"别人今年都十几二十万"* — and
the campaign's own reporting had been answering it with a number computed on a window that
stopped two months early.

---

## 1. P1 alone, per 1 unit (≈ 1.27 NQ contracts)

| period | weeks | weekly $ | median week | positive weeks | longest losing streak | max DD | worst week | **annualised** |
|---|---|---|---|---|---|---|---|---|
| **FULL 2022-07 → 2026-07** | 213 | $1,315 | $279 | 56.3 % | 8 | $24,225 | −$7,418 | **$68,389** |
| **TRAILING 12 MONTHS** | 53 | $879 | $81 | 50.9 % | 6 | $24,225 | −$6,344 | **$45,709** |
| **2026 YTD** | 31 | $412 | $189 | 51.6 % | 6 | $24,225 | −$6,344 | **$21,439** |
| held-out Jun–Jul 2026 | 9 | −$2,298 | −$2,855 | 11.1 % | 6 | $18,341 | −$5,015 | −$119,522 |

The trend across the first three rows is the thing to look at: **$68k → $46k → $21k annualised as
the window moves toward the present, against a maximum drawdown that does not fall at all.**

## 2. What $150,000 a year would cost

| at this period's realised rate | units needed | **NQ contracts** | **implied max drawdown** | implied worst week |
|---|---|---|---|---|
| full-window rate | 2.19 | **2.8** | **$53,133** | −$16,270 |
| trailing-12-month rate | 3.28 | **4.2** | **$79,496** | −$20,819 |
| **2026 YTD rate** | 7.00 | **8.9** | **$169,492** | **−$44,389** |

Read the last row plainly: **at the rate the object has actually produced in 2026, earning
$150,000 a year requires accepting a $169,492 drawdown — a drawdown larger than the annual
profit.** That is not an investable configuration.

The middle row is the honest one to plan against, because a trailing year is the shortest window
that contains more than one regime: **$150k/year at ≈4.2 NQ contracts with a ~$79,500 drawdown,
i.e. MAR ≈ 1.9.**

## 3. The friction line that must travel with all of it

The C1 stress line ($10/RT of slippage on top of commission) costs **≈ $94/week per unit**:

- **6–7 %** of the full-window rate
- **11 %** of the trailing-12-month rate
- **23 %** of the 2026 rate

At 2026's rate, slippage alone consumes almost a quarter of the gross.

## 4. What has to be true for the top row to be the right one

The full-window row ($68k/unit/year, MAR 2.8) is the flattering one and it is **not** a forecast.
It assumes the 2024–2025 regime returns. The campaign's own evidence says to discount it:

- **W72**: eleven independently-constructed intraday directional gates are all flat-or-negative
  over 2006–2021 and all positive over 2022–2026, and all sit at the 85th–98th percentile of
  their own histories. Half of P1's net rests on that class of signal.
- **W76**: the first genuinely held-out window this campaign has ever read produced
  −22.49 pts/session at t = −2.74, broadly (median traded day −$1,447, 19.6 % positive days), in
  a market that fell 8.1 % with double the TREND-DOWN share.
- **W50**: the object earns +88.68 pts/session on TREND-UP days and loses 21.89 on TREND-DOWN
  days. It is a directional bet on the regime and always was.

## 5. What cannot be fixed by sizing

**The positive-week rate is scale-invariant.** Contracts move money and drawdown together and
leave the hit rate exactly where it is. So:

| | where we are | the campaign's binding target | reachable by size? |
|---|---|---|---|
| weekly $ at his tail tolerance (−$42,235) | ≈$8,398 net | $8,583 **gross** | **already there** |
| positive-week rate | **56.3 %** (2026: 51.6 %) | **76 %** | **never** |

**W74** measured what the hit rate does require: **six genuinely independent streams** at our
current quality (ten at ρ = 0.1; unreachable at ρ ≥ 0.2). **W75 + W79** counted what we have:
**one.** Every clock sleeve, member-set variant and channel arm is 0.30–0.89 correlated with P1
and cannot contribute; the three candidates that were decorrelated (SHORT, AXISB, S_sig) all
fail the 2025-and-2026 recency gate on corrected data.

## 6. The honest summary

- P1 is a **real** edge — 89 % of its net is timing, not market drift (W73), it beats its own
  circular-shift null at the 100th percentile, and it survived an independent NinjaScript
  reproduction at 0.64 % (W52).
- It is a **single directional stream** whose profitability tracks a regime that has been
  favourable since 2022 and turned against it in June–July 2026.
- At the trailing-year rate it can produce **$150k on ~4 contracts with a ~$80k drawdown**. At
  2026's rate it cannot produce that at any acceptable drawdown.
- **Every remaining improvement the repo has tested inside this object has failed** (W72, W74,
  W77, W78, W79 — six consecutive full-sample winners that did not survive sub-period testing).
- The one thing that would change the picture is **more independent streams**, and the binding
  constraint on those is **information**: this repository holds one instrument at one resolution
  (NQ 1-minute, 2006–2026) plus 48 sessions of 1-second data. That is the ceiling, and it is not
  a cleverness problem.

## 7. Files
Computed from `runs/WE_W76_FORWARD2026/out/streams_extended.csv`.
Supporting: `runs/WE_W74_WEEKMATH/REPORT.md`, `runs/WE_W75_STREAMCENSUS/REPORT.md` (+ amendment 1),
`runs/WE_W76_FORWARD2026/REPORT.md`, `runs/WE_W78_PAIR/REPORT.md`, `runs/WE_W79_CLIQUE/REPORT.md`.
