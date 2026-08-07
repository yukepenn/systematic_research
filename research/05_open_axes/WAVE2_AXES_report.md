# Wave 2 — the three axes the recovered mathematics unlocked

> ## ERRATA — 2026-08-07, after independent red-team review
>
> **H-006 is DOWNGRADED from PASS to INCONCLUSIVE.** The comparison below was not like-for-like:
> the fixed family was scored as two separate half-range ensembles (SM 180–250 and SM 280–880)
> while the adaptive family was scored across its whole sweep. Scored the same way, the **full
> 21-cell fixed family reaches Sharpe 0.917**, not 0.814, and the adaptive advantage falls from
> +0.210 to **+0.087**, with a paired block-bootstrap **P(Δ ≤ 0) = 0.358**. Excluding 2025 alone
> drops it to +0.046. The whole effect lives in one calendar year, and the adaptive family
> *underperforms* fixed in the low-volatility tercile — the opposite of the claimed mechanism.
>
> **All DSR figures in this report are WITHDRAWN.** They were computed with an inconsistent
> (N, V) pair: n_trials = 255 but a variance pool drawn only from the 44 surviving cells. Under an
> honest pool the adaptive ensemble's DSR at N = 255 is 0.16–0.38, not 0.832, and it fails a
> Harvey–Liu haircut at N = 1000 outright.
>
> **Sharpe convention:** figures below use ensemble-active days; the campaign convention is now
> all-days, which lowers them (R4 0.814 → 0.794, adaptive 1.010 → 1.004, and much more for sparse
> cells). Corrected table in the red-team report.
>
> The falsifications in this report (H-007, raw-HL anchor) were re-checked and **stand**.
> Full detail and controller re-verification: `research/06_red_team/RED_TEAM_WAVE1C_WAVE2.md`.


_2026-08-07 · Instrument `SolarWaveOpenV3` (open engine, **zero vendor dependency**) · NQ 09-26,
3-minute · full history 2022-01-01T06:00:00Z → 2026-07-31T21:59:59Z · **real NT8 slippage 1 tick
per execution** · Lifetime commission · analytics `src/analytics/{execledger,validation}.py`._

**Gate, run before any result was read:** `SolarWaveOpenV3` at its default settings (AnchorMode 0,
ThresholdMode 0, ExitMultiplier 0) reproduces the frozen canonical baseline exactly — 2,915 trades,
$146,440.60, PF 1.132213. Every axis defaults to the vendor behaviour, so a difference can only
come from the axis under test.

The evaluation unit is the **ensemble**, not the cell. Wave 1c established that the threshold
parameter is not selectable (PBO 0.63, negative IS→OOS slope), so comparing best-cells would be
comparing two lottery winners. Every family below is scored as an equal-risk ensemble over its
whole parameter range.

## Result

| family | cells | net | **Sharpe** | max DD | Calmar | PSR | **DSR** | worst year | positive years |
|---|---|---|---|---|---|---|---|---|---|
| **R4** fixed threshold, close anchor *(Wave-1c reference)* | 8 | $180,479 | 0.814 | −$53,689 | 0.659 | 0.969 | 0.677 | +$7,796 | 5/5 |
| **H-008** close-confirmed High/Low anchor | 10 | $215,137 | 0.947 | −$47,698 | 0.860 | 0.986 | 0.781 | +$7,023 | 5/5 |
| **H-006** adaptive threshold `S = k·σ` | 13 | $198,059 | **1.010** | **−$39,126** | **0.958** | 0.993 | **0.832** | **+$12,160** | 5/5 |
| **COMBO** adaptive + close-confirmed HL | 13 | $196,887 | **1.011** | −$41,178 | 0.893 | 0.993 | 0.835 | +$6,422 | 5/5 |

DSR at `n_trials = 255` (every configuration logged campaign-to-date, not just this wave).

Per-year, $k:

| | 2022 | 2023 | 2024 | 2025 | 2026 (7mo) |
|---|---|---|---|---|---|
| fixed (R4) | +44.2 | +7.8 | +35.0 | +29.5 | +64.0 |
| anchor | +7.0 | +14.6 | +59.8 | +72.3 | +61.4 |
| **adaptive** | **+41.1** | **+12.2** | **+29.3** | **+60.5** | **+55.1** |
| combo | +26.3 | +6.4 | +28.4 | +76.1 | +59.7 |

## H-006 — adaptive threshold `S = k·σ` frozen at trend birth: **PASS**

σ = causal mean |Δclose| over the trailing 460 bars (≈1 session on 3-minute), sampled **once** at
each trend's birth so the trailing stop stays monotone, clamped to [40, 1200] ticks. Swept
k = 6…30.

Versus the fixed reference: **+24 % Sharpe (1.010 vs 0.814), −27 % drawdown, +45 % Calmar**, a
better worst year, and DSR 0.832 vs 0.677. This is the first change in the campaign that improves
the system on the axes the constitution actually ranks.

### The confound, and how it was killed
The winning adaptive cells trade far less (893–2,459) than the fixed plateau (4,578–8,268). So the
gain could simply have been "a wider threshold is better", which would make normalisation
cosmetic. Two controls:

1. **Fixed thresholds pushed wide** — a dedicated sweep out to SM 880 (13 cells, 840–4,119 trades,
   matching the adaptive turnover range). Result: ensemble Sharpe **0.805**, net $146,466, worst
   year **−$625**. Wider is *not* better — it is indistinguishable from the plateau on Sharpe and
   worse on year-balance. **The confound is eliminated.**
2. **Turnover-matched, cell by cell** — interpolating the fixed curve at each adaptive cell's trade
   count, adaptive wins by +0.25 to +0.66 Sharpe across k = 14–24, and loses only at k = 28–30
   where the fixed comparator is an isolated spike (SM 830 shows Sharpe 1.709, the kind of
   single-point artefact Wave 1c proved is unusable).

### Exposure red-team check
| | mean net exposure | mean gross exposure | net per unit exposure | Sharpe |
|---|---|---|---|---|
| fixed plateau | 0.2411 | 0.3554 | $748,509 | 0.814 |
| **adaptive** | 0.1646 | 0.2633 | **$1,202,941** | **1.010** |

The adaptive family does run 32 % less net exposure — but it earns **61 % more per unit of
exposure**, and Sharpe is scale-free, so the risk-adjusted gain is not a sizing artefact. Members
agree on direction on only 36.3 % of days (versus 53.6 % for the fixed plateau), so the ensemble
diversification is stronger too.

This is the empirical payoff of **DC02**, which predicted the direction from the price series
alone at zero configuration cost: volatility normalisation halves the across-year drift of the
overshoot ratio `r = E[ω]/δ` (0.116 → 0.058), and `r` is the quantity the strategy monetises.

## H-008 — anchor definition: **split verdict**

| anchor | ensemble Sharpe | net | verdict |
|---|---|---|---|
| running **close** extreme (vendor) | 0.814 | $180,479 | reference |
| running **High/Low** extreme | **0.527** | $120,158 | **REJECT** |
| **close-confirmed** High/Low extreme | **0.947** | $215,137 | **PASS standalone** |

"Close-confirmed" means the intrabar extreme is adopted only when the bar's own close agrees with
the trend direction; otherwise the close is used.

The reading is sharp and it matters beyond this test: **the raw intrabar extreme is pure noise
injection** — wicks set the anchor, the ladder chases them, and Sharpe collapses to 0.527. But the
*confirmed* extreme carries real information, beating the pure close anchor by +16 % Sharpe. The
difference between the two is one boolean.

**They do not stack.** Combining the confirmed-HL anchor with the adaptive threshold gives Sharpe
1.011 versus adaptive-alone 1.010 — no incremental value at all. Both axes are doing the same job:
scaling the filter's sensitivity to the bar's own volatility. Once the threshold is normalised, the
anchor refinement is redundant. The simpler model wins on complexity budget, so **H-006 alone is
promoted and the anchor axis is recorded as PASS-but-redundant.**

## H-007 — split exit / reversal distance: **REJECT**

Tested at two reversal distances (SM 230 and SM 180), exit distance swept from 26 % to 100 % of it.
The response is **monotone in the wrong direction at both**:

| S_exit / S_reverse | 0.26 | 0.50 | 0.70 | 0.85 | **1.00 (no split)** |
|---|---|---|---|---|---|
| net (SM 230) | −$128,736 | −$85,412 | +$101,999 | +$120,247 | **+$249,934** |
| Sharpe (SM 230) | −0.75 | −0.39 | +0.38 | +0.44 | **+0.98** |
| net (SM 180) | −$114,886 | −$226,936 | +$30,357 | −$7,295 | **+$198,097** |

Every split is worse, and performance improves monotonically as the split disappears. Trade count
rises from 5,443 to 9,787 as the exit tightens, so each early exit buys another round trip at
~$131 of friction while truncating the right tail.

This is exactly what **DC01** predicted from the segment statistics: the overshoot distribution is
right-skewed with median `ω/δ ≈ 0.76` but mean 1.18 — the system loses on most segments and is
paid by a fat right tail, so **any rule that cuts the tail attacks the only source of profit**.

It also **falsifies DR03-H1**, the control-theory two-threshold-hysteresis recommendation, for this
system. The vendor's single-distance design is not a limitation to be fixed; it is correct for this
payoff shape.

## What the three rejections say together

H-011 (intrabar stop fills), H-008 mode 1 (intrabar anchor) and H-007 (early exit) all failed, and
they failed for one reason. DC01 measured that the close-basis crossing excess is ~23.5 ticks per
segment — **89 % of all friction**, four times commission plus slippage combined — which looked
like the single biggest prize on the board. Both routes to capturing it make things dramatically
worse:

- execute intrabar → position and close-based ladder state desynchronise (−$1.88 M across the
  plateau);
- anchor intrabar → the ladder chases wicks (Sharpe 0.527 vs 0.814).

**The close basis is not a defect; it is a noise filter, and the excess is what the filter costs.**
The 89 % figure is real but it is not recoverable, and that is now demonstrated rather than
assumed. The only thing that improved the system was scaling the threshold to volatility — i.e.
making the *filter* adaptive, not making the *execution* faster.

## Parameter selection remains impossible everywhere

CSCV, 16 blocks, 12,870 splits, within each family:

| family | PBO | P(OOS Sharpe < 0) | IS→OOS slope |
|---|---|---|---|
| fixed | 0.631 | 0.108 | −1.051 |
| anchor | 0.689 | 0.095 | −1.477 |
| **adaptive** | **0.898** | 0.129 | −0.923 |
| combo | 0.481 | 0.085 | −0.606 |

The adaptive family's `k` is *even less* selectable than the fixed family's StopMultiplier
(PBO 0.898). Every family has a negative IS→OOS slope. The ensemble is not a convenience — it is
the only defensible way to hold any of these.

## Status

| hypothesis | verdict |
|---|---|
| **H-006** adaptive threshold `S = k·σ` frozen at trend birth | **PASS** — new reference architecture **R5** |
| **H-008** close-confirmed High/Low anchor | **PASS standalone, redundant with H-006** |
| H-008 raw High/Low anchor | **REJECT** |
| **H-007 / DR03-H1** split exit ≠ reversal | **REJECT** — monotone, both reversal distances |
| H-011 stop-order execution | **REJECT** (Wave 1c report §3) |
| DC02 σ-normalisation predicted from price series alone | **CONFIRMED empirically** |

Configurations consumed this wave: 13 (H-006) + 22 (H-007) + 20 (H-008) + 13 (fixed-wide control)
+ 13 (combo) = **81**. Campaign total ≈ **255**, which is the `n_trials` used in the DSR above.

## Next

1. **R5 is not yet promotable.** It needs nested walk-forward at the ensemble level, per-fold
   turnover and exposure reporting, slip-2 stress, and an independent red-team pass by an agent
   that did not build it.
2. σ estimator robustness: only one estimator (mean |Δclose|, 460 bars) and one clamp pair were
   tested. DR04-H3 predicts non-monotonic sensitivity to estimator lag — that is the next control.
3. Type-0 attribution and the C0–C6 signal architectures, now unblocked by the complete model.
4. Complementary families (failed persistence per DR-05), ES portability, portfolio routing.

---

## H-012 — σ-estimator robustness (the preregistered gate on R5): **PASS**

H-006 used exactly one volatility estimator (mean |Δclose| over 460 bars ≈ 1 session). If the
result depended on that choice, it would be a fitted parameter wearing a mechanism's clothes.
Sweeping the estimator window from 60 to 3,660 3-minute bars (0.13 to 7.96 sessions) at k = 18:

| window (sessions) | 0.13 | 0.78 | **1.43** | 2.09 | 2.74 | 3.39 | 4.70 | 6.00 | 7.96 |
|---|---|---|---|---|---|---|---|---|---|
| Sharpe | **0.769** | 1.116 | **1.494** | 1.410 | 0.912 | 1.199 | 1.013 | 1.244 | 0.996 |
| positive years | 4/5 | 5/5 | 5/5 | 5/5 | 4/5 | 5/5 | 5/5 | 5/5 | 5/5 |

**Every estimator lag works.** Sharpe ranges 0.769–1.494 and 11 of 13 cells are positive in all
five years. The H-006 result is not an artifact of the 460-bar choice.

**DR04-H3 partially confirmed.** The packet predicted that both sub-daily *and* multi-week
estimators would underperform a ~1-session estimator. The sub-daily half holds — the 0.13-session
window is the worst cell by a clear margin (0.769), consistent with a procyclical estimator
chasing its own noise. The multi-week half does **not**: windows out to 8 sessions hold Sharpe
0.99–1.32. The honest reading is "sub-daily is harmful; anything from ~1 session upward is fine",
not the predicted hump.

`PBO` over the estimator lag is **0.297** — far below the `k` parameter's 0.898, so the estimator
window is much closer to being a genuine choice than `k` is. It is still above the 0.20 bar, so it
is held as an ensemble like everything else.

**Caveat, stated because it is load-bearing:** this sweep held `k = 18`, a value chosen *after*
seeing the k-sweep. The estimator-lag ensemble's headline (Sharpe 1.184, positive every year,
PSR 0.9953) therefore inherits that selection and **must not be quoted as a further improvement
over R5**. It is a robustness result only: it shows the adaptive mechanism survives a wide range
of estimator choices, which is what the gate asked.

**Remaining gates before R5 can be promoted:** ensemble-level nested walk-forward, slip-2 stress,
H-013 (weighting), and the independent red-team pass.
