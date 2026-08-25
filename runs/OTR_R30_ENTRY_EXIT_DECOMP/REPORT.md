# OTR_R30_ENTRY_EXIT_DECOMP — report

Spec + amendments 1–3 preregistered before their readouts. Directive v5.0 and the owner's
real-time epistemic correction, both 2026-08-25 (corrections 3, 5, 8).
Code: `run_r30a_quantity.py`, `run_r30a2_sessionbound.py`, `run_r30a3_stoppoints.py`,
`run_r30b_opportunity.py`, `run_r30c_exitfamilies.py`.

**Data boundary honoured.** Substrate ends 2026-05-29; June/July bars are not local.
`LOCKED_FORWARD` seals 2026-08-01 onward — August was **not** touched. The right-tail
discriminator is therefore late-May (OTRIMG-0148), not July/August.

---

## PART A — the −$2,600 fingerprint, conditional on quantity (owner correction 5)

The correction was justified: qty-2 is confirmed live, and **$2,600 = 65 pts × $20 × 2** where
65 points is *exactly* the established 2025-era stop, making "the stop never changed" the more
parsimonious rival. Three independent constraints were applied.

**1. Legal-tick.** `2600 / (20q)` must be a multiple of 0.25, admitting
q ∈ {1, 2, 4, 5, 8, 10, 13, 20} and **excluding q = 3, 6, 7, 9**.

**2. Parity.** A single-trade cell that is an odd multiple of $5 forces odd quantity *on that
trade*. Four SA records qualify — OTRIMG-0113, **0121**, **0129**, **0146** — of which three are
−$2,600 weeks. **Bucket A = 3, bucket B = 15, bucket C = 0.**

**3. Session bound (amendment 1) — landed in its registered WEAK direction.** "Exit on session
close" is checked, so no trade spans a session and `largest_win/(20q) ≤ max session range`. But
max session ranges are 461–1058 points, so even q=1's implied 145–584-point largest wins fit
comfortably. **Nothing excluded.** D3 registered this asymmetry in advance.

**4. Scale-invariance (amendment 2) — the test that worked.** `trades`, `wr`, `hold` and
`payoff` are invariant under uniform quantity scaling, so the stop *in points* is identifiable
without knowing q. Re-simulating the frozen incumbent at each candidate stop:

| stop pts | implied q | trades (his 1214) | wr % (his 39.2) | hold (his 59.7) | invariant score |
|---|---|---|---|---|---|
| **130.00** | **1** | 1512 | 31.8 | 72.2 | **0.4448** |
| **65.00** | **2** | 1599 | 30.5 | **61.9** | **0.4682** |
| 32.50 | 4 | 1744 | 26.9 | 48.9 | 0.6069 |
| 26.00 | 5 | 1799 | 24.9 | 45.0 | 0.6950 |
| 13.00 | 10 | 2002 | 19.0 | 33.1 | 1.0264 |
| 10.00 | 13 | 2105 | 16.2 | 27.6 | 1.1643 |

E1 PASS (monotone). **q = 4, 5, 10, 13 are decisively excluded** — their win rates collapse to
16–27 % against his 39.2 %.

### Part A verdict

- For the **four odd-cell SA records**, parity forces odd q, and behaviour excludes 5 and 13.
  **q = 1 is forced there — including OTRIMG-0129, the March catastrophe week.** The 130-point
  stop is confirmed for those, and the March reading (avg loss −$998 = 50 points) is solid.
- For the **other 15 −$2,600 weeks**, 130×1 and 65×2 separate by only **0.0234** — not a
  discriminator — and **65 points actually fits *hold* better** (61.9 vs 72.2 against his 59.7),
  and hold is a §40 weight-3 metric. **Both stay live (§6).** The owner's "the stop never changed"
  rival is not merely admissible, it is competitive.
- E4 confound, registered in advance: this identifies the stop only **conditional on the
  incumbent entry path**, which Part C now shows is itself suspect.

---

## PART B — market opportunity vs strategy capture (owner correction 3)

Measured from **bars alone**, never from any model's entries, so it cannot be contaminated by our
wrapper being wrong.

### H-MARKET is REFUTED — and in the opposite direction to the working assumption

March 2026-03-22→03-27 was not a low-opportunity week. It was one of the **highest**:

| measure | March rank (1 = least opportunity) |
|---|---|
| **max_run** (mean longest directional run) | **17 / 17** |
| mfe60_short | 16 / 17 |
| session_range | 15 / 17 |
| atr14 | 15 / 17 |
| mfe60_long | 14 / 17 |
| efficiency | 10 / 17 |

**Zero of six** measures rank 1–2; the preregistered rule needed ≥ 3.

**B3 FAILED** and is recorded, not rewritten: I predicted our realised per-trade MFE in March
would be below median. It was **above** it (54.5 vs 52.9 pts, rank 11/17). Excursion was there and
our trades had it.

**Our avg_win ranked 14/17 that week (one of our better weeks). His ranked 1/17 — his worst.**

> **The market offered the most, and he captured the least.**

### The structural finding: his capture is INVERSELY related to opportunity

Systematic across all 17 windows, not a one-week accident:

| opportunity measure | corr with **HIS** avg_win | corr with **OUR** avg_win |
|---|---|---|
| max_run | **−0.595** | +0.295 |
| mfe60_short | **−0.652** | +0.364 |
| atr14 | **−0.469** | +0.498 |
| session_range | −0.163 | +0.633 |

His holds carry the same sign: his **longest** hold of 2026 (123.1 min) is in the **lowest**-ATR
week (7.47), his shortest holds in the highest-ATR weeks.

**H-MARKET refuted. H-EXIT and H-ENTRY survive.**

---

## PART C — exit families: **F4 FIRES. Exit geometry alone cannot explain the residual.**

Entry path frozen at the incumbent; each family *adds* one discretionary exit, so X_OPP is the
baseline and every family's marginal effect is isolated. 26 variants across 8 families.

**F1 PASS** (registered in amendment 3 before readout): a fixed-point trail beats an ATR-scaled
trail on both metrics — X_TRAIL_PTS best corr **−0.067** / dist **0.5423**, X_TRAIL_ATR best corr
**+0.414** / dist **0.6078**. Scaling by volatility does remove the dependence, as predicted.

**F3 / F4 FAIL — the decisive result.**

| | target (his) | best achieved |
|---|---|---|
| corr(max_run, avg_win) | **−0.595** | **−0.067** (1 of 26 families is even negative) |

**C1 fails decisively.** Every family that pulls March down to ~$909 pulls late-May down with it:

| family | March (target **$909**) | late-May (target **$2,061**) | corr | §40 dist |
|---|---|---|---|---|
| X_TRAIL_PTS 40 | **$882** ✓ | $912 ✗ | +0.124 | 0.6836 |
| X_TRAIL_PTS 50 | **$930** ✓ | $922 ✗ | +0.017 | 0.6296 |
| X_TRAIL_PTS 60 | **$960** ✓ | $1,078 ✗ | +0.093 | 0.5856 |
| X_OPP (baseline) | $1,425 | $1,393 | +0.295 | 0.4768 |

**No exit family moves March and late-May in opposite directions.** That asymmetry was the whole
test, and nothing passes it.

**A §40 discipline note.** The best family by aggregate distance is **X_TARGET 80** (0.4594 vs
baseline 0.4768) — and its correlation is **+0.606**, the sign exactly backwards. The aggregate
metric prefers a family that gets the structure inverted. F3 anticipated this by making the
correlation primary, so X_TARGET is **rejected despite winning the aggregate**. Recorded because
it is a live example of why §40 forbids letting one summary number pick a mechanism.

### Why exits cannot do it — the argument, not just the result

If you are *in* a position while a large run happens, **any** exit rule captures some of it. An
exit rule can scale winners down uniformly, but it cannot invert their relationship with the
excursion that was available. To make winners *shrink* as runs get *bigger*, you must not be in
the position during the big runs — **and that is an entry property.**

**The sign of corr(opportunity, avg_win) is an entry signature, not an exit signature.**

---

## What R30 establishes, and what it does not

**Establishes:**
- q ∈ {4, 5, 10, 13} excluded behaviourally. **q = 1 forced for the four odd-cell records**,
  including the March week — the 130-point stop is confirmed *there*.
- For the other 15 −$2,600 weeks, **130×1 and 65×2 both remain live**, separated by 0.023, with
  65 fitting hold better. The owner's rival is competitive, not merely admissible.
- **H-MARKET refuted**: March was the highest-opportunity week of the sample, not the lowest.
- **His capture is inversely related to market opportunity (−0.60); ours is positively related
  (+0.30 to +0.63).** This is the sharpest structural difference found in the 2026 era.
- **Exit geometry alone cannot explain it** (F4). Best correlation achievable is −0.067 against
  −0.595, and no family reproduces the March/late-May asymmetry.

**Does not establish:**
- Which entry architecture produces a negative correlation. That is now the open question.
- Anything about June/July (bars not local) or August (sealed).
- That the incumbent entry path is correct — Part C's failure is direct evidence it is not.

## Consequence for the surviving cause set (owner correction 1)

| | cause | status after R30 |
|---|---|---|
| A | entry **timing** | **LIVE — now primary** |
| B | entry **selection** | **LIVE — now primary** |
| C | exit geometry | **strongly disfavoured as a sole explanation** (F4) |
| D | interaction A+B+C | live |
| E | direction-specific sizing | untested |

## The hypothesis this points to, registered here and tested in R31

Every one of the 144 members in the R7/R8 grid is **trend-conditional**: a long requires
`trend > 0`. The entire member space is trend-following. A **mean-reverting / fading**
architecture — sell the upper rail, buy the lower rail, *against* the move — has **never been
tested**, and it produces the observed sign by construction: in a quiet week price oscillates
around fair value and fades pay well; in a high-run week price trends and fades get run over.

VWAP Flux is a **value-area** indicator, and fading the outer rails toward Fair Value is its most
natural use. If he is fading, we have not merely mis-tuned his model — **we have never tested his
architecture.** Preregistered as OTR_R31.
