# Research Thesis — Empirical Update

_Living reconciliation document, opened 2026-08-07. The original `research/Research_Thesis.txt`
is a historical research artifact and is **not** edited; where this document and the thesis
disagree, this document is current and says so explicitly._

Sections are separated by evidence class on purpose. A claim's section tells you what would be
needed to overturn it.

---

## 1. Documented vendor mechanics (what the product says about itself)

- `RenkoKings_SolarWaveRK(ISeries<double> input, double offsetMultiplierTrend,
  double offsetMultiplierStop, int slowdownScan, int weakWeakSplit, bool pullbackEarly,
  int pullbackSplit)` — the public generated NinjaScript wrapper (from the shipped `.cs`).
- Published outputs: `TrendVector` (Values[0]), `TrailingStop` (Values[1]), `Signal_Trend`
  (Values[2]), `Signal_Trade` (Values[3]), `Signal_Wave` (Values[4]).
- Shipped chart templates use a **custom bar type** (`BarsPeriodTypeSerialize = 12345`,
  `ReversalType = Tick`) — i.e. the tool was designed for Renko charts. Our use on time bars is
  legitimate but off-label.
- Shipped template presets: MajorTrend `OMT=60 / OMS=120`; default `90 / 179`. **Both sit at
  V/S ≈ 0.50.** §2 shows this is exactly the boundary that keeps a second internal clamp inert —
  the product is designed to live there.
- Binary is protected with **Agile.NET / CliSecure 6.9.1.8** (declared in `Info.xml`); all 3,008
  `MethodDef` bodies are 1-byte `ret` stubs with the real IL in encrypted GUID-named resources.
  Cleartext metadata (types, fields, signatures) is normally readable and was read normally.

## 2. Exact recovered mathematics (behavioural; reproducible to the tick)

Recovered by hypothesis-and-exact-test against the indicator's own published per-bar output.
No decryption, unpacking, patching, memory dumping or other circumvention was performed; the
vendor assembly was not modified or redistributed. **This is behavioural mathematics, not vendor
source code.** Full derivation: `03_reverse_engineering/SOLARWAVE_MATH.md`; Type-2 work in
`TYPE2_RECOVERY_SPEC.md` / `TYPE2_RECOVERY_REPORT.md`; reference implementation
`src/analytics/solarwave.py`.

**Price core** — one state variable. With `S = OffsetMultiplierStop × tick`,
`V = OffsetMultiplierTrend × tick`, and `a` = running extreme of the **close** since the trend began:

```
uptrend  : c ≥ a → a ← c            |  c < a − S → flip down, a ← c   (Type 1)
downtrend: c ≤ a → a ← c            |  c > a + S → flip up,   a ← c   (Type 1)
TrailingStop = a ∓ S     TrendVector = a ∓ V
```

The flip test is **strict** — touching the stop does not reverse. Verified: `TrailingStop` and
`TrendVector` **100.000000 %** tick-exact on 737,707 bars; Type-1 event times **100.000000 %**
(5,405/5,405). No moving average, ATR, standard deviation, smoothing constant or lookback window
appears anywhere in the core. No look-ahead, no repainting (`a` is monotone within a trend).

**Wave/strength layer** — a pure bar counter. On flip: `weak=false, wave=1, rearm=t+WWS`. On a new
extreme while weak: `wave++, weak=false, rearm=t+WWS`, emit Type 3. Otherwise, once
`bars_without_new_extreme ≥ SlowdownScan` and `t ≥ rearm`: `weak=true, rearm=t+WWS`.
`Signal_Trend = sign×(weak?1:2)`; `Signal_Wave = sign×wave`. Signal-plot priority: **1 > 2 > 3**.

**Type 2 (pullback)** — *partially* recovered, currently 95.3 % exact; see §6. Established
exactly: it is a with-trend event (100 %), triggered by an **intrabar** High/Low excursion beyond
`TrendVector` (100 % of Type-2 bars; only 70 % have the close beyond), edge-triggered by a
`hasCrossed` latch that re-arms on a bar entirely clear of `TrendVector`, spaced by
`PullbackSplit` bars, with a new extreme resetting the latch *after* the trigger check.
`PullbackEarly=false` moves the firing point to close confirmation rather than filtering.

**`TrendVector` has a second ladder rung (new, 2026-08-07).** The single-rung formula is exact
whenever `V ≤ S/2` but only 69.8 % exact at `TM=135` (`V/S = 0.754`). The line is additionally
bounded by the previous ladder rung: uptrend `TV = max(a − V, r₁ + V)`. Because the flip is
strict, `a ≥ r₁ + S + 1 tick`, so the clamp **provably cannot bind when `V ≤ S/2`** — which is
where the vendor's own presets sit. All campaign work is defined on that design regime; `V > S/2`
is documented as a bounded ambiguity and excluded from every experiment.

## 3. Exact local-source behaviour (our own code, not the vendor's)

- `SolarWaveRKReplicaV0` — the frozen baseline wrapper. On a flip bar it exits and `return`s
  **before** the entry block, so the flip-bar entry signal is discarded. This is the mechanical
  cause of "46 % of Type-1 signals untaken" (2,915 trades from 5,405 signals). It is a property
  of *our wrapper*, not of the indicator.
- `SolarWaveOpenV1` — open reconstruction, **zero vendor references**, identical entry/exit
  policy. Reproduces the frozen canonical baseline with all deltas exactly zero
  (`runs/RE01_open_parity/`): net $146,440.60 · 2,915 trades · DD −$22,066.60 · PF 1.1322134 ·
  commission $12,709.40. Long 1,386 / $103,162.04 / PF 1.1994; short 1,529 / $43,278.56 / PF 1.0733.
- `SolarWaveOpenX2` — same engine plus a parameter-named execution ledger, so one NT8
  optimization sweep yields one fill-level CSV per cell. Verified against the engine's own
  summary to the penny (SM 230, 3m, slip-1: 5,443 trades, $249,933.52, PF 1.0797954) and against
  the frozen baseline through `src/analytics/execledger.py`.
- **Slippage does not change the trade sequence.** Slip-0 and slip-1 runs produce byte-identical
  entry/exit timestamps (signals are close-based); the cost is $9.5352/trade on NQ, distributed
  {0, 5, 10} per trade rather than a flat $10 — session-close and some boundary fills take none.
  This retro-justifies the campaign's $9.53 analytic overlay and means cost ladders can be
  produced without re-deriving paths.

## 4. Empirical findings that stand

- **The Type-1 core is 1-dimensional.** `TrendMultiplier`, `SlowdownScan`, `WeakWeakSplit`,
  `PullbackSplit` are bit-identical inert for Type 1. Measured first (Wave 1, D1), now *derived*:
  none of them appears in the flip rule. The searchable core is
  `f(StopMultiplier, timeframe, exit policy)`.
- **Single-point results are meaningless.** SM 179 → $259,102 but SM 180 → $170,997 on identical
  data: ±$40–90k of path chaos from a one-tick change. This is intrinsic to a discontinuous
  threshold recursion, not noise in the data. All ranking uses connected regions and
  neighbourhood medians.
- **Wider stops dominate after costs.** SM ≤ 150 on 1m is negative at 1 tick; the profitable band
  is ≈ [170, 280] on 1m and [180, 260] on 3m (16/16 dense points positive at slip-1).
- **No session-close fill artifact.** A 16:58 timed market exit retains 100.0 % of baseline net at
  slip-0 and slip-1 (SW02a). Separately, exiting ≈16:31 *dominates* the close (102.4 % net, lower
  DD) — the last 30 minutes of holding are negative.
- **Entry timing beats a matched random-entry null** at p = 0.0323 (SW01b); the same machinery
  with random entries is zero-mean, so the machinery alone does not manufacture the result.
- **Per-year thinning is real and has a mechanism.** The offset is a constant tick count, so the
  same 44.75 points fell from 0.255 % of price / 17.8 per-bar-vol units in 2023 to 0.196 % / 10.4
  in 2025 — a 41 % loss of effective selectivity as NQ grew. 2026 sits near breakeven at 1 tick.

## 5. Disproven / inverted hypotheses

- **Chop veto (original SW05): INVERTED.** High flip-count buckets are the *best* (PF 1.303), not
  the worst. Applying the original veto would have deleted 74 % of profit. Redesigned around
  low path-efficiency instead.
- **"Unconditional Type 2 or Type 0 is a viable core": REJECTED.** T2 grosses more ($316k vs
  $259k) but at 19,776 trades it nets less after 1 tick ($128k vs $162k). Cost-fragile exactly as
  the thesis predicted. Type 2/3 belong in conditional sleeves.
- **"The vendor's 90/179 is special": REJECTED.** SM 179 sits at the weak edge of the profitable
  band; the plateau centre is 180–260. The 2:1 TM/SM guidance is irrelevant to the Type-1 core
  because `TrendVector` never enters the flip rule.
- **"5-minute is a smoother 1-minute": REJECTED.** Timeframes are strongly non-monotonic; 5m at
  90/179 is near-dead after costs with 2.7× the drawdown.

## 6. Unresolved questions (with what would resolve each)

| # | Question | Resolver |
|---|---|---|
| U1 | Exact Type-2 rule (95.3 %, structured residual) | four-angle adversarial decode in flight; teacher-forced test says the defect is local, not model-class |
| U2 | Exact `PullbackEarly=false` firing rule | same decode; PE=false events cluster 1–10 bars after PE=true events |
| U3 | Exact `TrendVector` when `V > S/2` | bounded ambiguity, 95.6 % with a two-rung clamp; **excluded from all experiments** rather than chased |
| U4 | Is the overshoot ratio scale-invariant in ticks or in σ units? | DC01/DC02 (§7) — free, no config burn, and it *decides* whether H-006 can work |
| U5 | Does the edge survive High Order Fill Resolution? | DR07-H1 |

## 7. External scientific evidence (deep-research packets DR-01…DR-07)

Full packets in `research/deep_research/`. The two results that change how the campaign should
think:

**(a) The overshoot scaling law is the no-alpha null, not evidence of edge.** For a driftless
diffusion the maximum-before-a-δ-drawdown is exponentially distributed with mean δ
(Lehoczky 1977; Zhang & Hadjiliadis 2009). A stop-and-reverse system entered at directional-change
confirmation and exited at the next flip earns exactly `ω − δ` per segment, so
`E[P&L] = 0` pre-cost and strictly negative after costs. The celebrated empirical finding that
"mean overshoot ≈ threshold" across 13 FX pairs (Glattfelder, Dupuis & Olsen 2011) therefore
*confirms near-martingale behaviour* — it is not a tradable pattern, and the DC trading literature
that cites it should not be read as a prior of edge. Our entire full-history result
($259k over 10,182 trades ≈ 6 ticks gross per trade at δ = 179) is a **~3 % upward deviation of
r = E[ω]/δ from 1.0**. That reframes the thesis: the edge is thin *by construction*, and the
research question is precisely "where and when is r > 1".

**(b) There is a derivable optimal threshold, and its σ-dependence is an empirical question with a
free answer.** Combining the DC event-rate law `N(δ) ∝ (σ/δ)²` with a fixed per-flip cost `c`
gives expected profit per unit time `Π(δ) ∝ σ²[(r(δ)−1)/δ − c/δ²]`, maximised at
`δ* = 2c/(r−1)`. If `r` is scale-invariant in **tick** space, `δ*` is independent of volatility
and a *fixed* threshold is correct — H-006 would then be a distraction. If `r` is invariant in
**δ/σ** space, `δ*` scales with σ and H-006 is the right fix. This is measurable directly from
the close series with **zero** configuration burn, and it is now the highest expected-value-of-
information item on the frontier.

Other high-priority external hypotheses now on the frontier: DR03-H1 (split exit/reversal — the
control-theory case for H-007), DR03-H2 (CUSUM with a drift allowance `k > 0` generalises the
flip statistic), DR04-H2/H4 (frozen-at-birth vs continuously-updated adaptive threshold),
DR05-H2 (fade *failed* flips — a complementary engine defined natively on our own event stream),
DR06-H4 (neighbourhood-smoothed selection should dominate argmax under parameter chaos — testable
on the already-archived dense scans, no new burn), DR07-H1/H5 (fill-resolution and one-bar-delay
execution realism).

## 8. New open-model hypotheses (only reachable because we own the math)

- **H-006** `S_episode = k·σ_birth`, σ causal and frozen at trend birth. Success signature is *not*
  higher aggregate profit — it is a more stable event rate, a more stable S/σ ratio, better
  year/fold balance, and cross-market portability. Gated on U4.
- **H-007** split `S_exit ≠ S_reverse` (exit at the smaller, reverse only at the larger). Directly
  attacks the 46 %-untaken opportunity set, and is exactly the two-threshold hysteresis the
  control-theory literature recommends (DR-03).
- **H-008** anchor definition: close extreme vs High/Low extreme vs close-confirmed extreme.
- **H-009** event time vs clock time for the pause/wave counters — the vendor's counters change
  economic meaning between 1m and 3m, which is a confound in every timeframe comparison to date.
- **H-010** wave-index conditioning: leg 1 of a trend is a different object from leg 8, and the
  counter is free information already computed.

## 9. Portfolio hypotheses

- All Solar variants (any S, any timeframe) are **one family** until position and drawdown overlap
  prove otherwise; they share one risk budget.
- The natural complement is **failed persistence** (DR-05), because it is definable on the *same*
  recovered event stream: a Type-1 flip that fails to achieve a minimum overshoot, a re-cross of
  the old threshold, or a rapid opposite re-flip. It should earn exactly when the persistence
  family fails, and must be blocked during a strong, efficient continuation.
- A lower-standalone-Sharpe sleeve qualifies if it materially improves the portfolio *during Solar
  drawdowns*; incremental value is judged at equalised risk, never on combined net profit.

## 10. Standing validation reality (unchanged, restated because it is load-bearing)

All historical data through 2026-07-31 has been examined during discovery. **No clean out-of-sample
window remains.** ES is external mechanism evidence, not NQ OOS. Nested chronological validation,
purged CPCV, PBO/CSCV, DSR/PSR and Harvey-Liu haircuts are the substitutes, and every tested
configuration counts toward the haircut — renaming a strategy class does not reset the count.
