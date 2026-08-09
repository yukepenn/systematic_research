# U4B — short-side signal-gated early-flatten: NOT PROMOTED

**Disposition: NOT PROMOTED. Clean, decisive negative result.** The highest-EVI candidate
surfaced by wave 1 (`CONTINUOUS_EVOLUTION_WAVE1_SYNTHESIS.md`) — U4's giveback_ratio-at-
first-M-decay checkpoint, the cleanest right-tail-safe *descriptive* state found anywhere in
this campaign's diagnostic history — does **not** survive the transition from predictive label
to actionable trading rule. All 3 grid cells fail on every axis: worse net, worse Sharpe, and
worse (not better) maxDD/CDaR95 than control, both full-history and 2022-2025-only.

## Correctness gate: PASS

CONTROL (threshold=None) reproduces the certified incumbent exactly: NQ net $301,915.92, MNQ
net $28,587.10 (`runs/U4B_SHORT_DECAY_DERISK/out/u4b_control_summary.json`), and the CONTROL
position path is asserted identical to `substrate.build_pos_seq(M)` bar-for-bar.

## Construction

Short-only, signal-gated early flatten on Product B (BEST_ONE_NQ/MNQ, one shared decision
core). Once a short block's first-M-decay checkpoint fires (first bar where `M_change` opposes
the position — identical definition to `runs/U4_SHORT_MECHANISM/src/02_checkpoint_analysis.py`),
the overlay monitors `giveback_ratio` each subsequent bar and forces `tgt=0` (full flatten, the
only mechanically possible "de-risk" action in a strict one-contract system — see spec.yaml's
disclosed correction of U4's "halve exposure" wording) once it crosses a fixed threshold.
Preregistered grid: threshold ∈ {1.5, 1.75, 2.0}, informed by U4's own loser-population median
(2.12), well above U4's own right-tail-checked value of 1.0.

## Grid results (canonical window, NQ economics)

| threshold | net_NQ | Δ full-history | Δ 2022-2025-only | Δ LOYO(2026) | maxDD_eod | CDaR95 | n_overlay_exits |
|---|---:|---:|---:|---:|---:|---:|---:|
| control | $301,915.92 | — | — | — | $59,717.44 | $44,518.39 | — |
| 1.50 | $270,182.44 | **-$31,733.48** | -$15,190.20 | -$15,190.20 | $61,324.16 | $46,805.96 | 951 |
| 1.75 | $274,497.04 | **-$27,418.88** | -$12,572.92 | -$12,572.92 | $61,919.92 | $47,940.75 | 814 |
| 2.00 | $278,677.00 | **-$23,238.92** | -$8,007.20 | -$8,007.20 | $62,843.76 | $48,325.72 | 692 |

Every cell moves in the same (bad) direction — no fragile-needle ambiguity, a real plateau of
failure. Sharpe: control not separately re-quoted here but every candidate sits at 0.99-1.02,
below the incumbent's known ~1.2-region full-system Sharpe. MaxDD and CDaR95 are **worse**, not
better, at every threshold — this is not even a debatable "less net but safer" trade-off
(directive sec66's own test): the construction loses on both dimensions simultaneously.

## Right-tail check (post-construction, on the actual position path — not just U4's diagnostic)

At threshold=2.0 (the mildest, most conservative cell): only 2 of the top-20 all-time short
winners were actually touched by the overlay (blocks 2790 and 3589), losing **-$1,793.72** and
**-$5,578.72** respectively — a combined **-$7,291.16** hit concentrated in just 2 blocks, out
of **-$17,980.56** total damage across all 1,060 short blocks. Meanwhile the bottom-20 losers
improved by only **+$1,841.64** combined — an order of magnitude smaller than the damage to the
top-20 winners alone. This is the same "cuts real winners short while barely helping losers"
pattern R1's original grid was closed for, now confirmed independently via a narrowly-targeted,
well-validated-predictive-signal construction rather than R1's blind threshold sweep.

## Why the predictive signal didn't survive construction

U4's diagnostic measured a *population-level tendency*: higher giveback_ratio at the first-M-
decay checkpoint statistically associates with worse eventual outcomes (Spearman -0.50 to -0.65).
But that tendency is not a sharp separator — a meaningful share of real winners also pass through
elevated giveback_ratio at some point before recovering (short squeezes reversing back in the
position's favor), and forcing an exit the moment the threshold is crossed consumes exactly that
recovery optionality. The 692-951 overlay-exit count (out of 1,060 total short blocks) shows the
condition fires on the large majority of shorts, not a narrow, cleanly-separated minority —
confirming the same predictive-label-vs-actionable-rule gap this campaign has hit before (R1's
own closure, and R2V1/R2B's fixed-delay/pullback-reclaim mechanisms before *their* corrections).

## Verdict

**NOT PROMOTED.** Reinforces, via an independently-constructed and much more narrowly-targeted
mechanism, R1's original CONFIRMED-NOT-BENEFICIAL finding: giveback-conditioned early exits do
not translate into a net-positive, DD-improving trading rule for this system, even when gated to
the single cleanest-right-tail-in-diagnostic-history predictive state found in this campaign and
restricted to the one side (shorts) where the underlying mechanism is strongest. This closes the
short-side de-risk axis at this level of construction; a genuinely different mechanism (not
giveback-based) would be required to reopen it. Product B (`SolarWaveOneContractNQ_v5`/`MNQ_v5`)
is unchanged.
