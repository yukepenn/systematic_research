# OTR_R9 — hp-build pullback-qualification test (2026-08-24)

Members: T1 control | T2L (late/close-basis) | T2E (early), era-aware params,
frozen D-gate, 65-pt stop, comm 0. Grid: out/r9_grid.csv.

## Discriminator verdicts
- **D4 (control) PASS**: dev weeks fit T1 far better (0.284) than T2 modes
  (0.409/0.413) → dev = T1 build stands; machine split survives.
- **D1**: T2L cuts hp overtrade +39.5%→+23.8% (right direction, insufficient);
  T2E worsens (+49.3%). Overall hp distance: T1 0.421 ≤ T2L 0.435 < T2E 0.495.
- **D2**: in the two +18.5k hp trend weeks T2E swings nets by +8.5k/+17.9k
  toward target (+7,095 / +11,275 vs T1's −1,385 / −6,665) with larger avg
  wins — pullback qualification moves trend-week ECONOMICS the right way.
- **D3**: era-aware runs executed; no clean retune-tracking signal at this
  member granularity (counts move with era in both modes).

## Verdict
Pure T2-only entry is NOT the hp build (REJECTED as a complete model), but
pullback qualification is PARTIALLY SUPPORTED: it fixes the trend-week
economics (T2E) and the chop-week counts (T2L) — in DIFFERENT modes. The hp
build plausibly mixes T1 chains with pullback-qualified behavior or switches
by state; that is a NEW member family and stays unregistered until new labels
arrive (§5/§6 discipline). hp identification remains OPEN with a narrowed
shape: suppression-in-chop + pullback-priced entries in trend.
