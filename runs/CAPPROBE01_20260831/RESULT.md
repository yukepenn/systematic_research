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