# G3_CLOCKLAG01_20260831 — REPORT

> **STAGE 1 VERDICT, IN ONE SENTENCE: the identifying restriction cannot be tested because the
> predictability it would arbitrate does not exist — in MODERN the same clock bucket one day back
> carries `beta_same = +0.0063` (t = +0.48) against an adjacent-bucket control of `+0.0022`
> (t = +0.12), a margin of `+0.0041` that had to clear `+0.1151` to survive its own
> max-over-buckets circular-shift null and fell 28x short (p = 0.9985) — so the HKS-style
> cross-day clock-bucket scheduling mechanism DOES NOT TRANSFER TO NQ, Stage 2 never ran, no
> dollar figure was produced, and no candidate exists.**

| | |
|---|---|
| Run class | GENESIS III — NQ CHAMPION CHALLENGE / WAVE C |
| Spec | `runs/G3_CLOCKLAG01_20260831/spec.yaml`, committed at `dc68700` **before any statistic existed**; never edited |
| Evidence status | **PRE-FROZEN** falsifier. Data window includes the BURNED sub-window 2026-05-31 -> 2026-07-31. **No VIRGIN data (>= 2026-08-01) was read — 0 sessions.** |
| Stage 1 | **FAIL** (S1-C) -> family closed |
| Stage 2 | **NOT RUN.** No position formed, no P&L computed, no dollar figure produced |
| Improvement classification | none — this run produces a NULL, not an improvement |
| live_enabled | **NO** · orders placed: **NO** · deploys: **NO** · backtests: **NO** · spend: **$0** |

Deliverables: `src/panel.py`, `src/estim.py`, `src/stage2.py`, `src/run_clocklag01.py`,
`out/console.txt`, `out/gates.json`, `out/stage1_table.csv`.

---

## 1. What the run was for

The mechanism, stated so it could be wrong: institutional execution schedules — VWAP/TWAP slice
boundaries, model-portfolio and target-vol resets, index-fund cash flows — repeat at the **same
clock window** on consecutive days. *The scheduling repeats, not the information.* Price pressure
should therefore recur at lags that are exact multiples of one trading day and be absent at
non-daily lags.

That story has a falsifiable edge that generic momentum does not:

| | prediction |
|---|---|
| generic momentum | a recent return predicts the next one **regardless of clock alignment** |
| scheduling mechanism | the **same clock bucket one day ago** beats the **adjacent bucket minutes ago** |

Stage 1 computes no P&L and forms no position. Its entire job was to arbitrate that, cheaply, and
kill the whole family if the adjacent-bucket control wins. **The falsifier was coded and its firing
was demonstrated on synthetic data before it was pointed at NQ**: `estim.py`'s self-test plants a
cross-day effect (gate margin `+0.2201`, beats its own max null) and separately plants pure
within-day momentum (gate margin `-0.2423`, fails its own max null). 22/22 estimator self-tests,
14/14 panel self-tests, 30/30 `research_sdk/champion_eval.py` self-tests, all printed by the
program before any real number.

## 2. Data and definitions — every one frozen by the spec, none varied

NQ 1-minute via `research/weekly_edge/src/run_we_w17.py::load_deep(a, b, extend=True)` (imported,
not modified). 6,528,330 bars, 5,466 sessions, 2006-01-05 -> **2026-07-31 16:59**.

- **SEAL OK: 0 sessions >= 2026-08-01 were read.** Max session date 2026-07-31.
- Bars are END-STAMPED, so bucket 0 is the bars stamped **09:31..10:00** and bucket 12 is
  **15:31..16:00**; `r(0,d)` uses the OPEN of the bar stamped 09:31 as its base. There is no
  +/-1-minute shift.
- 13 x 30-minute buckets. **No other width was tried, in accordance with spec prohibition 5.**

Panel construction, all drops printed:

| | sessions |
|---|---|
| RTH calendar dates seen | 5,287 |
| dropped — no bar stamped 09:31 | 17 |
| dropped — >= 1 empty 30-minute bucket (half-days, holidays) | 179 |
| dropped — a >60-min intraday data hole split the session (`2006-11-21`, `2026-07-17`) | 2 |
| **KEPT (all 13 buckets non-empty, nothing interpolated)** | **5,091** |

PRE 4,036 sessions (2006-01-05 -> 2022-04-29) · MODERN 1,055 (2022-05-02 -> 2026-07-31).
Era stratification is mandatory under ERABREAK01 (p = 0.0011); **FULL is a diagnostic only** and a
result that existed only in PRE would be an old-regime finding, not a candidate.

## 3. `rho_bar` and `K_eff` — what a bucket count is worth here

| era | `rho_bar` (mean pairwise correlation of the 13 bucket series) | `K_eff = 13/(1+12*rho_bar)` |
|---|---|---|
| PRE | 0.00544 | 12.204 |
| **MODERN** | **0.00960** | **11.657** |
| FULL | 0.00809 | 11.850 |

The 13 bucket return series are very nearly uncorrelated within a day, so the effective bucket count
is 11.7 rather than a much smaller number — the multiplicity penalty is close to its full size, not
discounted away. `K_eff` sets the per-bucket significance stars in the console table
(|t| > 2.86 in MODERN); the max-statistic null below is the primary control.

## 4. The Stage 1 table — means over buckets, WITH and WITHOUT buckets 0 and 12

All 13 x 3 x 3 individual cells are in `out/stage1_table.csv` and printed in `out/console.txt` §3
with session-clustered t-statistics. The aggregates:

**`beta_adj(0)` is undefined** — bucket -1 does not exist — so the only bucket set on which the two
estimators can be compared head-to-head is **b = 1..12**, and that was frozen in code as the gate
set before the run. All three sets are reported.

| era | set | mean `beta_same` (t) | mean `beta_adj` (t) | **margin** (t) | mean `beta_nonmult` (t) |
|---|---|---|---|---|---|
| PRE | ALL_13 | -0.01573 (-1.67) | +0.01261 (+1.20) | -0.02323 (-1.40) | -0.01113 (-4.05) |
| PRE | **MATCHED_1_12** | -0.01063 (-0.98) | +0.01261 (+1.20) | **-0.02323 (-1.40)** | -0.00999 (-3.40) |
| PRE | INTERIOR_1_11 | +0.00394 (+0.43) | +0.00229 (+0.26) | +0.00165 (+0.13) | -0.00841 (-3.04) |
| **MODERN** | ALL_13 | +0.00479 (+0.39) | +0.00223 (+0.12) | +0.00406 (+0.17) | -0.00986 (-1.51) |
| **MODERN** | **MATCHED_1_12 <- GATE** | **+0.00629 (+0.48)** | **+0.00223 (+0.12)** | **+0.00406 (+0.17)** | **-0.00992 (-1.67)** |
| **MODERN** | INTERIOR_1_11 | +0.00529 (+0.38) | -0.00308 (-0.16) | +0.00837 (+0.33) | -0.01284 (-2.06) |
| FULL | ALL_13 | -0.00965 (-1.21) | +0.01092 (+1.00) | -0.01747 (-1.10) | -0.01052 (-3.35) |
| FULL | **MATCHED_1_12** | -0.00654 (-0.74) | +0.01092 (+1.00) | **-0.01747 (-1.10)** | -0.00988 (-3.27) |
| FULL | INTERIOR_1_11 | +0.00348 (+0.44) | +0.00237 (+0.22) | +0.00111 (+0.08) | -0.01023 (-3.30) |

**Is the whole effect two buckets?** (spec trap 4, mandatory reporting.) In PRE, yes — and it runs
*against* the mechanism. Buckets 0 (09:30-10:00, `beta_same = -0.0769`, t = -2.20) and 12
(15:30-16:00, `beta_same = -0.1709`, t = -2.44) are the only large |beta| in the entire PRE column,
and dropping them moves mean `beta_same` from **-0.01573 to +0.00394** and the margin from
**-0.02323 to +0.00165**. Those two buckets are open- and close-auction microstructure — a
*reversal* at the same clock bucket one day later — not a scheduling trace. **They were not
excluded from any gate**: excluding them after seeing the table would be a selection, the gate set
was frozen before the run, and this paragraph exists only so a reader can see the decomposition.
In MODERN the with/without difference is immaterial (+0.00479 vs +0.00529) because nothing in
MODERN is large enough for it to matter.

## 5. The null — where MC-11 died, and what it cost this candidate

2,000 draws, seed 20260831, 5-day buffer. One circular shift `k` of the **day index** per draw,
applied to the **predictor matrix only**. A whole day-row moves together, so each bucket's own
marginal distribution **and** the within-day cross-bucket dependence are preserved exactly. **On
every draw the entire analysis is redone — all 13 buckets, all three estimators, every mean and
every max-over-buckets step — and the maxima are recorded.** Reporting a best bucket without this
would be MC-11 exactly.

Two nulls were computed; **NULL_A is the gate** (the shifted matrix supplies both the lag-1 and the
same-day predictors, so no estimator keeps its true day alignment). NULL_B is a stricter diagnostic
in which only the cross-day predictor is shifted, so the margin is measured against the *real*
adjacent-bucket benchmark. Both are printed; the gate does not move between them.

MODERN, gate set b = 1..12:

| statistic | observed | null p50 | null p95 | percentile | p |
|---|---|---|---|---|---|
| mean `beta_same` | 0.00629 | -0.00030 | 0.01308 | 81.3% | 0.1869 |
| margin (same - adj) vs the null's **mean** margin | 0.00406 | -0.00093 | 0.01786 | 65.6% | 0.3438 |
| **margin vs the null's MAX-over-buckets margin <- GATE** | **0.00406** | 0.06754 | **0.11513** | **0.1%** | **0.9985** |
| margin vs the null's max margin against the REAL adj (NULL_B) | 0.00406 | 0.08775 | 0.13461 | 0.0% | 1.0000 |

The observed margin sits at the **66th percentile** of the null's own mean-margin distribution — a
completely ordinary draw — and at the **0.1st percentile** of the multiplicity-priced max
distribution.

**The best-bucket temptation, and why it is not a finding.** The largest single `beta_same` in
MODERN is bucket 8 (13:30-14:00) at `+0.1006`, which does clear the max null (p = 0.0040). Three
things kill it:

1. **At that very bucket the adjacent-bucket control is larger**: `beta_adj(8) = +0.1704` against
   `beta_same(8) = +0.1006`. The mechanism's own identifying restriction is violated exactly where
   the mechanism looks strongest.
2. **The max-only family is one-sided and understates the multiplicity.** Priced two-sided, the
   largest |`beta_same`| in MODERN is the *negative* one at bucket 11 (15:00-15:30, `-0.1128`),
   which is anti-mechanism — the mechanism predicts pressure *repeats*, i.e. positive.
3. **The max is elevated in the CONTROL-B family too.** `MAX_b |beta_nonmult| = 0.0330` at
   p = 0.0230 — but control B is a **non-daily-multiple** lag that the mechanism *requires* to be
   ~ 0 everywhere. An extreme max shared by treatment and control is a panel-wide feature (a few
   influential sessions, day-to-day variance clustering that the shift null deliberately destroys),
   not evidence for clock alignment.

**Head-to-head, the cleanest single reading of the restriction:** `beta_same > beta_adj` in
**5 of 12** buckets in MODERN (42%; null median 50%, observed at the 19.6th percentile), 6/12 in
PRE (50%, 38.8th percentile), and 4/12 in FULL (33%; **8.3rd percentile**). The clock-aligned term
wins the head-to-head *less often than a coin flip*, in every era.

## 6. Stage 1 gate — printed by the program, not assembled by hand

| GATE | SPEC | OBSERVED | PASS/FAIL |
|---|---|---|---|
| S1-A mean `beta_same` > 0 | mean_b `beta_same` > 0, MODERN, b=1..12 | +0.00629 (t = +0.48, session-clustered) | PASS |
| S1-B same beats adjacent | mean `beta_same` - mean `beta_adj` > 0 | margin +0.00406 = +0.00629 - +0.00223 (t = +0.17) | PASS |
| **S1-C margin survives MAX null** | margin > p95 of the max-over-buckets null, 2,000 draws | +0.00406 vs p95(max) +0.11513 [p95(mean) +0.01786] p = 0.9985 | **FAIL** |
| S1-D `beta_nonmult` ~ 0 | mean `beta_nonmult` indistinguishable from 0, abs(t) < 1.96 | -0.00992 (t = -1.67, clustered SE 0.00595) | PASS |
| **STAGE 1 VERDICT** | ALL of S1-A .. S1-D | at least one clause FAILS | **FAIL** |

**S1-A and S1-B "pass" on sign only and neither is a finding.** Neither the treatment nor the
adjacent-bucket control is distinguishable from zero at all (t = +0.48 and t = +0.12), and the
margin between two numbers that are both zero is itself zero. `beta_nonmult` (-0.00992) is *larger
in magnitude than the treatment* (+0.00629), which is the opposite of what the mechanism requires:
the non-daily-multiple lag is doing at least as much as the daily-multiple lag.

The population is **not** redefined. S1-C is recorded FAIL.

## 7. Stage 2 — did not run, and that is the point

`S2_precondition` is unambiguous: Stage 1 must PASS in MODERN, otherwise Stage 2 does not run and
**no dollar figure is produced**. None was. No position was formed, no P&L was computed, no
candidate was created.

The bucket-subset prohibition is enforced **in code**, not by convention, and the guard was
exercised on the record even though Stage 2 never ran — `stage2.refuse_bucket_subset([6, 8, 10])`
(the three best MODERN buckets in the table above) raises rather than obeying.

For the record, and as **spec text rather than a result of this run**: 13 round turns per session x
~250 sessions = ~3,250 RT/yr; at the EXEC01 primary line of **$20.65/ctrRT (= 1.032 NQ points)** the
annual cost of the frozen rule would have been **~$67,112/yr**. The WAVE B candidate's ~0.9-point
assumption was stale, and 1.03 points is roughly 4x a quiet 30-minute bucket's mean |return|. The
candidate never had to reach that bar, because the structural stage killed it for free — which is
exactly why Stage 1 exists and why it ran first.

## 8. What is closed and what is emphatically not

**CLOSED.** The transfer to NQ of the HKS-style cross-day clock-bucket periodicity mechanism, at the
30-minute bucket width, on NQ 1-minute data, in MODERN — and in PRE and FULL alike, so this is not
an old-regime-survives story. That also removes the shared premise from every other WAVE B candidate
that leans on *"scheduled institutional flow leaves a periodic price trace"* **on this instrument**.

**NOT CLOSED — HKS itself.** Heston/Korajczyk/Sadka (2010) was measured on **US EQUITY
CROSS-SECTIONS**, where the periodicity is a cross-sectional return-sorting effect across thousands
of names with heterogeneous institutional ownership and index membership. NQ is **one index
future**. A null here falsifies the **TRANSFER**, not the original finding. The spec named this trap
before the run and it is repeated here so no reader over-reads the result.

**Also out of scope by construction:** any other bucket width — spec prohibition 5 bans a width
search in this run **and in any successor**, so "try 15 minutes" is not an available next step; any
cross-sectional version; any conditional or state-dependent version.

**What the null actually bought.** The spec ranked this candidate first on EVI rather than on
expected profit precisely because a null here is worth more than a small edge elsewhere: it closes a
peer-reviewed channel's transfer, it closes a premise several sibling candidates were leaning on,
and it cost $0 and one afternoon of already-on-disk NQ 1-minute data. **A clean, cheap closure is
the success case for this run, and this is it.**

---

*No order was placed, modified or cancelled. No strategy was deployed, enabled, started or stopped.
No CrossTrade or NinjaTrader call was made. No `.cs` file, nothing under `research/weekly_edge/src/`
and nothing under `research_sdk/` was modified. No promotion, build or deployment originates from
this run. $0 spent. LIVE = NO.*
