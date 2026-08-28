# BBO recensus — **VERDICT B. A genuine blind BBO pool exists: 19 sessions.** And the old
# "no pool exists" verdict was **correct under its own criterion.**

| | |
|---|---|
| **verdict** | ✅ **B — 19 genuinely unread, RTH-complete, pre-seal NQ BBO sessions** |
| spec committed | `022c543`, **before** the crosswalk |
| manifest | `BBO_BLIND_POOL_MANIFEST.csv` · sha256 `84a8575a…0931` · **frozen at `022c543`** |
| **not done** | ⛔ **its returns were NOT read. It was NOT spent. No model was designed against it.** |
| **99 vs 123** | **fully explained by definitions.** Not a discovery of hidden data |
| power | **well powered to FALSIFY a large claim · weak to CONFIRM a modest one** |

---

## 1. The old classifier reproduced **exactly** before anything was compared

Source-provenance gate: locate the producing artifact → the producing code → reproduce → only then
test alternatives.

```
stored  runs/ORDERFLOW_EXPAND_20260827/out/bbo_hourly_truth.csv   310 rows
recomputed from bbo_hourly_truth.py's rule                        310 rows
class agreement                                        310 / 310  EXACT
  FULL 99 / 99      PARTIAL 47 / 47      NONE 164 / 164
```

## 2. The 99-vs-123 gap is a **definition difference**, and the crosstab settles it

| | NEW RTH-complete = **False** | NEW RTH-complete = **True** |
|---|---:|---:|
| **OLD `FULL`** | **2** | **97** |
| **OLD `PARTIAL`** | **28** | **19** |
| **OLD `NONE`** | **164** | 0 |

**99 = 97 + 2. 116 = 97 + 19.** There is no third population and nothing was hiding.

> ### OLD asks *"is the whole 23-hour session quote-complete?"* NEW asks *"is the RTH window
> ### quote-complete?"* **A session with complete RTH quotes and a missing overnight leg is
> ### `PARTIAL` under OLD and complete under NEW — and is perfectly usable by an RTH-only
> ### strategy, which every BBO object in this campaign has been.**

**The mechanism is exact, uniform, and understood.** All 19 share `old_quote_frac = 0.739` to three
decimals across **9 months and 4 contracts** — that uniformity is a systematic pattern, not random
corruption. Decomposed:

```
Bid   evening (D-1) labels: NONE          day (D) labels 1..17  (17)   17/23 = 0.739
Ask   evening (D-1) labels: NONE          day (D) labels 1..17  (17)   17/23 = 0.739
Last  evening (D-1) labels: 19..23        day (D) labels 0..17  (18)   23/23 = 1.000
```

**Quotes cover ET 00:00 → 16:59 on the session date; the prior evening (ET 18:00 → 23:59) has no
quotes at all.** A download-boundary effect. **RTH 10:00–15:30 ET sits entirely inside the covered
window**, so these sessions are fully usable for an RTH strategy and were correctly excluded by a
criterion built for full-session work.

⚠️ **A defect in the NEW criterion, declared in the SPEC before the count.** Under `label = ET hour +
1`, RTH needs labels **10..16**; `esnq00_census.py` used **9..16**, demanding an extra early hour.
Both were computed: **116 either way.** The looser window adds nothing, so the as-run figure was
never inflated.

## 3. Consumption — every flag names its chain

| state | count |
|---|---:|
| pre-seal dates with any NQ tick file | **310** |
| OLD quote-`FULL` (23 session-hours) | 99 |
| NEW RTH-complete | **116** |
| materialized in v2 (`MS01`, `MS01A`, `MSBBO_V1`, deployment freeze) | 58 |
| materialized in OLD substrate (`AUCTION01`–`04`, `ACTIONMAP01`, `FLOW01`, `U9`, `U9B`) | 48 |
| **materialized in EITHER = OUTCOME-CONSUMED** | **104** |
| RTH-complete **and** materialized | 97 |
| **RTH-complete and NOT materialized** | **19** |
| quote-`FULL` and NOT materialized | **1** |

**Two adversarial checks before believing it:**

1. **Does any run read `db/tick` directly and compute returns?** Nine files touch the store:
   `build_registry`, `ncd_day` (daily bars, not tick), `DATA_CAPABILITY_AUDIT` ×2, `ESNQ00`,
   `ORDERFLOW_EXPAND` ×3, and this recensus. **All enumerate or export; none computes a forward
   return on BBO prices.** No direct-read consumption path exists.
2. **Were any of the 19 ever extracted to CSV?** The extraction directory holds **1** session.
   **Overlap with the 19: zero.**

**Consumption was counted conservatively**, as declared: presence in *either* substrate marks
CONSUMED without proving a run's execution predated the file. Over-counting consumption shrinks the
claimed pool, which is the only safe direction.

## 4. ⚠️ What 19 sessions can and cannot decide

Variance estimated **only from the 48 already-consumed sessions** — the pool's returns were not read.
Session-level sd **$5,250.81**. This is a **one-sample** test of a frozen strategy's mean session net,
so the **level** variance is the correct denominator here — unlike a paired incremental test, which
is exactly why ESNQ's power was left open rather than computed this way.

| n | MDE at 80 % power |
|---:|---:|
| **19 (this pool)** | **$2,996/session** |
| 48 | $1,885 |
| 126 | $1,163 |

Against a **~$246/session** incumbent yardstick, n = 19 is roughly **12× short for confirmation.**

**But the asymmetry is what matters.** A candidate claiming **+$5,125** that truly earns **−$1,786**
differs by **$6,911/session = 5.7 standard errors** at n = 19. **Power to reject that false claim is
effectively 1.0.**

> ### The pool is a **FALSIFIER**, not a validator. It is well powered against exactly the failure
> ### this campaign has actually experienced — a spectacular discovery result collapsing forward —
> ### and badly underpowered to establish a modest edge. **It must be described that way whenever it
> ### is used.**

## 5. What this does and does not authorize

| | |
|---|---|
| ✅ **it does** | change future experimental design: a BBO-class lane now has **one** historical falsification shot it did not have yesterday |
| ⛔ **it does not** | un-void `MS-BBO-CANDIDATE-1`. That object read the future; a blind pool cannot repair a causality violation |
| ⛔ **it does not** | permit re-running the corrected NQ-BBO V1 feature set. **That formulation has paid its discovery budget** |
| ⛔ **it does not** | get spent because the project currently has no candidate. **A blind pool is an asset; its existence is not a reason to spend it** |
| ⛔ **it does not** | authorize reading its returns. **They have not been read, and this wave does not read them** |

**Governance, matching the 141-session Last-only pool:** any future use requires a **genuinely
different mechanism, frozen without reading the pool**, and one shot only.

## 6. Was the old verdict wrong?

**No.** `MICRO_DISCOVERY_CONFIRMATION_SPLIT` concluded *"NO VALID BLIND BBO POOL EXISTS"* — and under
its own full-session criterion that is **still true today: exactly 1 unread quote-`FULL` session**
(2026-05-25, `NQ 06-26`, frac 0.957).

What was wrong was not the measurement but the **scope word attached to it**: a criterion built for
full-session completeness was allowed to answer a question about an **RTH-only** strategy. That is
the same Level-1/Level-2 confusion this repo has already caught once — *"no such file is
materialized"* is a narrower claim than *"no such data can be reached."*

| | |
|---|---|
| pools consumed by this run | **none.** File names and hour labels only |
| seal | **9 sealed dates inventoried by metadata; 7 would be RTH-complete. Counted, NOT read.** All blind-eligibility flags `False` by construction |
| 141-session Last-only pool | **untouched** |
