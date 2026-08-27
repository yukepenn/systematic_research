# Validation harness — one-time hardening, 2026-08-27

POST-W118 owner directive §8 and §35. Three consecutive waves had **harness** defects rather than
market findings, and each would have corrupted a headline:

| wave | defect | what it would have done |
|---|---|---|
| **W115** | the causality *checker* corrupted every session at once, so every trailing window moved | reported **LEAKAGE on three clean drivers** |
| **W116** | the best-of-K null drew **independent** signs across 15 highly-correlated timing cells | inflated the bar $166 → $215, **enough to fail a real object** |
| **W118** | an event gate was evaluated at a fixed 12:00 clock instead of at the trigger bar | rule fired on the first 2-point wiggle — **median entry 09:32, 99.4 % of sessions** |

`research/weekly_edge/src/we_harness.py` exports the four primitives and runs the synthetic tests.
**7 of 7 checks pass** — and critically, each test *detects* the corresponding historical defect:

- **A** — a causal `rolling+shift(1)` feature PASSES; a no-shift feature and a `shift(-1)` feature
  both FAIL. The repaired check asserts a **window identity** *and* perturbs a **single**
  observation, requiring `driver[i]` unchanged **and** `driver[i+1]` moved.
- **B** — on a synthetic family at ρ = +0.918 (effective K **1.08 of 15**), the independent-sign
  bar is **1.65×** the shared-sign bar. The harness measures the inflation rather than assuming it.
- **C** — a gate at/before its trigger PASSES; a gate pinned to a fixed 12:00 **FAILS**, with
  193 of 400 gates landing *after* their own trigger. It also prints the realised trigger-time
  distribution, which is the cheapest possible tell that an "endogenous" rule is firing at a fixed
  early minute — before any P&L is read.
- **D** — early-close and missing-session alignment: a 15:44 bar is correctly absent for both.

§35 is explicit that this is a one-time hardening and not a software project. **Done; not to be
extended.** Future waves import the primitives instead of re-deriving them.
