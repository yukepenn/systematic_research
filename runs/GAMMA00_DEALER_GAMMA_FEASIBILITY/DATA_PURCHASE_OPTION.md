# DATA_PURCHASE_OPTION — SPX/NDX options-chain data for OPTIONS_DEALER_STATE research

Per directive sec48/B5: **no purchase or subscription has been made.** This documents the
concrete option for the owner to decide on.

## Exact blocker

Computing any genuine dealer-gamma metric (net dealer gamma by strike, gamma-flip price level,
vanna/charm, 0DTE share of open interest) requires strike-level open interest and/or Greeks for
SPX (the standard academic dealer-gamma proxy) and, if NQ-specific microstructure is wanted, NDX
too. This repo currently has none of that — zero strikes, zero OI, zero Greeks, zero NBBO quotes,
at any granularity.

## Vendor options found (public pricing, August 2026 — not independently verified for NDX completeness)

| Vendor | Tier | Price | Coverage | Granularity |
|---|---|---:|---|---|
| ThetaData | Options Value | $40/mo | 4yr | 1-min snapshots |
| ThetaData | Options Standard | $80/mo | 8yr | Full OPRA tick NBBO + chain snapshots |
| ThetaData | Options Pro | $160/mo | 12yr | Full tick trades+quotes |
| Polygon/Massive | Starter | $29/mo | 2yr | 15-min delayed, Greeks/IV/OI |
| Polygon/Massive | Developer | $79/mo | 4yr | 15-min delayed, Greeks/IV/daily OI |
| Polygon/Massive | Advanced | $199/mo | 5yr+ | Real-time quotes/trades/Greeks/OI |
| Cboe DataShop | — | quote-only, no public price list | SPX from Jan 2012 | Trade/quote/EOD products; +$1,000/mo CGIF license for underlying bid/ask |
| OptionMetrics IvyDB US | — | no public price; typically WRDS/university-mediated | back to 1996 | EOD only, no intraday |

**NDX caveat:** NDX is Nasdaq-listed, not Cboe-listed, so Cboe DataShop's core catalog centers on
SPX/VIX. NDX history would more naturally come from an OPRA-aggregating vendor (ThetaData,
Polygon/Massive, Databento), since OPRA is the shared options tape across exchanges. NDX
completeness at any specific vendor was **not verified** in this check.

## Research question unlocked

Full historical OPRA options chains (SPX at minimum, NDX if available) with strike-level OI
and/or Greeks would allow: (a) computing genuine dealer net-gamma-by-strike and a gamma-flip
level for SPX using the same Level-D-style OI-based approximation the literature itself
frequently uses (never Level A without capacity-tagged trade data, which the vendors above do not
offer at these price points); (b) testing whether that SPX-derived gamma regime has any residual,
causal, cross-market relationship with NQ's own continuation/reversal/volatility behavior,
controlling for NQ's own state (M, session, vol) per directive sec49; (c) an NDX-specific
replication if NDX coverage proves adequate.

## Marginal EVI assessment (informational, not a recommendation)

Genuine, rigorous SPX dealer-gamma research (Level A, capacity-tagged) already concludes the
effect is "not large" even in the deepest options market in the world. Absent NDX-specific
evidence, a good-faith (not empirically confirmed) inference is that the effect would be smaller,
not larger, for NQ. This tempers the expected payoff of the purchase relative to, say, unlocking
a wholly new predictive mechanism — the most likely realistic outcome of acquiring this data is a
clean, well-supported **null** result (consistent with the SPX literature), which still has
research value (closes GAMMA00 properly rather than leaving it DATA_LIMITED indefinitely) but
should be weighed against the $80-199/month ongoing cost with that expectation set correctly.

## Recommendation

Cheapest tier that would let GAMMA00 proceed as a genuine (not proxy) test: **ThetaData Options
Standard ($80/mo, 8yr history, full OPRA tick NBBO)** or **Polygon/Massive Advanced ($199/mo, 5yr+
history, includes Greeks/OI directly rather than requiring in-house Black-Scholes computation)**.
EOD-only tiers ($29-40/mo) would suffice only if the research question is confined to end-of-day
gamma-by-strike snapshots rather than intraday positioning dynamics. **Awaiting owner decision —
no action taken.**
