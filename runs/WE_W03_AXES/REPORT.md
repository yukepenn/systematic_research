# WE_W03 — AXES · REPORT

Spec preregistered. 35 members + 58 portfolios. Third read of the reused holdout
(confirm-only). Full table `out/summary.csv`.

## Headline: the dev tail bar was cleared for the first time — by mechanisms, not luck

**4 configs clear the bar** (worst > −$15k, ≥55 % pos, stress-positive), all of them
S4 + session-halt and/or context gate:

| config | dev | holdout |
|---|---|---|
| **S4.all13.h1300.gdl** (champion cand.) | $1,611/wk · 60.9 % · worst −$12,270 · Sharpe 0.284 · **$143.9/trade** | 0.180 → **confirm FAIL** |
| S4.narrow6.h1300.gfv | $1,730 · 59.6 % · −$14,244 · 0.259 | 0.293 (borderline) |
| S4.all13.h1300.gfv | $1,396 · 55.7 % · −$13,689 · 0.224 | 0.194 |
| S4.wide7.hnone.gdl | $1,371 · 57.0 % · −$14,874 · 0.209 | 0.651 |

**No confirmed champion** — the candidate fails the preregistered holdout confirm
(Sharpe 0.180 < 0.30). Reported as designed; the bar structure did its job.

## The two mechanism discoveries

1. **The delta gate (`gdl`) is the single best addition of the campaign so far.** A 1-minute
   up/down-tick cumulative-delta proxy — the VWAP Flux manual's own documented volume mode,
   re-added as CONTEXT exactly as directed — appears in the top dev rows almost uniformly.
   Best member anywhere: `S4.narrow6.hnone.gdl` dev Sharpe **0.355** (vs 0.176 for S1, 0.160
   for plain S4), 66.5 % positive, **$104.6/trade — at his $103 level**; holdout 0.783/77.8 %.
   Flow-direction agreement is genuine information on this instrument at this cadence.
2. **Session-level halts do what per-trade caps could not** (W02): h1300 pulls S4 worst weeks
   inside −$15k while keeping the hit rate — confirming the W02 diagnosis (tail = intra-week
   accumulation) and the D-gate-generalization design.

Also real: fast members + flow filter beat the full ensemble (narrow6.gdl > all13.gdl on
Sharpe), i.e., **filtering beats averaging** when the filter carries orthogonal information.

## What died

- **Multi-Osc reversal base: dead standalone** (dev Sharpe −0.159, holdout −0.7; the declared
  overlap→reversal-bar construction loses money at 1-min NQ). Kept as a possible *gate* only.
- **CumDelta as a standalone entry engine: marginal** (0.137 dev) — its information is already
  better used as the `gdl` gate on S4.
- SJB deferred (W04+): its only mechanical rule is a vendor series we cannot compute locally.

## Multiplicity and honesty

91 rows were computed; the top of any sorted table is selection-biased. The dev-bar +
holdout-confirm structure is the control, and it correctly refused to crown a champion. The
best portfolio rows (e.g., S1.none+S4.narrow6.hnone.gdl: dev 0.337, holdout 0.731 with a
−$807 worst week) remain **candidates for W05 confirmation**, not results. Holdout is on its
third read; only the virgin ≥ 2026-11-01 read arbitrates.

## Next (W04 running, W05 defined)

W04 = atomic ablation (single members, hysteresis/tilt/block marginals). W05 = freeze the
top 3 W03/W04 composites as named challengers, preregister the champion-vs-challenger
virgin-forward protocol, and stop touching them.
