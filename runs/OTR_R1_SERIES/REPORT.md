# OTR_R1_SERIES report (2026-08-24)

## R1.1 master rescore ($4.18/RT, canonical ledger)
| | target (pixels) | CAND1 (frozen) | T1+rev (new base) |
|---|---|---|---|
| trades | 4,351 (2166L/2185S) | 4,665 (2379/2286) | 5,403 (2703/2700) |
| net | 292,172.82 | 234,235.30 | 216,890.46 |
| WR | 40.29 | 39.79 | 39.46 |
| PF | 1.18 | 1.129 | 1.104 |
| DD | −32,677.42 | −33,530.90 | −37,746.34 |
| hold | 94.15 | 74.92 | 96.24 |
| largest win | 7,705.82 | 7,450.82 | **7,705.82 ✓ exact** |
| largest loss | −4,449.18 | **−4,449.18 ✓ exact** | **−4,449.18 ✓ exact** |

## R1.2 — the decisive result: per-day/per-trade forensics (OTRIMG-0003 Daily table)
Subset-diff of our trade multisets against the trader's own per-day W/L structure:
- **Engine/conventions/data validated to the CENT**: whole days reproduce trade-for-
  trade (1/10: 9/9, 1/11: 4/4 exact; 1/6 within $140 price-epsilon), and on other
  days the target equals our set minus an exact removable subset (residual $0.00 on
  1/3, 1/5, 1/9).
- **FALSIFIED: the 04:00–16:00 SelTime window** (OTR-S-CAND1's core): the target
  contains overnight trades the window forbids (e.g. L 21:39→06:44 +2,270.82 cent-
  exact) and windowed variants destroy cent-matches. OTR-S-CAND1 is retired.
- **FALSIFIED: T3 (strengthen) entry participation**: every ±3-signal entry in our
  runs is absent from the cent-exact target days; entries are T1 flips (reversal
  chains) — plus evidence of a close-basis (PullbackEarly=FALSE) T2 layer: the one
  missing 1/17 trade (−274.18) matches a late-mode T2 short filled 20:48 at
  14712.75 to the cent, while our EARLY-mode T2 stream cannot produce it. The
  trader's panel exposes no PullbackEarly bool (hard-coded in his code).
- **A sparse deterministic entry-gate remains unidentified** (~15 skipped flips in
  11 days; afternoon clusters, most-but-not-all evening entries, at least once
  direction-conditional). Single-rule candidates falsified so far: time windows,
  T3-gates, session-PnL limits, consecutive-loss counts, level filters, pure
  resume-at-open. A 5-family parallel hunt (wf_a7316a88) is running; labels are
  cent-certain on 5 days.
- Feb-2025 window vector: same-base comparisons show version churn within Feb
  (LossLimit/DSTM/commission experiments) — windows W0212+ belong to changed builds;
  W0206 was a Quantity=3 experiment (comm $12.54/trade), excluded.

## R1.3 LossLimit semantics: inconclusive at current base (all four modes miss the
20/4 trade-count targets while the entry base overtrades); re-run after gate lands.

## Status: MAJOR PROGRESS, gate identification pending. Class-B+ base model:
entry_types=(1,) [+ late-T2 layer TBD], reverse_on_flip, inclusive touch exit,
session-close flat, no time window, comm $4.18/RT, plus unidentified sparse gate.
