# WEEKLY_EDGE FORWARD PROTOCOL

> ## **Written 2026-08-27, BEFORE any ≥ 2026-08-01 outcome was read.**
> Every checkpoint, metric, expected sign and band below was fixed in advance and committed. That
> is the entire point: **a band chosen after seeing the data is not a band.**

**Governs:** the ≥ 2026-08-01 VIRGIN pool, against the objects frozen in
[`FROZEN_INCUMBENT_20260827.md`](FROZEN_INCUMBENT_20260827.md).
**Seal register:** `research/operational/LOCKED_FORWARD.md`.

> # 🔒 **This protocol reads data. It authorises no order and no deployment.**
> *(The repo-wide "LIVE ENABLED: NO" prefix is removed — a live real-money book exists on account
> `2047681` since 2026-09-01. This protocol simply is not it.)*

---

## 1. ⚠️ Read this before any checkpoint: what forward evidence CAN and CANNOT do

Derived from the frozen values themselves (weekly $ at fixed DD, **$1,230** at t = 4.16 over 213
ISO research weeks, `k = 0.882879`. **No Portfolio B band is quoted** — see §4):

| checkpoint | sessions | expected cum. | what it can actually resolve |
|---|---:|---:|---|
| **A** | 60 (~3 mo) | $14,764 | **t = 1.03.** Resolves essentially nothing about the mean |
| **B** | 126 (~6 mo) | $30,759 | **t = 1.49.** Still cannot confirm |
| **C** | 252 (~1 yr) | $61,518 | **t = 2.10.** Weak confirmation at best |

> ### ⚠️ **A LOSING QUARTER HAS A 13.9 % PROBABILITY IF NOTHING IS WRONG AT ALL.**
> _(empirical bootstrap, `runs/FWD_BOOTSTRAP_20260827/`; the Gaussian said 16.2 %)_
> ### **No checkpoint here can CONFIRM the edge. They exist to detect GROSS BREAKAGE.**
> Anyone reading a negative CPA as evidence against the strategy is reading noise. This is stated
> **first**, in advance, because the temptation to over-read the first quarter is the single most
> likely way this protocol gets abused.

## 2. Checkpoints — triggered by SESSION COUNT, not by date

Sessions counted from **2026-08-01** inclusive, using `research_sdk/session_boundary.py`.
As of 2026-08-27 roughly **19** have elapsed, so CPA is not due.

| | trigger | approx. |
|---|---|---|
| **CPA** | 60 sessions | ~2026-10-27 |
| **CPB** | 126 sessions | ~2027-02 |
| **CPC** | 252 sessions | ~2027-08 |

**Read the pool only at a checkpoint.** No continuous peeking, no "quick look", no partial reads.
An unscheduled read burns the seal and must be recorded in `LOCKED_FORWARD.md` as a burn.

### XM has its own gate — session count is not enough

`XM_CONFLICT` produced **346 trades over 213 weeks ≈ 1.6/week**, so CPA yields only **~19 trades**.

> **No strong statement about XM may be made below 50 realised XM trades**, whichever checkpoint
> that falls in. Below that, XM is reported as **UNDERPOWERED — NO VERDICT**, exactly as the event
> lane is. Sample size does not become adequate because a calendar date arrived.

## 3. Primary metric, fixed in advance

**Cumulative $ at the frozen fixed-$20,245-DD scaling**, on the frozen cost model
($4.36/ctrRT commission **plus** modelled spread — P1 $14.44, XM $12.50).

**Expected sign: POSITIVE.** Secondary metrics, all reported, none of them the decider:
positive-week rate (expect **56.3 %** P1 / 59.2 % B), realised max DD (research **$22,931** P1 / $11,489 B, ISO-week basis),
trade count vs the research rate, mean $/trade, right-tail retention, time under water, and
**decision agreement** between the Python object and the NT8 executable.

## 4. Preregistered bands — **EMPIRICAL BOOTSTRAP, primary** (amended 2026-08-27, §29)

Weekly P&L is **not Gaussian** and the test says so unambiguously: **skew +1.888, excess kurtosis
8.717, Jarque-Bera p ≈ 1.2 × 10⁻¹⁷⁴ — normality rejected.** Bands are therefore built by
**circular block bootstrap** (B = 40,000, block length 6 weeks, seed 20260827) on the frozen
213-week series, which preserves skew, tails and short serial dependence.
⚠️ **Bands below are `FWD_BOOTSTRAP_V2` (`B = 600,000`, MC SE ≤ $250 by a rule declared
before measurement). `runs/FWD_BOOTSTRAP_20260827/`'s bands are SUPERSEDED** — its "primary" and
"sensitivity" p01 at the same block length were two independent draws, and its `B = 40,000`
carried ±$200–450 of undisclosed simulation noise. See `runs/FWD_BOOTSTRAP_V2_20260827/`.

### `P1/PCT` — PRIMARY

| checkpoint | expected cum. | P(neg) | **HEALTHY** ≥ p25 | **WATCH** p05→p25 | **INVALIDATION** < p01 |
|---|---:|---:|---|---|---|
| CPA — 60 sessions | $14,764 | **13.9 %** | ≥ $5,118 | −$6,786 → $5,118 | **< −$14,805**  _(block-length range −$11,936 … −$14,805)_ |
| CPB — 126 sessions | $30,759 | **5.7 %** | ≥ $16,786 | −$1,134 → $16,786 | **< −$13,231**  _(range −$12,284 … −$13,231)_ |
| CPC — 252 sessions | $61,518 | **1.2 %** | ≥ $41,868 | $15,837 → $41,868 | **< −$1,688**  _(range −$601 … −$1,688)_ |

### Gaussian — SECONDARY DIAGNOSTIC ONLY, retained to show what it got wrong

| checkpoint | P(neg) | HEALTHY | WATCH | INVALIDATION | **error in the INVALIDATION band** |
|---|---:|---|---|---|---|
| CPA | 16.2 % | ≥ $4,687 | −$9,810 → $4,687 | < −$19,990 | **$5,185 TOO LOOSE** |
| CPB | 7.7 % | ≥ $16,214 | −$4,711 → $16,214 | < −$19,404 | **$6,173 TOO LOOSE** |
| CPC | 2.2 % | ≥ $40,949 | $11,356 → $40,949 | < −$9,424 | **$7,736 TOO LOOSE** |

> ### ⚠️ **The Gaussian bands erred in the dangerous direction.** Because the return distribution is
> ### **right-skewed**, its left tail is *less* extreme than a Gaussian assumes — so the Gaussian
> ### INVALIDATION threshold sat **$5.2–7.7k too low**, and **a genuinely broken strategy could have
> ### passed it.** The empirical bands trigger earlier and are now primary.

> ### ✅ **RESOLVED 2026-08-27, and the first resolution was WRONG.**
> `runs/FWD_DD_RECONCILIATION/` briefly claimed the canonical $22,931 was a commission-only
> drawdown; **that was retracted the same day.** Both $1,394 and $22,931 come from the same
> net series (`WE_W103_CONSOLIDATE`, ISO week on session date), reproducing **$22,930.67** and
> **$1,230.36/wk**. Bands use **`k = 0.882879`**.
>
> ### ⚠️ **BUCKETING IS BINDING ON THE FORWARD READ.** The same trades under a
> Sunday-ending week label give maxDD **$24,212.92** instead of $22,930.67 — **5.6 % from
> week-boundary placement alone.** **The forward read MUST bucket by ISO week on session
> date**, or it compares a realised drawdown against a threshold built on another convention.
>
> ### ⚠️ **THE INVALIDATION THRESHOLD IS NOT A SINGLE NUMBER.** Across preregistered block
> lengths (3 / 6 / 12 weeks) p01 moves by up to **$2,869** (at CPA). The ranges are shown above and
> the **most forgiving band is NOT selected**. **A result landing inside the range is INCONCLUSIVE,
> not an invalidation.**
>
> ### ✅ **AND THAT SPREAD IS NOW KNOWN TO BE REAL, WHICH V1 COULD NOT ESTABLISH.**
> `FWD_BOOTSTRAP_V2` measured the Monte-Carlo error directly (40 independent batches) instead of
> assuming it away. At `B = 40,000` the MC sd of p01 reached **$444** — **larger than V1's own
> claimed CPC block-length spread of $568**, so that cell was reporting noise. At `B = 600,000` the
> noise floor is $69–104 and the spreads are **10–41×** it. **The conclusion was right; the
> evidence for it was not.** The old **$4,099** figure is withdrawn — it came from the
> pre-canonical weekly series.
>
> ### ⚠️ **CPA's range is driven by a DEGENERATE cell and this is disclosed, not hidden.**
> At CPA, `L = 12` over a 12-week horizon is **one block**, so the sampler enumerates the **213**
> twelve-week windows in the record rather than resampling. Its percentiles are *quantized* and no
> number of replicates changes that. −$11,936 is the 2nd-worst of 213 historical windows.

**HEALTHY** = at or above the 25th percentile · **WATCH** = 5th–25th · **INVESTIGATE** = 1st–5th ·
**INVALIDATION** = below the **1st percentile** of what the frozen object itself predicts.

⚠️ **Portfolio B has NO empirical bands yet.** Its Gaussian figures from the first version
(CPA $24,144 / CPB $50,702 / CPC $101,405 expected) are **withdrawn as bands** and retained only as
expectations, because the bootstrap has not been run on a B weekly series. **B's bands are advisory
in any case**: B is a *research* weighting, **no integer-contract mapping exists** (`OQ-6`), so no
live or shadow book reproduces B, and comparing a component-set result to B's band is a category
error — see `FROZEN_INCUMBENT` §1.

## 5. What each band triggers — and what it explicitly does NOT

| band | action |
|---|---|
| **HEALTHY** | record, continue. **No change of any kind.** |
| **WATCH** | record, continue. Note it in `CURRENT_BASELINE`. **No investigation is owed** — this band is inside normal variation |
| **INVESTIGATE** | a **diagnostic** run: is the shortfall in decisions, fills, costs, or regime? **Diagnosis only** |
| **INVALIDATION** | the frozen object has failed its own preregistered bar. Record it. **Opening a new campaign is an owner decision** |

### ⚠️ Explicit NON-triggers — none of these may cause a parameter change

- **a negative CPA** — **13.9 %** likely with nothing wrong (empirical)
- **any single losing week, month, or quarter**
- **a drawdown inside the research max** ($22,931 P1 / $11,489 B) — ⚠️ **these are RESEARCH / PAPER
  thresholds at full 1-NQ size and are NOT live-account trip-wires.** At the live `MnqPerNq = 3`
  scale divide every dollar threshold by 3.33 (≈ $6,879 / ≈ $3,447). **As written, losing the entire
  $10,206.86 live account would be "inside the research max" and an explicit NON-trigger.**
  🔴 **No live-book drawdown trip-wire exists anywhere in this repo.** That gap belongs to
  `research/operational/CURRENT_LIVE_TRUTH.md` / `OWNER_QUEUE.md` OQ-7, not to this protocol.
- **XM being quiet** — it trades ~1.6×/week and silence is its normal state
- **old-regime underperformance** — owner doctrine, post-W115: *old-regime failure is a RISK
  CLASSIFICATION, not a promotion veto*
- **any comparison to a candidate discovered after 2026-08-27**

> ### **No forward result may be used to retune these objects. Ever.**
> Forward evidence can **invalidate** a frozen object or **fail to**. It cannot improve one. The
> moment a forward outcome adjusts a parameter, the pool stops being forward evidence and becomes
> in-sample — and it cannot be un-burned. **A failing gate is recorded failed** (`CLAUDE.md` §4).

## 6. Reporting

Each checkpoint gets `runs/WE_FORWARD_CP<A|B|C>_<date>/` with `spec.yaml` **committed before
results exist** (`prereg_guard.py`), a program-printed **GATE / SPEC / OBSERVED / PASS-FAIL** table
never assembled by hand, every metric tagged **FORWARD**, and an update to `LOCKED_FORWARD.md`
recording exactly which sessions were consumed.

## 7. Prospective shadow — separate evidence, separate ledger

Directive §21 authorises a **prospective** forward shadow on `Backtest` / `Playback` / `Sim101` —
**never a real-money account**. It records strategy, source hash, git hash, instrument, contract,
connection, account, parameters, session template, quantity, risk settings, cost assumptions and
start timestamp; then per decision: timestamp, signal, desired position, simulated fill, bid, ask,
spread, slippage, quantity, exit, realised P&L, MAE, MFE, and any error, disconnect or data gap.

> **Prospective only. Historical trades are never backfilled into this ledger**, and shadow evidence
> is **not** a substitute for the sealed-pool read — it measures **execution**, not edge.
