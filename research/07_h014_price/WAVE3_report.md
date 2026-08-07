# Wave 3 — mechanism, portability, and signal architecture

_2026-08-07 · `SolarWaveOpenV4` and `SolarWaveSleeveV1`, both gate-checked against the frozen
canonical baseline to the penny before any result was read · NQ and ES 09-26 · 3-minute ·
full history 2022-01-01 → 2026-07-31 · real NT8 slip-1 · all-days Sharpe on the union calendar via
`src/analytics/ensembles.py`._

Wave 2 ended with H-006 downgraded to INCONCLUSIVE because "adaptive beats fixed" was not
statistically separable. Wave 3 asks the three questions that do not depend on separating two
correlated families: **is the mechanism specific? does it travel? and is there anything additive
in the signal set we now own completely?**

---

## 1. H-014 — the mechanism IS volatility-specific: **PASS**

The decisive control. If a threshold proportional to **price** performed like one proportional to
**volatility**, then "volatility normalisation" would be nothing but "a threshold that varies over
time" and H-006's mechanism claim would die. DC02 had made this a live possibility: price
normalisation sat *between* fixed-tick and volatility in stabilising the overshoot ratio.

| NQ ensemble (13 cells each) | net | **Sharpe** | max DD | positive years |
|---|---|---|---|---|
| adaptive, `S = k·σ` | $198,059 | **0.978** | −$39,126 | 5/5 |
| fixed, all 21 cells | $159,424 | 0.893 | −$35,669 | 5/5 |
| **price-proportional, `S = bp·price`** | $43,299 | **0.250** | −$64,034 | 3/5 |

Paired circular block bootstrap (L = 20, B = 10,000):

| comparison | ΔSharpe | **P(Δ ≤ 0)** |
|---|---|---|
| **volatility − price** | **+0.728** | **0.009** |
| price − fixed | −0.643 | 0.999 |
| volatility − fixed | +0.085 | 0.358 |

**Volatility scaling is significantly better than price scaling (p = 0.009), and price scaling is
significantly worse than a plain fixed tick count.** This is the first clean significance result in
the campaign, and it survives precisely because it compares two *dissimilar* families rather than
two near-copies.

The mechanism claim therefore stands: what matters is the threshold's size relative to **how far
the market is currently moving**, not relative to its price level. Scaling by price actively
destroys the filter — it makes the threshold grow through 2022–2026 while volatility did not move
proportionally, pushing the system off the profitable operating point.

**This does not restore "adaptive beats fixed"** — that comparison is still +0.085 at P = 0.358.
What it establishes is narrower and more durable: *if* there is an advantage to a time-varying
threshold, its source is volatility, and the campaign is not merely rediscovering "any drift will
do".

## 2. ES portability — **FAILS**, and this is the most important negative in the campaign

No clean NQ out-of-sample window remains, so a second instrument is the strongest external
evidence obtainable. Both normalisations were run on ES over the identical grid and window.

| ES ensemble | net | Sharpe | positive cells | positive years |
|---|---|---|---|---|
| price-proportional (13) | −$66,379 | **−1.920** | 2/13 | 0/5 |
| **volatility-proportional (13)** | **−$12,455** | **−0.329** | 8/13 | 2/5 |

The volatility version is far better than the price version on ES too — consistent with §1 — but
**the ES ensemble is still negative**, with a block-bootstrap `P(Sharpe ≤ 0) = 0.829`.

The structure is informative rather than simply damning:

- **The shape transfers.** Spearman rank correlation of Sharpe across the `bp` grid, NQ vs ES:
  **0.780**. Both markets prefer wider thresholds; both collapse at narrow ones.
- **The level does not.** On ES the profitable region shifts *up*: `k ≥ 18` is positive (best
  k = 18: $35,208, Sharpe 0.72; k = 24: $28,709; k = 26: $23,468) while `k ≤ 16` is catastrophic.
  The whole low-k half of the grid, which is fine on NQ, is unusable on ES.
- **A mechanical reason exists.** ES's tick is $12.50 against NQ's $5, so per-trade friction is
  2.5× larger relative to a given move in σ units. The friction-optimal threshold must therefore
  sit higher on ES. That is a prediction the data matches, not a rationalisation after the fact.
- The two adaptive ensembles' daily P&L correlate at **0.797**, as expected for one underlying
  market factor.

**Honest verdict: a blind transfer of the NQ-calibrated parameter to ES loses money.** The
mechanism is partially portable — the ordering survives and a profitable ES region exists — but a
single normalised `k` does **not** produce a stable region on both instruments, which is exactly
the property §16 of the campaign constitution asks for. Per the constitution this earns a **large
overfitting penalty**, and it is recorded as such rather than explained away. It would be easy to
"fix" this by fitting `k` separately per instrument; that is curve-fitting a second market and it
is not being done.

## 3. Type-0 attribution — possible only now, and it found one live sleeve

With `solar_wave_full()` exact, all three signal types can be generated in Python and every
architecture evaluated at **zero engine time and zero configuration budget**. Full attribution in
`research/09_sleeves/`. The Python screen found Type-3 re-entries worth +$73.55 per marginal trade
and per-trade economics rising monotonically with the wave index ($26 → $53 → $76 → $151 for waves
1 → 4). Both were then taken to the engine.

### Engine confirmation, matched cells (SM 180–250, 8 cells each)

| architecture | net | **Sharpe** | max DD | worst year | positive years |
|---|---|---|---|---|---|
| **C1** Type-1 core (R4 plateau) | $180,479 | 0.784 | −$53,689 | +$7,796 | 5/5 |
| **C2** + one Type-3 re-entry per episode | **$233,628** | **0.862** | **−$47,413** | **+$19,801** | 5/5 |
| **C4** + one Type-2 *or* Type-3 re-entry | $141,303 | 0.450 | −$64,621 | +$9,988 | 5/5 |

**C2 improves every point estimate at once** — +29 % net, +0.078 Sharpe, a *smaller* drawdown, and
a worst year 2.5× better — which is unusual: most changes in this campaign trade one against
another. Marginal economics: **+10,838 trades earning $425,191 = +$39.23 per marginal trade**,
above the core's own $34.44 average.

**C4 is decisively worse.** Adding Type-2 costs 0.33 Sharpe. This confirms Wave 1's "unconditional
Type 2 is cost-fragile" from an independent direction, and matches the Python attribution
(Type-2 average $22.61 on a 28 % win rate).

### But the Type-3 sleeve does not clear significance either

Tested on its own 19,606 trades, which is a far higher-powered test than comparing two correlated
ensemble Sharpes:

| test | result |
|---|---|
| mean marginal trade | **+$24.89** |
| naive iid t-test | t = 2.432, one-sided **p = 0.0075** |
| **session-block bootstrap** (respects clustering) | **P(mean ≤ 0) = 0.1147** |
| ensemble ΔSharpe vs C1 | +0.078, P(Δ ≤ 0) = 0.413 |

The iid test clears 5 %; the block bootstrap, which is the correct one, does not. And the sleeve
has two structural weaknesses: **it loses $98,220 in 2022** (the bear year), and its gain is
concentrated in the wide cells — SM 230/240/250 contribute $111k/$125k/$136k while SM 200 is
slightly negative. Seven of eight cells are positive.

**Verdict: C2 is INCONCLUSIVE, leaning positive.** It is the best-behaved candidate the campaign
has produced on point estimates, and it is the only change that improved return *and* drawdown
*and* worst-year simultaneously. It still cannot be certified on 4.6 years.

## 4. DSR under the preregistered rule — nothing is promotable by deflation

`research/registry/TRIAL_ACCOUNTING_RULE.md` was written **before** any figure was recomputed
under it, precisely because the previous DSR figures had been produced with a dial rather than a
rule. Applying R1–R6 to all **213** inspected trials:

- R3: `N_eff` = **5** clusters (participation ratio of the correlation eigenvalues)
- R4: cluster-representative Sharpe variance `V` = **0.645** (std 0.803)
- Benchmark expected-max Sharpe = **0.958**

| candidate | Sharpe | PSR | **DSR** | promotable by R7 (≥ 0.90)? |
|---|---|---|---|---|
| R4 fixed, all 21 | 0.910 | 0.987 | **0.454** | no |
| adaptive (13) | 0.996 | 0.993 | **0.538** | no |
| combo (13) | 1.003 | 0.993 | **0.545** | no |

R6 (Harvey–Liu at the raw N = 255): every candidate has **haircut Sharpe 0.000** and none passes
BHY.

**Sensitivity, reported and explicitly NOT used for promotion:** removing the arms that were
mechanically broken for diagnosed reasons (H-011's desynchronised arm C, H-007's tail-truncating
splits) collapses `V` from 0.645 to 0.027 and lifts every DSR to **0.96**. The answer therefore
swings from "far below the bar" to "comfortably above it" on a judgement call about which failed
experiments count as trials.

That swing is the finding. **Deflation cannot adjudicate this edge in either direction**, because
the result is dominated by an arbitrary choice rather than by the data. The preregistered rule
anticipated this in writing:

> If that is the outcome, the honest conclusion is that the historical record is too short to
> certify this edge by deflation, and promotion must rest on structure, mechanism and
> out-of-sample portability instead.

That is now the campaign's position. And on the two of those three that Wave 3 could test:
**mechanism PASSED (§1), portability FAILED (§2).**

## 5. Config accounting

Wave 3 consumed: 13 (H-014) + 26 (ES, two normalisations) + 20 (C2, C4) + 2 gates = **61**.
Campaign total ≈ **316**. All DSR figures above use the preregistered `N_eff`, not this raw count,
with the raw count used for the R6 haircut.

## 6. What Wave 3 changes

| item | verdict |
|---|---|
| **H-014** volatility vs price normalisation | **PASS** — vol is significantly better (p = 0.009); the mechanism is specific |
| **ES portability** | **FAIL** — blind transfer loses money; shape travels (ρ 0.780), level does not |
| **C2** Type-1 + one Type-3 re-entry | **INCONCLUSIVE, leaning positive** — best point estimates in the campaign, p = 0.115 on the correct test |
| **C4** adding Type-2 | **FAIL** — −0.33 Sharpe |
| Wave-index conditioning | **live** — monotone per-trade economics through wave 4; not yet tested as a filter in the engine |
| DSR as a promotion criterion | **abandoned** — cannot adjudicate; promotion must rest on structure, mechanism, portability |

---

## 7. ADDENDUM — the two remaining live items both close NEGATIVE

### 7a. The Type-3 sleeve does **not** stack on an adaptive core — it destroys it

C2 was only ever tested on a *fixed*-threshold core. Re-running it on the adaptive core (13 cells,
matched k grid, everything else identical):

| architecture | net | **Sharpe** | max DD | Calmar | worst year | positive years |
|---|---|---|---|---|---|---|
| **R5** adaptive, Type-1 only | $198,059 | **0.994** | **−$39,126** | **0.926** | **+$12,160** | **5/5** |
| R5 + C2 one Type-3 re-entry | $147,931 | 0.592 | −$45,278 | 0.598 | **−$4,065** | 4/5 |

Paired block bootstrap: **ΔSharpe −0.402, P(Δ ≤ 0) = 0.879.** The sleeve costs 0.40 Sharpe, breaks
the every-year-positive property (2025 turns negative), and worsens the drawdown.

**This kills C2 as a general improvement.** Its apparent value on the fixed core (+29 % net, better
drawdown, better worst year) does not survive a change to the core it sits on. A sleeve whose sign
flips when you change the threshold rule is not capturing a robust effect — it is exploiting an
interaction with one specific threshold schedule. That is precisely the fragility the campaign
exists to detect, and it was found by a preregistered follow-up rather than by chance.

The mechanism is legible in hindsight: on the fixed core the re-entries were concentrated in the
wide cells (SM 230/240/250 supplied $111k/$125k/$136k of the sleeve's $488k). The adaptive core
already spends most of its time at an effectively wide threshold, so the re-entries no longer land
where they helped, and their cost — friction on 10,000+ marginal trades — is all that remains.

### 7b. Wave-index conditioning — **no exploitable signal**

The Python attribution had shown per-trade economics rising monotonically with the wave index
($26 → $53 → $76 → $151 for waves 1 → 4), which looked like the last free information in the
recovered model. Requiring a minimum wave index for re-entries (SM 230, up to 3 re-entries):

| MinWave | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| Sharpe | 0.81 | 0.81 | 0.54 | 0.86 | 0.54 | 0.65 | 0.55 | 0.93 |
| trades | 6,918 | 6,918 | 6,240 | 5,910 | 5,741 | 5,650 | 5,601 | 5,563 |

MinWave 1 and 2 are identical by construction (a Type-3 always implies wave ≥ 2). Beyond that the
response is **non-monotone and indistinguishable from noise** — 0.54, 0.86, 0.54, 0.65, 0.55, 0.93 —
on a steadily shrinking trade count. The attractive per-wave averages in the Python attribution came
from a handful of large trades in a thin cell count, not from a conditionable effect.

**The wave counter carries no usable trading signal.** It remains a correct and interesting
description of trend structure; it is not an edge.

### 7c. What this leaves

Every sleeve and every conditioning axis is now closed. **R5 — the volatility-normalised ensemble,
Type-1 signals only — stands alone as the recommended architecture**, and it stands unimproved by
anything the campaign was able to add to it. That is a cleaner result than a stack of marginal
enhancements would have been, and it is consistent with the campaign's dominant finding: on 4.6
years of one instrument, almost nothing is separable from noise, and the additions that look
helpful are the ones most likely to be fitting the specific core they were tested against.
