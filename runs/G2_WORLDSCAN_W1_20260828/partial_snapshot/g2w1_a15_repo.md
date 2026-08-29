# A15-REPO — GENESIS II WORLD DISCOVERY WAVE 1 — full working notes (2026-08-28, second pass)

Repo read-only at D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research
No repo writes performed. No web used (internal domain).

PROVENANCE NOTE: a prior partial run of this task left working notes at
runs/G2_WORLDSCAN_W1_20260828/partial_snapshot/g2w1_a15_repo.md. I treated it as data and
re-verified every load-bearing claim against primary sources before reuse. Verified this session:
- PARKED_NOT_DEAD.md read in FULL (all ~45 rows + NIGHT section) — matches.
- LIQREV01 SPEC.md + REPORT.md read in FULL — formulation, 8 gates, red-team veto all match.
- runs/GENESIS_BASELINES_20260828/REPORT.md + spec.yaml B3 definition — matches verbatim.
- CURRENT_BASELINE.md §0 table + §4 watchlist (FOLLOW_MORNING exact rule, numbers) — matches.
- HTFDIR01_DIRECTIONAL_TILT/REPORT.md (PASS-SCREEN B, FAIL A, SHORTHALF never touched) — matches.
- research/03_reverse_engineering/SOLARWAVE_MATH.md (rigid ±89t pair, open-model knobs §) — matches.
- research/frontier.yaml closure comments (H013 NOT RUN, SW05 redesigned veto never run,
  C3/C5/C6 NOT BUILT, SW07 no individual adjudication, ES k-fit NOT done) — matches.
- scalping_lab CAMPAIGN_STATE.md (Flatten1644 CONFIRMED_ADOPT, FSS-9 +1.3–2.9pp, CLEAN_MOVE
  path toll 0.63, 116/160 pool sessions lack BBO, friction floor 30–60min) — matches.
- C1 = $14.36 ≈ 2.872 ticks: CONSTITUTION.md / EXECUTION_MODEL.md — matches.
- GENESIS_PRIOR_RESEARCH_ATLAS item 1: LIQREV01 shadow "silently dropped from
  MONITORING_CALENDAR", "Cheapest high-value fix in the repo" — matches.

## (1) PARKED_NOT_DEAD.md inventory — research/weekly_edge/PARKED_NOT_DEAD.md
~45 rows + NIGHT section. Split:

FORWARD-GATED (revival = calendar time / forward data, not testable now):
- Mirrored SHORT sleeve (W61–63): best decoupling ever (daily rho −0.003 vs P1; trades 81.5% of
  P1-flat sessions; money stable in 95–100% of rolling windows). Killed by 2026 alone
  (−10.62 pts/session standalone; trailing-24m t at 0th pctile of own history; 0/5 usable LOYO
  folds). Revival: trailing-24m t reverting toward its median +2.1.
- W40 vol-expansion event sleeve: stress-net +$114/wk, corr +0.01 full / −0.25 in worst-decile
  weeks, 5.7% overlap, N1 97th; FAILS binding N2 count-matched null at 92nd (needs 95th).
  Revival: N2 ≥95th on a longer sample OR a causal mechanism for post-2019 viability.
- NIGHT overnight channel (W96): fails session-shift null at 88th (bar 95th; incumbent clears at
  100th). Standing FACTS: overnight SHORT dead (−$41,741/693 trades, 34.3% win; RTH short
  +$83,691 — short edge is an RTH phenomenon); overnight friction $19.77/ctrRT vs $14.52 →
  $5.25/RT standing tax. Revival: ANY overnight mechanism ≥95th on session-shift null; low rho
  alone does NOT revive.
- Prior-session-sign stand-aside (W51b): mechanism p=0.0635; passes worst-week nulls 98.8/99.3.
- h2000_t750 (W60): direction real (+4.9pp traded-day rate, 100% of windows); stopping point
  lacks an out-of-sample warrant.

TESTABLE NOW (unlock = data/construction the repo owns at $0):
- Tick/intrabar cluster — FOUR rows name intrabar info as the exact unlock:
  W42 MAE stop (winners' median MAE 0.86 ATR ≈ stop level → stop cuts winners; needs to tell
  recovering from non-recovering excursions); W54 entry-timing (closure on mechanism;
  "intrabar/tick information about the first five bars"); W55 hold-duration (prize −15.02
  pts/session in sub-37-min trades; unreachable from own features, max |rho| 0.11); W40
  sweep-and-reclaim (needs absorption visibility; DOM PAUSED but historical L1+L2 exports exist).
  Repo OWNS scalping_lab L1+L2 tick/BBO 2025-08-10→2026-05-31 (40 stratified dev sessions,
  ~341M rows) — never joined to weekly_edge questions.
- W43 ES/RTY/YM: dimensional constants re-derived (tail improved markedly, still no earnings);
  the SIGNAL family itself (VolMult set, sigma window, throttle q) never re-derived per
  instrument. Campaign-1 echo: frontier.yaml ES_PORTABILITY "Fitting k separately per
  instrument was NOT done"; shape travels (Spearman 0.780), level doesn't.
- Multi-Osc overlap as GATE (never as engine); CumDelta as delta gate with TRUE tick delta;
  event-based (not clock-based) segmentation; efficiency-chop idea with realized-range
  estimator ("the idea was right, the estimator wrong").

## (2) LIQREV01 dossier — research/system_master/LIQREV01_STRESS_REVERSAL/{SPEC.md,REPORT.md,src/,out/}
Formulation (frozen 2026-08-19, spec committed 9775c0a before run):
- Substrate research/scalping_lab/substrate/minute/NQ/nq1m_2005_202605.parquet (6,466,783 bars,
  sha256_16 dfd017ef, 2006-01-05→2026-05-29). Points, not %.
- ret(d)=sess_close(d)−sess_close(d−1); rv5(d)=sqrt(sum sq 1-min returns 09:30–15:58, d−4..d);
  Stress(d)=trailing-252 pct-rank(rv5)≥0.90; triggers from PRIOR 63 days: LONG iff Stress and
  ret≤q20; SHORT iff Stress and ret≥q80. Enter close(d)+1 tick adverse, exit close(d+1)+1 tick
  adverse, 1 NQ, $14.36/RT.
- 8 frozen gates: N≥300 · episode-block bootstrap CI_lo>0 (10k reps seed 20260819) · ≥5/7 named
  clusters positive · calm placebo not significantly positive · 3×3 plateau all 9 cells positive
  · tail safety · losing-day corr ≤0.25 vs certified Solar B ledger · 2016–26 not significantly
  negative.
Result: ALL 8 PASS on the letter. N=455 (243L/212S), net $263,646 ($579/t), episode CI
[+155,+1061], both cells positive ($552/$611), calm placebo −$43/t, MATCHED placebo −$162/t
(~$740/trade state spread), fill-robust (15:59/16:03/next-open keep G2), edge accrues next-day
RTH ($542/t of gross) not the gap ($51/t).
Veto (red team, W9-B1 precedent — letter-pass, claims refuted): (1) all statistical evidence
post-2020 (pre-2020 +$12.2/t CI [−171,+187]; post-2020 +$1,688/t; effective N≈5 macro events);
(2) mechanism label wrong (state gives ZERO stress sessions in 2009; Nagel-canonical clusters
negative → object = "vol-acceleration-gated reversal 2020–26"); (3) engine-#3 diversification
REFUTED (profit lands on Solar TOP-decile days +$148,934/14 days; Solar bottom-decile −$46,517;
zero trades in Solar's maxDD window; combo ΔSharpe +0.18 CI [−0.32,+0.70]); (4) standalone
uninvestable (20y Sharpe 0.680, 7.2-year underwater 2011→2018).
Shadow status: added to research/operational/MONITOR01_SHADOW_HTFDIR01.md as second frozen
construction (ADVANCE = forward net>0 AND ≥0 on Solar's forward losing days); PER ATLAS item 1
the shadow was SILENTLY DROPPED from MONITORING_CALENDAR — "Cheapest high-value fix in the
repo". The REGIME-LOCAL veto doctrine was later REVOKED by owner (post-W115, in CLAUDE.md §4).
Production readiness path: restore shadow → forward ADVANCE → new preregistered portfolio-role
spec → NT8 build + parity battery.

## (3) FOLLOW_MORNING — CURRENT_BASELINE.md §4; runs/WE_W114_INTRAMOM, WE_W116_FMADJUDICATE
Frozen object: buy at the 11:49 open if the 11:29 close > the 09:31 open, sell if below, exit
15:44, size 1 (END-stamped bars). "Parameter-light with a broad timing plateau", minute
inherited from W108 fade spec, never selected on outcomes.
Standalone CONFIRMED: $179/trade, 55.00%, corrected best-of-15 shared-sign null 96.3rd pctile,
mid-plateau 53rd, two-sided, dies only at ~18× measured spread.
Portfolio FAILS: worst-decile overlap 95.8th; +$66 on book-losing weeks vs chance +$842 (9.9th).
"XM_CONFLICT diversifies the book's LOSSES. FOLLOW_MORNING diversifies its WINS."
Virgin ≥2026-08-01 read is the scheduled decider.
World evidence that would strengthen the prior: NOT the Gao/Han/Li/Zhou open→last-half-hour
geometry (runs/GENESIS_H4B_LASTHALFHOUR_20260828: dead on modern NQ, slope −0.007 t −0.61, real
2006–09 t +3.02, gone by 2014). Useful evidence must be (a) midday-anchor continuation
specifically, (b) conditioning that revives intraday momentum on high-vol/news days, (c)
hedging-demand proxies (gamma, lev-ETF AUM) that TIME the effect. MOM01 already found
Baltussen-style diagnostic does not replicate on NQ.
MIRROR_CONT (runs/WE_W120_MOMMARGINAL): passes BOTH gates FOLLOW_MORNING failed (book maxDD
$11,489→$8,143, tail beta −1.861 at 0.9th pctile, 21 weeks) — standing
MIRROR_CONTINUATION_CONTROL for every future fade idea.

## (4) HTFDIR01 — research/system_master/HTFDIR01_DIRECTIONAL_TILT/REPORT.md + MONITOR01 shadow
PASS-SCREEN on Product B (ARM_LONGONLY: ΔSharpe +0.0853) with four binding red-team corrections
(86.4% of Δnet from 2025–26; post-dev 2026-06/07 adverse; mechanism = conditional trim of
marginal short class + long tilt, NOT new HTF information). Product A FAILED (closed, shot
spent). Role now: frozen candidate in MONITOR-01 shadow, evaluation-only, first reading
≥2026-11-01. NEVER TOUCHED: the A-side SHORTHALF channel — REPORT §3 names it as a materially
different HTF hypothesis requiring its own preregistration.

## (5) ORB control — runs/GENESIS_BASELINES_20260828/{spec.yaml,REPORT.md}
B3 exact: "opening-range breakout — 09:30-10:00 ET high/low; first break long/short; exit 15:59
close; one entry/session max; no stop (canonical simple form, NO parameter search)". 239 ISO
weeks 2022-01-03→2026-07-31, 1 ctr, $18.80/ctrRT ($4.36 comm + $14.44 modelled spread).
Result: $1,043/wk net, t 2.19, maxDD $60,782, 60.3% pos weeks, worst wk −$36,829; at common
$20,245 DD earns $347 vs incumbent $1,230. "THIRD independent sighting of modern-era intraday
continuation (after W114's clock geometry and W118's mirror)". Controls CANNOT be promoted from
that run. A fresh ORB campaign must: new preregistered hypothesis inside atlas family H4; face
the portfolio-marginal gate FOLLOW_MORNING failed; measure P1 overlap; state a mechanism for the
opening range specifically; survive session-shift/circular nulls + MIRROR_CONTINUATION_CONTROL;
note campaign-1 prior art: the ORB-FAILURE fade (FB01/B01c) is falsified — momentum side is the
live side.

## (6) SolarWave recovered math — research/03_reverse_engineering/SOLARWAVE_MATH.md (+TYPE2 reports)
Recovered exactly: close-only 1-state ratchet (S=179 ticks, strict '<' flip); TrailingStop /
TrendVector rigidly ±89t from same anchor (verified on all 737,707 bars); weak/strong automaton
(SlowdownScan=5, WeakWeakSplit=10); Signal_Wave impulse-leg counter (15,925 changes verified);
Type-2 edge-triggered intrabar H/L latch (45,825 events, 0FP/0FN); path chaos intrinsic (S=179
→ $259k vs S=180 → $171k) → neighbourhood medians the only honest read. Open-model knobs never
exposed by vendor: S non-constant; anchor ≠ close extreme; split reverse/exit distances; wave
counter interpretation.
Tested INSIDE Solar family (frontier.yaml): H006 adaptive S inconclusive; H007 split exit
failed; H008 anchor redundant; H011 failed; H014 vol-proportional CONFIRMED (P=0.009);
wave-index re-entry conditioning failed; C2/C4 failed; DC02B sigma-invariance of overshoot r
PASSED (banded r halves yearly CV; monitored).
NEVER tested AS FEATURES FOR OTHER ENGINES: automaton state vector {weak flag, wave index,
bars-since-extreme, signed distance-from-anchor in S units, banded overshoot ratio r} as
conditioning/gating inputs to non-Solar engines (XM_CONFLICT, B-MOM channel, FOLLOW_MORNING,
ORB/H4 objects). W40's complement-set model used 42 causal features on bars where Solar holds
NOTHING — the state-vector-as-gate-on-OTHER-engines direction is distinct and unrun.
solarwave.py deterministic, no NT8 needed.

## (7) Never-executed ideas — research/frontier.yaml closure comments + registries
- H013_ENSEMBLE_WEIGHTING: "recorded NOT RUN"; 1/N stands on complexity grounds.
- SW05 redesigned eff_120 low-path-efficiency veto: never run (class foreclosed by right-tail
  rule — top 1% of trades = 160–248% of net).
- SW02 catastrophe-stop half: "spec existed, never run" (superseded by campaign-3 SM02/SM03).
- SW07_MAJOR_MINOR_CONTEXT: "no individual adjudication on record anywhere in the repo".
- C3/C5/C6 sleeve architectures: recorded NOT BUILT (registry/hypotheses.md Wave 3).
- ES per-instrument k fit: NOT done (ES_PORTABILITY; shape Spearman 0.780).
- XSMOM cross-sectional momentum: never tested (GENESIS_HYPOTHESIS_ATLAS H3, E1).
- GAMMA00 dealer-gamma: DATA_LIMITED, owner-gated purchase (ACTIVE_RESEARCH_QUEUE).
- git log --diff-filter=D over *frontier*/*plan*: nothing deleted (per prior forensics pass).

## (8) Campaign-4 scalping-lab unexploited findings — research/scalping_lab/CAMPAIGN_STATE.md etc.
- C1 = $14.36/RT ≈ 2.872 NQ ticks (CONSTITUTION.md; EXECUTION_MODEL.md); C2 = 4.872t.
  Real spread 2–3t RTH median; spread at opportunity moments 2.42t vs 1.79t control.
- E10 Flatten1644 CONFIRMED_ADOPT (net −5.35% within gate, corr 0.9972, tail retention 95.8%).
- FSS-9 VWAP-reclaim: lift +1.3–2.9pp = campaign conditional RECORD, short of the +7–10pp
  needed at FAST horizon; NEVER re-tested at the ~30–60min friction-floor horizon where required
  capture falls to realistic levels (DR-E friction floor reclassified PRIOR, not closure).
- CLEAN_MOVE label map: clean fraction 42%, path toll P(−4 before +8)=0.63; clean-vs-dirty
  separates on DEEP contrarian pre-move (ret30 −15 vs −5), eff60, flow — not vol/spread. P3
  "one final migration experiment" (CLEAN seed at 10–60min holds, 40–80t brackets) superseded by
  Amendment 6 restructuring — never run as specified at 30–60min.
- Only directional precursor: CONTRARIAN 5–30s counter-move before up-opportunities.
- 116/160 untouched pool sessions lack local BBO; rolling ~1yr server window (OWNER_QUEUE OQ-4).

## Independence notes
- research/weekly_edge/REPO_MINING_20260825.md already mined campaigns 1/3/4/6 for #7: ranked
  Type-3 warm-start (acted on), TOD-normalized threshold clock, multi-clock members, LIQREV01
  parallel sleeve, gap-rejection fade, true-range sigma, session-target re-adjudication.
- GENESIS_PRIOR_RESEARCH_ATLAS ranks LIQREV01 shadow restoration #1, FOLLOW_MORNING #2,
  mirrored short / W40 vol-expansion / NIGHT #3. Overlaps flagged per lead.

## Deliberately NOT turned into leads
- CLOSEREV01 / TOMFLOW01 / ATRPOOL01 / TERMFLOW: adjudicated FAIL-closed.
- Macro surprise magnitude: N-bound (71 sessions), closed at any price.
- B-FADE 16-unseen-years +1.68t below existence bar.
- Mirrored SHORT sleeve / W51b / h2000_t750: purely forward/calendar-gated — inventoried above;
  covered by one combined monitoring-policy lead.
