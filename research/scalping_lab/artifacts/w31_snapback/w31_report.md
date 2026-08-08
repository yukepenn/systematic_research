# W3-1 SNAPBACK rule family — READOUT: REJECTED at Tier-0 (2026-08-08)

Spec: `specs/W3-1_snapback_rule.md` (frozen 1b3837d before readout). DoF charged: 8.
Data: 37 L2 discovery sessions, sequential episode simulation, sechilo 1s hi/lo.
Table: `w31_results.csv`; full stdout `w31_stdout.txt`. Registry S8.

## FACT — all 8 primary configs (and all 16 frozen neighbors) fail at C1

Net ticks/trade after C1, day-clustered 95% CI (delay=0; primary D=12 marked):

| k | dir | bracket | epi/day | P(tgt) | BE_C1 | net C1 [CI] | net C2 |
|---|---|---|---|---|---|---|---|
| 10 | long | +24/−8 | 351 | 0.254 | 0.340 | −2.73 [−3.04,−2.42] | −4.73 |
| 10 | long | +32/−10 | 320 | 0.241 | 0.307 | −2.73 [−3.16,−2.28] | −4.73 |
| 10 | short | +24/−8 | 354 | 0.250 | 0.340 | −2.87 [−3.12,−2.64] | −4.87 |
| 10 | short | +32/−10 | 323 | 0.241 | 0.307 | −2.72 [−3.03,−2.43] | −4.72 |
| 30 | long | +24/−8 | 321 | 0.262 | 0.340 | −2.49 [−2.79,−2.20] | −4.49 |
| 30 | long | +32/−10 | 294 | 0.251 | 0.307 | −2.31 [−2.59,−2.00] | −4.31 |
| 30 | short | +24/−8 | 328 | 0.258 | 0.340 | −2.60 [−2.84,−2.33] | −4.60 |
| 30 | short | +32/−10 | 300 | 0.252 | 0.307 | −2.26 [−2.60,−1.96] | −4.26 |

D∈{8,16} neighbors: −2.35 to −2.86 — a coherent NEGATIVE plateau (no fragile isolated
positives). 1s-delay entries: −2.32 to −2.90 (latency changes nothing). Spread≤2
diagnostic split: ±0.1–0.2t (nothing). Verdict per frozen rules: **REJECTED at Tier-0.**

## FACT — the conditional lift is real but an order of magnitude too small

vs the unconditional excursion surface (census, same clock/machinery):

| bracket | uncond P(tgt) | snapback best (k=30,D=12) | lift | needed lift (BE gap) |
|---|---|---|---|---|
| +24/−8 | 0.249–0.253 | 0.258–0.262 | **+0.9–1.0pp** | 8.7–9.1pp |
| +32/−10 | 0.233–0.236 | 0.251–0.252 | **+1.5–1.9pp** | 7.0–7.4pp |

The census precursor separation (P(precursor|move), effect ~0.5) inverts to only
+1–2pp of P(move|precursor). Reasons visible in the data: the trigger fires ~300–400
episodes/day in this high-vol sample — a 12t/10–30s counter-move is a near-permanent
state, not a rare setup, so conditioning adds little; and MAE symmetry means the fade
entry eats the same amplitude it seeks.

## INFERENCE — measured signal-magnitude ladder for fast NQ states (all our own data)

- unconditional micro momentum vs matched null: +0.2–0.6pp (W2-0)
- single contrarian fast trigger: +1–2pp (this study)
- required at 24–32t brackets under C1: **+7–10pp**

One-feature fast triggers are an order of magnitude short. Consistent with Amendment 4
§4: the viable architecture (if any) is STRUCTURAL OPPORTUNITY + CONDITIONAL STATE +
PRECISE TIMING. This RAISES the EVI of completed-structure setups (FSS-1/2/5 with real
level logic, S2a) and cross-market state (FSS-10/ES) relative to more fast-trigger
variants, which are hereby deprioritized.

## Closure

- REJECTED_IDEAS entry added: snapback-single-trigger (k∈{10,30}, D∈{8,12,16},
  24/8 & 32/10) may not be retried without a mechanically different construction
  (e.g., structure-anchored sweep/reclaim rather than raw return trigger).
- The +1–2pp contrarian lift is recorded as a REFERENCE FACT (role-B candidate: as a
  selectivity/veto feature it may still add value on top of a structural setup).
- No re-tuning; no additional brackets; discovery subset only.
