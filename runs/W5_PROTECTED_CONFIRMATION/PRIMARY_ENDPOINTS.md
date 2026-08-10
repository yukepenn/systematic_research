# PRIMARY_ENDPOINTS — frozen 2026-08-09, before any protected value is loaded

Per directive sec22: every endpoint below has both a **statistical replication** criterion and an
**economic relevance** floor, and the economic floor is derived from an actual, already-existing
convention in this campaign (a cost, a policy effect, or a precedent for "negligible"), never from
an arbitrary fraction of the discovery-pass effect chosen after seeing anything.

## Family 1 — AUCTION01 diagnostic replication (PRIMARY)

**Statistical replication** (12 cells: `{poc_share, value_dist_ticks}` × `{markout_15, markout_60,
markout_300}` interpreted per AUCTION01's own D4 table, i.e. 2 predictors × 3 horizons × {markout,
range} = 12): same sign as the discovery-pass result, session-block bootstrap 95% CI excludes
zero.

**Economic relevance floor**: this is a pure diagnostic (no policy is built directly from D4) — its
economic relevance is assessed by whether it *could* plausibly support a policy, not by a dollar
floor of its own. Floor: residualized |Spearman ρ| ≥ 0.10 (the smallest ρ among AUCTION01's own
original 12 cells that was judged non-negligible, per `AUCTION01_VALUE_STATE/REPORT.md`'s own
reported range of 0.13–0.37 — 0.10 sits just below that observed range as a floor, not picked to
flatter a replication result since it predates seeing any protected-pool number).

## Family 2 — AUCTION02 frozen Product-A policy (SECONDARY)

**Reused verbatim from `AUCTION02_ACTION_RELEVANCE/spec.yaml`'s own `primary_endpoints` and
`falsification_condition` sections** (frozen 2026-08-09, before this bundle existed) — not
restated here to avoid transcription drift. Four endpoints: (1) Product-A H=3 signed_markout
replication, (2) both products' H=3 large-move-probability replication, (3) redundancy-vs-U6B
replication (|ρ|<0.2), (4) constructed net/Sharpe/maxDD delta over tick-covered dates only.

**Economic relevance floor** (already frozen in that spec, reproduced here for completeness): step
(c)'s constructed net delta must be ≥1% of CONTROL's own net over the same coverage-restricted
date set — the identical wash-threshold convention this campaign has used for U4B/U6B/every prior
promotion-track candidate, not a new number invented for this family.

## Family 3 — FLOW01 PRE_EXIT confirmation (OPTIONAL SEPARATE FAMILY)

**Statistical replication** (10 cells: 5 features × 2 horizons): both session-block AND trade-block
bootstrap 95% CI exclude zero (the exact dual-clustering standard FLOW01/AUCTION02/COMBO01 already
established as this campaign's bar for "not merely underpowered").

**Economic relevance floor**: ΔR² ≥ 0.002 — the lower bound of the range this campaign has already
established as "economically negligible even when statistically real" (`SHADOW01_SETUP_
COMPATIBILITY`'s own closure: "ΔR² 0.0002-0.0019... economically negligible, null not practically
rejected"; `VAR01_VARIANCE_SIGNATURE`'s own closure at ΔR²=0.000313 in the identical range). A
FLOW01 PRE_EXIT cell clearing statistical replication but landing under this ΔR² floor is
classified `NO_LARGE_EFFECT_DETECTED`, not promoted to any further status, per direct precedent
from these two already-closed families — this is not a new standard invented for this bundle.

## Reporting convention (all families)

Every endpoint reports, without exception: the discovery-pass point estimate and CI side-by-side
with the confirmation-pass point estimate and CI, the sign-replication verdict, the
statistical-significance verdict, and the economic-relevance verdict, as three separate columns —
never collapsed into a single pass/fail without showing the underlying three-way breakdown.
