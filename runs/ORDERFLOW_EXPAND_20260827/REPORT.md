# ORDERFLOW_EXPAND — the BBO lane, extracted at zero cost

| | |
|---|---|
| **run class** | **DATA ACQUISITION + QA** — no hypothesis, no model, no feature, nothing promoted |
| date | 2026-08-27 |
| code | `src/build_runlist.py` · `src/bbo_hourly_truth.py` · `src/csv_to_substrate_v2.py` · `SWScalpTickExport_v4` |
| product | `research/data_microstructure_v2/` |
| seal | **untouched** — every window ends before 2026-08-01; the QA gate hard-fails any session dated ≥ seal |
| cost | **$0.** No purchase, no subscription, no new charge |

> ### **The BBO substrate goes 42 → 98 QA-passed sessions. 780 million events, 2.46 GB.**
> ### It was all already on this disk. The blocker was **manual labour**, not money.

---

## 1. What was actually built

| | |
|---|---|
| sessions | **58 new**, `2025-10-15` → `2026-07-31` |
| events | **780,167,968** — 31.3 M trades · 373.1 M bid · 375.8 M ask |
| size | 2.46 GB parquet (zstd) |
| contracts | `NQ 12-25` · `NQ 03-26` · `NQ 06-26` · `NQ 09-26` |
| quote coverage | **min 0.9993** bid and ask, as a fraction of session minutes |
| provenance | every row: contract, source, acquisition method, **sha256** (58 unique of 58) |

**Union with the pre-existing 48-session substrate: 104 distinct sessions**, of which **98 carry full
quote coverage** — against 42 before. The old substrate is **left untouched** so every prior wave
stays bit-reproducible.

### Why a new directory and not an extension

`research/scalping_lab/substrate/raw/NQ` is **not uniform**. **17 of its 48 files sit at exactly
12,000,000 rows** — the v1 exporter's cap — meaning they are **silently truncated mid-session**
(`s20260206` ends 13:28:44 instead of 16:59:59). Three carry no quotes at all. Appending to that
would produce one directory whose files mean different things. `SWScalpTickExport_v4` raises the cap
to 25 M and **rolls output per session date**; the largest session extracted here is **22.8 M rows**,
which the old cap would have cut by nearly half.

## 2. ⚠️ Two defects the pilots caught, either of which would have corrupted the substrate silently

**Neither would have shown up in a row count.** Both were found by checking **per-series time
ranges** on a single session before any batch ran.

**(a) The window loaded two sessions, not one.** NT8's Strategy Analyzer treats `from` as a **date**
and loads the session *dated* that day — which already begins at `D-1` 18:00 ET. My runlist
subtracted a day NT8 already subtracts. A request for session `2025-08-13` returned data from
`2025-08-11 18:00`. Fixed: `from` is now **midday on `D` itself**.

**(b) The BBO session count was measured at the wrong granularity — corrected in `44a8678`.**
A session spans **two calendar dates** of `.ncd` files, so date-level presence does not establish
session-level coverage. Recomputed at hour granularity, **BBO-FULL is 99, not 168**, and
**`Last`-complete is 243, not 310**. The claim that signed flow *"MEETS the ~300-session target"*
was **retracted** — it reaches **81 %** of it.

## 3. QA — gates, not vibes

Every session is gated before it enters the substrate: row count, session span, **single session
date under the 18:00 roll**, out-of-order events, duplicate rows, price sanity, and a hard
**`SEALED`** check that no session dated ≥ 2026-08-01 can ever pass.

| verdict | n |
|---|---:|
| `OK` | **58** |
| `QUARANTINE:short_span` | **1** — `s20260525`, span 19.0 h, 2.17 M rows |

**`s20260525` is Memorial Day** — a genuine early-close session, correctly refused rather than
silently averaged in. This is the same class of object that broke `XM_CONFLICT_v1`: an early-close
holiday the research substrate drops but the executable traded. The gate caught it unprompted.

## 4. What remains — specified, resumable, not hand-waved

| lane | now | ceiling on this disk | bar |
|---|---:|---:|---|
| **BBO / quote** | **98** | 99 | ~300 — **33 %**, still short |
| **signed flow** (`Last`) | ~104 | **243** | ~300 — **81 %**, still short |

**~139 sessions remain unextracted for the signed-flow lane.** They are enumerated in
`out/runlist.csv` with contract, corrected UTC window, and hour-level coverage class, so the job
resumes with no rediscovery. They are cheap — quote-less sessions are ~10× smaller than these.

> ⚠️ **Neither lane clears its own preregistered bar even fully extracted.** That is the honest
> position and it does not change with more effort here: **99 is the ceiling this disk holds** for
> quote-based work. Closing the rest is an acquisition question, which is exactly what `OQ-5` now
> says after being re-scoped.

## 5. Resource safety

`C:` was at **25 GB free** and holds the 11 GB NT8 store, so **every CSV was written to `D:`** and
**deleted immediately after conversion**. Peak `D:` consumption was ~10 GB against 173 GB free;
final footprint is 2.46 GB. NT8 RSS peaked at ~2.3 GB against 40 GB available. Concurrency was held
at **3–4 jobs**. **No continuous capture was started. No DOM/L2 collection was resumed.**

## 6. Continuation

| | |
|---|---|
| **outcome** | BBO substrate **42 → 98**; a clean, uniform, hash-stamped, QA-gated substrate exists |
| **next** | **Stage-A information test only** — does microstructure predict full-horizon `delta_action_value` incrementally? Information before policy, per directive §9 |
| **promoted / demoted** | **nothing.** This run measures no edge and selects no hypothesis |
| **acquired** | **nothing paid.** Data already on disk, extracted with tools already installed |
