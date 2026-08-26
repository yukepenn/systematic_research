# OWNER CHARTER — AMENDMENT 1 (issued 2026-08-26, binding, append-only)

Amends `OWNER_CHARTER_20260825.md`. The charter otherwise stands unchanged.

## 1. The correction

The owner's words, verbatim:

> 我也不是很在乎是这五年赚钱。因为可能近两年赚钱可能以后也能赚钱？…别过于 overfit 什么
> 2022-2026 因为不代表以后可以赚钱。甚至说不定有些 edge 近两年才有。

**The requirement that an arm be positive in every year, or "not negative in more than one
year", is WITHDRAWN as a standalone adoption gate.** It was never an owner requirement; I
introduced it and then applied it as if it were physics.

It was wrong in a specific way that is worth naming, because it is the same error the charter
already warns about pointed backwards: **requiring uniform performance across 2022-2026 is
itself a fit to 2022-2026.** A market that changed in 2024 does not owe us a 2022 edge, and an
edge that only exists in the last two years is not thereby less likely to exist next year — it
may be *more* likely, if what created it is still there.

## 2. What replaces it

A recency-concentrated result is admissible. It is **not** automatically admissible: it has to
survive the two things that actually make it doubtful, which uniformity was a crude proxy for.

**(a) Sample adequacy.** "It only works in 2026" is a 106-session claim. State the number of
sessions, weeks and EVENTS in the sub-period, and the standard error of the sub-period estimate.
An edge measured on 100 sessions with 40 trades is a small sample whatever its Sharpe; that is
a statistical objection and it survives the amendment.

**(b) A regime variable, not a date.** A date is not a mechanism. If an arm works recently, the
question is *what changed*, expressed as a **measurable, causally-observable regime variable**
(realised volatility level, term structure, session-range distribution, participation, tick
size and price level, the object's own event rate). Two things must then follow:
  1. the arm's performance must line up with the REGIME variable, not merely with the calendar
     — if it works in every high-volatility stretch including one in 2022, that is a mechanism;
     if it works only after 2025-01-01 regardless of regime, that is a date;
  2. we must be able to say **when it would stop**, from the same variable, causally.

**(c) The walk-forward form of the question, which is the honest one.** Would a causal,
expanding-window process that adopted the arm *when the evidence appeared* have earned money
from that point? That is what live trading would have done. Report it that way. A backtest that
is flat 2022-2025 and strong 2026 earns whatever the walk-forward earned after the switch —
not the full-window average, and not zero.

## 3. Consequences that take effect immediately

- Every adoption bar written in this campaign that contains "not negative in more than one
  year" is replaced by §2 (a)+(b)+(c). Applies to `WE_W51`, `WE_W53`, `WE_W54` and forward.
- **W54's withdrawal of the entry-timing family is PARTIALLY REVERSED.** R2/R2V1 and R2B were
  not promoted for two reasons: (i) a mechanism decomposition that is still valid and still
  argues against delay, and (ii) "the entire headline comes from the 106-session 2026 stub",
  which under this amendment is no longer a rejection by itself. Reason (i) stands on its own,
  so the family stays closed **for now** — but it is now closed on the mechanism evidence
  (R2V1's 93 %-net-cost decomposition, R2B's Spearman −0.32, W31's flip-vs-state 0.0603/0.0025,
  W42's flat-in-horizon bar-5 law), not on the chronology. If a regime variable is found that
  explains 2026, the family reopens under §2.
- A repo-wide re-audit is running to find every arm that was rejected **primarily** for
  non-uniformity rather than for a look-ahead, a failed null, or negative expectancy. Those are
  reopening candidates and each will be re-adjudicated under §2.

## 4. What does NOT change

Everything that catches self-deception stays exactly as it is: spec-first commits,
decision-bar causality, B1 reproduction, circular-shift and count-matched nulls,
exposure-matching in contract-minutes, scan-matched nulls (W53), causal re-derivation of every
threshold, no data ≥ 2026-08-01, and the evidence vocabulary.

This amendment loosens **one** criterion, and it loosens it towards taking the market's word
over mine. It does not loosen any test that protects against taking my own word.
