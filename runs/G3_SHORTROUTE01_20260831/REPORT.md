# G3_SHORTROUTE01 - did the mirrored short sleeve's 2022-2025 run have an ex-ante handle?

**Spec:** `runs/G3_SHORTROUTE01_20260831/spec.yaml`, committed at `9a18980` before any conditional
statistic existed. Not edited. Six state variables, no seventh, nothing re-binned after a result.

**Status:** LIVE = NO | spend $0 | no order, deploy, enable, backtest or CrossTrade/NT8 call |
no `.cs`, `research/weekly_edge/src/` or `research_sdk/` file was written to.

---

## THE VERDICT, IN ONE SENTENCE

**G2 FAILS and G3 FAILS: the best of the six preregistered spreads (S5, +1.015 pts/session) sits at
the 56.2nd percentile of the max-over-six circular-shift null - below its own median, let alone the
95th percentile of +1.680 - and its favourable tercile earns +0.246 pts/session against a
within-tercile $20.65 cost hurdle of 2.538, a shortfall of 2.29 pts/session or 4.2 bootstrap
standard deviations.**

**THERE IS NO WINNER. MODERN WAS NOT READ. THE SHORT AXIS IS RECORDED CLOSED.**

The 2022-2025 four-year run had **no ex-ante handle** among the six frozen variables. Under the
preregistered decision rule that is not a null result to be re-run with different variables - it is
the answer, and it saves every future wave on this axis.

---

## GATE TABLE (printed by the program - `out/console.txt` section 10, never assembled by hand)

| id | gate | spec | observed | verdict |
|----|------|------|----------|---------|
| G0 | reproduce WAVE C's object | 2,225 trd / 6.00 pts/s / $121,454 / P1 14.86 | 2,225 / 6.00 / $121,454 / 14.86 | **PASS** |
| G1 | separation in PRE (passes iff its spread survives G2) | best variable's SPREAD survives G2 | best S5 +1.015 | **FAIL** |
| G2 | best SPREAD beats the MAX-over-six circular-shift null | observed best > 95th pctile of the max-statistic null | +1.015 vs p95 +1.680 (56.2nd pctile) | **FAIL** |
| G3 | favourable tercile clears the $20.65 cost hurdle | point **and** bootstrap 90% CI lower bound above trd/sess x 1.0325 | +0.246 (CI lo -0.584) vs hurdle 2.538 | **FAIL** |
| G4 | monotone across all three terciles | middle tercile lies between the extremes, in the predicted direction | S5: +0.246 -> +0.645 -> -0.768 | **FAIL** |
| G5 | episode concentration (LOYO and LOEO) | >= 11 of 14 LOYO folds positive **and** >= 80% LOEO | LOYO 14/14, LOEO 100.0% over 14 episodes | **PASS** |

Four of the five identification gates fail independently. G5's PASS is not a rescue and is not sold
as one: leave-one-out only asks whether an effect is concentrated in a few episodes. S5's +1.015 is
indeed spread evenly across 14 years and 14 episodes - it is an evenly-distributed quantity that the
null says is ordinary and the cost line says is worthless.

---

## G0 - the object is the same one

Rebuilt from the substrate, not read from WAVE C's cache: the vendor targets, the vote, the signed
fills, the halt/target and the session box are all imported from `research/weekly_edge/src`.

```
2,225 trades | 6.00 pts/session | $121,454 net | P1 14.86 pts/session   (spec: identical)
```

**The substrate trap was handled explicitly.** `setup()` is never imported. `load_deep` is called
directly and the max bar timestamp asserted and printed for both substrates:

* **CORE** (`extend=False`, **G0 reproduction only**) - 1,558,497 bars, max bar `2026-05-29T16:59`.
  The truncation is *confirmed and printed*: 2026-07-31 17:00 was requested and the file stops two
  months earlier. This substrate feeds no conditional statistic.
* **FULL** (`extend=True`, the analysis object) - 6,528,330 bars, 5,466 sessions, max bar
  `2026-07-31T16:59` < the 2026-08-01 seal.
* Cross-check: FULL restricted to the CORE session set gives **$121,454, 100.0% identical sessions**.

**G0 control (not a spec gate).** To prove the drift-neutral machinery is WAVE C's rather than a
lookalike, WAVE C's *own* PRE cut (2006-01-01 -> 2022-04-30, no warm-up filter, an already-published
unconditional aggregate containing no MODERN month) was rebuilt with this run's estimator:

| | months | drift-neutral | 90% CI | hurdle |
|---|---|---|---|---|
| this run's replica | 196 | **+0.408** | [-0.324, +1.234] | 2.62 |
| WAVE C published | 196 | +0.408 | [-0.339, +1.187] | 2.62 |

Identical to three decimals. Every difference between that and this run's PRE number below is
**the spec's population**, not the estimator.

---

## POPULATIONS AND SEAL - printed, not assumed

| population | sessions | status |
|---|---|---|
| PRE 2006-01-01 -> 2019-12-31 | 3,760 | IDENTIFICATION |
| TRANS 2020-01-01 -> 2022-04-30 | 603 | **EXCLUDED ENTIRELY** |
| MODERN 2022-05-01 -> 2026-05-29 | 1,057 | **NOT READ** |
| 2026-05-30 -> 2026-07-31 (present in substrate, outside the spec's MODERN window) | 46 | not read |
| >= 2026-08-01 | **0** | seal |

The **PRE monthly panel** is 157 months, 2006-12 -> 2019-12, 3,436 sessions, 9,201 sleeve trades.
Eleven PRE months are lost to warm-up, and it is mechanical rather than chosen: S2 needs 21+63
sessions for its first value and 252 more for its first causal tercile, so 2006 carries no labelled
month. Printed in full in `out/console.txt` section 2.

Unconditional PRE control, which every conditional table is measured against:
**-0.075 pts/session, 90% CI [-0.492, +0.360], against a 2.76 hurdle** at 2.678 trades/session.
The spec's PRE population is, if anything, slightly *worse* than WAVE C's +0.408 - the identification
window was not a friendlier place for this sleeve than the one WAVE C reported.

---

## G1 - the six SPREADs

SPREAD = drift-neutral expectancy in the predicted-favourable tercile minus the predicted-unfavourable
tercile, PRE only. Signs were fixed in the spec before any of this existed, so a negative entry means
the variable ran **the wrong way** and is recorded that way.

| id | variable | predicted | LOW | MID | HIGH | SPREAD | vol-norm | marginal-null pctile |
|----|----------|-----------|-----|-----|------|--------|----------|----------------------|
| S1 | trailing realised vol (21-sess) | POSITIVE | +0.019 | -0.235 | -0.019 | **-0.038** | -0.058 | 47.8 |
| S2 | vol-of-vol (63-sess of S1) | NEGATIVE | +0.158 | +0.673 | -0.743 | **+0.901** | +1.379 | 89.6 |
| S3 | trend state (63-sess log return) | NEGATIVE | +0.056 | -0.537 | +0.512 | **-0.456** | -0.697 | 29.4 |
| S4 | range compression | NEGATIVE | -0.741 | -0.634 | +0.818 | **-1.559** | -2.384 | 2.2 |
| S5 | overnight share (21-sess) | UNSIGNED, two-sided | +0.246 | +0.645 | -0.768 | **+1.015** | +1.552 | 86.6 |
| S6 | prior-close VIX | POSITIVE | +0.173 | -0.850 | +0.189 | **+0.016** | +0.025 | 43.3 |

**S1, the PRIMARY hypothesis, is dead on arrival: -0.038.** The amplitude story - "the sleeve only
pays when moves are large enough to clear a fixed cost, so 2022-2025 was simply a high-vol regime" -
is the single most attractive explanation this campaign had for the four-year run, and trailing
realised volatility does not separate the sleeve's drift-neutral expectancy at all in fourteen years
of PRE. Its implied-vol competitor S6 (+0.016) says the same thing from the other side.

**S6's predicted sign** is not written as a field in the spec. The spec states S6 is "the natural
competitor to S1" and gives it S1's amplitude mechanism, so it was declared POSITIVE in the code
before running. Reading it as unsigned would have silently widened a one-sided test.

---

## G2 - the null that prices the search (THE ONE THAT MATTERS)

2,000 circular shifts of the state-label series against the sleeve's monthly (y, x) series.
**Every draw redoes the entire analysis** - all six variables, all three terciles, the S5 two-sided
rule - and records the **max over six**. **One shift is shared by all six variables per draw**, because
the six are a correlated family (S1-S6 label agreement 61%, session-level r = +0.465) and independent
shifts would price a search that was never run and set the bar far too high.

```
observed best SPREAD (S5)   +1.015
max-statistic null   p50 +0.950   p90 +1.592   p95 +1.680   p99 +2.347   max +2.384
observed sits at the 56.2nd percentile   ->   DOES NOT EXCEED p95
```

The observed best is **barely above the null's median**. Six variables x three terciles on 157 months
manufactures a best-of-six spread near +0.95 by construction; +1.015 is that, and nothing more.

**The sign-flip objection is closed too.** S4 ran significantly the *wrong* way (predicted
compression-favourable; observed expansion-favourable, at the 2.2nd percentile of its own marginal
null). Taking every variable two-sided post hoc, the largest |spread| anywhere is S4's **1.559** -
still below the **1.680** one-sided max-statistic bar, and a genuinely two-sided null bar would be
higher still. No sign convention rescues this table.

---

## G3 - the binding gate: 0 of 18 states are economically live

Winner S5, favourable tercile LOW (45 months, 984 sessions, 2.458 trades/session):

| | pts/session |
|---|---|
| drift-neutral expectancy | **+0.246**  (90% CI [-0.584, +1.218]) |
| hurdle @ **$4.36 FLOOR** - *a floor, never a headline* | 0.536 |
| hurdle @ **$20.65 PRIMARY** - **the gate** | **2.538** |
| hurdle @ **$25.01 all-in** | 3.074 |
| vol-normalised | +0.342 per 1,000 pts of session movement |

**It does not even clear the $4.36 commission-only floor.**

The whole surface, across all six variables and all eighteen terciles, favourable or not:

* states clearing the **$20.65** primary hurdle: **0 of 18**
* states clearing the **$4.36** floor: 3 of 18
* best cell anywhere: **S4 HIGH, +0.818 against a 2.640 hurdle - short by 1.822 pts/session**
* highest 90% CI **upper** bound anywhere on the surface: **+1.721**, still **0.916 below that
  state's own hurdle**. There is no cell in this design in which even the optimistic end of the
  interval pays $20.65/ctrRT.

**Power / MDE, printed before anyone proposes economics on a routed third of the sessions.** The
favourable tercile's bootstrap sd is 0.549 pts/session, so the smallest effect this population could
separate from zero at 90% one-sided is about 0.90. The gap between +0.246 and the 2.538 hurdle is
**2.29 pts/session = 4.2 bootstrap sd**. This is not an underpowered near-miss.

---

## G4 / G5

**G4 FAIL.** S5 runs +0.246 -> +0.645 -> -0.768: the middle tercile is *outside* the extremes.
**All six variables are non-monotone** - not one of the six produces an ordered three-tercile
response, which is what a genuine state variable is supposed to look like.

**G5 PASS**, and it is the only gate that passes on the identification side. Leave-one-year-out:
14/14 folds positive across the 14 declared PRE years (all 14 carry months; no fold is degenerate).
Leave-one-episode-out: 100.0% over **14 episodes** covering 45 favourable months.
**K = 45, rho_bar = 0.0071, K_eff = K/(1+(K-1)*rho_bar) = 34.3** (whole PRE series: K = 157,
rho_bar = 0.0000, K_eff = 157.0). Read correctly, this says S5's ordinary-sized spread is not driven
by a handful of episodes. It does not make the spread real and it does not make it pay.

---

## SCALE - every PRE number printed twice, as the spec requires

| population | sessions | med bars | med bars RTH | med abs-move/session | med session range |
|---|---|---|---|---|---|
| PRE 2006-01..2019-12 | 3,760 | 1,223 | 390 | 619.9 | 40.5 |
| TRANS (excluded) | 603 | 1,365 | 390 | 3,623.0 | 241.0 |
| MODERN 2022-05..2026-05 | 1,057 | 1,380 | 390 | 4,417.0 | 291.5 |

PRE vol normaliser = 653.9 points (median month's mean session absolute 1-minute movement). The
vol-normalised column in the G1 table and the vol-normalised expectancy in G3 are rescalings of the
identical estimate, not a different estimator, so a reader who rejects raw PRE points can still read
the table. It does not change the answer: the vol-normalised best spread is +1.552 per 1,000 points
of session movement, against a null whose own scale moves with it.

---

## THE TRAPS THE SPEC NAMED - all checked, whether or not they fired

* **S3 is a trap for itself.** It did *not* win (-0.456, rank 5 of 6), so there is no specification
  failure to investigate. The drift-neutral dependent variable did its job: with the market's own
  direction regressed out, the most obvious variable is the second-worst of the six.
* **The intercept is an extrapolation to x = 0.** Printed for every variable and every tercile
  (`console.txt` section 9): mean market drift, its sd, |mean|/sd, the slope, and slope x mean x.
  Several terciles sit 0.6-0.7 sd from zero, so part of the raw spread across the table is different
  x-supports rather than different behaviour. This works *against* believing any of the six, and none
  of them survived anyway.
* **S1 and S6 are near-collinear** (session-level r = +0.465, 60.5% monthly label agreement). Neither
  worked, so there is no double-counting to police - but had they, it would have been **one** finding.
* **PRE sessions are thinner.** Handled above.
* **A winner is not a candidate.** There is no winner, and nothing in this run produced a rule, a
  weight, an exit, a routed-strategy P&L or a `.cs` file on any outcome.

---

## WHAT THIS CLOSES, AND WHAT IT DOES NOT

**CLOSED - the short axis.** Under the preregistered decision rule, ANY failed gate means no winner,
MODERN is not read, and the axis is recorded CLOSED. Four gates failed. 2022-2025 was a four-year
regime with **no observable ex-ante trigger** among realised vol, vol-of-vol, trend state, range
compression, overnight share or implied vol. The sleeve is **not** a regime-routing object, and W61 /
W62 / W120 do not need re-running inside a routed population, because there is no routed population
to run them in.

**CLOSED - the amplitude explanation specifically.** S1 was the spec's declared PRIMARY hypothesis and
the campaign's most attractive story. It returned -0.038, its implied-vol twin returned +0.016, and
neither is monotone. Volatility level is not the handle.

**NOT CLOSED, stated as a limit rather than smuggled in as a finding.** This run tested six variables,
in PRE, at monthly resolution, on the drift-neutral intercept. It cannot say that no state variable
anywhere separates this sleeve. What it does say - and what the preregistration binds it to - is that
the six mechanisms this campaign could name in advance do not, that a best-of-six search over them
produces exactly the spread a shuffled null produces, and that not one of the eighteen resulting
states pays $20.65/ctrRT or even $4.36/ctrRT. Continuing to look would require a new preregistration
with new mechanisms stated before the data is touched, and it would be spending against a prior that
this run just made considerably worse.

**MODERN remains unread and therefore unspent** for the conditional question. The only 2022+ figures
anywhere in this run are G0's reproduction numbers, on the already-DISCOVERY_CONSUMED aggregate,
permitted explicitly by the spec.

---

## FILES

| path | what |
|---|---|
| `src/build_route.py` | substrate (own loader, `extend=True`, seal asserted and printed), sleeve rebuild, per-session RTH/overnight split, VIX join with a look-ahead assertion |
| `src/analyze_route.py` | six frozen variables, causal 252-session terciles, G0-G5, the max-statistic null, the confirmation branch (not taken) |
| `out/console.txt` | the full program output, including the harness selftest (13/13) and the gate table |
| `out/gates.json` | machine-readable gates, spreads, null quantiles, controls; `modern_read: false`, `confirmation: null` |
| `out/pre_terciles.csv` | all 18 PRE tercile cells: months, sessions, trade rate, intercept, slope, 90% CI, hurdles at $4.36 / $20.65 / $25.01, mean market drift, vol-normalised intercept |
| `out/pre_monthly_panel.csv` | the 157-month PRE panel with all six monthly state labels |
| `out/_cache/` | build log and the rebuilt session / trade frames |
