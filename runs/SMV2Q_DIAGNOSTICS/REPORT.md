# SMV2Q_DIAGNOSTICS — REPORT (seq 380)

Class: DIAGNOSTIC — pure measurement. No gates, no selection, no tuning.
Dev window: sessions 2022-01-03 .. 2026-05-29 (<= 2026-05-31), 1,139 sessions.
June–July 2026 values appear ONLY in the recency section, labeled CONSUMED, only for the
executable master, read from already-committed artifacts. No data >= 2026-08-01 touched.
Executors: `smv2q.py`, `q_addendum.py` (this run dir). Every number below is in `out/`.

## Curves and reproduction checks (FACT — out/crosschecks.csv)
| curve | source | unit basis |
|---|---|---|
| SOLAR_E10 | SM01 e10_daily_py.csv | MNQ exec $, up to 10 MNQ |
| SOLAR_DUAL | SMV2H solar_dual_htf_daily.csv | MNQ exec $, up to 13 MNQ |
| BMOM_E2 | SMV2B ledger_E2 net_c1_ticks x $5 | 1-NQ $ |
| MASTER_EXEC_NT | SMV2M parity_daily_aligned `nt`, 2023-04-05/06 pair merged (+2,366.2 single obs) | MNQ exec $ |
| MASTER_TWIN | SMV2M parity_daily_aligned `tw` | MNQ exec $ |
| SM14_MNQ | SMV2H2 regen col 355_SM14_ref_oldM(3,1)_MNQ (column exists → reused) | 1-lot MNQ $ |

Crosschecks all PASS: BMOM daily rebuild = rerank BM_E2 (319,198.1 both); SM14 regen column
identical to SMV2H daily_curves (max diff 0.0); parity `tw` = twin_daily (4.5e-13);
SOLAR_DUAL net = rerank DUAL (138,280.0). Dollar units differ across curves (NQ vs MNQ,
multi- vs one-lot); percentages/signs/shape are the comparable dimensions.

---

## Q8 — What percentage of days/weeks/months are currently positive? (FACT — out/smoothness_battery.csv)

Dev, ISO weeks, calendar months/quarters (partial edge periods included; 230 wk / 53 mo / 18 qtr):

| curve | day+ | week+ | month+ | qtr+ | worst wk | worst mo | worst qtr | lose-streak d/w/m | roll20/60/120 floor | TUW | med/p95 recov |
|---|---|---|---|---|---|---|---|---|---|---|---|
| MASTER_EXEC_NT | 44.1% | 56.1% | 64.2% | 83.3% | −10,307 | −7,523 | −14,300 | 10/4/3 | −12,796/−16,610/−3,454 | 131 | 5 / 62 |
| MASTER_TWIN | 44.1% | 56.5% | 62.3% | 83.3% | −10,341 | −7,502 | −14,329 | 10/4/3 | −12,809/−14,518/−4,207 | 133 | 4 / 62 |
| SOLAR_DUAL | 41.0% | 51.3% | 66.0% | 88.9% | −11,151 | −9,221 | −11,763 | 9/5/3 | −15,662/−20,420/−11,546 | 143 | 5 / 105 |
| SOLAR_E10 | 41.0% | 46.1% | 66.0% | 77.8% | −13,345 | −18,212 | −32,077 | 9/6/3 | −20,397/−29,810/−20,904 | 162 | 13 / 111 |
| BMOM_E2 | 50.2% | 57.8% | 62.3% | 83.3% | −22,562 | −20,176 | −16,325 | 5/4/3 | −32,771/−32,123/−23,566 | 126 | 6 / 67 |
| SM14_MNQ | 46.6% | 54.8% | 62.3% | 83.3% | −2,180 | −2,273 | −3,140 | 6/5/3 | −3,147/−5,250/−2,354 | 172 | 3 / 70 |

- BMOM_E2 has 101 zero (no-trade) sessions counted as non-positive; among its 1,038 active
  sessions the positive-day rate is 55.1% (572/1,038, derived from battery columns).
- Worst-period labels (out/worst_periods.csv): master worst week = 2026-W21, worst month =
  2026-04 (−7,523), worst quarter = 2026Q2-partial. SOLAR_DUAL worst month = 2024-11.
- TUW/recovery are house dd_battery definitions (longest consecutive underwater run; recovery =
  completed underwater-episode length). Every curve has an open (unrecovered) episode at dev end,
  excluded from recovery stats.
- FACT: the owner's Q12/Q13 anchors reproduce from these artifacts: executable maxDD −18,894
  (battery), worst month −7,523.

## Q9 — What causes negative weeks/months? (FACT counts; INFERENCE on mechanism)

Master weekly sign vs the Solar_DUAL x B-MOM 2x2 (out/master_week_cell_overlap.csv):
101/230 master weeks are negative (43.9%). By cell:

| cell | n weeks | master-neg | mean master wk | sum |
|---|---|---|---|---|
| S+B+ | 71 | 0 (0%) | +4,526 | +321,358 |
| S+B− | 45 | 19 (42%) | +477 | +21,451 |
| S−B+ | 62 | 32 (52%) | −188 | −11,678 |
| S−B− | 50 | 50 (100%) | −3,193 | −159,638 |

FACT: every joint-loss week is a master-negative week; joint-loss weeks are 49.5% of all master
negative weeks and carry essentially the entire negative week-sum. Single-engine-loss weeks are
close to a wash (+477 / −188 means) — the 60/40 pairing hedges them.
INFERENCE: negative master weeks/months are not caused by one engine misfiring; they are caused
by the state in which BOTH engines lose at once (Q10). Reducing single-leg noise would barely
move week-level consistency; the joint-loss state is the whole game.

## Q10 — What causes joint Solar+B-MOM losing periods? (FACT — out/joint_loss_profile.csv, out/joint_loss_periods.csv)

Frequency: 50/230 weeks (21.7%), 7/53 months (13.2%): 2023-05, 2023-09, 2024-06, 2024-09,
2025-09, 2026-04, 2026-05. 2026 is over-represented: 8 of the 21 dev-2026 weeks are joint-loss
(38% vs 21.7% base), including the four worst joint-loss weeks on record (2026-W21, W13, W15, W08).

Concurrent market state of joint-loss weeks (Welch t vs non-JL weeks):
- **Both sides lose simultaneously**: mtm_short −1,690 vs +806 (t = −7.5), mtm_long −1,315 vs
  +1,246 (t = −6.7) — whipsaw, not directional error.
- **Low path efficiency**: ER(150) 0.0855 vs 0.0960 (t = −6.5).
- **High flip rate**: 9.78 vs 8.86 vote_pos sign changes/day (t = +3.0).
- **Sub-normal opportunity/friction**: session range / 0.718-pt NQ friction 434 vs 492 (t = −2.1).
- **NOT a volatility regime**: sigma460 t = +0.27, 20d realized-vol percentile t = −0.19,
  B-MOM activation rate t = +0.60, HTF mix t = +0.84 — all indistinguishable.

Prior state (the period before a joint-loss period):
- Prior week has elevated long-side profit (mtm_long +1,807 vs +367, t = +2.4) and higher ER
  (0.0971 vs 0.0927, t = +2.3). Prior month mirrors it (mtm_long +5,459 vs +2,557, t = +2.6).

Monthly joint-loss adds a side asymmetry: mtm_short −5,376 vs +2,136 (t = −2.9) with HTF-up
share 0.80 vs 0.64 — the losses concentrate in shorts taken inside up-regimes. The conditioning
matrix (out/conditioning_matrix.csv, dev bars, gross MTM) corroborates: SHORT x HTF_UP is the
only side x HTF cell with negative total MTM (−4,118, vs +102,370 for LONG x HTF_UP); by
time-of-day, losses concentrate in RTH 09:33–12:00 (−2.93M gross) and 00:00–09:33 (−2.07M).

INFERENCE: joint-loss periods are **post-trend chop transitions** — they follow strong long-side
trend periods and are marked by low directional efficiency, elevated flip rate and thin
range-to-friction, at completely ordinary volatility levels. Both engines are trend-continuation
shaped, so the trend→range hand-off hits them simultaneously.
HYPOTHESIS (for Engine-3 targeting, not a rule): a chop/transition state defined on ER(150) +
DC flip rate (explicitly NOT on vol level, and NOT on recent PnL) is the axis that separates
joint-loss periods; the secondary axis is short-exposure inside HTF-up states.

## Q11 input — Can Engine #3 reduce those?

Measured targeting spec for Engine-3 candidates (INFERENCE from Q10 facts):
1. The target state is identifiable by market structure (ER, flip rate, range/friction), not by
   vol or by engine PnL — consistent with V4.1 §13's "use market state" constraint.
2. B-MOM stays fully active through joint-loss weeks (activation 0.86 vs 0.84, ns) — there is no
   self-throttling in chop; an Engine-3/router acting on the chop state would be additive, not
   redundant.
3. Conflict bars (concurrent sign(Tpp) x sign(B) < 0, 30.6% of both-active bars) carry
   −309,880 cumulative gross MTM (out/component_attribution.csv) while the system's total dev
   gross MTM is +219,255 (net 179,289 + friction 39,966). FACT: signal-conflict bars are a large
   standing drag. HYPOTHESIS: a state that de-risks conflict is a second Engine-3-adjacent axis
   (note SMV2H cell 352/353 already probed a conflict-flat policy at the one-lot level).

## Q12 input — Can the executable −$18.9k DD be reduced at equal risk? (FACT — out/dd_ownership.csv, out/component_attribution.csv)

Leg decomposition of the master (spec fractional attribution; legs rebuild the twin exactly,
max daily error 1.8e-12): LEG_SOLAR net 96,583 (53.9%, Sharpe 0.88, leg maxDD 18,601);
LEG_BMOM net 82,705 (46.1%, Sharpe 1.14, leg maxDD 12,952); friction 39,966.

Top-10 executable DD episodes — leg ownership of the peak→trough loss:
- #1 −18,894 (2025-04-25→07-28): solar 43% / bmom 57%
- #2 −16,471 (2026-05-11→05-22): solar 54% / bmom 46% (open at dev end; recovery date is a
  CONSUMED-window observation)
- #3 −15,634 (2025-11-21→12-10): solar 63% / bmom 37%
- #4 −15,262 (2025-03-04→04-04): solar 62% / bmom 38%
- #6 −14,608 (2022-06-08→07-15): solar 125% / bmom −25% (B-MOM made +3,681)
- #10 −11,339 (2024-09-10→10-04): solar 40% / bmom 60%

FACT: 9 of the 10 top episodes are shared-loss episodes; neither leg owns the DD tail
(median solar share ~60%). INFERENCE: removing or resizing one leg cannot delete the −18.9k
class of DD at equal risk; the DD tail lives in the joint-loss state (Q10), so DD compression at
equal expectancy requires either the Engine-3 chop axis or an instrument with positive
expectancy in that state. (Leg ownership is measured on twin leg curves against NT episode
windows; SMV2M documented nt–tw daily corr 0.9992.)

## Q13 input — Can worst month materially improve from roughly −$7.5k?

FACT: master worst month = 2026-04 (−7,523); the seven joint-loss months average solar −3,181 /
bmom −5,921 per month (out/joint_loss_periods.csv). All worst-month candidates are joint-loss
months (2026-04: dual −8,726, bmom −1,914; 2026-05: dual −3,037, bmom −14,411). INFERENCE: the
worst-month statistic is another face of the joint-loss state — same target as Q12, not an
independent problem.

## Q14 input — Can TUW materially shorten? (FACT — out/winner_drought.csv)

Top-decile SOLAR_DUAL days (>= +2,494.2, n=114) arrive with median wait 6 sessions, p90 21.8,
p95 32.4, max 47. Champion (MASTER_EXEC_NT) drawdown conditional on drought-length quartile:

| drought quartile | wait range | mean uw depth | max uw depth | mean uw days | max uw days |
|---|---|---|---|---|---|
| Q1 (short) | 1–3 | 4,953 | 16,252 | 1.4 | 3 |
| Q2 | 4–6 | 5,537 | 13,045 | 4.1 | 6 |
| Q3 | 7–14 | 7,798 | 15,634 | 9.4 | 14 |
| Q4 (long) | 15–47 | 7,667 | 18,894 | 23.3 | 46 |

FACT: underwater time scales nearly 1:1 with winner-drought length (Q4 mean 23.3 uw days), and
the deepest DD (−18,894) sits inside the longest drought bucket. Master TUW = 131 sessions,
median recovery 5 days, p95 62. INFERENCE: TUW is structurally the waiting time for the next
top-decile cluster; it shortens only via an income stream whose winners arrive in the solar
droughts (again the Q10/Q11 state), not via exit/sizing cosmetics on the existing legs.

## Recency — "does it still work in 2026?" (out/recency_2026.csv)

FACT (dev, <= 2026-05-29):
- 2026 YTD-May nets: MASTER_EXEC_NT +11,965 (Sharpe 0.68); BMOM_E2 +25,522 (0.97);
  SOLAR_DUAL +4,661 (0.26); SM14 +88 (0.03); SOLAR_E10 −7,638 (−0.39).
- Rolling-120-session Sharpe at dev end vs own history (percentile): BMOM 1.50 (52nd);
  MASTER_EXEC_NT 1.12 (41st); MASTER_TWIN 1.05 (36th); SOLAR_DUAL 0.56 (35th); SM14 0.55 (27th);
  SOLAR_E10 −0.02 (17th).
- 2026 trajectory (monthly r120 percentile, master): Jan 86th → Feb 95th → Mar 87th → Apr 52nd →
  May 41st. The weakness is entirely an April–May event (both joint-loss months; the −16.5k DD
  is episode #2 all-time), arriving directly off a 95th-percentile February.
- Historical context: master r120 has been below zero in 3.8% of its history (min −0.38);
  SOLAR_E10 in 18.2% (min −1.37). Current readings sit far above every curve's historical minimum.

FACT (CONSUMED — committed artifact values, executable master only, nothing >= 2026-08-01):
June 2026 net +20,617; July +14,380 (+7,013 excluding the documented 07-30/31 window-edge
boundary days); 53.3% positive days over the 45 sessions; r120 Sharpe at 2026-07-31 = 1.03 =
36th percentile of dev history.

INFERENCE (per V4 §56 language): 2026 is a below-median but unexceptional stretch — every
curve's rolling-120 percentile (17th–52nd) is inside its own historical range, the April–May
drawdown is the same magnitude class as 2025's fully-recovered −18.9k episode, and the CONSUMED
June–July master values are strongly positive. A below-median rolling window is path evidence,
not proof of death. Regime risk stands; the preregistered decay monitors (MONITOR-01 / SM13)
remain the load-bearing instruments. No tuning, no gate, no selection follows from this read.

---

## Methods notes (conventions used, for reproducibility)
- Weeks = ISO weeks of session dates; months/quarters = calendar periods; partial edge periods included.
- BMOM_E2 placed on the 1,139-session master calendar with 0 on no-trade days.
- MASTER_EXEC_NT merges the 2023-04-05/06 data-gap boundary pair into one observation
  (+129,340.3 − 126,974.1 = +2,366.2 at 2023-04-05), as in the SMV2M parity recompute.
- TUW / recovery / rolling floors follow house `smv2_common.dd_battery` definitions
  (underwater = dd > 1e-9; floors = min of rolling 20/60/120-session sums).
- Friction constant for range/friction: 1-lot NQ round turn = 2 ticks slip + $4.36 Lifetime
  commission = 0.718 NQ points.
- Flip rate counts all vote_pos sign transitions (−1/0/+1) bar-to-bar within session.
- Component attribution implements the frozen formula solar_leg_pos = pos x KS*Tpp/(KS*Tpp+KB*B),
  KS=0.728654 / KB=2.934159, with the ratio evaluated on the signal bar that generated the
  position (pos[t] = tgt_ops[t-1] at 99.99% of bars; next-open fills). Evaluating it on the
  concurrent bar instead produces unbounded shares on near-cancel conflict bars (leg positions
  up to 596 contracts) because the position lags the signal — measured and rejected as a
  misalignment, not as a judgment call on the formula. Flat-signal carry bars (2,334) use the
  last valid share. Costs allocated per session by each leg's share of sum|delta leg target|;
  leg daily curves rebuild the twin exactly (max abs daily error 1.8e-12).
- Bar MTM = pos x within-session dClose x $2; fill-price/slippage/commission effects land in the
  session friction residual by construction.
- Conditioning matrix covers all dev years 2022–2026(May); gross MTM, costs excluded.
- No RNG used anywhere in this run (no bootstrap deliverables in spec).

## Artifacts
out/smoothness_battery.csv, out/joint_loss_profile.csv, out/joint_loss_periods.csv,
out/winner_drought.csv, out/component_attribution.csv, out/leg_daily.csv, out/dd_ownership.csv,
out/conditioning_matrix.csv, out/recency_2026.csv, out/crosschecks.csv, out/worst_periods.csv,
out/master_week_cell_overlap.csv.
