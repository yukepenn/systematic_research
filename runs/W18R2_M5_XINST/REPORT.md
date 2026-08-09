# W18R2_M5_XINST — **PARTIAL.** The Sharpe effect replicates across instruments. The CDaR-tail effect fails again, on the same prong, with four times the evidence.

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
