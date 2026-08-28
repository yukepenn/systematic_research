# PROGRAM B — MISSION AMENDMENT, 2026-08-28

**COMMIT D.** Binding. Supersedes the four-archetype plan in the opening Program-B directive.
**No measurement, no signal, no P&L in this document.**

> ## **THE PREMISE THE CAMPAIGN OPENED WITH HAS BEEN MEASURED AND IS FALSE.**
> The next stage was designed to *clarify* whether the incumbent under-re-enters. The forensic and
> descriptive work **answered that question directly instead**, so the campaign adapts to its own
> data-only result. **This is not a post-hoc rescue** — nothing was rescued, a hypothesis was
> retired, and the replacement is narrower and harder.

---

## 1. ORIGINAL PREMISE

> *"The incumbent is sparse because it does not re-enter often enough during a session. The
> reference trader can enter and exit repeatedly through the day; we cannot."*

## 2. FALSIFICATION — measured, session-clustered, on the frozen object

`baseline_trade_net` by entry ordinal within session, 5,000 bootstrap resamples of **sessions**
(§28: a system taking 8 trades/day does not have 8 independent observations/day):

| ordinal | n | mean/trade | 95 % CI | P(mean > 0) |
|---|---:|---:|---:|---:|
| 1st | 638 | $146.76 | [17, 285] | 0.989 |
| 2nd | 460 | $147.22 | [−19, 363] | 0.953 |
| 3rd | 335 | $66.40 | [−73, 218] | 0.811 |
| 4th–5th | 371 | $145.60 | [9, 300] | 0.982 |
| **6th+** | 327 | **$181.33** | **[24, 375]** | **0.989** |

**`P1/PCT` takes 3.340 trades per active session** (median 3, p90 7, **max 19**), its **5th–8th
entries are its best bucket** ($180.88/trade), hold time **shrinks** with ordinal (37 → 10 min), and
**capping at any K < 8 loses money** (cap 3 costs −$113,312).

> ### **It already re-enters, and the re-entries pay. The original premise is retired.**

⚠️ **The comparison that motivated it also collapsed.** Per hour of available market the incumbent
already **trades 1.43× more often and earns 2.97× more** than the reference trader's own posted
backtest, at **2.07× the edge per trade** and **0.70× the drawdown**. Re-costing his backtest on the
incumbent's cost model cuts his advantage from **1.40× to 1.09×**. His visible advantage is
**session length (≈$1,989/wk) and an uncharged spread (≈$604/wk)** — together more than the whole
posted gap.

## 3. REVISED PREMISE — the binding sparsity

| | |
|---|---|
| ⛔ **not** re-entry | 3.340 trades/active session, later trades are the best |
| ⛔ **not** later-trade decay | ordinals 5–8 are the strongest bucket |
| ⛔ **not** coverage of big moves | correctly scoped, **0.38 %** (`RR_W006`) |
| ⛔ **not** turnover policy | caps are **worse than random** (`WE_W121`) |
| ✅ **GAP A — inactive-session coverage** | **`P1/PCT` is COMPLETELY FLAT on 420 of 1,058 sessions = 39.7 %** |
| ✅ **GAP B — time-window coverage** | it uses **≈6.5 h of the instrument's 23 h** |

## 4. CONSEQUENCE FOR THE ARCHETYPE PLAN

**The generic breakout / pullback / failed-breakout / regime-conditional-mean-reversion set is NOT
run merely because it appeared in an earlier planning document.** That set was explicitly declared
*"subject to reference-trader forensic evidence"*, and the forensic evidence says his advantage is
**hours and friction accounting**, not a richer menu of setups.

Those four remain **possible future hypotheses**, and only if capability work identifies a concrete
reason to study them. **They are not closed; they are not queued either.**

## 5. THE REVISED PROGRAM-B QUESTION

> ### **Can we expand the number of SESSIONS and HOURS in which a one-contract NQ book finds
> ### genuinely positive-EV opportunities, WITHOUT diluting the edge that already exists when
> ### `P1/PCT` is active?**

Two lanes, **independently preregistered**, answering different questions:

| lane | question | ⛔ NOT the question |
|---|---|---|
| **A · FLAT-SESSION COVERAGE** | Is there a causally observable, economically **distinct** state on some P1-flat sessions supporting a **new** engine? | *Can we weaken P1 until it trades?* |
| **B · SESSION-LENGTH COVERAGE** | Are there independently profitable opportunities **outside** P1's window after realistic off-hours spread, friction and tail risk? | *Does trading more hours mechanically create more dollars?* |

## 6. Binding prohibitions carried into every stage

> ### ⛔ **THERE WILL BE NO "LOWER THE P1 THRESHOLD UNTIL FLAT SESSIONS TRADE" EXPERIMENT.**
> That is the cleanest possible form of post-hoc threshold mining. If flat sessions turn out to sit
> near P1's boundary, the finding is recorded as **`P1_NEAR_ARM_STATE EXISTS`** and it motivates a
> *future distinct hypothesis*. It authorises **no** 0.95× / 0.90× / 0.75× threshold, no different
> box, no different sigma, no different Solar weight, and no "P1 aggressive mode".

- **`P1/PCT` stays frozen.** An expansion sleeve is **incremental**: it may not replace, modify,
  weaken, or re-time P1, nor reclassify a P1-active session as flat.
- **One contract remains binding**: `position ∈ {−1, 0, +1}`. P1 + a new sleeve are never counted as
  two simultaneous NQ contracts when answering the practical question.
- **More hours is not more alpha.** Every result reports net per **available** hour, per
  **in-market** hour, and per exposure-hour, so *being invested longer* cannot masquerade as edge.
- **The reference trader is a motivating observation, not a target.** ⛔ Do not optimise toward
  8.26 trades/day. ⛔ Do not attempt visual replication. ⛔ His screenshots are not ground truth, and
  the profitability of *his* later same-day trades is **UNKNOWABLE** from the fixed corpus.

## 7. Errors in this campaign's own earlier measurements — preserved, not hidden

| corrected | from | to | cause |
|---|---|---|---|
| trades/calendar session | 2.27 | **2.014** | numerator was the **whole-substrate 2,401**, including the 2022-01→06 warm-up; the in-window population is **2,131** |
| P1-flat sessions | 282 (26.7 %) | **420 (39.7 %)** | 282 was **BOOK**-flat (neither P1 *nor* XM); P1 alone touches **638** sessions |
| trades/active session | 3.09 | **3.340** | consequence of both |
| active-session count | 712 | **638** | sessions were counted by **`session_date`**, not **`session_id`** |

> ### **THE SCIENTIFIC UNIT OF THIS PROGRAMME IS THE 23-HOUR NQ TRADING SESSION (`session_id`),
> ### NOT THE CIVIL CALENDAR DATE.**
> NQ runs **18:00 → 17:00 ET**, so one trading session spans two calendar dates. Confirmed against
> `WE_W119`'s book ledger: **1,058 unique sessions against 1,056 unique dates.**
> **`research_sdk/test_session_unit.py` now enforces this class of error mechanically.**

## 8. Continuation

`OPPORTUNITY00` is preregistered next, as **data / state capability only** — no candidate P&L, no
outcome-ranked rules, no thresholds chosen from forward returns. Its continuation rules into an
economic V1 are frozen **before** its measurement exists.

**Protected assets unchanged and unspent** — ≥2026-08-01 seal · `ESNQ_BLIND_EFFECTIVE_14` ·
NQ BBO 19 · 20 unread ES BBO · 141-session Last-only pool.
**The prospective shadow clock is unaffected**: `SHADOW_START = 2026-09-01 18:00 ET`, not moved
backward, not backfilled. Research clock and evidence clock run in parallel.

**LIVE ENABLED = NO.**
