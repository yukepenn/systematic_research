# W2C_CL_MR_20260906 — CL short-horizon / multi-day mean-reversion (falsifier)

**Run:** `runs/W2C_CL_MR_20260906/` · **Date:** 2026-09-06 · **Campaign:** CROSS_ASSET, Wave 2c
**Ledger:** trial **G00065**, family `CROSS_ASSET_NATIVE` (registered before outcomes).
**Evidence status:** `DISCOVERY_CONSUMED`. **Judged to the P1 bar. No deploy, no order, no enable. $0.**
Nothing here touches the live book `2047681`.

---

## Verdict — **underpowered** (survives-flag = **False**)

A weak, directionally-sensible **multi-day (W=10) reversion** edge exists in point estimate, is
**genuinely orthogonal to P1** (the diversifier property the campaign wants), and is **not** a
drift artifact nor a fixed-DD artifact. **But it is statistically indistinguishable from zero**:
the primary cell's after-cost drift-control spread is **$168/wk against an MDE of $457/wk**, its
block-bootstrap 95% CI **[−$248, +$547] straddles 0**, and it **does not clear the circular-shift
null** (p = 0.135). Across the **entire 36-cell neighborhood, 0 cells have a CI that excludes 0**,
and only 3 scattered cells clear the shift-null (≈ chance). There is therefore **no promotable
orthogonal directional engine**.

Because the co-primary edge gate (G2) is not cleared **anywhere** in the neighborhood, this run
routes operationally to the spec's FAIL branch — **the $0 cross-asset directional frontier is
exhausted-for-now** — but the honest statistical label for the primary cell is **underpowered**:
we did not establish an edge, and (MDE ≫ observed) we did not have the power to firmly establish
its *absence* either. What we can say is that at this sample size (≈240 weeks, 54 trades in the
primary cell) CL's multi-day return structure yields nothing that clears the P1 bar.

---

## G0 — seal & basis (program-asserted)

- Data: `runs/SM1M_CL_SUBSTRATE/out/cl_1m_2022_2026.parquet` — 1,608,018 bars / 1,184 sessions,
  **2022-01-03 → 2026-07-31** (full window).
- **POINTS basis** (additively back-adjusted — DELEV01; CL tick $0.01 was F2-lossless per the
  substrate build log). **PV $1,000/pt, $10/tick.** Every figure is a point/dollar difference,
  never % of a back-adjusted level.
- **SEAL:** the loader (`xinst_bench.load_substrate`) hard-drops every bar ≥ 2026-08-01 at load
  and the program **asserts** `max session 2026-07-31 < 2026-08-01` → **PASS**. No virgin bar is
  materialized. (0 rows dropped — the export was already capped at the §5 boundary.)

## Daily aggregation & the "o→c" deviation (named + justified)

Two daily **close** bases, indexed by session date, built from the 1-min substrate (bars
END-stamped, ET; pit = end-stamps in [09:01, 14:30], opens 09:00, settles 14:30 — per the CL
autopsy `runs/CROSSASSET_W1_CL_AUTOPSY_20260906/`):

| basis | close used | daily return | dates |
|---|---|---|---|
| **PIT** | 14:30 pit settlement close | settle-to-settle | 1,172 (pit sessions ≥250 bars) |
| **FULL** | full 18:00→17:00 session close | close-to-close | 1,183 |

**DEVIATION (named, justified).** The spec labels the pit basis "o→c". A *literal* intraday
open→close day-trade cannot be held across an H-day reversion: an H-day hold would incur **H
round trips**, contradicting the spec's own stated cost premise ("daily hold → low turnover →
cost should not bind"). I therefore realise the pit basis as the **continuous prev-settle→settle**
series (the autopsy's own multi-day MR series — §3 measured daily VR(10)=0.838 on
prev-settle→settle) with **one round trip per trade**. The intraday pit o→c return is retained as
the `pit_oc` diagnostic column. FULL uses the 24h session close. Both bases are run in full; the
findings agree across them.

## Mechanism (exactly the spec)

signal = z-score of the trailing-W point return `R_W,t = P_t − P_{t−W}` (W∈{5,10}; W=1 as the
coherence analog), standardised by the rolling mean/std of `R_W` over a **fixed** N=100-day window
(a nuisance parameter, **not tuned**). **FADE:** enter SHORT when z ≥ +k, LONG when z ≤ −k
(k∈{1,1.5,2}); exit on **z mean-cross** (z back through 0) **or max-hold H days** (H∈{2,5}). One
round-trip cost per trade; 1-bar cooldown → low turnover. Position set at close t earns day t+1's
return (no look-ahead).

**Cost:** ALL_IN = **$4.36/ctrRT commission (MODELED, flagged)** + **ASSUMED** spread
{0.5, 1, 2} ticks × $10/tick = {$5, $10, $20}. Realistic rung = **1 tick → $14.36 ALL_IN/ctrRT**.

**P1 reference:** P1 daily PnL reproduced from the XINST01 bench
(`runs/XINST01_WEEKLY_EDGE_PORT_20260906/src/xinst_bench.py`) — 2,401 trades, spread
$14.436/ctrRT, 1,056 days 2022-07-04→2026-07-31 (matches the documented P1 $14.44).

---

## Primary cell — full falsifier (gate table, program-printed)

A-priori cell chosen **from the autopsy before any result**: **basis=FULL, W=10, k=1.5, H=5**
(autopsy measured multi-day MR at VR(10)=0.838 / acf(5)=−0.078 → W=10; reversion horizon ~5d → H=5;
middle threshold k=1.5; on close-to-close returns → FULL). 54 trades, avg hold 4.81d, win-rate
0.611, mean net exposure **+0.0186** (near-symmetric fade).

```
gate  spec                                                                          observed verdict
G0    points basis, max session < 2026-08-01 (seal)                               2026-07-31    PASS
G1    MDE printed before observed spread (barrier)                      MDE $457 vs obs $168   FAIL*
G2    spread>0 & block-boot CI excl 0 & clears null                 $168 CI[-248,547] p0.135    FAIL
G3    W x k x H plateau of positive spread (>=60%)                   7/12 multi-day cells >0    FAIL
G4    edge on weekly-vol, not fixed-DD-only                               wv(spread) $327/wk    PASS
G5    positive spread in BOTH walk-forward eras                       22-24 $223 | 25-26 $63    PASS
G6    PnL-rho-to-P1 printed (low/neg = diversifier)               daily +0.148 weekly +0.029    PASS
G7    survives {0.5,1,2}-tick ALL_IN cost band                       spread>0 all rungs True    PASS
```
`*G1 = the barrier is respected (MDE printed before observed); the "FAIL" flags that observed < MDE.`

- **G1 (MDE-first barrier).** MDE for the drift-control spread (80% power, α=0.05, weekly-spread
  sd $2,842, 239 wk) = **$457.08/wk**, printed **before** the observed **$168.48/wk**. Observed is
  **BELOW** MDE — the study cannot resolve an effect this small.
- **G2 (co-primary edge).** After-cost spread $168.48/wk; **block-boot 95% CI [−$248.36, +$547.28]
  → does NOT exclude 0**; **circular-shift null (2000 shifts, seed 20260906) p = 0.1354 → NOT
  cleared.** FAIL.
- **G3 (plateau).** 7/12 multi-day FULL cells positive (58% < 60%); **0/12 with CI excluding 0**.
  No plateau.
- **G4 (weekly-vol, not fixed-DD-only).** weekly-vol of the spread (matched to P1) = **+$327/wk**
  → the point-estimate edge is *not* a fixed-DD artifact. (fixed-DD income $172/wk shown only
  beside its **rate-matched random-thinning placebo**: side-blind 10%-thinning median $155/wk,
  lift **−$17** — thinning does *not* inflate it; obs at the 64th pct. eval_battery led by
  weekly-vol throughout.) PASS.
- **G5 (era stability).** Spread positive in both walk-forward eras: 2022-2024 **+$223/wk**
  (157 wk) | 2025-2026-07 **+$63/wk** (83 wk). PASS (point estimate; neither era is significant).
- **G6 (PnL-orthogonality — co-primary).** **PnL-ρ-to-P1 daily +0.1478, weekly +0.0292** — LOW,
  as the autopsy's ρ(CL,NQ)=+0.05 predicted. This is the diversifier property; it holds.
- **G7 (cost).** After-cost spread stays positive across {0.5, 1, 2}-tick ALL_IN
  (169.6 / 168.5 / 166.2 $/wk) — turnover is low (avg hold 4.8d), cost does **not** bind — but no
  rung's CI excludes 0.

**Drift-control decomposition:** the exposure-matched drift control (a constant position = the
strategy's mean net exposure +0.0186, earning drift with no timing) absorbs only **$3.92/wk** of
the $172.40/wk raw after-cost edge. **The failure is NOT drift** (CL's secular drift is tiny, as
the spec anticipated) — it is **power**.

Eval battery (weekly, native): Sharpe(ann) 0.442, maxDD $38,992, return/DD 1.06.

---

## Neighborhood (`out/neighborhood.csv`) — plateau & coherence

36 cells (PIT & FULL × W∈{1,5,10} × k∈{1,1.5,2} × H∈{2,5}), each with the after-cost spread,
block-boot CI, and circular-shift-null p at the realistic 1-tick cost.

- **CI-excludes-0: 0 / 36 cells.** No cell establishes a spread > 0.
- **Clears the shift-null: 3 / 36** — PIT W10/k1/H2 (p=0.012), PIT W10/k1/H5 (p=0.021),
  FULL W10/k2/H2 (p=0.011). Scattered across bases and thresholds, ≈ the 8% you expect by chance
  across correlated cells, and **none of the three has a CI excluding 0.** Not a plateau.
- **Direction is coherent:** the W=10 cells are uniformly **positive** in point estimate
  ($90–$404/wk), W=5 mostly negative, W=1 weak — the multi-day reversion the autopsy described,
  just too small to resolve.
- **Coherence check holds (multi-day > 1-day) on BOTH bases:** mean spread 1-day −$5.7 vs
  multi-day +$60.5 (PIT); 1-day −$42.5 vs multi-day +$52.9 (FULL). Consistent with the autopsy
  (pit returns ≈ random walk at 1 lag; structure appears only over multiple days).

---

## Decision & classification

Per the spec decision rule: G2 fails (and fails **everywhere** in the neighborhood), so this is
**not** the campaign's first portfolio-additive orthogonal engine. With equities/gold/rates/energy
directional MR now all tested and none clearing the P1 bar, the **$0 cross-asset directional
frontier is exhausted-for-now** — recorded, no deploy. **`DISCOVERY_CONSUMED`.**

- **Classification:** the point-estimate edge, were it real, would be **NEW INFORMATION**
  (multi-day reversion, orthogonal to P1, not drift, not leverage, not a DD denominator). It is
  **not established** — the study is underpowered at the primary cell and null across the
  neighborhood on the co-primary CI gate.
- **The one durable, positive datum:** CL is a **genuine diversifier** to P1 (PnL-ρ ≈ +0.03
  weekly / +0.15 daily). If a *powered* CL edge is ever found (the autopsy points to
  **volatility**, not returns — EIA-Wednesday vol, shock-overshoot), its PnL would very likely be
  orthogonal to the live NQ book. The prize exists; this particular (directional multi-day MR)
  key does not turn it.

## Deliverables

| file | contents |
|---|---|
| `src/run_cl_mr.py` | full falsifier; seal assertion in the loader; daily aggregation; mechanism; drift control; block-boot CI; circular-shift null; eval battery (weekly-vol lead, fixed-DD + placebo); program-printed gate table |
| `out/gate_table.txt` | program-printed GATE / SPEC / OBSERVED / PASS-FAIL for the primary cell |
| `out/neighborhood.csv` | all 36 cells (2 bases × W×k×H + 1-day analog): trades, spread, CI, null p, weekly-vol |
| `out/daily_pnl.csv` | primary-cell daily strat-net / drift-control / spread / position, with P1 daily PnL aligned |
| `out/run_log.txt` | full console log |

**Reproduce:** `python runs/W2C_CL_MR_20260906/src/run_cl_mr.py` (fixed seed 20260906; ~1 min).

**Semantics.** Every figure is an **in-sample, pre-seal (<2026-08-01), POINTS-basis, after-cost,
`DISCOVERY_CONSUMED`** measurement of a research mechanism — **not** a forward or live number, and
**not** multiplied by any live-book factor. No order, no strategy enable, no live change. $0.
