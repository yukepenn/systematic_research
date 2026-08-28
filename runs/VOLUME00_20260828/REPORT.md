# `VOLUME00` — RESULT · **`DATA-CAPABLE`**

Executes `SPEC.md`, committed at `9678168` **before** any measurement.
**No return, no P&L, no Sharpe, no signal, no model was computed in this run.**

> ## **VERDICT: `DATA-CAPABLE / CONTRACT-SPECIFIC BY STRUCTURE, NOT CROSS-SOURCE VERIFIED`**
> **21 roots · 6 sectors · 17 calendar years · 3,712–4,157 eligible root-days per root.**
> **Adopted representation: `ROOT_TOTAL`. Roll embargo `E = 0`.**

| clause | statistic | observed | gate | |
|---|---|---:|---:|:--:|
| **V1** cross-source | minute-store identity | **`REFERENCE UNAVAILABLE`** | — | ⚠️ |
| **V2** duplication | identical-volume-pair share of multi-contract root-days | **0.0101 %** (6 of 59,251) | ≤ 0.5 % | ✅ |
| **V3** front ≠ deferred | median `vol(next live) / vol(designated)` | **0.0011** | < 0.25 | ✅ |
| **V4** field semantics | `int64`, non-negative, integral | 0 neg · 0 NaN · 168 zero (0.086 %) | — | ✅ |
| **V5** expiry collapse | median `last-5 / own 63d median` | **0.0227** | < 0.50 | ✅ |
| **G7** causal roll | `info_cutoff < decision_date` on 1,954 volume rolls | asserted | all | ✅ |

---

## 1. ⭐ The result that actually settles the question — a **known-merged positive control**

V2 and V3 passing on `db/day` proves nothing unless they *can* fail. So the same two statistics
were run against `research/multi_market/export/test_ES2011_bars.csv` — the captured
**merge-back-adjusted** payload that established the merged-path defect in the first place.

| statistic | **merged control** | **`db/day` measured** | gate |
|---|---:|---:|---:|
| V2 identical-volume-pair share | **98.86 %** | **0.0101 %** | ≤ 0.5 % |
| V3 median `vol(next)/vol(front)` | **1.0000** | **0.0011** | < 0.25 |
| V3 share of ratios **exactly** 1.000 | **96.14 %** | **0.0038 %** | — |

> ### **The two statistics that pass decisively on `db/day` fail completely on a payload known to
> ### be merged. The `db/day` pass therefore DISCRIMINATES; it is not a formality.**
>
> This is a **stronger** test than the unavailable cross-source identity check would have been:
> an identity check tests the **decoder**, this tests the **claim**. A root-level merged
> front-volume series copied into every contract cannot produce a deferred/front ratio of 0.0011,
> and it reproduces 1.0000 to the digit when it is actually present.

**`db/day/<FULL CONTRACT ID>` carries the traded contract's own volume.** The question the design
brief raised — *"is it a merged front-month copy? that check was done for price, and volume is a
different field"* — is now answered for volume, on its own evidence.

## 2. Universe — locked before measurement, and **nothing was excluded**

**All 21 CORE roots admitted, all 6 sectors**, `2010-03-23 → 2026-07-31`, 17 calendar years.
Volume coverage against each root's canonical active-contract price days is **100.00 %** for 20
roots and **99.97 %** for `6A`. `CARRY_V1`'s 10-root universe was deliberately **not** inherited
(carry needed two simultaneously listed contracts; volume needs only the traded one). No new roots,
no micros, no `EXTENDED`.

| gate | observed | | | gate | observed | |
|---|---:|:--:|---|---|---:|:--:|
| **G1** roots ≥ 12 | **21** | ✅ | | **G5** coverage ≥ 80 % | **99.97 %** min | ✅ |
| **G2** sectors ≥ 4 | **6** | ✅ | | **G6** no semantics defect | V2–V5 pass | ✅ |
| **G3** years ≥ 8 | **17** | ✅ | | **G7** no causal-roll defect | asserted | ✅ |
| **G4** root-days ≥ 1,500 | **3,712** min | ✅ | | | | |

## 3. ⚠️ The roll entanglement was real, it bound, and it changed the representation

The audit measured the **same-day contract-switch log-volume jump**, `LV(new, d) − LV(old, d)` — a
same-market, same-day difference, so it isolates the contract switch and nothing else.

| | n | median jump | \|jump\| > 1 MAD-unit |
|---|---:|---:|---:|
| `VOLUME_CROSSOVER` | 863 | **+1.456** | **90.27 %** |
| `PRE_EXPIRY_OVERRIDE` | 495 | **−0.764** | **81.82 %** |
| **all causal rolls** | **1,358** | +0.628 | **`J` = 0.8719** |

> ### **`J = 0.8719` against a preregistered threshold of `0.10`.** The designated-contract volume
> ### series is **mechanically discontinuous at rolls in both directions** — up at a volume
> ### crossover, **down** at a forced pre-expiry roll.
>
> A forced roll's downward jump would have read as *"abnormally low participation"* and
> **manufactured a long signal out of the calendar**. The substrate carries **1,082 pre-expiry
> rolls** — 210 for `CL` alone and 68–70 for every FX root.

**SPEC §3.6 therefore selects `ROOT_TOTAL`**: the sum of volume across all live contracts of the
root on date `d`, which is **invariant to which contract is designated** and cannot jump at a roll.
The rule was frozen before the measurement and resolved **on roll mechanics only** — the two
branches were never compared by performance, and no P&L exists to compare them with.

> **The coupling matters:** `ROOT_TOTAL` is only a meaningful liquidity measure **because** V2/V3
> certify the per-contract fields are not duplicated copies. Under a merged copy the sum would
> simply be `n ×` the front month.

### The embargo ladder — and an honest near-miss

| radius | near-roll \|ZVOL\|>2 rate | far rate | ratio | gate |
|---|---:|---:|---:|---:|
| ±1 | 15.88 % | 10.72 % | **1.481** | ≤ 1.5 |
| ±3 | 14.77 % | 10.42 % | 1.418 | ≤ 1.5 |
| ±5 | 13.49 % | 10.33 % | 1.306 | ≤ 1.5 |

**`E = 0`**, by the frozen ladder.

> ⚠️ **1.481 against a 1.5 gate is a near-miss and is recorded as one.** Even under `ROOT_TOTAL`,
> days within one session of a roll carry **≈48 % more extreme participation readings** than days
> far from one. **The ladder is not altered — that would be precisely the forbidden post-hoc
> move** — but this is carried into `VOLUME_LIQUIDITY_V1` as a **declared residual risk**, and it
> is the reason the run report must decompose contribution by distance-to-roll.

## 4. Causal active-contract contract — stated exactly

`research/multi_market/src/roll.py::build_roll_ledger` compares the current vs next eligible
contract using **volume at `t−1` only**; the roll takes effect on `t`.

> ### **`ACTIVE_CONTRACT(t)` is decided from `t−1` volume. Stated plainly because it is true.**

The pre-expiry override (`PRE_EXPIRY_BUFFER_DAYS = 5`) uses **contract mechanics only** — no price,
no volume. Three unit tests re-run and passing: no-roll telescoping (reduces exactly to
`close_t − close_{t−1}`), basis invariance (a 5,000-point roll basis changes the economic return by
< 1e−9), and roll causality **with teeth** — perturbing `t−1` volume **moves** the ledger,
perturbing day-`t` volume **does not**. Real-ledger assertion: **1,954 of 1,954** volume rolls have
`info_cutoff` strictly before `decision_date`.

**Binding consequence, committed:** week `W`'s positions may use volume only from sessions
completed **strictly before `W` begins`**. No same-day final volume may predict that day's
already-earned return.

## 5. The two findings that needed explaining rather than excusing

### 5a. `CL` (5.683) and `NG` (1.742) do not "collapse" — a statistic-scope artifact, not a defect

**NT8 cached a median of 26 daily bars per `CL` contract** (vs 134 for `ES`). V5's 63-bar baseline
therefore lands in a monthly energy contract's **deferred, quiet** period while its last 5 days land
near **front-month** status, so the ratio measures the *rise into* front month, not a failure to
collapse.

Worked example — `CL 11-12`, expiry 2012-10-22, final five volumes
`102,195 · 103,382 · 96,179 · 34,805 · 5,456`: **the last two days do collapse**; the 5-day *median*
is dominated by the three front-month days before them.

**The frozen V5 statistic and its verdict are unchanged (0.0227, PASS).** Diagnostics only:
restricted to contracts with ≥120 cached bars the median is **0.0105**; under
`median(last 2 bars) / peak volume` **every root collapses**, `CL` at 0.062 and `NG` at 0.107.
⚠️ And it is not decisive anyway: **V2 and V3 already answer `CL` and `NG` directly** — 1 and 5
identical-volume days out of 2,132 and 4,041, deferred/front medians **0.1014** and **0.2020**.

### 5b. The minute reference is `UNAVAILABLE`, not `DISAGREEING`

The `db/minute` payload decodes with the **same 28-byte header** (`version 1`, `tickSize 0.25`,
`firstPrice 4778.5`) but its **8,968 remaining bytes admit no fixed record size in 24–64 bytes** —
about **6.5 bytes per bar** against ~1,380 bars in an ES session. **It is delta-compressed and
variable-length.** Decoding it means reverse-engineering NT8's minute codec: a separate engineering
project, out of scope here.

> ⛔ **`GetBars` was disqualified as the reference in the SPEC and stays disqualified**: it is the
> **writer** that produced the store under test, so using it is both circular and **mutating**.
> ⛔ `AddDataSeries` is barred outright as the merged path.

**SPEC §3.7 distinguishes unavailability from disagreement.** The verdict therefore carries
**`NOT CROSS-SOURCE VERIFIED`** into every later report — softened by nothing — and is offset by
§1's positive control, which tests a stronger proposition.

## 6. What VOLUME00 did NOT do

No return. No P&L. No Sharpe. No signal-vs-return correlation. No model. No parameter chosen by
looking at an outcome. The 63-session horizon, the MAD scaling and the sector demean are **not**
evaluated here.

⛔ **Protected assets untouched by this run and by this entire campaign:** `ESNQ_BLIND_EFFECTIVE_14`
· NQ BBO 19 (18 pristine / 1 metadata-exposed) · the remaining unread ES BBO · the 141-session
Last-only pool · **all data at or after `2026-08-01`** (asserted in code: `panel.date.max()` =
`2026-07-31`).

> ### **`MAXIMUM HISTORICAL EVIDENCE CLASS = DISCOVERY-GRADE`**, declared in the SPEC before this
> ### measurement and unchanged by it. Held-back windows are **`FAMILY-SPECIFIC HELD-BACK /
> ### MARKET-OUTCOME-CONSUMED`**, never "clean OOS".

**Next: COMMIT C — `VOLUME_LIQUIDITY_V1` SPEC.** One formulation, zero challengers, gates frozen
before any P&L. **LIVE ENABLED = NO.**
