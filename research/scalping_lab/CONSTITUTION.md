# Scalping Lab Constitution

Source of authority: `MANDATE_V2.txt` (owner, 2026-08-07). This file distills it into
operating rules. Where they conflict, the mandate governs.

## 1. Hard safety (inherited from repo CLAUDE.md + mandate §5)
Historical research only. No live/Sim101/Playback orders, no forward trading, no account
interaction, no deployment, no connection/credential changes, no paid data. Historical
Strategy Analyzer allowed. Research NinjaScripts FAIL CLOSED in `State.Realtime`
(`if (State == State.Realtime) { Log(...); Disable(); return; }`). Market Replay only with
explicit owner authorization.

## 2. Economic gate (mandate §8, frozen)
- NQ: $2.18/side, tick $5 (0.25 pt). C1 = commission + 1 tick slip/execution → RT friction
  $14.36 ≈ **2.872 NQ ticks**. C2 = commission + 2 ticks/execution → $24.36 ≈ 4.872 ticks.
- C0 (commission only) is reported but NEVER the promotion metric.
- MNQ is NOT the scalp vehicle: $0.65/side + tick $0.50 → C1 RT ≈ $3.30 ≈ **6.6 MNQ ticks**
  (commission is 30% of NQ's for 10% of the size). Scalp research prices NQ execution.
- Every candidate reports gross ticks/trade, friction ticks/trade, net ticks/trade, and the
  friction/gross ratio. Classification: ROBUST_MARGIN / THIN_MARGIN / NO_MARGIN.

## 3. Evidence discipline
- Prediction ≠ contemporaneous impact (mandate §12): signals timestamped at formation t,
  P&L measured from t+ε only; placebo shifts mandatory for flow/book features.
- Latency surface (§13): expectancy × delay ∈ {0, 1 event, 250ms, 500ms, 1s, 2s, 5s} where
  timestamp fidelity permits; classify LATENCY_ROBUST/SENSITIVE/FRAGILE/NON_RETAIL.
  NON_RETAIL is never promoted.
- Inference is day-clustered / block-bootstrap; report raw events, independent days,
  effective N (§17). No i.i.d. t-stats on autocorrelated micro events.
- Every promising event must beat a matched null (vol-matched, time-of-day-matched,
  unconditional same-class baseline) before escalation (§16).

## 4. Tiers and budgets (§19)
- Tier 0: event studies (conditional forward distributions, no strategy). Cheap, wide.
- Tier 1: simple trade transformation (fixed horizon exit, 1 NQ, market orders, C1).
- Tier 2: local stability mapping (neighboring thresholds/timeframes/horizons — region, not point).
- Tier 3: full validation (chronological walk-forward, C0/C1/C2, latency surface, red team).
- Every selection-relevant experiment gets a spec in `specs/` committed BEFORE results are
  read, and a row in `registry/tested_configs.csv`. Kill early; never rescue weak families.

## 5. Data splits (§18) — geometry frozen after the data audit
Default geometry (to be confirmed/frozen in CONTAMINATION_LEDGER.md once coverage is known):
chronological development period ending 2026-07-31; **≥ 2026-08-01 is sealed for this
campaign too** (it is Solar's LOCKED_FORWARD; scalp research reading it would leak a shared
virgin block — one seal protects both campaigns). Walk-forward folds inside the development
period; a late in-development sealed scalp holdout additionally frozen before any family
profitability is read. No random train/test splits. ML: all normalization/selection/thresholds
inside training folds only.

## 6. Champion tiers (§26)
SCALP_SIGNAL_REFERENCE, SCALP_1NQ_REFERENCE, SCALP_HIGH_WIN_REFERENCE, SCALP_MAX_SHARPE,
SCALP_LOW_DD, SCALP_FINAL_CHAMPION — tracked in `reports/SCALP_CHAMPION.md`; may differ.

## 7. Interaction with Solar campaign
- Frozen Solar frontier, falsified Solar axes, and Solar registries are untouched.
- NT8/CrossTrade engine access is exclusive: never run scalp Analyzer work while a Solar
  engine task is active (and vice versa). Analytics in Python are unrestricted.
- Complementarity with vm20/R5-E10 is measured ONLY after a scalp edge is established and
  frozen standalone (§29). No fitting to Solar losing days.
- Compilation mirror: canonical source in `src/ninjascript/` here; byte-identical copy to
  NT8 bin\Custom with hashes recorded per run (mandate §4).

## 8. Amendment 1 rules (2026-08-07, `MANDATE_AMENDMENT_1.txt` — governs on conflict)

- **Research zones with separate champions**: MICRO (tick → <30s), STRUCTURAL_SCALP
  (~30s → 5min), ADJACENT_INTRADAY (>5min). Adjacent ideas (e.g. last-30-min flows) are
  testable but never silently redefine the scalp mission or claim the scalp-champion title.
- **Three uses of microstructure information, evaluated separately**: (A) directional alpha,
  (B) selectivity/meta-labeling on a structural setup, (C) execution alpha (cost reduction).
  Failing A does not kill B/C.
- **Literature = prior, never local verdict or local constant.** External numbers are
  labeled EXTERNAL PRIOR / SOURCE-SAMPLE-SPECIFIC until reproduced on our NQ sample. No
  hypothesis family testable on our own L1/L2 data is closed by citation alone.
- **High-win-rate discovery is a formal axis**: preregistered coarse excursion grid
  P(+A before −B | state) with A/B ∈ {+4/−2, +6/−2, +6/−3, +8/−4}; report hit rate,
  break-even hit rate, avg win/loss, left-tail ES, net ticks after cost, PF, count,
  trades/day. Win rate bought with catastrophic left tails is rejected.
- **Interactions**: after univariate Tier-0 characterization, a SMALL economically motivated
  interaction space is allowed (e.g. impulse + spread state + imbalance); no unrestricted
  combinatorial search. ML estimates conditional trade quality (P(target-before-stop), MFE/
  MAE), simple models first, chronological benchmark to escalate.
- **Clock validation must not assume the economic result**: timestamp integrity tests
  (monotonicity, cross-source consistency, common exogenous events) are the sync audit;
  ES→NQ lag is itself an empirical object, never forced to zero.
- **No live/realtime data recording** (owner ruling): historical resources only.

## 9. Stop condition (§35)
Converge only when: frontier materially explored; families qualified/rejected/BLOCKED_BY_DATA;
champions survive red team; three consecutive well-designed waves without Pareto improvement;
marginal value low. A null overall result ("no robust retail-executable NQ scalping edge")
is an acceptable, publishable outcome — standards are never lowered to avoid it.
