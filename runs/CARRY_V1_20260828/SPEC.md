# SPEC — `CARRY_V1` · ONE within-sector relative-carry specification

**Committed BEFORE any carry P&L exists.** One primary design. **No carry zoo.**

| | |
|---|---|
| **family** | multi-market **CURVE / TERM STRUCTURE** — a genuinely different information source |
| **what it is NOT** | **not TSMOM V3, not a TSMOM rescue, not a different trend length.** TSMOM's failure is not evidence about carry, in either direction |
| universe | **10 roots · 4 sectors**, fixed by `CARRY00` on **coverage alone**: ES YM · ZN ZB · GC SI · ZC ZW ZM ZL |
| **attempt budget** | **ONE primary specification. Zero challengers.** Every cell tried against outcome data is selection debt |
| **LIVE ENABLED** | **NO** |

---

## 1. Signal — one formula, chosen for robustness before any result

```
curve_slope_i,t  =  (P_near_i,t  -  P_deferred_i,t) / month_gap_i,t

carry_score_i,t  =  curve_slope_i,t / sigma_i,t          sigma = LAGGED 63-day sd of the
                                                          basis-safe daily price change
```

**Why this and not a log or a ratio.** April 2020 put CL below zero; `log(P_near/P_def)` is
undefined there and a ratio explodes near zero. A **difference** is defined for every price a
futures market can print. Dividing by `month_gap` makes a 1-month commodity spread comparable to a
3-month financial spread — `CARRY00` measured that gaps are **not** uniform across sectors, so this
is a required correction, not a flourish. Dividing by lagged σ expresses the slope in **units of
that root's normal daily risk**, removing price-level scale.

**σ reuses the already-tested 63-day lagged volatility** from the TSMOM substrate. Reusing a
tested estimator is not a free parameter; inventing a carry-specific one after seeing results would
be. **The formula does not change after performance.** If implementation reality forces a different
definition, it is resolved and committed **before** any P&L.

## 2. Architecture — WITHIN-SECTOR RELATIVE, not global direction

At each rebalance, `carry_score` is **centred-ranked inside each sector** to `[−1, +1]`:

```
w_raw_i  =  2 * (rank_i - 1) / (n_sector - 1) - 1        for n_sector >= 2, ranks ascending
```

Long relatively high-carry roots, short relatively low-carry roots, **within the sector**.

> ### A single absolute zero-carry threshold across equity, rates, metals and ags would encode
> ### **financing and storage conventions**, not expected return. Equities are in contango
> ### essentially always because the curve carries interest; that is not a forecast. Sector-relative
> ### ranking removes the permanent sector level, most of global beta, and the obvious
> ### equity/rates sign bias — and it makes `C8` (not-a-disguised-long) a meaningful gate rather
> ### than a formality.

**A fixed deterministic transform, chosen now.** No z-score-vs-rank-vs-threshold comparison after
seeing P&L.

## 3. Sector rule (§40)

A sector participates only with **≥ 2** carry-capable roots **that have a valid pair on that
rebalance date**. Otherwise the sector is **CASH** for that rebalance. **No root is borrowed from
another sector. No root is deleted for its result.**

## 4. Rebalance — ONE frequency

**WEEKLY.** Weights for an ISO week are determined **entirely from information through the
immediately preceding eligible session**. No weekly-vs-monthly shootout: if weekly is chosen,
**weekly stays.** Carry is a slow signal and `CARRY00` showed some pairs coexist for as little as
one day, so a daily-churn design would pay turnover for noise.

## 5. Causality — with teeth

For a position applied on date `t`, **every** input satisfies `information timestamp ≤ prior
eligible close`. The perturbation gate is blocking and symmetric:

| probe | required |
|---|---|
| corrupt **future** date-`t` prices | weights for `t` **MUST NOT** change |
| corrupt **`t−1`** curve state | weights for `t` **MUST** change |

**A causality probe that only tests one direction has no teeth** — it cannot distinguish a causal
engine from one that ignores its inputs. Both clauses are asserted in code.

⚠️ **This gate is not a formality today.** Hours ago an `int32` overflow made seven BBO features read
**+2.065 s into the future** while every summary statistic looked excellent. The engine must be
*proved* causal, not assumed.

## 6. Risk sizing and portfolio construction

Strictly **lagged 63-day** volatility. **Equal risk across active sectors**, then risk-normalised
roots inside each sector. **No optimizer. No Markowitz. No ex-post covariance. No full-sample
inverse-vol weight.** Fractional research sizing is acceptable and is labelled research sizing.

## 7. Costs — and turnover is a mandatory diagnostic, not a footnote

Actual per-contract tick values. **Primary: $4.36 RT commission + 1 tick** of realistic friction.
**Stress: 2 ticks.** Costs are charged to **actual position changes only**, never to unchanged
holdings.

**Reported every time:** gross · costs · net · **cost / gross** · turnover.

> **TSMOM V1 was gross-positive and economically dead**: cost drag **47.2 % of gross**, and it was
> scale-invariant, so no sizing change could rescue it. That diagnostic is mandatory here.

## 8. Protected chronology — and the honest name for it

| window | role |
|---|---|
| **2009 → 2018** | DEVELOPMENT |
| **2019 → 2022** | VALIDATION — unreachable until the development verdict is committed |
| **2023 → 2026-05-30** | FINAL FAMILY HOLDOUT — unreachable until validation is committed |

> ### These windows are **FAMILY-SPECIFIC UNREAD CARRY OUTPUT**, not pristine market history.
> These markets have been examined for **other** families. The defensible claim is narrow and exact:
> **carry signal and carry P&L were never computed on these dates before their protected read.**
> Calling it "unseen data" would be false and is refused here.

**Protection is structural, not advisory.** The development runner asserts
`max(evaluated date) < 2019-01-01`. No "load the full frame and filter later" — the later windows
are unreachable from the development code path.

## 9. Development gates — frozen before the result, all must pass

| gate | requirement |
|---|---|
| **C1** | PRIMARY net > 0 |
| **C2** | annualized Sharpe ≥ **0.30** |
| **C3** | positive in **≥ 6 of 9** complete development years (2010–2018; 2009 is warmup) |
| **C4** | STRESS (2 ticks) net > 0 |
| **C5** | cost drag ≤ **50 %** of gross positive economics |
| **C6** | no single root contributes > **40 %** of positive total contribution |
| **C7** | no single sector contributes > **50 %** of positive total contribution |
| **C8** | **not a disguised persistent long-equity position** — realized mean signed exposure to equity_index within ±0.25 of zero, and \|weekly ρ with `P1/PCT`\| < 0.35 |

**No gate is added, removed or altered after the result.** C3's denominator is fixed now: **9 years,
2010–2018**, with 2009 consumed by the 63-day σ warmup and the roll ledger's initialisation.

## 10. Continuation — pre-committed so no result can be rescued

| outcome | action |
|---|---|
| **all gates pass** | commit the development verdict → **one-shot** validation read, same frozen object |
| **any blocking gate fails** | **`CARRY_V1` CLOSED.** Move on |

**On failure, explicitly forbidden:** monthly rebalance · 2-week rebalance · 3-month slope ·
second-vs-third contract · long-only · commodity-only · drop metals · drop ags · thresholded carry ·
blended carry/trend · a second rank transform. **Those are a search after failure.** A genuinely new
V2 would need new information, its own preregistration and an explicit multiplicity debt, and it
would have to win an EVI comparison against every other family. **Default: move on to ES↔NQ.**
