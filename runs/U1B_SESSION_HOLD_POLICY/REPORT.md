# U1B — session-conditioned HOLD policy: NOT PROMOTED (both legs)

Persisted here by the orchestrating session from the subagent's returned text — its Write tool
blocked direct creation of this file.

## Correctness gate: PASSED exactly

Leg 1 at `exit_level_eth=1.0` reproduces `health_substrate.build_pos_seq(M)` bar-for-bar;
canonical-slice nets = NQ $301,915.92, MNQ $28,587.10 (exact). Leg 2 at `multiplier=1.0`
reproduces canonical net = $177,924.40 (exact). Both cross-checked independently against
`u0_state_table.parquet`'s own `position_B`/`bar_pnl_B_nq_dollars` and `target_exposure_A`/
`bar_pnl_A_dollars` columns — exact match, a second, independently-built construction agreeing
byte-for-byte with U0. Extended-window baselines also match U0's own recon exactly.

## Disclosed construction artifact: Leg 1's 2-cell grid is mechanistically degenerate

`M = WSOLAR·Tp + WBMOM·B` only takes discrete values — enumerating all achievable values shows a
quantization gap between ≈1.42 and ≈2.13. Since `exit_level_eth∈{1.5, 2.0}` both sit inside that
gap, they produce bit-for-bit identical position paths and dollar-for-dollar identical results.
The preregistered "2-cell grid" therefore tested only one distinct construction, not two —
disclosed rather than silently reported as a genuine sweep.

## Leg 1 — Product B, graded ETH exit weakening — NOT PROMOTED

| Metric | Control | Candidate (exit_level_eth=1.5 or 2.0, identical) |
|---|---:|---:|
| NQ net (canonical) | $301,915.92 | $276,702.72 (**−$25,213.20, −8.35%**) |
| MNQ net (canonical) | $28,587.10 | $25,914.60 (**−$2,672.50, −9.35%**) |
| Sharpe (NQ) | 1.1131 | 1.0363 (worse) |
| Sortino (NQ) | 1.8839 | 1.7533 (worse) |
| Calmar (NQ) | 1.1186 | 1.3105 (better) |
| maxDD_eod (NQ) | $59,717.44 | $46,713.60 (better, −21.8%) |
| CDaR95 (NQ) | $44,518.39 | $35,596.13 (better, −20.0%) |
| Years positive (of 5) | — | 2/5 (2023, 2025) |

2022-2025-only delta = −$22,858.44 (LOYO identical) — not a 2026-stub artifact, barely changes
excluding 2026. Year-by-year: 2022 −$22,798.88 (~90% of the full-history loss), 2023 +$1,124.0,
2024 −$9,090.16, 2025 +$7,906.64, 2026-stub −$2,354.76. Extension (observational): worse there
too (NQ −$6,346.16, MNQ −$639.80). Right-tail (1,341/1,978 = 67.8% of canonical blocks are
ETH-touched): top-20 ETH-touched winners: 16/20 untouched, 4/20 mildly reduced (sum −$8,463.08),
0/20 flipped negative. Bottom-20 ETH-touched losers: 5/20 improved (sum +$13,141.02), 2/20
worsened. Net effect on these 40 flagged blocks is positive (+$4,677.94) but dwarfed by the
−$25,213 full-window loss — damage concentrated in the broad middle population, not the extremes.
Turnover/cost: +240 extra round-trips, ≈$523/$156 extra commission — only ~2% of the loss, a
genuine forfeited-continuation-value effect, not a cost artifact.

A real DD/CDaR95 risk-reduction exists, but at a disproportionate net-dollar cost with degraded
Sharpe/Sortino, majority-of-years failure, and a loss concentrated in the earliest year rather
than fading.

## Leg 2 — Product A, graded ETH exposure shrinkage — NOT PROMOTED (cleaner failure than Leg 1)

| Metric | Control | mult=0.85 | mult=0.70 |
|---|---:|---:|---:|
| Net (canonical) | $177,924.40 | $170,927.30 (**−$6,997.10**) | $166,138.60 (**−$11,785.80**) |
| Sharpe | 1.1770 | 1.1461 (worse) | 1.1285 (worse) |
| Sortino | 2.3371 | 2.2834 (worse) | 2.2830 (worse) |
| Calmar | 2.2896 | 2.0797 (worse) | 1.9428 (worse) |
| maxDD_eod | $17,192.90 | $18,184.20 (worse, +5.8%) | $18,920.00 (worse, +10.0%) |
| CDaR95 | $14,323.08 | $14,774.74 (worse) | $15,226.32 (worse) |
| Years positive (of 5) | — | 0/5 | 2/5 |

Every risk AND return metric is worse at both grid cells — strictly dominated. Monotonic
dose-response in the wrong direction (more shrinkage = worse). 2022-2025-only delta: −$4,594.10
(0.85) / −$8,436.20 (0.70), not a 2026-stub artifact — every single year negative at mult=0.85.
Extension also worse. Right-tail (3,503/4,809 = 72.8% ETH-touched): top-20 winners 13/20 damaged
at both cells (worse than Leg 1's 4/20), 0/20 flipped negative. Bottom-20 losers 11-12/20
improved. Turnover: counterintuitively fewer transitions, a commission saving — so this failure
too is a genuine lost-continuation-value effect.

## Verdict

**NOT PROMOTED — both legs, exactly per the U4B precedent.** Leg 1 trades a real DD/CDaR95
improvement for a larger, chronologically-inconsistent net-dollar loss with degraded Sharpe/
Sortino. Leg 2 is strictly worse on every metric at both grid cells with a clean monotonic
dose-response confirming the direction is genuinely negative. Both legs show the same
qualitative pattern U1's diagnostic anticipated (RTH>ETH continuation value is real) but, exactly
as U3 and U4B found before them, acting on that signal via an actual holding-phase rule destroys
more value across the broad population of affected positions than it recovers from the specific
bad holds it targets. No cell looks genuinely promising on all axes — no adversarial
re-verification pass is warranted.

This closes U1B and leaves U1's cross-product-corroborated finding as a real-but-not-actionable-
at-this-construction-layer empirical fact, consistent with U3's and U4B's prior closures on this
same continuation-value question. The session-conditioned hold/exposure axis at the "graded delta
on the incumbent's own exit/exposure threshold" level of construction should be considered
exhausted absent a materially different state variable.
