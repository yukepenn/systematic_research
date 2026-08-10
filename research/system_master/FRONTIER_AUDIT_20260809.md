# Frontier audit — 2026-08-09 (directive sec82's own required bar before any exhaustion claim)

**Trigger:** 13 independent CONTINUOUS SYSTEM EVOLUTION hypotheses now closed (H0-family
diagnostics aside, the alpha-search set is U1/U3/U4/U5/U6/U7/U4B/SHADOW01/U1B/U6B/U8/U9B/U8B/
LEV01/LEV02/SKEW01 — 16 constructions/diagnostics with a definitive verdict, zero promotable),
plus PORT01's portfolio synthesis quantifying zero diversification benefit from combining the
two current incumbents. Per directive sec82, "information frontier exhausted" may only be
declared if ALL of: (a) remaining local features are redundant/closed, (b) short-history data
cannot support honest validation, (c) no compatible unused data remains, (d) literature scout
yields no distinct mechanism, (e) self-generated residual hypotheses are exhausted. Checking
each explicitly, honestly, against what has and has not actually been done.

## (a) Remaining local features redundant/closed?

**Largely yes, with caveats.** Every OHLCV-derived residual-information class tested this
campaign — price-transformation (R4 slope, redundant), microstructure-proxy (R5, tail-blind),
soft-weighting on already-found leads (U5, sunk-P&L confound), path organization at both level
and rate-of-change (U8/U8B, right-tail-unsafe), return skewness (SKEW01, weak + worst right-tail
failure recorded), and volatility asymmetry both as a trade-level and regime-level signal (LEV01
Test 2/LEV02, confounded then null) — has converged on the same handful of outcomes: real bulk
correlation that fails right-tail safety, or genuinely too small to matter, or an artifact of a
sunk-outcome confound. This is a consistent, cross-validated pattern across 8 independently
constructed feature families, not a coincidence of any one team's blind spot. **Not literally
100% closed** — no one has tested every conceivable transformation of OHLCV data — but the
marginal EVI of "one more single-feature residual-information test in this class" is now low
given how uniformly this pattern has held.

## (b) Short-history data cannot support honest validation?

**True for microstructure specifically, not resolved for the underlying question.** U9B's
first-ever genuine order-flow test found no detectable signal, honestly attributed to
insufficient sample (62-232 events, 33-37 sessions) rather than to the absence of real
information. This is explicitly re-testable, not closed — but re-testing requires calendar time
to pass (more scalping_lab sessions to accumulate), not more research capacity right now. This
is the one genuine "wait for data" item on the list, and per directive sec83's own instruction
("no wait-for-future-data as the default answer... continue all research that can be completed
now"), it should not be used as a reason to pause other research, only flagged as a standing
future action.

## (c) No compatible unused data remains?

**False — cross-market bars (ES/RTY/YM, `runs/W18_XINST_BARS/`) remain fully unused this phase.**
U2's audit found them chronology-compatible (full 2022-2026 history) but noted the
standalone-signal form of that idea is already 15/15 killed from the prior campaign. Per
addendum sec45, using them requires "a NEW conditional mechanism," not a standalone re-test —
none has yet emerged from this wave's own findings. This audit does not manufacture one (per the
standing prohibition on fishing for a candidate to fill a slot) — it is recorded as available but
not yet motivated.

## (d) Literature scout yields no distinct mechanism?

**Partially explored, not exhausted.** One scout pass (`LITERATURE_SCOUT_20260809.md`) generated
two hypotheses (leverage effect, skewness forecasting) — both tested to a definitive conclusion
this wave (leverage effect: real market fact, no tradeable signal; skewness: weak and tail-unsafe
in this system's own data). The scout's search terms covered volatility/liquidity/leverage and
trend-persistence/reversal topics specifically; it did NOT cover several of directive sec69's own
named topics: opening/closing auction spillovers, intraday liquidity cycles specifically (as
opposed to overnight-vs-RTH liquidity generally, which was searched), or volatility-conditioned
trend-following implementation details. A second scout pass on these untried topics has not been
performed. **This condition is not met.**

## (e) Self-generated residual hypotheses exhausted?

**Not met.** PORT01 itself is an example of a self-generated pivot (directive sec57/68) that
produced a genuinely new, valuable result (precise diversification quantification) without any
alpha search at all. Other directive-named-but-not-yet-executed self-generated angles remain
available: the action-value (Q-function) diagnostic framework (sec46), Product-A marginal
exposure value shape (sec28, distinct from U6/U6B's exposure-band and scale-rate questions —
specifically whether the exposure-to-value mapping is linear/concave/convex), and the reversed
short/long entry-mechanics side-finding LEV01 disclosed but did not investigate further.

## Verdict

**The directive's own bar for "information frontier exhausted" is NOT met** — conditions (c),
(d), and (e) are each explicitly open, not just technically-unclosed formalities. What IS
genuinely established, with unusual thoroughness for a single research phase, is that the
*easy-to-reach* local information (OHLCV transformations, organization measures, soft-weighting
on already-known leads, trade-level volatility-regime effects) has been harvested about as far
as this campaign's current toolkit reaches, with a consistent, cross-validated failure signature
(right-tail unsafety or magnitude) rather than scattered, inconclusive results. The honest
recommendation is not to declare exhaustion, but to be candid that continuing in the SAME
local-feature-hunting mode has sharply diminishing expected value, and that the highest-EVI next
steps are qualitatively different in kind: a second literature scout pass on the untried topics,
a specifically-motivated cross-market conditioning test (not a standalone re-test), the
action-value/marginal-exposure diagnostics named in (e), or simply waiting for U9B's data to
accumulate before re-testing microstructure.
