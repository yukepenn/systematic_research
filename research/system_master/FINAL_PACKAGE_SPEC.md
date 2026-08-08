# FINAL_PACKAGE_SPEC — Joint Finalist Package (FROZEN)

_Frozen 2026-08-08, committed BEFORE the single joint holdout read (2026-06-01 →
2026-07-31). Per CONVENTIONS §8. Nothing in this file may change after the read;
post-read modifications create new candidates with no holdout claim._

## Finalists (all definitions closed, no free parameters)

| id | definition |
|---|---|
| F1 SOLAR_REFERENCE | E10 research baseline: 13 members, target = round(10·mean pend) MNQ ±10, session-close flatten (SM01 substrate semantics) |
| F2 SOLAR_TILT50 | F1 with target = round(1.25×·tgt·0.9296) on HTF-agree bars (daily SMA50 state, prior session close, ×1.25 agree / ×1.0 else; rescale constant 0.9296 = dev matched-exposure factor, frozen; cap ±13) |
| F3 BMOM | exact frozen W8-1 rule, 1 NQ, C1 (generator `sm_bmom.py`) |
| F4 PORT_532 | 0.5·F1 + 0.3·vm(F3) + 0.2·vm(B1) daily composition; vm() = scale to F1 dev σ ($2,338.66); leg scales frozen from dev: BMOM ×0.6588, B1 ×0.8270; portfolio rescale to F1 σ frozen at dev value ×1.431 |
| F5 PORT_TILT_532 | as F4 with F2 in place of F1 (F2 leg scale to F1 dev σ frozen from dev) |
| B1 leg | frozen W9-1 rule (long 16:45 close → next 09:30 close, 2.0t friction) |

## Holdout read protocol (ONE read)

1. Data: sessions 2026-06-01 → 2026-07-31 only. Bars: AUDIT03/B01A (already on disk,
   never analytically read for these rules; E10 engine artifacts for this window were
   published for the BASELINE — so F1's holdout result is CONFIRMATORY-ONLY, while
   F2−F1 (tilt increment), F3, and F4/F5 composition results are the clean reads).
2. Compute per finalist: net, Sharpe (63-session basis, reported not annualized-
   overweighted), maxDD, worst week, daily vectors committed to the run dir.
3. Primary judgment statistics (frozen):
   - F2−F1 increment sign and magnitude vs dev expectation (+$5.6k/yr scale).
   - F3 net sign (B-MOM entered June at its dev-frozen rule).
   - F4/F5 vs F1: ΔSharpe and Δnet sign.
   - E01 drawdown continuation: does the open Feb→Jun episode recover/deepen under
     F1 vs F5?
4. Interpretation rule (frozen): two months is CHARACTERIZATION, not validation.
   No finalist is dropped on holdout alone unless a defect is revealed (rule bug,
   sign inversion with dev). The package ships with holdout results labeled
   HOLDOUT-CHARACTERIZED. After the read the holdout is CONSUMED (ledger updated in
   CONTAMINATION_LEDGER and here).
5. Challenger classes (directive §34) mapped after the read in FINAL_NQ_SYSTEM.md.

## Operational attachments (not judged on holdout)

16:44-flatten variant applies to the Solar leg for live ops (v2 default, −5.35% known);
MONITOR-01 r-statistic + B-MOM rolling-2y decay floor + B1 top-10-night concentration
monitor; virgin data ≥2026-08-01 untouched.
