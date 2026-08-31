# CAPPROBE01 — RESULT: **PASS.** The 2022 start was a FETCH boundary, not a data boundary.

Preregistered `spec.txt` committed `69df1ae` BEFORE any provider call. Gate frozen: PASS iff >=90%
of probed dates return >=300 bars, scored per symbol. No economic statistic computed.

## OBSERVED

| year | files | with payload | coverage |
|---|---:|---:|---:|
| **2013** | 264 | **252** | **95.5 %** |
| **2015** | 249 | **247** | **99.2 %** |
| **2017** | 251 | **251** | **100 %** |
| 2022-2026 (pre-existing) | 1,415 | 1,151 | — |

**`db\minute\^TICK` went 1,419 -> 2,183 files.** Three complete pre-2022 years, **750 payload
sessions**, acquired in minutes for **$0** on the already-paid connection.

Sample values are real, not residue: 2013-03-13 ranged -492 to +434; 2013-12-31 -787 to +751.

## WHY THIS WAS NOT THE VX/VXM ERROR

The prior "VX/VXM already in NT8" claim was FALSE because probe residue looked like data. That
failure mode was tested for FIRST and the signature discriminates: the store holds **206 empty files
at <=32 B** against a payload median of **3,298 B**. The four pre-2022 files that already existed
(20130102, 20150102, 20180709, 20180710) were all 3,148-3,537 B — genuine payloads. The probe
confirmed it by materialising three full years at the same median.

## WHAT IT UNLOCKS

`INTERNALS_ACQUIRE` was measured **MARGINAL at 1.07x its own bar — failing by 7 %**, the closest any
new surface has come. Its binding constraint was N. Joinable internals+NQ sessions were ~1,147; a
completed 2013-2021 backfill takes that toward ~3,380 (**2.95x**), so every MDE in the family
multiplies by **1/sqrt(2.95) = 0.58**. A lane failing by 7 % crosses comfortably at 0.58x.

The recovered window also contains precisely the regimes `TICK01`'s own closure said its window
lacked (Aug-2015, Jan-2016, Feb-2018, Oct/Dec-2018, Feb/Mar-2020) — its event class ran **44/yr
outside** the tested window versus **2/yr inside** it.

## ⚠️ ACQUISITION IS FREE. SPENDING IT IS A SEPARATE OWNER DECISION.

- 2013-2021 carries **family-selection debt** from prior campaigns.
- **ERABREAK01 (p=0.0011)** makes pre-2022 intraday-vol statistics **inadmissible as pooled modern
  priors** — admissible only **era-stratified**, or as the discovery half of a preregistered
  discovery/confirmation split.
- ⛔ **PERMANENT CEILING NO ACQUISITION REMOVES:** `$TICK`/`$TRIN` exist **only in RTH**, while P1 is
  a **~62 %-overnight book**. Internals can never speak to two-thirds of P1's decisions. This raises
  n on the RTH third; it does not touch that ceiling.

## OPEN / MECHANICAL

- 2014 and 2016 returned a **cached tail without fetching** (the wide 2014-2021 range did the same —
  it exceeds a bar cap). Year-by-year works; those two need a retry. Mechanical, not a research
  question.
- `^TRIN` (1,398 files) **not yet probed**. Same method applies.
- This is the **fourth** instance in this repo of *"we don't have X"* meaning *"this repo hasn't
  fetched X"* — after MNQ tick, the order-flow session count, and the L1 store undercount.
---

## BACKFILL EXECUTED 2026-08-31 — **1,770 pre-2022 sessions now local, up from 4**

`db\minute\^TICK` : **1,419 -> 3,234 files**. All acquired free, read-only, on the already-paid
connection. **No P&L computed on any of it.**

| year | files | payload | |
|---|---:|---:|---|
| 2013 | 264 | **252** | FULL |
| 2014 | 132 | 129 | H2 |
| 2015 | 249 | **247** | FULL |
| 2016 | 129 | 129 | H2 |
| 2017 | 251 | **251** | FULL |
| 2018 | 251 | **251** | FULL |
| 2019 | 128 | 128 | H2 |
| 2020 | 269 | **253** | FULL |
| 2021 | 145 | 129 | H2 |

**PRE-2022 PAYLOAD SESSIONS: 1,770** (session start: 4). Every date scored payload-vs-empty with the
**<=32 B residue signature** against a ~3,298 B payload median — the same discriminator that exposed
the earlier false "VX/VXM already in NT8" claim.

### ⚠️ THE BOUNDARY TRAP — and the workaround. This is the durable finding.

Two distinct request patterns silently return **cached data instead of fetching**, both with
`success: true`, so **HTTP success is not evidence of a fetch**:

1. **A multi-year range** (e.g. 2014-01-01 -> 2021-12-31) exceeds a bar cap and returns the tail of
   what is already cached. It looks like a successful call and acquires nothing.
2. **A year request whose start abuts the previously-fetched year** returns that year's cached tail.
   After fetching 2013, the 2014 request returns `2013-12-31`; after 2015, the 2016 request returns
   `2015-12-31`; after 2020, the 2021 request returns `2020-12-31`.

**The tell is LATENCY, and it is unambiguous: a real fetch takes ~750-1,300 ms; a cache return takes
~10-15 ms.** Score on that, and on the resulting files — never on `success`.

✅ **WORKAROUND, verified on all four stuck years: start the request MID-PERIOD** so it does not abut
the cache boundary. `2021-07-01 -> 2021-12-31` fetched in 807 ms where `2021-01-01 -> …` had returned
cache in 15 ms. Same for 2019 (784 ms), 2014 (891 ms) and 2016 (763 ms).

⚠️ **A year returning cache does NOT mean the data is absent.** 2016 looked missing four times, then
a narrow probe at `2016-06-15` returned real values (-567 to +695). **Never infer absence from a
cache return** — that is this repo's recurring error in a new costume.

### REMAINING (mechanical, not a research question)

H1 of 2014, 2016, 2019, 2021 — roughly 500 further sessions, reachable with the same mid-period
workaround. `^TRIN` (1,398 files) not yet probed; same method applies.

### GOVERNANCE — UNCHANGED AND NOT CROSSED

Acquisition is free; **SPENDING this window is a separate owner decision.** 2013-2021 carries
family-selection debt, and **ERABREAK01 (p=0.0011)** makes pre-2022 intraday-vol statistics
inadmissible as pooled modern priors — admissible only **era-stratified**, or as the discovery half
of a preregistered discovery/confirmation split. **No statistic has been computed on the new data.**
And the permanent ceiling stands: `$TICK`/`$TRIN` are **RTH-only** while P1 is a ~62 %-overnight book.