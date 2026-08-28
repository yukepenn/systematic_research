# MS-BBO-V1 · PREREGISTRATION — committed before any model result

| | |
|---|---|
| **status** | **SPEC + RUNNER COMMITTED BEFORE THE RESULT** |
| date | 2026-08-28 |
| **claim ceiling** | **DISCOVERY-GRADE CANDIDATE ONLY** — no clean BBO historical holdout exists |
| sample | **58 quote-complete v2 sessions**, no truncation |
| seal | ≥ 2026-08-01 excluded by assertion |

---

## 1. The ceiling, stated before the work

Every quote-complete BBO session in this repo has had its price outcomes consumed. **There is no
clean BBO historical holdout and none can be manufactured.** Therefore the *best possible* outcome
of this wave is a **discovery-grade candidate** that must earn real validation **prospectively**.
This run cannot produce "validated", "confirmed", "production-ready" or "live-eligible" alpha, and
those words will not be used about it whatever the numbers say.

## 2. Certified fill contract (`src/fill_contract.py`, timestamps only)

Run **before** any price was read, so the rule below cannot have been tuned on performance.

| leg | missing | median | p99 | worst |
|---|---:|---:|---:|---:|
| entry bid / ask | **0.000 %** | 8.0 ms | 94.8 / 100.8 ms | 964 / 1,352 ms |
| exit bid / ask | **0.000 %** | 8.0 ms | 94.8 / 98.0 ms | 964 / 1,352 ms |

**FROZEN: `MAX_FILL_WAIT = 1,000 ms`.** A decision whose entry *or* exit quote does not arrive
inside the cap is **dropped**, never filled at a stale price. Fill availability is **adequate**
(100.000 % usable upper bound).

**Decision schedule, declared not selected:** RTH, fixed **non-overlapping 60-second grid**,
decisions **10:00:00 → 15:30:00 ET**, horizon **60 s**. Start at 10:00 to exclude the opening
auction and its microstructure initialisation; end at 15:30 so the last holding period closes at
15:31, clear of closing-auction effects. **No time-of-day search.** 331 decisions/session,
**19,198 total**.

## 3. Information vs execution — two different clocks

```
FEATURES   events with timestamp STRICTLY <  t
EXECUTION  first quote at a DISTINCT timestamp >  t      (entry)
           first quote at a DISTINCT timestamp >  t+h    (exit)
```

Neither clock may touch an event stamped **exactly** `t`: same-millisecond ordering is
unrecoverable (MS01A). Where a side has several prices inside one millisecond, the **mean** is used
— permutation-invariant by construction.

**Permanently blocked:** true aggressor side · queue position · quote-then-trade causality inside a
millisecond · displayed-depth absorption · **bid/ask size imbalance** · true microprice · depth
sweep. **Quote VOLUME is not used anywhere. Bid/ask PRICE only.**

## 4. Feature budget — 18, fixed

**F1 mid/price state:** mid returns 1s/5s/15s/30s · 30 s realized vol · 30 s range · distance to
30 s high and low.
**F2 spread state:** current quoted spread (ticks) · 30 s spread change · fraction of the last 30 s
at the minimum spread · spread percentile within the last 30 s.
**F3 quote PRICE update state:** bid and ask distinct-timestamp update counts over 30 s · count of
upward price updates per side.
**F4 order-invariant trade controls:** distinct-timestamp trade buckets · total trade volume ·
bucket-VWAP signed flow (signed against the **prior distinct timestamp**, the construction already
certified permutation-invariant in `MSLAST_CONTRACT`).
Plus time-of-day.

**The rowwise tick rule is NOT reintroduced** — it failed permutation invariance (moved 274 % of
its own value) and stays blocked. Last-only features appear here only as **controls**, not as a
reason to re-run MS-LAST.

## 5. Labels — the actual execution contract

```
long_gross  = (Bid_exit  - Ask_entry) x $20/pt
short_gross = (Bid_entry - Ask_exit ) x $20/pt
commission $4.36 charged EXACTLY ONCE
```

**No extra median spread is subtracted** — real bid/ask sides are already used.
**Stress ladder, declared:** +0.5 and +1.0 tick **per side**, not searched.

## 6. Model and target

**PRIMARY: Ridge (α = 10.0, fixed).** **ONE challenger: shallow GBM** (depth 3, 150 iters, lr 0.05).
**No third model.** Both count toward multiplicity. No hyperparameter selection touches test folds.

**Target:** the future mid move in dollars. **The policy, not the target, applies cost**: LONG if
predicted move exceeds a **causal** threshold (the spread observable strictly before `t`, plus
commission), SHORT if it clears it downward, else **FLAT**. **Primary score is out-of-fold
after-cost net P&L.** Accuracy is diagnostic only.

## 7. Validation and nulls

Chronological **session-block expanding-origin** walk-forward, training-only scaling, **the session
is the dependence unit**. Test sessions never choose model settings.

- **A — session-block outcome-shift null**, full pipeline refit inside every replicate, with an
  assertion that the null has **≥ 2 distinct values**.
- **D — multiplicity:** the null statistic is the **MAX over {Ridge, GBM}**, so the better model is
  never compared against a single-model null.
- **B — activity-matched random-direction placebo** (same timestamps, same trade rate, random side).
- **C — same-trigger mirror**: opposite direction at the candidate's exact timestamps, which tests
  whether the result comes from picking *direction* rather than merely picking profitable moments.

## 8. Gates — all must pass. Fixed here, before the run.

| gate | rule |
|---|---|
| **B1** | OOF PRIMARY after-cost net **> 0** |
| **B2** | **> 95th percentile** of the multiplicity-aware (max-stat) dependence null |
| **B3** | **> 95th percentile** of the activity-matched placebo |
| **B4** | beats the same-trigger opposite-direction mirror |
| **B5** | net **> 0** at STRESS +0.5 tick/side |
| **B6** | **top-5 sessions ≤ 50 %** of net *(concentration criterion declared now, not after seeing the table)* |
| **B7** | net **> 0 in ≥ 3 of 4** equal chronological quartiles |

## 9. Verdict rules

**If any gate fails → MS-BBO-V1 is CLOSED.** Do **not** switch to 30 s or 15 s, add features, add
quote size, add neural models, hand-select hours, choose high-volatility days, invert a losing
strategy, or change the execution model after the fact. **A failed well-designed BBO wave is
evidence**, and the budget moves to an EVI-ranked new surface.

**If all gates pass → `MS-BBO-CANDIDATE-1`**, discovery-grade. Freeze source, features, transforms,
model family, hyperparameters, decision schedule, execution semantics, thresholds, costs and hashes
immediately. **No historical retuning after freeze.** Next stage is **prospective shadow**.
**LIVE remains NO.**
