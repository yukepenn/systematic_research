# VF_CLEANROOM_SPEC — clean-room VWAP Flux architecture (directive v3.0 §12-§26)
2026-08-24. Sources: owner reverse-engineering study (external research note),
ninZa VWAP Flux Trader Manual (owner-supplied PDF, EV-038/039), our image
audit, R3/VF4 experiments. NO vendor code seen; NO code-lineage claims.

## Leading architecture (incumbent)

VF-ANCHOR: every P=AnchorPeriod minutes start a new anchored VWAP accumulator;
retain the latest A=Amount layers; ALL retained layers keep updating each bar;
per bar, collect the A layer values, sort, and map to 5 rails via the level
percentages; FairValue = Median rail. Trend state computed from price vs rails
+ a TrendPeriod=20 EMA of PRICE (manual §2.4: trend classification only — the
EMA does NOT smooth the cloud; changing it must not change cloud geometry).

Falsification control: VF-BLOCK (current P-minute block updates, completed
blocks freeze). Decided by V2 morphology tests, not PnL.

## Semantics pinned by the manual (Class-A public doc)

| Param | Semantics | Status |
|---|---|---|
| Volume Base = BidAskPrice_RealVolume | per-tick: price>=ask -> buy vol, <=bid -> sell vol; **NO historical calculation without Tick Replay** (EV-039) | pinned |
| Anchor Period (min) | VWAP recalculation cycle | pinned (lifecycle open: V2) |
| VWAP Amount | number of most-recent VWAP layers forming the bands | pinned |
| Trend Period / MA Type | averaging of PRICE for trend determination | pinned (role); composition open (V3) |
| Level Max/Upper/Median/Lower/Min (%) | "thresholds within the VWAP bands" | formula OPEN: percentile-linear vs min-max interpolation (V2 §16 probes; wording slightly favors min-max) |
| Signal Quantity Per Trend | max SAME-DIRECTION signals within one trend/zone episode | pinned (reset rule open: V4 §26) |
| Signal Close Threshold (%) | candle-close-location (CLV) filter — H1 family CONFIRMED; direction reading ambiguous | two members preregistered: H1a momentum-close (buy needs close in top T% of range), H1b extreme-pullback-close (buy needs close in bottom T% of range); trader T=10 makes them maximally different -> V4 probe |
| Signal Split (Bars) | min bar distance between consecutive SAME-DIRECTION signals | pinned |
| Zone Period | static S/R zone cycle — EXISTS in the product; **absent from every trader frame** | supports selective-exposure/reimplementation (H2/H3/H4) |
| Signal_Trend / Signal_Trade | documented output alphabet 1 / −1 (manual p15; no ±2, no Signal_Cum_Delta) | manual likely predates Feb-2026 upgrades |

## The EV-039 embedding contradiction (new, load-bearing)

Trader frames: Tick Replay OFF everywhere + Volume Base=BidAskPrice_RealVolume
+ SA backtests full of historical trades. Manual: that combination computes
NOTHING historically. -> A directly-embedded licensed VWAP Flux cannot produce
his backtests in the displayed mode. Leading reading: his 2026 stack is his own
reimplementation (or adaptation) computing from BAR data (close/typical ×
volume), with vendor-style parameter names. Consequences:
1. Our bar-level clean-room clone is not an approximation of his input — it IS
   the same input class he must have used. Tick-fidelity is bounded anyway
   (R3 addendum: 1.7% trend-state disagreement).
2. Purchase-gate oracle protocol must use Tick Replay or UpDownTick modes to
   make the licensed indicator compute historically at all; a naive purchase
   would NOT reproduce his SA context.
3. "Custom wrapper on licensed VWAP Flux" (previous CURRENT_TRUTH wording)
   downgrades to "custom implementation of a VWAP-Flux-style stack" as the
   leading hypothesis (H4/H3 over H1) pending the panel-completeness image pass.

## Build plan (V1/V2 tests, all deterministic, no PnL selection)
1. vf_core.py: VF_ANCHOR + VF_BLOCK constructors; price inputs {close, hlc3};
   rails {percentile_linear, nearest_rank, minmax}; anchor-age metadata
   retained as diagnostics (§18; not used in reconstruction).
2. Unit tests incl. adversarial population [100,101,102,103,140]:
   percentile-linear Q75=103.x vs minmax 75%=130 — sharp separation (§16).
3. Morphology comparison vs chart-image geometry: reset jumps (BLOCK jumps at
   period boundaries; ANCHOR drifts), rail smoothness, asymmetry.
