# HTFMECH01 — HTF marginal-contribution mechanism decomposition (PREREGISTRATION)

**Committed before any result is generated.** Diagnostic only (campaign directive sec44-50 class),
zero alpha budget, zero construction, zero promotion, no incumbent file touched. Reuses PLACEBO01's
already-certified `grid_core` substrate and `solve_A`/`solve_B` executors verbatim — no new data,
no re-derivation of the core formulas, no new protected/locked-forward evidence opened.

## Why this task exists

`STRUCTURAL_INVARIANCE_MINIMUM_SYSTEM_SYNTHESIS.md` (2026-08-10) identifies HTF (`tiltState`) as
"the single clearest, best-evidenced lead this campaign produced for a *future*, better-powered
structural test" — two independent methods (PLACEBO01's causal placebo, SIMPLE01's blind
non-inferiority ladder) both flag it as the weakest-evidenced component, and the synthesis
explicitly declines to act on it "per this campaign's own no-optimize-in-the-same-campaign rule."
That campaign is closed; this is the flagged future work, scoped deliberately narrow: **explain**
the existing PLACEBO01 finding, do not try to fix, re-tune, or promote anything.

**Explicitly distinct from forbidden/closed axes**: this does not touch `B1` (a specific frozen
Product-B construction file/spec awaiting either a calendar-gated MONITOR-01 reading or a
separately-authorized protected-pool batch — neither happens here); does not reopen ACTIONMAP01 or
U6B; is not generic OHLCV feature mining (it decomposes an existing architectural component's own
already-measured causal contribution, it does not search for new predictive features); touches no
DOM/Market Replay data.

## Question

PLACEBO01 found HTF's real marginal net/Sharpe contribution sits at the 27.8th–32.1st percentile
of a 1000-draw randomized-chronology null (below the null median, for both products) over the
canonical window (2023-01-01 to 2025-02-02). That is a whole-window, whole-population verdict. This
task asks: **is the shortfall uniform across time and direction, or concentrated?** A uniform
shortfall strengthens the case that HTF's mechanism is generically weak. A concentrated shortfall
(e.g., one bad year, or one side) would be a materially different, more specific finding — still
not grounds for any construction here, but a sharper target for whatever future work the owner
authorizes.

## Exact method (frozen before any number is computed)

1. Import `grid_core` (PLACEBO01's own certified substrate) — reuses its module-level self-check
   against both certified dev-window nets; aborts if that fails.
2. Reuse `solve_A`/`solve_B` (PLACEBO01's `02_htf_placebo.py`, copied verbatim, not modified) to
   compute per-bar P&L for two conditions over the canonical window: **real** (actual `tiltState`)
   and **baseline** (`tiltState≡0`, PLACEBO01's own Solar+BMOM-only control).
3. `marginal_bar_pnl = bar_pnl_real - bar_pnl_baseline`, per bar, per product — the bar-level
   decomposition of the exact same whole-window quantity PLACEBO01 already reported in aggregate.
4. **Year decomposition**: sum `marginal_bar_pnl` by calendar year (2023 full, 2024 full, 2025
   stub — the same 3-year partition PLACEBO01's own null construction already uses).
5. **Side decomposition**: sum `marginal_bar_pnl` split by `sign(T_bar)` (Product A) /
   `sign(T'_bar)` (Product B) — i.e., bars where the underlying signal was net-long vs net-short
   at the moment HTF's multiplier applied. This asks whether HTF's up-weight mechanism helps one
   side and hurts the other, given it always up-weights agreement regardless of direction.
6. Report both decompositions as **descriptive** dollar/count tables — no new significance test is
   run per slice (that would require regenerating full per-bar null draws per slice, a materially
   heavier and separately-scoped task not authorized here). This is explicitly a decomposition of
   the already-established whole-window finding, not a new hypothesis test with its own p-value.

## What this will NOT do

Will not build, backtest, or promote an HTF variant. Will not touch `B1`'s own files or spec. Will
not re-run PLACEBO01's null generation (1000 draws) — reuses only the real/baseline computation
path, which is the cheap half of that script. Will not open any data beyond the same canonical
window (2023-01-01 to 2025-02-02) PLACEBO01 already used — no new locked-forward or protected-pool
consumption. Will not compute per-slice statistical significance (see step 6) — flagged explicitly
as a boundary of this task, not silently implied.

## Outputs

`out/htfmech01_year_decomposition.csv`, `out/htfmech01_side_decomposition.csv`,
`out/htfmech01_results.json`, `REPORT.md` (written after the numbers exist).
