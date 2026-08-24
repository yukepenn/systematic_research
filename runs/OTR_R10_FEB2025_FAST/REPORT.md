# OTR_R10 — Feb-2025 fast build: TrendVector-cycle test (2026-08-24)

Grid: out/r10_grid.csv. Members F_TV2{E,L} x LL{none,2500} + F_T1 control.

## Verdict: F_TV2 (TV-cycle machine) REJECTED
- Decisive discriminator FAILED: on the 90-trade day (2/27) every TV-cycle
  member produces 26-31 trades (control: 22) — nobody explodes on HIS day —
  while TV-cycle explodes on the WRONG days (3/12-14: 145 vs tgt 60; 3/4-5:
  130 vs 70). Holds far too short (8-18 min vs 20-45). |n err| 50-112% vs
  control 43%.
- LL2500 literal halt reduces counts but does not fix the pattern.

## Unexpected positive finding (recorded, not tuned)
The T1 CONTROL's average-loss profile tracks the Feb-Mar daily series
remarkably well: −840/−945, −808/−869, −717/−742, −588/−596, −682/−704,
−658/−619 (sim/target per window) with same-scale holds. → the Feb-Mar
series is mostly T1-scale behavior; the load-bearing anomaly is the SINGLE
2/27 row (n90, avg loss −331), which no bounded member reproduces.
Leading reading: 2/27's 90-trade row belongs to a distinct one-off
experiment build (the trader demonstrably ran experiments daily in this era:
qty-3 on 2/6, commission churn, LossLimit add/remove) rather than to a
persistent "fast layer" of the flagship lineage. The June-2026 fast-sleeve
question stays open independently.
