# A15-REPO — GENESIS II WORLD DISCOVERY WAVE 1 — full working notes (2026-08-28)

Repo read-only at D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research
No repo writes performed. No web needed/used.

## Task items and where each was answered

### (1) PARKED_NOT_DEAD.md full inventory — research/weekly_edge/PARKED_NOT_DEAD.md
~45 rows + the NIGHT section. Key split (testable-now vs forward-gated):

FORWARD-GATED (revival = calendar time / forward data):
- Mirrored SHORT sleeve (W61–63): best decoupling ever (daily rho −0.003 vs P1; trades 81.5% of P1-flat
  sessions; money improvement stable in 95–100% of rolling windows) — KILLED by 2026 alone
  (−10.62 pts/session standalone 2026; trailing-24m t at 0th pctile of own history; usable weight in 0/5
  LOYO folds). Revival: trailing-24m t reverting toward its median +2.1.
- W40 vol-expansion event sleeve: stress-net +$114/wk standalone, corr +0.01 full / −0.25 inside worst-decile
  weeks, 5.7% bar overlap, N1 97th; FAILS N2 count-matched null at 92nd (needs 95th). Revival: N2 ≥95th on a
  LONGER sample (time delivers this), or a mechanism for post-2019 viability with a causal trailing threshold.
- NIGHT overnight displacement channel (W96): fails session-shift null at 88th (bar 95th; incumbent B-MOM
  clears at 100th). FACTS worth keeping: overnight SHORT is dead (−$41,741/693 trades, −$60.2 each, 34.3% win;
  B-MOM RTH short +$83,691 — the short edge is an RTH phenomenon); overnight friction $19.77/ctrRT vs P1's
  $14.52 → standing $5.25/RT tax on the whole overnight axis. Revival: ANY overnight mechanism clearing the
  session-shift null ≥95th; low rho alone does NOT revive (temporal disjointness gives rho<0.20 for free).
- Prior-session-sign stand-aside (W51b): passes worst-week nulls (98.8/99.3) but mechanism p=0.0635; revival =
  longer sample clearing 0.05, or owner objective valuing worst week.
- h2000_t750 move (W60): direction real (+4.9pp traded-day rate, 100% of windows), stopping point needs an
  out-of-sample warrant that does not exist yet.

TESTABLE NOW (revival condition is data/construction the repo already OWNS or can build at $0):
- Tick/intrabar cluster — FOUR rows name tick/intrabar info as the exact unlock:
  * W42 MAE structural stop: needs intrabar info to distinguish adverse excursions that recover from ones that
    don't (winners' median MAE 0.86 ATR ≈ stop level → stop cuts winners).
  * W54 entry-timing family: closure is on mechanism; "intrabar/tick information about the first five bars,
    which W42 showed is where the trade is decided".
  * W55 hold-duration filter: prize −15.02 pts/session in sub-37-min trades; not reachable from the object's
    own features (max |rho| 0.11); needs "order flow, DOM, or a second engine's state at the flip bar".
  * W40 sweep-and-reclaim: needs tick/DOM to see absorption (DOM PAUSED, but historical tick/BBO exports are
    explicitly allowed per DOM_PAUSE_CLEANUP_20260812 carve-out noted in scalping CAMPAIGN_STATE 2026-08-18).
  The repo OWNS L1+L2 tick/BBO 2025-08-10→2026-05-31 dev window (scalping_lab substrate/raw/NQ, 40 stratified
  sessions, 341M rows; MANIFEST.csv), never joined to these weekly_edge questions.
- W43 ES/RTY/YM: constants were re-derived, but "a per-instrument re-derivation of the SIGNAL family itself
  (VolMult set, sigma window, throttle q)" was never done. Campaign-1 echo: ES_PORTABILITY "Fitting k
  separately per instrument was NOT done"; shape travels (Spearman 0.780) but level doesn't (ES friction 2.5×
  per sigma unit).
- Multi-Osc overlap reversal as a GATE (never as engine), CumDelta as the delta gate with true tick delta,
  event-based (not clock-based) segmentation, efficiency-chop idea with realized-range estimator (estimator
  was wrong, idea right) — all listed with explicit revive conditions.

### (2) LIQREV01 dossier — research/system_master/LIQREV01_STRESS_REVERSAL/{SPEC.md,REPORT.md,src/01_liqrev01.py,out/}
Formulation (frozen, spec committed 9775c0a before run, date 2026-08-19):
- Substrate: research/scalping_lab/substrate/minute/NQ/nq1m_2005_202605.parquet (6,466,783 bars, sha256_16
  dfd017ef, 2006-01-05→2026-05-29).
- ret(d)=sess_close(d)−sess_close(d−1) in POINTS; rv5(d)=sqrt(sum sq 1-min point returns 09:30–15:58 over
  d−4..d); Stress(d)= trailing-252 pct-rank of rv5 ≥0.90; triggers from PRIOR 63 days only: LONG iff Stress and
  ret ≤q20; SHORT iff Stress and ret ≥q80; enter sess_close(d)+1 tick adverse, exit sess_close(d+1)+1 tick
  adverse; 1 NQ; $2.18/side commission (C1 total $14.36/RT).
- 8 frozen gates: N≥300; episode-block bootstrap CI_lo>0 (episodes = stress runs, gaps ≤5, 10k reps seed
  20260819); ≥5/7 named stress clusters positive {2008-09,2010,2011,2015-16,2018,2020,2022}; calm placebo NOT
  significantly positive; 3×3 plateau (stress {85,90,95} × quintile {20,25,30}) all 9 positive; tail-safety
  (top-1% ≤50% |net|, no trade >25%); losing-day corr ≤0.25 vs certified Solar B ledger; 2016–26 subperiod not
  significantly negative (+ NFP/CPI, 2-day-hold, cell-asymmetry, roll-flag reads).
Result: ALL 8 PASS on the letter. N=455 (243L/212S), net $263,646 ($579/t), episode CI [+155,+1061], both cells
positive ($552/$611), calm placebo −$43/t, matched placebo −$162/t → ~$740/trade state spread; fill-robust
(15:59/16:03/next-open keep G2); edge accrues next-day RTH ($542/t) not the gap ($51/t).
Veto reason (red team, W9-B1 precedent — letter-pass but claims refuted):
1. All statistical evidence post-2020 (pre-2020: +$12.2/t CI [−171,+187]; post-2020 $1,688/t; top-3 episodes
   64.7% of net; effective N≈5 macro events).
2. Mechanism label wrong: trailing-252 state gives ZERO stress sessions in 2009; Nagel-canonical clusters
   (2008-09, 2015-16) NEGATIVE → what passed = "vol-acceleration-gated reversal 2020–2026".
3. Engine-#3 diversification role REFUTED: profits land on Solar TOP-decile days (+$148,934 on 14 days);
   Solar bottom-decile days −$46,517; zero trades in Solar's maxDD window; combo ΔSharpe +0.18 CI [−0.32,+0.70].
4. Standalone uninvestable: 20-yr Sharpe 0.680, 7.2-year underwater 2011→2018, one trade =16% of 20y net.
Shadow status: added 2026-08-19 as second construction in research/operational/MONITOR01_SHADOW_HTFDIR01.md —
ADVANCE = forward net>0 AND forward P&L on Solar's forward LOSING days ≥0, once ≥20 forward trades; KILL =
−$10,000 accumulated, or −$10,000 on Solar losing days, or <20 trades by 2028-08. **GENESIS_PRIOR_RESEARCH_ATLAS
item 1: the shadow "was silently dropped from MONITORING_CALENDAR" — flagged there as "cheapest high-value fix
in the repo"; also notes the REGIME-LOCAL veto doctrine was later revoked by owner (post-W115: old-regime
failure is a risk classification, not a promotion veto).**
Production readiness would need: shadow restored to calendar → forward window passes ADVANCE → NEW preregistered
portfolio-role spec → NT8 executable build + parity battery. Frozen constants byte-pinned in src/01_liqrev01.py.

### (3) FOLLOW_MORNING — exact frozen object
research/weekly_edge/CURRENT_BASELINE.md §4 + runs/WE_W114_INTRAMOM + runs/WE_W116_FMADJUDICATE/REPORT.md:
- Rule: direction = sign(11:29 CLOSE − 09:31-bar OPEN i.e. the 09:30:00 print); enter at the 11:49-bar OPEN
  (the 11:48:00 print); exit at 15:44 close; size 1. END-stamped bars: 571 OPEN / 689 CLOSE / 709 OPEN / 944
  CLOSE, present on 99.4/99.3/99.3/95.8% of sessions. Bars 690–708 (11:30–11:48) verifiably unused (corruption
  probe) and cost nothing ($183 vs $179 diagnostic). Minute inherited from W108 fade spec, never selected on
  FOLLOW_MORNING outcomes → "parameter-light with a broad timing plateau", never "zero parameter".
- Standalone CONFIRMED: $179/trade, 55.00%, clears corrected best-of-15 shared-per-session-sign null at 96.3rd
  pctile (bar $166; single-cell 98.6th; effective independent cells 1.23 of 15, mean pairwise corr +0.800);
  mid-plateau 53rd; two-sided; dies only at ~18× measured spread.
- Portfolio FAILS: worst-decile overlap with book 95.8th; on book-losing weeks contributes +$66 vs chance +$842
  (9.9th pctile). Classification: CURRENT_REGIME_UNEXPLAINED, WATCHLIST. The virgin ≥2026-08-01 read is the
  scheduled decider (GENESIS_HYPOTHESIS_ATLAS H4; no new mining before it).
- Key contrast (CURRENT_BASELINE): "XM_CONFLICT diversifies the book's LOSSES. FOLLOW_MORNING diversifies its
  WINS."
- What world evidence would strengthen the prior (GENESIS_EXTERNAL_EVIDENCE item 2 + H4B result): Gao/Han/Li/
  Zhou JFE 2018 first-half-hour→last-half-hour momentum, mechanism gamma hedging + lev-ETF rebalancing
  (Baltussen JFE 2021, 16 markets), decaying OOS (Sharpe 0.39 in 2024–26 replication); "conditioning
  (volatile/high-volume/news days) is where the residual lives". BUT runs/GENESIS_H4B_LASTHALFHOUR_20260828:
  the Gao open→last-half-hour geometry is DEAD on modern NQ (slope −0.007, t −0.61); real 2006–2009 (t +3.02),
  gone by 2014. So useful world evidence must be about (a) MIDDAY-anchor / 11:48-window continuation
  specifically, (b) conditioning variables that revive intraday momentum on high-vol/news days, or (c) hedging-
  demand proxies (gamma, lev-ETF AUM) that time the effect. MOM01 (system_master) already found Baltussen-style
  diagnostic does NOT replicate on NQ — redundant with substrate state.
- Also: MIRROR_CONT (runs/WE_W120_MOMMARGINAL) passes BOTH gates FOLLOW_MORNING failed (would take book maxDD
  $11,489→$8,143; tail beta −1.861 at 0.9th pctile; only 21 weeks) — standing MIRROR_CONTINUATION_CONTROL
  required of every future fade idea.

### (4) HTFDIR01 exact role/status
research/system_master/HTFDIR01_DIRECTIONAL_TILT/REPORT.md + MONITOR01_SHADOW_HTFDIR01.md:
- ARM_LONGONLY on Product B: PASS-SCREEN on frozen gates (ΔSharpe +0.0853, G1 P=0.9556, LOYO min +0.051,
  top-10 retention 99.4%) with FOUR binding red-team corrections: 86.4% of Δnet from 2025+2026 (pre-2025-04
  P=0.585); post-dev 2026-06/07 ADVERSE both products; mechanism re-read = "conditional trim of the marginal
  short class + genuine long-side tilt value", NOT new HTF information; trimmed-short toxicity flips sign by
  regime (partly a bet on continued melt-up squeeze regimes). Product A FAILED (closed, one shot spent).
- Current role: frozen candidate in MONITOR-01 shadow (evaluation-only). ADVANCE = forward Δnet>0 AND
  day-clustered P(ΔSharpe>0) ≥0.75 AND no incumbent top-5 forward winning day retained <95%, at ≥120 forward
  sessions; KILL = Δnet ≤ −$5,000 or P<0.50 at ≥250 sessions. First reading ≥2026-11-01.
- NEVER TOUCHED: the A-side SHORTHALF channel — named in REPORT §3 as a materially different HTF hypothesis
  requiring its own preregistration.

### (5) ORB control exact definition — runs/GENESIS_BASELINES_20260828/{spec.yaml,REPORT.md}
B3: "opening-range breakout — 09:30-10:00 ET high/low; first break long/short; exit 15:59 close; one
entry/session max; no stop (canonical simple form, NO parameter search)". Cost $4.36 commission + $14.44
modelled spread/ctrRT; 239 ISO weeks 2022-01-03→2026-07-31; 1 contract.
Result: $1,043/wk net, t 2.19, maxDD $60,782, 60.3% positive weeks, worst wk −$36,829; net @ common $20,245 DD
= $347 vs incumbent P1's $1,230 (3.5×). "THIRD independent sighting of modern-era intraday continuation (after
W114's clock geometry and W118's mirror), on a formulation frozen in the spec with zero search."
A fresh ORB campaign must: (a) be a NEW preregistered hypothesis inside atlas family H4 (controls can never be
promoted from the baselines run); (b) face the portfolio-marginal gate FOLLOW_MORNING failed (contribution on
book-losing weeks vs chance-alignment null + worst-decile overlap); (c) measure P1 overlap; (d) carry a stated
mechanism for why the opening range (vs generic continuation); (e) survive the MIRROR_CONTINUATION_CONTROL
convention and the campaign's circular-shift/session-shift null machinery; (f) note prior art inside repo:
campaign-1 FB01/B01c ORB-FAILURE fade is falsified (net −$22,534 slip-1) — the fade side is dead, the
momentum side is the live one.

### (6) SolarWave recovered math — research/03_reverse_engineering/SOLARWAVE_MATH.md (+TYPE2_RECOVERY_REPORT.md)
Recovered exactly: 1-state-variable close-ratchet (S=179 ticks reversal, strict '<' flip), TrailingStop/
TrendVector rigid pair (separation always ±89t), weak/strong automaton (SlowdownScan=5 bars-no-progress,
WeakWeakSplit=10 re-arm hysteresis; support exactly [5,10]), Signal_Wave = impulse-leg counter (changes only on
flip/new-extreme; 15,925 changes verified), Type-2 = edge-triggered intrabar H/L latch beyond TrendVector
(45,825 events 0FP/0FN, RE02), signal priority rules. Open-model axes (§6): S non-constant; anchor definition;
split reverse/exit distances; wave counter interpretation.
Tested INSIDE the Solar family (frontier.yaml): H006 adaptive S (inconclusive after red team), H007 split exit
(failed), H008 anchor (redundant), H011 stop execution (failed), H014 price-proportional control (vol-specific
mechanism CONFIRMED, P=0.009), WAVE_INDEX_CONDITIONING for re-entries (failed, non-monotone), C2 Type-3 sleeve
(rejected on adaptive core), C4 Type-2 (failed −0.33 Sharpe), DC02B sigma-invariance of overshoot ratio r
(passed; r~f(theta/sigma), banded r halves yearly CV; MONITOR-01 monitors banded r).
NEVER tested AS FEATURES FOR OTHER ENGINES: the automaton state vector {weak flag, wave index, bars-since-
extreme, signed distance-from-anchor in S units, banded overshoot ratio r} exported as conditioning/gating
inputs to NON-Solar engines (XM_CONFLICT, B-MOM channel, FOLLOW_MORNING, any ORB/H4 object). W40's complement-
set model used 42 causal features on bars where Solar holds NOTHING — the state-vector-as-gate-on-OTHER-engines
direction is distinct and unrun. Cheap: solarwave.py is deterministic, no NT8 needed.

### (7) Never-executed ideas in old frontier.yaml/plans — research/frontier.yaml (closure reconciliation 2026-08-18)
- H013_ENSEMBLE_WEIGHTING: "recorded NOT RUN … 1/N stands on complexity grounds".
- SW07_MAJOR_MINOR_CONTEXT: "no individual adjudication on record anywhere in the repo" (closed as class).
- SW05 redesigned eff_120 low-path-efficiency veto: never run (class foreclosed by right-tail rule).
- SW02 catastrophe-stop half: never run in campaign 1 (superseded by campaign-3 SM02/SM03 stop frontier).
- C3/C5/C6 sleeve architectures: recorded NOT BUILT (registry/hypotheses.md Wave 3).
- ES per-instrument k fit: "Fitting k separately per instrument was NOT done" (ES_PORTABILITY).
- XSMOM cross-sectional momentum: "never tested (E1)" — GENESIS_HYPOTHESIS_ATLAS H3.
- GAMMA00 options/dealer-gamma: DATA_LIMITED, purchase not authorized (owner-gated; ACTIVE_RESEARCH_QUEUE).
- Deleted plan files: git log --diff-filter=D over *frontier*/*plan* found nothing.

### (8) Campaign-4 scalping-lab unexploited findings — research/scalping_lab/CAMPAIGN_STATE.md + artifacts
- C1 = 2.872 ticks round-trip cost hurdle (still the campaign constant; reused by ACTIONMAP01).
- Real NQ spread 2–3 ticks RTH median (1-tick only 2–7% of time) → honest market-order RT ≈3–4t; spread at
  opportunity moments 2.42t vs 1.79t control (C1 optimistic in-state; C2 mandatory).
- 16:44 flatten: E10 Flatten1644 CONFIRMED_ADOPT (net −5.35% within gate [−8%,0%], corr 0.9972, tail retention
  95.8%); v2 = live-ops default.
- Zone F formally closed §34 with RT-1's four scope conditions (regime 2025-08→2026-05 only; FSS-6
  absent-not-falsified; UNRESOLVED list carried: B1 overnight power catch-22, S2a short-side, W5-C1 mechanism
  never realized; ceiling library/clock-relative).
- Measured signal ladder (fast NQ states): micro momentum +0.2–0.6pp; single fast trigger +1–2pp; needed
  +7–10pp. Excursion surface: +32/−10 bracket needs only ~7pp conditional lift at C1.
- CLEAN_MOVE label map (W4): clean fraction 42%, path toll P(−4 before +8)=0.63, median pre-target DD 7.5t;
  clean-vs-dirty separates on DEEP contrarian pre-move (ret30 −15 vs −5), eff60, flow — NOT vol/spread. Fast-
  clock exploitation killed (W5-C1 0/24) but RT-1: "intended mechanism never realized" → unresolved. The P3
  "ONE final migration experiment" (CLEAN seed at 10–60min holds, 40–80t brackets) was superseded by Amendment
  6 restructuring; at 30–60min holds it was never run as specified.
- FSS-9 VWAP-reclaim: lift +1.3–2.9pp = campaign conditional RECORD, 3–8pp short at fast horizon; never
  re-tested at the ≥30-min friction-floor horizon.
- Only directional precursor found: CONTRARIAN 5–30s counter-move (up-opps preceded by −5t drops); kept as
  role-B reference fact.
- DR-E friction floor ~30–60min holds (reclassified PRIOR per Amendment 6, not a closure).
- 116/160 untouched pool sessions lack local BBO; rolling ~1yr server window; archival idle → OWNER_QUEUE OQ-4.

## Independence notes
- research/weekly_edge/REPO_MINING_20260825.md already mined campaigns 1/3/4/6 for #7 production candidates:
  its ranked list = (1) Type-3 warm-start [ACTED ON as WE_W31_RESTORE], (2) TOD-normalized threshold clock,
  (3) multi-clock members, (4) LIQREV01 parallel sleeve, (5) gap-rejection fade stopped variant, (6) true-range
  sigma, (7) session-target re-adjudication. Overlapping leads below are flagged.
- GENESIS_PRIOR_RESEARCH_ATLAS already ranks: LIQREV01 shadow restoration (#1), FOLLOW_MORNING (#2), mirrored
  short sleeve / W40 vol-expansion / W96 NIGHT (#3). Flagged where applicable.

## Facts deliberately NOT turned into leads
- CLOSEREV01, TOMFLOW01, ATRPOOL01, TERMFLOW: all have REPORT.md and are FAIL-closed/adjudicated (memory +
  file presence) — not leads.
- Macro surprise magnitude: N-bound (71 sessions) — closed at any price per memory.
- B-FADE 16-unseen-years +1.68t [−6.43,+9.64] below existence bar — excluded, matching REPO_MINING exclusion.
