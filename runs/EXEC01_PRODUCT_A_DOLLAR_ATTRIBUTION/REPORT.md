# EXEC01 — Product A (SolarWaveSMMaster_v4) dollar-level execution attribution

**Disposition: RECONCILIATION COMPLETE for 9 sampled periods (exact); full-history explanation
EXTRAPOLATED, not proven.** This is audit/reconciliation work — it does not promote, kill, or
re-rank any strategy. It exists to answer one question precisely: *of Product A's certified
full-history NT8-vs-Python net-profit residual (+$19,405.30, +10.91%,
`runs/V1R4_NT8_PARITY/FULL_HISTORY_CERTIFICATION.md` L59-68), how much is attributable to known,
already-disclosed, non-defect execution conventions, and how much is genuinely unexplained?*

Answer: **100% of the dollars actually leg-verified are exactly explained (zero unexplained), and
a mechanically-justified extrapolation puts 97.8% of the full-history residual in the same two
known buckets — but only 6.2% of full-history turnover (55/1,139 sessions) was reduced to an
exact leg-by-leg proof.** The load-bearing number for future work, per campaign directive sec70,
is stated in Section 5.

## 1. What this measures, and what it does not

- Confirmed at task start, verbatim from source (no correction needed): Product A's full-history
  residual is **+$19,405.30 (+10.91%)** — NT8 stitched `$197,329.70` (7 chunks, E1 to E7,
  2022-01-03 to 2026-05-29, 1,139 sessions, no gaps) vs. the independently-certified Python
  mark-to-market reference `$177,924.40`. `FULL_HISTORY_CERTIFICATION.md` and
  `PRODUCT_A_CERTIFICATE.md` both state this residual was not yet reduced to an exact leg-by-leg
  proof the way BEST_ONE_NQ/MNQ were ("a plausibility argument, not a proof"). This run is the
  first attempt to close that gap for Product A specifically.
- Scope: 9 periods (55 sessions, 4.8% of the 1,139-session canonical window; 2,296 of 36,794
  contracts of turnover, 6.2%), selected before any NT8 record was opened, purely from
  Python-side decision-layer extremes (turnover, exposure, reversal density, scale-in/down
  density, best/worst day, early-close stress, cross-chunk spread) -- never from where NT8 and
  Python happen to disagree. Full selection rationale, frozen prior to reconciliation:
  `out/00_period_selection.md`.
- This is not a promotion decision for Product A itself, and it does not touch, re-derive, or
  contradict any prior CONTINUOUS SYSTEM EVOLUTION verdict.

## 2. Method (leg-by-leg, dollar-exact)

1. Python order-events, both price bases, built by re-running `product_a_exec_generalized`
   (reused byte-for-byte from `runs/PRICE01_PRODUCT_A_GENUINE_MNQ/src/01_dual_truth_repricing.py`,
   not re-derived) against the certified substrate. Correctness gate: canonical-window net
   reproduced the certified `$177,924.40` exactly before any output was trusted. PASS.
   (`src/01_build_python_orders.py`)
2. NT8 order-events extracted from the already-run output already on disk for the 9 periods --
   `chunks/A_E1/E3/E5/E6/E7_trades.json` (quantity recovered exactly via `comm / 0.65 / 2`, MNQ
   Lifetime commission, verified exact against the one explicit-`Quantity` source available
   [`producta_v4_2024apr_2025mar.json`] for every one of 78 overlapping trades) and the rich
   `producta_v4_2024apr_2025mar.json` job directly where it covers a period (explicit `Quantity`).
   No new NT8 backtest was run. (`src/02_build_nt8_orders.py`)
3. Reconciliation (`src/03_reconcile.py`): match Python and NT8 legs 1:1 within each period
   (exact `(time, side)` match, then a 30-minute fuzzy fallback for leftovers -- unused here, see
   Section 3), decompose every leg's dollar diff into exactly one of 9 buckets:
   `genuine_mnq_vs_proxy_price_basis`, `one_tick_convention`, `fill_timing`,
   `bar_boundary_serialization`, `same_bar_transition`, `commission`, `session_close_handling`,
   `rounding`, `unexplained`. Every row is asserted to sum its bucket columns back to its own
   `diff_total` to within $0.02 (floating-point tolerance only -- a hard failure otherwise). Price
   basis is isolated first and exactly (Python genuine-MNQ cash minus Python legacy-NQ-proxy cash,
   at identical time/side/qty -- the byte-identical-target-exposure invariant already proved by
   PRICE01). The remainder is classified by tick-size price difference and timing.

## 3. Leg-matching result: exact, complete, no ambiguity

| | value |
|---|---:|
| Periods reconciled | 9 (P1-P9), 55 sessions |
| Total legs | 1,371 |
| Exact (time, side) match | 1,371 / 1,371 (100%) |
| Fuzzy-matched | 0 |
| Python-only (unmatched) legs | 0 |
| NT8-only (unmatched) legs | 0 |
| Quantity mismatches (py_qty != nt_qty) | 0 / 1,371 |
| Total dollar residual examined (sum diff_total) | $1,203.50 |

Every single leg across all 9 periods -- spanning P1's earliest-history 2022 window through P9's
terminal-chunk 2026 window -- has a 1:1 NT8 counterpart at the identical bar timestamp, side, and
quantity. There is no decision-layer or order-count discrepancy anywhere in the 1,371 legs
examined: the entire $1,203.50 sample residual is a pure fill-price/basis effect, not a
missing-trade or extra-trade effect.

## 4. Bucket attribution: 100% of the sample residual, zero unexplained

| bucket | $ | % of $1,203.50 |
|---|---:|---:|
| `one_tick_convention` | $1,136.50 | 94.4% |
| `genuine_mnq_vs_proxy_price_basis` | $67.00 | 5.6% |
| `fill_timing` | $0.00 | 0.0% |
| `bar_boundary_serialization` | $0.00 | 0.0% |
| `same_bar_transition` | $0.00 | 0.0% |
| `commission` | $0.00 | 0.0% |
| `session_close_handling` | $0.00 | 0.0% |
| `rounding` | $0.00 | 0.0% |
| `unexplained` | $0.00 | 0.0% |

Both mechanisms are the same two, already-disclosed, non-defect conventions the certification
docs named for BEST_ONE_NQ/MNQ (fill-price convention, price basis) -- no new mechanism, and no
decision-logic defect, was found:

1. `one_tick_convention` ($1,136.50, 94.4%) -- Python's `_fill()` adds a synthetic 1-tick
   adverse slip on every leg (disclosed, deliberate conservative approximation); NT8's real
   Standard fill has none. Confirmed leg-by-leg, not assumed: 1,355 / 1,371 legs (98.8%) show
   NT8's price beating Python's genuine-MNQ price by exactly one tick (0.25pt) in the predicted
   direction; the remaining 16 / 1,371 (1.2%) show exact price equality, consistent with the
   synthetic slip being clipped by the bar's own high/low range (a bar too narrow to contain a
   full extra tick beyond the actual fill).
2. `genuine_mnq_vs_proxy_price_basis` ($67.00, 5.6%) -- isolated exactly via the
   byte-identical-target-exposure invariant (PRICE01): Product A's decision layer depends only on
   NQ-derived signal, never on price, so genuine-MNQ vs. NQ-proxy pricing affects fill economics
   only, and the effect is separable to the cent.

## 5. The sec70 bar -- current unexplained/unresolved execution-dollar residual

Per campaign directive sec70: a future Product-A challenger whose Python-research PnL
improvement is smaller than this residual must not be promoted on Python evidence alone -- it
requires executable (NT8) validation first. Three tiers, from most-proven to least:

| tier | scope | unexplained $ | unexplained % |
|---|---|---:|---:|
| A. Exactly proven (this run, 55/1,139 sessions, 6.2% of turnover) | 1,371 legs, $1,203.50 examined | $0.00 | 0.0% |
| B. Primary extrapolation (turnover-scaled, mechanically justified -- see Section 6) | full 1,139-session canonical history | $429.59 | 0.24% (of Python net) / 2.2% (of the $19,405.30 gap) |
| C. Conservative fallback (nothing beyond Tier A is proof, only plausibility) | full 1,139-session canonical history | $19,405.30 (minus the $1,203.50 already proven, so $18,201.80 not yet leg-verified) | 10.91% (unreduced full-history figure) |

**Headline number to cite going forward: $429.59 (0.24% of Python-side certified net profit;
equivalently 2.2% of the $19,405.30 full-history gap), Tier B, the primary point estimate.** This
is the residual left over after applying the study's own best (turnover-scaled) extrapolation of
the exactly-proven sample rate to the full canonical history -- see Section 6 for why turnover,
not session count, is the mechanically correct scaling variable. It is an extrapolation, not a
leg-by-leg proof, for anything outside the 9 sampled periods.

For any challenger whose claimed Python-side edge is comparable to or smaller than Tier C's
$19,405.30 (10.91%) -- i.e. anywhere near or below the full, not-yet-fully-leg-verified
historical gap -- treat it as requiring NT8 validation regardless of which tier is used, since Tier
B's optimism rests on an extrapolation assumption (constant per-contract tick-clip rate across
chunks) that has not been checked against the two unsampled chunks (E2, E4; see Section 7). For a
challenger whose edge safely clears $19,405.30 by a wide margin, Tier B is the operative,
better-supported estimate of what remains genuinely open.

## 6. Extrapolation to full history: 97.8% (primary) to 125.2% (upper bound) explained

| | value |
|---|---:|
| Full-history certified residual | $19,405.30 (+10.91%) |
| Sample coverage | 55 / 1,139 sessions (4.8%); 2,296 / 36,794 contracts turnover (6.2%) |
| `genuine_mnq_vs_proxy_price_basis`, full history | $763.00 -- EXACT, not extrapolated (PRICE01's own already-computed full-history figure, reused directly: `runs/PRICE01_PRODUCT_A_GENUINE_MNQ/REPORT.md` -- canonical genuine-MNQ net $178,687.40 vs legacy $177,924.40) |
| `one_tick_convention` sample rate | $0.4950 / contract-of-turnover (theoretical max $0.50/contract if never clipped by bar range -- sample rate is within 1% of that max) |
| `one_tick_convention`, turnover-scaled (PRIMARY) | $18,212.71 |
| `one_tick_convention`, session-count-scaled (upper bound) | $23,535.88 |
| Total explained, turnover-scaled (PRIMARY) | $18,975.71 = 97.8% of $19,405.30 |
| Total explained, session-count-scaled (upper bound) | $24,298.88 = 125.2% of $19,405.30 |

Turnover-scaling is primary because `one_tick_convention`'s dollar impact is a near-deterministic
linear function of turnover (approximately $0.50/contract, empirically $0.4950/contract in-sample
-- within 1% of the theoretical max). Session-count scaling is shown only as an explicit,
deliberately-biased upper bound: the 9 periods were selected for turnover/exposure/reversal
extremes, so they over-represent high-turnover sessions (41.7 contracts/session in-sample vs. 32.3
contracts/session full-history, +29%) -- applying the sample's average dollars-per-session
to the full history systematically overstates the explained total, which is exactly what its
125.2% (over 100%) result shows. Both bounds strongly support "fully attributable to the same two
known mechanisms, no decision-layer defect found" as a plausibility conclusion; neither is a
substitute for leg-verifying the remaining 93.8% of sessions.

## 7. Caveats and disclosures (carried from selection + surfaced by reconciliation)

- Chunks E2 (2022-09-01 to 2023-05-01) and E4 (2024-01-01 to 2024-09-01) are not independently
  represented among the 9 periods -- none of the top-ranked extremes on any selection criterion
  happened to fall there. If either chunk has a structurally different bar-range tick-clip rate
  (the 1.2%-of-legs mechanism that caps the synthetic slip below a full tick), the Tier B
  extrapolation in Section 5/6 would be off by a correspondingly small amount. This is the single
  largest source of uncertainty in the extrapolated (not the exact) portion of this result.
- P9 boundary caveat, resolved. P9 sits in the terminal chunk E7, which
  `FULL_HISTORY_CERTIFICATION.md` flags with an aggregate boundary-serialization anomaly (E7's own
  overall residual flips to -76%/-96%, attributed to a position still open at the literal last bar
  of the whole certified window, 2026-05-29, invisible to NT8's serialized trade list). P9's own
  window (2026-05-14 to 05-22) ends 7 sessions before that boundary. Its measured residual,
  +$149.00, is small, positive (NT8-favorable, same sign/order-of-magnitude as every other
  period), and entirely `one_tick_convention` plus `price_basis` -- zero
  `bar_boundary_serialization` dollars in P9, confirming the disclosed caveat did not
  materialize for Product A in this window.
- Quantity inference for the 4 chunk-only periods (P1, P2, P7, P8, P9) uses
  `quantity = comm / 0.65 / 2`. This inference produced zero quantity mismatches against the
  explicit-`Quantity` NT8 source it was checked against in the one overlap window available
  (2025-01-06 to 10, 78 trades) -- but was not independently re-verified in-place for P1/P2/P7/P8/P9
  specifically, since no explicit-quantity NT8 source exists for those calendar windows. The fact
  that all 1,371 legs in this run (including all 4 comm-inferred periods) matched 1:1 with zero
  quantity mismatches is itself further evidence the inference holds, but is not a fully
  independent re-verification.
- Day-bucketing convention: NT8 buckets a trade's whole PnL onto its entry date; Python's
  mark-to-market `bar_pnl` series (used for period selection, not for this leg-level
  reconciliation, which uses raw fill events) splits PnL across every day a position is held. This
  is an already-known, disclosed convention difference (confirmed concretely on 2025-01-06 to 10:
  NT8 entry-bucketed 1/9 net -$530.50 vs. Python mark-to-market 1/9 net -$322.20), not a defect,
  and does not affect the leg-level reconciliation in Sections 3-4 (which compares individual
  fills, not day buckets).
- Product A's leg-level decision layer had never been independently trade-count/leg verified in
  any prior wave before this run (unlike BEST_ONE_NQ/MNQ, which have an exact Q1-2025 proof).
  This run is the first such leg-level verification for Product A, and it is exact for the 9
  periods examined -- but it remains unverified, in the strict leg-by-leg sense, for the other
  1,084 (95.2%) of canonical sessions.
- Position never reaches the nominal +/-13-contract cap anywhere in the canonical window (observed
  ceiling: 11 contracts, 51 sessions touch it). "Near-cap" periods above target that actual
  observed maximum, disclosed in `00_period_selection.md` rather than silently redefined.

## 8. Bottom line

- No decision-layer defect was found in any of the 1,371 legs examined (zero quantity mismatches,
  zero unmatched legs, zero dollars unexplained in-sample).
- The full-history residual remains +$19,405.30 (+10.91%), unchanged by this run (this run
  explains it, does not revise it).
- Best current point estimate of what's genuinely still open: $429.59 (0.24% of Python net /
  2.2% of the gap) -- an extrapolation, not a proof, resting on turnover-scaling one exactly
  proven sample rate across two chunks (E2, E4) that were not independently sampled.
- Conservative fallback per sec70, until E2/E4 and the remaining approximately 93.8% of sessions
  are independently leg-verified: treat $19,405.30 (10.91%) as the bar for "small enough that
  NT8-only validation is mandatory before promotion," since only $1,203.50 of that figure is an
  actual proof today.

## 9. Files

| file | contents |
|---|---|
| `out/00_period_selection.md` | Frozen period-selection rationale, written before any reconciliation |
| `out/periods_selected.csv` | Machine-readable period definitions + per-period Python-side stats |
| `out/day_stats.csv` | Per-session Python decision-layer stats, all 1,139 canonical sessions |
| `out/python_orders_periods.csv`, `out/python_orders_full.csv` | Python-side order events (both price bases) |
| `out/nt8_orders_periods.csv` | NT8-side order events, 9 periods |
| `out/leg_reconciliation.csv`, `out/leg_reconciliation.json` | 1,371-row leg-by-leg match + bucket decomposition (this run's core evidence) |
| `out/reconciliation_summary.json` | Bucket totals, extrapolation arithmetic (source for Sections 4-6 tables above) |
| `src/00_select_periods.py` | Period selection (Python decision-layer stats, correctness-gated to `$177,924.40`) |
| `src/01_build_python_orders.py` | Python order-event construction, both price bases |
| `src/02_build_nt8_orders.py` | NT8 order-event extraction from already-run output |
| `src/03_reconcile.py` | Leg matching + bucket classification + extrapolation |
