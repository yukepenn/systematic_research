# GENESIS_BASELINES — RESULT: 8/8 rows produced (7 NULL controls · 1 DEFECT)

Executes `spec.yaml` (committed `0440f30` before results). Trials `G00001–G00008`. All structural
gates PASS (SEAL, POPULATION, COST_MODEL, MULTIPLICITY — zero search). Program-printed table in
`out/baseline_table.csv`, weekly series in `out/weekly_net_series.csv`.

## The first benchmark the incumbent has ever had

239 ISO weeks (2022-01-03 → 2026-07-31), 1 contract, $18.80/ctrRT, $20/pt:

| baseline | net $/wk | t | maxDD | net @ $20,245 DD | %pos | worst wk |
|---|---:|---:|---:|---:|---:|---:|
| B0 cash | 0 | — | 0 | — | — | 0 |
| B1a always-long (held) | 718 | 1.02 | 99,555 | **146** | 54.4 | −37,555 |
| B1b long RTH only | 86 | 0.15 | 92,541 | 19 | 51.5 | −23,279 |
| B2 TSMOM-63 daily | 136 | 0.19 | 125,419 | 22 | 53.6 | −43,023 |
| **B3 ORB 09:30–10:00** | **1,043** | **2.19** | 60,782 | **347** | **60.3** | −36,829 |
| B4 meanrev lag-1 | 978 | 1.26 | 78,523 | 252 | 51.9 | −35,444 |
| B5 incumbent P1_PCT *(artifact quote)* | 1,394 | 4.16 | 22,931 | 1,230 | 56.3 | −9,221 |
| B6 inv-vol B1a+B2 | 543 | 1.02 | 68,829 | 160 | 53.1 | −31,205 |

**Reading:** the incumbent **dominates every trivial rule** where it matters — t 4.16 vs best
control 2.19, and at common $20,245 DD it earns **3.5×** the best control. The strongest control is
**B3 (opening-range breakout, momentum-side)**: t 2.19, 60.3% positive weeks — a THIRD independent
sighting of modern-era intraday continuation (after W114's clock geometry and W118's mirror), on a
formulation frozen in the spec with zero search.

## Binding caveats (in the outputs)

- **Population**: B1–B6 run on all 239 weeks incl. 2022-H1; B5 quotes its recorded in-window
  aggregates (213 weeks). Fixed-DD column is the comparable one; treat cross-row deltas as
  indicative, not adjudicative.
- **B5 = DEFECT as specced**: no per-week series exists in `WE_W103_CONSOLIDATE/out/` — aggregates
  quoted, gross/Sharpe NA, nothing recomputed.
- Cost conventions per spec understate B4's true friction (RT charged only on sign change).
- **Controls cannot be promoted from this run.** Any pursuit of B3's class requires a new
  preregistered hypothesis (it lives inside atlas family H4, intraday momentum) and must face the
  portfolio-marginal gate that FOLLOW_MORNING failed, plus P1-overlap measurement.

**`LIVE ENABLED = NO` · $0 · evidence ceiling: DISCOVERY-layer controls on consumed data.**
