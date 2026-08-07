# B01a — DR05-H1 calibration result

_2026-08-07 · 19,311 DC segments (theta=179 ticks) on 1,620,044 one-minute closes 2022-01→2026-07 · driver `src/analytics/b01a_h1.py` · constants frozen in DR-05.md._

## VERDICT: **FAIL**  (arm a: PASS, arm b: FAIL)

## Arm (a) — yearly mean overshoot, band [89.5, 268.5] ticks

```
      count    mean  in_band
year                        
2022   4353  208.59     True
2023   2012  204.67     True
2024   2988  214.55     True
2025   5129  217.07     True
2026   4829  217.86     True
```

## Arm (b) — failed-flip continuation vs unconditional

- failed flips: 4,570 of 19,311 (23.7%)
- pooled median continuation: failed -3.00 ticks vs unconditional -1.00 ticks → diff -2.00 (requirement ≤ −10)
- sign stability: worse in 3/5 years (requirement ≥ 4)
- one-sided Mann-Whitney p = 1.71e-01 (requirement < 0.05)

```
 year  n_flips  n_failed  med_uncond  med_failed  diff  worse
 2022     4353      1062         0.0        -6.5  -6.5   True
 2023     2012       605        -3.0        -3.0   0.0  False
 2024     2988       802        -5.0        -2.0   3.0  False
 2025     5129      1135        -1.0        -3.0  -2.0   True
 2026     4829       967         1.0        -2.5  -3.5   True
```

## Ledger
`b01a_h1_ledger.csv.gz` — per-flip omega, 60-min max overshoot, failure flag, re-cross bar (≥10-tick margin), forward returns at 15/30/60/120 min, year/side/session strata. Feeds DR05-H2 (B01b) if PASS; kills it unbuilt if FAIL.