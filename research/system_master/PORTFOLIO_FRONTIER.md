# PORTFOLIO_FRONTIER — Multi-Engine NQ Portfolio Evidence

_2026-08-08. Sources: `runs/SM05_BMOM_PORTFOLIO/out/*` (frozen-spec measurement),
`runs/SM09_LEVERAGE_FRONTIER/out/*`. All dev 2022-01→2026-05-31, union session
calendar, legs vol-matched to SOLAR dev σ, portfolios rescaled to SOLAR σ._

## Verdicts (preregistered gates, SM05 spec)

- **SOLAR+BMOM: PASSES ALL GATES AT EVERY CELL w=0.2..0.5 (plateau met 5/5).**
  w=1/3: ΔlogG +0.237 (P≤0 0.020), ΔSharpe +0.349, Calmar 1.222, maxDD −$32,145,
  worst month −$14,951; w=0.5: Sharpe 1.197, maxDD −$28,514 (−29% vs Solar). H1/H2
  positive everywhere. FACT — advanced to candidate (pending holdout).
- **SOLAR+B1 two-way: FAILS every cell** (H1 drag at all w; bootstrap p 0.19-0.35). FACT
- **Three-ways pass as points:** 0.5/0.3/0.2 (H1 +0.073, worst month −$10,259) robust;
  thirds knife-edge (H1 +0.009). B1 belongs ONLY as a small sleeve inside a three-way. FACT
- **PORT_TILT_532** (tilt-Solar composition): Sharpe 1.222, maxDD −$27,209, worst
  month −$8,695, P(dmean≤0)=0.017 — best object on every headline; see LEVERAGE_FRONTIER. FACT

## Diversification scorecard (vs SOLAR)

| leg | ρ_full | ρ Solar-losing-days | ρ losing-weeks | DD-corr | worst-20 Solar days leg≥0 | top-20 gain overlap |
|---|---|---|---|---|---|---|
| BMOM | 0.344 | **0.043** | 0.052 | 0.054 | 45% | 8/20 (**gains crowd**) |
| B1 | 0.015 | 0.157 | — | −0.280 | 40% | 3/20 |

The owner-directive thesis is confirmed: B-MOM's diversification is **loss-side-only**
(shared upside, independent losses) — exactly the useful kind for DD/TUW; but gain-side
crowding means combined same-day gross exposure must be capped in the master spec. FACT

## Regime symmetry warning (standing)

BOTH engines are current-regime engines: B-MOM pre-2022 PF 1.013 (W10 REGIME-LOCAL);
Solar pre-2022 net −$9.0k (SM06 REGIME_LOCAL). The portfolio premium is a
current-regime object; MONITOR-01 (r-statistic) plus a B-MOM decay monitor are
mandatory operational attachments. B1 is the only leg with pre-2022 structure
(Sharpe 0.52 historical) and the weakest dev leg — robustness and performance point at
different legs; the 0.5/0.3/0.2 shape holds both. INFERENCE

## ES5 note

Daily ES5 is flat across all portfolios (−$3.7k..−$4.3k): the diversification benefit
lives at week/month horizon (worst-month, roll60, TUW, streaks), NOT in the daily loss
tail. Any DD-based deleveraging should key off rolling-60/monthly aggregates. FACT
