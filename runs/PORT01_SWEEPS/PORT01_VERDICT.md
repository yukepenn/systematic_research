# PORTABILITY-01 verdict — 0/3, NQ-SPECIFIC ALPHA CONFIRMED

_2026-08-07 · preregistered at `b139cbb` before any result · jobs 5e4cdbefeb834edf
(YM), 07477199a89246b4 (RTY), aff52fd49e79499d (CL) · identical VolMult 6–30 grid,
sigma-scaled thresholds, tick-value-normalized clamps, per-instrument Lifetime
commissions, slip-1, 2022-01→2026-07-31, strict 1/N._

| market | ensemble net (1/N) | positive cells | Spearman shape vs NQ |
|---|---:|---:|---:|
| NQ (reference) | **+$198,059** | 13/13 | 1.000 |
| ES (campaign, prior) | −$12,455 | 8/13 | 0.780 |
| YM | **−$21,947** | 6/13 | (mid-grid positive, narrow catastrophic) |
| RTY | **−$17,006** | 4/13 | 0.341 (p=0.26) |
| CL | **−$12,218** | 0/13 | 0.231 (p=0.45) |

Preregistered rule: ≥2/3 positive = universal-mechanism support. **Result: 0/3.**

## Conclusions (binding for the final package)

1. **The persistence mechanism, as implemented, is NQ-specific.** Four external
   markets, zero after-cost successes. On CL not a single cell is positive.
2. The earlier "shape travels, level does not" consolation (ES, 0.78) does NOT
   generalize: RTY/CL shape correlations are statistically indistinguishable
   from zero. There is no evidence of a transportable structural law here.
3. Candidate mechanical explanation, reported not asserted: NQ's $20/point on a
   ~$5 tick gives it the lowest friction-per-sigma of the set (YM 4× worse per
   notional; CL's $10 tick + energy microstructure worse still). But a genuine
   structural edge should still show positive gross-of-friction shape transfer —
   RTY/CL do not deliver even that.
4. Constitution §20 penalty: all structural-alpha language must be removed from
   final claims. The honest classification of R5/R5-E10 is **"NQ-specific
   historical edge, 2022–2026, tail-concentrated, externally unvalidated."**
5. No rescue: per the spec, no per-instrument fitting or clamp retuning was run,
   and none may be run against these results.

Trials: seq 233–271 consumed (39 configs, 3 preregistered family reads).
Evidence: `ym_summary.json`, `ledgers_ym/`, `ledgers_rty/`, `ledgers_cl/`.
