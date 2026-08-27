# Complementary return engines — status: NOT BUILT

_2026-08-07 · This report exists to record honestly that a required part of the campaign mandate
was **not completed**, and why. It contains no results, because none were produced._

## Status

The campaign mandate (§15) called for four independent return engines alongside the Solar
persistence family:

| family | mechanism | status |
|---|---|---|
| **A — Directional persistence (Solar)** | overshoot beyond a directional-change threshold | **COMPLETE** — see [`solar_family_finalists.md`](solar_family_finalists.md) |
| **B — Failed persistence / failed breakout** | earns when persistence fails | **NOT BUILT** |
| **C — Value reacceptance / VWAP** | return to value after failed extension | **NOT BUILT** |
| **D — Session / overnight inventory** | handoff and inventory-correction effects | **NOT BUILT** |
| **E — Other directional / auction mechanisms** | breakout, vol expansion, multi-session momentum | **NOT BUILT** |

Consequently [`portfolio.md`](portfolio.md) contains no portfolio: a portfolio of one family is
not a portfolio, and the router design in the mandate (§17) has nothing to route between.

**This is the largest single gap between the campaign mandate and what was delivered.** It is
recorded as a gap, not rationalised as a decision.

## Why it stopped here

Two reasons, of unequal weight.

**1. The binding one — the campaign hit its formal stop condition first.** Constitution §23(B)
fires when three consecutive properly designed waves fail to produce a robust Pareto improvement.
Wave 2's H-006 was downgraded to inconclusive by the red team; Wave 3's sleeves (C2, C4) and
wave-conditioning were all rejected; the red team's own follow-ups were all negative. The rule
fired before Family B was started. Continuing past a declared stop condition to open a new front
would have been a violation of the campaign's own governance, which exists precisely to stop
researchers from digging until they find something.

**2. The supporting one — DR-05 already argued the mechanism is weak here.** The deep-research
packet on failed persistence and value reacceptance concluded that the evidence base transfers
poorly to 1–3 minute index futures. That lowered Family B's expected value of information, but it
is **not** a result. No NQ experiment was run. DR-05 is a literature review, and a literature
review is not a falsification.

## What is genuinely known about Family B from inside the Solar work

Not nothing — but not enough to substitute for the experiment:

- **DC01** measured the overshoot distribution directly. The right tail is what pays; the median
  directional-change segment loses money. A failed-persistence strategy is, mechanically, short
  that same tail. Its unconditional expectancy is therefore likely **negative**, and it would have
  to earn its keep entirely from *conditioning* — knowing when persistence is about to fail.
- **H-007** (split exit ≠ reversal distance) failed with monotone degradation. That is the closest
  the campaign came to testing an early-exit-on-failure idea, and it lost money at every setting,
  for the DC01 reason: exiting early amputates the tail.
- **The C2 interaction failure** is a warning for any future sleeve: an addition that improves a
  fixed core can reverse sign on an adaptive one. Any Family-B engine must be tested against
  **both** cores before it is believed.

Taken together these say a naive Family B would probably fail, and a conditional one would need a
selector the campaign never found. They do **not** say Family B is dead.

## If this is resumed

Family B is still the highest-value complementary direction, and the open model makes it cheap to
define precisely — a failed directional change is now a *computable event*, not a chart pattern:

- a Type-1 flip that fails to achieve a minimum overshoot before the opposite threshold;
- price crossing back through the prior episode's directional-change threshold;
- a new trend re-entering the prior episode's accepted range;
- a reversal followed by rapid opposite re-flip.

Preregister before running: it must earn **standalone** expectancy (not merely improve the
blend), must be tested on both a fixed and an adaptive core, and must be checked for right-tail
retention on the Solar side — an engine that fires during Solar's best days is not a complement,
it is a hedge that pays for itself out of the only profitable trades in the system.

The honest expected outcome, stated in advance: **more likely to fail than succeed.**
