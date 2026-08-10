# SPEC01 — evening/session specification audit: ALREADY RESOLVED, not a defect

**Disposition: CLOSED — pre-existing false positive, corrected before this baseline was frozen.
No fix needed. No candidate. `SolarWaveSMMaster_v4`/`SolarWaveOneContractNQ_v5`/`_MNQ_v5`
unchanged.**

## What the owner recalled vs. what actually happened

The owner's recollection ("~16 evening trades, roughly -$33.5k, very large loss per trade,
material share of baseline net") is **partially accurate as a number, but describes a closed
non-issue, not an open defect.**

The canonical artifact is `runs/W17_C4_COMPLIANCE/REPORT.md`, section **V1h** (also
`runs/W17_C4_COMPLIANCE/spec.yaml` key `v1h_premise_correction`; rolled up in
`research/system_master/CURRENT_TRUTH.md`). A prior Wave-16 directive flagged 16 `BEST_ONE_NQ`
(`SolarWaveOneContractNQ`) trades exiting after 16:45 as a suspected initial-margin/compliance
**breach** — the fear being these were overnight positions carried through the 17:00–18:00 CME
maintenance halt without initial margin posted.

Wave 17's V1h investigation (self-authored correction: *"the directive's premise is FALSE, and
the Wave-16 framing that produced it was mine"*) established that premise is false. Direct
measurement: all 16 trades are **entered between 18:06–20:24 ET and exited between 18:39–23:30 ET
the same evening** — entirely inside the post-18:00 product-open window, where intraday margin
has already resumed. "Exit time-of-day > 16:45" was simply the wrong test: it mis-flags evening
*entries* at the start of a session as if they were overnight holds. Under the correct exposure
test (does the holding interval intersect `[session_close − 15min, 18:00)`?), `BEST_ONE_NQ` has
**0 / 1,975** normal-session breaches, not 16.

**Verdict: NOT a compliance defect, NOT a margin/session-leak problem.** It was a false positive
produced by a badly-specified test in Wave 16, corrected in Wave 17 — before `BASELINE_MODELS.md`
was ever frozen. Nothing in the current baseline needs fixing.

## The dollar figure is real, but small and never actioned as alpha

V1h's report separately notes, explicitly flagged as an aside ("not a compliance matter"): all 16
of these trades happen to be losers, totalling **≈ −$33.5k**, and calls "evening-session entries
dying overnight" a real pattern worth a future D2 (missed-winner) / D4 (intraday-profile)
diagnostic. It was never acted on or promoted into a filter.

The "material share of baseline net" part of the owner's recollection is **not supported**:
−$33.5k is being measured against `BEST_ONE_NQ`'s own net (~$303k at the time, ≈11%), not
against CLAUDE.md's frozen canonical baseline (`SolarWaveRKReplicaV0`, net $146,440.60) — that
baseline is a different, earlier vendor-replica object over a different window, and this artifact
never touches it at all.

## Two things not to confuse this with

1. **V1e — the real breach, already fixed, same wave.** A *different*, coincidentally
   equal-sized set: 16 early-close-session margin breaches on the pre-fix `BEST_ONE_NQ` object
   (43 holiday early-close sessions in the dev window; the flatten rule was hardcoded to the
   normal session clock and never fired on early closes). Measured overlap with V1h's 16 evening
   trades: **0 — disjoint sets, coincidence only.** V1e *was* a real compliance breach and *was*
   fixed in W17 (C2 change, `MNQ_v2` adopts the parity-proven flatten logic).
2. **D4 (`runs/W18R1_M1_VOLSEASON`) — a separate, still-open, portfolio-level lead.** For the
   whole incumbent portfolio (not just the 16 V1h trades), the EVENING cohort (18:00–23:59 ET) is
   26.0% of bars but only −9.2% of P&L, net **−$10,989**. This is a broader, many-trade,
   aggregate time-of-day selectivity finding — a different object, different mechanism, different
   dollar figure than V1h's 16-trade set. It remains an unactioned lead, not closed the way V1h
   is, but per directive sec12 this run does **not** attempt to optimize a time window around it
   — that would re-litigate the closed session/hold construction axis (U1/U1B/U3/U4B, 3
   independent failed attempts) under a new name, which the standing directive prohibits.

## Also checked, and ruled out as the source

`U1_SESSION_HETEROGENEITY` (ETH-vs-RTH signal-mapping heterogeneity — finds ETH often *favorable*,
nearly opposite in flavor) and `U7_2026_TIMING_REGIME` (2026 entry-timing anomaly explained by a
volatility-regime shift, not an evening-specific effect) were both checked and are unrelated to
this issue.

## Search coverage

No duplicate or independently-named "SPEC01" investigation exists elsewhere. Searched and found
no mention: `reports/latest.md`, `reports/robustness.md`, `reports/leaderboard.md`,
`reports/OWNER_STATUS.html`, `research/registry/{experiments.yaml,hypotheses.md,
rejected_ideas.md,tested_configs.csv}`, `research/CAMPAIGN_STATE.md`, `research/frontier.yaml`,
`research/Research_Thesis.txt`.

## Verdict

**CLOSED — intended/already-corrected, not a specification defect.** No fix applied (none
needed — W17 already fixed the actual bug, V1e, and already corrected the false-positive
framing, V1h, before this baseline was frozen). Both Product A and Product B baselines unchanged.
The one live, still-open lead (D4's evening-cohort portfolio drag, −$10,989) is recorded here as
context, not reopened as a construction target this run.
