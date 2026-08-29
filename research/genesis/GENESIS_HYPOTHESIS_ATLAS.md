# GENESIS HYPOTHESIS ATLAS — ranked by priors, not by backtests

**State document, Phase 5.** Ranked by: mechanism plausibility × information novelty × data
quality × causal observability × N × execution feasibility × portfolio independence ÷ engineering
burden. **No hypothesis below has been run by GENESIS.** Every future test: one frozen primary,
ledger trial before compute, independent implementation before any confirmation read, McLean-Pontiff
haircut on externally-sourced priors (−26%/−58%).

Format per hypothesis: mechanism · observables · horizon · expected sign · failure mode · data ·
execution contract · evidence plan · power · relation to prior families.

---

## H1 — VX/VXN term-structure state as a session-exposure conditioner — ❌ **NULL, CLOSED AT FORMULATION** (`runs/GENESIS_H1_VOLSTATE_20260828`, G00010)

**Tested 2026-08-28: F1/F2/F3 all FAIL — wrong sign (T3−T1 = −0.037%/session, t −1.42), collapses
under RV match, 11th percentile of its own null. The 2022+ confirmation window was never opened.**
Exact closure scope in the run report. Remains open: vol-state as RISK SPECIFICATION (sizing), and
intraday horizons — neither is scheduled. Original prior below, kept for the record.

### (original rank-1 prior, superseded by the test)

- **Mechanism:** the vol futures curve prices risk transfer; backwardation = stress demand for
  near-dated protection. Conditional NQ return/vol distributions differ across curve states
  (Cheng RFS 2019 coeff≈1; Simon-Campasano; VX leads spot intraday). This is a **state variable**,
  not a signal-on-P1.
- **Observables:** daily VX settlements per contract (curve slope, roll yield), VIX, **VXN**
  (NQ-native — never used by anyone here), VIX3M/VIX ratio. All free (Wave-2 FD certifying now).
- **Horizon:** next-session to next-week exposure/sizing state.
- **Expected sign:** contango → risk-on (positive conditional drift, lower tail); backwardation →
  negative/fat-tailed conditional distribution.
- **Failure mode:** the curve state adds nothing beyond NQ's own trailing realized vol —
  **the mandatory control is an own-realized-vol-matched conditioning**; if VXN state ≈ RV state,
  the information is not new.
- **Data:** Cboe 2004→2026-07-31 certified layer (~5,600 sessions).
- **Execution contract:** state known at prior close (settlement); applied to next session's
  exposure; no intraday data needed; costs only when exposure changes.
- **Evidence plan:** DISCOVERY on 2004→2018 · development confirmation 2019→2026-07 chronological
  · strongest = prospective (shadow-compatible). Ceiling on all history: DISCOVERY-GRADE.
- **Power:** high for state-conditional means at session N≈5,600 (≈22 years, both vol eras).
- **Prior families:** BREADTH03 VRP was closed-by-**power** (priced coin-flip on 71 events) —
  different observable and N. W109/W113 "regime info real, policy dead" closed **detector-veto
  policies on P1**, not exposure conditioning by an external state. Genuinely distinct.

## H2 — Calendar/flow-day conditioning — ❌ **NULL, CLOSED AT FORMULATION** (`runs/GENESIS_H2_CALENDAR_20260828`, G00011)

**Tested 2026-08-28: 0 of 11 day-types survive the family-wise bar (max-|t| q95 = 2.849; best real
2.296). FOMC_DAY +0.137%/session (t 1.73) under bar; NFP contra-sign; ToM/FOMC-cycle flat. ⭐ The
day-of-week closure is now a TESTED fact.** Exact scope + MDEs in the run report. Interactions and
variance effects were out of scope and stay unscheduled without a new mechanism. Original prior
below, kept for the record.

### (original rank-2 prior, superseded by the test)

- **Mechanism:** institutional flow cycles (month-end rebalancing, Fed information cycle, option
  expiry hedge unwinds) and scheduled-risk premia (Savor-Wilson: announcement days carry 10× the
  daily premium).
- **Observables:** pure calendars — ToM day index, FOMC meeting cycle week, OPEX week, CPI/NFP/FOMC
  day dummies. BLS 08:30 calendar 2005–2021 **already committed and never joined** (A2 §6).
- **Horizon:** session close-to-close.
- **Expected sign:** ToM last+3 positive; FOMC weeks 0/2/4/6 positive; announcement days positive
  mean with higher vol; OPEX week positive drift into expiry.
- **Failure mode:** multiplicity (many dummies) — ONE wave, ALL dummies preregistered together,
  session-clustered family null, effective-K correction; no post-hoc subsetting. Decay: these are
  published effects (−58% haircut).
- **Data:** deep NQ substrate 2006→2026 (5,000+ sessions) — no new data at all.
- **Execution contract:** positions known the prior close; one decision/session.
- **Evidence plan:** DISCOVERY split by era (2006–2018 / 2019–2026-07); the repo's macro closure
  (event-response magnitude, N-bound) is untouched — this uses day-TYPE, not surprise magnitude.
- **Power:** ToM ≈ 240 events; FOMC-cycle ≈ 1,100 weeks pooled; adequate only for effects ≥ a few
  bp/day — state the MDE in the spec.
- **Prior families:** day-of-week "closure" has **no in-repo test** (E1 over-generalization #4);
  event-day *flag* was tested only as an XM covariate. New at exact scope.

## H3 — Futures cross-sectional momentum (XSMOM) — ❌ **NULL, CLOSED AT FORMULATION** (`runs/GENESIS_H3_XSMOM_20260828`, G00012)

**Tested 2026-08-28: positive net (+$349k, survives 3-tick stress and 6/6 LOSO) but t 1.43 and —
decisively — its own dependence-preserving null earns the same money (real 60.7th pctile). The P&L
is vol-scaled long/short structure, not rank information. The 2019+ held-back window was NEVER
loaded and remains pristine.** Original prior below, kept for the record.

### (original rank-3 prior, superseded by the test)

- **Mechanism:** relative-strength across asset classes (information diffusion + flow persistence);
  literature support is cross-asset, not single-index (where TSMOM is contested).
- **Observables:** `economic_returns.parquet` — 24 roots, daily, 2009→2026-07.
- **Horizon:** weekly rebalance, rank top-k vs bottom-k across roots.
- **Expected sign:** winners > losers over 1–12m formation.
- **Failure mode:** the CARRY_V1 lesson — sector degeneracy (n_sector=2 forces rank ±1); use
  cross-ALL-roots ranks, not within-sector; SI-style concentration check preregistered.
- **Data:** in hand; 2019+ windows preserved by CARRY/VOLUME remain unread — an honest held-back
  window EXISTS for this family.
- **Execution contract:** daily closes → next-day open baskets; cost per root per RT as in
  VOLUME_LIQUIDITY's model (with the D1 caveat: 1-tick multi-market spread is assumed, so stress
  ×2/×3 costs).
- **Evidence plan:** discovery 2009→2018 · **held-back 2019→2026-07 one shot** (a genuinely
  unconsumed confirmation window — rare asset).
- **Power:** 17 years × 24 roots, weekly unit ≈ 880 weeks.
- **Prior families:** TSMOM (time-series, own-history sign) closed at scope; XSMOM
  (cross-sectional rank) **never tested** (E1). NQ relevance: portfolio diversifier + NQ leg
  conditioning, not an NQ-only strategy.

## H4 — Intraday momentum family (FOLLOW_MORNING + last-half-hour) — the permitted addition is ❌ **NULL** (`runs/GENESIS_H4B_LASTHALFHOUR_20260828`, G00013)

**Tested 2026-08-28: the Gao open→last-half-hour geometry is DEAD on modern NQ (slope −0.007,
t −0.61, 49.2% sign-agreement) — and the diagnostic dated its death: real 2006–2009 (t +3.02),
decayed through 2010–2013, gone by 2014. The family's LIVE member remains FOLLOW_MORNING (11:48
geometry, modern-era), whose virgin ≥2026-08-01 read is the scheduled decider — untouched.**
Original prior below, kept for the record.

### (original rank-4 prior, superseded by the test)

- **Mechanism:** hedging-demand flows (gamma + leveraged-ETF rebalancing) make late-session
  returns continue the day's direction; the repo independently found the class alive (W114,
  three-way confirmation that continuation is modern-era).
- **Observables:** NQ's own path (first half-hour, morning direction), optionally vol state.
- **Horizon:** intraday, 11:48→15:44 (frozen) and 15:00→15:59 (Gao geometry, never tested here).
- **Expected sign:** continuation.
- **Failure mode:** decay (external OOS Sharpe 0.39 post-2024); overlap with P1 (ρ +0.279) means
  portfolio-marginal is the binding gate, already failed once — **the virgin ≥2026-08-01 read
  (already scheduled) decides; no new mining before it.**
- **Action, not mining:** hold. One permitted addition: the exact Gao last-half-hour geometry as a
  SEPARATE frozen object (it is a different mechanism window than 11:48), single shot, logged.
- **Prior families:** FOLLOW_MORNING is this family's live member; seven fade kills are its
  mirror-side evidence.

## H5 — Overnight/RTH structure re-adjudication — ⏸ **DEFERRED TO FORWARD DATA (correction 2026-08-28)**

⚠️ **Sequencing correction:** the parked objects' revival conditions ("longer sample", "trailing-24m
t reverting") require data **after** the point at which they were parked — i.e. the sealed ≥2026-08-01
window or shadow accrual. Re-reading the same pre-seal data now would be multiplicity without
information. **No historical re-adjudication is scheduled; these wait for the seal/shadow.**

- **Mechanism:** distinct liquidity/participant regimes per session phase; overnight-vs-intraday
  split persists as structure even though the naive drift is dead.
- **Observables:** NQ 1-min phase returns (Asia/Europe/premarket/RTH/close).
- **Horizon:** phase-level positions.
- **Failure mode:** the 2026-dominance that parked W96 (one-era effect); needs the longer sample
  that time has now partially delivered.
- **Evidence plan:** single frozen re-adjudication of the PARKED objects at their recorded revival
  conditions (not new construction): W96 NIGHT, mirrored short sleeve, W40 vol-expansion.
- **Prior families:** exactly the parked rows of PARKED_NOT_DEAD (54/38/56) — this is their owed
  re-read, with pre-W82 economics re-costed at $14.65.

## H6 — ATR/vol-normalized-offset — ⏸ **RECLASSIFIED: FORWARD-ONLY (correction 2026-08-28)**

⚠️ **The "one proper adjudication" idea is withdrawn as historically untestable.** A meta-test
designed after observing three near-misses is post-hoc by construction — pooling them now is
"lower the bar until it passes" wearing a statistics costume. The family died 3× at its own
preregistered bars; its next legitimate evidence is **forward** (sealed window or shadow), where a
single preregistered joint read is honest. Nothing scheduled on historical data.

## H7 — COT positioning crowding — ❌ **NULL, CLOSED AT FORMULATION** (`runs/GENESIS_H7_COT_20260828`, G00014)

**Tested 2026-08-28: T3−T1 +0.049%/wk (t +0.35, anti-contrarian point estimate), 30th pctile of an
856-shift null, halves opposite-signed — under a strict Friday-15:30-ET availability rule and with
MDE 0.277%/wk printed (a real effect was detectable). Dealer/Asset-Manager diagnostics also flat.**
The low prior was stated in advance and confirmed. Original prior kept below for the record.

## H8 — Liquidity-state session conditioning from ES/MNQ books — rank 8 (park)

ES tick full-BBO (126 dates) and MNQ tick (128 pre-burn) exist locally and unread — but the
adjacent lane is 0-for-4, N≲130 caps power at falsifier-grade, and F2's literature scores depth as
execution-relevant, not alpha-relevant, at this scale. **Park until a specific mechanism with a
session-level observable is written; never spend the blind pools on this.**

---

## Explicitly NOT seeded (and why)

Overnight drift, pre-FOMC drift, day-of-week alone, 1-min lead-lag, seconds-OFI, VPIN, GEX-label
products — externally dead (GENESIS_EXTERNAL_EVIDENCE.md). Threshold-relaxation on P1's arming,
anti-P1 supervised targets — barred by standing owner directives. Databento depth — reframed as an
execution/cost falsifier decision, not a hypothesis.

## Sequencing

Wave 3 = H1 (needs FD certification, running) + H2 (needs nothing) as two independent preregistered
specs; H3 next (its held-back window is precious — spec must be airtight before any read); H5/H6 as
cheap adjudications interleaved. H4 waits for the virgin read. Portfolio search (charter §23/§40)
begins when ≥2 sleeves survive development confirmation.
