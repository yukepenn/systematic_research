# 6E (CME Euro FX) DAILY autopsy — FX pod Wave-1

**Run:** `runs/DAILY_6E_EXTRACT_AUTOPSY_20260906/` · 2026-09-06 · DESCRIPTIVE / DISCOVERY_CONSUMED ·
$0 · no ledger trial · no forward holdout withheld (P1 doctrine: judge on in-sample robustness).
Series: `out/6e_daily.parquet` (4,273 sessions, 2009-03-30 -> 2026-07-31, seal-clean). Primary
return = `ret_pct` (ratio-stitched, cross-era percent-safe per DELEV01). Extraction provenance and
roll method: see `MANIFEST.md`. **Read the .ncd without NT8? YES** (pure-Python 48-byte reader;
point returns reproduce the certified s7 construction to 0.0).

---

## 0. Headline

6E daily returns are, in the **mean/direction**, close to a random walk — no day-of-week effect, no
sign persistence, variance ratios ~= 1.0 at every horizon, low path efficiency. The **only robust
dependence is volatility clustering** (strong, out to a quarter). Tails are fat but modest and
symmetric; annualized vol is low (~7-8%). Its correlation to NQ is low **on average (+0.15)** but
**regime-varying (-0.30 ... +0.50)** — the diversification value is real but is a *mixture*, not a
stable constant. This profile says: the closed price-direction families (single-index TSMOM, XSMOM,
day-type seasonality) are *both* previously-closed *and* unsupported by 6E's own structure — a
native 6E edge must come from **carry/rate mechanics, flow timing, or risk-state**, not price
momentum.

---

## 1. Autopsy findings (§9 protocol, daily resolution)

### RETURNS (`autopsy_dow.csv`, `autopsy_month.csv`)
- **Day-of-week: NULL.** All five |t| <= 1.13 (Mon +0.014%/t0.84 ... Fri -0.021%/t-1.13). Confirms
  FAILURE_MEMORY's "day-of-week (2004; re-measured NULL here 2026)" on a *different asset*.
- **Month:** weak, multiplicity-fragile — May -0.049%/t-1.71, Apr +0.037%/t1.36; nothing survives
  12-way multiplicity.
- **Prior-day sign:** no persistence. next|priorUP -0.0046%/t-0.39, next|priorDOWN -0.011%/t-1.00,
  unconditional -0.0064%/t-0.79. No daily follow-through either way.

### DISTRIBUTION (`autopsy_distribution.json`)
- **Skew +0.038 (symmetric), excess kurtosis +1.72.** Fat-tailed but *mild* for a daily series
  (equity indices run higher). |z|>3 = 3.9x Gaussian; |z|>4 = 30x Gaussian; JB p~=1e-113.
- **Variance is ~93% "intraday".** Decomposing the daily point-return: `var(overnight)` 2.8e-6 vs
  `var(intraday)` 4.0e-5 -> overnight (prior-close->open) carries only **6.6%** of variance. 6E is a
  ~24h market, so the close->open gap is small and nearly all daily variance is inside the
  session-window NT8 stamps. **Load-bearing for any session-based work.**
- **Low vol, clustered:** 21-day annualized realized vol median **7.2%** (min 2.7%, p95 13.1%, max
  17.1%). A low-vol asset vs NQ.

### DEPENDENCE (`autopsy_autocorr.csv`, `autopsy_varratio.csv`, `autopsy_trend_reversal.csv`)
- **Return autocorrelation ~= 0.** lag1 +0.006 (z0.4), lag2 +0.010 (z0.6). Two marginal negatives
  (lag3 z-2.6, lag10 z-2.9) are multiplicity-fragile weak reversal, not a mechanism.
- **Volatility autocorrelation is STRONG and persistent** — |log-ret| acf lag1 **+0.126 (z+8.2)**,
  lag5 +0.134 (z+8.7), lag21 **+0.107 (z+6.9)**, lag63 +0.059 (z+3.8). This is the single robust,
  powered structure in the series.
- **Sign persistence: none.** P(up)=0.494, P(up|up)=0.491, P(up|up)-P(up) = -0.003.
- **Variance ratios ~= 1.0 at every horizon** — VR(2) 1.006, VR(5) 0.988, VR(10) 0.966, VR(21)
  0.943, VR(63) 0.980; **all |z| < 0.7**. No trend and no reversal signature in the mean.
- **Trend/reversal regressions** (forward-k on trailing-k, non-overlapping): all insignificant —
  best is k=21 momentum t+1.82; k=252 reversal t-1.04. No stable horizon.

### PATH (`autopsy_efficiency.csv`)
- **Low path efficiency (choppy).** Kaufman ER mean 0.325 (10d) -> 0.222 (21d) -> **0.130 (63d)**;
  only **0.2%** of 63-day windows exceed ER 0.5. 6E rarely trends cleanly at multi-week+ scale —
  independent corroboration of why single-index daily TSMOM failed and stays closed.
- **Trend maturation:** forward-21d returns are negative in all trailing-63 terciles (bottom
  -0.334%/t-4.83, top -0.141%/t-2.25) — this is the secular EUR-down drift bleeding through, not a
  momentum signal (top is *less* negative than bottom, i.e. no clean continuation).

### STRUCTURE — FX-specific (`autopsy_turn_of_month.csv`)
- No intraday session (Asia/Europe/US) data locally — stated, not faked. Daily-resolution only.
- **Turn-of-month:** the second-to-last trading day shows +0.051%/t1.47 — *suggestive but
  underpowered unconditionally*. Last-td, first-td, and the ToM window are flat. Turn-of-week: no
  Mon/Fri effect (see DOW). The month-end bump is the one calendar structure worth a *conditioned*
  test (below), not a raw calendar mean.

### CROSS-ASSET — rho(6E, NQ) (`autopsy_corr_nq*.{csv,json}`)
- **Pearson +0.154, Spearman +0.156** over 4,136 shared sessions. Low positive — the
  diversification prize is real.
- **But it is a regime mixture, not a constant:** by-year rho runs **-0.30 (2015) ... +0.50 (2011)**,
  high in risk-on/off crises (2009-13: +0.25..+0.50; 2022 +0.37; 2026 +0.38) and negative/near-zero
  mid-decade (2014-17). This mirrors the campaign's own P1/XM "the hedge is a mixture" lesson — a
  fixed-weight 6E+NQ blend banks the *average* diversification and eats the *conditional*
  co-movement in exactly the crises where risk matters most.

---

## 2. Three preregisterable NATIVE daily/swing mechanism families (ranked)

DESCRIPTIVE proposals only — no test run here. Each names its FX-specific economics, its cheapest
falsifier, and clears the relevant FAILURE_MEMORY closure (anti-rescue). Eval discipline
(rate-matched random-thinning placebo, weekly-vol-led battery, circular-shift/label-shuffle nulls
preserving dependence, concentration + timing-teeth classification) attaches **when** any becomes a
test.

### RANK 1 — Month-end FX hedge-rebalancing flow (flow-sign-conditioned turn-of-month)
- **Economics (FX-specific, mechanical):** global equity/bond managers hedge foreign-currency
  exposure and rebalance those hedges near month-end. When US equities rally over a month, the USD
  value of foreign-held US assets rises and hedgers must **sell USD / buy EUR** into the month-end
  fix — a calendar-timed, flow-driven, *sign-predictable* pressure on 6E (Melvin & Prins). Direction
  is given by an **exogenous instrument** (the trailing calendar-month equity return), not by 6E's
  own price.
- **Why now:** the autopsy shows a raw last-1-day bump (+0.051%/t1.47) that is real-shaped but
  underpowered *unconditionally*; the untested lever is conditioning the **sign** on the month's
  equity move.
- **Cheapest falsifier:** regress the last-3-trading-day 6E `ret_pct` (sum) on `sign(trailing
  calendar-month NQ return)` (and its magnitude), 2009-2026; gate the conditioned mean against
  (a) the matched **rest-of-month** control and (b) a **month-label circular-shift null**. Dead if
  the flow-conditioned mean does not beat the rest-of-month control at the family bar.
- **Clears FAILURE_MEMORY:** materially different from **GENESIS_H2** (11 calendar day-types ->
  *unconditional same-session mean*, NULL 0/11) — this is a **flow-sign-conditioned directional**
  prediction with an exogenous driver, over a turn-of-**month** window, not a day-of-week/day-type
  mean. Different from the (NULL) day-of-week effect.

### RANK 2 — Carry / rate-differential DIRECTION (CIP via the term-structure basis)
- **Economics (FX-specific):** covered interest parity ties the 6E futures term structure
  (deferred - front) to the **EUR-USD short-rate differential**; the FX carry premium (be long the
  higher-yielder) is among the most robust cross-currency effects. Native single-name form: hold 6E
  by the **sign of the rate differential** — short EUR when USD out-yields (post-2022 Fed-hike
  regime), long EUR when EUR out-yields. This is a *rate-mechanics* edge, orthogonal to the
  price-momentum families the autopsy rules out.
- **Data honesty (drives the rank):** the 6E-native basis is only quoted during the ~3-session
  quarterly roll overlaps (~4 samples/yr -> underpowered from the local store alone). Cleanest
  falsifier needs an **EUR-US short-rate differential series** (a $0-obtainable free-data
  acquisition: US 3M T-bill/OIS vs EUR OIS/Euribor; US leg proxyable from local ZT/ZF).
- **Cheapest falsifier:** `sign(rate-diff)` -> next-month 6E `ret_pct`, terciles, 2009-2026, vs a
  matched unconditional control; require **sign-stable across >=3 sub-eras** (the ZB->NQ G2_F13
  playbook). Fold in the ~4/yr native-basis samples as a corroborating check.
- **Clears FAILURE_MEMORY:** distinct from **single-index daily TSMOM / XSMOM** (dead — those are
  *price* momentum; VR~=1 and ER 0.13 here confirm 6E has no price-trend to harvest) and from
  **CARRY_V1** (closed, *cross-market* carry ranking, SI-concentrated) — this is a **single-name FX
  rate-differential direction**, a different observable and decision role.

### RANK 3 — Volatility-/correlation-state risk router (RISK SPECIFICATION, not a direction edge)
- **Economics:** the one powered structure is **vol clustering** (|ret| acf z+8->+3.8 across lag
  1->63) and 6E's rho-to-NQ is a **regime mixture** (-0.30..+0.50). With near-random-walk direction,
  vol cannot be traded for direction — but vol-and-corr *state* is a legitimate **risk
  specification**: a 6E vol-target plus an NQ-6E rolling-corr-aware weight could cut a 6E+NQ
  portfolio's realized risk (and lift realized MAR) even at **zero** 6E direction edge, precisely by
  down-weighting 6E in the crisis windows where its diversification collapses.
- **Cheapest falsifier:** does the vol-target + corr-aware weight beat a fixed-weight 6E+NQ blend on
  **realized weekly-vol-adjusted** terms, at matched gross exposure, net of the modelled FX cost,
  with a **rate-matched random-thinning placebo** (`eval_battery.py`)? Dead if it does not beat the
  fixed-weight control out-of-sample.
- **Clears FAILURE_MEMORY:** not a direction mechanism at all, so it collides with no
  TSMOM/XSMOM/day-type closure; and distinct from the closed **VOLSIZE01** (NQ *single-asset*
  extremes-only vol-managed sizing, "no growth timing") because this is **cross-asset,
  correlation-timed risk allocation**, which FAILURE_MEMORY lists explicitly as NOT-closed
  ("vol-state as RISK SPECIFICATION (sizing)").

**Ranking logic:** #1 is fully testable on data-in-hand with a supportive prior and a clean
anti-rescue story; #2 has the strongest economics but is data-thin locally (needs one free external
series); #3 is the most robust *fact* but is risk-shaping, not new alpha — so it ranks last as a
source of edge while being the safest to build.

---

## 3. What NOT to re-propose (autopsy + FAILURE_MEMORY agree)
Single-index daily TSMOM (VR~=1, ER 0.13 — no price trend) · XSMOM · day-of-week / day-type calendar
means (NULL, re-confirmed) · naive prior-day continuation (no sign persistence). Any 6E "trend"
pitch must state a **non-price** observable or it is a rescue.
