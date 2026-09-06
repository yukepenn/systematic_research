# ZBMACRO01 engine dossier -- G3_ZBMACRO_ENGINE_20260906 (ledger G00079)

**EVIDENCE STATUS: DISCOVERY_CONSUMED (every table).** Program-written by `src/run_engine.py`; the
gate table and full log are `out/gate_table.txt` / `out/run_log.txt`.

## 0. The engine object (FT0-freeze candidate)

- **Rule (frozen, G00072, zero retuning):** on GENESIS_H2_CALENDAR NFP_DAY/CPI_DAY sessions,
  if close(08:45) - close(08:30) < 0 (ZB points), SHORT k ZB, exit at close(15:00). No
  overnight, no other conditioning.
- **Entry convention (THE EXECUTABLE CLAIM): fill at the close of the 08:46 bar** -- the
  signal is known at the 08:45 close; one full minute of latency is charged before the fill.
- **Size: k=2** (G00078 Class-P decision cell; k=1 also dossiered throughout).
- **Cost (BASIS=MODELED ALL_IN):** PRIMARY $66.86/RT (comm $4.36 + 1 tk/side); STRESS $129.36/RT.

## 1. THE DECISIVE QUESTION -- the delay curve (G_delay)

Same 40 events, same signal, same exit; only the entry close is delayed. Paired moving-block
bootstrap (L=5, B=2000, seed 20260910; one shared draw across arms).

| entry | n | gross move pt | net $/ct | CI95 profit $/ct | STRESS $/ct | retention |
|---|---|---|---|---|---|---|
| 08:45 | 40 | -0.2445 | +177.7 | [+48.0, +428.5] | +115.2 | 1.000 |
| 08:46 | 40 | -0.2531 | +186.3 | [+44.8, +432.4] | +123.8 | 1.048 |
| 08:47 | 40 | -0.2703 | +203.5 | [+59.7, +450.4] | +141.0 | 1.145 |
| 08:48 | 40 | -0.2695 | +202.7 | [+64.4, +444.1] | +140.2 | 1.141 |
| 08:50 | 40 | -0.2641 | +197.2 | [+55.0, +435.5] | +134.7 | 1.110 |

- **G_delay verdict: PASS** -- 08:46 net +186.3 $/ct, CI
  [+44.8, +432.4], retention 1.048 of the 08:45 edge;
  curve monotone non-increasing: False.
- The G00072 neighborhood's 08:50 cell ($17.7/ct) conditioned on r(08:50); THIS curve holds
  the signal fixed at r1(08:45) and delays only the fill -- the executable question.

## 2. Per-minute drift 08:45 -> 09:15 (event days, cumulative from the 08:45 close)

| minute | n | cum move pt | cum short $ | incr pt |
|---|---|---|---|---|
| 08:45 | 40 | +0.0000 | -0.0 | +0.0000 |
| 08:46 | 40 | +0.0086 | -8.6 | +0.0086 |
| 08:47 | 40 | +0.0258 | -25.8 | +0.0172 |
| 08:48 | 40 | +0.0250 | -25.0 | -0.0008 |
| 08:49 | 40 | +0.0086 | -8.6 | -0.0164 |
| 08:50 | 40 | +0.0195 | -19.5 | +0.0109 |
| 08:51 | 40 | +0.0172 | -17.2 | -0.0023 |
| 08:52 | 40 | +0.0078 | -7.8 | -0.0094 |
| 08:53 | 40 | +0.0016 | -1.6 | -0.0063 |
| 08:54 | 40 | +0.0063 | -6.2 | +0.0047 |
| 08:55 | 40 | -0.0156 | +15.6 | -0.0219 |
| 08:56 | 40 | -0.0078 | +7.8 | +0.0078 |
| 08:57 | 40 | -0.0156 | +15.6 | -0.0078 |
| 08:58 | 40 | -0.0250 | +25.0 | -0.0094 |
| 08:59 | 40 | -0.0195 | +19.5 | +0.0055 |
| 09:00 | 40 | -0.0250 | +25.0 | -0.0055 |
| 09:01 | 40 | -0.0352 | +35.2 | -0.0102 |
| 09:02 | 40 | -0.0211 | +21.1 | +0.0141 |
| 09:03 | 40 | -0.0242 | +24.2 | -0.0031 |
| 09:04 | 40 | -0.0383 | +38.3 | -0.0141 |
| 09:05 | 40 | -0.0359 | +35.9 | +0.0023 |
| 09:06 | 40 | -0.0359 | +35.9 | +0.0000 |
| 09:07 | 40 | -0.0414 | +41.4 | -0.0055 |
| 09:08 | 40 | -0.0484 | +48.4 | -0.0070 |
| 09:09 | 40 | -0.0516 | +51.6 | -0.0031 |
| 09:10 | 40 | -0.0477 | +47.7 | +0.0039 |
| 09:11 | 40 | -0.0539 | +53.9 | -0.0063 |
| 09:12 | 40 | -0.0523 | +52.3 | +0.0016 |
| 09:13 | 40 | -0.0437 | +43.8 | +0.0086 |
| 09:14 | 40 | -0.0602 | +60.2 | -0.0164 |
| 09:15 | 40 | -0.0617 | +61.7 | -0.0016 |

Share of the eventual (15:00) mean move already realized: by 08:50 **-8.0%**,
by 09:15 **25.2%** (gross, pts). Checkpoints: 09:30
+41 $, 10:30
+54 $, 12:00
+147 $, 14:00
+241 $, 15:00
+245 $ (per ct, gross).

## 3. eval_battery (weekly-vol LEAD; LEAD arm = executable 08:46 entry)

| arm | Sharpe_wk | $/wk mean (sd) | $/yr k=1 | $/yr k=2 | wk maxDD k=1 | wk CDaR95 k=1 |
|---|---|---|---|---|---|---|
| **08:46 executable (LEAD)** | **0.91** | 39.6 (313.7) | 2,074 | 4,148 | 1,674 | 1,333 |
| 08:45 research reference | 0.86 | 37.8 (318.8) | 1,978 | 3,957 | 1,799 | 1,510 |

maxDD/CDaR are **dollar path descriptors only** -- no income is normalized by them, no trade
is removed by any rule in this run, so **the thinning placebo is N/A (stated)**. Sharpe is
k-invariant; dollars and dollar tails scale linearly in k.

## 4. MAE/MFE (1-min as-of path) and worst-5 anatomy

- Entry 08:46: MAE mean 0.417 / med 0.375 /
  p90 0.797 / max 1.531 pt
  ($417 mean, $1531 max per ct);
  MFE mean 0.641 / max 2.188 pt.
- Winners' MAE mean 0.213 pt vs losers'
  0.693 pt -- per-trade table in `out/maemfe.csv`.

Worst 5 by net $ at the executable entry:

| date | rel | r1 pt | net46 $ | net45 $ | MAE pt @ t | MFE pt @ t | pnl@09:15 $ |
|---|---|---|---|---|---|---|---|
| 2023-01-12 | CPI | -0.656 | -1160.6 | -1504.4 | 1.250 @ 13:14 | 1.031 @ 09:55 | +62.5 |
| 2023-10-06 | NFP | -1.219 | -879.4 | -816.9 | 1.281 @ 11:50 | 0.688 @ 08:57 | +281.2 |
| 2025-12-16 | NFP | -0.469 | -723.1 | -785.6 | 0.688 @ 14:47 | 0.156 @ 09:19 | +62.5 |
| 2024-01-11 | CPI | -0.812 | -629.4 | -816.9 | 0.625 @ 14:56 | 0.625 @ 09:00 | +375.0 |
| 2024-08-14 | CPI | -0.188 | -598.1 | -535.6 | 0.719 @ 12:45 | 0.125 @ 08:52 | -0.0 |

## 5. Calendar honesty

- NFP+CPI same-session overlaps among the 40: **0**.
- Weekdays: Friday 21  Thursday 7  Tuesday 6  Wednesday 6. NFP not on Friday:
  **3** (2025-07-03, 2025-12-16, 2026-02-11).
- Roll windows (**ASSUMED-PROXY** -- the merged chain carries only the rolled contract's
  volume, so the true volume crossover is NOT measurable here; proxy = last session of
  Feb/May/Aug/Nov): event days within +-3 sessions: **2**
  -> 2023-06-02 (d=2), 2023-09-01 (d=1).

## 6. Session, margin, capacity

- Entry 08:45-08:46 ET, flat at the 15:00 close: intraday only, **no overnight margin**.
- ZB day margin **ASSUMED ~$2,000/ct (FLAGGED, not broker-verified; no broker surface
  touched)**; k=2 ~ $4,000 for ~6h14m on ~11 days/yr.
- Capacity: ZB top-of-book depth is deep; k=2 is negligible. **Stated, not proven.**

## 7. Orthogonality at k=2 (G00078 joint series AS-IS, 178-week grid)

rho(ZB k=2, P1): daily -0.0058, weekly +0.1004 (identical to k=1 -- correlation is
scale-invariant in k). k=2 LIVE_SCALE marginal weekly-vol Sharpe +0.0923
(reproduces G00078's +0.0923: OK).

## 8. Verdict carried to the gate table

G_delay = **PASS**; skeptic = **SURVIVES** ->
**ZBMACRO01 ENGINE FROZEN-READY (FT0 licensed: rule + entry close(08:46) + k=2)** (ledger PASS).
