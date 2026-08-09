# S2_SELTIME R2 — Product A adjudication

**STATUS: NOT PROMOTED**

Per `r2_spec.yaml`'s frozen interpretation: S2's eligibility rule (block new commitments/
reversals 02:00-08:00 ET) applied to Product A's own Solar E10 leg `T`, before tilt/c1_50
recombination; B-MOM (`B`) and every other component untouched. Code: `src/r2_battery.py`
(`product_a_exec`), `src/r2_metrics.py`. Independently adversarially verified (workflow, 3
parallel reviewers on Product A/NQ/MNQ) — **CONFIRMED, no bug found**, every number in
`out/r2/summary_A.json` reproduces exactly from the raw saved arrays.

## Headline numbers (incumbent -> +S2)

| metric | incumbent | +S2 | delta |
|---|---:|---:|---:|
| Net | $177,924.40 | $180,347.10 | +$2,422.70 |
| Sharpe | 1.1770 | 1.1889 | +0.0119 |
| CDaR₀.₉₅ | $14,323.08 | $14,729.16 | **−$406.09 (worse)** |
| maxDD (EOD) | $17,192.90 | $17,830.60 | worse |
| Capital needed (1x stress, 20% DD-thr) | $254,709 | $247,764 | **−$6,945 (better)** |

(Incumbent net is within 1.2% of `BASELINE_MODELS.md`'s $175,798.80 — the small gap is the
disclosed, deliberate session-relative-C4 fix vs. whatever exact convention produced that
historical figure, not a bug; incumbent-vs-S2 uses identical code, so the relative comparison
is unaffected either way.)

## Gate results

| gate | result |
|---|---|
| A (Sharpe↑ AND CDaR↑ AND top10-retention≥95%) | **FAIL** — Sharpe improves marginally, but CDaR gets WORSE (not better); this alone fails gate A |
| B (chronology, ≥4/5 years agree) | **FAIL** — 3/5 years positive (2022: −0.033, 2025: −0.024 negative; 2023/2024/2026 positive) |
| C (tail preservation) | **FAIL, narrowly** — top-1% retention 94.9% (passes), top-20-move retention **88.1%** (fails the 90% bar by 1.9pp), long-share drift 1.4pp (well inside the 15pp bar) |

Two of three required gates fail decisively; the third fails narrowly on one of its three
sub-conditions. Per the frozen verdict rule (gate_A AND gate_B AND gate_C required), this is a
clean, unambiguous FAIL on Product A's own numbers.

## Robustness context

- **Bootstrap P(Δmean>0) = 0.646** — a coin-flip-adjacent confidence level, well below any bar
  this program has used elsewhere ("strong" = 0.85+).
- **D7-boundary split**: pre-2024-08-05 ΔSharpe +0.0069, post +0.0176 — both now POSITIVE
  (unlike the original isolated-diagnostic's pre-negative/post-positive split), i.e. combining
  with B-MOM meaningfully dampens the diagnostic-level D7 asymmetry, but the post-boundary period
  still carries more than double the pre-boundary benefit.
- **2-tick-equivalent cost stress**: Δ Sharpe stays positive under a conservative extra-friction
  stress (+0.0207) — cost is not the reason this fails.
- **Capital map**: modestly better (~2.7% less bootstrap-implied capital needed at the 20%-DD
  threshold) — a real, small, genuine capital-efficiency signal.

## Why NOT PROMOTED, not INCONCLUSIVE

The evidence is not "imperfect mechanism, strong product-level result" (the case the directive
says should still promote) — it is a **direct product-level gate failure on 2 of 3 required
gates**, including CDaR moving the WRONG direction outright. A small, genuine capital-efficiency
gain does not, on its own, meet the spec's own bar (capital-neutral-or-better is a necessary
condition alongside passing gates, not a substitute for them). This is a clean NOT PROMOTED, not
a close call requiring INCONCLUSIVE.

## Disposition

`SolarWaveSMMaster_v3.cs` remains the incumbent. No `_v4` created. `BASELINE_MODELS.md` /
`CURRENT_TRUTH.md` updated to record that R2 ran and did not promote (see those files' own
change log), not to change Product A's own definition.
