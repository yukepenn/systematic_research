# V3/V4 verdict — POST_CAMPAIGN_AUDIT_01, AUDIT-A04

_2026-08-07 · verdict vocabulary fixed in the preregistered specs before results:
TRADE_PATH_EQUIVALENT / PERFORMANCE_SIMILAR_ONLY / NOT_EQUIVALENT._

## Verdict

**Trade-path level: `NOT_EQUIVALENT`.** **Ensemble level: `PERFORMANCE_SIMILAR_ONLY`.**

The half-tick snap in V4's `ResolveS()` alone changes individual member nets by up
to −49% (VolMult 6: $166,145 → $83,955; 7 of 13 members move ≥10%, the six
widest-threshold cells move ≤3.3%) while the 13-member strict-1/N ensembles remain
statistically indistinguishable (daily corr 0.9952, ΔSharpe +0.019, paired
circular-block P(Δ≤0) = 0.328; 95% CI for ΔSharpe [−0.064, +0.094], spanning
zero). Members that move up to 49% under a half-tick perturbation are not
"equivalent" in any executable sense; only the ensemble aggregate is robust. This
is the single-cell-fragility argument again, now measured on a clean pair.

## New finding: the published comparison was confounded

`V3_V4_EQUIVALENCE.md` compared committed V3 ledgers (produced with **StartUp=false**)
against committed V4 ledgers (produced with **StartUp=true**) and attributed every
difference to the tick-snap ("Cause: one line"). The attribution was incomplete: the
two runs also differed in an undocumented run-config parameter. Proof:

- The committed v4verify first fills (`Short SellShort 2022-01-03T09:03 @19751.25 …`)
  are byte-identical to a V3 run at StartUp=true — the StartUp signature, not a snap
  effect. The doc's own observation "V3 enters long at bar 39, V4 does not" is the
  StartUp difference.
- Audit re-runs isolate both factors:
  - `AUDIT02_V4_SWEEP_C` (V4, StartUp=true) reproduces all 13 committed v4verify
    ledgers **fill-by-fill EXACTLY** — the committed V4 evidence is deterministic
    and now correctly configured-documented.
  - `AUDIT02_V4_SWEEP_B` (V4, StartUp=false) provides the first clean tick-snap-only
    comparison against the committed V3 ledgers (below).

The confound does **not** overturn the published conclusion — on the clean pair the
ensemble-level statistics are quantitatively close to the published confounded ones
(corr 0.9952 vs 0.9949; ΔSharpe +0.019 vs +0.029) — but the published per-cell table
in `V3_V4_EQUIVALENCE.md` mixes two causes and its per-cell numbers should not be
cited as pure snap sensitivity. Use `research/audit/v3_v4_trade_diff.csv` instead.

## Clean matched-StartUp comparison (both engines StartUp=false, slip-1, Lifetime)

Basis: calendar-date-of-exit daily P&L, REALIZED_ONLY, 1,333-day union of the pair.

| vm | V3 net | V4 net | ratio | common fills (% of V3) |
|---:|---:|---:|---:|---:|
| 6 | $166,145 | $83,955 | 0.505 | 85.8% |
| 8 | $170,549 | $189,650 | 1.112 | 90.9% |
| 10 | $150,033 | $98,881 | 0.659 | 93.1% |
| 12 | $138,883 | $164,101 | 1.182 | 94.7% |
| 14 | $241,924 | $209,334 | 0.865 | 96.0% |
| 16 | $228,891 | $225,530 | 0.985 | 97.1% |
| 18 | $246,515 | $271,506 | 1.101 | 97.3% |
| 20 | $245,125 | $237,105 | 0.967 | 98.0% |
| 22 | $245,446 | $242,191 | 0.987 | 97.6% |
| 24 | $193,737 | $197,811 | 1.021 | 98.1% |
| 26 | $132,860 | $130,889 | 0.985 | 97.7% |
| 28 | $165,399 | $183,154 | 1.107 | 99.0% |
| 30 | $249,257 | $255,254 | 1.024 | 99.1% |

Ensemble: V3 net $198,058.82 (Sharpe 1.0100) vs V4 $191,489.32 (0.9911); mean
common-fill share 95.7%. Narrow cells diverge most (the snap moves the threshold by a
larger fraction of S when S is small) — exactly the mechanical expectation.

## Consequences

1. R5 remains defined on **V3** (continuous S), as published; nothing in this audit
   moves any published R5 number.
2. Neither discretisation is "correct"; the ensemble's insensitivity (ΔSharpe +0.019,
   P = 0.33) is a genuine robustness property, now established without the confound.
3. Any future executable implementation must pin: engine version, StartUp, and the
   snap policy — the audit-era spec.yaml schema already requires all three.
4. `V3_V4_EQUIVALENCE.md` stays on the record uncorrected (append-only evidence);
   this document supersedes its causal attribution.

Artifacts: `v3_v4_trade_diff.csv`, `v3_v4_daily_diff.csv`,
`v4c_reproduction_diff.csv` (C-arm 13/13 EXACT certificate),
`v4_startup_confound_diff.csv` (B-arm vs v4verify — the confound demonstration;
this file was briefly named `v4_reproduction_diff.csv`, which misread as a failed
reproduction — renamed on second-red-team finding); ledgers under
`runs/AUDIT02_V4_SWEEP_B/` and `runs/AUDIT02_V4_SWEEP_C/` with SHA-256 manifests
in `audit_evidence_hashes.json`; driver `src/analytics/audit02_v3v4.py`.
