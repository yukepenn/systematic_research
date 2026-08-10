
# REL01_CONDITIONAL_CROSSMARKET — scoping pass, closed NOT_YET_JUSTIFIED

**2026-08-09. Directive Master v3 sec58. Task: scoping only, per explicit instruction — do not
attempt construction this pass regardless of outcome.**

## Question

Does a genuine, defensible mechanism exist for why NQ's relative state vs ES/RTY/YM (leadership,
divergence, breadth) should carry incremental continuation/reversal information beyond NQ's own
state — sufficient to justify opening a REL01 construction, per sec58's explicit requirement of
"an explicit, real mechanism... no arbitrary cross-index feature farm"?

## What was checked

1. **`research/system_master/RECENT_REGIME_BMOM.md`** (38 lines, read in full) — B-MOM's frozen
   rule, evidence stack, and standing requirements. **Zero mention** of ES/RTY/YM, cross-market,
   leadership, divergence, or breadth anywhere in the document. This is the first doc
   `CONTINUOUS_EVOLUTION_WAVE4_PLAN.md`'s own P8 entry names to check ("Requires a motivating
   mechanism — check `PORTFOLIO_FRONTIER.md`/`RECENT_REGIME_BMOM.md` first"); it yields nothing.
   `PORTFOLIO_FRONTIER.md` was also checked and is equally silent on cross-market content.

2. **`runs/GAMMA00_DEALER_GAMMA_FEASIBILITY/REPORT.md`** (71 lines, read in full) — its literature
   synthesis on Baltussen, Da, Lammers, Martens (*JFE* 2021), "Hedging Demand and Market Intraday
   Momentum." Confirmed via direct web search of the paper's own abstract/findings: the mechanism
   is that option/leveraged-ETF market makers hedge gamma exposure by trading in the direction of
   the day's move, so **each instrument's own** early-day return predicts **that same
   instrument's own** last-30-minute return (tested across 60+ futures independently, NQ among
   the strongest). This is a **single-instrument** intraday-momentum mechanism. It says nothing
   about one index future's state predicting or conditioning another's — no cross-asset spillover
   or relative-leadership claim is made or tested in the paper. It was already correctly spun off
   in its own-instrument form as `MOM01_INTRADAY_MOMENTUM` and provides no grounding for
   NQ-vs-ES/RTY/YM conditioning specifically.

3. **Standard microstructure/index-arbitrage literature**, web-searched directly per task item 2
   (primary sources, not vendor/retail — consistent with this repo's directive sec44/79
   convention):
   - Index-futures lead-lag/price-discovery: **Chan (1992)**, *Rev. Financial Studies* 5:123-152,
     and **Hasbrouck (1995)**, information-share model. Both establish that a **given index's own
     futures** lead **that same index's own cash market** (leverage/low-cost/easy-short
     advantages). This is a real, well-established mechanism — but it is futures-vs-own-spot, not
     index-future-vs-different-index-future. It doesn't map onto NQ-vs-ES/RTY/YM, and this repo
     has no spot-index data to apply it to even if it did.
   - ETF creation/redemption arbitrage: real, primary-source-documented mechanism, but it
     describes an **ETF converging to its own underlying basket** (law-of-one-price enforcement),
     not one index converging toward or diverging from a different index.
   - Market breadth/concentration-divergence (e.g. "Herding for profits: Market breadth and the
     cross-section of global equity returns"): a real, robust, predictive literature — but it is
     built on **individual-stock advance/decline breadth**, which `DR_SM_B_practitioner.md` item
     10 already confirms this repo does not have ("Market-internals trend-day tells (cumulative
     TICK, ADD, breadth thrust) — data not in the inventory... mandate forbids paid data").
     Substituting 3 index-level series (ES/RTY/YM) as a breadth proxy is not what that literature
     tests — it would be a manufactured analogy, not a citable grounding.

4. **All 8 `research/system_master/deep_research/*.md` files**, grepped for
   ES/RTY/YM/cross-market/relative-state/breadth/leadership/divergence/lead-lag. Five matched
   (`DR_SM_A_academic.md`, `DR_SM_B_practitioner.md`, `DR_SM_C_dsp_control.md`,
   `DR_V4_EXPANSION_PASSES_20260808.md`, `DR_V4_SOLARCORE_EXPANSION_20260808.md`); three did not
   (`DR_V2_PASS_A_AUCTION.md`, `DR_V2_PASS_B_DSP.md`, `DR_V2_PASS_C_RISK.md`). Only
   `DR_V4_EXPANSION_PASSES_20260808.md`'s Pass D1 (7 candidates: cap-tier catch-up, duration-spread
   shock reaction, European session lead, index-rebalance flow, dispersion catch-up, weekend
   info-diffusion lag, roll-week basis convergence) and Pass D2#1 (cross-index dispersion
   catch-up) are actually cross-market proposals. Unlike `DR_SM_A`/`DR_SM_B` — which cite a
   primary source with a URL for every single candidate (Baltussen-Da, Gao-Han-Li-Zhou,
   Boyarchenko-Larsen-Whelan, etc.) — **the D1/D2 cross-market candidates carry no primary-source
   citation anywhere in this repo**, only a one-line mechanism-name description. This is a
   materially weaker evidentiary basis than every other family in this campaign that has been
   opened for construction.

5. **The standalone form of this exact question is already exhausted and dead in-repo.**
   `COMPLEMENTARY_ENGINE_FRONTIER.md`'s `ENGINE3_SLATE5_CROSSMARKET` entry: **15 of 15**
   ES/RTY/YM candidates killed across 5 slates. Critically, the *closest* existing analog to a
   "divergence carries information" mechanism — Wave-9's **duration-spread reaction to macro-clock
   shocks (NQ vs RTY/YM)** — was tested directly as a standalone signal and killed (`CURRENT_TRUTH.md`
   Wave-9: "ALL THREE KILLED... none clears its significance gate"). A genuinely NEW mechanism
   class, not a re-spec of any of the 15, is explicitly required per
   `COMPLEMENTARY_ENGINE_FRONTIER.md`'s own closing line.

## Internal governance already anticipated this exact gap

Three independent audits in this repo, written before this pass, already flag precisely the
situation found here and instruct against forcing it open:
- `FRONTIER_AUDIT_20260809.md` condition (c): cross-market bars "remain fully unused... recorded
  as available but not yet motivated," with an explicit "standing prohibition on fishing for a
  candidate to fill a slot."
- `CONTINUOUS_EVOLUTION_WAVE3_SYNTHESIS.md`: "watch for a genuine cross-market conditioning
  mechanism to emerge from some future finding (**not manufactured pre-emptively**)."
- `CONTINUOUS_EVOLUTION_WAVE4_PLAN.md` P8 (REL01's own queue entry): "Requires a motivating
  mechanism."

This pass is the first to actually execute that check (literature read + primary-source web
search + full deep_research grep), and it comes back empty against sec58's own bar.

## Verdict

**NOT_YET_JUSTIFIED.** No genuine, citable, NQ-vs-ES/RTY/YM-*specific* mechanism was found.
Every candidate mechanism examined is either (a) a single-instrument effect that says nothing
about cross-index relative state (Baltussen et al. hedging demand, futures-vs-own-cash-index
lead-lag), (b) a within-object convergence mechanism that doesn't generalize to index-vs-index
(ETF arbitrage), (c) grounded in data this repo doesn't have and can't legitimately proxy with
index-level series (individual-stock breadth), or (d) an uncited mechanism-name-only proposal
already tested to death in its natural (standalone) form (15/15 killed, including the closest
divergence analog). Per sec58's own instruction, REL01 is closed explicitly rather than forced
open on "it might help" reasoning. **No construction was attempted this pass** — this is a pure
literature/mechanism scoping result.

## Retry condition (for any future reopening)

REL01 may only be reopened if a future pass independently produces a **specific, primary-source-
grounded mechanism** for why NQ's relative state vs ES/RTY/YM specifically (not "more features")
should condition NQ's *existing* engines (Solar/B-MOM) — e.g. a documented dispersion-trading /
index-convergence mechanism specific to major US equity index futures, or genuine individual-
stock breadth data (not an ES/RTY/YM index-level substitute). It may **not** be reopened by
wrapping any of the 15 already-killed standalone candidates in a conditioning/interaction
framing without that independent grounding — that would be exactly the "arbitrary cross-index
feature farm" sec58 prohibits.

## No new data needed if a mechanism is later found

`runs/SM1M_ES_SUBSTRATE/`, `runs/SM1M_RTY_SUBSTRATE/`, `runs/SM1M_YM_SUBSTRATE/` (1-minute
ESU6/RTYU6/YMU6 bars, 2022-01 through 2026-07-31, NT8-Analyzer-verified, read-only context
instruments per V4 §0/§36) and `runs/W18_XINST_BARS/` already exist in-repo. This governance wall
is unrelated to and does not conflict with the scalping_lab tick/BBO 40-session boundary
(different instrument class, different substrate, no export was requested or performed this
pass).
