> _Supersede note (2026-08-18): the three open-lead lines in this file are all terminally
> resolved by later waves — (1) the 1-minute VolMult-rescale R2 candidate: **1-minute Solar is
> CLOSED FOR GOOD** (SMV2AF, third independent failure); (2) SMV2Y sigma460+ER150 "policy design
> licensed": the sigma460/ER150→exposure **escalation path is EXHAUSTED**; (3) the ER150-damper
> spec was never warranted. Do not requeue any of the three from this file._

> _Supersede note (2026-08-19, ATRPOOL01): the **sigma-ESTIMATOR axis is now PERMANENTLY
> CLOSED** (ATR/range/semivariance/vol-of-vol blends — DR_V4 candidates 3/6/8). SMV2AJ's
> near-miss was re-adjudicated ONCE on the pooled 2006-2026 sample (5,269 sessions) at an
> elevated 0.90 bar per frozen spec 5db5318: P(dCDaR>0)=0.8910 < 0.90 → FAIL. Additionally,
> **instrument-level re-adjudication of ANY closed lead is exhausted program-wide** (that spec's
> §2.5, priced in advance) — this kills CLOCKHIST01-style reopenings too (SMV2W's dev
> confidence failed on its own terms). Standing prospective amendment: future R2 confidence
> gates run on the pooled dev+hist instrument from the start (dev-only CDaR power measured at
> 0.207 — see `ATRPOOL01_POOLED_READJUDICATION/out/power_audit.json`)._

## SMV2AD + SMV2AE (2026-08-08, seq 415-419) — VolMult ceiling/cohort CLOSED, 1m rescale PASS-SCREEN
- **Fixed clamp ceiling / fixed slow-cohort extension: CLOSED.** Raising the 1200t ceiling
  (tested to 2400t) and/or adding VolMult 34-50 members mechanically relieves the clamp bind
  (which reaches 39.2% of bars in Jan-May 2026, the highest of any year on file) and lifts
  Sharpe monotonically — but CDaR_0.95 worsens at every cell tested. 0/5 arms cleared the
  Sharpe-AND-CDaR-AND-95%-retention bar. Current 1200t/VMS-6-30 is a genuine Sharpe/CDaR local
  optimum, not an accident. No third bite at a FIXED-value version of this idea.
- **1-minute bars: the multiplier-rescale gap is now closed too, with a live PASS-SCREEN.**
  Every prior 1m failure (WAVE1/WAVE1C fixed-SM family; SMV2U's two VolMult-family sigma-window
  conventions) is now superseded by one further finding: rescaling VolMult itself by the
  measured 3m/1m sigma-scale ratio (R=1.7301, stable 1.72-1.74 across 5 years) flips the
  time-matched 1m arm from net -$3,163/Sharpe -0.018 to net $77,748/Sharpe 0.439, friction
  share 1.02→0.47. Still trails the 3m incumbent (Sharpe 0.709) and has NOT been through
  bootstrap/LOYO/old-regime/portfolio testing — queued as an R2_CONFIRMATION candidate, not
  adopted. This is the first time any 1-minute construction has cleared a bare economic-
  viability screen in this program's history.
- **Mechanism-expansion pass** ranked a genuinely different, not-yet-tested idea #1: an
  ADAPTIVE (percentile/rolling) clamp ceiling, distinct from the now-closed FIXED-ceiling test
  above — plugs into the same `resolve_s()` `hi` bound but recomputed from the recent
  distribution of `k*sigma` rather than a constant. Ranked #2: volume bars as a new clock
  (distinct from the 3x-killed fixed-time-bar family). Full 9-candidate ranked list:
  `deep_research/DR_V4_SOLARCORE_EXPANSION_20260808.md`.

## SMV2G (2026-08-08): HTF mechanism plateau — CONFIRMED (7/8 neighbors improve)
Identical x1.25 tilt through 8 alternative daily HTF-state definitions (SMA20/100,
EMA50, Donchian50-mid, ret50/ret100 sign, SMA50-slope, dual SMA50&200): 7/8 improve
Sharpe (+0.016..+0.097; only ret50 flat at -0.006). SM08's SMA50 (+0.072) is mid-pack,
not the argmax (SMA20 +0.097) - the effect is the MECHANISM (long-horizon directional
agreement), not a fitted cell. Deployed form stays SMA50. Gate >=6/8: PASS.
Seq 335-342; runs/SMV2G_HTF_MECHANISM/out/results.csv.

## SMV2J JOB1 harness (2026-08-08, seq 366-367) — VR and ER KILLED
Variance ratio (9 cells) and Kaufman ER (3 cells) vs next-session SOLAR_DUAL_HTF PnL with
sigma460 + HTF controls: 0/12 cells reach |t_NW|>2; plateau criterion fails badly (rel-range
3.6-5.4 vs <0.30); states are orthogonal to deployed controls (|corr| ≤ 0.14) so this is a
genuine no-signal result, not collinearity. Old regime: zero sign reversals (8 same-sign, 4
flat). The DR-prior "H1/H3 cluster" was not borne out (corr 0.18). Red-team CONFIRMED.
Queue advances per DR pass B sequencing: B-H2 Kalman innovation whiteness + B-H4 BOCPD regime
age are the next JOB1 candidates (separate frozen spec).

## SMV2O + SMV2R state/indicator verdicts (2026-08-08)
- Kalman innovation whiteness (9 cells) KILLED; BOCPD regime age (3 cells) KILLED. With VR/ER
  (SMV2J), the ENTIRE ranked DSP JOB1 slate is now dead — none of the four external
  trend-quality axes adds information beyond sigma460 + HTF on this system.
- T2/T3 Solar signal layers: KILLED (zero incremental info conditional on positioned ensemble).
- MA30/59 (owner's question): KILLED in all four jobs — hard confirmation costs 22% of net and
  6.2% of the right tail; pure lag. The four-job harness is reusable for any future state.
- SURVIVING HYPOTHESIS (not policy): ER150-top-tercile agreement predicts LOWER next-day E10
  PnL (-$206/sd, t_NW=-3.27, HTF-controlled) — a DAMPER direction (over-extended efficiency
  mean-reverts). Needs its own frozen spec before any read is acted on.
- Clamp architecture: 40t floor irrelevant; 1200t cap ACTIVELY binds slow members (vm30 10.9%
  of dev bars; partial-2026 highest at 39.2%) — it is a live regularizer, and its binding rate
  is itself a candidate vol-regime state.
- Vol memory: 460 = CONFIRMED PLATEAU (230 destructive, 920 equivalent). Owner Q4 answered.
- Cohorts: SLOW load-bearing; FAST (vm6-12) = REMOVABLE-CANDIDATE (Sharpe 0.768 vs 0.709,
  churn halved, top-10 105.9%) pending R2 confirmation — the single live Solar-core lead.

## SMV2T (seq 389) — FAST-cohort removal lead CLOSED
The one live Solar-core lead from SMV2R failed R2 confirmation under the SAME 0.85-confidence
bootstrap bar applied to every one-contract challenger: dev P(dSharpe>0)=0.80, P(dCDaR>0)=0.39
(both <0.85); old-regime net gap −$16.7k breaches the −$10k non-inferiority floor; at the
portfolio level the removal actually WORSENS CDaR by $1,653 (dSharpe positive but small). Wins
10/16 old-regime years on net (corrected from an initial mis-cite of 9; red-team caught it).
13-member incumbent RETAINED. Pattern now seen twice (also SMV2S one-contract): point estimates
favor the challenger but 4.4y of daily data cannot deliver 0.85 confidence for risk-shaped
improvements of this size — a standing statistical-power caveat for this program's gate design.

## SMV2U clock challenge (seq 390-392) — 3m incumbent survives 1m/5m bar-matched; 5m
## time-matched earns R2 confirmation (SMV2W, frozen)
1m clock (both memory conventions) fails decisively: friction consumes 102-128% of gross PnL —
NQ 1m is not tradeable for this ensemble after realistic costs. 5m bar-matched (mechanism-
neighbor memory) shows a standalone edge (Sharpe 0.728 vs 0.709) that does NOT survive to the
portfolio level and has fragile chronology (LOYO 3/5). 5m time-matched (VolPeriod=276 bars ≈
23h, matching the INCUMBENT's memory in wall-clock time rather than bar count) beats the
incumbent on every axis tested — standalone, portfolio, LOYO, AND with lower turnover — and
earns the program's first genuine R2-confirmation-worthy Solar-core clock challenger. Framed
correctly per V4.1 §20: until SMV2W resolves, the object is CURRENT ROBUST SOLAR INCUMBENT
(3m), not yet displaced.

## SMV2W (seq 395) — 5m time-matched clock lead CLOSED; Solar core survives 5/5 challenges
The strongest core-level challenger the program has produced (screening: standalone Sharpe
0.793 vs 0.709, portfolio Sharpe 1.156 vs 1.120, LOYO 5/5, lower turnover) failed the SAME
0.85-confidence bootstrap bar and 4/5-year LOYO bar applied to every other challenger:
P(dSharpe>0)=0.642, P(dCDaR>0)=0.549, LOYO only 3/5. Old-regime confirmation was structurally
BLOCKED (5m bars are not derivable from the committed 3m-only hist substrate) rather than run
around — a genuine data-coverage limit, disclosed as such. Point estimates still favor the
challenger (net $152.7k vs $138.3k on the raw core); the pattern seen three times now (FAST-
cohort, A-dominant/HTF-gated one-lot families, now the 5m clock) is that ~4.4 years of daily
data cannot deliver 0.85 confidence for risk-shaped improvements of this size, even when every
point estimate is favorable. 3m remains CURRENT ROBUST SOLAR INCUMBENT, having now survived
five independent challenges (memory 460, cohort structure, MA30/59, T2/T3 signal layers,
clock) — the language upgrade from "untested baseline" to "repeatedly re-earned incumbent" is
now justified per V4.1 §20.

## SMV2Y (seq 399-402) — FIRST VIABILITY STATE TO PASS: sigma460 + ER150 predict next-WEEK
## downside (V4 s21 causal edge-viability state)
After 16/16 state cells failed against the next-session-Solar-PnL target (VR, ER, Kalman
whiteness, BOCPD across SMV2J/O), the SAME sigma460 and ER150 series pass cleanly against a
DIFFERENT target: next-week champion portfolio downside. t_NW=-2.297 (sigma460) / -3.047
(ER150), bootstrap same-sign 0.990/0.998, monotonic quintiles (1 inversion each, within the
4/5 tolerance), same-sign on an E10-only old-regime proxy (t=-7.13/-3.14). Cluster rule did
NOT fire (corr=-0.036) -- both stand independently as candidate viability-state inputs.
Flip-rate and VR both fail on this new target too (VR now 0/12 cells across two different
targets). OPEN QUESTION (INFERENCE, not yet explained): ER150's FORWARD relationship (high
efficiency this week -> worse downside next week) is opposite-signed from SMV2Q's CONCURRENT
finding (joint-loss weeks have LOW ER150 while they are happening) -- plausibly an
exhaustion/mean-reversion pattern (a clean trending week gets followed by a rougher one), but
unproven mechanistically. NEXT STEP (not yet run): a bounded 0/0.5/1 exposure-reduction policy
gated on these two states ahead of high-predicted-downside weeks, per V4 s21's own escalation
order -- diagnostic passed, policy design is now licensed.
