# G3_LIQREV01_READJ_20260906 — REPORT

**Ledger G00071 · family GENESIS3_REGIME · executed 2026-09-06.**
Design: `DESIGN_FROZEN.md`, sha256 `45fedf86bf0a209dd5571a2797f6cb51078634df3c251e5566d3ea3ce775cb79` (verified before execution). Object: the byte-frozen s90_q20 cell of `research/system_master/LIQREV01_STRESS_REVERSAL/SPEC.md` (stress 0.90 / q20-q80 / rv5 win 5 / pct win 252 / ret win 63 / 1-day hold / C1 costs / seed 20260819). Zero retuning. **Evidence status: DISCOVERY_CONSUMED throughout** — the object was selected on this same window.

## VERDICT (mechanical, preregistered binary rule)

> **DEAD — PERMANENT CLOSURE.**
> Scoped reason (verbatim per §3): *"the exact LIQREV01 post-2020 vol-acceleration reversal object is not a rational regime-local standalone engine at deployable micro size — failed D6b worst combined day, D6c daily corr on DISCOVERY_CONSUMED re-adjudication."*
>
> Scope of closure: **this exact rule as a production engine, permanently.** NOT closed: the rv5 stress-state infrastructure, the matched-placebo machinery, the historical 8-gate dev record. Closure does not reopen any alpha-hypothesis budget. "Wait for future data" was not an admissible disposition and is not taken.

## Gate table (printed by the program — `out/gate_table.txt` carries the full log)

```
GATE                       | SPEC                                                           | OBSERVED                                       | PASS-FAIL
--------------------------------------------------------------------------------------------------------------------------------------------------------
D1 repro                   | regenerated trade-table sha == canonical artifact sha          | repro c133ba198bbfbdca / canon c133ba198bbfbdca | PASS
D2 W2020 economics         | episode-block bootstrap CI_lo > 0 (seed 20260819, 10k)         | CI_lo +$692.71 (dev-def CI_lo +$687.42)        | PASS
D3 W2021 ex-COVID          | episode-block bootstrap CI_lo > 0 on entries >= 2021-01-01     | CI_lo +$607.63 (n_ep 20, n_trades 118)         | PASS
D4a worst trade @1MNQ      | |worst historical trade| <= $2,594.55 (5% of full pool)        | -$2,313.44                                     | PASS
D4b W2020 maxDD @1MNQ      | maxDD (worse of two computations) <= $7,783.65 (15% of pool)   | way1 -$2,314.37 / way2 -$2,314.37              | PASS
D5 regime monitor          | R(2026-05) ON: >=8 trades in 36m AND trailing-36m net > 0      | n36=72, net36 +$110,126.08, ON                 | PASS
D6a bottom-decile damage   | LIQREV net on P1 bottom-decile days > -$10,000 @1NQ            | -$9,415.52 on 7 active of 61 days              | PASS
D6b worst combined day     | <= 1.5x worst P1-alone day at deployed scale                   | 1.604x (-$2,782.17 vs -$1,734.89)              | FAIL
D6c daily corr             | full-overlap daily corr <= 0.25                                | +0.365 (active-day corr +0.614)                | FAIL
D7 worst-rung cost         | W2020 net/trade > $500 @1NQ at worst fill x 4t/side x 3x comm  | $1469.83 (next_open_0930)                      | PASS
```

## D1 — validity precondition (PASS)

The frozen pipeline of `research/system_master/LIQREV01_STRESS_REVERSAL/src/01_liqrev01.py` was replicated verbatim (substrate sha `dfd017ef...` asserted; max session 2026-05-29 < 2026-08-01 asserted; release source `hist_calendar(2005-2021) + w8bfade release rows (2022+)` reproduced). The regenerated 455-trade table serialized to sha256 `c133ba198bbfbdca058aba70503ccb617d2ae8b55cc29800b50a7ed23342016e` — **byte-identical to the canonical artifact**. The environment has not drifted; the run adjudicates.

Frozen-pool intersection (OQ-8 rule): all four registers (W5-168, MICRO-141, BBO-19, ESNQ-15) are tick/BBO session pools; this run read no tick/BBO file and extracted nothing — input-file-list ∩ pool-member lists = EMPTY. Disclosed: the design cites the governance memo at `research/genesis2/`, which does not exist; the actual file is `runs/G2_WAVE5_CARDS_20260906/BBO_GOVERNANCE_MEMO.md` and was used.

## D2 — post-2020 economics (PASS)

W2020 (entries 2020-01-01 → 2026-05-29): **154 trades, net +$259,973.56, +$1,688.14/trade, +$777.70/wk** over the 334.3-week window. **Weekly-vol Sharpe (lead metric) 1.018** on the 335-week exit-attributed grid (63 non-zero weeks); eval_battery native income $776.04/wk. Trade-level-equity maxDD −$23,143.72 @1 NQ / −$2,314.37 @1 MNQ — **descriptor only, never a selection denominator; no fixed-DD/CDaR improvement claim is made anywhere in this run, so no thinning placebo is owed.**

Episode-block bootstrap (10,000 reps, seed 20260819), both definitions printed:
- **SPEC-conformant** (maximal runs of stress sessions, gaps ≤5; 67 full-sample stress episodes, 23 with W2020 trades): **CI [+$692.71, +$2,558.75] → GATE PASS.**
- DEV definition (trade entry-gap runs — disclosed deviation of the original code from SPEC wording; 28 groups): CI [+$687.42, +$2,546.32]. The two constructions agree.

## D3 — episode dependence / not-a-lottery (PASS)

All 23 W2020 episodes listed in `out/episode_table.csv` (none omitted). Top-1 episode (COVID, 2020-02-24→04-02, +$83,971) = **32.3%** of W2020 net; top-3 = **65.6%**. Ex-top-3: net +$89,410 over 20 episodes, CI [+$143.18, +$1,617.31] (non-gating, still positive). Droughts in words: after 2022-05-17 the stress gate went fully dark for **661 days** until 2024-03-08; calendar **2023 and 2019 produced zero trades** — a 1.8-year silent stretch is normal for this object and is not regime death (handled by D5's 36-month lookback).

**W2021 gate** (calendar-prespecified COVID exclusion): 118 trades, +$181,920.52 (+$1,541.70/t), episode CI [+$607.63, +$2,549.46] over 20 episodes → **PASS**. The object earns after its dominant episode is date-excluded.

## D4 — tail at 1 MNQ (PASS on both bars)

At the fixed deployment unit 1 MNQ (= 1/10 of the measured NQ ledger): worst historical trade **−$2,313.44** (2025-04-03 long; bar $2,594.55 = 5.0% of the $51,891 full pool) → PASS. W2020 ES5 −$1,264.72; worst episode −$634.94; worst calendar month −$925.12 (2022-01).

MaxDD computed **two ways, each stated in words (the CAP01 lesson)**:
- WAY 1 — largest peak-to-trough decline of cumulative *trade-level* equity, trades in entry order: **−$2,314.37**.
- WAY 2 — largest peak-to-trough decline of the *calendar-day* equity path (exit-date-attributed daily P&L including 1,498 zero sessions): **−$2,314.37**. Identical.
Bar $7,783.65 (15% of pool) → PASS with wide margin. Neither figure is "P(losing the account)"; each is a maximum historical drawdown of one realized path.

Live-account ratios (non-gating; pool policy is the owner's): worst trade and maxDD are each **22.7% of the $10,206 live account**.

**Zero-edge line for the owner packet** (CAP02B-style, labeled): removing the mean from the 154 W2020 trade P&Ls (edge := 0) and forming all 154 circular shifts, the event "trade-path maxDD reaches the $7,784 bar" has **probability 0.000** (null median $6,437, p95 $6,913). A drawdown probability under a stated null — not a ruin probability.

## D5 — regime observability (PASS)

R(d) = trailing-36-month net of the frozen rule's own trades, ON iff ≥8 trades and net > 0, monthly 2010-01→2026-05 (`out/regime_monitor.csv`, 197 rows): pre-2020 ON 67/120 months; **ON in 77 of 77 months from 2019-12 through 2026-05** — flips ON with the 2020 regime and never flips OFF; 2023's zero trades are absorbed by the lookback (min n36 in 2023 = 46). Last computable month-end 2026-05-31: n36 = 72, net36 = +$110,126.08, **regime ON → PASS**. Secondary era-safe read V(2026-05-29) = 1.557 (non-gating). The optional 2026-06→07 extension was NOT performed: the only 2026-06→07 store on this box is a bid/ask quote-bar parquet with no Last-price series, so the frozen rule cannot be extended without constructing a new substrate; per R_extension its absence does not block.

## D6 — portfolio marginal vs the LIVE P1 book (a: PASS · b: FAIL · c: FAIL)

Reference: `runs/WE_W56_BREADTH/out/p1_daily.csv`, sha256 `9bc2d7f7000653b4d15f82b9ac9bf76ac25ec4cdbdb008d382453ec082a75357`; disclosed: Python-chain P1 is ~2.0% optimistic (double-lagged ATR, we_fastctx.py:81) — immaterial for correlation/geometry. Join: 632-day union grid 2022-07-05→2026-05-29 (607 P1 rows; 72 LIQREV-active days; 25 LIQREV exit days zero-filled on the P1 side). **Thin-overlap honesty: only 72 LIQREV trades intersect the ledger** (2024–2026 only; 2022 trades end 05-17, 2023 empty).

- **(a)** LIQREV net on P1 bottom-decile days (threshold −$1,794.57, 61 days, LIQREV active on 7): **−$9,415.52 @1 NQ → PASS**, by only $584 against the −$10,000 bar. A zero-trade P1-bad-day contributes $0 — that is the no-harm finding, but the seven active days nearly consumed the entire allowance.
- **(b)** Worst combined day at deployed scale (0.3×P1 + 0.1×LIQREV): **−$2,782.17 on 2025-04-04** (P1 −$1,562.44 plus LIQREV's worst historical trade −$23,134.36 ×0.1) vs worst P1-alone deployed −$1,734.89 (2023-08-25) → **1.604x > 1.5x bar → FAIL.** The Solar precedent (1.76x refuting) reproduces against P1: the object's worst outcome lands on a P1 losing day and makes the book's worst day materially worse.
- **(c)** Full-overlap daily corr **+0.365 > 0.25 → FAIL** (both-active-day corr +0.614; P1-losing-day corr +0.013). The engine trades the same high-vol state P1 monetizes.
- Reported: weekly-vol Sharpe P1-alone(deployed) 2.261 vs combined 2.107 (Δ −0.155); day-clustered bootstrap (paired day resampling, 10,000 reps, seed 20260819) P(ΔSharpe > 0) = 0.465 — the addition does not improve the book even before the damage bounds.

## D7 — cost / micro-execution viability (PASS)

Commission: MNQ **$1.30/ctrRT [BASIS=COMMISSION_ONLY, EVIDENCE=MEASURED, n=704]** → $13.00 per NQ-equivalent ctrRT; 3× stress rung $39.00. MNQ spread **UNMEASURED [ASSUMED]** → preregistered rungs {1,2,4} ticks/side. Fill-timing rungs {15:59, 16:03, next-open 09:30} recomputed on W2020 (gross at variant closes; the frozen ledger's 1-tick-adverse fills replaced by the explicit spread rung — no double-charge; next-open preserves the 1-session hold, 154/154 computable). All 24 rungs in `out/stress_rungs.csv`, BASIS-tagged. Net $/trade @1 NQ spans $1,680 (baseline best) down to **$1,469.83 at the worst rung (next-open × 4t/side × 3× commission)** → gate $500 → **PASS** ($146.98 @1 MNQ). Adapter feasibility facts stated in the log (MX01 pattern; overnight hold ⇒ full initial MNQ margin, 16:39/16:45 flatten conventions do not transfer; MIN-over-series roll guard; `LiqRev01Mnq_v1`; local-path compile only). Broker margin figure is a packet-time item — moot under DEAD.

## D8 — reporting obligations (reported, not gates)

1. **Post-2020 3×3 grid** (all 9 cells, no selection): s85_q20 n=211 $1,222/t · s85_q25 n=243 $1,121/t · s85_q30 n=272 $1,184/t · **s90_q20 n=154 $1,688/t** · s90_q25 n=175 $1,504/t · s90_q30 n=194 $1,396/t · s95_q20 n=83 $2,386/t · s95_q25 n=94 $2,061/t · s95_q30 n=103 $1,952/t. All positive; monotone in stress percentile — a plateau, not an argmax.
2. **Thin (13:00-halt) holiday sessions** (defined here as last-RTH-bar ≤ 13:05; 75 sessions): full-sample 8 trades touch them, net −$12,334.88 (conservative direction; the RECOVERY note's 11-entries/15-exits/−$15,695 used a different per-leg accounting — definitional variance disclosed). W2020 without them: n=151, $1,798/t (vs $1,688/t with).
3. **Overnight-gap flag, both constructions**: DEV ret-proxy flags 1 W2020 trade (+$42,081 — the best trade; without it $1,424/t); red-team-corrected minute-data gap flags 6 trades (+$729; without them $1,752/t). Both directions shown; neither changes any verdict.
4. **Long/short split W2020**: LONG n=83, +$131,433 ($1,584/t); SHORT n=71, +$128,540 ($1,810/t).
5. **Matched-placebo spread on W2020** (nearest calm-state trade by signed entry-day move, same side, median match distance 0.8 pts): real $1,688/t vs matched-calm **−$508/t** → state-attributable spread **$2,197/t**. The stress conditioning, not the trigger, carries the W2020 economics.

## §4 shadow-protocol reconciliation (recorded, never silent)

Outcome is DEAD ⇒ per the frozen design: **it is recommended to the owner, in writing, that the LIQREV01 shadow amendment to MONITOR-01 be formally retired.** The MONITORING_CALENDAR row edit ("HTFDIR01 + LIQREV01 shadow readings", due 2026-11-01) is to be performed **only after recorded owner acknowledgment** — no calendar row was touched by this run, and under no circumstance is one removed without a recorded decision. Until then the shadow amendment's KILL clauses remain in force as written.

## §6 honest multiplicity note (mandatory)

The object was originally SELECTED on this same window, so **D2's pass is partially guaranteed by construction**; the decision therefore hinges on D3–D7, which are new questions — and the verdict label says **REGIME-LOCAL(2020+) forever**. As it happens, the object died on D6, the genuinely never-measured number: its standalone ledger is real on its own terms, but it concentrates damage into the live book's bad days (1.604x worst-day amplification) and co-moves with P1 (+0.365 full-overlap, +0.614 when active) beyond the preregistered no-harm bounds.

## Artifacts

`runs/G3_LIQREV01_READJ_20260906/`: `src/run_readjudication.py` · `out/gate_table.txt` (full program log incl. the gate table) · `out/liqrev01_trades_repro.csv` (sha-identical to canonical) · `out/episode_table.csv` · `out/regime_monitor.csv` · `out/portfolio_marginal.csv` · `out/stress_rungs.csv` · `out/summary.json`. Nothing outside the run directory was written; no canonical document was modified; no NT8/CrossTrade tool was called; no data ≥ 2026-08-01 was read.