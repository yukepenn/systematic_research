# U5 — soft residual-information weighting on Product A

**Disposition: Stage 1 diagnostic complete. Stage 2 construction NOT ATTEMPTED. NOT SUPPORTED.**
(Persisted here by the orchestrating session from the subagent's returned text — its Write tool
blocked direct creation of this file.)

## Setup

Product-A `SCALE_IN` bars, canonical window (2022-01-03..2026-05-29): **8,137**, from **2,093
distinct trading blocks** (of 4,809 total; a block can scale in more than once — mean 3.9, max 21
scale-ins/block). Block "eventual net_pnl" = `run_pnl_A_dollars` at the block's own last bar (max
`age_bars_A` within `block_id_A`, immediately before EXIT starts a new block_id). Four features
tested, all aligned to trade direction at the scale-in bar (R4/R5's own convention),
`direction_x_volume` excluded per spec (R5: fully tail-blind, disqualified outright): `clv_aligned`
(R4's CLV lead), `vwap_aligned` (R5's vwap-displacement lead), `stvr`=`short_term_vol_ratio`
(non-directional, R5 precedent), `bad_rejection` (R5's rejection lead, aligned).

## Stage 1 point 1 — literal test: does the feature predict the block's eventual total net_pnl?

| feature | raw Spearman | residualized Spearman | OLS ΔR² | year-sign-stability |
|---|---:|---:|---:|---|
| `clv_aligned` | +0.100 | +0.067 | +0.0018 | 5/5 (0.040-0.097, monotone decay) |
| **`vwap_aligned`** | **+0.329** | **+0.212** | **+0.0417** | **5/5 (0.157-0.248, all years)** |
| `stvr` | +0.039 | -0.020 | +0.0007 | 1/5 (sign-flips every year) |
| `bad_rejection` | -0.014 | -0.013 | +0.0001 | 4/5 but magnitude ≈0 every year |

By this literal test, `vwap_aligned` is the strongest residualized relationship found anywhere in
the R4/R5/U5 information program — over 4x R4's CLV (ΔR² 0.009) and over 3.5x R5's
`direction_x_volume` (ΔR² 0.0118), stable in all 5 years, no sign flip.

## Stage 1 point 2 — right-tail check (top-20 / bottom-20 Product-A blocks by net_pnl)

| feature | top-20 % "bad" (bottom tercile) | bottom-20 % "bad" | top-20 blocks fully blocked by hard filter |
|---|---:|---:|---:|
| `clv_aligned` | 25.7% | 42.6% | 0/20 |
| **`vwap_aligned`** | **15.6%** | **62.6%** | **0/20** |
| `stvr` | 28.1% | 38.3% | 0/20 |

`vwap_aligned` passes cleanly: top-20 winners' scale-ins are "bad" at roughly half the
population base rate (~33%), bottom-20 losers' at nearly double, zero top-20 blocks would be
entirely blocked by a naive filter. **On the literal Stage-1 letter alone, this clears the
Stage-2 gate.**

## The decisive check that stopped construction: forward-only robustness

A soft-weighting rule can only affect P&L accrued **after** the scale-in bar. `block_final_pnl`
conflates already-banked P&L with forward P&L, and a position can only be far from session VWAP
in its own favor *because it has already moved* — so `vwap_aligned` may just be measuring "how
profitable is this position already," not real forward information. Tested directly via
`forward_pnl = block_final_pnl − run_pnl_A_dollars(at the scale-in bar)`:

| feature | raw ρ (forward-only) | residualized ρ (forward-only) | ΔR² (forward-only) | year-sign-stability (forward-only) |
|---|---:|---:|---:|---|
| `clv_aligned` | -0.006 | -0.009 | +0.00002 | 4/5, magnitude ≈0 every year |
| `vwap_aligned` | +0.023 | **+0.003** | **+0.0006** | **2/5, sign-flips 2024/2025/2026** |
| `stvr` | +0.006 | -0.002 | +0.00002 | 1/5 |
| `bad_rejection` | -0.002 | -0.003 | +0.0002 | 3/5, magnitude ≈0 |

Every feature's signal collapses to noise once isolated to forward-only outcome. `vwap_aligned`'s
residualized Spearman falls 0.212→0.003 (ΔR² 0.042→0.0006), year-stability falls 5/5→2/5 with
sign flips in 2024 (-0.023), 2025 (-0.043), 2026 (-0.030). Restricting to one observation per
block (first scale-in only, n=2,093) reproduces the pattern: `vwap_aligned` total ρ=0.151 vs
forward-only ρ=0.035; `clv_aligned` total ρ=0.105 vs forward-only ρ=0.009.

**Mechanism, confirmed directly**: `Spearman(vwap_aligned, run_pnl_A_dollars already-banked-at-
scale-in) = 0.643` — `vwap_aligned` is substantially a proxy for how profitable the position
already is at the moment of the scale-in, not a time-in-block proxy
(`Spearman(vwap_aligned, age_bars_A) = 0.020`, essentially zero). A block already 6-12 ATR-units
in its favor has, by construction, already banked much of its eventual profit; scaling in there
looks good for reasons unrelated to the scale-in itself. This is the same class of artifact
`R2B_VERDICT.md` names as this campaign's standing example of the promotion bar — caught here at
the diagnostic stage, before any construction was built.

`block_final_mfe` and `block_final_giveback_ratio` show the same qualitative pattern (large raw
correlations for `vwap_aligned`: MFE +0.255, giveback_ratio -0.347; shrinking sharply on
residualization: +0.095, -0.048) — consistent with the same confound, not independent
corroboration.

## Verdict

**Stage 1: diagnostic complete.** The literal block-total-outcome test finds a real, 5/5-year-
stable, right-tail-safe relationship for `vwap_disp_atr` (aligned) at Product-A SCALE_IN moments
— the strongest single finding across R4+R5+U5. **This does not survive isolation to the forward
(post-scale-in) component of block outcome** — the only component an increment-sizing rule could
capture — collapsing on residualized Spearman (0.212→0.003), ΔR² (0.042→0.0006), year-stability
(5/5→2/5 with recent-year sign flips), with a directly confirmed sunk-profit mechanism (0.64
correlation with already-banked P&L). `clv_aligned` shows the same pattern at smaller scale.
`short_term_vol_ratio` and `rejected_upper/lower_break` show no usable signal in either framing.

**Stage 2: NOT ATTEMPTED.** Per spec.yaml's explicit conditional ("if weak/inconsistent/
tail-dangerous, STOP HERE... do not force a construction") — the forward-only check is the
economically correct test for an increment-sizing rule, and every candidate fails it. Building
the preregistered tercile-multiplier candidate would size increments on information that is
demonstrably about the past, not the future — plausibly adding only commission/rounding noise,
no real edge. **NOT SUPPORTED.** Product A (`SolarWaveSMMaster_v4`) is unchanged; no candidate
exists to run through the full battery, 2022-2025 delta, or 2026 extension because none was
built.
