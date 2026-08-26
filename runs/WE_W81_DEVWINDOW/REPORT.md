# WE_W81 — IS P1'S ADVANTAGE CONFINED TO ITS OWN DEVELOPMENT WINDOW? · REPORT

Preregistered, including the disclosure that the wave was motivated by a pattern I noticed
**after** W80's read — which is exactly why it carries a placebo arm, a regime-variable check
and per-block standard errors.

> ## VERDICT: **H is FALSIFIED. The anchor question is closed.**
> ## The P1 / X9a difference is not distinguishable from zero on any sample this repo holds.

---

## 1. The pattern that motivated it

W80 found X9a (P1 with the OR-slot channel anchored at the 18:00 session open instead of 09:31)
beating P1 **outside** P1's 2022–2026 development window and losing **inside** it: +53 % over the
sixteen unseen years, +$16,702 vs −$20,686 in the 46 never-read sessions, better in 2024 and 2026,
much worse in 2023 and 2025. That is the shape you would expect if the 09:31 anchor were fitted to
the middle of the development sample — and the rolling test cannot see it, because the rolling
test is computed entirely inside the contaminated region.

## 2. The four preregistered conditions

Forty non-overlapping 6-month blocks, 2006–2026, `(P1 − X9a)` per trade:

| condition | result | |
|---|---|---|
| (a) P1 ahead in a **majority** of the 8 DEV blocks | **62 %** | yes |
| (b) P1 **not** ahead in a majority of the 32 non-DEV blocks | **47 %** | **NO** |
| (c) placebo arm X2 does **not** reproduce the pattern | dev 50 % / non-dev 47 % | placebo clean |
| (d) dev-window dummy explains more than any regime variable | R² **+0.084** vs best regime R² +0.037 | dev-window wins |

**Condition (b) fails.** P1 is ahead in 62 % of development blocks and in **53 %** of all the
others — a difference of nine percentage points across forty blocks, which is nothing.

And the sample-adequacy line, which the spec required and which decides the wave:

> **0 of 40 block differences are individually |t| > 2.**

The curve is a shape, not a set of measurements.

## 3. The paired test that settles it (`FACT`)

The two objects run on the **same bars** with **one constant** different, so the honest statistic
is the per-session paired difference:

| | sessions | mean (X9a − P1) | SE | **t** |
|---|---|---|---|---|
| **deep 2006–2021** | 2,769 | **+$14.95/session** | $11.10 | **+1.35** |
| **modern 2022-07 → 2026-07** | 1,058 | **−$43.81/session** | $54.09 | **−0.81** |

**Neither is significant.** W80's headline — X9a +53 % over sixteen years ($120,461 vs $79,076) —
is a **1.35-sigma** effect. On 2,769 sessions the two objects are the same object within noise;
X9a is strictly better on only 24.3 % of sessions and identical on 53.3 %.

> `RECORDED`: **the 09:31-vs-18:00 anchor makes no measurable difference to the OBJECT on any
> sample this repository holds.** W72's finding that the session-anchored *channel* is the only
> durable one of eleven (standalone pre-2022 t = 1.83 vs 0.93) stands as a **channel-level**
> result. It does not survive being embedded in the object, because the Solar consensus supplies
> the entry on 53 % of sessions regardless of which anchor the OR gate uses.

## 4. What this closes, and what it is worth

- **The anchor question is closed.** Two waves (W72 amendment 1, W80) and this one; three
  independent tests; no promotable difference.
- **W80's deep run is unaffected as a measurement of the OBJECT**: 0.92 pts/session over sixteen
  unseen years against 14.86 modern, stress-negative, with 2006–2017 at −$15.4k and 2018–2021 at
  +$94.5k. That finding is about P1, not about the anchor, and it stands.
- **My own post-hoc pattern died on its placebo**, which is the outcome the placebo existed to
  produce. Noticing a shape in a table after the fact and then testing it properly is the correct
  sequence; believing the shape would have been the seventh full-sample-dominance error of this
  campaign.

## 5. The method note worth keeping

The block curve *looked* convincing — a run of DEV blocks favouring P1 flanked by non-DEV blocks
favouring X9a. What killed it was not the pattern-matching but three cheap additions the spec
required in advance:

1. **a placebo arm with no claim attached** (X2 showed the same 50/47 split → the pattern is a
   property of the measurement);
2. **per-block standard errors** (0 of 40 significant);
3. **a paired test at the level the objects actually differ** (session-level, t = 1.35 and −0.81).

Any one of them alone would have been enough. None of them cost more than a few lines.

## 6. Files
`out/devwindow.txt` `out/console.log` · `out/blocks.csv` `out/deep_P1.csv` `out/deep_X9a.csv`
`out/deep_X2.csv` · code `research/weekly_edge/src/run_we_w81.py`
