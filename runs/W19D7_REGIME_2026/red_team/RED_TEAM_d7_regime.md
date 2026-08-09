# RED TEAM — W19D7_REGIME_2026

Independent adversarial review. Every number below was recomputed from the committed substrates;
nothing in the repo was modified except this file. Scratch code ran in the system temp dir.
Seal respected: no data at or after 2026-08-01 was read for any purpose, and no pre-2022 data
was read at all.

---

## VERDICT: **CONFIRMED-WITH-CORRECTIONS** (at the edge of REFUTED)

The run's *primary* answer survives and is in fact **stronger than the report claims**: the
January-May 2026 P&L concentration is not accounted for by any detectable market-structure
change in the pre-registered panel. I corroborated that with an instrument the run never used —
an OLS of the Solar leg's daily net on the seven standardized market variables, fitted 2022-2025,
predicts the stub at **+$172/session against an actual −$72/session** (2022-2025 mean +$110), i.e.
the measured market state says the stub should have been *better* than average. "UNEXPLAINED" is
not merely un-found; it is actively corroborated. But **two of the five headline lines must be
withdrawn or rewritten.** Headline 1 ("no market variable places a changepoint in 2026") is
**true by construction** — the frozen 10% edge exclusion makes the last admissible changepoint
2025-12-18, so the entire 106-session stub lies outside the candidate set and the procedure could
not have returned a 2026 date; I re-ran at a 2% edge and the conclusion happens to survive, so
the claim is right for a reason the report does not give. Headline 2 ("a monotone three-year
trend, not a break") is **contradicted by the model comparison the report asserted but never
ran**: on the full sample BIC prefers a STEP over a linear trend by 66.8 for v6 and 22.3 for v6b,
the two variables the sentence is about, and the report's own yearly table shows both variables
*rising* from 2022 to 2023, which is not monotone. Headline 4's "and badly" and its diversification
corollary are unsupported: the spec-mandated block-bootstrap CIs were not produced, and when
computed they span [−3.39, +2.20] for the Solar leg and [−2.04, +3.22] for Product A — every
object's stub Sharpe is indistinguishable from zero and from every other object's. Separately, an
index-mapping bug puts the headline boundary date 19 sessions early (2024-07-09 → **2024-08-05**),
and the report instructs the successor spec to inherit the wrong date. The run is not REFUTED
because its central null holds; it is not CONFIRMED because two headline sentences are wrong and
a third rests on undelivered uncertainty.

**Defect count: 3 headline-flipping, 8 material, 6 disclosure, 1 cosmetic (18 total).**

---

# DEFECTS

## D1 — HEADLINE-FLIPPING. The changepoint procedure is structurally incapable of placing a break in 2026. Headline 1 is true by construction.

**What is wrong.** `src/panel.py:20` freezes `EDGE = 0.10`, and `src/panel.py:109-120` restricts
candidate locations to `stat` indices `[int(0.1n), int(0.9n))`. For the seven-variable panel
`n = 1139`, so `hi = 1025` and the **last admissible changepoint date is 2025-12-18**. For v2 and
PC1 (`n = 1120`) it is 2025-12-22. The 2026 stub occupies panel indices 1033-1138
(2026-01-02..2026-05-29). **Every session in the window under investigation is excluded from the
candidate set before any data is looked at.**

`REPORT.md:10-12` presents the result as an empirical finding — *"No market variable places a
changepoint in 2026... The 106-session stub is not where the market changed"* — and
`REPORT.md:1` puts it in the title. It is a restatement of the edge rule.

This is not p-hacking: `spec.yaml:63-66` froze the 10% exclusion before any code, for a
defensible reason. It is a design flaw that makes the run unable to answer its own primary
question, compounded by a report that never notices.

**Evidence (re-run).** Relaxing the edge to 5% and 2% — which admits candidate locations inside
the stub — leaves every detecting variable's argmax **unchanged**:

| variable | edge 10% (as run) | edge 5% | edge 2% |
|---|---|---|---|
| v1 realised vol | 2022-11-15 (13.18) | 2022-11-15 | 2022-11-15 |
| v2 vol-of-vol | 2025-01-24 (7.16) | 2025-01-24 | 2025-01-24 |
| v3 range/close | 2024-03-20 (5.48) | 2024-03-20 | 2024-03-20 |
| v6 profile Spearman | 2025-04-02 (13.37) | 2025-04-02 | 2025-04-02 |
| v6b peak/trough | 2024-07-31 (8.56) | 2024-07-31 | 2024-07-31 |
| PC1 | 2024-08-05 (10.28) | 2024-08-05 | 2024-08-05 |

So the substantive conclusion holds. **But the second half of the claim does not.** A
single-changepoint model reports only the *argmax*; "the argmax is elsewhere" is not "nothing
happened here". Evaluated at the 2026 boundary the same statistic is large and would clear each
variable's own bar if that location were tested:

| variable | best CUSUM inside 2026 | date | that variable's own 95% null crit |
|---|---:|---|---:|
| v6 profile Spearman | **9.89** | 2026-01-08 | 4.10 |
| PC1 | **5.87** | 2026-01-14 | 3.64 |
| v6b peak/trough | **4.49** | 2026-01-16 | 3.39 |
| v3 range/close | 3.01 | 2026-03-31 | 3.78 |
| v1 realised vol | 2.19 | 2026-01-28 | 5.60 |

Three of the tests would "detect" a break at the 2026 boundary. With a slowly-moving series,
*every* split point in the second half is significant, which is exactly why the argmax carries no
information about whether 2026 is special.

**Corrected statement.** *"The single-changepoint estimator places its maximum outside 2026 for
every variable. This is partly a property of the frozen 10% edge exclusion, which removes the
last 114 sessions — the entire stub — from the candidate set; the conclusion is unchanged when the
exclusion is relaxed to 2%. It is NOT evidence that nothing changed at the 2026 boundary: the same
CUSUM statistic evaluated there is 9.89 for v6, 5.87 for PC1 and 4.49 for v6b, all above their own
95% bars. The correct reading is that the profile variables are moving continuously and the
single-changepoint machinery cannot distinguish 'the market changed in 2026' from 'the market has
been changing throughout'."*

---

## D2 — HEADLINE-FLIPPING. "The incumbent IS degraded in the stub, and badly" is unsupported, and the spec-mandated CIs that would have shown it were never produced.

**What is wrong.** `spec.yaml:152-153` requires *"net, Sharpe, CDaR_0.95 and trade count by year
and by the §2 split, **each with a block-bootstrap CI**"*. `src/structure.py:138-147` computes no
CI, `out/incumbent_decomposition.csv` contains none, and no trade count is produced either.
`REPORT.md:18-20` and `REPORT.md:126-140` then state the ranking as fact, in bold, with "and
badly" — and `spec.yaml:155-156` had demanded a one-sentence unhedged answer, which the run
delivered by dropping the uncertainty that would have prevented it.

**Evidence (re-run).** Moving-block bootstrap (block 5, B = 4000) on each object's 2026 stub:

| object | n | stub Sharpe | **90% block-bootstrap CI** |
|---|---:|---:|---|
| E10 Solar leg | 106 | −0.387 | **[−3.394, +2.196]** |
| Product A v3 | 106 | +0.659 | **[−2.041, +3.220]** |
| BEST_ONE_NQ v4 | 100 | +0.073 | **[−2.967, +3.165]** |
| ES CONTROL | 106 | −1.045 | **[−4.295, +1.548]** |
| RTY CONTROL | 106 | −0.090 | **[−3.259, +2.533]** |
| YM CONTROL | 106 | −1.020 | **[−4.277, +1.513]** |

Every interval contains zero. Every pair overlaps almost completely. This is arithmetic, not
bad luck: the standard error of an annualized Sharpe on n = 106 sessions is
`sqrt(252/106) = 1.54`, so nothing smaller than ±2.5 is resolvable.

**This re-instates a retracted claim.** `research/system_master/CURRENT_TRUTH.md:247-252` records
the **"2026 edge collapse" narrative as RETRACTED** by the Wave-17 red team, on precisely this
ground (*"BEST_ONE_NQ's 2026 partial net of −$46.60 is 0.001 SE from zero"*), and
`runs/W18R1_M1_VOLSEASON/REPORT.md:211-212` cites that retraction as the reason its own
no-uncertainty framing was wrong. `REPORT.md:212` of this run correctly writes consequence #2
("in-stub challenger comparisons are low-power") — and then exempts its own headline 4 from the
same standard.

**Corrected statement.** *"In the 2026 stub the Solar leg realises −$7,638 over 106 sessions, its
only negative period in the sample, and all three cross-instrument controls are also negative on
net. That sign pattern is worth recording. The Sharpe ordering is not: the 90% block-bootstrap
interval on the Solar leg's stub Sharpe is [−3.39, +2.20] and overlaps Product A's [−2.04, +3.22]
and ES's [−4.30, +1.55]. The stub cannot distinguish a degraded incumbent from an intact one, and
the word 'badly' is not supportable. What IS established is that in-stub comparisons of ANY object
against ANY other — including the ones this report makes — are low-power."*

---

## D3 — HEADLINE-FLIPPING. Product A's stub result is not diversification. Decomposed, roughly half of it is the short-halving overlay and the Solar leg *inside Product A* is positive.

**What is wrong.** `REPORT.md:20` and `REPORT.md:142-146`: *"Product A — the 60/40 blend of the
tilted Solar leg with the unchanged B-MOM leg — holds +0.659 Sharpe and +$11,657 in the same
window where the Solar leg alone runs −0.387 and −$7,638. **The diversification is doing its job
precisely when the primary engine is at its worst.**"* The attribution is asserted; nothing in
`src/structure.py` decomposes Product A, and no output splits it by leg. The spec required no such
decomposition, but the report makes the claim anyway and calls it *"never been demonstrated
before"*.

**Evidence (re-run).** `runs/W18E_PRODUCTA_C4/out/smm_v3_bars.csv` carries per-bar `T`, `Tpp`, `B`
and `phys`, and `src/ninjascript/SolarWaveSMMaster_v3.cs:348` gives the exact aggregation
`M = KSolar*Tpp + KBmom*bmomPos`. That makes an exact linear decomposition of the gross
mark-to-market available. Over the 106-session stub (MNQ, $2/pt, gross of commission; gross total
+$14,388 reconciles with the reported net +$11,657 after ~$2.7k of costs):

| component | stub net | stub Sharpe | share of gross |
|---|---:|---:|---:|
| Solar leg (`KSolar × Tpp`) | **+$6,079** | **+0.456** | 42% |
| B-MOM leg (`KBmom × B`) | **+$8,886** | **+1.163** | 62% |
| rounding / ops residual | −$577 | −0.148 | −4% |

**The Solar leg inside Product A is POSITIVE in the stub.** The report's contrast is not
"Solar leg vs Solar leg + diversifier"; it is "raw E10 target vs tilted-and-short-halved E10
target + diversifier". Isolating the overlay (reconstructed from `T` and `tilt_state`, verified
to match the committed `Tpp` on 100.00% of 519,712 bars):

| Solar-leg variant | stub net | stub Sharpe | 2022-2025 |
|---|---:|---:|---:|
| raw E10 target `T` (no tilt, no scaling) | −$3,012 | −0.152 | — |
| ×0.9026 rescale only | −$2,885 | −0.218 | +$118,432 |
| tilt only | −$1,164 | −0.081 | +$135,997 |
| **short-half only** | **+$4,358** | **+0.359** | +$108,840 |
| as built (tilt + short-half) | +$6,079 | +0.456 | +$126,405 |

**The short-halving alone moves the stub by +$7,243** (−2,885 → +4,358); the tilt alone moves it
+$1,721. So the ~$9k improvement over the plain Solar leg is dominated by a *directional risk
reduction on shorts* — a fitted constant (`ShortHalf = 0.5`, `W18E_PRODUCTA_C4/spec.yaml`
nothing_else_changes block) selected on this same sample — not by combining uncorrelated engines.
Diversification is real and contributes 62% of the gross, but it is one of two mechanisms of
comparable size, and the second is an in-sample-selected overlay.

**Corrected statement.** *"Product A's +$11,657 in the stub decomposes into +$8,886 gross from
the B-MOM leg (Sharpe +1.163) and +$6,079 gross from its own Solar leg (+0.456), less costs. The
Solar leg as Product A actually runs it — tilted and short-halved — is positive in the stub; the
−$7,638/−0.387 figure is the untilted, un-halved E10 control. Of the roughly $9k gap between
them, ~$7.2k comes from the short-halving overlay and ~$1.7k from the tilt. Both the B-MOM
diversification and a fitted directional overlay contribute at comparable scale, and neither
attribution is separable from noise at n = 106 (see D2). The sentence 'the diversification is
doing its job precisely when the primary engine is at its worst' is not what the decomposition
shows and should be withdrawn."*

---

## D4 — MATERIAL. Off-by-19 index bug: the headline boundary date and its CI are wrong, and the report instructs the successor spec to inherit the error.

**What is wrong.** `src/panel.py:135-137` drops non-finite observations (`x = x[ok]`) and then
`src/panel.py:154-156` maps the resulting index back through the **full** panel
(`P["sess"].iloc[k]`, `P["sess"].iloc[int(np.quantile(locs, 0.05))]`). `v2_vol_of_vol` is a
`rolling(20).std()` (`src/panel.py:98`) and therefore has exactly 19 leading NaNs; PC1 is built on
`Z.dropna()` (`src/panel.py:167`) and inherits them. Both series have `n = 1120` against the
panel's 1139 (`out/changepoints.csv`). Every date reported for those two series is **19 sessions
too early**.

**Evidence (re-run).**

| series | reported | **correct** | reported CI | **correct CI** |
|---|---|---|---|---|
| **PC1** | 2024-07-09 | **2024-08-05** | 2024-06-14 .. 2024-08-01 | **2024-07-11 .. 2024-08-28** |
| v2 vol-of-vol | 2024-12-27 | **2025-01-24** | 2023-05-16 .. 2025-07-31 | **2023-06-12 .. 2025-08-27** |

The five variables without NaNs are unaffected.

**Propagation.** `out/boundary.json` carries `"boundary": "2024-07-09"`;
`src/structure.py:24-25` reads it; every BEFORE/AFTER row of `out/d1_diversity.csv`,
`out/incumbent_decomposition.csv` and `out/challenger_diff_decomposition.csv` is cut at the wrong
date; and `REPORT.md:208-210` **mandates it for the successor**: *"The successor selectivity spec
must split at 2024-07-09."*

**Does it matter numerically?** Yes, for three of five rows in `REPORT.md:150-156`:

| comparison (after break, excl. stub) | 2024-07-09 (as reported) | **2024-08-05 (corrected)** | 2024-08-28 (CI top) |
|---|---:|---:|---:|
| M1 arm_FULL − control | +$8,073 | **+$6,898** | +$9,754 |
| M5 NQ blend − control | +$48,243 | **+$39,170** | +$44,586 |
| M5 ES blend − control | −$1,267 | **+$4,747** ← **sign flip** | +$1,138 |
| M5 RTY blend − control | −$1,662 | **−$174** | +$5,676 ← sign flip |
| M5 YM blend − control | +$20,066 | **+$20,377** | +$19,738 |

It also reverses the Solar leg's BEFORE/AFTER ordering: at 2024-07-09, BEFORE Sharpe 0.697 <
AFTER 0.741; at 2024-08-05, BEFORE 0.804 > AFTER 0.630.

The two claims the report makes *in text* — M1 helping at +$8,073 and YM at +$20,066 — both
survive the correction (+$6,898 and +$20,377) and survive across the whole corrected CI. The
table rows for ES and RTY do not.

**Corrected statement.** *"The PC1 changepoint is 2024-08-05, CI 2024-07-11..2024-08-28. All
downstream splits and the successor spec's mandated split date must use 2024-08-05. The ES and
RTY 'after break, excluding stub' figures change sign under the correction and should not be
read as signed results."*

---

## D5 — MATERIAL. The block-5 bootstrap null is badly under-sized for autocorrelated series. "Six of eight detect" overstates; v2's detection is an artifact and v3's is fragile.

**What is wrong.** `src/panel.py:125-129, 142` builds the no-change null by moving-block
resampling the mean-removed series with a **fixed block of 5 sessions** (`spec.yaml:70`, frozen).
A block of 5 cannot reproduce dependence at lags beyond 5, so for a persistent series the null
distribution of the max-CUSUM is far too narrow and the test rejects far too often. `v2` is
literally a **20-session rolling standard deviation**, with lag-1 autocorrelation 0.98 and lag-5
0.84; `v1` has lag-1 0.68.

**Evidence 1 — measured size of the exact procedure on synthetic no-change series** (same
statistic, same block-5 null, same 95% bar, 300 replicates each):

| generating process (no change anywhere) | measured false-positive rate |
|---|---:|
| iid Gaussian (sanity) | 0.043 ✔ calibrated |
| AR(1) ρ = 0.3 | 0.093 |
| AR(1) ρ = 0.5 | 0.163 |
| AR(1) ρ = 0.7 | **0.300** |
| AR(1) ρ = 0.9 | **0.757** |
| AR(1) ρ = 0.98 | **0.993** |
| 20-session rolling sd of an AR(1) — *v2's own construction* | **0.780** |

**Evidence 2 — block-length sweep on the actual series.** Detected (stat > own 95% crit):

| variable | ac(1) | b=1 | b=5 (as run) | b=10 | b=20 | b=40 | b=80 | b=160 |
|---|---:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| v1 realised vol | 0.68 | Y | Y | Y | Y | Y | Y | n |
| **v2 vol-of-vol** | **0.98** | Y | **Y** | **n** | **n** | **n** | **n** | **n** |
| v3 range/close | 0.19 | Y | Y | Y | Y | n | n | n |
| v4 autocorr | −0.04 | n | n | n | n | n | n | n |
| v5 excursion | −0.05 | n | n | n | n | n | n | n |
| v6 profile Spearman | 0.22 | Y | Y | Y | Y | Y | Y | **Y** |
| v6b peak/trough | 0.08 | Y | Y | Y | Y | Y | Y | **Y** |
| PC1 | 0.13 | Y | Y | Y | Y | Y | Y | **Y** |

v2 detects only at blocks shorter than its own 20-session construction window. At block 10 its
critical value is 9.11 against a statistic of 7.16.

**Evidence 3 — Bonferroni over the 7 variable tests** independently kills the same one variable:
v2 (p = 0.027 vs 0.05/7 = 0.0071). All four strong detections have p < 0.001 and survive.

**Evidence 4 — HAC standard errors on the §(b) shift table.** `REPORT.md:82-84` names four
shifts clearing |Welch t| > 4. Recomputed at the corrected 2024-08-05 boundary with Newey-West:

| variable | Welch t (iid, as reported) | HAC L=20 | HAC L=60 | HAC L=120 |
|---|---:|---:|---:|---:|
| v2 vol-of-vol | +5.90 | **+1.51** | **+1.24** | **+1.28** |
| v3 range/close | +4.89 | +3.13 | +2.95 | +3.16 |
| v6 profile Spearman | −13.86 | −7.97 | −6.11 | −5.16 |
| v6b peak/trough | −9.37 | −8.23 | −8.21 | −9.34 |

Only v6 and v6b survive an autocorrelation-robust standard error. `REPORT.md:87` — *"its intraday
shape flattened **and its variability rose**"* — the second half rests entirely on v2 and is not
supported.

**Corrected statement.** *"Four detections are robust to block length up to 160 sessions and to
Bonferroni (v1, v6, v6b, PC1); one is marginal (v3, lost beyond block 20 and reduced to HAC
t ≈ 3.0); one (v2) is an artifact of a bootstrap block shorter than the 20-session window the
variable is built from and must be withdrawn. Two do not detect. The count is 4 robust + 1
marginal, not 6 of 8. Of the shifts across the boundary, only the two profile variables survive
autocorrelation-robust inference; 'its variability rose' is withdrawn."*

*(Fairness note: I also ran a phase-randomized-surrogate size estimate, which gave a mean FPR of
0.82 and would imply 6.58 expected detections out of 8 — i.e. that the whole result is chance. I
do **not** rely on it: a phase-randomized surrogate inherits the low-frequency spectral power that
a genuine step itself creates, so that test is biased against the procedure. The block-length
sweep and the AR(1) size table above are the honest instruments, and they leave v1/v6/v6b/PC1
standing.)*

---

## D6 — MATERIAL. The "estimated boundary" moves by 18 months under leave-one-variable-out. It is not an estimate.

**What is wrong.** `REPORT.md:46-50` reports PC1's changepoint with a ~7-week CI and adopts it as
*"the estimated boundary... used for every downstream split"*. `REPORT.md:201-203` discloses that
PC1 explains only 27.3% of variance, but never tests variable-selection sensitivity — which
`spec.yaml:190-193` explicitly instructed the red team to do.

**Evidence (re-run, with the D4 NaN mapping fixed).**

| dropped variable | explained var | PC1 changepoint | stat |
|---|---:|---|---:|
| (none, all 7) | 0.273 | 2024-08-05 | 10.28 |
| − v1 realised vol | 0.307 | 2024-08-01 | 12.01 |
| − v2 vol-of-vol | 0.317 | 2024-08-05 | 10.53 |
| − v3 range/close | 0.283 | 2024-08-05 | 10.24 |
| − v4 autocorr | 0.316 | 2024-08-05 | 10.40 |
| − v5 excursion | 0.295 | 2024-08-05 | 10.45 |
| **− v6 profile Spearman** | 0.278 | **2023-02-07** | 10.37 |
| **− v6b peak/trough** | 0.264 | **2023-02-14** | 10.52 |

**Spread = 545 calendar days**, against a reported CI of 49 days. Note the statistic stays at
~10.4 in every case — detection is stable, *location* is not. The boundary is entirely a property
of the two profile-shape variables; drop either and it jumps back 18 months.

PC1 is also not a summary of seven things: `corr(PC1, −(v6+v6b)/2) = 0.850`, PC1 explains 27.3%
against PC2's 21.3%.

**On the CI construction itself I could not find a fault** — see "could not break" item 5; its
coverage under a true step is 0.80-0.885 against a nominal 0.90. The problem is not the CI's
arithmetic but that it conditions on a model and a variable set whose contribution to uncertainty
is 11× larger and is unreported.

**Corrected statement.** *"The PC1 boundary of 2024-08-05 is not robust to variable selection:
removing either profile variable moves it to February 2023, a spread of 545 days against a
within-model CI of 49 days. PC1 correlates 0.850 with −(v6+v6b)/2 and explains 27.3% of variance
against PC2's 21.3%. The honest object is 'the intraday volatility profile flattened somewhere in
2023-2025', not a dated boundary, and no downstream split should be pre-registered on 2024-08-05
as though it were located."*

---

## D7 — MATERIAL. The trend-versus-break claim is the report's central methodological move, is asserted rather than tested, and mostly fails when tested.

**What is wrong.** `REPORT.md:12-13` and `REPORT.md:52-68`: *"What the profile variables actually
show is a monotone three-year trend, not a break — and a step model fitted to a ramp lands in the
middle of the ramp, which is what happened."* No model comparison appears anywhere in
`src/panel.py`, `src/structure.py` or `out/`.

**Evidence 1 — the word "monotone" is false and the report's own table two lines below
disproves it.** `REPORT.md:58-59`: v6 goes 0.4446 → **0.4866** (2022→2023) before falling; v6b
goes 10.66 → **11.12**. Both *rise* first. (The claim is only true if "three-year" silently means
2023-2026, which is a different object from the 2022-2026 sample the changepoint was fitted on.)

**Evidence 2 — BIC, full 2022-2026 sample** (step charged an extra parameter for τ; lower is
better):

| variable | const | **STEP** | **TREND** | trend+step | winner | ΔBIC(step − trend) |
|---|---:|---:|---:|---:|:--|---:|
| v1 realised vol | −5563.1 | −5737.7 | −5602.4 | −5743.5 | trend+step | −135.4 |
| v2 vol-of-vol | −7309.4 | −7347.9 | −7302.8 | −7420.4 | trend+step | −45.1 |
| v3 range/close | −5678.9 | −5695.3 | −5691.4 | −5688.7 | STEP | −3.9 |
| v4 autocorr | −5786.0 | −5773.5 | −5778.9 | −5767.7 | const | +5.4 |
| v5 excursion | 4294.2 | 4301.7 | 4299.3 | 4307.6 | const | +2.4 |
| **v6 profile Spearman** | −5061.6 | **−5242.1** | −5175.3 | −5235.8 | **STEP** | **−66.8** |
| **v6b peak/trough** | 3783.8 | **3722.1** | 3744.4 | 3727.9 | **STEP** | **−22.3** |
| PC1 | 737.9 | 640.8 | 641.5 | 642.4 | tie | −0.6 |

For the two variables the sentence is about, **a step beats a linear trend decisively** (ΔBIC > 10
is conventionally "very strong"). PC1 is a genuine tie. Only when the sample is restricted to
2023-2026 does v6 flip to preferring trend (ΔBIC +13.4) — while v6b still prefers step (−11.2).
The claim is sample-dependent and was never tested either way.

**Evidence 3 — the ramp mechanism the report invokes.** Simulating `fitted linear trend +
block-resampled residuals` and refitting the step, 2000 replicates, gives the distribution of
where a step estimator lands on a genuine ramp:

| variable | observed cp | sample midpoint | ramp-null argmax 5/50/95% | observed percentile |
|---|---|---|---|---:|
| PC1 | 2024-08-05 | 2024-04-01 | 2023-05-01 / 2024-03-25 / 2025-02-26 | 0.731 |
| v6b peak/trough | 2024-07-31 | 2024-03-15 | 2023-01-03 / 2024-03-06 / 2025-06-13 | 0.686 |
| **v6 profile Spearman** | 2025-04-02 | 2024-03-15 | 2023-01-31 / 2024-03-05 / 2025-05-01 | **0.931** |

The ramp story is consistent with PC1 and v6b. It is a **poor** account of v6 — the variable with
the largest statistic in the whole panel — whose estimate sits at the 93rd percentile of what a
ramp would produce. (Analytically, on a pure ramp the CUSUM argmax is at the *sample* midpoint, so
"lands mid-ramp" predicts 2024-03/04, not the observed dates.)

**Evidence 4 — quarterly means favour a mid-2024 level change over a continuing ramp for v6b:**
2024Q2 11.22 → 2024Q4 8.27, then 8.90 / 7.59 / 8.79 / 8.56 / 7.94 / 7.57 through 2026Q2.

**Corrected statement.** *"Neither model is clearly right and the report should not have picked
one by assertion. Over the full sample BIC prefers a step to a linear trend for both profile
variables (ΔBIC 66.8 and 22.3); restricted to 2023-2026 it prefers a trend for v6 and a step for
v6b. The two variables are not monotone over 2022-2026 — both rise from 2022 to 2023. The 'step
fitted to a ramp lands mid-ramp' explanation is consistent with PC1 and v6b but not with v6,
whose estimate sits at the 93rd percentile of the ramp null. The defensible statement is: the
intraday volatility profile is materially flatter in 2025-2026 than in 2022-2024, and the data do
not identify whether it moved by a step or a drift."*

---

## D8 — MATERIAL. "All-13-agree is at its lowest in 2026" reverses the sign of the spec's own metric.

**What is wrong.** `spec.yaml:127` defines the metric as *"fraction of bars on which all 13
members agree in sign"* — unconditional. `src/structure.py:65-67` computes
`frac_all13_agree_given_all_nonzero`, i.e. **conditional on all 13 members being simultaneously
non-flat**, which happens on only 1.8-3.1% of bars (`out/d1_diversity.csv`,
`frac_bars_all13_nonzero`). `REPORT.md:94-100` prints the conditional number under the column
header "all-13-agree" with no indication of the conditioning, and `REPORT.md:104` concludes
*"agreement is at its lowest"*.

**Evidence (re-run from the member simulation).**

| year | P(all 13 non-zero) | P(agree \| all non-zero) — *as reported* | **P(all 13 agree) — as SPECIFIED** |
|---|---:|---:|---:|
| 2022 | 0.0307 | 0.8944 | **0.0275** |
| 2023 | 0.0194 | 0.8595 | 0.0167 |
| 2024 | 0.0182 | 0.8848 | 0.0161 |
| 2025 | 0.0217 | 0.8216 | 0.0179 |
| **2026** | 0.0273 | **0.8082** ← lowest | **0.0221** ← **second highest, +23% over 2025** |

On the spec's own definition, all-13 agreement **rises** in 2026 — the direction the pre-registered
collapse hypothesis predicted. (`out/d1_diversity.csv`'s `frac_target_at_pm10_cap` moves the same
way, 1.79% → 2.21%, and the report prints it in the adjacent column without noting that the two
columns disagree in direction.)

**The REJECTION itself survives** — see "could not break" item 7 — but on the participation ratio
alone, and the report's second supporting fact points the other way.

**Corrected statement.** *"Effective diversity does not collapse: the participation ratio is 3.521
in 2026 with a 90% block-bootstrap band of [3.202, 3.814], overlapping 2022 (3.370 [3.176, 3.576])
and 2025 (3.776 [3.550, 4.006]); on equal-length 48,341-bar sub-windows the 2022-2025 medians are
3.60/3.60/3.82/3.89, so 2026 is lowest but by less than a within-year band. The member-collapse
hypothesis is REJECTED on that metric. The evidence is mixed, not one-sided: on the spec's own
definition the all-13-agree fraction RISES in 2026 to 2.21%, its second-highest value, as does the
±10-cap rate. The 0.808 figure in the report is the fraction agreeing conditional on all 13 being
non-flat, which is true of only 2.7% of bars, and must be labelled as such."*

---

## D9 — MATERIAL. "The standing figure had no written definition anywhere in the repo" is false. The identification is correct and unique, but it is not new.

**What is wrong.** `REPORT.md:107-109`: *"The standing figure quoted in the directives
(9.8 / 0.2 / 3.9 / 18.3 / 39.2%) **had no written definition anywhere in the repo**. It is now
identified exactly."* It did.

**Evidence.** `research/system_master/CURRENT_TRUTH.md:513-515`: *"The 1200t/300pt clamp on
**the slowest member (VolMult=30)** binds 39.2% of Jan-May 2026 bars vs 9.8%/0.2%/3.9%/18.3% in
2022-2025 (SMV2R sub_381)."* And `research/system_master/INDICATOR_FRONTIER.md:52-54`: *"1200t cap
ACTIVELY binds slow members (**vm30** 10.9% of dev bars; partial-2026 highest at 39.2%)."* Both
already attribute it to VolMult = 30, with a provenance.

**What IS new and correct.** I enumerated 28 candidate definitions (each member's instantaneous
`vm × σ460 ≥ 1200t`, each member's resampled `s_eff` pinned rate, any-member, all-member, pooled
member-bars) and **exactly one reproduces the standing figure**:

| definition | 2022 | 2023 | 2024 | 2025 | 2026 | max dev from standing |
|---|---:|---:|---:|---:|---:|---:|
| **instantaneous 30 × σ460 ≥ 1200t** | **9.825** | **0.156** | **3.931** | **18.256** | **39.213** | **0.044** ✔ unique |
| VM=30's *resampled* `s_eff` pinned | 13.610 | 2.814 | 7.956 | 21.222 | 50.113 | 10.9 |
| any member `s_eff` pinned | 13.612 | 2.814 | 7.956 | 21.413 | 50.642 | 11.4 |
| pooled member-bars pinned (13) | 3.394 | 0.216 | 2.223 | 6.589 | 12.944 | 26.3 |
| VM=28 instantaneous | 6.390 | 0.064 | 3.173 | 15.520 | 32.006 | 7.2 |

So the report's reproduction claim holds and the identification is unique. But the report's
*contrast* is slightly muddled: 39.2% is **neither** the ensemble rate (12.9%) **nor** VM=30's
actual pinned rate (50.1%). Because `s_eff` is resampled only at trend flips
(`src/analytics/sm01_solarsim.py:29-30`), the instantaneous exceedance is not the rate at which
any member's threshold is actually constrained. There are three numbers here, not two.

**Corrected statement.** *"The standing figure is the instantaneous rate at which the widest
member's uncapped 30×σ460 exceeds the 1200-tick ceiling. This was already recorded, correctly, at
CURRENT_TRUTH.md:513-515 and INDICATOR_FRONTIER.md:52-54; this run confirms it and shows the
identification is unique among 28 candidate definitions. What is genuinely new is that it is also
not VM=30's realised pinned rate: because s_eff is resampled only at flips, VM=30's threshold is
actually pinned on 50.1% of 2026 bars while the ensemble member-bar rate is 12.9%. Three
quantities, spanning 4×, are in circulation; any future use must name which."*

---

## D10 — MATERIAL. `out/clamp_definitions.csv` is written by no committed script — the identical defect the previous wave's red team raised.

`src/` contains only `panel.py` and `structure.py`. Neither writes `clamp_definitions.csv`;
neither produces the columns `raw_S_uncapped_gt_1200t_pct` or `top_member_vm30_pinned_pct`. A
repo-wide grep for `raw_S_uncapped` hits **only the CSV itself**. `spec.yaml:195-197` lists the
run's outputs and does not include this file either — it was added after the spec was frozen, by
uncommitted code.

The whole of `REPORT.md:107-119` — a section the report elevates to a standing caution
(`REPORT.md:216-218`) — rests on it. I reproduced the numbers independently (D9), so the content
is right; the run as committed cannot reproduce its own output.

This is precisely the defect `runs/W18R1_M1_VOLSEASON/red_team/RED_TEAM_m1_volseason.md` raised as
D10 one wave earlier (`root_cause_S_freeze.csv` written by no committed script). It recurred.

**Corrected action.** Commit the generating script, or mark the table as externally verified with
the reproduction recipe stated.

---

## D11 — MATERIAL. "Independently corroborates the M5 red team" — it is not independent.

`REPORT.md:158-162`: *"YM ... is positive in that same interval (+$20,066) ... That **independently
corroborates** the M5 red team's finding that which instruments agree is period-dependent."*

The YM figure is a re-slicing of `runs/W18R2_M5_XINST/out/curves_all.csv`
(`src/structure.py:124-134, 172-178`) — the **same file** the M5 red team used to build its own
period-dependence table. That table
(`runs/W18R2_M5_XINST/red_team/RED_TEAM_m5_xinst.md:83-101`) already contains the yearly ΔSharpe
grid including YM 2026 = −0.0897, and states the conclusion verbatim: *"Which instruments 'agree'
is period-dependent — 2022-2023: ES ✓, RTY ✓, NQ ✗, YM ✗; 2024-2026: ES ✓, YM ✓, NQ ✓, RTY ✗.
Only ES is stable across sub-periods."*

Same data, a different cut. It corroborates; it does not do so independently. And the interval
it is computed over is 19 sessions wrong (D4) — though the figure survives the correction
(+$20,377).

**Corrected statement.** *"...which is a further cut of the same curves the M5 red team used, and
is consistent with — not independent evidence for — its finding that the identity of the agreeing
instruments is period-dependent."*

---

## D12 — DISCLOSURE. Undeclared deviation from the frozen spec on bootstrap size.

`spec.yaml:70` freezes **B = 10,000**. `src/panel.py:19` sets `NBOOT = 10000` and then never uses
it: `src/panel.py:142` hard-codes `range(1000)`. `REPORT.md:34` says "1,000 replicates" — so the
number is disclosed, but not that it departs from a frozen spec. Consequence: the smallest
attainable p-value is 0.001, which is what every "p = 0.000" in `REPORT.md:39-46` and
`out/changepoints.csv` actually means. At B = 10,000 the Bonferroni-corrected comparison in D5
would have had ten times the resolution.

---

## D13 — DISCLOSURE. Five spec-mandated deliverables were not produced.

| requirement | where frozen | delivered? |
|---|---|---|
| "bootstrap CIs on each period mean" | `spec.yaml:112-113` | **No** — `out/variables_by_period.csv` has mean/shift/Welch t only |
| "the standardized distance of the 2026 period from the 2022-2025 pooled distribution" | `spec.yaml:113-114` | **No** |
| "net, Sharpe, CDaR_0.95 and **trade count** ... each with a block-bootstrap CI" | `spec.yaml:152-153` | **No CIs, no trade count** |
| seal-audit **verdict pasted into the report** | `spec.yaml:182-185` | **No** — `REPORT.md:220-223` points at `out/seal_audit.csv`, which has no verdict row |
| "any artifact whose contents extend past 2026-05-29 is **listed by name** with the slice applied" | `spec.yaml:185-186` | **No** — `runs/AUDIT03_BARS/nq_3m_2022_2026.csv` (max ts 2026-07-31, class `CONSUMED (disclose)`) is never named in the report text |

The last one matters most: the run *did* correctly slice it (`src/panel.py:25`,
`runs/W18R1_M1_VOLSEASON/src/common.py:load_dev_bars`), and I verified the slice, but the
disclosure the owner directive R4 demanded is in a CSV rather than in the report.

I supply the two missing quantitative items in D2 (CIs) and "What is missing" (standardized
distance).

---

## D14 — DISCLOSURE. Sharpe denominators are not comparable across the §(d) objects.

`daily_from_fills` (`src/structure.py:89-104`) produces a row only for sessions that had fills.
BEST_ONE_NQ has **61 missing sessions** across the sample (n = 247/246/246/239/100 against the
Solar leg's 258/258/259/258/106), so its Sharpes are computed on fill-days only and annualized
with `sqrt(252)` regardless. Zero-filling to the full session calendar:

| year | as reported | zero-filled |
|---|---:|---:|
| 2022 | +1.901 | +1.860 |
| 2023 | +0.731 | +0.714 |
| 2024 | +1.409 | +1.373 |
| 2025 | +1.176 | +1.132 |
| **2026** | **+0.073** (n=100) | **+0.071** (n=106) |

Immaterial in size, but the 2026 row is the one being set beside a 106-session Solar leg in
`REPORT.md:130-131`, and BEST_ONE's stub ends 2026-05-28 rather than 2026-05-29. Product A's index
is identical to the control's on all 1,139 sessions, so it is unaffected.

---

## D15 — DISCLOSURE. The novelty test has no resolution.

`src/panel.py:226-251` builds the reference distribution from 1,034 rolling 106-session windows
stepped **1 session**. Over 1,139 sessions that is **≈10.7 independent windows**. A
95th-percentile bar estimated from ~10 effective observations cannot distinguish 88.6 from 95, and
the pre-registered novelty test (`spec.yaml:167-171`) therefore has essentially no power in either
direction. The NOT-NOVEL verdict happens to be robust for other reasons (see "could not break"
item 6), but not because this test established it.

Minor related note: `src/panel.py:242-247` includes the target window itself in the reference
distribution.

---

## D16 — DISCLOSURE. The named analog is not stable, yet consequence #3 pre-registers that exact window as the Wave-20 test.

`REPORT.md:214-215`: *"The 2025-04-25 .. 2025-09-19 analog is the Wave-20 test."* Re-running the
identical search at other window lengths and with distributional rather than mean summaries:

| variant | nearest analog | distance | percentile | novel? |
|---|---|---:|---:|:--|
| WIN = 40 | 2025-05-06 .. 2025-06-30 | 0.253 | 0.152 | no |
| WIN = 60 | **2025-10-02 .. 2025-12-24** | 0.472 | 0.702 | no |
| WIN = 80 | **2025-10-16 .. 2026-02-06** | 0.444 | 0.648 | no |
| **WIN = 106 (as run)** | **2025-04-25 .. 2025-09-19** | 0.683 | 0.886 | no |
| WIN = 130 | 2025-04-22 .. 2025-10-20 | 0.574 | 0.736 | no |
| WIN = 150 | 2025-04-02 .. 2025-10-29 | 0.642 | 0.737 | no |
| WIN = 180 | **2024-07-22 .. 2025-04-01** | 0.687 | 0.604 | no |
| mean + sd (WIN 106) | **2025-07-31 .. 2025-12-26** | 0.763 | 0.689 | no |
| mean + sd + skew | 2025-05-12 .. 2025-10-06 | 1.370 | 0.415 | no |
| deciles | 2025-07-31 .. 2025-12-26 | 2.673 | 0.800 | no |

The *episode* is stable — it is 2025, mostly H2 — but the specific 106-day window is not, moving by
up to six months. Pre-registering a Wave-20 test on those exact dates is false precision.

**Corrected statement.** *"The nearest analog is somewhere in 2025, most often H2-2025; the
specific window depends on the window length and the summary statistic and ranges from
2025-04-02..2025-10-29 to 2025-10-16..2026-02-06. A Wave-20 analog test should be specified over
calendar-2025 as a whole, or its window length pre-registered with a sensitivity band, not on the
single 2025-04-25..2025-09-19 cut."*

---

## D17 — DISCLOSURE. Causal and mechanistic language, which the spec's own §1 makes a defect.

`spec.yaml:48-53` — *"Any causal language in the report is a defect and the red team is instructed
to hunt for it."* Found, in descending severity:

1. **`REPORT.md:122-124`** — *"The clamp is **squeezing** the ensemble from the top without
   collapsing it: the widest members are **truncated toward a common value** while **enough**
   distinct members remain below the ceiling **to preserve diversity**."* A causal mechanism, an
   unmeasured quantitative claim ("truncated toward a common value" is computed nowhere in `out/`),
   and a teleology ("to preserve"). This is the clearest instance in the document.
2. **`REPORT.md:145`** — *"The diversification is doing its job precisely when the primary engine
   is at its worst."* Causal attribution, refuted by D3.
3. **`REPORT.md:1`** (title) — *"**The market's break is in mid-2024**"*, asserting an event whose
   existence is one of two competing models (D7) and whose date is variable-selection-dependent
   (D6) and 19 sessions wrong (D4).
4. **`REPORT.md:27-28`** — *"**What replaces the break story** is a slower and less dramatic one —
   a multi-year drift plus a hard-binding clamp."* Offers a replacement *explanation* for a P&L
   pattern in a run whose spec says it cannot establish one. The sentence that follows hedges, but
   the framing has already been made.
5. **`REPORT.md:64-65`** — *"PC1's 2024-07-09 is consistent with **exactly that**."* Asserted; only
   partly true when tested (D7).
6. **`REPORT.md:71-72`** — *"— **the end of the 2022 high-volatility period**"*, a market narrative
   attached to a changepoint on co-occurrence alone.
7. **`REPORT.md:87`** — *"its variability rose"*, not supported under HAC (D5).
8. **`REPORT.md:161-162`** — *"**it means** the sign count was never a stable property"*, an
   inference drawn from a single interval computed at the wrong boundary date.

To the report's credit, `REPORT.md:190-204` ("What this run does NOT establish") is a genuinely
strong disclaimer section and states the co-occurrence limitation correctly. The defect is that
the body does not honour it.

---

## D18 — COSMETIC. "Six of eight" counts PC1 as an eighth test.

`REPORT.md:10, 48` and `out/boundary.json` (`"n_variables": 8`) count PC1 alongside the seven
variables. PC1 is a linear combination of those seven: `corr(PC1, −(v6+v6b)/2) = 0.850`. It is a
restatement, not independent evidence. (The spec's own trigger clause, `spec.yaml:76-78`, is
phrased over "the variables" — 5 of 7 detect as run, 4-5 of 7 after D5's corrections, so the
clause correctly does not fire either way.)

---

# WHAT I TRIED TO BREAK AND COULD NOT

These are as load-bearing as the defect list. Each is an attack that failed.

**1. `daily_from_fills` — the highest-severity thing available, and it is correct.**
Both reconciliations are exact:
- Product A over 2022-01-01..2026-05-29: **$175,798.80** against the committed NT8 net
  **$175,798.80**.
- BEST_ONE_NQ: **$303,239.64** against **$303,239.64**.

Both assumptions verified directly, not assumed:
- *Flat at every session close*: net signed quantity per session is **exactly 0 on all 1,139
  Product A sessions and all 1,078 BEST_ONE sessions**, max |residual| = 0, cumulative position at
  the last fill = 0.
- *The `hour >= 18` roll rule*: **no fill in either ledger occurs at hour 18 minute 0** (the only
  boundary case that could mis-assign), and Product A's resulting session index is **identical**
  to the independently-constructed `daily_control.csv` index on all 1,139 sessions.

**§(d)'s P&L table is not wrong.** Its uncertainty (D2) and its Sharpe denominators (D14) are the
problems, not its arithmetic.

**2. v6's reference-profile circularity — the attack I expected to land, and it does not.**
Rebuilt v6 from the bars under four alternative references. Yearly means:

| year | pooled 2022-25 (as run) | 2022 only | 2022-2023 only | all incl. 2026 | **leave-one-YEAR-out** |
|---|---:|---:|---:|---:|---:|
| 2022 | 0.4446 | 0.4497 | 0.4488 | 0.4435 | 0.4378 |
| 2023 | 0.4866 | 0.4851 | 0.4896 | 0.4857 | 0.4827 |
| 2024 | 0.4505 | 0.4442 | 0.4470 | 0.4501 | 0.4482 |
| 2025 | 0.3928 | 0.3833 | 0.3853 | 0.3938 | 0.3900 |
| **2026** | **0.3370** | **0.3305** | **0.3321** | **0.3415** | **0.3370** |

Identical pattern under every variant, including a reference built only from 2022. The
circularity does not manufacture the decline. Confirmed again by a fully symmetric year×year
Spearman matrix of the mean profiles (no circularity possible): 2022-vs-2026 = 0.899,
2025-vs-2026 = 0.937, monotone in year distance.

**3. v6 as a volatility or bar-count artifact.** The time trend survives controls:
`v6 ~ time` gives t = −11.27; `v6 ~ time + log(realised vol) + n_bars` gives t(time) = **−12.04**.
Bars per session are flat by year (mean 456.6/456.3/456.9/455.5/456.1). The profile drift is real.

**4. The clamp identification.** Unique among 28 candidate definitions to two decimal places
(D9). The report's reproduction claim is exactly right.

**5. The location-CI construction.** I simulated coverage under a *true* step with residuals drawn
from the real series: 0.885 (v6), 0.865 (PC1), 0.800 (v1) against nominal 0.90 — mild
under-coverage, not a broken construction. Resampling residuals at block 20 instead of 5 gives
0.850. The CI is sound conditional on the model; D6 is about the model, not the CI.

**6. The NOT-NOVEL conclusion.** Holds at every window length from 40 to 180 sessions and under
every distributional summary I tried (mean; mean+sd; mean+sd+skew; 10 deciles per variable) —
percentile 0.415 to 0.886, never above the 0.95 bar (table in D16). The report's disclosed
asymmetry is also genuine and genuinely conservative: the target is the terminal window and can
only look backwards, which biases its nearest-neighbour distance upward, toward more apparent
novelty. It came out not-novel anyway.

**7. The member-collapse REJECTION.** Survives every way I attacked it.
- *Is the participation ratio sensible on {−1,0,+1} positions?* Yes: on synthetic 13-member
  ensembles it returns **1.000** when fully collapsed, **12.997** when fully independent, and is
  monotone in between (90%/80%/70%/60%/50% common-signal share → 1.47 / 2.19 / 3.35 / 5.07 / 7.45).
  The observed 3.4-3.9 corresponds to ~70% common-signal share.
- *Is 3.52 vs 3.93 inside the noise?* Block bootstrap (block = 1 session, B = 400): 2026 **3.521
  [3.202, 3.814]**; 2022 3.370 [3.176, 3.576]; 2023 3.605 [3.390, 3.798]; 2024 3.933 [3.696, 4.159];
  2025 3.776 [3.550, 4.006]. 2026 overlaps 2022, 2023 and 2025.
- *Is the 106-session sample length doing it?* No. On random contiguous 48,341-bar sub-windows the
  other years give medians 3.596 / 3.599 / 3.820 / 3.887 with 5-95% bands up to 0.74 wide. 2026 is
  the lowest but by less than a within-year band.

No collapse. D8 corrects a supporting fact, not the verdict.

**8. The two P&L claims the report makes in text.** M1 "helping between the break and the stub"
and YM "positive in that same interval" both survive the D4 boundary correction and the entire
corrected CI range 2024-07-11..2024-08-28: M1 +$6,898 to +$9,754 (reported +$8,073); YM +$19,738 to
+$20,476 (reported +$20,066).

**9. Family-wise error.** Bonferroni at 0.05/7 removes exactly one detection (v2, p = 0.027) — the
same variable the block-length sweep removes. The four strong detections (p < 0.001) survive. The
detections are not a multiple-testing artifact.

**10. The seal.** `out/seal_audit.csv` correctly classifies `runs/AUDIT03_BARS/nq_3m_2022_2026.csv`
as `CONSUMED (disclose)` (max ts 2026-07-31), and both scripts slice to `DEV_END = 2026-05-29`
before any computation (`src/panel.py:18, 25`; `runs/W18R1_M1_VOLSEASON/src/common.py:22, 27-31`).
No locked-forward read. My own review touched nothing at or after 2026-08-01 and read no pre-2022
data. The defect is the missing disclosure in the report text (D13), not the practice.

---

# WHAT IS MISSING

**1. The second half of the run's own pre-registered null was never computed.**
`spec.yaml:37-41` defines the null as *"no variable's changepoint statistic clears its own
bootstrap bar, **and** the period's standardized feature vector is not an outlier against the rest
of the dev window"*. No outlier test appears anywhere in `src/` or `out/`. I ran it: the
Mahalanobis D² of the 2026 stub's mean standardized vector against all earlier 106-session
windows is **11.62, at the 93.6th percentile** — just under a 95% bar, and subject to the same
~10-effective-windows resolution limit as D15. The stub is mildly unusual multivariately, which is
neither the report's "nothing changed" framing nor an outlier finding, and it should have been
stated.

**2. The report never asks whether the panel explains the P&L — and it is the strongest result
available.** Regressing the E10 Solar leg's daily net on the seven standardized variables, fitted
on 2022-2025 and evaluated on the stub (LHS is P&L, so this does not define the regime from P&L
and does not violate the D5 rule — it *tests* the D5-clean panel):

| | |
|---|---|
| in-sample R² (2022-2025) | 0.0357 |
| 2022-2025 actual mean daily net | +$110.68 |
| **2026 stub actual** | **−$72.05/session (−$7,638 total)** |
| **2026 stub PREDICTED from the market panel** | **+$172.14/session (+$18,247 total)** |

The panel predicts the stub should have been **better than average**. Product A the same:
actual +$109.97/session, predicted +$320.84. This is a far stronger and more useful statement of
the run's central finding than the one the report makes — the concentration is not merely
un-explained, it runs *opposite* to what the pre-registered market variables would predict.

**3. Almost the entire "market change" is one variable.** Standardized distance of the 2026 stub
mean from the 2022-2025 pooled mean, per variable:

| variable | z (sd) | Welch t |
|---|---:|---:|
| **v6 profile Spearman** | **−0.990** | **−9.30** |
| **v6b peak/trough** | **−0.426** | **−6.01** |
| v3 range/close | +0.150 | +1.39 |
| v1 realised vol | +0.129 | +1.70 |
| v5 excursion length | −0.123 | −1.59 |
| v4 autocorr | −0.006 | −0.06 |
| v2 vol-of-vol | −0.001 | −0.02 |

Five of seven variables put the stub within 0.15 sd of the 2022-2025 mean. The panel is not seven
pieces of evidence about a regime; it is one measurement (profile flatness, with a second variable
correlated 0.444 to it) plus five nulls. `REPORT.md:53-55` gestures at this — "the two strongest
detections are both profile-shape variables" — but the report then presents the eight-row
changepoint table as if it were eight findings.

**4. Uncertainty, generally.** No CIs on any period mean (D13), on any participation ratio (D8),
on any Sharpe (D2), or on any per-variable trend. I have supplied all four.

**5. Trade counts**, required by `spec.yaml:152` and absent everywhere.

**6. The seal-audit verdict text and the named CONSUMED artifact** (D13).

---

# SUMMARY TABLE

| # | severity | one line |
|---|---|---|
| D1 | headline-flipping | The 10% edge exclusion removes the whole 2026 stub from the candidate set; headline 1 is true by construction (though it survives at a 2% edge) |
| D2 | headline-flipping | "Incumbent degraded, and badly" — spec-mandated CIs omitted; when computed, every stub Sharpe CI contains zero and they all overlap |
| D3 | headline-flipping | Product A's stub result is ~half short-halving overlay, not diversification; the Solar leg *inside* Product A is +0.456 |
| D4 | material | Off-by-19 NaN index bug: PC1 boundary is 2024-08-05, not 2024-07-09; two table rows flip sign; the wrong date is mandated for the successor |
| D5 | material | Block-5 null is under-sized for autocorrelated series (measured FPR 0.76-0.99 at ρ≥0.9); v2's detection is an artifact; only v6/v6b survive HAC |
| D6 | material | Boundary moves 545 days under leave-one-variable-out, against a 49-day CI |
| D7 | material | Trend-vs-step is asserted, never tested; BIC prefers STEP for both named variables by 66.8 and 22.3; "monotone" is false |
| D8 | material | "All-13-agree at its lowest" is the conditional statistic; on the spec's definition it is second-highest and rising |
| D9 | material | "No written definition anywhere in the repo" is false (CURRENT_TRUTH.md:513-515); the identification is nonetheless correct and unique |
| D10 | material | `clamp_definitions.csv` written by no committed script — a repeat of the previous wave's D10 |
| D11 | material | "Independently corroborates" the M5 red team — same file, different cut |
| D12 | disclosure | B = 1,000 against a frozen B = 10,000, not labelled a deviation |
| D13 | disclosure | Five spec-mandated deliverables missing (period-mean CIs, standardized distance, Sharpe CIs, trade counts, seal verdict + named artifact) |
| D14 | disclosure | BEST_ONE_NQ Sharpes computed on fill-days only (61 sessions dropped) |
| D15 | disclosure | Novelty percentile built on ~10.7 effective independent windows; the 95% bar has no resolution |
| D16 | disclosure | The named analog moves by up to six months with window length; consequence #3 pre-registers a single cut |
| D17 | disclosure | Eight instances of causal/mechanistic language, which the spec makes a defect by its own terms |
| D18 | cosmetic | "Six of eight" counts PC1, which correlates 0.850 with −(v6+v6b)/2 |

---

*Reviewer note on method, per `spec.yaml:190-194`: every de-confounding experiment identified was
run rather than flagged — edge-exclusion sensitivity, bootstrap block-length sweep, synthetic-null
size calibration, Bonferroni, HAC standard errors, leave-one-variable-out PCA, step-vs-trend BIC,
ramp-null simulation of the step estimator, four alternative v6 reference profiles, a symmetric
year×year profile similarity matrix, v6 confound regressions, participation-ratio bootstrap bands
and synthetic-ensemble calibration, 28-way clamp-definition enumeration, exact ledger
reconciliation and flat-at-close/roll-rule verification, an exact leg-and-overlay decomposition of
Product A, analog-search window and summary-statistic sensitivity, location-CI coverage
simulation, a Mahalanobis outlier test, and a predictive regression of P&L on the panel. Nothing in
the repo outside this file was modified.*
