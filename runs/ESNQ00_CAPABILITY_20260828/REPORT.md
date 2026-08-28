# ESNQ00 — capability measured. **59 overlapping sessions exist. The lane is alive but its
# QUESTION is void, and its power is NOT established.**

| | |
|---|---|
| **what this is** | a **disk inventory**. No outcome data was read, no model fitted, no gate evaluated |
| **why no prereg** | nothing was tested against outcomes, so preregistration does not bind. **An `ESNQ_V1` would need a full one** |
| **capability** | ✅ **59 sessions with complete RTH Bid+Ask+Last on BOTH ES and NQ**, all pre-seal |
| **the blocker** | ⛔ **the question §52 asks has lost its object** — its baseline, the frozen NQ-only BBO set, was **voided today** |
| **power** | ⚠️ **NOT ESTABLISHED, and deliberately not faked** |

---

## 1. Exact current disk truth — measured today, not copied from an old count

NT8 `db/tick`, requiring `Bid`, `Ask` **and** `Last` present for RTH hours 09–16 ET on the session
date (covers the 10:00–15:30 grid, the 30 s feature warmup, and the 15:31 exit):

| | days | span |
|---|---:|---|
| **NQ** RTH-complete | **123** | 2025-08-13 → 2026-08-11 |
| **ES** RTH-complete | **64** | 2025-08-13 → 2026-07-15 |
| **BOTH** (the ES↔NQ universe) | **59** | 2025-08-13 → 2026-07-15 |
| of those, pre-seal | **59** | all of them |
| of those, already exported to the v2 substrate | **7** | |
| **never exported** | **52** | |

**The test validates against a known answer**: all **58 of 58** exported v2 sessions pass it, and
none fail. A completeness criterion that disagreed with the substrate it is supposed to describe
would not be usable.

| contract | RTH-complete days | Bid | Ask | Last |
|---|---:|---:|---:|---:|
| ES 09-25 · 12-25 · 03-26 · 06-26 · 09-26 | 16 · 30 · 23 · 31 · 3 | 107–334 MB each | 110–334 MB | 32–83 MB |
| NQ 09-25 · 12-25 · 03-26 · 06-26 · 09-26 | 30 · 80 · 79 · 79 · 56 (calendar days) | 124–1,023 MB | 126–1,026 MB | 50–167 MB |

## 2. ⚠️ The lane's question is void, and re-posing it is a new preregistration

Directive §52 asks the sharp, correct question:

> *Does causal sub-minute ES information add incremental value for 60-second NQ executable return
> **BEYOND the frozen NQ-only BBO information set**?*

**That baseline was voided this morning.** `MS-BBO-CANDIDATE-1` read up to +2.065 s into the future;
the causal NQ-only object earns **−$1,785.88/session at OOF correlation 0.0072**. There is no NQ-only
edge for ES to be incremental *to*.

The question can only be re-posed as **"do ES and NQ sub-minute quote states jointly predict
60-second NQ return?"** — and that is a **fresh discovery question**, not a continuation. It inherits
a new attempt budget, a new multiplicity count, and its own preregistration. **Quietly substituting
it for the incremental question would be redefining the population after seeing a result**, which is
exactly what this repo forbids.

## 3. ⚠️ Power is NOT established — and the level-variance shortcut is refused

It is tempting to compute an MDE right now from the session-level P&L dispersion already in hand
(the corrected BBO arm gives session sd ≈ $3,466 over 48 sessions, which at n = 59 would imply an
MDE near **$1,123/session** against a ~$246/session incumbent yardstick — a "4.6× short,
CLOSED-BY-POWER" headline).

> ### That calculation would be wrong, and wrong in a way this project has already been corrected on.
> A **paired incremental** test compares two models on the **same sessions and mostly the same
> decisions**. Its variance is the variance of the *difference*, which is far smaller than the
> variance of the *levels*. Using a level sd as the denominator for a paired effect is the same class
> of error as *"using a 100 %-activity friction denominator to establish power for a 2.4 %-activity
> strategy"* — a defect the owner named and I conceded in this campaign.

**The paired dispersion is not knowable without running both arms**, so power is recorded as **OPEN**,
not as a pass and not as a `CLOSED-BY-POWER`. **59 sessions is the binding capability fact; whether
59 is enough is undetermined.**

## 4. Cost of proceeding, stated plainly

The 59 sessions are **raw NT8 cache, not an exported substrate.** Producing them needs a NinjaScript
tick export per instrument per session. NQ's 58 exported sessions occupy **2.3 GB**; ES+NQ over 59
sessions is a **multi-gigabyte, multi-hour** job, against a standing constraint not to fill the disk
with bulk exports and a binding resource-safety rule from the DOM incident.

**That cost is worth paying for a well-posed question. It is not worth paying for one whose baseline
was deleted eight hours ago.**

## 5. A separate finding, stated at the right strength

`MICRO_DISCOVERY_CONFIRMATION_SPLIT` (2026-08-27) recorded a **quote-FULL ceiling of 99** sessions:
58 in v2, 40 in the old substrate, 1 never materialized — all consumed. Today's file-level census
finds **123** NQ RTH-complete days, of which **116 are pre-seal**.

**This is NOT a claim that a blind BBO pool exists.** The two counts use different criteria: mine is
**file presence** across RTH hours; the split's was **measured quote completeness** with `NONE` /
`PARTIAL` / `FULL` classes. A file can exist and still be quote-sparse. Some of the gap is also
`NQ 09-26` data cached *after* the split was frozen.

> **Recorded as a NAMED OPEN QUESTION, not a finding:** *is the quote-complete ceiling materially
> larger than 99 under a re-census with the split's own criterion?* It is cheap to answer and it
> would matter — but **it matters only if a BBO-class candidate exists**, and right now none does.
> The 141-session **Last-only** blind pool is **untouched** and this census did not read it.

## 6. Status

| | |
|---|---|
| **lane** | **DATA-CAPABLE (59 sessions), QUESTION-VOID, POWER-OPEN, EXPORT-GATED** |
| **not** | closed-by-data · closed-by-power · runnable-as-posed |
| pools consumed | **none.** Directory listings and file sizes only |
| seal | **untouched.** 7 post-seal NQ days were counted in an inventory and **not read** |
| next | it must **win an EVI comparison as a new discovery question**, against the alternatives — not inherit rank 3 from a directive written before its baseline was voided |
