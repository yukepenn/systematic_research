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
| **A** | 60 (~3 mo) | $14,760 | **t = 0.99.** Resolves essentially nothing about the mean |
| **B** | 126 (~6 mo) | $30,996 | **t = 1.43.** Still cannot confirm |
| **C** | 252 (~1 yr) | $61,992 | **t = 2.02.** Weak confirmation at best |

> ### ⚠️ **A LOSING QUARTER HAS A 16.2 % PROBABILITY IF NOTHING IS WRONG AT ALL.**
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

## 4. Preregistered bands — percentiles of the research-implied distribution

| checkpoint | expected cum. | resolving power | **HEALTHY** | **WATCH** | **INVALIDATION** |
|---|---:|---|---|---|---|
| **`P1/PCT`** | | | | | |
| CPA — 60 sessions | $14,760 | t=0.99 · P(neg)=16.2 % | ≥ $4,674 | −$9,837 → $4,674 | **< −$20,026** |
| CPB — 126 sessions | $30,996 | t=1.43 · P(neg)=7.6 % | ≥ $16,380 | −$4,648 → $16,380 | **< −$19,414** |
| CPC — 252 sessions | $61,992 | t=2.02 · P(neg)=2.2 % | ≥ $41,322 | $11,584 → $41,322 | **< −$9,298** |
| **Portfolio B** | | | | | |
| CPA — 60 sessions | $24,144 | t=1.16 · P(neg)=12.2 % | ≥ $10,137 | −$10,014 → $10,137 | **< −$24,165** |
| CPB — 126 sessions | $50,702 | t=1.68 · P(neg)=4.6 % | ≥ $30,405 | $1,202 → $30,405 | **< −$19,303** |
| CPC — 252 sessions | $101,405 | t=2.38 · P(neg)=0.9 % | ≥ $72,699 | $31,401 → $72,699 | **< $2,402** |

**HEALTHY** = at or above the 25th percentile · **WATCH** = 5th–25th · **INVESTIGATE** = 1st–5th ·
**INVALIDATION** = below the **1st percentile** of what the frozen object itself predicts.

⚠️ **Portfolio B's bands are advisory only.** B is a *research* weighting; **no integer-contract
mapping exists** (`OQ-6`), so no live or shadow book reproduces B. Comparing a component-set result
to B's band is a category error — see `FROZEN_INCUMBENT` §1.

## 5. What each band triggers — and what it explicitly does NOT

| band | action |
|---|---|
| **HEALTHY** | record, continue. **No change of any kind.** |
| **WATCH** | record, continue. Note it in `CURRENT_BASELINE`. **No investigation is owed** — this band is inside normal variation |
| **INVESTIGATE** | a **diagnostic** run: is the shortfall in decisions, fills, costs, or regime? **Diagnosis only** |
| **INVALIDATION** | the frozen object has failed its own preregistered bar. Record it. **Opening a new campaign is an owner decision** |

### ⚠️ Explicit NON-triggers — none of these may cause a parameter change

- **a negative CPA** — 16.2 % likely with nothing wrong
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
