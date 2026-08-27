# WE_W110 — XM_CONFLICT, loss diversification and tail-winner state · REPORT

Preregistered (`spec.yaml`, committed at `f01b5fe` before any code was written).
Directive V5 §§8, 9, 25, 39, P0-C. `W110b` corrects **this wave's own null** and was run before
anything was reported. Reproduction gate PASSED: anchor 570 → N = 342, anchor 571 → N = 348.

> ## **BOTH QUESTIONS COME BACK IN XM'S FAVOUR, and the first one reverses the direction of W105's alarm.**
> ## **§9 — the +0.464 six-month correlation is NOT downside coupling.** Ordinary ρ sits at the 89.2nd percentile of its circular-shift null, but ρ conditioned on P1's losing weeks is **−0.165 at the 5.2nd percentile**, the worst-decile overlap is at the **7.1st**, and the tail beta in P1's bottom decile is **−0.660 against an all-week beta of +0.073.** The two engines are mildly coupled **when they win** and **anti-coupled when P1 loses**. That is the exact distinction §9 said to look for.
> ## **§8 — the concentration is MECHANISM-CONSISTENT.** Under a fully corrected null the pre-entry state predicts the tail winners at **AUC 0.735 / 0.783 / 0.869** for the top 20 / 10 / 5, **p = 0.000 / 0.003 / 0.000.**
> ## ⚠️ And **two of my own numbers are withdrawn below.**

## 1. The correlation, as a path rather than a number

213 weeks. P1/PCT $1,394/wk, XM $916/wk, XM active in **179 of 213 weeks**.

| window | last | min | p25 | median | p75 | max | frac > +0.30 |
|---|---|---|---|---|---|---|---|
| 13-week | +0.369 | −0.743 | −0.235 | +0.046 | +0.266 | +0.689 | 21.9 % |
| 26-week | **+0.464** | −0.537 | −0.179 | +0.021 | +0.229 | **+0.566** | 12.2 % |
| 52-week | +0.258 | −0.348 | −0.199 | +0.036 | +0.133 | **+0.258** | **0.0 %** |

> **W105's +0.464 reproduces exactly — and it is not unprecedented.** The 26-week series has been
> as high as +0.566 and as low as −0.537 on this same pair, with a median of +0.021, and **12.2 %
> of all 26-week windows have exceeded +0.30.** At 52 weeks the correlation has **never once**
> exceeded +0.30 in four years. W105 was right to flag it and right that it is the quantity to
> watch; it is **not** evidence that a regime changed.

## 2. ⭐ Loss diversification — every statistic against 212 circular shifts

The null re-shifts XM's weekly vector against P1's, preserving both marginals and both
autocorrelation structures exactly and destroying only the alignment.

| statistic | REAL | null mean | null p5 | null p95 | percentile | |
|---|---|---|---|---|---|---|
| ρ, all weeks | +0.081 | −0.000 | −0.109 | +0.113 | 89.2th | mildly coupled |
| **ρ ∣ P1 < 0** | **−0.165** | +0.000 | −0.165 | +0.183 | **5.2th** | **losses ANTI-coupled** |
| ρ ∣ XM < 0 | −0.075 | +0.001 | −0.170 | +0.183 | 27.8th | |
| **P(XM<0 ∣ P1<0)** | **0.341** | 0.352 | 0.292 | 0.418 | 33.0th | vs **0.352 unconditional** |
| P(P1<0 ∣ XM<0) | 0.413 | 0.427 | 0.354 | 0.507 | 33.0th | vs 0.427 unconditional |
| **worst-decile overlap** | **0.005** | 0.011 | 0.000 | 0.023 | **7.1th** | 1 week of 213 |
| **tail beta** (P1's bottom decile) | **−0.660** | +0.003 | −0.873 | +0.871 | 13.7th | all-week beta **+0.073** |
| ρ ∣ XM active | +0.099 | −0.000 | −0.116 | +0.138 | 90.6th | the honest conditional |
| **joint max DD** | **$11,489** | $13,382 | $9,749 | $17,158 | 18.9th | lower is better |
| **joint DD duration** | **7 weeks** | 18.2 | 11.0 | 26.5 | **beyond the null, p < 0.05** | lower is better |

> ### The ordinary correlation is at the **89th** percentile of its null. Every downside statistic is at the **5th–33rd**. That is not a contradiction — it is the whole point of §9. **P1 and XM tend to make money in the same weeks and do NOT tend to lose in the same weeks.**
>
> Conditional on P1 losing, XM's probability of also losing is **0.341 against an unconditional
> 0.352** — if anything *lower*. And in P1's worst decile the regression slope of XM on P1 is
> **negative**.

### ⚠️ WITHDRAWN (found by `W110b`, my own defect)

> The first run reported **"joint worst-10 overlap = 0, at the 0.0th percentile"** — zero overlap
> between P1's ten worst weeks and XM's ten worst weeks. The percentile was computed as *fraction
> of shifts strictly below*, which for a discrete statistic whose null has mass **at** zero is
> meaningless. Corrected: **61.3 % of circular shifts also produce zero overlap.** The fact is
> true and the inference is not. **The statistic is withdrawn.** The joint-drawdown-duration
> result survives the same tie-aware treatment (P(null ≤ 7) = 0.000).

### Has the coupling actually moved?

| statistic | first 26 weeks | last 26 weeks | full |
|---|---|---|---|
| ρ | +0.018 | **+0.464** | +0.081 |
| ρ ∣ P1 < 0 | −0.450 | **−0.027** | −0.165 |
| **P(XM<0 ∣ P1<0)** | 0.200 | **0.500** | 0.341 |
| worst-decile overlap | 0.038 | **0.000** | 0.005 |

> **One recent statistic did move adversely and it is stated plainly: P(XM<0 ∣ P1<0) rose from
> 0.200 to 0.500.** On ~11 P1-losing weeks in that span. ρ ∣ P1<0 stayed negative (−0.027) and the
> worst-decile overlap fell to zero. **The honest read: the downside case has not degraded, and
> the single statistic that could be read as degradation rests on about eleven observations.**

## 3. ⭐ The tail winners share a causal pre-entry state

Every feature known at or before **09:45 on the trade's own session**. No MFE, no MAE, no realized
move — using the future path would make the answer circular by construction.

| feature | top-20 mean | rest mean | perm p | | top-5 mean | rest | perm p |
|---|---|---|---|---|---|---|---|
| **overnight range ÷ trailing median** | **1.620** | 1.144 | **0.002** | | **1.746** | 1.163 | **0.018** |
| **CPI / NFP / FOMC day** | **35.0 %** | 11.3 % | **0.006** | | **80.0 %** | 11.7 % | **0.001** |
| **divergence** (NQ z − composite z) | 0.959 | 1.048 | 0.595 | | **0.255** | 1.054 | **0.013** |
| opening drive, points | 48.6 | 34.9 | 0.086 | | 11.3 | 36.1 | 0.092 |
| gap, points | 125.8 | 90.7 | 0.104 | | 171.7 | 91.6 | 0.055 |
| composite ∣z∣, NQ σ, morning volume, long/short, weekday | — | — | 0.31–0.90 | | — | — | 0.45–0.75 |

### ⚠️ The corrected null (`W110b`) — my first one was too easy

> The first run built leave-one-out predictions from the **true** labels and then tested them
> against a null that permuted labels while **holding the predictions fixed**. With 20 positives of
> 348, dropping one leaves 19 — the prediction vector is heavily informed by the label vector as a
> whole, so that null is far too easy. **W110's 0.697 / 0.758 / 0.863 at the "99.7th / 99.9th /
> 99.9th percentile" are WITHDRAWN.**
>
> Corrected: 400 permutations, each one **re-running the entire 10-fold cross-validated fit on its
> permuted labels**, scaler fitted inside each fold.

| cut | % of net | **real AUC** | null mean | null p95 | **p** | |
|---|---|---|---|---|---|---|
| top 20 | 86 % | **0.735** | 0.492 | 0.630 | **0.000** | MECHANISM-CONSISTENT |
| top 10 | 51 % | **0.783** | 0.481 | 0.683 | **0.003** | MECHANISM-CONSISTENT |
| top 5 | 29 % | **0.869** | 0.453 | 0.752 | **0.000** | MECHANISM-CONSISTENT |

**The correction did not overturn the finding — it strengthened it.**

### Ablation — and it is *not* "just announcement days"

| feature set | AUC | Δ vs full |
|---|---|---|
| all 10 | 0.735 | — |
| **ONLY `is_ann`** | **0.498** | **−0.237** |
| ONLY `on_range_rel` | 0.712 | −0.023 |
| ONLY `is_ann` + `on_range_rel` | 0.703 | −0.032 |
| the 8 features *excluding* both | 0.662 | −0.073 |
| drop `drive_pts` | 0.670 | −0.065 |
| drop `divergence` | 0.689 | −0.046 |
| drop `on_range_rel` | 0.691 | −0.044 |

> **The announcement flag alone is worthless as a ranker (AUC 0.498)** even though its base-rate
> difference is significant. No single feature carries the result and the eight features excluding
> the two headline ones still reach 0.662. **This is a genuinely multivariate pre-entry state.**

### What that state *is*, mechanistically

The top-5 winners are sessions with a **wide overnight range**, an **announcement**, a **large gap**
— and a **small opening drive that barely disagrees with the complex** (divergence 0.26 vs 1.05;
drive 11.3 points vs 36.1). High stored energy, an unresolved 09:45 auction, a faint directional
tell. That is mechanically coherent with what the object claims to be, and it is the opposite of
"the big winners were obvious".

> **THE CAVEAT THAT TRAVELS WITH ALL OF §3:** "tail winner" is defined by the P&L of these same 348
> trades. Cross-validation controls overfitting; it does not create a holdout. This is a
> **descriptive** claim about which pre-entry states the big winners came from, **not** a
> demonstration that the next one can be picked in advance. Per the spec, **no filter is built.**

## 4. Decision — status label, no retuning

Per §39, judged on the four questions it names:

| | |
|---|---|
| standalone alpha still positive? | **yes** — $916/wk, N = 348 |
| downside overlap worsening beyond its own null? | **no** — every downside statistic sits at the 5th–33rd percentile |
| still adds fixed-drawdown portfolio value? | **yes** — joint max DD $11,489 (18.9th), joint DD duration 7 weeks vs a null mean of 18.2 |
| is the recent change meaningful? | **the ordinary-ρ rise is real but inside its own four-year range**; the downside statistics did not follow it |

### `XM_CONFLICT` → **ACTIVE COMPONENT** of the candidate portfolio (raised from the reduced-confidence position W105 left it in).

Standing caveats, unchanged and not softened: **N = 348 in a discovery-consumed window**;
**~20 sessions carry 85 % of the money** — now shown to be *mechanism-consistent* rather than
accidental, which changes its interpretation but not its risk; **REGIME_LOCAL by data availability**
(ES/RTY/YM begin 2022-01-02); **the only intra-trade risk control is the clock**, worst adverse
excursion −$10,865, a sample maximum and not a bound; **the trailing 26-week ρ is still the
quantity to watch.**

**Nothing was retuned, restricted or filtered. Two of my own statistics were withdrawn.**
