# MECHANISM COVERAGE MATRIX — 2026-08-26

Owner directive V4 §9: *stop counting strategies, count information sources.* Built from a
four-way parallel mine of `intraday_system`, every campaign in this repo, all 16 vendor manuals +
the deep-research packets, and a full on-disk data census (`DATA_CENSUS_20260826.md`).

Legend: **STRONG** · **SUPPORTED** · **WEAK** · **REGIME_LOCAL** · **NULL** (tested, failed) ·
**·** (untested) · **✗** (no data). A cell is marked from an artifact, not from memory.

---

## 1. The matrix

| mechanism ↓ / information → | OHLC | **volume** | VWAP / value | bid-ask | trade flow | **cross-mkt** | calendar | volatility | higher TF | micro |
|---|---|---|---|---|---|---|---|---|---|---|
| **trend persistence** | **STRONG** | **WEAK**² | SUPPORTED | ✗ | ✗ | NULL | NULL | **STRONG** | WEAK | ✗ |
| **downside persistence** | **WEAK** | **NULL**¹ | WEAK | ✗ | ✗ | · | · | **NULL**¹ | WEAK | ✗ |
| **reversal / failed persistence** | NULL | **NULL**³ ⁶ | **NULL**³ | ✗ | ✗ | · | · | **NULL**³ | · | ✗ |
| **range / value** | NULL | **NULL**³ ⁶ | **NULL**³ | ✗ | ✗ | · | · | **NULL**³ | · | ✗ |
| **market state / action value** | **NULL**⁷ | · | **NULL**⁷ | ✗ | ✗ | **NULL**⁷ | · | · | · | ✗ |
| **volatility transition** | WEAK | **·** | · | ✗ | ✗ | · | · | WEAK | **·** | ✗ |
| **opening auction** | **·** | **·** | · | ✗ | ✗ | · | · | · | · | ✗ |
| **overnight inventory** | NULL | **·** | · | ✗ | ✗ | · | · | · | · | ✗ |
| **event / calendar** | — | · | · | ✗ | ✗ | · | NULL / **·** | · | · | ✗ |
| **order flow** | — | · | · | **·**(45d) | **·**(45d) | · | · | · | · | ✗ |
| **liquidity / book** | — | — | — | ✗ | ✗ | — | — | — | — | **✗ paused** |
| **cross-market** | — | · | · | ✗ | ✗ | **NULL (0/15)** | · | · | · | ✗ |
| **execution** | **STRONG** | · | · | SUPPORTED | · | · | · | · | · | ✗ |
| **management / sizing** | SUPPORTED | · | · | · | · | · | · | **REGIME_LOCAL** | · | ✗ |

> ¹ **W100 (2026-08-26)**, and read the quantifier: `relvol >= 1.0` and
> `rsv_share >= trailing-250-session median`, each as an **acceptance gate on B-MOM's short-leg
> triggers**, are TESTED-NULL — 25.5th and 77.5th percentile of rate-matched random filters.
> Both accepted ~92 % of the target leg, so they were nearly non-binding; that is a design flaw in
> the test as much as a fact about the axes. **Volume as a signal, volume decay, effort-without-
> result, volume spikes, and semivariance as a THRESHOLD SCALE inside the channel remain untested.**
>
> ² **W100**: `relvol >= 1.0` on the LONG leg reached the 98.5th percentile of its rate-matched
> null but not the Bonferroni bar for the family of six. **WEAK**, and it was a control arm, not a
> hypothesis. High-participation *upside* continuation is the one live corner of the volume column.

> ⚠️ **³ IS CORRECTED BY ⁶ BELOW. Read them together — the striking part of ³ turned out to be
> definitional.** The original text is kept verbatim because this repo does not rewrite results.
>
> ³ **W108 (2026-08-27), and this is the most important cell in the table.** Six fade mechanisms
> with participation and path-efficiency terms: primary **−$143/trade, 0.5th percentile**. But
> **all five genuine fades are POSITIVE on RANGE and MIXED and heavily NEGATIVE on both TREND
> classes** — the signs are exactly what the mechanisms predict, and the trend-day losses run
> 2–3× the range-day gains. **So "fading does not work on modern NQ" is TOO STRONG.** The correct
> statement is: **fading works on the sessions it is designed for, and there is no causal trend-day
> veto to keep it off the others.** The missing object is not a better fade — it is a **causal
> trend-day detector**, and building one would make five already-built mechanisms tradeable at
> once. `VWAP_RECLAIM` is separately closed: it earns on trend classes, loses on the two it was
> written for, and its 54.20 % hit rate is indistinguishable from an always-long control's 54.25 %.
>
> ⁴ **W106 (2026-08-27):** four participation mechanisms as DIRECTIONS at 10:01 held to 11:29 —
> primary −$56/trade, 18.0th percentile. `EFFORT_NO_RES` at 25 % acceptance is WEAK ($166,
> clears its own p\*, not the family bar). **`VOL_DECAY` is STILL UNTESTED** — my specification
> fired on 3 of 1,058 sessions.
>
> ⁵ **W107 (2026-08-27):** eight of nine causal states known at 13:29 carry no separating structure
> for the afternoon; the ninth (path efficiency, 13.1 pp spread) is not significant as a trade
> ($53/trade, 78.5th percentile). The afternoon's unconditional tilt is now measured: always-long
> −$66/trade, always-short +$37.
>
> ⁶ ⚠️ **W111 (2026-08-27) — THE VOLUME COLUMN IS NOW MARKED FROM EVIDENCE, AND IT CORRECTS ³.**
> Five continuous participation mechanisms (decay slope, decay ratio, effort-without-result,
> absorption bar, extreme exhaustion) as fade DIRECTIONS at 11:48 held to 15:44, all five clearing
> a preregistered specification gate at 89–99 % of sessions: primary **−$233/trade, 0.0th
> percentile**, all 15 cells negative, and **three of five sit BELOW the 5th percentile of a
> volume-decile-matched null** — anti-predictive, not merely absent. Row #1 of the frontier moves
> **UNTESTED → NULL** after two prior specification failures of mine (W100 accepted 92 %, W106
> fired on 3 of 1,058). Quantifier: *as a fade direction, at this geometry.* Volume as a
> **confidence weight** or as a **threshold scale inside an existing channel** is still untested.
>
> **AND THE CORRECTION TO ³:** `run_we_w111b.py` ran the matched control W108 owed — an
> **unconditional** fade of the morning direction, no mechanism at all — and it produces the same
> −TREND/+RANGE signature at the same magnitudes (**−$943 / −$1,121 / +$470 / +$516**, −$206/trade).
> The W51 taxonomy defines TREND by |close−open| ≥ 0.60 × session range and the afternoon close
> lands on the same side of 09:31 as the 11:29 close on 86.1 % of TREND-UP vs 73.3 % of RANGE
> sessions, so **any** rule trading against the morning direction must show it. **The signature is
> a property of the labels and W108's interpretation of it is WITHDRAWN.** Also: the unconditional
> fade earns −$206/trade against W108's five-mechanism mean of −$183; two of five beat it, three
> are worse. **None of the six was ever shown to beat fading the morning direction unconditionally.**
> Binding from here: **a class-conditional table requires its matched unconditional control in the
> same wave.** This is the second time a striking class table was reproduced by a matched control
> (the first was `VWAP_RECLAIM` 54.20 % vs always-long 54.25 %).
>
> ⁷ **W109 (2026-08-27) — the FADE_HOSTILE_STATE transfer test, and it splits in two.**
> *The policy fails:* six causal states at 11:48 as a binary veto on five frozen fades, three
> alphabetically-fixed for development and **two held out**. Primary **$204/trade on the held-out
> engines vs a rate-matched RANDOM-VETO null whose p95 is $338 → 85.0th percentile, FAILS**; the
> clean single-holdout variant fails at the 82.0th. The mechanism of failure is the **SELECTIVITY
> RATIO** — trend loss removed ÷ range profit removed — which lies between **0.74 and 1.12 across
> all 18 cells**. A veto at this discrimination is exposure reduction, not selection.
> *The information is REAL:* three of the six detectors discriminate ex-post TREND from RANGE/MIXED
> using only pre-11:48 information at **AUC 0.621 (VWAP displacement), 0.617 (directional
> efficiency), 0.613 (repeated extremes)**, all at the 100th percentile of 2,000-draw label
> permutation nulls (bar ≈ 0.535). **That is not definitional** — the detectors see the morning, the
> label sees the whole session. And the detector development P&L selected, `D3_RANGE_EXP`, is one of
> the three carrying **no** class information (AUC 0.525, null).
> **Conclusion: the failure is at the POLICY layer, not the information layer.** This detector family
> is closed to further tuning (§13/§38). The untested successor is §22's continuous action value —
> estimate `E[PnL(fade) | I_t]` and weight exposure by it, instead of thresholding a weak state into
> a binary cut that discards the magnitude information an AUC-0.62 signal carries.

> ⁸ ⭐ **W114 / W117 / W118 (2026-08-27) — THE ROW THAT REPLACES THE FADE ROWS.**
> **Intraday CONTINUATION is live and REVERSAL is on the wrong side of it, at every geometry tested.**
> W118 built the reversal mechanism at its OWN event-driven geometry - the running excursion must
> clear a causal trailing threshold, then a retracement of R triggers entry, so entries are
> endogenous and spread across 10:00-12:00 rather than sitting on W108's fixed midday clock.
> **Primary −$405/trade; the MOMENTUM mirror at the exact same entry bars earns +$374, a delta of
> $778.** Always-long and always-short at those bars earn −$9 and −$22, so it is continuation and
> not drift. All nine cells negative, all nine mirrors positive.
> **§6 DIAGNOSTIC, and it is the valuable part: on 2006-2021 BOTH sides are ≈zero** (reversal −$31,
> momentum −$1). So the continuation edge is a MODERN phenomenon confirmed now by three independent
> constructions - W114's fixed 11:49 clock, W111b's unconditional control, and W118's event-driven
> entry - and absent in the old era at every one of them.
> ⚠️ **Defect disclosed:** W118's first run applied the excursion gate to the 12:00 excursion after
> the fact instead of at the trigger bar, so it fired on the first 2-point wiggle (median entry
> 09:32, 99.4 % of sessions). Repaired; the defective output is preserved in the run directory.
> **Status: REVERSAL is CLOSED AT TWO GEOMETRIES.** Reopening requires NEW INFORMATION, not another
> clock and not another retracement depth.
>
> ⁹ **W117 (2026-08-27) — what the BOOK loses on, measured for the first time.** The candidate
> portfolio loses 87 of 213 weeks. Losing weeks have **fewer TREND-UP sessions (0.167 vs 0.238,
> p=0.005) and more REVERSAL sessions (0.299 vs 0.230, p=0.011)** - and **identical TREND-DOWN share
> (0.147 vs 0.143, p=0.880)**, with 53 % of losing weeks being weeks NQ ROSE. **The book's hole is
> not directional.** Six frozen objects screened against those weeks: **zero survivors**.
> FOLLOW_MORNING's long leg earns $482/week unconditionally and **−$2** on book-losing weeks against
> a random-alignment null of +$484 - absent, not merely weak.

> ¹⁰ **W119 / W120 / W121 (2026-08-27) — THE BOOK-LOSS TRIO.**
> **W119 (`BOOK_LOSS_LEDGER`, 1,058 sessions x 25 cols):** the book's gap is **NOT COVERAGE** —
> `E_NO_ENGINE` = **0 sessions** in four years. It loses on sessions where P1 takes **3.042 entries
> vs 1.377**, for **18 % fewer contract-minutes**, while the market moves **31 % less** and the range
> is barely different. **XM is the tail**: active on 33 % of sessions, present in **69.8 %** of the
> worst decile (+34.3 pp). W119 also **narrows W117** — at session resolution the REVERSAL excess is
> **+1.7 pp**, not the +6.9 pp the weekly aggregation showed, and **RANGE is the larger dollar class**
> (−$114,807 vs −$91,216). The TREND-UP deficit (−8.6 pp) and TREND-DOWN null (+0.8 pp) survive.
>
> **W120:** `MIRROR_CONT` (W118's construction, direction flipped) **fails its four-gate test on gate
> 2 only** — $614 on book-losing weeks against a chance-alignment $663, the 42.9th percentile. It
> passes **both gates FOLLOW_MORNING failed** and would take book max DD **$11,489 → $8,143**, but
> its value is **tail not average**: session-level it is pro-cyclical (**+$1,315** when the book wins,
> **−$297** when it loses) while its weekly tail beta is **−1.861 at the 0.9th percentile on 21
> weeks**. **WATCHLIST**, and it becomes the standing `MIRROR_CONTINUATION_CONTROL`.
>
> **W121 — TURNOVER IS NOT A CAUSAL STATE, and the failure is worse than a null.** Capping P1 at K
> new entries per session is beaten by the baseline at every K AND sits at the **0.0th / 4.0th /
> 1.0th / 0.0th percentile of a COUNT-MATCHED RANDOM-HALT PLACEBO** — **removing the same entries at
> random does BETTER than removing them by the rule.** Stage A shows why: the **4th** entry of a
> session is the **best** cell at **$253/entry** against a $139 unconditional mean, so a cap deletes
> better-than-average entries. **W119's turnover signature is a property of losing SESSIONS, not of
> marginal ENTRIES.** The closed intraday loss-reactivity family is confirmed a fourth time — 72.5 %
> of entries with ordinal >= 2 follow a negative running session P&L, which is the mechanism by which
> entry count and loss count are the same variable.
> ⚠️ **Defect disclosed:** the preregistered Stage-A falsifier had two clauses and I implemented
> only the slope one, so the wave proceeded past a gate its own spec had closed. Binding rule:
> **implement every clause of a multi-clause falsifier in code.**

## 2. ⭐ The single largest hole — **CLOSED as a direction by W111, 2026-08-27**

> ### ⚠️ **THE CLAIM BELOW WAS TRUE WHEN WRITTEN AND IS NOW SUPERSEDED.** W111 used volume as a
> ### signal, five ways, and it **FAILED**: −$233/trade at the 0.0th percentile, and three of the
> ### five mechanisms sit *below* the 5th percentile of a volume-decile-matched null. The
> ### opportunity was real, the data was there, the two prior failures were specification defects
> ### of mine — and once specified so it could actually be measured, **the answer was no**.
> ###
> ### What is *still* open in this column is narrower and must be quoted with its quantifier:
> ### volume as a **CONFIDENCE WEIGHT** on an existing signal, and volume as a **THRESHOLD SCALE**
> ### inside the ratchet or the B-MOM channel. Volume as a standalone **DIRECTION** at 11:48 or at
> ### 10:01 is tested and null. The original text follows unaltered.

> ### **VOLUME HAS NEVER ONCE BEEN USED AS A SIGNAL IN THIS PROGRAM.**
> Every engine ever built here — Solar ratchet, B-MOM, X9a, NETFUSE, the scalping families, the
> system_master engines — is **close-only or range-based**. The `volume` column is empty on every
> row of the matrix above.
>
> And the data is not marginal: **clean 1-minute NQ volume, zero nulls and zero zeros, 2006 → 2026**
> (`DATA_CENSUS §2`). Twenty years, already on disk, no purchase, no owner action.
>
> Three of the four independent mines converged on this without being told to. The vendor corpus
> concentrates its only real mechanism content here (exhaustion by monotone volume decay, absorption
> / effort-no-result, the "high volume + mid-bar close = no edge" tag), `intraday_system` has a
> volume-spike reversal it never OOS-tested, and the deep-research packets rank a volume clock
> EVI-5. **`VOLCLOCK` and `SMV2AK` are not counter-evidence** — SMV2AK tested volume as a *clock*
> (resampling bars) and lost; nobody has tested volume as a *signal* or as a *confidence weight*.

## 3. Rows that are genuinely closed — do not reopen without new information

Every item here is tested-and-failed with an artifact. Re-running these is the failure mode the
directive names in §22.

| closed | evidence |
|---|---|
| overnight range, all four quadrants | `runs/.../ONRANGE01` N=4,961 +$29.8/trade CI [−23.7,+84.1], top-1 % = 2.76× the entire net · `ONRANGE02` −$27.0/trade, net −$138,347, CI [−47.2,−7.4] entirely below zero |
| **unconditional** overnight drift | ≈0 since 2021; closing-imbalance σ fell 6.5 % → 2.9 % |
| overnight *channel* traded directly | W96 fails its own session-shift null at the 88th vs a 95th bar; overnight SHORT loses $41,741 |
| gap fade · ORB-failure + VWAP reacceptance · failed-flip reversion | B01e/B02, B01c, DR05-H1b |
| sweep-and-reclaim / failed range-break fade | E3-A: penetration of a reference level **continues** on modern NQ |
| value-area rotation · month-end · turn-of-month · post-OPEX · post-FOMC & post-CPI 08:30 drift | registry + `TOMFLOW01` |
| announcement-day exposure conditioning, **both** directions | 24.2 % of top-1 % P&L sits on announcement days |
| low-range fade · fade-as-event · seconds-scale compression | W11/W18, W40, FSS-6 |
| breadth trilogy · KDJ+MA120 ladder | KDJMA01 is negative **before** costs |
| loss-reactivity intraday (day circuit breaker, ER damper, disaster stop) | **three independent constructions converge**: SMV2AH beaten by a count-matched random-halt placebo in 16 of 16 cells; SMV2V TUW delta literally 0 days; SM03B 2006-21 maxDD 6.1–6.8 % *worse* |
| "different clock ⇒ independent alpha" | W97 falsified it: `X9a_RTH` shares B-MOM's clock completely and correlates **+0.0205**; `P1_RTH` correlates **+0.2744** because P1 *contains* bmom |
| generic "ES predicts NQ" standalone | cross-market engines **0-for-15**; W18R2 added ES/RTY/YM (~4× the evidence) and moved P(ΔCDaR>0) only 0.753 → 0.784 |

## 4. Ranked frontier — coverage × opportunity × data × mechanism

Ranked by (monetizable opportunity) × (weakness of current coverage) × (data on hand) ×
(plausible causal mechanism) × (expected independence from existing P&L). Nothing here is a
result; every row is a hypothesis with a named falsifier.

> ### ⚠️ **RE-RANKED 2026-08-27 after W109 / W110 / W111.** Rows **#0** and **#1** — the two the
> ### ledger ranked highest — have both been **TESTED AND CLOSED**, and their strikeout rows are
> ### kept below with the evidence. The new **#0** is the successor W109 pointed at, and it is a
> ### different object, not a retune of anything.

| # | candidate | information that is NEW | data | why it is not already closed | main falsifier |
|---|---|---|---|---|---|
| **0** | ⭐ **CONTINUOUS FADE ACTION VALUE** — estimate `E[PnL(fade) \| I_t]` at 11:48 and weight exposure by it, instead of thresholding a state into a binary veto | nothing new is needed; it re-uses the three detectors W109 proved carry real class information (AUC 0.613–0.621, 100th pctile of permutation nulls) | 1-min OHLCV + the ES/RTY/YM substrates already joined | **W109 showed the failure is at the POLICY layer, not the information layer.** A 25/50/75 % binary cut discards the magnitude information an AUC-0.62 signal carries, and its selectivity ratio is 0.74–1.12 — pure exposure reduction. A continuous weight has never been tried here | the continuous weight's selectivity ratio is also ≈1, i.e. the information is too weak at any policy; **or** it needs fresh held-out engines because W109 consumed these five |
| ~~**1**~~ | ~~**VOL-EXHAUST / ABSORB**~~ **CLOSED by W111** — −$233/trade, 0.0th percentile, all 15 cells negative, three of five *below* the 5th percentile of the volume-decile-matched null this row itself named as the falsifier | volume, and it was genuinely the first time | 1-min OHLCV 2006–2026 | it *was* open; two prior attempts were specification failures | **the falsifier fired** |
| ~~**0(old)**~~ | ~~**CAUSAL TREND-DAY DETECTOR as a fade veto**~~ **CLOSED by W109** — held-out primary 85.0th percentile against a rate-matched random veto; and W111b showed the class signature that motivated it is definitional | — | — | — | **both falsifiers fired**: the veto did not beat a random veto of the same rate, and the class table it rested on is reproduced by an unconditional fade |
| **2** | **SEMIVAR-SKEW** — σ_down for short legs, σ_up for long legs inside the existing ratchet | realized semivariance; every vol conditioning ever run used total RV | 1-min OHLCV 2006–2026 | attacks the campaign's **named** weakness from inside the engine rather than adding a sleeve; corroborated by HTFMECH01 (+$11.9k long / −$22.0k short) | RSV−/RSV+ share carries no forward information on NQ at 1 min |
| **3** | **CROSS-MARKET, CONDITIONAL ONLY** — does NQ/ES disagreement predict *failed* persistence; does RTY weakness mark bad NQ longs | ES/RTY/YM, as a **condition on an NQ trade**, never as a standalone signal | **on disk, aligned, same 1,058 sessions**, zero cost | the 0-for-15 record is on *standalone* cross-market engines; the conditional form has never been run | **run the zero-lag timestamp known-answer test FIRST** or this manufactures a beautiful artifact |
| ~~**0**~~ | ~~**CAUSAL TREND-DAY DETECTOR** — a statement at ~11:45 about whether today is a trend day, used ONLY as a veto on fades~~ ⚠️ **row superseded — see the CLOSED entry at the top of this table** | nothing new is needed; it re-uses five mechanisms already built | 1-min OHLCV | **W108 measured that five fade mechanisms have the right class signature and are only killed by trend-day exposure.** A veto makes all five tradeable at once — the highest-leverage single object the ledger has ever pointed at | *(fired)* the detector cannot beat its own p\* on the classes that matter, **or a veto with a random detector of the same rate does as well** |
| **4** | **OPENTYPE-FREEZE** — Dalton/Steidlmayer opening taxonomy (drive / test-drive / rejection-reverse / auction) as an **exposure weight**, never a trade | opening-auction structure; zero fitted parameters | 1-min OHLCV 2006–2026 | unique clean geometry: freeze the taxonomy on 2006–2021, read once on 2022+ | tag carries no expectancy separation on 2022+ after the freeze |
| **5** | **MIDDAY-VWAP-BAND** — ±2σ same-slot band around session VWAP, **11:00–14:00 only**, hard flat at 14:00 | window-restriction; the dead fades were all-day rules | 1-min OHLCV | fires exactly where P1's channel decays and where P1 is thin | the edge is present outside 11:00–14:00 too ⇒ not the mechanism |
| **6** | **CASCADE-EXHAUSTION** — −2.5σ 30-min move **and** volume z>3 **and** range z>3 **and** a rejection close | three simultaneous extremes; a different population from unconditional fades | 1-min OHLCV | the fade kills (SMV2K t=−2.35, SMV2P t=−2.17) are unconditional | fires < 20×/yr, or negative |
| **7** | **CONDITIONAL OVERNIGHT REBOUND** — long only, bottom decile of 15:30–16:00 signed close pressure | the extreme-decile conditional; the unconditional version's *decay* is the mechanism, not a refutation | 1-min OHLCV | killed 3× unconditionally, never in the extreme decile; carry W96's overnight tax ($19.77/ctrRT vs $14.52) | extreme decile is also flat; or top-decile rally closes rebound equally |
| **8** | **B-FADE at 60 min, release-type conditioned** | scheduled-release **type**, not "announcement" generically | calendar + 1-min | **verified**: release@60 n=102 **+98.991 ticks, CI [+12.155, +183.797]**; placebo n=998 −17.884 CI [−44.008,+6.228]; **NFP@60 n=50 +161.108 CI [+30.796,+299.880]**, FOMC@60 n=34 −24.343 | the effect is generic-announcement after all, i.e. it does not survive splitting by release type |
| **9** | **FLATMEAN-FADE** — band fade gated on `|Δmean20|/ATR ≤ 0.06` | an explicit *anti-trend* gate on a fade | 1-min OHLCV | the only reversion construct that survived 2025 OOS **and** 2026 recency in `intraday_system` (ρ 0.013 vs its trend engine) — but it **failed its own neighbourhood gate**, and none of it is NQ | on NQ the slope gate adds nothing over raw z |
| **10** | **INVVOL-EXPOSURE + FIXED-POINT TRAIL** — contracts ∝ 1/ATR with a *fixed-distance* trail frozen at entry | scales the **position** by vol and holds the exit distance fixed; we do the opposite | 1-min OHLCV + ledgers | the reconstructed trader's hold obeys `hold ~ ATR^−1.636` (R²=0.923), which only distance-based exits produce | on our entries a 25-pt trail gives avg_win ≈ $517 vs his ~$1,780 ⇒ the pairing needs *his* entries |
| **11** | **PRIOR-SESSION LEVEL TRAP** | yesterday's H/L/C as anchors — neither engine touches them | 1-min OHLCV | untested OOS anywhere | on NQ the overnight session already trades through yesterday's levels, voiding the "untested level" premise |
| **12** | **OWN-FAMILY AGREEMENT** as an up-weight | breadth of our *own* signals | our own streams | measured large in `intraday_system` (all-three-agree +90.2 R vs single-family −7.3 R, PF 0.29) | on NQ the agreement effect is just a volatility proxy |

## 5. Gated — not research, waiting on someone

| | gate |
|---|---|
| DOM / Level-II / Market Replay | **owner risk-control PAUSE, 2026-08-12.** No history exists anyway |
| options / dealer gamma | purchase decision (`GAMMA00_..._FEASIBILITY/DATA_PURCHASE_OPTION.md`) |
| VWAP Flux | owner purchase (OTR R33 decision: buy as *instrument*, not proof) |
| ~~NT8 Strategy Analyzer parity for `WeeklyEdgeX9a_v1.cs` / `WeeklyEdgeBmom_v1.cs`~~ | ⚠️ **NOT GATED — this row was false and is removed from the gate list, 2026-08-27.** CrossTrade MCP compiles and runs the real Strategy Analyzer (add-on v1.13.9, NT8 8.1.8.1); both legs of the book were parity-certified through it on 2026-08-27. The claim was **inherited, never probed**, and cost a full day. **Standing rule, CLAUDE.md §6: never assert an action is owner-only without re-probing the tool surface that day.** Parity for these two is simply *not done*, which is a queue position, not a gate |
| MONITOR-01 read #2 | calendar, on/after **2026-11-01** |
| frozen-champion annual evaluation | calendar, on/after **2027-08-01** |

## 6. One standing warning carried forward

The deep-research documents label several items "never tested" that **were subsequently run and
killed** (`DR_V4_...` lists a volume *clock* and a percentile-adaptive clamp as EVI-5 untested;
SMV2AK returned −$44,809 and SMV2AG went 0/6). The DR docs predate the runs.
**Treat any DR "never tested" label as a claim to check against `runs/`, never as a fact.**
