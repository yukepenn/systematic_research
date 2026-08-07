# C01 T0-3 — CUSUM drift-allowance diagnostic (DR03-H2 stage 1)

_Executed 2026-08-07 against the frozen constants in `C01_WAVE_SPEC.md` §2 T0-3. Tier-0
instrumentation: 0 R1 trials consumed. All constants were fixed before any result was read;
nothing was adjusted afterward._

## Verdict: **REJECT — DR03-H2 CLOSES. Tier-1 k-sweep NOT unlocked.**

The tercile P&L profile is not "monotone and significant under session-block bootstrap".
Point estimates lean toward slow retraces earning more (would imply k<0), but the effect is
far from significance (primary p = 0.35), the long side is not monotone (V-shaped), and the
rank statistic points weakly the **opposite** way. Flips are impulse-dominated; the retrace
speed at threshold-crossing carries no exploitable timing information.

## 1. Reproduction and validation (gate: ≥99% flip↔entry match)

The V3 DC state machine (AnchorMode 0 close-extreme anchor, strict-inequality flip at
anchor ∓ S, S = VolMult·σ sampled once at trend birth, σ = trailing mean |Δclose| over
min(t, 460) bars — NaN below 30 diffs with fallback S = 44.75 pts, clamp [40, 1200] ticks,
StartUp = false) was re-implemented in Python from `runs/AUDIT03_BARS/nq_3m_2022_2026.csv`
(540,232 bars) following `src/ninjascript/SolarWaveOpenV3.cs` semantics exactly, including
the detail that σ is updated *before* the ladder on each bar, so the flip-bar diff enters
the resampled S.

Match rule: a reproduced flip at bar f (direction = new trend) predicts an entry fill at the
close-timestamp of bar f+1. Entries only occur on flips reached while flat (V3 exits on the
flip bar and re-enters at the *next* flip; session-close exits break the parity), so entries
⊆ flips, as expected.

| member | entries | matched | rate | flips reproduced |
|---|---|---|---|---|
| vm6 | 8,492 | 8,492 | 100.000% | 16,386 |
| vm8 | 5,538 | 5,538 | 100.000% | 10,512 |
| vm10 | 4,036 | 4,036 | 100.000% | 7,512 |
| vm12 | 3,083 | 3,083 | 100.000% | 5,616 |
| vm14 | 2,459 | 2,458 | 99.959% | 4,345 |
| vm16 | 2,033 | 2,033 | 100.000% | 3,489 |
| vm18 | 1,680 | 1,680 | 100.000% | 2,823 |
| vm20 | 1,469 | 1,469 | 100.000% | 2,397 |
| vm22 | 1,299 | 1,299 | 100.000% | 2,055 |
| vm24 | 1,160 | 1,160 | 100.000% | 1,801 |
| vm26 | 1,054 | 1,054 | 100.000% | 1,593 |
| vm28 | 952 | 952 | 100.000% | 1,405 |
| vm30 | 893 | 893 | 100.000% | 1,261 |

**Overall: 34,147 / 34,148 = 99.997% ≥ 99% — validation PASSED.** The single unmatched
entry (vm14, 2026-07-31 17:00:00) is a data-boundary artifact, not a state-machine error:
the bar export ends at the 16:57 bar of the final session while NT8 carried one more 17:00
bar; the reproduction actually detects that final flip too, but has no next bar to map a
fill to. (Same artifact excludes 4 of 34,147 trades from MAE, exits timestamped 17:00:00 on
2026-07-31.) Fill *times* match perfectly; fill *prices* match at ~97.5% with the residual
fully explained by NT8 clamping the 1-tick slip to the fill bar's high/low. Trade P&L is
taken from the ledgers, so price clamping does not affect any number below.

## 2. Definitions (frozen)

At each flip: **B** = flip bar − last bar the ending trend's running close-extreme strictly
updated (equal-close bars do not reset, matching `barsSinceExtreme`; flip/birth bar counts
as a reset). **S** = the ending trend's threshold (sampled at its birth). **σ_bar** = the
trailing-460 mean |Δclose| at the flip bar. **speed = S / B / σ_bar** (σ units per bar).
Next-trade = the ledger round trip opened by that flip's entry fill (net of $4.36 RT
commission, 1-tick slip in prices; session-close truncation kept as-is — executable
reality). MAE from 3-min bar extremes over the held window (entry fill bar through the bar
before a flip-exit fill / through the session-close bar), floored at 0.

Terciles: pooled across all 13 members, cutoffs per side (long: 0.367/1.106, short:
0.350/1.084 σ/bar). Analysis set = the 34,143 matched trades with complete MAE.

## 3. Results

### Per tercile per side (pooled across members) — full table in `c01_t03_flip_speed_terciles.csv`

| side | tercile | n | med B | mean net $ | hit rate | mean MAE $ |
|---|---|---|---|---|---|---|
| long | T1 slow | 5,024 | 75 | **+153.34** | 0.400 | 1,251 |
| long | T2 mid | 5,023 | 15 | +73.96 | 0.410 | 1,091 |
| long | T3 fast | 5,024 | 4 | **+154.26** | 0.428 | 966 |
| short | T1 slow | 6,357 | 91 | **+96.14** | 0.401 | 1,180 |
| short | T2 mid | 6,357 | 16 | +36.02 | 0.381 | 982 |
| short | T3 fast | 6,358 | 4 | **−29.70** | 0.367 | 945 |

### Frozen gate test — session-block bootstrap (1000 draws, block = 5 sessions, seed 20260807)

| profile | T1 slow | T2 | T3 fast | T3−T1 | 95% CI | p | monotone? |
|---|---|---|---|---|---|---|---|
| **PRIMARY: combined ranks** | +121.39 | +52.77 | +51.50 | **−69.89** | [−222.6, +72.3] | **0.35** | yes (point est.); only 38.8% of draws |
| long side | +153.34 | +73.96 | +154.26 | +0.92 | [−177.8, +206.8] | 0.92 | **NO (V-shape)** |
| short side | +96.14 | +36.02 | −29.70 | −125.84 | [−347.2, +58.6] | 0.21 | yes |
| robustness: within-member terciles | +99.12 | +81.26 | +45.29 | −53.84 | [−196.5, +87.4] | 0.45 | yes |
| robustness: R-units (net/S), within-member | +0.0423 | +0.0420 | +0.0189 | −0.0235 | [−0.0922, +0.0457] | 0.48 | yes |

Rank check: Spearman(speed, net) = **+0.017** pooled (long **+0.033**, short +0.005) — the
*rank* association is weakly positive while the tercile *means* lean negative. The mean
profile is a right-tail composition effect (median net is negative in every cell; hit rates
even *increase* with speed on longs), not a coherent monotone relation.

### Per-year sign stability (combined ranks, T3−T1 $/trade)

| year | T1 slow | T2 | T3 fast | T3−T1 |
|---|---|---|---|---|
| 2022 | +136.31 | +3.24 | +66.81 | −69.50 |
| 2023 | +82.15 | +0.98 | −13.85 | −96.00 |
| 2024 | +87.49 | +59.40 | +10.32 | −77.16 |
| 2025 | +162.43 | +0.43 | +160.17 | −2.26 |
| 2026 | +145.04 | +268.95 | +36.11 | −108.93 |

Sign is negative 5/5 years (suggestive of the slow-retraces-win lean) but per-side yearly
signs are unstable (long 2022: +150.49; short 2025: +52.21), and no year's effect
approaches its own noise band. T2 < T1 in every year — the middle tercile is the worst or
near-worst, i.e., the profile is U/J-shaped as often as monotone.

### MAE

MAE falls monotonically with speed on both sides (slow ≈ $1,180–1,251 vs fast ≈ $945–966),
but this is mechanical: slow-retrace flips open longer trades (mean 100–123 bars held vs
31–42) with proportionally deeper excursions. The slow tercile's P&L lean, such as it is,
is bought with ~29% more adverse excursion — no free lunch even in the point estimates.

## 4. Interpretation and answer to the directional question

**Direction:** SLOW retraces (small speed) WIN more in tercile means — the k<0 side of the
DR03-H2 fork (crediting slow drifts / flipping earlier on slow bleeds), consistent with the
literature default for large-h regimes. **But the gate requires monotone AND significant,
and the data delivers neither robustly:** p = 0.35 primary, long side V-shaped, rank
statistic sign-flipped, within-member and scale-free robustness views equally flat.
Per the frozen reject branch: **k is irrelevant — flips are impulse-dominated** (median
fast-tercile B = 4 bars; even the "slow" tercile's threshold information is swamped by
what happens after entry). DR03-H2 closes. No Tier-1 trials consumed; none unlocked.

## 5. Files

- This report: `research/04_complementary_family/c01_t03_cusum_drift_diagnostic.md`
- Tercile table: `research/04_complementary_family/c01_t03_flip_speed_terciles.csv`
- Inputs: `runs/AUDIT02_V3_SWEEP_B/ledgers/b2v3__*.csv` (13 members),
  `runs/AUDIT03_BARS/nq_3m_2022_2026.csv`, `src/ninjascript/SolarWaveOpenV3.cs` (semantics),
  `src/analytics/solarwave.py` (reference recurrence)
- Analysis scripts + per-trade parquet: session scratchpad (`t03_full.py`,
  `t03_trades.parquet`, `t03_results.json`) — derivable end-to-end from the committed
  inputs above with seed 20260807.
