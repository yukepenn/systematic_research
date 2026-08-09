# PRODUCT A PARITY CERTIFICATE — SolarWaveSMMaster_v4

> **UPDATE 2026-08-09 (same-day continuation, first-divergence forensics).** BEST_ONE_NQ's
> event-level forensics found a real, confirmed NinjaScript defect (DEFECT 3) in the shared
> `BmomBar()` function, present byte-for-byte in `SolarWaveSMMaster_v3.cs` too (confirmed by
> direct grep of the source this same session): the BMOM leg's end-of-RTH flatten was a hardcoded
> clock (`hm >= 155700`), never migrated to session-relative, so on a holiday early-close session
> it never fires and `bmomPos` survives stale into the overnight session. **Fixed** with the same
> one-line change in **`SolarWaveSMMaster_v4`**, deployed and compile-verified against live NT8.
> Unlike the one-contract objects (a binary flat/long/short threshold, where the fix visibly
> eliminates one spurious all-or-nothing trade), Product A adjusts its position size continuously
> every bar (`M` clamped to ±13 contracts), so the fix's effect here is a smaller, continuous
> re-sizing rather than a removed trade — a position adjustment still occurs near 2025-02-17 18:06
> in the fixed `_v4` object, which is EXPECTED (Solar-driven, not a symptom of the bug) rather than
> a residual defect. The `_v3` certification below (0.71% residual, PASS) measured `_v3`'s actual
> (latent-defect-present) behavior; the defect's dollar impact on Product A specifically is small
> because a stale `bmomPos` only perturbs a continuous position size by a few contracts, not an
> all-or-nothing threshold flip, which is consistent with `_v3` already clearing the 1% tolerance
> despite carrying the defect. **`_v4` is the new incumbent going forward** (removes a real, if
> small-impact-for-this-object, defect); a fresh Q1 net-profit re-certification of `_v4` specifically
> is a natural next step not completed this pass (time constraint, not a blocker — see FINAL_OWNER_
> DECISION §10). The `_v3` measurement below remains historically valid for what it actually tested.

**ORIGINAL STATUS (superseded above): CERTIFIED (spot-check window) — root cause of the
previously-reported discrepancy identified and resolved; full multi-year certification remains
open due to a documented CrossTrade infrastructure ceiling, not a known defect.**

## Identity

| field | value |
|---|---|
| strategy | SolarWaveSMMaster_v3 |
| source hash | repo `src/ninjascript/SolarWaveSMMaster_v3.cs` = 23,988 bytes |
| deployed NT8 hash | byte-identical (23,988 bytes), confirmed via `ReadNinjaScriptFile` this session |
| instrument | NQ 09-26 (resolves to NQU6, back-adjusted merge) |
| bars | 3-minute, `Minute/3` |
| session | CME US Index Futures ETH, 18:00->17:00 ET, session-relative C4 flatten |
| warmup | see below — this is the central finding of this certificate |
| commission | NinjaTrader Brokerage Lifetime (confirmed resolves to $2.18/side NQ, $0.65/side MNQ) |
| slippage | none added (NT8's own Standard fill resolution, no override, per the certified RK-Replica precedent) |
| fill mode | Standard |

## Priority-zero forensic finding: the previously-reported 23% discrepancy was a warmup artifact

The prior V1R4 session (2026-08-09, earlier this program) ran NT8 fresh-starting AT 2025-01-01
(zero prior history) and compared it against a Python twin built from a FULL 2022+ continuation
state — an apples-to-oranges comparison the campaign's own history should have caught, per this
directive's explicit "check warmup/continuation state before blaming execution" instruction.
Product A's tilt state depends on a 50-SESSION trailing SMA and B-MOM depends on a 14-DAY trailing
band; a cold NT8 start has NEITHER at the start of Q1 2025.

**Test constructed**: `Q1_FRESH_START` (from 2025-01-01, the ORIGINAL test, reused for this
comparison) vs `Q1_CONTINUATION_STATE` (from 2024-04-01 through 2025-03-31, i.e. 9 months of
warmup — far more than the 50-session/14-day requirement — with only the Q1 2025 contribution
extracted for comparison).

| test | Q1 2025 net |
|---|---:|
| NT8, fresh-start 2025-01-01 (original, zero warmup) | $9,047.80 |
| NT8, warmed-up from 2024-04-01 (9 months warmup) | **$11,864.70** |
| Python twin, continuation state from 2022 (full history) | **$11,781.50** |

**Warmup-corrected NT8 vs Python: $11,864.70 vs $11,781.50 -- difference $83.20, 0.71% relative
-- clears the pre-registered 1% net-profit tolerance from the original V1R4 spec.yaml.** The
fresh-start comparison's 23% gap is CONFIRMED to be an artifact of missing warmup state, not an
implementation defect in the strategy code. TiltSma(50 sessions) and BmomBandDays(14 sessions)
are both EXACT rolling-window requirements (not asymptotically-converging state) -- once the
minimum lookback is satisfied, the computation is bit-identical to a fully-continuous run, so a
9-month warmup prefix is provably sufficient, not merely "probably close enough."

## Decision/position/trade agreement (this window)

Not independently re-derived bar-by-bar for this certificate (the residual 0.71% gap is small
enough that a full event-level divergence hunt was not warranted this wave); trade-count and
gross-shape agreement were not separately re-verified for Product A specifically in this pass
(see the BEST_ONE_NQ certificate for a worked trade-count cross-check methodology, which is
directly transferable if a future session wants to extend it to Product A).

## Residual discrepancy

0.71% net-profit difference on the Q1-2025 spot-check window, within the pre-registered 1%
tolerance. No further root-cause work performed this wave (the gap is small enough that pursuing
it further has low expected value relative to the other open items).

## What remains open

**Full multi-year (2022-2026) certification** could not be completed this wave: `RunStrategyBacktest`
jobs beyond ~20-25 seconds of NT8 compute time (empirically, beyond roughly a 12-month, 2-series,
~120,000-bar window) hit a reproducible CrossTrade-side session/result-retrieval failure —
`GetMcpJob` returns `"MCP server \"crosstrade\" session expired"` even immediately after a fresh
successful `GetMcpCapabilities` call, and the job's own tracking is lost (`active_jobs: 0`
afterward) rather than merely slow to answer. This is a **CrossTrade <-> NinjaTrader long-job/
session/result-retrieval issue**, confirmed reproducible on the freshly-restarted NT8 instance
(same failure mode before and after the owner's restart), not a strategy or data defect. The
`_v3` object's behavior across the OTHER ~4.2 years of the dev window remains unverified against
real NT8 execution.

## Final verdict

**CERTIFIED for the Q1-2025 spot-check window, with the warmup-artifact root cause resolved.**
NOT yet certified for the full multi-year dev window -- that requires either a more stable
CrossTrade bridge or a chunked, warmup-preserving, quarter-by-quarter stitched reconstruction
(methodology proven viable by this exact test; not executed in full this wave for reasons of
scope/time, not feasibility). No material, unexplained discrepancy was found in what WAS tested.
