# BBO GOVERNANCE MEMO — which unextracted pre-seal NQ full-BBO tick sessions are SAFE to extract

**2026-09-06 · read-only governance check. Nothing was extracted; no price or outcome content
was read.** Inputs: the capability census CSV (metadata), pool manifest CSVs/TXTs (name lists),
and file NAMES in the extraction substrate directories.

## Headline

> **The "~129 unextracted sessions" premise dissolves under measurement. The true unextracted
> candidate set is 57 sessions, of which 55 are frozen-pool members (BLOCKED) and exactly
> 2 are SAFE: `2026-06-19` and `2026-07-03` — both holiday early-close sessions.**

Two definitional corrections produced the collapse, both verified from artifacts:

1. **187 "sessions" are calendar FILE dates, not sessions.** 29 of the 187 are Sundays, whose
   files are the evening leg (18:00–23:59 ET) of the following Monday session
   (`runs/NQ1M_BIDASK_EXTRACT_20260906/MANIFEST.md` records the same fold for minute data).
   After folding, the owned pre-seal full-BBO universe is **158 distinct sessions**
   (2025-08-13 → 2026-07-31). Every one of the 29 Sunday legs pairs with a Monday that has its
   own census files — none stands alone.
2. **"~58 already extracted" was one of three substrates.** On disk today: v2 substrate
   58 (`research/data_microstructure_v2/raw/NQ`), scalping-lab v1 61 files / 48+13 RTH dates
   (`research/scalping_lab/substrate/raw/NQ`), ESNQ dev 44 (`research/data_esnq/parquet/NQ`).
   **Union: 104 sessions already materialized.** 158 − 104-that-overlap = **57 unextracted.**

## The intersection (exact, computed)

| set | n | span |
|---|---:|---|
| owned pre-seal full-BBO calendar dates (census, Last∧Bid∧Ask PAYLOAD, < 2026-08-01) | 187 | 2025-08-13 → 2026-07-31 |
| distinct sessions after Sunday fold | 158 | 2025-08-13 → 2026-07-31 |
| already materialized (3-substrate union, file names only) | 104 | — |
| **unextracted candidate sessions** | **57** | 2025-08-13 → 2026-07-03 |
| **BLOCKED (in ≥1 frozen pool)** | **55** | 2025-08-13 → 2026-05-25 |
| **SAFE (no pool, pre-seal, unextracted)** | **2** | **2026-06-19, 2026-07-03** |

Blocked attribution (overlapping — one session can sit in several pools):

| register | members among the 55 blocked |
|---|---:|
| `W5 PROTECTED 168-pool` minus batch-1 (160 protected-untouched) — `runs/W5_PROTECTED_CONFIRMATION/manifest_work/confirmation_pool_168_dates.txt` | **55 of 55** |
| `MICRO_BLIND_CONFIRMATION_POOL` (141) — `runs/MICRO_DISCOVERY_CONFIRMATION_SPLIT/out/MICRO_BLIND_CONFIRMATION_POOL.csv` | 52 |
| `BBO_BLIND_POOL` (19) — `runs/BBO_COMPLETENESS_RECENSUS_V1_20260828/out/BBO_BLIND_POOL_MANIFEST.csv` | 19 |
| `ESNQ_BLIND_15` / `EFFECTIVE_14` (NQ side of the paired sessions) — `runs/ESNQ_V1_20260828/manifests/` | 15 |

Pool nesting, measured: the 19 BBO pool ⊂ the 141 MICRO pool ⊂ the W5 protected 160; the
ESNQ 15 ⊂ all three. **Every unextracted session from the Aug-2025→May-2026 stretch is a W5
pool member** — the W5 dev window *was* the owned tick+BBO universe when that pool was frozen,
so nothing in that stretch is governance-free. No pool member has been tick-extracted
(pool ∩ extracted = 0 for BBO/MICRO/ESNQ registers; 13 W5 members were batch-consumed or
later legitimately materialized by MS01/ESNQ dev — all outside the 55).

Seal check: all 57 candidates < 2026-08-01 — **PASS**. The census's 9 post-seal full-BBO dates
(2026-08-01 → 2026-08-11) were excluded by construction. Note for any future export: calendar
date 2026-07-31's evening files belong to the sealed 2026-08-03 session; the export `to` must be
the 2026-07-31 session-close boundary, exactly as `NQ1M_BIDASK_EXTRACT_20260906` did it.

## The 2 SAFE sessions

| session | day | notes |
|---|---|---|
| 2026-06-19 | Fri | Juneteenth observed, early close (~1,140 min bars) |
| 2026-07-03 | Fri | July-4th observed, early close |

Both are inside the **BURNED** window (2026-05-31 → 2026-07-31): extraction is seal-legal and
pool-legal, and anything computed on them carries the BURNED / LEGACY_DIAGNOSTIC evidence tag —
engineering/cost use (spread curves, latency) is the honest purpose, not alpha evidence.

## RULING: **GO — for the 2-session safe subset only.** HOLD on the other 55.

- **GO**: extract `2026-06-19` and `2026-07-03` whenever an extraction wave runs. $0, no pool,
  no seal, prior evening sessions (06-18, 07-02) are already-materialized non-pool sessions so
  the session windows touch nothing frozen.
- **HOLD**: the remaining 55. Materializing a pool member's price content into a parquet is
  exactly the exposure the pools exist to prevent, and `blindguard` freezes by manifest name —
  it cannot detect that an extraction read the substrate. Opening any of them requires the
  pools' own protocols (W5: a new frozen preregistration bundle per AMENDMENT_3; MICRO/BBO:
  a genuinely different mechanism frozen without reading the pool, one shot) — an **owner /
  preregistration decision, not an extraction-wave decision.**
- The XM sub-second latency-curve motivation (`G3_XMLAT_01` X3) **cannot be fed from the safe
  subset** (n=2, both holiday sessions). If that measurement matters, the honest paths are
  (a) spend pool sessions under a preregistered protocol, or (b) probe provider-side history
  for non-pool dates — both owner-gated.

## Two observations surfaced en route (flagged, not ruled on here)

1. 🔴 **`NQ1M_BIDASK_EXTRACT_20260906` already materialized minute-BBO quote content on 5
   frozen-pool dates** — 2026-05-04, 05-07, 05-08 (MICRO+W5), **2026-05-05 (BBO_BLIND_POOL +
   ESNQ + MICRO + W5)**, and 2026-05-25 (W5) — and printed their per-session spread stats in a
   committed MANIFEST. The pools are *tick* pools and their tick content remains unread, but
   minute-close quote width derived from the same underlying quote stream has now been read
   and published for those dates. Combined with the 2026-09-01 freeze-defect finding (pools
   frozen by name; substrate backfilled post-freeze), any future one-shot spend against these
   pools must disclose this partial exposure.
2. The `DATA_VERDICT_20260831` figures "187 sessions / ~58 extracted / 129 to extract" are a
   calendar-date count, a single-substrate count, and their difference. The true numbers are
   158 / 104 / 57. Suggest correcting the verdict doc the next time it is touched (not done
   here — outside this check's write scope).

## Method / reproduction

`scratchpad/bbo_governance_check2.py` (session-level; pass-1 calendar-level variant agrees
after the fold). Census filter: `kind=tick, root=NQ, payload_class=PAYLOAD`, date carrying all
three of Last/Bid/Ask; Sunday→Monday fold; extracted = parquet file names in the three
substrate dirs (`s<yyyymmdd>[_rth].parquet`); pools = the four manifest name-lists above;
blocked = candidate ∩ (union of pools); registers also checked:
`research/operational/LOCKED_FORWARD.md` (seal ≥ 2026-08-01 + 2026-08-30 scoped-burn
amendment), `research/operational/ALPHA_EVIDENCE_CLASSIFICATION.md` (19-pool row),
`research/operational/BLIND_POOL_FREEZE_DEFECT_20260901.md` (pool inventory incl. W5),
`research/system_master/PROTECTED_EVIDENCE_BUDGET.md` (168-pool arithmetic, batch-1 8).
Cross-checks: census replicates DATA_VERDICT exactly (196 all / 187 pre-seal); 19-pool fully
inside the candidate set pre-intersection; `208 − 40 = 168` and `8 ⊂ 168` re-verified from the
`.txt` manifests.
