# WE_W53 — TWO BOOKS (overnight vs RTH) · REPORT

Spec preregistered. 2022-07-01 → 2026-08-01, 1,012 sessions / 204 weeks, net $4.36/RT.

**VERDICT: `FALSIFIED` on the wave's own preregistered terms. Nothing adopted.** The NIGHT/DAY
split is one bet sampled twice: random contiguous time splits, scanned identically, beat it.

---

## 1. Phase 1 — the two books as they already exist

| | trades | pts/session | exposure | money | weekly | worst week | maxDD | mean top-5 DD | MAR | ann Sharpe |
|---|---|---|---|---|---|---|---|---|---|---|
| P1 incumbent | 1,942 | 14.86 | 100 % | 100 % | $1,475 | −$7,418 | $20,245 | $14,266 | 14.86 | 2.26 |
| NIGHT 18:00–08:00 | 1,056 | 7.18 | **71.6 %** | **48.3 %** | $712 | −$5,118 | $15,180 | $9,210 | 9.57 | 1.70 |
| DAY 08:00–17:00 | 886 | 7.68 | **28.4 %** | **51.7 %** | $762 | −$6,927 | $17,641 | $12,350 | 8.82 | 1.48 |

`FACT`, and sharper than W51b's version of it: the money is split almost exactly in half, but
the **exposure is not** — the DAY book earns 51.7 % of the money on 28.4 % of the
contract-minutes, i.e. it is roughly **2.6× more productive per contract-minute** than the
NIGHT book. Overnight positions are held far longer for the same money. The two books also
have opposite per-year profiles: NIGHT is −0.59 pts/session in 2023 and +19.49 in 2026; DAY is
+3.63 in 2023 and **−3.70 in 2026**.

Weekly correlation of the two books: **−0.032** over all 204 weeks.

### A correction I have to make to my own diagnostic

The spec asked for that correlation *inside the worst decile of the combined object's weeks*,
and it comes out **−0.692**. I am not going to present that as tail-hedging, because
**conditioning on the SUM being extreme mechanically induces negative correlation between its
components** — in the limit of conditioning on a fixed sum it is −1 by construction. The
number is a selection artifact of my own test design, not evidence. The honest version of that
test conditions on something exogenous (a volatility-regime variable, or one book's own worst
weeks) and it has not been run. W43's lesson still stands unaltered; this wave simply did not
test it correctly.

## 2. Phase 2 — constant-total-exposure weight scan

w = share of the incumbent's total contract-minutes given to NIGHT. The incumbent sits at
w = 0.716 by construction and reproduces exactly.

| w | 0.00 | 0.25 | 0.50 | 0.60 | **0.65** | 0.70 | 0.75 | 0.85 | 1.00 |
|---|---|---|---|---|---|---|---|---|---|
| pts/session | 27.08 | 22.82 | 18.55 | 16.85 | 15.99 | 15.14 | 14.29 | 12.58 | 10.02 |
| maxDD | $62,168 | $46,107 | $30,130 | $23,774 | $20,971 | $20,423 | $19,875 | $18,780 | $21,194 |
| **MAR** | 8.82 | 10.02 | 12.46 | 14.34 | **15.44** | 15.00 | 14.55 | 13.56 | 9.57 |

The best interior weight is w = 0.65 at MAR 15.44 against the incumbent's 14.86 — **+3.9 %**,
which is nothing. `FACT`: **the object is already sitting essentially on the optimum of this
axis by accident.** There is no breadth to harvest here by re-weighting.

**The unifying event-count law survived a direct test.** Both corners lose badly (all-DAY MAR
8.82, all-NIGHT 9.57) against every interior weight from 0.30 up. The law predicted exactly
that and would have been reopened if a corner had won.

## 3. Phase 3 — per-book session boxes are WORSE

| | pts | maxDD | mean top-5 DD | MAR | exposure |
|---|---|---|---|---|---|
| P1 (one combined box) | 14.86 | $20,245 | $14,266 | **14.86** | 100 % |
| sum of per-book boxes, rescaled to equal exposure | 14.95 | $25,239 | $14,628 | 11.99 | 100 % |

Giving each book its own −$1,300/+$1,000 box makes the drawdown **25 % worse** for the same
money. `SUPPORTED`: this is W22/W26's mechanism confirmed from the other side — the box works
because it truncates the loss **where it is actually formed**, and the loss is formed in the
combined book, not separately in two tapes.

## 4. Phase 4 C1 — my own event-count law, tested head-on

Standing aside in 10:30–12:00 ET, the *only* window W51b measured as negative (−0.06
pts/session), reduces events. The law predicts the tail gets worse faster than production
improves. Measured:

| | pts | worst week | maxDD | mean top-5 DD | Ulcer | MAR |
|---|---|---|---|---|---|---|
| P1 incumbent | 14.86 | −$7,418 | $20,245 | $14,266 | $6,183 | **14.86** |
| C1 no 10:30–12:00 entries | **15.39** | −$6,890 | **$24,827** | **$16,545** | **$7,987** | 12.55 |

Production **up 3.5 %**, drawdown **up 23 %**, Ulcer **up 29 %**, MAR down 16 %. `REPRODUCED` —
a fourth independent instance of the law, and the first one where I aimed a falsifier at it
deliberately.

## 5. Phase 4 C2 — the binding null, and the verdict

200 random contiguous 840-minute windows on the session clock, each weight-scanned identically,
each contributing its own best-interior-w:

| quantity | NIGHT/DAY | null mean | percentile | |
|---|---|---|---|---|
| best interior **MAR** | 15.44 | **18.06** | **37.0 %** | fail |
| best interior pts | 15.99 | 14.09 | 94.5 % | fail |
| best interior mean top-5 DD | $16,453 | $12,304 | **1.5 %** | fail |
| best interior Ulcer | $6,892 | $5,256 | 4.0 % | fail |
| weekly correlation | −0.032 | −0.061 | 22.0 % | fail |

The preregistered bar was ≥ 95th percentile on both pts and MAR. **MAR sits at the 37th
percentile and the drawdown metrics at the 1.5th and 4th** — the NIGHT/DAY split is not merely
un-special, it is **worse than a typical random time split** on exactly the dimension the owner
cares about. Recorded conclusion: the overnight and RTH tapes are the same bet sampled twice,
and breadth has to come from somewhere else.

## 6. The method rule this wave bought (`FACT`, applies retroactively)

The C2 null's *mean* best-interior MAR is **18.06** against the incumbent's 14.86, with a 95th
percentile of **29.15**. Both the true arm and every null draw take a **maximum over 21
correlated weights**, so that inflation is pure selection: **taking the best w out of a scan
inflates MAR by roughly 20 % on average, and by up to 2× in the tail, on data with no
structure at all.**

> **New binding rule: a weight scan may never be compared against the incumbent directly. It
> must be compared against a null that is itself scanned the same way (scan-matched null).**

Every prior weight-scan claim in this campaign that lacked a scan-matched null is now suspect.
The W41 clock basket was already withdrawn for a different defect; this rule would have caught
it independently.

## 7. What still stands after this wave
- `FACT` half the money is overnight — but the DAY book is 2.6× more efficient per
  contract-minute, so "trade more at night" is the wrong reading of it.
- `FACT` the object's night/day weighting is already near-optimal.
- `REPRODUCED` the event-count law, now 4 instances, one of them a deliberate falsifier.
- `SUPPORTED` the session box belongs on the combined book.
- The live lead is **W54 entry timing**, generated by W51d's N1 null.

## 8. Files
`out/twobooks.txt` `out/books.csv` `out/wscan.csv` `out/wscan_box.csv` `out/nulls.csv`
Code: `research/weekly_edge/src/run_we_w53.py`.
