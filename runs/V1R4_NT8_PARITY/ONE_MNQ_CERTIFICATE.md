# BEST_ONE_MNQ PARITY CERTIFICATE — SolarWaveOneContractMNQ_v4

**STATUS: NOT CERTIFIED — same warmup-driven improvement pattern as BEST_ONE_NQ (same shared
decision sequence), compounded by the already-known, still-open MNQ daily-correlation gap from
the earlier campaign.**

## Identity

| field | value |
|---|---|
| strategy | SolarWaveOneContractMNQ_v4 |
| source hash | repo `src/ninjascript/SolarWaveOneContractMNQ_v4.cs` = 25,693 bytes |
| deployed NT8 hash | byte-identical (25,693 bytes), confirmed via `ReadNinjaScriptFile` this session |
| instrument | signal = NQ 09-26 (primary series); execution = MNQ 09-26 (added series[1]) |
| bars | 3-minute |
| session | CME ETH, session-relative C4 flatten, 16:45 mandatory close honored |
| commission | NinjaTrader Brokerage Lifetime ($0.65/side MNQ) |
| slippage | none added (Standard fill, no override) |
| fill mode | Standard |

## Warmup-corrected comparison

| test | Q1 2025 net |
|---|---:|
| NT8, warmed-up from 2024-04-01 (9 months warmup) | **-$760.60** |
| Python twin, continuation state from 2022, genuine MNQU6 prices | **-$658.40** |

**Difference: -$102.20, 15.5% relative** -- same sign, similar small-scale magnitude pattern as
BEST_ONE_NQ (expected, since the underlying decision sequence is identical, per
`runs/S2_SELTIME/r2_spec.yaml`'s confirmed `interpretation_one_MNQ`; only fill $ differ).

## Decision-sequence identity (independently confirmed this wave)

The R2 adversarial-verification workflow independently confirmed, over the full 519,714-bar dev
window, that `barpos_NQ_incumbent.npy` and `barpos_MNQ_incumbent.npy` are `np.array_equal` --
i.e. the position DECISION sequence genuinely is shared, not separately (re)computed, matching
the real object's own NQ-only-signal architecture. Trade-count agreement for this instrument
inherits BEST_ONE_NQ's own count-level result (106 vs 107) directly, since it is the same
decision sequence executed at different prices.

## The pre-existing, still-open MNQ-specific caveat

Independent of this wave's warmup work, `runs/PRODUCTB_ONECONTRACT_FINAL/REPORT.md` (an earlier
wave) already found the real NT8 MNQ backtest's daily P&L correlation to its Python reference is
**0.8996**, below the >=0.999 bar, narrowed to 5 specific named sessions (2025-04-07, 2025-04-09,
2025-04-11, 2025-11-18, 2026-04-08). This wave's own workflow verifier independently confirmed the
genuine MNQU6 price series used here does NOT touch any of those 5 sessions with its 11
scattered/thin-print forward-filled bars (2022-06-09, 2024-04-22, 2026-05-29 -- none overlap),
so this wave's warmup work and that older open item are independent, additive open questions, not
the same issue re-appearing.

## What remains open

Two separate, additive open items: (1) this wave's ~15.5% Q1-2025 residual (same
FILL/ORDER_TIMING hypothesis as BEST_ONE_NQ's certificate, not yet root-caused), and (2) the
pre-existing 5-named-session fill-sequencing gap from the earlier campaign (not re-investigated
this wave -- the directive named these sessions as a priority target; time did not permit reaching
them this pass). Full multi-year certification also remains open, same CrossTrade long-job
limitation as the other two certificates.

## Final verdict

**NOT CERTIFIED.** Directionally and structurally consistent with BEST_ONE_NQ's result (same
decision sequence, same warmup improvement, same residual class), plus one additional, older,
still-unresolved open item specific to this instrument. No object's shipped status changes.
