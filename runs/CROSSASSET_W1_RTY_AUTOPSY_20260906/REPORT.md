# RTY MARKET AUTOPSY — Cross-Asset Wave 1

**Run:** `CROSSASSET_W1_RTY_AUTOPSY_20260906` · **Instrument:** RTY (E-mini Russell 2000), point value **$50/pt**
**Status:** DESCRIPTIVE SCIENCE / DISCOVERY_CONSUMED. No strategy, no P&L, no ledger trial, no promotion.
**Basis discipline:** POINTS ONLY (substrate is additively back-adjusted — DELEV01 law; every return/range/threshold is a POINT difference, never % of price, never a level threshold).
**Substrate:** `runs/SM1M_RTY_SUBSTRATE/out/rty_1m_2022_2026.parquet` (1-min OHLCV, END-stamped ET, additive back-adjusted continuous front-month).

---

## 0. Data boundary & session (both determined, not assumed)

- **Seal:** retained bars `2022-01-02 18:01 .. 2026-07-31 16:59 ET`; **retained sessions `2022-01-03 .. 2026-07-31`**. Hard-drop rule for sessions >= 2026-08-01 fired on **0 rows** — the substrate already ends before the seal. Nothing >= 2026-08-01 was read.
- **n sessions = 1,177** raw; **1,175 with an RTH block**; **1,174** usable daily point-returns (one lost to the first-session lag). 43 half-days (RTH ended <16:00 — US early closes at 13:00/13:15; retained, flagged).
- **Identity gate:** `ret_c2c == ret_on + ret_rth` reproduced to max abs diff **0.000000 pt** across all sessions.

### NATIVE SESSION (from RTY own volume profile — see `out/volume_profile.txt`)
- **ETH (full electronic): 18:00 -> 17:00 ET** (~23h; 1,380 distinct minute-of-day buckets = 23h), with a **maintenance halt 17:00->18:00** (hour-17 volume share 0.05%, ~1,131 stub bars).
- **RTH (cash-equity core): 09:30 -> 16:00 ET.** First RTH bar END-stamped **09:31** (opens 09:30; volume jumps 0.28M->3.39M at that mark); last RTH bar END-stamped **16:00**, which carries a **9.97M settlement print** (5–10x the neighbours).
- Volume mass concentrates in the **open drive (09-10h = 31.8%)** and the **cash close (15-16h = 22.0%)** — textbook CME equity-index shape, **confirmed on RTY own tape, not copied from NQ**.

---

## 1. RETURNS (points)

### The single dominant return fact: **drift is ~entirely OVERNIGHT.**
| segment | n | mean (pt) | std (pt) | sum over window (pt) | skew | ex-kurt |
|---|---|---|---|---|---|---|
| RTH intraday (open->close) | 1,175 | +0.0448 | 24.53 | **+52.6** | +0.08 | +3.10 |
| Overnight (prevClose->open) | 1,174 | +0.2927 | 18.22 | **+343.6** | -0.07 | +5.51 |
| Close-to-close (daily) | 1,174 | +0.3239 | 29.42 | +380.3 | +0.03 | +1.47 |

Over 4.5 years RTY positive drift (+380 pt daily) is **90% carried overnight** (+343.6 pt) — RTH is a near-zero-drift, higher-*variance*, mean-reverting arena. (Note: with overnight defined close->open, the **overnight return and the opening gap are the same quantity** in this autopsy.)

### Time-of-day (30-min buckets, contiguous 1-min close-to-close — `out/returns_by_tod.csv`)
- Nearly all buckets are individually insignificant. Two nudge past |t|~2 on ~35k obs: the **09:00 pre-open bucket** (08:59–09:29) mean -0.0128 pt/min, **t = -2.92** (a small pre-open drift-down), and the **13:30 bucket** +0.0109 pt/min, t = +2.15. The **09:30 RTH-open bucket has the highest 1-min variance** (std 2.08 pt) — vol, not drift, is what the open delivers.

### Day-of-week (per-session point returns)
- **Monday is the only strongly positive day: c2c +2.98 pt** (both RTH +1.82 and ON +1.22); **Thu -0.88, Fri -1.16**. A turn-of-week tilt is visible descriptively — but cells are small (n~233, std 25–31) and **DOW is a FAILURE_MEMORY closure** (GENESIS H2 NULL, re-measured NULL 2026); recorded as description only, not a lead.

### Conditional on prior sign (reversal tendency)
- **After a DOWN day: next c2c +1.53 pt (P up 54.0%); after UP: -0.84 pt (P up 48.6%)** — a mild daily *reversal*.
- **Gap does not continue intraday, it fades weakly:** after a gap-up, RTH mean -0.91 pt; after gap-down, RTH +1.11 pt.

---

## 2. DISTRIBUTION (points)

- **Daily c2c:** std 29.42 pt (**~ $1,471**), skew +0.03, **excess-kurt +1.47** (mild fat tails); 1%/99% = -76.5 / +68.4 pt; min/max -134 / +151.
- **Overnight is the fat-tail carrier:** ex-kurt **+5.51** (vs RTH +3.10) — the segment that holds the drift also holds the jump risk. |z|>4 empirical **0.51%** overnight vs 0.006% Gaussian.
- **1-min RTH:** std 1.27 pt (~$63), skew +0.58, **ex-kurt +35.9** — heavy microstructure tails (min/max -37.8 / +56.5 pt).
- **Gaps are large:** |gap| median **9.6 pt**, mean 12.9 pt; **48.2% of sessions gap >10 pt**; only 11.9% gap <2 pt. P(gap up) 52.3%.
- **Range:** RTH range mean **36.7 pt** vs overnight range 26.8 pt (**RTH/ON range ratio median 1.44**); opening-range (first 30 min) mean 17.5 pt.
- **Realized vol (sqrt sum 1-min sq, pt):** RTH RV mean 22.9, overnight RV 17.8 — **overnight RV is ~78% of RTH RV** (a lot of RTY variance, not just its drift, is overnight). RTH/ON RV ratio median 1.40.

---

## 3. DEPENDENCE (points)

- **Returns are unforecastable; volatility is highly forecastable.** This is the core dependence fact.
  - Return ACF ~ 0 at every lag (daily L1 -0.016; **1-min RTH L1 +0.0008**).
  - **Variance ratios** (Lo-MacKinlay, corrected): 1-min RTH **VR~1.00 at all q** (pure random walk — consistent with the ~0 ACF, a self-check); **daily** VR(2)=0.99, VR(5)=0.91, VR(10)=0.87, **VR(20)=0.80**; **RTH-to-RTH** VR(2)=0.97 … **VR(20)=0.72** — mild-to-moderate mean reversion that grows with horizon and is stronger on the RTH leg.
  - **Vol clustering is strong and persistent:** RTH-RV ACF **L1 +0.595**, L5 +0.348, L20 +0.169; daily-range ACF L1 +0.417. |daily return| ACF is weak (L1 +0.09) — it is the *range/RV* that clusters, not signed magnitude.
- **Sign persistence:** daily **47.4%** (below 50 -> slight anti-persistence), RTH 49.7%, overnight 51.5%.
- **Continuation vs reversal (magnitude):** prior bottom-tercile day -> today +1.81 pt (P up 53.7%); prior top-tercile -> -0.53 pt — a mild reversion after extremes, not a momentum tell.

---

## 4. PATH (points)

- **Extremely low intraday efficiency / high tortuosity:** Kaufman ER per RTH session **mean 0.057, median 0.050**; **tortuosity (1/ER) median ~ 19.9**. Median daily path length **305 pt** for a median net displacement of **14.6 pt** — RTY RTH path is very choppy relative to where it ends up (a mean-reverting/liquidity-provision signature, not a trending one).
- **MFE/MAE (long-frame from RTH open):** MFE mean 17.8 pt, MAE mean 18.8 pt (symmetric unconditionally). **Directionally clean:** on UP days median MFE 23.8 vs median heat (MAE) 7.1 -> **heat/target ~ 0.30**; on DOWN days median MAE 25.4 vs heat 6.5. On a day that resolves directionally, adverse excursion is ~30% of the favorable move.
- **Compression persists — it does NOT precede expansion.** RTH-range ACF L1 +0.42; next-day range after a **bottom-tercile (compressed) day = 30.3 pt vs 39.9 pt after a non-compressed day**. The naive "coil -> breakout" story is *backwards* here at daily scale (compressed begets compressed). Pre-register this expected sign before any expansion test.

---

## 5. SESSION STRUCTURE (points, descriptive)

- **Overnight extremes get run in RTH:** RTH takes out the overnight HIGH **60.1%**, overnight LOW **60.8%**, **both 26.7%**, and stays inside the overnight range only **5.7%** — i.e. RTH breaks >=1 overnight extreme ~94% of sessions.
- **Opening range (09:30–10:00):** OR ~ **50.7% of full RTH range** (median); RTH stays entirely inside the OR only **0.9%** (99% break one side); session high set inside OR 35.8%, low inside OR 33.7%. When the OR high breaks, close finishes above it only **54.1%** (weak follow-through — consistent with the low ER / MR read).
- **Gaps fill often:** gap-up filled (RTH revisits prior close) **63.7%**, gap-down filled **60.3%**.
- **Prior-day levels:** PDH touched **50.4%**, PDL touched **49.7%**, RTH inside prior-day range only **10.5%**. (Level-magnetism is *geometry* — MC-07/SWEEP01 closed this class; recorded as description.)

---

## 6. NQ CORRELATION — the diversification pre-read (`out/nq_correlation.txt`)

Daily **POINT-return** correlation on **1,174 shared sessions** (2022-01-04 .. 2026-07-31):

| basis | Pearson rho | Spearman |
|---|---|---|
| daily close-to-close | **+0.7506** | +0.7226 |
| RTH intraday | +0.7444 | +0.6853 |

Per-year daily-c2c rho: 2022 **0.906**, 2023 0.618, 2024 0.600, 2025 0.804, 2026 0.747.

**READ:** RTY is another CME equity-index and co-moves strongly with NQ (rho ~ 0.75, higher in stress years). **As a directional clone it adds almost nothing to the book.** Any RTY contribution must come from a **native mechanism whose *underwater curve* decouples** from the live NQ momentum object — not from index beta. This is the binding constraint on every hypothesis below and elevates mechanisms that are *contrarian to NQ momentum* or *idiosyncratic in timing* (flow events, vol-state risk transforms) over anything that is just "long small-caps."

---

## 7. WAVE-2 HYPOTHESES — native mechanism families this structure suggests (ranked)

Each is a *family*, preregisterable as a single dependence-preserving test with its matched control — **not** a grid search. Ranked by (defensibility given the autopsy) x (orthogonality potential to NQ) x (distance from the graveyard).

### RANK 1 — `RTY-VOLSTATE`: volatility as RISK SPECIFICATION (not return timing)
- **Economic reason (RTY-specific):** the one thing RTY forecasts about itself is its **variance** — RV ACF L1 0.595, range ACF 0.42, compression persistence — while its returns are a random walk (1-min VR~1, ACF~0). Small-caps carry pronounced credit/rate-sensitive vol regimes, so a *variance* handle is where the information is. Used as a **risk/DD transform on a native RTY return engine (or on the book)**, a vol-state control is plausibly orthogonal to NQ direction (it is a risk transform, not a directional bet).
- **Cheapest falsifier:** (a) does a plain HAR-RV / trailing-RV forecast of RTY rest-of-session (or next-day) RV beat a random-walk RV forecast **OOS on QLIKE/DM**? and (b) does vol-scaling **reduce maxDD/CDaR beyond its rate-matched random-thinning placebo** (`eval_battery.py`)? If the placebo matches the DD reduction, it is thinning not information -> KILL. Pre-register the compression sign as **compressed->compressed** (Section 4), so a "coil-breakout" reading is falsified by construction.
- **Must clear (graveyard):** `G2_F11_MC54LEG2` (fixed-window diurnal-deseasonalized RV = NOT-IDENTIFIED collinearity defect, VIF 92.86 — so use plain HAR / a *non-collinear* deseasonalization, never fixed-window diurnal); `G2_F3_VOLSIZE01` (vol-managed sizing gave **no growth timing, tail-only benefit** — so this MUST be framed as RISK SPECIFICATION / DD, explicitly *not* as return growth, which is exactly the NOT-CLOSED lane "vol-state as RISK SPECIFICATION (sizing)"); `G2_F1_COND01` (RV-tercile-as-ORB-conditioner was 5.5x under MDE). Materially different: different market (RTY, higher small-cap vol) and a DD/tail objective judged on the weekly-vol + placebo battery, not a growth claim.

### RANK 2 — `RTY-RECON`: Russell reconstitution / index-rebalance flow structure
- **Economic reason (RTY-specific, and the only one orthogonal to NQ *by construction*):** RTY is the **one instrument in the book with a massive, calendar-fixed, mechanical flow event** — the annual **Russell reconstitution** (late June, effective the Friday after the June quad-witch) plus quarterly IPO adds. Index funds tracking Russell must execute enormous size at the reconstitution close; this is a documented, *Russell-native* microstructure event that ES/NQ/YM do **not** share. Its timing is idiosyncratic to the Russell calendar, so its P&L is mechanically decoupled from NQ momentum — the exact orthogonality the book needs.
- **Cheapest falsifier:** on a **points basis**, is there abnormal RTY return / RV / **RTY-minus-ES spread** behavior in the reconstitution window (rebalance day +/-k) vs matched non-event days — and is it **powered**? Compute the **MDE before looking** (n ~ 1 reconstitution/yr x 4.5 yr + a few quad-witch/add dates ~ 20–25 events): almost certainly **UNDERPOWERED**. Pre-declare it as a *measure-once-descriptively* item, not a wave to spend.
- **Must clear (graveyard):** the **rare-event-collapse lesson** — `G2_F1_TICK01` (events 44->2/yr collapsed the class) and `G2_F10 / MC-50` (macro-calendar premium NULL, "no model or money moves an N-bound gate"). RTY-RECON is materially different (it is a *structural flow* event, not a macro-surprise or a rare price event), but it inherits the **N-bound veto**: if MDE >> |effect|, it is marked UNDERPOWERED and not pursued as a monetizable edge.

### RANK 3 — `RTY-RTHMR`: intraday RTH mean-reversion / gap-fade, vs NQ live momentum
- **Economic reason (RTY-specific cross-market contrast):** RTY RTH is a **mean-reverting arena** (RTH VR falls to 0.72 at 20 sessions; ER median 0.05 / tortuosity ~20; gaps fade intraday -0.91/+1.11; after-down rebound +1.53), whereas the live NQ object pays as **long-only momentum**. Small-cap RTH is dominated by liquidity provision, not mega-cap-tech trend. The portfolio upside: a *contrarian* RTY intraday engine **underwater curve could anti-correlate with NQ momentum P1** (the XM_CONFLICT -0.165-underwater-corr template), which would be worth more than its modest standalone edge.
- **Cheapest falsifier:** does a fade of the RTY overnight-extreme / gap (points, vol-normalized) beat its **matched unconditional control** and clear a **circular-shift null**, *and* does its underwater curve show negative correlation with the NQ object? The descriptive effect is **weak** (VR(2)=0.97; conditional means ~1 pt) — the honest prior is that the cheapest falsifier **kills the standalone edge**; it survives only if the *diversification* leg (underwater decoupling) carries it.
- **Must clear (graveyard):** the entire **fade / mean-reversion graveyard** — `G2_F2_SWEEP01` (sweep-and-reclaim NULL both ways; response is *generic post-cross MR*, no level information), `WE_W108/W109/W118` (7 fade geometries = mirror of a live momentum effect; continuation wins at the same bars), and MC-07 level-magnetism (geometry-explained). Materially different required: a **different market** (RTY *is* structurally more mean-reverting than NQ — a genuine cross-market difference, not a re-run of the NQ fade) and a **portfolio/underwater objective** rather than a standalone return claim. If the fade reproduces as generic geometry (as on NQ), it is a rediscovery and dies.

**Cross-cutting design constraint (from section 6):** with rho~0.75 to NQ, no *directional* RTY engine diversifies on its own. Rank the families by underwater-curve decoupling, not weekly rho — RANK 2 (idiosyncratic flow timing) and RANK 3 (contrarian-to-momentum) are the orthogonality plays; RANK 1 is a risk transform that helps the whole book regardless of direction.

---

## 8. Deviations from protocol
- None material. This is a descriptive autopsy (Lane B, transfer-checklist step 6): **no spec.yaml / prereg_guard** run (that gate binds alpha-bearing *tests*; this is DISCOVERY_CONSUMED description) and **no ledger trial** written (SEARCH_LEDGER untouched, per hard rule). Cost model not invoked (no candidate). Half-days (43) retained for daily continuity and flagged; excluding them shifts RTH means negligibly. Overnight-return and opening-gap are defined identically (close->open) and reported once. Variance-ratio estimator was corrected mid-run to the standard Lo-MacKinlay sigma_c^2/sigma_a^2 form (the 1-min VR~1 self-check confirms the fix).

_Artifacts: `src/autopsy_rty.py`; `out/{returns_by_tod.csv, distribution.txt, dependence.txt, path.txt, session.txt, volume_profile.txt, returns_summary.txt, nq_correlation.txt, autopsy_console.txt}`._
