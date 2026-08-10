# Batch 1 export session selection — chosen before any outcome was touched

Per owner decision (2026-08-10): export a small, chronologically-diverse subset of the 52
Last+Bid/Ask-eligible protected-pool sessions rather than the full set (50-200+ hours), running in
the background.

**Method (fixed, disclosed, seeded)**: sorted the 52 eligible dates
(`ELIGIBLE_SESSION_MANIFEST_METADATA_ONLY.csv`, `eligible_for_tick_bbo_confirmation==True`)
chronologically, divided into 8 equal-size consecutive segments, `random.seed(20260810)` picked
one date uniformly at random from each segment (ensures spread across the whole Aug-2025→May-2026
window rather than a cluster). No outcome data was read before or during this selection.

**Selected 8 sessions**: `20250819, 20250912, 20251028, 20251125, 20260217, 20260302, 20260422,
20260512`

This is Batch 1 of what may become a larger export if the owner authorizes more later — it does
not preclude additional batches, but each additional batch must be separately selected before
seeing any outcome from a prior batch, per the same no-post-hoc-selection discipline.
