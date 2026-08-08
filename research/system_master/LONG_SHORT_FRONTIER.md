# LONG_SHORT_FRONTIER — side asymmetry on Solar E10 (SMV2E, seq 328-334 + ext 343-346)

_2026-08-08. Integer-contract implementable (short targets scaled then rounded, replayed
through the certified executor). Dev 2022-2026/05. Crisis check = 20 worst NQ sessions.
Code `runs/SMV2E_SIDE_ASYM/smv2e.py`; extension inline (committed in run log)._

## Unconditional short scaling (seq 328-332): informative, NOT promoted

| arm | net | Sharpe | maxDD | equal-vol DD | crisis retention |
|---|---|---|---|---|---|
| s100 | $119.0k | 0.71 | −$40.2k | −$40.2k | 1.00 |
| s75 | $114.9k | 0.77 | −$27.9k | −$31.5k | 0.75 |
| s50 | $111.9k | 0.86 | −$22.6k | −$29.1k | **0.45 ✗** |
| s25 | $113.5k | 0.98 | −$20.3k | −$29.4k | **0.15 ✗** |
| s0 long-only | $107.3k | 0.97 | −$26.3k | −$39.8k | **−0.18 ✗** |

Unconditional short-cutting buys Sharpe by selling crash insurance — exactly the
trade the constitution forbids (right-tail/crisis preservation). Only s75 passes
retention and its gain is modest. **No unconditional arm promoted.**

## Conditional: cut shorts ONLY against an HTF uptrend (seq 333-334 + plateau ext)

| arm | net | Sharpe | maxDD | P(equal-vol diff>0) | crisis retention |
|---|---|---|---|---|---|
| c1_75 (short×0.75 iff HTF-UP) | $124.5k | 0.78 | −$32.2k | 0.941 | ~0.86 |
| **c1_50 (short×0.5 iff HTF-UP)** | **$129.1k** | **0.86** | **−$26.1k** | **0.922** | **0.72 ✓** |
| c1_25 | $136.5k | 0.94 | −$23.2k | 0.908 | 0.58 ✗ |
| c1_0 | $141.7k | 1.00 | −$23.6k | 0.877 | 0.42 ✗ |
| c2 (symmetric counter-HTF ×0.5) | $116.8k | 0.88 | −$27.1k | — | 0.78 (but cuts long-side net) |

Monotone family, broad plateau, and — unlike the unconditional grid — **net RISES as
HTF-UP shorts shrink**: counter-HTF shorts are negative-expectancy inventory, not
insurance. The insurance lives in HTF-DOWN shorts, which c1 never touches (crisis
days overwhelmingly occur with HTF already DOWN; retention 72% at the promoted cell,
the residual 28% being first-leg-down days where HTF is still UP).

**PROMOTED: c1_50** (the only cell passing all three gate legs: P≥0.9, retention ≥60%,
plateau membership). Deeper cells are Sharpe-better but fail convexity — recorded, not
promoted.

## Composition with SM08 tilt — the new Solar-core candidate

Apply ×1.25 up-weight on HTF agreement (SM08, passed) AND ×0.5 on HTF-UP shorts (c1_50):

| object | net | Sharpe | maxDD | worst month | crisis retention |
|---|---|---|---|---|---|
| tilt only (SM08) | $131.5k | 0.78 | −$37.6k | −$17.0k | 1.02 |
| **tilt + c1_50 ("SOLAR_DUAL_HTF")** | **$138.1k** | **0.89** | **−$26.7k** | **−$11.0k** | 0.78 |

Status: candidate composition of two separately-gated components (same pedigree class
as F5 was). It becomes the Solar leg for the V2 portfolio re-rank. Mechanism note: this
is the DD1 family from Directive V2 §12 — HTF conflict handled by DOWN-weighting the
conflicted side, complementing SM08's up-weight; together they make the HTF state a
two-sided exposure map {agree: 1.25, neutral-long: 1.0, conflicted-short: 0.5}.
