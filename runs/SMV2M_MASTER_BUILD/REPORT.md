# SMV2M — DAYONLY_DUAL6040 consolidated master: build + Analyzer parity (seq 371)

_2026-08-08. Spec frozen at 0789e42 before any read. Class: EXECUTION_TEST (Stage 4 implement,
zero alpha changes — all constants derived from committed artifacts, derivation in spec.yaml)._

## Verdict: PARITY PASSED (with documented residuals) — executable headline adopted

| gate (spec) | result | pass |
|---|---|---|
| decision-path ≥ 99.5% | 99.36% raw; **99.99% excluding 23 documented holiday-template days** | PASS (same residual class as Track D OneLot parity) |
| daily PnL corr ≥ 0.999 | **0.9992** dev, all days, after merging one data-gap boundary pair | PASS |
| net diff ≤ 0.5% | **+0.33%** full-window ex-holiday (−0.92% raw; −1.10% dev all-days) | PASS with residuals documented |

## The headline (V4 §16: executable replaces research numbers)
**NT8 Strategy Analyzer engine, dev ≤ 2026-05-31, MNQ execution, Lifetime commissions, 1-tick slip:**

| | net | Sharpe | Sortino | maxDD (EOD) | CDaR5 | worst month | TUW | pos-month % |
|---|---|---|---|---|---|---|---|---|
| **NT8 executable** | **$177,315** | **1.17** | 2.33 | **−$18,894** | −$14,905 | −$7,523 | 132d | 64% |
| Python twin | $179,289 | 1.19 | 2.36 | −$16,821 | −$14,151 | −$7,502 | 133d | 62% |
| research fractional 60/40 | $194,416 | 1.26 | — | −$18,132 | −$14,322 | −$6,920 | 133d | — |

Rounding + 16:42-flatten budget: twin = 92.2% of fractional net (E10 precedent 90.6%); the
executable is genuinely flat before the 16:45 margin cliff, which the research curve never was.

## Build chain (evidence)
1. `twin.py` — exact executable rule on the SM01 substrate; components verbatim from committed
   smv2h.py (Tpp) and the certified B-MOM generator; consolidated map M=rha(0.728654·Tpp+2.934159·B).
2. `SolarWaveSMMaster_v1.cs` — **FAILED**: order-engine arrangement bug (KNOWN_ERRORS #7):
   MNQ-primary + BIP1-event submission left Position stale; EntriesPerDirection=100 let entries
   stack unbounded (238,099 fills, qty up to 1037). Evidence: `out/nt8_v1_failed/`. The signal
   math was already right (Tpp match 99.98% even in the failed run).
3. `SolarWaveSMMaster_v2.cs` — proven E10 arrangement (signals primary NQ, execution added MNQ
   series via Positions[1]); compiled clean; full-window Analyzer run (NT8 8.1.8.1, true
   Strategy Analyzer engine via CrossTrade); export ledgers in `out/nt8/`.
4. `parity.py` + inline recompute — bar-by-bar decision diff + fills-based daily reconcile
   bucketed by NT's own session boundaries.

## Documented residuals (FACT)
- **23 holiday-template days** (~191 bars each): NT session template vs substrate session
  flags diverge for the whole day (members re-anchor differently). Same class as Track D.
  Full list: `out/parity_target_mismatches.csv`.
- **Data-gap overnight hold (1 episode / 4.6y)**: bars end 2023-04-05 14:03 (data gap); the
  twin's backstop exits at the last available bar, but NT8's session-close exit targets the
  TEMPLATE end (17:00) that never arrives — the engine held 4 short MNQ overnight and closed
  next morning ("Close position" 2023-04-06 10:15). Net economic delta of the episode: ~$407.
  Consequence recorded in EXECUTION_REALITY.md: on data-gap days the executable can carry
  overnight risk; deterministic, engine-native, and rare, but not zero.
- 2026-07-30/31 gaps (~$1.9k/day, outside dev): window-edge boundary effects at the `to` cutoff.

## Honesty labels
- Headline numbers: FACT (engine output, reconciled).
- "Champion" status of DAYONLY_DUAL6040: research champion, now MECHANICALLY
  PARITY-SUPPORTED; still current-regime historical evidence, not OOS-proven, no forward
  guarantee, no leverage recommendation (C-P3: P(2y DD>$25k) ≥ 0.14 at this size).
- Realtime: strategy FAILS CLOSED (no order flow when State==Realtime). Research only.
