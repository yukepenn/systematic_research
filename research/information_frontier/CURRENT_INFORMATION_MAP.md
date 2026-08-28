# CURRENT INFORMATION MAP — what the project actually owns

**Information, not strategies.** 2026-08-28. `RO` = raw observable · `TX` = transformation.

> ## ⚠️ **THE HEADLINE: THE FREE TIER IS NOT EXHAUSTED.**
> The frontier currently says *"the free surfaces are exhausted."* **That is false**, and the items
> below were found by **probing the connection and the disk**, not by reading a marketing page —
> the same method that previously produced `$TICK/$TRIN/$VIX`, the 243/99 tick ceiling and 17.6-year
> multi-market depth.

---

## 1. Raw observable channels the project OWNS

| # | family | class | coverage | causal | used in alpha? | protected |
|---|---|---|---|---|---|---|
| **R1** | NQ 1-min Last OHLCV — deep | RO | 2006-01-05 → 2026-05-29, 6,466,783 rows | PARTIAL | ✅ the spine, 123 waves | discovery-consumed |
| **R2** | NQ 1-min Last OHLCV — modern | RO | 2022-01-02 18:01 → 2026-07-31 16:59, **1,620,044 bars / 1,058 sessions** | PARTIAL | ✅ P1/PCT, XM, Program B | 2026-05-31→07-31 **BURNED** |
| **R3** | NQ 1-min volume | RO | full history, 0 nulls | PARTIAL | ✅ `W111` (anti-predictive) | inherits parent |
| **R4** | ES / YM / RTY 1-min Last | RO | 1,058 common sessions | PARTIAL | ✅ `XM_CONFLICT_v2`, `W122` | seal-clean |
| **R7/R8/R9** | NQ tick + BBO | RO | **104 materialized** of a **243 Last / 99 quote** store ceiling | PARTIAL | ✅ MS-BBO (**VOID**), `ESNQ_V1` | ⚠️ v1 lane **defect-limited**: 15 files at exactly 12,000,000 rows = exporter cap, truncated mid-session. **Do not merge v1 with v2** |
| **R11+** | ES tick + BBO | RO | 79 pre-seal RTH-complete | PARTIAL | ✅ `ESNQ_V1` (44 consumed) | 15 blind · **20 unread** |
| — | multi-market daily unmerged | RO | 21 roots · 6 sectors · 2009→2026 | ✅ certified | ✅ TSMOM, CARRY, VOLUME | seal-capped |

## 2. ⭐ RAW OBSERVABLES THE PROJECT OWNS AND HAS **NEVER READ** — all $0

| # | item | why it matters | status |
|---|---|---|---|
| **F3** | **VX / VXM futures — daily AND 1-minute OHLCV, multiple contract months, already in NT8** | **the VIX futures term structure.** ⚠️ **Never named in ANY repo data document.** The canonical liquidity-stress / vol-regime conditioner | **UNACQUIRED, $0** |
| **F2** | **`$TICK` 1-minute back to ~2013** on the existing connection | the repo believes internals are `REGIME-LOCAL (2022+)`. Probe returns bars at **2013-01-02 and 2015-01-02**. **~9–13 extra years** — converts internals from regime-local to multi-era | **UNACQUIRED, $0** |
| **R10** | **MNQ tick — 187 dates, 128 pre-burn, never read** | a **separate order book** with a retail-weighted participant mix. ⚠️ **Absent from the registry** because `build_registry.py:197-206` hard-codes `symbol="NQ"` — an invisibility bug, not an absence | **ENTIRELY UNSPENT, $0** |
| **R5** | **nine unextracted 1-min futures stores** — ES, CL, MNQ, RTY, YM, ZB, 6J, ZN, MGC | `evidence_class` = **`unclassified`** for all nine. CL/ZB/6J/ZN/MGC are genuinely **new sectors**. The largest untested intraday surface named anywhere | **$0**, completeness **UNAUDITED** |
| ~~**R9b**~~ | ~~141 NQ Last-usable tick sessions "extractable at $0"~~ | ⚠️ **GOVERNANCE CORRECTION — THESE ARE THE PROTECTED BLIND POOL.** The 141 unextracted Last-usable sessions **are** the frozen 141-session Last-only pool (`fd7b05f`). **Extraction MATERIALIZES a protected asset** — exactly the act that caused the `ESNQ` blind-export incident. **Free in dollars, NOT free in governance.** Requires blind-spend authorization behind a frozen mechanism | ⛔ **NOT a free item** |
| — | Cboe free CDN/CFE files | `VIX_History` (1990→), `VIX3M` (2009→), VX/VXM/**IBHY/IBIG** settlements, CFE volume + **open interest** (2004→) | **public, $0** |
| — | FRED / ALFRED **vintages**, BLS/BEA/Census schedules | point-in-time vintages are the **correct revision handle**; BLS/BEA are the **authoritative** release times every vendor copies | **public domain** |
| — | **CFTC Commitments of Traders** | free, weekly — the **crowding axis**. ⚠️ **Absent from both censuses, UNPROBED** | **$0** |
| — | RTY / RB / HO / HG curve data | closed-by-**cache**, recoverable; attacks `CARRY_V1`'s `n_sector = 2` degeneracy | **$0** |

## 3. ⚠️ Two recorded conclusions this census contradicts

> ### **C1 — "Order flow is CLOSED-BY-POWER, unreachable at any coverage (998 needed, 713 exist)."**
> **713 is the ceiling of the LOCAL NT8 tick store, not of acquirable data.** Databento
> `GLBX.MDP3` carries CME NQ **MBO from 2017-05-21** (order-level, so signed flow is *exactly*
> derivable) and MBP-10 from 2010-06-06 — on the order of **~2,300 sessions**.
> **The impossibility arithmetic is not established.** This is the same failure mode the repo
> already diagnosed once: *"'no data' was a statement about this REPO, not the connection."*
> ⚠️ The closure may still hold **on evidence**; what is withdrawn is the claim that it holds
> **by arithmetic**.

> ### **C2 — internals are `REGIME-LOCAL (2022+)`.**
> True of the **store**. False of the **feed** — see F2. A prior claim of hidden pre-2022 depth was
> retracted on store evidence; the retraction was right about the store and **wrong as a general
> claim**.

## 4. Transformations — not information families

Everything computable from OHLC / Last / BBO / volume / VWAP / moving averages the project already
holds is a **`TRANSFORMATION`**, however it is branded. That includes the externally-sourced
indicator families examined in campaign #6 (VWAP-flux-shaped tools, sweep detectors, auction
overlays, trend composites). **FEATURE NAME ≠ OBSERVED FIELD.**

**Metadata note:** a harness clock briefly reported 2026-08-18 while every run and state document is
dated 2026-08-27/28. **Resolved: the correct date is 2026-08-28**; the maps are written to the
document dates.
