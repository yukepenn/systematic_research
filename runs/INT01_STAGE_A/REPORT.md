# INT01 — internals do not predict P1 action value. That closes ONE mapping.

| | |
|---|---|
| **run class** | **STAGE-A INFORMATION TEST** — no router, no policy, no threshold, nothing promoted |
| date | 2026-08-27 |
| preregistration | `spec.yaml`, committed at **`96a0019`, before the code existed** |
| code | `research/weekly_edge/src/run_int01.py` · reproduction `out/int01.txt` · `out/arms.csv` · `out/gates.csv` |
| population | **760** RTH P1 decisions on internals-covered sessions (pre-declared ~764) |
| seal | untouched |

> ### **VERDICT: NULL.** `X + internals` sits at the **37.5th percentile** of its own refitted null.
> ### **Per §41 this closes `internals → P1 action value` and NOTHING ELSE.**

---

## 1. G1 — the causality gate passed, and it caught a defect in my own feature

The contract was **tested, not asserted**: every internals bar strictly after each row's
`info_cutoff_ts` was replaced with garbage and all features rebuilt. Anything that moved was
reading the future.

| probe | moved on | verdict |
|---|---:|---|
| `PROBE_LEAK` — reads the **decision** bar | **100.00 %** | **DROPPED** ✅ as required |
| `PROBE_SAFE` — reads the **info_cutoff** bar | 0.00 % | **KEPT** ✅ as required |

**The gate discriminates.** It also **dropped one of my nine declared primitives**: `vix_shock`
moved on **2.63 %** of rows, because it references the session's first RTH bar, which for the
earliest decisions of a session is *at or after* the cutoff. **That is a real leak in a feature I
wrote, caught by the gate rather than by me.** 8 of 9 primitives survived.

## 2. Arms — declared before the run

| arm | features | OOS ρ | percentile of its **own refitted** null |
|---|---:|---:|---:|
| `X` (RR_W002A's 20) | 20 | **−0.0481** | 29.5th |
| **`X + INT`** | 28 | **−0.0265** | **37.5th** |
| `INT` alone | 8 | **+0.0062** | 69.5th |
| `NEGCTRL` (known-null, matched count) | 28 | −0.0400 | 28.0th |

## 3. Gates

| gate | result | |
|---|---|---|
| **G1** integrity | **PASS** | leak dropped, safe probe kept |
| **G2** increment | *PASS* | **but carries NO WEIGHT — see below** |
| **G3** beats own null | **FAIL** | 37.5th percentile, needs ≥ 95th |
| **G4** control | **PASS** | beats `NEGCTRL`; `NEGCTRL` does not beat its own null |
| **G5** fold sign | **FAIL** | increment positive in **44 %** of 9 folds |

> ### ⚠️ **G2's pass carries no weight, and that was declared in advance.**
> `X + INT` (−0.0265) beats `X` (−0.0481) — but **both are worse than chance.** This is a pass at
> being *less negative than something already below zero*. The spec named this exact shape as
> weightless before the run, because `RR_W004` produced it and the reading was refused there too.
> **The gates that test for information — G3 and G5 — both fail.**

`INT` alone is the only arm with positive ρ (+0.0062, 69.5th percentile). **That is not evidence.**
It is inside the null's normal range and would need the 95th percentile to mean anything.

## 4. What this closes — and what it explicitly does not

**CLOSED: `internals → P1 full-horizon action value`.** Recorded as
**`CLOSED-BY-POWER-AND-EVIDENCE`**, not as proof of absence, because the power disclosure was made
**before** the result: MDE is **1.31× the covered mean** on this target, so the wave could only ever
have found a *large* effect.

> ### ⚠️ **NOT CLOSED, per directive §41: "internals contain NQ alpha."**
> This tested **one mapping**. The **direct-return** question — do internals predict RTH NQ return
> itself — is a different target with different variance and is **untested**. Inferring the general
> claim from this specific null is precisely the error the order-flow lane taught, where a closed
> *router* mapping was nearly read as a closed *data surface*.

**Also unchanged:** internals can never speak to the **64.3 %** of P1 decisions that are overnight.
That ceiling is a property of P1's schedule, not of the data, and no acquisition moves it.

## 5. A merge defect caught before it reached a result

The first run reported a base population of **2,305** where `features.csv` holds **2,131**. The
merge key `(session_date, entry_ordinal_in_session)` is **not unique** — a calendar *date* can host
two *sessions*, since the 18:00 evening open belongs to the next session — so matches were
duplicated. Fixed by keying on `(session_date, session_id, entry_ordinal_in_session)`, which is
unique in both frames, with assertions that the row count is preserved and nothing is unmatched.

**Row-count inflation of 8 % would not have thrown an error anywhere.** It would simply have made
every ρ, every null and every gate wrong.

## 6. Continuation

| | |
|---|---|
| **outcome** | `internals → P1 action value` **NULL**, closed by power and evidence |
| **still open** | `internals → direct RTH NQ return` — separate target, untested, needs its own preregistration |
| **still open** | `internals → XM quality`, but only if information exists before XM's 09:45 decision |
| **evidence class** | internals substrate remains **REGIME-LOCAL (2022+)**, unchanged |
| **promoted / demoted** | **nothing** |
