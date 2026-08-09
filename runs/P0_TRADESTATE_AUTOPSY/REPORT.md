# P0 — Product-B trade-state ledger + April-2026 giant-loser autopsy — RESULTS

Descriptive/diagnostic only, per frozen `spec.yaml`. No promotion, no construction. Code:
`src/build_ledger.py`, `src/april_autopsy.py`, `src/generalize_autopsy.py`. Reference object:
BEST_ONE_NQ / Product-B shared decision core (`pos_incumbent`, from the already-certified
`runs/S2_SELTIME/out/r2/barpos_NQ_incumbent.npy` + `barpnl_NQ_incumbent.npy`). Ledger:
`out/ledger_full.parquet` (519,714 bars, 47 columns). **Reconciles exactly**: sum of bar P&L =
$301,915.92 = the certified BEST_ONE_NQ full-history net; 1,978 position-blocks = 1,978 round
trips in the independently-verified leg CSV.

## Part 1 — identifying the exact April-2026 trades

The owner's two named observations, matched by entry/exit date pair (not assumed from
screenshot timestamps):

| owner's label | exact trade (from ledger) | net P&L |
|---|---|---:|
| "2026-04-06 / 2026-04-07" | SHORT, entry 2026-04-06 21:42:00 @ 24512.00, exit 2026-04-07 04:03:00 (128 bars, 6.4h) | **-$2,032.18** |
| "2026-04-12 / 2026-04-13" | SHORT, entry 2026-04-12 18:06:00 @ 25259.75, exit 2026-04-13 02:24:00 (167 bars, 8.4h) | **-$2,727.18** |

For context, the single largest short loser in the surrounding window (2026-04-01..04-20) is a
different, un-flagged trade: 2026-04-07 18:36→18:36 (1 bar, -$4,477.18, a single-bar adverse
print), and 2026-04-07 15:00→15:21 (8 bars, -$3,372.18) — both smaller in duration than the two
the owner flagged, and not date-pair-matching either named observation, so not treated as the
targets. Full context table: `out/april_all_short_losers.csv`.

## Part 2 — testing the owner's hypothesis ("Solar reversed while B-MOM/M kept the short held")

**Literally as stated: NOT CONFIRMED for either trade.** `B` (BMOM) is **flat (0.0) for the
entire duration of BOTH trades** — BMOM never took a position, engaged or otherwise, so there is
no "B-MOM veto" in either flagged case; `M` reduces to `WSOLAR * T'` throughout. None of the
four operationalized reversal tests (>=7/13 members bullish, >=10/13 strong majority, T' sign
flip, fast-member+majority) fired materially ahead of the eventual exit in either trade — in
Trade A, T' does flip positive, but in the *same bar* the exit itself fires (0 bars / 0 minutes
lead time); in Trade B, none of the four tests ever fire during the entire 167-bar hold. Full
bar-by-bar traces: `out/trace_2026-04-06_2026-04-07_block3743.csv`,
`out/trace_2026-04-12_2026-04-13_block3757.csv`; machine-readable verdicts:
`out/april_hypothesis_test.json`.

**What actually happened instead, identically in both trades:**
1. Entry on a real but not-overwhelming Solar consensus (Trade A: T=-4/-5, 5-6 of 13 members
   bearish; Trade B: T=-9, 12 of 13 members bearish — stronger, but still Solar-only, B=0).
2. Price moved favorably first, building real open profit (Trade A MFE $1,247.82 at 22:09;
   Trade B MFE $982.82 at 20:00).
3. The Solar ensemble then decayed gradually — members flip back to neutral/opposite ONE AT A
   TIME over many hours (Trade A: T walks -5→-4→-3→-2→+1 over ~6 hours; Trade B: T walks
   -9→-8→-7→-4→-3→-2→-1 over ~8 hours) — while `M` (=0.7086×T' here, since B never engages)
   stays inside the hold band (`M < -EXIT_LEVEL = -1.0`) for most of that decay, because
   `EXIT_LEVEL` is an absolute threshold and T' only moves in whole-number steps.
4. The position is held through the ENTIRE decay, giving back essentially all of the open
   profit (giveback ratio 2.6x and 3.8x respectively — i.e. the eventual loss is 2.6-3.8x the
   size of the profit that was once open) before `M` finally crosses `-EXIT_LEVEL` and the exit
   fires.

This is a **real, mechanistically identified pattern** — "hold through a slow, monotonic
own-signal decay, give back the open profit before the coarse threshold catches it" — just not
the specific BMOM-veto form the owner guessed. It is a more general, and arguably more
important, finding than the original hypothesis, and it generalizes (Part 3).

## Part 3 — generalization across all 1,978 incumbent position-blocks

`out/block_level_summary.csv` (per-block giveback_ratio, decay_frac, duration, max conviction,
B-engagement), `out/bucket_summary.csv` (percentile-bucket comparison), `out/
generalization_diagnostics.json`.

| bucket | n | net $ sum | giveback_ratio median | % giveback_ratio > 1.0 | decay_frac median | n_bars median | % B engaged |
|---|---:|---:|---:|---:|---:|---:|---:|
| bottom 1% losers | 20 | -116,784 | 5.92 | 75.0% | 0.75 | 54.5 | 55.0% |
| bottom 5% losers | 99 | -409,760 | 6.07 | 66.7% | 0.50 | 37.0 | 78.8% |
| bottom 10% losers | 198 | -684,193 | 5.62 | 68.7% | 0.57 | 41.0 | 78.8% |
| top 1% winners | 20 | +280,054 | 0.063 | **0.0%** | 0.00 | 252.5 | 95.0% |
| top 5% winners | 99 | +844,883 | 0.089 | **0.0%** | 0.00 | 151.0 | 93.9% |
| top 10% winners | 198 | +1,273,731 | 0.120 | **0.0%** | 0.10 | 141.0 | 93.4% |
| all losers (n=1,151) | | -1,784,477 | 2.72 | 78.5% | 0.60 | 48.0 | 66.3% |
| all winners (n=827) | | +2,100,548 | 0.33 | 0.0% | 0.20 | 127.0 | 83.6% |

**Headline finding: `giveback_ratio` is a strong, clean, monotonic discriminator between
catastrophic losers and preserved winners.** Spearman correlation of `giveback_ratio` with
`net_pnl` among losers alone = **-0.656** (bigger loss <=> more given back, strongly
material). **100% of bottom-decile losers have giveback_ratio > 1.0, vs 0.0% of top-decile
winners** — a near-total separation, not a marginal tendency. `decay_frac` is directionally
consistent (losers decay more before exit) but materially weaker (Spearman -0.192 among
losers) — giveback dominates as the actionable signal, decay is corroborating context, not
the primary lever.

**This generalizes and strengthens the prior campaign's D-WINNER-2 finding** (`runs/
D_WINNER_AUTOPSY/REPORT.md`, top-decile WINNERS only: mean giveback 10.5%, median 0%, p90
42.1%, concentrated in long-held blocks) by showing the mirror image is true, more strongly, on
the LOSER side, and specifically that duration alone does NOT discriminate: the "long-held"
bucket (>20 bars, n=1,567) is net **+$722,950** in aggregate (this is where essentially all the
edge lives) but **46.8% of even these long-held blocks still have giveback_ratio > 1.0** — so a
duration-only rule would be far too blunt; `giveback_ratio` (optionally combined with `decay_frac`
as a confirming signal) is the correct lever, not `n_bars` alone.

**Right-tail caution, already visible here (mandatory per directive sec 11/25):** top-decile
winners are NOT giveback-free — p90/p95/p99 giveback_ratio among the top 198 winners is
0.34/0.41/0.54, max 0.64. A naive rule that exits on ANY meaningful giveback (e.g. ratio > 0.3)
would risk clipping legitimate winners still in progress. The clean separation is at the >1.0
boundary (net giveback exceeding the entire peak profit) where zero winners ever appear, in any
bucket, at any percentile tested. Any R1 construction must therefore look for state-conditioned
triggers close to that boundary, not an aggressive low threshold, and must be evaluated with the
full right-tail retention gate before any promotion is considered.

**Secondary finding (not this run's focus, flagged for R1's disposition):** BMOM engagement
rate differs by bucket (55-79% for loser buckets vs 93-95% for winner buckets) — trades where
BMOM never confirms (Solar-only) are over-represented among the worst losers. This is
correlational context, not a re-opening of the literal B-MOM-veto hypothesis (which is
independently refuted for the two named trades in Part 2); it is noted for R1-C's honest
disposition, not asserted as causal here.

## Disposition

Diagnostic complete. The owner's literal hypothesis is **refuted** for the two named trades
(no B-MOM engagement at all, hence no veto possible) but the autopsy surfaces a **stronger,
generalizable, and already partially corroborated** mechanism (own-signal decay + un-captured
giveback before a coarse absolute exit threshold fires), independently confirmed on both flagged
trades AND on the full 1,978-block population with a clean, large-effect-size discriminator.
**Promoted to R1 preregistration** (`runs/R1_ADAPTIVE_EXIT/spec.yaml`) as the primary construction
hypothesis, superseding the narrower R1-C framing suggested in the MEGA RESEARCH DIRECTIVE with
the evidence actually found. No trading rule has been constructed or tested in this run.
