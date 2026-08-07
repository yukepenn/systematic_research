# Open-model validation

_2026-08-07 · suite: `src/analytics/test_solarwave.py` · model under test:
`solar_wave()` / `solar_wave_full()` in `src/analytics/solarwave.py` ·
**45 / 45 tests pass, exit code 0.**_

This document closes campaign section 6. It records what the open model is verified to do, how it
was verified, and — more importantly — the one thing it is *not* verified to do.

Run it with:

```
python src/analytics/test_solarwave.py
```

## 1. Why property tests rather than regression snapshots

A stored-output comparison would pass forever and teach nothing the moment the model is extended
along a new axis. Every test here asserts something that must be true of the *mathematics* —
monotonicity, strictness, causality, symmetry — so the suite keeps its value as the open model
grows axes the vendor never had. The one exception is category F, which is a direct comparison
against vendor output, because that is the gate that actually decides whether the recovery is real.

## 2. Coverage

| category | tests | what it pins down |
|---|--:|---|
| **A** recurrence | 16 | anchor and stop monotone inside a trend; stop exactly `S` from anchor; strict-break flips; **no look-ahead** |
| **B** signal state | 10 | sign of every signal type equals trend direction; wave resets on flip and only moves on flip/Type-3; Type-2 never collides with Type-1; **sign symmetry under price negation** |
| **D** determinism | 4 | bit-identical reruns; no state leakage across parameter runs; params object not mutated |
| **E** edge cases | 11 | exact-threshold touch does **not** flip; one tick beyond does; gaps; constant series; degenerate bars; 1-bar and 3-bar series; both warm-up conventions |
| **F** vendor parity | 9 | **every published series exact on every bar**, 9 configurations |
| **G** bounded ambiguity | 5 | the one known gap, pinned so it cannot silently widen |

Category C (cross-language Python↔C#) is covered operationally rather than by this suite: every
NinjaScript strategy in the campaign was gate-checked against the frozen canonical baseline
(2,915 trades / $146,440.60 / PF 1.132213) to the penny before any of its results were read, and
`SolarWaveOpenV1` reproduces the vendor baseline exactly in `runs/RE01_open_parity/`.

## 3. Vendor parity — the gate that matters

Exact on **every bar of every series** (`TrailingStop`, `TrendVector`, `Signal_Trade`,
`Signal_Trend`, `Signal_Wave`):

| probe | what it varies | bars |
|---|---|--:|
| `t2_canonical_1m` | canonical, 1-minute | 737,707 |
| `t2_probe_CONTROL` | canonical, probe window | 177,021 |
| `t2_probe_PS3` / `PS25` | PullbackSplit 3 / 25 | 354,042 |
| `t2_probe_TM45` | TrendMultiplier 45 | 177,021 |
| `t2_probe_SM240` | StopMultiplier 240 | 177,021 |
| `t2_probe_SS8WWS15` | SlowdownScan 8, WeakWeakSplit 15 | 177,021 |
| `t2_probe_PEfalse` | PullbackEarly false | 177,021 |
| `t2_probe_3m` | 3-minute bars | 59,015 |
| | **total** | **2,035,869** |

**2,035,869 bars · 9 configurations · zero mismatches on any series.**

> **Correction, 2026-08-07.** Campaign documents previously reported this as "1,436,860 bars".
> That figure was wrong and **understated** the evidence; the count above is the row count of the
> committed ledgers, printed by the suite itself. Every document quoting the old number has been
> corrected. The configuration count (9) was always right.

Type-2 specifically: 45,825 events at 0 false positives and 0 false negatives.

## 4. The one known gap — `V > S/2`

`TrendVector` carries a second ladder rung that is provably inert while `V ≤ S/2` and becomes
active above it. Its tie-breaking could not be resolved from published output alone, and resolving
it by any other means would have required attacking the vendor binary, which the campaign
constitution forbids. So the regime is **characterised and bounded rather than resolved**, and
category G pins the boundary with a dedicated probe at `TrendMultiplier = 135, StopMultiplier = 179`
(V/S = 0.754), 177,021 bars:

| series | agreement |
|---|--:|
| `TrailingStop` | **100.0000 %** |
| **every Type-1 flip** (1,077 of them) | **100.0000 %** |
| `Signal_Trade` overall | 98.586 % |
| `Signal_Trend` | 96.164 % |
| `TrendVector` | 69.757 % |
| `Signal_Wave` | 63.328 % |

The tested property is not "we match" — it is **"the divergence never touches Type-1."** Of the
2,504 disagreeing bars, **not one involves a Type-1 signal on either side**; every disagreement is
a Type-2 or Type-3 present in one and absent in the other.

**Why this does not affect any campaign conclusion.** Two independent reasons: (a) the recommended
architecture R5 and every promoted candidate use **Type-1 signals only**, which are exact even
here; and (b) the vendor's own presets sit at V/S = 0.503 (90/179) and 0.500 (60/120), inside the
resolved regime, and every experiment in the campaign was run with `V ≤ S/2`.

## 5. What this suite does *not* establish

- It does not validate any **economic** claim. Passing means the model reproduces the indicator,
  not that the indicator makes money.
- It does not cover **contract roll or missing-bar** handling at the data layer; those are NT8
  concerns, handled by the back-adjusted merge policy in the frozen baseline, not by this model.
- Category C is covered by strategy-level gate checks rather than by a direct Python↔C# series
  diff. A true series-level cross-language diff remains the cleanest available hardening step and
  is **not done**.
- The `V > S/2` tie-break is **unresolved**, not merely untested.

## 6. Provenance

The model was recovered by **behavioural observation of the indicator's own published output**.
No decryption, unpacking, patching, memory dumping or protection bypass was performed at any
point; the vendor assembly is unmodified and was never redistributed. The recovered logic is a
behavioural reimplementation and is **not** vendor source code.
