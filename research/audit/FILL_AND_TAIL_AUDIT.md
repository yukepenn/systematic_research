# Fill and tail-day audit — POST_CAMPAIGN_AUDIT_01, AUDIT-A07/A08/A09/A10

_2026-08-07 · runs `AUDIT05_V3_SLIP2` (13 cells), `AUDIT05_V3_HIGHRES`
(cells vm6/vm18/vm30), all preregistered at `2a125a4` before execution._

## 1. Two-tick stress (AUDIT-A09) — the "halves net" claim is falsified upward

Slippage 2 ticks/execution, all 13 R5 members, identical engine/data:

- **Trade paths identical to slip-1** in all 13 cells (TradesCount unchanged —
  preregistered pass criterion; slippage cannot alter paths, only prices).
- Strict-1/N ensemble net: **$173,084 vs $198,059 = 87.4% retained.**
- Per-cell retention is turnover-driven: vm6 51.6% → vm30 96.6%.
- Claim correction, precisely scoped (second red team): the measured source of the
  "slip-2 halves" language is WAVE1C (3-minute plateau cells at high turnover — the
  audit's own vm6 result, 51.6% retention, partially supports it there), and the
  1-minute robustness table showed 63–78% retention, never halving. What this
  measurement **falsifies is the unmeasured extension of that language to R5** in
  the final design package: R5 retains 87.4%. Implied marginal cost ≈ $25.0k per
  extra tick per execution on the ensemble; linear extrapolation puts slip-3
  retention near 75%, and the NT8 bar-range slippage cap binds more often at
  larger slippage, making that extrapolation a floor — "slip-3 erases the edge"
  is likewise wrong for R5.
- Full table: `runs/AUDIT05_V3_SLIP2/sweep_summary.json`.

## 2. Standard vs High Order Fill Resolution (AUDIT-A07/A08)

Preregistered expectation: identical fills (market-on-next-open orders only).
Measured on vm6 / vm18 / vm30 over 2022-01→2026-07:

| cell | fills | differing prices | of which 1-tick | net effect (High − Std) |
|---|---:|---:|---:|---:|
| vm6 | 16,984 | 363 (2.1%) | 362 | **+$1,910** (+1.1% of net) |
| vm18 | 3,360 | 46 (1.4%) | 46 | **+$230** (+0.09%) |
| vm30 | 1,786 | 9 (0.5%) | 8 | **−$185** (−0.07%) |

- Order/action/commission **sequences are identical** — same trades, same paths.
- The 1-tick differences are the slippage cap evaluated on the finer 1-minute
  sub-bars (narrower ranges cap the modeled slippage slightly more often, usually
  in High's favor). Zero differences on session-close fills.
- Two isolated >1-tick fills in 22,130 audited (one −5.00 pts favorable 2022-06-09
  03:14 ET, one +11.25 pts adverse 2024-07-25 10:51 ET) — sub-series alignment gaps
  in thin minutes, one each direction.
- **Verdict: expectation confirmed economically.** Net effects ≤1.1% with both
  signs; Standard is a fair and on-balance slightly conservative assumption.
  **The edge is not a fill-resolution artifact.**

## 3. Tail-day inspection (AUDIT-A10)

R5 E0 (session TRUE_MTM) extreme days, cross-referenced against every
fill-resolution difference found in the three audited cells:

- Top-10 days (+$9.8k…+$16.3k each): only **2 of 10** sessions contain any
  differing fill, each difference exactly one tick ($5/contract) — noise relative
  to five-figure day P&L. **Top-day P&L does not depend on fill modeling.**
- Worst-10 days: 3 of 10 touched, same triviality.
- The 328 sessions containing any difference are scattered across the sample, not
  clustered on tail days or roll weeks.
- Same-instant exit+reversal events: **18 of 34,148 entries (0.05%)** across the 13
  members; sequences identical under both fill models — no same-bar ambiguity
  affecting results.
- Top-10 day identity note: 8 of the top 10 and 7 of the worst 10 fall in 2025–26,
  consistent with the right-tail concentration disclosures (§26 monitoring).

## 4. Standing limits of this audit

- High resolution was run on 3 of 13 cells (32% of member-fills volume — 22,130 of
  68,296 fills — spanning the narrowest/middle/widest thresholds); the mechanism
  (slip-cap on sub-bars) is structural and cell-independent.
- Playback parity was not run: with fills stamped identical in sequence and price
  to within a tick under both resolutions, and market-orders-only execution, the
  incremental information of Playback is judged nil for this order type. Recorded
  as an explicit non-run.
- Live slippage remains an assumption (1 tick/execution base, 2-tick stress);
  external evidence (`research/01_diagnostics/external_review.md`) measures retail
  NQ at 0.7–1.2 ticks RTH.
