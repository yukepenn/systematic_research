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
2. A late in-development sealed scalp holdout will be declared here (dates frozen) after the
   data audit reports actual tick/second coverage, BEFORE any family profitability is read.
   Until that entry exists, NO experiment may compute strategy-level P&L beyond Tier-0 event
   statistics.

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
