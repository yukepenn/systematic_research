# BEST_ONE_MNQ PARITY CERTIFICATE — SolarWaveOneContractMNQ_v5

> **UPDATE 2026-08-09 (same-day continuation, first-divergence forensics).** BEST_ONE_NQ's
> event-level forensics found a real, confirmed NinjaScript defect (DEFECT 3) shared byte-for-byte
> in this object's own `BmomBar()`: the BMOM leg's end-of-RTH flatten was a hardcoded clock
> (`hm >= 155700`), never migrated to session-relative, so on a holiday early-close session it
> never fires and `bmomPos` survives stale into the overnight session. Since `BEST_ONE_MNQ` shares
> the identical NQ-only decision sequence with `BEST_ONE_NQ` (independently confirmed
> `np.array_equal` this same wave), this defect affects it identically. **Fixed** with the same
> one-line change in **`SolarWaveOneContractMNQ_v5`**, deployed and spot-verified on live NT8
> output for the Presidents Day 2025-02-17 window: the spurious 18:06 short entry is gone; the
> object now enters short at 2025-02-18 09:51 (23592.75), matching `SolarWaveOneContractNQ_v5`'s
> corrected decision exactly (same timestamp, same side, execution-leg price differs only by MNQ's
> own tick/contract economics as expected). **STATUS: CERTIFIED** for the event-level mechanism
> (inherits BEST_ONE_NQ's full leg-by-leg proof by construction, since the decision sequence is the
> same array). Full multi-year net-profit certification and the separate 5-named-session gap below
> remain open **as of this banner** — both were subsequently closed the same day; see
> "Full-history chunked certification + 5-session reopen" and "Final verdict" near the end of this
> file for CURRENT status. Everything between this banner and that section (Identity through "What
> remains open (post-fix)") describes the pre-fix `_v4` object and this wave's early-pass findings
> — kept as the diagnostic record, not current status.

## ORIGINAL/EARLY-PASS CONTENT (superseded by "Full-history chunked certification" and "Final verdict" below — kept for the diagnostic trail, not current status)

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

## What remained open after this wave's FIRST pass (HISTORICAL — both items closed by the third continuation below)

(1) The pre-existing 5-named-session fill-sequencing gap from the earlier campaign — confirmed
NOT explained by DEFECT 3 (zero date overlap), and at this point in the wave not yet
individually re-investigated. (2) Full multi-year net-profit certification, blocked at this point
by the CrossTrade long-job limitation. **Both were closed later the same day** — see immediately
below.

## Full-history chunked certification + 5-session reopen (2026-08-09, third continuation — CURRENT STATUS)

All 4.5 years now covered via 7 chunked NT8 jobs (see `FULL_HISTORY_CERTIFICATION.md`); NT8
$30,052.60 vs Python $28,783.40 (+4.41%), same 2 disclosed mechanisms as BEST_ONE_NQ. Separately,
all 5 historically-named sessions (2025-04-07, 2025-04-09, 2025-04-11, 2025-11-18, 2026-04-08)
were reopened against real, current `_v5` NT8 output: **every one shows exact leg-level
decision agreement** (matching timestamps and sides, only the standard 1-tick fill difference).
The OLD 0.8996 daily-correlation finding was traced to `SolarWaveOneContractMNQ_Final.cs` — a
materially different, already-superseded object with a confirmed cross-series order-arrangement
defect (100% forced exits, zero voluntary exits, per `PRODUCTB_ONECONTRACT_FINAL/REPORT.md`) —
not something that reproduces on the current object. This closes the 5-session gap: it does not
apply to `_v5`.

## Final verdict

**CERTIFIED**: for the event-level decision mechanism (inherits BEST_ONE_NQ's full leg-by-leg
proof by construction — same decision array, spot-verified independently on live NT8 output for
the Presidents Day window); for full-history executable coverage (all 7 chunks, no gaps, NT8
$30,052.60 vs Python $28,783.40, +4.41%, fully reconciled to the same two disclosed conventions
as BEST_ONE_NQ); and for all 5 historically-named sessions (exact decision agreement on current
`_v5`, closing the old 0.8996 gap — traced to a different, superseded object). No known
unexplained decision-level divergence exists anywhere in the tested history. `_v4` (unfixed) is
superseded; `_v5` is the current incumbent for this object.
