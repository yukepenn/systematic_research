# FAILURE_RULES — frozen 2026-08-09, before any protected value is loaded

## Date firewall (absolute, restated per directive sec20/46)

No script in this bundle may read, export, compute on, or use for metadata beyond bare calendar
identity any data dated **≥2026-08-01**. This is the repo-wide `research/operational/
LOCKED_FORWARD.md` seal and is strictly stronger than AMENDMENT_3 — AMENDMENT_3 never authorized
anything past 2026-05-29 in the first place (the confirmation pool's own upper bound), so this
firewall is not expected to bind in practice for this bundle, but every script must still assert it
explicitly (per this campaign's standing "no unsupported hand arithmetic, defensive assertion over
trust" discipline) rather than relying on the pool's own definition alone.

## Correctness gates (must PASS before any confirmation result is trusted)

Every script in this bundle must reproduce its relevant certified/frozen canonical figure (e.g.
AUCTION01's own certified canonical Product-B net $301,915.92 and Product-A net $177,924.40 for
any script that touches `u0_state_table.parquet`; AUCTION02's own `VOTE_THRESH=6.0` and
`CUT_FAR_TICKS=315.3333333333333` reproduced verbatim, never re-derived) before computing any
confirmation-pool statistic. A correctness-gate failure halts that script; it is reported as an
`EXECUTION_DEFECT`, not silently worked around, and does not consume the one-shot pool opening for
that family (the family's confirmation attempt is void and may be re-attempted once the defect is
fixed, since no protected outcome was actually read before the gate failed).

## What counts as "opening" the pool (defines when the one-shot is consumed)

The pool is considered **opened** the first time any script reads an actual price, volume, P&L, or
derived-feature VALUE from a protected-pool session (not file existence/metadata, which
`ELIGIBLE_SESSION_MANIFEST_METADATA_ONLY.csv` already legitimately touched under sec18's own
metadata-only allowance). Once opened, the entire frozen bundle runs to completion in one
uninterrupted pass (sec21) — there is no "partial opening."

## Falsification handling — do not tune against the protected pool

If a family's endpoint fails (per `PRIMARY_ENDPOINTS.md`/`MULTIPLE_TESTING_PLAN.md`'s own frozen
criteria), the response is **exactly** the diagnostics directive sec43 allows and no more:
classify the failure as one of {sign failure, effect-size collapse, regime concentration, data-
quality issue, confound} using only the data already computed by the frozen bundle itself (no new
protected-pool queries to investigate *why* it failed). Then close/downgrade per
`MULTIPLE_TESTING_PLAN.md`'s own labels. **Never ask "what threshold would have worked" and never
rerun with an adjusted parameter** — the pool is consumed regardless of the outcome.

## Explicit non-outcomes this bundle must be prepared to report honestly

- **AUCTION01 replicates, AUCTION02 policy fails.** Per sec42: this is `CONFIRMED INFORMATION,
  FAILED ACTION MAPPING` — return the state to `STATE_INFORMATION_LIBRARY.csv`, do not declare the
  information itself dead. Any future re-mapping attempt cannot reuse this same protected pool as
  a "pristine confirmation" again (sec42's own instruction) — it would need new data.
- **AUCTION01 does not replicate.** Per sec43: do not tune against the pool; classify the failure
  mode from what the frozen bundle already measured, close/downgrade, the pool is consumed.
- **AUCTION02 policy passes on the coverage-restricted construction but the coverage itself is too
  thin to be meaningful** (e.g. `ELIGIBLE_SESSION_MANIFEST_METADATA_ONLY.csv` finds most of the
  168 sessions lack the required tick+BBO modality) — labeled `DATA_LIMITED` per AUCTION02's own
  promotion-gate taxonomy, not forced into PROMOTED or NOT_PROMOTED.
- **FLOW01 PRE_EXIT clears 1-2 of 10 cells.** Labeled `PROBABLE_MULTIPLE_TESTING_ARTIFACT, NOT A
  FINDING` per `MULTIPLE_TESTING_PLAN.md` — reported, not hidden, not promoted.

## Sign-off

This bundle (`MASTER_PREREGISTRATION.md`, `SPEC_HASHES.md`,
`ELIGIBLE_SESSION_MANIFEST_METADATA_ONLY.csv`, `PRIMARY_ENDPOINTS.md`, `MULTIPLE_TESTING_PLAN.md`,
this file) is committed to git **before** the protected pool is opened. The commit hash of that
commit is the audit anchor — any subsequent claim about what was "already frozen" is checked
against that commit, not against memory or a later restatement.
