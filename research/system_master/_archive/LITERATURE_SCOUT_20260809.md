# Literature/mechanism scout — 2026-08-09

Per directive sec69: local, OHLCV-derived residual-information avenues are now heavily explored
(R4, R5, U5, U8, U8B all independently found real-but-unsafe or real-but-tiny effects; the
session/hold construction axis has failed 3 independent times). This scout looks at external,
primary/serious sources to generate NEW falsifiable mechanism ideas — not to import vendor
parameters or performance claims, per the standing prohibition. Three targeted searches; findings
below are hypothesis generators only, adjudicated against this campaign's own causal data before
any of them can matter.

## 1. Leverage effect / volatility feedback (equity index asymmetric volatility)

The finance literature's two standard explanations for asymmetric volatility: the **leverage
effect** (a large negative return raises effective leverage, mechanically increasing subsequent
volatility, then relaxing back roughly exponentially) and the **volatility feedback effect**
(an unexpected volatility increase raises required forward returns, itself causing an immediate
negative price impact). Firm-level evidence: leverage's effect on volatility is cumulative,
"up to five times larger over twelve quarters than a static model would predict for one quarter"
(ResearchGate, Leverage effect and volatility asymmetry). Recent high-frequency studies show
mixed results on which channel dominates.

**Relevance to this campaign:** this is a literature-grounded, falsifiable account of a pattern
already found EMPIRICALLY but not yet EXPLAINED in this campaign: shorts are structurally
weaker than longs (SA0: Sharpe 0.18 vs 1.54; PA0: 0.40 vs 1.38) AND U7 found the 2026 anomaly is
driven by a volatility uptrend that specifically raised the SEVERITY of losing entries. The
leverage-effect literature predicts these two facts should be mechanistically LINKED, not
coincidental: if NQ's own realized volatility spikes asymmetrically MORE after negative returns
than positive ones, that single asymmetry would independently predict both (a) why shorts (which
profit from, and are held through, negative-return episodes) face structurally worse volatility
conditions than longs, and (b) why a market-wide volatility uptrend disproportionately raises
loss severity (since losing entries — long or short — are more likely sitting through negative-
return, leverage-effect-triggered volatility spikes).

**Candidate NEW hypothesis (not tested, no construction, genuinely distinct from every closed
family):** does NQ's own `sigma460_atr_proxy_pts` (or a return-based realized-vol proxy) exhibit
a measurable leverage effect (asymmetric response to negative vs positive returns), and does
that asymmetry — not organization, not session, not soft-weighting — explain the short/long
Sharpe gap and the 2026 loss-severity finding as ONE unified mechanism rather than two separate
facts? This is distinct from every closed family: R4/R5/U8/U8B tested price-transformation and
organization features, not volatility's own directional asymmetry; U4/U4B tested reactive
exit-timing after decay, not a leading volatility-regime indicator; U7 found the loss-severity
shift but did not test whether it is itself asymmetric by prior-return direction.

## 2. Trend persistence / momentum-crash research (2024-2025 specific)

Current practitioner/academic research (Man Group, Invesco, arXiv 2510.23150) on time-series
momentum: **longer-horizon trend signals (500-day) have remained robust through 2024-2025**,
while **medium-term momentum sleeves (60-125 day) have "shown repeated episodes of whipsawing...
flatten after mid-2022, with limited recovery"** and 2025 specifically saw "on/off US policy
dynamics creating a whipsaw effect" that "hurt trend-following strategies" broadly (not specific
to this system). Separately: "time series momentum reversals are partly forecasted by the
asymmetric structure of the tail-distributed upside and downside risk."

**Relevance to this campaign:** this is independent, external corroboration that U7's own finding
(a 2024-2026 volatility/whipsaw regime driving up loss severity) is a genuine, broad market
phenomenon affecting trend-followers generally — not an idiosyncratic property of this system's
own construction. This strengthens confidence in U7's mechanism (real, not overfit) while also
tempering any expectation that a system-side fix could reverse a macro regime shift. The
skewness/tail-asymmetry forecasting claim is a second candidate feature class genuinely distinct
from everything tested: not organization (path shape), not volatility level (already tested via
sigma460), but the SKEW of the recent return distribution specifically.

**Candidate NEW hypothesis (not tested):** does a causal, short-window return-skewness measure
(distinct from ret1s_vol/organization/entropy, all already tested) forecast reversal hazard or
continuation value beyond what M/HTF/B/vol already capture? Would need its own Step-0 redundancy
check against U8's already-tested features before proceeding (skewness could correlate with
organization/entropy — untested).

## Disposition

Neither hypothesis is constructed or tested this run — both require their own preregistration,
Step-0 redundancy check, and full right-tail/chronology workup per this campaign's standing
discipline. Recorded as the top two EVI candidates for the next research wave, ranked above
re-testing U9B's microstructure result (which depends on external data accumulation, not
available research capacity) and below nothing currently open. Hypothesis 1 (leverage-effect
unification of short-asymmetry + 2026-severity) ranks higher: it explains TWO already-documented
empirical facts with one literature-grounded mechanism, rather than proposing a wholly new
untested feature class.

## Addendum — second pass (auction spillovers, intraday liquidity U-shape), same day

Per `FRONTIER_AUDIT_20260809.md` condition (d), searched the two directive-sec69 topics the
first pass hadn't covered. Findings: opening/closing auction research is dominated by
single-name-equity/ETF/index-fund rebalancing mechanics (Russell reconstitution, closing-auction
notional share growth) with no clear NQ-futures-specific, testable mechanism distinct from what
this campaign already captures via session-phase state. The classic intraday U-shaped liquidity/
volatility/spread pattern (Brock-Kleidon 1992 market-closure theory, confirmed across CBOT corn
futures, CSI 300 index futures, and NASDAQ equities) is real and well-established — but this
system's own `session_phase` state (RTH_OPEN/RTH_MID/RTH_CLOSE/etc.) already implicitly
encodes it, and U1's own interaction test already found `M_abs × session_phase` significant
specifically at RTH_OPEN and RTH_MID (t=−2.22, −2.66) — the mechanism this literature describes
is not a genuinely NEW, untested angle; it corroborates work already done (U1/U1B/U3), not a
distinct next hypothesis. **No new candidate hypothesis generated from this second pass.**

## Sources

- [Leverage Effect and Volatility Asymmetry (ResearchGate)](https://www.researchgate.net/publication/326894634_Leverage_Effect_and_Volatility_Asymmetry)
- [Leverage and asymmetric volatility: The firm-level evidence (ScienceDirect)](https://www.sciencedirect.com/science/article/abs/pii/S0927539816300226)
- [Asymmetric Volatility and Risk in Equity Markets — Bekaert (Columbia)](https://business.columbia.edu/sites/default/files-efs/citation_file_upload/asymmetric%20volatility.pdf)
- [Revisiting the Structure of Trend Premia (arXiv 2510.23150)](https://arxiv.org/html/2510.23150v2)
- [Navigating momentum crashes in a trend-following strategy (Invesco)](https://www.invesco.com/content/dam/invesco/emea/en/pdf/RRE_2024_Q2_NavigatingMomentum.pdf)
- [Trend Following and Drawdowns: Is This Time Different? (Man Group)](https://www.man.com/insights/is-this-time-different)
- [Time series momentum (ScienceDirect)](https://www.sciencedirect.com/science/article/pii/S0304405X11002613)
