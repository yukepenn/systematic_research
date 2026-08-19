# MONITORING_CALENDAR — every scheduled or gated future read, all programs (2026-08-18)

Single consolidated schedule. Each row cites its governing protocol; this file adds no new
authority — regenerate/extend it whenever a protocol changes. Dates are "due on/after".

## Dated

| Due | Read | Object | Protocol / rule | Notes |
|---|---|---|---|---|
| **2026-11-01** | MONITOR-01 reading #2 (quarterly) | Frozen campaign-1 champion (R5-E10, 13 members; live-ops default = 16:44-flatten v2) | `MONITOR01_PROTOCOL.md`; alarm: σ-banded r < 1.05 two consecutive quarters, or banded drift beyond protocol bounds | Requires one fresh engine-exact 1-min NQ bar export (consumes nothing). Same reading also owes: SM13 B-MOM decay statistic (`../system_master/SM13_BMOM_DECAY_RULE.md`, floor $60/day rolling 504-session mean); CURRENT_EDGE_HEALTH refresh both products; re-check Product-A 10-13-contract band POSSIBLE_DECAY flag (escalate to STRUCTURAL_BREAK_EVIDENCE if still present at ~1,000 bars, else downgrade); Product-B rolling-120 Sharpe WATCH flag (should mean-revert as Jan-May 2026 rolls out). |
| quarterly thereafter | MONITOR-01 #3, #4, … | same | same | Standing cadence. |
| **2027-08-01** | Annual frozen-champion locked-forward evaluation | R5-E10 (FROZEN definition only) | `LOCKED_FORWARD.md`; must be preregistered before the read; challenger comparisons need their own written protocol first | First full-year virgin-data evaluation. |
| **2027-08-01** | MONITOR-02: Program-B combined re-read | B-MOM + B-FADE + B1-overnight (all PARKED, 0 frozen) | **`MONITOR02_PROTOCOL.md`** (frozen 2026-08-18, before any forward read) | ≥12 months forward accrual; evaluation, not selection; unparking ≠ promotion. |

## Gated (no calendar date — a condition, authorization, or data volume unlocks them)

| Gate | Item | Governing doc |
|---|---|---|
| Owner authorization of §10(a) or (b), then ≥60 paired new sessions | SYSTEM_MASTER **B1 challenger** (drop-HTF Product B) future confirmation — resolves the INCONCLUSIVE Sharpe margin | `../system_master/B1_FUTURE_CONFIRMATION_SPEC.md` |
| Materially more tick/BBO sessions accumulated (archival currently idle — see OWNER_QUEUE §OQ-4) | U9/U9B microstructure re-test (frozen prequential design, larger sample) | `../system_master/ACTIVE_RESEARCH_QUEUE.md` (EVI rank 3) |
| Owner decision on NT8 export cost + new frozen AMENDMENT_3-style bundle with power analysis | AUCTION02 larger confirmation batch (160/168 protected sessions untouched) | `../system_master/` AUCTION02 ledger rows + `PROTECTED_EVIDENCE_BUDGET.md` |
| Explicit recorded owner re-authorization + improved resource architecture | DOM01 collection restart → eventually DOM-M1 discovery read | `../data_forward_sealed/DOM01/DOM01_DATA_GOVERNANCE.md`; pause: `../system_master/DOM_PAUSE_CLEANUP_20260812.md` |
| Explicit owner re-authorization (probe dates aging out ~90-day server window — OQ-4) | DATA03 Market Replay probe/batch acquisition | `runs/DATA03_HISTORICAL_MARKET_REPLAY_INVENTORY/acquisition_plan.yaml` |
| Owner purchase decision (~$80-199/mo) | GAMMA00 options/dealer-state data → re-open that feasibility lane | GAMMA00 ledger row (`../system_master/TESTING_LEDGER.csv`) |
| Preregistered spec + full gate battery (READY now — highest-EVI actionable item) | Direction-conditioned HTF construction | `../system_master/ACTIVE_RESEARCH_QUEUE.md` rank 2; evidence `HTFMECH01_TILT_MECHANISM/REPORT.md` |
| A frozen preregistered family showing ≥ +7pp on discovery AND (forward-data) holdout | Zone-F scalp reopening | `../scalping_lab/reports/ZONE_F_FINAL_VERDICT.md` (+ 2026-08-18 post-verdict note: holdout leg must use ≥2026-08-01 data) |

## Standing per-wave (no date — every wave, mechanical)

- Seal audit: `src/analytics/seal_audit.py` — verdict pasted into each wave report (W18/W19 CLEAN precedent).
- Preregistration guard: `research_sdk/prereg_guard.py` — spec commit strictly before result commit.
- Boundary math: `research_sdk/session_boundary.py` — compute every backtest/read window against `LOCKED_FORWARD.md` before data is touched; canonical constants live there (dev end 2026-05-29; last consumed session 2026-07-31).

## Standing invalidation triggers (data-triggered, not scheduled)

- B-MOM decay below SM13 floor ($60/day rolling mean) → decision per SM13.
- Product invalidation criteria in `/BASELINE_MODELS.md` ("what would invalidate" per object).
- CME/broker schedule changes (margin windows, early-close calendar) → re-check C4 compliance assumptions.
