# ROLL02_EXECSERIES_GATING_20260906 — REPORT

**Trial G00047 · preregistered spec committed before results · run 2026-09-06 · seed 20260906**
**Evidence class: DISCOVERY_CONSUMED, in-sample · cost basis COMMISSION_ONLY ($4.36/ctrRT Lifetime, inherited from the G00041 ledger — the same basis as every G3_ROLLCOST figure)**

## VERDICT: **KILL**

G1_money FAILS: the P1-only recovered-strip net is **+$13,445.32** over 56 trades, but the
stationary-bootstrap CI90 is **[−$5,077, +$36,001] — it does not exclude 0** (P(resample
sum ≤ 0) = 0.139). Per the preregistered decision rule, **per-series roll gating is CLOSED as
not-worth-building; the ~9-day blackout stands as the price of the fail-safe.** The by-year
clause passed (positive in exactly 3/5 years) and G3_materiality passed (2.00 recovered trading
days/quarter > the 1.0 latch-fix kill bar) — the family dies on money, not on calendar
materiality: the strip is real but its P&L is statistically indistinguishable from zero, and
2024 alone contributes $13,256 of the $13,445 point estimate (99 %).

G4_risk_premise remains **OPEN** verbatim per spec (deferred to the 2026-09 crossover quote
capture, `research/operational/roll_quotes/quotes.csv`) — moot for a build decision now that
G1 killed the family, but the quote capture is unaffected by this verdict.

Program: `src/run_roll02.py` (self-contained, deterministic). Gate table printed by the
program: `out/gate_table.txt`. Per-quarter detail: `out/strip_by_quarter.csv`.

## Gate summary (program-printed table in out/gate_table.txt)

| Gate | Spec (falsifier) | Observed | Verdict |
|---|---|---|---|
| G1_money | P1-only strip: bootstrap CI90 excludes 0 AND positive ≥ 3 of years 2022–26 | net +$13,445.32; CI90 [−$5,077.24, +$36,000.96] includes 0; years 3/5 positive | **FAIL → KILL** |
| G2_frequency | restate headlines if strip entry rate < 50 % of baseline | 1.556 vs 2.014 entries/trading-day = **77.2 %** (calendar basis 108 %) → no restatement | PASS (informational) |
| G3_materiality | P1 recovered trading days/quarter > 1.0 | **2.00** (36 days / 18 quarters, Tue+Wed before expiry week) | PASS |
| G4_risk_premise | OPEN by construction (back-month tradability undecidable locally) | deferred to live crossover quote capture | **OPEN** |
| G5_semantic | headline semantics stated; strip + remaining = blackout net to the dollar | reconciles exactly, per leg and pooled (below) | PASS |

## What was measured (G5 headline semantics)

- **“+$13,445.32 P1 strip net”** — the event is: the sum of COMMISSION_ONLY P&L of the 56 (of
  2,439) historical P1 trades, 2022-01-02→2026-08-25, whose ENTRY calendar date fell in
  [R−10, R−8) around each of 18 quarterly third-Friday rolls R — the 2 trading days the live
  all-series guard blocks (NQ stored rollover = R−2, lead 8) but an exec-series-only guard
  (MNQ-pattern date = R) would not. In-sample, not forward, silent on fills (G4).
- **“−$26,378.48 XM strip net”** — same event over XM’s 4-day strip [R−12, R−8) (ES rolls
  earliest, R−4). **XM: in observation — secondary arm.** The negative sign means the earlier
  all-series block historically *helped* the XM leg.
- **“2.00 recovered days/quarter”** — CME trading days (Mon–Fri minus full closures; the only
  in-strip closures are Labor Day 2022-09-05 and 2023-09-04, both in XM strips) inside the P1
  strip, averaged over the 18 observable quarters.

## Reconciliation identity (G5) — proof this is the same object as G3_ROLLCOST

All 21 figures G3_ROLLCOST_00 published (pooled/same-day/lead-4 variants, per-leg splits,
five by-year rows, ledger totals) were reproduced **to the dollar** from the same ledger
(`runs/G2_AUG_INCUMBENT_READ_20260830/out/{p1,xm}_trades_full.csv`, the G00041 owner-authorized
read: 2,439 + 378 = 2,817 trades, $537,352.88) before anything new was computed — the program
aborts on any mismatch. Then, with the strip and remaining-blackout windows partitioning the
all-series window by construction:

| Leg | strip net | + remaining blackout net | = all-series blackout net | remaining ≡ G3 published |
|---|---|---|---|---|
| P1 (primary) | +$13,445.32 (56 tr) | $47,684.56 (250 tr) | $61,129.88 (306 tr) | $47,685 ✔ |
| XM (secondary, observation) | −$26,378.48 (18 tr) | $58,421.24 (41 tr) | $32,042.76 (59 tr) | $58,421 ✔ |
| Pooled | −$12,933.16 | $106,105.80 | $93,172.64 | $106,106 ✔ |

## DEVIATIONS (recorded, none affecting the falsifiers)

1. **G3_ROLLCOST’s `src/` does not exist in its run directory** (only `spec.yaml` and
   `out/console.txt` are committed). Its construction was recovered by exhaustive fingerprint
   over {date basis × window end × per-leg roll-date offset} and is **unique**: one roll date
   per quarter (R = third Friday of Mar/Jun/Sep/Dec, all series collapsed), classification by
   the ENTRY timestamp’s calendar date, observed window [R−8, R+1] (≡ [R−8, R], R+1 being a
   Saturday). Dollar-exact reproduction of all 21 published figures is the proof of identity —
   exactly the proof G5 was designed to demand.
2. **The spec’s premise about G3’s window is corrected, before results, by the fingerprint.**
   The spec assumed G3’s window was anchored at the *earliest* stored rollover across all
   series. In fact G3’s single third-Friday date **is the MNQ/YM-like latest-equity-index
   date**, so G3’s published window is already the exec-series window, and the live all-series
   guard blocks *earlier* (NQ = R−2, machine-verified 2026-09: NQ 09-16 vs MNQ 09-18 with
   blockFrom 09-08; ES = R−4). The recovered strip therefore sits **outside** G3’s window, at
   [R−10, R−8) / [R−12, R−8), matching ROLL01’s ~2 (P1) / ~4 (XM) recovered days, and the G5
   identity holds with G3’s number as the *remaining-blackout* term (table above). Under the
   spec’s literal premise the strip would be empty — a degenerate reading that would kill the
   family for an artifactual reason; it is recorded here and not used.
   **Corollary worth keeping:** the live all-series blackout’s historical foregone net is
   **$93,173 pooled — LESS than G3’s $106,106 headline** — because XM’s four extra blocked
   days were strongly negative. G3’s figure prices the exec-gated window, not the live guard’s.
3. **Adding the research spread model would only deepen the kill**: 56 P1 strip trades ×
   $14.44/RT ≈ −$809 off the +$13,445 point estimate (not applied; the gate runs on the
   ledger’s own basis, same as G3).

## Per-quarter table (P1 primary; full CSV in out/strip_by_quarter.csv)

| Roll R | P1 strip (2 td) | trades | net | | XM strip (obs., 3–4 cd) | trades | net |
|---|---|---|---|---|---|---|---|
| 2022-03-18 | 03-08..03-09 | 2 | −2,158.72 | | 03-06..03-09 | 1 | −4,269.36 |
| 2022-06-17 | 06-07..06-08 | 4 | +1,347.56 | | 06-05..06-08 | 0 | 0.00 |
| 2022-09-16 | 09-06..09-07 | 6 | +1,268.84 | | 09-04..09-07 | 0 | 0.00 |
| 2022-12-16 | 12-06..12-07 | 0 | 0.00 | | 12-04..12-07 | 1 | −3,649.36 |
| 2023-03-17 | 03-07..03-08 | 5 | −1,321.16 | | 03-05..03-08 | 1 | −3,354.36 |
| 2023-06-16 | 06-06..06-07 | 1 | +225.64 | | 06-04..06-07 | 1 | −1,044.36 |
| 2023-09-15 | 09-05..09-06 | 2 | −553.72 | | 09-03..09-06 | 1 | +2,300.64 |
| 2023-12-15 | 12-05..12-06 | 2 | +1,126.28 | | 12-03..12-06 | 2 | +341.28 |
| 2024-03-15 | 03-05..03-06 | 2 | +681.28 | | 03-03..03-06 | 1 | +305.64 |
| 2024-06-21 | 06-11..06-12 | 2 | +4,871.92 | | 06-09..06-12 | 0 | 0.00 |
| 2024-09-20 | 09-10..09-11 | 1 | +5,631.28 | | 09-08..09-11 | 1 | +1,630.64 |
| 2024-12-20 | 12-10..12-11 | 1 | +2,071.28 | | 12-08..12-11 | 2 | −7,113.72 |
| 2025-03-21 | 03-11..03-12 | 2 | +2,156.28 | | 03-09..03-12 | 0 | 0.00 |
| 2025-06-20 | 06-10..06-11 | 8 | −2,184.24 | | 06-08..06-11 | 0 | 0.00 |
| 2025-09-19 | 09-09..09-10 | 0 | 0.00 | | 09-07..09-10 | 2 | +726.28 |
| 2025-12-19 | 12-09..12-10 | 5 | −1,250.52 | | 12-07..12-10 | 3 | −9,618.08 |
| 2026-03-20 | 03-10..03-11 | 12 | −737.32 | | 03-08..03-11 | 2 | −2,633.72 |
| 2026-06-19 | 06-09..06-10 | 1 | +2,270.64 | | 06-07..06-10 | 0 | 0.00 |
| **Total** | 18 qtrs | **56** | **+13,445.32** | | 18 qtrs | **18** | **−26,378.48** |

P1 by-year strip net: 2022 +$458 · 2023 −$523 · 2024 +$13,256 · 2025 −$1,278 · 2026 +$1,533.
Headline rates: +$747/quarter ≈ **+$55/wk** on the ledger span — versus the $437/wk G3 quotes
for the whole exec-window blackout — and even that $55/wk cannot be told from zero (G1).

## What follows from KILL

- Per-series (exec-only) roll gating: **closed, not worth building.** No ROLL03 build spec.
- The roll fail-safe, its latch, and the 2026-09 blackout dates are untouched by this run —
  nothing here licenses any change to the live guard (P1 blocks new entries from 2026-09-08;
  both legs safe only ≥ 2026-09-19; authority remains `CURRENT_LIVE_TRUTH.md` §ROLL).
- The 2026-09 crossover quote capture (G4’s instrument) continues; its value is now
  descriptive (pricing the back-month spread), not a gate for any pending build.
- FAILURE_MEMORY row for family ROLL_PROCEDURE: to be added by the campaign ledger keeper
  (this run does not write the ledger).
