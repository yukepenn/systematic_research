# SW01b_DRIFT_MATCHED_CONTROL — Preregistered Spec

_Committed before results are read. 2026-08-06. Red-team-originated (SW00 §7). Null-hypothesis test; zero DoF added to the candidate (the control strategy is instrumentation, not a candidate)._

## Hypothesis (H-003, null to reject)
**Null:** Solar Type-1 entry timing carries no information — random entries at matched frequency, processed through IDENTICAL exit machinery (Solar trailing-stop crossings + exit-on-session-close) on the same window/costs, produce net profit statistically indistinguishable from the baseline's $146,440.60 (slip-0).
**Rejection of the null requires:** baseline net > ALL 30 mode-0 null seeds (empirical one-sided p ≤ 1/31 ≈ 0.032).

## Instrument: `SW01bRandomEntryV1` (new strategy class; frozen baseline untouched)
Clone of SolarWaveRKReplicaV0 with ONLY the entry condition replaced:
- Seeded `System.Random(Seed)`; one uniform draw per eligible flat bar (eligibility identical to baseline: BarsInProgress 0, CurrentBar ≥ BarsRequiredToTrade, time filter); enter when draw < EntryProbBps/10000; direction = independent 50/50 draw.
- `EntryProbBps = 68` (≈0.0068/flat-bar), targeting ≈2,900 trades to match baseline frequency.
- `ExitMode 0`: Solar trailing-stop crossing exits + session close (identical machinery). NOTE (preregistered interpretation): because the vendor TrailingStop sits on the trend side, counter-trend random entries exit almost immediately — mode 0 therefore tests **entry timing given trend-aligned holding**, which is exactly the baseline's machinery.
- `ExitMode 1`: session-close exit ONLY — measures raw hold-to-close drift harvest (trade frequency ≈1/session; NOT frequency-matched; interpret per-trade and per-session, not by total).
- All other SetDefaults identical (exit-on-session-close 30s, BarsRequired 20, lookback 256, Standard fill, GTC, DefaultQuantity 1).

## Runs (slip-0, canonical 2023-25 window, Lifetime commission)
- Sweep A: ExitMode=0 fixed, Seed = 1..30 (30 combos, native optimization, summary payload).
- Sweep B: ExitMode=1 fixed, Seed = 1..15 (15 combos).
- Determinism spot-check: Seed=7/ExitMode=0 rerun as a standalone Tier-2 job must reproduce its sweep summary exactly.

## Preregistered readouts & decisions
1. Null distribution of mode-0 NetProfit (30 seeds): report min/median/max. **Baseline > max → entry timing has information (null rejected, p≤0.032). Baseline ≤ 90th pct of nulls → MAJOR finding: Type-1 entries add nothing beyond exit machinery + drift → campaign pivots to exit/risk machinery (SW02/SW08) and the leaderboard reference loses its "signal" interpretation.** Intermediate → inconclusive; extend seeds to 60 once.
2. Mode-1 distribution: mean per-trade and total → quantifies drift+hold-to-close harvest; qualifies the SW00 close-bucket finding.
3. Long-vs-short split of null runs: quantifies pure drift asymmetry vs baseline's Long PF 1.20 / Short 1.07.

## Multiple-testing accounting
The 45 null runs are instrumentation (no selection among them); logged in the registry as `null_control` (info_risk: none — results cannot promote any candidate, only demote).
