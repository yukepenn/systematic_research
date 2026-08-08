# Statistical Red Team — SMV2S_ONELOT_F2 (mandatory pass, V4 §48)

Date: 2026-08-08. Reviewer: independent red-team agent (separate session from executor).
Scope: HTF-GATED DOMINANT one-lot family #2, seq 386-388. Verdict below.

## VERDICT: CONFIRMED

All three gate FAILs and the mechanical KILL decision are correct, letter-exact to the
frozen spec, and every recomputed load-bearing number matches (39/39 independent checks,
several bit-exact).

## 1. Spec letter-exactness — PASS

- spec.yaml frozen in commit 58dc2d2 (2026-08-08 13:14:29) BEFORE any result was produced
  (out/ artifacts timestamped 13:20-13:21). Working-tree spec.yaml is byte-identical to the
  committed version (`git diff 58dc2d2` empty).
- Cells: exactly thr in {3,5,7} = seq 386/387/388, center thr5. cells.csv contains only
  355 (ref) + 386/387/388; gate_A.csv and gate_B_retention.csv only 386/387/388. No extra
  cells, no post-hoc selection anywhere.
- Policy implemented exactly as spec pseudo-code: `pol_htf_dominant` = B priority, Solar
  leg iff |T_dd| >= thr AND HTF_state == sign(T_dd); NaN/0 HTF blocks the Solar leg
  (correct side-blind gate semantics — NaN != sign comparison is False).
- Gate A: block=5, B=10000, seed=20260808, house circular index construction — verified
  character-identical to SMV2H2 confirm_gate_a.py (same seed/construction, so P-values are
  cross-wave comparable as claimed). Center bar 0.85 both metrics both instruments;
  neighbors point-positive: exactly as frozen.
- Gate B: hard 0.90 evaluated on center. Spec sentence does not name the cell; note that
  thr3 (0.855) and thr7 (0.820) are also < 0.90, so the FAIL is invariant under every
  possible reading. Not outcome-affecting.
- Gate C: net >= SM14-$10k (NQ costs $2.18/side, PV $20 — correct), maxDD <= 1.25x,
  "trades/yr <= 1.5x" tested as BOTH entries/yr and fills/yr (stricter-or-equal
  interpretation, both pass, disclosed). Solar-only degeneration and SM14 reference
  (hysteresis 3/1 on 0.7086*Tp_old, B silent) match spec.
- Executor "verbatim" claims verified against committed sources: run_policy functionally
  identical to smv2h.py (F2 copy drops only a dead `pend=` line upstream immediately
  overwrote); pol_hyst, state coefficients (0.9026, 0.7086, 2.83, 1.25 agree-boost,
  0.5 short-halving, clip +-13, SMA50.shift(1) HTF) and run_policy_hist all
  character-identical to smv2h.py / confirm_gate_b.py.
- Reconciliation regenerated 3 extra previously-tested cells (350/351/357) beyond the
  required SM14 — reconciliation evidence on already-registered configs, not new cells.
- Registry: no pre-existing rows for seq 386-388 (no collision); registry update correctly
  left to orchestrator.

## 2. Independent recomputation — PASS (39/39)

Own code, from out/ artifacts (scratchpad script, not the executor's):

| Quantity | Reported | Recomputed | Match |
|---|---|---|---|
| SM14 recon max abs daily diff (355 MNQ/NQ vs SMV2H2 regen, round_trip) | 0.0 | 0.0 | bit-exact |
| Gate A P(dSharpe>0) 387 MNQ / NQ | 0.6406 / 0.6361 | 0.6406 / 0.6361 | bit-exact (own bootstrap impl) |
| Gate A P(dCDaR>0) 387 MNQ / NQ | 0.4860 / 0.4799 | 0.4860 / 0.4799 | bit-exact |
| 90% band dSharpe MNQ | [-0.417, +0.647] | [-0.4173, +0.6472] | OK |
| Gate B retention 387 MNQ / NQ | 0.8412354... / 0.8415125... | same | bit-exact |
| Biggest miss day | 2024-08-08, +$1,157.70 vs -$211.60 | same | OK |
| Gate C net s5 / SM14 / gap | $10,815.84 / $46,866.36 / -$36,050.52 | same | OK (<1e-7) |
| maxDD ratio | 0.5538204134707948 | same | bit-exact |
| 2021 delta / ex-2021 | -$55,702.84 / +$19,652.32 ahead | same | OK |
| thr3 net / gap, thr7 net | $35,928.16 / -$10,938.20, $11,957.36 | same | OK |
| Kill screen (no year < -$25k, any policy) | holds | worst: SM14 2009 -$14,661 | OK |
| Cell battery 387/355 (net, Sharpe, maxDD, CDaR, pt deltas) | cells.csv | matches | OK |
| vote->T_dd rebuild vs stored tdd_dev_from_tgt.npy | 0 mismatches / 519,714 | 0 mismatches | bit-exact |

Gate P-values reproduced bit-exactly by an independently written bootstrap using only the
published (seed, block, B, construction) — the strongest possible reproduction.

## 3. Lookahead / leakage scan — CLEAN

- Dev prefix: sess_date <= 2026-05-31 masked immediately after load with a prefix
  assertion in BOTH scripts; dev curves end 2026-05-29 (verified from artifact). No data
  >= 2026-08-01 anywhere in scope (bar CSV ends 2026-07; June/July excluded before use).
- Hist substrate: max sess_date asserted <= 2021-12-31 (verified: curves end 2021-12-31).
- Causality: HTF = prior-session close vs SMA50, shift(1) — no same-session info. B-MOM
  bands use prior-day history only (appended after each day's decision loop, BAND_DAYS
  burn-in enforced). desired[t] decided at bar t fills at bar t+1 open (dev, capped 1-tick
  slip) / t+1 close +-1 tick (hist, disclosed approximation, identical for both policies).
  Session-close flatten and 16:30-18:03 ops freeze verbatim.
- No full-sample scaling: all coefficients are frozen constants from the committed SM
  lineage; nothing fit on the dev or hist windows in this run.
- Writes confined to runs/SMV2S_ONELOT_F2/; no git mutations by executor (spec-freeze
  commit predates execution); no NT8/order-side tools.

## 4. Report language — HONEST

- FACT / INFERENCE / HYPOTHESIS labels used correctly; the mechanism hypothesis for the
  next wave is explicitly labeled HYPOTHESIS and "not tested here".
- The kill is recorded prominently and mechanically ("FAMILY KILLED — all three
  preregistered gates fail"), including the honest observation that the family is
  pointwise BETTER on dev everywhere yet not certifiable — no attempt to spin the kill.
- Second-consecutive-kill pause clause invoked correctly (SMV2H2 A-dominant
  CONFIRMATION-FAILED is named as kill #1 in the frozen spec's own parent line).
- No BLOCKED items claimed. Round-trip float parsing disclosure is accurate (verified:
  default parser noise is real; round_trip comparison is bit-exact).

## 5. Policy/adoption language — N/A / CLEAN

This is a preregistered gated family test, not a diagnostic track; decision language is
the spec's own mechanical rule. No new policy adopted: SM14-form correctly retained as
ONE_CONTRACT_FINAL. Next-wave constraint (no consensus-threshold or HTF-gate variants)
is quoted from the frozen spec, not invented post-hoc.

## Minor observations (none affect the verdict)

1. Gate B spec sentence is cell-silent; executor applied it to the center cell (mirroring
   SMV2H2 convention) — outcome identical under any reading since all three cells < 0.90.
2. "trades/yr" in gate C read as entries/yr AND fills/yr (both) — stricter-or-equal,
   disclosed, both pass, so not outcome-affecting.
3. REPORT.md's gate C table lists maxDD/entry/fill criteria as PASS — correct, and the
   composite FAIL on c1 alone is correctly propagated to the family kill.
