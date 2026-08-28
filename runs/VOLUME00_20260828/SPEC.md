# SPEC — `VOLUME00` · DATA SEMANTICS + CAPABILITY ONLY

**COMMITTED BEFORE ANY MEASUREMENT.** Preregistration commit A of the `VOLUME / LIQUIDITY`
campaign. **No return, no P&L, no Sharpe, no correlation with returns, no signal, no model is
computed in this run.** The only outputs are data-contract facts and a capability verdict.

| | |
|---|---|
| **run class** | `DIAGNOSTIC` — data capability, zero alpha budget |
| **question** | Does `db/day/<FULL CONTRACT ID>` contain causally usable, **CONTRACT-SPECIFIC** daily volume suitable as an alpha input — rather than a merged / front-month / copied / artificial field? |
| **verdicts available** | `DATA-CAPABLE` · `VOLUME SEMANTICS NOT CERTIFIED` (STOP) · `CLOSED-BY-DATA` (STOP) |
| **LIVE ENABLED** | **NO** |

> ### ⚠️ **MAXIMUM HISTORICAL EVIDENCE CLASS FOR THIS ENTIRE FAMILY = `DISCOVERY-GRADE`.**
> Declared here, before anything is measured. Every usable historical date in this substrate has
> already been outcome-consumed by TSMOM development (2009–2018), TSMOM V2 validation (2019–2022)
> and TSMOM TAIL-H1 (2023–2026). **No historical window can promote a positive result to
> `VALIDATED`.** Chronological held-back windows remain useful for controlling *family-specific*
> selection and are named exactly that: **`FAMILY-SPECIFIC HELD-BACK / MARKET-OUTCOME-CONSUMED`**.
> Never `pristine OOS`, `clean historical validation`, `forward`, `prospective`, or `independent
> validation`.

---

## 1. Why a data gate runs before a signal

`TSMOM_DATA_CONTRACT` established that **NT8 serves different data through different paths for the
same contract name**: `AddDataSeries` / `RunStrategyBacktest` return **merge-back-adjusted** series,
while `GetBars` / the `db/day` `.ncd` store return **true unmerged contract data**. The evidence for
the merged path was measured on **price** — ES 12-11 minus ES 03-11 is exactly −16.000 with sd
0.0000 — and, incidentally, on volume: four ES "contracts" reported an **identical** 1,098,424 on
2010-01-04.

> ### **That check certified PRICE in the unmerged store. VOLUME IS A DIFFERENT FIELD and has never
> ### been certified as its own object.** Volume has only ever been used in this repo as the **roll
> ### criterion**, where a monotone comparison between two contracts is all that is needed and a
> ### shared scale factor would cancel. An alpha signal reads the **level**, so the field must be
> ### proved contract-specific in its own right.

**No alpha may be tested on an ambiguous field.** If the checks below do not certify it, the family
closes here, before a single feature is written.

## 2. Universe — locked before measurement

**The canonical 21-root CORE universe**, authoritative in `research/multi_market/src/ncd_day.py`
(`CORE`), already certified for the daily substrate and the causal roll engine:

```
equity_index  ES  NQ  YM
rates         ZT  ZF  ZN  ZB
fx            6E  6J  6B  6A  6C  6S
energy        CL  NG
metals        GC  SI
ags           ZC  ZW  ZM  ZL
```

**21 roots · 6 sectors.**

- ⛔ **`CARRY_V1`'s ten-root universe is NOT inherited.** Carry required two *simultaneously listed*
  contracts; volume requires only the traded contract, so the carry restriction is not a volume
  restriction and importing it would be an unjustified exclusion.
- ⛔ **No new roots are fetched in this campaign.** `EXTENDED` (`RTY`, `RB`, `HO`, `HG`) is **not**
  admitted: it was measured not to reach 2009 in the CORE depth probe and admitting it would change
  the chronology.
- ⛔ **No micros.** "More breadth" is not a reason.
- **Exclusions may arise ONLY from the preregistered data-capability rules in §6.** No root may ever
  be excluded because its eventual alpha is bad.

## 3. Certification of contract-specific volume

### 3.0 Sample — deterministic, chosen WITHOUT volume or returns

The cross-source sample is fixed by **presence only**:

1. `M` = contract IDs present as a directory under **both** `db/day` and `db/minute`, whose root ∈
   CORE and whose `(month, year)` lies in that root's declared `CYCLES` entry.
2. Sort `M` by `(root, expiry_key)`.
3. Per root, select up to **3** contracts at sorted indices `0`, `floor(n/2)`, `n−1` (deduplicated)
   — first, middle, last of that root's minute-store history.
4. For each selected contract, take **every** date with a per-session minute file
   `<YYYYMMDD>.Last.ncd`, capped at the **first 400 by date** (deterministic; never selected on
   value).

**Known in advance from an inventory listing** (directory names only — no volume was read): the
minute store holds 203 CORE-contract directories covering **ES · NQ · YM · ZN · ZB · 6J · CL** —
**7 roots across 4 sectors** (equity_index, rates, fx, energy). **Metals and ags have no minute
coverage.** The cross-source clause **V1** is therefore limited to those 4 sectors, and this is
stated now rather than discovered later. **The structural clauses V2–V5 run on all 21 roots and all
6 sectors.**

### 3.1 Reference source, and why `GetBars` is deliberately not used

**PRIMARY REFERENCE: the `db/minute` per-session store** — an independently derived trade-volume
total already on disk, written by a different NT8 subsystem at a different granularity. The test is
`sum(minute volume over a contract-session) == daily bar volume for that contract-session`.

> ⛔ **`GetBars` / `BarsRequest` is NOT used as the reference.** A `GetBars` call **writes its
> download into `db/day/<REQUESTED ID>/<YEAR>.Last.ncd`** — it is the very writer that produced the
> store under test. Using it as its own reference is **circular**, and it would **mutate the
> evidence** while certifying it. Both are disqualifying. **`AddDataSeries` is barred outright** as
> the merged path.

**Minute reader.** The daily record layout is known (28-byte header; 48-byte record
`int64 ticks | float64 OHLC | int64 volume`). The minute layout is **not assumed**. It is accepted
only if a candidate layout satisfies, structurally: `(filesize − header)` divisible by the record
size; timestamps strictly increasing; every timestamp inside the named session's plausible window;
`high ≥ max(open, close)`, `low ≤ min(open, close)`; `volume ≥ 0`. **If no layout satisfies these,
the minute reference is `UNAVAILABLE`** — see §3.7.

**Session alignment.** CME sessions run 18:00 → 17:00 ET, so a session may be labelled by either
calendar date. Two alignments are declared now and both are reported:

| | rule |
|---|---|
| **A0** | minute file `YYYYMMDD` ↔ daily bar whose normalized date **equals** `YYYYMMDD` |
| **A1** | minute file `YYYYMMDD` ↔ daily bar at `YYYYMMDD ± 1` calendar day |

The alignment with the higher exact-match rate is adopted and named. **This is a labelling question
resolved on data, declared before measurement, and it is not a tolerance.**

### 3.2 The five certification clauses

| # | clause | statistic | **PASS requires** |
|---|---|---|---|
| **V1** | **cross-source identity** | exact-match rate of `sum(minute vol)` vs `day vol` on aligned contract-days, under the adopted alignment | **≥ 95 %** exact, **or** ≥ 95 % within a relative error of **0.5 %** with the residual explained and reported |
| **V2** | **no duplication between simultaneously listed contracts** | share of root-days carrying ≥ 2 live contracts on which **two contracts report identical volume**, counting only pairs whose shared volume **≥ 1,000** (small shared values are legitimate coincidences) | **≤ 0.5 %** |
| **V3** | **front ≠ deferred** | median of `volume(2nd-nearest live contract) / volume(designated contract)` over all root-days with ≥ 2 live contracts | **< 0.25** — a merged copy gives exactly **1.000** |
| **V4** | **field semantics** | dtype, sign, integrality | volume is a non-negative **integer**; **zero** volume-days counted and reported; **no negative** values |
| **V5** | **volume collapses into expiry** | per contract, median volume over its **last 5 traded days** ÷ its own **63-day trailing median**, taken across all contracts of all roots | **median < 0.50** — under a merged front-month copy an expiring back contract would show **no** collapse |

**V2, V3 and V5 are direct tests of the exact failure mode.** They are structural: a root-level
merged front-volume series copied into every contract cannot pass any of the three.

### 3.3 Provenance record (mandatory output)

For the volume field: source directory, file name pattern, header size, record dtype, byte offset of
the volume field, reader function and its **git blob hash**, and the count of files read. **A
nearest numerical match is not evidence of mechanism** — the producing artifact and the producing
code are both named.

### 3.4 Causal active-contract contract (§3C of the directive)

The existing causal roll ledger is **recovered, not reinvented.** No new volume-based roll
algorithm is written.

**To be stated exactly and asserted in code:**

- `research/multi_market/src/roll.py::build_roll_ledger` compares the current vs next eligible
  contract using **volume at `t−1` only**, and the roll takes effect on `t`. **The roll for day `t`
  uses `t−1` volume. This is stated plainly because it is true.**
- The safety override (`PRE_EXPIRY_BUFFER_DAYS = 5`) is a property of the **contract**, known in
  advance, and uses no price or volume at all.
- `roll.test_roll_causality` is re-run and recorded: perturbing `t−1` volume **must** move the
  ledger (teeth), perturbing day-`t` volume **must not** (causality).
- The real ledger assertion is re-run: every `info_cutoff` is **strictly** before its
  `decision_date`.

> ### **BINDING CONSEQUENCE FOR THE SIGNAL, committed now:**
> **No same-day final volume may enter a signal that predicts that same day's already-earned
> return.** Week `W`'s positions may use volume only from sessions **completed strictly before `W`
> begins.**

### 3.5 Roll-entanglement audit (§3D) — measured WITHOUT returns

Volume is already involved in contract selection, so the audit is mandatory. Reported per root and
pooled, **using no return or P&L**:

- signal-eligible days within 1 / 3 / 5 sessions of a causal roll;
- the distribution of the designated-contract **log-volume jump at the switch itself**, defined as
  `LV(new contract, roll date) − LV(old contract, roll date)` — a same-day, same-market difference,
  so it isolates the contract switch and nothing else;
- share of extreme `|ZVOL| > 2` observations within 1 / 3 / 5 sessions of a causal roll, against the
  unconditional rate on days farther than that radius from any roll;
- history available for the newly active contract at the moment it becomes active;
- whether root-level active-volume continuity is **mechanically broken** at rolls.

⚠️ **This is expected to bind.** The substrate carries **210 forced pre-expiry rolls for `CL`** and
**68–70 for every FX root** against 0–2 volume-crossover rolls, so a designated-contract volume
series can jump downward at a forced roll for a purely mechanical reason. A mechanical drop would
read as "abnormally low participation" and manufacture a long signal out of the calendar.

### 3.6 REPRESENTATION DECISION RULE — frozen now, resolved by data only

Let `J` = the fraction of causal roll dates whose same-day contract-switch log-volume jump exceeds
**1.0** in units of the root's own trailing `1.4826 × MAD63` of `LV`.

| condition | representation adopted for the whole campaign |
|---|---|
| **`J ≤ 0.10`** | **DESIGNATED-CONTRACT volume** — the volume of the causally active contract |
| **`J > 0.10`** | **ROOT-TOTAL volume** — the sum of volume across **all live contracts** of that root on date `d`, which is **invariant to which contract is designated** and therefore cannot jump at a roll |

**Both branches are legitimate liquidity measures and the choice is made on roll mechanics, never on
alpha.** Note the coupling: the root-total branch is only meaningful **because** V2/V3 certify the
per-contract fields are not duplicated copies — under a merged copy the sum would be `n ×` the
front. **The two branches are never compared by performance.**

**ROLL EMBARGO `E`** — a deterministic ladder, evaluated on the adopted representation. Let `x(e)`
be the `|ZVOL| > 2` rate within `±e` sessions of a roll divided by the rate at distance `> e`:

```
E = 0  if x(1) <= 1.5
E = 1  elif x(3) <= 1.5
E = 3  elif x(5) <= 1.5
E = 5  otherwise
```

`E` excludes an observation from **entering the rolling median/MAD and from being the current
observation**. It is a **feature-hygiene rule only**: positions still roll normally and still pay
real roll turnover costs.

### 3.7 Failure and fallback rules — declared before the result

| finding | verdict |
|---|---|
| **V2, V3 or V5 fails** | **`VOLUME SEMANTICS NOT CERTIFIED` → STOP.** The family closes. Do not alpha-test an ambiguous field |
| **V1 fails under both alignments** | **`VOLUME SEMANTICS NOT CERTIFIED` → STOP.** Sources disagree |
| **V4 fails** | **`VOLUME SEMANTICS NOT CERTIFIED` → STOP** |
| **minute reference `UNAVAILABLE`, or < 200 aligned contract-days** | **not** a disagreement. V1 is recorded `REFERENCE UNAVAILABLE`; certification rests on the structural clauses V2–V5, and the verdict is **downgraded and carried in every later report** as **`CONTRACT-SPECIFIC BY STRUCTURE, NOT CROSS-SOURCE VERIFIED`** |
| **causal-roll defect** | **STOP.** No alpha on a non-causal active-contract series |
| **capability gates (§6) fail** | **`VOLUME_LIQUIDITY = CLOSED-BY-DATA` → STOP.** No extra data is fetched in this campaign |

## 4. What VOLUME00 may NOT do

**No return. No P&L. No Sharpe. No signal-vs-return correlation. No model. No universe change based
on anything but §6. No parameter chosen by looking at an outcome.** The 63-session horizon, the MAD
scaling and the sector demean are **not** evaluated here — they are committed in `VOLUME_LIQUIDITY_V1`'s
own SPEC (commit C) and no alternative is compared by alpha at any point.

## 5. Population and seal

| | |
|---|---|
| span examined | the substrate's own span, **2009-03-31 → 2026-07-31** |
| **hard cap** | **every row `date < 2026-08-01`**, asserted in code |
| ⛔ | the **≥ 2026-08-01 global seal** is not read, not counted, not listed |
| ⛔ | no `ESNQ EFFECTIVE_14`, no NQ BBO 19, no remaining unread ES BBO, no 141-session Last-only pool — **none of these is touched by this campaign at any stage** |

## 6. Capability gates — frozen before measurement

| # | gate | requirement |
|---|---|---|
| **G1** | eligible non-micro roots | **≥ 12** |
| **G2** | economically distinct sectors | **≥ 4** |
| **G3** | usable history | **≥ 8 calendar years** |
| **G4** | eligible root-days per admitted root | **≥ 1,500** over the full pre-seal span |
| **G5** | volume coverage vs that root's canonical active-contract **price** days | **≥ 80 %** |
| **G6** | volume-semantics defect | **none unresolved** (V1–V5 per §3.7) |
| **G7** | causal-roll defect | **none** (§3.4) |

**A root is volume-eligible on date `d`** iff it is already price-eligible under the certified
substrate rule (`build_substrate.py`: designated contract present, ≥ 200 of the prior 260 business
days covered, 252-day warmup elapsed) **and** it has a volume observation **strictly greater than
zero** under the adopted representation. **A zero-volume day is counted as MISSING for volume
purposes** — `log(1+0) = 0` would otherwise be an enormous artificial outlier.

> **A threshold may be amended only BEFORE any alpha return is read, only for an explicit
> data-shape reason, and the reason must be recorded.** ⛔ **No threshold may be lowered after
> discovering that a favourite root narrowly misses it.**

## 7. Deliverables

`out/volume00.txt` (full log) · `out/volume00.json` (machine verdict) ·
`out/volume_semantics.csv` (per-clause, per-root) · `out/roll_entanglement.csv` ·
`out/coverage.csv` · `REPORT.md`.

**Commit B lands the result and is a strict descendant of this commit.** `research_sdk/prereg_guard.py`
is run in prospective mode before the measurement code executes.
