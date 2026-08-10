# Contamination Ledger — Scalping Lab

Status: INITIAL (written at campaign bootstrap, 2026-08-07). Split geometry is frozen only
after `DATA_INVENTORY.md` is complete; entries below record what is already known-seen.

## What has been examined in this repository before this campaign (Solar/Family-A)

| Object | Resolution | Window | Seen by | Contamination for scalp research |
|---|---|---|---|---|
| NQ 1-min Last (back-adjusted merge) | 1-min OHLCV | 2022-01 → 2026-07-31 | Claude + owner (heavily mined: Solar params, ensembles) | Minute-level price paths known; any scalp rule expressible on 1-min closes over this window is at risk of implicit selection. Sub-minute structure NEVER inspected. |
| NQ 3-min bars (`runs/AUDIT03_BARS/nq_3m_2022_2026.csv`) | 3-min closes | 2022-01 → 2026-07-31 | Claude (DC/overshoot studies, E10 validation) | Same as above at 3-min granularity. |
| Daily P&L vectors (E10, members) | daily | 2022 → 2026-07 | Claude + owner | Daily-level only. |
| NQ tick / second / Bid-Ask / depth | — | — | **NEVER inspected by anyone in this program** | Clean. All sub-minute event definitions are first-look. |
| ES / RTY / YM any resolution | — | — | Never inspected | Clean. |

## Standing seals

1. **≥ 2026-08-01 is SEALED for this campaign** (also Solar's LOCKED_FORWARD). No scalp
   experiment reads it until a frozen champion exists and the reading is logged as an
   evaluation, not selection. One virgin block protects both campaigns.
2. **SPLIT GEOMETRY — FROZEN 2026-08-07 (before any Tier-0 profitability was read):**
   - Tick/BBO sample: 2025-08-10 → 2026-07-31 (~247 sessions).
   - **Development: 2025-08-10 → 2026-05-31** (~205 sessions). All Tier-0/1/2 work lives here.
   - **Sealed scalp holdout: 2026-06-01 → 2026-07-31** (~42 sessions). Read ONLY at Tier-3
     promotion of a frozen candidate; every read logged here; never re-consumed for redesign.
   - Overall seal ≥ 2026-08-01 (shared with Solar LOCKED_FORWARD) — unchanged.
   - Internal validation: chronological expanding-window walk-forward inside the development
     period; for ML, all normalization/feature/threshold/hyperparameter selection nested
     inside training folds.
   - Minute-history studies (STRUCTURAL_SCALP / ADJACENT_INTRADAY): development = 2005-01 →
     2026-05-31; the same 2026-06/07 holdout dates apply at promotion.
   - Instrumentation measurements (spread map, Roll-bounce, sync integrity, L3 semantics —
     no selection content) may use the full development period, never the holdout.

## Sample roles within the development window (Amendment 3, frozen 2026-08-08)

- **TIER-0 DISCOVERY SUBSET = the 40 stratified sessions** already exported (seed 20260807,
  session_sample_40.csv). All discovery/event-study work runs here.
- **INTERNAL CONFIRMATION POOL = the remaining ~168 development sessions** (2025-08-10 →
  2026-05-31 minus the 40). NOT exported, NOT examined for alpha selection; used only to
  confirm surviving Tier-1 candidates before Tier-2. Indiscriminate export is forbidden;
  exception: oldest-first RAW ARCHIVAL exports are permitted WITHOUT analysis (server
  Bid/Ask is a rolling ~1yr window and data vanishes — archiving ≠ examining; any analysis
  of archived confirmation sessions still requires the candidate to have survived Tier-1).
- Sealed holdout 2026-06/07 and ≥2026-08 locks unchanged.

## Known owner-side exposure

Owner has watched Solar equity curves and Analyzer outputs over 2022–2026 (minute-level and
coarser). Owner has NOT seen tick/second-level conditional statistics. Any scalp hypothesis
that is a re-expression of a Solar finding (e.g. "trend days trend") must cite the Solar
result as prior knowledge, not claim independent discovery.

## Amendment log
- 2026-08-07: ledger created; development/holdout geometry pending data audit.
- 2026-08-07: DATAPROBE01 read raw tick/BBO events for two capability windows
  (2026-07-14/15 and 2025-10-14/15, NQ). Raw event dumps only — no conditional statistics,
  no signal evaluation, no P&L. These sessions are NOT considered selection-contaminated,
  but the probe is logged here for completeness.

## 2026-08-08 — SEALED SCALP HOLDOUT CONSUMED (system_master SM11)
The 2026-06-01→2026-07-31 block was read ONCE under the frozen
research/system_master/FINAL_PACKAGE_SPEC.md protocol (Tier-3-equivalent joint
finalist read: Solar baseline, HTF-tilt, B-MOM, B1, two portfolios). It is now
CONSUMED for all campaigns. >= 2026-08-01 remains virgin (LOCKED_FORWARD).

## 2026-08-10 — INTERNAL CONFIRMATION POOL: 8 sessions consumed (Master Directive v4, W5_PROTECTED_CONFIRMATION)
Owner-authorized ONE controlled use of the ~168-session INTERNAL CONFIRMATION POOL, subject to a
fully frozen and git-committed pre-registration bundle (`runs/W5_PROTECTED_CONFIRMATION/`,
commit `2eabcad`, frozen BEFORE any pool session's outcome was read). A metadata-only manifest
(`ELIGIBLE_SESSION_MANIFEST_METADATA_ONLY.csv`, file-existence checks only, zero outcome values
read) found only 52/168 pool sessions have both Last and Bid/Ask tick data cached locally. A
seeded, disclosed, pre-outcome selection (`manifest_work/BATCH1_SELECTION_METHOD.md`) picked 8 of
those 52, spread chronologically: `20250819, 20250912, 20251028, 20251125, 20260217, 20260302,
20260422, 20260512`.

These 8 sessions were exported (SWScalpTickExport_v3 → csv_to_parquet → build_grid1s, identical
pipeline to the original 40 discovery sessions) and the frozen confirmation bundle was run against
them in full (`runs/W5_PROTECTED_CONFIRMATION/results/REPORT.md`): AUCTION01 D4 diagnostic
(12/12 sign-replicated, 2/12 CI-excludes-zero — power-limited at n=6 usable session-clusters, 2 of
the 8 sessions had zero RTH Bid/Ask), AUCTION02 Product-A rate-limiter policy (NOT_PROMOTED per
its own frozen falsification rule, flagged low-confidence/fragile given only 23 in-domain
scale-up bars total), FLOW01 PRE_EXIT (PROBABLE_MULTIPLE_TESTING_ARTIFACT, consistent with
discovery's own null).

**These exact 8 sessions are now CONSUMED for these three specific constructions** (AUCTION01 D4,
AUCTION02 Product-A rate-limiter policy, FLOW01 PRE_EXIT) — per this ledger's own indiscriminate-
export discipline, they may not be re-used as a "pristine confirmation" for the same constructions
again. They remain usable for genuinely different future hypotheses not yet tested. **The
remaining ~160 sessions of the confirmation pool are untouched and still protected** — this was a
partial, disclosed opening of the pool (8 of 168), not an exhaustion of it. >= 2026-08-01 remains
virgin (LOCKED_FORWARD, unaffected by this entry).
