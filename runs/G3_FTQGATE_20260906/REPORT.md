# G3_FTQGATE_20260906 — corr-regime-gated flight-to-quality — REPORT

**Ledger:** G00076, family GENESIS3_EVENT (registered before outcomes, seq 146).
**Verdict:** **CLOSED AT SCOPE (§28)** — decision rule fired mechanically: **G2 FAIL + G3 FAIL**.
**Evidence status:** DISCOVERY (2009-03..2026-07; no forward claim; seal ≥ 2026-08-01 untouched).

## 1. What was tested (frozen object, spec.yaml verbatim)

Event day: ES daily point-return ≤ −1.5 × trailing-60-session sigma (causal, sigma excludes day
d). Regime (causal, lagged one day): sign of trailing-60-session ES–ZB daily-point-return
correlation through d−1. The 2×2: {event} × {corr NEG / POS} → ZB forward close-to-close point
returns at h ∈ {+1, +1..+3, +1..+5}. Single primary claim at h=3: NEG-cell delta vs its
**own-regime unconditional control** > 0 AND interaction (NEG delta − POS delta) > 0.

Governance: the P-2 corr-reserve ruling is recorded **in the spec** (owner 2026-09-06 rider +
GENESIS III §25; precedent: same-day CL holdout retirement). Proceeded under it. The
≥ 2026-08-01 seal is a safety rule and was asserted on every input.

## 2. Data (documented choice)

Both legs from the per-contract NT8 **day store** via the certified causal construction
(`research/multi_market/src/ncd_day.py` + `roll.py`): ES 4,308 return-days, ZB 4,393
return-days, 2009-03-31 → 2026-07-31; identity gates vs `roll.economic_returns` **0.0e+00**
both roots; every roll info_cutoff < decision_date; roll.py unit tests (telescoping /
basis-invariance / causality) ALL PASS. The spec allows "es_1m → daily (or the ES daily
store)"; the **day store** was used for ES so both legs share the identical certified roll.
Merged axis: 4,270 shared sessions. All math in POINTS (DELEV01); gap-spanning returns nulled.

## 3. Results

Events: **298** (spec expected ~150–250 — modestly above; anomaly note §6). Split NEG **226** /
POS **72**; 159 clusters, max span 18 sessions (block length 60 spans it). Regime: NEG 3,315
days, POS 905 — POS concentrated 2021–2026 (2022: 53%, 2023: 66%, 2024: 63%, 2026: 87% of
defined days), exactly the inflation-regime shape the mechanism presumed.

2×2 (delta = event-cell mean − own-regime unconditional control; ZB points; CI = 95%
event-clustered block bootstrap; p_shift = one-sided shared-draw circular-shift null):

| h | cell | n | cell mean | uncond ctrl | delta | CI95 | p_shift | p_boot |
|---|------|---|-----------|-------------|-------|------|---------|--------|
| 1 | NEG | 224 | −0.1336 | +0.0160 | **−0.1497** | [−0.2771, −0.0195] | 0.9930 | 0.9905 |
| 1 | POS | 72 | +0.0247 | −0.0106 | +0.0353 | [−0.1887, +0.2622] | 0.3618 | 0.3553 |
| 1 | INTER | | | | −0.1849 | [−0.4449, +0.0725] | 0.9410 | 0.9135 |
| **3** | **NEG (primary)** | 221 | −0.1267 | +0.0402 | **−0.1669** | [−0.3949, +0.0516] | 0.9535 | 0.9300 |
| 3 | POS | 71 | +0.0216 | −0.0244 | +0.0459 | [−0.3512, +0.4852] | 0.4013 | 0.4098 |
| **3** | **INTER (primary)** | | | | **−0.2129** | [−0.6968, +0.2514] | 0.8251 | 0.8131 |
| 5 | NEG | 219 | −0.1200 | +0.0634 | −0.1834 | [−0.4859, +0.1070] | 0.9070 | 0.8886 |
| 5 | POS | 71 | −0.0308 | −0.0261 | −0.0047 | [−0.4656, +0.4978] | 0.4898 | 0.5002 |
| 5 | INTER | | | | −0.1788 | [−0.7530, +0.3663] | 0.7231 | 0.7361 |

**The mechanism is not just absent — the sign is inverted.** In the NEG-corr regime (bonds
nominally "the hedge"), ZB after an ES stress day **underperforms** its own-regime base rate at
every horizon; at h=1 the clustered CI **excludes zero on the wrong side** (−0.150 pts,
[−0.277, −0.020]; descriptive, secondary horizon, no multiplicity claim). The interaction is
negative at all horizons. The POS cell does not pay either (h3 +0.046, CI wide) — no
reclassification to unconditional FTQ. 2022 POS sub-cell (decisive modern cell): n=8, mean
−0.270 vs regime uncond −0.029 — stress days in the inflation regime saw ZB fall further, the
one cell that behaved as narrated, but the NEG side (the claim's payoff side) failed its half.

MDE (printed first, 80% power): NEG h3 0.31 pts (0.42 cluster-adjusted) — the run was powered
to see a delta of the size the mechanism needed; the observed delta is −0.17. This is a
**powered, identified inversion**, not an underpowered null.

## 4. Gate table (program-printed; full text in `out/gate_table.txt`)

| GATE | OBSERVED | PASS-FAIL |
|------|----------|-----------|
| G0a_SEAL | ES 2026-07-31, ZB 2026-07-31 | PASS |
| G0b_IDENTITY | ES 0.0e+00, ZB 0.0e+00 | PASS |
| G0c_ROLL_CAUSAL | ES True, ZB True | PASS |
| G0d_REGIME_LAG | independent recompute, max err 4.4e−16 | PASS |
| G0e_POINTS_ONLY | no % column formed | PASS |
| G1_MDE_first | printed first; 298 events (NEG 226 / POS 72) | PASS |
| G2_interaction | −0.2129 pts, CI [−0.6968, +0.2514] | **FAIL** |
| G3_neg_cell | −0.1669 pts, CI [−0.3949, +0.0516], p .95 | **FAIL** |
| G4_pos_cell_honesty | printed; POS +0.0459, does not pay | PASS |
| G5_cost | $35.61 / $66.86 RT; NEG h3 delta −$166.92/ct | PASS |
| G6_P_MEANING | p stated in words; second computation p_boot | PASS |
| G7_CLUSTER_SPAN | 159 clusters, max span 18 ≤ block 60 | PASS |

Decision rule (mechanical): G2 FAIL + G3 FAIL → **closed at scope**. No portfolio pre-read is
run (it was conditional on the positive branch).

## 5. §28 closure block

### Corr-regime-gated flight-to-quality (G00076, `G3_FTQGATE_20260906`)
```
Closed:  observable = ES + ZB causal-rolled daily point returns 2009-03..2026-07 (day store, identity-gated, 4,270 shared sessions)
representation = 2x2 {ES <= -1.5sigma stress day} x {trailing-60d ES-ZB corr sign through d-1} -> ZB fwd close-to-close points
event = ES daily stress day (298; NEG 226 / POS 72; 159 clusters)      horizon = 1-5 days      target = h3 NEG-cell delta vs own-regime uncond control > 0 AND interaction > 0
execution = screen-level cost only (ZB {1,2}-tick RT $35.61/$66.86)      sample = 2009..2026-07 DISCOVERY; powered (MDE_h3 0.31-0.42 pts vs |obs| 0.17)
reason = SIGN-INVERTED, powered: NEG-cell deltas NEGATIVE at all horizons (h3 -0.167 pts, p_shift .95/p_boot .93; h1 -0.150 with clustered CI [-0.277,-0.020] excluding 0 on the WRONG side); interaction negative everywhere (h3 -0.213); POS cell does not pay (+0.046, CI wide) so no unconditional-FTQ reclassification. Post-ES-stress ZB UNDERPERFORMS its own-regime base rate even when the trailing corr says bonds are the hedge.
```
Still open (adjacent): ZB post-stress beyond 5 days (never tested) · intraday/overnight FTQ
response paths (this was daily close-to-close only) · the ES–ZB corr-regime series as a
conditioning/risk input for OTHER engines (descriptive infrastructure, no engine claim tested;
`out/regime_series.csv` persists it) · the h1 anti-FTQ continuation observed here would be a
NEW preregistered object (opposite sign, different claim) — flagged, not opened. NOT closed by
this run: ZB rates-state work already closed separately (MC-57, powered NULL).

## 6. Anomalies

1. **Event count 298 vs spec expectation ~150–250.** G1's band was an expectation, not a bar
   (gate = "printed"); fat tails + clustering under a trailing sigma produce more exceedances
   than the Gaussian intuition. Recorded, not improvised around.
2. **REPORT.md (a spec-listed output) was refused by the write harness** ("subagents should
   return findings as text"). Not worked around; full report content returned in structured
   output for the orchestrator to place. All other spec outputs written in `out/`.
3. None else. ES source = day store is inside the spec's stated alternative and documented (§2).

## 7. Artifacts

`out/gate_table.txt` (program-printed gates + full tables) · `out/twobytwo.csv` ·
`out/regime_series.csv` · `out/verdicts.json` · `out/es_daily.parquet` / `out/zb_daily.parquet`
(+ `out/inputs_manifest.json`, sha256'd) · `src/build_daily_inputs.py` / `src/ftq_gate.py`
(seed 20260906; 2,000 shift draws, 2,000 block-bootstrap draws, block 60).