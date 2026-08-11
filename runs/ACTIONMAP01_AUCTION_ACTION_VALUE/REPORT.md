# ACTIONMAP01 — Auction Action-Value Decomposition: CLOSURE REPORT

**Date:** 2026-08-10
**Family:** Auction (`NQ_VOLUME_AT_PRICE`), action-mapping layer on top of AUCTION04/M5's clean
causal-predictor finding
**Data used:** consumed data only — the 37 BBO-usable discovery sessions + 6 BBO-usable
confirmation-pool sessions already read by AUCTION01-04 (43-session union). Zero new sessions
opened, zero protected-pool sessions touched (`research/system_master/PROTECTED_EVIDENCE_BUDGET.md`
still shows 160 untouched). Predictor rebuilt via the certified-clean causal code path
(`runs/AUCTION04_CLEAN_CAUSAL_SUBSTRATE/src/01_build_clean_substrate.py` /
`05_m5_clean.py`, imported verbatim, not re-derived).

## 0. Verdict

**CLEAN INFORMATION STATE. NO CURRENT ACTION MAPPING.**

Per master directive sec146: this result is classified as a clean closure, not a failed run and
not grounds to retune Auction. `abs_value_dist_ticks` / `value_dist_ticks` remain a real,
direction-stable piece of state -- they are simply not, on this substrate, decomposable into a
distinct add/hold/reduce **action-value** mapping beyond the single univariate relationship M5
already reported. The state is preserved as-is for future interaction with DOM/new execution
information (sec146); Auction itself is not re-tuned, and no new Auction construction is opened
this pass.

## 1. Why: the diagnostic's own findings

`runs/ACTIONMAP01_AUCTION_ACTION_VALUE/out/00_diagnostic.md` (full detail; reused here) ran the
add/hold/reduce decomposition the task asked for, on Product-A primary / Product-B secondary,
discovery n=4,374 (36 sessions) + confirmation n=673 (6 sessions), horizons H in {1,3,20} bars,
cost hurdle C1=2.872 ticks.

**1a. Mechanical identity -- no 3-way action space exists to decompose.** Reading the actual
upstream build code (`runs/AUCTION02_ACTION_RELEVANCE/src/01_build_action_substrate.py`) shows
`signed_markout_H_A = sign(target_exposure_A) * (fwd_close - close) / TICK` -- a per-contract
formula with **no size term at all**. Under the master directive's own no-market-impact
assumption for tiny research size, this makes the three candidate actions mathematically
identical to Q_hold, not empirically distinguishable from it:

| Action | Value | Relation to `Q_hold(t) = signed_markout_H_A(t)` |
|---|---|---|
| HOLD | `Q_hold(t)` | -- |
| ADD (one more unit, same side) | `Q_add(t)` | `== Q_hold(t)` |
| REDUCE (one fewer unit) | `Q_reduce(t)` | `== -Q_hold(t)` |
| REVERSE (one unit, opposite side) | `Q_reverse_per_unit(t)` | `== -Q_hold(t)` (same per-unit number as REDUCE) |

This is a definitional consequence of how the substrate was built, not a testable claim -- there
is zero fill-level, partial-size, or market-impact-vs-size data anywhere in this substrate capable
of contradicting it even if real impact existed. Flat-state (`target_exposure_A==0`) rows, which
would need a separate "initiate" convention, are 1 row in the full raw table before filtering -- not
an analyzable population. **Conclusion: there is no distinct Q_add question separate from Q_hold
in this data**, so the requested 3-way action-value decomposition collapses to a single question --
does distance deteriorate the incumbent's own held value, and is that deterioration (a) symmetric
by direction, (b) linear or threshold-shaped, and (c) large enough to make reversal (not just
reduction) attractive.

**1b. (a) Symmetric.** Long and short both deteriorate with distance, same sign at every horizon
(long: -5.5t/-15.3t/-76.2t; short: -9.1t/-26.8t/-115.4t at H=1/3/20) -- though only the short side
individually clears dual-clustered (session+trade) significance standalone. A joint
aligned-vs-abs-distance fit shows the abs (direction-agnostic) coefficient dominates and reaches
significance at H=20 while the aligned (signed, "chasing") coefficient never does -- this is
symmetric magnitude-only distance, not a directional-extension effect.

**1c. (b) Closer to linear-with-mild-acceleration than a hard threshold.** Quintile-binned mean
Q_hold declines gradually from Q1-Q5 rather than showing a flat-then-cliff pattern; hinge
(broken-stick at the existing mid/far tercile boundary, 282.3 ticks) and quadratic-term
regressions add only small R2 improvements over the plain linear OLS at every horizon (e.g. H=20:
R2_linear=0.0289 vs R2_hinge=0.0299). The hinge-above slope is consistently steeper than
hinge-below (some acceleration, not ruled out as a true kink), but there is no clean
safe-below-X-ticks cutoff.

**1d. (c) Reversal is not economically attractive.** By the mechanical identity, the per-unit
value of reversing when far-from-POC equals `-1 x (far-tercile mean Q_hold)`. At the actionable
H=1 horizon this is +2.412 ticks -- only **+0.84x** the C1=2.872-tick round-trip cost hurdle, and
not itself dual-significant. Reducing/de-risking (which mechanically realizes the same
already-measured negative Q_hold) is supported by the evidence; reversing further is not.

**1e. (Q5) Direction is robust; significance is fragile.** Direction survives every stress test
run: symmetric by side, present in the RTH_MID-only subsample alone (dual-significant, n=3,740),
100% leave-one-session-out sign-stable across all 36 discovery sessions, same sign in the
6-session confirmation pool, and confirmed by an independently-designed block=5 circular-session
bootstrap (CONVENTIONS.md sec5: block=5, B=10,000, seed=20260808) at H=3/H=20. But formal
dual-clustered **significance** is not robust: it is lost at every horizon once the 3
most-influential of 36 discovery sessions (20260220, 20251124, 20260423) are removed, is never
dual-significant in the low-volatility regime, and does not reach dual-significance in the
underpowered 6-session confirmation pool (point estimate keeps the same sign, but the CI is wide).
A true RTH-vs-ETH split was infeasible: 0 of 4,375 `analysis_ok` rows are ETH -- the upstream
liquidity filter already restricts every usable decision point to RTH.

**1f. Product B needs no separate layer.** `position_B` is a pure {-1,0,1} directional flag with
no size dimension (0 rows with `|position_B|>1` exist anywhere in the raw table) -- "add one more
unit" is not a representable action for B at all. B's action space collapses to exactly
HOLD-vs-REDUCE-TO-FLAT, which by the same mechanical identity is simply `-Q_hold_B` -- a
structurally *simpler* decomposition than Product A's, not a distinct new finding.

**1g. Right-tail-mapping ambiguity, disclosed not resolved.** Per the task's own caveat (master
directive sec36-37/83-84) against defaulting to a de-risk/exit mapping: the deterioration is
measured directly on `Q_hold` (the existing incumbent exposure's own forward markout), not on a
separately-identified "new adds only" population -- because section 1a showed no such population
exists distinct from Q_hold. Read literally, the evidence implicates the existing position's own
expected value, not only the marginal economics of new additions. That said, significance is
session-concentrated (1e) and reversal is not economically attractive (1d), so this is not
evidence for an aggressive exit/reverse policy either. This diagnostic does not propose or freeze
any policy -- that remains explicitly out of scope.

## 2. Why this closes as CLEAN_NULL / NO_CURRENT_MAPPING, not a failed run

The task's premise -- "ACTIONMAP01 found NO stable action separation (or the diagnostic failed to
run)" -- is the correct read of the *action-differentiation* question specifically, and the
diagnostic **did** run to completion (see `out/00_diagnostic_log.txt`, 109 lines, all 7 parts
executed; `out/actionmap01_results.json`, full numeric detail). It did not fail; it answered the
question it was given and the honest answer is that no add/hold/reduce action space exists to
separate in this substrate (1a) -- the underlying univariate state itself (M5's
`abs_value_dist_ticks` deterioration finding) remains real and direction-stable, just not
decomposable into per-action values beyond what M5 already reported, and not significant enough
under stress (1e) to support any policy construction today. This is exactly the "clean
information state, no current action mapping" outcome sec146 anticipates, distinct from either
(i) a genuine action-differentiated finding ready for construction, or (ii) a diagnostic that
failed to produce usable output.

## 3. Disposition

- **No retuning of Auction.** Per sec146, this closure does not authorize revisiting AUCTION02's
  already-frozen rate-limiter policy, AUCTION03's M1-M4 slate, or AUCTION04's clean-substrate
  replication -- all remain exactly as previously closed
  (`runs/AUCTION02_ACTION_RELEVANCE/`, `runs/AUCTION03_MECHANISM_DECOMPOSITION/`,
  `runs/AUCTION04_CLEAN_CAUSAL_SUBSTRATE/`).
- **No new protected-pool spend.** This diagnostic opened zero new sessions; the
  `ACTIVE_RESEARCH_QUEUE.md` READY item "ACTIONMAP01 protected-pool power analysis + sequential
  protocol" was explicitly conditional on ACTIONMAP01 completing with a PASS verdict -- it does
  not, so that item does not trigger this wave.
- **State preserved, not discarded.** `abs_value_dist_ticks` / `value_dist_ticks` (causal running
  POC distance, certified-clean per AUCTION04) remain flagged `reusable_as_state=YES` in
  `STATE_INFORMATION_LIBRARY.csv` -- the direction-stable deterioration-with-distance relationship
  is exactly the kind of state a future DOM/Level-II or new execution-information family (sec146)
  could condition on or interact with, once that information class exists. Nothing here says the
  state is dead; it says the *action-mapping* attempt on top of it, using only currently-consumed
  data, is closed null.
- **EVI moves on.** With P3 (ACTIONMAP01) resolving NULL rather than PASS, the conditional P4
  ("Auction protected confirmation") item in `ACTIVE_RESEARCH_QUEUE.md`'s standing priority order
  does not trigger. The next genuinely-new-information-class items in that same standing order are
  P5 (DOM/Level-II operationalization -- `BLOCKED_OWNER`, pending one owner entitlement action per
  `runs/DOM01_DEPLOY_NT8_FEASIBILITY/`), P6 (options/dealer-state feasibility -- already
  `DATA_LIMITED`, no purchase authorized), P7 (cross-market EVI -- deferred, no specific motivating
  mechanism identified per `RESEARCH_FRONTIER.md` sec58/REL01), and P8 (capital/portfolio science
  refresh -- deferred, current). None of these are opened by this closure; this report only
  records that Auction's own queue slot is now fully resolved and does not itself select or start
  the next family.

## 4. Output files

- `runs/ACTIONMAP01_AUCTION_ACTION_VALUE/out/00_diagnostic.md` -- full diagnostic writeup (9
  sections, all tables reused above)
- `runs/ACTIONMAP01_AUCTION_ACTION_VALUE/out/actionmap01_results.json` -- full numeric results
- `runs/ACTIONMAP01_AUCTION_ACTION_VALUE/out/00_diagnostic_log.txt` -- execution log (all 7 parts
  ran to completion)
- `runs/ACTIONMAP01_AUCTION_ACTION_VALUE/src/01_action_value_diagnostic.py` -- diagnostic source
  (imports AUCTION04's certified causal substrate code verbatim, per this task's reuse mandate)
- `research/system_master/STATE_INFORMATION_LIBRARY.csv` -- Auction M5 row (`value_dist_ticks_action_relevance`)
  addended with this closure's action-mapping status
- `research/system_master/TESTING_LEDGER.csv` -- new row: ACTIONMAP01,
  family=Auction, hypothesis_class=action-value decomposition, status=CLOSED_NULL
