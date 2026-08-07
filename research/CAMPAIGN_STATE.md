# Campaign State

_Last updated: 2026-08-07 (Solar Wave RK **fully** recovered; Wave 1c complete; ensemble promoted
over parameter selection; four hypotheses falsified)_

## 1. Vendor independence — COMPLETE (RE01 + RE02)

The RenkoKings Solar Wave RK indicator is **fully reverse-engineered**. Every published series,
every signal symbol, exact on every bar:

**1,436,860 bars · 9 parameter configurations · zero mismatches on any series.**
Type 2 specifically: 45,825 events, 0 false positives, 0 false negatives.

Reference implementation `solar_wave_full()` in `src/analytics/solarwave.py`; derivation in
`research/03_reverse_engineering/{SOLARWAVE_MATH.md, TYPE2_RECOVERY_SPEC.md,
TYPE2_RECOVERY_REPORT.md}`. Method: behavioural observation of the indicator's own published
output. **No decryption, unpacking, patching or memory dumping was performed; the vendor assembly
was not modified or redistributed** (constitution: never bypass vendor protections).

Recovered model in one place:
- **Core:** one state variable `a` = running extreme of the CLOSE since trend start.
  `TrailingStop = a ∓ S`, `TrendVector = a ∓ V`. Flip on a **strict** break of the stop.
- **Wave layer:** pure bar counter. `SlowdownScan` bars of no new extreme ⇒ weak; a new extreme
  while weak increments the wave and emits Type 3; `WeakWeakSplit` is anti-chatter re-arm.
- **Type 2:** an edge-triggered latch on an **intrabar High/Low** excursion beyond `TrendVector`,
  spaced by `PullbackSplit`, re-armed by a full-bar clear, by a flip, and — the only coupling to
  the wave layer — by a Type-3 event. `PullbackEarly` switches the basis from the excursion
  (High/Low) to close-confirmed return. Touching `TrendVector` is not a cross (sticky latch).
- **New:** `TrendVector` carries a second ladder-rung clamp that is **provably inert when
  `V ≤ S/2`** — exactly where the vendor's own presets sit (90/179 = 0.503, 60/120 = 0.500).
  `V > S/2` is a characterised ambiguity, excluded from all experiments.

`SolarWaveOpenV1` (no vendor reference) reproduces the frozen canonical baseline exactly
(`runs/RE01_open_parity/`). `SolarWaveOpenX2` adds a fill-level ledger; `SolarWaveOpenV3` adds the
three new axes. All gate-checked against the baseline to the penny before use.

## 2. Current phase

**WAVE 2 — open-model axes.** Historical research only (no live-sim / paper / forward monitoring
ever, unless explicitly requested). Research universe = all data 2022-01 → 2026-07-31; no clean
OOS remains and none is claimed.

## 3. The central result: the deliverable is a region, not a parameter

CSCV over 16 chronological blocks (12,870 splits, 1,318 trading days): **PBO 0.56–0.66** with a
**negative** in-sample→out-of-sample slope (−1.03, r = −0.79). Walk-forward argmax selection earns
**$16,131 on 1-minute where the median config earns $121,373**. StopMultiplier is **not
selectable** from in-sample performance.

What works instead — hold the whole connected plateau at equal risk:

| | 3m ensemble (8 cells) | best single (unknowable ex ante) | mean single |
|---|---|---|---|
| net, exposure-matched | **$216,922** | $249,934 | $180,479 |
| daily Sharpe | **+0.803** | +0.947 | +0.668 |
| max drawdown | **−$53,689** | −$71,395 | — |
| positive in all 5 years | **yes** | — | 3 of 8 members |

The ensemble beats 88 % of its own members on Sharpe, is positive every year when only 3 of 8
members are, and is not an exposure artifact (gross exposure ratio 1.000; members agree on
direction only 53.6 % of days). DSR 0.83 at n_trials = 170: **the family's edge survives
multiple-testing deflation even though the choice within it does not.** Promoted to reference
architecture **R4**.

## 4. Frozen baseline (unchanged)
SolarWaveRKReplicaV0 · T1 · 90/179/5/10/true/10 · 1m Last · NQU6 · Lifetime · canonical window.
slip0 $146,440.60 / 2,915 trades / DD −$22,066.60 / PF 1.132213. Reproduced exactly by
`SolarWaveOpenV1`, `SolarWaveOpenX2` and `SolarWaveOpenV3` at their default settings — that
three-way gate is run before any new axis result is read.

## 5. Completed

- **PARITY, SW00, SW01, SW01b, SW01c, SW02a** — as before (see git history).
- **RE01** — open reconstruction reproduces the vendor baseline, all deltas zero.
- **RE02** — Type 2 and the full indicator recovered exactly (§1).
- **Wave 1 / 1b** — Type-1 core collapses to `f(StopMultiplier, timeframe, exit)`; profitable
  plateau 1m [170,280], 3m [180,260]; 3-minute is the stronger timeframe.
- **Wave 1c** — 80 configs, real slip 0/1/2, full history; PBO/CSCV, DSR/PSR, walk-forward,
  block bootstrap (`research/02_solar_refinements/WAVE1C_report.md`).
- **DR-01…DR-07** — seven deep-research packets, 32 falsifiable hypotheses
  (`research/deep_research/`).
- **DC01/DC02** — directional-change decomposition (`research/deep_research/DC01_DC02_RESULTS.md`).

## 6. Falsified this wave (each with evidence, none deleted)

| claim | verdict | evidence |
|---|---|---|
| 16:30 timed exit dominates the session close | **FALSE** on full history | wins 4/28 matched pairs, median −$12,476. SW02a's collapse test still stands; only its bonus finding is withdrawn |
| the 46 % untaken Type-1 signals are an opportunity set (SW03 premise) | **FALSE** | taking them costs **−$9.04/marginal trade** over 54,151 trades |
| H-011: stop orders at the ladder level recover the 89 % friction | **FALSE** | negative in 10/10 cells; close-based state and intrabar fills desynchronise |
| H-007 / DR03-H1: splitting exit from reversal distance helps | **FALSE** | monotone degradation as the split widens; ratio 1.00 (no split) is best at every point |
| DR06-H5: iid shuffling understates tail risk | **FALSE** | block-vs-iid 5th-percentile drawdown ratio 0.987 |
| SW05 original chop veto | **INVERTED** (earlier wave) | would delete 74 % of profit |

## 7. Confirmed this wave

- **DR06-H4** — neighbourhood-smoothed selection dominates argmax on both timeframes.
- **DC01** — the overshoot ratio `r = E[ω]/δ` exceeds the martingale null at every threshold
  (t = 31 → 2.1). The edge is real but is a **~3 % deviation of r from 1.0**, i.e. thin by
  construction.
- **DC01 cost structure** — the close-basis crossing excess is ~23.5 ticks = **$117.57 per
  segment = 89 % of all friction**, four times commission plus 1-tick slippage combined.
- **DC02** — volatility normalisation halves the across-year drift of `r` (0.116 → 0.058);
  price normalisation is intermediate (0.085). Supports H-006's functional form.

## 8. Open / in flight

1. **H-006 adaptive threshold** — the adaptive ensemble shows Sharpe 1.010 vs the fixed
   ensemble's 0.803, DD −$39,126 vs −$53,689, positive every year. **Not yet accepted:** the
   winning cells trade far less (893–1,680 vs ~6,000), so the gain is confounded with simply using
   a wider threshold. A fixed-threshold control out to SM 880 is running to separate the two.
2. **H-008 anchor definition** — High/Low anchor sweep running; first cells are worse than the
   close anchor at matched SM, but trade more, so matched-turnover comparison is required.
3. **Type-0 attribution + controlled architectures C0–C6** — now unblocked by the complete model.
4. **Complementary families** (failed persistence, value reacceptance), ES portability, portfolio.

## 9. Config accounting

Wave 1 + 1b ≈ 90 · Wave 1c 80 · H-011 30 · open axes ≈ 55 → **≈ 255** campaign-to-date.
DSR in the Wave-1c report used n_trials = 170 (the count at that time); it must be re-run at the
current total before any promotion decision.

## 10. Unresolved integrity issues

None. Benign notes: the exporter emits 737,707 of 737,708 bars (boundary bar); the vendor
publishes `Signal_Wave = 0` before the first flip and treats bar 0 as a seed rather than a
no-progress bar — both now reproduced exactly.

## 11. Next highest-value action

Finish the H-006 confound control (fixed thresholds at matched turnover). If adaptive still wins
at matched turnover *and* at matched exposure, it is the first genuine improvement over the vendor
design; if not, the correct conclusion is "wider is better and normalisation is cosmetic", which
is equally publishable inside the campaign and much cheaper to run.
