# TERMFLOW01 — Calendar-flagged terminal-flow continuation into the cash close

**Status: FROZEN before any outcome read. Run class: BOUNDED_SELECTION (one 9-cell plateau,
no selection within it — pooled primary cell is the only adjudicated object).**
**Alpha budget: 2 of 2 for wave 2026-08-19d. One shot. Last funded candidate of the
ENGINE3_SCOUT_20260819 pool (rank 4 of 4; the honest weakest prior — both stronger-ranked
siblings CLOSEREV01/TOMFLOW01 already failed).**

## 1. Hypothesis (verbatim from the funded scout candidate)

On calendar-flagged sessions (month-end, quarter-end, monthly OPEX, quad-witching, NDX December
reconstitution), benchmark-tracked passive funds must execute at the 16:00 cash close; their
anticipatory order flow is price-inelastic and partially telegraphed from ~15:50, so the
15:30→15:50 drift on flagged days CONTINUES into the close rather than reverting. The
information is the calendar (who is forced to trade today), not the price path — MOM01's
CLEAN_NULL on all days is the built-in control: the claim is a flagged-day DIFFERENCE.
Literature: Cushing-Madhavan JFM 2000; Bogousslavsky-Muravyev JFM 2023; Chinco-Sammon JFE 2024;
Harris-Gurel JF 1986. Loser paying the bill: tracking-fidelity-constrained passive funds.
Mechanism predicts a RISING effect over 2006-2026 (passive AUM growth).

## 2. Data and construction (all frozen)

- Substrate: `research/scalping_lab/substrate/minute/NQ/nq1m_2005_202605.parquet`
  (2006-01-05..2026-05-29, POINT space, PV=$20, tick 0.25). LOCKED_FORWARD untouched.
- Trading-day calendar: RTH days with ≥200 bars 09:30-15:58 (house convention, TOMFLOW01's).
- **Step 0 (pre-outcome convention audit, mandatory before any P&L)**: document the bar-label
  semantics around 15:30-16:00 (bar counts per label minute across years; presence of 15:51 and
  15:59 labels) and write `out/convention_audit.json` BEFORE the event study runs. Prices used:
  `r_pre = c(15:50) − c(15:30)`; entry = o(15:51) (fallback c(15:50) if 15:51 label absent that
  day); exit = c(15:59). If >2% of flagged days lack any of the three labels, those days are
  dropped and counted in the audit.
- Flags (pure calendar arithmetic; a day trades ONCE regardless of how many flags it carries):
  last trading day of month; last trading day of quarter; 3rd Friday of every month; quad-witch
  3rd Fridays (Mar/Jun/Sep/Dec); 3rd Friday of December (NDX reconstitution effective). The
  standalone-N=4 December-reconstitution kill (slate 5) is disclosed; here it is one member of
  a pooled family and no subfamily selection is permitted after the read.
- Rule: flagged days only; dir = sign(r_pre) (skip if 0); long/short 1 NQ at entry+1 tick
  adverse, exit at exit−1 tick adverse (per direction); commission $4.36/RT. One event/day,
  always flat by the close; no overnight.

## 3. Gates (ALL AND-required unless marked disclosure)

- **G1** N_traded ≥ 400.
- **G2** pooled net > 0 AND iid bootstrap CI_lo > 0 AND year-block bootstrap CI_lo > 0
  (B=10,000, seed=20260819).
- **G3-SPLIT (standing rule)** pre-2020 and post-2020 event means both > 0; iid CI on each:
  ≥1 CI_lo > 0, neither CI_hi < 0.
- **G4** structural halves 2006-2015 / 2016-2026: both means same sign; the mechanism's own
  prediction (second half STRONGER) is reportable, not a kill, if both are positive.
- **G5** flagged-minus-matched-unflagged difference: control = identical rule on 3 unflagged
  days per flagged day, drawn without replacement within the same calendar year
  (seed=20260819). Require t_NW(lag 5) ≥ 2 on the pooled flagged mean vs 0 AND on the
  flagged-vs-control difference.
- **G6** plateau: entry {15:45, 15:50, 15:52} × lookback-start {15:30, 15:35, 15:40} = 9 cells
  (exit fixed 15:59): all 9 pooled means same sign. No cell selection — primary cell is
  (15:50 entry ≡ o(15:51), 15:30 lookback).
- **G7** concentration: top-1% of events ≤ 50% of |net|; single best and single worst each
  ≤ 25% of |net|.
- **G8** losing-day correlation vs Solar (daily MTM of TERMFLOW events joined to
  `HTFDIR01_DIRECTIONAL_TILT/out/daily_ledgers_dev.csv` B_SYM on Solar losing days) ≤ 0.25;
  net on Solar losing days reported (disclosure).
- **G9** redundancy: proxy for deployed-momentum direction at 15:50 = sign(c(15:50) − session
  09:30 open); if it matches TERMFLOW's direction on > 70% of traded flagged events, FAIL
  (the flow signal would already be held by the momentum book; proxy disclosed as such).
- **G10** cost stress: 2 ticks/side + 3× commission; require stress net > 0 AND stress iid
  CI_lo > 0.
- Disclosure only: per-flag subfamily table (no selection); per-year net; skip counts.

## 4. Decision rule (frozen)

- ALL PASS → adversarial red team; if confirmed → engine-3 construction path (separately
  preregistered C1 confirmation; nothing touches the frozen baselines).
- ANY FAIL → family CLOSED one-shot. With it, the ENGINE3_SCOUT_20260819 funded pool is
  exhausted (0-for-18 constructed candidates if so), and per the program's own EVI note,
  OHLCV-substrate engine hunting PAUSES pending the forward calendar (MONITOR-01 #2,
  ≥2026-11-01) and new-data classes (GAMMA00 / DOM re-auth / U9B accrual).

## 5. Honest prior (written before the read)

Rank 4 of 4 in its own scout pool. Three compounding halvers named in the scout: the direction
proxy (no imbalance feed), Bogousslavsky-Muravyev's near-complete auction-deviation reversion
(the final-minutes segment may be fade-shaped), and the early-era cost squeeze (0.72 pt RT was
~4.5bp of 2006 NQ). MOM01's all-days CLEAN_NULL is an honest bad prior for any NQ intraday
continuation. Power at literature effect sizes is real (~500 events; 5bp flagged drift vs
~30bp 10-min sigma → t≈4; 2bp → t≈1.6). Prediction: FAIL is more likely than PASS; a
significantly NEGATIVE pooled mean (fade-shaped close) would be a reportable finding but the
engine dies either way. Either outcome closes the scout pool decisively — that closure is the
deliverable.
