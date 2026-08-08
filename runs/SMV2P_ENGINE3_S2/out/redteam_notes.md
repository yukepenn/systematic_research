# STATISTICAL RED TEAM — SMV2P_ENGINE3_S2 (V4 §48 mandatory pass)

Reviewer: independent red-team agent, 2026-08-08. Verdict: **CONFIRMED**.
Scope: spec letter-exactness, independent recomputation, lookahead/leakage scan, report-language audit.
Nothing was fixed or modified; this file is the only write.

## 1. Spec applied letter-exact — PASS

- `spec.yaml` frozen in commit 58dc2d2 (2026-08-08 13:14:29 -0400), BEFORE any out/ artifact
  (13:25–13:26). `git diff 58dc2d2 -- spec.yaml` is empty — spec untouched since freeze.
- e377: VA = minimal contiguous band around VWAP bin holding coverage x RTH volume, 25c bins;
  center 70%/30min(10 bars); entry next 3m open; target far edge; 15:54 time-stop; one
  event/session. Plateau EXACTLY {60,70,80}% x {21,30,39}min = 9 cells (7/10/13 bars), no extras.
- e378: 20-sess RTH-close extremes rolling shift(1), range frozen at break, reclaim strictly
  inside within 2 sessions, entry next session 09:33 (0936 bar open), midpoint target, exit
  <= session close of 3rd held session, overnight held (as the spec itself discloses). Plateau
  EXACTLY lookback {10,20,40}, no extras.
- e379: last 2 trading days, sign = -sign(MTD at D_{n-2} session close vs prior-month final
  close), RTH-only day trades 09:33->15:57, day-only. Old-regime direction check on SM06 hist
  closes 2006-2021, gross points, per spec ("direction check").
- Gates coded at the spec thresholds verbatim: e377 t>=2/N>=150/WF/9-cell-sign;
  e378 t>=2/N>=80/WF/3-cell-sign; e379 t>=2/N>=100/dev-sign/old-regime-sign. No gate moved,
  no threshold softened, no post-hoc selection anywhere (summary-CSV dir/exit/year/day splits
  are diagnostics of the frozen center cell; no verdict depends on choosing among them).
- Verdicts follow the frozen verdict_rule mechanically: 0/3 pass -> slate-2 total failure ->
  V4 §51 quoted from the spec itself, not invented post hoc.

## 2. Independent recomputation — ALL MATCH

Own code (separate script, own VA/fill/NW/bootstrap implementations), from raw committed
substrate `runs/AUDIT03_BARS/nq_3m_2022_2026.csv` and the out/ artifacts:

| quantity | executor | red team | match |
|---|---|---|---|
| e377 full RE-SIMULATION (center cell, from raw bars) | N=273, total -80,465.28 | N=273, total -80,465.28, per-event max diff **0.00** | EXACT |
| e377 t_NW / t_iid | -2.1744 / -2.1681 | -2.1744 / -2.1681 | EXACT |
| e377 p_boot (block 5, B=10k, seed 20260808) | 0.9832 | 0.9832 | EXACT |
| e377 long side | N=152, -482.75, t -2.58 | N=152, -482.75, t -2.580 | EXACT |
| e377 target/timeout mix | 120/273 +1136.60 / -1417.37 | same | EXACT |
| e378 t_NW / WF halves | -0.8441 / -999.43 \| +172.01 | -0.8441 / -999.43 \| +172.01 | EXACT |
| e378 MTM reconciliation | -62,629.14 = -62,629.14 | same | EXACT |
| e378 target hits | 24/99 @ +4,530.95 | 24/99 @ +4,530.95 | EXACT |
| e379 full RE-SIMULATION (from raw bars) | N=104, total +5,411.56 | N=104, total +5,411.56, per-event max diff **0.00** | EXACT |
| e379 t_NW / p_boot | 0.1540 / 0.4562 | 0.1540 / 0.4562 | EXACT |
| e379 hist check (re-derived from SM06 parquet) | 191 mo, -1.0243 bps, t -0.1727, hit 51.31% | 191 mo, -1.0243 bps, t -0.1727, hit 51.31% | EXACT |
| joint-loss weeks (re-derived from source artifacts) | 230 wk, 50 primary / 69 secondary | 230 / 50 / 69 | EXACT |
| e377/e378/e379 JL-primary means | -624.91 / +252.68 / +104.43 | same | EXACT |
| e379 JL-secondary sign flip | -23.22 | -23.22 | EXACT |
| BMOM ledger x $5 vs BM_E2 column | "max abs diff 0.0" | 1.8e-12 (within assert tol 1e-6) | effectively exact |

Two full engines (377, 379) were re-simulated end-to-end from raw bars with independently
written code and reproduce the executor to the cent on every event. NW t, bootstrap, hist
check, and complementarity were all rebuilt independently and match.

## 3. Lookahead / leakage scan — CLEAN

- No full-sample scaling or normalization anywhere in `smv2p.py`.
- e377: decision info = prior-session VA + closes through bar j; fill at bar j+1 open. No
  same-bar decision-fill. Target-touch fills use the disclosed SMV2K e368 semantics
  (base = open if already beyond level else level, 1-tick adverse, capped by bar range).
- e378: signal at session r RTH close; entry next session's 0936 bar open. Rolling extremes
  `.shift(1)` exclude the break session; range frozen at break; first `lb` sessions correctly
  skipped (NaN guard) — burn-in respected. busy_until uses realized exit index only.
- e379: sign frozen at D_{n-2} session close; entry the following session. "Last 2 trading
  days" is exchange-calendar knowledge (ex-ante). Dev end 2026-05-29 is a true month end, so
  no truncated-month artifact in the 52nd month.
- Virgin data: raw substrate max sess_date 2026-07-31 (< 2026-08-01 assert), everything used
  clipped to <= 2026-05-31; event/exit max dates 2026-05-27 / 2026-05-20 / 2026-05-29; hist
  parquet asserted <= 2021-12-31. No data >= 2026-06-01 used, let alone >= 2026-08-01.
- All five input artifacts (AUDIT03 bars, SM06 hist parquet, SMV2H rerank_curves, SMV2B
  ledger_E2, SMV2M twin_daily) are git-committed and carry no local modifications.

## 4. Report language — HONEST

- FACT/INFERENCE/HYPOTHESIS labels used and used correctly; the one HYPOTHESIS (mirror
  continuation engine) is explicitly marked not-tested and anti-dup-barred from this run.
- All three kills recorded plainly; the "3/4 gates passed" framing for e377 is immediately
  qualified with "sign-stability passes are on NEGATIVE sign" — no gaming.
- No BLOCKED items claimed; none existed.
- Diagnostic INFO item (complementarity) explicitly disclaims rescue value ("noise on dead
  engines", V4 §42 no promotion from Stage 1). No policy/adoption language anywhere; the
  §51 consequence is the frozen verdict_rule, correctly triggered.

## 5. Minor notes (no verdict impact, recorded for the file)

1. Gate `old_regime_same_sign` adds `and sgn(dev_mean) > 0` beyond the spec letter. Strictly
   MORE conservative and moot here (signs already differ: +52.03 dev vs -1.02 bps hist).
2. Spec's "sign consistent across 2022-2026" was operationalized as the standard WF split
   (PASS: +69.43 | +16.23) rather than per-year signs (which are mixed and would FAIL). The
   operationalization is disclosed in REPORT.md and the per-year table is published alongside.
   Generous reading, but immaterial: e379 dies on the t-gate and the old-regime gate regardless.
3. REPORT wording "all episodes clear on entry" (e378) — in code, episodes clear on SIGNAL
   even when the entry is subsequently dropped (busy/no-0936). Wording imprecision only;
   the coded behavior is the disclosed most-recent-break convention and was verified.
4. Exec summary rounded ledger-vs-BM_E2 max diff to 0.0; true value 1.8e-12. Trivial.
5. e378 events CSV max entry sd = 2026-05-18 (verify_invariants says the same); the exec
   summary's "max exit 2026-05-20" is the sd_exit column — both correct.

## Verdict

**CONFIRMED.** Letter-exact spec application, exact independent reproduction of every
load-bearing number (including two full from-raw re-simulations), no lookahead or virgin-data
contamination, honest kill reporting, no adoption language. Slate-2 total failure stands;
V4 §51 (three new mechanism-expansion passes before any slate 3) is correctly triggered.
