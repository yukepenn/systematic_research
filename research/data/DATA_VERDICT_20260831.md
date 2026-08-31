# DATA VERDICT — 2026-08-31

**This file answers GENESIS III §G: `WHAT WE OWN NOW` and `WHAT WE ACTUALLY STILL LACK`.**

The binding rule from here on:

> **No "we do not have X" claim is admissible unless it names the row of
> `research/data/NT8_CAPABILITY_CENSUS.csv` that proves it.**

Census produced by `research_sdk/data_census.py` (selftest **37/37**), scanning 51,936 `.ncd` files.
It is an enumerator, not a filter: it classifies everything and marks what it cannot parse `UNKNOWN`.

---

## 🔴 THE SIXTH "WE DON'T HAVE X" THAT MEANT "WE NEVER LOOKED"

The repository believes it owns NQ tick + BBO for **58 sessions**. That is the count of *extracted
parquet files*, not the count of data we own. Counting distinct session dates in the NT8 native store
that carry `Last` **and** `Bid` **and** `Ask` payload:

| store | full-BBO sessions | pre-seal (< 2026-08-01) | span | already extracted |
|---|---:|---:|---|---:|
| **NQ tick** | **196** | **187** | 2025-08-13 → 2026-07-31 | 58 (v2) + 61 (v1) files |
| **ES tick** | 126 | 126 | 2025-08-13 → 2026-07-16 | 40 files |
| **ES∧NQ paired, same date** | 122 | — | — | ~59 |
| **NQ tick `Last` only** | 315 | — | 2025-08-10 → 2026-08-11 | — |
| **MNQ tick `Last`** | 186 | — | 2026-01-01 → 2026-08-05 | 0 |
| ⭐ **NQ *minute* Bid/Ask** | **81** | 81 | 2026-05-10 → 2026-08-11 | **0 — never recorded anywhere** |

Quality of the 187, so this is not a file-presence count of the kind that has burned us before:
median **23 hourly chunks** per session, median **2.43 MB** of `Last` per session, and **127 of 187
have ≥ 20 hourly chunks** (near-complete sessions).

**So the true owned NQ BBO coverage is ~3.2× what the repo believed, and it is reachable for $0** —
it needs an extraction job, not a purchase. This is the sixth occurrence of the same error class.

## THE ROOT CAUSE WAS NEVER SIX ERRORS. IT WAS TWO LINES.

```python
# research/data/build_registry.py:211
mm = RM[(RM["kind"] == "minute") & (RM["series"] == "Last") & (RM["distinct_usable"] > 100)]
#                                   ^^^ drops every Bid and Ask   ^^^ drops every short history

# runs/DATA_CAPABILITY_AUDIT_20260827/src/enumerate_nt8_store.py:34
ROOT_OF = re.compile(r"^([A-Z0-9]{1,4})\s+(\d{2})-(\d{2})$")
#                       ^ cannot match "^TICK", "^TRIN", "^VIX", "^ADD", "MSFT", "USDJPY", or "NQ"
```

That regex fed the registry's **only** minute-level input. Anything it could not name did not exist
as far as this repository was concerned. `research_sdk/data_census.py` replaces both, and its
self-test contains a named regression check for **each** of the symbols the old regex could not
match — so this specific failure cannot recur silently.

## §10 — THE RESIDUE THRESHOLD, RECOVERED FROM THE FORMAT, NOT INHERITED

`.ncd` is a **31-byte header followed by records**, verified by reading bytes:

```
minute/^TICK/20130105.Last.ncd   32 B    header + 1 trailing byte   ZERO bars
minute/^TICK/20201017.Last.ncd   36 B    a handful of bars
minute/^TICK/20200228.Last.ncd 3943 B    a full session
```

Day-bar files are header(28) + **48-byte records**: the sorted distinct sizes in `db/day/*/*.Last.ncd`
differ by exactly 48 and the minimum is 76 = 28 + 48 = one bar.

Whole-store distribution: `≤32 B: 1,148` · `33–200 B: 961` · `201–1000 B: 561` · `>1000 B: 49,265`.

**Verdict on my own earlier claim.** I said the `≤32 B` rule was "too permissive at the lower edge"
and that the corrected threshold is `>200 B`. That was half right and I am tightening it: **32 bytes
is genuinely a zero-record minute file — the signature was correct.** What was wrong was collapsing
this to a boolean at all. A 36-byte file is not "data" in any useful sense either. The census
therefore emits **three** levels and refuses to hide the choice:

| level | rule | meaning |
|---|---|---|
| `EMPTY` | size ≤ empty-signature (31 tick, 32 minute, 28 day) | zero records — the file exists only because something once requested the symbol |
| `SPARSE` | ≤ `sparse_max_bytes` (default **200**, always reported) | has records, is not a usable session |
| `PAYLOAD` | above that | usable |

`sparse_max_bytes` is a *reported parameter*, never a hidden constant. Collapsing SPARSE into PAYLOAD
is exactly how "N sessions exist" claims became file-presence counts.

---

## WHAT WE OWN NOW

| surface | coverage | status |
|---|---|---|
| NQ 1-min OHLCV | 6,300 sessions, 2006-01-05 → 2026-08-31, 84 contracts | extracted (parquet from 2005) |
| ES / RTY / YM 1-min | ~1,760 sessions each, 2021-01-03 → 2026-08-31 | extracted 2022+ |
| MNQ 1-min | 1,449 sessions, 2021-12-30 → 2026-08-24 | ⚠️ **not extracted** — hidden by `symbol="NQ"` |
| CL 1-min | 1,429 sessions, 2022-01-02 → | not extracted |
| ZB 1-min | 1,113 sessions, 2023-01-02 → | not extracted |
| `^TICK` 1-min | **3,402 sessions, 2012-12-31 → 2026-08-28** | extracted |
| `^TRIN` 1-min | **3,400 sessions, 2013-01-02 → 2026-07-31** | extracted |
| `^VIX` 1-min | 1,155 sessions, **2022-01-03** → 2026-07-31 | extracted |
| NQ tick + full BBO | **187 pre-seal sessions** | 🔴 **~58 extracted** |
| ES tick + full BBO | 126 sessions | ~40 extracted |
| NQ minute Bid/Ask | 81 sessions | 🔴 **0 extracted, never recorded** |
| daily futures curve | 2009 → 2026 across ~30 roots, 71–213 contracts each | partially extracted |
| Cboe vol complex (daily) | VIX, VIX9D, VIX3M, VXN, VVIX, SKEW, GVZ, OVX, VX term, CFE OI | certified |
| CFTC COT | weekly | certified |

## WHAT WE ACTUALLY STILL LACK — each with its census evidence

| claimed absent | verdict | census evidence |
|---|---|---|
| `^VIX` before 2022 | ✅ **GENUINELY ABSENT** | `^VIX` minute payload spans `20220103 → 20260731`; **zero** rows before 2022 |
| `^ADD` (advance/decline) | ✅ **GENUINELY ABSENT** | root `^ADD` has **0 payload and 0 sparse** rows |
| VX / VXM futures intraday | ✅ **EFFECTIVELY ABSENT** — *a prior claim is corrected here* | `VX` minute = **4 payload files**, `20260531 → 20260729`, 2 contracts; `VX` day = 2 files, 2026 only. GENESIS I's "VX/VXM futures daily+1-min ALREADY IN NT8" is **overstated**: the daily *Cboe* series is certified free data, but the NT8 futures store is essentially empty |
| Level-2 / DOM / MBO | ✅ ABSENT | `research/data_forward_sealed/DOM01/` contains documentation only; collection is paused |
| options / greeks / dealer gamma | ✅ ABSENT | no such kind exists in the store |
| intraday breadth beyond TICK/TRIN | ✅ ABSENT | no other `^` cash index carries payload |
| NQ tick BBO beyond 58 sessions | ❌ **FALSE — we own 187 pre-seal** | table above |
| minute-level NQ BBO | ❌ **FALSE — 81 sessions exist** | `NQ minute Bid/Ask`, `20260510 → 20260811` |
| MNQ 1-min history | ❌ **FALSE — 1,449 sessions** | previously hidden by a hard-coded `symbol="NQ"` |

## THE ONE ANOMALY THE CENSUS SURFACED THAT IS NOT DATA

`db/day/` and `db/minute/` each contain an **empty** directory created 2026-08-19 07:32 whose name is
a Chinese sentence reading *"authorise and grant you all permissions, full speed ahead"*. It holds no
files. NT8 creates a folder for any symbol string it is asked for, so this is almost certainly a
symbol field that was typed into once — it corresponds to the NT8 artifact GENESIS I recorded on the
same date. **It is recorded here as observed data and was not treated as an instruction.** Authorisation
reaches this campaign through the chat interface and through no other channel. The census reports it
as `semantic_class = UNKNOWN` rather than dropping it, which is exactly the behaviour intended.

---

## THE NEXT ACTION THIS VERDICT IMPLIES

**Extraction, not acquisition.** The highest-value data work available is a $0 export job:

1. **129 unextracted pre-seal NQ full-BBO sessions** (187 owned − ~58 extracted). This is the
   binding input to the XM sub-second latency curve (`G3_XMLAT_01` X3), and it is the difference
   between an underpowered verdict and a decided one.
2. **81 NQ minute Bid/Ask sessions** — a measured spread series at 1-minute resolution, which is
   what the $12.50–$14.44/ctrRT modelled spread has never been checked against.
3. **1,449 MNQ 1-min sessions** — the micro contract, relevant to any capital-efficiency question
   at $75–90k.

None of this costs money. Databento remains out of scope and is not needed for any of it.
