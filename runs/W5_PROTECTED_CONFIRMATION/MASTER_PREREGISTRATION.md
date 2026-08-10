# W5_PROTECTED_CONFIRMATION — Master Preregistration

**Frozen 2026-08-09, before any protected-pool value is loaded.** Master Directive v4 sec18-19.
This document, `SPEC_HASHES.md`, `ELIGIBLE_SESSION_MANIFEST_METADATA_ONLY.csv`,
`PRIMARY_ENDPOINTS.md`, `MULTIPLE_TESTING_PLAN.md`, and `FAILURE_RULES.md` together constitute the
complete one-shot confirmation bundle. **Nothing in this bundle may be altered once the protected
pool is opened** (sec21): no threshold changes, no feature swaps, no new "one more variant," no
inspection-then-adjustment. The bundle is committed to git before the pool is touched.

## Scope authorization

Per the owner's directive sec0: this authorizes **one controlled use** of the AMENDMENT_3
protected confirmation pool (`research/scalping_lab/CONTAMINATION_LEDGER.md`'s "INTERNAL
CONFIRMATION POOL" — the 168 development-window sessions not used for discovery), subject to
every condition in that section. It does **not** authorize touching any data dated ≥2026-08-01
(see `FAILURE_RULES.md`'s date-firewall restatement), does not authorize exploring the pool before
this bundle is frozen, and does not authorize adding new questions once opened.

## Eligible session population

Per sec1's exact definition: eligible = (AMENDMENT_3 protected pool) AND (date ≤ 2026-07-31) AND
(has the exact raw-data modality the preregistered test requires). The full protected pool is 168
sessions (2025-08-12 through 2026-05-29 — the 208-session tick/BBO development window minus the 40
discovery sessions already used by `AUCTION01_VALUE_STATE`/`FLOW01_AGGRESSIVE_PARTICIPATION`/
`COMBO01_MULTIMODAL_SYNERGY`/`AUCTION02_ACTION_RELEVANCE`; derivation script and both session lists
are in `manifest_work/`). All 168 dates are ≤2026-07-31 by construction — the pool's own definition
never extended into the June-July 2026 sealed-and-consumed scalp holdout or the ≥2026-08-01 virgin
boundary. **Actual eligibility by data modality is determined in
`ELIGIBLE_SESSION_MANIFEST_METADATA_ONLY.csv`** — file-existence/metadata only, no outcome data
was read to build it. Each confirmation family below runs on whatever subset of the 168 that
manifest finds has the required modality; a family is not entitled to demand more data than
actually exists.

## What enters the bundle (priority order per sec19)

### PRIMARY — AUCTION01 diagnostic replication

Re-run `runs/AUCTION01_VALUE_STATE/src/03_diagnostics.py`'s own D4 diagnostic (`poc_share` /
`value_dist_ticks` vs subsequent absolute expansion, 12 preregistered cells: 2 predictors × 3
horizons × {markout, range}) on the eligible protected-pool sessions, using the byte-identical
construction (`02_build_poc_substrate.py`'s causal running-POC algorithm, unchanged). This is a
**diagnostic replication**, not a new construction — no new thresholds, no new features.

### SECONDARY — AUCTION02 frozen Product-A policy

`runs/AUCTION02_ACTION_RELEVANCE/spec.yaml`'s `confirmation_procedure` section (steps a-d) is
**reused verbatim as the confirmation protocol for this family** — it is already complete,
mechanical, and was written before any protected data was touched. Do not re-read it as a
suggestion; it is binding. Its four steps (diagnostic replication, redundancy replication,
coverage-restricted constructed-P&L delta, right-tail check) and its exact `falsification_condition`
(sec 239-253 of that file) are the confirmation test for this family — reproduced by reference,
not restated here, to avoid any risk of transcription drift between the two documents.

### OPTIONAL SECONDARY — Product-B Auction policy

**Not included.** `AUCTION02_ACTION_RELEVANCE/spec.yaml`'s own Step 3 explicitly declined to
freeze a Product-B construction (evidence did not clear the dual-CI-excludes-zero bar as cleanly
as Product A's). Per sec16's own instruction ("If no clean Product-B action mapping exists: DO NOT
FORCE ONE"), there is nothing to confirm here.

### OPTIONAL SEPARATE FAMILY — FLOW01 PRE_EXIT confirmation

Re-run `runs/FLOW01_AGGRESSIVE_PARTICIPATION/src/02_analysis.py`'s own PRE_EXIT test — the
already-frozen 5-feature family (`avg_spread_ticks_60s`, `quote_intensity_60s`, `ret1s_vol_60s`,
`signed_flow_aligned_60s`, `flow_persistence_60s`) × 2 horizons (fwd1/fwd3) = 10 cells — on the
eligible protected-pool sessions' PRE_EXIT checkpoints (the bar immediately preceding an actual
Product-B EXIT/REVERSAL). No primary feature was ever declared among the 5 (FLOW01's own spec
tested them as a preregistered set); per sec25's explicit instruction, **all 10 cells are reported
together, multiplicity-adjusted per `MULTIPLE_TESTING_PLAN.md`** — no post-hoc selection of "the
nicest-looking one." No new flow feature engineering of any kind occurs in this confirmation step.

### OPTIONAL — combination interaction candidates

**None frozen.** `AUCTION02_ACTION_RELEVANCE/spec.yaml`'s Step 4 tested exactly the two a priori
candidates sec17 anticipated (Auction × U6B-quality-low; Auction × |M|-magnitude) on the discovery
set; neither cleared the session-block-CI-excludes-zero bar (both flagged `DATA_LIMITED`/near-null,
not frozen). Per sec19 ("No other idea may be added after the pool is opened") and sec17's own
"at most TWO combination candidates may survive into the protected confirmation bundle" — zero
survived discovery, so zero enter this bundle. This is a valid, complete outcome, not a gap.

## What is explicitly excluded from this bundle

- U6B's own adjudication (genuine-MNQ repricing, capital frontier, forward-readiness, adversarial
  review) — a **separate track entirely**, using long-history OHLCV data already fully available
  (not tick/BBO), governed by directive sec5-11, not the AMENDMENT_3 pool. It does not touch this
  bundle and this bundle does not gate it.
- Any ICT01/ICT02/VAR01/REL01/DOM01-adjacent question — none of these closed with a frozen,
  protected-pool-ready policy spec this wave; nothing from them is eligible for inclusion.
- Any new hypothesis, feature, or threshold not already frozen in `AUCTION01_VALUE_STATE`,
  `AUCTION02_ACTION_RELEVANCE`, or `FLOW01_AGGRESSIVE_PARTICIPATION`'s own prior artifacts.

## Binding procedural rules (restated from the directive for a single reference point)

1. **Run the entire bundle before interpreting any single result** (sec21). No stopping after the
   first endpoint, no adapting a later test based on an earlier one.
2. **No parameter changes of any kind once opened** — not `poc_share` for `value_dist_ticks`, not
   a horizon, not a POC lookback window, not a materiality bar. If a frozen test turns out to be
   miscalibrated for the actual protected-pool sample size, that miscalibration is itself a
   reportable finding (see `FAILURE_RULES.md`), not a license to adjust and rerun.
3. **Separate INTERNAL PROTECTED CONFIRMATION from CHRONOLOGICAL/PREQUENTIAL evidence** (sec23) —
   the 168 sessions are not pristine forward out-of-sample data; they were excluded from discovery
   by design, not by time-ordering. Some protected-pool sessions may be chronologically *earlier*
   than some discovery sessions (both are drawn from the same Aug-2025–May-2026 window). Report
   this distinction explicitly in the final adjudication, never blur it.
4. **Date firewall absolute** — see `FAILURE_RULES.md`.
