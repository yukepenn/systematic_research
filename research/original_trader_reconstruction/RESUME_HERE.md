# RESUME_HERE (2026-08-24, after Directive v4.0)

## Authority chain — read in this order
1. `CURRENT_KNOWN.md` (FACT + REPRODUCED only) and `CURRENT_HYPOTHESES.md` (everything open)
2. `CLAIM_REGISTRY.csv` (141 rows, one status token each) · `FALSIFIED_HYPOTHESES.md`
3. `DIRECTIVE_V4_ANSWERS_20260824.md` (§45 answers, incl. the failed-prediction ledger)
4. `MODEL_REGISTRY.yaml` · `RUN_PROVENANCE.csv` · `REVISION_HISTORY.md`

`CURRENT_TRUTH.md` is **deprecated as authority** — kept as historical record only.

## The one result everything now rests on

`solar_family/inverse/GLOBAL_PATH_JAN2023.md` — a **unique continuous 89-trade path**
reproduces **all eleven** visible rows of OTRIMG-0003 exactly (every cell, cent and tick),
and its cumulative net matches a cell that was never used as a constraint.

That pinned three model choices **by elimination, never by profit**:
- entries are **T1 only** (T2/T3 never used: `min_extra = 0` in all six universes)
- the exit test is **STRICT** (`close < TrailingStop`) — INCLUSIVE admits **zero** global paths
- report rows are **CALENDAR exit dates**, not trading-session dates

The machine is a pure always-in stop-and-reverse: 72 reversals, 10 session-close exits,
16 declines out of 105 decisions.

## What is blocking, in EVI order

1. **The suppression layer (highest EVI, free).** 16 declines are located exactly, but no
   threshold rule over 15 observable state features reaches ≤2 errors, and the incumbent
   D-gate scores 87/105. Do NOT bolt on another gate term — that is explicitly forbidden by
   §13 and was the failure mode this pass corrected.
2. **Extend the global inverse to Feb-2025** (OTRIMG-0026: 2 days, full MAE/MFE). Same
   machinery, different era, no new data, no purchase. This is the named next experiment
   (§45 Q28) and it tests whether the 2023 mechanism survives the arrival of the risk stack.
3. **VF Layer-A rebuild** per `vwap_flux_family/VF_SIGNAL_GENERATOR_v2.md` — move
   QtyPerTrend/Split from execution to signal generation. Every R7/R8 conclusion that
   inherits the defect is named in that file and is currently PROVISIONAL.
4. **Free vendor-side VF measurements not yet run**: rail extraction from the vendor manual's
   own archived chart PNGs, and the vendor's published videos. Both are in-repo or public.

## Two live tensions — do not collapse either one

- **Exit rule is era-split.** STRICT is the only rule that works in 2023 (INCLUSIVE
  impossible); INCLUSIVE is marginally better on the 2025 weeklies (0.376 vs 0.389). Keep
  both for 2025.
- **VF lifecycle reopened** to UNKNOWN with ACTIVE / SEGMENT / SLIDING / BAND-REFRESH all
  admitted. Our morphology evidence compares our model to our model, not to the vendor.

## Purchase gate: CLOSED, verdict PREMATURE

VWAP Flux would resolve vendor semantics but not whether the trader's build follows them —
which is the binding uncertainty. And EV-039, which drove the previous "he reimplemented it"
lean, **lost its premise**: no frame in the corpus shows Tick Replay state and
`BidAskPrice_RealVolume` together, and the vendor manual explicitly invites user-written
wrappers. Free work is not exhausted (items 3 and 4 above).

## Standing rules

Spec-first commit before every readout, amendments included. §6 keep rivals and report
intervals, not point values. §40 net must never rescue wrong trade geometry. No ad-hoc term
added to force a fit. CrossTrade = historical backtests only, never orders/deploy/Sim101.
Originals read-only. LOCKED_FORWARD ≥ 2026-08-01 virgin. No force-push, no history rewrites.
