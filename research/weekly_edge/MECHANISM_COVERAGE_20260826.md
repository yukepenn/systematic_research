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
| **trend persistence** | **STRONG** | **·** | SUPPORTED | ✗ | ✗ | NULL | NULL | **STRONG** | WEAK | ✗ |
| **downside persistence** | **WEAK** | **·** | WEAK | ✗ | ✗ | · | · | **·** | WEAK | ✗ |
| **reversal / failed persistence** | NULL | **·** | · | ✗ | ✗ | · | · | · | · | ✗ |
| **range / value** | NULL | **·** | **·** | ✗ | ✗ | · | · | · | · | ✗ |
| **volatility transition** | WEAK | **·** | · | ✗ | ✗ | · | · | WEAK | **·** | ✗ |
| **opening auction** | **·** | **·** | · | ✗ | ✗ | · | · | · | · | ✗ |
| **overnight inventory** | NULL | **·** | · | ✗ | ✗ | · | · | · | · | ✗ |
| **event / calendar** | — | · | · | ✗ | ✗ | · | NULL / **·** | · | · | ✗ |
| **order flow** | — | · | · | **·**(45d) | **·**(45d) | · | · | · | · | ✗ |
| **liquidity / book** | — | — | — | ✗ | ✗ | — | — | — | — | **✗ paused** |
| **cross-market** | — | · | · | ✗ | ✗ | **NULL (0/15)** | · | · | · | ✗ |
| **execution** | **STRONG** | · | · | SUPPORTED | · | · | · | · | · | ✗ |
| **management / sizing** | SUPPORTED | · | · | · | · | · | · | **REGIME_LOCAL** | · | ✗ |

## 2. ⭐ The single largest hole, and it is free

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

| # | candidate | information that is NEW | data | why it is not already closed | main falsifier |
|---|---|---|---|---|---|
| **1** | **VOL-EXHAUST / ABSORB** — monotone body+range+**volume** decay over N bars; and effort-no-result (max volume, non-max body, non-max range, close at bar mid) | volume, first time ever | 1-min OHLCV **2006–2026** | every dead fade here was a *structure* fade (failed break, gap, value area) with no participation term | effect survives holding volume rank fixed ⇒ it is just "big bar" |
| **2** | **SEMIVAR-SKEW** — σ_down for short legs, σ_up for long legs inside the existing ratchet | realized semivariance; every vol conditioning ever run used total RV | 1-min OHLCV 2006–2026 | attacks the campaign's **named** weakness from inside the engine rather than adding a sleeve; corroborated by HTFMECH01 (+$11.9k long / −$22.0k short) | RSV−/RSV+ share carries no forward information on NQ at 1 min |
| **3** | **CROSS-MARKET, CONDITIONAL ONLY** — does NQ/ES disagreement predict *failed* persistence; does RTY weakness mark bad NQ longs | ES/RTY/YM, as a **condition on an NQ trade**, never as a standalone signal | **on disk, aligned, same 1,058 sessions**, zero cost | the 0-for-15 record is on *standalone* cross-market engines; the conditional form has never been run | **run the zero-lag timestamp known-answer test FIRST** or this manufactures a beautiful artifact |
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
| NT8 Strategy Analyzer parity for `WeeklyEdgeX9a_v1.cs` / `WeeklyEdgeBmom_v1.cs` | owner-only interactive action |
| MONITOR-01 read #2 | calendar, on/after **2026-11-01** |
| frozen-champion annual evaluation | calendar, on/after **2027-08-01** |

## 6. One standing warning carried forward

The deep-research documents label several items "never tested" that **were subsequently run and
killed** (`DR_V4_...` lists a volume *clock* and a percentile-adaptive clamp as EVI-5 untested;
SMV2AK returned −$44,809 and SMV2AG went 0/6). The DR docs predate the runs.
**Treat any DR "never tested" label as a claim to check against `runs/`, never as a fact.**
