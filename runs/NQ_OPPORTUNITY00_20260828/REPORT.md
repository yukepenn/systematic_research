# `NQ_OPPORTUNITY00` — RESULT

> ## ⚠️ **SCOPE CORRECTION, added 2026-08-28 (Program C §3). THE TEXT BELOW IS UNCHANGED.**
> §4 of this report says **"`OPPORTUNITY00` found no third family."** That wording is **too
> strong** and is corrected here rather than edited away.
>
> ### **What was established:** *no third **admissible** state family was identified **within the
> ### currently owned and examined information surface**, under this run's **preregistered** rules.*
>
> **What was NOT established, and must never be quoted from this report:**
> ⛔ that no other transformation of market history can ever work · ⛔ that no unknown causal state
> exists · ⛔ that flat sessions are unpredictable · ⛔ that price-derived information is universally
> exhausted · ⛔ that opportunity-density research is permanently closed.
>
> **The defensible consequence is narrower and is the one that binds:** *continuing to modify the
> same incumbent state machine is no longer a high-EVI research direction.* The two disqualified
> families were disqualified **by governance** (forbidden threshold mining; a 5×-falsified object),
> **not by a proof of non-existence** — and the search space examined was **the incumbent's own
> arming structure**, not the space of all observables.
>

Executes `SPEC.md`, committed at `f62575f` **before this measurement existed**.
**No candidate P&L, no model, no rule ranked by subsequent return was computed.**

> # **VERDICT**
> ## LANE A · **`FLAT-SESSIONS CONTAIN MATERIAL MOVEMENT BUT P1 DOES NOT ARM`**
> ## LANE B · **`OFF-HOURS ALREADY TRADED (NOT A GAP)`** + **`B-QUOTE CLOSED-BY-DATA/POWER`**
> ## → **NEITHER LANE PROCEEDS TO AN ECONOMIC V1. Lane A closes at `A-C2`.**
>
> **The 39.7 % coverage hole is REAL and the market moves through it.** What is missing is not
> opportunity — it is **an instrument to see it that is neither a loosened `P1` nor the
> already-falsified short leg.**

---

## 0. Engine certification — the decomposition is the frozen object, exactly

The arming identity was re-derived and checked against the frozen `votes()` on **every bar**:

```
K · g · (1 + dL) >= 16        disagreements: 0 of 1,620,044 bars
```

Long leg armed on **275,855 bars (17.03 %)**, short leg on **252,479 (15.58 %)**, **overlap exactly
0**. Population asserted in code and cross-checked against a second artifact: **1,058 sessions ·
638 active · 420 flat**, with the book ledger's own `p1_pnl != 0` count independently returning 638.
Seal asserted: max bar **2026-07-31 16:59**.

## 1. Q1 — Why exactly is P1 flat on 420 sessions?

**Mutually exclusive, fixed precedence, from the code:**

| cause | sessions | share | median session range |
|---|---:|---:|---:|
| **`K_max = 0`** — no member set ever went long | **252** | **60.0 %** | **$5,762** |
| `K_max = 1` — one set only; max attainable vote `1·4·2 = 8/32 = 0.25` | 86 | 20.5 % | $5,465 |
| `g_max = 1` — throttle wall all session | 3 | 0.7 % | $3,825 |
| **`NEAR`** — `K ≥ 2` and `g ≥ 2`, product never reached 16 | 79 | 18.8 % | $4,135 |

**Four in five flat sessions (338) fail on `K` alone** — the solar ensemble's hysteresis never
carried two of four member sets long. **The throttle explains 3 sessions. Time-of-day gates explain
none.**

## 2. ⭐ Q2 — Are flat sessions quieter? **NO. Barely distinguishable.**

| statistic | FLAT median | ACTIVE median | ratio |
|---|---:|---:|---:|
| realised range (pts) | **263.88** | 314.25 | **0.84** |
| path length (pts) | **4,181.25** | 4,561.88 | **0.92** |
| realised variation (pts) | **178.19** | 194.26 | **0.92** |
| **40-tick directional changes** | **95.00** | 106.00 | **0.90** |
| bars | 1,380 | 1,380 | 1.00 |

- **77.9 %** of flat sessions reach **≥ 60 %** of the median *active* session's range — against a
  preregistered bar of **40 %**. **`A-C1` PASSES decisively.**
- **100 % of flat sessions contain ≥ 3 forty-tick directional changes** (≥ $200 of reversal each).

> ### **A session on which `P1/PCT` never trades still travels ~4,180 points, reverses by ten points
> ### ninety-five times, and covers 84 % of a trading session's range. These are not dead days.**
> ### **The 39.7 % hole is not empty. We are simply blind to it.**

## 3. Q3 — How close does P1 come? Two answers, and the second is the honest one

**In vote space: `0.0 %` of flat sessions come within 10 % of the boundary — and that metric is
structurally degenerate.** `K·g·(1+dL)` is a coarse integer lattice; the largest attainable
non-arming product is **12**, i.e. `vote = 0.75`. **Nothing can sit in the 0.9–1.0 band.** Reported
and then discarded as uninformative rather than quoted as "no session comes close".

**In `M` space — the real continuum:**

| | FLAT | ACTIVE |
|---|---:|---:|
| median `M_max` (entry threshold **3.0**) | **2.830** | 7.790 |
| never reached `M ≥ 3.0` on any member set | **252 = 60.0 %** | — |

> ### ⚠️ **`2.830` IS NOT A COINCIDENCE. `M = 0.7086·Tp + 2.83·chan`, so `M_max = 2.830` means the
> ### B-MOM channel fired and the solar ensemble contributed EXACTLY ZERO (`Tp = 0`).**
> ### **The median flat session lands `0.170` below the threshold with one of the two inputs saying
> ### nothing at all.**
>
> **That is a structural description, not an opportunity.** `M = 2.83` is not "almost a signal" — it
> is *one input fired, the other was silent*. **`P1_NEAR_ARM_STATE EXISTS` is recorded.**

## 4. ⛔ Q4 — Is there a distinct causal state family worth an alpha test? **NO. `A-C2` FAILS.**

Only two state families are identifiable on the flat population, and **both were disqualified in
advance, in the SPEC, before this measurement**:

| family | reach | why it is disqualified |
|---|---:|---|
| **the entry threshold** | lowering `3.0 → 1.0` takes flats **420 → 145** and trades 2,401 → 4,840 | ⛔ **THRESHOLD MINING.** §A5 forbids it absolutely — no 0.95× / 0.90× / 0.75×, no different box, no different sigma, no "P1 aggressive mode" |
| **the mirrored short leg** | armed on **343 of 420 flat sessions = 81.7 %** | ⛔ **ALREADY FALSIFIED FIVE TIMES** (W38/39/61/75/78). It builds `NETFUSE_1`, listed **DEAD / FALSIFIED**; W91 measured *"the mirrored Solar vote is worth NOTHING short"*, and B-MOM supplies 89.5 % of that sleeve's entire net |

**`OPPORTUNITY00` found no third family.** Manufacturing one would require a new feature zoo, which
the amendment forbids and which would be a fresh campaign with its own preregistration.

## 5. Q5 — What fraction of the hole could be addressed?

**NOT DETERMINABLE — and that is the correct answer, not an evasion.** `A-C4` asks how often an
*admissible* state occurs. **No admissible state family exists (§4), so the question has no
denominator.** ⛔ No number is manufactured for it.

## 6. Q6–Q9 — Lane B, pre-closed in the SPEC

**B-bar:** the substrate carries the **full 23-hour session** (1,380 bars median; the only missing
60 minutes are the 17:01–18:00 CME break; non-zero volume in all 24 hour buckets), P1 has **no RTH
gate anywhere in `votes()`**, and **63.3 % of its entries already fill outside RTH**.
**There was never an off-hours gap.**
**B-quote:** **9.8 %** session coverage, no NQ quotes before **2025-08-10**, already
`CLOSED-BY-POWER`, and the one protected falsifier carries **day labels 01–17 only** — it covers ET
00:00–16:59 and **none of 18:00–23:59**, so it cannot falsify an evening mechanism at all.

## 7. Q10 — Which lanes proceed? **Neither.**

| gate | observed | |
|---|---:|:--|
| **A-C1** ≥40 % of flat sessions reach ≥60 % of median active range | **77.9 %** | ✅ **PASS** |
| **A-C2** a state family that is not threshold-loosening and not the falsified short leg | **none found** | ⛔ **FAIL — decisive** |
| **A-C3** causally computable from certified fields | yes | ✅ PASS |
| **A-C4** occurs on ≥85 of 1,058 sessions | **no denominator** | **NOT ADJUDICATED** |
| **A-C5** a mechanism stateable before returns | **none to state** | ⛔ FAIL |

> ## **`OPPORTUNITY-DENSITY BOTTLENECK MEASURED; NO CURRENT FREE DATA-CAPABLE EXPANSION LANE.`**

⛔ **Per §24, no new archetypes are invented in this campaign.** ⛔ **Per §39, no outcome-driven
rescue**: no morning-only, no high-vol-only, no wider stop, no reversed sign, no adjacent window.

## 8. What this bought, and it is not nothing

**A negative that is precisely located.** Before this run, "the incumbent is sparse" had three
candidate explanations. Now:

| | |
|---|---|
| ⛔ it under-re-enters | **false** — 3.340 trades/active session, later trades its best |
| ⛔ it ignores 16 hours a day | **false** — it trades 23 of 24 hours, 63.3 % of entries outside RTH |
| ⛔ the flat sessions are dead | **false** — 84–92 % of active path geometry, 95 ten-point reversals each |
| ✅ **the arming instrument is blind on 39.7 % of sessions** | **and the two ways to un-blind it are both already closed** |

> ### **The bottleneck is INFORMATION, not policy, not clock, and not turnover.**
> This is the same wall `RR_W002A` hit from the other side: *no tested current information surface
> separates P1 action quality.* Program B now says the matching thing about **coverage** — and the
> two together mean **the next real gain requires an input this repo does not yet have**, not a
> rearrangement of the ones it does.

## 9. Protected assets — untouched

⛔ ≥2026-08-01 seal (asserted, max bar 2026-07-31 16:59) · `ESNQ_BLIND_EFFECTIVE_14` · NQ BBO 19 ·
20 unread ES BBO · 141-session Last-only pool · the 21 ungoverned evening-only quote dates.
**This run opened no quote file.** ⚠️ Newly recorded: **`EFFECTIVE_14` is a strict subset of the
BBO 19 — they are not two independent shots.**

**LIVE ENABLED = NO.**
