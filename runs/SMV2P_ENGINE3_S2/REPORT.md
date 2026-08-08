# SMV2P_ENGINE3_S2 — Engine #3 slate 2 (seq 377–379): value-area rotation / multi-day false-break / month-end flow

**Class:** R1_FAMILY_TEST (Stage 1 screen; no promotion possible from this run).
**Spec:** `spec.yaml` frozen 2026-08-08, committed at 58dc2d2 before execution.
**Executor:** `smv2p.py`; invariant audit `verify_invariants.py` -> `out/verify_invariants.txt` (32 checks, 0 failures).
**Data:** NQ 3m END-stamped bars via `sm01_solarsim.load_bars_3m`, dev sessions 2022-01-04 .. 2026-05-29 (clip <= 2026-05-31; loader assert blocks anything >= 2026-08-01). Old-regime check (379): `runs/SM06_SOLAR_HISTORY/out/vote_state_3m_hist.parquet` session closes 2006-2021 (committed artifact).
**Costs:** every expectancy NET of $4.36/RT + 1 tick/side embedded in fills (`_fill`), NQ $20/pt.
**Stats:** NW t = mean per-event net, session-clustered SE, Bartlett lag 5 (SMV2K convention). House bootstrap: moving block 5, B=10,000, seed 20260808; p_boot = fraction of resampled means <= 0.

## Verdict (FACT)

| seq | engine | N | mean net/event | t_NW | p_boot | gates passed | verdict |
|---|---|---|---|---|---|---|---|
| 377 | value-area rotation | 273 | -294.74 | -2.17 | 0.983 | 3/4 | **KILLED — significantly negative** |
| 378 | multi-day balance false-break | 99 | -632.62 | -0.84 | 0.792 | 1/4 | **KILLED** |
| 379 | month-end flow tilt | 104 | +52.03 | +0.15 | 0.456 | 2/4 | **KILLED — no old-regime structure** |

**Slate-2 total failure.** Frozen verdict_rule -> V4 §51: three NEW mechanism-expansion passes are owed before any slate 3. Combined with slate 1 (seq 368–370), all six externally-sourced reversion/rotation/calendar families are now dead on this substrate.

## Frozen conventions and disclosed adaptations

- Wall-time convention (SMV2K anchor): "09:33 open" = open of the 0936-stamped bar; "15:57 exit" = open of the 1600-stamped bar; "15:54 time-stop" = close of the last RTH bar stamped <= 1554. RTH = stamps 0933..1600.
- **377 VA algorithm (exact, per spec):** histogram prior-session RTH 3m closes x volume in 25c bins (NQ trades on a 25c grid, so each bin is one price level, k = round(close/0.25)); seed bin = floor(prior-RTH-VWAP/0.25); grow the contiguous band one bin at a time toward the adjacent side with the LARGER volume (tie -> up; exhausted side -> other) until cumulative >= coverage x total RTH volume. VAL/VAH = lowest/highest included level. Independently recomputed on 25 sampled events: band holds >= 70% of volume and contains the VWAP bin in 25/25 (`verify_invariants.txt`).
- 377 event: 09:30 RTH open strictly outside [VAL,VAH]; acceptance = first run of 30 min (10 bars) of consecutive RTH closes inside; entry next 3m open (must be stamped <= 1554 else event void); target = far VA edge; level-touch fills use SMV2K e368 semantics (base = open if already beyond level else level, +/-1 tick capped by bar range); one event/session (verified unique).
- 378: rolling 20-session RTH-close extremes (shift 1); range frozen at break; reclaim = RTH close strictly inside within 2 sessions; entry next session 09:33; exit at midpoint touch on ANY bar (overnight included) or at the ~17:00 session close of the 3rd held session (entry session = 1). One position at a time (7 signals dropped in-position at center); dev-end right-censor drops 0; most-recent break episode wins when several are active. **Held overnight, as disclosed in the spec — engine is NOT day-only.**
- 379: MTD sign frozen ONCE per month = -sign(session close of D_n-2 minus prior-month final session close), point difference, applied to both day-events; 5/104 day-events fell on early-close sessions (no 1600 bar) -> forced exit at last RTH bar close, flagged `early_close_exit`, kept. "Sign consistent across 2022-2026" operationalized as the standard WF split (2022-24 vs 2025-26) plus the per-year table below.
- 379 hist check: GROSS close-to-close 2-day windows in POINTS (exact under additive back-adjustment), one observation per month, 191 months 2006-02..2021-12.
- Complementarity legs (code-map curves): PRIMARY Solar_DUAL = `DUAL` column of `runs/SMV2H_ONECONTRACT/out/rerank_curves.csv`; BMOM = `runs/SMV2B_BMOM_EXEC_AUDIT/out/ledger_E2_next_open.parquet` net_c1_ticks x $5 by session — verified IDENTICAL to the stored `BM_E2` column (max abs diff 0.0, asserted in `smv2p.py`). SECONDARY (robustness): champion twin `runs/SMV2M_MASTER_BUILD/out/twin_daily.csv` (dev-clipped) AND BMOM.

## seq 377 — A-H2 value-area rotation

FACT. 694 dev sessions opened outside the prior 70% VA; 273 produced 30-min acceptance events. Pooled net **-294.74/event (t_NW -2.17, total -80,465$)**. 120/273 reached the far edge (+1,136.60/event); 153 timed out at 15:54 (-1,417.37/event) — acceptance does not buy enough traverse. Long rotations (open below value) are the toxic side: -482.75/event (t -2.58, N 152) vs shorts -58.57 (t -0.32). WF halves -328.41 | -223.96 — both negative.

Plateau — **9/9 cells negative**:

| coverage | acceptance | N | mean net | t_NW |
|---|---|---|---|---|
| 60% | 21 min | 309 | -206.66 | -1.74 |
| 60% | 30 min | 274 | -280.53 | -2.24 |
| 60% | 39 min | 243 | -224.63 | -1.99 |
| 70% | 21 min | 298 | -174.96 | -1.38 |
| 70% | 30 min | 273 | -294.74 | -2.17 |
| 70% | 39 min | 244 | -416.39 | -3.12 |
| 80% | 21 min | 295 | -155.05 | -1.13 |
| 80% | 30 min | 269 | -179.42 | -1.35 |
| 80% | 39 min | 244 | -332.52 | -2.42 |

Gates: t_NW>=2 FAIL (-2.17) · N>=150 PASS (273) · WF same-sign PASS (both NEGATIVE) · plateau same-sign PASS (all NEGATIVE). Positive-expectancy family: **dead**.

## seq 378 — A-H9 multi-day balance false-break

FACT. 99 events at center (lb 20, ~0.4/wk). Pooled **-632.62/event (t_NW -0.84)**; 24/99 reached the range midpoint within 3 sessions (+4,530.95/event), 75 timed out (-2,284.96/event). WF sign FLIPS (-999.43 -> +172.01). Daily MTM at session closes reconciles exactly to event totals (-62,629.14 vs -62,629.14).

Plateau — mixed sign:

| lookback | N | mean net | t_NW |
|---|---|---|---|
| 10 | 127 | +264.95 | +0.54 |
| 20 | 99 | -632.62 | -0.84 |
| 40 | 71 | -971.65 | -1.15 |

Gates: t_NW>=2 FAIL · N>=80 PASS (99) · WF FAIL · plateau FAIL. **Dead.** INFERENCE: 2022-24 NQ trended through its 20-day close range too persistently for a 3-session reversion to the midpoint; the positive 2025-26 half (t +0.11) is noise.

## seq 379 — A-H12 month-end flow tilt

FACT, dev: 104 day-events (52 months x 2, zero skipped months), pooled **+52.03/day-event (t_NW +0.15, p_boot 0.456)**. Per-year means: 2022 -757 · 2023 +599 · 2024 +297 · 2025 +231 · 2026(Jan-May) -498 — NOT sign-consistent across years. Day-1 -354.65 vs day-2 +458.72: noise-level.

FACT, old regime 2006-2021 (gross direction check, 191 months): mean signed 2-day window **-1.02 bps/month (t_NW -0.17, hit rate 51.3%)**; eras 2006-2009: -1.5 bps · 2010-2013: -4.3 bps · 2014-2017: +9.4 bps · 2018-2021: -7.8 bps. No structural rebalancing-flow premium in either regime.

Gates: t>=2 FAIL (+0.15) · N>=100 PASS (104) · dev WF same-sign PASS (both weakly positive) · old-regime same-sign FAIL (-1.02 bps vs +52.03$ dev). Spec: "calendar mechanisms should be structural or die" — **dead**.

## Joint-loss-week complementarity (`out/jointloss_complementarity.csv`)

Weekly (W-FRI) sums over the 230-week dev calendar. Joint-loss (PRIMARY, Solar_DUAL<0 AND BMOM<0): **50 weeks** (champion mean -3,205.58/week there); SECONDARY (twin AND BMOM): 69 weeks.

| engine | mean wk (all) | mean wk (joint-loss, primary) | total in JL weeks | mean wk (JL, secondary) | weekly corr vs champion |
|---|---|---|---|---|---|
| e377 | -349.85 | -624.91 | -31,245 | -568.75 | +0.02 |
| e378 (MTM) | -272.30 | +252.68 | +12,634 | -142.31 | +0.06 |
| e379 | +23.53 | +104.43 | +5,222 | -23.22 | -0.05 |

FACT: e377 loses HARDER in joint-loss weeks — anti-complementary as well as negative. e378/e379 show mildly positive primary joint-loss means, but both are dead on their own economics and e379's read flips sign under the secondary definition. INFERENCE: noise on dead engines, not a rescue argument (V4 §42: no promotion from Stage 1 regardless).

## Gate table (`out/gates.csv`)

| engine | gate | value | pass |
|---|---|---|---|
| e377 | t_nw>=2 | -2.174 | FAIL |
| e377 | N>=150 | 273 | PASS |
| e377 | WF_sign_stable | -328.41 / -223.96 | PASS |
| e377 | plateau_9cells_same_sign | [-1.0] | PASS |
| e378 | t_nw>=2 | -0.844 | FAIL |
| e378 | N>=80 | 99 | PASS |
| e378 | WF_sign_stable | -999.43 / 172.01 | FAIL |
| e378 | plateau_3cells_same_sign | [-1.0, 1.0] | FAIL |
| e379 | t_nw>=2 | 0.154 | FAIL |
| e379 | N>=100_day_events | 104 | PASS |
| e379 | dev_sign_2022_24_vs_2025_26 | 69.43 / 16.23 | PASS |
| e379 | old_regime_same_sign | dev_mean 52.03  /  hist_bps -1.02 (t -0.17) | FAIL |

## Red-team notes

- 377 is a clean two-sided kill: significantly NEGATIVE across the entire 3x3 plateau, not merely edgeless. HYPOTHESIS (not tested here; anti-dup rule forbids flipping sides within this run): its mirror — continuation away from value after FAILED acceptance — aligns with the campaign's standing finding that NQ pays breakout/trend premium and charges for fading structure (slate-1 seq 368/369 fade premium was also significantly negative).
- 378's exit mix (24% target hits) shows the mechanism mostly expires worthless; no lookback neighborhood rescues it.
- 379's +$52/event dev point estimate over 2023-25 is exactly the recency trap the structural gate exists to catch; 191 old-regime months put the prior at zero.
- No data >= 2026-06-01 used anywhere: loader assert + per-artifact max-date checks (e377 max sd 2026-05-27, e378 max exit 2026-05-20, e379 max sd 2026-05-29) in `verify_invariants.txt`.

## Artifacts

`out/e377_events.csv` (273) · `out/e377_summary.csv` · `out/e377_plateau.csv` · `out/e378_events.csv` (99) · `out/e378_summary.csv` · `out/e378_plateau.csv` · `out/e378_daily_mtm.csv` · `out/e379_events.csv` (104) · `out/e379_summary.csv` · `out/e379_hist_check.csv` (191) · `out/e379_hist_summary.csv` · `out/jointloss_complementarity.csv` · `out/gates.csv` · `out/verify_invariants.txt`
