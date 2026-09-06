# MC-57 — ZB intraday STATE -> NQ rest-of-session RV forecast

**Run** `G2_F13_MC57_ZBSTATE_20260906` · **Ledger trial** `G00054` · **Seed** `20260906`
**Campaign** GENESIS II (Formal Wave 6) · **Stage** DIAGNOSTIC / RISK-SPECIFICATION
**Evidence status: DISCOVERY_CONSUMED** (every number here is burned; no strategy, no sizing licensed).

---

## VERDICT: **FAIL** (frozen primary leg a). `survives_info_gate = False`.

Adding ZB (30-yr bond future) intraday POINTS state to a HAR(NQ-RV)+$0-macro baseline **does not
lower**, and if anything slightly **raises**, the out-of-sample QLIKE of the NQ
rest-of-session-from-11:00 realized-variance forecast. The increment is **identified** (max ZB
VIF 4.45 << 10) and **well-powered** (364 test sessions, all corr-regime cells >= 20), so this is a
genuine FAIL, not a power closure.

| statistic | value |
|---|---|
| mean QLIKE BASE | 0.324049 |
| mean QLIKE FULL | 0.338184 |
| relative QLIKE improvement (FULL vs BASE) | **-4.36 %** (negative -> FULL worse) |
| d_bar = mean(L_base - L_full) | -1.413e-02 |
| HAC (Newey-West, L=5) se | 1.038e-02 |
| **DM statistic / two-sided p** | **-1.361 / p = 0.173** -> FAIL |
| **circular-shift p (leg a, 2000 shifts)** | **0.967** -> FAIL (real alignment worse than 96.7 % of shuffles) |
| MDE barrier (a=.05, power=.80) | 2.909e-02 · abs(d_bar)/MDE = -0.49 |
| max ZB VIF (identification) | 4.449 -> **IDENTIFIED** |
| powered | **YES** (n_test=364; cells >=20) |

**Per the decision rule:** a FAIL on the frozen primary **retires ZB's "last genuinely new raw
surface" flag** (a bankable negative) and writes a FAILURE_MEMORY row. MC-35 (conditioning P1 on a
new surface) **is not unblocked** by this run's primary.

---

## Preregistration compliance

Implemented exactly from `spec.yaml`, honoring all three binding amendments:

- **A1 (no VXN).** VXN appears in neither arm. BASE = plain HAR(NQ-RV) {rv_pre11, rv_d, rv_w, rv_m}
  + $0 macro flags only. No implied-vol join anywhere.
- **A2 (POINTS + seal).** Every ZB observable is POINTS: ZB RV = sum(dPrice)^2, true range = high-low,
  NQ-ZB corr on point-returns. Never percent (the parquet is additively back-adjusted). Program
  **hard-dropped every session > 2026-05-31 at load** — ZB parquet ran to 2026-07-31 (the BURNED
  window inside an owned file); after drop, ZB max = 2026-05-29. **Retained boundary printed =
  2026-05-29 (<= 2026-05-31 : PASS).** NQ target uses LOG-return RV (A2 scopes POINTS to *ZB*
  observables; NQ level ~15k-22k in-window -> log-RV is undistorted and cross-day comparable — the
  basis flags are printed in G0).
- **A3 (alignment).** The 60-min NQ-ZB corr uses an **inner-join on common minutes** (ZB prints no
  bar in zero-trade minutes). **Min-coverage rule = 30/60 common minutes, printed**; only 3/878
  sessions (0.3 %) fell below and were NaN->train-median imputed with a missingness flag. Coverage
  distribution printed (min 0 / median 60 / max 60).

Design matrices, one fit no refit, train 2022-12-27..2024-12-31 (n=514), test 2025-01-02..2026-05-31
(n=364, effective last session 2026-05-29). n_total = **878** ZB-intersect-NQ sessions (spec anticipated ~860).

---

## Gate table (program-printed — `out/gate_table.txt`)

- **G1 BARRIER (printed before gates; MDE before observed):** MDE = 2.91e-02; observed abs(d_bar) = 1.41e-02
  (abs(d_bar)/MDE = -0.49). test-n = 364. leg-b events = 34, leg-c flip events = **0**.
- **G0 seal/points:** max session 2026-05-29 <= 2026-05-31 [PASS]; ZB basis POINTS/POINTS/POINT-RETURN [PASS].
- **G2 cell occupancy** (thin < 20 -> CLOSED-BY-POWER): hedging(<=-0.3) TRAIN 28 / TEST 71 [ok];
  neutral 377 / 246 [ok]; liquidation(>=+0.3) 109 / 47 [ok]. **No corr cell is thin** — the modern
  regime here leans neutral/positive but the hedging cell is still read at both eras.
- **G3 identification (VIF):** all five ZB terms VIF 2.4-4.4, max **4.449 < 10 -> IDENTIFIED**. (The
  FULL coefficients do show sign-offsetting among the three correlated ZB-magnitude terms —
  sess_rv -0.45, 30m_rv +0.25, exp_cnt +0.19 — i.e. mutually collinear enough to overfit train and
  not generalize, though below the VIF NOT-IDENTIFIED bar.)
- **G4 primary:** DM p = 0.173 [FAIL] **and** circular-shift p = 0.967 [FAIL]; identified & powered.
  **=> FAIL.**
- **G5 semantic sentence** (below).

### G5 (the one sentence)
> Over 878 ZB-intersect-NQ sessions (2022-12-27..2026-05-29), does adding ZB intraday POINTS state
> (diurnal-adjusted RV, NQ-ZB 60-min point-return correlation level/sign, 95th-pct range-expansion
> count) to a HAR(NQ-RV)+$0-macro baseline **lower** the out-of-sample QLIKE of the NQ
> rest-of-session-from-11:00 realized-variance forecast? **ANSWER: NO (FAIL)** — rel. QLIKE -4.36 %,
> DM p = 0.173, shift p = 0.967, max VIF = 4.45.

---

## Legs (b)/(c) — secondary, triple-matched controls, shared circular-shift null

Controls = same-era **AND** NQ-trailing-60min-RV-decile **AND** macro-flag matched (triple).
One shared per-session circular shift across (a)/(b)/(c); effective-K over active legs.

- **Leg c (corr FLIP hedge->liquidation, corr_early <= -0.3 -> corr_late >= +0.3):** **0 events** in the
  whole population -> **CLOSED-BY-POWER, unread** — exactly the empty "bonds-still-hedging within one
  morning" cell G2 anticipated for the post-2022 regime. Dropped from the family.
- **Leg b (95th-pct ZB range-expansion sessions, n=34):** matched delta(NQ forward RV) = **+2.06e-04,
  p_shift = 0.001** — a real association (expansion mornings precede higher NQ forward vol than
  triple-matched controls). Per-era: TRAIN 26 events [read], TEST 8 events [thin -> CLOSED-BY-POWER];
  the association is read on the full population.
- **Family effective-K:** active legs = 2 (a+b), rho_bar = -0.091, **K_eff = 2.20**, per-leg alpha = 0.0227.
- **Supplementary robustness (beyond spec):** adding a **4th** match dimension — NQ overnight/morning
  (rv_pre11) RV decile — does **not** collapse leg b (delta +2.06e-04 -> +2.47e-04, on 23 matched events).
  So leg b is **not** merely NQ's own overnight vol in a cross-asset costume.

---

## The one nuance the primary FAIL must not bury (flagged, not promoted)

The frozen primary (rest-of-session-**from-11:00**) fails, but two pre-declared-secondary readouts
point the **same** direction and are **robust**:

- **Next-session (daily-horizon) NQ RV, properly refit** (same BASE/FULL design): rel. QLIKE
  **+8.08 %, DM = +3.28, p = 0.001** — ZB state **helps** the *next-session* forecast.
- **Leg b** survives the triple-match and the 4th NQ-overnight match.

**Interpretation = horizon mismatch, not redundancy.** The rest-of-session-from-11:00 target is
dominated by NQ's *already-realized* overnight+morning RV (rv_pre11 coefficient +0.83), leaving
almost no residual variance for ZB — so five extra ZB parameters only add OOS estimation noise
(FULL worse). At the **daily / overnight horizon**, where NQ's own lagged terms are weaker, ZB's
slow-moving macro-vol content appears to carry incremental information.

**This changes nothing about the verdict.** The spec froze the primary as rest-of-session-from-11:00
and pre-declared that the next-session target *cannot generate a PASS alone*; leg b likewise cannot
PASS alone. All of these numbers are now **DISCOVERY_CONSUMED / burned**. What they license is a
**new preregistration on fresh data**, not a promotion:

> *Follow-up hypothesis (for a future spec, fresh window):* does ZB intraday state (to 11:00) improve
> the **next-session / daily-horizon** NQ RV forecast beyond a daily HAR(NQ-RV)+macro baseline?
> If it survives OOS on unburned data with the same identification/power/null discipline, that —
> not this run — would be the surface that could unblock MC-35.

---

## One hand-checked session (independently recomputed from raw parquet)

**Session 2025-09-16 (TEST era)** — recomputed straight from the two parquets, bypassing the pipeline:

| quantity | pipeline | independent hand-recompute | match |
|---|---|---|---|
| NQ rv_pre11 (18:01 D-1 -> 11:00 D, 1020 bars) | 1.233e-05 | **1.233292e-05** | yes |
| NQ rv_rest = TARGET (11:01 -> 17:00 D, 360 bars) | 5.864e-06 | **5.863536e-06** | yes |
| ZB pre-11 range-expansion count (TR > 0.0625 pt) | 9 | **9** | yes |

The check also confirms the **critical window fix**: the 358 evening bars (2025-09-15 18:00-24:00)
land in the **pre-11** window (all <= the 2025-09-16 11:00 cutoff), and the target's first bar is
11:01, last is 17:00 — i.e. "rest-of-session" is genuinely 11:00->close, **not** contaminated by the
session's own overnight open. (An earlier minute-of-day split wrapped at midnight and wrongly put the
evening into the target; fixed by splitting on the actual timestamp vs the session-date 11:00 instant.)

Forecasts for this session: BASE 8.43e-06, FULL 7.87e-06, realized 5.86e-06 (QLIKE base 0.0585,
full 0.0393 — FULL happens to win *here*, but loses on the 364-session test average).

---

## Deviations from spec

1. **NQ RV basis = LOG-return, not points.** A2 scopes POINTS to *ZB* observables (which are all
   points here). NQ is high-priced in-window so log-RV is undistorted and cross-day comparable
   (points^2-RV on NQ would scale with the ~15k-22k level). Basis flags printed in G0. This is a
   reading of A2, made explicit, not a silent choice.
2. **Macro flags are $0 rule-based approximations** (NFP = first Friday; CPI = mid-month Wednesday,
   APPROX; FOMC = hardcoded scheduled announcement dates; Treasury coupon auctions = mid-month
   Wed/Thu + end-month Mon-Wed, APPROX). They enter **both** arms symmetrically, so any date error
   cancels in the FULL-BASE increment (verified irrelevant to the primary); they matter only as a
   fair baseline control and for leg-b/c macro-matching, where the effect is second-order.
3. **Leg-c is empty (0 flip events)** — reported as CLOSED-BY-POWER and dropped from the effective-K
   family, as G2 anticipated; not a deviation so much as the anticipated closure.
4. **Added a supplementary 4-way match** for leg b (beyond the mandated triple-match) purely as a
   robustness probe of the redundancy hypothesis; it does not alter any gate.

## Artifacts
- `src/run_mc57.py` — implementation (spec-committed-before-results; one fit, no refit).
- `out/gate_table.txt` — program-printed GATE/SPEC/OBSERVED/PASS-FAIL (MDE before observed).
- `out/dm_summary.txt` — DM/HAC, VIF, FULL coefficients.
- `out/leg_bc_tables.csv` — per-era event occupancy, matched diffs, corr-cell occupancy, effective-K.
- `out/metrics.json`, `out/run_log.txt` — machine-readable metrics and full run log.
