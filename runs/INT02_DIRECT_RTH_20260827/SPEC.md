# INT02 — market internals → DIRECT RTH NQ return · PREREGISTRATION

| | |
|---|---|
| **status** | **COMMITTED BEFORE ANY RESULT** |
| date | 2026-08-27 |
| authorized by | owner directive §11 — the lane to open immediately after TSMOM failed |
| window | 2022-01-03 → **2026-05-30** (internals substrate begins 2022-01-03) |
| seal | **≥ 2026-08-01 NOT READ.** 2026-05-31 → 07-31 BURNED window also excluded |

---

## 1. What this tests, and what it must not be confused with

`INT01` closed **internals → `P1/PCT` full-horizon action value**: a routing question about an
existing strategy's decisions. It is **NULL** and stays closed.

**INT02 tests a different mapping entirely: internals → the DIRECT RTH NQ return.** Different
target, different variance, different sample. `INT01`'s null says nothing about it, and this run
may not be used to reopen `INT01`.

> **"Internals are null" is NOT an available conclusion from INT01.** Only this mapping is tested
> here, and only this mapping may be concluded on.

## 2. Decision clock and information rule

- **RTH only.** Decisions at **09:45, 10:45, 11:45, 12:45, 13:45, 14:45** ET — six per session,
  each held exactly **60 minutes** (last exit 15:45). **Non-overlapping by construction.**
- **Primary horizon = 60 minutes.** Declared here, not selected.
- **Information set at decision time `t`: strictly `< t`.** No bar stamped `t` is readable.
  (Bars are END-stamped, so the bar labelled `09:45` closes *at* 09:45 and is excluded.)
- **The session is the dependence unit**, not the decision. ~1,100 sessions, ~6,600 decisions.

## 3. Feature budget — small, interpretable, fixed

Causal transforms of `$TICK`, `$TRIN`, `$VIX` only, plus NQ state used for normalization:

| # | feature | why |
|---|---|---|
| 1–3 | last level of TICK / TRIN / VIX | current breadth, up/down volume ratio, vol |
| 4–6 | 20-session z-score of each level | regime-relative position |
| 7–8 | TICK 15-min and 30-min change | breadth impulse |
| 9 | VIX 30-min change | vol impulse |
| 10 | TICK extreme occupancy, last 30 min (\|TICK\| > 800) | crowding |
| 11 | TICK sign persistence, last 15 min | breadth trend |
| 12 | internals disagreement: `sign(z_TICK) ≠ sign(−z_TRIN)` | conflicting breadth signals |
| 13 | NQ realized volatility, trailing 30 min | normalization |
| 14 | NQ trailing 30-min return | price state, so internals are tested *incrementally* |
| 15 | time of day | intraday seasonality |

**No feature zoo. No feature search. No P1 action-value labels anywhere.**

## 4. Model budget

- **PRIMARY: one regularized linear model** (Ridge, α = 10.0, fixed — not tuned on test data).
- **At most ONE shallow nonlinear challenger** (HistGradientBoosting, depth 3, 150 iters, lr 0.05).
- **Both attempts counted** and carried into the multiplicity threshold.

## 5. Cost model — frozen before results

Grounded in this repo's own NQ RTH measurement (`MSLAST_CONTRACT`: median quoted RTH spread
**3 ticks**, NQ tick = **$5**, commission **$4.36**/ctrRT):

| | round-trip cost |
|---|---:|
| **PRIMARY** | 3 ticks + commission = **$19.36** |
| **STRESS** | 5 ticks + commission = **$29.36** |

**Policy:** LONG if predicted 60-min move > cost, SHORT if < −cost, else **CASH**. Cash is an
action. The economic target is **after-cost P&L**; directional accuracy is diagnostic only.

## 6. Validation and nulls

- **Expanding-origin chronological session-block** validation, 5 folds. No random row split.
- **Training-only normalization.**
- **Refitted session-block null** — the corrected construction from the MS-LAST repair: whole
  session outcome blocks circularly shifted against feature sessions, every row preserved, folds
  rebuilt, **model refit from scratch inside every replicate**. A null distribution must have
  **≥ 2 distinct values** and its sd is printed (the `np.roll(...).mean()` failure will not recur).
- **Activity-matched random-direction placebo**: same trade times, random side.

## 7. Gates — declared here, all must pass for a candidate to exist

| gate | rule |
|---|---|
| **I1** | out-of-fold session-clustered net P&L per session **> 0** at PRIMARY cost |
| **I2** | observed **> 95th percentile** of the refitted session-block null |
| **I3** | observed **> 95th percentile** of the activity-matched placebo |
| **I4** | net **> 0** at STRESS cost |

**Failure rule.** If any gate fails, the outcome is recorded as **NO CANDIDATE** for this mapping
at this horizon and feature budget. It is **not** generalized to "internals are null", and it does
**not** authorize a horizon sweep, a feature expansion or a model upgrade — each of those is a new
hypothesis needing its own preregistration.

**Power rule.** If the economic test cannot detect an effect of portfolio-relevant size, the verdict
is **CLOSED-BY-POWER**, not NULL. Materiality is declared as in the MS-LAST repair: the incumbent
earns ~**$246/session** at fixed DD; a sleeve worth engineering must reach ~**$49/session** (20 %).
Both are reported against the measured MDE.
