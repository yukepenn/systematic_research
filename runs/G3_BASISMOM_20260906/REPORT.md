# G3_BASISMOM_20260906 — basis-momentum (Boons & Prado 2019) on {CL,GC,SI,ZN,ZB}

**Ledger G00075, family GENESIS3_RV. Preregistered 2026-09-06, executed 2026-09-06.**
**Verdict: G2 FAIL + G3 FAIL → CLOSED AT SCOPE (§28 block below). ARM-X returned EMPTY (0 months) and, per the frozen rule, could never have rescued ARM-W anyway.**

All numbers below are printed by the program (`out/gate_table.txt`, `out/verdicts.json`); none are hand-assembled. Evidence status: **DISCOVERY** (in-sample diagnostic on sealed pre-2026-08 data; nothing here is forward).

## 1. What was tested (frozen object, spec.yaml verbatim)

BM_i = cumret_12m(front-nearby) − cumret_12m(second-nearby), point-return basis, monthly end-of-month, causal-rolled.
**ARM-W (the claim):** within-root calendar spread — long front / short second (legs 1/σ63, lagged) where BM>0, reverse where BM<0, hold 1 month.
**ARM-X (secondary):** cross-sectional rank on BM, long top-2 / short bottom-2 outright; n=5 breadth flagged.

Series construction reused the certified transport and roll verbatim (`research/multi_market/src/ncd_day.py` + `roll.py`; roll.py's telescoping / basis-invariance / causality unit tests all pass in `out/build_log.txt`). The second-nearby leg is the CARRY_V1 deferred-leg convention (nearest later listed month vs the causal front, same self-financing `economic_returns`; asserted distinct from the front on every date, min gap CL 1mo / GC,SI 2mo / ZN,ZB 3mo).

## 2. Data-availability reality (the run's dominant fact — measured before any P&L)

The local NT8 day store holds the **full contract strip only for 2009–2015**. After 2015 the cache is front-only for CL (2016–2025: second-nearby unobservable) and patchy for GC/SI/ZN/ZB (near-full 2017/2020/2023, ~40–60% otherwise; 2016 is a hole for every root). Availability rule declared before results (s3): month VALID iff ≥14 joint both-leg sessions; cumret_12m requires 12 consecutive valid months.

Resulting live sample: **CL 67 / GC 68 / SI 72 / ZN 4 / ZB 5 root-months = 216 pooled; 80 portfolio months** (accrual 2010-04..2024-08, mass 2010–2015). **ZN and ZB are effectively untested** (their deferred quarterly contract has cached bars mostly near rolls only). **ARM-X never had ≥4 simultaneously-live roots → 0 months, EMPTY.**

**G1 MDE printed first: detectable annualized Sharpe = 1.08** at M=80. The test is powered only against implausibly large effects.

## 3. Results (PRIMARY = 1-tick/leg + $4.36 RT × 2 legs)

| quantity | value |
|---|---|
| ARM-W gross | $254 total, $3.18/mo, **gross annSharpe 0.215** |
| ARM-W net (1-tick) | $2 total, $0.03/mo, **annSharpe 0.002**, drag **99.1%** |
| net (2-tick) / (SI-3-tick) | −$199 (Sharpe −0.165) / −$289 (Sharpe −0.239) |
| Sharpe 95% CI (12-mo block bootstrap) | **[−0.630, +0.648]** — includes 0 |
| shift-null p (2000 shared-offset draws, seed 20260906) | **0.247** |
| BM terciles (fwd spread $/mo pooled) | T1 +0.76, T2 −6.84, T3 −1.55 — **NOT monotone** |
| subsumption alpha vs {static-basis, mom12} | +1.12 $/mo, NW CI [−11.74, +13.99] — **includes 0** |
| eras | 2009-15: + (n=67) · 2016-21: − (n=9) · 2022-26: − (n=4) |
| ARM-X | 0 live months (breadth never ≥4) — EMPTY |

Gate table: G0a–G1 PASS (seal 2026-07-31 max; certified roll; two-sided causality probe PASS ×5 roots); **G2a PASS (0.002>0, trivially), G2b FAIL, G2c FAIL, G2d FAIL → G2 FAIL; G3 FAIL**; G4/G5/G6 print-gates PASS. Full table: `out/gate_table.txt`.

The kill is **not cost-only**: gross Sharpe 0.215 with p≈0.25 against the dependence-preserving null, and the tercile response is non-monotone (mildly inverted if anything). Costs then erase even that: at 1-tick/leg the calendar-spread expression pays leg-level friction to hold a spread-sized return — drag 99.1% (a structural fact about two-leg execution at this signal strength). The frozen monthly-turnover cost model does NOT charge continuous-series roll executions (annex printed: CL≈11.5 front rolls/yr) — adding them would only deepen the failure.

## 4. §28 closure block

```
Closed:  observable = BM_i = cumret_12m(front-nearby) − cumret_12m(second-nearby), POINT-return
         basis, monthly end-of-month, causal volume-crossover roll + carry_v1 deferred-leg
         convention, universe {CL, GC, SI, ZN, ZB}
representation = ARM-W within-root calendar spread sign(BM), legs 1/σ63 lagged, hold 1 month;
         ARM-X rank top-2/bottom-2 outright (returned EMPTY, 0 months)
event = end-of-month rebalance      horizon = 1 month      target = after-cost Sharpe > 0 with
         CI/null clearance + positive alpha vs static-basis and 12m-outright-momentum parents
execution = MODELED $4.36 RT × 2 legs + {1,2}-tick per leg (SI 3-tick rung), monthly turnover
sample = availability-collapsed: 216 root-months (CL 67 / GC 68 / SI 72 / ZN 4 / ZB 5),
         80 portfolio months, accrual 2010-04..2024-08, mass 2010-2015; MDE annSharpe 1.08
reason = gross edge indistinguishable from zero (annSharpe 0.215, shift-null p 0.247, terciles
         NOT monotone: +0.76/−6.84/−1.55); after 1-tick costs Sharpe 0.002 with drag 99.1%;
         subsumption alpha CI [−11.7, +14.0] includes 0. G2 FAIL, G3 FAIL → closed at scope.
```

**Still open (adjacent), NOT closed by this run:** (1) basis-momentum on a **full-strip data surface** — the 2016–2025 window was largely unobservable here and ZN/ZB were never really tested (4–5 root-months); a Databento-class purchase (owner-gated, already a standing fork) would re-open the object at real power. (2) ARM-X cross-sectional expression — returned empty, uninformative. (3) Percent-return BM (the original paper's construction) — this run tested the point-basis variant the spec froze. None of these may be run without a new preregistered spec.

## 5. Anomalies / spec-reality conflicts recorded

1. **Spec data clause "2009..2026-07" is not satisfiable from the local day store** for the second-nearby leg (full strip cached 2009–2015 only; CL front-only 2016–2025; 2016 hole for all roots). Availability rule (≥14 joint days/month, 12 consecutive valid months) declared before any P&L; sample moved for DATA AVAILABILITY, never for returns.
2. **ZN/ZB effectively untested** (deferred quarterly leg has bars only near rolls in this store): 4 and 5 live root-months respectively.
3. **ARM-X is EMPTY** (never ≥4 simultaneously live roots) — reported, flagged, and by frozen rule irrelevant to the decision.
4. Spec's G1 note "~200 root-months per arm" — actual 216 pooled root-months / 80 portfolio months; MDE printed first as required.
5. "Shared draw with G3_ZNZB_SLOPE": that run has not executed yet; the shared-draw contract is honored by fixed seed 20260906 and `out/null_offsets.csv` (2000 offsets) for it to consume.
6. BM cross-root ranks (ARM-X) compare POINT scales across roots — frozen wording implemented verbatim and flagged; moot given the empty arm.
7. REPORT.md (a spec-listed output) could not be written: the harness refused report-file writes; this document is returned in structured output instead, per instruction (no workaround attempted).

## 6. Files

- `spec.yaml` (preregistered, committed before results)
- `src/build_series.py`, `src/basismom.py`
- `out/build_log.txt`, `out/build_manifest.json`, `out/legs_{CL,GC,SI,ZN,ZB}.parquet`
- `out/gate_table.txt` (program-printed GATE/SPEC/OBSERVED/PASS-FAIL), `out/verdicts.json`
- `out/bm_signals.csv` (225 root-month signals), `out/armW_pnl.csv`, `out/armX_pnl.csv` (empty arm), `out/subsumption.csv`, `out/null_offsets.csv`