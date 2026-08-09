# U4 — short-side mechanism science

**Disposition: diagnostic complete — partial-clean result found, does not fully clear promotion
bar.** (Persisted here by the orchestrating session from the subagent's returned text — its
Write tool blocked direct creation of this file.)

## Correctness gate: PASS

Product-B canonical short net reproduced from this family's own block segmentation =
**$35,112.38**, exact match to SA0 sec14 (independently re-verified by the orchestrator against
`runs/U0_UNIFIED_STATE/out/u0_state_table.parquet` directly: identical to the cent).

## Core finding: separation DOES emerge later on the path, growing monotonically

Entry-only replication (independent NN construction): matched-winner-rate 31.5% vs unconditional
38.4% — confirms SA0 sec15's null result at entry. But population-level Spearman(giveback_ratio-
at-checkpoint, eventual net_pnl), full canonical short-block population (not just extremes):

| checkpoint | Product B | Product A |
|---|---:|---:|
| +15min (5 bars) | -0.267 (n=741, p=1.6e-13) | -0.189 (n=1,691, p=4.8e-15) |
| +30min (10 bars) | -0.417 (n=771, p=8.8e-34) | -0.302 (n=1,681, p=1.2e-36) |
| first M-decay signal | **-0.544** (n=782, p=2.0e-61) | -0.399 (n=1,872, p=1.6e-72) |

Bottom-20 loser vs top-20 winner giveback_ratio medians (Product B): +15min 0.630 vs 0.000;
+30min 0.794 vs 0.171; first-M-decay 2.121 vs 0.261. `downtrend_age_M`/`reversal_freq_20` (both
directive-specified) show **no** signal (|Spearman|<0.03) — a clean negative result.

P0's two named April-2026 trades (block 3743 net -$2,032.18, block 3757 net -$2,727.18): at the
first-M-decay checkpoint, both show giveback_ratio 0.86-0.95 — above the winner median (0.26)
but below the worst-loser median (2.12), with 90-130 bars (4.5-6.5 hrs) of lead time before
actual exit. `first_fastflip` never fires in either (0/2), confirming P0's own finding.

## Right-tail check — the decisive result

Testing P0's own established boundary (`giveback_ratio > 1.0`) mid-trade against the largest
short winners ever:

| product | checkpoint | top-20 giant winners flagged | top-40 flagged | bottom-20 losers flagged (context) |
|---|---|---:|---:|---:|
| B | +15min | 5.3% | 15.4% | 22.2% |
| B | +30min | 15.8% | 15.4% | 31.3% |
| B | **first-M-decay** | **0.0% (0/19)** | **10.3% (4/39)** | 47.4% |
| A | +15min | 20.0% | — | 40.0% |
| A | +30min | 15.0% | — | 40.0% |
| A | first-M-decay | 30.0% | — | 70.0% |

Named giant winners that looked like disasters early: block 2864 ($16,267.82 net, giveback 2.62
at +15min), block 1449 ($10,242.82, giveback 2.88 at +30min), block 2790 ($11,782.82), block
2231 ($11,212.82). `vwap_disp_atr` was also checked (comparably strong bulk correlation, -0.25
to -0.37) but is **worse** on the tail (33-47% of giant B winners flagged) — giveback_ratio
remains the better lever.

**Verdict: NOT clean.** Product A fails at every checkpoint (15-30%). Product B's first-M-decay
checkpoint is the cleanest right-tail result found anywhere in this campaign's diagnostic
history (0/19 at n=20) but degrades to 10.3% at n=40 — comparable to R4's CLV (15%, already
judged not hard-filter-safe), not a clean pass.

## Chronology (2022-2026 canonical, year by year) + Jun-Jul-2026 extension (separate)

Spearman(giveback-at-first-M-decay, net_pnl) by year — Product B: 2022 -0.549, 2023 -0.593, 2024
-0.560, 2025 -0.502, 2026 canonical (Jan-May) -0.542, **2026 Jun-Jul health-only (observational)
-0.644 (n=43)**. Product A: 2022 -0.403, 2023 -0.457, 2024 -0.370, 2025 -0.425, 2026 canonical
-0.285, Jun-Jul health-only -0.518 (n=96). Remarkably stable every year, both products; the
health-only extension holds/strengthens rather than breaking down — consistent with SA0's
finding that the short-side reversed to profitability in Jun-Jul (this decay mechanism itself did
not stop working; the Jan-May weakness looks like a shift in how trades resolved after a normal
decay signal, not evidence the signal broke).

## Verdict

A real, causal, chronologically stable, monotonically-strengthening state **does** separate short
losers from winners at later checkpoints — directly answering the family's question, extending
P0/SA0 sec15. But it does **not** clear the promotion bar ("preserves historical giant short
winners while reliably flagging risk"): Product A never clears it; Product B clears it only at
small sample (n=20), degrading at n=40. Per directive instruction, this partial result is itself
the finding — reported plainly, not hidden.

## NOT YET TESTED idea (prose only, no code/backtest run)

A *graded* de-risk-speed policy for Product B only — upon the first-M-decay signal, halve
exposure (not flatten) only if giveback_ratio at that instant already exceeds ~1.5-2x (near the
loser population's own median 2.12, well above the 1.0 boundary that still catches real
winners), leaving ~90%+ of cases (including every top-20 giant winner and all but ~10% of
top-40) untouched. This is mechanistically the same lever R1 already tested broadly and closed
as CONFIRMED-NOT-BENEFICIAL (tail-dollar-negative, MNQ-divergent, unstable); this variant differs
(short-specific, signal-gated not fixed-window, partial-size not full-exit) but has no evidence
yet that those differences survive the same scrutiny — would need its own preregistration. Does
not transfer to Product A (no comparably clean checkpoint found).
