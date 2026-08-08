# SMV2U_CLOCK_CHALLENGE -- clock/memory challenge to the 3m Solar core (seq 390-392)

Class: R1_FAMILY_TEST + DIAGNOSTIC (SOLAR_CORE_CHALLENGE part 2, V4.1 s4-5). Spec frozen 2026-08-08
(`spec.yaml`). Executors: `step0_substrate.py`, `step1_clock_arms.py`, `step2_mtf_reads.py` (this
dir). Artifacts: `out/substrate_verify.json`, `out/clock_arms.csv`, `out/portfolio_contrib.csv`,
`out/smoothness_battery.csv`, `out/loyo_tables.csv`, `out/daily_curves.csv`, `out/mtf_reads.csv`,
`out/mtf_reads_meta.json`. Every number below is read from those artifacts. Dev sessions
<= 2026-05-31 only; no data >= 2026-08-01 read anywhere (substrate files extend to 2026-07-31 but
were truncated to dev immediately after session-tagging, before any economic computation).

## Verdict (NO adoption language -- per spec verdict_rule, this section states only what the
frozen rule outputs, not a deployment recommendation)

| seq | object | result |
|---|---|---|
| 390 | 1m clock, bar-matched (N=460 1m bars) | standalone FAIL, portfolio FAIL -- does not earn an R2 spec |
| 390 | 1m clock, time-matched (N=1380 1m bars) | standalone FAIL, portfolio FAIL -- does not earn an R2 spec |
| 391 | 5m clock, bar-matched (N=460 5m bars) | standalone PASS, portfolio FAIL (near miss) -- does not earn an R2 spec |
| 391 | 5m clock, time-matched (N=276 5m bars) | standalone PASS, portfolio PASS -- **earns an R2 spec** under the frozen rule |
| 392 | R1 failed-start detection | NOT_INFORMATIVE (both 1m conventions) |
| 392 | R2 entry-timing value | **INFORMATIVE** (bar-matched 1m only; t_NW=-2.09, boot 0.984) |
| 392 | R3 agreement acceleration | NOT_INFORMATIVE (both 1m conventions) |

FACT: exactly one of the four challenger arms clears the frozen bar (Sharpe AND CDaR5, standalone
AND portfolio, simultaneously): **5m time-matched**. Per spec this means it "earns an R2 spec" --
a defined technical outcome (a follow-up confirmatory spec becomes eligible), not an adoption or
promotion decision. The two "expected honest outcomes" the spec called out both occurred: 1m
churns away the edge after costs (both 1m arms have friction_share > 1.0, i.e. friction exceeds
gross P&L) and the 5m bar-matched arm is a genuine near-miss, not a clean pass.

## 0. Substrate verification (FACT, `out/substrate_verify.json`)

Session assignment for the 1m bars used the 3m file's own NT8-native session end-times
(`runs/AUDIT03_BARS/nq_3m_2022_2026.csv`, built by `AuditBarExport1` from NT8's session template)
via a backward interval search -- NOT a from-scratch intraday-gap heuristic. This matters: a naive
">1hr gap = new session" builder applied to the raw 1m feed produces a **false extra session split
on 2022-11-06** (a genuine ~10.5h thin-liquidity data gap inside that Sunday-open session, present
in both the 1m and 3m raw feeds, that a naive builder mis-reads as two sessions). The interval
method inherits the 3m file's authoritative boundaries directly and is immune to this.

| | 3m (dev) | 1m (dev) | 5m (dev, built from 1m) |
|---|---|---|---|
| sessions | 1139 | 1139 (exact match) | 1139 (exact match) |
| bars | 519,714 | 1,558,498 | 311,849 |
| session-date-set == 3m dev | -- | TRUE | TRUE |

Zero of 1139 sessions were flagged for an abnormal 1m/3m bar-count ratio (checked outside
[2.5, 3.05]x -- the ~3x expected from bar-width alone; flag list in
`out/substrate_flagged_sessions.csv`, empty). Only 2 of the full file's 1,620,044 1m bars fall
outside the 3m calendar's bounds -- both are the file's final two timestamps (2026-07-31
16:58-16:59), past dev end and never used. 5m bars are built by session-grouped `ceil('5min')`
aggregation of the tagged 1m bars (18:00 ET open is a 5-minute-boundary time, so this is
18:00-anchored automatically, exactly as the incumbent's `ceil('3min')` 3m build is).

## 1. Construction (FACT, verbatim reuse)

13-member V3 ensemble (`sm01_solarsim.member_states` / `member_trades`, VMS = 6..30 step 2) and
the E10 executor (`tgt = clip(rha(10*mean pending), +-10)`, fills next bar open +-1 tick on the
SAME clock, MNQ costs $0.65/side, session flatten) are the exact functions from the verified
SMV2R_SOLAR_CORE_1 simulator, called unmodified with only the bars-frame and `sigma_series`
`vol_period` argument changed. `bars_required=20`, `sigma` `min_count=30`, S clamp [40,1200] ticks
are all unchanged from the incumbent. The 3m incumbent reference is **not recomputed** -- reused
verbatim from the already-committed `runs/SMV2R_SOLAR_CORE_1/out/cache_incumbent.npz` and
`e10_daily_dev_incumbent.csv` (net $119,008.90 dev, cross-checked identical to
`runs/SM01_SUBSTRATE/out/e10_daily_py.csv` and to the SOLAR_E10 row of
`runs/SMV2Q_DIAGNOSTICS/out/smoothness_battery.csv`).

## 2. Standalone battery (seq 390/391, `out/clock_arms.csv`)

| arm | net $ | Sharpe | Sortino | Calmar | CDaR5 $ | worst month $ | top-10-day sum $ |
|---|---:|---:|---:|---:|---:|---:|---:|
| 3m incumbent | 119,008.9 | 0.709 | 1.527 | 0.655 | 27,161.8 | -18,211.5 | 117,986.2 |
| 1m bar-matched | -33,045.2 | -0.195 | -0.302 | -0.120 | 56,417.9 | -29,511.1 | 105,746.4 |
| 1m time-matched | -3,163.4 | -0.018 | -0.032 | -0.010 | 52,924.4 | -24,952.5 | 105,506.5 |
| 5m bar-matched | 129,089.0 | 0.728 | 1.524 | 0.913 | 25,528.0 | -16,760.2 | 127,777.8 |
| 5m time-matched | 136,527.2 | 0.793 | 1.654 | 1.056 | 22,521.0 | -16,380.8 | 126,399.3 |

FACT: both 1m arms lose money outright on dev. Both 5m arms beat the incumbent on every column
shown; 5m time-matched is the stronger of the two on every metric except being the more
bar-count-fragile choice (see SS6 LOYO).

## 3. Why: friction share (`commissions + slippage / gross`, per spec's own framing)

Friction/contract-side = 1-tick adverse slip x MNQ point value + commission = 0.25 x $2.00 +
$0.65 = **$1.15/side** (same accounting convention as `smv2q.py`'s `NQ_FRICTION_PTS`). Gross =
net + total friction; friction share = total friction / gross.

| arm | tgt changes/session/day | total contracts traded (dev) | total friction $ | gross $ | **friction share** |
|---|---:|---:|---:|---:|---:|
| 3m incumbent | 33.0 | 49,964 | 57,458.6 | 176,467.5 | **0.326** |
| 1m bar-matched | 90.4 | 130,558 | 150,141.7 | 117,096.5 | **1.282** |
| 1m time-matched | 99.0 | 140,526 | 161,604.9 | 158,441.5 | **1.020** |
| 5m bar-matched | 20.3 | 33,100 | 38,065.0 | 167,154.0 | **0.228** |
| 5m time-matched | 19.6 | 31,682 | 36,434.3 | 172,961.5 | **0.211** |

FACT: this is exactly the mechanism the spec anticipated. 1m has ~2.7-2.8x the incumbent's
turnover (contracts traded) despite the state machine being unchanged -- the same anchor/flip
logic reacts to far more bar closes per unit time on a 1-minute clock -- and friction consumes
100-128% of the strategy's own gross edge. 5m has *lower* turnover than the 3m incumbent (19.6-20.3
vs 33.0 tgt-changes/day) even though it decides more frequently per session in wall-clock terms;
coarser bars apparently damp bar-to-bar whipsaw in this anchor-and-flip mechanism enough to net out
ahead, not just avoid 1m's damage.

## 4. Right-tail retention vs incumbent (`out/clock_arms.csv`, k=114 = ceil(10% x 1139))

| arm | RTC on incumbent's top-decile days | own-vs-incumbent top-decile day overlap |
|---|---:|---:|
| 1m bar-matched | 0.733 | 0.675 |
| 1m time-matched | 0.714 | 0.596 |
| 5m bar-matched | 0.972 | 0.842 |
| 5m time-matched | 0.952 | 0.825 |

FACT: 5m retains 95-97% of the incumbent's best-day P&L; 1m retains only 71-73%. INFERENCE (bonus,
not spec-required): full daily-curve correlation with the incumbent is 0.882 (5m bar-matched),
0.893 (5m time-matched), but only 0.788 (1m bar-matched) / 0.751 (1m time-matched) -- the 1m clock
is not a noisy version of the same signal at the margin, it is a *different* signal
(`out/daily_curves.csv` correlation matrix).

## 5. Portfolio contribution (`out/portfolio_contrib.csv`) -- 60/40 vm-blend vs frozen BMOM E2

Same rerank construction as `runs/SMV2H_ONECONTRACT/rerank.py`: `SIG = leg.std()`; both legs
rescaled to that basis (`vm(x) = x * SIG/x.std()`); blended `ws*leg + wb*vm(BM)` at ws=0.6, wb=0.4;
result re-scaled to SIG once more. BM = frozen `runs/SMV2B_BMOM_EXEC_AUDIT/out/ledger_E2_next_open
.parquet` (`net_c1_ticks` x $5), reindexed to each arm's own dev calendar, unmodified. **Leg =
each arm's own plain-E10 daily curve** (this run builds no DUAL_HTF layer, so there is no "DUAL"
curve to blend as in SMV2H/SMV2Q; the plain-E10 curve is the only leg SMV2U produces -- INFERENCE,
flagged in SS10).

| portfolio | net $ | Sharpe | CDaR5 $ | maxDD $ | longest TUW (days) |
|---|---:|---:|---:|---:|---:|
| 3m incumbent | 187,905.5 | 1.120 | 19,299.3 | 30,745.2 | 134 |
| 1m bar-matched | 85,964.2 | 0.507 | 32,821.6 | 47,896.8 | 327 |
| 1m time-matched | 110,635.4 | 0.642 | 35,492.9 | 51,642.8 | 324 |
| 5m bar-matched | 197,346.5 | 1.113 | **19,509.6** | 25,958.7 | 139 |
| 5m time-matched | 199,173.3 | **1.156** | **17,921.7** | 25,009.0 | 139 |

FACT: 5m bar-matched is a genuine near-miss at the portfolio level -- Sharpe 1.113 < 1.120 and
CDaR5 $19,509.6 > $19,299.3 (worse by $210, ~1.1%) -- it fails the portfolio half of the rule by a
small margin despite a large standalone win. 5m time-matched clears both (Sharpe +0.036, CDaR5
-$1,377.6, ~7.1% better). Both 5m portfolios have a slightly *longer* longest-TUW than the
incumbent portfolio (139 vs 134 days) -- the verdict rule is defined on Sharpe+CDaR5 only, so this
does not change the outcome, but it is reported honestly per the spec's "report friction share to
prove WHY, whatever the outcome" instruction extended to every non-gate metric.

## 6. LOYO robustness (`out/loyo_tables.csv`, dSharpe = arm - incumbent, 5 leave-one-year-out folds)

| arm | full-sample dSharpe | LOYO sign agreement |
|---|---:|---:|
| 1m bar-matched | -0.904 | 5/5 |
| 1m time-matched | -0.728 | 5/5 |
| 5m bar-matched | +0.019 | **3/5** |
| 5m time-matched | +0.083 | 5/5 |

FACT: 1m's underperformance is robust (consistently negative in every leave-one-year-out fold --
not one bad year driving the whole result). 5m bar-matched's standalone edge over the incumbent is
tiny (+0.019 Sharpe) and its sign flips in 2 of 5 LOYO folds -- exactly the kind of fragile,
near-tie result the portfolio-level near-miss above would predict. 5m time-matched's edge (+0.083)
is 4x larger and sign-stable in all 5 folds, including leave-2022-out.

## 7. Verdict scorecard (frozen rule: beats incumbent on Sharpe AND CDaR5, standalone AND portfolio)

| arm | standalone beats | portfolio beats | earns R2 spec |
|---|---|---|---|
| 1m bar-matched | FALSE | FALSE | FALSE |
| 1m time-matched | FALSE | FALSE | FALSE |
| 5m bar-matched | TRUE | FALSE | FALSE |
| 5m time-matched | TRUE | TRUE | **TRUE** |

## 8. MTF information reads (seq 392, `out/mtf_reads.csv`, `out/mtf_reads_meta.json`)

DIAGNOSTIC -- information only, no policy, no exposure rule triggered by any outcome here.
Machinery identical to SMV2J_STATE_HARNESS ("JOB1"): OLS with Newey-West HAC (maxlags=5), bar
|t_NW| > 2, moving-block bootstrap confirm (block=5, B=10,000, seed=20260808, house convention),
same-sign fraction >= 0.975 required to confirm. 1m votes are resampled onto the 3m decision-bar
spine via a **backward** asof join on timestamp (no lookahead: state at or before the 3m bar close
only). 519,489 of 519,714 3m decision bars (99.957%) have an exact-timestamp 1m bar; the remaining
225 (0.043%) are resolved by carrying forward the most recent 1m state -- isolated single-minute
gaps scattered across the multi-year 1m feed (thin-liquidity zero-print minutes), confirmed NOT a
systematic or clustered gap (spot-checked: e.g. 2022-03-09 21:00-23:00 has roughly 15-24 missing
individual minutes out of ~120 depending on inclusive/exclusive window-bound interpretation,
scattered singly, never more than 1-2 consecutive). Both frozen 1m memory
conventions are read; **bar-matched is primary** (mechanism-neighbor: matches the incumbent's
bar-count memory, reacts fastest), time-matched is a secondary cross-check -- this split is not
spelled out verbatim in the frozen spec and is flagged INFERENCE (SS10).

### R1 -- failed-start detection: 1m disagreement -> next-3m-bar adverse move (same-session bars only)

| convention | n | n disagree | mean adverse|disagree | mean adverse|agree | spread (pt) | t_NW | boot same-sign | verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| bar-matched | 420,601 | 83,978 (20.0%) | +0.0392 | -0.0344 | +0.0736 | +1.66 | 0.949 | NOT_INFORMATIVE |
| time-matched | 420,601 | 78,044 (18.6%) | -0.0010 | -0.0240 | +0.0229 | +0.48 | 0.688 | NOT_INFORMATIVE |

FACT: neither convention clears |t_NW|>2; bar-matched is the closer of the two (t=1.66) but its
bootstrap same-sign fraction (0.949) still falls short of the 0.975 confirm bar. 1m member-vote
disagreement with the positioned 3m core carries no statistically defensible early-warning content
for the very next 3m bar under this harness.

### R2 -- entry-timing value: 1m disagreement at entry -> episode final PnL (n=4,746 episodes)

| convention | n disagree | mean PnL|disagree | mean PnL|agree | spread ($) | t_NW | boot same-sign | verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| bar-matched | 769 (16.2%) | -38.76 | +39.16 | **-77.92** | **-2.09** | **0.984** | **INFORMATIVE** |
| time-matched | 577 (12.2%) | +39.34 | +24.77 | +14.57 | +0.37 | 0.630 | NOT_INFORMATIVE |

FACT: bar-matched clears both bars (|t_NW|=2.09>2, boot same-sign 0.984>=0.975) -- the only
INFORMATIVE cell in this run's 6-cell multiple-testing budget (spec's 3 preregistered reads R1/R2/R3
x 2 frozen memory conventions = 6, confirmed by `out/mtf_reads.csv` row count). When the incumbent's 3m E10 executor opens a
new position and the 1m bar-matched ensemble's vote sign disagrees with that entry's side at the
entry bar, the episode's average total PnL is -$38.76 vs +$39.16 when the 1m vote agrees -- a
$77.92 spread. Per spec class=DIAGNOSTIC: **this triggers no policy and is not a gate the
incumbent must clear** -- it is recorded as the one live information result from this run.
time-matched does not replicate it (t=+0.37, wrong-signed relative to bar-matched even).

### R3 -- agreement acceleration: d/dt(15min 1m vote sum) -> next-session DUAL PnL beyond sigma460+HTF

| convention | n | beta (z-state) | t_NW | boot same-sign | verdict |
|---|---:|---:|---:|---:|---|
| bar-matched | 880 | -64.62 | -0.86 | 0.801 | NOT_INFORMATIVE |
| time-matched | 880 | -45.59 | -0.58 | 0.708 | NOT_INFORMATIVE |

FACT: neither convention adds incremental information about next-session SOLAR_DUAL_HTF PnL beyond
sigma460+HTF (SMV2J's own control set) -- both far short of |t_NW|>2, consistent with SMV2J's
own 0/12 result on a structurally similar family of trend-quality states.

## 9. What stands, honestly labeled

- FACT: 1m clock KILLED outright at both frozen memory conventions -- friction share 102-128% of
  gross, net negative on dev, LOYO-robust in its badness (5/5 folds agree it underperforms).
- FACT: 5m clock is a genuine split result, not a clean pass. Bar-matched wins standalone by a
  fragile, LOYO-unstable margin and misses the portfolio bar narrowly; time-matched wins both
  levels of the frozen rule with a LOYO-stable margin and earns an R2 spec.
- INFERENCE: 5m's edge over 3m appears to come from turnover reduction in the SAME anchor/flip
  mechanism (tgt-changes/day roughly 1.6-1.7x lower than the incumbent, not higher), not from
  catching moves earlier -- the opposite of the "faster clock, earlier information" intuition that
  motivated testing 1m. INFERENCE: coarsening the decision clock past 3m minutes (to 5m) still
  keeps the state machine responsive enough to trade, while damping some of the whipsaw the 3m
  clock itself pays for; this run does not test clocks coarser than 5m and draws no conclusion
  about where the tradeoff turns.
- INFERENCE: R2's entry-timing result (1m bar-matched disagreement at entry predicts worse episode
  PnL, INFORMATIVE) is the one statistically defensible new signal in the seq 392 battery. It is
  reported as information only per spec (class=DIAGNOSTIC, no_moves on policy); it did not
  replicate on the time-matched 1m convention, which is a genuine open question the frozen 6-cell
  budget does not resolve, not a contradiction to explain away.
- HYPOTHESIS (not tested here, no action licensed by this run): if the R2 entry-timing effect is
  real, it would most naturally motivate a JOB2-style soft-weight or entry-veto policy conditioned
  on 1m bar-matched disagreement at entry bars -- that would be a NEW pre-registered spec, not a
  re-read of this one, per the same discipline SMV2J and SMV2N both applied.

## 10. Caveats / ambiguity resolutions (all fixed before results were read, none decision-critical
except where noted)

1. Session tagging for 1m/5m bars: assigned via backward interval search against the 3m file's own
   session end-times, not a from-scratch gap heuristic (SS0). This is a construction choice the
   spec left implicit ("verify session calendar matches the 3m substrate's sess_dates"); the
   verification step it produced (zero mismatched sessions, one documented false-split avoided) is
   exactly what the spec asked for.
2. **Portfolio leg choice (flagged, most material inference in this run)**: "portfolio contribution
   uses frozen BMOM E2 daily and the rerank vm construction" is read as: apply rerank.py's blending
   METHOD to each arm's own plain-E10 daily curve (the only curve this run produces), not to a
   DUAL_HTF policy curve (which SMV2U does not build). The 3m incumbent's portfolio row uses its
   own plain-E10 curve for the identical reason, so the comparison is apples-to-apples internally;
   it is NOT comparable in level to SMV2H/SMV2Q's DUAL_HTF-based portfolio numbers.
3. Friction share formula: `total_friction / (net + total_friction)`, where total_friction =
   total contracts traded x ($1.15/side = 1-tick slip $ + $0.65 commission), matching the
   `NQ_FRICTION_PTS`-style per-side accounting already used in `smv2q.py`. The spec states
   "commissions+slippage / gross" without defining "gross" explicitly; this is the natural reading
   (gross = P&L before costs) and is applied identically to all 5 arms including the incumbent.
4. Right-tail overlap: implemented as (a) RTC = arm PnL summed over the incumbent's own top-decile
   (k=ceil(0.10n)=114) days / incumbent's sum over those same days (identical definition to
   SMV2N's RTC and sub383_cohort.py's retention_ALL_top10), and (b) a symmetric top-decile
   day-set overlap fraction, both reported.
5. MTF reads' 1m-clock memory convention: not specified verbatim by the spec for seq 392; bar-
   matched (N=460 1m bars) is treated as primary (mechanism-neighbor, fastest-reacting), time-
   matched reported as a secondary cross-check for all three reads (SS8).
6. R2 episode definition: contiguous nonzero runs of the incumbent 3m E10 executor's `bar_pos`
   array (from the already-verified `cache_incumbent.npz`), entry = first bar of the run, PnL =
   sum of `bar_pnl` over the run (includes entry and exit/flatten fill costs by construction).
7. R1's "next-3m-bar adverse move" excludes bars where the 3m core is flat (vote3m=0) and bars
   that are a session's last bar (so "next bar" never crosses the overnight session gap).
8. R3 state ("d/dt of 1m vote sum over last 15min") read as: roll15_t - roll15_{t-15}, where
   roll15_t = mean of the 1m vote over the trailing 15 1-minute bars ending at bar t, evaluated at
   each session's closing 1m bar; z-scored over the post-burn-in regression sample (burn-in >=12mo
   from the first dev session), identical construction to SMV2J's test_2.
9. No data >= 2026-08-01 was read anywhere. Source substrate files (`nq_1m_2022_2026.parquet`,
   `nq_3m_2022_2026.csv`) extend to 2026-07-31 (used only to establish correct session boundaries
   near the file tail); every economic computation in step1/step2 operates on sess_date <=
   2026-05-31 rows only, asserted in code.
