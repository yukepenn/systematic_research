# SM08 — HTF Agreement Tilt: PASS ALL FROZEN GATES (both arms) → CANDIDATE

_2026-08-08. Spec frozen before read (seq 310-311). Results: `out/results.csv`,
robustness in this report. Rule: E10 bar P&L ×1.25 when sign(vote_pend) agrees with
the prior-session daily SMA-state (n=50 / n=200), 1.0 otherwise (up-weight-only,
both sides symmetric), matched average exposure._

## Dev results (matched exposure vs BASE net $119,009 / Sharpe 0.709 / DD −$40,208)

| arm | Δnet | ΔSharpe | ΔlogG | ΔmaxDD | worst month | top-10 ret | H1/H2 | P(dmean≤0) | P(dSharpe≤0) |
|---|---|---|---|---|---|---|---|---|---|
| SMA50 (310) | **+$29,553** | **+0.174** | +0.127 | **+13.6%** | −$16,068 | 1.018 | +17.9/+34.2 | 0.0004 | 0.0001 |
| SMA200 (311) | +$28,568 | +0.180 | +0.123 | +13.6% | −$15,899 | 0.997 | +17.0/+33.4 | 0.0005 | 0.0000 |

Gates: logG ✓ Sharpe ✓ P<0.10 ✓✓ | H1/H2 same sign ✓ | top-10-day ≥0.90 ✓ |
two-point plateau (both n agree) ✓ → **PASS**.

## Robustness (beyond spec)

- FACT: yearly delta positive in ALL 5 dev years: 2022 +$3.4k, 2023 +$5.0k,
  2024 +$5.0k, 2025 +$11.7k, **2026 +$4.5k (cuts the Feb→Jun bleed 59%)**.
- FACT: **2006-2021 dead-regime stress: base −$8.2k → tilt +$10.2k; hist maxDD
  −$63.1k → −$53.6k.** The tilt improves the one regime where Solar was edge-less —
  the opposite of regime-local overfit. (Constants n=50/200 are literature defaults,
  not fitted anywhere.)
- FACT: engine-implementable integer form (target = round(mult·tgt·rescale), cap 13):
  net $130,534 (+9.7%), Sharpe 0.770, maxDD −$37,572 (−6.6%), top-10 ret 1.005 at
  matched mean |target| (2.787 vs 2.741). Quantization compresses the linear +25% to
  +9.7%; both forms improve every headline. `out/tilt50_rounded_daily.csv`.
- INFERENCE (mechanism): the tilt underweights counter-daily-trend exposure — exactly
  the SM02 atlas DD driver (shorts bleeding through 2024-2026 rallies) — while
  PRESERVING crisis shorts (agreement boosts shorts in downtrends; 2022 delta
  positive). Distinct from killed axes: not an entry gate (thesis §14), not
  suppression (C01 ML), not short-only gating (SOLAR-01), no exposure below baseline.

## Verdict

**CANDIDATE: SOLAR_HTF_TILT (SMA50 primary, SMA200 co-equal plateau member)** —
advances to the finalist package pending the single joint holdout read. Directive
answers: Q8 YES (a higher timeframe helps, as exposure shaping); Q9 MA information IS
incremental when applied as a tilt, NOT as a lagging entry gate.
Registry: seq 310-311 PASS_CANDIDATE.
