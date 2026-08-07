# Leaderboard — post-Wave-1 (full history 2022-01 → 2026-07-31)

_Ranked by neighborhood-median analytic slip-1 net (single points carry ±$40-90k path noise — see WAVE1_report D2). "slip1" = net − trades×$9.53 (validated vs real slip-1 run to 0.3%). NOT promotions — Tier-2 confirmation (real slip-1, per-year, long/short, concentration) pending in Wave 1c._

| Rank | Config (Type-1 core) | net0 | trades | PF | slip1 | avg1 | nb-median slip1 |
|---|---|---|---|---|---|---|---|
| 1 | **3m · SM 230** | $301,638 | 5,442 | 1.097 | $249,776 | $45.90 | $174,581 |
| 2 | **3m · SM 250** | $270,410 | 4,843 | 1.092 | $224,255 | $46.30 | $224,256 |
| 3 | **3m · SM 200** | $255,035 | 6,648 | 1.075 | $191,679 | $28.83 | $191,679 |
| 4 | **3m · SM 180-190** | $256-271k | 7.1-7.6k | 1.073-1.075 | $188-198k | $26-28 | $188,146 |
| 5 | 1m · SM 200 | $330,862 | 8,550 | 1.085 | $249,380 | $29.17 | $215,767 |
| 6 | 1m · SM 220 | $285,925 | 7,461 | 1.077 | $214,822 | $28.79 | $173,429 |
| ref | 1m · SM 179 (frozen canonical) | $259,102 | 10,183 | 1.060 | $161,567 (REAL) | $15.76 | — |
| — | 2m · 90/179 | $165,914 | 8,654 | 1.043 | $83,442 | $9.64 | — |
| — | 5m · 90/179 | $94,825 | 6,632 | 1.027 | $31,622 | $4.77 | — |

Dead/mapped-out: SM≤160 on 1m (negative after costs), 5m at 90/179 (DD −$142k), unconditional Type 2/0/3 cores (cost-fragile), flip-count chop veto (inverted).

Exit-architecture option (SW02a): ~16:31 timed exit ≥ session close (102.4% net, lower DD on canonical) — to be applied to top candidates in Wave 1c.

Structural facts that shrink the search space: Type-1 core = f(StopMultiplier, timeframe, exit) ONLY (TrendMultiplier/SlowdownScan/WeakWeakSplit/StageB all proven inert, bit-identical). Full-history canonical is positive every calendar year 2022–2026 (real slip-1: 11.4k/34.1k/68.3k/42.6k/4.0k) but 2026 is near-breakeven — per-year stability of the 3m plateau is the key Wave-1c question.
