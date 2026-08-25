# OTR R34 — METHODOLOGY EQUALIZER · REPORT

**Question:** how much of the visual gap between HIS weekly sheets and OUR frozen results is
display methodology (weekly-retuned, gross, in-sample backtest sheets) rather than edge?

Preregistered spec committed `d2a2590` before any readout. B1 harness PASS (incumbent
reproduces 1512 fit trades exactly). 21 comparable SA weeks (17 fit + 4 holdout); the 2 Trade
Performance records and everything ≥ 2026-08-01 excluded per spec.

## The five sheets (same 21 weeks, same market, same family)

| sheet | pos/21 | total | mean wk | best wk | worst wk |
|---|---|---|---|---|---|
| **HIS** (gross, as displayed) | 16/21 | **$180,250** | $8,583 | $49,940 | **−$42,235** |
| FROZEN incumbent (net) | 13/21 | $30,028 | $1,430 | $23,296 | −$16,318 |
| FROZEN leading (net) | 12/21 | $11,839 | $564 | $16,282 | −$19,777 |
| **SHOWCASE V1** (per-week hindsight argmax, gross) | **21/21** | **$522,395** | $24,876 | $49,645 | **+$12,790** |
| **SHOWCASE V2** (retune on last week, apply this week) | 10/21 | **$8,130** | $387 | $24,380 | −$21,565 |

Post-hoc (amendment 1): **FROZEN_ORACLE** — the best *single* config in full-period hindsight —
makes **$119,160 at 16/21 positive** (`P_Q75|C_DIR|X_TARGET:60`). The incumbent ranks 71/288 by
total, i.e. our a-priori frozen choice was not even a lucky one.

## Preregistered readouts

- **A1 = TRUE.** V1 is 21/21 positive with 2.9× his total. **Hindsight weekly selection over a
  mere 288 discrete configs — a LOWER bound on what continuous tuning can do — manufactures a
  sheet strictly better-looking than his, including a +$49,645 week inside his −$42,235
  disaster week.** "He basically wins every week" therefore carries, by itself, ZERO evidence
  of a persistent edge.
- **A2 = FALSE** (V1 ≫ 50 % of his total): the family is rich enough to fake his sheet, so no
  structural-gap conclusion can be drawn from this run.
- **A3 = 3.28**: the methodology has 3.3× the power needed to explain the ENTIRE gap between
  his sheet and our frozen net.
- **A4: V2 ($8,130) lands BELOW frozen ($30,028).** Weekly retuning has **negative transfer**:
  last week's best config is anti-informative for this week. The V1 winner changes identity 16
  times in 21 weeks and flips between D_MOM and D_FADE and across exit families — noise-chasing
  in its purest form. This is campaign #1's PBO 0.48–0.90 finding, restated in dollars.

## Where HIS sheet actually sits — the most informative placement

His sheet (16/21, $180k, with a displayed −$42k week) is **not** the maximal-hindsight profile:
a V1-style showcase never shows a losing week, and panel-extent forensics measured only 4 build
events, not 21 retunes. But it sits **far above anything our family achieves frozen a priori**
($12–30k) and closest in *shape* to the single-config-full-hindsight oracle (16/21, $119k).

Two readings remain compatible with everything measured, and this run **cannot** separate them:

1. his frozen system genuinely earns ~$180k gross on these weeks (our clean-room family is
   simply not his system — consistent with R32's reconstruction scores ≤ 20); or
2. his displayed record is partially in-sample — a config held for stretches and retuned at the
   build events, each sheet run by the then-current version over the week just passed.

Only the R33 frozen-build test (recover → freeze → 2022–2026 uniform with frictions) separates
them. What R34 **does** settle: the *observation* "his weekly sheets look great" must never
again be used as evidence for reading (1) over reading (2).

## Forbidden-list compliance

Nothing is promoted. The V1/V2/oracle configs are selection artifacts by construction and are
recorded only to measure selection power. No data ≥ 2026-08-01 touched. No mechanism inference
from which config wins which week.
