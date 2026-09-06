# G3_EVENT_GC_20260906 — GC 6-event DAILY catalog with drift-matched controls

**Ledger:** G00069, family GENESIS3_EVENT · **Stage:** DIAGNOSTIC / DISCOVERY (daily-only) ·
**Executed:** 2026-09-06 · **Result: NULL — all six events DEAD. 0/33 cells survive the
K_eff-corrected drift-matched screen; no LEAD, no DESCRIPTIVE.**

## 1. Question and the rule that governed it

Does GC carry daily-resolution event structure — liquidation signatures, flight-to-quality,
vol transitions, multisession extremes, cross-metal divergence, gap days — beyond its secular
drift? The G00060 lesson made a **drift-matched control MANDATORY on every cell**: gold drifts
+3.03 bps/day (~+7.6%/yr) over 2009-03→2026-07, and any long-side conditional mean will look
like an edge unless compared to random entries with identical holding period on the same series.

## 2. Data (all seal-asserted < 2026-08-01)

| series | source | rows / span | basis |
|---|---|---|---|
| GC daily | `runs/DAILY_GC_EXTRACT_AUTOPSY_20260906/out/gc_daily.parquet` | 4,347 d, 2009-03-31→2026-07-31 | ratio-stitched `ret_pct` (%-safe, identity gate 0.0); raw held-contract OHLC for ranges; `close_radj` for local level comparisons |
| NQ daily | **deep spine** `research/scalping_lab/substrate/minute/NQ/nq1m_2005_202605.parquet` aggregated to sessions (18:00→17:00 ET, END-stamped) | 5,262 sess, 2006-01-05→2026-05-29 | **additively back-adjusted → POINT differences only (DELEV01)**; z = ret_pts / trailing-60 sd(ret_pts) |
| SI daily | **built this run** into `out/si_daily.parquet` from the per-contract NT8 day `.ncd` store via `research/multi_market/src/ncd_day.py::read_ncd_day` + the certified causal roll (`roll.py`) — method identical to the GC autopsy | 4,361 d, 2009-03-31→2026-07-31, 89 contracts (69 vol-crossover / 19 pre-expiry / 1 init rolls) | self-financing points / `old_close_prev` → %-safe `ret_pct`; identity gate vs `roll.economic_returns` err 0.0; causality PASS |

**NQ source documented (per task):** the deep spine was chosen over `runs/SM1M_SUBSTRATE`
(2022+ only — would cut the E2 sample ~4×) and over any weekly_edge series. An **alignment gate**
was added because a session-dating phase error here would be silent: spine session point-returns
vs day-store causal-roll NQ returns correlate **+0.962 at lag 0** vs −0.030/−0.045 at ±1 BDay —
no phase error (the W52 failure class). Spine coverage is complete (253–259 sessions/yr every
year); it ends 2026-05-29, so E2 cannot fire on the last ~42 GC days (documented, immaterial).
**E5 was RUNNABLE** — SI daily built, so the conditional clause resolved to run, not fake.

## 3. Method (as preregistered)

- **Outcomes.** DIR cell at horizon h = sum of next-h daily `ret_pct` (entry close of event day
  t). E6 day0 = event-day `intraday_pct` (gap known at the open; entry open→close). E5 = forward
  GC sum minus forward SI sum on the shared-date axis (equal-notional spread).
- **Drift-matched control (MANDATORY, every cell):** circular shift of the event mask — random
  entry times with identical count, holding period, and within-event clustering on the same
  series, so the control carries the full drift. 2000 draws, **one shared uniform draw per
  iteration across the whole 33-cell family** (dependence-preserving). Unconditional time-matched
  mean also printed per cell (`controls.csv`).
- **Second, independent p:** block bootstrap on days (block 5, wraparound), 2000 draws.
- **Multiplicity:** K_eff = K/(1+(K−1)ρ̄) from the shared-draw null matrix: K=33, ρ̄=0.073,
  **K_eff=9.9, alpha_eff=0.00507**.
- **LEAD screen (spec):** shift-p < 0.05/K_eff AND |excess $/ct| ≥ 2× conservative cost
  (GC $24.36 = $4.36 + 2×$10 tick; pair $78.72 incl. SI tick $25) AND n ≥ 30. PATH cells
  LEAD-ineligible by prereg (futures cannot monetize a vol path directly).
- **Verdict:** LEAD / DESCRIPTIVE (K_eff-significant but untradable) / DEAD.
- Implementation freezes (fixed before results): trailing sigmas and reference windows exclude
  the current day; E3 events are first-crossing days (pctl>0.5 at t, ≤0.5 at t−1, min pctl over
  t−3..t−1 ≤ 0.2); E4 breach on `close_radj` vs trailing-20 prior closes; RNG seed 20260906.

## 4. Results — per-cell (obs vs drift-matched control; excess = obs − ctrl; bps)

```
cell          n   obs(bps) ctrl(bps)   excess   exc$/ct  p_shift  p_bboot  sigK  mat  LEAD
E1_h1       228      11.12      3.13     7.99    133.26   0.2569   0.2119     .    Y     .
E1_h2       228      16.37      5.85    10.52    175.41   0.2869   0.3838     .    Y     .
E1_h3       226      23.89      8.76    15.13    252.24   0.2019   0.3768     .    Y     .
E1_h5       226      42.03     13.80    28.22    470.63   0.0880   0.2949     .    Y     .
E2_h1       105      13.18      2.90    10.27    182.97   0.3078   0.3148     .    Y     .
E2_h2       104      26.20      6.07    20.13    358.45   0.1679   0.2749     .    Y     .
E2_h5       102      13.09     14.06    -0.97    -17.23   0.9395   0.9685     .    .     .
E3dir_h1    126      14.48      2.96    11.52    209.31   0.2089   0.2029     .    Y     .
E3dir_h2    124      12.92      5.75     7.17    130.34   0.5897   0.6557     .    Y     .
E3dir_h3    123       2.52      8.47    -5.95   -108.12   0.7066   0.8076     .    Y     .
E3dir_h4    123       9.90     10.98    -1.09    -19.73   0.9585   0.9755     .    .     .
E3dir_h5    122      16.54     13.45     3.08     56.04   0.8796   0.9335     .    Y     .
E3path_h1   126      58.75     74.51   -15.76   -286.24   0.0180   0.0400     .    .     .
E3path_h2   124      66.88     74.48    -7.59   -137.95   0.1199   0.3458     .    .     .
E3path_h3   123      63.82     74.44   -10.62   -193.01   0.0130   0.1609     .    .     .
E3path_h4   123      66.72     74.45    -7.73   -140.40   0.0400   0.3128     .    .     .
E3path_h5   122      66.24     74.45    -8.21   -149.15   0.0150   0.2519     .    .     .
E4H_h1      641       3.14      2.89     0.25      4.53   0.9605   0.9945     .    .     .
E4H_h2      637       5.69      5.73    -0.03     -0.61   0.9935   0.9695     .    .     .
E4H_h3      633      11.18      8.28     2.89     53.22   0.7466   0.8246     .    Y     .
E4H_h5      628      16.82     13.38     3.44     63.33   0.7936   0.8476     .    Y     .
E4L_h1      403       4.83      3.03     1.80     29.37   0.7176   0.7356     .    .     .
E4L_h2      402       4.86      6.00    -1.14    -18.54   0.8966   0.8936     .    .     .
E4L_h3      402       8.23      8.76    -0.52     -8.56   0.9415   0.9715     .    .     .
E4L_h5      401      29.20     14.03    15.17    247.56   0.3368   0.4908     .    Y     .
E5P_h5      124      10.58     -9.73    20.31    356.01   0.5777   0.6577     .    Y     .
E5P_h10     120      56.75    -18.75    75.49   1323.19   0.2449   0.3368     .    Y     .
E5M_h5      119      17.04     -9.73    26.77    506.07   0.5327   0.5587     .    Y     .
E5M_h10     118     -53.13    -17.81   -35.32   -667.65   0.6387   0.6797     .    Y     .
E6U_d0      153       2.91      0.65     2.26     35.34   0.7426   0.7336     .    .     .
E6U_d1      154      -4.79      2.96    -7.74   -120.93   0.3298   0.3678     .    Y     .
E6D_d0      139     -12.49      0.94   -13.44   -200.46   0.0680   0.0890     .    Y     .
E6D_d1      140      -7.96      3.18   -11.13   -166.07   0.2229   0.2259     .    Y     .
```

## 5. Verdicts and reading

| event | verdict | honest reading |
|---|---|---|
| E1 liquidation signature (n=228) | **DEAD** | The naive read — "buy the washout" — shows +42 bps raw 5d mean, but a third of it is drift (ctrl +13.8) and the +28 bps excess is p=0.088 uncorrected, 0.29 by block bootstrap. Consistent with G00060: liquidation-day rebounds are mostly gold drift plus noise. |
| E2 flight-to-quality (n=105) | **DEAD** | The FTQ narrative (GC up ≥1σ while NQ down ≥1σ → continuation) does not survive: excess fades to −1 bps by 5d; nothing approaches significance. |
| E3 vol transition (n=126) | **DEAD** | Direction: nothing. The only structure anywhere in the run is the PATH side — forward |ret| runs ~8–16 bps/day BELOW the drift-matched control (p 0.013–0.04 uncorrected at h1/3/5) — i.e., low→above-median vol crossings do NOT launch vol expansions; vol-regime persistence pulls path back down. LEAD-ineligible by prereg, dies at alpha_eff=0.00507, and the block bootstrap disagrees (0.16–0.31). Recorded as a hint, claimed as nothing. |
| E4 multisession extreme (n=641 H / 403 L) | **DEAD** | Both sides reported: fresh 20d-close highs earn the drift and nothing more (excess ≤3.4 bps); fresh lows show +15 bps 5d excess at p=0.34. The largest-n, best-powered event in the catalog is flat. |
| E5 cross-metal divergence (n=124/119) | **DEAD** | RUNNABLE (SI built). The convergence hypothesis is not just null — the signs point the other way in both tails (+z → spread +75 bps over 10d, −z → −35 bps): GC−SI divergence tends to CONTINUE. p ≥ 0.24 everywhere; no claim either direction. |
| E6 gap day (n=153 up / 139 dn) | **DEAD** | Down-gaps show same-day continuation (−13.4 bps excess, p=0.068) and next-day drift-underperformance in both gap signs — all inside the null. |

**Decision rule:** PASS iff ≥1 LEAD survives; all DEAD → **NULL**. The diagnostic itself is
valid (all 17 gates PASS), so not FAIL.

## 6. Gates

All 17 program-printed gates PASS (see `out/gate_table.txt`): seals on GC/NQ/SI; DELEV01 point-space
discipline on the spine; SI identity gate 0.0 and roll causality; NQ session alignment (lag-0
dominance); drift-matched control on 33/33 cells; shared null draws; both directions reported for
E4/E5/E6; prereg constants echoed; K_eff correction, min-n, and materiality applied; every p
computed two independent ways (2 clustering-driven disagreements on LEAD-ineligible path cells,
documented); and the p-value's event stated in words with a second computation (per the CAP01
mislabelled-statistic rule).

## 7. What this closes and what it does not

- **Closes (daily resolution, $0 data):** the GC event-conditional frontier at daily bars. With
  the washout z-MR (G00060, drift-explained), the vol-managed sleeve (G00064, neutral), and now
  all six event families dead against drift-matched controls, GC's daily surface offers **drift,
  a fat left tail, and ρ≈0.07 to NQ — and no conditional timing information found by this catalog**.
  Any GC allocation case rests on the unconditional drift/diversification math, not on events.
- **Does not close:** intraday GC structure (no local GC 1-min — honesty rule; MGC is thin),
  event definitions outside this preregistered catalog, and lower-frequency (weekly+) state
  conditioning. Sub-threshold hints (E3 path suppression, E6 down-gap continuation, E5
  anti-convergence) are recorded for meta-analysis only; none may be quoted as findings.

## 8. Artifacts

`runs/G3_EVENT_GC_20260906/`: `src/build_daily_inputs.py`, `src/event_study.py`;
`out/event_tables.csv` (33 cells), `out/controls.csv`, `out/gate_table.txt` (full program print),
`out/verdicts.json`, `out/si_daily.parquet` (+ build log, `inputs_manifest.json` with SHA256s),
`out/nq_daily_spine.parquet`. Deterministic: seed 20260906; rerun reproduced identical verdicts.

**Evidence status:** DISCOVERY (GC/SI/NQ daily ≤2026-07-31 now DISCOVERY_CONSUMED for this
event catalog). No P&L object, no promotion, no forward claim.