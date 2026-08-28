# `ESNQ_V1` — SPEC AMENDMENT **A3**. The **final** pre-result amendment.

Committed **before the runner exists and before any development number**. Extends A1/A2; weakens
nothing.

| § | change | value |
|---|---|---|
| **A3-1** | materialization wording corrected to the state taxonomy | see below |
| **A3-2** | **operational quarantine** of `2025-08-13` → `ESNQ_BLIND_EFFECTIVE_14` | **n = 14** |
| **A3-3** | **`CROSS_MARKET_ES_EMBARGO = 200 ms`** — a data-contract safety margin | **frozen, unsearchable** |
| **A3-4** | `mu_claim` = 10th pctile of a **circular block bootstrap** over session nets | **L=4, B=20,000, seed=20260828** |

---

## A3-1. The state taxonomy — "never materialized" was false

`PIPELINE_FREEZE.json` said *"15 sessions, never materialized, never read."* **The second clause is
true; the first is not.** During the exporter incident `2025-08-13`'s **NQ** tick CSV was
transiently written and deleted unread.

| state | count |
|---|---:|
| `ORIGINAL_FROZEN_BLIND_MANIFEST` | **15** |
| `OUTCOME_CONSUMED` | **0** |
| `PRICE_DERIVED_INFORMATION_READ` | **0** |
| `TRANSIENTLY_MATERIALIZED` | **1** |
| `METADATA_EXPOSED` | **1** |
| `CURRENT_BLIND_BYTES_IN_DEV_SUBSTRATE` | **0** |

The incident classification is unchanged: **`BLIND MATERIALIZATION INCIDENT — NO RESEARCH OUTCOME
CONSUMPTION`**. Immutable run output is not rewritten; only current-truth wording is corrected.

## A3-2. Operational quarantine — and why it is not outcome selection

**`2025-08-13` may not participate in any future `ESNQ_V1` blind adjudication.**

> It was excluded on an **operational data-integrity fact known before any blind price or outcome was
> read**: its NQ CSV was transiently materialized and its market-activity metadata (row/trade/bid/ask
> counts and span) was exposed. **No price, return, feature, direction, label or P&L was ever read
> from it.** This is not outcome-based session selection.

**Instrument resolution, from the export logs — not guessed:**

| | |
|---|---|
| **NQ** `2025-08-13` | **TRANSIENTLY MATERIALIZED**, deleted unread; metadata exposed |
| **ES** `2025-08-13` | **NEVER MATERIALIZED** — refused by the allow-list guard (present in ES `_skipped_sessions.txt`) |

**The original manifest is preserved byte-for-byte** (`f4a8090e…3c8a`). A **derived** manifest is
created instead: `ESNQ_BLIND_EFFECTIVE_14.csv`, sha256 **`00654d4f…4743`**, with
`original_n = 15`, `excluded_session = 2025-08-13`,
`exclusion_reason = PRE-OUTCOME OPERATIONAL QUARANTINE: TRANSIENT MATERIALIZATION / METADATA
EXPOSURE`, `effective_n = 14`. **Every future ESNQ blind runner must require EFFECTIVE_14.**

**Power at n = 14**, on the already-frozen `sigma_blind = $5,250.81`:

```
SE_blind  = 5250.81 / sqrt(14) = $1,403.34/session
MDE(80%)                       = $3,489.36/session
```

### The NQ BBO 19-session asset — classified exactly, not conveniently

`2025-08-13` is also a member of that asset (`NQ 09-25`), and it is the **NQ** side that was written.
So the asset must **not** be described as 19 pristine-never-materialized sessions:

| status | count |
|---|---:|
| **outcome-unconsumed** | **19** — unchanged; no outcome status changes because metadata was exposed |
| **pristine-never-materialized** | **18** |
| **metadata-exposed** | **1** (`2025-08-13`) |

## A3-3. `CROSS_MARKET_ES_EMBARGO = 200 ms` — turning clock uncertainty into an executable rule

The clock verdict is `CLOCK-COMPATIBLE-BUT-SEMANTICS-UNKNOWN` and the timing diagnostic resolves
**100 ms bins**. Therefore `ES feature_ts < t` alone is **not strong enough**: a systematic
sub-100 ms ES-vs-NQ semantic offset would be invisible to the probe while letting nominally pre-`t`
ES events sit *after* the true NQ decision instant.

```
every ES-derived feature:   max_es_source_ts  <=  t - 200 ms      asserted ROW BY ROW
NQ-native features:         max_nq_source_ts  <   t
execution:                  first DISTINCT NQ quote  >  t   and  >  t + 60 s
```

Use the last **distinct observable** ES event at or before the cutoff. **No interpolation from any
observation after the cutoff.**

> ### **This is a DATA-CONTRACT SAFETY MARGIN, not an alpha parameter. It may NOT be searched.**
> 50 / 100 / 150 / 200 / 500 ms will **not** be compared with the best kept. **200 ms is the single
> frozen value**, chosen as 2× the probe's resolution before any feature exists.

Unchanged: the 11 feature formulas · 60 s target · schedule · Ridge · costs · policy · model family.
**Only the admissible ES information cutoff changes.**

## A3-4. The frozen development-uncertainty procedure

`mu_hat_dev ≥ ~$4,385` in A2 was an **illustration**, not a binding number — real development
uncertainty does not exist until the 44 session nets exist. **There is no fixed dollar
authorization threshold.** Frozen instead:

| | |
|---|---|
| dependence unit | **SESSION** |
| input | the **44** chronological OOF session net P&Ls |
| procedure | **circular block bootstrap** on session nets |
| n · L · B · seed · pctl | **44 · 4 · 20,000 · 20260828 · 10** |
| `mu_claim` | `max(0, 10th percentile of the bootstrap mean distribution)` |

Circular blocks preserve short-run session dependence an IID resample would destroy — and that
destruction would *narrow* the interval, flattering the claim.

> **After the result, `mu_claim` may NOT be replaced by an ordinary row-level SE, an IID decision
> SE, whichever SE is smaller, a HAC chosen after inspection, or `sigma/sqrt(44)` because it is
> friendlier.** Those may be reported as diagnostics. **Only this bound controls blind spending.**

Blind power is then computed at **effective n = 14**, `sigma_blind = $5,250.81`, one-sided
α = 0.05, true effect = `mu_claim`. **Authorization requires power ≥ 0.80 in addition to every
original development gate.** The realized threshold and power are reported **only after**
development.
