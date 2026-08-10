# MULTIPLE_TESTING_PLAN — frozen 2026-08-09, before any protected value is loaded

## Total endpoint count

Family 1 (AUCTION01 D4 replication): 12 cells. Family 2 (AUCTION02 policy): 4 endpoints, evaluated
as ONE family-level falsification decision (an OR of 5 failure conditions, per its own spec — not
4 independently-corrected hypothesis tests). Family 3 (FLOW01 PRE_EXIT, optional): 10 cells.
**26 total statistical cells across 3 families.**

## Why no formal Bonferroni/FDR correction is applied, and what replaces it

This campaign has not used formal multiple-comparison corrections anywhere in its prior 40+
constructions; instead it has consistently required (a) **dual clustering** (both session-block
AND trade-block bootstrap CI must exclude zero, not either alone — this is already a materially
more conservative bar than a single naive CI, since it requires two different resampling schemes
to agree), and (b) **consistency across related cells** (chronological half-stability, multiple
horizons agreeing in sign) as the practical safeguard against a single lucky cell being mistaken
for a real effect. This bundle continues that established convention rather than introducing a new
one at the confirmation stage that wasn't used at discovery — introducing a stricter standard now
would make the confirmation an unfair test of a discovery pass held to a looser one.

## Per-family replication thresholds (frozen, not adjustable after opening)

**Family 1 (AUCTION01, 12 cells).** The discovery pass found **all 12** cells cleared session-block
CI-excludes-zero with consistent sign (`AUCTION01_VALUE_STATE/REPORT.md` D4 table). Replication
threshold: **at least 9 of 12 cells** (75%) must replicate in sign with session-block CI excluding
zero for the family to be judged "REPLICATED." 6-8 of 12 is "PARTIALLY REPLICATED" (report exactly
which cells, and whether the pattern is horizon-dependent or predictor-dependent). Fewer than 6 is
"NOT REPLICATED."

**Family 2 (AUCTION02, 4 endpoints / 1 family decision).** Governed entirely by its own
pre-existing `falsification_condition` (an OR of 5 conditions — ANY one triggering means NOT
PROMOTED). No additional multiplicity adjustment is layered on top; that spec was itself written
with this exact confirmation use already in mind.

**Family 3 (FLOW01 PRE_EXIT, 10 cells, optional).** The discovery pass found **zero of 10** cells
cleared the dual-CI-excludes-zero bar (`FLOW01_AGGRESSIVE_PARTICIPATION/REPORT.md` PRE_EXIT
section — DATA_LIMITED throughout, n=61). With a materially larger protected-pool sample, some
cells may newly clear the bar by chance alone under 10 simultaneous tests. Threshold: **at least 3
of 10 cells** clearing dual-CI-excludes-zero, WITH consistent sign across those cells and WITH the
economic-relevance floor (`PRIMARY_ENDPOINTS.md`, ΔR²≥0.002) also cleared, is required before this
is reported as a plausible real effect rather than a multiple-testing artifact. 1-2 cells clearing
is reported explicitly (never hidden) but labeled `PROBABLE_MULTIPLE_TESTING_ARTIFACT, NOT A
FINDING` in the adjudication, consistent with running 10 simultaneous tests under a true null.

## What "replication" does NOT license

Per sec21/25: clearing a replication threshold does **not** license retroactively picking the
best-looking cell as "the" finding, does not license a new construction beyond what's already
frozen in `AUCTION02_ACTION_RELEVANCE/spec.yaml`, and does not license extending Family 3 into a
policy (FLOW01 never built one; this bundle doesn't either, regardless of confirmation outcome —
per sec42, a confirmed-information/failed-or-absent-action-mapping result returns to
`STATE_INFORMATION_LIBRARY.csv` for a future, separately-scoped construction pass, not an
on-the-spot policy built during adjudication).
