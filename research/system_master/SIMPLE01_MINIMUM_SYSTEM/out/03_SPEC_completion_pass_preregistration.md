# SIMPLE01 completion-pass preregistration

**Written and committed BEFORE any of the two gaps below are computed**, per the practice change
adopted this session (`research/registry/REGISTRY_GAP_NOTE.md`'s 2026-08-10 addendum): frozen spec
committed separately and first, results committed after.

## What this closes

`SIMPLE01_MINIMUM_SYSTEM/REPORT.md`'s red-team pass (§ RedTeam, `overall_confidence: MEDIUM`) found
two issues, neither of which is a new research question — both are completions of the
already-designed SIMPLE01 test:

1. **HIGH severity / procedural gap**: the frozen margin 3.4's trade-level leg (top-1% trade P&L
   retention ≥90% vs the FULL reference, jointly required alongside the day-level leg per
   `CONVENTIONS.md` gate 6) was never computed for any of the 7 rungs — `execution_productA.py` /
   `execution_productB.py` only exported session-level daily P&L. Per SIMPLE01's own frozen rule
   ("passes only if it clears ALL margins"), no rung can currently be certified.
2. **MEDIUM severity, non-decision-changing / data defect**: the "Execution Product B (raw)" summary
   blob supplied to the Product-B statistical agent duplicated `maxDD_eod` into
   `maxDD_bar_intraday` for 5 cells; the authoritative `execution_productB_raw.json` has the correct
   (larger) bar-level figures. Recomputing the `intraday_dd_margin` ratios with correct figures does
   not flip any PASS/FAIL in the original run, but the blob should be regenerated from source before
   being relied on again.

## Method (frozen before computing either)

- **Trade-level retention**: reconstruct a per-trade P&L series for each of the 7 rungs directly
  from the already-computed `bar_pos`/`bar_pnl` arrays in `execution_productA.py` /
  `execution_productB.py` (a trade = a maximal contiguous run of nonzero, same-signed position;
  its P&L = sum of `bar_pnl` over that run). This is a mechanical reconstruction from data already
  computed and certified in SIMPLE01's own EXECUTION phase — no new backtest, no new formula, no
  parameter choice beyond "what counts as one trade" (stated above, decided now).
- **Definition reused verbatim, not redefined**: top-1% trade retention = (sum of P&L of the FULL
  reference's own top 1% of trades by P&L, restricted to trades that occur on the SAME dates in the
  candidate rung) / (sum of P&L of the FULL reference's top 1% of trades), matching
  `CONVENTIONS.md` gate 6's existing definition — read that file's exact wording before implementing
  and use it verbatim, do not invent a new formula.
- **Blob fix**: regenerate every `maxDD_bar_intraday` cell directly from `execution_productB_raw.json`
  (the authoritative source), do not hand-transcribe.
- **Scope**: apply to all 7 rungs across both products (not just the two near-misses), for
  completeness and so the already-failing rungs (A0, A2, B0) get a fully consistent record even
  though they are not expected to change status.
- **No margin is loosened or added.** This pass only fills in a previously-missing leg of an
  already-frozen margin and corrects a transcription error in an already-frozen margin — it does not
  revisit the Sharpe/CDaR/DD margins' thresholds, the block-bootstrap methodology, or the complexity
  rule from `01_SPEC_frozen_margins.md` / `02_SPEC_complexity_metric.md`, all of which remain exactly
  as originally frozen.
- **Re-adjudication**: after both gaps are closed, re-apply the exact frozen promotion rule (all
  margins must pass) to each of the 5 non-reference rungs and report the updated verdict. This is
  not a new blind statistical pass (the underlying Sharpe/CDaR/DD numbers are unchanged) — it is
  completing the evidence table the original ADJUDICATOR was missing one row of.
