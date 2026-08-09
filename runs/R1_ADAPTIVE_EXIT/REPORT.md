# R1 — adaptive exit / giveback / loss containment — RESULTS

**Disposition: CONFIRMED-NOT-BENEFICIAL. No candidate promoted. Incumbent unchanged.**

Frozen `spec.yaml` (12-candidate giveback-overlay grid) + one authorized R1-D ATR-stop benchmark
(3 settings, per directive sec10's "benchmark only" carve-out). Code: `src/construct.py`,
`src/construct_r1d_benchmark.py`. Construction verified byte-exact against the certified
incumbent before any candidate ran (`CONTROL` reproduces $301,915.92 NQ / $28,587.10 MNQ exactly,
asserted in code). Reference: BEST_ONE_NQ/MNQ shared Product-B decision core; same candidate
decision sequence priced on both instruments' genuine economics per directive sec2/sec32.

## Why this family was opened

`runs/P0_TRADESTATE_AUTOPSY/REPORT.md` found `giveback_ratio` (MFE surrendered before exit) is a
strong, clean discriminator between catastrophic losers and preserved winners (Spearman -0.656
among losers; 100% of bottom-decile losers have giveback_ratio>1.0 vs 0.0% of top-decile
winners) — both on the owner's own two flagged April-2026 trades and on the full 1,978-block
population. This motivated testing whether an early-exit overlay conditioned on live giveback
(optionally confirmed by signal decay) improves the incumbent.

## What was tested

An additive overlay (entry/reversal logic UNCHANGED) that forces an early flatten when, for the
CURRENTLY open position, running giveback_ratio >= threshold AND MFE >= a minimum floor
(optionally AND signal decay_frac >= 0.30). Grid: 2 designs x 3 thresholds {0.50, 0.65, 0.80} x
2 floors {$300, $600} = 12 candidates, thresholds chosen with reference to P0's own measured
winner-population giveback ceiling (p99=0.54). Plus 3 ATR-multiple hard-stop benchmarks {3x, 5x,
8x sigma460 at entry} as an R1-D price-risk-only control.

## Result: nothing in this family beats the incumbent's risk-adjusted return

| candidate | net $ | Sharpe | Sortino | Calmar | CDaR95 | maxDD | vs control |
|---|---:|---:|---:|---:|---:|---:|---|
| **CONTROL (incumbent, reproduced exactly)** | 301,915.92 | **1.113** | **1.884** | 1.119 | 44,518 | 59,717 | — |
| C03 (giveback>=0.65, floor $300) — best of 12 | 256,459.04 | 0.959 | 1.589 | **1.178** | **37,711** | 48,187 | Sharpe/Sortino WORSE, Calmar/CDaR better |
| C04 (giveback>=0.65, floor $600) — highest net of 12 | 262,929.56 | 0.996 | 1.669 | 1.092 | 40,528 | 53,257 | Sharpe/Sortino WORSE |
| ATR x8.0 (R1-D benchmark, best of 3) | 278,279.80 | 1.037 | — | — | 46,952 | 66,927 | Sharpe WORSE, DD WORSE |

Full leaderboard: `out/leaderboard.csv` (24 rows, NQ+MNQ x 12 candidates), `out/
r1d_benchmark.csv`, `out/control_battery.json`. **Every one of the 12 giveback candidates and
all 3 ATR-stop benchmarks has LOWER Sharpe and Sortino than the do-nothing control**, on both NQ
and MNQ execution economics. Only C03 clears the bare "2-of-4 primary metrics improved" bar
(Calmar + CDaR95), and even that is not a clean win once decomposed:

**C03 decomposed (the only candidate that reaches the primary-metrics gate):**
- **Tail dollar attribution is net negative, not net positive.** Over control's own top-decile
  winning blocks' exact time spans, C03 gives up **-$80,130 (-6.3%)** of the $1,273,730.92 the
  top 10% of winners earned; over control's own bottom-decile losing blocks' spans, C03 recovers
  **+$31,593 (+4.6%)** of the -$684,192.80 those losers cost. The overlay removes 2.5x more
  dollars from winners than it saves from losers — the net -$45,457 full-sample delta is NOT a
  coincidence of two offsetting effects, it is dominated by winner erosion.
- Top-day retention (91.6% top-10, 94.3% top-20) and top-trade retention (92.9%/94.2%/93.7% for
  top 1%/5%/10%) both clear the 90% floor in isolation, but the dollar-attribution check above
  shows *why* a bucket-retention-only view is insufficient on its own: percentage retention can
  look acceptable while the absolute dollars removed still dominate the dollars saved.
- **Chronologically inconsistent**: year-by-year net change vs control is -15.2% (2022), **-51.8%
  (2023)**, -9.9% (2024), -10.9% (2025) — 2023 is disproportionately damaged, not a
  uniformly-scaled effect, which is the standing chronology-robustness red flag (directive sec22).
- **MNQ leg shows a WEAKER, partially divergent result** (Sharpe 0.799 vs control 1.053, Sortino
  1.318 vs 1.784, Calmar 0.936 vs 1.045 — all three worse; only CDaR95 improves) — NQ's Calmar
  improvement does not carry over to MNQ, a real (if secondary) violation of the shared-core
  discipline's spirit (directive sec32).

**R1-D (ATR-stop benchmark) confirms this is not a construction-quality artifact**: naive
price-risk-only stops do WORSE than the state-aware giveback overlay on every setting tested
(lower Sharpe, and MaxDD actually INCREASES, 63-67k vs control's 59.7k) — so the giveback
mechanism is the stronger of the two exit-overlay ideas tested, and even it fails. This is
evidence the incumbent's existing `EXIT_LEVEL=1.0` M-threshold exit is already close to
efficient for this architecture, not that the overlay implementation is flawed.

## Right-tail / left-tail gate verdict (directive sec11/25/26, mandatory)

**FAILED for every candidate that reached this check.** The one candidate closest to promotion
(C03) removes more absolute dollars from the right tail than it recovers from the left tail. No
candidate is proposed for promotion on tail grounds even before Sharpe/chronology are considered.

## Promotion gate — formal verdict

| gate | C03 (best candidate) |
|---|---|
| (a) improves >=2 of {Sharpe,Sortino,Calmar,CDaR95} vs NQ control | PASS (Calmar, CDaR95 only) |
| (b) top-10-day / top-1%-trade retention >= 90% | PASS in isolation, but net tail dollars negative (see above) |
| (c) same sequence priced on genuine MNQ does not diverge materially | **FAIL** (Sharpe/Sortino/Calmar all worse on MNQ) |
| (d) survives year-by-year / LOYO chronology | **FAIL** (2023 -51.8%, not uniform) |
| (e) survives 2-tick cost stress | not run (already failed (c) and (d)) |
| (f) independent adversarial audit | not run (already failed (c) and (d)) |

**Missing gates (c) and (d) is sufficient for NOT PROMOTED per spec.yaml's own binding rule**
("Missing ANY gate => NOT PROMOTED... no partial credit"). No other candidate reaches gate (a)
at all.

## Disposition

**R1: CONFIRMED-NOT-BENEFICIAL.** The diagnostic motivation (P0's giveback-ratio finding) was
real and correctly identified a genuine loser/winner discriminator — but a mechanical overlay
that acts on it, across a bounded, honestly-preregistered 12-candidate grid plus a 3-setting
ATR-stop benchmark, does not produce a promotable improvement: it trims tail-shape metrics
(Calmar, CDaR) at a larger absolute dollar cost to the right tail than it saves on the left tail,
fails the shared NQ/MNQ core-consistency check, and is not chronologically stable. Per directive
sec38(C), this is treated as a real research result (a tempting, well-motivated axis closed with
high confidence), not a wasted cycle. No trading rule changes. Incumbent (`SolarWaveOneContractNQ_v5`
/ `SolarWaveOneContractMNQ_v5` / `SolarWaveSMMaster_v4`) remains unchanged and is NOT to be
re-tuned on this same population without new information (directive sec20).

**Note for any future reopening**: the giveback overlay's OWN weakness is concentrated in
removing dollars from winners, not in failing to find losers (the loser-side recovery, +4.6% of
the bottom-decile bucket, is real and directionally consistent with P0). A future mechanism that
could distinguish "signal decayed AND price stalled" (true reversal risk) from "signal decayed
but price is merely consolidating before resuming" (a temporary pause inside a still-valid trend
— exactly what the top-decile winners' own p90-p99 giveback of 34-54%, per P0, describes) would
need a materially different, better-targeted state variable than giveback_ratio alone. That is a
new hypothesis, not a parameter retune of this grid, and would require its own preregistration.
