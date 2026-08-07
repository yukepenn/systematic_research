# Solar Wave RK — recovered mathematics

_2026-08-07 · Reference implementation: `src/analytics/solarwave.py` · Ground truth: `research/01_diagnostics/sw01_bar_ledger.csv` (737,707 NQ 1-min bars, 2023-01-02 → 2025-01-31)_

## 0. Method and provenance (read this first)

Two routes exist to a vendor algorithm. Only one was used.

**Not used — static code recovery.** `SolarWaveRK/RenkoKings_SolarWaveRK_NT8.dll` (4.6 MB, sha256 `0F83396462733542E643BD9680D531B64C1E9D042B8327428641C828363B30B5`) is protected by **Agile.NET / CliSecure 6.9.1.8** (declared in `Info.xml`). Class structure, fields, properties and method signatures are in cleartext metadata and were read normally with the ILSpy decompiler library. Every *method body*, however, is a 1-byte `ret` stub: of 3,008 `MethodDef` rows all carry real RVAs, but each points at a fat header with `CodeSize = 1` containing only opcode `0x2A`. The real IL sits in two GUID-named encrypted manifest resources (`ca22c3b6-…`, `6779a452-…`) and is installed at runtime by `<AgileDotNetRT>.Initialize()` through a JIT hook. Recovering it means defeating the protection — which the campaign constitution forbids ("never bypass vendor protections") and which is a licensing question, not a technical one. **No decryption, patching, unpacking or memory dumping was performed, and the vendor assembly was not modified.**

**Used — behavioural reverse engineering.** The indicator publishes five `Series<double>` (`TrendVector`, `TrailingStop`, `Signal_Trend`, `Signal_Trade`, `Signal_Wave`). `SolarWaveRKLedgerV1` already exported all five for every bar of the canonical window. Treating those 737,707 rows as ground truth, the generating recurrence was recovered by hypothesis-and-exact-test. This is observation of licensed software's own output — legally unencumbered, and it yields something source recovery does not: an *open* model we may extend past the vendor's six parameters.

**Result: the core is recovered exactly, not approximately.**

| Series | Agreement with vendor | Notes |
|---|---|---|
| `TrailingStop` | **100.000000 %** | tick-for-tick, all 737,707 bars |
| `TrendVector` | **100.000000 %** | tick-for-tick |
| `Signal_Trend` | 99.999864 % | 1 bar — the ledger's uninitialised first bar |
| `Signal_Trade`, Type 1 | **100.000000 %** | all 5,405 trend starts, exact bars |
| `Signal_Trade`, Type 3 | 100 % recall | 200 bars where a Type-2 overwrites the plot slot |
| `Signal_Wave` | 99.970585 % | same 200 collisions |

## 1. The whole core, in five lines

Let `c_t` be the **close** (nothing else is used — no high, low, open, volume or time), `κ` the tick size, and

```
S = OffsetMultiplierStop  × κ        # reversal distance   (179 ticks = 44.75 NQ pts)
V = OffsetMultiplierTrend × κ        # early-warning offset ( 90 ticks = 22.50 NQ pts)
```

State: a direction `u_t ∈ {up, down}` and one price `a_t`, the **running extreme of the close since the current trend began**.

```
if u = up:    c_t ≥ a       →  a ← c_t                        (extend)
              c_t < a − S   →  u ← down, a ← c_t              (FLIP)
if u = down:  c_t ≤ a       →  a ← c_t                        (extend)
              c_t > a + S   →  u ← up,   a ← c_t              (FLIP)

TrailingStop_t = a ∓ S       (− in an uptrend, + in a downtrend)
TrendVector_t  = a ∓ V
```

That is the entire price engine. Consequences worth stating explicitly:

- **One state variable.** `TrailingStop` and `TrendVector` are two parallel lines rigidly bolted to the same anchor. Their separation is constant forever: `TrailingStop − TrendVector = ±(179−90) = ±89` ticks, confirmed on **every one of the 737,707 bars**.
- **The flip test is strict.** Touching the stop exactly does not reverse; the close must trade *through* it. Verified against 4,682 bars where the non-strict rule diverges — this single `<` vs `≤` is the difference between 99.37 % and 100 %.
- **No look-ahead and no repainting.** Within a trend `a_t` is monotone, so `TrailingStop` is monotone; every value is a function of closes up to and including `t`. This closes a standing audit question for the campaign.
- **No averaging of any kind.** There is no moving average, no ATR, no standard deviation, no smoothing constant and no lookback window in the core. The only "period" in the whole model is a bar counter (§2).

## 2. The Solar Wave layer — a bar counter, not a price model

`Signal_Trend` ∈ {±1, ±2} (sign = direction, 2 = strong, 1 = weak) and `Signal_Wave` ∈ [−29, +29] come from a small automaton driven purely by *how many bars pass without a new extreme*:

```
on FLIP:            weak ← false; wave ← 1; rearm ← t + WeakWeakSplit; emit Type 1
on NEW EXTREME:     if weak:  wave ← wave + 1; weak ← false;
                              rearm ← t + WeakWeakSplit; emit Type 3
otherwise:          if (bars since last extreme ≥ SlowdownScan) and t ≥ rearm:
                              weak ← true; rearm ← t + WeakWeakSplit
```

- **`SlowdownScan` (5)** = bars of no progress that declare the trend *slowing*.
- **`WeakWeakSplit` (10)** = minimum bars between consecutive weak declarations — pure anti-chatter hysteresis. Empirically the strong→weak transition fires at 5 bars in 7,431 of 14,664 cases and is pushed to 6–10 bars in the rest by exactly this re-arm; the observed support is `[5, 10]` with **nothing outside it**, which is what pinned the rule.
- **`Signal_Wave` = the number of impulse legs in the current trend.** It changes on flips and new extremes and *nowhere else* (verified: 15,925 changes = 5,405 flips + 10,520 extensions, zero others). A "wave" is therefore: run → pause ≥5 bars → resume. This is the eponymous Solar *Wave*: an Elliott-flavoured leg count defined without any price geometry at all.
- **Signal priority:** when a pullback and a strengthening land on the same bar, `Signal_Trade` shows the pullback. 10,524 modelled Type-3 events − 200 collisions = 10,324 observed, exactly.

`Signal_Trade` = ±1 trend start ("Up"/"Down"), ±2 pullback ("Pb"), ±3 strengthening ("Str"). **Type 2 is the one piece not yet exact** — its trigger distribution (median retrace 89 ticks, i.e. one tick shy of `OffsetMultiplierTrend`) strongly implies it is tested against the bar's **high/low** rather than the close, which the close-only ledger cannot resolve. `PullbackEarly` and `PullbackSplit` feed only this branch. Closing it needs one re-run of the exporter with H/L columns.

## 3. Why our sweeps found what they found

The reverse engineering *explains* Wave-1's empirical results rather than merely agreeing with them:

- **`TrendMultiplier` was bit-identical inert for Type 1** — because `TrendVector` appears nowhere in the flip rule. It is a cosmetic line that feeds only the Type-2/3 branch. This was measured first and is now derived.
- **`SlowdownScan` / `WeakWeakSplit` were inert for Type 1** — they drive only `Signal_Trend`'s strong/weak cosmetic and the Type-3 branch.
- **The Type-1 core really is `f(StopMultiplier, timeframe, exit)` and nothing else.** That is not an empirical accident; it is the structure of the algorithm.
- **Path chaos (SM 179 → \$259k vs SM 180 → \$171k) is intrinsic.** The map is a discontinuous threshold recursion: shifting `S` by one tick re-times a flip, which relocates the anchor, which cascades through every subsequent trend. Neighbourhood medians are the only honest read — this justifies the leaderboard's ranking rule.

## 4. What the indicator actually is, and what edge it bets on

Stripped of branding, Solar Wave RK is a **fixed-threshold directional-change filter on closing prices**: mark a new extreme; when price retraces `S` from it, declare a reversal and restart. This is the same object as a point-and-figure reversal, a Renko brick chain, a ZigZag with a fixed absolute threshold, and the "directional change" event framework of the econophysics literature (Guillaume et al. 1997; Glattfelder et al. 2011). The vendor's own chart templates ship a **custom bar type (`BarsPeriodType = 12345`, `ReversalType = Tick`)** — the tool was designed for Renko charts, where fixed-tick geometry is the native unit. We are applying it to time bars, which is a legitimate but off-label use.

The single economic bet is therefore sharp and falsifiable: **after NQ retraces 44.75 points on a closing basis from a swing extreme, the next move continues in the new direction more often, or further, than chance.** Everything else — waves, pullbacks, strengthening, the colour scheme — is presentation. Our measured profile fits a pure trend-persistence payoff: ~37–38 % win rate with PF ≈ 1.06–1.08, i.e. many small losses paid for by few large wins. The SW01b null test already showed entry timing beats random entries at p = 0.0323, so the persistence is real but thin.

## 5. The design flaw this exposes — and the experiment it implies

`OffsetMultiplierStop` is **a constant number of ticks**. It does not scale with price level or volatility. So the strategy's aggressiveness is not a constant of the design; it drifts with the market:

| Year | median NQ close | 44.75 pts as % of price | 44.75 pts in per-bar vol units |
|---|---|---|---|
| 2023 | 17,558 | 0.255 % | 17.8 |
| 2024 | 21,138 | 0.212 % | 14.9 |
| 2025 | 22,881 | 0.196 % | 10.4 |

**The same parameter has become 41 % less selective in two years** purely because NQ doubled in price and its per-bar range grew. This is a mechanism — not a story — for the per-year thinning already in the record (per-trade economics falling and 2026 sitting near breakeven at one tick of slippage). It also explains why the profitable `StopMultiplier` plateau sits at 180–260 rather than the vendor's 179: the market has grown into the higher end of that band.

**Implied experiment (Wave 2, H-006):** replace the constant `S` with `S_t = k · σ_t`, σ causal and frozen at each trend's birth so the stop stays monotone. `solar_wave_adaptive()` in `src/analytics/solarwave.py` implements it. A first close-fill screen on ledger data is **not a free win** — at matched trade counts fixed and adaptive trade blows, both drowning in the same path noise — but the adaptive run at k = 14 (≈ matched trade count, 5,719 vs 5,404) distributed P&L far more evenly across years (\$85k / \$46k / \$29k) than fixed 179 (\$26k / \$116k / \$24k, i.e. 70 % of everything in one year). Even year-balance at equal aggregate is exactly the signature normalisation should produce. This deserves a proper dense scan through the NT8 pipeline, not a Python approximation.

## 6. What this unlocks

We are no longer restricted to the vendor's six parameters, four of which are inert for our core. The open model exposes the knobs that were never exposed:

1. **`S` need not be constant** — volatility- or price-normalised (above), or regime-switched.
2. **The anchor need not be the close extreme** — high/low extremes, or a quantile, change the noise sensitivity.
3. **Stop and reversal need not be the same number.** In the vendor design one distance does both jobs: it is simultaneously the exit and the entry trigger for the opposite side. Splitting them (reverse at `S_r`, exit at `S_x ≠ S_r`) is a genuinely new degree of freedom and directly addresses the "46 % of signals untaken" opportunity set.
4. **The wave counter is free information we have never used.** `Signal_Wave` = leg number is available on the vendor series too, but only now is it *interpretable*: leg 1 of a trend is a different animal from leg 8. Conditioning position size or entry eligibility on wave index is a Wave-2 sleeve that costs nothing to test.

## 7. Reproduce

```
python src/analytics/solarwave.py research/01_diagnostics/sw01_bar_ledger.csv
```

Prints the validation table in §0. Deterministic, no network, no NT8 required.
