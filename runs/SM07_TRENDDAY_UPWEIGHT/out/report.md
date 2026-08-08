# SM07 — Morning Trend-Day Up-weight: FAIL (all arms)

_2026-08-08. Two-phase frozen procedure: classifier constants frozen on 2006-2021 and
committed BEFORE the single dev read (`out/frozen_classifier.json`, commit history).
Results: `out/results.csv` (seq 307-309)._

- FACT (phase 1, history): trend-day base rate 25.3%; best C1 (gap) precision 0.304 =
  1.2× lift with threshold at the GRID EDGE (g*=0.30); C2 (narrow IB + outside value)
  precision 0.168 — BELOW base rate; C3 precision = base rate. The morning information
  set barely sees trend days.
- FACT (phase 2, dev, matched exposure): C1 +$8,749 / dSharpe +0.019 / P(dmean)=0.189
  → fails P<0.10; C2 −$9,485 (negative); C3 +$241 (flat). All three arms FAIL.
- INFERENCE: the external prior (DR_SM_B EVI-5, practitioner trend-day literature) does
  not survive local test at NQ/E10 granularity — gap size and IB narrowness are not
  usable morning classifiers for up-weighting this engine. EXTERNAL PRIOR ≠ local edge.
- Registry: seq 307-309 FAIL. Axis closed (constants may not be re-tuned; a future
  attempt requires a mechanically different information set, e.g. cross-asset state).
