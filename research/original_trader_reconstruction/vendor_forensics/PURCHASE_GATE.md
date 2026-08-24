# PURCHASE GATE (owner directive 2026-08-24 §17-19) — status + pre-purchase parity kit

## Gate conditions (§18) — VWAP Flux status after the no-buy program

| Condition | Status |
|---|---|
| 1. Public/local evidence exhausted | NEARLY — manual, CMS changelog, chart images consumed; forum sweep done; local machine clean |
| 2. Component strongly identified as used | YES — 13/13 ordered parameter-label match (EV-019) |
| 3. Remaining uncertainty narrow + materially blocking | CONVERGING — see "what the no-buy clone recovered" below |
| 4. Licensed copy gives discriminating observable | YES — public NinjaScript series Signal_Trend/Signal_Trade/Signal_Cum_Delta + 5 plots + Fair Value, bar-by-bar |
| 5. Concrete parity test ready BEFORE purchase | YES — kit below |

**Recommendation state: NOT YET.** The remaining unknown is broader than "Signal_Trade
timing only" (WR/count residuals imply trigger + exit interactions). Continue no-buy
refinement; re-evaluate after the Signal_Trend/plot recovery is scored (§17).

## What the no-buy clone has recovered so far (§17 checklist)

- VWAP-layer plots: architecture selected on IMAGE fidelity — anchored-cumulative
  5-layer (smooth drift + rotation jumps matches both manual charts); frozen-segment
  staircase REJECTED. Level math: quantile-of-layers (QLEV) currently beats range
  interpolation behaviorally; both retained.
- Fair Value: leading = Median (50%) level of the layer set; alternatives (volume- or
  recency-weighted center, combined 5-segment VWAP) documented, undiscriminated.
- Signal_Trend: direction via cloud-break hysteresis implemented; strength via
  cumulative delta buildable (OF2 certified).
- Cumulative-delta state: DONE — ninZa-verbatim rule (>=ask buy / <=bid sell / inside
  EXCLUDED) certified on both clean tick sessions (corr delta-vs-ret 0.55/0.67).
- Signal gating: literal (Qty 3/trend, Split 5 bars) implemented.
- Risk behavior: intrabar 130-pt ($2,600) stop IDENTIFIED (EV-017 exact tail match).
- Residual: exact Signal_Trade trigger + the trader's exit rule (VF4 best D=3.40:
  net/hold/avg-win ✓, WR −15pp, count +41%).

## Pre-purchase parity kit (ready NOW, per §18 "do not buy first and decide later")

- Data: NQ 1-minute; contracts NQ MAR26/JUN26 (trader screenshots); test windows
  2026-05-10→22 (window A, consumed history) + 2026-03-08→13 + 2026-03-22→27.
- Exact settings to enter: Volume Base=BidAskPrice_RealVolume, Anchor 60, Amount 5,
  Trend 20/EMA, Levels 95/75/50/25/5, Qty 3, CloseThr 10, Split 5. (Also run manual
  values 20/5/14/EMA/100-70-50-30-0/4/80/30 as a control.)
- Export: chart-attached NinjaScript exporter (pattern: SolarWaveRKLedgerV2) writing
  per-bar: time, OHLCV, the 5 level plots, Fair Value, Signal_Trend, Signal_Trade,
  Signal_Cum_Delta. Tick Replay ON and OFF arms (the No-Tick-Replay tech question).
- Comparison script: bar-by-bar equality vs our anchored-layer implementation
  (`vwap_flux_family/src/run_vf4.py` layer/level arrays) + signal-timestamp diff table;
  acceptance = layer/level parity first, then signal-timing identification.
- Cost: $300 one-time (ninza.co). Purchase and license activation are OWNER actions.

## Priority if purchases eventually approved (§19)

1. VWAP Flux ($300) — after no-buy program completes its residual scoring.
2. Any product achieving a direct Track-B property match (none yet).
3. ThunderZilla ($700) — only on new evidence (currently MEDIUM/CONDITIONAL).
4. ApexFlow — only if the June TP short-hold sleeve stays unexplained after proxy work.
5. Infinity/Captain — LOW (meta/execution layers; capabilities reproducible in-house).
