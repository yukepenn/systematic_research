# Final system-design and decision package — NQ Solar Wave campaign

_2026-08-07 · All figures: NQ 09-26 back-adjusted, 3-minute, full history 2022-01-01 → 2026-07-31,
real NT8 slippage of 1 tick per execution, NinjaTrader Brokerage Lifetime commission, all-days
Sharpe on the **1,424-session NQ campaign calendar**. Every ensemble number produced by
`src/analytics/ensembles.py`; every candidate strategy gate-checked against the frozen canonical
baseline (2,915 trades / $146,440.60 / PF 1.132213) to the penny before its results were read._

> **Revised 2026-08-07 after a full integrity audit of the reports.** Sharpe figures below were
> previously quoted on a 1,370-session calendar while the accompanying `final_pareto.csv` had been
> computed on a 1,374-session one; all are now on a single 1,424-session basis (the union over
> every NQ family evaluated, fixed so that rejecting a candidate cannot move it). **Net, drawdown
> and worst-year figures are calendar-invariant and did not change. No ranking changed, and the
> recommendation is unaltered.** Audit trail: `research/CAMPAIGN_STATE.md` §13 and
> `reports/final_red_team.md` §2.

---

## 1. The one-paragraph answer

The vendor indicator was fully reverse-engineered and the campaign is completely vendor-independent.
The underlying edge is **real but very thin, and the historical record is too short to certify it**.
A directional-change filter on NQ closes does capture genuine trend persistence — the overshoot
ratio exceeds the martingale null at every threshold with t up to 31, and every candidate ensemble's
absolute edge has `P(Sharpe ≤ 0) ≤ 0.015`. But the edge is a ~3 % deviation from a no-alpha null,
the top 1 % of trades supply 160–250 % of net profit, **no individual parameter is selectable**
(PBO 0.48–0.90 with a negative in-sample→out-of-sample slope), **no refinement is statistically
separable from any other** on 4.6 years, and **the system does not transfer to ES**. The
recommended historical-research architecture is an unselected ensemble; the recommended posture is
that this is a candidate for further study, not a validated edge.

## 2. What was definitively achieved

**The indicator is 100 % recovered.** Every published series, every signal symbol, exact on every
bar: **2,035,869 bars** across 9 parameter configurations, zero mismatches. Type-2 alone: 45,825
events, 0 false positives, 0 false negatives. Recovered by behavioural observation of published
output only — no decryption, unpacking, patching or memory dumping; the vendor assembly is
unmodified and not redistributed. Reference implementation `src/analytics/solarwave.py`.

This is the only unambiguous, non-statistical result in the campaign, and it is what made
everything downstream possible: the open model can be modified along axes the vendor never exposed,
and all three signal types can be generated with zero vendor dependency.

## 3. Ranked Pareto set

No candidate dominates. All are ensembles; none is a single cell.

| candidate | net | Sharpe | max DD | Calmar | worst year | pos. years | P(Sharpe ≤ 0) |
|---|---|---|---|---|---|---|---|
| **R5** adaptive `S = k·σ`, 13 cells | $198,059 | **0.977** | −$39,126 | **0.896** | +$12,160 | 5/5 | **0.0020** |
| anchor: close-confirmed High/Low, 10 cells | $215,137 | 0.912 | −$47,698 | 0.798 | +$7,023 | 5/5 | 0.0102 |
| **R4** fixed, all 21 cells | $159,424 | 0.892 | **−$35,669** | 0.791 | +$2,583 | 5/5 | 0.0051 |
| ~~**C2** T1 core + one T3 re-entry, 8 cells~~ **REJECTED** | $233,628 | 0.850 | −$47,413 | 0.872 | +$19,801 | 5/5 | 0.0074 |
| R4b fixed plateau, 8 cells *(as first published)* | $180,479 | 0.773 | −$53,689 | 0.595 | +$7,796 | 5/5 | 0.0170 |

_The C2 row previously read $221,253 / 0.818. That was the one row in `final_pareto.csv` not
produced by `ensembles.py`: it used a skipna mean instead of the binding strict-1/N rule (flat days
as zero). Recomputed correctly it is $233,628 / 0.850 — **better** than published, and still
rejected, on its interaction test rather than its level._

**Recommended architecture: R5** — the volatility-normalised ensemble, **Type-1 signals only**.
Best Sharpe, best Calmar, best drawdown among the profitable set, strongest absolute-edge
significance, positive every year, and the only family whose *mechanism* was confirmed by a
preregistered control (§4).

**R5 stands unimproved.** C2 looked like the strongest available addition on a fixed core
(+29 % net, smaller drawdown, better worst year) — and then **failed its interaction test**: on the
adaptive core it costs 0.40 Sharpe, breaks the every-year-positive property, and worsens drawdown
(ΔSharpe −0.402, P(Δ ≤ 0) = 0.879). A sleeve whose sign flips when the core's threshold rule
changes is exploiting an interaction, not capturing an effect. It is rejected. Wave-index
conditioning, the last untested signal in the model, likewise produced nothing usable
(non-monotone, 0.54–0.93 across MinWave 1–8). **Every sleeve and conditioning axis is closed.**

Every one of these is quoted at one contract of average exposure. None should be scaled without the
tail analysis in §6.

## 4. What is actually established, and how strongly

| claim | evidence | strength |
|---|---|---|
| The indicator is exactly recovered | 1.4 M bars, 9 configs, zero mismatches | **certain** |
| NQ closes carry directional persistence beyond the null | overshoot ratio `r > 1` at every threshold, t = 31 → 2.1 | **strong** |
| Each ensemble's absolute edge ≠ 0 | block bootstrap P(Sharpe ≤ 0) = 0.003–0.015 | **strong** |
| The threshold mechanism is **volatility**-specific, not generic time-variation | volatility vs price normalisation, ΔSharpe +0.728, **p = 0.009** | **strong** |
| Parameter selection is impossible | PBO 0.48–0.90, negative IS→OOS slope at every block count; walk-forward argmax earned $16k where the median config earned $121k | **strong** |
| Ensembles beat their own members | beats 7/8 (fixed) and 88 % (adaptive) on Sharpe; positive every year when only 3/8 members are | **strong** |
| Adaptive beats fixed | ΔSharpe +0.087, P = 0.358 | **not established** |
| The Type-3 re-entry sleeve adds value | +$24.89/marginal trade over 19,606 trades, but session-block P(mean ≤ 0) = 0.115; loses $98k in 2022 | **not established** |
| The system travels to ES | ES ensemble Sharpe −0.329, P(Sharpe ≤ 0) = 0.829 | **refuted** |

## 5. What was killed, with evidence (none deleted)

| hypothesis | verdict | evidence |
|---|---|---|
| 16:30 timed exit dominates | **FALSE** on full history | wins 4/28 matched pairs, median −$12,476 |
| the 46 % untaken Type-1 signals are opportunity | **FALSE** | −$9.04 per marginal trade over 54,151 trades |
| H-011 stop-order execution recovers the 89 % friction | **FALSE** | negative in 10/10 cells, −$1.88 M |
| H-007 / DR03-H1 split exit ≠ reversal | **FALSE** | monotone degradation at both reversal distances |
| H-008 raw High/Low anchor | **FALSE** | Sharpe 0.527 — the ladder chases wicks |
| C4 adding Type-2 to the core | **FALSE** | −0.33 Sharpe vs the T1 core |
| C2 Type-3 re-entry sleeve as a general improvement | **FALSE** | works on a fixed core, costs 0.40 Sharpe on an adaptive one (P = 0.879) |
| wave-index conditioning | **FALSE** | non-monotone, 0.54–0.93 across MinWave 1–8; no usable signal |
| price-proportional threshold | **FALSE** | Sharpe 0.250; worse than a plain fixed tick count (p = 0.999) |
| DR06-H5 iid understates tail risk | **FALSE** | block/iid drawdown ratio 0.987 |
| original SW05 chop veto | **INVERTED** | would delete 74 % of profit |

Three of these — H-011, the raw High/Low anchor, and H-007 — failed for one shared reason worth
carrying forward: **the close basis is a noise filter, not a defect.** DC01 measured the close-basis
crossing excess at ~$117.57 per segment, 89 % of all friction and four times commission plus
slippage combined. Both routes to capturing it (intrabar execution, intrabar anchor) fail
catastrophically. The excess is what the filter costs, and it is not recoverable.

## 6. The risk disclosures that matter more than the returns

1. **The P&L is entirely right tail.** The top 1 % of trades contribute **160 % (adaptive) / 214 %
   (fixed)** of net profit — the bottom 99 % lose money in aggregate. The top 10 *days* carry 64 %
   of the adaptive ensemble's net. Any fill degradation, any filter, any profit target, any
   position cap that touches the right tail destroys the entire result. This is not a defect —
   DC01 predicted it from the exponential overshoot distribution — but it is the dominant risk.
2. **The short side has no standalone edge.** Excluding 2022 and 2025 it is net negative
   (−$8,397, Sharpe −0.113). The long side carries the system.
3. **The edge is thin by construction.** A ~3 % deviation of the overshoot ratio from its no-alpha
   value. There is no version of this system with a large margin of safety.
4. **Deflation cannot certify it.** Under the preregistered trial-accounting rule, DSR is 0.45–0.55
   for every candidate — far below the 0.90 bar — and the Harvey–Liu haircut Sharpe is 0.000. A
   defensible alternative variance pool gives 0.96. **The answer is dominated by a judgement call,
   not by the data**, which means deflation adjudicates nothing here in either direction.
5. **No clean historical out-of-sample window remains.** All data through 2026-07-31 was examined
   during discovery. **229 configurations consumed** on the preregistered rule-R1 basis (383
   counting every ledger including cost-stress re-runs) — counted from the committed evidence in
   `research/registry/tested_configs_backfill.csv`, not asserted.
6. **Waves 1c–3 were not preregistered.** The `runs/<run_id>/spec.yaml` convention lapsed after
   `RE01_open_parity`. Results are reproducible from ~296 committed ledgers, but there is no record
   proving pass/fail criteria were fixed before the numbers were seen. A reviewer should discount
   those waves accordingly. Full disclosure: `research/registry/REGISTRY_GAP_NOTE.md`.

## 7. Exact specification of the recommended architecture (R5)

```
Engine     : SolarWaveOpenV3, ThresholdMode = 1        (open model, zero vendor dependency)
Instrument : NQ 09-26 back-adjusted, 3-minute bars, Last
Core       : anchor = running extreme of the CLOSE since trend start
             flip when close STRICTLY breaks anchor -/+ S
             S = VolMult * sigma, sampled ONCE at trend birth, clamped [40, 1200] ticks
             sigma = causal mean |close - close[1]| over the trailing 460 bars
Entries    : Type-1 flips only (EntrySignalType = 1), long and short
Exits      : the trailing level, plus flat at session close
Ensemble   : equal risk across VolMult = 6, 8, 10, ..., 30 (13 members, 1/N each)
             DO NOT select a VolMult - PBO for that choice is 0.898
Costs      : $4.36/RT commission, 1 tick/execution slippage ($9.5352/RT realised on NQ)
Inert      : TrendMultiplier, SlowdownScan, WeakWeakSplit, PullbackSplit do not enter the
             Type-1 flip rule at all - this is derived, not merely measured
```

> **Corrected 2026-08-07.** This block previously named `SolarWaveOpenV4`. It was verified by
> re-running all 13 cells through V4 and comparing fill-by-fill: **V4 is not equivalent.** V4's
> `ResolveS()` snaps `S` to the tick grid; V3 does not. Every published R5 figure was measured on
> **V3**, so no number changes — but the spec was naming a strategy that had never been run.
> Full analysis: `research/10_v3v4_equivalence/V3_V4_EQUIVALENCE.md`.

Robustness already established for it: every σ-estimator lag from 0.13 to 7.96 sessions gives
Sharpe 0.769–1.494 with 11/13 cells positive in all five years (H-012), so the 460-bar choice is
not load-bearing.

**Threshold-discretisation robustness (new, 2026-08-07).** The V3/V4 check above doubles as a free
sensitivity test: V4 differs from V3 *only* by rounding `S` to the nearest tick (≤ half a tick,
$2.50 on NQ). Result: ΔSharpe +0.029 with paired block-bootstrap **P(Δ ≤ 0) = 0.247**, daily P&L
correlation 0.9949, and V4 has the *smaller* drawdown (−$36,275 vs −$39,126). **R5 is insensitive
to the discretisation.** Note the same test shows individual cells moving by up to 44 % (VolMult 6:
$166k vs $84k) — the ensemble is stable where its members are not, which is the campaign's central
finding, reproduced here by accident.

## 8. What would invalidate this system economically

Stated in advance so it cannot be rationalised later:

- **The right tail stops recurring.** If a 12-month period passes in which the top 1 % of trades no
  longer supply the bulk of profit while the bottom 99 % keep losing, the system is broken — this
  is the single most likely failure mode.
- **Execution degrades beyond ~2 ticks.** The slip-2 stress already halves net; slip-3 would erase
  it.
- **Volatility compresses persistently.** The edge lives at δ/σ ≈ 10–18 with a fixed dollar friction
  floor; a durable low-volatility regime pushes the system onto that floor (the ES failure is
  partly this mechanism).
- **Intraday persistence disappears** — the overshoot ratio `r` returning to 1.0 would remove the
  edge outright, and `r` is directly measurable each quarter at zero cost. **This is the single
  best early-warning statistic and it requires no trading to monitor.**

## 9. Honest limitations

- **No clean historical OOS remains.** Nothing in this package is out-of-sample.
- **Historical robustness does not imply future profitability.** Every result here is conditional
  on 4.6 years of one instrument in one macro regime (a bear year, two strong bull years, and a
  partial year).
- **The comparative claims are unresolved, not resolved in favour of the leaders.** R5 over R4, and
  C2 over C1, are both point-estimate improvements that fail their significance tests. They are
  ranked above the alternatives because point estimates plus a confirmed mechanism is the best
  available evidence — not because they were shown to be better.
- **ES portability failed.** Per the campaign constitution this earns a large overfitting penalty,
  and it is applied rather than explained away.
- **A second market, or genuinely forward data, is the only thing that can move this forward.**
  Resampling 4.6 years of NQ has been exhausted; every remaining question is now data-limited
  rather than method-limited.

## 10. Recommendation

**Do not treat this as a validated edge.** Treat it as a well-characterised candidate with a
confirmed mechanism, a fully open implementation, a known dominant risk (right-tail dependence),
and one failed external portability test.

If work continues, the highest-value next steps are, in order:

1. **Monitor the overshoot ratio `r` quarterly** — free, requires no trading, and is the system's
   own early-warning statistic.
2. **A third instrument** (RTY, YM, or CL) to convert the single ES failure into an actual
   portability distribution rather than one data point. This is now the highest-value empirical
   step, because portability is the only one of the three promotion criteria still open.
3. Complementary families (failed persistence per DR-05), which is the only route to a portfolio
   that does not simply hold more of the same factor.
4. Genuinely forward data after a strategy freeze. Every remaining question is data-limited rather
   than method-limited: resampling 4.6 years of NQ has been exhausted.

Items 2 and 3 from the earlier draft — re-testing C2 on an adaptive core, and wave-index
conditioning — have since been **run and both failed**; they are recorded in §5 rather than
carried forward.

Nothing here should be deployed. This campaign is historical research only, and its most defensible
output is the exact open model plus a clear-eyed account of how thin the edge is.
