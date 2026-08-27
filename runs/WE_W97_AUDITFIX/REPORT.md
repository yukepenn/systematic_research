# WE_W97 — ACT ON THE AUDIT · REPORT

Preregistered (`spec.yaml`). A 5-agent adversarial audit of W89–W93, every finding independently
re-tested by a skeptic instructed to refute it: **33 confirmed (10 MAJOR, 23 MINOR), 12 refuted.**
The three conclusion-changing findings were then re-derived here from scratch.

> ## **The deep-history verdict INVERTS, and it favours the pair.**
> ## `{BMOM + X9a}`'s 16-year drawdown reduction is **34.6 %**, not the published 28.2 % —
> ## W87 measured it against a **wrong P1 baseline**. The pair's C4 PASS is **strengthened**.
> ## **NETFUSE_1 is deep-NEGATIVE (−$8,951) with a top-5 drawdown 32.9 % WORSE than P1's.**
> ##
> ## Two of my own `FACT`s are withdrawn: **the clock does not explain the low ρ** (signal
> ## sharing does), and **the quality layer HELPS the two-sided object** once the exit policy
> ## is held fixed.

---

## M10 `RESOLVED` — and the auditor's fear was the wrong way round

W93 compared *"the pair delivers 28.2 % (PASS)"* against *"NETFUSE_1 delivers 11.4 % (FAIL)"* and
labelled them *"reused so the two are comparable"*. They were ratios against **two different P1
deep series**. All four objects rebuilt on 2006–2021 in **one run**, sharing a baseline by
construction:

| | top-5 DD | max DD | net | wk + % |
|---|---|---|---|---|
| **THIS RUN, P1** | **18,925.096** | **39,555.24** | **79,076.48** | **44.484** |
| W93 `deep.csv` P1 | 18,925.096 | 39,555.24 | 79,076.48 | 44.484 | ✅ identical |
| **W87 `deep.csv` P1** | **21,645.704** | **47,250.40** | **57,343.44** | **44.844** | ❌ |

> **W93's P1 is right (and reproduces W80's bit-for-bit). W87's is the anomaly** — and it is not a
> rescaling, because a scale factor cannot change a positive-week rate, and it differs.

### The 16 unseen years, one baseline, every object

| | trades | contract-min | **net $** | wk + % | **max DD** | **top-5 DD** | worst week | streak |
|---|---|---|---|---|---|---|---|---|
| P1 | 9,557 | 1,022,157 | $79,076 | 44.5 % | $39,555 | $18,925 | −$7,019 | 7 |
| BMOM | 5,640 | 1,393,702 | $58,645 | **51.2 %** | $39,743 | $28,361 | −$12,687 | 7 |
| X9a | 9,504 | 1,044,284 | **$120,461** | 45.1 % | $40,933 | $15,866 | **−$6,249** | 10 |
| **PAIR 2:3** | 39,792 | 1,184,051 | **$95,734** | **47.7 %** | **$24,686** | **$12,384** | −$7,250 | **6** |
| **NETFUSE_1** | 20,147 | 1,532,556 | **−$8,951** | 42.4 % | **$49,961** | **$25,148** | −$8,572 | 8 |

**The bar (≥25 % smaller mean top-5 drawdown than P1), on one baseline:**

| | nominal | contract-minute-matched | income-matched |
|---|---|---|---|
| **PAIR 2:3** | **34.6 %** ✅ | **43.5 %** ✅ | **45.9 %** ✅ |
| NETFUSE_1 | **−32.9 %** ❌ | (W93's 11.4 %) | *undefined* |

> ## `FACT` — **over sixteen years it has never touched, the 2:3 pair beats P1 on EVERY
> ## dimension: more money ($95,734 vs $79,076), a 38 % smaller max drawdown, a 35 % smaller
> ## top-5 drawdown, a higher positive-week rate and a shorter losing streak.**
> **W87 understated its own result.** The corrected figure clears the 25 % bar with room, at every
> exposure convention.

⚠️ **Two honesty notes.** (a) The income-matched column is **undefined for NETFUSE_1** because its
deep net is negative — scaling a losing series to match a winner's income flips its sign. The
−910 % the script printed is meaningless and is not quoted; the operative fact is simply *it loses
money*. (b) W93's "11.4 % better" was **contract-minute-matched and the scaling was not
disclosed** (audit MINOR). At nominal exposure NETFUSE_1's deep drawdown is **worse**, not better.

## M3 `CONFIRMED` — my "temporal disjointness" `FACT` is WITHDRAWN

W89 §2 labelled *"BMOM and X9a are substantially disjoint IN TIME … a structural reason for their
weekly ρ = +0.009"* as **`SUPPORTED`**, and preregistered W96 on it. The deconfounding control —
split each object's daily P&L by **entry segment** and correlate weekly against BMOM:

| series | RTH share of net | **weekly ρ vs BMOM** | z |
|---|---|---|---|
| P1 (all) | 100 % | **+0.2869** | 4.16 |
| **P1_RTH** | 35.3 % | **+0.2744** | **3.98** |
| P1_ON | 64.7 % | +0.1097 | 1.59 |
| X9a (all) | 100 % | +0.0094 | 0.14 |
| **X9a_RTH** | 14.3 % | **+0.0205** | **0.30** |
| X9a_ON | 85.7 % | −0.0017 | −0.02 |
| SOLAR_RTH | −7.6 % | +0.0528 | 0.77 |

> **`FALSIFIED`. `X9a_RTH` shares B-MOM's clock completely and still correlates +0.02. `P1_RTH`
> shares the same clock and correlates +0.27 — because P1 *contains* the B-MOM channel.
> The clock never varies with ρ. SIGNAL SHARING does.**
>
> Consequences, all mine to own: the `SUPPORTED` tag becomes **`FALSIFIED`**; the sentence in
> `STATE_OF_THE_SYSTEM.md` that prints it as `FACT` is corrected; and **the "hunt streams three
> and four on the session clock" directive is withdrawn.** W96 was preregistered on this
> inference and then failed its own null at the 88th percentile — which is exactly what should
> have happened if the inference was wrong.

## M8 `CONFIRMED` — W92 §4's `FACT` is WITHDRAWN, and it reverses

`sfills`' session box is a **dollar** limit on **total position** P&L, so a size-2 entry trips the
−$1,300 halt at **32.28 points instead of 64.78**. "NETFUSE_Q" therefore changed the **exit
policy** as well as the sizing. Isolation control — box accumulating **per contract**:

| arm | trades | contracts | wk$ @ fixed DD | wk + % | top-5 DD | t | 2026 wk $ |
|---|---|---|---|---|---|---|---|
| NETFUSE_1 | 3,893 | 3,893 | $1,068 | 58.69 % | $15,611 | 3.67 | $767 |
| NETFUSE_Q (published) | 3,536 | 4,120 | $903 | 56.81 % | $16,289 | 3.41 | $196 |
| **NETFUSE_QN (per-ctr box)** | **3,893** | 4,601 | **$1,177** | **59.15 %** | **$14,401** | **3.79** | **$831** |
| NETFUSE_1N (per-ctr box) | 3,893 | 3,893 | $1,068 | 58.69 % | $15,611 | 3.67 | $767 |

(The last row is byte-identical to the first, as it must be — size 1 everywhere makes the two box
denominations equivalent. That is the control that proves the harness.)

> **Holding the exit policy fixed, quality sizing wins every column.** W92 §4's
> *"`FACT` — the quality layer hurts the two-sided object"* is **withdrawn**.
>
> **And it generalises past the correction**: P1 also runs size 2 on 18.3 % of its trades, so
> **P1's own session box has been tripping early on every one of them for the whole campaign.**
> A per-contract box is now a live candidate object — queued, not adopted, and it needs its own
> null.

## M1 `CONFIRMED` by my own re-derivation — with one disagreement recorded

Two of the corrected rolling gate's three legs are **algebraically scale-invariant**
(`weekly_dd` is a shape ratio, `wkpos` is a sign rate, and cost scales with the series). Measured
on the 2:3 basket over one window: **weekly_dd = 1922.4349378102 and wkpos = 60.0000000000 at both
scale 0.05 and scale 7.30**, identical to 10 dp, while top-5 moves exactly linearly. Only the raw
top-5 leg discriminates — so the published ALL-THREE is a property of the chosen divisor:

| basket | NOMINAL (published) | PEAK contracts | time-weighted | **income-matched** |
|---|---|---|---|---|
| 1:1 | 64 % | 16 % | 72 % | 24 % |
| **1:2** | 52 % | **48 %** | 52 % | 52 % |
| **2:3** | **92 %** | 36 % | **92 %** | **64 %** |

And at any **common** scale, 1:1 ≥ 2:3 (s = 0.20 → 92/92; 0.25 → 92/36; 0.333 → 92/0; 0.50 → 64/0).
**The published ordering exists only because each rung was divided by its own nominal order count
(1/2, 1/3, 1/5).**

> **Where I disagree with the auditor.** It concluded *"under peak matching the ranking becomes
> 1:2 > 1:3 > 2:3 and agrees with the matched-income table"*. That holds under **peak** matching
> only. Under **income** matching — the one scale with no free choice, since income is what is
> being bought and drawdown is its price — **2:3 still leads, at a reduced 64 %.**
> The correct statement: **the ranking is unit-dependent; 2:3 leads in 3 of 4 units at a lower
> figure than published; 1:2 is the only rung stable across all four (48–52 %).**

Oracle battery re-run at every scale the table uses: **100 % at 0.20 / 0.25 / 0.333 / 0.50 / 1.0**,
and 0 % at 2.0. It had only ever been run at 1.0.

## M9 — WITHDRAWN, and corrected to the owner directly

W92's banner *"beats P1 in 2026"* and the row *"2026 weekly $ | $287 | $575 | **2×**"* carry no
standard error, which charter amendment 2 §2(a) requires. The **paired** weekly difference is
**+$288/wk, SE $599, t = 0.48, p = 0.635, N = 31 weeks**, 95 % CI **[−$936, +$1,511]**. McNemar on
the "+5.2 pp positive weeks" claim: **p = 0.193**. A 200k paired bootstrap puts
**P(NETFUSE < P1 in 2026) = 0.32**.

**Withdrawn.** I repeated this figure to the owner in conversation; the correction goes to him
explicitly, not only into a file.

## The other six MAJOR findings — corrections applied, verdicts survive

| | correction |
|---|---|
| **M2** W89 | quote-session membership tested on **calendar dates**; the 45 sessions span 78 calendar days. Correct coverage **P1 128/4,004 (3.2 %)**, BMOM 84, X9a 148 — not 206/118/228. P1's 128 reproduces W82's committed `fillaudit.txt` verbatim. Nothing downstream moves — `direct_cov` has no consumer and every cost figure uses the minute-weighted profile at 100 % minute coverage. |
| **M4** W90 | H4's null scored the **full 1,043-trade book** against 518-trade controls — 2.01× the exposure. Corrected percentiles **82.0 / 30.5 / 76.0** against the published 86.5 / 81.0 / 73.5. Verdict **GENERIC either way**, and the corrected positive-week leg (30.5th) is *more* unflattering. |
| **M5** W90 | the two-box arm ran **31 % more exposure**. Matched: top-5 DD is a dead heat (+0.24 %), **max DD reverses to two boxes**, worst week is 1.50× not "doubles", streak is a **tie**. *"beats on every column"* and the `REPRODUCED` tag are withdrawn; **H3 stays 0/3** because both scale-invariant legs still favour one box. |
| **M6** W91 | W67's 7.26 pts/session is **NET**; W91's 6.64 is **GROSS**. Like-for-like: **7.26 → 6.19 net (−14.85 %)**, not −8.5 %. P1: 14.86 → **13.24** net, not 13.73. W95's B1 gate enshrined the gross figure — relabelled, not loosened. |
| **M7** W91 | `one_budget()` charged cost and exposure on trades whose P&L it deleted (23.3 % of contract-RTs). Corrected the ONE-budget row is **$471/wk not $330**, and the ordering **reverses** — one budget is *worse* than two on top-5 DD and worst week. **E_a FALSIFIED and "separate budgets are necessary" both survive.** |
| 23 MINOR | listed in `out/audit_confirmed.json`. Mislabelled artifact columns (`null p95` printing 5th percentiles), prose-only numbers, an undisclosed exposure scale in W93's deep row, a quarter-boundary gap in the walk-forward coverage mask, and an unlabelled 8-of-16-year subset in W93's deep table. **None changes a verdict.** |

## What this wave changes about the standing picture

1. **`{BMOM + X9a}` is stronger than the campaign believed.** Over 16 unseen years it beats P1 on
   money, max drawdown, top-5 drawdown, positive-week rate and losing streak — simultaneously.
2. **NETFUSE_1 is weaker.** Deep-negative, and its drawdown geometry is worse than P1's at nominal
   exposure. It remains the only object to clear a specificity null, and that still stands.
3. **The clock is not a research axis.** Withdrawn on its own control, consistent with W96's failure.
4. **The session box's dollar denomination is a defect, not a design.** It penalises exactly the
   trades the quality layer sized up. New candidate; needs its own wave.
5. **The rolling gate needs a fixed exposure convention written into the instrument**, or every
   future ALL-THREE is a divisor choice. Recommended: **income-matched**, because it is the only
   convention with no free parameter.

**NOTHING IS PROMOTED OR ADOPTED BY THIS WAVE.**

## Files
`out/auditfix.txt` · `out/deep_common_baseline.csv` · `out/deep_series.csv` ·
`out/clock_control.csv` · `out/m8_isolation.csv` · `out/gate_by_unit.csv` ·
`out/audit_summary.md` · `out/audit_confirmed.json` · `out/verify_m1.py` · `out/verify_m1b.py` ·
code `research/weekly_edge/src/run_we_w97.py`
