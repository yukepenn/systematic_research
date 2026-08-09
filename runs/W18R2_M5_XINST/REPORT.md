# W18R2_M5_XINST — **PARTIAL.** The Sharpe effect replicates across instruments. The CDaR-tail effect fails again, on the same prong, with four times the evidence.

> ⚠ **THE TITLE ABOVE IS WITHDRAWN (2026-08-09, post red team).** The Sharpe prong does **not**
> replicate at the house bar: on the three instruments that did not generate the hypothesis it
> is **0.8223**, below 0.85, and no new instrument clears 0.85 on either prong individually. The
> verdict PARTIAL is unchanged; the framing is not. The title is left in place per C7 — nothing
> is rewritten — but read **RED-TEAM INGESTION** at the foot of this file before anything else.

Wave 18 of the SYSTEM_MASTER campaign, MEGA PROMPT V7. Track R. Spec frozen and committed at
`d0b9f92` before any code existed; the substrate spec frozen at `6685808` before the export ran.
Alpha budget consumed: 1 of 2. **Run once, as pre-registered.**

---

## Verdict against the pre-registered bar

| test | bar | measured | |
|---|---|---:|:--:|
| (a) sign agreement on NEW instruments | ≥ 2 of 3 | **2 of 3** (ES ✓, RTY ✓, YM ✗) | PASS |
| (b) pooled P(mean ΔSharpe > 0) | ≥ 0.85 | **0.9108** | PASS |
| (b) pooled P(mean ΔCDaR_ratio > 0) | ≥ 0.85 | **0.7841** | **FAIL** |

Both prongs of (b) must hold, so (b) fails and the verdict is **PARTIAL**. The frozen spec
defines PARTIAL explicitly: *"a PARTIAL is NOT a pass and does NOT re-queue the R2."* The
ATR-blend lead therefore stays closed. No promotion, no re-queue, no third bite.

## The result that matters most

Wave 14 (`SMV2AJ_ATR_BLEND_R2`) closed this lead on NQ alone with Gate A at
**P(ΔSharpe>0) = 0.932 PASS / P(ΔCDaR>0) = 0.753 FAIL** — one prong of one gate, by 0.097.
The stated diagnosis was that the mechanism might well be real and only lacked statistical
power on 4.4 years of daily data.

**Adding three instruments and 3.68 effective independent samples moved that prong from 0.753
to 0.784.** It did not clear 0.85. Meanwhile the Sharpe prong held at 0.911. The power
hypothesis has now been tested with roughly four times the evidence and the tail effect still
does not appear. That is a much stronger closure than Wave 14's, and it is the useful outcome.

## Per instrument

| instrument | role | ΔSharpe | ΔCDaR ratio | P(ΔSharpe>0) | P(ΔCDaR>0) | sign agree |
|---|---|---:|---:|---:|---:|:--:|
| NQ | KNOWN | +0.0364 | +7.52% | 0.9029 | 0.7547 | ✓ |
| ES | NEW | +0.0377 | +5.75% | 0.8329 | 0.6975 | ✓ |
| RTY | NEW | +0.0334 | **+0.35%** | 0.8200 | 0.7967 | ✓ |
| YM | NEW | **−0.0094** | **−1.84%** | 0.3904 | 0.3610 | ✗ |

Note that RTY's sign agreement is carried by a **+0.35%** CDaR ratio — technically positive,
economically nothing. Read the sign-agreement pass as the thin thing it is.

**Pipeline validation.** The NQ cell was included as a KNOWN control to check the machinery
against an answer already on the record. Wave 13 (`SMV2AI`) reported control Sharpe 0.709 →
blend 0.746 (**ΔSharpe +0.037**) and CDaR $27,162 → $25,183 (**ratio +7.29%**). This run, on a
completely different cost basis (full-size NQ at $2.18/side rather than MNQ at $0.65/side),
gets **ΔSharpe +0.036** and **ratio +7.52%**. The levels differ as they must; the *increments*
match. The machinery reproduces a known answer.

## Dependence — the finding I did not expect

The four instruments' **raw daily P&L** correlate at a mean off-diagonal of **0.677**. Their
**daily difference series** (BLEND75 − CONTROL) correlate at a mean off-diagonal of **0.029**:

| | NQ | ES | RTY | YM |
|---|---:|---:|---:|---:|
| NQ | 1.000 | −0.010 | −0.041 | 0.095 |
| ES | −0.010 | 1.000 | −0.001 | 0.064 |
| RTY | −0.041 | −0.001 | 1.000 | 0.066 |
| YM | 0.095 | 0.064 | 0.066 | 1.000 |

Effective sample size **ESS = 3.68 of 4** (`ESS = k²/1ᵀR1`), against a pre-registered
disclosure bar of 2.0 which is comfortably cleared. The instruments' *levels* move together;
the mechanism's *increment* is nearly independent across them. Four instruments really do carry
close to four instruments' worth of information about this mechanism.

**This makes the CDaR failure worse, not better.** The pooled test is not a weak test padded
with redundant samples — it is close to a genuine four-fold increase in evidence, and the tail
effect still does not clear the bar. The pooled bootstrap resamples the **same date blocks
across all four instruments simultaneously**, so whatever dependence does exist is preserved
exactly rather than estimated.

## The disclosure a reader must not miss

**ES, RTY and YM all lose money under this construction.** Control Sharpe: ES **−0.045**,
RTY **−0.633**, YM **−0.563** — against NQ's +0.838. The 13-member Solar ensemble does not port
to those instruments at all.

What is under test here is therefore the **paired increment**, not the system. "The mechanism
replicates on ES" means "adding ATR information improved a losing system's Sharpe by 0.038 on
ES", not "this works on ES". Anyone reading a REPLICATES-style verdict as evidence that the
strategy travels would be reading it wrong. Per C2 these instruments are mechanism-replication
samples only; nothing here proposes trading them, and nothing may.

## Method disclosures

- **Substrate gate applied before any P&L.** All four instruments passed
  (`out/substrate_check.csv`): bar ratio vs NQ 1.000 / 1.000 / 0.992 / 0.994; session coverage
  1.000 / 1.000 / 0.9939 / 0.9939; monotone; zero duplicate timestamps. None excluded. RTY and
  YM have **1,132** sessions vs NQ/ES's 1,139, so the pooled test runs on the 1,132-session
  intersection.
- **Instrument scaling carries no free parameter.** The state machine is scale-invariant
  (`VolMult × sigma` is in the instrument's own points); the only scale-dependent term is the
  clamp, specified in **ticks**, which scales with each instrument's tick (NQ/ES 0.25, RTY 0.10,
  YM 1.00). Implemented by setting the simulator's module-level `TICK` per instrument inside a
  `try/finally`, which reaches the clamp bounds, the 179-tick fallback and the 1-tick slippage
  identically.
- **`R` per instrument** (`ATR460/sigma460` whole-dev median) is a units correction, not a tuned
  parameter — the *rule* is fixed and applied once per instrument, never re-picked. Values in
  `out/R_per_instrument.json`.
- **Costs are assumed, and stated rather than invented.** $2.18/side/contract on every
  instrument — the NQ Lifetime rate, which is **not** the correct rate for ES/RTY/YM and is not
  claimed to be. It is applied identically to both arms, so it very largely cancels from the
  paired comparison. The zero-commission sensitivity flips **no** instrument's sign
  (ES +0.0373 / +6.66%, RTY +0.0335 / +0.36%, YM −0.0099 / −3.59%, NQ +0.0364 / +7.61%). No
  verdict here is cost-driven.
- **Window**: 2022-01-03 .. 2026-05-29 dev only, on every instrument. No data at or after
  2026-08-01 was read. No 2006-2021 data was read.

## What this cannot do, stated before the results as well as after

Cross-instrument replication is a **substitute** for out-of-sample evidence, not an equivalent.
ES/RTY/YM over 2022-2026 share the same macro regime, the same sessions and the same scheduled
releases as NQ. A shared-regime artifact would replicate across all four, and this test cannot
distinguish "the mechanism is real" from "the 2022-2026 US index-futures regime rewards this
construction". The near-zero *increment* correlation (0.029) is mild evidence against the pure
shared-artifact reading, but it is not proof and is not offered as such.

Nothing here establishes anything about future profitability on any instrument.

## Disposition

`arm_BLEND_75` remains **CLOSED**, now on two independent grounds: it failed Gate A's CDaR
prong on NQ (Wave 14), and its tail effect fails to replicate at four times the evidence
(this run). The family is closed for good. Any future range/true-range idea needs a genuinely
different construction targeting the CDaR tail directly, not another estimator blend.

## Red team

Commissioned per V7 §G. Verdict filed verbatim under `red_team/`; corrections ingested into
this REPORT and never into the frozen spec.

---

# RED-TEAM INGESTION — appended 2026-08-09. **This report's title was wrong. Read this first.**

Verdict: **CONFIRMED-WITH-CORRECTIONS.** 12 defects — 1 headline-flipping, 5 material,
4 disclosure, 2 cosmetic. Full verdict verbatim at `red_team/RED_TEAM_m5_xinst.md`, unedited.
Corrections live here and never in the frozen spec (C6).

**Reproduction was exact.** The reviewer rebuilt all four instruments × two arms from raw
3-minute bars in a fresh process using the unmodified simulator: every committed daily curve
matched to **max |deviation| = $0.0000000000**. The pooled bootstrap, `per_instrument.csv`,
`dep_corr.csv`, `ess.json` and `substrate_check.csv` all reproduce.

## 1. RETRACTED — "The Sharpe effect replicates across instruments." It does not, at the house bar.

The pooled statistic includes **NQ — the cell that generated the hypothesis.** On the three
NEW instruments alone:

| | pooled over all 4 (as reported) | **NEW instruments only** | bar |
|---|---:|---:|---:|
| P(mean ΔSharpe > 0) | 0.9108 | **0.8223** | 0.85 |
| P(mean ΔCDaR_ratio > 0) | 0.7841 | **0.7108** | 0.85 |

And **not one new instrument clears 0.85 on either prong individually** — ES 0.833/0.698,
RTY 0.820/0.797, YM 0.390/0.361.

Including the generating cell in the pooled statistic was pre-registered and disclosed, so this
is not a protocol breach; it is a framing error. **The honest summary is that the replication
was too weak to establish EITHER prong** — which is a different and *stronger* closure than
"Sharpe replicated, the tail did not". The verdict PARTIAL is unchanged, because it follows
mechanically from the frozen rule; but this report's title and its framing of a clean
Sharpe/CDaR split are withdrawn.

## 2. The effect lives in the 2026 stub, and I ran no chronology check

Dropping the last 106 sessions (9.4% of the sample) moves the pooled prongs from
**0.9108 / 0.7841** to **0.7661 / 0.6547**.

Worse, every instrument — **including NQ** — is only **3 of 5** on yearly ΔSharpe sign, below
the **4 of 5** LOYO bar this program applied one wave earlier (SMV2AF Gate B, where 3/5 was
ruled a failure). And *which* instruments agree is period-dependent: 2022-23 gives ES+RTY,
2024-26 gives ES+YM+NQ. **Only ES is stable.** On 2022-23 alone NQ itself is negative on both
prongs. "2 of 3" is therefore not a stable property of the instrument set, and the spec should
have pre-registered a chronology gate alongside the sign count. It did not, and that is a
design defect in the spec, recorded here rather than repaired retroactively.

**This is the second time in one wave that a 106-day stub carries the result** — M1's failure is
74.5% concentrated in the same 106 sessions. That is now a wave-level observation and belongs in
the standing cautions, not in either run's footnotes.

## 3. Two "identical construction" claims are false

**(a) The clamp does not scale the way the spec claims it does.** The spec argues the clamp is
specified in ticks and therefore "scales correctly with each instrument's own tick size", so no
free parameter is introduced. The rule is identical; the *object* is not. Expressed in ticks the
clamp binds on **13.5% of ES member-bars against 2.9% on NQ**, floors ES's VolMult-6 member on
**71.96%** of bars, and leaves the two arms **bit-identical on 13.3% of ES member-bars**. The ES
cell is therefore testing a partly different object from the NQ cell. Identical rule ≠ identical
object, and the spec asserted the latter.

**(b) An undisclosed eight-session data hole in RTY and YM.** 2023-04-05 is truncated at 14:03,
2023-04-06 through 04-14 are **absent**, and the series resumes 04-16 — producing an artificial
one-bar splice of roughly **50 sigma** that perturbs `sigma460` by **+11%** and `ATR460` by
**+5.8%**, i.e. by *different* amounts, which breaks the arm-to-arm pairing for about 460 bars.
My pre-registered substrate gate (bar-count ratio, session coverage ≥ 0.95, monotone, no
duplicates) **structurally cannot see a contiguous hole of that size** — 8 sessions is 0.7% of
1,139. The reviewer verified that excising it changes no verdict and in fact *helps* RTY, so the
conclusion is unaffected; the gate design is not.

## 4. The "0.753 → 0.784" comparison is not like-for-like

Wave 14's 0.753 is a **dollar-CDaR** statistic on the **DUAL-transformed** leg. This run's 0.784
is a **ratio** statistic on the **raw** leg, pooled across four instruments. The like-for-like
NQ number in this run is **0.7547**. So the sentence "adding ~4× the evidence moved the prong
from 0.753 to 0.784" is comparing two different statistics and must be withdrawn as stated.

**The conclusion it supported survives and is in fact stronger.** Like-for-like, NQ moved
0.753 → 0.7547 (i.e. nowhere), and the NEW-instruments-only pooled figure is **0.7108** — worse
than either. Adding instruments did not rescue the tail effect under any comparison; the power
hypothesis is still rejected, on better grounds than the ones I gave.

## 5. R is a units correction, but the effect size it implies is poorly identified

Using NQ's R on RTY instead of RTY's own multiplies RTY's ΔCDaR ratio by **13** — from +0.35% to
+4.58%. The pre-registration protected this run by fixing the rule in advance and, as it turns
out, by selecting the **less favourable** variant. But it means the tail effect size on the new
instruments is not well identified, and RTY's sign-agreement contribution rests on a quantity
that moves by an order of magnitude under a defensible alternative convention.

## 6. What the reviewer tried hardest to break and could NOT

- **The `sm.TICK` monkey-patch is correct.** All three uses resolve the global at call time, no
  module in the chain imports it by value, and the `try/finally` is per-iteration — proven
  empirically by the bit-exact rebuild. It is also **load-bearing**: a stale `TICK = 0.25` would
  move RTY's control net by −$135,615 and **flip YM's ΔSharpe from −0.0094 to +0.0140**, which
  would have produced a 3-of-3 sign count. The patch working is the reason the verdict is not
  falsely favourable.
- **The turnover/friction explanation is dead.** Δcommission is −$8.72 / +$17.44 / −$78.48 /
  −$126.44 against Δnet of +$59,579 / +$33,545 / +$15,508 / −$6,014. ES's blend traded **more**
  and improved anyway; zero-commission ΔSharpe differs by ≤ 0.0006 everywhere. The decomposition
  is a pure **mean** effect — and on a negative-mean series a volatility-shrinkage artifact would
  move Sharpe the *wrong* way, so that alternative is excluded too.
- **ESS 3.68 survives everything thrown at it.** Spearman ESS 4.005; Kendall agrees; same-sign
  rate on co-active days 0.49–0.52; tail co-movement mild. Most decisively, the correlation of
  the **bootstrap estimators themselves** gives ESS 3.63 (ΔSharpe) and 3.66 (ΔCDaR).
- **No defensible pooling rule flips the verdict.** Eight were tested — median, NEW-only,
  dollar-CDaR, CDaR-weighted, NQ's-R-everywhere, min, and others. All fail. **Only post-hoc
  deletion of YM passes** (0.9588 / 0.8610), which is exactly the move the pre-registration
  exists to prevent. The as-run rule is the **most generous** of the honest set — which clears
  the run of pooling-shopping, and also means the verdict is if anything too kind.
- **RTY's knife-edge +0.35% is sign-robust** across CDaR depths k = 10…113 and across excising
  the data contamination. Tiny, but not an artifact of the depth convention.
- The `k5` inconsistency the brief suspected **does not exist**: all three are 56.

## Revised disposition

`arm_BLEND_75` remains **CLOSED**, and the closure is firmer than this report originally
argued. The corrected statement is: *on three instruments never used to select it, in the same
era, neither the Sharpe effect nor the tail effect reaches the house confirmation bar; the only
prong that appeared to pass did so on the strength of the cell that generated the hypothesis;
and the whole result is concentrated in the final 106 sessions.* The ATR/range family is closed
for good.
