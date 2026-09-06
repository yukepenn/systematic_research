# G3_ZNZB_SLOPE_20260906 — REPORT

**Verdict: CLOSED AT SCOPE (ledger G00074: FAIL).** The preregistered decision rule
(`G2+G3 PASS -> ZNZB_RV01 ENGINE CANDIDATE; either fails -> closed`) fired on its negative
branch: **G2 failed all three clauses and G3 failed with a significantly NEGATIVE alpha.**

Evidence status: **DISCOVERY** (window 2009-01-01 → 2026-07-31 per frozen spec; the
2026-06/07 segment lies inside the globally BURNED window and carries no forward claim).
Costs MODELED ($4.36 RT + 1-tick primary / 2-tick stress per leg). Research sizing.
Seal asserted by the program: max session 2026-07-31 < 2026-08-01.

## What was tested (frozen object, zero free parameters)

Weekly ISO rebalance, decision = last observation strictly before the week's first trading
day. `carry_i = (P_near − P_deferred)/month_gap / sigma_i` for i ∈ {ZN, ZB} — the CARRY_V1
construction **verbatim** (module = `carry_v1.py` + exactly two mechanical changes, enforced
by an in-program diff audit: load range 2009–2027, window 2009-01-01/2026-08-01). LONG the
carry-richer root, SHORT the other, legs 1/sigma_i (points-vol-neutral proxy for
DV01-neutral, named not hidden). Always in; sign = carry ordering. Certified causal roll
(s6/s7 unit tests re-run in-program; two-sided causality probe PASS both clauses).

## Headline numbers [DISCOVERY, MODELED costs]

| quantity | value |
|---|---|
| N (ISO weeks with P&L) | **596** (spec anticipated ~910 — see anomaly A1) |
| MDE, printed before observed | $71/week (≈ ann Sharpe 0.83 at 80% power) |
| after-cost weekly mean (PRIMARY) | **−$41.79** |
| total net / gross / cost | **−$24,905** / **−$9,476** / $15,429 |
| ann Sharpe (weekly basis) | **−0.487** |
| STRESS (2-tick) weekly mean | −$63.08 |
| 95% block-bootstrap CI of weekly mean | [−$82.28, −$0.44] (13-wk blocks, seed 20260906) |
| circular-shift null percentile | **20.5** (595 offsets, bar ≥ 95) |
| G3 alpha vs both outright-carry controls | **−$46.64/wk**, CI [−$84.14, −$3.43] (seed 20260907) |
| era signs 2009-15 / 2016-21 / 2022-26 | **− / − / −** (−$7.2k / −$8.8k / −$8.9k) |
| beta-stability audit | 4.5% alt-sigma ordering flips (flag bar 20%) — NOT sigma-driven |
| weekly turnover / weekly cost | 1.054 dUnits / $25.89 (1-tick) $47.18 (2-tick) |

The gate table printed by the program is in `out/gate_table.txt`; full console in
`out/znzb_console.txt`; weekly P&L in `out/weekly_pnl.csv`; controls in
`out/outright_control.csv`; machine verdict in `out/znzb_verdict.json`.

## Why it died (mechanism autopsy, honest)

1. **The mechanism claim fails at the sign level, before costs.** Gross is −$9,476 over 17
   years. "Slope position toward the carry-richer leg earns roll-down without outright
   duration risk" is refuted at this scope — there is no roll-down harvest in the
   duration-neutral direction on this pair at weekly horizon.
2. **The RV transform DESTROYS value that the outright legs contain.** Both single-root
   carry-timing controls (identical machinery, sign of OWN carry, always in) are positive —
   ZN +$47.7k (Sharpe 0.61), ZB +$58.7k (Sharpe 0.70) — while the pair RV object is
   −$24.9k, and its alpha against the two controls is **significantly negative**
   (CI entirely below 0). The spec's close condition was "alpha CI includes 0"; the observed
   outcome is strictly worse. Whatever information ZN/ZB calendar slopes carry is the
   **level/direction component the neutralization subtracts**, not the relative component
   this object keeps.
3. **Not a construction artifact of the sigma choice:** the 52-week alternative-sigma audit
   flips the carry ordering in only 4.5% of weeks (bar 20%) — the ordering is slope-driven,
   and it still loses.
4. **Uniform across regimes:** all three era signs negative (2009-15 bond bull, 2016-21
   mixed, 2022-26 bear/chop). No old-regime/new-regime classification question arises.

## Anomalies (recorded, not improvised around)

- **A1 — sample size below spec estimate.** The spec anticipated "~910 weeks"; the realized
  panel has 596 P&L weeks (66.9% of calendar weeks spanned), with holes concentrated in
  specific years (2016: 3 weeks; 2022: 14; 2019: 15; 2025: 16). Cause: deferred-leg bar
  availability in the local per-contract .ncd store — the same partial-pairing property
  CARRY00 measured (GC 0.734 / SI 0.781 paired fractions). This spec preregistered **no
  coverage INVALID-RUN clause** (unlike CARRY_SIGC_CONFIRM), so the run stands, with MDE
  printed from realized N ($71/wk vs ~$57/wk at 910). The verdict does not hinge on the
  missing weeks: four independent failures (gross sign, mean sign, null percentile, negative
  alpha CI) would all have to reverse.
- **A2 — cost/gross ratio is meaningless here** (162.8% of |gross| with gross near zero and
  negative); dollar drag is the honest figure and is printed ($25.89/wk primary, $47.18
  stress).
- **A3 — probability-event discipline:** the null percentile's event is stated in words in
  the console and its "distinguishable from zero" claim is computed a second, different way
  (block-bootstrap CI). Both agree: the observed mean is on the WRONG side.

## §28 closure block

### ZN/ZB duration-neutral slope-carry RV (G00074, `G3_ZNZB_SLOPE_20260906`)
```
Closed:  observable = ZN + ZB per-contract dailies (local .ncd, certified causal roll), calendar-spread
  slope carry_i = (P_near - P_deferred)/gap / sigma_63d, CARRY_V1 construction verbatim (diff-audited)
representation = weekly duration-neutral pair RV: LONG carry-richer root / SHORT other, legs 1/sigma_i,
  always in, zero free parameters
event = weekly carry-ordering decision      horizon = weekly rebalance      target = after-cost weekly mean > 0,
  CI excl. 0, shift-null 5%, positive alpha vs BOTH single-root carry-timing controls
execution = MODELED $4.36 RT + {1,2}-tick both legs      sample = 596 ISO weeks 2009-06..2026-07 (67% coverage,
  DISCOVERY; 2026-06/07 segment BURNED-window, no forward claim)
reason = gross-negative (-$9,476 before costs; net -$24,905, Sharpe -0.487); all three era signs negative;
  shift-null pctl 20.5 (bar 95); alpha vs outright-carry controls SIGNIFICANTLY NEGATIVE (-$46.64/wk,
  CI [-84.14, -3.43]) — the duration-neutralization subtracts exactly the component that pays; ordering
  not sigma-driven (4.5% alt-sigma flips). Preferred-habitat roll-down does NOT exist duration-neutral
  at weekly horizon on this pair.
```
Adjacent questions still open (genuinely different observables): **outright rates
carry-timing** — both single-root controls were positive (ZN Sharpe 0.61, ZB 0.70,
identical machinery) — but that is a DIRECTIONAL duration object observed in an
unregistered control (selection caveat; mostly-long through a 13-year bond bull), sits on
the exhausted-for-now directional frontier, and would need its own preregistration + bar;
ZN/ZB at horizons other than weekly with a different mechanism story; ZBMACRO01's event
lane (G00072, unaffected). NOT reopened by this closure: anything about the CARRY_V1 family
verdicts or the SIGC G00070 closure.

## Ledger

G00074, family GENESIS3_RV: **FAIL** (registered before outcomes; recorded failed).
Seeds recorded for shared draws with G3_BASISMOM (G00075): shift null deterministic
all-offsets; block bootstrap 13-week blocks, seeds 20260906 (mean CI) / 20260907 (alpha CI).