# CROSS-ASSET WAVE 1 — SYNTHESIS (ES / RTY / YM / ZB vs the live NQ book)

**Run:** `runs/CROSSASSET_W1_SYNTHESIS_20260906/`
**Type:** DESCRIPTIVE SCIENCE — a market autopsy synthesis. **NOT a falsifiable test.**
No ledger trial, no strategy, no P&L, no promotion. Evidence status: **DISCOVERY_CONSUMED**.
Every number below is a *description* of the four sealed substrates, not a verified edge.
**All figures are POINTS basis** (per DELEV01); rho is scale-invariant so the point-basis
rho equals the dollar-basis rho.

**Inputs (four completed autopsies, all substrates end 2026-07-31, seal-clean, 0 rows hard-dropped ≥2026-08-01):**
- `runs/CROSSASSET_W1_ES_AUTOPSY_20260906/`  (ES, $50/pt, tick 0.25)
- `runs/CROSSASSET_W1_RTY_AUTOPSY_20260906/` (RTY, $50/pt)
- `runs/CROSSASSET_W1_YM_AUTOPSY_20260906/`  (YM, $5/pt)
- `runs/CROSSASSET_W1_ZB_AUTOPSY_20260906/`  (ZB, $31.25/tick)

Out of scope: a fifth autopsy `CROSSASSET_W1_CL_AUTOPSY_20260906/` exists in `runs/` but was
not handed to this synthesis; it is not covered here.

---

## 1. How the four markets differ from NQ, and from each other

### The single load-bearing result
**NQ is the momentum/continuation outlier. Every one of the four markets we autopsied is
MORE MEAN-REVERTING than NQ, at every scale we measured.** On NQ the fade graveyard closed
because *continuation* won (VR>1, big moves continue). On ES/RTY/YM/ZB the variance ratios sit
below 1 and large moves reverse. This is the structural fact that makes the complex interesting:
the natural orthogonal complement to a long-only NQ momentum book is a mean-reversion mechanism,
and one exists **natively in all four markets**. The open question is purely whether any survives
friction + the graveyard's unconditional controls.

| | NQ (incumbent) | ES | RTY | YM | ZB |
|---|---|---|---|---|---|
| Asset class | equity-index (tech/growth) | equity-index (broad/SPX) | equity-index (small-cap) | equity-index (blue-chip/cyclical) | **rates (30y duration)** |
| ρ to NQ (daily c2c, pt) | 1.00 | **0.94** | **0.75** | **0.74** | **0.06** |
| Return dependence | continuation (VR>1) | daily MR VR(10)=0.75 | daily MR VR(20)=0.80 | MR every scale VR(5)=0.77 | **MR every horizon VR(60)=0.65** |
| Big-move next step | continues | reverses | ~random | **reverses −15.4pt** | **reverses −0.007pt** |
| Where drift lives | (momentum) | ~50/50 RTH/ON, neither sig. | **~all overnight** | **RTH-only (+10.18/sess)** | none (cc −0.019, t −0.69) |
| Daily skew / tail | fat LEFT tail | skew +0.68 (big days UP), exkurt 15.4 | skew +0.03, exkurt +1.47 | skew +0.10 (near-symmetric) | **skew −0.09, THIN tails (1.07× Gaussian)** |
| Vol forecastability (daily RV acf1) | — | 0.69 | 0.595 | 0.72 | 0.58 |
| Path ER (median) | ~0.053 | 0.050 | 0.050 | 0.047 | **0.043 (choppiest)** |
| Coil→expansion | — | refuted (0.92×) | refuted (backwards) | — | refuted (0.84×) |

### What is UNIVERSAL across all four (and mostly NQ too)
- **Returns are near-unforecastable intraday; volatility is highly forecastable.** 1-min VR≈1.00
  and 1-min return ACF≈0 in every market; daily RV autocorrelation 0.58–0.72 is the single most
  persistent structure everywhere. If anything is tradeable in this complex it is a *variance*
  handle, not a return-timing handle.
- **Paths are extremely choppy.** Kaufman ER median 0.043–0.050, tortuosity ~20–23× in all four.
  Liquidity-provision / mean-reversion signature, not trending.
- **Compression does NOT precede expansion.** The coil→breakout story is refuted (weakly on ES,
  backwards on RTY, refuted on ZB). Any Wave-2 vol hypothesis must pre-register the sign as
  *compressed→compressed* so a coil-breakout reading is falsified by construction.
- **Gaps fill near random-walk rates** (57–66%), so any gap-fade claim must beat a matched
  unconditional gap-fill geometry control (WE_W111b), not an unconditional bar.

### What is ASSET-CLASS-specific (equity-index quartet) vs MARKET-NATIVE
- **Equity-class shared:** classic CME 18:00→17:00 ET clock with a strict 17:00–18:00 halt;
  09:30–16:00 RTH carries 72–80% of volume in ~28% of bars; open/close volume double-hump;
  RTH sweeps ≥1 overnight extreme most sessions. ES/RTY/YM are variations on one template.
- **NQ-vs-equity-siblings:** NQ's continuation and fat LEFT tail are *not* shared — ES is
  right-skewed in RTH (big days are UP days), YM and RTY are near-symmetric. NQ's crash-geometry
  is idiosyncratic to tech-growth.
- **ES:** deepest, most-hedged index; the landing zone for the 0DTE-SPX options complex and
  passive/overnight risk transfer; strongest measured gap-fade (E[RTH|gap-dn]=+3.14,
  E[RTH|gap-up]=−1.15); overnight is NOT quiet (ON range ≈ RTH range, ratio 1.02).
- **RTY:** small-cap; drift lives almost entirely overnight; overnight is the fat-tail carrier
  (ON exkurt +5.51); carries the book's ONE calendar-fixed mechanical flow event — Russell
  reconstitution.
- **YM:** price-weighted blue-chip/cyclical; a handful of high-price names (UNH/GS/MSFT/HD)
  dominate, so single-name gaps over-extend and revert — this is *why* YM is the most
  mean-reverting equity index (VR(5)=0.77 vs NQ 0.88, signed-continuation −15.4pt). Its
  non-NQ variance is the value/growth/cyclical-vs-tech rotation.
- **ZB:** the odd one out entirely — a genuine near-24h **rates** market on an **08:00–16:00 ET**
  native session (90 min earlier than NQ), European window ~15% of volume, tiny gaps
  (|gap|/RTH-range 0.35), THIN tails, and the highest-vol minutes clustered at the **08:30 ET
  scheduled-data release**. Mean-reverting at *every* horizon and essentially uncorrelated to NQ.

---

## 2. Diversification read

### ρ-to-NQ per instrument (daily close-to-close, POINTS basis; scale-invariant)
| Instrument | Pearson ρ | Read |
|---|---|---|
| **ES** | **0.94** (RTH 0.940, ON-gap 0.945, by-yr 0.907–0.964) | **same equity-index direction factor as NQ** |
| **RTY** | **0.75** (by-yr 0.600–0.906) | strong co-move |
| **YM**  | **0.74** (RTH o→c 0.7534; by-yr 0.57–0.88) | strong co-move |
| **ZB**  | **0.06** (Pearson 0.064, Spearman 0.091; P(opp sign) 45.4%; by-yr −0.069…+0.255) | **~orthogonal** |

### Best a-priori diversifier: **ZB, unambiguously.**
ρ=0.06 to the live NQ book. Under the campaign's orthogonality-is-first-class doctrine, even a
modest-Sharpe ZB engine carries real marginal portfolio value against NQ — and ZB is *also* the
market with the strongest and cleanest native mean-reversion and the sharpest scheduled-vol
structure. It is the prize on two axes at once (orthogonality **and** signal), which is rare.

### The equity-index correlation cap (state it plainly)
**The three equity indices' high NQ-correlation caps their portfolio value.** A long-biased,
directional ES/RTY/YM sleeve co-moves heavily with the NQ book — ES shares ~88% of variance,
RTY/YM ~56% — so as *directional beta* they add almost nothing to a book that is already long-only
NQ momentum. **Do not spend Wave-2 budget on a directional equity-index sleeve.**

Two further cautions that sharpen the cap:
- **The equity correlations TIGHTEN in stress.** RTY 2022 +0.906, YM 2022 +0.88, ES 2022 &
  2025 +0.964 — precisely the years you would want the diversification, the equity ρ converges.
  Equity-index diversification is a fair-weather friend; it can vanish inside a drawdown.
- **Raw index ρ caps a DIRECTIONAL sleeve, not every mechanism.** Two escape hatches remain, and
  they are the *only* legitimate equity-index spends:
  1. **Point-hedged residual (orthogonal BY CONSTRUCTION).** A points-regression-hedged residual
     `e = X_pt − β·NQ_pt` has ~0 index beta by construction — the one family that structurally
     defeats ρ=0.94. Applies to ES and YM.
  2. **Sign-opposite mean-reversion (orthogonal by SIGN + underwater curve).** A *contrarian*
     equity-index MR engine's underwater curve can anti-correlate with NQ's momentum P1 (the
     XM_CONFLICT −0.165 underwater-corr template), even at high raw ρ. But this must be *proven*
     on the underwater curve; raw ρ alone caps it. The true portfolio verdict belongs to eventual
     engines' underwater-curve correlation, not the raw index ρ quoted above.

---

## 3. Descriptive cells proposed for `research/cross_asset/MECHANISM_TRANSFER_MATRIX.md`

⚠️ **Governance note.** The matrix header binds cells to *verified experiments* with a run+ledger
trial, and its glyph legend (✅/✗/?) encodes **edge verdicts**. An autopsy is **DISCOVERY_CONSUMED
description, not a verified edge** — so these must be transcribed as **descriptive annotations
(prefix `desc:` + run cite)**, explicitly *NOT* as ✅ marks. I cannot write the matrix myself
(it is outside this run dir and the write requires the owner's §30 directive). Proposed cell
contents for the owner to transcribe follow; each is descriptive-only with its autopsy cite.

**`session / auction structure` row (descriptive):**
- **ES:** `desc: ON-touch hi 52.5%/lo 49.3%, inside-ON 16.6%; gap-fill 62.5% (≈RW); PDH 55.4%/PDL 46.4%; OR15 holds day-high 17.6% [CROSSASSET_W1_ES_AUTOPSY_20260906/out/session.txt]`
- **RTY:** `desc: runs ≥1 ON extreme 94% (hi 60.1/lo 60.8/both 26.7/neither 5.7); OR≈50.7% of RTH range, stays-inside-OR 0.9%; gap-fill 60–64%; PDH 50.4/PDL 49.7 [CROSSASSET_W1_RTY_AUTOPSY_20260906/out/session.txt]`
- **YM:** `desc: sweeps ON hi 69/lo 65/both 36/neither 2%; PDH 52/PDL 48; OR30 up 69/dn 70/both 40 (whipsaw); gap-fill 65.7%; close-loc 0.566 [CROSSASSET_W1_YM_AUTOPSY_20260906/out/session.txt]`
- **ZB:** `desc: NOT an OR market (OR holds extreme 21%, rest-of-day breaks OR 78–79%); ON hi 48.7/lo 52.7; gap-fill 57–58%; PDH 47.3/PDL 51.3; inside-PD-range 11.5% [CROSSASSET_W1_ZB_AUTOPSY_20260906/out/session.txt]`

**Dependence (descriptive — annotate on the `mean reversion` / `trend / momentum persistence` rows; NQ is the continuation reference):**
- **ES:** `desc: intraday 1-min martingale (VR≈1.00 q2–60, sign-persist 49.0%); DAILY MEAN-REVERTS acf(1)=−0.103, VR(2)0.90/VR(5)0.80/VR(10)0.75; vol forecastable RV acf(1)=0.69 [CROSSASSET_W1_ES_AUTOPSY_20260906/out/dependence.txt]`
- **RTY:** `desc: returns unforecastable (daily acf(1)=−0.016, 1-min VR≈1.00); daily VR(2)0.99→VR(20)0.80, RTH→RTH VR→0.72; vol clusters RV acf(1)=0.595, range acf 0.417 [CROSSASSET_W1_RTY_AUTOPSY_20260906/out/dependence.txt]`
- **YM:** `desc: MR at every scale, MORE than NQ — daily VR(5)=0.77 (NQ 0.88), 1-min VR(30)=0.96 (NQ 0.99), daily acf(1)=−0.10; big prior moves REVERSE (top tercile signed-cont −15.4pt); daily RV acf 0.72 [CROSSASSET_W1_YM_AUTOPSY_20260906/out/dependence.txt]`
- **ZB:** `desc: MR at EVERY horizon — intraday VR(2/10/60)=0.85/0.70/0.65, daily VR(2/10/20)=0.98/0.89/0.86; 1-min acf(1)=−0.146 (partly bid-ask bounce); big move → reversal (−0.007pt); daily RV acf 0.58→0.19. OPPOSITE NQ [CROSSASSET_W1_ZB_AUTOPSY_20260906/out/dependence.txt]`

**`path organization (ER/entropy)` row (descriptive):**
- **ES:** `desc: ER median 0.050 (mean 0.058), tortuosity ~20; MFE≈MAE (23/23, ratio 1.02); range clusters acf(1)=0.557 but NR7 does NOT precede expansion (next-day 0.92×) [CROSSASSET_W1_ES_AUTOPSY_20260906/out/path.txt]`
- **RTY:** `desc: ER mean 0.057/med 0.050, tortuosity ~19.9, path 305pt for 14.6pt net; up-day MFE 23.8 vs heat 7.1 (heat/target 0.30); compression persists (next-day 30.3 vs 39.9) [CROSSASSET_W1_RTY_AUTOPSY_20260906/out/path.txt]`
- **YM:** `desc: ER median 0.047, tortuosity ~21; MFE/MAE symmetric (up 177/dn 178); RTH-range acf(1)=0.52; OR30 ~45% of RTH range [CROSSASSET_W1_YM_AUTOPSY_20260906/out/path.txt]`
- **ZB:** `desc: ER median 0.043, tortuosity ~23 (choppiest of the four); MFE/MAE symmetric; net move 0.49× range; NR7 coil→break REFUTED (bottom-quartile→0.84× vs top-quartile→1.18×) [CROSSASSET_W1_ZB_AUTOPSY_20260906/out/path.txt]`

**ρ-to-NQ (descriptive, for the header note or `cross-asset / relative state` descriptive layer):**
`desc: daily-c2c pt ρ(NQ): ES 0.94, RTY 0.75, YM 0.74, ZB 0.06 [respective /out/*correlation*.txt]`.
The `cross-asset / relative state` **edge** cells for ES-NQ / YM-NQ residuals remain `?`
(untested) — the residual-MR hypotheses in §4 are Wave-2 candidates, not descriptive facts.

---

## 4. Ranked Wave-2 plan — preregisterable NATIVE mechanism hypotheses

Each is a **hypothesis to preregister**, not a strategy. All carry a points-basis cost band
(mandatory), an MDE-before-looking rule where N is small, a circular-shift null that preserves
dependence, and a matched **unconditional** control for any class-conditional claim. Families are
consolidated so we do not pay twice for one mechanism across correlated equity indices.

### TIER 1 — Orthogonal + native + powered (ZB). Spend here first.

**W2-ZB-MACRO — Scheduled-macro-release volatility/path structure at 08:30 ET.**
- Instrument: **ZB** (+ optional ZN confirm later). ρ_NQ=0.06.
- Mechanism: ZB is THE duration instrument; 08:30 ET rates data (plus 10:00 ISM/JOLTS, 14:00 FOMC)
  discretely reprices the curve. The volume/vol profile *shows* 08:30 minutes are the
  highest-vol minutes and the 08:00 hour runs ~2× any overnight hour. A vol-transition / event-path
  family on a pre-announced calendar — **not a directional macro bet.**
- Cheapest falsifier: powered RV(points) in the 08:30–09:00 window on release days vs matched
  non-release days, **MDE printed first**; then post-release continuation-vs-reversion net of the
  ~2-tick cost band.
- Cost basis: **points-RV, ~2-tick (~$62.50) round-trip band**, EVIDENCE=FORWARD-on-preregister.
- FAILURE_MEMORY: differs from G2_F12 (NQ FOMC 14:05–15:30 vol×5.66 — different instrument /
  observable / time); NOT GENESIS_H2 / G2_F1_TICK01 (calendar-type→mean NULL; this is vol/path,
  not a mean-by-calendar bet); NOT G2_F10 (overnight HOLD into NFP/CPI absent premium; this is
  ZB *intraday reaction*). Power ~50–100 release days/yr — genuinely powered, NOT N-bound like
  FOMC's ~8.

**W2-ZB-VOLSTATE — ZB own forward-vol as RISK SPECIFICATION / regime layer.**
- Instrument: **ZB**. ρ_NQ=0.06.
- Mechanism: daily RV autocorrelation 0.58→0.19 is the surest phenomenon in the ZB autopsy. Used
  as a sizing/regime-routing denominator, explicitly **NOT** standalone alpha.
- Cheapest falsifier: HAR-RV on ZB points-RV must beat a random-walk RV forecast OOS on
  QLIKE/DM > MDE; any sizing overlay must clear the **rate-matched random-thinning placebo**
  (eval_battery, weekly-vol led) or it is thinning not information — KILL. Pre-register
  compression sign as compressed→compressed.
- Cost basis: **points-RV (DELEV01)**; classified RISK SPECIFICATION, never information alpha.
- FAILURE_MEMORY: distinct target from **G2_F13** (that predicted NQ from ZB and FAILED; this is
  ZB's OWN forward vol); avoid **G2_F11** collinearity trap (use multi-horizon HAR, never
  fixed-window diurnal deseasonalization, VIF 92.9); must beat **G2_F3_VOLSIZE01** (extremes-only
  vol-sizing FAILED, tail-only below null) by being a DD/risk transform, not a growth timer.

### TIER 2 — Orthogonal BY CONSTRUCTION (equity residual). The only structural defeat of ρ=0.94.

**W2-EQ-RESID — Equity-index-vs-NQ point-hedged residual mean-reversion (lead ES, extend to YM only if ES clears).**
- Instrument: **ES** first (deepest, tightest, cleanest residual), **YM** as confirming cross-check.
  Both are ~0 index-beta by construction.
- Mechanism: the ~6% ES residual (value/broad-vs-growth dispersion, tech rate-sensitivity) and the
  ~44% YM residual (value/growth/cyclical vs tech rotation) are distinct priced factors. A
  points-regression-hedged residual `e = X_pt − β·NQ_pt` is orthogonal-to-NQ by construction — the
  campaign's stated prize.
- Cheapest falsifier: fit point-hedge β on a dev window (strict chronology), test daily residual
  ACF / half-life / VR(2..5) at ONE preregistered horizon vs a circular-shift null AND a matched
  unconditional raw-index-MR control. KILL if inside the **TWO-leg friction band** or half-life
  ≤1 bar (already arbitraged) or residual VR≈1/ACF≈0.
- Cost basis: **TWO-leg all-in (ES+NQ or YM+NQ)**, points; heavier than any single-leg family.
- FAILURE_MEMORY: adverse prior — **WE_W101 sec5.7** (standalone cross-market 0-for-15, only the
  CONDITIONAL/spread form ever cleared → this must be the spread form, beat a best-of-N null);
  **WE_W122/ESNQ** (sub-minute ES↔NQ closed, −$503/sess → material diff = DAILY residual, not
  sub-minute taking); **GENESIS_H3 XSMOM** (that was cross-sectional rank momentum, weekly; this is
  2-leg daily MR, opposite sign/horizon). Run ES only first; do not pay for YM unless ES survives.

### TIER 3 — Orthogonal by SIGN vs NQ momentum (equity MR). Capped by ρ; consolidate to ONE probe.

**W2-EQ-FADE — Equity-index gap / intraday mean-reversion, sign-opposite to NQ (lead ES gap-fade; YM over-extension as sign cross-check).**
- Instrument: **ES** (strongest measured gap conditional + SPX-gamma story + 0.25 tick for
  friction survival); **YM** as the over-extension variant (most mean-reverting equity index,
  signed-continuation −15.4pt). **RTY-RTHMR folds in here — do not run separately** (weakest
  standalone: VR(2)=0.97, conditional means ~1pt).
- Mechanism: ES/SPX is the 0DTE-gamma landing zone → gap over/undershoot pulled back to the open
  (E[RTH|gap-dn]=+3.14, E[RTH|gap-up]=−1.15, daily VR(10)=0.75). YM's price-weighting →
  single-name gap over-extension reverts. Sign is **OPPOSITE** NQ's live momentum — the natural
  complement despite high ρ.
- Cheapest falsifier: preregistered regression of next-RTH point-return on prior overnight gap
  (points), sign must be negative, expectancy must **beat the matched unconditional gap-fill
  geometry control (WE_W111b)** AND a circular-shift null AND exceed the all-in cost band; AND
  demonstrate **negative underwater correlation with the NQ P1 object** (the portfolio's actual
  value test). KILL inside the friction band or if it reduces to generic post-cross MR.
- Cost basis: **single-leg all-in**, points (ES tick 0.25 is the friction advantage).
- FAILURE_MEMORY: the entire NQ fade graveyard — **WE_W108/W109/W118** (7 fade geometries = mirror
  of a live momentum effect, continuation won at the same bars), **G2_F2_SWEEP01** (sweep-reclaim
  NULL both ways), **MC-07** (level-magnetism geometry-explained), **G2_F6_BREADTHPM01 + G2_F14**
  (breadth rebound = generic MR). Material difference required and MEASURED: ES/YM are structurally
  MORE mean-reverting than NQ (daily VR 0.75/0.77 vs 0.88; YM signed-continuation −15.4pt), the
  horizon is daily/gap not intraday-trigger, and the objective is a portfolio/underwater one. If it
  reproduces as generic gap-fill geometry (as on NQ), it is a rediscovery and dies.

### TIER 4 — Native vol-state on a correlated equity index. Only after ZB-VOLSTATE.

**W2-RTY-VOLSTATE — RTY forward-vol as RISK SPECIFICATION (small-cap credit/rate vol regime).**
- Instrument: **RTY** (ρ_NQ=0.75; chosen over ES/YM because small-caps carry the most distinct,
  credit/rate-sensitive vol regime, plausibly orthogonal to NQ *direction* even at high return-ρ).
- Mechanism: RTY's only self-forecast is its variance (RV ACF 0.595, range ACF 0.417) while returns
  are a random walk; a variance handle as a DD/risk transform.
- Cheapest falsifier: (a) HAR-RV beats random-walk RV OOS on QLIKE/DM; (b) vol-scaling reduces
  maxDD/CDaR **beyond its rate-matched random-thinning placebo** — if the placebo matches, it is
  thinning not information, KILL. Compression pre-registered as compressed→compressed.
- Cost basis: **points-RV**; RISK SPECIFICATION only, explicitly not a growth claim.
- FAILURE_MEMORY: **G2_F11** (fixed-window diurnal deseasonalization NOT-IDENTIFIED, VIF 92.86 —
  use plain multi-horizon HAR); **G2_F3_VOLSIZE01** (tail-only, below null — frame as RISK
  SPEC/DD, the explicitly not-closed lane); **G2_F1_COND01** (RV-tercile-as-ORB-conditioner 5.5×
  under MDE). Rank BELOW ZB-VOLSTATE because it is the correlated-index version of the same
  mechanism — measure ZB first, port to RTY only if the mechanism lives.

### TIER 5 — Measure descriptively ONLY; do NOT spend a wave budget.

**W2-RTY-RECON — Russell reconstitution / index-rebalance flow (DESCRIPTIVE, N-bound).**
- Instrument: **RTY**. The book's ONLY calendar-fixed mechanical flow event (annual late-June
  reconstitution + quarterly adds); index funds trade huge size at the reconstitution close;
  timing is idiosyncratic to the Russell calendar → decoupled from NQ momentum BY CONSTRUCTION.
- Falsifier / status: points-basis abnormal RTY return/RV/RTY-minus-ES spread in the ±k-day window
  vs matched non-event days, **MDE printed first**. n≈20–25 events over 4.5y → **almost certainly
  UNDERPOWERED**. Pre-declare **measure-once-descriptively**, not a wave to spend. Inherits the
  N-bound veto (**G2_F10 / MC-50**: no model or money moves an N-bound gate; **G2_F1_TICK01**
  events 44→2/yr collapse). Strategically the most orthogonal idea in the book, operationally
  un-buyable — record the description, mark UNDERPOWERED.

**W2-ZB-FADE — ZB intraday range-fade (orthogonal but cost-fragile; cheap descriptive kill).**
- Instrument: **ZB**. MR is genuine (VR(60)=0.65) and orthogonal, but the autopsy says it dies
  cheapest on cost: median RTH range ~0.9pt ≈ 29 ticks, 1-tick spread $31.25. Falsifier: reversion
  vs continuation at a tradeable 5–30 min horizon net of ~1-tick cost. Expect a cost kill; run only
  as a cheap confirmatory measurement, not a budgeted wave.

**W2-ES-VOLEXP — ES vol-regime → direction-neutral range/expansion harvest (expected cheap death).**
- Instrument: **ES**. NR7→next-range 0.92× already weakly refutes coil→break. Falsifier: does a
  compression indicator predict next-session ABSOLUTE range beyond an HAR-RV baseline (MDE first)?
  KILL if ΔR² < MDE. Lowest priority; expected to die cheaply.

---

## 5. EV-priority order for Wave 2 (orthogonality-weighted)

**Directive applied:** orthogonality is first-class; do NOT spend the Wave-2 budget on correlated
equity-index directional beta. EV ≈ (measured native signal) × (orthogonality to NQ) ×
(cheapness/power of falsifier) × (distance from graveyard). Orthogonality is weighted heavily, so
ZB and orthogonal-by-construction residuals rise above single-leg equity engines regardless of raw
signal size.

1. **W2-ZB-MACRO** — ρ=0.06, native, powered (~50–100 days/yr), sharp measured 08:30 vol
   structure, cheap single-instrument falsifier. **The single best spend.**
2. **W2-ZB-VOLSTATE** — ρ=0.06, the surest phenomenon in the whole complex (RV persistence),
   cheap HAR-RV falsifier, RISK-SPEC lane is open. Pairs with #1 on the same instrument.
3. **W2-EQ-RESID (ES lead)** — orthogonal BY CONSTRUCTION (~0 index beta); the only family that
   structurally defeats ρ=0.94. Ranked here despite an adverse cross-market prior because
   orthogonality-by-construction outranks single-leg raw signal. Two-leg cost; ES only first.
4. **W2-EQ-FADE (ES gap-fade lead)** — orthogonal by SIGN (opposite NQ momentum), strongest fresh
   measured conditional, single-leg + tight tick. Capped by ρ and must beat the near-random-walk
   geometry baseline and prove underwater-anti-correlation; ranked below the by-construction
   residual for that reason.
5. **W2-RTY-VOLSTATE** — same mechanism as #2 but on a correlated index (ρ=0.75); run only after
   ZB-VOLSTATE confirms the mechanism lives. RTY chosen for its distinct small-cap vol regime.
6. **W2-ZB-FADE** — orthogonal but expected to die on cost; cheap confirmatory measurement only.
7. **W2-RTY-RECON** — most orthogonal *idea* but N-bound/un-buyable; **descriptive measure-once,
   no wave budget.**
8. **W2-ES-VOLEXP** — expected cheap death (coil→break already refuted); lowest.

**Consolidation discipline (the budget guard):** items 3–5 collapse three equity indices into
*two* orthogonalized equity mechanisms plus one deferred vol-state — we never fund a directional
equity-index sleeve, and we never pay twice for one mechanism across correlated instruments (YM
residual waits on ES residual; RTY vol-state waits on ZB vol-state; RTY/YM/ES fades are one probe).
**Net Wave-2 spend concentrates on ZB (two orthogonal native families) plus one orthogonalized
equity-residual probe** — exactly where orthogonality-weighted EV points.

---

*Descriptive synthesis only. No promotion, no ledger trial, no live action. DISCOVERY_CONSUMED.*
*Substrates sealed at 2026-07-31; nothing ≥2026-08-01 was read or materialized.*
