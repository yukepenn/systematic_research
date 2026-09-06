# G3_MEREBAL_20260906 — month-end stock-bond rebalancing flow + reversal (ES/ZB)

**Ledger G00077 · family GENESIS3_EVENT · executed 2026-09-06 · spec frozen before results (`spec.yaml`).**

## VERDICT: **FAIL — CLOSED AT SCOPE (§28)**

The preregistered conjunction (G4 = flow leg AND revert leg, both vs matched unconditional controls) failed — and not narrowly: **both legs came out wrong-signed relative to the mechanism's prediction.** Conditional on equities strongly outperforming bonds into month-end (top-tercile REL), the turn-of-month ZB-minus-ES spread was *more negative* than the generic turn (delta −0.318 vol-units, boot CI [−0.94, +0.25], one-sided p 0.81), and the post-turn window *failed to revert* (delta +0.468, boot CI [−0.50, +1.41], one-sided p 0.84). The shared-draw conjunction null puts the joint outcome at p 0.678. There is no rebalancing-flow signature here at any resolution this sample can see.

All validity gates passed; the outcome gates failed and are recorded failed.

## Construction (frozen object, implemented exactly)

- **Data**: ES + ZB per-contract NT8 day store → certified causal volume-crossover roll (`ncd_day.py` + `roll.py`), self-financing daily POINT returns, identity-gated against `roll.economic_returns` (max err 0.0e+00 both roots), roll causality asserted, seal asserted (max session 2026-07-31 both). ES 4,308 return-days, ZB 4,393; joint axis 4,270 sessions 2009-03-31 → 2026-07-31. Built independently of G3_FTQGATE from the same construction line.
- **Day labelling** (pinned by the spec's own parenthetical "T-3 (3rd-to-last trading day)"): T = first trading day of month m+1; T-3/T-2/T-1 = 3rd-to-last/2nd-to-last/last trading days of month m; T+1, T+5 = 2nd and 6th trading days of m+1. Every flow window = exactly 3 sessions (T-2 close → T+1 close), every revert window = exactly 4 (T+1 close → T+5 close); verified 170/170.
- **Signal**: REL_m = (ES MTD pts / σ_ES) − (ZB MTD pts / σ_ZB) through T-3 close; σ = trailing-60-joint-session sd of daily point returns through T-3 (spec silent on the σ window; 60 is the house standard — declared before results). Condition = REL_m > trailing-36-month upper-tercile bound (previous 36 finite-REL months, causal, excludes current).
- **Legs**: spread = ZB/σ_ZB − ES/σ_ES over each window (points-vol-scaled), expected + at the turn (flow) and − after (revert), both vs the matched unconditional control (all eligible turns, same windows).
- **Nulls/CIs**: shared-draw circular shift of the condition flag over the eligible-turn sequence (ONE offset per draw applied to BOTH legs — dependence-preserving); event-block bootstrap CIs (circular, block 6 turns, flag+outcomes resampled jointly); normal-approx CI printed as the second computation. Seed 20260906.

## Key numbers (all `DISCOVERY_CONSUMED`, in-sample; costs MODELED = commission + k-tick)

| | cond mean | uncond ctrl | delta | boot 95% CI | p₁ (shift) |
|---|---:|---:|---:|---:|---:|
| LEG-FLOW [T-2→T+1] | −0.4126 | −0.0943 | **−0.3184** | [−0.9395, +0.2491] | 0.8126 |
| LEG-REVERT [T+1→T+5] | −0.1502 | −0.6185 | **+0.4683** | [−0.5035, +1.4062] | 0.8351 |

- Sample: 205 candidate month-turns → 170 computed (35 integrity drops, ledger closes exactly) → **134 eligible** (trailing-36m tercile history) → **45 conditional events** (33.6%). Honest count below the spec's ~211/~70 estimate: the trailing-36m bound consumes the first 36 REL months and the day store starts 2009-03.
- G1 MDE (one-sided α=5%, 80% power): flow 0.827 vol-units (~$945/event at 1ES+1ZB), revert 1.160. **Power is moderate** — but the point is moot: both observed deltas are wrong-signed.
- Conjunction joint null p (shared draw, both legs at least as favorable): **0.678**.
- Dollar deltas at 1ES+1ZB: flow −$439/event, revert-trade −$228/event — negative BEFORE cost; cost band $52.47 (1-tick) / $96.22 (2-tick) per event per leg only deepens it.
- 3-era signs (G5): flow −/+/−, revert +/+/− — no era shows the predicted (+, −) pair.

## Banked either way: the generic turn-of-month control table (n=170, unconditional)

- Flow window [T-2→T+1]: spread +0.029 vol-u ≈ $6/event — **the generic ES/ZB turn-of-month spread effect is ~zero** in 2009–2026.
- Revert window [T+1→T+5]: spread −0.544 vol-u ≈ −$772/event, driven by **ES +8.85 pts** in the first 2–6 sessions of the month (ZB −0.33 pts). This is the familiar early-month equity drift sitting in the control — a *control-table fact*, not an edge claim (the calendar day-type family was already closed NULL at the family bar in GENESIS_H2; nothing here reopens it). Full table incl. per-era rows: `out/controls.csv`.

## Data facts recorded

- **ES day-store hole 2025-06-16 → 2025-08-31** (ZB complete there); 2025-07/08 have zero joint sessions. Turns near the hole were dropped by the integrity guards, not imputed.
- ES also missing 2026-06-09..12 → the 2026-06 turn dropped (mtd window unclean).
- Drop ledger: short_month 7, short_next 1, no_prev_month 1, mtd_unclean 14, sigma_nan 2, window_unclean 10 (= 35; 205 − 35 = 170 ✓).

## Gate table

Program-printed in `out/gate_table.txt` (GATE/SPEC/OBSERVED/PASS-FAIL): G0a–G0f, G1, G5–G8 PASS; **G2 FAIL, G3 FAIL, G4 FAIL**. Decision rule applied mechanically: G4 FAIL → closed at scope.

## §28 closure block

```
Closed:  observable = ES + ZB causal-roll daily point returns (NT8 day store, identity-gated), 2009-03..2026-07
representation = month-turn event study: top-tercile REL (ES-vs-ZB vol-scaled MTD through T-3, trailing-36m
  causal tercile) -> ZB-minus-ES points-vol-scaled spread over [T-2 close -> T+1 close] (flow) and
  [T+1 close -> T+5 close] (revert), BOTH vs matched unconditional month-turn controls
event = 45 top-tercile month-turns of 134 eligible (170 computed)      horizon = 3d flow + 4d revert
target = preregistered conjunction: flow delta > 0 AND revert delta < 0, CIs excluding 0
execution = screen-level cost only ({1,2}-tick + $4.36 commission, 2 RTs/event/leg, MODELED)
sample = 2012-12..2026-05 eligible turns (DISCOVERY_CONSUMED)
reason = BOTH legs wrong-signed vs prediction: flow delta -0.318 (CI [-0.94,+0.25], p1 .81), revert delta
  +0.468 (CI [-0.50,+1.41], p1 .84); conjunction joint null p .678; no era shows the (+,-) pair; dollar
  deltas negative before cost. The generic ES/ZB turn-of-month spread itself is ~zero (+$6/event, n=170).
```
Still open (adjacent): NOT closed by this run — month-end rebalancing expressed in OTHER pairs (e.g., ZN, international equity legs) or via order-flow/auction data (different observable); the early-month ES drift seen in the control window (a calendar family already closed as a standalone at GENESIS_H2 scope — reopening would need a NEW observable, not this one); quarter-end (vs month-end) mandates, never tested here. The banked unconditional ToM control table (`out/controls.csv`) prices any future calendar-turn card on this pair at ~$0.

## Outputs

- `out/gate_table.txt` — program-printed report + gate table
- `out/event_table.csv` — all 170 turns: anchors, REL, tercile bound, cond flag, both legs (vol-u and $), sigmas
- `out/controls.csv` — generic ToM table, all-turns / eligible / 3 eras
- `out/verdicts.json` — machine-readable verdict + gates
- `out/es_daily.parquet`, `out/zb_daily.parquet`, `out/inputs_manifest.json` (sha256, identity-gate, roll-ledger, seal evidence); `out/build_inputs_log.txt`

## Notes / anomalies (none improvised around)

1. Spec's T-labelling parenthetical pins T = first trading day of m+1; implemented as pinned.
2. σ window unspecified in spec → 60-session house standard declared in code header before results existed.
3. Eligible/event counts (134/45) honestly below spec estimate (~211/~70): trailing-36m burn-in + 2009-03 data start + 35 integrity drops.
4. Tercile bound uses the previous 36 finite-REL turn observations (≈ trailing 36 calendar months; slightly longer when a turn was dropped).
5. Gate-summary line relabelled (validity vs outcome gates separated) and the program re-run deterministically (same seed) after first execution; every number identical; the change is presentation-only, both executions verdict-identical (G2/G3/G4 FAIL).
6. ES day-store holes (2025 summer, 2026-06-09..12) recorded above — data availability facts, handled by preregistered integrity guards.
7. This REPORT.md was returned via structured output (harness refused the file write for subagents); orchestrator to place it at `runs/G3_MEREBAL_20260906/REPORT.md`.