# G2_F3_DELEV01 — RESULT: **DEFECT — MC-40 was NOT tested, and the defect is a standing discovery**

Spec committed `bb426af` pre-result. Trial G00027 DEFECT. Programmatic proof in
`out/defect_evidence.txt`.

> ## ⚠️ **THE NQ CONTINUOUS SUBSTRATE IS ADDITIVELY BACK-ADJUSTED: point moves are preserved,
> ## PERCENT returns are structurally distorted across eras.**
> Sep–Dec 2008 shows min daily return −3.00% and **zero days |r| ≥ 3.5% — impossible for the
> GFC** (the 2008-10-13 +154.5-pt move reads +3.3% instead of its real +11–13%; the "price" on
> 2008-10-01 is ~3.5× the real level). **Any absolute percent threshold spanning eras on this
> substrate inherits this defect.** MC-40's [−5.0%, −2.5%) band cannot see 2008 deleveraging
> days BY CONSTRUCTION → the mechanism was not tested; a NULL would have been a false claim.

The as-computed gates (all FAIL on the distorted population) are retained as evidence only and
are NOT quotable as an MC-40 result.

## Blast-radius audit (orchestrator, recorded)

- **Unaffected**: point-denominated P&L (all $/pt engines, P1, baselines, ORB, sweep, MAE) ·
  within-session normalized objects (ERABREAK01's profiles) · tick-domain work (EXEC01/EXECSTATE).
- **Attenuated but standing**: percent-return diagnostics mixing eras (H1, H2, VOLSIZE01) — the
  distortion shrinks old-era percents, it cannot manufacture effects; NULL/FAIL verdicts stand,
  with retest-on-ratio-adjusted as the recorded revival condition where noted.
- **Blocked until fixed**: any future cross-era percent-band object.

## The unlock (free)

A ratio-adjusted or unadjusted NQ daily series — constructible at $0 from the owned per-contract
`db/day` store (2009→) and/or the certified multi-market economic-returns panel, with external
free sources for 2006–2008. Queued as a data-contract card; **MC-40 retest is gated on it, not
re-run.**

**`LIVE ENABLED = NO` · $0.**
