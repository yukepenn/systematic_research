# ES MARKET AUTOPSY — Cross-Asset Wave 1

**Run:** `CROSSASSET_W1_ES_AUTOPSY_20260906` · **Instrument:** ES (E-mini S&P 500), point value **$50**
**Status:** DESCRIPTIVE SCIENCE / **DISCOVERY_CONSUMED**. No strategy, no P&L, no ledger trial, no promotion. $0.
**Substrate:** `runs/SM1M_ES_SUBSTRATE/out/es_1m_2022_2026.parquet` (1-min OHLCV, ET END-stamped,
additively back-adjusted continuous front-month). **Cross:** `runs/SM1M_SUBSTRATE/out/nq_1m_2022_2026.parquet` (PV 20).

**Discipline honored:** POINTS BASIS ONLY throughout (DELEV01 law — additive back-adjustment shifts
absolute levels, so every return/range/threshold is a point difference, never % of price, never a
level threshold). Native session determined from ES's own volume profile, not assumed. Sessions
`>= 2026-08-01` hard-dropped at load.

---

## 0. Data boundary (printed from the program)

- Raw last bar `2026-07-31 16:59` ET; **dropped `>=SEAL(2026-08-01)` = 0 rows** (substrate already
  ends at the seal). **Retained sessions: 2022-01-03 .. 2026-07-31, n=1184** trading sessions.
- Per-session frame uses **1139 full-RTH sessions** (`>=300` RTH bars; drops half-day/holiday shells).
- Shared ES∩NQ sessions for the correlation: **1137**.

## 1. Native session (from ES's OWN volume profile — NOT assumed)

ES is a CME equity-index future trading **ETH 18:00 → 17:00 ET** (Sun–Fri) with a **17:00–18:00
maintenance halt** (strict 17:01–17:59 bar-count = **0**, confirming the break). The volume profile
by 30-min bucket resolves the structure the data actually has:

- **RTH core 09:30–16:00 ET carries 79.9% of total volume in only 28.0% of the bars.** The single
  largest bucket is the **09:30 open (10.65% of daily volume)**; a **close ramp** at 15:30 (8.07%)
  and 16:00 (6.86%); a US pre-open data bump at **08:30 (2.05%)**; and a modest **European-hours
  bump 03:00–04:00 (~0.7% each)**. Overnight is thin but continuously traded.
- **NATIVE session = ETH 18:00→17:00 ET. RTH-equivalent = 09:30–16:00 ET** (same clock as NQ — both
  are CME equity-index — but this was *confirmed from ES's profile*, not copied). All session-level
  measurements below use RTH 09:30→16:00 and overnight = prior-16:00→next-09:30.

## 2. RETURNS

- **The drift splits almost exactly 50/50 between RTH and overnight** over 2022–2026: sum(RTH)=**+963pt**,
  sum(overnight gap)=**+968pt**; RTH is 57.7% of the gross absolute move, overnight 42.3%. The
  textbook "equities only rise overnight" pattern does **not** hold in points for this window — ES
  makes money in both segments and neither drift is statistically strong (RTH t=0.63, ON t=0.84).
- **Gap-fade is the strongest conditional in the market:** `E[RTH ret | gap up] = -1.15pt` vs
  `E[RTH ret | gap down] = +3.14pt`; `corr(gap, same-day RTH) = -0.074`. Gaps down bounce, gaps up fade.
- **Day-to-day reversal:** `corr(prev RTH, RTH) = -0.103`; `E[RTH | prior day down] = +1.60` vs
  `prior day up = +0.20`. ES buys its own dips at the session horizon.
- **Time-of-day** means are mostly noise (open 09:30 is the highest-vol bucket; a thin 23:00 overnight
  blip reads t=3.2 but is microstructure, not a tradeable clock). **Day-of-week**: Monday RTH +6.88,
  Thursday -3.85 — noisy, and DOW is a closed NULL (GENESIS_H2), so not to be over-read.
  Full 30-min table: `out/returns_by_tod.csv`.

## 3. DISTRIBUTION

- **1-min returns:** std 1.47pt, skew +0.75, **excess kurtosis 193** (extreme fat tails);
  P(|1-min move|>3pt)=3.98% (~1 per 25 bars), >8pt=0.29% (~1 per 350).
- **Daily RTH return:** std **45.3pt**, skew **+0.68** (positive — the big days are UP days),
  exkurt 15.4; range [-254.75, +506.50] (the +506 is an April-2025 tariff-vol day).
- **Overnight gap:** std **34pt**, skew **-0.32** (the gap tail is a gap-*down* tail), exkurt 5.6;
  **|gap| mean 23.6pt, 67.5% of sessions gap >10pt** — overnight risk transfer is large.
- **Overnight range ≈ RTH range (median ratio 1.02; ON 65.3pt vs RTH 62.0pt).** ES's overnight is
  **not** quiet — it carries as much range as the day session. This matters: an "overnight = low
  information" prior is false for ES.
- **Vol regimes are sharp:** daily RTH realized vol (pt) 2022≈44 → 2023≈27 → 2024≈30 → 2025≈43
  (max 287) → 2026≈46. Big-day frequency (|RTH|>60pt) swings 5.6%→23.2% across years.

## 4. DEPENDENCE — the load-bearing section

- **Intraday 1-min is a near-perfect martingale:** all autocorrelations ≈0, **VR(q)≈1.00 at
  q=2,5,10,30,60**, sign persistence 49.0%. There is **no linear intraday drift structure** to trade
  in the return series itself.
- **Daily returns MEAN-REVERT:** `acf(1) = -0.103`, and **variance ratios fall well below 1 —
  VR(2)=0.90, VR(5)=0.80, VR(10)=0.75.** This is the defining ES phenotype: at the session/multi-day
  horizon ES is *anti-persistent*, the opposite sign of a trend/momentum instrument.
- **Volatility is the most forecastable thing in ES:** daily RV `acf(1)=0.69, acf(5)=0.39`;
  `|1-min ret| acf(1)=0.32` decaying slowly to +0.19 at lag 390. Strong, persistent vol clustering.
- **After a large 1-min move**, P(continue)=48.2% vs a 42.6% small-move baseline — a *weak* relative
  continuation tell but still sub-50% and `E[next same-dir]=-0.15pt`: no exploitable intraday momentum.

## 5. PATH GEOMETRY

- **Kaufman efficiency ratio median 0.050 (mean 0.058)** — ES RTH days are **extremely choppy**;
  price travels ~20× its net displacement (tortuosity median 19.97). Captured fraction of the daily
  range = 0.52 (price closes near the middle of its range on average). This is a mean-reversion path
  signature, consistent with §4.
- **MFE ≈ MAE from the open (median 23pt each, ratio 1.02)** — excursions are symmetric; ES has no
  intraday long/short excursion bias.
- **Range clustering is strong:** RTH range `acf(1)=0.557, acf(2)=0.522`. But **NR7 compression does
  NOT reliably precede expansion** — next-day range after NR7 = **0.92× average** (compression
  persists, it doesn't explode). The naive "coil → break" story is already weakly refuted here.

## 6. SESSION STRUCTURE

- **Overnight extremes are frequently taken out in RTH:** P(RTH takes out ON high)=52.5%,
  P(takes out ON low)=49.3%, P(RTH stays inside ON range)=16.6% — the overnight range is a live
  reference the day session interacts with, not a container.
- **Opening range rarely holds the day's extreme:** for OR15, day-high-in-OR=17.6%, day-low-in-OR=20.5%;
  ranges expand well beyond the OR most sessions (OR60 break-up-later 65.8%).
- **Gaps fill 62.5% of the time to prior close during RTH** (gap-up fill 60.0%, gap-dn fill 59.5%),
  consistent with the gap-fade in §2 — but note 62.5% is close to what a random walk with this
  range would fill, so any gap-fade claim MUST beat an unconditional geometry control.
- **Prior-day levels:** P(touch prior-day high)=55.4%, P(touch prior-day low)=46.4% (mild upward tilt);
  P(engulf prior-day range)=10.6%.

## 7. NQ CORRELATION — the diversification pre-read (points-return basis)

| basis | Pearson rho (ES pt vs NQ pt) |
|---|---|
| RTH session return | **0.940** |
| overnight gap | 0.945 |
| full-day return | 0.937 |
| RTH Spearman | 0.929 |

By year, RTH rho in [0.907 (2026), 0.964 (2022/2025)] — **stable and high in every regime.** ES and NQ
are the **same equity-index direction factor.**

> **Diversification verdict:** any ES engine whose P&L is essentially *index direction* (a long-biased
> trend/flip engine, a directional vol-timer) is ~worthless to the live NQ book — it re-expresses a
> factor already carried at rho 0.94. **The only ES engines worth building are ones whose P&L is
> orthogonal to shared index direction:** a mean-reversion engine (whose returns load on the reversal
> component, not the direction — and ES's autocorr sign is *opposite* NQ's momentum-flip edge), or a
> point-hedged ES-NQ relative-value residual (zero index beta by construction). This directly shapes
> the ranked hypotheses below.

---

## 8. Wave-2 preregisterable NATIVE mechanism families (ranked)

Ranked by **measured native signal strength × orthogonality to the NQ book × cheapness of the
falsifier.** None is a strategy; each is a single preregistered test against a dependence-preserving
null with its **matched unconditional control** (playbook §4.4), evaluated at the ES cost band
(0.25 tick = $12.50; commission MODELED ~$4.36 RT, FLAGGED). A candidate dead at +1 tick is fragile.

### Family 1 — ES session/gap MEAN-REVERSION (the gap-fade + daily-reversal complex) — RANK 1

- **Economic reason (ES-specific):** ES/SPX is the broadest, deepest, most-hedged index and the
  primary landing zone for the 0DTE-SPX options complex and passive rebalancing/overnight
  risk-transfer flows. Those flows push the overnight gap to over/undershoot; dealer gamma and
  liquidity provision then pull the RTH open back. The autopsy measures this directly:
  `E[RTH|gap-down]=+3.14`, `E[RTH|gap-up]=-1.15`, daily **VR(10)=0.75**, efficiency ratio 0.05,
  daily `acf(1)=-0.103`. Crucially the **sign is opposite** the NQ momentum-flip edge P1 harvests,
  so a MR engine's P&L can be low- or negatively-correlated with the book despite rho=0.94 in raw
  direction — the natural orthogonal complement.
- **Cheapest falsifier:** one preregistered regression of next-RTH point-return on the prior overnight
  gap (points), sign must be **negative** and the gap-conditioned MR expectancy must **exceed the ES
  all-in cost per round trip** and clear a **circular-shift null**. KILL if the coefficient sits
  inside the friction band, or if it fails against its matched **unconditional gap-fill geometry
  control** (gaps fill 62.5% by construction).
- **Must clear (FAILURE_MEMORY):**
  - **G2_F2_SWEEP01** ("response is generic post-cross MR, not level information") — material diff:
    conditioned on the **overnight gap magnitude at the RTH open**, not an intraday level-reclaim; ES
    not NQ; and it must beat the *unconditional* post-open MR control, not just exist.
  - **G2_F2_CLAIMS01** (value-area/VWAP/PDH-PDL all geometry-explained folklore) — must beat the
    unconditional gap-fill/geometry baseline (class-conditional-needs-matched-control law, WE_W111b).
  - **Fade/MR graveyard WE_W108/W118, G2_F2_SWEEP01** (on NQ the fade was the wrong side of a live
    momentum effect) — material diff: **ES daily VR=0.75 is measured here** (NQ was not this
    anti-persistent), the horizon is daily/gap not intraday-trigger, and this is ES's own phenotype.
  - **G2_F6_BREADTHPM01 / G2_F14** (breadth-washout rebound = generic MR) — not breadth-conditioned,
    must not collapse onto the generic-MR control.
  - **GENESIS_H2** (DOW/calendar NULL) and **"overnight drift ~2021" dead external effect** — must be
    gap/return-conditioned (not a calendar effect) and is the RTH *reaction to* the gap (not an
    overnight-hold drift).

### Family 2 — ES-NQ point-hedged RELATIVE-VALUE residual mean-reversion — RANK 2

- **Economic reason (ES-specific):** rho=0.94 means ES and NQ share one factor; the ~6% residual is the
  **value/broad-vs-growth/tech dispersion** (sector rotation, rate-sensitivity of tech), which is
  economically real. A **point-beta-hedged** residual `ES - beta*NQ` (beta from a points regression, NOT
  dollars, NOT %) has ~0 index beta **by construction** — the single family that structurally solves the
  diversification problem the rho=0.94 read exposes. ES's deep, 0.25-tick liquidity makes the tight leg
  cheap to trade.
- **Cheapest falsifier:** estimate the point-hedge beta on the dev window, then test the daily residual's
  autocorrelation / mean-reversion half-life. KILL if the residual `acf` is inside the **two-leg**
  friction band (ES + NQ cost), or if the half-life is <=1 bar (already arbitraged away).
- **Must clear (FAILURE_MEMORY):**
  - **WE_W122 / ESNQ** (ES<->NQ sub-minute cross-market state closed, -$503/session) — material diff:
    **daily** residual MR, not sub-minute/1-min taking; the ms-arbitrage that killed W122 does not
    operate at a daily horizon.
  - **GENESIS_H3 XSMOM** (cross-sectional momentum NULL, P&L=structure) — this is the **reversal
    mirror at the pair level**, not cross-all-roots momentum.
  - **WE_W101 §5.7** (standalone cross-market engines **0-for-15**; only the *conditional* form ever
    cleared) — this fights an adverse prior and likely needs a conditional form; ranked 2 for that
    reason, but the falsifier kills it fast if the residual is arbitraged.

### Family 3 — ES vol-regime state → direction-NEUTRAL expansion/range harvest — RANK 3

- **Economic reason (ES-specific):** RV `acf(1)=0.69` and range `acf(1)=0.557` are the most
  forecastable structures in ES, with sharp regime shifts (2023–24 calm → 2025 hot). Because a
  *directional* vol-timer is non-orthogonal to NQ (and already closed), the ES-native play is to use
  the vol STATE to time a **direction-neutral** structure (range/expansion capture) whose P&L is
  orthogonal to index direction. ES's tight tick is what could let such a harvest survive friction
  where NQ would not.
- **Cheapest falsifier:** does a compression indicator (trailing-range percentile / NR-style) predict
  next-session **absolute** range (expansion) **beyond an HAR-RV baseline**, with the MDE computed
  *before* looking? KILL if `dR2 < MDE`. Adverse prior already visible: **NR7->next range = 0.92x**
  (compression persists, doesn't expand), so this is ranked last and expected to die cheaply.
- **Must clear (FAILURE_MEMORY):**
  - **G2_F11_MC54LEG2** (vol seasonality NOT-IDENTIFIED, VIF 92.86) — must use a **non-collinear**
    state extraction (per-minute/multi-window), never a fixed-window deseasonalization.
  - **G2_F3_VOLSIZE01** (vol-state sizing = tail-only, below its null) and **MC-35 block** (sizing P1
    on existing surfaces = rescue) — must be a **new direction-neutral forecast target**, not a
    sizing overlay on a directional engine.
  - **G2_F13** (ZB intraday state made the NQ RV forecast *worse*; the "last new raw surface" retired)
    — the vol state here must be **ES-endogenous**, not a cross-asset conditioner.
  - **ERABREAK01 doctrine** — modern-window only; pre-2022 intraday-vol stats are inadmissible priors.

---

## 9. Files

- `src/autopsy_es.py` — the full autopsy program (all numbers reproducible from this one file).
- `out/returns_by_tod.csv` — 30-min time-of-day 1-min mean point-return table.
- `out/returns.txt` · `out/distribution.txt` · `out/dependence.txt` · `out/path.txt` ·
  `out/session.txt` · `out/nq_correlation.txt` — the §9 descriptive tables.

**One-line phenotype:** *ES is the broad, mean-reverting equity index — near-martingale intraday,
anti-persistent daily (VR10=0.75), choppy paths (ER=0.05), a strong gap-fade, large-and-informative
overnight range, and powerful vol clustering — and it is rho=0.94 to NQ, so its only portfolio value is
a mechanism orthogonal to shared index direction (mean-reversion or a hedged ES-NQ residual).*
