# DAY_MARGIN_FLAT operational variant — measured

_2026-08-07 · run `DM01_DAYMARGIN_SWEEP` (preregistered `b9e7686`; job
59a1405f7ec442fd) · SolarWaveOpenV3 native time filter, 13-cell R5 grid,
StartUp=false, NQ 3m, Lifetime, slip-1, 2022-01→2026-07-31 · basis
calendar-of-exit REALIZED_ONLY (matches the published R5 basis; members flat
at every exit so session TRUE_MTM identity holds within the trading window)._

## Verified margin facts (official sources; `research/operational/day_margin_variant/MARGIN_RULES.md`)

- Intraday margins end **15 min before session close = 16:45 ET / 15:45 CT**
  (NinjaTrader margin policy page; HIGH confidence). Day margin NQ **$1,000**,
  MNQ **$100**; initial (overnight) NQ **$43,433.67**, MNQ **$4,343.38**.
- Positions held past the cutoff are "subject to liquidation" (discretionary,
  not a guaranteed auto-flatten) + $25/$50 violation fees.
- The frozen baseline's exit-on-session-close (17:00 ET) therefore does **NOT**
  qualify for day margins. The variant flattens at the first bar close ≥ 16:40 ET
  (5-minute buffer) and blocks entries until the 18:00 ET reopen.
- Re-entry policy: **arm D (reconfirmation)** — after 18:00 the strategy is flat
  until a NEW Type-1 pulse fires (the code's native semantics; the most
  conservative arm; immediate-restore arms deliberately not run — no operational
  parameter search).

## Measured opportunity cost (vs the unconstrained 13-cell R5 ensemble, equal 1/N risk)

| | unconstrained | DAY_MARGIN_FLAT | delta |
|---|---:|---:|---:|
| net (strict 1/N) | $198,058.82 | **$188,605.25** | −4.8% |
| daily Sharpe (1,332 d) | 1.0104 | 0.9726 | −0.038 |
| max DD (daily) | −$39,125.61 | −$40,110.34 | +2.5% |
| top-10 unconstrained-day retention | 100% | **96.2%** | −3.8% |

Per-cell nets in `runs/DM01_DAYMARGIN_SWEEP/` (13 ledgers + spec).

## Reading

1. **The 16:40→18:00 flat window costs ~5% of net and preserves the right tail
   (96.2%)** — the big trend days are overwhelmingly RTH phenomena for this
   system; the 16:40–17:00 stub and the overnight re-entry lag carry little
   expectancy. (Consistent with SW02a's old finding that the final 30 minutes of
   holding was not the profit source.)
2. Under day margins the capital footprint falls ~40× (NQ $1,000 vs $43,434
   initial; MNQ $100 vs $4,343 for the E10 implementation), at a cost of
   0.04 Sharpe. For a small account this variant strictly dominates on
   return-on-margin; for the unconstrained scientific champion it remains a
   constrained variant, not a replacement (thesis §24: it does not dominate on
   both Sharpe and tail retention).
3. Caveats: month-end 15:10–15:30 CT fair-value halt (plausible-unverified)
   argues for a 16:10 ET buffer on month-ends; margin figures are volatile
   policy variables (4× news-window multipliers documented) and must be
   re-verified before any live consideration — which remains out of scope.

Trials: seq 272–284 (13 operational-variant configs, descriptive read).
