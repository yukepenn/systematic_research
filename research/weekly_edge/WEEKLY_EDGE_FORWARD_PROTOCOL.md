# WEEKLY_EDGE FORWARD PROTOCOL

> ## **Written 2026-08-27, BEFORE any ≥ 2026-08-01 outcome was read.**
> Every checkpoint, metric, expected sign and band below was fixed in advance and committed. That
> is the entire point: **a band chosen after seeing the data is not a band.**

**Governs:** the ≥ 2026-08-01 VIRGIN pool, against the objects frozen in
[`FROZEN_INCUMBENT_20260827.md`](FROZEN_INCUMBENT_20260827.md).
**Seal register:** `research/operational/LOCKED_FORWARD.md`.

> # 🔒 LIVE ENABLED: **NO.** This protocol reads data. It authorises no order and no deployment.

---

## 1. ⚠️ Read this before any checkpoint: what forward evidence CAN and CANNOT do

Derived from the frozen values themselves (weekly $ at fixed DD, $1,230 at t = 4.16 over 213.1
research weeks ⇒ implied weekly sd **$4,317**; Portfolio B $2,012 at t = 4.90 ⇒ sd **$5,995**):

| checkpoint | sessions | expected cum. | what it can actually resolve |
|---|---:|---:|---|
| **A** | 60 (~3 mo) | $13,986 | **t = 0.99.** Resolves essentially nothing about the mean |
| **B** | 126 (~6 mo) | $29,138 | **t = 1.43.** Still cannot confirm |
| **C** | 252 (~1 yr) | $58,276 | **t = 2.02.** Weak confirmation at best |

> ### ⚠️ **A LOSING QUARTER HAS A 14.5 % PROBABILITY IF NOTHING IS WRONG AT ALL.**
> _(empirical bootstrap, `runs/FWD_BOOTSTRAP_20260827/`; the Gaussian said 16.1 %)_
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
positive-week rate (expect **56.3 %** P1 / **59.2 %** B), realised max DD (research $22,931 / $11,489),
trade count vs the research rate, mean $/trade, right-tail retention, time under water, and
**decision agreement** between the Python object and the NT8 executable.

## 4. Preregistered bands — **EMPIRICAL BOOTSTRAP, primary** (amended 2026-08-27, §29)

Weekly P&L is **not Gaussian** and the test says so unambiguously: **skew +1.888, excess kurtosis
8.717, Jarque-Bera p ≈ 1.2 × 10⁻¹⁷⁴ — normality rejected.** Bands are therefore built by
**circular block bootstrap** (B = 40,000, block length 6 weeks, seed 20260827) on the frozen
213-week series, which preserves skew, tails and short serial dependence. See `runs/FWD_BOOTSTRAP_20260827/`.

### `P1/PCT` — PRIMARY

| checkpoint | expected cum. | P(neg) | **HEALTHY** ≥ p25 | **WATCH** p05→p25 | **INVALIDATION** < p01 |
|---|---:|---:|---|---|---|
| CPA — 60 sessions | $13,986 | **14.5 %** | ≥ $4,736 | −$7,185 → $4,736 | **< −$15,585**  _(range −$11,486 … −$15,585)_ |
| CPB — 126 sessions | $29,138 | **6.3 %** | ≥ $15,636 | −$1,986 → $15,636 | **< −$13,657**  _(range −$12,235 … −$14,136)_ |
| CPC — 252 sessions | $58,276 | **1.6 %** | ≥ $39,214 | $13,544 → $39,214 | **< −$4,366**  _(range −$1,533 … −$4,077)_ |

### Gaussian — SECONDARY DIAGNOSTIC ONLY, retained to show what it got wrong

| checkpoint | P(neg) | HEALTHY | WATCH | INVALIDATION | **error in the INVALIDATION band** |
|---|---:|---|---|---|---|
| CPA | 16.1 % | ≥ $4,705 | −$9,772 → $4,705 | < −$19,938 | **$3,482 TOO LOOSE** |
| CPB | 7.7 % | ≥ $16,242 | −$4,654 → $16,242 | < −$19,328 | **$4,908 TOO LOOSE** |
| CPC | 2.2 % | ≥ $40,993 | $11,440 → $40,993 | < −$9,311 | **$4,701 TOO LOOSE** |

> ### ⚠️ **The Gaussian bands erred in the dangerous direction.** Because the return distribution is
> ### **right-skewed**, its left tail is *less* extreme than a Gaussian assumes — so the Gaussian
> ### INVALIDATION threshold sat **$3.5–4.9k too low**, and **a genuinely broken strategy could have
> ### passed it.** The empirical bands trigger earlier and are now primary.

> ### ✅ **RESOLVED 2026-08-27** — `runs/FWD_DD_RECONCILIATION/` found the canonical **$22,931** was computed on a
> **commission-only** stream while the **$1,394** numerator is **net of the modelled spread**. Mixing
> them flattered the headline by **5.2 %**. All bands above now use **`k = 0.836124`**, the frozen
> spread-inclusive stream on **both** sides. `P(neg)` is scale-invariant and unchanged.
>
> ### ⚠️ **THE INVALIDATION THRESHOLD IS NOT A SINGLE NUMBER.** Across preregistered block
> lengths (3 / 6 / 12 weeks) p01 moves by up to **$4,099**. The ranges are shown above and the **most
> forgiving band is NOT selected**. **A result landing inside the range is INCONCLUSIVE, not an
> invalidation** — 40,000 resamples reduce Monte-Carlo noise, they do not create historical
> information.

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

- **a negative CPA** — **14.5 %** likely with nothing wrong (empirical)
- **any single losing week, month, or quarter**
- **a drawdown inside the research max** ($22,931 P1 / $11,489 B)
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
