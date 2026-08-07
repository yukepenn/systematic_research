# C01 T0-6 — Univariate feature stability screens (RESULT: PASS, 5/8 fold-stable)

_Executed 2026-08-07 under the frozen constants of `C01_WAVE_SPEC.md` §T0-6 (unlocked by
T0-2 PASS). All interpretation decisions were pre-registered in the analysis script header
BEFORE any statistic was computed
(scratchpad `c01_t06_screen.py`, session wf 707cc7ae). Tier-0, zero config burn._

## Verdict

**WAVE GATE: PASS — 5 of 8 registered features are fold-stable on the frozen hit-rate rule
(gate requires ≥2). Tier-1 ML arms unlock: L2-logistic C ∈ {.01, .1, 1}, calibrated sigmoid
sizing vs binary filter vs vol-only control.**

| # | Feature | rho_hit by fold (1–5) | sign agree (hit) | stable HIT (gate) | sign agree (pnl) | stable PNL |
|---|---------|----------------------|------------------|-------------------|------------------|------------|
| 1 | consensus (dirn-aligned member mean sign) | +.98 +.93 +.90 +.72 +.83 | **5/5 +** | **YES** | 5/5 + | YES |
| 2 | age (bars since trend-birth extreme) | +.02 −.37 −.55 −.08 +.01 | 3/5 | no | 4/5 − | yes |
| 3 | prev_os (previous-segment overshoot/θ) | −.93 −.77 −.50 −.54 −.75 | **5/5 −** | **YES** | 5/5 − | YES |
| 4 | eff120 (path efficiency, 120 bars) | +.26 +.35 −.48 +.37 +.20 | 4/5 + | **YES** (borderline) | 3/5 | no |
| 5 | sig460 (ticks/bar) | −.56 −.40 +.42 +.44 +.47 | 3/5 | no | 4/5 − | yes |
| 6 | volvol (std/mean of \|dclose\|, 460b) | +.77 +.31 +.32 +.64 −.53 | 4/5 + | **YES** (borderline) | 4/5 + | yes |
| 7 | sessbkt (6 ET bins; leave-one-out bucket replication) | +.71 +1.0 +.89 +.94 +.37 | **5/5 +** | **YES** | 4/5 + | yes |
| 8 | gap_atr (signed overnight gap / ATR14) | −.42 −.44 +.27 +.30 +.02 | 3/5 | no | 4/5 − | yes |

Tallies: hit-rate gate **5/8**; P&L version 7/8; stable on BOTH 4/8 (consensus, prev_os,
volvol, sessbkt); either 8/8. All 8 reported, none selected out; all 8 stand registered for
multiplicity in any downstream Tier-1 claim.

## What the stable features look like (pooled test deciles, uniqueness-weighted)

Weighted base hit-rate 0.335 (unweighted 0.396; n = 34,147).

- **consensus** — the strongest screen by far, monotone in both metrics, 5/5 both versions:
  hit 0.266 (lowest bin) → 0.387 (highest); pooled mean net −$221 → **+$24** (the only
  consensus bin with positive weighted P&L is full alignment). 13 distinct values (9 bins).
- **prev_os** — monotone NEGATIVE: hit 0.387 → 0.287, pnl +$72 (decile 1) → −$301
  (decile 10). Entries taken after an over-extended dying segment are the worst trades in
  the family; small prior overshoot is the only prev_os decile with positive weighted P&L.
- **sessbkt** — hit by bucket [18–02, 02–08:30, 08:30–09:30, 09:30–11:30, 11:30–15, 15–17]:
  0.303, 0.322, 0.318, 0.344, 0.353, **0.421**. The 15:00–17:00 ET bucket replicates as the
  best in every fold pairing; overnight 18:00–02:00 is the worst. Unweighted ordering
  identical (0.469 for 15–17).
- **eff120** (borderline 4/5, pnl version only 3/5): weak positive tilt, top decile hit
  0.352/pnl −$69 vs bottom 0.337/−$150. Treat as the weakest of the five.
- **volvol** (borderline 4/5 on both): top decile is the only one P&L-positive (+$17),
  hit 0.351 vs 0.334 bottom; fold 5 sign-flips on both metrics.

Failed plainly: **age** (3/5 hit — no stable ordering), **sig460** (3/5 hit; sign flipped
between the 2022 folds and 2024–2026 folds; its P&L version is 4/5 NEGATIVE, consistent
with SW08's known high-vol drag, but the frozen gate metric does not confirm), **gap_atr**
(3/5 hit; signed-gap monotonicity does not replicate).

## Harness (as frozen)

- Population: all 34,148 entries of the 13 V3 member ledgers
  (`runs/AUDIT02_V3_SWEEP_B/ledgers/b2v3__tf3_sm179_am0_th1_vp460_vm{6..30 step 2}_xm0_sc_slip1.csv`);
  34,147 matched to the rebuilt DC state machines (99.9971%, identical to T0-3's validated
  match; 1 dropped). Net is after Lifetime commission + 1 tick/execution. Label y = net > 0.
- Features strictly as-of flip-bar close (fill is next bar open); session bucket from actual
  fill clock time (bar stamp − 3 min). NaN counts: prev_os 13 (first flip per member),
  eff120 14, gap_atr 485 (ATR14 warm-up), dropped per-feature only.
- 5 chronological day-grouped folds, 236–237 trading days each:
  F1 2022-01-03→2022-11-30, F2 →2023-10-31, F3 →2024-10-01, F4 →2025-09-01,
  F5 →2026-07-31. Purge of overlapping label intervals: structurally vacuous (100% of
  trades are intraday — session-close exit — verified; 0 purged). 2-trading-day embargo
  after each test block: 35–69 training trades removed per fold. De Prado
  average-uniqueness weights over the 13-member concurrency (mean w = 0.208).
- Decile edges fit on TRAIN only; per-decile uniqueness-weighted hit-rate and mean net on
  TEST; Spearman(decile, stat) per fold; stable = majority sign in ≥4/5 folds. Gate counts
  the hit-rate version (label is frozen as net > 0). Feature 7 (categorical): Spearman of
  fold-f test-bucket hit-rates vs pooled other-folds bucket hit-rates, positive in ≥4/5.

## Pre-registered interpretation decisions (made before computation; recorded in script)

1. Consensus registered in direction-aligned form (trade_dirn × mean member sign): the raw
   mean sign is mechanically confounded with trade direction (the entering member
   contributes its own sign), so pooled-side monotonicity is only defined for the aligned
   version. Raw column retained in the trade cache as an unregistered diagnostic.
2. Episode age = bars since the trend-birth EXTREME (f − i_ext, T0-3's validated "B"):
   entries fire at flip confirmation, so "bars since birth" is only non-degenerate
   extreme-to-extreme.
3. prev_os θ = the threshold whose crossing ended the dying segment (S_old at the flip).
4. gap_atr SIGNED (spec-literal); ATR14 = Wilder (ewm α=1/14) on session daily bars.
5. Gate bit = hit-rate Spearman version (label frozen as P&L>0); P&L version reported.

## Honest calibration notes (do not affect the frozen verdict)

- The frozen 4/5-sign rule is loose: under an independent-fold null a feature passes the
  two-sided version with p ≈ 0.375, so "≥2 of 8" alone is weak evidence (null P ≈ 0.86).
  The PASS is carried by the two 5/5-both-versions features (consensus, prev_os) with
  large monotone spreads and by sessbkt's 5/5 replication — all three also replicate
  unweighted and would pass far stricter rules. eff120 and volvol are borderline
  passengers; Tier-1 should expect them to contribute little.
- Uniqueness weighting inverts per-trade economics: unweighted mean net is +$75/trade,
  weighted −$140/trade. The family's profit is concentrated in exactly the high-concurrency
  episodes that the weights discount — independent confirmation that consensus is the
  load-bearing feature, and a warning that any per-trade classifier trained with these
  weights is learning "which unique bets pay", not "where the money was".
- T0-10 negative control (day-of-week) governs pipeline trust for this wave; this screen
  used the same fold/embargo harness family.

## Files

- `research/04_complementary_family/c01_t06_fold_spearman.csv` — per feature × fold:
  n_train, n_test, n_bins, rho_hit, rho_pnl.
- `research/04_complementary_family/c01_t06_decile_stats.csv` — per feature × fold × bin:
  n, weighted hit, weighted mean net, train-fit bin edges.
- `research/04_complementary_family/c01_t06_pooled_deciles.csv` — pooled test deciles.
- Script + trade/feature cache: scratchpad `c01_t06_screen.py`,
  `c01_t06_trades.parquet`, `c01_t06_validation.json` (session wf 707cc7ae).

## Consequence

Tier-1 ML arms UNLOCK per spec: L2-logistic only, C ∈ {.01, .1, 1}, on the 8 registered
features (no selection), calibrated sigmoid sizing vs binary filter vs the mandatory
vol-only control; if the vol control matches the classifier, adopt vol targeting and close
the ML program. Global promotion gates (2-tick stress, ≥3/5 years, split-half, right-tail
constraint, Romano-Wolf) apply unchanged.
