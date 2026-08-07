# Red team — Wave 1c (R4 ensemble) and Wave 2 (R5 adaptive threshold)

_2026-08-07 · Four independent adversarial reviewers, none of whom produced the results, attacking
along separate axes: implementation artifact/look-ahead, luck, statistical validity, and the H-006
confound. Every severe claim below was **re-verified by the controller with its own code** before
being accepted. Verification script: `/tmp/verify_rt.py`, reproduced in §5._

**Headline: H-006 is downgraded from PASS to INCONCLUSIVE. The claim "the adaptive threshold beats
the fixed threshold" does not survive a fair comparison.** The R4 ensemble finding survives.

---

## 1. What survived — verified clean

The artifact reviewer re-derived everything from the raw NT8 fill ledgers with its own parser,
bypassing `src/analytics` entirely, and found no defects:

- **Fill pairing is correct.** Across all 137 ledgers, fills strictly alternate entry/exit starting
  with an entry, quantity is 1 on every fill, no trade overlaps the next, no position spans a
  session boundary, all prices sit on the 0.25 grid.
- **No look-ahead in the adaptive σ.** Code review of `UpdateVol()` / `ResolveS()` /
  `CausalSigma()` in `SolarWaveOpenV3.cs`: the recompute loop sums `|Close[i] − Close[i+1]|` and
  NinjaScript `barsAgo` indexing makes `Close[i+1]` *older* than `Close[i]`, so the loop reads
  strictly backward. σ is frozen at trend birth as documented.
- **The ensemble is a strict fixed 1/N mean including flat days**, not a hindsight reweighting.
  Dividing by active members instead fails to reproduce any published number; strict `sum/N`
  reproduces net, Sharpe, drawdown and every per-year figure to the cent.
- **`validation.py` is correct** against the published definitions. Independent reimplementation of
  Bailey–López de Prado PSR matches to 0.0; a 2,000-draw null Monte Carlo gives mean PSR 0.507
  (KS p = 0.346); the DSR expected-max benchmark matches a 200,000-draw simulation within 0.6 %.
  No rank-convention error, no logit off-by-one, no annualisation error.
- **PBO is stable across partition granularity.** Recomputed at 8/12/16/24 blocks: adaptive
  0.814/0.850/0.898/0.878, fixed 0.643/0.683/0.625/0.671. Every IS→OOS slope negative in every
  cell. **The non-selectability conclusion — the load-bearing finding of Wave 1c — is confirmed.**
- **The R4 ensemble reproduces exactly**: net $180,479.44, Sharpe 0.803 (all-days), max DD
  −$53,689.43, beats 7 of 8 members, only 3 of 8 members positive in all five years.
- **Leave-one-year-out is clean**: adaptive Sharpe stays in 0.924–1.112 across all five cuts.
  Removing 2022 *raises* Sharpe to 1.027, so the NQ bear year is not carrying the result.
- The slippage side-claims verify ($9.72/RT on the SM 230 cell against a campaign-wide $9.5352,
  {0,5,10} distribution confirmed; slip-0 and slip-1 timestamps byte-identical).

## 2. FATAL TO THE H-006 CLAIM — the comparison was not like-for-like

**The fixed family was split into two half-range ensembles while the adaptive family was given its
full range.** R4 covered SM 180–250 (8 cells) and the "fixed-wide control" covered SM 280–880
(13 cells) — but they were never combined, while the adaptive family was scored across its entire
k = 6…30 sweep. Scoring the fixed family the same way it scored the adaptive one:

| family | cells | net | **Sharpe** |
|---|---|---|---|
| adaptive `S = k·σ` | 13 | $198,059 | **1.004** |
| fixed plateau (the published comparator) | 8 | $180,479 | 0.794 |
| fixed wide | 13 | $146,466 | 0.766 |
| **FIXED, FULL RANGE (the fair comparator)** | **21** | $159,424 | **0.917** |

The advantage collapses from **+0.210 to +0.087 Sharpe**.

Paired circular block bootstrap (L = 20 days, B = 10,000), controller-verified:

| comparison | observed ΔSharpe | **P(Δ ≤ 0)** | 5th percentile |
|---|---|---|---|
| vs fixed plateau (as published) | +0.210 | **0.280** | −0.361 |
| **vs fixed full range (fair)** | **+0.087** | **0.358** | −0.291 |
| vs fixed plateau, excluding 2025 | +0.053 | 0.458 | — |
| vs fixed full range, excluding 2025 | +0.046 | 0.455 | — |

**Even the published comparison is not significant (P = 0.28), and the fair one is nowhere near
(P = 0.36).** Removing a single calendar year — 2025 — reduces the difference to noise. Per-year
ΔSharpe is +0.10 / +0.23 / +0.05 / **+0.69** / −0.19: the entire effect lives in 2025.

**Worse for the mechanism story:** the adaptive advantage is concentrated in the *high*-volatility
tercile and **reverses in low volatility** (adaptive 0.180 vs fixed 0.629). A volatility-normalised
threshold is supposed to make behaviour *more* uniform across volatility regimes. It did the
opposite.

**And DC02's supporting evidence is thinner than reported.** Its "2025" cell is January 2025 only
(406 segments) because the canonical ledger ends 2025-01-31. Recomputed, the vol-vs-price
normalisation ordering narrows to 0.118 / 0.099 / 0.079 — vol-normalisation still leads, but the
margin over *price*-normalisation is small, and price-scaling was never tested as a strategy. The
mechanism attribution to volatility specifically, rather than to generic time-variation, is not
established.

**Verdict: H-006 → INCONCLUSIVE.** Not refuted — the point estimates still favour adaptive on
drawdown (−$39,126 vs −$53,689), Calmar, and worst year, and its worst leave-one-year-out Sharpe
(0.924) exceeds the fixed plateau's best (0.916). But "adaptive beats fixed" is not supported at
any conventional standard, and the campaign does not promote on point estimates.

## 3. MAJOR — the DSR figures were computed with an inconsistent (N, V) pair

The published DSR claimed `n_trials = 255` but drew the trial-Sharpe **variance** from only the 44
member cells of the four *surviving* families (std 0.216), silently excluding every rejected trial
— H-007's 22 cells, the raw-HL anchor's 10, the fixed-wide 13. The reviewer recovered the implied
std by inversion (0.2132/0.2151/0.2159/0.2157 across the four published rows — a single common
pool) and reproduced all four published values to ±0.006.

Using an honest pool, the true campaign-wide trial-Sharpe dispersion is **0.40–0.50**, not 0.216.
Consequences for the adaptive ensemble:

| variance pool | DSR @ N=255 | DSR @ N=1000 |
|---|---|---|
| published (44 survivors, std 0.216) | 0.832 | 0.773 |
| all 168 archived series | 0.377 | 0.238 |
| Wave-2's own 81 trials (std 0.499) | **0.160** | 0.068 |

**And it fails Harvey–Liu outright at N = 1000:** t = 2.323, two-sided p = 0.0202; Bonferroni
p_adj = 1.0 → haircut Sharpe **0.000**; the BHY 5 % FDR threshold at N=1000 is 6.7e-6.

A defensible rescue exists but is a *different* claim: the Wave-2 trials are highly correlated
(mean pairwise ρ = 0.295, effective number of independent bets 6.6), and treating clusters as
trials with the honest variance gives DSR ≈ 0.854. **That is a legitimate procedure, but it must be
preregistered and applied campaign-wide, including to every future wave — not adopted now because
it produces the desired number.** Until that decision is made and written down, **no DSR figure in
`WAVE1C_report.md` or `WAVE2_AXES_report.md` should be relied upon.**

## 4. MAJOR — the P&L is entirely right tail, and the short side has no standalone edge

Controller-verified by pooling every member's 1/N-scaled trades:

| family | trades | net | top 1 % of trades | as % of net |
|---|---|---|---|---|
| adaptive | 34,148 | $198,059 | $317,424 | **160.3 %** |
| fixed plateau | 48,868 | $180,479 | $448,380 | **248.4 %** |

**The bottom 99 % of trades lose money in aggregate in both families.** Removing the top 10 *days*
takes the adaptive ensemble from $198,059 to $71,923.

This is not a defect — DC01 predicted it exactly (median `ω/δ ≈ 0.76`, mean 1.18; an exponential
overshoot distribution) and it is why H-007's early exits failed. But it is a **first-order risk
disclosure that the reports did not make**, and it sets a hard constraint: any future filter,
veto, position cap or profit target must be checked for right-tail retention before anything else.

**Short side:** adaptive short-only Sharpe 0.347, and **excluding 2022 and 2025 the short book is
net negative** (−$8,397, Sharpe −0.113). Short profits are essentially two bear episodes. The long
side carries the system (net $147,453, Sharpe 1.189, max DD −$27,376).

## 5. MINOR but material — conventions and bookkeeping

- **Sharpe day-basis shifted between reports without disclosure.** The same R4 ensemble is 0.803 in
  `WAVE1C_report.md` (all 1,318 days) and 0.814 in `WAVE2_AXES_report.md` (ensemble-active days).
  For sparse cells the active-day convention inflates hard — adaptive k = 30 reads 1.290 active vs
  0.993 all-days. **Ruling: all-days is the campaign convention from now on**; sparse-cell Sharpes
  in the Wave-2 tables are overstated and are reissued in §6.
- **The archived `wave1c_table_daily.csv` calendar is incomplete.** It holds 1,285 traded dates; the
  union across all families is **1,348**. It omits ~52 Sunday-evening and holiday sessions the
  Wave-2 families trade. Reusing it as a cross-family calendar silently drops P&L (adaptive k = 6
  alone: −$15,679 of dropped losing days). The controller's re-verification in §2 uses the union
  calendar; all future cross-family work must.
- **The exposure-matched $216,922 headline is convention-dependent**, overstating leverage-achievable
  dollars by ~15 % under a minute-level position reconstruction versus the daily-tilt convention used.
- **`cscv_pbo` has a conservative tie-handling bias** (a logit of exactly 0 counts as overfit;
  8.8 % of adaptive splits). Strict `<` would give PBO 0.810 rather than 0.898. The direction
  *strengthens* the non-selectability conclusion, so no change is needed, but it is now documented.
- **The fixed-wide family's PBO is 0.219** — far below every other family and below the conventional
  0.20-ish bar. That was computed but never reported. It weakens the rhetorical use of the
  fixed-wide ensemble as a mere "control": on the selectability criterion it is the *best-behaved*
  family in the campaign.

## 6. Corrected headline numbers (all-days Sharpe, union calendar)

| family | cells | net | Sharpe | max DD | status |
|---|---|---|---|---|---|
| **fixed, full range** | 21 | $159,424 | **0.917** | — | reference |
| fixed plateau (R4) | 8 | $180,479 | 0.794 | −$53,689 | sub-range of the above |
| fixed wide | 13 | $146,466 | 0.766 | — | sub-range of the above |
| adaptive `S = k·σ` | 13 | $198,059 | **1.004** | −$39,126 | **INCONCLUSIVE vs fixed** |

All DSR figures previously published are **withdrawn** pending a preregistered trial-counting rule.

## 7. What would change the verdict on H-006

Stated in advance so the next test cannot be rigged:

1. **Ensemble-level nested walk-forward** showing adaptive ≥ fixed-full-range in a clear majority of
   outer folds — the fold structure, not the aggregate, is the honest unit.
2. **The high-volatility-tercile edge surviving causal (expanding-window) tercile definitions and
   the exclusion of 2023.**
3. **A price-proportional threshold family run through NT8** over the same window. `SolarWaveOpenV3`
   already parameterises the threshold axis. If price-scaling matches vol-scaling, the mechanism
   claim is dead and both are just "time-varying threshold".
4. **A full-year 2025 and 2026 DC02 recomputation** (the current one uses January 2025 only).
5. **ES portability** — the same normalised `k` producing a stable region on a second instrument
   would be mechanism evidence no amount of NQ resampling can provide.

Any one of these failing should move H-006 to FAILED rather than back to INCONCLUSIVE.

## 8. What stands

- **The plateau ensemble result (R4) stands.** Independently reproduced to the dollar; PBO/CSCV
  verified; non-selectability confirmed at every block count; the ensemble genuinely beats 7 of 8
  members and is positive in all five years when only 3 of 8 members are.
- **The complete indicator recovery (RE01/RE02) is untouched by this review** — it is exact parity
  against vendor output, not a statistical claim.
- **The falsifications stand** (H-007, H-011, raw-HL anchor, 16:30 exit, the 46 %-untaken premise).
  Negative results at this effect size are far more robust than positive ones: H-007 and H-011 were
  not marginal, they were monotone and catastrophic respectively.
