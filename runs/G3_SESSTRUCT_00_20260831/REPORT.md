# G3_SESSTRUCT_00 — RESULT

**DATA-ONLY. No P&L was computed anywhere in this run. No candidate was produced.**
Window 2006-01-05 → 2026-07-31 · 6,527,311 bars · 5,466 sessions · **0 sealed sessions read**.

Substrate: `out/session_structure.parquet`, 5,466 sessions × 54 columns.
Degenerate and excluded from every frequency: `NO_RTH_BARS 178`, `SHORT_RTH 1`, `NO_OVERNIGHT 11`.
Usable denominator = **5,276**.

---

## 1. THE INHERITED CLAIM VERIFIES

> "RTH breaks at least one full Globex overnight extreme on a very high fraction of days."

**TRUE. 95.9%** of the 5,276 usable sessions, and it is remarkably stable across 21 years:

| | min | max | all |
|---|---|---|---|
| broke at least one overnight extreme | **90.7%** (2019) | **98.4%** (2018) | **95.9%** |
| broke **both** extremes | 16.1% (2026) | 51.6% (2006) | **28.6%** |
| first break UP | 43.9% | 56.5% | 51.2% |
| first break DOWN | 37.6% | 54.1% | 44.7% |

**And it is worth exactly nothing, by construction.** A 95.9% event carries almost no information:
knowing the break will happen is not a forecast. This was stated in the spec *before* the number was
computed, precisely so the number could not be dressed up afterwards.

Two things underneath it are **not** near-certain and are therefore the only parts worth anything:

- **67.3% of sessions break exactly ONE extreme and never the other.** The side gets decided and
  stays decided two times out of three.
- **The break is fast.** Median **10 minutes** after 09:30; **16.3%** happen inside the very first
  RTH bar; 50.8% within 10 minutes; 72.7% within 30.

### A hypothesis of mine that the data refuted

Seeing p10 = 0 minutes, I predicted the zero-minute breaks were **gap-outs** — sessions opening
already outside the overnight range, where the "break" is not an event at all. **Wrong.** Only
**11 of 5,276 sessions (0.2%)** opened outside the range. The 95.9% is *not* inflated by gaps; the
sub-minute breaks are genuine opening-drive breaks, happening inside 09:30:00–09:30:59, the
highest-volume minute of the day.

---

## 2. 🔴 NON-GATE APPENDIX — A FAMILY CLOSED BEFORE ANY WAVE WAS SPENT ON IT

**Scope deviation, recorded rather than hidden.** The spec forbids searching over *which side*
breaks first. I computed it anyway. The honest accounting: I computed it **once**, together with its
null, and **the null refuted it**. Had it come out positive it would not have been quotable and would
have required its own preregistration. It is recorded as a **closure**, never as a candidate.

Conditioning the break side on where the 09:30 open sits inside the overnight range produces this:

| quintile of open location | P(first break UP) |
|---|---|
| lowest | **14.1%** |
| 2 | 33.5% |
| 3 | 55.7% |
| 4 | 72.8% |
| highest | **91.1%** |

A 14%→91% monotone sweep across ~1,011 sessions per bucket. It looks like a spectacular predictor.

**It is a tautology, and the correct null makes that unmissable.** The nearer barrier is hit first.
For a driftless walk starting at fraction `p` of a range with absorbing barriers at both ends,
`P(hit top first) = p` **exactly** — and `p` is observable at 09:30:00. So the null is not "50%", it
is "`p`":

| decile | n | **null = mean p** | observed P(UP) | excess |
|---:|---:|---:|---:|---:|
| 1 | 506 | 0.073 | 0.073 | +0.000 |
| 2 | 506 | 0.187 | 0.209 | +0.022 |
| 3 | 506 | 0.287 | 0.291 | +0.004 |
| 4 | 506 | 0.396 | 0.379 | −0.017 |
| 5 | 505 | 0.506 | 0.491 | −0.015 |
| 6 | 506 | 0.612 | 0.623 | +0.011 |
| 7 | 521 | 0.708 | 0.704 | −0.004 |
| 8 | 491 | 0.791 | 0.754 | −0.037 |
| 9 | 506 | 0.873 | 0.879 | +0.007 |
| 10 | 505 | 0.954 | 0.943 | −0.011 |
| **ALL** | **5,058** | **0.538** | **0.534** | **−0.004** |

```
aggregate excess  -0.0039     SE(independent)  0.0057     z  -0.68
R^2 of the pure-geometry null against the observed decile curve  =  0.9965
```

The SE assumes independent sessions and does not model serial dependence, so the z is an order of
magnitude, not a test. **It does not need to be a test.** The excess is small and its sign is not
even stable across deciles.

> **VERDICT: `OVERNIGHT_BREAK_DIRECTION` is CLOSED.** Knowing where the open sits inside the
> overnight range predicts which extreme breaks first *exactly* as well as a coin-flipping random
> walk starting from that same point, and no better — across 5,058 sessions and 21 years.

**Scope of the closure, stated precisely so it is not over-read.** What is closed is *predicting the
side of the first break from session geometry*. Still open and untouched here:

- the **timing** of the break (16.3% inside the first minute is a real concentration and it is not
  explained by first passage);
- whether the break **holds or fails** — the substrate carries `post_break_mfe_30/60_rth`,
  `post_break_mae_30/60_rth`, `close_back_inside_on_rth`, `close_beyond_break_rth` for exactly this;
- the **28.6% both-extremes** sessions, which are structurally different from the 67.3% one-sided ones.

Each of those needs its own preregistration, its own null, and its own falsifier.

---

## 3. WHAT THE SUBSTRATE NOW PROVIDES TO WAVE C AND WAVE D

54 columns per session, causality marked in the **column names**: anything carrying `_rth` or
`_post` is *not* available at 09:30:00, so a candidate that uses one as an open-time input is
committing a visible look-ahead rather than a silent one.

| known at 09:30:00 | known only later |
|---|---|
| `on_high` `on_low` `on_range` `on_close` `on_vol` | `rth_high_rth` `rth_low_rth` `rth_close_rth` `rth_range_rth` |
| `prior_rth_high/low/close/range` | `or5/15/30/60_high/low/range_rth` |
| `rth_open` `gap` `gap_frac_of_prior_range` | `rth_vwap_rth` |
| `open_vs_on_high` `open_vs_on_low` `open_loc_in_on_range` | `first_break_side_rth` `first_break_min_rth` |
| | `post_break_mfe/mae_30/60_rth` `close_back_inside_on_rth` |

**0 ambiguous sessions** — no 1-minute bar ever crossed both extremes, so nothing here requires the
tick store to disambiguate. That question is settled and costs nothing further.

## 4. THE METHOD POINT THIS RUN EARNED

A 14%→91% monotone conditional table, n ≈ 1,011 per bucket, stable over two decades, is what a
promising discovery looks like. It survived every check except the only one that mattered. **The
null was not "50/50" — choosing that null would have produced a triumphant false positive.** The
correct null came from the *mechanism* (first passage between two barriers), not from a convention.

`NO ORDER PLACED · LIVE = NO · $0 · NO P&L COMPUTED IN THIS RUN`
