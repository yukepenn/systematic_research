# V3 MASTER-GAP HUNTER — result (tag: mg)

Scripts: `v_mg_diag.py` (excess localization), `v_mg_refine.py` (stage 1/2 grid),
`v_mg_refine2.py` (stage 3 constrained), `v_mg_final.py` (micro-grid + fingerprint).
JSON outputs: `v_mg_diag.json`, `v_mg_refine.json`, `v_mg_refine2.json`, `v_mg_final.json`.
Method: T1-only flip chains make legs gate-independent, so all gates were replayed
exactly over a once-generated leg stream (sanity: base D-gate replay reproduces the
registered INT_T1only cell bit-for-bit: n=5011, net=244,589.02). Label constraint is
checked on the EARLY-mode base stream with hunt_D semantics (42 HARD labels), master
aggregates on the LATE-mode INT_T1only stream.

## 1. WHERE the +660 excess / −47.6k gap lives (base INT_T1only, X1600/K3/C1000)

Month-by-month trades/day (sim; target overall = 8.26/day):

| period | t/day | note |
|---|---|---|
| 2023 (258 sess) | 7.42 | at/below target rate |
| 2023-01 | 8.00 | ≈ target — the labeled month already fits |
| 2024 (259 sess) | 10.53 | above |
| 2024-07 | 12.70 | |
| **2024-08** | **20.55** (452 trades / 22 sess) | VIX-spike chop; sessions 08-05: **69** trades, 08-02: **59** |
| 2024-09 | 13.19 | |
| **2025-01** | **16.77** (369 trades) | |

The excess is **NOT uniform — it is concentrated in high-volatility chop months**
(2024-07..09, 2024-12, 2025-01). Supporting cuts:
- Sessions with ≥12 trades: 140 sessions carry 2,419 trades netting **−57.5k**; ≥15
  trades: 80 sessions, 1,656 trades, −30.4k. Chop-session churn is both the count
  excess and the net gap.
- Hold-length: trades held <30 min net −839k gross (wr 4.9–22%); everything ≥60 min is
  strongly positive. The excess trades are short-hold churn re-entries.
- Direction: sim SHORT net 38.8k vs target 77.3k (−38.4k of the −47.6k gap is short-side);
  count excess is direction-balanced (+317L/+343S).
- NOT the evenings (18:00–24:00 entries: n=308, pf 1.163, +17.7k — blocking them moves
  AWAY from target), not weekday-specific, not overnight sessions.

## 2. Refinements tested (all on top of the D-gate; hard gate = 42/42 HARD labels AND
Jan per-day-table feasibility not worse than base: nosol ≤ 2, cents ≥ 5)

| family | outcome |
|---|---|
| stronger X within (1536.6,1937.5] / C within (300.16,1328.52] | X: no help; **C=700 helps** in the final combo (holdS + net closeness) |
| **second armed threshold pre-noon (X2)** | **WORKS.** high ≥ X2 arms the cum<0 / K-consec blocks at any time of day. X2=2000 breaks 6 HARD labels (01-03 pre-noon session high 2,486.64 ⇒ X2 must be > 2,486.64); X2=2500 passes everything, alone: −127 trades, +12.5k net |
| **max-entries-per-session cap (capM)** | **WORKS.** capM=20 Jan-neutral (busiest Jan day = 19 legs sets the floor; target itself traded 16 on 01-12, so caps ≤16 are impossible); clamps the 69/59-trade Aug-24 sessions |
| **reentry cooldown after touch-exits (cd)** | **WORKS at cd=3 bars** only; cd ≥ 5 destroys Jan feasibility (nosol 2→3-4) |
| daily-stop after N total losses (lossN) | lossN=11 alone strong (score 0.85, jan rm 6→1) but breaks 01-04 feasibility (nosol→3); lossN=14/16 add nothing in combos — rejected |
| stop-after-N-consec-losses any side, with re-enable (stopN/R) | never competitive |
| evening variant (block 18–24h unless \|prior\| small, eveP) | never helps — evening entries are profitable |

## 3. Best configuration (all constraints pass: 42/42 HARD, Jan cents=5, nosol=2, rm improves 6→5)

**D-gate X=1600, K=3, C=700 + X2=2500 (pre-noon armed) + capM=20 (max 20 entries/session) + cd=3 (3-bar reentry cooldown after touch-exits)**

Closeness score (weighted master distance) 1.0909 → **0.5441** (−50%).

| | n | L/S | net | WR% | PF | DD | hold (L/S) | maxW/maxL | lnet/snet | t/day | cW/cL |
|---|---|---|---|---|---|---|---|---|---|---|---|
| TARGET | 4351 | 2166/2185 | 292,172.82 | 40.29 | 1.18 | −32,677 | 94.15 (105.85/82.56) | 7705.82/−4449.18 | 214,911/77,262 | 8.26 | 8/15 |
| base INT_T1only | 5011 | 2483/2528 | 244,589 | 39.83 | 1.127 | −29,077 | 93.02 (105.61/80.65) | same | 205,741/38,848 | 9.30 | —/— |
| **FINAL** | **4598** | 2265/2333 | **264,955** | **40.08** | **1.152** | **−31,934** | 95.56 (109.62/81.91) | 7705.82/−4449.18 | 208,387/56,568 | **8.53** | 7/15 |

Direction detail: LONG n=2265 wr 41.59 pf 1.250 (target 41.97/1.27); SHORT n=2333 wr
38.62 pf 1.062 (target 38.63/1.09). avgW 1089 / avgL −633 / W:L 1.72 (target 1112/−638/1.74).

Attribution: vs the base D-gate the refinement removes 435 legs (sum pnl −18.3k, avg
−42/leg) concentrated exactly where the excess was — 2024-08: 158, 2025-01: 65,
2024-07: 30, 2024-12: 27 — and Aug-24 t/day drops 20.6→13.8, 2025-01 16.8→13.8.

## 4. Honest caveats

- X2/capM/cd were selected on master aggregates; Jan only interval-bounds them
  (X2 > 2486.64, capM ≥ ~19, cd ≤ ~4). Overfit risk to the master row is real; the
  constants are round and the mechanism (chop-day throttle) is plausible for a manual
  or semi-manual trader, but this is a closeness fit, not an identification.
- Remaining gap: +247 trades, −27.2k net, and −20.7k of it is SHORT-side net; the two
  stubborn Jan NOSOL days (01-13, 01-17 — each missing one trade) and the unexplained
  01-16 resume short are unchanged. Residual still points at the signal-stream family
  (late-mode variant / unknown resume trigger), not at more equity gating.
- consecW 7 vs target 8: one long win-streak is being interrupted by a block — a cheap
  future probe for which rule fires mid-streak.
