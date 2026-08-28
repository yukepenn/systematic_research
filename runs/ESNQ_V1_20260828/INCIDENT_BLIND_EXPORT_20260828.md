# ⚠️ INCIDENT — a BLIND session was written to disk on the first export. Deleted unread.
# And the cause is a **data-contract finding**, not carelessness.

| | |
|---|---|
| **what happened** | the first ESNQ export wrote **`s20250813_ticks.csv`** — and **2025-08-13 is in `ESNQ_BLIND_15`** |
| **detected** | immediately, by directory listing, before any read |
| **action** | **deleted within ~90 seconds, without opening it** |
| **read by any research process?** | **NO.** No feature, no label, no return, no model, no inspection of price content |
| **root cause** | **`RunStrategyBacktest`'s `from` does NOT bound the data the strategy sees** |
| **fix** | `SWScalpTickExportAllow_v1` — an allow-list enforced at the only place that writes bytes. **Validated against this exact failure** |

---

## 1. The data-contract finding

Requested range, chosen deliberately to cover exactly one session:

```
from = 2025-08-13T22:00:00Z  =  2025-08-13 18:00 ET   (the OPEN of session 2025-08-14)
to   = 2025-08-14T21:00:00Z  =  2025-08-14 17:00 ET   (its close)
```

What NT8 actually delivered, from the exporter's own manifest:

```
s20250813   t_min 2025-08-12 18:00:00.024   t_max 2025-08-13 16:59:59.000    <-- A FULL SESSION EARLIER
s20250814   t_min 2025-08-13 18:00:00.028   t_max 2025-08-14 16:59:59.920    <-- the one requested
```

> ### **`from` is a strategy `From` property, not a data-loading bound.** NT8 loaded bars back to
> **2025-08-12 18:00 ET**, a full session before the requested start, and the exporter — which rolls
> its output file on session change — dutifully wrote that session too.
>
> ### **A DATE RANGE IS NOT A SAFE ISOLATION MECHANISM FOR A BLIND POOL.**

This is now a standing data-contract fact for this repo, alongside *"`AddDataSeries`/
`RunStrategyBacktest` return merge-back-adjusted daily series"*. Both are cases where the requested
object and the delivered object differ silently.

## 2. Exposure assessment — precise, and deliberately not self-flattering

**What was exposed:** the file's **existence and size** (226 MB), and the manifest's **event counts**
— 5,381,126 rows · 407,366 trades · 2,467,618 bid · 2,506,142 ask · session span timestamps.

**What was NOT exposed:** any price, any return, any direction, any feature, any label. Nothing read
the file. It was deleted from a directory listing, not from an inspection of its contents.

**Classification.** By this repo's own established standard — *"file enumeration does NOT consume a
session; computing forward returns DOES"* — the exposed quantities are **event-count metadata of the
same class as the hour-label census** that already established the pool's eligibility. **Session
2025-08-13 is therefore recorded as NOT CONSUMED.**

> ### ⚠️ **But this is a near-miss, and it is recorded as one rather than as a non-event.**
> The distance between "counts were written to a manifest" and "prices were read into a model" was
> one directory listing and about ninety seconds. **The manifest is deliberately NOT mutated to drop
> the session** — `blindguard.require_authorization` re-checks the manifest hash precisely to prevent
> post-hoc session substitution, and quietly editing a frozen manifest after an accident is exactly
> the move that guard exists to block.
>
> **If the owner prefers maximum conservatism**, quarantining 2025-08-13 leaves **14** blind sessions:
> SE rises $1,355.75 → **$1,402.90**/session and the §A1-7 authorization threshold rises
> **$3,371 → $3,489**/session. **That is the owner's call, not mine**, and it is recorded here so
> the choice is available rather than foreclosed.

## 3. The fix — enforced where bytes are written, not where ranges are chosen

`SWScalpTickExportAllow_v1` (class resolved and verified by reflection, all three properties present):

- reads an **allow-list file**; a session whose date is not on it **never has a writer opened**;
- **FAILS CLOSED** — a missing, unreadable or empty allow-list exports **nothing**, never everything;
- writes `_allowlist_status.txt` (loaded flag + count) and `_skipped_sessions.txt` so the guard's
  behaviour is auditable after the fact rather than assumed.

**Validated against the exact failure, not a hypothetical.** Re-running the identical range that
produced the leak:

```
_allowlist_status.txt   loaded=1   n_allowed=44   policy=FAIL_CLOSED
_skipped_sessions.txt   20250813                      <-- the blind session, refused
_manifest.csv           s20250814 ONLY                <-- the dev session, written
```

A guard tested only on a case it was designed for proves nothing. This one was tested on the case
that actually broke.

## 4. Why the amendment's own isolation clause was necessary and insufficient

`SPEC_AMENDMENT_A1` §A1-3 required *"do not bulk-export the 59 sessions into one alpha-readable
directory"* and provided `blindguard.assert_no_blind_contamination` for the **runner**. Both were
correct and neither was sufficient, because **the leak happened upstream of the runner** — at export
time, before any Python guard could see a session.

**Amendment A1 §A1-3 is therefore extended, and the extension is already implemented:**

> **Isolation must be enforced at every stage that can MATERIALIZE a session, not only at the stage
> that READS one.** For ESNQ that means: the exporter's allow-list (source), the runner's
> intersection assertion (consumption), and `BLIND_SPEND_AUTHORIZED` (adjudication) — three
> independent mechanisms, because the first one failed on its first use.

## 5. What did not change

Blind manifest **unmutated**: 15 sessions, `f4a8090e…3c8a`. NQ BBO blind pool **19, unspent**.
141-session Last-only pool **untouched**. Global seal **virgin**. No order path exists in the
exporter and none was created; the run used NT8's isolated `Backtest` account and produced **zero
trades**.
