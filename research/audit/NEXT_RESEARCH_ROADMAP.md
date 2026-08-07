# Next research roadmap — post-audit, POST_AUDIT_TRANSITION active

_2026-08-07. The audit PASSED; per Constitution v2 the campaign proceeds
automatically. Ordering by expected value of information._

## Frozen going in

- **Family-A reference: executable R5-E10** (research proxy: R5 theoretical,
  corr 0.9985). R4-21 = theoretical robustness benchmark only.
- Solar parameter optimization: CLOSED (unchanged).
- Every new configuration requires a pre-committed `runs/<run_id>/spec.yaml`
  (schema: `runs/AUDIT_GATE_R01/spec.yaml`); trial counter resumes at seq 230.
- All risk metrics labeled TRUE_MTM / REALIZED_ONLY; drawdown budgets use
  bar-level numbers.

## Wave B01 — FAILED_DIRECTIONAL_CHANGE_AND_VALUE_REACCEPTANCE (starts now)

Seeds: DR-05 (H1–H5, preregistered on paper, never run) + thesis FAIL-01/VALUE-01
/SESSION-01 + `complementary_families.md` event definitions.
Design resolution required at preregistration (conflict documented by the
deep-research reader): thesis FAIL-01 triggers on *opposite re-flip*; DR-05's
triage rules the re-flip ENTRY-USELESS (fade already consumed) and selects the
*re-cross of the flip price* as the entry event, demoting re-flip to
invalidation/exit. **B01 adopts the DR-05 resolution** (it is the preregistered,
mechanism-argued one) and tests the thesis variant only as a sensitivity arm.
Stages:
1. B01a = DR05-H1 overshoot/failed-flip calibration (pure Python on committed and
   audit bar series; zero engine cost; instrumentation).
2. B01b = DR05-H2 failed-flip fade (Python vector backtest → NT8 confirmation for
   survivors), gates as preregistered in DR-05 (eight gates incl. losing-day corr
   ≤ +0.25 vs Family A, no month > 40% of net, positive ≥3/5 years).
3. B01c = DR05-H3 ORB-failure + reacceptance; B01d = H4 asymmetry read; B01e = H5
   gap-fade null control.
4. Every arm compared for incremental portfolio value against **both** executable
   R5-E10 and theoretical R4 (constitution requirement).

## PORTABILITY-01 — third-instrument mechanism test (parallel-eligible)

YM + RTY + CL preregistered as the instrument set (already named in the thesis;
no cherry-picking). Instrument-normalized thresholds (VolMult in sigma units
transfers; clamps re-scaled by tick value), instrument-specific commissions.
Pass: positive after-cost ensemble expectancy in ≥2 of 3, or preregistered pooled
test. This is the highest-information falsification left for the persistence
mechanism after the ES failure.

## Then, in order

3. **PORT-01** fixed family combinations (50/50, 60/40, 40/60 risk) — only after a
   Family-B candidate passes standalone gates.
4. **PORT-02** router (PERSISTENCE / FAILED_PERSISTENCE / AMBIGUOUS; ≤3 state
   variables) — only after an unrouted two-family portfolio qualifies out-of-fold.
5. **DAY_MARGIN_FLAT** operational variant — margin facts verified (16:45 ET
   cutoff; NQ day $1,000 / MNQ $100; discretionary liquidation + $25/$50 fees).
   Build after Family-B wave: flatten ≈16:40 ET, 18:00 reopen policy arms
   (immediate / next bar / reconfirmed state / new event), right-tail retention
   reporting mandatory.
6. **SOLAR-01/02** (long/short marginal contribution at portfolio level; member-
   disagreement state) — only as portfolio-level questions, not new Solar mining.
7. **MONITOR-01** — freeze the quarterly overshoot-r protocol definition alongside
   Wave B01 preregistration (free, no trading).
8. ML overlays — only after interpretable-state research matures (constitution §17).

## Explicit non-goals (unchanged)

No new Solar parameter search; no Type-2/3 revivals; no wave filters; no leverage;
no live/sim/paper/forward activity; no history rewrite (human action pending).
