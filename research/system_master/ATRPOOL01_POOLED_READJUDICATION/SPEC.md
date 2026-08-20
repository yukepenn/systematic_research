# ATRPOOL01 — One-time pooled full-history re-adjudication of SMV2AJ arm_BLEND_75

**Status: FROZEN before any pooled statistic is computed. Run class: PROTECTED_CONFIRMATION.**
**Alpha budget: 1 of 2 for wave 2026-08-20. One shot; no variant, no re-run, no constant change.**

## 1. What this is and is not

SMV2AJ (spec 8c030f8) closed the ATR-blend lead (`arm_BLEND_75`: sigma = 0.75·sigma460 +
0.25·ATR460/R, R_ATR_SELECTED = 2.025539235146222, frozen from SMV2AI) with 4 of 5 gates
passing on real margin (chronology 4/5 LOYO improving into recent years; old-regime 2006-2021
net gap **+$86,004** with maxDD ratio 0.864; right-tail retention 100.14%; portfolio rebuild
dSharpe +0.0328 / dCDaR +$318 both positive) and exactly one failing prong: the dev-window
(1,139-session) paired-MBB CDaR confidence, P(dCDaR>0) = 0.7529 < 0.85, while the Sharpe prong
passed at 0.9316.

This spec does **not** re-tune anything (SMV2AJ's own closure clause bans a re-test "of the
same blend at a different weight" — no weight, window, or constant changes here; every number
is reused verbatim). It changes exactly one thing: the **adjudication instrument** — from the
dev-only 1,139-session bootstrap to the pooled 5,269-session (2006-2026-05) bootstrap over the
SAME two committed daily curves SMV2AJ itself produced and red-team-verified
(`runs/SMV2AJ_ATR_BLEND_R2/out/curves.csv` + `out/gate_C_hist_curves.csv`). No simulator runs;
no new data; the readout is pure arithmetic on already-committed, already-published artifacts.

## 2. Why reopening is legitimate here (governance)

1. **Documented repeated instrument pathology.** Four independent R2 closures (SMV2T
   FAST-cohort, SMV2H2 one-lot, SMV2W 5m clock, SMV2AJ ATR blend) share the identical failure
   signature the program itself recorded as a standing caveat each time: *"~4.4y of daily data
   cannot deliver 0.85 confidence for risk-shaped improvements of this size, even when every
   point estimate is favorable."* That is a property of the instrument, not of the candidates.
2. **Quantified, not rhetorical**: the pre-freeze power audit
   (`out/power_audit.json`, instrumentation, zero alpha budget, computed WITHOUT touching any
   hist curve value) measures the dev-only CDaR prong's power to detect an effect exactly as
   large as the dev point estimate. Results are pasted in §5 below before freeze.
3. **The second look is priced**: both prongs elevated 0.85 → **0.90**.
4. **The ceiling is the shadow ledger, not promotion**: a full pass earns exactly what
   HTFDIR01/LIQREV01 earned — an evaluation-only forward construction adjudicated by virgin
   data at MONITOR-01 reads. No baseline changes on re-adjudicated historical evidence, ever.
5. **Failure is priced harder than the original closure**: ANY gate failing permanently closes
   the entire sigma-ESTIMATOR axis (ATR/range/semivariance/vol-of-vol blends as a class,
   DR_V4 candidates 3/6/8), and — win or lose — **no closed lead may ever again be
   re-adjudicated by instrument change**; this is the one-time transitional case that
   establishes the pooled instrument prospectively.
6. **Prospective amendment**: every future R2 confirmation must run its confidence gate on the
   pooled (dev+hist) instrument from the start wherever a hist substrate exists.
7. Distinguish from SMV2T/SMV2H2: those failed old-regime **outright** (net-gap floor
   breaches) — they are NOT power casualties and remain closed regardless of this result.
   SMV2AJ is the only closure whose every era-level point estimate favored the challenger.

## 3. Data (all committed, none new)

- Dev pair: `runs/SMV2AJ_ATR_BLEND_R2/out/curves.csv` — 1,139 sessions 2022-01-03..2026-05-29,
  columns DUAL_CONTROL / DUAL_BLEND75 (daily $, DUAL-transformed decision objects).
- Hist pair: `runs/SMV2AJ_ATR_BLEND_R2/out/gate_C_hist_curves.csv` — 4,130 sessions
  2006-01-05..2021-12-31, same two objects on the SM06 hist substrate.
- Pooled series: hist then dev, chronological, n = 5,269.
- LOCKED_FORWARD untouched (both artifacts end 2026-05-29; seal boundary 2026-08-01).

## 4. Gates (ALL AND-required; constants frozen here)

- **G0 integrity**: the 8 published endpoint numbers reproduce exactly from the artifacts
  (dev nets 138,280.0 / 144,815.2; hist nets 447,134.7 / 533,138.9; Sharpes 0.8992 / 0.9431 /
  0.2945 / 0.3504; hist maxDDs 246,834.0 / 213,326.8; tolerance ±$0.1 / ±0.0001).
- **G1 pooled confidence (primary)**: paired circular MBB, block=5, B=10,000, seed=20260820,
  on the pooled 5,269-session pair; battery verbatim from `SMV2AJ/src/gate_A.py`
  (Sharpe = mean/std·√252; CDaR5 with k = int(0.05·n) = 263).
  Require **P(dSharpe>0) ≥ 0.90 AND P(dCDaR5>0) ≥ 0.90**.
- **G2 era consistency**: the same paired MBB run within each era separately
  (dev-only n=1,139 — its P(dCDaR>0)=0.7529 is already published and will reproduce;
  hist-only n=4,130). Require: both eras' point dSharpe > 0 AND both eras' P(dCDaR>0) ≥ 0.55
  (direction-consistency floor, not significance).
- **G3-SPLIT (standing rule)**: split the pooled daily diff series at 2020-01-01.
  Require: both sub-era mean diffs > 0; iid bootstrap (B=10,000, seed=20260820) 95% CI on each
  sub-era mean: at least one CI_lo > 0 and neither CI_hi < 0.
- **G4 pooled right-tail retention**: challenger's summed PnL on the control's top-10 pooled
  days ≥ 0.95 × control's own top-10 sum (program's standing retention floor; the dev-only
  version already passed at 1.0014 against a ≥1.00 bar).
- **G5 both-conventions check**: stratified pooled bootstrap (blocks resampled within each era
  independently, era lengths preserved, concatenated; same B/seed/battery). Require both
  prongs ≥ 0.85 under this second convention. If G1 and G5 disagree in pass/fail direction,
  the overall verdict is **INCONCLUSIVE = FAIL** (no cherry-picking the convention).

## 5. Power audit (run before freeze; `out/power_audit.json`, seed 20260820, 300 outer × 2,000 inner)

DGP = circular block-5 bootstrap of the SMV2AJ dev pair itself (i.e., true effect = the dev
point estimate; no hist curve values touched, only the published hist row count):

| instrument | CDaR-prong power at 0.85 | Sharpe-prong power at 0.85 | median simulated P(dCDaR) |
|---|---:|---:|---:|
| dev-only, n=1,139 (SMV2AJ's) | **0.207** | 0.680 | **0.7533** |
| pooled, n=5,269 (this spec's) | 0.617 | 0.967 | 0.8725 |

Reading: if the ATR-blend tail effect is real at exactly the size dev showed, SMV2AJ's
instrument confirms it only ~21% of the time — and the median P it produces is 0.7533,
statistically indistinguishable from the 0.7529 actually observed. The observed "failure" is
the CENTRAL outcome of an underpowered instrument applied to a true effect. This quantifies
§2.1's standing caveat. Note the elevated 0.90 bar makes even the pooled instrument
conservative under dev-like dynamics — a pass is highly informative; a fail is priced as
permanent closure and accepted in advance.

## 6. Decision rule (frozen)

- **ALL of G0-G5 pass** → `arm_BLEND_75` becomes **SHADOW CONSTRUCTION #3** in
  `research/operational/MONITOR01_SHADOW_HTFDIR01.md` (amendment appended, evaluation-only):
  - ADVANCE: at ≥2 consecutive MONITOR-01 reads on virgin forward data (≥2026-08-01, fresh
    3m export with H/L required), forward Δnet(BLEND75−CONTROL) > 0 AND forward dSharpe > 0.
  - KILL: cumulative forward Δnet ≤ −$5,000, or forward CDaR5 ≥ 1.20× control's over ≥120
    forward sessions.
  - No NT8 build, no promotion step, no baseline change until ADVANCE fires AND a separately
    preregistered promotion battery passes.
- **ANY gate fails** → sigma-estimator axis (ATR/range/semivariance/vol-of-vol blends)
  **PERMANENTLY CLOSED**; standing protocol note recorded that instrument-level
  re-adjudication of closed leads is exhausted program-wide.

## 7. Honest prior / predictions (written before the readout)

- The pooled Sharpe prong is expected to pass: both eras' point dSharpe are already published
  positive (+0.0439 dev, +0.0559 hist), and pooling only adds power to an effect present in
  both eras. This prong is NOT the test's bite.
- The bite is CDaR: the pooled CDaR5 (k=263) is dominated by hist-era drawdowns (hist maxDD
  ≈6× dev's). Published hist maxDD favors the challenger (0.864 ratio), but maxDD ≠ CDaR and
  the hist-era CDaR delta has never been computed. If the challenger's tail improvement is
  regime-local to dev, G2's hist floor (0.55) and/or G1's 0.90 fail and the axis closes — a
  decisive, cheap null. If the tail improvement is era-stable, this is the first Solar-core
  mechanism improvement in program history to clear a harder bar than the one that closed it.
- Either outcome is the deliverable. Estimated cost: one afternoon, zero new simulation.
