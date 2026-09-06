# G3_CLOSEHOUR_20260906 — close-hour hedging-flow momentum, vol-gated (ledger G00085)

**VERDICT: FAIL-CLOSED AT SCOPE (spec §28). G2 FAIL, G4 FAIL — blocking set dead. The flow story
is refuted at this scope: the close hour REVERSES the day's direction on ES/RTY/YM, and the vol
gate makes the reversal STRONGER, the exact opposite of the LETF/dealer-gamma rebalance prediction.**

Evidence status: DISCOVERY (substrates DISCOVERY_CONSUMED for other objects). POINTS math on
back-adjusted 1-min substrates (`runs/SM1M_{ES,RTY,YM}_SUBSTRATE/out/`), seal-asserted < 2026-08-01.
Program: `src/closehour.py` → `out/gate_table.txt` (program-printed), `out/cells.csv`,
`out/era_table.csv`. No hand-assembled numbers.

## Frozen object (spec.yaml, committed before results)

s = sign(close(15:00) − close(09:30)) at 15:00 ET; hold s to close(16:00); 1 RT/day max.
Vol gate (PRIMARY arm): trailing-20-session daily range top half, causal. Family = 3 markets
× {gated, ungated} = 6 cells, K_eff-corrected; preregistered headline = **gated-ES**.

Two interpretation freezes were made mechanical **inside the program before results printed**
(recorded, see Anomalies): the gate reads "R(t−1) ≥ median of trailing-20 completed full sessions"
(full = reaches the 16:00 stamp; range = full-session high−low); the {1,2}-tick band is read per
SIDE plus the $4.36 Lifetime commission (BASIS=MODELED ALL_IN), the family convention set by
G00072 in this same wave.

## Result

| cell | n | gross pt/ses | net pt/ses (PRIMARY) | net $/ses | shift-null right-tail pct |
|---|---|---|---|---|---|
| **ES gated (HEADLINE)** | 555 | **−0.494** | **−1.081** | **−$54.07** | 70.05% |
| ES ungated | 1113 | +0.230 | −0.357 | −$17.85 | 31.12% |
| RTY gated | 543 | −0.105 | −0.392 | −$19.62 | 61.06% |
| RTY ungated | 1109 | +0.069 | −0.218 | −$10.89 | 38.94% |
| YM gated | 550 | −6.955 | −9.827 | −$49.13 | 89.30% |
| YM ungated | 1111 | −0.022 | −2.894 | −$14.47 | 49.73% |

- **G2 FAIL** (all three clauses): mean −1.081 pt < 0; block CI95 [−2.557, +0.686] does not exclude
  0 from above; shift-null right-tail pct 70.05% vs the K_eff-corrected bar 3.35%
  (ρ̄ = +0.603 over 15 pairs → K_eff = 1.494; null fully enumerated, k = 1..1111, shared offset
  across all 6 cells).
- **G4 FAIL**: gated-ES net 2022-23 = −0.931 pt AND 2024-26 = −1.184 pt — both-wrong-sign.
- **G3 FAIL** (recorded, classification): gated ≥ ungated fails in ALL THREE markets
  (ES −0.72, RTY −0.17, YM −6.93 pt gated-minus-ungated); RTY/YM positive support 0/2.
  The ordering is anti-flow-story: high-vol days reverse harder.
- **G5 FAIL** (recorded): STRESS net −1.581 pt. Moot — the headline cell is **gross-negative**,
  so the verdict is invariant to ANY non-negative cost reading (see Anomalies #2).
- **G1/G6 PASS** (procedural): MDE printed per cell before observed (gated-ES MDE_80 = 2.361 pt =
  $118/ses); weekly-vol lead Sharpe −0.59; path descriptives only, no DD-normalized income quoted.
- **ρ to P1** (G6, SOURCE `runs/WE_W56_BREADTH/out/p1_daily.csv`, zero-filled common calendar
  2022-07-05..2026-05-29, 971 sessions): **daily +0.216, weekly +0.272, both-traded-days +0.305.**
  The 15:00–16:00 window sits inside P1's live exposure; had the cell passed, it would have STACKED
  risk on P1, not diversified it. Recorded for the campaign's stacking ledger; moot for promotion.

## Classification

NEW INFORMATION (negative). Extends the campaign law — "NQ is the momentum outlier; everything
else mean-reverts" — into the cash-close hour: on ES/RTY/YM 2022–26 the day's 09:30→15:00
direction mean-reverts into the close, and conditioning on high trailing vol amplifies the
reversal in all three markets. The one positive cell-half anywhere is UNGATED-ES 2022-23
(+0.73 pt net) — the era the intraday-momentum literature was fit on — and it flips to −1.16 pt
in 2024-26.

**Post-hoc observation, NOT a candidate, NOT promotable from this run:** the mirrored fade would
be gross +0.494 pt/ses on gated-ES — still below even the PRIMARY all-in cost (0.587 pt), so no
monetizable reversal is hiding in the mirror at these costs either. Any pursuit would need its own
preregistered spec.

## Decision (mechanical)

G2 FAIL + G4 FAIL → **CLOSED AT SCOPE (§28)**. MC-13's close-window cluster is now measured and
dead at this scope; ledger G00085 records FAIL.

## Anomalies / notes

1. Spec predicted ~590 gated ES sessions; observed 558 gated / 555 traded (s==0 on 3 gated days).
   Delta comes from requiring the 16:00 cash-close stamp for "full session" and the exact
   top-half-rank construction; within the spec's "~".
2. Spec's G5 text named "{1,2}-tick band; ES $12.50/tick" without commission or a per-side/per-RT
   ruling. Frozen per-side + $4.36 ALL_IN (family convention, G00072). Robustness: at the cheapest
   defensible reading (1 tick per RT, $16.86 = 0.337 pt) gated-ES net = −0.831 pt — the verdict is
   cost-reading-invariant because the headline cell is already gross-negative (−0.494 pt).
3. G3 and G5 failed beyond the blocking set; recorded failed, no population redefined.
4. Verification: three-session manual spot-check by direct bar lookup and a full third-path rebuild
   of the ES cells both reproduced `cells.csv` exactly.
5. REPORT.md could not be written to the run directory (harness refused subagent report-file
   writes); full report content is returned in this structured output for the orchestrator to place.