# TERMFLOW01 — REPORT (readout 2026-08-19; spec frozen at 8cc0fcf BEFORE the run)

**Verdict: FAIL — the flagged-day difference is literally zero (t = −0.06 vs matched
unflagged control). Family CLOSED one-shot. With it the ENGINE3_SCOUT_20260819 funded pool is
EXHAUSTED: engine-3 constructed candidates now 0-for-18 (+2 parked regime-locals). Per the
frozen decision rule, OHLCV-substrate engine hunting PAUSES pending the forward calendar
(MONITOR-01 #2 ≥2026-11-01) and new-data classes. Alpha budget 2/2 spent (wave 2026-08-19d).**

## Numbers (N=470 flagged events, 2006-2026, C1 with 1t/side)

- Net **−$1,769** (−$3.76/event); iid CI [−46.8, +39.8], year-block CI [−54.4, +44.6] — G2 FAIL.
- **G5 (the mechanism's own gate) is the decisive null**: flagged-day t_NW = −0.15; the
  flagged-MINUS-matched-unflagged difference t_NW = **−0.06** (control mean −$0.17/event,
  n=1,350). Flagged days behave exactly like any other day — the passive-flow story leaves NO
  tradable 15:50→close residual on NQ at any point in 20 years. MOM01's all-days CLEAN_NULL
  extends to the flagged-day difference.
- G3-SPLIT FAIL: pre-2020 mean **−$10.20**/event (CI [−22.2, +1.9]); post-2020 +$9.97
  (CI [−125, +145]). G4 halves opposite signs (−$18.6 / +$10.1) — the "rising with passive
  AUM" prediction is directionally present (G4_second_half_stronger=true) but the first half
  is negative and nothing is distinguishable from zero.
- G6 plateau FAIL — with a disclosed implementation defect: the three e1545 cells as coded
  keep the 15:30→15:50 lookback while entering at 15:45, i.e. they use c(15:50) before it
  exists — **lookahead; those three cells are INVALID as constructed** (their +$65-99 means
  are an artifact of peeking 5 minutes ahead, and incidentally an unintended extra
  confirmation that the only "signal" here is lookahead). The six legitimate cells span both
  signs (−$23.3 to +$12.5) → G6 fails on the valid cells alone; no rerun (verdict unaffected).
- G7 concentration "fails" mechanically (top-1% share 5.28×) — meaningless: the denominator
  |net| ≈ 0. Disclosed, not interpreted.
- G10 stress FAIL. G8 PASS (ρ_losing = −0.26; net on Solar losing days −$8,731 disclosed).
  G9 PASS (momentum-direction match 58.5% ≤ 70%).
- Per-flag (descriptive ONLY, selection banned by spec): quarter-end +$90.3/event (n=80),
  OPEX −$57.6 (n=156), plain month-end +$1.5 (n=153). The quarter-end cell is exactly the
  post-hoc cherry the spec pre-banned; anyone tempted should reread G5's t = −0.06 and
  TOMFLOW01 (the month-end long family already failed at N=244).

## Interpretation

The gatekeeper's rank-4 prior was right, and the most-likely kill named in the spec fired:
futures price the anticipated MOC flow before 15:50 (or the residual is fade-shaped and
self-cancelling) — either way there is nothing left to continue. The closure is the
deliverable: all four funded candidates of the 2026-08-19 literature scout (LIQREV, CLOSEREV,
TOM-FLOW, TERMFLOW) are now adjudicated, at a total cost of four preregistered one-shots. No
red team needed (FAIL, nothing adopted; the one implementation defect found is disclosed above
and is anti-conservative in the direction that makes the FAIL more certain, not less).
Artifacts: `out/termflow01_{results.json,events.csv,control.csv}`, `out/convention_audit.json`.
Seals untouched (substrate ends 2026-05-29).
