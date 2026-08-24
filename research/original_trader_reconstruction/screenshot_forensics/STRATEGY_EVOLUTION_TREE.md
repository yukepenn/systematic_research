# STRATEGY EVOLUTION TREE (directive §35) — image-evidence-based, branches allowed

```
2023-01 ─ 2025-02-02   [backtest era, params already fixed]
   SolarWindRKSelTime  (A1-A5 = 90/179/5/10/10, Qty 1, NQ 1-min Last)
   │  master backtest 1/1/2023→2/2/2025: +$292,172.82, 4,351 tr, comm $4.18/RT
   │  captured 2/2/2025 11:57 PM — goes LIVE next morning (0005: 2/3/2025)
   │
   ├─ 2025-02-13..18  DSTM branch: + LossLimit (4000→2500), class renamed
   │     RKSelTimeDSTMa; commission experiments ($4.18 → $5.68 → $0 forever)
   │
   ├─ 2025-03..06  same engine, daily/2-day verification runs through the tariff-
   │     crash regime (26-90 trades/day weeks), then batch documentation Jul 6
   │
   ├─ 2025-07..10  ACCRETION phase (same A-params 90/179/5/10/10):
   │     + M… money-management group (E✔, Daily? 4500, Max? 2000)
   │     + St… stop group (Initial 65, Trailing 30, I 65, M 20)  → −$1,300 caps
   │     + Tr… (Qty 1), U… (E✔, 80), and a group above A1 ending …180?/140?
   │
   ├─ 2025-10-24..11-07  RETUNE: A3/A4/A5 5/10/10 → 3/6/9 (A2 179→180?)
   │     St group grows → 65/30/75/20/46/36; Thanksgiving −$15,365 week sits
   │     between retune steps; Dec adds [☑10/26/14/198?/180?/140?], [☑1], [☑80]
   │
   ├─ 2026-01  transition: 46/36→46/30, Entries/direction 1→2, extra toggles;
   │     Jan weeks −13,235 / −2,185 / +3,515
   │
   └─ 2026-02  NEW FLAGSHIP (VF-wrapper strategy, likely new class):
         head params ([30?]/16/0/10/15…) + embedded ninZa VWAP Flux stack
         (BidAskPrice_RealVolume / 60 / 5 / 20 EMA / 95-75-50-25-5 / 3 / 10 / 5)
         + account/wrapper hard stop → largest loss EXACTLY −$2,600 every week
         2/22→8/14 (first −2600: week 2/1-6; −1300 residue early weeks)
         │
         ├─ 2026-04-29  VARIANT A test (1 week): [☑10/20/14/198?/180?/140?] +
         │     [☑16/6/9] + two explicit windows 13:00-13:30 & 15:00-15:30 → reverted
         ├─ 2026-06-05  VARIANT B test: …30/70/2/20 + [14, 6] internal pair +
         │     [3,0,12,0] + checkbox bank → posted +$14,540 that week
         ├─ 2026-06-07..19  LIVE Trade-Performance reporting (+$11,860.30, +$8,503.24,
         │     real commission ≈$1.04/side; 23-33 tr/day, 20-34 min holds)
         └─ 2026-06-21..08-14  main VF layout, parameters FROZEN (verified identical
               5/23 vs 8/14), big-trend windows +$42,765 / +$49,940 / +$24,145
```

Notes:
- ONE continuous lineage plus a 2026 re-platform; no evidence of vendor turnkey
  strategies. Every panel is the author's own NinjaScript (obfuscated A-labels in
  2025; meaningful labels in 2026), wrapping licensed vendor indicators (Solar Wave
  RK math in 2025 — engine identity Class B from our recovered math; actual ninZa
  VWAP Flux in 2026 — Class A from labels+enum value).
- "Several strategies simultaneously" (author) = the account ran the flagship plus
  other sleeves; the weekly posts track ONE strategy per report. Variants A/B may be
  those other sleeves surfacing briefly in the Analyzer.
- Machines: creator (Feb-Mar 2025) → hp (Jul 2025+) → dev appears Oct 2025 → mimi
  appears Feb 2026; multiple hosts run the same template concurrently (multi-sleeve
  infrastructure), matching AS-1.
