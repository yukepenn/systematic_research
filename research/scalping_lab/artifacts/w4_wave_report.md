# W4 wave synthesis — 4 kills + 1 label map (2026-08-08)

Spec: `specs/W4_alpha_wave1.md` (frozen 2db9058 before readouts). Five families run in
parallel; per-family reports in `artifacts/w4_*/`. All numbers verified against saved
stdout/CSVs (spot-checked by orchestrator). Amendment-5 KPI: **B×4 + labels with W5 seed.**

## Verdicts

| Family | Verdict | Decisive numbers |
|---|---|---|
| W4-A FSS-1 impulse→pullback→rebreak | **KILL** (0/48 pass; negative plateau) | market net C1 −2.2..−3.9t (max CI_hi −1.29); primary w30/I12 −3.4..−3.9t; P(tgt) 0.19–0.27 vs BE 0.31–0.34 |
| W4-A passive limit variant | **KILL** | net C1p (1.872t friction) −3.0..−3.8t; fill rate 72–87%; **passive GROSS worse than market gross (−1.50 vs −0.93): adverse selection exceeds the ~1t friction saving** |
| W4-B S2a (owner seed, frozen params) | **KILL at this parameterization** | primary 3-min fixed-time net C1 −1.675t (n=109, CI [−12.3,+11.0] — wide but gate requires CI_lo>−0.5); brackets −4.0/−4.2t with CI<0; long side −11.6t CI<0. Short side +13.5t point est. (n=43, CI straddles 0) logged as OBSERVATION only |
| W4-C FSS-5 sweep→reclaim | **KILL** (0/144) | reclaim −2.1..−4.6t CI<0 everywhere; continuation mirror also −2.4..−3.1t; only 5–7% of sweeps reclaim within 60s |
| W4-D H-B5 spikes | **KILL** | pooled P(CONT)=0.390 < P(REV)=0.407 — no continuation bias; the one frozen-trigger cell (low 10s-retracement, P(CONT)=0.87) is outcome-overlap confounded and its honest +10s-entry readout lost −3.46t C1 CI<0 |
| W4-E CLEAN_MOVE | **labels delivered** | see below |

## The cross-family FACT pattern (all our own data)

1. Every entry trigger tested in this campaign lands P(target-first) ≈ 0.20–0.30 against
   break-evens 0.31–0.40. No family has closed the gap; most don't move it at all.
2. **The entry point pays a structural path toll**: from any decision second,
   P(−4t before +8t) ≈ 0.63 both directions; among paths that DO reach +20t within 60s,
   median pre-target drawdown = 7.5t (p90 = 29.5t); only ~42% of +20t reachers are
   "clean" at MAE≤6t.
3. **Passive entries do not escape the toll** (W4-A): limit fills select the
   continuing-against paths; gross degrades by more than the spread saved. The owner's
   limit-order intuition is answered for THIS trigger class: at mechanical pullback
   levels, the queue fill is adversely selected. (Not a universal claim about limit
   orders — only about these locations.)
4. Level events (ON/OR extremes) carry no exploitable asymmetry in EITHER direction at
   C1 — the "sweep→reclaim" story and the "sweep→continuation" story both lose.
5. Spikes have no continuation bias (49:51 cont:rev among resolved).

## The W5 seed (the only positive signal in the wave)

CLEAN vs DIRTY same-direction moves separate on (day-clustered CIs exclude 0):
- **deeper contrarian pre-move**: ret30 median −15.0t before clean-up vs −5.0t before
  dirty-up (effect −0.26 to −0.30 across ret5/10/30/60);
- **higher path efficiency**: eff60 0.140 vs 0.112 (effect +0.19);
- **aligned (contrarian) tick flow**: sflow10 effect −0.19;
- NOT vol, NOT spread, NOT activity (clean-dirty is not a volatility proxy).

INFERENCE: our triggers have been consistently EARLY. Clean owner-scale moves begin
after a DEEPER, more orderly counter-move than the ones we've been buying. W5-1 must
test a wait-deeper entry: enter toward recovery only after retracement ≥ X ticks
(X from the clean-move distribution) AND eff/flow alignment — new frozen spec required;
the enrichment statistics here are conditioned on the future and prove nothing yet.

## Data notes
- s20250902: L2 feed truncated (sechilo ends 2025-09-01 23:59; zero RTH quote updates)
  → effectively L1-only for RTH; excluded by quote-alive filter (36-session pooling in
  W4-D/E). Recorded in DATA_INVENTORY terms as a permanent server defect.
- ES export pipeline CONFIRMED (pilots s20250814 ESU5 6.08M rows, s20260123 ESH6 8.83M
  rows, full sessions, L1+L2, uncapped) → FSS-10 unblocked; oldest-first archival of ES
  discovery sessions underway (rolling-window vanishing risk).

Stop-condition bookkeeping: waves without Pareto improvement = 2 (W3, W4). Untested
high-EVI space remains: deep-pullback/clean-entry family, fast FSS-2 variants (5–30s
clocks), FSS-3, FSS-6/7, FSS-10 ES conditional lift, ML conditional trade quality (§23).
