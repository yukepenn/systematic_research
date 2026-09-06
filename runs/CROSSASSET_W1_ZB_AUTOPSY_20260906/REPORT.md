# ZB MARKET AUTOPSY — Cross-Asset Wave 1 (Lane B, descriptive science)

**Run:** `CROSSASSET_W1_ZB_AUTOPSY_20260906` · **Instrument:** ZB (CBOT 30-yr US Treasury bond
future), $1,000/pt, 1 tick = 1/32 = 0.03125 pt = $31.25 · **Evidence status: DISCOVERY_CONSUMED.**
This is a market autopsy, not a falsifiable test — no ledger trial, no strategy, no P&L, no
promotion. $0. Live book `2047681` untouched.

**Substrate:** `runs/SM1M_ZB_SUBSTRATE/out/zb_1m_2023_2026.parquet` (additive back-adjusted
continuous front-month, END-stamped ET, OHLCV, 1/32 grid restored, volume = true front).
**SEAL enforced:** hard-drop trade-dates >= 2026-08-01 at load (0 dropped — export was pre-capped).
**Retained window: 2022-12-27 -> 2026-07-31, 923 sessions, 1,086,151 1-min bars.**

**DISCIPLINE — POINTS BASIS ONLY (DELEV01 law).** The series is additively back-adjusted, so
absolute levels are shifted; every return / range / gap / threshold below is a **point difference**,
never a percent of price and never a level threshold. Intraday continuity is clean (no roll-gap
contamination); levels are not usable.

---

## 0. NATIVE SESSION (determined from ZB's own volume profile — NOT assumed)

ZB is a **genuine near-24h rates market**, unlike the equity indices. Volume share by ET hour:

| block | volume share | character |
|---|---|---|
| 02:00–07:00 ET | ~15% | real European / London liquidity (the "overnight" is NOT dead) |
| **08:00–16:00 ET** | **~73% in 8h** | **US cash-Treasury day session** |
| 18:00–01:00 ET | ~5% | thin Asian session |

- The tightest contiguous clock window holding **90% of volume spans 03:53 -> 17:00 ET (13 h)** — a
  structural fact that separates ZB from NQ/ES (whose overnight is nearly empty).
- Volume steps **3.7% (07h) -> 11.8% (08h)** at 08:00 ET and stays >6.5% through 16:00 ET.
- **Highest-volume single minutes** are the **08:30 ET data-release cluster** (08:31, 08:32, ...), the
  **08:20 pit open**, and the **16:00 ET settlement runup** (the single largest minute).
- **ADOPTED PARTITION** (economically grounded in the profile, used for all session-structure work):
  **RTH-equivalent day session = [08:00, 16:00) ET** (brackets the 08:20 pit open, 08:30/10:00 data
  releases, and 16:00 settlement); **Overnight = complement within the 18:00->17:00 container.**
  Note this **starts 08:00 ET, 90 min before NQ's 09:30** — copying NQ's session would have been wrong.

---

## 1. RETURNS (points)

- **No meaningful directional drift.** Full close-to-close mean **−0.019 pt/session ($−18.6, t −0.69)**
  over the window — bonds drifted marginally down in the higher-for-longer era, but not
  significantly. Contrast NQ's strong up-drift; ZB is essentially driftless. RTH day open->close
  **+0.0024 pt (t 0.11)**; the weak net move lives **overnight (−0.022 pt, t −1.35)**, not in the US day.
- **Intraday drift concentration:** the **08:00 ET hour is the highest-vol hour (1-min sigma 0.049 vs
  ~0.020–0.027 elsewhere)** and carries a negative average return (−0.00025 pt/min) — the data-release
  reaction window. 14:00 ET hour also negative (−0.00019). Midday (12:00–13:00) and 15:00 mildly positive.
- **Day-of-week (session cc):** only **Monday** stands out — **−0.125 pt/session ($−125, t −2.07)** —
  the rest are |t|<1.1. With 5 uncorrected tests this is a descriptive curiosity, not a claim.
- **Conditioning is flat.** After a prior-UP session next cc = −0.033 (t −0.81); after prior-DOWN
  = +0.006 (t 0.17); daily lag-1 autocorr **−0.024**. RTH return vs overnight-return sign: both ~+0.01
  (t~0.3); corr(overnight, RTH) **−0.021**. No usable same-sign continuation or reversal at the
  session level from these simple conditioners.

## 2. DISTRIBUTION (points)

- **1-min return:** sigma 0.029 pt ($29), skew −0.21, **excess kurtosis +51.7** (very fat, typical of
  1-min). **Daily return:** sigma 0.815 pt ($815), **skew −0.09 (near-symmetric), excess kurtosis +1.40.**
- **Bonds have THIN daily tails vs equities.** Daily empirical |99th| / Gaussian = **1.07x** (1-min
  1.25x). The daily distribution is close to Gaussian — a materially different tail phenotype from
  NQ, whose binding constraint was the left tail. **ZB's binding constraint is NOT a fat left tail.**
- **Extreme 1-min moves:** |ret|>=4 ticks 0.44% of bars (~1/227); >=8 ticks 0.04%; >=1 full point 0.001%.
- **Overnight gap** (prior RTH close -> RTH open): mean −0.022 pt, sigma 0.49, skew −0.24, kurt +4.2;
  **|gap| is small — median |gap|/RTH-range = 0.35.** Bonds barely gap (they trade continuously).
- **Overnight range ~ RTH range.** RTH mean range **0.99 pt** vs **overnight 1.02 pt** — the overnight
  session carries as much range as the US day. RTH holds only **86%** of the full-session range.
- **Daily realized vol** (sqrt of sum of 1-min sq. pt-returns): mean **0.97 pt ($966)**, median 0.92,
  p5 0.71, p95 1.38.

## 3. DEPENDENCE (points) — the load-bearing section

- **ZB is a MEAN-REVERTING market at every horizon.** Variance ratios:
  - 1-min: **VR(2)=0.85, VR(10)=0.70, VR(60)=0.65** (strong intraday mean reversion).
  - daily: **VR(2)=0.98, VR(10)=0.89, VR(20)=0.86** (mild but consistent daily mean reversion).
  - 1-min lag-1 return autocorr **−0.146** (partly bid-ask bounce — treat sub-5-min MR as microstructure).
  - Signed continuation after a top-decile 1-min move = **−0.007 pt (reversal)**.
  - **This is the opposite of NQ**, where continuation won at the same trigger bars (WE_W118).
- **Vol clustering is the STRONGEST dependence in the market.** Daily RV autocorrelation
  **0.58, 0.52, 0.47 ... 0.19** (lags 1–10) — slow-decaying, highly forecastable vol state. |ret| ACF
  ~0.12–0.18 at both frequencies; RTH-range ACF 0.28.
- **Sign persistence** is near-random at the daily level (P(same sign) 0.498 vs iid 0.501).

## 4. PATH (points)

- **Extremely choppy paths.** RTH Kaufman **efficiency ratio median 0.043** (mean 0.047);
  **tortuosity median 23x** (the day's path is ~23x its net displacement). Consistent with VR<1.
- **MFE/MAE symmetric from the open** — MFE mean 0.49 / MAE 0.50, **ratio 0.98**: no long or short
  intraday bias. Median net move = **0.49x the RTH range** (price ends mid-range — again MR-consistent).
- **Compression->expansion (NR7 coil-then-break) is REFUTED for ZB.** Bottom-quartile range days are
  followed by **LOWER** next-day range (0.84) and top-quartile by **HIGHER** (1.18) — this is **vol
  PERSISTENCE, not compression->expansion.** Range ACF ~0.28.

## 5. SESSION STRUCTURE (points)

- **Not an opening-range market.** The first-30-min OR holds the day extreme only **~21%/21%** of
  sessions (rest-of-day breaks the OR high 78% / low 79%); first-60-min ~36%. ORB-continuation is
  structurally unlikely here (contrast equities).
- **Overnight levels matter (ETH is liquid).** RTH takes out the overnight high **48.7%** / low
  **52.7%**; takes out **both 19.3%**, **neither 17.9%** — much less one-sided extension than equities
  because the overnight already ranged widely.
- **Gap fill ~57–58%** both directions (up-gap 58.5%, down-gap 57.3%) — modest, MR-consistent, but
  gaps are tiny.
- **Prior-day levels:** takes out PDH 47.3% / PDL 51.3%; **inside prior-day range only 11.5%** — a
  wide-ranging market that routinely exceeds prior-day extremes (no strong level-magnet effect).

## 6. DIVERSIFICATION PRE-READ — daily point-return correlation to NQ

- Shared trade-dates 2022-12-28 -> 2026-07-31 (n=922), points-return basis (both series additively
  back-adjusted -> point returns are the correct basis).
- **Pearson rho(ZB, NQ) = +0.064** (Spearman +0.091). P(opposite daily sign) **45.4%**.
- Per-year: 2023 **+0.165**, 2024 **+0.015**, 2025 **−0.069**, 2026 **+0.255** — hovers around zero,
  no persistent sign.
- **READ: ZB is ~orthogonal to NQ.** Under the campaign's orthogonality-is-first-class doctrine, even
  a modest-Sharpe ZB engine would carry real marginal portfolio value against the NQ book. This is the
  single most important cross-asset fact from the autopsy.

---

## 7. Preregisterable NATIVE mechanism families (ranked) — for Wave 2

Each is a family to preregister, not a strategy. Points basis; cost band mandatory (ZB commission
MODELED ~$4.36/RT, spread unmeasured — a candidate dead at +1 tick ($31.25) is fragile); each carries
a dependence-preserving null and its matched unconditional control.

### Family 1 (top) — Scheduled-macro-release VOLATILITY/PATH structure at 08:30 ET (+10:00, +14:00 FOMC)
- **Economic reason (ZB-native):** ZB is the duration instrument; US rates data (NFP/CPI/PPI/retail
  at 08:30 ET, ISM/JOLTS at 10:00 ET, FOMC at 14:00 ET) discretely reprices the discount curve. The
  volume/vol profile proves this: 08:30 minutes are the single highest-vol minutes and the 08:00
  hour has ~2x the vol of any overnight hour. This is a **vol-transition / event-path** family (how
  vol and the post-release path behave on a pre-announced calendar), **not** a directional macro bet.
- **Cheapest falsifier:** realized vol (points) in 08:30–09:00 on scheduled-release days vs matched
  non-release days, powered, MDE printed first; then post-release continuation-vs-reversion of the
  first move. If the vol expansion isn't present/powered, or the path is directionless net of ~2-tick
  cost, dead.
- **Graveyard clearance:** must differ materially from **G2_F12** (FOMC vol EXPANDS x5.66 — banked,
  but that is NQ at 14:05–15:30; a ZB-native 08:30-data vol/path structure is a different
  instrument/observable/time). Must NOT collapse to **GENESIS_H2 / G2_F1_TICK01** (calendar-day-type ->
  same-session mean = NULL) — this is vol/path, not a mean-return-by-calendar bet. Must NOT be
  **G2_F10** (overnight hold into NFP/CPI on NQ = absent premium) — this is a ZB intraday reaction,
  not an overnight directional carry. 08:30-data days are ~50–100/yr (not as N-bound as FOMC's ~8/yr),
  but MDE-before-looking (WE_W57 discipline) is mandatory.

### Family 2 — Intraday MEAN-REVERSION / range-fade (ZB's choppy microstructure)
- **Economic reason (ZB-native):** efficiency ratio 0.04, VR(60)=0.65, tortuosity 23x — ZB's intraday
  path is dominated by mean reversion far more than equities, because rates are anchored by the cash
  Treasury market and dealer/RV inventory trading; ranges are tight and revert (net move = 0.49x range).
  Fade displacement from an intraday anchor (open / prior settle / session VWAP).
- **Cheapest falsifier:** after a k-tick displacement, next-window reversion vs continuation at a
  **tradeable horizon (5–30 min, beyond bid-ask bounce)**, net of the ~1-tick spread ($31.25) and
  commission. The −0.007 pt 1-min "reversal" is partly microstructure and must NOT be quoted as edge;
  the real test is whether MR survives at a horizon and net of cost. Dies cheapest on cost: median RTH
  range is only ~0.9 pt (~29 ticks), so per-fade edge is small.
- **Graveyard clearance:** the NQ fade graveyard (**WE_W108/W118, G2_F2_SWEEP01**) is NQ-specific —
  there continuation won (VR>1 / momentum). ZB has the **opposite** structure (VR<1 at every horizon),
  which is the material difference that keeps this from being a rediscovery. Must carry its
  **unconditional control** (WE_W111b rule): an unconditional fade must not reproduce the signature.
  Not an ORB (G2_F1_ORB01) — OR holds the day extreme only 21%, so this is explicitly a fade, not a break.

### Family 3 — VOL-STATE forecasting as a RISK-SPECIFICATION / regime layer (persistence, not coil)
- **Economic reason (ZB-native):** daily RV autocorr **0.58->0.19** is the strongest, most forecastable
  dependence in the entire autopsy; range ACF 0.28. High vol follows high vol. Usable as a **sizing /
  regime-routing layer** (including for a cross-asset portfolio), explicitly **NOT** standalone
  information alpha. Note the NR7 "coil-then-break" folklore is **refuted here** (compression is
  followed by lower range) — the mechanism is persistence, not expansion-after-compression.
- **Cheapest falsifier:** a 1-day-ahead **HAR-RV forecast on ZB points-RV** must beat a random-walk RV
  forecast OOS (DM/QLIKE) by more than its MDE; any sizing overlay must clear the **count-matched
  random-thinning placebo** (eval_battery.py, lead with weekly-vol) and never be a fixed-DD artifact.
- **Graveyard clearance:** must avoid the **G2_F11** collinearity trap (fixed-window diurnal
  deseasonalization was NOT-IDENTIFIED, VIF 92.9 — use multi-horizon HAR, not a single-window
  deseasonalization). Different target from **G2_F13** (that was ZB->NQ RV, FAILED; this forecasts
  ZB's own forward vol). Must beat **G2_F3_VOLSIZE01**'s bar (extremes-only NQ vol-sizing FAILED —
  tail-only, below its null): the improvement must be classified RISK-SPECIFICATION, never dressed as
  information alpha (CLAUDE.md §4). Points-RV only (DELEV01).

**Ranking rationale:** Family 1 is the most ZB-native and least likely to be an NQ rediscovery (the
volume profile is the evidence). Family 2 is strongly supported by VR/efficiency but has the highest
cost-mortality risk (thin per-fade edge). Family 3 is the most robust phenomenon but is a
risk/diversification layer, not standalone alpha, and sits closest to closed vol-forecasting work — so
ranked third despite being the surest thing in the data.

---

## 8. Deviations from the brief / caveats

- **§9 protocol:** NQ_RESEARCH_PLAYBOOK.md and CAMPAIGN_STATE.md contain no literal "§9" section;
  the "§9 protocol" is the descriptive-science structure the task enumerates and the playbook spells
  out at §2-step-1 ("DESCRIPTIVE — instrument-native sessions") and transfer-checklist step 6. I
  executed that structure (RETURNS / DISTRIBUTION / DEPENDENCE / PATH / SESSION STRUCTURE + rho-to-NQ).
- **Native session:** the volume-derived 90%-mass window is 13h wide (ZB is near-24h). I report that
  finding but adopt the economically-grounded US cash-Treasury day session **[08:00, 16:00) ET** for
  the RTH/overnight partition, because a 13h "RTH" defeats the partition; both are documented in
  out/session_native.txt.
- All significance is descriptive; no headline clears a preregistered bar (none was set — this is an
  autopsy). No probability headline is quoted, so the CAP01 semantic gate is not triggered.

**Deliverables:** src/autopsy_zb.py; out/{session_native.txt, returns.txt, returns_by_tod.csv,
distribution.txt, dependence.txt, path.txt, session.txt, correlation_nq.txt}; this REPORT.md.
