> _Era banner (2026-08-18): this is **campaign #1's** final report package, frozen at its
> 2026-08-07 close. "Latest" is relative to that campaign only — repo truth has since advanced
> (campaigns #3/#4). Current state: `/STATE_OF_RESEARCH_20260818.md` and `/BASELINE_MODELS.md`.
> Within this package, `FINAL_PARETO_FRONTIER.md` supersedes this file's champion framing._

# Latest — 2026-08-07 · campaign CLOSED

**Status: closed at the formal stop condition** (constitution §23(B)). Three consecutive waves
produced no robust Pareto improvement and the remaining frontier is data-limited, not
method-limited. Start at [`../README.md`](../README.md).

## The result

**R5** — a volatility-normalised directional-change ensemble on 3-minute NQ, Type-1 signals only,
13 members at equal risk.

| Sharpe | net | max DD | positive years | P(Sharpe ≤ 0) |
|--:|--:|--:|--:|--:|
| **0.977** | $198,059 | −$39,126 | 5/5 | **0.0020** |

**Nothing is promotable.** The edge is real but ~3 % from a no-alpha null, it failed its one
external portability test (ES), and it cannot be certified by deflation on 4.6 years. This is a
well-characterised candidate, not a validated system.

## What closed the campaign

| wave | outcome |
|---|---|
| Wave 3 — H-014 | **PASS.** Volatility beats price normalisation by +0.728 Sharpe, **p = 0.009**. The mechanism is volatility-specific. The campaign's only clean significance result |
| Wave 3 — ES portability | **FAIL.** Ensemble Sharpe −0.329, P(Sharpe ≤ 0) = 0.829. Shape travels (Spearman 0.780), level does not |
| Wave 3 — C2 Type-3 sleeve | **REJECTED.** Best point estimates in the campaign, then cost 0.40 Sharpe on an adaptive core (P = 0.879). An effect that reverses with the core is an interaction |
| Wave 3 — C4, wave conditioning | **FAIL.** −0.33 Sharpe; 0.54–0.93 non-monotone |
| DSR as a promotion criterion | **ABANDONED.** 0.45–0.55 against a 0.90 bar; a defensible alternative pool gives 0.96. Dominated by a judgement call, not the data |

**R5 stands alone and unimproved.** Every sleeve and conditioning axis is closed.

## Integrity audit, 2026-08-07

A full audit of the reports (not the research) found eight bookkeeping defects — stale reports, a
mixed calendar in `final_pareto.csv`, one ensemble row computed with the wrong estimator, and an
understated vendor-parity bar count. **All are fixed or disclosed; none changed the ranking.**
Two remain open and are recorded in [`final_red_team.md`](final_red_team.md) §5: the config
registry stops at Wave 1b, and the immutable `runs/` convention lapsed after `RE01_open_parity`.

## Next, if resumed

1. Monitor the overshoot ratio `r` quarterly — free, no trading, the system's own early warning.
2. A third instrument (RTY/YM/CL) — portability is the only promotion criterion still open.
3. Complementary families — never built; see [`complementary_families.md`](complementary_families.md).
4. Genuinely forward data after a freeze. No clean historical out-of-sample window remains.
