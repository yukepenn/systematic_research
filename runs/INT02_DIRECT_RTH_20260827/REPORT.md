# INT02 — internals → direct RTH NQ 60-min return: NO CANDIDATE, and only partly closed

| | |
|---|---|
| **verdict** | **NO CANDIDATE / NO DETECTED SIGNAL** for this mapping, horizon and feature budget |
| spec committed | `1e2592d`, before the run |
| sample | **1,093 sessions**, 5,434 decisions, 2022-01-18 → 2026-05-29 |
| seal | ≥ 2026-08-01 **not read**; BURNED 2026-05-31→07-31 excluded |

---

## 1. Result

| arm | $/session | t | net | trade rate | directional accuracy |
|---|---:|---:|---:|---:|---:|
| **RIDGE (primary)** | **−$66.73** | −0.81 | −$60,723 | 84.1 % | **49.5 %** |
| GBM (challenger) | −$40.91 | −0.45 | −$37,225 | 84.9 % | 51.4 % |

| gate | observed | |
|---|---:|---|
| I1 net/session > 0 | −$66.73 | **FAIL** |
| I2 > 95th pctile of refitted null | 66.7th | **FAIL** |
| I3 > 95th pctile of placebo | 57.6th | **FAIL** |
| I4 net > 0 at STRESS | −$75.96 | **FAIL** |

The refitted session-block null is a **real** distribution — 120 replicates, **120 distinct
values**, sd $77.40 — and the `≥ 2 distinct values` assertion from the MS-LAST repair is now
permanent in the code.

**Why the policy trades 84 % of decisions** (versus MS-LAST's 2.4 %): the mean absolute 60-minute
move is **$879.73** against a $19.36 cost, so the threshold is almost always cleared and the result
reduces to directional accuracy — **49.5 %**, a coin flip, paying cost on five in six decisions.

## 2. ⚠️ The power statement, precisely — this is only PARTLY closed

| | |
|---|---:|
| sessions | 910 evaluated |
| per-session sd | $2,471.36 |
| **MDE** | **$229.39/session** |
| one-sided upper 95 % bound | **+$68.16/session** |
| materiality WEAK ($49) | MDE is **4.68×** the threshold |
| materiality STRONG ($246) | MDE is 0.93× the threshold |

> ### **The upper 95 % bound (+$68.16) sits ABOVE the weak materiality threshold ($49).**
> ### **So a $49/session effect is NOT ruled out.**
>
> This is closed at the **strong** threshold ($68.16 < $246) and **not** at the weak one. The
> correct verdict is therefore **NO DETECTED SIGNAL**, *not* equivalence-closed — the distinction
> the MS-LAST repair established, applied here on its own terms rather than restated.

## 3. Verdict

| | |
|---|---|
| **what was measured** | whether 15 causal TICK/TRIN/VIX features (plus NQ state) predict the direct 60-minute RTH NQ return after cost |
| **what passed** | the machinery — a real refitted null, the seal assertion, the causal information rule |
| **what failed** | all four gates. Two model attempts, both counted |
| **what changed** | this specific mapping produces **no candidate**. `INT01`'s routing null is now joined by a direct-return no-detection at 60 minutes |
| **what did NOT change** | ⚠️ **"internals are null" is still NOT an available conclusion.** A $49/session effect is not excluded; other horizons, other feature classes and other targets are untested |
| **evidence class** | **DISCOVERY-CONSUMED, NO DETECTED SIGNAL.** Not equivalence-closed at the weak materiality threshold |
| **ladder status** | no candidate, no promotion |
| **data burned** | 2022–2026-05 internals for this mapping. Seal untouched |
| **does NOT authorize** | a horizon sweep, a feature expansion, or a model upgrade — each is a new hypothesis needing its own preregistration |
