# PRICE01 — Product-A genuine-MNQ dual-truth infrastructure: built, small and stable effect

**Disposition: INFRASTRUCTURE COMPLETE.** Confirms directive sec13's concern was real: Product
A's Python research substrate has been pricing on NQ's own OHLC (a proxy) throughout this entire
campaign, not genuine MNQ. The effect turns out to be small, stable, and does not change any
prior verdict — but it is now available as a proper dual-truth convention for every future
Product-A candidate, as required.

## What was built

Re-ran the byte-identical `product_a_exec_generalized` decision/execution formula (verbatim from
`pa0_substrate.py`/`U0`) twice on the identical `T`/`tilt_state`/`B`/C4 decision inputs:

- **LEGACY_RESEARCH_PROXY** — fills on NQ's own OHLC (existing convention, unchanged, still the
  certified canonical number).
- **GENUINE_MNQ_EXECUTION_ECONOMICS** — fills on genuine MNQU6 OHLC
  (`runs/PRODUCTB_ONECONTRACT_FINAL/out/mnq_3m_raw.csv`, the same file and alignment pattern U0
  already uses for Product B's MNQ leg: genuine through 2026-05-29, disclosed NQ-proxy for the
  June-July 2026 health-only extension).

**Correctness gate, verified before anything else:** target-exposure sequences are **byte-
identical** between the two runs — confirms Product A's decision layer depends only on the
NQ-derived signal (`T`/`tilt_state`/`B`), never on which price series fills execute at. Price
choice affects fill economics only, exactly as it should.

## Headline numbers

| | Legacy (NQ proxy) | Genuine MNQ | diff | diff % |
|---|---:|---:|---:|---:|
| Canonical (≤2026-05-31) | $177,924.40 (certified) | $178,687.40 | +$763.00 | +0.43% |
| Extended (through 2026-07-31) | $212,894.50 | $213,657.50 | +$763.00 | +0.36% |

The dollar diff is **identical** canonical vs extended — makes sense: the June-July 2026
extension already uses an NQ-proxy for MNQ (disclosed, same as Product B's convention there), so
no further genuine-MNQ divergence accrues past 2026-05-29. The effect is small (well under any
1% wash threshold this campaign has used) and stable, not concentrated in a single regime.

## Resolves a previously-unproven piece of the NT8 parity gap

`runs/V1R4_NT8_PARITY/FULL_HISTORY_CERTIFICATION.md` found Product A's real, chunked NT8
execution (which genuinely trades MNQ) totals $197,329.70 vs the Python NQ-proxy reference
$177,924.40 — a $19,405.30 (+10.91%) gap the certificate could only attribute to two *other*
mechanisms (synthetic fill-slip, boundary-serialization), explicitly calling that attribution
"a plausibility argument, not a proof" for Product A.

This run isolates the price-basis component directly: genuine MNQ pricing closes **$763.00 of
the $19,405.30 gap — only 3.9%.** Price-basis is a real but minor contributor; the fill-slip and
boundary-serialization mechanisms the certificate already named remain the dominant, still-
unproven-to-the-dollar explanation for the other ~96%. This is a genuine (if modest) correction
to prior uncertainty, not a new open question.

## What this means for prior findings

No prior CONTINUOUS SYSTEM EVOLUTION verdict changes. Every closed Product-A family (H0, U1, U3,
U4, U6, U7, U8, U8B, U9B, LEV01, SKEW01, EXP01, U4B, U6B, U1B-leg2) was NOT_PROMOTED or CLOSED —
none were promotion decisions resting on a margin anywhere near 0.43%, so none flip under genuine
pricing. **One flagged follow-up, not yet done:** `U6B_PRODUCT_A_SCALE_RATE` is the closest call
in campaign history (2022-2025-only deltas of +0.503%/+0.579%, both just under the preregistered
1% wash threshold). PRICE01's effect (+0.43% pooled) is the same order of magnitude as U6B's own
margin below threshold — worth an explicit genuine-MNQ repricing of U6B specifically (not just
the incumbent) before any O2 reconsideration verdict, since a uniform-looking pooled effect could
still be unevenly distributed across U6B's exposure-level-conditioned construction. Flagged for
the O2 synthesis, not resolved here.

## Convention going forward (per directive sec13/sec77)

Daily P&L series for both conventions saved: `out/daily_legacy_proxy.csv`,
`out/daily_genuine_mnq.csv`, plus `out/year_by_year_comparison.csv` and `out/price01_recon.json`.
For every future Product-A candidate: report both; genuine MNQ economics is primary for
execution-sensitive ranking; if a verdict changes materially between the two conventions, stop
and investigate before promoting. `LEGACY_RESEARCH_PROXY` is **not** being retired — it remains
the certified canonical number every prior finding in this campaign was built against, and stays
unchanged.
