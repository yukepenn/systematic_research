# R6 — orthogonal Engine-3 audit — RESULTS

Per directive sec27-28/sec59: "Search old Engine-3 research first... If no genuinely orthogonal
mechanism exists in available data: R6 CLOSED — NO JUSTIFIED CANDIDATE is correct. Do not invent
another momentum indicator." No new run/spec.yaml frozen — this is an evidence audit, not a new
analysis, per the directive's own instruction not to duplicate closed work.

## Prior evidence (audited, not rerun)

`research/system_master/COMPLEMENTARY_ENGINE_FRONTIER.md`: **5 slates, 15 candidates, 0
survivors**, axis declared exhausted 2026-08-09 (same day, prior wave). Slates 1-2 (6 candidates)
tested fade/rotation/reversion mechanisms directly, including **VWAP reversion explicitly**
("VALUE-1 VWAP reacceptance"), and found "the market punishes every reversion form we have tested
at these horizons" — a decisive, general finding, not a narrow miss. Slate 3 (3 candidates) tested
continuation/smoothness mechanisms, also killed. Slate 4 (3 candidates) tested cross-market
lead-lag, killed. Slate 5 (3 candidates) tested cross-market dispersion/catchup variants, killed,
closing the axis at 15/15.

## Does anything from this session's SA0/R3/R4/R5 work constitute a genuinely new mechanism class?

Checked directly against the prior 15 killed candidates:

- **R5's `failed_breakout_rejection` finding** is the closest candidate to a "new idea" surfaced
  this session — but it was tested and used as a CONDITIONING feature on the incumbent's own
  entries (does this specific entry look like a failed breakout, given the incumbent already
  decided to enter), not as an independently-tradable standalone mechanism. A standalone
  breakout-rejection/mean-reversion ENGINE is exactly the class of idea slates 1-2 already tested
  and killed (VWAP reversion, fade mechanisms) — reusing the same underlying mean-reversion
  premise at a different implementation layer does not clear directive sec27's "genuinely new"
  bar.
- SA0's B-MOM standalone-Sharpe finding (1.26) is a real, strong result, but B-MOM is already
  INSIDE the current architecture (not orthogonal by definition — it is one of the two existing
  legs, not a third independent engine).
- SA0's short-side crisis-insurance-convexity finding and the C4-forced-exit-superiority finding
  are both structural/mechanistic insights about the EXISTING system, not proposals for a new,
  independent, low-correlation mechanism.
- No genuinely new data source was introduced this session (R5's own honest inventory confirms
  no order-flow data exists; no new market/instrument was added).

**No candidate surfaced this session clears the bar directive sec27 sets ("a genuinely new idea
surfaces") against the already-exhausted 15/15 record.**

## Disposition

**R6: CLOSED — NO JUSTIFIED CANDIDATE.** Consistent with directive sec59's explicit instruction,
no candidate is manufactured to fill this slot. The Engine-3 axis remains exhausted at 15/15
(unchanged from the prior wave); this session adds a fresh, dated confirmation that nothing in
the current architecture-science pass reopened it. Continuing automatically to PA0/PA1 per
directive priority order.
