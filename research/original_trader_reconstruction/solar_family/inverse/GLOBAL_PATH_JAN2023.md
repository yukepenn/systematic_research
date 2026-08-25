# GLOBAL_PATH_JAN2023 — the trader's first 11 trading days, recovered exactly

Run `runs/OTR_R11_INVERSE/` (amendment_4 preregistered before this readout).
Artefact: `out/r22_global_path_11days.json` (89 trades). Log: `out/r22_log.txt`.
Directive v4.0 sections 7–10.

## Result

A **single continuous 89-trade path** reproduces **all eleven visible rows** of the trader's
NT8 Daily Analysis table (OTRIMG-0003) — trade count, winner count, loser count, gross
profit, gross loss, largest winner, largest loser, **sum MAE** and **sum MFE**, every cell,
to the cent and to the tick.

89 is exactly the sum of the eleven reported trade counts. The path's cumulative net,
**$8,032.98**, equals the report's final `cum_net` cell — a value never used as a constraint.

| day | n | net | all 8 cells exact |
|---|---|---|---|
| 2023-01-03 | 12 | −300.16 | YES |
| 2023-01-04 | 14 | −1,148.52 | YES |
| 2023-01-05 | 6 | −30.08 | YES |
| 2023-01-06 | 10 | 2,993.20 | YES |
| 2023-01-09 | 3 | 5,262.46 | YES |
| 2023-01-10 | 9 | 1,192.38 | YES |
| 2023-01-11 | 4 | 1,768.28 | YES |
| 2023-01-12 | 16 | −3,321.88 | YES |
| 2023-01-13 | 6 | 1,424.92 | YES |
| 2023-01-16 | 3 | 607.46 | YES |
| 2023-01-17 | 6 | −415.08 | YES |

Fingerprint of the recovered path: 44 long / 45 short, **WR 42.70 %**, **PF 1.2392**,
mean hold 110.8 min, median hold 57 min.

## The three model choices this pins, each by elimination

| choice | rivals tested | result |
|---|---|---|
| **entry universe = T1 only** | T1, T1+T2E, T1+T2L, T1+T3, T1+T2E+T3, T1+T2L+T3 | every solvable day everywhere solves with `min_extra = 0`; T2/T3 entries never used |
| **exit test = STRICT** (`close < TS`) | STRICT vs INCLUSIVE | INCLUSIVE yields **0** global paths; STRICT yields 2 |
| **daily row = CALENDAR exit date** | calendar vs trading-session date | session-date yields **0** global paths (and only 8/11 even day-by-day) |

Each was decided by feasibility, never by profit.

### The two trades that decide the day-assignment rule

The readings differ only for a trade that both enters and exits inside the 18:00–23:59
evening block. The recovered path contains exactly such trades, and they are the reason the
session reading fails:

- `S 2023-01-04 21:07 → 2023-01-04 23:36` — calendar row **01-04**, session row 01-05.
- `L 2023-01-12 19:17 → 2023-01-12 20:36` — calendar row **01-12**, session row 01-13.
- `L 2023-01-17 21:42 → 2023-01-17 22:39` — calendar row **01-17**; without it the 01-17
  row is short by exactly one trade, which is why that day was unexplainable until the
  reporting window was extended past 17:00.

An earlier note recorded the day rule as NOT SEPARABLE because zero trades in the R6
certification window exited in that block. That was true of the *inclusive-exit* run and
false of the correct model — a good reminder that "not separable" is a statement about the
model you happen to be holding.

## What the machine actually is

Of the 89 trades:

- **72 are stop-and-reverse** — the position flips directly at a trend flip,
- **10 are session-close exits**,
- **7 are declined reversals** — the only moments in eleven days when the strategy chose to
  go flat instead of flipping.

So the early flagship is a **pure always-in stop-and-reverse machine on Solar T1 flips**,
flat only at session boundaries and at seven discretionary suppressions. There is no
pullback entry layer, no strengthening entry layer, and no fixed stop.

The seven flat gaps — the entire suppression behaviour of the era — are:

| exit | next entry | bars flat |
|---|---|---|
| 01-03 12:37 | 01-03 12:48 | 11 |
| 01-03 13:28 | 01-03 16:04 | 156 |
| 01-04 13:25 | 01-04 14:49 | 84 |
| 01-04 23:36 | 01-05 02:52 | 196 |
| 01-05 12:21 | 01-05 19:33 | 372 |
| 01-12 13:29 | 01-12 14:54 | 85 |
| 01-17 22:39 | (window ends) | — |

That is the complete identification target for the risk/gate layer, and it is far smaller
than the six-parameter D-gate that was previously fitted to it.

## Status, stated precisely

- **REPRODUCED**: the 89-trade path reproduces every visible cell of OTRIMG-0003.
- **INFERENCE**: that this path *is* the trader's trade list. It is the unique path
  consistent with his report **under the stated model class** (Solar A1-A5 = 90/179/5/10/10,
  T1-only entries, strict flip exits, NT8 S0 conventions, $4.18/RT). Two global solutions
  were returned, not one, so even within the class it is not strictly unique — the residual
  ambiguity is recorded, not hidden.
- **NOT ESTABLISHED**: ORIGINAL_PARITY. This is an 11-day window out of a 2023-01→2025-02
  backtest. It is the strongest reconstruction artefact the campaign has produced and it is
  still a sample.

## Why this was reachable only now

Three things had to be corrected together, and none of them alone is sufficient:

1. Using **avg_MAE / avg_MFE** at all — path statistics that no P&L-matching subset can fake.
2. The **$5-tick lattice**, which turns two rounded cells per day into exact integers and
   recovers every cropped cell uniquely.
3. Solving the days **jointly rather than independently** — a free trade for one day is a
   constrained trade for its neighbour, and the joint problem has ~99 constraints where the
   eleven separate problems have nine each.

Solved independently, the calendar reading gave 11/11 feasible but with 1–4 paths per day;
solved jointly it gives one path for the whole window. Independence was hiding the answer.
