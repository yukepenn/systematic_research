# WE_W32 — CLOCK & TOD THRESHOLD · REPORT

**All arms rejected — with a disclosed harness defect that limits how far the conclusion travels.**

| arm | pts/session | % in position | pts/bar | Sharpe | flips |
|---|---|---|---|---|---|
| C clock = 1 min (this wave's reference) | 4.85 | 17.13 % | 0.0208 | 0.139 | 553,982 |
| C clock = 3 min | 3.84 | 16.65 % | 0.0169 | 0.105 | 414,027 |
| C clock = 5 min | 0.72 | 15.67 % | 0.0034 | 0.021 | 350,943 |
| C union {1,3,5} min | 2.49 | 14.95 % | 0.0122 | 0.073 | — |
| T TOD-normalised threshold | 3.17 | 24.41 % | 0.0095 | 0.075 | 544,747 |

## HARNESS DEFECT (disclosed, not hidden)

This wave re-implemented the ratchet (`ratchet_targets`) to make the clock a parameter, and
that re-implementation **drops the HTF tilt, the hysteresis and the combiner**. Its 1-min arm
scores **4.85 pts/session against the real object's 10.62**, so it is a weaker engine, and
**no arm here is comparable to the campaign's baseline**. W32 lacked the B1-style reproduction
check that W01 had; that check has been added to W33 and is now mandatory for every new
harness. The *relative* comparison across clocks is internally valid; the absolute conclusion
"coarser clocks are worse" is only established inside the simplified engine.

## What is nonetheless established

- The TOD arm did **not** fall into campaign #3's M1 failure mode — the distortion signature is
  E[f|flip] 1.122 vs E[f|all] 1.064, against M1's 1.536 vs 1.000. It lost cleanly, on its
  merits, with the thing that broke M1 explicitly measured and absent.
- Coarser clocks reduce flip count monotonically (554k → 414k → 351k) and reduce production
  faster than they reduce flips, i.e. the surviving flips are not better enough to compensate.
  Campaign #1's 3-min advantage ($27.18/trade vs $15.76) did **not** transfer to a voted,
  throttled, session-boxed object.

## Status
The clock axis is **provisionally closed** pending a re-run on the true engine; the TOD axis is
closed on its own evidence.
