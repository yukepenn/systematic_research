# SMV2AG_ADAPTIVE_CLAMP — REPORT

_Frozen spec: `runs/SMV2AG_ADAPTIVE_CLAMP/spec.yaml`. seq [424,425]. class R1_FAMILY_TEST +
DIAGNOSTIC — mechanism-expansion pass's #1-ranked idea. Authored by the orchestrator from the
execution agent's structured output — subagent Write tool refused REPORT.md; every number
independently reproduced exactly by red-team (verdict: CONFIRMED-with-corrections — the only
correction is this file itself resolving the missing-report gap, zero numeric issues)._

## Mechanism implemented
For each of the 13 incumbent members, `raw_m(t) = VolMult_m × sigma460(t)`. The clamp ceiling
`hi` in `resolve_s()` — normally the fixed 300.0pt (1200t) constant — becomes:
`ceil_m(t) = max(300.0pt, P-th percentile of {raw_m(t-1),...,raw_m(t-N)})`, computed strictly
causally (bar t's own raw_m(t) excluded), floored at 300.0pt so it can only widen relative to
the incumbent, never tighten below it. Fixed 300.0pt used during warmup (t < N+30).
Red-team traced the rolling→shift(1) algebra exactly and confirmed no same-bar lookahead, and
independently confirmed `member_states_adaptive()` is byte-identical to the incumbent
`member_states()` except this one term.

## sub_424 — adaptive sweep (6 arms, 2×3 grid: P∈{90,95,99} × N∈{460,920})

| arm | net $ | Sharpe | maxDD $ | CDaR₀.₉₅ $ | top10-day $ | retention vs control | Δsharpe | ΔCDaR | CANDIDATE |
|---|---|---|---|---|---|---|---|---|---|
| control_1200t_fixed | 119,009 | 0.7092 | 40,208 | 27,162 | 117,986 | 1.000 | — | — | — |
| P90_N460 | 139,138 | 0.8326 | 44,770 | 28,773 | 123,325 | 0.858 | +0.1233 | −1,612 | No |
| **P90_N920** | 142,651 | 0.8505 | 39,900 | **27,023** | 123,532 | 0.876 | +0.1412 | **+138** | No |
| P95_N460 | 137,373 | 0.8222 | 45,095 | 28,917 | 123,201 | 0.858 | +0.1129 | −1,755 | No |
| P95_N920 | 137,740 | 0.8235 | 44,770 | 28,776 | 123,325 | 0.857 | +0.1142 | −1,614 | No |
| P99_N460 | 141,934 | 0.8498 | 43,539 | 28,532 | 122,965 | 0.865 | +0.1406 | −1,371 | No |
| P99_N920 | 138,938 | 0.8311 | 44,345 | 28,616 | 122,965 | 0.854 | +0.1219 | −1,455 | No |

Every arm improves standalone Sharpe (+0.11 to +0.14) — but only **P90_N920** also improves
CDaR₀.₉₅ (+$138, the smallest possible win), and it fails the top-10-day retention floor
(87.6% vs the ≥95% requirement); the other five cells worsen CDaR₀.₉₅ outright. **Same
Sharpe/tail-risk tradeoff pattern SMV2AD found for the fixed-ceiling raise. 0/6 arms qualify.**

### Effective-ceiling-distribution diagnostic (vm30, the slowest member)
Does the adaptive ceiling actually widen more in 2026 than in calmer years — the entire
premise? Directionally yes, but concentrated and modest:

| arm | year | median (ticks) | p90 | p99 |
|---|---|---|---|---|
| P90_N920 | 2022 | 1200 | 1322 | 1937 |
| P90_N920 | 2023 | 1200 | 1200 | 1200 |
| P90_N920 | 2024 | 1200 | 1200 | 2448 |
| P90_N920 | **2025** | 1200 | 1645 | **4297** |
| P90_N920 | 2026 (partial) | 1314 | 1889 | 2144 |

The median ceiling stays pinned at exactly 1200t (incumbent) in every year except partial-2026;
widening is an upper-tail (p90/p99) effect only. **2025, not 2026, shows the most extreme p99
widening (~4300t)** — 2026 (partial) shows the highest median widening but a lower p99 than
2025. Consistent with the motivating premise but the widening is a thin upper-tail effect, not
a broad regime shift — plausibly explaining why it buys Sharpe (occasional extra room) without
reliably buying CDaR (tail-risk cost concentrates in drawdown days, not the rare widened bars).

Pooled across all 13 members, only 4.2-5.9% of member-bars are touched (vm30 alone: 15.0-20.3%)
— faster members rarely hit the 1200t ceiling in the first place, consistent with SMV2R
sub_381's finding that vm30 alone bears the binding.

### Portfolio blend (DAYONLY_DUAL6040 60/40)

| arm | net $ | Sharpe | CDaR₀.₉₅ $ | d_Sharpe vs champion | d_CDaR vs champion | beats champion |
|---|---|---|---|---|---|---|
| control | 194,416 | 1.2642 | 14,322 | — | — | — |
| P90_N460 | 201,515 | 1.3257 | 14,816 | +0.0614 | −494 | No |
| **P90_N920** | 204,521 | 1.3425 | **13,720** | +0.0782 | **+602** | **Yes** |
| P95_N460 | 200,263 | 1.3179 | 14,895 | +0.0536 | −573 | No |
| P95_N920 | 200,689 | 1.3193 | 14,835 | +0.0550 | −513 | No |
| P99_N460 | 203,537 | 1.3406 | 14,606 | +0.0763 | −283 | No |
| P99_N920 | 201,809 | 1.3289 | 14,692 | +0.0647 | −370 | No |

At the portfolio level P90_N920 beats the champion on both Sharpe and CDaR — disclosed as
informal context only, not part of the spec's standalone-only AND-rule verdict (matching
SMV2AD's own convention).

## sub_425 — old-regime screen: NONE_QUALIFIED
Zero candidates from sub_424, so per spec this screen is explicitly N/A (disclosed via
`status=NONE_QUALIFIED`, not silently skipped). Rebuild machinery retained parameterized for a
future wave.

## kill_or_keep
**CONFIRMED-NOT-BENEFICIAL.** 0/6 arms pass the AND-rule (Sharpe AND CDaR₀.₉₅ improve AND
≥95% top-10-day retention). Combined with SMV2AD's fixed-ceiling-raise finding (same
Sharpe-for-CDaR tradeoff), **both the fixed-raise and adaptive-widen-only clamp-ceiling ideas
are now exhausted.** Any future clamp idea needs a genuinely different shape (e.g. one that can
also tighten, explicitly out of scope here) to be worth a new spec.

## Disclosed interpretive calls (all confirmed by red-team as non-materially-biased)
1. Pandas' default linear interpolation used for the rolling percentile (spec silent on method).
2. Warmup mask applied by explicit bar-index threshold (t<N+30), verified to coincide exactly
   with the rolling-quantile's natural NaN behavior — redundant, not a mechanism change.
3. Scale-equivariance shortcut (percentile of vm·sigma computed as vm·percentile(sigma))
   verified mathematically exact and numerically cross-checked — a performance optimization.
4. Portfolio "beats champion" reported as informal context only, not part of the standalone
   AND-rule (matches the spec's own standalone-only verdict definition).

## Red-team disposition
Verdict: **CONFIRMED-with-corrections**. All numerical, causal-integrity, and gate-logic claims
(mechanism correctness, no lookahead, all 6 arms' metrics, effective-ceiling distribution,
portfolio blend, verdict application) independently reproduced exactly. No gate-shopping, no
loosened rule versus SMV2AD's precedent. The only correction is procedural — this REPORT.md
itself resolves the missing-deliverable gap red-team flagged; zero numeric corrections needed.

## Files
`out/adaptive_sweep.csv`, `out/effective_ceiling_distribution.csv`,
`out/pct_bars_ceiling_differs.csv`, `out/old_regime_screen.csv`, `out/portfolio_blend.csv`,
`out/portfolio_blend_424.csv`, `out/portfolio_curves_424.csv`, `out/sub424_verdict.json`,
`out/gates.csv`, `out/daily_adaptive_P{90,95,99}_N{460,920}.csv`. Code: `src/common.py`,
`src/adaptive.py`, `src/sub424_adaptive_sweep.py`, `src/sub425_old_regime.py`, `src/finalize.py`.
