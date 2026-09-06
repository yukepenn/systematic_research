# G3_SWEEPREV_20260906 — Post-sweep liquidity-provision reversal (Nagel family) with the generic-MR discriminator

**Ledger G00092 · family GENESIS3_EVENT · EVIDENCE STATUS: DISCOVERY · result: CLOSED AT SCOPE (S28)**

Spec committed before results (`8d5d584`). Program: `src/sweeprev.py` (frozen mechanical readings
R1–R14 in the src header, stated before any result was computed). Full program-printed log:
`out/gate_table.txt`. All cells: `out/cells.csv`. Discriminator: `out/discriminator.csv`.
Markets ES/RTY/YM/ZB/CL 1-min POINTS substrates (sha256 printed in [G0]); **NQ excluded — flagged**
(house law: NQ is the momentum outlier). Seal asserted per substrate: 0 bars ≥ 2026-08-01.

## Verdict in one line

**The sweep conditioning is value-SUBTRACTING, not value-adding: the sweep-fade earns LESS than the
plain k-sigma MR control it had to beat (delta −1.77 $/ev, CI [−3.93, +0.42]), the non-sweep placebo
earns MORE than the sweep cells, the gross edge itself is indistinguishable from zero, and the
whole family is ~25–50× under water at the conservative cost rung.** G2, G3, G4, G5, G6 all FAIL →
closed at scope, and with it the last open intraday-MR representation on the non-NQ complex.

## Gate table (program-printed, from `out/gate_table.txt`)

```
GATE  | SPEC                                                                          | OBSERVED | PASS-FAIL
G1    | MDE printed per market BEFORE any observed mean                               | printed  | PASS
G2    | pooled ex-macro after-cost mean>0 AND session-block CI excl 0 AND circular p<.05| -50.14$/p=0.085 | FAIL
G3    | DISCRIMINATOR: sweep minus k-sigma control delta CI excludes 0 (delta>0)      | -1.77$   | FAIL
G4    | vol-matched non-sweep placebo shows LESS than the sweep cells                 | +2.16!<+1.53 | FAIL
G5    | ZB per-event gross >= G00062 breakeven ticks at the 2-tick rung (else COST-DEAD)| +0.19tk  | FAIL
G6    | 2022-23 vs 2024-26 sign consistency, pooled ex-macro gross mean               | -1.1/+3.4 | FAIL
G7    | {1,2}-tick/side per-market band printed; conservative 2tk/side rung gates     | applied  | PASS

DECISION RULE (spec verbatim, mechanical): G2+G3+G4+G6 NOT all PASS -> CLOSED AT SCOPE (S28)
```

## Key numbers (pooled ex-macro gating cell; USD/contract per event, GROSS unless noted)

| quantity | value |
|---|---|
| pooled ex-macro sweep events (non-overlapping) | 118,847 over 1,184 union sessions |
| MDE_80 (printed first) | $3.10/ev pooled; $2.65–7.29 per market |
| sweep gross mean | **+1.53** $/ev, session-block CI **[−0.53, +3.54]** (includes 0) |
| sweep after-cost mean @2tk/side (GATING) | **−50.14** $/ev (CI [−52.40, −47.88]; @1tk/side −26.48) |
| circular shared-draw null (operative, k=1..1183) | two-sided **p = 0.085**; sign-flip second computation p = 0.162 |
| K_eff over 5 markets | rho_bar +0.169 → **K_eff 2.98** (printed; pooled test is one test at α .05) |
| **DISCRIMINATOR** sweep − control | **−1.77** $/ev, joint CI **[−3.93, +0.42]**; per-market deltas all ≤ +0.89, ZB **−5.51 CI [−7.80, −3.28]** |
| control gross mean | +3.31 $/ev (the generic object ≥ the conditioned one) |
| placebo gross mean | +2.16 $/ev > sweep +1.53 (G4 inverted) |
| ZB cost bar (G5) | +0.187 ticks/ev vs 2.1395-tick G00062 bar → **~11× short, COST-DEAD** |
| chronology | era1 −1.12 vs era2 +3.38 $/ev — **sign flip** |

## What the run means

1. **The card's own falsifier fired exactly as designed.** The mechanism claim ("providers fade
   forced-aggressor sweeps") required the breach+range conditioning to add edge over an
   unconditioned k-sigma fade. It does not — pointwise it *subtracts* on 4 of 5 markets, and on ZB
   the subtraction is itself significant (CI [−7.80, −3.28]). The graveyard's verdict on the
   G2_F2_SWEEP01 NQ scope — "response is generic post-cross MR carrying no level information" —
   now extends measured to the entire non-NQ complex, with the stronger reading that the level/
   sweep dressing is mildly anti-informative.
2. **Even the generic MR it collapses into is not tradeable.** Control gross +3.31 $/ev vs
   $24–129/RT conservative costs. The ZB control cell shows the largest gross (+11.34 $/ev,
   market-level CI [9.17, 13.49]) — a re-sighting of the already-closed G00062 scope (ZB generic
   intraday MR, cost-fragile: 0.36 ticks vs a 2.14-tick breakeven), NOT a new opening.
3. **No probability statistic is published as a headline here**; the one p-value (0.085) is stated
   in words in [G2] with a second, independent computation (sign-flip p 0.162) beside it.

## §28 closure block (for FAILURE_MEMORY.md — maintainer to append; this pod is read-only on state docs)

```
### Post-sweep liquidity-provision reversal, non-NQ complex (G00092, `G3_SWEEPREV_20260906`)
Closed:  observable = ES/RTY/YM/ZB/CL 1-min POINTS substrates 2022-01..2026-07 (ZB 2022-12+), sha-printed
representation = fade of 1-min sweep bars (breach of trailing-30-min extreme AND bar range >= 2x trailing
  median range) vs plain k-sigma MR control (|1-min move| >= 2*trailing-30-min sd) vs vol-matched
  non-sweep placebo; non-overlapping events, +30-min exit, ex-macro gating cell
event = forced-aggressor sweep bar      horizon = +30 min      target = after-cost mean AND sweep-minus-control delta
execution = screen-level, MODELED ALL_IN {1,2}tk/side + $4.36      sample = 118,847 pooled ex-macro events,
  1,184 union sessions, K_eff 2.98
reason = DISCRIMINATOR NEGATIVE: sweep minus generic-MR delta -1.77 $/ev CI [-3.93,+0.42], ZB leg
  significantly NEGATIVE (-5.51 CI [-7.80,-3.28]); placebo (+2.16) > sweep (+1.53) — G4 inverted;
  gross edge itself null (circular shared-draw p .085, CI incl 0) and era-sign-flipped (-1.12 vs +3.38);
  after-cost -50.14 $/ev at the gating rung; ZB COST-DEAD (0.19 tk vs the 2.14-tk G00062 bar, ~11x short)
```
Still open (adjacent): nothing on this axis. The sweep/level conditioning is measured
value-subtracting relative to generic MR, and generic intraday MR is itself closed at scope
(G00062 ZB, G00063 daily equity, G00065 CL). This closes the last open intraday-MR representation
on the non-NQ complex.

## Anomalies / disclosures

- **One implementation defect fixed between attempts:** the first execution crashed on a grid-width
  IndexError (slot 1379 = the 17:00-stamped session-last bar) before any gate or mean was printed;
  fixed `W = 1379 → 1380` and reran. No result was observed before the fix; no frozen reading changed.
- **Spec-underdetermined choices were frozen in the src header (R1–R14) before results:** "the same
  z" = 2.0 (the sweep definition's own range multiplier) on the trailing-30-min sd; costs = ticks
  PER SIDE + $4.36 (family convention, 2tk/side gates) with the spec-named G00062 per-RT model used
  for the G5 ZB bar; G4 on point estimates; G6 on the gross mean's sign; 20-of-30-bar trailing-window
  tolerance; greedy 30-min non-overlap suppression before the macro split.
- **G2b as coded read "CI excludes 0" literally and returned True because the after-cost CI
  [−52.40, −47.88] excludes 0 from BELOW.** Stated plainly to avoid a mislabelled-statistic trap:
  the after-cost mean is significantly NEGATIVE. G2 fails on G2a and G2c regardless.
- ZB substrate begins 2022-12-26, so its era1 is 2023 only (disclosed in [G6]).
- The macro-window cells (n≈5–6k pooled) show positive gross means for placebo/control
  (+12.26/+6.67 $/ev) — small, non-gating, cost-dead at the band, and direction-unstable across
  eras; reported for completeness in `out/cells.csv`.
- The REPORT.md listed in spec outputs could not be written to the run directory (Write refused by
  the harness for subagent report files); this document is returned in the structured output for
  the orchestrator to place at `runs/G3_SWEEPREV_20260906/REPORT.md`.