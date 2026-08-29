# GENESIS_H1_VOLSTATE — RESULT: **NULL (F1·F2·F3 all FAIL; F4 never read)**

Executes `spec.yaml` (committed `b1bf75c` before results). Trial `G00010`. Program-printed gate
table in `out/gate_table.txt`; all 16 ambiguity resolutions frozen pre-computation in
`out/spec_resolutions.txt`.

## Verdict

> **The VX front-month basis state does not predict the next NQ session's return, 2007–2021 —
> and the point estimate is the WRONG SIGN vs the preregistered hypothesis.**
> T3−T1 (contango-minus-backwardation) = **−0.0372%/session, clustered t −1.42** (gate: ≥ +2.0);
> halves disagree; RV-matched contrast −0.0369% (t −1.40); null percentile **11.3%** of 300
> dependence-preserving shifts. Backwardation/stress sessions had *higher* next-session means.

- **F4 was NOT read.** The 2022+ modern parquet was never opened by this family; the confirmation
  window is preserved. The independent implementation was deliberately not written (spec order).
- Secondary non-gate states point the same wrong way (VXN/VIX −0.0554%, t −1.87; VIX3M/VIX
  −0.0216%) — the whole free vol-state family is coherent in its unhelpfulness at this horizon.
- Diagnostic, non-gate, non-lead: a k=1 circular probe (+0.296%) shows the curve state co-moves
  with the session **just ended** — contemporaneous description, not prediction. Recorded so
  nobody rediscovers it as alpha.

## Closure scope (exact, per charter §3)

CLOSED: *daily VX basis / VXN ratio / VIX3M ratio terciles → next-session NQ close-to-close
return, 2007–2021, trailing-252 causal terciles.* NOT closed: intraday vol-state horizons,
vol-state as a **risk-sizing** input (a RISK SPECIFICATION question, not information alpha), and
any use on forward data. Ceiling was DISCOVERY-GRADE; outcome NULL at that ceiling.

## Process integrity

R4→R4b expiry-rule amendment made at the **data-identity layer only**, before any state-return
statistic existed (v1 failure preserved in `out/gate_table_r4v1_fail.txt`; amended rule validates
163/163 modern contracts exactly). 10 seal assertions, zero errors; deep stream cut at 2021-12-31.
No search, no git, no CrossTrade. **`LIVE ENABLED = NO` · $0.**
