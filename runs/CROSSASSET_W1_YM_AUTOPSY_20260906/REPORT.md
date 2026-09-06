# CROSSASSET Wave-1 — YM MARKET AUTOPSY

**Run:** `CROSSASSET_W1_YM_AUTOPSY_20260906` · **Instrument:** YM (E-mini Dow, CBOT/Globex,
point value **$5/pt**) · **2026-09-06.**

> **This is DESCRIPTIVE SCIENCE (a market autopsy), not a falsifiable test.** No ledger trial, no
> strategy, no P&L, no promotion. Evidence status **DISCOVERY_CONSUMED**. Lane-B Wave-1 phenotype of
> YM per `NQ_RESEARCH_PLAYBOOK.md` transfer-checklist step 6.

## 0. Discipline enforced in code
- **POINTS BASIS ONLY (DELEV01 law).** Substrate is NT8 **additive back-adjusted** continuous
  front-month; absolute levels are shifted, so every return/range/threshold is a **point difference**
  (`close_t − close_{t−1}`), never a % of price, never a level threshold.
- **NATIVE SESSION determined from YM own volume profile** (not assumed NQ 09:30–16:00) — §1.
- **Hard-drop `time >= 2026-08-01` at load.** Result: **0 rows dropped** (substrate ends
  `2026-07-31 16:59`). Retained boundary printed by the program: last bar `2026-07-31 16:59:00`.
- Data: `runs/SM1M_YM_SUBSTRATE/out/ym_1m_2022_2026.parquet` (1,595,378 bars) + NQ from
  `runs/SM1M_SUBSTRATE/out/nq_1m_2022_2026.parquet` for the correlation pre-read.

## 1. Native session (from YM own volume/bar profile)
- **1,177 distinct sessions**, `2022-01-03 → 2026-07-31`.
- Bars present on **1,380/1,440** minutes-of-day. The **only** non-traded block is **17:01–18:00 ET**
  (0 bars) — the CME daily maintenance halt. Session runs **18:00 ET → 17:00 ET** next day.
- **RTH 09:30–16:00 ET carries 72.15 % of volume** (ETH-overnight 27.85 %). Volume peaks at the
  **09:31 open** (1.50 %, minute std 41.8 pt) and the **16:00 close** (1.53 %) — the equity-index
  open/close double-hump; 09:00–10:59 alone is ~31 % of daily volume.
- **RTH-equivalent = 09:30–16:00 ET.** Verdict: YM native session shape = ES/RTY equity-index clock,
  measured not assumed.

## 2. RETURNS (points) — out/returns_summary.txt, out/returns_by_tod.csv
- **Drift lives entirely in RTH; overnight is a coin-flip.** RTH open→close **mean +10.18 pt/session,
  sum +11,519 pt** (1,132 sessions; ~$57.6k full-size @ $5/pt). Overnight (prevRTHclose→RTHopen)
  **mean −0.35 pt, sum −400 pt** — flat. Same "modern long drift concentrated in RTH" shape the NQ
  campaign flagged as the **ORB control-gate trap** — a fact, not an edge.
- **Time-of-day:** vol front-loaded (09:31 std 41.8 pt → ~12 pt into close); 09:31 mean +3.94 pt.
- Informative conditional: **large prior-day moves reverse** (§4).

## 3. DISTRIBUTION — out/distribution.txt
- **Extreme intraday tails, moderate daily.** 1-min exkurt **167** (skew +0.91); daily close-close
  exkurt **5.7**, skew **+0.10** (near-symmetric). Down/up daily mean ratio 1.03 — no strong daily
  left-skew (unlike NQ tail-dominated phenotype).
- **Ranges:** RTH range median **401 pt** (mean 446), overnight **214 pt**; intraday/overnight range
  ratio median **1.79x**. RTH realized vol median **247 pt**.
- **Gaps:** median |gap| **108 pt**; P(|gap|>50pt) 73 %; **gap-fill rate 65.7 %**.
- **Extreme 1-min:** |ret|>=50 pt once/~232 bars (0.43 %); >=100 pt once/~2,338 bars.

## 4. DEPENDENCE — out/dependence.txt
- **Returns mildly mean-reverting; volatility strongly persistent** (the headline).
  - 1-min return AC ~ **−0.009** (lag1). Daily RTH-ret AC lag1 **−0.10**, lag3 **−0.10**.
  - **Vol clustering dominates:** 1-min |ret| AC **0.39→0.25** (lags 1→60); **daily RV AC 0.72/0.66/0.55**.
  - **VR all < 1:** 1-min VR(30)=**0.960** (z −2.05); daily VR(5)=**0.772** (z −1.79), VR(10)=0.684.
    Sign persistence 1-min **0.483**, daily **0.499**.
  - **Large moves reverse:** top prior-day |RTH| tercile → **E[signed continuation] −15.4 pt** (small −4.8,
    mid +1.6).
- **YM more mean-reverting than NQ at every scale:** daily VR(5) **0.77 vs 0.88**; 1-min VR(30) **0.96 vs
  0.99**; RTH ER median **0.047 vs 0.053** — the "materially different" evidence for §9.

## 5. PATH — out/path.txt
- **Extremely choppy intraday.** RTH **ER median 0.047** (tortuosity ~21x; pathlen median 3,581 pt vs
  displacement 172 pt).
- **MFE/MAE symmetric:** up-exc median 177 pt, dn-exc 178 pt; up/(up+dn) 0.489.
- **Range clusters:** RTH-range AC lag1 **0.52**; P(range<0.7x) 18 %, P(range>1.5x) 16 %. **OR30 ~ 45 %**
  of full RTH range.

## 6. SESSION STRUCTURE — out/session.txt
- **Overnight swept routinely:** RTH takes out ON high **69 %**, ON low **65 %**, both **36 %**, neither
  only **2 %**.
- Prior-day high **52 %**, low **48 %** (coin-flip).
- **OR30 whipsaws:** broken up 69 %, down 70 %, both 40 %.
- Close location median **0.566** of range. Gaps mildly fade: corr(gap, RTH ret) **−0.084**.

## 7. YM<->NQ CORRELATION — diversification pre-read — out/dependence.txt
- **rho(YM daily RTH o→c, NQ) = +0.7534**; close-close **+0.7405** (POINTS basis; scale-invariant so =
  dollar-basis rho). Per year 0.88/0.71/0.57/0.83/0.60.
- **Read:** on a directional daily basis YM is a **weak diversifier** (~56 % shared variance); a
  long-biased YM sleeve co-moves heavily with the live NQ book. The orthogonality prize lives in YM
  **residual** and its **stronger mean-reversion**, not a directional YM-long. (The number that decides
  portfolio value is the eventual engines underwater-curve correlation, not this raw index rho — a
  pre-read, not a verdict.)

## 8. Descriptive digest (load-bearing facts)
1. Native session = equity-index ETH 18:00→17:00 ET, RTH 09:30–16:00 (72 % of volume) — measured.
2. Drift is RTH-only (+11,519 pt); overnight flat (−400 pt) → ORB long-drift trap applies.
3. Vol clustering dominates (daily RV AC 0.72); returns near-unforecastable.
4. YM more mean-reverting than NQ everywhere (VR 0.77 vs 0.88; ER 0.047 vs 0.053); large daily moves
   reverse (−15.4 pt signed continuation, top tercile).
5. Intraday path extremely choppy (ER 0.047, tortuosity 21x); OR30 ~ 45 % of RTH range.
6. Overnight extremes swept ~2/3 of sessions; prior-day levels coin-flip; gaps mildly fade.
7. rho(YM,NQ) ~ +0.75 → low raw diversification; orthogonality must come from residual/MR, not long.

## 9. Wave-2 preregisterable NATIVE mechanism families (ranked). None tested here.

### H-YM-1 (rank 1) — Value/growth DISPERSION: YM−betaNQ residual mean-reversion (orthogonality prize)
- **Economic reason (YM-specific):** YM is the price-weighted blue-chip/cyclical index; NQ is
  tech-growth. The ~44 % of YM variance not shared with NQ is the value–growth/cyclical/rate-sensitivity
  rotation — a distinct priced factor. Trading the YM residual is orthogonal-to-NQ *by construction* —
  exactly the campaign stated prize. YM stronger MR (§4) is the mechanism that would make a spread revert.
- **Cheapest falsifier:** daily YM point-return residual `e = ymRTH − beta*nqRTH` (beta trailing, points,
  strict chronology); test residual AC / VR(2..5) at ONE preregistered horizon vs a **circular-shift null**
  (preserves marginals+dependence). Random-walk residual (VR~1, AC~0) kills it in one test. Add the
  matched **unconditional raw-YM MR control** (W111b) so a definitional signature is ruled out.
- **Must clear:** `GENESIS_H3` (XSMOM cross-root NULL) — different: that was cross-sectional 12-1
  *momentum*, weekly, rank-based; this is 2-leg cointegration **mean-reversion**, daily (opposite sign,
  different observable/horizon). `WE_W122` (ESNQ sub-minute −$503) & `G2_F13` (ZB→NQ NULL) — different:
  those predict *NQ* from another series at sub-minute/1-min; here YM is the *traded* instrument and the
  object is a *daily relative-value spread*. `WE_W101 §5.7` (standalone cross-market 0-for-15) — must beat
  a **best-of-N** null and be the conditional/spread form, not a naked directional cross-market bet.

### H-YM-2 (rank 2) — Intraday mean-reversion / fade of over-extension (YM structurally choppier than NQ)
- **Economic reason (YM-specific):** YM is the **least liquid** equity-index mini and is **price-weighted**
  — a few high-price names (UNH, GS, MSFT, HD, CAT) dominate, so a single-name gap over-extends the index
  and reverts. This is *why* YM VR<NQ, ER<NQ and large daily moves reverse (§4–5). Native expression:
  fade a stretched RTH move (displacement beyond k*ATR from open/OR by a fixed time).
- **Cheapest falsifier:** forward RTH point-return conditional on over-extension vs the **matched
  unconditional continuation control** (W111b), ONE horizon, circular-shift null; **plus** the YM-vs-NQ
  VR/ER contrast (already +evidence 0.77 vs 0.88) as the regime-difference gate. If YM fade collapses
  onto the unconditional control (as NQ did), it dies.
- **Must clear (heavy graveyard):** `WE_W108/W109/W118`, `G2_F2_SWEEP01` (sweep-reclaim NULL both ways;
  momentum mirror wins), `G2_F1_TICK01` (capitulation fade; events regime-collapse),
  `G2_F6_BREADTHPM01` + `G2_F14` (breadth rebound long CLOSED-AS-GENERIC-MR). **Materially different only
  if** it is a genuinely different market regime: those closures established **NQ is a continuation/momentum
  market**; the autopsy shows **YM is measurably more mean-reverting at every scale** — that measured gap
  (not a re-tuned horizon) is the anti-rescue argument. If YM MR is merely generic post-cross MR
  (SWEEP01), it is closed.

### H-YM-3 (rank 3) — Volatility-state as RISK SPECIFICATION (not a growth timer)
- **Economic reason (YM-specific):** the cleanest structure in the autopsy is **vol persistence** (daily
  RV AC 0.72, 1-min |ret| AC 0.39, RTH-range AC 0.52) while returns are near-unforecastable. YM RV is
  highly predictable session-to-session — natural use is a **risk denominator / vol-target** for whatever
  directional engine H-YM-1/2 produces.
- **Cheapest falsifier:** HAR-RV (points) forecast of next-session RTH RV, OOS **QLIKE/DM vs random-walk
  vol**; for any *sizing* claim, the mandatory **rate-matched random-thinning placebo** + count-matched
  control (eval_battery), led by weekly-vol. Tail-only benefit below its own null => folklore, not alpha.
- **Must clear:** `G2_F3_VOLSIZE01` (vol-managed sizing FAIL — no growth timing, tail-only, below null) and
  `G2_F11` (fixed-window deseasonalized vol NOT-IDENTIFIED, VIF 92.86 DEFECT). **Materially different only
  if** framed as **RISK SPECIFICATION** (the explicitly *not-closed* lane), on a YM-native engine own
  vol, with a **non-collinear** deseasonalization — never a standalone growth/return timer (closed), never
  a fixed-DD figure without its placebo.

**Ranking rationale:** H-YM-1 first — the only family orthogonal to NQ *by construction* (the prize) and
genuinely open (no daily index-pair relative-value closure exists). H-YM-2 second — strong native
motivation but the heaviest graveyard burden, viability resting on the VR/ER regime gap. H-YM-3 third —
mostly a risk-denominator substrate; its directional/growth forms are already closed on NQ.

## 10. Files
- `src/autopsy_ym.py`; `out/returns_by_tod.csv`, `out/returns_summary.txt`, `out/distribution.txt`,
  `out/dependence.txt` (incl. YM<->NQ corr + structural contrast), `out/path.txt`, `out/session.txt`;
  supporting `out/volume_profile_by_minute.csv`, `out/daily_session_frame.csv`.

_Descriptive only. No promotion, no live deploy, no sizing change; live book `2047681` untouched. $0._
