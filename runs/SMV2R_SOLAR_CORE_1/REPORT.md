# SMV2R_SOLAR_CORE_1 — SOLAR_CORE_CHALLENGE part 1 (seq 381-385)

Run dir: `runs/SMV2R_SOLAR_CORE_1` | Spec frozen at 58dc2d2 before execution.
Dev window: sessions <= 2026-05-31 (519,714 3m bars, 1,139 sessions, 2022-01-03 -> 2026-05-29).
No market data >= 2026-08-01 read anywhere; June-July 2026 bars in the shared CSV/substrate were
truncated out before any computation. No adoption of anything this wave (per spec gates).

Every number below is from an artifact in `out/` (file named per section).

---

## STEP ZERO — committed simulator verification (out/step0_verify.json)

Simulator: `src/analytics/sm01_solarsim.py` (the committed SM06 build engine; located via
`runs/SM06_SOLAR_HISTORY/run_hist.py`, which imports it to generate vote_state_3m_hist).

- FACT: vote_pend match vs `runs/SM01_SUBSTRATE/out/vote_state_3m.parquet` on dev =
  **100.0000%** (0 mismatches / 519,714 bars) — gate was >= 99.99%. **VERIFIED**.
- FACT: vote_pos match 100%; sigma460 max |dev| = 0.0; substrate p6..p30 columns are the
  member PENDING positions (100% match as pend, 99.13% as pos).
- FACT: instrumented E10 executor (verbatim `e10_sim` semantics + telemetry) reproduces
  committed `runs/SM01_SUBSTRATE/out/e10_daily_py.csv` on all 1,139 dev sessions,
  max |dev| = 1.8e-12 $.
- All subtracks therefore ran UNBLOCKED on the verified engine.

Incumbent dev baseline (out/vol_memory.csv, N460 row): net **$119,008.9**, Sharpe **0.709**,
maxDD **-$40,207.6**, CDaR5 **$27,161.8**, top-10-day sum **$117,986.2**, 43.9 contracts/day.

---

## 381 — Clamp audit (DIAGNOSTIC) — out/clamp_audit.csv, clamp_audit_meta.json

S = clamp(k*sigma460, 40t=10 pts, 1200t=300 pts), per member per bar on dev
(30 NaN-sigma warmup bars excluded; those use the 179t fallback).

- FACT: **lower bound is BOUND-IRRELEVANT** — worst member is vm6 at 0.125% of bars
  (vm8 0.006%, all others 0.000%). Well under the 1% bar for every member.
- FACT: **upper bound BINDS** for the slow cohort: vm18 1.08%, vm20 1.78%, vm22 2.86%,
  vm24 4.33%, vm26 6.37%, vm28 8.67%, **vm30 10.93%** of bars have k*sigma >= 300 pts.
  By-year rows in the CSV show the binding concentrates in high-vol years (2022, 2025).
- Verdict recorded: lower bound BOUND-IRRELEVANT (no parameter budget ever);
  upper bound NOT irrelevant — it is an active regularizer on slow members' thresholds.
- INFERENCE: the 1200t cap is doing real work: it caps slow-member reversal thresholds in
  high-vol regimes (at-flip binding 1.5-1.7% of all flips, out/vol_memory.csv). Combined with
  383 (SLOW cohort earns its place on tail metrics), the cap is part of why slow members stay
  useful rather than becoming un-exitable. Diagnostic only; no parameter budget granted.

## 382 — Vol memory (3 arms) — out/vol_memory.csv, vol_memory_verdict.json, boot_deltas.csv

Same 13 members, sigma memory N in {230, 460 incumbent, 920}; E10 execution
(round(10*mean pending), clamp +-10, MNQ $0.65/side + 1-tick slip, session flatten, _fill).

| arm | net $ | Sharpe | maxDD $ | CDaR5 $ | top10 sum $ | ES5/day $ | S@flip p50 pts | clamp-hi @flip % | contracts/day |
|---|---|---|---|---|---|---|---|---|---|
| N230 | 71,917.6 | 0.442 | -50,884.4 | 31,505.7 | 112,364.2 | -4,146.0 | 56.7 | 2.21 | 43.9 |
| **N460 (inc)** | 119,008.9 | 0.709 | -40,207.6 | 27,161.8 | 117,986.2 | -3,804.7 | 60.7 | 1.71 | 43.9 |
| N920 | 117,623.3 | 0.699 | -35,312.6 | 23,980.8 | 116,186.6 | -3,752.7 | 60.9 | 1.50 | 44.6 |

- FACT (frozen rule): neither neighbor beats the incumbent by >20% on Sharpe AND CDaR
  simultaneously -> **PLATEAU = TRUE** (N230_dominates=false, N920_dominates=false).
- FACT: halving memory (N230) is destructive: -$47,091 net, Sharpe 0.442 vs 0.709; paired
  bootstrap dMean -$41.3/day, p(d<=0)=0.949 (out/boot_deltas.csv).
- FACT: doubling memory (N920) is near-neutral: Sharpe -1.4% (0.699 vs 0.709), but CDaR5
  -11.7% and maxDD -$4,895; dMean -$1.2/day, p=0.537 — statistically indistinguishable.
- INFERENCE: the plateau is one-sided — performance is insensitive to LONGER memory and very
  sensitive to shorter. N920 is not a dominating neighbor under the frozen rule (Sharpe does
  not improve), so no R2 spec is earned; it is noted as a mild tail-softener only.

**V4.1 s22 Q4 answer: YES — the current volatility memory (460) is a robust plateau.**

## 383 — Cohort ablation (4 arms) — out/cohort_ablation.csv, cohort_marginal.csv, boot_deltas.csv

FAST = vm{6,8,10,12}, MID = vm{14..22}, SLOW = vm{24..30}. Target = round(10*mean over arm
members), clamp +-10, same executor.

| arm | net $ | Sharpe | maxDD $ | CDaR5 $ | ES5/day $ | top10 sum $ | retention of ALL-top10 | contracts/day |
|---|---|---|---|---|---|---|---|---|
| ALL (13) | 119,008.9 | 0.709 | -40,207.6 | 27,161.8 | -3,804.7 | 117,986.2 | 1.000 | 43.9 |
| no-FAST (9) | 146,122.6 | 0.768 | -40,473.6 | 26,742.6 | -4,415.8 | 133,021.5 | 1.059 | 23.7 |
| no-SLOW (9) | 116,147.2 | 0.660 | -56,588.9 | 36,355.4 | -4,186.1 | 118,089.5 | 0.998 | 55.3 |
| MID-only (5) | 168,336.0 | 0.835 | -53,221.6 | 34,562.0 | -4,919.7 | 133,116.6 | 1.073 | 29.9 |

- FACT (frozen rule): **FAST = REMOVABLE-CANDIDATE** — removal improves Sharpe (0.768 > 0.709)
  AND CDaR5 (26,743 < 27,162) AND retains 105.9% (>= 95%) of the ALL top-10-day sum. It also
  adds +$27,114 net and halves churn (43.9 -> 23.7 contracts/day).
- FACT: **SLOW is NOT removable** — removing it degrades everything that matters for tails:
  CDaR5 +$9,194 (+34%), maxDD -$56,589 vs -$40,208, Sharpe 0.660 vs 0.709.
- FACT: MID-only has the best Sharpe (0.835) and net but clearly worse tails (CDaR5 34,562,
  maxDD -53,222, ES5 -4,920). The frozen rule evaluates cohorts singly; MID-only is not a
  cohort-removal verdict and earns nothing by itself.
- Caveats (FACT, out/boot_deltas.csv): the no-FAST daily-mean edge is NOT statistically
  resolved — d +$23.8/day, p(d<=0)=0.179, CI [-26.4, +73.7]. ES5/day is WORSE without FAST
  (-4,416 vs -3,805): fast members damp typical bad days even while costing net.
- INFERENCE: FAST members act as expensive short-horizon hedgers: they cut daily left-tail
  (ES) but bleed churn costs and lower Sharpe/CDaR. Under the frozen prongs they are a
  REMOVABLE-CANDIDATE -> earns an **R2 confirmation spec later** (chronology + plateau +
  portfolio contribution per V4.1 s11). **NO adoption this wave.**

**V4.1 s22 Q5 answer: MID and SLOW earn their places decisively; FAST (vm6-12) does not
prove its keep on dev and is flagged REMOVABLE-CANDIDATE pending R2.**

## 384 — Signal layer T1/T2/T3 (DIAGNOSTIC) — out/signal_layer.csv, signal_layer_conditional.csv, signal_events.parquet, signal_layer_meta.json

Transplant of E10Master_v2.cs UpdateMachine ev/weak/wave semantics (SlowdownScan=5,
WeakWeakSplit=10) into the verified simulator; transplant asserted bar-for-bar identical to
`sm.member_states` (is_up/flip/S/anchor) for all 13 members. Events at decision bar close;
294,276 member events -> 94,140 unique (bar, type, dir) events (105 last-bar events dropped);
forward returns from next bar open via _fill, exit at close of bar t+{10,20,40}, truncated at
session end, net of 1-lot MNQ costs (2 x $0.65 + slip). MFE/MAE over the 120-min window.

Raw expectancy (unique events, $/event net):

- T1 (flip): long -1.65/+0.19/+1.34 at 30/60/120min (all |t_NW| < 1.9);
  short -2.40/-2.85/-2.96 (t_NW -2.29 at 30min, else n.s.).
- T2 (weak onset): long -1.63/-1.15/+0.42 (n.s. beyond 30min);
  short **-2.61/-3.47/-4.44 with t_NW -3.23/-2.92/-2.21** — significantly negative.
- T3 (resumption): long -1.85/-0.79/+0.88; short -1.44/-2.42/-2.08 (only long-30min t -2.24).
- FACT: no event type x direction has significantly POSITIVE net forward expectancy at any
  horizon; the only |t_NW| > 2 cells are NEGATIVE (short-side T1/T2, long T2/T3 at 30min).
- Overlap: 45-72% of events fire while the ensemble is already positioned the same way
  (T3-short 72.3%, T1-long 47.4%).
- FACT (key test, out/signal_layer_conditional.csv): conditional on the ensemble already
  positioned in the event direction, the incremental information of T1/T2/T3 is **zero** —
  event-dummy increments -$0.40..+$1.00/event with **all |t_NW| <= 0.70** across 9
  (type x horizon) cells against a baseline of 421,620 positioned bars.
- INFERENCE: T2/T3 fire mostly as restatements of the position state the ensemble already
  holds; the weak/wave layer adds no exploitable timing information at 30-120min on 3m dev.
  The mild NEGATIVE short-side readings are consistent with long-drift cost drag, not signal.

**V4.1 s22 Q6 answer: NO — T2/T3 contain no useful incremental information beyond the
position state (this closes the 3m-answerable part; 1m timing info is Part 2).**

## 385 — MA state jobs (DIAGNOSTIC) — out/ma_jobs.csv, ma_jobs_meta.json

States on 3m closes: ST1 = MA30/59, ST2 = MA100/400 (broad/HTF control), ER150 terciles
(dev breakpoints 0.0329/0.0781). Undefined warmup states = agree (no gating), excluded from
B/C/D stats. All information reads; |t_NW| > 2 bar; NO POLICY.

**JOB A — entry-confirmation counterfactual** (delay exposure-increasing target changes until
state agrees; reductions immediate):

| gate | net $ | dNet vs base | Sharpe | CDaR5 $ | PnL on base top-10 days | right-tail retention |
|---|---|---|---|---|---|---|
| baseline | 119,008.9 | — | 0.709 | 27,161.8 | 117,986.2 | 1.000 |
| MA30/59 | 92,786.3 | **-26,222.6** | 0.577 | 24,496.0 | 110,697.9 | 0.938 |
| MA100/400 | 82,547.2 | -36,461.7 | 0.615 | 24,617.1 | 78,478.0 | 0.665 |
| ER150-top | 71,043.5 | -47,965.4 | 0.514 | 21,942.4 | 98,174.1 | 0.832 |

- FACT: every confirmation gate destroys net (-22% to -40%) and Sharpe. MA30/59 gating blocks
  52,829 of 81,567 target-change decisions and costs $26.2k plus 6.2% of the right tail.
  Gates do reduce CDaR5/maxDD, but only by shrinking participation — Sharpe falls, so this is
  de-levering with lag, not risk skill.

**JOB B — soft confidence (next-day, HTF-controlled, NW lag 5, 1,138 days):**
- MA30/59 agreement | HTF: -$121.4/sd, t_NW = **-1.62** -> no information (and wrong sign).
- HTF (MA100/400) itself: +$0.28/sd, t_NW = 0.004 -> nothing.
- ER150-top fraction | HTF: -$206.0/sd, t_NW = **-3.27** -> crosses the bar, NEGATIVE sign:
  days spent positioned in top-tercile-ER regime predict LOWER next-day E10 PnL.
- Same-day MA30/59 agreement co-moves with same-day PnL (t 8.35) — mechanical, context only.

**JOB C — failure warning (state flip against open position vs random-flip placebo, matched
count, seed 20260808):** remaining-episode PnL real vs placebo: MA30/59 +$54.1 vs +$84.5
(t_welch -0.73, N=2,042); MA100/400 +$149.3 vs +$252.2 (t -0.70, N=232); ER150-drop +$35.6 vs
+$43.7 (t -0.25, N=3,063). FACT: no state flip predicts remaining-trade PnL beyond placebo.

**JOB D — re-entry after conflict resolution (exit at conflict, re-enter at resolution,
RT cost |pos|*2*($0.65+$0.50)):** mean benefit MA30/59 **-$123.5**/event (t -10.9, N=1,210,
25.4% positive); MA100/400 -$563.1 (t -5.2); ER150 -$292.1 (t -13.6). FACT: conflict windows
carry POSITIVE PnL on average (+$117 to +$557); stepping aside loses it and pays costs.

- Key output: **conditional on Solar+HTF, only ONE read crosses |t_NW|>2 — the JOB B ER150
  result, and its sign is a warning (rich-trend days revert next day), not a confirmation
  signal.** No MA state adds usable confirmation, failure-warning, or re-entry information.
- HYPOTHESIS (for a future spec only, no policy): the negative ER150 next-day read might be
  usable as a day-level exposure damper; it must survive its own chronology/plateau battery
  before any R2 consideration.

**V4.1 s22 Q7 answer: 30/59-style short-term state merely adds lag — it costs 22% of net and
0.13 Sharpe as an entry confirm, predicts nothing next-day, warns of nothing, and re-entry
timing off it is strongly negative.**

---

## V4.1 s22 Q1 (partial): why is the current Solar core still incumbent?

From this wave's evidence (dev, 3m-answerable parts): its volatility memory sits on a genuine
plateau (382); its clamp's upper bound is an active, useful regularizer on slow members
(381 + 383); its slow cohort is load-bearing for tails (383); its weak/wave signal layer is
redundant with the position state (384); and short-term MA confirmations only add lag (385).
The one open crack is the FAST cohort (REMOVABLE-CANDIDATE, unresolved at p=0.18) — Part 2
(1m/5m clock challenge) and an R2 cohort spec remain before the incumbent language can change.

## Conventions and caveats
- All arms share one calendar (1,139 sessions), one bar substrate, one executor; deltas are
  paired. House bootstrap: block=5, B=10,000, seed=20260808 (out/boot_deltas.csv).
- 384 forward returns are session-truncated; events deduplicated across members (pooled
  member counts reported alongside); NW lag = horizon bars (overlap correction).
- 385 ER150 "agreement" = top tercile (interpretation stated in spec terms: non-directional
  state); JOB D re-entry size approximated by position at conflict onset.
- Dev-only, in-sample diagnostics; ER tercile breakpoints are full-dev — fine for information
  reads, not for policy. NOTHING ADOPTED; incumbent language unchanged:
  CURRENT ROBUST SOLAR INCUMBENT.


## Post-red-team corrections (2026-08-08, orchestrator; artifacts were always correct)
1. Section 385 prose quoted stale ER150 tercile breakpoints "0.0329/0.0781"; the values
   actually used (and recorded in out/ma_jobs_meta.json, reviewer-recomputed) are
   0.050160 / 0.113819. No verdict affected.
2. Section 381 prose said vm30 upper-clamp binding "concentrates in 2022, 2025"; the
   artifact shows partial-2026 is the HIGHEST (39.2% of Jan-May 2026 bars vs 18.3% in 2025,
   9.8% in 2022). The 1200t cap is MORE binding now than in any full historical year —
   the prose understated this. Recorded accordingly in INDICATOR_FRONTIER/CURRENT_TRUTH.
