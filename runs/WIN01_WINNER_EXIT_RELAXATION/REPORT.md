## WIN01 -- Winner-Qualified Exit Relaxation: CLOSED (both products fail the battery)

**Question.** Once a trade has proven itself (already-realized favorable excursion), is the incumbent's exit hysteresis flattening winners too early? Tested via a strictly causal, online winner-qualification rule and a frozen, data-justified relaxation construction for both Product B (discrete {-1,0,1}) and Product A (continuous exposure -13..+13).

**Bottom line: no. Both products fail decisively.** Product B's relaxation is a robust, uniformly-negative effect roughly 11-16x the campaign's 1% wash threshold, consistent across every year, every LOYO cut, and every cost-stress level. Product A's mild throttle (CAP1) is a small but consistent drag; its stronger floor variant (FLOOR050) nominally clears the wash threshold but is revealed by LOYO to be a single-year (2025) artifact, not a genuine effect. This closes the "loosen exit hysteresis for qualified winners" construction, joining STOP_OVERLAY_FRONTIER.md's other closed exit families -- and confirms, from a new angle, that this architecture's exit points are not leaving recoverable tail money on the table.

---

### 1. Correctness gates (passed before any candidate was evaluated)

- **Product B**: the merged single-pass decision+execution loop (needed to give the winner-qualification predicate a causal, online running-MFE signal) reproduces the certified canonical net **$301,915.92** exactly when qualification is set unreachable, AND matches the original two-pass `health_substrate.build_pos_seq`/`onelot_exec` **bar-for-bar** (`np.array_equal` on position, `np.allclose` on bar P&L). The refactor introduces zero behavior change on its own.
- **Product A**: the generalized decision+execution function reproduces the certified LEGACY (NQ-priced) canonical net **$177,924.40** exactly at qualification-unreachable. The separate `reprice()` function (used to re-price a fixed, already-decided position path onto genuine MNQ OHLC, mirroring PRICE01's dual-truth pattern) is self-checked by repricing CONTROL's own path back onto NQ prices and confirming it reproduces the same $177,924.40.

Both gates PASS. No STOP condition triggered.

### 2. Frozen construction (spec.yaml, written and committed before any result was read)

**Winner qualification** (both products, identical mechanism): running block MFE in dollars, tracked **online** inside the merged loop exactly as `u0_state_table`'s own `segment_and_mfe_mae` defines it (`mfe = running-max(max(cum bar pnl since block start, 0))`) -- a pure function of already-realized bars, zero look-ahead, reset on every sign change (flat, reversal, or forced session-close). Threshold **MFE >= $1,000** for both products, chosen from the *substrate's own* descriptive distribution before any candidate was run: for Product B this sits at the 54.6th percentile of the 1,978 canonical-window blocks (median block MFE = $1,172.82); for Product A it sits at the 86.7th percentile (median block MFE only $77.35, because most A blocks are small scale-in/out blips) -- disclosed as a stricter bar for A, not adjusted, because the question was "does the same proven-itself standard help," not "find A's own median." Pre-registered motivating fact (descriptive only, not fit to any intervention outcome): blocks that reach $1,000 MFE end up net winners 68.2% of the time vs 41.8% overall, but the mean `giveback_ratio` at the incumbent's own exit for those blocks is already **0.853** -- i.e., 85% of a qualified block's own peak favorable excursion is typically already given back by the time the incumbent flattens it.

**Product B relaxation** (2 cells): once qualified, the ordinary flatten trigger (`M <= EXIT_LEVEL=1.0`) is replaced, for that block only, by a lower threshold. Reversal trigger, C4 windows, and end-of-session forced flatten are completely unchanged.
- `WINB_RELAX_050`: relaxed exit level = 0.5 (position holds through the M in [0.5, 1.0] band the baseline treats as flat)
- `WINB_RELAX_000`: relaxed exit level = 0.0 (holds until M actually crosses to the opposite side of neutral)

**Product A relaxation** (2 cells): once qualified, the per-bar *same-sign decay* of `target_exposure_A` (never sign flips, never forced_flat/entry_blocked windows) is throttled by one of two mechanisms, chosen from the actual per-bar-decrease distribution (median decrease already 1 contract/bar; 90th pct = 3; 99th = 4; max = 8):
- `WINA_CAP1`: cap the per-bar |exposure| decrease at 1 contract (glide the rest over subsequent bars)
- `WINA_FLOOR050`: |exposure| may not decay below 50% of the block's own running peak (tracked online) until the raw M-implied target reaches 0 or flips sign

### 3. Product B results

**Headline (canonical window, <=2026-05-29, NQ 1-lot):**

| cell | canonical net | 2022-2025 net | delta vs control | delta % of control |
|---|---:|---:|---:|---:|
| CONTROL | $301,915.92 | $300,156.88 | -- | -- |
| WINB_RELAX_050 | $257,793.00 | $264,434.60 | -$35,722.28 | **-11.90%** |
| WINB_RELAX_000 | $260,634.16 | $268,200.76 | -$31,956.12 | **-10.65%** |

Both fail the <1% wash threshold by an order of magnitude, and both are actively *harmful*, not a wash.

**Year-by-year (LEGACY-equivalent, NQ 1-lot):**

| year | CONTROL | RELAX_050 | RELAX_000 |
|---|---:|---:|---:|
| 2022 | 116,718.52 | 109,636.48 | 109,305.84 |
| 2023 | 25,964.92 | 23,236.72 | 24,420.44 |
| 2024 | 67,398.52 | 53,090.96 | 53,419.68 |
| 2025 | 90,074.92 | 78,470.44 | 81,054.80 |
| 2026 (health-only, separate) | 1,759.04 | -6,641.60 | -7,566.60 |

Every single year is negative for both candidates -- there is no favorable year hiding in the aggregate.

**LOYO (leave-one-year-out, 2022-2025):** all 8 cuts (2 cells x 4 dropped years) are negative: -15.61%, -12.03%, -9.20%, -11.48% (RELAX_050); -13.38%, -11.09%, -7.72%, -10.92% (RELAX_000). This is about as robust a negative result as this campaign produces.

**2026 health-only extension (separate, not blended):** both cells identical, -$730.64 vs control's $58,675.04 (-1.2%).

**Cost stress** (commission 1x/1.5x/2x NQ, $2.18/$3.27/$4.36 per side): the gap does **not** close under stress -- RELAX_050 stays -14.6% to -15.2%, RELAX_000 stays -13.7% to -14.2%. Trade count drops modestly (CONTROL 1,890 entries vs 1,852/1,846 for the two candidates, -2.0%/-2.3%) -- fewer round trips, but the commission savings are trivial next to the giveback loss.

**Right-tail audit (MANDATORY):**

| | n blocks | top-20 sum | bottom-20 sum |
|---|---:|---:|---:|
| CONTROL | 1,978 | $280,054.22 | -$116,783.60 |
| WINB_RELAX_050 | 1,950 | $284,374.22 | -$117,483.60 |
| WINB_RELAX_000 | 1,944 | $284,374.22 | -$117,483.60 |

The 19 largest winning blocks in every cell are **byte-identical in dollar P&L** to control's own top blocks (e.g. the 2025-04-09 block: $41,337.82 in all three; the 2025-11-20 block: $19,717.82 in all three). These giant trending winners exit via **reversal, C4-forced-flatten, or session-close** -- never via the ordinary M-threshold that relaxation touches -- so the true right tail is completely unaffected by this construction. The only change in the top-20 sum is one new $15,017.82 block entering the list, displacing a $10,697.82 control block (net +$4,320, explaining the entire top-20 delta). The bottom-20 sum gets modestly worse (-$700). **Relaxation does not extend the right tail at all; the entire net loss is a body-of-distribution effect.**

**Opportunity-occupancy attribution (MANDATORY, sec30):**

| | extension_pnl | added_winner $ | added_loser $ | occupancy_blocked_cost | total delta (canonical) |
|---|---:|---:|---:|---:|---:|
| RELAX_050 | -$44,410.00 | +$75,155.00 | -$119,565.00 | $0.00 | -$44,122.92 |
| RELAX_000 | -$41,555.00 | +$85,545.00 | -$127,100.00 | $0.00 | -$41,281.76 |

The entire net loss is pure **giveback on the extension itself** (added losers outweigh added winners by ~1.6x). `occupancy_blocked_cost` (the "later-entry/reversal-blocking" channel sec30 asks for) is **exactly $0.00** for both cells -- this is not a coincidence but a structural fact of this architecture: Product B's reversal trigger (`M <= -ENTRY_LEVEL`) is checked identically for control and candidate regardless of exit-level relaxation, so whenever control has already reversed into a genuinely different position, candidate's own reversal condition necessarily fires on the *same bar* too (the reversal-strength move is always strong enough to blow through any relaxed exit level on its way past it). **This family therefore does NOT fail via occupancy-cost offset (sec30's stated failure mode) -- it fails via straightforward giveback on the extended holds themselves**, a cleaner and more decisive failure than an occupancy-cost wash would have been. (A small residual, ~$270-290 or ~0.6-0.7% of the total delta, separates `extension_pnl` from the exact total delta -- traced to a known limitation: a same-position "agree" bar occurring immediately after a control-side re-entry fill carries a small cash-basis discontinuity the bar-level AGREE/DIFFER split doesn't capture; disclosed, does not change the conclusion.)

**C4 interaction (explicitly tested per sec30):** of the blocks that *ever* reached qualification, ~49% (521/1,066 for RELAX_050, 524/1,065 for RELAX_000) end their life via the forced C4 flatten rather than via the relaxed M-threshold or a reversal -- versus only 1.0% (20/1,978) of ALL control blocks ever reaching a C4-forced exit. Within the qualified-and-relaxed population, exit-reason bucket **means** (absolute, not marginal-vs-control -- the marginal number is the extension_pnl above):

| exit reason (RELAX_050) | n | mean pnl | win rate |
|---|---:|---:|---:|
| C4_FORCED | 521 | +$3,162.49 | 92.1% |
| M_RELAXED_EXIT | 501 | -$107.46 | 43.1% |
| REVERSAL | 44 | -$1,365.59 | 29.6% |

Trades that keep trending favorably all the way to session close (C4_FORCED) look excellent in isolation -- relaxation never got a chance to hurt them because the loosened threshold was never triggered. The damage concentrates in the M_RELAXED_EXIT bucket (giving back most of the qualified gain before the looser threshold finally releases it, near-breakeven on average) and especially the REVERSAL bucket (holding through more of the reversal move before flipping, clearly negative). Separately: CONTROL's own tiny native C4-forced-exit population (n=20, the rare cases where the *unmodified* baseline still holds something into the close window) has a poor 20.0% win rate and -$2,424.93 mean -- a different, much smaller population, and one that does **not** match this family's background reference fact ("C4-forced exits win 75% of the time historically"). That discrepancy is flagged for the record but not reconciled here (likely a different measured population/construction elsewhere in the campaign) -- it does not affect this family's own conclusion.

### 4. Product A results (dual truth: LEGACY_RESEARCH_PROXY / GENUINE_MNQ_EXECUTION_ECONOMICS)

**Headline (canonical window):**

| cell | LEGACY canonical | GENUINE canonical | 2022-2025 delta LEGACY | 2022-2025 delta GENUINE |
|---|---:|---:|---:|---:|
| CONTROL | $177,924.40 | $178,687.40 | -- | -- |
| WINA_CAP1 | $175,599.20 | $176,337.70 | -1.105% | -1.114% |
| WINA_FLOOR050 | $187,726.10 | $188,521.60 | **+5.203%** | **+5.182%** |

GENUINE and LEGACY move together throughout (as expected -- the decision sequence is identical, only fill economics differ), so all qualitative conclusions below hold on both bases; GENUINE is primary for ranking per sec13/77 and shown alongside LEGACY throughout.

**WINA_CAP1**: consistently, mildly negative. LOYO (LEGACY): -0.66%, -0.66%, -1.95%, -1.16% across the four dropped years -- all four negative, a small but genuine drag with no offsetting benefit in any year or under cost stress (-1.31% to -1.51% at 1.5x/2x commission).

**WINA_FLOOR050**: nominally clears the 1% wash threshold and looks cost-stress robust (delta actually *increases* with friction: +5.51% at 1x, +6.12% at 1.5x, +6.77% at 2x -- the classic "looks unusually strong" pattern this campaign's discipline explicitly flags for a too-good-to-be-true check). Applying that check:
- **LOYO reveals single-year dependency**: drop-2022 +9.32%, drop-2023 +5.10%, drop-2024 +6.96%, **drop-2025 -2.17%**. Excluding 2025 flips the whole 2022-2025 result negative.
- **Year-by-year confirms it directly**: 2022 delta -$2,453.80, 2023 +$1,055.60, 2024 -$705.50, **2025 +$10,823.20** -- 2025 alone is larger than the entire aggregate delta ($8,719.50); the other three years net to -$2,103.70 (exactly matching the LOYO drop-2025 figure).
- **Manual block inspection** (not a bug): the single largest contributor is the 2025-04-09 block (control $17,871.45 -> candidate $23,686.15, +$5,815), the same tariff-shock trend day that also produced Product B's largest-ever block ($41,337.82). Several other large 2025 trending days (2025-11-20, 2025-04-08, 2025-10-10) contribute smaller positive deltas on top. This is a genuine, coherent trading dynamic during an unusually strong 2025 trending regime, not a leakage/lookahead artifact -- the qualification signal was already correctness-gate-verified as strictly causal. But it is exactly the "result depends on one year" pattern this campaign's own standing criteria treat as disqualifying, and it does not survive LOYO.

**Right-tail audit (LEGACY):**

| | n blocks | top-20 sum | bottom-20 sum |
|---|---:|---:|---:|
| CONTROL | 4,809 | $194,687.05 | -$61,275.40 |
| WINA_CAP1 | 4,804 | $199,508.60 (+$4,822) | -$62,252.45 (-$977) |
| WINA_FLOOR050 | 4,760 | $202,104.20 (+$7,417) | -$61,997.55 (-$722) |

Both cells show a modest, genuine right-tail improvement -- but it doesn't rescue CAP1's net-negative result (body-of-distribution losses dominate), and FLOOR050's improvement is itself part of the 2025-concentrated pattern above.

**Opportunity-occupancy attribution:**

| | extension_pnl | added_winner $ | added_loser $ | occupancy_blocked_cost | total delta |
|---|---:|---:|---:|---:|---:|
| WINA_CAP1 | +$1,234.10 | +$3,304.25 | -$2,070.15 | **-$2,844.30** | -$2,325.20 |
| WINA_FLOOR050 | +$4,784.55 | +$13,026.30 | -$8,241.75 | **+$5,245.35** | +$9,801.70 |

Unlike Product B, Product A's occupancy channel is **not** structurally zero: CAP1 shows a real, negative later-entry/scale-in cost (-$2,844.30) that overwhelms a small positive extension effect, netting negative overall. Entry/scale-in event counts confirm the mechanism is real: CONTROL 3,483 entries / 11,965 scale-ins vs FLOOR050 3,392 entries (-2.6%) / 11,602 scale-ins (-3.0%) -- the throttle genuinely suppresses some subsequent trading opportunity by keeping capital committed to the extended block.

**2026 health-only extension (separate):** WINA_CAP1 -$1,214.90 vs control ($34,970.10); WINA_FLOOR050 +$2,171.40 vs control (both bases identical since genuine MNQ prices aren't available in the health-only window, per U0's own disclosed NQ-proxy convention there).

### 5. Too-good-to-be-true gate (discipline sec6)

Applied explicitly to WINA_FLOOR050 given its surface-level cost-stress-robust +5.2% result. Checked for lookahead/leakage first: the winner-qualification MFE signal is computed online, purely from already-realized bar P&L within the current block (correctness-gate-verified identical to the certified baseline when qualification is set unreachable) -- no overlap between the predictor's measurement window and the outcome's own realization window. **No confound found.** The disqualifying finding is single-year (2025) regime concentration, confirmed by LOYO and direct block inspection, not a computational error.

### 6. Disposition and rationale

**CLOSED_EXIT_MAPPING.** Neither product produces a promotable candidate:
- Product B: both cells show a large, uniformly robust NEGATIVE effect (-10.6% to -11.9% of control's 2022-2025 net, 8/8 LOYO cuts negative, cost-stress-stable, right tail untouched, pure giveback mechanism cleanly identified).
- Product A: CAP1 is a small, consistent negative; FLOOR050's apparent positive is a single-year artifact that fails LOYO and does not represent a genuine cross-regime effect.

This closes the "loosen exit hysteresis for qualified winners" construction for this architecture -- a genuinely new, non-duplicative test (confirmed no prior art: D3/B9 do not exist in this repo; H-007 only tested tighter-or-equal ratios; SM03B used winner retention only as a pass/fail constraint, never as the treatment variable). It complements STOP_OVERLAY_FRONTIER.md's existing closures from the opposite direction, and is consistent with that document's own structural read: "37.9% of drawdown dollars are pure winner-absence... no exit rule can help these" -- this family adds the direct confirmation that loosening the exit doesn't help the *present* winners either, because the biggest ones already escape via reversal/C4/session-close untouched by any ordinary exit-threshold change, and the ones that do get extended mostly give back what relaxation bought them.

### Files
- `runs/WIN01_WINNER_EXIT_RELAXATION/spec.yaml` (frozen before any result was read; committed first)
- `runs/WIN01_WINNER_EXIT_RELAXATION/src/01_product_b_winner_relax.py` (merged causal decision+exec+qualification loop, correctness gates, full battery)
- `runs/WIN01_WINNER_EXIT_RELAXATION/src/02_product_a_winner_relax.py` (generalized decision+exec with cap/floor throttle, dual-truth LEGACY/GENUINE repricing, full battery)
- `runs/WIN01_WINNER_EXIT_RELAXATION/src/03_product_b_exit_reason_pnl.py` (C4-interaction exit-reason breakdown)
- `runs/WIN01_WINNER_EXIT_RELAXATION/out/*.json`, `*.csv` (recon JSON, year-by-year, LOYO, block-level tables for both products, all committed)
